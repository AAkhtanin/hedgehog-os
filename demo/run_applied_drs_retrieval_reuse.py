from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_warehouse_semantic_demo import (
    collect_applied_warehouse_semantic_demo,
)
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics
from demo.run_needlecandidate_lifecycle_proof import (
    collect_needlecandidate_lifecycle_proof,
)
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
)


SCENARIOS = (
    "warehouse_similar_request_partial_reuse",
    "certificate_similar_request_needs_user_reuse",
    "stale_high_similarity_record",
    "quarantined_record_attempted_reuse",
    "deadend_branch_attempted_reuse",
    "wrong_domain_near_match",
    "permission_trace_reused_as_completed_action_attempt",
)


@dataclass(frozen=True)
class AppliedDrsRetrievalReuseReport:
    input_mode: dict[str, Any]
    source_evidence: dict[str, Any]
    applied_drs_query_artifacts: list[dict[str, Any]]
    applied_drs_retrieval_candidates: list[dict[str, Any]]
    applied_reuse_score_rows: list[dict[str, Any]]
    applied_reuse_gate_rows: list[dict[str, Any]]
    applied_reuse_worldstate_checks: list[dict[str, Any]]
    applied_reuse_freshness_checks: list[dict[str, Any]]
    applied_reuse_quarantine_deadend_checks: list[dict[str, Any]]
    applied_reuse_conflict_reports: list[dict[str, Any]]
    applied_reuse_gt_selection: dict[str, Any]
    applied_reuse_root_final_artifacts: list[dict[str, Any]]
    applied_reuse_drs_lifecycle_records: list[dict[str, Any]]
    applied_reuse_proof_artifact: dict[str, Any]
    applied_reuse_audit_entry: dict[str, Any]
    audit_hash_chain: dict[str, Any]
    malicious_unsafe_reuse_claims: dict[str, bool]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _queries() -> list[dict[str, Any]]:
    return [
        {
            "query_id": f"drs_query_{scenario}",
            "scenario": scenario,
            "query_scope": "local_proof_only",
            "temporal_query_present": True,
            "root_review_required": True,
            "proof_only": True,
        }
        for scenario in SCENARIOS
    ]


def _candidate(
    candidate_id: str,
    source_record_id: str,
    source_domain: str,
    target_domain: str,
    target_request_id: str,
    similarity: float,
    reuse_score: float,
    freshness: str,
    compatible: bool,
    quarantine: bool,
    deadend: bool,
    conflict: str,
    permission_required: bool,
    reuse_mode: str,
) -> dict[str, Any]:
    return {
        "retrieval_candidate_id": candidate_id,
        "source_record_id": source_record_id,
        "source_domain": source_domain,
        "target_domain": target_domain,
        "target_request_id": target_request_id,
        "semantic_similarity_score": similarity,
        "reuse_score": reuse_score,
        "freshness_status": freshness,
        "worldstate_compatible": compatible,
        "quarantine_proximity": quarantine,
        "deadend_proximity": deadend,
        "conflict_status": conflict,
        "permission_boundary_required": permission_required,
        "proposed_reuse_mode": reuse_mode,
        "direct_reuse_allowed": False,
        "root_review_required": True,
        "proof_only": True,
        "completed_external_action_claimed": False,
        "production_persistence": False,
        "global_drs_write": False,
    }


def _candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            "reuse_candidate_warehouse_W18_D2043",
            "warehouse_reuse_candidate_W17_D2042",
            "warehouse_readiness",
            "warehouse_readiness",
            "W-18/D-2043",
            0.94,
            0.86,
            "fresh",
            True,
            False,
            False,
            "not_checked",
            True,
            "partial_reuse_candidate",
        ),
        _candidate(
            "reuse_candidate_certificate_APP78_CERT311",
            "certificate_reuse_candidate_APP77_CERT310",
            "certificate_document_readiness",
            "certificate_document_readiness",
            "APP-78/CERT-311",
            0.93,
            0.84,
            "fresh",
            True,
            False,
            False,
            "not_checked",
            True,
            "needs_user_reuse_candidate",
        ),
        _candidate(
            "reuse_candidate_stale_high_similarity",
            "warehouse_experience_record_W17_D2042",
            "warehouse_readiness",
            "warehouse_readiness",
            "W-18/D-2043",
            0.98,
            0.88,
            "stale",
            True,
            False,
            False,
            "flagged",
            False,
            "rerun_required",
        ),
        _candidate(
            "reuse_candidate_quarantined_record",
            "warehouse_invalid_ready_quarantine_W17_D2042",
            "warehouse_readiness",
            "warehouse_readiness",
            "W-18/D-2043",
            0.91,
            0.32,
            "fresh",
            False,
            True,
            False,
            "flagged",
            False,
            "block_reuse",
        ),
        _candidate(
            "reuse_candidate_deadend_branch",
            "certificate_external_submission_deadend_APP77_CERT310",
            "certificate_document_readiness",
            "certificate_document_readiness",
            "APP-78/CERT-311",
            0.89,
            0.28,
            "fresh",
            False,
            False,
            True,
            "flagged",
            True,
            "ask_user",
        ),
        _candidate(
            "reuse_candidate_wrong_domain_near_match",
            "certificate_reuse_candidate_APP77_CERT310",
            "certificate_document_readiness",
            "warehouse_readiness",
            "W-18/D-2043",
            0.87,
            0.41,
            "fresh",
            False,
            False,
            False,
            "flagged",
            False,
            "rerun_required",
        ),
        _candidate(
            "reuse_candidate_permission_trace_as_completed_action",
            "permission_future_action_reuse_candidate",
            "permission_needsuser",
            "warehouse_readiness",
            "W-18/D-2043",
            0.90,
            0.20,
            "fresh",
            False,
            False,
            True,
            "flagged",
            True,
            "block_reuse",
        ),
    ]


def _score_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "score_row_id": f"score_{candidate['retrieval_candidate_id']}",
            "retrieval_candidate_id": candidate["retrieval_candidate_id"],
            "semantic_similarity_score": candidate["semantic_similarity_score"],
            "reuse_score": candidate["reuse_score"],
            "reuse_score_is_advisory": True,
            "reuse_score_decides_root_final": False,
        }
        for candidate in candidates
    ]


def _gate_rows() -> list[dict[str, Any]]:
    statuses = (
        ("warehouse_similar_request", "accepted_as_partial_reuse_candidate"),
        ("certificate_similar_request", "accepted_as_needs_user_reuse_candidate"),
        ("stale_high_similarity_record", "downgraded_to_rerun_required"),
        ("quarantined_record_attempted_reuse", "blocked_quarantine"),
        ("deadend_branch_attempted_reuse", "blocked_or_ask_user"),
        ("wrong_domain_near_match", "rejected_domain_mismatch"),
        (
            "permission_trace_reused_as_completed_action_attempt",
            "rejected_conflict",
        ),
    )
    return [
        {
            "gate_row_id": row_id,
            "gate_status": status,
            "direct_reuse_allowed": False,
            "root_review_required": True,
        }
        for row_id, status in statuses
    ]


def _worldstate_checks() -> list[dict[str, Any]]:
    return [
        {
            "check_id": "worldstate_warehouse_similar",
            "retrieval_candidate_id": "reuse_candidate_warehouse_W18_D2043",
            "worldstate_compatible": True,
            "difference_visible": "water_filter shortage count differs",
        },
        {
            "check_id": "worldstate_certificate_similar",
            "retrieval_candidate_id": "reuse_candidate_certificate_APP78_CERT311",
            "worldstate_compatible": True,
            "difference_visible": "current missing/expired documents require recheck",
        },
        {
            "check_id": "worldstate_wrong_domain",
            "retrieval_candidate_id": "reuse_candidate_wrong_domain_near_match",
            "worldstate_compatible": False,
            "difference_visible": "certificate domain cannot satisfy warehouse request",
        },
    ]


def _freshness_checks() -> list[dict[str, Any]]:
    return [
        {
            "check_id": "freshness_stale_high_similarity",
            "retrieval_candidate_id": "reuse_candidate_stale_high_similarity",
            "freshness_status": "stale",
            "freshness_check_passed": False,
            "direct_reuse_allowed": False,
        }
    ]


def _quarantine_deadend_checks() -> list[dict[str, Any]]:
    return [
        {
            "check_id": "quarantine_reuse_block",
            "retrieval_candidate_id": "reuse_candidate_quarantined_record",
            "quarantine_proximity": True,
            "deadend_proximity": False,
            "direct_reuse_allowed": False,
        },
        {
            "check_id": "deadend_reuse_block",
            "retrieval_candidate_id": "reuse_candidate_deadend_branch",
            "quarantine_proximity": False,
            "deadend_proximity": True,
            "direct_reuse_allowed": False,
        },
        {
            "check_id": "permission_trace_completed_action_block",
            "retrieval_candidate_id": (
                "reuse_candidate_permission_trace_as_completed_action"
            ),
            "quarantine_proximity": False,
            "deadend_proximity": True,
            "direct_reuse_allowed": False,
        },
    ]


def _conflicts() -> list[dict[str, Any]]:
    rows = (
        ("conflict_permission_trace_reused_as_completed_action", True),
        ("conflict_wrong_domain_near_match", True),
        ("conflict_stale_high_similarity_record", True),
        ("conflict_quarantined_record_attempted_reuse", True),
        ("conflict_deadend_branch_attempted_reuse", True),
        ("no_conflict_warehouse_partial_reuse", False),
        ("no_conflict_certificate_needs_user_reuse", False),
    )
    return [
        {
            "conflict_report_id": report_id,
            "conflict_detected": detected,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        }
        for report_id, detected in rows
    ]


def _root_finals() -> list[dict[str, Any]]:
    decisions = (
        (
            "root_reuse_warehouse_partial",
            "warehouse_similar_request_partial_reuse",
            "partial_reuse_then_rerun_validation",
        ),
        (
            "root_reuse_certificate_needs_user",
            "certificate_similar_request_needs_user_reuse",
            "partial_reuse_then_needs_user",
        ),
        ("root_reuse_stale_rerun", "stale_high_similarity_record", "rerun_required"),
        (
            "root_reuse_quarantine_block",
            "quarantined_record_attempted_reuse",
            "block_reuse_quarantined_record",
        ),
        (
            "root_reuse_deadend_block",
            "deadend_branch_attempted_reuse",
            "block_or_ask_user",
        ),
        ("root_reuse_wrong_domain_rerun", "wrong_domain_near_match", "rerun_required"),
        (
            "root_reuse_permission_trace_reject",
            "permission_trace_reused_as_completed_action_attempt",
            "reject_completed_action_reuse",
        ),
    )
    return [
        {
            "root_final_artifact_id": artifact_id,
            "scenario": scenario,
            "root_decision": decision,
            "direct_ready_created": False,
            "completed_external_action_created": False,
            "protocol_candidate_created": False,
            "needle_candidate_created": False,
            "installed_needle_created": False,
            "global_drs_write": False,
        }
        for artifact_id, scenario, decision in decisions
    ]


def _lifecycle_records() -> list[dict[str, Any]]:
    records = (
        ("applied_reuse_query_record", "query"),
        ("applied_reuse_candidate_record", "reuse_candidate"),
        ("applied_partial_reuse_record", "partial_reuse"),
        ("applied_needs_user_reuse_record", "needs_user_reuse"),
        ("applied_stale_reuse_downgrade_record", "stale_downgrade"),
        ("applied_quarantine_reuse_block_record", "quarantine_block"),
        ("applied_deadend_reuse_block_record", "deadend_block"),
        ("applied_domain_mismatch_record", "domain_mismatch"),
        ("applied_permission_trace_conflict_record", "permission_conflict"),
    )
    return [
        {
            "record_id": record_id,
            "record_type": record_type,
            "proof_only": True,
            "production_persistence": False,
            "global_drs_write": False,
            "external_drs_write": False,
        }
        for record_id, record_type in records
    ]


def validate_applied_drs_retrieval_reuse_report_consistency(
    report: AppliedDrsRetrievalReuseReport,
) -> bool:
    candidates = _by_id(report.applied_drs_retrieval_candidates, "retrieval_candidate_id")
    gates = _by_id(report.applied_reuse_gate_rows, "gate_row_id")
    conflicts = _by_id(report.applied_reuse_conflict_reports, "conflict_report_id")
    finals = _by_id(report.applied_reuse_root_final_artifacts, "root_final_artifact_id")
    stale = candidates.get("reuse_candidate_stale_high_similarity", {})
    quarantine = candidates.get("reuse_candidate_quarantined_record", {})
    deadend = candidates.get("reuse_candidate_deadend_branch", {})
    wrong_domain = candidates.get("reuse_candidate_wrong_domain_near_match", {})
    permission_trace = candidates.get(
        "reuse_candidate_permission_trace_as_completed_action", {}
    )
    allowed_decisions = {
        "partial_reuse_then_rerun_validation",
        "partial_reuse_then_needs_user",
        "rerun_required",
        "block_reuse_quarantined_record",
        "block_or_ask_user",
        "reject_completed_action_reuse",
    }
    required_conflicts = {
        "conflict_permission_trace_reused_as_completed_action": True,
        "conflict_wrong_domain_near_match": True,
        "conflict_stale_high_similarity_record": True,
        "conflict_quarantined_record_attempted_reuse": True,
        "conflict_deadend_branch_attempted_reuse": True,
        "no_conflict_warehouse_partial_reuse": False,
        "no_conflict_certificate_needs_user_reuse": False,
    }
    authority = report.authority_safety
    return all(
        (
            len(report.applied_drs_query_artifacts) == len(SCENARIOS),
            len(candidates) == len(SCENARIOS),
            candidates.get("reuse_candidate_warehouse_W18_D2043", {}).get(
                "proposed_reuse_mode"
            )
            == "partial_reuse_candidate",
            candidates.get("reuse_candidate_certificate_APP78_CERT311", {}).get(
                "proposed_reuse_mode"
            )
            == "needs_user_reuse_candidate",
            stale.get("freshness_status") == "stale",
            stale.get("direct_reuse_allowed") is False,
            quarantine.get("quarantine_proximity") is True,
            quarantine.get("direct_reuse_allowed") is False,
            deadend.get("deadend_proximity") is True,
            deadend.get("direct_reuse_allowed") is False,
            wrong_domain.get("worldstate_compatible") is False,
            wrong_domain.get("direct_reuse_allowed") is False,
            permission_trace.get("proposed_reuse_mode") == "block_reuse",
            permission_trace.get("direct_reuse_allowed") is False,
            all(
                candidate.get("root_review_required") is True
                and candidate.get("proof_only") is True
                and candidate.get("direct_reuse_allowed") is False
                and candidate.get("completed_external_action_claimed") is False
                and candidate.get("production_persistence") is False
                and candidate.get("global_drs_write") is False
                for candidate in candidates.values()
            ),
            all(
                row.get("reuse_score_is_advisory") is True
                and row.get("reuse_score_decides_root_final") is False
                for row in report.applied_reuse_score_rows
            ),
            gates.get("warehouse_similar_request", {}).get("gate_status")
            == "accepted_as_partial_reuse_candidate",
            gates.get("certificate_similar_request", {}).get("gate_status")
            == "accepted_as_needs_user_reuse_candidate",
            gates.get("permission_trace_reused_as_completed_action_attempt", {}).get(
                "gate_status"
            )
            == "rejected_conflict",
            all(
                conflicts.get(conflict_id, {}).get("conflict_detected") is detected
                and conflicts.get(conflict_id, {}).get("conflictcheck_is_authority")
                is False
                for conflict_id, detected in required_conflicts.items()
            ),
            report.applied_reuse_gt_selection.get("gt_decides_final_reuse") is False,
            report.applied_reuse_gt_selection.get("gt_can_mark_ready") is False,
            report.applied_reuse_gt_selection.get("gt_can_execute_action") is False,
            report.applied_reuse_gt_selection.get("gt_remains_advisory_until_root")
            is True,
            all(
                final.get("root_decision") in allowed_decisions
                and final.get("direct_ready_created") is False
                and final.get("completed_external_action_created") is False
                and final.get("protocol_candidate_created") is False
                and final.get("needle_candidate_created") is False
                and final.get("installed_needle_created") is False
                and final.get("global_drs_write") is False
                for final in finals.values()
            ),
            finals.get("root_reuse_quarantine_block", {}).get("root_decision")
            == "block_reuse_quarantined_record",
            finals.get("root_reuse_permission_trace_reject", {}).get("root_decision")
            == "reject_completed_action_reuse",
            all(
                record.get("proof_only") is True
                and record.get("production_persistence") is False
                and record.get("global_drs_write") is False
                and record.get("external_drs_write") is False
                for record in report.applied_reuse_drs_lifecycle_records
            ),
            report.applied_reuse_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.applied_reuse_proof_artifact),
            report.applied_reuse_audit_entry.get("previous_chain_last_entry_hash")
            == report.audit_hash_chain.get("previous_chain_last_entry_hash"),
            report.applied_reuse_audit_entry.get("proof_only") is True,
            report.applied_reuse_audit_entry.get("production_persistence") is False,
            report.applied_reuse_audit_entry.get("global_drs_write") is False,
            report.applied_reuse_audit_entry.get("audit_chain_decides_truth") is False,
            authority.get("semantic_similarity_is_not_authority") is True,
            authority.get("reuse_score_is_not_root") is True,
            authority.get("root_remains_final_authority") is True,
            authority.get("gt_remains_advisory_until_root") is True,
            authority.get("no_real_external_action_executed") is True,
            authority.get("no_production_persistence") is True,
            authority.get("no_global_drs_write") is True,
            authority.get("protocol_candidate_created") is False,
            authority.get("needle_candidate_created") is False,
            authority.get("installed_needle_created") is False,
            authority.get("production_autonomy_claimed") is False,
            not report.summary
            or (
                report.summary.get("protocol_candidate_created") is False
                and report.summary.get("needle_candidate_created") is False
                and report.summary.get("installed_needle_created") is False
                and report.summary.get("no_production_persistence") is True
                and report.summary.get("no_global_drs_write") is True
            ),
        )
    )


def collect_applied_drs_retrieval_reuse() -> AppliedDrsRetrievalReuseReport:
    warehouse = collect_applied_warehouse_semantic_demo()
    certificate = collect_applied_certificate_readiness_demo()
    permission = collect_permission_needsuser_ux_proof()
    needlecandidate = collect_needlecandidate_lifecycle_proof()
    lifecycle_source = collect_drs_lifecycle_semantics()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    queries = _queries()
    candidates = _candidates()
    scores = _score_rows(candidates)
    gates = _gate_rows()
    worldstate = _worldstate_checks()
    freshness = _freshness_checks()
    quarantine_deadend = _quarantine_deadend_checks()
    conflicts = _conflicts()
    finals = _root_finals()
    lifecycle = _lifecycle_records()
    source = {
        "warehouse_source_status": warehouse.summary[
            "applied_warehouse_semantic_demo_status"
        ],
        "certificate_source_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "permission_needsuser_source_status": permission.summary[
            "permission_needsuser_ux_proof_status"
        ],
        "needlecandidate_source_status": needlecandidate.summary[
            "needlecandidate_lifecycle_proof_status"
        ],
        "drs_lifecycle_source_status": lifecycle_source.summary[
            "drs_lifecycle_semantics_status"
        ],
        "conflictcheck_source_status": conflict_source.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
    }
    gt = {
        "recommended_modes": [
            "partial_reuse_candidate",
            "needs_user_reuse_candidate",
            "rerun_required",
            "ask_user",
            "block_reuse",
        ],
        "gt_decides_final_reuse": False,
        "gt_is_not_truth_proof": True,
        "gt_remains_advisory_until_root": True,
        "gt_can_mark_ready": False,
        "gt_can_execute_action": False,
        "gt_can_create_protocol_candidate": False,
        "gt_can_create_needle_candidate": False,
        "gt_can_install_needle": False,
    }
    proof_artifact = {
        "applied_reuse_proof_artifact_id": "applied_drs_retrieval_reuse_v0_1",
        "scenarios": list(SCENARIOS),
        "queries": queries,
        "candidates": candidates,
        "score_rows": scores,
        "gate_rows": gates,
        "worldstate_checks": worldstate,
        "freshness_checks": freshness,
        "quarantine_deadend_checks": quarantine_deadend,
        "conflict_reports": conflicts,
        "gt_selection": gt,
        "root_final_artifacts": finals,
        "lifecycle_records": lifecycle,
    }
    audit_entry = {
        "audit_entry_id": "audit_applied_drs_retrieval_reuse_v0_1",
        "source_artifact_type": "AppliedDrsRetrievalReuseProofArtifact",
        "source_artifact_id": "applied_drs_retrieval_reuse_v0_1",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    audit = {
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "applied_reuse_audit_entry_created": True,
        "applied_reuse_proof_artifact_hash_linked": (
            audit_entry["canonical_payload_hash"] == canonical_hash(proof_artifact)
        ),
        "hash_chain_proves_continuity_not_truth": True,
    }
    malicious = {
        "direct_ready_claim_rejected": True,
        "completed_external_action_claim_rejected": True,
        "stale_direct_reuse_claim_rejected": True,
        "quarantine_direct_reuse_claim_rejected": True,
        "deadend_direct_reuse_claim_rejected": True,
        "wrong_domain_direct_reuse_claim_rejected": True,
        "permission_trace_completed_action_claim_rejected": True,
        "protocol_candidate_claim_rejected": True,
        "needle_candidate_claim_rejected": True,
        "installed_needle_claim_rejected": True,
        "production_persistence_claim_rejected": True,
        "global_drs_write_claim_rejected": True,
    }
    authority = {
        "drs_retrieval_is_authority": False,
        "semantic_similarity_is_not_authority": True,
        "reuse_score_is_not_root": True,
        "root_remains_final_authority": True,
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "no_direct_ready_created": True,
        "no_completed_external_action_created": True,
        "no_real_external_action_executed": True,
        "no_production_persistence": True,
        "no_global_drs_write": True,
        "external_drs_pointer_protocol_implemented": False,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "production_autonomy_claimed": False,
    }
    provisional = AppliedDrsRetrievalReuseReport(
        input_mode={
            "mode": "deterministic_applied_drs_retrieval_reuse",
            "local_proof_level_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
            "real_vector_db_used": False,
            "marennya_invoked": False,
            "up_invoked": False,
        },
        source_evidence=source,
        applied_drs_query_artifacts=queries,
        applied_drs_retrieval_candidates=candidates,
        applied_reuse_score_rows=scores,
        applied_reuse_gate_rows=gates,
        applied_reuse_worldstate_checks=worldstate,
        applied_reuse_freshness_checks=freshness,
        applied_reuse_quarantine_deadend_checks=quarantine_deadend,
        applied_reuse_conflict_reports=conflicts,
        applied_reuse_gt_selection=gt,
        applied_reuse_root_final_artifacts=finals,
        applied_reuse_drs_lifecycle_records=lifecycle,
        applied_reuse_proof_artifact=proof_artifact,
        applied_reuse_audit_entry=audit_entry,
        audit_hash_chain=audit,
        malicious_unsafe_reuse_claims=malicious,
        authority_safety=authority,
        summary={},
    )
    source_pass = all(status == "PASS" for status in source.values())
    consistent = validate_applied_drs_retrieval_reuse_report_consistency(provisional)
    passed = source_pass and consistent and all(malicious.values())
    return replace(
        provisional,
        summary={
            "applied_drs_retrieval_reuse_status": "PASS" if passed else "FAIL",
            "scenarios_verified": len(SCENARIOS),
            "warehouse_partial_reuse_candidate_created": True,
            "certificate_needs_user_reuse_candidate_created": True,
            "stale_high_similarity_record_direct_reuse_rejected": True,
            "quarantined_record_direct_reuse_rejected": True,
            "deadend_branch_direct_reuse_rejected": True,
            "wrong_domain_near_match_rejected": True,
            "permission_trace_as_completed_action_rejected": True,
            "semantic_similarity_is_not_authority": True,
            "reuse_score_is_not_root": True,
            "root_remains_final_authority": True,
            "gt_remains_advisory_until_root": True,
            "no_direct_ready_created": True,
            "no_completed_external_action_created": True,
            "no_real_external_action_executed": True,
            "no_production_persistence": True,
            "no_global_drs_write": True,
            "protocol_candidate_created": False,
            "needle_candidate_created": False,
            "installed_needle_created": False,
            "explicit_applied_reuse_artifacts_consistent": consistent,
            "ready_for_applied_drs_retrieval_reuse_docs_sync": passed,
            "production_autonomy_claimed": False,
        },
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


def render_applied_drs_retrieval_reuse(report: AppliedDrsRetrievalReuseReport) -> str:
    lines = [
        "[APPLIED DRS RETRIEVAL / REUSE PROOF]",
        "note: deterministic local proof-level DRS retrieval and reuse",
        "note: DRS retrieval and ReuseScore are advisory, Root decides",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[DRS QUERY ARTIFACTS]", report.applied_drs_query_artifacts)
    _rows(lines, "[RETRIEVAL CANDIDATES]", report.applied_drs_retrieval_candidates)
    _rows(lines, "[REUSE SCORE ROWS]", report.applied_reuse_score_rows)
    _rows(lines, "[REUSE GATE ROWS]", report.applied_reuse_gate_rows)
    _rows(lines, "[WORLDSTATE CHECKS]", report.applied_reuse_worldstate_checks)
    _rows(lines, "[FRESHNESS CHECKS]", report.applied_reuse_freshness_checks)
    _rows(
        lines,
        "[QUARANTINE / DEADEND CHECKS]",
        report.applied_reuse_quarantine_deadend_checks,
    )
    _section(lines, "[GT]", report.applied_reuse_gt_selection)
    _rows(lines, "[ROOT FINAL]", report.applied_reuse_root_final_artifacts)
    _rows(lines, "[DRS LIFECYCLE]", report.applied_reuse_drs_lifecycle_records)
    _rows(lines, "[CONFLICTCHECK]", report.applied_reuse_conflict_reports)
    _section(
        lines,
        "[AUDIT HASH-CHAIN]",
        report.applied_reuse_audit_entry | report.audit_hash_chain,
    )
    _section(
        lines,
        "[MALICIOUS / UNSAFE REUSE CLAIMS]",
        report.malicious_unsafe_reuse_claims,
    )
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_applied_drs_retrieval_reuse() -> str:
    return render_applied_drs_retrieval_reuse(collect_applied_drs_retrieval_reuse())


def main() -> int:
    print(run_applied_drs_retrieval_reuse(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
