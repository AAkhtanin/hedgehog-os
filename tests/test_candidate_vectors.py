from pathlib import Path

import pytest

from hedgehog.candidate_vectors import (
    load_candidate_vectors_from_needle,
    load_declared_actions_from_needles,
)
from hedgehog.policies import is_allowed_candidate_source


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def by_id(vectors):
    return {vector.vector_id: vector for vector in vectors}


def test_load_government_services_candidate_vectors():
    vectors = load_candidate_vectors_from_needle(
        NEEDLES_DIR / "government_services.json"
    )

    assert len(vectors) >= 4
    assert all(is_allowed_candidate_source(vector.source) for vector in vectors)

    illegal_coercion = by_id(vectors)["illegal_coercion"]
    assert illegal_coercion.hard_forbidden is True
    assert illegal_coercion.branching_hint == "forbidden"


def test_load_fallback_exploration_candidate_vectors():
    vectors = load_candidate_vectors_from_needle(
        NEEDLES_DIR / "fallback_exploration.json"
    )

    assert len(vectors) == 1
    fallback_exploration = vectors[0]
    assert fallback_exploration.vector_id == "fallback_exploration"
    assert fallback_exploration.source == "fallback_template"
    assert fallback_exploration.requires_architect_creativity is True
    assert fallback_exploration.hard_forbidden is False


def test_invalid_candidate_source_raises_value_error(tmp_path):
    needle = tmp_path / "bad_source.json"
    needle.write_text(
        """
{
  "declared_vectors": [
    {
      "vector_id": "bad",
      "source": "llm_free_generation",
      "domain": "government_certificate",
      "branching_hint": "hybrid",
      "features": {
        "rel": 0.1,
        "p_success": 0.1,
        "utility": 0.1,
        "cost": 0.1,
        "risk": 0.1,
        "time_penalty": 0.1,
        "policy_conflict": 0.1,
        "gt_prior": 0.1,
        "novelty": 0.1
      }
    }
  ]
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_candidate_vectors_from_needle(needle)


def test_missing_declared_vectors_raises_value_error(tmp_path):
    needle = tmp_path / "missing_declared_vectors.json"
    needle.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        load_candidate_vectors_from_needle(needle)


def test_loader_does_not_invent_missing_vector_fields_from_parent_needle(tmp_path):
    needle = tmp_path / "missing_source.json"
    needle.write_text(
        """
{
  "source": "needle",
  "domain": "government_certificate",
  "declared_vectors": [
    {
      "vector_id": "incomplete",
      "branching_hint": "vertical",
      "features": {
        "rel": 0.1,
        "p_success": 0.1,
        "utility": 0.1,
        "cost": 0.1,
        "risk": 0.1,
        "time_penalty": 0.1,
        "policy_conflict": 0.1,
        "gt_prior": 0.1,
        "novelty": 0.1
      }
    }
  ]
}
""",
        encoding="utf-8",
    )

    with pytest.raises((KeyError, ValueError)):
        load_candidate_vectors_from_needle(needle)


def test_load_declared_actions_from_needles_returns_metadata_in_order():
    actions = load_declared_actions_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )

    action_ids = [action["action_id"] for action in actions]
    assert action_ids == [
        "mock_request_certificate",
        "mock_turn_on_tv",
        "mock_open_camera",
        "mock_show_usual_clips",
        "mock_order_pizza",
    ]
    assert actions[1]["intent_aliases"] == ["turn on tv", "switch on tv"]
    assert [step["step_id"] for step in actions[1]["protocol_steps"]] == [
        "validate_tv_command",
        "check_tv_permission",
        "mock_tv_execute",
        "audit_tv_command",
    ]
    assert actions[-1]["risk_level"] == "purchase"
    assert [step["kind"] for step in actions[-1]["protocol_steps"]] == [
        "validate_input",
        "permission_check",
        "mock_execute",
        "mock_receipt",
        "audit_marker",
    ]
    assert all(action["real_execution_supported"] is False for action in actions)
