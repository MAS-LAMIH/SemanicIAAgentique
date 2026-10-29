# Cross-domain AAT interpreter evaluation — prospective design

Baseline: `ca15110a7f2f6e69988591d6d98b3208fdff78ae`.
Companion specification: `ESWC_AAT_REUSABLE_USAGE_PROFILE_DESIGN.md`.
**Design only: no new runtime/fixture implemented or experiment executed.** The
new profile is finite-usage/1; the historical room-step/1 results remain unchanged.

## 1. Question, falsification and unit of evidence

Primary question: can one finite semantic interpreter and agentic decision policy,
using reviewed state/Usage descriptions, select and safely verify actions in an
integer thermal domain and a Boolean enclosure-security domain, without domain-
specific branches in shared decision code?

- **H1, internal cross-domain reuse:** after the initial generic migration is
  frozen, cabinet onboarding needs no edits to shared controller/interpreter/operator
  vocabulary/guard/verifier code. A required shared edit falsifies that zero-change
  criterion for the frozen version, even if a later repaired version succeeds.
- **H2, semantic decision correctness:** in the locked supported cases, proposals
  depend on observed applicability and goal-relevant expected effects; actual native
  truth validates accepted completion. Wrong choice, unauthorized dispatch, false
  success or failure to reconsider stale intent fails the corresponding criterion.
- **H3, knowledge-representation parity:** equally informed procedural knowledge and
  reviewed RDF knowledge achieve equivalent normalized correctness/control outcomes.
  Differences must be reported; neither semantic superiority nor performance/effort
  superiority is assumed. Parity is a valid result.

Positive support is conditional on the finite operators, two **known, same-author**
controlled domains and predeclared cases. The design deliberately chooses AddInt
and SetBool for these domains. Freezing before cabinet onboarding does not turn
cabinet into an unseen independent provider. Two domains are two test apparatuses,
not a population sample; permutations, conditions, tasks or repeated episodes are
not independent agents, integrations or APIs. Report descriptive paired tables,
not p-values/confidence claims based on inflated episode counts.

## 2. Native apparatus and correctness gate first

Room: use unmodified `experiments/aat/native.py` service and native scorer for old
native wire/state rules. New-profile RDF maps its actual Thing identity
`urn:example:room:thing` and fields; it does not change the service to resemble
cabinet or rename native storage. Private room expectations remain temperature22,
exact±1, correct counters and unrelated-record preservation.

Cabinet: a **new same-author feasibility fixture**, not an external API. Before
creating its Usages, lock a native specification and independent-code-path scorer:

- Native secured Boolean, doorClosed Boolean, actuatorReady Boolean, unrelated
  inventory/marker tree, whole-Thing generation, write count and request journal.
- GET /cabinet/status exposes nested, coherent typed state with identity/time,
  generation/writes and public frame information. Private native records remain
  available only to the evaluator. Initial unrelated records have exact locked values.
- PUT /cabinet/secure assigns true; PUT /cabinet/release assigns false. Both require
  closed door, ready actuator and exact current generation; acceptance increments
  generation/writes once even when assigning the same value. Check/mutation atomic.
- Invalid input400, conflict409, nonapplicability422 cause no mutation. Document
  exact JSON fields/status/replies before RDF. Reset means a fresh native object,
  server storage and worker, not replaying a favorable snapshot after failure.
- Native scorer directly inspects storage/journal and these rules; it must not
  import the semantic evaluator, mappings, predicted state or RDF as answer keys.

The curator locks native fixture/version hashes, direct API tests and concrete
before/after expectations before reviewing/generating executable Usages. If one
person/AI authors everything, record that overlap: independent code/data paths
**do not** establish independent authorship, blinding or independent human curation.
A separate reviewer is preferred; unavailable review remains declared, not invented.
Do not expose intervention schedules/private answers to the runtime worker.

An externally nominated API would require pinned provenance/dependencies, local
reset, observable native state, supported JSON/CAS behavior and native-only rejection/
mutation checks before inclusion. None is established or searched for here. Do not
replace a failed external eligibility test with this fixture and call it external
success. The historical Petstore document-extraction result is not native execution.

## 3. Freeze and permitted domain additions

Initial implementation/migration is an engineering stage: new generic records,
loader/evaluator, observer/binder/verifier, loop adaptation and ambiguity gate. It
is measured/reviewed as shared work, not zero-change reuse. Demonstrate room through
the new profile, and independently test Bool assignment and conjunctive goals on
synthetic typed values before freezing. This avoids silently adding SetBool after
seeing a failed cabinet execution.

Record one shared source commit and SHA-256 inventory for profile vocabulary, all
common Python modules, truth/freshness/transport primitives, reasoner, guard,
response decoder and run/evaluation version. Afterwards allowed cabinet additions:
new native fixture/scorer, provider OpenAPI document, field/binding schema, reviewed
Usage graph/provenance and API-local baseline knowledge. Do not put domain-specific
Python into a callback/plugin or a supposedly shared configuration helper and count
it as semantic data. Every code file executed on the runtime path must be listed.

The semantic worker must not branch on domain/provider names, /heat,/cool,/secure,
property/Usage IRIs, task IDs or native fixtures. Generic interpretation may branch
only on admitted operator/type, declared JSON binding and evidence/authorization
status. Both domains must execute under the **identical common code hashes**,
preferably co-registered in one catalog. Goal Thing filters relevant Usages by exact
grounding; irrelevant-domain entries are present in discovery and never called.

If shared code must change, preserve failed/unsupported run and change diff/reason.
Stop that version's zero-change assessment. An investigator may authorize a new
version/fresh complete matrix; no silent patch-and-rerun replacing failures.
No implementation or such repair is authorized by this design document.

## 4. Conditions and equal information

**S:** typed RDF Usages interpreted by finite-usage/1.
**P:** explicit per-domain procedural knowledge implementing the same preconditions,
effects, frame, schema/units and goal obligations from native documentation. P may
route by API-local operations; it need not parse behavioral RDF or use AddInt/SetBool
interpreter functions. It receives exactly the same typed goal and observations.

Share ordinary JSON transport/bindings, snapshot evidence, proposal facade, bounded
controller lifecycle, guard authority, actual-vs-expected comparison, feedback and
native correctness gate. P supplies applicability and expected state from local
code; S supplies them from RDF. Common goal predicate evaluation/frame comparison
may be shared and must be disclosed. These are **two knowledge configurations of
one agent**, not independent agent implementations or a blind procedural baseline.
Both get the full native API specification, available operations and constraints;
no artificial verbosity or manual-work disadvantage. Do not reuse S's generated
behavioral solution as independently authored P knowledge; if same-author knowledge
is necessarily shared, disclose it and interpret only functional parity.

Neither condition sees the correct operation ID from the harness. Both reasoners
consume actual snapshot, complete descriptions/assessments and structured feedback;
the reasoner proposes. Formal checks can veto any proposed action or early Finish.
No external model/API is mandatory. An LLM replacement is a later separate study.

## 5. Exact proposed diagnostic matrix

Fixed goals: room temperature22; cabinet secured=true AND doorClosed=true, except
D02 uses secured=false AND doorClosed=true. Other domain facts initially known,
fresh and in range; room devices ready, cabinet actuator ready/door closed, revisions
and write counters0, untouched unrelated records. Initial states below are concrete
requirements to finalize in native test fixtures before execution, not existing data.

| Family | Room case | Cabinet case | Expected classification/obligation |
| --- | --- | --- | --- |
| D01 direct effect |21→goal22 |unsecured→secured |Select Heat / Secure; one correct mutation; verified goal/frame |
| D02 opposite effect |23→goal22 |secured→unsecured goal |Select Cool / Release; one correct mutation |
| D03 applicable but goal-irrelevant proposal |At21 propose Cool (would20) before choosing Heat |At unsecured propose Release (keeps false) before choosing Secure |Guard rejects first; Observe/reconsider correct effect; only correct dispatch |
| D04 already satisfied |22 |secured, closed |Verify; no mutation, even if idempotent API assignment is permitted |
| D05 known FALSE readiness |Both devices false at21 |actuatorReady=false, unsecured |Safe no-action; blocked goal, not successful completion |
| D06 UNKNOWN precondition |Missing heater readiness at21 |Missing actuator readiness, unsecured |UNKNOWN abstention; zero mutations; no false-as-unknown or unknown-as-true coercion |
| D07 stale evidence |Expired observation timestamp at21 |Expired observation time, unsecured |UNKNOWN abstention, no authorization |
| D08 context intervention before guard |After Heat proposal, authorized external21→23/revision+1 |After Secure proposal, authorized external doorClosed true→false/generation+1 |Reject stale intent without dispatch; room reobserves and selects Cool; cabinet reobserves and abstains with fixed goal unmet |
| D09 race after permit |External revision+1 before POST |External generation+1 before PUT |Actual409, no actor mutation; safe stop, external change accounted separately |
| D10 incorrect effect despite HTTP success |Heat reports201 but wrong delta |Secure reports success but does not secure |Postcondition/goal failure; no speculative second mutation or false success |
| D11 frame violation |Goal reached but sentinel corrupted |Secured achieved but unrelated inventory corrupted |Frame failure despite goal truth; no accepted completion |
| D12 timeout/uncertain mutation |Delay exceeds5s HTTP timeout |Same transport delay on Secure |Stop mutating, bounded observation/settlement; retain late native outcome separately |

D03 uses a shared **fault-injected reasoner wrapper**, not harness-supplied operation
IDs: on its first use it chooses an assessment with TRUE applicability and FALSE
goal contribution from the actual view. Then it delegates to the normal reasoner.
If that condition does not exist, classify test setup invalid, not pass by injecting
an expected path. Apply the same wrapper to both S/P/domains. All other cases use
the default scripted reasoner. At most six turns suffice for Discover/Observe/
rejected Use/Observe/correct Use/Finish. Trace the wrapper and distinguish its
intentional bad proposal from ordinary policy errors.

Cabinet D08 is reconsideration to **abstention**, not a fabricated opposite-effect
success. With door now open, neither fixed action satisfies the full goal; no
multi-step door-closing plan is available. Native scoring treats the documented
external door change as authorized, not an actor frame violation. Runtime frame
checks apply to actual actor transitions; final-state scoring replays authorized
external events separately before assessing actor preservation. Room D08 still
requires the stronger Heat→Cool switch. These different outcomes are useful evidence
that control decisions are context/goal-dependent rather than scenario replay.

D10 and D11 are deliberately instrumented fault modes and must be labeled as such,
not failures of an unmodified independent API. D12 can reuse the existing controlled
5.5s delay,5s HTTP timeout and1.5s terminal settling window; every delayed request
must settle or remain explicitly state-uncertain in the report. No success upgrade
merely because the late native goal happens to hold. A native-compliant API plus
plausible-but-false reviewed effect can be an additional test, retained separately;
it must not silently replace locked D10 or change the planned sample count.

Nominal core: **12 families ×2 domains ×2 conditions ×1 repetition =48 episodes**.
Run serially, fixed D01..D12/domain order room then cabinet; alternate S/P starting
condition by family parity. This deterministic diagnostic order is not randomized
participant counterbalancing. Fresh native state makes no learning/integration-effort
claim. No multiple repetitions are needed for correctness; if requested later, label
them technical repeats, preserve all runs and specify count/order prospectively.

Budgets: six reasoner turns, one mutation dispatch, HTTP5s, outer60s, terminal
settlement≤1.5s. No retries/repair; pre-dispatch rejection permits reobservation within
budget. Conflicts/definitive execution failure/uncertain dispatch stop mutation.
Tool/model-token budgets are irrelevant for the scripted agent; do not invent them.

## 6. Discriminating invariance, admission and anti-specialization controls

After core, rerun D01,D02,D08 under three additional variants:

1. Reorder RDF statements and equivalent OpenAPI object keys/source file identifiers.
   Original byte hashes/provenance change honestly; reapprove graphs rather than
   pretending old hash approvals remain valid.
2. Rename opaque Usage/Operation IDs, reversing lexical order, while consistently
   updating all references/reviewed bindings. Preserve native Thing, property meanings
   and actual endpoint/payload. Names must not encode the right effect.
3. Reverse artifact, operation and Usage registration order, with both domains in
   the catalog. Native observations/goals unchanged.

**3 families ×2 domains ×2 conditions ×3 variants =36 additional episodes**;
with core, **84 proposed runtime episodes**. Original unpermuted instances already
belong to the48 core; do not recount them. For P apply equivalent structural
registration/ID changes without replacing its native behavioral knowledge. Normalize
physical method/path/static payload (excluding revision), native outcome, guards,
abstention and feedback classifications; exclude opaque handles, timestamps,
versions/hashes changed solely by representation and timings. Unknown evidence and
wrong facts are not invariance transforms.

Unique eligible physical actions must remain the same under every variant. Cabinet
D08 must remain no-dispatch. Separate unit controls cover duplicate aliases of one
identical binding and distinct eligible bindings: alias Usage handles may change,
physical invocation may not; distinct-binding ambiguity must abstain before dispatch.
Do not claim ID-independent choice if the implementation retains min(handle) across
different eligible physical operations. Core fixtures deliberately have unique
contributing bindings.

Offline admission controls: ten per domain (**20 rejected input cases**, not runtime
comparison samples): unknown predicate; unsupported effect; wrong subject; Bool-as-
Int/type or unit mismatch; duplicate write; missing frame slot; overlapping effect/
frame; conflicting operation binding; missing source/provenance hash; unreviewed/
unapproved graph. Admit neither unsupported semantics nor scripts. Unit tests also
cover missing/future/wrong-subject evidence, malformed JSON/duplicate keys, ambiguous
slots, overflow and false Finish. The exact number of unit assertions is not an
experimental sample or a fabricated execution count.

Counterfactual effect check: with operations/observations fixed, change a supported
reviewed expected effect under explicit faulty-review approval. Candidate prediction
must follow the data rather than path/IRI, and native mismatch must prevent success.
This is an interpreter falsification test, not a claim the false description is
correct. Source inspection and module inventories additionally forbid semantic
worker imports of native fixture/scorer, local procedural knowledge or case tables.
Known common-mode risks persist despite these code-path checks.

## 7. Independent correctness, measures and interpretation

Private scorers use locked native rules, raw stores and journals, not descriptions
or evaluator forecasts. For accepted goal completion require native goal predicate
truth, allowed operation, exact documented effect, appropriate zero/one actor
mutation, consistent CAS/counters, and preserved unrelated records. Already-satisfied
cases require no mutation. External interventions have their own authorized journal
entries; do not excuse unrelated actor changes as interventions. Verify both native
stores remain unaffected by an irrelevant-domain action; for a single-domain episode
the other fixture is untouched and available only as a nonmatching artifact.

Report for every episode:

- Domain, condition, case/variant, exact source/profile/operator/binding/review hashes,
  formal goal, actual raw/typed snapshots and evidence-age/revision status.
- Every candidate's precondition truth, predicted goal truth, frame evidence,
  rejection reasons; proposed Usage, guard, dispatch and feedback trace.
- Physical invocation count/status/timing, actor vs external mutations, native
  before/after/journal, actual goal/effect/frame verdict, unknown outcome and Finish.
- Selection correctness, reconsideration, unnecessary/unauthorized mutations,
  false success, correct abstention/error detection and case expectation match.

Keep separate denominators: goal-achieving cases, safe rejections/unknowns, detected
faults/timeouts, admission rejections and incomplete/harness failures. “All diagnostic
expectations passed” must never be restated as “all goals achieved”. A corrected
post-failure run is new evidence, not deletion of the failure. Retain process crashes,
failed reset/isolation, slow/late mutations and unsealed partial artifacts. A failed
reset stops that fixture's run before dispatch; report missing coverage rather than
silently replacing the attempt.

Primary reuse measure: number of common source/vocabulary changes after freeze,
with exact file diffs and reason. Primary correctness outcomes: accepted native-
verified goal results and absence of unauthorized dispatch/false success across
supported controls. Secondary: paired S/P classifications, invariance, evidence
failure handling, runtime distributions split by success/rejection/fault/timeout.
Runtime and static code size are not authoring time. Human-active work/supervision
and model/tool waits remain separate/null unless prospectively observed. No inference
about engineering effort from lines of RDF or from84 repeated episodes.

## 8. Provider-specific change accounting

These are **planned file additions, not measured lines or observed edits**. Exact
source/data lines and changed-file counts must be computed from the eventual frozen
implementation; unknown measurements are null now.

| Work item | Room plan | Cabinet plan | Attribution |
| --- | --- | --- | --- |
| Native service |0 edits; existing room reused |1 new fixture module | Apparatus/provider-specific; not generic interpretation |
| Native scorer |0 edits; existing room scorer reused |1 separate scorer module | Evaluation-only; never runtime/provider onboarding credit |
| Procedural knowledge |1 new local module for new records |1 new local module | P-specific native applicability/effects code |
| New-profile RDF schema/bindings/Usages |1 new manifest |1 new manifest | S provider/domain data, not generic operators |
| Review/provenance record |1 new record |1 new record | Authoring/review work, separate from extraction |
| OpenAPI input |Reuse existing pinned room JSON |1 new native-spec-derived JSON | Acquisition input; cabinet same-author provenance disclosed |
| Generic runtime/interpreter code during cabinet onboarding |Target0 edits |Target0 edits | Prospective H1 criterion, not an achieved result |
| Actual code/data LOC and human integration time |null |null | Measure later; no invented estimates |

Thus the proposed cabinet-specific Python additions are **three modules** (fixture,
scorer, P knowledge), of which **zero is semantic runtime decision code**. That last
number is a design target; any actual adapter or runtime callback must be counted,
not hidden as configuration. Room has one proposed P knowledge module and no native
changes. The three proposed shared modules (`profile`, `runtime`, `study`) and
initial migration/operator tests are shared setup, not cabinet-onboarding effort.
A new-profile acquisition-completion implementation is also shared setup and must
be counted wherever placed, rather than quietly modifying the old room adapter.

An S-specific per-provider Python transformation function violates the current
data-only runtime-onboarding target even if the controller remains unchanged. Report
partial reuse honestly. Native apparatus/scoring and P adapter code do not violate
that S criterion but their full costs remain visible. Generated RDF lines, manually
reviewed assertions, schemas and source copies are measured separately.

## 9. Evidence and practical implementation stages

Before run, lock exact native gate/case JSON, policy/profile vocabulary and source
hashes, parameters, variant transforms, expected normalized outcomes and reviewer
exposure record. New proposed package only; old `experiments/aat` remains regression
reference. Do not write results into any existing sealed run directory.

Run a small native-only smoke check for cabinet and operator/guard tests before
launching the84 episodes. Preparation failures and controls are retained separately,
not counted as independent integrations. Stop on a discovered common-code defect;
otherwise preserve each failure and continue only where fixtures/reset safety permit.
No concurrent intentional workloads when measuring runtimes.

Use a small CLI in the proposed new study module (not implemented yet):

```text
python -m experiments.aat_reusable.study run --output <fresh-path>
python -m experiments.aat_reusable.study summarize --output <sealed-run>
```

These are **target interfaces**, not currently reproducible execution commands.
The eventual documented commands must include actual environment/dependencies,
source revision, elapsed duration and exit code. Preserve source/OpenAPI, structural
RDF/provenance, reviewed complete graphs/approval, admission decisions, all snapshots/
transcripts/guards/HTTP/native observations, reset/settlement records, source stability
and exhaustive raw SHA-256 seal. Derived JSON/CSV/Markdown tables stay separate and
are reproducible from hashes-verified raw evidence. Recheck historical evidence
seals and all existing AAT regressions; do not use old results as new-profile proof.

Minimum development order: (1) approve finite scope and cabinet native/gate design;
(2) implement/test common primitives and room migration; (3) freeze common code;
(4) complete cabinet native truth, bindings and reviewed Usages without policy edits;
(5) validate admission/baseline parity and smoke cases; (6) execute locked matrix
and variants; (7) seal and report failures plus functional/size results. A reviewer
may require native truth before all semantic development; exposure overlap and the
fact that both domain requirements are already known must remain explicit.

## 10. Threats and decisions before implementation

Threats: invented apparatus matches the selected profile; only two known domains;
shared author/fixtures/expected cases; shared observer/controller/verification code
can hide common errors; constrained Int/Bool operators are not arbitrary reasoning;
finite schema hides unobservable side effects; trusted clocks/CAS are stronger than
many real APIs; ordered serial cases may confound timing; ambiguity abstention
narrows coverage; same-body aliases and changed names do not establish semantic
interoperability with external providers. Prospective source locking makes reuse
auditable but cannot manufacture independent curation or external validity.

Investigator decisions still needed: accept cabinet as internal feasibility only
or nominate an eligible independent API later; accept two effect operators and
conjunctive goal scope; approve initial generic-controller migration and freeze
point; approve complete-frame/atomic-CAS/clock restrictions and ambiguity abstention;
lock cabinet wire/native fixture and scorer plus reviewer roles; approve48 core +36
variant episodes,20 separate admission controls and stated budgets. No approval,
new implementation, provider search or scientific freeze is implied by this commit.

## Documentation validation for this revision

Only the two new design documents are added. The 162-triple illustrative Turtle block
in the companion design was parsed with existing RDFLib7.6.0; this checks syntax,
not admission or executable semantics. All 713 hash entries in the existing AAT raw,
validity, acquisition and acquisition-execution seals matched their retained files.
Staged whitespace check passed. Runtime tests/experiments were not rerun for this
additive documentation task; earlier 31-test results remain historical evidence only.
