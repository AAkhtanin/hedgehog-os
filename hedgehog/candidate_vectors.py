from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from hedgehog.models import CandidateVector
from hedgehog.policies import is_allowed_candidate_source


REQUIRED_DECLARED_ACTION_FIELDS = {
    "action_id",
    "intent_aliases",
    "capability",
    "execution_mode",
    "risk_level",
    "requires_confirmation",
    "mock_supported",
    "real_execution_supported",
    "permission_policy",
    "audit_required",
    "drs_writeback_required",
    "output_contract",
}


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


def _validate_declared_action(action: dict, path: Path) -> None:
    missing = REQUIRED_DECLARED_ACTION_FIELDS - set(action)
    if missing:
        raise ValueError(f"{path} declared_action missing fields: {sorted(missing)}")
    if not isinstance(action["intent_aliases"], list) or not action["intent_aliases"]:
        raise ValueError(f"{path} declared_action intent_aliases must be a non-empty list")
    if action["real_execution_supported"] is not False:
        raise ValueError("real action execution is not supported in the MVP")
    if action["audit_required"] is not True:
        raise ValueError("declared actions must require audit")
    if action["drs_writeback_required"] is not True:
        raise ValueError("declared actions must require DRS writeback")
    if not isinstance(action["permission_policy"], dict):
        raise ValueError("declared action permission_policy must be an object")


def load_declared_actions_from_needle(path: Path) -> list[dict]:
    needle = load_needle(path)
    declared_actions = needle.get("declared_actions", [])
    if declared_actions is None:
        declared_actions = []
    if not isinstance(declared_actions, list):
        raise ValueError(f"{path} declared_actions must be a list when present")

    actions = []
    for raw_action in declared_actions:
        if not isinstance(raw_action, dict):
            raise ValueError(f"{path} declared_actions items must be objects")
        _validate_declared_action(raw_action, path)
        actions.append(dict(raw_action))
    return actions


def load_declared_actions_from_needles(paths: Iterable[Path]) -> list[dict]:
    actions: list[dict] = []
    for path in paths:
        actions.extend(load_declared_actions_from_needle(path))
    return actions
