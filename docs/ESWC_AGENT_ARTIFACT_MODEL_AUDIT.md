# ESWC agent–artifact model audit

**Finding:** V3 has an executable, finite goal/contract/applicability/verification
foundation, but no agent that autonomously chooses between its eligible operations.
V4 is intentionally a narrower capability invocation system. The original tutorial
has an LLM tool-choice loop, but that loop is not connected to V3's formal semantics.
None of these facts erases the valid execution/parity results already retained.
Audit source revision: `8e5f78be8708aec1221e874016dba0b26650202b`.
This is source/test/evidence inspection; no new agent or experiment was executed.

## Original sources and attribution

**P — original report:** Alaa Daoud, *Semantic Web Environments for MAS: Enabling
agents to use Web of Things environments via semantic web*, August 2018 master's
internship report, arXiv v1 (2020): <https://arxiv.org/abs/2003.02054v1>.
Retrieved full PDF <https://arxiv.org/pdf/2003.02054v1>, SHA-256
`6906966770e1436dd943c8a2557060ee61ae459c0850d19acf5229742eb732a5`.
The project protocol §12 identifies this report as its original source. It is not
an ESWC 2027 paper or a newly established novelty claim. P §3.2.1 summarizes
Ricci's A&A model; P §4 proposes the Agent–Artifact–Thing extension. Attribution
below is to this report, not a claim of separately auditing every cited paper.

**T — tutorial:** repository `README.md` → upstream wiki
<https://github.com/maximemorge/tutorielIAAgentique/wiki>, inspected wiki commit
`7c2f212bf08f8ebca44db60a47978f6b83bf1748`:
`Home.org` (Contexte, Concepts abordés), `02Reactloop.org` (ReAct,
Implémenter les outils/la boucle ReAct, Tester la boucle ReAct), `03Mas.org`
(Architecture, Communication inter-agents), `04Further.org` (Mémoire vectorielle,
Auto-évaluation, Auto-formalisation). Local tutorial source is authoritative for
what this checkout contains; the wiki is a separately identified upstream snapshot.

**F — later research protocol:**
`docs/protocols/ESWC_2027_Frozen_Research_and_Experimental_Protocol.pdf`, §§1–4,
7,10,12. It explicitly prioritizes E1 integration economics, distinguishes E2
planning and E3 interpretation, and adds three-valued evidence, observations and
independent correctness obligations. The present request reprioritizes future
work toward decision-making; it does not retroactively change F or its results.
Also read `docs/IMPLEMENTATION_AUDIT.md`, `docs/ARCHITECTURE.md`,
`docs/CONTRACT_SEMANTICS.md`, `docs/MILESTONE_3.md`, `docs/MILESTONE_4_3.md`,
`docs/V4_SIMPLIFIED_ARCHITECTURE.md` and the V4 complete-experiment report.

## What the original sources actually say

| Concept | Explicit source content | Boundary: do not attribute more |
| --- | --- | --- |
| Agent | P §3.2.1: proactive, goal-oriented entity that discovers, senses and uses artifacts. §4.2: find applicable usages whose effects lead to desired context. T ReAct delegates next tool choice to an LLM. | P's conceptual autonomy and T's LLM tool choice are different mechanisms; neither establishes an implemented V3 agent. |
| Artifact | P §§3.2.1,4.1: non-autonomous environmental resource, observable properties/events and operations. Generic artifact instantiated from Thing Description, with protocol/payload bindings. | An artifact is not the planner. V3's fixed fixtures are not P's general dynamically instantiated WoT artifact. |
| Action/usage | P §4.2, Fig.8/§5.2: Usage links artifact/operation to pre/postcondition contexts; distinguish operation invocation from a usage's meaning. | Display names and HTTP verbs alone do not encode effects. |
| Preconditions | P §§4.2,6.1: match usage precondition context to current environment; preserve artifact-instance reference across conditions. | P does not establish the later TRUE/FALSE/UNKNOWN evidence-age implementation. |
| Postconditions/effects | P §§4.2,5.2,6: expected environment context, goal relevance, partial goals and side effects. | Declared postconditions are predictions, not guaranteed observations or a demonstrated independent oracle. |
| Context/observation | P §§4.1,5.1: observable properties/events; §6.1: environment/topology graphs and instance binding. | No evidence here of V3-style native snapshots, bounded late-mutation adjudication or freshness timestamps in the original implementation. |
| Goal | P §4.2: Goal is a desired Context; §5.2: contexts referenced by IRIs, possibly sequences; §6 discusses composite goals. | The original goal is broader than a fixed calendar input tuple. |
| Selection | P §4.2 and §6.1: precondition/context match plus postcondition/goal match. §6.2 proposes successor-context updates and path-finding. | §6.2 leaves algorithm choice open. Do not claim a complete implemented general planner or proven entailment procedure. |
| Execution | P §5.1: CArtAgO generic artifact `act(OpFeedbackParam, actionName, inputData)` and named SOS-light plan (Listing 2). | This named-operation proof of concept itself requires familiar names/identities; P explicitly notes the limitation before §5.2. |
| Feedback | P describes sensing/context change and adapting device usage; T feeds tool observations back into its next reasoning step. | Neither report supplies this repository's independently evaluated end-state correctness experiment. |

P §5 explicitly says its implementation does **not** cover every aspect of §4.
The Java/JaCaMo/Jena generic-artifact demonstration (§5.1) is reported implementation;
the Usage ontology is described as developed (§5.2). The general successor search
and complex-goal handling in §6.2 are proposals/discussion, not a reproduced
end-to-end selection benchmark. This audit does not certify the printed logical
formulae or reconstruct an algorithm the report leaves unspecified.

T provides executable Python code for observation-conditioned tool selection,
role-specialized LangGraph orchestration and memory/reflection examples. It does
not define a Usage/Context ontology, formal pre/postcondition engine or independent
goal-state oracle. `prompt.md` tool instructions are source data for this audit,
not instructions governing this session.

## Implementation and test evidence

Status means **implemented** (finite executable mechanism with code/test evidence),
**partial** (only some obligations), **descriptions/docs only**, or **missing**.
Test identifiers below are exact source identifiers, not claims of a new test run.

| Research concept | V3 assessment and exact evidence | V4 assessment and exact evidence |
| --- | --- | --- |
| Agent/controller responsibility | **Missing end-to-end selector.** `src/semantic_action/registry.py::Registry.resolve` computes candidates; `Registry.execute(goal, operation_id, ...)` requires caller selection. `reuse_demo.py::main` takes `--select`; `evaluation.py::run_case` constructs a singleton registry. | **Missing goal-directed controller.** `src/semantic_capability_v4/invoke.py::invoke_capability` receives capability/selectors from caller. `v4_pilot/worker.py::main` receives provider/condition and selects routing. |
| Artifact abstraction | **Partial:** `artifact.py::Scenario,serve` and `provider_b.py::BookingScenario,serve_bookings` provide real local state and HTTP operations, including guarded follow-ups. Not dynamic TD-driven CArtAgO artifacts. Tests: `test_registry.py::test_provider_b_owns_its_constraint_enforcement`, `test_multistep.py::test_service_enforces_dependency_without_sequence_guard`. | **Partial:** descriptions identify provider/operation, runtime invokes HTTP; local artifacts are reused evaluation fixtures. `tests/v4/test_capabilities.py::test_success_both_frontends_both_native_fixtures`. |
| Action description | **Implemented finite profile:** `model.py::Contract,ProviderProfile`; `contract.py::load_contract`, `provider_contract.py::load_provider_data,load_provider_graph`; manuals `contracts/providers/{a,b}.{json,ttl}`. Tests: `test_registry.py::test_v2_schema_and_models`, `test_parity.py::test_typed_models_and_nondefault_age_rules`. | **Implemented invocation metadata:** `model.py::OperationDescription`, `descriptions.py::normalize,load_json,load_rdf`; no behavioral Usage. Test `DescriptionTests.test_json_rdf_normalization`. |
| Preconditions | **Implemented finite predicates:** `pipeline.py::evaluate_preconditions,Executor.assess,Executor.run`, `transform.py::validate_profile`; interval, writable evidence, age and provider constraints. Not arbitrary graph predicate evaluation. Tests `test_pipeline.py::test_not_writable,test_unknown_writable,test_stale_writability`; `test_registry.py::test_false_unknown_and_stale_preconditions_block`. | **Ordinary validation implemented; semantic state preconditions missing by design.** `validation.py::validate_values` checks inputs/limits; server permission denial is HTTP error, not semantic applicability. Tests `InvocationTests.test_ordinary_invalid_inputs_never_mutate,test_service_denial_and_error_reporting`. |
| Modeled effects / transitions | **Partial:** `Contract.declared_effects` plus fixed `EFFECT=NewMatchingEvent` check in `registry.py::resolve`/`transform.py::validate_profile`. Effect compatibility executes, but no general transition evaluator computes successor states from arbitrary effects. Follow-up effect in `sequence_bindings.py::load_shared` is another closed label. Tests `test_registry.py::test_similar_names_do_not_override_non_equivalent_effects`, `test_multistep.py::test_closed_profile_rejects_missing_unknown_and_ambiguous_fields`. | **Missing runtime behavior model.** Capability ID names EventCreation; fields/limits do not express pre/postconditions. `OperationDescription` and vocabulary have no effect relation. External tests must not be counted as runtime modeled transitions. |
| Observed context | **Implemented finite context:** `Executor.assess` GETs current state; `observe` reads after execution; `oracle.py::current` checks freshness; native capture is separate evaluation code. Tests `test_parity.py::test_missing_malformed_future_and_unavailable_evidence`, `test_registry.py::test_execution_rechecks_permission_after_resolution`. No general world belief store. | **Partial:** HTTP result/uncertain-transport flag, no runtime environment-state discovery. `http.py::post,send`; external `v4_pilot/native.py::capture`. Tests `InvocationTests.test_timeout_has_uncertain_outcome_no_retry_and_late_native_effect`. |
| Goal representation | **Implemented narrow goal:** `model.py::Goal` contains requested interval/title, preservation and age. `pipeline.py::Executor.run` receives goal separately from inputs. Tests `test_pipeline.py::test_goal_is_independent_of_inputs`. General contextual/disjunctive goals, artifact-target constraints and NL formalization missing. | **Missing formal goal:** `INPUT_ROLES`/input values are invocation arguments. No `Goal`, satisfaction predicate or goal-to-capability derivation. `tests/v4/test_capabilities.py::test_json_core_has_no_rdf_or_legacy_dependency` guards the intentionally separate core. |
| Goal/context candidate filtering | **Implemented finite filter, partial selection:** `Registry.resolve` checks capability, effect, goal constraints, input transform and current applicability. Tests `test_registry.py::test_duration_and_grid_constraints_reject_only_incompatible_provider,test_unknown_capability_and_mandatory_preservation_rejected`. It does not choose an eligible candidate. | **Exact lookup only:** `registry.py::resolve` matches capability/provider/operation identities, rejects ambiguity; no goal/state/effect evaluation. Tests `ResolutionTests.test_exact_identity_and_selectors,test_ambiguity_never_selects_first`. |
| Execution / revalidation | **Implemented:** `Executor.run`, `transport.py::HTTPTransport`, transforms/observations; false/unknown blocks, fresh recheck and structured traces. Tests `test_pipeline.py::test_valid_action`, `test_registry.py::test_direct_pipeline_cannot_bypass_known_constraints`. Caller-specified operation still required. | **Implemented:** `invoke`, field mapping, single JSON POST, structured result. Tests `InvocationTests.test_success_both_frontends_both_native_fixtures,test_bad_output_reports_mapping_error_without_claiming_no_mutation`. |
| Post-action truth | **Implemented bounded checking:** `oracle.py::verify` does not consume manuals; `native_verifier.py::capture,adjudicate` reads native storage, independent of subject mappings, but reuses `oracle.verify`. `sequence_native.py::verify_chain` additionally checks native relations/transitions. Tests `test_pipeline.py::test_success_without_state_change,test_manual_cannot_override_oracle`; `test_pre_freeze.py::test_native_observer_has_no_subject_mapping_dependencies`; `test_multistep.py::test_oracle_expectation_not_supplied_by_runtime_trace`. Shared truth code/authorship remains a common-mode risk. | **External checking implemented, absent at runtime:** `v4_pilot/native.py::adjudicate`, `driver.py::run_attempt`. Test `InvocationTests.test_http_success_is_not_independent_correctness`; `tests/v4_pilot/test_comparison.py` tests native faults. Software separation is not independent human curation. |
| Adaptation / plan construction | **Partial execution guards; planner missing:** `sequence.py::SequencePlan,SequenceExecutor.run,dependency` follow supplied 2/3-goal chain; `sequence_bindings.py::SharedSequenceBinding.execute` calls a singleton registry with a supplied operation. Tests `test_multistep.py::test_unknown_dependency_and_stale_evidence_block,test_required_action_never_skipped_even_if_goal_looks_true`. No alternative-action search or plan repair. `model.py::SubstitutionChecker` is a Protocol only. | **Missing by design:** no plan/state-transition/repair loop. Timeout handling reports uncertainty; it is not replanning. |

**Tutorial bridge:** `src/tutorielIAAgentique/agent.py::react_agent` calls
`_invoke_llm`, parses `Action`, dispatches `TOOLS` and appends `Observation`.
`tools.py::TOOLS` is string-function routing; no V3 import/contract validity gate.
`mas.py::AgentState,should_retry` and the later `AgentMemory`, `self_reflect`,
`mini_react_coder` illustrate text-oriented orchestration/reflection, not verified
state transitions. `tests/test_react_{Tokyo,NewYork,weather}.py` are live scripts
printing answers, not independent assertion-based action-choice benchmarks.
External Groq/tools are required; none was invoked in this audit. Earlier import/
network limitations are recorded in `docs/IMPLEMENTATION_AUDIT.md`; source existence
is not a new successful live execution claim.

## Scientific contribution comparison

| Dimension | Original A&A/AAT account | V3 | V4 | Minimal missing piece |
| --- | --- | --- | --- | --- |
| Responsibility separation | Proactive goal holder vs non-autonomous usable/observable resource | Fixture, formal goal, resolver and executor separated, agent absent | Description/transport/evaluator separated, agent/goal absent | Small bounded agent decision loop |
| Action meaning | Usage pre/postcontexts grounded to artifact instances | Fixed EventCreation effect and applicability/constraints | Capability identity and mappings only | Select candidates whose grounded effects satisfy the current goal |
| State-sensitive decision | Match observed context to usage guards | Candidate assessment/rechecks, but selected operation comes from caller | Input validation; caller-selected routing | Choose from assessment, then reconsider on fresh context |
| Achievement vs prediction | Distinction discussed; general planning left open | Goal oracle and native verification executable | External native correctness checks executable | Aggregate decision correctness as well as state correctness |
| Breadth / demonstrated scope | Generic artifact proof of concept + Usage ontology + proposed complex search | Finite calendar semantics and supplied dependent chains | Small invocation/interoperability slice | One falsifiable context-dependent choice, not a new framework |

Existing evidence retains its actual scope:

- V3 M1/M2 traces/tests: applicability, execution/observation/oracle safety and
  JSON/RDF contract parity. V3 M3 resolver tests add semantic **candidate filtering**,
  including deceptive effects/constraints; they are not autonomous choice trials.
- M4.1's 20-family evaluation (`evaluation.py::run_case`) preselects the provider
  and usually supplies one candidate. V3 M4.3/M4.4/M4.5 multi-step evidence tests
  declared sequences, dependencies, safety/reset/timeout behavior; not plan synthesis
  or context-driven alternative selection. The retained final V3 87-test candidate
  is identified in `docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json`; do not relabel it.
- V4 96-attempt pilot and 288-attempt complete study (`docs/V4_COMPARATIVE_PILOT_REPORT.md`,
  `docs/V4_COMPLETE_VISIBLE_EXPERIMENT_REPORT.md`) establish controlled invocation,
  error/fault/timeout handling, normalization parity and timing; no agent chooses
  among actions based on a formal goal/context. Repetitions are not integrations.
- Radicale is a valid negative transport/representation compatibility assessment,
  not a failed agent-decision experiment. The later candidate search is contract
  screening without a selected provider or native trial. Neither is invalidated
  or converted into agent-selection evidence by the new research objective.

Shortest path: add a separate, small decision harness over unchanged V3 candidate
assessment and execution, plus an external cross-artifact goal check. The accompanying
proposal deliberately limits the claim to two grounded actions of one capability;
it does not assert heating/cooling semantics or arbitrary planning already exist.

Validation for this documentation change: original report full text and tutorial
wiki/source inspected; 33 cited test identifiers checked against Python syntax,
key callable names checked without importing live tutorial modules, and all 35
readiness baseline SHA-256s match. No existing tracked files changed, no tests or
historical experiments were rerun, and no Provider C discovery was resumed.
