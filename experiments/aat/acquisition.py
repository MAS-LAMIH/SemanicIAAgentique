"""Offline, quarantined OpenAPI structure extraction. No execution or Usage inference."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from .model import NS

AA = Namespace(NS)
SX = Namespace('urn:eswc:aat:structure:1#')
VERSION = 'openapi-structure/1.1'
MAX_BYTES, MAX_DEPTH, MAX_NODES, MAX_TRIPLES = 1048576, 32, 20000, 20000
METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pointer(base, key):
    return base + '/' + str(key).replace('~', '~0').replace('/', '~1')


def read_json(data):
    if len(data) > MAX_BYTES:
        raise ValueError('Document exceeds byte limit')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    result = json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite number')))
    count = 0
    def check(value, depth):
        nonlocal count
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES:
            raise ValueError('JSON depth/node limit')
        if isinstance(value, dict):
            for item in value.values(): check(item, depth + 1)
        elif isinstance(value, list):
            for item in value: check(item, depth + 1)
    check(result, 0)
    return result


class Extractor:
    def __init__(self, document, config, source_hash):
        self.doc, self.config, self.source_hash = document, config, source_hash
        self.graph, self.provenance, self.diagnostics = Graph(), {}, []
        self.nodes = 0
        self.config_hash = digest(canonical(config).encode())

    def problem(self, code, path, detail, status='UNSUPPORTED'):
        entry = dict(status=status, code=code, source=path, detail=detail)
        if entry not in self.diagnostics: self.diagnostics.append(entry)

    def node(self, path):
        return URIRef('urn:aat:extracted:' + digest((self.config['artifact'] + '\n' + path).encode()))

    def add(self, subject, predicate, obj, path, rule, evidence='STRUCTURE', detail='Exact documented fact'):
        triple = (subject, predicate, obj)
        text = ' '.join(x.n3() for x in triple) + ' .'
        key = digest(text.encode())
        source = dict(document_sha256=self.source_hash, source=path, rule=rule,
                      evidence_class='CONFIGURATION' if path.startswith('config:') else evidence, extractor_version=VERSION, transformation=detail)
        if path.startswith('config:'): source['configuration_sha256'] = self.config_hash
        if key not in self.provenance:
            if len(self.provenance) >= MAX_TRIPLES: raise ValueError('Assertion limit')
            self.graph.add(triple)
            self.provenance[key] = dict(assertion_id=key, triple=text, sources=[])
        if source not in self.provenance[key]['sources']: self.provenance[key]['sources'].append(source)

    def resolve(self, value, path, trail=()):
        if not isinstance(value, dict): raise ValueError('Object required at ' + path)
        if '$ref' not in value: return value, path
        if len(trail) >= 16: raise ValueError('Reference depth limit at ' + path)
        ref = value['$ref']
        if not isinstance(ref, str) or not ref.startswith('#/'):
            raise ValueError('Remote/non-pointer reference forbidden at ' + path)
        if ref in trail: raise ValueError('Cyclic reference at ' + path)
        if len(value) != 1:
            self.problem('REF_SIBLINGS', path, 'Reference siblings not merged; referring object retained only as diagnostic')
            return {}, path
        target = self.doc
        for token in ref[2:].split('/'):
            if re.search(r'~(?![01])', token): raise ValueError('Malformed JSON Pointer')
            token = token.replace('~1', '/').replace('~0', '~')
            if isinstance(target, dict) and token in target: target = target[token]
            elif isinstance(target, list) and re.fullmatch(r'0|[1-9][0-9]*', token) and int(token) < len(target): target = target[int(token)]
            else: raise ValueError('Unresolved reference ' + ref)
        return self.resolve(target, ref, trail + (ref,))

    def schema(self, value, path, trail=()):
        self.nodes += 1
        if self.nodes > MAX_NODES or len(trail) > MAX_DEPTH: raise ValueError('Schema expansion limit')
        value, actual = self.resolve(value, path)
        if actual in trail: raise ValueError('Cyclic schema at ' + actual)
        node = self.node(path)
        self.add(node, RDF.type, SX.Schema, path, 'schema-node')
        self.add(node, SX.rawSchema, Literal(canonical(value), datatype=RDF.JSON), actual, 'schema-source')
        if actual != path: self.add(node, SX.referenceTarget, Literal(actual), path + '/$ref', 'local-reference')
        allowed = {'type','properties','items','required','enum','minimum','maximum','exclusiveMinimum','exclusiveMaximum',
                   'minLength','maxLength','minItems','maxItems','pattern','format','additionalProperties','nullable',
                   'description','title','default','example','examples','readOnly','writeOnly','deprecated'}
        blocked = set(value) - allowed
        if blocked:
            for key in sorted(blocked): self.problem('SCHEMA_KEYWORD', pointer(actual,key), 'Not interpreted: ' + key)
            # Preserve opaque schema instead of pretending its conjuncts/alternatives are flattened.
            return node
        schema_type = value.get('type')
        if schema_type is not None:
            valid = schema_type in ('object','array','integer','number','string','boolean') if isinstance(schema_type,str) else False
            if not valid:
                self.problem('SCHEMA_TYPE',actual, 'Unsupported type or union; no type coercion'); return node
            self.add(node,SX.schemaType,Literal(schema_type),pointer(actual,'type'),'schema-type','CONSTRAINT')
        for key in ('required','enum','minimum','maximum','exclusiveMinimum','exclusiveMaximum','minLength','maxLength','minItems','maxItems','pattern','format','additionalProperties','nullable','readOnly','writeOnly'):
            if key not in value: continue
            v=value[key]
            if key=='nullable' and self.doc['openapi'].startswith('3.1.'):
                self.problem('DIALECT_NULLABLE',pointer(actual,key),'3.1 does not define nullable; not interpreted'); continue
            if key in ('exclusiveMinimum','exclusiveMaximum'):
                valid=type(v) is bool if self.doc['openapi'].startswith('3.0.') else type(v) in (int,float)
            elif key in ('minimum','maximum'): valid=type(v) in (int,float)
            elif key in ('minLength','maxLength','minItems','maxItems'): valid=type(v) is int and v>=0
            elif key in ('nullable','readOnly','writeOnly'): valid=type(v) is bool
            elif key in ('pattern','format'): valid=isinstance(v,str)
            elif key=='required': valid=isinstance(v,list) and all(isinstance(x,str) for x in v) and len(v)==len(set(v))
            elif key=='enum': valid=isinstance(v,list) and bool(v)
            else: valid=type(v) is bool  # schema-valued additionalProperties remains unsupported
            if not valid:
                self.problem('CONSTRAINT_SHAPE',pointer(actual,key),'Unsupported/malformed constraint'); continue
            self.add(node,SX[key],Literal(canonical(v),datatype=RDF.JSON),pointer(actual,key),'schema-constraint','CONSTRAINT', 'Exact JSON constraint in declared OpenAPI dialect; no behavioral entailment')
            if key=='format': self.problem('FORMAT_ANNOTATION',pointer(actual,key),'Format retained as annotation, not a validator', 'UNKNOWN')
        props=value.get('properties',{})
        if not isinstance(props,dict): raise ValueError('properties must be object')
        for name, child in sorted(props.items()):
            p=pointer(pointer(actual,'properties'),name);prop=self.node(p+'/property')
            self.add(node,SX.property,prop,p,'schema-property')
            self.add(prop,SX.name,Literal(name),p,'property-name')
            self.add(prop,SX.schema,self.schema(child,p,trail+(actual,)),p,'property-schema')
        if 'items' in value:
            p=pointer(actual,'items');self.add(node,SX.items,self.schema(value['items'],p,trail+(actual,)),p,'array-items')
        return node

    def media(self, parent, value, path):
        if not isinstance(value,dict): raise ValueError('content must be object')
        for media, item in sorted(value.items()):
            p=pointer(path,media);node=self.node(p)
            if not isinstance(item,dict): raise ValueError('Media object required')
            self.add(parent,SX.content,node,p,'media-link');self.add(node,SX.mediaType,Literal(media),p,'media-type')
            if media!='application/json': self.problem('MEDIA_TYPE',p,'Structure only; wire execution unsupported')
            if 'encoding' in item: self.problem('ENCODING',p+'/encoding','Content encoding not interpreted')
            if 'schema' in item:self.add(node,SX.schema,self.schema(item['schema'],p+'/schema'),p+'/schema','media-schema')
            else:self.problem('MISSING_SCHEMA',p,'No schema documented','UNKNOWN')

    def parameters(self, parent, parameters, path):
        if not isinstance(parameters,list): raise ValueError('parameters must be array')
        seen=set()
        for i,item in enumerate(parameters):
            item,p=self.resolve(item,pointer(path,i));name,location=item.get('name'),item.get('in')
            if not isinstance(name,str) or not name or location not in ('path','query','header','cookie'): raise ValueError('Missing/invalid parameter binding')
            if (name,location) in seen: raise ValueError('Duplicate parameter binding')
            seen.add((name,location));node=self.node(p)
            required=item.get('required',False)
            if type(required) is not bool or location=='path' and required is not True: raise ValueError('Invalid parameter required')
            self.add(parent,SX.parameter,node,p,'parameter-link')
            for key,v in (('name',name),('location',location),('required',required)):
                self.add(node,SX[key],Literal(v),(pointer(p,'in' if key=='location' else key) if (key!='required' or 'required' in item) else p),'parameter-field',detail='OpenAPI required defaults false when absent' if key=='required' else 'Exact documented field')
            default_style='form' if location in ('query','cookie') else 'simple'
            style=item.get('style',default_style);explode=item.get('explode',style=='form')
            self.add(node,SX.serialization,Literal(canonical(dict(style=style,explode=explode)),datatype=RDF.JSON),p,'parameter-serialization',detail='Explicit values or OpenAPI location defaults')
            if style!=default_style or type(explode) is not bool or item.get('allowReserved',False) or 'content' in item:
                self.problem('PARAMETER_SERIALIZATION',p,'Nondefault serialization/content retained, not executable')
            if 'schema' in item:self.add(node,SX.schema,self.schema(item['schema'],p+'/schema'),p+'/schema','parameter-schema')
            else:self.problem('PARAMETER_SCHEMA',p,'Missing supported schema','UNKNOWN')
        return seen

    def security(self,parent,value,path):
        if not isinstance(value,list) or any(not isinstance(v,dict) for v in value): raise ValueError('security must be array of objects')
        self.add(parent,SX.securityRequirements,Literal(canonical(value),datatype=RDF.JSON),path,'security-requirements',detail='Explicit requirements or OpenAPI default empty requirements; no authentication performed')
        for group in value:
            for name,scopes in group.items():
                if name not in self.doc.get('components',{}).get('securitySchemes',{}): raise ValueError('Undeclared security scheme')
                if not isinstance(scopes,list) or not all(isinstance(s,str) for s in scopes): raise ValueError('Invalid security scopes')
                self.problem('AUTH_EXECUTION',path,'Authentication declaration only; no credential acquisition or execution')

    def extract(self):
        d=self.doc
        if not isinstance(d,dict) or not re.fullmatch(r'3\.[01]\.[0-9]+',str(d.get('openapi',''))): raise ValueError('Unsupported OpenAPI version')
        if not isinstance(d.get('info'),dict) or not all(isinstance(d['info'].get(k),str) for k in ('title','version')): raise ValueError('Missing info title/version')
        if not isinstance(d.get('paths'),dict) or not d['paths']: raise ValueError('Missing paths')
        for key in d:
            if key.startswith('x-'):self.problem('VENDOR_EXTENSION',pointer('#',key),'Source claim only; no inferred behavioral assertions')
        if 'webhooks' in d:self.problem('WEBHOOKS','#/webhooks','Not extracted')
        if 'jsonSchemaDialect' in d:self.problem('SCHEMA_DIALECT','#/jsonSchemaDialect','Custom dialect unsupported')
        def inspect_refs(value, path):
            if isinstance(value,dict):
                if '$ref' in value:self.resolve(value,path)
                for k,v in sorted(value.items()):inspect_refs(v,pointer(path,k))
            elif isinstance(value,list):
                for i,v in enumerate(value):inspect_refs(v,pointer(path,i))
        inspect_refs(d,'#')
        artifact,thing=URIRef(self.config['artifact']),URIRef(self.config['thing'])
        self.add(thing,RDF.type,AA.Thing,'config:thing','configured-thing')
        self.add(artifact,RDF.type,AA.Artifact,'config:artifact','configured-artifact')
        self.add(artifact,AA.represents,thing,'config:thing','configured-grounding',detail='Deployment-assigned identity; not inferred from API')
        self.add(artifact,SX.origin,Literal(self.config['origin']),'config:origin','configured-origin')
        self.add(artifact,SX.openapiVersion,Literal(d['openapi']),'#/openapi','dialect')
        if 'servers' in d:
            self.add(artifact,SX.documentedServers,Literal(canonical(d['servers']),datatype=RDF.JSON),'#/servers','server-declarations')
            self.problem('SERVER_BINDING','#/servers','Documented servers retained; explicit configuration is not proof of deployment compatibility','UNKNOWN')
        for name,item in sorted(d.get('components',{}).get('securitySchemes',{}).items()):
            p=pointer('#/components/securitySchemes',name);item,actual=self.resolve(item,p);n=self.node(p)
            self.add(artifact,SX.securityScheme,n,p,'security-scheme');self.add(n,SX.name,Literal(name),p,'scheme-name')
            self.add(n,SX.declaration,Literal(canonical(item),datatype=RDF.JSON),actual,'scheme-declaration')
            self.problem('AUTH_SCHEME',p,'Declaration retained only; no authentication mechanism executed')
        ids=set();count=0
        for path,pathitem in sorted(d['paths'].items()):
            if not path.startswith('/') or '?' in path or '#' in path: raise ValueError('Invalid operation path')
            pathitem,pp=self.resolve(pathitem,pointer('#/paths',path))
            if 'servers' in pathitem:self.problem('PATH_SERVERS',pp+'/servers','Not resolved to executable binding')
            for method,op in sorted(pathitem.items()):
                if method not in METHODS:
                    if method not in ('parameters','summary','description','servers'):
                        self.problem('PATH_FEATURE',pointer(pp,method),'Not interpreted')
                    continue
                if not isinstance(op,dict) or not isinstance(op.get('responses'),dict) or not op['responses']: raise ValueError('Missing operation/response binding')
                count+=1;p=pointer(pp,method);node=self.node(p)
                self.add(artifact,AA.hasOperation,node,p,'artifact-operation');self.add(node,RDF.type,AA.Operation,p,'operation-type')
                self.add(node,AA.method,Literal(method.upper()),p,'http-method');self.add(node,AA.path,Literal(path),pp,'http-path')
                if 'operationId' in op:
                    oid=op['operationId']
                    if not isinstance(oid,str) or not oid or oid in ids: raise ValueError('Conflicting/invalid operationId')
                    ids.add(oid);self.add(node,SX.operationId,Literal(oid),p+'/operationId','operation-identifier')
                if method=='get':self.add(node,SX.observationCandidate,Literal(True),p,'get-candidate',detail='GET heuristic only, not confirmed observation or read-only guarantee')
                # Preserve both levels. Overrides are reported, not silently merged.
                inherited=self.parameters(node,pathitem.get('parameters',[]),pp+'/parameters')
                local=self.parameters(node,op.get('parameters',[]),p+'/parameters')
                if inherited & local:self.problem('PARAMETER_OVERRIDE',p+'/parameters','Both declarations retained; effective merge unsupported')
                if {name for name,loc in inherited|local if loc=='path'}!=set(re.findall(r'\{([^{}]+)\}',path)):
                    raise ValueError('Missing/ambiguous path parameter binding')
                if 'requestBody' in op:
                    body,bp=self.resolve(op['requestBody'],p+'/requestBody');bn=self.node(p+'/requestBody')
                    if not isinstance(body.get('content'),dict) or not body['content']: raise ValueError('Missing request body content')
                    required=body.get('required',False)
                    if type(required) is not bool: raise ValueError('Invalid body required')
                    self.add(node,SX.requestBody,bn,p+'/requestBody','request-body')
                    self.add(bn,SX.required,Literal(required),bp,'body-required',detail='Explicit required or OpenAPI default false')
                    self.media(bn,body['content'],bp+'/content')
                for code,response in sorted(op['responses'].items()):
                    if not re.fullmatch(r'[1-5][0-9]{2}|[1-5]XX|default',code): raise ValueError('Invalid response status')
                    response,rp=self.resolve(response,pointer(p+'/responses',code));rn=self.node(pointer(p+'/responses',code))
                    if not isinstance(response.get('description'),str):raise ValueError('Missing response description')
                    self.add(node,SX.response,rn,pointer(p+'/responses',code),'response');self.add(rn,SX.statusCode,Literal(code),pointer(p+'/responses',code),'response-status')
                    self.media(rn,response.get('content',{}),rp+'/content')
                    if 'headers' in response:
                        self.add(rn,SX.headers,Literal(canonical(response['headers']),datatype=RDF.JSON),rp+'/headers','response-headers')
                        self.problem('RESPONSE_HEADERS',rp+'/headers','Header declarations retained, not mapped to runtime')
                    if 'links' in response:self.problem('RESPONSE_LINKS',rp+'/links','Not interpreted')
                secpath=p+'/security' if 'security' in op else '#/security'
                self.security(node,op.get('security',d.get('security',[])),secpath if ('security' in op or 'security' in d) else p)
                for key in op:
                    if key not in {'operationId','parameters','requestBody','responses','security','tags','summary','description','externalDocs','deprecated'}:
                        self.problem('OPERATION_FEATURE',pointer(p,key),'Retained in source only; no inferred behavioral meaning')
        if not count: raise ValueError('No operations')
        self.problem('BEHAVIOR_UNKNOWN','#','No Usage, readiness, effect, revision guarantee or frame inferred; behavioral review required','UNKNOWN')
        return self


def acquire(source, config, output):
    """Always quarantined. Existing output directories are never overwritten."""
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    with Path(source).open('rb') as stream:data=stream.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        report=dict(status='INVALID',executable=False,source_sha256=None,extractor_version=VERSION,error='Document exceeds byte limit; original not copied',diagnostics=[])
        (output/'diagnostics.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        return report
    (output/'source.json').write_bytes(data)
    source_hash=digest(data);extractor=None
    try:
        if set(config)!={'artifact','thing','origin'}: raise ValueError('Exactly artifact, thing, origin configuration required')
        for key in ('artifact','thing'):
            if not isinstance(config[key],str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|\\^`]+',config[key]): raise ValueError('Absolute identity IRI required')
        if config['artifact']==config['thing']: raise ValueError('Artifact and Thing must differ')
        origin=urlsplit(config['origin'])
        if origin.scheme not in ('http','https') or not origin.hostname or origin.username or origin.password or origin.query or origin.fragment: raise ValueError('Public HTTP(S) origin configuration required')
        document=read_json(data);extractor=Extractor(document,config,source_hash).extract()
        triples=sorted(entry['triple'] for entry in extractor.provenance.values())
        (output/'structural.ttl').write_text('\n'.join(triples)+'\n')
        (output/'config.json').write_text(json.dumps(config,sort_keys=True,indent=2)+'\n')
        provenance=dict(extractor_version=VERSION,source_sha256=source_hash,assertions=sorted(extractor.provenance.values(),key=lambda x:x['assertion_id']))
        (output/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
        report=dict(status='QUARANTINED',executable=False,source_sha256=source_hash,graph_sha256=digest((output/'structural.ttl').read_bytes()),
                    extractor_version=VERSION,assertions=len(triples),diagnostics=sorted(extractor.diagnostics,key=canonical))
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError) as error:
        report=dict(status='INVALID',executable=False,source_sha256=source_hash,extractor_version=VERSION,error=str(error),
                    diagnostics=extractor.diagnostics if extractor else [])
    (output/'diagnostics.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--config',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=acquire(args.source,read_json(args.config.read_bytes()),args.output)
    print(json.dumps(report,indent=2));return 0 if report['status']=='QUARANTINED' else 2


if __name__=='__main__':raise SystemExit(main())
