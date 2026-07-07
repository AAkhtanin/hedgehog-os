from __future__ import annotations

from pathlib import Path

import hedgehog.avf_v02 as avf_v02


def _candidate(**overrides: object) -> avf_v02.AVFCandidateV02:
    values = {
        "candidate_id": avf_v02.CANDIDATE_PREPARE_SUPPLIER_A_PAYMENT_FORM_ONLY,
        "candidate_label": "Prepare Supplier A payment form only",
        "source_drs_record_refs": ("supplier_a_prior_scoped_trace",),
        "candidate_direction": "Prepare a bounded form for later Root review.",
        "base_viability_score": 0.8,
    }
    values.update(overrides)
    return avf_v02.AVFCandidateV02(**values)


def test_avf_v02_candidate_is_not_authority_or_permission() -> None:
    candidate = _candidate()
    valid, reasons = avf_v02.validate_avf_candidate_v02(candidate)
    authority_ok, authority_reasons = avf_v02.assert_no_authority_fields(candidate)

    assert valid is True
    assert reasons == ()
    assert authority_ok is True
    assert authority_reasons == ()
    assert candidate.candidate_grants_permission is False
    assert candidate.candidate_is_action is False
    assert candidate.candidate_is_final_output is False


def test_avf_v02_score_is_not_permission() -> None:
    report = avf_v02.build_avf_decision_report_v02(
        _candidate(base_viability_score=1.0),
    )

    assert report.score_explanation.score_is_not_permission is True
    assert report.score_explanation.root_review_required is True
    assert report.payment_allowed is False


def test_avf_v02_top_ranked_candidate_not_permission() -> None:
    report = avf_v02.build_avf_decision_report_v02(_candidate(), rank=1)

    assert report.score_explanation.rank == 1
    assert report.score_explanation.top_ranked_candidate_not_permission is True
    assert report.approved is False
    assert report.execute is False
    assert report.ready is False


def test_avf_v02_hardmask_release_all_and_pay_all() -> None:
    candidate = _candidate(
        candidate_id=avf_v02.CANDIDATE_RELEASE_ALL_AND_PAY_ALL,
        candidate_label="Release all and pay all",
        base_viability_score=1.0,
    )
    hard_mask = avf_v02.build_hard_mask_v02(candidate)
    explanation = avf_v02.build_score_explanation_v02(candidate)

    assert hard_mask.hard_mask_value == 0
    assert (
        avf_v02.REASON_RELEASE_ALL_AND_PAY_ALL_FORBIDDEN
        in hard_mask.hard_mask_reasons
    )
    assert explanation.final_avf_score == 0.0


def test_avf_v02_supplier_b_payment_hardmasked() -> None:
    candidate = _candidate(
        candidate_id=avf_v02.CANDIDATE_PAY_SUPPLIER_B,
        candidate_label="Pay Supplier B",
        supplier_b_payment=True,
    )
    hard_mask = avf_v02.build_hard_mask_v02(candidate)

    assert hard_mask.hard_mask_value == 0
    assert avf_v02.REASON_SUPPLIER_B_PAYMENT_BLOCKED in hard_mask.hard_mask_reasons


def test_avf_v02_old_receipt_as_permission_hardmasked() -> None:
    candidate = _candidate(base_viability_score=1.0, old_receipt_as_permission=True)
    hard_mask = avf_v02.build_hard_mask_v02(candidate)
    explanation = avf_v02.build_score_explanation_v02(candidate)

    assert hard_mask.hard_mask_value == 0
    assert avf_v02.REASON_OLD_RECEIPT_NOT_PERMISSION in hard_mask.hard_mask_reasons
    assert explanation.final_avf_score == 0.0


def test_avf_v02_old_root_final_as_current_decision_hardmasked() -> None:
    candidate = _candidate(old_root_final_as_current_decision=True)
    hard_mask = avf_v02.build_hard_mask_v02(candidate)

    assert hard_mask.hard_mask_value == 0
    assert (
        avf_v02.REASON_OLD_ROOT_FINAL_NOT_CURRENT_DECISION
        in hard_mask.hard_mask_reasons
    )


def test_avf_v02_missing_time_envelope_temporal_query_invalid_ttl_hardmasked() -> None:
    cases = (
        (
            _candidate(time_envelope_present=False),
            avf_v02.REASON_MISSING_TIME_ENVELOPE,
        ),
        (
            _candidate(temporal_query_present=False),
            avf_v02.REASON_MISSING_TEMPORAL_QUERY,
        ),
        (_candidate(ttl_valid=False), avf_v02.REASON_INVALID_TTL),
    )

    for candidate, expected_reason in cases:
        hard_mask = avf_v02.build_hard_mask_v02(candidate)
        assert hard_mask.hard_mask_value == 0
        assert expected_reason in hard_mask.hard_mask_reasons


def test_avf_v02_quarantine_deadend_wrong_domain_permission_trace_hardmasked() -> None:
    cases = (
        (
            _candidate(quarantine_pressure=0.1),
            avf_v02.REASON_QUARANTINE_PRESSURE_HARD_MASK,
        ),
        (_candidate(deadend_pressure=0.1), avf_v02.REASON_DEADEND_PRESSURE_HARD_MASK),
        (
            _candidate(wrong_domain_pressure=0.1),
            avf_v02.REASON_WRONG_DOMAIN_PRESSURE_HARD_MASK,
        ),
        (
            _candidate(permission_trace_pressure=0.1),
            avf_v02.REASON_PERMISSION_TRACE_PRESSURE_HARD_MASK,
        ),
    )

    for candidate, expected_reason in cases:
        hard_mask = avf_v02.build_hard_mask_v02(candidate)
        assert hard_mask.hard_mask_value == 0
        assert expected_reason in hard_mask.hard_mask_reasons


def test_avf_v02_softmask_penalizes_stale_changed_conflict_pressure() -> None:
    candidate = _candidate(
        base_viability_score=0.9,
        staleness_penalty=0.1,
        changed_fact_pressure=0.2,
        conflict_pressure=0.1,
    )
    soft_mask = avf_v02.build_soft_mask_v02(candidate)
    explanation = avf_v02.build_score_explanation_v02(candidate)
    report = avf_v02.build_avf_decision_report_v02(candidate)

    assert soft_mask.soft_penalty == 0.4
    assert (
        avf_v02.REASON_STALE_LEGAL_ACCOUNTING_EVIDENCE
        in soft_mask.soft_penalty_reasons
    )
    assert avf_v02.REASON_CHANGED_WAREHOUSE_FACT in soft_mask.soft_penalty_reasons
    assert avf_v02.REASON_CONFLICT_PRESSURE in soft_mask.soft_penalty_reasons
    assert explanation.final_avf_score == 0.5
    assert report.payment_allowed is False


def test_avf_v02_hardmask_beats_high_score() -> None:
    explanation = avf_v02.build_score_explanation_v02(
        _candidate(base_viability_score=1.0, old_receipt_as_permission=True),
    )

    assert explanation.hard_mask_value == 0
    assert explanation.final_avf_score == 0.0


def test_avf_v02_safe_preparation_candidate_can_score_without_permission() -> None:
    candidate = _candidate(base_viability_score=0.75)
    report = avf_v02.build_avf_decision_report_v02(candidate)

    assert report.hard_mask.hard_mask_value == 1
    assert report.score_explanation.final_avf_score > 0.0
    assert report.approved is False
    assert report.execute is False
    assert report.payment_allowed is False
    assert report.root_review_required is True


def test_avf_v02_root_review_only_candidate_safe_but_not_final() -> None:
    candidate = _candidate(
        candidate_id=avf_v02.CANDIDATE_ROOT_REVIEW_ONLY,
        candidate_label="Root review only",
        base_viability_score=0.7,
    )
    report = avf_v02.build_avf_decision_report_v02(candidate)

    assert report.score_explanation.final_avf_score > 0.0
    assert report.score_explanation.final_output_claimed is False
    assert report.final_decision is False


def test_avf_v02_fixture_candidates_cover_wow_baseline() -> None:
    fixtures = avf_v02.build_wow_v1_2_avf_v02_candidate_fixtures()
    candidate_ids = {candidate.candidate_id for candidate in fixtures}

    assert candidate_ids == {
        avf_v02.CANDIDATE_RELEASE_ALL_AND_PAY_ALL,
        avf_v02.CANDIDATE_PAY_SUPPLIER_A_ONLY,
        avf_v02.CANDIDATE_PAY_SUPPLIER_B,
        avf_v02.CANDIDATE_PREPARE_SUPPLIER_A_PAYMENT_FORM_ONLY,
        avf_v02.CANDIDATE_REQUEST_FRESH_WAREHOUSE_VALIDATION,
        avf_v02.CANDIDATE_REQUEST_FRESH_LEGAL_ACCOUNTING_VALIDATION,
        avf_v02.CANDIDATE_KEEP_SHIPMENT_HELD,
        avf_v02.CANDIDATE_ROOT_REVIEW_ONLY,
        avf_v02.CANDIDATE_BLOCK_SUPPLIER_B_AND_HOLD_SHIPMENT,
    }


def test_avf_v02_decision_report_has_no_effects() -> None:
    report = avf_v02.build_avf_decision_report_v02(_candidate())
    authority_ok, authority_reasons = avf_v02.assert_no_authority_fields(report)

    assert report.real_world_effects_count == 0
    assert report.production_ready_claimed is False
    assert report.public_auditor_ready_claimed is False
    assert report.approved is False
    assert report.execute is False
    assert report.payment_allowed is False
    assert report.shipment_release_allowed is False
    assert authority_ok is True
    assert authority_reasons == ()


def _evaluation_report() -> avf_v02.AVFEvaluationReportV02:
    return avf_v02.evaluate_avf_candidates_v02(
        avf_v02.build_wow_v1_2_avf_v02_evaluation_input(),
    )


def _row_by_id(
    report: avf_v02.AVFEvaluationReportV02,
    candidate_id: str,
) -> avf_v02.AVFRankedCandidateRowV02:
    return next(row for row in report.ranked_candidates if row.candidate_id == candidate_id)


def _decision_by_id(
    report: avf_v02.AVFEvaluationReportV02,
    candidate_id: str,
) -> avf_v02.AVFDecisionReportV02:
    return next(
        decision for decision in report.decision_reports
        if decision.candidate_id == candidate_id
    )


def test_avf_v02_evaluator_builds_ranked_report() -> None:
    report = _evaluation_report()

    assert report.candidates_evaluated_count == 9
    assert len(report.ranked_candidates) == 9
    assert len(report.decision_reports) == 9
    assert report.hard_mask_table
    assert report.soft_mask_table
    assert report.score_explanation_table
    assert report.real_world_effects_count == 0


def test_avf_v02_evaluator_top_ranked_candidate_not_permission() -> None:
    report = _evaluation_report()
    top_decision = _decision_by_id(report, report.top_candidate_id or "")

    assert report.top_candidate_id is not None
    assert report.top_ranked_candidate_not_permission is True
    assert top_decision.approved is False
    assert top_decision.execute is False
    assert top_decision.payment_allowed is False
    assert top_decision.shipment_release_allowed is False
    assert top_decision.final_decision is False


def test_avf_v02_evaluator_hardmasked_candidates_score_zero() -> None:
    report = _evaluation_report()
    release_all = _row_by_id(report, avf_v02.CANDIDATE_RELEASE_ALL_AND_PAY_ALL)
    supplier_b = _row_by_id(report, avf_v02.CANDIDATE_PAY_SUPPLIER_B)

    assert release_all.final_avf_score == 0.0
    assert supplier_b.final_avf_score == 0.0
    assert release_all.hard_mask_value == 0
    assert supplier_b.hard_mask_value == 0


def test_avf_v02_evaluator_hardmask_beats_high_score() -> None:
    candidate = _candidate(
        candidate_id=avf_v02.CANDIDATE_RELEASE_ALL_AND_PAY_ALL,
        candidate_label="Release all and pay all",
        base_viability_score=1.0,
    )
    report = avf_v02.evaluate_avf_candidates_v02(
        avf_v02.AVFEvaluationInputV02(
            evaluation_id="hardmask-beats-score",
            candidates=(candidate,),
        ),
    )
    row = report.ranked_candidates[0]

    assert row.base_viability_score == 1.0
    assert row.hard_mask_value == 0
    assert row.final_avf_score == 0.0


def test_avf_v02_evaluator_safe_candidates_can_rank_without_permission() -> None:
    report = _evaluation_report()
    safe_candidate_ids = {
        avf_v02.CANDIDATE_PREPARE_SUPPLIER_A_PAYMENT_FORM_ONLY,
        avf_v02.CANDIDATE_ROOT_REVIEW_ONLY,
        avf_v02.CANDIDATE_KEEP_SHIPMENT_HELD,
    }

    for candidate_id in safe_candidate_ids:
        row = _row_by_id(report, candidate_id)
        decision = _decision_by_id(report, candidate_id)
        assert row.final_avf_score > 0.0
        assert row.score_is_not_permission is True
        assert row.candidate_vector_is_not_final_output is True
        assert row.root_review_required is True
        assert decision.payment_allowed is False
        assert decision.final_decision is False


def test_avf_v02_evaluator_reports_soft_penalty_reasons() -> None:
    report = _evaluation_report()
    warehouse = _row_by_id(
        report,
        avf_v02.CANDIDATE_REQUEST_FRESH_WAREHOUSE_VALIDATION,
    )
    legal_accounting = _row_by_id(
        report,
        avf_v02.CANDIDATE_REQUEST_FRESH_LEGAL_ACCOUNTING_VALIDATION,
    )

    assert avf_v02.REASON_CHANGED_WAREHOUSE_FACT in warehouse.soft_penalty_reasons
    assert avf_v02.REASON_RERUN_VALIDATION_PRESSURE in warehouse.soft_penalty_reasons
    assert (
        avf_v02.REASON_STALE_LEGAL_ACCOUNTING_EVIDENCE
        in legal_accounting.soft_penalty_reasons
    )


def test_avf_v02_evaluator_report_is_advisory_only() -> None:
    report = _evaluation_report()

    assert report.advisory_only is True
    assert report.avf_score_is_not_authority is True
    assert report.hardmask_is_not_root is True
    assert report.production_ready_claimed is False
    assert report.public_auditor_ready_claimed is False
    assert report.real_world_effects_count == 0


def test_avf_v02_evaluator_no_actions_or_outputs() -> None:
    report = _evaluation_report()

    for decision in report.decision_reports:
        assert decision.approved is False
        assert decision.execute is False
        assert decision.ready is False
        assert decision.payment_allowed is False
        assert decision.shipment_release_allowed is False
        assert decision.final_decision is False
        assert decision.score_explanation.truth_claimed is False
        assert decision.score_explanation.authority_claimed is False
        assert decision.score_explanation.action_permission_claimed is False
        assert decision.score_explanation.final_output_claimed is False


def test_avf_v02_wow_evaluation_input_includes_drs_refs() -> None:
    evaluation_input = avf_v02.build_wow_v1_2_avf_v02_evaluation_input()

    assert evaluation_input.source_drs_report_ref == (
        "local_drs_v0_2_reuse_decision_report"
    )
    assert set(evaluation_input.source_drs_record_refs) == {
        "supplier_a_prior_scoped_trace",
        "supplier_b_blocker_trace",
        "old_receipt_trace",
        "old_shipment_held_trace",
        "old_root_final_trace",
        "changed_warehouse_fact",
        "stale_legal_accounting_evidence",
        "quarantined_record",
        "deadend_record",
        "wrong_domain_near_match",
        "permission_trace_completed_action_attempt",
    }


def test_avf_v02_no_provider_network_runtime_imports() -> None:
    source = Path("hedgehog/avf_v02.py").read_text(encoding="utf-8")
    forbidden_terms = (
        "google.genai",
        "requests",
        "urllib",
        "openai",
        "subprocess",
        "run_full_wow",
        "run_full_semantic",
        "ActionCommitPacket creation",
        "MockBankSandbox execution",
        "real" + " payment" + " executed",
    )

    for term in forbidden_terms:
        assert term not in source
