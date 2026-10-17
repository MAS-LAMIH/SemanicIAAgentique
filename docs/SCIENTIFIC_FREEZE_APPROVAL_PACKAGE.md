# Milestone 4.2 — investigator approval package

Status: **pending investigator review; no scientific freeze approval and no unsealing authorization**.
This package audits the immutable Milestone 4.1 candidate. It adds documentation only;
it does not implement a provider, change the engine, or amend the frozen research questions.
Condition C (RDF) and held-out Provider C are different axes. Only visible providers A/B
were used. The governing [protocol](protocols/ESWC_2027_Frozen_Research_and_Experimental_Protocol.pdf)
§§4–9 remains authoritative: RQ1/E1 primary, RQ2 secondary, RQ3 optional.
The protocol is specification material, not an investigator signature.

## 1. Exact candidate and documentation identities

| Item | Verified identity |
| --- | --- |
| Candidate commit | `2829c6dc41344431e83bde7c3addf30d1241befc` |
| Annotated local tag | `candidate/milestone-4.1-pre-freeze`, peeled to that commit |
| Candidate branch at audit entry | `codex/milestone-4-1-pre-freeze` |
| Implementation commit in manifest | `1b6b8e43c31230d6e458ce6747c447f5fba5bab3` |
| [V2 manifest](SCIENTIFIC_FREEZE_MANIFEST_V2.json) SHA-256 | `7f8e8d1d4f0f07e8c5ef999c36aaf987d17bf58d757df4a733f736ceaa78bcc2` |
| Manifest source-tree digest | `20bde86375955f144494a0b8353c87a1b1b1b48de2ea4b7daf218e79240b6494` |
| [Retained source archive](artifacts/milestone4_1/candidate-source-v2.tar.gz) SHA-256 | `b2c9d888f81bdd4bdb941d16eaef520fecc5f58fe35c8b8736e949b42ed7d7a3` |
| M4 historical manifest SHA-256 | `2a01e44585d355cd3b763f0551a9f33c1139fe53595d3c8b28cd62d71a93bd4c` |
| M4 historical archive SHA-256 | `ae34e3efe0b278ee1b6fafe90f90f6e7f845d2d5eeaf0d8c69c1c7fb60902c69` |

The implementation commit and final evidence/metadata commit are intentionally distinct;
this is not a mismatch. Entry working tree was clean and HEAD/tag/digest matched the
user-supplied identifiers. The tag is annotated, not evidence of a cryptographically
signed investigator decision. Its historical “No remote push performed” describes
creation time; the branch was subsequently pushed on user instruction. No claim is
made that the local tag itself was published remotely.

This documentation revision consists solely of this file and
[SCIENTIFIC_FREEZE_DECISION_RECORD.json](SCIENTIFIC_FREEZE_DECISION_RECORD.json).
Their eventual Git commit identifies the review revision, not a replacement tested
implementation. Until committed, their revision is the working-tree diff against
`2829c6d`. Do not regenerate V2, retag, or insert approval into its immutable bytes.
The decision record binds the package by SHA-256 and leaves its own eventual commit
null to avoid circular commit identity. A signed detached decision must bind both the
original candidate manifest and the reviewed documentation revision.

## 2. Technical verification evidence

At audit entry, these commands returned exit 0:

```sh
git status --porcelain                         # empty at entry
git rev-parse HEAD 'candidate/milestone-4.1-pre-freeze^{}'
sha256sum docs/SCIENTIFIC_FREEZE_MANIFEST_V2.json
python3 scripts/candidate_v2.py --verify
python3 scripts/candidate_v2.py --verify-history
```

The first verifier checked all 104 scoped source files, artifact hashes, exact archive
membership/bytes, source-tree digest, pending approval and false unsealing flag.
Historical verification checked 14 immutable evidence files and 74 archived M4 source
members. No original evidence was rewritten. Exact final commands and stage IDs are in
[validation-results.json](artifacts/milestone4_1/validation-results.json):

| Final candidate stage ID | Result | Recorded runtime | Log |
| --- | --- | --- | --- |
| `source_after_native_extension` | 66 pass; 0 failures/errors/skips | 145.313 s | [source log](artifacts/milestone4_1/source-after-native-extension-tests.log) |
| `wheel_after_native_extension` | 66 pass; 0 failures/errors/skips | 145.765 s | [wheel log](artifacts/milestone4_1/wheel-after-native-extension-tests.log) |
| `restored_after_native_extension` | 66 pass; 0 failures/errors/skips | 145.513 s | [restoration log](artifacts/milestone4_1/restored-after-native-extension-tests.log) |

These are retained M4.1 results, not new M4.2 wheel builds. Intermediate 64/65-test
runs are not final evidence. The archived [integrity probes](artifacts/milestone4_1/final-integrity-checks.json)
record acceptance, deliberate source-tamper rejection, and acceptance after restoration.
The [local-only environment](artifacts/milestone4_1/local-only-v2-environment.json)
records successful local execution without RDFLib/jsonschema installed.

The current `.venv` was inspected: Python 3.12.14 and all nine project/runtime package
versions exactly match the retained [environment](artifacts/milestone4_1/evaluation-environment.json):
attrs 26.1.0, jsonschema 4.26.0, jsonschema-specifications 2025.9.1,
pyparsing 3.3.3, rdflib 7.6.0, referencing 0.37.0, rpds-py 2026.9.1,
tutorielIAAgentique 0.1.0, typing_extensions 4.16.0. Reproduction pins are
[evaluation-requirements.txt](artifacts/milestone4_1/evaluation-requirements.txt).
Matching installed version strings alone does not authenticate installed code;
the retained wheel hash and source/archive hashes supply separate provenance.

M4.2 source revalidation: `.venv/bin/python -m unittest discover -s tests/semantic_action -v`
passed **66 tests in 145.260 seconds**, exit 0, with no failures/errors/skips.
The complete captured runner output and its hash are retained in the decision JSON.
No wheel/reinstallation or confirmatory experiment is claimed for M4.2.

After adding these documents, `candidate_v2.py --verify` in the expanded checkout
will reject **Unclassified source addition/deletion**: its coverage rule includes
new documentation. This is an expected scope difference, not permission to revise
the manifest. Reproduce verification of the exact candidate in a temporary checkout:

```sh
review_dir=$(mktemp -d /tmp/semanic-m42-candidate.XXXXXX)
git archive 2829c6dc41344431e83bde7c3addf30d1241befc | tar -x -C "$review_dir"
python3 "$review_dir/scripts/candidate_v2.py" --verify
python3 "$review_dir/scripts/candidate_v2.py" --verify-history
git diff 2829c6d --name-status
git ls-files --others --exclude-standard
```

Review both tracked diff and untracked paths; only the two approval documents may
be added. The original archived candidate, not this enlarged document tree, remains
the tested implementation. No catch-all exclusion or verifier change is proposed.

### Discrepancies and editorial qualifications (preserved, not repaired)

- No mismatch in requested candidate identity, hashes, archive, dependency versions
  or final recorded test counts was found.
- [M4.1 checklist](SCIENTIFIC_FREEZE_APPROVAL_CHECKLIST.md), “Approval record,” still
  says manifest identity is pending. This package supplies the exact digest above;
  that placeholder is stale, not evidence that approval occurred.
- [M4.1 report](MILESTONE_4_1.md), “Observed test evidence,” calls 65-test runs final
  before its later “Final candidate distinction” identifies 66. Likewise validation
  IDs `final_source`/`final_installed_wheel` are intermediate; use only
  `final_candidate_suite_ids` for the final candidate.
- [Held-out protocol](HELD_OUT_EVALUATION_PROTOCOL.md), “Prospective task families,”
  leaves numerical settings unset before its later M4.1 proposals. Those numbers
  are proposals, not contradictory approvals. Its reference to approval pending
  in the older manifest is historical; V2 is the current technical candidate.
- The 60-second outer deadline, order schedule, role controls and human timers are
  prospective procedures, not enforced by the visible `run_case` implementation.
  Approval must not mistake documented controls for implemented supervision.

## 3. Three-condition parity assessment

Equivalent **correctness obligations** are supported on the controlled scenarios;
A does not have equivalent cross-provider discovery information. A explicitly
selects local code/contracts; B/C carry identical shared semantic information.
No A-to-B substitution table occurs in `Registry.resolve`: it iterates registrations,
checks capability/effect/constraints and probes applicability. `execute` requires a
unique eligible operation, checks manual identity and invokes the validating pipeline.
The caller still selects an operation ID; this is not autonomous planning.

Exact test identifiers below are unittest module/class/method names under
`tests/semantic_action/`. The [66-test source log](artifacts/milestone4_1/source-after-native-extension-tests.log)
records them; the 120-case matrix is one test method with subtests, not 120 independent
provider observations.

| Obligation | Condition A evidence | Shared B/C evidence | Executable evidence |
| --- | --- | --- | --- |
| Complete input validation; timezone, title, precision | [local_baseline.py](../src/semantic_action/local_baseline.py), `CalendarLocal.validate`, `BookingLocal.validate/milliseconds` | [pipeline.py](../src/semantic_action/pipeline.py), `validate_inputs`; [transform.py](../src/semantic_action/transform.py), `validate_profile` | `test_parity.ParityTests.test_invalid_inputs_parity`; `test_registry.RegistryTests.test_input_precision_cannot_be_silently_lost`; matrix D09/D10 |
| TRUE/FALSE/UNKNOWN and fresh evidence; no unchecked mutation | `LocalExecutor.run`: fresh baseline, explicit bool permission, execution only TRUE | `Executor.assess/run`, `evaluate_preconditions`; [registry.py](../src/semantic_action/registry.py), `resolve/execute` | `test_registry.RegistryTests.test_execution_rechecks_permission_after_resolution`; `test_false_unknown_and_stale_preconditions_block`; matrix D05–D08 |
| Effects, preservation, bounds, formats and bindings | [local descriptions](../contracts/api_local/), local `validate/encode` and endpoint methods | [a.json](../contracts/providers/a.json), [a.ttl](../contracts/providers/a.ttl), [b.json](../contracts/providers/b.json), [b.ttl](../contracts/providers/b.ttl); shared `validate_profile/adapted_request` | `test_registry.RegistryTests.test_similar_names_do_not_override_non_equivalent_effects`; `test_direct_pipeline_cannot_bypass_known_constraints`; matrix D03/D04/D11/D19/D20 |
| Same B/C accepted semantic domain and typed mappings | A is a different authoring mechanism, not a serialization counterpart | [provider_contract.py](../src/semantic_action/provider_contract.py), `load_provider_graph` decodes then calls `load_provider_data`; [contract-v2.schema.json](../src/semantic_action/schemas/contract-v2.schema.json); v1 JSON also enters common graph validator | `test_registry.RegistryTests.test_v2_schema_and_models`; `test_unsupported_extra_rdf_information_is_not_silently_dropped`; `test_parity.JsonValidationTests.test_duplicate_keys_nonfinite_and_malformed_json` |
| Read-after-write, evidence age, revision, formal goal and noninterference | `LocalExecutor.run/observation/state` | `Executor.observe/run`, profile transforms | [oracle.py](../src/semantic_action/oracle.py), `current/verify`; `test_parity.ParityTests.test_typed_models_and_nondefault_age_rules`; matrix D12–D18 |
| Native truth and unsafe-call detection | Same evaluation wrapper as B/C | Same evaluation wrapper as A | `test_pre_freeze.ThreeConditionTests.test_all_twenty_diagnostics_on_visible_providers`; `test_unsafe_mutation_attempt_is_not_hidden_by_goal_outcome` |
| Local baseline excludes semantic discovery | neutral model/oracle/transport imports only | B/C intentionally share registry/loaders/transforms | `test_pre_freeze.ThreeConditionTests.test_no_semantic_discovery_imports_in_local_baseline`; retained dependency-free local run |

The matrix compares compatibility, probed applicability, mutation count, API success,
runtime/native/final verdicts and unsafe execution across fresh fixtures, and typed
B/C models for every variant. Earlier v1 differential tests compare normalized full
semantic traces/reasons, omitting run IDs, hashes and evidence timestamps while testing
freshness classifications explicitly. A/B/C parser diagnostics need not be identical.
JSON duplicates reject; identical RDF triples collapse by graph semantics. RDF extra
assertions/cardinality ambiguity reject. This is bounded typed-profile parity, not
arbitrary JSON/RDF equivalence or a proof over all possible malformed inputs.

Cautions: the matrix serializes mutated RDF from JSON using `provider_graph`, so
writer/reader common errors could agree; static authored Turtle model checks partly
mitigate this. Independent neutral content review is still pending. D02 resembles
D01 except names/title; D04 and D11 use the same reservation-effect intervention;
these are overlapping controls, not 20 orthogonal semantic capabilities. D09 uses
unsupported local encoding in A versus unavailable mapping source in B/C, a common
failure category rather than identical internal representation. B/C also do a
resolution probe plus execution recheck; A probes in execution. Charge actual reads
and timing rather than hiding the architectural difference. Tests establish no
latency, labor-saving, discovery superiority or RDF-superiority result.

Shared by all: model/goal/time parsing, neutral HTTP transport, unchanged formal
oracle, fixtures, evaluation tasks/native adjudication and collector. A-specific:
local descriptions, local validators/encoders and ordinary local helper setup.
B/C-specific shared setup: vocabulary, registry, schema, transforms and semantic
validation. Representation-specific: parsing, serialization, authoring/conversion,
format diagnostics and review. The all-condition harness imports both stacks;
that evaluation overhead must not be charged as A's semantic dependency.

## 4. Oracle independence and leakage assessment

Trace the actual data path in [native_verifier.py](../src/semantic_action/native_verifier.py):

1. `evaluation.run_case` creates a fresh `Scenario`/`BookingScenario`; `capture`
   deep-copies native `events`/`items`, revision/version, permission and call count
   before and after execution. Snapshot time is evaluator-generated.
2. `_calendar` reads native event fields; `_booking` reads `booking_ref`, integer
   `begins_ms/finishes_ms`, and `label`, converting with epoch/timedelta. Neither
   imports subject output mappings or `transform.convert`.
3. `adjudicate` derives the unique new ID from native key-set difference, not the
   HTTP response or manual. It constructs its own canonical observation and calls
   the same frozen `oracle.verify` using `NativeExpectation.goal`.
4. It additionally compares raw pre-existing record content and mutation-count
   bounds. Runtime verdict is used only to flag disagreement. `evaluation.run_case`
   requires runtime AND native achievement AND no task-defined unsafe mutation.

[Tests](../tests/semantic_action/test_pre_freeze.py):
`NativeVerifierTests.test_native_observer_has_no_subject_mapping_dependencies`,
`test_snapshot_deep_copy_and_native_extra_change_detection`,
`test_stale_native_evidence_never_establishes_truth`, and
`test_evaluator_owned_extension_needs_no_core_truth_change` cover structural separation,
raw-state preservation, stale evidence, and trusted decoder identity. D15 deliberately
stores the wrong title and exposes a decoy mapped title: runtime accepts but native
rejects, in all conditions; [retained example](artifacts/milestone4_1/examples-final/D15-b-B/evaluation.json).
D17/D18 show that independently observed achievement cannot excuse missing mandatory
runtime evidence. Native truth alone is not the final success criterion.

This establishes independence from **subject mappings, declared effects and pipeline
canonicalization**, not independence of every assumption or human author. Remaining
common modes include the shared oracle/Goal/clock/time parser, one AI author exposed
to A/B manuals, trusted fixture implementation/call counters, same-process harness,
and lack of external state attestation. `NativeSnapshot.writable` is recorded but
`adjudicate` does not independently enforce permission; safety rejection uses the
task's independently specified maximum/expected call count in the wrapper. A wrong
curator label could mask an unsafe call. Whole-world preservation is not proved:
only captured fixture storage is checked; concurrent/external side effects and
metadata on the newly created event beyond goal fields are outside this claim.

`NativeInterpretation.source_reference` is provenance text, not signature enforcement.
Arbitrary evaluator decoder code is trusted; path separation cannot prevent malicious
or mistaken reuse of a subject map. Future curator-supplied observation code requires
independent review and custody before execution, under the existing addition-only
boundary; generic truth rules may not change.

Public `DiagnosticTask.expectation(provider)` contains visible A/B apparatus labels.
It is not sealed ground truth and must never feed the resolver/manual author or
be copied as a held-out answer generator. The same author's task provenance statement
is not evidence of independent curation. Before any future evaluation, an independent
curator must derive and sign task inputs, feasible-positive/negative labels, state
predicates, allowed effects and evidence rules from domain requirements/reference
service behavior, **not provider manual postconditions**. Curator native bindings may
use authoritative service/storage specifications after authorized release, but
not the subject's mapping as their sole source. Review and hash expectations before
subject runs; keep answer material away from onboarding contributors. No such future
provider artifacts or answers are created or accessed here.

## 5. Proposed cost allocation — decision required before exposure

Preserve the [cost protocol](COST_MEASUREMENT_PROTOCOL.md) and raw
[44-event ledger](artifacts/milestone4_1/events.jsonl). Its
[summary](artifacts/milestone4_1/resource-summary.json) reports measured automation
22.085086981433257 minutes and measured elapsed intervals 29.73695 minutes, each
with missing records and a limited observation window. Human active, AI supervision,
tool waiting and model waiting totals are null. These are apparatus engineering
records, not experimental human onboarding costs or complete cold-start totals.
Do not add runtime to elapsed time or supervision to human active time.

Proposed resource policy: human active person-minutes are primary labor; AI-assisted
human supervision is a tagged subset, reported separately. Automated runtime, tool
wait, model wait and elapsed are separate axes; simultaneous automation is allowed,
human active intervals cannot overlap for the same person, elapsed is interval union
per declared scope rather than a sum across concurrent runs. Unknowns stay null with
measured-subtotal/missingness counts; no zero imputation, reconstructed history or
unobserved pricing. Record AI usage/model/tool identity and observed tokens/rates only
when actually available. New review labor uses a new ledger, never appends to frozen
M4/M4.1 evidence. This audit does not fabricate its own unobserved labor duration.

| Work | Proposed prospective classification |
| --- | --- |
| Neutral transport/goal oracle, evaluator/native verification, common apparatus | Common neutral setup; distinguish research evaluation overhead from deployable integration cost |
| A helpers/local contract machinery | A setup; provider-native rules/encoders/descriptions are A onboarding |
| Ontology/registry/shared schema/transforms/mapping curation | B/C shared semantic setup; provider-specific annotations/adapters are onboarding |
| JSON/RDF authoring, conversion, syntax checks and independent review | Attribute to actual format/asset activity, preserve conversion provenance; no format receives free derived artifacts |
| Documentation reading, environment onboarding, binding, fixture configuration | Provider/condition onboarding unless demonstrably reusable setup |
| Testing/debugging, failed attempts, rework | Charge to originating scope/condition including unsuccessful censored attempts; link event IDs, retain all costs |
| Maintenance | Separate dated API/manual/shared-infrastructure revisions; charge regression and repair to actual affected asset, show shared effects |
| Mixed unmeasured historical work | `mixed_unallocated`/null; never split by imagined minutes or lines changed |

Choose and register a primary allocation policy **before outcomes**; report alternatives
as sensitivity analyses regardless of which favors a condition:

| Policy | Allocation | Implication |
| --- | --- | --- |
| P1 standalone cold start (proposed primary) | Each standalone condition bears full relevant study-specific neutral setup; B and C each bear full required semantic setup plus their own authoring. Common preexisting assets are disclosed with unknown creation costs where missing. | Answers independent deployment economics; sums across conditions intentionally duplicate counterfactual setup and are not a joint spend total. |
| P2 joint deployment | Charge each unique shared asset once in a portfolio; neutral cost split equally A/B/C and semantic shared cost equally B/C, with provider work direct. Publish unsplit totals too. | Answers combined-program economics; allocation depends on usage assumptions and cannot be called standalone savings. |
| P3 usage/amortization sensitivity | Use predeclared equal provider counts or observed documented usage weights, and ranges for unknown setup/maintenance. Freeze weights before evaluation. | Shows sensitivity to reuse scale; no post-hoc weights minimizing a favored condition's cost. |

For each resource axis report cold start `setup + sum(onboarding) + maintenance`,
incremental provider/condition cost after visible integration, and evaluation overhead
separately. Unknown setup means a complete empirical cold-start total is unavailable.
Do not present known incremental automation as observed labor savings. Beyond observed
providers, break-even uses explicitly model-based ranges, including no-crossing cases,
not empirical evidence. Censoring records observed costs and unfinished correctness,
not a completed integration at the time cap. Approval must specify collector/timer
practice, common-asset ownership, allocation, assistance access and missingness policy.

## 6. Prospective evaluation parameters — proposals, not an executed study

The [20-task specification](EVALUATION_TASK_SPECIFICATION.md),
[machine-readable sheet](evaluation_tasks_v1.json), and
[evaluation_tasks.py](../src/semantic_action/evaluation_tasks.py) define public apparatus
controls only. The following operational clarification must be approved and its actual
schedule sealed before release; no new runner or tasks are implemented here.

| Parameter | Proposed setting and rationale |
| --- | --- |
| Counts/families | Retain D01–D20: matches/names/formats (01–03), effect incompatibility (04/11), false/unknown/stale/missing permission (05–08), conversion/precision (09/10), HTTP/error/state/mapping/side-effects (12–16), stale/missing observation (17/18), duration/grid (19/20). One sweep = 20 × 2 visible providers × 3 conditions = 120. Three apparatus repetitions = 360, for stability rather than statistical power. |
| Scope gate | These single-action overlapping diagnostics do not meet the protocol's multi-step pilot requirement. Full E1 remains blocked pending a separate pre-confirmatory apparatus milestone or explicit registered scope deviation; neither is silently approved here. No future provider count/answer set is inferred from these A/B repetitions. |
| Seeds | Keep root seed 20271017; use separately registered task-order seed 20271018 and contributor-assignment seed 20271019. Record Python/random version and archive actual schedule; seed alone is insufficient. Seeds govern ordering/assignment, not retrospective answer selection. |
| Condition order | Canonical blocks sorted by provider ID, repetition 1–3, task ID D01–D20: 120 blocks. Assign the six permutations ABC, ACB, BAC, BCA, CAB, CBA cyclically by block index, 20 occurrences each. Shuffle block execution order using task-order seed, retaining each block's assigned condition order. All conditions start fresh. |
| Contributor order | Randomize/counterbalance onboarding separately from task execution with assignment seed. Prefer separate contributors per condition, balanced experience and equal documentation/tool access. One repeated author cannot undo learning with fixture resets; disclose it and withhold blind-cost claims. Register roster/schedule before exposure. |
| Reset/cache | Fresh separately initialized service per condition/task/repetition; identical task inputs, initial records, permissions, revision and counters, verified against curator reset evidence. Archive raw initial state and unique run directory. No carry-over events, cached discoveries/task answers or repairs; declare process/cache policy. Existing apparatus starts empty; preservation regression also tests existing records. |
| Budgets | Same existing 5 s per HTTP request; proposed outer 60 s per execution, 0 automatic retries, 0 planner/repair iterations. Proposed onboarding cap 90 human-active person-minutes and 300 elapsed minutes per provider/condition; includes setup within that attempt, testing/debugging/rework. All waiting remains separately logged. No exception grants by outcome. |
| Supervisor readiness | Outer deadline is not implemented in `run_case`. Before use, approve an external supervisor/operational procedure that terminates the subject, captures post-timeout native state and preserves traces. Do not alter generic code here. Until demonstrated, deadline enforcement is PENDING. |
| Stops/restarts | Stop affected runs on source/dependency drift, parity mismatch, unexpected unsafe mutation, unplanned oracle disagreement, untrusted observer or missing reset evidence. Quarantine impacted blocks; archive incomplete runs/costs and obtain independent classification. No favorable-result stop or hidden replacement runs. Timeouts are failures/unverifiable as appropriate, never successful censoring of the denominator. |
| Operational incident | Nonsemantic environment recovery requires recorded evidence and auditor agreement; retain original attempt. Any replacement is separately labeled. Generic defects stop affected confirmatory evaluation; preserve baseline failures or retire candidate. Exposure cannot be undone: repaired same-provider results are exploratory unless a valid new-holdout restart design is registered. |

### Metrics, denominators and reporting

Predeclare a row for every planned provider/task/condition/repetition, including unrun,
unsupported, timed-out, aborted and missing-evidence rows. Report counts and denominators
for feasible positives, intended negatives and feasibility unresolved. Feasibility is
curator-reviewed before execution; never relabel an unsupported intended positive as
a convenient negative after seeing the system's result.

Primary correctness is verified achievement on feasible positives, requiring runtime
and native verification plus no unsafe execution. Negative-control correctness is safe
rejection with zero forbidden mutation. Report these separately and a strict integration
readiness gate: all required positives achieve and negatives safely reject, zero unsafe
execution. This is a proposed operational threshold, not an observed provider-general
result. Also report false-positive eligibility/substitution, false-negative rejection,
FALSE/UNKNOWN handling, actual mutation counts, HTTP success, actual state change,
runtime/native disagreement, forbidden side effects, and missing evidence. Current
single-registration diagnostics do not estimate broad-catalog discovery accuracy.

Use layered failure labels, preserving simultaneous causes: input/schema/profile;
semantic incompatibility/unsupported transition or transform; FALSE block; UNKNOWN
block; binding/mapping defect; HTTP/transport; no state change; wrong properties;
forbidden side effect; stale/missing/inconsistent evidence; observer disagreement;
unsafe execution; timeout/budget exhaustion; environment incident; protocol deviation;
unrun. `case_passed`/CLI exit 0 means expected diagnostic behavior, not action success.
D15 disagreement is planned control behavior; unplanned disagreement stops review.

Costs: raw axis-specific measured subtotals and missingness; provider-level paired
A–B/A–C/B–C incremental and cold-start differences, component breakdowns, failures and
censored attempts. Record experience, assistance, mappings added/reused, edits and
maintenance separately; lines changed are descriptors, not person-minute estimators.

Providers are the independent generalization units. A/B are exposed development
fixtures (n=2), not two independent held-out validations. One future held-out provider
would give n=1 held-out provider regardless of 60 task-condition rows or repetitions.
Show all provider-level paired outcomes and within-provider task/family tables, medians,
ranges and stability discrepancies. Avoid pooled execution-level significance tests,
provider-population confidence intervals or bootstrap over task repetitions presented
as provider uncertainty. If future independent provider numbers justify inference,
pre-register provider-cluster uncertainty and assumptions before collecting them.
For this small sample, report raw paired differences and descriptive variation; model
sensitivity intervals for unknown costs are not statistical confidence intervals.
Negative/null outcomes and no observed break-even remain reportable results.

## 7. Roles, access and exposure controls

No named human roster, independent-review signature or external custody evidence is
present in this candidate. The historical exposed AI author is not an independent
provider author/curator. The following is a proposed access policy, not a statement
that blinding already occurred. Public A/B tasks/answers cannot be blinded retrospectively.

| Role | Before separately authorized unsealing | After authorized unsealing | Restricted material / required evidence |
| --- | --- | --- | --- |
| Investigator | Candidate, protocol, this decision package; custody metadata rather than sealed contents by default | May authorize staged releases and review deviations/results | Declare any prior sealed access; sign exact candidate/docs/parameters and a separate release decision |
| Independent provider author | Common vocabulary/schema and domain design brief; only custodian-authorized access to their own sealed provider if already assigned | Maintain provider-local documentation/manual provenance within boundary | No held-out task instances, expected answers or target mappings from evaluators; author exposure/conflict declaration |
| Onboarding contributor | Visible training materials, frozen interfaces and permitted tools; no sealed provider/tasks/answers | Approved provider docs/API and condition-specific artifacts only | Task answers, evaluator interventions/native decoder implementation and post-run adjudication unavailable during integration; timed sessions and access ledger |
| Evaluation curator / sealed-material custodian | May independently prepare sealed task templates/oracles and custody hashes; own sealed-provider access only if explicitly assigned and declared | Bind/review native observer from authoritative reference behavior; seal expectations before subject execution | Do not author subject integration or disclose answers to contributor; record every exposure and independent reviewer |
| Auditor | Public candidate, hashes, role declarations, custody/access metadata | Read-only audited patches, sealed expectations and raw results in controlled review after task lock | No silent mapping repair or answer transfer; signed parity, observer and change-audit findings |

A custodian may already know sealed material; that is compatible only with declared
separation from generic implementation/onboarding. This task does not inspect it.
No role receives access merely because this package exists. Use least-privilege storage
outside the public repository for sealed material; record hashes/authorization without
copying protected contents. Expected answers never enter registry/catalog/contracts.

Proposed append-only **exposure ledger**, separate from time ledger: event ID, participant
and role IDs, artifact class/path or custody identifier, SHA-256/version, first-access
UTC timestamp, access purpose, authorizing decision ID, allowed use, actual access
channel, prior external exposure declaration, conflicts, reviewer and linked corrections.
Unknown prior dates stay null with an explicit unknown declaration. Log provider docs,
manuals/mappings, task inputs, expected answers, observer code, outputs and feedback;
include AI/tool sessions and recipients. Hashes and self-declarations support auditing,
not proof of no off-platform exposure. No fabricated access events are created here.

Require independent review of neutral B/C content, condition-A obligations, domain task
predicates, native field interpretations and invariants, allocation/schedule and change
allowlist **before** execution. Signed reviews identify reviewer, relevant expertise,
artifact hashes, findings, conflicts and date. Provider author and curator should be
separate from integrator; observer reviewer should not merely approve their own code.

If staffing forces overlap: declare it before access, seek investigator disposition,
use a second external reviewer where feasible, restrict author privileges and preserve
all resulting limitations. Do not relabel overlap “blind” or “independent.” If a generic
author/integrator already knows the intended holdout/tasks, disqualify that material as
uncontaminated confirmation, or explicitly classify the run exploratory. Investigator
approval cannot retroactively remove exposure. An undecided conflict blocks release.

## 8. Limitations and threats to validity

The apparatus has one bounded event-creation capability, closed transforms, local
loopback APIs, trusted single-writer fixtures and single-action goals. It is not a
planner, LLM comparison, general transition reasoner, full E1 benchmark, multi-step
pilot or operational deployment. External APIs are outside the current transport
boundary. Future provider requirements may simply be unsupported, which must remain
a result rather than trigger an undisclosed generic repair.

Shared authoring and public diagnostics threaten independence and task generality;
shared oracle/fixtures threaten common-mode correctness. Format conversion helps parity
but does not prove independent authoring reliability. Small provider counts prevent
population-level economics claims; missing historic labor prevents complete observed
cold-start inference. Repeated tasks and overlapping families do not increase provider
sample size. In-process hash chains detect limited tampering but cannot authenticate
human effort or defeat a full ledger rewrite by a trusted writer. Candidate hashes
establish byte identity, not completeness of model semantics or scientific approval.

## 9. Explicit investigator decisions

All decisions in the linked JSON remain null/pending. Before authorizing any release,
require a dated detached signature binding this package hash, candidate commit/tag,
manifest/source digest, exact approved settings and rationale, deviations and reviewers.
Approval of a technical artifact is distinct from satisfaction of protocol Gate 1 and
from authorization to unseal. A decision may accept the apparatus while withholding
confirmatory readiness. Human choices still required:

1. Accept/reject exact technical candidate and this documentation revision.
2. Resolve single-action scope versus protocol multi-step requirement; no quiet scope reduction.
3. Obtain independent parity/manual/native-observer/task reviews and adjudicate findings.
4. Assign named roles, custody, conflicts and exposure controls; determine whether a truly uncontaminated holdout exists.
5. Select primary cost allocation and declared sensitivity policies; approve timers, assistance/missingness and maintenance accounting.
6. Approve task distribution, counts, seeds, archived ordering/roster, budgets, supervisor/reset evidence, thresholds, stopping and analysis plan.
7. Approve addition-only integration/change-audit boundary from the held-out protocol and treatment of generic defects. No changes to resolver, validation, shared interfaces/prompts, goal truth or task-specific repair are permitted under the original candidate.
8. Decide separately whether Gate 1 is satisfied and whether/when to authorize release. This package grants neither.

## 10. Final approval checklist

PASS means an evidenced technical fact, FAIL a known unmet substantive requirement,
and PENDING an unapproved/unestablished decision. PASS does not imply investigator sign-off.

| Gate | Status | Evidence / closure needed |
| --- | --- | --- |
| Exact commit/tag/clean entry/manifest identity | PASS | §1 and entry commands §2 |
| Archived source, artifacts and M4 historical preservation | PASS | `candidate_v2.py --verify/--verify-history`; 104/74 source members and 14 historic files |
| Pinned versions and final source/wheel/restoration records | PASS | §2, environment and three final-stage logs |
| Controlled A/B three-condition correctness and B/C typed parity | PASS | §3 evidence matrix and 120-case subtest matrix |
| Native mapping separation and decoy detection | PASS | §4; D15 and native unit tests |
| Complete multi-step pilot coverage required by protocol | FAIL | §6; existing apparatus explicitly single-action; resolve before full confirmatory readiness |
| Independent manual/neutral semantic review | PENDING | Signed content/validation review; same-author tests insufficient |
| Independent curator/task/native observer review | PENDING | §4 and §7 signed predicates/storage interpretation review |
| Human labor and complete historic cold-start measurements | FAIL | §5; nulls cannot be repaired historically; approve prospective measurement and qualified reporting |
| Cost policy/collector/maintenance and missingness approval | PENDING | §5 policy choice and timer practice |
| Task counts/seeds/schedule/roster/metrics/statistics approval | PENDING | §6, archive actual schedule before release |
| Demonstrated reset and outer-deadline operational procedure | PENDING | §6; 60 s is not enforced in `run_case` |
| Named roles, exposure declarations, conflicts and sealed custody | PENDING | §7; no current independence/blinding evidence |
| Provider-local addition boundary and generic-defect handling approval | PENDING | §9; [held-out protocol](HELD_OUT_EVALUATION_PROTOCOL.md) |
| Detached investigator approval of exact candidate and review revision | PENDING | [decision record](SCIENTIFIC_FREEZE_DECISION_RECORD.json); all approval fields null |
| Confirmatory Gate 1 / separate unsealing authorization | PENDING | Protocol §9 plus all applicable above gates; not granted |

**Ready for investigator review as a decision package. Not approved, not ready for an
unqualified confirmatory claim, and not authorization to inspect or unseal Provider C.**
