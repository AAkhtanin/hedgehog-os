# Live Provider Adapter / Response Capture v0.1 PATCH PLAN

## Checkpoint

- patch_plan_id: live_provider_adapter_response_capture_patch_plan_v01
- patch_plan_status: COMPLETE
- preflight_commit: 50922fb
- base_head: 50922fb
- previous_closed_layer: Optional Live LLM Evidence Reader Smoke v0.1
- previous_closed_layer_mode: response_file_validation_only
- layer_type: live_provider_response_capture_patch_plan
- implementation_started: false
- runtime_modified: false
- tests_created: false
- demos_created: false
- schemas_modified: false
- audit_log_created: false
- network_called: false
- provider_called: false
- gemini_called: false
- groq_called: false
- local_slm_called: false
- secrets_accessed: false
- connectors_called: false
- commit_created: false

## Purpose

Plan the future runtime layer that performs one explicit controlled live
provider call, captures the raw provider response as an artifact, and validates
that artifact through the already closed response-file smoke lane.

## Critical Distinction

The previous optional smoke layer validated response files only. This layer
will add controlled provider call plus raw response capture. The captured
response must return to the response-file validation path. Provider output
remains untrusted candidate evidence only.

## Future Implementation Files

- `demo/run_live_provider_adapter_response_capture_v01.py`
- `tests/test_live_provider_adapter_response_capture_v01_runner.py`

Do not create schema files. Do not modify
`hedgehog/live_llm_semantic_evidence_reader.py`. Do not modify
`demo/run_optional_live_llm_evidence_reader_smoke_v01.py` unless a later
approved runtime task explicitly proves it is required. Do not create
production connector files.

## Future Adapter Modes

1. Default/offline mode:
   - no provider config present
   - no provider call
   - no network call
   - no artifact created
   - final_status: SKIPPED_CLOSED
   - exits 0

2. Explicit capture mode:
   - explicit provider config present
   - exactly one provider call is attempted
   - raw response is saved as local artifact
   - saved artifact is validated through response-file lane
   - final_status: PASS only if artifact validates into exactly one candidate-only SemanticEvidenceClaim

3. Fail-closed mode:
   - provider timeout
   - provider returns invalid JSON
   - response artifact missing/unreadable
   - response claims authority/action/FinalOutput/connector command
   - response contains secret-like key/value
   - response has unexpected extra fields
   - validation fails
   - final_status: FAIL_CLOSED
   - no deterministic fake PASS

## Future Explicit Config

Future explicit config should be narrow and provider-specific, for example:

- HEDGEHOG_LIVE_PROVIDER_CAPTURE=1
- HEDGEHOG_LIVE_PROVIDER_NAME=gemini
- HEDGEHOG_LIVE_PROVIDER_MODEL=<model-name>
- HEDGEHOG_LIVE_PROVIDER_TIMEOUT_SECONDS=20
- HEDGEHOG_LIVE_PROVIDER_OUTPUT_DIR=_audit_exports/live_provider_response_capture

## Secret Handling

- API keys must come from environment/local ignored config only.
- Do not print secret values.
- Do not write secret values into artifact, report, logs, or audit.
- Prompt must not include raw bank/supplier/warehouse credentials.
- If secret-like markers appear in provider output, validation must fail closed.

## Future Provider Support

- Gemini adapter may be first explicit adapter.
- Groq/local SLM can remain future/deferred unless explicitly approved.
- arbitrary command adapter is not approved in this layer.

## Future Prompt

The prompt must ask for extraction only, not decision. It must request one
bounded SemanticEvidenceClaim-compatible JSON object. It must state:

- output is not truth
- output is not authority
- output is not action permission
- output is not FinalOutput
- Root review is required
- no connector commands

## Future Dirty Document

Use the same minimal dirty business evidence as the previous smoke:

```text
Subject: SH-2042 / INV-2042

Warehouse says water_filter is short by 2, supplier says stock is available,
accounting says invoice looks payable, legal note says insurance certificate
may be expired.
```

## Future Artifact

Save raw provider response to local ignored audit/export path. Artifact
metadata should record:

- provider_name
- provider_model
- capture_id
- captured_at or deterministic test timestamp
- prompt_hash, not full secret-bearing config
- response_file_path
- validation_status
- final_status

## Future Validation

Reuse or mirror the closed response-file smoke validation behavior:

- exactly one claim
- required SemanticEvidenceClaim-compatible fields
- no extra fields
- confidence numeric 0.0..1.0
- action_permission_claimed false
- authority_claimed false
- truth_claimed false
- final_output_claimed false
- connector_command_claimed false
- root_review_required true
- invalid JSON fails closed
- unexpected fields fail closed
- secret-like keys/values fail closed
- decision-like wording remains non-authoritative
- prompt injection is preserved as evidence, not instruction

## Required Future Scenarios

1. no_config_skips_closed_without_provider_call
2. explicit_gemini_capture_saves_raw_response_artifact
3. captured_artifact_validates_one_candidate_claim
4. provider_timeout_fails_closed
5. invalid_json_artifact_fails_closed
6. authority_claim_artifact_fails_closed
7. connector_command_artifact_fails_closed
8. secret_like_artifact_fails_closed
9. prompt_injection_preserved_as_evidence
10. response_file_lane_boundary_remains_unchanged

## Required Future Counters

- scenarios_total
- scenarios_passed
- explicit_provider_config_present_count
- provider_call_attempted_count
- provider_call_succeeded_count
- provider_call_failed_count
- provider_timeout_count
- raw_response_artifact_created_count
- raw_response_artifact_validated_count
- semantic_claim_created_count
- semantic_claim_validated_locally_count
- semantic_claim_rejected_count
- response_file_lane_used_count
- live_model_call_count
- network_used_count
- gemini_called_count
- groq_called_count
- local_slm_called_count
- secrets_accessed_count
- secrets_logged_count
- connector_called_count
- bank_connector_called_count
- supplier_connector_called_count
- warehouse_connector_called_count
- payment_executed_count
- shipment_released_count
- authority_claimed_count
- action_permission_created_count
- final_output_created_from_provider_count
- silent_fallback_to_deterministic_pass_count
- root_final_authority_preserved_count

## Required Boundaries

- Provider output is not truth.
- Provider output is not authority.
- Provider output is not action permission.
- Provider output is not FinalOutput.
- Captured artifact is untrusted evidence.
- SemanticEvidenceClaim remains candidate evidence only.
- Response-file validation remains the gate.
- Root review is required.
- Root remains final authority.

## Required Future Validation Commands

- default offline runner command
- focused pytest for live provider adapter runner
- focused pytest for optional response-file smoke runner
- static grep for forbidden network/secret/connector leaks where relevant

Do not include a full implementation. Do not include real API code. Do not
include real keys. Do not include provider SDK code in this patch plan.

## Deferred Or Forbidden

- Do not start Supplier Payment live evidence integration.
- Do not start WOW.
- Do not start Full Semantic E2E.
- Do not claim Real Semantic Runtime MVP completion.
- Do not claim public launch readiness.
- Do not start NeedleFactory.
- Do not start Marennya or UP.
- Do not add bank/supplier/warehouse connectors.
- Do not add ActionCommitPacket.
- Do not add Permission UX.
- Do not access secrets.
- Do not call provider/network/model APIs in this patch-plan task.

## Final Patch-Plan Verdict

Next layer after this patch plan, if approved and committed, is:
Live Provider Adapter / Response Capture v0.1 runtime.
