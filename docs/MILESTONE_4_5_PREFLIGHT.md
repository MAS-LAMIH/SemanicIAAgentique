# Milestone 4.5 — visible-provider operational preflight

This is an evaluator-only addition on `codex/milestone-4-5-preflight`, based on
`ef123513e27d1e63abe79f39b272b5587e710909`. It does not establish a scientific
freeze or supply confirmatory results. Provider C remains sealed and was not
requested, inspected, inferred, generated or imported.

The immutable V3 candidate remains `752da7b8de85dd38c7eee30a101b786ea4743821`,
implementation `2d264169a5ec363b78d4bf78b3f40e82d7b59f85`, tag
`candidate/milestone-4.3-pre-freeze`. Its manifest SHA-256 remains
`53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352`;
source-tree digest `bd14f5b4839ac7a49e1bfca01b1adff29fbde6f17497723fac7186cfb6137368`.
The retained archive digest is
`b659c852d78ff2bad99f6ec743b5b0bd0a16ad88bbcd20af5e8e6e091089c27d`;
wheel digest `538f5acdb7366300f81166232f8877c31c9260e6dbb7dbb226150ea35621cc1b`.
No new implementation candidate or tag was created.

## Composition and preservation

The pre-code [inspection](artifacts/milestone4_5/initial-inspection.md) records
why the old single-action entry point cannot simply be killed as a unit: it owns
its fixture server. `preflight/driver.py` instead owns the fixture, calls the frozen
reset gate, supervises a fresh `preflight.single_subject` process, retains the
service after termination and calls the frozen native adjudicator. The child
invokes existing validated LocalExecutor or Registry execution. It receives no
native expectation. Multi-step execution directly calls frozen `run_pilot`.
Neither path performs raw mutation requests, automatic retries or compensation.
The existing HTTP timeout remains 5 seconds; the rehearsal outer budget is 60.

Single-action service modes, public missing-evidence interventions and manual
variants reproduce `semantic_action.evaluation.run_case`. For the decoy-mapping
control, the evaluator callback inserts the same advertised field before POST
response delivery; the original harness inserts it immediately after delivery.
Both occur before observation GET. All 120 normalized single-action summaries
are compared against separately run frozen references to test this boundary.
Multi-step summaries are compared against the retained final V3 pilot.

New files are confined to `preflight/`, these two reports and
`docs/artifacts/milestone4_5/`. The final evidence inventory lists every added
file and digest. `start-state.json` records all 3,216 pre-existing tracked files;
`verification-results.json` checks their bytes without rewriting historical
manifests, archives, evidence, ledgers or pending decisions.

## Reproduction

Use Python 3.12 and the frozen pins in
`docs/artifacts/milestone4_3/evaluation-requirements.txt`. Install the retained
wheel or editable source into an isolated environment; `preflight` runs from the
repository root and is deliberately outside the frozen wheel.

```sh
python -m preflight.environment
PREFLIGHT_FOCUSED_OUTPUT=/tmp/m45-fresh-focused python -m unittest discover -s preflight/tests -v
python -m preflight.rehearsal --phase reference --output /tmp/m45-fresh
python -m preflight.rehearsal --phase rehearsal --output /tmp/m45-fresh
```

The rehearsal checks the retained focused safety gate; do not treat a failed
focused run as authorization to proceed. Each run path must be new. To rerun the
frozen suites independently, restore exact candidate source and the retained
archive into different directories, install each plus the pins (or install the
retained wheel for the wheel condition), then in each source directory run:

```sh
python -m unittest discover -s tests/semantic_action -v
```

Exact actual commands, interpreter paths, timestamps, exits and logs are in
[verification-results.json](artifacts/milestone4_5/verification-results.json).
The current regression reruns used existing isolated source/wheel/archive
installations from M4.4, verified afresh against every frozen runtime member;
test files came from newly extracted exact candidate/restored source directories.
These are fresh test executions, not claims of fresh installation effort.
Candidate verification ran in the exact candidate extraction because the review
checkout intentionally contains additional documentation outside V3's closed
source inventory. Nothing was regenerated to make that check pass.

## Recorded results

Engineering verdict PASS: 180/180 protected attempts match frozen expectations;
zero normalized differences against the 120 frozen single-action references and
60 retained final V3 chain summaries. Both focused runs passed, with 14 reset
rejections and 18 deadline outcomes (six initially uncertain) retained separately.
Source, wheel and restored suites each passed 87/87. All 3,216 old tracked files
and all pending approval records are unchanged. See the report for expected
negative and INCOMPLETE chain counts, environment-cache retries and limitations.

## Interpretation and decisions

See [the operational report](COMBINED_DRIVER_PREFLIGHT_REPORT.md) for measured
coverage and safety results. Expected diagnostic rejection, expected HTTP/native
failure and runtime/native disagreement are retained, not deleted as unsuccessful
runs. Only two providers are independent provider units; repeated task and
condition runs are correlated diagnostics, not 180 independent provider samples.

Actual command runtimes are recorded through the unchanged Event/Ledger collector
in a new `events.jsonl`. Human active time, AI supervision and model/tool waiting
remain null. Automated durations may overlap; do not add overlapping runtime to
infer elapsed wall-clock time or human effort. Start/end observations delimit
this preflight only; no historical costs were reconstructed.

Investigator decisions remain pending: independent semantic/native-oracle review,
cost-policy approval, locked tasks and analysis, custody/roles, freeze signoff and
separate future unsealing authorization. No push or merge was performed.
