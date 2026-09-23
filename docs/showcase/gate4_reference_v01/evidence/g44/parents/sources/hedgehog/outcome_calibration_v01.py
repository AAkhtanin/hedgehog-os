"""Pure source-bound GT rating, explicit-time decay, and bounded event folding."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import json
import re
import unicodedata

from hedgehog import outcome_feedback_v01 as feedback_v01
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)


PROFILE_ID = "G3_FIXED_POINT_REFERENCE_V01"
UPDATE_SCHEMA = "GT_TRUST_UPDATE_V01"
TRUST_AT_SCHEMA = "GT_TRUST_AT_V01"
FOLD_SCHEMA = "GT_EVENT_FOLD_V01"
NUMERICAL_EVENT_SCHEMA = "GT_NUMERICAL_REFERENCE_EVENT_V01"
NUMERICAL_EVIDENCE_CLASS = "NUMERICAL_REFERENCE_NOT_RUNTIME"
CALCULATION_SOURCE_CLOSURE_REF = (
    "hedgehog.outcome_calibration_v01:G3_FIXED_POINT_REFERENCE_V01"
)

Q = 1_000_000_000
K_FP = 125_000_000
BASE_HALF_LIFE_SECONDS = 86_400
HALF_LIFE_MIN_SECONDS = 3_600
HALF_LIFE_MAX_SECONDS = 604_800
MAXIMUM_TRUST_AGE_SECONDS = 604_800
MAX_EFFECTIVE_EVENTS = 64
WARM_SAMPLE_COUNT = 3
REVIEW_THRESHOLD_FP = 600_000_000
MAX_CANONICAL_BYTES = 262_144

_HEX = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT_FIELDS = (
    "local_root_scope_id",
    "domain_scope_id",
    "pack_family_id",
    "advisory_source_class",
    "advisory_source_revision",
    "advice_claim_profile_id",
    "route_family_id",
    "task_risk_class",
    "validation_profile_id",
    "policy_semantics_version",
    "history_key_profile_id",
)
_OCCURRENCE_FIELDS = (
    "local_root_scope_id",
    "domain_scope_id",
    "producer_occurrence_ref",
    "proposal_ref",
    "purpose",
)
_NUMERICAL_EVENT_FIELDS = frozenset(
    (
        "event_id",
        "schema_version",
        "profile_id",
        "evidence_class",
        "source_profile_id",
        "subject_key",
        "original_occurrence",
        "original_occurrence_id",
        "feedback_id",
        "event_time",
        "causal_sequence",
        "expected_fp",
        "observed_result_fp",
        "proposal_assessment",
        "enforcement_outcome",
        "update_eligibility",
        "pre_decision_expectation_ref",
        "advice_ref",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
        "regret_status",
        "regret_norm_fp",
        "regret_source_ref",
        "safety_status",
        "producer_source_closure_ref",
        "source_refs",
    )
)
_UPDATE_FIELDS = frozenset(
    (
        "update_id",
        "schema_version",
        "profile_id",
        "evidence_class",
        "source_profile_id",
        "subject_key",
        "original_occurrence_id",
        "predecessor_update_ref",
        "accepted_feedback_ref",
        "advice_ref",
        "pre_decision_expectation_ref",
        "rating_before_fp",
        "expected_fp",
        "observed_result_fp",
        "rating_after_fp",
        "k_fp",
        "effective_sample_count",
        "sample_state",
        "observed_at",
        "evaluated_at",
        "history_observation_anchor",
        "history_updated_at",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
        "half_life_seconds",
        "trust_boost_fp",
        "regret_status",
        "regret_norm_fp",
        "regret_factor_fp",
        "regret_source_ref",
        "safety_status",
        "safety_factor_fp",
        "freshness_factor_fp",
        "producer_source_closure_ref",
        "calculation_source_closure_ref",
        "source_refs",
        "explanation_refs",
        "update_disposition",
        "reason_codes",
        "non_authority_flags",
    )
)
_TRUST_FIELDS = frozenset(
    (
        "trust_id",
        "schema_version",
        "profile_id",
        "update_ref",
        "subject_key",
        "sample_state",
        "rating_after_fp",
        "history_observation_anchor",
        "history_updated_at",
        "advice_ref",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
        "evaluated_at",
        "age_seconds",
        "half_life_seconds",
        "trust_status",
        "trust_at_time_fp",
        "review_pressure_fp",
        "review_recommended",
        "mandatory_policy_checks_required",
        "reason_codes",
        "calculation_source_closure_ref",
        "non_authority_flags",
    )
)
_FOLD_FIELDS = frozenset(
    (
        "fold_id",
        "schema_version",
        "profile_id",
        "evidence_class",
        "source_profile_id",
        "subject_key",
        "initial_rating_fp",
        "evaluated_at",
        "ordered_event_refs",
        "accepted_occurrence_ids",
        "effective_sample_count",
        "sample_state",
        "rating_after_fp",
        "final_update_ref",
        "history_observation_anchor",
        "audit",
        "fold_disposition",
        "reason_codes",
        "calculation_source_closure_ref",
        "non_authority_flags",
    )
)


def _require(condition: bool, reason: str = "g33_invalid_input") -> None:
    if not condition:
        raise ValueError(reason)


def _exact_int(value: object, *, low: int = 0, high: int = 2**53 - 1) -> int:
    _require(type(value) is int and low <= value <= high, "g33_integer")
    return value


def _text(value: object) -> str:
    _require(
        type(value) is str
        and 0 < len(value) <= 256
        and unicodedata.normalize("NFC", value) == value
        and not any(ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF for char in value),
        "g33_text",
    )
    return value


def _text_tuple(value: object, *, maximum: int = 128) -> tuple[str, ...]:
    _require(type(value) in (list, tuple) and len(value) <= maximum, "g33_text_array")
    result = tuple(_text(item) for item in value)
    _require(len(result) == len(set(result)), "g33_duplicate_reference")
    return result


def _delivery_ref_tuple(value: object) -> tuple[str, ...]:
    _require(type(value) in (list, tuple) and len(value) <= 256, "g33_text_array")
    return tuple(_text(item) for item in value)


def _closed_keys(value: object, fields: object) -> dict:
    _require(type(value) is dict and set(value) == set(fields), "g33_closed_fields")
    return value


def _tree(value: object, depth: int = 0, count: list[int] | None = None) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    _require(depth <= 12 and count[0] <= 8192, "g33_size_limit")
    if type(value) is dict:
        _require(len(value) <= 128, "g33_size_limit")
        for key, item in value.items():
            _text(key)
            _tree(item, depth + 1, count)
    elif type(value) in (list, tuple):
        _require(len(value) <= 256, "g33_size_limit")
        for item in value:
            _tree(item, depth + 1, count)
    elif type(value) is str:
        _text(value)
    elif type(value) is int:
        _require(abs(value) <= 2**53 - 1, "g33_integer")
    else:
        _require(value is None or type(value) is bool, "g33_scalar_type")


def _canonical(value: object) -> bytes:
    _tree(value)
    result = canonical_json_bytes_v01(value)
    _require(len(result) <= MAX_CANONICAL_BYTES, "g33_size_limit")
    return result


def _pairs(rows):
    result = {}
    for key, value in rows:
        _require(key not in result, "g33_duplicate_json_key")
        result[key] = value
    return result


def _reject_number(value):
    raise ValueError("g33_non_integer_number")


def _decode(raw: bytes) -> dict:
    _require(type(raw) is bytes and len(raw) <= MAX_CANONICAL_BYTES, "g33_canonical_type")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("g33_json") from error
    _require(type(value) is dict and _canonical(value) == raw, "g33_noncanonical")
    return value


def _identity(domain: str, value: object) -> str:
    return domain_separated_sha256_hex_v01(domain=domain, payload=_canonical(value))


def _subject(value: object) -> dict:
    result = _closed_keys(value, _SUBJECT_FIELDS)
    for item in result.values():
        _text(item)
    return result


def _occurrence(value: object) -> dict:
    result = _closed_keys(value, _OCCURRENCE_FIELDS)
    for item in result.values():
        _text(item)
    return result


def _optional_fp(value: object) -> int | None:
    if value is None:
        return None
    return _exact_int(value, high=Q)


def _sample_state(count: int) -> str:
    return "COLD_START_NEUTRAL" if count == 0 else "SPARSE" if count < WARM_SAMPLE_COUNT else "WARM"


def _non_authority(value: object) -> None:
    _closed_keys(value, ("claims_permission", "claims_root_decision", "requests_effect"))
    _require(all(item is False for item in value.values()), "g33_authority_claim")


def _iso_epoch(value: object) -> int:
    _text(value)
    try:
        instant = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("g33_advice_time") from error
    _require(instant.tzinfo is not None and instant.microsecond == 0, "g33_advice_time")
    utc = instant.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = utc - epoch
    result = delta.days * 86_400 + delta.seconds
    return _exact_int(result, high=253402300799)


def round_half_even_rational_v01(numerator: int, denominator: int) -> int:
    """Return exact signed rational round-to-nearest, ties-to-even."""
    _require(type(numerator) is int and type(denominator) is int and denominator > 0, "g33_rational")
    sign = -1 if numerator < 0 else 1
    quotient, remainder = divmod(abs(numerator), denominator)
    comparison = remainder * 2 - denominator
    if comparison > 0 or comparison == 0 and quotient % 2:
        quotient += 1
    return sign * quotient


def _clamp(value: int, low: int, high: int) -> int:
    return low if value < low else high if value > high else value


def _source_bundle(event: "SourceBoundGTEventV01"):
    if event.source_profile_id == feedback_v01.ACTION_ADVICE_SOURCE_PROFILE_ID:
        from hedgehog.domains.supplier_water_filter.adversarial_feedback_v01 import ActionAdviceSourceContextV01
        return ActionAdviceSourceContextV01(event.source_canonical)
    if event.source_profile_id == feedback_v01.PREDICTIVE_SOURCE_PROFILE_ID:
        return feedback_v01.PredictiveOutcomeSourceContextV01(event.source_canonical)
    if event.source_profile_id == feedback_v01.NATIVE_SOURCE_PROFILE_ID:
        return feedback_v01.NativeOutcomeSourceContextV01(event.source_canonical)
    return json.loads(event.source_canonical)


@dataclass(frozen=True, slots=True)
class SourceBoundGTEventV01:
    """Immutable application-supplied feedback plus its independent source bytes."""

    feedback_canonical: bytes
    source_canonical: bytes
    source_profile_id: str

    def __post_init__(self) -> None:
        _require(type(self.feedback_canonical) is bytes and type(self.source_canonical) is bytes)
        _require(
            self.source_profile_id
            in (feedback_v01.SOURCE_PROFILE_ID, feedback_v01.NATIVE_SOURCE_PROFILE_ID, feedback_v01.PREDICTIVE_SOURCE_PROFILE_ID, feedback_v01.ACTION_ADVICE_SOURCE_PROFILE_ID),
            "g33_source_profile",
        )
        value = feedback_v01.OutcomeFeedbackEnvelopeV01(self.feedback_canonical)
        errors = feedback_v01.validate_outcome_feedback_against_sources_v01(
            value,
            source_bundle=_source_bundle(self),
            profile=self.source_profile_id,
        )
        _require(not errors, errors[0] if errors else "g33_feedback_source")


def bind_outcome_feedback_event_v01(
    value: feedback_v01.OutcomeFeedbackEnvelopeV01,
    *,
    source_bundle: dict | feedback_v01.NativeOutcomeSourceContextV01,
    profile: str,
) -> SourceBoundGTEventV01:
    _require(type(value) is feedback_v01.OutcomeFeedbackEnvelopeV01, "g33_feedback_type")
    errors = feedback_v01.validate_outcome_feedback_against_sources_v01(
        value, source_bundle=source_bundle, profile=profile
    )
    _require(not errors, errors[0] if errors else "g33_feedback_source")
    if profile == feedback_v01.ACTION_ADVICE_SOURCE_PROFILE_ID:
        from hedgehog.domains.supplier_water_filter.adversarial_feedback_v01 import ActionAdviceSourceContextV01
        _require(type(source_bundle) is ActionAdviceSourceContextV01,'g36_independent_source_required')
        source_canonical=bytes(source_bundle.canonical)
    elif profile in (feedback_v01.NATIVE_SOURCE_PROFILE_ID, feedback_v01.PREDICTIVE_SOURCE_PROFILE_ID):
        _require(
            type(source_bundle) is (feedback_v01.NativeOutcomeSourceContextV01 if profile == feedback_v01.NATIVE_SOURCE_PROFILE_ID else feedback_v01.PredictiveOutcomeSourceContextV01),
            "g33_native_source_context",
        )
        source_canonical = bytes(source_bundle.canonical)
    else:
        _require(type(source_bundle) is dict, "g33_reference_source_context")
        source_canonical = canonical_json_bytes_v01(source_bundle)
    return SourceBoundGTEventV01(bytes(value.canonical), source_canonical, profile)


def _numerical_event_shape(value: dict) -> None:
    _closed_keys(value, _NUMERICAL_EVENT_FIELDS)
    _require(value["schema_version"] == NUMERICAL_EVENT_SCHEMA and value["profile_id"] == PROFILE_ID)
    _require(value["evidence_class"] == NUMERICAL_EVIDENCE_CLASS)
    for name in (
        "event_id",
        "source_profile_id",
        "original_occurrence_id",
        "feedback_id",
        "pre_decision_expectation_ref",
        "advice_ref",
        "regret_source_ref",
        "producer_source_closure_ref",
    ):
        _text(value[name])
    _require(_HEX.fullmatch(value["event_id"]) is not None and _HEX.fullmatch(value["feedback_id"]) is not None)
    _subject(value["subject_key"])
    occurrence = _occurrence(value["original_occurrence"])
    _require(
        value["original_occurrence_id"]
        == _identity("g3_original_occurrence_v01", occurrence),
        "g33_occurrence_identity",
    )
    for name in (
        "event_time",
        "causal_sequence",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
    ):
        _exact_int(value[name], high=253402300799 if name != "causal_sequence" else 2**53 - 1)
    _require(value["advice_valid_from"] <= value["advice_valid_to"], "g33_advice_window")
    _optional_fp(value["expected_fp"])
    _optional_fp(value["observed_result_fp"])
    _require(value["proposal_assessment"] in ("CORRECT", "INCORRECT", "UNSAFE", "NOT_SCORABLE"))
    _require(
        value["enforcement_outcome"]
        in (
            "BLOCKED_AS_REQUIRED",
            "ALLOWED_AS_REQUIRED",
            "UNEXPECTED_EFFECT",
            "NOT_EXERCISED",
            "UNKNOWN",
        )
    )
    _require(value["update_eligibility"] in ("ELIGIBLE", "NO_UPDATE"))
    _require(value["regret_status"] in ("KNOWN", "UNKNOWN"))
    if value["regret_status"] == "KNOWN":
        _exact_int(value["regret_norm_fp"], high=Q)
    else:
        _require(value["regret_norm_fp"] is None, "g33_regret")
    _require(value["safety_status"] in ("VERIFIED_UNSAFE", "NOT_VERIFIED_UNSAFE"))
    _text_tuple(value["source_refs"])
    if value["update_eligibility"] == "ELIGIBLE":
        _require(value["expected_fp"] is not None and value["observed_result_fp"] in (0, Q), "g33_update_inputs")
        _require(value["enforcement_outcome"] != "UNEXPECTED_EFFECT", "g33_unexpected_effect")
    _require(
        value["event_id"]
        == _identity("g3_gt_numerical_event_v01", {k: v for k, v in value.items() if k != "event_id"}),
        "g33_event_identity",
    )


@dataclass(frozen=True, slots=True)
class GTNumericalEventV01:
    canonical: bytes

    def __post_init__(self) -> None:
        _numerical_event_shape(_decode(self.canonical))


def build_numerical_reference_event_v01(
    *,
    subject_key: dict,
    original_occurrence: dict,
    feedback_id: str,
    event_time: int,
    causal_sequence: int,
    expected_fp: int | None,
    observed_result_fp: int | None,
    proposal_assessment: str,
    enforcement_outcome: str,
    update_eligibility: str,
    pre_decision_expectation_ref: str,
    advice_ref: str,
    advice_created_at: int,
    advice_valid_from: int,
    advice_valid_to: int,
    advice_ttl_seconds: int,
    regret_status: str,
    regret_norm_fp: int | None,
    regret_source_ref: str,
    safety_status: str,
    producer_source_closure_ref: str,
    source_refs: tuple[str, ...],
) -> GTNumericalEventV01:
    occurrence = json.loads(_canonical(original_occurrence))
    material = {
        "schema_version": NUMERICAL_EVENT_SCHEMA,
        "profile_id": PROFILE_ID,
        "evidence_class": NUMERICAL_EVIDENCE_CLASS,
        "source_profile_id": "G33_DECLARED_NUMERICAL_REFERENCE_V01",
        "subject_key": json.loads(_canonical(subject_key)),
        "original_occurrence": occurrence,
        "original_occurrence_id": _identity("g3_original_occurrence_v01", occurrence),
        "feedback_id": feedback_id,
        "event_time": event_time,
        "causal_sequence": causal_sequence,
        "expected_fp": expected_fp,
        "observed_result_fp": observed_result_fp,
        "proposal_assessment": proposal_assessment,
        "enforcement_outcome": enforcement_outcome,
        "update_eligibility": update_eligibility,
        "pre_decision_expectation_ref": pre_decision_expectation_ref,
        "advice_ref": advice_ref,
        "advice_created_at": advice_created_at,
        "advice_valid_from": advice_valid_from,
        "advice_valid_to": advice_valid_to,
        "advice_ttl_seconds": advice_ttl_seconds,
        "regret_status": regret_status,
        "regret_norm_fp": regret_norm_fp,
        "regret_source_ref": regret_source_ref,
        "safety_status": safety_status,
        "producer_source_closure_ref": producer_source_closure_ref,
        "source_refs": list(source_refs),
    }
    material["event_id"] = _identity("g3_gt_numerical_event_v01", material)
    return GTNumericalEventV01(_canonical(material))


def _plain_event(event: SourceBoundGTEventV01 | GTNumericalEventV01) -> dict:
    if type(event) is GTNumericalEventV01:
        value = _decode(event.canonical)
        _numerical_event_shape(value)
        return value
    _require(type(event) is SourceBoundGTEventV01, "g33_event_type")
    supplied = feedback_v01.OutcomeFeedbackEnvelopeV01(event.feedback_canonical)
    source_bundle = _source_bundle(event)
    errors = feedback_v01.validate_outcome_feedback_against_sources_v01(
        supplied, source_bundle=source_bundle, profile=event.source_profile_id
    )
    _require(not errors, errors[0] if errors else "g33_feedback_source")
    value = feedback_v01.outcome_feedback_to_plain_data_v01(supplied)
    source, _ = feedback_v01._source(source_bundle, event.source_profile_id)
    expected = value["pre_decision_expectation"]
    observed = value["observed_result"]
    occurrence = {
        "local_root_scope_id": source["context"]["local_root_scope_id"],
        "domain_scope_id": source["context"]["domain"],
        "producer_occurrence_ref": source["origin"]["occurrence_id"],
        "proposal_ref": source["proposal"]["source_id"],
        "purpose": value["advice_claim_profile_id"],
    }
    advice = value["gt_advice_ref"]
    advice_ref = advice["value"] if advice["state"] == "KNOWN" else source["proposal"]["source_id"]
    # G34's new outcome advice is produced after Work. The predictive claim and E
    # remain prospective; their timestamp is not reused as new advice production.
    advice_created_at = source['observation']['event_time'] if event.source_profile_id == feedback_v01.PREDICTIVE_SOURCE_PROFILE_ID else source['proposal']['created_at']
    if event.source_profile_id == feedback_v01.PREDICTIVE_SOURCE_PROFILE_ID:
        advice_ref = source['native']['capture_ref']
    valid_from = _iso_epoch(value["time_envelope"]["valid_from"])
    valid_to = _iso_epoch(value["time_envelope"]["valid_to"])
    eligible = (
        value["update_eligibility"] == "ELIGIBLE"
        and expected["state"] == "KNOWN"
        and observed["state"] == "KNOWN"
        and observed["value"] in (0, Q)
        and value["enforcement_outcome"] != "UNEXPECTED_EFFECT"
    )
    regret = value["observed_regret"]
    event_material = {
        "event_id": value["feedback_id"],
        "schema_version": NUMERICAL_EVENT_SCHEMA,
        "profile_id": PROFILE_ID,
        "evidence_class": value["evidence_class"],
        "source_profile_id": event.source_profile_id,
        "subject_key": value["advisory_subject_key"],
        "original_occurrence": occurrence,
        "original_occurrence_id": _identity("g3_original_occurrence_v01", occurrence),
        "feedback_id": value["feedback_id"],
        "event_time": value["event_time"],
        "causal_sequence": value["causal_event_sequence"],
        "expected_fp": expected["value"] if expected["state"] == "KNOWN" else None,
        "observed_result_fp": observed["value"] if observed["state"] == "KNOWN" else None,
        "proposal_assessment": value["proposal_assessment"],
        "enforcement_outcome": value["enforcement_outcome"],
        "update_eligibility": "ELIGIBLE" if eligible else "NO_UPDATE",
        "pre_decision_expectation_ref": (
            expected["evidence_refs"][0] if expected["evidence_refs"] else "NO_PRE_OUTCOME_EXPECTATION"
        ),
        "advice_ref": advice_ref,
        "advice_created_at": advice_created_at,
        "advice_valid_from": valid_from,
        "advice_valid_to": valid_to,
        "advice_ttl_seconds": value["time_envelope"]["ttl_seconds"],
        "regret_status": "KNOWN" if regret["state"] == "KNOWN" else "UNKNOWN",
        "regret_norm_fp": regret["value"] if regret["state"] == "KNOWN" else None,
        "regret_source_ref": regret["evidence_refs"][0] if regret["evidence_refs"] else "NO_COUNTERFACTUAL",
        "safety_status": "VERIFIED_UNSAFE" if value["proposal_assessment"] == "UNSAFE" else "NOT_VERIFIED_UNSAFE",
        "producer_source_closure_ref": value["source_closure_ref"],
        "source_refs": list(dict.fromkeys(value["source_refs"] + value["validation_refs"])),
    }
    _subject(event_material["subject_key"])
    _occurrence(event_material["original_occurrence"])
    _optional_fp(event_material["expected_fp"])
    _optional_fp(event_material["observed_result_fp"])
    _exact_int(event_material["event_time"], high=253402300799)
    _exact_int(event_material["causal_sequence"])
    _require(
        event_material["advice_valid_from"] <= event_material["advice_valid_to"],
        "g33_advice_window",
    )
    return event_material


def _update_shape(value: dict) -> None:
    _closed_keys(value, _UPDATE_FIELDS)
    _require(value["schema_version"] == UPDATE_SCHEMA and value["profile_id"] == PROFILE_ID)
    for name in (
        "update_id",
        "evidence_class",
        "source_profile_id",
        "original_occurrence_id",
        "advice_ref",
        "pre_decision_expectation_ref",
        "regret_status",
        "regret_source_ref",
        "safety_status",
        "producer_source_closure_ref",
        "calculation_source_closure_ref",
        "sample_state",
        "update_disposition",
    ):
        _text(value[name])
    _require(_HEX.fullmatch(value["update_id"]) is not None)
    _subject(value["subject_key"])
    for name in ("predecessor_update_ref", "accepted_feedback_ref"):
        _require(value[name] is None or type(value[name]) is str, "g33_update_ref")
    for name in (
        "rating_before_fp",
        "rating_after_fp",
        "k_fp",
        "trust_boost_fp",
        "regret_factor_fp",
        "safety_factor_fp",
        "freshness_factor_fp",
    ):
        _exact_int(value[name], high=Q + Q // 2 if name == "trust_boost_fp" else Q)
    _optional_fp(value["expected_fp"])
    _optional_fp(value["observed_result_fp"])
    for name in (
        "effective_sample_count",
        "observed_at",
        "evaluated_at",
        "history_observation_anchor",
        "history_updated_at",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
    ):
        _exact_int(value[name], high=253402300799)
    _require(value["effective_sample_count"] <= MAX_EFFECTIVE_EVENTS)
    _require(value["sample_state"] == _sample_state(value["effective_sample_count"]), "g33_sample_state")
    _require(value["observed_at"] <= value["evaluated_at"], "g33_update_time")
    _require(value["advice_valid_from"] <= value["advice_valid_to"], "g33_advice_window")
    _require(value["half_life_seconds"] is None or type(value["half_life_seconds"]) is int and HALF_LIFE_MIN_SECONDS <= value["half_life_seconds"] <= HALF_LIFE_MAX_SECONDS)
    _require(value["regret_status"] in ("KNOWN", "UNKNOWN"))
    _optional_fp(value["regret_norm_fp"])
    _require((value["regret_status"] == "KNOWN") == (value["regret_norm_fp"] is not None), "g33_regret")
    _require(value["safety_status"] in ("VERIFIED_UNSAFE", "NOT_VERIFIED_UNSAFE"))
    _text_tuple(value["source_refs"])
    _text_tuple(value["explanation_refs"])
    _text_tuple(value["reason_codes"])
    _require(value["update_disposition"] in ("ACCEPTED", "NO_UPDATE", "CAP_REACHED"))
    _non_authority(value["non_authority_flags"])
    _require(
        value["update_id"]
        == _identity("g3_gt_trust_update_v01", {k: v for k, v in value.items() if k != "update_id"}),
        "g33_update_identity",
    )


@dataclass(frozen=True, slots=True)
class GTTrustUpdateV01:
    canonical: bytes

    def __post_init__(self) -> None:
        _update_shape(_decode(self.canonical))

    def to_plain_data(self) -> dict:
        return _decode(self.canonical)


def _half_life(
    rating_after_fp: int,
    *,
    regret_status: str,
    regret_norm_fp: int | None,
    safety_status: str,
) -> tuple[int, int, int, int, int]:
    trust_boost = Q // 2 + rating_after_fp
    regret_factor = Q - regret_norm_fp if regret_status == "KNOWN" else Q // 2
    freshness_factor = Q
    safety_factor = Q // 2 if safety_status == "VERIFIED_UNSAFE" else Q
    value = round_half_even_rational_v01(
        BASE_HALF_LIFE_SECONDS
        * trust_boost
        * regret_factor
        * freshness_factor
        * safety_factor,
        Q**4,
    )
    return (
        _clamp(value, HALF_LIFE_MIN_SECONDS, HALF_LIFE_MAX_SECONDS),
        trust_boost,
        regret_factor,
        freshness_factor,
        safety_factor,
    )


def evaluate_gt_trust_update_v01(
    event: SourceBoundGTEventV01 | GTNumericalEventV01,
    *,
    predecessor: GTTrustUpdateV01 | None = None,
    evaluated_at: int,
) -> GTTrustUpdateV01:
    """Evaluate one immutable event; caller-supplied predecessors remain unchanged."""
    _exact_int(evaluated_at, high=253402300799)
    source = _plain_event(event)
    return _evaluate_from_plain(
        source,
        predecessor=predecessor,
        evaluated_at=evaluated_at,
        initial_rating_fp=Q // 2,
    )


def _occurrence_fingerprint(value: dict) -> str:
    fields = (
        "subject_key",
        "original_occurrence",
        "event_time",
        "expected_fp",
        "observed_result_fp",
        "proposal_assessment",
        "enforcement_outcome",
        "update_eligibility",
        "pre_decision_expectation_ref",
        "advice_ref",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
        "regret_status",
        "regret_norm_fp",
        "regret_source_ref",
        "safety_status",
        "producer_source_closure_ref",
    )
    return _identity("g3_gt_occurrence_value_v01", {name: value[name] for name in fields})


def _fold_shape(value: dict) -> None:
    _closed_keys(value, _FOLD_FIELDS)
    _require(value["schema_version"] == FOLD_SCHEMA and value["profile_id"] == PROFILE_ID)
    for name in (
        "fold_id",
        "evidence_class",
        "source_profile_id",
        "sample_state",
        "fold_disposition",
        "calculation_source_closure_ref",
    ):
        _text(value[name])
    _require(_HEX.fullmatch(value["fold_id"]) is not None)
    _require(value["subject_key"] is None or type(value["subject_key"]) is dict)
    if value["subject_key"] is not None:
        _subject(value["subject_key"])
    _exact_int(value["initial_rating_fp"], high=Q)
    _exact_int(value["evaluated_at"], high=253402300799)
    _exact_int(value["effective_sample_count"], high=MAX_EFFECTIVE_EVENTS)
    _exact_int(value["rating_after_fp"], high=Q)
    _require(value["sample_state"] == _sample_state(value["effective_sample_count"]), "g33_sample_state")
    ordered_event_refs = _delivery_ref_tuple(value["ordered_event_refs"])
    accepted_occurrence_ids = _text_tuple(
        value["accepted_occurrence_ids"], maximum=MAX_EFFECTIVE_EVENTS
    )
    _require(
        len(accepted_occurrence_ids) == value["effective_sample_count"],
        "g33_fold_occurrences",
    )
    _require(value["final_update_ref"] is None or type(value["final_update_ref"]) is str)
    _require(value["history_observation_anchor"] is None or type(value["history_observation_anchor"]) is int)
    _require(type(value["audit"]) is list and len(value["audit"]) <= 256)
    _require(len(ordered_event_refs) == len(value["audit"]), "g33_fold_audit")
    for event_ref, row in zip(ordered_event_refs, value["audit"]):
        _closed_keys(row, ("event_ref", "occurrence_id", "disposition", "reason_codes"))
        _text(row["event_ref"])
        _require(row["event_ref"] == event_ref, "g33_fold_audit")
        _text(row["occurrence_id"])
        _require(row["disposition"] in ("ACCEPTED", "DUPLICATE", "NO_UPDATE", "CAP_REACHED"))
        _text_tuple(row["reason_codes"])
    _require(
        tuple(
            row["occurrence_id"]
            for row in value["audit"]
            if row["disposition"] == "ACCEPTED"
        )
        == accepted_occurrence_ids,
        "g33_fold_occurrences",
    )
    _require(value["fold_disposition"] in ("EMPTY", "COMPLETE", "CAP_REACHED"))
    _text_tuple(value["reason_codes"])
    _non_authority(value["non_authority_flags"])
    _require(
        value["fold_id"]
        == _identity("g3_gt_event_fold_v01", {k: v for k, v in value.items() if k != "fold_id"}),
        "g33_fold_identity",
    )


@dataclass(frozen=True, slots=True)
class GTEventFoldV01:
    canonical: bytes
    updates: tuple[GTTrustUpdateV01, ...]

    def __post_init__(self) -> None:
        value = _decode(self.canonical)
        _fold_shape(value)
        _require(type(self.updates) is tuple)
        refs = tuple(update.to_plain_data()["update_id"] for update in self.updates)
        _require(len(refs) == value["effective_sample_count"], "g33_fold_updates")
        _require(value["final_update_ref"] == (refs[-1] if refs else None), "g33_fold_final")

    def to_plain_data(self) -> dict:
        return _decode(self.canonical)


def bounded_gt_event_fold_v01(
    events: tuple[SourceBoundGTEventV01 | GTNumericalEventV01, ...],
    *,
    evaluated_at: int,
    initial_rating_fp: int = Q // 2,
) -> GTEventFoldV01:
    """Refold at most 256 deliveries and 64 effective events without persistence."""
    _require(type(events) is tuple and len(events) <= 256, "g33_event_batch")
    _exact_int(evaluated_at, high=253402300799)
    _exact_int(initial_rating_fp, high=Q)
    plain = [_plain_event(event) for event in events]
    plain.sort(key=lambda row: (row["event_time"], row["causal_sequence"], row["feedback_id"]))
    if plain:
        subject = plain[0]["subject_key"]
        evidence_class = plain[0]["evidence_class"]
        source_profile = plain[0]["source_profile_id"]
        for row in plain[1:]:
            _require(row["subject_key"] == subject, "g33_subject_stream_mismatch")
            _require(
                row["evidence_class"] == evidence_class
                and row["source_profile_id"] == source_profile,
                "g33_evidence_lane_mismatch",
            )
    else:
        subject = None
        evidence_class = "NO_EMPIRICAL_HISTORY"
        source_profile = "NONE"
    seen: dict[str, str] = {}
    accepted_occurrences: list[str] = []
    updates: list[GTTrustUpdateV01] = []
    audit: list[dict] = []
    ordered_refs: list[str] = []
    cap_reached = False
    for row in plain:
        event_ref = row["feedback_id"]
        occurrence_id = row["original_occurrence_id"]
        ordered_refs.append(event_ref)
        fingerprint = _occurrence_fingerprint(row)
        if occurrence_id in seen:
            _require(seen[occurrence_id] == fingerprint, "g33_occurrence_conflict")
            audit.append(
                {
                    "event_ref": event_ref,
                    "occurrence_id": occurrence_id,
                    "disposition": "DUPLICATE",
                    "reason_codes": ["ORIGINAL_OCCURRENCE_ALREADY_COUNTED"],
                }
            )
            continue
        seen[occurrence_id] = fingerprint
        if row["update_eligibility"] != "ELIGIBLE":
            audit.append(
                {
                    "event_ref": event_ref,
                    "occurrence_id": occurrence_id,
                    "disposition": "NO_UPDATE",
                    "reason_codes": ["INELIGIBLE_OR_UNSCORABLE_FEEDBACK"],
                }
            )
            continue
        if len(updates) >= MAX_EFFECTIVE_EVENTS:
            cap_reached = True
            audit.append(
                {
                    "event_ref": event_ref,
                    "occurrence_id": occurrence_id,
                    "disposition": "CAP_REACHED",
                    "reason_codes": ["MAX_EFFECTIVE_EVENTS_REACHED"],
                }
            )
            continue
        _require(row["event_time"] <= evaluated_at, "g33_update_time")
        update = _evaluate_from_plain(
            row,
            predecessor=updates[-1] if updates else None,
            evaluated_at=evaluated_at,
            initial_rating_fp=initial_rating_fp,
        )
        updates.append(update)
        accepted_occurrences.append(occurrence_id)
        audit.append(
            {
                "event_ref": event_ref,
                "occurrence_id": occurrence_id,
                "disposition": "ACCEPTED",
                "reason_codes": ["SOURCE_BOUND_NUMERICAL_UPDATE"],
            }
        )
    final = updates[-1].to_plain_data() if updates else None
    material = {
        "schema_version": FOLD_SCHEMA,
        "profile_id": PROFILE_ID,
        "evidence_class": evidence_class,
        "source_profile_id": source_profile,
        "subject_key": subject,
        "initial_rating_fp": initial_rating_fp,
        "evaluated_at": evaluated_at,
        "ordered_event_refs": ordered_refs,
        "accepted_occurrence_ids": accepted_occurrences,
        "effective_sample_count": len(updates),
        "sample_state": _sample_state(len(updates)),
        "rating_after_fp": final["rating_after_fp"] if final else initial_rating_fp,
        "final_update_ref": final["update_id"] if final else None,
        "history_observation_anchor": final["history_observation_anchor"] if final else None,
        "audit": audit,
        "fold_disposition": "CAP_REACHED" if cap_reached else "COMPLETE" if plain else "EMPTY",
        "reason_codes": ["MAX_EFFECTIVE_EVENTS_REACHED"] if cap_reached else ["NO_USABLE_HISTORY"] if not updates else [],
        "calculation_source_closure_ref": CALCULATION_SOURCE_CLOSURE_REF,
        "non_authority_flags": {
            "claims_permission": False,
            "claims_root_decision": False,
            "requests_effect": False,
        },
    }
    material["fold_id"] = _identity("g3_gt_event_fold_v01", material)
    return GTEventFoldV01(_canonical(material), tuple(updates))


def _evaluate_from_plain(
    source: dict,
    *,
    predecessor: GTTrustUpdateV01 | None,
    evaluated_at: int,
    initial_rating_fp: int,
) -> GTTrustUpdateV01:
    previous = predecessor.to_plain_data() if predecessor else None
    if previous is not None:
        _require(previous["profile_id"] == PROFILE_ID, "g33_predecessor_profile")
        _require(previous["subject_key"] == source["subject_key"], "g33_predecessor_subject")
    _require(source["event_time"] <= evaluated_at, "g33_update_time")
    rating_before = previous["rating_after_fp"] if previous else initial_rating_fp
    count_before = previous["effective_sample_count"] if previous else 0
    expected, observed = source["expected_fp"], source["observed_result_fp"]
    if source["update_eligibility"] != "ELIGIBLE" or expected is None or observed not in (0, Q):
        disposition = "NO_UPDATE"
        reasons = ["INELIGIBLE_OR_UNSCORABLE_FEEDBACK"]
    elif source["enforcement_outcome"] == "UNEXPECTED_EFFECT":
        disposition = "NO_UPDATE"
        reasons = ["UNEXPECTED_EFFECT_INVARIANT"]
    elif count_before >= MAX_EFFECTIVE_EVENTS:
        disposition = "CAP_REACHED"
        reasons = ["MAX_EFFECTIVE_EVENTS_REACHED"]
    else:
        disposition = "ACCEPTED"
        reasons = ["SOURCE_BOUND_NUMERICAL_UPDATE"]
    if disposition == "ACCEPTED":
        increment = round_half_even_rational_v01(K_FP * (observed - expected), Q)
        rating_after = _clamp(rating_before + increment, 0, Q)
        count_after = count_before + 1
        half_life, trust_boost, regret_factor, freshness_factor, safety_factor = _half_life(
            rating_after,
            regret_status=source["regret_status"],
            regret_norm_fp=source["regret_norm_fp"],
            safety_status=source["safety_status"],
        )
    else:
        rating_after = rating_before
        count_after = count_before
        half_life = previous["half_life_seconds"] if previous else None
        trust_boost = previous["trust_boost_fp"] if previous else Q
        regret_factor = previous["regret_factor_fp"] if previous else Q // 2
        freshness_factor = previous["freshness_factor_fp"] if previous else Q
        safety_factor = previous["safety_factor_fp"] if previous else Q
    history_anchor = (
        source["event_time"]
        if disposition == "ACCEPTED"
        else previous["history_observation_anchor"] if previous else source["event_time"]
    )
    history_updated = (
        evaluated_at
        if disposition == "ACCEPTED"
        else previous["history_updated_at"] if previous else evaluated_at
    )
    material = {
        "schema_version": UPDATE_SCHEMA,
        "profile_id": PROFILE_ID,
        "evidence_class": source["evidence_class"],
        "source_profile_id": source["source_profile_id"],
        "subject_key": source["subject_key"],
        "original_occurrence_id": source["original_occurrence_id"],
        "predecessor_update_ref": previous["update_id"] if previous else None,
        "accepted_feedback_ref": source["feedback_id"] if disposition == "ACCEPTED" else None,
        "advice_ref": source["advice_ref"],
        "pre_decision_expectation_ref": source["pre_decision_expectation_ref"],
        "rating_before_fp": rating_before,
        "expected_fp": expected,
        "observed_result_fp": observed,
        "rating_after_fp": rating_after,
        "k_fp": K_FP,
        "effective_sample_count": count_after,
        "sample_state": _sample_state(count_after),
        "observed_at": source["event_time"],
        "evaluated_at": evaluated_at,
        "history_observation_anchor": history_anchor,
        "history_updated_at": history_updated,
        "advice_created_at": source["advice_created_at"],
        "advice_valid_from": source["advice_valid_from"],
        "advice_valid_to": source["advice_valid_to"],
        "advice_ttl_seconds": source["advice_ttl_seconds"],
        "half_life_seconds": half_life,
        "trust_boost_fp": trust_boost,
        "regret_status": source["regret_status"],
        "regret_norm_fp": source["regret_norm_fp"],
        "regret_factor_fp": regret_factor,
        "regret_source_ref": source["regret_source_ref"],
        "safety_status": source["safety_status"],
        "safety_factor_fp": safety_factor,
        "freshness_factor_fp": freshness_factor,
        "producer_source_closure_ref": source["producer_source_closure_ref"],
        "calculation_source_closure_ref": CALCULATION_SOURCE_CLOSURE_REF,
        "source_refs": list(source["source_refs"]),
        "explanation_refs": list(
            dict.fromkeys(
                source["source_refs"]
                + [source["pre_decision_expectation_ref"], source["regret_source_ref"]]
            )
        ),
        "update_disposition": disposition,
        "reason_codes": reasons,
        "non_authority_flags": {
            "claims_permission": False,
            "claims_root_decision": False,
            "requests_effect": False,
        },
    }
    material["update_id"] = _identity("g3_gt_trust_update_v01", material)
    return GTTrustUpdateV01(_canonical(material))


def _trust_shape(value: dict) -> None:
    _closed_keys(value, _TRUST_FIELDS)
    _require(value["schema_version"] == TRUST_AT_SCHEMA and value["profile_id"] == PROFILE_ID)
    for name in (
        "trust_id",
        "sample_state",
        "advice_ref",
        "trust_status",
        "calculation_source_closure_ref",
    ):
        _text(value[name])
    _require(_HEX.fullmatch(value["trust_id"]) is not None)
    _require(value["update_ref"] is None or type(value["update_ref"]) is str)
    _require(value["subject_key"] is None or type(value["subject_key"]) is dict)
    if value["subject_key"] is not None:
        _subject(value["subject_key"])
    for name in (
        "rating_after_fp",
        "advice_created_at",
        "advice_valid_from",
        "advice_valid_to",
        "advice_ttl_seconds",
        "evaluated_at",
    ):
        _exact_int(value[name], high=253402300799 if name not in ("rating_after_fp",) else Q)
    for name in ("history_observation_anchor", "history_updated_at", "age_seconds", "half_life_seconds", "trust_at_time_fp"):
        _require(value[name] is None or type(value[name]) is int and value[name] >= 0, "g33_trust_value")
    _exact_int(value["review_pressure_fp"], high=Q)
    _require(type(value["review_recommended"]) is bool and value["mandatory_policy_checks_required"] is True)
    _require(
        value["trust_status"]
        in ("USABLE", "COLD_START_NEUTRAL", "INVALID_TIME", "NOT_YET_VALID", "EXPIRED_NOT_CONSUMABLE")
    )
    _text_tuple(value["reason_codes"])
    _non_authority(value["non_authority_flags"])
    _require(
        value["trust_id"]
        == _identity("g3_gt_trust_at_v01", {k: v for k, v in value.items() if k != "trust_id"}),
        "g33_trust_identity",
    )


@dataclass(frozen=True, slots=True)
class GTTrustAtV01:
    canonical: bytes

    def __post_init__(self) -> None:
        _trust_shape(_decode(self.canonical))

    def to_plain_data(self) -> dict:
        return _decode(self.canonical)


def _decayed_trust(rating: int, age: int, half_life: int) -> int:
    if age % half_life == 0:
        exponent = age // half_life
        if exponent >= 64:
            return 0
        return round_half_even_rational_v01(rating, 2**exponent)
    if age >= 64 * half_life:
        return 0
    with localcontext() as context:
        context.prec = 80
        context.rounding = ROUND_HALF_EVEN
        exponent = -(Decimal(age) / Decimal(half_life)) * Decimal(2).ln()
        value = Decimal(rating) * exponent.exp()
        return int(value.to_integral_value(rounding=ROUND_HALF_EVEN))


def evaluate_gt_decay_value_v01(
    rating_fp: int, *, age_seconds: int, half_life_seconds: int
) -> int:
    """Evaluate only the fixed-point decay formula after separate time admission."""
    _exact_int(rating_fp, high=Q)
    _exact_int(age_seconds, high=2**53 - 1)
    _exact_int(
        half_life_seconds,
        low=HALF_LIFE_MIN_SECONDS,
        high=HALF_LIFE_MAX_SECONDS,
    )
    return _decayed_trust(rating_fp, age_seconds, half_life_seconds)


def evaluate_review_pressure_v01(
    *, trust_status: str, trust_at_time_fp: int | None
) -> tuple[int, bool]:
    """Return advisory pressure; it never suppresses mandatory policy review."""
    _require(
        trust_status
        in (
            "USABLE",
            "COLD_START_NEUTRAL",
            "INVALID_TIME",
            "NOT_YET_VALID",
            "EXPIRED_NOT_CONSUMABLE",
        ),
        "g33_trust_status",
    )
    if trust_status != "USABLE":
        _require(trust_at_time_fp is None, "g33_unusable_trust_value")
        return Q, True
    trust = _exact_int(trust_at_time_fp, high=Q)
    return Q - trust, trust < REVIEW_THRESHOLD_FP


def evaluate_gt_trust_at_v01(
    update: GTTrustUpdateV01 | None,
    *,
    evaluation_time: int,
    advice_ref: str | None = None,
    advice_created_at: int | None = None,
    advice_valid_from: int | None = None,
    advice_valid_to: int | None = None,
    advice_ttl_seconds: int | None = None,
) -> GTTrustAtV01:
    """Evaluate trust at explicit UTC seconds without reading a clock."""
    _exact_int(evaluation_time, high=253402300799)
    source = update.to_plain_data() if update is not None else None
    supplied = (advice_ref, advice_created_at, advice_valid_from, advice_valid_to, advice_ttl_seconds)
    if any(item is not None for item in supplied):
        _require(all(item is not None for item in supplied), "g33_advice_window")
        _text(advice_ref)
        for item in supplied[1:]:
            _exact_int(item, high=253402300799)
        _require(advice_valid_from <= advice_valid_to, "g33_advice_window")
    elif source is not None:
        advice_ref = source["advice_ref"]
        advice_created_at = source["advice_created_at"]
        advice_valid_from = source["advice_valid_from"]
        advice_valid_to = source["advice_valid_to"]
        advice_ttl_seconds = source["advice_ttl_seconds"]
    else:
        advice_ref = "NO_CURRENT_ADVICE"
        advice_created_at = advice_valid_from = 0
        advice_valid_to = 253402300799
        advice_ttl_seconds = 253402300799
    if source is None or source["effective_sample_count"] == 0 or source["update_disposition"] != "ACCEPTED":
        status = "COLD_START_NEUTRAL"
        rating = Q // 2
        history_anchor = history_updated = age = half_life = None
        trust = Q // 2
        pressure = Q
        recommended = True
        reasons = ["NO_USABLE_EMPIRICAL_HISTORY"]
        update_ref = subject = None
        sample_state = "COLD_START_NEUTRAL"
    else:
        update_ref = source["update_id"]
        subject = source["subject_key"]
        sample_state = source["sample_state"]
        rating = source["rating_after_fp"]
        history_anchor = source["history_observation_anchor"]
        history_updated = source["history_updated_at"]
        half_life = source["half_life_seconds"]
        anchor = min(history_anchor, advice_created_at)
        age = evaluation_time - anchor if evaluation_time >= anchor else None
        if evaluation_time < anchor or evaluation_time < history_updated:
            status, reasons = "INVALID_TIME", ["EVALUATION_BEFORE_HISTORY_OR_ADVICE_ANCHOR"]
        elif evaluation_time < advice_created_at or evaluation_time < advice_valid_from:
            status, reasons = "NOT_YET_VALID", ["ADVICE_NOT_YET_VALID"]
        elif (
            age >= MAXIMUM_TRUST_AGE_SECONDS
            or evaluation_time >= advice_valid_to
            or evaluation_time >= advice_created_at + advice_ttl_seconds
        ):
            status, reasons = "EXPIRED_NOT_CONSUMABLE", ["HISTORY_OR_ADVICE_EXPIRED"]
        else:
            status, reasons = "USABLE", ["EXPLICIT_TIME_DECAY_APPLIED"]
        if status == "USABLE":
            trust = evaluate_gt_decay_value_v01(
                rating, age_seconds=age, half_life_seconds=half_life
            )
            pressure, recommended = evaluate_review_pressure_v01(
                trust_status=status, trust_at_time_fp=trust
            )
        else:
            trust = None
            pressure, recommended = evaluate_review_pressure_v01(
                trust_status=status, trust_at_time_fp=None
            )
    material = {
        "schema_version": TRUST_AT_SCHEMA,
        "profile_id": PROFILE_ID,
        "update_ref": update_ref,
        "subject_key": subject,
        "sample_state": sample_state,
        "rating_after_fp": rating,
        "history_observation_anchor": history_anchor,
        "history_updated_at": history_updated,
        "advice_ref": advice_ref,
        "advice_created_at": advice_created_at,
        "advice_valid_from": advice_valid_from,
        "advice_valid_to": advice_valid_to,
        "advice_ttl_seconds": advice_ttl_seconds,
        "evaluated_at": evaluation_time,
        "age_seconds": age,
        "half_life_seconds": half_life,
        "trust_status": status,
        "trust_at_time_fp": trust,
        "review_pressure_fp": pressure,
        "review_recommended": recommended,
        "mandatory_policy_checks_required": True,
        "reason_codes": reasons,
        "calculation_source_closure_ref": CALCULATION_SOURCE_CLOSURE_REF,
        "non_authority_flags": {
            "claims_permission": False,
            "claims_root_decision": False,
            "requests_effect": False,
        },
    }
    material["trust_id"] = _identity("g3_gt_trust_at_v01", material)
    return GTTrustAtV01(_canonical(material))


def validate_calibration_against_sources_v01(
    value: GTTrustUpdateV01 | GTEventFoldV01 | GTTrustAtV01,
    *,
    events: tuple[SourceBoundGTEventV01 | GTNumericalEventV01, ...],
    fold_evaluated_at: int,
    initial_rating_fp: int = Q // 2,
    evaluation_time: int | None = None,
    advice_window: dict | None = None,
) -> tuple[str, ...]:
    """Independently recompute a supplied derived value from immutable sources."""
    try:
        fold = bounded_gt_event_fold_v01(
            events, evaluated_at=fold_evaluated_at, initial_rating_fp=initial_rating_fp
        )
        if type(value) is GTEventFoldV01:
            _require(value.canonical == fold.canonical, "g33_fold_source_mismatch")
            _require(
                tuple(item.canonical for item in value.updates)
                == tuple(item.canonical for item in fold.updates),
                "g33_fold_update_mismatch",
            )
        elif type(value) is GTTrustUpdateV01:
            plain = [_plain_event(event) for event in events]
            plain.sort(
                key=lambda row: (
                    row["event_time"],
                    row["causal_sequence"],
                    row["feedback_id"],
                )
            )
            seen: dict[str, str] = {}
            predecessor = None
            candidates: list[GTTrustUpdateV01] = []
            for row in plain:
                occurrence_id = row["original_occurrence_id"]
                fingerprint = _occurrence_fingerprint(row)
                if occurrence_id in seen:
                    _require(
                        seen[occurrence_id] == fingerprint,
                        "g33_occurrence_conflict",
                    )
                    continue
                seen[occurrence_id] = fingerprint
                candidate = _evaluate_from_plain(
                    row,
                    predecessor=predecessor,
                    evaluated_at=fold_evaluated_at,
                    initial_rating_fp=initial_rating_fp,
                )
                candidates.append(candidate)
                if candidate.to_plain_data()["update_disposition"] == "ACCEPTED":
                    predecessor = candidate
            _require(
                any(value.canonical == item.canonical for item in candidates),
                "g33_update_source_mismatch",
            )
        elif type(value) is GTTrustAtV01:
            _require(evaluation_time is not None, "g33_evaluation_time_required")
            update = fold.updates[-1] if fold.updates else None
            kwargs = {}
            if advice_window is not None:
                _closed_keys(
                    advice_window,
                    (
                        "advice_ref",
                        "advice_created_at",
                        "advice_valid_from",
                        "advice_valid_to",
                        "advice_ttl_seconds",
                    ),
                )
                kwargs = dict(advice_window)
            expected = evaluate_gt_trust_at_v01(
                update, evaluation_time=evaluation_time, **kwargs
            )
            _require(value.canonical == expected.canonical, "g33_trust_source_mismatch")
        else:
            raise ValueError("g33_derived_type")
        return ()
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as error:
        reason = str(error)
        return (reason if reason.startswith(("g31_", "g32_", "g33_")) else "g33_invalid_input",)


@dataclass(frozen=True, slots=True)
class AVFHistoryPriorV01:
    canonical: bytes

    def __post_init__(self):
        value = _decode(self.canonical)
        _closed_keys(value, ('prior_id','profile','fold_ref','history_key','source_profile','lane',
            'accepted_occurrence_ids','prior_fp','effective_count','positive','negative','unresolved','sample_state'))
        _require(value['profile']=='G34_AVF_EMA_V01','g34_prior_profile')
        _closed_keys(value['history_key'],feedback_v01._HISTORY_FIELDS)
        for item in value['history_key'].values(): _text(item)
        _require(type(value['prior_fp']) is int and -Q<=value['prior_fp']<=Q,'g34_prior_value')
        for name in ('effective_count','positive','negative','unresolved'): _exact_int(value[name],high=256)
        _require(value['effective_count']<=64 and value['positive']+value['negative']==value['effective_count'],'g34_prior_count')
        _text_tuple(value['accepted_occurrence_ids'],maximum=64)
        _require(len(value['accepted_occurrence_ids'])==value['effective_count']
            and len(set(value['accepted_occurrence_ids']))==value['effective_count'],'g34_prior_occurrences')
        _require(value['sample_state']==_sample_state(value['effective_count']),'g34_prior_sample_state')
        _require(value['source_profile'] in (feedback_v01.SOURCE_PROFILE_ID,feedback_v01.NATIVE_SOURCE_PROFILE_ID,
            feedback_v01.PREDICTIVE_SOURCE_PROFILE_ID,feedback_v01.ACTION_ADVICE_SOURCE_PROFILE_ID),'g34_prior_source_profile')
        _text(value['lane']);_text(value['fold_ref'])
        _require(value['prior_id']==_identity('g34_avf_prior_v01',{k:v for k,v in value.items() if k!='prior_id'}),'g34_prior_identity')

    def to_plain_data(self):
        return _decode(self.canonical)


def fold_avf_history_prior_v01(events, *, evaluated_at):
    """Use exactly the GT fold's admitted occurrence set, never delivery count."""
    _require(type(events) is tuple and bool(events),'g34_history_events_required')
    fold=bounded_gt_event_fold_v01(events,evaluated_at=evaluated_at)
    admitted=fold.to_plain_data()['accepted_occurrence_ids']
    values=[feedback_v01.outcome_feedback_to_plain_data_v01(feedback_v01.OutcomeFeedbackEnvelopeV01(e.feedback_canonical)) for e in events]
    first=values[0]
    _require(all((v['avf_history_key'],v['source_profile_id'],v['execution_lane']) ==
        (first['avf_history_key'],first['source_profile_id'],first['execution_lane']) for v in values),'g34_incomparable_history')
    rows=sorted((_plain_event(e) for e in events),key=lambda v:(v['event_time'],v['causal_sequence'],v['feedback_id']))
    prior=positive=negative=unresolved=0;seen=set()
    for row in rows:
        occurrence=row['original_occurrence_id']
        if occurrence in seen: continue
        seen.add(occurrence)
        if occurrence not in admitted:
            if row['update_eligibility']!='ELIGIBLE': unresolved+=1
            continue
        signal=2*row['observed_result_fp']-Q
        increment=round_half_even_rational_v01(62_500_000*(signal-prior),Q)
        _require(abs(increment)<=Q//8,'g34_step_bound')
        prior=_clamp(prior+increment,-Q,Q)
        positive+=row['observed_result_fp']==Q
        negative+=row['observed_result_fp']==0
    result=dict(profile='G34_AVF_EMA_V01',fold_ref=fold.to_plain_data()['fold_id'],history_key=first['avf_history_key'],
        source_profile=first['source_profile_id'],lane=first['execution_lane'],accepted_occurrence_ids=admitted,
        prior_fp=prior,effective_count=len(admitted),positive=positive,negative=negative,unresolved=unresolved,
        sample_state=_sample_state(len(admitted)))
    result['prior_id']=_identity('g34_avf_prior_v01',result)
    return AVFHistoryPriorV01(_canonical(result))


def adjusted_avf_score_v01(base_score_fp, prior_fp):
    _exact_int(base_score_fp,high=Q)
    _require(type(prior_fp) is int and -Q<=prior_fp<=Q,'g34_prior_value')
    adjusted=_clamp(base_score_fp+round_half_even_rational_v01(250_000_000*prior_fp,Q),0,Q)
    return adjusted,round_half_even_rational_v01(adjusted*1_000_000,Q)


def validate_avf_prior_against_sources_v01(value, *, events, evaluated_at):
    try:
        _require(type(value) is AVFHistoryPriorV01,'g34_prior_type')
        _require(value.canonical==fold_avf_history_prior_v01(events,evaluated_at=evaluated_at).canonical,'g34_prior_source_mismatch')
        return ()
    except (ValueError,TypeError,KeyError,AttributeError) as error:
        return (str(error),)
