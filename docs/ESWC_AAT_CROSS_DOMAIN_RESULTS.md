# Frozen reusable Usage interpreter: controlled cross-domain results

**Implemented, frozen and executed `finite-usage/1` across two different domains.**
The same semantic interpreter/controller handles integer room temperature and Boolean
cabinet security using reviewed RDF and declarative JSON bindings. Cabinet onboarding
made **zero edits to frozen common code**. All **88 diagnostic expectations passed**:
**48 verified successes, 24 safe abstentions, 16 detected failure/uncertain outcomes**.
These categories are different outcomes, not 88 successful goals. Twenty malformed-graph
controls rejected admission; no false success or condition/invariance difference.

This is internal cross-domain reuse in **same-author controlled fixtures**, not
external-API generalization, independent human semantic review, general planning or
LLM performance. The original room native service is unchanged. No V3/V4, tutorial,
prior runtime/profile or historical evidence was modified. New work is local only.

## Implementation and mandatory chronology

| Point | Exact commit / evidence |
| --- | --- |
| Requested design baseline | `08ba35c4017bf116e171144c09caeb338ad3e818` |
| Phase A common implementation and room migration | `b53cea2f021ddc60a9e6c456da83f8a95a109a6a` |
| Mandatory engineering freeze + native cabinet specification and gate | **`ed0e010d9ba56ef551944b991b6c788cc40de06b`** |
| Cabinet native/scorer/knowledge/RDF onboarding, no common edits | `bff253a2a2c2306a2474b31f5db5e2b3cc8bedba` |
| Evaluation-only source-key permutation evidence correction | `95fec661ca716dd670798711c0ecfde776ba8bb6` |
| Actual full run source | **`95fec661ca716dd670798711c0ecfde776ba8bb6`**, clean at start |

Phase A passed seven focused tests, including actual room HTTP execution, synthetic
SetBool **records and RDF**, conjunctions, UNKNOWN/type handling, invalid graphs,
wrong effects/frame, guarded reconsideration, permits and ambiguous candidates.
Five separate subprocess room episodes passed before freeze (cold, hot, already
satisfied, and S/P final smoke with irrelevant first proposal/reversed registration).
The final smoke ran the committed implementation. Initial development tests failed
because RDFLib Namespace.lower/upper resolve to Python string methods; bracket
predicate access corrected this **before freeze**. Failed and corrected logs remain
in `phase-a/`; no initial failures were relabeled successful.

The freeze committed the source hashes **before** cabinet service, scorer, bindings,
Usages or local knowledge were created. `freeze/cabinet-native-spec.json` and
`freeze/native-case-expectations.json` locked native action rules, cases, statuses,
mutations/goal/fault expectations, budgets, variants and 88 runtime records. These
are native specifications/answers, not Usages generated from runtime forecasts.
No freeze point was redefined. Post-freeze corrections were confined to the private
evaluation driver's source-serialization variant, before the full matrix, so actual
object-key permutations are retained instead of sorted away. No common policy code
changed. No failed zero-change criterion or runtime repair was required.

`freeze/runtime-freeze.json` is a **machine-readable engineering source freeze**,
not investigator scientific-freeze approval (`scientific_freeze_approval: null`).
It hashes nine shared repository files (new package initializer, profile, runtime,
worker and ontology; unchanged semantic_action initializer/model/oracle/transport),
195 actually loaded stdlib/dependency files, the existing room provider sources,
and locked cabinet specification/gate. Both domains and all conditions checked
those shared hashes before/after every attempt. Dependencies were not installed or
changed. Exact file inventories and environment-specific dependency paths are retained.

## Metamodel and executable semantics

New isolated package: `experiments/aat_reusable/`. No retrofit of room-step/1.

- `profile.py`: immutable grounded Artifact catalog, Slots, Operations, Usages,
  Conditions/Effects, Goal, Snapshot and Candidate records; closed RDF loader and
  finite typed evaluation. Artifact represents Thing; Usage links an Operation to
  grounded pre/post ContextTemplates. User supplies Goal; expected facts are not
  inserted into actual observation state.
- `runtime.py`: generic typed observer, candidate assessment, replaceable
  `Reasoner.propose(View)` Protocol/default scripted strategy, formal authorization,
  one-use permits, declarative JSON invocation, actual postcondition/goal/frame
  comparison, structured feedback and bounded observe–reason–act–observe loop.
- `worker.py`: loads approved catalogs, selects the exact grounded Goal Thing,
  exposes both artifacts in discovery evidence, runs the common loop, records loaded
  modules. Semantic workers import no fixture/scorer/local procedural knowledge.
- `ontology.ttl`: separate `urn:eswc:aat:usage:1#` finite vocabulary, with original
  AAT conceptual relations/types retained under `urn:eswc:aat:prototype:1#`.
- `data_tools.py`: offline RDF authoring helper only. It translates explicitly
  authored JSON specifications, **not automatic behavioral acquisition**.
- `harness.py` / `study.py`: private process/barrier/native scoring and export;
  never imported by the worker. Native cabinet and API-local modules are separate.

Effect operators are exactly **AddInt** (strict bounded Int, delta±1, explicit unit)
and **SetBool** (strict Boolean assignment). Preconditions are nonempty conjunctions
of Equal/IntRange; goals nonempty typed Equal conjunctions. Missing/stale/ill-typed
facts yield UNKNOWN, known false values remain FALSE, conjunction uses FALSE-dominant
three-valued truth. Bool is never an Int. Opaque bounded JSON is frame-only, compared
canonically; no scripts, arbitrary expressions, OWL imports, SPARQL or search.

Implementation encoding choices: Slots use closed kind tags Int/Bool/JSON rather
than xsd datatype declarations; expressions are named RDF nodes rather than optional
anonymous syntax sugar. These choices are pinned in the manifest. The admission
loader rejects unconsumed triples, malformed links/frames, unsupported operators,
wrong units/subjects/types, ambiguous schema pointers and unreviewed graphs, and
requires the supplied approved byte hash. Source/review hashes must be present and
well formed; retention validation checks every graph's declared source/review hash
against the actual retained native source/review records. The loader itself relies
on the explicitly approved graph hash rather than accessing private native files. Hashes/review flags are not proof that effects are true or reviewers
independent. No acquisition-to-new-profile completion converter is claimed: the old
acquisition/completion pipeline and its evidence remain preserved separately.

Slots partition exactly into written targets and explicit frame; all required
before evidence is known before dispatch. The matcher predicts a one-step complete
goal, not merely progress. Multiple distinct eligible bindings or conflicting
expected states abstain with AMBIGUOUS. No path/name/IRI priority is used. Aliases
of one consistent binding may use lexical handles without changing physical action.
Reobserve before authorization; reject stale snapshot; bind goal/graph/revision and
expiry in a single-use permit; actual server CAS closes the final race. Verify
observed state (including frame), counters+1, timestamp, goal and reply echoes.
One failed/uncertain mutation stops further dispatch. Finish reobserves; model/tool
success or HTTP success alone cannot report goal satisfaction.

Runtime binding subset remains approved loopback HTTP, JSON objects, static GET
observation and POST/PUT invocation, bounded object JSON Pointers, a static body
with one permit-revision placeholder and declared response echoes. Original V3
HTTP transport is reused unchanged (5s/no redirects). Integer CAS applies to a whole
Thing; both native APIs implement it atomically. The new profile is intentionally
not a general external API transport/observation adapter.

## Two domains and independent native checks

| Aspect | Room | Cabinet |
| --- | --- | --- |
| Native service | Existing `experiments/aat/native.py`, unchanged | New `cabinet_native.py`, same-author feasibility fixture |
| State/effect | Integer Celsius;±1 | secured Bool; assign true/false |
| Goal | temperature22 | secured=target AND door_closed=true |
| Operations | POST /heat and /cool | PUT /cabinet/secure and /cabinet/release |
| Observation | Flat GET /state | Nested GET /cabinet/status |
| Request CAS | expected_revision | guard.generation |
| Precondition | Relevant readiness + integer range | Door closed AND actuator ready |
| Frame | Readiness and unrelated sentinels | Door, readiness and unrelated inventory/marker |
| Private scoring | Unchanged native room score | `cabinet_score.py`, no semantic interpreter/runtime imports |

Cabinet source implements the previously locked native specification: strict Boolean
assignment, generation/write+1 even for repeated same-value assignment,400/409/422
no-mutation rejections and unrelated-state preservation. Its separate scorer uses
raw stores/journal/native rules, not the RDF effect or canonical prediction as the
answer. External door/revision interventions are separately journaled; an authorized
external frame-fact change is not counted as an actor violation. Every episode starts
fresh instances of **both** native stores/servers and a fresh worker. The irrelevant
store's full before/after state remains unchanged.

## Locked matrix and actual outcomes

Two knowledge conditions: S interprets RDF; P uses explicit API-local applicability/
expected-state code. Both use the same typed goals, public observations, structural
bindings, reasoner strategy, evidence/guard/verification services, budgets and private
native gate. P uses no RDF precondition/effect interpreter; a test changes RDF
thermal effects while P predictions remain unchanged. P does read catalog bindings/
Usage handles; views/catalogs contain the same reviewed descriptions. This is a
**procedural-knowledge versus interpreted-knowledge comparison**, not independently
implemented agents or semantic superiority. Shared goal/evidence/verifier code and
same-author truth are common-mode risks, despite separate expected-state calculation.

Core48 episodes:12 families ×2 domains ×2 conditions. Additional36: D01/D02/D08 ×2
domains ×2 conditions ×3 variants (statement/source-key order, opaque Usage/Operation
identifiers, actual catalog/slot/operation/Usage registration reversal). Four extra
conflicting-candidate episodes (2 domains ×2 conditions) satisfy the explicit ambiguity
requirement; the freeze gate locked this total88 before cabinet onboarding. Thus
84 originally proposed core/variant episodes plus4 declared controls, not84 inflated
independent integrations. Every attempt uses six turns, at most one mutation, HTTP5s,
outer60s and terminal settlement≤1.5s; no planning, repair or speculative retries.

| Family/control | Actual result under both conditions | Goal-success interpretation |
| --- | --- | --- |
| Cold room / secure cabinet | Correct Heat / Secure | Verified |
| Hot room / release cabinet | Correct Cool / Release | Verified |
| Applicable but goal-irrelevant first proposal | Generic fault-reasoner wrapper uses actual candidate evidence; guard rejects, then correct action | Verified after reconsideration |
| Already satisfied | Fresh verification, no mutation | Verified; not a creation/action success |
| FALSE preconditions | NO_DIRECT_MATCH, no dispatch | Safe abstention |
| Missing readiness / stale observations | UNKNOWN_CONTEXT, no dispatch | Safe abstention |
| Pre-guard intervention | Room stale Heat rejected→Observe→Cool; cabinet stale Secure rejected→Observe→no action with open door | Room verified; cabinet safely blocked, fixed goal unmet |
| Post-permit CAS conflict | Actual409; zero actor mutations; stop | Detected rejection |
| Wrong effect, HTTP success | POSTCONDITION_FAILED | Detected failure |
| Goal reached but unrelated state corrupted | POSTCONDITION_FAILED | Detected frame failure, not success |
| Timeout / late mutation | UNCERTAIN_MUTATION; no second dispatch; late native effect retained | No accepted success |
| Conflicting candidates | AMBIGUOUS before dispatch | Safe abstention |

The ambiguity controls deliberately provide conflicting reviewed-knowledge claims
(in RDF and equivalent local test functions), not a claim the native APIs genuinely
have these alternative effects. Their extra frame-effect expectations conflict while
both predict the goal; the common guard refuses to choose. No actor mutation occurs.
D03 likewise is an explicitly injected bad reasoner proposal based on available
assessments, not a harness-provided correct operation ID. All other cases use the
default scripted reasoner. Intervention hooks check stage/turn only, not handle.

Actual terminal counts:

| Status | Records |
| --- | ---: |
| SUCCESS |48 |
| NO_DIRECT_MATCH |12 |
| UNKNOWN_CONTEXT |8 |
| AMBIGUOUS |4 |
| CONFLICT |4 |
| POSTCONDITION_FAILED |8 |
| UNCERTAIN_MUTATION |4 |

48 verified successes comprise **44 verified actor transitions +4 already-satisfied
no-ops**.24 safe abstentions comprise12 no-match,8 unknown and4 ambiguous.16 detected
failure/uncertain outcomes comprise4 CAS rejections,8 effect/frame failures and4
timeouts. Native goal facts hold in56 records, including4 frame-corruption and4 late-
timeout outcomes that are **not** accepted.56 total actor mutations include44 verified,
8 deliberately wrong/frame-fault transitions and4 late effects.60 mutating HTTP
attempts include4 no-mutation CAS conflicts. Native applicability/revision breaches
and false success claims are zero; do **not** describe all effects as safe merely
because authorization breaches are zero. Eight injected harmful transitions remain
explicit failures. Every irrelevant store stayed untouched; every reset/settlement
check passed. No unexpected full-matrix failure or replacement/rerun occurred.

Condition parity and invariance compare physical calls (method/path/body), guard
codes, native before/after, counters, goal/frame/acceptance; exclude trace IDs,
source hashes changed by representation, timestamps and durations. Both comparison
lists are empty. Multiple technical episodes/representations are not independent
provider or agent samples. No statistical generalization or confidence interval
from these 88 observations is claimed.

## Code reuse and actual size

Physical line counts, including comments/blanks, from tested sources (not effort):

| Component | New Python source lines |
| --- | ---: |
| Shared profile/records/loader/evaluator |225 |
| Shared observer/controller/guard/binder/verifier/reasoner |149 |
| Shared worker |28 |
| Shared initializer |1 |
| Room procedural knowledge |21 |
| Cabinet native fixture |62 |
| Cabinet native scorer |17 |
| Cabinet procedural knowledge |19 |
| Offline RDF authoring helper |36 |
| Evaluation-only harness + study |219 |

The cabinet-specific Python additions are exactly **three modules/98 lines**:62
fixture,17 scorer,19 P knowledge. **Zero S-specific Python adapter or shared-code
edit** was required. P's runtime intentionally imports its19-line native knowledge
module, just as room P imports21 lines: these are domain-specific execution-path
code and are reported, not hidden as generic code. Shared S code contains no room/
cabinet identities, operation-path/property-name or native-fixture branches.
Unchanged neutral primitives live in older modules that also define legacy types;
only Truth/time/freshness/HTTP services are called, not calendar behavior.

Room reviewed RDF is121 lines, authoring JSON140 and review5; cabinet RDF112,
authoring JSON135 and review6. These data are manually reviewed behavioral knowledge,
not automatically inferred or evidence of reduced authoring time. Initial common
migration, two-operator development, shared ontology and evaluation infrastructure
are setup, **not zero onboarding work**. Human-active and supervision measurements
were not prospectively captured and remain null. No additional runtime dependency
or model service was introduced. The experiment is source-checkout execution;
no new wheel-distribution claim is made.

## Regressions, failures retained and integrity

All **165 offline tests pass**, across seven suites:

| Suite | Passed |
| --- | ---: |
| Existing semantic_action (V3) |87 |
| Existing v4 |20 |
| Existing v4_pilot, fresh output |6 |
| Existing v4_experiment |3 |
| Existing goal_choice |9 |
| Existing aat |31 |
| New aat_reusable |9 |

Initial legacy-pilot invocation omitted its documented fresh-output environment
variable: three of six tests refused existing historical attempt paths with
FileExistsError. This preserved previous evidence. The initial failure log remains;
rerunning with documented `V4_PILOT_FOCUSED_OUTPUT` in a new directory passed all6,
with new focused traces retained separately. No old test/source/evidence was fixed
or overwritten. Tutorial root files execute live web/Groq demonstrations at import
and are not offline regression assertions; they were deliberately not invoked.
Those live demonstrations are not claimed validated by this result. One packaging
whitespace warning is retained: a trailing space in the initial failed test log;
the original evidence bytes were preserved rather than cleaned after the fact.

New common tests passed before freeze; post-onboarding native tests and six cabinet
smokes passed. Four ambiguity smokes and20 admission smokes passed before the final
run. These 15 preflight subprocess episodes (5 Phase A +6 onboarding +4 ambiguity)
are retained separately, not added to the88 matrix or described as independent
implementations. The initial RDFLib-access test failures and the legacy output-path
refusal are disclosed development/command rework, not hidden experiment reruns.

Actual matrix: exit0, serial/no concurrent test workloads, **95.379137s** whole loop.
Worker times include interpreter/import/supervision, not pure action latency. Median
worker SUCCESS0.164514s; timeout5.177563s. Median whole-attempt SUCCESS0.623349s;
timeout6.060677s includes settlement/server shutdown. Full min/median/max by status
are in validation JSON. One sample per controlled case/configuration cannot support
runtime superiority; fixture shutdown/polling dominate these timings.

New run raw seal and derived regeneration are verified. Historical AAT/validity/
acquisition/acquisition-execution seals retain713 checked entries. Every file that
existed at baseline08ba35 remains unchanged; source differences are additions only.
The full run's13,617 tracked file hashes stayed unchanged during execution. The
nine frozen repository and195 dependency/stdlib hashes still match. Plain hash
records and module inventories demonstrate source/data paths, not security isolation
against a hostile host or authenticated independent human signatures.

## Evidence and reproduction

`docs/artifacts/eswc_aat_cross_domain/` contains:

- `freeze/`: committed source manifest, native specification and pre-Usage gate.
- `phase-a/`: initial/corrected tests and actual pre-freeze room worker/native evidence.
- `run-001/raw/`: both reviewed graphs/specs/reviews for every attempt, scoped graph
  approvals, coherent observed snapshots, candidates/proposals/feedback/guards,
  permit-driven actual HTTP logs, full native before/after/intervention journals,
  independent scoring, two-store reset/isolation, subprocess logs/module inventories,
  controlled faults, all20 malformed RDF graphs/admission decisions, source inventory,
  completion status and exhaustive SHA-256 seal.
- `run-001/derived/`: hash-verified JSON/CSV/Markdown outcomes and summary.
- `validation/`: all test/command logs, initial refused invocation, fresh legacy
  pilot traces, onboarding/ambiguity/admission smokes, timing/size/environment and
  final preservation/source checks.

From repository root, with existing Python3.12.14/RDFLib7.6.0 environment:

```sh
PYTHONPATH=src .venv/bin/python -m experiments.aat_reusable.study run \
  --output /tmp/aat-cross-domain-fresh

PYTHONPATH=src .venv/bin/python -m experiments.aat_reusable.study summarize \
  --output docs/artifacts/eswc_aat_cross_domain/run-001

PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/aat_reusable -v
```

Actual run destination was `/workspace/aat-cross-domain-run-001`. Existing output
paths are refused. Run checks freeze hashes and seals incomplete attempts in finally;
hard kills may leave partial/unsealed evidence that must not be called complete.
Installed module hashes pin this environment; a deliberately different Python/
dependency installation must be reported as a different environment, not silently
accepted as the same freeze. Summary regeneration needs only retained raw files,
not a model/API or active provider. Full offline regression commands/exit codes are
retained; use a fresh explicit legacy-pilot output as documented.

## Interpretation and limitations

This demonstrates an operational Agent–Artifact–Thing/Usage loop across Int and
Bool domains with context-dependent choice, feedback-driven reconsideration,
formal veto, observed postconditions and native verification. Cabinet onboarding
satisfied the frozen zero-shared-change criterion. No unsupported cabinet requirement
or runtime exception workaround was needed under this restricted profile.

Both domains were known when selecting AddInt/SetBool and both native fixtures are
same-author; source freezing is an engineering check, **not held-out external
validation**. P shares controller, typed observations/goals and verifier, and both
oracles/case expectations share authorship. Common bugs/omitted world effects remain
possible. Only one Thing per admitted graph and one mutation per episode; no goal
formation, arbitrary reasoning, multi-step planning, remote authentication, arbitrary
JSON transformations, genuine clock/CAS discovery or general API acquisition.
Reviewed behavior can still be wrong; this study tests bounded recognition and
fault detection, not semantic truth certification. Existing evidence remains valid
within its original scope; no scientific freeze or broad semantic superiority is
claimed. New work remains local, with no push or merge.
