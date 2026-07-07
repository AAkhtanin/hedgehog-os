from __future__ import annotations

from dataclasses import dataclass


AVF_FORMULA = "FV(v_i) = HM(v_i) * SM(v_i) * VS(v_i)"

CANDIDATE_RELEASE_ALL_AND_PAY_ALL = "release_all_and_pay_all"
CANDIDATE_PAY_SUPPLIER_A_ONLY = "pay_supplier_a_only"
CANDIDATE_PAY_SUPPLIER_B = "pay_supplier_b"
CANDIDATE_PREPARE_SUPPLIER_A_PAYMENT_FORM_ONLY = (
    "prepare_supplier_a_payment_form_only"
)
CANDIDATE_REQUEST_FRESH_WAREHOUSE_VALIDATION = (
    "request_fresh_warehouse_validation"
)
CANDIDATE_REQUEST_FRESH_LEGAL_ACCOUNTING_VALIDATION = (
    "request_fresh_legal_accounting_validation"
)
CANDIDATE_KEEP_SHIPMENT_HELD = "keep_shipment_held"
CANDIDATE_ROOT_REVIEW_ONLY = "root_review_only"
CANDIDATE_BLOCK_SUPPLIER_B_AND_HOLD_SHIPMENT = (
    "block_supplier_b_and_hold_shipment"
)

REASON_RELEASE_ALL_AND_PAY_ALL_FORBIDDEN = "release_all_and_pay_all_forbidden"
REASON_SUPPLIER_B_PAYMENT_BLOCKED = "supplier_b_payment_blocked"
REASON_SHIPMENT_RELEASE_HELD = "shipment_release_held"
REASON_OLD_RECEIPT_NOT_PERMISSION = "old_receipt_not_permission"
REASON_OLD_ROOT_FINAL_NOT_CURRENT_DECISION = "old_root_final_not_current_decision"
REASON_MISSING_TIME_ENVELOPE = "missing_time_envelope"
REASON_MISSING_TEMPORAL_QUERY = "missing_temporal_query"
REASON_INVALID_TTL = "invalid_ttl"
REASON_QUARANTINE_PRESSURE_HARD_MASK = "quarantine_pressure_hard_mask"
REASON_DEADEND_PRESSURE_HARD_MASK = "deadend_pressure_hard_mask"
REASON_WRONG_DOMAIN_PRESSURE_HARD_MASK = "wrong_domain_pressure_hard_mask"
REASON_PERMISSION_TRACE_PRESSURE_HARD_MASK = "permission_trace_pressure_hard_mask"
REASON_ACTION_CANDIDATE_REQUIRES_ROOT_REVIEW = (
    "action_candidate_requires_root_review"
)

REASON_STALE_LEGAL_ACCOUNTING_EVIDENCE = "stale_legal_accounting_evidence"
REASON_CHANGED_WAREHOUSE_FACT = "changed_warehouse_fact"
REASON_CONFLICT_PRESSURE = "conflict_pressure"
REASON_DUPLICATE_POISONING_PRESSURE = "duplicate_poisoning_pressure"
REASON_SUPPLIER_B_BLOCKER_PRESSURE = "supplier_b_blocker_pressure"
REASON_OLD_RECEIPT_PRESSURE = "old_receipt_pressure"
REASON_OLD_ROOT_FINAL_PRESSURE = "old_root_final_pressure"
REASON_SOURCE_PROVENANCE_WEAKNESS = "source_provenance_weakness"
REASON_UNCERTAINTY_PRESSURE = "uncertainty_pressure"
REASON_RERUN_VALIDATION_PRESSURE = "rerun_validation_pressure"

REASON_AVF_SCORE_NOT_PERMISSION = "avf_score_not_permission"
REASON_TOP_RANKED_CANDIDATE_NOT_PERMISSION = "top_ranked_candidate_not_permission"
REASON_CANDIDATE_IS_NOT_ACTION = "candidate_is_not_action"
REASON_CANDIDATE_VECTOR_NOT_FINAL_OUTPUT = "candidate_vector_not_final_output"
REASON_HARDMASK_IS_NOT_ROOT = "hardmask_is_not_root"
REASON_ROOT_REVIEW_REQUIRED = "root_review_required"
REASON_ROOT_REMAINS_FINAL_AUTHORITY = "root_remains_final_authority"

REASON_CANDIDATE_ID_REQUIRED = "candidate_id_required"
REASON_CANDIDATE_LABEL_REQUIRED = "candidate_label_required"
REASON_BASE_VIABILITY_SCORE_OUT_OF_RANGE = "base_viability_score_out_of_range"
REASON_TRUTH_CLAIMED = "truth_claimed"
REASON_AUTHORITY_CLAIMED = "authority_claimed"
REASON_ACTION_PERMISSION_CLAIMED = "action_permission_claimed"
REASON_FINAL_OUTPUT_CLAIMED = "final_output_claimed"
REASON_APPROVED_NOT_ALLOWED = "approved_not_allowed"
REASON_EXECUTE_NOT_ALLOWED = "execute_not_allowed"
REASON_READY_NOT_ALLOWED = "ready_not_allowed"
REASON_PAYMENT_ALLOWED_NOT_ALLOWED = "payment_allowed_not_allowed"
REASON_SHIPMENT_RELEASE_ALLOWED_NOT_ALLOWED = "shipment_release_allowed_not_allowed"
REASON_FINAL_DECISION_NOT_ALLOWED = "final_decision_not_allowed"
REASON_FINAL_SCORE_OUT_OF_RANGE = "final_avf_score_out_of_range"
REASON_HARD_MASK_SCORE_MUST_BE_ZERO = "hard_mask_score_must_be_zero"


@dataclass(frozen=True)
class AVFCandidateV02:
    candidate_id: str
    candidate_label: str
    source_drs_record_refs: tuple[str, ...] = ()
    candidate_direction: str = ""
    base_viability_score: float = 0.0
    candidate_is_action: bool = False
    candidate_is_final_output: bool = False
    candidate_grants_permission: bool = False
    truth_claimed: bool = False
    authority_claimed: bool = False
    action_permission_claimed: bool = False
    final_output_claimed: bool = False
    root_review_required: bool = True
    freshness_pressure: float = 0.0
    staleness_penalty: float = 0.0
    changed_fact_pressure: float = 0.0
    conflict_pressure: float = 0.0
    quarantine_pressure: float = 0.0
    deadend_pressure: float = 0.0
    wrong_domain_pressure: float = 0.0
    permission_trace_pressure: float = 0.0
    old_receipt_pressure: float = 0.0
    old_root_final_pressure: float = 0.0
    duplicate_poisoning_pressure: float = 0.0
    source_provenance_weakness_pressure: float = 0.0
    uncertainty_pressure: float = 0.0
    time_envelope_present: bool = True
    temporal_query_present: bool = True
    ttl_valid: bool = True
    old_receipt_as_permission: bool = False
    old_root_final_as_current_decision: bool = False
    supplier_b_payment: bool = False
    shipment_release_candidate: bool = False
    release_all_candidate: bool = False


@dataclass(frozen=True)
class AVFHardMaskV02:
    hard_mask_applied: bool
    hard_mask_value: int
    hard_mask_reasons: tuple[str, ...]


@dataclass(frozen=True)
class AVFSoftMaskV02:
    soft_penalty: float
    soft_penalty_reasons: tuple[str, ...]


@dataclass(frozen=True)
class AVFScoreExplanationV02:
    candidate_id: str
    source_drs_record_refs: tuple[str, ...]
    base_viability_score: float
    hard_mask_applied: bool
    hard_mask_value: int
    hard_mask_reasons: tuple[str, ...]
    soft_penalty: float
    soft_penalty_reasons: tuple[str, ...]
    final_avf_score: float
    rank: int | None = None
    root_review_required: bool = True
    why_score_is_not_permission: str = (
        "AVF score is advisory pressure only and is not action permission."
    )
    score_is_not_permission: bool = True
    top_ranked_candidate_not_permission: bool = True
    candidate_is_not_action: bool = True
    candidate_vector_is_not_final_output: bool = True
    hardmask_is_not_root: bool = True
    root_remains_final_authority: bool = True
    truth_claimed: bool = False
    authority_claimed: bool = False
    action_permission_claimed: bool = False
    final_output_claimed: bool = False


@dataclass(frozen=True)
class AVFDecisionReportV02:
    report_id: str
    candidate_id: str
    source_drs_record_refs: tuple[str, ...]
    hard_mask: AVFHardMaskV02
    soft_mask: AVFSoftMaskV02
    score_explanation: AVFScoreExplanationV02
    advisory_only: bool = True
    root_review_required: bool = True
    approved: bool = False
    execute: bool = False
    ready: bool = False
    payment_allowed: bool = False
    shipment_release_allowed: bool = False
    final_decision: bool = False
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class AVFEvaluationInputV02:
    evaluation_id: str
    candidates: tuple[AVFCandidateV02, ...]
    source_drs_report_ref: str | None = None
    source_drs_record_refs: tuple[str, ...] = ()
    resolver_mode: str = "deterministic_local"
    root_review_required: bool = True
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False


@dataclass(frozen=True)
class AVFRankedCandidateRowV02:
    candidate_id: str
    candidate_label: str
    rank: int
    base_viability_score: float
    hard_mask_value: int
    hard_mask_applied: bool
    hard_mask_reasons: tuple[str, ...]
    soft_penalty: float
    soft_penalty_reasons: tuple[str, ...]
    final_avf_score: float
    root_review_required: bool
    score_is_not_permission: bool = True
    top_ranked_candidate_not_permission: bool = True
    candidate_is_not_action: bool = True
    candidate_vector_is_not_final_output: bool = True


@dataclass(frozen=True)
class AVFEvaluationReportV02:
    report_id: str
    evaluation_id: str
    resolver_mode: str
    candidates_evaluated_count: int
    ranked_candidates: tuple[AVFRankedCandidateRowV02, ...]
    decision_reports: tuple[AVFDecisionReportV02, ...]
    hard_mask_table: tuple[dict[str, object], ...]
    soft_mask_table: tuple[dict[str, object], ...]
    score_explanation_table: tuple[dict[str, object], ...]
    top_candidate_id: str | None
    top_candidate_score: float | None
    hard_masked_count: int
    unmasked_count: int
    root_review_required_count: int
    advisory_only: bool = True
    top_ranked_candidate_not_permission: bool = True
    avf_score_is_not_authority: bool = True
    hardmask_is_not_root: bool = True
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False
    real_world_effects_count: int = 0


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _positive_pressure(value: float) -> float:
    return _clamp_01(float(value))


def _candidate_has_authority_claims(candidate: AVFCandidateV02) -> bool:
    return any(
        (
            candidate.truth_claimed,
            candidate.authority_claimed,
            candidate.action_permission_claimed,
            candidate.final_output_claimed,
        )
    )


def validate_avf_candidate_v02(
    candidate: AVFCandidateV02,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []

    if not _non_empty_string(candidate.candidate_id):
        _append_reason(reasons, REASON_CANDIDATE_ID_REQUIRED)
    if not _non_empty_string(candidate.candidate_label):
        _append_reason(reasons, REASON_CANDIDATE_LABEL_REQUIRED)
    if not 0.0 <= candidate.base_viability_score <= 1.0:
        _append_reason(reasons, REASON_BASE_VIABILITY_SCORE_OUT_OF_RANGE)
    if candidate.candidate_is_action:
        _append_reason(reasons, REASON_CANDIDATE_IS_NOT_ACTION)
    if candidate.candidate_is_final_output:
        _append_reason(reasons, REASON_CANDIDATE_VECTOR_NOT_FINAL_OUTPUT)
    if candidate.candidate_grants_permission:
        _append_reason(reasons, REASON_AVF_SCORE_NOT_PERMISSION)
    if candidate.truth_claimed:
        _append_reason(reasons, REASON_TRUTH_CLAIMED)
    if candidate.authority_claimed:
        _append_reason(reasons, REASON_AUTHORITY_CLAIMED)
    if candidate.action_permission_claimed:
        _append_reason(reasons, REASON_ACTION_PERMISSION_CLAIMED)
    if candidate.final_output_claimed:
        _append_reason(reasons, REASON_FINAL_OUTPUT_CLAIMED)
    if not candidate.time_envelope_present:
        _append_reason(reasons, REASON_MISSING_TIME_ENVELOPE)
    if not candidate.temporal_query_present:
        _append_reason(reasons, REASON_MISSING_TEMPORAL_QUERY)
    if not candidate.ttl_valid:
        _append_reason(reasons, REASON_INVALID_TTL)

    invalid_reasons = {
        REASON_CANDIDATE_ID_REQUIRED,
        REASON_CANDIDATE_LABEL_REQUIRED,
        REASON_BASE_VIABILITY_SCORE_OUT_OF_RANGE,
        REASON_CANDIDATE_IS_NOT_ACTION,
        REASON_CANDIDATE_VECTOR_NOT_FINAL_OUTPUT,
        REASON_AVF_SCORE_NOT_PERMISSION,
        REASON_TRUTH_CLAIMED,
        REASON_AUTHORITY_CLAIMED,
        REASON_ACTION_PERMISSION_CLAIMED,
        REASON_FINAL_OUTPUT_CLAIMED,
    }
    return not any(reason in invalid_reasons for reason in reasons), tuple(reasons)


def assert_no_authority_fields(candidate_or_report: object) -> tuple[bool, tuple[str, ...]]:
    checks = (
        ("truth_claimed", REASON_TRUTH_CLAIMED),
        ("authority_claimed", REASON_AUTHORITY_CLAIMED),
        ("action_permission_claimed", REASON_ACTION_PERMISSION_CLAIMED),
        ("final_output_claimed", REASON_FINAL_OUTPUT_CLAIMED),
        ("approved", REASON_APPROVED_NOT_ALLOWED),
        ("execute", REASON_EXECUTE_NOT_ALLOWED),
        ("ready", REASON_READY_NOT_ALLOWED),
        ("payment_allowed", REASON_PAYMENT_ALLOWED_NOT_ALLOWED),
        ("shipment_release_allowed", REASON_SHIPMENT_RELEASE_ALLOWED_NOT_ALLOWED),
        ("final_decision", REASON_FINAL_DECISION_NOT_ALLOWED),
    )
    reasons: list[str] = []
    for field_name, reason in checks:
        if getattr(candidate_or_report, field_name, False) is True:
            _append_reason(reasons, reason)
    return not reasons, tuple(reasons)


def build_hard_mask_v02(candidate: AVFCandidateV02) -> AVFHardMaskV02:
    reasons: list[str] = []

    if (
        candidate.candidate_id == CANDIDATE_RELEASE_ALL_AND_PAY_ALL
        or candidate.release_all_candidate
    ):
        _append_reason(reasons, REASON_RELEASE_ALL_AND_PAY_ALL_FORBIDDEN)
    if candidate.candidate_id == CANDIDATE_PAY_SUPPLIER_B or candidate.supplier_b_payment:
        _append_reason(reasons, REASON_SUPPLIER_B_PAYMENT_BLOCKED)
    if candidate.shipment_release_candidate:
        _append_reason(reasons, REASON_SHIPMENT_RELEASE_HELD)
    if candidate.old_receipt_as_permission:
        _append_reason(reasons, REASON_OLD_RECEIPT_NOT_PERMISSION)
    if candidate.old_root_final_as_current_decision:
        _append_reason(reasons, REASON_OLD_ROOT_FINAL_NOT_CURRENT_DECISION)
    if not candidate.time_envelope_present:
        _append_reason(reasons, REASON_MISSING_TIME_ENVELOPE)
    if not candidate.temporal_query_present:
        _append_reason(reasons, REASON_MISSING_TEMPORAL_QUERY)
    if not candidate.ttl_valid:
        _append_reason(reasons, REASON_INVALID_TTL)
    if candidate.quarantine_pressure > 0:
        _append_reason(reasons, REASON_QUARANTINE_PRESSURE_HARD_MASK)
    if candidate.deadend_pressure > 0:
        _append_reason(reasons, REASON_DEADEND_PRESSURE_HARD_MASK)
    if candidate.wrong_domain_pressure > 0:
        _append_reason(reasons, REASON_WRONG_DOMAIN_PRESSURE_HARD_MASK)
    if candidate.permission_trace_pressure > 0:
        _append_reason(reasons, REASON_PERMISSION_TRACE_PRESSURE_HARD_MASK)
    if candidate.candidate_is_action:
        _append_reason(reasons, REASON_ACTION_CANDIDATE_REQUIRES_ROOT_REVIEW)
        _append_reason(reasons, REASON_CANDIDATE_IS_NOT_ACTION)
    if candidate.candidate_grants_permission:
        _append_reason(reasons, REASON_AVF_SCORE_NOT_PERMISSION)
    if candidate.candidate_is_final_output or candidate.final_output_claimed:
        _append_reason(reasons, REASON_CANDIDATE_VECTOR_NOT_FINAL_OUTPUT)
    if candidate.action_permission_claimed:
        _append_reason(reasons, REASON_AVF_SCORE_NOT_PERMISSION)
    if _candidate_has_authority_claims(candidate):
        _append_reason(reasons, REASON_ROOT_REVIEW_REQUIRED)

    hard_mask_value = 0 if reasons else 1
    return AVFHardMaskV02(
        hard_mask_applied=hard_mask_value == 0,
        hard_mask_value=hard_mask_value,
        hard_mask_reasons=tuple(reasons),
    )


def build_soft_mask_v02(candidate: AVFCandidateV02) -> AVFSoftMaskV02:
    penalty = 0.0
    reasons: list[str] = []

    def add_pressure(value: float, reason: str) -> None:
        nonlocal penalty
        pressure = _positive_pressure(value)
        if pressure > 0:
            penalty += pressure
            _append_reason(reasons, reason)

    add_pressure(candidate.freshness_pressure, REASON_STALE_LEGAL_ACCOUNTING_EVIDENCE)
    add_pressure(candidate.staleness_penalty, REASON_STALE_LEGAL_ACCOUNTING_EVIDENCE)
    add_pressure(candidate.changed_fact_pressure, REASON_CHANGED_WAREHOUSE_FACT)
    if candidate.changed_fact_pressure > 0:
        _append_reason(reasons, REASON_RERUN_VALIDATION_PRESSURE)
    add_pressure(candidate.conflict_pressure, REASON_CONFLICT_PRESSURE)
    if candidate.conflict_pressure > 0:
        _append_reason(reasons, REASON_RERUN_VALIDATION_PRESSURE)
    add_pressure(
        candidate.duplicate_poisoning_pressure,
        REASON_DUPLICATE_POISONING_PRESSURE,
    )
    if candidate.supplier_b_payment or candidate.candidate_id == CANDIDATE_PAY_SUPPLIER_B:
        add_pressure(0.2, REASON_SUPPLIER_B_BLOCKER_PRESSURE)
    add_pressure(candidate.old_receipt_pressure, REASON_OLD_RECEIPT_PRESSURE)
    add_pressure(candidate.old_root_final_pressure, REASON_OLD_ROOT_FINAL_PRESSURE)
    add_pressure(
        candidate.source_provenance_weakness_pressure,
        REASON_SOURCE_PROVENANCE_WEAKNESS,
    )
    add_pressure(candidate.uncertainty_pressure, REASON_UNCERTAINTY_PRESSURE)

    return AVFSoftMaskV02(
        soft_penalty=_clamp_01(penalty),
        soft_penalty_reasons=tuple(reasons),
    )


def build_score_explanation_v02(
    candidate: AVFCandidateV02,
    *,
    rank: int | None = None,
) -> AVFScoreExplanationV02:
    hard_mask = build_hard_mask_v02(candidate)
    soft_mask = build_soft_mask_v02(candidate)
    if hard_mask.hard_mask_value == 0:
        final_score = 0.0
    else:
        final_score = _clamp_01(
            max(0.0, candidate.base_viability_score - soft_mask.soft_penalty)
        )

    return AVFScoreExplanationV02(
        candidate_id=candidate.candidate_id,
        source_drs_record_refs=candidate.source_drs_record_refs,
        base_viability_score=candidate.base_viability_score,
        hard_mask_applied=hard_mask.hard_mask_applied,
        hard_mask_value=hard_mask.hard_mask_value,
        hard_mask_reasons=hard_mask.hard_mask_reasons,
        soft_penalty=soft_mask.soft_penalty,
        soft_penalty_reasons=soft_mask.soft_penalty_reasons,
        final_avf_score=final_score,
        rank=rank,
        root_review_required=True,
        truth_claimed=False,
        authority_claimed=False,
        action_permission_claimed=False,
        final_output_claimed=False,
    )


def build_avf_decision_report_v02(
    candidate: AVFCandidateV02,
    *,
    report_id: str | None = None,
    rank: int | None = None,
) -> AVFDecisionReportV02:
    hard_mask = build_hard_mask_v02(candidate)
    soft_mask = build_soft_mask_v02(candidate)
    explanation = build_score_explanation_v02(candidate, rank=rank)
    return AVFDecisionReportV02(
        report_id=report_id or f"avf_v0_2:{candidate.candidate_id}",
        candidate_id=candidate.candidate_id,
        source_drs_record_refs=candidate.source_drs_record_refs,
        hard_mask=hard_mask,
        soft_mask=soft_mask,
        score_explanation=explanation,
        advisory_only=True,
        root_review_required=True,
        approved=False,
        execute=False,
        ready=False,
        payment_allowed=False,
        shipment_release_allowed=False,
        final_decision=False,
        production_ready_claimed=False,
        public_auditor_ready_claimed=False,
        real_world_effects_count=0,
    )


def validate_score_explanation_v02(
    explanation: AVFScoreExplanationV02,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not 0.0 <= explanation.final_avf_score <= 1.0:
        _append_reason(reasons, REASON_FINAL_SCORE_OUT_OF_RANGE)
    if explanation.hard_mask_value == 0 and explanation.final_avf_score != 0.0:
        _append_reason(reasons, REASON_HARD_MASK_SCORE_MUST_BE_ZERO)
    if not explanation.score_is_not_permission:
        _append_reason(reasons, REASON_AVF_SCORE_NOT_PERMISSION)
    if not explanation.candidate_is_not_action:
        _append_reason(reasons, REASON_CANDIDATE_IS_NOT_ACTION)
    if not explanation.candidate_vector_is_not_final_output:
        _append_reason(reasons, REASON_CANDIDATE_VECTOR_NOT_FINAL_OUTPUT)
    if not explanation.hardmask_is_not_root:
        _append_reason(reasons, REASON_HARDMASK_IS_NOT_ROOT)
    if not explanation.root_remains_final_authority:
        _append_reason(reasons, REASON_ROOT_REMAINS_FINAL_AUTHORITY)
    authority_ok, authority_reasons = assert_no_authority_fields(explanation)
    for reason in authority_reasons:
        _append_reason(reasons, reason)
    return authority_ok and not reasons, tuple(reasons)


def build_wow_v1_2_avf_v02_candidate_fixtures() -> tuple[AVFCandidateV02, ...]:
    return (
        AVFCandidateV02(
            candidate_id=CANDIDATE_RELEASE_ALL_AND_PAY_ALL,
            candidate_label="Release all and pay all",
            candidate_direction="Unsafe all-clear route.",
            base_viability_score=0.95,
            release_all_candidate=True,
            shipment_release_candidate=True,
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_PAY_SUPPLIER_A_ONLY,
            candidate_label="Pay Supplier A only",
            candidate_direction="Supplier A scoped payment candidate direction.",
            base_viability_score=0.55,
            source_drs_record_refs=("supplier_a_prior_scoped_trace",),
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_PAY_SUPPLIER_B,
            candidate_label="Pay Supplier B",
            candidate_direction="Supplier B payment candidate direction.",
            base_viability_score=0.8,
            source_drs_record_refs=("supplier_b_blocker_trace",),
            supplier_b_payment=True,
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_PREPARE_SUPPLIER_A_PAYMENT_FORM_ONLY,
            candidate_label="Prepare Supplier A payment form only",
            candidate_direction="Prepare a bounded form for later Root review.",
            base_viability_score=0.8,
            source_drs_record_refs=("supplier_a_prior_scoped_trace",),
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_REQUEST_FRESH_WAREHOUSE_VALIDATION,
            candidate_label="Request fresh warehouse validation",
            candidate_direction="Refresh warehouse evidence before any route.",
            base_viability_score=0.72,
            source_drs_record_refs=("changed_warehouse_fact",),
            changed_fact_pressure=0.2,
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_REQUEST_FRESH_LEGAL_ACCOUNTING_VALIDATION,
            candidate_label="Request fresh legal/accounting validation",
            candidate_direction="Refresh stale legal/accounting evidence.",
            base_viability_score=0.7,
            source_drs_record_refs=("stale_legal_accounting_evidence",),
            staleness_penalty=0.2,
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_KEEP_SHIPMENT_HELD,
            candidate_label="Keep shipment held",
            candidate_direction="Preserve held shipment boundary.",
            base_viability_score=0.82,
            source_drs_record_refs=("old_shipment_held_trace",),
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_ROOT_REVIEW_ONLY,
            candidate_label="Root review only",
            candidate_direction="Return all candidate pressure to Root.",
            base_viability_score=0.75,
        ),
        AVFCandidateV02(
            candidate_id=CANDIDATE_BLOCK_SUPPLIER_B_AND_HOLD_SHIPMENT,
            candidate_label="Block Supplier B and hold shipment",
            candidate_direction="Maintain Supplier B block and shipment hold.",
            base_viability_score=0.85,
            source_drs_record_refs=("supplier_b_blocker_trace",),
        ),
    )


def _ranked_row_from_report(
    candidate: AVFCandidateV02,
    report: AVFDecisionReportV02,
    rank: int,
) -> AVFRankedCandidateRowV02:
    explanation = report.score_explanation
    return AVFRankedCandidateRowV02(
        candidate_id=candidate.candidate_id,
        candidate_label=candidate.candidate_label,
        rank=rank,
        base_viability_score=explanation.base_viability_score,
        hard_mask_value=explanation.hard_mask_value,
        hard_mask_applied=explanation.hard_mask_applied,
        hard_mask_reasons=explanation.hard_mask_reasons,
        soft_penalty=explanation.soft_penalty,
        soft_penalty_reasons=explanation.soft_penalty_reasons,
        final_avf_score=explanation.final_avf_score,
        root_review_required=True,
        score_is_not_permission=True,
        top_ranked_candidate_not_permission=True,
        candidate_is_not_action=True,
        candidate_vector_is_not_final_output=True,
    )


def _hard_mask_table_row(report: AVFDecisionReportV02) -> dict[str, object]:
    return {
        "candidate_id": report.candidate_id,
        "hard_mask_value": report.hard_mask.hard_mask_value,
        "hard_mask_applied": report.hard_mask.hard_mask_applied,
        "hard_mask_reasons": report.hard_mask.hard_mask_reasons,
    }


def _soft_mask_table_row(report: AVFDecisionReportV02) -> dict[str, object]:
    return {
        "candidate_id": report.candidate_id,
        "soft_penalty": report.soft_mask.soft_penalty,
        "soft_penalty_reasons": report.soft_mask.soft_penalty_reasons,
    }


def _score_explanation_table_row(report: AVFDecisionReportV02) -> dict[str, object]:
    explanation = report.score_explanation
    return {
        "candidate_id": report.candidate_id,
        "rank": explanation.rank,
        "base_viability_score": explanation.base_viability_score,
        "final_avf_score": explanation.final_avf_score,
        "score_is_not_permission": explanation.score_is_not_permission,
        "top_ranked_candidate_not_permission": (
            explanation.top_ranked_candidate_not_permission
        ),
        "candidate_is_not_action": explanation.candidate_is_not_action,
        "candidate_vector_is_not_final_output": (
            explanation.candidate_vector_is_not_final_output
        ),
        "root_review_required": explanation.root_review_required,
    }


def evaluate_avf_candidates_v02(
    input: AVFEvaluationInputV02,
) -> AVFEvaluationReportV02:
    initial_reports = tuple(
        build_avf_decision_report_v02(candidate)
        for candidate in input.candidates
    )
    indexed = tuple(zip(range(len(input.candidates)), input.candidates, initial_reports))
    ranked = sorted(
        indexed,
        key=lambda item: (
            item[2].score_explanation.final_avf_score,
            -item[0],
        ),
        reverse=True,
    )

    ranked_rows: list[AVFRankedCandidateRowV02] = []
    ranked_reports: list[AVFDecisionReportV02] = []
    for rank, (_index, candidate, _report) in enumerate(ranked, start=1):
        ranked_report = build_avf_decision_report_v02(candidate, rank=rank)
        ranked_reports.append(ranked_report)
        ranked_rows.append(_ranked_row_from_report(candidate, ranked_report, rank))

    hard_mask_table = tuple(_hard_mask_table_row(report) for report in ranked_reports)
    soft_mask_table = tuple(_soft_mask_table_row(report) for report in ranked_reports)
    score_table = tuple(_score_explanation_table_row(report) for report in ranked_reports)

    top_row = ranked_rows[0] if ranked_rows else None
    hard_masked_count = sum(1 for row in ranked_rows if row.hard_mask_value == 0)
    root_review_required_count = sum(
        1 for row in ranked_rows
        if row.root_review_required
    )

    return AVFEvaluationReportV02(
        report_id=f"avf_v0_2_evaluation:{input.evaluation_id}",
        evaluation_id=input.evaluation_id,
        resolver_mode=input.resolver_mode,
        candidates_evaluated_count=len(input.candidates),
        ranked_candidates=tuple(ranked_rows),
        decision_reports=tuple(ranked_reports),
        hard_mask_table=hard_mask_table,
        soft_mask_table=soft_mask_table,
        score_explanation_table=score_table,
        top_candidate_id=top_row.candidate_id if top_row else None,
        top_candidate_score=top_row.final_avf_score if top_row else None,
        hard_masked_count=hard_masked_count,
        unmasked_count=len(ranked_rows) - hard_masked_count,
        root_review_required_count=root_review_required_count,
        advisory_only=True,
        top_ranked_candidate_not_permission=True,
        avf_score_is_not_authority=True,
        hardmask_is_not_root=True,
        production_ready_claimed=False,
        public_auditor_ready_claimed=False,
        real_world_effects_count=0,
    )


def build_wow_v1_2_avf_v02_evaluation_input() -> AVFEvaluationInputV02:
    return AVFEvaluationInputV02(
        evaluation_id="avf_v0_2_full_wow_v1_2_local_evaluation",
        candidates=build_wow_v1_2_avf_v02_candidate_fixtures(),
        source_drs_report_ref="local_drs_v0_2_reuse_decision_report",
        source_drs_record_refs=(
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
        ),
        resolver_mode="deterministic_local",
        root_review_required=True,
        production_ready_claimed=False,
        public_auditor_ready_claimed=False,
    )
