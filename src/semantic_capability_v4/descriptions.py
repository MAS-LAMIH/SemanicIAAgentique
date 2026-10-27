"""Independent JSON/Turtle parsing into one strict finite description profile."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from .model import EVENT_CREATION, INPUT_ROLES, NAMESPACE, OperationDescription

FIELDS = {'description_version', 'provider_id', 'operation_id', 'capability_id',
          'method', 'path', 'input_mapping', 'output_mapping', 'input_limits'}
LIMITS = {'title_max_length', 'max_duration_seconds', 'time_grid_seconds'}


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def _bad_number(value):
    raise ValueError('Nonfinite JSON number: ' + value)


def _keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('Missing or unsupported profile fields')


def _identifier(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        raise ValueError('Identifier must be an absolute URI')
    address = urlsplit(value)
    if not ((address.scheme in {'http', 'https'} and address.netloc) or
            (address.scheme == 'urn' and address.path)):
        raise ValueError('Identifier must be an absolute URI')


def normalize(data):
    _keys(data, FIELDS)
    if type(data['description_version']) is not int or data['description_version'] != 1:
        raise ValueError('Unsupported description version')
    for key in ('provider_id', 'operation_id', 'capability_id'):
        _identifier(data[key])
    if data['capability_id'] != EVENT_CREATION:
        raise ValueError('Unsupported capability vocabulary entry')
    if data['method'] != 'POST':
        raise ValueError('Only POST operations are supported')
    path = data['path']
    if (not isinstance(path, str) or not re.fullmatch(r'/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*', path)):
        raise ValueError('Expected a fixed local operation path')
    mappings = []
    for key, roles in (('input_mapping', INPUT_ROLES), ('output_mapping', ('id',))):
        _keys(data[key], roles)
        values = []
        for role, rule in sorted(data[key].items()):
            _keys(rule, {'field', 'conversion'})
            field, conversion = rule['field'], rule['conversion']
            if not isinstance(field, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', field):
                raise ValueError('Unsupported native field')
            allowed = ('identity', 'iso_to_epoch_ms') if role in ('start_time', 'end_time') else ('identity',)
            if conversion not in allowed:
                raise ValueError('Unsupported role conversion')
            values.append((role, field, conversion))
        if len({field for _, field, _ in values}) != len(values):
            raise ValueError('Ambiguous native field mapping')
        mappings.append(tuple(values))
    _keys(data['input_limits'], LIMITS)
    for value in data['input_limits'].values():
        if type(value) is not int or not 0 <= value <= 1000000000:
            raise ValueError('Input limits must be bounded nonnegative integers; zero means no limit')
    return OperationDescription(*(data[key] for key in ('description_version', 'provider_id', 'operation_id',
        'capability_id', 'method', 'path')), *mappings,
        **data['input_limits'])


def load_json(path):
    try:
        return normalize(json.loads(Path(path).read_text(), object_pairs_hook=_object, parse_constant=_bad_number))
    except (TypeError, KeyError, OverflowError) as error:
        raise ValueError('Malformed JSON description') from error


def load_rdf(path):
    # Lazy import: JSON and invocation work without RDFLib installed/imported.
    from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef, XSD
    ns = Namespace(NAMESPACE)
    from rdflib.exceptions import ParserError
    from rdflib.plugins.parsers.notation3 import BadSyntax
    try:
        graph = Graph().parse(data=Path(path).read_text(), format='turtle')
    except (ParserError, BadSyntax) as error:
        raise ValueError('Malformed Turtle description') from error
    used = set()
    def one(subject, predicate, kind):
        values = list(graph.objects(subject, predicate))
        if len(values) != 1:
            raise ValueError('Missing or ambiguous RDF singleton')
        value = values[0]
        used.add((subject, predicate, value))
        if kind == 'node':
            if not isinstance(value, (BNode, URIRef)):
                raise ValueError('Mapping/limits require a node')
            return value
        if kind == 'uri':
            if not isinstance(value, URIRef):
                raise ValueError('Expected URI identifier')
        elif kind == 'int':
            if not isinstance(value, Literal) or value.datatype != XSD.integer:
                raise ValueError('Expected integer literal')
            try:
                return int(str(value))
            except ValueError as error:
                raise ValueError('Invalid integer literal') from error
        elif not isinstance(value, Literal) or value.language or value.datatype not in (None, XSD.string):
            raise ValueError('Expected plain string literal')
        return str(value)
    roots = list(graph.subjects(RDF.type, ns.OperationDescription))
    if len(roots) != 1:
        raise ValueError('Exactly one operation description required')
    root = roots[0]
    if not isinstance(root, URIRef):
        raise ValueError('Operation identity must be a URI')
    used.add((root, RDF.type, ns.OperationDescription))
    data = {'operation_id': str(root)}
    for key in ('description_version', 'provider_id', 'capability_id', 'method', 'path'):
        kind = 'int' if key == 'description_version' else 'uri' if key.endswith('_id') else 'str'
        data[key] = one(root, ns[key], kind)
    for key in ('input_mapping', 'output_mapping'):
        mapping = {}
        for node in graph.objects(root, ns[key]):
            used.add((root, ns[key], node))
            if not isinstance(node, (BNode, URIRef)):
                raise ValueError('Mapping requires a node')
            role_uri = one(node, ns.role, 'uri')
            if not role_uri.startswith(NAMESPACE):
                raise ValueError('Unknown role namespace')
            role = role_uri[len(NAMESPACE):]
            if role in mapping:
                raise ValueError('Duplicate role mapping')
            mapping[role] = {'field': one(node, ns.field, 'str'), 'conversion': one(node, ns.conversion, 'str')}
        data[key] = mapping
    limits = one(root, ns.input_limits, 'node')
    data['input_limits'] = {key: one(limits, ns[key], 'int') for key in LIMITS}
    if set(graph) != used:
        raise ValueError('Unsupported RDF assertions')
    return normalize(data)


def load(path):
    suffix = Path(path).suffix
    if suffix == '.json':
        return load_json(path)
    if suffix == '.ttl':
        return load_rdf(path)
    raise ValueError('Expected .json or .ttl; no fallback parsing')
