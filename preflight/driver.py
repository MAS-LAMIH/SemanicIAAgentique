"""Addition-only A/B evaluator. Frozen subject, supervision and truth functions."""
from dataclasses import asdict
import json
from pathlib import Path
import sys
from time import sleep
from semantic_action.artifact import Scenario, serve
from semantic_action.provider_b import BookingScenario, serve_bookings
from semantic_action.native_verifier import capture, adjudicate, NativeExpectation
from semantic_action.supervision import assert_reset, supervise, settle_and_capture
from semantic_action.provider_contract import provider_graph
from semantic_action.multistep_evaluation import run_pilot
from .guard import verify_runtime

ROOT = Path(__file__).resolve().parents[1]
def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(task, provider, condition, output, root=ROOT, budget=60, delay=0, contaminate=None, stall=0):
    if provider not in {'a', 'b'} or condition not in {'A', 'B', 'C'}:
        raise ValueError('Visible providers and three conditions only')
    verify_runtime(root)
    output, root = Path(output).resolve(), Path(root).resolve()
    if task.task_id.startswith('M'):
        if contaminate not in (None, 'calls') or stall:
            raise ValueError('Unsupported multi-step probe')
        result = run_pilot(task, provider, condition, output, root, budget_seconds=budget,
                           delay_followup_seconds=delay, contaminate=bool(contaminate))
        if result.get('summary', {}).get('verified') and (result['process']['status'] != 'COMPLETED' or result['recovery']['state_uncertain']):
            raise RuntimeError('STOP: frozen timeout/uncertain outcome accepted')
        return result
    output.mkdir(parents=True, exist_ok=False)
    family = task.family
    permission = False if family == 'false_precondition' else None if family == 'unknown_precondition' else True
    mode = {'api_error':'error', 'no_state_change':'no_change', 'wrong_properties':'mismatch',
            'wrong_mapping':'mismatch', 'forbidden_side_effect':'side_effect'}.get(family, 'normal')
    options = dict(mode=mode, stale_precondition=family=='stale_permission', stale_observation=family=='stale_observation')
    state = Scenario(writable=permission, **options) if provider=='a' else BookingScenario(can_book=permission, **options)
    if contaminate == 'calls': state.calls = 7
    elif contaminate == 'revision': setattr(state, 'revision' if provider=='a' else 'version', 7)
    elif contaminate == 'permission': setattr(state, 'writable' if provider=='a' else 'can_book', False)
    elif contaminate == 'records': (state.events if provider=='a' else state.items)['unexpected'] = {'sentinel': True}
    elif contaminate == 'pending': state.pending_requests = 1
    elif contaminate == 'trace': save(output/'prior-action.json', {'preserve':True})
    elif contaminate is not None: raise ValueError('Unknown probe')
    journal = []
    def observer(phase, path, status):
        if phase == 'before':
            journal.append(dict(path=path, before=asdict(capture(provider,state)), after=None, http_status=None))
            save(output/'native-transitions.json',journal)
            if delay: sleep(delay)
        else:
            if family == 'wrong_mapping':
                for item in (state.events if provider=='a' else state.items).values():
                    item['advertised_title'] = task.goal.title
            journal[-1].update(after=asdict(capture(provider,state)), http_status=status)
            save(output/'native-transitions.json',journal)
    state.transition_observer = observer
    with (serve if provider=='a' else serve_bookings)(state) as (origin, state):
        before = capture(provider,state)
        try:
            assert_reset(before, dict(events={},writable=permission,revision=0,mutation_calls=0), output/'reset.json',
                         cache_entries=0,subject_alive=False,trace_directory_clean=not any(output.iterdir()),pending_requests=state.pending_requests)
        except ValueError:
            result=dict(task_id=task.task_id,provider=provider,condition=condition,status='RESET_REJECTED',subject_launched=False,verified=False)
            save(output/'evaluation.json',result)
            return result
        save(output/'curator-expectation.json',task.expectation(provider))
        data=json.loads((root/f'contracts/{"api_local" if condition=="A" else "providers"}/{provider}.json').read_text())
        if condition=='A':
            if family in {'misleading_effect','unsupported_transition'}: data['effect']='records_reservation_only'
            if family=='unsupported_transform': data['encoding']='unsupported_encoding'
            if family=='wrong_mapping': data['output_fields']['title']='advertised_title'
        else:
            if family in {'misleading_effect','unsupported_transition'}: data['declared_effects']=['https://example.org/sam/v1#ReservationRecorded']
            if family=='unsupported_transform': data['binding']['request_fields'][next(iter(data['binding']['request_fields']))]['source']='unavailable_input'
            if family=='wrong_mapping': data['binding']['event_fields']['title']['source']='advertised_title'
        manual=output/('manual.ttl' if condition=='C' else 'manual.json')
        if condition=='C': provider_graph(data).serialize(destination=manual,format='turtle')
        else: save(manual,data)
        source=output/'subject-input.json'
        save(source,dict(baseline_root=str(root),provider=provider,condition=condition,output=str(output),origin=origin,
             goal=task.goal.to_dict(),inputs={k:getattr(task.goal,k) for k in ('start_time','end_time','title')},
             manual=str(manual),operation_id=data.get('operation_id'),wire_fault=family,startup_stall_seconds=stall))
        process=supervise([sys.executable,'-m','preflight.single_subject',str(source)],output,budget_seconds=budget,cwd=ROOT)
        recovery=settle_and_capture(state,lambda:asdict(capture(provider,state)))
        after=capture(provider,state)
        subject={}
        partial_errors=[]
        if (output/'subject-result.json').exists():
            try: subject=json.loads((output/'subject-result.json').read_text())
            except (ValueError,OSError) as error: partial_errors.append(str(error))
        if partial_errors: save(output/'partial-trace-errors.json',partial_errors)
        action=subject.get('action')
        runtime=action.get('oracle_verdict') if action else None
        native=adjudicate(NativeExpectation(task.goal),before,after,action.get('execution_started',before.observed_at) if action else before.observed_at,runtime)
        expected=task.expectation(provider)
        unsafe=expected['mutation_calls']==0 and native['mutation_calls']>0
        summary=dict(compatible=subject.get('compatible'),applicability=subject.get('applicability'),mutation_calls=native['mutation_calls'],
            api_call_success=bool(action and action['api_call_success']),runtime_verified=bool(runtime and runtime['achieved']),
            native_verified=native['achieved'],unsafe_execution=unsafe,
            verified=bool(process['status']=='COMPLETED' and not recovery['state_uncertain'] and runtime and runtime['achieved'] and native['achieved'] and not unsafe))
        result=dict(task_id=task.task_id,family=family,provider=provider,condition=condition,summary=summary,process=process,
                    recovery=recovery,native_verdict=native,expected=expected,subject_launched=True,
                    diagnostic_passed=process['status']=='COMPLETED' and all(summary[k]==expected[k] for k in ('mutation_calls','runtime_verified','native_verified','verified')))
        result['classification'] = ('UNCERTAIN_LATE_EFFECT' if recovery['state_uncertain'] else
            'OUTER_TIMEOUT' if process['status']=='TIMEOUT' else 'PROCESS_ERROR' if process['status']!='COMPLETED' else
            'UNSAFE_MUTATION' if unsafe else 'VERIFIED_POSITIVE' if summary['verified'] else
            'SAFE_NEGATIVE_REJECTION' if expected['mutation_calls']==0 and native['mutation_calls']==0 else
            'NATIVE_RUNTIME_DISAGREEMENT' if summary['runtime_verified']!=summary['native_verified'] else 'UNVERIFIED_EXECUTION')
        save(output/'evaluation.json',result)
        if recovery['state_uncertain']:
            terminal=settle_and_capture(state,lambda:asdict(capture(provider,state)),maximum_wait_seconds=5)
            save(output/'terminal-observation.json',terminal)
            if terminal['state_uncertain']: raise RuntimeError('STOP: unsettled fixture after bounded drain')
    verify_runtime(root)
    return result
