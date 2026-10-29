"""Bounded structural acquisition and strict executable-admission separation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph, RDF
from experiments.aat.acquisition import acquire, AA, SX, MAX_DEPTH, MAX_BYTES
from experiments.aat.rdf import load

DATA=Path('experiments/aat/data/acquisition')
CONFIG=json.loads((DATA/'room.config.json').read_text())


def document(version='3.1.0'):
    return {'openapi':version,'info':{'title':'Test','version':'1'},'paths':{'/x':{'post':{
        'operationId':'x','requestBody':{'content':{'application/json':{'schema':{'type':'integer'}}}},
        'responses':{'200':{'description':'ok','content':{'application/json':{'schema':{'type':'integer'}}}}}}}}}


class AcquisitionTests(unittest.TestCase):
    def run_doc(self,doc):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
        source=root/'input.json';source.write_text(json.dumps(doc))
        out=root/'out';return acquire(source,CONFIG,out),out

    def test_pinned_documents_quarantined_and_rejected_by_runtime(self):
        for case in ('room','petstore'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
                out=Path(d)/'out';r=acquire(DATA/(case+'.json'),json.loads((DATA/(case+'.config.json')).read_text()),out)
                self.assertEqual(r['status'],'QUARANTINED');self.assertFalse(r['executable'])
                g=Graph().parse(out/'structural.ttl',format='turtle')
                self.assertEqual(len(set(g.subjects(RDF.type,AA.Operation))),3)
                self.assertFalse(list(g.subjects(RDF.type,AA.Usage)))
                with self.assertRaises(ValueError):load(out/'structural.ttl',r['graph_sha256'])
                provenance=json.loads((out/'provenance.json').read_text())['assertions']
                self.assertEqual(len(g),len(provenance))
                for assertion in provenance:
                    self.assertEqual(hashlib.sha256(assertion['triple'].encode()).hexdigest(),assertion['assertion_id'])
                    for source in assertion['sources']:
                        self.assertEqual(source['document_sha256'],r['source_sha256'])
                        self.assertTrue(source['source']);self.assertTrue(source['rule']);self.assertTrue(source['transformation'])

    def test_invalid_versions_and_missing_ambiguous_bindings(self):
        controls=[]
        for version in ('2.0','3.2.0','3.1','not-openapi'):
            d=document(version);controls.append(d)
        controls+=[[],{},dict(document(),paths={})]
        d=document();d['paths']['/x']['post']['responses']={};controls.append(d)
        d=document();d['paths']['/y']=deepcopy(d['paths']['/x']);controls.append(d) # duplicate ID
        d=document();d['paths']['/{id}']=d['paths'].pop('/x');controls.append(d)
        d=document();d['paths']['/x']['post']['parameters']=[{'name':'x','in':'query'},{'name':'x','in':'query'}];controls.append(d)
        for i,d in enumerate(controls):
            with self.subTest(control=i):self.assertEqual(self.run_doc(d)[0]['status'],'INVALID')

    def test_remote_cyclic_and_missing_references_reject_without_network(self):
        for ref in ('https://example.invalid/schema.json','#/components/schemas/S','#/missing'):
            d=document();d['paths']['/x']['post']['requestBody']['content']['application/json']['schema']={'$ref':ref}
            d['components']={'schemas':{'S':{'$ref':'#/components/schemas/S'}}}
            self.assertEqual(self.run_doc(d)[0]['status'],'INVALID')
        d=document();d['components']={'schemas':{'S':{'type':'object','properties':{'child':{'$ref':'#/components/schemas/S'}}}}}
        d['paths']['/x']['post']['requestBody']['content']['application/json']['schema']={'$ref':'#/components/schemas/S'}
        self.assertEqual(self.run_doc(d)[0]['status'],'INVALID')

    def test_unsupported_composition_auth_serialization_and_behavior_not_flattened(self):
        d=document();op=d['paths']['/x']['post']
        op['requestBody']['content']['application/json']['schema']={'allOf':[{'type':'integer'}]}
        op['parameters']=[{'name':'q','in':'query','style':'deepObject','schema':{'type':'object'}}]
        d['components']={'securitySchemes':{'token':{'type':'oauth2','flows':{'clientCredentials':{'tokenUrl':'https://example.invalid/token','scopes':{}}}}}}
        op['security']=[{'token':[]}];op['x-aat-effects']={'delta':1,'reviewed':True}
        r,out=self.run_doc(d);self.assertEqual(r['status'],'QUARANTINED')
        codes={x['code'] for x in r['diagnostics']}
        self.assertTrue({'SCHEMA_KEYWORD','AUTH_SCHEME','AUTH_EXECUTION','PARAMETER_SERIALIZATION','OPERATION_FEATURE','BEHAVIOR_UNKNOWN'}<=codes)
        g=Graph().parse(out/'structural.ttl',format='turtle')
        self.assertFalse(list(g.triples((None,AA.delta,None))));self.assertFalse(list(g.triples((None,AA.reviewed,None))))
        request=g.value(None,SX.requestBody);media=g.value(request,SX.content);schema=g.value(media,SX.schema)
        self.assertIsNone(g.value(schema,SX.schemaType))

    def test_openapi_dialect_constraints_are_distinct(self):
        for version,exclusive,nullable in (('3.0.3',True,True),('3.1.0',1,True)):
            d=document(version);d['paths']['/x']['post']['requestBody']['content']['application/json']['schema']={'type':'integer','minimum':0,'exclusiveMinimum':exclusive,'nullable':nullable}
            r,out=self.run_doc(d);g=Graph().parse(out/'structural.ttl',format='turtle')
            self.assertTrue(list(g.triples((None,SX.exclusiveMinimum,None))))
            self.assertEqual(bool(list(g.triples((None,SX.nullable,None)))),version.startswith('3.0'))
        d=document('3.1.0');d['paths']['/x']['post']['requestBody']['content']['application/json']['schema']={'type':['integer','null']}
        r,_=self.run_doc(d);self.assertIn('SCHEMA_TYPE',{x['code'] for x in r['diagnostics']})

    def test_byte_and_depth_limits_duplicate_keys_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'input.json'
            for i,data in enumerate((b'{',b'{"openapi":"3.1.0","openapi":"3.0.0"}',b' '*(MAX_BYTES+1),('['*(MAX_DEPTH+2)+'0'+']'*(MAX_DEPTH+2)).encode())):
                p.write_bytes(data);self.assertEqual(acquire(p,CONFIG,root/str(i))['status'],'INVALID')
            with self.assertRaises(FileExistsError):acquire(p,CONFIG,root/'0')

    def test_local_pointer_escaping_and_parameter_inheritance(self):
        d=document();d['components']={'schemas':{'a/b~c':{'type':'string'}}}
        d['paths']['/x']['parameters']=[{'name':'q','in':'query','schema':{'$ref':'#/components/schemas/a~1b~0c'}}]
        r,out=self.run_doc(d);self.assertEqual(r['status'],'QUARANTINED')
        g=Graph().parse(out/'structural.ttl',format='turtle');self.assertTrue(list(g.triples((None,SX.schemaType,None))))

    def test_header_named_x_next_is_not_a_vendor_extension(self):
        d=document();d['paths']['/x']['post']['responses']['200']['headers']={'x-next':{'description':'Next link','schema':{'type':'string'}}}
        d['x-aat-effects']={'delta':1}
        r,_=self.run_doc(d)
        extensions=[x for x in r['diagnostics'] if x['code']=='VENDOR_EXTENSION']
        self.assertEqual([x['source'] for x in extensions],['#/x-aat-effects'])
        self.assertTrue(any(x['code']=='RESPONSE_HEADERS' for x in r['diagnostics']))

    def test_reference_metrics_detect_an_omitted_structural_assertion(self):
        from experiments.aat.acquisition_evaluation import reference_facts,graph_facts
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out';acquire(DATA/'petstore.json',CONFIG,out)
            g=Graph().parse(out/'structural.ttl',format='turtle')
            reference=reference_facts(json.loads((DATA/'petstore.reference.json').read_text()))
            self.assertEqual(graph_facts(g),reference)
            g.remove((None,SX.schemaType,None))
            self.assertTrue(reference-graph_facts(g))

    def test_determinism_and_document_key_reordering(self):
        d=document();r,a=self.run_doc(d);r2,b=self.run_doc(d)
        self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()},{p.name:p.read_bytes() for p in b.iterdir()})
        def reverse(value):
            if isinstance(value,dict):return {k:reverse(v) for k,v in reversed(list(value.items()))}
            if isinstance(value,list):return [reverse(x) for x in value]
            return value
        _,c=self.run_doc(reverse(d));self.assertEqual((a/'structural.ttl').read_bytes(),(c/'structural.ttl').read_bytes())
        self.assertNotEqual((a/'provenance.json').read_bytes(),(c/'provenance.json').read_bytes()) # exact source hash changes


if __name__=='__main__':unittest.main()
