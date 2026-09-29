# Football Domain: from intent to recorded booking

Engineering basis: `64f2b38b0d671e4907bae8649fff8f3d2ee0751c`.

<a id="F01"></a>

## F01 / Three training sessions became a recorded, reviewable result

The motivation was Andrey's real trip to arrange a training camp for friends. The executed venue, inventory and prices are synthetic. The Football Domain is one of three connected Gate 5 results: a useful application, external evidence shared across owners, and an independently authored extension. The accepted program arranged three 90-minute sessions on a full-size natural-grass field after the owner permitted one narrowly defined change. It then recorded an authorized mock booking and could recover that result without repeating the effect. This dossier follows the application and its evidence rather than the chronology of building the authoring kit.

The setting is deliberately inspectable. The venue, inventory and monetary amounts are synthetic. The resulting state change is real within a disposable mock registry; it is not a reservation at an operating stadium or a payment. Two business participants, VenueRoot and ActivePlanetRoot, retain separate local decisions. The venue supplies an offer, while the requester checks whether that evidence can serve its own task.

The engineering source is admitted at commit 64f2b38b0d671e4907bae8649fff8f3d2ee0751c. Its final D1 native matrix contains sixteen accepted scenarios, and a separate live series consumes three genuine Gemini proposals. Acceptance follows an explicitly authorized fourth author correction in a restored continuation. The earlier G54D trial remains INCOMPLETE. Those qualifications identify the result accurately without changing what the working program achieved. Publication and the future Gate 6 program have their own status.

Sources:

- [S-EDITORIAL-MOTIVATION](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/gate5_reference_v01/source/editorial/motivation.json) — SHA-256 `f3cd9018493b989e194b6da7a0860c5da6486cff784296001013c4eb7bea9eef`
- [g54d1: NATIVE_ACCEPTED.json](../evidence/SOURCE_MAP.json) — SHA-256 `684b28a43cfc27808876c7cdb6122a563b1d2c0182093c4a396de4d644385c5d`
- [g54d1: LIVE/consumption_verified.json](../evidence/SOURCE_MAP.json) — SHA-256 `d781b19311a99ebe7c92eb749e3f1b9856d8b122d47bf7b2ba7716742cc6e1af`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `8b951d254ab79f7ec0273953098526d4089055a2f5869451f17b4bd6cfeecebd`
- [g54d1: PROTOCOL_AMENDMENT.json](../evidence/SOURCE_MAP.json) — SHA-256 `543a30dfbf59c3eac0b4c8ddfce554ff6ef7b4f6e4408266b757eca36b45e4cd`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`

<a id="F02"></a>

## F02 / Hard requirements make the initial failure intelligible

The request names three civil-time intervals in Europe/Tirane: 7 January 2027, 16:30–18:00; 8 January, 11:00–12:30; and 9 January, 11:00–12:30. Each session must last 90 minutes and use a full-size natural-grass field. The budget is 7,000 EUR minor units: EUR 70.00. Keeping the minor-unit representation visible prevents a hundredfold error when a technical result becomes a human story.

The main inventory includes an artificial field priced at one minor unit and a natural-grass field, field:elm, priced at 2,100 minor units per session. The cheap field cannot satisfy the surface requirement. The natural field has an occupied interval on 8 January from 11:00 to 11:30 local time, intersecting the requested session. Broad opening hours therefore do not imply that every requested interval is free.

The domain treats intervals as half-open: overlap([a,b),[c,d)) is true exactly when a < d and c < b. A session beginning at the occupied interval's end does not overlap it. Availability, duration, surface, field size and total cost are checked together. These constraints explain why the exact request has no complete solution and why a 30-minute shift can later make one possible. The evidence exposes inventory and selection inputs, allowing the reasoning to be checked independently of the candidate's status string.

### Synthetic main inventory

| Field | Surface | Full size | Price / 90 min | Relevant occupancy |
| --- | --- | --- | --- | --- |
| field:cheap | Artificial | Yes | 1 minor EUR | None |
| field:elm | Natural grass | Yes | 2,100 minor EUR | 8 Jan 11:00–11:30 |

Sources:

- [g54d1: RUNTIME_INPUTS/attempt_04/main_repr/publisher/input.json](../evidence/SOURCE_MAP.json) — SHA-256 `8acbb5b7fae1e929690cfca2b75aa445531ad136c64df1c1b0065ec7571765fd`
- [g54d1: RUNTIME_INPUTS/attempt_04/main_repr/requester/input.json](../evidence/SOURCE_MAP.json) — SHA-256 `595ae470ba8a67c1b8b8bed2c0b19aabd99518308fb3e1fdf0119ab4a4578ff6`
- [hedgehog/domains/football_pitch_booking/pack_v01/candidate_domain/domain.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/domains/football_pitch_booking/pack_v01/candidate_domain/domain.py) — SHA-256 `a98b895d5c6d59ee72d64f6beef97567e320eef4bfc986d8513ae7888abf3662`
- [docs/gate5_authoring_kit_v01/FOOTBALL_PROFILE.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_authoring_kit_v01/FOOTBALL_PROFILE.md) — SHA-256 `01f5afd9cab361bef65a456ff612c84d33d9bb39e56ab5719f200fcf0de5ec53`

<a id="F03"></a>

## F03 / EXACT preserved the request and found no complete offer

The first live provider request asks for the three sessions at exact times and supplies no approval reference. Gemini returns FIND_OFFER with request revision 1 and shift allowances [0, 0, 0]. The dates, timezone, session identifiers, team, venue and 7,000-unit budget remain present in the returned parameters. The model's contribution is a concrete proposed operation and its bounded fields, rather than a claim that a pitch has already been found.

In the subsequent native live capture, both publisher and requester intake reconstruct the same normalized request. Their recorded request hash agrees with the independently preserved proposal. Each side then executes one pure Work in this FIND event. The venue's calculation has no eligible complete set, and the requester consumes the evidence for that conclusion. The independently reviewed result is NO_COMPLETE_OFFER, with no dispatch, executor start or registry mutation.

This is a useful outcome. Substituting artificial grass, shortening a session or moving it without consent would have satisfied a weaker problem than the one asked. The program retains the original requirements and exposes the missing fit. The native main matrix exercises the same exact request using controlled inputs; the live series separately demonstrates that an actual model response reached the program. These two sources support related claims but are not the same run.

### Actual model user input

```text
Find three full-size natural-grass 90-minute football sessions: 7 January 2027 16:30-18:00, 8 January 11:00-12:30, and 9 January 11:00-12:30. Exact times only. Budget 7000 EUR minor units. Request request:exam:one revision 1; team:one; venue:synthetic; session IDs session:7, session:8, session:9. No approval reference.
```

### Actual returned text

```text
{"operation":"FIND_OFFER","parameters":{"request_id":"request:exam:one","revision":1,"team_ref":"team:one","venue_ref":"venue:synthetic","timezone":"Europe/Tirane","currency":"EUR","budget_minor":7000,"owner_approval_ref":null,"sessions":[{"session_id":"session:7","start":"2027-01-07T16:30:00","end":"2027-01-07T18:00:00","allow_shift_minutes":0},{"session_id":"session:8","start":"2027-01-08T11:00:00","end":"2027-01-08T12:30:00","allow_shift_minutes":0},{"session_id":"session:9","start":"2027-01-09T11:00:00","end":"2027-01-09T12:30:00","allow_shift_minutes":0}]}}
```

Sources:

- [g54d1: LIVE/prepare_01/provider_exact/request_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `e00f39528c53f6b938fe6e5765ad974134af69ce65943dd82aab7a232b53228c`
- [g54d1: LIVE/prepare_01/provider_exact/completed_turn.json](../evidence/SOURCE_MAP.json) — SHA-256 `f2062e2fc5257a14737ae69fb8ac7109d14fa735e5743220e2071b2c8433ac6c`
- [g54d1: LIVE/prepare_01/provider_exact/response_body.raw](../evidence/SOURCE_MAP.json) — SHA-256 `d3cbf7c9b51fe172df62ecc5273231e36a3565eab4fbdcfcdaf82be3e201c913`
- [g54d1: LIVE/consumption_verified.json](../evidence/SOURCE_MAP.json) — SHA-256 `d781b19311a99ebe7c92eb749e3f1b9856d8b122d47bf7b2ba7716742cc6e1af`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_66a1519a/trusted_parent_receipt.json](../evidence/SOURCE_MAP.json) — SHA-256 `da7477c7f03ea482f943512a9f267792ac80905785af831a2e1fc37742d6ee46`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_66a1519a/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `1fe73e0fcd19dad25f66ee31f4d7f07bc4a3b9b5168931998a7e3aa02622f081`

<a id="F04"></a>

## F04 / One permitted change opened the offer

The second live instruction explicitly allows only the 8 January session to move by up to 30 minutes. It requests revision 2 and supplies consent:jan8-only, while stating that this is not approval to book. The returned FIND_OFFER preserves the original requested times and changes only the second session's allowance to 30. The allowance vector is [0, 30, 0], not three rewritten appointments.

That distinction separates the request from a selected solution. Native selection chooses 8 January 11:30–13:00, immediately after the occupied interval. The sessions on 7 and 9 January remain unchanged. All three use field:elm, satisfying the natural-grass and full-size requirements. At 2,100 minor EUR each, the total is 6,300 minor EUR, or EUR 63.00, within the unchanged EUR 70.00 budget. These are test amounts rather than quoted market prices.

Both parties' actual live intake hashes agree on the revised request. The source Work produces OFFER_READY, and the requesting Work consumes its checked evidence without creating a booking. The offer carries the selected times, whereas the request continues to record the original times and permission to search nearby. This preserves an auditable explanation of what changed: the human relaxed one scheduling constraint; the program selected a newly valid set within that relaxation.

### Requested and selected local times — Europe/Tirane

| Date | Original request | Allowance | Selected | Price |
| --- | --- | --- | --- | --- |
| 7 Jan 2027 | 16:30–18:00 | 0 min | 16:30–18:00 | 2,100 |
| 8 Jan 2027 | 11:00–12:30 | 30 min | 11:30–13:00 | 2,100 |
| 9 Jan 2027 | 11:00–12:30 | 0 min | 11:00–12:30 | 2,100 |
| Total |  |  |  | 6,300 minor EUR |

### Actual model user input

```text
For the same request and same hard requirements, I explicitly allow only the January 8 session to shift up to 30 minutes. Keep original requested times; mark its shift allowance 30, the others zero. Use revision 2 and local approval reference consent:jan8-only. This does not approve a booking.
Previous normalized request: {"budget_minor": 7000, "currency": "EUR", "operation": "FIND_OFFER", "owner_approval_ref": null, "request_id": "request:exam:one", "revision": 1, "sessions": [{"allow_shift_minutes": 0, "end": "2027-01-07T18:00:00", "session_id": "session:7", "start": "2027-01-07T16:30:00"}, {"allow_shift_minutes": 0, "end": "2027-01-08T12:30:00", "session_id": "session:8", "start": "2027-01-08T11:00:00"}, {"allow_shift_minutes": 0, "end": "2027-01-09T12:30:00", "session_id": "session:9", "start": "2027-01-09T11:00:00"}], "team_ref": "team:one", "timezone": "Europe/Tirane", "venue_ref": "venue:synthetic"}
```

### Actual returned text

```text
{"operation":"FIND_OFFER","parameters":{"request_id":"request:exam:one","revision":2,"team_ref":"team:one","venue_ref":"venue:synthetic","timezone":"Europe/Tirane","currency":"EUR","budget_minor":7000,"owner_approval_ref":"consent:jan8-only","sessions":[{"session_id":"session:7","start":"2027-01-07T16:30:00","end":"2027-01-07T18:00:00","allow_shift_minutes":0},{"session_id":"session:8","start":"2027-01-08T11:00:00","end":"2027-01-08T12:30:00","allow_shift_minutes":30},{"session_id":"session:9","start":"2027-01-09T11:00:00","end":"2027-01-09T12:30:00","allow_shift_minutes":0}]}}
```

Sources:

- [g54d1: RUNTIME_INPUTS/attempt_04/main_repr/publisher/input.json](../evidence/SOURCE_MAP.json) — SHA-256 `8acbb5b7fae1e929690cfca2b75aa445531ad136c64df1c1b0065ec7571765fd`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/publisher/evidence/shift/offer_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `1a9177b5b2748fa65193d0d6de3d268854b0924b773953d99bc136382d1279de`
- [g54d1: LIVE/consumption_verified.json](../evidence/SOURCE_MAP.json) — SHA-256 `d781b19311a99ebe7c92eb749e3f1b9856d8b122d47bf7b2ba7716742cc6e1af`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_66a1519a/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `1fe73e0fcd19dad25f66ee31f4d7f07bc4a3b9b5168931998a7e3aa02622f081`
- [g54d1: LIVE/prepare_01/provider_shift/request_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `dcb78c3cfd3292be8cf5c4a7eb58dfa524be0481616f47bf054133e53ecd887e`
- [g54d1: LIVE/prepare_01/provider_shift/completed_turn.json](../evidence/SOURCE_MAP.json) — SHA-256 `dcdec43a7d44e8887bce6c8202f8b4b88bacbaddb717bb18e8503cc0e5c0ee8f`
- [g54d1: LIVE/prepare_01/provider_shift/response_body.raw](../evidence/SOURCE_MAP.json) — SHA-256 `af07b80977f175aa3952a1bee770f3ae24a5eadd10848ae8664f9a7d7dfde806`

<a id="F05"></a>

## F05 / The offer became an input to another owner’s Work

The venue's result does not become local authority merely by crossing a boundary. In the accepted FIND path, VenueRoot owns the producer Work and its review. The published offer is disclosed through the governed external exchange. ActivePlanetRoot checks the received body, source status, task binding and local policy before its own Work uses that evidence. The two Roots are peers; the runner and examiner are instruments of the experiment, not a third business owner above them.

Three representations describe one causal history. E is the producer Work's domain result. B is the published body containing E together with source, Work, review and time references. C is the checked consumption context containing B and the later status information needed by the recipient. The required relationships are B.offer = E and C.body = B, not byte equality among all three documents. Added evidence explains a transformation rather than silently replacing the original result.

The main SHIFT capture contains the producer Work, offer body, consumption context and requester Work as distinct exact files. Independent review joins them to actual recorded events and confirms local consumer execution. External material therefore became an input to work owned by the other side. The External DRS dossier explains the address, retrieval and lifecycle mechanisms in detail; this example shows their application to a football offer.

Sources:

- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `8b951d254ab79f7ec0273953098526d4089055a2f5869451f17b4bd6cfeecebd`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/trusted_parent_receipt.json](../evidence/SOURCE_MAP.json) — SHA-256 `45a0356b9dc39cb19c42bfdc7742b8f87c039aebf998d8194d5154b9626b2155`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/publisher/evidence/shift/offer_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `1a9177b5b2748fa65193d0d6de3d268854b0924b773953d99bc136382d1279de`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/publisher/evidence/shift/venue_work.json](../evidence/SOURCE_MAP.json) — SHA-256 `69c4d0c3b2d910a9a2ad7185374513659d12729efbacf774481e8cb0899cd447`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/requester/evidence/shift/consumption_context.json](../evidence/SOURCE_MAP.json) — SHA-256 `650f01a2685c806a85cda38351be038ec1ad9b302f1de21c75102e8b63fb7844`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/requester/evidence/shift/requester_work.json](../evidence/SOURCE_MAP.json) — SHA-256 `0722be5b586b1210258468010c9cbaab9b5c85ac05164608cdd4dd3c4cc3dbd6`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`

<a id="F06"></a>

## F06 / Separate consent led to one three-slot state change

Finding a valid offer is not approval to execute it. BOOK is a separate controlled owner input with operation CONFIRM_MOCK_BOOKING and reference consent:controlled:booking. Local policy binds that approval to the booking request and preceding offer request. The semantic provider does not manufacture this permission, and the January 8 shift reference cannot substitute for it.

The venue's reviewed native route checks current policy, source state, offer and request binding, schedule revision, tariff, occupancy and the existing registry before the effect. The main event records one Host dispatch, one executor start, one effect callback and one business-state write. That single mock action adds three reservation records and one idempotency entry in the owning registry. It is one batch effect with three slots, not three separately authorized executions.

Evidence goes beyond the returned MOCK_BOOKED label. The saved native receipt is an EVIDENCE_ONLY artifact owned by VenueRoot; it records the effect result rather than granting permission for a future one. The registry snapshot and independently observed final source state agree. The receipt, action result and readback are joined by the examiner to the actual trace. This establishes an observed state change in the synthetic registry. It does not establish a transaction with a real venue or resilience to untested operating-system failures.

### Five events in the native main history

| Event | Operation | Observed result | New mock effects |
| --- | --- | --- | --- |
| EXACT | FIND_OFFER | NO_COMPLETE_OFFER | 0 |
| SHIFT | FIND_OFFER | OFFER_READY | 0 |
| BOOK | CONFIRM_MOCK_BOOKING | MOCK_BOOKED | 1 |
| REPEAT | CONFIRM_MOCK_BOOKING | Same receipt | 0 |
| VERIFY | VERIFY_EXISTING | VERIFIED | 0 |

Sources:

- [g54d1: RUNTIME_INPUTS/attempt_04/main_repr/requester/input.json](../evidence/SOURCE_MAP.json) — SHA-256 `595ae470ba8a67c1b8b8bed2c0b19aabd99518308fb3e1fdf0119ab4a4578ff6`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `8b951d254ab79f7ec0273953098526d4089055a2f5869451f17b4bd6cfeecebd`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/trusted_parent_receipt.json](../evidence/SOURCE_MAP.json) — SHA-256 `45a0356b9dc39cb19c42bfdc7742b8f87c039aebf998d8194d5154b9626b2155`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/publisher/evidence/book/receipt.json](../evidence/SOURCE_MAP.json) — SHA-256 `aa74811764727515c5543e9ba83f5021ba418ea383bec0637b180f6c79b9e453`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/publisher/state/registry.json](../evidence/SOURCE_MAP.json) — SHA-256 `b694ab8b5a6dfbab565bc757842dcf8c58bfca5a82dc0b39fb070e45aab07894`
- [hedgehog/domains/football_pitch_booking/pack_v01/candidate_domain/effect.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/domains/football_pitch_booking/pack_v01/candidate_domain/effect.py) — SHA-256 `f06c394747f8746dae844e787c760f07c782e9eb1dad918a6864aa2fa7803be7`

<a id="F07"></a>

## F07 / Repeat and verification recovered the result without executing it again

The main REPEAT event repeats the confirmed booking request after the first effect has completed. It returns the previous receipt instead of creating another reservation batch. Independent flow review records zero new pure Work, dispatches, executor starts, effects and state writes for both roles. The registry hash remains equal to the post-BOOK snapshot, so an unchanged report is supported by unchanged business state.

VERIFY has a different operation: VERIFY_EXISTING. Its actual live model input asks to use existing history and readback without searching or booking again. Gemini returns that operation with revision 2, the same session constraints and the historical booking approval reference. Later native intake consumes it on both sides. The result is VERIFIED, with the existing receipt and no new search Work or effect. The reference is historical evidence, not a fresh permission to act.

The timing matters. All three live proposals, including VERIFY, were collected before the subsequent native booking run. The model did not see the receipt that the program later created. What was demonstrated is preparation and later consumption of a request to verify, followed by the program's actual historical check. The saved evidence supports this precise sequence without inventing an interactive conversation in which the model personally observes the completed booking.

### Actual model user input

```text
Verify the already completed booking from source history and readback only. Do not search for or book anything new. Keep revision 2, the same sessions and January 8 allowance. Historical booking approval reference is consent:controlled:booking, not a new grant.
Previous normalized request: {"budget_minor": 7000, "currency": "EUR", "operation": "FIND_OFFER", "owner_approval_ref": "consent:jan8-only", "request_id": "request:exam:one", "revision": 2, "sessions": [{"allow_shift_minutes": 0, "end": "2027-01-07T18:00:00", "session_id": "session:7", "start": "2027-01-07T16:30:00"}, {"allow_shift_minutes": 30, "end": "2027-01-08T12:30:00", "session_id": "session:8", "start": "2027-01-08T11:00:00"}, {"allow_shift_minutes": 0, "end": "2027-01-09T12:30:00", "session_id": "session:9", "start": "2027-01-09T11:00:00"}], "team_ref": "team:one", "timezone": "Europe/Tirane", "venue_ref": "venue:synthetic"}
```

### Actual returned text

```text
{"operation": "VERIFY_EXISTING", "parameters": {"request_id": "request:exam:one", "revision": 2, "team_ref": "team:one", "venue_ref": "venue:synthetic", "timezone": "Europe/Tirane", "currency": "EUR", "budget_minor": 7000, "owner_approval_ref": "consent:controlled:booking", "sessions": [{"session_id": "session:7", "start": "2027-01-07T16:30:00", "end": "2027-01-07T18:00:00", "allow_shift_minutes": 0}, {"session_id": "session:8", "start": "2027-01-08T11:00:00", "end": "2027-01-08T12:30:00", "allow_shift_minutes": 30}, {"session_id": "session:9", "start": "2027-01-09T11:00:00", "end": "2027-01-09T12:30:00", "allow_shift_minutes": 0}]}}
```

Sources:

- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `8b951d254ab79f7ec0273953098526d4089055a2f5869451f17b4bd6cfeecebd`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/publisher/state/registry.json](../evidence/SOURCE_MAP.json) — SHA-256 `b694ab8b5a6dfbab565bc757842dcf8c58bfca5a82dc0b39fb070e45aab07894`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/requester/evidence/repeat/report.json](../evidence/SOURCE_MAP.json) — SHA-256 `10f7328d40b320803959a0626f13633249290e9def5ea299de607046e29c9bbf`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/worker/requester/evidence/verify/report.json](../evidence/SOURCE_MAP.json) — SHA-256 `a52caab8bd4476038ef142b95ab00e18f1e216a0751b59c1dddcad8d6f7c58aa`
- [g54d1: LIVE/consumption_verified.json](../evidence/SOURCE_MAP.json) — SHA-256 `d781b19311a99ebe7c92eb749e3f1b9856d8b122d47bf7b2ba7716742cc6e1af`
- [g54d1: LIVE/prepare_01/provider_verify/request_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `2aa3a73bf0379aeb3b8b268c2098330073f66b8362d7ba889248fc93f8aaad7e`
- [g54d1: LIVE/prepare_01/provider_verify/completed_turn.json](../evidence/SOURCE_MAP.json) — SHA-256 `b6264c4776b50eff698d90ed271e158ceb43a31b9d73a5e55ade652425da81f1`
- [g54d1: LIVE/prepare_01/provider_verify/response_body.raw](../evidence/SOURCE_MAP.json) — SHA-256 `07e6ac07cc881831ea0b076ae577d53ed9c2a5e0525b41bea619fd08fde24543`

<a id="F08"></a>

## F08 / Three genuine model responses have a traceable consumer

The live provider is gemini-2.5-flash. The attempt ledger records exactly three completed requests, one wire send per role, for EXACT, SHIFT and VERIFY. The inputs disclose the method: a supplied system instruction limits the response to an operation and parameters; a JSON schema enumerates request fields; SHIFT and VERIFY also receive the previous normalized request. Temperature is 0.0, maximum output is 4,096 tokens, and returned content is JSON. Field choice, price, booking success and Root authority are outside the model's proposed decision.

Consumption is checked at both business roles. EXACT intake returns occur at observer sequence 5 for publisher and requester. SHIFT returns occur at 31 and 61; VERIFY at 106 and 189. In each pair, the reconstructed intake request hash equals the corresponding normalized provider request hash. The verifier also checks parent events and captured intake values before joining to independent Work or history results. An HTTP success response alone would not establish this chain.

The contribution is specific and useful: a changed human instruction changes the operation or a permitted parameter, and the actual program follows it. Native Work determines the offer; local policy and Root determine admissibility; controlled owner input supplies booking consent. The complete input, returned text and schema are retained alongside this dossier as exact source material. No new model call was made to prepare the publication.

### Actual proposal, native intake and result

| Role | Operation / allowance | Publisher / requester intake | Native result |
| --- | --- | --- | --- |
| EXACT | FIND_OFFER / [0, 0, 0] | 5 / 5 | NO_COMPLETE_OFFER |
| SHIFT | FIND_OFFER / [0, 30, 0] | 31 / 61 | OFFER_READY |
| VERIFY | VERIFY_EXISTING | 106 / 189 | VERIFIED |

### Actual shared system instruction

```text
Interpret the user's intent into a bounded football semantic proposal. Return only JSON operation and parameters. No field selection, prices, booking success or Root authorization is yours to decide. Preserve identifiers and civil times exactly. Datetime strings use YYYY-MM-DDTHH:MM:SS, Europe/Tirane. A shift allowance means keep original times and change only allow_shift_minutes for January 8. Parameters include all request fields except operation. Operations: FIND_OFFER, VERIFY_EXISTING, CLARIFY. An owner approval reference is a supplied local reference, never permission created by you.
```

Sources:

- [g54d1: LIVE/consumption_verified.json](../evidence/SOURCE_MAP.json) — SHA-256 `d781b19311a99ebe7c92eb749e3f1b9856d8b122d47bf7b2ba7716742cc6e1af`
- [g54d1: LIVE/provider_attempt_ledger.json](../evidence/SOURCE_MAP.json) — SHA-256 `f596e9bfc3cf0a7dd72bd3efad4be5af477807603f9ce46e1b706fa2e4aa9090`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_66a1519a/trusted_parent_receipt.json](../evidence/SOURCE_MAP.json) — SHA-256 `da7477c7f03ea482f943512a9f267792ac80905785af831a2e1fc37742d6ee46`
- [g54d1: LIVE/prepare_01/provider_exact/request_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `e00f39528c53f6b938fe6e5765ad974134af69ce65943dd82aab7a232b53228c`
- [g54d1: LIVE/prepare_01/provider_shift/request_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `dcb78c3cfd3292be8cf5c4a7eb58dfa524be0481616f47bf054133e53ecd887e`
- [g54d1: LIVE/prepare_01/provider_verify/request_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `2aa3a73bf0379aeb3b8b268c2098330073f66b8362d7ba889248fc93f8aaad7e`

<a id="F09"></a>

## F09 / Sixteen cases exercise one final program

The final native matrix executes the same frozen D1 candidate across sixteen scenarios. The complete rows are reproduced here rather than replacing the matrix with a single PASS total. They account for 56 events and seven isolated mock executor starts. The main case contributes five events and one effect; other positive and variation cases have their own disposable registry and evidence. Seven effects are not seven repeats of the main booking.

The cases cover useful work, permissions, source suitability, input variation and history. A low budget may legitimately produce no complete offer. Missing BOOK approval prevents action. Missing history yields CURRENT_STATUS_UNKNOWN. Revoked or wrongly addressed external material cannot become usable local evidence. A changed schedule revision or occupancy blocks later confirmation even when the earlier FIND produced an offer.

Other cases exercise reordered inputs, changed identifiers and prices, another team and lawful continuation after earlier refusals. The same-key-changed case contains a successful booking followed by refusal of a changed repeat, explaining its one effect. The final reserved variation is the preserved G54D challenge, not a newly unseen benchmark after restored continuation. Together the cases establish breadth within this finite domain and fixture family; they do not certify a universal planner for every training-camp problem.

### Complete recorded D1 native matrix

| Case | Events | Bookings | Host dispatches | Executor starts | Result |
| --- | --- | --- | --- | --- | --- |
| main | 5 | 1 | 1 | 1 | PASS |
| low_budget | 1 | 0 | 0 | 0 | PASS |
| missing_BOOK | 3 | 0 | 0 | 0 | PASS |
| missing_history | 1 | 0 | 0 | 0 | PASS |
| release_denied | 2 | 0 | 0 | 0 | PASS |
| revoked_source | 2 | 0 | 0 | 0 | PASS |
| foreign_audience | 2 | 0 | 0 | 0 | PASS |
| revision_conflict | 3 | 0 | 0 | 0 | PASS |
| same_key_changed | 4 | 1 | 1 | 1 | PASS |
| permuted_main | 5 | 1 | 1 | 1 | PASS |
| variation_feedback | 5 | 1 | 1 | 1 | PASS |
| second_team | 5 | 1 | 1 | 1 | PASS |
| long_overlap | 2 | 0 | 0 | 0 | PASS |
| occupancy | 3 | 0 | 0 | 0 | PASS |
| continuation | 8 | 1 | 1 | 1 | PASS |
| variation_final_reserved | 5 | 1 | 1 | 1 | PASS |

Sources:

- [g54d1: NATIVE_ACCEPTED.json](../evidence/SOURCE_MAP.json) — SHA-256 `684b28a43cfc27808876c7cdb6122a563b1d2c0182093c4a396de4d644385c5d`
- [g54d1: SUPERVISOR_EVIDENCE/p7_candidate_f779b790/independent_flow_review.json](../evidence/SOURCE_MAP.json) — SHA-256 `8b951d254ab79f7ec0273953098526d4089055a2f5869451f17b4bd6cfeecebd`
- [g54d1: PROTOCOL_AMENDMENT.json](../evidence/SOURCE_MAP.json) — SHA-256 `543a30dfbf59c3eac0b4c8ddfce554ff6ef7b4f6e4408266b757eca36b45e4cd`
- [g54d1: SUPPLIED/one.json](../evidence/SOURCE_MAP.json) — SHA-256 `0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0`

<a id="F10"></a>

## F10 / Refusal is part of a complete domain process

The most consequential final correction concerns a source whose authenticated status is REVOKED. The program already stopped using that source without booking, but the earlier G54D candidate omitted the required local Root refusal in this exception branch. D1 retains the stop and now records a genuine BLOCKED_FAIL_CLOSED decision, bound to the original request, source record, revision, status and reason status_not_active. The evidence identifies actual decision calls, not a newly written refusal caption.

For the two revoked FIND events, the recorded refusal calls occur at sequences 29 and 66. Both are joined to the authenticated terminal source state and corresponding request hashes. The final native case has two events, no dispatch and no mock executor start. The old trial remains INCOMPLETE: an explicitly authorized extra correction repaired a real profile obligation without rewriting the earlier result.

Other negative cases address distinct causes rather than collapsing them into one generic failure. Missing history is uncertainty, denied disclosure is a release refusal, foreign audience is a scope mismatch, and an occupied or changed schedule prevents later action. Correct behavior is assessed using the concrete inputs and captured path. A program that could only display a successful booking would miss these boundaries; this domain also makes the reasons for withholding action inspectable.

Sources:

- [g54d1: NATIVE_ACCEPTED.json](../evidence/SOURCE_MAP.json) — SHA-256 `684b28a43cfc27808876c7cdb6122a563b1d2c0182093c4a396de4d644385c5d`
- [g54d1: evidence/refusal_binding_d1.json](../evidence/SOURCE_MAP.json) — SHA-256 `0cbb08146e2a0eaf4d38847ae1ab646ed1688bd17b7a1fca51251d090d806c50`
- [g54d1: PROTOCOL_AMENDMENT.json](../evidence/SOURCE_MAP.json) — SHA-256 `543a30dfbf59c3eac0b4c8ddfce554ff6ef7b4f6e4408266b757eca36b45e4cd`
- [hedgehog/domains/football_pitch_booking/pack_v01/candidate_domain/run.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/domains/football_pitch_booking/pack_v01/candidate_domain/run.py) — SHA-256 `0d56d79c2c0cdf4a9d410a4bf39331b5ad9e9fa8f7a9fbc2b1eabfc974f98f12`
- [g54d1: SUPPLIED/one.json](../evidence/SOURCE_MAP.json) — SHA-256 `0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0`

<a id="F11"></a>

## F11 / Variation changes the answer without replacing the program

The reference keeps the authored source fixed while changing facts around it. Permuted inputs test independence from presentation order. Changed inventory and pricing test whether selection depends on actual source material. Another team tests request identity and task binding. The continuation case includes earlier refused events followed by a later admissible request and one successful booking, preserving the distinction between a scoped refusal and a permanent ban on the whole task.

Recorded variant results make that dependence visible. The final reserved variation totals 6,798 minor EUR, rather than the main case's 6,300. The second-team and continuation accepted offers total 6,414. These are results of their own supplied inventories and requests, not alternative prices retrospectively attached to the main story. Each successful path has its own receipt and source-state readback, and repeats are checked within that path's history.

Nine coherent altered-evidence controls form a separate pure examiner test group. They ask whether internally edited evidence is rejected; they are not nine additional native attacks. Native refusal scenarios likewise do not demonstrate every possible race or failure between validation and execution. The useful architectural conclusion is bounded: a new authored domain can use the same governed activity and exchange mechanisms across this range of changed inputs, with acceptance grounded in records of what actually happened.

Sources:

- [g54d1: NATIVE_ACCEPTED.json](../evidence/SOURCE_MAP.json) — SHA-256 `684b28a43cfc27808876c7cdb6122a563b1d2c0182093c4a396de4d644385c5d`
- [g54d1: evidence/domain_controls_d1/RESULT.json](../evidence/SOURCE_MAP.json) — SHA-256 `66ae587dc41e9440515cb12b6f39dc58ffa6e8ff3f70ff10ffedc8f0b4d24deb`
- [g54d1: SUPPLIED/one.json](../evidence/SOURCE_MAP.json) — SHA-256 `0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0`

<a id="F12"></a>

## F12 / The saved result can be checked without booking again

Three evidence levels remain separate. D1 native acceptance covers sixteen controlled scenarios, 56 events and seven isolated mock effects. Its live series adds three genuine provider responses, a separate five-event run and one additional mock effect. Across these groups there are 61 events and eight mock effects, not eight payments or one booking repeated eight times. The authoring model, gpt-6-astra, created the program during a different process; it is not the runtime semantic provider.

The independent D1 review verified 362 Ed25519-signed messages in the native corpus, 25 completed FIND joins across E, B and C, and seven confirmation consumptions. These are scoped native evidence checks, not counts of Roots or every cryptographic operation across Gate 5.

The two accepted D1 supplied results are each 32,702 bytes and have SHA-256 0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0. They recheck saved source-bound evidence in separate pure processes. The installed Gate 5 verification entry reconstructs declared historical inputs and invokes reviewed pure consumers, without importing the candidate, calling a provider, making new Root decisions or performing a mock effect. File reads, hashing and verification processes still occur.

Trust is limited to the exact reviewed reference implementation, observer, runner, examiner and pinned evidence. This does not attest arbitrary hostile Python, real venue identity, production payments, all prestart races, post-effect uncertainty or power-loss recovery. Keeping receipts evidence-only prevents history from becoming current permission. Within that scope, the dossier traces original human conditions through model parameters, actual Work, authorized mutation and independently checked history. The adjoining DRS and authoring dossiers explain the other two views of the same engineering result.

Sources:

- [S-REVIEW-G54D1-INDEPENDENT](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/gate5_reference_v01/source/reviews/G54D1_INDEPENDENT_ACCEPTANCE_REVIEW_RU.md) — SHA-256 `7f2b4a8eb78301807758e35760e5cf370182da794ff0327d39616de25135e857`
- [g54d1: NATIVE_ACCEPTED.json](../evidence/SOURCE_MAP.json) — SHA-256 `684b28a43cfc27808876c7cdb6122a563b1d2c0182093c4a396de4d644385c5d`
- [g54d1: LIVE/consumption_verified.json](../evidence/SOURCE_MAP.json) — SHA-256 `d781b19311a99ebe7c92eb749e3f1b9856d8b122d47bf7b2ba7716742cc6e1af`
- [g54d1: LIVE/provider_attempt_ledger.json](../evidence/SOURCE_MAP.json) — SHA-256 `f596e9bfc3cf0a7dd72bd3efad4be5af477807603f9ce46e1b706fa2e4aa9090`
- [g54d1: PROTOCOL_AMENDMENT.json](../evidence/SOURCE_MAP.json) — SHA-256 `543a30dfbf59c3eac0b4c8ddfce554ff6ef7b4f6e4408266b757eca36b45e4cd`
- [g54d1: SUPPLIED/one.json](../evidence/SOURCE_MAP.json) — SHA-256 `0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0`
- [g54d1: SUPPLIED/two.json](../evidence/SOURCE_MAP.json) — SHA-256 `0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0`
- [g54d1: FINAL_EVIDENCE_FREEZE.json](../evidence/SOURCE_MAP.json) — SHA-256 `692d4994937634dd0ba4f3b187678f143e9d3d0c44227aee254eb04a5679fb49`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`
- [demo/verify_gate5_reference_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/demo/verify_gate5_reference_v01.py) — SHA-256 `2852dda26988804f665181374ae9d2a44d96d395808f038707db4f02b7b63c22`

