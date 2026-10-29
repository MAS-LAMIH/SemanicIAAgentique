"""Post-e9fc92c finite-profile audit; no historical evidence is rewritten."""
from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph, RDF, Literal, URIRef, BNode
from experiments.aat.model import StateGoal, ROOM, NS, ContextSnapshot
from experiments.aat.rdf import load, AA
from experiments.aat.runtime import Runtime, ScriptedReasoner, candidates
from experiments.aat.native import Room, serve
from experiments.aat.study import DATA
from semantic_action.model import now


class ValidityTests(unittest.TestCase):
    def admit(self, graph, directory, name):
        path=Path(directory)/(name+'.ttl')
        path.write_text('\n'.join(' '.join(x.n3() for x in t)+' .' for t in reversed(sorted(graph,key=lambda t:tuple(map(str,t)))))+'\n')
        return load(path,hashlib.sha256(path.read_bytes()).hexdigest())

    def test_closed_profile_rejects_unsupported_semantics(self):
        # A matching test hash isolates validation; it is not human approval.
        for control in ('readiness','operator','subject','frame_missing','frame_extra',
                        'frame_literal','frame_blank','delta_bool','delta_two','revision',
                        'mutation','bounds','profile','extra_assertion','ambiguous_ready'):
            with self.subTest(control=control),tempfile.TemporaryDirectory() as d:
                g=Graph().parse(DATA/'room.ttl',format='turtle')
                u=next(g.subjects(RDF.type,AA.Usage));pre=g.value(u,AA.hasPrecond);post=g.value(u,AA.hasPostcond)
                if control=='readiness':g.set((pre,AA.readyProperty,AA.unknownReady))
                elif control=='operator':g.set((post,AA.rule,AA.multiplyInteger))
                elif control=='subject':g.set((post,AA.subject,URIRef('urn:wrong:thing')))
                elif control=='frame_missing':g.remove((u,AA.preserves,AA.sentinels))
                elif control.startswith('frame_'):
                    value={'frame_extra':AA.extra,'frame_literal':Literal(str(AA.sentinels)),'frame_blank':BNode()}[control]
                    g.add((u,AA.preserves,value))
                elif control=='delta_bool':g.set((post,AA.delta,Literal(True)))
                elif control=='delta_two':g.set((post,AA.delta,Literal(2)))
                elif control=='revision':g.set((post,AA.revisionIncrement,Literal(0)))
                elif control=='mutation':g.set((post,AA.mutationIncrement,Literal(2)))
                elif control=='bounds':g.set((pre,AA.minimum,Literal(30)))
                elif control=='profile':g.set((u,AA.profile,Literal('room-step/unknown')))
                elif control=='extra_assertion':g.add((post,AA.unsupported,Literal(True)))
                elif control=='ambiguous_ready':g.add((pre,AA.readyProperty,AA.unknownReady))
                with self.assertRaises(ValueError):self.admit(g,d,control)

    def test_unknown_predicate_in_memory_has_no_cooler_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.admit(Graph().parse(DATA/'room.ttl',format='turtle'),d,'valid')
            ctx=ContextSnapshot('urn:ctx',ROOM,23,True,True,0,0,'{}',now(),'{}')
            with self.assertRaisesRegex(ValueError,'Unsupported readiness'):
                candidates(StateGoal(ROOM,22),ctx,(replace(c.usages[0],ready_property=NS+'unknownReady'),))

    def test_loaded_graph_and_registration_invariance_with_actual_execution(self):
        for temperature,expected in ((21,'/heat'),(23,'/cool')):
            for variant in ('original','reordered','renamed_and_reverse_registration'):
                with self.subTest(temperature=temperature,variant=variant),tempfile.TemporaryDirectory() as d:
                    g=Graph().parse(DATA/'room.ttl',format='turtle')
                    if variant=='renamed_and_reverse_registration':
                        # Reverse lexical ordering of the two opaque Usage identifiers.
                        ids=sorted(g.subjects(RDF.type,AA.Usage),key=str)
                        renamed={ids[0]:URIRef('urn:opaque:z'),ids[1]:URIRef('urn:opaque:a')}
                        h=Graph()
                        for s,p,o in g:h.add((renamed.get(s,s),p,renamed.get(o,o)))
                        g=h
                    if variant=='original':c=load(DATA/'room.ttl',hashlib.sha256((DATA/'room.ttl').read_bytes()).hexdigest())
                    else:c=self.admit(g,d,variant)
                    if variant=='renamed_and_reverse_registration':
                        c=replace(c,usages=tuple(reversed(c.usages)),operations=tuple(reversed(c.operations)),
                                  artifact=replace(c.artifact,operations=tuple(reversed(c.artifact.operations))))
                    state=Room(temperature);views=[];delegate=ScriptedReasoner()
                    class RecordingReasoner:
                        def propose(self,view):
                            views.append(view);return delegate.propose(view)
                    with serve(state) as origin:
                        runtime=Runtime(c,origin,'semantic',StateGoal(ROOM,22),Path(d)/'worker')
                        runtime.barrier=lambda *args:None
                        result=runtime.run(RecordingReasoner())
                    self.assertTrue(result['verified'])
                    self.assertEqual([h['path'] for h in runtime.http if h['method']=='POST'],[expected])
                    self.assertEqual(state.temperature,22);self.assertEqual(state.mutations,1)
                    use_view=next(v for v in views if v.context and v.candidates)
                    self.assertEqual(use_view.context.temperature,temperature)
                    self.assertEqual(use_view.descriptions,runtime.descriptions)
                    self.assertEqual(use_view.feedback[-1].code,'OBSERVED')
                    self.assertEqual(use_view.feedback[-1].context,use_view.context)


if __name__=='__main__':unittest.main()
