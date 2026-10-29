"""Evaluation-only subprocess/barrier helper, never loaded by the shared worker."""
from dataclasses import asdict
import json
from pathlib import Path
import sys
from threading import Thread,Event
from .profile import sha
from .runtime import save
from semantic_action.supervision import supervise


def worker(graphs,origins,goal,out,intervene=None,stage='intent',irrelevant=False,knowledge=None,reverse=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);public=out/'worker';public.mkdir()
    approvals=[dict(path=str(Path(p).resolve()),approved_hash=sha(p)) for p in graphs]
    save(out/'approvals.json',dict(scope='Task-authorized same-author controlled experiment; not independent human review',graphs=approvals))
    config=dict(graphs=approvals,origins=origins,goal=asdict(goal),irrelevant_first=irrelevant,knowledge=knowledge,reverse_registration=reverse)
    save(public/'input.json',config);stop=Event();handled=set();intervened=[]
    def sync():
        while not stop.is_set():
            for s in ('intent','authorized'):
                for i in range(1,7):
                    if (public/f'{s}-{i}.json').exists() and (s,i) not in handled:
                        if s==stage and intervene and not intervened:intervene();intervened.append(True)
                        (public/f'release-{s}-{i}').touch();handled.add((s,i))
            stop.wait(.003)
    thread=Thread(target=sync,daemon=True);thread.start()
    try:process=supervise([sys.executable,'-m','experiments.aat_reusable.worker',str(public/'input.json')],out,60,cwd=Path.cwd())
    finally:stop.set();thread.join(timeout=2)
    result=json.loads((public/'result.json').read_text()) if (public/'result.json').exists() else {}
    save(out/'process-summary.json',process);return result,process
