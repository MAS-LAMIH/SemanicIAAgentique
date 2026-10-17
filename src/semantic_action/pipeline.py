"""Validated REST execution. There is no public unchecked mutation operation."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4
from .contract import SAM, load_contract
from .model import (ApiResult, Condition, Goal, Observation, Truth, Validation,
                    instant, now)
from .oracle import current, verify


def validate_inputs(inputs: dict, required: tuple[str, ...]) -> Validation:
    errors = []
    if not isinstance(inputs, dict) or set(inputs) != set(required):
        return Validation(False, ('Exactly start_time, end_time, title are required',))
    if not isinstance(inputs['title'], str) or not 0 < len(inputs['title'].strip()) <= 500:
        errors.append('Title must be a nonempty string of at most 500 characters')
    try:
        if instant(inputs['end_time']) <= instant(inputs['start_time']):
            errors.append('end_time must be after start_time')
    except (ValueError, TypeError):
        errors.append('Times must be timezone-aware ISO 8601 timestamps')
    return Validation(not errors, tuple(errors))


def evaluate_preconditions(contract, inputs: dict, evidence: dict | None) -> tuple[Condition, ...]:
    interval = validate_inputs(inputs, contract.inputs)
    conditions = [Condition(str(SAM.PositiveInterval), Truth.TRUE if interval.valid else Truth.FALSE,
                            'Validated interval' if interval.valid else '; '.join(interval.errors),
                            {'start_time': inputs.get('start_time'), 'end_time': inputs.get('end_time')})]
    if not current(evidence, contract.max_evidence_age_seconds):
        verdict, reason = Truth.UNKNOWN, 'Missing, stale, or insufficient writability evidence'
    elif evidence.get('writable') is True:
        verdict, reason = Truth.TRUE, 'Current observation establishes writable'
    elif evidence.get('writable') is False:
        verdict, reason = Truth.FALSE, 'Current observation establishes not writable'
    else:
        verdict, reason = Truth.UNKNOWN, 'Writability not established'
    conditions.append(Condition(str(SAM.CalendarWritable), verdict, reason, evidence or {}))
    return tuple(conditions)


class Executor:
    def __init__(self, base_url: str):
        address = urlsplit(base_url)
        if (address.scheme != 'http' or address.hostname != '127.0.0.1' or
            not address.port or address.path or address.query or address.fragment or address.username):
            raise ValueError('Milestone 1 supports only a controlled 127.0.0.1 HTTP origin')
        self._base = base_url
        # Loopback requests need no external proxy. Redirects are not followed.
        from urllib.request import HTTPRedirectHandler
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        self._http = build_opener(ProxyHandler({}), NoRedirect())

    def _request(self, method: str, path: str, values=None) -> ApiResult:
        data = None if values is None else json.dumps(values).encode()
        request = Request(self._base + path, data=data, method=method,
                          headers={'Content-Type': 'application/json'})
        try:
            with self._http.open(request, timeout=5) as response:
                body = json.loads(response.read(1000000))
                if not isinstance(body, dict):
                    raise ValueError('Expected JSON object')
                return ApiResult(response.status, body)
        except HTTPError as error:
            try:
                body = json.loads(error.read(1000000))
            except (ValueError, OSError):
                body = {}
            return ApiResult(error.code, body if isinstance(body, dict) else {}, f'HTTP {error.code}')
        except (URLError, TimeoutError, OSError, ValueError) as error:
            return ApiResult(None, {}, f'{type(error).__name__}: {error}')

    def observe(self, event_id: str) -> Observation:
        # Identifier cannot supply URL path components or redirect the observer.
        if not isinstance(event_id, str) or not event_id or not all(
            c.isascii() and (c.isalnum() or c in '-_') for c in event_id
        ):
            return Observation(None, None, 'Invalid returned event identifier')
        event = self._request('GET', '/events/' + event_id)
        state = self._request('GET', '/events')
        return Observation(event.body if event.success else None,
                           state.body if state.success else None,
                           event.error or state.error)

    def run(self, contract_path: str | Path, goal: Goal, inputs: dict,
            trace_path: str | Path) -> dict:
        trace = {'schema_version': 1, 'run_id': str(uuid4()), 'timestamp': now(),
                 'artifact_id': None, 'operation_id': None, 'formal_goal': goal.to_dict(),
                 'inputs': inputs, 'contract_sha256': None, 'preconditions': [],
                 'evidence': {}, 'applicability': Truth.UNKNOWN,
                 'execution_decision': 'BLOCK', 'api_call_success': False,
                 'api_response': None, 'declared_effects': [], 'observed_effects': None,
                 'observed_state_change': None, 'oracle_verdict': None, 'reason': None}
        try:
            trace['contract_sha256'] = hashlib.sha256(Path(contract_path).read_bytes()).hexdigest()
            contract = load_contract(contract_path)
            trace.update(artifact_id=contract.artifact_id, operation_id=contract.operation_id,
                         declared_effects=list(contract.declared_effects))
            validation = validate_inputs(inputs, contract.inputs)
            trace['input_validation'] = asdict(validation)
            if not validation.valid:
                trace.update(applicability=Truth.FALSE, execution_decision='REJECT',
                             reason='; '.join(validation.errors))
                return trace
            baseline = self._request('GET', '/calendar')
            evidence = baseline.body if baseline.success else None
            trace['evidence']['baseline'] = evidence
            conditions = evaluate_preconditions(contract, inputs, evidence)
            trace['preconditions'] = [asdict(c) for c in conditions]
            verdicts = {c.verdict for c in conditions}
            applicability = (Truth.FALSE if Truth.FALSE in verdicts else
                             Truth.UNKNOWN if Truth.UNKNOWN in verdicts else Truth.TRUE)
            trace['applicability'] = applicability
            if applicability != Truth.TRUE:
                trace.update(execution_decision='REJECT' if applicability == Truth.FALSE else 'BLOCK',
                             reason='Critical precondition not established TRUE')
                return trace
            trace['execution_decision'] = 'EXECUTE'
            trace['execution_started'] = now()
            response = self._request(contract.method, contract.path, inputs)
            trace['api_response'] = asdict(response)
            trace['api_call_success'] = response.success
            # Observe even after error: failure status is not proof of no side effects.
            event_id = response.body.get('id')
            observation = self.observe(event_id) if event_id else Observation(
                None, self._request('GET', '/events').body, 'No returned event identifier')
            if not all(current(item, contract.max_evidence_age_seconds, trace['execution_started'])
                       for item in (observation.event, observation.state)):
                observation = Observation(observation.event, observation.state,
                                          observation.error or 'Contract observation evidence insufficient')
            trace['observed_effects'] = asdict(observation)
            after = observation.state
            trace['observed_state_change'] = (
                evidence.get('events') != after.get('events')
                if current(after, goal.max_evidence_age_seconds, trace['execution_started'])
                and isinstance(after.get('events'), dict) else None)
            oracle = verify(goal, evidence, observation, event_id, trace['execution_started'])
            trace['oracle_verdict'] = asdict(oracle)
            if not oracle.achieved:
                trace['reason'] = '; '.join(oracle.reasons)
            return trace
        except (ValueError, TypeError, OSError) as error:
            trace['reason'] = f'{type(error).__name__}: {error}'
            return trace
        finally:
            trace['completed_at'] = now()
            target = Path(trace_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation prevents silently replacing prior run evidence.
            with target.open('x', encoding='utf-8') as stream:
                json.dump(trace, stream, indent=2, sort_keys=True, allow_nan=False)
                stream.write('\n')
