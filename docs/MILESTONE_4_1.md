# Milestone 4.1 — close the technical pre-freeze gates

Status: new candidate for human review, not an approved scientific freeze.
Provider C was not inspected, unsealed, implemented or integrated. No LLM planner
or full confirmatory benchmark was implemented. The supplied frozen protocol PDF
is now retained under docs/protocols with its extracted text; it governs RQ1/E1
primary, RQ2/E2 secondary, RQ3/E3 optional and B/C information parity. Its generic
holdout description is not a revealed provider interface or an instruction to
unseal. No frozen research question/condition was changed.

## Historical preservation and working identity

Entry: clean commit 58816ad152a33a1e4464dc431e38f25b3dbbffbe, branch
codex/semantic-actions-json-rdf-parity. Dedicated branch:
codex/milestone-4-1-pre-freeze. Entry verification passed before changes.
Milestone 4's manifest SHA-256 is
2a01e44585d355cd3b763f0551a9f33c1139fe53595d3c8b28cd62d71a93bd4c.
Its archive SHA-256 is
ae34e3efe0b278ee1b6fafe90f90f6e7f845d2d5eeaf0d8c69c1c7fb60902c69.
Those artifacts, all old evidence files and the old manifest remain unchanged.

The old manifest's working-tree comparator necessarily disagrees with V2 code
and the three required updated protocols. Verify historical bytes against the
retained original archive with scripts/candidate_v2.py --verify-history, not by
rewriting the historical manifest to match the new tree. start-state.json retains
all immutable historical hashes. No repository history was rewritten and no
remote push is part of this milestone. Local candidate commits/tags are not
scientific approval; source identity and final candidate metadata are distinct.

## New architecture and actual provenance

- local_baseline.py and contracts/api_local/{a,b}.json implement condition A.
  The caller explicitly selects a provider-local operation. CalendarLocal and
  BookingLocal have local validation/encoding/observation code, no shared ontology
  IDs, discovery registry, shared contract loader or semantic transform language.
  Booking-specific millisecond precision, quarter-hour boundaries and two-hour
  duration are enforced, not omitted to create a cheaper baseline.
- transport.py extracts the existing loopback HTTP transport unchanged from
  Executor. Existing shared execution inherits it. Goal/Truth/Observation/current
  and the unchanged oracle are neutral infrastructure reused by all conditions.
  Ordinary common event-shape validation inside the local baseline is condition-A
  setup; it is not ontology-mediated capability discovery. This reuse is declared
  and subject to common cost-allocation review.
- native_verifier.py is evaluation-only. It deep-copies actual fixture storage,
  permission, revision and call counts, independently decodes native A/B fields
  and invokes the unchanged goal oracle. It never imports subject manuals/loaders
  or output mapping code. It also compares full raw other-record contents.
- evaluation.py combines runtime and native verification and separately records
  unsafe mutation attempts against independently specified task controls. A
  deliberately bad map can yield runtime_verified=true but native_verified=false;
  final verified remains false. Actual achievement and missing required runtime
  evidence remain distinct; an independent live snapshot does not retroactively
  make a stale runtime observation valid.
- event_ledger.py implements append-only, hash-chained, locked/fsynced resource
  events, linked corrections, overlap prevention and unknown-preserving summaries.
  Old integration_work.jsonl and previous wall-clock evidence were not reinterpreted.
- evaluation_tasks.py, docs/evaluation_tasks_v1.json and the specification define
  20 public diagnostics. They are not a sealed answer set or full multi-step E1.

All new descriptions/validators/tasks were authored by Codex after prior exposure
to existing shared manuals. Provider-local files were newly written against the
actual fixture specifications, not converted from ontology descriptions and
represented as blind independent authoring. Software/module separation is not
human/organizational independence. Human review/roles remain explicit gates.

## Reproduction

From repository root with Python 3.11+ (validated Python/environment in manifest):

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r docs/artifacts/milestone4_1/evaluation-requirements.txt -e .
python -m unittest discover -s tests/semantic_action -v
python -m unittest discover -s tests/semantic_action -p test_pre_freeze.py -v
python -m semantic_action.evaluation --provider a --condition A --task D01 --output-dir /tmp/m41-example-a --ledger /tmp/m41-events.jsonl
python -m semantic_action.evaluation --provider b --condition C --task D15 --output-dir /tmp/m41-example-b --ledger /tmp/m41-events.jsonl
python scripts/candidate_v2.py --verify-history
python scripts/candidate_v2.py --verify
```

Use fresh output directories. The diagnostic CLI exits 0 when the expected
positive/negative control outcome is observed, not merely when an API succeeds.
D15 intentionally prints verified=false. Raw runtime traces, native snapshots and
resource events are kept under artifacts/milestone4_1/examples* for visible demos.
The V2 source archive, retained wheel, dependency pins, exact commands, actual
runner logs and source hashes permit clean restoration. No external service,
credential, model or paid API is needed. Original live tutorial tests remain
outside this deterministic suite; tutorial source remains unchanged.

## Cost accounting

Actual new elapsed intervals and automated execution records are in
artifacts/milestone4_1/events.jsonl. Human active and human supervision fields are
null because they were not observed. These are AI-assisted engineering wall-clock
and runtime measurements, not person-minutes or economic experimental results.
The initial read/launch before instrumentation and final serialization/reporting
outside timed intervals are explicitly excluded. Mixed implementation/review/test
intervals are not retrospectively split into provider onboarding versus shared
setup. Artifact attribution is known even when component duration is null.
Separate observed component/activity records may link manual/binding/collector
work without inventing its duration. Test-unit synthetic timer values are not
included as empirical labor. Expected negative diagnostics are not failed
engineering attempts; genuine failures/rework would be retained and linked.

The cold-start formula includes setup + observed onboarding increments + observed
maintenance, per the governing PDF. Shared transport/oracle and mapping/ontology
assets are charged consistently. Proposed collector/allocation and independent
integrator practice still require approval; previous missing costs stay unknown.

## Readiness and limitations

The technical components support visible A/B three-condition correctness review.
The final manifest records actual source, wheel and restoration test outcomes.
Remaining risks: one previously exposed AI author, trusted in-process single-
writer fixture snapshots, loopback-only APIs, bounded capability/transform rules,
unknown historic human effort, no external service attestation, and single-action
scope. The PDF's multi-step pilot coverage is not silently satisfied by these
20 apparatus tasks. Counts/seeds/order/budgets are proposals, not approved choices.

SCIENTIFIC_FREEZE_APPROVAL_CHECKLIST.md lists required investigator decisions:
exact candidate digest/source identity, independent manual/task/native-observer
review, roles/blinding, cost allocation/collector, task distribution and budgets,
full-pilot scope and future sealed-material custody. The candidate can be reviewed
technically; it is not an approved scientific freeze or an authorization to unseal.

## Observed test evidence

Entry baseline: 50 tests passed. Initial new component suite: 13 tests passed.
After concurrency and unsafe-call controls, final source and fresh installed-wheel
suites each passed 65 tests with no failures/errors/skips (146.720 and 147.009
seconds respectively). Additional targeted native raw-state invariant coverage
passed after strengthening that test. The source/wheel package uses no new runtime
dependencies. The 20-family matrix checks 120 controlled executions per full suite;
these are not independent provider samples or confirmatory trials.

Both positive and deliberate wrong-map retained examples run on visible A/B under
A/B/C; 24 observed demo records are preserved across intermediate/final examples.
Resource durations are actual automated/elapsed observations with null human fields.
Fresh archive restoration evidence, exact final commits and final digests are
recorded by the V2 manifest rather than a self-referential source-file checksum.
Local commit/tag creation is candidate versioning only; no push or unsealing is
part of this task. The candidate is technically ready for investigator review
subject to those final restoration/hash checks and the explicit methodological
approval gates above.
