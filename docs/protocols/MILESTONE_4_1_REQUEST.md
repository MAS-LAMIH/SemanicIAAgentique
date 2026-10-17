# Codex Task — Milestone 4.1: Close the Pre-Freeze Gates

You are continuing the ESWC 2027 research implementation in the `SemanicIAAgentique` repository.

Milestones 1–3 are implemented. Milestone 4 produced an auditable scientific freeze candidate, but **scientific approval remains pending**.

Your task is to resolve the remaining pre-freeze blockers, produce a new reproducible candidate, and prepare it for human approval.

**Do not unseal, inspect, implement, or integrate Provider C. Do not declare the scientific freeze approved.**

## 1. Read the governing documents

Before modifying code, inspect:

- `docs/MILESTONE_4_FREEZE_AUDIT.md`
- `docs/SCIENTIFIC_FREEZE_MANIFEST.json`
- `docs/HELD_OUT_EVALUATION_PROTOCOL.md`
- `docs/COST_MEASUREMENT_PROTOCOL.md`
- `docs/EXPERIMENTAL_PARITY_CHECKLIST.md`
- `docs/PROVIDER_C_FREEZE_PROCEDURE.md`
- `docs/MILESTONE_3.md`
- `docs/CONTRACT_SEMANTICS.md`

If available, also read `ESWC_2027_Frozen_Research_and_Experimental_Protocol.pdf`.

Do not change the frozen research questions or experimental conditions.

## 2. Preserve the existing freeze candidate

The Milestone 4 archive and manifest are historical evidence.

- Verify their integrity before making changes.
- Do not overwrite or rewrite them.
- Record the current Git status and commit.
- Create a dedicated working branch for Milestone 4.1.
- Make all changes traceable.
- Generate a new candidate manifest after implementation.

Do not claim the existing HEAD commit contains all previously tested changes if some remain uncommitted.

## 3. Implement the missing API-local baseline — Experimental Condition A

The experiment compares three infrastructure conditions:

- **Condition A:** API-local contracts, mappings, and validators without shared semantic infrastructure.
- **Condition B:** JSON contracts with shared semantic identifiers, reusable mappings, and validators.
- **Condition C:** RDF contracts with equivalent shared semantic knowledge and validation.

Implement Condition A as a genuine experimental baseline.

Requirements:

1. Support the existing controlled Providers A and B.
2. Use provider-local operation descriptions and mappings.
3. Do not use the shared semantic registry or shared ontology-mediated discovery.
4. Preserve equivalent input validation, state preconditions, goal constraints, observation requirements, and correctness checks.
5. Preserve TRUE/FALSE/UNKNOWN handling.
6. Reject unsafe or unsupported operations.
7. Use the same independent goal oracle as Conditions B and C.
8. Do not artificially weaken Condition A to create a semantic-reuse advantage.
9. Do not copy shared semantic mappings into Condition A while pretending they were independently authored.
10. Record the actual engineering work needed to implement and maintain the provider-local baseline.

Condition A may reuse neutral transport, state observation, and oracle infrastructure where the approved cost-allocation policy permits it. Document all reuse explicitly.

**Important:** Provider A and Condition A are different concepts.

## 4. Implement independent native-state verification

The existing oracle verifies observed state but relies partly on provider-supplied output mappings.

Introduce an evaluation-only native-state verification mechanism.

Requirements:

1. Read the provider's actual controlled fixture state independently of the semantic contract mappings.
2. Use independently specified provider-native field interpretations.
3. Compare native state against a task-specific oracle expectation.
4. Detect incorrect output mappings, missing changes, unexpected changes, and forbidden side effects.
5. Preserve raw evidence alongside canonical observations.
6. Do not modify the goal truth definition to accommodate a provider.
7. Keep this verifier separate from the execution pipeline and provider manuals.
8. Apply the same verification obligations to all three experimental conditions.

Add a negative test in which the semantic mapping is wrong but the native-state oracle correctly detects the discrepancy.

Do not use the manual's declared effects as evidence of actual success.

## 5. Implement the prospective cost collector

Extend cost measurement without reinterpreting existing historical logs.

Record separately:

- Human active person-minutes.
- AI-assisted human supervision time.
- Automated execution/runtime.
- Tool/model waiting time.
- Total elapsed wall-clock time.
- Shared setup effort.
- Provider onboarding effort.
- Testing and debugging.
- Failed attempts and rework.
- Maintenance when observed.

Requirements:

1. Implement an append-only structured event ledger.
2. Support contributor IDs, provider IDs, experimental condition IDs, task IDs, activity categories, timestamps, and artifact references.
3. Prevent obvious double counting of overlapping human-active intervals.
4. Record AI/tool runtime separately from human labor.
5. Keep missing or unmeasured values null.
6. Support corrections through linked records rather than destructive edits.
7. Document allocation rules for shared infrastructure costs.
8. Test the collector using controlled A/B integration activities.

Do not fabricate historical person-minutes or treat previous AI wall-clock measurements as human effort.

## 6. Prepare prospective evaluation tasks

Create a provider-neutral evaluation specification before Provider C is revealed.

Include:

- Valid semantic matches.
- Equivalent capabilities with different names or field formats.
- Misleadingly similar operations with non-equivalent effects.
- False critical preconditions.
- Unknown or stale evidence.
- Unsupported input transformations.
- Unsupported state transitions.
- API errors.
- HTTP success without actual goal achievement.
- Incorrect output mappings.
- Forbidden side effects.

For each task family, define:

- Formal goal.
- Initial-state requirements.
- Mandatory constraints.
- Independent oracle expectations.
- Required evidence.
- Correct acceptance or rejection behavior.
- Failure classification.

Do not generate Provider C-specific tasks or answers.

Propose a feasible task count, repetition policy, ordering strategy, random seeds, timeouts, and stopping rules. Clearly mark these as proposals requiring human approval.

Avoid treating repeated executions against the same provider as independent provider samples.

## 7. Complete experimental parity validation

Verify that Conditions A, B, and C have equivalent correctness obligations.

For Conditions B and C, verify semantic information parity:

- Capabilities.
- Inputs and types.
- Preconditions.
- Effects.
- Transformations.
- Constraints.
- Evidence requirements.
- Failure handling.

For Condition A, verify equivalent functional and correctness requirements without granting it shared semantic infrastructure.

Add differential tests across all three conditions using identical controlled fixtures and independently specified goals.

Preserve negative cases and unknown-state behavior.

Any difference in functionality must be documented and resolved before proposing scientific approval.

## 8. Reproducibility and version control

After implementation:

1. Run all existing tests.
2. Run the new baseline, oracle, and cost-collector tests.
3. Run installed-wheel tests.
4. Verify fresh-environment restoration where feasible.
5. Record exact dependency versions and commands.
6. Produce a new source manifest with file hashes.
7. Record the complete tested source identity.
8. Prefer a clean Git commit and tag, but do not rewrite repository history or push without authorization.
9. Keep Milestone 4 evidence unchanged.

If a clean commit is not possible, preserve an auditable source archive and explain why.

Do not label the candidate as approved.

## 9. Required deliverables

Create or update:

- `docs/MILESTONE_4_1.md`
- `docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json`
- `docs/EXPERIMENTAL_PARITY_CHECKLIST.md`
- `docs/HELD_OUT_EVALUATION_PROTOCOL.md`
- `docs/COST_MEASUREMENT_PROTOCOL.md`
- `docs/EVALUATION_TASK_SPECIFICATION.md`
- `docs/SCIENTIFIC_FREEZE_APPROVAL_CHECKLIST.md`

Include all new source files, tests, and reproducibility artifacts.

## 10. Definition of done

Milestone 4.1 is complete when:

- Condition A exists and is tested against Providers A and B.
- Conditions A, B, and C satisfy equivalent correctness obligations.
- JSON/RDF semantic parity remains intact.
- Native-state verification is independent of provider contract mappings.
- Incorrect mappings are detectable.
- A prospective cost collector is operational.
- Evaluation task families and measurement procedures are documented.
- A new reproducible source candidate is generated.
- All relevant tests pass.
- Provider C remains sealed.
- The scientific freeze remains explicitly pending human approval.

## 11. Final report

At completion, report:

1. Files created and modified.
2. Architecture and experimental decisions.
3. Test counts and outcomes.
4. New candidate commit and digest.
5. Actual recorded engineering effort.
6. Remaining methodological risks.
7. Any decisions requiring investigator approval.
8. Whether the candidate is technically ready for scientific freeze review.

**Do not stop after producing a plan. Implement the missing components, execute the tests, and prepare the candidate for approval.**

**Do not implement Provider C, an LLM planner, or the full confirmatory benchmark in this milestone.**