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
    TIE_BREAK_RULE,
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


def accepted_report(
    proposal_id: str,
    *,
    utility: float,
    robustness: float,
    compute_cost: float = 0.0,
    violations: float = 0.0,
    vector_id: str | None = None,
    avf_final_viability: float | None = None,
    avf_soft_mask: float | None = None,
    dependency_depth: int = 0,
    risk_level: str = "none",
) -> dict:
    report = {
        "proposal_id": proposal_id,
        "decision": "accept",
        "status": "accepted",
        "normalized_features": {
            "utility": utility,
            "robustness": robustness,
            "compute_cost": compute_cost,
            "violations": violations,
            "transfer": 0.0,
            "novelty_guard": 0.0,
        },
        "violations": [],
        "dependency_depth": dependency_depth,
        "risk_level": risk_level,
    }
    if vector_id is not None:
        report["vector_id"] = vector_id
    if avf_final_viability is not None:
        report["avf_final_viability"] = avf_final_viability
    if avf_soft_mask is not None:
        report["avf_soft_mask"] = avf_soft_mask
    return report


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
    assert "tie_detected" in gt_report
    assert "tie_candidate_ids" in gt_report
    assert "tie_break_rule" in gt_report
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
            "base_payoff_v0_1",
            "vector_role_bonus",
            "fallback_role_penalty",
            "human_burden_penalty",
            "dependency_depth_penalty",
            "evidence_strength_bonus",
            "payoff",
            "regret",
            "selection_notes",
        }.issubset(score)

    gt_report_validator().validate(gt_report)


def test_validate_gt_v02_official_path_beats_fallback_when_base_payoff_equal():
    official = accepted_report(
        "proposal:official",
        utility=0.5,
        robustness=0.5,
        vector_id="official_online_request",
        avf_final_viability=0.8,
    )
    fallback = accepted_report(
        "proposal:fallback",
        utility=0.5,
        robustness=0.5,
        vector_id="fallback_exploration",
        avf_final_viability=0.8,
    )

    gt_report = validate_gt([fallback, official])
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }

    assert gt_report["payoff_formula_version"] == "gt_payoff_v0_2"
    assert gt_report["winner"] == "proposal:official"
    assert score_by_id["proposal:official"]["vector_role_bonus"] > 0
    assert score_by_id["proposal:fallback"]["fallback_role_penalty"] > 0
    gt_report_validator().validate(gt_report)


def test_validate_gt_v02_higher_avf_final_viability_wins_when_otherwise_equal():
    high_avf = accepted_report(
        "proposal:high_avf",
        utility=0.5,
        robustness=0.5,
        vector_id="personal_visit",
        avf_final_viability=0.9,
    )
    low_avf = accepted_report(
        "proposal:low_avf",
        utility=0.5,
        robustness=0.5,
        vector_id="personal_visit",
        avf_final_viability=0.2,
    )

    gt_report = validate_gt([low_avf, high_avf])

    assert gt_report["winner"] == "proposal:high_avf"
    assert gt_report["tie_detected"] is False
    gt_report_validator().validate(gt_report)


def test_validate_gt_v02_needs_user_high_burden_loses_to_completed_candidate():
    completed = accepted_report(
        "proposal:completed",
        utility=0.5,
        robustness=0.5,
        vector_id="official_online_request",
    )
    needs_user = accepted_report(
        "proposal:needs_user",
        utility=0.5,
        robustness=0.5,
        vector_id="official_online_request",
    )
    needs_user["decision"] = "revise"
    needs_user["status"] = "needs_revision"
    needs_user["violations"] = [
        {
            "violation_id": "vv_human_input_required",
            "kind": "consistency",
            "description": "ResultProposal requires human input before completion.",
        }
    ]

    gt_report = validate_gt([needs_user, completed])
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }

    assert gt_report["winner"] == "proposal:completed"
    assert score_by_id["proposal:needs_user"]["human_burden_penalty"] > 0
    assert score_by_id["proposal:needs_user"]["accepted"] is False
    gt_report_validator().validate(gt_report)


def test_validate_gt_v02_legal_representative_has_lower_priority_than_safe_primary():
    legal = accepted_report(
        "proposal:legal",
        utility=0.5,
        robustness=0.5,
        vector_id="legal_representative",
        avf_final_viability=0.8,
    )
    official = accepted_report(
        "proposal:official",
        utility=0.5,
        robustness=0.5,
        vector_id="official_online_request",
        avf_final_viability=0.8,
    )

    gt_report = validate_gt([legal, official])
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }

    assert gt_report["winner"] == "proposal:official"
    assert score_by_id["proposal:legal"]["human_burden_penalty"] > 0
    assert score_by_id["proposal:official"]["vector_role_bonus"] > score_by_id["proposal:legal"]["vector_role_bonus"]
    gt_report_validator().validate(gt_report)


def test_validate_gt_v02_illegal_coercion_cannot_be_executable_winner():
    illegal = accepted_report(
        "proposal:illegal",
        utility=10.0,
        robustness=10.0,
        vector_id="illegal_coercion",
    )
    official = accepted_report(
        "proposal:official",
        utility=0.1,
        robustness=0.1,
        vector_id="official_online_request",
    )

    gt_report = validate_gt([illegal, official])
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }

    assert gt_report["winner"] == "proposal:official"
    assert score_by_id["proposal:illegal"]["accepted"] is False
    assert score_by_id["proposal:illegal"]["risk_penalty"] + score_by_id["proposal:illegal"]["human_burden_penalty"] >= 10.0
    gt_report_validator().validate(gt_report)


def test_validate_gt_tie_detected_for_equal_payoff_candidates():
    high_risk = accepted_report(
        "proposal:b_high_risk",
        utility=0.7,
        robustness=0.5,
        violations=0.1,
    )
    low_risk = accepted_report(
        "proposal:a_low_risk",
        utility=0.5,
        robustness=0.5,
    )

    gt_report = validate_gt([high_risk, low_risk])

    assert gt_report["tie_detected"] is True
    assert gt_report["tie_candidate_ids"] == [
        "proposal:a_low_risk",
        "proposal:b_high_risk",
    ]
    assert gt_report["tie_break_rule"] == TIE_BREAK_RULE
    assert gt_report["winner"] == "proposal:a_low_risk"
    assert "tie-break" in gt_report["selection_reason"]
    regrets = {
        candidate["candidate_id"]: candidate["regret"]
        for candidate in gt_report["candidates"]
    }
    assert regrets["proposal:a_low_risk"] == 0.0
    assert regrets["proposal:b_high_risk"] == 0.0
    gt_report_validator().validate(gt_report)


def test_validate_gt_tie_break_prefers_lower_risk():
    high_risk = accepted_report(
        "proposal:high_risk",
        utility=0.7,
        robustness=0.5,
        violations=0.1,
    )
    low_risk = accepted_report(
        "proposal:low_risk",
        utility=0.5,
        robustness=0.5,
    )

    gt_report = validate_gt([high_risk, low_risk])

    assert gt_report["tie_detected"] is True
    assert gt_report["winner"] == "proposal:low_risk"
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }
    assert score_by_id["proposal:low_risk"]["risk_penalty"] < score_by_id["proposal:high_risk"]["risk_penalty"]
    gt_report_validator().validate(gt_report)


def test_validate_gt_tie_break_prefers_lower_cost_after_risk():
    high_cost = accepted_report(
        "proposal:high_cost",
        utility=0.56,
        robustness=0.5,
        compute_cost=0.1,
    )
    low_cost = accepted_report(
        "proposal:low_cost",
        utility=0.5,
        robustness=0.5,
    )

    gt_report = validate_gt([high_cost, low_cost])

    assert gt_report["tie_detected"] is True
    assert gt_report["winner"] == "proposal:low_cost"
    score_by_id = {
        score["proposal_id"]: score
        for score in gt_report["candidate_scores"]
    }
    assert score_by_id["proposal:low_cost"]["cost_penalty"] < score_by_id["proposal:high_cost"]["cost_penalty"]
    gt_report_validator().validate(gt_report)


def test_validate_gt_tie_break_is_deterministic_by_proposal_id():
    report_b = accepted_report(
        "proposal:b",
        utility=0.5,
        robustness=0.5,
    )
    report_a = accepted_report(
        "proposal:a",
        utility=0.5,
        robustness=0.5,
    )

    first = validate_gt([report_b, report_a])
    second = validate_gt([report_a, report_b])

    assert first["tie_detected"] is True
    assert first["winner"] == "proposal:a"
    assert second["winner"] == "proposal:a"
    assert first["tie_candidate_ids"] == ["proposal:a", "proposal:b"]
    gt_report_validator().validate(first)
    gt_report_validator().validate(second)


def test_validate_gt_no_tie_sets_tie_detected_false():
    high = accepted_report(
        "proposal:high",
        utility=0.8,
        robustness=0.5,
    )
    low = accepted_report(
        "proposal:low",
        utility=0.5,
        robustness=0.5,
    )

    gt_report = validate_gt([low, high])

    assert gt_report["winner"] == "proposal:high"
    assert gt_report["tie_detected"] is False
    assert gt_report["tie_candidate_ids"] == []
    assert gt_report["tie_break_rule"] == "highest_payoff"
    assert "highest payoff" in gt_report["selection_reason"]
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
