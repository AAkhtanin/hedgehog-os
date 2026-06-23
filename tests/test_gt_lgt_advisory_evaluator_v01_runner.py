from __future__ import annotations

import subprocess
import sys

import demo.run_gt_lgt_advisory_evaluator_v01 as runner
import hedgehog.gt_lgt_advisory_evaluator as evaluator
from demo import run_candidate_vector_generator_avf_scoring_v01 as avf_runner
from hedgehog.gt_lgt_advisory_evaluator import (
    AdvisoryEvaluationInput,
    AdvisorySignal,
    DECISION_VOCABULARY_MAPPING,
    GTLGTAdvisoryReport,
    build_advisory_report,
    evaluate_candidate_report,
    evaluate_gt_signal,
    evaluate_lgt_signal,
)


def _source_report(source_scenario_id: str = "high_score_candidate_still_requires_gt_lgt_root_review"):
    return avf_runner.evaluate_scenario(source_scenario_id)["report"]


def _input(
    *,
    top_score: float = 0.9,
    high_score: bool = True,
    conflict: bool = False,
    stale: bool = False,
    quarantine: bool = False,
    poisoning: bool = False,
) -> AdvisoryEvaluationInput:
    return AdvisoryEvaluationInput(
        candidate_vector_report_id="test_report",
        drs_candidate_refs=("record:test",),
        avf_score_refs=("vector:test",),
        ranked_candidate_ids=("candidate:test",),
        reason_codes=("test_reason",),
        conflict_flags=("conflicting_provenance",) if conflict else (),
        stale_flags=("stale_candidate",) if stale else (),
        quarantine_deadend_flags=("quarantine",) if quarantine else (),
        poisoning_flags=("poisoning_pressure",) if poisoning else (),
        provenance_refs=({"created_by": "root_orchestrator"},),
        trace_refs=({"trace_id": "trace:test"},),
        source_refs=({"source": "local_drs", "source_id": "source:test"},),
        root_review_required=True,
        direct_reuse_allowed=False,
        candidate_count=1,
        high_score_candidate_ids=("candidate:test",) if high_score else (),
        schema_valid_candidate_ids=("candidate:test",),
        top_score=top_score,
    )


def test_api_symbols_exist() -> None:
    assert evaluator.AdvisoryEvaluationInput is AdvisoryEvaluationInput
    assert evaluator.AdvisorySignal is AdvisorySignal
    assert evaluator.GTLGTAdvisoryReport is GTLGTAdvisoryReport
    assert callable(evaluator.evaluate_candidate_report)
    assert callable(evaluator.evaluate_gt_signal)
    assert callable(evaluator.evaluate_lgt_signal)
    assert callable(evaluator.build_advisory_report)


def test_build_advisory_report_returns_structured_report() -> None:
    report = build_advisory_report(_input())

    assert isinstance(report, GTLGTAdvisoryReport)
    assert report.candidate_count == 1
    assert report.root_review_required is True
    assert report.direct_reuse_allowed_count == 0
    assert report.action_permission_granted_count == 0
    assert report.final_output_created_count == 0
    assert report.root_final_authority_preserved is True
    assert report.counters["direct_reuse_allowed_count"] == 0
    assert report.counters["action_permission_granted_count"] == 0
    assert report.counters["final_output_created_count"] == 0
    assert report.counters["gt_authority_claimed_count"] == 0
    assert report.counters["lgt_authority_claimed_count"] == 0
    assert report.counters["advisory_truth_claimed_count"] == 0


def test_evaluate_candidate_report_returns_candidate_advisory_only_report() -> None:
    report = evaluate_candidate_report(_source_report())
    gt_signal = next(signal for signal in report.signals if signal.signal_kind == "gt")

    assert report.candidate_count == 1
    assert gt_signal.advisory_decision == "accept_candidate"
    assert gt_signal.authority_claimed is False
    assert gt_signal.truth_claimed is False
    assert gt_signal.action_permission_claimed is False
    assert gt_signal.final_output_claimed is False
    assert gt_signal.direct_reuse_allowed is False
    assert report.root_review_required is True


def test_evaluate_gt_and_lgt_signals_are_advisory_only() -> None:
    advisory_input = AdvisoryEvaluationInput.from_candidate_report(_source_report())
    gt_signal = evaluate_gt_signal(advisory_input, _source_report())
    lgt_signal = evaluate_lgt_signal(advisory_input)

    assert gt_signal.signal_kind == "gt"
    assert gt_signal.advisory_decision == "accept_candidate"
    assert gt_signal.authority_claimed is False
    assert gt_signal.truth_claimed is False
    assert gt_signal.action_permission_claimed is False
    assert gt_signal.final_output_claimed is False
    assert gt_signal.direct_reuse_allowed is False
    assert gt_signal.root_review_required is True

    assert lgt_signal.signal_kind == "lgt_deferred"
    assert lgt_signal.advisory_decision == "no_update"
    assert lgt_signal.metadata["concrete_lgt_runtime_module"] == "absent"
    assert lgt_signal.authority_claimed is False
    assert lgt_signal.truth_claimed is False
    assert lgt_signal.action_permission_claimed is False
    assert lgt_signal.final_output_claimed is False
    assert lgt_signal.direct_reuse_allowed is False
    assert lgt_signal.root_review_required is True


def test_decision_vocabulary_mapping_is_preserved() -> None:
    assert DECISION_VOCABULARY_MAPPING["accept_candidate"] == (
        "advisory accept only, not Root Final"
    )
    assert DECISION_VOCABULARY_MAPPING["degrade_candidate"] == (
        "existing revise / needs_user style semantics"
    )
    assert DECISION_VOCABULARY_MAPPING["reject_candidate"] == (
        "candidate route block, not Root Final rejection"
    )
    assert DECISION_VOCABULARY_MAPPING["needs_review"] == "Root review required"
    assert DECISION_VOCABULARY_MAPPING["no_update"] == (
        "advisory no_update only, not final rejection"
    )


def test_high_avf_score_and_stale_pressure_cannot_force_gt_accept() -> None:
    report = build_advisory_report(_input(stale=True))
    gt_signal = next(signal for signal in report.signals if signal.signal_kind == "gt")

    assert gt_signal.advisory_decision == "degrade_candidate"
    assert report.counters["high_score_forced_accept_count"] == 0
    assert report.counters["stale_silent_accept_count"] == 0
    assert "stale_high_score_candidate_cannot_silent_accept" in report.reason_codes


def test_quarantine_deadend_overrides_high_score_to_review() -> None:
    report = build_advisory_report(_input(quarantine=True))
    gt_signal = next(signal for signal in report.signals if signal.signal_kind == "gt")

    assert gt_signal.advisory_decision == "reject_candidate"
    assert report.counters["quarantine_deadend_override_count"] == 0
    assert "quarantine_deadend_overrides_high_score_to_review" in report.reason_codes


def test_conflicting_provenance_blocks_advisory_accept() -> None:
    report = build_advisory_report(_input(conflict=True))
    gt_signal = next(signal for signal in report.signals if signal.signal_kind == "gt")

    assert gt_signal.advisory_decision == "reject_candidate"
    assert report.counters["conflicting_provenance_hidden_count"] == 0
    assert "conflicting_provenance_blocks_advisory_accept" in report.reason_codes


def test_duplicate_spam_cannot_force_gt_lgt_accept() -> None:
    report = build_advisory_report(_input(poisoning=True))
    gt_signal = next(signal for signal in report.signals if signal.signal_kind == "gt")

    assert gt_signal.advisory_decision == "needs_review"
    assert report.counters["duplicate_spam_forced_accept_count"] == 0
    assert "duplicate_spam_cannot_force_gt_lgt_accept" in report.reason_codes


def test_runner_result_passes_required_counters_and_scenarios() -> None:
    result = runner.run_all_scenarios()
    counters = result["counters"]

    assert result["scenarios_total"] == 10
    assert result["scenarios_passed"] == result["scenarios_total"]
    assert {scenario["scenario_id"] for scenario in result["scenarios"]} == set(
        runner.SCENARIOS
    )
    assert all(scenario["status"] == "PASS" for scenario in result["scenarios"])
    assert counters["direct_reuse_allowed_count"] == 0
    assert counters["action_permission_granted_count"] == 0
    assert counters["final_output_created_count"] == 0
    assert counters["gt_authority_claimed_count"] == 0
    assert counters["lgt_authority_claimed_count"] == 0
    assert counters["advisory_truth_claimed_count"] == 0
    assert counters["advisory_accept_as_root_final_count"] == 0
    assert counters["high_score_forced_accept_count"] == 0
    assert counters["duplicate_spam_forced_accept_count"] == 0
    assert counters["stale_silent_accept_count"] == 0
    assert counters["quarantine_deadend_override_count"] == 0
    assert counters["conflicting_provenance_hidden_count"] == 0
    assert counters["manifest_mutation_count"] == 0
    assert counters["transition_matrix_mutation_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["root_final_authority_preserved_count"] == result["scenarios_total"]


def test_main_returns_zero_and_command_output_has_pass() -> None:
    assert runner.main() == 0

    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_gt_lgt_advisory_evaluator_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    expected_markers = (
        "FINAL STATUS: PASS",
        "scenarios_total: 10",
        "scenarios_passed: 10",
        "direct_reuse_allowed_count: 0",
        "action_permission_granted_count: 0",
        "final_output_created_count: 0",
        "gt_authority_claimed_count: 0",
        "lgt_authority_claimed_count: 0",
        "advisory_truth_claimed_count: 0",
        "root_final_authority_preserved_count: 10",
    )
    for marker in expected_markers:
        assert marker in completed.stdout


def test_runner_output_does_not_claim_public_or_runtime_completion() -> None:
    output = runner.render_report(runner.run_all_scenarios())
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "runtime " + "complete",
        "GT is " + "authority",
        "LGT is " + "authority",
        "GT/LGT report is " + "truth",
    )

    for marker in forbidden:
        assert marker not in output
