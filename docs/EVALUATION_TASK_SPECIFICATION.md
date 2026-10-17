# Public prospective apparatus tasks — proposal pending approval

Authority: user-supplied frozen ESWC protocol, especially §§4–9. RQ1/E1 is primary;
B/C semantic information parity is fixed. These tasks are authored from formal
calendar goal predicates and diagnostic interventions, not from the subject
manual's declared effects. They are not Provider C tasks or a sealed answer set.

Source of truth: semantic_action.evaluation_tasks.proposed_tasks/task_sheet and
its retained docs/evaluation_tasks_v1.json. Every task has a formal Goal with an
explicit start/end/title, preserve_other_events=True, evidence age 30 seconds,
empty initial fixture storage, and one intended newly stored event. The goal
values are domain task inputs; the manuals never supply oracle answers. Cases
change permissions/storage/wire evidence only as explicitly listed. Both visible
providers are independently reset per condition and repetition.

## Families and independent expectations

| ID / family | Initial state or intervention | Acceptance/rejection and failure classification |
| --- | --- | --- |
| D01 valid match | Writable, empty, requested 09:00–10:00 UTC | Execute once; both verifiers achieve; verified |
| D02 different names | Same goal, visible APIs' distinct operation names | Same correct result; no name-based equivalence |
| D03 different formats | Equivalent +02:00 goal instants, ISO versus integer-ms APIs | Lossless conversion; both verifiers achieve |
| D04 misleading effect | Familiar operation name declares only a reservation record | Reject without mutation; safe incompatibility |
| D05 false permission | Native permission explicitly false | FALSE; zero mutation calls |
| D06 unknown permission | Native permission null | UNKNOWN; zero mutation calls |
| D07 stale permission | Old permission timestamp | UNKNOWN; zero mutation calls |
| D08 missing permission evidence | Remove permission-read timestamp | UNKNOWN; zero mutation calls |
| D09 untransformable input | No supported local encoding / unavailable shared input source | Reject without mutation; unsupported integration |
| D10 precision loss | Start includes one microsecond | A-provider supports it; B-provider rejects rather than round; same across conditions |
| D11 unsupported transition | Reservation effect cannot establish stored-event goal | Reject without mutation; unsupported transition |
| D12 API error | Controlled 500/503 response, no state change | One attempted call; no goal achieved; API failure |
| D13 false HTTP success | 201 without storing event | HTTP succeeds; both reject achievement |
| D14 incorrect properties | Service stores wrong actual title | Both reject achievement |
| D15 incorrect output map | Wrong real stored title plus decoy advertised title; subject map reads decoy | Runtime may accept; native verifier rejects; final unverified mapping discrepancy |
| D16 forbidden side effect | Service creates an additional record | Both reject; raw snapshot preserved |
| D17 stale observation | Post-execution wire timestamps stale | Runtime fails evidence; native may establish actual state, final remains unverified |
| D18 missing observation | Post-execution wire timestamps absent | Same distinction: actual state versus mandatory runtime evidence |
| D19 duration constraint | Requested interval 09:00–12:00 | A-provider executes correctly; B-provider rejects its two-hour bound |
| D20 grid constraint | Start 09:05 | A-provider executes correctly; B-provider rejects its quarter-hour restriction |

For each family, raw pre/post native storage and mutation-call counts are required,
alongside runtime permission evidence, actual API response and complete fresh
read-back where available. Native expectations use actual field interpretations
from fixture storage code, never the subject output map. The same goal oracle
checks canonical native observations in all conditions. Preserved raw state also
reveals forbidden changes to existing records outside the canonical projection.
The expected feasibility differences in D10/D19/D20 come from independently read
fixture specifications, not from a subject manual choosing its own correct label.

Acceptance is not simply a passing test: reported fields separate compatibility,
TRUE/FALSE/UNKNOWN when actually probed, mutation count, HTTP success, runtime
verification, native verification and their conjunction. Safe rejection is a
correct apparatus outcome for a negative but not successful integration of an
otherwise feasible positive. A static rejection never invents state evidence.
Missing observation is not proof that the state failed to change. An intentional
negative returning the expected false verdict is a passed diagnostic, not a
successful action. CLI exit 0 means diagnostic_passed, not verified=True.

## Proposed counts, order and budgets

- 20 public single-action tasks × 2 visible providers × 3 conditions = 120 paired
  condition/provider/task executions per apparatus sweep. One sweep is tested.
- Propose 3 repetitions for apparatus stability (360 executions); repetitions
  are not new provider samples. These are not confirmatory trials on Provider C.
- Propose seed 20271017 and counterbalanced six permutations ABC, ACB, BAC, BCA,
  CAB, CBA across task/provider/repetition blocks. Seal the actual schedule and
  generator version before release; use isolated initial states. No code infers
  a superiority result or changes order based on favorable observed outcomes.
- Existing transport uses 5-second HTTP timeouts. Propose no automatic retries,
  no planner/repair iterations, and a 60-second outer run budget. The latter is a
  proposed supervisor policy, not currently enforced by run_case itself.
- Propose 90 active human person-minutes and 300 elapsed minutes per incremental
  provider/condition onboarding attempt; record waits/runtime separately, pause
  active timers for inactive waiting, and classify exhausted budgets as censored.
- Stop affected confirmatory execution on unexpected mutation after false/unknown
  preconditions, source hash changes, oracle discrepancy not a planned control,
  or condition parity mismatch. Preserve all evidence/costs; do not silently patch.
- Finish all predeclared tasks unless a safety/operational stop is triggered.
  No favorable-results early stop, hidden retry or removal of failed cases.

All numeric settings above require investigator approval. They are operational
proposals, not changes to frozen scientific questions. The PDF's 20-case pilot
also includes multi-step goals. The current apparatus is single-action only:
these 20 diagnostics do not satisfy that full pilot fragment. Approve this bounded
engineering review scope; implement/review multi-step apparatus in a later
pre-confirmatory milestone or explicitly register a deviation. No LLM planner
or full confirmatory benchmark is introduced here.

## Independence, roles and measurements

The software native observer is separate from contract mappings, but all new
code/tasks were authored by the same AI contributor with prior exposure to A/B
manuals. That is not organizational independence. An independent curator must
review the formal predicates, raw storage interpretation, decoy-map control and
future sealed task generation before evaluation. The evaluator must not return
expected answers to the integrator. Public A/B diagnostics are apparatus tests,
not blinded integration evidence. Never transplant their answers into discovery.

Provider is the primary unit for onboarding-cost generalization. Report matched
condition outcomes and all failures, unknowns and unsupported positives; do not
pretend 360 executions are 360 providers. Human costs remain null without direct
observation; automated task timing is recorded separately. Proposed cold-start
allocation and maintenance accounting are in COST_MEASUREMENT_PROTOCOL.md.

## Reproduce a visible-provider diagnostic

```sh
. .venv/bin/activate
python -m unittest discover -s tests/semantic_action -p test_pre_freeze.py -v
python -m semantic_action.evaluation --provider b --condition A --task D01 --output-dir /tmp/m41-local --ledger /tmp/m41-events.jsonl
python -m semantic_action.evaluation --provider b --condition B --task D15 --output-dir /tmp/m41-wrong-json --ledger /tmp/m41-events.jsonl
python -m semantic_action.evaluation --provider b --condition C --task D15 --output-dir /tmp/m41-wrong-rdf --ledger /tmp/m41-events.jsonl
```

Use new output directories. D15 should print runtime_verified=true,
native_verified=false, verified=false and diagnostic_passed=true. These examples
require no key, model or external service. They never configure or inspect a
held-out provider.
