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


def test_purchase_risk_requires_confirmation_even_if_flag_is_missing():
    permission = check_action_permission(
        {
            "action_kind": "purchase",
            "risk_level": "purchase",
            "requires_confirmation": False,
            "external_side_effect": False,
            "mock_supported": True,
            "real_execution_supported": False,
            "permission_policy": {
                "requires_user_confirmation": False,
                "allowed_without_confirmation": True,
            },
        },
        user_confirmed=False,
    )

    assert permission["allowed"] is False
    assert permission["reason"] == "confirmation_required"


def test_low_risk_declared_action_can_pass_without_confirmation():
    permission = check_action_permission(
        {
            "action_kind": "device_control",
            "risk_level": "low",
            "requires_confirmation": False,
            "external_side_effect": False,
            "mock_supported": True,
            "real_execution_supported": False,
            "permission_policy": {
                "requires_user_confirmation": False,
                "allowed_without_confirmation": True,
            },
        }
    )

    assert permission["allowed"] is True
    assert permission["reason"] == "allowed"


def test_mock_unsupported_action_is_blocked():
    permission = check_action_permission(
        {
            "action_kind": "device_control",
            "risk_level": "low",
            "requires_confirmation": False,
            "external_side_effect": False,
            "mock_supported": False,
            "real_execution_supported": False,
        }
    )

    assert permission["allowed"] is False
    assert permission["reason"] == "mock_execution_not_supported"
