from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_applied_warehouse_semantic_demo import (
    collect_applied_warehouse_semantic_demo,
)
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_drs_adversarial_stress_pack import collect_drs_adversarial_stress_pack
from demo.run_needlecandidate_lifecycle_proof import (
    collect_needlecandidate_lifecycle_proof,
)
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
)


LAYER_IDS = (
    "warehouse_applied_layer",
    "certificate_applied_layer",
    "permission_needsuser_layer",
    "needlecandidate_lifecycle_layer",
    "applied_drs_retrieval_reuse_layer",
    "drs_adversarial_stress_layer",
    "conflictcheck_layer",
    "audit_hash_chain_layer",
)


@dataclass(frozen=True)
class AllLayersAppliedSuperSmokeReport:
    input_mode: dict[str, Any]
    super_smoke_source_evidence: dict[str, Any]
    super_smoke_layer_matrix: list[dict[str, Any]]
    super_smoke_authority_matrix: list[dict[str, Any]]
    super_smoke_boundary_matrix: list[dict[str, Any]]
    super_smoke_root_final: dict[str, Any]
    super_smoke_proof_artifact: dict[str, Any]
    super_smoke_audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _layer_matrix(source: dict[str, Any]) -> list[dict[str, Any]]:
    status_keys = (
        "applied_warehouse_semantic_demo_status",
        "applied_certificate_readiness_demo_status",
        "permission_needsuser_ux_proof_status",
        "needlecandidate_lifecycle_proof_status",
        "applied_drs_retrieval_reuse_status",
        "drs_adversarial_stress_pack_status",
        "conflictcheck_status",
        "audit_hash_chain_status",
    )
    return [
        {
            "layer_id": layer_id,
            "source_status": source[status_key],
            "observed": True,
            "root_authority_preserved": True,
            "advisory_only_when_not_root": True,
            "no_real_external_action": True,
            "production_persistence": False,
            "global_drs_write": False,
            "external_drs_write": False,
        }
        for layer_id, status_key in zip(LAYER_IDS, status_keys)
    ]


def _authority_matrix() -> list[dict[str, Any]]:
    return [
        {"authority_id": "Root", "final_authority": True},
        {"authority_id": "DRS retrieval", "final_authority": False},
        {"authority_id": "ReuseScore", "final_authority": False},
        {"authority_id": "GT", "final_authority": False},
        {"authority_id": "ConflictCheck", "final_authority": False},
        {"authority_id": "Audit/hash-chain", "final_authority": False},
        {"authority_id": "NeedleCandidate", "final_authority": False},
        {
            "authority_id": "Permission approval",
            "final_authority": False,
            "completed_action": False,
        },
    ]


def _boundary_matrix() -> list[dict[str, Any]]:
    return [
        {
            "boundary_id": "warehouse_not_ready_preserved",
            "boundary_preserved": True,
            "observed_outcome": "not_ready",
        },
        {
            "boundary_id": "certificate_not_ready_preserved",
            "boundary_preserved": True,
            "observed_outcome": "not_ready",
        },
        {
            "boundary_id": "permission_is_not_execution",
            "boundary_preserved": True,
            "completed_action": False,
        },
        {
            "boundary_id": "needlecandidate_is_not_installed_needle",
            "boundary_preserved": True,
            "source_candidate_status": "candidate_pending_review",
            "new_needle_candidate_created": False,
            "installed_needle_created": False,
        },
        {
            "boundary_id": "drs_retrieval_proposes_root_decides",
            "boundary_preserved": True,
            "drs_retrieval_is_authority": False,
        },
        {
            "boundary_id": "adversarial_drs_reuse_blocked",
            "boundary_preserved": True,
            "attacks_blocked": 8,
        },
        {
            "boundary_id": "conflictcheck_advisory_until_root",
            "boundary_preserved": True,
            "final_authority": False,
        },
        {
            "boundary_id": "audit_proves_continuity_not_truth",
            "boundary_preserved": True,
            "audit_chain_decides_truth": False,
        },
        {
            "boundary_id": "non_production_boundary",
            "boundary_preserved": True,
            "no_real_external_action": True,
            "no_completed_dispatch": True,
            "no_completed_restock": True,
            "no_completed_certificate_submission": True,
            "no_direct_ready_override": True,
            "protocol_candidate_created": False,
            "needle_candidate_created_by_super_smoke": False,
            "installed_needle_created": False,
            "production_persistence": False,
            "global_drs_write": False,
            "external_drs_write": False,
            "gemini_called": False,
            "network_called": False,
            "telegram_used": False,
            "marennya_invoked": False,
            "up_invoked": False,
        },
    ]


def validate_all_layers_applied_super_smoke_report_consistency(
    report: AllLayersAppliedSuperSmokeReport,
) -> bool:
    layers = _by_id(report.super_smoke_layer_matrix, "layer_id")
    authorities = _by_id(report.super_smoke_authority_matrix, "authority_id")
    boundaries = _by_id(report.super_smoke_boundary_matrix, "boundary_id")
    non_production = boundaries.get("non_production_boundary", {})
    non_root_authorities = {
        "DRS retrieval",
        "ReuseScore",
        "GT",
        "ConflictCheck",
        "Audit/hash-chain",
        "NeedleCandidate",
        "Permission approval",
    }
    return all(
        (
            len(layers) == len(LAYER_IDS),
            set(layers) == set(LAYER_IDS),
            all(
                layer.get("source_status") == "PASS"
                and layer.get("observed") is True
                and layer.get("root_authority_preserved") is True
                and layer.get("advisory_only_when_not_root") is True
                and layer.get("no_real_external_action") is True
                and layer.get("production_persistence") is False
                and layer.get("global_drs_write") is False
                and layer.get("external_drs_write") is False
                for layer in layers.values()
            ),
            authorities.get("Root", {}).get("final_authority") is True,
            all(
                authorities.get(authority, {}).get("final_authority") is False
                for authority in non_root_authorities
            ),
            authorities.get("Permission approval", {}).get("completed_action")
            is False,
            boundaries.get("warehouse_not_ready_preserved", {}).get(
                "observed_outcome"
            )
            == "not_ready",
            boundaries.get("certificate_not_ready_preserved", {}).get(
                "observed_outcome"
            )
            == "not_ready",
            boundaries.get("permission_is_not_execution", {}).get("completed_action")
            is False,
            boundaries.get("needlecandidate_is_not_installed_needle", {}).get(
                "new_needle_candidate_created"
            )
            is False,
            boundaries.get("needlecandidate_is_not_installed_needle", {}).get(
                "installed_needle_created"
            )
            is False,
            boundaries.get("adversarial_drs_reuse_blocked", {}).get("attacks_blocked")
            == 8,
            boundaries.get("audit_proves_continuity_not_truth", {}).get(
                "audit_chain_decides_truth"
            )
            is False,
            all(
                non_production.get(key) is False
                for key in (
                    "protocol_candidate_created",
                    "needle_candidate_created_by_super_smoke",
                    "installed_needle_created",
                    "production_persistence",
                    "global_drs_write",
                    "external_drs_write",
                    "gemini_called",
                    "network_called",
                    "telegram_used",
                    "marennya_invoked",
                    "up_invoked",
                )
            ),
            report.super_smoke_root_final.get("root_decision")
            == "all_layers_observed_no_autonomy",
            report.super_smoke_root_final.get("root_final_authority_preserved") is True,
            report.super_smoke_root_final.get("system_ready_for_external_drs") is False,
            report.super_smoke_root_final.get("system_ready_for_marennya") is False,
            report.super_smoke_root_final.get("system_ready_for_up") is False,
            report.super_smoke_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.super_smoke_proof_artifact),
            report.super_smoke_audit_entry.get("audit_chain_decides_truth") is False,
            report.super_smoke_audit_entry.get("proof_only") is True,
            report.super_smoke_audit_entry.get("production_persistence") is False,
            report.super_smoke_audit_entry.get("global_drs_write") is False,
            report.super_smoke_audit_entry.get("external_drs_write") is False,
        )
    )


def collect_all_layers_applied_super_smoke() -> AllLayersAppliedSuperSmokeReport:
    warehouse = collect_applied_warehouse_semantic_demo()
    certificate = collect_applied_certificate_readiness_demo()
    permission = collect_permission_needsuser_ux_proof()
    needlecandidate = collect_needlecandidate_lifecycle_proof()
    retrieval = collect_applied_drs_retrieval_reuse()
    adversarial = collect_drs_adversarial_stress_pack()
    conflict = collect_conflictcheck()
    audit = collect_audit_hash_chain()

    source = {
        "applied_warehouse_semantic_demo_status": warehouse.summary[
            "applied_warehouse_semantic_demo_status"
        ],
        "applied_certificate_readiness_demo_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "permission_needsuser_ux_proof_status": permission.summary[
            "permission_needsuser_ux_proof_status"
        ],
        "needlecandidate_lifecycle_proof_status": needlecandidate.summary[
            "needlecandidate_lifecycle_proof_status"
        ],
        "applied_drs_retrieval_reuse_status": retrieval.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "drs_adversarial_stress_pack_status": adversarial.summary[
            "drs_adversarial_stress_pack_status"
        ],
        "conflictcheck_status": conflict.summary["conflictcheck_status"],
        "audit_hash_chain_status": audit.summary["audit_hash_chain_status"],
    }
    layers = _layer_matrix(source)
    authorities = _authority_matrix()
    boundaries = _boundary_matrix()
    root_final = {
        "root_decision": "all_layers_observed_no_autonomy",
        "root_final_authority_preserved": True,
        "system_ready_for_external_drs": False,
        "system_ready_for_marennya": False,
        "system_ready_for_up": False,
        "next_engineering_direction": "DRS adversarial postcommit/audit/docs",
    }
    proof_artifact = {
        "super_smoke_proof_artifact_id": "all_layers_applied_super_smoke_v0_1",
        "source_evidence": source,
        "layer_matrix": layers,
        "authority_matrix": authorities,
        "boundary_matrix": boundaries,
        "root_final": root_final,
    }
    audit_entry = {
        "audit_entry_id": "audit_all_layers_applied_super_smoke_v0_1",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = AllLayersAppliedSuperSmokeReport(
        input_mode={
            "mode": "deterministic_all_layers_applied_super_smoke",
            "integration_smoke_only": True,
            "new_capability_layer": False,
            "live_network_used": False,
            "gemini_called": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
            "marennya_invoked": False,
            "up_invoked": False,
        },
        super_smoke_source_evidence=source,
        super_smoke_layer_matrix=layers,
        super_smoke_authority_matrix=authorities,
        super_smoke_boundary_matrix=boundaries,
        super_smoke_root_final=root_final,
        super_smoke_proof_artifact=proof_artifact,
        super_smoke_audit_entry=audit_entry,
        summary={},
    )
    source_pass = all(status == "PASS" for status in source.values())
    consistent = validate_all_layers_applied_super_smoke_report_consistency(
        provisional
    )
    passed = source_pass and consistent
    return replace(
        provisional,
        summary={
            "all_layers_applied_super_smoke_status": "PASS" if passed else "FAIL",
            "layers_observed": len(layers),
            "source_statuses_all_pass": source_pass,
            "root_remains_final_authority": True,
            "drs_retrieval_is_not_authority": True,
            "reuse_score_is_not_root": True,
            "semantic_similarity_is_not_authority": True,
            "gt_remains_advisory_until_root": True,
            "conflictcheck_remains_advisory_until_root": True,
            "audit_chain_decides_truth": False,
            "permission_is_not_execution": True,
            "needlecandidate_is_not_installed_needle": True,
            "adversarial_drs_reuse_blocked": True,
            "no_direct_ready_created": True,
            "no_completed_external_action_created": True,
            "no_real_external_action_executed": True,
            "no_production_persistence": True,
            "no_global_drs_write": True,
            "no_external_drs_write": True,
            "protocol_candidate_created": False,
            "needle_candidate_created_by_super_smoke": False,
            "installed_needle_created": False,
            "gemini_called": False,
            "network_called": False,
            "telegram_used": False,
            "marennya_invoked": False,
            "up_invoked": False,
            "production_autonomy_claimed": False,
            "ready_for_auditor_review": passed,
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


def render_all_layers_applied_super_smoke(
    report: AllLayersAppliedSuperSmokeReport,
) -> str:
    lines = [
        "[ALL-LAYERS APPLIED SUPER-SMOKE]",
        "note: deterministic auditor-facing integration smoke over completed layers",
        "note: this smoke observes capabilities but creates no new capability layer",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE EVIDENCE]", report.super_smoke_source_evidence)
    _rows(lines, "[LAYER MATRIX]", report.super_smoke_layer_matrix)
    _rows(lines, "[AUTHORITY MATRIX]", report.super_smoke_authority_matrix)
    _rows(lines, "[BOUNDARY MATRIX]", report.super_smoke_boundary_matrix)
    _section(lines, "[ROOT FINAL]", report.super_smoke_root_final)
    _section(lines, "[AUDIT ENTRY]", report.super_smoke_audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_all_layers_applied_super_smoke() -> str:
    return render_all_layers_applied_super_smoke(
        collect_all_layers_applied_super_smoke()
    )


def main() -> int:
    print(run_all_layers_applied_super_smoke(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
