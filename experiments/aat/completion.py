"""Bounded room-step/1 completion; structural RDF is an input, never a manual graph copy."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from rdflib import Graph, RDF, Literal, URIRef
from .acquisition import acquire, AA, SX, canonical, digest, read_json
from .rdf import load

VERSION='room-completion/1'
FIELDS={'temperature':str(AA.temperatureC),'heater_ready':str(AA.heaterReady),'cooler_ready':str(AA.coolerReady),
        'revision':str(AA.revision),'mutations':str(AA.mutationCount),'sentinels':str(AA.sentinels),
        'thing':str(AA.subject),'observed_at':str(AA.observedAt)}
REQUEST={'type':'object','required':['expected_revision'],'properties':{'expected_revision':{'type':'integer'}},'additionalProperties':False}
REPLY={'type':'object','required':['revision','temperature'],'properties':{'revision':{'type':'integer'},'temperature':{'type':'integer'}}}
STATE={'type':'object','required':['temperature','heater_ready','cooler_ready','revision','mutations','requests','sentinels','pending_requests','thing','observed_at'],
       'properties':{**{k:{'type':'integer'} for k in ('temperature','revision','mutations','requests','pending_requests')},
                     **{k:{'type':'boolean'} for k in ('heater_ready','cooler_ready')},
                     'sentinels':{'type':'object','additionalProperties':True},'thing':{'type':'string'},'observed_at':{'type':'string'}}}


def sha(path):return digest(Path(path).read_bytes())
def save(path,value):Path(path).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
def exact(value,keys):
    if not isinstance(value,dict) or set(value)!=set(keys.split()):raise ValueError('Missing/unsupported completion fields: '+keys)


def one(g,s,p):
    values=list(g.objects(s,p))
    if len(values)!=1:raise ValueError('Missing/ambiguous structural field '+str(p))
    return values[0]


def schema(g,node):
    """Decode only mapped structural assertions, not rawSchema JSON as an answer key."""
    result={}
    if list(g.objects(node,SX.schemaType)):result['type']=str(one(g,node,SX.schemaType))
    for key in ('required','additionalProperties'):
        if list(g.objects(node,SX[key])):result[key]=json.loads(str(one(g,node,SX[key])))
    props={}
    for p in g.objects(node,SX.property):
        name=str(one(g,p,SX.name))
        if name in props:raise ValueError('Duplicate structural property')
        props[name]=schema(g,one(g,p,SX.schema))
    if props:result['properties']=props
    # Require no hidden constraints or unsupported schema assertions.
    allowed={RDF.type,SX.rawSchema,SX.referenceTarget,SX.schemaType,SX.required,SX.additionalProperties,SX.property}
    if any(p not in allowed for p in g.predicates(node)):raise ValueError('Unsupported wire constraint')
    return result


def content_schema(g,parent):
    media=list(g.objects(parent,SX.content))
    if len(media)!=1 or str(one(g,media[0],SX.mediaType))!='application/json':raise ValueError('Exactly JSON media required')
    return schema(g,one(g,media[0],SX.schema)),str(one(g,media[0],SX.mediaType))


def complete(bundle,sidecar,output):
    bundle,output=Path(bundle),Path(output);output.mkdir(parents=True,exist_ok=False)
    shutil.copytree(bundle,output/'structural');shutil.copyfile(sidecar,output/'sidecar.json')
    bundle=output/'structural'
    inputs={n:sha(output/'structural'/n) for n in ('source.json','config.json','structural.ttl','provenance.json','diagnostics.json')}
    inputs['sidecar.json']=sha(output/'sidecar.json')
    mapping=[]
    try:
        sc=read_json((output/'sidecar.json').read_bytes())
        exact(sc,'version source_sha256 structural_sha256 provenance_sha256 native_source_sha256 artifact thing review observation usages')
        if sc['version']!=VERSION:raise ValueError('Unsupported completion version')
        exact(sc['review'],'status reviewer scope reference')
        if sc['review']['status']!='reviewed' or not all(isinstance(sc['review'][k],str) and sc['review'][k] for k in ('reviewer','scope','reference')):raise ValueError('Unreviewed/unknown behavior')
        for field,name in (('source_sha256','source.json'),('structural_sha256','structural.ttl'),('provenance_sha256','provenance.json')):
            if sc[field]!=inputs[name]:raise ValueError('Sidecar/source hash mismatch')
        if not isinstance(sc['native_source_sha256'],str) or len(sc['native_source_sha256'])!=64:raise ValueError('Missing native review hash')
        config=read_json((bundle/'config.json').read_bytes())
        # Verify every structural/provenance assertion by deterministic re-extraction, not trust in supplied hashes alone.
        with tempfile.TemporaryDirectory() as d:
            report=acquire(bundle/'source.json',config,Path(d)/'reextract')
            if report['status']!='QUARANTINED':raise ValueError('Invalid structural input')
            for name in ('structural.ttl','provenance.json','diagnostics.json'):
                if (Path(d)/'reextract'/name).read_bytes()!=(bundle/name).read_bytes():raise ValueError('Structural/provenance reconciliation mismatch')
        diagnostics=json.loads((bundle/'diagnostics.json').read_text())
        if any(d['code']!='BEHAVIOR_UNKNOWN' for d in diagnostics['diagnostics']):raise ValueError('Unsupported/unknown structural feature')
        g=Graph().parse(bundle/'structural.ttl',format='turtle');out=Graph()
        things=list(g.subjects(RDF.type,AA.Thing));artifacts=list(g.subjects(RDF.type,AA.Artifact))
        if len(things)!=1 or len(artifacts)!=1:raise ValueError('Ambiguous grounding')
        t,a=things[0],artifacts[0]
        if (str(t),str(a))!=(sc['thing'],sc['artifact']) or one(g,a,AA.represents)!=t:raise ValueError('Sidecar grounding conflict')
        def extracted(s,p,o):
            if (s,p,o) not in g:raise ValueError('Binding not extracted')
            out.add((s,p,o));mapping.append(dict(from_triple=' '.join(x.n3() for x in (s,p,o)),to_triple=' '.join(x.n3() for x in (s,p,o)),kind='copied-structural'))
        for triple in ((t,RDF.type,AA.Thing),(a,RDF.type,AA.Artifact),(a,AA.represents,t)):extracted(*triple)
        obs=sc['observation'];exact(obs,'operation fields')
        if obs['fields']!=FIELDS:raise ValueError('Unsupported observation mapping')
        ops=set(g.objects(a,AA.hasOperation))
        if len(ops)!=3 or ops!=set(g.subjects(RDF.type,AA.Operation)):raise ValueError('Unsupported operation set')
        observe=URIRef(obs['operation'])
        if observe not in ops or str(one(g,observe,AA.method))!='GET' or str(one(g,observe,AA.path))!='/state' or one(g,observe,SX.observationCandidate).toPython() is not True:raise ValueError('Unsupported observer binding')
        response=next((r for r in g.objects(observe,SX.response) if str(one(g,r,SX.statusCode))=='200'),None)
        if response is None or content_schema(g,response)[0]!=STATE:raise ValueError('Unsupported observation schema')
        observation_path=one(g,observe,AA.path);out.add((a,AA.observationPath,observation_path))
        mapping.append(dict(from_operation=str(observe),from_predicate=str(AA.path),to_predicate=str(AA.observationPath),value=str(observation_path),kind='reviewed-observer-projection'))
        if not isinstance(sc['usages'],list) or len(sc['usages'])!=2:raise ValueError('Incomplete behavioral Usages')
        used=set()
        for u in sc['usages']:
            exact(u,'id operation request_schema response_schema pre post frame')
            op=URIRef(u['operation']);uid=URIRef(u['id'])
            if op not in ops-{observe} or op in used or not u['id'].startswith('urn:'):raise ValueError('Conflicting Usage operation/identity')
            used.add(op)
            if list(g.objects(op,SX.parameter)) or json.loads(str(one(g,op,SX.securityRequirements)))!=[]:raise ValueError('Unsupported parameters/security')
            if list(g.objects(observe,SX.parameter)) or json.loads(str(one(g,observe,SX.securityRequirements)))!=[]:raise ValueError('Unsupported observer parameters/security')
            bodies=list(g.objects(op,SX.requestBody))
            if len(bodies)!=1 or one(g,bodies[0],SX.required).toPython() is not True:raise ValueError('Required request body missing')
            req,media=content_schema(g,bodies[0]);response=next((r for r in g.objects(op,SX.response) if str(one(g,r,SX.statusCode))=='201'),None)
            if req!=REQUEST or response is None or content_schema(g,response)[0]!=REPLY:raise ValueError('Unsupported operation wire schema')
            if u['request_schema']!=str(AA.RevisionRequest) or u['response_schema']!=str(AA.RoomReply):raise ValueError('Unsupported profile schema identity')
            for triple in ((a,AA.hasOperation,op),(op,RDF.type,AA.Operation),(op,AA.method,one(g,op,AA.method)),(op,AA.path,one(g,op,AA.path))):extracted(*triple)
            for p,value in ((AA.requestSchema,URIRef(u['request_schema'])),(AA.responseSchema,URIRef(u['response_schema'])),(AA.mediaType,Literal(media))):out.add((op,p,value))
            mapping.append(dict(operation=str(op),request_schema=u['request_schema'],response_schema=u['response_schema'],media=media,kind='validated-wire-profile-interpretation'))
            pre,post=URIRef(u['id']+':pre'),URIRef(u['id']+':post')
            for p,value in ((RDF.type,AA.Usage),(AA.profile,Literal('room-step/1')),(AA.reviewed,Literal(True)),(AA.reviewRef,Literal(sc['review']['reference'])),(AA.forArtifact,a),(AA.forOperation,op),(AA.hasPrecond,pre),(AA.hasPostcond,post)):out.add((uid,p,value))
            exact(u['pre'],'subject ready_property minimum maximum current_revision')
            exact(u['post'],'subject property rule delta revision_increment mutation_increment')
            for node,body in ((pre,u['pre']),(post,u['post'])):
                out.add((node,RDF.type,AA.ContextTemplate));out.add((node,AA.subject,URIRef(body['subject'])))
            for key,p in (('ready_property',AA.readyProperty),('minimum',AA.minimum),('maximum',AA.maximum),('current_revision',AA.requiresCurrentRevision)):
                out.add((pre,p,URIRef(u['pre'][key]) if key=='ready_property' else Literal(u['pre'][key])))
            for key,p in (('property',AA.property),('rule',AA.rule),('delta',AA.delta),('revision_increment',AA.revisionIncrement),('mutation_increment',AA.mutationIncrement)):
                out.add((post,p,URIRef(u['post'][key]) if key in ('property','rule') else Literal(u['post'][key])))
            if not isinstance(u['frame'],list) or len(u['frame'])!=len(set(u['frame'])):raise ValueError('Malformed frame')
            for value in u['frame']:out.add((uid,AA.preserves,URIRef(value)))
        candidate=output/'candidate.ttl';candidate.write_text('\n'.join(sorted(' '.join(v.n3() for v in triple)+' .' for triple in out))+'\n')
        # Structural/profile validation using actual hash is NOT an approval or execution admission.
        load(candidate,sha(candidate))
        result=dict(status='COMPLETED_UNAPPROVED',version=VERSION,graph_sha256=sha(candidate),inputs=inputs,
                    origin=config['origin'],native_source_sha256=sc['native_source_sha256'],review=sc['review'],mapping=mapping)
    except (ValueError,TypeError,KeyError,AttributeError) as error:
        result=dict(status='QUARANTINED',version=VERSION,inputs=inputs,error=str(error))
    save(output/'completion.json',result);return result


def admit(completed,approval):
    completed=Path(completed);record=json.loads((completed/'completion.json').read_text());decision=read_json(Path(approval).read_bytes())
    exact(decision,'approved reviewer scope graph_sha256 completion_sha256')
    if record['status']!='COMPLETED_UNAPPROVED' or decision['approved'] is not True or not all(isinstance(decision[k],str) and decision[k] for k in ('reviewer','scope')):raise ValueError('Explicit graph approval required')
    if decision['completion_sha256']!=sha(completed/'completion.json') or decision['graph_sha256']!=record['graph_sha256'] or sha(completed/'candidate.ttl')!=record['graph_sha256']:raise ValueError('Approval graph/review hash mismatch')
    for name,h in record['inputs'].items():
        p=completed/name if name=='sidecar.json' else completed/'structural'/name
        if sha(p)!=h:raise ValueError('Completed input changed')
    catalog=load(completed/'candidate.ttl',decision['graph_sha256'])
    return catalog,dict(admitted=True,graph_sha256=catalog.graph_hash,approval_sha256=sha(approval),completion_sha256=sha(completed/'completion.json'),origin=record['origin'])


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('complete');c.add_argument('--bundle',type=Path,required=True);c.add_argument('--sidecar',type=Path,required=True);c.add_argument('--output',type=Path,required=True)
    a=sub.add_parser('admit');a.add_argument('--completed',type=Path,required=True);a.add_argument('--approval',type=Path,required=True)
    args=p.parse_args()
    if args.command=='complete':
        result=complete(args.bundle,args.sidecar,args.output);print(json.dumps(result,indent=2));return 0 if result['status']=='COMPLETED_UNAPPROVED' else 2
    _,record=admit(args.completed,args.approval);print(json.dumps(record,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
