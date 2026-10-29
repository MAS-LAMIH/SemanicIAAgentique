"""Private controlled-fixture driver, native scoring, sealing and table export."""
import argparse
from dataclasses import asdict
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from threading import Event, Thread
from .native import Room, serve, score
from .model import StateGoal, ROOM
from .rdf import load, AA
from .runtime import dump

ROOT=Path(__file__).resolve().parents[2]
DATA=Path(__file__).parent/'data'


def cases():
    return [dict(id='R01',temperature=21,status='SUCCESS',choices=['/heat']),
      dict(id='R02',temperature=23,status='SUCCESS',choices=['/cool']),
      dict(id='R03',temperature=21,flip=True,status='SUCCESS',choices=['/heat','/cool']),
      dict(id='R04',temperature=22,status='SUCCESS',choices=[]),
      dict(id='R05',temperature=21,ready=False,status='NO_ELIGIBLE',choices=[]),
      dict(id='R06',temperature=21,mode='unknown',status='UNKNOWN_CONTEXT',choices=[]),
      dict(id='R07',temperature=21,mode='stale',status='UNKNOWN_CONTEXT',choices=[]),
      dict(id='R08',temperature=21,conflict=True,status='CONFLICT',choices=['/heat']),
      dict(id='R09',temperature=21,mode='timeout',status='UNCERTAIN_MUTATION',choices=['/heat']),
      dict(id='R10',temperature=21,mode='wrong',status='POSTCONDITION_FAILED',choices=['/heat']),
      dict(id='R11',temperature=21,mode='frame',status='POSTCONDITION_FAILED',choices=['/heat'])]


def episode(case,policy,out):
    from semantic_action.supervision import supervise,settle_and_capture
    out=Path(out);out.mkdir(parents=True,exist_ok=False);public=out/'worker';public.mkdir()
    state=Room(case['temperature'],case.get('ready',True),case.get('ready',True),case.get('mode','normal'))
    before=state.snapshot();assert before['revision']==before['mutations']==before['requests']==0 and before['pending_requests']==0
    assert before['sentinels']=={'lamp':'off','marker':{'untouched':True}}
    dump(out/'reset.json',dict(passed=True,native=before))
    stop=Event();handled=set();clock=time.monotonic()
    review=json.loads((DATA/'review.json').read_text());catalog=load(DATA/'room.ttl',review['graph_sha256'])
    dump(out/'admission.json',dict(admitted=True,graph_hash=catalog.graph_hash,review=review,artifact=asdict(catalog.artifact)))
    with serve(state) as origin:
        config=dict(policy=policy,origin=origin,graph=str(DATA/'room.ttl'),approved_hash=review['graph_sha256'],goal=asdict(StateGoal(ROOM,22)))
        dump(public/'input.json',config)
        def synchronize():
            while not stop.is_set():
                for stage in ('intent','authorized'):
                    for i in range(1,7):
                        key=(stage,i)
                        if (public/f'{stage}-{i}.json').exists() and key not in handled:
                            # Neither condition reads the chosen handle or expected answer.
                            if (stage=='intent' and case.get('flip') or stage=='authorized' and case.get('conflict')) and not any(e['kind']=='external' for e in state.journal):state.intervene()
                            (public/f'release-{stage}-{i}').touch();handled.add(key)
                stop.wait(.003)
        thread=Thread(target=synchronize,daemon=True);thread.start()
        try:process=supervise([sys.executable,'-m','experiments.aat','worker',str(public/'input.json')],out,60,cwd=ROOT)
        finally:stop.set();thread.join(timeout=2)
        recovery=settle_and_capture(state,state.snapshot,maximum_wait_seconds=1.5)
        after=state.snapshot();native=score(before,after,state.journal,22)
        result=json.loads((public/'result.json').read_text()) if (public/'result.json').exists() else {}
        choices=[e['operation_path'] for e in result.get('transcript',[]) if e['proposal']['tool']=='use']
        expected_goal=case['id'] in {'R01','R02','R03','R04','R09','R11'}
        expected_mutations=0 if case['id'] in {'R04','R05','R06','R07','R08'} else 1
        expected_faults=1 if case['id'] in {'R10','R11'} else 0
        selection_correct=choices==case['choices']
        accepted=bool(result.get('verified') and native['native_success'])
        passed=bool(process['status']=='COMPLETED' and result.get('status')==case['status'] and selection_correct
          and native['goal_state']==expected_goal and native['mutations']==expected_mutations
          and native['unauthorized_mutations']==0 and native['incorrect_native_transitions']==expected_faults
          and accepted==(case['status']=='SUCCESS') and not recovery['state_uncertain'])
        row=dict(case=case['id'],policy=policy,status=result.get('status'),choices=choices,selection_correct=selection_correct,
            passed=passed,native=native,accepted=accepted,agent_claimed_success=bool(result.get('verified')),
            false_success=bool(result.get('verified') and not native['native_success']),before=before,after=after,
            journal=state.journal,recovery=recovery,process=process,expected=dict(case=case,goal_state=expected_goal,mutations=expected_mutations,faults=expected_faults),
            worker_seconds=process['automated_runtime_seconds'])
        dump(out/'evaluation.json',row)
    row['whole_seconds']=time.monotonic()-clock;dump(out/'evaluation.json',row);return row


def admission_controls(out):
    from rdflib import Graph, Literal, RDF
    review=json.loads((DATA/'review.json').read_text());result=[]
    for name in ('invalid','unreviewed','hash_mismatch'):
        g=Graph().parse(DATA/'room.ttl',format='turtle');u=next(g.subjects(RDF.type,AA.Usage))
        if name=='invalid':g.remove((next(g.objects(u,AA.hasPostcond)),AA.delta,None))
        if name=='unreviewed':g.set((u,AA.reviewed,Literal(False)))
        p=out/f'{name}.ttl';g.serialize(destination=p,format='turtle')
        # Matching test hash isolates shape/review checks; it is not a real admission approval.
        approved=hashlib.sha256(p.read_bytes()).hexdigest() if name!='hash_mismatch' else '0'*64
        try:load(p,approved);entry=dict(control=name,rejected=False,reason=None)
        except ValueError as e:entry=dict(control=name,rejected=True,reason=str(e))
        result.append(entry)
    dump(out/'admission-controls.json',result);return result


def summarize(output):
    raw=output/'raw'
    for n,h in json.loads((raw/'sha256.json').read_text()).items():
        if hashlib.sha256((raw/n).read_bytes()).hexdigest()!=h:raise ValueError('Raw hash mismatch: '+n)
    rows=json.loads((raw/'inventory.json').read_text());derived=output/'derived';derived.mkdir(exist_ok=True)
    table=[dict(case=r['case'],policy=r['policy'],status=r['status'],choices=r['choices'],selection_correct=r['selection_correct'],
       native_goal=r['native']['goal_state'],accepted=r['accepted'],mutations=r['native']['mutations'],requests=r['native']['requests'],
       unsafe_mutations=r['native']['unauthorized_mutations'],incorrect_native_effects=r['native']['incorrect_native_transitions'],
       false_success=r['false_success'],passed=r['passed'],worker_seconds=r['worker_seconds'],whole_seconds=r['whole_seconds']) for r in rows]
    dump(derived/'results.json',table)
    if table:
        with (derived/'results.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
        columns=('case','policy','status','choices','native_goal','accepted','mutations','passed')
        text=['# Agentic AAT results','','| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
        text+=['| '+' | '.join(str(r[k]) for k in columns)+' |' for r in table];(derived/'table.md').write_text('\n'.join(text)+'\n')
    parity=[]
    for c in cases():
        group=[r for r in table if r['case']==c['id']]
        if len(group)!=2 or len({tuple(str(r[k]) for k in ('status','choices','native_goal','accepted','mutations','requests','unsafe_mutations','incorrect_native_effects')) for r in group})!=1:parity.append(c['id'])
    source_stable=not json.loads((raw/'source-stability.json').read_text())['changed']
    controls=json.loads((raw/'admission-controls.json').read_text())
    good=len(rows)==22 and all(r['passed'] for r in rows) and all(c['rejected'] for c in controls) and not parity and source_stable
    summary=dict(verdict='PASS' if good else 'FAIL',episodes=len(rows),diagnostic_passes=sum(r['passed'] for r in rows),
      accepted_satisfactions=sum(r['accepted'] for r in rows),false_success_claims=sum(r['false_success'] for r in rows),
      unauthorized_mutations=sum(r['native']['unauthorized_mutations'] for r in rows),injected_incorrect_effects=sum(r['native']['incorrect_native_transitions'] for r in rows),
      parity_differences=parity,admission_controls=controls,source_stable=source_stable,controller_conditions=2,
      independently_authored_agents=0,external_api_generalization=False,model_backed_reasoning_evaluated=False)
    dump(derived/'summary.json',summary);print(json.dumps(summary,indent=2));return 0 if good else 1


def run(output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False);raw=output/'raw';raw.mkdir();rows=[]
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    # Include package/tests even for an explicitly recorded dirty development run.
    paths=sorted(set(n for n in paths if n)|{str(p.relative_to(ROOT)) for area in (ROOT/'experiments/aat',ROOT/'tests/aat') for p in area.rglob('*') if p.is_file() and '__pycache__' not in str(p)})
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in paths}
    from importlib.metadata import version
    dump(raw/'source.json',dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        working_tree=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),hashes=hashes,python=sys.version,
        dependencies={n:version(n) for n in ('rdflib','jsonschema','pyparsing')},order='serial R01..R11; semantic then procedural',repetitions=1))
    shutil.copytree(DATA,raw/'graphs');status='incomplete';clock=time.monotonic()
    try:
        admission_controls(raw)
        for case in cases():
            for policy in ('semantic','procedural'):
                try:r=episode(case,policy,raw/'episodes'/f'e{len(rows)+1:03d}')
                except Exception as e:
                    dump(raw/'harness-error.json',dict(case=case['id'],policy=policy,error=f'{type(e).__name__}: {e}'));raise
                rows.append(r);dump(raw/'inventory.json',rows)
        status='completed'
    finally:
        dump(raw/'cases.json',cases());dump(raw/'inventory.json',rows)
        dump(raw/'run-status.json',dict(status=status,elapsed_seconds=time.monotonic()-clock))
        dump(raw/'source-stability.json',dict(changed=[n for n,h in hashes.items() if not (ROOT/n).exists() or hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]))
        dump(raw/'sha256.json',{str(p.relative_to(raw)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='sha256.json'})
    return summarize(output)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['run','summarize']);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    return run(a.output) if a.command=='run' else summarize(a.output)
