# Independent semantic review preparation — V3

Status: **pending independent review**. This is a review worksheet prepared by the
same AI collaborator previously exposed to the implementation. Its evidence inventory
and successful automated checks are not independent reviewer conclusions or approval.
Reviewer name: __________. Affiliation: __________. Conflicts/exposure declaration:
__________. Review date: __________. Signature/reference: __________.

## Immutable subject of review

Candidate commit `752da7b8de85dd38c7eee30a101b786ea4743821`; implementation commit
`2d264169a5ec363b78d4bf78b3f40e82d7b59f85`; annotated local tag
`candidate/milestone-4.3-pre-freeze`. [V3 manifest](SCIENTIFIC_FREEZE_MANIFEST_V3.json)
SHA-256 `53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352`;
source-tree digest `bd14f5b4839ac7a49e1bfca01b1adff29fbde6f17497723fac7186cfb6137368`;
[source archive](artifacts/milestone4_3/candidate-source-v3.tar.gz) SHA-256
`b659c852d78ff2bad99f6ec743b5b0bd0a16ad88bbcd20af5e8e6e091089c27d`.

[Audit results](artifacts/milestone4_4/verification-results.json) separately record
M4.4 reproduction. Prior files and manifests are not edited. These new documents
are a review revision outside V3, not a new implementation candidate.

## Scope and how to review

Condition A means API-local engineering, B means JSON with shared semantics, and C
means RDF with shared semantics. Provider A is the calendar fixture and Provider B
the booking fixture. Condition C does not mean access to held-out Provider C.
B/C must have equal supported semantic information; A must meet equal correctness
obligations, but intentionally has no equivalent ontology-mediated discovery knowledge.

Inspect neutral domain requirements, service/native storage semantics and information
correspondence before inspecting outcome labels where feasible. Public A/B diagnostics
are already exposed: a reviewer cannot retrospectively blind themself or their author.
Compare goal truth and safety, not HTTP success or a diagnostic CLI's zero exit code.
Record disagreements, unsupported cases, missing evidence and any proposed correction;
do not silently amend mappings, expected labels, code or frozen artifacts.

Tests below use the exact `module.Class.method` identifiers in
[tests/semantic_action](../tests/semantic_action/). Logs list these identifiers;
parameterized matrices include subtests. A method count is not a provider sample size.
The following rows deliberately leave **all reviewer conclusions blank**.

| ID / criterion | Exact source / inspectable meaning | Exact tests | Retained evidence to inspect | Reviewer conclusion / findings |
| --- | --- | --- | --- | --- |
| S01 condition boundaries | [local_baseline.py](../src/semantic_action/local_baseline.py) `CalendarLocal`, `BookingLocal`; [sequence_bindings.py](../src/semantic_action/sequence_bindings.py) `LocalSequenceBinding`; A reuses neutral transport/model/oracle but no semantic discovery | `test_pre_freeze.ThreeConditionTests.test_no_semantic_discovery_imports_in_local_baseline`; `test_multistep.MultiStepTests.test_local_binding_has_no_semantic_discovery_imports` | [dependency-free local evidence](artifacts/milestone4_3/local-only-final/environment.json); [final wheel environment](artifacts/milestone4_3/wheel-environment.json) | |
| S02 B/C information and validation | [provider_contract.py](../src/semantic_action/provider_contract.py) `load_provider_data/load_provider_graph`; [v2 schema](../src/semantic_action/schemas/contract-v2.schema.json); [sequence profiles](../contracts/sequences/README.md) and `load_shared`; both yield equal typed contracts/guards | `test_registry.RegistryTests.test_v2_schema_and_models`; `test_unsupported_extra_rdf_information_is_not_silently_dropped`; `test_multistep.MultiStepTests.test_sequence_profile_json_rdf_typed_parity`; `test_closed_profile_rejects_missing_unknown_and_ambiguous_fields` | [a.json](../contracts/providers/a.json), [a.ttl](../contracts/providers/a.ttl), [b.json](../contracts/providers/b.json), [b.ttl](../contracts/providers/b.ttl), [sequence a](../contracts/sequences/a.json), [sequence b](../contracts/sequences/b.json); [serialization equivalence](artifacts/milestone4_3/serialization-equivalence.json) | |
| S03 Provider A meanings | [artifact.py](../src/semantic_action/artifact.py) `Scenario/serve`: POST `/events` stores requested ISO event; `/followups/{id}` additionally requires existing predecessor and temporal order; GET snapshots and revisions | `test_pipeline.PipelineTests.test_valid_action`; `test_multistep.MultiStepTests.test_service_enforces_dependency_without_sequence_guard`; matrix M01/M09 | [M01-a-A](artifacts/milestone4_3/pilot-final/M01-a-A/evaluation.json), [M09-a-C](artifacts/milestone4_3/pilot-final/M09-a-C/evaluation.json), [local description](../contracts/api_local/a-followup.json) | |
| S04 Provider B meanings | [provider_b.py](../src/semantic_action/provider_b.py) `BookingScenario/serve_bookings`: integer milliseconds, local names/fields, UTC quarter-hour grid and <=2 h duration; `/booking-after/{id}` stores `previous_booking` | `test_registry.RegistryTests.test_duration_and_grid_constraints_reject_only_incompatible_provider`; `test_input_precision_cannot_be_silently_lost`; `test_provider_b_owns_its_constraint_enforcement`; direct dependency test | [M01-b-B](artifacts/milestone4_3/pilot-final/M01-b-B/evaluation.json); [booking local description](../contracts/api_local/b-followup.json); D10/D19/D20 matrix in final suite logs | |
| S05 TRUE/FALSE/UNKNOWN | [pipeline.py](../src/semantic_action/pipeline.py) `evaluate_preconditions/Executor.assess/run`; [oracle.py](../src/semantic_action/oracle.py) `current`; `LocalExecutor.run`: absent, stale, future or malformed evidence cannot become TRUE | `test_registry.RegistryTests.test_false_unknown_and_stale_preconditions_block`; `test_execution_rechecks_permission_after_resolution`; `test_parity.ParityTests.test_missing_malformed_future_and_unavailable_evidence`; `test_multistep.MultiStepTests.test_unknown_dependency_and_stale_evidence_block` | [M02-b-C](artifacts/milestone4_3/pilot-final/M02-b-C/evaluation.json), [M04-a-A](artifacts/milestone4_3/pilot-final/M04-a-A/evaluation.json), [M10-b-B](artifacts/milestone4_3/pilot-final/M10-b-B/evaluation.json) | |
| S06 two/three-action dependencies | [sequence.py](../src/semantic_action/sequence.py) `SequencePlan/dependency/SequenceExecutor`; every later action refers to immediately preceding actual event, observes fresh state, and must start after its end; no skipping | `test_multistep.MultiStepTests.test_all_scenarios_three_conditions_visible_providers`; `test_finite_profile_rejects_unsupported_plan_before_execution`; `test_required_action_never_skipped_even_if_goal_looks_true` | M01/M09 `sequence.json`, `step-*/action.json`, `native-transitions.json` under [final pilot](artifacts/milestone4_3/pilot-final/pilot-results.json) | |
| S07 effect mismatch, failures and no-op | `LocalSequenceBinding.compatible`, `SharedSequenceBinding.compatible`, [registry.py](../src/semantic_action/registry.py) `resolve/execute`; sequence stops at failed action, never compensates/retries | `test_registry.RegistryTests.test_similar_names_do_not_override_non_equivalent_effects`; main multistep matrix M03/M05/M07/M08; required-action test | [M03-a-B](artifacts/milestone4_3/pilot-final/M03-a-B/evaluation.json), [M05-b-C](artifacts/milestone4_3/pilot-final/M05-b-C/evaluation.json), [M07-b-A](artifacts/milestone4_3/pilot-final/M07-b-A/evaluation.json), [M08-a-C](artifacts/milestone4_3/pilot-final/M08-a-C/evaluation.json) | |
| S08 native truth and full preservation | [native_verifier.py](../src/semantic_action/native_verifier.py) `capture/adjudicate`; [sequence_native.py](../src/semantic_action/sequence_native.py) `verify_chain`; deep-copied storage, independently decoded fields/IDs, required transitions and raw existing-record contents | `test_pre_freeze.NativeVerifierTests.test_snapshot_deep_copy_and_native_extra_change_detection`; `test_multistep.SequenceNativeTests.test_wrong_relation_and_raw_preservation_fail`; `test_missing_required_transition_never_verifies`; `test_oracle_expectation_not_supplied_by_runtime_trace` | [M06-a-B](artifacts/milestone4_3/pilot-final/M06-a-B/evaluation.json), [M06-b-C](artifacts/milestone4_3/pilot-final/M06-b-C/evaluation.json); raw snapshots and curator expectations in each run | |
| S09 mapping independence and trusted decoder boundary | `NativeInterpretation`, `ChainInterpretation`; native reader does not import subject mapping/pipeline; provenance strings do not authenticate approval | `test_pre_freeze.NativeVerifierTests.test_native_observer_has_no_subject_mapping_dependencies`; `test_multistep.SequenceNativeTests.test_curator_owned_relation_extension_without_core_truth_change`; `test_pre_freeze.ThreeConditionTests.test_all_twenty_diagnostics_on_visible_providers` D15 | [D15 decoy mapping](artifacts/milestone4_1/examples-final/D15-b-B/evaluation.json), final 87-test logs containing curator-owned extension test | |
| S10 permissions, revisions and mutation counters | `oracle.verify` checks fresh consistent revision increase; `verify_chain` checks native TRUE permission before each POST, exactly one attempt per required transition and continuity; permission is not a whole-world final-state invariant | `test_registry.RegistryTests.test_execution_rechecks_permission_after_resolution`; `test_pre_freeze.ThreeConditionTests.test_unsafe_mutation_attempt_is_not_hidden_by_goal_outcome`; multistep M02/M04; native wrong-relation/raw tests | M02/M04 `native-transitions.json`; M01/M09 full `before/after` evidence | |
| S11 reset isolation | [supervision.py](../src/semantic_action/supervision.py) `assert_reset`; [multistep_evaluation.py](../src/semantic_action/multistep_evaluation.py) `initial_records/run_pilot`; raw records, permissions, counters and pending requests; fresh process/path/no persistent resolution cache | `test_multistep.OperationalTests.test_each_reset_axis_detects_contamination`; `test_contaminated_reset_rejects_before_subject_launch`; `test_repetitions_have_equivalent_clean_state_and_distinct_processes` | [negative reset](artifacts/milestone4_3/pilot-final/contaminated-reset-a-A/reset.json), [rejected attempt](artifacts/milestone4_3/pilot-final/contaminated-reset-a-A/evaluation.json), `repetition-2-*/reset.json` and `supervision.json`; [reset report](RESET_ISOLATION_REPORT.md) | |
| S12 deadlines, late mutation and uncertainty | `supervise/settle_and_capture`; [transport.py](../src/semantic_action/transport.py) 5 s HTTP timeout; process stop does not cancel server work; final success requires completed supervision plus both verifiers and settled evidence | `test_multistep.OperationalTests.test_timeout_kills_stalled_process_and_preserves_costs`; `test_inflight_timeout_observes_late_state_without_claiming_success`; `test_http_timeout_is_distinct_from_outer_timeout`; `test_unsettled_service_remains_uncertain` | [in-flight B](artifacts/milestone4_3/pilot-final/inflight-timeout-b-B/evaluation.json), [HTTP timeout](artifacts/milestone4_3/pilot-final/http-timeout-a-A/evaluation.json), [stall](artifacts/milestone4_3/pilot-final/isolated-stall/supervision.json) | |
| S13 final candidate provenance | Final manifest `validation.final_candidate_suite_ids`, `pilot_results_path`, source/archive hashes; [wheel comparison](artifacts/milestone4_3/wheel-source-comparison.json) | Final 87-test source/wheel/restored logs; curator-owned extension test distinguishes 87 from 86 | [original validation](artifacts/milestone4_3/validation-results.json), [final pilot](artifacts/milestone4_3/pilot-final/pilot-results.json), [M4.4 provenance assessment](artifacts/milestone4_4/provenance-assessment.json), new audit logs/pilot | |

### Equivalence limits a reviewer must adjudicate

Typed B/C equality includes meanings, inputs, constraints, effects, wire transformations,
observations, evidence lifetimes and guard predicates. It is not arbitrary RDF/JSON
syntax equivalence. JSON duplicates reject; identical RDF triples collapse as graph
semantics. Array/member/prefix order and internal nodes may be nonsemantic. Ambiguous
cardinality/unknown assertions must not silently enable an action. The sequence RDF
loader is closed and eventually uses the same typed base contract; A encodes its wire
knowledge locally instead of importing shared discovery. B/C do an extra resolution
probe; identical obligations do not imply identical request counts or engineering cost.

The multi-step matrix asserts full normalized summaries and B/C profile model equality;
old v1 differential tests compare more trace fields/reasons. Neither proves correctness
for every possible malformed input. D02 overlaps D01; D04 overlaps D11; M01/M09 extend
one event-creation capability. These are controlled apparatus families, not independent
capabilities or representative provider sampling. Direct service dependency enforcement
is an important additional check, not proof that the fixtures model all real services.

### Common-mode and independence risks to record

The same previously exposed AI author wrote fixtures, local/shared contracts, mappings,
tasks and observer code. Agreement can share a mistake. The native reader is independent
of subject mappings/declared effects, but shares Goal/oracle/time parsing/clock assumptions
and trusted service storage/counters with the apparatus. It observes only captured local
state; external asynchronous side effects and newly created-event metadata outside the
goal model are not generally certified. Raw preservation applies to pre-existing records.
Reset cache/process assertions partly follow runner construction, not memory attestation.

`NativeInterpretation`/`ChainInterpretation` callbacks are trusted evaluator code, not
sandboxed or automatically authenticated by their source-reference strings. Independent
curator review/custody must prevent reuse of subject mappings as the sole truth source.
Public A/B task labels cannot become sealed, independently authored answers by renaming
them. Generating RDF variants from JSON also introduces writer/reader common modes;
review the static Turtle files against a neutral information sheet.

Retained artifacts and hashes establish consistency and byte identity, not cryptographic
proof of which source a historical process ran or independent human authorship. New M4.4
reproduction strengthens executable consistency; it does not retroactively establish
blinding. Investigator decisions and reviewer findings must retain these distinctions.

## Reviewer disposition (to be completed independently)

Semantic conclusions: __________. Native-oracle conclusions: __________.
Unresolved findings / severity / evidence references: __________.
Recommended scope and limitations: __________. Independent review reference: __________.
Reviewer identity: __________. Date: __________. Signature: __________.

No blank in this worksheet is completed by a passing test or by this preparation task.
