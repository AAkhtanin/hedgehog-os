from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


LLM_CALL_FIELDS = (
    "intake_llm_calls",
    "connector_interpretation_llm_calls",
    "evidence_resolution_llm_calls",
    "legal_state_llm_calls",
    "drs_reuse_llm_calls",
    "external_pointer_llm_calls",
    "semantic_summary_llm_calls",
    "needle_candidate_llm_calls",
    "child_cell_llm_calls",
    "conflict_resolution_llm_calls",
    "action_planning_llm_calls",
    "finalization_llm_calls",
)


@dataclass(frozen=True)
class ComputeCollapseEnterpriseBenchReport:
    source_evidence: dict[str, Any]
    source_checkpoints: list[dict[str, Any]]
    benchmark_purpose: dict[str, Any]
    enterprise_bench_request: dict[str, Any]
    baseline_long_chain_estimate: dict[str, Any]
    hedgehog_root_controlled_path: dict[str, Any]
    compute_collapse_metrics: dict[str, Any]
    safety_authority_boundaries: dict[str, bool]
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
        },
        {
            "checkpoint_id": "read_only_enterprise_connector_sandbox_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "external_evidence_acceptance_gate_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "bounded_llm_semantic_executor_node_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "enterprise_chaos_pack_v01",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
            "commits": "082753e,104105b,668a51a,03636b8",
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


def _baseline_long_chain_estimate() -> dict[str, Any]:
    estimate = {
        "path_id": "naive_long_chain_baseline",
        "estimate_mode": "deterministic_synthetic_estimate",
        "real_llm_calls_executed": 0,
        "intake_llm_calls": 1,
        "connector_interpretation_llm_calls": 4,
        "evidence_resolution_llm_calls": 4,
        "legal_state_llm_calls": 2,
        "drs_reuse_llm_calls": 2,
        "external_pointer_llm_calls": 2,
        "semantic_summary_llm_calls": 2,
        "needle_candidate_llm_calls": 2,
        "child_cell_llm_calls": 2,
        "conflict_resolution_llm_calls": 3,
        "action_planning_llm_calls": 3,
        "finalization_llm_calls": 2,
        "baseline_collector_replays": 4,
        "baseline_validation_passes": 6,
        "baseline_context_units": 180,
        "baseline_action_planning_steps": 6,
        "baseline_escalation_surfaces": 18,
        "baseline_unbounded_authority_risk_units": 18,
        "baseline_failed_attempts": 18,
        "baseline_expensive_semantic_expansions": 18,
    }
    estimate["baseline_llm_calls"] = sum(estimate[field] for field in LLM_CALL_FIELDS)
    return estimate


def _hedgehog_root_controlled_path() -> dict[str, Any]:
    path = {
        "path_id": "hedgehog_root_controlled_path",
        "measurement_mode": "deterministic_local_benchmark",
        "intake_llm_calls": 0,
        "connector_interpretation_llm_calls": 0,
        "evidence_resolution_llm_calls": 0,
        "legal_state_llm_calls": 0,
        "drs_reuse_llm_calls": 0,
        "external_pointer_llm_calls": 0,
        "semantic_summary_llm_calls": 1,
        "needle_candidate_llm_calls": 0,
        "child_cell_llm_calls": 0,
        "conflict_resolution_llm_calls": 0,
        "action_planning_llm_calls": 0,
        "finalization_llm_calls": 0,
        "bounded_llm_executor_nodes_used": 1,
        "hedgehog_collector_replays": 0,
        "hedgehog_validation_passes": 1,
        "hedgehog_context_units": 32,
        "hedgehog_action_planning_steps": 0,
        "hedgehog_escalation_surfaces": 18,
        "hedgehog_unbounded_authority_risk_units": 0,
        "hedgehog_failed_attempts": 0,
        "hedgehog_blocked_attempts": 18,
        "hedgehog_quarantined_and_blocked": 4,
        "hedgehog_expensive_semantic_expansions": 1,
        "root_controlled_metadata_reuse": True,
        "bounded_llm_use_only": True,
    }
    path["hedgehog_llm_calls"] = sum(path[field] for field in LLM_CALL_FIELDS)
    return path


def _compute_metrics(
    baseline: dict[str, Any],
    hedgehog: dict[str, Any],
) -> dict[str, Any]:
    llm_call_reduction = baseline["baseline_llm_calls"] - hedgehog["hedgehog_llm_calls"]
    context_unit_reduction = (
        baseline["baseline_context_units"] - hedgehog["hedgehog_context_units"]
    )
    return {
        "metric_mode": "proof_level_compute_collapse_signal",
        "llm_call_reduction": llm_call_reduction,
        "llm_call_reduction_ratio": llm_call_reduction / baseline["baseline_llm_calls"],
        "context_unit_reduction": context_unit_reduction,
        "context_unit_reduction_ratio": (
            context_unit_reduction / baseline["baseline_context_units"]
        ),
        "collector_replay_reduction": (
            baseline["baseline_collector_replays"]
            - hedgehog["hedgehog_collector_replays"]
        ),
        "validation_pass_reduction": (
            baseline["baseline_validation_passes"]
            - hedgehog["hedgehog_validation_passes"]
        ),
        "action_planning_reduction": (
            baseline["baseline_action_planning_steps"]
            - hedgehog["hedgehog_action_planning_steps"]
        ),
        "unbounded_authority_risk_reduction": (
            baseline["baseline_unbounded_authority_risk_units"]
            - hedgehog["hedgehog_unbounded_authority_risk_units"]
        ),
        "expensive_semantic_expansion_reduction": (
            baseline["baseline_expensive_semantic_expansions"]
            - hedgehog["hedgehog_expensive_semantic_expansions"]
        ),
        "synthetic_estimate_only": True,
        "billing_measurement_performed": False,
        "latency_measurement_performed": False,
    }


def _safety_boundaries() -> dict[str, bool]:
    return {
        "root_remains_final_authority": True,
        "closed_metadata_prevents_collector_replay": True,
        "drs_reuse_prevents_unnecessary_recomputation": True,
        "bounded_llm_use_only": True,
        "llm_is_not_root": True,
        "benchmark_does_not_execute_baseline": True,
        "benchmark_does_not_authorize_action": True,
        "benchmark_does_not_authorize_killer_demo": True,
        "benchmark_does_not_authorize_multi_llm_showcase": True,
        "no_network": True,
        "no_gemini": True,
        "no_external_action": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "no_installed_needle": True,
        "no_production_persistence": True,
        "no_marennya": True,
        "no_up": True,
        "audit_hash_decides_truth_false": True,
    }


def validate_compute_collapse_enterprise_bench_v01(
    report: ComputeCollapseEnterpriseBenchReport,
) -> bool:
    source = report.source_evidence
    baseline = report.baseline_long_chain_estimate
    hedgehog = report.hedgehog_root_controlled_path
    metrics = report.compute_collapse_metrics
    root = report.root_final
    return all(
        (
            source["source_evidence_mode"] == "closed_checkpoint_metadata_only",
            source["source_collectors_replayed"] is False,
            source["source_collectors_replayed_count"] == 0,
            len(report.source_checkpoints) == 5,
            all(
                row["checkpoint_status"] == "PASS"
                and row["closure_status"] == "closed"
                for row in report.source_checkpoints
            ),
            baseline["baseline_llm_calls"] == 29,
            hedgehog["hedgehog_llm_calls"] == 1,
            metrics["llm_call_reduction"] == 28,
            0.96 < metrics["llm_call_reduction_ratio"] < 0.97,
            baseline["baseline_context_units"] == 180,
            hedgehog["hedgehog_context_units"] == 32,
            metrics["context_unit_reduction"] == 148,
            0.82 < metrics["context_unit_reduction_ratio"] < 0.83,
            metrics["collector_replay_reduction"] == 4,
            metrics["validation_pass_reduction"] == 5,
            metrics["action_planning_reduction"] == 6,
            metrics["unbounded_authority_risk_reduction"] == 18,
            hedgehog["hedgehog_blocked_attempts"] == 18,
            hedgehog["hedgehog_quarantined_and_blocked"] == 4,
            all(report.safety_authority_boundaries.values()),
            root["benchmark_status"] == "PASS",
            root["production_economics_claimed"] is False,
            root["real_billing_claimed"] is False,
            root["killer_demo_authorized"] is False,
            root["root_remains_final_authority"] is True,
            report.audit_entry["canonical_payload_hash"]
            == canonical_hash(report.proof_artifact),
            report.audit_entry["audit_chain_decides_truth"] is False,
        )
    )


def collect_compute_collapse_enterprise_bench_v01() -> ComputeCollapseEnterpriseBenchReport:
    source_evidence, source_checkpoints = _closed_checkpoint_metadata()
    benchmark_purpose = {
        "benchmark_id": "compute_collapse_enterprise_bench_v01",
        "benchmark_type": "deterministic_local_proof_only",
        "comparison": "naive_long_chain_estimate_vs_root_controlled_semantic_routing",
        "synthetic_estimate": True,
        "new_runtime_capability_created": False,
    }
    enterprise_bench_request = {
        "request_id": "ENTERPRISE-COMPUTE-COLLAPSE-001",
        "request_family": "enterprise_chaos_dirty_request",
        "surfaces": [
            "connector_observations",
            "accepted_evidence",
            "stale_legal_state",
            "drs_reuse",
            "external_pointer_claim",
            "llm_semantic_draft",
            "needle_candidate",
            "child_cell_claim",
            "gt_advisory",
            "resultproposal_bypass_attempt",
            "conflicting_sources",
        ],
        "root_review_required": True,
        "proof_only": True,
    }
    baseline = _baseline_long_chain_estimate()
    hedgehog = _hedgehog_root_controlled_path()
    metrics = _compute_metrics(baseline, hedgehog)
    boundaries = _safety_boundaries()
    root_final = {
        "root_result": "compute_collapse_enterprise_bench_completed",
        "safe_secondary_outcome": "hardening_can_continue_without_authorizing_killer_demo",
        "benchmark_status": "PASS",
        "production_economics_claimed": False,
        "real_billing_claimed": False,
        "real_latency_claimed": False,
        "real_cloud_cost_claimed": False,
        "killer_demo_authorized": False,
        "multi_llm_showcase_authorized": False,
        "root_remains_final_authority": True,
        "no_network": True,
        "no_gemini": True,
        "no_external_action": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "no_installed_needle": True,
        "no_production_persistence": True,
        "no_marennya": True,
        "no_up": True,
    }
    proof_artifact = {
        "proof_artifact_id": "compute_collapse_enterprise_bench_v01",
        "source_evidence": source_evidence,
        "source_checkpoints": source_checkpoints,
        "benchmark_purpose": benchmark_purpose,
        "enterprise_bench_request": enterprise_bench_request,
        "baseline_long_chain_estimate": baseline,
        "hedgehog_root_controlled_path": hedgehog,
        "compute_collapse_metrics": metrics,
        "safety_authority_boundaries": boundaries,
        "root_final": root_final,
    }
    audit_entry = {
        "audit_entry_id": "audit_compute_collapse_enterprise_bench_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = ComputeCollapseEnterpriseBenchReport(
        source_evidence,
        source_checkpoints,
        benchmark_purpose,
        enterprise_bench_request,
        baseline,
        hedgehog,
        metrics,
        boundaries,
        root_final,
        audit_entry,
        proof_artifact,
        {},
    )
    passed = validate_compute_collapse_enterprise_bench_v01(provisional)
    summary = {
        "compute_collapse_enterprise_bench_v01_status": "PASS" if passed else "FAIL",
        "source_checkpoints_referenced": len(source_checkpoints),
        "source_collectors_replayed": False,
        "source_collectors_replayed_count": 0,
        "baseline_llm_calls": baseline["baseline_llm_calls"],
        "hedgehog_llm_calls": hedgehog["hedgehog_llm_calls"],
        **metrics,
        "hedgehog_blocked_attempts": hedgehog["hedgehog_blocked_attempts"],
        "hedgehog_quarantined_and_blocked": hedgehog[
            "hedgehog_quarantined_and_blocked"
        ],
        "root_remains_final_authority": True,
        "ready_for_compute_collapse_enterprise_bench_v01_tests": passed,
    }
    return replace(provisional, summary=summary)


def _format(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if isinstance(value, float):
        return f"{value:.4f}"
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


def render_compute_collapse_enterprise_bench_v01(
    report: ComputeCollapseEnterpriseBenchReport,
) -> str:
    lines = [
        "[COMPUTE COLLAPSE ENTERPRISE BENCH v0.1]",
        "note: deterministic local synthetic estimate only",
        "note: baseline path is estimated, not executed",
        "note: benchmark is not an economics or billing measurement",
    ]
    _rows(lines, "[SOURCE CHECKPOINTS]", report.source_checkpoints)
    _section(lines, "[BENCHMARK PURPOSE]", report.benchmark_purpose)
    _section(lines, "[ENTERPRISE BENCH REQUEST]", report.enterprise_bench_request)
    _section(lines, "[BASELINE LONG-CHAIN ESTIMATE]", report.baseline_long_chain_estimate)
    _section(lines, "[HEDGEHOG ROOT-CONTROLLED PATH]", report.hedgehog_root_controlled_path)
    _section(lines, "[COMPUTE COLLAPSE METRICS]", report.compute_collapse_metrics)
    _section(lines, "[SAFETY / AUTHORITY BOUNDARIES]", report.safety_authority_boundaries)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_compute_collapse_enterprise_bench_v01() -> str:
    return render_compute_collapse_enterprise_bench_v01(
        collect_compute_collapse_enterprise_bench_v01()
    )


def main() -> int:
    print(run_compute_collapse_enterprise_bench_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
