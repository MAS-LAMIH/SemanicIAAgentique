# V4 minimal experiment — prospective proposal

Status: for review, not an approved protocol or a V4 result. This is a separate
research direction from the preserved V3 ESWC action-contract experiment. Do not
rewrite V3's research questions, conditions, historical findings or pending
approval records. Provider C is outside this proposal and remains sealed.

## Question and conditions

Primary question: for an integration that passes the same external correctness
tests, how much provider-specific engineering effort is required with API-local
integration versus reusable semantic capability descriptions? Secondary questions
concern mapping reuse, defects/rework and JSON/RDF authoring differences. No
serialization is hypothesized to be superior by construction.

| Condition | Integration work | Reusable/shared infrastructure |
| --- | --- | --- |
| A: API-local | Explicit provider/operation dispatch, ordinary validation, request and response adapters authored from the visible API specification; no shared capability registry | Same domain task input envelope, HTTP helper, conversion primitives, result envelope and external test harness may be reused |
| B: JSON + shared capability knowledge | Provider operation mapped to versioned shared capability roles with JSON descriptions and explicit input bounds | Vocabulary, JSON loader, finite lookup, common validator/invoker |
| C: RDF + equivalent shared knowledge | Same mappings and bounds, represented as Turtle | Same vocabulary/lookup/validator/invoker plus RDF parser |

A is allowed competent reusable programming helpers and the same provider API
information. It must not be forced to duplicate transport/conversion code merely
to make B/C look cheaper. The difference is where capability-to-operation knowledge
is authored: provider/application-local routing code versus a reusable registry
entry. A may use the same input field names for the test interface; that does not
give it the shared vocabulary or lookup implementation. Charge local routing work.

B/C must normalize to equal OperationDescriptions: capability/operation identity,
roles, paths/methods, conversions, required fields and bounds. Test duplicate and
incomplete descriptions symmetrically; JSON does not invoke the RDF loader. Do
not add stronger matching, hidden mappings, answer data or validation to either
condition. Origins, timeout, HTTP controls, response handling and invocation counts
are the same. Vocabulary/setup costs are shared semantic costs, not free input.

## Small visible-provider pilot

Use existing A/B fixtures only, fresh state per task and condition, a single
selected operation per invocation, no automatic fallback, retry, sequence or
repair. Propose these 16 public diagnostic cases, once per provider/condition:
96 diagnostic attempts, not 96 independent provider observations. Task instances
are to be written after architecture review and before condition results are
examined; the following specifies their families and expected evaluation policy,
not new benchmark answers or provider files.

| Case | Input/control | External correctness criterion |
| --- | --- | --- |
| T01 | Valid one-hour UTC event, writable fixture | Exactly one matching new record, correct returned ID, unrelated record preserved |
| T02 | Same valid interval expressed with non-UTC offsets | Same instants stored; exact conversion, no timezone shift |
| T03 | Valid Unicode title and provider-specific native field names | Correct title and mapped ID despite different names/formats |
| T04 | Missing required title | Reject before mutation |
| T05 | End before start | Reject before mutation |
| T06 | Valid submillisecond instants | A may represent exactly; B must reject before mutation rather than truncate |
| T07 | Off-grid but positive interval | A accepts; B rejects its documented grid violation before mutation |
| T08 | Three-hour interval | A accepts; B rejects its documented duration bound before mutation |
| T09 | Service denies permission | HTTP rejection, no new record; no semantic precondition query required |
| T10 | Service error | Invocation reports HTTP error; native capture determines any mutation, not status alone |
| T11 | HTTP success with no storage mutation | Incorrect attempted positive, even if runtime reports HTTP success |
| T12 | HTTP success with wrong stored title | Incorrect attempted positive, detected from native storage |
| T13 | HTTP success with unrelated record changed | Incorrect attempted positive, side effect retained/detected |
| T14 | Required domain capability not offered (similar display names allowed) | No mutation; B/C exact capability mismatch, A explicitly unsupported local task route |
| T15 | Successful mutation with unusable/missing returned ID | Native achievement recorded separately; invocation output is unusable, so integration does not pass this positive-output case |
| T16 | Delayed service mutation beyond outer deadline | Timed out, never accepted as a successful invocation; later native state retained, uncertainty explicit |

Provider-specific limits create legitimate A-versus-B differences; within a
provider all conditions have the same expected result. These are diagnostic test
outcomes: a test for a rejected request can pass without achieving a creation
intent. Deliberate wrong-storage/side-effect controls test error detection outside
the runtime; they are not evidence that V4 promises to prevent provider defects.
Do not copy the V3 180-run success rate as a V4 result.

Use fixed, published fixture inputs/order for this small engineering pilot; no
random sampling or seeds are needed. Iterate T01–T16, fresh isolated services and
trace paths for each attempt. Use a 5-second HTTP timeout and a 60-second outer
subject limit. T16 uses an explicitly labeled shorter outer limit (1 second) and
controlled delay (1.5 seconds), equally across conditions. Stop/reap the subject,
retain the parent fixture for bounded post-stop observation, and keep pending
state uncertain. No automatic retry; diagnostic reruns use new paths and remain
separate attempts. Reuse frozen supervisory mechanisms outside V4, not the old
combined driver that invokes Contract-based subjects. Reject contaminated resets
without clearing evidence; a harness defect pauses the affected pilot, rather
than discarding inconvenient results.

For authoring order, propose A: A/B/C and B: C/B/A, then alternate task direction
between sessions if more measured sessions are available. This partially balances
exposure only; two providers cannot balance all six permutations or remove
learning. Record actual order, prior familiarity, reused artifacts, contributor
identity and manual versus generated portions. If one person writes all conditions,
label this an exposed within-contributor pilot. Do not claim blind or independent
annotation, or use reruns as additional onboarding samples. No new governance
committee or approval schema is needed: record these facts with the run report.

## Correctness stays external

Before integration results are evaluated, specify expected native states directly
from task inputs and the A/B service/storage specification. Do not derive expected
records or conversions from capability descriptions, runtime response mappings or
runtime outputs. Retain initial sentinel records to detect unrelated changes.
Reuse evaluator-owned native captures/decoders; it is acceptable for a harness to
call the existing V3 native verifier, whose legacy Goal/evidence machinery stays
outside the V4 runtime. Record that shared authorship and fixture assumptions can
still cause common-mode errors; separation of imports alone proves no human
independence.

The harness records separate axes: invocation/HTTP outcome, output usability,
native correctness, forbidden side effects and incomplete/uncertain observation.
Use identical native assertions for A/B/C. A successful HTTP call is not an
independent correctness verdict. A timeout is an unsuccessful invocation even
when late mutation establishes the intended native state. Retain failed traces,
all raw snapshots, partial outcomes and denominators. Report expected-control
test passes separately from actual successful positive invocations.

## Prospective effort measurement

Record from the start of implementation, without estimating past V3 person-time:

| Cost category | What to record |
| --- | --- |
| Shared technical setup | Common transport/conversions, environment, generic result/test harness |
| Shared semantic setup | Vocabulary/role definitions and common semantic resolution/validation |
| Representation setup | JSON frontend versus RDF frontend/parser costs, separately |
| Provider-specific onboarding | API reading, local route or capability assignment, field mappings, input bounds, output decoding, initial fixture configuration |
| Testing/debugging/rework | Active testing and diagnosis, failed approaches, corrections and reruns; retain links to failed attempts |
| Maintenance | Later measured changes, charged to affected shared or provider component; not forecast as observed effort |

For each activity keep human-active engineering minutes, human AI-supervision
minutes, automated execution/runtime, tool/model waiting and elapsed wall time
separate. Do not count supervision twice as engineering time. Concurrent runtime
is not additive elapsed time. Keep missing values null; report measurement coverage
and exclusions. Charge AI-generated authoring/review/testing at actual measured
resource categories, not as zero-effort authoring. Separate code/data authored from
material copied or derived from V3/another condition; record reuse provenance and
conversion/review effort. Existing visible-provider knowledge makes a claim of
unexposed cold-start onboarding impossible in this session.

Primary display: provider-specific active human engineering plus separately
reported supervision required to reach the fixed correctness gate, per condition
and provider. Define that gate before measurement: ordinary positives/invalid
inputs must behave correctly; adversarial provider-fault/timeout cases must be
retained and correctly classified by the external harness, not falsely required
to become successful runtime executions. Stop measured integration at this fixed
gate; show time-to-budget and unresolved defects if a prereported time budget is
reached. Choose that budget with the investigator before measured authoring, not
retrospectively from observed effort. No implementation/measurement is authorized
by this design document.

Also show shared technical, shared semantic and frontend totals without folding
them invisibly into onboarding. For a standalone deployment, report each condition
with all setup it needs; a common component may appear in each standalone total
while being measured only once. For a joint deployment, count common components
once and state the allocation. Show both views rather than choosing the favorable
one after results. Any amortization/break-even beyond the two observed providers
is a labeled sensitivity calculation, not an empirical finding.

With two visible, previously exposed providers, report paired tables and raw
provider-specific differences, ranges and failure/rework counts. No population
p-values, provider-general superiority or narrow confidence claims from repeated
tasks. Describe JSON/RDF parity and correctness diagnostically; different authoring
costs are observations only if measured prospectively under declared exposure.

## Review decisions before coding

Review the finite capability profile and exact-match resolution, the single-call
scope, the API-local baseline's permitted helpers, the task/correctness gate and
prospective time budget, and the shared-cost/exposure reporting above. These are
V4 design choices, not retroactive scientific-freeze approvals. Implementation
steps and component disposition are in [the architecture proposal](V4_SIMPLIFIED_ARCHITECTURE.md).
Provider C remains untouched; extending beyond A/B requires a separate request.
