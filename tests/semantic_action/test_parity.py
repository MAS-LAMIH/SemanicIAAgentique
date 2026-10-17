"""Differential checks on separate fixtures; no serialization-specific executor."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from semantic_action.artifact import Scenario, serve
from semantic_action.contract import load_contract, load_goal, load_rdf_contract
from semantic_action.json_contract import load_json_contract
from semantic_action.model import ApiResult, Truth
from semantic_action.pipeline import Executor, evaluate_preconditions

ROOT = Path(__file__).resolve().parents[2]
TTL = ROOT / 'contracts/calendar.ttl'
JSON = ROOT / 'contracts/calendar.json'
SCHEMA = ROOT / 'src/semantic_action/schemas/contract-v1.schema.json'
FIXED = datetime(2030, 1, 1, tzinfo=timezone.utc)


class Clock(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED if tz else FIXED.replace(tzinfo=None)


def normalized(trace):
    """Keep every semantic field; drop only run metadata and evidence timestamps.

    Evidence contents, status, reasons, and oracle freshness verdicts are retained.
    Timestamp classification is checked by explicit expectations and boundary tests.
    """
    result = deepcopy(trace)
    for key in ('run_id', 'timestamp', 'completed_at', 'execution_started', 'contract_sha256'):
        result.pop(key, None)
    wrappers = [result.get('evidence', {}).get('baseline')]
    wrappers += [condition.get('evidence') for condition in result.get('preconditions', [])]
    observed = result.get('observed_effects') or {}
    wrappers += [observed.get('event'), observed.get('state')]
    for evidence in wrappers:
        if isinstance(evidence, dict):
            evidence.pop('observed_at', None)
    return json.loads(json.dumps(result))


class ParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.goal = load_goal(ROOT / 'contracts/goal.json')
        self.values = {k: getattr(self.goal, k) for k in ('start_time', 'end_time', 'title')}
        self.counter = 0
        for target, value in [('semantic_action.artifact.now', lambda: FIXED.isoformat()),
                              ('semantic_action.pipeline.now', lambda: FIXED.isoformat()),
                              ('semantic_action.oracle.datetime', Clock)]:
            context = patch(target, value)
            context.start()
            self.addCleanup(context.stop)

    def execute(self, manual, scenario, values=None, goal=None, baseline_transform=None):
        self.counter += 1
        # Deep copies are essential: the first execution must not seed the second.
        with serve(deepcopy(scenario)) as (base, state):
            executor = Executor(base)
            original = executor._request
            def request(method, path, values=None):
                result = original(method, path, values)
                return baseline_transform(result) if path == '/calendar' and baseline_transform else result
            with patch.object(executor, '_request', request):
                trace = executor.run(manual, goal or self.goal,
                                     self.values if values is None else deepcopy(values),
                                     self.output / f'{self.counter}.json')
            return normalized(trace), state.calls

    def assert_pair(self, scenario, decision, achieved, values=None, goal=None,
                    baseline_transform=None, paths=(TTL, JSON)):
        outcomes = [self.execute(path, scenario, values, goal, baseline_transform) for path in paths]
        self.assertEqual(outcomes[0], outcomes[1])
        trace, calls = outcomes[0]
        self.assertEqual(trace['execution_decision'], decision)
        self.assertEqual(calls, int(decision == 'EXECUTE'))
        actual = None if trace['oracle_verdict'] is None else trace['oracle_verdict']['achieved']
        self.assertEqual(actual, achieved)
        return trace

    def test_all_milestone_1_execution_scenarios(self):
        cases = [
            ('success', Scenario(), 'EXECUTE', True),
            ('not_writable', Scenario(writable=False), 'REJECT', None),
            ('unknown_writable', Scenario(writable=None), 'BLOCK', None),
            ('stale_precondition', Scenario(stale_precondition=True), 'BLOCK', None),
            ('execution_error', Scenario(mode='error'), 'EXECUTE', False),
            ('no_state_change', Scenario(mode='no_change'), 'EXECUTE', False),
            ('wrong_properties', Scenario(mode='mismatch'), 'EXECUTE', False),
            ('forbidden_side_effect', Scenario(mode='side_effect'), 'EXECUTE', False),
            ('stale_observation', Scenario(stale_observation=True), 'EXECUTE', False),
            ('preserved_event', Scenario(events={'old': {'id': 'old', 'title': 'Keep'}}), 'EXECUTE', True),
        ]
        for name, scenario, decision, achieved in cases:
            with self.subTest(name=name):
                self.assert_pair(scenario, decision, achieved)
        with self.subTest(name='goal_mismatch'):
            self.assert_pair(Scenario(), 'EXECUTE', False, goal=replace(self.goal, title='Other goal'))
        for key, value in [('start_time', '2027-05-31T08:00:00+00:00'),
                           ('end_time', '2027-05-31T11:00:00+00:00')]:
            with self.subTest(name='goal_mismatch_' + key):
                self.assert_pair(Scenario(), 'EXECUTE', False, goal=replace(self.goal, **{key: value}))
        with self.subTest(name='side_effect_permitted_by_goal'):
            self.assert_pair(Scenario(mode='side_effect'), 'EXECUTE', True,
                             goal=replace(self.goal, forbid_other_changes=False))

    def test_invalid_inputs_parity(self):
        for values in [
            {'title': 'Missing timestamps'},
            dict(self.values, end_time=self.values['start_time']),
            dict(self.values, start_time='2027-05-31T09:00:00'),
            dict(self.values, title=''), dict(self.values, title=1),
            dict(self.values, title='x' * 501), dict(self.values, extra=True),
            dict(self.values, end_time=None),
        ]:
            with self.subTest(values=values):
                self.assert_pair(Scenario(), 'REJECT', None, values=values)

    def test_missing_malformed_future_and_unavailable_evidence(self):
        for name in ['missing_writable', 'missing_timestamp', 'malformed_timestamp', 'future', 'unavailable']:
            def transform(result):
                body = deepcopy(result.body)
                if name == 'missing_writable':
                    body.pop('writable')
                elif name == 'missing_timestamp':
                    body.pop('observed_at')
                elif name == 'malformed_timestamp':
                    body['observed_at'] = 'not a timestamp'
                elif name == 'future':
                    body['observed_at'] = (FIXED + timedelta(seconds=1)).isoformat()
                else:
                    return ApiResult(503, {}, 'HTTP 503')
                return ApiResult(200, body)
            with self.subTest(name=name):
                trace = self.assert_pair(Scenario(), 'BLOCK', None, baseline_transform=transform)
                self.assertEqual(trace['applicability'], Truth.UNKNOWN)

    def test_invalid_contract_pairs_block_before_execution(self):
        pairs = [
            ('malformed', 'not valid Turtle', '{'),
            ('extra_assertion', TTL.read_text() + '\n<urn:extra> sam:path "/ignored" .',
             json.dumps(dict(json.loads(JSON.read_text()), ignored_constraint=True))),
            ('unknown_predicate', TTL.read_text() + '\n<urn:x> <urn:unknown> true .',
             json.dumps(dict(json.loads(JSON.read_text()), unknown=True))),
        ]
        data = json.loads(JSON.read_text())
        data['preconditions'].pop()
        pairs.append(('missing_precondition',
                      TTL.read_text().replace('sam:PositiveInterval, sam:CalendarWritable',
                                              'sam:PositiveInterval'), json.dumps(data)))
        for name, rdf_text, json_text in pairs:
            rdf, js = self.output / f'{name}.ttl', self.output / f'{name}.json'
            rdf.write_text(rdf_text)
            js.write_text(json_text)
            with self.subTest(name=name):
                results = [self.execute(path, Scenario()) for path in (rdf, js)]
                for trace, calls in results:
                    self.assertEqual((trace['execution_decision'], calls), ('BLOCK', 0))
                    self.assertIsNone(trace['oracle_verdict'])
                    self.assertTrue(trace['reason'])
                    # Parser diagnostics differ, but rejection is the same outcome.
                    trace['reason'] = 'contract_rejected'
                self.assertEqual(*results)

    def test_typed_models_and_nondefault_age_rules(self):
        self.assertEqual(load_rdf_contract(TTL), load_json_contract(JSON))
        for age in [0.5, 1, 30, 300]:
            rdf = self.output / f'age-{age}.ttl'
            rdf.write_text(TTL.read_text().replace('maxEvidenceAgeSeconds 30', f'maxEvidenceAgeSeconds {age}'))
            data = json.loads(JSON.read_text())
            data['observation']['max_evidence_age_seconds'] = age
            js = self.output / f'age-{age}.json'
            js.write_text(json.dumps(data))
            contracts = [load_contract(path) for path in (rdf, js)]
            self.assertEqual(*contracts)
            with self.subTest(age=age):
                self.assert_pair(Scenario(), 'EXECUTE', True, paths=(rdf, js))
            def old_baseline(result):
                return ApiResult(200, dict(result.body, observed_at=(FIXED - timedelta(seconds=1)).isoformat()))
            if age == 0.5:
                self.assert_pair(Scenario(), 'BLOCK', None, baseline_transform=old_baseline, paths=(rdf, js))
            if age == 300:
                self.assert_pair(Scenario(), 'EXECUTE', False,
                                 goal=replace(self.goal, max_evidence_age_seconds=0.5),
                                 baseline_transform=old_baseline, paths=(rdf, js))
            for seconds, expected in [(0, Truth.TRUE), (age, Truth.TRUE),
                                      (age + 0.01, Truth.UNKNOWN), (-1, Truth.UNKNOWN)]:
                evidence = {'writable': True, 'observed_at': (FIXED - timedelta(seconds=seconds)).isoformat()}
                outcomes = [evaluate_preconditions(c, self.values, evidence) for c in contracts]
                self.assertEqual(*outcomes)
                self.assertEqual(outcomes[0][1].verdict, expected)

    def test_identifiers_and_unordered_sets(self):
        data = json.loads(JSON.read_text())
        text = TTL.read_text()
        for field, original in [('artifact_id', 'calendar'), ('operation_id', 'createEvent'),
                                ('capability_id', 'EventCreation')]:
            data[field] = 'urn:parity:' + field
            text = text.replace('cal:' + original + ' ', '<' + data[field] + '> ')
        data['inputs'].reverse()
        data['preconditions'].reverse()
        rdf, js = self.output / 'identifiers.ttl', self.output / 'identifiers.json'
        rdf.write_text(text)
        js.write_text(json.dumps(data))
        self.assertEqual(load_contract(rdf), load_contract(js))
        self.assert_pair(Scenario(), 'EXECUTE', True, paths=(rdf, js))


class JsonValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.data = json.loads(JSON.read_text())
        self.schema = json.loads(SCHEMA.read_text())

    def test_schema_is_valid_and_example_conforms(self):
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.data)

    def test_all_required_fields_are_required(self):
        for name in self.data:
            data = deepcopy(self.data)
            del data[name]
            with self.subTest(name=name):
                self.assert_invalid(data)
        for parent in ['binding', 'observation']:
            for name in self.data[parent]:
                data = deepcopy(self.data)
                del data[parent][name]
                with self.subTest(parent=parent, name=name):
                    self.assert_invalid(data)

    def assert_invalid(self, data):
        path = self.output / 'bad.json'
        path.write_text(json.dumps(data))
        self.assertFalse(Draft202012Validator(self.schema).is_valid(data))
        with self.assertRaises(ValueError):
            load_json_contract(path)

    def test_unsupported_ambiguous_and_mistyped_fields(self):
        cases = [(['schema_version'], 2), (['schema_version'], True),
                 (['artifact_id'], ''), (['artifact_id'], 'relative-id'),
                 (['artifact_id'], 'urn:contains space'), (['artifact_id'], 'urn:trailing\n'),
                 (['operation_id'], None),
                 (['inputs'], ['title', 'title', 'end_time']),
                 (['preconditions'], []), (['preconditions'], ['urn:unknown']),
                 (['declared_effects'], ['urn:unknown']),
                 (['binding', 'method'], 'DELETE'), (['binding', 'path'], '/other'),
                 (['observation', 'path'], '/other'),
                 (['observation', 'max_evidence_age_seconds'], True)]
        cases += [(['observation', 'max_evidence_age_seconds'], v) for v in [0, -1, 301, '30', None]]
        for keys, value in cases:
            data = deepcopy(self.data)
            target = data
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value
            with self.subTest(keys=keys, value=value):
                self.assert_invalid(data)
        for parent in [None, 'binding', 'observation']:
            data = deepcopy(self.data)
            (data if parent is None else data[parent])['ignored_constraint'] = True
            with self.subTest(extra=parent):
                self.assert_invalid(data)
        for root in [None, [], 'contract', 1]:
            with self.subTest(root=root):
                self.assert_invalid(root)

    def test_duplicate_keys_nonfinite_and_malformed_json(self):
        text = JSON.read_text()
        cases = ['{', text.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
                 text.replace('"method": "POST"', '"method": "POST", "method": "POST"')]
        cases += [text.replace('"max_evidence_age_seconds": 30',
                               f'"max_evidence_age_seconds": {value}') for value in ['NaN', 'Infinity', '-Infinity', '1e999']]
        for index, text in enumerate(cases):
            path = self.output / f'bad-{index}.json'
            path.write_text(text)
            with self.subTest(index=index), self.assertRaises(ValueError):
                load_json_contract(path)

    def test_no_format_fallback(self):
        path = self.output / 'contract.txt'
        path.write_text(JSON.read_text())
        with self.assertRaises(ValueError):
            load_contract(path)

    def test_identity_aliases_use_shared_validator(self):
        # Distinct typed resources cannot alias in either representation.
        data = deepcopy(self.data)
        data['operation_id'] = data['artifact_id']
        path = self.output / 'alias.json'
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            load_json_contract(path)
        rdf = self.output / 'alias.ttl'
        rdf.write_text(TTL.read_text().replace('cal:createEvent ', 'cal:calendar '))
        with self.assertRaises(ValueError):
            load_rdf_contract(rdf)


if __name__ == '__main__':
    unittest.main()
