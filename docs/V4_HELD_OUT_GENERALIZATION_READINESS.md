# V4 held-out generalization readiness

**Preparation only; Provider C remains sealed.** Primary question: can infrastructure
built on visible A/B support one unseen provider without changing shared V4 code
or vocabulary? This replaces effort reduction as the primary objective for the
next study; earlier protocols/results remain historical and unchanged. One held-out
provider supports a bounded case study, not population generalization.

## Immutable reference

Baseline commit: `87309bca7456f3d8df827549761052cd467a3f7b`, clean at preparation.
Its complete visible run has 288 passed diagnostics, 18 rejected reset controls,
and zero condition-parity differences. No new implementation candidate or formal
scientific approval is claimed. The commit's Git tree also anchors all historical
evidence; no new tag or archive is required. Python 3.12.14, RDFLib 7.6.0 and
pyparsing 3.3.3 are the reference environment.

The SHA-256 inventory below records shared runtime, vocabulary, A/B descriptions
and adapters, catalogue, evaluation modules, fixture/supervision dependencies,
tests, dependency pins and the visible run's manifest/seal. Shared runtime and
vocabulary are strictly immutable. Existing A/B assets, catalogue inputs and
expectations, fixtures and historical evidence are also immutable. Evaluation
modules are anchored at baseline: narrowly scoped extensions require the audit
below, not a claim that their baseline hashes still match after edits.

<!-- BASELINE_HASHES -->
```json
{
  "docs/artifacts/v4_complete_visible/run-001/raw/evidence-sha256.json": "9a93766cd155fc9e15c0c5b34ef6ce311a2dba4cdd475e4535ce2175e5837356",
  "docs/artifacts/v4_complete_visible/run-001/raw/manifest.json": "7cadf69541a2d7472e1faefb38f7ed04f13f09aef075279983e30fb9459dc980",
  "src/api_local_v4/__init__.py": "834b02333eda5ef481f5fdec4bcc3b712999861d2d7240de4eb73654acd40fd3",
  "src/api_local_v4/a.py": "db5c0327e95f7d73ca1cd926e742b6e2d17aa64fd2e65911494922f8397fc107",
  "src/api_local_v4/b.py": "5d4742cb93605a24ab44650bbe54f392156682cb0cecfa886726f4a93b1857a8",
  "src/api_local_v4/common.py": "4c32a5243ca9f0842ac5298ecd369f9cc35a3785e884d7df91c1516905aa93e1",
  "src/semantic_action/artifact.py": "f3265de6a747092b0e74f06578d5c37bf4d3c7933f7b9b08a3c9064f5558badd",
  "src/semantic_action/model.py": "0f241776b02d70348b09a92755c816fa1524a85c49e5190594180806c73d9f43",
  "src/semantic_action/provider_b.py": "e1ff70938fe4c98abed96fdf6aa95a154d7b23540789a117a9de51d71ca41107",
  "src/semantic_action/supervision.py": "f9f0d8c99f069f98047ed0481da18f4724525c55d200efcd02ff3eb53f294a8f",
  "src/semantic_capability_v4/__init__.py": "8ab5cae4fd6a2b0720e0eeeb0bd4c6e4d68e4b1f137d01deae403badd7ad7f38",
  "src/semantic_capability_v4/descriptions.py": "d0714effcd70db0c564e19f5fe8733591d55efe748bab07ce9e65cbf2bb2e6f6",
  "src/semantic_capability_v4/http.py": "e1e1c82904f87265faf01daac0be683bfafb8c90adabb7aa5e2175fb5997c754",
  "src/semantic_capability_v4/invoke.py": "b083cc07addf95142993ee1746621058fc0d40019796433ee41db28c576ef7c8",
  "src/semantic_capability_v4/mapping.py": "3bf6e88be44cb1c2ee01b6f925ad4380efee1ca5edf0c8c69706d5c8c76101aa",
  "src/semantic_capability_v4/model.py": "8a085a3417d6e2842fc305cde642fcd53f7b0a78ff199004e9e0295a6a57a397",
  "src/semantic_capability_v4/registry.py": "6de9ab11f36f1698c139b81105642969c750c909baaec7eb4db7890656fb1937",
  "src/semantic_capability_v4/validation.py": "3db4eb858a9df3bf541ce73df60d523129fd3d167c403cb5bf5f12040c095aa8",
  "tests/v4/test_capabilities.py": "01fd72d77587b108f4d6f7d1ef658421cb383d1ea8cf32f0404a65fa85244866",
  "tests/v4_experiment/test_experiment.py": "486be8b3cb9a957155dd6c0439d373e01f12935be723e9ad60f679800a1d697f",
  "tests/v4_pilot/test_comparison.py": "764956447fc968189ddfab9d54cdf7e058ca14b90222ed503baa25614d742f10",
  "v4/descriptions/a.json": "35c0af705e403db70e66c75f262c7bf9590da0bf49df3b10234ef2b675126c4f",
  "v4/descriptions/a.ttl": "f9338626ec934f52df21c51ac47270886589b859911ace30191fe20e81f7a281",
  "v4/descriptions/b.json": "95fb3c6647e99ca265225611b7f43c49b880f9b0cb8625aba1f42f8024f3300f",
  "v4/descriptions/b.ttl": "4ac874f1edefaa995c2f5f53698b40250a6fc987408af509daa83912f463e815",
  "v4/requirements-rdf.txt": "2b96826d99ddc4d5fa0d77fbbe69bbaedd4463abb0527b1635947312f650ebeb",
  "v4/vocabulary.json": "08e1970430fdd92e5f7c823e1b794b2025b78af61b8825876ba09c842a73bf95",
  "v4_pilot/__init__.py": "dcea2e2fc15e9f8d7773b86e6883923a0ea37c80a8740b11f8e7eb12be58e69e",
  "v4_pilot/driver.py": "2fa5a7f9912ddfcfa91f6ab85dbe77375d621a420f55a83666cdd54681f8d023",
  "v4_pilot/experiment.py": "5034dd826987701f404c4abd8a026a2bc06e4ebe388bf316de58f22e56c7eda5",
  "v4_pilot/native.py": "7d583c3a640e5d8bb243423afa419b9b4ca86f8a45ff8f17d05512b398076ca9",
  "v4_pilot/record.py": "bf1c9ff709aa89bf2bdf51de97e30c264f96cb62b748ffcc0334f737f2091e75",
  "v4_pilot/summarize.py": "b2e59586b647c88533af5212d8bfdd16693717bd8f6ca8201ee15104be638955",
  "v4_pilot/tasks.py": "ba82d0da9b04b705e80335a2359f520fee36f4bc2e8dc36afb680650de92714d",
  "v4_pilot/worker.py": "6ae9f658c72c880cf53938a61058a61cadcf437de1f48f596386b906b5ad21d1"
}
```

Read-only verification from repository root; expected PASS now. After authorized
evaluation extensions, report each changed evaluator hash explicitly; do not edit
this inventory to conceal differences:

```sh
python3 - <<'PY_VERIFY'
from pathlib import Path
import hashlib, json
s = Path('docs/V4_HELD_OUT_GENERALIZATION_READINESS.md').read_text()
block = s.split('<!-- BASELINE_HASHES -->', 1)[1].split('```json', 1)[1].split('```', 1)[0]
expected = json.loads(block)
changed = [p for p, h in expected.items()
           if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]
print('PASS' if not changed else 'CHANGED', changed)
raise SystemExit(bool(changed))
PY_VERIFY
```

## Locked success criteria and allowed scope

- Conditions: A explicit provider/operation routing; B JSON plus frozen shared
  capability knowledge; C equivalent Turtle plus the same knowledge. Condition C
  is a representation, distinct from Provider C. Same public API/task information,
  canonical inputs, constraints and external correctness gate for all three.
- Required positive behavior: exact EventCreation capability, correct title and
  start/end instants, exactly one new native event, usable returned ID, preserved
  unrelated records and permissions. Independently specified revision/call-count
  invariants must hold where the native service exposes them. HTTP success alone
  is insufficient. Missing native observability is UNKNOWN, never success.
- Full supported-profile generalization requires mandatory positive tasks to pass
  all conditions, all locked applicable negatives/fault controls to behave as
  expected, functional parity, clean resets, no unexplained mutations, and no
  shared runtime/vocabulary edits. Repeated runs must not hide any failures.
  Equal failure in three conditions does not satisfy the positive gate.
- Existing frozen conversion, validation, result, exact-ID lookup and HTTP behavior
  must be used unchanged by B/C. JSON/Turtle must normalize identically and have
  the same constraints/mappings. No provider-specific semantic-runtime patch,
  monkeypatch or wrapper performing missing semantic conversions outside the
  description is allowed to count as frozen-runtime support.
- Allowed additions: a provider-specific A adapter; provider-specific JSON/Turtle
  descriptions; provider-specific fixture/native reader/tests; minimal evaluator
  and worker dispatch/reporting extensions. No A/B integration or evidence changes.
  Reuse ordinary shared utilities in A fairly; do not make it intentionally verbose.
- Extensions must be evaluation-only or provider-specific. Prefer a small new
  held-out entry point and native reader over editing historical runners. If
  existing evaluator/worker dispatch needs an edit, preserve A/B semantics, record
  exact before/after hashes and diff, test A/B behavior into new output paths, and
  retain validation evidence. No new framework, capability, planner, contracts,
  repair or semantic inference. No nested AI sessions/model dependency.

Current profile is explicitly limited: loopback HTTP, JSON POST, fixed response
shape/size, five-second HTTP deadline, existing mapping conversions and ordinary
limits. Do not infer that the unknown provider fits. Authentication, transport,
format or conversion requirements outside the profile are UNSUPPORTED, even if A
can implement them. A proxy/adapter that supplies such missing functionality is a
reported workaround, not unqualified generalization. Pure routing that leaves wire
semantics unchanged must be documented separately. No provider requirements are
asserted here.

## Integration / independent evaluation separation

After separate authorization, a custodian releases only public API specification
and task requirements to the integration contributor. The independent evaluator
curator/reviewer receives native service specifications/storage access and writes
expected results **before reviewing integration mappings or outputs**. They must
not derive answers from JSON/Turtle descriptions, A adapter code or runtime
canonicalization. Native extraction must use original native fields, independently
established units/IDs and exact instant comparison; preserve raw before/after
snapshots and complete unrelated-record comparison. Expectations must be written
and hashed before integration submission/evaluation, with provenance/reviewer
identity. Conflicts or overlapping roles must be disclosed; code separation is
not proof of independent human curation. If an independent reviewer is unavailable,
label that limitation and do not claim independent curation.

Keep private native reader, expected answers, fixture controls and scoring output
outside the integration workspace. The integration sees only public tasks/API and
its own solution. Evaluation runs submitted immutable revisions in fresh workers;
only API access and result files cross the worker boundary. No native storage
access from V4 runtime. Raw private evidence must not be fed back during scoring.
The trusted pilot worker is not a hostile-contributor sandbox; use the demonstrated
separate evaluator/worker mounts if isolation is required and verify them again.
No AI-session experiment is required.

The current `v4_pilot.native.decode` treats non-A as B and the driver/worker reject
unknown providers. Never call them with C and accept fallback behavior. An explicit,
independently reviewed native reader/dispatch must be added after authorization;
retain adjudication obligations and A/B tests. Unsupported native observability
must remain UNKNOWN rather than manufacturing counters or expected state.

## Prospective task and classification gate

Retain all 16 baseline families and their canonical inputs as the reference. No
Provider C-specific inputs/answers are generated here. Before integration exposure,
the authorized curator locks concrete service-valid inputs, fixture controls,
expectations and applicability from public/native specifications. If a baseline
input conflicts with a published limit, preserve that case as a rejection; any
additional positive input must be specified before implementation and reported as
a prospectively locked variant, never silently replacing the original. At minimum
T01–T03 must each have a locked valid positive instantiation to test creation.

| Family | Provider-neutral obligation |
| --- | --- |
| T01 | Valid EventCreation and unrelated-record preservation |
| T02 | Offset timestamps denote the same instants |
| T03 | Unicode title preserved exactly |
| T04 | Missing required canonical title rejected without mutation |
| T05 | End before start rejected without mutation |
| T06 | Sub-millisecond input: exact representability or documented rejection |
| T07 | Off-grid input: documented native constraint or exact accepted value |
| T08 | Long duration: documented limit or exact accepted interval |
| T09 | Permission-denied response, no mutation |
| T10 | Server failure response, no mutation |
| T11 | HTTP success without creation detected externally |
| T12 | Wrong stored properties detected externally |
| T13 | Forbidden extra/change/delete side effect detected externally |
| T14 | Unsupported exact capability/operation rejected before invocation |
| T15 | Missing response ID not accepted as usable creation |
| T16 | Delayed mutation after deadline: timeout/uncertainty, never accepted creation |

Curator specifies exact native permission/revision/counter rules and error codes;
never reuse `expectation(task, 'c')` (its branches encode visible providers).
Baseline T16 uses 1.5-second service delay and one-second outer budget; other tasks
use 60 seconds outer, HTTP five seconds, zero automatic retries. Use fresh state
per attempt, existing unrelated sentinel records, reset checks and bounded
post-stop observations (1.5 seconds, up to five-second terminal drain when needed).
No pending work may contaminate the next fixture. Unsettled state remains UNKNOWN
and the fixture is quarantined; timeout does not cancel remote effects.

Before execution, lock an applicability/expectations manifest with native provenance.
All original slots remain in reporting: planned base matrix = 16 × 3 conditions ×
3 repetitions = 144 diagnostic slots, plus nine contaminated reset controls. If a
control cannot be implemented honestly, mark UNSUPPORTED with reason; do not count
it as executed/pass or remove it from the planned denominator. Record original and
additional positive variants separately. State narrower supported-profile findings;
unqualified full coverage requires all locked requirements, not just convenient
cases. Provider-specific restrictions must apply equally to A/B/C conditions.

Classify each slot as successful creation, correct ordinary rejection, correct
HTTP rejection, correct external fault detection, correct timeout detection,
incorrect behavior, UNSUPPORTED, or UNKNOWN/incomplete/harness error. A deliberately
injected faulty service can be a passed diagnostic while creation itself fails.
Report diagnostic expectation satisfaction separately from creation correctness,
ID usability, unexpected mutations, late effects and uncertainty. Compare normalized
functional outcomes within each repetition/task/variant, not IDs/times/process
metadata. Unsupported asymmetry (e.g. A works but B/C cannot express it) is a finding.

## Exact next steps — not executed or currently executable for C

1. Investigator authorizes custodian access/release and names integration and
   independent native-evaluation reviewers. This document does not unseal anything.
2. Curator locks native expectations, applicability and any positive variants
   without semantic descriptions as answers; record hash/signature/conflicts.
3. On a new development branch, add only allowed provider/evaluation files. Review
   native reader, prove JSON/Turtle normalization and unchanged shared hashes, and
   validate the complete A/B matrix in a fresh directory if dispatch changed.
4. Review/lock integration revision and evaluation configuration. The next author
   must implement a **minimal** `v4_pilot.heldout` CLI with the same `run`/`summarize`
   interface and exports as `v4_pilot.experiment`; this module does not exist now.
   Provider is fixed to held-out C (no unknown-provider fallback). It must consume
   the independently locked gate, preserve failures, enforce fresh/reset isolation,
   seal raw evidence and export JSON/CSV/Markdown. Existing visible CLI has no
   `--provider c` flag: do not claim otherwise. Freeze that evaluation revision
   before scoring; no general orchestration system is needed.
5. Proposed exact invocation contract, **only after** implementation/review and
   separate execution authorization (these are prepared commands, not runnable now):

   ```sh
   PYTHONPATH=src .venv/bin/python -m v4_pilot.heldout run --gate /private/provider-c-gate.json --output /private/v4-heldout-run-001 --repetitions 3
   PYTHONPATH=src .venv/bin/python -m v4_pilot.heldout summarize --output /private/v4-heldout-run-001
   ```

   Gate path is an evaluator-only prospective interface, not an existing file or
   generated answer set. Run serially on new paths; preserve attempted failures.
   Release sanitized public result exports only after custody/answer review.
6. Verify planned slots/actual attempts/unsupported/unknown separately, controls,
   raw seals, source stability, independent native verdicts and normalized parity.
   Regenerate tables solely from sealed data. Report execution time by outcome
   and scope; repeated executions are not independent providers. Engineering effort
   is secondary and unknown measurements stay null.

If shared code/vocabulary must change, preserve the first failure, baseline hashes,
all attempted revisions, exact required change and justification. Stop that frozen
arm; do not retrofit it and call the result frozen-runtime generalization. A
separately authorized amended-runtime exploratory study needs a new revision and
separate results, not replacement of the original. Likewise retain all workarounds,
unsupported requirements, deviations, missing data and failed/incomplete attempts.
Do not repeatedly adjust expectations after seeing outcomes.

**Readiness:** baseline hashes and provider-neutral decision rules prepared;
held-out materials untouched. Custody/release authorization, independent concrete
gate, minimal provider/evaluator additions, review and execution authorization are
pending. This preparation commits only this document; no experiment was run.
