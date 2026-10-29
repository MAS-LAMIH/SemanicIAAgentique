from dataclasses import replace,asdict
import json
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph,RDF,URIRef,Literal
from experiments.aat_reusable.profile import *
from experiments.aat_reusable.runtime import Runtime,Proposal,ScriptedReasoner,IrrelevantFirst
from experiments.aat.native import Room,serve
from semantic_action.model import now
D=Path('experiments/aat_reusable/data')
def catalog():return load(D/'room.ttl',sha(D/'room.ttl'))
def goal(c):
 s=next(s for s in c.slots if s.pointer=='/temperature');return Goal(c.thing,(Condition('Equal',s.id,22,unit=s.unit),))
class Tests(unittest.TestCase):
 def test_arithmetic_truth_unknown_overflow_and_no_hidden_baseline_semantics(self):
  c=catalog();s=next(s for s in c.slots if s.kind=='Int');ctx=Snapshot('x',c.thing,tuple((s.id,21 if s.kind=='Int' else True if s.kind=='Bool' else '{}') for s in c.slots),0,0,now(),'{}')
  cs=assess(c,goal(c),ctx);self.assertEqual(sum(x.contributes==Truth.TRUE for x in cs),1)
  self.assertEqual(evaluate((Condition('Equal',s.id,22,unit=s.unit),),{s.id:True}),Truth.UNKNOWN)
  self.assertEqual(all_truth((Truth.UNKNOWN,Truth.FALSE)),Truth.FALSE)
  self.assertEqual(all_truth((Truth.UNKNOWN,Truth.TRUE)),Truth.UNKNOWN)
  from experiments.aat_reusable.room_local import assess as local
  altered=replace(c,usages=tuple(replace(u,effects=tuple(replace(e,value=-e.value) for e in u.effects)) for u in c.usages))
  self.assertEqual(local(c,goal(c),ctx),local(altered,goal(c),ctx));self.assertNotEqual(assess(c,goal(c),ctx),assess(altered,goal(c),ctx))
 def test_synthetic_boolean_assignment_and_conjunctive_goals(self):
  b=Slot('urn:b','urn:p','Bool','/b');f=Slot('urn:f','urn:q','Bool','/f')
  u=Usage('urn:u','urn:o',(Condition('Equal','urn:f',True),),(Effect('SetBool','urn:b',True),),('urn:f',))
  c=Catalog('urn:a','urn:t',(b,f),(),(u,),'/view','/id','/time','/v','/n','hash')
  g=Goal('urn:t',(Condition('Equal','urn:b',True),Condition('Equal','urn:f',True)));validate_goal(c,g)
  ctx=Snapshot('x','urn:t',(('urn:b',False),('urn:f',True)),0,0,now(),'{}');candidate=assess(c,g,ctx)[0]
  self.assertEqual(candidate.contributes,Truth.TRUE);self.assertEqual(candidate.applicable,Truth.TRUE)
  self.assertEqual(assess(c,g,replace(ctx,values=(('urn:b',False),('urn:f',None))))[0].applicable,Truth.UNKNOWN)
  with self.assertRaises(ValueError):validate_goal(c,Goal('urn:t',(Condition('Equal','urn:b',1),)))
 def test_boolean_rdf_loader_and_nested_json_bindings_before_freeze(self):
  from experiments.aat_reusable.data_tools import write
  spec=json.loads((D/'room-spec.json').read_text());spec['slots'][0]['kind']='Bool'
  for key in ('unit','minimum','maximum'):spec['slots'][0].pop(key)
  for i,u in enumerate(spec['usages']):
   u['pre']=[dict(kind='Equal',slot=spec['slots'][1]['id'],value=True)]
   u['effects']=[dict(kind='SetBool',slot=spec['slots'][0]['id'],value=i==0)]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'synthetic.ttl';write(spec,p);c=load(p,sha(p));g=Goal(c.thing,(Condition('Equal',c.slots[0].id,True),))
   values=tuple((s.id,False if s.id==c.slots[0].id else True if s.kind=='Bool' else '{}') for s in c.slots)
   cs=assess(c,g,Snapshot('x',c.thing,values,0,0,now(),'{}'));self.assertEqual(sum(x.contributes==Truth.TRUE for x in cs),1)
  body={'guard':{'generation':None}};put(body,'/guard/generation',7);self.assertEqual(get(body,'/guard/generation'),7)

 def test_invalid_graphs_and_missing_approval_fail_closed(self):
  for fault in ('operator','predicate','subject','frame','overlap','bool_delta','unit','bounds','metadata','binding','review','extra'):
   with self.subTest(fault=fault),tempfile.TemporaryDirectory() as d:
    g=Graph().parse(D/'room.ttl',format='turtle');u=next(g.subjects(RDF.type,A.Usage));pre=g.value(u,A.hasPrecond);post=g.value(u,A.hasPostcond);e=g.value(post,U.effect)
    if fault=='operator':g.set((e,RDF.type,U.Unknown))
    elif fault=='predicate':g.set((g.value(pre,U.all),RDF.type,U.Unknown))
    elif fault=='subject':g.set((pre,A.subject,URIRef('urn:other')))
    elif fault=='frame':g.remove((u,U.frameSlot,g.value(u,U.frameSlot)))
    elif fault=='overlap':g.add((u,U.frameSlot,g.value(e,U.onSlot)))
    elif fault=='bool_delta':g.set((e,U.value,Literal(True)))
    elif fault=='unit':g.set((e,U.unit,URIRef('urn:other')))
    elif fault=='bounds':g.set((g.value(e,U.onSlot),U.maximum,Literal(17)))
    elif fault=='metadata':g.set((next(g.subjects(RDF.type,A.Artifact)),U.revisionPointer,Literal('/sentinels/nested')))
    elif fault=='binding':g.set((g.value(u,A.forOperation),A.path,Literal('http://bad')))
    elif fault=='review':g.set((next(g.subjects(RDF.type,A.Artifact)),A.reviewed,Literal(False)))
    else:g.add((u,U.extra,Literal(True)))
    p=Path(d)/'bad.ttl';g.serialize(destination=p,format='turtle')
    with self.assertRaises(ValueError):load(p,sha(p))
  with self.assertRaises(ValueError):load(D/'room.ttl','0'*64)
 def test_actual_room_heat_cool_finish_frame_fault_and_unknown(self):
  for t,mode,expected in ((21,'normal','SUCCESS'),(23,'normal','SUCCESS'),(22,'normal','SUCCESS'),(21,'unknown','UNKNOWN_CONTEXT'),(21,'stale','UNKNOWN_CONTEXT'),(21,'wrong','POSTCONDITION_FAILED'),(21,'frame','POSTCONDITION_FAILED')):
   with self.subTest(t=t,mode=mode),tempfile.TemporaryDirectory() as d,serve(Room(t,mode=mode)) as origin:
    c=catalog();r=Runtime(c,origin,goal(c),d);r.barrier=lambda *args:None;result=r.run();self.assertEqual(result['status'],expected)
 def test_stale_reconsideration_wrong_proposal_permit_and_false_finish(self):
  state=Room()
  with tempfile.TemporaryDirectory() as d,serve(state) as origin:
   c=catalog();r=Runtime(c,origin,goal(c),d);changed=[]
   def barrier(turn,stage,p):
    if stage=='intent' and not changed:state.intervene();changed.append(True)
   r.barrier=barrier;result=r.run();self.assertTrue(result['verified']);self.assertEqual([x['path'] for x in r.http if x['method']=='POST'],['/cool'])
  with tempfile.TemporaryDirectory() as d,serve(Room()) as origin:
   c=catalog();r=Runtime(c,origin,goal(c),d);r.barrier=lambda *args:None;self.assertTrue(r.run(IrrelevantFirst())['verified'])
  with tempfile.TemporaryDirectory() as d,serve(Room()) as origin:
   c=catalog();r=Runtime(c,origin,goal(c),d);ctx=r.observe();use=next(x for x in r.candidates(ctx) if x.contributes==Truth.TRUE);permit,_=r.authorize(Proposal('use',use.handle,ctx.id),ctx)
   self.assertTrue(r.execute(permit)['verified'])
   with self.assertRaises(ValueError):r.execute(permit)
   class Early:
    def propose(self,v):return Proposal('finish')
   r2=Runtime(c,origin,goal(c),Path(d)/'early');self.assertEqual(r2.run(Early())['status'],'PREMATURE_FINISH')
 def test_conflicting_candidates_abstain_for_semantic_and_local_assessments(self):
  c=catalog();target=next(s.id for s in c.slots if s.kind=='Int');flag=next(s.id for s in c.slots if s.pointer=='/heater_ready')
  us=[]
  for u in c.usages:
   o=next(o for o in c.operations if o.id==u.operation);es=(Effect('AddInt',target,1,next(s.unit for s in c.slots if s.id==target)),Effect('SetBool',flag,o.path=='/heat'))
   us.append(replace(u,effects=es,frame=tuple(s.id for s in c.slots if s.id not in (target,flag))))
  c=replace(c,usages=tuple(us))
  from experiments.aat_reusable.room_local import ambiguous
  for knowledge in (None,ambiguous):
   with tempfile.TemporaryDirectory() as d,serve(Room()) as origin:
    r=Runtime(c,origin,goal(c),d,knowledge);r.barrier=lambda *args:None;result=r.run();self.assertEqual(result['status'],'AMBIGUOUS');self.assertEqual(r.dispatches,0)
if __name__=='__main__':unittest.main()
