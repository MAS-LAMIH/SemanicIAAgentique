# Prospective scientific cost policy — V3

**All policies below are proposed until investigator approval.** P1 is the proposed
primary analysis; P2/P3 are declared sensitivity analyses, not alternatives to select
after observing which condition wins. This document does not amend the frozen RQ1 or
reinterpret historical elapsed/runtime records as human effort.

Candidate: [V3 manifest](SCIENTIFIC_FREEZE_MANIFEST_V3.json), SHA-256
`53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352`.
The [existing cost protocol](COST_MEASUREMENT_PROTOCOL.md) and frozen
[event collector](../src/semantic_action/event_ledger.py) remain unchanged.
Approval/signature: null. Effective study starting point: pending investigator choice.

## Resource measurements (proposed)

| Axis | Definition / collection | Aggregation and limits |
| --- | --- | --- |
| Human-active integration person-minutes | Contemporaneous start/pause/stop for reading, designing, authoring, mapping, coding, analysis, testing review, debugging and maintenance; contributor confirms session | Sum disjoint active intervals per person, then people; no same-person double billing |
| Human AI-supervision minutes | Active instruction, steering, reading/checking AI work, explicitly tagged within human-active intervals | A subset of human active, never added to it; AI compute is not human supervision |
| Automated runtime | Monotonic command/service/model execution duration with exact invocation and outcome; CPU separately only if observed | Keep parent/child nesting and concurrency; count each interval once within a declared resource total |
| Tool waiting | Observed tool request-to-result/unattended latency; queue/network decomposition only when observed | Distinct from active work and elapsed; null when unobserved |
| Model waiting | Observed model request/result latency and available queue/generation components | Same nonadditivity rule; do not infer human effort from model wait |
| Elapsed wall-clock | First start to last completion for declared workflow, recording exclusions; interval union for concurrent work | Calendar elapsed and working elapsed separately; never sum concurrent command elapsed as study duration |

A person can actively review while automation runs: both axes record the overlap but
are not summed as a scalar “total time.” Two active people can legitimately contribute
two person-minutes per minute. Inactive waiting pauses the active timer. Measured zero
requires observation; null means unknown/not measured, with context distinguishing
nonapplicable fields. Unknown historical costs remain unknown.

## Asset/activity attribution (proposed)

Each event identifies resource, contributor, provider, condition, scope, activity,
attempt, outcome, artifact hashes and assistance/exposure context where known. Use
`shared_setup`, `provider_onboarding`, `task_execution`, `maintenance` or
`mixed_unallocated`. The last is required when a mixed interval was not measured by
component; do not split it using guessed minutes, line counts or favorable weights.

| Component | Charge / retain |
| --- | --- |
| Neutral model, HTTP transport, runtime oracle, shared execution/supervisor requirements | Required deployable neutral setup, same policy across all conditions |
| Independent native observer, evaluation fixtures, hidden task curation, audit instrumentation | Separately identify common evaluation overhead; show both integration-only and all-in study engineering totals under fixed definitions |
| A provider-local descriptions, validators, encoders and ordinary local helper code | A-specific setup plus actual provider-local onboarding work; ordinary utility reuse is allowed and charged |
| Shared vocabulary/registry/mapping language/semantic validators | B/C semantic setup; not free because already built for this repository |
| JSON/RDF-specific authoring, parsing, conversion and content review | Charge actual format-specific activity; record source/derived provenance and equivalent assistance access; no free conversion/manual for either condition |
| Provider documentation, manuals, new mappings, adapters, native observation binding, fixture configuration | Provider/condition onboarding, distinguishing subject integration from independently curated evaluation work |
| Tests, setup/onboarding, debugging, failed and abandoned attempts, rework | Included in originating scope even if no goal is achieved; link rework and retain unsuccessful costs |
| Maintenance/revisions and regression checks | Dated affected asset/provider/condition; common changes apportioned under the same preregistered rule |

Before first exposure, inventory asset IDs, purpose, prior ownership, creation cost
availability and reuse links. A/C/B helper reuse is not a license to give one condition
free ontology or neutral infrastructure. File hashes locate assets but do not measure
work duration. Investigator must approve the scope boundary, including existing
infrastructure, independent review, assistance and evaluation overhead.

## P1 — standalone cold-start (proposed primary)

For each condition k and provider order pi, on each resource axis separately:
`Total_k(n) = Setup_k + sum(Onboard_k,p | prior providers) + Maintenance_k(n)`.
Human-active is the primary labor axis; always report runtime/waits/elapsed separately
and pair effort with independently checked correctness.

Each standalone counterfactual bears the full study-specific neutral setup it needs.
B and C each bear the full shared semantic setup needed for standalone deployment,
plus their own format costs. A bears its local engineering setup. Evaluation-only
common overhead is shown separately and in a consistently defined all-in sensitivity.
A shared asset is created once in the underlying ledger; P1's charges across separate
standalone scenarios intentionally duplicate counterfactual costs. They must not be
summed and labeled actual joint expenditure.

Report both cold-start totals and incremental onboarding after visible providers are
integrated. An increment includes unsuccessful binding, failures, tests and rework,
not just the final successful POST. A fast increment does not prove low cumulative
cost. A missing setup or maintenance measurement makes the complete empirical total
null/incomplete; show measured subtotals and coverage, not an invented full total.
Report A–B and A–C paired differences (plus B–C diagnostics), not only the best contrast.

## P2 — joint deployment sensitivity (proposed)

Charge each unique asset once in an A/B/C combined deployment. Proposed fixed equal
allocation: neutral common cost one third to each condition; semantic B/C shared cost
one half to B and half to C; directly attributable format/provider costs to their actual
condition. Publish the unique-asset portfolio total and allocations. Within a single
portfolio total, never count the same asset twice. This answers joint-program economics,
not standalone deployment economics. Equal allocation is a proposal needing approval,
not an empirical result about actual use or a retrospective default favoring a format.

## P3 — prospective amortization sensitivity (proposed)

Before outcomes, register asset lifetimes, reuse/provider counts, usage weights and
maintenance assumptions. Proposed sensitivity grids use equal provider counts n=1,
2,3,5,10, alongside no-reuse and high-maintenance/no-crossing cases; n beyond observed
providers is explicitly modeled. Show `Setup/n + incremental + maintenance allocation`
or cumulative curves with all assumptions and unknown ranges disclosed. Use documented
observed usage weights only if their collection/design was approved before evaluation.
Never change weights after inspecting the winning condition. P3 complements P1 rather
than replacing unfavorable standalone results.

Projected break-even beyond observed providers is **model-based sensitivity analysis**,
not empirical savings. Missing historical setup cannot be reconstructed by fitting a
curve. No observed crossing means report no observed break-even. Null costs cannot
support an observed n=1/2/3 total-cost curve merely because those provider labels exist.

## Collection, correction and missingness (proposed)

Use the frozen `Event/Ledger` schema with UTC times, monotonic runtime, append-only
hash-chained/locked writes and fsync. Contributors confirm active timer intervals and
assistance at session end; independent daily review checks overlaps and missingness.
No historical records are edited. Corrections append with `supersedes` and reason;
failed attempts/rework link with `rework_of`. Keep originals in raw data and use
current records only in derived summaries. Hash chaining does not authenticate a
person's honesty or prevent a trusted writer replacing an entire unsigned ledger.

Parent pilot command runtime nests individual subject runtimes: keep raw command
elapsed metadata but do not add both in a resource subtotal. Preserve separately
observed orchestration overhead if measured; do not silently claim that child subtotals
are the entire study runtime. Parallel invocation resource totals can exceed wall time.
Model/token/money metrics require actual usage, model/version and dated prices; otherwise
null. Tool failure is still an attempt. No model of unobserved historical person-minutes,
AI supervision or waits is permitted. Synthetic unit timers are not empirical labor.

For each cell report measured subtotal, expected/incomplete records, missingness reason,
coverage by activity and whether a total is estimable. Do not zero-impute, drop failures,
fill from memory, or substitute a CPU duration for human labor. Any assumed unknown
range belongs only to a labeled sensitivity analysis. Capped attempts retain measured
cost as a censored/unfinished attempt, not successful integration at the budget limit.

## Units, ordering and study limitations (proposed)

Independent provider, not task execution, is the unit for integration-cost generalization.
Visible A/B are exposed development fixtures. One future held-out provider is n=1
held-out provider, irrespective of 30 tasks, three conditions or repetitions. Repeated
execution estimates apparatus stability; repeated same-person integration is not a
fresh cold-start sample and cannot erase learning. Use prospectively assigned independent
contributors where feasible; disclose experience, condition order, prior exposure,
assistance and role overlap. Counterbalancing cannot make a previously seen answer unknown.

Historical [M4.3 resource records](artifacts/milestone4_3/resource-summary.json) measure
automation and partial elapsed scope, with human axes null. [M4.4 records](artifacts/milestone4_4/resource-summary.json)
are audit work, not experimental provider onboarding. Neither estimates labor savings.
Approving prospective collection does not repair incomplete historical cold-start data.

Investigator decisions: P1 scope/starting point, evaluation overhead boundary, P2 weights,
P3 grid/assumptions, collector/timer practice, contributor/assistance plan, budgets,
missingness/censoring and maintenance reporting. All remain pending in
[the V3 decision worksheet](SCIENTIFIC_FREEZE_DECISION_V3.json).
