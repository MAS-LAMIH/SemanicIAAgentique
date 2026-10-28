"""Bounded goal-driven choice on existing V3 artifacts; no frozen-source edits.

Agent worker receives only objective and public bindings. Fixture controls and
native scoring stay in the parent process. Trusted deterministic code, not a sandbox.
"""
import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def matches(item, goal):
    from semantic_action.model import instant
    try:
        return (item['title'] == goal.title and instant(item['start_time']) == instant(goal.start_time)
                and instant(item['end_time']) == instant(goal.end_time))
    except (KeyError, TypeError, ValueError):
        return False


@dataclass(frozen=True)
class Objective:
    event: object  # unchanged V3 Goal
    allowed_artifacts: tuple[str, ...]


def assess(objective, actions, policy):
    """Public observation/description paths only; no fixture or oracle arguments."""
    from semantic_action.model import Truth
    from semantic_action.oracle import current
    from semantic_action.transport import HTTPTransport
    values = {k: getattr(objective.event, k) for k in ('start_time', 'end_time', 'title')}
    candidates, contexts, reads = [], {}, []
    if policy == 'semantic':
        from semantic_action.registry import Registry, Registration
        from semantic_action.contract import load_contract
        from semantic_action.transform import adapted_request
        registry = Registry([Registration(Path(a['manual']), a['origin']) for a in actions])
        resolution = registry.resolve(objective.event, inputs=values)
        for c, a in zip(resolution['candidates'], actions):
            contract = load_contract(a['manual'])
            def request(method, path, body=None):
                r = HTTPTransport(a['origin'])._http_request(method, path, body)
                reads.append(dict(artifact=c['artifact_id'], method=method, path=path, **asdict(r)))
                return r
            r = adapted_request(request, contract.profile, 'GET', '/calendar')
            contexts[c['artifact_id']] = r.body if r.success else None
            candidates.append(dict(artifact=c['artifact_id'], operation=c['operation_id'],
                 eligible=c['eligible'], reasons=list(c['reasons']), assessment=c['assessment']))
    elif policy == 'procedural':
        from semantic_action.local_baseline import CalendarLocal, BookingLocal
        for a in actions:
            local = (CalendarLocal if a['kind'] == 'calendar' else BookingLocal)(a['local'])
            r = HTTPTransport(a['origin'])._http_request('GET', local.permission_path)
            reads.append(dict(artifact=a['artifact'], method='GET', path=local.permission_path, **asdict(r)))
            try: evidence = local.state(r.body) if r.success else None
            except (ValueError, KeyError, TypeError, OverflowError): evidence = None
            contexts[a['artifact']] = evidence
            errors = local.validate(objective.event, values)
            truth = (Truth.UNKNOWN if not current(evidence, local.description['max_evidence_age_seconds'])
                     else Truth.TRUE if evidence.get('writable') is True
                     else Truth.FALSE if evidence.get('writable') is False else Truth.UNKNOWN)
            if truth != Truth.TRUE: errors.append('Current write permission is ' + truth)
            candidates.append(dict(artifact=a['artifact'], operation=local.operation,
                 eligible=not errors, reasons=errors, assessment={'applicability': truth, 'evidence': evidence}))
    else: raise ValueError('Unknown policy')
    for c in candidates:
        if c['artifact'] not in objective.allowed_artifacts:
            c['eligible'] = False; c['reasons'].append('Grounded effect targets a forbidden artifact')
    complete = bool(contexts) and len(contexts)==len(actions) and set(contexts)=={a['artifact'] for a in actions} and all(current(v, objective.event.max_evidence_age_seconds)
                   and isinstance(v.get('events'), dict) for v in contexts.values())
    found = [(artifact, key) for artifact, ctx in contexts.items() if isinstance(ctx, dict)
             for key, item in (ctx.get('events') or {}).items() if matches(item, objective.event)]
    return dict(candidates=candidates, contexts=contexts, reads=reads, complete=complete, matching=found)


def agent(objective, actions, policy, output):
    """No operation ID in the objective; two choices, at most one mutation dispatch."""
    from semantic_action.model import now
    output = Path(output); values = {k: getattr(objective.event, k) for k in ('start_time','end_time','title')}
    trace = dict(policy=policy, objective={'event': objective.event.to_dict(), 'allowed_artifacts': objective.allowed_artifacts},
                 status='RUNNING', decisions=[], dispatches=0, returned_id=None, selected_artifact=None)
    for cycle in (1, 2):
        snapshot = assess(objective, actions, policy)
        step = dict(cycle=cycle, observed_at=now(), **snapshot, selected=None, invocation=None)
        trace['decisions'].append(step); save(output/'agent.json', trace)
        if not snapshot['complete']:
            trace['status']='UNKNOWN_CONTEXT'; break
        found = snapshot['matching']
        if len(found) == 1 and found[0][0] in objective.allowed_artifacts:
            trace.update(status='SATISFIED_EXISTING', returned_id=found[0][1], selected_artifact=found[0][0]); break
        if found:
            trace['status']='INCONSISTENT_GOAL_STATE'; break
        eligible = sorted((c for c in snapshot['candidates'] if c['eligible']), key=lambda c:(c['artifact'], c['operation']))
        if not eligible:
            trace['status']='NO_ELIGIBLE_ACTION'; break
        chosen=eligible[0]; step['selected']=chosen
        save(output/'agent.json',trace)
        # Same generic decision barrier in every episode, every policy. No case labels/control data.
        save(output/f'intent-{cycle}.json', {'artifact':chosen['artifact'],'operation':chosen['operation']})
        deadline=time.monotonic()+10
        while not (output/f'release-{cycle}').exists():
            if time.monotonic()>deadline: raise TimeoutError('Decision barrier unavailable')
            time.sleep(.005)
        directory=output/f'action-{cycle}'; directory.mkdir()
        if policy=='semantic':
            from semantic_action.registry import Registry, Registration
            result=Registry([Registration(Path(a['manual']),a['origin']) for a in actions]).execute(
                   objective.event,chosen['operation'],directory,inputs=values)
            invocation=result['action']; step['resolution_recheck']=result['resolution']
        else:
            from semantic_action.local_baseline import CalendarLocal, BookingLocal, LocalExecutor
            a=next(a for a in actions if a['artifact']==chosen['artifact'])
            local=(CalendarLocal if a['kind']=='calendar' else BookingLocal)(a['local'])
            invocation=LocalExecutor(a['origin']).run(local,objective.event,values,directory/'action.json')
        step['invocation']=invocation
        if invocation and invocation['execution_decision']=='EXECUTE':
            trace.update(dispatches=1,selected_artifact=chosen['artifact'])
            body=(invocation.get('api_response') or {}).get('body',{})
            trace['returned_id']=body.get('id') if policy=='semantic' else local.response_id(body)
            response=invocation.get('api_response') or {}
            trace['status']='UNCERTAIN_MUTATION' if response.get('status') is None else 'EXECUTION_FAILED'
            if response.get('status') is not None and (invocation.get('oracle_verdict') or {}).get('achieved'):
                post=assess(objective,actions,policy);trace['post_observation']=post
                if not post['complete']:
                    trace['status']='UNKNOWN_POST_STATE'
                elif post['matching']==[(chosen['artifact'],trace['returned_id'])]:
                    frame_ok=True
                    for artifact,old in snapshot['contexts'].items():
                        records=dict(post['contexts'][artifact]['events'])
                        if artifact==chosen['artifact']:records.pop(trace['returned_id'],None)
                        frame_ok=frame_ok and records==old['events']
                        if artifact!=chosen['artifact']:
                            frame_ok=frame_ok and post['contexts'][artifact]['revision']==old['revision']
                    if frame_ok:trace['status']='SATISFIED_AFTER_ACTION'
            break  # No alternate dispatch, including after errors, bad effects or uncertainty.
        trace['status']='RECONSIDER_LIMIT'
        save(output/'agent.json',trace)
    trace['completed_at']=now(); save(output/'agent.json',trace)
    save(output/'worker-modules.json',sorted(n for n in sys.modules if n.startswith('semantic_action')))
    return trace


def cases():
    return [dict(id='G01',a=True,b=False,status='SATISFIED_AFTER_ACTION',choices=['a'],calls=[1,0]),
      dict(id='G02',a=False,b=True,status='SATISFIED_AFTER_ACTION',choices=['b'],calls=[0,1]),
      dict(id='G03',a=True,b=True,status='SATISFIED_AFTER_ACTION',choices=['a'],calls=[1,0]),
      dict(id='G04',a=False,b=False,status='NO_ELIGIBLE_ACTION',choices=[],calls=[0,0]),
      dict(id='G05',a=True,b=False,flip=True,status='SATISFIED_AFTER_ACTION',choices=['a','b'],calls=[0,1]),
      dict(id='G06',a=None,b=False,status='NO_ELIGIBLE_ACTION',choices=[],calls=[0,0]),
      dict(id='G07',a=True,b=False,stale=True,status='UNKNOWN_CONTEXT',choices=[],calls=[0,0]),
      dict(id='G08',a=True,b=True,delay=5.5,status='UNCERTAIN_MUTATION',choices=['a'],calls=[1,0]),
      dict(id='G09',a=True,b=True,existing=True,status='SATISFIED_EXISTING',choices=[],calls=[0,0]),
      dict(id='G10',a=False,b=True,only_a=True,status='NO_ELIGIBLE_ACTION',choices=[],calls=[0,0]),
      dict(id='G11',a=False,b=True,mode='no_change',status='EXECUTION_FAILED',choices=['b'],calls=[0,1])]


def run_episode(case, policy, output, reverse=False):
    """Evaluation parent; controls/answers/native handles never passed to agent worker."""
    from contextlib import ExitStack
    from copy import deepcopy
    from threading import Event, Thread
    from semantic_action.artifact import Scenario, serve
    from semantic_action.provider_b import BookingScenario, serve_bookings
    from semantic_action.model import Goal, now, instant
    from semantic_action.native_verifier import capture, adjudicate, NativeExpectation, _calendar, _booking
    from semantic_action.supervision import supervise, settle_and_capture, assert_reset
    output=Path(output); output.mkdir(parents=True,exist_ok=False); public=output/'worker';public.mkdir()
    goal=Goal('2030-01-07T10:00:00+00:00','2030-01-07T11:00:00+00:00','Decision test')
    artifacts={'a':'https://example.org/provider-a#calendar','b':'https://example.org/provider-b#appointments'}
    initial={'a':{'sentinel':dict(id='sentinel',start_time='2030-01-07T08:00:00+00:00',end_time='2030-01-07T09:00:00+00:00',title='Keep',metadata={'untouched':True})},
             'b':{'sentinel':dict(booking_ref='sentinel',begins_ms=1894003200000,finishes_ms=1894006800000,label='Keep',metadata={'untouched':True})}}
    if case.get('existing'):initial['a']['satisfied']=dict(id='satisfied',start_time=goal.start_time,end_time=goal.end_time,title=goal.title)
    states={'a':Scenario(writable=case['a'],events=deepcopy(initial['a']),stale_precondition=case.get('stale',False)),
            'b':BookingScenario(can_book=case['b'],items=deepcopy(initial['b']),mode=case.get('mode','normal'))}
    journal=[]
    def observer(provider, phase, path, status):
        journal.append(dict(provider=provider,phase=phase,path=path,status=status,state=asdict(capture(provider,states[provider])),at=now()))
        if phase=='before' and case.get('delay'):time.sleep(case['delay'])
    for p in states:states[p].transition_observer=lambda phase,path,status,p=p:observer(p,phase,path,status)
    clock=time.monotonic(); interventions=[]; stop=Event()
    with ExitStack() as stack:
        origins={p:stack.enter_context((serve if p=='a' else serve_bookings)(states[p]))[0] for p in states}
        before={p:capture(p,s) for p,s in states.items()}; pre_mutation=dict(before)
        for p,s in before.items():
            assert_reset(s,dict(events=initial[p],writable=case[p],revision=0,mutation_calls=0),output/f'reset-{p}.json',
                         cache_entries=0,subject_alive=False,trace_directory_clean=not any(public.iterdir()),pending_requests=states[p].pending_requests)
        allowed=[artifacts['a']] if case.get('only_a') else list(artifacts.values())
        actions=[dict(artifact=artifacts[p],manual=str(ROOT/f'contracts/providers/{p}.json'),
                      local=str(ROOT/f'contracts/api_local/{p}.json'),kind='calendar' if p=='a' else 'booking',origin=origins[p]) for p in states]
        if reverse:actions.reverse()
        save(public/'input.json',dict(event=goal.to_dict(),allowed_artifacts=allowed,actions=actions,policy=policy))
        def barrier():
            handled=set()
            while not stop.is_set():
                for cycle in (1,2):
                    f=public/f'intent-{cycle}.json'
                    if f.exists() and cycle not in handled:
                        if cycle==1 and case.get('flip'):
                            old={p:asdict(capture(p,s)) for p,s in states.items()}
                            states['a'].writable=False;states['b'].can_book=True
                            pre_mutation.update({p:capture(p,s) for p,s in states.items()})
                            interventions.append(dict(kind='authorized_permission_flip',before=old,after={p:asdict(s) for p,s in pre_mutation.items()},at=now()))
                        (public/f'release-{cycle}').touch();handled.add(cycle)
                stop.wait(.003)
        thread=Thread(target=barrier,daemon=True);thread.start()
        try: process=supervise([sys.executable,'-m','experiments.goal_choice','worker','--input',str(public/'input.json')],output,60,cwd=ROOT)
        finally:stop.set();thread.join(timeout=2)
        recovery={p:settle_and_capture(s,lambda p=p:asdict(capture(p,states[p])),maximum_wait_seconds=1.5) for p,s in states.items()}
        after={p:capture(p,s) for p,s in states.items()}
        trace=json.loads((public/'agent.json').read_text()) if (public/'agent.json').exists() else {}
        decode={'a':_calendar,'b':_booking}
        matching=[(p,k) for p,s in after.items() for k,item in s.events.items() if matches(decode[p](item),goal)]
        added={p:set(after[p].events)-set(before[p].events) for p in states}
        unchanged_existing=all(all(after[p].events.get(k)==v for k,v in before[p].events.items()) for p in states)
        calls=[after[p].mutation_calls-before[p].mutation_calls for p in ('a','b')]
        actual_choices=[next(p for p,a in artifacts.items() if a==d['selected']['artifact']) for d in trace.get('decisions',[]) if d.get('selected')]
        selected=next((p for p,a in artifacts.items() if a==trace.get('selected_artifact')),None)
        native={}
        for p in states:
            native[p]=adjudicate(NativeExpectation(goal),pre_mutation[p],after[p],before[p].observed_at)
        goal_state=bool(len(matching)==1 and artifacts[matching[0][0]] in allowed)
        id_usable=bool(goal_state and selected==matching[0][0] and trace.get('returned_id')==matching[0][1] and decode[selected](after[selected].events[matching[0][1]])['id']==trace['returned_id'])
        permissions_ok=all(after[p].writable==pre_mutation[p].writable for p in states)
        revisions_ok=all(after[p].revision-before[p].revision==len(added[p]) for p in states)
        wrong_additions=sum(artifacts[p] not in allowed or not matches(decode[p](after[p].events[k]),goal) for p in states for k in added[p])
        prior_matching=sum(matches(decode[p](item),goal) for p,s in before.items() for item in s.events.values())
        unnecessary=sum(after[p].events.get(k)!=v for p,s in before.items() for k,v in s.events.items())+wrong_additions+max(0,sum(len(v) for v in added.values())-wrong_additions-(0 if prior_matching else 1))
        unnecessary+=sum(after[p].writable!=pre_mutation[p].writable for p in states)
        unexpected=bool(not unchanged_existing or not permissions_ok or not revisions_ok or sum(len(v) for v in added.values())>1
              or any(artifacts[p] not in allowed or not matches(decode[p](after[p].events[k]),goal) for p in states for k in added[p]))
        clean=bool(not unexpected
                   and all(not v['state_uncertain'] for v in recovery.values()))
        # Native correct creation and unchanged nonselected artifact; satisfaction-existing needs no creation/revision.
        created_ok=bool(selected and native[selected]['achieved'] and all(after[p].events==before[p].events and after[p].revision==before[p].revision for p in states if p!=selected))
        verified=bool(goal_state and id_usable and clean and (created_ok if sum(calls) else len([(p,k) for p,s in before.items() for k,item in s.events.items() if matches(decode[p](item),goal)])==1 and all(after[p].events==before[p].events and after[p].revision==before[p].revision for p in states)))
        expected_state=case['id'] in {'G01','G02','G03','G05','G08','G09'}
        expected_verified=case['id'] in {'G01','G02','G03','G05','G09'}
        # A timeout can leave correct final state but no usable returned ID or accepted achievement.
        decision_correct=(actual_choices==case['choices'])
        passed=bool(process['status']=='COMPLETED' and trace.get('status')==case['status'] and decision_correct
              and calls==case['calls'] and clean and goal_state==expected_state and verified==expected_verified)
        row=dict(case=case['id'],policy=policy,passed=passed,selection_correct=decision_correct,status=trace.get('status'),
             choices=actual_choices,goal_state_satisfied=goal_state,independently_verified=verified,usable_id=id_usable,
             unnecessary_mutations=unnecessary,excess_mutating_requests=max(0,sum(calls)-(0 if case.get('existing') or not any(case['calls']) else 1)),
             calls=calls,clean=clean,unexpected_mutations=unexpected,worker_seconds=process['automated_runtime_seconds'],process=process,
             before={p:asdict(s) for p,s in before.items()},pre_mutation={p:asdict(s) for p,s in pre_mutation.items()},
             after={p:asdict(s) for p,s in after.items()},native_creation_checks=native,recovery=recovery,interventions=interventions,
             expected=dict(status=case['status'],choices=case['choices'],calls=case['calls'],goal_state=expected_state,verified=expected_verified),
             agent_reported_success=trace.get('status') in {'SATISFIED_EXISTING','SATISFIED_AFTER_ACTION'},reverse_order=reverse)
        save(output/'native-journal.json',journal);save(output/'evaluation.json',row)
    row['whole_seconds']=time.monotonic()-clock;save(output/'evaluation.json',row);return row


def summarize(output):
    raw=output/'raw'
    for name,h in json.loads((raw/'sha256.json').read_text()).items():
        if hashlib.sha256((raw/name).read_bytes()).hexdigest()!=h:raise ValueError('Evidence hash mismatch: '+name)
    rows=json.loads((raw/'inventory.json').read_text()); derived=output/'derived';derived.mkdir(exist_ok=True)
    table=[{k:r[k] for k in ('case','policy','passed','selection_correct','status','choices','goal_state_satisfied','independently_verified','usable_id','calls','unnecessary_mutations','excess_mutating_requests','unexpected_mutations','worker_seconds','whole_seconds')} for r in rows]
    save(derived/'results.json',table)
    with (derived/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
    columns=('case','policy','status','choices','goal_state_satisfied','independently_verified','calls','passed')
    text=['# Bounded goal-choice results','','| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    text+=['| '+' | '.join(str(r[k]) for k in columns)+' |' for r in table];(derived/'table.md').write_text('\n'.join(text)+'\n')
    summary=dict(episodes=len(rows),passed=sum(r['passed'] for r in rows),selection_correct=sum(r['selection_correct'] for r in rows),
                 selector_policies=2,independently_authored_agents=0,controlled_provider_fixtures=2,human_authorship_independent=False,
                 source_stable=not json.loads((raw/'source-stability.json').read_text())['changed'],
                 parity_differences=[c['id'] for c in cases() if len([r for r in rows if r['case']==c['id']])!=2 or len({(r['status'],tuple(r['choices']),tuple(r['calls']),r['goal_state_satisfied'],r['independently_verified']) for r in rows if r['case']==c['id']})!=1])
    summary['verdict']='PASS' if json.loads((raw/'run-status.json').read_text())['status']=='completed' and len(rows)==22 and summary['passed']==22 and summary['source_stable'] and not summary['parity_differences'] else 'FAIL'
    save(derived/'summary.json',summary);print(json.dumps(summary,indent=2));return 0 if summary['verdict']=='PASS' else 1


def run(output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False);raw=output/'raw';raw.mkdir()
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in tracked if n}
    hashes['experiments/goal_choice.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    from importlib.metadata import version
    import platform
    save(raw/'source.json',dict(dependencies={n:version(n) for n in ('rdflib','jsonschema','pyparsing')},platform=platform.platform(),revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),hashes=hashes,
         python=sys.version,ordering='serial; case G01..G11, semantic then procedural',repetitions=1,
         tie_break='lexicographic (artifact identity, operation identity), never registration order'))
    rows=[]; status='incomplete'; clock=time.monotonic()
    try:
        for case in cases():
            for policy in ('semantic','procedural'):
                path=raw/'episodes'/f'e{len(rows)+1:03d}'
                try:r=run_episode(case,policy,path)
                except Exception as e:
                    save(raw/'harness-failure.json',dict(case=case['id'],policy=policy,error=f'{type(e).__name__}: {e}'));raise
                rows.append(r);save(raw/'inventory.json',rows)
        status='completed'
    finally:
        save(raw/'cases.json',cases())
        save(raw/'inventory.json',rows)
        save(raw/'run-status.json',dict(status=status,completed_episodes=len(rows),elapsed_seconds=time.monotonic()-clock))
        save(raw/'source-stability.json',dict(changed=[n for n,h in hashes.items() if not (ROOT/n).is_file() or hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]))
        save(raw/'sha256.json',{str(p.relative_to(raw)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='sha256.json'})
    return summarize(output)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['worker','run','summarize']);parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args()
    if args.command=='worker':
        from semantic_action.model import Goal
        data=json.loads(args.input.read_text());agent(Objective(Goal(**data['event']),tuple(data['allowed_artifacts'])),data['actions'],data['policy'],args.input.parent);return 0
    if args.output is None:parser.error('--output required')
    return run(args.output) if args.command=='run' else summarize(args.output)


if __name__=='__main__':raise SystemExit(main())
