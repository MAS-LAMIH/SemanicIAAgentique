"""Two serialization frontends for one finite semantic contract profile."""
import json
from pathlib import Path
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from .model import Contract, Goal

SAM = Namespace('https://example.org/sam/v1#')


def load_goal(path: str | Path) -> Goal:
    return Goal(**json.loads(Path(path).read_text(encoding='utf-8')))


def load_contract(path: str | Path) -> Contract:
    """Dispatch by explicit filename suffix; never fall back after a parse failure."""
    suffix = Path(path).suffix.lower()
    if suffix == '.json':
        from .json_contract import load_json_contract
        return load_json_contract(path)
    if suffix == '.ttl':
        return load_rdf_contract(path)
    raise ValueError('Unsupported contract format; expected .ttl or .json')


def load_rdf_contract(path: str | Path) -> Contract:
    # Explicit Turtle parsing: no JSON-LD remote contexts or network imports.
    from rdflib.plugins.parsers.notation3 import BadSyntax
    try:
        graph = Graph().parse(data=Path(path).read_text(encoding='utf-8'), format='turtle')
    except BadSyntax as error:
        raise ValueError('Malformed Turtle contract') from error
    from .provider_contract import V, load_provider_graph
    if list(graph.subjects(RDF.type, V.ProviderContract)):
        return load_provider_graph(graph)
    return _contract_from_graph(graph)


def _contract_from_graph(graph: Graph) -> Contract:
    """Shared profile validation and canonical typed model construction."""
    allowed = {RDF.type, SAM.hasOperation, SAM.providesCapability, SAM.hasContract,
               SAM.requiredInput, SAM.hasPrecondition, SAM.hasExpectedEffect,
               SAM.hasBinding, SAM.requiresObservation, SAM.method, SAM.path,
               SAM.maxEvidenceAgeSeconds}
    if any(p not in allowed for _, p, _ in graph):
        raise ValueError('Unsupported contract predicate')

    def one(subject, predicate):
        values = list(graph.objects(subject, predicate))
        if len(values) != 1:
            raise ValueError(f'Expected one value for {predicate}')
        return values[0]

    def typed(subject, kind):
        if not isinstance(subject, URIRef) or set(graph.objects(subject, RDF.type)) != {kind}:
            raise ValueError(f'Expected named {kind}')

    artifacts = list(graph.subjects(RDF.type, SAM.Artifact))
    if len(artifacts) != 1:
        raise ValueError('Exactly one artifact is supported')
    artifact = artifacts[0]
    typed(artifact, SAM.Artifact)
    operation = one(artifact, SAM.hasOperation)
    typed(operation, SAM.Operation)
    capability = one(operation, SAM.providesCapability)
    typed(capability, SAM.Capability)
    manual = one(operation, SAM.hasContract)
    typed(manual, SAM.Contract)
    binding = one(manual, SAM.hasBinding)
    observation = one(manual, SAM.requiresObservation)
    typed(observation, SAM.Observation)
    inputs = set(graph.objects(manual, SAM.requiredInput))
    if inputs != {Literal('start_time'), Literal('end_time'), Literal('title')}:
        raise ValueError('Unsupported input schema')
    preconditions = set(graph.objects(manual, SAM.hasPrecondition))
    if preconditions != {SAM.PositiveInterval, SAM.CalendarWritable}:
        raise ValueError('Unsupported or missing critical precondition')
    for condition in preconditions:
        typed(condition, SAM.Precondition)
    effects = set(graph.objects(manual, SAM.hasExpectedEffect))
    if effects != {SAM.NewMatchingEvent}:
        raise ValueError('Unsupported modeled transition')
    typed(SAM.NewMatchingEvent, SAM.Effect)
    if one(binding, SAM.method) != Literal('POST') or one(binding, SAM.path) != Literal('/events'):
        raise ValueError('Unsupported executable binding')
    if one(observation, SAM.path) != Literal('/events/{id}'):
        raise ValueError('Unsupported observation binding')
    age = float(one(observation, SAM.maxEvidenceAgeSeconds))
    if not 0 < age <= 300:
        raise ValueError('Invalid evidence lifetime')
    # Reject additional disconnected assertions: no constraints are silently ignored.
    expected = Graph()
    for s, p, o in [
        (artifact, RDF.type, SAM.Artifact), (artifact, SAM.hasOperation, operation),
        (operation, RDF.type, SAM.Operation), (operation, SAM.providesCapability, capability),
        (capability, RDF.type, SAM.Capability), (operation, SAM.hasContract, manual),
        (manual, RDF.type, SAM.Contract), (manual, SAM.hasBinding, binding),
        (manual, SAM.requiresObservation, observation),
        (binding, SAM.method, Literal('POST')), (binding, SAM.path, Literal('/events')),
        (observation, RDF.type, SAM.Observation),
        (observation, SAM.path, Literal('/events/{id}')),
        (observation, SAM.maxEvidenceAgeSeconds, one(observation, SAM.maxEvidenceAgeSeconds)),
        (manual, SAM.hasExpectedEffect, SAM.NewMatchingEvent),
        (SAM.NewMatchingEvent, RDF.type, SAM.Effect),
    ]:
        expected.add((s, p, o))
    for value in inputs:
        expected.add((manual, SAM.requiredInput, value))
    for condition in preconditions:
        expected.add((manual, SAM.hasPrecondition, condition))
        expected.add((condition, RDF.type, SAM.Precondition))
    if set(graph) != set(expected):
        raise ValueError('Extra assertions outside supported profile')
    return Contract(str(artifact), str(operation), str(capability),
                    tuple(sorted(map(str, inputs))), tuple(sorted(map(str, preconditions))),
                    tuple(map(str, effects)), 'POST', '/events', '/events/{id}', age)
