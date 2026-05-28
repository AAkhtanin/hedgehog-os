from __future__ import annotations

from demo.run_cold_start_benchmark import collect_cold_start_benchmark
from demo.run_cold_start_benchmark import run_cold_start_benchmark


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def _phase(report, name: str):
    for phase in report.phases:
        if phase.phase == name:
            return phase
    raise AssertionError(f"missing phase {name}")


def test_cold_start_benchmark_prints_all_phases():
    output = run_cold_start_benchmark()

    assert "[COLD START BENCHMARK]" in output
    assert "empty_drs_precheck" in output
    assert "first_run_cold_start" in output
    assert "after_first_writeback" in output
    assert "second_run_memory_influence" in output
    assert "seeded_direct_reuse_eligible_run" in output


def test_cold_start_starts_empty_without_direct_reuse():
    report = collect_cold_start_benchmark()
    phase = _phase(report, "empty_drs_precheck")

    assert report.work_records_before == 0
    assert report.direct_reuse_available_before is False
    assert phase.status == "PASS"
    assert "work_records_before=0" in phase.evidence
    assert "direct_reuse_available_before=false" in phase.evidence


def test_first_run_succeeds_without_direct_reuse_and_writes_work():
    report = collect_cold_start_benchmark()
    phase = _phase(report, "first_run_cold_start")

    assert report.cold_start_first_run_success is True
    assert phase.status == "PASS"
    assert phase.route == "proof_full_pipeline"
    assert phase.reuse_applied is False
    assert phase.direct_reuse_applied is False
    assert phase.architect_skipped is False
    assert phase.executor_skipped is False
    assert phase.drs_writes >= 1
    assert report.first_run_wrote_memory is True


def test_first_work_record_has_time_envelope_and_structured_writeback():
    report = collect_cold_start_benchmark()
    phase = _phase(report, "after_first_writeback")

    assert report.work_records_after_first >= 1
    assert report.first_work_has_time_envelope is True
    assert report.first_work_sensitive_input_absent is True
    assert report.first_work_structured_fields_present is True
    assert phase.status == "PASS"
    assert "time_envelope=true" in phase.evidence
    assert "sensitive_input_absent=true" in phase.evidence
    assert "structured_fields=true" in phase.evidence


def test_second_run_shows_memory_influence_without_faking_direct_reuse():
    report = collect_cold_start_benchmark()
    phase = _phase(report, "second_run_memory_influence")

    assert report.second_run_memory_influenced is True
    assert (
        phase.memory_context_applied is True
        or phase.retrieved_records > 0
    )
    if phase.direct_reuse_applied:
        assert phase.reuse_decision == "direct_reuse"
    else:
        assert phase.reuse_applied is False
        assert phase.reuse_decision in {"context_only", "none", "direct_reuse_candidate"}


def test_seeded_direct_reuse_applies_and_skips_compute():
    report = collect_cold_start_benchmark()
    phase = _phase(report, "seeded_direct_reuse_eligible_run")

    assert report.seeded_direct_reuse_success is True
    assert phase.status == "PASS"
    assert phase.route == "direct_reuse"
    assert phase.reuse_applied is True
    assert phase.direct_reuse_applied is True
    assert phase.architect_skipped is True
    assert phase.executor_skipped is True


def test_root_authority_and_summary_flags_are_preserved():
    report = collect_cold_start_benchmark()
    output = run_cold_start_benchmark()

    assert report.root_final_authority_preserved is True
    assert report.direct_reuse_requires_eligibility is True
    assert "cold_start_first_run_success: true" in output
    assert "first_run_wrote_memory: true" in output
    assert "second_run_memory_influenced: true" in output
    assert "direct_reuse_requires_eligibility: true" in output
    assert "seeded_direct_reuse_success: true" in output
    assert "root_final_authority_preserved: true" in output
    assert "no_real_external_actions: true" in output
    assert "live_gemini: false" in output


def test_cold_start_output_is_safe():
    output = run_cold_start_benchmark().lower()

    assert "note: no live gemini by default" in output
    assert "note: no real external actions" in output
    for term in FORBIDDEN_TERMS:
        assert term not in output
