import json
from copy import deepcopy
from pathlib import Path

import jsonschema

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.executor import execute_plan_graph
from hedgehog.gt_validator import (
    PAYOFF_FORMULA_VERSION,
    classify_vv_report,
    compute_payoff_components,
    validate_gt,
)
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
    assert gt_report["payoff_formula_version"] == PAYOFF_FORMULA_VERSION
    assert gt_report["candidate_scores"]
    assert "winner_payoff" in gt_report
    assert "regret_summary" in gt_report
    assert "dominated_candidate_ids" in gt_report
    assert "selection_reason" in gt_report
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

    for score in gt_report["candidate_scores"]:
        assert {
            "proposal_id",
            "status",
            "accepted",
            "utility",
            "risk_penalty",
            "cost_penalty",
            "robustness",
            "status_bonus",
            "novelty_or_reuse_bonus",
            "payoff",
            "regret",
            "selection_notes",
        }.issubset(score)

    gt_report_validator().validate(gt_report)


def test_classify_vv_report_returns_expected_classes():
    assert (
        classify_vv_report({"decision": "accept", "status": "accepted"})
        == "accepted_completed"
    )
    assert (
        classify_vv_report({"decision": "revise", "status": "needs_revision"})
        == "needs_revision"
    )
    assert (
        classify_vv_report({"decision": "reject", "status": "rejected"})
        == "rejected"
    )
    assert classify_vv_report({"decision": "accept", "status": "needs_revision"}) == "needs_revision"
    assert classify_vv_report({"decision": "unknown", "status": "unknown"}) == "unknown"


def test_validate_gt_prefers_official_online_request_over_fallback():
    proposals, vv_reports = build_demo_proposals_and_vv_reports()
    gt_report = validate_gt(vv_reports)

    proposal_by_id = {proposal["proposal_id"]: proposal for proposal in proposals}
    utility_by_vector = {}
    for proposal, report in zip(proposals, vv_reports):
        if report["decision"] != "accept":
            continue
        vector_id = proposal["vector_id"]
        utility_by_vector[vector_id] = max(
            utility_by_vector.get(vector_id, 0.0),
            report["normalized_features"]["utility"],
        )
    payoff_by_vector = {}
    for candidate in gt_report["candidates"]:
        vector_id = proposal_by_id[candidate["candidate_id"]]["vector_id"]
        payoff_by_vector[vector_id] = max(
            payoff_by_vector.get(vector_id, 0.0),
            candidate["payoff"],
        )

    assert utility_by_vector["official_online_request"] > utility_by_vector["fallback_exploration"]
    assert payoff_by_vector["official_online_request"] > payoff_by_vector["fallback_exploration"]
    assert proposal_by_id[gt_report["winner"]]["vector_id"] == "official_online_request"
    assert not contains_key(gt_report, "final_output")
    assert not contains_key(gt_report, "answer")
    assert not contains_key(gt_report, "raw_user_text")


def test_validate_gt_completed_candidate_wins_over_high_utility_needs_revision():
    accepted = deepcopy(build_demo_vv_reports()[0])
    accepted["proposal_id"] = "proposal:accepted_completed"
    accepted["decision"] = "accept"
    accepted["status"] = "accepted"
    accepted["normalized_features"] = {
        "utility": 0.4,
        "robustness": 0.4,
        "compute_cost": 0.0,
        "violations": 0.0,
        "transfer": 0.0,
        "novelty_guard": 0.0,
    }
    needs_revision = deepcopy(accepted)
    needs_revision["proposal_id"] = "proposal:needs_revision_high_utility"
    needs_revision["decision"] = "revise"
    needs_revision["status"] = "needs_revision"
    needs_revision["normalized_features"] = {
        "utility": 1.0,
        "robustness": 1.0,
        "compute_cost": 0.0,
        "violations": 0.0,
        "transfer": 0.0,
        "novelty_guard": 0.0,
    }

    gt_report = validate_gt([needs_revision, accepted])
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }

    assert gt_report["decision"] == "accept"
    assert gt_report["winner"] == "proposal:accepted_completed"
    assert [
        candidate["candidate_id"] for candidate in gt_report["candidates"]
    ] == ["proposal:accepted_completed"]
    assert score_by_id["proposal:accepted_completed"]["accepted"] is True
    assert score_by_id["proposal:accepted_completed"]["status_bonus"] > 0
    assert score_by_id["proposal:needs_revision_high_utility"]["accepted"] is False
    assert score_by_id["proposal:needs_revision_high_utility"]["risk_penalty"] > 0
    gt_report_validator().validate(gt_report)


def test_compute_payoff_components_penalizes_blocked_needs_revision():
    accepted = deepcopy(build_demo_vv_reports()[0])
    accepted["proposal_id"] = "proposal:accepted_component"
    accepted["decision"] = "accept"
    accepted["status"] = "accepted"
    accepted["normalized_features"] = {
        "utility": 0.7,
        "robustness": 0.7,
        "compute_cost": 0.0,
        "violations": 0.0,
        "transfer": 0.0,
        "novelty_guard": 0.0,
    }
    blocked = deepcopy(accepted)
    blocked["proposal_id"] = "proposal:blocked_component"
    blocked["decision"] = "revise"
    blocked["status"] = "needs_revision"
    blocked["normalized_features"]["utility"] = 1.0
    blocked["normalized_features"]["robustness"] = 1.0
    blocked["violations"] = [
        {
            "kind": "blocked",
            "description": "ResultProposal is blocked before completion.",
        }
    ]

    accepted_score = compute_payoff_components(accepted)
    blocked_score = compute_payoff_components(blocked)

    assert accepted_score["status_bonus"] > 0
    assert blocked_score["risk_penalty"] > accepted_score["risk_penalty"]
    assert "blocked_before_completion" in blocked_score["selection_notes"]
    assert blocked_score["accepted"] is False


def test_validate_gt_blocked_candidate_cannot_win():
    accepted = deepcopy(build_demo_vv_reports()[0])
    accepted["proposal_id"] = "proposal:accepted_low"
    accepted["decision"] = "accept"
    accepted["status"] = "accepted"
    accepted["normalized_features"] = {
        "utility": 0.25,
        "robustness": 0.25,
        "compute_cost": 0.0,
        "violations": 0.0,
        "transfer": 0.0,
        "novelty_guard": 0.0,
    }
    blocked = deepcopy(accepted)
    blocked["proposal_id"] = "proposal:blocked_high"
    blocked["decision"] = "revise"
    blocked["status"] = "needs_revision"
    blocked["normalized_features"] = {
        "utility": 1.0,
        "robustness": 1.0,
        "compute_cost": 0.0,
        "violations": 0.0,
        "transfer": 0.0,
        "novelty_guard": 0.0,
    }
    blocked["violations"] = [
        {
            "kind": "blocked",
            "description": "ResultProposal is blocked before completion.",
        }
    ]

    gt_report = validate_gt([blocked, accepted])

    assert gt_report["decision"] == "accept"
    assert gt_report["winner"] == "proposal:accepted_low"
    assert all(
        candidate["candidate_id"] != "proposal:blocked_high"
        for candidate in gt_report["candidates"]
    )
    gt_report_validator().validate(gt_report)


def test_validate_gt_regret_summary_exists_for_multiple_scored_candidates():
    reports = build_demo_vv_reports()
    gt_report = validate_gt(reports)

    assert gt_report["regret_summary"]["candidate_count"] == len(
        gt_report["candidate_scores"]
    )
    assert gt_report["regret_summary"]["max_regret"] >= 0
    assert gt_report["regret_summary"]["mean_regret"] >= 0
    gt_report_validator().validate(gt_report)


def test_validate_gt_returns_revise_when_only_needs_revision_candidates_exist():
    reports = []
    for report in build_demo_vv_reports():
        revised = deepcopy(report)
        revised["decision"] = "revise"
        revised["status"] = "needs_revision"
        revised["normalized_features"]["utility"] = 1.0
        reports.append(revised)

    gt_report = validate_gt(reports)

    assert gt_report["decision"] == "revise"
    assert "winner" not in gt_report
    assert gt_report["candidates"] == []
    assert gt_report["candidate_scores"]
    assert gt_report["payoff_formula_version"] == PAYOFF_FORMULA_VERSION
    assert any("needs_revision" in note for note in gt_report["notes"])
    assert not contains_key(gt_report, "final_output")
    assert not contains_key(gt_report, "answer")
    assert not contains_key(gt_report, "raw_user_text")
    gt_report_validator().validate(gt_report)


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
    assert gt_report["candidate_scores"] == []
    assert gt_report["payoff_formula_version"] == PAYOFF_FORMULA_VERSION
    gt_report_validator().validate(gt_report)
