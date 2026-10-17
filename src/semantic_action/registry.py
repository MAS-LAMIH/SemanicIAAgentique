"""Finite capability discovery and resolution, with no provider substitution table."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from .contract import load_contract
from .model import Truth, now
from .pipeline import Executor, validate_inputs
from .provider_contract import CAPABILITY, EFFECT
from .transform import validate_profile


@dataclass(frozen=True)
class Registration:
    manual: Path
    origin: str


class Registry:
    def __init__(self, registrations):
        self.registrations = tuple(registrations)

    def resolve(self, goal, required_capability=CAPABILITY, inputs=None):
        values = ({key:getattr(goal,key) for key in ('start_time','end_time','title')}
                  if inputs is None else inputs)
        trace = {'schema_version':1,'run_id':str(uuid4()),'timestamp':now(),
                 'formal_goal':goal.to_dict(),'required_capability':required_capability,
                 'inputs':values,'candidates':[]}
        operations = set()
        for index, registration in enumerate(self.registrations):
            candidate = {'registration':index,'operation_id':None,'artifact_id':None,
                         'compatible':False,'eligible':False,'applicability':Truth.UNKNOWN,
                         'reasons':[],'assessment':None,'contract_sha256':None}
            trace['candidates'].append(candidate)
            try:
                path = Path(registration.manual)
                candidate['contract_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                contract = load_contract(path)
                candidate.update(operation_id=contract.operation_id,artifact_id=contract.artifact_id)
                if contract.operation_id in operations:
                    raise ValueError('Ambiguous duplicate operation registration')
                operations.add(contract.operation_id)
                if contract.profile is None:
                    candidate['reasons'].append('Explicit shared-semantics v2 mapping required')
                if contract.capability_id != required_capability:
                    candidate['reasons'].append('Declared capability does not match required capability')
                if EFFECT not in contract.declared_effects:
                    candidate['reasons'].append('Modeled effects do not establish required goal effect')
                validation = validate_inputs(values,contract.inputs)
                if validation.valid:
                    validation = validate_profile(contract,values,goal)
                candidate['reasons'].extend(validation.errors)
                if candidate['reasons']:
                    continue
                candidate['compatible'] = True
                executor = Executor(registration.origin)
                assessment = executor.assess(path,values,goal)
                candidate['assessment'] = assessment
                candidate['applicability'] = assessment['applicability']
                candidate['eligible'] = assessment['applicability'] == Truth.TRUE
                if not candidate['eligible']:
                    candidate['reasons'].append('Critical applicability is '+assessment['applicability'])
            except (ValueError,TypeError,OSError) as error:
                candidate['reasons'].append(str(error))
        # Duplicate declarations invalidate every matching candidate, not just the latter.
        ids = [c['operation_id'] for c in trace['candidates']]
        for candidate in trace['candidates']:
            if candidate['operation_id'] and ids.count(candidate['operation_id']) > 1:
                candidate.update(compatible=False,eligible=False)
                candidate['reasons'].append('Ambiguous duplicate operation registration')
        return trace

    def execute(self, goal, operation_id, output_dir, required_capability=CAPABILITY, inputs=None):
        output = Path(output_dir)
        output.mkdir(parents=True,exist_ok=True)
        resolution = self.resolve(goal,required_capability,inputs)
        resolution['selected_operation'] = operation_id
        candidates = [c for c in resolution['candidates'] if c['operation_id'] == operation_id and c['eligible']]
        resolution['execution_started'] = False
        action = None
        try:
            if len(candidates) == 1:
                selected = candidates[0]
                registration = self.registrations[selected['registration']]
                if hashlib.sha256(Path(registration.manual).read_bytes()).hexdigest() != selected['contract_sha256']:
                    raise ValueError('Manual changed after resolution')
                resolution['execution_started'] = True
                action = Executor(registration.origin).run(registration.manual,goal,resolution['inputs'],output/'action.json')
            else:
                resolution['rejection_reason'] = 'Selected operation is not uniquely eligible'
            return {'resolution':resolution,'action':action}
        finally:
            with (output/'resolution.json').open('x',encoding='utf-8') as stream:
                json.dump(resolution,stream,indent=2,sort_keys=True)
                stream.write('\n')
