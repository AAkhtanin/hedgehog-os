# Core Extraction: ActionCommitPacket + Mock Connector + Fractal Fulfillment Preflight v0.1

preflight_id: core_extraction_action_mock_fractal_preflight_v01
preflight_status: COMPLETE
base_head: d0ebf82
planning_only: true
runtime_created: false
tests_created: false
audit_log_created: false
core_modules_created: false
core_modules_modified: false
public_wow_ready: false
production_ready: false
new_runner_required: false
existing_full_e2e_runner_remains_source_of_truth: true
semantic_behavior_change_allowed: false
commit_created: false

## Purpose

Plan how to extract proven universal contracts out of `demo/run_full_semantic_e2e_v01.py` while preserving behavior exactly.

This extraction must not change semantics, create a new proof island, create a new runner, make public-WOW or production claims, introduce real connectors, real payments, real shipments, Gemini calls, model calls, network calls, NeedleFactory, Marennya, or UP.

Core extraction thesis:
The demo runner should remain the Full Semantic E2E spine and integration harness. Stable contracts and validators should move to `hedgehog/*`. The runner should call core functions instead of owning all mechanics.

## Source Of Truth Inspected

Committed durable sources:
- `demo/run_full_semantic_e2e_v01.py`
- `tests/test_full_semantic_e2e_v01_runner.py`
- `docs/audit_reports/auditor_action_commit_packet_root_mock_approval_gate_runtime_v01.log`
- `docs/audit_reports/auditor_mock_connector_sandbox_runtime_v01.log`
- `docs/audit_reports/auditor_fractal_order_fulfillment_dag_runtime_v01.log`
- `docs/audit_reports/auditor_dual_gemini_fractal_fulfillment_composition_v01.log`
- `docs/action_commit_packet_root_mock_approval_gate_preflight_v01.md`
- `docs/mock_connector_sandbox_preflight_v01.md`
- `docs/fractal_order_fulfillment_dag_preflight_v01.md`
- `docs/public_wow_dual_gemini_walkthrough_v01.md`

No `.tmp` artifact is required for this preflight. Committed audit logs are the durable source of truth.

Closed evidence now proves:
- two real Gemini roles can participate as bounded proposal roles
- Root can create `mock_action_commit_packet`
- Mock Connector Sandbox can create 3 mock receipts and ExecutionEvidence
- Fractal Order Fulfillment DAG can preserve child O/A/I topology
- real/external counters remain zero

## Extraction Principles

- preserve exact current default behavior
- preserve current output shape unless explicitly audited
- preserve current counters
- preserve current stage_map statuses
- preserve current fail-closed behavior
- preserve current manual smoke meanings
- no real/external action
- no new model/network/Gemini calls
- no production claims
- no public-WOW-readiness claims
- no NeedleFactory
- no Marennya / UP
- no new runner
- prevent output shape drift and counter drift with focused regression tests

## Extraction Candidates

### 1. ActionCommitPacket core extraction

Candidate future file:
- `hedgehog/action_commit_packet.py`

Move only stable reusable pieces:
- ActionCommitPacket required fields
- allowed/forbidden action kinds
- fake adapter allowlist / real adapter denylist
- packet shape builder when generic enough
- packet validator
- Root boundary consistency checks
- mock-only / `real_world_effects_allowed` checks
- forbidden packet field checks
- expiry field policy helpers
- validator receipt checks

Keep in the integration runner:
- Full E2E env gate parsing
- supplier-payment fixture-specific mock-ready facts unless safely abstracted
- runner result rendering
- runner counters application
- `.tmp` smoke logic

Planned public functions:
- `build_mock_action_commit_packet(...)`
- `validate_action_commit_packet(...)`
- `action_commit_packet_default()`
- `root_mock_approval_context_default()`
- `validate_root_mock_approval_preconditions(...)`

Dataclass decision:
Use plain dict-compatible builders/validators first. The current evidence, tests, reports, and smoke summaries depend on dict-shaped artifacts. Dataclasses can be considered after a separate output-shape audit.

### 2. MockConnectorSandbox core extraction

Candidate future file:
- `hedgehog/mock_connector_sandbox.py`

Move only stable reusable pieces:
- fake adapter names
- mock receipt required fields
- ExecutionEvidence required fields
- `fake_bank_adapter_v0`
- `fake_supplier_adapter_v0`
- `fake_warehouse_adapter_v0`
- mock receipt validators
- execution evidence builder
- execution evidence validator
- sandbox packet validation
- deterministic scenario-time expiry validation

Keep in the integration runner:
- env gate parsing
- runner stage_map integration
- runner report rendering
- DRS writeback integration
- supplier-payment fixture construction unless safely abstracted

Planned public functions:
- `fake_bank_adapter_v0(...)`
- `fake_supplier_adapter_v0(...)`
- `fake_warehouse_adapter_v0(...)`
- `validate_mock_receipt(...)`
- `build_mock_connector_execution_evidence(...)`
- `validate_mock_connector_execution_evidence(...)`
- `run_mock_connector_sandbox(...)`

Counter distinction to preserve:
- `fake_*_connector_called_count` may rise for local/fake sandbox calls
- `connector_called_count` must remain 0 for real/external connector use
- `payment_executed_count` must remain 0
- `shipment_released_count` must remain 0
- `real_*_api_called_count` must remain 0

### 3. FractalFulfillmentTopology core extraction

Candidate future file:
- `hedgehog/fractal_fulfillment.py`

Move only stable reusable pieces:
- branch definitions
- child O/A/I topology envelope
- branch context builder
- branch topology validator
- branch ResultProposal builder
- branch ResultProposal validator
- parent merge builder
- parent merge validator
- forbidden branch connector/API claim checks
- DRS write claim checks
- topology preservation summary

Keep in existing modules/runner:
- pre-Root fractal executor remains in `hedgehog/fractal_dag_executor.py`
- Gemini provider logic remains in the integration runner lane
- runner env gates remain in the runner
- runner stage_map rendering remains in the runner
- DRS writeback integration remains in the runner

Planned public functions:
- `build_fulfillment_branch_contexts(...)`
- `validate_fulfillment_branch_topology(...)`
- `build_fulfillment_branch_result_proposals(...)`
- `validate_fulfillment_branch_result_proposals(...)`
- `build_fulfillment_merge_context(...)`
- `validate_fulfillment_merge_context(...)`
- `run_fractal_order_fulfillment_dag(...)`

Two fractal layers must remain distinct:
- existing pre-Root Fractal executor remains in `hedgehog/fractal_dag_executor.py`
- post-Root Fractal Fulfillment topology goes to `hedgehog/fractal_fulfillment.py`

### 4. Optional common authority/boundary helper

Candidate future file:
- `hedgehog/authority_boundaries.py`

Evaluate only.

Reusable pieces may include:
- forbidden authority claim keys
- forbidden action claim keys
- forbidden connector claim keys
- forbidden DRS write claim keys
- helper for detecting truthy forbidden claim keys

Recommendation:
Do not extract this first unless it reduces duplication without changing behavior. Focus first on ActionCommitPacket, MockConnectorSandbox, and FractalFulfillmentTopology.

## Context Enrichment Boundary

Richer Gemini/PlanGraph context comes after core extraction.

Do not enrich Gemini context or PlanGraph in this extraction. Do not add richer prompts, new Gemini roles, or new PlanGraph capabilities.

Future context work should introduce bounded context packets, not raw dumps:
- EvidenceContextPacket
- DRSCandidateContextPacket
- AVFAttractorPacket
- RouteDecisionContext
- PlanGraphContext
- ActionCommitPacketContext
- MockReceipt / ExecutionEvidence context
- FractalBranchContext
- CapabilityRequestContext

Reason:
Richer context should be passed through validated core contracts, not directly from the integration runner.

## Recommended Extraction Order

### Slice A

ActionCommitPacket core extraction.

Likely future files:
- `hedgehog/action_commit_packet.py`
- `tests/test_action_commit_packet_core.py`
- `demo/run_full_semantic_e2e_v01.py`
- `tests/test_full_semantic_e2e_v01_runner.py`

Goal:
Runner delegates ActionCommitPacket builder, validator, and default contexts to core. Behavior unchanged.

### Slice B

MockConnectorSandbox core extraction.

Likely future files:
- `hedgehog/mock_connector_sandbox.py`
- `tests/test_mock_connector_sandbox_core.py`
- `demo/run_full_semantic_e2e_v01.py`
- `tests/test_full_semantic_e2e_v01_runner.py`

Goal:
Runner delegates fake adapters, receipt validators, and execution evidence validator to core. Behavior unchanged.

### Slice C

FractalFulfillmentTopology core extraction.

Likely future files:
- `hedgehog/fractal_fulfillment.py`
- `tests/test_fractal_fulfillment_core.py`
- `demo/run_full_semantic_e2e_v01.py`
- `tests/test_full_semantic_e2e_v01_runner.py`

Goal:
Runner delegates branch topology, branch proposals, and parent merge validators to core. Behavior unchanged.

### Slice D Optional

Common authority/boundary helper extraction.

Only proceed if Slices A-C reveal duplication that can be removed without output shape drift or counter drift.

## Testing Strategy

For each extraction slice:
- keep existing Full E2E focused suite passing
- add small direct core tests for module-level validators/builders
- run default CLI
- run current focused regression suites
- run smoke only after all slices or when needed
- forbid output shape drift unless explicitly planned
- forbid counter drift unless explicitly planned

Core tests should assert:
- valid packet accepted
- `not_ready` Root rejected
- missing packet field rejected
- packet from Gemini rejected
- valid mock receipt accepted
- missing false flag rejected
- execution evidence mismatch rejected
- valid branch topology accepted
- child Root / FinalOutput / ActionCommitPacket rejected
- connector/API claim rejected
- DRS write claim rejected
- parent merge missing / duplicate / wrong receipt rejected

Manual smoke after extraction:
- deterministic Fractal Fulfillment smoke
- Dual Gemini + Fractal Fulfillment + Mock Connector Sandbox composition smoke

Expected smoke invariants:
- `final_status: PASS`
- dual Gemini composition still has `dual_gemini_model_call_count: 2`
- ActionCommitPacket still `created_by: root_mock_approval_gate`
- Fractal Fulfillment still has 3 child branches
- `mock_receipt_created_count: 3`
- `execution_evidence_created_count: 1`
- `connector_called_count: 0`
- `payment_executed_count: 0`
- `shipment_released_count: 0`
- `real_bank_api_called_count: 0`
- Root remains final authority

## Preflight Answers

1. What exactly should move to core?
Stable packet builders/validators, mock adapter receipt/evidence contracts, and Fractal Fulfillment branch topology/merge validators should move to core.

2. What must stay in the integration runner?
Env gates, supplier-payment fixtures, rendering, stage_map wiring, counter aggregation, DRS writeback integration, and smoke/report presentation should stay in the runner.

3. Is a new runner needed?
No. The existing Full Semantic E2E runner remains the integration harness.

4. Should extraction be one big patch or slices?
Use slices. One big patch would make semantic drift harder to isolate.

5. Which slice should be first?
Slice A ActionCommitPacket core extraction should be first because MockConnectorSandbox and FractalFulfillmentTopology both depend on a validated Root-created packet.

6. Which future files are expected?
Expected future files are `hedgehog/action_commit_packet.py`, `hedgehog/mock_connector_sandbox.py`, `hedgehog/fractal_fulfillment.py`, and focused core test files for each slice.

7. Which existing output shapes must remain stable?
`action_commit_packet`, `root_mock_approval_context`, `mock_connector_sandbox_context`, `mock_connector_receipts`, `execution_evidence`, `root_mock_execution_summary_context`, `fractal_order_fulfillment_context`, `fulfillment_branch_contexts`, `fulfillment_branch_result_proposals`, `fulfillment_merge_context`, `topology_preservation_context`, stage_map entries, and DRS writeback trace fields must remain stable.

8. Which counters must remain stable?
ActionCommitPacket counters, MockConnectorSandbox counters, Fractal Fulfillment counters, real/external safety counters, dual Gemini counters, and aggregate model/network counters must remain stable unless a later audit explicitly approves counter drift.

9. Which tests are required?
Existing Full E2E tests must pass, and direct core tests must cover valid and invalid packet, receipt, evidence, branch topology, branch proposal, and parent merge cases.

10. How do we prevent semantic drift during extraction?
Use a one-slice-at-a-time migration, keep dict-compatible output shapes, compare runner outputs before/after, preserve counters and stage_map statuses, and keep all fail-closed reasons unchanged.

11. When should richer Gemini/PlanGraph context be added?
Richer Gemini/PlanGraph context comes after core extraction begins or completes. It should use bounded context packets routed through core validators.

12. What is the next exact implementation step?
Next approved implementation: Slice A ActionCommitPacket core extraction.

13. Is a separate patch plan required?
No separate patch plan is required. Slice A should be implemented directly with focused tests and behavior-preservation checks.

## Verdict

- next approved implementation: Slice A ActionCommitPacket core extraction
- no new runner
- no context enrichment yet
- no production claim
- no public-WOW-readiness claim
- no NeedleFactory
- no Marennya / UP
- richer Gemini / PlanGraph context only after core extraction begins or completes
