# Hedgehog OS - Tri-Party Airline Ticket Purchase Mock E2E v0.1 Preflight

document_id: tri_party_airline_ticket_purchase_mock_e2e_preflight_v01
document_status: PREFLIGHT
observed_base_head: 6c77c91
planning_only: true
runtime_modified: false
tests_modified: false
provider_called: false
network_called: false
gemini_called: false
secrets_accessed: false
real_airline_api_called: false
real_bank_api_called: false
real_payment_executed: false
real_ticket_issued: false
real_travel_booking_created: false
real_world_effects_count: 0
production_ready_claimed: false
public_auditor_ready_claimed: false

Canonical title:

Hedgehog OS - Tri-Party Airline Ticket Purchase Mock E2E v0.1

Observed repository state before this preflight:

- `git status --short --untracked-files=all` returned a clean worktree.
- `git --no-pager log --oneline --max-count=15` showed latest commit
  `6c77c91 Document Non-Action Direct Reuse economics-ready checkpoint`.
- `git rev-parse --short HEAD` returned `6c77c91`.

Strategic source docs:

- `[ЁЖИК] [РУБЕЖ ПОСЛЕ ACTION CORRIDOR] [ДАЛЬШЕ]`
- `[AIRLINE TRI-PARTY SPEC] [ДЛЯ ПОМОЩНИКА]`
- `docs/non_action_direct_reuse_positive_control_preflight_v01.md`
- `docs/non_action_direct_reuse_positive_control_explainer_v01.md`

Closed basis:

- Full WOW v1.2 live action corridor integrated organism: PASS.
- Local DRS v0.2: PASS.
- AVF v0.2: PASS.
- ActionCommitPacket v0.2 / MockBankSandbox corridor: PASS.
- Non-Action Direct Reuse Positive Control v0.1: PASS.
- Reuse economics-ready checkpoint: PASS.

## 1. Purpose

Define the narrowest safe implementation path for one mock tri-party airline
ticket purchase transaction with:

- one transaction;
- three Root systems;
- three bounded views;
- one shared `transaction_id`;
- one shared artifact set;
- one shared transaction ledger;
- evidence crossing Root boundaries without authority transfer.

This is planning only. It is not runtime, tests, live Gemini, real booking,
real payment, real ticket, real travel readiness, production readiness, or a
public-auditor package.

## 2. One-Screen Summary

A Client Hedgehog OS, an Airline Hedgehog OS, and a Bank Hedgehog OS complete
one mock ticket-purchase transaction through sealed refs, Root-created scoped
packets, deterministic corridors, receipts, and a shared audit ledger. The
client sees a purchase, the airline sees offer/order/ticket fulfilment, and
the bank sees payment authorization. No raw card, raw passport, real payment,
real ticket, or authority leakage occurs.

## 3. Participants

### ClientRoot

ClientRoot:

- knows travel intent;
- knows passenger sealed refs;
- knows payment profile sealed ref;
- knows user approval;
- knows selected offer;
- does not expose raw passport;
- does not expose raw card;
- does not expose raw IBAN;
- does not issue ticket;
- does not authorize bank payment;
- produces client purchase approval evidence only.

### AirlineRoot

AirlineRoot:

- knows mock inventory;
- knows mock fares;
- knows mock seats;
- knows baggage rule;
- knows offer TTL;
- knows order creation rule;
- knows ticket issue rule;
- creates OfferResponse;
- creates OfferHoldReceipt;
- validates payment evidence against offer hold;
- creates OrderCreatedReceipt;
- creates MockTicketReceipt / mock PNR;
- does not charge card;
- does not authorize client payment;
- does not request raw passport;
- does not call real airline API.

### BankRoot

BankRoot:

- knows payment token ref;
- knows debtor slot;
- knows merchant/airline ref;
- knows amount/currency;
- knows idempotency;
- knows consent/payment order/status;
- creates PaymentIntent;
- creates PaymentConsent;
- creates PaymentAuthorizationReceipt;
- creates PaymentStatusReceipt;
- does not create ticket;
- does not call real bank API;
- does not execute real payment.

## 4. Core Invariants

- ClientRoot cannot issue ticket.
- AirlineRoot cannot authorize client payment.
- BankRoot cannot create airline ticket.
- PaymentAuthorizationReceipt is not ticket permission.
- MockTicketReceipt is not payment permission.
- Receipt from one Root is evidence for another Root, not authority over it.
- Each Root consumes evidence, not foreign authority.
- No Root becomes God over the others.
- Root boundaries remain side-specific.
- Sealed refs are not raw secrets.
- Old quote is not ticket permission.
- Old ticket receipt is not future ticket permission.
- Non-Action Direct Reuse may inform context only; it cannot buy ticket.

## 5. Transaction Identity

```text
transaction_id: tri_airline_purchase:PAR-LIM:2026-08-12:client_001
client_root_id: root:client_os_001
airline_root_id: root:mock_airline_al
bank_root_id: root:mock_bank_a
mock_only: true
real_world_effects_allowed: false
```

All artifacts must carry the same `transaction_id`. Do not create three
unrelated runs. All three views render the same transaction.

## 6. Top-Level Flow

1. ClientRoot receives travel intent.
2. ClientRoot asks AirlineRoot for offers.
3. AirlineRoot checks mock inventory/fare/baggage/TTL.
4. AirlineRoot returns OfferCandidates / OfferHold evidence.
5. ClientRoot selects offer and creates scoped approval evidence.
6. ClientRoot asks BankRoot for payment authorization.
7. BankRoot validates amount, merchant, idempotency, expiry, payment token ref.
8. BankRoot returns PaymentAuthorizationReceipt.
9. AirlineRoot validates payment evidence against OfferHold.
10. AirlineRoot creates Order / mock ticket / mock PNR.
11. ClientRoot receives ticket evidence.
12. ClientRoot RootFinal says: mock ticket issued, mock payment authorized, no
    raw secrets exposed, no real payment, no real airline API, receipts
    evidence only.

## 7. Geometry

This is not one flat chain.

Correct geometry:

```text
Root -> phase-loop -> Root -> phase-loop -> Root
```

Per side:

ClientRoot:

```text
intent -> route proposal -> selected offer -> purchase approval -> final user summary
```

AirlineRoot:

```text
offer request -> inventory/fare validation -> offer hold -> payment evidence validation -> mock order/ticket
```

BankRoot:

```text
payment request -> consent/authorization validation -> payment authorization receipt/status
```

## 8. Mock Protocol Objects To Plan

Client side:

- TravelIntentV01
- PassengerSealedRefsV01
- PaymentProfileSealedRefV01
- ClientOfferSelectionV01
- ClientPurchaseApprovalEvidenceV01
- ClientFinalTravelSummaryV01

Airline side:

- AirlineOfferRequestV01
- AirlineOfferCandidateV01
- AirlineOfferResponseV01
- AirlineOfferHoldCommitPacketV01
- AirlineOfferHoldReceiptV01
- AirlinePaymentEvidenceValidationV01
- AirlineTicketIssueCommitPacketV01
- AirlineOrderCreatedReceiptV01
- MockTicketReceiptV01
- MockPNRV01

Bank side:

- BankPaymentIntentV01
- BankPaymentConsentV01
- BankPaymentAuthorizationCommitPacketV01
- BankPaymentAuthorizationReceiptV01
- BankPaymentStatusReceiptV01

Shared:

- TriPartyAirlineTransactionEnvelopeV01
- TriPartyAirlineTransactionLedgerV01
- TriPartyAirlineArtifactRefV01
- TriPartyAirlineRootBoundaryReportV01
- TriPartyAirlineFinalSummaryV01

## 9. Scoped Packets

- AirlineOfferHoldCommitPacket is created only by AirlineRoot.
- BankPaymentAuthorizationCommitPacket is created only by BankRoot.
- AirlineTicketIssueCommitPacket is created only by AirlineRoot after
  validating OfferHoldReceipt, PaymentAuthorizationReceipt,
  ClientPurchaseApprovalEvidence, quote freshness, and slot completeness.

Scoped packet rules:

- ClientRoot cannot create AirlineOfferHoldCommitPacket.
- ClientRoot cannot create BankPaymentAuthorizationCommitPacket.
- BankRoot cannot create AirlineTicketIssueCommitPacket.
- AirlineRoot cannot create BankPaymentAuthorizationCommitPacket.
- No scoped packet widens another Root boundary.

## 10. Receipt Boundaries

Receipts evidence only:

- OfferHoldReceipt is evidence only.
- PaymentAuthorizationReceipt is evidence only.
- PaymentStatusReceipt is evidence only.
- OrderCreatedReceipt is evidence only.
- MockTicketReceipt is evidence only.
- MockTicketReceipt is not real ticket.
- PaymentAuthorizationReceipt is not ticket permission.
- OfferHoldReceipt is not payment permission.
- ClientPurchaseApprovalEvidence is evidence for BankRoot and AirlineRoot, not
  their authority.

## 11. Privacy And Sealed Slots

Privacy/sealed-slot boundaries:

- raw passport not exposed;
- raw card not exposed;
- raw IBAN not exposed;
- raw payment token not exposed;
- passenger sealed ref only;
- payment profile sealed ref only;
- vault refs are not LLM context;
- no raw private profile in provider context;
- no raw secrets in artifacts.

## 12. Non-Action Direct Reuse In Airline

Non-Action Direct Reuse can help Airline remember:

- old route preference;
- old quote;
- old failed route;
- old payment token ref;
- old ticket receipt;
- traveler refs.

But:

- old quote is not ticket permission;
- old payment receipt is not current payment authorization;
- old ticket receipt is not future ticket permission;
- old traveler refs cannot expose raw passport;
- DRS hit is context only unless RootShortcutGate allows informational reuse;
- action-like Airline requests must route to Root/corridor, not direct reuse.

## 13. DRS / AVF Positioning

- DRS can provide context, lineage, freshness, and stale warnings.
- DRS is not truth.
- DRS is not authority.
- DRS is not permission.
- AVF can hard-mask unsafe candidates.
- AVF can rank safe directions.
- AVF score is not authority.
- Top-ranked candidate is not ticket permission.
- Root remains final authority for each side.

## 14. Future Implementation Slices

Slice A - docs-only preflight.

- Current task.

Slice B - deterministic tri-party skeleton with inline fixtures.

Recommended files:

- `demo/run_tri_party_airline_ticket_purchase_mock_e2e_v01.py`
- `tests/test_tri_party_airline_ticket_purchase_mock_e2e_v01_runner.py`

Scope:

- inline deterministic fixtures;
- TravelIntent;
- TriPartyTransactionEnvelope;
- ClientRoot fixture;
- AirlineRoot fixture;
- BankRoot fixture;
- OfferCandidate;
- OfferHoldReceipt;
- PaymentAuthorizationReceipt;
- MockTicketReceipt;
- shared summary;
- no Gemini;
- no real APIs;
- no core extraction yet.

Optional later extraction only after deterministic v0.1 is stable:

- `hedgehog/tri_party_airline_ticketing.py`
- `tests/test_tri_party_airline_ticketing_core.py`

For v0.1, prefer inline deterministic fixtures. Do not modify core unless
necessary. Do not add generic RootScopedContractEnvelope runtime in this
layer.

Slice C - deterministic AirlineRoot Offer/Order sandbox.

Scope:

- mock inventory/fare/baggage/TTL;
- OfferCandidates;
- OfferHoldCommitPacket;
- OfferHoldReceipt;
- no payment;
- no ticket.

Slice D - deterministic BankRoot payment authorization sandbox.

Scope:

- PaymentIntent;
- PaymentConsent;
- BankPaymentAuthorizationCommitPacket;
- PaymentAuthorizationReceipt;
- PaymentStatusReceipt;
- no real payment;
- no ticket.

Slice E - deterministic ClientRoot purchase orchestration.

Scope:

- travel intent;
- sealed passenger/payment refs;
- offer selection;
- client purchase approval evidence;
- cross-root evidence routing;
- no raw secrets.

Slice F - Airline ticket issue mock corridor.

Scope:

- AirlineRoot validates OfferHoldReceipt, PaymentAuthorizationReceipt, and
  ClientPurchaseApprovalEvidence;
- AirlineTicketIssueCommitPacket;
- mock OrderCreatedReceipt;
- MockTicketReceipt / mock PNR;
- no real ticket.

Slice G - integrated tri-party transaction trace.

Scope:

- one `transaction_id`;
- one shared ledger;
- all three views;
- all receipts evidence-only;
- no real effects.

Slice H - three human renderers.

- client view;
- airline view;
- bank view.

Slice I - optional live semantic lane after deterministic PASS.

Possible real Gemini semantic actor roles:

- client_purchase_orchestrator_llm;
- airline_offer_policy_reviewer_llm;
- bank_payment_policy_reviewer_llm.

All advisory only. No semantic actor creates packet, receipt, payment, ticket,
or FinalOutput.

## 15. Required Negative Tests To Propose

- client_root_cannot_issue_ticket
- airline_root_cannot_authorize_payment
- bank_root_cannot_create_ticket
- payment_receipt_not_ticket_permission
- ticket_receipt_not_payment_permission
- old_quote_not_ticket_permission
- old_ticket_receipt_not_future_ticket_permission
- offer_hold_receipt_not_payment_permission
- client_purchase_approval_not_bank_authority
- client_purchase_approval_not_airline_authority
- raw_passport_not_exposed
- raw_card_not_exposed
- raw_payment_token_not_exposed
- real_airline_api_forbidden
- real_bank_api_forbidden
- real_payment_forbidden
- real_ticket_forbidden
- transaction_id_required_on_all_artifacts
- three_unrelated_runs_rejected
- receipt_authority_leakage_rejected
- root_boundary_cross_authority_rejected
- drs_hit_not_ticket_permission
- avf_top_rank_not_ticket_permission
- non_action_reuse_cannot_buy_ticket
- provider_output_not_authority
- no_real_world_effects

## 16. Expected Final Deterministic Counters

- tri_party_airline_transaction_count: 1
- client_root_count: 1
- airline_root_count: 1
- bank_root_count: 1
- shared_transaction_id_count: 1
- offer_candidates_created_count: >=1
- offer_hold_receipt_created_count: 1
- client_purchase_approval_evidence_created_count: 1
- bank_payment_intent_created_count: 1
- bank_payment_consent_created_count: 1
- bank_payment_authorization_receipt_created_count: 1
- airline_order_created_receipt_count: 1
- mock_ticket_receipt_created_count: 1
- mock_pnr_created_count: 1
- client_root_issued_ticket_count: 0
- airline_root_authorized_payment_count: 0
- bank_root_created_ticket_count: 0
- payment_receipt_created_ticket_count: 0
- ticket_receipt_created_payment_count: 0
- raw_passport_exposed_count: 0
- raw_card_exposed_count: 0
- raw_iban_exposed_count: 0
- raw_payment_token_exposed_count: 0
- real_airline_api_called_count: 0
- real_bank_api_called_count: 0
- real_payment_executed_count: 0
- real_ticket_issued_count: 0
- real_world_effects_count: 0
- provider_called_count: 0 for deterministic slices
- network_used_count: 0 for deterministic slices
- gemini_called_count: 0 for deterministic slices

## 17. Non-Goals

- no real GDS;
- no real NDC schemas;
- no real ONE Order schemas;
- no real Open Banking schemas;
- no real card acquiring;
- no real settlement;
- no BSP;
- no real passport validation;
- no real airline inventory pricing;
- no real seat map complexity;
- no production connectors;
- no real booking;
- no real payment;
- no real ticket;
- no production/public-auditor claim;
- no Bank B Hedgehog-native supplier-payment roadmap implementation;
- no NeedleFactory / Middle Factory;
- no Marennya / UP.

## 18. Next Gate

After this preflight is accepted:

- Airline tri-party deterministic Slice B local skeleton / inline fixtures.

Do not start runtime, tests, live Gemini, real APIs, real payment, real ticket,
Bank B Hedgehog-native supplier-payment corridor, NeedleFactory, Middle
Factory, Marennya, or UP from this preflight.
