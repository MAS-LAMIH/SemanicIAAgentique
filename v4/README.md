# V4 — minimal semantic capability interoperability

V4 loads an operation description, resolves an exact capability ID, validates
ordinary inputs, maps fields and makes one HTTP call. It returns invocation data,
not a proof of domain correctness. It does not import the V3 runtime.

## Run

From the repository root, using Python 3.12 (tested with 3.12.14):

```sh
uv venv --python 3.12 /tmp/semanic-v4-env
UV_CACHE_DIR=/workspace/.cache/uv uv pip install --python /tmp/semanic-v4-env/bin/python \
  -r v4/requirements-rdf.txt
PYTHONPATH=src /tmp/semanic-v4-env/bin/python -m unittest discover -s tests/v4 -v
```

Or use the already configured `.venv/bin/python` with the same PYTHONPATH. JSON
loading and HTTP invocation need only the Python standard library. RDF/Turtle
support adds RDFLib and its parser dependency, pinned in `requirements-rdf.txt`.
No changes to V3's packaging/dependency files are needed. This first slice runs
from source with PYTHONPATH; it is not included in the preserved V3 wheel.

A self-contained loopback demonstration (the fixture import is demonstration-only):

```sh
PYTHONPATH=src /tmp/semanic-v4-env/bin/python - <<'PY'
from dataclasses import asdict
from semantic_action.provider_b import serve_bookings
from semantic_capability_v4.descriptions import load
from semantic_capability_v4.invoke import invoke_capability
from semantic_capability_v4.model import EVENT_CREATION

operation = load('v4/descriptions/b.ttl')  # b.json normalizes identically
with serve_bookings() as (origin, _):
    result = invoke_capability([operation], EVENT_CREATION, origin, {
        'start_time': '2030-01-07T10:00:00+00:00',
        'end_time': '2030-01-07T11:00:00+00:00',
        'title': 'Team meeting',
    })
    print(asdict(result))
PY
```

The result includes HTTP status, `http_ok`, mapped `output`, an optional
`error_kind`, diagnostics and `remote_outcome_unknown`. There is no verified-goal
field. Tests independently inspect native fixture storage; that reader never runs
inside V4. A timeout is an error with uncertain remote outcome, not proof that
nothing happened. No retries or fallback operations are attempted.

## Description profile 1

The vocabulary in `vocabulary.json` defines EventCreation and its canonical roles.
`descriptions/{a,b}.{json,ttl}` contain equivalent visible-provider descriptions.

- Required fields: `description_version`, absolute URI `provider_id`,
  `operation_id`, `capability_id`, `method`, `path`, `input_mapping`,
  `output_mapping`, `input_limits`.
- Currently only EventCreation and POST at a configured `http://127.0.0.1:port`
  origin are supported. Paths are fixed local segments, without queries,
  templates or traversal. Redirects are disabled. The HTTP timeout is five seconds.
- Input mappings give `field` and `conversion` for exactly `start_time`,
  `end_time`, `title`. Output mapping supplies exactly `id`. Native fields must
  be identifiers; input targets must be unique.
- Time-role conversions: `identity` or `iso_to_epoch_ms`; title/id use `identity`.
  Epoch conversion rejects precision loss. The small utility also supports
  `epoch_ms_to_iso`, tested directly. Submicrosecond timestamps are rejected
  rather than silently truncated by Python's datetime parser.
- Input limits are integers: `title_max_length`, `max_duration_seconds`,
  `time_grid_seconds`. Zero means no limit. Limits describe API request validity,
  not live state. B uses 500 characters, two hours and a 900-second grid; A has no
  additional numeric bounds. The interval must always be positive, timestamps
  timezone-aware and title nonempty. Timestamps use `YYYY-MM-DDTHH:MM:SS`,
  optional 1–6 fractional digits, and `Z` or a `±HH:MM` offset; unsupported
  precision/offset forms reject rather than silently round.
- RDF uses the V4 namespace, one URI-rooted `OperationDescription`, singleton
  fields, mapping nodes with `role`/`field`/`conversion`, and a limits node.
  Version/limits use `xsd:integer`; identifiers and roles are URIs. See the small
  examples for the complete profile. Extra assertions reject, including
  disconnected triples. Identical RDF triples are idempotent under RDF set
  semantics; conflicting singleton values reject.

Load errors raise ValueError (file access errors remain OSError). `resolve` raises
NotFound or Ambiguous; it never uses operation labels to infer equivalence. Supply
an explicit `provider_id` or `operation_id` when several operations offer the same
capability. `invoke_capability` converts resolution errors into structured results.
`invoke` also validates directly constructed OperationDescriptions; there is no
alternate unchecked invocation path in the public API. The transport helper is
an internal ordinary HTTP primitive, not a security boundary against Python code.

The runtime does not assess permissions, read native fixture storage, perform
read-back verification, model transitions or plan/repair actions. Service denials
remain HTTP errors. Runtime HTTP success may coexist with a missing record, wrong
properties or extra mutation: the external test harness demonstrates those cases.

See `docs/V4_IMPLEMENTATION_REPORT.md` for measured complexity, fresh test results,
reuse provenance, preservation checks and limitations. No confirmatory experiment
or Provider C work is included.
