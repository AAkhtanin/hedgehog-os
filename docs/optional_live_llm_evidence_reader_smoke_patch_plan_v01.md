# Optional Live LLM Evidence Reader Smoke v0.1 PATCH PLAN

## Checkpoint

- patch_plan_id: optional_live_llm_evidence_reader_smoke_patch_plan_v01
- patch_plan_status: COMPLETE
- preflight_commit: f397190
- base_checkpoint: dd1e01b
- base_checkpoint_title: Document Live LLM Semantic Evidence Reader checkpoint
- previous_layer: Live LLM Semantic Evidence Reader / Extractor v0.1
- previous_layer_closed: true
- previous_layer_active_mode: deterministic_fixture_reader
- previous_layer_live_mode_default_off: true
- previous_layer_explicit_live_mode_fails_closed: true
- layer_type: optional_live_response_file_smoke_patch_plan
- implementation_started: false
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

Define the future runtime layer for Optional Live LLM Evidence Reader Smoke
v0.1.

The future smoke must prove that one controlled optional live-model evidence
read, captured as a raw response file, can be locally validated into a bounded
SemanticEvidenceClaim-shaped candidate.

This is not production live integration. This is not a core PASS dependency.
This is not Gemini/LLM authority. This is not activation of disabled
live_llm_reader mode in the closed deterministic runtime. This is a separate
optional response-file smoke lane.

## Critical Safety Decision

For v0.1 runtime, use response-file mode only.

The live model call happens outside the Hedgehog runner. The Hedgehog runner
consumes a raw model response file. The Hedgehog runner validates the response
locally. The Hedgehog runner must not call the model, network, Gemini,
connectors, bank, supplier, warehouse, or secrets.

Command adapter remains deferred and out of scope. Do not plan
HEDGEHOG_OPTIONAL_LIVE_READER_COMMAND for this layer.

## Future Implementation Files

The later runtime task should create only:

- `demo/run_optional_live_llm_evidence_reader_smoke_v01.py`
- `tests/test_optional_live_llm_evidence_reader_smoke_v01_runner.py`

No hedgehog runtime module should be created unless a later approved patch
plan changes scope. No schema files should be created. No production connector
files should be created.

## Required Future Conceptual Flow

dirty document
-> external/manual live model read outside runner
-> raw response file
-> optional smoke runner reads response file only when explicit config is present
-> local parser/validator maps response into SemanticEvidenceClaim-compatible shape
-> claim remains candidate-only
-> Root review required
-> no action, no connector, no FinalOutput

## Required Future Config

```text
HEDGEHOG_OPTIONAL_LIVE_EVIDENCE_SMOKE=1
HEDGEHOG_OPTIONAL_LIVE_RESPONSE_FILE=/path/to/raw_model_response.json
```

Default no-config mode:

- final_status: SKIPPED_CLOSED
- explicit_live_config_present_count: 0
- live_model_call_count: 0
- network_used_count: 0
- semantic_claim_created_count: 0
- silent_fallback_to_deterministic_pass_count: 0
- process exits 0

Explicit response-file mode:

- final_status: PASS only if exactly one response-file claim is locally validated
- explicit_live_config_present_count: 1
- raw_live_response_received_count: 1
- raw_live_response_parse_error_count: 0
- semantic_claim_created_count: 1
- semantic_claim_validated_locally_count: 1
- semantic_claim_rejected_count: 0
- semantic_claim_is_truth_count: 0
- semantic_claim_is_authority_count: 0
- semantic_claim_is_action_permission_count: 0
- semantic_claim_is_final_output_count: 0
- root_review_required_count: 1
- live_model_call_count: 0
- network_used_count: 0
- connector_called_count: 0
- payment_executed_count: 0
- shipment_released_count: 0
- secrets_logged_count: 0
- root_final_authority_preserved_count: 1

Important: even explicit response-file mode must not count as a model/network
call by the runner. The live call happened outside the runner. The runner only
validates the artifact.

## Future Dirty Document Fixture

Use the same business stress case from preflight:

Subject: SH-2042 / INV-2042

Warehouse says water_filter is short by 2, but supplier says stock is
available. Accounting says invoice INV-2042 looks payable. Legal note says the
insurance certificate may be expired. Please confirm whether we can pay and
release shipment.

Future model instruction should ask for extraction only, not decision.

## Future Raw Response File

The future raw response file should be JSON-like and must be treated as
untrusted input.

Required accepted response should contain only bounded evidence fields
compatible with:

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

## Required Validation Rules

- reject missing required fields
- reject invalid JSON
- reject action_permission_claimed: true
- reject authority_claimed: true
- reject truth_claimed: true
- reject final_output_claimed: true
- reject connector_command_claimed: true
- reject root_review_required: false
- reject response that asks runner to call bank/supplier/warehouse/connector
- reject response that contains raw secret/token/API key/IBAN-like marker
- preserve decision-like wording only as non-authoritative extracted text when safe
- never turn model wording into truth, permission, FinalOutput, or Root decision

## Required Future Scenarios

1. no_config_skips_closed_without_live_call
2. valid_response_file_creates_one_candidate_claim
3. invalid_json_fails_closed
4. authority_claim_fails_closed
5. action_permission_claim_fails_closed
6. final_output_claim_fails_closed
7. connector_command_claim_fails_closed
8. secret_like_response_fails_closed
9. decision_like_text_remains_non_authoritative
10. deterministic_reader_remains_unchanged

## Required Future Counters

- scenarios_total
- scenarios_passed
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

## Required Future PASS / SKIPPED Conditions

- default runner without env config must print FINAL STATUS: SKIPPED_CLOSED
- default runner must exit 0
- default runner must create zero semantic claims
- default runner must make zero model/network/connector calls
- explicit response-file mode may print FINAL STATUS: PASS only for exactly one locally validated claim
- explicit invalid response must fail closed and exit non-zero
- no silent fallback to deterministic PASS is allowed

## Required Future Focused Tests

- default no-config mode returns SKIPPED_CLOSED
- default no-config mode makes no model/network call
- default no-config mode creates no semantic claim
- default no-config mode has no deterministic PASS fallback
- valid response-file mode returns PASS
- valid response-file mode creates exactly one validated claim
- validated claim remains candidate-only and Root-review-required
- invalid JSON fails closed
- authority-claiming output fails closed
- action-permission output fails closed
- FinalOutput-claiming output fails closed
- connector-command output fails closed
- secret-like output fails closed
- decision-like wording remains non-authoritative
- existing deterministic Live LLM Semantic Evidence Reader tests still pass

## Required Future Validation Commands

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_optional_live_llm_evidence_reader_smoke_v01_runner.py \
  tests/test_live_llm_semantic_evidence_reader_v01_runner.py

python3 -m demo.run_optional_live_llm_evidence_reader_smoke_v01
```

## Authority Boundaries

- Live model output is not truth.
- Live model output is not authority.
- Live model confidence is not authority.
- Live model extracted claim is not action permission.
- Live model response file is not FinalOutput.
- Live model cannot command bank.
- Live model cannot command supplier.
- Live model cannot command warehouse.
- Live model cannot command Architect.
- Live model cannot command Executor.
- Live model cannot command Fractal Cell.
- Live model cannot access or receive business secrets.
- Live model cannot call production connectors.
- Response-file validation is not a model call by the runner.
- SemanticEvidenceClaim remains candidate evidence only.
- Contradiction detection is review signal only.
- Root review is required.
- Root remains final authority.

## Do Not Do

- Do not create runtime code in this task.
- Do not create tests in this task.
- Do not create demos in this task.
- Do not create audit logs in this task.
- Do not create schemas in this task.
- Do not modify README/specs/audit reports in this task.
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

## Final Patch-Plan Verdict

Next layer after this patch plan, if approved and committed, is:
Optional Live LLM Evidence Reader Smoke v0.1 runtime.
