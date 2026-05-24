from __future__ import annotations


KNOWN_ACTION_KINDS = {
    "device_control",
    "non_action_preview",
    "purchase",
}


def check_action_permission(action: dict, user_confirmed: bool = False) -> dict:
    action_kind = action.get("action_kind")
    if action_kind == "non_action_preview":
        return {
            "allowed": True,
            "reason": "preview_only",
        }

    if action_kind not in KNOWN_ACTION_KINDS:
        return {
            "allowed": False,
            "reason": "unknown_action_kind",
        }

    if action.get("requires_confirmation") is True and user_confirmed is False:
        return {
            "allowed": False,
            "reason": "confirmation_required",
        }

    if action.get("external_side_effect") is True and user_confirmed is False:
        return {
            "allowed": False,
            "reason": "external_side_effect_requires_confirmation",
        }

    return {
        "allowed": True,
        "reason": "allowed",
    }
