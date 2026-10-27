"""Small closed conversion table, adapted from V3's pure conversion primitives."""
from datetime import datetime, timedelta, timezone
import re

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def instant(value):
    if not isinstance(value, str):
        raise ValueError('Timestamp must be a string')
    pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})'
    if not re.fullmatch(pattern, value):
        raise ValueError('Expected ISO date-time, up to six fractional digits, and Z or ±HH:MM offset')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def microseconds(value):
    delta = instant(value) - EPOCH
    return (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds


def convert(value, conversion):
    if conversion == 'identity':
        return value
    if conversion == 'iso_to_epoch_ms':
        micros = microseconds(value)
        if micros % 1000:
            raise ValueError('Conversion would lose submillisecond precision')
        return micros // 1000
    if conversion == 'epoch_ms_to_iso':
        if type(value) is not int:
            raise ValueError('Expected integer epoch milliseconds')
        return (EPOCH + timedelta(milliseconds=value)).isoformat()
    raise ValueError('Unsupported conversion')


def map_inputs(values, mapping):
    return {native: convert(values[role], conversion) for role, native, conversion in mapping}


def map_output(body, mapping):
    return {role: convert(body[native], conversion) for role, native, conversion in mapping}
