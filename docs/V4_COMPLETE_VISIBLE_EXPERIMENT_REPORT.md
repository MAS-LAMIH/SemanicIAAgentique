# Complete visible-provider V4 experiment

Executed once from clean source `cfa4eba993e34b2916706b3953c55919fd3d8e54` on 2026-10-28. Results-only revision: source, evaluator, catalogue and prior evidence remain unchanged. No AI integration sessions or Provider C access.

## Execution and reproduction

Python 3.12.14; RDFLib 7.6.0; pyparsing 3.3.3; Linux 6.18.55 x86_64 / glibc 2.41; five reported logical CPUs. The runner executed serially with no concurrent tests or intentional workloads. The managed host was not proven exclusive. Exact environment and command status are retained in `docs/artifacts/v4_complete_visible/`.

Actual commands from repository root (both exit 0):

```sh
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment run --output /workspace/v4-complete-visible-evidence-001/run-001 --repetitions 3
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment summarize --output /workspace/v4-complete-visible-evidence-001/run-001
```

Use a new output path for any authorized future execution. Retained results are copied byte-for-byte into `docs/artifacts/v4_complete_visible/run-001/`; regenerate their tables with:

```sh
PYTHONPATH=src .venv/bin/python -m v4_pilot.experiment summarize --output docs/artifacts/v4_complete_visible/run-001
```

No experiment attempt was rerun. Before invocation, an external environment-metadata wrapper used system Python and stopped because RDFLib metadata was absent. It created no experiment directory or attempts. The wrapper was then run with repository `.venv/bin/python`; `prelaunch-note.txt` retains this setup issue. No tests were executed during this task.

Command elapsed: **198.931347 s**. Runner-loop elapsed: **198.592873 s** (excludes metadata setup and summary export). Both are automated wall time, not integration effort. Human-active, supervision and onboarding effort remain null.

## Coverage and verification

All 16 task families × 2 providers × 3 conditions × 3 repetitions = **288 unique attempts**. Each provider/condition has 48 attempts. All 288 meet the pre-existing diagnostic expectations. All 18 contaminated call-counter reset controls rejected before launch. Fresh fixtures/reset assertions, 288 distinct child PIDs and new attempt paths were verified; no subjects remained alive after stop. All runs completed, no unsettled observations or source drift.

| Outcome | Count |
| --- | ---: |
| Successful creation | 81 |
| Correct input/resolution rejection | 81 |
| Correct HTTP rejection | 36 |
| Correct external fault detection | 72 |
| Correct timeout detection | 18 |

Native oracle checks match every pre-recorded expectation. There were 207 native POST attempts. The 36 unexpected mutations were the intentional T12/T13 interventions and were detected, not accepted. Native final state was correct in 117 records: 81 accepted creations, 18 T15 missing-ID responses and 18 T16 late mutations. The latter 36 are not end-to-end successes. No timeout was accepted as creation. There are no failed diagnostic attempts to suppress.

JSON and Turtle normalized descriptions match. All **96 task/provider/repetition groups** have identical normalized A/B/C outcomes, invocation content and native evidence, excluding timing, process identifiers and serialization metadata. Provider A permits some inputs rejected by B (T06–T08); this intended provider validity difference is preserved in all conditions. Native correctness is outside runtime; it does not establish independently curated human answers.

All **3,013 sealed raw files** passed SHA-256 verification before regeneration and after preservation. No required raw files were missing. All **9,377 pre-existing tracked files** matched their before-run hashes. See `verification.json` and `pre-existing-files-sha256.json`.

Raw manifest SHA-256: `7cadf69541a2d7472e1faefb38f7ed04f13f09aef075279983e30fb9459dc980`.

Raw seal SHA-256: `9a93766cd155fc9e15c0c5b34ef6ce311a2dba4cdd475e4535ce2175e5837356`.

## Execution-time distributions

All values below are milliseconds, median / nearest-rank p95. The JSON/CSV distribution files additionally contain n, min, mean and max. Distributions are stratified by provider, condition and outcome; rejections are split into ordinary validation/resolution and HTTP rejection.

Worker time is parent-supervised process wall time, including interpreter/import/loading/conversion/HTTP work and process-wait overhead. Whole-attempt time also includes reset/fixture setup, observations, serialization and server shutdown. These are different measurement scopes; neither is isolated HTTP or parser CPU time.

| Provider | Condition | Outcome | n | Worker median / p95 ms | Whole attempt median / p95 ms |
| --- | --- | --- | ---: | ---: | ---: |
| a | A | External fault | 12 | 64.197 / 64.402 | 551.311 / 555.573 |
| a | A | HTTP rejection | 6 | 64.350 / 64.577 | 551.542 / 554.239 |
| a | A | Input/resolution rejection | 9 | 64.174 / 64.492 | 501.167 / 503.218 |
| a | A | Timeout | 3 | 1001.584 / 1001.596 | 2051.995 / 2055.227 |
| a | A | Creation | 18 | 64.272 / 114.519 | 552.632 / 563.797 |
| a | B | External fault | 12 | 64.166 / 64.273 | 552.195 / 555.325 |
| a | B | HTTP rejection | 6 | 64.261 / 114.504 | 552.285 / 578.327 |
| a | B | Input/resolution rejection | 9 | 64.326 / 64.760 | 501.197 / 503.162 |
| a | B | Timeout | 3 | 1001.600 / 1001.643 | 2056.193 / 2056.859 |
| a | B | Creation | 18 | 64.199 / 114.508 | 551.926 / 568.898 |
| a | C | External fault | 12 | 114.344 / 114.773 | 584.402 / 591.465 |
| a | C | HTTP rejection | 6 | 114.372 / 114.917 | 584.277 / 587.584 |
| a | C | Input/resolution rejection | 9 | 114.322 / 114.770 | 501.159 / 501.304 |
| a | C | Timeout | 3 | 1001.630 / 1001.637 | 2086.172 / 2095.808 |
| a | C | Creation | 18 | 114.338 / 114.688 | 584.323 / 597.019 |
| b | A | External fault | 12 | 64.246 / 114.549 | 552.003 / 558.433 |
| b | A | HTTP rejection | 6 | 64.262 / 64.432 | 551.849 / 553.762 |
| b | A | Input/resolution rejection | 18 | 64.228 / 64.706 | 501.151 / 501.290 |
| b | A | Timeout | 3 | 1001.614 / 1001.649 | 2051.891 / 2052.743 |
| b | A | Creation | 9 | 64.319 / 114.301 | 552.713 / 556.027 |
| b | B | External fault | 12 | 64.273 / 114.433 | 551.092 / 556.527 |
| b | B | HTTP rejection | 6 | 64.322 / 114.513 | 553.555 / 558.005 |
| b | B | Input/resolution rejection | 18 | 64.351 / 114.676 | 501.142 / 502.849 |
| b | B | Timeout | 3 | 1001.622 / 1001.675 | 2054.374 / 2055.048 |
| b | B | Creation | 9 | 64.347 / 114.461 | 552.198 / 558.681 |
| b | C | External fault | 12 | 114.517 / 114.743 | 584.273 / 596.055 |
| b | C | HTTP rejection | 6 | 114.418 / 114.587 | 584.382 / 595.072 |
| b | C | Input/resolution rejection | 18 | 114.370 / 116.026 | 501.141 / 501.538 |
| b | C | Timeout | 3 | 1001.622 / 1001.624 | 2085.729 / 2088.215 |
| b | C | Creation | 9 | 114.583 / 164.806 | 591.663 / 604.129 |

## RDF–JSON comparison and interpretation

Paired comparison uses the same provider/task/repetition, C minus B, excluding deadline-dominated T16. It describes this execution configuration, not independent provider integrations.

| Provider | Non-timeout pairs | C slower worker pairs | Median worker difference ms | Mean worker difference ms | Median whole-attempt difference ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| a | 45 | 41 | 50.120 | 43.478 | 30.743 |
| b | 45 | 43 | 50.115 | 47.995 | 30.524 |

C has higher worker time in **84/90 non-timeout matched pairs**, with an approximately 50 ms median difference on each provider. This is a consistent direction in this run, not a universal per-task difference. It is compatible with extra RDFLib import/Turtle loading work in fresh workers; the experiment does not instrument parsing separately, so it cannot attribute all of the difference to RDF parsing.

The supervisor uses `subprocess.Popen.wait(timeout=...)`. In this Python implementation, wait polling backs off to a 50 ms sleep cap. Observed worker times cluster around roughly 64 and 114 ms; completion-detection quantization is material relative to the measured representation difference. Whole-attempt medians differ less (about 31 ms), and fixture HTTP-server shutdown/settling dominates much of that scope. T16 worker times cluster near the imposed one-second deadline and are censored time-to-stop, not successful completion latency. No parser microbenchmark, pure service latency or statistical significance claim is warranted.

The functional result supports execution parity on these two controlled visible providers: equivalent capability descriptions and a fair local baseline satisfy the same independent native checks, including errors and deliberate service faults. It does not establish semantic superiority, onboarding savings, external validity for real services or held-out provider compatibility.

Only two provider units are available; 288 task executions are not 288 independent integrations. Three repetitions characterize local runtime variability, not participant variability. Shared authorship, fixture/oracle common-mode failures, fixed task order, one managed environment, limited repetitions and small tail samples constrain inference. Condition order rotates across repetitions; no randomized provider sampling or controlled CPU affinity was used. Standard p95 is descriptive and often equals max at small n. No confirmatory evaluation or scientific freeze approval is claimed.

## Retained publication outputs

- `run-001/raw/`: sealed catalogue, source/dependency manifest, per-attempt raw traces and native evidence, reset controls, inventory and completion status.
- `run-001/derived/`: regenerated JSON/CSV correctness, errors, execution distributions, static size/reuse inventory and Markdown tables.
- `timing-distributions.json/csv`: two explicit timing scopes by outcome, mirroring the runner distribution method.
- `rdf-json-paired.json`: all 90 matched non-timeout differences and descriptive provider summaries. Differences are C minus B; median/mean are computed directly from pairs, with p95 by nearest rank.
- `verification.json`, `environment.json`, `command-result.json`, logs and evidence hash indexes: reproduction and preservation evidence.

Static code metrics are unchanged from the implementation report and were regenerated, not interpreted as measured time: shared runtime 396 lines, shared A glue 17, vocabulary 17; A adapters 7/14, B JSON descriptions 33/33, C Turtle descriptions 12/12. Shared infrastructure is counted separately, once. No actual provider-specific engineering effort was observed.
