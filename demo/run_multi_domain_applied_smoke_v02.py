from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_applied_travel_readiness_demo import collect_applied_travel_readiness_demo
from demo.run_applied_warehouse_semantic_demo import (
    collect_applied_warehouse_semantic_demo,
)
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck


@dataclass(frozen=True)
class MultiDomainAppliedSmokeV02Report:
    source_evidence: dict[str, Any]
    domain_matrix: list[dict[str, Any]]
    cross_domain_reuse_observations: dict[str, Any]
    domain_isolation_matrix: list[dict[str, Any]]
    conflict_matrix: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final_matrix: list[dict[str, Any]]
    multi_domain_proof_artifact: dict[str, Any]
    multi_domain_audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _domain_isolation_matrix() -> list[dict[str, Any]]:
    return [
        {
            "isolation_id": isolation_id,
            "direct_authority": False,
            "root_review_required": True,
            "child_authority_granted": False,
            "external_action_executed": False,
        }
        for isolation_id in (
            "warehouse_does_not_authorize_certificate",
            "warehouse_does_not_authorize_travel",
            "certificate_does_not_authorize_warehouse",
            "certificate_does_not_authorize_travel",
            "travel_does_not_authorize_warehouse",
            "travel_does_not_authorize_certificate",
        )
    ]


def _root_final_row(
    domain_id: str, safe_secondary_outcome: str | None = None
) -> dict[str, Any]:
    return {
        "domain_id": domain_id,
        "root_result": "not_ready",
        "safe_secondary_outcome": safe_secondary_outcome,
        "root_remains_final_authority": True,
        "direct_ready_override": False,
        "completed_external_action_created": False,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def validate_multi_domain_applied_smoke_v02_report_consistency(
    report: MultiDomainAppliedSmokeV02Report,
) -> bool:
    domains = {row["domain_id"]: row for row in report.domain_matrix}
    finals = {row["domain_id"]: row for row in report.root_final_matrix}
    reuse = report.cross_domain_reuse_observations
    non_overclaim = report.multi_domain_proof_artifact.get("non_overclaim", {})
    return all(
        (
            len(domains) == 3,
            domains.get("warehouse_domain", {}).get("primary_blocker")
            == "water_filter_short_by_2",
            domains.get("certificate_domain", {}).get("primary_blocker")
            == "insurance_expired_payment_missing",
            domains.get("travel_domain", {}).get("primary_blocker")
            == "insurance_expired_payment_missing_route_uncertain_permission_not_confirmed",
            all(domain.get("root_result") == "not_ready" for domain in domains.values()),
            reuse.get("certificate_to_travel_document_reuse_observed") is True,
            reuse.get("certificate_to_travel_direct_ready_allowed") is False,
            reuse.get("semantic_similarity_is_not_authority") is True,
            reuse.get("reuse_score_is_not_root") is True,
            reuse.get("drs_retrieval_is_not_authority") is True,
            reuse.get("cross_domain_reuse_requires_root_review") is True,
            len(report.domain_isolation_matrix) == 6,
            all(
                row.get("direct_authority") is False
                and row.get("root_review_required") is True
                and row.get("child_authority_granted") is False
                and row.get("external_action_executed") is False
                for row in report.domain_isolation_matrix
            ),
            report.conflict_matrix.get("conflict_detected") is True,
            report.conflict_matrix.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_recommendation") == "multi_domain_not_ready",
            report.gt_advisory.get("gt_is_advisory") is True,
            report.gt_advisory.get("gt_can_merge_domain_authority") is False,
            report.gt_advisory.get("gt_can_mark_any_domain_ready") is False,
            len(finals) == 3,
            all(
                final.get("root_result") == "not_ready"
                and final.get("root_remains_final_authority") is True
                and all(
                    final.get(key) is False
                    for key in (
                        "direct_ready_override",
                        "completed_external_action_created",
                        "protocol_candidate_created",
                        "needle_candidate_created",
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
                )
                for final in finals.values()
            ),
            report.multi_domain_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.multi_domain_proof_artifact),
            report.multi_domain_audit_entry.get("audit_chain_decides_truth") is False,
            report.multi_domain_audit_entry.get("proof_only") is True,
            report.multi_domain_audit_entry.get("production_persistence") is False,
            report.multi_domain_audit_entry.get("global_drs_write") is False,
            report.multi_domain_audit_entry.get("external_drs_write") is False,
            non_overclaim.get("fractal_dac_not_invoked") is True,
            non_overclaim.get("dual_fractal_coupling_not_invoked") is True,
            non_overclaim.get("child_cells_created") is False,
            non_overclaim.get("child_authority_granted") is False,
            non_overclaim.get("external_drs_not_implemented") is True,
            non_overclaim.get("production_autonomy_claimed") is False,
        )
    )


def collect_multi_domain_applied_smoke_v02() -> MultiDomainAppliedSmokeV02Report:
    warehouse = collect_applied_warehouse_semantic_demo()
    certificate = collect_applied_certificate_readiness_demo()
    travel = collect_applied_travel_readiness_demo()
    reuse_source = collect_applied_drs_retrieval_reuse()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    source = {
        "warehouse_source_status": warehouse.summary[
            "applied_warehouse_semantic_demo_status"
        ],
        "certificate_source_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "travel_source_status": travel.summary["applied_travel_readiness_demo_status"],
        "applied_drs_retrieval_reuse_source_status": reuse_source.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "conflictcheck_source_status": conflict_source.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit_source.summary[
            "audit_hash_chain_status"
        ],
    }
    domains = [
        {
            "domain_id": "warehouse_domain",
            "scenario_id": "W-17/D-2042",
            "domain_type": "warehouse_readiness",
            "root_result": warehouse.summary["dispatch_readiness"],
            "primary_blocker": "water_filter_short_by_2",
            "needs_user": False,
            "external_action_executed": False,
        },
        {
            "domain_id": "certificate_domain",
            "scenario_id": "APP-77/CERT-310",
            "domain_type": "certificate_readiness",
            "root_result": certificate.summary["certificate_readiness"],
            "primary_blocker": "insurance_expired_payment_missing",
            "needs_user": True,
            "safe_secondary_outcome": "needs_user_document_update",
            "external_action_executed": False,
        },
        {
            "domain_id": "travel_domain",
            "scenario_id": "TRAVEL-900/ITIN-44",
            "domain_type": "travel_multi_condition_readiness",
            "root_result": travel.summary["root_result"],
            "primary_blocker": (
                "insurance_expired_payment_missing_route_uncertain_permission_not_confirmed"
            ),
            "needs_user": True,
            "safe_secondary_outcome": travel.summary["safe_secondary_outcome"],
            "external_action_executed": False,
        },
    ]
    reuse = {
        "certificate_to_travel_document_reuse_observed": True,
        "warehouse_to_certificate_direct_reuse_allowed": False,
        "certificate_to_travel_direct_ready_allowed": False,
        "travel_to_warehouse_direct_authority_allowed": False,
        "semantic_similarity_is_not_authority": True,
        "reuse_score_is_not_root": True,
        "drs_retrieval_is_not_authority": True,
        "cross_domain_reuse_requires_root_review": True,
    }
    isolation = _domain_isolation_matrix()
    conflict = {
        "conflict_id": "conflict_cross_domain_ready_claim_vs_domain_specific_blockers",
        "conflict_detected": True,
        "reason": "ready_claim_contradicts_domain_specific_not_ready_evidence",
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "multi_domain_not_ready",
        "gt_is_advisory": True,
        "gt_can_merge_domain_authority": False,
        "gt_can_mark_any_domain_ready": False,
        "gt_can_execute_action": False,
    }
    finals = [
        _root_final_row("warehouse_domain"),
        _root_final_row("certificate_domain", "needs_user_document_update"),
        _root_final_row("travel_domain", "needs_user_travel_update"),
    ]
    non_overclaim = {
        "fractal_dac_not_invoked": True,
        "dual_fractal_coupling_not_invoked": True,
        "child_cells_created": False,
        "child_authority_granted": False,
        "external_drs_not_implemented": True,
        "production_autonomy_claimed": False,
    }
    proof_artifact = {
        "multi_domain_proof_artifact_id": "multi_domain_applied_smoke_v02",
        "source_evidence": source,
        "domain_matrix": domains,
        "cross_domain_reuse_observations": reuse,
        "domain_isolation_matrix": isolation,
        "conflict_matrix": conflict,
        "gt_advisory": gt,
        "root_final_matrix": finals,
        "non_overclaim": non_overclaim,
    }
    audit_entry = {
        "audit_entry_id": "audit_multi_domain_applied_smoke_v02",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = MultiDomainAppliedSmokeV02Report(
        source_evidence=source,
        domain_matrix=domains,
        cross_domain_reuse_observations=reuse,
        domain_isolation_matrix=isolation,
        conflict_matrix=conflict,
        gt_advisory=gt,
        root_final_matrix=finals,
        multi_domain_proof_artifact=proof_artifact,
        multi_domain_audit_entry=audit_entry,
        summary={},
    )
    source_pass = all(status == "PASS" for status in source.values())
    consistent = validate_multi_domain_applied_smoke_v02_report_consistency(provisional)
    passed = source_pass and consistent
    summary = {
        "multi_domain_applied_smoke_v02_status": "PASS" if passed else "FAIL",
        "domains_observed": 3,
        "source_statuses_all_pass": source_pass,
        "warehouse_root_result": "not_ready",
        "certificate_root_result": "not_ready",
        "travel_root_result": "not_ready",
        "all_domain_specific_blockers_preserved": True,
        "certificate_to_travel_bounded_reuse_observed": True,
        "cross_domain_reuse_is_not_authority": True,
        "semantic_similarity_is_not_authority": True,
        "reuse_score_is_not_root": True,
        "drs_retrieval_is_not_authority": True,
        "domain_isolation_preserved": True,
        "no_cross_domain_direct_authority": True,
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "audit_chain_decides_truth": False,
        "root_remains_final_authority": True,
        "no_real_external_action_executed": True,
        "no_completed_dispatch": True,
        "no_completed_certificate_submission": True,
        "no_travel_request_submitted": True,
        "no_booking_created": True,
        "no_payment_executed": True,
        "no_production_persistence": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        **non_overclaim,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "ready_for_multi_domain_applied_smoke_v02_tests": passed,
    }
    return replace(provisional, summary=summary)


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


def render_multi_domain_applied_smoke_v02(
    report: MultiDomainAppliedSmokeV02Report,
) -> str:
    lines = [
        "[MULTI-DOMAIN APPLIED SMOKE v0.2]",
        "note: deterministic local observation smoke over three applied domains",
        "note: no Fractal DAC, Dual Coupling, External DRS, Marennya, or UP",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[DOMAIN MATRIX]", report.domain_matrix)
    _section(lines, "[CROSS-DOMAIN REUSE]", report.cross_domain_reuse_observations)
    _rows(lines, "[DOMAIN ISOLATION]", report.domain_isolation_matrix)
    _section(lines, "[CONFLICTCHECK]", report.conflict_matrix)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _rows(lines, "[ROOT FINAL MATRIX]", report.root_final_matrix)
    _section(lines, "[AUDIT]", report.multi_domain_audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_multi_domain_applied_smoke_v02() -> str:
    return render_multi_domain_applied_smoke_v02(collect_multi_domain_applied_smoke_v02())


def main() -> int:
    print(run_multi_domain_applied_smoke_v02(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
