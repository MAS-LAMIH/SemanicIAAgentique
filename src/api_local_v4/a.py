"""Calendar API adapter, authored from the visible wire specification."""
from .common import invoke_local


def invoke(origin, values, operation='create_event'):
    return invoke_local(origin, values, operation, 'create_event', 'urn:provider:a:create',
                        '/events', dict, 'id')
