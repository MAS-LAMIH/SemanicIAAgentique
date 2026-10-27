"""Validate ordinary request values, map fields, and invoke once. No runtime oracle."""
from dataclasses import asdict
from .descriptions import normalize
from .http import post
from .mapping import instant, map_inputs, map_output, microseconds
from .model import INPUT_ROLES, InvocationResult
from .registry import ResolutionError, resolve


def validate_description(operation):
    # Directly constructed data receives the same checks as loaded data.
    data = asdict(operation)
    data['input_mapping'] = {role: {'field': field, 'conversion': conversion}
                             for role, field, conversion in operation.input_mapping}
    data['output_mapping'] = {role: {'field': field, 'conversion': conversion}
                              for role, field, conversion in operation.output_mapping}
    data['input_limits'] = {key: data.pop(key) for key in
                           ('title_max_length', 'max_duration_seconds', 'time_grid_seconds')}
    checked = normalize(data)
    if checked != operation:
        raise ValueError('Noncanonical or duplicate description mappings')


def validate_inputs(values, operation):
    if not isinstance(values, dict) or set(values) != set(INPUT_ROLES):
        raise ValueError('Exactly start_time, end_time and title are required')
    title = values['title']
    if not isinstance(title, str) or not title.strip():
        raise ValueError('Nonempty title required')
    if operation.title_max_length and len(title.strip()) > operation.title_max_length:
        raise ValueError('Title exceeds API length limit')
    start, end = instant(values['start_time']), instant(values['end_time'])
    if end <= start:
        raise ValueError('Positive interval required')
    if operation.max_duration_seconds and (end - start).total_seconds() > operation.max_duration_seconds:
        raise ValueError('Duration exceeds API limit')
    if operation.time_grid_seconds:
        for key in ('start_time', 'end_time'):
            if microseconds(values[key]) % (operation.time_grid_seconds * 1000000):
                raise ValueError('Timestamp violates API time grid')


def invoke(operation, origin, values):
    try:
        validate_description(operation)
    except (ValueError, TypeError, AttributeError) as error:
        return InvocationResult(error_kind='description', diagnostics=(str(error),))
    try:
        validate_inputs(values, operation)
        wire = map_inputs(values, operation.input_mapping)
    except (ValueError, TypeError, KeyError, OverflowError) as error:
        return InvocationResult(operation.operation_id, error_kind='input', diagnostics=(str(error),))
    try:
        result, body = post(origin, operation.path, wire, operation.operation_id)
    except (ValueError, TypeError) as error:
        return InvocationResult(operation.operation_id, error_kind='input', diagnostics=(str(error),))
    if result.error_kind:
        return result
    try:
        output = map_output(body, operation.output_mapping)
        if not isinstance(output['id'], str) or not output['id'].strip():
            raise ValueError('Response id must be a nonempty string')
        return InvocationResult(operation.operation_id, result.http_status, result.http_ok, output)
    except (KeyError, ValueError, TypeError, OverflowError) as error:
        return InvocationResult(operation.operation_id, result.http_status, result.http_ok,
                                error_kind='response_mapping', diagnostics=(str(error),))


def invoke_capability(operations, capability_id, origin, values, *, provider_id=None, operation_id=None):
    try:
        operation = resolve(operations, capability_id, provider_id=provider_id, operation_id=operation_id)
    except ResolutionError as error:
        return InvocationResult(error_kind='resolution', diagnostics=(f'{type(error).__name__}: {error}',))
    return invoke(operation, origin, values)
