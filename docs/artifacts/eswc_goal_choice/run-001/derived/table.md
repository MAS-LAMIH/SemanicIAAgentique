# Bounded goal-choice results

| case | policy | status | choices | goal_state_satisfied | independently_verified | calls | passed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G01 | semantic | SATISFIED_AFTER_ACTION | ['a'] | True | True | [1, 0] | True |
| G01 | procedural | SATISFIED_AFTER_ACTION | ['a'] | True | True | [1, 0] | True |
| G02 | semantic | SATISFIED_AFTER_ACTION | ['b'] | True | True | [0, 1] | True |
| G02 | procedural | SATISFIED_AFTER_ACTION | ['b'] | True | True | [0, 1] | True |
| G03 | semantic | SATISFIED_AFTER_ACTION | ['a'] | True | True | [1, 0] | True |
| G03 | procedural | SATISFIED_AFTER_ACTION | ['a'] | True | True | [1, 0] | True |
| G04 | semantic | NO_ELIGIBLE_ACTION | [] | False | False | [0, 0] | True |
| G04 | procedural | NO_ELIGIBLE_ACTION | [] | False | False | [0, 0] | True |
| G05 | semantic | SATISFIED_AFTER_ACTION | ['a', 'b'] | True | True | [0, 1] | True |
| G05 | procedural | SATISFIED_AFTER_ACTION | ['a', 'b'] | True | True | [0, 1] | True |
| G06 | semantic | NO_ELIGIBLE_ACTION | [] | False | False | [0, 0] | True |
| G06 | procedural | NO_ELIGIBLE_ACTION | [] | False | False | [0, 0] | True |
| G07 | semantic | UNKNOWN_CONTEXT | [] | False | False | [0, 0] | True |
| G07 | procedural | UNKNOWN_CONTEXT | [] | False | False | [0, 0] | True |
| G08 | semantic | UNCERTAIN_MUTATION | ['a'] | True | False | [1, 0] | True |
| G08 | procedural | UNCERTAIN_MUTATION | ['a'] | True | False | [1, 0] | True |
| G09 | semantic | SATISFIED_EXISTING | [] | True | True | [0, 0] | True |
| G09 | procedural | SATISFIED_EXISTING | [] | True | True | [0, 0] | True |
| G10 | semantic | NO_ELIGIBLE_ACTION | [] | False | False | [0, 0] | True |
| G10 | procedural | NO_ELIGIBLE_ACTION | [] | False | False | [0, 0] | True |
| G11 | semantic | EXECUTION_FAILED | ['b'] | False | False | [0, 1] | True |
| G11 | procedural | EXECUTION_FAILED | ['b'] | False | False | [0, 1] | True |
