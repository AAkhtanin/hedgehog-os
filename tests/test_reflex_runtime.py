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
    assert result["protocol_mock_only"] is True
    assert "mock_pizza_execute" not in result["protocol_steps_executed"]
    assert "mock_pizza_receipt" not in result["protocol_steps_executed"]
    assert result["protocol_steps_executed"] == [
        "validate_pizza_order",
        "check_pizza_permission",
        "audit_pizza_order",
    ]


def test_allowed_permission_returns_simulated_success():
    action = detect_reflex_action("turn on tv")
    permission = check_action_permission(action)
    result = execute_reflex_action(action, permission)

    assert result["action_id"] == "mock_turn_on_tv"
    assert result["status"] == "simulated_success"
    assert result["permission_reason"] == "allowed"
    assert result["protocol_mock_only"] is True
    assert result["protocol_steps_executed"] == [
        "validate_tv_command",
        "check_tv_permission",
        "mock_tv_execute",
        "audit_tv_command",
    ]
    assert result["protocol_step_count"] == 4


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


def test_order_pizza_confirmed_executes_mock_protocol_steps():
    action = detect_reflex_action("order pizza")
    permission = check_action_permission(action, user_confirmed=True)
    result = execute_reflex_action(action, permission)

    assert result["status"] == "simulated_success"
    assert result["protocol_steps_executed"] == [
        "validate_pizza_order",
        "check_pizza_permission",
        "mock_pizza_execute",
        "mock_pizza_receipt",
        "audit_pizza_order",
    ]
    assert result["protocol_step_count"] == 5
    assert result["protocol_mock_only"] is True
    assert "real_execution" not in result
    assert "external_side_effect" not in result
