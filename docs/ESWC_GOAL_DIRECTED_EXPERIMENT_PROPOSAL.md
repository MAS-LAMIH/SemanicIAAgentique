# Minimal goal-directed artifact-action experiment

**Proposal only.** Implement no code in this task. Keep V3/V4 and their frozen
vocabularies/evidence unchanged; a future implementation belongs in one separate
small experiment module and its tests, not a new framework. No Provider C, model
API, nested CLI, natural-language planner or ontology reasoner is required.

## Question and limited claim

Can a deterministic agent choose a suitable **grounded artifact action** from
its goal, current observations and semantic descriptions, then reconsider when
context invalidates the choice, without a caller supplying the operation ID?

Use existing V3 calendar/booking artifacts, not another interoperability search.
Actions have different artifact-scoped effects even though both instantiate the
same EventCreation capability. This tests a minimal action-selection layer; it
is not arbitrary action-type selection (e.g. heating vs cooling), autonomous goal
formation or multi-step plan synthesis. General-purpose contextual goals would
require more than the current V3 model; do not smuggle that claim into this test.

## One scenario: create exactly one event on an allowed writable calendar

Explicit task goal: create exactly one new event across allowed artifacts
`{A,B}`, with title `Decision test`, start `2030-01-07T10:00:00+00:00`, end
`2030-01-07T11:00:00+00:00`; preserve all unrelated event records on both.
For an artifact-restricted control, allowed artifacts is `{A}`. The task contains
no operation ID, preferred provider, endpoint, expected choice or plan.

Let `E_A,E_B` denote native event sets. Goal satisfaction is one new matching
event in an allowed set and no other new/deleted/changed records anywhere. This
cross-artifact predicate is a **proposed experiment-owned goal wrapper**, not an
existing feature of `semantic_action.model.Goal`. Per-candidate checks reuse its
unchanged single-artifact Goal; an external aggregate check adds destination and
exactly-one-across-both obligations.

| Grounded action | Different preconditions | Different expected effect |
| --- | --- | --- |
| A calendar `create_event` | Current A.writable TRUE; positive interval; ordinary inputs | Add matching event to `E_A`; preserve `E_B` and existing A records |
| B appointment `reserveAppointment` | Current B.can_book TRUE; positive interval; exact milliseconds; 15-minute grid; duration ≤2 hours | Add matching native booking to `E_B`; preserve `E_A` and existing B records |

Those are different state updates on different artifact instances, not merely two
names for the same ground transition. The generic V3 `NewMatchingEvent` label does
not itself represent the cross-artifact frame condition: the proposal makes that
additional grounding/verification explicit. Endpoints, mappings and constraints
already exist in `contracts/providers/{a,b}.json`; no new capability is needed.

Initial observable context: both artifacts reachable; A writable, B not writable;
neither contains the requested event; both have one unrelated native sentinel.
Read permitted API observations through V3 assessment, with explicit timestamps
and current evidence. Agent never reads fixture storage or interventions.

Main episode:

1. Agent reads the goal and available manuals/registrations, calls `Registry.resolve`,
   filters to eligible goal-relevant grounded effects, and chooses A without caller
   selection. Log the snapshot, all rejection reasons and chosen operation.
2. Before dispatch, the external harness revokes A's permission and grants B's.
   Synchronize at the logged decision boundary, not a sleep-based race. Do not
   reveal the intervention schedule or expected choice to the agent.
3. `Registry.execute(goal, chosen_id, ...)` performs fresh resolution. A is no
   longer eligible: no POST occurs. The agent observes the new context and chooses
   B on a second bounded decision cycle, then executes B through V3's guarded
   pipeline. No raw mutation bypass or post-timeout speculative retry.
4. Independently capture both native stores. Exactly one matching B booking must
   exist; A and unrelated records remain unchanged; B's returned ID must be usable.
   The goal is now achieved and the agent stops.

The permission flip is an exogenous context change, not an agent effect. Keep
snapshots before/after the flip and immediately before mutation. Preservation of
permissions is assessed against the post-flip state and the explicit intervention
record; do not count the authorized flip as a forbidden agent mutation or silently
ignore other changes. On a fresh unchanged-context variant the same goal chooses A;
on initially reversed permissions it chooses B. Thus the choice changes with context.

## Small decision loop and reuse boundary

Proposed policy, not current V3 behavior:

```text
for at most two decision cycles:
    observe/check the aggregate goal; if already achieved, stop
    resolution = existing Registry.resolve(per_artifact_goal)
    eligible = candidates with TRUE applicability, required effect,
               preservation compatibility, and artifact allowed by task goal
    if empty: record false/unknown reasons and stop without mutation
    choose an eligible candidate (stable identity tie-break only if several valid)
    result = existing Registry.execute(per_artifact_goal, chosen_operation_id, ...)
    if dispatch occurred: observe and verify; stop (no alternate mutation after uncertainty)
    otherwise: reconsider only after fresh context (bounded second cycle)
```

The missing component is this choice/reconsideration policy plus target grounding,
not another executor. `Registry.execute` still needs an operation ID; **the agent
computes it**, whereas current demos and tests pass it from the caller. Eligibility
alone is not a selection result. The policy must not use candidate position, provider
name, test ID or oracle expectation as a decision shortcut. Where both effects are
valid, any declared stable tie-break is sufficient; no optimality is claimed.

Reuse unchanged:

- `semantic_action.registry::{Registration,Registry.resolve,Registry.execute}`;
  `pipeline::{Executor.assess,Executor.run}`; existing JSON v2 manuals/loaders.
- `artifact::{Scenario,serve}`, `provider_b::{BookingScenario,serve_bookings}`;
  `model.Goal`, freshness checks and explicit false/unknown behavior.
- `native_verifier::{capture,NativeExpectation,adjudicate}` for chosen-artifact
  truth, plus a small experiment-owned aggregate raw-state check over both stores.
  Do not let the agent supply native expectations or which state differences count.
- `supervision::{assert_reset,supervise,settle_and_capture}` where appropriate;
  fresh fixtures/directories and structured traces. Check both fixtures/reset state.

Neither V3's single-artifact Goal nor its native adjudicator already checks the
aggregate disjunction/target restriction. Those are explicit new experiment logic,
kept outside frozen sources. No editing registry, effect validator, V4 or vocabulary.
If this small wrapper cannot express the obligations honestly, report the gap;
do not call an externally supplied choice autonomous.

## Fair nonsemantic comparison

Use one ordinary, hand-coded context-sensitive agent with explicit A/B routing:
read each provider's documented permission state, apply its native constraints,
check whether its native creation affects an allowed target, choose an applicable
route and recheck immediately before invoking `LocalExecutor.run` with
`CalendarLocal`/`BookingLocal` and `contracts/api_local/{a,b}.json`.
It uses no shared ontology, RDF, semantic registry or contract-effect lookup.
A small new read-only local assessment helper is required: `LocalExecutor` has
no existing `assess` method. Reuse local `validate`, `state`, ordinary transport
and freshness checking; never invoke creation just to test eligibility.

Give both agents the same goal/state information, A/B API specifications, budgets,
intervention boundary and independent oracle. The baseline encodes operation meaning
and constraints in ordinary code; do not deprive it of effects or context to make
semantics win. Both can and should achieve equal correctness. The comparison tests
where decision knowledge resides and whether the proposed semantic agent actually
uses descriptions; it does not assume an accuracy or efficiency advantage.

## Six diagnostic cases, same scenario

Run each policy once per case on fresh state (12 episodes, not 12 providers or
integrations). Hold JSON encoding fixed; no JSON/RDF benchmark is needed.

| Case | Context/goal change | Correct decision behavior | Independent result |
| --- | --- | --- | --- |
| D1 | A TRUE, B FALSE; no change | Choose/execute A | One correct A event; B unchanged |
| D2 | A FALSE, B TRUE; no change | Choose/execute B | One correct B event; A unchanged |
| D3 | A TRUE/B FALSE → A FALSE/B TRUE at decision boundary | Initial A intent; zero A POST; reconsider and execute B | Exactly one B event; A unchanged |
| D4 | A UNKNOWN, B FALSE | No mutation; report insufficient/false applicability | Both native stores unchanged; goal unachieved |
| D5 | Only A allowed by goal; A FALSE, B TRUE | Do not choose B merely because it is writable | Both unchanged; goal safely reported unachieved |
| D6 | A FALSE, B TRUE; B returns 201 without storing | Choose B correctly, then report failed achievement; stop | No matching new native event; no false success |

D1/D2 isolate context dependence; D5 isolates goal/grounded-effect relevance;
D3 tests reconsideration and revalidation; D6 separates good choice from failed
execution. Add source-level/regression checks that reverse candidate enumeration
and use opaque operation identifiers while preserving legitimate bindings. A
policy that always executes the first registration should fail D2/D5. Do not
artificially rename the baseline's native endpoints without updating its explicit
binding information; give both the same permitted interface information.

As a mechanism diagnostic, withhold/corrupt the semantic candidate's required effect
assertion and verify fail-closed behavior in a separate non-scored validation test.
This tests consumption of descriptions, not a fair comparison of bad semantic
information against a correct baseline, and does not create a new native action.

## Correctness, measurements and falsification

Record task goal, timestamped observations, every candidate verdict/reason,
selected operation before/after context change, all assessment/dispatch requests,
returned result, independent raw before/after states for both artifacts, mutation
counts, uncertainty and terminal decision. The evaluator derives expectations from
fixture contracts and the fixed case sheet, never from the manual's declared effects.
Native data-path separation is not independent human authorship; disclose shared
curation and shared `oracle.verify` code if reused.

Primary: correct action choice or justified abstention for the observed goal/context;
for D3 separately score valid initial intent, post-change safe rejection and new
choice. Secondary: independently verified achievement, false achievement claims,
invalid executed actions, unexpected mutations and number of decision cycles.
D4/D5 can pass decision safety while not achieving the goal. D6 can pass choice
correctness while failing creation; do not collapse those outcomes into one success.
Runtime is descriptive, not integration effort or an agent intelligence score.

Budgets: two decision cycles, at most one dispatched mutation across both stores,
existing five-second HTTP timeout, 60-second outer supervision, no automatic
mutation retries. The D3 rejected pre-dispatch selection is not a dispatched call.
Any timeout/uncertain dispatch ends the episode with independent bounded observation;
never switch artifacts after an uncertain creation. Reset/settle both fixtures before
the next case; retain incomplete and failed traces.

Falsifiers include caller-supplied selection, unchanged choice in D2/D3, ignoring
target restriction in D5, using unknown/stale facts as TRUE, selecting from labels
or ordering rather than the model, a POST to revoked A, duplicate A+B creation,
forbidden sentinel changes, or accepting D6's HTTP response as achievement.
If the hand-coded baseline matches the semantic policy, report parity; if it
outperforms it, report that. Twelve deterministic episodes establish a mechanism
or expose its absence, not statistical superiority or open-world generality.

## Shortest next implementation step

After review, write one standalone `experiments/goal_choice.py` and one assertion-
based test file, with the six cases, two policies and aggregate oracle. These paths
are proposals and do not exist as part of this change. Keep observations separate
from native evaluation, compute choices inside each policy, save all decisions and
run D3 first as the decisive demonstration. Then run all 12 episodes into a new
output directory and inspect failures. No framework, tutorial/LLM dependency,
Provider C, new runtime capability or historic experiment redesign is necessary.
