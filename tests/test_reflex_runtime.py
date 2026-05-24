from hedgehog.action_permission import check_action_permission
from hedgehog.reflex import detect_reflex_action, execute_reflex_action


def test_detects_turn_on_tv():
    action = detect_reflex_action("turn on tv")

    assert action["action_id"] == "mock_turn_on_tv"
    assert action["action_kind"] == "device_control"
    assert action["execution_mode"] == "deterministic_reflex"
    assert action["mock_supported"] is True
    assert action["real_execution_supported"] is False


def test_detects_open_camera():
    action = detect_reflex_action("open camera")

    assert action["action_id"] == "mock_open_camera"
    assert action["action_kind"] == "device_control"


def test_detects_show_usual_clips():
    action = detect_reflex_action("show usual clips")

    assert action["action_id"] == "mock_show_usual_clips"
    assert action["action_kind"] == "non_action_preview"


def test_detects_order_pizza_as_confirmation_required():
    action = detect_reflex_action("order pizza")

    assert action["action_id"] == "mock_order_pizza"
    assert action["action_kind"] == "purchase"
    assert action["requires_confirmation"] is True
    assert action["external_side_effect"] is True
    assert action["risk_level"] == "purchase"


def test_unknown_text_returns_none():
    assert detect_reflex_action("solve the certificate problem") is None


def test_blocked_permission_returns_blocked_result():
    action = detect_reflex_action("order pizza")
    permission = check_action_permission(action, user_confirmed=False)
    result = execute_reflex_action(action, permission)

    assert result["action_id"] == "mock_order_pizza"
    assert result["status"] == "blocked"
    assert result["permission_reason"] == "confirmation_required"


def test_allowed_permission_returns_simulated_success():
    action = detect_reflex_action("turn on tv")
    permission = check_action_permission(action)
    result = execute_reflex_action(action, permission)

    assert result["action_id"] == "mock_turn_on_tv"
    assert result["status"] == "simulated_success"
    assert result["permission_reason"] == "allowed"


def test_reflex_uses_declared_metadata_aliases():
    action = detect_reflex_action("switch on tv")

    assert action["action_id"] == "mock_turn_on_tv"
    assert action["mock_supported"] is True


def test_reflex_blocks_actions_without_mock_support():
    action = detect_reflex_action("turn on tv")
    action["mock_supported"] = False
    permission = check_action_permission(action)
    result = execute_reflex_action(action, permission)

    assert result["status"] == "blocked"
    assert result["permission_reason"] == "mock_execution_not_supported"
