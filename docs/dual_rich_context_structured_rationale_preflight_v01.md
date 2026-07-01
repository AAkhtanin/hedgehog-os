# Dual Rich Context Structured Rationale Preflight v0.1

preflight_id: dual_rich_context_structured_rationale_preflight_v01
preflight_status: COMPLETE
base_head: 3d8a5f0
planning_only: true
runtime_created: false
tests_created: false
audit_log_created: false
new_capabilities_created: false
context_packets_modified: false
demo_runner_modified: false
gemini_provider_called: false
network_called: false
secrets_accessed: false
commit_created: false

## Purpose

Plan the next engineering layer after Rich Context / Bounded Context Packets Slice D:
Dual Rich Context Structured Rationale v0.1.

This preflight defines how both bounded Gemini roles may later return long but structured JSON rationale artifacts. It does not implement runtime, modify tests, modify `hedgehog/context_packets.py`, modify the Full Semantic E2E runner, call Gemini/provider/network/model APIs, access secrets, create capabilities, or create a new runner.

## 1. Current Baseline

Committed baseline:

- Slice A context packet core contracts committed at `3f780b4`.
- Slice B runner adapter committed at `9af295c`.
- Slice A+B audit committed at `44acb06`.
- Slice C OrchestratorRouteContextPacket input committed at `5b92725`.
- Slice C audit committed at `6b3db8b`.
- Slice D ArchitectPlanContextPacket input committed at `93eda30`.
- Slice D audit committed at `3d8a5f0`.

Current proven state:

- Orchestrator can consume validated OrchestratorRouteContextPacket under explicit gate.
- Architect can consume validated ArchitectPlanContextPacket under explicit gate.
- Dual injected-provider path can carry both packets.
- Root remains final authority.
- No raw cross-role text.
- No default output/counter/stage_map drift.
- No production/public WOW claim.
- No NeedleFactory/Marennya/UP.

## 2. Layer Definition

Dual Rich Context Structured Rationale is the planned layer where each bounded Gemini role may return a structured explanation artifact in addition to its already validated proposal artifact.

Structured rationale is JSON explanation, not hidden chain-of-thought. It is bounded, auditable, user-readable, and machine-validatable. The runtime should treat it as a rationale artifact with explicit fields, rejection reasons, and authority boundaries.

Structured rationale is not raw Gemini text. It is not raw chain-of-thought. It is not a transcript dump, prompt dump, cross-role dump, PlanGraph dump, or runner state dump.

## 3. Non-Authority Boundary

Structured rationale is:

- not truth
- not authority
- not action permission
- not FinalOutput
- not ActionCommitPacket
- not connector command
- not DRS write permission
- not raw Gemini text
- not raw chain-of-thought
- not production readiness
- not public WOW readiness

The rationale may explain why a role proposed a route or PlanGraph, but it must not become the route authority, execution authority, final-output authority, permission artifact, DRS writer, or connector command.

## 4. Proposed Orchestrator Rationale Shape

Future field:

`structured_orchestrator_rationale`

Required shape:

- `observed_semantics`
- `route_selection_reason`
- `rejected_routes`
- `required_guards_reasoning`
- `selected_vector_reasoning`
- `uncertainty_notes`
- `authority_boundary`
- `root_review_required`

Each field must be bounded and list/dict based. No raw_user_text. No raw_gemini_text. No raw_cross_role_text. No secrets. No connector commands.

Expected semantics:

- `observed_semantics` summarizes structured evidence and context-packet facts, not raw user text.
- `route_selection_reason` explains the selected route within allowed-route boundaries.
- `rejected_routes` lists route candidates rejected or not selected, with bounded reasons.
- `required_guards_reasoning` maps guards to explicit route safety expectations.
- `selected_vector_reasoning` explains selected vector ids without claiming truth.
- `uncertainty_notes` lists unresolved or review-required conditions.
- `authority_boundary` states Orchestrator is not Root.
- `root_review_required` remains true when Root review is required.

## 5. Proposed Architect Rationale Shape

Future field:

`structured_architect_rationale`

Required shape:

- `plan_shape_reason`
- `node_selection_reasoning`
- `executor_constraint_reasoning`
- `forbidden_surface_review`
- `validator_coverage_reasoning`
- `return_to_root_path`
- `uncertainty_notes`
- `authority_boundary`
- `root_review_required`

Each field must be bounded and list/dict based. No raw PlanGraph dump. No connector commands. No action permission. No final output claim.

Expected semantics:

- `plan_shape_reason` explains the proposed bounded PlanGraph shape without making PlanGraph authority.
- `node_selection_reasoning` maps node choices to allowed node kinds.
- `executor_constraint_reasoning` maps executor choices to allowed executor ids.
- `forbidden_surface_review` records connector/action/final-output surfaces that remain blocked.
- `validator_coverage_reasoning` maps PlanGraph contract, Post V&V, GT/LGT, and Root final authority checks.
- `return_to_root_path` confirms the proposal returns upward to Root.
- `uncertainty_notes` lists unresolved or review-required conditions.
- `authority_boundary` states Architect is not Root.
- `root_review_required` remains true when Root review is required.

## 6. Future Validators

Planned validators for later runtime:

- `validate_orchestrator_structured_rationale(...)`
- `validate_architect_structured_rationale(...)`

Required rejection reasons for later runtime:

- `structured_rationale_missing_required_field:<field>`
- `structured_rationale_must_be_mapping`
- `structured_rationale_raw_text_forbidden`
- `structured_rationale_truth_claim_forbidden`
- `structured_rationale_authority_claim_forbidden`
- `structured_rationale_action_permission_claim_forbidden`
- `structured_rationale_final_output_claim_forbidden`
- `structured_rationale_connector_command_forbidden`
- `structured_rationale_drs_write_forbidden`
- `structured_rationale_action_commit_packet_forbidden`
- `structured_rationale_root_bypass_forbidden`
- `structured_rationale_unbounded_dump_forbidden`
- `structured_rationale_secret_marker_forbidden:<marker>`

Validator expectations:

- Reject non-mapping rationale artifacts.
- Reject missing required fields.
- Reject explicit truth, authority, action permission, final output, ActionCommitPacket, connector command, DRS write, or Root bypass claims.
- Reject raw text dumps, raw Gemini outputs, raw cross-role text, raw PlanGraph dumps, full runner state dumps, and secret markers.
- Preserve long rationale only when it is structured, bounded, and field-level auditable.

## 7. Future Slices

Slice E:

- Add deterministic core validators/builders for structured rationale artifacts.
- No Gemini integration yet.

Slice F:

- Gemini Orchestrator proposal may include `structured_orchestrator_rationale`.
- Validate before accepting route proposal.

Slice G:

- Gemini Architect proposal may include `structured_architect_rationale`.
- Validate before accepting plan graph proposal.

Slice H:

- Dual rich-context smoke with both packets and both structured rationales.
- Injected providers first.
- Live Gemini only under explicit real-provider gates later.

## 8. Safety Invariants

- Gemini proposes, Root disposes.
- Orchestrator is not Root.
- Architect is not Root.
- PlanGraph is not authority.
- ResultProposal is not FinalOutput.
- Post V&V does not finalize.
- GT/LGT does not finalize.
- Root remains final authority.
- No real connector.
- No payment/shipment/action execution.
- No production/public WOW claim.

## 9. Recommended Next Step

The next implementation step is Slice E: deterministic core validators/builders for structured rationale artifacts. Slice E should remain core-only and should not call Gemini, change runner behavior, or alter existing packet gates.

Ready condition for Slice F and Slice G:

- Slice E validators reject authority/action/final-output/connector/DRS/Root bypass claims.
- Structured rationale artifacts remain JSON explanation, not hidden chain-of-thought.
- Structured rationale artifacts remain bounded, auditable, user-readable, and machine-validatable.
