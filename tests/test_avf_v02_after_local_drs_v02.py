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
