# V4 API-local / JSON / RDF comparative diagnostic pilot

**Engineering verdict: PASS.** On `codex/v4-comparative-pilot`, based on
`61f96e919ccc08a6cb70e339d76598895b1f4dd9`, all **96/96** T01–T16 attempts matched
prewritten expectations. All 32 task/provider comparisons agree across Conditions
A (API-local), B (JSON) and C (RDF). This is a diagnostic parity result on two
visible providers, not evidence of independently measured onboarding effort,
semantic-format superiority or confirmatory generalization.

## What changed and what was recovered

The restored workspace contained 13 uncommitted files/changes, including adapters,
shared helpers, tasks, worker and independent native checks. A hash-verified copy
was saved before continuing; the exact archive location and file hashes are in
`docs/artifacts/v4_pilot/recovery.json`. The driver was absent and there were zero
prior pilot outputs. It was implemented after that inspection; no offline save
was assumed. The interrupted interval was not reconstructed as measured effort.

A's two adapters explicitly select `create_event` / `reserveAppointment`, their
paths, field names and API bounds. They call the same ordinary HTTP, conversion,
validation and response helpers as B/C. They do not import descriptions or the
semantic registry, verified by an import-blocking test and retained worker module
lists. They have the same structured InvocationResult and usable-output policy.

For fair reuse, ordinary validation moved to `validation.py` and existing response
handling moved to `http.send`; B/C invocation delegates to them. The only existing
V4 test change points its no-HTTP resolution assertion at the extracted transport
helper. No assertion was weakened. Description semantics, capability lookup,
validation rules, HTTP budget and behavior were preserved. JSON/RDF descriptions
are unchanged and normalize identically for both providers.

## Outcomes

Each condition executed 32 tasks; each used the same task/native expectations.

| Outcome | A: API-local | B: JSON | C: RDF | Total |
| --- | ---: | ---: | ---: | ---: |
| Successful, independently correct creation | 9 | 9 | 9 | 27 |
| Correct input/unsupported-operation rejection | 9 | 9 | 9 | 27 |
| Correct service denial/error handling | 4 | 4 | 4 | 12 |
| Correct external detection of injected faults | 8 | 8 | 8 | 24 |
| Correct outer-timeout detection, never accepted as creation | 2 | 2 | 2 | 6 |
| Diagnostic attempts matching expectations | 32 | 32 | 32 | 96 |

Provider A accepts T06 submillisecond input, T07 off-grid input and T08 three-hour
input; Provider B rejects those documented API-invalid requests without POST.
A therefore has 18 successful creations and B nine, with parity across conditions
within each provider. The pilot does not force cross-provider validity equality.
T09 denies permission in the service, not by semantic precondition assessment.
Fixture call counters count POST attempts, including rejected calls, not stored
mutations; the native evidence records those facts separately.

There are **zero normalized parity differences** in invocation status/error class,
output, native verdicts, actual native records and HTTP request/response content.
Diagnostic wording, process IDs and timestamps are excluded from semantic
comparison. Each attempt has its own trace directory and fresh process; all 96
PIDs are distinct, all resets passed, and all source-bundle hashes agree.

T11's HTTP-success/no-storage, T12's wrong properties and T13's extra/sentinel
changes remain domain failures despite successful HTTP calls. T15 creates correct
native state but returns an unusable ID; its integration does not pass as a
successful creation. T16's six children are terminated/reaped at the one-second
outer limit. The service mutations are subsequently observed, with native goals
achieved, but none is accepted as successful invocation. The remote outcome was
uncertain at stop; all six settled within the bounded observation window.
Thus native correctness is true in 39 attempts (27 successful + six T15 + six late
T16), while only 27 creations are accepted. Twelve injected wrong-property/
side-effect attempts have unexpected native mutations. No unexpected mismatch
with the prewritten diagnostic expectations occurred.

Six additional call-counter contamination probes (one per provider/condition)
reject before launch. Separately retained focused tests cover six reset axes,
existing-path preservation, unusable output and an initially unsettled timeout.
The unsettled control remains unaccepted even after a bounded terminal observation
settles it. There are 16 focused retained attempt records, six matrix reset
controls and 96 base records; those extra controls are not counted as base coverage.

## Test and automation evidence

Fresh executions, all exit 0:

| Command phase | Tests / diagnostic attempts | Runner time | Measured command elapsed |
| --- | ---: | ---: | ---: |
| V4 regression suite | 20 tests | 28.867 s | 28.968 s |
| New fairness/native/safety suite | 6 tests | 16.139 s | 16.250 s |
| Full matrix plus six reset controls | 96 + 6 controls | 64.084 s inside driver | 64.196 s |

Times are observed automation wall durations, not CPU seconds or human work. The
two test commands overlapped, so their durations must not be summed as total
elapsed wall time. The matrix's child/attempt times are nested inside its parent
time and are not additional independent costs. These recorded phases exclude unmeasured coding/inspection overhead. Human-active work, AI supervision
and tool/model waits were not prospectively measured and remain null. No V3
historical test results are used as V4 comparative evidence.

Exact commands, timestamps and exits: `docs/artifacts/v4_pilot/{focused-tests,
v4-regressions,pilot-matrix}.json` and corresponding logs. Actual automation is
also recorded through the unchanged collector in a new `events.jsonl`.
Per-attempt durations, Python/dependency versions, task/source hashes, budgets,
raw/native observations and expected results are in `run-001/attempt-inventory.json`.
Complete output hashes are in `run-001/evidence-index.json`. Reproduction commands
are in [v4/PILOT_README.md](../v4/PILOT_README.md).

## Size accounting

Physical source lines include comments and blank lines. No lines are interpreted
as person-time or as independent integration samples.

| Component | Lines | Attribution |
| --- | ---: | --- |
| Shared V4 package, eight files including initializer | 396 | Full shared package, not charged as free onboarding |
| Ordinary utility subset: model, HTTP, conversions, validation, initializer | 163 | Shared technical code reused by A/B/C; whole-module count includes unused definitions |
| Description loading, registry and semantic invocation remainder | 233 | Additional B/C semantic/frontend infrastructure |
| Shared capability vocabulary | 17 data lines | B/C shared semantic setup, reused unchanged |
| A shared baseline glue, including initializer | 17 | Baseline-specific shared infrastructure |
| Provider A explicit adapter | 7 | Provider-specific A source |
| Provider B explicit adapter | 14 | Provider-specific A source |
| Provider A description | 33 JSON / 12 RDF | Provider-specific B/C data |
| Provider B description | 33 JSON / 12 RDF | Provider-specific B/C data |
| New pilot evaluation/recording/analysis package | 490 | Shared external evaluation infrastructure |
| New focused tests | 107 | Evaluation infrastructure; original V4 tests retained separately |

No provider-specific Python was added to B/C runtime. Provider-specific native
knowledge exists in the separate evaluator and existing A/B fixtures; it is not
free semantic onboarding knowledge. Existing frozen fixtures/supervision were
reused unchanged and are not miscounted as newly authored code. The runtime still
requires only the standard library for A/JSON execution; RDF uses RDFLib 7.6.0 and
pyparsing 3.3.3. Counts and their exact file breakdown are in `run-001/summary.json`.
A's concise adapters demonstrate that this baseline was not inflated to favor
semantic descriptions. Representation line counts depend on formatting and do
not establish an effort advantage.

## Preservation, deviations and limitations

Of 7,381 files present at the pilot base, 7,378 are byte-for-byte unchanged; the
three authorized V4 changes are the two helper-extraction files and the transport
mock-target update. All V3 candidate/source/manifests, M4.4/M4.5 reports/evidence,
old V4 descriptions and historical evidence are unchanged. No original ledger,
tag, candidate or research question was rewritten. No Provider C implementation,
manual, answers or state reader was accessed; condition C here only means RDF.

Disclosed controls: T13 uses the existing transition-observer hook to alter the
existing sentinel as well as the fixture's extra-record fault. T15 removes the ID
in an evaluator-owned wire shim at the common HTTP boundary, equally for all
conditions. These are not runtime repair or condition-specific descriptions.
The cloud interruption prevented the original driver write; recovery and testing
continued without inventing execution or effort from that interval. No matrix
attempt was discarded or replaced. The additional unsettled focused control is
expected not to meet the default catalogue timing; its failed diagnostic flag is
retained and asserted by the safety test, not counted as a base-matrix failure.

Before a genuinely prospective integration study:

- Use fresh integration assignments/contributors or report prior exposure and
  crossover learning explicitly; these visible APIs and mappings were already known.
- Fix engineering time budgets, correctness gate, task instances, authoring order
  and shared-cost allocation before observing measured authoring work. Log failures,
  review/rework, maintenance and AI use; keep unknown values null.
- Independently review native assertions/task meanings. The oracle does not consume
  runtime mappings, but fixtures, task expectations and code share authorship.
- Treat providers as independent units and task/condition runs as repeated
  diagnostics; two exposed providers cannot support population superiority claims.
- Broader API/authentication/transport coverage is untested. Bounded process
  supervision cannot guarantee cancellation or eventual remote settlement. The
  prototype remains one capability, one operation per invocation, local services
  and flat mappings, with no planning, retries or repair.

No confirmatory experiment, scientific-freeze approval, commit or push was part
of this pilot. Provider C remains sealed. Stop here for review.
