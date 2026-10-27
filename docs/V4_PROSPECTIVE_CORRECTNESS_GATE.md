# V4 provider-neutral correctness gate — preparation specification

Status: specification only; **held-out gate not instantiated or approved**.
No Provider C material was inspected, no provider-specific reader/solution/task
answer was created, and no prospective session or experiment was run. Condition C
means RDF. This document supplements protocol `1e5704d` and the nine-session
[preparation addendum](V4_PROSPECTIVE_EXECUTION_PREPARATION.md).

## Existing evidence and implementation boundary

The visible A/B reference is `v4_pilot/native.py:adjudicate`, with tasks and public
expectations in `v4_pilot/tasks.py`, process/reset controls in
`v4_pilot/driver.py` and `src/semantic_action/supervision.py`, and retained results
in `docs/artifacts/v4_pilot/run-001/`. The previous pilot's 96 attempts are diagnostic
background, not fresh onboarding observations or a held-out gate lock.

The existing `capture`/`decode` implementations and worker/driver provider guards
are A/B-specific. Do not pass a new provider as `b`, treat the decoder's non-A
branch as a general provider reader, or claim this driver already supports an
unseen provider. A separately authorized curator must prepare a provider-local
native reader/fixture entry point and a thin evaluator-side invocation shim, then
have them reviewed. Those are evaluation assets, inaccessible to integration
sessions; they are not new shared V4 runtime features or runtime mappings. None
is implemented here. Current V4 HTTP execution also requires loopback/local POST
and its finite mapping profile; eligibility remains unverified without unsealing.

## Independent inputs and observation rules

Before any provider documentation/endpoint reaches an integrator, lock: service
and API-document versions, public task packet, hidden instances, native-reader
code, expected outcomes and independent review identities/hashes. Provider
creation behavior is judged from task inputs and service/storage specifications,
never generated from submitted JSON/RDF descriptions, an A adapter, runtime field
conversions, returned HTTP bodies or another condition's new solution.

The evaluator retains a raw native baseline and final state, permissions/revisions,
POST-attempt counters, pending-work information and a transition journal when
available. Derive new identifiers by comparing native key sets. Independently
decode the native item and compare its identifier, requested title and exact
instants. Preserve raw unrelated records, including sentinel metadata; record
extra, removed and changed records. Permission/revision assertions must reflect
independently documented service behavior, not assumptions copied from A/B.
A POST-attempt counter is not itself evidence of a stored mutation.

Output usability is a separate check that the returned canonical `id` identifies
the actual newly stored item. Missing/unusable output must not erase observed
native creation. Missing, malformed, conflicting or still-pending native evidence
is UNKNOWN and cannot pass as success or safe rejection. This is external
assessment, not a semantic precondition calculus inside V4. The current A/B code
is a reference for these invariants, not proof of complete malformed-evidence
handling for a future reader; that boundary needs reviewer validation.

## Family specification (no held-out instances or answers)

Use two independently curated hidden instances per applicable family, with a
separate public smoke/diagnostic set. The proposed total is 32 hidden cases.
This table defines policies only; actual field names, inputs, expected native
records, hashes and applicability for the unseen provider remain null/unset.

| Family | Case meaning | Required external judgment |
| --- | --- | --- |
| T01 | Valid ordinary creation | One correct new item, usable output, unrelated state preserved |
| T02 | Equivalent instants with different UTC offsets | Exact same intended instants, no time shift |
| T03 | Unicode title / heterogeneous wire names | Exact content and consistent native/returned identifier |
| T04 | Missing required canonical input | Ordinary rejection before POST; unchanged native state |
| T05 | Nonpositive interval | Ordinary rejection before POST; unchanged native state |
| T06 | Precision boundary | Exact representation when supported; otherwise reject without truncation or mutation |
| T07 | Provider grid boundary | Validity follows independently documented API limits, identically in all conditions |
| T08 | Provider duration boundary | Supported input succeeds; documented invalid input rejects without mutation |
| T09 | Service permission denial | Truthful HTTP error, no stored change; a rejected POST attempt may be counted |
| T10 | Service error | Truthful invocation error; actual mutation checked separately rather than inferred from status |
| T11 | HTTP success, no storage change | External oracle rejects domain achievement; HTTP success alone cannot pass creation |
| T12 | Wrong stored properties | External oracle rejects correctness and records wrong properties |
| T13 | Extra or unrelated-record mutation | External oracle detects every relevant new/changed/deleted unrelated record |
| T14 | Unsupported task/capability despite similar labels | No execution; explicit local unsupported route in A, exact-ID rejection in B/C |
| T15 | Mutation with missing/unusable returned ID | Native achievement recorded separately; invocation output not accepted as usable |
| T16 | Delayed mutation past subject deadline | Stop/reap, retain late native evidence, never accept timed-out invocation as creation |

Curator applicability decisions precede integrator exposure and all solution
results. If a family cannot be instantiated, explicitly propose an amended exact
denominator/gate for approval before release; do not score N/A as a pass or select
cases after seeing which condition benefits. Every condition receives the same
public facts and faces the same hidden native criteria and fault settings.

A fault-injected service is not expected to become correct through integration.
A diagnostic PASS requires the external evaluator to reject incorrect domain
success and the invocation result to report its actual HTTP/error/output facts.
It does not require a V4 runtime oracle to detect wrong storage. Report separately
normal successful creation, correct rejection, correct external fault detection,
correct timeout handling, unsafe failure, unknown and incomplete observation.

## Gate execution policy (future authorization required)

- Lock all cases and expected verdicts before release, with the same fixed order
  for every submission. Proposed acceptance is all applicable hidden cases passing
  their expected diagnostic policy, usable outputs for normal positives and no
  unauthorized mutations in rejection cases. UNKNOWN/FAIL/NOT_EVALUATED do not pass.
- Fresh isolated service/state, subject process and output path for every case.
  Reset checks cover records, permissions, revision/POST counters, pending work,
  live subjects and trace reuse; cache freshness follows a new process/context.
  Preserve contaminated state and reject before launch, never clear it to pass.
- Existing budgets: five-second HTTP timeout and 60-second outer limit; T16 alone
  uses the disclosed one-second outer limit and 1.5-second service delay equally
  across conditions. Record actual request arrival and pending work at stop.
- Keep service/native observation alive in the evaluator when the subject is
  terminated/reaped. Retain initial bounded recovery observation (1.5 seconds)
  and any separately labeled bounded drain (at most five more seconds). Initial
  uncertainty and timeout remain failures to accept an invocation, even if a
  later snapshot shows the desired state. No cancellation guarantee or retries.
- Preserve raw observations, subject logs/partials, invocation/error, expected
  policy, native assertions, process/timeout/reset reports and per-case times.
  Never replace an unsuccessful integration outcome with an unrecorded rerun.
- Evaluate submitted revisions without feeding hidden verdicts to integrators;
  only receipt acknowledgment until all nine sessions close. A separately
  approved evaluator/infrastructure-error repeat retains both attempts and its
  adjudication; integration mistakes do not qualify. Final evaluation runtime is
  separate from integration wall time; public tests during authoring are included.

## Lock boundary and current blockers

Provider-neutral policy and the visible reference hashes can be checked now.
The unseen provider's eligibility, independent reader, fixtures, concrete hidden
cases/answers, packet hashes and human review cannot be certified from A/B.
The manifest leaves those identities null. A neutral gate outline is **not** a
complete native-state gate lock. No integration session may receive held-out
material until that lock and explicit investigator release authorization exist.
If curator-only preparation is necessary, it needs a separate authorization;
this task grants none and creates no new provider-specific artifacts.
