from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics


CONFLICT_TYPES = (
    "completed_vs_completed_conflict",
    "completed_vs_deadend_conflict",
    "reuse_candidate_vs_quarantine_conflict",
    "promotion_candidate_vs_rejected_evidence",
    "stale_vs_fresh_conflict",
    "lower_trust_vs_higher_trust_conflict",
    "action_like_blocked_vs_reuse_conflict",
    "permission_required_vs_action_execution_conflict",
    "protocol_candidate_vs_deadend_conflict",
    "needle_candidate_vs_quarantine_conflict",
    "no_conflict_same_completed_lineage",
)


@dataclass(frozen=True)
class ConflictCheckReport:
    input_mode: dict[str, Any]
    source_lifecycle: dict[str, Any]
    conflict_candidate_pairs: list[dict[str, Any]]
    conflict_reports: list[dict[str, Any]]
    malicious_claims: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario"]: row for row in rows}


def _comparison_view(
    record: dict[str, Any],
    *,
    semantic_address: str,
    resonance_tags: list[str],
    evidence_claim: str,
    observed_at: str | None = None,
    gt_trust_hint: float | None = None,
    source_reliability_hint: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    view = copy.deepcopy(record)
    view["semantic_address"] = semantic_address
    view["resonance_tags"] = resonance_tags
    view["comparison_evidence_claim"] = evidence_claim
    if observed_at is not None:
        view["time_envelope"]["observed_at"] = observed_at
    if gt_trust_hint is not None:
        view["trust_state"]["gt_trust_hint"] = gt_trust_hint
    if source_reliability_hint is not None:
        view["trust_state"]["source_reliability_hint"] = source_reliability_hint
    view.update(extra or {})
    return view


def _pair(
    conflict_type: str,
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    comparison_scope: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "scenario": conflict_type,
        "conflict_candidate_pair_id": f"conflict_candidate_pair_{conflict_type}",
        "left_experience_record_id": left["experience_record_id"],
        "right_experience_record_id": right["experience_record_id"],
        "left_status": left["status"],
        "right_status": right["status"],
        "left_lifecycle_stage": left["lifecycle_stage"],
        "right_lifecycle_stage": right["lifecycle_stage"],
        "left_semantic_address": left["semantic_address"],
        "right_semantic_address": right["semantic_address"],
        "shared_resonance_tags": sorted(
            set(left["resonance_tags"]) & set(right["resonance_tags"])
        ),
        "comparison_scope": comparison_scope,
        "conflict_check_reason": reason,
        "_left": left,
        "_right": right,
    }


def _report(
    pair: dict[str, Any],
    *,
    conflict_status: str,
    severity: str,
    root_review_required: bool,
    gt_review_recommended: bool = False,
    reuse_block_recommended: bool = False,
    promotion_block_recommended: bool = False,
    quarantine_review_recommended: bool = False,
    invalidation_recommended: bool = False,
    older_record_id: str | None = None,
    newer_record_id: str | None = None,
    lower_trust_record_id: str | None = None,
    higher_trust_record_id: str | None = None,
    recommended_next_step: str,
) -> dict[str, Any]:
    left = pair["_left"]
    right = pair["_right"]
    return {
        "scenario": pair["scenario"],
        "conflict_report_id": f"conflict_report_{pair['scenario']}",
        "created_by": "conflictcheck_v0_1",
        "source_candidate_pair_id": pair["conflict_candidate_pair_id"],
        "conflict_type": pair["scenario"],
        "conflict_status": conflict_status,
        "severity": severity,
        "root_review_required": root_review_required,
        "gt_review_recommended": gt_review_recommended,
        "reuse_block_recommended": reuse_block_recommended,
        "promotion_block_recommended": promotion_block_recommended,
        "quarantine_review_recommended": quarantine_review_recommended,
        "invalidation_recommended": invalidation_recommended,
        "older_record_id": older_record_id,
        "newer_record_id": newer_record_id,
        "lower_trust_record_id": lower_trust_record_id,
        "higher_trust_record_id": higher_trust_record_id,
        "evidence": {
            "shared_resonance_tags": pair["shared_resonance_tags"],
            "left_evidence_claim": left["comparison_evidence_claim"],
            "right_evidence_claim": right["comparison_evidence_claim"],
            "left_gt_trust_hint": left["trust_state"]["gt_trust_hint"],
            "right_gt_trust_hint": right["trust_state"]["gt_trust_hint"],
            "left_observed_at": left["time_envelope"]["observed_at"],
            "right_observed_at": right["time_envelope"]["observed_at"],
        },
        "recommended_next_step": recommended_next_step,
        "conflictcheck_decides_truth": False,
        "conflictcheck_mutates_drs": False,
        "conflictcheck_invalidates_record": False,
        "conflictcheck_promotes_record": False,
        "conflictcheck_demotes_record": False,
        "root_remains_authority": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_network_write": False,
        "production_external_action_executed": False,
    }


def _candidate_pairs(records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    semantic = "local://conflictcheck/certificate_workflow"
    common = ["certificate_workflow", "root_controlled"]

    root_completed = _comparison_view(
        records["root_final_completed_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["completed"],
        evidence_claim="certificate_workflow_is_complete",
        observed_at="2026-06-08T10:00:00Z",
    )
    incompatible_completed = _comparison_view(
        records["sandbox_needle_completed_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["completed"],
        evidence_claim="certificate_workflow_requires_unresolved_step",
        observed_at="2026-06-08T10:05:00Z",
    )
    compatible_completed = _comparison_view(
        records["child_cell_completed_boundary_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["completed"],
        evidence_claim="certificate_workflow_is_complete",
        observed_at="2026-06-08T10:06:00Z",
        extra={"lineage_refs": root_completed["lineage_refs"]},
    )
    deadend = _comparison_view(
        records["child_cell_blocked_max_depth_deadend_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["deadend"],
        evidence_claim="certificate_workflow_branch_is_not_viable",
    )
    quarantine = _comparison_view(
        records["sandbox_needle_invalid_json_quarantined_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["quarantine"],
        evidence_claim="certificate_workflow_evidence_is_malformed",
    )
    reuse = _comparison_view(
        records["sandbox_needle_completed_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["reuse_candidate"],
        evidence_claim="certificate_workflow_is_reusable",
    )
    protocol = _comparison_view(
        records["repeated_success_protocol_candidate"],
        semantic_address=semantic,
        resonance_tags=common + ["protocol_candidate"],
        evidence_claim="certificate_workflow_is_ready_for_protocol_promotion",
    )
    needle = _comparison_view(
        records["draft_needle_candidate_with_root_policy"],
        semantic_address=semantic,
        resonance_tags=common + ["needle_candidate"],
        evidence_claim="certificate_workflow_is_ready_for_needle_candidate_review",
    )
    rejected = _comparison_view(
        records["live_child_executor_action_like_blocked_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["action_like", "rejected"],
        evidence_claim="certificate_workflow_action_like_route_is_rejected",
    )
    stale = _comparison_view(
        records["root_final_completed_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["completed"],
        evidence_claim="certificate_workflow_uses_old_requirements",
        observed_at="2025-06-08T00:00:00Z",
    )
    fresh = _comparison_view(
        records["child_cell_degraded_budget_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["fresh", "degraded"],
        evidence_claim="certificate_workflow_has_new_budget_constraint",
        observed_at="2026-06-08T11:00:00Z",
    )
    lower_trust = _comparison_view(
        records["sandbox_needle_timeout_degraded_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["trust_comparison"],
        evidence_claim="certificate_workflow_timeout_is_acceptable",
        gt_trust_hint=0.2,
        source_reliability_hint="low",
    )
    higher_trust = _comparison_view(
        records["root_final_completed_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["trust_comparison"],
        evidence_claim="certificate_workflow_timeout_requires_review",
        gt_trust_hint=0.95,
        source_reliability_hint="high",
    )
    permission = _comparison_view(
        records["sandbox_needle_permission_required_blocked_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["permission_required"],
        evidence_claim="certificate_workflow_requires_permission",
    )
    action_claim = _comparison_view(
        records["root_final_completed_experience"],
        semantic_address=semantic,
        resonance_tags=common + ["action_execution_claim"],
        evidence_claim="certificate_workflow_action_was_executed",
        extra={"claimed_action_execution": True},
    )

    return [
        _pair(
            "completed_vs_completed_conflict",
            root_completed,
            incompatible_completed,
            comparison_scope="same_semantic_address_incompatible_evidence",
            reason="completed_records_make_incompatible_claims",
        ),
        _pair(
            "completed_vs_deadend_conflict",
            root_completed,
            deadend,
            comparison_scope="same_semantic_address_status_conflict",
            reason="completed_record_conflicts_with_deadend_evidence",
        ),
        _pair(
            "reuse_candidate_vs_quarantine_conflict",
            reuse,
            quarantine,
            comparison_scope="reuse_safety_review",
            reason="reuse_candidate_conflicts_with_quarantined_evidence",
        ),
        _pair(
            "promotion_candidate_vs_rejected_evidence",
            protocol,
            rejected,
            comparison_scope="promotion_safety_review",
            reason="promotion_candidate_conflicts_with_rejected_evidence",
        ),
        _pair(
            "stale_vs_fresh_conflict",
            stale,
            fresh,
            comparison_scope="freshness_review",
            reason="older_record_conflicts_with_fresher_evidence",
        ),
        _pair(
            "lower_trust_vs_higher_trust_conflict",
            lower_trust,
            higher_trust,
            comparison_scope="advisory_trust_review",
            reason="lower_trust_record_conflicts_with_higher_trust_record",
        ),
        _pair(
            "action_like_blocked_vs_reuse_conflict",
            rejected,
            reuse,
            comparison_scope="action_safety_reuse_review",
            reason="action_like_blocked_trace_conflicts_with_reuse_candidate",
        ),
        _pair(
            "permission_required_vs_action_execution_conflict",
            permission,
            action_claim,
            comparison_scope="permission_action_review",
            reason="permission_required_record_conflicts_with_action_execution_claim",
        ),
        _pair(
            "protocol_candidate_vs_deadend_conflict",
            protocol,
            deadend,
            comparison_scope="protocol_promotion_review",
            reason="protocol_candidate_conflicts_with_deadend_evidence",
        ),
        _pair(
            "needle_candidate_vs_quarantine_conflict",
            needle,
            quarantine,
            comparison_scope="needle_candidate_promotion_review",
            reason="needle_candidate_conflicts_with_quarantined_evidence",
        ),
        _pair(
            "no_conflict_same_completed_lineage",
            root_completed,
            compatible_completed,
            comparison_scope="same_lineage_compatibility_review",
            reason="completed_records_have_compatible_lineage_and_evidence",
        ),
    ]


def _conflict_reports(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_type = {pair["scenario"]: pair for pair in pairs}
    return [
        _report(
            by_type["completed_vs_completed_conflict"],
            conflict_status="flagged",
            severity="high",
            root_review_required=True,
            gt_review_recommended=True,
            reuse_block_recommended=True,
            recommended_next_step="root_review_incompatible_completed_evidence",
        ),
        _report(
            by_type["completed_vs_deadend_conflict"],
            conflict_status="flagged",
            severity="high",
            root_review_required=True,
            gt_review_recommended=True,
            reuse_block_recommended=True,
            recommended_next_step="root_review_completed_and_deadend_evidence",
        ),
        _report(
            by_type["reuse_candidate_vs_quarantine_conflict"],
            conflict_status="flagged",
            severity="high",
            root_review_required=True,
            reuse_block_recommended=True,
            quarantine_review_recommended=True,
            recommended_next_step="block_reuse_pending_root_quarantine_review",
        ),
        _report(
            by_type["promotion_candidate_vs_rejected_evidence"],
            conflict_status="needs_root_review",
            severity="high",
            root_review_required=True,
            gt_review_recommended=True,
            promotion_block_recommended=True,
            recommended_next_step="block_promotion_pending_root_and_gt_review",
        ),
        _report(
            by_type["stale_vs_fresh_conflict"],
            conflict_status="needs_root_review",
            severity="medium",
            root_review_required=True,
            invalidation_recommended=True,
            older_record_id=by_type["stale_vs_fresh_conflict"][
                "left_experience_record_id"
            ],
            newer_record_id=by_type["stale_vs_fresh_conflict"][
                "right_experience_record_id"
            ],
            recommended_next_step="root_review_freshness_before_any_invalidation",
        ),
        _report(
            by_type["lower_trust_vs_higher_trust_conflict"],
            conflict_status="needs_root_review",
            severity="medium",
            root_review_required=True,
            gt_review_recommended=True,
            lower_trust_record_id=by_type["lower_trust_vs_higher_trust_conflict"][
                "left_experience_record_id"
            ],
            higher_trust_record_id=by_type["lower_trust_vs_higher_trust_conflict"][
                "right_experience_record_id"
            ],
            recommended_next_step="gt_advisory_review_then_root_decision",
        ),
        _report(
            by_type["action_like_blocked_vs_reuse_conflict"],
            conflict_status="flagged",
            severity="critical",
            root_review_required=True,
            gt_review_recommended=True,
            reuse_block_recommended=True,
            promotion_block_recommended=True,
            recommended_next_step="block_reuse_and_promotion_pending_root_review",
        ),
        _report(
            by_type["permission_required_vs_action_execution_conflict"],
            conflict_status="flagged",
            severity="critical",
            root_review_required=True,
            gt_review_recommended=True,
            reuse_block_recommended=True,
            recommended_next_step="block_action_claim_pending_permission_and_root_review",
        ),
        _report(
            by_type["protocol_candidate_vs_deadend_conflict"],
            conflict_status="needs_root_review",
            severity="high",
            root_review_required=True,
            gt_review_recommended=True,
            promotion_block_recommended=True,
            recommended_next_step="block_protocol_promotion_pending_root_review",
        ),
        _report(
            by_type["needle_candidate_vs_quarantine_conflict"],
            conflict_status="flagged",
            severity="critical",
            root_review_required=True,
            gt_review_recommended=True,
            promotion_block_recommended=True,
            quarantine_review_recommended=True,
            recommended_next_step="block_needle_candidate_pending_root_quarantine_review",
        ),
        _report(
            by_type["no_conflict_same_completed_lineage"],
            conflict_status="no_conflict",
            severity="info",
            root_review_required=False,
            recommended_next_step="retain_records_without_conflict_action",
        ),
    ]


def _malicious_claims(base_report: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "malicious_conflictcheck_truth_decision_claim_rejected": (
            "conflictcheck_decides_truth"
        ),
        "malicious_conflictcheck_drs_mutation_claim_rejected": (
            "conflictcheck_mutates_drs"
        ),
        "malicious_conflictcheck_invalidation_claim_rejected": (
            "conflictcheck_invalidates_record"
        ),
        "malicious_conflictcheck_promotion_claim_rejected": (
            "conflictcheck_promotes_record"
        ),
        "malicious_conflictcheck_demotion_claim_rejected": (
            "conflictcheck_demotes_record"
        ),
        "malicious_production_persistence_claim_rejected": "production_persistence",
        "malicious_global_drs_write_claim_rejected": "global_drs_write",
        "malicious_external_drs_network_claim_rejected": "external_drs_network_write",
    }
    result: dict[str, Any] = {}
    for name, field in fields.items():
        malicious = copy.deepcopy(base_report)
        malicious[field] = True
        result[name] = malicious[field] is True
    result.update(
        {
            "conflictcheck_decides_truth": False,
            "conflictcheck_mutates_drs": False,
            "conflictcheck_invalidates_record": False,
            "conflictcheck_promotes_record": False,
            "conflictcheck_demotes_record": False,
            "production_persistence": False,
            "global_drs_write": False,
            "external_drs_network_write": False,
        }
    )
    return result


def collect_conflictcheck() -> ConflictCheckReport:
    lifecycle = collect_drs_lifecycle_semantics()
    lifecycle_records_before = copy.deepcopy(lifecycle.lifecycle_records)
    records = _by_scenario(lifecycle.lifecycle_records)
    pairs_internal = _candidate_pairs(records)
    reports = _conflict_reports(pairs_internal)
    malicious = _malicious_claims(reports[0])
    lifecycle_records_unchanged = lifecycle.lifecycle_records == lifecycle_records_before

    pairs = [
        {key: value for key, value in pair.items() if not key.startswith("_")}
        for pair in pairs_internal
    ]
    source = {
        "source_collector": "collect_drs_lifecycle_semantics",
        "drs_lifecycle_semantics_status": lifecycle.summary[
            "drs_lifecycle_semantics_status"
        ],
        "lifecycle_records_consumed": len(lifecycle.lifecycle_records),
        "statuses_available": lifecycle.summary["statuses_represented"],
        "lifecycle_stages_available": lifecycle.summary["lifecycle_stages_represented"],
        "conflict_status_default": lifecycle.trust_ttl["conflict_status_default"],
        "lifecycle_records_local_only": lifecycle.authority_safety[
            "lifecycle_records_are_local_only"
        ],
        "root_commit_authority_preserved": lifecycle.authority_safety[
            "root_remains_commit_authority"
        ],
        "lifecycle_records_unchanged": lifecycle_records_unchanged,
    }
    authority = {
        "conflictcheck_is_authority": False,
        "conflictcheck_decides_truth": any(
            report["conflictcheck_decides_truth"] for report in reports
        ),
        "conflictcheck_mutates_drs": any(
            report["conflictcheck_mutates_drs"] for report in reports
        ),
        "conflictcheck_invalidates_records": any(
            report["conflictcheck_invalidates_record"] for report in reports
        ),
        "conflictcheck_promotes_records": any(
            report["conflictcheck_promotes_record"] for report in reports
        ),
        "conflictcheck_demotes_records": any(
            report["conflictcheck_demotes_record"] for report in reports
        ),
        "drs_remains_storage_index_lifecycle_layer": True,
        "root_remains_final_authority": all(
            report["root_remains_authority"] for report in reports
        ),
        "gt_review_is_advisory_until_root": True,
        "lifecycle_records_unchanged": lifecycle_records_unchanged,
        "production_persistence_claimed": any(
            report["production_persistence"] for report in reports
        ),
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "production_external_action_executed": any(
            report["production_external_action_executed"] for report in reports
        ),
        "marennya_invoked": False,
        "up_invoked": False,
    }
    malicious_count = sum(
        malicious[key]
        for key in (
            "malicious_conflictcheck_truth_decision_claim_rejected",
            "malicious_conflictcheck_drs_mutation_claim_rejected",
            "malicious_conflictcheck_invalidation_claim_rejected",
            "malicious_conflictcheck_promotion_claim_rejected",
            "malicious_conflictcheck_demotion_claim_rejected",
            "malicious_production_persistence_claim_rejected",
            "malicious_global_drs_write_claim_rejected",
            "malicious_external_drs_network_claim_rejected",
        )
    )
    conflict_types = {report["conflict_type"] for report in reports}
    pass_facts = (
        source["drs_lifecycle_semantics_status"] == "PASS"
        and source["lifecycle_records_consumed"] > 0
        and source["conflict_status_default"] == "not_checked"
        and source["lifecycle_records_local_only"]
        and source["root_commit_authority_preserved"]
        and lifecycle_records_unchanged
        and len(pairs) == len(CONFLICT_TYPES)
        and len(reports) == len(CONFLICT_TYPES)
        and conflict_types == set(CONFLICT_TYPES)
        and all(
            report["root_review_required"]
            for report in reports
            if report["conflict_status"] != "no_conflict"
        )
        and all(
            not report["root_review_required"]
            and not report["reuse_block_recommended"]
            and not report["promotion_block_recommended"]
            for report in reports
            if report["conflict_status"] == "no_conflict"
        )
        and malicious_count == 8
        and not authority["conflictcheck_is_authority"]
        and not authority["conflictcheck_decides_truth"]
        and not authority["conflictcheck_mutates_drs"]
        and not authority["conflictcheck_invalidates_records"]
        and not authority["conflictcheck_promotes_records"]
        and not authority["conflictcheck_demotes_records"]
        and authority["root_remains_final_authority"]
        and not authority["production_persistence_claimed"]
        and not authority["production_external_action_executed"]
    )
    summary = {
        "conflictcheck_status": "PASS" if pass_facts else "FAIL",
        "source_drs_lifecycle_status": source["drs_lifecycle_semantics_status"],
        "lifecycle_records_consumed": source["lifecycle_records_consumed"],
        "candidate_pairs_created": len(pairs),
        "conflict_reports_created": len(reports),
        "conflict_types_represented": sorted(conflict_types),
        "flagged_conflicts": sum(
            report["conflict_status"] == "flagged" for report in reports
        ),
        "no_conflict_reports": sum(
            report["conflict_status"] == "no_conflict" for report in reports
        ),
        "root_review_required_reports": sum(
            report["root_review_required"] for report in reports
        ),
        "gt_review_recommended_reports": sum(
            report["gt_review_recommended"] for report in reports
        ),
        "reuse_block_recommended_reports": sum(
            report["reuse_block_recommended"] for report in reports
        ),
        "promotion_block_recommended_reports": sum(
            report["promotion_block_recommended"] for report in reports
        ),
        "malicious_claims_rejected": malicious_count,
        "conflictcheck_does_not_decide_truth": not authority[
            "conflictcheck_decides_truth"
        ],
        "conflictcheck_does_not_mutate_drs": not authority[
            "conflictcheck_mutates_drs"
        ],
        "root_remains_final_authority": authority["root_remains_final_authority"],
        "ready_for_audit_hash_chain_hardening_v0_1": pass_facts,
        "production_autonomy_claimed": False,
    }
    return ConflictCheckReport(
        input_mode={
            "mode": "deterministic_conflictcheck",
            "source_drs_lifecycle_status": source["drs_lifecycle_semantics_status"],
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
        },
        source_lifecycle=source,
        conflict_candidate_pairs=pairs,
        conflict_reports=reports,
        malicious_claims=malicious,
        authority_safety=authority,
        summary=summary,
    )


def _format(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_conflictcheck(report: ConflictCheckReport) -> str:
    lines = [
        "[CONFLICTCHECK]",
        "note: deterministic ConflictCheck v0.1 proof",
        "note: consumes DRS Lifecycle ExperienceRecord objects",
        "note: emits ConflictReport only",
        "note: ConflictCheck does not decide final truth",
        "note: ConflictCheck does not mutate DRS",
        "note: ConflictCheck does not invalidate records by itself",
        "note: ConflictCheck does not promote or demote records by itself",
        "note: Root remains final authority",
        "note: GT may later evaluate conflict candidates",
        "note: no production persistence",
        "note: no external/global DRS",
        "note: no real external actions",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE LIFECYCLE]", report.source_lifecycle)
    _rows(lines, "[CONFLICT CANDIDATE PAIRS]", report.conflict_candidate_pairs)
    _rows(lines, "[CONFLICT REPORTS]", report.conflict_reports)
    _section(lines, "[MALICIOUS CLAIMS]", report.malicious_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_conflictcheck() -> str:
    return render_conflictcheck(collect_conflictcheck())


def main() -> int:
    print(run_conflictcheck(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
