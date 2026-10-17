"""One finite v2 profile validator and a lossless RDF/JSON structural frontend."""
from copy import deepcopy
from importlib.resources import files
import json
import math
from pathlib import Path
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from .model import Contract, ProviderProfile

V = Namespace('https://example.org/sam/v2#')
CAPABILITY = 'https://example.org/sam/v1#EventCreation'
EFFECT = 'https://example.org/sam/v1#NewMatchingEvent'


def schema():
    return json.loads(files('semantic_action').joinpath('schemas/contract-v2.schema.json').read_text())


def load_provider_data(data):
    try:
        Draft202012Validator(schema()).validate(data)
    except ValidationError as error:
        raise ValueError('Invalid v2 contract: ' + error.message) from error
    # JSON bools and nonfinite numbers must not masquerade as bounds.
    age = data['observation']['max_evidence_age_seconds']
    duration = data['constraints']['max_duration_seconds']
    if not math.isfinite(age) or (duration is not None and not math.isfinite(duration)):
        raise ValueError('Nonfinite profile bound')
    if len({data[k] for k in ['artifact_id','operation_id','capability_id']}) != 3:
        raise ValueError('Conflicting resource identities')
    binding = data['binding']
    # Canonical observations must contain exactly the oracle's event properties.
    if set(binding['event_fields']) != {'id','start_time','end_time','title'}:
        raise ValueError('Incomplete or extra canonical observation fields')
    return Contract(data['artifact_id'], data['operation_id'], data['capability_id'],
                    tuple(sorted(data['inputs'])), tuple(sorted(data['preconditions'])),
                    tuple(sorted(data['declared_effects'])), 'POST', binding['create_path'],
                    binding['event_path'], float(age),
                    ProviderProfile(deepcopy(data['constraints']), deepcopy(binding)))


def provider_graph(data):
    """Authoring helper only; the RDF loader validates independently of this writer."""
    graph = Graph()
    graph.bind('p', V)
    root = URIRef('urn:manual:' + data['operation_id'])
    graph.add((root, RDF.type, V.ProviderContract))
    def emit(node, value, spec):
        dynamic = isinstance(spec.get('additionalProperties'), dict)
        if dynamic:
            for key, child in value.items():
                entry = BNode()
                graph.add((node, V.entry, entry))
                graph.add((entry, V.key, Literal(key)))
                emit(entry, {'value':child}, {'properties':{'value':spec['additionalProperties']}})
        else:
            for key, child in value.items():
                field = spec['properties'].get(key,{})
                children = child if field.get('type') == 'array' else [child]
                for member in children:
                    if field.get('type') == 'object':
                        target = BNode()
                        graph.add((node, V[key], target))
                        emit(target, member, field)
                    else:
                        iri = key in {'artifact_id','operation_id','capability_id','preconditions','declared_effects'}
                        literal = URIRef(member) if iri else (V.Null if member is None else Literal(member))
                        graph.add((node, V[key], literal))
    emit(root, data, schema())
    return graph


def load_provider_graph(graph):
    roots = list(graph.subjects(RDF.type, V.ProviderContract))
    if len(roots) != 1:
        raise ValueError('Expected exactly one v2 contract')
    seen = {(roots[0], RDF.type, V.ProviderContract)}
    active = set()
    def objects(node, predicate):
        values = list(graph.objects(node, predicate))
        seen.update((node, predicate, value) for value in values)
        return values
    def one(node, predicate):
        values = objects(node,predicate)
        if len(values) != 1:
            raise ValueError('Ambiguous or missing v2 field ' + str(predicate))
        return values[0]
    def decode(node, spec):
        if node in active:
            raise ValueError('Cyclic RDF profile')
        active.add(node)
        result = {}
        if isinstance(spec.get('additionalProperties'), dict):
            for entry in objects(node,V.entry):
                key = one(entry,V.key)
                if not isinstance(key,Literal) or key.language or key.datatype:
                    raise ValueError('Mapping keys must be plain strings')
                key = str(key)
                if key in result:
                    raise ValueError('Duplicate mapping target')
                value_node = one(entry,V.value)
                result[key] = decode(value_node,spec['additionalProperties'])
        else:
            for key, field in spec['properties'].items():
                array = field.get('type') == 'array'
                values = objects(node,V[key]) if array else [one(node,V[key])]
                decoded = []
                for value in values:
                    if field.get('type') == 'object':
                        if not isinstance(value,(BNode,URIRef)):
                            raise ValueError('Expected RDF profile record')
                        child = decode(value,field)
                    elif key in {'artifact_id','operation_id','capability_id','preconditions','declared_effects'}:
                        if not isinstance(value,URIRef):
                            raise ValueError('Expected semantic IRI')
                        child = str(value)
                    elif value == V.Null:
                        child = None
                    elif isinstance(value,Literal):
                        child = value.toPython()
                        if type(child) not in (str,int,float,bool):
                            raise ValueError('Unsupported RDF literal')
                        if value.language:
                            raise ValueError('Language-tagged profile values unsupported')
                    else:
                        raise ValueError('Expected literal profile value')
                    decoded.append(child)
                result[key] = sorted(decoded) if array else decoded[0]
        active.remove(node)
        return result
    data = decode(roots[0],schema())
    if set(graph) != seen:
        raise ValueError('Unsupported extra RDF profile assertions')
    return load_provider_data(data)
