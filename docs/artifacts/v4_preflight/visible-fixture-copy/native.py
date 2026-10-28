"""External fixture truth. No V4 imports, manual reads or runtime conversions."""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Snapshot:
    provider: str
    observed_at: str
    events: dict
    writable: bool | None
    revision: int
    mutation_calls: int  # Fixture counter counts POST attempts, even rejected ones.


def capture(provider, state):
    if provider == 'a':
        values = state.events, state.writable, state.revision
    elif provider == 'b':
        values = state.items, state.can_book, state.version
    else:
        raise ValueError('Visible providers only')
    return Snapshot(provider, datetime.now(timezone.utc).isoformat(), deepcopy(values[0]),
                    values[1], values[2], state.calls)


def initial_records(provider):
    if provider == 'a':
        item = dict(id='existing', start_time='2030-01-07T08:00:00+00:00',
                    end_time='2030-01-07T09:00:00+00:00', title='Preserve me', metadata={'sentinel': True})
    elif provider == 'b':
        item = dict(booking_ref='existing', begins_ms=1894003200000, finishes_ms=1894006800000,
                    label='Preserve me', metadata={'sentinel': True})
    else:
        raise ValueError('Visible providers only')
    return {'existing': item}


def decode(provider, item):
    if provider == 'a':
        return (item['id'], datetime.fromisoformat(item['start_time'].replace('Z', '+00:00')),
                datetime.fromisoformat(item['end_time'].replace('Z', '+00:00')), item['title'])
    if type(item['begins_ms']) is not int or type(item['finishes_ms']) is not int:
        raise ValueError('Native timestamps must be integer milliseconds')
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (item['booking_ref'], epoch + timedelta(microseconds=item['begins_ms'] * 1000),
            epoch + timedelta(microseconds=item['finishes_ms'] * 1000), item['label'])


def adjudicate(before, after, values, result):
    added = sorted(set(after.events) - set(before.events))
    removed = sorted(set(before.events) - set(after.events))
    changed = sorted(k for k in before.events if k in after.events and before.events[k] != after.events[k])
    matching, wrong = [], []
    for key in added:
        try:
            identifier, start, end, title = decode(after.provider, after.events[key])
            target_start = datetime.fromisoformat(values['start_time'].replace('Z', '+00:00'))
            target_end = datetime.fromisoformat(values['end_time'].replace('Z', '+00:00'))
            (matching if (identifier == key and start == target_start and end == target_end and
                          title == values['title']) else wrong).append(key)
        except (KeyError, ValueError, TypeError, OverflowError):
            wrong.append(key)
    permission_changed = before.writable != after.writable
    unexpected = bool(removed or changed or len(added) > 1 or wrong or permission_changed)
    unchanged = (before.events == after.events and before.revision == after.revision and not permission_changed)
    correct = (len(added) == 1 and matching == added and not unexpected and
               after.revision == before.revision + 1 and after.mutation_calls - before.mutation_calls == 1)
    output = result.get('output') if result else None
    output_id = output.get('id') if isinstance(output, dict) else None
    usable = (isinstance(output_id, str) and output_id in added and
              decode(after.provider, after.events[output_id])[0] == output_id)
    return dict(native_state_correct=bool(correct), unchanged_state=unchanged, output_usable=bool(usable),
                unexpected_mutations=unexpected, added_ids=added, matching_ids=matching, wrong_property_ids=wrong,
                changed_existing_ids=changed, removed_ids=removed, permission_changed=permission_changed,
                post_attempts=after.mutation_calls - before.mutation_calls,
                revision_before=before.revision, revision_after=after.revision)
