# Fractal Cell Runtime Integration v0.1 - Read-only Preflight

## 1. Current checkpoint

- preflight_id: fractal_cell_runtime_integration_preflight_v01
- preflight_status: COMPLETE
- current_head_before_layer: 09523bf
- previous_runtime_layer: Bounded LLM/SLM Actors v0.1
- previous_runtime_checkpoint: 09523bf
- runtime_gate_commit: 1e1afe6
- roadmap_block: Real Semantic Runtime MVP
- follows_STOP_PROOF_ONLY_EXPANSION_GATE: true
- runtime_modified: false
- schemas_modified: false
- tests_modified: false
- demos_modified: false
- proof_started: false
- audit_started: false
- human_walkthrough_started: false
- full_pytest_run: false

## 2. Purpose

This preflight starts Fractal Cell Runtime Integration after bounded actor
contracts are closed.

The current Real Semantic Runtime MVP thread is:

Real Local DRS Resolver -> CandidateVectorGenerator -> AVF scoring -> AVF
Candidate Advisory Evaluator -> Bounded LLM/SLM Actor Contracts -> Fractal Cell
Runtime Integration next.

The goal is to inspect how existing Fractal Cell, Fractal DAG, child executor,
Root boundary, Post V&V, GT, and bounded actor contract surfaces can be
integrated with the Real Semantic Runtime MVP chain while preserving Root-only
authority.

A Fractal Cell must be a bounded recursive execution container, not a new
authority layer.

## 3. Non-goals / boundaries

- no runtime implementation in preflight
- no production distributed runtime
- no external/global DRS
- no network
- no Gemini
- no real model calls
- no autonomous action
- no connector side effects
- no production Fractal Cell runtime
- no Marennya/UP
- no manifest mutation
- no transition matrix mutation
- no Root behavior modification
- no child Root
- no child FinalOutput authority
- no child action permission
- no public WOW
- no whitepaper/public auditor packet
- Real Semantic Runtime MVP is not complete

## 4. Existing assets found

- `hedgehog/fractal_dag_executor.py`
  - Observed role: deterministic Fractal DAG executor core.
  - Type: runtime/proof helper.
  - Provides: dependency ordering, bounded `max_nodes`, `max_parallelism`,
    cycle and unknown dependency blocking, ResultProposal-shaped outputs, and
    child boundary snapshot placeholders for non-atomic nodes.
  - Does not provide yet: full child actor chain, Fractal Cell integration with
    `bounded_actor_contracts`, production distributed runtime, or child Root.
  - Authority status: bounded/proposal; not final authority.

- `demo/run_fractal_dag_executor_core.py`
  - Observed role: deterministic Fractal DAG core proof runner.
  - Type: demo/proof.
  - Provides: horizontal, vertical, hybrid, child placeholder, parallelism
    limit, cycle, and max-node scenarios.
  - Does not provide yet: full Fractal Cell actor contract integration.
  - Authority status: proof-only proposal evidence.

- `tests/test_fractal_dag_executor_core_runner.py`
  - Observed role: focused tests for Fractal DAG core.
  - Type: tests.
  - Provides: coverage that non-atomic nodes return child boundary snapshots,
    Executor returns ResultProposal only, no FinalOutput appears in executor
    outputs, and no real external action occurs.
  - Does not provide yet: bounded actor contract composition inside child cell.
  - Authority status: test evidence only.

- `demo/run_fractal_cell_runtime.py`
  - Observed role: deterministic older Fractal Cell Runtime proof.
  - Type: demo/proof.
  - Provides: parent PlanGraph with atomic, needle-bound, and non-atomic child
    cell routes; child requests; bounded mini-cell execution; child boundary
    snapshots; parent adapter to ResultProposal-like rows; Post V&V / GT /
    Root-style downstream rows; malicious child claim rejection; bounded
    recursion and budget counters.
  - Does not provide yet: integration with the new Bounded LLM/SLM Actor
    Contracts v0.1 target-boundary checks.
  - Authority status: bounded proof; child cell is not final authority.

- `tests/test_fractal_cell_runtime_runner.py`
  - Observed role: focused tests for the older deterministic Fractal Cell proof.
  - Type: tests.
  - Provides: coverage for child completion, degraded budget, max-depth block,
    contract mismatch containment, non-child routes, malicious child output
    rejection, and Root authority safety flags.
  - Does not provide yet: future Real Semantic Runtime MVP integration tests.
  - Authority status: test evidence only.

- `docs/audit_reports/auditor_fractal_cell_runtime.log`
  - Observed role: historical audit evidence for deterministic Fractal Cell
    proof.
  - Type: audit log.
  - Provides: evidence that child cell snapshots return upward and child cells
    do not create final authority in that proof.
  - Does not provide yet: audit of this future integration layer.
  - Authority status: audit evidence only.

- `demo/run_live_child_executor_in_fractal_cell.py`
  - Observed role: optional live child Executor smoke surface with deterministic
    fallback.
  - Type: demo/proof/smoke.
  - Provides: bounded child node contract, action-like request blocking,
    ChildExecutionResult validation, parent adapter, and Post V&V / GT / Root
    return rows.
  - Does not provide yet: required live path for this layer; it must remain
    optional/historical and not become required runtime behavior.
  - Authority status: bounded child executor evidence; not Root.

- `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_deterministic.log`
  - Observed role: audit evidence for deterministic fallback child Executor
    path inside Fractal Cell.
  - Type: audit log.
  - Provides: evidence for bounded child Executor behavior and no API/tool/root
    bypass in deterministic mode.
  - Does not provide yet: current Real Semantic Runtime MVP integration audit.
  - Authority status: audit evidence only.

- `hedgehog/bounded_actor_contracts.py`
  - Observed role: Bounded LLM/SLM Actors v0.1 contract adapter / validator.
  - Type: runtime-facing contract module.
  - Provides: `BoundedActorRole`, `ActorInputEnvelope`,
    `ActorOutputEnvelope`, `ActorTransitionCheck`, `ActorBoundaryReport`,
    `validate_actor_input`, `validate_actor_output`,
    `validate_actor_transition`, `build_actor_boundary_report`, role contracts,
    canonical transition checks, and Target Boundary Fix enforcement.
  - Does not provide yet: Fractal Cell wrapper or child-cell-specific result
    model.
  - Authority status: boundary validator; not execution authority.

- `tests/test_bounded_llm_slm_actors_v01_runner.py`
  - Observed role: focused tests for bounded actor contracts.
  - Type: tests.
  - Provides: target-boundary tests proving final-output targets and invalid
    non-final targets are blocked while the canonical chain remains accepted.
  - Does not provide yet: Fractal Cell-specific child actor integration tests.
  - Authority status: test evidence only.

- `hedgehog/root_orchestrator.py`
  - Observed role: Root-controlled orchestration and FinalOutput boundary.
  - Type: runtime.
  - Provides: optional `use_fractal_dag_executor` path, DRS query/writeback,
    AttractorPacket, Architect, Executor/Fractal DAG, Post V&V, GT, Root-created
    FinalOutput, and audit trace fields.
  - Does not provide yet: direct integration with future
    `fractal_cell_integration.py` or child actor boundary reports.
  - Authority status: Root final authority.

- `hedgehog/architect.py`
  - Observed role: deterministic PlanGraph proposal generator.
  - Type: runtime.
  - Provides: PlanGraph creation from AttractorPacket.
  - Does not provide yet: child-cell-specific PlanGraph wrapper.
  - Authority status: proposal only; not execution or final authority.

- `hedgehog/executor.py`
  - Observed role: deterministic executor returning ResultProposal dictionaries.
  - Type: runtime.
  - Provides: bounded simulated ResultProposal outputs from PlanGraph nodes.
  - Does not provide yet: child cell orchestration or Root final behavior.
  - Authority status: proposal only.

- `hedgehog/post_vv.py`
  - Observed role: Post V&V runtime validator.
  - Type: runtime.
  - Provides: ResultProposal runtime schema validation and outgoing VVReport
    validation with forbidden key checks for root-only/user-facing fields.
  - Does not provide yet: child-cell-specific schema.
  - Authority status: validation/advisory boundary; not Root Final.

- `hedgehog/gt_validator.py`
  - Observed role: GT report and deterministic payoff/selection runtime.
  - Type: runtime.
  - Provides: GTReport decisions over VVReports with accept/revise/reject/no
    update behavior.
  - Does not provide yet: Root Final authority or child Root.
  - Authority status: advisory/selection; not Root Final.

- `hedgehog/gt_lgt_advisory_evaluator.py`
  - Observed role: AVF Candidate Advisory Evaluator / GT-style advisory layer.
  - Type: runtime-facing advisory module.
  - Provides: advisory signals over AVF-ranked DRS candidates and Root review
    requirements.
  - Does not provide yet: commands to Architect or Fractal Cell.
  - Authority status: advisory only.

- `hedgehog/candidate_vector_generator.py` and `hedgehog/local_drs_resolver.py`
  - Observed role: Real Semantic Runtime MVP memory candidate and vector input
    surfaces.
  - Type: runtime-facing modules.
  - Provides: local DRS candidate resolution, bounded candidate vectors, AVF
    score inputs, review flags, and advisory-only counters.
  - Does not provide yet: execution authority or child cell command authority.
  - Authority status: candidate/advisory signal only.

- `schemas/plan_graph.schema.json`
  - Observed role: PlanGraph contract.
  - Type: schema.
  - Provides: plan id, source packet id, time assumptions, nodes, edges, and
    executor assignments.
  - Does not provide yet: FractalCellResult schema.
  - Authority status: shape boundary only.

- `schemas/result_proposal.schema.json`
  - Observed role: ResultProposal contract.
  - Type: schema.
  - Provides: ResultProposal shape and excludes root-only `final_output` /
    `answer` payload keys.
  - Does not provide yet: explicit Fractal Cell result wrapper.
  - Authority status: proposal shape only.

- `schemas/vv_report.schema.json`, `schemas/gt_report.schema.json`, and
  `schemas/final_output.schema.json`
  - Observed role: Post V&V, GT, and Root FinalOutput schema boundaries.
  - Type: schemas.
  - Provides: downstream validation/selection/report shapes and Root-only
    FinalOutput with `created_by: root_orchestrator`.
  - Does not provide yet: child Root or child FinalOutput authority.
  - Authority status: VV/GT are validation/advisory; FinalOutput is Root-only.

- `demo/run_controlled_fractal_dac_expansion_v01.py` and
  `demo/run_dual_fractal_coupling_v01.py`
  - Observed role: applied/proof-mode child cell and coupling guardrail
    examples.
  - Type: demos/proofs.
  - Provides: child cells as local bounded candidates, no child Root authority,
    no sibling/cross-parent authority, and Root aggregation requirement.
  - Does not provide yet: current runtime-facing integration with bounded actor
    contracts.
  - Authority status: proof-only bounded/advisory examples.

## 5. Canonical topology

Intended future topology:

Parent Root / Orchestrator
-> Root-shaped task / route
-> Fractal Cell boundary
-> bounded child actor chain
   - child Intake if needed
   - child Orchestrator
   - child Architect
   - child Executor
   - child Verifier/Post V&V boundary
   - child GT/advisory boundary
-> child bounded ResultProposal / cell report
-> parent Post V&V / GT route
-> parent Root final review

Required topology statements:

- child cell is not Root
- child Orchestrator is not Root
- child Architect is not Root
- child Executor is not Root
- child GT/advisory boundary is not Root Final
- child output returns upward
- parent Root remains final authority

## 6. Integration with bounded actor contracts

Future implementation should use `hedgehog/bounded_actor_contracts.py` as the
first boundary contract surface for child actor input, output, and transition
checks.

The integration should preserve:

- `ActorInputEnvelope`
- `ActorOutputEnvelope`
- `ActorTransitionCheck`
- `ActorBoundaryReport`
- canonical accepted chain:
  - intake -> Root/Orchestrator
  - Root-shaped route -> Architect
  - PlanGraph -> Executor
  - ResultProposal -> Verifier/Post V&V
  - VVReport -> GT boundary
  - GTReport -> Root return
  - Root return -> Root/Orchestrator

Fractal Cell integration must reuse or compose these contracts, not bypass them.

Target Boundary Fix: it is not enough to check what a child actor outputs; the
system must check where child output is being sent.

Dangerous transitions must remain blocked:

- child Architect PlanGraph -> final_output
- child Executor ResultProposal -> final_output
- child Verifier VVReport -> final_output
- child GTReport -> final_output
- child GTReport -> parent Architect command
- child Root return -> user FinalOutput

## 7. Proposed implementation seam

Recommended future implementation seam:

- add `hedgehog/fractal_cell_integration.py`

It should compose:

- existing `hedgehog/fractal_dag_executor.py`
- existing `hedgehog/bounded_actor_contracts.py`
- existing PlanGraph / ResultProposal boundaries
- existing Post V&V / GT boundaries
- existing RootOrchestrator boundary concepts
- existing DRS / AVF / advisory candidate context only as signals

Do not replace:

- RootOrchestrator
- fractal_dag_executor
- bounded_actor_contracts
- Architect
- Executor
- Post V&V
- GTValidator

Do not create a new schema unless a hard blocker is found and a separate schema
patch plan is approved.

Rationale: the repo already has a deterministic Fractal DAG core and older
Fractal Cell proof surfaces. The safest v0.1 integration is a narrow adapter
that wraps or composes those surfaces with the newer bounded actor contract
checks and returns a proof-local cell report upward. Direct RootOrchestrator
modification should be deferred until the adapter proof closes.

## 8. Future cell model v0.1

Future conceptual dataclasses/functions, not implemented in this preflight:

- `FractalCellInput`
- `FractalCellBoundary`
- `FractalCellResult`
- `FractalCellTrace`
- `validate_fractal_cell_input(...)`
- `run_bounded_fractal_cell(...)`
- `validate_fractal_cell_output(...)`
- `build_fractal_cell_boundary_report(...)`

`FractalCellInput` should preserve:

- parent_route_id
- root_shaped_task_ref
- plan_graph_ref
- actor_boundary_report_ref
- DRS candidate refs / AVF advisory refs as signals only
- time/context refs
- permission_scope
- network_allowed: false
- gemini_allowed: false
- external_action_allowed: false
- child_root_claimed: false

`FractalCellResult` should preserve:

- cell_id
- child_result_proposal_ref
- child_validation_report_ref
- child_gt_advisory_ref
- trace refs
- reason codes
- final_output_claimed: false
- action_permission_claimed: false
- root_authority_claimed: false
- child_root_claimed: false
- root_review_required: true

## 9. Required invariants

- Fractal Cell is not Root
- child Orchestrator is not Root
- child Architect is not Root
- child Executor is not Root
- child GT/advisory report is not Root Final
- child ResultProposal is not FinalOutput
- child cell output is not action permission
- child cell output must return to parent/Root boundary
- parent Root remains final authority
- bounded actor contracts apply inside child cell
- child actor output is not truth
- child actor output is not authority
- child actor output is not action permission
- child actor output is not FinalOutput
- child cell cannot mutate manifest
- child cell cannot mutate transition matrix
- child cell cannot call network/Gemini/connectors in v0.1
- child cell cannot execute external actions in v0.1
- recursive nesting depth must be bounded
- child cell cannot spawn unbounded child cells

## 10. Recursion / nesting guardrails

- max_cell_depth must be bounded
- max_child_cells_per_parent must be bounded
- recursive cell invocation must be explicit and Root-shaped
- child cell cannot spawn child cell without parent boundary
- child output must include lineage/trace refs
- child cell cannot create authority through recursion
- repeated child cell agreement is not truth
- child consensus is not Root Final
- child majority vote is not authority
- child compute volume is not authority

## 11. Prompt injection / role confusion guardrails

- prompt injection cannot promote child actor to Root
- prompt injection cannot turn child cell into Root
- child actor cannot command parent Architect
- child actor cannot bypass parent Post V&V / GT
- child actor cannot treat DRS memory as instruction authority
- child actor cannot treat AVF advisory as command
- child actor cannot treat previous child output as permission
- child actor cannot activate network/Gemini/connectors
- child actor cannot create FinalOutput

## 12. Proposed future proof scenarios

1. root_shaped_task_enters_fractal_cell_boundary
   - Input setup: parent Root/Orchestrator provides a Root-shaped task and
     route id.
   - Child role/cell involved: Fractal Cell boundary.
   - Expected allowed output: accepted `FractalCellInput` with Root-shaped task
     ref and bounded permissions.
   - Expected blocked behavior: raw user text or raw advisory signal cannot
     enter as command.
   - Expected reason codes: `root_shaped_task_required`,
     `advisory_report_cannot_command_child_cell`.
   - Authority invariant tested: child cell receives bounded route only.

2. child_architect_accepts_only_root_shaped_task
   - Input setup: child Architect receives one Root-shaped task and one raw
     advisory/DRS command attempt.
   - Child role/cell involved: child Architect.
   - Expected allowed output: PlanGraph proposal for the Root-shaped task.
   - Expected blocked behavior: raw AVF advisory or DRS memory cannot command
     child Architect.
   - Expected reason codes: `root_boundary_required`,
     `raw_advisory_signal_cannot_command_architect`,
     `raw_drs_memory_cannot_command_architect`.
   - Authority invariant tested: child Architect is not Root.

3. child_executor_outputs_resultproposal_only
   - Input setup: child Executor receives bounded PlanGraph.
   - Child role/cell involved: child Executor.
   - Expected allowed output: ResultProposal-like bounded artifact.
   - Expected blocked behavior: FinalOutput, direct tool call, external action,
     or authority claim.
   - Expected reason codes: `resultproposal_only`,
     `final_output_blocked`, `direct_tool_call_blocked`.
   - Authority invariant tested: child Executor is not Root.

4. child_verifier_validates_without_finaloutput
   - Input setup: child Verifier/Post V&V receives ResultProposal-like output.
   - Child role/cell involved: child Verifier/Post V&V boundary.
   - Expected allowed output: VVReport / validation report.
   - Expected blocked behavior: verifier report cannot target final_output or
     root_return directly.
   - Expected reason codes: `vv_report_must_route_to_gt_boundary`,
     `final_output_target_boundary_blocked`.
   - Authority invariant tested: validation report is not Root Final.

5. child_gt_report_returns_to_parent_root_boundary
   - Input setup: child GT/advisory boundary receives VVReport.
   - Child role/cell involved: child GT/advisory boundary.
   - Expected allowed output: GTReport/advisory report routed to parent Root
     return boundary.
   - Expected blocked behavior: GTReport cannot target final_output or parent
     Architect command.
   - Expected reason codes: `gt_report_must_route_to_root_return`,
     `final_output_target_boundary_blocked`.
   - Authority invariant tested: child GT/advisory boundary is not Root Final.

6. child_finaloutput_claim_is_blocked
   - Input setup: child output claims final output or root authority.
   - Child role/cell involved: any child actor.
   - Expected allowed output: none for unsafe claim.
   - Expected blocked behavior: unsafe claim rejected before parent adapter.
   - Expected reason codes: `final_output_blocked`,
     `authority_claim_blocked`.
   - Authority invariant tested: no child FinalOutput authority.

7. child_actor_self_promotion_to_root_is_blocked
   - Input setup: child actor declares itself Root or child Root.
   - Child role/cell involved: child Orchestrator or child Executor.
   - Expected allowed output: blocked boundary report.
   - Expected blocked behavior: self-promotion cannot pass transition checks.
   - Expected reason codes: `actor_self_promotion_blocked`,
     `child_root_claim_blocked`.
   - Authority invariant tested: child actor cannot become Root.

8. child_cell_cannot_command_parent_architect
   - Input setup: child GTReport or child Root return attempts to command
     parent Architect.
   - Child role/cell involved: child GT/advisory boundary and child Root return.
   - Expected allowed output: none for parent Architect command.
   - Expected blocked behavior: command route blocked; report returns to parent
     Root boundary only.
   - Expected reason codes: `gt_report_must_route_to_root_return`,
     `child_report_cannot_command_parent_architect`.
   - Authority invariant tested: child cell cannot bypass parent route.

9. recursive_child_cell_depth_is_bounded
   - Input setup: child cell request exceeds max depth.
   - Child role/cell involved: Fractal Cell boundary.
   - Expected allowed output: blocked/degraded cell report with trace refs.
   - Expected blocked behavior: no child actor chain starts beyond depth limit.
   - Expected reason codes: `max_cell_depth_exceeded`.
   - Authority invariant tested: recursion cannot create escape authority.

10. child_consensus_does_not_create_authority
    - Input setup: several child cells agree on a recommendation.
    - Child role/cell involved: child cell aggregation.
    - Expected allowed output: parent review report only.
    - Expected blocked behavior: consensus cannot become Root Final or action
      permission.
    - Expected reason codes: `child_consensus_not_authority`,
      `root_review_required`.
    - Authority invariant tested: child majority vote is not authority.

11. child_output_returns_to_parent_post_vv_gt_route
    - Input setup: completed child ResultProposal-like output.
    - Child role/cell involved: parent adapter.
    - Expected allowed output: parent ResultProposal/report routed through
      parent Post V&V / GT.
    - Expected blocked behavior: direct Root final target or user final target
      is blocked.
    - Expected reason codes: `resultproposal_must_route_to_verifier`,
      `final_output_target_boundary_blocked`.
    - Authority invariant tested: child output returns upward through
      downstream validation.

12. root_final_authority_preserved_across_fractal_cell
    - Input setup: full bounded child cell chain returns to parent.
    - Child role/cell involved: full child cell integration report.
    - Expected allowed output: Root review required with parent-return report.
    - Expected blocked behavior: no child Root, no direct action permission, no
      FinalOutput authority, no Post V&V / GT bypass.
    - Expected reason codes: `root_final_authority_preserved`,
      `root_review_required`.
    - Authority invariant tested: parent Root remains final authority.

## 13. Proposed counters for future proof

- scenarios_total
- scenarios_passed
- cells_started_count
- child_actor_inputs_seen_count
- child_actor_outputs_emitted_count
- child_result_proposals_count
- child_validation_reports_count
- child_gt_reports_count
- parent_return_reports_count
- root_review_required_count
- final_output_created_count: 0
- action_permission_granted_count: 0
- child_root_claimed_count: 0
- child_authority_claimed_count: 0
- child_finaloutput_claimed_count: 0
- child_action_permission_claimed_count: 0
- child_actor_self_promotion_count: 0
- parent_boundary_bypass_count: 0
- post_vv_bypass_count: 0
- gt_bypass_count: 0
- parent_architect_commanded_count: 0
- recursive_depth_limit_exceeded_count: 0
- unbounded_child_spawn_count: 0
- child_consensus_authority_claimed_count: 0
- manifest_mutation_count: 0
- transition_matrix_mutation_count: 0
- network_used_count: 0
- gemini_used_count: 0
- connector_side_effect_count: 0
- root_final_authority_preserved_count

Required PASS conditions:

- scenarios_passed == scenarios_total
- final_output_created_count == 0
- action_permission_granted_count == 0
- child_root_claimed_count == 0
- child_authority_claimed_count == 0
- child_finaloutput_claimed_count == 0
- child_action_permission_claimed_count == 0
- child_actor_self_promotion_count == 0
- parent_boundary_bypass_count == 0
- post_vv_bypass_count == 0
- gt_bypass_count == 0
- parent_architect_commanded_count == 0
- recursive_depth_limit_exceeded_count == 0
- unbounded_child_spawn_count == 0
- child_consensus_authority_claimed_count == 0
- manifest_mutation_count == 0
- transition_matrix_mutation_count == 0
- network_used_count == 0
- gemini_used_count == 0
- connector_side_effect_count == 0
- root_final_authority_preserved_count == scenarios_total

## 14. Risks / decisions needed

- Decide whether future implementation wraps `fractal_dag_executor.py` or calls
  it directly from a narrow integration adapter.
- Decide whether existing ResultProposal schema is sufficient for parent-facing
  child output or whether proof-local `FractalCellResult` should be used first.
- Decide whether a proof-local FractalCellResult is enough for v0.1; safest
  default is yes.
- Define explicit `max_cell_depth` and `max_child_cells_per_parent` values.
- Reuse `bounded_actor_contracts` transition checks instead of duplicating role
  logic.
- Avoid changing RootOrchestrator prematurely; future proof should close the
  adapter first.
- Avoid production distributed runtime claims; this layer remains local,
  deterministic, bounded, and proof-scoped unless a later plan says otherwise.
- Full pytest should be required after runtime implementation because this
  future layer touches runtime-facing execution boundaries.

## 15. Recommended next step

Fractal Cell Runtime Integration v0.1 PATCH PLAN
