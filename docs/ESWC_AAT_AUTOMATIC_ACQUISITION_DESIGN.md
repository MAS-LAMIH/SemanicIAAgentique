# Minimal OpenAPI → AAT acquisition design (not implemented)

Design baseline: `e9fc92c`, with the accompanying finite-profile validity audit.
No universal converter, new runtime profile, provider integration or external-model
service is implemented here. Target namespace is `urn:eswc:aat:prototype:1#`;
current executable profile is **room-step/1**, not a generic API ontology.

## One bounded pipeline

Input: a pinned local OpenAPI 3.0.x or 3.1.x JSON document, explicit artifact/Thing
identity and origin, plus a separately reviewed behavioral sidecar. First reject
unsupported OpenAPI versions. Resolve local JSON Pointer references with cycle/
size/depth limits; do not fetch remote references or execute examples. Preserve
3.0 nullable/exclusive-bound semantics separately from 3.1 JSON Schema semantics;
unsupported composition/dialects stay UNKNOWN, never silently flattened.

Output in four small files: immutable original document, structural candidate RDF,
assertion-provenance JSON, and admission report. A reviewed executable graph is a
separate output; structural output is quarantined and cannot enter candidate queries.
Use existing RDFLib for graphs and explicit subset checks; no ontology reasoner or
LLM is required. A future implementation should be a small offline function/CLI,
not a registry service or workflow framework.

| Evidence class | Examples | Treatment |
| --- | --- | --- |
| Direct API structure | Path, method, operationId if present, request media/schema, response status/media/schema, parameter location, security declarations | Extract exactly; operationId is not a Usage meaning; server variables/credentials need deployment configuration |
| Explicit machine-readable constraints | Required fields, primitive types, enum, integer bounds, supported format/pattern; explicit conditional revision/header requirements | Retain exact schema scope and dialect; required request field is not evidence of a state transition or atomic revision enforcement |
| Behavioral assertions requiring review | Grounded Thing, observation mapping, temperature unit, readiness meaning, operation delta, revision/mutation effects, frame preservation | Must be independently reviewed against native specification/implementation and tested; descriptions/examples/extensions are claims, not verified effects |
| Unknown/unsupported | Missing effect/frame, ambiguous units, unsupported media/auth/schema/protocol, undocumented side effects, non-temperature actions | Record reason/evidence and abstain; do not fill defaults or infer heat/cool behavior from names |

Even an explicit vendor extension specifying `delta: 1` is a documented claim that
needs behavior review. An OpenAPI response schema with temperature bounds does not
establish +1, goal contribution or preservation. A path named `/heat` is only a path.
The current loader requires exactly /state and /heat,/cool, fixed wire schemas,
Celsius integers, named subject and two reviewed Usages. Generic API structure may
therefore be extracted correctly yet remain inadmissible. Do not hide that mismatch
with a translation proxy or label it successful runtime generalization.

## Assertion-level provenance

For every generated triple, store a stable triple identifier (hash of normalized
subject/predicate/object terms), original document byte SHA-256, local JSON Pointer,
extractor version/source revision, rule ID, evidence class, extraction timestamp and
transformation details. One triple may cite multiple sources. Generated resource IDs
use deterministic source/pointer hashes; they convey no behavioral confidence.
Deployment-assigned Thing IDs and origin cite their configuration artifact/hash.

Reviewed assertions additionally cite sidecar/review record SHA, exact native source
version/section, reviewer identity/date and decision; pending values remain null.
Conflict/UNKNOWN entries cite the relevant pointer and explicit omission reason.
Keep provenance outside the executable RDF graph because `rdf.load` rejects extra
assertions. Bind the provenance file and candidate graph in the admission record.
Never treat a self-authored `reviewed true` or a matching hash as independent review.

## Admission contract

1. Validate structural subset and all references; save every unsupported feature.
2. Separate candidate structure from behavior; no executable Usage from structure alone.
3. Curator reviews complete preconditions, effect operator/property/unit, grounding,
   frame, observation evidence and concurrency guarantees against native truth.
4. Run native-only create/change/rejection/frame checks with expectations locked
   independently of the generated graph; a schema check cannot replace them.
5. Require exact compatibility with the existing executor/observer/profile; otherwise
   reject with UNSUPPORTED_PROFILE, without modifying runtime to force admission.
6. Only an explicit external approval of the complete graph's byte hash permits
   `rdf.load`. Bind document/provenance/review/native checks/source revisions to it.
   An unsupported or incomplete graph remains quarantined. Changed source/binding/
   graph invalidates that admission and outstanding permits; re-review is required.

## Independent reference comparison

Before seeing generated output, a curator creates a reference from the pinned API
and native behavior, with a second reviewer resolving disagreements. Record overlap
of authors/exposure honestly; if independent curation is unavailable, label it
same-author validation. Reference authors must not copy generated graphs.

Match operation by documented path/method and grounded role, not generated opaque
IDs. Compare normalized grounded assertions and explicit UNKNOWNs, not byte order.
Keep reference and generated graphs/seals separately. Report structural precision,
recall and unsupported-feature counts with explicit denominators, plus per-Usage
exact correctness/completeness for preconditions, effects, frame and observation.
Do not exclude missing behaviors from the denominator or count structurally valid
but false effects as correct. Report provenance coverage separately. Mutation probes
(unknown predicate/operator/subject/frame) must reject; semantic changes must not be
made equivalent merely by renaming resources. Keep pre-review and post-review results
and actual edit counts; reviewed completion is not fully automatic acquisition.
