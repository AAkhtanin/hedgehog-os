from pathlib import Path

import pytest

from hedgehog.candidate_vectors import load_candidate_vectors_from_needle
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
