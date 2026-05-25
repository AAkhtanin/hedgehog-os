from __future__ import annotations

import os
import re


GENERAL_RESPONDER_SYSTEM_PROMPT = """You are a subordinate GeneralResponder inside Hedgehog OS.
You are not the RootOrchestrator.
You do not create FinalOutput.
You answer the user's general request clearly and directly.
Do not claim to have performed real external actions.
Do not call tools.
Do not invent DRS writes, traces, or system state.
If the request is math, solve it directly and show concise steps.
If uncertain, say what is uncertain.
Return only the user-facing answer text, not JSON."""


def _config_value(*names: str, allow_config: bool = True) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value

    if not allow_config:
        return None

    try:
        import config  # type: ignore
    except ImportError:
        return None

    for name in names:
        value = getattr(config, name, None)
        if value:
            return value
    return None


def _mock_answer(text: str) -> str:
    normalized = text.lower()
    compact = re.sub(r"\s+", "", normalized)
    if "x+y=110" in compact and "x-y=100" in compact:
        return "x = 105\ny = 5"
    return "Mock general response: this request was routed to the GeneralResponder path."


def _gemini_answer(
    text: str,
    model: str | None,
    system_prompt: str,
    allow_config: bool,
) -> tuple[str, str]:
    api_key = _config_value(
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        allow_config=allow_config,
    )
    if not api_key:
        if allow_config:
            raise RuntimeError("Gemini API key is missing from environment or local config.py.")
        raise RuntimeError(
            "Gemini API key is missing from environment and config lookup is disabled."
        )

    model_name = model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-3.5-flash"

    try:
        from google import genai  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Gemini dependency is missing: google-genai.") from exc

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=text,
        config={
            "system_instruction": system_prompt,
        },
    )
    answer = getattr(response, "text", "") or ""
    if not answer.strip():
        raise RuntimeError("Gemini returned an empty response.")
    return answer.strip(), model_name


def generate_general_answer(
    *,
    text: str,
    request_id: str,
    provider: str = "mock",
    model: str | None = None,
    system_prompt: str | None = None,
    allow_config: bool = True,
) -> dict:
    prompt = system_prompt or GENERAL_RESPONDER_SYSTEM_PROMPT
    if provider == "mock":
        return {
            "status": "completed",
            "provider": "mock",
            "model": model or "mock_general_responder_v1",
            "used_llm": False,
            "answer": _mock_answer(text),
            "claims": [
                "general_responder_was_subordinate",
                "root_must_create_final_output",
            ],
            "warnings": [],
            "error": None,
        }

    if provider != "gemini":
        return {
            "status": "error",
            "provider": provider,
            "model": model or "unknown",
            "used_llm": False,
            "answer": "",
            "claims": [],
            "warnings": ["unsupported_provider"],
            "error": f"Unsupported LLM provider: {provider}",
        }

    try:
        answer, model_name = _gemini_answer(text, model, prompt, allow_config)
    except Exception as exc:
        return {
            "status": "error",
            "provider": "gemini",
            "model": model
            or _config_value("GEMINI_MODEL", allow_config=allow_config)
            or "gemini-3.5-flash",
            "used_llm": False,
            "answer": "",
            "claims": [],
            "warnings": ["gemini_unavailable"],
            "error": str(exc),
        }

    return {
        "status": "completed",
        "provider": "gemini",
        "model": model_name,
        "used_llm": True,
        "answer": answer,
        "claims": [
            "general_responder_was_subordinate",
            "root_must_create_final_output",
        ],
        "warnings": [],
        "error": None,
    }
