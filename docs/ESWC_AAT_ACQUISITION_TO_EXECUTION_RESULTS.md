# Acquisition-derived RDF → guarded AAT execution

**Implemented and executed the full controlled-room pipeline:** local OpenAPI →
automatic structural RDF → explicitly authored/reviewed behavioral sidecar →
validated completed graph → explicit graph approval → **unchanged** semantic
controller → independent native-state scoring. Behavioral Usages were **not**
automatically inferred. This remains a same-author controlled fixture experiment,
not independent external-API generalization or independently curated semantics.

Baseline `242c3bc15f9aad76201806ca2098e63bed5fff0f` was pushed first, as requested,
and GitHub branch `codex/v4-prospective-protocol` was verified at that exact SHA.
New implementation: **`972ebddc203ea7dbab51f29c3bcc77e122f151be`**; the experiment
started from that clean local commit. This report/evidence is a later local revision.
No subsequent implementation/results were pushed or merged.

## Exact integration boundary

`experiments/aat/completion.py` is an isolated, bounded adapter for the existing
`room-step/1` profile. It does not import or copy the manually authored executable
`data/room.ttl`. It receives the extractor's source/config, structural RDF, every
assertion's provenance and diagnostics, plus a separate behavioral JSON sidecar.
It re-extracts deterministically from the retained source/config and demands exact
structural/provenance/diagnostic reconciliation before projecting any binding.
Rehashing a forged graph or provenance record cannot pass this reconciliation.

| Information | Source and transformation |
| --- | --- |
| Thing, Artifact, represents | Copy the validated extracted triples with consistent sidecar grounding |
| Two action operation IRIs, hasOperation, Operation type, method/path | Copy **actual extracted** triples, preserving extracted operation IDs. No independent hardcoded binding reconstruction |
| Observation path | Sidecar explicitly chooses extracted GET operation; validate /state, candidate flag and exact supported state schema, then project its extracted path to `aa:observationPath` |
| Media type | Validate actual extracted request/response content and carry its JSON media type |
| RevisionRequest / RoomReply schema IRIs | Reviewed finite-profile interpretation of matching **mapped RDF schema structure**, not rawSchema/source JSON or an assumed operation name |
| Preconditions/effects, subject/unit meaning, readiness and frame | Explicit behavioral sidecar, authored from the pinned native contract; no extraction inference |
| Atomicity / revision and mutation increments | Sidecar assertion checked structurally against the finite profile; source review/native execution still needed to establish truth |
| Goal, evidence age, loop/dispatch budgets, decisions and verification | Existing StateGoal/controller/guard policy, unchanged |

The extractor has **three** operations; the executable profile allows two actions
plus a separate observation path. The GET operation remains in retained structural
RDF and is explicitly projected into the observation binding, rather than admitted
as a third action. OperationId, security declarations, status/schema detail, source
provenance and other structural metadata remain in the input bundle; the closed
executable graph cannot carry those extra assertions. This is an explicit finite
projection, not a universal ontology mapping.

`completion.py::schema` decodes mapped structural assertions, never treats the
`rawSchema` literal as the reference answer. It checks exact supported request,
response and state shapes against fixed profile wire requirements. Additional
constraints, unsupported diagnostics, parameters/authentication, wrong subjects,
unknown/mismatched operations and changed observation fields fail closed. The
existing `rdf.load` still enforces all supported methods/paths, context grounding,
precondition types/bounds/readiness, operator/delta, counters and complete frame.
No loader/profile/controller changes were made to accommodate acquisition.

Each successful completed graph has **66 triples**, like the manual graph:
11 copied structural assertions, one reviewed observer-path projection, six
wire-schema/media interpretations and 48 reviewed Usage/context/frame assertions.
`completion.json` contains 14 mapping records (11 copies + observer projection +
two wire interpretations); retained sidecar supplies the remaining behavioral data.
The sidecar's identity links point to extracted operation IRIs, not display names.

## Reviewed completion and explicit admission

New files:

- `experiments/aat/completion.py`: completion CLI/function and separate admission.
- `experiments/aat/completion_study.py`: small private comparison/evidence driver;
  uses existing fixture, worker, supervisor, scorer and deterministic barriers.
- `experiments/aat/data/room-completion.template.json`: explicit, same-author
  native-source-reviewed behavior. This was manually authored, not generated from
  endpoint names, prose, examples or the old executable graph.
- `tests/aat/test_completion.py`: eight focused tests with multiple rejection probes.

The sidecar version is `room-completion/1`. It pins OpenAPI source and native-spec
hashes, artifact/Thing identities, exact extracted operation references, supported
observation field mapping, wire schema identities, per-Usage pre/postconditions,
frame and review status/reviewer/scope/reference. Unknown/review-pending behavior
is not promoted. The template leaves structural/provenance hashes unbound: the
harness binds only these hashes to each fresh extraction, never inventing behavior.
It verifies the pinned document and actual native-source hashes first.

Each fresh fixture gets a loopback ephemeral origin. Its source configuration,
structural graph and provenance record that **actual** origin. Completion records
and approval bind it; the driver checks the approved origin equals the worker
origin. This avoids silently using the earlier documentation placeholder port8000.
Operation IRIs are pointer-derived and stay stable across these deployment origins.

Completion returns either QUARANTINED or COMPLETED_UNAPPROVED. It saves inputs and
sidecar snapshots, candidate RDF, all hashes, review metadata and mapping decisions.
Calling the unchanged loader with the candidate hash at this stage checks structural
profile validity only; it does not launch a worker or constitute approval.

A separate approval JSON must explicitly have `approved: true`, reviewer/scope,
exact candidate graph hash and completion-manifest hash. `admit` checks these,
all retained input/sidecar hashes, then calls the unchanged loader and returns an
admission record. The manifest transitively binds source/config, structural graph,
provenance, review, sidecar and origin. Altered inputs, false/missing approval,
wrong graph or review hashes reject. The runtime's existing graph-bound single-use
permits and postcondition checks remain authoritative during execution.

**Review authority limitation:** this task authorizes a controlled implementation
experiment. Its driver writes explicit experimental-operator approvals against the
manually reviewed template; it does not assert independent human signatures,
investigator scientific-freeze approval or automatic semantic truth. The separate
CLI accepts an externally supplied approval file. These plain hash-bound records
are an auditable trusted-operator workflow, not cryptographic identity authentication
or protection against a hostile host operator. Standalone completion cannot prove
that a declared native-spec checksum describes a remote deployment; this experiment
checks the actual fixture source and retains it as `raw/native-spec.py`.

## Actual manual-versus-acquired execution

Both representations use `policy='semantic'` and the **same** unmodified worker,
ScriptedReasoner, candidate evaluator, controller, guard, executor and native scorer.
Fresh fixture/server/process per attempt, same21/23/22 initial temperatures, goal22,
six reasoner turns, at most one dispatch, HTTP5s timeout, outer60s supervision and
bounded native settlement. The driver never supplies an expected action/Usage ID.
For intervention it only observes barrier stage/turn, changes native temperature
21→23/revision+1 once, then releases the barrier without reading the proposed handle.
Expected outcomes are checked after execution, outside the worker.

| Scenario | Manual A | Acquired + completed B | Native outcome |
| --- | --- | --- | --- |
| Cold21 | Heat, SUCCESS | Heat, SUCCESS |22, one mutation each |
| Hot23 | Cool, SUCCESS | Cool, SUCCESS |22, one mutation each |
| Intervention after initial Heat proposal | STALE_PROPOSAL; Observe; Cool, SUCCESS | Same | No heat POST; only cool POST;22, one actor mutation + one authorized external revision each |
| Already22 | SUCCESS, no Use | Same |22, zero mutations each |

**Four paired scenarios, eight successes**, including two already-satisfied no-ops; six actual
successful mutations. Normalized native outcomes, physical choices, guard decisions,
request counts and timestamp-free native journals have **zero parity differences**.
Opaque operation/Usage/context IDs, hashes, review references, origins, timestamps
and durations are not treated as behavioral differences. Structural identifiers
really differ: manual op17/op29 vs pointer-hashed extracted operation IRIs. Reviewed
preconditions/deltas/frame have equal operational meaning, verified by tests.
This is a representation/construction comparison with fully shared decision code,
not two independent agent implementations or evidence of semantic superiority.

### Retained negative controls

| Control | Completion/execution result | Native outcome |
| --- | --- | --- |
| Unknown behavior (pending review, missing delta) | QUARANTINED before worker |21, no requests/mutations |
| Reviewed but unsupported +2 effect | Unchanged loader rejects Unsupported transition; QUARANTINED |21, no requests/mutations |
| Deliberately faulty reviewed sidecar: signs reversed, still ±1 | Structurally valid and explicitly approved as a faulty-review test; controller predicts Cool reaches22 from21, actual201 Cool reaches20; POSTCONDITION_FAILED | One API-correct cooling mutation; goal false; no retry or false success |

The third control is intentionally more revealing than an invalid schema: a review
flag and approval hash **cannot establish effect truth**. Actual postcondition/goal
checks detect the false declaration. The native scorer uses actual service rules
and state, not the sidecar delta or runtime prediction; cooling itself is legal and
matches the native API, while the declared effect and desired goal do not hold.
Do not count this undesired cooling mutation as a successful goal outcome or hide
it behind zero authorization violations. It is retained as an explicit negative result.

Totals: **11 diagnostic records**, **9 executed episodes**, two no-execution
quarantine controls, eight accepted satisfactions, seven total actor mutations
(including the faulty-sidecar control), zero false success claims, zero native
applicability/revision breaches. Every diagnostic expectation passed. No unexpected
harness failure or silently rerun attempt occurred. Native scoring is independent
of runtime mappings as a data path, but native implementation, review and evaluation
share authorship; this is not independent human curation or blinded evaluation.

## Evidence, tests and reproducible commands

Retained run: `docs/artifacts/eswc_aat_acquisition_execution/run-001/`.
`raw/` contains original/manual review and graph, per-acquired-episode source/config,
structural graph and every assertion's provenance, sidecar snapshot, completion and
mapping decisions, candidate RDF, explicit approval/admission, fresh reset/native
before/after states and intervention journals, worker inputs, actual observations,
proposals, structured feedback, guards, HTTP traces/results, context RDF, process
logs/module inventories, scorer outcomes, full source hashes and raw seal.
`derived/` holds regenerated JSON/CSV/Markdown rows and summary, separately from raw.
Quarantined candidates retain rejection evidence and never receive worker configs.
`validation/` holds test/command logs and overall integrity checks.

Implemented source snapshot contains **13,311 tracked file hashes**, all unchanged
during execution. Run status completed, episode loop6.635241s; these timings include
extraction, completion, imports, synchronization and fixture shutdown and are not
integration-effort measurements or representation-latency comparisons. Human-active
and supervision costs remain null. Python3.12.14, RDFLib7.6.0, pyparsing3.3.3;
no added dependency, external model call or live external-provider execution.

Full AAT regression command, exit0: **31 tests pass in 9.788s** (previous23 plus eight
completion methods). New coverage includes exact binding/meaning reconciliation,
missing/conflicting/unreviewed effects/frame/subject/schema/observer rejection,
forged structural/provenance input despite rehashing, changed wire schemas, explicit
approval/input immutability, actual feedback-driven reconsideration, no worker for
quarantined graphs and native detection of a plausible false effect. Worker module
inventories confirm no fixture/scorer/completion-driver imports. This is code/data
separation, not a hostile-worker filesystem sandbox.

From repository root with the existing `.venv`:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/aat -v

# Complete comparison, fresh fixtures and new evidence directory.
PYTHONPATH=src .venv/bin/python -m experiments.aat.completion_study run \
  --output /tmp/aat-completion-fresh

# Verify raw hashes and regenerate tables, no execution.
PYTHONPATH=src .venv/bin/python -m experiments.aat.completion_study summarize \
  --output docs/artifacts/eswc_aat_acquisition_execution/run-001
```

Actual run command used `/workspace/aat-completion-run-001`, exit0. The driver
refuses an existing output path and seals partial evidence in `finally`. A hard
process kill can leave unsealed data, which must not be relabeled complete.

For explicit standalone completion/admission, inspect an episode's retained input
bundle and sidecar, then choose a new output directory:

```sh
PYTHONPATH=src .venv/bin/python -m experiments.aat.completion complete \
  --bundle docs/artifacts/eswc_aat_acquisition_execution/run-001/raw/episodes/e002/pipeline/extracted \
  --sidecar docs/artifacts/eswc_aat_acquisition_execution/run-001/raw/episodes/e002/pipeline/sidecar.json \
  --output /tmp/aat-completed-candidate

# After explicit review, supply an approval binding this candidate and completion hash.
PYTHONPATH=src .venv/bin/python -m experiments.aat.completion admit \
  --completed /tmp/aat-completed-candidate --approval /path/to/approval.json
```

The first command cannot execute; unknown/incompatible completion returns exit2.
The second admits only with the stated decision fields/hashes, and does not itself
invoke operations. Reusing a historical approval does not authorize a new deployment.
The experiment driver makes its scoped test approvals explicit and retains them.

## Scope and preservation

Only the new adapter, small experiment driver, sidecar template, focused tests and
new report/evidence were added. The extractor, existing controller/reasoner/matcher,
model, native fixture, RDF loader, ontology/profile, original executable graph,
V3/V4 and tutorial are unchanged. Prior336 sealed AAT raw files, previous validity
seal and all96 retained acquisition files were verified against their original hashes;
new raw seal and table-regeneration checks are recorded in validation evidence.
Packaging check reports nine blank lines at EOF in RDFLib-generated context Turtle;
these raw files are retained byte-for-byte rather than normalized after sealing.

This closes the controlled acquisition-to-execution link. It does **not** close
external generalization, independent semantic curation, automatic behavioral
acquisition, arbitrary OpenAPI compatibility, general planning or LLM reasoning.
A genuinely new API would still need compatible bindings/observations, reviewed
behavior and an independently established native gate. No new profile or proxy
was created to make that appear solved.
