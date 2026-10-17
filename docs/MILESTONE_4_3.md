# Milestone 4.3 — bounded multi-step pilot and operational readiness

Status: new technical candidate V3 for investigator review, **not an approved
scientific freeze**. Provider C was not accessed, unsealed, implemented or integrated.
No LLM, autonomous planner, confirmatory experiment or task-specific repair was added.

## Historical and working identities

Entry was clean commit `950ebf9` on `codex/milestone-4-1-pre-freeze` after M4.2.
A dedicated branch `codex/milestone-4-3-multistep` was created before code changes.
The original V2 candidate `2829c6dc41344431e83bde7c3addf30d1241befc`, tag
`candidate/milestone-4.1-pre-freeze`, and manifest SHA-256
`7f8e8d1d4f0f07e8c5ef999c36aaf987d17bf58d757df4a733f736ceaa78bcc2`
were verified from an exact temporary Git archive. Entry baseline passed 66 tests
in 146.837 seconds. `artifacts/milestone4_3/start-state.json` records provenance and
134 historical file hashes; old manifests, archives, logs and both M4.2 approval
files remain byte-for-byte unchanged. Old full-working-tree verifiers cannot be
used to relabel evolved V3 source as V2. `candidate_v3.py --verify-history` verifies
134 preserved files, the 104-member V2 archive and the historical M4 archive.

V3 is a distinct source commit, source-tree digest, archive and manifest. Exact
identities are in `SCIENTIFIC_FREEZE_MANIFEST_V3.json`; the implementation/documentation
commit is separate from the evidence/manifest commit to avoid self-referential
commit/digest loops. The candidate tag is `candidate/milestone-4.3-pre-freeze`.
A local candidate commit/tag is versioning, not scientific approval or release.
The retained M4.2 decision record refers to V2 only; its null fields were not filled
or reused as a V3 decision. V3 needs a new investigator decision binding its digest.

## Implemented bounded semantics

Original A/B support creation only. New controlled fixture endpoints create a
follow-up **only if the named predecessor exists and ends no later than the new
start**: calendar `/followups/{id}`, booking `/booking-after/{id}`. Native records
retain `predecessor_id` / `previous_booking`. Direct service tests reject absent
predecessors and overlapping intervals even without the subject sequence guard.
These added operations are deliberately controlled apparatus written by the same
previously exposed AI author, not naturally occurring independently authored APIs.

`sequence.py` executes a declared two/three-action chain with immutable formal goals.
It reads fresh wire evidence for each predecessor, preserves TRUE/FALSE/UNKNOWN,
reuses LocalExecutor or Registry/Executor for every mutation, and stops on any
failed required action, incompatible effect or insufficient evidence. There is no
new unchecked POST path, implicit substitute, compensation, retry or goal-based
skipping. Each step and available partial state are retained.

Condition A has explicit provider-local follow-up descriptions/bindings. B/C have
equal typed sequence profiles backed by their existing equal v2 manual information.
Only the finite follow-up guard and dynamic predecessor-ID binding are new; existing
registry, contract validators, schemas, transforms, LocalExecutor and single-action
pipeline/oracle are unchanged. Provider fixtures gained default-inert sequence
interventions and transition observation hooks. Changes are covered by the V3 identity.
See `MULTISTEP_PROFILE.md` and `contracts/sequences/README.md` for closed syntax,
versioning, exact information equivalence and unsupported behavior.

The independent `sequence_native.verify_chain` consumes curator expectations and
service-side native transition snapshots, not subject output mappings or declared
effects. It calls the unchanged native adjudicator/Goal oracle per action, separately
checks native predecessor links, exact call counts, raw preservation and no intervening
unobserved mutation. Final state alone cannot satisfy a missing required transition.
The subject does not supply oracle expectations. A changed independent expected title
rejects even when runtime said success; wrong relation or raw metadata change rejects.
This is software separation, not independent human curation or external attestation.

## Scenarios and parity

`MULTISTEP_PILOT_TASKS.md` defines M01–M10: genuine dependency, revoked permission,
intermediate failure, unknown permission, unsafe non-equivalent effect, forbidden
side effect, no-op success, recovery boundary, three-step chain and stale evidence.
All share fixed formal goals, native initial sentinel state, budgets and independent
correctness criteria under conditions A/local, B/JSON+shared, C/RDF+shared.
M08 retains partial state after a transient second failure; making the service
available afterward does not trigger a retry or third action.

The main retained matrix runs 10 tasks × 2 visible providers × 3 conditions = 60
executions, with identical normalized semantic summaries across conditions. The
additional six positive runs demonstrate a second isolated repetition for both
providers/all conditions. Raw traces, actual native state and timestamps remain
in `artifacts/milestone4_3/pilot-final/`; `pilot-final/pilot-results.json` lists every result and
all failure checks. These runs are not independent held-out provider observations,
not a labor/performance comparison and not proof of RDF superiority.

Condition A was also executed for both providers from a wheel-only environment
without RDFLib or jsonschema. The shared semantics packages are evaluation/B/C
requirements, not local discovery dependencies. All-condition tests themselves
import all stacks, which must not be misattributed to A's runtime needs.

## Timeout and reset evidence

`supervision.py` runs each subject in a fresh process/session, enforces the outer
60-second default with terminate/kill/reap, and leaves the evaluator-owned fixture
alive to capture post-timeout state. The fixed per-request timeout remains 5 seconds;
automatic retries and repair iterations remain zero. Atomic incremental sequence
traces, validated action traces, stdout/stderr, native journals and cost events survive
as available. An in-flight action trace may be incomplete after forced kill; absence
is explicitly not proof that no mutation happened.

Three retained short-budget tests (A/B/C) kill the subject while a delayed booking
follow-up is in flight. The service later completes its mutation and native truth is
true, but runtime is incomplete and **verified remains false**. A separate HTTP-timeout
case distinguishes null-status request failure from outer TIMEOUT. A stalled subject
is killed and reaped; an unsettled service remains uncertain in the unit control.
No remote-side-effect cancellation guarantee is claimed. See
`OPERATIONAL_SUPERVISION_PROTOCOL.md` and retained supervision/recovery records.

Every run gates exact initial records/metadata, permission, revision/call counters,
pending requests and clean trace location before spawning a new subject. Cache
isolation follows fresh processes and new Registry instances (there is no persistent
resolution cache), not memory attestation. A retained contaminated counter=7 attempt
is rejected before subject launch. `RESET_ISOLATION_REPORT.md` distinguishes native
measurements from lifecycle/cache architecture and links the negative controls.

## Validation and reproduction

Final suite IDs are `source_full`, `wheel_full`, `restored_full` in
`artifacts/milestone4_3/validation-results.json`. Each final suite has 87 test methods: 66 regression
and 21 new; earlier 86-test stages remain separately labeled. The two differential matrices exercise 120 original and 60 multi-step
condition/provider/task executions per full suite, plus operational/native/reset
probes; test methods/executions/repetitions are not provider sample size.
Source and wheel final logs, restored-archive log, exact commands, exit codes,
runner durations, environment inventory, retained wheel and hashes are in the manifest.
Only final successful suite IDs establish final candidate validation.

Initial new-component testing honestly failed (18 methods; 3 failure reports and
1 error): shared-condition permission FALSE was incorrectly summarized BLOCKED;
a textual import check matched a comment; the failed-subtest list comparison then
raised IndexError. Resolver/pipeline safety already blocked the second mutation.
The sequence adapter now preserves FALSE/REJECT versus UNKNOWN/BLOCK; the test checks
AST imports and keeps all compared summaries. The retained corrected intermediate
18-method run passed in 54.403 s. Two additional operational tests brought coverage to 20. Final review then
found the native relation reader was A/B-only: an evaluator-owned ChainInterpretation
now supplies a provider-local event interpretation and predecessor decoder without
changing goal/link/preservation truth. Unknown identities fail closed without that
reviewed observer. A synthetic in-memory test (no new API/provider) exercises it,
bringing final new coverage to 21 and final total to 87. The earlier retained `pilot/` and `local-only/` runs are pre-extension stages;
`pilot-final/` and `local-only-final/` are final-candidate evidence. Pre-extension 86-test source,
wheel and restoration results/archives remain separate from final candidate evidence. Failed logs and linked rework records remain; nothing was relabeled
as historical success. A final whitespace check identified RDFLib-generated extra
blank lines at Turtle EOF; they were normalized without changing the RDF graphs.
The pre-format archive/restoration log are retained separately; final restoration
uses the normalized archive. A pre-edit guard also refused to modify code while baseline
was still running; the edit proceeded only after baseline success.

From repository root, with Python 3.12.14 as validated (runtime supports Python 3.11+):

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r docs/artifacts/milestone4_3/evaluation-requirements.txt -e .
python -m unittest discover -s tests/semantic_action -v
python -m unittest discover -s tests/semantic_action -p test_multistep.py -v
python scripts/run_pilot_v3.py --output-dir /tmp/new-m43-pilot --ledger /tmp/new-m43-events.jsonl
python -m semantic_action.multistep_evaluation --provider b --condition B --task M01 --output-dir /tmp/new-m43-positive
python scripts/candidate_v3.py --verify-history
python scripts/candidate_v3.py --verify
```

Use fresh output paths. The pilot CLI exits 0 when its expected positive/negative
**diagnostic** behavior is observed, not when every action achieves its goal.
Package validation used an offline cached build and a fresh pinned wheel environment;
those exact commands are retained rather than claiming pip/browser network work.
To reproduce the clean source restoration:

```sh
mkdir /tmp/new-m43-restoration
tar -xzf docs/artifacts/milestone4_3/candidate-source-v3.tar.gz -C /tmp/new-m43-restoration
python3 -m venv /tmp/new-m43-restored-env
/tmp/new-m43-restored-env/bin/python -m pip install -r docs/artifacts/milestone4_3/evaluation-requirements.txt docs/artifacts/milestone4_3/tutorieliaagentique-0.1.0-py3-none-any.whl
cd /tmp/new-m43-restoration
/tmp/new-m43-restored-env/bin/python -m unittest discover -s tests/semantic_action -v
```

The source archive deliberately excludes new dynamic evidence and its own manifest;
the manifest separately hashes every retained evidence artifact. To run the full V3
verifier from a restored tree, copy the immutable final manifest and complete
`docs/artifacts/milestone4_3/` evidence directory from the candidate checkout. Static
source/pins/start-state in the archive must match those copied artifacts exactly.
No original tutorial source or dependency declaration changed.

## Actual work and scientific limits

New `events.jsonl` uses the existing locked/hash-chained cost mechanism. It records
observed command runtimes, actual validation failures/rework and instrumented elapsed
intervals. Human active, human AI supervision, tool/model-wait decomposition and
unobserved historical costs remain null. An initial pre-instrumentation interval and
final serialization/tagging/reporting are excluded. Parent pilot duration includes
its child runtimes; it is retained as command metadata and superseded to a note in
the cost ledger to avoid double counting those same observed child runtimes.
Resource axes overlap; elapsed is not additive to automated runtime or labor.
Component authoring/debugging time not separately observed is mixed/unallocated,
not retrospectively divided into provider onboarding or condition savings.

Remaining blockers: independent human manuals/task/native-observer review and
provenance, named roles/exposure/custody, approved cost allocation and prospective
human timing, schedule/parameters/stopping/analysis decisions, and explicit approval
of exact V3 identity plus a separate later unsealing decision. The bounded chain
closes the absence-of-any-multi-step apparatus gap, not every possible multi-step
goal or the full confirmatory experiment. One calendar capability, local controlled
fixtures, trusted journals/clock/counters and one previously exposed AI author limit
validity. RQ1 remains primary; RQ2 remains separate and no planner was implemented.
All observations are visible-provider apparatus evidence. Negative/null scientific
outcomes remain valid; no integration-cost or population-level result is inferred.

Technical review readiness is determined by the final manifest's successful source,
wheel, restoration and retained pilot evidence. Passing those checks makes V3 ready
for **investigator review**, not an approved freeze. Provider C remains sealed.
