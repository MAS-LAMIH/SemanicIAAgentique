"""Independent controlled booking API; does not import the calendar fixture."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from time import sleep
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
    # Controlled V3 sequence interventions; default leaves historical fixture behavior intact.
    followup_mode: str = 'normal'
    permission_after_first: str = 'unchanged'
    followup_delay_seconds: float = 0.0
    pending_requests: int = 0
    transition_observer: object = None

    def __post_init__(self):
        import math
        if self.followup_mode not in {'normal', 'error', 'no_change', 'mismatch', 'side_effect'}:
            raise ValueError('Unsupported follow-up mode')
        if self.permission_after_first not in {'unchanged', 'false', 'unknown', 'stale'}:
            raise ValueError('Unsupported permission intervention')
        if (type(self.followup_delay_seconds) not in (int, float) or not math.isfinite(self.followup_delay_seconds)
                or not 0 <= self.followup_delay_seconds <= 10):
            raise ValueError('Controlled delay must be finite, between zero and ten seconds')
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
            if self.command == 'POST' and not getattr(self, '_transition_finished', True):
                self._transition_finished = True
                if state.transition_observer:
                    state.transition_observer('after', self.path, status)
            data = json.dumps(payload, sort_keys=True).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

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
            self._transition_finished = False
            state.pending_requests += 1
            if state.transition_observer:
                state.transition_observer('before', self.path, None)
            try:
                self._post()
            finally:
                state.pending_requests -= 1
                if not self._transition_finished and state.transition_observer:
                    state.transition_observer('after', self.path, None)

        def _post(self):
            dependent = self.path.startswith('/booking-after/')
            predecessor_id = self.path.removeprefix('/booking-after/') if dependent else None
            if self.path != '/bookings' and not dependent:
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
            if dependent:
                predecessor = state.items.get(predecessor_id)
                if not predecessor or type(predecessor.get('finishes_ms')) is not int or start < predecessor['finishes_ms']:
                    self.reply(409, {'error': 'Previous booking and ordered interval required'})
                    return
            mode = state.followup_mode if dependent else state.mode
            if dependent and state.followup_delay_seconds:
                sleep(state.followup_delay_seconds)
            if mode == 'error':
                self.reply(503, {'error': 'Controlled booking failure'})
                return
            reference = f'booking-{state.calls:04d}'
            while reference in state.items:
                reference += '-new'
            stored = dict(item, booking_ref=reference)
            if dependent:
                stored['previous_booking'] = predecessor_id
            if mode == 'mismatch':
                stored['label'] = 'Incorrect booking label'
            if mode != 'no_change':
                state.items[reference] = stored
                state.version += 1
            if mode == 'side_effect':
                state.items['unexpected'] = dict(stored, booking_ref='unexpected')
            if not dependent and state.calls == 1:
                if state.permission_after_first in {'false', 'unknown'}:
                    state.can_book = False if state.permission_after_first == 'false' else None
                elif state.permission_after_first == 'stale':
                    state.stale_precondition = True
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
