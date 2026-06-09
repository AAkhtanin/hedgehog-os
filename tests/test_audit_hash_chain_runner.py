from __future__ import annotations

import copy
import hashlib
import json

from demo.run_audit_hash_chain import (
    ENTRY_SPECS,
    canonical_hash,
    canonical_json,
    collect_audit_hash_chain,
    run_audit_hash_chain,
    verify_audit_chain,
)


def _report():
    return collect_audit_hash_chain()


def test_runner_contains_required_sections():
    output = run_audit_hash_chain()
    for heading in (
        "[AUDIT HASH CHAIN]",
        "[INPUT / MODE]",
        "[SOURCE REPORTS]",
        "[AUDIT CHAIN ENTRIES]",
        "[CHAIN SUMMARY]",
        "[TAMPER CHECKS]",
        "[MALICIOUS CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_canonical_json_hashing_is_sorted_compact_and_deterministic():
    left = {"z": [2, 1], "a": {"b": True, "a": "meaning"}}
    right = {"a": {"a": "meaning", "b": True}, "z": [2, 1]}
    expected_json = json.dumps(
        left, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected_hash = hashlib.sha256(expected_json.encode("utf-8")).hexdigest()
    assert canonical_json(left) == expected_json
    assert canonical_json(left) == canonical_json(right)
    assert canonical_hash(left) == expected_hash == canonical_hash(right)


def test_all_required_source_collectors_are_consumed_without_network():
    report = _report()
    source = report.source_reports
    assert source["source_reports_consumed"] == [
        "collect_conflictcheck",
        "collect_drs_lifecycle_semantics",
        "collect_live_child_executor_in_fractal_cell",
        "collect_drs_writeback_from_root_final",
        "collect_root_native_sandbox_needleruntime_e2e",
        "collect_fractal_cell_runtime",
    ]
    assert report.input_mode["live_network_used"] is False
    assert source["source_artifacts_unchanged"] is True


def test_required_source_statuses_are_visible_and_valid():
    source = _report().source_reports
    assert source["conflictcheck_status"] == "PASS"
    assert source["drs_lifecycle_semantics_status"] == "PASS"
    assert source["live_child_executor_reference_status"] in {
        "PASS",
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS",
    }
    assert source["drs_writeback_status"] == "PASS"
    assert source["needleruntime_status"] == "PASS"
    assert source["fractal_cell_status"] == "PASS"


def test_entries_cover_all_required_source_artifacts():
    entries = _report().audit_chain_entries
    assert [(row["entry_type"], row["source_artifact_type"]) for row in entries] == list(
        ENTRY_SPECS
    )
    assert len(entries) == 7
    assert entries[3]["_source_payload"]["live_network_used"] is False
    assert entries[4]["_source_payload"]["drs_lifecycle_semantics_status"] == "PASS"
    assert entries[5]["_source_payload"]["conflictcheck_status"] == "PASS"
    assert set(entries[6]["_source_payload"]["closed_layers"]) == {
        "live_child_executor",
        "drs_lifecycle",
        "conflictcheck",
        "root_centered_geometry_docs",
    }


def test_every_entry_has_payload_hash_entry_hash_and_safety_fields():
    for entry in _report().audit_chain_entries:
        assert len(entry["canonical_payload_hash"]) == 64
        assert len(entry["entry_hash"]) == 64
        assert entry["proof_only"] is True
        assert entry["append_only"] is True
        assert entry["root_authority_preserved"] is True
        assert entry["audit_chain_is_authority"] is False
        assert entry["mutates_source_artifact"] is False
        assert entry["production_persistence"] is False
        assert entry["global_drs_write"] is False
        assert entry["external_drs_network_write"] is False


def test_chain_linkage_and_continuity_are_valid():
    report = _report()
    entries = report.audit_chain_entries
    for previous, current in zip(entries, entries[1:]):
        assert current["previous_entry_hash"] == previous["entry_hash"]
    assert verify_audit_chain(entries) is True
    assert report.chain_summary["chain_continuity_valid"] is True


def test_payload_or_linkage_mutation_invalidates_chain_without_mutating_original():
    report = _report()
    original = copy.deepcopy(report.audit_chain_entries)
    payload_tampered = copy.deepcopy(original)
    payload_tampered[0]["_source_payload"]["tampered"] = True
    linkage_tampered = copy.deepcopy(original)
    linkage_tampered[1]["previous_entry_hash"] = "0" * 64
    assert verify_audit_chain(payload_tampered) is False
    assert verify_audit_chain(linkage_tampered) is False
    assert report.audit_chain_entries == original


def test_all_required_tamper_checks_detect_changes():
    checks = _report().tamper_checks
    assert checks == {
        "payload_tamper_detected": True,
        "previous_hash_tamper_detected": True,
        "entry_reorder_detected": True,
        "missing_entry_detected": True,
        "injected_entry_detected": True,
        "authority_claim_tamper_detected": True,
        "production_persistence_claim_tamper_detected": True,
        "global_drs_claim_tamper_detected": True,
    }


def test_append_only_semantics_and_source_immutability_are_preserved():
    report = _report()
    assert report.chain_summary["append_only_semantics_preserved"] is True
    assert report.chain_summary["source_artifacts_unchanged"] is True
    assert report.authority_safety["source_artifacts_unchanged"] is True


def test_all_malicious_claims_are_rejected():
    malicious = _report().malicious_claims
    rejected = {
        key: value
        for key, value in malicious.items()
        if key.startswith("malicious_") and key.endswith("_rejected")
    }
    assert len(rejected) == 8
    assert all(rejected.values())
    assert malicious["audit_chain_decides_truth"] is False
    assert malicious["audit_chain_mutates_drs"] is False
    assert malicious["audit_chain_mutates_source_artifact"] is False
    assert malicious["audit_chain_grants_authority"] is False
    assert malicious["production_persistence"] is False
    assert malicious["global_drs_write"] is False
    assert malicious["external_drs_network_write"] is False
    assert malicious["real_external_action"] is False


def test_audit_chain_has_no_authority_or_mutation_power():
    authority = _report().authority_safety
    assert authority["audit_chain_is_authority"] is False
    assert authority["audit_chain_decides_truth"] is False
    assert authority["audit_chain_mutates_drs"] is False
    assert authority["audit_chain_mutates_source_artifacts"] is False
    assert authority["audit_chain_grants_authority"] is False
    assert authority["root_remains_final_authority"] is True


def test_gt_conflictcheck_and_drs_lifecycle_boundaries_remain_intact():
    authority = _report().authority_safety
    assert authority["gt_remains_advisory_until_root"] is True
    assert authority["conflictcheck_remains_advisory_until_root"] is True
    assert authority["drs_lifecycle_remains_storage_index_lifecycle"] is True


def test_no_production_external_or_deferred_systems_are_invoked():
    report = _report()
    mode = report.input_mode
    authority = report.authority_safety
    assert mode["production_persistence"] is False
    assert mode["global_drs_implemented"] is False
    assert mode["external_drs_network_implemented"] is False
    assert mode["telegram_used"] is False
    assert mode["real_external_action"] is False
    assert authority["production_persistence_claimed"] is False
    assert authority["production_external_action_executed"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_summary_pass_derives_from_sources_chain_tamper_and_authority_facts():
    report = _report()
    summary = report.summary
    assert summary["audit_hash_chain_status"] == "PASS"
    assert summary["entries_created"] == len(report.audit_chain_entries) == 7
    assert summary["source_reports_consumed"] == len(
        report.source_reports["source_reports_consumed"]
    )
    assert summary["chain_continuity_valid"] is True
    assert summary["tamper_detection_valid"] is True
    assert summary["append_only_semantics_preserved"] is True
    assert summary["source_artifacts_unchanged"] is True
    assert summary["malicious_claims_rejected"] == 8
    assert summary["root_remains_final_authority"] is True
    assert summary["local_proof_level_only"] is True
    assert summary["ready_for_controlled_root_orchestrator_integration"] is True
    assert summary["production_autonomy_claimed"] is False
