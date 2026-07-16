# Hedgehog OS — Airline All-Real Full-Stack Run v0.1
## Artifact-Backed Human Story

- document_status: HUMAN_EXPLANATION
- explanation_profile: airline_all_real_full_stack_v01
- evidence_base_commit: ec50c1f
- package_generation_commit: 3301ce3
- anchor_publication_commit: a701743
- anchored_replay_audit_commit: ec50c1f
- implementation_base_commit: a8d5036
- compatibility_repair_commit: 38ad0b0
- provider_mode: real_provider
- model: gemini-2.5-flash
- official_generation_status: PASS
- stored_crypto_status: SELF_CONSISTENT_UNANCHORED
- fresh_anchored_verification_status: PASS
- replay_status: PASS
- provider_called_during_explanation: false
- network_called_during_explanation: false
- gemini_called_during_explanation: false
- replay_rerun: false
- package_modified: false
- real_world_effects_count: 0
- production_ready_claimed: false

This document explains accepted evidence. It does not execute any part of the
transaction and does not replace the machine reports or audit logs.

## 1. Executive Summary

| Headline measure | Observed value |
| --- | ---: |
| Real Gemini semantic actors | 12 |
| Sovereign Roots | 3 |
| Deterministic transactions | 1 |
| Ledger artifacts | 19 |
| Dependency edges | 29 |
| Root finals | 3 |
| Exact Crypto source files | 9 |
| Critical package files | 11 |
| Committed external anchors | 1 |
| Deterministic Replay rows | 19 |
| Real-world effects | 0 |

The central architectural result is separation of semantic reasoning from
authority. Gemini produced bounded advisory semantic evidence. Gemini did not
become a Root, grant permission, create authority, or execute the transaction.

The deterministic Root-controlled system validated the provider output,
accepted bounded meanings, rejected authority and effect claims, and routed
the accepted evidence through the Ticket/Purchase Corridor, Transaction
Artifact Ledger, Crypto Artifact Seal, committed external Anchor, and
deterministic Sealed Trace Replay.

The result is a proof-level evidence chain for one mock Airline transaction,
not a real airline transaction.

## 2. The User’s Travel Task

The fixed scenario asked the system to evaluate a mock trip from Paris to Lima
on 2026-08-12 under semantic profile Preference A.

| Field | Accepted value |
| --- | --- |
| Route | PAR → LIM |
| Travel date | 2026-08-12 |
| Transaction | `tri_airline_purchase:PAR-LIM:2026-08-12:client_001` |
| Semantic profile | Preference A |
| Selected offer | `offer:mock_airline_al:PAR-LIM:001` |
| Model | `gemini-2.5-flash` |
| Provider mode | `real_provider` |
| Generation status | `PASS` |

The human result is that the accepted evidence consistently selected mock
Offer A, constructed a deterministic mock hold/payment/ticket path, sealed the
resulting trace, and later reconstructed it without rerunning the transaction.

> **MOCK EVIDENCE — NOT A REAL AIRLINE TICKET, BOOKING, OR PAYMENT.**

## 3. The Twelve Gemini Actors

The actors are listed in their exact committed call order. Every actor used the
same real-provider model, returned a schema-valid result, and was accepted only
as bounded advisory evidence.

### 3.1 `tri_party_airline_orchestrator_llm`

- **Human role:** Interpret the whole tri-party goal and propose the bounded semantic route that precedes BSEP creation.
- **Root side or advisory side:** Transaction-level advisory side.
- **Bounded information available to the actor:** Sealed references for the fixed transaction and deterministic mock Airline evidence; no unbounded private or connector context.
- **Accepted canonical answer:** The transaction should be routed through a bounded tri-party semantic program and a BSEP membrane before downstream architecture work.
- **Important accepted structured fields:** `actor_id=tri_party_airline_orchestrator_llm`; `side=transaction`; exact transaction ID; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Runtime BSEP construction and the bounded context supplied to the semantic Architect.
- **Authority boundary:** Advisory only; it created no authority, permission, action, payment, ticket, booking, packet, receipt, or FinalOutput.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_airline_orchestrator_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_airline_orchestrator_llm_validation.json`.

### 3.2 `tri_party_airline_semantic_architect_llm`

- **Human role:** Propose a semantic actor topology and validation obligations from BSEP-derived bounded context.
- **Root side or advisory side:** Transaction-level advisory side.
- **Bounded information available to the actor:** The validated BSEP-derived transaction context, sealed references, and deterministic mock Airline evidence.
- **Accepted canonical answer:** A bounded actor topology and validation plan can organize the client, airline, bank, vertical-cell, and cross-root reviews.
- **Important accepted structured fields:** `actor_id=tri_party_airline_semantic_architect_llm`; `side=transaction`; exact transaction ID; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Runtime orchestration of the remaining bounded semantic reviewers and validators.
- **Authority boundary:** Advisory only; the proposed topology did not become authority, permission, a transaction action, or a Root decision.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_airline_semantic_architect_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_airline_semantic_architect_llm_validation.json`.

### 3.3 `client_purchase_intent_reviewer_llm`

- **Human role:** Review which hard-compatible offer best matches the client’s soft travel preferences.
- **Root side or advisory side:** Client-side advisory evidence for ClientRoot.
- **Bounded information available to the actor:** Client-side BSEP projection, sealed references, the fixed transaction identity, and deterministic mock offers.
- **Accepted canonical answer:** Offer `offer:mock_airline_al:PAR-LIM:001` best matches the lower-price and window-seat preferences while the compared offers remain hard-compatible.
- **Important accepted structured fields:** `actor_id=client_purchase_intent_reviewer_llm`; `side=client`; exact transaction ID; accepted Offer A identity; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Validated canonical semantic evidence and the ClientRoot offer-selection decision.
- **Authority boundary:** Advisory only; ClientRoot, not Gemini, made the accepted client-side decision.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/client_purchase_intent_reviewer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/client_purchase_intent_reviewer_llm_validation.json`.

### 3.4 `client_profile_privacy_reviewer_llm`

- **Human role:** Review how passenger and payment references remain opaque and how private fields stay bounded.
- **Root side or advisory side:** Client-side advisory evidence for ClientRoot and the secret boundary.
- **Bounded information available to the actor:** Client-side sealed references and deterministic descriptions of opaque passenger/payment identities; no raw private profile or payment instrument.
- **Accepted canonical answer:** Passenger and payment references should remain opaque, with access controlled through bounded privacy mechanisms rather than raw-field exposure.
- **Important accepted structured fields:** `actor_id=client_profile_privacy_reviewer_llm`; `side=client`; exact transaction ID; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Runtime privacy/secret-boundary checks and ClientRoot review.
- **Authority boundary:** Advisory only; it neither accessed raw secrets nor authorized use of private or payment data.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/client_profile_privacy_reviewer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/client_profile_privacy_reviewer_llm_validation.json`.

### 3.5 `airline_offer_policy_reviewer_llm`

- **Human role:** Review the proposed Airline offer under bounded policy evidence.
- **Root side or advisory side:** Airline-side advisory evidence for AirlineRoot.
- **Bounded information available to the actor:** Airline BSEP projection, sealed references, deterministic mock Airline evidence, and the fixed transaction.
- **Accepted canonical answer:** Offer `offer:mock_airline_al:PAR-LIM:001` was reviewed as acceptable advisory policy evidence.
- **Important accepted structured fields:** `actor_id=airline_offer_policy_reviewer_llm`; `side=airline`; exact transaction ID; accepted Offer A identity; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Airline fare/seat vertical children, semantic synthesis, and AirlineRoot offer resolution.
- **Authority boundary:** Advisory only; AirlineRoot retained authoritative offer resolution.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_offer_policy_reviewer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_offer_policy_reviewer_llm_validation.json`.

### 3.6 `airline_fare_rules_vertical_cell_llm`

- **Human role:** Perform a bounded child review of fare-rule considerations for the proposed offer.
- **Root side or advisory side:** Airline-side vertical advisory cell.
- **Bounded information available to the actor:** Airline BSEP projection plus the validated canonical summary from `airline_offer_policy_reviewer_llm`; no parent raw response or sibling raw output.
- **Accepted canonical answer:** Offer `offer:mock_airline_al:PAR-LIM:001` passed the bounded fare-rules advisory review.
- **Important accepted structured fields:** `actor_id=airline_fare_rules_vertical_cell_llm`; `side=airline`; parent actor `airline_offer_policy_reviewer_llm`; parent validation `PASS`; parent canonical summary received; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Parent/Root review and validated causal semantic synthesis.
- **Authority boundary:** Advisory only; the child returned evidence to parent or Root review and created no authority or transaction artifact.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_fare_rules_vertical_cell_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_fare_rules_vertical_cell_llm_validation.json`.

### 3.7 `airline_seat_baggage_vertical_cell_llm`

- **Human role:** Perform a bounded child review of seat and baggage considerations for the proposed offer.
- **Root side or advisory side:** Airline-side vertical advisory cell.
- **Bounded information available to the actor:** Airline BSEP projection plus the validated canonical summary from `airline_offer_policy_reviewer_llm`; no parent raw response or sibling raw output.
- **Accepted canonical answer:** Offer `offer:mock_airline_al:PAR-LIM:001` passed the bounded seat/baggage advisory review.
- **Important accepted structured fields:** `actor_id=airline_seat_baggage_vertical_cell_llm`; `side=airline`; parent actor `airline_offer_policy_reviewer_llm`; parent validation `PASS`; parent canonical summary received; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Parent/Root review and validated causal semantic synthesis.
- **Authority boundary:** Advisory only; the child did not make the AirlineRoot decision or create a ticket/booking artifact.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_seat_baggage_vertical_cell_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_seat_baggage_vertical_cell_llm_validation.json`.

### 3.8 `airline_ticketing_policy_reviewer_llm`

- **Human role:** Review the preconditions for mock ticket evidence.
- **Root side or advisory side:** Airline-side advisory evidence for AirlineRoot.
- **Bounded information available to the actor:** Airline-side sealed references and deterministic mock hold, payment-authorization, client-approval, and ticket-evidence concepts.
- **Accepted canonical answer:** Mock ticket evidence requires a confirmed hold, successful mock payment authorization, and explicit client approval; the mock receipt is not an actual issued ticket.
- **Important accepted structured fields:** `actor_id=airline_ticketing_policy_reviewer_llm`; `side=airline`; exact transaction ID; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** AirlineRoot ticket-issue review and the deterministic Corridor’s ticket phase.
- **Authority boundary:** Advisory only; it did not grant ticket permission or issue any ticket.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_ticketing_policy_reviewer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_ticketing_policy_reviewer_llm_validation.json`.

### 3.9 `bank_payment_policy_reviewer_llm`

- **Human role:** Review the bounded mock payment-authorization evidence.
- **Root side or advisory side:** Bank-side advisory evidence for BankRoot.
- **Bounded information available to the actor:** Bank BSEP projection and sealed mock amount, merchant, debtor-slot, consent, and payment-token references.
- **Accepted canonical answer:** The bounded fields describe a mock authorization proposal and protected payment reference, not settlement or an external bank action.
- **Important accepted structured fields:** `actor_id=bank_payment_policy_reviewer_llm`; `side=bank`; exact transaction ID; deterministic review status `PASS`; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Bank idempotency child review and BankRoot authorization-boundary validation.
- **Authority boundary:** Advisory only; BankRoot retained the scoped authorization boundary and no payment was executed.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/bank_payment_policy_reviewer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/bank_payment_policy_reviewer_llm_validation.json`.

### 3.10 `bank_idempotency_risk_vertical_cell_llm`

- **Human role:** Review duplicate-payment, idempotency, expiry, TTL, amount, and merchant mismatch risk.
- **Root side or advisory side:** Bank-side vertical advisory cell.
- **Bounded information available to the actor:** Bank BSEP projection plus the validated canonical summary from `bank_payment_policy_reviewer_llm`; no parent raw response or sibling raw output.
- **Accepted canonical answer:** The bounded mock authorization evidence passed the idempotency and mismatch-pressure review.
- **Important accepted structured fields:** `actor_id=bank_idempotency_risk_vertical_cell_llm`; `side=bank`; parent actor `bank_payment_policy_reviewer_llm`; parent validation `PASS`; parent canonical summary received; deterministic review status `PASS`; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Parent/Root review and BankRoot authorization evidence checks.
- **Authority boundary:** Advisory only; the child created no payment, permission, receipt, or BankRoot final.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/bank_idempotency_risk_vertical_cell_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/bank_idempotency_risk_vertical_cell_llm_validation.json`.

### 3.11 `bank_payment_status_explainer_llm`

- **Human role:** Explain the evidence distinction between mock authorization and settlement.
- **Root side or advisory side:** Bank-side advisory evidence.
- **Bounded information available to the actor:** Bank projection, fixed transaction identity, and deterministic evidence-only payment-status concepts.
- **Accepted canonical answer:** A payment-status receipt is evidence of a mock state; it is neither settlement, action permission, nor final commitment.
- **Important accepted structured fields:** `actor_id=bank_payment_status_explainer_llm`; `side=bank`; exact transaction ID; evidence-only receipt classification; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** BankRoot evidence classification and final trace construction.
- **Authority boundary:** Advisory only; no settlement, payment instruction, or authority was created.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/bank_payment_status_explainer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/bank_payment_status_explainer_llm_validation.json`.

### 3.12 `tri_party_evidence_consistency_reviewer_llm`

- **Human role:** Review consistency across client, airline, and bank evidence.
- **Root side or advisory side:** Cross-root advisory side.
- **Bounded information available to the actor:** Cross-root BSEP projection, sealed references, fixed transaction identity, and deterministic mock evidence.
- **Accepted canonical answer:** Offer `offer:mock_airline_al:PAR-LIM:001` remained coherent across the reviewed evidence.
- **Important accepted structured fields:** `actor_id=tri_party_evidence_consistency_reviewer_llm`; `side=cross_root_advisory`; exact transaction ID; accepted Offer A identity; `validation_status=PASS`; `accepted=true`.
- **Validation result:** `validation_status: PASS`; `accepted: true`.
- **Downstream consumer:** Validated causal synthesis and Root-side consistency checks.
- **Authority boundary:** Advisory only; the reviewer is not a fourth Root and cannot transfer authority across Roots.
- **Evidence files:** `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_evidence_consistency_reviewer_llm_canonical_summary.json`; `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_evidence_consistency_reviewer_llm_validation.json`.

The five causal semantic actors were
`client_purchase_intent_reviewer_llm`,
`airline_offer_policy_reviewer_llm`,
`airline_fare_rules_vertical_cell_llm`,
`airline_seat_baggage_vertical_cell_llm`, and
`tri_party_evidence_consistency_reviewer_llm`. The other seven actors formed
the broader generic semantic program. This classification describes runtime
topology, not authority: all twelve actors remained advisory.

## 4. How the System Chose Offer A

The accepted decision path was:

```text
bounded user constraints
→ BSEP packet
→ four BSEP side projections
→ twelve actor outputs
→ validated canonical semantic evidence
→ ClientRoot offer selection
→ AirlineRoot authoritative offer resolution
→ Offer A
```

The BSEP was created once and validated once before it was used as the bounded
context membrane. Its client, airline, bank, and cross-root advisory
projections all passed.

The actor outputs did not directly select or execute an offer. Runtime
canonicalization accepted bounded semantic meaning and explicitly rejected
provider output as truth, authority, payment permission, ticket permission,
booking permission, or packet/receipt creation.

The causal and deterministic bridge evidence then showed:

| Decision check | Accepted result |
| --- | --- |
| ClientRoot selected offer | `offer:mock_airline_al:PAR-LIM:001` |
| AirlineRoot resolved offer | `offer:mock_airline_al:PAR-LIM:001` |
| Hold contract offer | `offer:mock_airline_al:PAR-LIM:001` |
| Deterministic Corridor offer | `offer:mock_airline_al:PAR-LIM:001` |
| Direct offer override | 0 |
| Default offer | 0 |
| Silent fallback | 0 |
| Provider output used as truth | 0 |
| Provider output used as authority | 0 |

Offer A is therefore a Root-controlled deterministic decision supported by
validated advisory evidence. It is not a ticket purchased by Gemini.

## 5. Three Sovereign Roots

### ClientRoot

ClientRoot owned the client constraints, accepted purchase intent, client-side
offer selection, and `client_root_final:001`.

### AirlineRoot

AirlineRoot owned authoritative offer resolution, the semantic-causal offer
packet, hold packet, ticket-issue intent, mock ticket evidence, and
`airline_root_final:001`.

### BankRoot

BankRoot owned the scoped mock payment-authorization boundary, payment
evidence, and `bank_root_final:001`.

The cross-root reviewer remained advisory evidence only. It did not become a
fourth Root, merge Root authority, or authorize a cross-root action.

Exactly one final artifact exists for each sovereign Root.

## 6. The Five-Phase Ticket/Purchase Corridor

The deterministic Ticket/Purchase Corridor executed once in this order:

1. **Airline offer and hold:** AirlineRoot reviewed the selected offer and
   created deterministic mock offer/hold evidence.
2. **Client purchase intent:** ClientRoot accepted a scoped mock purchase
   intent after the hold evidence.
3. **Bank payment authorization:** BankRoot produced bounded mock
   authorization evidence, not settlement.
4. **Airline ticket issue:** AirlineRoot created a deterministic ticket-issue
   intent and mock ticket receipt only after its declared dependencies.
5. **Client completion:** ClientRoot observed the evidence chain and produced
   mock purchase-receipt/final evidence.

| Corridor measure | Result |
| --- | --- |
| Final status | `PASS` |
| Execution count | 1 |
| Replay Corridor reruns | 0 |
| Real-world effects | 0 |

## 7. The Mock Ticket, PNR, Payment, and Receipt Evidence

> **MOCK / PROOF-LEVEL EVIDENCE**<br>
> **NO REAL TICKET**<br>
> **NO REAL PNR RESERVATION**<br>
> **NO REAL PAYMENT**<br>
> **NO AIRLINE, BANK, OR GDS API CALL**

| Evidence field | Accepted identity |
| --- | --- |
| Transaction ID | `tri_airline_purchase:PAR-LIM:2026-08-12:client_001` |
| Route | PAR → LIM |
| Travel date | 2026-08-12 |
| Selected offer | `offer:mock_airline_al:PAR-LIM:001` |
| ClientRoot | `root:client_os_001` |
| AirlineRoot | `root:mock_airline_al` |
| BankRoot | `root:mock_bank_a` |
| Offer packet ID | `airline_offer_packet:semantic_causal:001` |
| Hold packet ID | `airline_hold_commit_packet:semantic_causal:001` |
| Hold receipt ID | `offer_hold_receipt:mock_airline_al:001` |
| Client purchase-intent ID | `client_purchase_intent:client_001:001` |
| Payment-authorization reference ID | `bank_payment_authorization_ref:mock_bank_a:001` |
| Ticket-issue intent ID | `airline_ticket_issue_commit_packet:mock_airline_al:001` |
| Mock ticket-receipt ID | `mock_ticket_receipt:mock_airline_al:001` |
| Mock purchase-receipt ID | `mock_purchase_receipt:client_001:001` |
| ClientRoot final ID | `client_root_final:001` |
| AirlineRoot final ID | `airline_root_final:001` |
| BankRoot final ID | `bank_root_final:001` |
| Distinct accepted PNR value | Not exposed by the accepted Ledger evidence; no value is invented here. |

Receipts are evidence-only artifacts. The payment reference is mock
authorization evidence, not settlement. The ticket receipt is mock evidence,
not an issued ticket. No external connector consumed these artifacts.

## 8. The 19-Artifact Ledger

The Transaction Artifact Ledger records the accepted trace. It does not
authorize, prove semantic truth, or execute any action.

Its exact geometry is:

- Ledger entries: 19
- Dependency edges: 29
- Root finals: 3
- ClientRoot finals: 1
- AirlineRoot finals: 1
- BankRoot finals: 1
- Cross-root advisory finals: 0

| # | Artifact type | Artifact ID | Root owner | Dependencies | Root final |
| ---: | --- | --- | --- | ---: | --- |
| 0 | AirlineTransactionScopeV01 | `airline_transaction_scope:tri_airline_purchase:PAR-LIM:2026-08-12:client_001` | `transaction_scope:non_authoritative` | 0 | no |
| 1 | ClientBSEPProjectionV01 | `client_bsep_projection` | `bsep_side:client` | 1 | no |
| 2 | AirlineBSEPProjectionV01 | `airline_bsep_projection` | `bsep_side:airline` | 1 | no |
| 3 | BankBSEPProjectionV01 | `bank_bsep_projection` | `bsep_side:bank` | 1 | no |
| 4 | CrossRootAdvisoryBSEPProjectionV01 | `cross_root_bsep_projection` | `bsep_side:cross_root_advisory` | 1 | no |
| 5 | ValidatedAirlineSemanticSelectionEvidenceV01 | `canonical_selection:offer:mock_airline_al:PAR-LIM:001` | `runtime_canonicalization:advisory` | 1 | no |
| 6 | ClientRootOfferSelectionDecisionV01 | `client_root_offer_selection_decision:offer:mock_airline_al:PAR-LIM:001` | `root:client_os_001` | 1 | no |
| 7 | AirlineRootSelectedOfferResolutionV01 | `airline_root_selected_offer_resolution:offer:mock_airline_al:PAR-LIM:001` | `root:mock_airline_al` | 1 | no |
| 8 | AirlineOfferPacketV01 | `airline_offer_packet:semantic_causal:001` | `root:mock_airline_al` | 1 | no |
| 9 | AirlineHoldCommitPacketV01 | `airline_hold_commit_packet:semantic_causal:001` | `root:mock_airline_al` | 1 | no |
| 10 | AirlineOfferHoldReceiptV01 | `offer_hold_receipt:mock_airline_al:001` | `root:mock_airline_al` | 1 | no |
| 11 | ClientPurchaseIntentV01 | `client_purchase_intent:client_001:001` | `root:client_os_001` | 1 | no |
| 12 | BankPaymentAuthorizationRefV01 | `bank_payment_authorization_ref:mock_bank_a:001` | `root:mock_bank_a` | 1 | no |
| 13 | AirlineTicketIssueIntentV01 | `airline_ticket_issue_commit_packet:mock_airline_al:001` | `root:mock_airline_al` | 3 | no |
| 14 | MockTicketReceiptV01 | `mock_ticket_receipt:mock_airline_al:001` | `root:mock_airline_al` | 1 | no |
| 15 | MockPurchaseReceiptV01 | `mock_purchase_receipt:client_001:001` | `root:client_os_001` | 3 | no |
| 16 | ClientRootFinalV01 | `client_root_final:001` | `root:client_os_001` | 3 | yes — ClientRoot |
| 17 | AirlineRootFinalV01 | `airline_root_final:001` | `root:mock_airline_al` | 6 | yes — AirlineRoot |
| 18 | BankRootFinalV01 | `bank_root_final:001` | `root:mock_bank_a` | 1 | yes — BankRoot |

Every dependency points to an earlier accepted row. No missing, forward, or
self-dependency was accepted, and all 19 artifact IDs are unique.

## 9. The Crypto Seal

At generation time, the accepted package contained:

| Crypto surface | Count or status |
| --- | --- |
| Exact source files | 9 |
| Critical files | 11 |
| Manifest files | 1 |
| Stored Verification files | 1 |
| Stored Verification status | `SELF_CONSISTENT_UNANCHORED` |
| External anchor supplied | false |
| External anchor verified | false |
| Anchored PASS claimed | false |
| Signature mode | `UNSIGNED_PLACEHOLDER` |
| Signature verified | false |

This was the first verification moment. The package was internally
self-consistent, but no external expected Manifest Core hash had yet been
supplied. The stored Verification remained unchanged after anchor publication
and Replay.

The Crypto Seal binds the declared source bytes, 19 artifact hashes, ordered
hash chain, package hash, and Manifest Core. It proves declared byte integrity
and ordered continuity. It does not prove semantic truth, business truth,
signer identity, or permission.

## 10. The Committed External Anchor

The external Anchor was derived only after the recovery package passed its
owner-terminal gate. It was then committed at `a701743`, making the expected
Manifest Core hash an external repository trust input for the later Replay.

| Anchored identity | Exact value |
| --- | --- |
| Manifest Core hash | `4f6d9abe351e986abf147150a5dd4e76816430cf80bb718b50fa3536719a2472` |
| Source-package hash | `00662506fc3afe95d619a5003b572c9c1c9475e5ba26f7759b694115d092fdfa` |
| Chain-tail hash | `1f56be26e253f878e8d165d06a4da4430c1c4ec2e22daea1fc98c57b2f3b40fe` |
| Anchor SHA-256 | `54ee8e6dcceaa846ecc4bf8968b0ab26c9bcb849663a76c0cb9d01d564c694b0` |
| Replay Report SHA-256 | `7ceaa5400ef6b35fb1e39f2bdc739a68cb9bb4373d82e7586feee901ef414b57` |

This produced the second verification moment:

- The committed expected Manifest Core hash was supplied.
- The external Anchor was supplied and verified.
- Fresh verification status was `PASS`.
- The stored package Verification remained
  `SELF_CONSISTENT_UNANCHORED`.
- Signature mode remained `UNSIGNED_PLACEHOLDER`.
- `signature_verified` remained false.

The publication field `replay_allowed: false` records the historical
publication-time state. It was not treated as a mutable runtime permission
bit after the Anchor was committed.

The committed hash Anchor is not signer authentication, PKI, or
non-repudiation.

## 11. The Anchored Replay

The existing explicit Replay runner read one package, one committed external
Anchor, and one external output path. It reconstructed the trace and returned
an exact immutable PASS Report.

| Replay measure | Result |
| --- | --- |
| Replay status | `PASS` |
| Replay ID | `airline_sealed_trace_replay_v01:tri_airline_purchase:PAR-LIM:2026-08-12:client_001:4f6d9abe351e986abf147150a5dd4e76816430cf80bb718b50fa3536719a2472` |
| Timeline rows | 19 |
| Source files | 9 |
| Critical files | 11 |
| Ledger geometry | 19 / 29 / 3 |
| Ledger audit count | 1 |
| Fresh anchored verification count | 1 |
| Post-Replay package observations | 1 |

All public integrity and continuity flags were true, including Ledger,
Manifest, artifact-hash, chain-order, dependency-graph, Root-ownership,
authority/evidence, packet/receipt lineage, identity, source-reference, secret,
source-byte, critical-package-byte, and timeline checks.

The zero boundaries were exact:

| Replay boundary | Count |
| --- | ---: |
| Transaction reruns | 0 |
| Semantic reruns | 0 |
| Corridor reruns | 0 |
| Ledger recollections | 0 |
| Crypto recollections | 0 |
| Provider calls | 0 |
| Network calls | 0 |
| Gemini calls | 0 |
| Created authority | 0 |
| Created permission | 0 |
| Created actions | 0 |
| Created packets | 0 |
| Created receipts | 0 |
| Created FinalOutputs | 0 |
| Real-world effects | 0 |

The one post-Replay package snapshot callback was a local read-only observer.
It was not an LLM, provider, or network call.

## 12. The First Fail-Closed Run and the Accepted Recovery

The first official all-real package completed twelve real Gemini calls but was
rejected by a Ledger compatibility false positive. A valid typed canonical
reviewer response identity contained the word `response`, and the earlier
Ledger predicate classified that identifier too broadly as raw-response
evidence.

The primary failure reason was
`raw_prompt_response_not_auxiliary_only`. The derivative stored-status reason
was `ledger_stored_validation_status_mismatch`.

The repository handled the failure explicitly:

- No Anchor was published from the failed package.
- No Replay was run from the failed package.
- The failed package remained unchanged historical evidence.
- The package was not repaired or promoted in place.
- The compatibility defect was fixed in commit `38ad0b0`.
- Focused validation completed with 411 PASS.
- Closed-chain compatibility validation completed with 1230 PASS.
- A distinct recovery package was generated under the approved recovery plan.
- The recovery package passed generation, Ledger, Crypto, Anchor, and Replay
  validation.

This history demonstrates fail-closed discipline. It is part of the evidence,
not a hidden or erased attempt.

## 13. What This Demonstration Proves

This proof-level demonstration establishes that:

- Twelve real Gemini actors can contribute bounded semantic evidence to one
  fixed Airline scenario.
- Local validators can accept safe semantic meaning while rejecting provider
  claims to truth, authority, permission, or effects.
- ClientRoot, AirlineRoot, and BankRoot retain distinct decision boundaries.
- A deterministic five-phase Corridor can consume accepted evidence once.
- The resulting transaction trace can be represented as a 19-entry,
  29-edge, three-Root-final Ledger.
- Nine exact source files can be sealed into an eleven-file critical package
  surface.
- A separately committed external hash can anchor a fresh verification.
- The accepted trace can be reconstructed into the same 19-row order without
  rerunning semantics or effects.
- The package, stored Verification, Anchor, and Replay evidence remain
  independently auditable.
- A compatibility failure can stop promotion until the contract defect is
  repaired and a distinct recovery package passes.

## 14. What This Demonstration Does Not Prove

This demonstration is:

- not a real ticket;
- not a real booking;
- not a real payment;
- not a real airline, bank, or GDS integration;
- not production;
- not legal completion of a transaction;
- Gemini output is not truth;
- Gemini output is not authority;
- Crypto validity is not semantic truth or business truth;
- not signer authentication;
- not PKI;
- not non-repudiation;
- not trusted timestamping;
- no Root Attestation;
- Replay is not effect authorization.

`signature_verified` remains false. Root Attestation remains a deferred future
strengthening profile and is not required for this Base Replay proof.

Evidence is not permission. Replay verification is not effect authorization.

## 15. Evidence Map

| Claim | Observed value | Primary evidence | Field or section | Commit or hash |
| --- | --- | --- | --- | --- |
| Real Gemini calls | 12 | `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/summary.json` | `counter_table.gemini_called_count` | Generation commit `3301ce3` |
| Actor validations | 12 PASS / 0 FAIL | Accepted package `*_validation.json` files | `validation_status`, `accepted` | Generation commit `3301ce3` |
| Offer selected | `offer:mock_airline_al:PAR-LIM:001` | `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/semantic_to_contract_bridge.json` | Client/Airline/hold/Corridor offer fields | Generation commit `3301ce3` |
| BSEP projections | 4 PASS | `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/tri_party_airline_bsep_side_projections.json` | Four projection validation statuses | Generation commit `3301ce3` |
| Corridor | PASS, count 1 | `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/integrated_deterministic_airline_summary.json` | `corridor_final_status`, `corridor_execution_count` | Generation commit `3301ce3` |
| Ledger geometry | 19 / 29 / 3 | `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_transaction_artifact_ledger.json` | Entry, edge, Root-final counts | Ledger byte hash `ff31c776bf0ff43cd478e4ae94ba0a7b63a6d2f6de295d7ac13915d739722e61` |
| Crypto geometry | 9 / 11 | `docs/audit_reports/auditor_airline_all_real_full_stack_v01_generation_anchor_publication.log` | `[CRYPTO GENERATION]` | Commit `a701743` |
| Stored verification | `SELF_CONSISTENT_UNANCHORED` | `.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1/airline_crypto_artifact_seal_verification_v01.json` | `verification_status` | Stored file hash `ab17dcd2219a8366d1d06753384a06655b8725fdc25b1e9b50a7f86b618a9435` |
| Fresh verification | Anchored PASS | `docs/airline_all_real_full_stack_replay_report_v01.json` | `fresh_anchored_verification_status`, anchor flags | Replay Report hash `7ceaa5400ef6b35fb1e39f2bdc739a68cb9bb4373d82e7586feee901ef414b57` |
| Replay timeline | 19 rows | `docs/airline_all_real_full_stack_replay_report_v01.json` | `reconstructed_timeline` | Commit `ec50c1f` audit basis |
| Replay Gemini calls | 0 | `docs/airline_all_real_full_stack_replay_report_v01.json` | `gemini_call_count` | Replay Report hash `7ceaa5400ef6b35fb1e39f2bdc739a68cb9bb4373d82e7586feee901ef414b57` |
| Real-world effects | 0 | `docs/airline_all_real_full_stack_replay_report_v01.json` | `real_world_effects_count` | Replay Report hash `7ceaa5400ef6b35fb1e39f2bdc739a68cb9bb4373d82e7586feee901ef414b57` |
| Package unchanged | true | `docs/audit_reports/auditor_airline_all_real_full_stack_v01_anchored_replay.log` | `[INTEGRITY]`, `[HASHES]` | Commit `ec50c1f` |
| External Anchor | Committed and verified | `docs/airline_all_real_full_stack_crypto_anchor_v01.json` | `expected_manifest_core_hash` | Commit `a701743`; SHA-256 `54ee8e6dcceaa846ecc4bf8968b0ab26c9bcb849663a76c0cb9d01d564c694b0` |
| Historical failure evidence | Preserved, not promoted | `docs/audit_reports/auditor_airline_all_real_full_stack_v01_anchored_replay.log` | `[PRIOR FAIL-CLOSED HISTORY]` | Commit `ec50c1f` |

## 16. Next Step: Evidence Showcase

The proposed presentation thesis is:

> Hedgehog OS separates LLM reasoning from authority, then preserves the accepted decision path as a deterministic, cryptographically anchored, replayable evidence chain.

The next task is:

**Hedgehog OS Airline All-Real Evidence Showcase v0.1**

No presentation artifact is created in this task.
