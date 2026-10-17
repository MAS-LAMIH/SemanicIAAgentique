# Milestone 4 scientific freeze audit — candidate, not an approved freeze

## Scope and provenance

No Provider C material was inspected, implemented or integrated. No frozen
research question or experimental condition was changed. No frozen protocol PDF
was found in the workspace; the supplied frozen decisions and milestone briefs
were used. Runtime validation is limited to controlled A/B services and the
finite profile. The generic resolver, transforms, loaders, bindings, execution
pipeline, fixtures, oracle and existing tests are unchanged in this milestone.

The base commit is b70e8314e3a00f10522e65c82a6b4b3fd29ac4bb on branch
codex/semantic-actions-json-rdf-parity. Milestone 3 is present as tracked changes
and untracked files, not in that commit. The new scientific manifest records the
actual working-source hashes and a source archive including those files; it does
not misrepresent HEAD as the tested complete implementation. The prior
freeze-manifest.json hashes verified at audit entry. That preparation manifest
remains unchanged as historical evidence.

## Implementation findings

| Check | Evidence / conclusion | Qualification |
| --- | --- | --- |
| Provider-specific separation | Providers' paths, wire keys and limits are in contracts/providers and fixtures; generic registry/transform code uses descriptors | The generic model is still calendar-domain-specific, one capability and three transforms; it is not arbitrary Web API interoperability |
| No substitution lookup table | Registry resolves explicit capability ID and required effect; no A-to-B name/ID switch or replacement table found | Demo/test wiring names A/B explicitly; that is evaluation configuration, not inference |
| JSON/RDF equivalence | Both v2 loaders feed load_provider_data with one schema; current A/B typed models are equal; differential controls compare raw/canonical semantic outcomes | B/C are shared implementations, not independent engine or parser-performance baselines; syntax/error strings may differ |
| Input/critical state gates | Pipeline validates profile and inputs before POST, requires all current TRUE conditions, blocks FALSE/UNKNOWN; execution probes fresh state again | A caller with raw HTTP or private method access is outside this software API boundary; no security sandbox claim |
| Independent verification | verify consumes Goal, before/after observations and event ID, not declared effects; success/no-change, wrong data, stale evidence and side effects fail | Observations are canonicalized by subject-supplied mappings; native-state independence still needs external review/measurement |
| Explicit semantics | Capability/effect/constants, transforms and constraints reside in shared code/schema plus vocabulary | Vocabulary Turtle is explanatory, not a dynamically loaded reasoning engine; all those files must be frozen together |
| Negative controls | test_registry covers different/similar names, effect mismatch, missing transform source, precision loss, FALSE/UNKNOWN/stale, constraints and false success | Missing/malformed/future evidence is also covered in Milestone 2 tests of the shared evaluator; not every family has a separately authored multi-provider native-state test |
| No oracle/applicability bypass through supported bindings | Registry-selected execution delegates to Executor.run; direct-pipeline test rejects known constraints; successful action paths call the oracle | Validated mappings are trusted; a dishonest field mapping is not semantically authenticated. See risk R3 below |

No blocking defect in the supported A/B workflow justified changing the generic
resolver. Findings are recorded rather than silently changing behavior. Public
execution does not treat API success as goal achievement; null/not-run oracle
results are not successes. A resolution decision is not a reusable permission
token. Manual hashes are checked but trusted local files/single-writer behavior
are assumed; this is not a concurrent adversarial transaction protocol.

## Freeze/evaluation discrepancies and unresolved risks

- R1 — Source identity: dirty/untracked Milestone 3 cannot be reproduced by
  checking out HEAD alone. The candidate archive and per-file hashes preserve the
  tested source; commit/tag or formally approve the archive identity before freeze.
- R2 — Condition A: a distinct API-local experimental baseline is absent. Provider
  A is not condition A. Implement/review it before unsealing for a three-condition
  comparison. Do not weaken its validators to create an apparent reuse advantage.
- R3 — Oracle independence: raw data are retained, but the oracle trusts manual-
  supplied output mapping and completeness. An independent curator/native-state
  observer procedure and task-specific expectations must be approved before runs.
- R4 — Holdout provenance: A/B were authored by one AI contributor. No repository
  check proves independent organizational development or external human blinding.
  Obtain exposure declarations and independent review; no C exposure is claimed.
- R5 — Cost validity: historic logs mix AI activity and waits and omit human-active
  time, supervision split and some categories. No human-cost savings or complete
  cold-start totals can be estimated from them. Approve prospective collection.
- R6 — Bounded coverage/platform: loopback HTTP, trusted complete snapshots, one
  writer, local clocks, supported timestamp precision and fixed transformation
  vocabulary. Unsupported C requirements must remain unsupported, not trigger
  hidden generic adaptation after release. Live tutorial examples are unverified.
- R7 — Reproducibility: root tutorial dependencies are unpinned; project metadata
  omits semantic runtime dependencies (installed separately). The candidate pins
  the resolved minimal evaluation dependencies and retains a wheel/source hash;
  platform/build-tool availability still needs environment archival. No cross-
  platform reproducibility or fresh cloud restoration claim is made.
- R8 — Trace/error scope: private HTTP methods can mutate without the public
  pipeline; output directories must be new, since exclusive trace writing occurs
  after action execution. A successful low-level call or process error is never
  a verified success. The candidate is for trusted harness operation, not hostile
  in-process callers or idempotent retry guarantees.

These findings prevent a claim of an approved, ready three-condition confirmatory
experiment. They do not prevent archiving and auditing this bounded candidate.
No Provider C implementation or answer is needed to resolve the pre-release gates.

## Prospective controls and explicit approval gates

HELD_OUT_EVALUATION_PROTOCOL.md defines the permitted addition-only provider
boundary, change audit and generic-defect/restart rule, task families and
independent expectations. COST_MEASUREMENT_PROTOCOL.md separates labor, AI
supervision, runtime, waiting, wall time, activities, failures and reuse costs.
EXPERIMENTAL_PARITY_CHECKLIST.md records current B/C evidence and missing A.

Human approval is required for the exact candidate digest and source identity,
condition-A baseline, independent observer and task expectations, task counts,
seeds/order/budgets/stopping rules, contributor exposure plan, cost collector and
allocation, and final parity review. No approval or unsealing authorization is
implied by completion of this milestone. Formal approval must identify signer,
time and approved digest; a later source change creates a new candidate.

## Reproduce candidate verification

The scientific manifest lists commands/results, scoped files, Python/dependencies,
artifact hashes and limitations. Candidate archive extraction includes the exact
uncommitted source without git metadata; HEAD/branch provenance is recorded
separately. The artifact helper in artifacts/milestone4/candidate_artifacts.py
creates the deterministic source archive or verifies the saved manifest. It does
not approve a freeze and does not run or discover Provider C.

From repository root, verify:

```sh
python3 docs/artifacts/milestone4/candidate_artifacts.py --verify
```

For isolated restoration, extract the source archive into a new empty directory
and install the retained wheel with the pinned evaluation dependency list. Run
unittest discovery only under tests/semantic_action (50 deterministic methods;
subtests exercise additional cases). Use a new output directory for each demo.
Full commands and recorded evidence are in the manifest. Do not broadly discover
the original tests/test_*.py, which are external-service tutorial demonstrations.

The test-result and artifact-verification summary is populated from actual
commands at the end of this audit; unknown approvals remain null.

## Actual validation results

- Source suite: 50/50 passed in 82.102 seconds; no failures, errors or skips.
- Fresh installed-wheel suite: 50/50 passed in 82.438 seconds; no failures,
  errors or skips. Both supported schemas and the tutorial prompt are packaged.
- A/B typed JSON/RDF profiles were equal; all four provider/representation demos
  verified their goals; UNKNOWN and false-success demos returned the intended
  exit 1. Expected-negative outcomes are not counted as failed setup checks.
- The prior manifest verified at entry. Generic/provider/oracle/test file bytes
  were checked against an audit-entry snapshot and are unchanged.

Actual commands, output logs, interpreter/dependency inventory and generator
metadata are retained under artifacts/milestone4 and hashed by the scientific
manifest. The exact minimal evaluation pins complement the retained project
wheel; the latter must be installed separately because pyproject has no runtime
dependency declarations. Source-archive restoration and tamper-detection evidence,
when performed, are recorded in validation-results.json, not implied by this text.
No original live tutorial tests or Provider C tests were run.
