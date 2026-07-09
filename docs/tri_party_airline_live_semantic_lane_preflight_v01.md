# Hedgehog OS - Tri-Party Airline Live Semantic Lane v0.1 Preflight

document_id: tri_party_airline_live_semantic_lane_preflight_v01
document_status: PREFLIGHT
observed_base_head: b6786c9
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
real_booking_created: false
real_world_effects_count: 0
production_ready_claimed: false
public_auditor_ready_claimed: false

Observed repository state before this preflight:

- `git status --short --untracked-files=all` returned a clean worktree.
- `git --no-pager log --oneline --max-count=15` showed latest commit
  `b6786c9 Add integrated trace to Airline tri-party mock E2E`.
- `git rev-parse --short HEAD` returned `b6786c9`.

Accepted deterministic basis:

- `docs/tri_party_airline_ticket_purchase_mock_e2e_preflight_v01.md`
- `demo/run_tri_party_airline_ticket_purchase_mock_e2e_v01.py`
- `tests/test_tri_party_airline_ticket_purchase_mock_e2e_v01_runner.py`

Closed deterministic slices:

- Slice B: inline tri-party skeleton.
- Slice C: AirlineRoot Offer Hold Sandbox.
- Slice D: BankRoot Payment Authorization Sandbox.
- Slice E: ClientRoot Purchase Orchestration.
- Slice F: AirlineRoot Ticket Issue Mock Corridor.
- Slice G: Integrated Tri-Party Transaction Trace.

## 1. Purpose

Define the live semantic overlay over the deterministic Airline tri-party mock
E2E. The future live lane must show that real LLM actors do meaningful
semantic work across ClientRoot, AirlineRoot, BankRoot, and cross-root evidence
consistency while preserving:

- one `transaction_id`;
- three Root boundaries;
- evidence-only receipts;
- sealed refs;
- no raw secrets;
- no real APIs;
- no actual payment;
- no actual ticket issuance;
- no actual booking;
- no authority transfer.

This document is planning only. It does not implement runtime, tests, live
provider calls, connector calls, payment, ticketing, booking, or audit output.

## 2. BSEP / Bounded Semantic Membrane

The Airline live semantic lane must preserve the BSEP geometry from Full WOW
v1.2.

Correct chain:

```text
Deterministic tri-party transaction trace
-> tri_party_airline_orchestrator_llm
-> runtime validates orchestrator semantic proposal
-> runtime creates tri_party_airline_bsep_packet
-> runtime validates tri_party_airline_bsep_packet
-> runtime creates side-specific BSEP projections:
   - client_bsep_projection
   - airline_bsep_projection
   - bank_bsep_projection
   - cross_root_bsep_projection
-> tri_party_airline_semantic_architect_llm receives BSEP-derived bounded context
-> side semantic actors receive BSEP-derived bounded context
-> vertical fractal child cells receive bounded parent-derived context only
-> runtime canonicalizes all accepted semantics
-> Root boundaries remain side-specific
```

BSEP rules:

- BSEP is not truth.
- BSEP is not authority.
- BSEP is not permission.
- BSEP is not FinalOutput.
- BSEP does not create packet.
- BSEP does not create receipt.
- BSEP does not create payment.
- BSEP does not create ticket.
- BSEP does not create booking.
- BSEP carries bounded context only.
- BSEP must not contain raw passport, raw card, raw IBAN, raw payment token,
  raw private profile, raw provider text, or raw response dumps.

Required BSEP artifacts for future implementation:

- `tri_party_airline_bsep_packet.json`
- `tri_party_airline_bsep_validation.json`
- `tri_party_airline_bsep_side_projections.json`

Each side projection must include:

- projection_id
- transaction_id
- side
- bounded_context_summary
- allowed_refs
- forbidden_raw_fields
- forbidden_authority_claims
- raw_secrets_included: false
- raw_provider_text_included: false
- validation_status

## 3. Live Semantic Actor Topology

Required live semantic actor count: 12.

### 1. tri_party_airline_orchestrator_llm

side: transaction

Semantic work:

- interpret the whole tri-party transaction goal;
- identify ClientRoot / AirlineRoot / BankRoot responsibilities;
- identify required evidence routes;
- identify happy-path mock purchase conditions;
- propose bounded semantic route for BSEP creation;
- not create ticket/payment/booking/packet/receipt/authority.

### 2. tri_party_airline_semantic_architect_llm

side: transaction

Semantic work:

- receive BSEP-derived bounded context;
- propose semantic actor topology and validation obligations;
- explain side-specific bounded contexts;
- explain horizontal and vertical semantic actor structure;
- not output runtime PlanGraph objects;
- not create authority, packet, receipt, payment, ticket, booking, or
  FinalOutput.

### 3. client_purchase_orchestrator_llm

side: client

Semantic work:

- interpret travel intent;
- explain budget/preferences;
- compare selected offer with client constraints;
- identify what evidence ClientRoot may send to AirlineRoot and BankRoot;
- not create payment authorization;
- not issue ticket.

### 4. client_profile_privacy_reviewer_llm

side: client

Semantic work:

- review passenger sealed refs;
- review payment profile sealed refs;
- explain why raw passport/card/IBAN/payment token stay sealed;
- not expose raw secrets;
- not create authority.

### 5. airline_offer_policy_reviewer_llm

side: airline

Semantic work:

- interpret mock inventory/fare/baggage/TTL/route constraints;
- evaluate Offer A/B/C;
- explain selected offer and rejected/downgraded offers;
- not create payment authorization;
- not issue an actual ticket.

### 6. airline_fare_rules_vertical_cell_llm

side: airline
vertical_fractal_cell: true

Semantic work:

- analyze fare basis;
- analyze refund/change restrictions;
- analyze TTL pressure;
- analyze price-vs-flexibility tradeoff;
- return advisory child ResultProposal to AirlineRoot.

### 7. airline_seat_baggage_vertical_cell_llm

side: airline
vertical_fractal_cell: true

Semantic work:

- analyze checked baggage;
- analyze seat choice / seat fee / cabin constraints;
- verify selected seat remains mock-only;
- return advisory child ResultProposal to AirlineRoot.

### 8. airline_ticketing_policy_reviewer_llm

side: airline

Semantic work:

- interpret when OfferHoldReceipt + PaymentAuthorizationReceipt +
  ClientPurchaseApprovalEvidence are sufficient for mock ticket evidence;
- distinguish mock ticket evidence from an actual ticket;
- not call GDS/API;
- not create an actual ticket.

### 9. bank_payment_policy_reviewer_llm

side: bank

Semantic work:

- interpret payment intent, consent, amount/currency, merchant, debtor slot,
  and sealed payment token ref;
- explain authorization vs execution;
- not execute payment;
- not issue ticket.

### 10. bank_idempotency_risk_vertical_cell_llm

side: bank
vertical_fractal_cell: true

Semantic work:

- analyze idempotency key;
- analyze duplicate payment risk;
- analyze expiry/TTL;
- analyze amount/merchant mismatch pressure;
- return advisory child ResultProposal to BankRoot.

### 11. bank_payment_status_explainer_llm

side: bank

Semantic work:

- explain payment authorization vs settlement vs receipt evidence;
- explain PaymentStatusReceipt as evidence-only;
- not create settlement;
- not create ticket permission.

### 12. tri_party_evidence_consistency_reviewer_llm

side: cross_root_advisory

Semantic work:

- check all artifacts share the same `transaction_id`;
- check evidence routing is coherent;
- check no Root gains foreign authority;
- check payment receipt does not create ticket;
- check mock ticket receipt does not create payment;
- check no raw secrets are present;
- advisory only; not a fourth Root.

## 4. Richer Scenario

Deterministic base transaction:

```text
transaction_id: tri_airline_purchase:PAR-LIM:2026-08-12:client_001
```

Travel intent:

- origin: PAR
- destination: LIM
- depart_date: 2026-08-12
- return_date: 2026-08-21
- passenger_count: 1
- cabin: economy
- budget: 840 EUR
- baggage_needed: true
- seat_preference: window_or_aisle
- avoid_overnight_layover: true
- prefer_changeable_ticket: true

Mock offers:

Offer A:

- offer_id: offer:mock_airline_al:PAR-LIM:001
- price_amount: 782
- currency: EUR
- baggage_included: true
- seat_option: 18A window included
- changeable: true
- refundable: false
- offer_ttl_seconds: 900
- status: selected

Offer B:

- offer_id: offer:mock_airline_al:PAR-LIM:002
- price_amount: 806
- currency: EUR
- baggage_included: true
- seat_option: 12C extra-legroom aisle
- seat_fee_included_in_total: true
- changeable: true
- refundable: false
- offer_ttl_seconds: 600
- status: viable_but_less_preferred

Offer C:

- offer_id: offer:mock_airline_al:PAR-LIM:003
- price_amount: 741
- currency: EUR
- baggage_included: false
- overnight_layover: true
- change_penalty: high
- offer_ttl_seconds: 900
- status: downgraded

## 5. Strict Vertical Fractal Definition

The live lane may execute semantic vertical cells as LLM actors:

- `airline_fare_rules_vertical_cell_llm`
- `airline_seat_baggage_vertical_cell_llm`
- `bank_idempotency_risk_vertical_cell_llm`

They are child semantic cells:

- they may analyze bounded context;
- they may return advisory child ResultProposal;
- they cannot create authority;
- they cannot create packets;
- they cannot create receipts;
- they cannot execute payment;
- they cannot issue ticket;
- they cannot call APIs;

Strict vertical fractal definition:

A vertical fractal cell is not just another parallel actor. A vertical child
actor may start only after its parent actor validates.

Required vertical dependency rules:

```text
child has parent_actor_id.
child has parent_validation_status: PASS.
child_started_after_parent_validation: true.
child_received_parent_canonical_summary: true.
child_received_parent_raw_response: false.
child_received_sibling_raw_output: false.
child_received_unbounded_context: false.
child_result_returns_to_parent_or_root_review: true.
child_creates_authority: false.
child_creates_packet: false.
child_creates_receipt: false.
child_creates_payment: false.
child_creates_ticket: false.
child_creates_booking: false.
real_world_effects_count: 0.
```

Required vertical chains:

```text
airline_offer_policy_reviewer_llm
  -> airline_fare_rules_vertical_cell_llm

airline_offer_policy_reviewer_llm
  -> airline_seat_baggage_vertical_cell_llm

bank_payment_policy_reviewer_llm
  -> bank_idempotency_risk_vertical_cell_llm
```

Future tests must prove:

- child does not start if parent validation fails;
- child prompt contains parent canonical summary;
- child prompt does not contain parent raw response;
- child prompt does not contain sibling raw output;
- child output is advisory only;
- child result returns upward;
- child cannot create authority/action/ticket/payment/receipt/booking/effects.

## 6. Artifact Transparency

For each of the 12 actors, the later implementation must write:

- `<actor_id>_prompt.txt`
- `<actor_id>_raw_response.txt`
- `<actor_id>_extracted_json_candidate.json`
- `<actor_id>_validation.json`
- `<actor_id>_canonical_summary.json`

Required transparency report fields for each actor:

- actor_id
- side
- prompt_artifact
- raw_response_artifact
- extracted_json_artifact
- validation_artifact
- canonical_summary_artifact
- input_context_summary
- output_semantic_summary
- validation_status
- what_runtime_used
- what_runtime_rejected
- authority_created: false
- action_permission_created: false
- packet_created: false
- receipt_created: false
- real_payment_executed: false
- real_ticket_issued: false
- real_booking_created: false
- real_world_effects_count: 0

Raw responses are stored as artifacts, not authority. The runtime may use only
validated canonical summaries.

## 7. Prompt Rules

Each prompt must include bounded context only:

- no raw passport;
- no raw card;
- no raw IBAN;
- no raw payment token;
- no raw private profile;
- no connector credentials;
- no API keys;
- no direct real API instructions;
- explicit JSON skeleton;
- provider output is advisory only;
- runtime canonicalizes;
- validators verify;
- Root decides;
- actor cannot create ActionCommitPacket, receipt, payment, ticket, booking,
  FinalOutput, or authority.

## 8. Runtime Processing Plan

For each actor:

1. Build bounded prompt.
2. Call provider only when live env is enabled.
3. Save prompt artifact.
4. Save raw response artifact.
5. Extract JSON candidate.
6. Validate semantic contract.
7. Canonicalize accepted fields.
8. Add canonical summary to live semantic report.
9. Feed only canonical accepted summary into side-specific Root review.
10. Preserve raw response as artifact only, not authority.

## 9. Test Strategy

Tests must not call Gemini/network. Tests must use fake providers.

Tests must verify:

- all 12 prompts are generated;
- all 12 fake responses are captured;
- all 12 extracted JSON candidates are captured;
- all 12 validations are captured;
- actor inputs contain bounded context;
- actor inputs do not contain raw secrets;
- actor outputs are advisory only;
- runtime records what it used and what it rejected;
- fake provider call count = 12;
- real provider call count = 0 in tests;
- provider/network/Gemini counters = 0 in tests;
- no packet/receipt/payment/ticket/booking/effects are created by actors;
- vertical child cells return to parent and do not create authority;
- cross-root reviewer is not a fourth Root.

Required future fake-provider tests:

- valid fake LLM responses produce PASS;
- malformed fake response fails closed;
- unsafe authority claim fails closed;
- missing required semantic fields fail closed;
- actor output claiming payment/ticket/booking/packet/receipt fails closed;
- fake provider raw response drives extraction and validation;
- tests do not ignore LLM output;
- tests are deterministic because fake provider is deterministic, not because
  runtime ignores provider output;
- Orchestrator valid response is required before BSEP creation;
- BSEP validation is required before Architect call;
- Architect valid response is required before side actor calls;
- vertical child actor is not called if parent validation fails.

## 10. Real Run Plan

operator-gated real Gemini run is required to close the live checkpoint after
fake-provider PASS and explicit operator action.

Tests must not call the live provider. Implementation can pass CI with fake
provider only. Checkpoint closure requires a separate operator-run real Gemini
terminal pass with:

- provider_mode: real_provider
- model: gemini-2.5-flash
- semantic_actor_call_count: 12
- real_provider_call_count: 12
- network_used_count: 12
- gemini_called_count: 12
- artifact capture enabled
- secret scan enabled
- raw responses saved as artifacts
- canonical summaries rendered
- no actual payment/ticket/booking/API/effects

## 11. Terminal Visibility

The live runner must show:

```text
[TRI-PARTY AIRLINE LIVE SEMANTIC LANE]
[BSEP MEMBRANE]
[SIDE-SPECIFIC BSEP PROJECTIONS]
[SEMANTIC ACTOR CALLS]
[TRANSACTION ORCHESTRATOR]
[SEMANTIC ARCHITECT]
[CLIENT SIDE LLM ACTORS]
[AIRLINE SIDE LLM ACTORS]
[AIRLINE VERTICAL FRACTAL CELLS]
[BANK SIDE LLM ACTORS]
[BANK VERTICAL FRACTAL CELLS]
[CROSS-ROOT CONSISTENCY REVIEWER]
[STRICT VERTICAL FRACTAL DEPENDENCIES]
[WHAT EACH LLM RECEIVED]
[WHAT EACH LLM RETURNED]
[WHAT RUNTIME USED]
[WHAT RUNTIME REJECTED]
[ROOT BOUNDARIES]
[COUNTER TABLE]
[ARTIFACTS]
[FINAL STATUS]
```

Raw response terminal output:

- default: do not print full raw responses;
- print raw response artifact path and canonical summary;
- allow raw response terminal dump only with explicit env
  `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ALLOW_RAW_RESPONSE_OUTPUT=1`;
- even if raw output is allowed, secret scan must pass.

## 12. Required Counters

```text
semantic_actor_call_count: 12
tri_party_orchestrator_call_count: 1
tri_party_architect_call_count: 1
bsep_created_count: 1
bsep_validated_count: 1
bsep_side_projection_count: 4
transaction_semantic_actor_count: 2
client_semantic_actor_count: 2
airline_semantic_actor_count: 4
bank_semantic_actor_count: 3
cross_root_semantic_actor_count: 1
vertical_fractal_semantic_cell_count: 3
prompts_written_count: 12
raw_responses_written_count: 12
extracted_json_candidates_written_count: 12
validations_written_count: 12
canonical_summaries_written_count: 12
semantic_actor_validation_pass_count: 12
semantic_actor_validation_fail_count: 0
provider_output_used_as_truth_count: 0
provider_output_used_as_authority_count: 0
provider_output_created_packet_count: 0
provider_output_created_receipt_count: 0
provider_output_created_payment_count: 0
provider_output_created_ticket_count: 0
provider_output_created_booking_count: 0
cross_root_authority_transfer_count: 0
raw_passport_exposed_count: 0
raw_card_exposed_count: 0
raw_iban_exposed_count: 0
raw_payment_token_exposed_count: 0
real_airline_api_called_count: 0
real_bank_api_called_count: 0
real_gds_api_called_count: 0
real_payment_executed_count: 0
real_ticket_issued_count: 0
real_booking_created_count: 0
real_world_effects_count: 0
```

## 13. Future Implementation Files

Required future implementation files:

- `demo/run_tri_party_airline_live_semantic_lane_v01.py`
- `tests/test_tri_party_airline_live_semantic_lane_v01_runner.py`

Recommended later audit:

- `docs/audit_reports/auditor_tri_party_airline_live_semantic_lane_real_run_v01.log`

Recommended later human story:

- `demo/run_human_tri_party_airline_live_semantic_story_v01.py`
- `tests/test_human_tri_party_airline_live_semantic_story_v01_runner.py`

## 14. Non-Claims

- not production;
- not public auditor package;
- no runtime changes in this preflight;
- no tests changed in this preflight;
- no provider/network/Gemini call in this preflight;
- no secret access;
- no real airline API;
- no real bank API;
- no GDS/NDC/Open Banking call;
- no actual payment;
- no actual ticket issuance;
- no actual booking;
- no real-world effects.

## 15. Next Gate

After this preflight is accepted, the next step is live semantic lane
implementation with fake-provider tests:

- deterministic fake-provider implementation first;
- artifact transparency for all 12 actors;
- no live provider call in tests;
- operator-gated real Gemini run is required for checkpoint closure after
  fake-provider PASS and explicit operator action.
