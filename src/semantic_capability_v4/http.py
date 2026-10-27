"""Loopback JSON HTTP; adapted from V3 transport without legacy model imports."""
import json
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from .model import InvocationResult


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def post(origin, path, values, operation_id):
    address = urlsplit(origin)
    if (address.scheme != 'http' or address.hostname != '127.0.0.1' or not address.port
            or address.path or address.query or address.fragment or address.username or address.password):
        raise ValueError('Only an explicit 127.0.0.1 HTTP origin is supported')
    request = Request(origin + path, json.dumps(values, allow_nan=False).encode(),
                      headers={'Content-Type': 'application/json'}, method='POST')
    client = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with client.open(request, timeout=5) as response:
            status = response.status
            try:
                raw = response.read(1000001)
                if len(raw) > 1000000:
                    raise ValueError('Response size limit exceeded')
                body = json.loads(raw)
                if not isinstance(body, dict):
                    raise ValueError('Expected JSON response object')
            except (ValueError, UnicodeError) as error:
                return InvocationResult(operation_id, status, True, error_kind='response_mapping',
                                        diagnostics=(str(error),)), None
            return InvocationResult(operation_id, status, True), body
    except HTTPError as error:
        # Includes redirects, which are never followed. No second mutation.
        return InvocationResult(operation_id, error.code, error_kind='http',
                                diagnostics=(f'HTTP {error.code}',)), None
    except (URLError, TimeoutError, OSError, HTTPException) as error:
        # Conservatively unknown: failure may follow dispatch or remote mutation.
        return InvocationResult(operation_id, error_kind='transport', diagnostics=(str(error),),
                                remote_outcome_unknown=True), None


def send(origin, path, wire, operation_id, output_mapping):
    """Ordinary one-call response handling shared by all three conditions."""
    from .mapping import map_output
    try:
        result, body = post(origin, path, wire, operation_id)
    except (ValueError, TypeError) as error:
        return InvocationResult(operation_id, error_kind='input', diagnostics=(str(error),))
    if result.error_kind:
        return result
    try:
        output = map_output(body, output_mapping)
        if not isinstance(output['id'], str) or not output['id'].strip():
            raise ValueError('Response id must be a nonempty string')
        return InvocationResult(operation_id, result.http_status, result.http_ok, output)
    except (KeyError, ValueError, TypeError, OverflowError) as error:
        return InvocationResult(operation_id, result.http_status, result.http_ok,
                                error_kind='response_mapping', diagnostics=(str(error),))

