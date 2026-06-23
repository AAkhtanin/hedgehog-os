from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from hedgehog.avf import score_candidate_vector as _score_avf_candidate_vector
from hedgehog.candidate_vector_generator import CandidateVectorReport
from hedgehog.gt_validator import (
    classify_vv_report,
    compute_payoff_components,
    validate_gt,
)


POST_VV_FORBIDDEN_KEYS = ("answer", "final_output", "raw_user_text")


ADVISORY_DECISIONS = {
    "accept_candidate",
    "degrade_candidate",
    "reject_candidate",
    "needs_review",
    "no_update",
}

DECISION_VOCABULARY_MAPPING = {
    "accept_candidate": "advisory accept only, not Root Final",
    "degrade_candidate": "existing revise / needs_user style semantics",
    "reject_candidate": "candidate route block, not Root Final rejection",
    "needs_review": "Root review required",
    "no_update": "advisory no_update only, not final rejection",
}


@dataclass(frozen=True)
class AdvisoryEvaluationInput:
    candidate_vector_report_id: str
    drs_candidate_refs: tuple[str, ...]
    avf_score_refs: tuple[str, ...]
    ranked_candidate_ids: tuple[str, ...]
    reason_codes: tuple[str, ...] = ()
    conflict_flags: tuple[str, ...] = ()
    stale_flags: tuple[str, ...] = ()
    quarantine_deadend_flags: tuple[str, ...] = ()
    poisoning_flags: tuple[str, ...] = ()
    provenance_refs: tuple[dict[str, Any], ...] = ()
    trace_refs: tuple[dict[str, Any], ...] = ()
    source_refs: tuple[dict[str, Any], ...] = ()
    root_review_required: bool = True
    direct_reuse_allowed: bool = False
    candidate_count: int = 0
    high_score_candidate_ids: tuple[str, ...] = ()
    schema_valid_candidate_ids: tuple[str, ...] = ()
    top_score: float = 0.0

    def __post_init__(self) -> None:
        if self.direct_reuse_allowed:
            raise ValueError("AdvisoryEvaluationInput requires direct_reuse_allowed false")

    @classmethod
    def from_candidate_report(
        cls,
        report: CandidateVectorReport,
        *,
        report_id: str | None = None,
    ) -> "AdvisoryEvaluationInput":
        return cls(
            candidate_vector_report_id=report_id or _report_id(report),
            drs_candidate_refs=tuple(
                candidate.source_input.source_record_id for candidate in report.candidates
            ),
            avf_score_refs=tuple(score.vector_id for score in report.ranked_candidates),
            ranked_candidate_ids=tuple(
                score.candidate_id for score in report.ranked_candidates
            ),
            reason_codes=tuple(report.reason_codes),
            conflict_flags=_collect_flags(report, "conflict"),
            stale_flags=_collect_flags(report, "stale"),
            quarantine_deadend_flags=_collect_flags(report, "quarantine_deadend"),
            poisoning_flags=_collect_flags(report, "poisoning"),
            provenance_refs=_collect_dict_refs(report, "provenance_refs"),
            trace_refs=_collect_dict_refs(report, "trace_refs"),
            source_refs=_collect_dict_refs(report, "source_refs"),
            root_review_required=report.root_review_required,
            direct_reuse_allowed=False,
            candidate_count=len(report.candidates),
            high_score_candidate_ids=tuple(
                score.candidate_id
                for score in report.ranked_candidates
                if score.score >= 0.75
            ),
            schema_valid_candidate_ids=tuple(
                candidate.candidate_id
                for candidate in report.candidates
                if candidate.source_input.schema_valid
            ),
            top_score=report.ranked_candidates[0].score
            if report.ranked_candidates
            else 0.0,
        )


@dataclass(frozen=True)
class AdvisorySignal:
    signal_id: str
    signal_kind: str
    advisory_decision: str
    confidence: float
    reason_codes: tuple[str, ...] = ()
    authority_claimed: bool = False
    truth_claimed: bool = False
    action_permission_claimed: bool = False
    final_output_claimed: bool = False
    direct_reuse_allowed: bool = False
    root_review_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.advisory_decision not in ADVISORY_DECISIONS:
            raise ValueError(f"unknown advisory decision: {self.advisory_decision}")
        unsafe = (
            self.authority_claimed,
            self.truth_claimed,
            self.action_permission_claimed,
            self.final_output_claimed,
            self.direct_reuse_allowed,
        )
        if any(unsafe):
            raise ValueError("AdvisorySignal cannot claim authority, truth, output, or reuse")
        if not self.root_review_required:
            raise ValueError("AdvisorySignal requires Root review")


@dataclass(frozen=True)
class GTLGTAdvisoryReport:
    report_id: str
    candidate_count: int
    signals: tuple[AdvisorySignal, ...]
    recommended_review_route: str
    root_review_required: bool = True
    direct_reuse_allowed_count: int = 0
    action_permission_granted_count: int = 0
    final_output_created_count: int = 0
    root_final_authority_preserved: bool = True
    counters: dict[str, int] = field(default_factory=dict)
    reason_codes: tuple[str, ...] = ()


def _report_id(report: CandidateVectorReport) -> str:
    first = report.ranked_candidates[0].candidate_id if report.ranked_candidates else "empty"
    return f"candidate_vector_report:{first}:{len(report.ranked_candidates)}"


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[str] = set()
    ordered: list[Any] = []
    for item in items:
        key = repr(item)
        if key not in seen:
            seen.add(key)
            ordered.append(item)
    return tuple(ordered)


def _collect_dict_refs(report: CandidateVectorReport, attr: str) -> tuple[dict[str, Any], ...]:
    refs: list[dict[str, Any]] = []
    for candidate in report.candidates:
        refs.extend(dict(ref) for ref in getattr(candidate.source_input, attr))
    return _dedupe(refs)


def _collect_flags(report: CandidateVectorReport, kind: str) -> tuple[str, ...]:
    flags: list[str] = []
    for candidate in report.candidates:
        if kind == "conflict":
            flags.extend(candidate.source_input.conflict_flags)
        elif kind == "quarantine_deadend":
            flags.extend(candidate.source_input.quarantine_deadend_flags)
        elif kind == "poisoning":
            flags.extend(candidate.source_input.poisoning_flags)
    for score in report.ranked_candidates:
        if kind == "stale" and score.penalties.get("stale_penalty", 0.0) > 0:
            flags.append("stale_candidate")
        elif kind == "conflict" and score.penalties.get("conflict_penalty", 0.0) > 0:
            flags.append("conflicting_provenance")
        elif (
            kind == "quarantine_deadend"
            and score.penalties.get("quarantine_deadend_penalty", 0.0) > 0
        ):
            flags.append("quarantine_deadend")
        elif (
            kind == "poisoning"
            and score.penalties.get("poisoning_pressure_penalty", 0.0) > 0
        ):
            flags.append("poisoning_pressure")
    return tuple(str(flag) for flag in _dedupe(flags))


def _input_has_blocking_pressure(advisory_input: AdvisoryEvaluationInput) -> bool:
    return bool(
        advisory_input.conflict_flags
        or advisory_input.quarantine_deadend_flags
        or advisory_input.poisoning_flags
        or advisory_input.stale_flags
    )


def _vv_decision_for_input(advisory_input: AdvisoryEvaluationInput) -> str:
    if not advisory_input.ranked_candidate_ids:
        return "reject"
    if advisory_input.conflict_flags or advisory_input.quarantine_deadend_flags:
        return "reject"
    if advisory_input.stale_flags or advisory_input.poisoning_flags:
        return "revise"
    return "accept"


def _vv_reports_from_candidate_report(
    advisory_input: AdvisoryEvaluationInput,
    candidate_report: CandidateVectorReport | None,
) -> list[dict[str, Any]]:
    if not candidate_report or not candidate_report.ranked_candidates:
        return []
    vv_decision = _vv_decision_for_input(advisory_input)
    status = {
        "accept": "accepted",
        "revise": "needs_revision",
        "reject": "rejected",
    }[vv_decision]
    raw_avf_by_candidate = {
        candidate.candidate_id: _score_avf_candidate_vector(candidate.vector)
        for candidate in candidate_report.candidates
    }
    reports: list[dict[str, Any]] = []
    for index, score in enumerate(candidate_report.ranked_candidates):
        raw_avf = raw_avf_by_candidate.get(score.candidate_id, {})
        policy = 0.0 if score.hard_blocks or advisory_input.conflict_flags else 1.0
        time_score = 0.0 if score.penalties.get("stale_penalty", 0.0) else 1.0
        safety = 0.0 if score.hard_blocks else 1.0
        evidence = min(1.0, max(0.0, score.score))
        report = {
            "vv_report_id": f"vv:gt_lgt_advisory:{index}",
            "proposal_id": score.candidate_id,
            "status": status,
            "scores": {
                "schema": 1.0,
                "evidence": evidence,
                "policy": policy,
                "time": time_score,
                "safety": safety,
                "consistency": 0.0 if advisory_input.conflict_flags else 1.0,
            },
            "overall_score": evidence,
            "decision": vv_decision,
            "checked_at": "2026-06-22T12:00:00+00:00",
            "vector_id": score.vector_id,
            "artifact_type": "candidate_vector_advisory_input",
            "execution_status": "review_required",
            "normalized_features": {
                "utility": evidence,
                "robustness": safety,
                "compute_cost": 0.0,
                "violations": 0.0 if policy and safety else 1.0,
                "transfer": 0.0,
                "novelty_guard": 0.0,
                "avf_final_viability": raw_avf.get("final_viability", score.score),
                "avf_soft_mask": raw_avf.get(
                    "soft_mask",
                    score.score_components.get("avf_soft_mask"),
                ),
            },
            "violations": [
                {
                    "violation_id": f"advisory:{reason}",
                    "kind": "safety" if "quarantine" in reason else "consistency",
                    "description": reason,
                }
                for reason in (
                    *advisory_input.conflict_flags,
                    *advisory_input.quarantine_deadend_flags,
                    *advisory_input.stale_flags,
                    *advisory_input.poisoning_flags,
                )
            ],
            "notes": [
                "candidate_vector_report_input_only",
                "gt_lgt_advisory_mapping_only",
            ],
        }
        reports.append(report)
    return reports


def _gt_metadata(
    advisory_input: AdvisoryEvaluationInput,
    candidate_report: CandidateVectorReport | None,
) -> dict[str, Any]:
    vv_reports = _vv_reports_from_candidate_report(advisory_input, candidate_report)
    gt_report = validate_gt(vv_reports) if vv_reports else validate_gt([])
    candidate_scores = [
        compute_payoff_components(report)
        for report in vv_reports
        if classify_vv_report(report) in {"accepted_completed", "needs_revision"}
    ]
    return {
        "source_gt_decision": gt_report["decision"],
        "source_gt_report_id": gt_report["gt_report_id"],
        "source_candidate_scores_count": len(candidate_scores),
        "post_vv_forbidden_keys_screened": POST_VV_FORBIDDEN_KEYS,
    }


def evaluate_gt_signal(
    advisory_input: AdvisoryEvaluationInput,
    candidate_report: CandidateVectorReport | None = None,
) -> AdvisorySignal:
    metadata = _gt_metadata(advisory_input, candidate_report)
    reasons = [
        *advisory_input.reason_codes,
        "gt_signal_advisory_only",
        "root_review_required",
        "root_final_authority_preserved_across_gt_lgt_advisory",
    ]
    if not advisory_input.ranked_candidate_ids:
        decision = "no_update"
        reasons.extend(("no_ranked_candidates", "advisory_no_update_only"))
    elif advisory_input.conflict_flags:
        decision = "reject_candidate"
        reasons.extend(
            (
                "conflicting_provenance_blocks_advisory_accept",
                "conflicting_provenance_blocks_accept",
                "conflict_review_required",
                "gt_reject_signal_blocks_candidate_not_root_final",
            )
        )
    elif advisory_input.quarantine_deadend_flags:
        decision = "reject_candidate"
        reasons.extend(
            (
                "quarantine_deadend_overrides_high_score_to_review",
                "quarantine_deadend_overrides_score",
                "direct_reuse_permission_blocked",
                "gt_reject_signal_blocks_candidate_not_root_final",
            )
        )
    elif advisory_input.stale_flags:
        decision = "degrade_candidate"
        reasons.extend(
            (
                "stale_high_score_candidate_cannot_silent_accept",
                "stale_high_score_review_required",
                "silent_accept_blocked",
                "gt_degrade_signal_routes_to_review_not_final",
            )
        )
    elif advisory_input.poisoning_flags:
        decision = "needs_review"
        reasons.extend(
            (
                "duplicate_spam_cannot_force_gt_lgt_accept",
                "duplicate_spam_cannot_force_accept",
                "poisoning_review_pressure_only",
            )
        )
    elif advisory_input.top_score >= 0.75:
        decision = "accept_candidate"
        reasons.extend(
            (
                "gt_accept_signal_requires_root_final_review",
                "gt_accept_advisory_only",
                "root_final_review_required",
            )
        )
    else:
        decision = "needs_review"
        reasons.append("ranked_candidate_requires_review")
    if decision == "reject_candidate":
        reasons.extend(("gt_reject_blocks_candidate_only", "root_remains_required"))
    if decision == "degrade_candidate":
        reasons.extend(("gt_degrade_routes_to_review", "final_output_not_created"))
    return AdvisorySignal(
        signal_id=f"signal:gt:{advisory_input.candidate_vector_report_id}",
        signal_kind="gt",
        advisory_decision=decision,
        confidence=round(min(1.0, max(0.0, advisory_input.top_score)), 6),
        reason_codes=tuple(dict.fromkeys(reasons)),
        authority_claimed=False,
        truth_claimed=False,
        action_permission_claimed=False,
        final_output_claimed=False,
        direct_reuse_allowed=False,
        root_review_required=True,
        metadata=metadata,
    )


def evaluate_lgt_signal(
    advisory_input: AdvisoryEvaluationInput,
    *,
    lgt_status: str = "deferred",
) -> AdvisorySignal:
    signal_kind = "lgt_placeholder" if lgt_status == "placeholder" else "lgt_deferred"
    return AdvisorySignal(
        signal_id=f"signal:{signal_kind}:{advisory_input.candidate_vector_report_id}",
        signal_kind=signal_kind,
        advisory_decision="no_update",
        confidence=0.0,
        reason_codes=(
            "lgt_absent_or_local_signal_remains_advisory",
            "lgt_status_deferred",
            "lgt_deferred_not_authority",
            "root_review_required",
        ),
        authority_claimed=False,
        truth_claimed=False,
        action_permission_claimed=False,
        final_output_claimed=False,
        direct_reuse_allowed=False,
        root_review_required=True,
        metadata={
            "concrete_lgt_runtime_module": "absent",
            "concrete_lgt_schema": "absent",
            "concrete_lgt_tests_or_demos": "absent",
            "lgt_status": lgt_status,
        },
    )


def _recommended_review_route(gt_signal: AdvisorySignal) -> str:
    return {
        "accept_candidate": "root_final_review_required",
        "degrade_candidate": "root_degrade_review_required",
        "reject_candidate": "root_block_or_review_required",
        "needs_review": "root_review_required",
        "no_update": "root_review_no_update",
    }[gt_signal.advisory_decision]


def _report_counters(
    advisory_input: AdvisoryEvaluationInput,
    signals: tuple[AdvisorySignal, ...],
) -> dict[str, int]:
    gt_signal = next(signal for signal in signals if signal.signal_kind == "gt")
    lgt_signals = tuple(
        signal for signal in signals if signal.signal_kind.startswith("lgt_")
    )
    blocking_pressure = _input_has_blocking_pressure(advisory_input)
    return {
        "advisory_inputs_count": 1,
        "gt_signals_emitted_count": 1,
        "lgt_signals_emitted_count": len(lgt_signals),
        "lgt_deferred_count": sum(
            1 for signal in lgt_signals if signal.signal_kind == "lgt_deferred"
        ),
        "advisory_reports_created_count": 1,
        "advisory_accept_count": sum(
            1 for signal in signals if signal.advisory_decision == "accept_candidate"
        ),
        "advisory_degrade_count": sum(
            1 for signal in signals if signal.advisory_decision == "degrade_candidate"
        ),
        "advisory_reject_count": sum(
            1 for signal in signals if signal.advisory_decision == "reject_candidate"
        ),
        "advisory_needs_review_count": sum(
            1 for signal in signals if signal.advisory_decision == "needs_review"
        ),
        "direct_reuse_allowed_count": 0,
        "action_permission_granted_count": 0,
        "final_output_created_count": 0,
        "gt_authority_claimed_count": int(gt_signal.authority_claimed),
        "lgt_authority_claimed_count": sum(
            int(signal.authority_claimed) for signal in lgt_signals
        ),
        "advisory_truth_claimed_count": sum(
            int(signal.truth_claimed) for signal in signals
        ),
        "advisory_accept_as_root_final_count": 0,
        "high_score_forced_accept_count": int(
            bool(advisory_input.high_score_candidate_ids)
            and blocking_pressure
            and gt_signal.advisory_decision == "accept_candidate"
        ),
        "duplicate_spam_forced_accept_count": int(
            bool(advisory_input.poisoning_flags)
            and gt_signal.advisory_decision == "accept_candidate"
        ),
        "stale_silent_accept_count": int(
            bool(advisory_input.stale_flags)
            and gt_signal.advisory_decision == "accept_candidate"
        ),
        "quarantine_deadend_override_count": int(
            bool(advisory_input.quarantine_deadend_flags)
            and gt_signal.advisory_decision == "accept_candidate"
        ),
        "conflicting_provenance_hidden_count": int(
            bool(advisory_input.conflict_flags)
            and gt_signal.advisory_decision == "accept_candidate"
        ),
        "manifest_mutation_count": 0,
        "transition_matrix_mutation_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "root_review_required_count": 1,
        "root_final_authority_preserved_count": 1,
    }


def build_advisory_report(
    advisory_input: AdvisoryEvaluationInput,
    *,
    candidate_report: CandidateVectorReport | None = None,
    lgt_status: str = "deferred",
) -> GTLGTAdvisoryReport:
    gt_signal = evaluate_gt_signal(advisory_input, candidate_report)
    lgt_signal = evaluate_lgt_signal(advisory_input, lgt_status=lgt_status)
    signals = (gt_signal, lgt_signal)
    counters = _report_counters(advisory_input, signals)
    reason_codes = tuple(
        dict.fromkeys(reason for signal in signals for reason in signal.reason_codes)
    )
    return GTLGTAdvisoryReport(
        report_id=f"gt_lgt_advisory:{advisory_input.candidate_vector_report_id}",
        candidate_count=advisory_input.candidate_count,
        signals=signals,
        recommended_review_route=_recommended_review_route(gt_signal),
        root_review_required=True,
        direct_reuse_allowed_count=0,
        action_permission_granted_count=0,
        final_output_created_count=0,
        root_final_authority_preserved=True,
        counters=counters,
        reason_codes=reason_codes,
    )


def evaluate_candidate_report(
    candidate_report: CandidateVectorReport,
    *,
    report_id: str | None = None,
    lgt_status: str = "deferred",
) -> GTLGTAdvisoryReport:
    advisory_input = AdvisoryEvaluationInput.from_candidate_report(
        candidate_report,
        report_id=report_id,
    )
    return build_advisory_report(
        advisory_input,
        candidate_report=candidate_report,
        lgt_status=lgt_status,
    )
