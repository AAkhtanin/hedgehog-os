document_id: airline_semantic_to_contract_causal_binding_preflight_v01
document_status: PREFLIGHT
observed_base_head: 23d3787
planning_only: true
runtime_modified: false
tests_modified: false
provider_called: false
network_called: false
gemini_called: false
secrets_accessed: false
semantic_to_contract_causal_binding_implemented: false
real_payment_executed: false
real_ticket_issued: false
real_booking_created: false
real_world_effects_count: 0
production_ready_claimed: false
public_auditor_ready_claimed: false

# Hedgehog OS — Airline Semantic-to-Contract Causal Binding v0.1 Preflight

## Purpose

This preflight defines the missing causal bridge:

```text
validated LLM semantics
-> runtime canonical semantic evidence
-> side-specific Root decision
-> Root-created scoped Airline contract artifacts
-> existing deterministic Ticket/Purchase Corridor
```

This is planning only. It does not implement runtime, tests, Ledger, Crypto,
Replay, provider calls, payment, ticket issue, booking, or any real-world
effect.

## Current Proven Facts

Semantic side already proved:

- real_provider.
- model: gemini-2.5-flash.
- 12 semantic actors.
- BSEP created and validated before Architect.
- four BSEP projections.
- horizontal actors.
- strict vertical parent-child actors.
- prompt, raw response, extracted JSON, validation, and canonical artifacts.
- runtime-owned what_runtime_used / what_runtime_rejected.
- provider output not truth.
- provider output not authority.
- no real effects.

Contract side already proved:

- one Airline transaction_id.
- ClientRoot / AirlineRoot / BankRoot.
- Airline domain contracts.
- five Root-centered corridor phases.
- exact source-to-contract binding matrix.
- evidence-only receipts.
- no cross-Root authority transfer.
- deterministic corridor PASS.
- no real effects.

Current missing proof:

- the real semantic output has not yet been proven to causally select the
  offer/contract facts used by the deterministic corridor.
- current deterministic fixtures can still select a prewritten offer.
- final integrated Corridor audit must remain blocked until causal binding PASS.

## Core Causal Formula

AirlineRoot publishes bounded authoritative offer candidates.

LLM actors analyze bounded semantic meaning and may recommend only an existing
offer identifier.

Runtime extracts, validates, and canonicalizes the recommendation.

ClientRoot accepts or rejects the semantic recommendation.

AirlineRoot resolves all authoritative offer facts from its own candidate set.

Root-created scoped contract artifacts reference the accepted selected offer.

Human approval remains separate scoped evidence.

The deterministic corridor applies fixed safety and contract invariants.

Provider output never creates packet, receipt, permission, payment, ticket,
booking, or FinalOutput.

Short formula:

```text
LLM chooses meaning.
Runtime validates meaning.
Root chooses authority.
Domain contracts bind the Root decision.
Corridor enforces invariant execution geometry.
```

## Hard-Coded Safety Vs Semantic Choice

Semantic choice controlled by validated LLM evidence:

- recommended offer_id.
- ranking among hard-valid candidates.
- client preference interpretation.
- fare/seat/baggage tradeoff explanation.
- uncertainty.
- semantic rejection reasons.
- whether more Root review is needed.

Fixed deterministic safety:

- candidate must exist.
- transaction_id must match.
- candidate set reference must match.
- amount comes from AirlineRoot offer facts.
- currency comes from AirlineRoot offer facts.
- route comes from AirlineRoot offer facts.
- passenger_ref comes from sealed Root-owned context.
- TTL comes from AirlineRoot offer facts.
- idempotency comes from runtime/Root contract.
- Root ownership is fixed.
- expired offer fails closed.
- hard constraint violation fails closed.
- receipt remains evidence only.
- no post-Root reasoning restart.
- no real effects.

The LLM may choose a candidate reference. The LLM may not manufacture or
override authoritative candidate facts.

## Bounded Offer Set

Use the already documented mock offer set as the causal proof basis.

Offer A:

- offer_id: offer:mock_airline_al:PAR-LIM:001.
- 782 EUR.
- baggage included.
- window seat.
- changeable.
- hard-valid.

Offer B:

- offer_id: offer:mock_airline_al:PAR-LIM:002.
- 806 EUR.
- baggage included.
- extra-legroom aisle.
- changeable.
- hard-valid.

Offer C:

- offer_id: offer:mock_airline_al:PAR-LIM:003.
- 741 EUR.
- baggage absent.
- overnight layover.
- high change penalty.
- hard-invalid for the current declared constraints.

Required distinction:

- A and B permit genuine semantic tradeoff.
- C proves deterministic hard constraints remain stronger than LLM preference.
- No offer may carry raw passport/card/IBAN/payment-token data.

## Required Future Typed Artifacts

### ClientRootTravelConstraintSetV01

Created/owned by ClientRoot.

Fields:

- constraint_set_id.
- transaction_id.
- client_root_id.
- travel_intent_ref.
- origin.
- destination.
- departure_date.
- return_date.
- max_amount.
- currency.
- baggage_required.
- avoid_overnight_layover.
- preferred_seat_characteristics.
- changeable_preferred.
- soft_preference_priority.
- raw_passport_included: false.
- raw_payment_data_included: false.
- authority_transferred: false.

Hard client constraints and soft preferences are distinct. LLM actors may
interpret soft preferences, but they may not rewrite hard constraints.

### AirlineRootOfferCandidateSetSnapshotV01

Created/owned by AirlineRoot.

Fields:

- candidate_set_ref.
- candidate_set_snapshot_id.
- candidate_set_version.
- candidate_set_digest.
- transaction_id.
- airline_root_id.
- offer_candidate_ids.
- authoritative_offer_records.
- snapshot_created_at.
- snapshot_ttl.
- raw_secret_included: false.
- provider_created: false.

Each authoritative offer record contains:

- offer_id.
- amount.
- currency.
- route_ref.
- baggage.
- seat characteristics.
- changeability.
- inventory validity.
- offer TTL / expiry.
- airline policy validity.

Provider receives a bounded projection. Provider does not own candidate facts.
The same immutable snapshot must be used through Root resolution and hold.

### AirlineSemanticSelectionInputV01

Runtime-created bounded input artifact.

Fields:

- selection_input_id.
- transaction_id.
- source_bsep_projection_ref.
- source_client_constraint_set_id.
- source_candidate_set_snapshot_id.
- source_candidate_set_digest.
- visible_candidate_ids.
- hard_valid_candidate_ids.
- soft_tradeoff_candidate_ids.
- raw_secret_included: false.
- provider_authority_created: false.

### AirlineSemanticOfferSelectionProposalV01

Provider-origin semantic proposal fields:

- proposal_id.
- transaction_id.
- actor_id.
- source_selection_input_id.
- source_bsep_projection_ref.
- source_client_constraint_set_id.
- source_candidate_set_snapshot_id.
- source_candidate_set_digest.
- candidate_set_ref.
- recommended_offer_id.
- ranked_offer_ids.
- decision_factors.
- preference_matches.
- uncertainty_notes.
- requires_root_review.
- semantic_summary.
- authority_created: false.
- action_permission_created: false.
- packet_created: false.
- receipt_created: false.
- payment_created: false.
- ticket_created: false.
- booking_created: false.
- final_output_created: false.
- real_world_effects_count: 0.

Provider must not return authoritative:

- amount.
- currency.
- passenger_ref.
- route_ref.
- hold_id.
- merchant_ref.
- TTL.
- idempotency key.
- adapter id.
- packet id.
- receipt id.

If such fields are returned, validation fails closed rather than silently using
or ignoring an attempted authority expansion.

### ValidatedAirlineSemanticSelectionEvidenceV01

Runtime-owned canonical artifact:

- canonical_selection_id.
- transaction_id.
- source_selection_input_id.
- source_actor_id.
- source_proposal_id.
- source_candidate_set_ref.
- source_client_constraint_set_id.
- source_candidate_set_snapshot_id.
- source_candidate_set_digest.
- source_synthesis_report_id.
- recommended_offer_id.
- accepted_semantic_factors.
- rejected_semantic_factors.
- validation_status.
- validation_errors.
- what_runtime_used.
- what_runtime_rejected.
- advisory_only: true.
- evidence_only: true.
- authority_created: false.
- permission_created: false.

ValidatedAirlineSemanticSelectionEvidenceV01 references the
AirlineSemanticSelectionSynthesisReportV01. It must not silently compress or
replace actor outputs without a synthesis record.

### ClientRootOfferSelectionDecisionV01

Created only by ClientRoot:

- decision_id.
- transaction_id.
- client_root_id.
- source_canonical_selection_id.
- source_candidate_set_snapshot_id.
- source_candidate_set_digest.
- recommended_offer_id.
- selected_offer_id.
- decision_status.
- recommendation_accepted.
- root_override_used.
- root_override_reason.
- semantic_influence_claimed.
- acceptance_reasons.
- rejection_reasons.
- created_by: ClientRoot.
- creates_purchase_permission: false.
- creates_payment_permission: false.
- creates_ticket_permission: false.
- requires_human_approval_before_purchase_intent: true.

This decision is a Root decision but is not yet ClientPurchaseIntent.

For causal binding PASS:

- recommendation_accepted == true.
- root_override_used == false.
- selected_offer_id == recommended_offer_id.

Root may reject or override safely. If Root overrides, do not claim semantic
causal selection: semantic_influence_claimed == false, and the binding report
status records ROOT_OVERRIDE, not CAUSAL_PASS. Root override is authority
preservation, not a general safety failure, but it is incompatible with the A/B
causal PASS proof.

### AirlineRootSelectedOfferResolutionV01

Created only by AirlineRoot:

- resolution_id.
- transaction_id.
- airline_root_id.
- source_candidate_set_snapshot_id.
- source_candidate_set_digest.
- selected_offer_id.
- authoritative_offer_ref.
- resolved_offer_record_ref.
- resolved_amount.
- resolved_currency.
- resolved_route_ref.
- resolved_baggage.
- resolved_seat.
- resolved_changeability.
- resolved_ttl.
- offer_exists.
- offer_unexpired.
- airline_offer_validity_pass.
- client_constraint_compatibility_pass.
- resolved_from_same_candidate_snapshot: true.
- semantic_values_used_as_authoritative_facts: false.

All resolved business facts come from the AirlineRoot candidate set, not from
provider text.

AirlineRoot checks:

- offer exists.
- inventory available.
- fare/policy valid.
- offer unexpired.
- candidate snapshot valid.

ClientRoot checks:

- amount within budget.
- currency accepted.
- baggage requirement.
- overnight-layover constraint.
- route/date compatibility.
- other declared client hard constraints.

Offer C may remain a real AirlineRoot offer, but fails ClientRoot hard
compatibility because baggage is absent and overnight layover is present. An
unknown or expired offer fails AirlineRoot validity. Neither Root may replace
the other Root's validation.

### AirlineSemanticSelectionSynthesisReportV01

This is Airline-domain local only. It is not the future global
SemanticWorkContract / Synthesis Loop.

Fields:

- synthesis_report_id.
- transaction_id.
- source_selection_input_id.
- canonical_actor_output_refs.
- proposer_actor_id.
- compatibility_reviewer_actor_ids.
- consistency_reviewer_actor_id.
- actor_recommended_offer_ids.
- actor_conflicts.
- synthesis_status.
- synthesized_recommended_offer_id.
- accepted_semantic_factors.
- rejected_semantic_factors.
- unresolved_conflict_present.
- requires_client_root_review.
- what_runtime_used.
- what_runtime_rejected.
- authority_created: false.
- permission_created: false.
- provider_created_contract_artifact_count: 0.

Role contract:

- client_purchase_intent_reviewer_llm: semantic offer proposer.
- airline_offer_policy_reviewer_llm: Airline compatibility reviewer.
- airline_fare_rules_vertical_cell_llm: fare/change/refund semantic reviewer.
- airline_seat_baggage_vertical_cell_llm: seat/baggage semantic reviewer.
- tri_party_evidence_consistency_reviewer_llm: identity/evidence consistency
  reviewer.

Rules:

- only validated canonical actor outputs enter synthesis.
- raw sibling outputs never enter synthesis.
- no last-writer-wins.
- no majority vote unless explicitly specified later.
- no hidden actor priority.
- conflicting recommendations do not auto-resolve.
- unresolved conflict returns Root review / FAIL_CLOSED for causal PASS.
- runtime synthesis remains proposal/evidence, not Root authority.

### AirlineHoldCommitPacket Future Binding Fields

Add these fields to the future AirlineHoldCommitPacket projection:

- source_offer_resolution_ref.
- source_candidate_set_snapshot_id.
- source_candidate_set_digest.

Required snapshot binding rules:

- candidate snapshot substitution fails closed.
- candidate digest/version mismatch fails closed.
- expired snapshot fails closed.
- no selection from one snapshot may resolve against another snapshot.

### AirlineSemanticToContractBindingReportV01

- binding_status.
- transaction_id.
- source_semantic_artifact_ref.
- canonical_selection_ref.
- client_root_decision_ref.
- airline_root_resolution_ref.
- selected_offer_id.
- hold_packet_ref.
- human_approval_ref.
- purchase_intent_ref.
- causal_binding_rows.
- silent_fallback_used: false.
- hardcoded_default_offer_used: false.
- provider_created_contract_artifact_count: 0.
- authority_transferred_count: 0.
- real_world_effects_count: 0.

## Multi-Actor Semantic Input

Future causal semantic composition:

- client_purchase_intent_reviewer_llm recommends an offer based on client goals
  and soft preferences.
- airline_offer_policy_reviewer_llm evaluates whether the candidate is
  compatible with Airline policy.
- airline_fare_rules_vertical_cell_llm explains fare/change/refund
  implications.
- airline_seat_baggage_vertical_cell_llm explains seat/baggage implications.
- tri_party_evidence_consistency_reviewer_llm checks transaction identity and
  cross-root evidence consistency.

Runtime builds one canonical selection evidence object from validated actor
outputs.

No actor independently creates the Root decision.

No sibling raw output becomes authority.

Validated canonical actor outputs feed the domain-local
AirlineSemanticSelectionSynthesisReportV01. Raw sibling outputs never enter
synthesis. The synthesis report is advisory evidence only and cannot become a
Root decision.

## Human Approval Boundary

Semantic selection does not equal purchase approval.

Required order:

```text
validated semantic recommendation
-> ClientRoot offer selection decision
-> AirlineRoot offer resolution / hold
-> scoped human approval evidence
-> ClientRoot-created ClientPurchaseIntent
-> BankRoot authorization
-> AirlineRoot ticket-issue intent
-> deterministic corridor
```

Human approval remains evidence only.

The LLM cannot fabricate human approval.

ClientPurchaseIntent cannot be created before valid hold evidence and scoped
human approval.

## Anti-Podlog / Causal Intervention Tests

Future implementation must prove:

### Selection A causes Contract A

- accepted canonical recommendation: Offer A.
- ClientRoot decision selects A.
- AirlineRoot resolves A facts.
- hold/purchase contract references A.

### Selection B causes Contract B

- same bounded candidate set.
- accepted canonical recommendation: Offer B.
- ClientRoot decision selects B.
- AirlineRoot resolves B facts.
- contract references B.

### Semantic mutation changes downstream contract

- mutate only accepted recommended_offer_id A -> B.
- downstream selected_offer_id and contract refs change A -> B.
- fixed safety invariants do not change.

### Unknown offer fails closed

- recommendation references unknown offer.
- no silent fallback to A.
- no contract artifact created.

### Hard-invalid Offer C fails closed

- even if LLM strongly recommends C.
- Root rejects C because deterministic constraints fail.
- no fallback and no contract.

### Other required negative proofs

- Missing/invalid semantic output creates no contract.
- Provider authoritative-field injection fails closed for amount override,
  currency override, passenger_ref override, route override, TTL override, and
  idempotency override.
- Rejected semantic proposal cannot create Root decision.
- ClientRoot decision absent means no contract.
- Human approval absent means no ClientPurchaseIntent.
- Provider output cannot create packet/receipt/payment/ticket/booking.
- No hardcoded default offer: source inspection and mutation tests must prove
  no unconditional selected_offer_id = Offer A path exists.
- No semantic theatre: report cannot say semantic output influenced contract
  unless causal binding rows connect semantic artifact -> canonical selection
  -> ClientRoot decision -> AirlineRoot offer resolution -> hold/purchase
  contract.

## Upstream Anti-Podlog Interventions

Preserve downstream mutation:

```text
recommended_offer_id A -> B
-> downstream contract A -> B
```

Add upstream semantic interventions with one unchanged candidate snapshot.

Scenario preference_A:

- prefer lower price.
- prefer window seat.
- extra-legroom is not a priority.

Expected:

- semantic recommendation A.
- ClientRoot accepts A.
- contract references A.

Scenario preference_B:

- prefer extra-legroom aisle.
- willing to pay up to 30 EUR more.
- budget remains 840 EUR.

Expected:

- semantic recommendation B.
- ClientRoot accepts B.
- contract references B.

Required proof:

- only soft preference input changes.
- candidate set snapshot stays identical.
- hard constraints stay identical.
- fixed safety validators stay identical.
- selected contract changes A -> B.

Fail if:

- semantic input changes but contract remains hardcoded A.
- provider response changes but synthesis ignores it.
- synthesis output changes but Root/contract ignores it.

Required future tests:

- changed_soft_preference_changes_semantic_selection.
- changed_soft_preference_changes_root_selected_offer.
- changed_soft_preference_changes_hold_contract.
- candidate_snapshot_unchanged_across_A_B_intervention.
- hard_safety_invariants_unchanged_across_A_B_intervention.
- candidate_snapshot_substitution_rejected.
- candidate_digest_mismatch_rejected.
- multi_actor_conflict_not_silently_resolved.
- root_override_does_not_claim_semantic_causality.
- offer_C_fails_client_constraint_compatibility.
- expired_offer_fails_airline_offer_validity.
- ranked_offer_ids_unknown_or_duplicate_rejected.

## Causal Binding Matrix

Required rows:

- bsep_projection_to_selection_input.
- client_constraints_to_selection_input.
- candidate_snapshot_to_selection_input.
- selection_input_to_actor_prompts.
- validated_actor_outputs_to_synthesis.
- synthesis_to_canonical_selection.
- canonical_selection_to_client_root_decision.
- client_root_decision_to_airline_root_resolution.
- airline_root_resolution_to_hold_packet.
- hold_packet_to_human_approval_scope.
- human_approval_to_client_purchase_intent.
- client_purchase_intent_to_corridor.

Each row:

- binding_id.
- transaction_id.
- source_artifact_type.
- source_artifact_id.
- source_field.
- source_value.
- target_artifact_type.
- target_artifact_id.
- target_field.
- target_value.
- values_match.
- source_snapshot_id.
- target_snapshot_id.
- snapshot_match.
- causal_input_present.
- semantic_influence_present.
- authority_transferred: false.
- provider_created_target: false.

PASS requires all required rows and snapshot bindings to match.

## Implementation Program

Slice A:

- this preflight only.

Slice B:

- local Airline domain contracts and validators.
- recommended future files:
  - hedgehog/domains/airline/semantic_to_contract_binding_v01.py.
  - tests/test_airline_semantic_to_contract_binding_v01.py.
- includes ClientRootTravelConstraintSetV01,
  AirlineRootOfferCandidateSetSnapshotV01,
  AirlineSemanticSelectionInputV01, and
  AirlineSemanticSelectionSynthesisReportV01.
- no provider/network.
- no runner integration.

Slice C:

- injected/fake semantic proposal causal tests.
- A/B counterfactual selection.
- C hard-constraint rejection.
- upstream preference_A / preference_B intervention tests over one immutable
  candidate snapshot.
- multi-actor conflict and Root override honesty tests.
- no real Gemini.

Slice D:

- integrate typed semantic selection into the existing Airline live semantic
  lane and existing deterministic Airline runner.
- no new duplicate demo.
- no silent default offer.

Slice E:

- operator-gated real Gemini causal run.
- structured semantic offer selection artifacts.
- source artifact capture.
- causal binding matrix.
- no real effects.

Slice F:

- one combined audit and human story for real semantics -> Root contract ->
  deterministic corridor.

Only after Slice F PASS:

- close final Airline Corridor audit.
- open Airline Transaction Artifact Ledger v0.1.

## Ledger / Crypto / Replay Gate

Transaction Artifact Ledger remains blocked until:

- semantic-to-contract causal binding deterministic PASS.
- real-provider causal binding PASS.
- causal binding audit PASS.
- integrated Corridor audit PASS.

Crypto and Replay remain blocked behind Ledger.

Reason: do not seal or replay a trace until the semantic-to-contract causal
edge is proven rather than narrated.

## Preserved Program And Gates

Preserve:

- provider proposes semantics only.
- Runtime canonicalizes.
- Root decides.
- human approval separate.
- no provider contract creation.
- no hardcoded fallback.
- no real effects.
- Slice B local model first.
- real Gemini only later.
- Ledger blocked until causal binding + integrated audit PASS.
- Crypto/Replay remain blocked.

Do not create:

- global synthesis runtime.
- new universal authority engine.
- new demo.
- Ledger/Crypto/Replay implementation.

## Non-Goals

- no production recommendation engine.
- no real airline inventory.
- no real booking.
- no real payment.
- no real ticket.
- no provider-created contract.
- no provider-created Root decision.
- no autonomous human approval.
- no LLM-controlled safety invariants.
- no post-Root reasoning restart.
- no new universal authority engine.
- no new demo.
- no Ledger implementation.
- no Crypto implementation.
- no Replay implementation.

## Definition Of Done

The preflight is complete only if it records:

- the current semantic/corridor gap honestly.
- input->semantic and semantic->contract edges.
- immutable candidate snapshot binding.
- separated ClientRoot and AirlineRoot hard checks.
- semantic choice vs deterministic safety separation.
- typed semantic proposal contract.
- domain-local multi-actor synthesis contract.
- runtime canonical semantic evidence.
- ClientRoot decision boundary.
- honest Root override semantics.
- AirlineRoot authoritative offer resolution.
- human approval remains separate.
- no direct provider contract creation.
- no hardcoded default offer.
- A/B counterfactual causal tests.
- C hard-invalid rejection.
- no silent fallback.
- causal binding matrix.
- gated path to real Gemini causal run.
- Ledger remains blocked.
