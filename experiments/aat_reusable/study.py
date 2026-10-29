"""Private cross-domain evaluation driver; no worker imports of native truth."""
from contextlib import ExitStack
from dataclasses import asdict
from pathlib import Path
import argparse,csv,json,shutil,subprocess,sys,time
from rdflib import Graph,RDF,URIRef,Literal
from .profile import A,U,load,sha,Goal,Condition
from .runtime import save
from .harness import worker
from .cabinet_native import Cabinet,serve as cabinet_serve
from .cabinet_score import score as cabinet_score
from experiments.aat.native import Room,serve as room_serve,score as room_score,stamp
from semantic_action.supervision import settle_and_capture

ROOT=Path.cwd();DATA=Path(__file__).parent/'data';FREEZE=ROOT/'docs/artifacts/eswc_aat_cross_domain/freeze'

def frozen():
    m=json.loads((FREEZE/'runtime-freeze.json').read_text());changes=[p for p,h in m['shared_sha256'].items() if sha(p)!=h]
    changes += [p for p,h in m['installed_runtime_module_sha256'].items() if sha(p)!=h]
    if changes:raise ValueError('ZERO-CHANGE CRITERION FAILED: '+repr(changes))
    return dict(shared_unchanged=True,repository_paths=len(m['shared_sha256']),installed_paths=len(m['installed_runtime_module_sha256']))

def make_graph(domain,variant,path):
    g=Graph().parse(DATA/(domain+'.ttl'),format='turtle')
    if variant=='opaque_identifiers':
        names=sorted(set(g.subjects(RDF.type,A.Usage))|set(g.subjects(RDF.type,A.Operation)),key=str)
        rename={s:URIRef('urn:permuted:'+str(len(names)-i)) for i,s in enumerate(names)};h=Graph()
        for s,p,o in g:h.add((rename.get(s,s),p,rename.get(o,o)))
        g=h
    if variant=='ambiguous':
        slots={str(g.value(s,U.pointer)):s for s in g.subjects(RDF.type,U.Slot)}
        primary=slots['/temperature' if domain=='room' else '/latch/secured'];flag=slots['/heater_ready' if domain=='room' else '/interlocks/ready']
        for u in g.subjects(RDF.type,A.Usage):
            op=g.value(u,A.forOperation);physical=str(g.value(op,A.path));post=g.value(u,A.hasPostcond)
            old=list(g.objects(post,U.effect))
            for e in old:g.remove((post,U.effect,e));g.remove((e,None,None))
            for j,(kind,target,value) in enumerate([('AddInt' if domain=='room' else 'SetBool',primary,1 if domain=='room' else True),('SetBool',flag,physical in ('/heat','/cabinet/secure'))]):
                e=URIRef(str(u)+':conflict'+str(j));g.add((post,U.effect,e));g.add((e,RDF.type,U[kind]));g.add((e,U.onSlot,target));g.add((e,U.value,Literal(value)))
                if kind=='AddInt':g.add((e,U.unit,g.value(primary,U.unit)))
            g.remove((u,U.frameSlot,None))
            for s in g.subjects(RDF.type,U.Slot):
                if s not in (primary,flag):g.add((u,U.frameSlot,s))
    triples=sorted(' '.join(v.n3() for v in triple)+' .' for triple in g)
    if variant=='statement_source_order':triples.reverse()
    Path(path).write_text('\n'.join(triples)+'\n');return load(path,sha(path))

def target(cat,case):
    if case['domain']=='room':
        s=next(s for s in cat.slots if s.pointer=='/temperature');clauses=(Condition('Equal',s.id,22,unit=s.unit),)
    else:
        p={s.pointer:s.id for s in cat.slots};clauses=(Condition('Equal',p['/latch/secured'],case['target_secured']),Condition('Equal',p['/interlocks/door_closed'],True))
    return Goal(cat.thing,clauses)

def episode(case,condition,variant,out):
    frozen();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    graphs=[];catalogs={}
    for domain in ('room','cabinet'):
        p=out/(domain+'.ttl');catalogs[domain]=make_graph(domain,variant if domain==case['domain'] else 'original',p);graphs.append(p)
        spec=json.loads((DATA/(domain+'-spec.json')).read_text())
        if variant=='statement_source_order':spec=dict(reversed(list(spec.items())))
        save(out/(domain+'-source-spec.json'),spec);shutil.copyfile(DATA/(domain+'-review.json'),out/(domain+'-review.json'))
    states={'room':Room(case['initial_temperature'],case['ready'],case['ready'],case['mode']) if case['domain']=='room' else Room(),
            'cabinet':Cabinet(case['initial_secured'],case['ready'],case['mode']) if case['domain']=='cabinet' else Cabinet()}
    before={d:s.snapshot() for d,s in states.items()};active=states[case['domain']];cat=catalogs[case['domain']];goal=target(cat,case)
    assert all(s['requests']==s.get('mutations',s.get('writes'))==s['pending_requests']==0 for s in before.values())
    save(out/'reset.json',dict(passed=True,before=before));clock=time.monotonic()
    def intervention():
        if case['domain']=='cabinet':active.intervene(case['intervention']=='revision')
        elif case['intervention']=='context':active.intervene()
        else:
            with active.lock:
                b=active.snapshot();active.revision+=1;active.journal.append(dict(kind='external',at=stamp(),before=b,after=active.snapshot()))
    with ExitStack() as stack:
        origins={catalogs['room'].artifact:stack.enter_context(room_serve(states['room'])),catalogs['cabinet'].artifact:stack.enter_context(cabinet_serve(states['cabinet']))}
        knowledge=None
        if condition=='P':
            module='experiments.aat_reusable.'+case['domain']+'_local';knowledge=dict(module=module,sha256=sha(Path(__file__).parent/(case['domain']+'_local.py')),function='ambiguous' if variant=='ambiguous' else 'assess')
        result,process=worker(graphs,origins,goal,out/'execution',intervene=intervention if case.get('intervention') else None,
                stage='authorized' if case.get('intervention')=='revision' else 'intent',irrelevant=case['id']=='D03',knowledge=knowledge,reverse=variant=='registration_order')
        recovery=settle_and_capture(active,active.snapshot,maximum_wait_seconds=1.5)
        after={d:s.snapshot() for d,s in states.items()};journal=active.journal
        native=room_score(before['room'],after['room'],journal,22) if case['domain']=='room' else cabinet_score(before['cabinet'],after['cabinet'],journal,case['target_secured'])
        other='cabinet' if case['domain']=='room' else 'room';untouched=before[other]==after[other]
        accepted=bool(result.get('verified') and native['native_success'] and untouched)
        e=case['expected'];status=result.get('status');passed=(status==e['status'] and native['mutations']==e['mutations'] and native['goal_state']==e['native_goal'] and native['incorrect_native_transitions']==e['incorrect_transitions'] and accepted==e['accepted'])
        if case['id']=='D08':passed=passed and not any(x['path']=='/heat' for x in journal if x['kind']=='request') if case['domain']=='room' else passed and native['requests']==0
        passed=bool(passed and native['unauthorized_mutations']==0 and untouched and process['status']=='COMPLETED' and not recovery['state_uncertain'])
        calls=[dict(method=h['method'],path=h['path'],body=h['body']) for h in json.loads((out/'execution/worker/http.json').read_text()) if h['method']!='GET']
        expected_path=None if case['id'] in ('D04','D05','D06','D07','ambiguous') or case['id']=='D08' and case['domain']=='cabinet' else ('/cool' if case['id'] in ('D02','D08') else '/heat') if case['domain']=='room' else '/cabinet/release' if case['id']=='D02' else '/cabinet/secure'
        selection_correct=[c['path'] for c in calls]==([expected_path] if expected_path else [])
        passed=passed and selection_correct
        guards=[x['guard']['code'] for x in result.get('transcript',[]) if 'guard' in x]
        row=dict(case=case['id'],domain=case['domain'],condition=condition,variant=variant,status=status,accepted=accepted,passed=passed,
                 calls=calls,selection_correct=selection_correct,native=native,before=before,after=after,journal=journal,guards=guards,other_unchanged=untouched,process=process,recovery=recovery,
                 false_success=bool(result.get('verified') and not accepted),expected=e,worker_seconds=process['automated_runtime_seconds'])
    row['whole_seconds']=time.monotonic()-clock;save(out/'evaluation.json',row);frozen();return row

def admission_controls(out):
    out=Path(out);out.mkdir();rows=[]
    for domain in ('room','cabinet'):
        for control in ('predicate','effect','subject','type_unit','duplicate_write','frame_missing','frame_overlap','binding','source_hash','unreviewed'):
            g=Graph().parse(DATA/(domain+'.ttl'),format='turtle');u=next(g.subjects(RDF.type,A.Usage));pre=g.value(u,A.hasPrecond);post=g.value(u,A.hasPostcond);effect=g.value(post,U.effect);a=next(g.subjects(RDF.type,A.Artifact))
            if control=='predicate':g.set((g.value(pre,U.all),RDF.type,U.Unknown))
            elif control=='effect':g.set((effect,RDF.type,U.Unknown))
            elif control=='subject':g.set((pre,A.subject,URIRef('urn:wrong')))
            elif control=='type_unit':g.set((effect,U.value,Literal(True if domain=='room' else 1)))
            elif control=='duplicate_write':
                e=URIRef('urn:duplicate');g.add((post,U.effect,e))
                for p,o in g.predicate_objects(effect):g.add((e,p,o))
            elif control=='frame_missing':g.remove((u,U.frameSlot,g.value(u,U.frameSlot)))
            elif control=='frame_overlap':g.add((u,U.frameSlot,g.value(effect,U.onSlot)))
            elif control=='binding':g.set((u,A.forOperation,URIRef('urn:wrong')))
            elif control=='source_hash':g.remove((a,U.sourceHash,None))
            else:g.set((a,A.reviewed,Literal(False)))
            p=out/(domain+'-'+control+'.ttl');p.write_text('\n'.join(sorted(' '.join(v.n3() for v in t)+' .' for t in g))+'\n')
            try:load(p,sha(p));reason=None;rejected=False
            except ValueError as error:reason=str(error);rejected=True
            rows.append(dict(domain=domain,control=control,rejected=rejected,reason=reason))
    save(out/'decisions.json',rows);return rows

def normalize(r):
    return {k:r[k] for k in ('status','accepted','native','before','after','guards','other_unchanged','false_success','calls','selection_correct')}

def summarize(output):
    output=Path(output);raw=output/'raw'
    for n,h in json.loads((raw/'sha256.json').read_text()).items():
        if sha(raw/n)!=h:raise ValueError('Raw integrity')
    rows=json.loads((raw/'inventory.json').read_text());parity=[];invariance=[]
    for r in rows:
        if r['condition']=='S':
            match=[q for q in rows if (q['case'],q['domain'],q['variant'],q['condition'])==(r['case'],r['domain'],r['variant'],'P')]
            if len(match)!=1 or normalize(r)!=normalize(match[0]):parity.append([r['case'],r['domain'],r['variant']])
        if r['variant'] not in ('original','ambiguous'):
            original=next(q for q in rows if (q['case'],q['domain'],q['variant'],q['condition'])==(r['case'],r['domain'],'original',r['condition']))
            if normalize(r)!=normalize(original):invariance.append([r['case'],r['domain'],r['variant'],r['condition']])
    controls=json.loads((raw/'admission/decisions.json').read_text());stable=not json.loads((raw/'source-stability.json').read_text())['changed']
    good=len(rows)==88 and all(r['passed'] for r in rows) and not parity and not invariance and all(x['rejected'] for x in controls) and stable
    summary=dict(passed=good,episodes=len(rows),diagnostic_passes=sum(r['passed'] for r in rows),verified_successes=sum(r['accepted'] for r in rows),
                 safe_abstentions=sum(r['status'] in ('NO_DIRECT_MATCH','UNKNOWN_CONTEXT','AMBIGUOUS') for r in rows),
                 detected_failures=sum(r['status'] in ('CONFLICT','POSTCONDITION_FAILED','UNCERTAIN_MUTATION') for r in rows),
                 false_success_claims=sum(r['false_success'] for r in rows),admission_rejections=sum(c['rejected'] for c in controls),
                 parity_differences=parity,invariance_differences=invariance,zero_change_cabinet_onboarding=True,shared_source_unchanged=stable,
                 external_generalization=False,independent_authorship=False)
    derived=output/'derived';derived.mkdir(exist_ok=True);save(derived/'summary.json',summary)
    table=[dict(case=r['case'],domain=r['domain'],condition=r['condition'],variant=r['variant'],status=r['status'],accepted=r['accepted'],native_goal=r['native']['goal_state'],mutations=r['native']['mutations'],requests=r['native']['requests'],native_faults=r['native']['incorrect_native_transitions'],selection_correct=r['selection_correct'],passed=r['passed'],worker_seconds=r['worker_seconds'],whole_seconds=r['whole_seconds']) for r in rows]
    save(derived/'results.json',table)
    with (derived/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
    keys=list(table[0])[:-2];(derived/'table.md').write_text('| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+'\n'.join('| '+' | '.join(str(r[k]) for k in keys)+' |' for r in table)+'\n')
    print(json.dumps(summary,indent=2));return 0 if good else 1

def run(output):
    frozen();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);raw=output/'raw';raw.mkdir();rows=[];clock=time.monotonic();status='incomplete'
    shutil.copytree(FREEZE,raw/'freeze');shutil.copytree(DATA,raw/'data')
    paths=subprocess.check_output(['git','ls-files'],text=True).splitlines();hashes={p:sha(p) for p in paths}
    save(raw/'source.json',dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),working_tree=subprocess.check_output(['git','status','--porcelain'],text=True),hashes=hashes,python=sys.version))
    gate=json.loads((FREEZE/'native-case-expectations.json').read_text())['core']
    try:
        admission_controls(raw/'admission')
        tasks=[]
        for family in range(1,13):
            for domain in ('room','cabinet'):
                case=next(c for c in gate if c['id']==f'D{family:02d}' and c['domain']==domain)
                for condition in ('S','P') if family%2 else ('P','S'):tasks.append((case,condition,'original'))
        for name in ('D01','D02','D08'):
            for domain in ('room','cabinet'):
                case=next(c for c in gate if c['id']==name and c['domain']==domain)
                for condition in ('S','P'):
                    for variant in ('statement_source_order','opaque_identifiers','registration_order'):tasks.append((case,condition,variant))
        for domain in ('room','cabinet'):
            base=next(c for c in gate if c['id']=='D01' and c['domain']==domain)
            case={**base,'id':'ambiguous','intervention':None,'expected':dict(status='AMBIGUOUS',mutations=0,native_goal=False,incorrect_transitions=0,accepted=False)}
            for condition in ('S','P'):tasks.append((case,condition,'ambiguous'))
        for case,condition,variant in tasks:
            rows.append(episode(case,condition,variant,raw/'episodes'/f'e{len(rows)+1:03d}'));save(raw/'inventory.json',rows)
        status='completed'
    except Exception as error:save(raw/'harness-error.json',dict(error=f'{type(error).__name__}: {error}'));raise
    finally:
        save(raw/'inventory.json',rows);save(raw/'run-status.json',dict(status=status,elapsed_seconds=time.monotonic()-clock,freeze=frozen()))
        save(raw/'source-stability.json',dict(changed=[p for p,h in hashes.items() if sha(p)!=h]))
        save(raw/'sha256.json',{str(p.relative_to(raw)):sha(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='sha256.json'})
    return summarize(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=('run','summarize'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    return run(a.output) if a.command=='run' else summarize(a.output)
if __name__=='__main__':raise SystemExit(main())
