# V4 comparative diagnostic pilot

Conditions: A = explicit API-local adapters, B = JSON capability descriptions,
C = equivalent RDF/Turtle descriptions. C is a representation condition, never
an additional provider. Only visible providers a/b are available.

Run from the repository root with Python 3.12, RDFLib 7.6.0 and pyparsing 3.3.3
(the existing `.venv` has these). Environment setup instructions remain in
[v4/README.md](README.md). No running external services or model API are needed.

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/v4 -v
V4_PILOT_FOCUSED_OUTPUT=/tmp/v4-new-focused PYTHONPATH=src \
  .venv/bin/python -m unittest discover -s tests/v4_pilot -v
PYTHONPATH=src .venv/bin/python -m v4_pilot.driver --output /tmp/v4-new-pilot
PYTHONPATH=src .venv/bin/python -m v4_pilot.summarize --run /tmp/v4-new-pilot
```

Both output destinations must be new. The focused tests deliberately preserve
reset/fault/timeout traces, and reject reusing an existing attempt path. A full
pilot creates 96 diagnostic attempts plus six separately labeled reset controls.
The summarizer reads outcomes and compares conditions; it never manufactures task
answers or removes failed attempts. A rerun is a new diagnostic execution, not
an additional independent integration. Run the tests before the matrix.

Actual retained run: `docs/artifacts/v4_pilot/run-001/`. It includes:

- `catalogue.json`: the fixed T01–T16 input/control catalogue; expectations are
  separately saved before each child invocation.
- `frontend-parity.json`: equal normalized JSON/Turtle operation data.
- `attempt-inventory.json`: all 96 attempts, expected and observed outcomes,
  invocation result/error, independent native checks, uncertainty, timings,
  process status and reproducibility metadata.
- `attempts/Txx-provider-condition/`: reset, supervisor, native before/after,
  transition journal, child configuration, stdout/stderr, HTTP calls and returned
  invocation (when the child returned one). A timeout can leave partial traces.
- `reset-controls/`: all six contaminated call-counter fixtures rejected before
  child launch; original contamination is retained, not cleared.
- `summary.json` and `evidence-index.json`: normalized parity, coverage, safety,
  physical source-size counts and hashes of the complete retained run.

Explicit API-local use needs no descriptions or semantic registry:

```python
from api_local_v4.b import invoke
result = invoke(origin, {
    'start_time': '2030-01-07T10:00:00Z',
    'end_time': '2030-01-07T11:00:00Z',
    'title': 'Team meeting',
}, operation='reserveAppointment')
```

`api_local_v4.a.invoke` uses the local operation `create_event`. Unsupported local
operation names return a structured resolution error. B/C use the unchanged
capability-based call interface documented in the main V4 README. All three
share ordinary validation, timestamp conversion, HTTP timeout and response
mapping/error handling. Local adapters never load an OperationDescription or
perform capability lookup. The evaluative worker chooses the explicit adapter;
there is no automatic provider substitution.

The diagnostic harness owns fixtures and native observations in its parent
process. Each invocation runs in a fresh supervised child. Default HTTP/outer
budgets are 5/60 seconds, with zero retries. Only T16 uses the documented shorter
one-second outer limit and 1.5-second service-side delay. Parent observation is
bounded; stopping the subject cannot guarantee cancellation of service mutations.

The service modes implement no storage (T11), wrong properties (T12), and extra
mutation (T13). T13 also changes the existing sentinel record through the existing
fixture observer hook to exercise unrelated-record preservation. T15 deletes the
native response ID in a common evaluator-owned wire shim after the HTTP response,
before the shared response mapper; native storage is unchanged by that shim.
These are disclosed controls, not condition-specific runtime repair rules.

The oracle reads native fixture records directly and compares them with task
inputs. It does not read runtime mappings or capability descriptions. Output
usability additionally checks returned-ID consistency with native creation; it
is not used to infer what should have been stored. Side-effect controls and
HTTP-success/no-goal cases are diagnostic passes only when the external oracle
rejects their domain correctness. They are not successful creations.

See [the report](../docs/V4_COMPARATIVE_PILOT_REPORT.md) for results, source-size
accounting, actual automation times and limitations. These are visible diagnostic
executions with shared authoring/exposure, not measured independent onboarding
work or a confirmatory experiment. Provider C remains sealed.
