# Milestone 3: semantic capability reuse across two controlled providers

This is architectural preparation, not the confirmatory held-out-provider
experiment or full E1 benchmark. No frozen research question or condition is
changed. No protocol PDF was present; the supplied frozen decisions and task
brief were used. The audit/design was recorded before modifying core behavior
in MILESTONE_3_DESIGN.md.

## Reproduce

From the repository root with Python 3.11+, use the existing virtual environment
or install requirements-semantic.txt and the project editable as in Milestone 2.
There are no new dependencies, credentials, model downloads, or paid services.

```sh
. .venv/bin/activate
python -m unittest discover -s tests/semantic_action -v
python -m unittest discover -s tests/semantic_action -p test_registry.py -v
python -m semantic_action.reuse_demo --format json --select a --output-dir /tmp/m3-json-a
python -m semantic_action.reuse_demo --format json --select b --output-dir /tmp/m3-json-b
python -m semantic_action.reuse_demo --format ttl --select a --output-dir /tmp/m3-rdf-a
python -m semantic_action.reuse_demo --format ttl --select b --output-dir /tmp/m3-rdf-b
```

Use new output directories. Both candidates should be eligible, the selected
provider should execute once, and goal_verified=True should be printed with exit
0. Fixture processes are shut down by the command. Negative demonstrations:

```sh
python -m semantic_action.reuse_demo --permission unknown --output-dir /tmp/m3-unknown
python -m semantic_action.reuse_demo --mode no_change --output-dir /tmp/m3-nochange
```

Both intentionally exit 1. The former records UNKNOWN and never mutates B; the
latter records HTTP success followed by failed goal verification. There is no
silent fallback to another provider. resolution.json records each attempted
candidate's mapping compatibility, eligibility, applicability, reasons, current
precondition evidence, and contract hash. action.json, when executed, contains
the validated pipeline trace plus provider profile and raw wire evidence.
scenario.json records demo settings; work.jsonl measures demo runtime only.

## Shared knowledge and bindings

`contracts/shared-capabilities.ttl` defines a proposed shared EventCreation
capability and NewMatchingEvent effect. Provider-local operation IDs differ:
A has create_event and B has reserveAppointment. Both explicitly map to the same
shared capability. No discovery by names, embeddings, provider-ID branches,
A-to-B substitution tables, or benchmark answers are used.

Each provider has a v2 manual in JSON and Turtle under contracts/providers/.
The packaged contract-v2.schema.json fixes the finite profile. v1 manuals and
commands remain supported. Contract has one optional ProviderProfile; absent
profiles retain the Milestone 1 behavior. JSON and RDF use one schema and one
semantic validator. Explicit transforms describe input mapping and observed
output mapping; field names, timestamp representation, response ID and evidence
keys are data, not code branches in the executor.

A remains the existing calendar REST fixture. B's separately implemented booking
API is documented in providers/PROVIDER_B.md. It uses different endpoints,
request/response/storage keys, integer Unix milliseconds, quarter-hour boundaries,
and a maximum two-hour duration. Its wire model is independent of A's and its
constraints are enforced by the service itself, as well as by contract validation.
It allows overlapping bookings; no conflict-free calendar claim is made.
Both controlled services were authored by Codex in this task. This is not evidence
of independent organizational authorship or a heterogeneous-provider experiment.

## Resolution and validation

Registry accepts local manual paths and explicitly configured loopback origins.
Given a formal Goal and required capability, it checks exact declared mapping,
modeled event-creation effects, canonical input validation, transformations,
provider duration/grid constraints, and mandatory preservation of other events.
It then probes writability using the same three-valued evaluator as execution.
Only uniquely eligible explicit selection delegates to Executor.run. Execution
rechecks inputs, constraints and fresh writability. An earlier resolution verdict
is never an authorization token. Duplicate operation registrations are ambiguous
and cannot execute. A changed manual hash after resolution blocks delegation.

The adapter has three operations: identity, ISO instant to integer epoch
milliseconds, and integer epoch milliseconds to ISO instant. Precision loss is
rejected; no rounding, arbitrary Python, unit guessing, or inferred mapping.
The unchanged independent oracle checks observed canonical state, not declared
effects. Raw requests/status/bodies are retained so mappings can be audited.

## Parity and negative controls

Differential tests run each JSON and Turtle registry on separately initialized A
and B services with the same fixed clock. They compare candidate explanations,
applicability, execution decisions, raw/canonical evidence, and oracle verdicts.
Only run metadata and serialization-specific file hashes are excluded.

Controls include compatible different names; identical create_event local names
with non-equivalent effects; unavailable transformation source; submillisecond
precision loss; wrong capability; false/unknown/stale writability; excessive
duration; off-grid times; inability to guarantee preservation; allowed versus
forbidden additional changes; stale observations; API errors; wrong stored
properties; success without state change; duplicate registrations; unsupported
transform vocabulary and extra/omitted profile assertions. Direct execution is
also tested to ensure it cannot bypass known input/provider constraints.

## Work records and limitations

Actual nonoverlapping instrumented wall-clock intervals are appended through
cost.log_work in docs/integration_work.jsonl. Records identify shared audit/design,
shared schema/registry/adapter/engine work, Provider B documentation/fixture work,
manual/mapping authoring, and validation/documentation. Mixed shared/onboarding
intervals are explicitly unallocated; do not assign their full duration to either
condition. Counts and separately unmeasured debugging time remain null. These
intervals include tool waits and AI work, not active human effort or complete
historical integration costs. Failed attempts are recorded only when observed.
Demo runtime is a separate measurement and must not be added as independent
human integration effort.

The oracle assumes trusted mappings, complete snapshots, one writer, and local
clock consistency. It is independent of declared effects, not of all transport
interpretation: a dishonest mapping can misdescribe external state. This milestone
preserves raw evidence for review but does not solve evidence attestation. Only
one capability domain, bounded scalar transforms and known constraints are
supported. Arbitrary ontology reasoning, dynamic network discovery, provider
substitution planning, LLM interpretation and registry persistence are out of
scope. The registry is in-memory and origins are explicit runtime configuration.

The fixture controls are negative controls, not separate real providers. No
Provider C implementation, requirements or answers were used. Freeze preparation
is documented in PROVIDER_C_FREEZE_PROCEDURE.md and freeze-manifest.json; no
confirmatory freeze or held-out experiment is claimed. Tutorial source is
unchanged; its live external examples retain the earlier credential/network
limitations.

## Validation results

- Before changes: all 35 Milestone 1/2 tests passed.
- After changes: all 50 tests passed in the development and installed-wheel
  environments. The final complete installed-wheel run passed in 82.433 seconds.
- Final strict v2 schema checks passed in a fresh minimal wheel environment after
  trailing-newline validation was hardened.
- All four JSON/Turtle × A/B CLI demos verified the selected goal; unknown
  permission and no-state-change demos returned the expected exit 1.
- Package build, bundled schema resources, dependency consistency, original
  tutorial local tools and diff checks passed. The independent oracle and
  original tutorial source have no changes.
- Preparation-manifest source coverage and SHA-256 verification are performed
  with scripts/freeze_manifest.py; regeneration is required after source edits.

## Instrumented engineering intervals

These are measured elapsed wall-clock minutes, including AI work and waits, not
human labor or comparable experimental costs. The initial read/baseline launch,
final serialization/manifest verification and final reporting are unmeasured.
Mixed work remains unallocated.

| Activity category | Measured minutes |
| --- | ---: |
| Shared setup: audit, baseline validation and design | 1.670 |
| Provider B onboarding: independently specified API documentation and separate fixture implementation | 1.064 |
| Shared machinery: versioned profile, schema, adapters, validated pipeline extension and capability registry | 1.540 |
| Provider onboarding: A/B JSON and RDF manuals, shared vocabulary, first integration smoke and RDF field-classification correction | 0.305 |
| Shared validation/documentation: differential registry tests, compatibility controls, regression suite, demo and freeze-procedure documentation | 4.068 |
| Shared freeze preparation and final verification: manifest tooling, package validation, final schema hardening and installed-wheel checks | 3.125 |

Two observed failed attempts are recorded: the first RDF smoke test and the
initial negative-fixture authoring helper error. Neither is erased from costs.
Separate debugging minutes and annotation/mapping/test counters were not
instrumented and remain null. No historical measurements were fabricated.
