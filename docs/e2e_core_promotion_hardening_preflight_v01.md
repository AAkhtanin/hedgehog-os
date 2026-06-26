# E2E Core Promotion & Hardening v0.1 PREFLIGHT

- preflight_id: e2e_core_promotion_hardening_preflight_v01
- preflight_status: COMPLETE
- base_head: 11df12c
- previous_closed_layer: Full Semantic E2E v0.1
- planning_only: true
- patch_plan_required: false
- separate_patch_plan_created: false
- runtime_created: false
- tests_created: false
- demo_runner_created: false
- audit_log_created: false
- existing_full_e2e_runner_will_be_extended: true
- separate_proof_runner_allowed: false
- network_called: false
- provider_called: false
- secrets_accessed: false
- connector_called: false
- payment_executed: false
- shipment_released: false
- commit_created: false

## Purpose

Promote the represented middle stages in `demo/run_full_semantic_e2e_v01.py` into directly invoked runtime stages, slice by slice, without creating a parallel E2E demo. This is not an attack catalog and not another proof-only layer. Hardening checks are attached only to newly invoked components.

The next approved implementation must be Slice 1 runtime code. Slice 1 must modify the existing Full Semantic E2E route. A narrowly scoped adapter under `hedgehog/` is allowed only if direct composition of existing core contracts is proven awkward by implementation.

## Current Invoked Baseline

- Existing Full E2E entry point: `demo/run_full_semantic_e2e_v01.py::run_full_semantic_e2e`
- Current invoked stages: dirty request intake, supplier live evidence lane, SemanticEvidenceClaim validation, `root_final_output_boundary`
- Current represented middle stages: DRS resolve/reuse, CandidateVectorGenerator, AVF, advisory review, bounded Orchestrator, bounded Architect, PlanGraph, Fractal Cell / Executor, ResultProposal, Post V&V, GT/LGT, DRS writeback
- Current proof test: `tests/test_full_semantic_e2e_v01_runner.py`

## Callable Promotion Inventory

Each row below records the exact callable found in the repository, not just a documented name.

### Slice 1

1. Stage name: DRS resolve/reuse
   - current status: represented
   - existing implementation file: `hedgehog/local_drs_resolver.py`
   - exact callable class/function/symbol: `SemanticDRSRecordInput`, `SemanticResolveQuery`, `write_semantic_record`, `resolve_semantic_candidates`
   - existing focused test: `tests/test_real_local_drs_resolver_writeback_v01_runner.py`
   - can be invoked directly: yes
   - adapter or contract gap: map supplier/payment `SemanticEvidenceClaim` and dirty business context into `SemanticDRSRecordInput`, then query with `SemanticResolveQuery`
   - target runtime slice: Slice 1
   - minimal hardening checks: stale DRS cannot authorize; conflicting provenance remains review-only; legal-hold evidence beats score or memory

2. Stage name: CandidateVectorGenerator
   - current status: represented
   - existing implementation file: `hedgehog/candidate_vector_generator.py`
   - exact callable class/function/symbol: `CandidateVectorInput`, `candidate_inputs_from_resolved_report`, `generate_candidate_vectors`, `rank_candidate_vectors`, `build_avf_candidate_report`
   - existing focused test: `tests/test_candidate_vector_generator_avf_scoring_v01_runner.py`
   - can be invoked directly: yes
   - adapter or contract gap: preserve `records_by_id` from the DRS write/resolve step so `candidate_inputs_from_resolved_report` can enrich vectors from actual local records
   - target runtime slice: Slice 1
   - minimal hardening checks: candidate vector is not truth; direct reuse remains false; conflicting or stale candidate does not become permission

3. Stage name: AVF scoring/ranking
   - current status: represented
   - existing implementation file: `hedgehog/avf.py` and `hedgehog/candidate_vector_generator.py`
   - exact callable class/function/symbol: `score_candidate_vector`, `compute_hard_mask`, `compute_soft_mask`, `build_avf_candidate_report`
   - existing focused test: `tests/test_avf_runtime.py`, `tests/test_avf_hardmask.py`, `tests/test_candidate_vector_generator_avf_scoring_v01_runner.py`
   - can be invoked directly: yes
   - adapter or contract gap: prefer `build_avf_candidate_report` because it already composes generated vectors with AVF scoring and review counters
   - target runtime slice: Slice 1
   - minimal hardening checks: AVF is not authority; high score cannot override legal hold; hard-masked candidate cannot become selected action

4. Stage name: advisory review
   - current status: represented
   - existing implementation file: `hedgehog/gt_lgt_advisory_evaluator.py`
   - exact callable class/function/symbol: `AdvisoryEvaluationInput`, `build_advisory_report`, `evaluate_candidate_report`
   - existing focused test: `tests/test_gt_lgt_advisory_evaluator_v01_runner.py`
   - can be invoked directly: yes, if Slice 1 has a `CandidateVectorReport`
   - adapter or contract gap: attach supplier-payment reason codes and keep advisory route separate from terminal GT
   - target runtime slice: Slice 1
   - minimal hardening checks: advisory cannot create FinalOutput; advisory cannot grant action permission; stale/conflicting pressure cannot be hidden

### Slice 2

5. Stage name: bounded Orchestrator
   - current status: represented
   - existing implementation file: `hedgehog/root_orchestrator.py` and `demo/run_controlled_orchestrator_matrix_gate.py`
   - exact callable class/function/symbol: `RootOrchestrator.process_event`, `collect_controlled_orchestrator_matrix_gate`, `_evaluate_gate`
   - existing focused test: `tests/test_root_orchestrator_runtime.py`, `tests/test_controlled_orchestrator_matrix_gate_runner.py`
   - can be invoked directly: partial
   - adapter or contract gap: core `RootOrchestrator.process_event` is current certificate-domain oriented; supplier-payment E2E needs a bounded route/matrix adapter instead of wholesale Gemini-smoke copying
   - target runtime slice: Slice 2
   - minimal hardening checks: prompt injection cannot alter target boundary; wrong downstream actors are rejected; Orchestrator cannot create FinalOutput or execute action

6. Stage name: bounded Architect
   - current status: represented
   - existing implementation file: `hedgehog/architect.py`
   - exact callable class/function/symbol: `make_plan_graph`
   - existing focused test: `tests/test_architect_runtime.py`, `tests/test_architect_from_bounded_attractor_packet_runner.py`
   - can be invoked directly: yes, after Slice 2 builds a bounded AttractorPacket-like input
   - adapter or contract gap: convert Slice 1 candidate/advisory output into a bounded packet; do not pass raw provider text or raw dirty request
   - target runtime slice: Slice 2
   - minimal hardening checks: raw provider text blocked; rejected vectors absent; Architect returns PlanGraph only

7. Stage name: PlanGraph construction/validation
   - current status: represented
   - existing implementation file: `hedgehog/architect.py` and `hedgehog/llm_architect.py`
   - exact callable class/function/symbol: `make_plan_graph`, `validate_plan_graph_contract`
   - existing focused test: `tests/test_architect_runtime.py`, `tests/test_llm_architect_runtime.py`
   - can be invoked directly: yes
   - adapter or contract gap: supplier-payment packet must expose allowed vector ids, time assumptions, and executor assignments compatible with the existing contract
   - target runtime slice: Slice 2
   - minimal hardening checks: invalid DAG rejected; disallowed vector rejected; PlanGraph cannot contain FinalOutput or raw user text

8. Stage name: Fractal Cell / Executor
   - current status: represented
   - existing implementation file: `hedgehog/fractal_dag_executor.py`, `hedgehog/fractal_cell_integration.py`, `hedgehog/executor.py`
   - exact callable class/function/symbol: `run_fractal_dag_executor`, `run_bounded_fractal_cell`, `execute_plan_graph`, `execute_node`
   - existing focused test: `tests/test_fractal_dag_executor_core_runner.py`, `tests/test_fractal_cell_runtime_integration_v01_runner.py`, `tests/test_executor_runtime.py`
   - can be invoked directly: yes for DAG executor and executor; bounded Fractal Cell may need a supplier-specific input adapter
   - adapter or contract gap: map validated supplier PlanGraph nodes into safe executor tasks; only invoke bounded cell branch if `FractalCellInput` can be built without authority drift
   - target runtime slice: Slice 2
   - minimal hardening checks: cycle and max-node blocks; child branch cannot overreach parent boundary; executor cannot call bank/supplier/warehouse

### Slice 3

9. Stage name: ResultProposal
   - current status: represented
   - existing implementation file: `hedgehog/executor.py`, `hedgehog/fractal_dag_executor.py`
   - exact callable class/function/symbol: `execute_node`, `execute_plan_graph`, `run_fractal_dag_executor`
   - existing focused test: `tests/test_executor_runtime.py`, `tests/test_dag_executor_from_valid_plan_graph_runner.py`
   - can be invoked directly: yes
   - adapter or contract gap: Full E2E must preserve schema-compatible ResultProposal dictionaries from whichever executor path Slice 2 selected
   - target runtime slice: Slice 3
   - minimal hardening checks: ResultProposal is not FinalOutput; TimeEnvelope is present; no action/connector claim

10. Stage name: Post V&V
    - current status: represented
    - existing implementation file: `hedgehog/post_vv.py`
    - exact callable class/function/symbol: `validate_result_proposal`, `validate_result_proposals`
    - existing focused test: `tests/test_post_vv_runtime.py`, `tests/test_post_vv_from_result_proposal_runner.py`
    - can be invoked directly: yes
    - adapter or contract gap: ensure Slice 2 proposals meet current `result_proposal.schema.json`; do not feed raw executor text or raw PlanGraph
    - target runtime slice: Slice 3
    - minimal hardening checks: malformed ResultProposal fails; FinalOutput claim fails; Post V&V failure prevents GT success path

11. Stage name: GT/LGT review
    - current status: represented
    - existing implementation file: `hedgehog/gt_validator.py`, `hedgehog/gt_lgt_advisory_evaluator.py`
    - exact callable class/function/symbol: `validate_gt`, `classify_vv_report`, `evaluate_candidate_report`
    - existing focused test: `tests/test_gt_validator_runtime.py`, `tests/test_gt_from_validation_report_runner.py`, `tests/test_gt_lgt_advisory_evaluator_v01_runner.py`
    - can be invoked directly: yes for GT; LGT is currently advisory/deferred
    - adapter or contract gap: terminal E2E stage must separate Slice 1 advisory report from terminal GT selection and record LGT as deferred unless directly callable
    - target runtime slice: Slice 3
    - minimal hardening checks: GT/LGT cannot finalize; GT decision cannot create FinalOutput; needs-revision reports cannot be silently accepted

12. Stage name: DRS writeback
    - current status: represented
    - existing implementation file: `hedgehog/local_drs_resolver.py`, `hedgehog/drs.py`
    - exact callable class/function/symbol: `write_root_final_record`, `write_semantic_record`, `LocalDRS.write_record`
    - existing focused test: `tests/test_real_local_drs_resolver_writeback_v01_runner.py`, `tests/test_drs_writeback_from_root_final_runner.py`
    - can be invoked directly: yes, after Root-shaped artifact adapter
    - adapter or contract gap: existing Full E2E `root_final_output_boundary` uses `created_by: root_boundary`; `write_root_final_record` requires a Root-reviewed semantic outcome shape with `created_by: root_orchestrator`
    - target runtime slice: Slice 3
    - minimal hardening checks: writeback only after Root; raw/malicious root artifact rejected; local writeback does not imply production persistence

## Root Boundary Preservation

- Root FinalOutput boundary is already invoked in Full E2E through `demo/run_full_semantic_e2e_v01.py::_root_final_output_boundary`.
- Core Root surface exists in `hedgehog/root_orchestrator.py::RootOrchestrator.process_event`.
- Slice 3 may adapt the existing boundary to a `write_root_final_record`-compatible local audit artifact, but existing Root authority geometry must remain unchanged.

## Required Runtime Slicing

Slice 1:
- real DRS resolve/reuse
- real CandidateVectorGenerator
- real AVF scoring/ranking
- existing advisory surface where directly compatible
- stale/conflicting DRS and legal-hold-over-score checks
- target runtime file: existing `demo/run_full_semantic_e2e_v01.py`

Slice 2:
- bounded Orchestrator
- bounded Architect
- validated PlanGraph
- Fractal Cell / Executor branch
- prompt-injection, target-boundary, DAG, and child-overreach checks
- target runtime file: existing `demo/run_full_semantic_e2e_v01.py`

Slice 3:
- ResultProposal
- Post V&V
- terminal GT/LGT
- Root-only FinalOutput
- real local DRS writeback after Root
- Post V&V failure, GT non-finality, and writeback-order checks
- target runtime file: existing `demo/run_full_semantic_e2e_v01.py`

## Measurable Gate For Every Slice

- represented_count decreases
- invoked_count increases
- no represented stage is reported as invoked
- existing Root authority geometry remains unchanged
- payment, shipment, and connector execution remain zero

## Anti-Overclaim Boundaries

- not production
- not Public WOW
- not real external execution
- not NeedleFactory readiness
- provider/LLM output remains candidate evidence
- DRS is not truth
- AVF is not authority
- GT/LGT cannot finalize
- Root remains final authority

## Preflight Verdict

No separate patch plan is required for this slice. The next approved step is Slice 1 runtime implementation against the existing Full Semantic E2E route.

next_approved_step: E2E Core Promotion & Hardening v0.1 Slice 1 runtime
next_runtime_target: existing Full Semantic E2E route
next_runtime_priority: DRS resolve/reuse -> CandidateVectorGenerator -> AVF
another_planning_document_allowed: false
