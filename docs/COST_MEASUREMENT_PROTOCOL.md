# Prospective cost-measurement protocol — candidate, not approved

Scope: RQ1 integration effort with correctness preserved. Provider labels A/B/C
are distinct from experimental conditions A/API-local, B/JSON+shared semantics,
C/RDF+shared semantics. Nothing here retrospectively turns Milestone 1–3 elapsed
intervals into human labor. Frozen scientific decisions prevail; the user-supplied frozen protocol PDF is retained under docs/protocols/
with its SHA-256 in candidate V2. Investigator approval is required before collection.

## Measurement axes

Record resource, activity, condition, scope and outcome separately. Do not force
all time into one scalar or add overlapping clocks.

| Measure | Prospective definition | Aggregation |
| --- | --- | --- |
| Human active person-minutes | Hands-on design, reading, annotation, mapping, coding, review, test analysis, debugging | Sum disjoint active intervals per person, then across people |
| AI-assisted active supervision | Human active time preparing instructions, steering, reading/reviewing/verifying AI output | A labeled subset of human active time, not an additional additive cost |
| Unassisted active time | Human active time without AI assistance | Disjoint complement within recorded human active time |
| Automated execution/runtime | Measured service, build, test, script or model execution wall duration; CPU time separately if available | Sum by invocation for resource accounting; retain overlap/concurrency |
| Tool/model waiting | Request-to-result latency, with queue/generation/network components only if observed | Report latency and unattended wait separately; do not infer active labor |
| Total elapsed wall-clock | Last completion minus first start for a declared workflow, plus union of working intervals if reporting working elapsed | Never sum concurrent task elapsed times as total elapsed |

A human reviewing results while another tool runs records active review and that
tool's runtime as distinct overlapping resources. A person cannot bill the same
minute to two active activities. Two people working concurrently contribute two
person-minutes per minute. Passive attended waiting is not active supervision.
Model computation is not human time. Unavailable queue/compute decomposition
stays null. Pauses, external blockers, overnight gaps and wall-clock scope must
be explicit; report both calendar elapsed and measured working elapsed if used.

## Activity and attribution taxonomy

Each event must identify one primary activity: setup, provider documentation,
manual/annotation authoring, semantic mapping, adapter/transformation development,
generic infrastructure development, testing, debugging/rework, maintenance,
review, or execution-only. Failed attempts retain their time and artifacts; link
rework to the failed attempt instead of replacing it with the successful run.
Retries, abandoned mappings, unsuccessful tests and tooling failures all count.

Scope is shared setup, provider onboarding, task execution, maintenance, or mixed
unallocated. Provider, condition and contributor IDs may be null when genuinely
unknown. Do not assign a mixed interval to onboarding merely to improve a result.
If work benefits B and C, record one underlying shared activity with allocation
policy and reuse links. Distinguish semantic content authoring from serialization
conversion and independent review. Common transport/oracle/environment setup
belongs in every condition's cost ledger according to the same declared rule.

## Event record and collection

Use UTC ISO timestamps, monotonic duration for processes, stable IDs and append-only
corrections. An approval-ready event schema must include:

```json
{
  "event_id": null,
  "task_id": null,
  "provider_id": null,
  "condition_id": null,
  "scope": null,
  "activity": null,
  "contributor_id": null,
  "resource_kind": null,
  "started_at": null,
  "ended_at": null,
  "elapsed_wall_minutes": null,
  "human_active_minutes": null,
  "ai_supervision_minutes": null,
  "automated_runtime_minutes": null,
  "tool_wait_minutes": null,
  "model_wait_minutes": null,
  "concurrency_group": null,
  "ai_model_and_version": null,
  "artifact_references": [],
  "mapping_rule_test_counts": null,
  "attempt_id": null,
  "outcome": null,
  "rework_of": null,
  "measurement_source": null,
  "missingness_reason": null,
  "supersedes": null
}
```

This is an empty prospective template, not an observed measurement. The prospective collector now implements these fields in
semantic_action.event_ledger.Event/Ledger. It is tested on the visible A/B
apparatus; investigator approval remains required before experimental collection. The existing WorkEntry/log_work supports coarse
activity, contributor, elapsed, artifact and failure records, but cannot express
all resource/overlap distinctions. Preserve it as provenance and link a separate
approved event ledger; do not silently reinterpret its elapsed_minutes field.
Milestone 4.1 adds a separate append-only JSONL ledger with advisory Linux file
locks, fsync, hash chaining, linked corrections, and overlap rejection for active
human intervals belonging to the same person. Corrections replace records only
in derived views; the original bytes remain in the log. Cross-contributor active
work and separate automated runtime may overlap. A supervision value cannot
exceed measured human active time. Unknown values stay null; resource kinds
prevent automation events from recording human labor. A hash chain detects edits
but cannot authenticate human truth or defeat an attacker rewriting an unsigned
entire ledger. Concurrent writers must use the collector, not bypass its lock.

Use Ledger(path).append(Event(...)); Ledger.summary reports measured resource
subtotals and unmeasured counts, never a fabricated total. Unknown/nonapplicable
metric cells are both null and require the resource kind/context for interpretation.
Do not add supervision to human total or sum runtime into labor. Synthetic timer
values in unit tests are explicitly test data, not observed engineering effort.
The actual events under docs/artifacts/milestone4_1/events.jsonl contain only
observed automation/elapsed resources and null unmeasured human fields. All old
WorkEntry logs remain unchanged. Review/freeze this collector before unsealing.

Human contributors start/pause/stop contemporaneous activity timers and confirm
active versus passive intervals at session end. A command wrapper records exact
command (with secrets redacted), exit status, monotonic runtime and output hash.
Model/tool metadata records observed timing and identities only. Daily review
resolves overlap and records missingness without filling it from memory. Missing
is null, measured zero is 0; both have provenance. Tool timestamps cannot identify
how long a human thought, read or supervised. Keep raw events and correction
history; never edit a failed event into a successful one.

## Cold-start and incremental reporting

For condition k and observed provider order pi, report shared setup S_k and each
provider onboarding increment I_(k,p|previous providers), with all setup, annotation,
mapping, adaptation, testing, debugging and review included. Cold-start total
through n providers is S_k + sum of observed increments + observed maintenance, with common dependencies
allocated by the same approved policy. Report human-active, runtime, waiting,
elapsed and correctness separately; do not mix their units in that formula.

Report shared semantic content cost once when constructing a shared asset; show
its charge in each stand-alone condition cold-start scenario and its reuse in a
joint-workflow analysis. Do not count one asset twice in a single combined total,
and do not give either JSON or RDF a free ontology, mapping, validator or curator.
For a C-provider increment retain the full actual work, even when it produces
UNKNOWN/incompatibility or no successful action. Report absolute increments,
cumulative totals, setup amortization policy, cached-versus-cold environment and
unallocated/missing work. Do not divide by successful calls and hide failed work.

Condition order and contributor experience can confound increments. Approve
independent teams or counterbalanced ordering and record exposure/carryover.
The same person reusing a known answer is not a cold independent integration.
Historic A/B tutorial work has incomplete measurements; report it as such and
collect fresh prospective cold-start runs if needed rather than invent totals.

## Analysis, missingness and extrapolation

Report verified correctness and unsafe-execution counts alongside costs. Show
raw provider-level paired differences; task repetitions within one provider are
not independent provider integrations. No significance or power claim follows
from one held-out provider. Budget censoring, missing time, unsupported services,
failed attempts and null results remain visible. Report measured lower bounds
when records are incomplete, with missingness coverage by category; do not impute
zero. Any imputation requires a separately labeled sensitivity analysis.

Beyond observed providers, define an explicit model such as T_k(n)=S_k+n*i_k
with assumptions and uncertainty ranges. A projected crossing is a model-based
sensitivity analysis, not empirical break-even evidence. Include no-crossing
cases, variable increments, learning, maintenance and uncertainty in shared setup.
Do not label fitted extrapolations as observed savings. Monetary/token costs,
if reported, require observed usage, dated rates and units, separate from time.

Approval must specify timer/collector version, allocation policy, contributor and
condition ordering, budgets, missingness treatment and analysis rules. All remain
pending until the investigator signs the candidate artifact digest.

## Milestone 4.1 implementation and proposed allocation

The neutral HTTP transport was extracted without changing its request behavior;
the unchanged formal Goal and correctness oracle are available to all conditions.
Charge their study-specific creation/maintenance to common neutral infrastructure
in each standalone condition cold-start analysis, once in a combined deployment
analysis. Charge the local validator/encoder/descriptions to condition A, and
ontology/registry/shared mappings to B/C consistently. Within condition A, its
common non-ontology event-shape helper is condition-A setup; booking-specific
rules/encoding and local mappings are onboarding work. This avoids pretending
normal programming utility reuse is ontology-mediated discovery or forcing
condition A to duplicate neutral infrastructure artificially.

The API-local descriptions and code were authored after exposure to the shared
manuals. Their measured engineering work is real apparatus work, not a blinded
cold-start integration estimate. Independent prospective integrators/order control
are still needed for scientific costs. Component time not separately measured
remains null or mixed_unallocated, even when artifact attribution is known.
No historical person-minutes have been reconstructed.

Proposed collection budgets are in EVALUATION_TASK_SPECIFICATION.md; elapsed,
automated waits and human-active limits are distinct. Maintenance, failed attempts
and rework remain visible. Approval of allocation, collector version and timer
practice is still pending and is listed in SCIENTIFIC_FREEZE_APPROVAL_CHECKLIST.md.
