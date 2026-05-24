from __future__ import annotations

import json
import os
import re

from hedgehog.architect import _make_deterministic_plan_graph
from hedgehog.architect_prompt_compiler import compile_architect_prompt


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


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def _assert_plan_graph_uses_allowed_vectors(plan_graph: dict, attractor_packet: dict) -> None:
    allowed = {vector["vector_id"] for vector in attractor_packet.get("candidate_vectors", [])}
    for node in plan_graph.get("nodes", []):
        if node.get("vector_id") not in allowed:
            raise ValueError(f"PlanGraph node uses disallowed vector_id: {node.get('vector_id')}")
    forbidden_text = json.dumps(plan_graph, sort_keys=True).lower()
    for key in ("final_output", "raw_user_text"):
        if key in forbidden_text:
            raise ValueError(f"PlanGraph contains forbidden key/text: {key}")


def _gemini_plan_graph(attractor_packet: dict, model: str | None, allow_config: bool) -> tuple[dict, str]:
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

    model_name = model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-1.5-flash"
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Gemini dependency is missing: google-generativeai.") from exc

    prompt_contract = compile_architect_prompt(attractor_packet)
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=prompt_contract["system_prompt"],
    )
    response = gemini_model.generate_content(prompt_contract["user_prompt"])
    text = getattr(response, "text", "") or ""
    if not text.strip():
        raise RuntimeError("Gemini Architect returned an empty response.")
    plan_graph = json.loads(_strip_markdown_fences(text))
    _assert_plan_graph_uses_allowed_vectors(plan_graph, attractor_packet)
    return plan_graph, model_name


def make_plan_graph_with_llm(
    *,
    attractor_packet: dict,
    provider: str = "mock",
    model: str | None = None,
    allow_config: bool = True,
) -> dict:
    prompt_contract = compile_architect_prompt(attractor_packet)
    if provider == "mock":
        plan_graph = _make_deterministic_plan_graph(attractor_packet)
        _assert_plan_graph_uses_allowed_vectors(plan_graph, attractor_packet)
        return {
            "status": "completed",
            "provider": "mock",
            "model": model or "mock_architect_v1",
            "used_llm": False,
            "plan_graph": plan_graph,
            "error": None,
            "warnings": [],
            "prompt_contract": prompt_contract,
        }

    if provider != "gemini":
        return {
            "status": "error",
            "provider": provider,
            "model": model or "unknown",
            "used_llm": False,
            "plan_graph": None,
            "error": f"Unsupported Architect provider: {provider}",
            "warnings": ["unsupported_provider"],
            "prompt_contract": prompt_contract,
        }

    try:
        plan_graph, model_name = _gemini_plan_graph(attractor_packet, model, allow_config)
    except Exception as exc:
        return {
            "status": "error",
            "provider": "gemini",
            "model": model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-1.5-flash",
            "used_llm": False,
            "plan_graph": None,
            "error": str(exc),
            "warnings": ["gemini_architect_unavailable"],
            "prompt_contract": prompt_contract,
        }

    return {
        "status": "completed",
        "provider": "gemini",
        "model": model_name,
        "used_llm": True,
        "plan_graph": plan_graph,
        "error": None,
        "warnings": [],
        "prompt_contract": prompt_contract,
    }
