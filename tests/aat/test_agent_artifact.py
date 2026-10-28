"""Metamodel, guard authority, reasoning feedback and native-truth tests."""
from dataclasses import replace, FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rdflib import Graph, RDF, Literal, URIRef
from experiments.aat.model import StateGoal, ROOM, Proposal, NS
from experiments.aat.rdf import load, AA
from experiments.aat.runtime import Runtime, ScriptedReasoner, ControllerView, candidates, definitions
from experiments.aat.native import Room, serve, score
from experiments.aat.study import DATA, cases, episode, admission_controls


def catalog():return load(DATA/'room.ttl',json.loads((DATA/'review.json').read_text())['graph_sha256'])


class AATTests(unittest.TestCase):
    def test_records_are_immutable_and_operations_are_not_usages(self):
        c=catalog();self.assertNotEqual({u.id for u in c.usages},{o.id for o in c.operations})
        self.assertEqual({u.delta for u in c.usages},{-1,1})
        with self.assertRaises(FrozenInstanceError):c.thing.id='other'
        with self.assertRaises(ValueError):StateGoal(ROOM,True)

    def test_invalid_unreviewed_and_unapproved_rdf_never_admitted(self):
        with tempfile.TemporaryDirectory() as d:
            result=admission_controls(Path(d));self.assertTrue(all(r['rejected'] for r in result))
            self.assertIn('delta',result[0]['reason']);self.assertIn('Unreviewed',result[1]['reason'])
        with self.assertRaises(ValueError):load(DATA/'room.ttl','0'*64)

    def test_model_delta_is_used_not_identifiers_or_order(self):
        from experiments.aat.model import ContextSnapshot
        from semantic_action.model import now
        ctx=ContextSnapshot('urn:test',ROOM,21,True,True,0,0,'{}',now(),'{}');c=catalog();goal=StateGoal(ROOM,22)
        renamed=tuple(replace(u,id='urn:opaque:'+str(i)) for i,u in enumerate(reversed(c.usages)))
        eligible=[a for a in candidates(goal,ctx,renamed) if a.applicable=='TRUE' and a.contributes]
        self.assertEqual(len(eligible),1)
        self.assertEqual(next(u.delta for u in renamed if u.id==eligible[0].handle),1)
        flipped=tuple(replace(u,delta=-u.delta) for u in c.usages)
        self.assertNotEqual([x.handle for x in candidates(goal,ctx,c.usages) if x.contributes],
                            [x.handle for x in candidates(goal,ctx,flipped) if x.contributes])
        # Procedural knowledge is native code and independent of RDF behavior fields.
        self.assertEqual(definitions(c,'procedural'),definitions(replace(c,usages=flipped),'procedural'))

    def test_native_atomic_conflict_and_correct_direct_operations(self):
        from semantic_action.transport import HTTPTransport
        state=Room()
        with serve(state) as origin:
            t=HTTPTransport(origin)
            self.assertEqual(t._http_request('POST','/heat',{'expected_revision':0}).status,201)
            self.assertEqual(state.temperature,22)
            self.assertEqual(t._http_request('POST','/cool',{'expected_revision':0}).status,409)
            self.assertEqual(state.mutations,1)
            self.assertEqual(t._http_request('POST','/cool',{'expected_revision':1}).status,201)
            self.assertEqual(state.temperature,21)
        self.assertEqual(state.mutations,2)

    def test_wrong_reasoner_proposal_cannot_bypass_effect_check(self):
        state=Room(23)
        with tempfile.TemporaryDirectory() as d,serve(state) as origin:
            r=Runtime(catalog(),origin,'semantic',StateGoal(ROOM,22),d);ctx=r.observe()
            heat=next(u for u in r.catalog.usages if u.delta==1)
            permit,feedback=r.authorize(Proposal('use',heat.id,ctx.id),ctx)
            self.assertIsNone(permit);self.assertEqual(feedback['code'],'NOT_AUTHORIZED');self.assertEqual(state.requests,0)

    def test_permit_is_single_use_and_not_forgeable_through_proposal(self):
        state=Room()
        with tempfile.TemporaryDirectory() as d,serve(state) as origin:
            r=Runtime(catalog(),origin,'semantic',StateGoal(ROOM,22),d);ctx=r.observe();u=next(u for u in r.descriptions if u.delta==1)
            self.assertIsNone(r.authorize(Proposal('use','http://bad',ctx.id),ctx)[0])
            permit,_=r.authorize(Proposal('use',u.id,ctx.id),ctx);result=r.execute(permit)
            self.assertTrue(result['verified'])
            with self.assertRaises(ValueError):r.execute(permit)
            self.assertEqual(state.mutations,1)

    def test_react_flip_contains_feedback_observation_and_new_choice(self):
        for policy in ('semantic','procedural'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'episode';r=episode(cases()[2],policy,p)
                self.assertTrue(r['passed']);self.assertEqual(r['choices'],['/heat','/cool'])
                trace=json.loads((p/'worker/result.json').read_text())['transcript']
                uses=[e for e in trace if e['proposal']['tool']=='use']
                self.assertEqual(uses[0]['feedback']['code'],'STALE_PROPOSAL')
                subsequent=trace[uses[0]['turn']]
                self.assertEqual(subsequent['proposal']['tool'],'observe')
                self.assertEqual(subsequent['view']['feedback'][-1]['code'],'STALE_PROPOSAL')
                mods=json.loads((p/'worker/modules.json').read_text());self.assertNotIn('experiments.aat.native',mods)
                config=json.loads((p/'worker/input.json').read_text());self.assertEqual(set(config),{'policy','origin','graph','approved_hash','goal'})

    def test_early_finish_and_missing_observation_do_not_claim_success(self):
        class Early:
            def propose(self,view):return Proposal('finish')
        with tempfile.TemporaryDirectory() as d,serve(Room()) as origin:
            r=Runtime(catalog(),origin,'semantic',StateGoal(ROOM,22),d);result=r.run(Early())
            self.assertEqual(result['status'],'PREMATURE_FINISH');self.assertFalse(result['verified']);self.assertEqual(r.dispatches,0)

    def test_native_scorer_rejects_wrong_delta_and_frame_without_semantics(self):
        before=Room().snapshot();after=dict(before,temperature=22,mutations=1,revision=1,sentinels={'changed':True})
        journal=[dict(kind='request',status=201,path='/heat',body={'expected_revision':0},before=before,after=after)]
        verdict=score(before,after,journal,22)
        self.assertFalse(verdict['native_success']);self.assertEqual(verdict['incorrect_native_transitions'],1)

    def test_runtime_context_and_goal_rdf_remain_distinct(self):
        with tempfile.TemporaryDirectory() as d,serve(Room(22)) as origin:
            r=Runtime(catalog(),origin,'semantic',StateGoal(ROOM,22),d);self.assertTrue(r.run()['verified'])
            g=Graph().parse(Path(d)/'contexts.ttl',format='turtle')
            self.assertEqual(len(set(g.subjects(RDF.type,AA.Goal))),1)
            self.assertGreater(len(set(g.subjects(RDF.type,AA.ContextSnapshot))),0)


if __name__=='__main__':unittest.main()
