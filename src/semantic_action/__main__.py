"""A complete local action, with persisted trace and measured validation runtime."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
from time import monotonic
from .artifact import Scenario, serve
from .contract import load_goal
from .cost import WorkEntry, log_work
from .model import now
from .pipeline import Executor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', default='contracts/calendar.ttl')
    parser.add_argument('--goal', default='contracts/goal.json')
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--mode', choices=['normal', 'error', 'no_change', 'mismatch', 'side_effect'],
                        default='normal')
    parser.add_argument('--writable', choices=['true', 'false', 'unknown'], default='true')
    args = parser.parse_args()
    goal = load_goal(args.goal)
    values = {key: getattr(goal, key) for key in ('start_time', 'end_time', 'title')}
    output = Path(args.output_dir)
    started, clock = now(), monotonic()
    scenario = Scenario(writable={'true': True, 'false': False, 'unknown': None}[args.writable],
                        mode=args.mode)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'scenario.json').open('x', encoding='utf-8') as stream:
        json.dump(asdict(scenario), stream, indent=2, sort_keys=True)
    with serve(scenario) as (base, _):
        trace = Executor(base).run(args.contract, goal, values, output / 'trace.json')
    log_work(output / 'work.jsonl', WorkEntry(
        activity='Run controlled Milestone 1 validation', contributor='semantic_action CLI',
        files=(str(output / 'trace.json'),), started_at=started, ended_at=now(),
        elapsed_minutes=(monotonic() - clock) / 60,
        measurement_source='automatic_wall_clock_validation_only',
        notes='Runtime only; excludes setup, implementation, annotation, mapping, and debugging effort.'))
    achieved = bool(trace['oracle_verdict'] and trace['oracle_verdict']['achieved'])
    print(f"decision={trace['execution_decision']} applicability={trace['applicability'].value} "
          f"api_success={trace['api_call_success']} goal_verified={achieved}")
    print(f"Trace: {output / 'trace.json'}")
    return 0 if achieved else 1


if __name__ == '__main__':
    raise SystemExit(main())
