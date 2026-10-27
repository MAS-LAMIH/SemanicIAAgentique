"""Single-action A/B pilot; frozen supervision/reset helpers stay outside runtime."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
from time import monotonic, sleep
from semantic_action.artifact import Scenario, serve
from semantic_action.provider_b import BookingScenario, serve_bookings
from semantic_action.supervision import assert_reset, supervise, settle_and_capture
from .native import capture, initial_records, adjudicate
from .tasks import catalogue, expectation

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def reproducibility():
    files = sorted([*ROOT.glob('src/semantic_capability_v4/*.py'), *ROOT.glob('src/api_local_v4/*.py'),
                    *(ROOT / 'v4_pilot' / name for name in ('driver.py','native.py','tasks.py','worker.py')),
                    *ROOT.glob('v4/descriptions/*'), ROOT / 'src/semantic_action/artifact.py',
                    ROOT / 'src/semantic_action/provider_b.py', ROOT / 'src/semantic_action/supervision.py'])
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    bundle = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return dict(source_bundle_sha256=bundle, files=hashes, python=sys.version,
                executable=sys.executable, dependencies={p:importlib.metadata.version(p) for p in ('rdflib','pyparsing')})


def classify(process, result, native):
    if process['status'] == 'TIMEOUT':
        return 'correct_timeout_detection'
    if process['status'] != 'COMPLETED' or result is None:
        return 'process_error'
    if result['error_kind'] in ('input', 'resolution', 'http'):
        if not native['unchanged_state']:
            return 'unsafe_failure'
        return 'correct_http_rejection' if result['error_kind'] == 'http' else 'correct_rejection'
    if result['http_ok']:
        if result['error_kind'] is None and native['native_state_correct'] and native['output_usable']:
            return 'successful_creation'
        return 'correct_external_fault_detection'
    return 'unclassified_failure'


def run_attempt(task, provider, condition, output, *, contamination=None, budget_seconds=None, delay_seconds=None):
    if provider not in ('a', 'b') or condition not in ('A', 'B', 'C'):
        raise ValueError('Visible A/B providers and conditions A/B/C only')
    if contamination not in (None, 'calls', 'records', 'permission', 'revision', 'pending', 'trace'):
        raise ValueError('Unknown reset control')
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=False)
    clock, started = monotonic(), datetime.now(timezone.utc).isoformat()
    initial = initial_records(provider)
    state = (Scenario(events=deepcopy(initial), writable=task['permission'], mode=task['mode']) if provider == 'a' else
             BookingScenario(items=deepcopy(initial), can_book=task['permission'], mode=task['mode']))
    storage = state.events if provider == 'a' else state.items
    if contamination == 'calls': state.calls = 7
    if contamination == 'records': storage['unexpected'] = {'sentinel': 'do not clear'}
    if contamination == 'permission': setattr(state, 'writable' if provider == 'a' else 'can_book', not task['permission'])
    if contamination == 'revision': setattr(state, 'revision' if provider == 'a' else 'version', 7)
    if contamination == 'pending': state.pending_requests = 1
    if contamination == 'trace': save(output / 'previous-trace.json', {'retained': True})
    budget = budget_seconds if budget_seconds is not None else 1 if task['task_id'] == 'T16' else 60
    delay = task['delay_seconds'] if delay_seconds is None else delay_seconds
    journal = []
    def observer(phase, path, status):
        if phase == 'before':
            journal.append(dict(path=path, before=asdict(capture(provider, state)), after=None))
            save(output / 'native-transitions.json', journal)
            if delay: sleep(delay)
        else:
            if task['task_id'] == 'T13':
                storage['existing']['metadata'] = {'sentinel': 'unexpectedly changed'}
            journal[-1].update(after=asdict(capture(provider, state)), http_status=status)
            save(output / 'native-transitions.json', journal)
    state.transition_observer = observer
    with (serve if provider == 'a' else serve_bookings)(state) as (origin, state):
        before = capture(provider, state)
        expected_reset = dict(events=initial, writable=task['permission'], revision=0, mutation_calls=0)
        try:
            assert_reset(before, expected_reset, output / 'reset.json', cache_entries=0, subject_alive=False,
                         trace_directory_clean=not any(output.iterdir()), pending_requests=state.pending_requests)
        except ValueError:
            rejected = dict(task_id=task['task_id'], provider=provider, condition=condition,
                            status='RESET_REJECTED', subject_launched=False, contamination=contamination,
                            initial_native=asdict(before), duration_seconds=monotonic() - clock)
            save(output / 'evaluation.json', rejected)
            return rejected
        expected = expectation(task, provider)
        save(output / 'curator-expectation.json', {'task': task, 'expected': expected,
             'provenance': 'visible task + native service specifications; not runtime mappings; shared authorship'})
        config = dict(provider=provider, condition=condition, values=task['values'], origin=origin,
                      output=str(output), wire_fault=task['wire_fault'], unsupported=task['unsupported'])
        if condition != 'A':
            config['description'] = str(ROOT / f'v4/descriptions/{provider}.{"json" if condition == "B" else "ttl"}')
        save(output / 'subject-input.json', config)
        process = supervise([sys.executable, '-m', 'v4_pilot.worker', str(output / 'subject-input.json')],
                            output, budget_seconds=budget, cwd=ROOT)
        recovery = settle_and_capture(state, lambda: asdict(capture(provider, state)))
        after = capture(provider, state)
        result, parse_error = None, None
        if (output / 'invocation.json').exists():
            try: result = json.loads((output / 'invocation.json').read_text())
            except ValueError as error: parse_error = str(error)
        native = adjudicate(before, after, task['values'], result)
        summary = {key: native[key] for key in ('post_attempts', 'native_state_correct', 'unchanged_state',
                                               'unexpected_mutations', 'output_usable')}
        summary.update(classification=classify(process, result, native), supervision=process['status'],
                       error_kind='outer_timeout' if process['status'] == 'TIMEOUT' else result['error_kind'] if result else 'process',
                       http_status=result['http_status'] if result else None)
        passed = all(summary[key] == value for key, value in expected.items()) and not recovery['state_uncertain']
        evaluation = dict(task_id=task['task_id'], provider=provider, condition=condition, started_at=started,
                          expected=expected, summary=summary, invocation=result, native=native,
                          native_before=asdict(before), native_after=asdict(after), process=process, recovery=recovery,
                          uncertain_remote_outcome_at_stop=process['status'] == 'TIMEOUT' or bool(result and result['remote_outcome_unknown']),
                          state_uncertain_after_observation=recovery['state_uncertain'],
                          creation_accepted=summary['classification'] == 'successful_creation' and not recovery['state_uncertain'],
                          diagnostic_passed=passed, partial_trace_error=parse_error, subject_launched=True,
                          metadata=dict(python=platform.python_version(), reproducibility=reproducibility(),
                                        task_sha256=hashlib.sha256(json.dumps(task,sort_keys=True).encode()).hexdigest(),
                                        http_timeout_seconds=5, outer_timeout_seconds=budget,
                                        service_delay_seconds=delay, automatic_retries=0, source='visible diagnostic, not confirmatory'))
        if recovery['state_uncertain']:
            terminal = settle_and_capture(state, lambda: asdict(capture(provider, state)), maximum_wait_seconds=5)
            save(output / 'terminal-observation.json', terminal)
            evaluation['terminal_state_uncertain'] = terminal['state_uncertain']
        save(output / 'evaluation.json', evaluation)
    evaluation['duration_seconds'] = monotonic() - clock
    save(output / 'evaluation.json', evaluation)
    return evaluation


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    from semantic_capability_v4.descriptions import load
    parity = {}
    for provider in ('a','b'):
        left, right = (load(ROOT / f'v4/descriptions/{provider}.{suffix}') for suffix in ('json','ttl'))
        if left != right: raise ValueError('JSON/RDF description mismatch')
        parity[provider] = asdict(left)
    save(output / 'frontend-parity.json', parity)
    tasks = catalogue(); save(output / 'catalogue.json', tasks)
    clock = monotonic(); rows = []
    for task in tasks:
        for provider in ('a', 'b'):
            for condition in ('ABC' if provider == 'a' else 'CBA'):
                path = output / 'attempts' / f'{task["task_id"]}-{provider}-{condition}'
                result = run_attempt(task, provider, condition, path)
                rows.append(dict(path=str(path.relative_to(output)), **result))
                save(output / 'attempt-inventory.json', rows)
                print(task['task_id'], provider, condition, result['diagnostic_passed'], flush=True)
    controls = []
    for provider in ('a', 'b'):
        for condition in 'ABC':
            path = output / 'reset-controls' / f'{provider}-{condition}'
            controls.append(run_attempt(tasks[0], provider, condition, path, contamination='calls'))
    save(output / 'reset-controls.json', controls)
    save(output / 'run-timing.json', dict(automated_elapsed_seconds=monotonic() - clock, diagnostic_attempts=len(rows),
                                        reset_controls=len(controls), human_active_minutes=None, ai_supervision_minutes=None,
                                        tool_model_wait_minutes=None, independent_provider_units=2, confirmatory=False))
    return 0 if all(r['diagnostic_passed'] for r in rows) and all(r['status']=='RESET_REJECTED' for r in controls) else 1


if __name__ == '__main__':
    raise SystemExit(main())
