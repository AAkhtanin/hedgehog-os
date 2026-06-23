# Bounded LLM/SLM Actors v0.1 — Patch Plan

## 1. Current checkpoint

- patch_plan_id: bounded_llm_slm_actors_patch_plan_v01
- patch_plan_status: COMPLETE
- preflight_commit: a0e3145
- current_head_before_patch: a0e3145
- roadmap_block: Real Semantic Runtime MVP
- previous_runtime_layer: GT/LGT Advisory Evaluator v0.1 / AVF Candidate Advisory Evaluator v0.1
- next_later_layer: Fractal Cell Runtime integration after bounded actor contracts
- runtime_gate_commit: 1e1afe6
- implementation_started: false
- runtime_modified: false
- schemas_modified: false
- tests_created: false
- demos_created: false
- full_pytest_run: false

## 2. Purpose

This patch plan defines the future implementation of bounded actor contracts for Intake, Orchestrator, Architect, Executor, Verifier/Post V&V, GT boundary, and Root return boundary.

The goal is not to create autonomous actors. The goal is to define role envelopes and role transition checks so later Fractal Cell Runtime integration knows who may speak, route, propose, execute, verify, and return to Root.

Current semantic runtime thread:

```text
Real Local DRS Resolver
-> CandidateVectorGenerator
-> AVF scoring
-> AVF Candidate Advisory Evaluator
-> Root/Orchestrator route decision required
-> Bounded actor contracts now needed
-> Fractal Cell Runtime integration later
```

Core boundary:

- LLM/SLM actor output is not truth.
- LLM/SLM actor output is not authority.
- LLM/SLM actor output is not action permission.
- LLM/SLM actor output is not FinalOutput.
- Actor role does not create authority.
- Tool capability does not create permission.
- Architect receives only Root-shaped tasks/routes.
- Executor returns ResultProposal-like bounded outputs only.
- Post V&V / GT remains downstream validation/advisory boundary.
- Root remains final authority.

## 3. Implementation decision

Future implementation seam:

- add `hedgehog/bounded_actor_contracts.py`

This module should be a contract adapter / validator, not a new execution engine. It should define proof-local actor envelopes, validate role inputs and outputs, and report allowed or blocked role transitions without replacing existing runtime stages.

It should compose existing:

- RootOrchestrator route concepts from `hedgehog/root_orchestrator.py`
- input_intake deterministic classification from `hedgehog/input_intake.py`
- Architect / PlanGraph boundary from `hedgehog/architect.py`
- Executor / ResultProposal boundary from `hedgehog/executor.py` and `hedgehog/fractal_dag_executor.py`
- Post V&V / VVReport boundary from `hedgehog/post_vv.py`
- GTValidator / GTReport boundary from `hedgehog/gt_validator.py`
- AVF Candidate Advisory Evaluator output shape from `hedgehog/gt_lgt_advisory_evaluator.py`
- DRS resolver / candidate refs from `hedgehog/local_drs_resolver.py` and CandidateVectorGenerator refs from `hedgehog/candidate_vector_generator.py`

Do not replace:

- RootOrchestrator
- Architect
- Executor
- Post V&V
- GTValidator
- AVF Candidate Advisory Evaluator

Do not modify schemas unless a hard blocker is found and a separate schema patch plan is approved.

## 4. Future allowed implementation files

Expected future implementation files:

- `hedgehog/bounded_actor_contracts.py`
- `demo/run_bounded_llm_slm_actors_v01.py`
- `tests/test_bounded_llm_slm_actors_v01_runner.py`

No schema changes are expected for v0.1.

If schema changes are proposed, they must be deferred and require a separate schema patch plan.

## 5. Actor contract model v0.1

Future conceptual dataclasses and functions:

- `BoundedActorRole`
- `ActorInputEnvelope`
- `ActorOutputEnvelope`
- `ActorTransitionCheck`
- `ActorBoundaryReport`
- `validate_actor_input(...)`
- `validate_actor_output(...)`
- `validate_actor_transition(...)`
- `build_actor_boundary_report(...)`

Expected roles:

- `intake`
- `orchestrator`
- `architect`
- `executor`
- `verifier`
- `gt_boundary`
- `root_return`

`ActorInputEnvelope` should preserve:

- role
- input_kind
- source_boundary
- payload_ref
- root_shaped_task
- route_id
- plan_graph_ref
- result_proposal_ref
- advisory_report_ref
- time_envelope / context refs
- permission_scope
- network_allowed: false
- gemini_allowed: false
- external_action_allowed: false

`ActorOutputEnvelope` should preserve:

- role
- output_kind
- payload_ref
- reason_codes
- truth_claimed: false
- authority_claimed: false
- action_permission_claimed: false
- final_output_claimed: false
- direct_tool_call_claimed: false
- manifest_mutation_claimed: false
- transition_matrix_mutation_claimed: false
- root_review_required: true

`ActorTransitionCheck` should preserve:

- source_role
- target_role
- input_kind
- output_kind
- transition_allowed
- blocked_reason_codes
- root_boundary_required
- post_vv_required
- gt_boundary_required
- root_review_required

`ActorBoundaryReport` should preserve:

- report_id
- actor_inputs_seen_count
- actor_outputs_emitted_count
- accepted_transitions
- blocked_transitions
- reason_codes
- root_review_required: true
- final_output_created_count: 0
- action_permission_granted_count: 0
- root_final_authority_preserved: true

## 6. Actor role contracts

### Intake Actor

Allowed:

- parse/normalize user intent
- attach TimeEnvelope/context refs
- flag missing information
- return structured intent candidate

Forbidden:

- final decision
- tool/action execution
- direct DRS write authority
- FinalOutput

### Orchestrator Actor

Allowed:

- consume DRS/AVF/advisory reports as signals
- propose Root-shaped route
- request Architect/Executor path
- request user clarification
- return route proposal to Root

Forbidden:

- direct command to Architect without Root boundary
- final output
- action permission
- manifest mutation
- transition matrix mutation

### Architect Actor

Allowed:

- consume Root-shaped task/route only
- produce PlanGraph proposal only

Forbidden:

- consume raw AVF/advisory command as authority
- execute action
- create FinalOutput
- bypass Post V&V / GT

### Executor Actor

Allowed:

- consume bounded PlanGraph only
- produce ResultProposal-like bounded output only

Forbidden:

- create FinalOutput
- execute external real action
- bypass Post V&V
- claim Root authority

### Verifier Actor / Post V&V boundary

Allowed:

- validate ResultProposal-like output
- produce validation/advisory report

Forbidden:

- create Root Final
- grant action permission

### GT boundary

Allowed:

- produce GT advisory / selection report

Forbidden:

- create Root Final
- grant action permission
- command Architect or Executor

### Root return boundary

Allowed:

- collect validated/advisory results
- require Root final review

Forbidden:

- allowing child actor to bypass Root

## 7. LLM / SLM activation policy

- no real model calls in v0.1
- no Gemini activation in v0.1
- no network in v0.1
- no production LLM actor runtime in v0.1
- no production SLM actor runtime in v0.1
- optional live Gemini demos remain separate historical/optional smoke paths
- LLM/SLM are role-capable but not activated
- model confidence is advisory metadata only
- being an LLM or SLM does not create authority

The existing repository has deterministic/mock paths for current runtime proofing and separate optional live Gemini smoke surfaces. Bounded LLM/SLM Actors v0.1 should keep the default proof deterministic and local.

## 8. Role transition matrix v0.1

Future implementation should define an explicit role transition table for allowed and blocked paths.

Allowed examples:

- user/context -> intake
- intake output -> Root/Orchestrator review
- Root-shaped route -> Architect
- PlanGraph -> Executor
- ResultProposal -> Post V&V
- VVReport -> GT boundary
- GTReport/advisory -> Root return boundary

Blocked examples:

- raw user text -> Architect
- AVF/advisory signal -> Architect command
- DRS memory -> Architect command
- LLM actor -> direct tool call
- Orchestrator route proposal -> FinalOutput
- Architect PlanGraph -> FinalOutput
- Executor ResultProposal -> FinalOutput
- Verifier report -> FinalOutput
- GT report -> FinalOutput
- any actor -> manifest mutation
- any actor -> transition matrix mutation
- any actor -> network/Gemini/connectors

The transition matrix should report why a transition is blocked instead of attempting fallback execution.

## 9. Required invariants

- actor output is not truth
- actor output is not authority
- actor output is not action permission
- actor output is not FinalOutput
- LLM output is not truth
- SLM output is not truth
- model confidence is not authority
- tool capability is not permission
- route proposal is not Root decision
- PlanGraph proposal is not execution authority
- ResultProposal is not FinalOutput
- advisory report is not command
- Architect receives only Root-shaped tasks/routes
- Executor receives only bounded PlanGraph
- Post V&V / GT remains downstream validation/advisory boundary
- Root remains final authority
- actor cannot mutate manifest
- actor cannot mutate transition matrix
- actor cannot call network/Gemini/connectors in v0.1
- actor cannot execute external actions in v0.1

## 10. Prompt injection / role confusion acceptance criteria

- prompt injection cannot grant action permission
- prompt injection cannot change actor role
- actor cannot self-promote to Root
- actor cannot command another actor outside Root-shaped route
- actor cannot treat AVF/advisory signal as command
- actor cannot treat DRS memory as instruction authority
- actor cannot treat previous output as permission
- model output cannot mutate manifest
- model output cannot mutate transition matrix
- model output cannot bypass Post V&V / GT
- model output cannot create FinalOutput
- model output cannot activate tools/connectors/network

These criteria should be tested as actor-boundary checks, not as live LLM prompts.

## 11. Future proof scenarios

1. `intake_actor_normalizes_intent_without_authority`

   - input setup: raw user/context envelope with no route, no PlanGraph, and no action permission
   - actor role involved: Intake Actor
   - expected allowed output: structured intent candidate with context refs and missing-information flags when needed
   - expected blocked behavior: no final decision, no tool execution, no direct DRS write authority, no FinalOutput
   - expected reason codes: `intent_candidate_only`, `root_review_required`, `no_action_permission`
   - authority invariant tested: actor output is not truth and actor output is not authority

2. `orchestrator_actor_consumes_advisory_report_as_signal_only`

   - input setup: AVF Candidate Advisory Evaluator report plus DRS/candidate refs
   - actor role involved: Orchestrator Actor
   - expected allowed output: Root-shaped route proposal or user-clarification proposal
   - expected blocked behavior: advisory report cannot become a command to Architect or Executor
   - expected reason codes: `advisory_signal_only`, `root_boundary_required`, `route_proposal_only`
   - authority invariant tested: advisory report is not command

3. `orchestrator_route_proposal_requires_root_boundary`

   - input setup: Orchestrator route proposal pointing toward Architect
   - actor role involved: Orchestrator Actor / Root return boundary
   - expected allowed output: route proposal returned to Root review
   - expected blocked behavior: direct handoff to Architect without Root-shaped route
   - expected reason codes: `root_boundary_required`, `direct_architect_command_blocked`
   - authority invariant tested: route proposal is not Root decision

4. `architect_actor_accepts_only_root_shaped_task`

   - input setup: one Root-shaped task and several raw inputs: user text, AVF/advisory signal, DRS memory record
   - actor role involved: Architect Actor
   - expected allowed output: only Root-shaped task is accepted for PlanGraph proposal
   - expected blocked behavior: raw user text, raw advisory signal, and DRS memory as instruction are blocked
   - expected reason codes: `root_shaped_task_required`, `raw_input_blocked`, `memory_not_instruction_authority`
   - authority invariant tested: Architect receives only Root-shaped tasks/routes

5. `architect_actor_outputs_plangraph_proposal_only`

   - input setup: valid Root-shaped task/route envelope
   - actor role involved: Architect Actor
   - expected allowed output: PlanGraph proposal reference
   - expected blocked behavior: Architect cannot execute, create FinalOutput, or bypass Post V&V / GT
   - expected reason codes: `plangraph_proposal_only`, `execution_blocked`, `final_output_blocked`
   - authority invariant tested: PlanGraph proposal is not execution authority

6. `executor_actor_accepts_only_bounded_plangraph`

   - input setup: bounded PlanGraph envelope and invalid raw/unbounded PlanGraph candidates
   - actor role involved: Executor Actor
   - expected allowed output: bounded PlanGraph accepted for deterministic execution path
   - expected blocked behavior: raw Architect text, unvalidated PlanGraph, oversized/unbounded graph, and raw user intent are blocked
   - expected reason codes: `bounded_plangraph_required`, `raw_plan_blocked`, `unbounded_graph_blocked`
   - authority invariant tested: Executor receives only bounded PlanGraph

7. `executor_actor_outputs_resultproposal_only`

   - input setup: accepted bounded PlanGraph
   - actor role involved: Executor Actor
   - expected allowed output: ResultProposal-like bounded output
   - expected blocked behavior: no FinalOutput, no external real action, no Post V&V bypass
   - expected reason codes: `resultproposal_only`, `external_action_blocked`, `post_vv_required`
   - authority invariant tested: ResultProposal is not FinalOutput

8. `verifier_actor_validates_without_finaloutput`

   - input setup: ResultProposal-like output with trace/source refs
   - actor role involved: Verifier Actor / Post V&V boundary
   - expected allowed output: validation/advisory report
   - expected blocked behavior: verifier cannot create Root Final or grant action permission
   - expected reason codes: `validation_report_only`, `root_final_required`, `action_permission_blocked`
   - authority invariant tested: Post V&V / GT remains downstream validation/advisory boundary

9. `prompt_injection_cannot_promote_actor_to_root`

   - input setup: malicious payload instructing Intake, Orchestrator, Architect, or Executor to become Root
   - actor role involved: all non-Root actor contracts
   - expected allowed output: blocked transition report or sanitized candidate output
   - expected blocked behavior: actor role cannot change, Root authority cannot be claimed
   - expected reason codes: `prompt_injection_blocked`, `actor_self_promotion_blocked`, `root_authority_preserved`
   - authority invariant tested: actor cannot self-promote to Root

10. `actor_role_confusion_is_blocked`

   - input setup: role-mismatched envelope, such as Executor receiving advisory report as command or Architect receiving DRS memory as instruction
   - actor role involved: Orchestrator, Architect, Executor, Verifier
   - expected allowed output: no accepted role transition for mismatched input
   - expected blocked behavior: command outside Root-shaped route is blocked
   - expected reason codes: `role_confusion_blocked`, `invalid_source_boundary`, `root_boundary_required`
   - authority invariant tested: actor_role_confusion_is_blocked

11. `model_confidence_does_not_create_authority`

   - input setup: mock LLM/SLM actor output with high confidence metadata
   - actor role involved: any model-capable actor contract
   - expected allowed output: confidence preserved as advisory metadata only
   - expected blocked behavior: confidence cannot grant permission, authority, direct tool call, or final output
   - expected reason codes: `model_confidence_advisory_only`, `authority_claim_blocked`, `tool_permission_blocked`
   - authority invariant tested: model confidence is not authority

12. `root_final_authority_preserved_across_actor_chain`

   - input setup: full local chain envelope from intake candidate to Root return boundary
   - actor role involved: Intake, Orchestrator, Architect, Executor, Verifier, GT boundary, Root return boundary
   - expected allowed output: actor boundary report with root review required and Root final authority preserved
   - expected blocked behavior: no child actor creates FinalOutput, bypasses Root, bypasses Post V&V, or bypasses GT
   - expected reason codes: `root_review_required`, `post_vv_required`, `gt_boundary_required`, `root_final_authority_preserved`
   - authority invariant tested: root_final_authority_preserved_across_actor_chain

## 12. Future counters

Expected counters:

- scenarios_total
- scenarios_passed
- actor_inputs_seen_count
- actor_outputs_emitted_count
- intake_outputs_count
- route_proposals_count
- plangraph_proposals_count
- result_proposals_count
- validation_reports_count
- root_review_required_count
- final_output_created_count: 0
- action_permission_granted_count: 0
- actor_authority_claimed_count: 0
- llm_truth_claimed_count: 0
- slm_truth_claimed_count: 0
- model_confidence_authority_claimed_count: 0
- prompt_injection_escalation_count: 0
- actor_self_promotion_count: 0
- raw_advisory_command_accepted_count: 0
- raw_drs_memory_instruction_accepted_count: 0
- root_boundary_bypass_count: 0
- post_vv_bypass_count: 0
- gt_bypass_count: 0
- manifest_mutation_count: 0
- transition_matrix_mutation_count: 0
- network_used_count: 0
- gemini_used_count: 0
- connector_side_effect_count: 0
- root_final_authority_preserved_count

Required PASS conditions:

- scenarios_total == 12
- scenarios_passed == scenarios_total
- final_output_created_count == 0
- action_permission_granted_count == 0
- actor_authority_claimed_count == 0
- llm_truth_claimed_count == 0
- slm_truth_claimed_count == 0
- model_confidence_authority_claimed_count == 0
- prompt_injection_escalation_count == 0
- actor_self_promotion_count == 0
- raw_advisory_command_accepted_count == 0
- raw_drs_memory_instruction_accepted_count == 0
- root_boundary_bypass_count == 0
- post_vv_bypass_count == 0
- gt_bypass_count == 0
- manifest_mutation_count == 0
- transition_matrix_mutation_count == 0
- network_used_count == 0
- gemini_used_count == 0
- connector_side_effect_count == 0
- root_final_authority_preserved_count == scenarios_total

## 13. Future validation plan

Future implementation should run targeted validation only inside Codex:

```bash
python3 -m demo.run_bounded_llm_slm_actors_v01

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_bounded_llm_slm_actors_v01_runner.py \
  tests/test_architect_runtime.py \
  tests/test_executor_runtime.py \
  tests/test_post_vv_runtime.py \
  tests/test_gt_validator_runtime.py \
  tests/test_root_orchestrator_runtime.py
```

Do not instruct Codex to run full pytest.

Because this future patch will add runtime-facing code, full pytest must be run separately by the user before commit and before closure/docs sync.

## 14. Non-goals

- no production LLM autonomy
- no production SLM autonomy
- no real model calls
- no Gemini activation
- no network
- no embeddings
- no external tool calls
- no connector side effects
- no autonomous action
- no Fractal Cell Runtime integration in this layer
- no Root behavior modification
- no Architect command from AVF/advisory evaluator
- no Executor command from LLM actor without Root-shaped route
- no FinalOutput creation
- no action permission
- no direct reuse permission
- no manifest mutation
- no transition matrix mutation
- no Marennya/UP
- no public WOW
- no whitepaper/public auditor packet
- Real Semantic Runtime MVP is not complete

## 15. Recommended next step

Bounded LLM/SLM Actors v0.1 IMPLEMENTATION
