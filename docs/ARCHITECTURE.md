# Semantic action architecture (Milestones 1–3)

This module is a deterministic semantic execution foundation. It does not use an
LLM or import the tutorial's agents. JSON and RDF frontends now share the same
finite semantic profile. This is a representation-parity check, not an empirical
comparison of integration effort or a claim of serialization superiority.

## Components and interfaces

- `model.py`: immutable Goal, Contract, Validation, Condition, ApiResult,
  Observation, OracleVerdict, and a future SubstitutionChecker protocol.
- `contract.py`: suffix-based JSON/Turtle dispatch, local Turtle parsing, shared
  graph-profile validation, canonical typed Contract construction, and JSON Goal
  loading. Unknown suffixes reject; parse errors never trigger format fallback.
- `json_contract.py`: strict JSON parsing, validation against the packaged
  Draft 2020-12 contract-v1 schema, then construction of the finite assertion graph
  consumed by that same profile validator. This adapter reuses validation, not
  execution. It never imports a provider client or oracle. The schema has no
  remote references and validation does not fetch its example $id URL.
- `pipeline.py`: input validation → three-valued evaluation → controlled HTTP
  request → observation → independent verification → JSON trace. `Executor.run`
  is the only public mutating entry point; it always loads and validates the
  contract before POST. `observe` is read-only.
- `artifact.py`: loopback-only REST fixture, independent of the manual. GET
  /calendar supplies writability and baseline state; POST /events creates an
  event; GET /events/{id} and GET /events supply read-back evidence. Each test
  gets a fresh service and state. Scenario controls are Python fixture settings,
  not semantic engine repair rules.
- `oracle.py`: checks the Goal against before/after snapshots and event read-back;
  it never consumes declared effects or the RDF graph.
- `cost.py`: append-only structured work records, with nullable unknown effort.

The executable binding is limited to POST /events at an explicitly supplied
127.0.0.1 origin. Contracts cannot supply arbitrary code, hosts, paths, or HTTP
methods. Redirects are disabled. This is a software API boundary, not a security
sandbox against Python callers accessing private methods or directly using HTTP.

## Evidence and execution

A current writability observation is required before mutation. The fixture also
checks writability on POST. The pipeline records applicability, call success,
state change, and oracle verdict independently. After an HTTP error it still
observes the state; missing returned identifiers prevent positive verification.
The oracle checks a newly created identifier, matching properties, revision
progress, consistent read-back, fresh post-execution evidence, and optionally
unchanged other events. A 201 without storage fails verification.

## Future tutorial integration

A future tutorial tool can accept a formal Goal and input mapping, call
Executor.run, and return the structured trace. The LLM must not bypass validation
or turn UNKNOWN into TRUE. Keep language interpretation and planning outside
this module. Substitution remains an interface only; it must account for
applicability, goal effects, types, constraints, and evidence. Names alone do
not establish equivalence. Provider C remains held out after generic machinery
is frozen; this fixture introduces no additional providers or benchmark answers.

## JSON/RDF parity boundary

Both frontends return the unchanged Contract dataclass. The pipeline, REST
artifact, observer, input validator, precondition evaluator, trace recorder, and
independent oracle are unchanged in Milestone 2. JSON uses the standard library
parser and jsonschema (MIT); RDFLib remains shared infrastructure. Schema JSON
is packaged with the wheel via importlib.resources, so installed execution does
not depend on a schema file relative to the caller's working directory.

The adapter deliberately uses the same assertion validator to avoid a second
implementation of semantic constraints. This is not a measurement of parsing or
execution speed: the JSON adapter constructs an internal graph and makes no
performance claim. Information equivalence means equality of all supported
Contract fields and normalized semantic outcomes, not byte-for-byte RDF graph
round-tripping. See CONTRACT_SEMANTICS.md for the exact mapping and exclusions.
The schema version selects a fixed profile; neither frontend accepts arbitrary
new capabilities merely because identifiers look similar.

## Milestone 3: explicit multi-provider capability reuse

See MILESTONE_3_DESIGN.md for the audit recorded before core changes. Contract now
has an optional ProviderProfile. The legacy v1 path is retained. V2 loaders in
provider_contract.py share a schema/semantic validator and build identical typed
profiles; RDF structure uses v2 property IRIs, explicit mapping entries and typed
literals. It does not hide a JSON document in an RDF literal. Additional or
unreachable RDF assertions and ambiguous/missing mapping keys reject.

transform.py defines a closed transformation language, known constraint checking,
and a transport adapter over the existing canonical calendar interface. The
existing pipeline keeps its stages; it adds v2 profile validation, raw wire
capture and a read-only assess method. ApiResult has optional raw_body. The
independent oracle is unchanged. registry.py implements local registrations,
exact capability/effect compatibility, read-only applicability probes, explicit
selection, and revalidation through Executor.run. No provider names appear in
the generic resolver or transform engine.

provider_b.py is a separate appointment REST fixture with its own wire/storage
model and constraints. Provider-local descriptions live in contracts/providers/;
shared meanings live in contracts/shared-capabilities.ttl. reuse_demo.py is
explicit evaluation wiring that starts both fixtures, not generic provider
knowledge. No Provider C appears in the generic machinery. The new registry
resolves candidates for one action; it is not a multi-step planner or general
substitution proof system. See MILESTONE_3.md for cost/provenance qualifications.
