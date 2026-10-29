Turn 1: proposed discover [c00005].
Turn 2: proposed observe [c00009].
Turn 3: proposed use [c00014]. POST /heat; recorded applicability=TRUE, goal contribution=TRUE [c00022]. Alternatives: /cool applicability=TRUE, contribution=FALSE [c00015]. Recorded forecast targets={"urn:example:room:temperature":22} (predicted, not observed). Recorded goal truth=FALSE [c00013]. Guard=AUTHORIZED [c00029].
Recorded terminal status=POSTCONDITION_FAILED [c00032]; verified=False [c00033].
Recorded runtime checks={"echoes":true,"evidence":true,"expected_state":false,"goal":true,"mutations":true,"response_revision":true,"revision":true} [c00035].
Reconstructed effect_comparisons: urn:example:room:temperature=TRUE [c00039].
Reconstructed frame_comparisons: urn:example:room:cooler=TRUE [c00040], urn:example:room:heater=TRUE [c00041], urn:example:room:unrelated=FALSE [c00042].
Separate native-scoring plane: {"external_changes":0,"frame_preserved":false,"goal_state":true,"incorrect_native_transitions":1,"mutations":1,"native_success":false,"requests":1,"revision_accounted":true,"unauthorized_mutations":0} [c00044]. This must not be treated as an agent observation.
Unavailable: actual per-atom runtime verdicts, permit contents, evaluation clock and hidden intent. Raw predicate/frame replays are explicitly reconstructed, not general causal identification.
