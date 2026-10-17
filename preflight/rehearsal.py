"""Complete public A/B catalogue, one repetition; never held-out evidence."""
import argparse
import json
from pathlib import Path
from semantic_action.evaluation import run_case
from semantic_action.evaluation_tasks import proposed_tasks
from semantic_action.multistep_tasks import pilot_tasks
from .driver import run, ROOT, save

AREA=ROOT/'docs/artifacts/milestone4_5'
def main():
    p=argparse.ArgumentParser(); p.add_argument('--phase',choices=['rehearsal','reference'],required=True); p.add_argument('--output',type=Path,default=AREA)
    a=p.parse_args()
    if a.phase=='rehearsal':
        focus=json.loads((AREA/'focused.json').read_text())
        if focus['exit_code']!=0: raise RuntimeError('Focused safety gate failed; stop')
    rows=[]
    tasks=proposed_tasks() if a.phase=='reference' else (*proposed_tasks(),*pilot_tasks())
    for task in tasks:
        for provider in ('a','b'):
            for condition in 'ABC':
                path=a.output/a.phase/f'{task.task_id}-{provider}-{condition}'
                result=(run_case(task,provider,condition,path,ROOT) if a.phase=='reference' else run(task,provider,condition,path))
                passed=result.get('diagnostic_passed',result.get('case_passed',False))
                row=dict(task_id=task.task_id,provider=provider,condition=condition,path=str(path),passed=passed,summary=result['summary'])
                rows.append(row); save(a.output/(a.phase+'-inventory.json'),rows)
                print(json.dumps(row),flush=True)
                if not passed: raise RuntimeError('STOP: diagnostic mismatch; preserve evidence')
    return 0
if __name__=='__main__': raise SystemExit(main())
