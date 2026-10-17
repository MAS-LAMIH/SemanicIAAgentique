"""Benchmark oracle: consumes observations and a goal, never an artifact manual."""
from datetime import datetime, timezone
from .model import Goal, Observation, OracleVerdict, instant


def current(evidence: dict | None, max_age: float, since: str | None = None) -> bool:
    try:
        stamp = instant(evidence['observed_at'])
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        return 0 <= age <= max_age and (since is None or stamp >= instant(since))
    except (ValueError, TypeError, KeyError):
        return False


def verify(goal: Goal, before: dict | None, observation: Observation,
           event_id: str | None, execution_started: str) -> OracleVerdict:
    errors = []
    event_evidence, after = observation.event, observation.state
    if observation.error:
        errors.append(observation.error)
    if not current(before, goal.max_evidence_age_seconds):
        errors.append('Missing or stale baseline evidence')
    for label, evidence in [('event', event_evidence), ('state', after)]:
        if not current(evidence, goal.max_evidence_age_seconds, execution_started):
            errors.append(f'Missing, stale, or pre-execution {label} evidence')
    if errors:
        return OracleVerdict(False, tuple(errors))
    before_events, after_events = before.get('events'), after.get('events')
    if not isinstance(before_events, dict) or not isinstance(after_events, dict):
        return OracleVerdict(False, ('Incomplete calendar snapshot',))
    event = event_evidence.get('event')
    if not event_id or not isinstance(event, dict) or event.get('id') != event_id:
        errors.append('Expected event does not exist')
    elif event_id in before_events:
        errors.append('Returned identifier is not a new event')
    else:
        for key in ('start_time', 'end_time', 'title'):
            expected, actual = getattr(goal, key), event.get(key)
            try:
                matches = actual == expected if key == 'title' else instant(actual) == instant(expected)
            except (ValueError, TypeError):
                matches = False
            if not matches:
                errors.append(f'Goal mismatch: {key}')
        if after_events.get(event_id) != event:
            errors.append('Event query disagrees with calendar snapshot')
    if (type(after.get('revision')) is not int or
        type(before.get('revision')) is not int or
        event_evidence.get('revision') != after['revision'] or
        after['revision'] <= before['revision']):
        errors.append('State transition evidence is absent or inconsistent')
    if goal.forbid_other_changes:
        others = {key: value for key, value in after_events.items() if key != event_id}
        if others != before_events:
            errors.append('Forbidden change to other calendar contents')
    return OracleVerdict(not errors, tuple(errors))
