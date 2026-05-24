from telegram_bot import format_telegram_response


def test_format_telegram_response_includes_debug_block():
    response = format_telegram_response("reply", "[debug]\nrequest_id: tg:test")

    assert response == "reply\n\n[debug]\nrequest_id: tg:test"


def test_format_telegram_response_without_debug_returns_reply_only():
    response = format_telegram_response("reply", "")

    assert response == "reply"
