"""Runner/export behavior, including evidence integrity and repeated coverage."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from v4_pilot.experiment import run, summarize


class ExperimentTests(unittest.TestCase):
    def test_repetitions_exports_and_read_only_regeneration(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            p=Path(d)/'run'
            self.assertEqual(run(p,2,['T04']),0)
            inventory=json.loads((p/'raw/attempt-inventory.json').read_text())
            self.assertEqual(len(inventory),12)
            self.assertEqual({r['repetition'] for r in inventory},{1,2})
            self.assertEqual(len(json.loads((p/'raw/reset-controls.json').read_text())),12)
            self.assertTrue(all(r['summary']['post_attempts']==0 for r in inventory))
            before={str(f.relative_to(p)):f.read_bytes() for f in (p/'raw').rglob('*') if f.is_file()}
            first=(p/'derived/correctness.csv').read_bytes()
            self.assertEqual(summarize(p),0)
            self.assertEqual(first,(p/'derived/correctness.csv').read_bytes())
            self.assertEqual(before,{str(f.relative_to(p)):f.read_bytes() for f in (p/'raw').rglob('*') if f.is_file()})
            with self.assertRaises(FileExistsError):run(p,1,['T01'])
            (p/'raw/catalogue.json').write_text('[]')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):summarize(p)

    def test_harness_failures_are_retained_and_fail_summary(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            p=Path(d)/'run'
            with patch('v4_pilot.experiment.run_attempt',side_effect=RuntimeError('synthetic harness failure')):
                self.assertEqual(run(p,1,['T01']),1)
            rows=json.loads((p/'raw/attempt-inventory.json').read_text())
            self.assertEqual(len(rows),6)
            self.assertTrue(all('synthetic harness failure' in r['harness_error'] for r in rows))
            self.assertEqual(len(json.loads((p/'raw/reset-controls.json').read_text())),6)
            self.assertEqual(summarize(p),1)

    def test_invalid_selection_creates_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run'
            for reps,tasks in [(0,['T01']),(1,['T99']),(1,['T01','T01']),(1,[])]:
                with self.assertRaises(ValueError):run(p,reps,tasks)
                self.assertFalse(p.exists())


if __name__=='__main__':unittest.main()
