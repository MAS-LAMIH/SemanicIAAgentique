"""Record real command/test work in a new ledger; historical records stay immutable."""
import argparse
import fcntl
import json
from pathlib import Path
import re
import subprocess
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from semantic_action.event_ledger import Event, Ledger
from semantic_action.model import now


def record(command, identity, log, cwd=ROOT):
    area = ROOT / 'docs/artifacts/milestone4_3'
    ledger = Ledger(area / 'events.jsonl')
    started, clock = now(), monotonic()
    target = area / log
    if target.exists():
        raise FileExistsError('Validation evidence already exists')
    with target.open('x') as stream:
        result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
    elapsed = monotonic() - clock
    text = target.read_text()
    count = re.search(r'Ran (\d+) tests in ([\d.]+)s', text)
    entry = {'id': identity, 'command': command, 'cwd': str(cwd), 'exit_code': result.returncode,
             'log_path': str(target.relative_to(ROOT)), 'elapsed_seconds': elapsed,
             'tests_run': int(count[1]) if count else None,
             'runner_seconds': float(count[2]) if count else None}
    ledger.append(Event(contributor_id='codex-validation', activity='testing', scope='shared_setup',
        resource_kind='automation', started_at=started, ended_at=now(), automated_runtime_minutes=elapsed / 60,
        outcome='passed' if result.returncode == 0 else 'failed', artifact_references=(entry['log_path'],),
        measurement_source='Measured parent monotonic subprocess runtime, actual command including setup/testing'))
    results = area / 'validation-results.json'
    with results.open('a+') as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.seek(0)
        previous = stream.read()
        saved = json.loads(previous) if previous else {'commands': [], 'approval': 'pending', 'unseal_authorized': False}
        saved['commands'].append(entry)
        stream.seek(0); stream.truncate()
        stream.write(json.dumps(saved, indent=2) + '\n')
        stream.flush()
    print(json.dumps(entry, indent=2))
    return result.returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--log', required=True)
    parser.add_argument('--cwd', default=str(ROOT))
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    raise SystemExit(record(command, args.id, args.log, Path(args.cwd)))
