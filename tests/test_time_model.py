from datetime import datetime

from hedgehog.time_model import make_temporal_query, make_time_envelope


def parse_iso_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def test_make_time_envelope_contains_schema_fields_and_defaults():
    envelope = make_time_envelope(session_anchor="sess_001")

    assert set(envelope) == {
        "pt_created_at",
        "kt_asof",
        "et_observed_at",
        "ct_session_anchor",
        "ttl_seconds",
        "freshness_class",
        "valid_from",
        "valid_to",
    }
    assert envelope["ct_session_anchor"] == "sess_001"
    assert envelope["ttl_seconds"] == 2_592_000
    assert envelope["freshness_class"] == "normal"
    assert envelope["et_observed_at"] is None
    assert envelope["valid_to"] is None
    assert parse_iso_timestamp(envelope["pt_created_at"]).tzinfo is not None
    assert parse_iso_timestamp(envelope["kt_asof"]).tzinfo is not None
    assert parse_iso_timestamp(envelope["valid_from"]).tzinfo is not None


def test_make_temporal_query_contains_schema_fields_and_defaults():
    query = make_temporal_query()

    assert set(query) == {
        "as_of",
        "time_range",
        "freshness_bias",
        "max_age_seconds",
        "freshness_required",
    }
    assert query["freshness_bias"] == "prefer_recent"
    assert query["max_age_seconds"] == 2_592_000
    assert query["freshness_required"] == "normal"
    assert query["time_range"]["from"] is None
    assert query["time_range"]["to"] == query["as_of"]
    assert parse_iso_timestamp(query["as_of"]).tzinfo is not None
    assert parse_iso_timestamp(query["time_range"]["to"]).tzinfo is not None
