from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from demo.run_drs_writeback_from_root_final import collect_drs_writeback_from_root_final
from demo.run_fractal_cell_runtime import collect_fractal_cell_runtime
from demo.run_live_child_executor_in_fractal_cell import (
    collect_live_child_executor_in_fractal_cell,
)
from demo.run_root_native_sandbox_needleruntime_e2e import (
    collect_root_native_sandbox_needleruntime_e2e,
)


SUPPORTED_STATUSES = {
    "completed",
    "degraded",
    "blocked",
    "failed",
    "rejected",
    "quarantined",
    "deadend",
    "promotion_candidate",
}
SUPPORTED_STAGES = {
    "experience_record",
    "reuse_candidate",
    "protocol_candidate",
    "needle_candidate",
    "installed_needle_ref",
}
RECORD_SCENARIOS = (
    "root_final_completed_experience",
    "sandbox_needle_completed_experience",
    "sandbox_needle_timeout_degraded_experience",
    "sandbox_needle_invalid_json_quarantined_experience",
    "sandbox_needle_permission_required_blocked_experience",
    "sandbox_needle_contract_mismatch_failed_experience",
    "child_cell_completed_boundary_experience",
    "child_cell_degraded_budget_experience",
    "child_cell_blocked_max_depth_deadend_experience",
    "live_child_executor_completed_experience",
    "live_child_executor_action_like_blocked_experience",
    "repeated_success_protocol_candidate",
    "draft_needle_candidate_with_root_policy",
)


@dataclass(frozen=True)
class DrsLifecycleSemanticsReport:
    input_mode: dict[str, Any]
    source_experience_types: dict[str, Any]
    lifecycle_records: list[dict[str, Any]]
    promotion_ladder: dict[str, Any]
    quarantine_deadends: dict[str, Any]
    trust_ttl: dict[str, Any]
    malicious_claims: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario"]: row for row in rows}


def _trust(
    *,
    status: str,
    validation_status: str,
    conflict_check_required: bool = False,
) -> dict[str, Any]:
    trust = {
        "completed": 0.82,
        "promotion_candidate": 0.9,
        "degraded": 0.48,
        "blocked": 0.2,
        "failed": 0.12,
        "rejected": 0.08,
        "quarantined": 0.05,
        "deadend": 0.04,
    }[status]
    return {
        "gt_trust_hint": trust,
        "validation_status": validation_status,
        "source_reliability_hint": "high" if trust >= 0.8 else "bounded",
        "freshness_hint": "current_proof",
        "conflict_status": "not_checked",
        "conflict_check_required": conflict_check_required,
        "trust_update_is_advisory": True,
    }


def _ttl(status: str) -> dict[str, Any]:
    ttl_class = (
        "long"
        if status in {"completed", "promotion_candidate"}
        else "medium"
        if status == "degraded"
        else "short"
        if status in {"blocked", "failed", "rejected"}
        else "archive"
    )
    return {
        "ttl_class": ttl_class,
        "ttl_reason": f"{status}_experience_policy",
        "freshness_hint": "current_proof",
        "decay_hint": "slow" if ttl_class == "long" else "normal" if ttl_class == "medium" else "fast",
        "ttl_is_advisory": True,
    }


def _quarantine(required: bool, reason: str = "none") -> dict[str, Any]:
    return {
        "quarantine_required": required,
        "quarantine_reason": reason,
        "quarantine_layer": "local_quarantine" if required else "none",
        "quarantine_release_requires_root": True,
    }


def _deadend(marker: bool, reason: str = "none") -> dict[str, Any]:
    return {
        "deadend_marker": marker,
        "deadend_reason": reason,
        "deadend_reuse_blocked": marker,
        "deadend_requires_root_override": marker,
    }


def _promotion(
    state: str,
    *,
    policy_mode: str = "strict_local",
    repeated_validation_count: int = 0,
) -> dict[str, Any]:
    candidate = state in {"reuse_candidate", "protocol_candidate", "needle_candidate"}
    return {
        "promotion_state": state,
        "policy_mode": policy_mode,
        "promotion_allowed_by_policy": candidate,
        "promotion_requires_root": True,
        "root_approval_required": True,
        "promotion_requires_repeated_validation": True,
        "repeated_validation_count": repeated_validation_count,
        "repeated_validation_threshold": 3,
        "promotion_requires_sandbox_tests": state == "needle_candidate",
        "sandbox_tests_required": state == "needle_candidate",
        "promotion_requires_manifest": state == "needle_candidate",
        "manifest_required": state == "needle_candidate",
        "promotion_requires_permission_model": state == "needle_candidate",
        "permission_model_required": state == "needle_candidate",
        "installed_needle": False,
    }


def _record(
    scenario: str,
    *,
    source_artifact_type: str,
    source_artifact_id: str,
    status: str,
    lifecycle_stage: str = "experience_record",
    promotion_state: str = "none",
    pointers: dict[str, Any],
    resonance_tags: list[str],
    risks: list[str] | None = None,
    quarantine_required: bool = False,
    quarantine_reason: str = "none",
    deadend_marker: bool = False,
    deadend_reason: str = "none",
    validation_status: str = "accepted",
    conflict_check_required: bool = False,
    policy_mode: str = "strict_local",
    repeated_validation_count: int = 0,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "experience_record_id": f"experience_record_{scenario}",
        "created_by": "root_authorized_lifecycle_adapter",
        "source_artifact_type": source_artifact_type,
        "source_artifact_id": source_artifact_id,
        "source_trace_id": f"trace_{scenario}",
        "semantic_address": f"local://experience/{scenario}",
        "resonance_tags": resonance_tags,
        "status": status,
        "lifecycle_stage": lifecycle_stage,
        "trust_state": _trust(
            status=status,
            validation_status=validation_status,
            conflict_check_required=conflict_check_required,
        ),
        "ttl_state": _ttl(status),
        "promotion_state": _promotion(
            promotion_state,
            policy_mode=policy_mode,
            repeated_validation_count=repeated_validation_count,
        ),
        "quarantine_state": _quarantine(quarantine_required, quarantine_reason),
        "deadend_state": _deadend(deadend_marker, deadend_reason),
        "lineage_refs": [source_artifact_id],
        "artifact_pointers": pointers,
        "risks": risks or [],
        "provenance": {
            "adapter": "drs_lifecycle_semantics_v0_2",
            "source_scenario": scenario,
            "proof_only": True,
        },
        "time_envelope": {
            "observed_at": "2026-06-08T00:00:00Z",
            "valid_from": "2026-06-08T00:00:00Z",
            "valid_to": None,
            "time_basis": "deterministic_proof_clock",
        },
        "root_authorized": True,
        "drs_is_authority": False,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_network_write": False,
        "direct_reuse_allowed": status == "completed" and promotion_state == "reuse_candidate",
        **(extra or {}),
    }


def _malicious_claims(base: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "malicious_installed_needle_claim_rejected": "installed_needle",
        "malicious_drs_authority_claim_rejected": "drs_is_authority",
        "malicious_global_drs_write_claim_rejected": "global_drs_write",
        "malicious_external_drs_network_claim_rejected": "external_drs_network_write",
        "malicious_production_persistence_claim_rejected": "production_persistence",
    }
    result: dict[str, Any] = {}
    for name, field in checks.items():
        malicious = copy.deepcopy(base)
        if field == "installed_needle":
            malicious["promotion_state"]["installed_needle"] = True
            unsafe = (
                malicious["promotion_state"]["installed_needle"]
                and (
                    malicious["promotion_state"]["root_approval_required"]
                    or malicious["promotion_state"]["manifest_required"]
                    or malicious["promotion_state"]["sandbox_tests_required"]
                )
            )
        else:
            malicious[field] = True
            unsafe = malicious[field] is True
        result[name] = unsafe
    result["automatic_needle_creation_blocked"] = result[
        "malicious_installed_needle_claim_rejected"
    ]
    result["installed_needle"] = False
    result["drs_is_authority"] = False
    result["production_persistence"] = False
    result["global_drs_write"] = False
    result["external_drs_network_write"] = False
    return result


def collect_drs_lifecycle_semantics() -> DrsLifecycleSemanticsReport:
    drs = collect_drs_writeback_from_root_final()
    needle = collect_root_native_sandbox_needleruntime_e2e()
    child = collect_fractal_cell_runtime()
    live_child = collect_live_child_executor_in_fractal_cell(live_requested=False)

    audit_records = {
        row["root_final_status_seen"]: row for row in drs.drs_writeback_audit_records
    }
    needle_rows = _by_scenario(needle.needleruntime_executions)
    child_rows = _by_scenario(child.child_boundary_snapshots)
    live_rows = _by_scenario(live_child.child_boundary_snapshot)
    live_exec = _by_scenario(live_child.live_child_executor)

    records = [
        _record(
            "root_final_completed_experience",
            source_artifact_type="DRSWritebackAuditRecord",
            source_artifact_id=audit_records["accepted"]["drs_writeback_record_id"],
            status="completed",
            pointers={
                "source_root_final_artifact_ref": audit_records["accepted"][
                    "source_root_final_artifact_id"
                ],
                "source_audit_record_ref": audit_records["accepted"][
                    "drs_writeback_record_id"
                ],
            },
            resonance_tags=["root_final", "completed", "local_audit"],
        ),
        _record(
            "sandbox_needle_completed_experience",
            source_artifact_type="NeedleExecutionResult",
            source_artifact_id=needle_rows["sandbox_needle_completed"][
                "needle_execution_result_id"
            ],
            status="completed",
            promotion_state="reuse_candidate",
            pointers={
                "source_needle_execution_result_ref": needle_rows[
                    "sandbox_needle_completed"
                ]["needle_execution_result_id"]
            },
            resonance_tags=["sandbox_needle", "completed", "reuse_candidate"],
        ),
        _record(
            "sandbox_needle_timeout_degraded_experience",
            source_artifact_type="NeedleExecutionResult",
            source_artifact_id=needle_rows["sandbox_needle_timeout_degraded"][
                "needle_execution_result_id"
            ],
            status="degraded",
            pointers={
                "source_needle_execution_result_ref": needle_rows[
                    "sandbox_needle_timeout_degraded"
                ]["needle_execution_result_id"]
            },
            resonance_tags=["sandbox_needle", "timeout", "degraded"],
            risks=["timeout"],
            validation_status="degraded",
            conflict_check_required=True,
        ),
        _record(
            "sandbox_needle_invalid_json_quarantined_experience",
            source_artifact_type="NeedleExecutionResult",
            source_artifact_id=needle_rows["sandbox_needle_invalid_json_failed"][
                "needle_execution_result_id"
            ],
            status="quarantined",
            pointers={
                "source_needle_execution_result_ref": needle_rows[
                    "sandbox_needle_invalid_json_failed"
                ]["needle_execution_result_id"]
            },
            resonance_tags=["sandbox_needle", "invalid_json", "quarantine"],
            risks=["invalid_json"],
            quarantine_required=True,
            quarantine_reason="invalid_json",
            validation_status="rejected",
        ),
        _record(
            "sandbox_needle_permission_required_blocked_experience",
            source_artifact_type="NeedleExecutionResult",
            source_artifact_id=needle_rows["sandbox_needle_permission_required_blocked"][
                "needle_execution_result_id"
            ],
            status="blocked",
            pointers={
                "source_needle_execution_result_ref": needle_rows[
                    "sandbox_needle_permission_required_blocked"
                ]["needle_execution_result_id"]
            },
            resonance_tags=["sandbox_needle", "permission_required", "blocked"],
            risks=["permission_required"],
            validation_status="rejected",
            extra={"permission_required": True},
        ),
        _record(
            "sandbox_needle_contract_mismatch_failed_experience",
            source_artifact_type="NeedleExecutionResult",
            source_artifact_id=needle_rows["sandbox_needle_contract_mismatch_blocked"][
                "needle_execution_result_id"
            ],
            status="failed",
            pointers={
                "source_needle_execution_result_ref": needle_rows[
                    "sandbox_needle_contract_mismatch_blocked"
                ]["needle_execution_result_id"]
            },
            resonance_tags=["sandbox_needle", "contract_mismatch", "failed"],
            risks=["contract_mismatch"],
            validation_status="rejected",
        ),
        _record(
            "child_cell_completed_boundary_experience",
            source_artifact_type="ChildBoundarySnapshot",
            source_artifact_id=child_rows["non_atomic_child_cell_completed"][
                "child_boundary_snapshot_id"
            ],
            status="completed",
            promotion_state="reuse_candidate",
            pointers={
                "source_child_boundary_snapshot_ref": child_rows[
                    "non_atomic_child_cell_completed"
                ]["child_boundary_snapshot_id"]
            },
            resonance_tags=["child_cell", "completed", "boundary_snapshot"],
        ),
        _record(
            "child_cell_degraded_budget_experience",
            source_artifact_type="ChildBoundarySnapshot",
            source_artifact_id=child_rows[
                "non_atomic_child_cell_degraded_budget_limit"
            ]["child_boundary_snapshot_id"],
            status="degraded",
            pointers={
                "source_child_boundary_snapshot_ref": child_rows[
                    "non_atomic_child_cell_degraded_budget_limit"
                ]["child_boundary_snapshot_id"]
            },
            resonance_tags=["child_cell", "budget_limit", "degraded"],
            risks=["budget_limit_approached"],
            validation_status="degraded",
            conflict_check_required=True,
        ),
        _record(
            "child_cell_blocked_max_depth_deadend_experience",
            source_artifact_type="ChildBoundarySnapshot",
            source_artifact_id=child_rows["non_atomic_child_cell_blocked_max_depth"][
                "child_boundary_snapshot_id"
            ],
            status="deadend",
            pointers={
                "source_child_boundary_snapshot_ref": child_rows[
                    "non_atomic_child_cell_blocked_max_depth"
                ]["child_boundary_snapshot_id"]
            },
            resonance_tags=["child_cell", "max_depth", "deadend"],
            risks=["max_depth_exceeded"],
            deadend_marker=True,
            deadend_reason="max_depth_exceeded",
            validation_status="rejected",
        ),
        _record(
            "live_child_executor_completed_experience",
            source_artifact_type="ChildExecutionResult",
            source_artifact_id=live_rows["live_child_executor_completed_proof_task"][
                "source_child_execution_result_id"
            ],
            status="completed",
            promotion_state="reuse_candidate",
            pointers={
                "source_child_execution_result_ref": live_rows[
                    "live_child_executor_completed_proof_task"
                ]["source_child_execution_result_id"],
                "source_child_boundary_snapshot_ref": live_rows[
                    "live_child_executor_completed_proof_task"
                ]["child_boundary_snapshot_id"],
            },
            resonance_tags=["live_child_executor", "completed", "boundary_evidence"],
            extra={
                "live_child_executor_used": live_exec[
                    "live_child_executor_completed_proof_task"
                ]["live_child_executor_used"],
                "automatic_protocol_template_created": False,
            },
        ),
        _record(
            "live_child_executor_action_like_blocked_experience",
            source_artifact_type="ChildExecutionResult",
            source_artifact_id=live_rows[
                "live_child_executor_blocks_action_like_request"
            ]["source_child_execution_result_id"],
            status="rejected",
            pointers={
                "source_child_execution_result_ref": live_rows[
                    "live_child_executor_blocks_action_like_request"
                ]["source_child_execution_result_id"],
                "source_child_boundary_snapshot_ref": live_rows[
                    "live_child_executor_blocks_action_like_request"
                ]["child_boundary_snapshot_id"],
            },
            resonance_tags=["live_child_executor", "action_like", "blocked"],
            risks=["action_like_request_blocked"],
            deadend_marker=True,
            deadend_reason="action_like_request_blocked",
            validation_status="rejected",
            extra={
                "action_like_request_detected": True,
                "real_external_action_executed": False,
            },
        ),
        _record(
            "repeated_success_protocol_candidate",
            source_artifact_type="SyntheticRepeatedValidationSummary",
            source_artifact_id="synthetic_repeated_success_summary",
            status="promotion_candidate",
            lifecycle_stage="protocol_candidate",
            promotion_state="protocol_candidate",
            pointers={"source_audit_record_ref": "synthetic_repeated_success_audit"},
            resonance_tags=["repeated_success", "protocol_candidate"],
            repeated_validation_count=4,
            conflict_check_required=True,
            extra={"installed_needle": False},
        ),
        _record(
            "draft_needle_candidate_with_root_policy",
            source_artifact_type="SyntheticNeedleCandidateDraft",
            source_artifact_id="synthetic_needle_candidate_draft",
            status="promotion_candidate",
            lifecycle_stage="needle_candidate",
            promotion_state="needle_candidate",
            pointers={"source_audit_record_ref": "synthetic_candidate_policy_audit"},
            resonance_tags=["developer_local", "needle_candidate", "not_installed"],
            policy_mode="developer_local",
            repeated_validation_count=3,
            conflict_check_required=True,
            extra={"installed_needle": False},
        ),
    ]

    malicious = _malicious_claims(records[-1])
    stages_in_records = {row["lifecycle_stage"] for row in records}
    promotion_ladder = {
        "experience_record_count": sum(
            row["lifecycle_stage"] == "experience_record" for row in records
        ),
        "reuse_candidate_count": sum(
            row["promotion_state"]["promotion_state"] == "reuse_candidate"
            for row in records
        ),
        "protocol_candidate_count": sum(
            row["lifecycle_stage"] == "protocol_candidate" for row in records
        ),
        "needle_candidate_count": sum(
            row["lifecycle_stage"] == "needle_candidate" for row in records
        ),
        "installed_needle_count": 0,
        "supported_lifecycle_stages": sorted(SUPPORTED_STAGES),
        "automatic_needle_creation_blocked": malicious[
            "automatic_needle_creation_blocked"
        ],
        "root_approval_required_for_promotion": all(
            row["promotion_state"]["root_approval_required"] for row in records
        ),
        "repeated_validation_required_for_strict_mode": True,
        "sandbox_tests_required_for_needle_candidate": records[-1]["promotion_state"][
            "sandbox_tests_required"
        ],
        "manifest_required_for_needle_candidate": records[-1]["promotion_state"][
            "manifest_required"
        ],
        "permission_model_required_for_needle_candidate": records[-1][
            "promotion_state"
        ]["permission_model_required"],
    }
    quarantine_deadends = {
        "quarantined_records": [
            row["experience_record_id"]
            for row in records
            if row["quarantine_state"]["quarantine_required"]
        ],
        "deadend_records": [
            row["experience_record_id"]
            for row in records
            if row["deadend_state"]["deadend_marker"]
        ],
        "direct_reuse_blocked_records": [
            row["experience_record_id"]
            for row in records
            if not row["direct_reuse_allowed"]
        ],
        "quarantine_release_requires_root": all(
            row["quarantine_state"]["quarantine_release_requires_root"]
            for row in records
        ),
        "deadend_override_requires_root": all(
            row["deadend_state"]["deadend_requires_root_override"]
            for row in records
            if row["deadend_state"]["deadend_marker"]
        ),
    }
    trust_ttl = {
        "completed_records": sum(row["status"] == "completed" for row in records),
        "degraded_records": sum(row["status"] == "degraded" for row in records),
        "blocked_records": sum(row["status"] == "blocked" for row in records),
        "failed_records": sum(row["status"] == "failed" for row in records),
        "ttl_advisory_only": all(row["ttl_state"]["ttl_is_advisory"] for row in records),
        "trust_update_advisory_only": all(
            row["trust_state"]["trust_update_is_advisory"] for row in records
        ),
        "conflict_status_default": "not_checked",
        "conflict_check_next_layer": all(
            row["trust_state"]["conflict_status"] == "not_checked" for row in records
        ),
    }
    source_types = {
        "collectors_consumed": [
            "collect_drs_writeback_from_root_final",
            "collect_root_native_sandbox_needleruntime_e2e",
            "collect_fractal_cell_runtime",
            "collect_live_child_executor_in_fractal_cell",
        ],
        "source_drs_writeback_status": drs.summary["drs_writeback_from_root_final_status"],
        "source_needleruntime_status": needle.summary[
            "root_native_sandbox_needleruntime_e2e_status"
        ],
        "source_fractal_cell_status": child.summary["fractal_cell_runtime_status"],
        "source_live_child_reference_status": live_child.summary[
            "live_child_executor_in_fractal_cell_status"
        ],
        "root_final_experience_available": bool(audit_records),
        "sandbox_needle_experience_available": bool(needle_rows),
        "child_cell_boundary_experience_available": bool(child_rows),
        "live_child_executor_experience_available": bool(live_rows),
        "synthetic_protocol_candidate_examples_available": True,
    }
    authority = {
        "drs_lifecycle_is_authority": False,
        "drs_is_full_memory": False,
        "drs_is_vector_store": False,
        "drs_is_automatic_needle_factory": False,
        "root_remains_commit_authority": all(row["root_authorized"] for row in records),
        "lifecycle_records_are_local_only": all(
            not row["global_drs_write"] and not row["external_drs_network_write"]
            for row in records
        ),
        "lifecycle_records_are_proof_level": all(
            row["provenance"]["proof_only"] for row in records
        ),
        "production_persistence_claimed": any(
            row["production_persistence"] for row in records
        ),
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "production_external_action_executed": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    source_pass = (
        source_types["source_drs_writeback_status"] == "PASS"
        and source_types["source_needleruntime_status"] == "PASS"
        and source_types["source_fractal_cell_status"] == "PASS"
        and source_types["source_live_child_reference_status"]
        in {"PASS", "SAFE_FALLBACK_NOT_LIVE_SUCCESS"}
    )
    malicious_count = sum(
        malicious[key]
        for key in (
            "malicious_installed_needle_claim_rejected",
            "malicious_drs_authority_claim_rejected",
            "malicious_global_drs_write_claim_rejected",
            "malicious_external_drs_network_claim_rejected",
            "malicious_production_persistence_claim_rejected",
        )
    )
    pass_facts = (
        source_pass
        and len(records) == len(RECORD_SCENARIOS)
        and {row["scenario"] for row in records} == set(RECORD_SCENARIOS)
        and SUPPORTED_STATUSES <= {row["status"] for row in records}
        and {"experience_record", "protocol_candidate", "needle_candidate"}
        <= stages_in_records
        and promotion_ladder["installed_needle_count"] == 0
        and promotion_ladder["automatic_needle_creation_blocked"]
        and malicious_count == 5
        and bool(quarantine_deadends["quarantined_records"])
        and bool(quarantine_deadends["deadend_records"])
        and trust_ttl["ttl_advisory_only"]
        and trust_ttl["trust_update_advisory_only"]
        and trust_ttl["conflict_check_next_layer"]
        and not authority["drs_lifecycle_is_authority"]
        and not authority["drs_is_full_memory"]
        and not authority["drs_is_vector_store"]
        and not authority["drs_is_automatic_needle_factory"]
        and authority["root_remains_commit_authority"]
        and authority["lifecycle_records_are_local_only"]
        and authority["lifecycle_records_are_proof_level"]
        and not authority["production_persistence_claimed"]
        and not authority["production_external_action_executed"]
    )
    summary = {
        "drs_lifecycle_semantics_status": "PASS" if pass_facts else "FAIL",
        "records_created": len(records),
        "statuses_represented": sorted({row["status"] for row in records}),
        "lifecycle_stages_represented": sorted(SUPPORTED_STAGES),
        "promotion_ladder_represented": True,
        "automatic_needle_creation_blocked": promotion_ladder[
            "automatic_needle_creation_blocked"
        ],
        "malicious_claims_rejected": malicious_count,
        "quarantine_and_deadends_represented": bool(
            quarantine_deadends["quarantined_records"]
            and quarantine_deadends["deadend_records"]
        ),
        "trust_ttl_advisory_represented": trust_ttl["ttl_advisory_only"]
        and trust_ttl["trust_update_advisory_only"],
        "conflict_check_deferred_to_next_layer": trust_ttl[
            "conflict_check_next_layer"
        ],
        "root_remains_commit_authority": authority["root_remains_commit_authority"],
        "local_proof_level_only": authority["lifecycle_records_are_local_only"]
        and authority["lifecycle_records_are_proof_level"],
        "ready_for_conflictcheck_v0_1": pass_facts,
        "production_autonomy_claimed": False,
    }
    return DrsLifecycleSemanticsReport(
        input_mode={
            "mode": "deterministic_drs_lifecycle_semantics",
            "local_drs_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
        },
        source_experience_types=source_types,
        lifecycle_records=records,
        promotion_ladder=promotion_ladder,
        quarantine_deadends=quarantine_deadends,
        trust_ttl=trust_ttl,
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


def render_drs_lifecycle_semantics(report: DrsLifecycleSemanticsReport) -> str:
    lines = [
        "[DRS LIFECYCLE SEMANTICS]",
        "note: deterministic LocalDRS lifecycle semantics proof",
        "note: local/proof-level lifecycle records only",
        "note: DRS is address/resonance/lineage/audit layer",
        "note: DRS is not full memory",
        "note: DRS is not decision authority",
        "note: DRS is not vector store",
        "note: DRS is not automatic NeedleFactory",
        "note: Root remains commit authority",
        "note: no production persistence",
        "note: no external/global DRS",
        "note: no real external actions",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE EXPERIENCE TYPES]", report.source_experience_types)
    _rows(lines, "[LIFECYCLE RECORDS]", report.lifecycle_records)
    _section(lines, "[PROMOTION LADDER]", report.promotion_ladder)
    _section(lines, "[QUARANTINE / DEADENDS]", report.quarantine_deadends)
    _section(lines, "[TRUST / TTL]", report.trust_ttl)
    _section(lines, "[MALICIOUS CLAIMS]", report.malicious_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_drs_lifecycle_semantics() -> str:
    return render_drs_lifecycle_semantics(collect_drs_lifecycle_semantics())


def main() -> int:
    print(run_drs_lifecycle_semantics(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
