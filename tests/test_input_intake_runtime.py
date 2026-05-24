from hedgehog.input_intake import classify_input_text


def test_math_text_is_general_request():
    result = classify_input_text("x + y = 110\nx - y = 100")

    assert result["intent_kind"] == "general_request"
    assert result["reason"] == "default_general_request"


def test_arbitrary_question_is_general_request():
    result = classify_input_text("What is a concise way to explain this?")

    assert result["intent_kind"] == "general_request"


def test_certificate_text_is_certificate_demo():
    result = classify_input_text("I need a mock government certificate request.")

    assert result["intent_kind"] == "certificate_demo"
    assert result["confidence"] >= 0.8


def test_unknown_text_does_not_become_certificate_demo():
    result = classify_input_text("hello there")

    assert result["intent_kind"] == "general_request"


def test_known_action_text_is_reflex_candidate():
    result = classify_input_text("turn on tv")

    assert result["intent_kind"] == "reflex_candidate"
