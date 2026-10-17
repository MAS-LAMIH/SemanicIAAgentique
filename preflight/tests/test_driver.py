"""Focused operational controls, separate from the 87 frozen tests."""
import json
import os
from pathlib import Path
import unittest
from preflight.driver import ROOT, run
from semantic_action.evaluation_tasks import proposed_tasks
from semantic_action.multistep_tasks import pilot_tasks

AREA=Path(os.environ.get('PREFLIGHT_FOCUSED_OUTPUT', ROOT/'docs/artifacts/milestone4_5/focused'))
TASKS={t.task_id:t for t in (*proposed_tasks(),*pilot_tasks())}
class Controls(unittest.TestCase):
    def attempt(self, label, task='D01', condition='A', **kw):
        return run(TASKS[task], 'a', condition, AREA/label, **kw)
    def test_normal_and_negative(self):
        for task in ('D01','D05','D06','D07','D08','D13','D14','D15','D16','D17','D18','M01','M03','M04','M09'):
            for c in 'ABC':
                with self.subTest(task=task,condition=c):
                    self.assertTrue(self.attempt(task+'-'+c,task,c)['diagnostic_passed'])
    def test_reset_axes(self):
        for axis in ('calls','revision','permission','records','pending','trace'):
            result=self.attempt('reset-'+axis,contaminate=axis)
            self.assertEqual(result['status'],'RESET_REJECTED')
            self.assertFalse(result['subject_launched'])
        result=self.attempt('multi-reset',task='M01',contaminate='calls')
        self.assertEqual(result['status'],'RESET_REJECTED')
    def test_timeouts_and_uncertainty(self):
        for c in 'ABC':
            for task in ('D01','M01'):
                result=self.attempt('late-'+task+'-'+c,task,c,budget=1,delay=1.5)
                self.assertEqual(result['process']['status'],'TIMEOUT')
                self.assertFalse(result['process']['process_alive_after_stop'])
                self.assertFalse(result['summary']['verified'])
                self.assertGreater(result['summary']['mutation_calls'],0)
            result=self.attempt('uncertain-'+c,condition=c,budget=.75,delay=3)
            self.assertTrue(result['recovery']['state_uncertain'])
            self.assertFalse(result['summary']['verified'])
            self.assertFalse(json.loads((AREA/('uncertain-'+c)/'terminal-observation.json').read_text())['state_uncertain'])
    def test_fresh_paths(self):
        a=self.attempt('fresh-1'); b=self.attempt('fresh-2')
        self.assertNotEqual(a['process']['pid'],b['process']['pid'])
        with self.assertRaises(FileExistsError): self.attempt('fresh-1')
        self.assertTrue(json.loads((AREA/'fresh-1/reset.json').read_text())['passed'])
    def test_provider_restriction(self):
        with self.assertRaises(ValueError): run(TASKS['D01'],'z','A',AREA/'not-launched')

if __name__=='__main__': unittest.main()
