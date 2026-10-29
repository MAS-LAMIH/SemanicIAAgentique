from copy import deepcopy
import hashlib,json
from pathlib import Path
import shutil,tempfile,unittest
import jsonschema
from experiments.calm import build,verify,semantic,raw_atom
ROOT=Path('docs/artifacts/eswc_aat_cross_domain/run-001/raw')
SCHEMA=json.loads(Path('experiments/calm_schema.json').read_text())
ROWS=json.loads((ROOT/'inventory.json').read_text())
def episode(case,domain='room',condition='S',variant='original'):
 i=next(i for i,r in enumerate(ROWS,1) if (r['case'],r['domain'],r['condition'],r['variant'])==(case,domain,condition,variant))
 return ROOT/'episodes'/f'e{i:03d}'
def values(ex):return {c['id']:c['value'] for c in ex['claims']}
class CalmTests(unittest.TestCase):
 def test_all_historical_claims_supported_schema_and_deterministic(self):
  count=0
  for p in sorted((ROOT/'episodes').iterdir()):
   ex=build(p,ROOT/'sha256.json');jsonschema.validate(ex,SCHEMA);count+=verify(ex,p)
  self.assertGreater(count,1000)
  p=episode('D01');self.assertEqual(build(p,ROOT/'sha256.json'),build(p,ROOT/'sha256.json'))
 def test_false_and_unknown_alternatives_are_not_conflated(self):
  ex=build(episode('D06'));v=values(ex)
  self.assertTrue(any(v[c['record']]['applicable']=='UNKNOWN' for s in ex['steps'] for c in s['candidates']))
  self.assertTrue(any(v[a['truth']]=='UNKNOWN' for s in ex['steps'] for c in s['candidates'] for a in c['raw_preconditions']))
  self.assertEqual(v[ex['outcome']['verified']],False)
  cold=build(episode('D01'));v=values(cold)
  cool=next(v[c['record']] for s in cold['steps'] for c in s['candidates'] if v[c['record']]['contributes']=='FALSE')
  self.assertEqual(cool['applicable'],'TRUE') # Noncontributing, not inapplicable.
 def test_wrong_effect_frame_and_timeout_never_success_explanations(self):
  for domain in ('room','cabinet'):
   for case in ('D10','D11','D12'):
    ex=build(episode(case,domain));v=values(ex);self.assertFalse(v[ex['outcome']['verified']])
    if case=='D10':self.assertIn('FALSE',[v[c['truth']] for c in ex['outcome']['effect_comparisons']])
    if case=='D11':self.assertIn('FALSE',[v[c['truth']] for c in ex['outcome']['frame_comparisons']]);self.assertTrue(v[ex['outcome']['native_score']]['goal_state'])
    if case=='D12':self.assertEqual(v[ex['outcome']['status']],'UNCERTAIN_MUTATION');self.assertTrue(v[ex['outcome']['native_score']]['native_success'])
 def test_missing_evidence_and_permits_are_unavailable_not_invented(self):
  ex=build(episode('D08'));self.assertEqual(ex['coverage']['permit_contents']['status'],'unavailable');self.assertEqual(ex['coverage']['runtime_precondition_atoms']['status'],'unavailable')
  with tempfile.TemporaryDirectory() as d:
   shutil.copytree(episode('D01'),Path(d)/'input');p=Path(d)/'input';(p/'execution/worker/transcript.json').unlink();(p/'execution/worker/result.json').unlink()
   ex=build(p);self.assertEqual(ex['steps'],[]);self.assertIsNone(ex['outcome']['status']);self.assertEqual(ex['coverage']['candidate_aggregates']['status'],'unavailable')
 def test_tampered_evidence_claim_or_reference_rejects(self):
  p=episode('D01');ex=build(p,ROOT/'sha256.json');wrong=deepcopy(ex);wrong['claims'][0]['value']='invented'
  with self.assertRaises(ValueError):verify(wrong,p)
  wrong=deepcopy(ex);wrong['steps'][0]['proposal']='c99999'
  with self.assertRaises(ValueError):verify(wrong,p)
  wrong=deepcopy(ex);wrong['narrative']+='An invented cause.'
  with self.assertRaises(ValueError):verify(wrong,p)
  wrong=deepcopy(ex);next(c for c in wrong['claims'] if c['rule']=='raw_atom')['plane']='agent_record'
  with self.assertRaises(ValueError):verify(wrong,p)
  wrong=deepcopy(ex);wrong['claims'][0]['evidence'][0]['sha256']='0'*64
  with self.assertRaises(ValueError):verify(wrong,p)
 def test_identifier_and_registration_permutations_preserve_semantic_meaning(self):
  for domain in ('room','cabinet'):
   for condition in ('S','P'):
    for case in ('D01','D02','D08'):
     original=semantic(build(episode(case,domain,condition)))
     for variant in ('statement_source_order','opaque_identifiers','registration_order'):
      self.assertEqual(original,semantic(build(episode(case,domain,condition,variant))))
 def test_raw_replay_does_not_rewrite_stale_aggregate(self):
  ex=build(episode('D07'));v=values(ex)
  self.assertTrue(any(v[a['truth']]=='TRUE' for s in ex['steps'] for c in s['candidates'] for a in c['raw_preconditions']))
  self.assertTrue(all(v[c['record']]['applicable']=='UNKNOWN' for s in ex['steps'] for c in s['candidates']))
  self.assertEqual(raw_atom({'kind':'Equal','slot':'s','value':True},[['s',None]]),'UNKNOWN')
 def test_builder_reads_without_input_mutation(self):
  p=episode('D01');before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}
  build(p,ROOT/'sha256.json');after={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()};self.assertEqual(before,after)
if __name__=='__main__':unittest.main()
