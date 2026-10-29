"""Closed RDF profile loader and admission. No external ontology imports/reasoner."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from .model import Thing, Artifact, Operation, Usage, NS, ROOM

AA=Namespace(NS)

@dataclass(frozen=True)
class Catalog:
    thing: Thing
    artifact: Artifact
    operations: tuple[Operation,...]
    usages: tuple[Usage,...]
    graph_hash: str


def load(path, approved_hash):
    data=Path(path).read_bytes();g=Graph().parse(data=data.decode(),format='turtle');seen=set()
    def one(s,p,kind):
        values=list(g.objects(s,p))
        if len(values)!=1:raise ValueError('Missing/ambiguous '+str(p))
        v=values[0];seen.add((s,p,v))
        if kind=='uri':
            if not isinstance(v,URIRef):raise ValueError('Named resource required')
            return str(v)
        if not isinstance(v,Literal) or v.language:raise ValueError('Typed literal required')
        result=v.toPython()
        if type(result) is not kind:raise ValueError('Incorrect literal type')
        return result
    def typed(s,cls):
        if not isinstance(s,URIRef) or one(s,RDF.type,'uri')!=str(cls):raise ValueError('Unsupported resource type')
    def instances(cls):return sorted(set(g.subjects(RDF.type,cls)),key=str)
    ts,ars=instances(AA.Thing),instances(AA.Artifact)
    if len(ts)!=1 or len(ars)!=1:raise ValueError('One grounded room thing/artifact required')
    t,a=ts[0],ars[0];typed(t,AA.Thing);typed(a,AA.Artifact)
    if str(t)!=ROOM or one(a,AA.represents,'uri')!=str(t):raise ValueError('Inconsistent thing grounding')
    if one(a,AA.observationPath,str)!='/state':raise ValueError('Unsupported observation binding')
    linked=list(g.objects(a,AA.hasOperation));seen.update((a,AA.hasOperation,o) for o in linked)
    if len(linked)!=2 or set(linked)!=set(instances(AA.Operation)):raise ValueError('Two operations required')
    operations=[]
    for o in sorted(linked,key=str):
        typed(o,AA.Operation);method=one(o,AA.method,str);path_value=one(o,AA.path,str)
        if method!='POST' or path_value not in {'/heat','/cool'}:raise ValueError('Unsupported binding')
        request_schema=one(o,AA.requestSchema,'uri');response_schema=one(o,AA.responseSchema,'uri');media=one(o,AA.mediaType,str)
        if (request_schema,response_schema,media)!=(str(AA.RevisionRequest),str(AA.RoomReply),'application/json'):raise ValueError('Unsupported wire schema/media')
        operations.append(Operation(str(o),str(a),method,path_value,request_schema,response_schema,media))
    if {o.path for o in operations}!={'/heat','/cool'}:raise ValueError('Ambiguous operation binding')
    usages=[]
    for u in instances(AA.Usage):
        typed(u,AA.Usage)
        if one(u,AA.reviewed,bool) is not True:raise ValueError('Unreviewed Usage')
        if one(u,AA.profile,str)!='room-step/1':raise ValueError('Unsupported profile')
        if one(u,AA.forArtifact,'uri')!=str(a):raise ValueError('Wrong artifact scope')
        operation=one(u,AA.forOperation,'uri')
        if operation not in {o.id for o in operations}:raise ValueError('Unknown operation')
        pre=URIRef(one(u,AA.hasPrecond,'uri'));post=URIRef(one(u,AA.hasPostcond,'uri'))
        typed(pre,AA.ContextTemplate);typed(post,AA.ContextTemplate)
        if one(pre,AA.subject,'uri')!=str(t) or one(post,AA.subject,'uri')!=str(t):raise ValueError('Ungrounded Usage contexts')
        if one(pre,AA.requiresCurrentRevision,bool) is not True:raise ValueError('Current revision guard required')
        ready=one(pre,AA.readyProperty,'uri');lo=one(pre,AA.minimum,int);hi=one(pre,AA.maximum,int)
        if ready not in {str(AA.heaterReady),str(AA.coolerReady)} or not 18<=lo<=hi<=26:raise ValueError('Unsupported precondition')
        if one(post,AA.property,'uri')!=str(AA.temperatureC) or one(post,AA.rule,'uri')!=str(AA.addInteger):raise ValueError('Unsupported effect rule')
        delta=one(post,AA.delta,int)
        if delta not in (-1,1) or one(post,AA.revisionIncrement,int)!=1 or one(post,AA.mutationIncrement,int)!=1:raise ValueError('Unsupported transition')
        frame=list(g.objects(u,AA.preserves));seen.update((u,AA.preserves,f) for f in frame)
        if set(frame)!={AA.heaterReady,AA.coolerReady,AA.sentinels}:raise ValueError('Incomplete frame')
        usages.append(Usage(str(u),str(a),operation,str(pre),str(post),ready,lo,hi,delta,
                            tuple(sorted(map(str,frame))),one(u,AA.reviewRef,str)))
    if len(usages)!=2 or len({u.operation for u in usages})!=2:raise ValueError('Two distinct reviewed usages required')
    if set(g)!=seen:raise ValueError('Unsupported or disconnected RDF assertions')
    h=hashlib.sha256(data).hexdigest()
    if h!=approved_hash:raise ValueError('Graph not admitted by external reviewed hash')
    return Catalog(Thing(str(t)),Artifact(str(a),str(t),tuple(o.id for o in operations),'/state'),tuple(operations),tuple(usages),h)
