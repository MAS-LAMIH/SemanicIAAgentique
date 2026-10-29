# CALM explanation results — run-001

CALM is a deterministic read-only postprocessor for retained finite-usage/1 evidence. The baseline is `f0f005ccaccc2c54d6fac7eda24986fd48551d08`; the clean implementation and prospective intervention plan were committed at `2cac350ce4248590529751cbb16b0d02de9dc268` before execution. No frozen interpreter, controller, policy, native fixture, historical artifact, V3/V4 or tutorial source changed. No external model, provider search, push or merge was used.

## Implementation and evidence boundary

See [design](CALM_CAUSAL_EXPLANATION_DESIGN.md), `experiments/calm.py`, `experiments/calm_schema.json`, `experiments/calm_study.py` and `tests/calm/test_explanations.py`. The builder imports no runtime or fixture code. Claims carry source hashes, JSON pointers, evidence planes and bounded replay rules. Deterministic narratives cite claim IDs. Copy, aggregate candidate translation, raw predicate replay, recorded state comparisons and context differences are the only supported derivations. A pure verifier checks references, values, rules, links and deterministic reconstruction.

Recorded applicability, predictions, guard decisions, HTTP responses, subsequent observations and independent native scores remain separate. The evaluator's expected-answer fields are not explanatory inputs. Aggregate native scores are private evaluation evidence, not observations available to the agent.

Actual runtime per-predicate verdicts, Permit objects, exact age-evaluation clocks, hidden reasoner intent and general causal identification are unavailable. In particular, `authorized-N.json` records a Proposal, not a retained Permit. A generic veto is not assigned an invented unique cause. Raw predicate replay is explicitly reconstructed, cannot establish freshness and may be TRUE while recorded aggregate applicability is UNKNOWN. Postcondition/frame comparisons reconstructed from authorized expected state, declarations and recorded observations are not presented as logged per-slot runtime verdicts.

## Measured results

| Measure | Result |
| --- | ---: |
| Historical episodes explained | 88 |
| Historical claim values verified | 5,200 |
| Directly supported coverage category instances | 748 |
| Reconstructed category instances | 148 |
| Unavailable category instances | 440 |
| Not applicable category instances | 72 |
| Historical identifier/order comparisons with semantic differences | 0 / 36 |
| Prospective intervention pairs | 12 |
| Actual new executions, explanation OFF/ON | 48 |
| Predicted intervention differences matched | 12 / 12 |
| OFF/ON comparisons with behavioral differences | 0 / 24 |
| New ON explanations / verified claim values | 24 / 1,411 |

Coverage has 16 categories per historical episode: 1,408 instances, or 1,336 after excluding not-applicable categories. Direct plus reconstructed support is 896/1,336 (67.1%). The 440 unavailable requests remain explicitly unanswered; they are not fabricated asserted claims. Passing source/rule checks establishes trace consistency, not independently curated semantic truth. New ON coverage is 204 direct, 41 reconstructed, 120 unavailable and 19 not applicable.

All 48 new episodes completed: 32 SUCCESS (30 verified mutations and two already-satisfied no-ops), four NO_DIRECT_MATCH, four UNKNOWN_CONTEXT, four POSTCONDITION_FAILED and four AMBIGUOUS. The four deliberately incorrect transitions were detected; none became a verified success. There were 34 agent native mutations, including those four wrong transitions. These counts describe behavior, independently of explanation coverage. New experiments did not inject timeouts; retained historical timeout evidence preserves uncertain runtime outcomes even when a late native mutation satisfies the goal.

The actual serial experiment took 34.030024747 seconds. This is automated experiment elapsed time, not engineering effort. Human-active and supervision measurements are null.

## Bounded interventions

Each pair changes one declared experimental input; incidental clocks, service ports and observation UUIDs differ between fresh runs. Predictions were saved before execution. Both domains use unchanged native services and frozen controller code.

| Intervention | Room | Cabinet |
| --- | --- | --- |
| Readiness true to false | Heat success to no direct match | Secure success to no direct match |
| Goal polarity | Desired 22 to 20: Heat to Cool | Desired secured true to false: Secure to already satisfied |
| Missing readiness observation | UNKNOWN, no dispatch | UNKNOWN, no dispatch |
| Revision/generation increment after proposal | Stale veto, reobserve, Heat succeeds | Stale veto, reobserve, Secure succeeds |
| Wrong native effect | Postcondition failure, no false success | Postcondition failure, no false success |
| Added conflicting candidate | Ambiguous, no dispatch | Ambiguous, no dispatch |

The added conflicting candidate deliberately declares false/conflicting effects over existing operations; it tests ambiguity handling, not an independently valid native capability. Revision intervention changes only revision/generation, not physical goal facts; it tests proposal freshness, not a newly injected timestamp-age threshold. Existing stale-evidence cases cover the latter explanation boundary.

The ON builder runs after execution, native scoring and service closure. OFF never builds an explanation. Strict normalized comparisons preserve decisions, requests, guards, native states and journals while removing incidental timestamps. Input seals also establish that explanation processing leaves inputs unchanged. Historical evidence covers both semantic and procedural conditions; the new interventions use the semantic condition only.

## Reproduction and validation

From repository root with the existing environment:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/calm -v
PYTHONPATH=src .venv/bin/python -m experiments.calm_study run --output /tmp/calm-fresh-run
PYTHONPATH=src .venv/bin/python -m experiments.calm_study summarize --output docs/artifacts/calm_explanations/run-001
PYTHONPATH=src:. .venv/bin/python docs/artifacts/calm_explanations/validation/verify_retained.py
```

The actual execution used `/workspace/calm-run-001`, subsequently copied byte-for-byte into the retained directory. Summary regeneration from sealed raw evidence was byte-identical. Use a new output path for any new execution; never overwrite run-001. The retained verification script also compares the original workspace copy when it remains available.

The eight serial offline suites were run with `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/<suite> -v`. The V4 pilot suite used fresh `V4_PILOT_FOCUSED_OUTPUT=/workspace/calm-v4-regression-001`, whose traces are retained under validation.

| Suite | Passed |
| --- | ---: |
| semantic_action | 87 |
| v4 | 20 |
| v4_pilot | 6 |
| v4_experiment | 3 |
| goal_choice | 9 |
| aat | 31 |
| aat_reusable | 9 |
| calm | 8 |
| Total | 173 |

All commands exited zero; exact timings and logs are retained in `validation/`. Live tutorial scripts with network/model side effects were not executed. Python was 3.12.14, rdflib 7.6.0 and jsonschema 4.26.0.

Integrity verification passed for 3,281 historical seal entries, 1,264 new raw seal entries, all 16,189 source hashes captured at execution, nine frozen repository modules and 195 installed runtime modules. Repository differences against baseline contain additions only. Retained artifacts include the schema, prospective plan, raw explanations, narratives, controller records, observations, guards, HTTP/native journals, scores, source/environment identity, JSON/CSV/Markdown summaries and test logs. `retained-evidence-sha256.json` seals the new artifact collection separately from historical evidence.

## Scientific limitations

These are controlled same-author room/cabinet mechanisms, not external generalization or general causal identification. Counterfactual statements are relative to a finite reviewed model and declared interventions. The builder and its verifier share reconstruction code, which creates common-mode risk; focused assertions independently check selected FALSE/UNKNOWN, wrong-effect and timeout cases. Native scoring uses a separate code path but is not independent human curation or blinded review. The procedural comparison shares controller, observation and verification mechanisms and does not establish semantic superiority. Opaque identifier normalization tests semantic invariance only within the recorded permutations.

No unrestricted causal inference, hidden reasoning reconstruction or automatic behavior discovery is claimed. The result demonstrates bounded, auditable explanation faithfulness and postprocessing noninterference for the retained evidence.
