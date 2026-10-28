"""Observe–reason–act–observe kernel. No native fixture/control imports."""
from dataclasses import asdict
import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4
import time
from semantic_action.model import Truth, now
from semantic_action.oracle import current
from semantic_action.transport import HTTPTransport
from .model import NS, ContextSnapshot, Candidate, ControllerView, Proposal, Permit, Usage, Feedback


def dump(path,value):
    Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def fresh(ctx,goal):
    return ctx is not None and current({'observed_at':ctx.observed_at},goal.max_age)


def complete(ctx):
    return ctx is not None and all(type(v) is int for v in (ctx.temperature,ctx.revision,ctx.mutations)) and bool(ctx.sentinel_json)


def definitions(catalog,mode):
    if mode=='semantic':return catalog.usages
    if mode!='procedural':raise ValueError('Unknown controller condition')
    # Native API-local knowledge, not RDF preconditions/effects or Usage names.
    result=[]
    for op in catalog.operations:
        ready,delta,lo,hi={'/heat':('heaterReady',1,18,25),'/cool':('coolerReady',-1,19,26)}[op.path]
        result.append(Usage(op.id,op.artifact,op.id,'local-pre','local-post',NS+ready,lo,hi,delta,
                            (NS+'heaterReady',NS+'coolerReady',NS+'sentinels'),'procedural native contract/1'))
    return tuple(result)


def candidates(goal,ctx,descriptions):
    result=[]
    for u in descriptions:
        reasons=[];truth=Truth.TRUE
        ready=(ctx.heater_ready if u.ready_property==NS+'heaterReady' else ctx.cooler_ready) if ctx else None
        if not fresh(ctx,goal) or not complete(ctx):truth=Truth.UNKNOWN;reasons.append('Missing/stale complete context')
        elif ctx.thing!=goal.thing:truth=Truth.FALSE;reasons.append('Wrong grounded subject')
        elif ready is None:truth=Truth.UNKNOWN;reasons.append('Readiness UNKNOWN')
        elif ready is not True or not u.minimum<=ctx.temperature<=u.maximum:truth=Truth.FALSE;reasons.append('Readiness/bounds FALSE')
        predicted=ctx.temperature+u.delta if ctx and type(ctx.temperature) is int else None
        contributes=predicted==goal.temperature
        if not contributes:reasons.append('Predicted effect does not establish goal')
        result.append(Candidate(u.id,u.operation,truth,contributes,predicted,tuple(reasons)))
    return tuple(result)


class Reasoner(Protocol):
    def propose(self,view:ControllerView)->Proposal: ...


class ScriptedReasoner:
    """Uses runtime evidence/descriptions, never case IDs or expected actions."""
    def propose(self,view):
        if not view.discovered:return Proposal('discover')
        if view.context is None:return Proposal('observe')
        if not fresh(view.context,view.goal) or not complete(view.context):return Proposal('stop_unknown')
        if view.context.temperature==view.goal.temperature:return Proposal('finish')
        eligible=[c for c in view.candidates if c.applicable==Truth.TRUE and c.contributes]
        if not eligible:return Proposal('stop_unknown' if any(c.applicable==Truth.UNKNOWN and c.contributes for c in view.candidates) else 'stop_no_match')
        return Proposal('use',min(eligible,key=lambda c:c.handle).handle,view.context.id)


class Runtime:
    def __init__(self,catalog,origin,mode,goal,output):
        self.catalog,self.origin,self.mode,self.goal,self.output=catalog,origin,mode,goal,Path(output)
        self.output.mkdir(parents=True,exist_ok=True);self.descriptions=definitions(catalog,mode)
        self.transport=HTTPTransport(origin);self.http=[];self.observations=[];self.issued={};self.dispatches=0

    def request(self,method,path,body=None):
        t=time.monotonic();r=self.transport._http_request(method,path,body)
        self.http.append(dict(method=method,path=path,body=body,result=asdict(r),at=now(),elapsed_seconds=time.monotonic()-t))
        dump(self.output/'http.json',self.http);return r

    def observe(self):
        r=self.request('GET',self.catalog.artifact.observation_path);b=r.body if r.success else {}
        integer=lambda k:b.get(k) if type(b.get(k)) is int else None
        boolean=lambda k:b.get(k) if type(b.get(k)) is bool else None
        ctx=ContextSnapshot('urn:context:'+str(uuid4()),b.get('thing') if isinstance(b.get('thing'),str) else '',integer('temperature'),boolean('heater_ready'),
            boolean('cooler_ready'),integer('revision'),integer('mutations'),
            json.dumps(b['sentinels'],sort_keys=True) if isinstance(b.get('sentinels'),dict) else '',b.get('observed_at'),json.dumps(b,sort_keys=True))
        self.observations.append(ctx);return ctx

    def authorize(self,proposal,old):
        if proposal.tool!='use' or old is None or proposal.snapshot_ref!=old.id:return None,dict(code='INVALID_PROPOSAL')
        u=next((u for u in self.descriptions if u.id==proposal.handle),None)
        if u is None:return None,dict(code='UNKNOWN_USAGE')
        ctx=self.observe()
        if not fresh(old,self.goal) or not fresh(ctx,self.goal) or not complete(ctx):return None,dict(code='UNKNOWN_CONTEXT',context=asdict(ctx))
        if (old.revision,old.temperature,old.heater_ready,old.cooler_ready,old.sentinel_json)!=(ctx.revision,ctx.temperature,ctx.heater_ready,ctx.cooler_ready,ctx.sentinel_json):
            return None,dict(code='STALE_PROPOSAL',context=asdict(ctx))
        c=next(c for c in candidates(self.goal,ctx,(u,)))
        if c.applicable!=Truth.TRUE or not c.contributes:return None,dict(code='NOT_AUTHORIZED',assessment=asdict(c))
        permit=Permit(str(uuid4()),u.id,ctx.revision,self.catalog.graph_hash)
        self.issued[permit.nonce]=(permit,ctx,u)
        return permit,dict(code='AUTHORIZED',assessment=asdict(c),context=asdict(ctx))

    def execute(self,permit):
        entry=self.issued.pop(permit.nonce,None)
        if entry is None or entry[0]!=permit or permit.graph_hash!=self.catalog.graph_hash or self.dispatches:
            raise ValueError('Invalid, reused or over-budget permit')
        _,before,u=entry
        if not fresh(before,self.goal):return dict(status='UNKNOWN_CONTEXT',verified=False)
        op=next(o for o in self.catalog.operations if o.id==u.operation)
        self.dispatches+=1;started=now();r=self.request(op.method,op.path,{'expected_revision':permit.revision})
        after=self.observe()
        enough=fresh(after,self.goal) and complete(after) and current({'observed_at':after.observed_at},self.goal.max_age,started)
        checks=dict(evidence_sufficient=enough,postcondition=enough and after.temperature==before.temperature+u.delta,
            revision=enough and after.revision==before.revision+1,mutation_count=enough and after.mutations==before.mutations+1,
            frame=enough and (after.heater_ready,after.cooler_ready,after.sentinel_json)==(before.heater_ready,before.cooler_ready,before.sentinel_json),
            goal=enough and after.thing==self.goal.thing and after.temperature==self.goal.temperature,
            response_revision=enough and r.body.get('revision')==after.revision,
            response_schema=set(r.body)=={'revision','temperature'} and all(type(r.body[k]) is int for k in r.body) and r.body.get('temperature')==after.temperature)
        verified=bool(r.success and all(checks.values()))
        status=('UNCERTAIN_MUTATION' if r.status is None else 'SUCCESS' if verified else
                'CONFLICT' if r.status==409 and enough and after.mutations==before.mutations else 'POSTCONDITION_FAILED')
        return dict(status=status,verified=verified,checks=checks,invocation=asdict(r),before=asdict(before),after=asdict(after),started_at=started)

    def barrier(self,index,stage,proposal):
        """Public synchronization; the private driver never supplies a chosen handle."""
        dump(self.output/f'{stage}-{index}.json',asdict(proposal))
        deadline=time.monotonic()+10
        while not (self.output/f'release-{stage}-{index}').exists():
            if time.monotonic()>deadline:raise TimeoutError('Driver barrier unavailable')
            time.sleep(.003)

    def run(self,reasoner=None):
        reasoner=reasoner or ScriptedReasoner();ctx=None;discovered=False;feedback=[];transcript=[];status='BUDGET_EXHAUSTED';verified=False;invocation=None
        for turn in range(1,7):
            view=ControllerView(self.goal,discovered,ctx,self.descriptions if discovered else (),candidates(self.goal,ctx,self.descriptions) if discovered else (),tuple(feedback))
            p=reasoner.propose(view)
            if not isinstance(p,Proposal):p=Proposal('invalid')
            event=dict(turn=turn,view=asdict(view),proposal=asdict(p),feedback=None)
            transcript.append(event);dump(self.output/'transcript.json',transcript)
            if p.tool=='discover':
                discovered=True;event['feedback']=dict(code='DISCOVERED',artifact=asdict(self.catalog.artifact),operations=[asdict(o) for o in self.catalog.operations],usages=[asdict(u) for u in self.descriptions])
            elif p.tool=='observe':ctx=self.observe();event['feedback']=dict(code='OBSERVED',context=asdict(ctx))
            elif p.tool=='use':
                chosen=next((u for u in self.descriptions if u.id==p.handle),None)
                op=next((o for o in self.catalog.operations if chosen and o.id==chosen.operation),None)
                event['operation_path']=op.path if op else None
                self.barrier(turn,'intent',p);permit,f=self.authorize(p,ctx);event['guard']=f
                if permit is None:event['feedback']=f;ctx=None
                else:
                    self.barrier(turn,'authorized',p);invocation=self.execute(permit);event['feedback']=invocation
                    status=invocation['status']
                    if invocation['verified']:
                        ctx=self.observations[-1];status='BUDGET_EXHAUSTED' # Finish still required.
                    else:break # No speculative second dispatch after any uncertain/failed mutation.
            elif p.tool=='finish':
                latest=self.observe()
                verified=bool(fresh(latest,self.goal) and complete(latest) and latest.thing==self.goal.thing and latest.temperature==self.goal.temperature
                      and ctx is not None and (latest.revision,latest.mutations,latest.heater_ready,latest.cooler_ready,latest.sentinel_json)==(ctx.revision,ctx.mutations,ctx.heater_ready,ctx.cooler_ready,ctx.sentinel_json)
                      and (self.dispatches==0 or invocation and invocation['verified']))
                status='SUCCESS' if verified else 'PREMATURE_FINISH';event['feedback']=dict(code=status,verified=verified);break
            elif p.tool in {'stop_unknown','stop_no_match'}:
                status='UNKNOWN_CONTEXT' if p.tool=='stop_unknown' else 'NO_ELIGIBLE';event['feedback']=dict(code=status);break
            else:status='INVALID_PROPOSAL';event['feedback']=dict(code=status);break
            f=event['feedback'];context_data=f.get('context') or f.get('after')
            feedback.append(Feedback(f.get('code',f.get('status','RESULT')),tuple((f.get('assessment') or {}).get('reasons',())),ContextSnapshot(**context_data) if context_data else None))
            dump(self.output/'transcript.json',transcript)
        result=dict(status=status,verified=verified,dispatches=self.dispatches,transcript=transcript,invocation=invocation)
        dump(self.output/'transcript.json',transcript);dump(self.output/'result.json',result)
        self.serialize_contexts();return result

    def serialize_contexts(self):
        from rdflib import Graph, Namespace, RDF, URIRef, Literal
        a=Namespace(NS);g=Graph();goal=URIRef('urn:goal:room');agent=URIRef('urn:agent:'+self.mode)
        g.add((agent,RDF.type,a.Agent));g.add((agent,a.pursuesGoal,goal))
        g.add((goal,RDF.type,a.Goal));g.add((goal,a.subject,URIRef(self.goal.thing)));g.add((goal,a.temperatureC,Literal(self.goal.temperature)));g.add((goal,a.maxEvidenceAgeSeconds,Literal(self.goal.max_age)))
        for ctx in self.observations:
            node=URIRef(ctx.id);g.add((agent,a.observedContext,node));g.add((node,RDF.type,a.ContextSnapshot));
            if ctx.thing:g.add((node,a.subject,URIRef(ctx.thing)))
            g.add((node,a.sentinelState,Literal(ctx.sentinel_json,datatype=RDF.JSON)))
            for key,value in [('temperatureC',ctx.temperature),('heaterReady',ctx.heater_ready),('coolerReady',ctx.cooler_ready),('revision',ctx.revision),('mutationCount',ctx.mutations),('observedAt',ctx.observed_at)]:
                if value is not None:g.add((node,a[key],Literal(value)))
        g.serialize(destination=self.output/'contexts.ttl',format='turtle')
