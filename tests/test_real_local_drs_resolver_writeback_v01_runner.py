from __future__ import annotations

import subprocess
import sys

import pytest

from hedgehog.drs import LocalDRS
from hedgehog.local_drs_resolver import (
    SemanticDRSRecordInput,
    SemanticResolveQuery,
    ResolvedDRSCandidate,
    ResolvedDRSReport,
    resolve_semantic_candidates,
    write_root_final_record,
    write_semantic_record,
)
from demo.run_real_local_drs_resolver_writeback_v01 import (
    main,
    run_all_scenarios,
)


NOW = "2026-06-22T12:00:00+00:00"
OLD = "2026-01-01T00:00:00+00:00"


def _time_envelope(created_at=NOW, freshness_class="normal"):
    return {
        "pt_created_at": created_at,
        "kt_asof": created_at,
        "et_observed_at": created_at,
        "ct_session_anchor": "sess_test_real_local_drs_resolver_v01",
        "ttl_seconds": 86_400,
        "freshness_class": freshness_class,
        "valid_from": created_at,
        "valid_to": None,
    }


def _temporal_query():
    return {
        "as_of": NOW,
        "time_range": {"from": None, "to": NOW},
        "freshness_bias": "prefer_recent",
        "max_age_seconds": 86_400,
        "freshness_required": "normal",
    }


def _record_input(record_id, **overrides):
    content = {
        "summary": "Mock certificate renewal candidate.",
        "subject_key": "certificate:demo-user",
        "claim_key": "document_readiness",
        "claim_value": "ready",
        "worldstate": {"worldstate_version": "v1"},
        "schema_valid": True,
    }
    content.update(overrides.pop("content", {}))
    return SemanticDRSRecordInput(
        record_id=record_id,
        domain="mock_government_certificate",
        content=content,
        semantic_keys=("certificate", "renewal", "document_readiness"),
        time_envelope=overrides.pop("time_envelope", _time_envelope()),
        trace_refs=({"trace_id": f"trace:{record_id}", "kind": "test"},),
        source_refs=(
            {
                "source": "local_drs",
                "source_id": f"source:{record_id}",
                "trace_ref": {"trace_id": f"trace:{record_id}", "kind": "test"},
            },
        ),
        **overrides,
    )


def _query(**overrides):
    return SemanticResolveQuery(
        query_id=overrides.pop("query_id", "query:test"),
        domain="mock_government_certificate",
        semantic_terms=("certificate", "renewal", "document_readiness"),
        content_filters={"subject_key": "certificate:demo-user"},
        temporal_query=_temporal_query(),
        worldstate=overrides.pop("worldstate", {"worldstate_version": "v1"}),
        require_root_review=True,
        **overrides,
    )


def test_api_dataclasses_and_functions_exist():
    assert SemanticDRSRecordInput
    assert SemanticResolveQuery
    assert ResolvedDRSCandidate
    assert ResolvedDRSReport
    assert callable(write_semantic_record)
    assert callable(resolve_semantic_candidates)
    assert callable(write_root_final_record)


def test_write_semantic_record_writes_local_drs_record(tmp_path):
    drs = LocalDRS(tmp_path)
    record = write_semantic_record(drs, _record_input("record:test_write"))

    loaded = drs.read_record("work", "record:test_write")
    assert loaded == record
    assert loaded["domain"] == "mock_government_certificate"
    assert loaded["content"]["drs_record_is_truth"] is False


def test_resolve_semantic_candidates_returns_candidates_only(tmp_path):
    drs = LocalDRS(tmp_path)
    write_semantic_record(drs, _record_input("record:candidate_only"))

    report = resolve_semantic_candidates(drs, _query())

    assert report.candidate_count == 1
    assert report.direct_reuse_allowed_count == 0
    assert report.counters["direct_reuse_allowed_count"] == 0
    assert report.counters["action_permission_granted_count"] == 0
    assert report.candidates[0].review_required is True
    assert report.candidates[0].action_permission_granted is False


def test_stale_record_forces_root_review(tmp_path):
    drs = LocalDRS(tmp_path)
    write_semantic_record(
        drs,
        _record_input(
            "record:stale",
            time_envelope=_time_envelope(OLD, "stale"),
        ),
    )

    report = resolve_semantic_candidates(drs, _query())

    assert report.candidates[0].stale is True
    assert report.counters["stale_record_reuse_blocked_count"] == 1
    assert "stale_record_forces_root_review" in report.reason_codes


def test_quarantine_and_deadend_block_direct_reuse(tmp_path):
    drs = LocalDRS(tmp_path)
    write_semantic_record(
        drs,
        _record_input(
            "record:quarantine",
            layer="quarantine",
            status="quarantined",
            content={"quarantine_proximity": True},
        ),
    )
    write_semantic_record(
        drs,
        _record_input(
            "record:deadend",
            layer="deadends",
            record_type="dead_end",
            status="rejected",
            content={"deadend_proximity": True},
        ),
    )

    report = resolve_semantic_candidates(drs, _query(max_candidates=4))

    assert report.counters["quarantine_reuse_blocked_count"] == 2
    assert all(candidate.direct_reuse_allowed is False for candidate in report.candidates)
    assert "quarantine_proximity_blocks_direct_reuse" in report.reason_codes


def test_changed_worldstate_blocks_old_reuse(tmp_path):
    drs = LocalDRS(tmp_path)
    write_semantic_record(drs, _record_input("record:old_worldstate"))

    report = resolve_semantic_candidates(
        drs,
        _query(worldstate={"worldstate_version": "v2"}),
    )

    assert report.candidates[0].changed_worldstate is True
    assert report.counters["changed_worldstate_reuse_blocked_count"] == 1
    assert "changed_worldstate_blocks_old_reuse" in report.reason_codes


def test_conflicting_provenance_blocks_reuse(tmp_path):
    drs = LocalDRS(tmp_path)
    write_semantic_record(
        drs,
        _record_input(
            "record:conflict",
            content={"conflicting_provenance": True},
        ),
    )

    report = resolve_semantic_candidates(drs, _query())

    assert report.candidates[0].conflicting_provenance is True
    assert report.counters["conflicting_provenance_blocked_count"] == 1
    assert "conflicting_provenance_blocks_reuse" in report.reason_codes


def test_duplicate_poisoning_pressure_does_not_create_authority(tmp_path):
    drs = LocalDRS(tmp_path)
    for suffix in ("a", "b"):
        record_input = _record_input(
            f"record:duplicate:{suffix}",
            content={
                "duplicate_group": "poisoned_certificate_reuse",
                "poisoning_markers": ["duplicate_spam"],
                "repeated_external_pointer_count": 3,
            },
        )
        write_semantic_record(drs, record_input)

    report = resolve_semantic_candidates(drs, _query(max_candidates=4))

    assert report.counters["duplicate_poisoning_records_seen_count"] == 2
    assert report.counters["poisoning_pressure_authority_claimed_count"] == 0
    assert all(candidate.direct_reuse_allowed is False for candidate in report.candidates)
    assert "duplicate_poisoning_pressure_does_not_create_authority" in report.reason_codes


def test_write_root_final_record_writes_without_action_side_effects(tmp_path):
    drs = LocalDRS(tmp_path)
    record = write_root_final_record(
        drs,
        {
            "artifact_type": "RootFinal",
            "final_artifact_id": "root_final:test:001",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
            "domain": "mock_government_certificate",
            "trace_refs": [{"trace_id": "trace:root_final_test", "kind": "test"}],
            "production_persistence_claimed": False,
            "real_external_action_executed": False,
            "connector_side_effects": False,
        },
    )

    loaded = drs.read_record("work", record["record_id"])
    assert loaded["content"]["local_writeback_only"] is True
    assert loaded["content"]["action_side_effects"] is False
    assert loaded["content"]["connector_side_effects"] is False
    assert loaded["content"]["root_final_authority_preserved"] is True


def test_write_root_final_record_rejects_raw_artifacts(tmp_path):
    drs = LocalDRS(tmp_path)
    with pytest.raises(ValueError):
        write_root_final_record(
            drs,
            {
                "artifact_type": "ValidationPacket",
                "packet_id": "packet:raw",
                "created_by": "validator",
                "root_reviewed": False,
            },
        )


@pytest.mark.parametrize(
    "artifact",
    [
        {
            "artifact_type": "ValidationPacket",
            "packet_id": "packet:root_claim",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "validation_packet",
            "packet_id": "packet:snake_root_claim",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "EvidenceCandidate",
            "candidate_id": "candidate:root_claim",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "evidence_candidate",
            "candidate_id": "candidate:snake_root_claim",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "ResultProposal",
            "result_payload": {"summary": "raw result proposal"},
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "result_proposal",
            "result_payload": {"summary": "raw result proposal"},
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "ConnectorObservation",
            "observation_id": "observation:root_claim",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
        {
            "artifact_type": "connector_observation",
            "observation_id": "observation:snake_root_claim",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
        },
    ],
)
def test_write_root_final_record_rejects_root_reviewed_raw_shapes(tmp_path, artifact):
    drs = LocalDRS(tmp_path)

    with pytest.raises(ValueError):
        write_root_final_record(drs, artifact)


def test_write_root_final_record_rejects_external_global_drs_write_claim(tmp_path):
    drs = LocalDRS(tmp_path)

    with pytest.raises(ValueError):
        write_root_final_record(
            drs,
            {
                "artifact_type": "RootFinal",
                "final_artifact_id": "root_final:unsafe_external_global:001",
                "created_by": "root_orchestrator",
                "root_reviewed": True,
                "root_final_status": "accepted",
                "domain": "mock_government_certificate",
                "external_global_drs_write": True,
            },
        )


def test_runner_structured_result_has_required_counters():
    result = run_all_scenarios()
    counters = result["counters"]

    assert result["final_status"] == "PASS"
    assert result["scenarios_total"] == 8
    assert result["scenarios_passed"] == 8
    assert counters["direct_reuse_allowed_count"] == 0
    assert counters["poisoning_pressure_authority_claimed_count"] == 0
    assert counters["action_permission_granted_count"] == 0
    assert counters["production_drs_used_count"] == 0
    assert counters["external_drs_used_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["root_final_authority_preserved_count"] == 8


def test_main_returns_zero(capsys):
    assert main() == 0
    output = capsys.readouterr().out
    assert "FINAL STATUS: PASS" in output
    assert "scenarios_total: 8" in output
    assert "scenarios_passed: 8" in output
    assert "root_final_authority_preserved_count: 8" in output
    assert "production_drs_used_count: 0" in output
    assert "external_drs_used_count: 0" in output
    assert "network_used_count: 0" in output
    assert "gemini_used_count: 0" in output


def test_command_execution_exits_zero_and_has_required_output():
    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_real_local_drs_resolver_writeback_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    output = completed.stdout
    assert "FINAL STATUS: PASS" in output
    assert "scenarios_total: 8" in output
    assert "scenarios_passed: 8" in output
    assert "root_final_authority_preserved_count: 8" in output
    assert "production_drs_used_count: 0" in output
    assert "external_drs_used_count: 0" in output
    assert "network_used_count: 0" in output
    assert "gemini_used_count: 0" in output
    forbidden = (
        "production ready",
        "public auditor ready",
        "runtime complete",
        "public launch ready",
        "whitepaper ready",
    )
    assert not any(term in output for term in forbidden)
