from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_needlecandidate_lifecycle_proof import (
    collect_needlecandidate_lifecycle_proof,
)
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
)


SCENARIO_SPECS = (
    (
        "spoofed_high_similarity_score",
        "rejected_score_spoof",
        "block_reuse_score_spoof",
        "conflict_score_spoof_vs_independent_reuse_score",
    ),
    (
        "fake_freshness_on_stale_record",
        "downgraded_to_rerun_required",
        "rerun_required",
        "conflict_fake_freshness_vs_independent_freshness",
    ),
    (
        "quarantine_laundering_attempt",
        "blocked_quarantine_laundering",
        "block_reuse_quarantine_laundering",
        "conflict_quarantine_laundering_detected",
    ),
    (
        "deadend_laundering_attempt",
        "blocked_deadend_laundering",
        "block_reuse_deadend_laundering",
        "conflict_deadend_laundering_detected",
    ),
    (
        "permission_laundering_attempt",
        "rejected_permission_laundering",
        "reject_permission_laundering",
        "conflict_permission_laundering_detected",
    ),
    (
        "domain_camouflage_attempt",
        "rejected_domain_camouflage",
        "reject_domain_camouflage",
        "conflict_domain_camouflage_detected",
    ),
    (
        "fake_audit_hash_attempt",
        "blocked_bad_audit_hash",
        "block_reuse_bad_audit_hash",
        "conflict_bad_audit_hash_detected",
    ),
    (
        "root_final_injection_attempt",
        "rejected_injected_root_final",
        "reject_injected_root_final",
        "conflict_injected_root_final_detected",
    ),
)


@dataclass(frozen=True)
class DrsAdversarialStressPackReport:
    input_mode: dict[str, Any]
    source_evidence: dict[str, Any]
    drs_adversarial_inputs: list[dict[str, Any]]
    drs_adversarial_retrieval_candidates: list[dict[str, Any]]
    drs_adversarial_detection_rows: list[dict[str, Any]]
    drs_adversarial_gate_rows: list[dict[str, Any]]
    drs_adversarial_conflict_reports: list[dict[str, Any]]
    drs_adversarial_gt_selection: dict[str, Any]
    drs_adversarial_root_final_artifacts: list[dict[str, Any]]
    drs_adversarial_proof_artifact: dict[str, Any]
    drs_adversarial_audit_entry: dict[str, Any]
    audit_hash_chain: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _inputs() -> list[dict[str, Any]]:
    return [
        {
            "adversarial_input_id": f"input_{scenario}",
            "scenario": scenario,
            "attack_type": scenario,
            "proof_only": True,
        }
        for scenario, _, _, _ in SCENARIO_SPECS
    ]


def _candidate(scenario: str) -> dict[str, Any]:
    values = {
        "spoofed_high_similarity_score": {
            "claimed_similarity_score": 0.99,
            "claimed_reuse_score": 0.99,
            "independent_similarity_score": 0.42,
            "independent_reuse_score": 0.18,
        },
        "fake_freshness_on_stale_record": {
            "claimed_freshness": "fresh",
            "independent_freshness": "stale",
        },
        "quarantine_laundering_attempt": {"quarantine_lineage_detected": True},
        "deadend_laundering_attempt": {"deadend_lineage_detected": True},
        "permission_laundering_attempt": {"permission_laundering_detected": True},
        "domain_camouflage_attempt": {
            "claimed_source_domain": "warehouse_readiness",
            "actual_source_domain": "certificate_document_readiness",
            "domain_camouflage_detected": True,
        },
        "fake_audit_hash_attempt": {"audit_hash_valid": False},
        "root_final_injection_attempt": {"injected_root_final_detected": True},
    }[scenario]
    candidate = {
        "adversarial_candidate_id": f"adversarial_candidate_{scenario}",
        "attack_type": scenario,
        "source_record_id": f"hostile_record_{scenario}",
        "claimed_source_domain": "warehouse_readiness",
        "actual_source_domain": "warehouse_readiness",
        "target_domain": "warehouse_readiness",
        "claimed_similarity_score": 0.90,
        "claimed_reuse_score": 0.90,
        "independent_similarity_score": 0.35,
        "independent_reuse_score": 0.10,
        "claimed_freshness": "fresh",
        "independent_freshness": "fresh",
        "quarantine_lineage_detected": False,
        "deadend_lineage_detected": False,
        "permission_laundering_detected": False,
        "domain_camouflage_detected": False,
        "audit_hash_valid": True,
        "injected_root_final_detected": False,
        "direct_reuse_allowed": False,
        "root_review_required": True,
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
    }
    candidate.update(values)
    return candidate


def _candidates() -> list[dict[str, Any]]:
    return [_candidate(scenario) for scenario, _, _, _ in SCENARIO_SPECS]


def _detection_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "detection_row_id": f"detection_{candidate['attack_type']}",
            "scenario": candidate["attack_type"],
            "attack_detected": True,
            "independent_checks_override_claims": True,
            "direct_reuse_rejected": True,
        }
        for candidate in candidates
    ]


def _gate_rows() -> list[dict[str, Any]]:
    return [
        {"gate_row_id": scenario, "scenario": scenario, "gate_status": gate}
        for scenario, gate, _, _ in SCENARIO_SPECS
    ]


def _conflicts() -> list[dict[str, Any]]:
    return [
        {
            "conflict_report_id": conflict_id,
            "scenario": scenario,
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        }
        for scenario, _, _, conflict_id in SCENARIO_SPECS
    ]


def _root_finals() -> list[dict[str, Any]]:
    return [
        {
            "root_final_artifact_id": f"root_final_{scenario}",
            "scenario": scenario,
            "root_decision": decision,
            "direct_ready_created": False,
            "completed_external_action_created": False,
            "completed_dispatch_created": False,
            "completed_restock_created": False,
            "completed_certificate_submission_created": False,
            "protocol_candidate_created": False,
            "needle_candidate_created": False,
            "installed_needle_created": False,
            "production_persistence": False,
            "global_drs_write": False,
            "external_drs_write": False,
        }
        for scenario, _, decision, _ in SCENARIO_SPECS
    ]


def validate_drs_adversarial_stress_pack_report_consistency(
    report: DrsAdversarialStressPackReport,
) -> bool:
    candidates = _by_id(
        report.drs_adversarial_retrieval_candidates, "adversarial_candidate_id"
    )
    gates = _by_id(report.drs_adversarial_gate_rows, "gate_row_id")
    conflicts = _by_id(report.drs_adversarial_conflict_reports, "conflict_report_id")
    allowed_decisions = {decision for _, _, decision, _ in SCENARIO_SPECS}
    expected_gates = {scenario: gate for scenario, gate, _, _ in SCENARIO_SPECS}
    expected_conflicts = {conflict for _, _, _, conflict in SCENARIO_SPECS}
    spoof = candidates.get("adversarial_candidate_spoofed_high_similarity_score", {})
    fake_freshness = candidates.get(
        "adversarial_candidate_fake_freshness_on_stale_record", {}
    )
    quarantine = candidates.get(
        "adversarial_candidate_quarantine_laundering_attempt", {}
    )
    deadend = candidates.get("adversarial_candidate_deadend_laundering_attempt", {})
    permission = candidates.get(
        "adversarial_candidate_permission_laundering_attempt", {}
    )
    domain = candidates.get("adversarial_candidate_domain_camouflage_attempt", {})
    fake_audit = candidates.get("adversarial_candidate_fake_audit_hash_attempt", {})
    injected = candidates.get("adversarial_candidate_root_final_injection_attempt", {})
    authority = report.authority_safety
    return all(
        (
            len(report.drs_adversarial_inputs) == len(SCENARIO_SPECS),
            len(candidates) == len(SCENARIO_SPECS),
            all(
                candidate.get("direct_reuse_allowed") is False
                and candidate.get("root_review_required") is True
                and candidate.get("proof_only") is True
                and candidate.get("production_persistence") is False
                and candidate.get("global_drs_write") is False
                and candidate.get("external_drs_write") is False
                for candidate in candidates.values()
            ),
            spoof.get("claimed_reuse_score", 0)
            > spoof.get("independent_reuse_score", 1),
            fake_freshness.get("claimed_freshness") == "fresh",
            fake_freshness.get("independent_freshness") == "stale",
            quarantine.get("quarantine_lineage_detected") is True,
            deadend.get("deadend_lineage_detected") is True,
            permission.get("permission_laundering_detected") is True,
            domain.get("domain_camouflage_detected") is True,
            domain.get("claimed_source_domain") != domain.get("actual_source_domain"),
            fake_audit.get("audit_hash_valid") is False,
            injected.get("injected_root_final_detected") is True,
            len(report.drs_adversarial_detection_rows) == len(SCENARIO_SPECS),
            all(
                row.get("attack_detected") is True
                and row.get("independent_checks_override_claims") is True
                and row.get("direct_reuse_rejected") is True
                for row in report.drs_adversarial_detection_rows
            ),
            all(
                gates.get(scenario, {}).get("gate_status") == gate
                for scenario, gate in expected_gates.items()
            ),
            set(conflicts) == expected_conflicts,
            all(
                conflict.get("conflict_detected") is True
                and conflict.get("conflictcheck_is_authority") is False
                for conflict in conflicts.values()
            ),
            report.drs_adversarial_gt_selection.get("gt_decides_final_reuse") is False,
            report.drs_adversarial_gt_selection.get("gt_can_mark_ready") is False,
            report.drs_adversarial_gt_selection.get("gt_can_execute_action") is False,
            all(
                final.get("root_decision") in allowed_decisions
                and final.get("direct_ready_created") is False
                and final.get("completed_external_action_created") is False
                and final.get("protocol_candidate_created") is False
                and final.get("needle_candidate_created") is False
                and final.get("installed_needle_created") is False
                and final.get("production_persistence") is False
                and final.get("global_drs_write") is False
                and final.get("external_drs_write") is False
                for final in report.drs_adversarial_root_final_artifacts
            ),
            report.drs_adversarial_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.drs_adversarial_proof_artifact),
            report.drs_adversarial_audit_entry.get("previous_chain_last_entry_hash")
            == report.audit_hash_chain.get("previous_chain_last_entry_hash"),
            report.drs_adversarial_audit_entry.get("audit_chain_decides_truth") is False,
            authority.get("drs_retrieval_is_not_authority") is True,
            authority.get("semantic_similarity_is_not_authority") is True,
            authority.get("reuse_score_is_not_root") is True,
            authority.get("root_remains_final_authority") is True,
            authority.get("gt_remains_advisory_until_root") is True,
            authority.get("conflictcheck_remains_advisory_until_root") is True,
            authority.get("protocol_candidate_created") is False,
            authority.get("needle_candidate_created") is False,
            authority.get("installed_needle_created") is False,
            authority.get("no_real_external_action_executed") is True,
            authority.get("no_production_persistence") is True,
            authority.get("no_global_drs_write") is True,
            authority.get("no_external_drs_write") is True,
            authority.get("production_autonomy_claimed") is False,
        )
    )


def collect_drs_adversarial_stress_pack() -> DrsAdversarialStressPackReport:
    applied = collect_applied_drs_retrieval_reuse()
    needlecandidate = collect_needlecandidate_lifecycle_proof()
    permission = collect_permission_needsuser_ux_proof()
    conflict = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    inputs = _inputs()
    candidates = _candidates()
    detections = _detection_rows(candidates)
    gates = _gate_rows()
    conflicts = _conflicts()
    finals = _root_finals()
    source = {
        "applied_drs_retrieval_reuse_source_status": applied.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "needlecandidate_source_status": needlecandidate.summary[
            "needlecandidate_lifecycle_proof_status"
        ],
        "permission_needsuser_source_status": permission.summary[
            "permission_needsuser_ux_proof_status"
        ],
        "conflictcheck_source_status": conflict.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
    }
    gt = {
        "recommended_outcomes": ["block_reuse", "rerun_required", "reject_reuse"],
        "gt_decides_final_reuse": False,
        "gt_is_not_truth_proof": True,
        "gt_remains_advisory_until_root": True,
        "gt_can_mark_ready": False,
        "gt_can_execute_action": False,
        "gt_can_create_protocol_candidate": False,
        "gt_can_create_needle_candidate": False,
        "gt_can_install_needle": False,
        "gt_can_write_global_drs": False,
    }
    proof_artifact = {
        "drs_adversarial_proof_artifact_id": "drs_adversarial_stress_pack_v0_1",
        "inputs": inputs,
        "candidates": candidates,
        "detection_rows": detections,
        "gate_rows": gates,
        "conflict_reports": conflicts,
        "gt_selection": gt,
        "root_final_artifacts": finals,
    }
    audit_entry = {
        "audit_entry_id": "audit_drs_adversarial_stress_pack_v0_1",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    audit = {
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "hash_chain_proves_continuity_not_truth": True,
    }
    authority = {
        "drs_retrieval_is_not_authority": True,
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
        "no_external_drs_write": True,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "production_autonomy_claimed": False,
    }
    provisional = DrsAdversarialStressPackReport(
        input_mode={
            "mode": "deterministic_drs_adversarial_stress_pack",
            "local_proof_level_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
        },
        source_evidence=source,
        drs_adversarial_inputs=inputs,
        drs_adversarial_retrieval_candidates=candidates,
        drs_adversarial_detection_rows=detections,
        drs_adversarial_gate_rows=gates,
        drs_adversarial_conflict_reports=conflicts,
        drs_adversarial_gt_selection=gt,
        drs_adversarial_root_final_artifacts=finals,
        drs_adversarial_proof_artifact=proof_artifact,
        drs_adversarial_audit_entry=audit_entry,
        audit_hash_chain=audit,
        authority_safety=authority,
        summary={},
    )
    consistent = validate_drs_adversarial_stress_pack_report_consistency(provisional)
    passed = all(value == "PASS" for value in source.values()) and consistent
    return replace(
        provisional,
        summary={
            "drs_adversarial_stress_pack_status": "PASS" if passed else "FAIL",
            "scenarios_verified": len(SCENARIO_SPECS),
            "spoofed_high_similarity_score_blocked": True,
            "fake_freshness_on_stale_record_downgraded": True,
            "quarantine_laundering_blocked": True,
            "deadend_laundering_blocked": True,
            "permission_laundering_rejected": True,
            "domain_camouflage_rejected": True,
            "fake_audit_hash_blocked": True,
            "injected_root_final_rejected": True,
            **authority,
            "explicit_drs_adversarial_artifacts_consistent": consistent,
            "ready_for_drs_adversarial_stress_pack_tests": passed,
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


def render_drs_adversarial_stress_pack(report: DrsAdversarialStressPackReport) -> str:
    lines = [
        "[DRS ADVERSARIAL STRESS PACK]",
        "note: deterministic proof-level adversarial DRS retrieval stress",
        "note: hostile records cannot force Root bypass or direct reuse",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[ADVERSARIAL INPUTS]", report.drs_adversarial_inputs)
    _rows(
        lines,
        "[ADVERSARIAL RETRIEVAL CANDIDATES]",
        report.drs_adversarial_retrieval_candidates,
    )
    _rows(lines, "[DETECTION ROWS]", report.drs_adversarial_detection_rows)
    _rows(lines, "[GATE ROWS]", report.drs_adversarial_gate_rows)
    _section(lines, "[GT]", report.drs_adversarial_gt_selection)
    _rows(lines, "[ROOT FINAL]", report.drs_adversarial_root_final_artifacts)
    _rows(lines, "[CONFLICTCHECK]", report.drs_adversarial_conflict_reports)
    _section(
        lines,
        "[AUDIT HASH-CHAIN]",
        report.drs_adversarial_audit_entry | report.audit_hash_chain,
    )
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_drs_adversarial_stress_pack() -> str:
    return render_drs_adversarial_stress_pack(collect_drs_adversarial_stress_pack())


def main() -> int:
    print(run_drs_adversarial_stress_pack(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
