# One verified semantic action

Python 3.11+ is required. This milestone needs no LLM, API key, embedding model,
or outbound service. From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-semantic.txt -e .
python -m unittest discover -s tests/semantic_action -v
python -m semantic_action --output-dir /tmp/semantic-action-demo
```

The output directory must be new (traces are never overwritten). Expected
successful output includes `decision=EXECUTE applicability=TRUE api_success=True
goal_verified=True`. Exit 0 means the oracle verified achievement; all other
outcomes exit 1. The command starts and shuts down its own loopback REST service.
No service is retained between tasks. In the cloud environment, uv can install
into .venv with `UV_CACHE_DIR=/workspace/.cache/uv uv pip install --python
.venv/bin/python -r requirements-semantic.txt -e .`.

## Reproduce a negative scenario

```sh
python -m semantic_action --mode no_change --output-dir /tmp/semantic-action-nochange
python -m semantic_action --writable unknown --output-dir /tmp/semantic-action-unknown
```

Both intentionally exit 1. The first records successful HTTP but failed goal
verification. The second records UNKNOWN, BLOCK, and no API call. Other fixture
modes: error (500), mismatch (wrong stored title), side_effect (extra event).
Tests additionally cover invalid inputs, nonwritable calendar, stale evidence,
preexisting events, malformed/unsupported RDF, and independent goal mismatch.

## Outputs and costs

trace.json records run ID, UTC timestamps, contract SHA-256, artifact/operation,
formal goal, inputs, validation, precondition evidence/verdicts, decision, API
status/body, declared effects, actual read-back, state change, and oracle verdict.
A null oracle verdict means verification was not run (blocked/rejected); false
means it ran and did not establish achievement. scenario.json records initial
fixture settings; work.jsonl records the measured runtime of this CLI validation
only. IDs and timestamps vary; semantic outcomes are reproducible. Preserve the
contract, goal, scenario, code revision, and dependency versions with the trace.
The trace is an execution audit, not an LLM reasoning transcript.

Use `semantic_action.cost.WorkEntry` and `log_work` for integration activities.
Human entry is required for setup, annotation, mapping, adaptation, testing,
debugging, failed attempts, and contributor time not actually instrumented.
Unknown values remain null. docs/integration_work.jsonl records this AI-assisted
implementation without inventing durations or retrospectively guessing counts.
Do not treat CLI runtime as total integration effort. Record overlapping work
carefully and include all categories in future experiments.

## Baseline preservation and limits

Original tutorial files and requirements remain unchanged; only package inclusion
was extended. Existing tests/test_*.py are live tutorial demonstrations, not the
milestone suite: broad discovery may call external services. Their search example
is blocked by the current network policy, and Groq examples require a valid key.
Local tutorial arithmetic and Python execution were validated before and after.
Live tutorial operation is not claimed as verified.

No protocol PDF was available; the supplied frozen brief was used. No A/B/C
comparison, integration-cost conclusion, full planner, LLM integration, registry,
or held-out provider is implemented. The oracle assumes a trusted complete local
snapshot and one writer. See CONTRACT_SEMANTICS.md for evidence and side-effect
limits. Next milestone: freeze the profile and evaluation fixtures, then design
an equivalent JSON frontend and cost collection protocol before adding providers.

## Verified in this checkout

All 23 deterministic tests passed in both the development environment and a
fresh environment containing only the built project wheel, RDFLib, and its
pyparsing dependency. Wheel construction and package consistency passed. The
normal CLI verified a goal; no_change and unknown CLI runs returned the expected
exit 1 and distinct failed-verification/blocked traces. The reusable install
script was rerun successfully. Cloud install_script and start_skill were saved
as a draft; publication and restoration in a new cloud task remain unverified.
