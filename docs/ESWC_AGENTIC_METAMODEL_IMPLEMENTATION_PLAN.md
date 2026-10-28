# Smallest executable Agent–Artifact implementation plan

**Design only.** No architecture implementation, new fixture, importer, model call
or experiment is part of this change. Source reference:
`297861ae8d7056cd9fbf3c210c5a747cc633027d`.
See `ESWC_AGENTIC_AGENT_ARTIFACT_ARCHITECTURE.md` for original-source attribution,
records, component diagram, interfaces and admission rules. Preserve frozen V3/V4,
tutorial and all existing results; add a separate experimental slice only after review.

## Demonstration: one room artifact, heating and cooling usages

The original report's §2.2 motivates heating/cooling according to context. Our
new fixture is a controlled virtual room, **not a real held-out provider**.
The agent receives user objective “Bring this room to 22°C”, with approved formal
goal `room.temperature_c = 22` and invariants preserving unrelated room data.
Initially the demonstration uses the explicit numeric objective; it makes no claim
of interpreting arbitrary phrases such as “comfortable”.

Native state: integer temperature in [18,26] °C, heater/cooler readiness facts,
revision, mutation count, pending-request count and an unrelated sentinel record.
GET `/state` returns observable temperature/readiness/revision, timestamp and
all frame-relevant public data, including the unrelated sentinel record. Private native storage/journal and case expectations remain
with the evaluator. Two operations have genuinely different effects:

| Usage / operation | Preconditions | Expected effect and frame |
| --- | --- | --- |
| HeatOne / POST `/heat` | Heater ready TRUE; 18 ≤ current T < 26; current revision matches | T′ = T + 1; mutation count +1; revision +1; cooler/readiness/unrelated records unchanged |
| CoolOne / POST `/cool` | Cooler ready TRUE; 18 < current T ≤ 26; current revision matches | T′ = T − 1; mutation count +1; revision +1; heater/readiness/unrelated records unchanged |

Both use JSON `{ "expected_revision": <observed integer> }`; only the executor
fills this reserved field from a valid permit. Responses are JSON with the resulting
revision and state/result. The server checks the expected revision atomically
before mutation and returns 409 without mutation on conflict. This is deliberately
new controlled apparatus, not an undocumented feature of existing V3 fixtures.

With both devices ready at T=21, both operations can be operationally applicable,
but only HeatOne's predicted postcontext meets the 22°C goal. At T=23, only CoolOne
contributes. This distinguishes **goal relevance** from mere precondition truth.
The new evaluator implements just these reviewed ±1 successor rules and bounded
numeric/equality predicates. The integer delta is data in each reviewed post-template; the evaluator
reads it through a closed `add_integer` rule restricted to ±1, rather than deciding
behavior from the Usage name. No arbitrary expression language, SPARQL Update planner,
OWL entailment or search algorithm is implied by storing those rules in RDF.
At T=20 neither one-step effect reaches 22: report NO_DIRECT_MATCH, not a proof
that 22 is unreachable. Multi-step heating is deliberately outside this first profile.

## Main end-to-end episode

0. Native fixture and API document exist before the agent runs. Extract the
   OpenAPI structural graph, combine with a separately reviewed Usage graph,
   validate binding/behavior/observation support, and admit the versioned artifact.
   Keep the source/graph/review hashes. No unreviewed graph is executable.
1. User supplies the objective. Controller creates AgentState/formal Goal and
   asks the injected reasoner for one structured tool proposal per turn.
2. `Discover` returns the admitted room artifact and its two Usages. `Observe`
   reads T=21, both devices ready, revision 0; immutable evidence snapshot is recorded.
3. Matcher predicts HeatOne→22 and CoolOne→20; the reasoner proposes HeatOne using
   its Usage ID and snapshot reference, not a raw HTTP endpoint.
4. Evaluator-controlled context change sets T=23, revision 1 after proposal and
   before authorization. It does not supply the new correct action to the controller.
   Guard reobserves, rejects the stale proposal; HeatOne would now yield 24 and
   does not meet the goal. No heating POST is dispatched.
5. Structured feedback contains stale-context/noncontributing-effect reasons and
   evidence. The controller observes/reasons again; matcher now exposes CoolOne→22.
   Reasoner proposes CoolOne; fresh permit binds goal, Usage version and revision 1.
6. Guarded executor sends POST `/cool` with expected revision 1. Native state becomes
   T=22, revision 2, mutation count 1. Atomic revision enforcement remains necessary
   if a new race occurs after the guard's last read.
7. Observer reads fresh state; runtime verifier checks actual postcondition, frame,
   evidence and goal. Independent scorer reads private native state/journal, accounts
   for the authorized external revision/temperature change, and checks exactly one
   cooling mutation with unrelated records preserved.
8. Feedback enters the ReAct transcript. `Finish` can report SUCCESS only after
   verification. An earlier model-generated final answer cannot skip that check.

This exercises discovery, observation, semantic Usage matching, formal applicability,
execution, postcondition verification and continued agentic reasoning through a
rejected proposal. The separate no-intervention cold/hot controls below execute
both action types. It is more than selecting between providers for EventCreation.

Bound the episode to six reasoner/tool turns, at most one mutating dispatch,
five-second HTTP timeout and 60-second outer supervision. A pre-dispatch refusal
is not a mutation. On uncertain dispatch/timeout, stop new mutation proposals and
observe within a bounded terminal window; never blindly switch actions or retry.
Known no-mutation rejection can lead to another observation/proposal within budget.
Definite postcondition failure is retained and terminates mutation attempts.

## RDF/record representation and acquisition slice

New data files instantiate Artifact, Thing, Operation, Usage and Context separately.
The following is an **illustration of the proposed profile**, not existing ontology
code or a claim about the original report's property spellings:

```turtle
@prefix aa: <urn:eswc:aat:prototype:1#> .
@prefix ex: <urn:example:room:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# Extractable structural facts, with source pointers/hashes in the actual graph:
ex:artifact a aa:Artifact ; aa:represents ex:thing ; aa:hasOperation ex:heat .
ex:thing a aa:Thing .
ex:heat a aa:Operation ; aa:method "POST" ; aa:path "/heat" ; aa:inputSchema ex:input .
ex:input aa:hasField ex:revisionField .
ex:revisionField aa:fieldName "expected_revision" ; aa:datatype xsd:integer ; aa:required true .
# Separately curated behavior; never inferred automatically from POST or "heat":
ex:heatUsage a aa:Usage ; aa:forArtifact ex:artifact ; aa:forOperation ex:heat ;
    aa:hasPrecond ex:heatPre ; aa:hasPostcond ex:heatPost ; aa:profile "room-step/1" .
ex:heatPre a aa:ContextTemplate .
ex:heatPost a aa:ContextTemplate .
```

The abbreviated template nodes above are **not sufficient for admission**. Complete
profile data must ground the subject/property, readiness/bounds, ±1 rule, frame,
units, evidence policy and provenance; likewise provide CoolOne's distinct rules.
Shapes/validator must reject these incomplete illustrative nodes if loaded as an
executable artifact. Validate record↔RDF preservation of the supported relationships,
not just syntactic RDF parsing. No JSON blob disguised as a fully interpreted
behavior graph and no automatic import of external ontology code.

For the first importer, support local OpenAPI JSON paths, GET/POST operations,
object schemas with supported primitive properties, declared required flags/media
and response codes, and bounded local references. Unsupported combinations are
reported/quarantined, not flattened silently. Preserve document hash + JSON Pointer
for every extracted structural assertion. Initially hand-reviewed domain annotations
provide Usage pre/postcontexts and property meanings; even explicit prose is only
a claim until reviewed against native behavior. Admission verifies shape, scope,
profile support and approved local binding before catalog registration.

A required negative test imports the same API without behavior annotations:
structural graph succeeds, executable admission fails with missing-semantic-evidence
reasons. Thus automatic acquisition is demonstrated without pretending it solves
behavior discovery. API/mapping drift invalidates version-bound registrations.

## Reuse decisions and genuinely new code

Do not copy V3's calendar pipeline into a “generic” class or add thermal predicates
to its frozen vocabularies. Reuse its neutral Truth/time/freshness primitives,
HTTPTransport/ApiResult, process supervision and suitable settling unchanged.
For existing calendar entries, a thin legacy adapter delegates to Registry and
Executor, loaders, transformations and existing native verifier. They remain the
sole authorities for their finite legacy profile; do not create a second calendar
resolver or decoder. The new room profile requires a small domain evaluator,
observer field projection, guarded binding and native scorer because those
semantics do not exist in V3. That is explicit new work, not a reuse claim.

Use tutorial `react_agent`'s loop as the starting point: goal/user message, bounded
reasoning turn, one tool proposal, actual tool result and observation feedback.
Adapt outside the import-time Groq/global TOOLS module. The mandatory interface is
an injected `Reasoner.propose(view)`, not Groq, LangGraph or an external API.
The default scripted backend supplies reproducible proposals and consumes feedback;
an injected faulty proposal tests guard authority. Optional model adapters must
use the **same** typed tools/guard/verifier and be evaluated separately. Offline
protocol tests do not prove that a real LLM interprets goals or plans reliably.

Keep implementation to these **proposed, currently nonexistent** files rather
than a service/framework/package hierarchy:

- `experiments/aat_agent.py`: records, small in-memory catalog/facade, observer,
  finite profile matcher/guard, guarded execution and ReAct controller. Logical
  interfaces can be functions; no eight-class hierarchy or plugin loader.
- `experiments/aat_demo.py`: local room fixture, native scorer, intervention driver
  and JSON/CSV export. Agent worker imports no native fixture/evaluator code.
- `experiments/openapi_to_artifact.py`: bounded structural extractor/admission checks.
- `tests/aat/test_agent_artifact.py`: focused assertion-based tests.
- Small data files for new experimental RDF profile, native OpenAPI document and
  reviewed room Usages. No edits to frozen V3/V4 files or historical manuals.

The first room demo need not rebuild a generic legacy bridge to every old example:
call unchanged V3 entry points when exercising that profile and keep existing
calendar regression tests. No new HTTP client, remote registry, ontology engine,
memory service or full MAS orchestration is required.

## Smallest executable development sequence

1. **Native apparatus first.** Implement unchanged-by-mappings room operations,
   reset, private journal and independent native expectations. Validate heat +1,
   cool −1, bounds, revision conflict and unrelated-state preservation with direct
   native requests. Pin source/environment; do not derive native answers from Usages.
2. **Metamodel and finite semantic core.** Define separate Artifact/Operation/Usage/
   Context/Goal records and small RDF profile. Implement reviewed room predicates,
   prediction, grounded subject checks and goal/frame comparison. Reuse V3 time,
   truth and transport primitives. Test FALSE/UNKNOWN and unsupported predicates.
3. **Acquire and admit.** Import the fixture's actual OpenAPI into structural RDF;
   validate provenance and unsupported cases. Add reviewed behavior annotations,
   test quarantine vs admission, and register the single artifact/two Usages. Do
   not hand-register a graph that failed validation just to complete the demo.
4. **Connect the agentic loop.** Adapt the tutorial's bounded loop with injected
   proposal backend, explicit tool facade and feedback. Route mutations only
   through permit checks; gate final success. Run the main stale-Heat→Cool episode
   with fixed barriers and actual observations, not replayed expected state.
5. **Compare and retain.** Run the six cases below under both semantic and
   procedural controllers, fresh fixture each time. Retain proposals, candidate
   assessments, RDF/source hashes, authoring provenance, API traces, raw context,
   native states/journal, rejections/timeouts and final verdicts. Export JSON/CSV
   and one concise results table. No large benchmark or prospective cost protocol.

These are sequential functional increments, not instructions to implement now.
Native/profile tests must pass before agent results are interpreted. A necessary
frozen-code change is an architectural incompatibility: report it and stop that
reuse path instead of silently unfreezing historical candidates.

## Fair baseline and falsifiable evaluation

Baseline is a procedural ReAct controller with the same goal, discoverable API
bindings, observable state, reasoner backend, feedback/budgets and guarded transport.
Its small local code explicitly knows heat/cool readiness, bounds, ±1 effects and
goal contribution; it does not read RDF Usage semantics. Structural discovery can
be shared because it does not tell the controller what the actions mean. The
semantic guard derives conditions/goal relevance from reviewed Usage records;
the baseline guard applies equivalent handwritten rules. Independent native scoring
is identical. Do not compare a state-aware semantic controller with a blind script.

| Case | Required observations/behavior under both controllers |
| --- | --- |
| R1: cold 21, both ready | Discover/observe, select HeatOne (not CoolOne), execute once, verify 22 |
| R2: hot 23, both ready | Select CoolOne, execute once, verify 22 |
| R3: context changes 21→23 after Heat proposal | Reject stale/noncontributing Heat, observe feedback, select Cool, one mutation total |
| R4: cold, heater readiness missing/unknown | No authorized heat; cool does not meet goal; report blocked/unknown without mutation |
| R5: cold, heat returns success without changing state | Correct initial choice but failed postcondition; no verified success or speculative alternate |
| R6: already 22 | Verify actual goal and stop without mutation |

Twelve deterministic episodes (six cases × two controllers) are diagnostic, not
independent agents/providers or a generalization sample. Additional focused tests
must reject an LLM-proposed Heat at 23 despite true operational preconditions,
raw-URL/tool injection, unknown Usage/predicate, early Finish, observation tampering,
unreviewed imported graph and atomic revision races. Reordering entries and renaming
opaque Usage/Operation IDs while preserving approved bindings/rules must not change
which effect is selected. A timeout test must retain
late native state separately from runtime success and forbid another dispatch.

Correctness: native temperature exactly equals the user goal where success is
claimed; exactly one authorized ±1 transition in R1–R3; zero mutations in R4/R6;
no sentinel/readiness corruption; consistent counters/revisions after separately
accounting for R3's authorized external change. Private native scorer uses fixture
contract/expected transitions, not declared postconditions as its answer key.
R5 must expose the difference between correct selection and failed achievement.

Report selection/abstention, invalid proposals vs invalid executions, postcondition
and goal truth, unknown-state handling, reconsideration turns, unnecessary mutations
and honest completion. Shared human/AI authorship and common-mode verification
risks must remain explicit. Parity with the procedural baseline is a valid result;
semantic superiority, labor savings and broad ontology reasoning are not assumed.
Actual model-backed reasoning would be a separate opt-in measurement with logged
backend/settings/exposure; the scripted demonstration alone cannot substantiate it.
