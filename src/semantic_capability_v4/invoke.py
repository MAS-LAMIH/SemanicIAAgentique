"""Validate ordinary request values, map fields, and invoke once. No runtime oracle."""
from dataclasses import asdict
from .descriptions import normalize
from .http import send
from .mapping import map_inputs
from .model import InvocationResult
from .validation import validate_values
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
    validate_values(values, title_max_length=operation.title_max_length,
                    max_duration_seconds=operation.max_duration_seconds,
                    time_grid_seconds=operation.time_grid_seconds)


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
    return send(origin, operation.path, wire, operation.operation_id, operation.output_mapping)


def invoke_capability(operations, capability_id, origin, values, *, provider_id=None, operation_id=None):
    try:
        operation = resolve(operations, capability_id, provider_id=provider_id, operation_id=operation_id)
    except ResolutionError as error:
        return InvocationResult(error_kind='resolution', diagnostics=(f'{type(error).__name__}: {error}',))
    return invoke(operation, origin, values)
