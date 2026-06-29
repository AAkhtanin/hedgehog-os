# Bounded Gemini Orchestrator Proposal Role v0.1 PREFLIGHT

- preflight_id: bounded_gemini_orchestrator_role_preflight_v01
- preflight_status: COMPLETE
- base_head: 4dbe89f
- planning_only: true
- runtime_created: false
- tests_created: false
- audit_log_created: false
- existing_full_e2e_runner_will_be_extended: true
- separate_runner_allowed: false
- separate_patch_plan_required: false
- commit_created: false

## Purpose

Plan the next runtime layer where Gemini may act as a bounded Orchestrator proposal role inside the existing Full Semantic E2E supplier-payment spine.

Current closed base:
- Full Semantic E2E runtime closed.
- E2E invoked boundary hardening closed.
- Full Semantic E2E live evidence mode closed.
- Gemini SDK/schema path fixed.
- Full Semantic E2E live evidence influence closed at 4dbe89f.
- Real Gemini can create a validated SemanticEvidenceClaim that influences supplier/DRS/CandidateVector/AVF contexts while remaining candidate-only.

This layer is not public WOW, not production, not NeedleFactory, and not Marennya / UP.

## Role Boundary

Gemini is not Root.
Gemini is not Architect.
Gemini is not Executor.
Gemini is not a FinalOutput creator.
Gemini is not a tool, connector, payment, shipment, or DRS writer.
The bounded Gemini Orchestrator proposal role does not create PlanGraph and does not create FinalOutput.

Canonical role placement:

User / dirty business request
-> live evidence reader / SemanticEvidenceClaim
-> DRS candidate context
-> CandidateVector
-> AVF/advisory
-> bounded Gemini Orchestrator proposal role
-> local route validator / guard completeness validator
-> deterministic Architect / PlanGraph in this first runtime slice
-> Fractal executor
-> ResultProposal
-> Post V&V
-> GT/LGT
-> Root FinalOutput boundary
-> DRS writeback

## Donor / Reference Inspection

- `demo/run_live_gemini_orchestrator_shadow.py`: present. It provides a shadow-only route proposal shape, hides expected route from the model, converts proposals into `RouteProposal`, and uses `validate_route_proposal`. It is donor/reference only because it does not run inside the current Full Semantic E2E supplier-payment route.
- `demo/run_live_gemini_orchestrator_smoke.py`: present. It contains bounded Orchestrator proposal prompt and validation ideas, including proposal-only flags and no Root/FinalOutput/DRS/action authority. It is donor/reference only.
- `demo/run_live_gemini_ordered_orchestrator_architect_smoke.py`: present. It contains `ORCHESTRATOR_PROPOSAL_JSON_SCHEMA` and ordered Orchestrator validation/repair patterns. It is donor/reference only because the first future runtime must not start Gemini Architect.
- `demo/run_gemini_orchestrator_architect_pair_smoke.py`: present. Pair smoke is donor/reference only for old Orchestrator/Architect role separation; it does not satisfy this layer.
- `demo/run_live_dual_gemini_full_chain_smoke.py`: present. It provides schema/fallback/repair references for live Orchestrator matrix and live Architect plan flows. It is donor/reference only; dual Gemini is explicitly out of scope.
- `demo/run_orchestrator_route_validator.py`: present. Direct callable: `RouteProposal` and `validate_route_proposal`. It can be reused directly for route allowance and guard-preserving validation after adapting the Gemini proposal artifact into `RouteProposal`.
- `demo/run_orchestrator_guard_completeness.py`: present. Direct callable: `GuardScenario` and `audit_guard_scenario`. It can be reused directly for guard completeness if the future runtime constructs a supplier-payment route scenario.
- `demo/run_full_semantic_e2e_v01.py`: present. It is the target runtime route. It already exposes `supplier_payment_context`, `drs_candidate_context`, `candidate_vector_context`, `avf_context`, `advisory_context`, allowed vector ids, deterministic Architect, PlanGraph validation, Fractal executor, Post V&V, GT/LGT, Root boundary, and local DRS writeback.
- `tests/test_full_semantic_e2e_v01_runner.py`: present. It is the target focused test surface.
- `demo/run_live_provider_adapter_response_capture_v01.py`: present. It provides the current `google-genai` response schema/fallback pattern and explicit provider-gated call shape.
- `tests/test_live_provider_adapter_response_capture_v01_runner.py`: present. It proves fake provider and schema fallback behavior without real network calls in tests.

Old live Gemini orchestrator/architect smokes are donor/reference only. They do not automatically satisfy the new layer unless their semantics are reintroduced inside the current Full Semantic E2E supplier-payment route.

## Future Runtime Shape

Preferred future runtime files:
- `demo/run_full_semantic_e2e_v01.py`
- `tests/test_full_semantic_e2e_v01_runner.py`

No new runner unless implementation discovers a hard blocker. Current inspection found no blocker.

Preferred future explicit env gate:
- `HEDGEHOG_FULL_E2E_GEMINI_ORCHESTRATOR=1`

Default mode:
- no Gemini Orchestrator role call
- no network/model call
- deterministic Full E2E PASS unchanged
- all Gemini Orchestrator counters zero

Future runtime should call real Gemini only when both:
- `HEDGEHOG_FULL_E2E_GEMINI_ORCHESTRATOR=1`
- provider/key/model config is present

The first runtime slice should use Gemini as Orchestrator only.
Architect remains deterministic/local in the first runtime slice.
Do not start dual Gemini Orchestrator+Architect yet.
Do not start Gemini Architect role yet.

## Allowed Gemini Input

Pass only bounded structured context:
- selected safe supplier facts from `supplier_payment_context`
- candidate-only live claim summary, without raw provider artifact text
- DRS candidate ids and review-only reason codes from `drs_candidate_context`
- CandidateVector ranked ids and allowed vector ids from `candidate_vector_context`
- AVF/advisory score summaries and hard blocks from `avf_context` / `advisory_context`
- legal hold and water_filter shortage blocker summaries
- required guard list and route validator expectations

Hide from Gemini input:
- raw secrets
- raw bank/supplier/warehouse credentials
- unrestricted raw provider output
- raw user text beyond bounded dirty request summary
- raw `.tmp` artifact contents
- hidden reasoning
- connector/payment/shipment credentials or commands
- Root boundary internals that could be imitated as authority

## Bounded Proposal Contract

Bounded Gemini Orchestrator may:
- receive bounded structured context only
- see selected safe summaries from supplier_payment_context, DRS, CandidateVector, AVF/advisory
- propose a route id
- propose required guards
- propose selected vector ids from allowed vector ids only
- provide confidence and reason
- mark uncertainty / needs review
- return a proposal artifact for local validation

Bounded Gemini Orchestrator must not:
- mutate DRS
- call connectors
- execute payment
- release shipment
- command Architect directly
- create PlanGraph
- create ResultProposal
- create FinalOutput
- claim Root authority
- claim truth
- claim action permission
- bypass AVF
- bypass Post V&V / GT / Root

## Validation Plan

Use the existing route validator by adapting Gemini output into `RouteProposal`:
- `suggested_route` should map to an allowed supplier-payment full-spine route, likely `proof_full_pipeline`.
- `confidence` remains advisory only.
- `required_guards` must include AVF, PlanGraph contract, Post V&V, GT/LGT, and Root final authority.
- authority/action/final-output/DRS-write/connector claims map to rejected or fail-closed outcomes.

Use guard completeness by constructing a `GuardScenario`:
- expected route: `proof_full_pipeline`
- proposed route: Gemini route id
- proposed guards: Gemini required guards
- missing critical guards cause rejection or downgrade.

Add local Full E2E checks for this new supplier-payment role:
- selected vector ids must be a subset of allowed vector ids
- raw provider/user text must be absent from Orchestrator input
- legal hold and stock shortage remain blockers
- Gemini proposal cannot override Root boundary

## Required Future Counters

- bounded_gemini_orchestrator_role_started_count
- gemini_orchestrator_model_call_count
- gemini_orchestrator_network_used_count
- gemini_orchestrator_proposal_created_count
- gemini_orchestrator_proposal_validated_count
- gemini_orchestrator_route_allowed_count
- gemini_orchestrator_route_rejected_count
- gemini_orchestrator_route_downgraded_count
- gemini_orchestrator_guard_completeness_validated_count
- gemini_orchestrator_selected_only_allowed_vectors_count
- gemini_orchestrator_raw_text_blocked_count
- gemini_orchestrator_authority_claim_blocked_count
- gemini_orchestrator_truth_claim_blocked_count
- gemini_orchestrator_action_claim_blocked_count
- gemini_orchestrator_final_output_claim_blocked_count
- gemini_orchestrator_connector_claim_blocked_count
- gemini_orchestrator_drs_write_claim_blocked_count
- gemini_orchestrator_plan_graph_claim_blocked_count
- gemini_orchestrator_bypassed_avf_blocked_count
- gemini_orchestrator_bypassed_root_blocked_count

## Future Acceptance Criteria

- default Full E2E remains PASS with role counters zero
- explicit fake Gemini Orchestrator path can produce a valid route proposal
- proposal is locally validated
- selected vector ids must be subset of allowed vector ids
- required guards must include AVF, PlanGraph contract, Post V&V, GT/LGT, Root final authority
- invalid authority/action/final-output/connector/DRS-write claims fail closed or are rejected
- raw provider/user text is blocked from Orchestrator input
- Gemini Orchestrator cannot override legal hold
- Gemini Orchestrator cannot override stock shortage
- payment_executed_count remains 0
- shipment_released_count remains 0
- connector_called_count remains 0
- Root remains final authority

## Preflight Answers

1. Existing donor callable/schema for Orchestrator proposal:
   - `RouteProposal` / `validate_route_proposal` can represent route proposal validation.
   - `ORCHESTRATOR_PROPOSAL_JSON_SCHEMA` from ordered smoke can guide future Gemini JSON output, but should be adapted to the supplier-payment context and selected vector ids.

2. Can `demo/run_orchestrator_route_validator.py` be reused directly?
   - Yes for route and guard validation through `validate_route_proposal`.
   - A thin local adapter is still needed in the existing Full Semantic E2E runner to translate the Gemini proposal artifact and enforce selected vector ids.

3. Can `demo/run_orchestrator_guard_completeness.py` be reused directly?
   - Yes for guard completeness through `GuardScenario` / `audit_guard_scenario`.
   - The future runtime should construct a supplier-payment `GuardScenario` instead of copying the old guard catalog.

4. Which current Full E2E contexts should be passed to Gemini?
   - Bounded supplier_payment_context summary, DRS candidate ids/reason codes, CandidateVector ranked ids/allowed vector ids, AVF/advisory summaries, legal hold status, stock shortage status, and required guard names.

5. What must be hidden from Gemini input?
   - Secrets, credentials, raw provider artifacts, unrestricted raw user/provider text, connector details, payment/shipment command surfaces, and Root final boundary internals.

6. Minimal future runtime patch:
   - Add `HEDGEHOG_FULL_E2E_GEMINI_ORCHESTRATOR`.
   - Add a local bounded prompt/schema helper inside `demo/run_full_semantic_e2e_v01.py`.
   - Use fake provider tests for proposal JSON.
   - Convert proposal to `RouteProposal`.
   - Run route validator and guard completeness validator.
   - Enforce selected vector ids subset locally.
   - Feed only validated route decision into the already deterministic Architect path.
   - Keep payment, shipment, connector, and Root authority boundaries unchanged.

7. Is a separate patch plan required?
   - No. No contract gap was found. The next approved implementation is runtime directly in the existing Full Semantic E2E runner and focused tests.
   - No public WOW yet.

## Preflight Verdict

No contract gap blocks Slice 1 runtime.
next approved implementation is runtime directly in the existing Full Semantic E2E runner and focused tests.
No separate patch plan.
No public WOW yet.
