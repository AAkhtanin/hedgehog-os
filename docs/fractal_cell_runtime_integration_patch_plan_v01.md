# Fractal Cell Runtime Integration v0.1 — Patch Plan

## 1. Current checkpoint

- patch_plan_id: fractal_cell_runtime_integration_patch_plan_v01
- patch_plan_status: COMPLETE
- preflight_commit: 84303eb
- previous_runtime_checkpoint: 09523bf
- runtime_gate_commit: 1e1afe6
- roadmap_block: Real Semantic Runtime MVP
- layer_type: runtime_facing_patch_plan
- implementation_started: false
- runtime_modified: false
- schemas_modified: false
- tests_created: false
- demos_created: false
- full_pytest_run: false

## 2. Purpose

This patch plan defines the future implementation of a bounded Fractal Cell integration layer.

The goal is not to create production distributed runtime. The goal is to integrate existing Fractal DAG / Fractal Cell proof surfaces with bounded actor contracts so a child cell can run as a bounded recursive execution container and return its output to parent/Root boundaries.

A Fractal Cell must not become Root. A child cell is a bounded execution container that may produce ResultProposal-like output, validation reports, GT/advisory reports, and cell boundary reports, but it cannot create FinalOutput, grant action permission, bypass parent boundaries, or claim final authority.

## 3. Implementation decision

Future implementation seam:

- add `hedgehog/fractal_cell_integration.py`

This should be a bounded integration adapter around existing runtime surfaces, not a replacement execution engine.

It should compose existing:

- `hedgehog/fractal_dag_executor.py`
- `hedgehog/bounded_actor_contracts.py`
- `hedgehog/post_vv.py`
- `hedgehog/gt_validator.py`
- existing PlanGraph / ResultProposal boundaries
- existing RootOrchestrator boundary concepts
- DRS / AVF / advisory candidate context as signals only

Do not replace:

- RootOrchestrator
- fractal_dag_executor
- bounded_actor_contracts
- Architect
- Executor
- Post V&V
- GTValidator

Do not create new schema unless a hard blocker is found and a separate schema patch plan is approved.

Repo inspection supports `hedgehog/fractal_cell_integration.py` as the safest seam because `hedgehog/fractal_dag_executor.py` already owns bounded DAG execution and child boundary snapshots, while `hedgehog/bounded_actor_contracts.py` already owns role transition and target-boundary checks. The future layer should wrap and validate those outputs rather than duplicate executor logic or move Root behavior.

## 4. Future allowed implementation files

Expected future implementation files:

- `hedgehog/fractal_cell_integration.py`
- `demo/run_fractal_cell_runtime_integration_v01.py`
- `tests/test_fractal_cell_runtime_integration_v01_runner.py`

No schema changes are expected for v0.1.

If a schema change is proposed, it is deferred and requires a separate schema patch plan.

## 5. Future cell model v0.1

The future implementation should define conceptual data structures and functions equivalent to:

- `FractalCellInput`
- `FractalCellBoundary`
- `FractalCellResult`
- `FractalCellTrace`
- `FractalCellBoundaryReport`
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
- max_cell_depth
- current_cell_depth
- max_child_cells_per_parent
- network_allowed: false
- gemini_allowed: false
- external_action_allowed: false
- child_root_claimed: false

`FractalCellBoundary` should preserve:

- cell_id
- parent_cell_id
- parent_route_id
- boundary_kind
- current_cell_depth
- max_cell_depth
- max_child_cells_per_parent
- accepted_actor_transitions
- blocked_actor_transitions
- root_review_required: true
- parent_return_required: true

`FractalCellResult` should preserve:

- cell_id
- parent_cell_id
- child_result_proposal_ref
- child_validation_report_ref
- child_gt_advisory_ref
- trace refs
- lineage refs
- reason codes
- final_output_claimed: false
- action_permission_claimed: false
- root_authority_claimed: false
- child_root_claimed: false
- root_review_required: true

`FractalCellTrace` should preserve:

- trace_id
- parent_route_id
- cell_lineage
- child_actor_transition_refs
- child_result_refs
- parent_return_refs
- recursion_guard_refs
- blocked_transition_refs
- root_review_required: true

`FractalCellBoundaryReport` should preserve:

- report_id
- cells_started_count
- child_actor_inputs_seen_count
- child_actor_outputs_emitted_count
- child_result_proposals_count
- child_validation_reports_count
- child_gt_reports_count
- parent_return_reports_count
- blocked_transitions
- recursion_guard_results
- root_review_required: true
- final_output_created_count: 0
- action_permission_granted_count: 0
- root_final_authority_preserved: true

## 6. Canonical topology

Future implementation must preserve this topology:

```text
Parent Root / Orchestrator
-> Root-shaped task / route
-> Fractal Cell boundary
-> bounded child actor chain
   - child Intake if needed
   - child Orchestrator
   - child Architect
   - child Executor
   - child Verifier / Post V&V boundary
   - child GT / advisory boundary
-> child bounded ResultProposal / cell report
-> parent Post V&V / GT route
-> parent Root final review
```

Required topology boundaries:

- child cell is not Root
- child Orchestrator is not Root
- child Architect is not Root
- child Executor is not Root
- child GT/advisory boundary is not Root Final
- child output returns upward
- parent Root remains final authority

## 7. Integration with bounded actor contracts

Future implementation must use or compose:

- `hedgehog/bounded_actor_contracts.py`
- ActorInputEnvelope
- ActorOutputEnvelope
- ActorTransitionCheck
- ActorBoundaryReport

Canonical accepted chain inside child cell:

- intake -> Root/Orchestrator
- Root-shaped route -> Architect
- PlanGraph -> Executor
- ResultProposal -> Verifier/Post V&V
- VVReport -> GT boundary
- GTReport -> Root return
- Root return -> Root/Orchestrator

Fractal Cell integration must reuse these contracts, not bypass them.

Target Boundary Fix:

It is not enough to check what a child actor outputs; the system must check where child output is being sent.

Dangerous transitions must remain blocked:

- child Architect PlanGraph -> final_output
- child Executor ResultProposal -> final_output
- child Verifier VVReport -> final_output
- child GTReport -> final_output
- child GTReport -> parent Architect command
- child Root return -> user FinalOutput

The future layer should treat any attempt to route child artifacts into final-output targets, parent Architect commands, or user-final boundaries as blocked child-boundary violations. A child actor output may be well-shaped and still unsafe if the target boundary is wrong.

## 8. Fractal DAG executor integration

Existing Fractal DAG reusable surface:

- `hedgehog/fractal_dag_executor.py` provides `run_fractal_dag_executor(...)`.
- It returns a report-shaped dictionary backed by the local `RunnerReport` concept.
- It already records `status`, `plan_id`, `ready_sequence`, `execution_batches`, `result_proposals`, `child_boundary_snapshots`, bounded graph counters, blocked node details, and safety flags such as `no_real_external_action` and `executor_created_final_output`.
- It already emits ResultProposal-shaped rows for executed nodes and child boundary snapshots for nested / child executor behavior.

Existing output shape:

- `result_proposals` are proposal dictionaries with fields such as `proposal_id`, `producer`, `vector_id`, `plan_id`, `result_payload`, `evidence`, `cost`, `risks`, `time_envelope`, and `trace_refs`.
- `child_boundary_snapshots` preserve child boundary observations and must remain snapshots/reports, not final outputs.
- Runner-level status fields summarize bounded execution, graph validity, and blocked conditions.

Mapping plan:

- Map each atomic Fractal DAG ResultProposal row to a child ResultProposal reference in `FractalCellResult`.
- Map child boundary snapshots to `FractalCellBoundary` / `FractalCellTrace` references.
- Map the runner status and counters into `FractalCellBoundaryReport`.
- Preserve PlanGraph and ResultProposal refs rather than copying payloads into authority-bearing fields.
- Preserve DRS / AVF / advisory refs only as signals.

Validation before parent accepts child output:

- Validate cell input flags before execution: no network, no Gemini, no external action, no child Root claim, bounded recursion settings present.
- Validate child actor transitions using bounded actor contracts.
- Validate Fractal DAG ResultProposal-like output before it enters parent Post V&V.
- Route child output through parent Post V&V / GT boundary before parent Root review.
- Reject or degrade any report claiming FinalOutput, action permission, Root authority, child Root authority, manifest mutation, transition matrix mutation, network use, Gemini use, or connector side effects.

Avoid duplicating Fractal DAG executor:

- Call the existing `run_fractal_dag_executor(...)` for bounded DAG behavior.
- Keep `fractal_cell_integration.py` focused on input validation, recursion bounds, actor contract composition, output mapping, parent-return enforcement, and counters.
- Do not change `fractal_dag_executor.py` in v0.1 unless a hard blocker is found and separate patch approval is requested.

Prevent Fractal DAG executor output from becoming FinalOutput:

- Treat every Fractal DAG output as ResultProposal-like or report-like only.
- Require parent Post V&V / GT route before parent Root review.
- Use bounded actor target-boundary checks to block final-output aliases.
- Keep RootOrchestrator as the only final-output authority.

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
- child cell cannot create authority through recursion
- child consensus is not Root Final
- child majority vote is not authority
- child compute volume is not authority

## 10. Recursion / nesting guardrails

Future implementation must include guardrails:

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

The future proof should include both accepted bounded-recursion cases and blocked recursion-escape cases. A child cell must not create a new Root by nesting, agreement, majority, volume, or repeated output.

## 11. Prompt injection / role confusion guardrails

Future implementation must enforce:

- prompt injection cannot promote child actor to Root
- prompt injection cannot turn child cell into Root
- child actor cannot command parent Architect
- child actor cannot bypass parent Post V&V / GT
- child actor cannot treat DRS memory as instruction authority
- child actor cannot treat AVF advisory as command
- child actor cannot treat previous child output as permission
- child actor cannot activate network/Gemini/connectors
- child actor cannot create FinalOutput

Prompt-like payloads, raw DRS memories, AVF/advisory signals, prior child outputs, or model-confidence-style metadata must be treated as untrusted inputs unless Root-shaped and boundary-validated.

## 12. Future proof scenarios

1. root_shaped_task_enters_fractal_cell_boundary
   - input setup: Parent Root/Orchestrator creates a Root-shaped task with bounded cell depth and no network/Gemini/external-action permission.
   - child role/cell involved: Fractal cell boundary plus child Orchestrator.
   - expected allowed output: cell input accepted and converted to bounded child actor envelopes.
   - expected blocked behavior: raw user text or non-Root-shaped task cannot enter as child command.
   - expected reason codes: root_shaped_task_required, child_cell_boundary_accepted.
   - authority invariant tested: Fractal Cell is not Root.

2. child_architect_accepts_only_root_shaped_task
   - input setup: child Architect receives one Root-shaped route and one raw AVF/advisory command.
   - child role/cell involved: child Architect.
   - expected allowed output: Root-shaped route can produce a PlanGraph proposal.
   - expected blocked behavior: raw AVF/advisory command and DRS memory command are blocked.
   - expected reason codes: architect_requires_root_shaped_task, raw_advisory_command_blocked, raw_drs_memory_instruction_blocked.
   - authority invariant tested: child Architect is not Root.

3. child_executor_outputs_resultproposal_only
   - input setup: child Executor receives bounded PlanGraph and an attempted final-output target.
   - child role/cell involved: child Executor.
   - expected allowed output: ResultProposal-like output routed to Verifier/Post V&V.
   - expected blocked behavior: any Executor output routed to final_output is blocked.
   - expected reason codes: resultproposal_must_route_to_verifier, final_output_target_boundary_blocked.
   - authority invariant tested: child ResultProposal is not FinalOutput.

4. child_verifier_validates_without_finaloutput
   - input setup: child Verifier receives ResultProposal-like output from child Executor.
   - child role/cell involved: child Verifier / Post V&V boundary.
   - expected allowed output: validation report / VVReport routed to GT boundary.
   - expected blocked behavior: verifier cannot create Root Final or final-output target.
   - expected reason codes: vv_report_must_route_to_gt_boundary, final_output_target_boundary_blocked.
   - authority invariant tested: child actor output is not FinalOutput.

5. child_gt_report_returns_to_parent_root_boundary
   - input setup: child GT/advisory boundary receives child VVReport.
   - child role/cell involved: child GT/advisory boundary.
   - expected allowed output: GTReport/advisory report routed to Root return / parent boundary.
   - expected blocked behavior: child GTReport cannot route to final_output or command parent Architect.
   - expected reason codes: gt_report_must_route_to_root_return, parent_architect_command_blocked.
   - authority invariant tested: child GT/advisory report is not Root Final.

6. child_finaloutput_claim_is_blocked
   - input setup: child actor output sets final_output_claimed or routes to final_output alias.
   - child role/cell involved: child Architect, Executor, Verifier, GT boundary.
   - expected allowed output: none for the unsafe claim.
   - expected blocked behavior: output is rejected and counted as final-output claim attempt.
   - expected reason codes: final_output_claim_blocked, final_output_target_boundary_blocked.
   - authority invariant tested: child actor output is not FinalOutput.

7. child_actor_self_promotion_to_root_is_blocked
   - input setup: child actor payload claims Root role or child_root_claimed.
   - child role/cell involved: any child actor.
   - expected allowed output: none for self-promotion.
   - expected blocked behavior: self-promotion blocked and routed to parent review.
   - expected reason codes: child_root_claim_blocked, actor_self_promotion_blocked.
   - authority invariant tested: child Orchestrator is not Root.

8. child_cell_cannot_command_parent_architect
   - input setup: child GTReport or child Root return attempts target parent Architect command.
   - child role/cell involved: child GT boundary / child root_return.
   - expected allowed output: parent-return report only.
   - expected blocked behavior: parent Architect command blocked.
   - expected reason codes: parent_architect_command_blocked, root_boundary_required.
   - authority invariant tested: child cell output must return to parent/Root boundary.

9. recursive_child_cell_depth_is_bounded
   - input setup: child cell invocation attempts current_cell_depth beyond max_cell_depth.
   - child role/cell involved: nested Fractal cell boundary.
   - expected allowed output: bounded invocation accepted only within configured depth.
   - expected blocked behavior: depth overflow and unbounded child spawn blocked.
   - expected reason codes: recursive_depth_limit_blocked, unbounded_child_spawn_blocked.
   - authority invariant tested: recursive nesting depth must be bounded.

10. child_consensus_does_not_create_authority
   - input setup: multiple child cells agree on the same advisory result.
   - child role/cell involved: multiple bounded child cells.
   - expected allowed output: parent-return reports with advisory/candidate evidence.
   - expected blocked behavior: child consensus cannot become Root Final or action permission.
   - expected reason codes: child_consensus_not_authority, root_review_required.
   - authority invariant tested: child_consensus_does_not_create_authority.

11. child_output_returns_to_parent_post_vv_gt_route
   - input setup: child Executor returns ResultProposal-like output through child verification.
   - child role/cell involved: child Executor, child Verifier, child GT boundary, parent Post V&V / GT route.
   - expected allowed output: child bounded report returns to parent validation route.
   - expected blocked behavior: parent boundary bypass blocked.
   - expected reason codes: parent_return_required, parent_boundary_bypass_blocked.
   - authority invariant tested: child cell output must return to parent/Root boundary.

12. root_final_authority_preserved_across_fractal_cell
   - input setup: full bounded child chain from Root-shaped task through parent return.
   - child role/cell involved: full child actor chain and parent Root return.
   - expected allowed output: bounded cell report with Root review required.
   - expected blocked behavior: any final-output/action/authority claim remains zero.
   - expected reason codes: root_final_authority_preserved, root_review_required.
   - authority invariant tested: root_final_authority_preserved_across_fractal_cell.

## 13. Future counters

Future proof counters:

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

- scenarios_total == 12
- scenarios_passed == scenarios_total
- all authority/action/final-output/bypass/mutation/network/recursion-escape counts == 0
- root_final_authority_preserved_count == scenarios_total

The zero-required count group includes:

- final_output_created_count
- action_permission_granted_count
- child_root_claimed_count
- child_authority_claimed_count
- child_finaloutput_claimed_count
- child_action_permission_claimed_count
- child_actor_self_promotion_count
- parent_boundary_bypass_count
- post_vv_bypass_count
- gt_bypass_count
- parent_architect_commanded_count
- recursive_depth_limit_exceeded_count
- unbounded_child_spawn_count
- child_consensus_authority_claimed_count
- manifest_mutation_count
- transition_matrix_mutation_count
- network_used_count
- gemini_used_count
- connector_side_effect_count

## 14. Future validation plan

Future implementation should run targeted validation only inside Codex:

```bash
python3 -m demo.run_fractal_cell_runtime_integration_v01

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_fractal_cell_runtime_integration_v01_runner.py \
  tests/test_fractal_dag_executor_core_runner.py \
  tests/test_bounded_llm_slm_actors_v01_runner.py \
  tests/test_post_vv_runtime.py \
  tests/test_gt_validator_runtime.py
```

Do not instruct Codex to run full pytest.

Because this future patch will add runtime-facing code, full pytest must be run separately by the user before commit and before closure/docs sync.

## 15. Non-goals

- no production Fractal Cell runtime
- no production distributed runtime
- no external/global DRS
- no network
- no Gemini
- no real model calls
- no autonomous action
- no connector side effects
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

## 16. Recommended next step

Fractal Cell Runtime Integration v0.1 IMPLEMENTATION
