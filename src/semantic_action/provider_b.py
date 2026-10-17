"""Independent controlled booking API; does not import the calendar fixture."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from .model import now


@dataclass
class BookingScenario:
    can_book: bool | None = True
    mode: str = 'normal'
    stale_precondition: bool = False
    stale_observation: bool = False
    items: dict = field(default_factory=dict)
    calls: int = 0
    version: int = 0

    def __post_init__(self):
        if self.mode not in {'normal', 'error', 'no_change', 'mismatch', 'side_effect'}:
            raise ValueError('Unsupported booking fixture mode')
        if self.can_book is not None and type(self.can_book) is not bool:
            raise ValueError('Invalid permission')


@contextmanager
def serve_bookings(scenario=None):
    state = scenario if scenario is not None else BookingScenario()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, status, payload):
            data = json.dumps(payload, sort_keys=True).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            stale = state.stale_precondition if self.path == '/availability' else state.stale_observation
            stamp = '2000-01-01T00:00:00+00:00' if stale else now()
            common = {'version': state.version, 'sampled_at': stamp}
            if self.path in {'/availability', '/bookings'}:
                self.reply(200, dict(common, can_book=state.can_book, items=deepcopy(state.items)))
            elif self.path.startswith('/booking/'):
                item = state.items.get(self.path.removeprefix('/booking/'))
                self.reply(200 if item else 404, dict(common, booking=deepcopy(item)))
            else:
                self.reply(404, {'error': 'No such resource'})

        def do_POST(self):
            if self.path != '/bookings':
                self.reply(404, {'error': 'No such resource'})
                return
            state.calls += 1
            if state.can_book is not True:
                self.reply(403, {'error': 'Booking permission not established'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 10000:
                    raise ValueError('Invalid size')
                item = json.loads(self.rfile.read(size))
                if set(item) != {'begins_ms', 'finishes_ms', 'label'}:
                    raise ValueError('Invalid keys')
                start, end, label = item['begins_ms'], item['finishes_ms'], item['label']
                if type(start) is not int or type(end) is not int:
                    raise ValueError('Times must be integer milliseconds')
                if start % 900000 or end % 900000 or not 0 < end - start <= 7200000:
                    raise ValueError('Invalid booking interval')
                if not isinstance(label, str) or not 0 < len(label.strip()) <= 500:
                    raise ValueError('Invalid label')
            except (ValueError, TypeError, KeyError):
                self.reply(422, {'error': 'Unsupported booking request'})
                return
            if state.mode == 'error':
                self.reply(503, {'error': 'Controlled booking failure'})
                return
            reference = f'booking-{state.calls:04d}'
            while reference in state.items:
                reference += '-new'
            stored = dict(item, booking_ref=reference)
            if state.mode == 'mismatch':
                stored['label'] = 'Incorrect booking label'
            if state.mode != 'no_change':
                state.items[reference] = stored
                state.version += 1
            if state.mode == 'side_effect':
                state.items['unexpected'] = dict(stored, booking_ref='unexpected')
            self.reply(201, {'booking_ref': reference})

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', state
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
