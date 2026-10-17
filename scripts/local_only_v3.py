"""Verify API-local chains from the installed project without semantic dependencies."""
import argparse
import importlib.util
import importlib.metadata
import json
from pathlib import Path
from semantic_action.multistep_evaluation import run_pilot
from semantic_action.multistep_tasks import pilot_tasks

parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=False)
assert importlib.util.find_spec('rdflib') is None
assert importlib.util.find_spec('jsonschema') is None
results = [run_pilot(pilot_tasks()[0], p, 'A', output / p, root) for p in ('a', 'b')]
assert all(r['summary']['verified'] for r in results)
report = {'rdflib_present': False, 'jsonschema_present': False,
          'providers_verified': ['a', 'b'], 'condition': 'A',
          'installed_distributions': [{'name': d.metadata['Name'], 'version': d.version}
                                      for d in importlib.metadata.distributions()]}
(output / 'environment.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
