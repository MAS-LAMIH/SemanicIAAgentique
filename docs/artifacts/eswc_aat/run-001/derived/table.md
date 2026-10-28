# Agentic AAT results

| case | policy | status | choices | native_goal | accepted | mutations | passed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | semantic | SUCCESS | ['/heat'] | True | True | 1 | True |
| R01 | procedural | SUCCESS | ['/heat'] | True | True | 1 | True |
| R02 | semantic | SUCCESS | ['/cool'] | True | True | 1 | True |
| R02 | procedural | SUCCESS | ['/cool'] | True | True | 1 | True |
| R03 | semantic | SUCCESS | ['/heat', '/cool'] | True | True | 1 | True |
| R03 | procedural | SUCCESS | ['/heat', '/cool'] | True | True | 1 | True |
| R04 | semantic | SUCCESS | [] | True | True | 0 | True |
| R04 | procedural | SUCCESS | [] | True | True | 0 | True |
| R05 | semantic | NO_ELIGIBLE | [] | False | False | 0 | True |
| R05 | procedural | NO_ELIGIBLE | [] | False | False | 0 | True |
| R06 | semantic | UNKNOWN_CONTEXT | [] | False | False | 0 | True |
| R06 | procedural | UNKNOWN_CONTEXT | [] | False | False | 0 | True |
| R07 | semantic | UNKNOWN_CONTEXT | [] | False | False | 0 | True |
| R07 | procedural | UNKNOWN_CONTEXT | [] | False | False | 0 | True |
| R08 | semantic | CONFLICT | ['/heat'] | False | False | 0 | True |
| R08 | procedural | CONFLICT | ['/heat'] | False | False | 0 | True |
| R09 | semantic | UNCERTAIN_MUTATION | ['/heat'] | True | False | 1 | True |
| R09 | procedural | UNCERTAIN_MUTATION | ['/heat'] | True | False | 1 | True |
| R10 | semantic | POSTCONDITION_FAILED | ['/heat'] | False | False | 1 | True |
| R10 | procedural | POSTCONDITION_FAILED | ['/heat'] | False | False | 1 | True |
| R11 | semantic | POSTCONDITION_FAILED | ['/heat'] | True | False | 1 | True |
| R11 | procedural | POSTCONDITION_FAILED | ['/heat'] | True | False | 1 | True |
