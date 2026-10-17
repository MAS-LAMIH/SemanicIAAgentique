"""Versioned candidate V2 builder/verifier. Historical Milestone 4 stays immutable."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'docs/artifacts/milestone4_1'
MANIFEST=ROOT/'docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    target=ROOT/path
    if target.is_symlink() or not target.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Unsafe source/artifact path')
    return digest(target.read_bytes())


def history():
    start=json.loads((AREA/'start-state.json').read_text())
    for path,expected in start['historical_immutable_files'].items():
        if file_hash(path)!=expected:
            raise ValueError('Historical evidence changed: '+path)
    old=json.loads((ROOT/'docs/SCIENTIFIC_FREEZE_MANIFEST.json').read_text())
    expected={p:h for group in old['file_groups'].values() for p,h in group.items()}
    archive=ROOT/'docs/artifacts/milestone4/candidate-source.tar.gz'
    with tarfile.open(archive,'r:gz') as stream:
        members=stream.getmembers()
        if len(members)!=len(expected) or {m.name for m in members}!=set(expected):
            raise ValueError('Historical archive coverage mismatch')
        for member in members:
            if not member.isfile() or digest(stream.extractfile(member).read())!=expected[member.name]:
                raise ValueError('Historical source archive corrupted')
    return {'manifest_sha256':file_hash('docs/SCIENTIFIC_FREEZE_MANIFEST.json'),
            'source_archive_sha256':file_hash('docs/artifacts/milestone4/candidate-source.tar.gz'),
            'historical_files_verified':len(start['historical_immutable_files']),
            'archive_members_verified':len(expected),'working_tree_comparison':'Not applicable: V2 intentionally changes code/documents, historical bytes are in the archive'}


def source_paths():
    raw=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode()
    paths=set()
    for path in raw.split('\0'):
        if not path or path=='docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json':
            continue
        if path.startswith('docs/artifacts/milestone4_1/') and path not in {
                'docs/artifacts/milestone4_1/start-state.json','docs/artifacts/milestone4_1/evaluation-requirements.txt'}:
            continue
        if any(part in {'__pycache__','.venv'} for part in Path(path).parts):
            continue
        if '/providers/c/' in path.lower() or path.lower().endswith('/providers/c.json') or 'provider_c.py' in path.lower():
            raise ValueError('Sealed provider implementation must not enter this candidate')
        paths.add(path)
    return sorted(paths)


def category(path):
    if path.startswith('docs/artifacts/milestone4/') or path in {'docs/SCIENTIFIC_FREEZE_MANIFEST.json','docs/freeze-manifest.json'}:
        return 'historical_evidence'
    if path.startswith('docs/protocols/'):
        return 'governing_research_protocol'
    if path.startswith('contracts/api_local/') or path=='src/semantic_action/local_baseline.py':
        return 'condition_A_provider_local'
    if path=='src/semantic_action/native_verifier.py':
        return 'independent_native_evaluation'
    if path=='src/semantic_action/event_ledger.py':
        return 'prospective_cost_collector'
    if path in {'src/semantic_action/transport.py','src/semantic_action/model.py','src/semantic_action/oracle.py'}:
        return 'neutral_transport_and_oracle'
    if path in {'src/semantic_action/evaluation.py','src/semantic_action/evaluation_tasks.py','docs/evaluation_tasks_v1.json'}:
        return 'prospective_tasks_and_harness'
    if path in {'src/semantic_action/artifact.py','src/semantic_action/provider_b.py'} or path.startswith('contracts/providers/'):
        return 'visible_provider_fixtures_and_shared_manuals'
    if path.startswith('src/semantic_action/') or path.startswith('contracts/'):
        return 'shared_semantic_infrastructure'
    if path.startswith('tests/'):
        return 'tests'
    if path.startswith('scripts/'):
        return 'reproducibility_tools'
    if path.startswith('docs/'):
        return 'documentation_and_provenance'
    return 'original_project_and_dependency_declarations'


def make_archive(paths):
    target=AREA/'candidate-source-v2.tar.gz'
    with target.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w',format=tarfile.PAX_FORMAT) as stream:
            for path in paths:
                data=(ROOT/path).read_bytes()
                info=tarfile.TarInfo(path)
                info.size=len(data)
                info.mode=0o644
                info.mtime=0
                stream.addfile(info,io.BytesIO(data))
    return target


def verify():
    previous=history()
    saved=json.loads(MANIFEST.read_text())
    files={p:h for group in saved['file_groups'].values() for p,h in group.items()}
    for path,expected in files.items():
        if file_hash(path)!=expected:
            raise ValueError('V2 source/protocol changed: '+path)
    if digest(json.dumps(files,sort_keys=True,separators=(',',':')).encode())!=saved['source_tree_sha256']:
        raise ValueError('Candidate identity mismatch')
    for item in saved['artifacts']:
        if file_hash(item['path'])!=item['sha256']:
            raise ValueError('V2 artifact changed: '+item['path'])
    with tarfile.open(AREA/'candidate-source-v2.tar.gz','r:gz') as stream:
        members=stream.getmembers()
        if len(members)!=len(files) or {m.name for m in members}!=set(files):
            raise ValueError('V2 archive coverage mismatch')
        for member in members:
            if not member.isfile() or digest(stream.extractfile(member).read())!=files[member.name]:
                raise ValueError('V2 archived source bytes mismatch')
    # No Git dependency for archive restoration. In a checkout, require full scope coverage.
    if (ROOT/'.git').exists():
        if set(source_paths())!=set(files):
            raise ValueError('Unclassified source addition/deletion')
    if saved['approval']['status']!='pending' or saved['unseal_authorized'] is not False:
        raise ValueError('Verifier cannot grant or authenticate scientific approval')
    print('V2 source, artifacts and historical Milestone 4 verified; approval pending, Provider C sealed.')


def prepare(wheel_source=None):
    prior=history()
    AREA.mkdir(parents=True,exist_ok=True)
    wheel=AREA/'tutorieliaagentique-0.1.0-py3-none-any.whl'
    if wheel_source:
        wheel.write_bytes(Path(wheel_source).read_bytes())
    if not wheel.is_file():
        raise ValueError('Retain the tested wheel with --wheel-source')
    files=source_paths()
    groups={}
    for path in files:
        groups.setdefault(category(path),{})[path]=file_hash(path)
    flattened={p:h for group in groups.values() for p,h in group.items()}
    make_archive(files)
    artifacts=[{'path':str(p.relative_to(ROOT)),'sha256':file_hash(str(p.relative_to(ROOT))),'bytes':p.stat().st_size}
               for p in sorted(AREA.rglob('*')) if p.is_file()]
    environment=json.loads((AREA/'evaluation-environment.json').read_text())
    validation=json.loads((AREA/'validation-results.json').read_text())
    source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest={'schema_version':2,'status':'technically_validated_candidate_pending_investigator_review',
        'approval':{'status':'pending','approver':None,'approved_at':None,'detached_approval_record':None},
        'unseal_authorized':False,'generated_at':datetime.now(timezone.utc).isoformat(),
        'source_commit_sha':source_sha,
        'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        'source_commit_note':'Implementation commit; final candidate metadata may be committed separately. Exact tested identity is source_tree_sha256 plus archive.',
        'uncommitted_scoped_changes':bool(subprocess.check_output(['git','status','--porcelain','--',*files],cwd=ROOT,text=True)),
        'source_tree_sha256':digest(json.dumps(flattened,sort_keys=True,separators=(',',':')).encode()),
        'file_groups':groups,'artifacts':artifacts,'historical_candidate':prior,
        'governing_protocol':{'path':'docs/protocols/ESWC_2027_Frozen_Research_and_Experimental_Protocol.pdf',
            'sha256':file_hash('docs/protocols/ESWC_2027_Frozen_Research_and_Experimental_Protocol.pdf'),
            'role':'User supplied governing pilot protocol; not scientific approval of this candidate'},
        'environment':environment,'validation':validation,
        'technical_gates':{'condition_A_on_visible_providers':'implemented_and_tested',
            'native_state_verification':'implemented; organizational independence still needs external review',
            'cost_collector':'implemented; actual human observations remain null when unmeasured',
            'three_condition_correctness_parity':'tested on 20 public diagnostics x 2 visible providers x 3 conditions',
            'B_C_information_parity':'typed profile equality and existing differential tests',
            'prospective_parameters':'proposed, not approved','Provider_C':'not unsealed or implemented'},
        'human_approval_required':['Exact candidate digest and source identity','Independent manual authors/integrators and exposure declarations',
            'Native observer/task expectations review','20 diagnostic scope versus full pilot multi-step goals',
            'Repetitions/seeds/order/budgets/stopping rules','Cost collector/allocation and external labor measurement',
            'Future sealed provider and held-out task/oracle custodianship'],
        'limitations':['One AI contributor previously exposed to shared manuals; no independent authoring or human cost inference',
            'One bounded calendar capability, fixed transforms, local fixtures, single writer',
            '20 public single-action apparatus diagnostics are not the full confirmatory benchmark or sealed task set',
            'Unmeasured historical effort remains unknown; hash chain does not authenticate human truth',
            'No LLM planner, no multi-step planner, no Provider C implementation'],
        'verification_command':'python3 scripts/candidate_v2.py --verify',
        'historical_verification_command':'python3 scripts/candidate_v2.py --verify-history'}
    MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    verify()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true')
    group.add_argument('--verify',action='store_true')
    group.add_argument('--verify-history',action='store_true')
    parser.add_argument('--wheel-source')
    args=parser.parse_args()
    if args.verify_history:
        print(json.dumps(history(),indent=2))
    elif args.verify:
        verify()
    else:
        prepare(args.wheel_source)


if __name__=='__main__':
    main()
