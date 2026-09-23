from __future__ import annotations

from datetime import UTC, datetime


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def make_time_envelope(
    session_anchor: str,
    ttl_seconds: int = 2_592_000,
    freshness_class: str = "normal",
) -> dict:
    now = utc_now_iso()
    return {
        "pt_created_at": now,
        "kt_asof": now,
        "et_observed_at": None,
        "ct_session_anchor": session_anchor,
        "ttl_seconds": ttl_seconds,
        "freshness_class": freshness_class,
        "valid_from": now,
        "valid_to": None,
    }


def make_temporal_query(
    max_age_seconds: int = 2_592_000,
    freshness_bias: str = "prefer_recent",
) -> dict:
    now = utc_now_iso()
    return {
        "as_of": now,
        "time_range": {
            "from": None,
            "to": now,
        },
        "freshness_bias": freshness_bias,
        "max_age_seconds": max_age_seconds,
        "freshness_required": "normal",
    }
