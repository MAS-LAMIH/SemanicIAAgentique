# Sequence profile version 1

These are controlled visible-provider additions for V3, not a revision of the
single-action contract v2 schema. `a.json`/`a.ttl` and `b.json`/`b.ttl` have equal
typed semantics under `sequence_bindings.load_shared`.

Every record has exactly these mandatory fields: integer `version=1`, named
`operation_id` (urn), `effect` (`NewEventAfterPredecessor` or the explicitly
incompatible `ReservationOnly`), boolean-true `requires_predecessor` and
`requires_after_end`, `create_path_template` (local path ending in `/{id}`), and
`base_manual` (relative in-repository v2 contract). JSON rejects duplicate keys
and nonfinite constants. Turtle has exactly one `seq:Profile`, exactly one literal
per field and no other assertions, using namespace
`https://example.org/sam/sequence/v1#`. Plain strings, integers and booleans only;
unknown keys, ambiguous cardinality, malformed values and unsafe references fail.
`base_manual` is representation provenance; equality compares its loaded typed
Contract, not its filename suffix. No remote dereferencing occurs.

`{id}` is the actual immediately prior action result's identifier, validated before
path substitution. A concrete v2 action manual is materialized in each action's
trace directory with that local path, operation ID and unchanged base semantic
validation/bindings. The sequence guard is an additional explicit applicability
requirement, checked on fresh observations for every dependent action. Only the
existing registry/validated action executor invokes mutations. This is bounded
conditional event creation, not a general transition language or automatic plan.

Condition A uses `../api_local/{a,b}-followup.json` and ordinary local code with
the same dependency/temporal/effect obligations; it does not use shared discovery.
See `docs/MULTISTEP_PROFILE.md` for the exact execution and observation boundary.
All authoring is by the same previously exposed AI contributor. Independent human
content review and scientific approval remain pending.
