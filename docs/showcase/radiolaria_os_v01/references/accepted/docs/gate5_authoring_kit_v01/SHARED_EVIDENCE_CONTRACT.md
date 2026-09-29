# Shared Evidence Contract G54C V01

## Causal Objects

1. DomainResult E is extracted from a real typed native producer result whose
   invocation is checked against independently held original source inputs.
2. PublishedEvidence B is built afterwards. A closed, reviewed domain profile
   defines payload_projection(B)==E and any original-input relations. B retains
   original source record/revision, actual Work artifact and source review IDs,
   original time axes/lineage and domain request binding. Independent supplied
   checks validate the real source review, not just an ID-shaped string.
3. ConsumptionContext C is built only after exact canonical B/manifest/pointer,
   publisher signature, release, request/audience/use, current signed STATUS,
   local policy, half-open time, conflict and history checks pass. Its closed
   domain mapping uses verified B/STATUS and independently held policy/request/time.
   It may add derived facts unavailable when E was produced. It must not rewrite B.

Source review, publication review, release review, retrieval/import review and
consumer result review have different subjects. No future identity is an input
to the Work that creates it. Retain signed originals outside C. A public-key
signature authenticates bytes and the independently pinned test key, not semantic
truth, current local authorization or a consequential effect.

## Independent Verification

The examiner receives original source inputs and clock/policy/bootstrap observations
from a trusted runner, outside candidate output. It validates producer admission,
invocation and result, derives E, checks actual source review/refs and independently
compares the published payload to E. It validates exact publication bytes and
request-bound STATUS through the existing public component primitives. It then
derives expected C without reading candidate consumer inputs, and passes that C to
the public supplied native validator. It compares consumer output to the reported
result and subsequent Root claim. Candidate input/output agreement alone is not
this proof. A re-signed wrong payload, valid stale/wrong STATUS or a genuine Work
that consumed the wrong C must fail the appropriate independent predicate.

Original highwater/conflict and current policy belong to the local observer.
Unknown/unavailable current STATUS is not ACTIVE. checked_at <= use_time <
min(valid_until, checked_at+60); source life and request deadline independently
bound use. Verification/ingestion does not renew historical evidence. A new
independent supplied check creates no new Root decision, Work or permission.

## Finite Profiles

Names such as offer_json and offer_sha256 are profile fields, not kernel laws.
See FOOTBALL_PROFILE.md for the task-specific mapping. The non-football numerical
example uses B.computed as E, binds B.sample to the actual source INTEGER input,
and consumes C through one typed PURE capability. It computes
B.computed + B.sample + C.source_projection.request_revision; it does not select
resources, expose an allocation algorithm or provide a target answer.

The numeric mapping is exactly implemented in example/numeric_context.py. It
requires the existing numeric ReviewedBodyProfileV01, actual public bundle/status
checks, independently pinned local policy and use time. It is a signed component
example with peer_io=0, not a second peer exchange, release authority or effect.
Native Work uses the existing controlled logical 1014 source clock; external
evidence/reviews have separately recorded UTC times. No Host authority is revived
from serialized proof, and no protected source/API is changed by this contract.
