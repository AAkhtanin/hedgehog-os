# Football Pitch Booking Reference

G54C preserves this task's business rules. Read FOOTBALL_PROFILE.md for the
versioned E -> B -> C evidence interface. The version line below identifies the
historical task definition, not an assertion that no earlier trial occurred.

Contract clarification version: G53R V01, before any cold-author trial.

Build one small domain pack using HOW_TO_BUILD and the supplied approved source
snapshot. Do not rewrite the kernel or External DRS transport. Return the declared
candidate directory for review, installable_now=false. Do not execute it unless
the supervising reviewer grants the separate restricted-run step.

## User Task

ActivePlanetRoot represents a synthetic team's request. VenueRoot owns the local
synthetic inventory and booking registry for one venue. They decide independently.
No personal names, contacts or identity documents are needed. The scenario is
explicitly synthetic, with January2027 in Europe/Tirane; it makes no statement about
real facility availability. No real venue contact, website, email, messages, payment,
cloud purchase or physical effect is allowed.

The initial request is for a full-size natural-grass pitch for three90-minute
sessions: January7 16:30-18:00; January8 11:00-12:30; January9 11:00-12:30.
Initial times are exact. Required budget and currency are explicit inputs. Missing
budget, timezone, unsupported duration or ambiguous essential constraints require
CLARIFY/unsupported output rather than guessing. Fixture prices are integer minor
units in one currency, not floats or exchange rates. The field inventory and tariff
are supplied at execution, not embedded in the implementation.

Supported operations: FIND_OFFER, CONFIRM_MOCK_BOOKING, VERIFY_EXISTING and CLARIFY.
Mode and parameters come from typed user events or locally validated semantic
proposals, never a scenario/test ID. Identical code handles changed requests.

Only explicit owner consent may relax January8 by30 minutes later. A new request
revision may authorize that one change while preserving the other sessions and
all hard conditions. A model can propose the relaxation, not approve it. Retain
the original request/history and bind the actual approved revision. If exact times
cannot be supplied, report NO_COMPLETE_OFFER or NEEDS_CONFIRMATION; do not silently
move a session or accept an alternative merely because it is cheaper.

## Finite Requirements

One venue, at most four fields, three sessions per request, at most two alternatives
per session. Natural grass and full-size are hard requirements. Price/preference
cannot compensate for an artificial surface, small field, unavailable interval,
wrong currency, missing approval or budget excess. Scope does not include travel,
accommodation, meals, variable-duration pricing or a marketplace.

Use half-open intervals[start,end), start<end. Intervals overlap exactly when
startA<endB and startB<endA. Adjacent intervals are compatible; a30-minute shift
does not automatically eliminate a longer overlap. Parse local calendar times once
using the explicit zone, then compare integer UTC. Session time is not source
observation time, offer TTL or dispatch permission time.

Select only complete allowed offers. Among feasible candidates prefer no forbidden
shift (always mandatory), minimum total allowed shift, then minimum integer total
price, then stable IDs. Preserve semantics under record permutation and ID renaming;
do not depend on the example's IDs, order or prices. Precisely, after comparing
total allowed shift in seconds and total integer price, compare the tuple of
`(session_id, field_id, start_utc, end_utc, venue_ref)` rows sorted by ASCII
`session_id`, using lexicographic ASCII string and integer ordering. IDs must be
unique within their declared session/field collections. Permuting records cannot
change this choice. Renaming IDs preserves feasibility and costs, but a tie is
resolved by the new IDs under this same rule; tied choices are not promised to
survive arbitrary renaming unchanged. Another team/request with other
permitted slots must work through the same implementation.

## External Meaning and Work

VenueRoot receives the bounded task and computes its offer from its own inventory
using actual native Work. The coordinator cannot supply a canned offer. Add one
reviewed FootballVenueOfferV01 body profile through the kit's local profile seam;
do not change calibration validation or accept payload-specified code/validators.
The offer contains request/recipient scope, fields, selected intervals/permitted
alternatives, surface/size, integer price/total/currency, schedule/offer revision,
source/provenance and expiry. Open only the necessary projection, not full private
inventory, all customers, complete source DRS or arbitrary historical graphs.

Persist a bounded pointer in actual local DRS. The requester resolves it via query,
passes current local retrieval review, obtains a current authorized source release,
and checks signature/bytes/schema/arithmetic/scope/time/status/conflict independently.
Pass the actually received offer fields to native requester Work. Missing required
producer output or imported slot/price must refuse, not use a caption/default answer.
Foreign signatures, ACCEPTs, pointers and receipts never become local permission.

Original source timestamps/IDs remain immutable. Ingestion cannot renew TTL. A
revoked, expired, unavailable-current or wrong-owner/request-revision offer cannot
authorize new booking. Recheck current inventory revision and occupancy at dispatch.
Historical offer/result may be displayed only as history, without a revived grant.

## MOCK Confirmation, Recovery and Verification

CONFIRM_MOCK_BOOKING needs the current selected offer, requester conditions/budget
and explicit consent; VenueRoot independently owns its current registry mutation.
Use the existing admitted MOCK consequential/Host/Firewall path, not a direct write
hidden in PURE or DRS lookup. A successful result means three local synthetic slots
committed all-or-none at this one venue, with actual native receipt and state readback.
Do not print BOOKED before that boundary completes or represent partial success as
complete. A changed schedule/occupancy between offer and commit must refuse without
overwriting another reservation. No new generic effect kind/transaction manager.

Use the native canonical logical-effect binding, not a model-generated arbitrary
idempotency token. Repeated exact confirmation returns the saved matching receipt
without a second booking. A changed payload under the same key refuses. CONSUMED
packets are never blindly dispatched again. Unknown/uncertain outcome requires
supported readback/reconciliation, not an automatic new effect. Preserve prior
evidence and do not claim untested OS-crash guarantees.

VERIFY_EXISTING loads actual saved receipt/current local state, with no new offer
selection, reservation, effect callback or duplicate write. Distinguish receipt
history from current authorization. A lawful new offer/consent after a refusal can
continue normally; a failure is scoped, not a permanent domain blacklist.

## Evidence and Handoff

Follow CANDIDATE_OUTPUT.md for files, schema projection and actual Work evidence.
Include own focused tests and threat/compatibility/source-impact declarations.
Keep counters for source/requester Work, search, transport, Root reviews, mock
dispatch, mutations, receipt reuse and pure verification. The independent examiner
will use new inputs; do not bundle target expected answers or hidden test code.

Authoring calls and runtime semantic-role calls are different. Runtime semantics
later need separate authorized live exact-only, approved-shift and verify contrasts
with real locally bound captures and consumed fields. No provider calls are part of
this authoring preparation. Keep controlled events honestly labeled rather than
presenting them as live customer or model actions. Source review/admission is a
separate owner process; the candidate cannot grant itself installation permission.
