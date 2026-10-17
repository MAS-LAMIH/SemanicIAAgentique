# Milestone 2: JSON/RDF contract parity

This milestone checks representation parity for the existing finite semantic
profile. It changes no frozen research question or experimental condition and
makes no RDF-versus-JSON superiority, integration-effort, or performance claim.
No provider, planner, registry, LLM, credential, or external service is added.

## Reproduce

From the repository root, with Python 3.11+:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-semantic.txt -e .
python -m unittest discover -s tests/semantic_action -v
python -m unittest discover -s tests/semantic_action -p test_parity.py -v
python -m semantic_action --contract contracts/calendar.ttl --output-dir /tmp/m2-rdf
python -m semantic_action --contract contracts/calendar.json --output-dir /tmp/m2-json
```

Use new output directories. Both demos should report EXECUTE, TRUE, successful
HTTP, goal_verified=True, and exit 0. The CLI needs no new flag: load_contract
selects .ttl or .json by filename. Unknown suffixes and malformed documents
block, with no fallback to a more permissive parser. For a negative example:

```sh
python -m semantic_action --contract contracts/calendar.json --mode no_change --output-dir /tmp/m2-nochange
```

This intentionally exits 1: HTTP succeeds, but read-back does not establish the
goal. All commands run locally without an API key. Avoid broad discovery of the
original live tutorial demonstrations.

## Changes and equivalence

The packaged Draft 2020-12 schema is
`src/semantic_action/schemas/contract-v1.schema.json`; the example is
`contracts/calendar.json`. JSON structural validation uses jsonschema 4.26.0
(MIT), pinned in requirements-semantic.txt. Strict parsing rejects duplicate
members and non-finite numbers before schema validation. The loader adapts
validated JSON into the same finite assertion profile used by the RDF loader.
The smallest refactor extracts the old RDF graph checker into
_contract_from_graph and adds suffix dispatch. No changes were needed in model,
pipeline, artifact, observer, oracle, CLI, or original tutorial source.

CONTRACT_SEMANTICS.md maps every JSON field to its RDF meaning and typed Contract
field, including the profile's implicit constraints. RDF syntax and structural
resource labels erased by the existing model are not round-tripped. This is
information equivalence at the supported semantic execution boundary.

## Differential checks

Each representation runs against a separately initialized deep-copied fixture.
The test clock is fixed; state is never reused between runs. Normalization keeps
all semantic payloads, decisions, status codes, and oracle results, dropping only
run IDs, run/observation timestamps, and contract-file hashes. Invalid-document
comparisons categorize parser diagnostics, while requiring rejection and zero
API calls. Positive and negative expected results are asserted independently of
pairwise equality to avoid treating two incorrect implementations as parity.

Coverage includes every Milestone 1 execution scenario, invalid inputs,
independent goal mismatch, state preservation, allowed and forbidden extra
changes, unknown/missing/malformed/future/stale evidence, execution error, missing
state change, incorrect stored title, stale observations, nondefault freshness
bounds, exact evidence-age boundaries, independent stricter goal freshness,
malformed/unsupported/incomplete contracts, unknown versions, nested extra
fields, duplicate keys/items, conflicting identifiers, and non-finite ages.

## Actual work and limitations

Work is appended through semantic_action.cost.log_work to
`docs/integration_work.jsonl`; the Milestone 1 entry is preserved. The Milestone 2
record measures wall-clock time from instrumentation after the initial audit and
baseline launch through implementation, test execution, and documentation. It
includes tool waits and does not equal active human effort. The earlier audit
and initial baseline work remain an explicitly unmeasured entry, not a guessed
historical duration. Unmeasured counters and separate debugging time stay null.
Do not use these records as complete experiment integration costs without human
reconciliation. CLI work.jsonl continues to measure validation runtime only.

Parity is limited to this one supported contract profile and trusted local
single-writer fixture. The JSON adapter uses RDFLib internally, so it is not an
independent implementation for parser-performance comparisons. RDF and JSON
schema diagnostics differ; that is not an execution-semantic difference. No
conclusions about heterogeneous providers, break-even, general OWL semantics,
or costs across experimental conditions are warranted. Original tutorial live
examples retain the Milestone 1 credential/network limitations.

## Validation results

- Before implementation: all 23 Milestone 1 tests passed.
- Combined suite: all 35 tests passed in the development environment and in an
  isolated environment using the built wheel and only semantic dependencies.
- Final parity run: all 12 parity/schema test methods passed (subtests exercise
  the scenario matrix and age boundaries). Final installed-wheel schema checks:
  all 6 schema-validation methods passed after identifier validation was tightened.
- Both Turtle and JSON CLI demos independently verified the goal over local HTTP.
- Wheel packaging includes the schema resource and original tutorial prompt.
  Dependency consistency, original tutorial local tools, and diff checks passed.
- Actual measured work interval and its coverage/exclusions are in
  docs/integration_work.jsonl. Uninstrumented audit time remains unknown.

The cloud startup instructions were updated in the configuration draft to run
both milestones and both contract examples. The installation script already
reads requirements-semantic.txt and requires no change. Draft saving does not
publish or prove restoration in a fresh cloud task.
