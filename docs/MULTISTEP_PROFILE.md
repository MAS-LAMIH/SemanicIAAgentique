# Bounded sequence profile 1 — candidate V3, approval pending

This is declared finite execution, not planning, replanning or arbitrary workflows.
A plan contains two or three immutable event goals; action zero creates a prerequisite,
and every later action creates a follow-up to the immediately previous action. The
follow-up must reference an actual stored predecessor and start at or after its end.
The service enforces this dependency too. This is not unrelated creation repeated.

Visible A/B originally supported creation only. Controlled follow-up fixture operations
are new, authored by the already exposed Codex contributor, not independently developed
provider features. Calendar uses `/followups/{id}` with ISO fields and `predecessor_id`;
booking uses `/booking-after/{id}` with integer milliseconds and `previous_booking`.
Both preserve existing records. Booking retains quarter-hour and two-hour restrictions.
No Provider C material was used. No portability or labor-cost result is inferred.

## Representation and execution boundary

Condition A has local follow-up descriptions and provider-local validation/encoding.
It does not import semantic discovery. B/C sequence profiles contain equivalent
operation identity, effect, explicit dependency predicates, URL template and base
single-action manual; the base manual loads to the same typed v2 Contract. A profile
is not a new general capability language: only event creation after an observed
predecessor is supported. The dependency rule is explicit in each condition, not
silently inferred from an operation name. The misleading-effect profile is rejected.

A predecessor ID is a runtime output reference, never an oracle answer. A fresh
wire baseline must establish the predecessor's event identity/properties, a nonnegative
interval gap, and current permission before the dependent action. FALSE rejects;
missing/stale/malformed critical evidence is UNKNOWN and blocks. Existing validated
LocalExecutor or Registry/Executor performs the actual mutation and fresh permission
assessment again. The sequence layer has no raw POST path, no provider substitution,
no compensating action and no automatic retry. There is one attempted invocation per
declared action, at most. Each action must runtime-verify; apparent final state cannot
skip a required action. Partial state and traces remain after failure.

Goals and all required actions are fixed before execution. The subject sees only its
plan and contracts, not expected scenario verdicts or native oracle predicates. The
evaluator owns native snapshots, transition expectations, raw link interpretation and
call-count/safety checks. Final correctness requires every required intermediate
transition, final goal predicates, raw preservation, correct native links and complete
runtime verification. A sequence with an omitted action fails even if similar events
already exist. Native adjudication reuses the unchanged single-action oracle and
native decoders for each transition and separately checks the entire sequence.

## Non-goals and unsupported inputs

Other lengths, branching, update/delete, cross-provider atomic transactions, parallel
execution, arbitrary transition predicates, compensation, resume/retry and autonomous
selection are unsupported and must reject. Profile keys/cardinalities and local path
references are closed; unknown effects do not execute. Shared validation is procedural
and finite, not general OWL reasoning. New profiles are a V3 addition and never alter
V2's identity. Scientific approval and future-provider unsealing remain pending.

## Evaluator-owned observation extension

`ChainInterpretation` accepts an existing `NativeInterpretation` and a native
predecessor-relation reader, bound to the same provider identity and provenance.
Unknown identities fail closed without this trusted curator-owned binding. The
subject manual must never choose it. Goal truth, exact required transitions and
raw preservation remain unchanged; no provider-specific expected answer is accepted.
The observer reference is not proof of independent human review. A synthetic
in-memory test exercises the boundary without another service or Provider C material.
