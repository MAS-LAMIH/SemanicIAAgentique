"""Worker loads no fixture/scorer modules; parent study owns private native state."""
import sys
if sys.argv[1:2]==['worker']:
    import json
    from pathlib import Path
    from .rdf import load
    from .model import StateGoal
    from .runtime import Runtime, dump
    config=json.loads(Path(sys.argv[2]).read_text())
    catalog=load(config['graph'],config['approved_hash'])
    runtime=Runtime(catalog,config['origin'],config['policy'],StateGoal(**config['goal']),Path(sys.argv[2]).parent)
    runtime.run()
    dump(runtime.output/'modules.json',sorted(sys.modules))
else:
    from .study import main
    raise SystemExit(main())
