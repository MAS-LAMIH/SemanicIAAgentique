"""Generate or verify an explicit preparation manifest; this does not freeze science."""
import argparse
import hashlib
from importlib.metadata import distributions
import json
from pathlib import Path
import platform
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'generic_engine': ['src/semantic_action/__init__.py','src/semantic_action/contract.py',
        'src/semantic_action/json_contract.py','src/semantic_action/provider_contract.py',
        'src/semantic_action/registry.py','src/semantic_action/transform.py','src/semantic_action/cost.py'],
    'shared_semantics_and_mapping_infrastructure': [
        'contracts/vocabulary.ttl','contracts/shared-capabilities.ttl',
        'src/semantic_action/schemas/contract-v1.schema.json','src/semantic_action/schemas/contract-v2.schema.json'],
    'validation_and_oracle': ['src/semantic_action/model.py','src/semantic_action/pipeline.py','src/semantic_action/oracle.py'],
    'provider_specific': ['src/semantic_action/artifact.py','src/semantic_action/provider_b.py',
        'contracts/calendar.ttl','contracts/calendar.json','contracts/providers/a.json',
        'contracts/providers/a.ttl','contracts/providers/b.json','contracts/providers/b.ttl','docs/providers/PROVIDER_B.md'],
    'evaluation_fixtures_and_commands': ['contracts/goal.json','src/semantic_action/__main__.py','src/semantic_action/reuse_demo.py'],
    'tests': ['tests/semantic_action/test_pipeline.py','tests/semantic_action/test_parity.py','tests/semantic_action/test_registry.py'],
    'dependencies_and_license': ['requirements-semantic.txt','requirements.txt','pyproject.toml','LICENSE'],
    'freeze_tools': ['scripts/freeze_manifest.py'],
    'documentation_and_cost_records': ['docs/IMPLEMENTATION_AUDIT.md','docs/ARCHITECTURE.md','docs/CONTRACT_SEMANTICS.md',
        'docs/MILESTONE_1.md','docs/MILESTONE_2.md','docs/MILESTONE_3_DESIGN.md','docs/MILESTONE_3.md',
        'docs/PROVIDER_C_FREEZE_PROCEDURE.md','docs/integration_work.jsonl']}


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def coverage():
    classified = {path for paths in GROUPS.values() for path in paths}
    discovered = set()
    for directory in ['src/semantic_action','tests/semantic_action','contracts','scripts']:
        for path in (ROOT/directory).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix in {'.py','.json','.ttl'}:
                discovered.add(str(path.relative_to(ROOT)))
    unknown = discovered - classified
    if unknown:
        raise ValueError('Unclassified implementation files: '+str(sorted(unknown)))
    for path in classified:
        if not (ROOT/path).is_file():
            raise ValueError('Missing classified file: '+path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='docs/freeze-manifest.json')
    parser.add_argument('--verify')
    args = parser.parse_args()
    coverage()
    groups = {name:{path:digest(path) for path in paths} for name,paths in GROUPS.items()}
    if args.verify:
        saved = json.loads((ROOT/args.verify).read_text())
        if saved['groups'] != groups:
            raise ValueError('Manifest does not match current classified source files')
        print('All classified source hashes match; this is not proof of a scientific freeze.')
        return
    manifest = {'schema_version':1,'status':'freeze_preparation_only',
                'generated_at':datetime.now(timezone.utc).isoformat(),
                'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                'python_version':platform.python_version(),'platform':platform.platform(),
                'resolved_environment_inventory':sorted(
                    [{'name':d.metadata['Name'],'version':d.version} for d in distributions()],key=lambda d:d['name'].lower()),
                'groups':groups,
                'exclusions':['The manifest itself (self-reference)','Original tutorial source/tests outside milestone module',
                              'Virtual environments, caches and run artifacts'],
                'held_out_provider_status':'No Provider C implemented or examined; future provenance review still required'}
    target = ROOT/args.output
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(target)


if __name__ == '__main__':
    main()
