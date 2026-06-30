# Core Extraction Checkpoint v0.1

checkpoint_id: core_extraction_action_mock_fractal_checkpoint_v01
checkpoint_status: CLOSED
based_on_audit: auditor_core_extraction_action_mock_fractal_v01
based_on_head: d433fa0
production_ready: false
public_wow_ready: false

Closed commits:
- c62ab84 Extract ActionCommitPacket core contract
- be4f40d Extract Mock Connector Sandbox core contract
- e26c05a Extract Fractal Fulfillment topology core contract
- 4723830 Harden Mock Connector Sandbox adapter registry

Checkpoint summary:

- no new runner
- no semantic drift observed in tested paths
- default CLI PASS
- regression suite 272 passed, 2 warnings
- deterministic extracted-core smoke PASS
- dual Gemini extracted-core smoke PASS

## What was validated

The checkpoint validates that the Full Semantic E2E runner can delegate stable contracts to:

- `hedgehog.action_commit_packet`
- `hedgehog.mock_connector_sandbox`
- `hedgehog.fractal_fulfillment`

Validated paths include:

- ActionCommitPacket builder and validator behavior
- Root-created mock-only ActionCommitPacket path
- Gemini cannot create ActionCommitPacket
- MockConnectorSandbox fake receipt and ExecutionEvidence validation
- deterministic expiry validation
- adapter registry fail-closed behavior for missing/non-callable adapters
- FractalFulfillmentTopology child O/A/I topology
- branch ResultProposal validation
- parent merge validation
- deterministic extracted-core Fractal Fulfillment smoke
- dual Gemini extracted-core Fractal Fulfillment smoke

## What was not validated

This checkpoint does not validate:

- production deployment
- public presentation wrapper completion
- real connector integration
- real payment movement
- real shipment release
- real bank, supplier, or warehouse API use
- unbounded Gemini context
- richer PlanGraph context
- NeedleFactory
- Marennya / UP activation
- global or external DRS

## Why this is not production

It is not production because the runtime remains a deterministic/local proof spine with bounded live-Gemini optional composition. The extracted core contracts still operate through the Full Semantic E2E integration harness, use local fake adapters, and preserve zero real/external action counters.

Key evidence:

- connector_called_count remains 0
- connector_called_count remains zero
- payment_executed_count remains 0
- shipment_released_count remains 0
- real_bank_api_called_count remains 0
- action_permission_created_count remains 0

## Why this is not public WOW ready yet

It is not public WOW ready yet because the core contracts are now extracted, but the public-facing wrapper and explanation layer still need a dedicated pass. The current proof is technically complete for the checkpoint, but it is still an integration/audit route rather than a polished public demonstration surface.

## Why docs sync was required

Docs sync was required because the source of truth moved:

- ActionCommitPacket mechanics moved from the runner to `hedgehog.action_commit_packet`.
- MockConnectorSandbox mechanics moved from the runner to `hedgehog.mock_connector_sandbox`.
- FractalFulfillmentTopology mechanics moved from the runner to `hedgehog.fractal_fulfillment`.

Without this sync, older docs would imply that the runner still owns all mechanics directly. The runner now remains the integration harness, while the stable contracts live in core modules.

## Behavior preservation

The audit records no output/counter/stage_map/fail-closed drift observed in tested paths.

Direct core tests now cover:

- `tests/test_action_commit_packet_core.py`
- `tests/test_mock_connector_sandbox_core.py`
- `tests/test_fractal_fulfillment_core.py`

Full runner regression remains covered by:

- `tests/test_full_semantic_e2e_v01_runner.py`

## Current authority boundary

Root remains final authority.

- Gemini proposes, Root disposes.
- Gemini does not create ActionCommitPacket.
- ActionCommitPacket is created by root_mock_approval_gate.
- MockConnectorSandbox is the only fake-adapter execution layer.
- FractalFulfillmentTopology does not call fake adapters directly.
- Child branch is not Root.
- ExecutionEvidence is not FinalOutput.

## Next recommended engineering direction

Recommended next direction:

- Rich Context / Bounded Context Packets preflight
- or Public WOW wrapper preflight

Explicitly not next:

- NeedleFactory
- Marennya / UP
- production connector integration
- real payment or shipment behavior
- public WOW ready claim

The context layer should pass bounded context packets through validated core contracts, not raw dumps from the integration runner.
