"""Closed finite-usage/1 records, RDF validation and typed one-step interpretation."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from rdflib import Graph,Namespace,RDF,XSD,URIRef,Literal
from semantic_action.model import Truth

A=Namespace('urn:eswc:aat:prototype:1#');U=Namespace('urn:eswc:aat:usage:1#')
MIN,MAX=-(2**31),2**31-1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def read(data):
    if len(data)>1048576:raise ValueError('Input size')
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('Duplicate JSON key')
            d[k]=v
        return d
    v=json.loads(data,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    def check(x,n=0):
        if n>32:raise ValueError('JSON depth')
        if type(x) is float:raise ValueError('Float outside profile')
        if type(x) is int and not MIN<=x<=MAX:raise ValueError('Integer range')
        if isinstance(x,dict):
            for y in x.values():check(y,n+1)
        if isinstance(x,list):
            for y in x:check(y,n+1)
    check(v);return v

def pointer(p):
    if not isinstance(p,str) or not p.startswith('/') or re.search(r'~(?![01])',p) or len(p)>512:raise ValueError('Invalid pointer')
    return [x.replace('~1','/').replace('~0','~') for x in p[1:].split('/')]
def get(obj,p):
    try:
        for key in pointer(p):obj=obj[key]
        return obj
    except (KeyError,TypeError):return None

def put(obj,p,value):
    keys=pointer(p)
    for key in keys[:-1]:obj=obj[key]
    if keys[-1] not in obj:raise ValueError('Absent revision placeholder')
    obj[keys[-1]]=value

@dataclass(frozen=True)
class Slot:
    id:str; property:str; kind:str; pointer:str; unit:str|None=None; minimum:int|None=None; maximum:int|None=None
@dataclass(frozen=True)
class Condition:
    kind:str; slot:str; value:object; upper:int|None=None; unit:str|None=None
@dataclass(frozen=True)
class Effect:
    kind:str; slot:str; value:object; unit:str|None=None
@dataclass(frozen=True)
class Operation:
    id:str; method:str; path:str; body:str; request_revision:str; response_revision:str; status:int; echoes:tuple
@dataclass(frozen=True)
class Usage:
    id:str; operation:str; pre:tuple; effects:tuple; frame:tuple
@dataclass(frozen=True)
class Catalog:
    artifact:str; thing:str; slots:tuple; operations:tuple; usages:tuple; observation:str; identity:str; timestamp:str; revision:str; mutations:str; graph_hash:str
@dataclass(frozen=True)
class Goal:
    thing:str; clauses:tuple; max_age:float=10.0
@dataclass(frozen=True)
class Snapshot:
    id:str; thing:str|None; values:tuple; revision:int|None; mutations:int|None; observed_at:str|None; raw:str
@dataclass(frozen=True)
class Candidate:
    handle:str; operation:str; applicable:Truth; contributes:Truth; expected:tuple; reasons:tuple


def typed(slot,value):
    if slot.kind=='Int':return type(value) is int and slot.minimum<=value<=slot.maximum
    if slot.kind=='Bool':return type(value) is bool
    if slot.kind=='JSON':return value is not None # Canonical JSON string, including literal null.
    raise ValueError('Unknown slot type')

def all_truth(values):
    values=tuple(values)
    return Truth.FALSE if Truth.FALSE in values else Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.TRUE

def evaluate(conditions,values):
    result=[]
    for c in conditions:
        v=values.get(c.slot)
        if v is None:result.append(Truth.UNKNOWN)
        elif c.kind=='Equal':result.append(Truth.UNKNOWN if type(v) is not type(c.value) else Truth.TRUE if v==c.value else Truth.FALSE)
        elif c.kind=='IntRange':result.append(Truth.UNKNOWN if type(v) is not int else Truth.TRUE if c.value<=v<=c.upper else Truth.FALSE)
        else:raise ValueError('Unsupported condition')
    return all_truth(result)

def validate_goal(cat,goal):
    if goal.thing!=cat.thing or type(goal.max_age) not in (int,float) or not 0<goal.max_age<=30 or not goal.clauses or len(goal.clauses)>16:raise ValueError('Unsupported goal')
    slots={s.id:s for s in cat.slots}
    for c in goal.clauses:
        if c.kind!='Equal' or c.slot not in slots or slots[c.slot].kind=='JSON' or not typed(slots[c.slot],c.value) or c.unit!=slots[c.slot].unit:raise ValueError('Invalid goal clause')

def assess(cat,goal,ctx):
    slots={s.id:s for s in cat.slots};before=dict(ctx.values);out=[]
    for u in cat.usages:
        pre=evaluate(u.pre,before);pred=dict(before);reasons=[]
        for e in u.effects:
            v=before[e.slot]
            new=(v+e.value if type(v) is int else None) if e.kind=='AddInt' else e.value
            pred[e.slot]=new if typed(slots[e.slot],new) else None
        if any(v is None for v in before.values()):pre=Truth.UNKNOWN if pre!=Truth.FALSE else pre;reasons.append('Incomplete state/frame evidence')
        out.append(Candidate(u.id,u.operation,pre,evaluate(goal.clauses,pred),tuple(sorted(pred.items())),tuple(reasons)))
    return tuple(out)


def load(path,approved):
    if sha(path)!=approved:raise ValueError('Explicit graph hash approval required')
    data=Path(path).read_bytes()
    if len(data)>1048576:raise ValueError('RDF size')
    g=Graph().parse(data=data.decode(),format='turtle');seen=set()
    def values(s,p):
        vs=list(g.objects(s,p));seen.update((s,p,v) for v in vs);return vs
    def one(s,p,kind):
        vs=values(s,p)
        if len(vs)!=1:raise ValueError('Missing/ambiguous '+str(p))
        v=vs[0]
        if kind=='iri':
            if not isinstance(v,URIRef):raise ValueError('Named IRI required')
            return str(v)
        if not isinstance(v,Literal) or v.language or type(v.toPython()) is not kind:raise ValueError('Incorrect literal type')
        return v.toPython()
    def type_(s,c):
        if not isinstance(s,URIRef) or one(s,RDF.type,'iri')!=str(c):raise ValueError('Resource type')
    def linked(s,p,cls,maximum):
        vs=values(s,p)
        if not 1<=len(vs)<=maximum or any(not isinstance(x,URIRef) for x in vs):raise ValueError('Cardinality/named links')
        for x in vs:type_(x,cls)
        return sorted(vs,key=str)
    arts=list(g.subjects(RDF.type,A.Artifact))
    if len(arts)!=1:raise ValueError('One artifact per admission graph')
    a=arts[0];type_(a,A.Artifact);t=URIRef(one(a,A.represents,'iri'));type_(t,A.Thing)
    if one(a,U.profile,str)!='finite-usage/1' or one(a,A.reviewed,bool) is not True:raise ValueError('Unreviewed/profile')
    for p in (U.sourceHash,U.reviewHash):
        if not re.fullmatch('[0-9a-f]{64}',one(a,p,str)):raise ValueError('Provenance hash')
    observation=one(a,U.observationPath,str)
    def path_(p):
        if not p.startswith('/') or p.startswith('//') or any(x in p for x in ('?','#','..',':')) or len(p)>512:raise ValueError('Unsafe binding path')
        return p
    path_(observation)
    metadata=[one(a,p,str) for p in (U.identityPointer,U.timestampPointer,U.revisionPointer,U.mutationPointer)]
    for p in metadata:pointer(p)
    if len(set(metadata))!=4:raise ValueError('Metadata alias')
    slots=[]
    for s in linked(a,U.slot,U.Slot,32):
        if one(s,A.subject,'iri')!=str(t):raise ValueError('Slot grounding')
        kind=one(s,U.kind,str);prop=one(s,U.property,'iri');ptr=one(s,U.pointer,str);pointer(ptr)
        unit=lo=hi=None
        if kind=='Int':
            unit=one(s,U.unit,'iri');lo=one(s,U.minimum,int);hi=one(s,U.maximum,int)
            if not MIN<=lo<=hi<=MAX:raise ValueError('Bounds')
        elif kind not in ('Bool','JSON'):raise ValueError('Unsupported type')
        slots.append(Slot(str(s),prop,kind,ptr,unit,lo,hi))
    if len({s.property for s in slots})!=len(slots) or len({s.pointer for s in slots}|set(metadata))!=len(slots)+4:raise ValueError('Ambiguous schema')
    pointers=[s.pointer for s in slots]+metadata
    if any(p!=q and q.startswith(p+'/') for p in pointers for q in pointers):raise ValueError('Overlapping pointers')
    slotmap={s.id:s for s in slots};operations=[]
    for o in linked(a,A.hasOperation,A.Operation,8):
        method=one(o,A.method,str);path_value=path_(one(o,A.path,str))
        if method not in ('POST','PUT') or one(o,U.mediaType,str)!='application/json':raise ValueError('Unsupported HTTP binding')
        body=one(o,U.bodyTemplate,str);obj=read(body.encode());req=one(o,U.requestRevisionPointer,str);resp=one(o,U.replyRevisionPointer,str);pointer(req);pointer(resp)
        if not isinstance(obj,dict) or get(obj,req) is not None:raise ValueError('Revision placeholder')
        put(obj,req,0)
        status=one(o,U.successStatus,int)
        if status not in (200,201):raise ValueError('Unsupported success status')
        echoes=[]
        for node in values(o,U.echo):
            type_(node,U.Echo);p=one(node,U.pointer,str);pointer(p);s=one(node,U.onSlot,'iri')
            if s not in slotmap:raise ValueError('Unknown echo slot')
            echoes.append((p,s))
        if len({p for p,s in echoes})!=len(echoes):raise ValueError('Echo conflict')
        operations.append(Operation(str(o),method,path_value,body,req,resp,status,tuple(sorted(echoes))))
    usages=[]
    for u in linked(a,U.usage,A.Usage,8):
        if one(u,A.forArtifact,'iri')!=str(a):raise ValueError('Usage owner')
        op=one(u,A.forOperation,'iri')
        if op not in {o.id for o in operations}:raise ValueError('Usage binding')
        pre=URIRef(one(u,A.hasPrecond,'iri'));post=URIRef(one(u,A.hasPostcond,'iri'))
        for context in (pre,post):
            type_(context,A.ContextTemplate)
            if one(context,A.subject,'iri')!=str(t):raise ValueError('Context grounding')
        conditions=[]
        for c in values(pre,U.all):
            kind=one(c,RDF.type,'iri').removeprefix(str(U));slot=one(c,U.onSlot,'iri')
            if slot not in slotmap:raise ValueError('Unknown condition slot')
            s=slotmap[slot]
            if s.kind=='JSON':raise ValueError('JSON condition unsupported')
            unit=one(c,U.unit,'iri') if s.kind=='Int' else None
            if unit!=s.unit:raise ValueError('Unit mismatch')
            if kind=='Equal':conditions.append(Condition(kind,slot,one(c,U.value,int if s.kind=='Int' else bool),unit=unit))
            elif kind=='IntRange' and s.kind=='Int':
                lo=one(c,U['lower'],int);hi=one(c,U['upper'],int)
                if not s.minimum<=lo<=hi<=s.maximum:raise ValueError('Condition bounds')
                conditions.append(Condition(kind,slot,lo,hi,unit))
            else:raise ValueError('Unsupported predicate')
            if kind=='Equal' and not typed(s,conditions[-1].value):raise ValueError('Condition value')
        if not 1<=len(conditions)<=16:raise ValueError('Precondition cardinality')
        effects=[]
        for e in values(post,U.effect):
            kind=one(e,RDF.type,'iri').removeprefix(str(U));slot=one(e,U.onSlot,'iri')
            if slot not in slotmap:raise ValueError('Unknown effect slot')
            s=slotmap[slot]
            if kind=='AddInt' and s.kind=='Int':
                value=one(e,U.value,int);unit=one(e,U.unit,'iri')
                if value not in (-1,1) or unit!=s.unit:raise ValueError('Unsupported arithmetic')
            elif kind=='SetBool' and s.kind=='Bool':value=one(e,U.value,bool);unit=None
            else:raise ValueError('Unsupported effect')
            effects.append(Effect(kind,slot,value,unit))
        targets={e.slot for e in effects};frame=values(u,U.frameSlot)
        if not 1<=len(effects)<=4 or len(targets)!=len(effects) or any(not isinstance(f,URIRef) for f in frame):raise ValueError('Effects/frame shape')
        frame=set(map(str,frame))
        if targets & frame or targets|frame!=set(slotmap):raise ValueError('Incomplete/overlapping frame')
        usages.append(Usage(str(u),op,tuple(conditions),tuple(effects),tuple(sorted(frame))))
    if {u.operation for u in usages}!={o.id for o in operations} or set(g)!=seen:raise ValueError('Unsupported/disconnected assertions')
    return Catalog(str(a),str(t),tuple(slots),tuple(operations),tuple(usages),observation,*metadata,sha(path))
