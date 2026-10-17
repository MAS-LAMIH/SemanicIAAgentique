# Provider B: appointment booking API, revision 1

This controlled appointment service is implemented separately from the tutorial
calendar API. Documentation precedes semantic manual authoring. It was authored
by Codex in the same task; it does not establish independent real-world provider
authorship. The API is its own reference for wire behavior, not generated from a
semantic manual.

GET /availability returns can_book (boolean or null), items (map of booking IDs
to bookings), version (integer), sampled_at (UTC timestamp). Null means the
service cannot currently establish write permission.

POST /bookings requires exactly begins_ms, finishes_ms, label. Times are integer
Unix milliseconds. Label is a nonblank string, at most 500 characters. Start and
end must fall on UTC quarter-hour boundaries; duration is positive and no more
than 7,200 seconds. Invalid requests receive 422. Permission not exactly true
receives 403. Successful creation returns 201 with booking_ref. This service
stores bookings immediately and supports read-after-write consistency.

GET /booking/{booking_ref} returns booking (or null for 404), version, sampled_at.
A booking contains booking_ref, begins_ms, finishes_ms, label. GET /bookings
returns the full items snapshot with can_book, version, sampled_at. Existing
bookings are preserved. Multiple overlapping bookings are permitted: this is
not a room-capacity or conflict-resolution service.

Fixture controls (not production endpoints): can_book true/false/null; stale
permission or observation evidence; modes normal, error (503), no_change (201
without storage), mismatch (wrong label), side_effect (unrequested booking).
These are deterministic diagnostic scenarios, not semantic repair rules.

A accepts arbitrary timezone-aware positive intervals and JSON start/end/title.
B enforces a different temporal domain and uses an independently implemented
wire/storage model. A semantic client must reject precision loss, respect the
grid and duration bound, and observe B's actual state rather than equating POST
success with achievement. No remote credentials or paid services are required.
