from __future__ import annotations


REFLEX_ACTIONS = {
    "turn on tv": {
        "action_id": "mock_turn_on_tv",
        "action_kind": "device_control",
        "requires_confirmation": False,
        "external_side_effect": False,
    },
    "open camera": {
        "action_id": "mock_open_camera",
        "action_kind": "device_control",
        "requires_confirmation": False,
        "external_side_effect": False,
    },
    "show usual clips": {
        "action_id": "mock_show_usual_clips",
        "action_kind": "non_action_preview",
        "requires_confirmation": False,
        "external_side_effect": False,
    },
    "order pizza": {
        "action_id": "mock_order_pizza",
        "action_kind": "purchase",
        "requires_confirmation": True,
        "external_side_effect": True,
    },
}


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def detect_reflex_action(raw_user_text: str) -> dict | None:
    action = REFLEX_ACTIONS.get(_normalize(raw_user_text))
    if action is None:
        return None
    return dict(action)


def execute_reflex_action(action: dict, permission: dict) -> dict:
    status = "simulated_success" if permission.get("allowed") is True else "blocked"
    return {
        "action_id": action["action_id"],
        "action_kind": action["action_kind"],
        "status": status,
        "permission_reason": permission["reason"],
    }
