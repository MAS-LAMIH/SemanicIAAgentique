"""Linux subject-process supervision; service stays alive for independent recovery."""
import json
import math
import os
from pathlib import Path
import signal
import subprocess
from time import monotonic, sleep
from .model import now
from .event_ledger import Event, Ledger


def supervise(command, output, budget_seconds=60, ledger=None, cwd=None):
    if type(budget_seconds) not in (int, float) or not math.isfinite(budget_seconds) or budget_seconds <= 0:
        raise ValueError('Positive finite outer deadline required')
    output = Path(output)
    if (output / 'supervision.json').exists():
        raise FileExistsError('Do not overwrite supervision evidence')
    started, clock = now(), monotonic()
    report = {'status': 'STARTING', 'started_at': started, 'budget_seconds': budget_seconds,
              'automatic_retries': 0, 'process_alive_after_stop': None,
              'remote_side_effect_cancellation_claimed': False}
    def save():
        (output / 'supervision.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    with (output / 'subject.stdout').open('x') as stdout, (output / 'subject.stderr').open('x') as stderr:
        process = subprocess.Popen(command, cwd=cwd, stdout=stdout, stderr=stderr, start_new_session=True)
        report.update(pid=process.pid, status='RUNNING')
        save()
        timed_out = False
        try:
            process.wait(timeout=max(0.001, budget_seconds - (monotonic() - clock)))
        except subprocess.TimeoutExpired:
            timed_out = True
            report.update(status='TIMEOUT', uncertainty='In-flight remote effects unknown until independent observation')
            save()
        finally:
            # Stop the process group even if a child outlived a normally exited leader.
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)
        report.update(status='TIMEOUT' if timed_out else 'COMPLETED' if process.returncode == 0 else 'PROCESS_ERROR',
                      exit_code=process.returncode, process_alive_after_stop=process.poll() is None,
                      ended_at=now(), automated_runtime_seconds=monotonic() - clock)
        save()
    if ledger:
        Ledger(ledger).append(Event(contributor_id='supervisor', activity='execution', scope='task_execution',
            resource_kind='automation', started_at=started, ended_at=now(),
            automated_runtime_minutes=report['automated_runtime_seconds'] / 60,
            outcome=report['status'], artifact_references=(str(output / 'supervision.json'),),
            measurement_source='Parent monotonic process supervision; not human labor'))
    return report


def settle_and_capture(state, capture, maximum_wait_seconds=1.5):
    """A bounded fixture observation window, not a cancellation guarantee."""
    clock = monotonic()
    pending_at_stop = state.pending_requests
    while state.pending_requests and monotonic() - clock < maximum_wait_seconds:
        sleep(0.01)
    stable = state.pending_requests == 0
    return {'pending_at_stop': pending_at_stop, 'settled': stable,
            'wait_seconds': monotonic() - clock,
            'state_uncertain': not stable, 'snapshot': capture()}


def assert_reset(snapshot, expected, evidence, cache_entries, subject_alive, trace_directory_clean, pending_requests):
    from dataclasses import asdict
    actual = asdict(snapshot)
    # Timestamps and provider-native field names are not cross-provider semantic differences.
    checks = {key: actual[key] == expected[key] for key in ('events', 'writable', 'revision', 'mutation_calls')}
    checks.update(no_cached_resolutions=cache_entries == 0, no_live_subject=not subject_alive,
                  fresh_trace_directory=bool(trace_directory_clean), no_pending_requests=pending_requests == 0)
    report = {'passed': all(checks.values()), 'checks': checks, 'native_initial': actual,
              'expected': expected, 'cache_entries': cache_entries, 'subject_alive': subject_alive}
    Path(evidence).write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    if not report['passed']:
        raise ValueError('Reset contamination detected; subject not launched')
    return report
