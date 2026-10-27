# V4 minimal implementation report

Implemented on `codex/v4-minimal-capabilities`, continuing the approved proposal.
This is a working single-operation vertical slice on visible A/B fixtures, not
an execution of the proposed comparative or confirmatory experiment. Provider C
was not requested, accessed, generated or imported. No push/merge is included.

## What works

`src/semantic_capability_v4/` contains an independent runtime. JSON and Turtle
frontends normalize to the same plain OperationDescription. Exact capability-ID
lookup reports NotFound/Ambiguous; duplicate operation IDs fail rather than
selecting the first. Optional explicit operation/provider selectors disambiguate.
Ordinary request validation and exact timestamp conversions precede one POST.
Structured results separate HTTP status, mapped output, errors and uncertain
transport outcomes. No capability match or HTTP status proves domain correctness.

The vocabulary is `v4/vocabulary.json`; visible descriptions are
`v4/descriptions/{a,b}.{json,ttl}`. A uses ISO instants and event field names; B
uses integer epoch milliseconds, different field/operation names, its existing
two-hour bound, quarter-hour grid and 500-character title limit. JSON does not
construct RDF graphs; RDFLib is imported only by the Turtle loader.

There are no Contract/Goal/effects/transitions/precondition truth values, runtime
oracle, native-state imports, planners, retries or repair rules. Runtime import
isolation is tested in a fresh Python process blocking V3, RDFLib and jsonschema
while exercising the JSON path. Native-state assertions live only in tests.

## Reuse and new components

| Component | Disposition |
| --- | --- |
| V3 `transport.py` | Narrow loopback/no-redirect/5-second HTTP pattern adapted into V4 `http.py`; new local result data, no legacy model import |
| V3 pure timestamp conversions | Adapted into `mapping.py`; exact integer arithmetic retained and unsupported precision rejected explicitly |
| V3 visible A/B fixtures | Reused unchanged by tests/demo only; not imported by the runtime |
| External correctness checks | New V4 test-side native assertions, independent of description mappings and runtime conversions; no V3 oracle or Goal used by the test assertions |
| `model.py` | New plain OperationDescription and InvocationResult, plus shared vocabulary identifiers |
| `descriptions.py` | New strict direct JSON and local Turtle loaders plus shared finite profile validation |
| `registry.py`, `invoke.py` | New finite lookup and ordinary single-call invocation |
| V3 behavioral engine/loaders/local executors | Neither modified nor wrapped/rebranded |

## Measured size and dependencies

Counts include physical source lines, comments and blanks, recorded in
[complexity-and-preservation.json](artifacts/v4_implementation/complexity-and-preservation.json).

- **6 functional modules plus a one-line `__init__.py`: 7 Python files, 378 lines.**
- **Zero third-party dependencies** for JSON loading and HTTP invocation.
- Optional RDF frontend: **one direct dependency**, RDFLib 7.6.0; its parser
  dependency is pyparsing 3.3.3. A fresh environment with only these two
  distributions ran the entire new test suite.
- Provider A: **33 JSON + 12 Turtle lines, zero provider-specific runtime Python**.
- Provider B: **33 JSON + 12 Turtle lines, zero provider-specific runtime Python**.
- New external test module: **282 lines**. Its fixture setup helper is 5 lines
  and independent native-check helper is 17 lines (physical function spans,
  including shared A/B logic). Provider-native evaluation knowledge is counted
  separately from runtime mappings, not treated as free onboarding functionality.

V3's package has 26 Python files, but includes fixtures, evaluation and sequence
facilities absent from this slice. This is a scope-qualified size observation,
not proof of an engineering-cost advantage. No prospective onboarding effort was
measured; unknown human/AI supervision time remains null. The data files contain
new reusable mappings, not new independently authored provider API implementations.

## Fresh validation

Command from the repository root:

```sh
PYTHONPATH=src /tmp/semanic-v4-minimal-env/bin/python -m unittest discover -s tests/v4 -v
```

**20 tests passed in 28.559 seconds**, Python 3.12.14, exit 0. These are new V4
executions; no V3 test results are used as V4 evidence. Tests expand across both
formats/providers and cover normalization, malformed/unsupported descriptions,
exact/ambiguous/missing resolution, mappings, offsets/precision, ordinary invalid
inputs, provider limits, HTTP success/errors, bad response shape and output mapping.

The external native reader checks actual A/B records, IDs, exact times/titles,
mutation count and unrelated-record preservation without reading runtime mappings.
Fault controls show HTTP success alongside no change, wrong properties and extra
mutation. A real five-second timeout retains an uncertain result and observes a
later native mutation after releasing the fixture; there is one mutation attempt,
not a retry. Service permission denial is an HTTP error, not semantic assessment.

The README's exact embedded Provider B example also passed (201 and mapped
`booking-0001`). Full logs, commands, installed package versions and exits are in:

- `docs/artifacts/v4_implementation/test-results-current.json` and `tests-current.log`.
- `minimal-environment.json` / `.log` (fresh offline dependency installation).
- `readme-demo.json` / `.log` (exact documented invocation).

Earlier attempts are retained: `tests-initial.log` passed 19 tests;
`test-results.json` / `tests-final.log` records an erroneous runner selection of
the base interpreter, which lacked RDFLib (20 tests, 16 errors, exit 1). The
interpreter symlink had been resolved out of its virtual environment. No runtime
code was changed to hide that failure. The fresh minimal environment corrected
the selection, passing 20 tests in `tests-minimal-env.log`; the final run above
also includes the strict timestamp grammar hardening. No tests were skipped.

## Preservation and remaining limits

All **7,353 pre-existing tracked/proposal/evidence files** match the before-work
hashes, including V3 source/manifests, retained archives/wheel, M4.4/M4.5 and the
approved V4 proposal. Historical tags and implementation identities are unchanged.
Only new V4 source/data/tests, this report/README and separate evidence were added;
V3 packaging, tutorial and dependency files were not changed.

The runtime is source-only (explicit PYTHONPATH), limited to local controlled
origins, fixed POST paths, flat JSON fields and one capability. No arbitrary Web
API authentication, general discovery, subclass reasoning, nested mappings or
multi-step execution is claimed. Loading untrusted Turtle is restricted to local
Turtle data, not remote ontologies; descriptions cannot supply executable code.
Python callers are not sandboxed by the helper API.

HTTP transport conservatively marks connection/timeout/read failures as unknown
remote outcome. Successful status with unusable output remains an error and may
have mutated native state; no cancellation claim is made. Real service behavior
and correctness remain outside the runtime. Fixture/test authorship is shared;
separate code does not establish independent human curation.

API-local comparative adapters, prospective integration-effort measurements and
the proposed full V4 diagnostic catalogue are not implemented/run in this slice.
No scientific freeze, confirmatory result or Provider C unsealing is authorized
or asserted. Stop here for implementation review.
