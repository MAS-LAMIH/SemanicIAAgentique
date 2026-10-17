"""Prospective apparatus tasks, authored from formal domain predicates, not manuals.

These public A/B diagnostics are not sealed held-out tasks or the full E1 pilot.
The frozen protocol's multi-step cases require a later supported goal fragment.
"""
from dataclasses import asdict, dataclass, replace
from .model import Goal

FAMILIES=('valid_match','different_names','different_formats','misleading_effect',
          'false_precondition','unknown_precondition','stale_permission','missing_permission',
          'unsupported_transform','precision_loss','unsupported_transition','api_error',
          'no_state_change','wrong_properties','wrong_mapping','forbidden_side_effect',
          'stale_observation','missing_observation','duration_constraint','grid_constraint')


@dataclass(frozen=True)
class DiagnosticTask:
    task_id: str
    family: str
    goal: Goal

    def expectation(self,provider):
        if provider not in {'a','b'}:
            raise ValueError('Only visible controlled providers are supported')
        rejected=self.family in {'misleading_effect','false_precondition','unknown_precondition',
            'stale_permission','missing_permission','unsupported_transform','unsupported_transition'}
        rejected=rejected or (provider=='b' and self.family in {'precision_loss','duration_constraint','grid_constraint'})
        runtime=self.family in {'valid_match','different_names','different_formats','precision_loss','duration_constraint','grid_constraint','wrong_mapping'} and not rejected
        native=runtime and self.family!='wrong_mapping'
        native=native or (self.family in {'stale_observation','missing_observation'} and not rejected)
        return {'mutation_calls':0 if rejected else 1,'runtime_verified':runtime,
                'native_verified':native,'verified':runtime and native,
                'classification':('safe_rejection' if rejected else 'verified' if runtime and native else
                                  'native_mapping_discrepancy' if self.family=='wrong_mapping' else
                                  'api_failure' if self.family=='api_error' else 'unverified_execution')}


def proposed_tasks():
    result=[]
    for index,family in enumerate(FAMILIES,1):
        goal=Goal('2030-01-07T09:00:00+00:00','2030-01-07T10:00:00+00:00',f'Diagnostic task {index:02d}')
        if family=='different_formats':
            goal=replace(goal,start_time='2030-01-07T11:00:00+02:00',end_time='2030-01-07T12:00:00+02:00')
        elif family=='precision_loss':
            goal=replace(goal,start_time='2030-01-07T09:00:00.000001+00:00')
        elif family=='duration_constraint':
            goal=replace(goal,end_time='2030-01-07T12:00:00+00:00')
        elif family=='grid_constraint':
            goal=replace(goal,start_time='2030-01-07T09:05:00+00:00')
        result.append(DiagnosticTask(f'D{index:02d}',family,goal))
    return tuple(result)


def task_sheet():
    return {'status':'proposal_pending_human_approval','seed':20271017,'repetitions':3,
            'condition_order':'counterbalance six permutations across task/provider blocks',
            'http_timeout_seconds':5,'per_run_budget_seconds':60,'automatic_retries':0,
            'planning_repair_iterations':0,'provider_scope':['a','b'],
            'scope_note':'20 single-action apparatus diagnostics; not the full protocol pilot including multi-step goals',
            'tasks':[{'task_id':t.task_id,'family':t.family,'formal_goal':t.goal.to_dict(),
                      'initial_state':'empty writable service unless intervention explicitly changes permission',
                      'mandatory_constraints':{'preserve_other_events':True,'evidence_age_seconds':30},
                      'required_evidence':['runtime permission/read-back','native before/after state','mutation-call count'],
                      'expectations':{p:t.expectation(p) for p in ('a','b')}} for t in proposed_tasks()]}
