import json
from copy import deepcopy
from pathlib import Path

import jsonschema

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


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


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


def test_completed_prepare_request_payload_remains_accepted():
    proposals = build_demo_proposals()
    reports = validate_result_proposals(proposals)
    report = reports_by_artifact(proposals, reports)["request_payload"]

    assert report["decision"] == "accept"
    assert report["status"] == "accepted"
    assert report["violations"] == []


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


def test_forbidden_final_output_key_rejects_policy():
    proposal = deepcopy(build_demo_proposals()[0])
    proposal["result_payload"]["final_output"] = "not allowed"

    report = validate_result_proposal(proposal)

    assert report["decision"] == "reject"
    assert report["scores"]["policy"] == 0.0
    assert report["normalized_features"]["utility"] == report["overall_score"]


def test_missing_time_envelope_revises_or_rejects_time():
    proposal = deepcopy(build_demo_proposals()[0])
    del proposal["time_envelope"]

    report = validate_result_proposal(proposal)

    assert report["decision"] != "accept"
    assert report["scores"]["time"] == 0.0


def test_vv_report_has_no_root_or_user_facing_output_keys():
    report = validate_result_proposal(build_demo_proposals()[0])

    assert not contains_key(report, "final_output")
    assert not contains_key(report, "answer")
    assert not contains_key(report, "raw_user_text")
