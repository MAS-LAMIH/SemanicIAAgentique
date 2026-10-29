# AAT finite-profile validity audit

Baseline: `e9fc92ce3adf4354c23b51651389304a983cd931` (results), runtime
`7d0126113dcb00b72391fcdf87668ebfad1d8e99`. This audit is a later, isolated
correction/test revision. Historical `docs/artifacts/eswc_aat/run-001` is unchanged;
its 22 diagnostic passes remain evidence for its recorded implementation, not for
this correction. No frozen V3/V4 or tutorial code is modified.

## Validated data and runtime interpretation

The admission boundary is `experiments/aat/rdf.py::load`, not arbitrary construction
of Python records. `model.py` records are immutable, but are not a second RDF
validator; direct Python Catalog/Usage construction is trusted internal code.
`load` checks the complete graph against the consumed triple set, then checks an
externally supplied approved byte hash. A hash and `reviewed true` alone do not
establish behavioral correctness or independent review.

| Runtime input / obligation | Admission check in `rdf.py::load` | Consumer in `runtime.py` |
| --- | --- | --- |
| Usage ID, artifact, operation | Named typed resources, unique fields, artifact scope, known operation; two distinct operation-linked Usages | `definitions`, `candidates`, `authorize`, `execute` |
| Pre/post context references and subject | Named ContextTemplates, both subjects equal sole grounded Thing `urn:example:room:thing` | Grounding compiled into catalog; `candidates` checks observation subject against Goal; verification checks final subject |
| Profile, reviewed, review reference | Exactly `room-step/1`, boolean true, one string review reference; graph hash match | Admission metadata, not dynamically inferred behavior; provenance, not proof |
| Readiness predicate | Only `aa:heaterReady` or `aa:coolerReady` | `candidates` reads corresponding actual observed boolean; missing value is UNKNOWN |
| Minimum/maximum | Typed integers, 18 ≤ minimum ≤ maximum ≤ 26 | Inclusive applicability bounds |
| Current revision requirement | Exactly boolean true | `authorize` reobserves; revision-bound single-use permit; expected_revision body; fixture atomically rejects mismatch |
| Effect property/operator/delta | Exactly temperatureC/addInteger, typed delta ±1 | Compiled delta predicts goal relevance and checks actual after temperature |
| Revision/mutation increments | Both typed integer 1 | `execute` checks both actual counters +1 |
| Frame | Exactly the three URI objects heaterReady, coolerReady, sentinels; no missing/additional objects | `execute` compares all three observed before/after values |
| Binding | Two distinct POST paths /heat and /cool; fixed JSON media and RevisionRequest/RoomReply schema IRIs; /state observation | Guarded HTTP request and fixed response/state checks |
| Anything else | Missing/multiple values, unknown predicates, disconnected triples, wrong resource/literal kinds rejected | Never executable after failed admission |

Operator, subject, revision policy and frame are compiled constants of the closed
profile rather than arbitrary runtime interpreters. This is legitimate only because
the loader rejects every alternative. There is no support for arbitrary predicates,
operators, frames, units, subjects, wire schemas or additional operations. The
finite profile accepts reviewed readiness/delta/bounds combinations without proving
that a physical operation implements them; wrong reviewed semantics remain possible
and require native review plus actual postcondition checks.

## Finding and minimal correction

Previously `candidates` used heater readiness for heaterReady and cooler readiness
for **every other** predicate. Valid admitted graphs could not reach the fallback,
but a manually constructed malformed Usage could. The new explicit allowlist raises
ValueError for unsupported readiness before any authorization or dispatch. It does
not silently reinterpret it. This is the only runtime correction. No ontology,
fixture, existing graph/review hash, controller policy or historical outcomes changed.
Direct Python records are still not a supported untrusted acquisition interface.

## Focused tests and actual execution

Reproduce:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/aat -v
```

New `tests/aat/test_validity.py`:

- `test_closed_profile_rejects_unsupported_semantics`: 15 mutated-graph controls:
  unknown/ambiguous readiness, unsupported effect operator, wrong subject, missing/
  extra/literal/blank-node frame members, boolean/+2 delta, unsupported increments,
  invalid bounds/profile and extra assertion. Matching synthetic hashes isolate
  structural rejection; they are not claimed human approvals.
- `test_unknown_predicate_in_memory_has_no_cooler_fallback`: direct malformed record
  rejects rather than using cooler readiness.
- `test_loaded_graph_and_registration_invariance_with_actual_execution`: six actual
  HTTP episodes, cold/hot × original/reordered/renamed-and-reverse-registration.
  Reverse RDF triple order, reverse lexical order of opaque Usage identifiers and
  reverse Usage/operation registration; physical POST remains heat for 21 and cool
  for 23, exactly one mutation, verified 22. Only one action contributes in these
  states. This does not prove tie independence for multiple eligible actions: the
  documented handle-based tie-break can depend on IDs.

Existing `test_agent_artifact.py` tests guard veto, single-use permits, premature
Finish, native faults, and actual intervention/reconsideration under both conditions.
Its flip test checks STALE_PROPOSAL enters the next reasoner view followed by Observe.
New recording-reasoner assertions check actual temperature, full admitted Usage
records and typed OBSERVED feedback/context reach `Reasoner.propose`. Tests execute
real loopback APIs; the six invariance episodes are focused test fixtures, not a
new 22-episode scientific run. Test log and source/evidence verification are retained
under `docs/artifacts/eswc_aat_validity/`. Actual result: **13 tests passed in
7.008 seconds, exit 0**. All **336 historical sealed raw files** still match their
recorded hashes. The only tracked baseline modification is the explicit readiness
rejection in `runtime.py`; all other deliverables are additions.

## Controller, harness and comparison validity

`runtime.py::run` builds ControllerView from actual `observe()` responses,
`definitions`, `candidates` and Feedback. `ScriptedReasoner.propose` chooses the
eligible goal-establishing Usage itself. `study.py::episode` passes only policy,
origin, graph, approved hash and goal. Its synchronization hook checks stage/turn
and private intervention flags; it does not read the proposed handle. Expected
choices in `study.py::cases` score results after execution, not as reasoner inputs.
Worker module inventories and public-input checks in run-001/test suite support
this data-path claim; host files are not a security boundary against a hostile worker.

The procedural arm is a **representation/procedural-knowledge comparison**, not
an independently implemented agent or independent algorithmic baseline. `definitions`
uses native path-indexed Python readiness/bounds/deltas rather than RDF behavior.
Both arms share immutable records, candidate evaluator, scripted reasoner, loop,
guard, transport, postverification and native scorer. Both load the structural
catalog. Shared errors can yield common-mode parity. No semantic superiority,
authoring-effort advantage, independent blinding or LLM reasoning is demonstrated.
