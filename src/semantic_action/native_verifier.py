"""Evaluation-only native fixture observer. No manuals, loaders or mappings imported.

Field interpretations are written against fixture storage APIs, not the subject's
output map. This is separate implementation, not independent human authorship.
"""
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from .model import Goal, Observation, now
from .oracle import current, verify


@dataclass(frozen=True)
class NativeSnapshot:
    provider: str
    observed_at: str
    revision: int
    writable: bool | None
    events: dict
    mutation_calls: int


@dataclass(frozen=True)
class NativeInterpretation:
    """Evaluator-owned provider-local decoder, never obtained from a subject manual.

    Future approved observation adapters can supply this interface without
    changing adjudication/goal semantics. source_reference identifies the reviewed
    observer artifact; it is provenance, not automatic proof of human approval.
    """
    provider: str
    decode_event: Callable[[dict], dict]
    source_reference: str


@dataclass(frozen=True)
class NativeExpectation:
    goal: Goal
    maximum_mutation_calls: int = 1


def capture(provider,fixture):
    if provider=='a':
        return NativeSnapshot('a',now(),fixture.revision,fixture.writable,deepcopy(fixture.events),fixture.calls)
    if provider=='b':
        return NativeSnapshot('b',now(),fixture.version,fixture.can_book,deepcopy(fixture.items),fixture.calls)
    raise ValueError('No native observer for this fixture')


def _calendar(item):
    return {'id':item['id'],'start_time':item['start_time'],'end_time':item['end_time'],'title':item['title']}


def _booking(item):
    # Intentionally not semantic_action.transform.convert or the local adapter.
    start,end=item['begins_ms'],item['finishes_ms']
    if type(start) is not int or type(end) is not int:
        raise ValueError('Native booking timestamps are not integer milliseconds')
    epoch=datetime(1970,1,1,tzinfo=timezone.utc)
    return {'id':item['booking_ref'],'start_time':(epoch+timedelta(milliseconds=start)).isoformat(),
            'end_time':(epoch+timedelta(milliseconds=end)).isoformat(),'title':item['label']}


def adjudicate(expectation,before,after,execution_started,runtime_verdict=None,interpretation=None):
    """Actual goal truth and independent evidence, separate from runtime verdict."""
    result={'achieved':False,'reasons':[],'runtime_discrepancy':False,
            'raw_before':asdict(before),'raw_after':asdict(after),
            'mutation_calls':after.mutation_calls-before.mutation_calls,'canonical_observation':None}
    goal=expectation.goal
    if before.provider!=after.provider:
        result['reasons'].append('Incompatible native snapshots')
        return result
    if not current({'observed_at':before.observed_at},goal.max_evidence_age_seconds):
        result['reasons'].append('Insufficient native baseline evidence')
        return result
    try:
        if interpretation is None:
            if before.provider not in {'a','b'}:
                raise ValueError('No evaluator-owned native interpretation supplied')
            interpret=_calendar if before.provider=='a' else _booking
        else:
            if interpretation.provider!=before.provider or not interpretation.source_reference or not callable(interpretation.decode_event):
                raise ValueError('Invalid evaluator-owned native interpretation')
            interpret=interpretation.decode_event
            result['interpretation_source']=interpretation.source_reference
        prior={k:interpret(v) for k,v in before.events.items()}
        post={k:interpret(v) for k,v in after.events.items()}
        created=set(post)-set(prior)
        # A fresh identifier is obtained from native state, never from the manual/response.
        event_id=next(iter(sorted(created))) if len(created)==1 else None
        baseline={'events':prior,'revision':before.revision,'observed_at':before.observed_at}
        state={'events':post,'revision':after.revision,'observed_at':after.observed_at}
        event={'event':post.get(event_id),'revision':after.revision,'observed_at':after.observed_at}
        observed=Observation(event,state)
        verdict=verify(goal,baseline,observed,event_id,execution_started)
        result['achieved']=verdict.achieved
        result['reasons'].extend(verdict.reasons)
        result['canonical_observation']=asdict(observed)
        if goal.forbid_other_changes:
            other_raw={k:v for k,v in after.events.items() if k!=event_id}
            if other_raw!=before.events:
                result['achieved']=False
                result['reasons'].append('Forbidden native-state change outside requested new event')
        if result['mutation_calls']<0 or result['mutation_calls']>expectation.maximum_mutation_calls:
            result['achieved']=False
            result['reasons'].append('Unexpected native mutation-call count')
    except (KeyError,ValueError,TypeError,OverflowError) as error:
        result['reasons'].append('Insufficient native evidence: '+str(error))
    if runtime_verdict is not None:
        result['runtime_discrepancy']=bool(runtime_verdict.get('achieved'))!=result['achieved']
    return result
