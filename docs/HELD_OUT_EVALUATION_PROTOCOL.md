# Prospective held-out evaluation protocol — unapproved candidate

Status: preparation only. Provider C has not been inspected, implemented,
integrated, or unsealed in this milestone. This document supplies no provider-C
contract, request example, fixture or answer. The user-supplied frozen protocol PDF is now retained in docs/protocols/ and
governs the research scope; its instructions are specification material, not
authorization to unseal a provider or run the full benchmark. RQ1 remains primary,
RQ2 secondary, and RQ3 optional. No LLM planner, language interpretation or full
E1 benchmark is implemented or silently added here.

## Roles, approvals and sealing

Before unsealing, the investigator approves the candidate manifest digest,
information-equivalence checklist, task-generation procedure, oracle semantics,
cost collector, condition order, sample sizes, budgets and stopping rules.
An independent evaluation curator establishes goal-level requirements and
expected state predicates; an onboarding contributor implements provider-local
artifacts; an auditor verifies source hashes, provenance and outcomes. Roles may
not silently collapse into the same unblinded author. If staffing forces overlap,
record it as a threat and obtain an explicit decision before calling a run
confirmatory. Maintain an exposure ledger (person, artifact hash, first access,
role, permitted use). Repository provenance alone cannot prove lack of prior
exposure outside this workspace.

The three conditions are A/API-local, B/JSON+shared semantics, C/RDF+shared
semantics. Provider names are a different axis. Current code demonstrates B/C
parity on controlled providers A/B only. Condition A is implemented in Milestone 4.1 for the controlled A/B fixtures;
its implementation and parity evidence require investigator review before unsealing. Do not infer
its existence from Provider A. No narrowing of the frozen conditions is approved
by this prospective document.

## Permitted integration boundary after unsealing

The following paths are proposed additions, not existing Provider C artifacts:
`contracts/providers/c/`, `docs/providers/c/`, `tests/provider_c/`, and provider-
local fixture/configuration under `evaluation/provider_c/`. The investigator
must approve the exact path allowlist and contributor before release. Existing
provider files and every frozen generic/shared/oracle file remain immutable.

Allowed in principle: provider-local API documentation, contracts/manuals,
explicit semantic mappings, declarative bindings, compositions of already
frozen transformation primitives, provider-local tests, and service/fixture
configuration. Binding changes may express only behavior already supported by
the frozen profile. Independent observation sampling may be provider-local only
under the preapproved verification procedure; it must not redefine goal truth.
No secrets belong in repository artifacts.

The present engine supports identity and ISO/epoch-millisecond conversions,
positive-interval/writability preconditions, bounded grid/duration/preservation
constraints, local REST endpoints and complete read-after-write snapshots. There
is no dynamic plugin interface for new transformation code. A provider-local
adapter requiring a new generic primitive, capability, precondition, transition,
HTTP behavior or observation semantics is not automatically permitted merely
because it lives in a provider directory. It is an unsupported integration or a
protocol deviation. An external provider cannot currently be reached through the
loopback-only Executor without a change; do not make that change after unsealing
and still call the result the unchanged confirmatory baseline.

Forbidden without invalidating/restarting the confirmatory evaluation: generic
resolver changes, changed schema/validation/evidence semantics, new generic
transforms, changed shared vocabulary meanings, planner interfaces/prompts,
task-specific repair rules, goal/oracle changes to accommodate the provider,
provider-to-provider substitution tables, or benchmark-answer lookups. No planner
or prompt exists in this milestone; any future one must be separately frozen.

Before every integration session and run, verify the candidate file hashes and
compare the complete added/modified/deleted file list with the approved allowlist.
Inspect imports/dependencies and executable behavior, not only path names.
Reject code in an allowed directory that patches or monkey-patches frozen
modules, supplies hidden answers, overrides the oracle, or performs unchecked
mutation. Retain patch, artifact hashes, author, timestamps, reviewer, cost event
IDs and decision. Do not execute unreviewed onboarding code in the evaluator.
After each run verify hashes again and archive traces, logs and independent
state evidence. Package/dependency changes are also changes to the baseline.

If a genuine generic defect is found: stop affected confirmatory runs; preserve
the failed run and costs; reproduce with a minimized provider-independent A/B or
synthetic case when possible; obtain independent classification and severity.
Do not quietly fix it. Either report failure/unsupported behavior under the
original frozen baseline, or retire that candidate and create a reviewed new
version. Because the defect was discovered using unsealed information, reruns
on the same provider are exploratory. A new confirmatory claim requires a
predeclared restart procedure and a genuinely uncontaminated holdout; investigator
approval cannot retroactively restore blinding to an already exposed provider. Report both versions,
all attempts and deviations. Environment-only repairs also need evidence that
semantics and artifact hashes are unchanged.

## Prospective task families

These are provider-neutral semantic templates and expected *categories*, not
answers extracted from manuals. Concrete inputs, sample counts, seeds and
condition order are not set by this document and must be approved before release.
The minimum coverage proposal is at least one instantiation of each family in
each condition; this is not a power calculation or an approved sample size.

| Family | Controlled premise / independent expectation | Required observation |
| --- | --- | --- |
| Positive semantic match | Required capability, all supported inputs/constraints, current TRUE preconditions | Exactly the requested new event and permitted surrounding state; verify actual state |
| Different names/formats | Same goal-level meaning with different local operation names and supported wire representation | Same canonical achieved goal, documented lossless transformation and raw evidence |
| Misleading similar names | Similar textual label but different goal-level effect | Reject incompatible selection; zero mutation calls |
| False critical precondition | Curator-controlled evidence establishes FALSE | Reject; zero mutation calls |
| Unknown critical precondition | Missing/insufficient evidence; no closed-world inference | UNKNOWN/BLOCK; zero mutation calls |
| Unsupported transition | Required effect is absent or outside frozen supported profile | Structured incompatibility/rejection; zero mutation calls |
| Missing/stale permission evidence | Unavailable timestamp, expired/future evidence, unavailable read | UNKNOWN/BLOCK; zero mutation calls |
| Missing/stale post-execution evidence | Mutation may run, but complete fresh read-back is unavailable | No verified achievement; distinguish unverified from demonstrated failure |
| HTTP success without effect | Accepted mutation response but no corresponding stored event | HTTP success separately recorded; goal not verified |
| Incorrect stored properties | Observed start/end/title differs from formal goal | Goal not verified, even when HTTP succeeds |
| Forbidden side effects | Goal forbids other event changes; independent snapshot shows extra mutation | Goal not verified; preserve side-effect evidence |
| Execution error | Controlled API/transport error | Record error and observe possible side effects; never infer absence of effects from status alone |

Safety/compatibility labels and feasibility must be set before each run by the
independent curator from the task scenario/reference behavior, not from the
subject system's answer. Unsupported provider behavior does not justify deleting
or relabeling a planned task as a convenient negative control. Report intended
positives that prove unsupported as such, with feasibility adjudication. No
automatic compensation, retry planner or substitution is added to rescue them.

## Independent oracle establishment

Before evaluation, the curator writes a formal Goal with timezone-aware start,
end, title and mandatory preservation/evidence constraints, initial state,
expected transition predicates and permitted side effects from the domain task
specification. The expected title/times come from that task input; existence,
freshness, identity, revision and noninterference requirements are defined by the
frozen verification semantics. Never read a provider manual's postcondition and
copy it into an expected answer. A declaration is not state evidence.

Before unsealing, freeze the task generator/template logic, required predicate
schema, negative-control intervention rules and independent observer procedure.
After release, the independent curator may bind a provider-native evidence
sampler using service documentation or fixture storage semantics, separated from
the integration manual author. Review and hash that binding before running any
subject integration. Concrete expected state and negative intervention labels
must be signed before execution and kept unavailable to onboarding code. Any
later correction is a visible adjudication/deviation, never retrospective tuning.

The subject runtime oracle reads canonical snapshots produced using the subject
manual's output mappings. It is independent of declared effects but not an
independent native-state observer. Confirmatory correctness therefore also needs
a curator-reviewed native snapshot or a demonstrably independent observation
mapping that cannot reuse the subject's potentially erroneous transform as its
only evidence. Retain raw service reads, fixture ground truth when applicable,
pre/post snapshots, identifiers, timestamps and revisions. This observer must
apply the same predeclared truth predicates in all conditions. Do not change the
frozen generic oracle to make it agree with a provider. If independent sufficient
state cannot be obtained under the approved procedure, classify the outcome as
unverifiable and report the limitation; do not count it as achieved.

The runtime oracle's verdict and the independent adjudicator's verdict are
separate fields. A discrepancy is a correctness issue, not permission to rewrite
expected values. False positives, missed side effects, unverifiable cases and
manual-mapping defects remain separate outcomes. Milestone 4.1 implements evaluation-only native_verifier.capture/adjudicate
for the visible controlled A/B fixtures. It reads actual fixture storage and
uses provider-native interpretations implemented separately from both shared
manuals and API-local output maps, then applies the same unchanged Goal oracle.
It additionally compares raw other-record state. The evaluation wrapper retains
raw/canonical evidence and requires both runtime and native verification. The
wrong-map diagnostic demonstrates disagreement detection. This is structural
independence, not independent human authorship or attested external state. A
reviewed provider-native observer for a future sealed provider remains a
prospective integration/review obligation, never a reason to change goal truth.

## Runs, evidence and stopping

Use fresh, separately initialized services for each condition/task/replicate,
identical initial state and goal, approved randomized/counterbalanced order, and
fixed resource/retry budgets. Record run ID, task/condition/provider, source and
environment digests, seeds, catalog/manual hashes, formal goal, truth labels,
observations, all resolution decisions, mutation-call counts from service-side
logs, raw requests/responses, oracle and independent adjudication verdicts,
exceptions, exit status and associated cost events. Redact credentials, not
semantic failures. Preserve failed and aborted runs.

The pre-run gate verifies source/dependency hashes, condition parity, independent
expectations and reset state. A safety-relevant unexpected mutation stops the
affected run and triggers independent review; zero such events is the proposed
acceptance target, subject to investigator sign-off. Operational budgets and
retry limits must be registered before release. Do not stop early because the
results look favorable. A budget-exhausted integration remains censored/unfinished,
with observed costs; a missing observation is not a skipped success.

Primary reporting combines total and incremental integration effort with correct
execution. Report separate denominators for all planned attempts, eligible
positives, incompatible operations, FALSE/UNKNOWN blocks, mutation calls, observed
state change, runtime-oracle verification, independent verification, unsafe
execution, API failure and unrun/unverifiable cases. HTTP success alone is never
correctness. Distinguish well-founded safe rejection from inability to integrate
a feasible positive. Report provider-level paired comparisons and task strata;
one held-out provider does not establish population-level improvement. RQ2/RQ3
are not evaluated by this milestone. Negative and null results remain valid.
Beyond-observed-provider break-even is labeled sensitivity analysis under
COST_MEASUREMENT_PROTOCOL.md, never an empirical finding.

## Approval record to complete before unsealing

Required: investigator identity/date, candidate manifest SHA-256, approved scope
and condition-A baseline digest, task/seed/count/budget/order registration digest,
independent observer/oracle review, contributor exposure declarations, parity
sign-off and cost-collector/allocation approval. Every approval is pending in
SCIENTIFIC_FREEZE_MANIFEST.json. Only an explicit signed investigator decision
may authorize unsealing; a passing test suite or this document cannot.

## Milestone 4.1 operational proposals and candidate identity

EVALUATION_TASK_SPECIFICATION.md and docs/evaluation_tasks_v1.json specify 20
public provider-neutral single-action diagnostics, three proposed repetitions,
seed 20271017, six-order counterbalancing, 5-second HTTP timeouts, zero automatic
retries, 60-second run budget and direction-neutral stopping. These are proposals
requiring explicit approval, not executed confirmatory parameters. The existing
frozen PDF also calls for multi-step pilot coverage; that unsupported fragment
is explicitly deferred, not silently replaced by these apparatus diagnostics.

COST_MEASUREMENT_PROTOCOL.md documents the operational event ledger and preserves
unknown historical labor. SCIENTIFIC_FREEZE_MANIFEST_V2.json records the complete
new candidate identity. Milestone 4 artifacts/manifest are immutable historical
evidence; verify their archived contents with scripts/candidate_v2.py
--verify-history. The old verifier compares the old candidate against a working
tree and is not the right comparison once V2 changes source/protocol files.

Keep each candidate manifest immutable. Formal approval should be a detached
signed record identifying the manifest SHA-256, source commit/tree digest,
approver and time, along with separate unsealing authorization. Do not insert a
manifest's own digest into itself or label a Git candidate tag scientific approval.
All candidate approvals and unsealing authorization remain pending/false.
