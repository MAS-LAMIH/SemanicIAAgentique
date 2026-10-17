"""One existing validated subject operation; no native oracle expectations supplied."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from time import sleep
from unittest.mock import patch

from semantic_action.local_baseline import CalendarLocal, BookingLocal, LocalExecutor
from semantic_action.model import ApiResult, Goal
from semantic_action.registry import Registry, Registration
from semantic_action.transport import HTTPTransport
from .guard import verify_runtime


def main():
    data = json.loads(Path(sys.argv[1]).read_text())
    verify_runtime(data['baseline_root'])
    if data['provider'] not in {'a', 'b'} or data['condition'] not in {'A', 'B', 'C'}:
        raise ValueError('Visible providers/three conditions only')
    output = Path(data['output'])
    (output / 'worker-start.json').write_text(json.dumps({'fresh_process': True, 'persistent_resolution_cache': False,
        'runtime_guard': verify_runtime(data['baseline_root'])}, indent=2) + '\n')
    # Explicit public operational probe only; never used for the 180 default runs.
    if data.get('startup_stall_seconds'):
        sleep(data['startup_stall_seconds'])
    goal = Goal(**data['goal'])
    raw_request = HTTPTransport._http_request
    def request(client, method, path, values=None):
        response = raw_request(client, method, path, values)
        if method == 'GET' and response.success:
            permission = '/calendar' if data['provider'] == 'a' else '/availability'
            if ((data['wire_fault'] == 'missing_permission' and path == permission) or
                (data['wire_fault'] == 'missing_observation' and path != permission)):
                body = deepcopy(response.body)
                body.pop('observed_at' if data['provider'] == 'a' else 'sampled_at', None)
                response = ApiResult(response.status, body, response.error)
        return response
    with patch.object(HTTPTransport, '_http_request', request):
        if data['condition'] == 'A':
            local = (CalendarLocal if data['provider'] == 'a' else BookingLocal)(data['manual'])
            action = LocalExecutor(data['origin']).run(local, goal, data['inputs'], output / 'action.json')
            resolution = None
            compatible = action['compatible']
            applicability = action['applicability'] if compatible else None
        else:
            result = Registry([Registration(Path(data['manual']), data['origin'])]).execute(
                goal, data['operation_id'], output)
            action, resolution = result['action'], result['resolution']
            candidate = resolution['candidates'][0]
            compatible = candidate['compatible']
            applicability = candidate['applicability'] if compatible else None
    (output / 'subject-result.json').write_text(json.dumps({'action': action, 'resolution': resolution,
        'compatible': compatible, 'applicability': applicability}, indent=2) + '\n')


if __name__ == '__main__':
    main()
