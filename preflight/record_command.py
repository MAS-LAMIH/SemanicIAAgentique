"""Record actual preflight commands; never write historical evidence or human costs."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from time import monotonic
from semantic_action.event_ledger import Event, Ledger

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'docs/artifacts/milestone4_5'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', required=True)
    p.add_argument('--cwd', default=str(ROOT))
    p.add_argument('--nested', action='store_true')
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    log = AREA / (a.id + '.log')
    started, clock = datetime.now(timezone.utc).isoformat(), monotonic()
    with log.open('x') as stream:
        result = subprocess.run(command, cwd=a.cwd, stdout=stream, stderr=subprocess.STDOUT)
    ended, duration = datetime.now(timezone.utc).isoformat(), monotonic() - clock
    count = re.search(r'Ran (\d+) tests in ([\d.]+)s', log.read_text())
    row = {'id': a.id, 'command': command, 'cwd': a.cwd, 'started_at': started, 'ended_at': ended,
           'exit_code': result.returncode, 'elapsed_seconds': duration,
           'tests_run': int(count[1]) if count else None, 'runner_seconds': float(count[2]) if count else None,
           'log_path': str(log.relative_to(ROOT)), 'nested_runtime': a.nested}
    (AREA / (a.id + '.json')).write_text(json.dumps(row, indent=2) + '\n')
    Ledger(AREA / 'events.jsonl').append(Event(contributor_id='preflight-automation', activity='testing',
        scope='shared_setup', resource_kind='note' if a.nested else 'automation',
        started_at=started, ended_at=ended, automated_runtime_minutes=None if a.nested else duration / 60,
        outcome='passed' if result.returncode == 0 else 'failed', artifact_references=(row['log_path'],),
        measurement_source='Actual monotonic subprocess runtime; parent nested duration kept as metadata only' if a.nested else 'Actual monotonic subprocess runtime, not human effort'))
    print(json.dumps(row, indent=2))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
