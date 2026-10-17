"""Closed transformation language; no provider names or arbitrary executable code."""
from datetime import datetime, timedelta, timezone
from .model import ApiResult, Validation, instant
from .provider_contract import CAPABILITY, EFFECT

EPOCH = datetime(1970,1,1,tzinfo=timezone.utc)


def convert(value, name):
    if name == 'identity':
        return value
    if name == 'iso_to_epoch_ms':
        delta = instant(value) - EPOCH
        micros = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
        if micros % 1000:
            raise ValueError('Transformation would lose submillisecond precision')
        return micros // 1000
    if name == 'epoch_ms_to_iso':
        if type(value) is not int:
            raise ValueError('Expected integer epoch milliseconds')
        return (EPOCH + timedelta(milliseconds=value)).isoformat()
    raise ValueError('Unsupported transformation ' + name)


def map_fields(values, description):
    result = {}
    for target, rule in description.items():
        if rule['source'] not in values:
            raise ValueError('Required input/observation cannot be transformed: ' + rule['source'])
        result[target] = convert(values[rule['source']],rule['transform'])
    return result


def validate_profile(contract, inputs, goal=None):
    if contract.profile is None:
        return Validation(True,())
    profile = contract.profile
    errors = []
    if contract.capability_id != CAPABILITY:
        errors.append('Unsupported shared capability mapping for event Goal')
    if goal and goal.forbid_other_changes and not profile.constraints['preserves_other_events']:
        errors.append('Cannot satisfy mandatory preservation constraint')
    if EFFECT not in contract.declared_effects:
        errors.append('Modeled effects cannot establish event-creation goal')
    rules = profile.binding['request_fields']
    if set(rule['source'] for rule in rules.values()) != set(contract.inputs):
        errors.append('Required input mapping is incomplete or has an unavailable source')
    try:
        map_fields(inputs,rules)
        start, end = instant(inputs['start_time']), instant(inputs['end_time'])
        limit = profile.constraints['max_duration_seconds']
        if limit is not None and (end-start).total_seconds() > limit:
            errors.append('Mandatory duration exceeds provider bound')
        grid = profile.constraints['time_grid_seconds']
        if grid:
            for value in (start,end):
                delta = value-EPOCH
                micros = (delta.days*86400+delta.seconds)*1000000+delta.microseconds
                if micros % (grid*1000000):
                    errors.append('Input times violate provider time grid')
                    break
    except (ValueError, TypeError, KeyError, OverflowError) as error:
        errors.append(str(error))
    return Validation(not errors,tuple(errors))


def adapted_request(raw_request, profile, method, path, values=None):
    binding = profile.binding
    if method == 'POST' and path == '/events':
        wire_path = binding['create_path']
        values = map_fields(values,binding['request_fields'])
        kind = 'response'
    elif method == 'GET' and path in {'/calendar','/events'}:
        wire_path = binding['baseline_path' if path == '/calendar' else 'state_path']
        kind = 'state'
    elif method == 'GET' and path.startswith('/events/'):
        wire_path = binding['event_path'].replace('{id}',path.removeprefix('/events/'))
        kind = 'event'
    else:
        raise ValueError('Unsupported canonical binding request')
    raw = raw_request(method,wire_path,values)
    if not raw.success:
        return ApiResult(raw.status,raw.body,raw.error,raw.body)
    body = raw.body
    try:
        if kind == 'response':
            canonical = {'id':body.get(binding['response_id'])}
        else:
            canonical = {'revision':body.get(binding['revision_field']),
                         'observed_at':body.get(binding['timestamp_field'])}
            if kind == 'state':
                events = body[binding['events_field']]
                if not isinstance(events,dict):
                    raise ValueError('Complete snapshot is required')
                canonical.update(writable=body.get(binding['writable_field']),
                                 events={key:map_fields(item,binding['event_fields'])
                                         for key,item in events.items()})
            else:
                item = body.get(binding['event_field'])
                canonical['event'] = map_fields(item,binding['event_fields']) if item else None
        return ApiResult(raw.status,canonical,raw.error,body)
    except (ValueError,KeyError,TypeError,OverflowError) as error:
        return ApiResult(None,{},'Insufficient mapped observation: '+str(error),body)
