# Reset isolation — visible A/B V3 apparatus

Status: bounded fixture evidence, not external-service reset certification.
`run_pilot` allocates a new Scenario/BookingScenario and loopback server per run,
reserves a never-existing output directory, then invokes `assert_reset` before any
subject launch. The normal run has one known sentinel event, TRUE permission,
zero revision and mutation counters, and zero pending requests. `reset.json` retains
the raw native snapshot, independent expected state and named gate verdicts.

| Axis | Evidence / enforcement | Negative control |
| --- | --- | --- |
| Native records and metadata | Exact raw dictionary equality to `initial_records`; ISO A and epoch-ms B encode the same sentinel interval/title | Extra/changed records reject |
| Permission | Native initial permission must be TRUE | null permission rejects |
| Revision | Initial native revision/version exactly zero | Nonzero revision rejects |
| Mutation counter | Initial fixture call count exactly zero | Retained contaminated run starts at 7 and rejects before subject launch |
| Pending requests | Initial local server counter zero | Injected pending counter rejects |
| Subject process | Each run calls Popen in a new session, never reuses a subject; prior leader reaped and process group stopped | Gate rejects a caller reporting live prior subject; retained PIDs and stop results support lifecycle review |
| Capability resolution cache | No persistent resolution cache exists in these bindings; B/C instantiate Registry afresh per action and workers restart per run | Nonzero cache input rejects; this is an architectural inference, not an instrumented scan of arbitrary process memory |
| Trace persistence | Run directory uses exist_ok=False; reset gate checks it was empty; action evidence uses fresh step paths | Existing supervisor/trace locations reject rather than overwrite |
| Fixture lifecycle | New server/thread per run; context shutdown, close and join after capture | Raw per-run counter/state snapshots cannot inherit another run's records |

The reset gate's process/cache fields reflect the controlled runner construction;
they are not external attestation. The subject has not been spawned at pre-run reset,
and there is no subject to query at that point. Fresh PIDs and no-cache construction
are distinct from direct native-state measurement. A future cached engine or service
must expose/review its reset mechanism rather than reuse these assertions unchanged.
Parent evaluation process reuse is allowed; fixture state and subject process are not
reused. No external persistence layer, concurrent service user or hidden remote state
is modeled or certified here.

Tests: `test_multistep.OperationalTests.test_each_reset_axis_detects_contamination`,
`test_contaminated_reset_rejects_before_subject_launch`,
`test_repetitions_have_equivalent_clean_state_and_distinct_processes`, and
`test_invalid_budget_and_existing_trace_reject`. Two repetitions of M01 under A/B/C
use equal initial snapshots and distinct subject PIDs. The retained sweep includes
an additional positive repetition for both visible providers and all three conditions.

Machine-readable retained evidence:

- `artifacts/milestone4_3/pilot/*/reset.json`: expected and actual per-run native state.
- `pilot/pilot-results.json`: all 60 main matrix runs and 6 extra positive repetitions.
- `pilot/repetition-2-*/supervision.json`: distinct process identities and stop results.
- `pilot/contaminated-reset-a-A/reset.json`: mutation counter mismatch, passed=false.
- `pilot/contaminated-reset-a-A/evaluation.json`: RESET_REJECTED, subject_launched=false.

The contaminated attempt has no subject-input file or mutation trace. It remains
visible as a rejected attempt, not removed from operational evidence. Normalized
cross-condition summaries omit run IDs, PIDs, observation timestamps and serialization
metadata but retain semantic verdicts, mutation counts, partial state size and
uncertainty. Raw state and timestamps remain archived, not discarded. Different
provider-native field names are not an information advantage for any condition.
