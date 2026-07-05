# Full WOW v1.1 Manual Live Gemini Lane Preflight v0.1

document_id: full_wow_v1_1_manual_live_gemini_lane_preflight_v01
document_status: PREFLIGHT
base_head: f119d7c
target_direction: Full WOW v1.1 Manual Live Gemini Lane
previous_checkpoint: Full Semantic E2E Live Evidence + WOW v1.1 coherence PASS
planning_only: true
runtime_modified: false
tests_modified: false
provider_called: false
network_called: false
gemini_called: false
secrets_accessed: false
payment_executed: false
shipment_released: false
real_world_effects_count: 0
production_ready_claimed: false
public_auditor_ready_claimed: false

## Purpose

This preflight determines the narrowest safe implementation path for adding the
optional manual live Gemini lane to the already integrated Full Semantic E2E +
Supplier Payment WOW v1.1 spine.

The future live lane must prove:

- live Orchestrator role can propose semantics for the WOW path;
- live Architect role can propose bounded plan semantics for the WOW path;
- provider output enters only through semantic_reasoning_adapter,
  canonicalization, and local validators;
- Full E2E still includes `supplier_payment_wow_v1_1_summary`;
- SemanticEvidenceClaim remains candidate-only;
- closed ActionCommitPacket and receipt remain observed only unless the closed
  WOW summary is invoked;
- live Gemini creates no ActionCommitPacket;
- live Gemini creates no receipt;
- live Gemini executes no mock payment;
- live Gemini executes no real payment;
- live Gemini releases no shipment;
- Root alone creates FinalOutput;
- no real-world effects occur.

No runtime, tests, provider, network, secrets, payment, shipment, connector, or
mock execution was used for this preflight.

## Current Checkpoint Summary

- Runtime coherence commit: `b4a3f31`.
- Latest audit/docs commit: `f119d7c`.
- Full E2E runner: `demo/run_full_semantic_e2e_v01.py`.
- Full E2E tests: `tests/test_full_semantic_e2e_v01_runner.py`.
- WOW v1.1 runner: `demo/run_supplier_payment_shipment_release_review_wow_v1_1.py`.
- WOW v1.1 human walkthrough:
  `demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py`.
- Current audit log:
  `docs/audit_reports/auditor_full_semantic_e2e_live_evidence_wow_v1_1_coherence_v01.log`.
- Explicit live/captured evidence mode includes
  `supplier_payment_wow_v1_1_summary`.
- `supplier_payment_wow_v1_1_summary` is PASS in live/captured mode.
- SemanticEvidenceClaim remains candidate-only.
- Provider output is not truth, authority, action permission, or FinalOutput.
- Closed ActionCommitPacket and closed receipt are observed only.
- Live evidence creates no ActionCommitPacket, no receipt, and no mock payment.
- Supplier B remains blocked.
- shipment release remains held.
- receipt remains evidence only.
- Root alone creates FinalOutput.
- No real payment, no real shipment release, no real bank/supplier/warehouse
  API effects, and no real-world effects.
- Optional live Gemini lane is not yet enabled for this WOW path.

## 004-Class Live Basis

BSEP real Gemini 004 is the correct precedent class for this lane:

- Run id: `manual-bounded-semantic-evidence-real-gemini-slice-d-004`.
- It used live Orchestrator + live Architect provider roles.
- Expected live_model_call_count: 2.
- Expected gemini_called_count: 2.
- Expected orchestrator_provider_call_count: 1.
- Expected architect_provider_call_count: 1.
- Contract mode: `semantic_reasoning_adapter`.
- Schema mode: `json_mime_only`.
- BSEP gate: enabled.
- BSEP was created and validated before Architect.
- Provider output was treated as untrusted semantic proposal.
- Runtime canonicalized provider semantics into local artifacts.
- Validators verified local contracts.
- Root decided.
- Action counters remained zero.

The 007 live unknown-request run is also relevant:

- Run id: `manual-live-unknown-request-real-gemini-007`.
- It delegates semantic adapter mechanics to
  `hedgehog.semantic_reasoning_adapter`.
- It validates provider proposals locally.
- It preserves the boundary: provider proposes semantics, runtime
  canonicalizes, validators verify, Root decides.

## Existing Implementation Inventory

| Layer | Files | Status | Interpretation |
| --- | --- | --- | --- |
| Full Semantic E2E runner/test | `demo/run_full_semantic_e2e_v01.py`, `tests/test_full_semantic_e2e_v01_runner.py` | current_reusable_layer | Existing integration spine already includes supplier WOW summary, live/captured evidence mode, bounded Gemini role gates, dual-role sequencing, stage_map, and provider-output boundary counters. |
| Supplier Payment WOW v1.1 runner/test | `demo/run_supplier_payment_shipment_release_review_wow_v1_1.py`, `tests/test_supplier_payment_shipment_release_review_wow_v1_1_runner.py` | current_reusable_layer | Closed deterministic business WOW summary source. It should stay unchanged and be observed by Full E2E. |
| Human walkthrough runner/test | `demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py`, `tests/test_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough_runner.py` | closed_historical_layer | Human-readable closed checkpoint evidence. Not the right host for live provider roles. |
| Live unknown request dual rich context runner/test | `demo/run_live_unknown_request_dual_rich_context_v01.py`, `tests/test_live_unknown_request_dual_rich_context_v01.py` | current_reusable_layer | Owns the proven 004/007 live dual-role pattern: semantic_reasoning_adapter, BSEP gate, runtime canonicalization, local validation, and Root final boundary. |
| semantic_reasoning_adapter core/test | `hedgehog/semantic_reasoning_adapter.py`, `tests/test_semantic_reasoning_adapter_core.py` | current_reusable_layer | Approved live-provider architecture. It should be reused, not reimplemented. |
| BSEP/context packet core/test | `hedgehog/context_packets.py`, `tests/test_context_packets_core.py` | current_reusable_layer | Existing bounded evidence and ContextPacket contracts support canonicalization and local validation. |
| structured rationale core/test | `hedgehog/structured_rationale.py`, `tests/test_structured_rationale_core.py` | current_reusable_layer | Existing structured rationale contracts preserve non-authority and Root boundaries. |
| Live provider adapter response capture runner/test | `demo/run_live_provider_adapter_response_capture_v01.py`, `tests/test_live_provider_adapter_response_capture_v01_runner.py` | current_reusable_layer | Existing explicit provider adapter/capture path. Future work may reuse its env handling and secret redaction patterns. |
| Live LLM semantic evidence reader runner/test | `demo/run_live_llm_semantic_evidence_reader_v01.py`, `tests/test_live_llm_semantic_evidence_reader_v01_runner.py` | closed_historical_layer | Useful evidence-reader precedent, but not the dual-role Full WOW lane host. |
| Optional live LLM evidence reader smoke runner/test | `demo/run_optional_live_llm_evidence_reader_smoke_v01.py`, `tests/test_optional_live_llm_evidence_reader_smoke_v01_runner.py` | closed_historical_layer | Useful opt-in/manual smoke precedent, but not the Full WOW dual-role lane host. |

No inspected layer is missing. The gap is alignment of the Full E2E spine with a
manual 004-class dual live provider lane for the WOW path.

## Option Decision

Selected option:

preflight_verdict: APPROVE_OPTION_A_PATCH_EXISTING_FULL_E2E_MANUAL_LIVE_GEMINI_LANE

Why Option A:

- Full Semantic E2E is already the integration spine.
- Full E2E already invokes `supplier_payment_wow_v1_1_summary`.
- Full E2E already has explicit env-gated bounded Gemini Orchestrator and
  Architect role surfaces.
- Full E2E already tracks provider-output boundary counters and
  invoked_count/represented_count accounting.
- Full E2E already keeps deterministic default CI at zero provider/network/Gemini
  calls.
- The desired manual lane is an integration-spine capability, not a new domain
  demo and not a direct modification of the closed WOW v1.1 runner.

Rejected options:

- Option B is unnecessary because a new runner would duplicate the integration
  spine and increase accounting ambiguity.
- Option C is too narrow because the Supplier Payment WOW runner is a closed
  deterministic business WOW summary source; live dual-role provider semantics
  should be integrated above it in Full E2E.
- Option D is not required; docs and runtime status are aligned enough to plan
  a narrow runtime patch.

## Required Live Lane Shape

Any future runtime patch must:

- be manual/env-gated only;
- preserve deterministic default lane with zero network/Gemini/provider calls;
- not become a core PASS dependency;
- require an explicit env flag, recommended:
  `HEDGEHOG_FULL_WOW_V1_1_LIVE_GEMINI=1`;
- require provider credentials only in a manual live run;
- never log secrets;
- never place raw bank secrets in prompts;
- keep raw IBAN/token values out of Orchestrator and Architect prompts;
- reuse `hedgehog.semantic_reasoning_adapter`;
- produce structured/canonical runtime artifacts after provider output;
- validate BSEP / context packet boundaries;
- include `supplier_payment_wow_v1_1_summary`;
- include Full E2E live evidence + WOW v1.1 coherence boundaries;
- keep Supplier B blocked;
- keep shipment release held;
- keep receipt evidence-only;
- keep Root alone as FinalOutput creator;
- not create ActionCommitPacket;
- not create receipt;
- not execute mock payment;
- not execute real payment;
- not release shipment;
- not call real bank/supplier/warehouse APIs.

The future patch should add the smallest useful surface to
`demo/run_full_semantic_e2e_v01.py` and
`tests/test_full_semantic_e2e_v01_runner.py`:

- a new manual gate flag for the Full WOW live lane;
- a deterministic default path that leaves all live counters zero;
- an explicit manual/live path that performs exactly one Orchestrator provider
  role call and exactly one Architect provider role call when enabled;
- summary/counter aliases that distinguish the Full WOW manual lane from older
  bounded Gemini role tests;
- fail-closed behavior if provider artifacts, BSEP validation, or context
  packet validation fail.

## Required Counters For Future Live Run

When manual live lane is enabled:

- manual_live_gemini_lane_enabled_count: 1
- orchestrator_provider_call_count: 1
- architect_provider_call_count: 1
- live_model_call_count: 2
- gemini_called_count: 2
- network_used_count: 2
- semantic_reasoning_adapter_used_count >= 1
- runtime_canonicalization_count >= 1
- bsep_created_count >= 1
- bsep_validated_count >= 1
- provider_output_used_as_truth_count: 0
- provider_output_used_as_authority_count: 0
- provider_output_used_as_action_permission_count: 0
- provider_output_used_as_final_output_count: 0
- live_gemini_created_action_commit_packet_count: 0
- live_gemini_created_receipt_count: 0
- live_gemini_executed_mock_payment_count: 0
- live_gemini_executed_real_payment_count: 0
- live_gemini_released_shipment_count: 0
- real_payment_executed_count: 0
- shipment_released_count: 0
- real_world_effects_count: 0
- root_alone_creates_final_output_count: 1

When default deterministic CI lane runs:

- manual_live_gemini_lane_enabled_count: 0
- orchestrator_provider_call_count: 0
- architect_provider_call_count: 0
- live_model_call_count: 0
- gemini_called_count: 0
- network_used_count: 0
- deterministic_lane_passed_count: 1

## Required Tests For Future Runtime Patch

Default CI tests:

- no env flag means no Gemini/network/provider calls;
- deterministic Full E2E still PASS;
- existing WOW tests still PASS;
- live lane tests are skipped or not invoked without env flag;
- `supplier_payment_wow_v1_1_summary` remains present and PASS;
- SemanticEvidenceClaim remains candidate-only;
- Root alone creates FinalOutput.

Manual live tests:

- must be opt-in only;
- can be marked/manual and skipped unless env is explicitly set;
- must assert exactly two provider role calls if live run is enabled;
- must assert `semantic_reasoning_adapter` is used;
- must assert provider output is not truth, authority, action permission, or
  FinalOutput;
- must assert live Gemini creates no ActionCommitPacket, no receipt, and no mock
  payment;
- must assert no real payment, shipment release, connector/API effect, or
  real-world effect;
- must assert Root FinalOutput boundary is preserved;
- must assert BSEP / context packet validation fail-closed before Architect when
  malformed.

## Required Future Validation Plan

Default validation:

```bash
python3 -m py_compile \
  demo/run_full_semantic_e2e_v01.py \
  demo/run_live_unknown_request_dual_rich_context_v01.py \
  demo/run_supplier_payment_shipment_release_review_wow_v1_1.py \
  demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py

python3 -m demo.run_full_semantic_e2e_v01

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_full_semantic_e2e_v01_runner.py \
  tests/test_supplier_payment_live_evidence_integration_v02_runner.py \
  tests/test_supplier_payment_shipment_release_review_wow_v1_1_runner.py \
  tests/test_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough_runner.py \
  tests/test_live_unknown_request_dual_rich_context_v01.py \
  tests/test_semantic_reasoning_adapter_core.py \
  tests/test_context_packets_core.py \
  tests/test_structured_rationale_core.py

git diff --check
```

Future positive grep:

```bash
rg -n "HEDGEHOG_FULL_WOW_V1_1_LIVE_GEMINI|manual_live_gemini_lane_enabled_count|orchestrator_provider_call_count|architect_provider_call_count|live_model_call_count|gemini_called_count|semantic_reasoning_adapter_used_count|runtime_canonicalization_count|bsep_created_count|bsep_validated_count|supplier_payment_wow_v1_1_summary|provider_output_used_as_truth_count|provider_output_used_as_authority_count|provider_output_used_as_action_permission_count|provider_output_used_as_final_output_count|live_gemini_created_action_commit_packet_count|live_gemini_created_receipt_count|live_gemini_executed_mock_payment_count|live_gemini_executed_real_payment_count|live_gemini_released_shipment_count|Root alone creates FinalOutput" \
  demo/run_full_semantic_e2e_v01.py \
  tests/test_full_semantic_e2e_v01_runner.py
```

Future forbidden grep:

```bash
FORBIDDEN_OVERCLAIM_PATTERN="<production/public-readiness wording>|<real API/payment/shipment completion wording>|<provider-created ActionCommitPacket wording>|<receipt truth/permission/final-output wording>|<nonzero action/effect counters>"
rg -n "$FORBIDDEN_OVERCLAIM_PATTERN" \
  demo/run_full_semantic_e2e_v01.py \
  tests/test_full_semantic_e2e_v01_runner.py || true
```

Manual live validation:

```bash
HEDGEHOG_FULL_WOW_V1_1_LIVE_GEMINI=1 \
GEMINI_API_KEY=<local secret> \
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_full_semantic_e2e_v01_runner.py -k "manual_live_gemini"
```

The manual live validation must never print `GEMINI_API_KEY`, raw provider
credentials, raw bank secrets, raw IBAN values, or bank/supplier/warehouse API
tokens.

## Commands Run For This Preflight

```bash
git status --short --untracked-files=all
```

Result: clean before writing this preflight.

```bash
git --no-pager log --oneline --max-count=25
```

Result: current HEAD observed as `f119d7c Document Full Semantic E2E live
evidence WOW v1.1 coherence checkpoint`.

```bash
rg -n "manual-bounded-semantic-evidence-real-gemini-slice-d-004|manual-live-unknown-request-real-gemini-007|semantic_reasoning_adapter|orchestrator_provider_call_count|architect_provider_call_count|live_model_call_count|gemini_called_count|HEDGEHOG_UNKNOWN_REQUEST_LIVE_GEMINI|GOOGLE_API_KEY|GEMINI_API_KEY|supplier_payment_wow_v1_1_summary|FULL E2E LIVE EVIDENCE \\+ WOW V1.1 COHERENCE|provider_output_used_as_truth|provider_output_used_as_authority|provider_output_used_as_action_permission|provider_output_used_as_final_output" \
  README.md AGENTS.md specs docs demo tests hedgehog || true
```

Result: found 004/007 live basis, semantic_reasoning_adapter, current Full E2E
WOW summary/coherence counters, and provider-output non-authority counters.

```bash
python3 -m py_compile \
  demo/run_full_semantic_e2e_v01.py \
  demo/run_live_unknown_request_dual_rich_context_v01.py \
  demo/run_supplier_payment_shipment_release_review_wow_v1_1.py \
  demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py
```

Result: PASS.

```bash
python3 -m demo.run_full_semantic_e2e_v01
```

Result: PASS; `FINAL STATUS: PASS`; default counters preserve
`live_model_call_count: 0`, `network_used_count: 0`, `gemini_called_count: 0`,
`real_world_effects_count: 0`, and `supplier_payment_wow_v1_1_summary_invoked_count: 1`.

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_full_semantic_e2e_v01_runner.py \
  tests/test_supplier_payment_live_evidence_integration_v02_runner.py \
  tests/test_supplier_payment_shipment_release_review_wow_v1_1_runner.py \
  tests/test_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough_runner.py \
  tests/test_live_unknown_request_dual_rich_context_v01.py \
  tests/test_semantic_reasoning_adapter_core.py \
  tests/test_context_packets_core.py \
  tests/test_structured_rationale_core.py
```

Result: 424 passed, 2 warnings.

Warnings:

- `jsonschema.RefResolver` deprecation warnings from `hedgehog/post_vv.py`.

## Final Verdict

preflight_verdict: APPROVE_OPTION_A_PATCH_EXISTING_FULL_E2E_MANUAL_LIVE_GEMINI_LANE

This preflight approves a narrow future patch to the existing Full Semantic E2E
runner and tests. It does not approve a new bridge runner, direct Supplier WOW
runner mutation, production connector work, public auditor packaging, or any
runtime action boundary expansion.
