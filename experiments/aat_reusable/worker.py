"""Frozen worker: no native fixtures, case schedules or scorer imports."""
import importlib
from dataclasses import asdict,replace
import json
from pathlib import Path
import sys
from .profile import load,Goal,Condition,sha
from .runtime import Runtime,IrrelevantFirst,save

def main():
    config=json.loads(Path(sys.argv[1]).read_text());catalogs=[load(g['path'],g['approved_hash']) for g in config['graphs']]
    if config.get('reverse_registration'):
        catalogs=[replace(c,slots=tuple(reversed(c.slots)),operations=tuple(reversed(c.operations)),usages=tuple(reversed(c.usages))) for c in reversed(catalogs)]
    goal=Goal(config['goal']['thing'],tuple(Condition(**c) for c in config['goal']['clauses']),config['goal'].get('max_age',10))
    matched=[c for c in catalogs if c.thing==goal.thing]
    if len(matched)!=1:raise ValueError('Ambiguous/missing goal grounding')
    cat=matched[0];knowledge=None
    if config.get('knowledge'):
        spec=config['knowledge']
        if not spec['module'].startswith('experiments.aat_reusable.'):raise ValueError('Unapproved local knowledge namespace')
        module=importlib.import_module(spec['module'])
        if sha(module.__file__)!=spec['sha256']:raise ValueError('Knowledge code hash')
        knowledge=getattr(module,spec.get('function','assess'))
    runtime=Runtime(cat,config['origins'][cat.artifact],goal,Path(sys.argv[1]).parent,knowledge)
    save(runtime.out/'discovery.json',[asdict(c) for c in catalogs])
    runtime.run(IrrelevantFirst() if config.get('irrelevant_first') else None)
    save(runtime.out/'modules.json',{name:str(Path(m.__file__).resolve()) for name,m in sys.modules.items() if getattr(m,'__file__',None) and Path(m.__file__).is_file()})
if __name__=='__main__':main()
