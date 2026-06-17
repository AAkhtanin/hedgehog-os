import json
from copy import deepcopy
from pathlib import Path

import jsonschema

from hedgehog import post_vv
from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.executor import execute_plan_graph
from hedgehog.post_vv import validate_result_proposal, validate_result_proposals
from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def vv_report_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    vv_report_schema = load_json(SCHEMAS_DIR / "vv_report.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        vv_report_schema["$id"]: vv_report_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(vv_report_schema, store=store)
    return jsonschema.Draft202012Validator(vv_report_schema, resolver=resolver)


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


def build_demo_proposals():
    vectors = load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )
    packet = build_attractor_packet(
        request_id="req_post_vv_001",
        intent_id="intent_post_vv_001",
        world_state_ref="world_state_post_vv_001",
        goal_id="goal_certificate_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=vectors,
        as_of=utc_now_iso(),
        max_selected=4,
    )
    plan_graph = make_plan_graph(packet)
    return execute_plan_graph(plan_graph, session_anchor="sess_post_vv_001")


def proposal_with_evidence_kind(kind: str):
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["evidence"][0]["kind"] = kind
    return proposal


def reports_by_artifact(proposals, reports):
    return {
        proposal["result_payload"]["artifact_type"]: report
        for proposal, report in zip(proposals, reports)
    }


def test_validate_demo_result_proposals_are_task_aware_and_schema_valid():
    proposals = build_demo_proposals()
    reports = validate_result_proposals(proposals)
    validator = vv_report_validator()

    assert len(reports) == len(proposals)
    for report in reports:
        assert "normalized_features" in report
        assert report["vector_id"]
        assert report["artifact_type"]
        assert report["execution_status"]
        assert "avf_final_viability" in report["normalized_features"]
        assert "avf_soft_mask" in report["normalized_features"]
        validator.validate(report)

    by_artifact = reports_by_artifact(proposals, reports)
    assert by_artifact["request_payload"]["decision"] == "accept"
    assert by_artifact["request_payload"]["status"] == "accepted"
    assert by_artifact["field_validation"]["decision"] == "revise"
    assert by_artifact["field_validation"]["status"] == "needs_revision"
    assert by_artifact["submission_simulation"]["decision"] == "revise"
    assert by_artifact["submission_simulation"]["status"] == "needs_revision"


def test_fractal_dag_executor_evidence_kind_validates_result_proposal_schema():
    proposal = proposal_with_evidence_kind("fractal_dag_executor")

    result_proposal_validator().validate(proposal)


def test_audit_evidence_kind_validates_result_proposal_schema():
    proposal = proposal_with_evidence_kind("audit")

    result_proposal_validator().validate(proposal)


def test_fractal_dag_executor_evidence_kind_does_not_create_authority_or_accepted_evidence():
    proposal = proposal_with_evidence_kind("fractal_dag_executor")
    report = validate_result_proposal(proposal)

    vv_report_validator().validate(report)
    assert report["proposal_id"] == proposal["proposal_id"]
    assert not contains_key(proposal, "final_output")
    assert not contains_key(report, "final_output")
    assert not contains_key(proposal, "authority")
    assert not contains_key(report, "authority")
    assert not contains_key(proposal, "AcceptedEvidence")
    assert not contains_key(report, "AcceptedEvidence")
    assert not contains_key(proposal, "accepted_evidence")
    assert not contains_key(report, "accepted_evidence")
    assert not contains_key(proposal, "action_authorized")
    assert not contains_key(report, "action_authorized")
    assert not contains_key(proposal, "action_executed")
    assert not contains_key(report, "action_executed")
    assert not contains_key(proposal, "drs_write")
    assert not contains_key(report, "drs_write")
    assert not contains_key(proposal, "drs_writes")
    assert not contains_key(report, "drs_writes")


def test_audit_evidence_kind_does_not_create_authority_or_accepted_evidence():
    proposal = proposal_with_evidence_kind("audit")
    report = validate_result_proposal(proposal)

    vv_report_validator().validate(report)
    assert report["proposal_id"] == proposal["proposal_id"]
    assert not contains_key(proposal, "truth")
    assert not contains_key(report, "truth")
    assert not contains_key(proposal, "final_output")
    assert not contains_key(report, "final_output")
    assert not contains_key(proposal, "authority")
    assert not contains_key(report, "authority")
    assert not contains_key(proposal, "AcceptedEvidence")
    assert not contains_key(report, "AcceptedEvidence")
    assert not contains_key(proposal, "accepted_evidence")
    assert not contains_key(report, "accepted_evidence")
    assert not contains_key(proposal, "action_authorized")
    assert not contains_key(report, "action_authorized")
    assert not contains_key(proposal, "action_executed")
    assert not contains_key(report, "action_executed")
    assert not contains_key(proposal, "drs_write")
    assert not contains_key(report, "drs_write")
    assert not contains_key(proposal, "drs_writes")
    assert not contains_key(report, "drs_writes")


def test_simulated_executor_evidence_kind_still_validates_result_proposal_schema():
    proposal = proposal_with_evidence_kind("simulated_executor")

    result_proposal_validator().validate(proposal)


def test_unknown_evidence_kind_is_still_rejected_by_runtime_schema_validation():
    proposal = proposal_with_evidence_kind("unknown_evidence_kind")

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["status"] == "rejected"
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    assert "unknown_evidence_kind" in violation_text(report)
    vv_report_validator().validate(report)


def test_malformed_evidence_item_shape_is_still_rejected_by_runtime_schema_validation():
    proposal = proposal_with_evidence_kind("fractal_dag_executor")
    proposal["evidence"][0] = {
        "kind": "fractal_dag_executor",
        "description": "Malformed EvidenceItem shape keeps old description field.",
    }

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["status"] == "rejected"
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    assert "summary" in violation_text(report)
    assert "description" in violation_text(report)
    vv_report_validator().validate(report)


def test_missing_required_result_proposal_field_rejected_by_runtime_schema_validation():
    proposal = deepcopy(build_demo_proposals()[0])
    del proposal["producer"]

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["status"] == "rejected"
    assert report["scores"]["schema"] == 0.0
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    assert "producer" in violation_text(report)
    vv_report_validator().validate(report)


def test_bad_nested_time_envelope_rejected_by_runtime_schema_validation():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["time_envelope"]["ttl_seconds"] = -1

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["schema"] == 0.0
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    assert "time_envelope.ttl_seconds" in violation_text(report)
    vv_report_validator().validate(report)


def test_malformed_risk_severity_rejected_by_runtime_schema_validation():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["risks"] = [
        {
            "risk_id": "risk:bad_schema_shape",
            "severity": "severe",
            "description": "Severity is outside the ResultProposal enum.",
        }
    ]

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["schema"] == 0.0
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    assert "risks.0.severity" in violation_text(report)
    vv_report_validator().validate(report)


def test_extra_top_level_field_rejected_by_runtime_schema_validation():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["unexpected_runtime_field"] = True

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["schema"] == 0.0
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    assert "Additional properties are not allowed" in violation_text(report)
    assert "unexpected_runtime_field" in violation_text(report)
    vv_report_validator().validate(report)


def test_completed_prepare_request_payload_remains_accepted():
    proposals = build_demo_proposals()
    reports = validate_result_proposals(proposals)
    report = reports_by_artifact(proposals, reports)["request_payload"]

    assert report["decision"] == "accept"
    assert report["status"] == "accepted"
    assert report["violations"] == []
    vv_report_validator().validate(report)


def test_required_field_validation_requires_user_revision():
    proposals = build_demo_proposals()
    reports = validate_result_proposals(proposals)
    report = reports_by_artifact(proposals, reports)["field_validation"]

    assert report["decision"] == "revise"
    assert report["status"] == "needs_revision"
    assert any(
        violation["violation_id"] == "vv_human_input_required"
        for violation in report["violations"]
    )
    vv_report_validator().validate(report)


def test_submission_simulation_blocked_before_completion_revises():
    proposals = build_demo_proposals()
    reports = validate_result_proposals(proposals)
    report = reports_by_artifact(proposals, reports)["submission_simulation"]

    assert report["decision"] == "revise"
    assert report["status"] == "needs_revision"
    assert any(
        violation["violation_id"] == "vv_blocked_before_completion"
        for violation in report["violations"]
    )
    vv_report_validator().validate(report)


def test_schema_valid_critical_risk_still_rejected_by_manual_safety_check():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["risks"] = [
        {
            "risk_id": "risk:critical_manual_check",
            "severity": "critical",
            "description": "Critical risk should be rejected after schema validation passes.",
        }
    ]

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["schema"] == 1.0
    assert report["scores"]["safety"] == 0.0
    assert "vv_safety_critical_risk" in violation_ids(report)
    vv_report_validator().validate(report)


def test_forbidden_final_output_key_rejects_policy():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["result_payload"]["final_output"] = "not allowed"

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["policy"] == 0.0
    assert report["normalized_features"]["utility"] == report["overall_score"]
    assert "vv_policy_forbidden_key" in violation_ids(report)
    vv_report_validator().validate(report)


def test_forbidden_answer_key_still_rejected_by_manual_policy_check():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["result_payload"]["answer"] = "not allowed"

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["policy"] == 0.0
    assert "vv_policy_forbidden_key" in violation_ids(report)
    vv_report_validator().validate(report)


def test_missing_time_envelope_revises_or_rejects_time():
    proposal = deepcopy(build_demo_proposals()[0])
    del proposal["time_envelope"]

    report = validate_result_proposal(proposal)

    assert report["decision"] != "accept"
    assert report["scores"]["time"] == 0.0


def test_malformed_proposal_does_not_crash_post_vv():
    report = validate_result_proposal(
        {
            "proposal_id": "rp:malformed",
            "trace_refs": "not-a-list",
        }
    )

    assert report["decision"] == "reject"
    assert report["status"] == "rejected"
    assert report["proposal_id"] == "rp:malformed"
    assert report["trace_refs"] == []
    assert report["scores"]["schema"] == 0.0
    assert "vv_runtime_schema_validation_failed" in violation_ids(report)
    vv_report_validator().validate(report)


def test_vv_report_has_no_root_or_user_facing_output_keys():
    report = validate_result_proposal(build_demo_proposals()[0])

    assert not contains_key(report, "final_output")
    assert not contains_key(report, "answer")
    assert not contains_key(report, "raw_user_text")


def test_internal_outgoing_vv_report_shape_error_returns_safe_schema_valid_report(monkeypatch):
    proposal = deepcopy(build_demo_proposals()[0])

    def fake_outgoing_schema_violations(report):
        return [
            post_vv._violation(
                "vv_outgoing_runtime_schema_validation_failed",
                "schema",
                "Outgoing VVReport runtime schema validation failed at $: test injected shape error.",
            )
        ]

    monkeypatch.setattr(
        post_vv,
        "_vv_report_schema_violations",
        fake_outgoing_schema_violations,
    )

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["status"] == "rejected"
    assert report["overall_score"] == 0.0
    assert report["scores"] == {
        "schema": 0.0,
        "evidence": 0.0,
        "policy": 0.0,
        "time": 0.0,
        "safety": 0.0,
        "consistency": 0.0,
    }
    assert "vv_outgoing_runtime_schema_validation_failed" in violation_ids(report)
    vv_report_validator().validate(report)


def test_outgoing_validation_fallback_does_not_create_authority_or_action(monkeypatch):
    proposal = deepcopy(build_demo_proposals()[0])

    monkeypatch.setattr(
        post_vv,
        "_vv_report_schema_violations",
        lambda report: [
            post_vv._violation(
                "vv_outgoing_runtime_schema_validation_failed",
                "schema",
                "Outgoing VVReport runtime schema validation failed at $: test injected shape error.",
            )
        ],
    )

    report = validate_result_proposal(proposal)

    assert "final_output" not in report
    assert "drs_write" not in report
    assert "action_executed" not in report
    assert "gt_report" not in report
    assert "root_final" not in report
    assert not contains_key(report, "final_output")
    vv_report_validator().validate(report)
