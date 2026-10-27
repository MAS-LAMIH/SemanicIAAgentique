"""Record actual command runtimes in new pilot evidence, never historical ledgers."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from time import monotonic
from semantic_action.event_ledger import Event, Ledger

AREA = Path(__file__).resolve().parents[1] / 'docs/artifacts/v4_pilot'


def main():
    name, command = sys.argv[1], sys.argv[2:]
    if command[:1] == ['--']: command = command[1:]
    log = AREA / (name + '.log')
    start, clock = datetime.now(timezone.utc).isoformat(), monotonic()
    with log.open('x') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    duration, end = monotonic() - clock, datetime.now(timezone.utc).isoformat()
    count = re.search(r'Ran (\d+) tests in ([\d.]+)s', log.read_text())
    data = dict(command=command, cwd=str(Path.cwd()), PYTHONPATH='src', started_at=start, ended_at=end,
                exit_code=result.returncode, automated_runtime_seconds=duration,
                tests_run=int(count[1]) if count else None, runner_seconds=float(count[2]) if count else None,
                human_active_minutes=None, ai_supervision_minutes=None, tool_model_wait_minutes=None)
    (AREA / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n')
    Ledger(AREA / 'events.jsonl').append(Event(contributor_id='v4-pilot-automation', activity='testing',
        scope='shared_setup', resource_kind='automation', started_at=start, ended_at=end,
        automated_runtime_minutes=duration / 60, outcome='passed' if result.returncode == 0 else 'failed',
        artifact_references=(str(log),), measurement_source='Actual command monotonic runtime; not human integration effort'))
    print(json.dumps(data, indent=2))
    return result.returncode


if __name__ == '__main__': raise SystemExit(main())
