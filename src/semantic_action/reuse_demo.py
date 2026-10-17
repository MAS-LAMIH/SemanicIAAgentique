"""Local architectural demonstration: same goal, declared capability, two APIs."""
import argparse
from contextlib import ExitStack
import json
from pathlib import Path
from time import monotonic
from .artifact import serve
from .contract import load_goal
from .cost import WorkEntry, log_work
from .model import now
from .provider_b import BookingScenario, serve_bookings
from .registry import Registry, Registration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--format',choices=['json','ttl'],default='json')
    parser.add_argument('--select',choices=['a','b'],default='b')
    parser.add_argument('--mode',choices=['normal','error','no_change','mismatch','side_effect'],default='normal')
    parser.add_argument('--permission',choices=['true','false','unknown'],default='true')
    parser.add_argument('--output-dir',required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True,exist_ok=True)
    with (output/'scenario.json').open('x') as stream:
        json.dump(vars(args),stream,indent=2,sort_keys=True)
    started,clock = now(),monotonic()
    goal = load_goal('contracts/goal.json')
    with ExitStack() as stack:
        a,_ = stack.enter_context(serve())
        b,_ = stack.enter_context(serve_bookings(BookingScenario(
            can_book={'true':True,'false':False,'unknown':None}[args.permission],mode=args.mode)))
        registrations = [Registration(Path(f'contracts/providers/{name}.{args.format}'),origin)
                         for name,origin in [('a',a),('b',b)]]
        registry = Registry(registrations)
        operation = ('https://example.org/provider-a#create_event' if args.select == 'a'
                     else 'https://example.org/provider-b#reserveAppointment')
        result = registry.execute(goal,operation,output)
    for candidate in result['resolution']['candidates']:
        print(candidate['operation_id'], 'eligible='+str(candidate['eligible']),candidate['reasons'])
    achieved = bool(result['action'] and result['action']['oracle_verdict'] and result['action']['oracle_verdict']['achieved'])
    log_work(output/'work.jsonl',WorkEntry(
        activity='Multi-provider architectural validation runtime only',contributor='reuse_demo',
        started_at=started,ended_at=now(),elapsed_minutes=(monotonic()-clock)/60,
        measurement_source='automatic_wall_clock_validation_only',
        notes='Excludes authoring, semantic mappings, setup, integration and human effort.'))
    print('goal_verified='+str(achieved))
    return 0 if achieved else 1


if __name__ == '__main__':
    raise SystemExit(main())
