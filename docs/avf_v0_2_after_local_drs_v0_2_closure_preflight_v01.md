# AVF v0.2 After Local DRS v0.2 Closure Preflight v01

## 1. Header

- document_id: avf_v0_2_after_local_drs_v0_2_closure_preflight_v01
- document_status: PREFLIGHT
- observed_base_head: dc6dac0
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- payment_executed: false
- shipment_released: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false

This document defines AVF v0.2 as the next local advisory candidate pressure,
ranking, and hard-mask layer after Local DRS v0.2 closure.

## 2. Closed Basis

Closed basis:

- Full WOW v1.2 PASS.
- Local DRS v0.2 PASS.
- Local DRS v0.2 live observation PASS.
- Local DRS v0.2 closure before AVF PASS.
- Closure audit:
  `docs/audit_reports/auditor_local_drs_v0_2_closure_before_avf_v01.log`.
- Source live observation audit:
  `docs/audit_reports/auditor_local_drs_v0_2_full_wow_v1_2_live_observation_real_run_v01.log`.

Closed Local DRS v0.2 facts:

- Slice A record/time/lineage model: PASS.
- Slice B local resolver/reuse decision report: PASS.
- Slice C Full WOW v1.2 deterministic product trace integration: PASS.
- Slice D adversarial/stale/quarantine/deadend hardening: PASS.
- Full WOW v1.2 + Local DRS v0.2 live observation real-provider run: PASS.
- DRS records evaluated: `11`.
- Direct reuse allowed by default: `0`.
- Root review required by default: `11`.
- BSEP carries bounded DRS context only.
- BSEP does not carry raw DRS tables.
- BSEP does not carry DRS authority.
- DRS writeback candidate after Root is local proof/audit only.
- Missing TimeEnvelope is rejected.
- Missing TemporalQuery is rejected.
- Invalid TTL is rejected.
- DRS remains not truth, not authority, and not permission.
- Root remains final authority.

The next layer is AVF v0.2 preflight, not AVF runtime.

## 3. AVF v0.2 Goal

AVF v0.2 upgrades AVF from simple score/rank existence into a clear risk
pressure, hard-mask, soft-mask, candidate suppression, and score explanation
layer.

Core formula:

```text
FV(v_i) = HM(v_i) * SM(v_i) * VS(v_i)
```

Where:

- `HM(v_i)` is HardMask, either `0` or `1`.
- `SM(v_i)` is SoftMask / soft penalty.
- `VS(v_i)` is weighted viability score.

AVF v0.2 should make candidate pressure visible before Architect-facing route
construction. It does not execute actions, create final artifacts, or replace
Root.

## 4. Non-Authority Boundaries

- AVF is not truth.
- AVF is not authority.
- AVF is not permission.
- AVF score is not truth.
- AVF score is not authority.
- AVF score is not permission.
- AVF score is not Root.
- Top-ranked candidate is not permission.
- HardMask is not Root.
- CandidateVector is not FinalOutput.
- CandidateVector is not action permission.
- DRS candidate is not truth.
- DRS candidate is not authority.
- DRS candidate is not permission.
- Root remains final authority.

AVF v0.2 must not:

- grant action permission;
- create FinalOutput;
- create ActionCommitPacket;
- create receipt;
- execute payment;
- release shipment;
- bypass Root;
- mutate DRS records;
- persist production/global DRS;
- call real connectors.

## 5. Inputs From Local DRS v0.2

AVF v0.2 consumes Local DRS v0.2 outputs only as bounded advisory inputs:

- DRS resolve report.
- Freshness table.
- Lineage table.
- Provenance table.
- Reuse decision table.
- Reason codes.
- `context_only` records.
- `partial_reuse_then_validation` records.
- `warning_only` records.
- `rerun_required` records.
- `blocked` records.
- `direct_reuse_candidate` records.
- `direct_reuse_allowed` only if a Root-gated all-hard-gates path is explicit,
  while still not becoming FinalOutput or action permission.

Default Full WOW v1.2 + Local DRS v0.2 input facts:

- `direct_reuse_allowed_count: 0`
- `root_review_required_count: 11`
- Candidate pressure must preserve DRS non-authority boundaries.

## 6. CandidateVector Model

Candidate classes for the WOW v1.2 baseline:

- `release_all_and_pay_all`
- `pay_supplier_a_only`
- `pay_supplier_b`
- `prepare_supplier_a_payment_form_only`
- `request_fresh_warehouse_validation`
- `request_fresh_legal_accounting_validation`
- `keep_shipment_held`
- `root_review_only`
- `block_supplier_b_and_hold_shipment`

These are candidate directions only, not actions. A CandidateVector can be
ranked, suppressed, or hard-masked, but it cannot create permission,
FinalOutput, payment, shipment release, receipt, or ActionCommitPacket.

## 7. HardMask Policy

HardMask examples for the WOW v1.2 baseline:

- `release_all_and_pay_all` -> HardMask `0`.
- Supplier B payment / `pay_supplier_b` -> HardMask `0` or blocked due to the
  Supplier B blocker trace.
- Shipment release candidate -> hard masked / held.
- `old_receipt_as_permission` -> hard masked.
- `old_root_final_as_current_decision` -> hard masked.
- Missing TimeEnvelope candidates -> hard masked.
- Missing TemporalQuery candidates -> hard masked.
- Invalid TTL candidates -> hard masked.
- Quarantine candidates -> hard masked.
- Deadend candidates -> hard masked or suppressed.
- Wrong-domain near match candidates -> hard masked.
- Permission trace completed action attempt candidates -> hard masked.

HardMask can suppress a candidate, but HardMask is not Root.

## 8. SoftMask / Risk Pressure

SoftMask and risk pressure sources:

- stale legal/accounting evidence.
- changed warehouse fact.
- conflict pressure.
- duplicate poisoning pressure.
- supplier_b blocker pressure.
- old receipt pressure.
- old Root Final lineage pressure.
- uncertainty pressure.
- source/provenance weakness.

SoftMask reduces or explains viability. It does not grant permission, does not
override HardMask, and does not replace Root review.

## 9. Score Explanation

Every AVF v0.2 candidate report should explain:

- `base_viability_score`
- `hard_mask_applied`
- `hard_mask_reasons`
- `soft_penalty`
- `soft_penalty_reasons`
- `final_avf_score`
- `rank`
- `why_score_is_not_permission`
- `root_review_required`

The score explanation must make clear that a candidate can be useful,
ranked, or suppressed without becoming action permission or FinalOutput.

## 10. WOW v1.2 Baseline Scenarios

Use the Full WOW v1.2 + Local DRS v0.2 baseline:

- `release_all_and_pay_all` -> HardMask `0`.
- Supplier B payment -> HardMask `0` or blocked/suppressed.
- Supplier A scoped preparation -> ranked but not permission.
- Prepare payment form only -> candidate may rank safe, but still not
  permission.
- old receipt -> hard masked as permission source.
- old Root Final -> lineage only, not current decision.
- changed warehouse fact -> rerun validation pressure.
- stale legal/accounting -> soft penalty or rerun pressure.
- quarantined record -> hard mask.
- deadend record -> hard mask or suppression.
- wrong-domain near match -> hard mask.
- permission trace completed action attempt -> hard mask.

The goal is visible advisory pressure: DRS candidates become CandidateVectors,
AVF applies HardMask / SoftMask / score explanation, and Root remains final
authority.

## 11. Proposed Implementation Slices

Slice A - AVF v0.2 local candidate/risk model:

- `AVFCandidateV02`
- `AVFHardMaskV02`
- `AVFSoftMaskV02`
- `AVFScoreExplanationV02`
- `AVFDecisionReportV02`

Slice B - AVF v0.2 local evaluator:

- deterministic evaluator over candidate vectors and DRS v0.2 signals.
- HM/SM/VS formula.
- ranked candidates.
- hard mask and soft mask tables.
- advisory report only.

Slice C - Full WOW v1.2 + Local DRS v0.2 baseline integration:

- no new demo.
- add AVF v0.2 section to existing deterministic product trace.
- show DRS candidates -> CandidateVectors -> AVF pressure/ranking -> still
  not permission.

Slice D - adversarial hard-mask tests:

- high score does not override hard mask.
- old receipt cannot become permission.
- Supplier B remains blocked.
- shipment release remains held.
- top-ranked candidate is not action permission.
- AVF cannot bypass Root.
- AVF cannot create FinalOutput.

Slice E - audit/docs sync:

- `auditor_avf_v0_2_after_local_drs_v0_2_v01.log`
- README / AGENTS / specs / manifest update.

## 12. Required Future Tests

Expected tests:

- `avf_score_is_not_authority`
- `top_ranked_candidate_not_permission`
- `hardmask_blocks_release_all_and_pay_all`
- `supplier_b_payment_hardmasked_or_suppressed`
- `old_receipt_not_permission_even_with_high_score`
- `old_root_final_not_current_decision`
- `stale_legal_accounting_penalized_or_rerun`
- `changed_warehouse_fact_requires_validation_pressure`
- `quarantine_deadend_wrong_domain_hardmasked`
- `permission_trace_cannot_be_completed_action`
- `hardmask_beats_high_score`
- `root_review_required_for_ranked_candidate`
- `avf_report_has_no_action_effects`

## 13. Explicit Non-Goals

- no AVF runtime implementation in this preflight.
- no ActionCommitPacket hardening.
- no Airline demo.
- no new domain demo.
- no production AVF.
- no production DRS.
- no external/global DRS.
- no vector DB requirement.
- no embeddings requirement.
- no real connectors.
- no action execution.
- no permission grant.
- no bypassing Root.
- no production or public-auditor claim.

## 14. Selected Path

Selected path: Option A - implement AVF v0.2 Slice A local candidate/risk
model first.

Reason:

Slice A creates the typed vocabulary for hard masks, soft masks, score
explanations, and candidate ranking before the evaluator or WOW integration.
That keeps the first implementation patch narrow and testable. It also lets
future Slice B consume Local DRS v0.2 records without turning DRS or AVF into
authority.

## 15. Next Immediate Implementation After Preflight

If this preflight is accepted, create Slice A in a narrow runtime/test patch.

Candidate allowed future files, not created by this preflight:

- `hedgehog/avf_v02.py` or `hedgehog/local_avf_v02.py`
- `tests/test_avf_v02_after_local_drs_v02.py`

The implementation should remain local and deterministic, with no provider,
network, Gemini, connector, payment, shipment, receipt, ActionCommitPacket, or
real-world effect.
