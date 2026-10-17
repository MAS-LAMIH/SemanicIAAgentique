"""Evaluator-owned whole-chain truth. Never loads subject contracts or transforms."""
from copy import deepcopy
from dataclasses import dataclass, asdict
from .model import Goal, instant
from typing import Callable
from .native_verifier import NativeSnapshot, NativeExpectation, NativeInterpretation, adjudicate


@dataclass(frozen=True)
class ChainInterpretation:
    """Trusted curator-owned observation binding, never selected by subject manuals.

    General truth stays frozen: decode existing event fields and the native parent
    relation only. Provenance text is not authentication or human approval.
    """
    provider: str
    event_interpretation: NativeInterpretation
    predecessor_of: Callable[[dict], str | None]
    source_reference: str


@dataclass(frozen=True)
class ChainExpectation:
    goals: tuple[Goal, ...]
    initial_records: dict

    def __post_init__(self):
        if len(self.goals) not in {2, 3}:
            raise ValueError('Only bounded chain expectations supported')


def verify_chain(expectation, initial, final, transitions, interpretation=None):
    """Curator expectations come from domain tasks, not the subject plan/trace."""
    reasons, steps = [], []
    def unsupported(reason):
        return {'achieved': False, 'reasons': [reason], 'transitions': [],
                'verified_transition_count': 0, 'partial_native_state': asdict(final),
                'expected_action_count': len(expectation.goals)}
    if final.provider != initial.provider:
        return unsupported('Inconsistent native provider')
    if interpretation is None:
        if initial.provider not in {'a', 'b'}:
            return unsupported('No curator-owned chain interpretation supplied')
        field = 'predecessor_id' if initial.provider == 'a' else 'previous_booking'
        predecessor_of = lambda event: event.get(field)
        event_interpretation = None
    else:
        if (not isinstance(interpretation, ChainInterpretation) or interpretation.provider != initial.provider
                or not isinstance(interpretation.event_interpretation, NativeInterpretation)
                or interpretation.event_interpretation.provider != initial.provider
                or not interpretation.source_reference or not callable(interpretation.predecessor_of)):
            return unsupported('Invalid curator-owned chain interpretation')
        predecessor_of = interpretation.predecessor_of
        event_interpretation = interpretation.event_interpretation
    if initial.events != expectation.initial_records:
        reasons.append('Initial reference state mismatch')
    if len(transitions) != len(expectation.goals):
        reasons.append('Not all required transitions occurred')
    previous_id = None
    prior_snapshot = initial
    accepted_ids = []
    for index, transition in enumerate(transitions):
        if index >= len(expectation.goals):
            reasons.append('Unexpected extra action')
            break
        before = NativeSnapshot(**transition['before'])
        after = NativeSnapshot(**transition['after'])
        if before.provider != initial.provider or after.provider != initial.provider:
            reasons.append('Inconsistent transition provider')
        if before.events != prior_snapshot.events or before.revision != prior_snapshot.revision or before.mutation_calls != prior_snapshot.mutation_calls:
            reasons.append('Unobserved mutation between transitions')
        if before.writable is not True:
            reasons.append('Mutation without native TRUE permission')
        native = adjudicate(NativeExpectation(expectation.goals[index]), before, after, before.observed_at,
                            interpretation=event_interpretation)
        created = set(after.events) - set(before.events)
        event_id = next(iter(created)) if len(created) == 1 else None
        if after.mutation_calls - before.mutation_calls != 1:
            reasons.append('Each required action must have exactly one mutation attempt')
        if index:
            event = after.events.get(event_id) or {}
            try:
                relation = predecessor_of(event)
            except (KeyError, ValueError, TypeError, OverflowError):
                relation = None
            if not previous_id or relation != previous_id:
                native['achieved'] = False
                native['reasons'].append('Missing or wrong native predecessor relation')
            # Domain ordering is checked independently of the sequence guard and manual.
            if instant(expectation.goals[index].start_time) < instant(expectation.goals[index - 1].end_time):
                native['achieved'] = False
                native['reasons'].append('Forbidden overlapping follow-up')
        if not native['achieved']:
            reasons.append(f'Required transition {index + 1} not verified')
        elif event_id:
            accepted_ids.append(event_id)
        steps.append(native)
        previous_id, prior_snapshot = event_id, after
    if (final.events != prior_snapshot.events or final.revision != prior_snapshot.revision or
        final.mutation_calls != prior_snapshot.mutation_calls):
        reasons.append('Unobserved final mutation')
    # Compare full native content, including the new relation metadata, across the whole run.
    preserved = {k: v for k, v in final.events.items() if k not in accepted_ids}
    if preserved != expectation.initial_records:
        reasons.append('Whole-sequence raw preservation failed')
    if final.mutation_calls - initial.mutation_calls != len(expectation.goals):
        reasons.append('Incomplete or excessive sequence mutation count')
    return {'achieved': not reasons and len(steps) == len(expectation.goals) and all(s['achieved'] for s in steps),
            'reasons': reasons, 'transitions': steps, 'verified_transition_count': sum(s['achieved'] for s in steps),
            'partial_native_state': asdict(final), 'expected_action_count': len(expectation.goals)}
