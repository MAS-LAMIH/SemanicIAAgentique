"""Finite follow-up bindings. Local condition never imports shared discovery.

Profiles add a dependency guard around the existing validated event mutation path.
No profile may provide evaluator expectations or executable transform code.
"""
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate sequence field')
        result[key] = value
    return result


def read_json(path):
    def reject(value):
        raise ValueError('Nonfinite sequence value ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=unique, parse_constant=reject)


def reference(root, name):
    if not isinstance(name, str) or Path(name).is_absolute():
        raise ValueError('Relative local reference required')
    root = Path(root).resolve()
    target = (root / name).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError('Unsafe or missing local reference')
    return target


def identifier(value):
    if not isinstance(value, str) or not value or not all(c.isascii() and (c.isalnum() or c in '-_') for c in value):
        raise ValueError('Invalid predecessor identifier')
    return value


@dataclass(frozen=True)
class SharedSequenceProfile:
    version: int
    operation_id: str
    effect: str
    requires_predecessor: bool
    requires_after_end: bool
    create_path_template: str
    base_contract: object


KEYS = {'version', 'operation_id', 'effect', 'requires_predecessor', 'requires_after_end',
        'create_path_template', 'base_manual'}


def load_shared(path, root):
    """Both frontends reconstruct one closed semantic record and typed v2 base."""
    from .contract import load_contract
    path = Path(path)
    if path.suffix == '.json':
        data = read_json(path)
    elif path.suffix == '.ttl':
        from rdflib import Graph, Literal, Namespace, RDF
        from rdflib.plugins.parsers.notation3 import BadSyntax
        ns = Namespace('https://example.org/sam/sequence/v1#')
        try:
            graph = Graph().parse(data=path.read_text(), format='turtle')
        except BadSyntax as error:
            raise ValueError('Malformed sequence Turtle') from error
        roots = list(graph.subjects(RDF.type, ns.Profile))
        if len(roots) != 1:
            raise ValueError('One sequence profile required')
        node = roots[0]
        seen = {(node, RDF.type, ns.Profile)}
        data = {}
        for key in KEYS:
            values = list(graph.objects(node, ns[key]))
            if len(values) != 1 or not isinstance(values[0], Literal) or values[0].language:
                raise ValueError('Missing/ambiguous sequence field ' + key)
            seen.add((node, ns[key], values[0]))
            decoded = values[0].toPython()
            if type(decoded) not in {str, int, bool}:
                raise ValueError('Unsupported sequence RDF literal')
            data[key] = decoded
        if set(graph) != seen:
            raise ValueError('Unsupported sequence assertions')
    else:
        raise ValueError('Explicit JSON/Turtle profile required')
    if not isinstance(data, dict) or set(data) != KEYS:
        raise ValueError('Incomplete/unsupported sequence profile')
    if type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Unsupported sequence version')
    if not all(type(data[k]) is bool and data[k] for k in ('requires_predecessor', 'requires_after_end')):
        raise ValueError('All follow-up dependency guards mandatory')
    if data['effect'] not in {'NewEventAfterPredecessor', 'ReservationOnly'}:
        raise ValueError('Unknown sequence effect')
    if not isinstance(data['operation_id'], str) or not data['operation_id'].startswith('urn:') or any(c.isspace() for c in data['operation_id']):
        raise ValueError('Named sequence operation required')
    template = data['create_path_template']
    import re
    if not isinstance(template, str) or not re.fullmatch(r'/[A-Za-z0-9_/-]+/\{id\}', template):
        raise ValueError('Unsafe dependent path template')
    base = load_contract(reference(root, data['base_manual']))
    if base.profile is None:
        raise ValueError('Explicit v2 base binding required')
    return SharedSequenceProfile(data['version'], data['operation_id'], data['effect'],
                                 True, True, template, base), data


class LocalSequenceBinding:
    def __init__(self, root, profile, origin):
        # Deliberately provider-local programming, no shared ontology/registry imports.
        from .local_baseline import CalendarLocal, BookingLocal
        data = read_json(profile)
        required = {'version', 'local_kind', 'operation', 'effect', 'requires_predecessor',
                    'requires_after_end', 'create_path_template', 'base_description'}
        if not isinstance(data, dict) or set(data) != required:
            raise ValueError('Incomplete local follow-up description')
        if type(data['version']) is not int or data['version'] != 1:
            raise ValueError('Unsupported local follow-up version')
        if not all(type(data[k]) is bool and data[k] for k in ('requires_predecessor', 'requires_after_end')):
            raise ValueError('Missing local dependency guard')
        if data['local_kind'] == 'calendar_followup':
            self.local_type, operation, template = CalendarLocal, 'create_followup', '/followups/{id}'
        elif data['local_kind'] == 'booking_followup':
            self.local_type, operation, template = BookingLocal, 'reserveAfterBooking', '/booking-after/{id}'
        else:
            raise ValueError('Unsupported local follow-up binding')
        if data['operation'] != operation or data['create_path_template'] != template:
            raise ValueError('Unsupported local operation/path')
        if data['effect'] not in {'stores_followup_after_existing_event', 'records_reservation_only'}:
            raise ValueError('Unknown local effect')
        self.compatible = data['effect'] == 'stores_followup_after_existing_event'
        self.base = reference(root, data['base_description'])
        self.origin, self.data = origin, data
        # Parse local base before any mutation, including dependent-only description defects.
        self.local_type(self.base)

    def read_state(self):
        from .local_baseline import LocalExecutor
        local = self.local_type(self.base)
        response = LocalExecutor(self.origin)._http_request('GET', local.permission_path)
        if not response.success:
            return None
        try:
            return local.state(response.body)
        except (KeyError, TypeError, ValueError, OverflowError):
            return None

    def execute(self, index, predecessor, goal, output):
        from .local_baseline import LocalExecutor
        local = self.local_type(self.base)
        if index:
            local.create_path = self.data['create_path_template'].replace('{id}', identifier(predecessor))
            # The local adapter still validates the single creation goal, encoding and effects.
            local.operation = self.data['operation']
            local.description['operation'] = self.data['operation']
        values = {k: getattr(goal, k) for k in ('start_time', 'end_time', 'title')}
        return LocalExecutor(self.origin).run(local, goal, values, output / 'action.json')


class SharedSequenceBinding:
    def __init__(self, root, profile, origin, output):
        self.root, self.profile_path, self.origin, self.output = Path(root), Path(profile), origin, output
        self.profile, self.data = load_shared(profile, root)
        self.compatible = self.profile.effect == 'NewEventAfterPredecessor'

    def read_state(self):
        from .pipeline import Executor
        executor = Executor(self.origin)
        executor._profile = self.profile.base_contract.profile
        response = executor._request('GET', '/calendar')
        return response.body if response.success else None

    def execute(self, index, predecessor, goal, output):
        from .provider_contract import provider_graph
        from .registry import Registry, Registration
        from .contract import load_contract
        # Materialize an explicit v2 binding from the typed base, preserving every field.
        contract = self.profile.base_contract
        profile = contract.profile
        data = {'schema_version': 2, 'artifact_id': contract.artifact_id,
                'operation_id': contract.operation_id, 'capability_id': contract.capability_id,
                'inputs': list(contract.inputs), 'preconditions': list(contract.preconditions),
                'declared_effects': list(contract.declared_effects),
                'constraints': deepcopy(profile.constraints), 'binding': deepcopy(profile.binding),
                'observation': {'max_evidence_age_seconds': contract.max_evidence_age_seconds}}
        if index:
            data['operation_id'] = self.profile.operation_id
            data['binding']['create_path'] = self.profile.create_path_template.replace('{id}', identifier(predecessor))
        suffix = self.profile_path.suffix
        manual = output / ('manual' + suffix)
        if suffix == '.json':
            manual.write_text(json.dumps(data, indent=2) + '\n')
        else:
            provider_graph(data).serialize(destination=manual, format='turtle')
        # Normal registry and Executor checks still apply, including fresh permission recheck.
        result = Registry([Registration(manual, self.origin)]).execute(goal, data['operation_id'], output)
        if result['action'] is not None:
            return result['action']
        candidates = result['resolution']['candidates']
        applicability = candidates[0]['applicability'] if len(candidates) == 1 else 'UNKNOWN'
        return {'execution_decision': 'REJECT' if applicability == 'FALSE' else 'BLOCK',
                'applicability': applicability, 'api_call_success': False,
                'oracle_verdict': None, 'resolution': result['resolution']}
