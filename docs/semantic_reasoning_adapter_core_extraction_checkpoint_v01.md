# Semantic Reasoning Adapter Core Extraction Checkpoint v0.1

document_id: semantic_reasoning_adapter_core_extraction_checkpoint_v01
document_status: CLOSED

## Source Commits

- `cdd5316` preflight: Add semantic reasoning adapter core extraction preflight
- `04d55d8` Slice A core: Extract semantic reasoning adapter core contracts
- `12f7e96` Slice B runner delegation: Delegate live semantic reasoning adapter to core
- `092042f` Slice C audit: Add semantic reasoning adapter delegation audit log

Source audit:

- `auditor_semantic_reasoning_adapter_delegation_slice_c_v01`

Smoke:

- smoke_id: `manual-semantic-reasoning-adapter-delegation-slice-c-001`
- final_status: PASS
- no_real_gemini_or_network: true

Changed core files:

- `hedgehog/semantic_reasoning_adapter.py`
- `tests/test_semantic_reasoning_adapter_core.py`

Changed runner delegation files:

- `demo/run_live_unknown_request_dual_rich_context_v01.py`
- `tests/test_live_unknown_request_dual_rich_context_v01.py`

## What Moved To Core

`hedgehog.semantic_reasoning_adapter` now owns stable semantic reasoning
adapter mechanics:

- semantic reasoning provider contract constants.
- Orchestrator and Architect required semantic reasoning fields.
- semantic reasoning string/list normalization.
- semantic reasoning field validation and diagnostics.
- `semantic_reasoning_missing_field:<field>`.
- `semantic_reasoning_empty_field:<field>`.
- `semantic_reasoning_invalid_type:<field>`.
- `semantic_reasoning_empty_item:<field>`.
- conversion from provider semantic reasoning into canonical builder inputs.
- expansion of Orchestrator semantic proposals into
  `structured_orchestrator_rationale`.
- expansion of Architect semantic proposals into
  `structured_architect_rationale`.
- safe local advisory PlanGraph node builders.
- preservation of provider claim booleans for downstream validators.
- direct fail-fast rejection for provider-supplied `plan_nodes` in semantic
  reasoning mode.

`hedgehog.semantic_reasoning_adapter` contains no Gemini/provider/network/
runtime imports.

## What Stayed In The Runner

`demo/run_live_unknown_request_dual_rich_context_v01.py` remains the live
unknown-request provider spine. It still owns:

- Gemini/provider adapter calls.
- provider API key lookup through existing adapter conventions.
- env gates.
- prompt construction and prompt policy.
- timeout and explicit HTTP timeout plumbing.
- Architect pre-delay controls.
- live provider contract-mode selection.
- `json_mime_only` / response-schema selection.
- CLI and report rendering.
- orchestration across Orchestrator, context packets, rationale validation,
  Architect, PlanGraph, ResultProposal, and Root boundary.
- 007 integration policy and runner-specific compatibility shape.

Provider/network/Gemini behavior did not move to core because core must remain a
deterministic local contract and canonicalization layer.

## Architecture Formula

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```

Provider output is semantic reasoning proposal, not truth and not authority.
`hedgehog.semantic_reasoning_adapter` canonicalizes. `hedgehog.structured_rationale`
validates canonical rationale. `hedgehog.context_packets` validates bounded
packets. The runner orchestrates live provider calls and env gates. Root remains
final authority.

## 007 Compatibility

Slice C replay smoke preserved the 007-compatible local PlanGraph shape:

- `node:unknown_request_semantic_review`
- `node:root_review_gate`
- executor_id: `local_unknown_request_review_executor`
- root gate has `Root remains final authority` true.
- forbidden_surface_absent: true
- no `action_permission`
- no `connector_command`
- no `final_output`
- no `ActionCommitPacket`
- no `real_world_effect`

Compact and full compatibility paths also remain preserved:

- `compact_rationale_adapter`
- `full_structured_rationale`

Provider-supplied `plan_nodes` remain forbidden after delegation:

- provider_plan_nodes_final_status: FAIL_CLOSED
- `architect_provider_plan_nodes_forbidden_in_semantic_mode`
- plan_graph_context_empty: true
- result_proposal_empty: true
- root_boundary_empty: true

## Counters And Validated Artifacts

Action counters remained zero:

- action_permission_created_count: 0
- action_commit_packet_created_count: 0
- connector_called_count: 0
- real_world_effects_count: 0

Validated artifacts remain:

- OrchestratorRouteContextPacket accepted.
- ArchitectPlanContextPacket accepted.
- structured_orchestrator_rationale accepted.
- structured_architect_rationale accepted.
- PlanGraph is not authority.
- ResultProposal is not FinalOutput.
- Root remains final authority.

## Current Core Baseline

Current hedgehog core baseline is six modules:

- `hedgehog.context_packets`
- `hedgehog.structured_rationale`
- `hedgehog.semantic_reasoning_adapter`
- `hedgehog.action_commit_packet`
- `hedgehog.mock_connector_sandbox`
- `hedgehog.fractal_fulfillment`

## Authority Boundaries

- Provider output is not truth.
- Provider output is not authority.
- ContextPacket is not truth.
- ContextPacket is not authority.
- structured rationale is explanation only.
- PlanGraph is not authority.
- ResultProposal is not FinalOutput.
- DRS is not truth.
- AVF/route/vector selection is not authority.
- Gemini proposes, Root disposes.
- Gemini does not create ActionCommitPacket.
- Gemini does not create FinalOutput.
- Root remains final authority.

## Non-Claims

- not production autonomy.
- not public launch-ready.
- no real connector called.
- no real physical-world action.
- no robot, hotel, or door API call.
- no payment, shipment, or external API call.
- no ActionCommitPacket from Gemini.
- no FinalOutput from Gemini.

## Next Step Completion

The next engineering layer identified by this checkpoint has now progressed:
BoundedSemanticEvidencePacket lives in `hedgehog.context_packets` as a bounded
ContextPacket family and reached real Gemini Slice D 004 PASS.

Current next major gate: Supplier Payment / Shipment Release LIVE DUAL-ROLE
WOW v1 preflight. The completed BSEP layer remains bounded evidence transfer,
not raw text dump, unbounded Gemini context dump, or production action.
