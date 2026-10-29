"""Two-document structural evaluation. References never come from generated graphs."""
import argparse
import csv
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import subprocess
import time
from rdflib import Graph, RDF
from .acquisition import acquire, AA, SX, VERSION, canonical, digest
from .rdf import load

DATA=Path(__file__).parent/'data/acquisition'
CONSTRAINTS=('required','enum','minimum','maximum','exclusiveMinimum','exclusiveMaximum',
             'minLength','maxLength','minItems','maxItems','pattern','format','additionalProperties','nullable','readOnly','writeOnly')


def reference_facts(reference):
    result=[]
    def schema(value, prefix):
        if 'type' in value: result.append(prefix+['type',canonical(value['type'])])
        for k in CONSTRAINTS:
            if k in value: result.append(prefix+[k,canonical(value[k])])
        for name,child in sorted(value.get('properties',{}).items()):
            result.append(prefix+['property',name]);schema(child,prefix+[name])
        if 'items' in value:result.append(prefix+['items']);schema(value['items'],prefix+['[]'])
    for op in reference['operations']:
        base=[op['method'],op['path']]
        result.append(['operation']+base+[op['id']])
        for p in op['parameters']:
            prefix=['parameter']+base+[p['name'],p['in']]
            result.append(prefix+[p['required']]);schema(p['schema'],prefix+['schema'])
        request=op['request']
        if request is None:result.append(['no-request']+base)
        else:
            for media,value in request['media'].items():
                prefix=['request']+base+[media];result.append(prefix+[request['required']]);schema(value,prefix+['schema'])
        for code,content in op['responses'].items():
            if not content:result.append(['response']+base+[code,''])
            for media,value in content.items():
                prefix=['response']+base+[code,media];result.append(prefix);schema(value,prefix+['schema'])
    return set(map(canonical,result))


def graph_facts(graph):
    """Decode mapped RDF, not rawSchema/source JSON or extraction return objects."""
    result=[]
    def one(s,p):
        values=list(graph.objects(s,p))
        if len(values)!=1:raise ValueError('Ambiguous/missing evaluation field '+str(p))
        return values[0]
    def schema(node,prefix):
        for t in graph.objects(node,SX.schemaType):result.append(prefix+['type',canonical(str(t))])
        for k in CONSTRAINTS:
            for value in graph.objects(node,SX[k]):result.append(prefix+[k,canonical(json.loads(str(value)))])
        for p in graph.objects(node,SX.property):
            name=str(one(p,SX.name));result.append(prefix+['property',name]);schema(one(p,SX.schema),prefix+[name])
        for item in graph.objects(node,SX.items):result.append(prefix+['items']);schema(item,prefix+['[]'])
    for op in graph.subjects(RDF.type,AA.Operation):
        base=[str(one(op,AA.method)),str(one(op,AA.path))]
        result.append(['operation']+base+[str(one(op,SX.operationId))])
        for p in graph.objects(op,SX.parameter):
            prefix=['parameter']+base+[str(one(p,SX.name)),str(one(p,SX.location))]
            result.append(prefix+[one(p,SX.required).toPython()]);schema(one(p,SX.schema),prefix+['schema'])
        requests=list(graph.objects(op,SX.requestBody))
        if not requests:result.append(['no-request']+base)
        for body in requests:
            for media in graph.objects(body,SX.content):
                prefix=['request']+base+[str(one(media,SX.mediaType))]
                result.append(prefix+[one(body,SX.required).toPython()]);schema(one(media,SX.schema),prefix+['schema'])
        for response in graph.objects(op,SX.response):
            code=str(one(response,SX.statusCode));content=list(graph.objects(response,SX.content))
            if not content:result.append(['response']+base+[code,''])
            for media in content:
                prefix=['response']+base+[code,str(one(media,SX.mediaType))]
                result.append(prefix);schema(one(media,SX.schema),prefix+['schema'])
    return set(map(canonical,result))


def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def evaluate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    raw=output/'raw';raw.mkdir();shutil.copytree(DATA,raw/'inputs')
    for name,h in json.loads((DATA/'reference-lock.json').read_text())['sha256'].items():
        if digest((DATA/name).read_bytes())!=h:raise ValueError('Reference/input lock mismatch')
    paths=['experiments/aat/acquisition.py','experiments/aat/acquisition_evaluation.py','tests/aat/test_acquisition.py',
           'experiments/aat/model.py','experiments/aat/rdf.py','experiments/aat/runtime.py']
    save(raw/'environment.json',dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         working_tree=subprocess.check_output(['git','status','--porcelain'],text=True),python=platform.python_version(),
         dependencies={n:version(n) for n in ('rdflib','pyparsing')},extractor_version=VERSION,
         source_hashes={p:digest(Path(p).read_bytes()) for p in paths},human_active_minutes=None,supervision_minutes=None))
    rows=[];start=time.monotonic()
    for case in ('room','petstore'):
        t=time.monotonic();source=DATA/(case+'.json');config=json.loads((DATA/(case+'.config.json')).read_text())
        first=raw/case/'first';second=raw/case/'repeat'
        report=acquire(source,config,first);again=acquire(source,config,second)
        if report['status']!='QUARANTINED' or again!=report:raise ValueError('Extraction failure or nondeterminism')
        identical={p.name:digest(p.read_bytes()) for p in first.iterdir()}=={p.name:digest(p.read_bytes()) for p in second.iterdir()}
        g=Graph().parse(first/'structural.ttl',format='turtle');expected=reference_facts(json.loads((DATA/(case+'.reference.json')).read_text()));actual=graph_facts(g)
        save(raw/case/'comparison.json',dict(expected=sorted(expected),actual=sorted(actual),missing=sorted(expected-actual),unexpected=sorted(actual-expected)))
        entries=json.loads((first/'provenance.json').read_text())['assertions']
        triples={' '.join(term.n3() for term in triple)+' .' for triple in g}
        complete=triples=={e['triple'] for e in entries} and all(e['assertion_id']==digest(e['triple'].encode()) and e['sources'] and all(
            s['document_sha256']==report['source_sha256'] and all(s.get(k) for k in ('source','rule','evidence_class','extractor_version','transformation')) for s in e['sources']) for e in entries)
        try:load(first/'structural.ttl',report['graph_sha256']);rejected=False;reason=None
        except ValueError as error:rejected=True;reason=str(error)
        save(raw/case/'runtime-admission.json',dict(rejected=rejected,reason=reason,matching_test_hash=True,review_approval=False))
        matched=len(actual&expected)
        rows.append(dict(case=case,reference_facts=len(expected),extracted_facts=len(actual),matched=matched,missing=len(expected-actual),unexpected=len(actual-expected),
          precision=matched/len(actual),recall=matched/len(expected),assertions=len(g),provenance_complete=complete,deterministic=identical,
          executable_admission_rejected=rejected,diagnostics=len(report['diagnostics']),
          unsupported=sum(d['status']=='UNSUPPORTED' for d in report['diagnostics']),unknown=sum(d['status']=='UNKNOWN' for d in report['diagnostics']),
          operations=len(set(g.subjects(RDF.type,AA.Operation))),usages=len(set(g.subjects(RDF.type,AA.Usage))),elapsed_seconds=time.monotonic()-t))
    stable={p:digest(Path(p).read_bytes()) for p in paths}==json.loads((raw/'environment.json').read_text())['source_hashes']
    save(raw/'measurements.json',dict(cases=rows,elapsed_seconds=time.monotonic()-start,source_stable=stable))
    save(raw/'sha256.json',{str(p.relative_to(raw)):digest(p.read_bytes()) for p in sorted(raw.rglob('*')) if p.is_file()})
    return summarize(output)


def summarize(output):
    raw=output/'raw'
    for path,h in json.loads((raw/'sha256.json').read_text()).items():
        if digest((raw/path).read_bytes())!=h:raise ValueError('Raw hash mismatch '+path)
    measurements=json.loads((raw/'measurements.json').read_text());rows=measurements['cases']
    derived=output/'derived';derived.mkdir(exist_ok=True);save(derived/'results.json',rows)
    with (derived/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    cols=('case','operations','reference_facts','precision','recall','assertions','unsupported','unknown','deterministic','executable_admission_rejected')
    (derived/'table.md').write_text('| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(str(r[c]) for c in cols)+' |' for r in rows)+'\n')
    passed=measurements['source_stable'] and all(r['precision']==r['recall']==1 and r['provenance_complete'] and r['deterministic'] and r['executable_admission_rejected'] and r['usages']==0 for r in rows)
    save(derived/'summary.json',dict(passed=passed,document_cases=2,independently_developed_documentation_cases=1,
                                   independent_reference_authors=0,external_execution_evaluated=False,behavioral_inference=False))
    print(json.dumps(rows,indent=2));return 0 if passed else 1


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('run','summarize'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    return evaluate(a.output) if a.command=='run' else summarize(a.output)


if __name__=='__main__':raise SystemExit(main())
