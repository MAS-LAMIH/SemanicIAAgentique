"""A/B/C correctness parity, mapping-independent observation and resource accounting."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import ast
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from semantic_action.contract import load_contract
from semantic_action.evaluation import run_case
from semantic_action.evaluation_tasks import proposed_tasks, task_sheet
from semantic_action.event_ledger import Event, Ledger
from semantic_action.model import Goal, now
from semantic_action.native_verifier import NativeExpectation, adjudicate, capture
from semantic_action.provider_b import BookingScenario

ROOT=Path(__file__).resolve().parents[2]


class ThreeConditionTests(unittest.TestCase):
    def test_all_twenty_diagnostics_on_visible_providers(self):
        with TemporaryDirectory() as directory:
            output=Path(directory)
            ledger=output/'runtime.jsonl'
            for task in proposed_tasks():
                for provider in ('a','b'):
                    results=[]
                    models=[]
                    for condition in ('A','B','C'):
                        with self.subTest(task=task.task_id,provider=provider,condition=condition):
                            path=output/f'{task.task_id}-{provider}-{condition}'
                            result=run_case(task,provider,condition,path,ROOT,ledger)
                            self.assertTrue(result['case_passed'],json.dumps(result['summary']))
                            results.append(result['summary'])
                            if condition in {'B','C'}:
                                models.append(load_contract(path/('manual.json' if condition=='B' else 'manual.ttl')))
                            if task.family=='wrong_mapping':
                                self.assertTrue(result['summary']['runtime_verified'])
                                self.assertFalse(result['summary']['native_verified'])
                                self.assertTrue(result['native_verdict']['runtime_discrepancy'])
                                self.assertTrue(result['native_verdict']['raw_after']['events'])
                    self.assertEqual(len(results),3)
                    self.assertEqual(results[0],results[1])
                    self.assertEqual(results[1],results[2])
                    self.assertEqual(*models)
            records=Ledger(ledger).records()
            self.assertEqual(len(records),120)
            self.assertEqual({r['event']['condition_id'] for r in records},{'A','B','C'})
            self.assertTrue(all(r['event']['human_active_minutes'] is None for r in records))

    def test_unsafe_mutation_attempt_is_not_hidden_by_goal_outcome(self):
        from unittest.mock import patch
        from semantic_action.local_baseline import LocalExecutor
        def bypass(client,local,goal,inputs,trace_path):
            response=client._http_request('POST',local.create_path,local.encode(inputs))
            return {'compatible':True,'applicability':'FALSE','api_call_success':response.success,
                    'oracle_verdict':{'achieved':False},'execution_started':now()}
        with TemporaryDirectory() as directory,patch.object(LocalExecutor,'run',bypass):
            result=run_case(proposed_tasks()[4],'a','A',Path(directory)/'unsafe',ROOT)
            self.assertTrue(result['summary']['unsafe_execution'])
            self.assertFalse(result['summary']['verified'])
            self.assertFalse(result['case_passed'])

    def test_no_semantic_discovery_imports_in_local_baseline(self):
        tree=ast.parse((ROOT/'src/semantic_action/local_baseline.py').read_text())
        imports={node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)}
        self.assertTrue(imports.isdisjoint({'registry','contract','provider_contract','transform','json_contract','pipeline'}))
        self.assertNotIn('https://example.org/sam/',(ROOT/'src/semantic_action/local_baseline.py').read_text())

    def test_task_sheet_is_provider_neutral_and_approval_pending(self):
        sheet=task_sheet()
        self.assertEqual(len(sheet['tasks']),20)
        self.assertEqual(sheet['status'],'proposal_pending_human_approval')
        self.assertEqual(sheet['provider_scope'],['a','b'])


class NativeVerifierTests(unittest.TestCase):
    def test_snapshot_deep_copy_and_native_extra_change_detection(self):
        state=BookingScenario(items={'old':{'booking_ref':'old','begins_ms':1894006800000,
                                             'finishes_ms':1894010400000,'label':'Keep','metadata':'stable'}})
        before=capture('b',state)
        state.items['old']['metadata']='changed'
        goal=Goal('2030-01-07T09:00:00+00:00','2030-01-07T10:00:00+00:00','New')
        state.items['new']={'booking_ref':'new',
                            'begins_ms':int(datetime.fromisoformat(goal.start_time).timestamp()*1000),
                            'finishes_ms':int(datetime.fromisoformat(goal.end_time).timestamp()*1000),'label':'New'}
        state.version=1
        state.calls=1
        after=capture('b',state)
        self.assertEqual(before.events['old']['metadata'],'stable')
        result=adjudicate(NativeExpectation(goal),before,after,before.observed_at)
        self.assertFalse(result['achieved'])
        self.assertIn('Forbidden native-state change',str(result['reasons']))

    def test_stale_native_evidence_never_establishes_truth(self):
        state=BookingScenario()
        before=capture('b',state)
        after=replace(before,observed_at='2000-01-01T00:00:00+00:00')
        goal=Goal('2030-01-07T09:00:00+00:00','2030-01-07T10:00:00+00:00','New')
        result=adjudicate(NativeExpectation(goal),before,after,before.observed_at)
        self.assertFalse(result['achieved'])

    def test_native_observer_has_no_subject_mapping_dependencies(self):
        tree=ast.parse((ROOT/'src/semantic_action/native_verifier.py').read_text())
        imports={node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)}
        self.assertTrue(imports.isdisjoint({'local_baseline','contract','provider_contract','transform','registry','pipeline'}))


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'events.jsonl'
        self.ledger=Ledger(self.path)

    def event(self,**changes):
        base=Event(contributor_id='test-person',activity='mapping',scope='provider_onboarding',resource_kind='human',
                   provider_id='a',condition_id='A',task_id='fixture-activity',
                   started_at='2030-01-01T09:00:00+00:00',ended_at='2030-01-01T09:10:00+00:00',
                   human_active_minutes=10,ai_supervision_minutes=4,measurement_source='synthetic test interval')
        return replace(base,**changes)

    def test_overlap_rejected_and_different_people_allowed(self):
        self.ledger.append(self.event())
        with self.assertRaisesRegex(ValueError,'Overlapping'):
            self.ledger.append(self.event(condition_id='B',provider_id='b'))
        self.ledger.append(self.event(contributor_id='second-person'))
        self.assertEqual(len(self.ledger.records()),2)

    def test_adjacent_intervals_and_automation_overlap_are_allowed(self):
        self.ledger.append(self.event())
        self.ledger.append(self.event(started_at='2030-01-01T09:10:00+00:00',ended_at='2030-01-01T09:20:00+00:00'))
        automated=self.event(resource_kind='automation',human_active_minutes=None,ai_supervision_minutes=None,
                             automated_runtime_minutes=10,condition_id='C')
        self.ledger.append(automated)
        self.assertEqual(self.ledger.summary()['resources']['human_active_minutes']['measured_total'],20)

    def test_corrections_append_and_do_not_double_count(self):
        first=self.event(outcome='failed')
        self.ledger.append(first)
        original=self.path.read_bytes()
        revised=self.event(human_active_minutes=8,supersedes=first.event_id,correction_reason='synthetic timer correction')
        self.ledger.append(revised)
        self.assertTrue(self.path.read_bytes().startswith(original))
        self.assertEqual(self.ledger.summary()['record_count'],2)
        self.assertEqual(self.ledger.summary()['current_record_count'],1)
        self.assertEqual(self.ledger.summary()['resources']['human_active_minutes']['measured_total'],8)
        with self.assertRaises(ValueError):
            self.ledger.append(self.event(supersedes=first.event_id,correction_reason='fork'))

    def test_unknown_stays_null_and_failed_attempt_links_rework(self):
        failed=Event(contributor_id='automation',activity='testing',scope='shared_setup',resource_kind='automation',
                     outcome='failed',measurement_source='synthetic test')
        self.ledger.append(failed)
        self.ledger.append(replace(failed,event_id='retry',activity='debugging',rework_of=failed.event_id,outcome='passed'))
        summary=self.ledger.summary()
        self.assertIsNone(summary['resources']['human_active_minutes']['measured_total'])
        self.assertEqual(self.ledger.records()[1]['event']['rework_of'],failed.event_id)

    def test_invalid_measurements_and_supervision_rejected(self):
        for changes in [{'human_active_minutes':float('nan')},{'human_active_minutes':True},
                        {'ai_supervision_minutes':11},{'resource_kind':'automation'},
                        {'human_active_minutes':11},{'started_at':None},
                        {'human_active_minutes':-1},{'condition_id':'provider-a'}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                self.ledger.append(self.event(**changes))
        self.assertFalse(self.path.exists())

    def test_chain_tampering_and_duplicate_ids_detected(self):
        event=self.event()
        self.ledger.append(event)
        with self.assertRaises(ValueError):
            self.ledger.append(event)
        text=self.path.read_text().replace('test-person','edited-person')
        self.path.write_text(text)
        with self.assertRaisesRegex(ValueError,'hash chain'):
            self.ledger.records()

    def test_cooperating_concurrent_writers_keep_one_valid_chain(self):
        from concurrent.futures import ThreadPoolExecutor
        def append(index):
            self.ledger.append(Event(contributor_id='worker',activity='execution',scope='task_execution',
                                     resource_kind='automation',task_id=str(index),measurement_source='synthetic concurrency test'))
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(append,range(12)))
        self.assertEqual(len(self.ledger.records()),12)

    def test_correction_cannot_create_overlap(self):
        first=self.event()
        self.ledger.append(first)
        self.ledger.append(self.event(started_at='2030-01-01T09:10:00+00:00',ended_at='2030-01-01T09:20:00+00:00'))
        with self.assertRaisesRegex(ValueError,'Overlapping'):
            self.ledger.append(self.event(started_at='2030-01-01T09:05:00+00:00',ended_at='2030-01-01T09:15:00+00:00',
                                          supersedes=first.event_id,correction_reason='bad correction'))


if __name__=='__main__':
    unittest.main()
