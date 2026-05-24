from __future__ import annotations


REFLEX_ALIASES = {
    "turn on tv",
    "open camera",
    "repeat last route",
    "show usual clips",
    "order pizza",
}

CERTIFICATE_TERMS = {
    "certificate",
    "mock government",
    "government certificate",
    "government service request",
    "government service",
}


def classify_input_text(text: str) -> dict:
    normalized = " ".join(text.strip().lower().split())
    if not normalized:
        return {
            "intent_kind": "general_request",
            "normalized_text": "",
            "confidence": 0.5,
            "reason": "empty_or_whitespace_text",
        }

    if normalized in REFLEX_ALIASES:
        return {
            "intent_kind": "reflex_candidate",
            "normalized_text": normalized,
            "confidence": 0.95,
            "reason": "known_reflex_alias",
        }

    if any(term in normalized for term in CERTIFICATE_TERMS):
        return {
            "intent_kind": "certificate_demo",
            "normalized_text": normalized,
            "confidence": 0.9,
            "reason": "certificate_demo_terms_present",
        }

    return {
        "intent_kind": "general_request",
        "normalized_text": normalized,
        "confidence": 0.8,
        "reason": "default_general_request",
    }
