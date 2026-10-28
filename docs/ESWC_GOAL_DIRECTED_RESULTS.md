# Executed goal-directed artifact action selection

**Result:** a bounded agent now computes its own grounded action choice from an
explicit goal and observed context, reconsiders after revocation, and executes
through unchanged V3 guards. The equally informed procedural selector achieves
the same results. No functional advantage for semantic descriptions is observed
in this diagnostic experiment.

Implementation commit: `cc1155c778f3f42b33982124731119211eb92964`, based on
reviewed audit/proposal `39f315e125aeb27337948429968940e3b4bd2db7`.
The official run started with a clean tree at that implementation commit.
Only `experiments/goal_choice.py` and `tests/goal_choice/test_goal_choice.py`
were added for implementation. No frozen package, vocabulary, A/B integration or
historical evidence was edited. This results revision adds documentation/data only.

## What was implemented

`Objective` contains an unchanged V3 event Goal and allowed artifact identities,
**no operation ID**. `agent` has at most two decision cycles and one dispatched
mutation. `assess(..., 'semantic')` discovers candidates through existing
`Registry.resolve`, consumes finite effect/applicability/constraint checks,
reads context through existing bindings, and grounds effects to the allowed
artifact targets. Selection sorts **eligible** candidates by `(artifact identity,
operation identity)`; no provider preference or registration-order heuristic.
`Registry.execute` receives the ID computed by the policy and freshly checks it
again. This differs from the earlier caller-selected demos and singleton evaluations.

The semantic policy is deterministic and uses JSON v2 manuals; this is not a
JSON/RDF representation comparison. Both actions instantiate EventCreation but
have different ground effects (new event in A versus new booking in B), permission
facts and provider constraints. The goal-to-effect fragment is intentionally finite,
not arbitrary predicate entailment or planning.

The procedural policy uses existing `CalendarLocal`, `BookingLocal`, `LocalExecutor`,
local descriptions and provider-specific validations/read paths. It receives the
same goal, public bindings, observable information, budgets and barriers. It
encodes native operation meaning in ordinary code; it is not deprived of semantic
information in the informal sense. It imports no registry/semantic contract loader
in its worker, which focused tests verify.

Both policies check current state **before** choosing. After a successful guarded
creation, both also reobserve both artifacts and check aggregate matching/event
preservation before claiming satisfaction. A native evaluator in the parent process
then independently checks both raw stores and identifiers, without using the
semantic description maps for native decoding.

## Actual execution

The run was serial, without concurrently launched tests/intentional workloads.
Python 3.12.14, RDFLib 7.6.0, jsonschema 4.26.0, pyparsing 3.3.3;
Linux 6.18.55 x86_64 / glibc 2.41. Exact metadata, dependencies and all source
hashes are retained in `run-001/raw/source.json`.

Actual command (exit 0; automated command wall time **35.332525 s**):

```sh
PYTHONPATH=src .venv/bin/python -m experiments.goal_choice run --output /workspace/goal-choice-execution-001
```

Runner episode-loop elapsed: 34.750550 s. Output was outside the checkout to
preserve a clean implementation identity. It was then copied byte-for-byte to
`docs/artifacts/eswc_goal_choice/run-001/`. For a new authorized reproduction:

```sh
PYTHONPATH=src .venv/bin/python -m experiments.goal_choice run --output /tmp/goal-choice-new
PYTHONPATH=src .venv/bin/python -m experiments.goal_choice summarize --output /tmp/goal-choice-new
```

The output path must be new. To regenerate retained publication tables without
rerunning agents/APIs or altering raw data:

```sh
PYTHONPATH=src .venv/bin/python -m experiments.goal_choice summarize --output docs/artifacts/eswc_goal_choice/run-001
```

## Results: 11 cases × 2 policies = 22 episodes

Each table row below occurred once under each policy with identical normalized
choices, native calls, goal truth and verification outcome. These are 22 diagnostic
episodes of two selector policies sharing a decision shell, not 22 independent
agents, integrations or trials of independently authored implementations.

| Case | Context / intervention | Choice(s) under each policy | A/B POST counts | Independent outcome |
| --- | --- | --- | --- | --- |
| G01 | A writable, B unavailable for mutation | A | 1 / 0 | One correct A event |
| G02 | A unavailable, B writable | B | 0 / 1 | One correct B event |
| G03 | Both writable | A via documented identity tie-break | 1 / 0 | One valid A event |
| G04 | Neither writable | Abstain | 0 / 0 | Both stores unchanged; goal unachieved |
| G05 | Choose A; revoke A and grant B before dispatch | A intent → fresh rejection → B | 0 / 1 | One correct B event; unrelated records unchanged |
| G06 | A permission unknown, B false | Abstain; UNKNOWN never becomes TRUE | 0 / 0 | Both stores unchanged |
| G07 | A context timestamp stale, B false | UNKNOWN_CONTEXT | 0 / 0 | Both stores unchanged |
| G08 | Both writable; selected A response delayed 5.5 s | A; stop on HTTP timeout, no alternate | 1 / 0 | Late correct event; no usable returned ID or verified invocation success |
| G09 | Goal event already exists in A | SATISFIED_EXISTING; no choice/creation | 0 / 0 | Existing event/ID verified; no duplicate |
| G10 | Only A is allowed by goal; A false, B true | Abstain despite B being applicable | 0 / 0 | Forbidden target never used |
| G11 | B writable but service returns 201 without storage | B; definitive execution failure; stop | 0 / 1 | No goal event; no false achievement claim |

“Unavailable” in G01/G02/G04 means permission denies mutation, not a disconnected
endpoint. The artifacts remain readable. G07 checks stale evidence, not a simulated
network partition. G08 is an actual five-second HTTP transport timeout with a
late mutation, **not** the 60-second outer process deadline. Every child completed;
all native services settled before final capture and the next episode.

Aggregate results:

- **22/22** correct choice/abstention sequences and case expectations; no parity
  differences. All 44 artifact reset assertions passed.
- **8 newly created** events independently verified, plus **2 already-satisfied**
  goals verified without mutation: **10 accepted satisfactions**, not 22.
- **8 safe abstentions**, **2 uncertain invocations with late native goal truth**,
  and **2 definite no-storage execution failures** are retained as distinct outcomes.
- 12 total mutating HTTP attempts, at most one per episode; **0 excess mutation
  requests, 0 unnecessary native mutations, 0 unexpected state changes and
  0 false achievement claims**. In G05 A receives zero POSTs after revocation.

The remaining native events in G08 bring final state satisfaction to 12, while
accepted verified satisfaction remains 10. No timeout is promoted to success just
because the independently observed state later looks correct. In G09 there is no
invocation result: the recorded ID comes from current observation and is checked
against native state, not fabricated as a returned creation ID.

The experiment treats the goal as a desired state that may already hold, as
required by the execution task. New-record semantics of V3's creation oracle are
used only when creation is attempted. The outside-core aggregate goal wrapper
handles the already-satisfied case and allowed destination set; neither is falsely
attributed to frozen V3's single-artifact Goal.

## Evidence and independent correctness boundary

`run-001/raw/episodes/e001`…`e022` retain isolated worker inputs/outputs, every
candidate's assessment/rejection reasons, timestamped context, selected intents,
recheck resolutions, guarded invocation/wire traces, native before/after snapshots,
pre-mutation snapshots, intervention journal and recovery observations. The parent
owns fixture objects and expected case outcomes; the worker input has only
`event`, `allowed_artifacts`, `actions`, `policy`. Both policies receive identical
public binding information. A common decision/release barrier exists in every
case, so its presence does not reveal the permission-flip schedule.

The G05 hook changes permissions after the first intent but before release.
A separate raw snapshot records that authorized external change; final permission
preservation is compared against the post-flip state. Event preservation is checked
against initial native contents. No permission changes are silently attributed to
an agent, and unrelated changes cannot be excused by this intervention.

The evaluator reuses `native_verifier.capture/adjudicate` and evaluator-owned
native `_calendar/_booking` decoding, plus aggregate raw-record preservation,
exact matching/allowed destination/ID checks, call budgets and exact revision
increments. It does not obtain truth from the agent's choice or description's
output mapping. Raw metadata changes, extra/deleted events and unauthorized
permission changes are checked. `native_creation_checks` may correctly be false
in an already-satisfied episode because that sub-oracle requires a **new** ID;
the separate aggregate state predicate verifies G09 without creation.

This is software/data-path separation, **not independent human curation or an
adversarial sandbox**. Policies and evaluator share this development context and
some goal/verification code. The trusted worker does not receive native handles,
case expectations or control parameters, and does not import the native verifier;
tests check this interface and module separation. The host filesystem and experiment
source are shared and were not claimed inaccessible to hostile worker code. No
LLM, AI-agent session, nested CLI or model authentication was used.

All **273 sealed raw files** match their SHA-256 inventory. All **12,539 source/
pre-existing tracked files** match their pre-run hashes. Summary regeneration
from the sealed evidence succeeds. The original 35 readiness baseline hashes
also remain unchanged, including V3/V4 runtime/vocabulary and A/B integrations.
No Radicale/candidate searches or historical experiment changes occurred.

## Validation

Before the clean-source experiment:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/goal_choice -v
# 9 tests passed, 7.596 s
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/semantic_action -p test_registry.py -v
# 15 existing registry tests passed, 34.126 s
```

Focused tests cover the no-operation-ID objective, permission-flip rechoice,
registration-order independence, already-satisfied duplicate prevention, native
extra-mutation rejection, no alternate after uncertain/failed dispatch, aggregate
post-observation before success, consuming the required semantic effect, and raw
hash tampering. The deliberately injected extra-mutation unit case is expected to
fail native correctness; it is not an unreported successful episode. Unit fixtures
use temporary directories; the full 22-episode experiment retains all raw files.
Development/final test logs are retained separately from official execution.

No unexpected experiment/harness failures occurred. The uncertain and failed
service behaviors above are deliberate controls, reported as such rather than
counted as successful creations. Code/schema fingerprints and test logs identify
the implemented source; there is no dependency/runtime change to the frozen code.

## Scientific interpretation and limitations

This closes a specific gap identified by the model audit: an agent now observes,
filters, chooses and reconsiders through executable code instead of receiving a
caller-selected operation. G02 contradicts a fixed A preference; G05 requires a
new choice from changed context; G10 requires goal-target reasoning beyond mere
permission; G08/G11 require honest post-action outcome handling.

**There is no observed correctness advantage over the procedural selector.**
Both branches have the same information and achieve parity. The semantic branch
consumes shared finite action descriptions; the procedural branch implements the
same knowledge with local rules. Source reuse is visible, but integration effort,
maintenance savings and scalability were not measured. Human-active and supervision
time remain unknown, not reconstructed from automation durations.

Only two known, shared-author controlled artifacts, one event capability and a
finite target-set goal fragment were used. Discovery is enumeration of supplied
registrations, not open-Web discovery. Effects are grounded event creation, not
arbitrary action types or a transition-language planner. Selection uses a stable
identity tie-break, not utility optimization. The two policies share a loop/goal
checker, and independent human authorship is zero. One execution per case does not
estimate stochastic variation or provide independent provider/agent samples.

Complete fresh state from both artifacts is required to rule out duplicates; this
conservatively blocks when global context is incomplete even if one operation's
local precondition might be true. Network partition handling, dynamic provider
addition, competing agents, arbitrary goals, multi-step search, compensation and
uncertain-outcome repair are not demonstrated. Existing V3 canonical verification
is reused and can share common-mode errors with the evaluator. Raw native/frame
checks reduce but do not eliminate this risk.

Worker and whole-episode wall times are in CSV/JSON. They include process/import,
read/check, synchronization, shutdown and (where applicable) recovery overhead;
Python timed-process waiting can quantize completion detection. Ordering is fixed
semantic then procedural, with one sample per case/policy. Do not infer parser,
planning efficiency or statistically meaningful latency superiority from these
values. The contribution demonstrated here is bounded goal/context-sensitive
action selection and reconsideration, with explicit verification and null/negative
comparative findings preserved.
