"""Fresh invocation subject; never sees native state or curator expectations."""
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import sys
from semantic_capability_v4 import http


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    config = json.loads(Path(sys.argv[1]).read_text())
    output = Path(config['output'])
    provider, condition = config['provider'], config['condition']
    if provider not in {'a', 'b'} or condition not in {'A', 'B', 'C'}:
        raise ValueError('Visible providers/three conditions only')
    calls, raw_post = [], http.post
    def record(origin, path, values, operation_id):
        row = dict(path=path, method='POST', values=values, result=None, wire_fault=config['wire_fault'])
        calls.append(row); save(output / 'http-calls.json', calls)
        result, body = raw_post(origin, path, values, operation_id)
        row['raw_body'] = body.copy() if isinstance(body, dict) else body
        if config['wire_fault'] == 'missing_id' and isinstance(body, dict):
            body = body.copy(); body.pop('id' if provider == 'a' else 'booking_ref', None)
        row.update(result=asdict(result), delivered_body=body)
        save(output / 'http-calls.json', calls)
        return result, body
    http.post = record
    if condition == 'A':
        adapter = importlib.import_module('api_local_v4.' + provider)
        operation = 'record_reservation' if config['unsupported'] else 'create_event' if provider == 'a' else 'reserveAppointment'
        result = adapter.invoke(config['origin'], config['values'], operation)
    else:
        from semantic_capability_v4.descriptions import load
        from semantic_capability_v4.invoke import invoke_capability
        from semantic_capability_v4.model import EVENT_CREATION
        description = load(config['description'])
        required = 'urn:unsupported:reservation' if config['unsupported'] else EVENT_CREATION
        result = invoke_capability([description], required, config['origin'], config['values'])
    save(output / 'invocation.json', asdict(result))
    save(output / 'worker-modules.json', sorted(x for x in sys.modules if x.startswith(('semantic_capability_v4', 'api_local_v4'))))


if __name__ == '__main__':
    main()
