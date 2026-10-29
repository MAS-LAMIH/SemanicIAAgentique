"""Acquisition completion, explicit admission and unchanged-controller integration."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph,RDF
from experiments.aat.acquisition import acquire,AA
from experiments.aat.completion import complete,admit,sha,save
from experiments.aat.completion_study import prepare,episode
from experiments.aat.study import DATA,cases
from experiments.aat.rdf import load


class CompletionTests(unittest.TestCase):
    def inputs(self,d,doc=None):
        root=Path(d);source=DATA/'acquisition/room.json'
        if doc is not None:save(root/'source.json',doc);source=root/'source.json'
        bundle=root/'bundle';acquire(source,json.loads((DATA/'acquisition/room.config.json').read_text()),bundle)
        sc=json.loads((DATA/'room-completion.template.json').read_text())
        for key,name in (('source_sha256','source.json'),('structural_sha256','structural.ttl'),('provenance_sha256','provenance.json')):sc[key]=sha(bundle/name)
        return root,bundle,sc

    def test_completed_graph_preserves_extracted_bindings_and_manual_meaning(self):
        with tempfile.TemporaryDirectory() as d:
            root,bundle,sc=self.inputs(d);save(root/'sidecar.json',sc)
            record=complete(bundle,root/'sidecar.json',root/'completed');self.assertEqual(record['status'],'COMPLETED_UNAPPROVED')
            derived=load(root/'completed/candidate.ttl',record['graph_sha256'])
            manual=load(DATA/'room.ttl',sha(DATA/'room.ttl'))
            def meaning(c):
                return sorted((next(o.path for o in c.operations if o.id==u.operation),u.ready_property,u.minimum,u.maximum,u.delta,sorted(u.frame)) for u in c.usages)
            self.assertEqual(meaning(manual),meaning(derived));self.assertNotEqual({o.id for o in manual.operations},{o.id for o in derived.operations})
            source=Graph().parse(bundle/'structural.ttl',format='turtle');g=Graph().parse(root/'completed/candidate.ttl',format='turtle')
            for op in derived.operations:
                for p in (AA.method,AA.path):self.assertEqual(set(source.objects(next(s for s in source.subjects(RDF.type,AA.Operation) if str(s)==op.id),p)),set(g.objects(next(s for s in g.subjects(RDF.type,AA.Operation) if str(s)==op.id),p)))
            self.assertTrue(record['mapping']);self.assertNotIn('admitted',record)

    def test_missing_conflicting_unreviewed_and_unsupported_semantics_quarantine(self):
        for control in ('unknown','delta','operator','frame','subject','binding','observer','artifact','wire','missing'):
            with self.subTest(control=control),tempfile.TemporaryDirectory() as d:
                root,bundle,sc=self.inputs(d)
                if control=='unknown':sc['review']['status']='pending'
                elif control=='delta':sc['usages'][0]['post']['delta']=2
                elif control=='operator':sc['usages'][0]['post']['rule']='urn:unsupported'
                elif control=='frame':sc['usages'][0]['frame'].pop()
                elif control=='subject':sc['usages'][0]['pre']['subject']='urn:wrong'
                elif control=='binding':sc['usages'][0]['operation']='urn:wrong'
                elif control=='observer':sc['observation']['fields']['temperature']='urn:wrong'
                elif control=='artifact':sc['artifact']='urn:wrong'
                elif control=='wire':sc['usages'][0]['request_schema']='urn:wrong'
                else:del sc['usages'][0]['post']['delta']
                save(root/'sidecar.json',sc);r=complete(bundle,root/'sidecar.json',root/'completed')
                self.assertEqual(r['status'],'QUARANTINED')

    def test_structural_graph_and_provenance_cannot_be_forged_by_rehashing(self):
        for name in ('structural.ttl','provenance.json'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                root,bundle,sc=self.inputs(d)
                if name.endswith('ttl'):
                    p=bundle/name;p.write_text(p.read_text().replace('"/heat"','"/fake"'))
                else:
                    p=bundle/name;value=json.loads(p.read_text());value['assertions'][0]['sources'][0]['rule']='forged';save(p,value)
                sc['structural_sha256']=sha(bundle/'structural.ttl');sc['provenance_sha256']=sha(bundle/'provenance.json')
                save(root/'sidecar.json',sc);r=complete(bundle,root/'sidecar.json',root/'completed')
                self.assertEqual(r['status'],'QUARANTINED');self.assertIn('reconciliation',r['error'])

    def test_schema_and_observer_changes_require_more_than_matching_hashes(self):
        for scope in ('/heat','/state'):
            with self.subTest(scope=scope),tempfile.TemporaryDirectory() as d:
                doc=json.loads((DATA/'acquisition/room.json').read_text());op=doc['paths'][scope]
                if scope=='/heat':op['post']['requestBody']['content']['application/json']['schema']['properties']['expected_revision']['type']='string'
                else:op['get']['responses']['200']['content']['application/json']['schema']['properties']['temperature']['type']='string'
                root,bundle,sc=self.inputs(d,doc);save(root/'sidecar.json',sc)
                r=complete(bundle,root/'sidecar.json',root/'completed');self.assertEqual(r['status'],'QUARANTINED')

    def test_explicit_approval_binds_graph_and_all_reviewed_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            graph,decision=prepare('http://127.0.0.1:8000',Path(d)/'pipeline')
            root=Path(d)/'pipeline';self.assertTrue(decision['admitted'])
            approval=json.loads((root/'approval.json').read_text());approval['approved']=False;save(root/'declined.json',approval)
            with self.assertRaisesRegex(ValueError,'Explicit'):admit(root/'completed',root/'declined.json')
            approval['approved']=True;approval['graph_sha256']='0'*64;save(root/'wrong.json',approval)
            with self.assertRaisesRegex(ValueError,'hash mismatch'):admit(root/'completed',root/'wrong.json')
            p=root/'completed/sidecar.json';p.write_text(p.read_text()+' ')
            with self.assertRaisesRegex(ValueError,'input changed'):admit(root/'completed',root/'approval.json')

    def test_actual_acquired_graph_reconsiders_after_feedback(self):
        with tempfile.TemporaryDirectory() as d:
            row=episode(cases()[2],'acquired',Path(d)/'episode')
            self.assertTrue(row['passed']);self.assertEqual(row['guards'],['STALE_PROPOSAL','AUTHORIZED'])
            self.assertEqual([e['path'] for e in row['journal'] if e['kind']=='request'],['/cool'])
            modules=json.loads((Path(d)/'episode/worker/modules.json').read_text())
            self.assertNotIn('experiments.aat.completion_study',modules);self.assertNotIn('experiments.aat.native',modules)

    def test_unknown_and_unsupported_sidecar_never_launch_worker(self):
        for fault in ('unknown','unsupported'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as d:
                row=episode(dict(id=fault,temperature=21),'acquired',Path(d)/'episode',fault)
                self.assertTrue(row['passed']);self.assertFalse(row['worker_launched']);self.assertEqual(row['before'],row['after'])

    def test_plausible_but_incorrect_review_never_becomes_false_success(self):
        with tempfile.TemporaryDirectory() as d:
            row=episode(dict(id='wrong',temperature=21),'acquired',Path(d)/'episode','wrong-supported')
            self.assertTrue(row['passed']);self.assertEqual(row['status'],'POSTCONDITION_FAILED')
            self.assertFalse(row['accepted']);self.assertFalse(row['false_success']);self.assertEqual(row['after']['temperature'],20)


if __name__=='__main__':unittest.main()
