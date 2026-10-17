"""Read-only baseline guard for an evaluator, not a new scientific candidate."""
import hashlib
import json
from pathlib import Path
import platform
import semantic_action

MANIFEST_SHA = '53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352'
CANDIDATE = '752da7b8de85dd38c7eee30a101b786ea4743821'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_runtime(root):
    root = Path(root).resolve()
    manifest = root / 'docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json'
    if sha(manifest) != MANIFEST_SHA:
        raise RuntimeError('STOP: immutable V3 manifest mismatch')
    saved = json.loads(manifest.read_text())
    package = Path(semantic_action.__file__).resolve().parent
    checked = 0
    for group in saved['file_groups'].values():
        for name, expected in group.items():
            if name.startswith(('src/semantic_action/', 'contracts/')):
                if sha(root / name) != expected:
                    raise RuntimeError('STOP: frozen source/contract changed: ' + name)
            if name.startswith('src/semantic_action/'):
                actual = package / name.removeprefix('src/semantic_action/')
                if sha(actual) != expected:
                    raise RuntimeError('STOP: loaded runtime differs from V3: ' + str(actual))
                checked += 1
    return {'candidate_commit': CANDIDATE, 'manifest_sha256': MANIFEST_SHA,
            'python_version': platform.python_version(), 'package_root': str(package),
            'runtime_members_checked': checked, 'matches_V3': True}
