# Visible-provider multi-step diagnostics — prospective apparatus, not confirmation

Status: technical V3 pilot, investigator review pending. Provider C remains sealed.
The ten task definitions live in `multistep_tasks.pilot_tasks`; machine-readable
results and per-run curator expectations are retained under
`artifacts/milestone4_3/pilot-final/`. This is 10 tasks × 2 visible providers × 3 conditions
= 60 executions per sweep, not 60 providers. A/B are exposed development fixtures.
Existing 20 single-action diagnostics remain unchanged. No LLM/planning experiment
or general-purpose workflow claim is made.

All tasks have two goals, except M08/M09 with three. Goal i is a required appointment
on 2030-01-07 UTC, [09+i,10+i] hours for i starting at zero, with task-specific title
`Mxx required appointment i+1`. Both services initially have one pre-existing event
on 2030-01-06 09:00–10:00 UTC with a metadata sentinel. Permissions start TRUE,
revision/mutation counters zero. Every next event must reference the prior newly
created event and start at or after its end. Every prior record and metadata must
remain unchanged. Required evidence age is 30 seconds, complete snapshots and
revision transitions are mandatory. Every action receives a fresh state observation.

| ID | Intervention / required transition | Independent expected outcome |
| --- | --- | --- |
| M01 sequential dependency | Create prerequisite, then create its follow-up | 2 calls, 2 new records with native link, all transitions and goal verified |
| M02 state-updated applicability | Service revokes permission after first creation | Second action FALSE/REJECTED using fresh state, 1 call, partial first record retained, final incomplete |
| M03 intermediate failure | Follow-up endpoint returns controlled 500/503 | 2 attempted calls, only first record exists, final incomplete |
| M04 unknown evidence | Permission becomes null after first creation | Second action UNKNOWN/BLOCKED, 1 call, partial state retained |
| M05 unsafe substitution | Similar follow-up operation advertises reservation-only effect | Non-equivalent effect rejected without invoking second action, 1 call |
| M06 forbidden side effect | Follow-up also changes unrelated calendar content | 2 calls; runtime/native reject; preserve full raw evidence |
| M07 no-op success | Follow-up returns 201 but stores nothing | 2 calls; no verified second transition or progress; incomplete |
| M08 recovery boundary | Three required actions; second transiently fails | 2 calls only, third unattempted; service is made available after run but no retry/resume/compensation occurs |
| M09 three-step chain | Create prerequisite, follow-up, follow-up to that follow-up | 3 calls and 3 independently verified transitions; all links and whole-state preservation checked |
| M10 stale evidence | Permission timestamp becomes stale after first creation | Next dependency observation UNKNOWN/BLOCKED, 1 call; no stale-state continuation |

The service itself rejects missing predecessor and overlapping follow-up intervals,
including direct calls that bypass subject orchestration. Negative tests demonstrate
this separately. The exact initial native A/B fields differ but encode the same
sentinel event. Calendar follow-up stores `predecessor_id`; booking stores
`previous_booking`. The evaluator interprets these independently of subject maps.

Curator expectations are fixed from domain goals and fixture behavior before subject
launch and archived as `curator-expectation.json`. The subject input file contains
only formal goals, selected condition/contracts and origin, not expected verdicts or
oracle answers. Subject and evaluator use the same task inputs; separation of data
paths is not independent human authorship. The author had prior A/B manual exposure;
a separate investigator-appointed curator must review all predicates/interpretations.

Normal runs use the same 60-second outer budget, 5-second per-request timeout, zero
retries/repair iterations, new process and fixture per run across A/B/C. Deliberate
short-budget/slow-service tests are labeled operational interventions, not silently
substituted for these pilot budgets. An HTTP error is an attempted action, never a
completed required action. The no-op control cannot allow skipping the missing goal.
Recovery is a stopping boundary, not replanning or automatically successful repair.

Unsupported: arbitrary lengths/dependency graphs, branching, update/delete, different
capabilities, cross-provider transactions, compensation, external services and new
transformation primitives. Such demands require a separately reviewed profile/candidate,
not reinterpretation of this bounded pilot. These added diagnostics demonstrate
multi-step coverage of a narrow chain; they do not certify full confirmatory E1,
independently authored providers, human cost savings or RDF superiority.
