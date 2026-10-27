"""Ordinary task/API validation shared by local adapters and semantic invocation."""
from .mapping import instant, microseconds
from .model import INPUT_ROLES


def validate_values(values, *, title_max_length=0, max_duration_seconds=0, time_grid_seconds=0):
    if not isinstance(values, dict) or set(values) != set(INPUT_ROLES):
        raise ValueError('Exactly start_time, end_time and title are required')
    title = values['title']
    if not isinstance(title, str) or not title.strip():
        raise ValueError('Nonempty title required')
    if title_max_length and len(title.strip()) > title_max_length:
        raise ValueError('Title exceeds API length limit')
    start, end = instant(values['start_time']), instant(values['end_time'])
    if end <= start:
        raise ValueError('Positive interval required')
    if max_duration_seconds and (end - start).total_seconds() > max_duration_seconds:
        raise ValueError('Duration exceeds API limit')
    if time_grid_seconds:
        for key in ('start_time', 'end_time'):
            if microseconds(values[key]) % (time_grid_seconds * 1000000):
                raise ValueError('Timestamp violates API time grid')

