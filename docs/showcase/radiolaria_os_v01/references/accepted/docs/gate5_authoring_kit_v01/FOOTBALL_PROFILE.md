# TASK-SPECIFIC PROFILE: Football Evidence G54D V01

This is a public evidence interface, not a pitch selector, expected answer or
booking implementation. WHAT_TO_BUILD defines business rules and bounds;
CANDIDATE_OUTPUT defines normalized request/report fields. Existing P01-P10/A-H,
ranking, explicit consent, idempotency, receipt/readback and variations remain.

## E and B

VenueRoot PURE inputs are TEXT request_json and inventory_json, both canonical
JSON of original local inputs. Its TEXT offer_json is canonical semantic E.
E is a closed object: request, fields, alternatives, slots, total_minor, currency,
status, schedule_revision, offer_revision. Preserve the normalized request and
original inventory revision; expose only relevant bounded field/interval/price
data, not private inventory/customer history. Alternatives have session_id and
choices; each choice/slot has the fields declared in CANDIDATE_OUTPUT. Each exposed
field has exactly field_id, surface, full_size and price_minor, matching the original
inventory. Alternative session IDs are unique and reference original sessions;
each choice independently satisfies the same hard/time/price rules as a slot.

FootballVenueOfferV01 B has the common body fields plus publisher, recipient,
request_sha256, offer and booking. payload_projection(B)=B.offer. B.offer must
equal E, request_sha256=sha(E.request), source_revision=E.offer_revision,
E.schedule_revision=original inventory.revision. B.source_work_ref is the actual
producer artifact; B.source_review_ref is its actual source review decision.
The source claim binds request_sha256, inventory_sha256, consumed_offer=E,
source_work_ref, booking and any previous source/review refs (null for FIND).
Review candidate IDs may differ from Work IDs; validate their recorded claims,
subjects and links, never require a self-referential future Work output.

For FIND, B.booking=null. For confirmation retain the selected historical E and
its original Work/time, with separately current consent/review/receipt. Booking
projection contains state, receipt_ref, payload_sha256, snapshot_sha256,
packet_ref, slots and request_sha256; it is not an effect permission. Full action
validation still requires trusted observations and actual receipt/state readback.

## C Mapping After Verified Retrieval

C has exactly body and source_projection, with C.body equal to authentic B.
Let T=B.time_envelope, V=verified STATUS.value, and J=V.entry after public
check_bundle/check_status for the independently recorded local FETCH request,
policy, bootstrap keyset, highwater/conflicts and bounded use time. Then S is:

| S field | Independent source |
| --- | --- |
| publisher, recipient | B.publisher, B.recipient, checked against local policy |
| request_revision | E.request.revision, checked against original request |
| schedule_revision | E.schedule_revision, checked against original inventory |
| offer_revision | B.source_revision, checked against E.offer_revision |
| observed_at | T.source_observed_at |
| valid_from, valid_to | T.valid_from, T.valid_to |
| ttl, pt | T.ttl_seconds, T.pt_created_at |
| status | J.state |
| status_checked, status_until | V.checked_at, V.valid_until |

Requester PURE receives TEXT request_json=canonical(original local request) and
TEXT offer_json=canonical({body:B,source_projection:S}). Its output result_json
is canonical(report without native_refs), including S where source is reported.
Missing/changed consumed fields are not defaulted from a caption or expected answer.

The final local Root selects the actual requester Work artifact and has exactly
{request_sha256:sha(request), offer_sha256:sha(B),
result_sha256:sha(report_without_native_refs)}. offer_sha256 intentionally refers
to the signed body B, NOT E or C. Retain C and the signed STATUS separately to prove
the consumed dependency. This claim gives no cross-Root or effect permission.

## Examiner Inputs

Trusted runner evidence supplies the original request/inventory, local operator
policy/bootstrap keys, local trust policy and use time, canonical publisher wire,
source/publication/release reviews and event-scoped observations. These are not
expected values chosen from candidate requester.inputs. Their source pins and
capture origins are mandatory. For historical confirmation the runner separately
pins the original FIND inputs and selected source proof; it cannot relabel a new
request as an old native invocation. Unsupported/missing history fails closed.
No candidate-provided full_boundary_review flag alone certifies an action.

For the finite FIND interface, the publication Root selects the actual pointer
and reviews {pointer, source_review_ref}, with the source record as subject. The
release Root selects the actual FETCH request and reviews {request, pointer_ref,
body_hash:sha(B), source_review_ref}, with the pointer as subject. Preserve these
materials alongside the real decision. These are source-bound evidence profile
shapes, not new Root laws. They must be publicly declared, not secret examiner
expectations. The source selection ID is captured by the trusted runner and need
not follow a new examiner-specific naming recipe.

## Selection And Event Semantics

E itself must have the complete lawful, optimally ranked selection and exact
integer total/currency, or the honest empty no-offer result. A consumer cannot
repair incorrect/missing producer slots, price or status from another source.
Successful consumption preserves E.slots, E.total_minor and E.currency exactly.
For FIND map E.OFFER_READY to report.OFFER_READY; an empty infeasible E maps to
NO_COMPLETE_OFFER or NEEDS_CONFIRMATION, with empty slots and total zero.
For first successful CONFIRM, historical E remains OFFER_READY while the
current result becomes MOCK_BOOKED only after the actual action and receipt.
VERIFY maps matching actual history/readback to VERIFIED, not a fresh offer.

An exact repeated CONFIRM is a HISTORY branch. Retain original Work/E, original
request/inventory and recorded computation/use time. New consent/current review
is distinct and cannot rewrite history. History after offer expiry may return
the old genuine receipt plus matching actual source readback with zero new
Work/effect; this is not current action permission. Both peers must reconcile
saved history with source readback. Missing or inconsistent history is UNKNOWN,
never a reason to book again. Changed payload under the same logical key refuses.
Current source UTC and the declared native logical clock are separate domains.

Authenticated BUNDLE.release.value.release_review_ref must equal the actual
release Root result.decision_id. Signature, body/hash, FETCH, subject and claim
checks still apply; none substitutes for that exact equality.

## Observable Evidence Without Private Helper Names

Implementation layout, state filenames, helper names and identifier recipes are
not an author ABI. Only the declared entrypoint, public wire/body/report shapes
and substantive evidence obligations are fixed. Provide an evidence index in
README mapping saved source/publication/release/current reviews, Work,
packet/Host outcome, receipt and state readback. The reviewer observes exact
reviewed code objects and independently reads source state in its real format.
No candidate-owned observation file is an independent oracle.

Separate role/event/stage accounting: Host attempt, Firewall entry, executor
start, mutation and outcome. A currentness rejection may have one Host attempt
and no executor/effect. A failure after start may have changed state: preserve
stage, original error, available receipt and readback, report
CURRENT_STATUS_UNKNOWN and prohibit blind retry. Do not claim REFUSED/zero effects
merely because evidence rendering failed. Requester-local zero does not imply
that VenueRoot did not legitimately perform its separately authorized effect.

Ordinary operator policy must expose and document finite release/BOOK approval,
active/revoked status and audience acceptance controls. Current inventory is an
ordinary per-event input. No secret prestart hook, injected clock, new action
service or universal crash-recovery machinery is required. Do not claim untested
timing races, arbitrary OS failure recovery or hostile-code isolation.
