# Evaluator-owned operational preflight

Run from the repository root with the V3 package/dependencies installed. This
package is outside the frozen wheel. `driver.run` dispatches public single or
multi-step tasks, rejects any provider other than a/b, and uses new output paths.
`single_subject` is launched only by the parent; it has no native expectations.

`rehearsal --phase rehearsal` runs all 180 public diagnostic cases after checking
the retained focused gate; `--phase reference` runs 120 separately labeled frozen
single-action references. Use `--output /tmp/new-path` to reproduce without
modifying retained evidence. Focus tests accept `PREFLIGHT_FOCUSED_OUTPUT`.

The 60-second outer/5-second HTTP defaults are unchanged. Short budgets and delays
are explicit focused controls. Reset rejection never clears the contaminated
fixture. Supervisor evidence and native journals survive subject termination.
An initial uncertain result stays uncertain even after an additional bounded
observation settles the fixture. No automatic retry or compensation occurs.

`record_command` captures actual commands and runtime through the frozen collector
into a new ledger. It refuses to overwrite command logs. `environment` reads
runtime provenance; `regression` records the three frozen-suite reruns using the
retained isolated environments. Those helper interpreter paths describe this
execution environment; create equivalent isolated environments for another host.

`summarize` compares every protected result with the frozen references/final pilot,
checks lifecycle evidence and old file hashes, then writes new audit summaries.
`seal_inventory` indexes new files only. It excludes its own digest by design and
must run last after reports and verification results are final.
