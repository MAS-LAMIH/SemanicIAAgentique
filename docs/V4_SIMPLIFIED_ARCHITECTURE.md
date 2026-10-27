# V4 simplified architecture — proposal for review

Status: design only. Branch `codex/v4-simplification-proposal`, based on
`ee3aa0bac538bf71b2acd1d26af22a1bcb913e60`. No V4 implementation, schema, new
provider description or dependency change is introduced in this step. V3 remains
intact; [recovery instructions](V3_PRESERVATION.md) identify its immutable backup.
Only visible Providers A/B are in scope. Provider C remains sealed.

## Purpose and conceptual boundary

V4 asks whether reusable capability knowledge helps integrate differently named
Web API operations and data formats. A capability description declares the
operation's intended domain meaning and data interface. It is an integration aid,
not an assertion that a call will establish a modeled world state.

The runtime has four concepts: capability, operation description, field mapping
and invocation result. The caller supplies a capability identifier and ordinary
input values, optionally an operation/provider selector. There is no Goal,
Contract, effect set, precondition truth value, expected transition, observation
obligation, evidence-age policy or behavioral proof. In particular, V4 will not
call V3 `Executor`, `Registry`, `assess`, `verify` or `LocalExecutor` under a new name.
The runtime never imports an evaluator or reads fixture storage.

## Vocabulary and representations

Start with a finite local vocabulary versioned independently as `capability/v4/1`:
`EventCreation` means the intent to create a time-bounded titled event; its input
roles are `start_time`, `end_time`, `title`, and its immediate response role is
`id`. Specify timezone-aware instants and an opaque string identifier. These roles
are defined once, not inferred from provider operation names. Different domain
meanings must have different identifiers even when their names look similar.

Use stable absolute identifiers (a documented project namespace) in JSON and RDF.
Do not change the meaning of the existing V3 namespace or regenerate its ontology.
Initial matching is exact capability-ID equality. No OWL reasoning, subclass
closure, fuzzy names, LLM inference, SPARQL server, remote registry or discovery.
This is a deliberately limited reusable vocabulary, not general semantic inference.

Each provider description contains exactly the following information:

| Field | Meaning |
| --- | --- |
| `description_version` | V4 description profile version, initially 1 |
| `provider_id`, `operation_id` | Unique identifiers, independent of display names |
| `capability_id` | Reference to the shared capability meaning |
| `method`, `path` | Concrete operation reference at an evaluator/caller-configured origin |
| `input_mapping` | Native request field to canonical role plus named conversion |
| `response_mapping` | Canonical response role to native response field plus conversion |
| `input_limits` | Ordinary declared API input bounds, where needed |

A finite JSON profile and a finite RDF/Turtle profile must carry these same
fields. Both loaders construct the same plain OperationDescription data structure
directly; JSON must not build an RDF graph internally. RDF uses explicit named
properties and mapping nodes. Both reject missing fields, duplicate declarations,
unsupported versions/conversions and ambiguous operation IDs. JSON rejects duplicate
keys and nonfinite numbers; RDF rejects conflicting/multiple values for singleton
properties and unsupported profile constructs. RDF set semantics cannot distinguish
repeated identical triples; those are semantically idempotent, not extra information.
Equal normalized descriptions receive identical validation and execution.

Use a closed, hand-written profile validator shared after parsing. Keep the
profile small enough that this is understandable. No new schema/validation
framework is proposed. If that becomes unwieldy during implementation, revise the
proposal rather than quietly adding an architecture layer. JSON uses the standard
library; the RDF frontend alone requires RDFLib and its necessary dependencies.
Install RDF support for B/C comparison environments, but do not make the JSON
runtime import RDFLib. Pin actual versions when implementation starts, not here.

## Visible mappings and invocation

| API detail | Provider A | Provider B |
| --- | --- | --- |
| Native operation | `create_event` | `reserveAppointment` |
| HTTP operation | `POST /events` | `POST /bookings` |
| Request fields | `start_time`, `end_time`, `title` | `begins_ms`, `finishes_ms`, `label` |
| Conversion | ISO instants unchanged | ISO instants to integer epoch milliseconds |
| Immediate returned ID | `id` | `booking_ref` |
| Ordinary bounds | Nonempty title and positive interval | Same, plus existing two-hour maximum and 900-second time grid |

These details were inspected in `contracts/providers/{a,b}.json`,
`src/semantic_action/{artifact,provider_b,local_baseline}.py`. They are descriptions
of visible APIs, not new provider implementations. No precision truncation:
conversion rejects values that cannot be represented exactly. Neither role names
nor a declared capability guarantees that the provider will store correct data.

Invocation flow:

1. Load a finite, explicitly supplied list of descriptions into an in-memory list.
2. Resolve exact capability identity, then an optional explicit operation/provider
   selector. Return not-found or ambiguous when zero/multiple candidates remain.
   Listing candidates does not call providers. Never choose the first match or
   fall back to another operation after failure.
3. Validate ordinary inputs: required fields, types, title length, timestamps,
   positive interval and API bounds. These are checks on the submitted request,
   not reasoning about live permission, world state, effects or evidence.
4. Apply the small conversion table and field mapping; execute the selected HTTP
   operation once. Use explicit configured loopback origins for the initial A/B
   prototype, fixed allowed methods/paths, no redirects, and a five-second timeout.
5. Decode/map the immediate response and return structured data. No permission
   GET, post-call state GET, revision check or runtime oracle is required.

The service still enforces its own authorization and native validation. Permission
failure is an HTTP error. Inability to establish a live permission in advance is
not a third semantic truth value. A timeout can leave remote effects uncertain;
report that transport outcome and never automatically retry a mutation.

InvocationResult fields: `operation_id`, `http_status` (nullable), `http_ok`,
`output` (nullable), `error_kind` (nullable), `diagnostics`, and
`remote_outcome_unknown` for a dispatched request whose outcome is unknown. Suggested
error kinds: description, resolution, input, transport, HTTP and response-mapping.
No `goal_achieved`, `verified`, `applicability` or `oracle_verdict` field exists.
For example, HTTP 201 with no stored record is `http_ok=true`; only the separate
evaluator will classify it as incorrect. A missing response ID is a mapping error,
not a proof that the operation did not mutate. Raw responses may be retained in
local diagnostic artifacts with the same policy for every condition.

## Proposed module size and component reuse/removal table

Target a separate `src/semantic_capability_v4/` package with six small modules:
`model.py` (plain data), `descriptions.py` (two parsers/shared profile validation),
`mapping.py` (conversion table), `registry.py` (finite lookup), `invoke.py` (input
validation/mapping) and `http.py` (transport). No provider subclasses, plugin
system, executor inheritance, planner or service registry framework. Start with
plain dictionaries plus two dataclasses, not a generic type ontology. The
vocabulary lives in a small versioned data file; provider data is separate.
Proposed paths are plans, not files created in this step.

| Existing component | V4 treatment | Reason / necessary change |
| --- | --- | --- |
| `model.py`: `Contract`, `Goal`, `Truth`, `Condition`, `Observation`, `OracleVerdict`, `SubstitutionChecker` | Exclude from runtime | They encode the behavioral research obligations being removed |
| `model.py`: `ApiResult`, `instant`, `now` | Copy only the small useful primitives into V4 | Avoid importing the legacy behavioral model; preserve strict timestamps |
| `transport.py`: `HTTPTransport` | Reuse narrow implementation with local result-type import | Already ordinary HTTP, 5 s timeout, explicit loopback origin/no redirects; do not broaden origin policy in initial V4 |
| `transform.py`: `convert`, `map_fields` | Extract only pure conversions/mapping | Current module also imports V3 effects/profile types; omit those dependencies |
| `transform.py`: `validate_profile`, `adapted_request` | Do not reuse | Effects/Goal constraints and synthetic observation routing are out of scope |
| `contract.py`, `json_contract.py`, `provider_contract.py`, contract schemas | Replace with minimal parsers | They construct/validate action contracts, including effects and evidence; no graph round trip for JSON |
| `registry.py`: `Registry` | New finite lookup, not a wrapper/subclass | Existing resolution performs assessment, effects checks, applicability and V3 execution |
| `pipeline.py`, `local_baseline.py` executors | Exclude | Both tie execution to preconditions, observations and runtime verification; A needs simple local adapters too |
| `contracts/providers/{a,b}.json` and `contracts/api_local/{a,b}.json` | Read as migration references only | Write new V4 data after review; do not strip/rewrite preserved originals |
| `artifact.py`, `provider_b.py` | Reuse unchanged in evaluation only | Existing independent A/B services and public fault modes; V4 runtime imports neither |
| `native_verifier.py`, `oracle.py` | Reuse only outside runtime through evaluator wrapper | Direct native snapshots/decoders and checks can validate fixture outcomes; existing Goal/freshness policies remain evaluator details, not V4 runtime requirements |
| `sequence*`, `multistep_*`, sequence descriptions | Omit from initial V4 | Single selected operation per invocation; no predecessor semantics/planning |
| `supervision.py`, `preflight/` | Reuse mechanisms in test harness only | Keep service alive for timeout/reset observation; do not import combined V3 driver unchanged because it invokes V3 subjects |
| `event_ledger.py`, `cost.py` | Optional evaluator-only recorder | Reuse measured fields/null handling; no runtime cost/governance dependency |
| Historical tests, manifests, M4.4/M4.5 evidence | Preserve unchanged | V4 gets separate tests/evidence; V3 suite cannot be rebranded as V4 evidence |
| Tutorial package and original sources | Preserve unchanged | No new tutorial/LLM coupling |

Expected simplification is testable: JSON invocation needs only standard-library
runtime modules; RDF adds one parser library. No V4 runtime imports from
`semantic_action`, no behavioral model fields, no pre/post-state requests and no
oracle call. Existing V3 core also uses RDFLib/jsonschema; V4 drops JSON-to-graph
validation and the jsonschema dependency, rather than introducing another layer.
Actual size/dependency reductions remain to be measured after implementation.

## Short implementation plan — after review only

1. Agree the finite profile, exact-match/ambiguity policy and single-operation
   scope. Keep the old package/data/tests untouched on this development branch.
2. Add the small V4 model/vocabulary and JSON/RDF loaders; differential tests cover
   normalized information and identical rejection of malformed descriptions.
3. Extract narrow HTTP/conversion primitives, add lookup/invocation, and produce
   new A/B descriptions. Add simple API-local adapters with the same technical
   validation/transport budgets, without the old local-contract executor.
4. Wire the external A/B test harness to each condition. Test success, mappings,
   API failures, HTTP success with incorrect storage, side effects and timeouts;
   runtime status never substitutes for independent correctness.
5. Measure actual authoring/onboarding/testing effort prospectively and report
   shared versus provider costs using [the minimal experiment](V4_MINIMAL_EXPERIMENT.md).
   Recheck V3 hashes, then report results for review before expanding scope.

This proposal is ready for architecture review; it does not authorize coding,
new experiments under the frozen V3 protocol, or any Provider C access.
