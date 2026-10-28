# Repeatable V4 execution study implementation

Implemented one small CLI module, `v4_pilot/experiment.py` (180 physical lines),
reusing the existing driver, worker, catalogue, native oracle, normalization and
supervision. No existing tracked file was edited. No V4 runtime/concept changes,
new capability, third provider, AI/model dependency or new runtime dependency.
The package remains source-invoked from repository root. See
`v4/EXPERIMENT_README.md` for complete operation and future extension boundary.

## Reproduction

Full matrix (not executed as part of this small smoke demonstration):

```sh
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment run --output /tmp/v4-repeat-001 --repetitions 3
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment summarize --output /tmp/v4-repeat-001
```

Actual smoke command (completed, exit 0):

```sh
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment run --output docs/artifacts/v4_repeated_smoke/run-002 --repetitions 2 --tasks T01 T04 T12 T16
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment summarize --output docs/artifacts/v4_repeated_smoke/run-002
```

Fresh destinations are required. Do not rerun into retained evidence. Raw files
are separate from JSON/CSV/Markdown derived tables; hash checks precede summary
regeneration. Run manifest records actual Python/dependency versions, source
revision, dirty status, actual file hashes, task hash/IDs, repetitions and order.
Execution was from an uncommitted source state based on `bc7fa48`; actual runner
hash identifies the tested source, rather than claiming that parent commit
contained the new module. The subsequent documentation commit preserves it.

## Actual results

Smoke: 48/48 expected diagnostic outcomes, 12/12 contaminated reset controls
rejected before worker launch, zero A/B/C normalized parity differences, no source
hash drift. Each provider/condition has 8 attempts, 2 successful creations,
2 correct input rejections, 2 externally detected property faults and 2 correct
timeout detections. Conditions are equivalent within each provider; no condition
advantage is asserted. Run-loop automated elapsed time: 50.605636385 seconds.
This includes reset controls and settling but excludes pre-run metadata setup and
post-run export. Tests ran concurrently with this diagnostic smoke: its timing
tables demonstrate measurement/export and are **not publication performance
estimates**. A publication timing study must run serially on a quiet fixed host.

The 12 deliberate T12 mutations are reported as unexpected mutations and correct
external fault detection, not runtime successes. The 12 T16 services mutate late;
caller timeouts are retained, their native state checked, and creations never
accepted on timeout. Native state is correct in 24 records but only 12 are
accepted creations: correctness of final storage alone does not imply completed
invocation. No actual onboarding or human/supervision effort was measured; null.
These 48 executions are repeated runtime observations across two known providers,
not independent integrations or prospective case-study results.

Before the fix, the initial runner tried to supply provider/condition keys twice
when recording a reset control. It aborted after 24 diagnostic attempts and the
first control. `run-001/`, `run.log`, `tests-initial-failed.log` and regenerated
`failed-run-summary.log` retain that failure (summary command exits 1). The
bookkeeping fix did not change runtime, oracle, expectations or outcomes.
`run-002/` is the final source smoke; it is not a relabeling of the failed run.

## Validation

Commands and results:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/v4_experiment -v
# 3 tests PASS, 12.151 seconds, exit 0
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/v4 -v
# 20 tests PASS, 28.456 seconds, exit 0
V4_PILOT_FOCUSED_OUTPUT=/tmp/v4-repeat-focused-final PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/v4_pilot -v
# 6 tests PASS, 16.222 seconds, exit 0
```

Tests cover repetition/coverage, rejection invocation counts, reset controls,
CSV regeneration without raw changes, output overwrite refusal, raw tampering,
invalid selection, retained harness failures and failed-summary exit behavior.
Existing suites cover frontend/adapter parity, native truth, reset axes, timeout
and unsettled state. Logs are retained in `docs/artifacts/v4_repeated_smoke/`.

All 8,578 previously tracked files matched their pre-change SHA-256 values,
including V3 and completed pilot evidence (`preservation.json`). No Provider C
materials were accessed, no integrations/confirmatory experiment launched, and
no model/API authentication used.

## Static inventory and reuse

Physical lines include comments/blanks; they are not development time.

| Category | Lines | Attribution |
| --- | ---: | --- |
| Existing shared V4 runtime | 396 | Ordinary utilities reused by A/B/C; loaders/registry additionally used by B/C |
| Existing shared baseline glue | 17 | Condition A common wrapper |
| Existing shared vocabulary | 17 | B/C shared semantic setup |
| A provider-specific adapters | 7 / 14 | a / b |
| B provider-specific JSON | 33 / 33 | a / b |
| C provider-specific Turtle | 12 / 12 | a / b |
| Evaluation infrastructure after addition | 670 | 490 existing + 180 new; external to all conditions |
| Shared native fixture/model/supervision sources | 524 | Evaluation setup, not provider integration effort |

Per-file hashes, bytes and lines are in derived `artifact_size.csv/json`.
Reusable ordinary utility subset (`http`, `mapping`, `model`, `validation`, init)
is 163 runtime lines. The remaining 233 lines implement description loading,
lookup and invocation. These subsets overlap condition usage and must not be
charged once per attempt or described as measured time saved. Separate actual
incremental authoring from shared setup in any future effort study.

## Limitations

Only T01/T04/T12/T16 were repeated in this demonstration; the full catalogue is
available by default but its new repeated matrix has not been executed. No new
held-out answers, descriptions or native decoder were prepared. The future
extension point is documented as explicit fixture/worker/native dispatch and
independently reviewed expectations, not a generic plugin framework. Current
native decoder assumes b for non-a: never route an unknown provider there.

Summary p95 uses nearest rank and can equal max at small n. Results are
publication-table exports, not a population inference, effort measurement or
independent oracle curation claim. Shared authorship and common-mode fixture
risks remain. Process timeout cannot undo remote mutation. A hard kill can leave
an unsealed partial run, which must remain incomplete. Trusted worker/harness
access is not hostile-agent isolation. Machine-readable raw outcomes remain the
authoritative data; edited derived tables never replace them.
