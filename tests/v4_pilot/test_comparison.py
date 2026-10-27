"""Fairness, external native checks and operational controls for the V4 pilot."""
from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from api_local_v4 import a, b
from semantic_capability_v4.descriptions import load
from semantic_capability_v4.invoke import invoke
from semantic_capability_v4.model import InvocationResult
from v4_pilot.driver import ROOT, run_attempt
from v4_pilot.native import Snapshot, adjudicate, initial_records
from v4_pilot.tasks import BASE, catalogue

OUTPUT = Path(os.environ.get('V4_PILOT_FOCUSED_OUTPUT', ROOT / 'docs/artifacts/v4_pilot/focused'))


class BaselineFairness(unittest.TestCase):
    def test_same_validation_request_encoding_and_results(self):
        samples = [BASE, dict(BASE, title='Réunion ✓'), {}, dict(BASE, title=' '), dict(BASE, title='x'*501),
                   dict(BASE, start_time='2030-01-07T10:05:00Z'), dict(BASE, end_time='2030-01-07T13:00:00Z'),
                   dict(BASE, start_time='2030-01-07T10:00:00.000001Z'), dict(BASE, end_time=BASE['start_time'])]
        for provider, adapter in (('a', a), ('b', b)):
            for values in samples:
                responses, requests = [], []
                for condition in 'ABC':
                    captured = []
                    def http(origin, path, wire, operation_id):
                        captured.append(dict(path=path, values=wire))
                        return InvocationResult(operation_id, 201, True), {'id' if provider=='a' else 'booking_ref':'native-id'}
                    with patch('semantic_capability_v4.http.post', http):
                        if condition == 'A': result = adapter.invoke('http://127.0.0.1:1234', values)
                        else: result = invoke(load(ROOT / f'v4/descriptions/{provider}.{"json" if condition=="B" else "ttl"}'),
                                              'http://127.0.0.1:1234', values)
                    responses.append(asdict(result)); requests.append(captured)
                self.assertEqual(responses[0], responses[1]); self.assertEqual(responses[1], responses[2])
                self.assertEqual(requests[0], requests[1]); self.assertEqual(requests[1], requests[2])
    def test_local_adapter_needs_no_registry_or_descriptions(self):
        code = '''
import sys
class Block:
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'semantic_capability_v4.registry','semantic_capability_v4.descriptions'} or fullname.split('.')[0] in {'rdflib','semantic_action'}:
            raise ImportError('Baseline must not import '+fullname)
sys.meta_path.insert(0,Block())
from api_local_v4 import a,b
for adapter in (a,b):
    assert adapter.invoke('http://127.0.0.1:1',{}).error_kind=='input'
    assert adapter.invoke('http://127.0.0.1:1',{},'unsupported').error_kind=='resolution'
'''
        result = subprocess.run([sys.executable, '-S', '-c', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class NativeTruth(unittest.TestCase):
    def test_native_truth_is_independent_of_output_and_checks_preservation(self):
        for provider in 'ab':
            initial = initial_records(provider)
            before = Snapshot(provider, 'unused', deepcopy(initial), True, 0, 0)
            item = (dict(BASE, id='new') if provider=='a' else
                    dict(booking_ref='new', begins_ms=1894010400000, finishes_ms=1894014000000, label=BASE['title']))
            events = dict(initial, new=item)
            after = Snapshot(provider, 'unused', deepcopy(events), True, 1, 1)
            result = adjudicate(before, after, BASE, None)
            self.assertTrue(result['native_state_correct']); self.assertFalse(result['output_usable'])
            changed = deepcopy(events); changed['existing']['metadata'] = 'wrong'
            verdict = adjudicate(before, Snapshot(provider,'unused',changed,True,1,1),BASE,{'output':{'id':'new'}})
            self.assertTrue(verdict['unexpected_mutations']); self.assertFalse(verdict['native_state_correct'])
            item['title' if provider=='a' else 'label'] = 'wrong'
            verdict = adjudicate(before, Snapshot(provider,'unused',dict(initial,new=item),True,1,1),BASE,None)
            self.assertFalse(verdict['native_state_correct'])


class OperationalControls(unittest.TestCase):
    def test_positive_missing_output_and_timeout(self):
        tasks = {t['task_id']: t for t in catalogue()}
        for condition in 'ABC':
            for task_id in ('T01','T15','T16'):
                result = run_attempt(tasks[task_id], 'a', condition, OUTPUT / f'{task_id}-{condition}')
                self.assertTrue(result['diagnostic_passed'], result['summary'])
                if task_id=='T16':
                    self.assertFalse(result['creation_accepted'])
                    self.assertTrue(result['uncertain_remote_outcome_at_stop'])
                    self.assertFalse(result['process']['process_alive_after_stop'])
    def test_contaminated_resets_and_existing_trace_preserved(self):
        task = catalogue()[0]
        for axis in ('calls','records','permission','revision','pending','trace'):
            path = OUTPUT / ('reset-'+axis)
            result = run_attempt(task,'a','A',path,contamination=axis)
            self.assertEqual(result['status'],'RESET_REJECTED'); self.assertFalse(result['subject_launched'])
            self.assertFalse((path/'subject-input.json').exists())
        self.assertTrue(json.loads((OUTPUT/'reset-trace/previous-trace.json').read_text())['retained'])
        with self.assertRaises(FileExistsError): run_attempt(task,'a','A',OUTPUT/'reset-trace')
    def test_unsettled_state_is_never_accepted(self):
        task = catalogue()[-1]
        result = run_attempt(task,'a','A',OUTPUT/'unsettled',budget_seconds=.75,delay_seconds=3)
        self.assertTrue(result['state_uncertain_after_observation'])
        self.assertFalse(result['creation_accepted'])
        self.assertFalse(result['diagnostic_passed'])  # Deliberate extra control, not catalogue T16 timing.
        self.assertFalse(result['terminal_state_uncertain'])


if __name__=='__main__': unittest.main()
