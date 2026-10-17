"""Strict JSON parsing, local schema validation, then the shared profile validator.

The transient RDF graph is an internal adapter, not a network service or a second
execution engine. Anonymous manual/binding identities carry no execution meaning.
"""
import json
from importlib.resources import files
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from rdflib import Graph, Literal, RDF, URIRef

from .contract import SAM, _contract_from_graph
from .model import Contract


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Ambiguous JSON contract: duplicate key {key}')
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError(f'Invalid JSON numeric constant: {value}')


def load_json_contract(path: str | Path) -> Contract:
    data = json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=_unique_object, parse_constant=_nonfinite)
    schema = json.loads(files('semantic_action').joinpath(
        'schemas/contract-v1.schema.json').read_text(encoding='utf-8'))
    try:
        Draft202012Validator(schema).validate(data)
    except ValidationError as error:
        location = '/'.join(map(str, error.absolute_path)) or '<root>'
        raise ValueError(f'JSON contract schema violation at {location}: {error.message}') from error
    # Construct exactly the assertions accepted by the RDF profile. This keeps
    # cardinality, vocabulary, binding and transition validation in one place.
    graph = Graph()
    artifact, operation, capability = (URIRef(data[key]) for key in (
        'artifact_id', 'operation_id', 'capability_id'))
    # Fresh internal IDs cannot collide with user-supplied identifiers.
    used = {artifact, operation, capability}
    def internal():
        while True:
            value = URIRef('urn:sam:json:' + str(uuid4()))
            if value not in used:
                used.add(value)
                return value
    manual, binding, observation = internal(), internal(), internal()
    for triple in [
        (artifact, RDF.type, SAM.Artifact), (artifact, SAM.hasOperation, operation),
        (operation, RDF.type, SAM.Operation), (operation, SAM.providesCapability, capability),
        (capability, RDF.type, SAM.Capability), (operation, SAM.hasContract, manual),
        (manual, RDF.type, SAM.Contract), (manual, SAM.hasBinding, binding),
        (manual, SAM.requiresObservation, observation),
        (binding, SAM.method, Literal(data['binding']['method'])),
        (binding, SAM.path, Literal(data['binding']['path'])),
        (observation, RDF.type, SAM.Observation),
        (observation, SAM.path, Literal(data['observation']['path'])),
        (observation, SAM.maxEvidenceAgeSeconds, Literal(data['observation']['max_evidence_age_seconds'])),
    ]:
        graph.add(triple)
    for name in data['inputs']:
        graph.add((manual, SAM.requiredInput, Literal(name)))
    for key, predicate, kind in [
        ('preconditions', SAM.hasPrecondition, SAM.Precondition),
        ('declared_effects', SAM.hasExpectedEffect, SAM.Effect),
    ]:
        for value in data[key]:
            node = URIRef(value)
            graph.add((manual, predicate, node))
            graph.add((node, RDF.type, kind))
    return _contract_from_graph(graph)
