# Mock Connector Sandbox v0.1 Preflight

preflight_id: mock_connector_sandbox_preflight_v01
preflight_status: COMPLETE
base_head: c9c1e3d
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

Plan the next runtime layer where a valid Root-created `mock_action_commit_packet` can be consumed by local fake connector adapters to produce mock receipts and local execution evidence.

This layer is not real payment, real shipment, real bank/supplier/warehouse API use, production, NeedleFactory, Marennya / UP, or autonomous external execution.

Core idea:
ActionCommitPacket is the key. Mock Connector Sandbox is the first door. The fake adapters may run only after the packet validator accepts a Root-created mock-only ActionCommitPacket.

## Closed Source Facts

Durable source documents inspected:
- docs/action_commit_packet_root_mock_approval_gate_preflight_v01.md
- docs/audit_reports/auditor_action_commit_packet_root_mock_approval_gate_runtime_v01.log
- demo/run_full_semantic_e2e_v01.py
- tests/test_full_semantic_e2e_v01_runner.py
- docs/audit_reports/auditor_dual_gemini_orchestrator_architect_runtime_v01.log
- docs/public_wow_dual_gemini_walkthrough_v01.md

Committed current facts:
- ActionCommitPacket / Root Mock Approval Gate is closed.
- Root can deny the blocked current supplier-payment scenario.
- Root can create one Root-approved mock-only ActionCommitPacket in the explicit mock-ready fixture.
- Current ActionCommitPacket is permission-to-attempt-a-mock-action later, not execution.
- Current runtime does not call fake bank / fake supplier / fake warehouse adapters.
- current mock_receipt_created_count: 0
- current execution_evidence_created_count: 0
- Root remains final authority

Manual smoke artifacts are local and intentionally not committed. Committed audit logs are the durable source of truth.

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
-> Mock Connector Sandbox
-> fake bank / fake supplier / fake warehouse adapters
-> mock receipts
-> execution evidence
-> mock execution validation
-> Root mock execution summary
-> DRS writeback

Important boundaries:
- Mock Connector Sandbox consumes ActionCommitPacket.
- ActionCommitPacket is non-executing.
- Gemini cannot invoke fake adapters.
- Orchestrator cannot invoke fake adapters.
- Architect cannot invoke fake adapters.
- Fractal executor cannot bypass ActionCommitPacket.
- AVF cannot authorize adapters.
- GT/LGT cannot authorize adapters.
- Root remains final authority.

## Future Env Gate

New gate to evaluate:
- HEDGEHOG_FULL_E2E_MOCK_CONNECTOR_SANDBOX=1

Required gate composition:
Mock Connector Sandbox may run only when all are true:
- HEDGEHOG_FULL_E2E_ACTION_COMMIT_PACKET=1
- HEDGEHOG_FULL_E2E_ROOT_MOCK_APPROVAL=1
- HEDGEHOG_FULL_E2E_MOCK_READY_FIXTURE=1
- HEDGEHOG_FULL_E2E_MOCK_CONNECTOR_SANDBOX=1

Dual Gemini is not required for the first sandbox runtime. The sandbox should work with the deterministic default Orchestrator/Architect path plus mock-ready fixture. Dual Gemini plus sandbox can be a later composition smoke.

Reason:
The sandbox validates ActionCommitPacket contract and local mock receipt discipline. It must not depend on live Gemini.

## Gate Behavior

1. Default mode:
- unchanged PASS
- no mock connector sandbox
- all mock connector counters zero

2. Sandbox gate without valid ActionCommitPacket:
- FAIL_CLOSED
- validation_errors includes mock_connector_sandbox_requires_valid_action_commit_packet
- no fake adapters run
- no mock receipts
- no execution evidence

3. Sandbox gate with blocked current scenario:
- Root decision remains not_ready
- ActionCommitPacket is not created
- sandbox denied before adapters
- fake adapter counters stay zero

4. Sandbox gate with valid mock-ready ActionCommitPacket:
- ActionCommitPacket validated
- fake adapters may run
- mock receipts may be created
- execution evidence may be created
- real-world safety counters remain zero

## Expiry Policy

ActionCommitPacket v0.1 has deterministic fixture `expires_at`. Mock Connector Sandbox must define expiry semantics before consuming packets.

Recommendation:
- Use deterministic scenario time in v0.1.
- Scenario time source: `SLICE1_NOW` or packet/root fixture time.
- Packet is valid only if `scenario_now <= expires_at`.
- Do not use runtime wall-clock in v0.1.
- production_ready remains false; later production work must replace this with signed TTL / wall-clock policy.
- No connector should consume an expired packet.

## Fake Adapters To Plan

The first sandbox slice plans three local deterministic adapters:
- fake_bank_adapter_v0
- fake_supplier_adapter_v0
- fake_warehouse_adapter_v0

Adapter restrictions:
- no network
- no `requests`, `httpx`, `urllib`, `socket`, or `subprocess`
- no real APIs
- no secrets
- no production persistence

Adapter inputs:
- validated ActionCommitPacket
- business_subject
- allowed_action_kinds
- idempotency_key
- deterministic scenario time
- bounded supplier/payment/shipment context summary

## Mock Receipt Shapes

fake_bank_adapter_v0 output:
- receipt_type: mock_bank_payment_review_receipt
- adapter_name: fake_bank_adapter_v0
- source_packet_id
- idempotency_key
- mock_only: true
- real_world_effects_allowed: false
- bank_api_called: false
- payment_executed: false
- amount_moved: 0
- status: mock_payment_review_recorded
- evidence_kind: mock_receipt

fake_supplier_adapter_v0 output:
- receipt_type: mock_supplier_confirmation_receipt
- adapter_name: fake_supplier_adapter_v0
- source_packet_id
- idempotency_key
- mock_only: true
- real_world_effects_allowed: false
- supplier_api_called: false
- supplier_order_created: false
- status: mock_supplier_review_recorded
- evidence_kind: mock_receipt

fake_warehouse_adapter_v0 output:
- receipt_type: mock_warehouse_reservation_receipt
- adapter_name: fake_warehouse_adapter_v0
- source_packet_id
- idempotency_key
- mock_only: true
- real_world_effects_allowed: false
- warehouse_api_called: false
- shipment_released: false
- inventory_reserved: mock_reserved_only
- status: mock_reservation_review_recorded
- evidence_kind: mock_receipt

## ExecutionEvidence Shape

ExecutionEvidence proposed shape:
- evidence_type: mock_connector_execution_evidence
- evidence_id
- created_by: mock_connector_sandbox
- source_packet_id
- source_root_outcome_id
- business_subject
- mock_only: true
- real_world_effects_allowed: false
- adapter_receipts
- receipt_count
- adapter_names
- scenario_time
- packet_expires_at
- packet_not_expired_at_scenario_time: true
- connector_sandbox_completed: true
- real_connector_called: false
- payment_executed: false
- shipment_released: false
- root_final_authority_preserved: true

## Mock Execution Validation

Local validation must check:
- source packet was accepted
- packet created_by is root_mock_approval_gate
- packet.mock_only is true
- packet.real_world_effects_allowed is false
- packet not expired at deterministic scenario time
- every receipt source_packet_id equals packet_id
- every receipt mock_only is true
- every receipt real_world_effects_allowed is false
- every receipt real API called flag is false
- every receipt payment/shipment execution flag is false
- allowed adapter names are exactly fake_*_adapter_v0
- no unknown adapter
- no missing receipt
- no duplicate receipt
- no real connector marker
- no secrets
- no .tmp path in evidence

## Counter Policy

Existing real/external safety counters must remain zero:
- connector_called_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- real_bank_api_called_count: 0
- real_supplier_api_called_count: 0
- real_warehouse_api_called_count: 0
- action_permission_created_count: 0

Mock-specific counters may become nonzero. Important naming policy:
- fake bank/supplier/warehouse local connector counters may become one because they are explicitly fake/local.
- connector_called_count must remain 0 because it represents real/external connector use in the safety ledger.
- payment_executed_count and shipment_released_count remain 0 because no real payment or real shipment occurs.
- Tests must preserve this distinction.

Required future counters to add or evaluate:
- mock_connector_sandbox_invoked_count
- mock_connector_sandbox_completed_count
- mock_connector_sandbox_denied_count
- mock_connector_sandbox_requires_packet_count
- mock_connector_sandbox_packet_validated_count
- mock_connector_sandbox_packet_expired_count
- mock_connector_sandbox_rejected_count
- mock_connector_sandbox_real_world_effects_blocked_count
- mock_connector_sandbox_unknown_adapter_blocked_count
- mock_connector_sandbox_duplicate_receipt_blocked_count
- mock_connector_sandbox_missing_receipt_blocked_count
- mock_connector_receipts_created_count
- mock_bank_receipt_created_count
- mock_supplier_receipt_created_count
- mock_warehouse_receipt_created_count
- fake_bank_adapter_invoked_count
- fake_supplier_adapter_invoked_count
- fake_warehouse_adapter_invoked_count
- fake_bank_connector_called_count
- fake_supplier_connector_called_count
- fake_warehouse_connector_called_count
- mock_receipt_created_count
- execution_evidence_created_count
- execution_evidence_validated_count
- root_mock_execution_summary_created_count
- real_bank_api_called_count
- real_supplier_api_called_count
- real_warehouse_api_called_count

Expected valid mock-ready sandbox counters:
- mock_connector_sandbox_invoked_count: 1
- mock_connector_sandbox_completed_count: 1
- mock_connector_sandbox_packet_validated_count: 1
- fake_bank_adapter_invoked_count: 1
- fake_supplier_adapter_invoked_count: 1
- fake_warehouse_adapter_invoked_count: 1
- fake bank local connector counter becomes one
- fake supplier local connector counter becomes one
- fake warehouse local connector counter becomes one
- mock_bank_receipt_created_count: 1
- mock_supplier_receipt_created_count: 1
- mock_warehouse_receipt_created_count: 1
- mock_connector_receipts_created_count: 3
- mock_receipt_created_count: 3
- execution_evidence_created_count: 1
- execution_evidence_validated_count: 1
- root_mock_execution_summary_created_count: 1
- real_bank_api_called_count: 0
- real_supplier_api_called_count: 0
- real_warehouse_api_called_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- connector_called_count: 0
- action_permission_created_count: 0
- root_final_authority_preserved_count: 1
- Root remains final authority

## Result Contexts

Future runtime should expose:
- mock_connector_sandbox_context
- mock_connector_receipts
- execution_evidence
- mock_execution_validation_context
- root_mock_execution_summary_context

These contexts must not expose secrets, raw provider response text as authority, .tmp paths, or real connector command surfaces.

## Stage Map

Recommendation:
Add stage_map entries if low-risk, because they make the route human-readable:
- mock_connector_sandbox
- mock_receipt_collection
- execution_evidence
- mock_execution_validation
- root_mock_execution_summary

If stage_map churn is unexpectedly high, expose result contexts/counters first. The preferred first implementation should still try the explicit stage_map entries.

## Root Mock Execution Summary

Root mock execution summary:
- created only after execution evidence validation
- created_by: root_mock_execution_summary_boundary
- summarizes mock receipts
- confirms real actions did not happen
- does not become payment
- does not become shipment
- does not become connector execution
- Root remains final authority

## DRS Writeback

DRS writeback should record ActionCommitPacket, mock receipts, execution evidence, and Root mock execution summary as local trace only.

Required writeback facts:
- external_global_drs_write: false
- production_persistence_claimed: false

## Required Future Tests

A. Default mode:
- PASS
- all mock sandbox counters zero
- no mock receipts
- no execution evidence
- existing ActionCommitPacket counters zero

B. Sandbox gate without packet gates:
- FAIL_CLOSED
- mock_connector_sandbox_requires_valid_action_commit_packet
- no fake adapter invoked
- no mock receipt
- no execution evidence

C. Sandbox gate with blocked current scenario:
- Root not_ready
- no ActionCommitPacket
- sandbox denied
- no fake adapters
- no receipts/evidence

D. Valid mock-ready sandbox:
- both ActionCommitPacket gates plus mock-ready fixture plus sandbox gate
- one valid Root-created mock_action_commit_packet
- all three fake adapters invoked
- three mock receipts created
- execution evidence created and validated
- Root mock execution summary created
- generic real/external counters remain 0

E. Packet expiry:
- expired packet at deterministic scenario time rejected
- mock_connector_sandbox_packet_expired_count increments
- no adapters run

F. Packet not Root-created:
- packet created_by changed to gemini/orchestrator/architect/executor
- rejected before adapters

G. Packet real_world_effects_allowed true:
- rejected before adapters
- real_world_effects_blocked counter increments

H. Unknown adapter:
- packet asks for unknown future adapter
- rejected
- no adapters run

I. Missing receipt:
- fake adapter omitted or returns no receipt
- execution evidence validation fails
- missing receipt counter increments
- Root mock execution summary not created

J. Duplicate receipt:
- duplicate bank receipt or duplicate adapter name
- rejected
- duplicate receipt counter increments

K. Receipt claims real action:
- fake receipt contains bank_api_called true / payment_executed true / shipment_released true
- rejected
- generic real counters remain 0

L. Connector sandbox does not use network or secrets:
- assert requests/httpx/urllib/socket/subprocess absent
- assert api_key/secret/token/password absent from receipts/evidence

M. Gemini and Fractal cannot bypass packet:
- dual Gemini plus sandbox but no ActionCommitPacket gates fails before fake adapters
- Fractal executor output cannot invoke fake adapters directly
- fake adapters only consume validated packet

N. DRS writeback:
- local trace includes mock receipts/evidence
- external_global_drs_write_count == 0
- production_persistence_claimed_count == 0

O. Existing regressions:
- default Full E2E still PASS
- Dual Gemini tests still PASS
- ActionCommitPacket tests still PASS
- no new real model/network calls from sandbox

## Preflight Answers

1. Can existing Full E2E runner host Mock Connector Sandbox safely?
Yes. The existing runner already owns Root boundary, Root Mock Approval Gate, ActionCommitPacket, counters, stage_map, and local DRS writeback. The sandbox should be added after packet creation and before local writeback.

2. Is a new runner needed?
No. A new runner would create a proof island and weaken the chain of custody from Root to packet to mock evidence.

3. Should fake adapters be prototyped in runner or new core module?
First runtime slice should prototype local deterministic adapters inside `demo/run_full_semantic_e2e_v01.py`. Extract to a core module only after receipt and evidence contracts stabilize.

4. What exact gates are required?
`HEDGEHOG_FULL_E2E_ACTION_COMMIT_PACKET=1`, `HEDGEHOG_FULL_E2E_ROOT_MOCK_APPROVAL=1`, `HEDGEHOG_FULL_E2E_MOCK_READY_FIXTURE=1`, and `HEDGEHOG_FULL_E2E_MOCK_CONNECTOR_SANDBOX=1`.

5. Is dual Gemini required for first runtime?
No. The first runtime should validate packet and sandbox discipline independent of live Gemini.

6. How should packet expiry be validated?
Use deterministic scenario time in v0.1. Reject when scenario time is after packet `expires_at`.

7. What exact receipts are created?
One `mock_bank_payment_review_receipt`, one `mock_supplier_confirmation_receipt`, and one `mock_warehouse_reservation_receipt`.

8. What exact ExecutionEvidence is created?
One `mock_connector_execution_evidence` artifact containing the validated packet references, three mock receipts, scenario time, expiry check, and zero real-world effects.

9. Which counters may become nonzero?
Mock sandbox, fake adapter invoked, fake local connector, mock receipt, execution evidence, validation, and Root mock execution summary counters.

10. Which counters must remain zero?
`connector_called_count: 0`, `payment_executed_count: 0`, `shipment_released_count: 0`, `real_bank_api_called_count: 0`, `real_supplier_api_called_count: 0`, `real_warehouse_api_called_count: 0`, and `action_permission_created_count: 0`.

11. How does Root mock execution summary work?
Root summarizes validated mock receipts and execution evidence after validation. It does not execute, finalize payment, release shipment, or call a real connector.

12. How is DRS writeback updated?
DRS writeback records local trace references for packet, receipts, evidence, validation, and Root mock execution summary. It remains local-only.

13. What tests are required?
Use the A-O list above as the focused test matrix.

14. What comes after Mock Connector Sandbox runtime?
Fractal Order Fulfillment DAG v0.1:
- use valid ActionCommitPacket
- route fake connector work through Fractal executor branches
- compare payment/reservation/supplier confirmation branches
- produce child ResultProposals and mock ExecutionEvidence
- Post V&V / GT-LGT / Root review over branch outcomes

15. Is a separate patch plan required?
No. If this preflight is committed, next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests.

## Verdict

- next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests
- no new runner
- no real connector
- no production claim
- no NeedleFactory
- no Marennya / UP
- Root remains final authority
