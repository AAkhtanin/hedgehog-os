from __future__ import annotations

from hedgehog.reflex import default_declared_actions


SIMPLE_ACTION_COMMANDS = {
    "turn on tv",
    "open camera",
    "repeat last route",
    "show usual clips",
}


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _declared_reflex_aliases() -> set[str]:
    aliases = set()
    for action in default_declared_actions():
        if action.get("execution_mode") != "deterministic_reflex":
            continue
        for alias in action.get("intent_aliases", []):
            aliases.add(_normalize(alias))
    return aliases


def classify_intent_complexity(raw_user_text: str) -> str:
    normalized = _normalize(raw_user_text)
    if detect_reflex_candidate(normalized):
        return "simple_known_action"
    if len(normalized.split()) <= 4:
        return "simple"
    return "normal"


def detect_reflex_candidate(raw_user_text: str) -> bool:
    normalized = _normalize(raw_user_text)
    return normalized in SIMPLE_ACTION_COMMANDS or normalized in _declared_reflex_aliases()


def route_execution(
    raw_user_text: str,
    retrieved_records: list[dict],
    reuse_gate: dict,
    allow_direct_reuse: bool = False,
    force_full_pipeline: bool = True,
) -> dict:
    if force_full_pipeline:
        return {
            "execution_mode": "proof_full_pipeline",
            "direct_reuse_allowed": False,
            "reason": "forced_full_pipeline_for_demo",
            "intent_complexity": classify_intent_complexity(raw_user_text),
        }

    if (
        allow_direct_reuse
        and reuse_gate.get("reuse_decision") == "direct_reuse_candidate"
    ):
        return {
            "execution_mode": "direct_reuse",
            "direct_reuse_allowed": True,
            "reason": "eligible_direct_reuse",
            "intent_complexity": classify_intent_complexity(raw_user_text),
        }

    if retrieved_records:
        return {
            "execution_mode": "context_only",
            "direct_reuse_allowed": False,
            "reason": "memory_context_only",
            "intent_complexity": classify_intent_complexity(raw_user_text),
        }

    if detect_reflex_candidate(raw_user_text):
        return {
            "execution_mode": "deterministic_reflex_candidate",
            "direct_reuse_allowed": False,
            "reason": "simple_known_action_candidate",
            "intent_complexity": "simple_known_action",
        }

    return {
        "execution_mode": "proof_full_pipeline",
        "direct_reuse_allowed": False,
        "reason": "default_full_pipeline",
        "intent_complexity": classify_intent_complexity(raw_user_text),
    }
