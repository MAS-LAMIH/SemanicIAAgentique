"""Reproduce visible A/B apparatus only, preserving full native/subject evidence."""
import argparse
import json
from pathlib import Path
import sys
from time import monotonic
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from semantic_action.multistep_evaluation import run_pilot
from semantic_action.multistep_tasks import pilot_tasks
from semantic_action.supervision import supervise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--ledger')
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=False)
    records, failures = [], []
    def run(task, provider, condition, name, **options):
        result = run_pilot(task, provider, condition, output / name, ROOT, ledger=args.ledger, **options)
        records.append({'task_id': task.task_id, 'provider': provider, 'condition': condition,
                        'name': name, 'summary': result.get('summary'), 'status': result.get('status'),
                        'diagnostic_passed': result.get('diagnostic_passed'),
                        'result_path': str((output / name / 'evaluation.json').relative_to(output))})
        return result
    for task in pilot_tasks():
        for provider in ('a', 'b'):
            results = [run(task, provider, condition, f'{task.task_id}-{provider}-{condition}') for condition in ('A', 'B', 'C')]
            if not all(r['diagnostic_passed'] for r in results) or not all(r['summary'] == results[0]['summary'] for r in results):
                failures.append({'task': task.task_id, 'provider': provider, 'cause': 'Expected verdict or condition parity mismatch'})
    # A second explicit positive repetition on fresh fixtures/processes for both providers.
    for provider in ('a', 'b'):
        for condition in ('A', 'B', 'C'):
            result = run(pilot_tasks()[0], provider, condition, f'repetition-2-{provider}-{condition}')
            if not result['diagnostic_passed']:
                failures.append({'task': 'repetition-2', 'provider': provider, 'condition': condition})
    for condition in ('A', 'B', 'C'):
        result = run(pilot_tasks()[0], 'b', condition, f'inflight-timeout-b-{condition}', budget_seconds=1, delay_followup_seconds=1.5)
        if not (result['diagnostic_passed'] and result['summary']['mutation_calls'] == 2 and
                result['recovery']['settled'] and not result['summary']['verified']):
            failures.append({'task': 'inflight-timeout', 'condition': condition})
    result = run(pilot_tasks()[0], 'a', 'A', 'http-timeout-a-A', delay_followup_seconds=5.2)
    if not (result['diagnostic_passed'] and result['process']['status'] == 'COMPLETED' and not result['summary']['verified']):
        failures.append({'task': 'http-timeout'})
    rejected = run(pilot_tasks()[0], 'a', 'A', 'contaminated-reset-a-A', contaminate=True)
    if rejected['status'] != 'RESET_REJECTED' or rejected['subject_launched']:
        failures.append({'task': 'contaminated-reset'})
    stalled = output / 'isolated-stall'; stalled.mkdir()
    stalled_result = supervise([sys.executable, '-c', 'import time; time.sleep(30)'], stalled, 0.15, args.ledger)
    if stalled_result['status'] != 'TIMEOUT' or stalled_result['process_alive_after_stop']:
        failures.append({'task': 'isolated-stall'})
    result = {'status': 'passed' if not failures else 'failed', 'approval': 'pending', 'unseal_authorized': False,
              'scope': 'Visible development fixtures only; not independent held-out providers or confirmation',
              'diagnostic_tasks': 10, 'normal_matrix_runs': 60, 'additional_positive_repetitions': 6,
              'inflight_timeout_runs': 3, 'http_timeout_runs': 1, 'rejected_reset_attempts': 1,
              'isolated_stall_runs': 1, 'records': records, 'failures': failures}
    (output / 'pilot-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
