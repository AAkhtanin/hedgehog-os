from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_compute_collapse_enterprise_bench_v01 import (
    collect_compute_collapse_enterprise_bench_v01,
    render_compute_collapse_enterprise_bench_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_compute_collapse_enterprise_bench_v01()


def test_renderer_has_required_sections(report):
    output = render_compute_collapse_enterprise_bench_v01(report)
    for section in (
        "[SOURCE CHECKPOINTS]",
        "[BENCHMARK PURPOSE]",
        "[ENTERPRISE BENCH REQUEST]",
        "[BASELINE LONG-CHAIN ESTIMATE]",
        "[HEDGEHOG ROOT-CONTROLLED PATH]",
        "[COMPUTE COLLAPSE METRICS]",
        "[SAFETY / AUTHORITY BOUNDARIES]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert section in output


def test_closed_checkpoint_metadata_has_no_replay(report):
    source = report.source_evidence
    assert source["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert source["source_collectors_replayed"] is False
    assert source["source_collectors_replayed_count"] == 0
    assert source["source_checkpoints_referenced"] == 5
    assert len(report.source_checkpoints) == 5
    assert all(row["checkpoint_status"] == "PASS" for row in report.source_checkpoints)
    assert all(row["closure_status"] == "closed" for row in report.source_checkpoints)


def test_llm_call_compute_collapse_metrics(report):
    baseline = report.baseline_long_chain_estimate
    hedgehog = report.hedgehog_root_controlled_path
    metrics = report.compute_collapse_metrics
    assert baseline["baseline_llm_calls"] == 29
    assert hedgehog["hedgehog_llm_calls"] == 1
    assert metrics["llm_call_reduction"] == 28
    assert 0.96 < metrics["llm_call_reduction_ratio"] < 0.97


def test_context_compute_collapse_metrics(report):
    baseline = report.baseline_long_chain_estimate
    hedgehog = report.hedgehog_root_controlled_path
    metrics = report.compute_collapse_metrics
    assert baseline["baseline_context_units"] == 180
    assert hedgehog["hedgehog_context_units"] == 32
    assert metrics["context_unit_reduction"] == 148
    assert 0.82 < metrics["context_unit_reduction_ratio"] < 0.83


def test_replay_validation_action_and_authority_reductions(report):
    metrics = report.compute_collapse_metrics
    assert metrics["collector_replay_reduction"] == 4
    assert metrics["validation_pass_reduction"] == 5
    assert metrics["action_planning_reduction"] == 6
    assert metrics["unbounded_authority_risk_reduction"] == 18


def test_hedgehog_path_remains_bounded(report):
    path = report.hedgehog_root_controlled_path
    assert path["hedgehog_collector_replays"] == 0
    assert path["hedgehog_action_planning_steps"] == 0
    assert path["hedgehog_unbounded_authority_risk_units"] == 0
    assert path["hedgehog_failed_attempts"] == 0
    assert path["hedgehog_blocked_attempts"] == 18
    assert path["hedgehog_quarantined_and_blocked"] == 4
    assert path["bounded_llm_use_only"] is True


def test_all_safety_and_authority_boundaries_hold(report):
    assert all(value is True for value in report.safety_authority_boundaries.values())


def test_root_final_preserves_anti_overclaim_boundaries(report):
    root = report.root_final
    assert root["root_result"] == "compute_collapse_enterprise_bench_completed"
    assert root["benchmark_status"] == "PASS"
    assert root["production_economics_claimed"] is False
    assert root["real_billing_claimed"] is False
    assert root["real_latency_claimed"] is False
    assert root["real_cloud_cost_claimed"] is False
    assert root["killer_demo_authorized"] is False
    assert root["multi_llm_showcase_authorized"] is False
    assert root["root_remains_final_authority"] is True


def test_no_external_or_deferred_system_is_used(report):
    root = report.root_final
    for field in (
        "no_network",
        "no_gemini",
        "no_external_action",
        "no_global_drs_write",
        "no_external_drs_write",
        "no_installed_needle",
        "no_production_persistence",
        "no_marennya",
        "no_up",
    ):
        assert root[field] is True


def test_audit_hash_matches_canonical_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(report.proof_artifact)
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_status_and_expected_metrics(report):
    summary = report.summary
    assert summary["compute_collapse_enterprise_bench_v01_status"] == "PASS"
    assert summary["source_checkpoints_referenced"] == 5
    assert summary["source_collectors_replayed"] is False
    assert summary["source_collectors_replayed_count"] == 0
    assert summary["baseline_llm_calls"] == 29
    assert summary["hedgehog_llm_calls"] == 1
    assert summary["llm_call_reduction"] == 28
    assert summary["context_unit_reduction"] == 148
    assert summary["hedgehog_blocked_attempts"] == 18
    assert summary["hedgehog_quarantined_and_blocked"] == 4
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_compute_collapse_enterprise_bench_v01_tests"] is True
