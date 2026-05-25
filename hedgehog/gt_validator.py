from __future__ import annotations

import math

from hedgehog.time_model import utc_now_iso


DEFAULT_ELO = 1500.0
DEFAULT_K = 32.0
DEFAULT_HALF_LIFE_BASE_HOURS = 720.0
PAYOFF_FORMULA_VERSION = "gt_payoff_v0_1"


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _normalized_features(vv_report: dict) -> dict:
    if "normalized_features" in vv_report:
        return vv_report["normalized_features"]

    scores = vv_report.get("scores", {})
    evidence = float(scores.get("evidence", 0.0))
    consistency = float(scores.get("consistency", 0.0))
    time = float(scores.get("time", 0.0))
    policy = float(scores.get("policy", 0.0))
    return {
        "utility": float(vv_report.get("overall_score", 0.0)),
        "robustness": (evidence + consistency + time) / 3,
        "compute_cost": 0.0,
        "violations": 1.0 - policy,
        "transfer": 0.0,
        "novelty_guard": 0.0,
    }


def compute_payoff(vv_report: dict) -> float:
    return compute_payoff_components(vv_report)["payoff"]


def _has_violation_kind(vv_report: dict, kind: str) -> bool:
    return any(
        isinstance(violation, dict) and violation.get("kind") == kind
        for violation in vv_report.get("violations", [])
    )


def compute_payoff_components(vv_report: dict) -> dict:
    features = _normalized_features(vv_report)
    report_class = classify_vv_report(vv_report)
    utility = float(features.get("utility", 0.0))
    robustness = float(features.get("robustness", 0.0))
    cost_penalty = 0.6 * float(features.get("compute_cost", 0.0))
    policy_penalty = 2.0 * float(features.get("violations", 0.0))
    novelty_or_reuse_bonus = (
        0.3 * float(features.get("transfer", 0.0))
        + 0.2 * float(features.get("novelty_guard", 0.0))
    )
    status_bonus = 0.25 if report_class == "accepted_completed" else 0.0
    semantic_penalty = 0.0
    notes = []

    if report_class == "accepted_completed":
        notes.append("accepted_completed")
    elif report_class == "needs_revision":
        semantic_penalty += 0.75
        notes.append("needs_revision_penalty")
    elif report_class == "rejected":
        semantic_penalty += 1.5
        notes.append("rejected_penalty")
    else:
        semantic_penalty += 0.25
        notes.append("unknown_status_penalty")

    if _has_violation_kind(vv_report, "human_input"):
        semantic_penalty += 0.25
        notes.append("human_input_required")
    if _has_violation_kind(vv_report, "blocked"):
        semantic_penalty += 0.5
        notes.append("blocked_before_completion")

    risk_penalty = policy_penalty + semantic_penalty
    payoff = (
        utility
        + robustness
        + status_bonus
        + novelty_or_reuse_bonus
        - risk_penalty
        - cost_penalty
    )
    return {
        "proposal_id": vv_report.get("proposal_id", "unknown"),
        "status": vv_report.get("status", "unknown"),
        "accepted": report_class == "accepted_completed",
        "utility": utility,
        "risk_penalty": risk_penalty,
        "cost_penalty": cost_penalty,
        "robustness": robustness,
        "status_bonus": status_bonus,
        "novelty_or_reuse_bonus": novelty_or_reuse_bonus,
        "payoff": payoff,
        "regret": 0.0,
        "selection_notes": notes,
    }


def classify_vv_report(vv_report: dict) -> str:
    decision = vv_report.get("decision")
    status = vv_report.get("status")
    if decision == "accept" and status == "accepted":
        return "accepted_completed"
    if decision == "revise" or status == "needs_revision":
        return "needs_revision"
    if decision == "reject" or status == "rejected":
        return "rejected"
    return "unknown"


def _softmax_mix(scored_candidates: list[tuple[dict, float]]) -> list[dict]:
    max_payoff = max(payoff for _, payoff in scored_candidates)
    exp_values = [
        (report, math.exp(payoff - max_payoff))
        for report, payoff in scored_candidates
    ]
    total = sum(value for _, value in exp_values)
    return [
        {
            "candidate_id": report["proposal_id"],
            "probability": value / total if total else 0.0,
        }
        for report, value in exp_values
    ]


def _rating_update(is_winner: bool) -> tuple[float, float, float, float]:
    expected = 0.5
    result = 1.0 if is_winner else 0.0
    elo_after = DEFAULT_ELO + DEFAULT_K * (result - expected)
    return DEFAULT_ELO, elo_after, expected, result


def _score_reports(vv_reports: list[dict]) -> list[dict]:
    scores = [
        compute_payoff_components(report)
        for report in vv_reports
        if classify_vv_report(report) in {"accepted_completed", "needs_revision"}
    ]
    if not scores:
        return []
    best_payoff = max(score["payoff"] for score in scores)
    for score in scores:
        score["regret"] = best_payoff - score["payoff"]
    return scores


def _regret_summary(candidate_scores: list[dict]) -> dict:
    if not candidate_scores:
        return {
            "candidate_count": 0,
            "max_regret": 0.0,
            "mean_regret": 0.0,
        }
    regrets = [float(score.get("regret", 0.0)) for score in candidate_scores]
    return {
        "candidate_count": len(candidate_scores),
        "max_regret": max(regrets),
        "mean_regret": sum(regrets) / len(regrets),
    }


def _dominated_candidate_ids(candidate_scores: list[dict], winner_id: str | None) -> list[str]:
    if winner_id is None:
        return []
    winner = next(
        (score for score in candidate_scores if score["proposal_id"] == winner_id),
        None,
    )
    if winner is None:
        return []
    dominated = []
    for score in candidate_scores:
        if score["proposal_id"] == winner_id:
            continue
        if (
            score["payoff"] <= winner["payoff"]
            and score["utility"] <= winner["utility"]
            and score["robustness"] <= winner["robustness"]
            and score["risk_penalty"] >= winner["risk_penalty"]
            and score["cost_penalty"] >= winner["cost_penalty"]
        ):
            dominated.append(score["proposal_id"])
    return dominated


def validate_gt(vv_reports: list[dict], game_mode: str = "result_selection") -> dict:
    accepted_reports = [
        report
        for report in vv_reports
        if classify_vv_report(report) == "accepted_completed"
    ]
    needs_revision_reports = [
        report
        for report in vv_reports
        if classify_vv_report(report) == "needs_revision"
    ]
    created_at = utc_now_iso()
    request_id = vv_reports[0].get("request_id") if vv_reports else None
    candidate_scores = _score_reports(vv_reports)
    base_benchmark_fields = {
        "payoff_formula_version": PAYOFF_FORMULA_VERSION,
        "candidate_scores": candidate_scores,
        "regret_summary": _regret_summary(candidate_scores),
        "dominated_candidate_ids": [],
    }

    if not accepted_reports:
        if needs_revision_reports:
            report = {
                "gt_report_id": f"gt:{game_mode}:revise",
                "game_mode": game_mode,
                "candidates": [],
                "decision": "revise",
                "created_at": created_at,
                **base_benchmark_fields,
                "selection_reason": "no accepted completed candidates; needs_revision candidates require revision before selection",
                "notes": [
                    "Only needs_revision Post V&V candidates were available; GT did not select a winner.",
                    "Needs-revision candidates do not receive Elo or half-life promotion.",
                    f"payoff_formula_version={PAYOFF_FORMULA_VERSION}",
                ],
            }
            if request_id is not None:
                report["request_id"] = request_id
            return report
        report = {
            "gt_report_id": f"gt:{game_mode}:no_update",
            "game_mode": game_mode,
            "candidates": [],
            "decision": "no_update",
            "created_at": created_at,
            **base_benchmark_fields,
            "selection_reason": "no accepted completed candidates available",
            "notes": ["No accepted Post V&V candidates; GT returned no_update."],
        }
        if request_id is not None:
            report["request_id"] = request_id
        return report

    scored_candidates = [
        (report, compute_payoff(report))
        for report in accepted_reports
    ]
    max_payoff = max(payoff for _, payoff in scored_candidates)
    winner_report, _ = max(
        scored_candidates,
        key=lambda item: (item[1], item[0]["proposal_id"]),
    )
    winner_id = winner_report["proposal_id"]
    winner_score = next(
        score for score in candidate_scores if score["proposal_id"] == winner_id
    )
    max_regret = max(max_payoff - payoff for _, payoff in scored_candidates) or 1.0

    candidates = []
    ratings = []
    half_life_values = []
    decay_values = []
    for report, payoff in scored_candidates:
        candidate_id = report["proposal_id"]
        is_winner = candidate_id == winner_id
        elo_before, elo_after, expected, result = _rating_update(is_winner)
        regret = max_payoff - payoff
        normalized_regret = _clamp(regret / max_regret, 0.0, 1.0)
        half_life_hours = max(
            1.0,
            DEFAULT_HALF_LIFE_BASE_HOURS
            * _sigmoid((elo_after - DEFAULT_ELO) / 200)
            * (1.0 - normalized_regret),
        )
        decay_rate = math.log(2) / half_life_hours

        candidates.append(
            {
                "candidate_id": candidate_id,
                "candidate_type": "result_proposal",
                "payoff": payoff,
                "regret": regret,
                "elo_before": elo_before,
                "elo_after": elo_after,
            }
        )
        ratings.append(
            {
                "candidate_id": candidate_id,
                "rating_before": elo_before,
                "rating_after": elo_after,
                "expected": expected,
                "result": result,
            }
        )
        half_life_values.append(half_life_hours)
        decay_values.append(decay_rate)

    dominance = "none"
    if len(scored_candidates) == 1:
        dominance = "strict"
    elif sorted((payoff for _, payoff in scored_candidates), reverse=True)[0] > sorted(
        (payoff for _, payoff in scored_candidates), reverse=True
    )[1]:
        dominance = "weak"

    gt_report = {
        "gt_report_id": f"gt:{game_mode}:{winner_id}",
        "game_mode": game_mode,
        "candidates": candidates,
        "decision": "accept",
        "created_at": created_at,
        "winner": winner_id,
        "mix": _softmax_mix(scored_candidates),
        "ratings": ratings,
        "half_life_hours": max(half_life_values),
        "decay_rate": min(decay_values),
        "dominance": dominance,
        **base_benchmark_fields,
        "winner_payoff": winner_score["payoff"],
        "dominated_candidate_ids": _dominated_candidate_ids(candidate_scores, winner_id),
        "selection_reason": "selected highest payoff among accepted completed candidates; GT is not TruthProof",
        "audit": {
            "audit_id": f"audit:gt:{winner_id}",
            "hash": "deterministic_mvp_gt",
        },
        "notes": [
            "GT selects by deterministic payoff; this is not TruthProof.",
            f"payoff_formula_version={PAYOFF_FORMULA_VERSION}",
            "needs_revision and blocked candidates are scored for diagnostics but cannot win while accepted_completed candidates exist.",
        ],
    }
    if request_id is not None:
        gt_report["request_id"] = request_id
    return gt_report
