# Operational supervision — V3 apparatus

Status: implemented bounded Linux/local-fixture supervision; approval pending.
No Provider C access or confirmatory evaluation is authorized by this protocol.

## Deadline and lifecycle

Each subject runs in a fresh Python process/session. `supervision.supervise` starts a
monotonic outer clock before Popen, waits only the remaining budget, records TIMEOUT,
sends SIGTERM to the process group, allows 0.5 seconds termination grace, then SIGKILLs
the group and reaps the leader (bounded wait). The 60-second default includes imports
and execution. Shutdown/observation can exceed that execution deadline and is separately
visible. Five-second HTTP timeouts remain unchanged; zero automatic retries and zero
planner/repair iterations apply. This is not resumable execution.

The evaluator owns the fixture server in the parent process. The subject cannot end
that service by exiting. A native POST journal records before/after states and response
status, independent of subject output. After stop, `settle_and_capture` waits at most
1.5 seconds for fixture pending-request counters, then records raw native state.
A pending service mutation is uncertain until independently settled/observed. A
remaining pending counter means state_uncertain=true and no verified success. This
window is a controlled fixture observation policy, not proof about arbitrary services.

Deliberately delayed follow-up tests show a mutation can finish after the subject is
killed. The final native goal may be true, but TIMEOUT always forces verified=false.
No claim of remote cancellation or distributed atomicity is made. Arbitrary externally
queued/asynchronous effects cannot be ruled out by a local pending counter and are
unsupported by this profile. The evaluator does not send compensation or repeat POSTs.

A service timeout is distinct: the request returns an API result with null HTTP status
and timeout error, while outer supervision may report COMPLETED and the sequence
INCOMPLETE. A nonzero subject exit is PROCESS_ERROR. HTTP errors retain actual status.
None is automatically a verified sequence. CLI diagnostic_passed may be true for an
expected negative; that is never successful goal achievement.

## Evidence and partial execution

Before mutation, reserve new run directories and archive reset evidence, curator
expectation, subject input and supervision STARTING/RUNNING record. The sequence trace
is atomically replaced after each decision/observation with fsync before replacement.
Each validated action retains its own trace. A forced process kill can prevent the
in-flight action's finally block from producing a full trace: keep the preceding
sequence snapshot, earlier action traces, subject stdout/stderr and service-side
native transition journal. Missing traces are uncertainty, not nonexistent actions.
The parent records supervision and actual automated runtime to a new hash-chained
resource ledger. Human-active and supervision time remain null unless measured.

Archive process exit code, PID, outer budget, timeout status, whether the leader was
reaped, pending-at-stop count, observation wait, final native state and both runtime
and native verdicts. A completed fixture journal can explain late side effects but
cannot retrospectively make an interrupted runtime observation valid.

## Validation and stop procedure

`test_multistep.OperationalTests` covers a deliberately stalled process; in-flight
late mutation under A/B/C; HTTP versus outer timeout; invalid budgets; immutable output
locations; reset contamination; and an unsettled observation window. The normal pilot
uses 60 seconds; tests use explicit shorter budgets (0.15 s isolated stall; 1 s delayed
follow-up) with a 1.5-second fixture delay, and a 5.2-second delay for HTTP timeout.
Actual logs and retained operational examples identify each intervention.

Stop affected evaluation on unexpected mutation, unplanned oracle disagreement,
reset mismatch, source/dependency drift or supervisor failure. Preserve partial state,
failed attempts and costs. A generic defect requires a new candidate and the existing
exposure/restart rules; no hidden retries or task-specific repair. Manual service
recovery in M08 does not resume the subject or skip required actions.
