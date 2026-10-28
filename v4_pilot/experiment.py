"""Repeatable visible-provider execution study, using the retained pilot harness."""
import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
from time import monotonic

from .driver import ROOT, run_attempt, save
from .tasks import catalogue
from .summarize import normalized


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def static_metrics():
    groups = {
        'shared_v4_runtime': list((ROOT/'src/semantic_capability_v4').glob('*.py')),
        'shared_baseline_glue': [ROOT/'src/api_local_v4/common.py', ROOT/'src/api_local_v4/__init__.py'],
        'shared_vocabulary': [ROOT/'v4/vocabulary.json'],
        'evaluation_infrastructure': list((ROOT/'v4_pilot').glob('*.py')),
        'shared_native_fixtures': [ROOT/f'src/semantic_action/{n}.py' for n in ('artifact','provider_b','model','supervision')],
    }
    for provider in 'ab':
        groups[f'A_adapter_{provider}'] = [ROOT/f'src/api_local_v4/{provider}.py']
        for condition, suffix in [('B','json'),('C','ttl')]:
            groups[f'{condition}_description_{provider}'] = [ROOT/f'v4/descriptions/{provider}.{suffix}']
    return [dict(category=g, file=str(p.relative_to(ROOT)), physical_lines=len(p.read_text().splitlines()),
                 bytes=p.stat().st_size, sha256=digest(p)) for g, files in groups.items() for p in sorted(files)]


def run(output, repetitions, task_ids):
    if repetitions < 1: raise ValueError('repetitions must be positive')
    tasks = [t for t in catalogue() if t['task_id'] in task_ids]
    if len(tasks) != len(task_ids) or not tasks: raise ValueError('Unknown, duplicate or empty task selection')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw = output/'raw'; raw.mkdir()
    metrics = static_metrics()
    files = {r['file']:r['sha256'] for r in metrics}
    files['v4_pilot/tasks.py'] = digest(ROOT/'v4_pilot/tasks.py')
    revision = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True)
    from importlib.metadata import version
    from semantic_capability_v4.descriptions import load
    parity = {}
    for p in 'ab':
        left, right = [load(ROOT/f'v4/descriptions/{p}.{s}') for s in ('json','ttl')]
        if left != right: raise ValueError('Frontend description mismatch')
        parity[p] = asdict(left)
    planned = repetitions*len(tasks)*6
    save(raw/'manifest.json', dict(schema_version=1, source_revision=revision, source_dirty=bool(dirty),
         source_status=dirty, files=files, python=platform.python_version(), platform=platform.platform(),
         dependencies={n:version(n) for n in ('rdflib','pyparsing')}, repetitions=repetitions,
         task_ids=[t['task_id'] for t in tasks], providers=['a','b'], conditions=list('ABC'),
         planned_attempts=planned, planned_reset_controls=repetitions*6,
         ordering='serial; catalogue order; left-rotate ABC by (repetition-1 + provider_index) modulo 3',
         seed=None, independent_provider_units=2, independent_integrations_measured=0,
         confirmatory=False, human_active_seconds=None, supervision_seconds=None,
         integration_effort_seconds=None, task_catalogue_sha256=hashlib.sha256(json.dumps(tasks,sort_keys=True).encode()).hexdigest(),
         started_at=datetime.now(timezone.utc).isoformat()))
    save(raw/'catalogue.json',tasks); save(raw/'frontend-parity.json',parity);save(raw/'static-metrics.json',metrics)
    rows, controls = [], []; clock=monotonic(); status='interrupted'
    try:
        for rep in range(1,repetitions+1):
            for task in tasks:
                for pi,p in enumerate('ab'):
                    offset=(rep-1+pi)%3; order='ABC'[offset:]+'ABC'[:offset]
                    for c in order:
                        path=raw/'attempts'/f'r{rep:03d}-{task["task_id"]}-{p}-{c}'
                        try: result=run_attempt(task,p,c,path)
                        except Exception as exc:
                            result=dict(task_id=task['task_id'],provider=p,condition=c,diagnostic_passed=False,
                                        harness_error=f'{type(exc).__name__}: {exc}')
                        rows.append(dict(path=str(path.relative_to(raw)),repetition=rep,**result))
                        save(raw/'attempt-inventory.json',rows)
            for p in 'ab':
                for c in 'ABC':
                    path=raw/'reset-controls'/f'r{rep:03d}-{p}-{c}'
                    try: result=run_attempt(catalogue()[0],p,c,path,contamination='calls')
                    except Exception as exc: result=dict(status='HARNESS_ERROR',harness_error=str(exc))
                    controls.append({**result, 'repetition':rep, 'provider':p, 'condition':c, 'path':str(path.relative_to(raw))})
                    save(raw/'reset-controls.json',controls)
        status='completed'
    finally:
        changed=[n for n,h in files.items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h]
        save(raw/'run-status.json',dict(status=status,automated_elapsed_seconds=monotonic()-clock,
             executed=len(rows),source_changed_during_run=changed,ended_at=datetime.now(timezone.utc).isoformat()))
        save(raw/'evidence-sha256.json',{str(p.relative_to(raw)):digest(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='evidence-sha256.json'})
    return summarize(output)


def write_csv(path, rows):
    if not rows: return
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def summarize(output):
    raw=output/'raw'
    for name,h in json.loads((raw/'evidence-sha256.json').read_text()).items():
        if digest(raw/name)!=h: raise ValueError('Evidence hash mismatch: '+name)
    manifest=json.loads((raw/'manifest.json').read_text())
    rows=json.loads((raw/'attempt-inventory.json').read_text()) if (raw/'attempt-inventory.json').exists() else []
    controls=json.loads((raw/'reset-controls.json').read_text()) if (raw/'reset-controls.json').exists() else []
    status=json.loads((raw/'run-status.json').read_text());groups=defaultdict(list);flat=[]
    for r in rows:
        groups[r['provider'],r['condition']].append(r)
        s=r.get('summary',{});p=r.get('process',{});n=r.get('native',{})
        flat.append(dict(provider=r['provider'],condition=r['condition'],task_id=r['task_id'],repetition=r['repetition'],
          diagnostic_passed=r['diagnostic_passed'],classification=s.get('classification','harness_error'),
          error_kind=s.get('error_kind'),http_status=s.get('http_status'),native_correct=n.get('native_state_correct'),
          unexpected_mutations=n.get('unexpected_mutations'),post_attempts=n.get('post_attempts'),
          worker_seconds=p.get('automated_runtime_seconds'),attempt_seconds=r.get('duration_seconds'),
          timeout=p.get('status')=='TIMEOUT',uncertain_at_stop=r.get('uncertain_remote_outcome_at_stop'),
          unsettled=r.get('state_uncertain_after_observation'),creation_accepted=r.get('creation_accepted'),
          source_revision=manifest['source_revision'],harness_error=r.get('harness_error')))
    correctness=[];timings=[];errors=[]
    for (p,c),g in sorted(groups.items()):
        correctness.append(dict(provider=p,condition=c,attempts=len(g),diagnostic_passed=sum(r['diagnostic_passed'] for r in g),
          successful_creations=sum(r.get('creation_accepted',False) for r in g),
          native_state_correct=sum(r.get('native',{}).get('native_state_correct',False) for r in g),
          unexpected_mutations=sum(r.get('native',{}).get('unexpected_mutations',False) for r in g)))
        for scope,key in [('worker','worker_seconds'),('whole_attempt','attempt_seconds')]:
            for classification in sorted({r['classification'] for r in flat if r['provider']==p and r['condition']==c}):
                times=sorted(r[key] for r in flat if r['provider']==p and r['condition']==c and r['classification']==classification and r[key] is not None)
                if times: timings.append(dict(provider=p,condition=c,classification=classification,scope=scope,n=len(times),
                  min_seconds=min(times),median_seconds=statistics.median(times),mean_seconds=statistics.mean(times),
                  p95_seconds=times[max(0,__import__('math').ceil(.95*len(times))-1)],max_seconds=max(times)))
        for classification,count in sorted(Counter(r.get('summary',{}).get('classification','harness_error') for r in g).items()):
            errors.append(dict(provider=p,condition=c,classification=classification,count=count))
    differences=[]
    for rep in range(1,manifest['repetitions']+1):
        for task in manifest['task_ids']:
            for p in manifest['providers']:
                g=[r for r in rows if (r['repetition'],r['task_id'],r['provider'])==(rep,task,p)]
                if len(g)!=3 or {r['condition'] for r in g}!=set('ABC') or any('harness_error' in r for r in g):
                    differences.append([rep,task,p,'missing/error']);continue
                values=[normalized(r,raw/r['path']) for r in g]
                if any(v!=values[0] for v in values[1:]):differences.append([rep,task,p,'semantic difference'])
    good=(status['status']=='completed' and not status['source_changed_during_run'] and len(rows)==manifest['planned_attempts']
          and all(r['diagnostic_passed'] for r in rows) and not differences
          and len(controls)==manifest['planned_reset_controls'] and all(r['status']=='RESET_REJECTED' and not r['subject_launched'] for r in controls))
    derived=output/'derived';derived.mkdir(exist_ok=True)
    summary=dict(verdict='PASS' if good else 'FAIL',executed=len(rows),planned=manifest['planned_attempts'],
      parity_differences=differences,reset_controls=len(controls),run_status=status,independent_provider_units=2,
      independent_integrations_measured=0,confirmatory=False,integration_effort_seconds=None)
    save(derived/'summary.json',summary)
    tables={'attempts':flat,'correctness':correctness,'error_handling':errors,'execution_times':timings,
            'artifact_size':json.loads((raw/'static-metrics.json').read_text())}
    for name,table in tables.items():save(derived/f'{name}.json',table);write_csv(derived/f'{name}.csv',table)
    text=['# Visible-provider runtime results','',f"Diagnostic verdict: {summary['verdict']}. Independent providers: 2; measured integrations: 0.",'']
    for name in ('correctness','error_handling','execution_times','artifact_size'):
        table=tables[name];text.extend([f'## {name}',''])
        if table:
            keys=list(table[0]);text+=['| '+' | '.join(keys)+' |','| '+' | '.join(['---']*len(keys))+' |']
            text+=['| '+' | '.join(str(r[k]) for k in keys)+' |' for r in table]
        text.append('')
    (derived/'tables.md').write_text('\n'.join(text))
    print(json.dumps(summary,indent=2));return 0 if good else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    execute=sub.add_parser('run');execute.add_argument('--output',type=Path,required=True)
    execute.add_argument('--repetitions',type=int,default=1);execute.add_argument('--tasks',nargs='+',default=[t['task_id'] for t in catalogue()])
    report=sub.add_parser('summarize');report.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    return run(args.output,args.repetitions,args.tasks) if args.command=='run' else summarize(args.output)


if __name__=='__main__':raise SystemExit(main())
