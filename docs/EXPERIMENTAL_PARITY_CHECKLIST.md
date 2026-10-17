# Experimental-condition parity checklist — candidate

This checklist applies to conditions, not provider names. Provider A is the
existing calendar fixture; Provider B is the booking fixture. Neither is the
API-local experimental condition A by virtue of its name. Provider C remains
sealed. RQ1 studies reusable semantic knowledge; there is no presumption that RDF
serialization is superior. The other frozen research questions remain unchanged.

## Present evidence and missing implementation

| Condition | Intended information | Current implementation/status |
| --- | --- | --- |
| A: API-local | Complete provider-local contracts, mappings, validators and effects, without cross-provider shared ontology reuse | Implemented by local_baseline.py and provider-local descriptions; 20-case A/B correctness parity tested in Milestone 4.1; human review pending |
| B: JSON + shared semantics | Shared IDs, explicit mappings, constraints/effects/evidence and reusable validation | V2 JSON provider manuals and common registry/pipeline; A/B fixture evidence only |
| C: RDF + shared semantics | Exactly the same supported semantic information and validation as B | V2 Turtle manuals and common registry/pipeline; A/B fixture evidence only |

Do not substitute a raw HTTP client for condition A or omit preconditions/evidence
checks to make that baseline cheaper or worse. Its externally judged correctness,
goals and mandatory constraints must be identical. Its implementation now exists; review and freeze the complete candidate before
unsealing for a three-condition comparison. A shared-semantics-only
study is a different approved scope decision, not a silent replacement of the
frozen experimental conditions.

## Pre-freeze evidence sheet

Each item requires artifact hashes, reviewer, date and pass/fail/not-run. Approval
is currently null; checked implementation facts below are not formal sign-off.

- [x] JSON and RDF A/B manuals decode to equal typed Contract/ProviderProfile
  objects in the current bounded profile, including constraints and every mapping.
- [x] Both use the same schema/semantic validator, input rules, three-valued
  preconditions, transport adapter, independent goal verifier and failure policy.
- [x] Differential tests compare outcomes and reasons on fresh identical fixtures,
  keeping raw/canonical observations. Only documented metadata is normalized.
- [x] Operation-name similarity is not capability equivalence. Unknown transitions,
  unsupported transforms and missing constraints cannot silently enable execution.
- [ ] Independent review of semantic content for both representations against a
  neutral information sheet, before runtime results are seen.
- [x] A complete API-local baseline with equally strong tested correctness obligations on visible A/B.
- [ ] Approved task list, seeds, scenario counts, budgets, condition order and
  contributor exposure plan, all registered before unsealing.
- [x] Prospective append-only cost collector implemented and tested; policy approval still pending.
- [ ] Investigator approval of cost collector and allocation.
- [x] Provider-neutral task predicates and separate native-state observation implementation.
- [ ] Independent human review/sign-off of native observers and expected states.
- [ ] Clean versioned baseline or approved archived candidate identity and signed
  investigator approval, with pinned evaluation environment artifacts.

## Semantic equivalence checklist for each operation

Record exact correspondence for artifact identity, local operation identity,
shared capability ID, required inputs/types, units/timezone/precision, required
critical preconditions and their TRUE/FALSE/UNKNOWN evidence rules, expected
transition, mandatory constraints, binding method/path, response identifier,
request field transforms, observed field transforms, complete snapshot semantics,
revision consistency, observation endpoints and evidence age bounds. Preserve
negative/unknown information and missing-value meaning. A prose assertion cannot
replace executable validation in either condition.

Known v2 equivalence is at the typed execution boundary, not arbitrary JSON/RDF
syntax. V2 supports one capability, closed scalar transforms and known constraint
keys. JSON duplicate keys/items reject; repeated identical RDF triples collapse
as graph semantics, while ambiguous cardinality and unknown assertions reject.
RDF nodes/prefix order and JSON member order are nonsemantic. Representation-
specific parser diagnostics may differ; whether an action executes or verifies
must not. Unsupported constructs must be outside both accepted semantic domains,
not a secret extra feature for one condition. Shared vocabulary text is not a
separate reasoning engine: runtime knowledge also resides in frozen constants,
schemas and validators, all included in the manifest.

Use the same independent task goals and oracle expectations, service snapshots,
initial state, capability catalog and mandatory goal constraints for every
condition. Reinitialize fixtures per run; do not let one condition inherit events,
warmed query outputs, cached task answers or provider-specific repairs. Declare
cache policy and run order. Use the same timeouts, retry budgets, evidence-age
policy and resource limits; representation differences must not create unequal
access to service documentation or semantic knowledge. No LLM is required here.

## Cost and contamination checks

Inventory ontology/capability design, generic engine, transport/oracle, provider
documentation, contracts, mapping annotation, representation conversion,
independent review, adapters, tests, failures, debugging and maintenance. Count
shared semantic assets consistently for B and C; do not charge authoring to JSON
while granting RDF a prebuilt manual, or the reverse. Preserve the asset creation
cost and report stand-alone and joint-reuse allocation separately.

Log who saw which provider documents, tasks, manual versions and outputs and when.
Conversion between formats is allowed for parity but its cost and provenance
must be recorded. Both formats currently originate from the same authoring task;
that is not evidence of independent annotation reliability. Independent review
is still required. Order/learning effects are controlled prospectively; existing
AI-authored A/B elapsed logs cannot stand in for randomized human experiments.

## Failure handling and release rule

Any mismatch in supported capability meaning, constraints, effects, transformation
or validation power stops confirmatory execution. Preserve the mismatch, classify
representation, mapping, environment or generic defect, and obtain a reviewed
pre-unsealing correction or restart under a new candidate. Never weaken the
stricter condition after seeing held-out results. HTTP success is not a success
metric without observed and independently verified achievement. Unknown evidence
must not be normalized into TRUE or excluded from denominators.

The final parity sheet must list all deviations and signatures. Unchecked items
are approval gates, not tasks to complete using Provider C knowledge.

## Milestone 4.1 functional parity evidence

The 20 public single-action apparatus tasks run on both visible providers under
all three conditions (120 controlled executions per suite). Each condition is
checked against separately specified expected calls, runtime verification,
native achievement and final conjunction. Cross-condition summaries also match:
compatibility, observed state applicability when probed, mutation-call count,
HTTP-call success, runtime verification, native verification and final verified
achievement. JSON/RDF typed models remain equal for every task variant. Raw
traces/reasons and native state are retained; static rejections do not invent a
state precondition verdict when no probe occurred.

Condition A uses explicitly selected CalendarLocal/BookingLocal operations,
provider-local JSON descriptions, validators and encoders. It imports no shared
contract loader, transform language, ontology ID or semantic registry. It reuses
neutral Goal/Truth/Observation/transport/oracle code only. It has equivalent
functional correctness obligations, not information equivalence in discovery:
its provider-local code stores its validation and wire knowledge, while B/C use
shared identifiers, schema and mappings. It may reuse ordinary provider-local
validation utilities; that setup is charged to A rather than counted as free.

The untransformable-input control uses an unsupported local encoding in A and
an unavailable mapping source in B/C; both express an unavailable valid conversion
and reject without mutation. Unsupported shared primitive names remain separate
schema regression controls. Parser messages and operation catalogs are not forced
to match across A versus B/C. No throughput or cost advantage is inferred from
the common diagnostic results. A real integrator must maintain each local binding;
this author had prior access to shared manuals and makes no blind-authorship claim.

The deliberate incorrect-output-map task fools the runtime verifier in all three
conditions while the independent native reader rejects the real stored title.
A run is counted verified only when both verifiers accept; this closes the prior
transport-interpretation loophole at evaluation time without changing goal truth
or pretending the subject's runtime verifier is mapping-independent. Full raw
before/after fixture state is checked for changes to existing records, including
fields outside the subject's canonical projection.

Technical coverage does not substitute for an independent annotator/integrator,
sealed holdout, multi-step pilot scope, approved cost allocation or investigator
sign-off. The frozen PDF is now available and governs those remaining decisions.
