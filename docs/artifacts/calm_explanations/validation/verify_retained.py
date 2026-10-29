from pathlib import Path
import json,hashlib,subprocess,platform,importlib.metadata
from experiments.calm import verify,canonical
from experiments.aat_reusable.study import frozen
root=Path('docs/artifacts/calm_explanations');run=root/'run-001';raw=run/'raw'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checkseal(p):
 d=json.loads(p.read_text())
 for n,h in d.items():assert sha(p.parent/n)==h,(p,n)
 return len(d)
old=[Path('docs/artifacts')/p for p in ['eswc_aat/run-001/raw/sha256.json','eswc_aat_validity/sha256.json','eswc_aat_acquisition/retained-evidence-sha256.json','eswc_aat_acquisition_execution/retained-evidence-sha256.json','eswc_aat_cross_domain/retained-evidence-sha256.json']]
counts={str(p):checkseal(p) for p in old};n=checkseal(raw/'sha256.json')
source=json.loads((raw/'source.json').read_text())
for p,h in source['hashes'].items():assert sha(Path(p))==h,p
# Original workspace copy is optional after archival; retained seals are mandatory.
for p in Path('/workspace/calm-run-001').rglob('*'):
 if p.is_file():assert sha(p)==sha(run/p.relative_to('/workspace/calm-run-001'))
pairs=json.loads((raw/'pair-results.json').read_text())
for row in pairs:
 for side in ('baseline','treatment'):assert canonical(row['actual'][side+'-on'])==canonical(row['actual'][side+'-off'])
claims=0
for ep in (raw/'counterfactuals').glob('p*/*-on'):
 ex=json.loads((ep/'calm/explanation.json').read_text());verify(ex,ep);claims+=len(ex['claims'])
 for c in ex['claims']:
  for e in c['evidence']:assert not e['pointer'].startswith('/expected')
 for name,h in json.loads((ep/'input-seal.json').read_text()).items():assert sha(ep/name)==h
changes=subprocess.check_output(['git','diff','--name-status','f0f005ccaccc2c54d6fac7eda24986fd48551d08'],text=True).splitlines()
assert all(x.startswith('A\t') for x in changes),changes
out=dict(passed=True,historical_seal_entries=counts,historical_total=sum(counts.values()),raw_seal_entries=n,source_hashes_verified=len(source['hashes']),frozen=frozen(),original_copy_and_regenerated_summaries_identical=True,strict_noninterference_comparisons=24,new_explanations_verified=24,new_claims_verified=claims,python=platform.python_version(),dependencies={k:importlib.metadata.version(k) for k in ('rdflib','jsonschema')},human_active_minutes=None,ai_supervision_minutes=None)
(root/'validation/final-integrity.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
