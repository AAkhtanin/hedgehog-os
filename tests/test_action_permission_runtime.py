from hedgehog.action_permission import check_action_permission


def test_preview_action_is_allowed():
    permission = check_action_permission(
        {
            "action_kind": "non_action_preview",
            "requires_confirmation": False,
            "external_side_effect": False,
        }
    )

    assert permission["allowed"] is True
    assert permission["reason"] == "preview_only"


def test_purchase_action_is_blocked_without_confirmation():
    permission = check_action_permission(
        {
            "action_kind": "purchase",
            "requires_confirmation": True,
            "external_side_effect": True,
        },
        user_confirmed=False,
    )

    assert permission["allowed"] is False
    assert permission["reason"] == "confirmation_required"


def test_purchase_action_is_allowed_with_confirmation():
    permission = check_action_permission(
        {
            "action_kind": "purchase",
            "requires_confirmation": True,
            "external_side_effect": True,
        },
        user_confirmed=True,
    )

    assert permission["allowed"] is True
    assert permission["reason"] == "allowed"


def test_unknown_action_is_blocked():
    permission = check_action_permission(
        {
            "action_kind": "unknown_action",
            "requires_confirmation": False,
            "external_side_effect": False,
        }
    )

    assert permission["allowed"] is False
    assert permission["reason"] == "unknown_action_kind"
