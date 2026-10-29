"""Controlled manual/acquired RDF comparison through the unchanged AAT worker."""
import argparse
from copy import deepcopy
import csv
from dataclasses import asdict
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Event,Thread
import time
from .acquisition import acquire
from .completion import complete,admit,sha,save
from .model import StateGoal,ROOM
from .native import Room,serve,score
from .study import cases,ROOT,DATA
from semantic_action.supervision import supervise,settle_and_capture


def prepare(origin,out,fault=None):
    """Only bind provenance hashes to an already authored behavioral template."""
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    config=json.loads((DATA/'acquisition/room.config.json').read_text());config['origin']=origin
    save(out/'config.json',config);report=acquire(DATA/'acquisition/room.json',config,out/'extracted')
    if report['status']!='QUARANTINED':raise ValueError('Structural extraction failed')
    sc=json.loads((DATA/'room-completion.template.json').read_text())
    if sc['source_sha256']!=sha(out/'extracted/source.json') or sc['native_source_sha256']!=sha(Path(__file__).parent/'native.py'):raise ValueError('Review template source changed')
    sc['structural_sha256']=sha(out/'extracted/structural.ttl');sc['provenance_sha256']=sha(out/'extracted/provenance.json')
    if fault=='unknown':sc['review']['status']='pending';sc['usages'][0]['post']['delta']=None
    if fault=='unsupported':sc['usages'][0]['post']['delta']=2
    if fault=='wrong-supported':
        for u in sc['usages']:u['post']['delta']=-u['post']['delta']
        sc['review']['scope']+='; DELIBERATE faulty-review control, not asserted correct behavior'
    save(out/'sidecar.json',sc);record=complete(out/'extracted',out/'sidecar.json',out/'completed')
    if record['status']!='COMPLETED_UNAPPROVED':return None,record
    # Explicit experiment-author approval of this complete graph + completion/input review hashes.
    # This is NOT an independent human signature or investigator freeze approval.
    approval=dict(approved=True,reviewer='Task-authorized experimental operator (Codex)',scope=sc['review']['scope'],
                  graph_sha256=record['graph_sha256'],completion_sha256=sha(out/'completed/completion.json'))
    save(out/'approval.json',approval);catalog,decision=admit(out/'completed',out/'approval.json')
    if decision['origin']!=origin:raise ValueError('Deployment origin mismatch')
    save(out/'admission.json',decision)
    return out/'completed/candidate.ttl',decision


def episode(case,representation,out,fault=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);worker=out/'worker';worker.mkdir()
    state=Room(case['temperature']);before=state.snapshot();clock=time.monotonic()
    assert before['revision']==before['mutations']==before['requests']==before['pending_requests']==0
    assert before['sentinels']=={'lamp':'off','marker':{'untouched':True}}
    save(out/'reset.json',dict(passed=True,native=before))
    with serve(state) as origin:
        if representation=='manual':
            shutil.copyfile(DATA/'room.ttl',out/'manual.ttl');shutil.copyfile(DATA/'review.json',out/'manual-review.json')
            graph=out/'manual.ttl';approval=json.loads((DATA/'review.json').read_text())['graph_sha256']
            from .rdf import load
            load(graph,approval);save(out/'admission.json',dict(admitted=True,graph_sha256=approval,source='original reviewed graph'))
        else:
            graph,decision=prepare(origin,out/'pipeline',fault)
            if graph is None:
                after=state.snapshot();row=dict(case=case['id'],representation=representation,fault=fault,status='QUARANTINED',choices=[],accepted=False,
                  worker_launched=False,requests=0,before=before,after=after,journal=[],passed=before==after and decision['status']=='QUARANTINED',decision=decision)
                save(out/'evaluation.json',row);return row
            approval=decision['graph_sha256']
        save(worker/'input.json',dict(policy='semantic',origin=origin,graph=str(graph.resolve()),approved_hash=approval,goal=asdict(StateGoal(ROOM,22))))
        stop=Event();handled=set()
        def sync():
            while not stop.is_set():
                for stage in ('intent','authorized'):
                    for turn in range(1,7):
                        key=(stage,turn)
                        if (worker/f'{stage}-{turn}.json').exists() and key not in handled:
                            # Schedule depends only on barrier stage, never proposed identity.
                            if stage=='intent' and case.get('flip') and not any(e['kind']=='external' for e in state.journal):state.intervene()
                            (worker/f'release-{stage}-{turn}').touch();handled.add(key)
                stop.wait(.003)
        thread=Thread(target=sync,daemon=True);thread.start()
        try:process=supervise([sys.executable,'-m','experiments.aat','worker',str(worker/'input.json')],out,60,cwd=ROOT)
        finally:stop.set();thread.join(timeout=2)
        recovery=settle_and_capture(state,state.snapshot,maximum_wait_seconds=1.5)
        after=state.snapshot();native=score(before,after,state.journal,22)
        result=json.loads((worker/'result.json').read_text()) if (worker/'result.json').exists() else {}
        choices=[e['operation_path'] for e in result.get('transcript',[]) if e['proposal']['tool']=='use']
        guards=[e['guard']['code'] for e in result.get('transcript',[]) if 'guard' in e]
        accepted=bool(result.get('verified') and native['native_success'])
        if fault=='wrong-supported':passed=result.get('status')=='POSTCONDITION_FAILED' and not accepted and not result.get('verified') and after['temperature']==20 and native['mutations']==1
        else:passed=result.get('status')=='SUCCESS' and accepted and choices==case['choices']
        passed=bool(passed and process['status']=='COMPLETED' and native['unauthorized_mutations']==native['incorrect_native_transitions']==0 and not recovery['state_uncertain'])
        row=dict(case=case['id'],representation=representation,fault=fault,status=result.get('status'),choices=choices,guards=guards,accepted=accepted,
          native=native,before=before,after=after,journal=state.journal,process=process,recovery=recovery,worker_launched=True,
          false_success=bool(result.get('verified') and not native['native_success']),passed=passed)
    row['whole_seconds']=time.monotonic()-clock;save(out/'evaluation.json',row);return row


def normalized(row):
    return dict(status=row['status'],choices=row['choices'],guards=row['guards'],accepted=row['accepted'],native=row['native'],after=row['after'],
                journal=[dict(kind=e['kind'],path=e.get('path'),status=e.get('status'),before=e['before'],after=e['after']) for e in row['journal']])


def run(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);raw=output/'raw';raw.mkdir();rows=[]
    paths=sorted(set(subprocess.check_output(['git','ls-files'],text=True).splitlines()))
    hashes={p:sha(p) for p in paths}
    save(raw/'source.json',dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),working_tree=subprocess.check_output(['git','status','--porcelain'],text=True),
         hashes=hashes,python=sys.version,dependencies={n:version(n) for n in ('rdflib','pyparsing')},order='R01..R04 manual then acquired; unknown, unsupported and wrong-supported controls',
         human_active_minutes=None,supervision_minutes=None))
    shutil.copyfile(Path(__file__).parent/'native.py',raw/'native-spec.py');shutil.copyfile(DATA/'room-completion.template.json',raw/'reviewed-template.json')
    status='incomplete';clock=time.monotonic()
    try:
        for case in cases()[:4]:
            for rep in ('manual','acquired'):
                rows.append(episode(case,rep,raw/'episodes'/f'e{len(rows)+1:03d}'));save(raw/'inventory.json',rows)
        for fault in ('unknown','unsupported','wrong-supported'):
            case=dict(id='control-'+fault,temperature=21)
            rows.append(episode(case,'acquired',raw/'episodes'/f'e{len(rows)+1:03d}',fault));save(raw/'inventory.json',rows)
        status='completed'
    except Exception as error:
        save(raw/'error.json',dict(error=f'{type(error).__name__}: {error}'));raise
    finally:
        save(raw/'inventory.json',rows);save(raw/'run-status.json',dict(status=status,elapsed_seconds=time.monotonic()-clock))
        save(raw/'source-stability.json',dict(changed=[p for p,h in hashes.items() if sha(p)!=h]))
        save(raw/'sha256.json',{str(p.relative_to(raw)):sha(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='sha256.json'})
    return summarize(output)


def summarize(output):
    output=Path(output);raw=output/'raw'
    for p,h in json.loads((raw/'sha256.json').read_text()).items():
        if sha(raw/p)!=h:raise ValueError('Raw evidence changed')
    rows=json.loads((raw/'inventory.json').read_text());parity=[]
    for case in cases()[:4]:
        pair=[r for r in rows if r['case']==case['id']]
        if len(pair)!=2 or normalized(pair[0])!=normalized(pair[1]):parity.append(case['id'])
    good=len(rows)==11 and all(r['passed'] for r in rows) and not parity and not json.loads((raw/'source-stability.json').read_text())['changed']
    summary=dict(passed=good,attempt_records=len(rows),executed_episodes=sum(r['worker_launched'] for r in rows),quarantine_controls=sum(not r['worker_launched'] for r in rows),
                 accepted_satisfactions=sum(r['accepted'] for r in rows),parity_differences=parity,false_success_claims=sum(r.get('false_success',False) for r in rows),
                 external_generalization=False,automatic_behavior_inference=False)
    derived=output/'derived';derived.mkdir(exist_ok=True);save(derived/'summary.json',summary)
    table=[dict(case=r['case'],representation=r['representation'],status=r['status'],choices=r['choices'],accepted=r['accepted'],worker_launched=r['worker_launched'],
                mutations=r['after']['mutations'],final_temperature=r['after']['temperature'],passed=r['passed']) for r in rows]
    save(derived/'results.json',table)
    with (derived/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
    keys=list(table[0]);(derived/'table.md').write_text('| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+'\n'.join('| '+' | '.join(str(r[k]) for k in keys)+' |' for r in table)+'\n')
    print(json.dumps(summary,indent=2));return 0 if good else 1


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('run','summarize'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    return run(a.output) if a.command=='run' else summarize(a.output)


if __name__=='__main__':raise SystemExit(main())
