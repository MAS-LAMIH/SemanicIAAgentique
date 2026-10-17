from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from semantic_action.artifact import Scenario, serve
from semantic_action.contract import load_contract, load_goal
from semantic_action.cost import WorkEntry, log_work
from semantic_action.model import Goal, Observation, Truth, now
from semantic_action.oracle import verify
from semantic_action.pipeline import Executor

ROOT = Path(__file__).resolve().parents[2]
MANUAL = ROOT / 'contracts/calendar.ttl'
GOAL = ROOT / 'contracts/goal.json'


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.goal = load_goal(GOAL)
        self.inputs = {k: getattr(self.goal, k) for k in ('start_time', 'end_time', 'title')}

    def run_action(self, scenario=None, values=None, goal=None, manual=MANUAL):
        with serve(scenario) as (base, state):
            result = Executor(base).run(manual, goal or self.goal,
                                        self.inputs if values is None else values,
                                        self.output / 'trace.json')
            self.assertEqual(json.loads((self.output / 'trace.json').read_text())['run_id'],
                             result['run_id'])
            return result, state

    def test_valid_action(self):
        trace, state = self.run_action()
        self.assertEqual(trace['applicability'], Truth.TRUE)
        self.assertEqual(state.calls, 1)
        self.assertTrue(trace['api_call_success'])
        self.assertTrue(trace['observed_state_change'])
        self.assertTrue(trace['oracle_verdict']['achieved'])
        self.assertIn('NewMatchingEvent', trace['declared_effects'][0])
        self.assertIn('state', trace['observed_effects'])

    def test_invalid_interval(self):
        values = dict(self.inputs, end_time=self.inputs['start_time'])
        trace, state = self.run_action(values=values)
        self.assertEqual((trace['execution_decision'], state.calls), ('REJECT', 0))
        self.assertEqual(trace['applicability'], Truth.FALSE)

    def test_invalid_missing_input(self):
        trace, state = self.run_action(values={'title': 'No times'})
        self.assertEqual((trace['execution_decision'], state.calls), ('REJECT', 0))

    def test_invalid_naive_timestamp(self):
        trace, state = self.run_action(values=dict(self.inputs, start_time='2027-05-31T09:00:00'))
        self.assertEqual((trace['execution_decision'], state.calls), ('REJECT', 0))

    def test_not_writable(self):
        trace, state = self.run_action(Scenario(writable=False))
        self.assertEqual(trace['applicability'], Truth.FALSE)
        self.assertEqual((trace['execution_decision'], state.calls), ('REJECT', 0))

    def test_unknown_writable(self):
        trace, state = self.run_action(Scenario(writable=None))
        self.assertEqual(trace['applicability'], Truth.UNKNOWN)
        self.assertEqual((trace['execution_decision'], state.calls), ('BLOCK', 0))

    def test_stale_writability(self):
        trace, state = self.run_action(Scenario(stale_precondition=True))
        self.assertEqual(trace['applicability'], Truth.UNKNOWN)
        self.assertEqual(state.calls, 0)

    def test_execution_error(self):
        trace, state = self.run_action(Scenario(mode='error'))
        self.assertEqual(state.calls, 1)
        self.assertEqual(trace['api_response']['status'], 500)
        self.assertFalse(trace['api_call_success'])
        self.assertFalse(trace['oracle_verdict']['achieved'])

    def test_success_without_state_change(self):
        trace, _ = self.run_action(Scenario(mode='no_change'))
        self.assertTrue(trace['api_call_success'])
        self.assertFalse(trace['observed_state_change'])
        self.assertFalse(trace['oracle_verdict']['achieved'])

    def test_mismatched_observation(self):
        trace, _ = self.run_action(Scenario(mode='mismatch'))
        self.assertTrue(trace['api_call_success'])
        self.assertFalse(trace['oracle_verdict']['achieved'])
        self.assertIn('Goal mismatch: title', trace['reason'])

    def test_forbidden_side_effect(self):
        trace, _ = self.run_action(Scenario(mode='side_effect'))
        self.assertFalse(trace['oracle_verdict']['achieved'])
        self.assertIn('Forbidden', trace['reason'])

    def test_preexisting_event_preserved(self):
        existing = {'old': {'id': 'old', 'title': 'Keep'}}
        trace, _ = self.run_action(Scenario(events=existing))
        self.assertTrue(trace['oracle_verdict']['achieved'])
        self.assertEqual(existing['old'], {'id': 'old', 'title': 'Keep'})

    def test_stale_observation(self):
        trace, _ = self.run_action(Scenario(stale_observation=True))
        self.assertTrue(trace['api_call_success'])
        self.assertFalse(trace['oracle_verdict']['achieved'])
        self.assertIsNone(trace['observed_state_change'])

    def test_goal_is_independent_of_inputs(self):
        trace, _ = self.run_action(goal=replace(self.goal, title='Different formal goal'))
        self.assertTrue(trace['api_call_success'])
        self.assertFalse(trace['oracle_verdict']['achieved'])

    def test_unknown_contract_assertion_fails_closed(self):
        manual = self.output / 'unsupported.ttl'
        manual.write_text(MANUAL.read_text() + '\n<urn:test> <urn:mandatoryConstraint> true .')
        trace, state = self.run_action(manual=manual)
        self.assertEqual((trace['execution_decision'], state.calls), ('BLOCK', 0))
        self.assertIn('Unsupported', trace['reason'])

    def test_missing_critical_precondition_fails_closed(self):
        manual = self.output / 'missing.ttl'
        manual.write_text(MANUAL.read_text().replace('sam:PositiveInterval, sam:CalendarWritable',
                                                   'sam:PositiveInterval'))
        trace, state = self.run_action(manual=manual)
        self.assertEqual((trace['execution_decision'], state.calls), ('BLOCK', 0))

    def test_manual_cannot_override_oracle(self):
        # The oracle has no contract parameter and requires actual evidence.
        verdict = verify(self.goal, None, Observation(None, None), 'invented', now())
        self.assertFalse(verdict.achieved)

    def test_malformed_contract_traced_and_blocked(self):
        manual = self.output / 'broken.ttl'
        manual.write_text('this is not valid turtle')
        trace, state = self.run_action(manual=manual)
        self.assertEqual((trace['execution_decision'], state.calls), ('BLOCK', 0))
        self.assertIn('Malformed', trace['reason'])

    def test_disconnected_constraints_rejected(self):
        manual = self.output / 'extra.ttl'
        manual.write_text(MANUAL.read_text() + '\n<urn:extra> sam:path "/ignored" .')
        trace, state = self.run_action(manual=manual)
        self.assertEqual((trace['execution_decision'], state.calls), ('BLOCK', 0))
        self.assertIn('Extra assertions', trace['reason'])

    def test_replayed_oracle_evidence_rejected(self):
        old = '2000-01-01T00:00:00+00:00'
        verdict = verify(self.goal, {'observed_at': old},
                         Observation({'observed_at': old}, {'observed_at': old}), 'id', now())
        self.assertFalse(verdict.achieved)

    def test_remote_executor_disallowed(self):
        with self.assertRaises(ValueError):
            Executor('https://example.org')

    def test_contract_and_goal_load(self):
        self.assertEqual(load_contract(MANUAL).method, 'POST')
        self.assertEqual(self.goal.title, 'Semantic interoperability meeting')

    def test_work_log_unknown_measurements(self):
        path = self.output / 'work.jsonl'
        log_work(path, WorkEntry('mapping', 'human', ai_assistance_used=True))
        log_work(path, WorkEntry('validation', 'runner', elapsed_minutes=0.5))
        entries = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertIsNone(entries[0]['elapsed_minutes'])
        self.assertTrue(entries[0]['ai_assistance_used'])
        self.assertEqual(entries[1]['elapsed_minutes'], 0.5)


if __name__ == '__main__':
    unittest.main()
