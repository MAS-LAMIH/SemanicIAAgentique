# Minimal agentic Agent–Artifact–Thing/Usage execution

**Implemented and executed:** an isolated finite metamodel integrated into a
replaceable-reasoner observe–reason–act–observe loop. Heating and cooling have
opposite effects, not just different API names. Both semantic and equally informed
procedural controller conditions pass all **22 diagnostic episodes**. No semantic
accuracy advantage, general planning or external-API generalization is established.

Reviewed design: `75d1a2f7ac888229399e47aa653504ddba452d03`.
Tested implementation: `7d0126113dcb00b72391fcdf87668ebfad1d8e99`, clean at run start.
This results commit adds data/documentation only; implementation and historical
V3/V4, tutorial, manuals, vocabularies and evidence remain unchanged.

## Implemented components and original concepts

One package, `experiments/aat/`, contains:

- `model.py`: immutable Thing, Artifact, Operation, Usage, ContextSnapshot,
  StateGoal, Candidate, Proposal, Feedback, ControllerView and Permit records.
- `rdf.py`: finite RDF catalog/loading and closed structural validation. Operation
  has a binding/wire-schema identity; Usage separately links the grounded artifact
  and operation to pre/postcondition ContextTemplates, readiness/bounds, signed
  delta, explicit revision/mutation increments, frame and review provenance.
- `runtime.py`: observer, data-driven finite applicability/effect matcher,
  structured `Reasoner` Protocol/default `ScriptedReasoner`, bounded controller,
  formal authorization, single-use permits, guarded transport and postcondition/
  goal verification. Goal and observed contexts are serialized separately in RDF;
  an Agent resource pursues the Goal and references actual observed contexts.
- `native.py`: controlled room API, private native state/journal and native-spec-
  based scorer. No semantic-loader/Usage/runtime imports.
- `study.py` / `__main__.py`: private synchronization/evaluation parent, fresh
  worker processes, native checks, sealing and JSON/CSV/Markdown export. Worker
  branch never imports fixture/scorer/study modules.
- `data/`: versioned experimental ontology, reviewed room graph and an external
  graph/native-source hash review record. Review is same-author, not independent
  human curation. Namespace: `urn:eswc:aat:prototype:1#`.

The operative relationships follow the original report's §4.2/§5.2 Usage model;
artifact/thing separation follows §4.1, consistent grounding §6.1. Evidence ages,
permits, atomic revisions and native scoring are explicit experimental extensions.
This does not claim the original report implemented a general planner.

The tutorial supplies the reasoning/tool/observation feedback pattern. Its original
Groq/global-tool implementation is unchanged and not imported. The new loop injects
`Reasoner.propose(view)`: structured observations, complete reviewed Usage records,
candidate reasons/predictions and prior structured feedback go in; one typed proposal
comes out. The default chooses an eligible goal-contributing Usage itself. The
harness passes no selected handle/operation or expected answer. A proposed early
Finish or applicable-but-noncontributing action cannot bypass formal checks.

Unchanged V3 primitives reused: `Truth`, timestamps/freshness (`oracle.current`),
`HTTPTransport`/`ApiResult`, `supervise` and `settle_and_capture`. The calendar-only
Registry/Executor/Goal/oracle were not renamed or forced to handle temperature.
The new room evaluator/catalog is a separate closed profile, not a duplicate
calendar engine or an extension of the frozen vocabulary. Existing registry
regressions passed. V4 was not retrofitted into the metamodel.

## Actual main episode

Raw semantic episode: `run-001/raw/episodes/e005/` (procedural counterpart e006).
Its transcript records these actual reasoner/tool turns:

1. Discover the admitted artifact, operations and distinct Usages.
2. Observe 21°C and current readiness/revision.
3. Propose Usage43 (HeatOne). A deterministic external barrier changes native
   temperature to 23°C/revision 1 before authorization. Guard reobserves and returns
   STALE_PROPOSAL, with structured context feedback. **No heat POST occurs.**
4. Reasoner receives feedback and proposes Observe; actual 23°C is read.
5. Reasoner proposes Usage71 (CoolOne): predicted 22°C contributes to the goal.
   Guard authorizes current context; executor POSTs `/cool` with expected revision 1.
   Native temperature becomes 22°C, revision 2, one mutation.
6. After fresh postcondition/goal/frame checks, reasoner proposes Finish. Controller
   independently rechecks actual state before reporting SUCCESS.

Operation/Usage identifiers are intentionally opaque. Preconditions/effects come
from reviewed data, not those names. The driver changes temperature on the first
proposal/authorization barrier in the designated cases without reading the proposed
handle. It never supplies the next correct choice. Revision checking is atomic
inside the service, closing races after the guard's last observation.

## Controls and outcomes

Every case ran once under each condition with fresh native state. Normalized
choices/outcomes match across conditions; detailed rows are in the derived table.

| Case | Behavior under both conditions | Accepted goal satisfaction |
| --- | --- | --- |
| R01 cold 21°C | Heat once, observe/verify 22 | Yes |
| R02 hot 23°C | Cool once, observe/verify 22 | Yes |
| R03 intervention 21→23 after Heat proposal | Reject stale Heat, feedback/Observe, Cool once | Yes |
| R04 already 22°C | Observe/verify; no mutation | Yes |
| R05 neither device ready | No eligible action; no mutation | No, safely blocked |
| R06 readiness unknown | Never assume TRUE; no mutation | No, unknown |
| R07 stale observations | No authorized mutation | No, unknown |
| R08 revision changes after permit | Actual POST gets 409; zero mutations; stop | No, conflict |
| R09 5.5-second service delay | Actual five-second HTTP timeout; no retry; late native change retained | No verified invocation success |
| R10 wrong +2 postcondition despite 201 | Wrong temperature detected; stop | No |
| R11 forbidden sentinel mutation despite 201 | Frame violation detected even though temperature reaches 22 | No |

Aggregate: **8 accepted satisfactions** (6 successful mutations + 2 already
satisfied), 14 POST attempts, 12 native mutations. Native final temperature equals
the goal in 12 episodes, including late effects and frame-fault controls that are
not accepted. **Zero unauthorized mutations and zero false success claims.**
Four deliberately injected bad native transitions (two wrong deltas, two sentinel
corruptions) were detected and retained. Do not describe them as zero unsafe effects:
CSV `unsafe_mutations` measures native applicability/revision authorization breaches;
`incorrect_native_effects` separately records these injected harmful transitions.

Three standalone admission probes rejected missing effect data, an unreviewed
Usage and an unapproved graph hash before execution. Their exact malformed graphs,
reasons and hashes are retained. They are schema/admission controls, not unfair
comparative episodes with broken information given only to the semantic agent.
The toy API's operations and native gate were source-defined; this is not an
independently authored provider generalization or automatic behavior acquisition.

## Evidence, data-path separation and reproduction

Retained area: `docs/artifacts/eswc_aat/`. `run-001/raw/` contains input/negative
RDF graphs and review hashes, admission decisions, case inventory, per-episode
public worker inputs, semantic contexts/goal RDF, observed JSON state, proposals,
feedback/final decision, guard decisions, HTTP results, native before/after/journal,
reset and recovery records, process logs, source/dependency hashes and raw seal.
`derived/` contains regenerated JSON/CSV summary and Markdown table. Validation
logs are separate. No unexpected harness/experiment failure occurred; failed and
uncertain service outcomes remain explicitly unsuccessful in the raw records.

All **336 sealed raw files** match SHA-256 and the seal lists every raw file.
All **12,840 pre-existing/source files** match pre-run hashes, including the original
35 readiness frozen hashes. All 22 reset checks passed, all subjects exited and all
native work settled before final capture. Worker inputs contain only policy,
origin, reviewed graph/hash and goal; no native handles, case IDs or intervention
schedule. Fixture/scorer modules are absent from all 22 workers' module inventories.

The private scorer reads native state and known server transition rules, not RDF
postconditions or the runtime's forecast as answer keys. It separately accounts
for authorized external temperature/revision changes and actor mutations. This is
software/data-path separation, not independently authored truth or blinding.
Source/evaluator sharing and host filesystem access remain common-mode risks;
the trusted deterministic worker is not an adversarial sandbox.

Actual full run command (exit 0, **25.004311 s** command wall time;
24.380366 s episode-loop time), serial without concurrently launched tests/work:

```sh
PYTHONPATH=src .venv/bin/python -m experiments.aat run --output /workspace/aat-execution-001
```

Use a new output path to reproduce with the existing environment. Python 3.12.14,
RDFLib 7.6.0, pyparsing 3.3.3, jsonschema 4.26.0 were recorded; no new mandatory
runtime dependency or external model service was introduced.

```sh
PYTHONPATH=src .venv/bin/python -m experiments.aat run --output /tmp/aat-new-run
PYTHONPATH=src .venv/bin/python -m experiments.aat summarize --output /tmp/aat-new-run
```

Regenerate retained tables without invoking the agent/API:

```sh
PYTHONPATH=src .venv/bin/python -m experiments.aat summarize --output docs/artifacts/eswc_aat/run-001
```

The summary validates raw hashes before export. New executions refuse existing
output directories. Failed Python runs seal incomplete evidence in `finally`;
a hard kill may leave unsealed partial data, which must not be relabeled complete.

## Tests and scientific interpretation

Before the clean-source experiment:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/aat -v
# 10 passed, 3.826 s
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/semantic_action -p test_registry.py -v
# 15 existing regressions passed, 34.105 s
```

Tests cover immutable/separate records, RDF admission, data-driven effects under
opaque IDs/reordering, procedural independence from RDF behavior fields, native
heat/cool and atomic conflicts, guard veto of a wrong reasoner proposal, single-use
permits, ReAct feedback/observation/rechoice, public worker interface, premature
Finish, native frame faults and distinct context/goal RDF. Unit fixtures are
temporary; official experiment traces and all admission-control graphs are retained.

The result operationalizes a finite part of the original metamodel **inside an
agentic control loop**: actual observations and reviewed Usage meaning guide
proposals; formal checks remain authoritative; feedback can change the proposal;
verified state, not model confidence or HTTP success, gates completion. Unlike the
previous EventCreation experiment, both increasing and decreasing temperature are
native executed effects.

There is **no observed functional advantage over the equally informed procedural
condition**. Both share the controller, reasoner interface, transport and verification
criteria. The baseline encodes native conditions/effects in Python and uses structural
operation bindings; it does not read the RDF pre/postcondition data. These are two
knowledge/guard configurations, not independent agent implementations. Shared
comparison machinery makes parity unsurprising and does not measure integration
or maintenance effort, which remains unmeasured.

The evaluated reasoner is scripted, not an LLM. Its replaceability and veto
boundary are tested, but model-backed reasoning quality, objective interpretation
or autonomous goal formation were not evaluated. This is one controlled room,
one-step ±1 effects, Celsius integers, fixed JSON API and local catalog discovery.
It is not general OWL reasoning, SPARQL planning, multi-step search, dynamic Web
artifact discovery, multi-agent concurrency or external-API generalization.
OpenAPI structural acquisition remains a planned extension, not an implemented
feature of this minimal task. Review hashes document provenance, not proof that
semantic assertions will always be correct; actual postconditions still require
verification. Timings include process/import/synchronization/shutdown and recovery,
with one sample per condition/case; infer no latency superiority or human effort.
