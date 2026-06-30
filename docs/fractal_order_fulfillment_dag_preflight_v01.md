# Fractal Order Fulfillment DAG v0.1 Preflight

preflight_id: fractal_order_fulfillment_dag_preflight_v01
preflight_status: COMPLETE
base_head: fbe634f
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

Plan the next runtime layer where mock connector work is routed through a bounded Fractal Order Fulfillment DAG instead of only through linear sandbox dispatch.

This layer is not real payment, real shipment, real bank API, real supplier API, real warehouse API, production, NeedleFactory, Marennya / UP, autonomous external execution, free-form Gemini-to-Gemini execution, or a new proof island.

Core thesis:
Fractalization without authority loss is possible only when topology is preserved. Each child branch can plan and execute a bounded local mock task, but it must return a child ResultProposal / branch receipt upward. Parent merge, Post V&V, GT/LGT, and Root remain downstream. Root remains final authority.

## Source Facts Inspected

Durable committed sources:
- docs/mock_connector_sandbox_preflight_v01.md
- docs/audit_reports/auditor_mock_connector_sandbox_runtime_v01.log
- docs/action_commit_packet_root_mock_approval_gate_preflight_v01.md
- docs/audit_reports/auditor_action_commit_packet_root_mock_approval_gate_runtime_v01.log
- docs/audit_reports/auditor_dual_gemini_orchestrator_architect_runtime_v01.log
- docs/public_wow_dual_gemini_walkthrough_v01.md
- demo/run_full_semantic_e2e_v01.py
- tests/test_full_semantic_e2e_v01_runner.py
- hedgehog/fractal_dag_executor.py
- hedgehog/architect.py
- hedgehog/llm_architect.py
- specs/demo_baseline_v0_25.md

Strategic note:
The exact requested Russian-title strategic files were not present as repo paths found by file search. Existing committed fractal topology evidence is present in `specs/demo_baseline_v0_25.md` and the fractal cell runtime/audit files. The relevant source fact is that a child cell may run child Orchestrator / child Architect / child Executor, but returns a ChildBoundarySnapshot upward and never becomes Root.

Current closed stack:
- Full Semantic E2E closed.
- Dual Gemini Orchestrator+Architect closed.
- ActionCommitPacket / Root Mock Approval Gate closed.
- Mock Connector Sandbox closed.
- Mock Connector Sandbox audit closed at fbe634f.
- Current system can create a Root-created mock_action_commit_packet.
- Current system can run local fake bank / supplier / warehouse adapters.
- Current system can create 3 mock receipts.
- Current system can create and validate mock_connector_execution_evidence.
- Current system can create Root mock execution summary.
- Real/external counters remain zero.

Current durable safety facts:
- mock_receipt_created_count: 3
- execution_evidence_created_count: 1
- connector_called_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- real_bank_api_called_count: 0
- real_supplier_api_called_count: 0
- real_warehouse_api_called_count: 0
- action_permission_created_count: 0
- Root remains final authority

## Two Fractal Layers

There are now two Fractal meanings in the Full E2E runner and they must remain distinct.

Existing pre-Root planning Fractal executor:
- consumes validated PlanGraph
- creates ResultProposal
- does not execute connectors
- does not create FinalOutput
- remains upstream of Post V&V, GT/LGT, and Root

New post-Root mock fulfillment Fractal DAG:
- runs only after Root-created ActionCommitPacket
- consumes only a validated Root-created mock_action_commit_packet
- routes fake connector sandbox work across branches
- may produce mock receipts and execution evidence only through Mock Connector Sandbox
- cannot create FinalOutput
- cannot call real connectors
- cannot bypass Root

The new layer is post-Root mock fulfillment. It is not a replacement for `hedgehog.fractal_dag_executor.run_fractal_dag_executor`.

## Canonical Future Placement

SemanticEvidenceClaim
-> DRS candidate context
-> CandidateVector
-> AVF/advisory
-> Gemini Orchestrator / validated route
-> Gemini Architect / validated PlanGraph
-> pre-Root Fractal executor
-> ResultProposal
-> Post V&V
-> GT/LGT
-> Root FinalOutput boundary
-> Root Mock Approval Gate
-> ActionCommitPacket candidate
-> Fractal Order Fulfillment DAG
   -> payment-review child branch
   -> supplier-confirmation child branch
   -> warehouse-reservation child branch
   -> parent merge
-> Mock Connector Sandbox adapter execution
-> mock receipts
-> mock_connector_execution_evidence
-> mock execution validation
-> Root mock execution summary
-> DRS writeback

Important boundary:
The Fractal Order Fulfillment DAG may orchestrate branch work, but the Mock Connector Sandbox remains the only layer that invokes fake adapters. No branch may invoke fake_bank_adapter_v0, fake_supplier_adapter_v0, or fake_warehouse_adapter_v0 directly outside the validated sandbox contract. No branch may call real connectors.

## Future Gate

New env gate to evaluate:
- HEDGEHOG_FULL_E2E_FRACTAL_ORDER_FULFILLMENT_DAG=1

Required gate composition:
Fractal Order Fulfillment DAG may run only when all are true:
- HEDGEHOG_FULL_E2E_ACTION_COMMIT_PACKET=1
- HEDGEHOG_FULL_E2E_ROOT_MOCK_APPROVAL=1
- HEDGEHOG_FULL_E2E_MOCK_READY_FIXTURE=1
- HEDGEHOG_FULL_E2E_MOCK_CONNECTOR_SANDBOX=1
- HEDGEHOG_FULL_E2E_FRACTAL_ORDER_FULFILLMENT_DAG=1

Dual Gemini is not required for the first Fractal Order Fulfillment runtime.

Recommendation:
- first runtime should be deterministic/local
- it should validate topology and branch execution discipline independent of live Gemini
- dual Gemini + Fractal fulfillment should be a later composition smoke

## Gate Behavior

1. Default mode:
- unchanged PASS
- all Fractal Order Fulfillment counters zero
- no new branch contexts
- no new model/network calls

2. Fractal fulfillment gate without valid ActionCommitPacket:
- FAIL_CLOSED
- validation_errors includes fractal_order_fulfillment_requires_valid_action_commit_packet
- no branch starts
- no fake adapters
- no receipts/evidence

3. Fractal fulfillment gate without Mock Connector Sandbox gate:
- FAIL_CLOSED
- validation_errors includes fractal_order_fulfillment_requires_mock_connector_sandbox
- no branch starts
- no fake adapters

4. Fractal fulfillment gate with blocked current scenario:
- Root decision remains not_ready
- no ActionCommitPacket
- no Fractal Order Fulfillment DAG
- no fake adapters
- no receipts/evidence

5. Valid mock-ready Fractal fulfillment:
- valid Root-created mock_action_commit_packet exists
- Mock Connector Sandbox gate is enabled
- Fractal Order Fulfillment DAG invoked
- three child branches start:
  - payment_review_branch
  - supplier_confirmation_branch
  - warehouse_reservation_branch
- each branch preserves child topology
- each branch returns upward
- parent merge validates branch outputs
- Mock Connector Sandbox produces the same 3 mock receipts
- ExecutionEvidence is created and validated
- Root mock execution summary is created
- real/external counters remain zero

## Runtime Shape Recommendation

Use the existing Mock Connector Sandbox as the actual fake-adapter execution layer.

The safer first runtime shape:
1. Validate the Root-created mock_action_commit_packet.
2. Build deterministic branch topology envelopes for payment, supplier, and warehouse branches.
3. Validate that each child branch has child Orchestrator, child Architect, and child Executor markers but no child Root authority.
4. Invoke the existing Mock Connector Sandbox once.
5. Map each sandbox receipt to the matching branch result proposal.
6. Validate branch result proposals and parent merge.
7. Pass merged branch evidence to mock execution validation / Root mock execution summary.

This avoids duplicating fake adapter logic, avoids bypassing existing sandbox validators, and keeps branch execution subordinate to the packet and Root boundary.

## Child Topology Envelope

Each branch should have a minimal local topology envelope:
- child_cell_id
- parent_fractal_id
- child_role_topology:
  - child_orchestrator: bounded_branch_router
  - child_architect: bounded_branch_plan
  - child_executor: mock_sandbox_task_executor
- input_packet_id
- allowed_adapter
- allowed_action_kind
- branch_task
- branch_status
- produced_receipt_type
- returns_to_parent: true
- creates_final_output: false
- creates_action_commit_packet: false
- root_authority_claimed: false
- connector_bypass_attempted: false
- real_world_effects_allowed: false

This is topology preservation, not independent child sovereignty.

Human-readable topology terms:
- child Orchestrator proposes branch routing only.
- child Architect proposes a bounded branch plan only.
- child Executor returns branch evidence upward only.

## Branch Definitions

payment_review_branch:
- branch_id: fulfillment_branch:payment_review
- allowed_adapter: fake_bank_adapter_v0
- allowed_action_kind: mock_supplier_payment_review
- expected_receipt_type: mock_bank_payment_review_receipt
- expected_status: mock_payment_review_recorded

supplier_confirmation_branch:
- branch_id: fulfillment_branch:supplier_confirmation
- allowed_adapter: fake_supplier_adapter_v0
- allowed_action_kind: mock_supplier_payment_review
- expected_receipt_type: mock_supplier_confirmation_receipt
- expected_status: mock_supplier_review_recorded
- note: supplier confirmation is tied to the payment-review side of this first mock fulfillment slice; shipment-reservation expansion can be considered later if the packet action taxonomy is expanded.

warehouse_reservation_branch:
- branch_id: fulfillment_branch:warehouse_reservation
- allowed_adapter: fake_warehouse_adapter_v0
- allowed_action_kind: mock_shipment_reservation_review
- expected_receipt_type: mock_warehouse_reservation_receipt
- expected_status: mock_reservation_review_recorded

## Parent Merge

merge_id: fulfillment_merge:mock_connector_receipts

Parent merge must:
- consume 3 branch outputs
- verify no duplicate branch
- verify no missing branch
- verify no unknown branch
- verify each branch returned upward
- verify each branch receipt matches expected adapter/receipt type
- create no FinalOutput
- pass merged branch evidence to mock execution validation / Root summary

## Result Contexts

Future result contexts to expose:
- fractal_order_fulfillment_context
- fulfillment_branch_contexts
- fulfillment_branch_result_proposals
- fulfillment_merge_context
- topology_preservation_context

## Stage Map

Expected stage_map entries after action_commit_packet_candidate:
- fractal_order_fulfillment_dag
- fulfillment_payment_review_branch
- fulfillment_supplier_confirmation_branch
- fulfillment_warehouse_reservation_branch
- fulfillment_branch_merge

Add them if low-risk. If stage map churn becomes noisy, contexts and counters are acceptable for the first patch, but stage entries are preferred because they make the route human-readable.

## Counters To Add

Fractal fulfillment counters:
- fractal_order_fulfillment_dag_invoked_count
- fractal_order_fulfillment_dag_completed_count
- fractal_order_fulfillment_dag_denied_count
- fractal_order_fulfillment_requires_packet_count
- fractal_order_fulfillment_requires_sandbox_count
- fulfillment_child_cells_started_count
- fulfillment_child_cells_completed_count
- fulfillment_payment_branch_started_count
- fulfillment_payment_branch_completed_count
- fulfillment_supplier_branch_started_count
- fulfillment_supplier_branch_completed_count
- fulfillment_warehouse_branch_started_count
- fulfillment_warehouse_branch_completed_count
- fulfillment_branch_result_proposals_created_count
- fulfillment_branch_merge_completed_count
- fulfillment_topology_preserved_count
- fulfillment_child_orchestrator_invoked_count
- fulfillment_child_architect_invoked_count
- fulfillment_child_executor_invoked_count
- fulfillment_child_root_created_count
- fulfillment_child_final_output_created_count
- fulfillment_child_action_commit_packet_created_count
- fulfillment_child_direct_adapter_bypass_blocked_count
- fulfillment_missing_branch_blocked_count
- fulfillment_duplicate_branch_blocked_count
- fulfillment_unknown_branch_blocked_count
- fulfillment_branch_real_action_claim_blocked_count
- fulfillment_branch_receipt_mismatch_blocked_count
- fulfillment_root_final_authority_preserved_count

Expected valid Fractal fulfillment counters:
- fractal_order_fulfillment_dag_invoked_count: 1
- fractal_order_fulfillment_dag_completed_count: 1
- fulfillment_child_cells_started_count: 3
- fulfillment_child_cells_completed_count: 3
- fulfillment_payment_branch_started_count: 1
- fulfillment_payment_branch_completed_count: 1
- fulfillment_supplier_branch_started_count: 1
- fulfillment_supplier_branch_completed_count: 1
- fulfillment_warehouse_branch_started_count: 1
- fulfillment_warehouse_branch_completed_count: 1
- fulfillment_branch_result_proposals_created_count: 3
- fulfillment_branch_merge_completed_count: 1
- fulfillment_topology_preserved_count: 1
- fulfillment_child_orchestrator_invoked_count: 3
- fulfillment_child_architect_invoked_count: 3
- fulfillment_child_executor_invoked_count: 3
- fulfillment_child_root_created_count: 0
- fulfillment_child_final_output_created_count: 0
- fulfillment_child_action_commit_packet_created_count: 0
- fulfillment_child_direct_adapter_bypass_blocked_count: 0
- fulfillment_root_final_authority_preserved_count: 1

Existing sandbox counters should remain compatible:
- fake_bank_adapter_invoked_count: 1
- fake_supplier_adapter_invoked_count: 1
- fake_warehouse_adapter_invoked_count: 1
- mock_receipt_created_count: 3
- execution_evidence_created_count: 1
- root_mock_execution_summary_created_count: 1

Real/external counters must remain zero:
- connector_called_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- real_bank_api_called_count: 0
- real_supplier_api_called_count: 0
- real_warehouse_api_called_count: 0
- action_permission_created_count: 0
- live_model_call_count: 0 unless dual Gemini is explicitly enabled separately
- network_used_count: 0 unless dual Gemini is explicitly enabled separately
- gemini_called_count: 0 unless dual Gemini is explicitly enabled separately

## Branch ResultProposal Shape

Required branch result proposal shape:
- proposal_type: fulfillment_branch_result_proposal
- branch_id
- parent_fractal_id
- source_packet_id
- adapter_name
- expected_receipt_type
- actual_receipt_type
- receipt_ref
- branch_status
- mock_only: true
- real_world_effects_allowed: false
- returns_to_parent: true
- child_root_created: false
- child_final_output_created: false
- child_action_commit_packet_created: false
- direct_adapter_bypass_attempted: false
- root_final_authority_preserved: true

## Topology Validation

Topology validation must reject:
- child branch claims or instantiates child-root authority
- child branch reports child_final_output_created true
- child branch reports child_action_commit_packet_created true
- child branch reports direct adapter invocation outside sandbox
- child branch claims real payment or real shipment
- missing branch
- duplicate branch
- unknown branch
- wrong adapter for branch
- wrong receipt type for branch
- branch output does not return upward
- branch tries DRS write directly
- branch tries to bypass Post V&V / GT-LGT / Root summary
- pre-Root executor path attempts to skip ActionCommitPacket
- branch reports external connector invocation

All rejection paths must preserve real/external counters at zero.

## DRS Writeback

DRS writeback should include local trace fields for:
- Fractal Order Fulfillment DAG trace
- branch result proposals
- branch merge summary
- execution evidence
- Root mock execution summary

DRS writeback must remain local trace only:
- external_global_drs_write: false
- production_persistence_claimed: false

## Required Future Tests

A. Default mode:
- PASS
- all Fractal Order Fulfillment counters zero

B. Fractal fulfillment gate without packet gates:
- FAIL_CLOSED
- fractal_order_fulfillment_requires_valid_action_commit_packet
- no branch starts
- no fake adapters

C. Fractal fulfillment gate without sandbox gate:
- FAIL_CLOSED
- fractal_order_fulfillment_requires_mock_connector_sandbox
- no branch starts

D. Blocked current scenario:
- Root not_ready
- no packet
- DAG denied
- no branch starts

E. Valid deterministic Fractal fulfillment:
- packet gates + mock-ready fixture + sandbox gate + fractal fulfillment gate
- PASS
- 3 child branches start and complete
- topology preserved
- 3 branch result proposals
- branch merge completed
- existing sandbox receipts/evidence/Root summary still produced
- real/external counters zero

F. Branch topology:
- every branch has child_orchestrator / child_architect / child_executor markers
- no child Root authority
- no child FinalOutput authority
- no child ActionCommitPacket authority
- returns_to_parent true

G. Missing branch:
- omit supplier branch
- fail closed or reject before Root mock execution summary
- missing branch counter increments

H. Duplicate branch:
- duplicate payment branch
- reject
- duplicate branch counter increments

I. Wrong adapter/receipt:
- payment branch points to fake_warehouse_adapter_v0 or warehouse receipt
- reject
- branch receipt mismatch counter increments

J. Direct adapter bypass:
- branch claims it directly invoked fake_bank_adapter_v0 outside sandbox
- reject
- direct adapter bypass counter increments

K. Branch real action claim:
- branch result claims payment_executed true or shipment_released true
- reject
- real/external counters remain zero

L. Child authority violations:
- child branch claims Root authority / FinalOutput / ActionCommitPacket authority
- reject
- child root/final/action packet counters remain zero or blocked counters increment

M. Expired packet:
- same expiry semantics as Mock Connector Sandbox
- no branches start or no adapters run after expiry rejection

N. DRS writeback:
- local trace includes branch proposals and merge summary
- external_global_drs_write_count == 0
- production_persistence_claimed_count == 0

O. Dual Gemini composition later:
- preflight only plans this as later smoke
- not required for first runtime

P. Existing regressions:
- default Full E2E PASS
- dual Gemini tests PASS
- ActionCommitPacket tests PASS
- Mock Connector Sandbox tests PASS
- no new model/network calls from deterministic Fractal fulfillment

## Preflight Answers

1. Can existing Full E2E runner host Fractal Order Fulfillment DAG safely?
Yes. The current runner already hosts Root Mock Approval Gate and Mock Connector Sandbox after Root boundary. The new layer can be inserted between ActionCommitPacket candidate and Mock Connector Sandbox without a new proof island.

2. Is a new runner needed?
No. A new runner would make the evidence weaker by separating the post-Root fulfillment DAG from the established supplier-payment spine.

3. Should this be prototyped in runner or core module?
Prototype in `demo/run_full_semantic_e2e_v01.py` first. Extract to a core module later only after branch shape, merge validation, and tests stabilize.

4. Is this post-Root or pre-Root fractal?
Post-Root. It runs after Root FinalOutput boundary and after Root Mock Approval Gate creates a validated mock_action_commit_packet.

5. How does it differ from the existing pre-Root Fractal executor?
The existing pre-Root executor consumes validated PlanGraph and returns ResultProposal before Root. The new DAG consumes Root-approved mock permission and coordinates sandbox-backed mock fulfillment branches after Root.

6. How is O/A/E topology preserved inside child branches?
Each branch records child Orchestrator, child Architect, and child Executor roles as bounded local topology markers. They can route, plan, and produce branch evidence, but cannot become Root or final authority.

7. How does each child return upward?
Each branch creates a fulfillment_branch_result_proposal with returns_to_parent: true. Parent merge consumes those branch proposals and validates receipt alignment.

8. How does the DAG consume ActionCommitPacket without letting children create one?
The parent DAG receives one Root-created packet and passes packet identity into child envelopes. Child outputs must set child_action_commit_packet_created: false.

9. How does the DAG use Mock Connector Sandbox without bypassing it?
The DAG builds and validates branch topology, then uses the existing sandbox for all fake adapter work. Branch outputs map to sandbox receipts after strict sandbox validation.

10. What exact branch shapes are required?
The three required branch shapes are payment_review_branch, supplier_confirmation_branch, and warehouse_reservation_branch with the adapter, action kind, expected receipt type, and status listed above.

11. What exact counters are required?
The counters listed in `Counters To Add` are required for invocation, completion, denial, child cells, branch starts/completions, merge, topology preservation, authority violations, receipt mismatch, and Root authority preservation.

12. What must remain zero?
Real/external counters remain zero: connector_called_count, payment_executed_count, shipment_released_count, real_bank_api_called_count, real_supplier_api_called_count, real_warehouse_api_called_count, and action_permission_created_count. Model/network counters remain zero unless Gemini gates are separately enabled.

13. What tests are required?
The tests listed in `Required Future Tests` are required.

14. Is dual Gemini required now?
No. The first runtime should prove deterministic topology preservation and sandbox discipline. Dual Gemini + Fractal Fulfillment + Mock Connector Sandbox composition smoke is the next layer after this runtime.

15. What comes after Fractal Order Fulfillment DAG runtime?
Dual Gemini + Fractal Fulfillment + Mock Connector Sandbox composition smoke:
- two real Gemini roles route/plan
- Root creates ActionCommitPacket
- Fractal fulfillment runs branch topology
- Mock Connector Sandbox records receipts/evidence
- Root summary preserves no real-world action

16. Is a separate patch plan required?
No. After this preflight is committed, the next approved implementation is runtime directly inside the existing Full Semantic E2E runner and focused tests.

## Verdict

Expected verdict if no blocker:
- next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests
- no new runner
- no real connector
- no production
- no NeedleFactory
- no Marennya / UP

next_step: implement Fractal Order Fulfillment DAG v0.1 runtime inside existing Full Semantic E2E runner and focused tests, after this preflight is committed.
