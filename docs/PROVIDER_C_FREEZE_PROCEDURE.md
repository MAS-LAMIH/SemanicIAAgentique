# Procedure for freezing generic machinery before Provider C

Status: preparation only. The current working tree is not an immutable reviewed
freeze. No Provider C has been implemented or examined in this task. That fact
alone does not prove independence of a future experiment.

1. Review the frozen scientific protocol, semantic profile, oracle guarantees,
   experimental conditions A/API-local, B/JSON+shared semantics and C/RDF+shared
   semantics (these condition labels are distinct from provider labels). Confirm
   capability meanings, constraints, mappings and validation power are equal for
   the shared-semantics representations. Decide the allowed onboarding edits,
   cost categories, correctness criteria and stopping rules before exposure to C.
2. Resolve known design issues using A/B and declared synthetic negative controls
   only. Do not inspect C documentation, code, schemas, request examples, failures,
   or expected benchmark answers during generic design. Keep provenance of who
   has seen which materials; this repository cannot establish organizational
   blinding. If already exposed, disclose it and redesign the holdout procedure.
3. Generate the preparation manifest with
   `.venv/bin/python scripts/freeze_manifest.py` and verify with
   `.venv/bin/python scripts/freeze_manifest.py --verify docs/freeze-manifest.json`.
   Review docs/freeze-manifest.json. It identifies generic engine, shared semantic
   vocabulary/mapping infrastructure, provider-specific files, validation/oracle,
   evaluation fixtures, tests and dependencies. Recompute each SHA-256 from the
   listed path and compare it. Explicitly classify new files; no catch-all ignore
   of unclassified implementation files. The manifest intentionally excludes its
   own hash to avoid self-reference.
4. Run the complete deterministic suite, all four representation/provider demos,
   package build, installed-wheel tests and dependency consistency checks. Save
   exact commands, results, Python/platform versions and resolved dependency
   inventory. Existing unpinned tutorial requirements are not a reproducible lock;
   freeze the actual environment artifact and record a resolved inventory outside
   the checkout or add a separately reviewed evaluation lock. Review licensing.
5. Commit the reviewed baseline, regenerate the manifest with the intended source
   tree/commit provenance, and create an immutable signed tag or equivalent
   archived artifact. Record commit, manifest hash and environment snapshot IDs
   in an experiment record. Check that the source files still match all hashes.
   A JSON manifest alone is not a freeze; approval and provenance are required.
6. Only after that freeze may a separate onboarding contributor receive Provider
   C materials. Add provider-local documentation, contracts, declared mappings,
   credentials/runtime settings and adapters only where predeclared permissible.
   Record all annotation, mapping, adaptation, setup, tests, debugging and failed
   attempts by condition and shared versus incremental work. Never omit a cost
   because an AI assistant performed it. Missing measurements remain missing.
7. Before each C run, verify all frozen generic/shared/oracle hashes. Unsupported
   requirements must be reported as compatibility failures, not patched into
   generic code using C knowledge. If a generic fix is necessary, record a protocol
   deviation; the modified engine is no longer the untouched confirmatory baseline.
   Separate exploratory repair results from confirmatory results. Never reset
   failures or replace hidden expected answers to make a run pass.
8. Evaluate C under the predeclared correctness oracle and equivalent goal-level
   requirements, retaining raw observations and normalized traces. Keep failed,
   unknown, rejected and unrun outcomes distinct. Report negative/null results;
   any beyond-observed-provider break-even projection is an estimate.

No LLM planner, full E1 benchmark, automatic substitution, or natural-language
goal interpretation is authorized by this procedure. Publishing the cloud
environment is separate from freezing a scientific implementation.
