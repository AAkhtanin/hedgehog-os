from __future__ import annotations


KNOWN_ACTION_KINDS = {
    "device_control",
    "non_action_preview",
    "purchase",
}

CONFIRMATION_RISK_LEVELS = {"purchase", "sensitive", "external"}


def check_action_permission(action: dict, user_confirmed: bool = False) -> dict:
    action_kind = action.get("action_kind")
    risk_level = action.get("risk_level")
    permission_policy = action.get("permission_policy", {})

    if action.get("mock_supported") is False or action.get("real_execution_supported") is True:
        return {
            "allowed": False,
            "reason": "mock_execution_not_supported",
        }

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

    requires_confirmation = (
        action.get("requires_confirmation") is True
        or permission_policy.get("requires_user_confirmation") is True
        or risk_level in CONFIRMATION_RISK_LEVELS
    )
    allowed_without_confirmation = permission_policy.get(
        "allowed_without_confirmation",
        not requires_confirmation,
    )

    if requires_confirmation and user_confirmed is False:
        return {
            "allowed": False,
            "reason": "confirmation_required",
        }

    if (
        action.get("external_side_effect") is True
        and user_confirmed is False
        and allowed_without_confirmation is not True
    ):
        return {
            "allowed": False,
            "reason": "external_side_effect_requires_confirmation",
        }

    return {
        "allowed": True,
        "reason": "allowed",
    }
