"""Capability resolution parity on separate independently implemented services."""
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from rdflib import Literal, URIRef
from semantic_action.artifact import Scenario, serve
from semantic_action.contract import load_contract, load_goal
from semantic_action.model import Truth
from semantic_action.pipeline import Executor
from semantic_action.provider_b import BookingScenario, serve_bookings
from semantic_action.provider_contract import CAPABILITY, V, provider_graph, schema
from semantic_action.registry import Registration, Registry
from test_parity import Clock, FIXED, normalized

ROOT = Path(__file__).resolve().parents[2]


def semantic_result(result):
    result = json.loads(json.dumps(result))
    resolution = result['resolution']
    resolution.pop('run_id')
    resolution.pop('timestamp')
    for candidate in resolution['candidates']:
        candidate.pop('contract_sha256')
    if result['action'] is not None:
        result['action'] = normalized(result['action'])
    return result


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.goal = load_goal(ROOT/'contracts/goal.json')
        self.counter = 0
        for target,value in [('semantic_action.artifact.now',lambda: FIXED.isoformat()),
                             ('semantic_action.provider_b.now',lambda: FIXED.isoformat()),
                             ('semantic_action.pipeline.now',lambda: FIXED.isoformat()),
                             ('semantic_action.registry.now',lambda: FIXED.isoformat()),
                             ('semantic_action.oracle.datetime',Clock)]:
            context = patch(target,value)
            context.start()
            self.addCleanup(context.stop)

    def manual(self,name,suffix,mutate=None):
        path = ROOT/f'contracts/providers/{name}.{suffix}'
        if mutate is None:
            return path
        data = json.loads((ROOT/f'contracts/providers/{name}.json').read_text())
        mutate(data)
        path = self.output/f'{self.counter}-{name}.{suffix}'
        if suffix == 'json':
            path.write_text(json.dumps(data))
        else:
            provider_graph(data).serialize(destination=path,format='turtle')
        return path

    def run_pair(self,selected='b',options=None,goal=None,mutate=None,capability=CAPABILITY,selected_operation=None):
        results = []
        for suffix in ['json','ttl']:
            self.counter += 1
            with ExitStack() as stack:
                a,astate = stack.enter_context(serve())
                b,bstate = stack.enter_context(serve_bookings(BookingScenario(**(options or {}))))
                paths = [self.manual('a',suffix),self.manual('b',suffix,mutate)]
                registrations = [Registration(paths[0],a),Registration(paths[1],b)]
                registry = Registry(registrations)
                operation = ('https://example.org/provider-a#create_event' if selected == 'a'
                             else 'https://example.org/provider-b#reserveAppointment')
                operation = selected_operation or operation
                output = self.output/f'run-{self.counter}'
                result = registry.execute(goal or self.goal,operation,output,capability)
                persisted = json.loads((output/'resolution.json').read_text())
                self.assertEqual(persisted['selected_operation'],operation)
                if result['action']:
                    self.assertTrue((output/'action.json').exists())
                results.append((semantic_result(result),astate.calls,bstate.calls))
        self.assertEqual(*results)
        return results[0]

    def test_both_distinct_operation_names_resolve_and_verify(self):
        for selected in ['a','b']:
            with self.subTest(selected=selected):
                result,a,b = self.run_pair(selected=selected)
                self.assertTrue(all(c['eligible'] for c in result['resolution']['candidates']))
                self.assertTrue(result['action']['oracle_verdict']['achieved'])
                self.assertEqual((a,b),(1,0) if selected == 'a' else (0,1))
                if selected == 'b':
                    raw = result['action']['api_response']['raw_body']
                    self.assertIn('booking_ref',raw)
                    self.assertIn('wire_evidence',result['action'])

    def test_provider_b_execution_failure_controls(self):
        for mode in ['error','no_change','mismatch','side_effect']:
            with self.subTest(mode=mode):
                result,a,b = self.run_pair(options={'mode':mode})
                self.assertEqual((a,b),(0,1))
                self.assertFalse(result['action']['oracle_verdict']['achieved'])
                self.assertEqual(result['action']['api_call_success'],mode != 'error')

    def test_false_unknown_and_stale_preconditions_block(self):
        for options,expected in [({'can_book':False},Truth.FALSE),({'can_book':None},Truth.UNKNOWN),
                                 ({'stale_precondition':True},Truth.UNKNOWN)]:
            with self.subTest(options=options):
                result,a,b = self.run_pair(options=options)
                self.assertEqual((a,b),(0,0))
                self.assertIsNone(result['action'])
                self.assertEqual(result['resolution']['candidates'][1]['applicability'],expected)

    def test_stale_observations_fail_verification(self):
        result,a,b = self.run_pair(options={'stale_observation':True})
        self.assertEqual((a,b),(0,1))
        self.assertTrue(result['action']['api_call_success'])
        self.assertFalse(result['action']['oracle_verdict']['achieved'])

    def test_duration_and_grid_constraints_reject_only_incompatible_provider(self):
        for goal in [replace(self.goal,end_time='2027-05-31T12:00:00+00:00'),
                     replace(self.goal,start_time='2027-05-31T09:05:00+00:00')]:
            with self.subTest(goal=goal):
                result,a,b = self.run_pair(goal=goal)
                self.assertEqual((a,b),(0,0))
                candidates = result['resolution']['candidates']
                self.assertTrue(candidates[0]['eligible'])
                self.assertFalse(candidates[1]['compatible'])
                self.assertTrue(candidates[1]['reasons'])

    def test_input_precision_cannot_be_silently_lost(self):
        goal = replace(self.goal,start_time='2027-05-31T09:00:00.000001+00:00')
        result,a,b = self.run_pair(goal=goal)
        self.assertEqual((a,b),(0,0))
        self.assertIn('lose submillisecond',str(result['resolution']['candidates'][1]['reasons']))

    def test_missing_input_transformation_rejected(self):
        def mutate(data):
            data['binding']['request_fields']['begins_ms']['source'] = 'unavailable_field'
        result,a,b = self.run_pair(mutate=mutate)
        self.assertEqual((a,b),(0,0))
        self.assertIsNone(result['action'])
        self.assertIn('mapping',str(result['resolution']['candidates'][1]['reasons']))

    def test_similar_names_do_not_override_non_equivalent_effects(self):
        def mutate(data):
            data['operation_id'] = 'https://example.org/provider-b#create_event'
            data['declared_effects'] = ['https://example.org/sam/v1#ReservationRecorded']
        result,a,b = self.run_pair(mutate=mutate,selected_operation='https://example.org/provider-b#create_event')
        self.assertEqual((a,b),(0,0))
        self.assertIn('effects',str(result['resolution']['candidates'][1]['reasons']))
        self.assertIsNone(result['action'])

    def test_unknown_capability_and_mandatory_preservation_rejected(self):
        result,a,b = self.run_pair(capability='urn:unrelated:Capability')
        self.assertEqual((a,b),(0,0))
        self.assertFalse(any(c['compatible'] for c in result['resolution']['candidates']))
        def unknown(data):
            data['capability_id'] = 'urn:unrelated:Capability'
        result,a,b = self.run_pair(capability='urn:unrelated:Capability',mutate=unknown)
        self.assertEqual((a,b),(0,0))
        self.assertFalse(any(c['eligible'] for c in result['resolution']['candidates']))
        def mutate(data):
            data['constraints']['preserves_other_events'] = False
        result,a,b = self.run_pair(mutate=mutate)
        self.assertEqual((a,b),(0,0))
        self.assertIn('preservation',str(result['resolution']['candidates'][1]['reasons']))
        permitted,a,b = self.run_pair(mutate=mutate,goal=replace(self.goal,forbid_other_changes=False))
        self.assertTrue(permitted['action']['oracle_verdict']['achieved'])

    def test_execution_rechecks_permission_after_resolution(self):
        for suffix in ['json','ttl']:
            with self.subTest(suffix=suffix), serve_bookings() as (base,state):
                path = ROOT/f'contracts/providers/b.{suffix}'
                registry = Registry([Registration(path,base)])
                resolution = registry.resolve(self.goal)
                self.assertTrue(resolution['candidates'][0]['eligible'])
                state.can_book = None
                values = {k:getattr(self.goal,k) for k in ['start_time','end_time','title']}
                action = Executor(base).run(path,self.goal,values,self.output/f'recheck-{suffix}.json')
                self.assertEqual(state.calls,0)
                self.assertEqual(action['applicability'],Truth.UNKNOWN)

    def test_duplicate_operations_and_empty_registry_are_not_selections(self):
        with serve_bookings() as (base,state):
            registration = Registration(ROOT/'contracts/providers/b.json',base)
            registry = Registry([registration,registration])
            result = registry.execute(self.goal,'https://example.org/provider-b#reserveAppointment',self.output/'duplicate')
            self.assertEqual(state.calls,0)
            self.assertIsNone(result['action'])
            self.assertFalse(any(c['eligible'] for c in result['resolution']['candidates']))
        self.assertEqual(Registry([]).resolve(self.goal)['candidates'],[])

    def test_direct_pipeline_cannot_bypass_known_constraints(self):
        with serve_bookings() as (base,state):
            goal = replace(self.goal,end_time='2027-05-31T12:00:00+00:00')
            values = {k:getattr(goal,k) for k in ['start_time','end_time','title']}
            trace = Executor(base).run(ROOT/'contracts/providers/b.json',goal,values,self.output/'direct.json')
            self.assertEqual(trace['execution_decision'],'REJECT')
            self.assertEqual(state.calls,0)

    def test_provider_b_owns_its_constraint_enforcement(self):
        with serve_bookings() as (base,state):
            # Deliberately call the raw service to show it is not implemented by the manual.
            raw = Executor(base)._http_request('POST','/bookings',{'begins_ms':1,'finishes_ms':2,'label':'off grid'})
            self.assertEqual(raw.status,422)
            self.assertFalse(state.items)

    def test_v2_schema_and_models(self):
        Draft202012Validator.check_schema(schema())
        for name in ['a','b']:
            self.assertEqual(load_contract(ROOT/f'contracts/providers/{name}.json'),
                             load_contract(ROOT/f'contracts/providers/{name}.ttl'))
        for mutate in [lambda d:d['constraints'].update(extra_rule=True),
                       lambda d:d['binding'].update(response_id='booking_ref\n'),
                       lambda d:d['binding'].update(create_path='/bookings\n'),
                       lambda d:d['binding']['request_fields']['begins_ms'].update(transform='execute_code'),
                       lambda d:d['binding']['event_fields'].pop('end_time')]:
            for suffix in ['json','ttl']:
                self.counter += 1
                path = self.manual('b',suffix,mutate)
                with self.subTest(suffix=suffix),self.assertRaises(ValueError):
                    load_contract(path)

    def test_unsupported_extra_rdf_information_is_not_silently_dropped(self):
        graph = provider_graph(json.loads((ROOT/'contracts/providers/b.json').read_text()))
        graph.add((URIRef('urn:extra'),URIRef('urn:unsupported'),Literal(True)))
        path = self.output/'extra.ttl'
        graph.serialize(destination=path,format='turtle')
        with self.assertRaises(ValueError):
            load_contract(path)


if __name__ == '__main__':
    unittest.main()
