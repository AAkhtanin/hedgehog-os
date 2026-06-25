# Optional Live LLM Evidence Reader Smoke v0.1 PREFLIGHT

## Checkpoint

- preflight_id: optional_live_llm_evidence_reader_smoke_preflight_v01
- preflight_status: COMPLETE
- base_head: dd1e01b
- base_checkpoint: Document Live LLM Semantic Evidence Reader checkpoint
- previous_layer: Live LLM Semantic Evidence Reader / Extractor v0.1
- previous_layer_closed: true
- previous_layer_active_mode: deterministic_fixture_reader
- previous_layer_live_mode_default_off: true
- previous_layer_explicit_live_mode_fails_closed: true
- planning_only: true
- patch_plan_created: false
- runtime_modified: false
- deterministic_reader_modified: false
- schemas_modified: false
- tests_created: false
- demos_created: false
- audit_log_created: false
- network_called: false
- live_model_called: false
- gemini_called: false
- secrets_accessed: false
- connectors_called: false
- commit_created: false

## Purpose

Define the future Optional Live LLM Evidence Reader Smoke v0.1 layer.

The future layer should prove that one controlled optional live-model evidence
read can produce a bounded SemanticEvidenceClaim-shaped candidate that passes
local validation and remains non-authoritative.

This is NOT production live integration. This is NOT a core PASS dependency.
This is NOT Gemini/LLM authority. This is NOT activation of the disabled
live_llm_reader mode in the closed deterministic runtime. This is a future
optional smoke lane over the already closed deterministic contract.

## Conceptual Pipeline

dirty document
-> optional live model read outside core deterministic PASS path
-> raw model response captured as untrusted response file/text
-> local parser/validator maps it into SemanticEvidenceClaim shape
-> claim is candidate-only
-> Root review required
-> no action, no connector, no FinalOutput

## Critical Boundary

The existing Live LLM Semantic Evidence Reader / Extractor v0.1 must remain
closed:

- deterministic_fixture_reader remains default
- live_llm_reader remains default-off
- explicit live_llm_reader in deterministic runner remains fail-closed
- existing deterministic PASS path must not depend on live provider
- do not relax existing schema/dataclass semantics
- do not weaken authority/action counters

## Preflight Safety Decision

For the first optional live smoke, prefer response-file mode.

The live model call should happen outside the runner. The future runner should
consume a raw model response file and validate it locally.

Command adapter is explicitly deferred and is NOT part of this preflight
approval. Do NOT approve HEDGEHOG_OPTIONAL_LIVE_READER_COMMAND in this
preflight.

## Future Allowed First Runtime Direction

Response-file mode:

```text
HEDGEHOG_OPTIONAL_LIVE_EVIDENCE_SMOKE=1
HEDGEHOG_OPTIONAL_LIVE_RESPONSE_FILE=/path/to/raw_model_response.json
```

No explicit live config should mean:

```text
status = SKIPPED_CLOSED
semantic_claim_created_count = 0
live_model_call_count = 0
network_used_count = 0
connector_called_count = 0
silent_fallback_to_deterministic_pass = false
```

Explicit response-file config should mean:

```text
status = PASS only if exactly one response-file claim is locally validated
semantic_claim_created_count = 1
semantic_claim_validated_locally = true
semantic_claim_is_truth = false
semantic_claim_is_authority = false
semantic_claim_is_action_permission = false
network_used_count = 0
root_review_required = true
```

## Dirty Document Fixture Concept

Subject: SH-2042 / INV-2042

Warehouse says water_filter is short by 2, but supplier says stock is
available. Accounting says invoice INV-2042 looks payable. Legal note says the
insurance certificate may be expired. Please confirm whether we can pay and
release shipment.

Future model prompt must ask for extraction only. It must not ask for a
decision. It must not include raw IBAN, token, API key, connector details, or
real credentials.

## Future SemanticEvidenceClaim-Compatible Shape

- source_id
- source_kind
- extracted_claim
- confidence
- uncertainty_notes
- provenance_notes
- contradiction_flags
- freshness_hint
- unsafe_instruction_flags
- action_requested
- action_permission_claimed: false
- authority_claimed: false
- truth_claimed: false
- final_output_claimed: false
- connector_command_claimed: false
- root_review_required: true

## Future Rejection / Coercion Rule

If the live model writes decision-like text such as:

- invoice is valid
- supplier can be paid
- shipment can be released

the local validator must either reject it or preserve it only as
non-authoritative extracted text. It must never become truth, permission,
FinalOutput, or Root decision.

## Future Counters To Plan

- optional_live_smoke_invoked_count
- explicit_live_config_present_count
- skipped_closed_count
- live_model_call_count
- network_used_count
- raw_live_response_received_count
- raw_live_response_parse_error_count
- semantic_claim_created_count
- semantic_claim_validated_locally_count
- semantic_claim_rejected_count
- semantic_claim_is_truth_count: 0
- semantic_claim_is_authority_count: 0
- semantic_claim_is_action_permission_count: 0
- semantic_claim_is_final_output_count: 0
- root_review_required_count
- silent_fallback_to_deterministic_pass_count: 0
- deterministic_reader_mutated_count: 0
- connector_called_count: 0
- bank_connector_called_count: 0
- supplier_connector_called_count: 0
- warehouse_connector_called_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- raw_secret_exposed_to_llm_count: 0
- raw_iban_exposed_to_llm_count: 0
- raw_api_token_exposed_to_llm_count: 0
- secrets_logged_count: 0
- action_permission_created_count: 0
- non_root_final_output_created_count: 0
- root_authority_claimed_by_llm_count: 0
- root_final_authority_preserved_count

## Authority Boundaries

- Live model output is not truth.
- Live model output is not authority.
- Live model confidence is not authority.
- Live model extracted claim is not action permission.
- Live model cannot create FinalOutput.
- Live model cannot command bank/supplier/warehouse/Architect/Executor/Fractal Cell.
- Live model cannot access or receive business secrets.
- Live model cannot call production connectors.
- SemanticEvidenceClaim remains candidate evidence only.
- Contradiction detection is review signal only.
- Root review is required.
- Root remains final authority.

## Do Not Do

- Do not create patch plan in this task.
- Do not start Zero Trust Supplier Payment WOW v0.2.
- Do not integrate live evidence lane into WOW yet.
- Do not start NeedleFactory.
- Do not start Marennya.
- Do not start UP.
- Do not add production connectors.
- Do not add real bank/supplier/warehouse/DRS network calls.
- Do not add ActionCommitPacket.
- Do not add Permission UX.
- Do not add secrets/vault.
- Do not claim production E2E.
- Do not claim public auditor readiness.
- Do not mutate schemas by relaxation.
- Do not skip or xfail tests to hide failures.

## Final Preflight Verdict

Next layer after this preflight, if approved and committed, is:
Optional Live LLM Evidence Reader Smoke v0.1 patch plan.
