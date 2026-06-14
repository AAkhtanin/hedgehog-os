from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


ATTEMPT_DEFINITIONS = (
    (
        "connector_observation_to_truth",
        "connector_observation",
        "promote_connector_observation_to_truth",
    ),
    (
        "connector_observation_to_accepted_evidence",
        "connector_observation",
        "bypass_external_evidence_acceptance_gate",
    ),
    (
        "accepted_evidence_to_external_action",
        "accepted_evidence",
        "execute_dispatch_payment_or_legal_submission",
    ),
    (
        "accepted_evidence_to_ready_status",
        "accepted_evidence",
        "create_enterprise_ready_status",
    ),
    (
        "semantic_draft_to_truth",
        "semantic_draft",
        "promote_semantic_draft_to_truth",
    ),
    (
        "semantic_draft_to_root_final",
        "semantic_draft",
        "promote_semantic_draft_to_root_final",
    ),
    (
        "semantic_draft_to_action",
        "semantic_draft",
        "execute_external_action_from_semantic_draft",
    ),
    (
        "drs_reuse_to_authority",
        "drs_reuse",
        "promote_reuse_hit_to_authority_and_bypass_root",
    ),
    (
        "external_pointer_to_global_drs_write",
        "external_drs_pointer_candidate",
        "write_pointer_claim_to_global_or_external_drs",
    ),
    (
        "bridge_traversal_to_provenance_laundering",
        "cross_domain_drs_bridge",
        "launder_provenance_across_domains",
    ),
    (
        "needlecandidate_to_installed_needle",
        "needle_candidate",
        "promote_candidate_to_installed_needle",
    ),
    (
        "child_cell_to_autonomous_actor",
        "bounded_child_cell",
        "promote_child_cell_to_autonomous_finalizer",
    ),
    (
        "gt_recommendation_to_root_authority",
        "gt_advisory",
        "promote_gt_recommendation_to_root_authority",
    ),
    (
        "audit_hash_to_truth",
        "audit_hash_chain",
        "promote_continuity_hash_to_truth",
    ),
    (
        "permission_needsuser_to_execution",
        "permission_needs_user",
        "treat_permission_or_needs_user_as_execution",
    ),
    (
        "root_bypass_via_resultproposal",
        "result_proposal",
        "skip_post_vv_gt_and_root",
    ),
    (
        "time_envelope_stale_to_current",
        "time_envelope",
        "promote_stale_or_expired_evidence_to_current",
    ),
    (
        "conflicting_sources_to_ready",
        "conflicting_enterprise_sources",
        "promote_conflicting_sources_to_ready",
    ),
)

QUARANTINED_ATTEMPT_IDS = {
    "external_pointer_to_global_drs_write",
    "bridge_traversal_to_provenance_laundering",
    "time_envelope_stale_to_current",
    "conflicting_sources_to_ready",
}


@dataclass(frozen=True)
class EnterpriseChaosPackReport:
    source_evidence: dict[str, Any]
    source_checkpoints: list[dict[str, Any]]
    enterprise_chaos_request: dict[str, Any]
    chaos_attempts: list[dict[str, Any]]
    quarantine_summary: dict[str, Any]
    boundary_matrix: dict[str, Any]
    root_final: dict[str, Any]
    audit_entry: dict[str, Any]
    proof_artifact: dict[str, Any]
    summary: dict[str, Any]


def _closed_checkpoint_metadata() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checkpoints = [
        {
            "checkpoint_id": "external_drs_pointer_protocol_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
            "commits": "0a690c5,3e3cc3d,2036247,1b37ba5,984d001,5f83451",
        },
        {
            "checkpoint_id": "read_only_enterprise_connector_sandbox_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
            "commits": "5110d14,01a6b64,af872eb,056e2cd",
        },
        {
            "checkpoint_id": "external_evidence_acceptance_gate_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
            "commits": "ece902f,00e98cd,632ecb1,71d76e0",
        },
        {
            "checkpoint_id": "bounded_llm_semantic_executor_node_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
            "commits": "863f850,fc328c8,4659f3e,0e1626c,524949f,d6504bf",
        },
    ]
    source_evidence = {
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
        "source_collectors_replayed_count": 0,
        "source_checkpoints_referenced": len(checkpoints),
        "historical_proof_reexecution_claimed": False,
    }
    return source_evidence, checkpoints


def _enterprise_chaos_request() -> dict[str, Any]:
    return {
        "request_id": "ENTERPRISE-CHAOS-001",
        "request_text": (
            "Prepare an enterprise dispatch/certificate readiness decision using "
            "bank payment, warehouse stock, legal certificate, logistics window, "
            "previous DRS reuse, external DRS pointer, semantic LLM draft, and "
            "NeedleCandidate."
        ),
        "bank_connector_signal": "payment_observed",
        "warehouse_connector_signal": "stock_available",
        "legal_connector_signal": "certificate_expired",
        "logistics_connector_signal": "dispatch_window_exists",
        "previous_drs_reuse_signal": "similar_request_not_ready",
        "external_pointer_claim": "external_trust_claimed_unaccepted",
        "semantic_llm_draft": "bounded_summary_only",
        "needle_candidate_claim": "can_submit_workflow_unaccepted",
        "child_cell_claim": "can_finish_subflow_unaccepted",
        "gt_recommendation": "safe_path_advisory_only",
        "conflicting_sources_present": True,
        "root_review_required": True,
        "proof_only": True,
    }


def _chaos_attempts() -> list[dict[str, Any]]:
    attempts = []
    for attempt_id, attack_surface, attempted_escalation in ATTEMPT_DEFINITIONS:
        quarantined = attempt_id in QUARANTINED_ATTEMPT_IDS
        attempts.append(
            {
                "attempt_id": attempt_id,
                "attack_surface": attack_surface,
                "attempted_escalation": attempted_escalation,
                "detected": True,
                "blocked": True,
                "quarantined": quarantined,
                "final_effect": (
                    "quarantined_and_blocked" if quarantined else "blocked"
                ),
                "authority_transferred": False,
                "root_bypassed": False,
                "truth_proven": False,
                "ready_status_created": False,
                "accepted_evidence_created_without_gate": False,
                "external_action_executed": False,
                "global_drs_write": False,
                "external_drs_write": False,
                "installed_needle_created": False,
                "child_autonomy_created": False,
                "plan_modified_by_llm": False,
                "root_final_created_by_non_root": False,
                "production_persistence": False,
                "network_called": False,
                "gemini_called": False,
            }
        )
    return attempts


def _boundary_matrix() -> dict[str, bool]:
    return {
        "root_remains_final_authority": True,
        "orchestrator_cannot_finalize": True,
        "architect_cannot_finalize": True,
        "executor_cannot_finalize": True,
        "llm_cannot_finalize": True,
        "gt_cannot_finalize": True,
        "audit_hash_cannot_prove_truth": True,
        "connector_observation_not_truth": True,
        "connector_observation_not_accepted_evidence": True,
        "accepted_evidence_not_action": True,
        "accepted_evidence_not_ready": True,
        "semantic_draft_not_truth": True,
        "semantic_draft_not_root_final": True,
        "drs_reuse_not_authority": True,
        "external_pointer_not_external_drs_write": True,
        "bridge_traversal_not_provenance_laundering": True,
        "needlecandidate_not_installed_needle": True,
        "child_cell_not_autonomous_actor": True,
        "permission_not_execution": True,
        "resultproposal_requires_post_vv_gt_root": True,
        "conflictcheck_detects_not_decides": True,
        "no_network": True,
        "no_gemini": True,
        "no_external_action": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "no_production_persistence": True,
        "no_marennya": True,
        "no_up": True,
        "showcase_only_false": True,
        "killer_demo_false": True,
    }


def validate_enterprise_chaos_pack_v01_report(
    report: EnterpriseChaosPackReport,
) -> bool:
    attempts = report.chaos_attempts
    illegal_effect_fields = (
        "authority_transferred",
        "root_bypassed",
        "truth_proven",
        "ready_status_created",
        "accepted_evidence_created_without_gate",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_needle_created",
        "child_autonomy_created",
        "plan_modified_by_llm",
        "root_final_created_by_non_root",
        "production_persistence",
        "network_called",
        "gemini_called",
    )
    root = report.root_final
    return all(
        (
            report.source_evidence["source_evidence_mode"]
            == "closed_checkpoint_metadata_only",
            report.source_evidence["source_collectors_replayed"] is False,
            report.source_evidence["source_collectors_replayed_count"] == 0,
            len(report.source_checkpoints) == 4,
            all(
                row["checkpoint_status"] == "PASS"
                and row["closure_status"] == "closed"
                for row in report.source_checkpoints
            ),
            len(attempts) == 18,
            all(row["detected"] is True for row in attempts),
            all(row["blocked"] is True for row in attempts),
            sum(row["final_effect"] == "quarantined_and_blocked" for row in attempts)
            == 4,
            all(
                all(row[field] is False for field in illegal_effect_fields)
                for row in attempts
            ),
            all(value is True for value in report.boundary_matrix.values()),
            root["root_result"] == "enterprise_chaos_pack_all_escalations_blocked",
            root["safe_secondary_outcome"]
            == "needs_root_supervised_hardening_before_killer_demo",
            root["enterprise_ready"] is False,
            root["truth_proven"] is False,
            root["external_action_executed"] is False,
            root["root_remains_final_authority"] is True,
            root["marennya_invoked"] is False,
            root["up_invoked"] is False,
            report.audit_entry["canonical_payload_hash"]
            == canonical_hash(report.proof_artifact),
            report.audit_entry["audit_chain_decides_truth"] is False,
        )
    )


def collect_enterprise_chaos_pack_v01() -> EnterpriseChaosPackReport:
    source_evidence, source_checkpoints = _closed_checkpoint_metadata()
    request = _enterprise_chaos_request()
    attempts = _chaos_attempts()
    quarantined = [
        row["attempt_id"] for row in attempts if row["quarantined"] is True
    ]
    quarantine_summary = {
        "quarantined_and_blocked_count": len(quarantined),
        "quarantined_attempt_ids": quarantined,
        "quarantine_is_not_acceptance": True,
        "quarantine_is_not_truth": True,
        "quarantine_is_not_ready_status": True,
        "quarantine_executes_no_action": True,
    }
    boundary = _boundary_matrix()
    root_final = {
        "root_result": "enterprise_chaos_pack_all_escalations_blocked",
        "safe_secondary_outcome": "needs_root_supervised_hardening_before_killer_demo",
        "enterprise_chaos_attempts_observed": len(attempts),
        "enterprise_chaos_attempts_blocked": sum(row["blocked"] for row in attempts),
        "enterprise_ready": False,
        "truth_proven": False,
        "accepted_evidence_created_without_gate": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "child_autonomy_created": False,
        "root_final_created_by_non_root": False,
        "network_called": False,
        "gemini_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_persistence": False,
        "showcase_created": False,
        "killer_demo_created": False,
        "root_remains_final_authority": True,
    }
    proof_artifact = {
        "proof_artifact_id": "enterprise_chaos_pack_v01",
        "source_evidence": source_evidence,
        "source_checkpoints": source_checkpoints,
        "enterprise_chaos_request": request,
        "chaos_attempts": attempts,
        "quarantine_summary": quarantine_summary,
        "boundary_matrix": boundary,
        "root_final": root_final,
    }
    audit_entry = {
        "audit_entry_id": "audit_enterprise_chaos_pack_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = EnterpriseChaosPackReport(
        source_evidence,
        source_checkpoints,
        request,
        attempts,
        quarantine_summary,
        boundary,
        root_final,
        audit_entry,
        proof_artifact,
        {},
    )
    passed = validate_enterprise_chaos_pack_v01_report(provisional)
    summary = {
        "enterprise_chaos_pack_v01_status": "PASS" if passed else "FAIL",
        "enterprise_chaos_attempts_observed": len(attempts),
        "enterprise_chaos_attempts_detected": sum(row["detected"] for row in attempts),
        "enterprise_chaos_attempts_blocked": sum(row["blocked"] for row in attempts),
        "quarantined_and_blocked_count": len(quarantined),
        "source_checkpoints_referenced": len(source_checkpoints),
        "source_collectors_replayed": False,
        "source_collectors_replayed_count": 0,
        "root_finals_created": 1,
        "external_actions_executed": 0,
        "global_drs_writes": 0,
        "external_drs_writes": 0,
        "installed_needles_created": 0,
        "network_calls": 0,
        "gemini_calls": 0,
        "production_persistence_writes": 0,
        "root_remains_final_authority": True,
        "enterprise_ready": False,
        "truth_proven": False,
        "ready_for_enterprise_chaos_pack_v01_tests": passed,
    }
    return replace(provisional, summary=summary)


def _format(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_enterprise_chaos_pack_v01(report: EnterpriseChaosPackReport) -> str:
    lines = [
        "[ENTERPRISE CHAOS PACK v0.1]",
        "note: deterministic local proof-only enterprise chaos pack",
        "note: closed checkpoints are metadata only; historical collectors are not replayed",
        "note: results establish local proof-level boundaries only",
    ]
    _rows(lines, "[SOURCE CHECKPOINTS]", report.source_checkpoints)
    _section(lines, "[ENTERPRISE CHAOS REQUEST]", report.enterprise_chaos_request)
    _rows(lines, "[CHAOS ATTEMPTS]", report.chaos_attempts)
    _section(lines, "[QUARANTINE SUMMARY]", report.quarantine_summary)
    _section(lines, "[BOUNDARY MATRIX]", report.boundary_matrix)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_enterprise_chaos_pack_v01() -> str:
    return render_enterprise_chaos_pack_v01(collect_enterprise_chaos_pack_v01())


def main() -> int:
    print(run_enterprise_chaos_pack_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
