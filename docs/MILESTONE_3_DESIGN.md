# Milestone 3 audit and design (recorded before core changes)

No frozen protocol PDF was found; the supplied frozen decisions and Milestone 3
brief govern. The baseline consists of finite v1 loaders, immutable Contract,
calendar-oriented Executor, independent observation oracle, and 35 deterministic
tests. Original tutorial modules are unrelated and remain unchanged.

The v1 model hardcodes HTTP paths and identity mappings. Small reversible change:
retain v1 verbatim, add an optional typed provider profile to Contract and a v2
frontend. JSON and RDF v2 descriptions produce identical data validated against
one packaged schema and one semantic validator. Shared knowledge lives in a
separate vocabulary/profile, not in provider-ID branches in the engine.

A remains the existing REST artifact. B is a separately implemented local booking
API with /availability, /bookings, /booking/{id}, millisecond timestamps, different
wire keys and identifiers, a 15-minute grid and maximum two-hour duration. Write
its API documentation before its manual. This is architectural independence of
the controlled services, not a claim that independent external organizations or
human contributors authored them. Both fixtures are authored in this task.

A generic finite transformation adapter uses declared field mappings and a closed
transform vocabulary. No arbitrary Python, mapping inference, provider lookup
switches, substitution table, or silent lossy time conversion. A capability
registry accepts local manual paths and separately configured loopback origins.
Resolution checks exact declared capability, required modeled effect, input
transformability, known constraints and preservation of other events, then probes
critical applicability using the common evaluator. Execution must revalidate
through Executor.run; resolver selection never bypasses it.

The existing independent oracle stays unchanged and sees canonical observed
snapshots. Raw wire evidence is retained alongside mapped evidence. Trusted
mappings and complete single-writer snapshots remain assumptions; this is not an
oracle independent of the entire observation transport. JSON/RDF must expose the
same maps/constraints/evidence rules. Negative fixtures test names versus effects,
untransformable inputs, mandatory constraints, FALSE/UNKNOWN, and false success.

No Provider C implementation, hidden requirements or benchmark answers are used.
Freeze preparation will list generic/shared/provider/oracle/test/dependency files
and describe a future immutable, reviewed baseline; this milestone does not claim
an already frozen confirmatory experiment. Cost logging separates nonoverlapping
measured shared work and provider onboarding where instrumented, and explicitly
leaves unmeasured historical effort unknown.
