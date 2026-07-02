# HEDGEHOG OS — Public WOW Core-Extracted Fractal Fulfillment Walkthrough v0.1

document_status: CURRENT_CHECKPOINT_WALKTHROUGH
based_on_head: d433fa0
production_ready: false
public_wow_ready: false

This walkthrough describes the current core-extracted Full Semantic E2E route. It is honest about scope: not production and not public WOW ready yet.

The story in one line:

Gemini proposes, Root disposes. Root remains final authority.

## Current hedgehog core baseline

This walkthrough remains a valid closed Action + Mock + Fractal core extraction
walkthrough. It is not a replacement for the full current core baseline.

Current hedgehog core baseline:

- `hedgehog.context_packets` contains bounded ContextPacket contracts.
- `hedgehog.structured_rationale` contains canonical structured rationale
  contracts, builders, and validators.
- `hedgehog.semantic_reasoning_adapter` contains stable semantic reasoning
  provider contracts, required field constants, reasoning field normalization
  and validation, conversion from provider semantic reasoning into canonical
  structured rationales, safe local advisory PlanGraph node builders, provider
  claim boolean preservation for downstream validators, and no
  Gemini/provider/network/runtime imports.
- `hedgehog.action_commit_packet` contains the Root-created/mock-only
  ActionCommitPacket contract.
- `hedgehog.mock_connector_sandbox` contains the fake-adapter/local-only
  sandbox contract.
- `hedgehog.fractal_fulfillment` contains the child branch / fulfillment
  topology contract.

Rich Context / Structured Rationale core checkpoint:

- `hedgehog.context_packets`
- `tests/test_context_packets_core.py`
- `hedgehog.structured_rationale`
- `tests/test_structured_rationale_core.py`
- ContextPacket is not truth.
- ContextPacket is not authority.
- structured rationale is explanation only.
- Root remains final authority.

Current integration/live spine:

- `demo/run_full_semantic_e2e_v01.py` remains an integration harness /
  integration spine.
- `demo/run_live_unknown_request_dual_rich_context_v01.py` is the current live
  unknown-request provider spine.
- These demo runners are not the same as `hedgehog` core modules.
- `semantic_reasoning_adapter` status is now
  `approved_live_provider_architecture`, `core_extracted`,
  `runner_delegated`, and `slice_c_audited`.
- `demo/run_live_unknown_request_dual_rich_context_v01.py` delegates semantic
  adapter mechanics to `hedgehog.semantic_reasoning_adapter`.
- The live runner still owns Gemini/provider/env/prompt/timeout/pre-delay/
  orchestration behavior, the 007 integration policy, and prompt policy.
- Core does not own Gemini or network.

## Card 1. Business request

A supplier-payment and shipment review arrives with mixed evidence:

- invoice INV-2042 looks payable
- shipment SH-2042 has fulfillment constraints
- legal and stock facts must still be checked

The system treats this as a semantic evidence problem, not as permission to act.

## Card 2. Candidate evidence / DRS / AVF

The runtime builds candidate evidence and runs it through DRS candidate context, CandidateVector generation, AVF scoring, and advisory review.

Important boundary:

- evidence is not truth by itself
- AVF is advisory
- hard masks can block risky signals
- Root remains final authority

## Card 3. Gemini Orchestrator

Two real Gemini roles can participate as bounded proposal roles.

The Gemini Orchestrator proposes a route. Local route validation checks that proposal before anything downstream can rely on it.

Boundary:

- Orchestrator is not Root
- Orchestrator does not create ActionCommitPacket
- Orchestrator does not call adapters
- Orchestrator does not create FinalOutput

## Card 4. Gemini Architect

The Gemini Architect proposes a PlanGraph. Local PlanGraph contract validation checks it before execution.

Boundary:

- Architect is not Root
- Architect is not Executor
- Architect does not create ActionCommitPacket
- Architect does not call adapters
- Architect does not create FinalOutput

## Card 5. Root Mock Approval

Post V&V and GT/LGT return upward. Root reviews the outcome and, only in the explicit mock-ready path, approves a mock-only action attempt packet.

Root remains final authority.

## Card 6. ActionCommitPacket

ActionCommitPacket is created by root_mock_approval_gate.

The packet records:

- packet_type: mock_action_commit_packet
- created_by: root_mock_approval_gate
- mock_only true
- real_world_effects_allowed false
- action_scope: local_mock_connector_sandbox

Gemini does not create ActionCommitPacket.

## Card 7. Fractal child O/A/I branches

Fractal Fulfillment expands into three child O/A/I branches:

- payment_review_branch
- supplier_confirmation_branch
- warehouse_reservation_branch

Each branch preserves local topology:

- child Orchestrator routes a branch only
- child Architect proposes a bounded branch plan only
- child Executor returns branch evidence upward only

Child branch is not Root.

Branches do not create Root, FinalOutput, or ActionCommitPacket.

## Card 8. MockConnectorSandbox receipts

MockConnectorSandbox is the only fake-adapter execution layer.

FractalFulfillmentTopology does not call fake adapters directly. It routes topology and maps sandbox receipts.

The sandbox records:

- mock_bank_payment_review_receipt
- mock_supplier_confirmation_receipt
- mock_warehouse_reservation_receipt

Mock receipt is not real payment.

`fake_*_connector_called_count may rise` because the sandbox calls local fake adapter functions. `connector_called_count remains zero` because that counter represents real/external connector use.

## Card 9. ExecutionEvidence

ExecutionEvidence records the sandbox outcome:

- evidence_type: mock_connector_execution_evidence
- created_by: mock_connector_sandbox
- receipt_count: 3
- connector_sandbox_completed: true
- real_connector_called: false
- payment_executed: false
- shipment_released: false

ExecutionEvidence is not FinalOutput.

## Card 10. Root mock execution summary

Root mock execution summary records the local fake outcome:

- decision: mock_execution_recorded
- reason: local fake connector receipts recorded; no real-world action occurred
- receipt_count: 3
- real_actions_executed: false
- connector_called: false

The summary records what happened in the sandbox. It does not become payment, shipment, or production behavior.

## Card 11. Safety ledger

The checkpoint smoke evidence records:

- dual_gemini_model_call_count: 2 in the dual-Gemini extracted-core smoke
- live_model_call_count: 2 in the dual-Gemini extracted-core smoke
- fractal_order_fulfillment_dag_completed_count: 1
- fulfillment_child_cells_started_count: 3
- fulfillment_child_root_created_count: 0
- fulfillment_child_final_output_created_count: 0
- fulfillment_child_action_commit_packet_created_count: 0
- mock_connector_sandbox_completed_count: 1
- mock_receipt_created_count: 3
- execution_evidence_created_count: 1
- root_mock_execution_summary_created_count: 1
- connector_called_count remains zero
- payment_executed_count remains 0
- shipment_released_count remains 0
- real_bank_api_called_count remains 0
- action_permission_created_count remains 0
- root_final_authority_preserved_count: 1

## Card 12. What this is not

- not production
- not public WOW ready yet
- not real connector integration
- not real payment movement
- not real shipment release
- not real bank, supplier, or warehouse API use
- not autonomous external execution
- not NeedleFactory
- not Marennya / UP
- not a public WOW ready claim

## Card 13. Why this remains a closed core-extraction walkthrough

This remains a valid closed walkthrough because the architecture shows the full
controlled chain with extracted Action/Mock/Fractal core contracts:

- two real Gemini roles can participate as bounded proposal roles
- Orchestrator proposes route
- Architect proposes PlanGraph
- local validators accept bounded proposals
- Root creates mock_action_commit_packet
- Fractal Fulfillment expands into three child O/A/I branches
- MockConnectorSandbox records three local fake receipts
- ExecutionEvidence records sandbox outcome
- Root mock execution summary records local fake outcome
- DRS writeback stores local trace
- no real connector/payment/shipment/API call occurred

The important change is that the proven contracts no longer live only inside the integration runner. They now have reusable core homes:

- hedgehog.action_commit_packet
- hedgehog.mock_connector_sandbox
- hedgehog.fractal_fulfillment

The current live-provider checkpoint is Real Gemini Unknown Request 007:
`manual-live-unknown-request-real-gemini-007`,
`auditor_live_unknown_request_real_gemini_007_v01`,
`semantic_reasoning_adapter`, `json_mime_only`, Root decision
`needs_more_evidence`, and `real_world_effects_count: 0`.

## Card 14. What comes next

Historical next recommended direction:

- Rich Context / Bounded Context Packets preflight

That core work now exists in `hedgehog.context_packets` and
`hedgehog.structured_rationale`. `hedgehog.semantic_reasoning_adapter` is now
core-extracted and delegated from the live unknown-request runner. Current next
direction is BoundedSemanticEvidencePacket Orchestrator -> Architect preflight.

The next layer should keep the same authority topology:

- Gemini proposes, Root disposes.
- Root remains final authority.
- Child branch is not Root.
- Mock receipt is not real payment.
- ExecutionEvidence is not FinalOutput.
