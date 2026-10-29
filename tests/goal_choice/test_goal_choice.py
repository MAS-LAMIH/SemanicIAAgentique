"""Choice, reconsideration, independent native truth and leakage-interface tests."""
from dataclasses import fields
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from experiments.goal_choice import Objective, ROOT, agent, assess, cases, run_episode, summarize
from semantic_action.model import Goal


class GoalChoiceTests(unittest.TestCase):
    def test_goal_contains_no_selected_operation(self):
        self.assertEqual({f.name for f in fields(Objective)}, {'event','allowed_artifacts'})

    def test_permission_flip_reconsiders_without_first_mutation(self):
        for policy in ('semantic','procedural'):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as d:
                r=run_episode(cases()[4],policy,Path(d)/'episode')
                self.assertTrue(r['passed']);self.assertEqual(r['choices'],['a','b'])
                self.assertEqual(r['calls'],[0,1]);self.assertTrue(r['independently_verified'])
                self.assertEqual(len(r['interventions']),1)
                trace=json.loads((Path(d)/'episode/worker/agent.json').read_text())
                self.assertEqual(len(trace['decisions']),2)
                config=json.loads((Path(d)/'episode/worker/input.json').read_text())
                self.assertEqual(set(config),{'event','allowed_artifacts','actions','policy'})
                self.assertFalse(any(k in config for k in ('case','expected','flip','state','delay')))
                modules=json.loads((Path(d)/'episode/worker/worker-modules.json').read_text())
                self.assertNotIn('semantic_action.native_verifier',modules)
                if policy=='procedural':
                    self.assertNotIn('semantic_action.registry',modules)
                    self.assertNotIn('semantic_action.contract',modules)

    def test_tie_break_is_independent_of_candidate_order(self):
        for policy in ('semantic','procedural'):
            with tempfile.TemporaryDirectory() as d:
                r=run_episode(cases()[2],policy,Path(d)/'episode',reverse=True)
                self.assertTrue(r['passed']);self.assertEqual(r['choices'],['a'])

    def test_existing_goal_stops_before_invocation(self):
        for policy in ('semantic','procedural'):
            with tempfile.TemporaryDirectory() as d:
                r=run_episode(cases()[8],policy,Path(d)/'episode')
                self.assertTrue(r['passed']);self.assertEqual(r['calls'],[0,0])
                self.assertTrue(r['independently_verified']);self.assertTrue(r['usable_id'])

    def test_native_extra_mutation_is_not_hidden_by_returned_id(self):
        with tempfile.TemporaryDirectory() as d:
            r=run_episode(dict(cases()[1],mode='side_effect'),'semantic',Path(d)/'episode')
            self.assertFalse(r['passed']);self.assertFalse(r['independently_verified'])
            self.assertTrue(r['unexpected_mutations']);self.assertGreaterEqual(r['unnecessary_mutations'],1)

    def test_uncertain_or_failed_dispatch_never_selects_alternate(self):
        goal=Goal('2030-01-07T10:00:00Z','2030-01-07T11:00:00Z','Test')
        objective=Objective(goal,('urn:artifact','urn:z'))
        snapshot=dict(complete=True,matching=[],contexts={},reads=[],candidates=[
          dict(artifact='urn:artifact',operation='urn:operation',eligible=True,reasons=[]),
          dict(artifact='urn:z',operation='urn:alternative',eligible=True,reasons=[])])
        for status,expected in [(None,'UNCERTAIN_MUTATION'),(500,'EXECUTION_FAILED')]:
            with tempfile.TemporaryDirectory() as d:
                p=Path(d);(p/'release-1').touch()
                action={'execution_decision':'EXECUTE','api_response':{'status':status,'body':{}},'oracle_verdict':None}
                with patch('experiments.goal_choice.assess',return_value=snapshot) as check, patch(
                    'semantic_action.registry.Registry.execute',return_value={'action':action,'resolution':{}}) as execute:
                    result=agent(objective,[], 'semantic',p)
                self.assertEqual(result['status'],expected);self.assertEqual(result['dispatches'],1)
                self.assertEqual(check.call_count,1);self.assertEqual(execute.call_count,1)

    def test_global_post_observation_required_before_success(self):
        goal=Goal('2030-01-07T10:00:00Z','2030-01-07T11:00:00Z','Test')
        objective=Objective(goal,('urn:artifact',))
        pre=dict(complete=True,matching=[],contexts={},reads=[],candidates=[
          dict(artifact='urn:artifact',operation='urn:operation',eligible=True,reasons=[])])
        post=dict(complete=False,matching=[],contexts={},reads=[],candidates=[])
        invocation={'execution_decision':'EXECUTE','api_response':{'status':201,'body':{'id':'new'}},'oracle_verdict':{'achieved':True}}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'release-1').touch()
            with patch('experiments.goal_choice.assess',side_effect=[pre,post]), patch(
                'semantic_action.registry.Registry.execute',return_value={'action':invocation,'resolution':{}}):
                result=agent(objective,[],'semantic',p)
            self.assertEqual(result['status'],'UNKNOWN_POST_STATE')
            self.assertEqual(result['dispatches'],1)

    def test_missing_effect_is_not_a_goal_contributing_candidate(self):
        from semantic_action.artifact import serve
        with tempfile.TemporaryDirectory() as d, serve() as (origin,state):
            data=json.loads((ROOT/'contracts/providers/a.json').read_text())
            data['declared_effects']=['https://example.org/sam/v1#ReservationRecorded']
            manual=Path(d)/'manual.json';manual.write_text(json.dumps(data))
            objective=Objective(Goal('2030-01-07T10:00:00Z','2030-01-07T11:00:00Z','Test'),(data['artifact_id'],))
            result=assess(objective,[dict(manual=str(manual),origin=origin,artifact=data['artifact_id'])],'semantic')
            self.assertFalse(result['candidates'][0]['eligible']);self.assertEqual(state.calls,0)
            self.assertIn('effects',str(result['candidates'][0]['reasons']))

    def test_summary_rejects_tampered_raw_evidence(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'raw').mkdir();f=p/'raw/item.json';f.write_text('{}')
            (p/'raw/sha256.json').write_text(json.dumps({'item.json':hashlib.sha256(f.read_bytes()).hexdigest()}))
            f.write_text('[]')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):summarize(p)


if __name__=='__main__':unittest.main()
