# Codex Task — Milestone 4.3: Bounded Multi-Step Pilot and Operational Readiness

## Context

Continue the ESWC 2027 research implementation in `SemanicIAAgentique`.

The Milestone 4.1 candidate is:

- Commit: `2829c6dc41344431e83bde7c3addf30d1241befc`
- Tag: `candidate/milestone-4.1-pre-freeze`
- Manifest SHA-256: `7f8e8d1d4f0f07e8c5ef999c36aaf987d17bf58d757df4a733f736ceaa78bcc2`

Milestone 4.2 produced:

- `docs/SCIENTIFIC_FREEZE_APPROVAL_PACKAGE.md`
- `docs/SCIENTIFIC_FREEZE_DECISION_RECORD.json`

Scientific approval remains pending. Provider C remains sealed.

## Objective

Implement and validate a minimal multi-step pilot using only visible Providers A and B, together with operational timeout and reset supervision.

The goal is to close the documented multi-step coverage gap before proposing a new scientific freeze candidate.

**Do not access Provider C. Do not implement an LLM planner. Do not conduct the confirmatory experiment.**

## 1. Preserve the previous candidate

Before modifying code:

1. Verify the Milestone 4.1 candidate against its manifest.
2. Preserve the Milestone 4.2 approval package and decision record.
3. Create a dedicated Milestone 4.3 working branch.
4. Record the base commit, branch, dependency versions and initial test results.
5. Keep historical manifests, archives, logs and approval records unchanged.

If generic implementation changes are required, they must produce a **new candidate identity**. Never silently reinterpret the previous freeze candidate.

## 2. Define a bounded multi-step profile

Implement a small, explicit action-sequence execution profile.

Requirements:

- Two or three sequential actions per task.
- Formal goals specified before execution.
- State observation after each action.
- Fresh precondition assessment before each action.
- Explicit TRUE/FALSE/UNKNOWN semantics.
- No unchecked execution when critical evidence is unknown.
- No assumption that HTTP success implies goal achievement.
- Final independent verification of the entire goal.
- Preservation and noninterference checks across the sequence.
- Structured traces for every action and state transition.

Prefer reusing existing validated action execution rather than introducing a second mutation pathway.

Do not claim general-purpose planning or arbitrary workflow support.

## 3. Design multi-step tasks on visible providers

Create a small set of genuinely multi-step scenarios using Providers A and B.

Include at least:

1. **Sequential dependency:** the second operation requires a state change produced by the first.
2. **State-updated applicability:** the second operation is assessed using fresh state, not assumptions from the initial state.
3. **Intermediate failure:** the first operation succeeds but the second fails; preserve partial state and report incomplete goal achievement.
4. **Unknown evidence:** the next action is blocked when a critical precondition cannot be established.
5. **Unsafe substitution:** an operation with a similar name but non-equivalent effects must not be selected.
6. **Forbidden side effect:** the sequence must fail verification if unrelated state changes.
7. **No-op success response:** an HTTP success without the required state transition must not count as progress.
8. **Recovery boundary:** show what happens after a recoverable failure without introducing task-specific repair or hidden retries.

Each scenario must have an independently specified formal goal, initial-state fixture, permitted transitions, forbidden effects, and expected verdict.

**Important:** If Providers A and B do not support enough genuinely distinct operations or state transitions to realize these scenarios, report the gap explicitly. You may add controlled visible-provider fixture operations and corresponding local/JSON/RDF contracts, but document their provenance and ensure equal correctness obligations across Conditions A, B and C.

Do not simulate multi-step coverage by executing the same unrelated event-creation operation twice and calling it a dependency.

## 4. Keep the three experimental conditions comparable

Run every supported multi-step scenario under:

- Condition A: API-local contracts and validators.
- Condition B: JSON with shared semantic capability knowledge.
- Condition C: RDF with equivalent shared semantic knowledge.

All conditions must receive identical formal goals, initial states, observations, task budgets and independent correctness criteria.

Condition A must not use shared semantic discovery. Conditions B and C must retain equivalent semantic content and validation.

Any unsupported task must be recorded as unsupported, not silently rewritten.

## 5. Define the sequence executor boundary

Implement only the minimal orchestration needed.

The executor must:

- Execute a declared finite sequence of operations.
- Re-evaluate preconditions from fresh observations.
- Preserve action-level traces.
- Stop on critical failure, unknown applicability or missing mandatory evidence.
- Report partial state explicitly.
- Never invent compensating actions.
- Never treat a failed action as successfully completed.
- Never skip a required action merely because the final goal appears true.
- Avoid task-specific provider substitutions.

Separate sequence execution from goal interpretation and autonomous plan generation.

The same independent native-state evaluator must verify final correctness.

If any current API or oracle limitation requires a generic change, document it and include it in the new candidate.

## 6. Implement operational timeout supervision

The Milestone 4.2 package proposed:

- 5-second HTTP timeout.
- 60-second outer execution budget.
- Zero automatic retries.
- Zero planner/repair iterations.

Implement or demonstrate a supervisor that:

1. Enforces the outer deadline.
2. Stops the subject process on timeout.
3. Captures or recovers post-timeout native state.
4. Records partial execution and uncertainty.
5. Preserves available traces and cost records.
6. Distinguishes timeout from transport failure.
7. Does not count timed-out runs as successful.
8. Does not silently retry.

Test with deliberately stalled execution.

Do not claim reliable cancellation of remote side effects unless demonstrated. If the process can be stopped while an HTTP mutation is in flight, classify the resulting state as uncertain until independently observed.

## 7. Verify reset isolation

Demonstrate that each condition and repetition starts from an equivalent fixture state.

Check:

- Native records.
- Permissions.
- Revision counters.
- Mutation counters.
- Process state.
- Cached capability resolutions.
- Persistent trace locations.

Archive reset evidence before execution.

Include a negative test where contaminated initial state is detected and the run is rejected.

## 8. Extend independent native-state verification

For multi-step tasks, verify:

- Required intermediate state transitions.
- Final goal achievement.
- Preserved pre-existing records.
- No forbidden mutations.
- Partial state after failure.
- Agreement or disagreement between runtime and native-state results.

Do not derive expected effects from subject manuals.

Do not allow the sequence executor to provide the oracle with its own expected answer.

## 9. Tests and evidence

Add tests covering all new orchestration, reset, supervision and multi-step behavior.

Run:

1. Existing Milestone 4.1 regression tests.
2. New multi-step tests.
3. A/B/C differential tests.
4. Timeout and contamination tests.
5. Source installation tests.
6. Installed-wheel tests.
7. Restored-archive tests.

Report test counts and failures honestly.

Do not treat multiple executions on Providers A/B as independent held-out provider observations.

## 10. Research-scope safeguards

Maintain these distinctions:

- Multi-step execution is not autonomous planning.
- Replanning is not implemented merely because an action is retried.
- State-updated applicability is not equivalent to general reasoning.
- B/C parity does not prove RDF superiority.
- Correctness does not prove lower engineering cost.
- A/B are exposed development providers, not independent held-out validation.
- The primary research question remains reusable semantic capability knowledge and integration effort.
- RQ2 remains a separate secondary experiment, not a prerequisite for this milestone.

Unsupported behavior must remain visible in results.

## 11. Required deliverables

Create:

- `docs/MILESTONE_4_3.md`
- `docs/MULTISTEP_PROFILE.md`
- `docs/MULTISTEP_PILOT_TASKS.md`
- `docs/OPERATIONAL_SUPERVISION_PROTOCOL.md`
- `docs/RESET_ISOLATION_REPORT.md`
- `docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json`

Also provide:

- New implementation and tests.
- Machine-readable pilot results.
- Source and wheel test logs.
- Restored-archive verification.
- Exact source commit and digest.
- A clear list of unresolved limitations.

Do not overwrite V2 or historical approval records.

## 12. Definition of done

Milestone 4.3 is complete when:

- At least one genuine sequential state dependency is demonstrated.
- Fresh state determines subsequent applicability.
- Partial failures are represented correctly.
- Unknown evidence blocks unsafe continuation.
- Final correctness is independently verified.
- A/B/C correctness obligations remain equivalent.
- Outer timeout supervision is demonstrated.
- Reset contamination is detected.
- All relevant regression tests pass.
- A new reproducible candidate is generated.
- Provider C remains sealed.
- Scientific approval remains pending.

If genuine multi-step semantics cannot be implemented within the bounded profile, do not fabricate coverage. Report the limitation and propose a controlled scope decision.

## 13. Final report

At completion, provide:

1. Summary of implementation.
2. Actual multi-step scenarios supported.
3. Condition parity results.
4. Test totals.
5. Timeout and reset evidence.
6. New commit/tag/digests.
7. Any remaining methodological blockers.
8. Whether the new candidate is technically ready for investigator review.

**Implement and test the milestone. Do not stop at a plan. Do not approve the scientific freeze or unseal Provider C.**