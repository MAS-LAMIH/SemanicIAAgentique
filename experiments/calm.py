"""CALM/1: pure, deterministic postprocessing. No runtime, clock, network or fixture imports."""
import argparse
import hashlib
import json
from pathlib import Path

VERSION='calm/1'

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def at(value,pointer):
    if pointer=='':return value
    if not pointer.startswith('/'):raise ValueError('JSON Pointer required')
    for key in pointer[1:].split('/'):
        key=key.replace('~1','/').replace('~0','~');value=value[int(key)] if isinstance(value,list) else value[key]
    return value

def raw_atom(c,values):
    """Raw captured-value interpretation only; not a historical freshness verdict."""
    if not isinstance(c,dict) or not all(k in c for k in ('kind','slot','value')):return 'UNAVAILABLE'
    v=dict(values).get(c['slot'])
    if v is None:return 'UNKNOWN'
    if c['kind']=='Equal':return 'UNKNOWN' if type(v) is not type(c['value']) else 'TRUE' if v==c['value'] else 'FALSE'
    if c['kind']=='IntRange' and c.get('upper') is not None:return 'UNKNOWN' if type(v) is not int else 'TRUE' if c['value']<=v<=c['upper'] else 'FALSE'
    return 'UNAVAILABLE'

def rule(name,inputs):
    if name=='copy':return inputs[0]
    if name=='raw_atom':return raw_atom(*inputs)
    if name=='candidate_status':
        c=inputs[0];return dict(applicability=c['applicable'],goal_contribution=c['contributes'],eligible=c['applicable']==c['contributes']=='TRUE')
    if name=='compare':
        expected,actual,evidence=inputs
        return 'UNKNOWN' if not evidence or expected is None or actual is None else 'TRUE' if type(expected) is type(actual) and expected==actual else 'FALSE'
    if name=='context_changes':
        old,new=inputs;out=[]
        for k in ('thing','revision','mutations'):
            if old[k]!=new[k]:out.append(k)
        a,b=dict(old['values']),dict(new['values'])
        out += sorted(k for k in a.keys()|b.keys() if a.get(k)!=b.get(k) or type(a.get(k)) is not type(b.get(k)))
        return out
    raise ValueError('Unsupported explanation rule')


class Evidence:
    def __init__(self,episode,seal=None):
        self.episode=Path(episode).resolve();self.docs={};self.files={};self.claims=[]
        self.seal=Path(seal).resolve() if seal else None
        self.hashes=json.loads(self.seal.read_text()) if self.seal else None
    def doc(self,name):
        if name not in self.docs:
            p=self.episode/name;h=sha(p)
            if self.seal and self.hashes.get(str(p.relative_to(self.seal.parent)))!=h:raise ValueError('Unsealed/changed input '+name)
            self.docs[name]=json.loads(p.read_text());self.files[name]=h
        return self.docs[name]
    def ref(self,name,pointer):
        at(self.doc(name),pointer);return dict(file=name,sha256=self.files[name],pointer=pointer)
    def claim(self,rule_,plane,*refs):
        value=rule(rule_,[at(self.doc(r['file']),r['pointer']) for r in refs]);cid='c'+str(len(self.claims)+1).zfill(5)
        self.claims.append(dict(id=cid,rule=rule_,plane=plane,value=value,evidence=list(refs)));return cid
    def copy(self,file,pointer,plane='agent_record'):return self.claim('copy',plane,self.ref(file,pointer))


def build(episode,seal=None):
    """Read inputs only; absent evidence stays unavailable. Never reads oracle expectations."""
    e=Evidence(episode,seal);base='execution/worker/';steps=[];lines=[]
    def optional(name):return e.doc(name) if (e.episode/name).is_file() else None
    config=optional(base+'input.json');trace=optional(base+'transcript.json');result=optional(base+'result.json');discovery=optional(base+'discovery.json')
    http=optional(base+'http.json');native=optional('evaluation.json');coverage={}
    goal=e.copy(base+'input.json','/goal') if config and 'goal' in config else None
    cat=None;catalog_claim=None
    if config and discovery:
        matches=[(i,c) for i,c in enumerate(discovery) if c['thing']==config['goal']['thing']]
        if len(matches)==1:
            i,cat=matches[0];catalog_claim=e.copy(base+'discovery.json','/'+str(i))
    ops={o['id']:o for o in cat['operations']} if cat else {};slots={s['id']:s for s in cat['slots']} if cat else {}
    binding=lambda op:canonical({k:ops[op][k] for k in ('method','path','body','request_revision')}) if op in ops else str(op)
    def predicate_key(c):return canonical({**c,'slot':slots.get(c['slot'],{}).get('property',c['slot'])})
    atom_count=0;context_count=0;guard_count=0;proposal_count=0
    for i,t in enumerate(trace or []):
        root='/'+str(i);v=t.get('view',{});ctx=v.get('context');descriptions={u['id']:u for u in v.get('descriptions',[])}
        step=dict(turn=e.copy(base+'transcript.json',root+'/turn'),context=e.copy(base+'transcript.json',root+'/view/context') if ctx else None,
                  goal_truth=e.copy(base+'transcript.json',root+'/view/goal_truth') if 'goal_truth' in v else None,candidates=[],
                  proposal=e.copy(base+'transcript.json',root+'/proposal') if 'proposal' in t else None,guard=None,feedback=None,changed_context=None)
        context_count+=bool(ctx);proposal_count+=step['proposal'] is not None
        candidates=list(enumerate(v.get('candidates',[])))
        for j,c in sorted(candidates,key=lambda jc:(binding(jc[1]['operation']),canonical(jc[1]['expected']))):
            ptr=root+'/view/candidates/'+str(j);ref=e.ref(base+'transcript.json',ptr)
            item=dict(record=e.claim('copy','agent_record',ref),eligibility=e.claim('candidate_status','record_translation',ref),description=None,raw_preconditions=[])
            u=descriptions.get(c['handle'])
            if u and ctx:
                u_index=next(n for n,x in enumerate(v['descriptions']) if x['id']==u['id'])
                item['description']=e.copy(base+'transcript.json',root+'/view/descriptions/'+str(u_index),'reviewed_model')
                for n,condition in sorted(enumerate(u.get('pre',[])),key=lambda nc:predicate_key(nc[1])):
                    cr=e.ref(base+'transcript.json',root+'/view/descriptions/'+str(u_index)+'/pre/'+str(n))
                    item['raw_preconditions'].append(dict(description=e.claim('copy','reviewed_model',cr),truth=e.claim('raw_atom','model_replay',cr,e.ref(base+'transcript.json',root+'/view/context/values'))));atom_count+=1
            step['candidates'].append(item)
        if 'guard' in t:
            step['guard']=e.copy(base+'transcript.json',root+'/guard');guard_count+=1
            if ctx and t['guard'].get('context'):
                step['changed_context']=e.claim('context_changes','record_comparison',e.ref(base+'transcript.json',root+'/view/context'),e.ref(base+'transcript.json',root+'/guard/context'))
        if 'feedback' in t:step['feedback']=e.copy(base+'transcript.json',root+'/feedback','runtime_observation')
        steps.append(step)
        p=t.get('proposal',{});line='Turn '+str(t['turn'])+': proposed '+str(p.get('tool','unavailable'))+' ['+str(step['proposal'])+'].'
        if p.get('tool')=='use':
            chosen=next((c for c in v.get('candidates',[]) if c['handle']==p.get('handle')),None)
            if chosen:
                o=ops.get(chosen['operation'],{});line+=' '+o.get('method','')+' '+o.get('path',chosen['operation'])+'; recorded applicability='+chosen['applicable']+', goal contribution='+chosen['contributes']+' ['+next(item['record'] for item in step['candidates'] if next(x['value'] for x in e.claims if x['id']==item['record'])['handle']==chosen['handle'])+'].'
            alternatives=[]
            for item in step['candidates']:
                cc=next(x['value'] for x in e.claims if x['id']==item['record'])
                if cc['handle']!=p.get('handle'):
                    o=ops.get(cc['operation'],{});alternatives.append(o.get('path',cc['operation'])+' applicability='+cc['applicable']+', contribution='+cc['contributes']+' ['+item['record']+']')
            if alternatives:line+=' Alternatives: '+'; '.join(alternatives)+'.'
            if chosen and chosen['handle'] in descriptions:
                targets={x['slot'] for x in descriptions[chosen['handle']]['effects']}
                predicted={slots.get(k,{}).get('property',k):v for k,v in chosen['expected'] if k in targets}
                line+=' Recorded forecast targets='+canonical(predicted)+' (predicted, not observed).'
        if ctx and step['goal_truth']:line+=' Recorded goal truth='+str(v.get('goal_truth'))+' ['+step['goal_truth']+'].'
        if p.get('tool') in ('stop_unknown','stop_no_match','finish') and step['candidates']:
            summaries=[]
            for item in step['candidates']:
                c=next(x['value'] for x in e.claims if x['id']==item['record']);o=ops.get(c['operation'],{})
                summaries.append(o.get('path',c['operation'])+' applicability='+c['applicable']+', contribution='+c['contributes']+' ['+item['record']+']')
            line+=' Recorded candidates: '+'; '.join(summaries)+'.'
        if step['guard']:line+=' Guard='+t['guard']['code']+' ['+step['guard']+'].'
        lines.append(line)
    outcome=dict(status=None,verified=None,dispatches=None,http=None,checks=None,before=None,after=None,effect_comparisons=[],frame_comparisons=[],native_score=None,native_before=None,native_after=None,native_journal=None)
    if result:
        for k in ('status','verified','dispatches'):
            if k in result:outcome[k]=e.copy(base+'result.json','/'+k,'runtime_observation')
        invocation=result.get('invocation')
        if invocation:
            for key,target in (('checks','checks'),('before','before'),('after','after')):
                if key in invocation:outcome[target]=e.copy(base+'result.json','/invocation/'+key,'runtime_observation')
            if invocation.get('before') and invocation.get('after') and 'checks' in invocation:
                authorized=next((t for t in reversed(trace or []) if t.get('guard',{}).get('code')=='AUTHORIZED'),None)
                selected=authorized['guard'].get('assessment') if authorized else None
                u=next((u for u in authorized.get('view',{}).get('descriptions',[]) if selected and u['id']==selected['handle']),None) if authorized else None
                if selected and u:
                    ti=next(i for i,t in enumerate(trace) if t is authorized)
                    ui=next(i for i,x in enumerate(authorized['view']['descriptions']) if x['id']==u['id'])
                    declaration=e.copy(base+'transcript.json','/'+str(ti)+'/view/descriptions/'+str(ui),'reviewed_model')
                    for category,keys in (('effect_comparisons',[x['slot'] for x in u['effects']]),('frame_comparisons',u['frame'])):
                        for slot in sorted(keys,key=lambda s:slots.get(s,{}).get('property',s)):
                            actual=next((i for i,x in enumerate(invocation['after']['values']) if x[0]==slot),None)
                            before=next((i for i,x in enumerate(invocation['before']['values']) if x[0]==slot),None)
                            predicted=next((i for i,x in enumerate(selected['expected']) if x[0]==slot),None)
                            if actual is None or before is None or predicted is None:continue
                            expected_ref=e.ref(base+'result.json','/invocation/before/values/'+str(before)+'/1') if category=='frame_comparisons' else e.ref(base+'transcript.json','/'+str(ti)+'/guard/assessment/expected/'+str(predicted)+'/1')
                            truth=e.claim('compare','record_comparison',expected_ref,e.ref(base+'result.json','/invocation/after/values/'+str(actual)+'/1'),e.ref(base+'result.json','/invocation/checks/evidence'))
                            outcome[category].append(dict(slot=slot,truth=truth,declaration=declaration))
    if http is not None:outcome['http']=e.copy(base+'http.json','','runtime_observation')
    if native and 'native' in native:
        outcome['native_score']=e.copy('evaluation.json','/native','native_evaluation')
        for key in ('before','after','journal'):
            if key in native:outcome['native_'+key]=e.copy('evaluation.json','/'+key,'native_evaluation')
    def cover(key,status,reason=None):coverage[key]=dict(status=status,reason=reason)
    for key,present in [('observed_context',context_count),('goal',goal),('candidate_aggregates',any(s['candidates'] for s in steps)),('prediction',any(s['candidates'] for s in steps)),('selection_or_abstention',proposal_count),('http_results',outcome['http']),('native_scoring',outcome['native_score'])]:cover(key,'direct' if present else 'unavailable','Retained field absent' if not present else None)
    cover('raw_model_preconditions','reconstructed' if atom_count else 'unavailable','Raw predicate replay does not establish runtime freshness or procedural atom evaluation')
    cover('guard_decision','direct' if guard_count else 'not_applicable' if trace and not any(t.get('proposal',{}).get('tool')=='use' for t in trace) else 'unavailable')
    dispatched=result.get('dispatches',0) if result else None
    cover('runtime_postconditions','direct' if outcome['checks'] else 'not_applicable' if dispatched==0 else 'unavailable')
    cover('frame_verification','reconstructed' if outcome['frame_comparisons'] else 'not_applicable' if dispatched==0 else 'unavailable','Runtime records aggregate expected_state, not a separate frame verdict')
    for key,reason in [('runtime_precondition_atoms','Not logged; aggregate truth cannot identify which atom was evaluated FALSE/UNKNOWN'),('permit_contents','Permit object/nonce/expiry/goal hash not serialized; authorized barrier file contains proposal only'),('freshness_clock','Exact evaluation clock and age calculation not logged'),('hidden_reasoner_intent','No private reasoning trace; proposal consistency is not mental causation'),('general_causal_identification','Only bounded model-relative comparisons and explicitly controlled fixture interventions supported')]:cover(key,'unavailable',reason)
    if result:lines.append('Recorded terminal status='+str(result.get('status'))+' ['+str(outcome['status'])+']; verified='+str(result.get('verified'))+' ['+str(outcome['verified'])+'].')
    if outcome['checks']:lines.append('Recorded runtime checks='+canonical(result['invocation']['checks'])+' ['+outcome['checks']+'].')
    for category in ('effect_comparisons','frame_comparisons'):
        if outcome[category]:lines.append('Reconstructed '+category+': '+', '.join(slots.get(x['slot'],{}).get('property',x['slot'])+'='+str(next(c['value'] for c in e.claims if c['id']==x['truth']))+' ['+x['truth']+']' for x in outcome[category])+'.')
    if outcome['native_score']:lines.append('Separate native-scoring plane: '+canonical(native['native'])+' ['+outcome['native_score']+']. This must not be treated as an agent observation.')
    lines.append('Unavailable: actual per-atom runtime verdicts, permit contents, evaluation clock and hidden intent. Raw predicate/frame replays are explicitly reconstructed, not general causal identification.')
    return dict(schema_version=VERSION,provenance=dict(files=e.files,integrity='verified' if seal else 'unsealed'),catalog=catalog_claim,goal=goal,claims=e.claims,steps=steps,outcome=outcome,coverage=coverage,narrative='\n'.join(lines)+'\n')


def verify(explanation,episode):
    """Every asserted value is a source copy or a bounded rule replay, with hashed inputs."""
    ids=set()
    for claim in explanation['claims']:
        if claim['id'] in ids:raise ValueError('Duplicate claim id')
        ids.add(claim['id']);inputs=[]
        planes={'raw_atom':'model_replay','candidate_status':'record_translation','compare':'record_comparison','context_changes':'record_comparison'}
        if claim['rule'] in planes and claim['plane']!=planes[claim['rule']]:raise ValueError('Evidence plane mismatch')
        for ref in claim['evidence']:
            path=(Path(episode)/ref['file']).resolve()
            if not path.is_relative_to(Path(episode).resolve()) or sha(path)!=ref['sha256']:raise ValueError('Evidence hash/path mismatch')
            inputs.append(at(json.loads(path.read_text()),ref['pointer']))
        if canonical(rule(claim['rule'],inputs))!=canonical(claim['value']):raise ValueError('Unsupported claim value')
    def links(value):
        if isinstance(value,str) and value.startswith('c') and value[1:].isdigit() and value not in ids:raise ValueError('Dangling claim reference')
        if isinstance(value,dict):
            for v in value.values():links(v)
        if isinstance(value,list):
            for v in value:links(v)
    for key in ('catalog','goal','steps','outcome'):links(explanation[key])
    rebuilt=build(episode)
    normalized={**explanation,'provenance':{**explanation['provenance'],'integrity':'unsealed'}}
    if canonical(normalized)!=canonical(rebuilt):raise ValueError('Explanation structure/narrative differs from grounded builder')
    return len(ids)


def semantic(explanation):
    """Identifier/provenance/time-free meaning, not byte identity of cited reports."""
    claims={c['id']:c['value'] for c in explanation['claims']};value=lambda c:claims[c] if c else None
    cat=value(explanation['catalog']) or {};slots={s['id']:s['property'] for s in cat.get('slots',[])};ops={o['id']:o for o in cat.get('operations',[])}
    facts=lambda vs:sorted((slots.get(k,k),v) for k,v in vs)
    def ctx(c):return None if not c else dict(thing=c['thing'],values=facts(c['values']),revision=c['revision'],mutations=c['mutations'])
    def binding(op):return {k:ops[op][k] for k in ('method','path','body','request_revision')} if op in ops else None
    goal=value(explanation['goal'])
    if goal:goal={**goal,'clauses':sorted([{**c,'slot':slots.get(c['slot'],c['slot'])} for c in goal['clauses']],key=canonical)}
    steps=[]
    for s in explanation['steps']:
        cs=[];selected=None;p=value(s['proposal']) or {}
        for item in s['candidates']:
            c=value(item['record']);atoms=[]
            for atom in item['raw_preconditions']:
                d=value(atom['description']);atoms.append(dict(condition={**d,'slot':slots.get(d['slot'],d['slot'])},raw_truth=value(atom['truth'])))
            cc=dict(binding=binding(c['operation']),applicable=c['applicable'],contributes=c['contributes'],expected=facts(c['expected']),raw_model=sorted(atoms,key=canonical))
            cs.append(cc)
            if c['handle']==p.get('handle'):selected=binding(c['operation'])
        g=value(s['guard']);changes=value(s['changed_context'])
        steps.append(dict(context=ctx(value(s['context'])),goal_truth=value(s['goal_truth']),candidates=sorted(cs,key=canonical),tool=p.get('tool'),selected=selected,
                          guard=g.get('code') if g else None,changed=sorted(slots.get(x,x) for x in changes) if changes is not None else None))
    o=explanation['outcome'];http=value(o['http']) or []
    return dict(goal=goal,steps=steps,status=value(o['status']),verified=value(o['verified']),checks=value(o['checks']),
                effect_comparisons=sorted([(slots.get(x['slot'],x['slot']),value(x['truth'])) for x in o['effect_comparisons']]),
                frame_comparisons=sorted([(slots.get(x['slot'],x['slot']),value(x['truth'])) for x in o['frame_comparisons']]),
                native=value(o['native_score']),calls=[{k:h[k] for k in ('method','path','body')} for h in http if h['method']!='GET'],coverage=explanation['coverage'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--episode',type=Path,required=True);p.add_argument('--seal',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.resolve()==a.episode.resolve() or a.output.resolve().is_relative_to(a.episode.resolve()):raise ValueError('Write explanations outside evidence inputs')
    ex=build(a.episode,a.seal);verify(ex,a.episode);a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'explanation.json').write_text(json.dumps(ex,sort_keys=True,indent=2)+'\n');(a.output/'narrative.md').write_text(ex['narrative'])
if __name__=='__main__':main()
