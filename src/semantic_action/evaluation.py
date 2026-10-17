"""Evaluation-only visible A/B wiring and interventions; never generic discovery."""
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from time import monotonic
from unittest.mock import patch

from .artifact import Scenario, serve
from .contract import load_contract
from .event_ledger import Event, Ledger
from .local_baseline import CalendarLocal, BookingLocal, LocalExecutor
from .model import ApiResult, now
from .native_verifier import NativeExpectation, capture, adjudicate
from .provider_b import BookingScenario, serve_bookings
from .provider_contract import provider_graph
from .registry import Registry, Registration
from .transport import HTTPTransport


def run_case(task,provider,condition,output_dir,root='.',ledger=None):
    if condition not in {'A','B','C'} or provider not in {'a','b'}:
        raise ValueError('Only the three conditions on visible A/B fixtures are supported')
    root,output=Path(root),Path(output_dir)
    output.mkdir(parents=True,exist_ok=False)
    started,clock=now(),monotonic()
    family=task.family
    permission=False if family=='false_precondition' else None if family=='unknown_precondition' else True
    mode={'api_error':'error','no_state_change':'no_change','wrong_properties':'mismatch',
          'wrong_mapping':'mismatch','forbidden_side_effect':'side_effect'}.get(family,'normal')
    options={'mode':mode,'stale_precondition':family=='stale_permission','stale_observation':family=='stale_observation'}
    scenario=Scenario(writable=permission,**options) if provider=='a' else BookingScenario(can_book=permission,**options)
    server=serve if provider=='a' else serve_bookings
    raw_request=HTTPTransport._http_request
    with server(scenario) as (origin,state):
        before=capture(provider,state)
        def request(client,method,path,values=None):
            response=raw_request(client,method,path,values)
            if family=='wrong_mapping' and method=='POST' and response.success:
                storage=state.events if provider=='a' else state.items
                for item in storage.values():
                    item['advertised_title']=task.goal.title
            if method=='GET' and response.success:
                permission_path='/calendar' if provider=='a' else '/availability'
                if ((family=='missing_permission' and path==permission_path) or
                    (family=='missing_observation' and path!=permission_path)):
                    body=deepcopy(response.body)
                    body.pop('observed_at' if provider=='a' else 'sampled_at',None)
                    response=ApiResult(response.status,body,response.error)
            return response
        with patch.object(HTTPTransport,'_http_request',request):
            if condition=='A':
                data=json.loads((root/f'contracts/api_local/{provider}.json').read_text())
                if family in {'misleading_effect','unsupported_transition'}:
                    data['effect']='records_reservation_only'
                if family=='unsupported_transform':
                    data['encoding']='unsupported_encoding'
                if family=='wrong_mapping':
                    data['output_fields']['title']='advertised_title'
                path=output/'local-description.json'
                path.write_text(json.dumps(data,indent=2)+'\n')
                local=(CalendarLocal if provider=='a' else BookingLocal)(path)
                values={key:getattr(task.goal,key) for key in ('start_time','end_time','title')}
                action=LocalExecutor(origin).run(local,task.goal,values,output/'action.json')
                compatible=action['compatible']
                applicability=action['applicability'] if compatible else None
                resolution=None
            else:
                data=json.loads((root/f'contracts/providers/{provider}.json').read_text())
                if family in {'misleading_effect','unsupported_transition'}:
                    data['declared_effects']=['https://example.org/sam/v1#ReservationRecorded']
                if family=='unsupported_transform':
                    data['binding']['request_fields'][next(iter(data['binding']['request_fields']))]['source']='unavailable_input'
                if family=='wrong_mapping':
                    data['binding']['event_fields']['title']['source']='advertised_title'
                suffix='json' if condition=='B' else 'ttl'
                path=output/f'manual.{suffix}'
                if suffix=='json':
                    path.write_text(json.dumps(data,indent=2)+'\n')
                else:
                    provider_graph(data).serialize(destination=path,format='turtle')
                result=Registry([Registration(path,origin)]).execute(task.goal,data['operation_id'],output)
                resolution,action=result['resolution'],result['action']
                candidate=resolution['candidates'][0]
                compatible=candidate['compatible']
                applicability=candidate['applicability'] if compatible else None
        after=capture(provider,state)
        runtime=action.get('oracle_verdict') if action else None
        native=adjudicate(NativeExpectation(task.goal),before,after,
                          action.get('execution_started',before.observed_at) if action else before.observed_at,runtime)
        expected=task.expectation(provider)
        unsafe_execution=expected['mutation_calls']==0 and native['mutation_calls']>0
        summary={'compatible':compatible,'applicability':applicability,'mutation_calls':native['mutation_calls'],
                 'api_call_success':bool(action and action['api_call_success']),
                 'runtime_verified':bool(runtime and runtime['achieved']),
                 'native_verified':native['achieved'],'unsafe_execution':unsafe_execution,
                 'verified':bool(runtime and runtime['achieved'] and native['achieved'] and not unsafe_execution)}
        case_passed=all(summary[k]==expected[k] for k in ('mutation_calls','runtime_verified','native_verified','verified'))
        result={'task_id':task.task_id,'family':family,'provider':provider,'condition':condition,
                'formal_goal':task.goal.to_dict(),'summary':summary,'expected':expected,'case_passed':case_passed,
                'runtime_action':action,'resolution':resolution,'native_verdict':native}
        (output/'evaluation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    if ledger:
        Ledger(ledger).append(Event(contributor_id='controlled-apparatus',activity='testing',scope='task_execution',
            resource_kind='automation',provider_id=provider,condition_id=condition,task_id=task.task_id,
            started_at=started,ended_at=now(),automated_runtime_minutes=(monotonic()-clock)/60,
            outcome='expected_diagnostic_outcome' if case_passed else 'unexpected_diagnostic_outcome',
            artifact_references=({'path':str(output/'evaluation.json'),
                                  'sha256':hashlib.sha256((output/'evaluation.json').read_bytes()).hexdigest()},),
            measurement_source='monotonic controlled A/B diagnostic runtime; not human effort'))
    return result


def main():
    import argparse
    from .evaluation_tasks import proposed_tasks
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',choices=['a','b'],required=True)
    parser.add_argument('--condition',choices=['A','B','C'],required=True)
    parser.add_argument('--task',choices=[t.task_id for t in proposed_tasks()],default='D01')
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--ledger')
    args=parser.parse_args()
    task=next(t for t in proposed_tasks() if t.task_id==args.task)
    result=run_case(task,args.provider,args.condition,args.output_dir,ledger=args.ledger)
    print(json.dumps({'diagnostic_passed':result['case_passed'],**result['summary']},sort_keys=True))
    return 0 if result['case_passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
