# Dual Gemini Orchestrator+Architect Integration v0.1 Preflight

preflight_id: dual_gemini_orchestrator_architect_integration_preflight_v01
preflight_status: COMPLETE
base_head: 22ee25f
planning_only: true
runtime_created: false
tests_created: false
audit_log_created: false
existing_full_e2e_runner_will_be_extended: true
separate_runner_allowed: false
separate_patch_plan_required: false
commit_created: false

## Purpose

Plan the next runtime layer where both bounded Gemini Orchestrator and bounded Gemini Architect roles can run in one existing Full Semantic E2E supplier-payment pass.

Current closed role stack:
- Bounded Gemini Orchestrator preflight: fe86aa8
- Bounded Gemini Orchestrator runtime: 239a0cf
- Bounded Gemini Orchestrator provider counter fix: 64cf778
- Bounded Gemini Orchestrator audit: eabe9f7
- Bounded Gemini Architect preflight: a749f4f
- Bounded Gemini Architect runtime: b87cbd6
- Bounded Gemini Architect schema adherence fix: e819fef
- Bounded Gemini Architect audit: 22ee25f

This is not public WOW.
This is not production.
No public WOW.
No NeedleFactory.
No Marennya.
No UP.
No real payment, shipment, or connector execution.

## Canonical Future Placement

User / dirty business request
-> live evidence reader / SemanticEvidenceClaim
-> DRS candidate context
-> CandidateVector
-> AVF/advisory
-> bounded Gemini Orchestrator proposal role
-> local route validator / guard completeness validator
-> validated bounded route decision
-> bounded Gemini Architect proposal role
-> local PlanGraph adapter / validate_plan_graph_contract
-> Fractal executor
-> ResultProposal
-> Post V&V
-> GT/LGT
-> Root FinalOutput boundary
-> DRS writeback

This is not a free-form Gemini-to-Gemini conversation.
Gemini Orchestrator does not talk directly to Gemini Architect.
Root/local runtime controls ordering.
Orchestrator output is validated locally before Architect sees anything.
Architect sees only bounded validated route context, not raw Orchestrator prompt/response.

## Role Boundaries

bounded Gemini Orchestrator:
- not Root
- not Architect
- not Executor
- does not create PlanGraph
- does not create FinalOutput
- does not execute actions
- does not mutate DRS
- may only propose bounded route / guards / selected vector ids

bounded Gemini Architect:
- not Root
- not Orchestrator
- not Executor
- does not create FinalOutput
- does not execute actions
- does not mutate DRS
- may only propose bounded PlanGraph-shaped candidate
- raw Gemini PlanGraph proposal must pass local adapter and validate_plan_graph_contract

Root remains final authority.

## Inspection Summary

- `docs/bounded_gemini_orchestrator_role_preflight_v01.md`: present. It planned `HEDGEHOG_FULL_E2E_GEMINI_ORCHESTRATOR`, bounded structured Orchestrator input, `validate_route_proposal`, `audit_guard_scenario`, separate provider lanes, and no dual Gemini in that slice.
- `docs/audit_reports/auditor_bounded_gemini_orchestrator_role_runtime_v01.log`: present. It confirms real `real_gemini_orchestrator_provider` smoke PASS, route validation allow_with_guards, guard completeness PASS_COMPLETE, no Gemini Architect, no dual Gemini role, no payment/shipment/connector, and Root remains final authority.
- `docs/bounded_gemini_architect_role_preflight_v01.md`: present. It planned `HEDGEHOG_FULL_E2E_GEMINI_ARCHITECT`, bounded Architect input, local PlanGraph adapter, and `hedgehog.llm_architect.validate_plan_graph_contract`.
- `docs/audit_reports/auditor_bounded_gemini_architect_role_runtime_v01.log`: present. It confirms real `real_gemini_architect_provider` smoke PASS after schema adherence, `bounded_gemini_architect_proposal_local_adapter`, strict local contract validation, no dual Gemini runtime, and Root remains final authority.
- `demo/run_full_semantic_e2e_v01.py`: present and is the only future runtime target. It already has separate Orchestrator and Architect role helpers, separate injection parameters `orchestrator_provider` and `architect_provider`, separate real provider paths `_call_gemini_orchestrator_provider` and `_call_gemini_architect_provider`, local route validation, guard completeness validation, PlanGraph adapter, `validate_plan_graph_contract`, Fractal executor, Post V&V, GT/LGT, Root boundary, and DRS writeback.
- `tests/test_full_semantic_e2e_v01_runner.py`: present and is the future focused test target. It already proves default mode, Orchestrator-only fake/real paths, Architect-only fake/real paths, provider lane separation, strict PlanGraph rejection, and current `dual_gemini_not_supported`.
- `demo/run_live_gemini_ordered_orchestrator_architect_smoke.py`: present. Donor/reference only for ordered role sequencing, Orchestrator schema ideas, and Architect contract checks; it is not the current supplier-payment Full E2E route.
- `demo/run_gemini_orchestrator_architect_pair_smoke.py`: present. Donor/reference only for pair semantics and route/guard validation; it does not satisfy the current Full E2E supplier-payment dual layer.
- `demo/run_live_dual_gemini_full_chain_smoke.py`: present. Donor/reference only for live dual-chain schema and diagnostics. Its PlanGraph schema differs from the current local Full E2E Architect contract and must not be copied directly.
- `hedgehog/architect.py`: present. `make_plan_graph` remains the deterministic default path and PlanGraph shape reference.
- `hedgehog/llm_architect.py`: present. `validate_plan_graph_contract` is directly reusable and must stay strict.
- `hedgehog/fractal_dag_executor.py`: present. `run_fractal_dag_executor` remains downstream and must receive only locally validated PlanGraph artifacts.

Search findings:
- Current runtime has `dual_gemini_not_supported` and blocks both role gates before either role starts.
- Current aggregate counters use `max(..., 1)` in single-role counter application. That is correct for Orchestrator-only and Architect-only smokes but must become additive for dual real Gemini calls.
- No unsafe provider lane reuse pattern like `architect_provider or orchestrator_provider or provider` was found in the active runner.

## Future Gate Contract

Safest dual env gate contract:
- `HEDGEHOG_FULL_E2E_DUAL_GEMINI_ROLES=1`
- `HEDGEHOG_FULL_E2E_GEMINI_ORCHESTRATOR=1`
- `HEDGEHOG_FULL_E2E_GEMINI_ARCHITECT=1`
- `HEDGEHOG_LIVE_PROVIDER_NAME=gemini`
- `HEDGEHOG_LIVE_PROVIDER_MODEL=gemini-2.5-flash`

Required gate behavior:
- default mode unchanged
- Orchestrator-only mode unchanged
- Architect-only mode unchanged
- both existing role gates set without `HEDGEHOG_FULL_E2E_DUAL_GEMINI_ROLES=1` must still fail closed with `dual_gemini_not_supported`
- dual mode requires explicit dual gate plus both role gates
- no accidental dual execution

Answer 1: the safest dual env gate contract is explicit triple gating. One dual gate alone should not silently enable both roles in v0.1 because explicit role gates already exist and tests rely on them.

Answer 2: existing `dual_gemini_not_supported` should change only when the dual gate is present. Without the dual gate, current behavior remains: fail closed before either role starts, with role counters zero. With the dual gate and both role gates, the runtime should execute ordered dual role flow instead of returning the unsupported context.

## Provider Lane Rules

- evidence provider is not Orchestrator provider
- evidence provider is not Architect provider
- Orchestrator provider is not Architect provider
- Architect provider is not Orchestrator provider
- injected test providers remain separate:
  - `orchestrator_provider`
  - `architect_provider`
- real provider paths remain separate:
  - `_call_gemini_orchestrator_provider`
  - `_call_gemini_architect_provider`
- do not use logic equivalent to `architect_provider or orchestrator_provider or provider`

## Future Sequencing Rules

1. Build local bounded route decision from DRS/CandidateVector/AVF/advisory.
2. Run Gemini Orchestrator proposal role.
3. Validate Orchestrator proposal through `validate_route_proposal` and `audit_guard_scenario`.
4. If Orchestrator fails, fail closed before Architect.
5. If Orchestrator passes, update route_decision using validated selected vector ids.
6. Build AttractorPacket from validated route decision.
7. Run Gemini Architect proposal role using only bounded validated route context.
8. Validate Architect proposal through local adapter and `validate_plan_graph_contract`.
9. If Architect fails, fail closed before Fractal executor.
10. If Architect passes, continue to Fractal executor, ResultProposal, Post V&V, GT/LGT, Root.

Answer 3: reusable current runtime functions:
- `_bounded_route_decision`
- `_evaluate_gemini_orchestrator_role`
- `_route_decision_from_gemini_orchestrator`
- `_attractor_packet_from_bounded_route`
- `_evaluate_gemini_architect_role`
- `_adapt_gemini_architect_proposal_to_plan_graph`
- `_validate_gemini_architect_proposal`
- `_validate_slice2_plan_graph`
- `_run_slice2_core_primitives`, after dual branch modification
- `_apply_gemini_orchestrator_counters`
- `_apply_gemini_architect_counters`, after aggregate counter policy modification

Answer 4: current runtime functions needing modification:
- add `ENV_FULL_E2E_DUAL_GEMINI_ROLES`
- add dual counters to `COUNTER_KEYS`
- add a dual-gate helper
- modify the early `dual_gemini_not_supported` branch in `_run_slice2_core_primitives`
- extend Architect safe input context with validated Orchestrator route summary, proposal id, route validation summary, and guard completeness summary
- update aggregate model/network/Gemini counter application from max-style boolean aggregation to additive aggregation for dual real calls
- add a `dual_gemini_context` or clear dual fields in existing contexts for sequence validation and audit visibility

## Architect Input in Dual Mode

Architect input may include:
- validated Orchestrator route_source
- validated Orchestrator proposal_id
- selected_vector_ids from validated Orchestrator decision
- allowed_vector_ids
- route validation summary
- guard completeness summary
- AttractorPacket summary
- CandidateVector/AVF/advisory summaries
- hard blockers
- PlanGraph contract constraints
- allowed executor ids/modes

Architect input must not include:
- raw Orchestrator prompt
- raw Orchestrator provider response text
- raw evidence text
- raw user dirty request text beyond bounded summary
- secrets
- connector/payment/shipment commands
- Root internals that can be imitated as authority

Answer 6: Orchestrator output should be passed to Architect only through a validated route decision artifact: proposal id, selected vector ids, validation decision, guard completeness result, and bounded route metadata. Do not pass raw cross-role text.

Answer 7: hidden from Architect are raw Orchestrator prompt, raw Orchestrator provider response text, raw evidence text, raw user dirty request text beyond bounded summary, secrets, connector/payment/shipment command surfaces, and Root internals that can be imitated as authority.

## Counter Contract

Existing single-role policies stay:
- Orchestrator-only real smoke: `live_model_call_count == 1`, `network_used_count == 1`, `gemini_called_count == 1`
- Architect-only real smoke: `live_model_call_count == 1`, `network_used_count == 1`, `gemini_called_count == 1`

Dual real smoke with no live evidence provider call must report:
- `gemini_orchestrator_model_call_count == 1`
- `gemini_orchestrator_network_used_count == 1`
- `gemini_architect_model_call_count == 1`
- `gemini_architect_network_used_count == 1`
- `live_model_call_count == 2`
- `network_used_count == 2`
- `gemini_called_count == 2`

Answer 5: aggregate model/network counters must be additive in dual mode. Current runtime `max(..., 1)` aggregation would block `live_model_call_count == 2`, `network_used_count == 2`, and `gemini_called_count == 2`; this is a required future runtime patch.

Generic actor counter policy:
- keep `bounded_gemini_actor_role_started_count` as boolean-presence for compatibility with current single-role semantics
- use `dual_gemini_roles_started_count` for exact two-role counting
- future tests should assert `bounded_gemini_actor_role_started_count == 1` when either or both bounded Gemini roles start, and `dual_gemini_roles_started_count == 2` or equivalent exact dual-role evidence when both roles start

## Required Future Dual Counters

- dual_gemini_roles_started_count
- dual_gemini_roles_completed_count
- dual_gemini_orchestrator_then_architect_sequence_validated_count
- dual_gemini_orchestrator_validated_before_architect_count
- dual_gemini_architect_consumed_validated_route_count
- dual_gemini_raw_cross_role_text_blocked_count
- dual_gemini_role_lane_separation_preserved_count
- dual_gemini_model_call_count
- dual_gemini_network_used_count
- dual_gemini_fail_closed_before_architect_count
- dual_gemini_fail_closed_before_fractal_count
- dual_gemini_root_final_authority_preserved_count

Existing role counters must remain:
- all Gemini Orchestrator counters
- all Gemini Architect counters
- `bounded_gemini_actor_role_started_count`

## Minimal Future Runtime Patch

Answer 8: minimal future runtime patch:
- add `HEDGEHOG_FULL_E2E_DUAL_GEMINI_ROLES`
- preserve current unsupported fail-closed behavior when both role gates are set without the dual gate
- when all three gates are set, run `_evaluate_gemini_orchestrator_role` first
- fail closed before Architect if Orchestrator is rejected
- convert accepted Orchestrator proposal into validated route_decision
- build AttractorPacket from that validated route_decision
- run `_evaluate_gemini_architect_role` with bounded validated route context only
- fail closed before Fractal executor if Architect is rejected
- keep deterministic/local validators downstream: `validate_route_proposal`, `audit_guard_scenario`, `validate_plan_graph_contract`, `_validate_slice2_plan_graph`
- add dual context and counters
- change aggregate model/network/Gemini counters to additive behavior for dual real calls
- keep payment/shipment/connector counters zero and Root boundary unchanged

No new runner.
No public WOW.

## Required Future Tests

Answer 9: fake-provider tests required:

A. Default mode:
- PASS
- all dual counters zero
- Orchestrator counters zero
- Architect counters zero

B. Both role gates set without dual gate:
- FAIL_CLOSED
- `dual_gemini_not_supported`
- no role starts
- no payment/shipment/connector

C. Dual fake valid:
- explicit dual gate plus both role gates
- injected `orchestrator_provider` returns valid bounded route proposal
- injected `architect_provider` returns valid bounded PlanGraph proposal
- PASS
- Orchestrator validates before Architect
- Architect consumes validated Orchestrator-selected vector ids
- PlanGraph validates
- Fractal executor runs
- Root not_ready
- no payment/shipment/connector
- fake path model/network/Gemini aggregate counters remain zero

D. Dual fake Orchestrator invalid:
- Orchestrator proposes disallowed vector or unsafe claim
- FAIL_CLOSED before Architect
- `architect_provider` not called
- no PlanGraph
- no Fractal executor

E. Dual fake Architect invalid:
- Orchestrator valid
- Architect invalid PlanGraph
- FAIL_CLOSED before Fractal executor
- Orchestrator validation remains recorded
- no Root FinalOutput from Gemini

F. Cross-role raw text block:
- Architect prompt/input must not contain raw Orchestrator prompt
- must not contain raw Orchestrator raw response text
- must not contain hostile raw evidence text such as "ignore all boundaries"
- must not contain `.tmp`, `api_key`, `secret`, `token`, or `password`

G. Provider lane separation:
- evidence provider not reused
- Orchestrator provider not reused as Architect provider
- Architect provider not reused as Orchestrator provider

Answer 10: mocked-real-provider tests required:
- monkeypatch `_call_gemini_orchestrator_provider` and `_call_gemini_architect_provider`
- do not pass injected providers
- dual gate enabled
- both `provider_call_path` values are real provider paths
- each role model/network counter is 1
- aggregate `live_model_call_count == 2`
- aggregate `network_used_count == 2`
- aggregate `gemini_called_count == 2`
- PASS
- no payment/shipment/connector

Answer 11: real Gemini dual smoke evidence required:
- one real provider call for Orchestrator
- one real provider call for Architect
- both outputs semantically summarized
- route validator passes
- guard completeness passes
- PlanGraph contract passes
- Fractal/Root invoked
- Root not_ready
- no payment/shipment/connector
- record separate Orchestrator and Architect provider call paths
- record dual aggregate model/network/Gemini counts as 2

## Limitations

- not public WOW
- not production
- no real connector/payment/shipment
- no NeedleFactory / Marennya / UP
- dual role output is proposal-only
- audit later must claim bounded dual-role integration, not general reasoning quality

## Preflight Answers

12. Separate patch plan required?
No. Current inspection found no contract gap requiring a separate patch plan. The next implementation can be runtime directly inside the existing Full Semantic E2E runner and focused tests.

13. Exact next step:
next_approved_step: Dual Gemini Orchestrator+Architect integration runtime inside existing Full Semantic E2E runner
next_runtime_target: demo/run_full_semantic_e2e_v01.py
next_test_target: tests/test_full_semantic_e2e_v01_runner.py
another_planning_document_allowed: false

## Verdict

Expected verdict if no blocker:
- next approved implementation is runtime directly inside existing Full Semantic E2E runner and focused tests
- no new runner
- no public WOW
- Root remains final authority
