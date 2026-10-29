# Radicale held-out Provider C feasibility result

**Negative compatibility finding: stop before integrations.** Radicale runs and
accepts genuine CalDAV event creation, but the frozen V4 profile cannot express
its protocol. This is a provider-specific counterexample to unrestricted Web API
generalization, not a failed HTTP service setup or evidence that semantic capability
descriptions cannot work in a broader implementation.

## Identity and methodology

Frozen baseline: `87309bca7456f3d8df827549761052cd467a3f7b`.
Assessment parent: `06c7ee364eef29b0e19d3d3b448f2d294774a4e4`.
The investigator selected Radicale and authorized direct inspection/native tests.
This assessment follows `V4_HELD_OUT_METHOD_AMENDMENT.md`: shared evaluation and
integration authorship, no independent curator/blinding claim, no measured effort
or population generalization. The earlier missing-material report is historical;
Radicale is now the supplied real candidate, not an invented replacement API.

Pinned existing release: **Radicale 3.5.0**, official project
<https://github.com/Kozea/Radicale>, documentation <https://radicale.org/v3.html>.
Source distribution was retrieved from PyPI and its SHA-256 checked against the
release metadata; wheel checksum was also matched. Source archive SHA-256:
`cdb4de6a10d7da9993727c3c3d9c2b30256d36915f4d6b2a655b8dd38f8de5eb`.
The archive, wheelhouse, metadata and checksums are retained, not just live URLs.
This release was selected by version before testing, not adapted to V4.

Python 3.12.14. Exact resolved runtime dependencies:

```text
defusedxml==0.7.1
passlib==1.7.4
pika==1.4.4
python-dateutil==3.0.0
pytz==2026.5
Radicale==3.5.0
six==1.17.0
tzdata==2026.6
vobject==0.9.9
```

`requirements-hashed.lock` pins every wheel with a SHA-256, and `pip check`
passed. The optional bcrypt/LDAP/test packages are not installed or needed for
this anonymous loopback native feasibility probe. These are Radicale assessment
dependencies, not additions to V4's runtime/dependency files.

## Actual native evidence

The standalone `native_probe.py` directly invokes Radicale with stdlib HTTP; it
imports no V4 module and implements no proxy, semantic adapter or translation
service. Configuration explicitly binds loopback with anonymous test-only rights
and fresh temporary filesystem storage; it is not a deployment/security profile.
Radicale is the original installed service, not an emulated API.

Two successful cycles, with server stopped and storage removed between cycles:

| Native operation | Observed result in each cycle |
| --- | --- |
| GET absent event | 404, showing fresh resource state |
| MKCALENDAR `/calendar/` | 201 |
| PUT `/calendar/native-event.ics`, `text/calendar`, `If-None-Match: *` | 201, empty body, ETag header |
| GET same resource | 200, `text/calendar`, expected VEVENT |
| Repeat conditional PUT at occupied resource | 412, native event bytes unchanged |

The actual text/calendar body uses VCALENDAR/VEVENT, UID
`radicale-native-preflight-001`, SUMMARY `Native CalDAV event`, UTC DTSTART
`20300107T100000Z`, DTEND `20300107T110000Z` and DTSTAMP. Retrieved and original
native event files contain exactly one VEVENT and match those values. Checks use
explicit native field strings/UTC values, not semantic description mappings.
This establishes real create/retrieve/rejection and reset feasibility, not the
complete 16-family correctness gate. No call-counter or revision invariants are
invented: this probe observes native files, resource status and ETag only.

The **initial probe failed** after HTTP create/retrieve when a recursive `.ics`
lookup included Radicale's binary cache entry. Its original script, traceback,
server log and process record remain in `native-run-001/` and associated files.
The original temporary native storage was deleted on exception and is unavailable;
no reconstructed snapshot is asserted. The corrected probe excludes `.Radicale*`
cache paths, records each HTTP response immediately and snapshots storage before
assertions. It then passed both cycles (exit 0, 0.343710 s command wall time).
This correction concerns native evidence selection, not V4 or Radicale behavior.
Every executed probe is disclosed; the failed probe was not relabeled successful.

Raw evidence: `docs/artifacts/v4_radicale_feasibility/`, including HTTP trace,
server logs/configs, native filesystem copies, requests/responses, process records,
package pins, source archive and sealed hash inventory. Source/docs reflect
Radicale 3.5.0 plus the separately archived current documentation (not assumed a
version-pinned specification). RFC 4791 and RFC 5545 snapshots provide CalDAV and
iCalendar protocol references; installed release code is authoritative for observed
behavior (`radicale/app/put.py` returns CREATED, ETag and no response body).

## Frozen compatibility boundary

| Requirement | Provider description alone? | Frozen limitation |
| --- | --- | --- |
| CalDAV HTTP PUT | No | `descriptions.py:48` permits only POST; `http.py:22` sends POST regardless of operation metadata |
| VEVENT request body | No | `http.py:22` JSON-encodes a dictionary; fixed application/json header; no raw-body/content-type control |
| iCalendar field encoding | No | `mapping.py:22` has identity/ISO-epoch conversions only, no VCALENDAR/VEVENT assembly, escaping or iCalendar timestamps |
| Resource URL / UID | No | `descriptions.py:50` permits fixed local paths, not per-event templates; no UID input/generator or body/URL binding |
| Response / returned id | No | `http.py:25` expects a JSON object; `send` maps its fields to nonempty id; actual PUT returns empty body and ETag, while UID/resource URL are client-selected |

In-memory probes modifying the existing **visible A** example (not constructing C
artifacts) confirm fail-closed errors `Only POST operations are supported` and
`Expected a fixed local operation path` for the tested `.ics` resource URL.
The `.ics` suffix itself is conventional, not required for every CalDAV URI;
choosing another constant URI would not solve the PUT, body, response or dynamic
resource/UID limitations. ETag is a resource revision token, not a replacement
for event UID or a returned JSON identifier. These distinctions must not be hidden.

Provider descriptions can rename supported fields, identify a capability/provider,
select a permitted constant path and select existing exact conversions/limits.
They cannot define methods, serializers, custom headers, URI templates, UID
creation or response-from-header/request mapping beyond the frozen profile.
Those would require shared runtime/schema changes. JSON and RDF share this same
limitation; there is no evidence of a representation-specific advantage here.

An ordinary bespoke CalDAV adapter could potentially handle these operations in
Condition A, but none was implemented or scored: the investigator explicitly
requires stopping if the frozen runtime is incompatible. Therefore A's condition
gate outcome is **not evaluated**, and B/C are **unsupported by the frozen
profile**, not observed failed integrations. Functional parity of a three-arm
held-out run is untested. No JSON-to-CalDAV proxy, monkeypatch, substitute API,
provider integration description, A adapter or amended runtime was created.

## Reproduction and stop decision

From repository root, with a new environment and new result destination:

```sh
python3 -m venv /tmp/radicale-native-env
/tmp/radicale-native-env/bin/python -m pip install --no-index --find-links docs/artifacts/v4_radicale_feasibility/packages --require-hashes -r docs/artifacts/v4_radicale_feasibility/requirements-hashed.lock
/tmp/radicale-native-env/bin/python docs/artifacts/v4_radicale_feasibility/native_probe.py --python /tmp/radicale-native-env/bin/python --output /tmp/radicale-native-new
```

Use distinct paths; the probe refuses overwriting existing evidence. Native data
and rights configuration are synthetic and local. No model access, authentication
credentials, containers or agent sessions are needed. SHA-256 verification:

```sh
python3 - <<'PY_VERIFY'
from pathlib import Path
import json, hashlib
p = Path('docs/artifacts/v4_radicale_feasibility')
for name, expected in json.loads((p/'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest() == expected, name
print('PASS')
PY_VERIFY
```

The unchanged V4 regression suite passed **20 tests**, exit 0 (see
`v4-regressions.log` and its command record). Loader rejection probes and both
corrected native cycles also passed; `pip check` reported no broken requirements.

All **35 readiness baseline hashes match**, including all shared runtime files,
vocabulary, A/B integrations, catalogue and evaluation infrastructure. No existing
tracked file was changed. This result stops at feasibility: no concrete integration
gate commit, no 144-slot condition matrix and no successful held-out integration
are claimed. Native success is distinct from frozen-runtime generalization.
A future broader transport/serialization study requires separate authorization
and a new baseline; it must not overwrite this negative result. No push or merge.
