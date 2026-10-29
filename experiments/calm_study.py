"""Private CALM evaluation: historical postprocessing and bounded fixture interventions."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import argparse,csv,json,shutil,subprocess,sys,time
from collections import Counter
import jsonschema
from rdflib import Graph,RDF,URIRef,Literal
from .calm import build,verify,semantic,sha,canonical
from .aat_reusable.profile import A,U,load,Goal,Condition
from .aat_reusable.harness import worker
from .aat_reusable.runtime import save
from .aat_reusable.study import frozen
from .aat.native import Room,serve as room_serve,score as room_score,stamp
from .aat_reusable.cabinet_native import Cabinet,serve as cabinet_serve
from .aat_reusable.cabinet_score import score as cabinet_score
from semantic_action.supervision import settle_and_capture

HISTORY=Path('docs/artifacts/eswc_aat_cross_domain/run-001/raw')
DATA=Path('experiments/aat_reusable/data')
SCHEMA=Path('experiments/calm_schema.json')
VARIABLES=('readiness','goal_polarity','missing_observation','revision_freshness','wrong_effect','ambiguous_alternative')


def plan():
    rows=[]
    for domain in ('room','cabinet'):
        base=dict(readiness=True,goal_value=22 if domain=='room' else True,observation='present',revision_delta=0,effect_mode='normal',extra_candidate=False)
        for variable in VARIABLES:
            modified=deepcopy(base);key={'readiness':'readiness','goal_polarity':'goal_value','missing_observation':'observation','revision_freshness':'revision_delta','wrong_effect':'effect_mode','ambiguous_alternative':'extra_candidate'}[variable]
            modified[key]={'readiness':False,'goal_polarity':20 if domain=='room' else False,'missing_observation':'missing','revision_freshness':1,'wrong_effect':'wrong','ambiguous_alternative':True}[variable]
            assert [k for k in base if base[k]!=modified[k]]==[key]
            rows.append(dict(domain=domain,variable=variable,changed_input=key,baseline=base,treatment=modified,
                prediction=dict(baseline_status='SUCCESS',treatment_status={'readiness':'NO_DIRECT_MATCH','missing_observation':'UNKNOWN_CONTEXT','wrong_effect':'POSTCONDITION_FAILED','ambiguous_alternative':'AMBIGUOUS'}.get(variable,'SUCCESS'),
                    baseline_call='/heat' if domain=='room' else '/cabinet/secure',
                    treatment_call=None if variable in ('readiness','missing_observation','ambiguous_alternative') or variable=='goal_polarity' and domain=='cabinet' else '/cool' if variable=='goal_polarity' and domain=='room' else '/heat' if domain=='room' else '/cabinet/secure',
                    baseline_first_guard='AUTHORIZED',treatment_first_guard='STALE_PROPOSAL' if variable=='revision_freshness' else 'AMBIGUOUS' if variable=='ambiguous_alternative' else None if variable in ('readiness','missing_observation') or variable=='goal_polarity' and domain=='cabinet' else 'AUTHORIZED',
                    interpretation='Prospective model-relative prediction; same action but changed verification for wrong_effect; no external causal identification')))
    return rows


def graph(domain,extra,path):
    g=Graph().parse(DATA/(domain+'.ttl'),format='turtle')
    if extra:
        props={str(g.value(s,U.pointer)):s for s in g.subjects(RDF.type,U.Slot)}
        primary=props['/temperature' if domain=='room' else '/latch/secured'];flag=props['/heater_ready' if domain=='room' else '/interlocks/ready']
        op=next(o for o in g.subjects(RDF.type,A.Operation) if str(g.value(o,A.path))==('/cool' if domain=='room' else '/cabinet/release'))
        original=next(u for u in g.subjects(RDF.type,A.Usage) if g.value(u,A.forOperation)==op)
        uid=URIRef('urn:calm:extra-alternative');post=URIRef('urn:calm:extra-post');artifact=next(g.subjects(RDF.type,A.Artifact));thing=g.value(artifact,A.represents)
        for triple in ((artifact,U.usage,uid),(uid,RDF.type,A.Usage),(uid,A.forArtifact,artifact),(uid,A.forOperation,op),(uid,A.hasPrecond,g.value(original,A.hasPrecond)),(uid,A.hasPostcond,post),(post,RDF.type,A.ContextTemplate),(post,A.subject,thing)):g.add(triple)
        for i,(kind,slot,value) in enumerate([('AddInt' if domain=='room' else 'SetBool',primary,1 if domain=='room' else True),('SetBool',flag,False)]):
            e=URIRef('urn:calm:extra-effect'+str(i))
            for triple in ((post,U.effect,e),(e,RDF.type,U[kind]),(e,U.onSlot,slot),(e,U.value,Literal(value))):g.add(triple)
            if kind=='AddInt':g.add((e,U.unit,g.value(primary,U.unit)))
        for s in g.subjects(RDF.type,U.Slot):
            if s not in (primary,flag):g.add((uid,U.frameSlot,s))
    Path(path).write_text('\n'.join(sorted(' '.join(x.n3() for x in t)+' .' for t in g))+'\n')
    return load(path,sha(path))


def emit(explanation,episode,out):
    jsonschema.validate(explanation,json.loads(SCHEMA.read_text()));count=verify(explanation,episode)
    out=Path(out);out.mkdir(parents=True,exist_ok=False);save(out/'explanation.json',explanation);(out/'narrative.md').write_text(explanation['narrative']);save(out/'semantic.json',semantic(explanation));return count


def execute(domain,spec,out,enabled):
    frozen();out=Path(out);out.mkdir(parents=True,exist_ok=False);catalog=graph(domain,spec['extra_candidate'],out/'artifact.ttl')
    slots={s.pointer:s for s in catalog.slots}
    clauses=(Condition('Equal',slots['/temperature'].id,spec['goal_value'],unit=slots['/temperature'].unit),) if domain=='room' else (Condition('Equal',slots['/latch/secured'].id,spec['goal_value']),Condition('Equal',slots['/interlocks/door_closed'].id,True))
    goal=Goal(catalog.thing,clauses);mode='unknown' if spec['observation']=='missing' else spec['effect_mode']
    state=Room(21,spec['readiness'],True,mode) if domain=='room' else Cabinet(False,spec['readiness'],mode)
    before=state.snapshot();save(out/'control.json',dict(domain=domain,input=spec,explanation_after_execution=enabled,scope='One declared input intervention; fresh clocks/UUIDs/ports are incidental metadata',extra_alternative_scope='Deliberate conflicting model claim, not verified native API behavior'))
    def advance():
        if domain=='cabinet':state.intervene(revision_only=True)
        else:
            with state.lock:
                b=state.snapshot();state.revision+=1;state.journal.append(dict(kind='external',at=stamp(),before=b,after=state.snapshot()))
    serve=room_serve if domain=='room' else cabinet_serve
    with serve(state) as origin:
        result,process=worker([out/'artifact.ttl'],{catalog.artifact:origin},goal,out/'execution',intervene=advance if spec['revision_delta'] else None)
        recovery=settle_and_capture(state,state.snapshot,maximum_wait_seconds=1.5);after=state.snapshot()
        native=room_score(before,after,state.journal,spec['goal_value']) if domain=='room' else cabinet_score(before,after,state.journal,spec['goal_value'])
        http=json.loads((out/'execution/worker/http.json').read_text());calls=[h for h in http if h['method']!='GET'];guards=[t['guard']['code'] for t in result['transcript'] if 'guard' in t]
        row=dict(domain=domain,status=result['status'],verified=result['verified'],accepted=bool(result['verified'] and native['native_success']),calls=[{k:h[k] for k in ('method','path','body')} for h in calls],guards=guards,
                 before=before,after=after,native=native,journal=state.journal,process=process,recovery=recovery)
        assert process['status']=='COMPLETED' and not recovery['state_uncertain']
    save(out/'evaluation.json',row)
    hashes={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};save(out/'input-seal.json',hashes)
    if enabled:
        explanation=build(out,out/'input-seal.json');emit(explanation,out,out/'calm')
        assert all(sha(out/p)==h for p,h in hashes.items()) # Read-only, not runtime instrumentation.
    return row


def behavioral(row):
    return {k:row[k] for k in ('status','verified','accepted','calls','guards','before','after','native')} | {'journal':[{k:v for k,v in e.items() if k!='at'} for e in row['journal']]}


def run(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);raw=output/'raw';raw.mkdir();clock=time.monotonic();status='incomplete'
    paths=subprocess.check_output(['git','ls-files'],text=True).splitlines();source={p:sha(p) for p in paths}
    save(raw/'source.json',dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),working_tree=subprocess.check_output(['git','status','--porcelain'],text=True),hashes=source,python=sys.version))
    shutil.copyfile(SCHEMA,raw/'explanation-schema.json');save(raw/'intervention-plan.json',plan())
    save(raw/'historical-source.json',dict(baseline='f0f005ccaccc2c54d6fac7eda24986fd48551d08',root=str(HISTORY),seal_sha256=sha(HISTORY/'sha256.json'),episodes=88))
    history=[];pairs=[];coverage=Counter();claims=Counter();invariance=[]
    try:
        originals={}
        for i,episode in enumerate(sorted((HISTORY/'episodes').iterdir()),1):
            ex=build(episode,HISTORY/'sha256.json');count=emit(ex,episode,raw/'historical'/f'e{i:03d}')
            metadata=json.loads((episode/'evaluation.json').read_text());key=(metadata['case'],metadata['domain'],metadata['condition'])
            meaning=semantic(ex)
            if metadata['variant']=='original':originals[key]=meaning
            elif metadata['variant']!='ambiguous' and meaning!=originals[key]:invariance.append(dict(key=key,variant=metadata['variant']))
            for x in ex['coverage'].values():coverage[x['status']]+=1
            for c in ex['claims']:claims[c['plane']]+=1
            history.append(dict(episode=str(episode),claims=count,coverage=ex['coverage'],status=metadata['status'],accepted=metadata['accepted']))
        save(raw/'historical-coverage.json',dict(episodes=history,category_counts=dict(coverage),claim_planes=dict(claims),invariance_differences=invariance))
        for i,p in enumerate(plan(),1):
            outcomes={}
            for side in ('baseline','treatment'):
                for enabled in (False,True):
                    key=side+('-on' if enabled else '-off');out=raw/'counterfactuals'/f'p{i:02d}'/key
                    outcomes[key]=execute(p['domain'],p[side],out,enabled)
            no_interference=all(behavioral(outcomes[side+'-on'])==behavioral(outcomes[side+'-off']) for side in ('baseline','treatment'))
            correct=True
            for side in ('baseline','treatment'):
                row=outcomes[side+'-on'];expected_status=p['prediction'][side+'_status'];expected_call=p['prediction'][side+'_call'];expected_guard=p['prediction'][side+'_first_guard']
                correct &= row['status']==expected_status and [h['path'] for h in row['calls']]==([expected_call] if expected_call else []) and (row['guards'][0] if row['guards'] else None)==expected_guard
                correct &= not row['verified'] or row['native']['native_success']
            record=dict(pair=i,domain=p['domain'],variable=p['variable'],changed_input=p['changed_input'],baseline=p['baseline'],treatment=p['treatment'],prediction=p['prediction'],actual={k:behavioral(v) for k,v in outcomes.items()},predictions_matched=bool(correct),noninterference=no_interference)
            pairs.append(record);save(raw/'pair-results.json',pairs)
        status='completed'
    except Exception as error:save(raw/'error.json',dict(error=f'{type(error).__name__}: {error}'));raise
    finally:
        save(raw/'pair-results.json',pairs);save(raw/'run-status.json',dict(status=status,elapsed_seconds=time.monotonic()-clock,freeze=frozen()))
        save(raw/'source-stability.json',dict(changed=[p for p,h in source.items() if sha(p)!=h]))
        save(raw/'sha256.json',{str(p.relative_to(raw)):sha(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='sha256.json'})
    return summarize(output)


def summarize(output):
    output=Path(output);raw=output/'raw'
    for n,h in json.loads((raw/'sha256.json').read_text()).items():
        if sha(raw/n)!=h:raise ValueError('CALM raw integrity mismatch')
    h=json.loads((raw/'historical-coverage.json').read_text());pairs=json.loads((raw/'pair-results.json').read_text());stable=not json.loads((raw/'source-stability.json').read_text())['changed']
    summary=dict(passed=len(h['episodes'])==88 and len(pairs)==12 and not h['invariance_differences'] and all(p['predictions_matched'] and p['noninterference'] for p in pairs) and stable,
                 historical_explanations=88,historical_claims_verified=sum(e['claims'] for e in h['episodes']),historical_coverage=h['category_counts'],claim_planes=h['claim_planes'],
                 intervention_pairs=len(pairs),counterfactual_executions=len(pairs)*4,enabled_explanations=len(pairs)*2,predictions_matched=sum(p['predictions_matched'] for p in pairs),
                 noninterference_pairs=sum(p['noninterference'] for p in pairs),semantic_invariance_differences=h['invariance_differences'],source_stable=stable,external_causal_identification=False)
    derived=output/'derived';derived.mkdir(exist_ok=True);save(derived/'summary.json',summary)
    table=[dict(domain=p['domain'],intervention=p['variable'],baseline=p['actual']['baseline-on']['status'],treatment=p['actual']['treatment-on']['status'],prediction_matched=p['predictions_matched'],noninterference=p['noninterference']) for p in pairs]
    save(derived/'counterfactuals.json',table)
    with (derived/'counterfactuals.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
    keys=list(table[0]);(derived/'counterfactuals.md').write_text('| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+'\n'.join('| '+' | '.join(str(r[k]) for k in keys)+' |' for r in table)+'\n')
    print(json.dumps(summary,indent=2));return 0 if summary['passed'] else 1


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=('run','summarize'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    return run(a.output) if a.command=='run' else summarize(a.output)
if __name__=='__main__':raise SystemExit(main())
