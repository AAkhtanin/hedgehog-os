import json
from copy import deepcopy
from pathlib import Path

import jsonschema

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.executor import execute_plan_graph
from hedgehog.gt_validator import validate_gt
from hedgehog.post_vv import validate_result_proposals
from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def gt_report_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    gt_report_schema = load_json(SCHEMAS_DIR / "gt_report.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        gt_report_schema["$id"]: gt_report_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(gt_report_schema, store=store)
    return jsonschema.Draft202012Validator(gt_report_schema, resolver=resolver)


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def build_demo_vv_reports():
    vectors = load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )
    packet = build_attractor_packet(
        request_id="req_gt_001",
        intent_id="intent_gt_001",
        world_state_ref="world_state_gt_001",
        goal_id="goal_certificate_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=vectors,
        as_of=utc_now_iso(),
        max_selected=4,
    )
    plan_graph = make_plan_graph(packet)
    proposals = execute_plan_graph(plan_graph, session_anchor="sess_gt_001")
    return validate_result_proposals(proposals)


def build_demo_proposals_and_vv_reports():
    vectors = load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )
    packet = build_attractor_packet(
        request_id="req_gt_rank_001",
        intent_id="intent_gt_rank_001",
        world_state_ref="world_state_gt_rank_001",
        goal_id="goal_certificate_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=vectors,
        as_of=utc_now_iso(),
        max_selected=4,
    )
    assert "fallback_exploration" in {
        vector["vector_id"] for vector in packet["candidate_vectors"]
    }
    assert "illegal_coercion" not in {
        vector["vector_id"] for vector in packet["candidate_vectors"]
    }
    plan_graph = make_plan_graph(packet)
    proposals = execute_plan_graph(plan_graph, session_anchor="sess_gt_rank_001")
    return proposals, validate_result_proposals(proposals)


def test_validate_gt_accepts_and_validates_schema():
    vv_reports = build_demo_vv_reports()
    gt_report = validate_gt(vv_reports)

    accepted_ids = {
        report["proposal_id"]
        for report in vv_reports
        if report["decision"] == "accept" or report["status"] == "accepted"
    }

    assert gt_report["decision"] == "accept"
    assert gt_report["winner"] in accepted_ids
    assert gt_report["candidates"]
    assert "half_life_hours" in gt_report
    assert "decay_rate" in gt_report
    assert not contains_key(gt_report, "final_output")
    assert not contains_key(gt_report, "answer")
    assert not contains_key(gt_report, "raw_user_text")

    for candidate in gt_report["candidates"]:
        assert candidate["candidate_id"] in accepted_ids
        assert candidate["candidate_type"] == "result_proposal"
        assert "payoff" in candidate
        assert "regret" in candidate
        assert "elo_before" in candidate
        assert "elo_after" in candidate

    gt_report_validator().validate(gt_report)


def test_validate_gt_prefers_official_online_request_over_fallback():
    proposals, vv_reports = build_demo_proposals_and_vv_reports()
    gt_report = validate_gt(vv_reports)

    proposal_by_id = {proposal["proposal_id"]: proposal for proposal in proposals}
    utility_by_vector = {
        proposal["vector_id"]: report["normalized_features"]["utility"]
        for proposal, report in zip(proposals, vv_reports)
    }
    payoff_by_vector = {
        proposal_by_id[candidate["candidate_id"]]["vector_id"]: candidate["payoff"]
        for candidate in gt_report["candidates"]
    }

    assert utility_by_vector["official_online_request"] > utility_by_vector["fallback_exploration"]
    assert payoff_by_vector["official_online_request"] > payoff_by_vector["fallback_exploration"]
    assert proposal_by_id[gt_report["winner"]]["vector_id"] == "official_online_request"
    assert not contains_key(gt_report, "final_output")
    assert not contains_key(gt_report, "answer")
    assert not contains_key(gt_report, "raw_user_text")


def test_validate_gt_returns_no_update_when_no_candidates_are_accepted():
    rejected_reports = []
    for report in build_demo_vv_reports():
        rejected = deepcopy(report)
        rejected["decision"] = "reject"
        rejected["status"] = "rejected"
        rejected_reports.append(rejected)

    gt_report = validate_gt(rejected_reports)

    assert gt_report["decision"] == "no_update"
    assert gt_report["candidates"] == []
    gt_report_validator().validate(gt_report)
