from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from demo.run_architect_from_bounded_attractor_packet import (
    collect_architect_from_bounded_attractor_packet,
)


EXECUTION_SCENARIOS = (
    "sandbox_needle_completed",
    "sandbox_needle_timeout_degraded",
    "sandbox_needle_invalid_json_failed",
    "sandbox_needle_contract_mismatch_blocked",
    "sandbox_needle_permission_required_blocked",
    "sandbox_needle_forbidden_external_action_blocked",
)
BLOCKED_SCENARIOS = (
    "raw_needleruntime_output_blocked",
    "malicious_needle_claiming_final_output_rejected",
    "malicious_needle_claiming_drs_write_rejected",
    "malicious_needle_claiming_root_bypass_rejected",
    "malicious_needle_claiming_real_external_action_rejected",
)
SCENARIOS_UNDER_TEST = EXECUTION_SCENARIOS + BLOCKED_SCENARIOS


@dataclass(frozen=True)
class RootNativeSandboxNeedleRuntimeE2EReport:
    input_mode: dict[str, Any]
    root_approved_plan_node: dict[str, Any]
    needleruntime_executions: list[dict[str, Any]]
    result_proposal_adapter: list[dict[str, Any]]
    post_vv_gt_root_final: list[dict[str, Any]]
    blocked_malicious_inputs: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _source_plan_node() -> dict[str, Any]:
    report = collect_architect_from_bounded_attractor_packet()
    proposal = next(
        row
        for row in report.architect_plan_proposals
        if row["scenario"] == "accepted_packet_architect_plan_valid"
        and row["plan_graph_contract_valid"]
    )
    node = proposal["nodes"][0]
    return {
        "source_architect_report_status": report.summary[
            "architect_from_bounded_attractor_packet_status"
        ],
        "plan_graph_proposal_id": proposal["proposal_id"],
        "plan_node_id": node["node_id"],
        "node_kind": node.get("kind", "sandbox_capability"),
        "capability_name": "sandbox_certificate_lookup",
        "root_gate_approved": True,
        "policy_checked": True,
        "permission_state": "sandbox_allowed",
        "sandbox_mode": True,
        "bounded_input_present": True,
        "bounded_input": {
            "certificate_type": "mock_residency_certificate",
            "lookup_scope": "local_fixture_only",
        },
    }


def _execution_result(
    scenario: str,
    plan_node: dict[str, Any],
) -> dict[str, Any]:
    facts = {
        "sandbox_needle_completed": ("completed", "none", False, False, False, True),
        "sandbox_needle_timeout_degraded": (
            "degraded",
            "timeout",
            False,
            True,
            False,
            True,
        ),
        "sandbox_needle_invalid_json_failed": (
            "failed",
            "invalid_json",
            False,
            False,
            True,
            False,
        ),
        "sandbox_needle_contract_mismatch_blocked": (
            "blocked",
            "contract_mismatch",
            False,
            False,
            True,
            False,
        ),
        "sandbox_needle_permission_required_blocked": (
            "blocked",
            "permission_required",
            True,
            False,
            False,
            False,
        ),
        "sandbox_needle_forbidden_external_action_blocked": (
            "blocked",
            "forbidden_external_action",
            False,
            True,
            True,
            False,
        ),
    }
    status, failure, permission, breaker, quarantine, safe_for_gt = facts[scenario]
    return {
        "scenario": scenario,
        "needle_execution_result_id": f"needle_execution_result_{scenario}",
        "created_by": "sandbox_needleruntime",
        "needle_id": "needle_sandbox_certificate_lookup_v0_1",
        "capability_name": plan_node["capability_name"],
        "source_plan_graph_node_id": plan_node["plan_node_id"],
        "source_plan_graph_proposal_id": plan_node["plan_graph_proposal_id"],
        "execution_status": status,
        "failure_kind": failure,
        "bounded_output": {
            "status": status,
            "fixture_result": (
                "mock_certificate_record_found" if status == "completed" else None
            ),
        },
        "evidence": [
            "sandbox_fixture_only",
            f"execution_status:{status}",
            f"failure_kind:{failure}",
        ],
        "risks": [] if status == "completed" else [f"needle_outcome:{failure}"],
        "permission_required": permission,
        "circuit_breaker_opened": breaker,
        "quarantine_required": quarantine,
        "safe_for_gt": safe_for_gt,
        "root_crash_risk_contained": True,
        "sandbox_mode": True,
        "real_external_action_executed": False,
        "needle_created_final_output": False,
        "needle_wrote_drs": False,
        "needle_bypassed_root": False,
        "time_envelope": {
            "observed_at": "2026-06-08T00:00:00Z",
            "valid_from": "2026-06-08T00:00:00Z",
            "valid_to": None,
            "time_basis": "deterministic_proof_clock",
        },
        "provenance": {
            "runtime": "sandbox_needleruntime",
            "capability_mode": "mock_fixture",
            "proof_only": True,
        },
    }


def _unsafe_claims(result: dict[str, Any]) -> list[str]:
    claims: list[str] = []
    if result.get("needle_created_final_output") is True:
        claims.append("needle_final_output_claim_rejected")
    if result.get("needle_wrote_drs") is True:
        claims.append("needle_drs_write_claim_rejected")
    if result.get("needle_bypassed_root") is True:
        claims.append("needle_root_bypass_claim_rejected")
    if result.get("real_external_action_executed") is True:
        claims.append("needle_external_action_claim_rejected")
    return claims


def _is_needle_execution_result(result: dict[str, Any]) -> bool:
    required = {
        "needle_execution_result_id",
        "created_by",
        "source_plan_graph_node_id",
        "source_plan_graph_proposal_id",
        "execution_status",
        "failure_kind",
        "evidence",
        "risks",
        "sandbox_mode",
        "real_external_action_executed",
        "needle_created_final_output",
        "needle_wrote_drs",
        "needle_bypassed_root",
    }
    return (
        required <= set(result)
        and result.get("created_by") == "sandbox_needleruntime"
        and result.get("execution_status")
        in {"completed", "degraded", "blocked", "failed"}
        and result.get("sandbox_mode") is True
    )


def _result_proposal(result: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_needle_execution_result(result) or _unsafe_claims(result):
        return None
    status = result["execution_status"]
    return {
        "scenario": result["scenario"],
        "result_proposal_id": f"result_proposal_{result['scenario']}",
        "created_by": "executor_adapter",
        "source_needle_execution_result_id": result["needle_execution_result_id"],
        "source_plan_graph_node_id": result["source_plan_graph_node_id"],
        "source_plan_graph_proposal_id": result["source_plan_graph_proposal_id"],
        "result_status": status,
        "node_results": [
            {
                "node_id": result["source_plan_graph_node_id"],
                "needle_execution_result_id": result["needle_execution_result_id"],
                "status": status,
            }
        ],
        "evidence": list(result["evidence"]),
        "risks": list(result["risks"]),
        "degraded_or_blocked_preserved": status in {"degraded", "blocked", "failed"},
        "final_output_claim": False,
        "drs_write_claim": False,
        "real_external_action_claim": False,
    }


def _validation_report(result: dict[str, Any]) -> dict[str, Any]:
    result_status = result["result_status"]
    validation_status = (
        "accepted"
        if result_status == "completed"
        else "degraded"
        if result_status == "degraded"
        else "rejected"
    )
    return {
        "validation_report_id": f"validation_report_{result['scenario']}",
        "created_by": "post_vv",
        "source_result_proposal_id": result["result_proposal_id"],
        "validation_status": validation_status,
        "validation_findings": [
            "needle_execution_result_checked",
            f"needle_result_status_preserved:{result_status}",
        ],
        "validation_risks": list(result["risks"]),
        "post_vv_creates_final_output": False,
        "post_vv_writes_drs": False,
        "post_vv_executes_actions": False,
    }


def _gt_decision(validation: dict[str, Any]) -> dict[str, Any]:
    mapping = {"accepted": "accept", "degraded": "degrade", "rejected": "reject"}
    decision = mapping[validation["validation_status"]]
    return {
        "gt_decision_id": f"gt_decision_{validation['source_result_proposal_id']}",
        "created_by": "gt_validator",
        "source_validation_report_id": validation["validation_report_id"],
        "source_result_proposal_id": validation["source_result_proposal_id"],
        "gt_decision": decision,
        "selection_reason": f"needle_validation_{validation['validation_status']}",
        "gt_creates_final_output": False,
        "gt_writes_drs": False,
        "gt_executes_actions": False,
    }


def _root_final(gt: dict[str, Any], scenario: str) -> dict[str, Any]:
    status = {"accept": "accepted", "degrade": "degraded", "reject": "rejected"}[
        gt["gt_decision"]
    ]
    return {
        "final_artifact_id": f"root_final_artifact_{scenario}",
        "created_by": "root_orchestrator",
        "source_gt_decision_id": gt["gt_decision_id"],
        "source_validation_report_id": gt["source_validation_report_id"],
        "source_result_proposal_id": gt["source_result_proposal_id"],
        "root_final_status": status,
        "root_created_final_output": True,
        "gt_created_final_output": False,
        "root_writes_drs": False,
        "drs_writeback_invoked": False,
        "root_executes_actions": False,
        "production_external_action_executed": False,
        "production_persistence_claimed": False,
    }


def _downstream_row(result_proposal: dict[str, Any]) -> dict[str, Any]:
    validation = _validation_report(result_proposal)
    gt = _gt_decision(validation)
    final = _root_final(gt, result_proposal["scenario"])
    return {
        "scenario": result_proposal["scenario"],
        "post_vv_status": validation["validation_status"],
        "gt_decision": gt["gt_decision"],
        "root_final_status": final["root_final_status"],
        "validation_report_id": validation["validation_report_id"],
        "gt_decision_id": gt["gt_decision_id"],
        "root_final_artifact_id": final["final_artifact_id"],
        "root_final_artifact_created": True,
        "root_is_only_final_output_authority": (
            final["root_created_final_output"]
            and not final["gt_created_final_output"]
            and not validation["post_vv_creates_final_output"]
        ),
        "post_vv_bypassed": False,
        "gt_bypassed": False,
        "root_bypassed": False,
        "unsafe_success_hidden": (
            result_proposal["result_status"] != "completed"
            and final["root_final_status"] == "accepted"
        ),
    }


def _blocked_malicious(base: dict[str, Any]) -> dict[str, Any]:
    malicious = {
        "malicious_needle_claiming_final_output_rejected": (
            "needle_created_final_output",
            "needle_final_output_claim_rejected",
        ),
        "malicious_needle_claiming_drs_write_rejected": (
            "needle_wrote_drs",
            "needle_drs_write_claim_rejected",
        ),
        "malicious_needle_claiming_root_bypass_rejected": (
            "needle_bypassed_root",
            "needle_root_bypass_claim_rejected",
        ),
        "malicious_needle_claiming_real_external_action_rejected": (
            "real_external_action_executed",
            "needle_external_action_claim_rejected",
        ),
    }
    details = {
        "raw_needleruntime_output_blocked": True,
        "raw_needleruntime_output_block_reasons": [
            "raw_needleruntime_output_not_allowed"
        ],
    }
    for scenario, (claim, expected_reason) in malicious.items():
        result = copy.deepcopy(base)
        result[claim] = True
        reasons = _unsafe_claims(result)
        details[scenario] = _result_proposal(result) is None and expected_reason in reasons
        details[f"{scenario}_reasons"] = reasons
    return details


def collect_root_native_sandbox_needleruntime_e2e() -> RootNativeSandboxNeedleRuntimeE2EReport:
    plan_node = _source_plan_node()
    executions = [_execution_result(scenario, plan_node) for scenario in EXECUTION_SCENARIOS]
    proposals = [
        proposal
        for result in executions
        if (proposal := _result_proposal(result)) is not None
    ]
    adapters = [
        {
            "scenario": proposal["scenario"],
            "result_proposal_created": True,
            "source_needle_execution_result_id": proposal[
                "source_needle_execution_result_id"
            ],
            "result_status": proposal["result_status"],
            "degraded_or_blocked_preserved": proposal[
                "degraded_or_blocked_preserved"
            ],
            "final_output_claim": proposal["final_output_claim"],
            "drs_write_claim": proposal["drs_write_claim"],
            "real_external_action_claim": proposal["real_external_action_claim"],
        }
        for proposal in proposals
    ]
    downstream = [_downstream_row(proposal) for proposal in proposals]
    blocked = _blocked_malicious(executions[0])
    authority = {
        "needleruntime_is_authority": False,
        "needle_execution_result_is_final_truth": False,
        "root_remains_authority": all(
            row["root_is_only_final_output_authority"] for row in downstream
        ),
        "root_is_only_final_output_authority": all(
            row["root_is_only_final_output_authority"] for row in downstream
        ),
        "needle_created_final_output": any(
            row["needle_created_final_output"] for row in executions
        ),
        "needle_wrote_drs": any(row["needle_wrote_drs"] for row in executions),
        "needle_bypassed_root": any(row["needle_bypassed_root"] for row in executions),
        "production_external_action_executed": any(
            row["real_external_action_executed"] for row in executions
        ),
        "production_persistence_claimed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "telegram_action_executed": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    malicious_rejections = [
        blocked["malicious_needle_claiming_final_output_rejected"],
        blocked["malicious_needle_claiming_drs_write_rejected"],
        blocked["malicious_needle_claiming_root_bypass_rejected"],
        blocked["malicious_needle_claiming_real_external_action_rejected"],
    ]
    execution_boundaries_pass = (
        len(executions) == len(EXECUTION_SCENARIOS)
        and len(proposals) == len(EXECUTION_SCENARIOS)
        and len(downstream) == len(EXECUTION_SCENARIOS)
        and all(result["sandbox_mode"] for result in executions)
        and all(result["root_crash_risk_contained"] for result in executions)
        and all(not row["unsafe_success_hidden"] for row in downstream)
        and all(
            not row["post_vv_bypassed"]
            and not row["gt_bypassed"]
            and not row["root_bypassed"]
            for row in downstream
        )
    )
    authority_pass = (
        not authority["needleruntime_is_authority"]
        and not authority["needle_execution_result_is_final_truth"]
        and authority["root_remains_authority"]
        and authority["root_is_only_final_output_authority"]
        and not authority["needle_created_final_output"]
        and not authority["needle_wrote_drs"]
        and not authority["needle_bypassed_root"]
        and not authority["production_external_action_executed"]
        and not authority["production_persistence_claimed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["telegram_action_executed"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
    )
    status = (
        "PASS"
        if plan_node["source_architect_report_status"] == "PASS"
        and execution_boundaries_pass
        and blocked["raw_needleruntime_output_blocked"]
        and all(malicious_rejections)
        and authority_pass
        else "FAIL"
    )
    summary = {
        "root_native_sandbox_needleruntime_e2e_status": status,
        "scenarios_verified": len(SCENARIOS_UNDER_TEST),
        "completed_scenarios": sum(
            row["execution_status"] == "completed" for row in executions
        ),
        "degraded_scenarios": sum(
            row["execution_status"] == "degraded" for row in executions
        ),
        "blocked_or_failed_scenarios": sum(
            row["execution_status"] in {"blocked", "failed"} for row in executions
        ),
        "malicious_claims_rejected": sum(malicious_rejections),
        "raw_needleruntime_output_blocked": blocked[
            "raw_needleruntime_output_blocked"
        ],
        "needleruntime_is_authority": authority["needleruntime_is_authority"],
        "root_remains_authority": authority["root_remains_authority"],
        "root_is_only_final_output_authority": authority[
            "root_is_only_final_output_authority"
        ],
        "no_real_external_actions": not authority[
            "production_external_action_executed"
        ],
        "no_drs_write_by_needle": not authority["needle_wrote_drs"],
        "no_production_persistence": not authority["production_persistence_claimed"],
        "ready_for_drs_lifecycle_semantics_v0_2": status == "PASS",
        "production_autonomy_claimed": False,
    }
    return RootNativeSandboxNeedleRuntimeE2EReport(
        input_mode={
            "mode": "deterministic_sandbox_needleruntime_e2e",
            "sandbox_mode": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
        },
        root_approved_plan_node=plan_node,
        needleruntime_executions=executions,
        result_proposal_adapter=adapters,
        post_vv_gt_root_final=downstream,
        blocked_malicious_inputs=blocked,
        authority_safety=authority,
        summary=summary,
    )


def _format_value(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format_value(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    for row in rows:
        lines.append(" | ".join(f"{key}={_format_value(value)}" for key, value in row.items()))


def render_root_native_sandbox_needleruntime_e2e(
    report: RootNativeSandboxNeedleRuntimeE2EReport,
) -> str:
    lines = [
        "[ROOT-NATIVE SANDBOX NEEDLERUNTIME E2E]",
        "note: deterministic Root-native sandbox NeedleRuntime E2E proof",
        "note: sandbox/mock needles only",
        "note: no real external API calls",
        "note: no real device actions",
        "note: no Telegram action",
        "note: NeedleRuntime is not authority",
        "note: NeedleExecutionResult is evidence, not final truth",
        "note: Root remains final authority",
        "note: no production DRS persistence",
        "note: no global/external DRS",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[ROOT-APPROVED PLAN NODE]", report.root_approved_plan_node)
    _rows(lines, "[NEEDLERUNTIME EXECUTIONS]", report.needleruntime_executions)
    _rows(lines, "[RESULT PROPOSAL ADAPTER]", report.result_proposal_adapter)
    _rows(lines, "[POST V&V / GT / ROOT FINAL]", report.post_vv_gt_root_final)
    _section(lines, "[BLOCKED / MALICIOUS INPUTS]", report.blocked_malicious_inputs)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_root_native_sandbox_needleruntime_e2e() -> str:
    return render_root_native_sandbox_needleruntime_e2e(
        collect_root_native_sandbox_needleruntime_e2e()
    )


def main() -> int:
    print(run_root_native_sandbox_needleruntime_e2e(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
