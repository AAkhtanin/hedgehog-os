# Bounded LLM/SLM Actors v0.1 — Preflight

## 1. Current checkpoint

- preflight_id: bounded_llm_slm_actors_preflight_v01
- preflight_status: COMPLETE
- current_head_before_layer: 68ca777
- previous_runtime_layer: GT/LGT Advisory Evaluator v0.1 / AVF Candidate Advisory Evaluator v0.1
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

This layer begins bounded actor contracts for the next Real Semantic Runtime
MVP stage.

The previous layers produce reviewed memory candidates, candidate vectors, AVF
scores, and advisory candidate review reports. Bounded LLM/SLM Actors v0.1
must define who may consume those signals and what each actor may output.

This preflight exists because Fractal Cell Runtime integration depends on
bounded actor contracts. Without actor contracts, a fractal shell would not
know who may speak, route, propose, execute, verify, or return to Root.

## 3. Non-goals / boundaries

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

## 4. Existing assets found

### RootOrchestrator / route assembly

- file path: `hedgehog/root_orchestrator.py`
- observed role: Root-controlled event processing, route selection, DRS retrieval, AVF/Architect/Executor/Post V&V/GT path, Root FinalOutput creation, local DRS writeback, and optional mock or Gemini-adjacent subordinate paths.
- status: deterministic by default; optional LLM/Gemini paths are subordinate and fallback-controlled.
- already provides: Root-created FinalOutput, final draft selection, direct reuse/reflex/general/full-pipeline routing, mock general LLM gateway path, optional mock/gemini Architect path with local validation and deterministic fallback.
- does not provide yet: explicit reusable actor contract envelopes for Intake, Orchestrator, Architect, Executor, Verifier, and Root return boundary.
- authority status: final authority only at Root; all subordinate outputs are candidate/proposal/advisory.

### Intake classification

- file path: `hedgehog/input_intake.py`
- observed role: local intent classification used before routing.
- status: deterministic.
- already provides: intent kind signal for general request versus certificate demo path.
- does not provide yet: a named `IntakeActorContract` or `ActorInputEnvelope`.
- authority status: candidate/context signal only.

### Architect / PlanGraph generation

- file path: `hedgehog/architect.py`
- observed role: deterministic PlanGraph proposal generation from AttractorPacket.
- status: deterministic by default; optional mock LLM route delegates through `hedgehog/llm_architect.py`.
- already provides: PlanGraph-shaped output from bounded AttractorPacket/candidate vectors, branch steps, executor assignments, and PlanGraph contract alignment.
- does not provide yet: explicit `ArchitectActorContract` that rejects raw advisory commands and accepts only Root-shaped tasks/routes.
- authority status: proposal only; not final authority.

### LLM Architect helper

- file path: `hedgehog/llm_architect.py`
- observed role: mock or Gemini Architect proposal helper with PlanGraph validation.
- status: mock deterministic path by default; Gemini path requires configuration/dependency and is optional/fallback-controlled.
- already provides: `make_plan_graph_with_llm(...)`, local PlanGraph contract validation, retry/containment for invalid Gemini responses, disallowed vector/key checks.
- does not provide yet: general bounded LLM/SLM role contracts across all actors.
- authority status: PlanGraph proposal helper only; not Root, not Executor, not GT, not FinalOutput.

### General LLM gateway

- file path: `hedgehog/llm_gateway.py`
- observed role: subordinate GeneralResponder path for general requests.
- status: mock deterministic by default; Gemini path is optional and config-gated.
- already provides: prompt text that states GeneralResponder is subordinate, cannot create FinalOutput, cannot call tools, and cannot claim external actions.
- does not provide yet: shared actor envelope/counter model.
- authority status: subordinate answer source only; Root still wraps final output.

### Executor / ResultProposal generation

- file path: `hedgehog/executor.py`
- observed role: deterministic execution of PlanGraph nodes into ResultProposal objects.
- status: deterministic/mock.
- already provides: schema-valid ResultProposal outputs, simulated payloads, TimeEnvelope, trace refs, no final_output/answer/raw_user_text keys.
- does not provide yet: explicit `ExecutorActorContract` that rejects any input other than bounded PlanGraph nodes.
- authority status: proposal only; not final authority and not action permission.

### Fractal DAG Executor

- file path: `hedgehog/fractal_dag_executor.py`
- observed role: bounded DAG runner for PlanGraph nodes, including cycle/unknown dependency/max node blocking and child boundary snapshots.
- status: deterministic.
- already provides: bounded execution, ResultProposal-shaped outputs, `executor_created_final_output: false`, `no_real_external_action: true`, child boundary snapshots.
- does not provide yet: full Fractal Cell Runtime integration for the new semantic actor thread.
- authority status: proposal/boundary evidence only; not Root.

### Post V&V / validation report flow

- file path: `hedgehog/post_vv.py`
- observed role: ResultProposal validation before GT.
- status: deterministic and schema-backed.
- already provides: ResultProposal schema validation, forbidden key checks, VVReport schema validation, semantic status/risk scoring.
- does not provide yet: explicit `VerifierActorContract` wrapper over actor outputs.
- authority status: validation/advisory boundary only.

### GTValidator / GT boundary

- file path: `hedgehog/gt_validator.py`
- observed role: payoff, classification, selection, and GT report creation from VV reports.
- status: deterministic.
- already provides: accept/revise/reject/no_update style selection, payoff components, report semantics.
- does not provide yet: bounded actor contract model for GT-style signals before Fractal Cell integration.
- authority status: advisory/selection; Root remains final authority.

### AVF Candidate Advisory Evaluator

- file path: `hedgehog/gt_lgt_advisory_evaluator.py`
- observed role: pre-Architect candidate-level advisory review over AVF-ranked DRS candidates.
- status: deterministic local runtime layer.
- already provides: `AdvisoryEvaluationInput`, `AdvisorySignal`, `GTLGTAdvisoryReport`, GT-style advisory decisions, LGT deferred/local placeholder, direct reuse/action/final-output counters at zero.
- does not provide yet: actor topology contracts for who may consume advisory reports and who may call Architect.
- authority status: advisory only.

### Candidate vectors and local semantic DRS

- file paths: `hedgehog/candidate_vector_generator.py`, `hedgehog/local_drs_resolver.py`
- observed role: local semantic memory candidates, bounded candidate vectors, deterministic AVF scoring, ranked/reviewable reports.
- status: deterministic local runtime layers.
- already provides: candidate-only memory and ranking signals with Root review required.
- does not provide yet: actor envelope routing from advisory reports to Root-shaped routes.
- authority status: candidate/advisory only.

### Existing Bounded LLM Semantic Executor Node proof

- file paths: `demo/run_bounded_llm_semantic_executor_node_v01.py`, `tests/test_bounded_llm_semantic_executor_node_v01_runner.py`, `demo/run_human_bounded_llm_semantic_executor_node_walkthrough_v01.py`
- observed role: older proof for a bounded mock LLM semantic executor node.
- status: deterministic/mock proof; not this runtime-facing actor-contract layer.
- already provides: mock LLM executor node envelope, semantic draft, ResultProposal wrapper, Post V&V, GT advisory, Root final authority checks, adversarial role-escalation blocking.
- does not provide yet: canonical reusable actor contracts for Intake, Orchestrator, Architect, Executor, Verifier, and Root return.
- authority status: proof-local proposal/advisory evidence only.

### Optional live Gemini smoke surfaces

- file paths: `demo/run_live_gemini_architect_smoke.py`, `demo/run_live_gemini_orchestrator_smoke.py`, `demo/run_live_gemini_ordered_orchestrator_architect_smoke.py`, `demo/run_live_child_executor_in_fractal_cell.py`, `tests/test_live_gemini_architect_smoke_runner.py`, `tests/test_live_gemini_orchestrator_smoke_runner.py`, `tests/test_live_gemini_ordered_orchestrator_architect_smoke_runner.py`
- observed role: opt-in smoke surfaces for Gemini role substitution or child Executor experiments.
- status: optional live smoke only; default modes are deterministic/network-free or skip without config.
- already provides: role flags, opt-in gates such as `HEDGEHOG_ALLOW_LIVE_GEMINI`, local validation, containment, fallback, and no Root final authority transfer.
- does not provide yet: default runtime actor contracts for the Real Semantic Runtime MVP.
- authority status: smoke/proposal only; not production.

### Schemas and tests for canonical boundaries

- file paths: `schemas/plan_graph.schema.json`, `schemas/result_proposal.schema.json`, `schemas/final_output.schema.json`, `schemas/attractor_packet.schema.json`, `tests/test_architect_runtime.py`, `tests/test_executor_runtime.py`, `tests/test_post_vv_runtime.py`, `tests/test_gt_validator_runtime.py`, `tests/test_root_orchestrator_runtime.py`, `tests/test_llm_architect_runtime.py`
- observed role: schema/test coverage for PlanGraph, ResultProposal, Root FinalOutput, AttractorPacket, and optional LLM Architect containment.
- status: deterministic focused tests; no schema change expected for v0.1 actor preflight.
- already provides: active PlanGraph/ResultProposal/FinalOutput contracts and checks that Root creates FinalOutput.
- does not provide yet: an actor-contract schema or proof-local envelope.
- authority status: contract validation only.

## 5. Required actor topology

Canonical topology for future implementation:

- Root / RootOrchestrator
- Intake Actor
- Route / Orchestrator Actor
- Architect Actor
- Executor Actor
- Verifier Actor / Post V&V boundary
- GT / GT-style advisory boundary
- Root return boundary

Required topology rules:

- Root/Orchestrator owns route decision.
- Intake may normalize request/context only.
- Candidate Advisory Evaluator may emit advisory signals only.
- Architect receives only Root-shaped tasks/routes.
- Architect outputs PlanGraph proposal only.
- Executor executes only bounded PlanGraph.
- Executor returns ResultProposal-like bounded output only.
- Post V&V validates ResultProposal-like output.
- GTValidator remains downstream after Executor/Post V&V.
- Root creates FinalOutput.
- No actor below Root may create FinalOutput.
- No actor may grant action permission.

## 6. Actor role contracts v0.1

Future conceptual contracts should be local dataclasses or repo-style structured
objects. This preflight does not implement them.

Expected future concepts:

- `BoundedActorRole`
- `ActorInputEnvelope`
- `ActorOutputEnvelope`
- `IntakeActorContract`
- `OrchestratorActorContract`
- `ArchitectActorContract`
- `ExecutorActorContract`
- `VerifierActorContract`
- `ActorBoundaryReport`

### Intake Actor

Allowed inputs:

- user/event text routed by Root
- session and TimeEnvelope context
- local context references approved for intake

Allowed outputs:

- structured intent candidate
- normalized request/context summary
- missing-information flags
- TimeEnvelope/context references

Forbidden:

- final decision
- tool/action execution
- direct DRS write authority
- FinalOutput

### Orchestrator Actor

Allowed inputs:

- Root-approved request/context envelope
- DRS/AVF/advisory reports
- route constraints and permission state

Allowed outputs:

- Root-shaped route proposal
- Architect / Executor path request
- user clarification request
- route proposal returned to Root

Forbidden:

- direct command to Architect without Root boundary
- final output
- action permission
- manifest/transition mutation

### Architect Actor

Allowed inputs:

- Root-shaped task/route
- AttractorPacket or bounded route context accepted by Root
- approved candidate/vector/AVF context as route input

Allowed outputs:

- PlanGraph proposal
- local validation warnings/reason codes

Forbidden:

- consume raw AVF/advisory command as authority
- execute action
- create FinalOutput
- bypass Post V&V / GT

### Executor Actor

Allowed inputs:

- bounded PlanGraph or bounded PlanGraph node
- executor assignment and budget constraints

Allowed outputs:

- ResultProposal-like bounded output
- execution evidence and trace refs
- needs_user/blocked/degraded status when applicable

Forbidden:

- create FinalOutput
- execute external real action
- bypass Post V&V
- claim Root authority

### Verifier Actor / Post V&V boundary

Allowed inputs:

- ResultProposal-like bounded output
- schema and policy validation context
- trace/evidence references

Allowed outputs:

- validation/advisory report
- needs_revision/reject/accept-style validation signal
- reason codes and safety findings

Forbidden:

- create Root Final
- grant action permission

## 7. LLM / SLM status and safe default

Existing real LLM/Gemini mentions or call-capable paths:

- `hedgehog/llm_architect.py` can call Gemini only when provider is `gemini` and configuration/dependency exists.
- `hedgehog/llm_gateway.py` can call Gemini for GeneralResponder only when provider is `gemini`.
- `demo/run_live_gemini_architect_smoke.py`, `demo/run_live_gemini_orchestrator_smoke.py`, `demo/run_live_gemini_ordered_orchestrator_architect_smoke.py`, `demo/run_live_child_executor_in_fractal_cell.py`, and related tests document optional live smoke surfaces.
- `demo/run_gemini_orchestrator_architect_pair_smoke.py` and `demo/run_live_gemini_orchestrator_shadow.py` are additional live-capable smoke/shadow paths.

Mock/deterministic paths:

- `hedgehog/architect.py` deterministic PlanGraph path.
- `hedgehog/llm_architect.py` provider `mock`, with `used_llm: false`.
- `hedgehog/llm_gateway.py` provider `mock`, with `used_llm: false`.
- `hedgehog/executor.py`, `hedgehog/fractal_dag_executor.py`, `hedgehog/post_vv.py`, `hedgehog/gt_validator.py`, and `hedgehog/gt_lgt_advisory_evaluator.py`.
- `demo/run_bounded_llm_semantic_executor_node_v01.py` uses `bounded_mock_llm` / `mock_llm`.

Optional live smoke only:

- live Gemini Architect, Orchestrator, ordered Orchestrator-to-Architect, shadow, pair, Telegram benchmark, and live child Executor surfaces are opt-in or explicitly live-capable smoke paths. They must remain separate from this v0.1 layer.

Production status:

- no production LLM actor runtime was found
- no production SLM actor runtime was found
- no concrete SLM runtime was found

Safe default for v0.1:

- Use deterministic/mock local actor contracts first.
- Treat LLM/SLM as role-capable but not activated.
- Any real model call requires separate explicit opt-in and is not part of this layer.
- No Gemini/network call in v0.1 proof.
- No actor may become authority because it is LLM or SLM.

## 8. Proposed implementation seam

Preferred future seam:

- add `hedgehog/bounded_actor_contracts.py`

It should compose existing:

- RootOrchestrator route concepts
- Architect PlanGraph boundary
- Executor ResultProposal boundary
- Post V&V / GT boundary
- AVF Candidate Advisory Evaluator output shape
- DRS resolver/candidate refs where useful

Do not replace RootOrchestrator. Do not modify Architect. Do not modify
Executor. Do not modify GTValidator. Do not modify schemas unless a hard
blocker is found and a separate schema patch plan is approved.

The safest v0.1 implementation should be a contract adapter/validator, not a
new execution engine. It should produce proof-local actor envelopes and a
boundary report while continuing to rely on existing active schemas for
PlanGraph, ResultProposal, VVReport, GT report, and FinalOutput.

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

Because this layer will define bounded actors, these guardrails are acceptance
criteria for Bounded LLM/SLM Actors v0.1:

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

## 11. Proposed future proof scenarios

1. intake_actor_normalizes_intent_without_authority
   - input setup: raw user/event text plus session/time context.
   - actor role involved: Intake Actor.
   - expected allowed output: structured intent candidate and missing-context flags.
   - expected blocked behavior: final answer, action execution, and DRS write authority.
   - expected reason codes: `intake_candidate_only`, `no_final_output`.
   - authority invariant tested: actor output is not truth.

2. orchestrator_actor_consumes_advisory_report_as_signal_only
   - input setup: AVF Candidate Advisory Evaluator report with accept/degrade/reject/needs-review signals.
   - actor role involved: Orchestrator Actor.
   - expected allowed output: route proposal returned to Root.
   - expected blocked behavior: treating advisory signal as command.
   - expected reason codes: `advisory_signal_only`, `root_route_required`.
   - authority invariant tested: advisory report is not command.

3. orchestrator_route_proposal_requires_root_boundary
   - input setup: Orchestrator route proposal for Architect path.
   - actor role involved: Orchestrator Actor and Root return boundary.
   - expected allowed output: Root-shaped route candidate.
   - expected blocked behavior: direct Architect command.
   - expected reason codes: `root_boundary_required`, `architect_not_directly_commanded`.
   - authority invariant tested: route proposal is not Root decision.

4. architect_actor_accepts_only_root_shaped_task
   - input setup: one Root-shaped task and one raw advisory command.
   - actor role involved: Architect Actor.
   - expected allowed output: accept Root-shaped task.
   - expected blocked behavior: reject raw advisory command.
   - expected reason codes: `root_shaped_task_required`, `raw_advisory_command_blocked`.
   - authority invariant tested: Architect receives only Root-shaped tasks/routes.

5. architect_actor_outputs_plangraph_proposal_only
   - input setup: bounded Architect input envelope.
   - actor role involved: Architect Actor.
   - expected allowed output: PlanGraph proposal.
   - expected blocked behavior: answer, ResultProposal, FinalOutput, action claim.
   - expected reason codes: `plangraph_proposal_only`, `final_output_forbidden`.
   - authority invariant tested: PlanGraph proposal is not execution authority.

6. executor_actor_accepts_only_bounded_plangraph
   - input setup: schema-valid bounded PlanGraph and malformed/raw actor text.
   - actor role involved: Executor Actor.
   - expected allowed output: consume bounded PlanGraph only.
   - expected blocked behavior: raw actor text or unbounded PlanGraph.
   - expected reason codes: `bounded_plangraph_required`, `raw_actor_text_blocked`.
   - authority invariant tested: Executor receives only bounded PlanGraph.

7. executor_actor_outputs_resultproposal_only
   - input setup: bounded PlanGraph node.
   - actor role involved: Executor Actor.
   - expected allowed output: ResultProposal-like bounded output.
   - expected blocked behavior: FinalOutput, external action, Root authority claim.
   - expected reason codes: `resultproposal_only`, `external_action_forbidden`.
   - authority invariant tested: ResultProposal is not FinalOutput.

8. verifier_actor_validates_without_finaloutput
   - input setup: ResultProposal-like bounded output.
   - actor role involved: Verifier Actor / Post V&V boundary.
   - expected allowed output: validation/advisory report.
   - expected blocked behavior: Root Final or action permission.
   - expected reason codes: `validation_report_only`, `root_final_forbidden`.
   - authority invariant tested: Post V&V / GT remains downstream validation/advisory boundary.

9. prompt_injection_cannot_promote_actor_to_root
   - input setup: prompt text claiming actor should become Root.
   - actor role involved: all bounded actor roles.
   - expected allowed output: rejection/blocked reason.
   - expected blocked behavior: role promotion.
   - expected reason codes: `prompt_injection_blocked`, `root_role_reserved`.
   - authority invariant tested: actor cannot self-promote to Root.

10. actor_role_confusion_is_blocked
    - input setup: Architect asked to execute; Executor asked to route; Verifier asked to finalize.
    - actor role involved: Architect, Executor, Verifier.
    - expected allowed output: role-bound rejection or needs-review signal.
    - expected blocked behavior: cross-role command acceptance.
    - expected reason codes: `actor_role_confusion_is_blocked`, `role_contract_enforced`.
    - authority invariant tested: actor role does not create authority.

11. model_confidence_does_not_create_authority
    - input setup: high-confidence mock/LLM/SLM output.
    - actor role involved: any model-capable actor.
    - expected allowed output: confidence metadata only.
    - expected blocked behavior: confidence as truth or route permission.
    - expected reason codes: `model_confidence_metadata_only`, `authority_not_granted`.
    - authority invariant tested: model confidence is not authority.

12. root_final_authority_preserved_across_actor_chain
    - input setup: full actor envelope chain from intake through verifier/GT-style advisory report.
    - actor role involved: all actor contracts and Root return boundary.
    - expected allowed output: Root review-required boundary report.
    - expected blocked behavior: non-Root FinalOutput and bypassed validation.
    - expected reason codes: `root_final_authority_preserved`, `root_review_required`.
    - authority invariant tested: Root remains final authority.

## 12. Proposed counters for future proof

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

## 13. Risks / decisions needed

- Decide whether actor contracts should be pure dataclasses first, with no schema changes.
- Decide whether to reuse existing route/PlanGraph/ResultProposal schemas or create proof-local envelopes for actor input/output.
- Decide whether the first implementation should build a mock local actor chain or only an actor contract validator.
- Keep optional live Gemini demos separate from this layer; they are not required runtime behavior.
- Avoid duplicating RootOrchestrator logic by making the new seam validate envelopes and role transitions rather than owning route selection.
- Avoid premature Fractal Cell integration; Fractal Cell comes after bounded actor contracts define who may speak, route, propose, execute, verify, and return to Root.
- Because future implementation will add runtime-facing code, decide whether full pytest is required after implementation and before closure/docs sync.

## 14. Recommended next step

Bounded LLM/SLM Actors v0.1 PATCH PLAN
