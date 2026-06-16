from __future__ import annotations

from hedgehog.models import CandidateVector
from hedgehog.policies import HARD_FORBIDDEN_REGIONS


DEFAULT_AVF_WEIGHTS = {
    "rel": 1.0,
    "p_success": 1.0,
    "utility": 1.0,
    "cost": -0.6,
    "risk": -1.0,
    "time_penalty": -0.4,
    "policy_conflict": -2.0,
    "gt_prior": 0.8,
    "novelty": 0.2,
}


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_viability_score(
    vector: CandidateVector, weights: dict | None = None
) -> float:
    active_weights = DEFAULT_AVF_WEIGHTS if weights is None else weights
    features = vector.features.to_dict()
    return sum(features[name] * active_weights[name] for name in DEFAULT_AVF_WEIGHTS)


def compute_hard_mask(
    vector: CandidateVector, hard_forbidden_regions: set[str] | None = None
) -> int:
    regions = HARD_FORBIDDEN_REGIONS if hard_forbidden_regions is None else hard_forbidden_regions
    if vector.hard_forbidden:
        return 0
    if vector.vector_id in regions:
        return 0
    if vector.branching_hint == "forbidden":
        return 0
    return 1


def compute_soft_mask(vector: CandidateVector) -> float:
    features = vector.features
    soft_mask = 1 - features.risk * 0.5 - features.policy_conflict * 0.5
    return _clamp_01(soft_mask)


def score_candidate_vector(
    vector: CandidateVector, weights: dict | None = None
) -> dict:
    hard_mask = compute_hard_mask(vector)
    soft_mask = compute_soft_mask(vector)
    viability_score = compute_viability_score(vector, weights)
    final_viability = 0.0 if hard_mask == 0 else _clamp_01(soft_mask * viability_score)
    return {
        "vector_id": vector.vector_id,
        "source": vector.source,
        "domain": vector.domain,
        "viability_score": viability_score,
        "final_viability": final_viability,
        "hard_masked": hard_mask == 0,
        "soft_mask": soft_mask,
        "branching_mode": vector.branching_hint,
    }


def build_attractor_packet(
    request_id: str,
    intent_id: str,
    world_state_ref: str,
    goal_id: str,
    desired_state: str,
    candidate_vectors: list[CandidateVector],
    as_of: str,
    freshness_required: str = "normal",
    max_selected: int = 3,
    exploration_allowed: bool = True,
    max_exploration_vectors: int = 1,
) -> dict:
    scored_vectors = [
        score_candidate_vector(vector)
        for vector in candidate_vectors
    ]
    selected_vectors = sorted(
        (score for score in scored_vectors if not score["hard_masked"]),
        key=lambda score: score["final_viability"],
        reverse=True,
    )[:max_selected]

    candidate_payloads = [
        {
            "vector_id": score["vector_id"],
            "source": score["source"],
            "domain": score["domain"],
            "final_viability": score["final_viability"],
            "hard_masked": score["hard_masked"],
            "soft_mask": score["soft_mask"],
            "branching_mode": score["branching_mode"],
            "branch_budget": {
                "max_fractals": 3,
                "max_depth": 3,
                "parallelism": 1,
            },
            "selection_status": "selected",
        }
        for score in selected_vectors
    ]

    return {
        "packet_id": f"packet:{request_id}",
        "request_id": request_id,
        "intent_id": intent_id,
        "goal": {
            "goal_id": goal_id,
            "desired_state": desired_state,
        },
        "world_state_ref": world_state_ref,
        "time_context": {
            "as_of": as_of,
            "freshness_required": freshness_required,
        },
        "hard_forbidden_regions": [
            {
                "region_id": region,
                "reason": "hard_policy_violation",
            }
            for region in sorted(HARD_FORBIDDEN_REGIONS)
        ],
        "candidate_vectors": candidate_payloads,
        "branch_budget": {
            "max_fractals": 3,
            "max_depth": 3,
            "parallelism": 1,
        },
        "exploration_budget": {
            "max_exploration_vectors": max_exploration_vectors,
            "exploration_allowed": exploration_allowed,
        },
        "architect_instructions": {
            "do_not_expand_forbidden_regions": True,
            "must_return_time_assumptions": True,
            "must_return_plan_graph_only": True,
        },
    }
