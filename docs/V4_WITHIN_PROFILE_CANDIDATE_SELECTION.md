# Within-profile held-out candidate selection

**No eligible provider was selected from this bounded search.** Eleven external
repository snapshots were inspected; ten fail required criteria and one is an
unimplemented scaffold. This is a search/contract-screening result, not an
observed failure of eleven running providers and not proof that no suitable API
exists. No semantic descriptions, provider integrations or native trials were made.

## Criteria recorded before search

Commit `626e5d21ae78889cbbc22fa66077e020ea12425c`
records `docs/artifacts/v4_within_profile_selection/eligibility-criteria.json`
before candidate retrieval or selection. Required: existing independently developed
API, title/start/end event creation, JSON POST and JSON response, reproducible
local/sandbox environment, independent native-state observation, meaningful native
schema/validation difference from A/B, and basic compatibility without changing
frozen shared runtime or vocabulary. Unknown requirements cannot count as PASS.

The frozen profile has precisely three input roles, fixed identifier-like field
names/local paths, no extra constant fields or custom authentication headers,
identity/ISO-to-epoch-ms conversions, and a nonempty **string** response ID mapped
from a top-level JSON field. Date-only/time-only formats, nested-only IDs, numeric
IDs requiring conversion and required extra inputs are not silently adapted.
These are contract checks against documented eligibility, not tests of V4 success.

## Search and comparison

Sources were anonymous GitHub searches, upstream README/API/model/router files and
immutable archive snapshots. REST search twice returned 502 and one HTML query
503; successful public HTML searches are recorded in `search-record.json`. No
route/proxy bypass was used. Repository commit IDs and archive SHA-256s are in
`comparison.json/csv` and per-owner `provenance.json`; all archive commit timestamps
predate criteria registration. External authorship/provenance is evidenced by
public upstream history, not an assertion of organizational independence or human
blinding. No claim of production readiness is made for small tutorial projects.

| Candidate | Native contract and reproduction | Screening outcome |
| --- | --- | --- |
| [gauraang01/flask-calendar-event-api](https://github.com/gauraang01/flask-calendar-event-api/tree/bdbc092210a9cb56fe3cd37ebd2866e780c6f200) | Google OAuth event retrieval service; POST /events takes start_date/end_date/user_id to fetch events, not create a titled interval. Docker/Flask/MongoDB plus Google OAuth; not provisioned. | Retrieval rather than creation; external OAuth and required user_id |
| [h4cktivist/web-calendar](https://github.com/h4cktivist/web-calendar/tree/2f701fbbeaa38ecd06d93b98487ab721e76df022) | Flask POST /api/event: event + date (day only), JSON acknowledgement without id; GET by integer ID. SQLite database and requirements file; not provisioned. | No start/end instants; no creation ID; datetime identity cannot encode date-only schema |
| [andeen171/Calendar-API](https://github.com/andeen171/Calendar-API/tree/596dce4d51cd4f722791094f756475252a6b4d42) | Flask POST /event/: event + date (day only), JSON acknowledgement without id; GET integer ID. SQLite database; dependency versions not declared; not provisioned. | No interval or returned identifier; trailing slash also outside fixed V4 path grammar |
| [femacedogomes/calendar-api](https://github.com/femacedogomes/calendar-api/tree/115da4c009e6a2d7bd8d4ae6f00a398d26851ce2) | POST event: title/description/startTime/endTime; JWT current user; Joi end>start; JSON Mongoose event response. MongoDB/Node setup with upstream package-lock; not provisioned. | Required description and Authorization header cannot be supplied by frozen three-role description |
| [LeperKing-IV/calendar-api](https://github.com/LeperKing-IV/calendar-api/tree/0c5159c16e37d9cf4f97cb70084988cac3158c79) | Read-only Jalali date/calendar formatting endpoints, not event creation. Node/Docker and upstream package-lock; not provisioned. | No event-creation capability or event storage |
| [BradWaterhouse/calendar-api](https://github.com/BradWaterhouse/calendar-api/tree/0cb22702473d8bb9ac1fd2a394bdaa46a684dfb0) | MySQL calendar_event has title/description/calendar_id/date_time, not separate start/end. Node/MySQL schema and upstream package locks; not provisioned. | No end instant; additional required fields and foreign key; no frozen interval mapping |
| [MGasiorowskii/ChronosAPI-FastAPI](https://github.com/MGasiorowskii/ChronosAPI-FastAPI/tree/078c21efa565864c0f10e4b19c7567a734bb561f) | POST events: event_name/agenda/start/end plus owner/location/participants; CurrentUser; integer response id. FastAPI/PostgreSQL/Redis, upstream uv.lock; not provisioned. | Required extra fields/current-user authentication and integer output ID |
| [ToviKn/family_heb_calendar_api](https://github.com/ToviKn/family_heb_calendar_api/tree/72cc7e5834a40bdb180538eb40d18fa4cc60da74) | JSON event model splits dates and timezone-free time-only start_time/end_time; JWT bearer access. FastAPI/PostgreSQL Docker development reset documented; not provisioned. | Mandatory bearer auth and time-only conversion outside frozen instant conversions |
| [smt-rae/Calendar-api](https://github.com/smt-rae/Calendar-api/tree/a9299c1a55c48d0011b28281611e6998a604748c) | Event router, schemas and models are empty scaffolds at inspected revision. No nonempty dependencies or runnable event implementation established. | No implemented creation contract; eligibility unknown/unestablished rather than operationally failed |
| [ciellaindria28/event-scheduler-fastapi](https://github.com/ciellaindria28/event-scheduler-fastapi/tree/4c1530441187252b220d1c65acff754139e34ea9) | POST /create_event requires name/date/description and echoes them; integer GET resource ID. FastAPI/PostgreSQL source; environment reproducibility not established. | Single date, required description, no returned creation ID |
| [dadeechvansh/FastAPI_CRUD_Operations](https://github.com/dadeechvansh/FastAPI_CRUD_Operations/tree/977ba841e6176c7184a16691106a340706fb7431) | POST /events requires title/category/location/date/organizer/capacity/is_open; nested note object with integer ID. FastAPI in-memory seeded list, restart reset possible in principle; not provisioned. | No interval, required extra fields, nested integer ID |

Relevant source files are retained with original bytes and provenance; immutable
archive links/hashes permit retrieval of full upstream versions. Complete archives
are **not vendored**: configuration/credential material, screenshots, application
DBs and unrelated code are omitted. Downloaded originals reside outside the
repository and are not claimed as permanently retained Git artifacts. No credential
values are included in the report. Retained source is evidence, never executed.

## Selection and native feasibility status

There is no defensible selection satisfying the registered criteria from this
sample. The closest interval APIs, femacedogomes/calendar-api and ChronosAPI,
require authentication and additional mandatory data. Removing those requirements,
inserting a proxy, inventing defaults/fields, changing IDs or choosing a date-only
API would weaken the stated experiment. Neither was selected. Screening successive
candidates before selection is disclosed; no selected provider was silently replaced
following a native/V4 failure.

Consequently no selected release/dependency environment was installed, and native
create/retrieve/rejection checks **were not run**. Dependency versions and service
reproducibility remain unverified beyond upstream declarations. Do not treat source
inspection as runtime feasibility evidence. `selection-result.json` explicitly
retains null selection/verdict and zero attempts. The earlier Radicale native
feasibility evidence does not substitute for new within-profile trials.

Native feasibility evidence and a selected dependency lock remain **unfulfilled**
because there is no eligible selection. Further discovery needs a real API with
an existing title/start/end interval contract and a frozen-profile-compatible
unauthenticated local/test configuration; no such service was established here.
No broader conclusion or successful held-out generalization can be drawn. A future
search can expand this sample under the same criteria; any criteria or runtime
change instead requires a separately reported baseline/study, not relabeling these
rejections.

## Preservation and reproducibility

Frozen experimental baseline: `87309bca7456f3d8df827549761052cd467a3f7b`.
All 35 readiness hashes match; no frozen code/vocabulary/A/B files, Radicale results
or historical evidence were modified. No V4 tests or integration experiment ran.
One criteria-only commit precedes this report/evidence commit. Nothing pushed or
merged. Human/AI effort was not measured and remains null.

Evidence directory: `docs/artifacts/v4_within_profile_selection/`. Read-only check:

```sh
python3 - <<'PY_VERIFY'
from pathlib import Path
import hashlib, json
p = Path('docs/artifacts/v4_within_profile_selection')
for name, expected in json.loads((p/'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest() == expected, name
print('PASS')
PY_VERIFY
```
