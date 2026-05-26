from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from hedgehog.telegram_shell import handle_telegram_text
from telegram_bot import _load_telegram_token, format_telegram_response


ROOT = Path(__file__).resolve().parents[1]
DRS_ROOT = ROOT / "data" / "drs"
NEEDLES_DIR = ROOT / "needles"
LOG_DIR = ROOT / "logs" / "telegram"
LOG_PATH = LOG_DIR / "polling_smoke_errors.log"
SAFE_OUTPUT_FORBIDDEN_TERMS = ("api_key", "token", "raw_user_text", "config.py")


@dataclass(frozen=True)
class SmokeMapping:
    command: str
    shell_text: str
    force_full_pipeline: bool
    allow_reflex: bool
    llm_provider: str
    user_confirmed: bool
    local_only: bool = False
    local_reply: str = ""


ShellHandler = Callable[..., dict]


def _sanitize_output(value: str) -> str:
    sanitized = value
    for term in SAFE_OUTPUT_FORBIDDEN_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def _command_payload(text: str, command: str) -> str:
    payload = text[len(command) :].strip()
    return payload


def map_smoke_command(
    text: str,
    *,
    provider: str = "mock",
    debug: bool = True,
) -> SmokeMapping:
    stripped = text.strip()
    lowered = stripped.lower()

    if lowered == "/ping":
        return SmokeMapping(
            command="/ping",
            shell_text="",
            force_full_pipeline=True,
            allow_reflex=False,
            llm_provider=provider,
            user_confirmed=False,
            local_only=True,
            local_reply="pong",
        )
    if lowered == "/mode":
        return SmokeMapping(
            command="/mode",
            shell_text="",
            force_full_pipeline=True,
            allow_reflex=False,
            llm_provider=provider,
            user_confirmed=False,
            local_only=True,
            local_reply=(
                "safe smoke commands: /ping, /mode, /reflex turn on tv, "
                "/math x + y = 110 / x - y = 100, /certificate_mock, /debug_last"
            ),
        )
    if lowered == "/debug_last":
        return SmokeMapping(
            command="/debug_last",
            shell_text="",
            force_full_pipeline=True,
            allow_reflex=False,
            llm_provider=provider,
            user_confirmed=False,
            local_only=True,
            local_reply="debug_last is available during manual polling after one handled message.",
        )
    if lowered.startswith("/reflex"):
        payload = _command_payload(stripped, "/reflex") or "turn on tv"
        return SmokeMapping(
            command="/reflex",
            shell_text=payload,
            force_full_pipeline=False,
            allow_reflex=True,
            llm_provider="mock",
            user_confirmed=False,
        )
    if lowered.startswith("/math"):
        payload = _command_payload(stripped, "/math") or "x + y = 110\nx - y = 100"
        return SmokeMapping(
            command="/math",
            shell_text=payload,
            force_full_pipeline=False,
            allow_reflex=False,
            llm_provider=provider,
            user_confirmed=False,
        )
    if lowered == "/certificate_mock":
        return SmokeMapping(
            command="/certificate_mock",
            shell_text="mock certificate request",
            force_full_pipeline=True,
            allow_reflex=False,
            llm_provider="mock",
            user_confirmed=False,
        )

    return SmokeMapping(
        command="text",
        shell_text=stripped,
        force_full_pipeline=True,
        allow_reflex=False,
        llm_provider=provider,
        user_confirmed=False,
    )


def handle_smoke_text(
    *,
    text: str,
    chat_id: str = "telegram_polling_smoke",
    provider: str = "mock",
    debug: bool = True,
    shell_handler: ShellHandler = handle_telegram_text,
) -> dict:
    mapping = map_smoke_command(text, provider=provider, debug=debug)
    if mapping.local_only:
        debug_text = (
            "[debug]\n"
            f"command: {mapping.command}\n"
            "transport: local_smoke\n"
            "network_called: false"
        )
        return {
            "reply_text": mapping.local_reply,
            "debug_text": debug_text if debug else "",
            "response_text": format_telegram_response(mapping.local_reply, debug_text if debug else ""),
            "mapping": mapping,
            "shell_called": False,
        }

    result = shell_handler(
        text=mapping.shell_text,
        chat_id=chat_id,
        drs_root=DRS_ROOT,
        needles_dir=NEEDLES_DIR,
        debug=debug,
        force_full_pipeline=mapping.force_full_pipeline,
        llm_provider=mapping.llm_provider,
        allow_reflex=mapping.allow_reflex,
        user_confirmed=mapping.user_confirmed,
    )
    response_text = format_telegram_response(result["reply_text"], result.get("debug_text", ""))
    return {
        **result,
        "response_text": _sanitize_output(response_text),
        "mapping": mapping,
        "shell_called": True,
    }


def render_dry_run(provider: str = "mock", debug: bool = True) -> str:
    examples = [
        "/ping",
        "/mode",
        "/reflex turn on tv",
        "/math x + y = 110 / x - y = 100",
        "/certificate_mock",
        "/debug_last",
    ]
    lines = [
        "[TELEGRAM POLLING SMOKE]",
        "dry_run: true",
        "network_called: false",
        f"provider: {provider}",
        f"debug: {'true' if debug else 'false'}",
        "note: manual polling only; no secrets are printed",
        "",
        "command | shell_text | force_full_pipeline | allow_reflex | llm_provider",
        "--- | --- | --- | --- | ---",
    ]
    for command in examples:
        mapping = map_smoke_command(command, provider=provider, debug=debug)
        shell_text = mapping.shell_text.replace("\n", " / ") or "local"
        lines.append(
            " | ".join(
                [
                    mapping.command,
                    shell_text,
                    "true" if mapping.force_full_pipeline else "false",
                    "true" if mapping.allow_reflex else "false",
                    mapping.llm_provider,
                ]
            )
        )
    lines.extend(
        [
            "",
            "real polling command:",
            "python -m demo.run_telegram_polling_smoke --provider gemini --debug",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def _setup_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("hedgehog.telegram_polling_smoke")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    return logger


def run_polling(*, provider: str, debug: bool) -> None:
    logger = _setup_logger()
    token = _load_telegram_token()

    try:
        import telebot  # type: ignore
    except ImportError as exc:
        raise RuntimeError("pyTelegramBotAPI is required for manual polling smoke.") from exc

    bot = telebot.TeleBot(token)
    last_result: dict[str, Any] = {}

    @bot.message_handler(content_types=["text"])
    def on_text(message: Any) -> None:
        nonlocal last_result
        text = getattr(message, "text", "") or ""
        chat = getattr(message, "chat", None)
        chat_id = str(getattr(chat, "id", "unknown"))
        try:
            if text.strip().lower() == "/debug_last" and last_result:
                reply = format_telegram_response(
                    "last debug summary",
                    last_result.get("debug_text", ""),
                )
            else:
                result = handle_smoke_text(
                    text=text,
                    chat_id=chat_id,
                    provider=provider,
                    debug=debug,
                )
                last_result = result
                reply = result["response_text"]
            bot.send_message(chat_id, _sanitize_output(reply))
        except Exception:
            logger.exception("Telegram polling smoke runtime error for chat_id=%s", chat_id)
            bot.send_message(chat_id, "Runtime error. Check local logs.")

    logger.info("Starting Telegram polling smoke.")
    bot.infinity_polling()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a safe Telegram polling smoke wrapper.")
    parser.add_argument("--provider", choices=["mock", "gemini"], default="mock")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-polling", action="store_true")
    args = parser.parse_args(argv)

    if args.dry_run or args.no_polling:
        print(render_dry_run(provider=args.provider, debug=args.debug), end="")
        return 0

    run_polling(provider=args.provider, debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
