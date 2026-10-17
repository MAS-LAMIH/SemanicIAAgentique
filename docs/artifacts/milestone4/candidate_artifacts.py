"""Archive/verify an unapproved working-source candidate. No provider discovery."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT/'docs/artifacts/milestone4'
MANIFEST = ROOT/'docs/SCIENTIFIC_FREEZE_MANIFEST.json'
DOCUMENTS = ['docs/MILESTONE_4_FREEZE_AUDIT.md','docs/HELD_OUT_EVALUATION_PROTOCOL.md',
             'docs/COST_MEASUREMENT_PROTOCOL.md','docs/EXPERIMENTAL_PARITY_CHECKLIST.md']


def checked(path):
    candidate = ROOT/path
    if not candidate.resolve().is_relative_to(ROOT.resolve()) or candidate.is_symlink():
        raise ValueError('Unsafe candidate path '+path)
    if not candidate.is_file():
        raise ValueError('Missing candidate file '+path)
    return candidate


def sha(path):
    return hashlib.sha256(checked(path).read_bytes()).hexdigest()


def groups():
    old = json.loads((ROOT/'docs/freeze-manifest.json').read_text())
    result = {name:sorted(paths) for name,paths in old['groups'].items()}
    known = {p for paths in result.values() for p in paths}
    tracked = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    result['original_project_context'] = sorted(p for p in tracked if p and p not in known)
    result['scientific_protocol_and_audit'] = DOCUMENTS
    result['candidate_preparation_tools'] = ['docs/artifacts/milestone4/candidate_artifacts.py',
        'docs/artifacts/milestone4/evaluation-requirements.txt','docs/freeze-manifest.json']
    # Fail on new implementation files not classified by the audited M3 manifest.
    for directory in ['src','contracts','tests','scripts']:
        for path in (ROOT/directory).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix in {'.py','.json','.ttl'}:
                relative = str(path.relative_to(ROOT))
                if relative not in {p for paths in result.values() for p in paths}:
                    raise ValueError('Unclassified implementation file '+relative)
    return result


def archive(paths):
    target = ARTIFACTS/'candidate-source.tar.gz'
    with target.open('wb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as zipped:
        with tarfile.open(fileobj=zipped,mode='w',format=tarfile.PAX_FORMAT) as out:
            for name in sorted(paths):
                data = checked(name).read_bytes()
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o644
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ''
                out.addfile(info,io.BytesIO(data))
    return target


def verify():
    saved = json.loads(MANIFEST.read_text())
    for group in saved['file_groups'].values():
        for name,digest in group.items():
            if sha(name) != digest:
                raise ValueError('Source/protocol hash mismatch: '+name)
    for item in saved['artifacts']:
        if sha(item['path']) != item['sha256']:
            raise ValueError('Evidence/artifact hash mismatch: '+item['path'])
    expected = {p:h for group in saved['file_groups'].values() for p,h in group.items()}
    identity = hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if identity != saved['candidate_source_tree_sha256']:
        raise ValueError('Candidate identity digest mismatch')
    for directory in ['src','contracts','tests','scripts']:
        for path in (ROOT/directory).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix in {'.py','.json','.ttl'}:
                if str(path.relative_to(ROOT)) not in expected:
                    raise ValueError('Unclassified implementation addition')
    with tarfile.open(ARTIFACTS/'candidate-source.tar.gz',mode='r:gz') as source:
        members = source.getmembers()
        if len(members) != len(expected) or {m.name for m in members} != set(expected):
            raise ValueError('Source archive coverage mismatch')
        for member in members:
            if not member.isfile() or hashlib.sha256(source.extractfile(member).read()).hexdigest() != expected[member.name]:
                raise ValueError('Archived bytes mismatch '+member.name)
    if saved['approval']['status'] != 'pending' or saved['unseal_authorized'] is not False:
        raise ValueError('This helper verifies unapproved candidates, not approval records')
    print('Candidate file, archive-member and artifact hashes verified; scientific approval remains pending.')


def prepare(wheel_source=None):
    ARTIFACTS.mkdir(parents=True,exist_ok=True)
    wheel = ARTIFACTS/'tutorieliaagentique-0.1.0-py3-none-any.whl'
    if wheel_source:
        wheel.write_bytes(Path(wheel_source).read_bytes())
    if not wheel.is_file():
        raise ValueError('Supply the tested --wheel-source')
    grouping = groups()
    file_groups = {name:{path:sha(path) for path in paths} for name,paths in grouping.items()}
    all_files = {path:digest for group in file_groups.values() for path,digest in group.items()}
    source = archive(all_files)
    artifacts = []
    for path in sorted(ARTIFACTS.iterdir()):
        if path.is_file() and path.name not in {'candidate_artifacts.py','evaluation-requirements.txt'}:
            relative = str(path.relative_to(ROOT))
            artifacts.append({'path':relative,'sha256':sha(relative),'bytes':path.stat().st_size})
    environment = json.loads((ARTIFACTS/'evaluation-environment.json').read_text())
    results = json.loads((ARTIFACTS/'validation-results.json').read_text())
    provenance = {'base_commit_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
                  'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                  'tested_identity':'Per-file SHA-256 plus retained source archive; HEAD alone is insufficient',
                  'scientific_freeze_commit_sha':None,'approved_tag_or_archive_digest':None}
    manifest = {'schema_version':1,'candidate_kind':'auditable_working_source_freeze_candidate',
        'scientific_freeze_status':'not_approved','unseal_authorized':False,
        'generated_at':datetime.now(timezone.utc).isoformat(),'git':provenance,
        'candidate_source_tree_sha256':hashlib.sha256(json.dumps(all_files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'python_version':environment['python_version'],'platform':environment['platform'],
        'resolved_evaluation_dependencies':environment['packages'],
        'dependency_lock':'docs/artifacts/milestone4/evaluation-requirements.txt',
        'file_groups':file_groups,'artifacts':artifacts,'validation':results,
        'source_archive_scope':'All file_groups members, including uncommitted source and protocols; excludes this manifest, mutable run evidence, Git metadata, virtualenvs and credentials',
        'protocol_authority':{'pdf_available':False,'basis':'User-supplied frozen ESWC decisions and milestone briefs','document_digest':None},
        'approval':{'status':'pending','approver':None,'approved_at':None,'approved_manifest_sha256':None,
                    'unsealing_decision':None},
        'human_decisions_required':['Approve exact candidate source/artifact identity',
            'Complete and approve condition-A baseline before a three-condition study',
            'Approve independent native-state observation and oracle expectations',
            'Approve task counts/seeds/order/budgets/stopping rules',
            'Approve contributor blinding/exposure and independence',
            'Approve cost collector/allocation and experimental parity'],
        'known_limitations':['Milestone 3 source is not contained in base HEAD; retained source archive is authoritative for this candidate',
            'Condition A/API-local is not implemented as an experimental baseline',
            'Oracle trusts subject output mappings and complete snapshots; independent native-state workflow is prospective',
            'One calendar capability, fixed transforms/constraints, loopback-only REST and single-writer clocks',
            'No independently developed organizational providers or externally verified blinding',
            'Historic effort lacks human-active/supervision/wait decomposition',
            'Evaluation dependency pins retained, but complete platform/build artifact availability is not guaranteed',
            'Original live tutorial examples not validated; no Provider C or full confirmatory benchmark'],
        'approval_document':'docs/HELD_OUT_EVALUATION_PROTOCOL.md',
        'verification_command':'python3 docs/artifacts/milestone4/candidate_artifacts.py --verify'}
    MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(MANIFEST)
    verify()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--wheel-source')
    args = parser.parse_args()
    if args.prepare == args.verify:
        parser.error('Choose exactly one of --prepare or --verify')
    prepare(args.wheel_source) if args.prepare else verify()


if __name__ == '__main__':
    main()
