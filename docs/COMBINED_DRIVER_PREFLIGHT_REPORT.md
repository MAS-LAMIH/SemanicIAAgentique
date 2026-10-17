# Combined-driver operational preflight report

This report concerns visible A/B diagnostics only. The machine-readable results,
commands and per-attempt hashes are in `docs/artifacts/milestone4_5/`.
Scientific approval, human independence and held-out generalization are not
established by these checks.

## Measured result: PASS (engineering preflight only)

- Full protected rehearsal: 180 planned, 180 executed, 180 expected diagnostic
  outcomes; 120 single-action and 60 multi-step. Zero missing/aborted attempts or
  reset rejections in the clean base matrix. Expected negative/partial task
  outcomes are retained, not labeled missing coverage. The 60 chain outcomes are
  12 COMPLETE, 12 REJECTED, 12 BLOCKED and 24 expected INCOMPLETE. Thus zero
  uncollected attempts does not mean every diagnostic chain achieved its goal.
- Frozen regressions: source 87/87 in 208.261 s; installed wheel 87/87 in
  206.589 s; restored archive 87/87 in 207.228 s. All exit 0, no errors or skips.
- Focused suite: 5 tests expanding to 63 retained attempts, passed twice
  (62.275 s and 65.005 s). Across both runs: 14 reset rejections before launch,
  18 deadline outcomes, six initially uncertain observations, zero timeout or
  uncertainty accepted as verified success. Additional existing-path and
  unsupported-provider rejection controls launched no subject.
- Separate references: 120/120 frozen single-action cases passed. All 180
  protected summaries match their frozen reference or retained V3 pilot summary;
  all three conditions agree per task/provider. All 180 PIDs are distinct.
- Inventory: 427 retained evaluation records: 180 rehearsal, 120 reference,
  126 focused and one initial development positive. None lacks its evaluation
  output. Lifecycle evidence completeness checks passed.
- All 3,216 pre-existing tracked files unchanged; all eight scientific approval
  gates remain pending with null signatures. Candidate identity checks passed.

Exact commands, times, exits and comparison arrays are in
[verification-results.json](artifacts/milestone4_5/verification-results.json);
[attempt-inventory.json](artifacts/milestone4_5/attempt-inventory.json) identifies
every attempt and its files. The new
[preflight-manifest.json](artifacts/milestone4_5/preflight-manifest.json) indexes
all added code, reports and evidence; it is not a replacement V3 manifest.

## Evidence and safeguards

`initial-inspection.md` precedes the evaluator additions. `start-state.json`
binds the review base and all 3,216 old tracked file hashes. `candidate-verify.log`
and `candidate-history.log` retain successful frozen verifier output. The exact
V3 identity and archive/wheel hashes are listed in `MILESTONE_4_5_PREFLIGHT.md`
and checked in `environments.json`.

The protected rehearsal uses all D01–D20 and M01–M10, providers a/b, Conditions
A/B/C, one repetition, fresh subprocesses and directories, 60-second outer and
5-second HTTP deadlines. The separate 120 original single-action reference runs
are not counted as protected rehearsal attempts. Focused probes use explicit
1-second outer/1.5-second service-delay controls and 0.75-second outer/3-second
service-delay controls. Both focused runs are retained, including their repeated
attempts; their test counts are not provider sample sizes.

Reset probes cover calls, revision, permission, unexpected records, pending
requests and trace contamination on single actions, plus frozen multi-step call
contamination. They reject before subject launch and preserve contamination.
Two fresh positive executions have distinct PIDs and clean resets. Reusing an
existing path raises without overwriting it. The fresh-registry/cache assertion
comes from constructing a new Registry in a fresh child, not memory forensics.

Late single-action native success and complete native chains are observed after
subject termination, with runtime and combined success false. Unsettled single
actions retain an initial uncertain observation and a later bounded terminal
snapshot; the original verdict is not upgraded. Subject processes are terminated
and reaped; stopping a process cannot guarantee cancellation of remote effects.
The frozen multi-step trace may retain status RUNNING after a timeout: the
supervisor TIMEOUT and final verified=false are the outcome, not that partial
trace label. No retry, repair or compensation is attempted.

Native/runtime disagreements are expected in D15 (decoy field: runtime true,
native false) and D17/D18 (stale/missing runtime observation: runtime false,
native state achieved). They remain unverified. The inventory preserves exact
verdicts, native journals, raw before/after state and process outputs. Expected
negative/partial chains remain diagnostic passes when matching frozen controls.

## Failures and limitations

No frozen engine or truth-rule change was needed. No scientific stop condition
was observed. An administrative note append failed with `ValueError: Unknown
activity or scope` because `implementation` is not a frozen activity. It appended
nothing; the retained `ledger-note-rework.json` documents use of the existing
`documentation` label on retry. No historical ledger was touched. Three initial dependency-check commands also
exited 2 because uv selected a read-only home cache. Their original logs are
retained as `dependencies-{source,wheel,restored}.log`. Explicitly setting
`UV_CACHE_DIR=/workspace/.cache/uv` allowed all three retry checks to pass, exit 0;
no dependency or frozen file was changed. All measured
command failures, expected diagnostic failures and timeouts remain in the logs
and inventory; none were removed to improve coverage.

Only controlled in-process fixture services were tested. Native truth shares
fixture/task authorship with the subject apparatus; byte separation is not proof
of independent human curation. Independent semantic/native-state review is still
pending. The 1.5-second recovery observation is bounded, not a universal remote
settlement guarantee. A further 5-second drain is only used to retain evidence in
the deliberate single-action uncertainty probe; it neither retries nor upgrades
truth. Exact installed environments were reused and reverified, not represented
as new installations or new human onboarding work. Cost measurements are limited
to actual automation runtimes; missing human/supervision/wait values remain null.

P1/P2/P3 policy, locked task instances/order, statistical analysis, role assignment,
independent reviews, investigator signoff and future unsealing authorization all
require investigator decisions. Two independent provider units cannot establish
population-level superiority. These diagnostic tasks are public and are not
future held-out answers.

No push, merge, new V3 candidate, scientific approval or unsealing occurred.
