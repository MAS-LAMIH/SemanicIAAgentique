# V4 prospective case-study execution preparation

**Prepared, not launched or authorized for provider access.** Continue from
`1e5704d7d43440f4872923582be9194805f55965` on `codex/v4-prospective-protocol`.
Only existing visible A/B descriptions/evaluation evidence were used. Provider C
remains sealed. Condition C means RDF. No integrations, provider-specific
solutions, fixtures, held-out instances or new orchestration software are added.

Companions: [session manifest](V4_PROSPECTIVE_SESSION_MANIFEST.json),
[neutral gate](V4_PROSPECTIVE_CORRECTNESS_GATE.md) and the retained
[protocol](V4_PROSPECTIVE_EXPERIMENT_PROTOCOL.md).

## 1. Protocol review and precedence

| Topic in committed `1e5704d` | Review / preparation decision |
| --- | --- |
| Three sessions, one per condition | This request explicitly plans **nine**, three per condition. This addendum/manifest records that prospective change; the original protocol is retained as historical design evidence. Approve the combined protocol/addendum before execution; do not launch under the obsolete three-session wording. |
| Proposed 20% improvement threshold | Already removed in `1e5704d`; it stays removed. No quantitative advantage threshold or statistical significance rule is introduced. |
| Primary comparisons | Already correct: **A versus B primary**, **B versus C secondary**, also report **A versus C** descriptively. |
| Correctness before effort | Retained: interpret an effort difference only after the relevant integrations pass the same independent native gate with comparable measurement. Failed/incomplete work is never a saving. |
| One-session analysis forbids within-arm summaries | With three sessions per arm, list all nine observations, completion counts and descriptive median/range only when the whole compared arms pass with observed times. Otherwise report failure/censoring and actual expenditure; do not use survivor averages to claim an advantage. No inference to provider populations or participant variability is justified. |
| Equal budgets assumed enforceable | Enforcement is not established for an AI session by the invocation supervisor. Manifest distinguishes hard-stop mechanisms that need preflight from logged-only telemetry. Resolve that boundary identically for all arms before release. |
| Gate outlined, not concretely locked | Existing driver/worker/native capture accept A/B only. The neutral specification is not an unseen-provider reader or full gate lock; eligibility and curator/reviewer artifacts remain blockers. |

Nine sessions are nine planned integration assignments on **one provider**; they
share a model/platform and are not certified independent samples. Three per arm
permit reporting observed run-to-run spread, not estimating human participant
variability or a generalizable treatment effect. The prior 96 diagnostic attempts
remain engineering background, not prospective integration replication.

## 2. Concrete session plan and equal budgets

The manifest enumerates nine logical slots, three serial scheduling groups, one
A/B/C in each group, and balanced order positions. Groups are scheduling strata,
not different providers, people or independently sampled blocks. It includes a
fully specified SHA-256-based deterministic ordering recipe and allocation seed.
Generating these **proposed slots** is preparation, not assigning live agents,
provisioning environments or running an experiment. Actual session identifiers,
model/settings, environment identities, generation seeds and observations are null.
No session has been launched, including in visible-provider mode.

Common proposed budget: **45 minutes raw release-to-stop wall time; 64 model
requests; 120,000 total input/output tokens; 256 leaf tool requests; three submitted
revisions**. One model request and one tool request may be in flight per session.
Same image, CPU/RAM, context/model/reasoning settings and documentation for all.
The scheduled maximum integration-window sum is 405 minutes, a plan, not an
observed cost; evaluation and shared preparation are separate.

| Limit | Can be enforced using existing external facilities | What is actually verified now / fallback |
| --- | --- | --- |
| 45-minute session | Operator/platform monotonic deadline plus revoking model/tool admission and exposure; retain in-flight work/overrun | No session controller is provisioned. Existing process supervisor protects invocations only. Must demonstrate on an empty/visible preflight before release. |
| 64 model requests | Count every admitted inference request, including failed requests/retries, in the selected platform/client | Platform and telemetry unselected. Exported model-call counts alone log usage, not a hard cap. |
| 120,000 model tokens | Platform hard budget, or known input token count plus bounded output admission | Provider-reported totals are usually after the response and **logged-only**, possibly unavailable. Cached/repeated inputs count under one approved convention. Do not claim a hard cap without demonstrated admission control. |
| 256 tool requests | Count/deny leaf tool dispatches in an existing gateway or controlled tool surface | A transcript can log calls but cannot stop hidden/unobserved dispatches. Do not count a batch wrapper and its leaf requests twice. No gateway is built here. |
| Three submissions | Operator accepts immutable numbered receipts 1–3 and closes at final submission/cap | Simple receipt procedure suffices; not yet exercised for a real session. No replacement runs. |
| HTTP/subject timeout | Existing HTTP 5 s and process 60 s controls; T16 uses 1 s outer / 1.5 s service delay | Present in unchanged A/B code and retained pilot evidence; no new session-level enforcement claim. |

Stop at the first enforced cap. Record actual in-flight completion/overrun; never
truncate resource logs to pretend the budget held. If a proposed hard cap cannot
be enforced, either choose an existing capable platform or obtain explicit approval
for the **same logged-target revision for every condition before exposure**.
That is a protocol amendment, not an implicit fallback. Missing usage stays null.
No new framework is needed, but an unenforceable approved hard cap blocks launch.

## 3. Exact recording procedure

Use existing platform exports plus operator-maintained JSONL/CSV and immutable
submission receipts; no new recorder service is proposed. Each session gets a
private evidence directory separate from its writable submission directory.
Collect these records (future empty paths in the manifest are not created now):

| Record | Required fields and source |
| --- | --- |
| Release/stop | Session/condition, boot/clock identity, UTC timestamp and monotonic tick at packet/endpoint access grant and at final receipt/cap/withdrawal; recorded by operator/platform, not recalled later |
| Model/tool event | Session, sequence, event ID, parent/correlation ID, request type, start/end clocks, status/error, model/version or tool name, usage source and reported token/call counts; retain failed/cancelled events |
| Submission | Sequence 1–3, trusted receipt clocks, artifact hash and diff from baseline/previous revision, final flag; receiver writes outside the agent's write access |
| Activity/supervision | Person ID, start/end, logistical/technical/engineering category, intervention and exposure note; use disjoint intervals per person. No retrospective guessed minutes. |
| Failure/rework | Event/patch/test reference, failure type, abandoned/corrected artifacts, resource use where observable; link rework to its predecessor without overwriting it |
| Evaluation | Submission hash, locked gate hash, expected policy, raw native before/after/journal, invocation result, reset/process/timeout evidence, external verdict and duration; evaluator-owned |

Primary wall integration time = monotonic elapsed from release to the receipt of
the **first submitted revision later passing the locked gate**, determined only
after evaluator review. Also report total release-to-final-stop wall time. No
internal edit is retroactively declared the completion moment. The raw 45-minute
clock includes waiting, public testing and outages; retain separately observed
outage intervals, never silently deduct them. A clock reset/lost start makes the
unreconstructable interval null, with a reason; UTC receipts do not justify
inventing unavailable monotonic measurements. One verified outage may suspend
work without pausing that cap; resume the same session only with budget left.

Model/tool durations are observed request latency unless the platform separately
exposes compute and queue time. Missing subcomponents remain null. Nested tests,
subprocesses and model/tool intervals are tagged with parent IDs and not added
again to parent elapsed time. Usage counters are not CPU seconds or human minutes.
Default observed metrics are null in the manifest; verified zero may be recorded
only with an actual observation. Reasons include not launched, not observable,
not applicable, lost telemetry and interrupted clock, not guessed values.

Public tests/failed commands/debugging during implementation count in the session
window. Final hidden evaluation is separate automation time and is withheld until
all nine sessions close. Keep all sessions/submissions, including failed/incomplete
ones, in the denominator. A human technical intervention is charged and flagged,
not free progress; the operator must not pass its content to other sessions.

Separate incremental provider-specific reading/authoring/validation/debugging from
shared technical helpers, semantic vocabulary/resolver/frontends and evaluation
preparation. Record source provenance, touched paths and generated code/data. No
shared-code edit is silently classified as onboarding. Historical V3/V4 effort
stays unknown; standalone/joint setup views retain unknowns, not zeros. No empirical
amortization or independence claim follows from nine runs on one provider.

## 4. Permitted files and unchanged shared infrastructure

Each isolated session receives an identical read-only baseline/image and public
API/task packet (packet hashes currently null). Public A/B examples and technical
facts are equally available; only the assigned integration interface differs.
The manifest stores exact current hashes and asset categories. All tracked base
files, including V3 and evidence, are read-only; no source tree is a write target.

| Condition | Provider-specific writable files (planned only) | Permitted execution use |
| --- | --- | --- |
| A | `submission/adapter.py`, `submission/entrypoint.py`, `submission/connection.json`, `submission/local_tests/**`, `submission/notes.md` | Explicit native operation routing using `api_local_v4/common.py`, ordinary `model.py`, `validation.py`, `mapping.py`, `http.py` helpers and approved standard libraries. No semantic description loader/registry as its integration. |
| B | `submission/operation.json`, `submission/entrypoint.py`, `submission/connection.json`, `submission/local_tests/**`, `submission/notes.md` | Existing JSON loader, exact resolver/invoker and common helpers; no newly coded provider conversion/repair to bypass the finite description profile. |
| C | `submission/operation.ttl`, `submission/entrypoint.py`, `submission/connection.json`, `submission/local_tests/**`, `submission/notes.md` | Same finite information/mappings/constraints through Turtle loader and the same resolver/invoker/helpers. |

`entrypoint.py` is a thin call binding, not a workflow engine. Scratch/cache paths
are private and never shared; they are not alternate locations for hidden runtime
patches. Packages/dependencies are installed in the same read-only image before
exposure. No monkeypatching shared semantics, runtime-native access, task-ID-specific
repair, arbitrary executable mapping rules, retries, planning or new provider
fixtures. An adapter may be concise and reuse helpers; A is not made verbose.

Operator verifies all manifest read-only SHA-256 values immediately before release
and at every submission/final stop; also inspect full baseline-tree diff/new files
and import/use adherence. Whole-file hashes establish byte identity, not absence
of dynamic bypasses. Check proposed entrypoint imports/call flow too. Hash missing
or changed shared code triggers a retained deviation and blocks correctness/effort
interpretation pending review; do not erase it or replace the session. Shared
runtime/vocabulary changes require a separately reviewed new baseline, not an
in-run architecture change. Current preparation changes no shared code.

## 5. Minimal isolation and supervision

1. Provision nine private existing-platform environments only after authorization;
   use the manifest's logical roots and image hash. Separate home/temp/checkout,
   writable Git object stores, memory/context and model session IDs. A shared read-
   only image/package cache is acceptable; new provider/session content is not.
2. Before exposure, use empty canaries/permission checks to verify no session can
   read another's private mounts, logs, submissions, refs or model transcript.
   Deny remote refs/collaboration/clipboard/persistent-memory paths exposing other
   new solutions. The current single workspace does not prove that isolation.
3. Operator retains hidden native/evaluation assets outside every integrator's
   access. Integrators receive documentation, public tests and API endpoints only
   after the independently reviewed gate/packet lock and release authorization.
4. Start fresh model contexts serially in proposed order; reuse no predecessor
   transcript, solution, mapping or generated description, even within a condition.
   Fix prompt/cache policy; reuse only approved prerelease examples/common assets.
5. Supervisor performs predefined logistics only (release, receipts, outage stop).
   No suggestions from earlier solutions; no same-model conversation handoff.
   Record all exposure/interventions. Any technical help/leak is a deviation,
   preserving the assignment and costs; no quiet resampling of clean-looking runs.
6. Close access at final submission/cap, retain all artifacts, then evaluate locked
   submissions without hidden feedback to still-active sessions. No release of
   protected material through logs; publication needs separate approval.

## 6. Readiness checklist

| Item | Current status | Evidence / next action |
| --- | --- | --- |
| Base identity and existing preservation | VERIFIED now | `1e5704d`; preparation only; original tracked-file hashes checked before commit |
| Nine slots / three per condition / deterministic order | VERIFIED as a plan | Parse/recompute manifest counts/order; no live session IDs or environments exist |
| No improvement threshold; comparison priorities | VERIFIED design | Base protocol and addendum retain A/B primary, B/C secondary, A/C reported |
| Existing JSON/RDF A/B information equality | VERIFIED now | Read-only normalization of existing visible descriptions; no API calls/new solutions |
| A/B diagnostic evidence integrity | VERIFIED now | Retained 96 records and existing hash inventory checked, not rerun |
| Shared asset file list/hashes | VERIFIED now | Manifest baseline hashes; actual per-session before/after checks still required |
| Exact model/settings/image/hardware | PENDING authorization | Fill common null identity fields identically; no arm-specific changes |
| Session-level time/call/token/tool enforcement | NOT VERIFIED / launch blocker | Select existing controls and preflight on empty/visible inputs; approve any common logged-target amendment explicitly |
| Nine-environment read isolation / neutral supervision | NOT PROVISIONED | Name operator, validate canaries/access rules and exposure declarations before release |
| Held-out provider eligibility, native reader, cases/answers | NOT INSPECTED / blocked | Neutral gate outline is not a completed independent gate lock |
| Independent curator/reviewer and exact gate/packet hashes | PENDING authorization | Review and lock complete artifacts before any integrator sees provider material |
| Combined nine-session addendum, budgets, cost/analysis rules | PENDING execution authorization | Review this preparation package as the operational revision; original three-session protocol remains preserved |
| Curator-only access, then integration release/execution | NOT AUTHORIZED | Separate explicit permissions; no provider access follows from this commit |

This package is reviewable preparation, not a readiness declaration or scientific
freeze. No new framework, integration, session or experiment is created/run.
