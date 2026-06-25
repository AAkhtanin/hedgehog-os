# Supplier Payment Live Evidence Integration v0.2 PATCH PLAN

## Checkpoint

- patch_plan_id: supplier_payment_live_evidence_integration_patch_plan_v02
- patch_plan_status: COMPLETE
- base_head: 896001a
- preflight_commit: 896001a
- planning_only: true
- runtime_created: false
- tests_created: false
- demos_created: false
- audit_log_created: false
- provider_called: false
- network_called: false
- secrets_accessed: false
- connector_called: false
- payment_executed: false
- shipment_released: false

## Purpose

Supplier Payment Live Evidence Integration v0.2 plans a runtime layer where
one captured/live-like SemanticEvidenceClaim enters the supplier-payment /
shipment-release business spine as candidate evidence only.

This is not WOW v0.2. This is not public WOW. This is not Full Semantic E2E.
This is not production. This is not NeedleFactory / Marennya / UP.

The future runtime must not be just another isolated proof-only demo. It is
still a controlled demo runner, but it must be shaped as an integration spine:
one focused place where already closed runtime-facing primitives are composed
without weakening their authority boundaries.

## Closed Surfaces To Compose

The future runtime should compose these closed surfaces:

- Live Provider Adapter / Response Capture v0.1
- Optional response-file SemanticEvidenceClaim validation lane
- Zero Trust Supplier Payment / Shipment Release deterministic sandbox
- DRS candidate context / CandidateVector / AVF / advisory / Post V&V /
  GT-LGT / Root boundary where available

The future runtime should not copy old live Gemini smoke files wholesale. Older
Gemini smokes are donor/reference only for provider boundary, schema
validation, repair/fallback, and Root-controlled authority shape. They are not
the authority for this layer.

## Future Implementation Files

Future allowed files for the runtime task:

- `demo/run_supplier_payment_live_evidence_integration_v02.py`
- `tests/test_supplier_payment_live_evidence_integration_v02_runner.py`

This patch plan is the final planning-only step for this slice. After this
patch plan is committed, the next approved layer is runtime implementation,
not another preflight, not another planning document, and not a human catalog.

The next approved runtime files are:

- `demo/run_supplier_payment_live_evidence_integration_v02.py`
- `tests/test_supplier_payment_live_evidence_integration_v02_runner.py`

This patch-plan task creates no runtime, test, demo, schema, audit, README,
spec, or audit-index changes.

## Runtime Design For Next Layer

The future runtime should:

- default to SKIPPED_CLOSED without explicit live/captured evidence config
- use response-file/captured artifact mode for deterministic tests
- allow injected fake provider only for tests
- compose closed adapter/response-file semantics instead of weakening them
- pass one candidate-only SemanticEvidenceClaim into supplier/payment context
- show DRS candidate context usage without truth authority
- show CandidateVector / AVF / advisory receiving claim without authority
- preserve Post V&V / GT-LGT / Root-only final boundary where available
- never execute payment/shipment/connector action

Recommended future flow:

```text
dirty supplier/payment/shipment evidence
-> Live Provider Adapter / Response Capture v0.1
-> raw provider response artifact
-> response-file SemanticEvidenceClaim validation lane
-> one candidate-only SemanticEvidenceClaim
-> supplier payment / shipment semantic context
-> DRS candidate context
-> CandidateVector context row
-> AVF score/rank as advisory signal
-> advisory review
-> Post V&V / GT-LGT review where available
-> Root business summary boundary
-> no payment
-> no shipment release
```

The future runtime may start as a runner-level integration spine. It should
keep counters and structured results shaped so a later extraction point into
`hedgehog/` can be documented without changing the authority model.

## Not Proof-Only Direction

This layer should be more than a disconnected demo:

- one place where closed primitives are composed
- counters expose reusable boundary behavior
- future extraction point into `hedgehog/` can be documented
- no giant copy-paste of old Gemini smoke files
- older Gemini smokes are donor/reference only
- closed adapter, response-file lane, and supplier sandbox remain visible
- no shortcut turns captured evidence into action permission

The intended contribution is an integration spine, not a public WOW packet.

## Invoked vs Represented Semantics

Use `*_invoked_count` only when the future runtime directly calls that closed
runtime surface or helper. Use `*_represented_count` when the supplier sandbox
only represents that layer's semantics without directly invoking it.

Do not claim represented Post V&V / GT-LGT / bounded actor / fractal branch
behavior as direct invocation. This layer is not Full Semantic E2E.

## Future Runtime Modes

### Default / No Explicit Config

- final_status: SKIPPED_CLOSED
- no provider call
- no network call
- no raw response artifact created
- no SemanticEvidenceClaim created
- no supplier context mutation
- no payment
- no shipment release
- no connector
- no silent deterministic PASS fallback

### Explicit Captured-Artifact / Fake-Provider Test Mode

- explicit config or injected fake provider is present
- raw response artifact enters the closed adapter/response-file lane
- exactly one valid SemanticEvidenceClaim may be created
- claim is added to supplier-payment context as candidate-only evidence
- DRS candidate context may be built from the claim and deterministic sandbox
  facts
- CandidateVector / AVF / advisory may receive the claim as context
- Post V&V / GT-LGT / Root boundary remains downstream
- final_status: PASS only if all authority/action/external counters remain 0

### Invalid / Unsafe Evidence Mode

- invalid JSON fails closed
- extra fields fail closed
- secret-like keys/values fail closed
- authority/action/FinalOutput/connector claims fail closed
- prompt injection is preserved as evidence, not instruction
- stale evidence cannot authorize payment
- legal hold beats payable invoice
- stock shortage blocks shipment release
- conflicting supplier evidence remains visible
- unsafe evidence never becomes payment/shipment permission

## Required Future Scenario IDs

1. no_config_skips_closed_without_provider_call
2. captured_live_evidence_claim_enters_supplier_spine_as_candidate_only
3. live_claim_enriches_drs_candidate_context_without_truth
4. candidate_vector_receives_live_evidence_context
5. avf_advisory_receives_live_evidence_without_authority
6. legal_hold_beats_payable_invoice
7. stock_shortage_blocks_shipment_release
8. invalid_json_live_evidence_fails_closed
9. extra_fields_live_evidence_fails_closed
10. secret_like_live_evidence_fails_closed
11. authority_claim_live_evidence_fails_closed
12. connector_command_live_evidence_fails_closed
13. prompt_injection_preserved_as_evidence
14. no_payment_or_shipment_release_executed
15. root_final_authority_preserved

## Required Future Counters

- supplier_live_integration_invoked_count
- explicit_live_evidence_config_present_count
- provider_call_attempted_count
- raw_response_artifact_created_count
- response_file_lane_used_count
- semantic_claim_created_count
- semantic_claim_validated_locally_count
- semantic_claim_rejected_count
- live_claim_added_to_supplier_context_count
- drs_candidate_context_used_count
- candidate_vector_created_count
- candidate_vector_represented_count
- avf_scored_count
- avf_invoked_count
- avf_represented_count
- advisory_review_count
- advisory_invoked_count
- advisory_represented_count
- bounded_actor_invoked_count
- bounded_actor_represented_count
- fractal_branch_invoked_count
- fractal_branch_represented_count
- post_vv_checked_count
- post_vv_invoked_count
- post_vv_represented_count
- gt_lgt_review_count
- gt_lgt_invoked_count
- gt_lgt_represented_count
- root_business_summary_created_count
- provider_authority_claimed_count
- action_permission_created_count
- final_output_created_from_provider_count
- provider_final_output_created_count
- connector_called_count
- bank_connector_called_count
- supplier_connector_called_count
- warehouse_connector_called_count
- payment_executed_count
- shipment_released_count
- secrets_logged_count
- silent_fallback_to_deterministic_pass_count
- full_semantic_e2e_claimed_count
- real_semantic_runtime_mvp_complete_claimed_count
- wow_started_count
- production_ready_claimed_count
- root_final_authority_preserved_count

## Future PASS Conditions

The future runner should PASS only when:

- default no-config mode is visibly SKIPPED_CLOSED
- explicit captured/fake-provider mode validates exactly one candidate claim
- semantic_claim_created_count is 1 only for valid explicit evidence mode
- semantic_claim_rejected_count increases for invalid or unsafe evidence
- live claim enters supplier context only as candidate evidence
- DRS candidate context does not claim truth
- CandidateVector context does not claim truth
- AVF score/rank does not claim authority
- advisory review does not claim Root finality
- Post V&V / GT-LGT remain review stages
- Root business summary is the only decision boundary
- provider_authority_claimed_count remains 0
- action_permission_created_count remains 0
- final_output_created_from_provider_count remains 0
- connector_called_count remains 0
- bank_connector_called_count remains 0
- supplier_connector_called_count remains 0
- warehouse_connector_called_count remains 0
- payment_executed_count remains 0
- shipment_released_count remains 0
- secrets_logged_count remains 0
- silent_fallback_to_deterministic_pass_count remains 0
- full_semantic_e2e_claimed_count remains 0
- real_semantic_runtime_mvp_complete_claimed_count remains 0
- wow_started_count remains 0
- production_ready_claimed_count remains 0
- provider_final_output_created_count remains 0
- represented_count values must not be reported as invoked_count values
- root_final_authority_preserved_count proves Root remains final authority

## Required Future Focused Tests

Future tests should assert:

- module imports
- default no-config mode returns SKIPPED_CLOSED
- default no-config mode attempts no provider call
- default no-config mode creates no claim
- valid captured/fake-provider evidence returns PASS
- valid evidence creates exactly one candidate-only SemanticEvidenceClaim
- live claim enters supplier-payment context as candidate only
- live claim enriches DRS candidate context without truth
- candidate vector receives live evidence context without truth
- AVF / advisory receives live evidence without authority
- legal hold beats payable invoice
- stock shortage blocks shipment release
- invalid JSON fails closed
- extra fields fail closed
- secret-like evidence fails closed
- authority claims fail closed
- connector command claims fail closed
- prompt injection is evidence, not instruction
- no payment or shipment release is executed
- Root remains final authority
- existing live provider adapter tests still pass
- existing optional response-file smoke tests still pass
- existing Zero Trust Supplier Payment WOW tests still pass

## Safety / Forbidden

- no WOW v0.2 started
- no public WOW
- no Full Semantic E2E complete claim
- no Real Semantic Runtime MVP complete claim
- no production ready claim
- no public auditor ready claim
- no NeedleFactory / Marennya / UP
- no ActionCommitPacket
- no Permission UX
- no real external action
- no real bank/supplier/warehouse connector
- no LLM/provider authority
- no DRS truth
- no AVF authority
- no GT finalization
- Root remains final authority

## Acceptance Criteria For This Patch Plan

- only `docs/supplier_payment_live_evidence_integration_patch_plan_v02.md`
  is new/changed
- no runtime/test/demo/audit/docs checkpoint changes
- no provider/network/model call
- no secrets access
- no connector
- no payment execution
- no shipment release
- no commit
- git diff --check is clean
- positive grep markers are present
- forbidden/overclaim grep has no unsafe positive claims

## Final Patch-Plan Verdict

Supplier Payment Live Evidence Integration v0.2 patch plan is COMPLETE.

Next layer after this patch plan, if approved and committed, is:
Supplier Payment Live Evidence Integration v0.2 runtime.
