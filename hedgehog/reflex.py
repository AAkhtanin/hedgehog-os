from __future__ import annotations

from pathlib import Path

from hedgehog.candidate_vectors import load_declared_actions_from_needles


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEEDLE_PATHS = [
    ROOT / "needles" / "government_services.json",
    ROOT / "needles" / "fallback_exploration.json",
]


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _action_kind_from_metadata(action: dict) -> str:
    capability = action.get("capability")
    if capability in {"device_control", "non_action_preview", "purchase"}:
        return capability
    if action.get("risk_level") == "purchase":
        return "purchase"
    return "device_control"


def _external_side_effect_from_metadata(action: dict) -> bool:
    return action.get("risk_level") in {"purchase", "sensitive", "external"}


def _runtime_action_from_metadata(action: dict) -> dict:
    runtime_action = dict(action)
    runtime_action["action_kind"] = _action_kind_from_metadata(action)
    runtime_action["external_side_effect"] = _external_side_effect_from_metadata(action)
    return runtime_action


def _declared_action_by_alias(declared_actions: list[dict]) -> dict[str, dict]:
    by_alias = {}
    for action in declared_actions:
        if action.get("execution_mode") != "deterministic_reflex":
            continue
        for alias in action.get("intent_aliases", []):
            by_alias[_normalize(alias)] = action
    return by_alias


def default_declared_actions() -> list[dict]:
    return load_declared_actions_from_needles(DEFAULT_NEEDLE_PATHS)


def detect_reflex_action(
    raw_user_text: str,
    declared_actions: list[dict] | None = None,
) -> dict | None:
    actions = declared_actions if declared_actions is not None else default_declared_actions()
    action = _declared_action_by_alias(actions).get(_normalize(raw_user_text))
    if action is None:
        return None
    return _runtime_action_from_metadata(action)


def execute_reflex_action(action: dict, permission: dict) -> dict:
    if action.get("mock_supported") is not True or action.get("real_execution_supported") is True:
        status = "blocked"
        reason = "mock_execution_not_supported"
    else:
        status = "simulated_success" if permission.get("allowed") is True else "blocked"
        reason = permission["reason"]
    return {
        "action_id": action["action_id"],
        "action_kind": action["action_kind"],
        "status": status,
        "permission_reason": reason,
    }
