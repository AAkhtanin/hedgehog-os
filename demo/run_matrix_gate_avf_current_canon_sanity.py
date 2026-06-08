from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_avf_attractor_from_accepted_matrix import (
    collect_avf_attractor_from_accepted_matrix,
)
from demo.run_controlled_orchestrator_matrix_gate import (
    collect_controlled_orchestrator_matrix_gate,
)
from demo.run_drs_writeback_from_root_final import (
    collect_drs_writeback_from_root_final,
)


LIVE_EVIDENCE_PATH = (
    "docs/audit_reports/auditor_live_dual_gemini_full_chain_smoke_LOCAL_PASS.log"
)
LIVE_EVIDENCE_MARKERS = {
    "live_dual_gemini_full_chain_smoke_status": (
        "live_dual_gemini_full_chain_smoke_status: PASS"
    ),
    "both_gemini_roles_live": "both_gemini_roles_live: true",
    "orchestrator_fallback_used": "orchestrator_fallback_used: false",
    "architect_fallback_used": "architect_fallback_used: false",
    "one_continuous_chain": "one_continuous_chain: true",
    "root_is_only_final_output_authority": "root_is_only_final_output_authority: true",
}


@dataclass(frozen=True)
class MatrixGateAvfCurrentCanonSanityReport:
    input_mode: dict[str, Any]
    matrix_gate_source: dict[str, Any]
    avf_source: dict[str, Any]
    drs_boundary_reference: dict[str, Any]
    live_dual_gemini_evidence_reference: dict[str, Any]
    current_canon_checks: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _scenario_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario"]: row for row in rows}


def _matrix_gate_source(report: Any) -> dict[str, Any]:
    decisions = _scenario_rows(report.gate_decisions)
    valid = decisions["valid_matrix_accept"]
    temporal = decisions["missing_temporal_query_reject"]
    guards = decisions["incomplete_guards_downgrade_or_reject"]
    actors = decisions["wrong_downstream_actors_reject"]
    bypass = decisions["forbidden_bypass_reject"]
    rejected = [row for row in report.gate_decisions if row["gate_decision"] == "reject"]
    source_checks_passed = (
        report.summary["controlled_orchestrator_matrix_gate_status"] == "PASS"
        and valid["gate_decision"] == "accept"
        and temporal["gate_decision"] == "reject"
        and "missing_or_false_temporal_query" in temporal["rejection_reasons"]
        and guards["gate_decision"] in {"downgrade", "reject"}
        and bool(guards["missing_guards"])
        and actors["gate_decision"] == "reject"
        and bool(actors["missing_downstream_actors"])
        and bool(actors["extra_downstream_actors"])
        and bypass["gate_decision"] == "reject"
        and bypass["forbidden_bypass_detected"]
    )
    return {
        "source_collector": "collect_controlled_orchestrator_matrix_gate",
        "controlled_orchestrator_matrix_gate_status": report.summary[
            "controlled_orchestrator_matrix_gate_status"
        ],
        "accepted_count": report.summary["accepted_count"],
        "rejected_count": report.summary["rejected_count"],
        "downgraded_count": report.summary["downgraded_count"],
        "source_checks_passed": source_checks_passed,
        "root_authority_preserved": report.summary["root_authority_preserved"],
        "root_created_gate_decisions": report.root_authority[
            "root_created_gate_decisions"
        ],
        "orchestrator_matrix_is_authority": report.root_authority[
            "orchestrator_matrix_is_authority"
        ],
        "rejected_matrix_reaches_avf": any(row["avf_invoked"] for row in rejected),
        "orchestrator_creates_final_output": report.boundary_checks[
            "orchestrator_created_final_output"
        ],
        "orchestrator_writes_drs": report.boundary_checks["orchestrator_wrote_drs"],
        "orchestrator_executes_actions": report.boundary_checks[
            "production_external_action_executed"
        ],
    }


def _avf_source(report: Any) -> dict[str, Any]:
    packets = report.attractor_packets
    forbidden_vectors_passed = any(
        bool(set(packet["forbidden_vector_classes"]) & set(packet["allowed_vectors"]))
        or not set(packet["forbidden_vector_classes"]).issubset(
            set(packet["hardmask_blocks"])
        )
        for packet in packets
    )
    architect_input_bounded = bool(packets) and all(
        packet["architect_input_bounded"] for packet in packets
    )
    return {
        "source_collector": "collect_avf_attractor_from_accepted_matrix",
        "avf_attractor_from_accepted_matrix_status": report.summary[
            "avf_attractor_from_accepted_matrix_status"
        ],
        "source_matrix_gate_status": report.summary["source_matrix_gate_status"],
        "attractor_packets_created": report.summary["attractor_packets_created"],
        "rejected_matrices_blocked_before_avf": report.summary[
            "rejected_matrices_blocked_before_avf"
        ],
        "avf_independent": report.authority_safety["avf_independent"],
        "hardmask_beats_orchestrator_confidence": report.authority_safety[
            "hardmask_beats_orchestrator_confidence"
        ],
        "policy_beats_orchestrator_confidence": report.authority_safety[
            "policy_beats_orchestrator_confidence"
        ],
        "forbidden_vectors_passed_to_architect": forbidden_vectors_passed,
        "architect_input_bounded": architect_input_bounded,
        "avf_creates_final_output": report.authority_safety[
            "avf_creates_final_output"
        ],
        "avf_writes_drs": report.authority_safety["avf_writes_drs"],
        "avf_executes_actions": report.authority_safety["avf_executes_actions"],
    }


def _drs_boundary_reference(report: Any) -> dict[str, Any]:
    summary = report.summary
    authority = report.authority_safety
    return {
        "source_collector": "collect_drs_writeback_from_root_final",
        "drs_writeback_from_root_final_status": summary[
            "drs_writeback_from_root_final_status"
        ],
        "writeback_scope_local_audit_only": summary[
            "writeback_scope_local_audit_only"
        ],
        "drs_is_authority": authority["drs_is_authority"],
        "root_authority_preserved": summary["root_authority_preserved"],
        "production_persistence_claimed": summary["production_persistence_claimed"],
        "production_external_action_executed": summary[
            "production_external_action_executed"
        ],
        "external_drs_network_implemented": authority[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": authority["global_drs_implemented"],
        "root_writes_drs_claim_rejected": summary[
            "malicious_root_drs_write_claim_rejected"
        ],
        "production_persistence_claim_rejected": summary[
            "malicious_production_persistence_claim_rejected"
        ],
        "external_drs_network_claim_rejected": summary[
            "malicious_external_drs_network_claim_rejected"
        ],
    }


def _live_evidence_reference(path: str = LIVE_EVIDENCE_PATH) -> dict[str, Any]:
    report_path = Path(path)
    available = report_path.exists()
    text = report_path.read_text(encoding="utf-8") if available else ""
    marker_results = {
        key: marker in text for key, marker in LIVE_EVIDENCE_MARKERS.items()
    }
    return {
        "live_evidence_available": available,
        "live_evidence_path": path,
        **(
            {
                "live_dual_gemini_full_chain_smoke_status": (
                    "PASS"
                    if marker_results["live_dual_gemini_full_chain_smoke_status"]
                    else "UNVERIFIED"
                ),
                "both_gemini_roles_live": marker_results["both_gemini_roles_live"],
                "orchestrator_fallback_used": not marker_results[
                    "orchestrator_fallback_used"
                ],
                "architect_fallback_used": not marker_results[
                    "architect_fallback_used"
                ],
                "one_continuous_chain": marker_results["one_continuous_chain"],
                "root_is_only_final_output_authority": marker_results[
                    "root_is_only_final_output_authority"
                ],
                "live_evidence_verified": all(marker_results.values()),
            }
            if available
            else {"live_evidence_verified": False}
        ),
        "live_evidence_used_as_runtime_input": False,
    }


def _current_canon_checks(
    matrix: dict[str, Any],
    avf: dict[str, Any],
    drs: dict[str, Any],
) -> dict[str, Any]:
    matrix_current = (
        matrix["controlled_orchestrator_matrix_gate_status"] == "PASS"
        and matrix["source_checks_passed"]
        and matrix["root_authority_preserved"]
        and matrix["root_created_gate_decisions"]
        and not matrix["orchestrator_matrix_is_authority"]
    )
    avf_current = (
        avf["avf_attractor_from_accepted_matrix_status"] == "PASS"
        and avf["source_matrix_gate_status"] == "PASS"
        and avf["rejected_matrices_blocked_before_avf"]
        and avf["avf_independent"]
        and avf["hardmask_beats_orchestrator_confidence"]
        and avf["policy_beats_orchestrator_confidence"]
        and not avf["forbidden_vectors_passed_to_architect"]
        and avf["architect_input_bounded"]
    )
    drs_current = (
        drs["drs_writeback_from_root_final_status"] == "PASS"
        and drs["writeback_scope_local_audit_only"]
        and not drs["drs_is_authority"]
        and drs["root_authority_preserved"]
    )
    return {
        "matrix_gate_current_after_live_gemini": matrix_current,
        "avf_current_after_live_gemini": avf_current,
        "matrix_gate_current_after_drs_writeback_boundary": matrix_current and drs_current,
        "avf_current_after_drs_writeback_boundary": avf_current and drs_current,
        "no_orchestrator_authority_leak": not matrix["orchestrator_matrix_is_authority"],
        "no_avf_bypass": matrix["rejected_matrix_reaches_avf"] is False
        and avf["rejected_matrices_blocked_before_avf"],
        "no_forbidden_vector_leak_to_architect": not avf[
            "forbidden_vectors_passed_to_architect"
        ],
        "no_drs_authority_leak": drs["drs_is_authority"] is False,
        "no_production_persistence_leak": drs["production_persistence_claimed"] is False
        and drs["production_persistence_claim_rejected"],
        "no_external_global_drs_leak": drs["external_drs_network_implemented"] is False
        and drs["global_drs_implemented"] is False
        and drs["external_drs_network_claim_rejected"],
        "no_root_writes_drs_claim_leak": matrix["orchestrator_writes_drs"] is False
        and avf["avf_writes_drs"] is False
        and drs["root_writes_drs_claim_rejected"],
        "no_real_action_leak": matrix["orchestrator_executes_actions"] is False
        and avf["avf_executes_actions"] is False
        and drs["production_external_action_executed"] is False,
    }


def collect_matrix_gate_avf_current_canon_sanity() -> MatrixGateAvfCurrentCanonSanityReport:
    gate_report = collect_controlled_orchestrator_matrix_gate()
    avf_report = collect_avf_attractor_from_accepted_matrix()
    drs_report = collect_drs_writeback_from_root_final()
    matrix = _matrix_gate_source(gate_report)
    avf = _avf_source(avf_report)
    drs = _drs_boundary_reference(drs_report)
    live = _live_evidence_reference()
    checks = _current_canon_checks(matrix, avf, drs)
    authority = {
        "root_remains_authority": matrix["root_authority_preserved"]
        and drs["root_authority_preserved"],
        "orchestrator_is_not_root": not matrix["orchestrator_matrix_is_authority"],
        "avf_is_not_root": avf["avf_independent"],
        "drs_is_not_root": not drs["drs_is_authority"],
        "matrix_is_proposal_only": matrix["source_checks_passed"],
        "attractor_packet_is_bounded_input_only": avf["architect_input_bounded"],
        "production_persistence_claimed": drs["production_persistence_claimed"],
        "production_external_action_executed": drs[
            "production_external_action_executed"
        ],
        "global_drs_implemented": drs["global_drs_implemented"],
        "external_drs_network_implemented": drs["external_drs_network_implemented"],
        "marennya_invoked": False,
        "up_invoked": False,
    }
    boundaries_pass = (
        all(checks.values())
        and authority["root_remains_authority"]
        and authority["orchestrator_is_not_root"]
        and authority["avf_is_not_root"]
        and authority["drs_is_not_root"]
        and authority["matrix_is_proposal_only"]
        and authority["attractor_packet_is_bounded_input_only"]
        and not authority["production_persistence_claimed"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
    )
    source_pass = (
        matrix["controlled_orchestrator_matrix_gate_status"] == "PASS"
        and avf["avf_attractor_from_accepted_matrix_status"] == "PASS"
        and drs["drs_writeback_from_root_final_status"] == "PASS"
    )
    status = "PASS" if source_pass and boundaries_pass else "FAIL"
    summary = {
        "matrix_gate_avf_current_canon_sanity_status": status,
        "matrix_gate_source_status": matrix[
            "controlled_orchestrator_matrix_gate_status"
        ],
        "avf_source_status": avf["avf_attractor_from_accepted_matrix_status"],
        "drs_boundary_reference_status": drs["drs_writeback_from_root_final_status"],
        "live_evidence_available": live["live_evidence_available"],
        "current_canon_checks_passed": all(checks.values()),
        "ready_for_root_native_sandbox_needleruntime_e2e": status == "PASS",
        "production_persistence_claimed": authority["production_persistence_claimed"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }
    return MatrixGateAvfCurrentCanonSanityReport(
        input_mode={
            "mode": "deterministic_sanity_check",
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
        },
        matrix_gate_source=matrix,
        avf_source=avf,
        drs_boundary_reference=drs,
        live_dual_gemini_evidence_reference=live,
        current_canon_checks=checks,
        authority_safety=authority,
        summary=summary,
    )


def _format_value(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format_value(value)}" for key, value in fields.items())


def render_matrix_gate_avf_current_canon_sanity(
    report: MatrixGateAvfCurrentCanonSanityReport,
) -> str:
    lines = [
        "[MATRIX GATE / AVF CURRENT CANON SANITY]",
        "note: deterministic sanity-check for existing Matrix Gate and AVF layers",
        "note: does not reimplement Matrix Gate",
        "note: does not reimplement AVF",
        "note: consumes existing collectors",
        "note: verifies current canon after live dual-Gemini and DRS writeback boundary",
        "note: no production persistence",
        "note: no external/global DRS",
        "note: no root_writes_drs",
        "note: no real external actions",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[MATRIX GATE SOURCE]", report.matrix_gate_source)
    _section(lines, "[AVF SOURCE]", report.avf_source)
    _section(lines, "[DRS BOUNDARY REFERENCE]", report.drs_boundary_reference)
    _section(
        lines,
        "[LIVE DUAL-GEMINI EVIDENCE REFERENCE]",
        report.live_dual_gemini_evidence_reference,
    )
    _section(lines, "[CURRENT CANON CHECKS]", report.current_canon_checks)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_matrix_gate_avf_current_canon_sanity() -> str:
    return render_matrix_gate_avf_current_canon_sanity(
        collect_matrix_gate_avf_current_canon_sanity()
    )


def main() -> int:
    print(run_matrix_gate_avf_current_canon_sanity(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
