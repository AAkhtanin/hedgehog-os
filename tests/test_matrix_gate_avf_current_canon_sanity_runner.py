from __future__ import annotations

from demo.run_matrix_gate_avf_current_canon_sanity import (
    collect_matrix_gate_avf_current_canon_sanity,
    run_matrix_gate_avf_current_canon_sanity,
)


def _report():
    return collect_matrix_gate_avf_current_canon_sanity()


def test_runner_contains_required_sections():
    output = run_matrix_gate_avf_current_canon_sanity()
    for heading in (
        "[MATRIX GATE / AVF CURRENT CANON SANITY]",
        "[INPUT / MODE]",
        "[MATRIX GATE SOURCE]",
        "[AVF SOURCE]",
        "[DRS BOUNDARY REFERENCE]",
        "[LIVE DUAL-GEMINI EVIDENCE REFERENCE]",
        "[CURRENT CANON CHECKS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_existing_collectors_are_consumed_and_pass():
    report = _report()
    assert report.matrix_gate_source["source_collector"] == (
        "collect_controlled_orchestrator_matrix_gate"
    )
    assert report.avf_source["source_collector"] == (
        "collect_avf_attractor_from_accepted_matrix"
    )
    assert report.drs_boundary_reference["source_collector"] == (
        "collect_drs_writeback_from_root_final"
    )
    assert report.summary["matrix_gate_source_status"] == "PASS"
    assert report.summary["avf_source_status"] == "PASS"
    assert report.summary["drs_boundary_reference_status"] == "PASS"


def test_matrix_gate_current_authority_and_rejection_boundaries():
    source = _report().matrix_gate_source
    assert source["source_checks_passed"] is True
    assert source["root_authority_preserved"] is True
    assert source["root_created_gate_decisions"] is True
    assert source["orchestrator_matrix_is_authority"] is False
    assert source["rejected_matrix_reaches_avf"] is False
    assert source["orchestrator_creates_final_output"] is False
    assert source["orchestrator_writes_drs"] is False
    assert source["orchestrator_executes_actions"] is False


def test_avf_current_boundaries():
    source = _report().avf_source
    assert source["rejected_matrices_blocked_before_avf"] is True
    assert source["avf_independent"] is True
    assert source["hardmask_beats_orchestrator_confidence"] is True
    assert source["policy_beats_orchestrator_confidence"] is True
    assert source["forbidden_vectors_passed_to_architect"] is False
    assert source["architect_input_bounded"] is True
    assert source["avf_creates_final_output"] is False
    assert source["avf_writes_drs"] is False
    assert source["avf_executes_actions"] is False


def test_drs_boundary_has_no_authority_or_persistence_leak():
    drs = _report().drs_boundary_reference
    assert drs["writeback_scope_local_audit_only"] is True
    assert drs["drs_is_authority"] is False
    assert drs["root_authority_preserved"] is True
    assert drs["production_persistence_claimed"] is False
    assert drs["production_external_action_executed"] is False
    assert drs["external_drs_network_implemented"] is False
    assert drs["global_drs_implemented"] is False
    assert drs["root_writes_drs_claim_rejected"] is True
    assert drs["production_persistence_claim_rejected"] is True
    assert drs["external_drs_network_claim_rejected"] is True


def test_live_evidence_is_reference_only_and_no_network_is_used():
    report = _report()
    assert report.input_mode["live_network_used"] is False
    assert report.live_dual_gemini_evidence_reference[
        "live_evidence_used_as_runtime_input"
    ] is False


def test_current_canon_checks_all_pass():
    checks = _report().current_canon_checks
    assert all(checks.values())
    assert checks["no_orchestrator_authority_leak"] is True
    assert checks["no_avf_bypass"] is True
    assert checks["no_forbidden_vector_leak_to_architect"] is True
    assert checks["no_drs_authority_leak"] is True
    assert checks["no_production_persistence_leak"] is True
    assert checks["no_external_global_drs_leak"] is True
    assert checks["no_root_writes_drs_claim_leak"] is True
    assert checks["no_real_action_leak"] is True


def test_authority_and_safety_boundaries_hold():
    authority = _report().authority_safety
    assert authority["root_remains_authority"] is True
    assert authority["orchestrator_is_not_root"] is True
    assert authority["avf_is_not_root"] is True
    assert authority["drs_is_not_root"] is True
    assert authority["matrix_is_proposal_only"] is True
    assert authority["attractor_packet_is_bounded_input_only"] is True
    assert authority["production_persistence_claimed"] is False
    assert authority["production_external_action_executed"] is False
    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_is_derived_from_sources_and_current_canon_checks():
    report = _report()
    summary = report.summary
    derived_pass = (
        summary["matrix_gate_source_status"] == "PASS"
        and summary["avf_source_status"] == "PASS"
        and summary["drs_boundary_reference_status"] == "PASS"
        and summary["current_canon_checks_passed"] is True
        and report.authority_safety["root_remains_authority"] is True
        and report.authority_safety["production_persistence_claimed"] is False
        and report.authority_safety["production_external_action_executed"] is False
    )
    assert derived_pass is True
    assert summary["matrix_gate_avf_current_canon_sanity_status"] == "PASS"
    assert summary["ready_for_root_native_sandbox_needleruntime_e2e"] is True
    assert summary["production_autonomy_claimed"] is False
