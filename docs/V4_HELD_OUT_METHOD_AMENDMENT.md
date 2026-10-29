# Controlled held-out Provider C case study: methodological amendment

Authorized by the investigator's uploaded request, "V4 — Execute Controlled
Held-Out Provider C Generalization Case Study". Frozen experimental baseline:
`87309bca7456f3d8df827549761052cd467a3f7b`. Readiness document:
`docs/V4_HELD_OUT_GENERALIZATION_READINESS.md`. Historical blocker:
`docs/V4_HELD_OUT_EXECUTION_BLOCKER.md` (preserved without edits).

## Amendment

This study uses **one development context for evaluation and integration**.
Separate evaluator/integrator identities, independent curator authorship and
integrator blinding are **not claimed**. The previous blocker is superseded only
with respect to those identity/separation requirements. This also amends the
readiness document's identity/exposure prerequisites for this controlled case
study; the earlier documents remain historical records, not rewritten protocols.

The investigator authorizes opening and inspecting existing Provider C materials.
Correctness will be evaluated against original native provider state using
native-specification-derived expectations, independently of semantic description
implementations. That is independence of the data path/criterion, not independent
human curation. The same context will see native code and expectations; shared
authorship creates expectation, implementation and confirmation bias. A separate
pre-integration gate commit establishes ordering/provenance but does not remove
that bias or prove an independently authored holdout.

The question is whether frozen V4 infrastructure developed on A/B supports one
previously unseen provider via provider-specific integration artifacts. This is
functional generalization in a controlled single-provider case study, not a
measurement of integration-effort reduction or provider-population generalization.
Provider provenance and any prior exposure must be reported, not assumed.

## Unchanged obligations

- Shared `src/semantic_capability_v4/` and `v4/vocabulary.json` remain byte-identical
  to baseline. Existing A/B integrations, V3 and historical evidence stay unchanged.
- Inspect the actual supplied public/native Provider C implementation before
  authoring concrete cases; never manufacture a replacement and call it held out.
- Before integration artifacts, record native behavior and applicability of all
  16 families, concrete expected native outcomes, evaluator checks and hashes in
  a separate gate commit. Expectations derive from the native API specification,
  not runtime mappings. Validate the native evaluator before condition execution.
- Add only provider-specific adapters/descriptions and minimal fixture/worker/
  evaluator/reporting support. Conditions A/API-local, B/JSON and C/Turtle share
  the same public specification, canonical tasks and native correctness standard.
- Keep all failures, unsupported requirements, deviations, attempted revisions,
  late mutations and unknown outcomes. Any gate correction must be separately
  justified/committed, never tuned silently to match integration results.
- Do not repair frozen runtime limitations. Report partial/unsupported support,
  explicit workarounds and functional parity differences. A successful HTTP call
  alone never proves domain correctness; repeated tasks are not provider units.
- No nested Codex/model sessions, planning, action contracts or semantic reasoning.
  Implementation and results commits follow the pre-integration gate commit.

## Current execution status

The amendment is recorded **before** any Provider C gate or integration. Authorized
searches found no existing Provider C API specification, native implementation or
service reference in the available checkout, attachment listing or shared workspace.
The repository's `docs/HELD_OUT_EVALUATION_PROTOCOL.md` explicitly describes the C
paths as proposed, not existing artifacts. Available native fixtures are A/B only.
This is a material-availability finding, not a provider compatibility result.

The investigator has been asked for the existing specification and native source/
service/artifact location. Until supplied, native constraints, applicability,
expected answers and all correctness outcomes remain unknown. No Provider C gate,
provider implementation, adapter, description, fabricated observations or study
results have been generated. The historical separation blocker is no longer the
reason for this pause. Execution proceeds once the actual provider is available;
this amendment does not substitute for the required native gate.
