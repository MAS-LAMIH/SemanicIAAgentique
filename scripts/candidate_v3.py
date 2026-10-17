"""New V3 candidate identity; never regenerate historical candidates or approval records."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'docs/artifacts/milestone4_3'
MANIFEST = ROOT / 'docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json'
STATIC = {'docs/artifacts/milestone4_3/start-state.json', 'docs/artifacts/milestone4_3/evaluation-requirements.txt'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def hash_file(path):
    target = ROOT / path
    if target.is_symlink() or not target.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Unsafe candidate file')
    return digest(target.read_bytes())


def history():
    saved = json.loads((AREA / 'start-state.json').read_text())
    for path, expected in saved['historical_hashes'].items():
        if hash_file(path) != expected:
            raise ValueError('Historical candidate/evidence changed: ' + path)
    # Verify the original V2 source archive itself, not the evolved V3 working source.
    old = json.loads((ROOT / 'docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json').read_text())
    files = {p: h for group in old['file_groups'].values() for p, h in group.items()}
    archive = ROOT / 'docs/artifacts/milestone4_1/candidate-source-v2.tar.gz'
    verify_archive(archive, files)
    for artifact in old['artifacts']:
        if hash_file(artifact['path']) != artifact['sha256']:
            raise ValueError('V2 artifact corruption')
    from candidate_v2 import history as m4_history
    previous = m4_history()
    return {'preserved_files': len(saved['historical_hashes']), 'V2_archived_files': len(files),
            'V2_manifest_sha256': hash_file('docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json'),
            'M4': previous, 'approval_records': 'Original M4.2 package/decision bytes retained, not new approval'}


def source_paths():
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    result = set()
    for path in paths:
        if not path or path == 'docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json':
            continue
        if path.startswith('docs/artifacts/milestone4_3/') and path not in STATIC:
            continue
        if '/providers/c/' in path.lower() or path.lower().endswith('/providers/c.json') or 'provider_c.py' in path.lower():
            raise ValueError('Sealed-provider implementation cannot enter this candidate')
        result.add(path)
    return sorted(result)


def file_group(path):
    if path in {'src/semantic_action/sequence.py', 'src/semantic_action/supervision.py'}:
        return 'bounded_orchestration_and_operational_supervision'
    if path == 'src/semantic_action/sequence_native.py':
        return 'whole_sequence_independent_native_evaluation'
    if path == 'src/semantic_action/sequence_bindings.py' or path.startswith('contracts/sequences/'):
        return 'finite_sequence_contract_frontends_and_bindings'
    if path.startswith('src/semantic_action/'):
        return 'engine_shared_semantics_and_visible_provider_code'
    if path.startswith('contracts/api_local/'):
        return 'condition_A_local_contracts'
    if path.startswith('tests/'):
        return 'tests'
    if path.startswith('docs/artifacts/') or path in {'docs/SCIENTIFIC_FREEZE_MANIFEST.json', 'docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json', 'docs/SCIENTIFIC_FREEZE_APPROVAL_PACKAGE.md', 'docs/SCIENTIFIC_FREEZE_DECISION_RECORD.json'}:
        return 'preserved_historical_evidence_and_provenance'
    return 'other_contracts_documentation_tools_and_original_project'


def verify_archive(archive, files):
    with tarfile.open(archive, 'r:gz') as stream:
        members = stream.getmembers()
        if len(members) != len(files) or {m.name for m in members} != set(files):
            raise ValueError('Source archive coverage mismatch')
        for member in members:
            if not member.isfile() or digest(stream.extractfile(member).read()) != files[member.name]:
                raise ValueError('Source archive bytes differ: ' + member.name)


def archive():
    paths = source_paths()
    files = {p: hash_file(p) for p in paths}
    target = AREA / 'candidate-source-v3.tar.gz'
    # Deterministic bytes allow comparison with the already tested restored archive.
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as stream:
            for path in paths:
                content = (ROOT / path).read_bytes()
                info = tarfile.TarInfo(path); info.size = len(content); info.mode = 0o644; info.mtime = 0
                stream.addfile(info, io.BytesIO(content))
    content = raw.getvalue()
    if target.exists() and target.read_bytes() != content:
        raise ValueError('Tested V3 archive would change; preserve it and rerun restoration under a new archive identity')
    target.write_bytes(content)
    verify_archive(target, files)
    return files


def prepare():
    previous = history()
    files = archive()
    scoped = subprocess.check_output(['git', 'status', '--porcelain', '--', *files], cwd=ROOT, text=True)
    if scoped.strip():
        raise ValueError('Commit scoped source/documentation before final candidate creation')
    validation = json.loads((AREA / 'validation-results.json').read_text())
    required = ['source_full', 'wheel_full', 'restored_full']
    by_id = {c['id']: c for c in validation['commands']}
    for identity in required:
        check = by_id.get(identity)
        if not check or check['exit_code'] != 0 or not check['tests_run']:
            raise ValueError('Missing successful final suite: ' + identity)
    if len({by_id[k]['tests_run'] for k in required}) != 1:
        raise ValueError('Final test counts differ')
    pilot = json.loads((AREA / 'pilot/pilot-results.json').read_text())
    if pilot['status'] != 'passed':
        raise ValueError('Retained pilot failed')
    groups = {}
    for path, checksum in files.items():
        groups.setdefault(file_group(path), {})[path] = checksum
    artifacts = [{'path': str(p.relative_to(ROOT)), 'sha256': hash_file(str(p.relative_to(ROOT))), 'bytes': p.stat().st_size}
                 for p in sorted(AREA.rglob('*')) if p.is_file()]
    manifest = {'schema_version': 3, 'status': 'technically_validated_candidate_pending_investigator_review',
        'approval': {'status': 'pending', 'approver': None, 'approved_at': None, 'detached_approval_record': None},
        'unseal_authorized': False, 'generated_at': datetime.now(timezone.utc).isoformat(),
        'source_commit_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
        'source_commit_note': 'Implementation/documentation commit; evidence/manifest committed separately; exact tested bytes are bound by source/archive digests.',
        'source_tree_sha256': digest(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()),
        'source_archive_sha256': hash_file('docs/artifacts/milestone4_3/candidate-source-v3.tar.gz'),
        'file_groups': groups, 'artifacts': artifacts, 'historical_preservation': previous,
        'environment': json.loads((AREA / 'environment.json').read_text()),
        'validation': validation, 'final_suite_ids': required,
        'pilot_summary': {k: v for k, v in pilot.items() if k != 'records'},
        'resource_summary': json.loads((AREA / 'resource-summary.json').read_text()),
        'unchanged_core': {p: hash_file(p) for p in ['src/semantic_action/registry.py','src/semantic_action/pipeline.py',
            'src/semantic_action/contract.py','src/semantic_action/provider_contract.py','src/semantic_action/transform.py',
            'src/semantic_action/local_baseline.py','src/semantic_action/native_verifier.py','src/semantic_action/oracle.py']},
        'limitations': ['Visible controlled A/B fixtures and same previously exposed AI author; independent human review pending',
            'Two/three-step immediate-predecessor event chains only; no autonomous planner, branching, updates or compensations',
            'New controlled follow-up endpoints are not evidence of naturally occurring independently authored provider capabilities',
            'Trusted in-process fixture journaling/clock/counters; remote cancellation and external state attestation not established',
            'Unknown historical human effort remains null; no empirical labor saving or provider-generalization claim',
            'Source/wheel tests and exposed-provider diagnostics are apparatus evidence, not confirmatory experiment'],
        'review_gates': ['Independent human manual/task/native-observer review','Roles and exposure/custody declarations',
            'Cost allocation and prospective labor collection','Scope/parameters/order/budgets/stopping/analysis approval',
            'Exact V3 identity approval and distinct later unsealing authorization'],
        'verification_command': 'python3 scripts/candidate_v3.py --verify'}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    verify()


def verify():
    previous = history()
    saved = json.loads(MANIFEST.read_text())
    files = {p: h for group in saved['file_groups'].values() for p, h in group.items()}
    if digest(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()) != saved['source_tree_sha256']:
        raise ValueError('V3 source-tree identity mismatch')
    for path, expected in files.items():
        if hash_file(path) != expected:
            raise ValueError('V3 source changed: ' + path)
    verify_archive(AREA / 'candidate-source-v3.tar.gz', files)
    for item in saved['artifacts']:
        if hash_file(item['path']) != item['sha256']:
            raise ValueError('V3 evidence changed: ' + item['path'])
    if {item['path'] for item in saved['artifacts']} != {str(p.relative_to(ROOT)) for p in AREA.rglob('*') if p.is_file()}:
        raise ValueError('Unclassified V3 evidence addition/deletion')
    if (ROOT / '.git').exists() and set(source_paths()) != set(files):
        raise ValueError('Unclassified V3 source addition/deletion')
    if saved['approval']['status'] != 'pending' or saved['unseal_authorized'] is not False:
        raise ValueError('Technical verifier cannot grant scientific approval')
    print(f'V3 verified: {len(files)} source files, {len(saved["artifacts"])} artifacts; historical candidates unchanged; approval pending, Provider C sealed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--archive-only', action='store_true')
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--verify', action='store_true')
    group.add_argument('--verify-history', action='store_true')
    args = parser.parse_args()
    if args.archive_only:
        archive()
    elif args.prepare:
        prepare()
    elif args.verify_history:
        print(json.dumps(history(), indent=2))
    else:
        verify()
