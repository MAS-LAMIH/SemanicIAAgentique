"""Domain-neutral observe/reason/guard/act/verify loop for finite-usage/1."""
from dataclasses import asdict,dataclass
import json
from pathlib import Path
import time
from typing import Protocol
from uuid import uuid4
from semantic_action.model import Truth,now
from semantic_action.oracle import current
from semantic_action.transport import HTTPTransport
from .profile import Snapshot,Goal,Candidate,assess,evaluate,typed,get,put,canonical,read,validate_goal


def save(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def fresh(ctx,goal,cat):
    return bool(ctx and ctx.thing==cat.thing and type(ctx.revision) is int and type(ctx.mutations) is int and 0<=ctx.revision<=2**31-1 and 0<=ctx.mutations<=2**31-1 and current({'observed_at':ctx.observed_at},goal.max_age))
def fingerprint(ctx):return ctx.thing,ctx.revision,ctx.mutations,ctx.values
@dataclass(frozen=True)
class Proposal:
    tool:str;handle:str|None=None;snapshot_ref:str|None=None
@dataclass(frozen=True)
class Feedback:
    code:str;reasons:tuple;context:Snapshot|None
@dataclass(frozen=True)
class View:
    goal:Goal;discovered:bool;context:Snapshot|None;descriptions:tuple;candidates:tuple;goal_truth:Truth;feedback:tuple
@dataclass(frozen=True)
class Permit:
    nonce:str;usage:str;operation:str;revision:int;graph_hash:str;goal_hash:str;expires_at:str
class Reasoner(Protocol):
    def propose(self,view:View)->Proposal:...
class ScriptedReasoner:
    def propose(self,v):
        if not v.discovered:return Proposal('discover')
        if v.context is None:return Proposal('observe')
        if v.goal_truth==Truth.TRUE:return Proposal('finish')
        eligible=[c for c in v.candidates if c.applicable==c.contributes==Truth.TRUE]
        if eligible:return Proposal('use',min(eligible,key=lambda c:c.handle).handle,v.context.id)
        return Proposal('stop_unknown' if v.goal_truth==Truth.UNKNOWN or any(c.applicable==Truth.UNKNOWN for c in v.candidates) else 'stop_no_match')
class IrrelevantFirst:
    """Symmetric diagnostic reasoner fault, based only on actual assessments."""
    def __init__(self):self.used=False;self.default=ScriptedReasoner()
    def propose(self,v):
        wrong=[c for c in v.candidates if c.applicable==Truth.TRUE and c.contributes==Truth.FALSE]
        if v.context and wrong and not self.used:
            self.used=True;return Proposal('use',min(wrong,key=lambda c:c.handle).handle,v.context.id)
        return self.default.propose(v)

class Runtime:
    def __init__(self,catalog,origin,goal,output,knowledge=None):
        validate_goal(catalog,goal);self.cat,self.goal,self.out=catalog,goal,Path(output);self.out.mkdir(parents=True,exist_ok=True)
        self.transport=HTTPTransport(origin);self.knowledge=knowledge or assess;self.http=[];self.observations=[];self.permits={};self.dispatches=0
    def request(self,method,path,body=None):
        t=time.monotonic();r=self.transport._http_request(method,path,body)
        self.http.append(dict(method=method,path=path,body=body,result=asdict(r),elapsed=time.monotonic()-t,at=now()));save(self.out/'http.json',self.http);return r
    def observe(self):
        r=self.request('GET',self.cat.observation);b=r.body if r.success else {};values=[]
        try:read(canonical(b).encode())
        except (ValueError,TypeError):b={}
        for s in self.cat.slots:
            v=get(b,s.pointer)
            if s.kind=='JSON':
                obj=b;exists=True
                from .profile import pointer
                for key in pointer(s.pointer):
                    if not isinstance(obj,dict) or key not in obj:exists=False;break
                    obj=obj[key]
                v=canonical(obj) if exists else None
            elif not typed(s,v):v=None
            values.append((s.id,v))
        integer=lambda p:get(b,p) if type(get(b,p)) is int else None
        ctx=Snapshot('urn:context:'+str(uuid4()),get(b,self.cat.identity),tuple(sorted(values)),integer(self.cat.revision),integer(self.cat.mutations),get(b,self.cat.timestamp),canonical(b))
        self.observations.append(ctx);save(self.out/'observations.json',[asdict(x) for x in self.observations]);return ctx
    def candidates(self,ctx):
        if ctx is None:return ()
        result=self.knowledge(self.cat,self.goal,ctx)
        if not fresh(ctx,self.goal,self.cat):result=tuple(Candidate(c.handle,c.operation,Truth.UNKNOWN,Truth.UNKNOWN,c.expected,('Invalid/stale evidence',)) for c in result)
        return result
    def goal_truth(self,ctx):return evaluate(self.goal.clauses,dict(ctx.values)) if fresh(ctx,self.goal,self.cat) else Truth.UNKNOWN
    def authorize(self,p,old):
        if p.tool!='use' or old is None or p.snapshot_ref!=old.id:return None,dict(code='INVALID_PROPOSAL')
        ctx=self.observe()
        if not fresh(old,self.goal,self.cat) or not fresh(ctx,self.goal,self.cat):return None,dict(code='UNKNOWN_CONTEXT',context=asdict(ctx))
        if fingerprint(old)!=fingerprint(ctx):return None,dict(code='STALE_PROPOSAL',context=asdict(ctx))
        cs=self.candidates(ctx);chosen=next((c for c in cs if c.handle==p.handle),None)
        eligible=[c for c in cs if c.applicable==c.contributes==Truth.TRUE]
        bindings={}
        for c in eligible:
            o=next(o for o in self.cat.operations if o.id==c.operation)
            key=(o.method,o.path,o.body,o.request_revision)
            bindings.setdefault(key,set()).add(c.expected)
        if len(bindings)>1 or any(len(v)>1 for v in bindings.values()):return None,dict(code='AMBIGUOUS',context=asdict(ctx))
        if ctx.revision==2**31-1 or ctx.mutations==2**31-1 or chosen not in eligible or any(v is None for _,v in ctx.values):return None,dict(code='NOT_AUTHORIZED',context=asdict(ctx))
        from hashlib import sha256
        from datetime import datetime,timedelta
        expiry=(datetime.fromisoformat(ctx.observed_at)+timedelta(seconds=self.goal.max_age)).isoformat()
        permit=Permit(str(uuid4()),chosen.handle,chosen.operation,ctx.revision,self.cat.graph_hash,sha256(canonical(asdict(self.goal)).encode()).hexdigest(),expiry)
        self.permits[permit.nonce]=(permit,ctx,chosen);return permit,dict(code='AUTHORIZED',context=asdict(ctx),assessment=asdict(chosen))
    def execute(self,p):
        entry=self.permits.pop(p.nonce,None)
        if not entry or entry[0]!=p or p.graph_hash!=self.cat.graph_hash or self.dispatches:raise ValueError('Invalid/reused permit')
        _,before,c=entry
        from hashlib import sha256
        if p.goal_hash!=sha256(canonical(asdict(self.goal)).encode()).hexdigest():raise ValueError('Goal changed after authorization')
        if not fresh(before,self.goal,self.cat):return dict(status='UNKNOWN_CONTEXT',verified=False)
        op=next(o for o in self.cat.operations if o.id==p.operation);body=read(op.body.encode());put(body,op.request_revision,p.revision)
        self.dispatches+=1;started=now();r=self.request(op.method,op.path,body);after=self.observe()
        evidence=fresh(after,self.goal,self.cat) and current({'observed_at':after.observed_at},self.goal.max_age,started) and all(v is not None for _,v in after.values)
        actual=dict(after.values);expected=dict(c.expected)
        checks=dict(evidence=bool(evidence),expected_state=bool(evidence and actual==expected),revision=bool(evidence and after.revision==before.revision+1),
          mutations=bool(evidence and after.mutations==before.mutations+1),goal=self.goal_truth(after)==Truth.TRUE,
          response_revision=type(get(r.body,op.response_revision)) is int and get(r.body,op.response_revision)==after.revision,
          echoes=all(type(get(r.body,ptr)) is type(actual[slot]) and get(r.body,ptr)==actual[slot] for ptr,slot in op.echoes))
        verified=r.status==op.status and all(checks.values())
        status='UNCERTAIN_MUTATION' if r.status is None else 'SUCCESS' if verified else 'CONFLICT' if r.status==409 and evidence and fingerprint(before)==fingerprint(after) else 'POSTCONDITION_FAILED'
        # A CAS rejection may follow an authorized external revision change; mutation count still proves no actor write here.
        if r.status==409 and evidence and after.mutations==before.mutations:status='CONFLICT'
        return dict(status=status,verified=verified,checks=checks,before=asdict(before),after=asdict(after),invocation=asdict(r))
    def barrier(self,turn,stage,p):
        save(self.out/f'{stage}-{turn}.json',asdict(p));deadline=time.monotonic()+10
        while not (self.out/f'release-{stage}-{turn}').exists():
            if time.monotonic()>deadline:raise TimeoutError('Barrier unavailable')
            time.sleep(.003)
    def run(self,reasoner=None):
        reasoner=reasoner or ScriptedReasoner();ctx=None;discovered=False;feedback=[];trace=[];invocation=None;verified=False;status='BUDGET_EXHAUSTED'
        for turn in range(1,7):
            view=View(self.goal,discovered,ctx,self.cat.usages if discovered else (),self.candidates(ctx) if discovered else (),self.goal_truth(ctx),tuple(feedback))
            p=reasoner.propose(view)
            if not isinstance(p,Proposal):p=Proposal('invalid')
            event=dict(turn=turn,view=asdict(view),proposal=asdict(p));trace.append(event);save(self.out/'transcript.json',trace)
            if p.tool=='discover':discovered=True;f=dict(code='DISCOVERED')
            elif p.tool=='observe':ctx=self.observe();f=dict(code='OBSERVED',context=asdict(ctx))
            elif p.tool=='use':
                self.barrier(turn,'intent',p);permit,f=self.authorize(p,ctx);event['guard']=f
                if permit is None:
                    ctx=None
                    if f['code']=='AMBIGUOUS':status='AMBIGUOUS';event['feedback']=f;break
                else:
                    self.barrier(turn,'authorized',p);invocation=self.execute(permit);f=invocation;status=f['status']
                    if not f['verified']:event['feedback']=f;break
                    ctx=self.observations[-1];status='BUDGET_EXHAUSTED'
            elif p.tool=='finish':
                latest=self.observe();verified=bool(self.goal_truth(latest)==Truth.TRUE and ctx is not None and fingerprint(latest)==fingerprint(ctx) and (self.dispatches==0 or invocation and invocation['verified']))
                status='SUCCESS' if verified else 'PREMATURE_FINISH';f=dict(code=status);event['feedback']=f;break
            elif p.tool in ('stop_unknown','stop_no_match'):status='UNKNOWN_CONTEXT' if p.tool=='stop_unknown' else 'NO_DIRECT_MATCH';f=dict(code=status);event['feedback']=f;break
            else:status='INVALID_PROPOSAL';event['feedback']=dict(code=status);break
            event['feedback']=f;payload=f.get('context') or f.get('after');feedback.append(Feedback(f.get('code',f.get('status')),(),Snapshot(**{**payload,'values':tuple(tuple(x) for x in payload['values'])}) if payload else None))
        result=dict(status=status,verified=verified,dispatches=self.dispatches,transcript=trace,invocation=invocation)
        save(self.out/'transcript.json',trace);save(self.out/'result.json',result);return result
