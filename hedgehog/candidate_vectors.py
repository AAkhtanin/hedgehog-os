from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from hedgehog.models import CandidateVector
from hedgehog.policies import is_allowed_candidate_source


def load_needle(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_candidate_vectors_from_needle(path: Path) -> list[CandidateVector]:
    needle = load_needle(path)
    declared_vectors = needle.get("declared_vectors")
    if not isinstance(declared_vectors, list):
        raise ValueError(f"{path} must contain declared_vectors as a list")

    vectors: list[CandidateVector] = []
    for raw_vector in declared_vectors:
        vector = CandidateVector.from_dict(raw_vector)
        if not is_allowed_candidate_source(vector.source):
            raise ValueError(f"candidate source is not allowed: {vector.source}")
        vectors.append(vector)
    return vectors


def load_candidate_vectors_from_needles(paths: Iterable[Path]) -> list[CandidateVector]:
    vectors: list[CandidateVector] = []
    for path in paths:
        vectors.extend(load_candidate_vectors_from_needle(path))
    return vectors
