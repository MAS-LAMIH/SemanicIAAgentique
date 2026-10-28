# V4 prospective interoperability case-study protocol

**Status: investigator design preferences incorporated; execution and release
authorization remain pending.** Based on GitHub `main`
`0372f3b507fdb1e1bffe48c00074cb30ec62e6a0`, which contains V4 implementation
`61f96e9` and comparative pilot `1ffd87f` through merge #9. This document alone
neither authorizes unsealing nor supplies a provider integration. Provider C
remains sealed; no implementation, manual, task instance or answer was inspected
in preparing this protocol. Condition C below means RDF, not Provider C.

Reviewed references: [architecture](V4_SIMPLIFIED_ARCHITECTURE.md),
[minimal experiment](V4_MINIMAL_EXPERIMENT.md),
[pilot report](V4_COMPARATIVE_PILOT_REPORT.md) and
[pilot instructions](../v4/PILOT_README.md). The pilot establishes engineering
feasibility on visible A/B, with 96 repeated diagnostic attempts, not 96
independent integrations or measured historical onboarding effort. V3, its frozen
protocol and all completed V4 evidence retain their original meanings and bytes.

## 1. Questions, estimands and falsifiable hypotheses

The target is onboarding an unseen provider to the **existing fixed V4 capability
profile**, not arbitrary Web APIs. The current profile is one EventCreation
capability, canonical time/title inputs and returned ID, flat mappings, supported
precise conversions and ordinary API bounds, fixed local POST operations and
structured results. It contains no action contracts, effects, state transitions,
semantic precondition calculus, runtime behavioral proofs, planning or repair.

**RQ1, primary — A versus B:** once both integrations meet the same independent
correctness gate, how does actual wall-clock provider-integration time differ
between a competent API-local adapter and reusable JSON capability descriptions?
**RQ2 — functional correctness:** can each condition produce usable invocations,
correct native storage, correct rejection and truthful error/timeout handling?
**RQ3 — semantic reuse:** can the existing capability meaning, roles, conversions
and invocation code be reused with provider-local descriptions/configuration,
without shared-engine changes? **RQ4, secondary — B versus C:** how do JSON and
RDF integration time, resource use, correctness and authoring failures differ
when their supported information is equivalent? Also report **A versus C** as an
additional descriptive comparison; it is not a second primary comparison.

Falsifiable case-level propositions, not statistical hypotheses:

| Proposition | Observation inconsistent with the proposition in this case |
| --- | --- |
| H-F: each of the three assigned integrations meets the full correctness gate within the equal resource budget | An assigned integration fails, times out or remains incomplete; identify that session/condition, without generalizing to all contributors or APIs |
| H-E: after A and B both pass the gate, B takes less observed wall-clock integration time than A | With complete comparable timing, B takes the same or more time; if either fails or timing is missing, the effort proposition is unestablished |
| H-R: correct B/C submissions reuse the existing shared semantics and need only provider-local descriptions/configuration | A correct submission requires a new meaning, conversion or generic runtime behavior, or B/C cannot meet the gate unchanged; record attempted shared changes even though prohibited |

There is **no percentage improvement threshold or effort-based success criterion**.
Correctness is the prerequisite for interpreting effort differences, not an
outcome to trade away for speed. Report observed differences in either direction;
do not declare an overall winner from a time comparison alone. For B/C or A/C,
likewise interpret effort only when both relevant integrations pass the same gate
and timing is comparable. No superiority hypothesis is presumed for RDF or JSON.
H-R is conditional on profile eligibility and does not deny A's technical reuse.
A failed or incomplete integration remains in the report with actual time spent;
its quick termination is not an effort saving.

## 2. Case-study units and assignment

The initial design is **three isolated AI integration sessions: exactly one each
for A, B and C, on one previously unseen provider**. This is a prospective,
unreplicated single-provider case study, not a statistically generalizable
experiment. It cannot estimate participant variability, within-condition variance,
model stochastic variability or population treatment effects. No human-only or
multi-session arm is part of this initial design; such extensions need a separate
prospective decision rather than being pooled with these three observations.

The assignment unit is one fresh AI session integrating this provider in one
condition. Fix the same exact model/version, reasoning settings, available context,
tools, hardware class and resource budgets across all three. Before exposure,
assign conditions to three anonymous session slots by a recorded random
permutation, using proposed allocation seed `20270319` and a specified PRNG/version.
Generate that schedule only after operational authorization; no allocation is
executed by this document. Run serially on equivalent infrastructure in the drawn
order, with no solution transfer or temporal tuning. With only three sessions,
random ordering does not estimate or eliminate order/learning effects. Record
model generation seeds if supported, otherwise null; do not invent them or run
extra sessions to select favorable outputs.

Fresh sessions must have separate writable filesystems, context, persistent
memory, branches and logs. Deny access to another condition's newly authored
solutions, transcripts, tests and remote refs. A fresh chat alone is insufficient
if storage or memory is shared. No session implements the provider in a second
condition. No supervisor may transfer a discovered mapping or correction across
assignments. Do not generate C's submission from B's newly authored JSON, or the
reverse. Within-arm tools and previously approved exemplars remain allowed under
the equal tool policy; record artifact provenance.

Declare prior exposure before release: provider/API/task access, repository/pilot
familiarity, model/tool familiarity, authoring/custody roles and known examples.
The provider author, native-oracle curator and reviewer do not direct integration
solutions. Give the sessions the same visible A/B familiarization and log that as
setup, not new-provider work. Do not tune prompts or models from earlier results.
Supervision is limited to predefined logistical actions. Technical intervention,
if unavoidable, is recorded as assisted work and a protocol deviation; it cannot
be hidden, repeated in other arms as advice, or used to replace a failed session.

There is **one provider unit and three integration-session observations**. AI
sessions share weights/training and possibly an operator/platform; isolation
limits leakage but does not establish statistical independence. Tasks, test runs,
submissions, seeds and restarts are repeated measurements within a session, not
new independent integrations. The existing 96 A/B pilot attempts are background
diagnostic executions, not integration replication for this case study.

## 3. Treatment and fairness controls

| Condition | Provider-specific work | Shared assets permitted |
| --- | --- | --- |
| A: API-local | Explicit provider/native-operation dispatch, request/response adapter and declared input limits | Existing ordinary validation, exact conversions, HTTP/result helpers, competent local adapter examples and ordinary programming libraries |
| B: JSON semantics | Independently author a JSON mapping from native operation/fields to the existing capability and roles | Frozen vocabulary/profile, JSON loader, resolver/invoker and common technical helpers |
| C: RDF semantics | Independently author equivalent profile information in Turtle | Same vocabulary/profile/resolver/invoker, RDF frontend/parser and common technical helpers |

Every unit receives the same provider API documentation revision, canonical task
specification, operational access, examples supplied by that documentation,
public tests/feedback, environment readiness, hardware, language, editor, model
access (if applicable), command/time limits and help policy. The declared API
limits, validation power, output obligations, timeout controls and external oracle
are equal. Tool availability is equal; the assigned representation/interface is
the treatment. Condition-specific instructions may explain syntax/entry points,
but not supply extra provider facts, solved mappings or stronger hints.

A need not hand-write HTTP or timestamp conversions or simulate semantic lookup.
It may use concise functions and any approved common helper. It may not invoke
the semantic registry/description loader as its integration, since that changes
the treatment. B/C receive no pre-authored new-provider mappings. All arms may
inspect the same public A/B exemplars and specifications; any differential access
to legacy examples must be removed before release. The post-pilot V4 helper
extraction is already part of the starting infrastructure and is not recharged
as provider onboarding work.

B/C start with equal reusable meanings, supported roles/mappings, input limits,
precision rules and validation power. After all independent submissions are
locked, audit normalized submitted descriptions. Differences caused by authoring
errors are outcomes, not permission to repair one condition from the other.
Compare intended semantic assignments and independent correctness as well as
serialization. Identical identifiers alone do not establish correct meaning.
No post-submission information balancing may erase integration defects.

Before release, identify exact code/data/environment hashes, public examples,
condition-specific asset allowlists and permitted provider-local write paths.
Common runtime/vocabulary/validator/transport files are read-only in every arm.
New generic features or task-specific repair rules are out of scope. Record
attempted shared changes and their stated need; do not silently permit them in
one arm. A genuinely discovered baseline defect pauses the affected comparison,
retains all attempts/costs and requires an explicit revised-baseline decision.
An already exposed provider cannot then be relabeled unseen in a restart.

**Eligibility uncertainty:** no claim is made that the sealed provider fits V4.
After separate authorization, a custodian must assess it against the previously
specified flat/local/POST/representation limits without revealing solutions to
contributors. A neutral transport/fixture qualification must not favor either
representation. If it requires unsupported auth, nested data, transformations or
capability meanings, classify the fixed-baseline case as out of scope/blocked;
do not redesign V4 or cherry-pick a replacement after viewing condition outcomes.
Any replacement/scope revision needs a newly declared study and exposure record.

## 4. Measurements and stopping rules

The same explicitly specified budget applies to each of A, B and C:

| Resource | Per-session limit |
| --- | --- |
| Wall-clock integration window | 45 minutes, packet/endpoint release to final submission or stop; includes reading, model/tool waits, public testing, failures and rework |
| Model calls | At most 64; one in flight at a time |
| Model token use | At most 120,000 total input plus output tokens across calls, including repeated/cached inputs; use one documented accounting convention in all arms |
| Tool calls | At most 256; one in flight at a time |
| Submitted revisions | At most three; final submission or first resource cap ends the session |
| Execution environment | Identical image, CPU/RAM allocation and model context/reasoning limits, recorded and locked before exposure |

Stop at the first cap; no automatic session replacement or cross-condition help.
Exact model and hardware/context settings still require investigator selection,
but must be identical and fixed before release. A call/token cap must be enforceable
under the selected model/tool telemetry; if not, pause preparation and approve a
common documented revision before exposure. Missing retrospective telemetry remains
null, not a guessed usage total. Public tests may run during development, with
all costs included. No budget increase may depend on seeing condition outcomes.

Measurement begins when the new-provider packet/endpoint is first released to
the unit, including reading and understanding it. Required environment setup is
completed/checked on visible APIs beforehand; any new-provider setup remains a
charged, separately tagged activity. Stop clocks at submission, caps, withdrawal
or documented interruption, never retrospectively at a guessed moment of success.
The evaluator later identifies the first submitted revision passing the locked
gate. Do not grant new implementation time after seeing final evaluation results.

| Quantity | Prospective definition / unit |
| --- | --- |
| Human-active engineering | Timed provider-document reading, design, editing, testing, diagnosis and review; person-minutes summed over people, with activity intervals |
| Human AI supervision | Active prompting, monitoring requiring attention, reviewing generated work and intervening; person-minutes, mutually exclusive with that person's engineering intervals |
| AI-assisted execution | Orchestrator release/submission/model/tool timestamps; agent-controlled phase elapsed plus available model/tool execution durations, calls and billed tokens; not invented human-equivalent minutes |
| Waiting | Model queue/response, tool and infrastructure waits where observable, separately; if model compute versus wait cannot be separated, retain a combined latency field and unknown subfields |
| Automation | Test/build/evaluation/process wall runtimes and available CPU metrics, with nested/overlapping intervals labeled to prevent double counting |
| Total elapsed | Monotonic release-to-stop wall time and UTC boundary timestamps, including waits and outages; retain outage intervals separately |
| Change surface | Added/modified/deleted physical source/data lines and files; provider-local versus shared proposals/changes; generated versus authored artifacts; ordinary versus semantic setup |
| Debugging and rework | Failed tests, abandoned patches, model/tool failures, correction iterations and technical help with actual time/resource records |
| Completion/correctness | Gate pass/fail, time of first passing submission, tests/attempts passed by family, unsafe mutation, error/timeout/uncertainty and unresolved defect classes |

The primary timing measure is **actual wall-clock integration time**, observed
from release to the first submitted revision later found to pass the locked gate.
For every session also report total release-to-final-stop wall time, including
work after that first passing revision. These are measured elapsed intervals,
not estimated CPU execution or human-equivalent engineering minutes. If no
submission passes, report actual time/resource use to stop and censored time-to-
gate, with no fabricated successful completion time. Keep verified external-outage
intervals separately visible; raw wall time is primary, while an outage-adjusted
sensitivity may be reported if its intervals are observable. Do not silently stop
the primary wall clock or subtract unmeasured waits.

Record model/tool calls, token usage and observed latency/execution intervals,
supervision, failures, abandoned patches and rework alongside timing. Separate
human-active engineering from human supervision if either occurs, with no double
counting; keep unobserved categories null. A supervisor who learns a solution
cannot guide another condition's integration. No historical V3/V4 effort is
reconstructed, and no timing result is interpreted before correctness is known.

Keep missing measurements null with a reason. Distinguish verified zero from
unobserved time. Preserve unfinished assignments, failed submissions, crashes,
queue failures and timeouts in the assigned denominator. Time-to-gate for failures
is censored at the recorded limit/withdrawal; show actual effort spent and censor
reason, not a fabricated completion time or a successful-only average. Report
all three completion statuses first; do not substitute successful-only averages
or an extra session for a missing/failed condition.
External outages suspend exposure/work for the affected session, retain the raw
elapsed clock and logs, and invoke the predefined interruption rule. Proposed
rule: suspend work only for a verified infrastructure outage, with no off-clock
access/work. The raw 45-minute cap keeps running; resume the same session at most
once and only if budget remains. An exhausted cap or second outage yields
incomplete/censored status.
No quiet replacement sessions. Participant mistakes count as integration failures.

Separate shared technical setup, shared semantic/vocabulary setup, frontend setup,
provider onboarding, debugging/testing and later maintenance. Reused infrastructure
is identified by provenance/hashes; historical V3/V4 human costs remain unknown.
Report incremental onboarding against installed infrastructure as primary. Show
standalone setup requirements and joint-deployment shared costs separately; unknown
setup costs remain null rather than zero. Any amortization/break-even projection
beyond observed providers is sensitivity analysis, not measured evidence.

## 5. Independent native-state gate, locked before provider release

The curator, distinct from integrators, establishes native interpretations and
expectations from the domain task and provider service/storage specification.
They must not derive answers from any condition's descriptions, encoders, output
mapping, runtime result or submitted solution. An independent reviewer checks
those interpretations and representative native before/after examples. Record
actual author/reviewer identities and conflicts; code separation alone is not
independent human curation. If independent review is unavailable, declare that
limitation and keep confirmatory claims disabled.

The **complete independent native-state gate must be locked before releasing
held-out provider API/task documentation, endpoints or other integration-facing
materials to any of the three sessions**. Lock the exact concrete cases, expected
native verdicts, reader/oracle implementation, public/hidden split and reviewer
record with hashes. Family definitions alone are not a sufficient gate lock.
The same locked packet and native checks apply to A, B and C.

Provider C stays sealed during this task. If a complete reviewed gate already
exists under custody, verify its identity through the authorized custodian before
integrator release. If it does not exist, release to integration sessions is
blocked: only a separate, explicit, narrowly scoped custodian/curator authorization
can permit preparation and eligibility assessment. That authorization is not
integration release, and cannot expose solutions/answers to the integration
sessions. Complete and review the gate under custody before any session gets the
provider. No provider-specific instance, reader or answer is authored here.

Proposed final gate: the 16 family meanings T01–T16 in the minimal experiment,
with **two disjoint hidden instances per family** (32), plus a common public
smoke/diagnostic suite for development. Final requirements are 32/32 expected
diagnostic outcomes, no unauthorized mutations in rejection cases, usable outputs
for normal positives, and honest timeout/error handling. The final set must
include representable valid cases and provider-specific unsupported inputs. A
curator must mark applicability before results: if an original family cannot be
instantiated for the eligible provider, keep its omission explicit, revise the
exact denominator/gate before integrator release and seek approval. Never relabel
N/A as a pass or choose families based on which arm succeeds.

Native checks require the correct newly stored identifier/properties/instants,
no unintended change to existing sentinel records, appropriate native counters
and consistent usable returned output. Validate precision, ordinary invalid inputs,
permission denial, service error, misleading capability/task requests, no-change
HTTP success, wrong stored properties, side effects, missing returned identifiers
and delayed mutation. No runtime behavioral proof is required. All conditions
face the same service faults, inputs, native reader and acceptance rules.

A deliberately faulty service is not expected to become correct because of the
integration. Its diagnostic passes if the separate evaluator rejects domain
success and the invocation does not misreport its HTTP/error/output outcome.
This is external fault detection, not a claimed runtime ability to detect wrong
storage. Likewise, a valid missing-ID response can leave native creation correct
while invocation output is unusable. Report each axis independently.

Every final case gets a fresh supervised child, fixture, registry context and
trace path. Reject dirty records, permissions, revisions, counters, pending work
or reused trace paths before launch; preserve the rejected reset without clearing
it. Default HTTP/outer budgets remain 5/60 seconds. The delayed-mutation diagnostic
uses the disclosed one-second outer/1.5-second service delay, identically for all
arms. Kill/reap evidence and bounded post-stop observation remain parent-owned.
Initial unsettled state stays uncertain; later observation cannot turn a timeout
into an accepted invocation. No automatic mutation retry or compensation.

Primary evaluation is one fixed-order pass of each locked case per submitted
revision, identical schedule across conditions. No automatic rerun converts failure
to success. A documented evaluator/infrastructure fault may trigger one separately
labeled repeat under a predeclared adjudication rule; retain both outcomes and
decision. Integration/provider failure is not a rerun reason. Final evaluation
time is recorded outside authoring effort; public test use during development
counts within the assignment budget. Detailed hidden verdicts are withheld until
all assignments close; earlier submissions receive only receipt acknowledgments.
This prevents repeatedly learning the hidden suite while timing authoring.

## 6. Practical execution sequence (future authorization required)

1. **Approve and prerecord:** settle the decisions below, identify a documentation
   revision plus immutable implementation/environment hashes, designate custodian,
   curator/reviewer, assignment operator and analyst, and declare conflicts.
   Keep the provider sealed. No approval is implied by repository presence.
2. **Prepare without exposure:** validate the existing machinery and clocks on
   visible A/B; provide equal familiarization, baseline examples and tool training.
   Prepare three isolated session slots, generate the recorded random assignment
   and serial execution order. Inspect packet/workspace access rules, not sealed materials.
3. **Authorize custody release separately:** only the approved custodian/curator
   may inspect the provider solely for eligibility/gate preparation if that
   separate authorization exists. Lock and independently review the complete
   service/docs/tasks/native gate before any integration-session release.
   Provider authors/curators do not serve as fresh integration contributors.
4. **Release equal packets:** provide the same API/task facts to the isolated
   units in their scheduled slots, start clocks and exposure logs, prohibit
   cross-arm solution exchange. Integrators get public API access and public
   tests, not native storage, oracle implementation/answers or hidden-test files.
5. **Implement and measure:** units edit only provider-local permitted artifacts,
   run public tests, submit at most three snapshots, and stop at final submission
   or cap. Capture diffs, prompts, outputs, resource intervals and all failures.
   Session debugging/rework stays inside the budget. Human technical help is a
   logged deviation; automated runtime planning/repair remains excluded.
6. **Evaluate locked submissions:** preferably an analyst sees neutral submission
   IDs until correctness decisions are recorded; record if paths/syntax reveal
   the condition. Apply the same independent native gate without arm-specific
   fixes. Any B/C normalization comparison occurs only after submissions close.
7. **Report every assigned unit:** publish packet/base identifiers, exposure and
   schedule, completion/failure/censoring, effort/resource/change tables, native
   safety results, deviations and exclusions. Release protected materials only
   under separately approved custody policy, never through an incidental log dump.
   Preserve V3 and pilot evidence; no post-hoc architecture or answer adjustment.

A compact run manifest, exposure/activity log and versioned submissions suffice;
no new governance framework is proposed. Actual identities/signatures, artifact
hashes, budgets and release permissions must be supplied by authorized humans,
not inferred or invented by an assistant.

## 7. Analysis and threats to validity

Publish one row for each of A, B and C, including correctness, time-to-gate or
censoring, total wall time, model/tool usage, supervision, failures, rework and
provider-specific change surface. **A versus B is primary; B versus C is secondary;
A versus C is also reported descriptively.** Report completion and native safety
first. Only for a pair in which both integrations pass and timing is comparable,
interpret the observed wall-time difference and optional ratio; if the denominator
is zero or a measurement is missing, the ratio is undefined. Do not impose an
improvement threshold or label a small time difference a demonstrated advantage.
When either condition fails, report the feasibility discrepancy and actual effort
spent, without making a correctness-controlled effort-benefit claim.

With one session per condition, report the three actual observations, not medians,
within-condition ranges, confidence intervals, p-values or an estimated treatment
effect. No significance testing or inference about participant/model variability
is supported. Preserve all assigned sessions and deviations, with no outlier
exclusions, best-of-several model sampling or quiet replacement. Any later
replicated, multi-provider study needs its own prospective sampling and analysis
plan; additional diagnostic test invocations do not supply that replication.

Important threats remain: one chosen provider and one capability; eligibility
selection favoring the existing profile; contributor skill and format familiarity;
previous pilot/domain exposure; shared AI model training and stochastic/session
correlation; supervision leakage; unequal documentation clarity; imperfect time
instrumentation; hidden-test coverage; fixture/oracle common-mode mistakes;
constrained loopback transport versus real authentication/network behavior;
and code-line counts being formatting-dependent rather than effort measures.
Shared infrastructure may amortize differently in practice; neither its absence
from incremental time nor its unknown historical cost implies zero total cost.

A prospective single-provider case study can falsify feasibility for that case,
expose defects and document conditional effort/reuse under controlled access.
Three isolated sessions cannot estimate participant/model variability, and one
provider cannot represent heterogeneous APIs. Replicated sessions would be needed
to study participant/model variation; additional independently selected providers
would be needed for provider-general claims. Neither is part of this initial case
study. Existing 96 A/B pilot attempts remain diagnostic background, not integration replication.

## 8. Decisions requiring investigator approval before unsealing

The investigator's design preferences are incorporated: a single-provider case
study; one isolated AI session per condition; A/B primary, B/C secondary and A/C
reported; no percentage threshold; correctness before effort interpretation;
observed wall time/usage/supervision/failure/rework measurement with nulls for
missing values; equal budgets/documentation; a locked independent native gate;
and incremental/shared-cost separation. These design choices do not authorize
provider access or study execution.

The following operational decisions remain **PENDING**:

| Decision | Required authorization before release |
| --- | --- |
| Model, resources and measurement | Choose exact model/version, reasoning/context settings and identical CPU/RAM/image; approve the equal 45-minute/64-model-call/120,000-token/256-tool-call/three-submission limits, enforceable telemetry and outage rule |
| Session assignment and exposure controls | Approve three isolated environments, assignment seed/PRNG and serial schedule, common prompts/training/tools, logistical-only supervision and actual exposure/conflict declarations |
| Immutable baseline and eligibility | Record exact code/data/environment/example hashes, provider-local write allowlists and neutral profile eligibility; approve handling of shared defects/out-of-scope cases without in-run architecture changes |
| Independent native-state gate | Approve final applicable families/denominator, public/hidden instances, native reader/answers and independent review; lock all before any provider documentation/endpoint reaches an integrator |
| Custody and separation of roles | Name the custodian, provider author, curator/reviewer, operator/supervisor and analyst; approve declared conflicts/overlaps; separately authorize any necessary curator-only gate preparation |
| Cost recording and retention | Approve observable wall/model/tool/supervision/failure/rework logs, incremental provider work versus shared infrastructure allocation and null/missingness policy; protect all existing V3/V4 records |
| Provider release and execution | Explicitly authorize release of the identical provider API/task packet to the three sessions only after the reviewed gate lock and all prerequisites; approve later retention/publication of protected artifacts separately |

Approval of this protocol, approval of eligibility/gate preparation, and permission
to release Provider C to integrators are distinct decisions. Until the appropriate
authorized decisions exist, do not inspect the provider, author its integration,
instantiate its hidden task answers or execute this study.
