"""Bounded chains, representation parity, trusted native truth and real process stops."""
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timezone
import ast
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from semantic_action.artifact import Scenario, serve
from semantic_action.provider_b import BookingScenario, serve_bookings
from semantic_action.model import Goal, Truth, now
from semantic_action.native_verifier import capture, NativeSnapshot
from semantic_action.sequence import SequencePlan, SequenceExecutor, dependency
from semantic_action.sequence_bindings import load_shared, LocalSequenceBinding
from semantic_action.sequence_native import ChainExpectation, verify_chain
from semantic_action.multistep_tasks import pilot_tasks
from semantic_action.multistep_evaluation import run_pilot, initial_records
from semantic_action.supervision import supervise, assert_reset
from semantic_action.transport import HTTPTransport
from semantic_action.event_ledger import Ledger

ROOT = Path(__file__).resolve().parents[2]


class MultiStepTests(unittest.TestCase):
    def test_all_scenarios_three_conditions_visible_providers(self):
        with TemporaryDirectory() as directory:
            for task in pilot_tasks():
                for provider in ('a', 'b'):
                    results = []
                    for condition in ('A', 'B', 'C'):
                        with self.subTest(task=task.task_id, provider=provider, condition=condition):
                            result = run_pilot(task, provider, condition, Path(directory) / f'{task.task_id}-{provider}-{condition}', ROOT)
                            results.append(result['summary'])
                            self.assertTrue(result['diagnostic_passed'], json.dumps(result.get('summary', result)))
                            self.assertTrue(result['reset']['passed'])
                            self.assertTrue(result['fixture_server_closed'])
                            self.assertFalse(result['process']['process_alive_after_stop'])
                            if task.family == 'dependency':
                                self.assertEqual(result['runtime_trace']['steps'][1]['dependency_verdict'], 'TRUE')
                                native = result['native_journal']
                                self.assertEqual(len(native), 2)
                                first_new = set(native[0]['after']['events']) - set(native[0]['before']['events'])
                                second_new = set(native[1]['after']['events']) - set(native[1]['before']['events'])
                                link = 'predecessor_id' if provider == 'a' else 'previous_booking'
                                self.assertEqual(native[1]['after']['events'][next(iter(second_new))][link], next(iter(first_new)))
                            if task.family == 'recovery_boundary':
                                self.assertFalse(result['recovery_boundary']['resume_performed'])
                                self.assertEqual(result['recovery_boundary']['calls_after_recovery'], 2)
                                self.assertEqual(len(result['runtime_trace']['steps']), 2)
                            if task.family in {'permission_revoked', 'unknown_permission', 'stale_permission'}:
                                self.assertEqual(len(result['native_journal']), 1)
                                self.assertEqual(result['summary']['partial_new_records'], 1)
                    self.assertEqual(results[0], results[1])
                    self.assertEqual(results[1], results[2])

    def test_service_enforces_dependency_without_sequence_guard(self):
        for provider in ('a', 'b'):
            state = Scenario() if provider == 'a' else BookingScenario()
            server = serve if provider == 'a' else serve_bookings
            with server(state) as (origin, fixture):
                client = HTTPTransport(origin)
                if provider == 'a':
                    values = {'start_time': '2030-01-07T10:00:00+00:00', 'end_time': '2030-01-07T11:00:00+00:00', 'title': 'Follow-up'}
                    create, dependent, storage, id_key = '/events', '/followups/', fixture.events, 'id'
                else:
                    values = {'begins_ms': 1894010400000, 'finishes_ms': 1894014000000, 'label': 'Follow-up'}
                    create, dependent, storage, id_key = '/bookings', '/booking-after/', fixture.items, 'booking_ref'
                self.assertEqual(client._http_request('POST', dependent + 'absent', values).status, 409)
                self.assertFalse(storage)
                created = client._http_request('POST', create, values)
                prior = created.body[id_key]
                # Same interval overlaps predecessor; existence alone does not suffice.
                self.assertEqual(client._http_request('POST', dependent + prior, values).status, 409)
                self.assertEqual(len(storage), 1)

    def test_sequence_profile_json_rdf_typed_parity(self):
        for provider in ('a', 'b'):
            one, _ = load_shared(ROOT / f'contracts/sequences/{provider}.json', ROOT)
            two, _ = load_shared(ROOT / f'contracts/sequences/{provider}.ttl', ROOT)
            self.assertEqual(one, two)

    def test_closed_profile_rejects_missing_unknown_and_ambiguous_fields(self):
        from rdflib import Graph, Literal, Namespace, RDF
        with TemporaryDirectory() as directory:
            target = Path(directory) / 'bad.json'
            data = json.loads((ROOT / 'contracts/sequences/a.json').read_text())
            for change in (lambda d: d.pop('requires_predecessor'), lambda d: d.update(extra=True),
                           lambda d: d.update(requires_after_end=False), lambda d: d.update(version=True),
                           lambda d: d.update(base_manual='../outside'), lambda d: d.update(create_path_template='https://elsewhere/{id}')):
                modified = deepcopy(data); change(modified); target.write_text(json.dumps(modified))
                with self.assertRaises(ValueError):
                    load_shared(target, ROOT)
            target.write_text('{"version":1,"version":1}')
            with self.assertRaises(ValueError):
                load_shared(target, ROOT)
            graph = Graph().parse(ROOT / 'contracts/sequences/a.ttl', format='turtle')
            ns = Namespace('https://example.org/sam/sequence/v1#')
            node = next(graph.subjects(RDF.type, ns.Profile))
            graph.add((node, ns.effect, Literal('ReservationOnly')))
            target = Path(directory) / 'bad.ttl'; graph.serialize(destination=target, format='turtle')
            with self.assertRaises(ValueError):
                load_shared(target, ROOT)

    def test_unknown_dependency_and_stale_evidence_block(self):
        goals = pilot_tasks()[0].domain_goals()
        for evidence in (None, {}, {'observed_at': '2000-01-01T00:00:00+00:00', 'events': {}},
                         {'observed_at': now(), 'events': {'x': {'id': 'x'}}}):
            self.assertEqual(dependency(goals[1], goals[0], 'x', evidence, '2000-01-01T00:00:00+00:00')[0], Truth.UNKNOWN)
        self.assertEqual(dependency(goals[1], goals[0], 'x', {'observed_at': now(), 'events': {}},
                                    '2000-01-01T00:00:00+00:00')[0], Truth.FALSE)

    def test_finite_profile_rejects_unsupported_plan_before_execution(self):
        goals = pilot_tasks()[0].domain_goals()
        for items in ((), goals[:1], goals + goals, [*goals], (goals[1], goals[0])):
            with self.assertRaises(ValueError):
                SequencePlan(items)
        with self.assertRaises(ValueError):
            SequencePlan((replace(goals[0], forbid_other_changes=False), goals[1]))

    def test_required_action_never_skipped_even_if_goal_looks_true(self):
        class RefusingBinding:
            compatible = True
            def execute(self, *args):
                self.calls += 1
                return {'execution_decision': 'EXECUTE', 'oracle_verdict': {'achieved': False}, 'api_call_success': True}
            calls = 0
        binding = RefusingBinding()
        with TemporaryDirectory() as directory:
            result = SequenceExecutor().run(SequencePlan(pilot_tasks()[0].domain_goals()), binding, directory)
            self.assertEqual(binding.calls, 1)
            self.assertFalse(result['runtime_verified'])
            self.assertEqual(result['status'], 'INCOMPLETE')

    def test_local_binding_has_no_semantic_discovery_imports(self):
        import inspect
        source = inspect.getsource(LocalSequenceBinding)
        local_imports = {n.module for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ImportFrom)}
        self.assertTrue(local_imports.isdisjoint({'registry', 'provider_contract', 'contract', 'transform', 'rdflib'}))
        tree = ast.parse((ROOT / 'src/semantic_action/sequence_native.py').read_text())
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertTrue(imports.isdisjoint({'sequence_bindings', 'sequence', 'pipeline', 'transform', 'registry'}))


class OperationalTests(unittest.TestCase):
    def test_timeout_kills_stalled_process_and_preserves_costs(self):
        with TemporaryDirectory() as directory:
            output = Path(directory); ledger = output / 'cost.jsonl'
            result = supervise([sys.executable, '-c', 'import time; time.sleep(30)'], output, 0.15, ledger)
            self.assertEqual(result['status'], 'TIMEOUT')
            self.assertFalse(result['process_alive_after_stop'])
            self.assertFalse(result['remote_side_effect_cancellation_claimed'])
            self.assertEqual(len(Ledger(ledger).records()), 1)
            self.assertIsNone(Ledger(ledger).records()[0]['event']['human_active_minutes'])

    def test_inflight_timeout_observes_late_state_without_claiming_success(self):
        with TemporaryDirectory() as directory:
            # Test all conditions; server delay exceeds outer budget but remains observable.
            for condition in ('A', 'B', 'C'):
                result = run_pilot(pilot_tasks()[0], 'b', condition, Path(directory) / condition, ROOT,
                                   budget_seconds=1.0, delay_followup_seconds=1.5)
                self.assertEqual(result['summary']['supervision_status'], 'TIMEOUT')
                self.assertFalse(result['summary']['verified'])
                self.assertFalse(result['process']['process_alive_after_stop'])
                self.assertTrue(result['recovery']['settled'])
                self.assertEqual(result['recovery']['pending_at_stop'], 1)
                self.assertTrue(result['native_verdict']['achieved'])
                self.assertEqual(result['summary']['mutation_calls'], 2)
                self.assertTrue(result['diagnostic_passed'])
                self.assertTrue((Path(directory) / condition / 'step-1/action.json').is_file())

    def test_contaminated_reset_rejects_before_subject_launch(self):
        with TemporaryDirectory() as directory:
            result = run_pilot(pilot_tasks()[0], 'a', 'A', Path(directory) / 'bad', ROOT, contaminate=True)
            self.assertEqual(result['status'], 'RESET_REJECTED')
            self.assertFalse(result['subject_launched'])
            self.assertFalse((Path(directory) / 'bad/subject-input.json').exists())

    def test_each_reset_axis_detects_contamination(self):
        from dataclasses import replace
        native = capture('a', Scenario())
        expected = {'events': {}, 'writable': True, 'revision': 0, 'mutation_calls': 0}
        with TemporaryDirectory() as directory:
            for key, value in (('events', {'leak': {}}), ('writable', None), ('revision', 1), ('mutation_calls', 1)):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    assert_reset(replace(native, **{key: value}), expected, Path(directory) / 'reset.json', 0, False, True, 0)
            for cache, alive, clean, pending in ((1, False, True, 0), (0, True, True, 0), (0, False, False, 0), (0, False, True, 1)):
                with self.assertRaises(ValueError):
                    assert_reset(native, expected, Path(directory) / 'reset.json', cache, alive, clean, pending)

    def test_repetitions_have_equivalent_clean_state_and_distinct_processes(self):
        with TemporaryDirectory() as directory:
            results = [run_pilot(pilot_tasks()[0], 'a', condition, Path(directory) / f'{repeat}-{condition}', ROOT)
                       for repeat in range(2) for condition in ('A', 'B', 'C')]
            self.assertEqual(len({r['process']['pid'] for r in results}), 6)
            for result in results:
                self.assertTrue(result['reset']['passed'])
                self.assertEqual(result['reset']['native_initial']['events'], initial_records('a'))
                self.assertEqual(result['reset']['native_initial']['mutation_calls'], 0)
                self.assertEqual(result['summary'], results[0]['summary'])

    def test_transport_failure_is_distinct_from_outer_timeout(self):
        with TemporaryDirectory() as directory:
            result = supervise([sys.executable, '-c', 'raise SystemExit(7)'], directory, 1)
            self.assertEqual(result['status'], 'PROCESS_ERROR')
            self.assertNotEqual(result['status'], 'TIMEOUT')
            self.assertEqual(result['exit_code'], 7)

    def test_http_timeout_is_distinct_from_outer_timeout(self):
        with TemporaryDirectory() as directory:
            result = run_pilot(pilot_tasks()[0], 'a', 'A', Path(directory) / 'transport-timeout', ROOT,
                               budget_seconds=60, delay_followup_seconds=5.2)
            self.assertEqual(result['summary']['supervision_status'], 'COMPLETED')
            self.assertEqual(result['summary']['status'], 'INCOMPLETE')
            self.assertFalse(result['summary']['runtime_verified'])
            self.assertFalse(result['summary']['verified'])
            response = result['runtime_trace']['steps'][1]['action']['api_response']
            self.assertIsNone(response['status'])
            self.assertIn('timed out', response['error'])
            self.assertTrue(result['recovery']['settled'])
            self.assertTrue(result['native_verdict']['achieved'])

    def test_unsettled_service_remains_uncertain(self):
        from semantic_action.supervision import settle_and_capture
        class Pending:
            pending_requests = 1
        recovery = settle_and_capture(Pending(), lambda: {'partial': True}, maximum_wait_seconds=0.01)
        self.assertFalse(recovery['settled'])
        self.assertTrue(recovery['state_uncertain'])
        self.assertEqual(recovery['snapshot'], {'partial': True})

    def test_invalid_budget_and_existing_trace_reject(self):
        with TemporaryDirectory() as directory:
            for value in (0, -1, float('nan'), True):
                with self.assertRaises(ValueError):
                    supervise([sys.executable, '-c', 'pass'], directory, value)
            Path(directory, 'supervision.json').write_text('{}')
            with self.assertRaises(FileExistsError):
                supervise([sys.executable, '-c', 'pass'], directory, 1)


class SequenceNativeTests(unittest.TestCase):
    def test_missing_required_transition_never_verifies(self):
        goals = pilot_tasks()[0].domain_goals()
        state = Scenario()
        native = capture('a', state)
        result = verify_chain(ChainExpectation(goals, {}), native, native, [])
        self.assertFalse(result['achieved'])
        self.assertEqual(result['verified_transition_count'], 0)

    def test_wrong_relation_and_raw_preservation_fail(self):
        with TemporaryDirectory() as directory:
            result = run_pilot(pilot_tasks()[0], 'a', 'A', Path(directory) / 'valid', ROOT)
            transitions = deepcopy(result['native_journal'])
            initial = NativeSnapshot(**transitions[0]['before'])
            final = NativeSnapshot(**transitions[-1]['after'])
            expectation = ChainExpectation(pilot_tasks()[0].domain_goals(), initial.events)
            self.assertTrue(verify_chain(expectation, initial, final, transitions)['achieved'])
            created = set(transitions[1]['after']['events']) - set(transitions[1]['before']['events'])
            transitions[1]['after']['events'][next(iter(created))]['predecessor_id'] = 'wrong'
            wrong_final = NativeSnapshot(**transitions[-1]['after'])
            self.assertFalse(verify_chain(expectation, initial, wrong_final, transitions)['achieved'])
            transitions = deepcopy(result['native_journal'])
            transitions[1]['after']['events']['existing']['metadata'] = 'corrupt'
            self.assertFalse(verify_chain(expectation, initial, NativeSnapshot(**transitions[-1]['after']), transitions)['achieved'])

    def test_oracle_expectation_not_supplied_by_runtime_trace(self):
        with TemporaryDirectory() as directory:
            result = run_pilot(pilot_tasks()[0], 'b', 'B', Path(directory) / 'valid', ROOT)
            wrong = tuple(replace(g, title='Independent different requirement') for g in pilot_tasks()[0].domain_goals())
            journal = result['native_journal']
            verdict = verify_chain(ChainExpectation(wrong, journal[0]['before']['events']),
                                   NativeSnapshot(**journal[0]['before']), NativeSnapshot(**journal[-1]['after']), journal)
            self.assertTrue(result['runtime_trace']['runtime_verified'])
            self.assertFalse(verdict['achieved'])


if __name__ == '__main__':
    unittest.main()
