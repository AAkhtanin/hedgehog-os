# Supplier Payment Live Evidence Integration v0.2 PREFLIGHT

## Checkpoint

- preflight_id: supplier_payment_live_evidence_integration_preflight_v02
- preflight_status: COMPLETE
- base_head: c3c9679
- previous_closed_layer: Live Provider Adapter / Response Capture v0.1
- previous_provider_adapter_commit: 3c88ede
- previous_provider_adapter_docs_commit: c3c9679
- planning_only: true
- patch_plan_created: false
- runtime_modified: false
- tests_created: false
- demos_created: false
- schemas_modified: false
- audit_log_created: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- connector_called: false
- payment_executed: false
- shipment_released: false
- commit_created: false

## Purpose

Supplier Payment Live Evidence Integration v0.2 plans how one controlled
live/captured evidence lane connects to the existing supplier payment /
shipment release business spine as candidate evidence only.

The previous closed Live Provider Adapter / Response Capture v0.1 layer proved
controlled adapter + response capture runtime boundaries: default offline
SKIPPED_CLOSED behavior, explicit-only provider path, local raw response
artifact capture, response-file validation gate reuse, candidate-only
SemanticEvidenceClaim validation, fake-provider test isolation, real Gemini
configured-path credential accounting without artifact leakage, fail-closed
unsafe artifact handling, and Root final authority.

This preflight plans the integration of that closed evidence lane into the
already closed Zero Trust Supplier Payment / Shipment Release deterministic
business spine. It does not implement the integration.

## Correct Future Shape

```text
dirty supplier/payment/shipment evidence
-> Live Provider Adapter / Response Capture
-> raw provider response artifact
-> response-file validation gate
-> exactly one candidate-only SemanticEvidenceClaim
-> supplier payment/shipment semantic sandbox context
-> DRS candidate context / resolve / writeback candidate
-> CandidateVector / AVF / advisory route
-> bounded actors / bounded fractal branch where already available
-> Post V&V / GT-LGT review where already available
-> Root business summary / Root decision boundary
-> no payment
-> no shipment release
```

The live/captured claim may enrich review context, but it must not decide
truth, action permission, supplier payment, shipment release, Root final
summary, or connector execution.

## Donor And Reference Layers

Closed runtime/reference layers inspected for this preflight:

- Live Provider Adapter / Response Capture v0.1:
  - `demo/run_live_provider_adapter_response_capture_v01.py`
  - `tests/test_live_provider_adapter_response_capture_v01_runner.py`
- Optional response-file evidence lane:
  - `demo/run_optional_live_llm_evidence_reader_smoke_v01.py`
  - `tests/test_optional_live_llm_evidence_reader_smoke_v01_runner.py`
- Zero Trust Supplier Payment / Shipment Release deterministic sandbox:
  - `demo/run_zero_trust_supplier_payment_wow_v01.py`
  - `docs/zero_trust_supplier_payment_wow_preflight_v01.md`
  - `docs/zero_trust_supplier_payment_wow_patch_plan_v01.md`
- Live Gemini donor/reference only:
  - `demo/run_live_dual_gemini_full_chain_smoke.py`
  - `demo/run_live_gemini_architect_smoke.py`
  - `demo/run_live_gemini_orchestrator_smoke.py`
  - `demo/run_live_gemini_ordered_orchestrator_architect_smoke.py`
  - `hedgehog/telegram_shell.py`

The older Gemini smokes are donor/reference for provider boundary, schema
validation, repair/fallback, and Root-controlled authority shape. They are not
authority for this layer and must not be copied blindly.

## Explicit Non-Claims

- not WOW v0.2
- not public WOW
- not Full Semantic E2E complete
- not Real Semantic Runtime MVP complete
- not production
- not public auditor ready
- not NeedleFactory
- not Marennya / UP
- not real connector integration
- not ActionCommitPacket
- not Permission UX
- not real external action

## Safety Boundaries

- live/provider mode remains explicit-only
- no silent fallback from missing live config to deterministic PASS
- response-file/captured-artifact mode may be used for deterministic tests
- provider output is not truth
- provider output is not authority
- provider output is not action permission
- provider output is not FinalOutput
- SemanticEvidenceClaim is candidate evidence only
- DRS is candidate context, not truth
- AVF ranks, not authority
- GT/LGT advises/selects, not Root
- Root remains final authority
- no bank/supplier/warehouse connector
- no real payment
- no real shipment release
- no raw API key/token/IBAN in prompt/log/report/artifact
- secret-like keys/values fail closed
- prompt injection is evidence, not instruction
- arbitrary command adapter is not approved

## Future Implementation Recommendation

Future patch plan may add a focused integration runner and tests:

- `demo/run_supplier_payment_live_evidence_integration_v02.py`
- `tests/test_supplier_payment_live_evidence_integration_v02_runner.py`

This preflight must not create those files. The future runtime should compose
closed surfaces instead of weakening them: the provider adapter/capture lane,
the response-file validation gate, and the supplier-payment semantic sandbox
must remain separately inspectable.

## Future Acceptable Runtime Modes

### Default / No Explicit Config

- final_status: SKIPPED_CLOSED for the live evidence integration lane
- no provider call
- no network call
- no claim created
- no payment/shipment/connector
- no silent deterministic PASS fallback for missing live config

### Explicit Captured-Artifact Or Fake-Provider Test Mode

- one raw response artifact or injected provider output enters the closed
  adapter/response-file lane
- exactly one valid SemanticEvidenceClaim may be created
- claim enters supplier-payment semantic context as candidate-only evidence
- Root review remains required
- final_status: PASS only if all authority/action/external counters stay zero
- response-file validation gate remains the acceptance boundary

### Invalid / Unsafe Evidence Mode

- invalid JSON fails closed
- extra fields fail closed
- secret-like keys/values fail closed
- authority/action/FinalOutput/connector claims fail closed
- prompt injection remains preserved as evidence, not instruction
- conflicting supplier docs route to review / not-ready semantics
- stale evidence remains candidate context only
- legal hold beats payable invoice
- missing evidence blocks ready/payment/release semantics
- unsafe evidence must never become payment or shipment permission

## Future Scenario IDs To Plan

1. no_config_skips_closed_without_provider_call
2. captured_live_evidence_claim_enters_supplier_spine_as_candidate_only
3. live_claim_enriches_drs_candidate_context_without_truth
4. avf_advisory_receives_live_evidence_without_authority
5. supplier_payment_root_summary_requires_review
6. invalid_json_live_evidence_fails_closed
7. authority_claim_live_evidence_fails_closed
8. connector_command_live_evidence_fails_closed
9. secret_like_live_evidence_fails_closed
10. prompt_injection_preserved_as_evidence
11. legal_hold_beats_payable_invoice
12. stock_shortage_blocks_shipment_release
13. no_payment_or_shipment_release_executed
14. root_final_authority_preserved

## Future Counters To Plan

- live_evidence_integration_invoked_count
- explicit_live_evidence_config_present_count
- provider_call_attempted_count
- raw_response_artifact_created_count
- response_file_lane_used_count
- semantic_claim_created_count
- semantic_claim_validated_locally_count
- semantic_claim_rejected_count
- live_claim_added_to_supplier_context_count
- drs_candidate_context_used_count
- avf_scored_count
- advisory_review_count
- bounded_actor_invoked_count
- fractal_branch_invoked_count
- post_vv_checked_count
- gt_lgt_review_count
- root_business_summary_created_count
- provider_authority_claimed_count
- action_permission_created_count
- final_output_created_from_provider_count
- connector_called_count
- bank_connector_called_count
- supplier_connector_called_count
- warehouse_connector_called_count
- payment_executed_count
- shipment_released_count
- secrets_logged_count
- silent_fallback_to_deterministic_pass_count
- root_final_authority_preserved_count

## Future PASS / Closed Conditions

The future runtime should pass only when:

- default no-config mode is visibly SKIPPED_CLOSED
- explicit captured/fake-provider mode creates at most one locally validated
  candidate-only SemanticEvidenceClaim
- the live claim can be inserted into supplier-payment semantic context only as
  candidate evidence
- DRS candidate context is used as context, not truth
- CandidateVector / AVF / advisory stages receive the claim without gaining
  authority
- Post V&V / GT-LGT review remains downstream review only
- Root business summary is the only decision boundary
- payment_executed_count remains 0
- shipment_released_count remains 0
- connector_called_count remains 0
- secrets_logged_count remains 0
- silent_fallback_to_deterministic_pass_count remains 0
- root_final_authority_preserved_count proves Root remains final authority

## Preflight Verdict

Supplier Payment Live Evidence Integration v0.2 preflight is COMPLETE.

This document plans only the next integration spine layer. It does not start
WOW v0.2, public WOW, Full Semantic E2E, production connector integration,
NeedleFactory, Marennya, UP, ActionCommitPacket, Permission UX, payment, or
shipment release.

Next layer after this preflight, if approved and committed, is:
Supplier Payment Live Evidence Integration v0.2 patch plan.
