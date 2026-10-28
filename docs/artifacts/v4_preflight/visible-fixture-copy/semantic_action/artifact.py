"""Deterministic loopback REST artifact; scenario controls belong to fixtures only."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from time import sleep
from .model import instant, now


@dataclass
class Scenario:
    writable: bool | None = True
    mode: str = 'normal'  # normal, error, no_change, mismatch, side_effect
    stale_precondition: bool = False
    stale_observation: bool = False
    events: dict = field(default_factory=dict)
    calls: int = 0
    revision: int = 0
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
            raise ValueError('Unsupported fixture mode')
        if self.writable is not None and type(self.writable) is not bool:
            raise ValueError('Invalid writability')


@contextmanager
def serve(scenario: Scenario | None = None):
    state = scenario if scenario is not None else Scenario()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, body):
            if self.command == 'POST' and not getattr(self, '_transition_finished', True):
                self._transition_finished = True
                if state.transition_observer:
                    state.transition_observer('after', self.path, status)
            data = json.dumps(body, sort_keys=True).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            timestamp = now()
            if (self.path == '/calendar' and state.stale_precondition) or (
                self.path != '/calendar' and state.stale_observation
            ):
                timestamp = '2000-01-01T00:00:00+00:00'
            if self.path in ('/calendar', '/events'):
                self.send(200, {'writable': state.writable,
                                'events': deepcopy(state.events),
                                'revision': state.revision, 'observed_at': timestamp})
            elif self.path.startswith('/events/'):
                event_id = self.path.removeprefix('/events/')
                self.send(200 if event_id in state.events else 404,
                          {'event': deepcopy(state.events.get(event_id)),
                           'revision': state.revision, 'observed_at': timestamp})
            else:
                self.send(404, {'error': 'Not found'})

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
            dependent = self.path.startswith('/followups/')
            predecessor_id = self.path.removeprefix('/followups/') if dependent else None
            if self.path != '/events' and not dependent:
                self.send(404, {'error': 'Not found'})
                return
            state.calls += 1
            if state.writable is not True:
                self.send(403, {'error': 'Calendar not established writable'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 10000:
                    raise ValueError('Invalid request size')
                values = json.loads(self.rfile.read(size))
                if set(values) != {'start_time', 'end_time', 'title'}:
                    raise ValueError('Invalid fields')
                if not isinstance(values['title'], str) or not values['title'].strip():
                    raise ValueError('Invalid title')
                if instant(values['end_time']) <= instant(values['start_time']):
                    raise ValueError('Invalid interval')
            except (ValueError, TypeError, KeyError):
                self.send(400, {'error': 'Invalid event'})
                return
            if dependent:
                predecessor = state.events.get(predecessor_id)
                try:
                    ordered = bool(predecessor) and instant(values['start_time']) >= instant(predecessor['end_time'])
                except (KeyError, ValueError, TypeError):
                    ordered = False
                if not ordered:
                    self.send(409, {'error': 'Existing predecessor and temporal order required'})
                    return
            mode = state.followup_mode if dependent else state.mode
            if dependent and state.followup_delay_seconds:
                sleep(state.followup_delay_seconds)
            if mode == 'error':
                self.send(500, {'error': 'Controlled execution failure'})
                return
            event_id = f'event-{state.calls:04d}'
            while event_id in state.events:
                event_id += '-new'
            event = dict(values, id=event_id)
            if dependent:
                event['predecessor_id'] = predecessor_id
            if mode == 'mismatch':
                event['title'] = 'Incorrect stored title'
            if mode != 'no_change':
                state.events[event_id] = event
                state.revision += 1
            if mode == 'side_effect':
                state.events['unrequested'] = {'id': 'unrequested', 'title': 'Unexpected'}
            if not dependent and state.calls == 1:
                if state.permission_after_first in {'false', 'unknown'}:
                    state.writable = False if state.permission_after_first == 'false' else None
                elif state.permission_after_first == 'stale':
                    state.stale_precondition = True
            self.send(201, {'id': event_id, 'accepted': True})

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', state
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
