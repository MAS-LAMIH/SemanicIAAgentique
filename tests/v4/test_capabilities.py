"""V4 tests only: fixture/storage assertions are outside the V4 runtime."""
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Event
import unittest
from unittest.mock import MagicMock, patch

from semantic_capability_v4.descriptions import load, load_json, load_rdf
from semantic_capability_v4.invoke import invoke, invoke_capability
from semantic_capability_v4.mapping import convert
from semantic_capability_v4.model import EVENT_CREATION, InvocationResult
from semantic_capability_v4.registry import Ambiguous, NotFound, resolve
# Visible fixture imports belong to tests, never the runtime.
from semantic_action.artifact import Scenario, serve
from semantic_action.provider_b import BookingScenario, serve_bookings

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'v4/descriptions'
VALUES = {'start_time': '2030-01-07T10:00:00+00:00',
          'end_time': '2030-01-07T11:00:00+00:00', 'title': 'Réunion ✓'}


def fixture(provider, mode='normal', permission=True):
    baseline = {'existing': {'metadata': 'preserve this unrelated native record'}}
    state = (Scenario(events=deepcopy(baseline), mode=mode, writable=permission) if provider == 'a'
             else BookingScenario(items=deepcopy(baseline), mode=mode, can_book=permission))
    return (serve if provider == 'a' else serve_bookings), state, baseline


def native_correct(provider, state, baseline, output):
    # Independent of description mappings, runtime conversion functions and responses
    # except the returned ID, whose consistency with actual native state is checked.
    records = state.events if provider == 'a' else state.items
    new = set(records) - set(baseline)
    if len(new) != 1 or {k: records.get(k) for k in baseline} != baseline or state.calls != 1:
        return False
    key = next(iter(new))
    if not output or output.get('id') != key:
        return False
    item = records[key]
    if provider == 'a':
        return (item.get('id') == key and item.get('title') == VALUES['title'] and
                datetime.fromisoformat(item['start_time']) == datetime.fromisoformat(VALUES['start_time']) and
                datetime.fromisoformat(item['end_time']) == datetime.fromisoformat(VALUES['end_time']))
    return (item.get('booking_ref') == key and item.get('label') == VALUES['title'] and
            item.get('begins_ms') == 1894010400000 and item.get('finishes_ms') == 1894014000000)


class DescriptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
    def json_file(self, data):
        path = Path(self.temp.name) / 'description.json'
        path.write_text(json.dumps(data))
        return path
    def test_json_rdf_normalization(self):
        for provider in 'ab':
            self.assertEqual(load(DATA / f'{provider}.json'), load(DATA / f'{provider}.ttl'))
        vocabulary = json.loads((ROOT / 'v4/vocabulary.json').read_text())
        self.assertIn(EVENT_CREATION, vocabulary['capabilities'])
    def test_strict_json_profile(self):
        base = json.loads((DATA / 'b.json').read_text())
        changes = [dict(description_version=True), dict(description_version=2), dict(extra='ignored'),
                   dict(capability_id='urn:unsupported'), dict(method='GET'), dict(path='//outside'),
                   dict(path='/../events'), dict(provider_id='display name'), dict(input_limits={})]
        for delta in changes:
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                load_json(self.json_file(dict(base, **delta)))
        for key in base:
            data = deepcopy(base); del data[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                load_json(self.json_file(data))
    def test_mapping_and_limits_reject(self):
        base = json.loads((DATA / 'b.json').read_text())
        for bad in ('script', None, 3):
            data = deepcopy(base); data['input_mapping']['title']['conversion'] = bad
            with self.assertRaises(ValueError): load_json(self.json_file(data))
        for bad in (True, -1, 1.5, '900', float('inf')):
            data = deepcopy(base); data['input_limits']['time_grid_seconds'] = bad
            with self.assertRaises(ValueError): load_json(self.json_file(data))
        data = deepcopy(base); data['input_mapping']['title']['field'] = 'begins_ms'
        with self.assertRaises(ValueError): load_json(self.json_file(data))
    def test_duplicate_nonfinite_and_unknown_suffix(self):
        path = Path(self.temp.name)/'bad.json'
        for text in ('{"description_version":1,"description_version":1}', '{"x":NaN}', '[1]', '{'):
            path.write_text(text)
            with self.assertRaises(ValueError): load(path)
        with self.assertRaises(ValueError): load(path.with_suffix('.xml'))
    def test_rdf_rejects_unsupported_ambiguous_and_incomplete(self):
        source = (DATA/'a.ttl').read_text(); path = Path(self.temp.name)/'bad.ttl'
        changes = [source + '\n<urn:extra> <urn:predicate> "data" .',
                   source + '\n<urn:provider:a:create> v:method "DELETE" .',
                   source.replace('v:method "POST" ;', ''),
                   source.replace('v:description_version 1', 'v:description_version true'),
                   source.replace('v:role v:title', 'v:role v:start_time'),
                   source.replace('v:conversion "identity"', 'v:conversion "script"'),
                   source.replace('v:time_grid_seconds 0', 'v:time_grid_seconds -1'), 'not turtle {']
        for text in changes:
            path.write_text(text)
            with self.subTest(text=text[-80:]), self.assertRaises(ValueError): load_rdf(path)
    def test_singleton_rdf_repeated_identical_triple_is_idempotent(self):
        path = Path(self.temp.name)/'same.ttl'
        path.write_text((DATA/'a.ttl').read_text() + '\n<urn:provider:a:create> v:method "POST" .')
        self.assertEqual(load(path), load(DATA/'a.json'))
    def test_json_core_has_no_rdf_or_legacy_dependency(self):
        code = """
import sys
class Block:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'rdflib','semantic_action','jsonschema'}:
            raise ImportError('Forbidden runtime dependency: '+fullname)
sys.meta_path.insert(0,Block())
from semantic_capability_v4.descriptions import load_json
from semantic_capability_v4.invoke import invoke
op=load_json('v4/descriptions/a.json')
assert invoke(op,'http://127.0.0.1:1',{}).error_kind=='input'
"""
        result = subprocess.run([sys.executable, '-S', '-c', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class ResolutionTests(unittest.TestCase):
    def test_exact_identity_and_selectors(self):
        a, b = [load(DATA/f'{p}.json') for p in 'ab']
        self.assertEqual(resolve([a], EVENT_CREATION), a)
        self.assertEqual(resolve([a,b], EVENT_CREATION, provider_id=b.provider_id), b)
        self.assertEqual(resolve([a,b], EVENT_CREATION, operation_id=a.operation_id), a)
        for capability in ('EventCreation', 'create_event', EVENT_CREATION.lower(), 'urn:unknown'):
            with self.assertRaises(NotFound): resolve([a,b], capability)
    def test_ambiguity_never_selects_first(self):
        a,b = [load(DATA/f'{p}.json') for p in 'ab']
        for entries in ([a,b],[b,a],[a,a],[a,replace(b, operation_id=a.operation_id)]):
            with self.assertRaises(Ambiguous): resolve(entries, EVENT_CREATION)
        with self.assertRaises(NotFound): resolve([], EVENT_CREATION)
    def test_resolution_failure_does_not_call_http(self):
        a,b = [load(DATA/f'{p}.json') for p in 'ab']
        with patch('semantic_capability_v4.http.post') as http:
            for entries,capability in (([a,b],EVENT_CREATION),([a],'urn:unknown')):
                result=invoke_capability(entries,capability,'http://127.0.0.1:1',VALUES)
                self.assertEqual(result.error_kind,'resolution')
            http.assert_not_called()


class ConversionTests(unittest.TestCase):
    def test_exact_conversions_and_offsets(self):
        self.assertEqual(convert('2030-01-07T11:00:00+01:00','iso_to_epoch_ms'),1894010400000)
        self.assertEqual(convert('1969-12-31T23:59:59.999Z','iso_to_epoch_ms'),-1)
        self.assertEqual(convert(-1,'epoch_ms_to_iso'),'1969-12-31T23:59:59.999000+00:00')
        for value in (True, 1.5, '123'):
            with self.assertRaises(ValueError): convert(value,'epoch_ms_to_iso')
        for value in ('2030-01-07T10:00:00.000001Z','2030-01-07T10:00:00.0000001Z','2030-01-07T10:00:00',
                      '2030-01-07T10:00:00.123456+00:00:00.0000001'):
            with self.assertRaises(ValueError): convert(value,'iso_to_epoch_ms')
        with self.assertRaises(ValueError): convert('x','executable')


class InvocationTests(unittest.TestCase):
    def test_success_both_frontends_both_native_fixtures(self):
        for provider in 'ab':
            for suffix in ('json','ttl'):
                with self.subTest(provider=provider,suffix=suffix):
                    server,state,baseline=fixture(provider)
                    with server(state) as (origin,state):
                        result=invoke_capability([load(DATA/f'{provider}.{suffix}')],EVENT_CREATION,origin,VALUES)
                    self.assertTrue(result.http_ok)
                    self.assertIsNone(result.error_kind)
                    self.assertTrue(native_correct(provider,state,baseline,result.output))
                    self.assertNotIn('verified',asdict(result))
    def test_ordinary_invalid_inputs_never_mutate(self):
        invalid = [{}, dict(VALUES, extra=1), dict(VALUES,title=' '), dict(VALUES,title=5),
                   dict(VALUES,end_time=VALUES['start_time']),dict(VALUES,start_time='invalid'),
                   dict(VALUES,start_time='2030-01-07T10:00:00'),
                   dict(VALUES,start_time='2030-01-07T10:00:00.0000001Z')]
        for provider in 'ab':
            server,state,_=fixture(provider)
            with server(state) as (origin,state):
                for suffix in ('json','ttl'):
                    for values in invalid:
                        self.assertEqual(invoke(load(DATA/f'{provider}.{suffix}'),origin,values).error_kind,'input')
            self.assertEqual(state.calls,0)
    def test_provider_specific_limits_and_exact_precision(self):
        cases=[dict(VALUES,start_time='2030-01-07T10:05:00Z'),dict(VALUES,end_time='2030-01-07T13:00:00Z'),
               dict(VALUES,start_time='2030-01-07T10:00:00.000001Z'),dict(VALUES,title='x'*501)]
        for provider in 'ab':
            for suffix in ('json','ttl'):
                for values in cases:
                    server,state,_=fixture(provider)
                    with server(state) as (origin,state):
                        result=invoke(load(DATA/f'{provider}.{suffix}'),origin,values)
                    self.assertEqual(result.error_kind,'input' if provider=='b' else None)
                    self.assertEqual(state.calls,0 if provider=='b' else 1)
    def test_service_denial_and_error_reporting(self):
        for provider in 'ab':
            for suffix in ('json','ttl'):
                for permission,mode,code in ((False,'normal',403),(None,'normal',403),(True,'error',500 if provider=='a' else 503)):
                    server,state,baseline=fixture(provider,mode,permission)
                    with server(state) as (origin,state):
                        result=invoke(load(DATA/f'{provider}.{suffix}'),origin,VALUES)
                    self.assertEqual(result.error_kind,'http')
                    self.assertEqual(result.http_status,code)
                    self.assertFalse(result.http_ok)
                    self.assertEqual(state.calls,1)  # Service, not runtime permission reasoning.
                    self.assertEqual(state.events if provider=='a' else state.items,baseline)
    def test_http_success_is_not_independent_correctness(self):
        for provider in 'ab':
            for suffix in ('json','ttl'):
                for mode in ('no_change','mismatch','side_effect'):
                    server,state,baseline=fixture(provider,mode)
                    with server(state) as (origin,state):
                        result=invoke(load(DATA/f'{provider}.{suffix}'),origin,VALUES)
                    self.assertTrue(result.http_ok)
                    self.assertIsNone(result.error_kind)
                    self.assertFalse(native_correct(provider,state,baseline,result.output))
    def test_bad_output_reports_mapping_error_without_claiming_no_mutation(self):
        op=replace(load(DATA/'a.json'),output_mapping=(('id','absent_field','identity'),))
        server,state,_=fixture('a')
        with server(state) as (origin,state): result=invoke(op,origin,VALUES)
        self.assertTrue(result.http_ok)
        self.assertEqual(result.error_kind,'response_mapping')
        self.assertEqual(state.calls,1)
        self.assertIn('event-0001',state.events)
    def test_invalid_direct_description_and_origin(self):
        op=load(DATA/'a.json')
        for bad in (replace(op,method='DELETE'),replace(op,input_mapping=op.input_mapping+op.input_mapping)):
            self.assertEqual(invoke(bad,'http://127.0.0.1:1',VALUES).error_kind,'description')
        for origin in ('https://127.0.0.1:1','http://localhost:1','http://127.0.0.1:1/path','http://user@127.0.0.1:1'):
            self.assertEqual(invoke(op,origin,VALUES).error_kind,'input')
    def test_http_transport_errors_and_response_shape(self):
        from urllib.error import HTTPError, URLError
        from semantic_capability_v4.http import post
        op=load(DATA/'a.json')
        for raw in (b'not json', b'[]', b'"text"', b'\xff', b'x'*1000001):
            client=MagicMock(); response=client.open.return_value.__enter__.return_value
            response.status=201; response.read.return_value=raw
            with patch('semantic_capability_v4.http.build_opener',return_value=client):
                result=invoke(op,'http://127.0.0.1:1234',VALUES)
            self.assertEqual(result.error_kind,'response_mapping')
            self.assertTrue(result.http_ok)
            client.open.assert_called_once()
            args,kw=client.open.call_args
            self.assertEqual(args[0].method,'POST')
            self.assertEqual(kw['timeout'],5)
        for error,kind in ((HTTPError('url',307,'redirect',{},None),'http'),
                           (URLError('unreachable'),'transport')):
            client=MagicMock(); client.open.side_effect=error
            with patch('semantic_capability_v4.http.build_opener',return_value=client):
                result=invoke(op,'http://127.0.0.1:1234',VALUES)
            self.assertEqual(result.error_kind,kind)
            self.assertEqual(result.remote_outcome_unknown,kind=='transport')
            client.open.assert_called_once()
        client=MagicMock(); response=client.open.return_value.__enter__.return_value
        response.status=201; response.read.return_value=b'{"id": false}'
        with patch('semantic_capability_v4.http.build_opener',return_value=client):
            self.assertEqual(invoke(op,'http://127.0.0.1:1234',VALUES).error_kind,'response_mapping')

    def test_timeout_has_uncertain_outcome_no_retry_and_late_native_effect(self):
        server,state,baseline=fixture('a');release=Event();finished=Event()
        def observer(phase,path,status):
            if phase=='before': release.wait(8)
            else: finished.set()
        state.transition_observer=observer
        with server(state) as (origin,state):
            try:
                result=invoke(load(DATA/'a.json'),origin,VALUES)
                self.assertEqual(result.error_kind,'transport')
                self.assertTrue(result.remote_outcome_unknown)
                self.assertFalse(result.http_ok)
                self.assertEqual(state.pending_requests,1)
            finally: release.set()
            self.assertTrue(finished.wait(2))
        self.assertEqual(state.calls,1)
        self.assertTrue(native_correct('a',state,baseline,{'id':'event-0001'}))


if __name__=='__main__': unittest.main()
