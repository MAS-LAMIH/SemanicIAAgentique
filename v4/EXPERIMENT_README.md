# Repeatable V4 runtime experiment

This is an execution study on the two existing visible providers, not a measure
of onboarding effort. Conditions A (API-local), B (JSON), and C (RDF/Turtle) use
the unchanged EventCreation runtime and the same external native-state checks.
Condition C never denotes a third provider. No model, agent, network service,
new dependency, planner or action-contract requirement is introduced.

From repository root, use the existing environment (`v4/README.md` describes setup).
Run the complete T01–T16 matrix, three times (288 attempts plus 18 reset controls):

```sh
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment run --output /tmp/v4-repeat-001 --repetitions 3
```

Regenerate summaries without invoking APIs or altering raw evidence:

```sh
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment summarize --output /tmp/v4-repeat-001
```

Output must be new. Optional `--tasks T01 T04 T12 T16` selects a labeled subset;
never report subset coverage as all 16 families. Repetitions must be positive.
Execute serially on a quiet, fixed machine for publication timing comparisons.
Condition order rotates ABC by repetition and provider; catalogue order remains
fixed. No randomization or random seed is claimed. The complete order and source
state are recorded. A fixed workload is reproducible; exact timings are not.

## Raw and derived data

`raw/` contains manifest, selected catalogue, equal normalized frontends, static
metrics, append-after-each-attempt inventory, reset controls, all child stdout,
stderr, invocation/HTTP traces, independent before/after snapshots and native
journals. Each repetition creates fresh fixtures and child processes; six
contaminated-call-counter reset controls per repetition must reject before launch.
All failures and uncertain outcomes remain in the inventory. Existing five-second
HTTP timeout, 60-second outer budget (one second on delayed T16), no retries and
bounded post-stop observation are inherited without changing the pilot. Timeout
is never accepted as successful creation, even if the delayed service later
mutates. Unsettled observations fail diagnostics. Whole-attempt wall time includes
fixture startup/shutdown and settling, unlike worker process wall time.

`raw/evidence-sha256.json` seals raw files after termination, including interrupted
runs caught by Python's finally block. Hard kill/power loss may leave an unsealed
partial run: preserve it and report incomplete, do not fabricate a final seal or
remove attempts. Harness exceptions are retained and fail diagnostics. Source
hash drift during execution fails the run. No concurrent runs in the same output.
The source revision may predate local changes: dirty status and actual hashes,
not commit alone, identify code. Archive matching source for publication reruns.

`derived/` can be regenerated: JSON and CSV attempt records, correctness, error
handling, execution distributions and artifact-size tables; `tables.md` provides
copyable Markdown. Hash mismatches stop regeneration. Summary exit code is 0
only for complete expected coverage, passed diagnostics, normalized A/B/C parity,
passed reset controls and unchanged source. Condition comparison removes timing,
PIDs and serialization metadata using the existing pilot normalization.

Diagnostic correctness means the expected outcome occurred: correct rejection and
correct external detection of injected faulty service behavior count separately
from successful creation. `native_state_correct` alone is not an end-to-end
success measure (T15 stores correctly but loses the returned ID). Deliberate
unexpected mutations are reported, never hidden. Errors/timeout counts include
all outcomes. Timing tables stratify provider, condition, observed classification
and scope; report n, min, median, mean, nearest-rank p95 and max. Small-sample p95
is descriptive and often equals max; no significance or provider-population claim.
CSV absent values are blank; JSON absent measurements remain null.

Static metrics list physical lines (including comments/blanks), UTF-8 bytes and
hash for each shared runtime/glue/vocabulary/evaluation/fixture file and each
provider adapter/description. Shared modules are counted once, not once per
attempt or provider. A reuses ordinary HTTP/validation/conversion/result utilities;
B/C additionally reuse loaders and exact capability resolution. These are source
inventory/reuse descriptions, not developer time or evidence of effort reduction.
Human active time, AI supervision and integration effort remain null. Repeated
executions are not independent integrations: only two visible provider units,
already authored by shared contributors, with common-mode oracle/fixture risks.

## Future provider extension boundary

No future provider is opened or implemented here. Current runner intentionally
accepts only visible a/b. A separately authorized future extension needs native
fixture lifecycle/reset/capture support, independently curated task expectations,
a native decoder and adjudication review, plus provider-specific A adapter and
information-equivalent B/C descriptions. The current native decoder's non-a
branch assumes b: never pass an unknown provider through it. Use explicit provider
validation and independently reviewed native extraction; do not derive answers
from semantic mappings. Only after that review extend the evaluation harness's
explicit provider dispatch, worker routing and task coverage; preserve existing
raw evidence and report the new revision. Keep fixture storage and evaluator
answers private from integration contributors. Runtime changes, new capabilities
and a general provider/plugin framework are not prerequisites or implemented here.
The inherited diagnostic harness runs trusted deterministic workers and is not
a hostile-agent sandbox; this runner does not claim prospective-session isolation.
