# Rich Context / Bounded Context Packets Preflight v0.1

preflight_id: rich_context_bounded_context_packets_preflight_v01
preflight_status: COMPLETE
base_head: 4ab64f7
planning_only: true
runtime_created: false
tests_created: false
audit_log_created: false
new_runner_created: false
core_modules_modified: false
schemas_modified: false
production_ready: false
public_wow_ready: false
gemini_provider_called: false
network_called: false
secrets_accessed: false
commit_created: false

## Purpose

Plan the next engineering layer after Core Extraction Action + Mock + Fractal:
Rich Context / Bounded Context Packets.

Core thesis:
Rich Context / Bounded Context Packets means bounded context packets, not raw dumps. The current Gemini and PlanGraph context is intentionally bounded and still relatively thin. The next safe improvement is to define typed, bounded, validated Context Packets, not to dump the full runner state into Gemini.

This is preflight only. It does not implement runtime, modify tests, modify `hedgehog/*`, modify schemas, call Gemini, call provider/model/network APIs, access secrets, create a public wrapper, create an audit log, or create a new runner.

## Source Of Truth Inspected

Durable committed sources:

- `README.md`
- `AGENTS.md`
- `specs/human_passport_v0_25.md`
- `specs/machine_manifest_v0_25.json`
- `docs/core_extraction_checkpoint_v01.md`
- `docs/full_semantic_e2e_core_contracts_v01.md`
- `docs/public_wow_core_extracted_fractal_fulfillment_walkthrough_v01.md`
- `docs/audit_reports/auditor_core_extraction_action_mock_fractal_v01.log`
- `docs/core_extraction_action_mock_fractal_preflight_v01.md`
- `demo/run_full_semantic_e2e_v01.py`
- `hedgehog/action_commit_packet.py`
- `hedgehog/mock_connector_sandbox.py`
- `hedgehog/fractal_fulfillment.py`

No `.tmp` evidence is required for this preflight.

## 1. Current Checkpoint

Core Extraction Action + Mock + Fractal is CLOSED.

Current HEAD: 4ab64f7.

The stable contracts have been extracted to:

- `hedgehog.action_commit_packet`
- `hedgehog.mock_connector_sandbox`
- `hedgehog.fractal_fulfillment`

The Full Semantic E2E runner, `demo/run_full_semantic_e2e_v01.py`, remains the integration spine / harness. It wires the supplier-payment route, gates, stage map, counters, local DRS writeback, and report rendering around the extracted contracts.

Authority and safety checkpoint:

- Root remains final authority.
- Gemini proposes, Root disposes.
- ActionCommitPacket is Root-created through `root_mock_approval_gate`.
- MockConnectorSandbox is the only fake-adapter execution layer.
- FractalFulfillmentTopology preserves child O/A/I topology.
- Child branch is not Root.
- ExecutionEvidence is not FinalOutput.
- Mock receipt is not real payment.
- not production
- not public WOW ready yet

## 2. Why This Layer Is Next

This layer follows the README, AGENTS, and Passport next engineering direction: Rich Context / Bounded Context Packets preflight.

It is the bridge from the current skeleton to passport muscles:

- AVF v0.2 needs richer structured pressures without letting AVF become route authority.
- GT/LGT v0.2 needs richer review context without letting GT/LGT finalize.
- DRS v0.2 needs richer candidate context without making DRS truth.
- Gemini Orchestrator and Gemini Architect need better structured input without gaining Root, action, or final-output authority.
- Fractal fulfillment branches need richer task packets without becoming independent child sovereignty.

Rich context must not be raw prompt stuffing. Rich context must not make Gemini truth, authority, action permission, connector executor, DRS writer, or final-output creator.

## 3. Problem Statement

Current context is safe but thin:

- Gemini Orchestrator sees bounded route context.
- Gemini Architect sees bounded route and PlanGraph context.
- PlanGraph remains small.
- AVF, DRS, and GT/LGT signals exist, but not yet as rich reusable typed packets.
- Fractal fulfillment topology exists, but child branches do not yet receive rich semantic task packets.

The next layer should enrich context while preserving output shape, counter semantics, stage_map behavior, and fail-closed authority boundaries.

## 4. Proposed Packet Families

These packet families are future contracts only. They are not implemented by this preflight.

### A. BusinessRequestContextPacket

Planned fields:

- packet_type: BusinessRequestContextPacket
- request_id
- business_subject
- domain
- requested_action
- explicit_blockers
- user_visible_summary
- forbidden_authority_fields
- forbidden_action_fields
- truth_claimed: false
- authority_claimed: false
- action_permission_claimed: false
- final_output_claimed: false

Boundary:
Business request context frames the task. It is not truth, authority, action permission, FinalOutput, or ActionCommitPacket.

### B. EvidenceContextPacket

Planned fields:

- packet_type: EvidenceContextPacket
- semantic_evidence_claim_refs
- candidate_only: true
- provenance_summary
- contradiction_flags
- unsafe_instruction_flags
- truth_claimed: false
- authority_claimed: false
- action_permission_claimed: false

Boundary:
Evidence context is candidate evidence only. It is not truth and not authority.

### C. DRSCandidateContextPacket

Planned fields:

- packet_type: DRSCandidateContextPacket
- candidate_ids
- stale_flags
- conflict_flags
- reuse_eligibility_flags
- direct_reuse_allowed: false unless separately proven
- drs_write_permission_claimed: false

Boundary:
DRS packet is not DRS write permission. DRS is not truth.

### D. CandidateVectorContextPacket

Planned fields:

- packet_type: CandidateVectorContextPacket
- vector_ids
- selected_vector_ids
- allowed_vector_ids
- ranking_summary
- blocked_candidates
- masked_candidates
- truth_claimed: false
- authority_claimed: false

Boundary:
CandidateVector is not truth. Candidate vectors may rank and expose candidates, but they do not decide.

### E. AVFAttractorContextPacket

Planned fields:

- packet_type: AVFAttractorContextPacket
- hard_masks
- soft_pressures_planned
- risk_pressure
- conflict_pressure
- freshness_pressure
- reuse_pressure
- advisory_only: true

Boundary:
AVF is advisory only. AVF packet is not route authority.

### F. OrchestratorRouteContextPacket

Planned fields:

- packet_type: OrchestratorRouteContextPacket
- allowed_routes
- required_guards
- selected_vector_ids
- route_validation_expectations
- orchestrator_is_root: false
- final_output_claimed: false
- action_permission_claimed: false

Boundary:
Orchestrator is not Root. Orchestrator may propose a route only after consuming bounded context.

### G. ArchitectPlanContextPacket

Planned fields:

- packet_type: ArchitectPlanContextPacket
- source_route_id
- allowed_executor_ids
- allowed_node_kinds
- required_validators
- forbidden_connector_claims
- forbidden_action_claims
- forbidden_final_output_claims
- architect_is_root: false
- creates_action_commit_packet: false

Boundary:
Architect is not Root. Architect does not create ActionCommitPacket. Plan packet is not execution authority.

### H. FractalBranchTaskContextPacket

Planned fields:

- packet_type: FractalBranchTaskContextPacket
- parent_fractal_id
- branch_id
- child_oai_topology
- child_orchestrator: bounded_branch_router
- child_architect: bounded_branch_plan
- child_executor: mock_sandbox_task_executor
- allowed_adapter_name as metadata only
- expected_receipt_type
- returns_to_parent: true
- child_root_created: false
- child_final_output_created: false
- child_action_commit_packet_created: false
- direct_adapter_bypass_attempted: false

Boundary:
Child branch is not Root. Fractal branch packet is not Root. The packet cannot authorize direct adapter calls.

### I. SandboxReceiptContextPacket

Planned fields:

- packet_type: SandboxReceiptContextPacket
- mock_receipt_refs
- adapter_names
- mock_only: true
- real_world_effects_allowed: false
- fake_connector_counter_notes
- real_external_counter_expectations

Boundary:
Mock receipt is not real payment. `fake_*_connector_called_count` may rise for local fake calls. Real/external counters remain zero.

### J. RootReviewContextPacket

Planned fields:

- packet_type: RootReviewContextPacket
- pre_root_advisory_summary
- post_vv_summary
- gt_lgt_summary
- root_boundary_expectations
- final_output_creator: root_only
- action_commit_packet_creator: root_mock_approval_gate_only

Boundary:
Only Root can create FinalOutput. Only Root Mock Approval Gate can create ActionCommitPacket.

## 5. Required Validators

Future validators should be created in a later runtime/core slice:

- `validate_business_request_context_packet`
- `validate_evidence_context_packet`
- `validate_drs_candidate_context_packet`
- `validate_candidate_vector_context_packet`
- `validate_avf_attractor_context_packet`
- `validate_orchestrator_route_context_packet`
- `validate_architect_plan_context_packet`
- `validate_fractal_branch_task_context_packet`
- `validate_sandbox_receipt_context_packet`
- `validate_root_review_context_packet`

Validator discipline:

- reject `truth_claimed: true`
- reject `authority_claimed: true`
- reject `action_permission_claimed: true`
- reject `final_output_claimed: true`
- reject `connector_command_claimed: true`
- reject `drs_write_claimed` by a non-Root stage
- reject `root_bypass_claimed: true`
- reject `direct_adapter_bypass_attempted: true`
- reject `real_world_effects_allowed: true`
- reject production-readiness assertions
- reject public-WOW-readiness assertions
- reject raw secret markers
- reject raw_user_text unbounded dump
- reject raw Gemini cross-role text
- reject unbounded PlanGraph context dump

Validators must be fail-closed and must return structured reasons that can be surfaced in the existing validation_errors shape without counter, stage_map, or report drift unless separately audited.

## 6. Runtime Placement Plan

Do not implement in this preflight. Planned future placement:

1. Create packet builders and validators in `hedgehog/context_packets.py`.
2. Add direct core tests for every packet family and validator.
3. Add a runner adapter that creates packets from existing Full Semantic E2E result objects without changing current output shape.
4. Gemini Orchestrator prompt consumes only `OrchestratorRouteContextPacket`.
5. Gemini Architect prompt consumes only `ArchitectPlanContextPacket`.
6. PlanGraph may include packet refs, not raw full state.
7. AVF v0.2 may consume `AVFAttractorContextPacket`.
8. GT/LGT v0.2 may consume `RootReviewContextPacket` or a later bounded strategy packet.
9. Fractal Runtime v0.2 may consume `FractalBranchTaskContextPacket`.

The existing `hedgehog.action_commit_packet`, `hedgehog.mock_connector_sandbox`, and `hedgehog.fractal_fulfillment` modules remain the stable source for their extracted contracts. Context packets should reference those contracts rather than duplicating authority or sandbox validation.

## 7. Safety Invariants

Required invariants for any later implementation:

- Gemini proposes, Root disposes.
- Root remains final authority.
- Context packet is not truth.
- Context packet is not authority.
- Context packet is not action permission.
- Context packet is not FinalOutput.
- Context packet is not ActionCommitPacket.
- DRS packet is not DRS write permission.
- AVF packet is not route authority.
- Plan packet is not execution authority.
- Fractal branch packet is not Root.
- Child branch is not Root.
- Mock receipt is not real payment.
- ExecutionEvidence is not FinalOutput.
- ActionCommitPacket remains Root-created and mock-only.
- MockConnectorSandbox remains the only fake-adapter execution layer.
- FractalFulfillmentTopology does not call fake adapters directly.

## 8. Non-Goals

This preflight and the first implementation slice must not introduce:

- production connectors
- real payment
- real shipment
- real bank, supplier, or warehouse API use
- public-WOW-readiness assertion
- production-readiness assertion
- no NeedleFactory / Marennya / UP
- raw context dumps
- new runner
- Gemini/provider/network/model calls in this preflight
- secret access
- ActionCommitPacket creation by Gemini
- direct fake-adapter calls from Fractal branches
- DRS write permission for non-Root stages

## 9. Proposed Future Implementation Slices

Slice A: Context packet core contracts and validators.

- future file likely: `hedgehog/context_packets.py`
- future tests likely: `tests/test_context_packets_core.py`
- goal: define packet defaults, required fields, forbidden claim checks, and validators

Slice B: Runner builds packets from existing Full Semantic E2E result without changing output shape.

- runner remains integration spine / harness
- packet contexts should be added behind gates or as non-disruptive internal contexts
- no counter drift, stage_map drift, or validation reason drift unless audited

Slice C: Gemini Orchestrator consumes `OrchestratorRouteContextPacket`.

- Orchestrator receives bounded route context only
- Orchestrator remains proposal-only
- raw cross-role text remains blocked

Slice D: Gemini Architect consumes `ArchitectPlanContextPacket`.

- Architect receives bounded plan context only
- Architect remains proposal-only
- PlanGraph can carry packet refs, not raw full state

Slice E: Fractal branch task packets for child O/A/I branches.

- Fractal branches consume `FractalBranchTaskContextPacket`
- branch task packets preserve child topology
- no direct adapter calls

Slice F: AVF/GT/LGT packet hooks for future muscle math.

- AVF consumes structured pressures
- GT/LGT consumes bounded Root review or strategy context
- all remain advisory below Root

Slice G: Audit + docs sync.

- record output shape, counter, stage_map, fail-closed, deterministic smoke, and dual Gemini smoke evidence
- update navigation only after implementation is closed and audited

## 10. Expected Validation Later

Future implementation should validate:

- default CLI PASS
- focused packet core tests
- existing Full Semantic E2E runner regression tests
- existing ActionCommitPacket core tests
- existing MockConnectorSandbox core tests
- existing FractalFulfillmentTopology core tests
- no output shape drift unless audited
- no counter drift unless audited
- no stage_map drift unless audited
- deterministic smoke
- dual Gemini smoke
- forbidden grep for overclaims and raw dumps
- no new model/network/Gemini calls unless explicitly enabled by already-existing Gemini gates

## Preflight Answers

1. What is this layer?
   Rich Context / Bounded Context Packets: typed, bounded, validated packets for richer Orchestrator, Architect, PlanGraph, AVF, DRS, GT/LGT, and Fractal branch context.

2. Is this a runtime patch now?
   No. This is planning only.

3. Is a new runner needed?
   No. The Full Semantic E2E runner remains the integration spine / harness.

4. Should context be raw runner state?
   No. Use bounded context packets, not raw dumps.

5. Does rich context grant authority?
   No. Context packet is not truth, not authority, not action permission, not FinalOutput, and not ActionCommitPacket.

6. Does Gemini gain authority?
   No. Gemini proposes, Root disposes.

7. Which module should come first?
   Future Slice A should create `hedgehog/context_packets.py` with plain dict-compatible builders and validators.

8. Should schemas change now?
   No. Schema work should follow a successful core packet proof or a separate schema preflight.

9. What comes after this preflight?
   Next approved implementation should be Slice A: Context packet core contracts and validators, if this preflight is accepted and committed.

## Verdict

preflight_verdict: APPROVE_NEXT_SLICE_A_CONTEXT_PACKET_CORE_CONTRACTS

The next safe improvement is Rich Context / Bounded Context Packets. The implementation should start with bounded packet builders and validators, preserve current Full Semantic E2E behavior, keep extracted core contracts authoritative for their domains, and keep Root as final authority.
