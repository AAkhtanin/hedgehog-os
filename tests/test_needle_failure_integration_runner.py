from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from demo.run_needle_failure_integration import collect_needle_failure_integration
from demo.run_needle_failure_integration import run_needle_failure_integration
from hedgehog.needle_runtime import NeedleCall
from hedgehog.needle_runtime import execute_needle_call
from hedgehog.needle_runtime import needle_result_to_result_proposal
from hedgehog.post_vv import validate_result_proposal


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_proposal_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    time_envelope_schema = load_json(SCHEMAS_DIR / "time_envelope.schema.json")
    result_proposal_schema = load_json(SCHEMAS_DIR / "result_proposal.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        result_proposal_schema["$id"]: result_proposal_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(result_proposal_schema, store=store)
    return jsonschema.Draft202012Validator(
        result_proposal_schema,
        resolver=resolver,
    )


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def violation_ids(report):
    return {violation["violation_id"] for violation in report["violations"]}


def violation_text(report):
    return " ".join(violation["description"] for violation in report["violations"])


def _call(scenario: str, *, permission_confirmed: bool = True) -> NeedleCall:
    return NeedleCall(
        needle_id="test_needle",
        capability="mock_capability",
        contract_version="1.0",
        required_contract_version="1.0",
        payload={"slot": "value"},
        permission_confirmed=permission_confirmed,
        timeout_ms=100,
        scenario=scenario,
    )


def _proposal_for(scenario: str):
    result = execute_needle_call(_call(scenario))
    return needle_result_to_result_proposal(result, request_id=f"test_{scenario}")


def test_adapter_emits_schema_valid_result_proposal_evidence_shape():
    proposal = _proposal_for("needle_success_mock")
    evidence = proposal["evidence"][0]

    result_proposal_validator().validate(proposal)
    assert evidence == {
        "kind": "audit",
        "summary": (
            "NeedleRuntime returned a structured mock result with no external action."
        ),
        "ref_id": "needle_runtime_mock_execution",
    }
    assert "evidence_id" not in evidence
    assert "description" not in evidence
    assert "ref" not in evidence
    assert proposal["trace_refs"][0]["kind"] == "needle_runtime"


def test_post_vv_no_longer_rejects_needleruntime_proposal_for_evidence_shape():
    proposal = _proposal_for("needle_success_mock")

    vv_report = validate_result_proposal(proposal)

    assert vv_report["scores"]["schema"] == 1.0
    assert "vv_runtime_schema_validation_failed" not in violation_ids(vv_report)
    assert vv_report["decision"] == "accept"
    assert vv_report["status"] == "accepted"
    assert vv_report["execution_status"] == "completed"


def test_old_needleruntime_evidence_fields_rejected_if_reintroduced():
    proposal = _proposal_for("needle_success_mock")
    proposal["evidence"][0] = {
        "evidence_id": "evidence:test_needle:none",
        "kind": "audit",
        "description": (
            "NeedleRuntime returned a structured mock result with no external action."
        ),
        "ref": "needle_runtime_mock_execution",
    }

    vv_report = validate_result_proposal(proposal)

    assert vv_report["decision"] == "reject"
    assert vv_report["status"] == "rejected"
    assert "vv_runtime_schema_validation_failed" in violation_ids(vv_report)
    text = violation_text(vv_report)
    assert "summary" in text
    assert "evidence_id" in text
    assert "description" in text
    assert "ref" in text


def test_needle_runtime_remains_trace_kind_not_evidence_kind():
    proposal = _proposal_for("needle_success_mock")
    assert proposal["trace_refs"][0]["kind"] == "needle_runtime"
    proposal["evidence"][0] = {
        "kind": "needle_runtime",
        "summary": "NeedleRuntime trace metadata must not become evidence kind.",
        "ref_id": "needle_runtime_mock_execution",
    }

    vv_report = validate_result_proposal(proposal)

    assert vv_report["decision"] == "reject"
    assert vv_report["status"] == "rejected"
    assert "vv_runtime_schema_validation_failed" in violation_ids(vv_report)
    assert "needle_runtime" in violation_text(vv_report)


def test_audit_evidence_does_not_create_authority_or_root_effects():
    proposal = _proposal_for("needle_success_mock")
    vv_report = validate_result_proposal(proposal)

    assert proposal["evidence"][0]["kind"] == "audit"
    assert not contains_key(proposal, "truth")
    assert not contains_key(vv_report, "truth")
    assert not contains_key(proposal, "authority")
    assert not contains_key(vv_report, "authority")
    assert not contains_key(proposal, "AcceptedEvidence")
    assert not contains_key(vv_report, "AcceptedEvidence")
    assert not contains_key(proposal, "accepted_evidence")
    assert not contains_key(vv_report, "accepted_evidence")
    assert not contains_key(proposal, "action_authorized")
    assert not contains_key(vv_report, "action_authorized")
    assert not contains_key(proposal, "action_executed")
    assert not contains_key(vv_report, "action_executed")
    assert not contains_key(proposal, "drs_write")
    assert not contains_key(vv_report, "drs_write")
    assert not contains_key(proposal, "drs_writes")
    assert not contains_key(vv_report, "drs_writes")
    assert not contains_key(proposal, "final_output")
    assert not contains_key(vv_report, "final_output")


def test_adapter_maps_completed_needle_to_completed_proposal():
    proposal = _proposal_for("needle_success_mock")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["source"] == "needle_runtime"
    assert payload["status"] == "completed"
    assert payload["failure_kind"] == "none"
    assert payload["safe_for_gt"] is True
    assert vv_report["execution_status"] == "completed"


def test_adapter_maps_blocked_needle_to_blocked_proposal():
    result = execute_needle_call(_call("needle_success_mock", permission_confirmed=False))
    proposal = needle_result_to_result_proposal(result, request_id="test_blocked")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["status"] == "blocked"
    assert payload["failure_kind"] == "permission_required"
    assert payload["permission_required"] is True
    assert payload["safe_for_gt"] is True
    assert vv_report["execution_status"] == "blocked"


def test_adapter_maps_degraded_timeout_to_degraded_proposal():
    proposal = _proposal_for("needle_timeout")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["status"] == "degraded"
    assert payload["failure_kind"] == "timeout"
    assert payload["safe_for_gt"] is True
    assert vv_report["execution_status"] == "degraded"


def test_adapter_maps_invalid_json_and_schema_failure_to_quarantine_caution():
    for scenario, failure_kind in [
        ("needle_invalid_json", "invalid_json"),
        ("needle_schema_validation_failed", "schema_validation_failed"),
    ]:
        proposal = _proposal_for(scenario)
        payload = proposal["result_payload"]
        vv_report = validate_result_proposal(proposal)

        assert payload["status"] == "failed"
        assert payload["failure_kind"] == failure_kind
        assert payload["quarantine_required"] is True
        assert payload["safe_for_gt"] is False
        assert vv_report["execution_status"] == "failed"


def test_adapter_maps_unknown_exception_without_throwing():
    proposal = _proposal_for("needle_unknown_exception")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["status"] == "failed"
    assert payload["failure_kind"] == "unknown_exception"
    assert payload["safe_for_gt"] is False
    assert payload["root_crash_risk_contained"] is True
    assert vv_report["execution_status"] == "failed"


def test_demo_collects_all_needle_failure_integration_scenarios():
    rows = collect_needle_failure_integration()
    scenarios = {row.scenario for row in rows}

    assert scenarios == {
        "needle_success_mock",
        "needle_timeout",
        "needle_invalid_json",
        "needle_contract_version_mismatch",
        "needle_permission_required",
        "needle_circuit_breaker_open",
        "needle_schema_validation_failed",
        "needle_unknown_exception",
    }
    for row in rows:
        assert row.proposal["result_payload"]["source"] == "needle_runtime"
        assert row.proposal["result_payload"]["no_real_external_action"] is True
        assert row.proposal["result_payload"]["root_crash_risk_contained"] is True


def test_demo_output_has_summary_and_no_sensitive_terms():
    output = run_needle_failure_integration()
    lowered = output.lower()

    assert "[NEEDLE FAILURE INTEGRATION]" in output
    assert "demo-level integration adapter, not full Root integration yet" in output
    assert "scenarios: 8" in output
    assert "completed_proposals:" in output
    assert "blocked_proposals:" in output
    assert "degraded_proposals:" in output
    assert "failed_or_quarantined_proposals:" in output
    assert "safe_for_gt_count:" in output
    assert "unsafe_or_caution_for_gt_count:" in output
    assert "unhandled_exceptions: 0" in output
    assert "no_real_external_actions: true" in output
    assert "root_crash_risk_contained: true" in output
    for scenario in [
        "needle_success_mock",
        "needle_timeout",
        "needle_invalid_json",
        "needle_contract_version_mismatch",
        "needle_permission_required",
        "needle_circuit_breaker_open",
        "needle_schema_validation_failed",
        "needle_unknown_exception",
    ]:
        assert scenario in output
    for term in FORBIDDEN_TERMS:
        assert term not in lowered
