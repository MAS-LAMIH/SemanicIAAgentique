# Proposed confirmatory evaluation protocol — V3

**Status: proposed lock, not an effective preregistration or authorization.** All
parameters require investigator approval. No confirmatory results are reported here.
Provider C remains sealed; this task neither requests nor prepares its implementation,
manuals, concrete task instances or answers. No generic code, planner or feature is added.

The governing [frozen research protocol](protocols/ESWC_2027_Frozen_Research_and_Experimental_Protocol.pdf)
§§4–9 controls the scope. The immutable subject is candidate `752da7b`, implementation
`2d264169a5ec363b78d4bf78b3f40e82d7b59f85`, tag `candidate/milestone-4.3-pre-freeze`,
[V3 manifest](SCIENTIFIC_FREEZE_MANIFEST_V3.json) SHA-256
`53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352`.
New documentation is a review revision, not a replacement V3 implementation candidate.

## 1. Questions, hypotheses and claim boundaries (proposed)

RQ1 remains primary: “To what extent does reusable ontology-mediated capability
knowledge reduce total and incremental effort for integrating independently developed
Web APIs while preserving correct execution?” Proposed directional hypothesis: B/C may
reduce incremental human-active integration effort relative to A under identical
correctness obligations; total cold-start effort may increase, decrease or remain
indistinguishable after shared setup and maintenance. Report both A–B and A–C paired
comparisons regardless of sign. No significance, superiority or savings is presumed.

B/C parity is a design obligation and representation control, not an RDF superiority
hypothesis. Exact supported-semantic outcome disagreement is a finding to preserve and
review; similar outcomes are not proof of population equivalence. RQ2 (LLM versus
classical planning/repair under identical formal goals) remains secondary and outside
this experiment: no planner is implemented here. RQ3 (ambiguous natural-language goal
interpretation) remains optional and unevaluated. Declared bounded chains are not planning.

## 2. Conditions and subject boundary (proposed)

| Condition | Available knowledge / mechanism | Equal obligations |
| --- | --- | --- |
| A API-local | Explicitly selected local operations, local contracts/validators/transforms; neutral programming helper reuse allowed; no shared semantic discovery | Same domain goals, input validity, fresh critical evidence, effects, constraints, preservation and independent correctness |
| B JSON + shared semantics | Ontology/capability identifiers, mappings, finite shared validators/registry and JSON frontends | Exactly the same supported semantic information/validation power as C |
| C RDF + shared semantics | Equivalent typed contracts/sequence profiles and frozen shared infrastructure, Turtle frontends | Exactly the same supported semantic information/validation power as B |

Providers and conditions are distinct axes. A is not Provider A; condition C is not
held-out Provider C. Inputs, service behavior, reset state, admissible evidence, tool
access, required predicates, budgets and oracle criteria must be equal across conditions.
Do not weaken A or either shared format. Preserve raw records; normalize only run IDs,
PIDs, timestamps/serialization metadata after evaluating freshness and semantic verdicts.
Compare actual calls and observations, not string identity of parser errors.

## 3. Exact public catalogue and prospective sealed task lock

The fixed **public apparatus catalogue** is exactly D01–D20 from
[evaluation_tasks.py](../src/semantic_action/evaluation_tasks.py) /
[evaluation_tasks_v1.json](evaluation_tasks_v1.json), plus M01–M10 from
[multistep_tasks.py](../src/semantic_action/multistep_tasks.py) and
[MULTISTEP_PILOT_TASKS.md](MULTISTEP_PILOT_TASKS.md). Their hashes are already bound by
V3. No cases are added, deleted or relabeled after seeing provider/condition outcomes.

| IDs | Exact family meanings |
| --- | --- |
| D01 / D02 / D03 | Valid semantic match / different operation names / equivalent time formats |
| D04 / D11 | Misleading effect / unsupported transition (overlapping reservation-effect controls) |
| D05 / D06 / D07 / D08 | FALSE permission / UNKNOWN permission / stale permission / missing permission evidence |
| D09 / D10 | Unavailable valid input conversion / forbidden precision loss |
| D12 / D13 / D14 / D15 | API error / HTTP success without storage / wrong stored properties / misleading output mapping |
| D16 / D17 / D18 | Forbidden side effect / stale post-execution evidence / missing post-execution evidence |
| D19 / D20 | Provider duration constraint / time-grid constraint |
| M01 / M02 | Genuine two-action predecessor dependency / state-updated revoked permission |
| M03 / M04 / M05 | Intermediate API failure / next-action UNKNOWN permission / non-equivalent follow-up effect |
| M06 / M07 / M08 | Forbidden sequence side effect / no-op follow-up response / recovery boundary with third action unattempted |
| M09 / M10 | Genuine three-action predecessor chain / stale next-action permission evidence |

Public D goals are fixed domain inputs from the frozen generator, generally 2030-01-07
09:00–10:00 UTC with documented format/precision/duration/grid variants. D initial
storage is empty unless the stated intervention changes permission/evidence. M goals
are fixed required appointments [09:00,10:00], [10:00,11:00] and, for M08/M09,
[11:00,12:00], with a pre-existing sentinel event and mandatory predecessor links.
All require preservation and sufficient fresh evidence; default evidence age is 30 s.
The exact input/property values and known A/B expectations remain in the frozen source,
not rewritten here. A/B precision/duration/grid feasibility labels must not be copied
as a future provider's answers.

**Unresolved lock condition:** these 30 public diagnostics and A/B answers are already
known to the generic author. They cannot simultaneously be described as sealed unseen
tasks. Proposed confirmatory distribution is one independently curated instance per
listed family (30 total), with the same goal fragment/negative-control intent, retained
IDs linking to the family. Concrete held-out instance inputs, feasibility labels,
expected native predicates and reference behavior must be independently prepared,
reviewed, sealed and hashed by the designated curator **before contributor release**.
No such instances/answers are created, requested or accessed here. Their custody
manifest and digest are null/pending in the decision record. Therefore this is a
complete proposed family/parameter specification, but not a fully locked hidden task set.

The investigator must choose between (a) a genuinely sealed independently instantiated
confirmatory task set under this family lock, or (b) explicitly limiting claims to
public-task evaluation with provider holdout only and registering the consequent
protocol deviation. Do not imply task blinding in (b). Any wider task/model requirement
outside the frozen profile is unsupported; do not invent a compatible replacement.

## 4. Counts, seeds and ordering (proposed)

- Exactly 30 families, one predeclared instance per family per evaluated provider,
  three execution repetitions and all three conditions: 270 planned task-condition
  executions per held-out provider. These are executions, not 270 independent providers.
- A/B validation uses the same public catalogue. A hypothetical complete three-repeat
  validation would be 540 executions across the two visible fixtures. M4.3 did not run
  that design: it retained one 60-run multi-step sweep plus six extra M01 repetitions,
  and regression matrices. M4.4 reproduction is still apparatus validation.
- Root seed 20271017; task-block shuffle seed 20271018; contributor-assignment seed
  20271019. Record Python/random version and the complete schedule, since a seed alone
  is not a portable registration artifact.
- Canonically enumerate blocks sorted by provider code, repetition 1–3, task ID D01–D20
  then M01–M10. Assign ABC, ACB, BAC, BCA, CAB, CBA cyclically by block index; shuffle
  the assigned blocks with the task-order seed, retaining within-block condition order.
  There are 90 blocks per provider, 15 of each permutation. Archive and hash the actual
  schedule before release; do not rerandomize after unfavorable outcomes.
- Assign onboarding contributors separately with the assignment seed after fixing a
  declared roster and experience strata. Prefer separate contributors per condition;
  counterbalance onboarding order across qualified contributors where possible. Task
  counterbalancing does not remove integrator learning or prior manual exposure.

The schedule and roster hashes are pending, not invented here. The public deterministic
runners use fixed loop order for engineering tests; their logs are not evidence that
this proposed randomized onboarding/evaluation schedule already ran.

## 5. Budgets, resets and stops (proposed)

Use 5 s per HTTP request, a 60 s outer subject execution deadline including startup,
zero automatic retries, zero planner/repair iterations, and no compensating actions.
Onboarding cap: 90 human-active person-minutes and 300 elapsed minutes per provider/
condition attempt; include reading/setup, authoring, debugging and tests in that attempt.
Record unused/unknown time and reasons; caps do not create missing measurements.
The supervisor's 0.5 s terminate grace, final kill/reap and bounded 1.5 s native settling
window are post-deadline controls, not extra subject repair time. Record any overshoot.

Before each condition/task/repetition: reserve a fresh trace directory and fresh subject
process; independently verify initial native records/metadata, permission, revision,
mutation and pending-request counters against the curator's expected reset state.
No retained resolutions, cached answers, warm provider repairs or cross-run events.
B/C instantiate the registry afresh; declare process/cache policy. Archive reset evidence
before subject launch. Reject contaminated initial state; retain the rejected attempt
and costs rather than executing and silently clearing contamination.

Use the frozen supervisor for both single-action and multi-step subject processes under
a preapproved evaluator-owned driver. Existing multi-step timeout/reset enforcement is
demonstrated; the public single-action `evaluation.run_case` has no built-in outer
supervisor. The future combined driver and its single-action timeout/reset coverage
remain an operational preflight gate, not an implemented feature or a passing claim here.
The visible pilot runner is A/B-only; future provider-local drivers must use frozen
interfaces and the approved addition-only boundary, not patch the generic runner/oracle.

Stop affected runs on identity/dependency drift, reset contamination, unexpected unsafe
mutation, condition parity mismatch, unplanned native/runtime disagreement, unreliable
observer or deadline enforcement. Preserve partially attempted blocks and all artifacts;
independently classify scope and whether unaffected runs can proceed. No favorable-result
stop, hidden retry, failed-case deletion or post-hoc budget increase. A planned decoy-map
or delayed-effect negative control is classified as planned, not an unplanned stop trigger.

A genuine generic defect stops affected confirmatory evaluation. Preserve baseline
failures/costs and obtain an independent report; do not patch the engine, validator,
shared meaning/transforms, oracle, planner interfaces/prompts or task-specific repair
rules after unsealing and retain an unchanged-baseline claim. Retire/version/review a
new candidate if correction is necessary. Same-provider reruns after exposure are
exploratory unless a genuinely uncontaminated new holdout and preregistered restart
design are available. Approval cannot retroactively remove exposure.

## 6. Independent native adjudication (proposed)

Before execution, the curator signs formal domain goals, complete initial state,
feasible-positive/negative labels, required intermediate/final transitions, permitted
alternatives, forbidden effects and observation requirements from domain/reference
behavior, **not subject manual postconditions or the resolver's answer**. Curator-native
field interpretations may use authoritative service/storage specifications under role
controls; never reuse the subject output map as the sole source of truth.

Preserve raw native before/after records, service-side call counts, timestamps/revisions,
wire evidence and runtime decisions. Use frozen `oracle.verify`, `native_verifier` and
`sequence_native.verify_chain`; a trusted, reviewed `NativeInterpretation` /
`ChainInterpretation` may decode provider-local evidence without changing truth rules.
A provenance string is not review authentication. Subject manuals cannot select the
oracle reader or receive expected-answer files. Independent reviewers sign hashes of
expectations and observer code before subject execution.

For chains, require every action and intermediate native transition, correct immediate
predecessor relationship, native TRUE permission at mutation, all final goal properties,
and preservation of all pre-existing raw records. Missing or failed required actions
cannot be skipped because a superficially similar final state exists. A 2xx/no-op is
not progress. Service recovery after failure does not authorize resume or retries.

Verified positive requires runtime verification AND independent native verification,
complete evidence, no unsafe execution, and completed (not timed-out) supervision.
Safe negative requires well-founded rejection with zero forbidden mutation; it is not
positive goal achievement. A timed-out client may leave a late mutation: retain native
achievement separately but final verified=false. An unsettled/insufficient observation
is uncertain/unverifiable, not proof of no effect. The bounded local pending counter
is not a remote cancellation guarantee or external-state attestation.

## 7. Cost collection and outcomes (proposed)

Apply [PROSPECTIVE_COST_POLICY_V3.md](PROSPECTIVE_COST_POLICY_V3.md): P1 standalone
cold start primary, P2 joint deployment and P3 prospective amortization sensitivity.
Start contemporaneous timers before the declared setup/onboarding starting point;
record activity, contributor, assistance, prior exposure, asset versions, failures,
rework, maintenance and end-of-budget status using the frozen append-only collector.
Keep human active, human AI supervision, runtime, tool/model waits and elapsed separate.
Unknown remains null. Preserve failed attempts and nested/concurrent timing. Publish
integration-only and consistently defined all-in costs rather than granting one condition
free common setup or evaluation infrastructure.

Primary reporting jointly presents (i) provider-level incremental and cold-start
human-active effort with missingness, and (ii) correctness/safety. A lower cost without
correct required behavior is not successful integration. Proposed strict integration
readiness criterion: all independently feasible required positives verified, all required
negative controls safely rejected, zero unsafe execution, with no unresolved mandatory
evidence. This is an approval-required operational criterion, not a demonstrated
population noninferiority margin.

Secondary measures: per-family verified/safe-rejection rates, partial verified transitions,
false-positive substitutions/eligibility, false-negative rejection of feasible positives,
FALSE/UNKNOWN handling, API status, actual state change, mutation counts, forbidden effects,
native/runtime disagreements, timeout/uncertainty, runtime/waits/elapsed, mapping reuse,
and maintenance/censored costs. Current single-registration diagnostics do not measure
general catalog-discovery accuracy. RQ2/RQ3 results are not inferred from these metrics.

## 8. Failure, missingness and analysis (proposed)

Create one row per planned provider/task/condition/repetition, including unrun, reset-
rejected, aborted, unsupported, timed-out and missing-evidence rows. Fix feasibility
labels before execution using independent adjudication. An intended feasible positive
that proves unsupported remains an integration failure/unsupported positive; never
quietly relabel it a successful negative or replace the task. Eligibility unresolved
is its own denominator. Report all planned attempts, feasible positives, intended
negatives, executed mutations and sufficient-observation cases separately.

Keep layered labels: contract/input/schema, semantic incompatibility, unsupported
transition/transform, FALSE rejection, UNKNOWN block, mapping/binding, transport/API,
no-op, wrong properties, forbidden side effect, stale/missing/inconsistent evidence,
observer disagreement, unsafe execution, outer timeout, budget-censored integration,
reset/environment incident, protocol deviation and unrun. Multiple labels may coexist.
Unexpected exceptions remain failures with available state recovery. CLI diagnostic
success is never substituted for end-state correctness.

Provider is the independent generalization unit. A/B are exposed development fixtures;
one held-out provider gives n=1 held-out provider, not three condition samples or
hundreds of independent task samples. Report all provider-level paired A–B, A–C and
B–C differences, setup/onboarding/maintenance breakdowns and raw task/family tables.
Within-provider repetitions show stability (counts/ranges/medians), not provider power.
No execution-level pooled significance test, provider-population confidence interval
or task bootstrap disguised as provider uncertainty. With this small design, descriptive
paired differences and explicit limitations are primary; any later provider-cluster
inference requires independent providers and prospective amendment before data collection.

Null/negative findings and no observed break-even are valid. Missing human costs remain
null with measured subtotals and coverage; no zero imputation or historical reconstruction.
Break-even beyond observed providers is a labeled model-based sensitivity analysis,
including no-crossing and high-maintenance scenarios, not empirical evidence. Correctness
agreement does not prove low engineering cost or RDF superiority.

## 9. Lock and release checklist

Investigator must approve the exact candidate and this review-document digest set,
independent semantic/native reviews, selected scope, sealed task-instance manifest,
actual schedule/roster hashes, custody/exposure declarations, cost allocation/timers,
budgets/reset/supervisor driver, stopping/analysis rules and addition-only boundary.
Keep dated detached signatures binding all artifacts. Every gate remains pending in
[SCIENTIFIC_FREEZE_DECISION_V3.json](SCIENTIFIC_FREEZE_DECISION_V3.json).

A scientific freeze decision and a **separate future unsealing authorization** are
required; neither follows from software tests, a tag, this proposed protocol, or a
public pull request. No party is asked to reveal Provider C in this milestone.
