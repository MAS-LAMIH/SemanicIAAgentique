"""Competent shared technical glue, also using B/C's validation/HTTP utilities."""
from semantic_capability_v4.http import send
from semantic_capability_v4.model import InvocationResult
from semantic_capability_v4.validation import validate_values


def invoke_local(origin, values, operation, expected_operation, operation_id,
                 path, encode, response_id, **limits):
    if operation != expected_operation:
        return InvocationResult(error_kind='resolution', diagnostics=('NotFound: Unsupported local operation',))
    try:
        validate_values(values, **limits)
        wire = encode(values)
    except (ValueError, TypeError, KeyError, OverflowError) as error:
        return InvocationResult(operation_id, error_kind='input', diagnostics=(str(error),))
    return send(origin, path, wire, operation_id, (('id', response_id, 'identity'),))
