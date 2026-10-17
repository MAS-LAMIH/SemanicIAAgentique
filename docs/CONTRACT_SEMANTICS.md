# Supported contract semantics

The project namespace `https://example.org/sam/v1#` is a proposed, versioned
example vocabulary, not a standard or a deployed namespace. The vocabulary uses
RDF/RDFS classes and properties and Dublin Core metadata. It is separate from
`contracts/calendar.ttl`, the provider-specific artifact description.

## Finite profile a = (I, P, T, B, O)

I: exactly start_time, end_time, title. Times must be timezone-aware ISO 8601
instants and end > start. Title is a nonblank string, at most 500 characters.
Unknown input fields are rejected. No implicit unit or timezone conversion is
inferred; instant comparison handles equivalent offsets. The API mapping is an
explicit identity mapping of these three JSON keys.

P: PositiveInterval (also enforced as input validity) and CalendarWritable.
A missing critical precondition declaration invalidates the manual. For state
evidence: boolean true plus current timestamp establishes TRUE; boolean false
plus current timestamp establishes FALSE; null, absent, stale, future-dated,
unavailable, or malformed evidence establishes UNKNOWN. Any FALSE rejects;
otherwise any UNKNOWN blocks; only all TRUE permits POST. Missing RDF statements
never establish truth. Invalid inputs reject before state observation, so their
traces have no state precondition verdicts and applicability FALSE.

T: NewMatchingEvent denotes S' = S union {fresh id → requested start, end, title}.
This is a modeled transition, not a deduction about what the API did. A separate
formal JSON goal requires existence of the new event with those properties and,
by default, equality of all other calendar contents. The goal is not inferred
from inputs or declared effects.

B: POST /events, supplied loopback origin, JSON body with identity mapping.
O: GET /events/{id} plus a full GET /events snapshot, current timestamps and
consistent revision. The manual supplies maxEvidenceAgeSeconds in (0, 300].
The oracle independently imposes the goal's evidence age bound; both bounds
must hold. Snapshots must postdate the execution start, show revision progress,
and agree about the event. The pre-execution baseline must still be current at
verification time.

## Supported RDF assertions

Artifact hasOperation Operation; Operation providesCapability Capability and
hasContract Contract; Contract requiredInput literals, hasPrecondition,
hasExpectedEffect, hasBinding, requiresObservation; binding method/path;
observation path/maxEvidenceAgeSeconds; explicit rdf:type declarations. Only the
shipped finite profile is supported, with arbitrary artifact/operation/capability
IRIs. Unknown predicates, extra assertions, unsupported bindings/effects, missing
fields, and contradictory cardinality fail closed. `hasEvidence` is reserved in
the vocabulary; evidence is recorded in JSON, not loaded as an executable RDF
constraint. No RDFS/OWL entailment, SPARQL, remote contexts, or arbitrary code.

## Guarantees and assumptions

The verifier establishes achievement only relative to trusted fixture snapshots,
not to declared effects or HTTP status. Evidence is not cryptographically signed.
The single-writer fixture, same-machine clocks, and complete snapshot assumption
make the before/after comparison meaningful. This is not a distributed transaction
or production authorization system; concurrent changes and time-of-check races
require future protocols. Forbidden side effects are scoped to other calendar
contents, not every possible external effect. No compensation, retry planner,
full ontology reasoner, natural-language interpretation, or provider substitution.
These reversible engineering assumptions do not alter the frozen research scope.

## JSON contract profile v1

The authoritative JSON Schema is
`src/semantic_action/schemas/contract-v1.schema.json` (Draft 2020-12), with stable
example identifier `https://example.org/sam/json/contract-v1.schema.json`.
`contracts/calendar.json` is information-equivalent to `contracts/calendar.ttl`.
No URL dereferencing, JSON-LD contexts, implicit defaults, or remote schema loads
are used. Identifiers must be absolute IRI strings without whitespace or forbidden
IRI delimiters; JSON never resolves relative IDs against a working directory.
Turtle relative IRIs are resolved by its parser before reaching the shared model.
All properties are required; extra properties at every object level
reject. Object member order is irrelevant. Repeated object keys reject even
when values agree. Arrays express sets, reject duplicates, and are canonicalized
to the same sorted tuples as RDF. Non-finite JSON numbers reject. Evidence age
must be a JSON number in (0, 300], never a boolean, null, or numeric string.

| JSON field | RDF meaning | Canonical Contract field |
| --- | --- | --- |
| schema_version = 1 | Selects the supported SAM v1 finite profile | No new model field |
| artifact_id | Named Artifact subject | artifact_id |
| operation_id | hasOperation, type Operation | operation_id |
| capability_id | providesCapability, type Capability | capability_id |
| inputs | requiredInput literals | inputs |
| preconditions | hasPrecondition, explicit Precondition types | preconditions |
| declared_effects | hasExpectedEffect, explicit Effect type | declared_effects |
| binding.method / binding.path | hasBinding node's method / path | method / path |
| observation.path | requiresObservation node's path | observation_path |
| observation.max_evidence_age_seconds | maxEvidenceAgeSeconds | max_evidence_age_seconds |

The version fixes precisely the same required input names, timezone and title
rules, identity API mapping, positive interval and writability preconditions,
NewMatchingEvent modeled transition, POST /events binding, read-back plus full
snapshot observation, and numeric freshness semantics. Validation, evaluation,
execution, observation, and verification run through the same functions. The
formal Goal remains separate and is never derived from a representation's effects.
The contract age and independent goal age remain separate constraints; neither
format may loosen the other.

RDF structural Contract/binding/Observation resource labels, prefix choices,
triple order, redundant identical triples, and numeric literal spellings are not
fields of the Milestone 1 Contract model. JSON omits those labels and implicitly
supplies the fixed type assertions. This does not preserve arbitrary RDF graph
syntax or provenance; it preserves every value that the supported execution
model retains. Unsupported extra RDF assertions still reject, just as unknown
JSON fields do. Malformed documents have no accepted semantic model: parser
error text may differ, but both must block before any API mutation. JSON schema
validation alone is necessary, not sufficient: the shared profile validator also
rejects conflicting resource identities, as it does for RDF.

Differential tests use independent, deep-copied fixture states and a fixed clock.
They remove only run metadata, contract hashes, and known observation-wrapper
timestamps from comparisons. Evidence payloads, state, validation results,
precondition verdicts/reasons, HTTP status/body, effects, decisions, and oracle
results are retained. Boundary tests explicitly verify freshness at the age limit,
past it, and for future evidence. Only parser-specific rejection diagnostics are
categorized as contract_rejected when comparing invalid documents. No semantic
failure is normalized into success or skipped.

## Provider profile v2 (Milestone 3)

V1 remains unchanged. V2 adds optional ProviderProfile to the typed model, with
one JSON Schema (schemas/contract-v2.schema.json) shared by both loaders. JSON
schema_version=2 corresponds to an RDF sam-v2:ProviderContract root with explicit
schema_version 2. JSON top-level members map to same-named predicates in
https://example.org/sam/v2#. Nested fixed records map to nodes; mapping dictionaries
use entry nodes, literal key targets, and value records containing source and
transform. Inputs/preconditions/effects are repeated set predicates. Artifact,
operation and capability identifiers and precondition/effect values are IRIs;
wire field names including response_id are literals. An absent duration bound
is represented explicitly as JSON null / sam-v2:Null. Null is never truth of a
critical precondition. Unknown RDF assertions, ambiguous cardinality, duplicate
mapping targets, cycles, missing fields, unknown JSON members and non-finite
bounds reject. RDF numeric values use integer or finite double literals; profile
text uses plain strings. No remote schema, context or ontology inference is used.

The three semantic IDs, exact input set, two preconditions, effect set, and
observation age have the same values in both frontends. Constraints and binding
records are also exactly equal, including every mapping target/source/transform,
path, response ID field, snapshot key and evidence key. The profile supports
EventCreation with NewMatchingEvent; ReservationRecorded exists as an explicitly
non-equivalent negative-control effect and cannot satisfy an event goal.

Known compatibility constraints are time_grid_seconds (0 disables grid),
max_duration_seconds (null means no declared upper bound), and a boolean
guarantee of preserves_other_events. These are not opaque uninterpreted text.
Both times must align to a UTC epoch-based grid and duration must respect the
bound. If a goal forbids changes to other events, a false preservation guarantee
rejects selection/execution. A true guarantee is only a declaration: actual
other events must still pass the independent oracle. All required canonical
inputs must have transformable sources; the execution adapter has no permissive
fallback or arbitrary expression evaluator. Epoch conversion uses integer
arithmetic and rejects submillisecond loss. Stored timestamps are compared as
instants by the unchanged oracle.

Resolution compatibility is separate from state applicability. A compatible
operation can still be FALSE or UNKNOWN after a current writability probe and
must not execute. Execution obtains fresh evidence again. Resolution traces
record these separately, with reasons. No operation-name equivalence is inferred.
The registry's inputs are local manifests and explicitly configured origins;
there is no open-world network crawling or implicit provider substitution.
