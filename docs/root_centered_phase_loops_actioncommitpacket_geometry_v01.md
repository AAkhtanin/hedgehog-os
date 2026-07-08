# Root-Centered Phase Loops / ActionCommitPacket Geometry v01

## 1. Status / Closed Basis

- document_id: root_centered_phase_loops_actioncommitpacket_geometry_v01
- document_status: ARCHITECTURE_CORRECTION_SPEC
- observed_base_head: 5cb71cd
- implementation_scope_now: ActionCommitPacket / permission hardening
- production_ready_claimed: false
- public_auditor_ready_claimed: false
- real_world_effects_count: 0

Closed basis:

- Full WOW v1.2 live multi-LLM/fractal observation: PASS.
- Local DRS v0.2: PASS.
- AVF v0.2: PASS.
- DRS + AVF live semantic package: PASS.
- Current next gate: ActionCommitPacket / permission hardening.

Do not start Airline, Privacy, Finance, Vendor, Marennya, UP, or real
connector work from this correction. This document records architecture before
ActionCommitPacket Slice A.

## 2. Core Correction: Hedgehog OS Is Not A Long Chain

Root is not only final endpoint.

Root is the phase boundary.

A task may pass through several Root-centered phase loops before terminal
FinalOutput.

Core geometry:

```text
Root -> phase-loop / petal -> Root -> next bounded phase-loop / petal -> Root
```

This means a Root checkpoint can close one bounded phase and open the next
bounded phase without making the whole system a single linear chain.

## 3. Main Phase Geometry

Main phase vocabulary:

- `DeliberationPetal` / `ProposalPetal`: semantic/reasoning plane work that
  returns advisory proposal artifacts.
- `RootReview`: Root boundary that evaluates proposals and may create the next
  bounded contract.
- `FulfillmentPetal` / `CommitPetal`: deterministic contract/commit plane work
  that consumes a Root-created scoped packet.
- `RootFinal`: terminal Root boundary that creates FinalOutput when appropriate.
- `RootAudit`: Root audit boundary for evidence, receipt, delivery, and status
  after a bounded phase.

RootReview and RootFinal are not interchangeable. If additional semantic work
is still needed, the boundary is RootReview, not terminal RootFinal.

## 4. Abstract Vocabulary: RootScopedContractEnvelope

`RootScopedContractEnvelope` is architecture vocabulary only. It is not current
runtime implementation.

Subtypes:

- `SemanticWorkContract`
- `ActionCommitPacket`
- `DeliveryEnvelope` / `TerminalDeliveryPetal`

Explicit current limits:

- Do not implement generic `RootScopedContractEnvelope` runtime now.
- Do not implement `SemanticWorkContract` now.
- Do not implement `DeliveryEnvelope` now.
- Implement only ActionCommitPacket / permission hardening for Supplier A mock
  payment.

## 5. Semantic Work Vs Action Work

Semantic work:

- may use bounded LLM/SLM;
- returns `SynthesisProposal` / `ResultProposal`;
- does not create FinalOutput;
- if LLM is still needed after a Root boundary, that boundary was RootReview,
  not terminal RootFinal.

Action work:

```text
RootDecision / scoped human approval evidence
-> Root-created ActionCommitPacket
-> deterministic ContractFulfillmentCorridor
-> MockBankSandbox
-> Receipt / CompletionEvidence
-> RootAudit or RootFinal
```

Action corridor requirements:

- action corridor must not restart LLM reasoning;
- action corridor validates and consumes packet only;
- action corridor does not reason;
- action corridor does not expand scope.

## 6. ActionCommitPacket Meaning

ActionCommitPacket is:

- sealed;
- scoped;
- Root-created;
- permission artifact;
- not action itself.

Human analogy:

ActionCommitPacket is a signed payment instruction from the director, not the
payment itself.

## 7. ActionCommitPacket Is Not

ActionCommitPacket is not:

- FinalOutput;
- LLM decision;
- AVF permission;
- DRS memory;
- receipt;
- real payment;
- shipment release;
- future permission.

## 8. Human Approval Rule

Formula:

```text
HumanApproval(scope) = scoped evidence for Root.
RootDecision + HumanApproval(scope) -> Root-created ActionCommitPacket(scope).
```

Forbidden creators:

- Human approval alone cannot create ActionCommitPacket.
- LLM cannot create ActionCommitPacket.
- AVF cannot create ActionCommitPacket.
- DRS cannot create ActionCommitPacket.
- GT/LGT cannot create ActionCommitPacket.

Only Root creates ActionCommitPacket.

## 9. Current Supplier A Mock Payment Packet

Current packet represents one logical Supplier A mock payment operation.

Supplier A mock payment only.

It does not represent:

- Supplier B;
- shipment release;
- real payment.

Conceptual fields:

- `packet_id`
- `created_by = root`
- `source_root_decision_ref`
- `human_approval_ref`
- `allowed_subjects`
- `forbidden_subjects`
- `allowed_action`
- `forbidden_actions`
- `allowed_adapter`
- `forbidden_adapters`
- `payment_intent`
- `evidence_refs`
- `expiry` / `TTL`
- `idempotency_key`
- `replay_guard`
- `receipt_policy`

## 10. Bank-Like Deterministic Corridor

Inside MockBankSandbox, emulate deterministic bank-like flow:

1. receive ActionCommitPacket
2. validate packet shape
3. validate `created_by == root`
4. validate scope
5. validate supplier is Supplier A
6. validate Supplier B is excluded
7. validate `shipment_release_allowed == false`
8. validate adapter is MockBankSandbox
9. validate expiry / TTL
10. validate `idempotency_key` / replay guard
11. validate payment intent fields
12. create mock payment intent / consent
13. create mock payment order
14. return mock receipt evidence
15. register terminal receipt / used idempotency key

Corridor boundaries:

- does not reason;
- does not call LLM;
- does not expand scope;
- does not call real bank;
- does not release shipment.

## 11. Scope Containment Laws

Containment laws:

- Allowed(child) ⊆ Allowed(parent)
- Scope(child) ⊆ Scope(parent)
- Forbidden(child) ⊇ Forbidden(parent)
- TTL(child) ≤ TTL(parent)
- Adapter(child) ∈ AllowedAdapters(parent)
- NoExpansionAfterRoot = true

If any law fails, the corridor fails closed and returns to Root.

## 12. Receipt Rules

receipt is evidence only.

Receipt must bind to packet:

- `receipt.packet_id == action_commit_packet.packet_id`
- `receipt.subject ⊆ packet.scope`
- `receipt.adapter == allowed_adapter`

Receipt must not create:

- future permission;
- shipment release;
- payment permission for Supplier B;
- Root decision;
- FinalOutput;
- ActionCommitPacket.

Forbidden receipt behavior:

- receipt cannot grant permission;
- receipt cannot release shipment;
- receipt cannot authorize future payment;
- receipt cannot override Root;
- receipt cannot mutate packet scope;
- receipt cannot create production DRS record.

## 13. Replay / Duplicate Rules

Minimal local registry:

- `local_packet_registry`
- `seen_packet_ids`
- `used_idempotency_keys`
- `expired_packet_ids`
- `terminal_receipts`

Required behavior:

- duplicate packet rejected;
- duplicate idempotency key rejected after terminal receipt;
- expired packet rejected;
- wrong `packet_id` in receipt rejected;
- receipt replay rejected.

Retry:

One packet may represent one logical operation. Retry may be allowed only before
terminal receipt and only with the same idempotency key. After terminal receipt,
duplicate execution is rejected.

## 14. Pre-Final Vs Post-Final Petals

If action result affects final answer:

```text
RootReview
-> ActionCommitPacket
-> ContractFulfillmentCorridor
-> Receipt / CompletionEvidence
-> RootFinal
```

If final answer already exists:

```text
RootFinalOutput
-> TerminalDeliveryPetal
-> DeliveryEvidence / AuditEvent
-> RootAudit
```

Post-final petal must not:

- modify FinalOutput;
- restart LLM reasoning;
- expand scope;
- create action permission;
- reinterpret result;
- turn delivery evidence into authority.

## 15. Current Implementation Slices

- Slice 0 preflight already done.
- Slice A local packet/corridor model.
- Slice B packet/corridor validator.
- Slice C Supplier A mock packet integration.
- Slice D MockBankSandbox corridor execution.
- Slice E adversarial/replay/receipt hardening.
- Slice F audit/docs/human story.

## 16. Required Counters

Required future counters:

- `action_commit_packet_created_by_root_count: 1`
- `action_commit_packet_created_by_llm_count: 0`
- `action_commit_packet_created_by_avf_count: 0`
- `action_commit_packet_created_by_drs_count: 0`
- `action_commit_packet_created_by_gt_lgt_count: 0`
- `human_approval_used_as_evidence_count: 1`
- `human_approval_created_packet_count: 0`
- `supplier_a_packet_created_count: 1`
- `supplier_b_packet_created_count: 0`
- `shipment_release_packet_created_count: 0`
- `real_bank_packet_created_count: 0`
- `mock_bank_sandbox_packet_validated_count: 1`
- `mock_payment_order_created_count: 1`
- `mock_receipt_created_count: 1`
- `receipt_evidence_only_count: 1`
- `receipt_permission_created_count: 0`
- `receipt_shipment_release_created_count: 0`
- `receipt_future_permission_created_count: 0`
- `duplicate_packet_rejected_count: >=1`
- `expired_packet_rejected_count: >=1`
- `wrong_scope_packet_rejected_count: >=1`
- `wrong_adapter_packet_rejected_count: >=1`
- `supplier_b_leakage_rejected_count: >=1`
- `shipment_leakage_rejected_count: >=1`
- `real_payment_executed_count: 0`
- `real_bank_api_called_count: 0`
- `real_supplier_api_called_count: 0`
- `real_warehouse_api_called_count: 0`
- `shipment_released_count: 0`
- `real_world_effects_count: 0`
- `root_final_authority_preserved_count: 1`

## 17. Strict Non-Goals

Do not implement:

- Airline demo;
- `TicketPurchaseCommitBundle`;
- `SemanticWorkContract` runtime;
- `DeliveryEnvelope` runtime;
- general `RootScopedContractEnvelope` runtime;
- Hedgehog-native bank-to-bank contract;
- real bank API;
- real supplier API;
- real warehouse API;
- production DRS;
- external/global DRS;
- Marennya;
- UP;
- NeedleFactory;
- public auditor package.

Do not call provider, network, Gemini, or a real connector.

Do not create real payment, real shipment release, production persistence,
production-ready claim, or public-auditor claim.

## 18. Human-Readable Final Story Target

The final story should say:

The system reasoned about Supplier A, Supplier B, shipment, DRS memory, AVF
pressure, LLM branch semantics, Post V&V, and Root review.

Then Root created exactly one scoped ActionCommitPacket for Supplier A mock
payment.

MockBankSandbox accepted only that packet, checked scope, adapter, expiry,
idempotency, and payment intent, and returned a mock receipt as evidence only.

Supplier B remained excluded.

Shipment release remained excluded.

Real bank remained excluded.

Receipt did not become permission.

Root remained final authority.

## 19. Final One-Line Instruction

Build ActionCommitPacket / permission hardening as a Root-created, scoped,
replay-protected, deterministic contract corridor for Supplier A mock payment
only: one Root packet enters MockBankSandbox, scope/adapter/expiry/idempotency
are validated, a mock receipt returns as evidence only, and Supplier B, shipment
release, real bank, receipt-as-permission, LLM/DRS/AVF authority, and all
real-world effects remain blocked.
