# Full Semantic E2E Core Contracts v0.1

document_id: full_semantic_e2e_core_contracts_v01
document_status: CURRENT_CHECKPOINT
based_on_head: d433fa0
production_ready: false
public_wow_ready: false
full_e2e_runner: demo/run_full_semantic_e2e_v01.py
runner_role: integration spine / harness

Core modules:
- hedgehog.action_commit_packet
- hedgehog.mock_connector_sandbox
- hedgehog.fractal_fulfillment

Current hedgehog core baseline:

- `hedgehog.context_packets` contains bounded ContextPacket contracts.
- `hedgehog.structured_rationale` contains canonical structured rationale
  contracts, builders, and validators.
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
- The live semantic reasoning adapter currently lives in the live
  unknown-request spine and is `approved_live_provider_architecture` but
  `pending_core_extraction`.

## 1. What moved to core

The core extraction moved stable contracts out of the Full Semantic E2E integration runner and into reusable `hedgehog/*` modules.

- `hedgehog.action_commit_packet` owns ActionCommitPacket defaults, required fields, builder logic, validation, Root boundary checks, mock-only checks, forbidden-field checks, and Root mock approval precondition validation.
- `hedgehog.mock_connector_sandbox` owns local fake adapter contracts, mock receipt required fields, receipt validators, ExecutionEvidence builder/validator, deterministic scenario-time expiry validation, sandbox packet validation, and adapter registry fail-closed validation.
- `hedgehog.fractal_fulfillment` owns post-Root Fractal Fulfillment branch definitions, child O/A/I topology envelopes, branch context builders/validators, branch ResultProposal builders/validators, parent merge builder/validator, and topology preservation context.

The runner now delegates these mechanics to core functions while remaining the integration spine.

## 2. What stayed in runner

`demo/run_full_semantic_e2e_v01.py` still owns the full supplier-payment route assembly:

- environment gate parsing
- fixture construction and mock-ready mutation
- stage_map integration
- counter aggregation into the Full Semantic E2E report
- DRS writeback wiring
- render/report formatting
- Gemini provider path selection
- orchestration across DRS, CandidateVector, AVF, advisory, Orchestrator, Architect, PlanGraph, Executor, Post V&V, GT/LGT, Root, ActionCommitPacket, Fractal Fulfillment, MockConnectorSandbox, and DRS writeback

The runner is not replaced by a new runner.

## 3. ActionCommitPacket contract

ActionCommitPacket is the Root-created permission artifact for a later mock-only local action attempt.

Exact checkpoint facts:

- ActionCommitPacket is created by root_mock_approval_gate
- Gemini does not create ActionCommitPacket
- created_by: root_mock_approval_gate
- packet_type: mock_action_commit_packet
- action_scope: local_mock_connector_sandbox
- mock_only true
- real_world_effects_allowed false
- ActionCommitPacket is not FinalOutput
- ActionCommitPacket does not execute itself
- idempotency_key derives from root_outcome_id

The validator rejects not-ready Root decisions, mismatched Root outcome IDs, pre-Root packets, non-Root packet creators, unsupported action kinds, and forbidden connector/payment/shipment fields.

## 4. MockConnectorSandbox contract

MockConnectorSandbox consumes only a validated Root-created `mock_action_commit_packet`.

Exact checkpoint facts:

- MockConnectorSandbox is the only fake-adapter execution layer
- fake adapters are local and deterministic
- fake_bank_adapter_v0 records `mock_bank_payment_review_receipt`
- fake_supplier_adapter_v0 records `mock_supplier_confirmation_receipt`
- fake_warehouse_adapter_v0 records `mock_warehouse_reservation_receipt`
- receipts are `mock_only: true`
- receipts have `real_world_effects_allowed: false`
- ExecutionEvidence is created by `mock_connector_sandbox`
- ExecutionEvidence is not FinalOutput
- adapter registry hardening fails closed for missing or non-callable required adapters before any adapter dispatch

The B.1 hardening added explicit registry validation reasons:

- `mock_connector_sandbox_missing_adapter_function:<adapter>`
- `mock_connector_sandbox_invalid_adapter_function:<adapter>`

## 5. FractalFulfillmentTopology contract

FractalFulfillmentTopology is the post-Root mock fulfillment topology layer.

Exact checkpoint facts:

- FractalFulfillmentTopology does not call fake adapters directly
- FractalFulfillmentTopology routes branch topology and maps sandbox receipts to branch ResultProposals
- child branches do not create Root / FinalOutput / ActionCommitPacket
- payment_review_branch maps to fake_bank_adapter_v0 and mock_bank_payment_review_receipt
- supplier_confirmation_branch maps to fake_supplier_adapter_v0 and mock_supplier_confirmation_receipt
- warehouse_reservation_branch maps to fake_warehouse_adapter_v0 and mock_warehouse_reservation_receipt
- parent merge verifies missing, duplicate, unknown, and mismatched branch outputs

This is topology preservation, not child sovereignty.

## 6. Full route from evidence to Root to mock fulfillment

The current Full Semantic E2E route is:

SemanticEvidenceClaim -> DRS candidate context -> CandidateVector -> AVF/advisory -> bounded Orchestrator -> bounded Architect -> validated PlanGraph -> pre-Root Fractal executor -> ResultProposal -> Post V&V -> GT/LGT -> Root FinalOutput boundary -> Root Mock Approval Gate -> ActionCommitPacket candidate -> FractalFulfillmentTopology -> MockConnectorSandbox -> mock receipts -> mock_connector_execution_evidence -> mock execution validation -> Root mock execution summary -> DRS writeback.

Dual Gemini can participate as bounded proposal roles in the Orchestrator and Architect stages. Local validators still control what proceeds.

## 7. Safety ledger counters

The smoke evidence records:

- connector_called_count remains 0
- connector_called_count remains zero
- payment_executed_count remains 0
- shipment_released_count remains 0
- real_bank_api_called_count remains 0
- real_supplier_api_called_count remains 0
- real_warehouse_api_called_count remains 0
- action_permission_created_count remains 0
- root_final_authority_preserved_count remains 1 in the smoke evidence

`fake_*_connector_called_count may rise` because those counters represent local fake sandbox calls. `connector_called_count` remains the real/external connector safety ledger counter.

## 8. Authority boundaries

Root remains final authority.

- Gemini proposes route and plan artifacts only.
- Orchestrator is not Root.
- Architect is not Root.
- Executor returns ResultProposal only.
- Post V&V validates but does not finalize.
- GT/LGT reviews but does not finalize.
- ActionCommitPacket is not FinalOutput.
- ExecutionEvidence is not FinalOutput.
- Root mock execution summary records a local fake outcome and does not become payment or shipment.

## 9. Fractal O/A/I topology preservation

Each fulfillment branch preserves a bounded local topology:

- child_orchestrator: bounded_branch_router
- child_architect: bounded_branch_plan
- child_executor: mock_sandbox_task_executor
- returns_to_parent: true
- child_root_created: false
- child_final_output_created: false
- child_action_commit_packet_created: false
- connector_bypass_attempted: false
- real_world_effects_allowed: false

Parent merge validates that all branches return upward and that no branch claims authority it does not have.

## 10. Why Gemini is bounded

Gemini is bounded because it participates only as proposal roles:

- Gemini Orchestrator proposes a route.
- Local route validation checks the Orchestrator proposal.
- Gemini Architect proposes a PlanGraph.
- Local PlanGraph contract validation checks the Architect proposal.
- Gemini does not create ActionCommitPacket.
- Gemini does not call adapters.
- Gemini does not create FinalOutput.

## 11. Why sandbox fake calls are not real connector calls

The sandbox adapters are local deterministic functions. They do not use real bank, supplier, or warehouse APIs.

The important counter distinction is:

- `fake_*_connector_called_count may rise`
- `connector_called_count remains zero`

The first tracks local fake sandbox activity. The second tracks real/external connector use and remains zero in the smoke evidence.

## 12. DRS writeback boundary

DRS writeback remains local trace/audit persistence only.

Recorded smoke facts:

- local_writeback_only: true
- external_global_drs_write: false
- production_persistence_claimed: false
- has_fractal_order_fulfillment_trace: true
- has_fulfillment_branch_result_proposals_trace: true
- has_fulfillment_branch_merge_trace: true
- has_execution_evidence_trace: true
- has_root_mock_execution_summary_trace: true

## 13. Current limitations

- not production
- not public WOW ready yet
- still local mock sandbox fulfillment
- Gemini/PlanGraph context remains intentionally bounded/simple
- no real connector, payment, shipment, or API call occurs
- no NeedleFactory, Marennya, or UP activation is part of this checkpoint
- later core contracts for bounded ContextPackets and canonical structured
  rationale are implemented in `hedgehog.context_packets` and
  `hedgehog.structured_rationale`; this d433fa0 document remains the
  Action/Mock/Fractal core-contract checkpoint
- not NeedleFactory / Marennya / UP

## 14. What comes next

Historical next engineering direction from this checkpoint:

- Rich Context / Bounded Context Packets preflight

Current next direction after Real Gemini Unknown Request 007 is core extraction
preflight for `semantic_reasoning_adapter`, followed by
BoundedSemanticEvidencePacket Orchestrator -> Architect. This should still
avoid NeedleFactory, Marennya, UP, real connectors, and production claims.
