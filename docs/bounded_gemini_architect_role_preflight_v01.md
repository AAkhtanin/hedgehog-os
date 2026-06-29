# Bounded Gemini Architect Proposal Role v0.1 Preflight

preflight_id: bounded_gemini_architect_role_preflight_v01
preflight_status: COMPLETE
base_head: eabe9f7
planning_only: true
runtime_created: false
tests_created: false
audit_log_created: false
existing_full_e2e_runner_will_be_extended: true
separate_runner_allowed: false
separate_patch_plan_required: false
commit_created: false

## Purpose

Plan the next runtime layer where Gemini may act as a bounded Architect proposal role inside the existing Full Semantic E2E supplier-payment spine.

This is not public WOW.
This is not production.
This is not NeedleFactory.
This is not Marennya / UP.
This is not dual Gemini Orchestrator+Architect runtime yet.

Closed base:
- Bounded Gemini Orchestrator Proposal Role is closed at preflight fe86aa8, runtime 239a0cf, real provider counter fix 64cf778, and audit eabe9f7.
- Full Semantic E2E has invoked DRS, CandidateVector, AVF, advisory, bounded Orchestrator route, deterministic Architect, PlanGraph validation, Fractal executor, ResultProposal, Post V&V, GT/LGT, Root boundary, and local DRS writeback.
- Live evidence influence is closed: real Gemini can create a validated candidate-only SemanticEvidenceClaim that influences supplier, DRS, CandidateVector, and AVF contexts without becoming truth or authority.

## Canonical Placement

User / dirty business request
-> live evidence reader / SemanticEvidenceClaim
-> DRS candidate context
-> CandidateVector
-> AVF/advisory
-> bounded Orchestrator route decision
-> route validator / guard completeness validator
-> bounded Gemini Architect proposal role
-> local PlanGraph adapter / contract validator
-> Fractal executor
-> ResultProposal
-> Post V&V
-> GT/LGT
-> Root FinalOutput boundary
-> DRS writeback

## Role Boundary

Gemini Architect is not Root.
Gemini Architect is not Orchestrator.
Gemini Architect is not Executor.
Gemini Architect is not a tool, connector, payment, or shipment actor.
Gemini Architect does not create FinalOutput.
Gemini Architect does not execute actions.
Gemini Architect does not mutate DRS.
Gemini Architect may only propose a bounded PlanGraph-shaped candidate or ArchitectPlanProposal for local validation.

Architect may propose PlanGraph structure. Raw Gemini output must not become authoritative PlanGraph automatically. A local PlanGraph adapter / PlanGraph contract validator must validate or reject the proposal before downstream Fractal executor. PlanGraph remains not authority. Root remains final authority.

## Inspection Summary

- `docs/bounded_gemini_orchestrator_role_preflight_v01.md`: present. Donor for explicit role gate, bounded structured input, route validator / guard completeness validator reuse, no new runner, no patch plan, and no public WOW.
- `docs/audit_reports/auditor_bounded_gemini_orchestrator_role_runtime_v01.log`: present. Confirms the Orchestrator role is closed, implemented inside the existing Full E2E runner, with no Gemini Architect and no dual Gemini.
- `demo/run_full_semantic_e2e_v01.py`: present. Target runtime. Current deterministic Architect stage uses `hedgehog.architect.make_plan_graph`; current PlanGraph stage invokes `hedgehog.llm_architect.validate_plan_graph_contract`; Fractal executor runs only after validation.
- `tests/test_full_semantic_e2e_v01_runner.py`: present. Target tests. Existing fake-provider and real-provider monkeypatch patterns for the Gemini Orchestrator role should be reused for Architect role tests.
- `demo/run_live_gemini_ordered_orchestrator_architect_smoke.py`: present. Donor/reference only. It shows ordered role separation and `make_plan_graph_with_llm` / `validate_plan_graph_contract`, but it is not the supplier-payment Full E2E route.
- `demo/run_gemini_orchestrator_architect_pair_smoke.py`: present. Donor/reference only for Orchestrator+Architect pairing and guard validation patterns.
- `demo/run_live_dual_gemini_full_chain_smoke.py`: present. Donor/reference only for live Architect prompt/repair/schema ideas. Dual Gemini remains out of scope.
- `demo/run_live_gemini_orchestrator_smoke.py` and `demo/run_live_gemini_orchestrator_shadow.py`: present. Orchestrator donor files only; they do not satisfy the Architect role.
- `hedgehog/architect.py`: present. `make_plan_graph` is reusable for the deterministic default path and as the existing PlanGraph shape reference.
- `hedgehog/llm_architect.py`: present. `validate_plan_graph_contract` can be reused directly. `make_plan_graph_with_llm` is a useful donor/callable, but future runtime still needs a local Architect proposal adapter because this layer needs an explicit proposal envelope, counters, safe input boundary, and fail-closed behavior.
- `hedgehog/fractal_dag_executor.py`: present. `run_fractal_dag_executor` remains the downstream executor and must receive only locally validated PlanGraph artifacts.

## Future Gate

Future explicit env gate:
- `HEDGEHOG_FULL_E2E_GEMINI_ARCHITECT=1`

Default future behavior:
- no Gemini Architect call
- no model/network call
- deterministic Architect path remains unchanged
- default Full E2E remains PASS
- Gemini Architect counters remain zero

First Architect runtime slice:
- enable Gemini Architect only
- keep the current bounded/validated Orchestrator route decision
- do not require real Gemini Orchestrator in the same run
- do not start dual Gemini
- keep deterministic/local validation downstream
- keep Root as the only FinalOutput authority

No dual Gemini in this slice.
No public WOW yet.

## Allowed Gemini Architect Input

Future Gemini Architect input may include only bounded structured context:
- validated bounded route context
- `selected_vector_ids`
- `allowed_vector_ids`
- AttractorPacket / route packet summary
- CandidateVector summaries
- AVF/advisory summaries
- hard blocks: legal hold, water_filter shortage
- required PlanGraph contract constraints
- allowed executor ids / allowed executor modes if available

The input must hide:
- raw user text
- raw provider artifact contents
- unrestricted raw Gemini output
- secrets, API keys, tokens, passwords, credentials
- bank, supplier, or warehouse connector details
- connector, payment, or shipment command surfaces
- hidden reasoning
- Root internals that can be imitated as authority

## Future Proposal Shape

Future Gemini Architect output proposal should include at minimum:
- `proposal_id`
- `proposal_role: bounded_gemini_architect`
- `source_packet_id`
- `plan_graph_proposal_id`
- `selected_vector_ids`
- `nodes`
- `edges`
- `executor_assignments`
- `time_assumptions`
- `required_validators`
- `confidence`
- `reason`
- `needs_review`
- `uncertainty_notes`
- `authority_claimed`
- `truth_claimed`
- `action_permission_claimed`
- `final_output_claimed`
- `connector_command_claimed`
- `drs_write_claimed`
- `root_bypass_claimed`
- `orchestrator_bypass_claimed`
- `unvalidated_plan_graph_claimed`
- `root_review_required`

Required safe values:
- `proposal_role` is `bounded_gemini_architect`
- `selected_vector_ids` is a subset of `allowed_vector_ids`
- node vector ids are a subset of selected and allowed vector ids
- executor assignments use allowed executor ids / modes only
- `authority_claimed: false`
- `truth_claimed: false`
- `action_permission_claimed: false`
- `final_output_claimed: false`
- `connector_command_claimed: false`
- `drs_write_claimed: false`
- `root_bypass_claimed: false`
- `orchestrator_bypass_claimed: false`
- `unvalidated_plan_graph_claimed: false`
- `root_review_required: true`

## Local Validation Requirements

The future runtime must validate or reject the proposal before Fractal executor:
- selected vector ids must be a subset of allowed vector ids
- every PlanGraph node vector id must be within selected/allowed vector ids
- executor assignments must use allowed executor ids / modes only
- no connector, payment, or shipment commands
- no FinalOutput field or text
- no Root authority claim
- no DRS write claim
- no bypass of Orchestrator, AVF, Post V&V, GT/LGT, or Root
- `hedgehog.llm_architect.validate_plan_graph_contract` must run before Fractal executor
- existing local PlanGraph hardening must still block disallowed vectors, cycles, raw text, and child overreach
- invalid explicit Architect proposals must fail closed or be rejected before Fractal executor

## Required Future Counters

- `bounded_gemini_architect_role_started_count`
- `gemini_architect_model_call_count`
- `gemini_architect_network_used_count`
- `gemini_architect_proposal_created_count`
- `gemini_architect_proposal_validated_count`
- `gemini_architect_plan_graph_proposal_created_count`
- `gemini_architect_plan_graph_contract_validated_count`
- `gemini_architect_plan_graph_allowed_count`
- `gemini_architect_plan_graph_rejected_count`
- `gemini_architect_node_vector_subset_validated_count`
- `gemini_architect_raw_text_blocked_count`
- `gemini_architect_authority_claim_blocked_count`
- `gemini_architect_truth_claim_blocked_count`
- `gemini_architect_action_claim_blocked_count`
- `gemini_architect_final_output_claim_blocked_count`
- `gemini_architect_connector_claim_blocked_count`
- `gemini_architect_drs_write_claim_blocked_count`
- `gemini_architect_root_bypass_claim_blocked_count`
- `gemini_architect_orchestrator_bypass_claim_blocked_count`
- `gemini_architect_unvalidated_plan_graph_blocked_count`
- `gemini_architect_disallowed_executor_blocked_count`
- `gemini_architect_disallowed_vector_blocked_count`

Generic actor counter:
- `bounded_gemini_actor_role_started_count` remains 0 by default.
- In Architect-only explicit mode, `bounded_gemini_actor_role_started_count` should be 1 when the bounded Gemini Architect role starts.
- Fake Architect provider tests must not increment model/network/Gemini aggregate counters.
- Real Architect provider success must honestly increment role model/network counters and aggregate live model/network/Gemini counters.
- Dual-role aggregation is deferred to a later layer and must not be designed as part of this preflight.

## Preflight Answers

1. Existing donor schema/callable for Architect proposal:
   `hedgehog.llm_architect.validate_plan_graph_contract` is the direct reusable contract validator. `hedgehog.architect.make_plan_graph` is the deterministic PlanGraph generator and shape reference. Old live Architect smokes provide donor schema/prompt patterns only.

2. Old Orchestrator+Architect / dual Gemini smokes:
   They cannot be reused directly. They are donor/reference only because they do not run inside the current hardened supplier-payment Full E2E route and some include fallback or dual-role behavior that is out of scope.

3. Donor/reference only parts:
   Ordered role prompts, repair prompts, Gemini PlanGraph schema hints, pair smoke guard patterns, and dual-chain PlanGraph diagnostics are donor/reference only. They must be reintroduced only through the existing Full E2E route.

4. `make_plan_graph` reuse:
   `make_plan_graph` can be reused directly for the deterministic default path. Future Gemini Architect runtime needs a local Gemini proposal -> PlanGraph adapter because Gemini output must be an explicit bounded proposal envelope before it becomes a candidate PlanGraph for validation.

5. `validate_plan_graph_contract` reuse:
   `validate_plan_graph_contract` can be reused directly and should remain the hard local contract gate before Fractal executor.

6. Current Full E2E contexts to pass:
   Pass bounded route context, selected vector ids, allowed vector ids, AttractorPacket summary, CandidateVector summaries, AVF/advisory summaries, legal hold and water_filter shortage summaries, required validators, and allowed executor ids / modes.

7. Hidden inputs:
   Hide raw user text, raw provider artifact text, secrets, credentials, connector/payment/shipment command surfaces, hidden reasoning, DRS mutation surfaces, and Root authority internals.

8. Minimal future runtime patch:
   Extend `demo/run_full_semantic_e2e_v01.py` with the env gate, counters, safe input builder, fake provider injection path, real Gemini Architect provider path, proposal parser, local proposal validator, Gemini proposal -> PlanGraph adapter, `validate_plan_graph_contract` call, and fail-closed integration before Fractal executor. Extend `tests/test_full_semantic_e2e_v01_runner.py` with focused fake-provider and monkeypatch coverage.

9. Required focused fake-provider tests:
   Default counters zero; valid fake Architect proposal PASS; selected vector violation rejected; node vector violation rejected; disallowed executor rejected; missing validators rejected or downgraded before executor; authority/truth/action/final-output/connector/DRS/root-bypass/orchestrator-bypass claims blocked; raw text and sensitive markers absent from prompt; invalid graph/cycle/final_output field fails closed; no payment, shipment, or connector.

10. Required real Gemini smoke evidence:
   Explicit `HEDGEHOG_FULL_E2E_GEMINI_ARCHITECT=1`, real Gemini provider path, model name, role model/network counters, aggregate model/network/Gemini counters, proposal created, proposal validated, PlanGraph contract validated, no unsafe claims, Fractal executor reached only from validated PlanGraph, Root decision remains not_ready, payment/shipment/connector counters remain zero.

11. Separate patch plan:
   No separate patch plan is required if the runtime keeps changes inside the existing Full E2E runner and tests. The only contract gap is the proposal-envelope adapter, which can be local to the runner in the next runtime slice.

12. Exact next step:
   Bounded Gemini Architect Proposal Role v0.1 runtime directly inside the existing Full Semantic E2E runner and focused tests.

## Future Acceptance Criteria

- default Full E2E remains PASS with Architect role counters zero
- explicit fake Gemini Architect path can produce a valid bounded PlanGraph proposal
- proposal is locally validated before Fractal executor
- `selected_vector_ids` are a subset of `allowed_vector_ids`
- node vector ids are a subset of selected/allowed vector ids
- executor assignments use allowed executor ids / modes only
- `validate_plan_graph_contract` passes before Fractal executor
- invalid explicit Architect proposal fails closed or is rejected before Fractal executor
- Gemini Architect cannot override legal hold
- Gemini Architect cannot override water_filter shortage
- Gemini Architect cannot create FinalOutput
- Gemini Architect cannot execute payment or shipment release
- Gemini Architect cannot call connectors
- payment_executed_count remains 0
- shipment_released_count remains 0
- connector_called_count remains 0
- Root remains final authority

## Verdict

No blocking contract gap was found for a local runner-hosted runtime slice. The next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests.

No new runner.
No public WOW.
No dual Gemini.
No production execution.
No NeedleFactory.
No Marennya / UP.
