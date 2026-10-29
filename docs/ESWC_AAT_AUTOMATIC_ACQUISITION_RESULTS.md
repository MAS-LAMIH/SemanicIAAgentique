# Automatic OpenAPI → AAT structural acquisition

Implemented and executed a bounded offline extractor. **Two documents, six operations,
144/144 scoped reference facts matched, complete provenance for 410 RDF assertions,
byte-identical reruns, zero inferred Usages.** Both graphs remain quarantined and
are rejected by the unchanged `room-step/1` loader even with a matching test hash.
This is automatic documentation structure acquisition, not automatic behavioral
understanding, executable artifact admission or external native-state generalization.

Baseline: `b04902ad198dc2f7bf03cc7fb0b027b65718712e`.
Initial implementation: `5248bf2de0300d14a1947d1fc02047b05f131cae`.
Corrected implementation: **`5883d4b1fee432af0fa31972d4ea69215b3efa10`**,
extractor version `openapi-structure/1.1`, clean tree at corrected evaluation start.
This report/evidence revision adds no runtime changes. V3/V4, original AAT runtime,
closed RDF profile, tutorial and prior evidence remain unchanged.

## Implementation and executable boundary

- `experiments/aat/acquisition.py`: offline function `acquire(source, config, output)`
  and CLI. No HTTP client, remote reference loading, model API, code evaluation or
  provider execution. Explicit configuration is exactly artifact/thing/origin;
  identities are distinct absolute IRIs, public origin has no embedded credentials.
- `experiments/aat/acquisition_evaluation.py`: two pinned documents, locked reference
  comparison from RDF, deterministic repeated extraction, admission probe, sealing
  and JSON/CSV/Markdown exports. This is a document evaluation, not orchestration.
- `tests/aat/test_acquisition.py`: ten focused test methods with multiple controls.
- `experiments/aat/data/acquisition/`: original public YAML, converted JSON, room
  JSON, configurations, manually specified references, pre-extraction lock and pins.

No new runtime dependency. RDFLib is already installed. PyYAML 6.0.3 was used once
for the disclosed YAML→JSON input preparation, not imported by either new module.
No optional behavioral sidecar merge is implemented. Extracted structure is not
converted into `Catalog` or `Usage`; reviewed behavior would require a separate
reviewed complete graph, unchanged loader and explicit external hash approval.

### Finite supported subset

Accept local JSON OpenAPI **3.0.x / 3.1.x** with info title/version, nonempty paths,
standard HTTP methods, operation responses/status bindings and optional unique
operationId. Parse duplicate JSON keys/nonfinite numbers as errors. Local references
use strict `#/…` JSON Pointer decoding (`~0`, `~1`) and dictionary/array traversal;
missing targets, remote references and cycles in traversed schemas fail closed.
Reference siblings are not merged: diagnostic and opaque/empty structure only.
Unreferenced schema semantics are not exhaustively compiled; original source is retained.
This is explicit subset validation, **not full OpenAPI/JSON Schema conformance validation**.

Bounds: source/config JSON ≤1 MiB, JSON depth32/nodes20,000, reference chains16,
schema expansion depth32/nodes20,000 and ≤20,000 unique emitted assertions.
Oversize source is rejected before copying; its invalid diagnostics explicitly say
no original copy/hash was produced. Output directories must not already exist.
Structural-invalid cases retain original input (within bound) and INVALID diagnostics;
partial graphs are not made executable.

Schema subset: scalar object/array/integer/number/string/boolean types, properties,
items, required, enum, numeric/length/item bounds, pattern/format annotations,
boolean additionalProperties and nullable/readOnly/writeOnly constraints. Preserve
raw schema JSON plus typed mapped assertions; no validator or reasoning engine is
inferred from these annotations. Schema-valued additionalProperties, type unions,
composition/conditionals/custom keywords and boolean schemas are not interpreted;
unknowns are diagnosed or structurally rejected, never coerced into supported behavior.
A blocked composite remains opaque instead of flattening one branch into truth.
OpenAPI3.0 boolean exclusive bounds/nullable are distinguished from 3.1 numeric
exclusive bounds; 3.1 nullable is unsupported, and type unions remain unsupported.
Formats are explicitly UNKNOWN annotations, not automatic date/integer validators.

Parameters: inherited/local name/location/required/schema, location-specific default
style/explode. Duplicate bindings and missing path parameters are invalid. Overrides
are retained as both declarations with an unsupported effective-merge diagnostic.
Nondefault serialization/content/allowReserved is diagnosed, not executed. Request
body required/media/schema and response status/media/schema are represented. Headers
are preserved as declaration JSON with unsupported runtime-mapping diagnostics.
Security declarations and per-operation effective requirements (including default
empty security) are retained; **all authentication execution is unsupported**. No
credentials are requested. Server declarations do not override explicit origin and
are UNKNOWN deployment compatibility. GET is only an **observation candidate**, not
a confirmed observable-state mapping or a guarantee that GET is side-effect-free.

### RDF and assertion provenance

Keep `urn:eswc:aat:prototype:1#` Thing / Artifact / represents / hasOperation /
Operation / method / path. Additional structural terms use the separate versioned
namespace **`urn:eswc:aat:structure:1#`**:

| Structural terms | Meaning |
| --- | --- |
| origin, openapiVersion, documentedServers | Configured origin and documented metadata; not execution authorization |
| operationId, observationCandidate | API ID and GET heuristic |
| parameter, name, location, required, serialization | Request parameter structure |
| requestBody, response, statusCode, content, mediaType, headers | Request/response bindings and declarations |
| Schema, schema, schemaType, rawSchema, property, items, referenceTarget | Reachable schema structure and local-reference provenance |
| required/enum/minimum/maximum/exclusiveMinimum/exclusiveMaximum/minLength/maxLength/minItems/maxItems/pattern/format/additionalProperties/nullable/readOnly/writeOnly | Exactly documented machine-readable constraints/annotations, no behavioral entailment |
| securityScheme, declaration, securityRequirements | Authentication declaration only |

Stable generated IRIs hash artifact identity plus source pointer; no blank nodes.
`structural.ttl` is sorted N-Triples syntax (valid Turtle), preserving literal types.
`provenance.json` stores every unique triple, its SHA-256 assertion ID and one or
more source records: source document hash, exact pointer/configuration source,
configuration hash for configured assertions, extraction rule, evidence class,
extractor version and transformation/default explanation. STRUCTURE, CONSTRAINT
and CONFIGURATION are distinct evidence classes. No source name/example/description
can create readiness, effect, revision guarantee, frame, reviewed status or Usage.
No run timestamp is put in deterministic assertions; runtime durations and environment
are separate raw metadata. Reordered keys preserve graph/assertion IDs, while the
changed original byte hash correctly changes source/provenance hashes.

## Inputs and reference construction

**Room:** no existing OpenAPI file. Authored a normal-mode wire description directly
from unchanged `experiments/aat/native.py` at baseline, SHA-256
`e657700f20b08a2d775ecf140fae839416f2fff351a2d5dfd90c0336e666f82d`.
GET/state includes native counters/readiness/sentinels/thing/timestamp. POST heat/cool
accept exact integer expected_revision and document native reply/status structures.
Fault-injection unknown/stale/wrong/frame/timeout modes are not claimed to conform
to this normal-mode response schema. No preconditions/effects were imported into it.
Room JSON SHA: `417118f60c367f670e35b5ae15a7c8f3740d9d6b4f0e51300b9a39715c1b5db0`.

**Petstore:** OpenAPI Initiative reference example, not an independently executed API.
Repository <https://github.com/OAI/OpenAPI-Specification>, tag3.0.3, commit
`c8e90dfa4ccf8054db1539f7a104c5ccfb1913c3`, `examples/v3.0/petstore.yaml`.
Original SHA: `ab60f59da478d4ac312cd9fabcc6cbd06f8f975ab8a1a0c2029b2a41f65fedd5`.
JSON SHA: `a8567818aee3543cb3c9ab4ba5a215e5c505d200166345d789e2b95a472f9d14`.
It has pet collections, list/create/detail operations, a path parameter, query limit,
array/item schemas, shared local refs, error responses and a pagination header.
The POST example documents **no request body**; extractor/reference preserve that
absence rather than inventing a Pet creation schema. Original declares MIT license.
Only this one external document/repository was selected; no broad provider search.
An initial guessed JSON URL returned404; repository tree identified the YAML source.
Original YAML trailing whitespace is deliberately retained to preserve its checksum.

References and their hashes were locked **before first extractor execution** in
`reference-lock.json`. Same author manually specified the wire-level operation,
parameter, request/response and reachable schema expectations from native source /
pinned YAML. Room input and reference share author and schema definitions: this is
**not independent curation or blinding**. No second reviewer participated. Extractor
output did not generate the reference. The evaluator decodes mapped RDF, not
`rawSchema` literals/source JSON, into scoped normalized facts. A negative test
removes mapped type assertions and checks reference recall detects the omissions.

## Actual evaluations and disclosed correction

`docs/artifacts/eswc_aat_acquisition/run-001/` retains the original `/1` evaluation
byte-for-byte. All reference comparisons passed, but inspection found an overbroad
vendor-extension detector treating ordinary header **x-next** as an extension.
Its seven Petstore diagnostics therefore include one false classification. Preserve
this result as a diagnostic defect, not an unqualified clean result.

`run-002/` is a separate **`/1.1`** corrected evaluation after the small classification
fix, an explicit response-binding provenance correction and regression test. Root
vendor extensions remain diagnosed; response header names are not interpreted as
extension fields. No reference edits or runtime/profile changes were needed.
Both runs started from their recorded clean source commits; no case was silently
replaced and the first run was not overwritten. Corrected results:

| Document | Operations | Reference facts / matched | Scoped precision / recall | RDF assertions / provenance | Unsupported / UNKNOWN | Runtime admission |
| --- | --- | --- | --- | --- | --- | --- |
| Room3.1.0 | 3 | 86 / 86 | 1.0 / 1.0 | 268 / 268 | 0 / 1 | Rejected, quarantined |
| Petstore3.0.0 | 3 | 58 / 58 | 1.0 / 1.0 | 142 / 142 | 1 / 5 | Rejected, quarantined |

Denominator is **144 selected normalized structural facts**, not all source prose,
all OpenAPI features or all410 RDF assertions. It covers operation/path/method/ID,
parameter name/location/required, body required/media, status/media and supported
reachable schema properties/types/constraints/items. Server/header/security metadata,
configured identities, generated graph links and descriptions are excluded from
precision/recall; their retention/provenance and unsupported reporting are separate.
Thus 100% supported-reference coverage does **not** mean 100% OpenAPI support or
behavioral completeness. No required Usage behaviors have been acquired/approved.

For each document, original source/config + RDF/provenance/diagnostics matched
byte-for-byte on two identical executions. Both admission probes passed the graph's
actual hash to the unchanged loader and were rejected structurally; a matching test
hash was not represented as approval. Every assertion has source/rule/class/version/
transformation and a verified stable ID. Room UNKNOWN is missing behavior. Petstore
UNKNOWNs are behavior, three format annotations and deployment binding; unsupported
header mapping is explicitly retained. No Usages in either graph; no API calls.

Corrected evaluation automated wall time **0.053437s** (room0.033456s,
Petstore0.019807s), including repeated extraction, parsing/reference comparison and
admission probe. These are document-processing measurements, not an API latency
benchmark or engineering effort. Human-active/supervision measurements remain null.

## Tests, evidence and reproduction

Final suite: **23 AAT tests pass**, including the original13 and ten acquisition tests.
Controls cover malformed/duplicate JSON, versions, empty/missing/ambiguous bindings,
conflicting IDs, remote/missing/cyclic refs, escaped local pointers, byte/depth limits,
unsupported composition/auth/serialization, unreviewed effect extensions, strict
structural-only admission rejection, dialect differences, no-overwrite behavior,
key-order invariance, header classification and missing-assertion detection.
Earlier passing development logs are retained; final log gives actual test duration.
No experiment executes the public Petstore service. Existing AAT tests do exercise
the controlled room guard/HTTP loop as regressions, not new generalization evidence.

From repository root, with existing `.venv`:

```sh
# One offline extraction, always quarantined; choose a fresh output directory.
PYTHONPATH=src .venv/bin/python -m experiments.aat.acquisition \
  --source experiments/aat/data/acquisition/petstore.json \
  --config experiments/aat/data/acquisition/petstore.config.json \
  --output /tmp/aat-petstore-fresh

# Complete two-document evaluation, references, double extraction and sealing.
PYTHONPATH=src .venv/bin/python -m experiments.aat.acquisition_evaluation run \
  --output /tmp/aat-acquisition-fresh

# Verify sealed evidence and regenerate tables only (no extraction or API calls).
PYTHONPATH=src .venv/bin/python -m experiments.aat.acquisition_evaluation summarize \
  --output docs/artifacts/eswc_aat_acquisition/run-002

PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/aat -v
```

Executed evaluation output paths were `/workspace/aat-acquisition-run-001` and
`/workspace/aat-acquisition-run-002`; both exit0. A zero extraction/evaluation exit
means the structural/quarantine checks completed, **not executable admission**.
INVALID extraction returns CLI exit2. Existing output paths are refused.
Public YAML→JSON conversion, if needed, is `yaml.safe_load` then sorted `json.dump`;
pinned JSON is already included so running acquisition needs no YAML package.

Each retained run has raw source/config copies, RDF, every assertion's provenance,
diagnostics, both reruns, expected/actual comparisons, rejection reasons, references,
source/dependency hashes, raw seal and separate derived JSON/CSV/Markdown tables.
`validation/` retains test/evaluation logs and overall verification. Corrected tables
can be regenerated exactly after checking raw hashes. Prior 336 sealed AAT files
and previous validity evidence are verified unchanged; no historical result is relabeled.

## Remaining limits

No universal converter, arbitrary ontology reasoning, behavioral learner, full JSON
Schema validator, authentication execution, sidecar approval workflow or automatic
operation-to-Usage inference. Discovery is quarantined structural inspection, not
runtime candidate admission. A documented bound on an output is not an expected
effect, a required expected_revision field is not an atomicity guarantee, and GET is
not verified observation. All such claims need source-specific native review.

The external case is **independently authored documentation**, not native execution
or independently curated evaluation. Two small chosen documents with shared-author
references cannot establish broad extraction accuracy; exotic schemas/real deployment
requirements remain unsupported. Structural precision/recall is conditional on the
explicit finite reference projection. New artifact goal-directed generalization is
still pending a compatible independent API and locked native evaluator; neither
shared runtime nor closed profile was weakened to manufacture compatibility.
