"""Visible A/B multi-step apparatus and supervision; never a generic planner."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import sys
from time import monotonic
from .artifact import Scenario, serve
from .provider_b import BookingScenario, serve_bookings
from .model import now
from .native_verifier import capture
from .sequence_native import ChainExpectation, verify_chain
from .supervision import assert_reset, supervise, settle_and_capture


def initial_records(provider):
    if provider == 'a':
        return {'existing': {'id': 'existing', 'start_time': '2030-01-06T09:00:00+00:00',
                             'end_time': '2030-01-06T10:00:00+00:00', 'title': 'Preserve me', 'metadata': 'sentinel'}}
    if provider == 'b':
        return {'existing': {'booking_ref': 'existing', 'begins_ms': 1893920400000,
                             'finishes_ms': 1893924000000, 'label': 'Preserve me', 'metadata': 'sentinel'}}
    raise ValueError('Only exposed fixtures A/B are available')


def run_pilot(task, provider, condition, output, root='.', budget_seconds=60, ledger=None,
              delay_followup_seconds=0, contaminate=False):
    if provider not in {'a', 'b'} or condition not in {'A', 'B', 'C'}:
        raise ValueError('Only visible A/B under the three conditions are supported')
    output, root = Path(output).resolve(), Path(root).resolve()
    output.mkdir(parents=True, exist_ok=False)
    goals = task.domain_goals()
    initial = initial_records(provider)
    options = {'followup_mode': {'intermediate_failure': 'error', 'recovery_boundary': 'error',
                'forbidden_side_effect': 'side_effect', 'noop_success': 'no_change'}.get(task.family, 'normal'),
               'permission_after_first': {'permission_revoked': 'false', 'unknown_permission': 'unknown',
                                         'stale_permission': 'stale'}.get(task.family, 'unchanged'),
               'followup_delay_seconds': delay_followup_seconds}
    fixture = Scenario(events=deepcopy(initial), **options) if provider == 'a' else BookingScenario(items=deepcopy(initial), **options)
    if contaminate:
        fixture.calls = 7
    journal = []
    def observer(phase, path, status):
        if phase == 'before':
            journal.append({'path': path, 'before': asdict(capture(provider, fixture)), 'after': None, 'http_status': None})
        else:
            journal[-1].update(after=asdict(capture(provider, fixture)), http_status=status)
        # Persist on the service side, independent of subject termination.
        (output / 'native-transitions.json').write_text(json.dumps(journal, indent=2) + '\n')
    fixture.transition_observer = observer
    server = serve if provider == 'a' else serve_bookings
    started = now()
    with server(fixture) as (origin, state):
        baseline = capture(provider, state)
        reset_expected = {'events': initial, 'writable': True, 'revision': 0, 'mutation_calls': 0}
        try:
            reset = assert_reset(baseline, reset_expected, output / 'reset.json', cache_entries=0,
                subject_alive=False, trace_directory_clean=not any(output.iterdir()), pending_requests=state.pending_requests)
        except ValueError:
            rejected = {'task_id': task.task_id, 'provider': provider, 'condition': condition,
                        'status': 'RESET_REJECTED', 'verified': False, 'subject_launched': False}
            (output / 'evaluation.json').write_text(json.dumps(rejected, indent=2) + '\n')
            return rejected
        # Freeze curator expectation before launching the subject; no subject output is a source.
        expectation = ChainExpectation(goals, deepcopy(initial))
        (output / 'curator-expectation.json').write_text(json.dumps({'source': 'domain task and native fixture specifications; independent human review pending',
            'formal_goals': [g.to_dict() for g in expectation.goals], 'initial_records': initial,
            'required_relation': 'each later event must reference the previous new event',
            'expected_calls': task.expected_calls, 'expected_native': task.expected_native,
            'expected_runtime': task.expected_runtime, 'expected_status': task.expected_status}, indent=2) + '\n')
        if condition == 'A':
            profile = root / f'contracts/api_local/{provider}-followup.json'
        else:
            profile = root / f'contracts/sequences/{provider}.{"json" if condition == "B" else "ttl"}'
        if task.family == 'unsafe_substitution':
            if condition == 'A':
                data = json.loads(profile.read_text()); data['effect'] = 'records_reservation_only'
                profile = output / 'misleading-local.json'; profile.write_text(json.dumps(data, indent=2) + '\n')
            elif condition == 'B':
                data = json.loads(profile.read_text()); data['effect'] = 'ReservationOnly'
                profile = output / 'misleading.json'; profile.write_text(json.dumps(data, indent=2) + '\n')
            else:
                from rdflib import Graph, Namespace, RDF, Literal
                ns = Namespace('https://example.org/sam/sequence/v1#')
                graph = Graph().parse(profile, format='turtle')
                node = next(graph.subjects(RDF.type, ns.Profile)); graph.set((node, ns.effect, Literal('ReservationOnly')))
                profile = output / 'misleading.ttl'; graph.serialize(destination=profile, format='turtle')
        subject = {'formal_goals': [g.to_dict() for g in goals], 'root': str(root),
                   'profile': str(profile), 'origin': origin, 'condition': condition, 'output': str(output)}
        source = output / 'subject-input.json'; source.write_text(json.dumps(subject, indent=2) + '\n')
        report = supervise([sys.executable, '-m', 'semantic_action.sequence', str(source)], output,
                           budget_seconds, ledger, cwd=root)
        recovery = settle_and_capture(state, lambda: asdict(capture(provider, state)))
        final = capture(provider, state)
        completed = [t for t in journal if t['after'] is not None]
        native = verify_chain(expectation, baseline, final, completed)
        trace = json.loads((output / 'sequence.json').read_text()) if (output / 'sequence.json').is_file() else None
        runtime = bool(trace and trace.get('runtime_verified'))
        calls = final.mutation_calls - baseline.mutation_calls
        verified = (report['status'] == 'COMPLETED' and not recovery['state_uncertain'] and runtime and native['achieved'])
        summary = {'status': trace['status'] if trace else 'NO_TRACE', 'supervision_status': report['status'],
                   'mutation_calls': calls, 'runtime_verified': runtime, 'native_verified': native['achieved'],
                   'verified': verified, 'verified_transitions': native['verified_transition_count'],
                   'partial_new_records': len(final.events) - len(initial), 'state_uncertain': recovery['state_uncertain']}
        expected = (calls == task.expected_calls and runtime == task.expected_runtime and native['achieved'] == task.expected_native
                    and summary['status'] == task.expected_status and report['status'] == 'COMPLETED')
        operational_intervention = None
        if delay_followup_seconds > budget_seconds:
            operational_intervention = 'expected_outer_timeout'
            expected = report['status'] == 'TIMEOUT' and not verified and not report['process_alive_after_stop']
        elif delay_followup_seconds > 5:
            operational_intervention = 'expected_http_timeout'
            expected = report['status'] == 'COMPLETED' and not runtime and not verified
        # Recovery is an explicit boundary: change service availability, perform no new action.
        recovery_boundary = None
        if task.family == 'recovery_boundary':
            state.followup_mode = 'normal'
            recovery_boundary = {'service_now_available': True, 'resume_performed': False,
                                 'automatic_retries': 0, 'calls_after_recovery': state.calls}
        result = {'task_id': task.task_id, 'family': task.family, 'provider': provider, 'condition': condition,
                  'started_at': started, 'formal_goals': [g.to_dict() for g in goals], 'summary': summary,
                  'native_verdict': native, 'native_journal': deepcopy(journal), 'recovery': recovery,
                  'recovery_boundary': recovery_boundary, 'operational_intervention': operational_intervention, 'diagnostic_passed': expected,
                  'source_of_expectations': 'Curator domain task, not subject trace or manual', 'reset': reset,
                  'process': report, 'runtime_trace': trace}
        (output / 'evaluation.json').write_text(json.dumps(result, indent=2) + '\n')
    result['fixture_server_closed'] = True
    (output / 'evaluation.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    import argparse
    from .multistep_tasks import pilot_tasks
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', required=True, choices=['a', 'b'])
    parser.add_argument('--condition', required=True, choices=['A', 'B', 'C'])
    parser.add_argument('--task', required=True, choices=[t.task_id for t in pilot_tasks()])
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--budget-seconds', type=float, default=60)
    parser.add_argument('--delay-followup-seconds', type=float, default=0)
    parser.add_argument('--ledger')
    args = parser.parse_args()
    task = next(t for t in pilot_tasks() if t.task_id == args.task)
    result = run_pilot(task, args.provider, args.condition, args.output_dir,
                       budget_seconds=args.budget_seconds, delay_followup_seconds=args.delay_followup_seconds, ledger=args.ledger)
    print(json.dumps({'diagnostic_passed': result['diagnostic_passed'], **result['summary']}, sort_keys=True))
    return 0 if result['diagnostic_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
