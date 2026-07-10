# Hedgehog OS — Airline Ticket/Purchase Corridor, Transaction Artifact Ledger, Crypto Artifact Seal, and Sealed Trace Replay Verifier Umbrella Preflight v0.1

## Header

- document_id: airline_ticket_purchase_corridor_artifact_ledger_crypto_replay_preflight_v01
- document_status: UMBRELLA_PREFLIGHT
- observed_base_head: 7447445
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- ticket_purchase_corridor_implemented: false
- transaction_artifact_ledger_implemented: false
- crypto_artifact_seal_implemented: false
- sealed_trace_replay_verifier_implemented: false
- real_airline_api_called: false
- real_bank_api_called: false
- real_gds_api_called: false
- real_payment_executed: false
- real_ticket_issued: false
- real_booking_created: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false

This document is planning only. It defines the narrowest safe engineering path
for the next four sequential Airline layers:

1. Airline Ticket/Purchase Corridor
2. Airline Transaction Artifact Ledger
3. Airline Crypto Artifact Seal
4. Airline Sealed Trace Replay Verifier

This order is mandatory.

## One-Screen Summary

The Airline semantic lane already provides the cognitive side of one tri-party
transaction. The next engineering program adds a deterministic, Root-scoped mock
purchase/ticket contract corridor; records the resulting transaction artifacts
in a non-authoritative ledger; seals the canonical artifact set for continuity
and tamper detection; and verifies/replays the sealed trace without another
Gemini call.

## Closed Basis

Airline deterministic tri-party transaction spine: PASS.

- one transaction_id
- ClientRoot / AirlineRoot / BankRoot
- offer-hold sandbox
- BankRoot mock payment authorization sandbox
- ClientRoot purchase orchestration
- AirlineRoot mock ticket issue corridor
- integrated transaction trace
- mock ticket / mock PNR evidence
- no real effects

Airline Tri-Party Live Semantic Lane v0.1: REAL GEMINI PASS.

- 12 semantic actors
- real_provider
- gemini-2.5-flash
- BSEP before Architect
- four bounded BSEP projections
- horizontal actors
- strict vertical parent -> child dependencies
- runtime-owned what_runtime_used / what_runtime_rejected
- secret scan PASS
- no real payment/ticket/booking/effects

Artifact-backed human story renderer: PASS.

- 12 actor cards
- actor inputs / outputs / runtime-used / runtime-rejected visible
- canonical semantic summaries loaded from artifacts
- no provider/network/Gemini rerun
- raw responses hidden by default
- explicit transparency guarded by source secret scan

Source audits:

- `docs/audit_reports/auditor_tri_party_airline_live_semantic_lane_real_run_v01.log`
- `docs/audit_reports/auditor_human_tri_party_airline_live_semantic_story_renderer_v01.log`

Source runtime/docs:

- `demo/run_tri_party_airline_ticket_purchase_mock_e2e_v01.py`
- `demo/run_tri_party_airline_live_semantic_lane_v01.py`
- `demo/run_human_tri_party_airline_live_semantic_story_v01.py`
- `docs/tri_party_airline_ticket_purchase_mock_e2e_preflight_v01.md`
- `docs/tri_party_airline_live_semantic_lane_preflight_v01.md`

## Explicit Gates

- Do not start the Ledger implementation until the Ticket/Purchase Corridor has
  deterministic PASS and audit PASS.
- Do not start Crypto Artifact Seal implementation until the Corridor and
  Ledger have deterministic PASS and audit PASS.
- Do not start Sealed Trace Replay Verifier implementation until the Crypto
  Artifact Seal has deterministic PASS and audit PASS.
- The first implementation gate after this umbrella preflight is only:
  Airline Ticket/Purchase Corridor v0.1.

## Architectural Geometry

Before Root:

- semantic/reasoning plane
- Airline live semantic actors may analyze, compare, explain, rank, and return
  validated canonical semantic evidence
- BSEP remains the bounded membrane
- provider output remains advisory
- provider output is not truth
- provider output is not authority
- provider output is not action permission

At Root boundary:

- each side-specific Root validates evidence within its own authority scope
- ClientRoot cannot issue a ticket
- AirlineRoot cannot authorize BankRoot payment
- BankRoot cannot create an airline ticket
- no shared reviewer becomes a fourth Root
- no one central "God packet" may absorb all three Root authorities

After Root:

- deterministic contract/commit plane only
- Root-created or Root-authorized scoped artifacts flow into side-specific
  contract corridors
- corridor validates and fulfils only declared mock steps
- receipts/status/evidence return upward
- authority never expands
- reasoning does not restart
- no post-Root LLM actor is introduced

## Root-Centered Side-Local Phase Loops

The Airline corridor is not one long corridor after one global Root approval.

Canonical geometry:

```text
AirlineRoot review
-> Airline offer/hold contract phase
-> AirlineRoot audit/status boundary

ClientRoot review
-> Client purchase-intent contract phase
-> ClientRoot audit/status boundary

BankRoot review
-> Bank payment-authorization contract phase
-> BankRoot audit/status boundary

AirlineRoot review
-> Airline mock ticket-issue contract phase
-> AirlineRoot audit/status boundary

ClientRoot review
-> Client completion observation
-> ClientRoot final purchase status
```

Rules:

- Each phase has its own side-specific Root gate.
- A PASS from one Root does not grant authority to another Root.
- Evidence may cross Root boundaries.
- Authority does not cross Root boundaries.
- No central Root replaces ClientRoot, AirlineRoot, or BankRoot.
- No shared corridor report becomes a fourth Root.
- RootReview and RootFinal are not interchangeable.
- No post-Root LLM reasoning restarts inside any contract phase.

## Existing ActionCommitPacket / Corridor Reuse Map

Read-only sources inspected for this preflight:

- `hedgehog/action_commit_packet_v02.py`
- `tests/test_action_commit_packet_contract_corridor_v02.py`
- `docs/root_centered_phase_loops_actioncommitpacket_geometry_v01.md`
- `docs/action_commit_packet_contract_fulfillment_corridor_preflight_v01.md`

Reuse these generic invariants where applicable:

- Allowed(child) ⊆ Allowed(parent)
- Scope(child) ⊆ Scope(parent)
- Forbidden(child) ⊇ Forbidden(parent)
- TTL(child) ≤ TTL(parent)
- adapter must be allowed by packet
- packet/step parent binding must match
- idempotency is required
- expired packet fails closed
- duplicate/replay pressure fails closed
- receipt is evidence only
- receipt cannot create future permission
- mismatch returns FAIL_CLOSED / RETURN_TO_ROOT
- reasoning does not restart after Root

Do not duplicate:

- Root-only creation geometry
- generic receipt-is-evidence boundary
- generic TTL/idempotency containment
- generic packet registry/replay concepts where existing contracts can be
  composed safely

Do not create a second universal authority engine.

Airline-specific code should become a domain contract projection over the
existing Root/corridor invariants, not an architectural fork.

## Layer 1 — Airline Ticket/Purchase Corridor v0.1

Purpose:

Promote the existing deterministic Airline fixtures and semantic results into a
bounded mock business transaction.

The semantic lane is the cognitive plane. The Ticket/Purchase Corridor is the
deterministic contract fulfilment plane.

Required human formula:

Semantic lane may explain. Runtime validates and canonicalizes. Side-specific
Roots create or authorize scoped contract artifacts. The corridor fulfils only
the scoped mock contract. Receipts return as evidence. No provider creates
packets, payment, ticket, receipt, booking, or authority.

Required tri-party corridor model:

The "one corridor" is an umbrella transaction composed of side-local,
Root-scoped contract phases:

1. AirlineRoot offer/hold phase
2. ClientRoot purchase-intent authorization phase
3. BankRoot payment-authorization phase
4. AirlineRoot mock ticket-issue phase
5. ClientRoot mock purchase completion observation phase

Initial user travel intent belongs to the semantic/reasoning plane.
ClientPurchaseIntentV01 is a scoped contract artifact for an already selected
and held offer. Therefore ClientPurchaseIntentV01 cannot precede Airline
offer/hold evidence. This ordering must match the Ledger dependency:
purchase_intent_created depends_on hold_created.

No central corridor becomes authority over ClientRoot, AirlineRoot, or BankRoot.

Required transaction identity:

- transaction_id: tri_airline_purchase:PAR-LIM:2026-08-12:client_001
- client_root_id: root:client_os_001
- airline_root_id: root:mock_airline_al
- bank_root_id: root:mock_bank_a
- mock_only: true
- real_world_effects_allowed: false

Required scoped purchase fields:

- transaction_id
- client_root_id
- airline_root_id
- bank_root_id
- offer_id
- hold_id
- amount
- currency
- passenger_ref
- route_ref
- departure_date
- return_date
- deadline
- ttl_seconds
- idempotency_key
- allowed_action: mock_purchase_only
- forbidden_actions
- allowed_adapters
- real_world_effects_allowed: false

Required future corridor artifacts:

1. AirlineOfferPacketV01
   - created_by: AirlineRoot
   - root_owner: AirlineRoot
   - selected offer facts
   - route, price, currency, baggage, seat, TTL
   - evidence only
   - not purchase permission
   - not payment permission
   - not ticket permission

2. AirlineHoldCommitPacketV01
   - created_by: AirlineRoot
   - root_owner: AirlineRoot
   - scoped to one offer / passenger ref / route / TTL
   - allowed_action: mock_offer_hold
   - cannot authorize payment
   - cannot issue ticket
   - cannot survive expiry

3. AirlineOfferHoldReceiptV01
   - produced by deterministic Airline hold corridor
   - evidence only
   - not payment permission
   - not ticket permission
   - cannot create future permission

4. ClientPurchaseIntentV01
   - created_by: ClientRoot
   - root_owner: ClientRoot
   - may reference scoped human approval evidence
   - source_human_approval_ref is evidence for ClientRoot
   - human approval alone cannot create ClientPurchaseIntentV01
   - human approval alone cannot create ActionCommitPacket
   - human approval alone cannot create receipt, payment authorization, ticket,
     booking, or future permission
   - ClientRoot validates the scoped human approval evidence and creates the
     ClientPurchaseIntentV01
   - scoped to selected offer / max amount / currency / passenger ref
   - expresses client purchase approval
   - does not create BankRoot authority
   - does not create AirlineRoot authority
   - does not issue ticket
   - does not execute payment

Human approval formula:

```text
HumanApproval(scope) = scoped evidence for ClientRoot.
ClientRootDecision + HumanApproval(scope)
-> ClientRoot-created ClientPurchaseIntentV01(scope).
```

5. BankPaymentAuthorizationRefV01
   - references a BankRoot-created authorization receipt
   - root_owner: BankRoot
   - amount/currency/merchant/idempotency/expiry bound
   - evidence only
   - not ticket permission
   - not settlement
   - not real payment

6. AirlineTicketIssueIntentV01
   - created only by AirlineRoot
   - requires:
     - valid unexpired AirlineHoldCommitPacket / OfferHoldReceipt
     - valid ClientPurchaseIntent
     - valid BankPaymentAuthorizationRef
     - amount/currency/merchant match
     - passenger/route match
     - transaction_id match
   - allowed_action: mock_ticket_issue
   - real_ticket_allowed: false
   - real_booking_allowed: false
   - real_airline_api_allowed: false

7. MockTicketReceiptV01
   - produced by deterministic Airline ticket corridor
   - evidence only
   - not a real ticket
   - does not create payment
   - cannot authorize a future ticket

8. MockPurchaseReceiptV01
   - produced after all mock phases complete
   - transaction summary evidence only
   - records observed mock fulfilment
   - cannot replace side-specific Root finals
   - cannot create future permission
   - cannot rewrite Root truth

9. TriPartyPurchaseCorridorReportV01
   - deterministic validation/fulfilment report
   - not authority
   - not permission
   - not FinalOutput
   - not a fourth Root

Artifact classification note:

- AirlineHoldCommitPacketV01 and AirlineTicketIssueIntentV01 are Airline
  domain contract projections that reuse existing ActionCommitPacket v0.2
  Root-creation, scope-containment, TTL, idempotency, binding, and replay
  invariants.
- ClientPurchaseIntentV01 is a ClientRoot-owned purchase authorization
  artifact.
- BankPaymentAuthorizationRefV01 is a BankRoot-owned evidence/reference
  artifact bound to a BankRoot-created authorization receipt.
- These artifacts do not form a new universal contract envelope.
- None of them absorbs authority from another Root.
- Receipt objects remain evidence only.

Required state machine:

1. semantic_lane_validated
2. airline_root_offer_hold_review_completed
3. airline_offer_packet_validated
4. airline_hold_packet_validated
5. airline_offer_hold_receipt_created
6. client_root_purchase_intent_review_completed
7. client_purchase_intent_validated
8. bank_root_payment_authorization_review_completed
9. bank_payment_authorization_ref_validated
10. airline_root_ticket_issue_review_completed
11. airline_ticket_issue_intent_validated
12. mock_ticket_receipt_created
13. mock_purchase_receipt_created
14. client_root_completion_review_completed
15. side_specific_root_finals_recorded

No phase may be skipped.
All phases carry the same transaction_id.
Failure at any phase returns FAIL_CLOSED / RETURN_TO_THE_RELEVANT_ROOT.
A later phase cannot repair an invalid earlier phase.

Required Root ownership:

ClientRoot may create/authorize:

- ClientPurchaseIntent
- client-side final purchase status

AirlineRoot may create/authorize:

- AirlineOfferPacket
- AirlineHoldCommitPacket
- AirlineTicketIssueIntent
- airline-side final ticket status

BankRoot may create/authorize:

- BankPaymentAuthorizationRef source receipt
- bank-side final authorization status

Deterministic corridor/adapter may create:

- OfferHoldReceipt
- MockTicketReceipt
- MockPurchaseReceipt

But corridor/adapter-created receipts remain evidence only.

Required final geometry:

Each Root creates its own side-specific final status.

A shared TriPartyTransactionSummary may aggregate the three statuses, but:

- it is not a fourth Root
- it is not authority
- it cannot override a side-specific Root
- it cannot create payment/ticket/booking permission

### Layer 1 Fail-Closed Checks

- ticket cannot be issued without AirlineRoot hold
- purchase cannot proceed without ClientRoot purchase intent
- purchase cannot be authorized without BankRoot approval
- provider cannot create purchase packet
- provider cannot create hold packet
- provider cannot create ticket issue intent
- provider cannot create receipt
- provider cannot alter passenger_ref
- provider cannot alter amount
- provider cannot alter currency
- provider cannot alter route
- provider cannot alter transaction_id
- expired hold blocks purchase
- expired payment authorization blocks ticket issue
- mismatched amount blocks purchase
- mismatched currency blocks purchase
- mismatched merchant blocks purchase
- mismatched passenger blocks purchase
- mismatched route blocks purchase
- duplicate idempotency key blocks duplicate fulfilment
- wrong Root owner blocks artifact
- mixed transaction_id blocks corridor
- old quote is not ticket permission
- old payment receipt is not current authorization
- old ticket receipt is not future ticket permission
- ticket receipt is evidence only
- purchase receipt is evidence only
- receipt does not rewrite Root truth
- receipt cannot create future permission
- post-Root reasoning restart is forbidden
- real airline API count remains 0
- real bank API count remains 0
- real GDS API count remains 0
- real payment count remains 0
- real ticket count remains 0
- real booking count remains 0
- real-world effects count remains 0

Future negative tests to record:

- client_purchase_intent_before_offer_hold_rejected
- client_purchase_intent_without_selected_offer_rejected
- human_approval_directly_creating_purchase_intent_rejected
- human_approval_directly_creating_action_commit_packet_rejected
- global_side_root_reviews_completed_shortcut_rejected
- airline_root_review_cannot_replace_client_root_review
- client_root_review_cannot_replace_bank_root_review
- bank_root_review_cannot_replace_airline_root_ticket_issue_review
- phase_failure_cannot_be_repaired_by_later_phase
- cross_root_evidence_does_not_transfer_authority

### Recommended First Implementation Slice After This Preflight

Slice B — local Airline corridor contracts and validators.

Recommended files:

- `hedgehog/domains/airline/ticket_purchase_corridor_v01.py`
- `tests/test_airline_ticket_purchase_corridor_v01.py`

Scope:

- frozen local dataclasses/constants
- scoped artifact contracts
- Root ownership validation
- TTL/idempotency validation
- dependency validation
- receipt evidence-only validation
- no runtime integration
- no Gemini/provider/network
- no real APIs
- no real effects

## Core / Domain Boundary

- Hedgehog core remains domain-neutral.
- Airline contracts live under `hedgehog.domains.airline`.
- The domain module depends on core; core does not depend on the domain.
- Airline-specific Offer/Hold/Ticket/PNR concepts are not universal core types.
- This Slice is a domain contract projection, not a Needle implementation.
- Generic core extraction may be considered only after the same contract
  structures are demonstrated in at least two actually implemented and
  explicitly approved domain projections.
- Existing Supplier Payment and Airline Ticket/Purchase evidence may be
  compared where their contracts are genuinely equivalent.
- Any future comparison domain must be introduced by an accepted roadmap or
  specification; no unnamed or invented domain may be assumed.
- Domain-specific Offer/Hold/Ticket/PNR fields must remain outside core.
- No second universal authority engine is introduced.

Important:

- Compose existing ActionCommitPacket/corridor invariants where possible.
- Do not create a second generic packet registry.
- Do not create a second universal contract envelope unless the preflight
  proves the current generic contracts cannot represent the required scope.
- Do not integrate into the existing Airline runner in the first implementation
  slice.

Later corridor slices to record only:

Slice C:

- deterministic corridor state machine
- side-local contract phases
- mock fulfilment only

Slice D:

- integrate corridor into existing deterministic Airline runner
- no new duplicate demo

Slice E:

- corridor audit / artifact-backed human corridor story

Only Slice B becomes the next implementation task after this preflight.

## Layer 2 — Airline Transaction Artifact Ledger v0.1

Gate:

Do not implement until Ticket/Purchase Corridor deterministic PASS and audit
PASS.

Purpose:

Define exactly what the transaction produced before attempting cryptographic
sealing.

Required ledger event types:

- transaction_started
- semantic_claim_created
- bsep_projection_created
- offer_created
- hold_created
- purchase_intent_created
- payment_authorization_created
- ticket_intent_created
- mock_ticket_receipt_created
- mock_purchase_receipt_created
- root_final_created

Required ledger entry fields:

- ledger_index
- artifact_id
- artifact_type
- transaction_id
- root_owner
- created_by
- authority_class
- evidence_class
- depends_on
- event_time
- recorded_at
- canonical_hash_input
- raw_secret_included: false
- raw_provider_text_included: false
- real_world_effects_count: 0

Required ledger rules:

- Ledger records trace.
- Ledger is not authority.
- Ledger does not prove truth.
- Ledger does not authorize action.
- Ledger does not create FinalOutput.
- Ledger does not create packets.
- Ledger does not create receipts.
- Ledger does not create payment.
- Ledger does not create ticket.
- Ledger does not create booking.
- Ledger cannot alter Root ownership.
- Ledger cannot repair a missing corridor dependency.
- Ledger cannot turn evidence into permission.

Required dependency examples:

- hold_created depends_on offer_created
- purchase_intent_created depends_on hold_created
- payment_authorization_created depends_on purchase_intent_created
- ticket_intent_created depends_on hold_created + purchase_intent_created +
  payment_authorization_created
- mock_ticket_receipt_created depends_on ticket_intent_created
- mock_purchase_receipt_created depends_on mock_ticket_receipt_created +
  payment_authorization_created
- root_final_created depends_on the relevant side-local evidence set

Required ledger fail-closed checks:

- duplicate artifact_id
- duplicate ledger_index
- mixed transaction_id
- missing dependency
- cyclic dependency
- wrong Root owner
- provider-created action artifact
- receipt classified as permission
- ledger entry classified as FinalOutput authority
- secret-bearing canonical hash input
- raw provider output treated as authority
- nonzero effect counter

Required canonical-chain policy for v0.1:

- canonical transaction chain contains validated canonical semantic summaries,
  BSEP projections, corridor packets, corridor validations, mock receipts, and
  side-specific Root finals
- raw provider prompt/response artifacts remain auxiliary observation artifacts
- raw provider text is excluded from the canonical authority/evidence chain
- auxiliary raw artifacts may be listed by opaque artifact reference
- no raw passport/card/IBAN/payment token/API key enters canonical_hash_input

## Layer 3 — Airline Crypto Artifact Seal v0.1

Gate:

Do not implement until Ticket/Purchase Corridor and Transaction Artifact Ledger
both have deterministic PASS and audit PASS.

Purpose:

Seal the complete canonical transaction artifact set after the set and its
dependencies are already defined.

Proof-grade v0.1 target only:

- canonical JSON
- explicit canonicalization profile/version
- stable SHA-256 hash
- artifact manifest
- ordered hash chain
- signature placeholder
- seal verification report

Do not claim:

- production key management
- production signatures
- hardware-backed keys
- PKI
- non-repudiation
- legal signing
- production cryptographic security

Required crypto formula:

Crypto seal proves continuity and integrity of the declared artifact set. Crypto
seal does not prove semantic truth. Crypto seal does not grant permission.
Crypto seal does not create authority. Crypto seal does not make provider
output trusted. Crypto seal does not repair invalid corridor state. Crypto seal
does not create FinalOutput.

Required manifest fields:

- seal_id
- transaction_id
- canonicalization_profile_id
- hash_algorithm
- artifact_count
- ordered_artifact_refs
- ordered_artifact_hashes
- chain_head_hash
- chain_tail_hash
- previous_manifest_ref
- signature_placeholder_present
- signature_verified: false for placeholder-only v0.1
- secret_scan_passed
- raw_secret_included: false
- real_world_effects_count: 0

Required crypto checks:

- changing any canonical artifact breaks manifest verification
- deleting any required artifact breaks verification
- adding an undeclared artifact is detected
- reordering the chain is detected
- wrong transaction_id is detected
- wrong artifact dependency is detected
- wrong Root owner is detected
- canonical serialization is stable
- secret-bearing input is rejected before hashing
- raw provider text is not treated as authority
- receipt remains evidence only after sealing
- Root final remains Root final after sealing
- signature placeholder is not reported as a verified signature
- seal verification does not grant permission

## Layer 4 — Airline Sealed Trace Replay Verifier v0.1

Gate:

Do not implement until Crypto Artifact Seal deterministic PASS and audit PASS.

Purpose:

Verify and reconstruct the sealed Airline transaction without another Gemini call.

Required verifier behavior:

- load sealed artifact manifest
- verify canonicalization profile
- verify all artifact hashes
- verify ordered hash chain
- verify artifact count
- verify required artifacts exist
- verify one transaction_id
- reconstruct transaction timeline
- validate dependency DAG
- validate Root ownership
- validate evidence classes
- validate authority classes
- validate packet lineage
- validate receipt lineage
- validate no provider-created action
- validate no receipt-created future permission
- validate no cross-Root authority transfer
- validate no real effects
- produce replay verification report

Required replay rules:

- Replay verifier does not call Gemini.
- Replay verifier does not call provider/network.
- Replay verifier does not rerun semantic reasoning.
- Replay verifier does not decide semantic truth.
- Replay verifier does not grant permission.
- Replay verifier does not create packet.
- Replay verifier does not create receipt.
- Replay verifier does not execute payment.
- Replay verifier does not issue ticket.
- Replay verifier does not create booking.
- Replay verifier does not create FinalOutput.
- Replay report is verification evidence only.

Required replay fail-closed cases:

- changed artifact
- missing artifact
- undeclared artifact
- reordered chain
- wrong transaction_id
- invalid dependency
- cyclic dependency
- wrong Root owner
- provider-created action artifact
- receipt classified as authority
- missing side-specific Root final
- nonzero real API/payment/ticket/booking/effect counter
- failed secret scan
- invalid or missing manifest

Required replay output:

AirlineSealedTraceReplayReportV01:

- verifier_status
- transaction_id
- manifest_verified
- hashes_verified
- chain_order_verified
- dependencies_verified
- root_ownership_verified
- authority_boundaries_verified
- evidence_classes_verified
- secret_boundary_verified
- real_effects_zero_verified
- reconstructed_timeline
- verification_errors
- provider_called: false
- network_used: false
- gemini_called: false
- permission_created: false
- real_world_effects_count: 0

## Cross-Layer Invariants

- One transaction_id across semantic, corridor, ledger, seal, and replay.
- ClientRoot, AirlineRoot, and BankRoot remain side-specific.
- No shared summary becomes a fourth Root.
- Provider output remains advisory.
- BSEP remains bounded context, not authority.
- Semantic actor output cannot create contract artifacts.
- Only the correct side-specific Root may create/authorize its contract
  artifact.
- Corridor fulfils; corridor does not decide.
- Receipt is evidence only.
- Ledger records; ledger does not authorize.
- Crypto seals continuity; crypto does not prove truth.
- Replay verifies; replay does not grant permission.
- No post-Root reasoning restart.
- No authority expansion.
- No raw secrets in canonical transaction artifacts.
- No real airline/bank/GDS calls.
- No real payment.
- No real ticket.
- No real booking.
- No real-world effects.

## Authority Table

ClientRoot:

- may authorize ClientPurchaseIntent
- may not issue ticket
- may not authorize BankRoot payment
- may not create BankRoot receipt

AirlineRoot:

- may create AirlineOfferPacket
- may create AirlineHoldCommitPacket
- may create AirlineTicketIssueIntent
- may not authorize BankRoot payment
- may not expose raw passport

BankRoot:

- may create payment authorization evidence/ref
- may not create airline ticket
- may not create airline order

Corridor:

- may validate and fulfil scoped mock steps
- may create evidence-only receipts
- may not create authority or expand scope

Ledger:

- may record artifacts/events
- may not authorize or execute

Crypto seal:

- may hash/canonicalize/verify continuity
- may not prove truth or permission

Replay verifier:

- may verify/reconstruct
- may not authorize, execute, or create FinalOutput

## Implementation Program / Gates

Program Gate 1:

Airline Ticket/Purchase Corridor v0.1

- next implementation gate
- starts only after this preflight is accepted and committed

Program Gate 2:

Airline Transaction Artifact Ledger v0.1

- blocked until Corridor PASS + audit PASS

Program Gate 3:

Airline Crypto Artifact Seal v0.1

- blocked until Corridor PASS + Ledger PASS + both audits

Program Gate 4:

Airline Sealed Trace Replay Verifier v0.1

- blocked until Crypto Seal PASS + audit PASS

After Gate 4 only:

- ExecutionModeRouter may become the next engineering preflight
- Router is not part of this implementation program

## Definition of Done for This Umbrella Preflight

- four-layer order explicitly fixed
- current closed Airline basis recorded
- existing ActionCommitPacket reuse map recorded
- first implementation scope limited to Corridor Slice B local contracts
- side-specific Root ownership recorded
- no central authority packet introduced
- corridor state machine recorded
- artifact taxonomy recorded
- ledger dependency model recorded
- crypto non-claims recorded
- replay no-Gemini behavior recorded
- cross-layer invariants recorded
- negative test matrix recorded
- production/non-effect boundaries recorded
- runtime/tests untouched

## Non-Goals

- no real airline API
- no real bank API
- no GDS/NDC/ONE Order implementation
- no real card acquiring
- no real Open Banking
- no settlement
- no BSP
- no real ticket
- no real payment
- no real booking
- no production signatures
- no key management
- no PKI
- no hardware security module
- no public auditor package
- no production connector
- no Router
- no Synthesis Loop
- no GT-TTL
- no AVF feedback implementation
- no packet kill-switch
- no DRS v0.2 implementation
- no NeedleFactory
- no Marennya / UP

## Validation Plan for This Preflight

- `python3 -m json.tool specs/machine_manifest_v0_25.json >/dev/null`
- `git status --short --untracked-files=all`
- `git diff --stat`
- `git diff --check`
- `git diff --name-only`
- explicit trailing whitespace check for this new preflight file
- positive grep for required layer/order/boundary markers
- forbidden grep for implementation, authority, production, and real-effect
  claims

## Final Status

- preflight_status: READY_FOR_REVIEW
- next_implementation_gate: Airline Ticket/Purchase Corridor v0.1 Slice B local
  contracts and validators only
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- real_world_effects_count: 0
