from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from hedgehog.telegram_shell import handle_telegram_text


DRS_ROOT = Path("data/drs")
NEEDLES_DIR = Path("needles")
ERROR_LOG_DIR = Path("logs/telegram")
ERROR_LOG_PATH = ERROR_LOG_DIR / "errors.log"


def format_telegram_response(reply_text: str, debug_text: str = "") -> str:
    if debug_text:
        return f"{reply_text}\n\n{debug_text}"
    return reply_text


def _setup_logging() -> logging.Logger:
    ERROR_LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("hedgehog.telegram_bot")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(ERROR_LOG_PATH, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    return logger


def _load_telegram_token() -> str:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN")
        or os.environ.get("BOT_TOKEN")
        or os.environ.get("TELEGRAM_TOKEN")
    )
    if token:
        return token

    try:
        import config  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Telegram token not found. Set TELEGRAM_BOT_TOKEN or provide local config.py."
        ) from exc

    for name in ("TELEGRAM_BOT_TOKEN", "BOT_TOKEN", "TELEGRAM_TOKEN", "TOKEN"):
        value = getattr(config, name, None)
        if value:
            return value

    raise RuntimeError(
        "Telegram token not found in config.py. Expected TELEGRAM_BOT_TOKEN, "
        "BOT_TOKEN, TELEGRAM_TOKEN, or TOKEN."
    )


def bridge_text_message(
    *,
    text: str,
    chat_id: str,
    debug: bool = True,
    force_full_pipeline: bool = True,
    llm_provider: str = "gemini",
) -> dict:
    return handle_telegram_text(
        text=text,
        chat_id=chat_id,
        drs_root=DRS_ROOT,
        needles_dir=NEEDLES_DIR,
        debug=debug,
        force_full_pipeline=force_full_pipeline,
        llm_provider=llm_provider,
    )


def _safe_runtime_error_reply() -> str:
    return "Runtime error. Check local logs."


def _handle_transport_message(message: Any, bot: Any, logger: logging.Logger) -> None:
    text = getattr(message, "text", "") or ""
    chat = getattr(message, "chat", None)
    chat_id = str(getattr(chat, "id", "unknown"))

    try:
        result = bridge_text_message(
            text=text,
            chat_id=chat_id,
            debug=True,
            force_full_pipeline=True,
        )
        bot.send_message(
            chat_id,
            format_telegram_response(result["reply_text"], result["debug_text"]),
        )
    except Exception:
        logger.exception("Telegram bridge runtime error for chat_id=%s", chat_id)
        bot.send_message(chat_id, _safe_runtime_error_reply())


def run_bot() -> None:
    logger = _setup_logging()
    token = _load_telegram_token()

    try:
        import telebot  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "pyTelegramBotAPI is not installed. Install telebot/pyTelegramBotAPI "
            "in the local environment to run telegram_bot.py."
        ) from exc

    bot = telebot.TeleBot(token)

    @bot.message_handler(content_types=["text"])
    def on_text(message: Any) -> None:
        _handle_transport_message(message, bot, logger)

    logger.info("Starting Hedgehog OS Telegram transport bridge.")
    bot.infinity_polling()


if __name__ == "__main__":
    run_bot()
