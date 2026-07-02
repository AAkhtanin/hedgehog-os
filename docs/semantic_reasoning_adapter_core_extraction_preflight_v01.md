# Semantic Reasoning Adapter Core Extraction Preflight v0.1

document_id: semantic_reasoning_adapter_core_extraction_preflight_v01
document_status: PREFLIGHT
base_head: 377ecb0

## Scope

This is a docs-only preflight for semantic_reasoning_adapter core extraction.
It does not modify runtime, tests, `hedgehog`, `.tmp` evidence, README,
AGENTS, passport, or manifest files.

Current official checkpoint:

- Real Gemini Unknown Request 007 PASS.
- run_id: `manual-live-unknown-request-real-gemini-007`
- audit_id: `auditor_live_unknown_request_real_gemini_007_v01`
- docs sync commit: `f6bcd78`
- current cleanup head: `377ecb0`
- contract_mode: `semantic_reasoning_adapter`
- schema_mode: `json_mime_only`

Approved live-provider architecture formula:

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```

Current hedgehog core baseline:

- `hedgehog.context_packets`
- `hedgehog.structured_rationale`
- `hedgehog.action_commit_packet`
- `hedgehog.mock_connector_sandbox`
- `hedgehog.fractal_fulfillment`

## Source Locations Inspected

The preflight is based on the current source locations below:

- `demo/run_live_unknown_request_dual_rich_context_v01.py`
  - current home of `semantic_reasoning_adapter` runtime behavior.
  - contains semantic reasoning required-field constants.
  - contains `_semantic_reasoning_string_list`.
  - contains `_validate_semantic_reasoning_fields`.
  - contains `_semantic_reasoning_entries`.
  - contains `_semantic_reasoning_fields_present`.
  - contains `_safe_local_plan_nodes_from_semantic_reasoning`.
  - contains `_expand_orchestrator_semantic_reasoning_proposal`.
  - contains `_expand_architect_semantic_reasoning_proposal`.
  - also contains provider calls, env gates, timeout handling, prompts, CLI, and
    orchestration that must stay out of core.
- `tests/test_live_unknown_request_dual_rich_context_v01.py`
  - currently tests semantic reasoning prompts, adapter expansion, fail-closed
    reasoning validation, forbidden provider claims, local plan node safety,
    live-path defaults, and `json_mime_only` behavior.
- `hedgehog/structured_rationale.py`
  - owns canonical structured rationale constants, builders, and validators.
  - provides `build_orchestrator_structured_rationale`.
  - provides `build_architect_structured_rationale`.
  - provides `validate_orchestrator_structured_rationale`.
  - provides `validate_architect_structured_rationale`.
- `hedgehog/context_packets.py`
  - owns bounded ContextPacket builders and validators.
  - includes OrchestratorRouteContextPacket and ArchitectPlanContextPacket
    contracts.
- `docs/audit_reports/auditor_live_unknown_request_real_gemini_007_v01.log`
  - records the first successful real live unknown-request run.
  - records that providers returned semantic reasoning proposals.
  - records that runtime built structured rationales and safe local PlanGraph
    nodes.
- `README.md`
  - records the current hedgehog core baseline and the 007 live checkpoint.
- `AGENTS.md`
  - records operator-facing checkpoint rules and current next layers.
- `specs/human_passport_v0_25.md`
  - records the current architecture boundary and core baseline.
- `specs/machine_manifest_v0_25.json`
  - records `latest_live_provider_checkpoint:
    real_gemini_unknown_request_007`.
  - records `semantic_reasoning_adapter_status:
    approved_live_provider_architecture, pending_core_extraction`.

## Why This Extraction Exists

`semantic_reasoning_adapter` is approved live-provider architecture. It
currently lives in `demo/run_live_unknown_request_dual_rich_context_v01.py` and
is marked pending core extraction.

The goal is to move stable semantic provider contracts and canonicalization
helpers into hedgehog core. The target is a reusable, deterministic, local
contract layer that converts untrusted semantic provider fields into canonical
structured rationale artifacts and safe advisory plan nodes.

The goal is not to move Gemini, network, runtime, provider, or CLI behavior
into core.

## What Belongs In Core

Candidate future core module:

- `hedgehog.semantic_reasoning_adapter`

Candidate direct core tests:

- `tests/test_semantic_reasoning_adapter_core.py`

Stable contracts and functions to extract:

- semantic reasoning required field constants.
- Orchestrator semantic reasoning field constants.
- Architect semantic reasoning field constants.
- semantic reasoning string/list normalization.
- semantic reasoning field validation.
- `semantic_reasoning_missing_field:<field>`.
- `semantic_reasoning_empty_field:<field>`.
- `semantic_reasoning_invalid_type:<field>`.
- `semantic_reasoning_empty_item:<field>`.
- semantic reasoning entries conversion into canonical builder inputs.
- semantic reasoning fields present diagnostics.
- `expand_orchestrator_semantic_reasoning_proposal`.
- `expand_architect_semantic_reasoning_proposal`.
- safe local PlanGraph node builder for semantic reasoning mode.
- preservation of provider claim booleans for validation.
- runtime-generated authority boundary objects.
- Root remains final authority boundary.
- PlanGraph is not authority boundary.
- ResultProposal is not FinalOutput boundary.

The future core API should keep provider booleans visible and untrusted. It
must not overwrite truth, authority, action, connector, FinalOutput, or
root-bypass claims before validators can reject them.

## What Must Not Move Into Core

The following stay in the live unknown-request runner or surrounding runtime:

- `_call_live_gemini_provider`.
- `google.genai` SDK integration.
- provider API key lookup.
- timeout / HttpOptions plumbing.
- Architect pre-delay.
- `HEDGEHOG_UNKNOWN_REQUEST_LIVE_GEMINI` live gate behavior.
- CLI / `render_report`.
- `.tmp` evidence capture.
- run IDs 001-007.
- raw provider outputs/prompts.
- model names.
- committed audit logs.
- prepared domain fixtures.
- full demo runner orchestration.

Core extraction must not introduce provider/model/network imports.

## Policy Boundary

The core adapter must be policy-driven or context-driven where possible. It
must not hardcode the city archive artifact request. It must not hardcode hotel
robot rooms.

The current unknown-request route/vector names may remain integration policy in
the runner unless a later Slice A preflight or implementation argues that names
such as `unknown_request_root_review` and `unknown_request_semantic_review` are
generic enough for core constants.

Core should own semantic reasoning normalization and canonicalization mechanics,
not deployment policy, live-provider policy, or prepared fixture facts.

## Relationship To Existing Core

`hedgehog.structured_rationale` already owns canonical structured rationale
builders and validators. `semantic_reasoning_adapter` core should call those
builders and validators where needed; it must not duplicate canonical
structured rationale schema logic.

`hedgehog.context_packets` already owns bounded ContextPacket builders and
validators. `semantic_reasoning_adapter` core may preserve references to
ContextPacket authority boundaries, but it should not reimplement
ContextPacket validation.

The adapter core must not become Root. It must not become DRS. It must not
become AVF. It must remain a canonicalization helper between untrusted
semantic provider proposals and existing validators.

## Proposed Extraction Slices

### Slice A: Core-Only Semantic Reasoning Contracts

- Add `hedgehog/semantic_reasoning_adapter.py`.
- Add `tests/test_semantic_reasoning_adapter_core.py`.
- No runner integration.
- No Gemini.
- No network.
- Validate constants, reason-field validator, string/list normalization,
  empty-object rejection, adapter expansion into valid structured rationales,
  and safe local plan nodes.

### Slice B: Runner Delegation

- `demo/run_live_unknown_request_dual_rich_context_v01.py` imports core
  helpers.
- Compatibility wrappers remain if needed for existing tests.
- Output shape, counters, fail-closed reasons, env gates, live provider
  behavior, prompts, and 007 semantic behavior stay unchanged.
- All existing live unknown request tests still pass.

### Slice C: Replay Smoke After Delegation

- Injected/monkeypatched semantic reasoning path PASS.
- Real live 007-style replay is optional and gated, not automatic.
- No action counters.

### Slice D: Audit / Docs Sync

- Audit the core extraction.
- Docs say `semantic_reasoning_adapter` is now hedgehog core.
- Machine manifest updates `current_core_baseline_modules`.

## Future Slice A Test Expectations

Core tests must prove:

- valid Orchestrator semantic reasoning expands to valid
  `structured_orchestrator_rationale`.
- valid Architect semantic reasoning expands to valid
  `structured_architect_rationale`.
- empty string/list/object reasoning fails closed.
- missing reasoning fields fail closed.
- provider forbidden booleans are preserved and not overwritten.
- canonical structured rationale booleans remain safe false.
- safe local PlanGraph node output contains no `action_permission`,
  `connector_command`, `final_output`, `ActionCommitPacket`, or
  `real_world_effect`.
- Root remains final authority.
- no Gemini/provider/network imports.

Expected validation reasons include:

- `semantic_reasoning_missing_field:<field>`.
- `semantic_reasoning_empty_field:<field>`.
- `semantic_reasoning_invalid_type:<field>`.
- `semantic_reasoning_empty_item:<field>`.

## Safety And Authority Invariants

- Provider output is not truth.
- Provider output is not authority.
- ContextPacket is not truth.
- ContextPacket is not authority.
- structured rationale is explanation only.
- PlanGraph is not authority.
- ResultProposal is not FinalOutput.
- Gemini proposes, Root disposes.
- Root remains final authority.
- Gemini does not create ActionCommitPacket.
- Gemini does not create FinalOutput.
- DRS is not truth.
- AVF/route/vector selection is not authority.

## Relationship To Next Layers

This extraction is prerequisite for:

- BoundedSemanticEvidencePacket Orchestrator -> Architect.
- replay/stability proof.
- multi-domain live unknown proof.
- adversarial live proof.
- DRS v0.2.
- AVF v0.2.
- mock permission/action/connector sandbox before physical-world action
  domains.

## Non-Claims

- not production autonomy.
- not public WOW ready yet.
- no real connectors.
- no robot/hotel/door APIs.
- no payment/shipment/API calls.
- no ActionCommitPacket from Gemini.
- no FinalOutput from Gemini.
- no NeedleFactory/Marennya/UP.

## Preflight Conclusion

The semantic reasoning adapter has crossed from experimental live-runner
mechanic to approved live-provider architecture. The next safe engineering
step is a core-only extraction that moves stable semantic reasoning contracts
and canonicalization helpers into `hedgehog.semantic_reasoning_adapter`, while
leaving provider calls, live gates, prompts, timeouts, CLI, raw evidence capture,
and orchestration in the runner.

The extraction must preserve the 007 formula:

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```
