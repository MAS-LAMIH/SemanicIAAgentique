# Phase 1 inspection — recorded before adding driver code

Boundary decision: an addition-only evaluator composition is available. No frozen
engine/meaning/truth/collector change is required. This is a preparation finding,
not scientific approval; Provider C remains sealed.

## Existing entry points

- `src/semantic_action/evaluation.py:run_case/main` handles D01–D20. It owns the
  fixture, public diagnostic interventions, LocalExecutor or Registry execution,
  and `capture/adjudicate`. Its subject executes in the same process as its service;
  it does not call `assert_reset`, `supervise` or bounded post-stop capture.
- `src/semantic_action/multistep_evaluation.py:run_pilot/main` handles M01–M10.
  It keeps its fixture server in the parent, checks `assert_reset`, invokes a fresh
  `semantic_action.sequence` child through `supervise`, calls `settle_and_capture`,
  and adjudicates native journals with `sequence_native.verify_chain`.
- `src/semantic_action/supervision.py:supervise` implements deadline/TERM/KILL/reap;
  `assert_reset` checks raw initial state and supplied lifecycle/cache conditions;
  `settle_and_capture` bounds observation. These frozen functions will be reused.
- `native_verifier.capture/adjudicate` reads actual fixture storage with a Goal;
  runtime mappings and declared effects do not determine native answers. Whole-
  chain truth is `sequence_native.verify_chain`; it will not be reimplemented.
- `artifact.serve` / `provider_b.serve_bookings` provide default-inert
  `transition_observer` hooks and pending-request counters. The callback runs in
  the evaluator-owned server, enabling journaling and controlled delay without
  changing fixture implementation. No held-out service is required or accessed.

## Intended additions and risks

Add `preflight/` only: a worker invoking existing LocalExecutor/Registry for one
single action, a parent-owned fixture driver using frozen reset/supervisor/native
interfaces, common inventory/rehearsal CLI, and focused evaluator tests. Reuse
`run_pilot` directly for M tasks. Add separate M4.5 reports/evidence. Do not modify
any existing source, contract, test, manifest, archive, ledger or approval document.

Single-action public interventions must match `evaluation.run_case`: same service
modes, permission evidence deletion, decoy observation field and local/JSON/RDF
manual variants. Such interventions are fixture controls, not new semantic features
or expected answers sent to the subject. The worker receives formal inputs and
public wire-fault configuration; independent expectations remain in the parent.
The same intervention and budget apply to all conditions. The only mutation calls
remain existing validated executors; no raw POST is introduced by orchestration.

Killing the entire old `run_case` process would kill its service/evidence path and
would not establish post-timeout native state. Therefore only the subject operation
is moved into a child; service/native observation remain parent-owned. Timeout is
a final evaluation veto even if late native achievement is observed. Pending state
is uncertain, never evidence of safe rejection. A separate bounded drain may retain
a later fixture observation, without reclassifying the original timeout/uncertainty
as success or retrying a request. If safe capture/drain cannot be established, stop.

Reset must precede launch, preserve contaminated state instead of clearing it,
reserve new paths, and record counters/permissions/records/pending requests. Fresh
PIDs/no persistent Registry caching are architectural facts, not memory attestation.
Malformed/partial subject traces after termination must be retained, not replaced.

Critical stop rules: frozen changes needed, native/semantic contradiction, unsafe
undetected reset, timeout accepted as verified, condition-specific protection or
any need for sealed material. Preserve failures and report rather than patch V3.

## Validation plan

Focused controls first; only on pass run all 180 public cases (30 × 2 × 3) at default
60 s with 5 s frozen HTTP timeout, zero retries/repair. Label shorter fault budgets
separately. Compare single-action normalized summaries with frozen `run_case`
reference executions (separate reference phase), and M summaries with retained final
V3 pilot and frozen expectations. Inventory references separately, not as the 180
protected rehearsal. Run original 87 tests in exact source, wheel and restored
installations; new tests are separate. Verify all 3,216 pre-existing files unchanged
and all decision gates pending. No push, merge, tag or implementation candidate.
