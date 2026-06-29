# ActionCommitPacket / Root Mock Approval Gate v0.1 Preflight

preflight_id: action_commit_packet_root_mock_approval_gate_preflight_v01
preflight_status: COMPLETE
base_head: bbb9182
planning_only: true
runtime_created: false
tests_created: false
audit_log_created: false
public_wow_ready: false
production_ready: false
new_runner_required: false
existing_full_e2e_runner_is_source_of_truth: true
commit_created: false

## Purpose

Plan the next runtime layer where Root may create a mock-only ActionCommitPacket after a safe Root approval boundary.

This layer is not fake bank execution, fake shipment execution, connector sandbox execution, real payment, real shipment, production, NeedleFactory, Marennya / UP, or autonomous business execution. It is a planning step toward a Root-only permission artifact for later mock connector sandbox work.

Core idea:
Today the full E2E path can refuse unsafe action. Next we add a Root-only mock approval gate that can create a bounded mock-only ActionCommitPacket, but still cannot execute connectors.

The packet is permission-to-attempt-a-mock-action later. It is not the action itself. It is not a receipt. It is not payment. It is not shipment release. It is not FinalOutput. It is not Root replacement.

## Current Closed Base

- Full Semantic E2E closed.
- Real Gemini evidence influence closed.
- Bounded Gemini Orchestrator role closed.
- Bounded Gemini Architect role closed.
- Dual Gemini Orchestrator+Architect runtime closed.
- Public WOW human walkthrough draft closed.
- Current system can run full E2E to Root.
- Current Root decision in supplier-payment scenario is not_ready.
- Current runtime executes no payment, no shipment, no connector.

Durable current facts:
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0
- Root remains final authority

## Canonical Future Placement

SemanticEvidenceClaim
-> DRS candidate context
-> CandidateVector
-> AVF/advisory
-> Gemini Orchestrator / validated route
-> Gemini Architect / validated PlanGraph
-> Fractal executor
-> ResultProposal
-> Post V&V
-> GT/LGT
-> Root FinalOutput boundary
-> Root Mock Approval Gate
-> ActionCommitPacket candidate
-> DRS writeback

Important boundaries:
- ActionCommitPacket can be created only after Root final boundary.
- ActionCommitPacket can be created only by Root / Root Mock Approval Gate.
- Gemini cannot create ActionCommitPacket.
- Orchestrator cannot create ActionCommitPacket.
- Architect cannot create ActionCommitPacket.
- Executor cannot create ActionCommitPacket.
- AVF cannot create ActionCommitPacket.
- GT/LGT cannot create ActionCommitPacket.
- DRS cannot create ActionCommitPacket.
- Root not_ready must not create an approval packet.

## Current Blocked Scenario

Current supplier-payment scenario:
- Invoice INV-2042 looks payable.
- Shipment SH-2042 requested.
- legal hold / expired insurance risk exists.
- water_filter shortage exists.
- Root decision: not_ready.

Expected behavior:
- Root Mock Approval Gate may deny approval if explicitly enabled.
- ActionCommitPacket must not be created.
- Human/mock approval must not override legal hold or stock shortage.
- If blockers remain, approval is denied.

Expected counters when gate is explicitly enabled on the current blocked scenario:
- root_mock_approval_gate_invoked_count: 1
- root_mock_approval_denied_count: 1
- root_mock_approval_blocked_by_legal_hold_count: 1
- root_mock_approval_blocked_by_stock_shortage_count: 1
- mock_action_commit_packet_created_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0

## Future Mock-Ready Scenario

The first runtime slice should include an explicit local fixture for a mock-ready scenario:
- HEDGEHOG_FULL_E2E_MOCK_READY_FIXTURE=1
- legal hold is cleared.
- stock shortage is cleared or mock-reservation-ready.
- Post V&V has run.
- GT/LGT has reviewed.
- Root decision can become ready_for_mock_action or equivalent.
- Root Mock Approval Gate may create one mock-only ActionCommitPacket.

Packet outcome constraints:
- mock_only: true
- real_world_effects_allowed: false
- connector_called_count remains 0 in this layer.
- fake_bank_connector_called_count: 0
- fake_supplier_connector_called_count: 0
- fake_warehouse_connector_called_count: 0
- real_bank_api_called_count: 0
- real_supplier_api_called_count: 0
- real_warehouse_api_called_count: 0
- mock_receipt_created_count: 0
- execution_evidence_created_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0
- Root remains final authority

Recommendation:
Do both in one runtime slice if safe:
- default/current blocked scenario proves no packet
- explicit mock-ready fixture proves Root can create one mock-only packet
- no connector execution yet

## Future Gates

Preferred env gates:
- HEDGEHOG_FULL_E2E_ACTION_COMMIT_PACKET=1
- HEDGEHOG_FULL_E2E_ROOT_MOCK_APPROVAL=1

Optional explicit fixture selector:
- HEDGEHOG_FULL_E2E_MOCK_READY_FIXTURE=1

Gate behavior:
- default mode has all Root Mock Approval Gate counters at zero
- enabling gate on the current blocked scenario denies approval
- enabling gate plus mock-ready fixture can produce one mock-only packet
- no connector sandbox runs in this layer
- no fake receipt is created in this layer

## ActionCommitPacket Proposed Shape

Required packet fields:
- packet_type: mock_action_commit_packet
- packet_id
- created_by: root_mock_approval_gate
- source_root_outcome_id
- source_root_decision
- business_subject
- action_scope: local_mock_connector_sandbox
- mock_only: true
- real_world_effects_allowed: false
- allowed_action_kinds
- forbidden_action_kinds
- allowed_future_adapters
- forbidden_real_adapters
- root_reviewed: true
- root_approved: true
- approval_reason
- blockers_checked:
  - legal_hold_clear
  - stock_available_or_mock_reservable
  - post_vv_passed
  - gt_lgt_reviewed
- validator_receipts
- trace_refs
- idempotency_key
- expires_at
- root_final_authority_preserved: true

Forbidden packet fields:
- real_payment_executed
- real_shipment_released
- bank_api_called
- warehouse_api_called
- supplier_api_called
- connector_called
- final_output_created_by_packet
- authority_claimed_by_packet
- gemini_created_packet

Packet rejection rules:
- packet with connector command is rejected
- packet with payment execution field is rejected
- packet with shipment release field is rejected
- packet before Root boundary is rejected with root_boundary_required
- packet from Gemini, Orchestrator, Architect, Executor, AVF, GT/LGT, or DRS is rejected or ignored
- packet with unknown action kind is rejected
- packet cannot create FinalOutput
- packet cannot execute itself

## Future Counters

Required counters to add:
- root_mock_approval_gate_invoked_count
- root_mock_approval_granted_count
- root_mock_approval_denied_count
- root_mock_approval_blocked_by_legal_hold_count
- root_mock_approval_blocked_by_stock_shortage_count
- action_commit_packet_created_count
- mock_action_commit_packet_created_count
- action_commit_packet_created_by_root_count
- action_commit_packet_created_by_gemini_count
- action_commit_packet_created_before_root_count
- action_commit_packet_rejected_count
- action_commit_packet_mock_only_count
- action_commit_packet_real_world_effects_allowed_count
- action_commit_packet_used_as_final_output_count
- action_commit_packet_executed_connector_count
- fake_bank_connector_called_count
- fake_supplier_connector_called_count
- fake_warehouse_connector_called_count
- real_bank_api_called_count
- real_supplier_api_called_count
- real_warehouse_api_called_count
- mock_receipt_created_count
- execution_evidence_created_count

Expected default mode:
- root_mock_approval_gate_invoked_count: 0
- action_commit_packet_created_count: 0
- mock_action_commit_packet_created_count: 0
- action_commit_packet_executed_connector_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0

Expected current blocked scenario with gate enabled:
- root_mock_approval_gate_invoked_count: 1
- root_mock_approval_denied_count: 1
- mock_action_commit_packet_created_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0

Expected explicit mock-ready scenario:
- root_mock_approval_gate_invoked_count: 1
- root_mock_approval_granted_count: 1
- mock_action_commit_packet_created_count: 1
- action_commit_packet_mock_only_count: 1
- action_commit_packet_real_world_effects_allowed_count: 0
- action_commit_packet_executed_connector_count: 0
- fake_bank_connector_called_count: 0
- fake_supplier_connector_called_count: 0
- fake_warehouse_connector_called_count: 0
- real_bank_api_called_count: 0
- real_supplier_api_called_count: 0
- real_warehouse_api_called_count: 0
- mock_receipt_created_count: 0
- execution_evidence_created_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0
- Root remains final authority

Counter policy:
- Existing action_permission_created_count currently means unsafe/real action permission in the full E2E safety ledger.
- action_permission_created_count should remain 0 in v0.1.
- Prefer mock-specific counters: mock_action_commit_packet_created_count and action_commit_packet_mock_only_count.

## Future Runtime Target

Preferred runtime files:
- demo/run_full_semantic_e2e_v01.py
- tests/test_full_semantic_e2e_v01_runner.py

No new runner unless a blocker is found.

Core-module policy:
- Do not modify hedgehog/* in this preflight.
- First runtime slice can prototype ActionCommitPacket locally in the existing runner.
- Extract to a core module such as hedgehog/action_commit_packet.py only after packet shape stabilizes.

## Required Future Tests

A. Default mode:
- FINAL STATUS: PASS
- root_mock_approval_gate counters zero
- action_commit_packet counters zero
- no payment/shipment/connector

B. Gate enabled on current blocked scenario:
- Root decision remains not_ready
- legal hold and water_filter shortage block approval
- root_mock_approval_denied_count == 1
- mock_action_commit_packet_created_count == 0
- payment/shipment/connector remain 0

C. Explicit mock-ready fixture:
- blockers cleared in controlled local fixture
- Root decision becomes ready_for_mock_action or equivalent
- Root Mock Approval Gate grants mock approval
- one mock-only ActionCommitPacket created
- mock_only: true
- real_world_effects_allowed: false
- connector_called_count == 0
- fake_bank_connector_called_count == 0
- real_bank_api_called_count == 0

D. Gemini cannot create packet:
- fake Orchestrator tries action_commit_packet_claimed
- fake Architect tries action_commit_packet_claimed
- packet rejected or ignored
- action_commit_packet_created_by_gemini_count == 0
- Root-created packet only

E. Pre-root packet blocked:
- attempt to create ActionCommitPacket before Root boundary
- action_commit_packet_created_before_root_count == 0
- rejection reason includes root_boundary_required

F. Packet cannot execute itself:
- packet contains connector command or payment execution field
- rejected
- action_commit_packet_executed_connector_count == 0
- connector_called_count == 0

G. Unknown action kind:
- packet asks for unsupported action
- rejected
- no receipt, no connector

H. Post V&V / GT-LGT remain upstream:
- packet creation requires Post V&V and GT/LGT facts
- GT/LGT does not create packet
- GT/LGT remains not Root

I. DRS writeback:
- packet creation or denial is recorded only as local audit/memory trace after Root
- no external/global DRS write
- no production persistence

## Preflight Answers

1. Can existing Full E2E runner host Root Mock Approval Gate safely?
- Yes. It already has the Root boundary, Post V&V, GT/LGT, DRS writeback context, and zero-action safety counters needed for a first local gate.

2. Is a new runner needed?
- No. A new runner would risk creating a proof island.

3. Is a new core module needed now, or should packet shape stabilize in runner first?
- No new core module is needed for the first slice. Stabilize the packet shape in the existing runner first.

4. How should blocked current scenario behave?
- Root decision remains not_ready. Gate denial is recorded only when explicitly enabled. No packet is created.

5. How should explicit mock-ready scenario be represented?
- Use HEDGEHOG_FULL_E2E_MOCK_READY_FIXTURE=1 to clear blockers in a controlled local fixture and allow Root to reach ready_for_mock_action or equivalent.

6. What exact packet fields are required?
- Use the ActionCommitPacket Proposed Shape section above.

7. What exact counters are required?
- Use the Future Counters section above.

8. Should action_permission_created_count remain 0?
- Yes. Keep action_permission_created_count at 0 in v0.1 to avoid implying real action permission.

9. What tests are required?
- Use the Required Future Tests section above.

10. What is the next runtime implementation target?
- demo/run_full_semantic_e2e_v01.py and tests/test_full_semantic_e2e_v01_runner.py.

11. What comes after ActionCommitPacket runtime?
- Mock Connector Sandbox v0.1: fake bank adapter, fake supplier adapter, fake warehouse adapter, and mock receipt only after valid ActionCommitPacket.

12. Is a separate patch plan required?
- No. If no blocker is found, next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests.

## Verdict

- next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests
- no new runner
- no fake bank connector yet
- no real connector
- no production
- no NeedleFactory
- no Marennya / UP
- Mock Connector Sandbox v0.1 is the next layer after this runtime, not now
