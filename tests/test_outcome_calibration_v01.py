"""Focused G3-3 numerical, source-bound, and one native producer control."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN, getcontext, localcontext
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys

import pytest

from hedgehog import outcome_calibration_v01 as calibration
from hedgehog import outcome_feedback_v01 as feedback
from hedgehog.domains.landslide_sentinel import events_v01 as sentinel_events
from hedgehog.domains.landslide_sentinel import semantic_adapter_v01 as sentinel_semantics
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode
from hedgehog.domains.landslide_sentinel.outcome_feedback_adapter_v01 import (
    SentinelOutcomeSourceV01,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def reference():
    return json.loads((ROOT / "fixtures/gate3_calibration_reference_v01.json").read_bytes())


def _feedback_id(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _numerical_event(
    reference,
    index: int,
    *,
    expected_fp: int | None,
    observed_result_fp: int | None,
    proposal_assessment: str,
    eligibility: str = "ELIGIBLE",
    occurrence: str | None = None,
    subject: dict | None = None,
    feedback_label: str | None = None,
    event_time: int | None = None,
    causal_sequence: int | None = None,
    regret_status: str = "UNKNOWN",
    regret_norm_fp: int | None = None,
    safety_status: str | None = None,
):
    subject = deepcopy(subject or reference["subject_key"])
    window = reference["advice_window"]
    occurrence = occurrence or f"occurrence:g33:{index}"
    if safety_status is None:
        safety_status = (
            "VERIFIED_UNSAFE"
            if proposal_assessment == "UNSAFE"
            else "NOT_VERIFIED_UNSAFE"
        )
    return calibration.build_numerical_reference_event_v01(
        subject_key=subject,
        original_occurrence={
            "local_root_scope_id": subject["local_root_scope_id"],
            "domain_scope_id": subject["domain_scope_id"],
            "producer_occurrence_ref": occurrence,
            "proposal_ref": f"proposal:g33:{index}",
            "purpose": subject["advice_claim_profile_id"],
        },
        feedback_id=_feedback_id(feedback_label or f"g33-feedback-{index}"),
        event_time=event_time if event_time is not None else 1000 + index,
        causal_sequence=causal_sequence if causal_sequence is not None else index,
        expected_fp=expected_fp,
        observed_result_fp=observed_result_fp,
        proposal_assessment=proposal_assessment,
        enforcement_outcome=(
            "BLOCKED_AS_REQUIRED"
            if proposal_assessment == "UNSAFE"
            else "ALLOWED_AS_REQUIRED"
        ),
        update_eligibility=eligibility,
        pre_decision_expectation_ref=f"expectation:g33:{index}",
        advice_ref=window["advice_ref"],
        advice_created_at=window["advice_created_at"],
        advice_valid_from=window["advice_valid_from"],
        advice_valid_to=window["advice_valid_to"],
        advice_ttl_seconds=window["advice_ttl_seconds"],
        regret_status=regret_status,
        regret_norm_fp=regret_norm_fp,
        regret_source_ref=(
            f"counterfactual:g33:{index}"
            if regret_status == "KNOWN"
            else "NO_COUNTERFACTUAL"
        ),
        safety_status=safety_status,
        producer_source_closure_ref="fixture:gate3_calibration_reference_v01",
        source_refs=(f"source:g33:{index}",),
    )


def _sequence(reference, rows, *, start=1):
    return tuple(
        _numerical_event(
            reference,
            start + index,
            expected_fp=row["expected_fp"],
            observed_result_fp=row["observed_result_fp"],
            proposal_assessment=row["proposal_assessment"],
        )
        for index, row in enumerate(rows)
    )


def _equivalent_event(event):
    return calibration.GTNumericalEventV01(bytes(event.canonical))


def _same_occurrence_wrapper(
    event,
    *,
    feedback_label: str,
    causal_sequence: int,
):
    value = calibration._decode(event.canonical)
    value["feedback_id"] = _feedback_id(feedback_label)
    value["causal_sequence"] = causal_sequence
    value["source_refs"] = [f"source:{feedback_label}"]
    value["event_id"] = calibration._identity(
        "g3_gt_numerical_event_v01",
        {key: item for key, item in value.items() if key != "event_id"},
    )
    return calibration.GTNumericalEventV01(calibration._canonical(value))


def test_g33_signed_rational_rounding_and_increment_position(reference):
    for numerator, denominator, expected in reference["rounding_cases"]:
        assert calibration.round_half_even_rational_v01(numerator, denominator) == expected
        fraction = Fraction(numerator, denominator)
        quotient, remainder = divmod(abs(fraction.numerator), fraction.denominator)
        if remainder * 2 > fraction.denominator or (
            remainder * 2 == fraction.denominator and quotient % 2
        ):
            quotient += 1
        oracle = (-1 if fraction < 0 else 1) * quotient
        assert oracle == expected
    row = reference["increment_counterexample"]
    event = _numerical_event(
        reference,
        90,
        expected_fp=row["expected_fp"],
        observed_result_fp=row["observed_result_fp"],
        proposal_assessment="INCORRECT",
    )
    fold = calibration.bounded_gt_event_fold_v01(
        (event,), evaluated_at=1090, initial_rating_fp=row["rating_before_fp"]
    )
    assert fold.to_plain_data()["rating_after_fp"] == row["rating_after_fp"]
    assert fold.to_plain_data()["rating_after_fp"] != row["incorrect_complete_sum_rounding"]


@pytest.mark.parametrize("series", ("negative_then_positive", "positive_then_negative"))
def test_g33_named_rating_and_half_life_vectors(reference, series):
    events = _sequence(reference, reference[series], start=10 if series.startswith("negative") else 20)
    fold = calibration.bounded_gt_event_fold_v01(events, evaluated_at=1200)
    assert [row.to_plain_data()["rating_after_fp"] for row in fold.updates] == [
        row["rating_after_fp"] for row in reference[series]
    ]
    assert [row.to_plain_data()["half_life_seconds"] for row in fold.updates] == [
        row["half_life_seconds"] for row in reference[series]
    ]
    assert not calibration.validate_calibration_against_sources_v01(
        fold, events=events, fold_evaluated_at=1200
    )
    assert fold.to_plain_data()["sample_state"] == "WARM"


def test_g33_regret_safety_factors_and_profile_bounds(reference):
    unknown = _numerical_event(
        reference,
        31,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    known_zero = _numerical_event(
        reference,
        32,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
        regret_status="KNOWN",
        regret_norm_fp=0,
    )
    incorrect = _numerical_event(
        reference,
        33,
        expected_fp=500000000,
        observed_result_fp=0,
        proposal_assessment="INCORRECT",
    )
    unsafe = _numerical_event(
        reference,
        34,
        expected_fp=500000000,
        observed_result_fp=0,
        proposal_assessment="UNSAFE",
    )
    values = [
        calibration.evaluate_gt_trust_update_v01(event, evaluated_at=1200).to_plain_data()
        for event in (unknown, known_zero, incorrect, unsafe)
    ]
    assert values[0]["regret_factor_fp"] == calibration.Q // 2
    assert values[1]["regret_factor_fp"] == calibration.Q
    assert values[1]["half_life_seconds"] == 91800
    assert values[2]["safety_factor_fp"] == calibration.Q
    assert values[3]["safety_factor_fp"] == calibration.Q // 2
    assert values[2]["half_life_seconds"] == 40500
    assert values[3]["half_life_seconds"] == 20250
    full_regret = _numerical_event(
        reference,
        35,
        expected_fp=500000000,
        observed_result_fp=0,
        proposal_assessment="UNSAFE",
        regret_status="KNOWN",
        regret_norm_fp=calibration.Q,
    )
    assert (
        calibration.evaluate_gt_trust_update_v01(full_regret, evaluated_at=1200)
        .to_plain_data()["half_life_seconds"]
        == calibration.HALF_LIFE_MIN_SECONDS
    )
    assert calibration.HALF_LIFE_MAX_SECONDS == 604800


def test_g33_frozen_expectation_is_not_replaced_by_fold_predecessor(reference):
    first = _numerical_event(
        reference,
        36,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    second = _numerical_event(
        reference,
        37,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    fold = calibration.bounded_gt_event_fold_v01(
        (first, second), evaluated_at=1200
    )
    rows = [value.to_plain_data() for value in fold.updates]
    assert rows[0]["rating_after_fp"] == 562500000
    assert rows[1]["rating_before_fp"] == 562500000
    assert rows[1]["expected_fp"] == 500000000
    assert rows[1]["rating_after_fp"] == 625000000


def _independent_round_half_even(numerator, denominator):
    assert type(numerator) is int and type(denominator) is int and denominator > 0
    quotient, remainder = divmod(abs(numerator), denominator)
    if remainder * 2 > denominator or (
        remainder * 2 == denominator and quotient % 2
    ):
        quotient += 1
    return -quotient if numerator < 0 else quotient


def _high_precision_decay(rating, age, half_life):
    if age % half_life == 0:
        return _independent_round_half_even(rating, 2 ** (age // half_life))
    with localcontext() as context:
        context.prec = 220
        context.rounding = ROUND_HALF_EVEN
        value = Decimal(rating) * context.power(
            Decimal(2), -(Decimal(age) / Decimal(half_life))
        )
        return int(value.to_integral_value(rounding=ROUND_HALF_EVEN))


def test_g33_decay_named_vectors_seeded_oracle_and_local_decimal(reference):
    original_precision, original_rounding = getcontext().prec, getcontext().rounding
    for numerator, denominator, expected in reference["rounding_cases"]:
        assert _independent_round_half_even(numerator, denominator) == expected
    assert _high_precision_decay(5, 3600, 3600) == 2
    assert _high_precision_decay(3, 1800, 3600) == 2
    for rating, age, half_life, expected in reference["decay_vectors"]:
        assert calibration.evaluate_gt_decay_value_v01(
            rating, age_seconds=age, half_life_seconds=half_life
        ) == expected
    spec = reference["seeded_decay_oracle"]
    generator = random.Random(spec["seed"])
    maximum = 0
    for _ in range(spec["case_count"]):
        rating = generator.randint(*spec["rating_range"])
        age = generator.randint(*spec["age_range"])
        half_life = generator.randint(*spec["half_life_range"])
        actual = calibration.evaluate_gt_decay_value_v01(
            rating, age_seconds=age, half_life_seconds=half_life
        )
        expected = _high_precision_decay(rating, age, half_life)
        maximum = max(maximum, abs(actual - expected))
    assert maximum <= spec["maximum_fixed_point_difference"]
    assert (getcontext().prec, getcontext().rounding) == (
        original_precision,
        original_rounding,
    )


def test_g33_explicit_time_boundaries_and_advice_history_anchors(reference):
    event = _numerical_event(
        reference,
        41,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
        event_time=1001,
    )
    update = calibration.bounded_gt_event_fold_v01(
        (event,), evaluated_at=1001
    ).updates[-1]
    assert calibration.evaluate_gt_trust_at_v01(
        update, evaluation_time=1000
    ).to_plain_data()["trust_status"] == "INVALID_TIME"
    override = dict(
        advice_ref="advice:g33:future",
        advice_created_at=1100,
        advice_valid_from=1100,
        advice_valid_to=900000,
        advice_ttl_seconds=800000,
    )
    assert calibration.evaluate_gt_trust_at_v01(
        update, evaluation_time=1099, **override
    ).to_plain_data()["trust_status"] == "NOT_YET_VALID"
    old_advice = dict(
        advice_ref="advice:g33:old",
        advice_created_at=1,
        advice_valid_from=1,
        advice_valid_to=604801,
        advice_ttl_seconds=604800,
    )
    expired = calibration.evaluate_gt_trust_at_v01(
        update, evaluation_time=604801, **old_advice
    ).to_plain_data()
    assert expired["trust_status"] == "EXPIRED_NOT_CONSUMABLE"
    at_valid_to = calibration.evaluate_gt_trust_at_v01(
        update,
        evaluation_time=1200,
        advice_ref="advice:g33:boundary",
        advice_created_at=1000,
        advice_valid_from=1000,
        advice_valid_to=1200,
        advice_ttl_seconds=500,
    ).to_plain_data()
    assert at_valid_to["trust_status"] == "EXPIRED_NOT_CONSUMABLE"
    pressure, recommended = calibration.evaluate_review_pressure_v01(
        trust_status="USABLE", trust_at_time_fp=600000000
    )
    assert pressure == 400000000 and recommended is False
    pressure, recommended = calibration.evaluate_review_pressure_v01(
        trust_status="USABLE", trust_at_time_fp=599999999
    )
    assert pressure == 400000001 and recommended is True
    cold = calibration.evaluate_gt_trust_at_v01(None, evaluation_time=1000).to_plain_data()
    assert cold["trust_status"] == "COLD_START_NEUTRAL"
    assert cold["rating_after_fp"] == calibration.Q // 2
    assert cold["review_pressure_fp"] == calibration.Q
    minimum_half_life = _numerical_event(
        reference,
        42,
        expected_fp=500000000,
        observed_result_fp=0,
        proposal_assessment="UNSAFE",
        event_time=1000,
        regret_status="KNOWN",
        regret_norm_fp=calibration.Q,
    )
    minimum_update = calibration.bounded_gt_event_fold_v01(
        (minimum_half_life,), evaluated_at=1000
    ).updates[-1]
    zero = calibration.evaluate_gt_trust_at_v01(
        minimum_update,
        evaluation_time=231400,
        advice_ref="advice:g33:zero",
        advice_created_at=1000,
        advice_valid_from=1000,
        advice_valid_to=700000,
        advice_ttl_seconds=699000,
    ).to_plain_data()
    assert zero["trust_status"] == "USABLE" and zero["trust_at_time_fp"] == 0
    new_advice_old_history = calibration.evaluate_gt_trust_at_v01(
        update,
        evaluation_time=700000,
        advice_ref="advice:g33:new-does-not-refresh-history",
        advice_created_at=700000,
        advice_valid_from=700000,
        advice_valid_to=900000,
        advice_ttl_seconds=200000,
    ).to_plain_data()
    assert new_advice_old_history["trust_status"] == "EXPIRED_NOT_CONSUMABLE"


def test_g33_exact_redelivery_audit_and_supplied_validation(reference):
    first = _numerical_event(
        reference,
        49,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
        event_time=1049,
    )
    single = calibration.bounded_gt_event_fold_v01((first,), evaluated_at=1200)
    reconstructed = _equivalent_event(first)
    wrapper = _same_occurrence_wrapper(
        first,
        feedback_label="g33-redelivery-wrapper",
        causal_sequence=999,
    )
    repeated_folds = (
        (
            calibration.bounded_gt_event_fold_v01(
                (first, first), evaluated_at=1200
            ),
            (first, first),
        ),
        (
            calibration.bounded_gt_event_fold_v01(
                (first, reconstructed), evaluated_at=1200
            ),
            (first, reconstructed),
        ),
        (
            calibration.bounded_gt_event_fold_v01(
                (first, wrapper), evaluated_at=1200
            ),
            (first, wrapper),
        ),
    )
    stable_fields = (
        "accepted_occurrence_ids",
        "effective_sample_count",
        "sample_state",
        "rating_after_fp",
        "final_update_ref",
        "history_observation_anchor",
    )
    single_plain = single.to_plain_data()
    for repeated, events in repeated_folds:
        repeated_plain = repeated.to_plain_data()
        assert repeated.updates[0].canonical == single.updates[0].canonical
        assert {name: repeated_plain[name] for name in stable_fields} == {
            name: single_plain[name] for name in stable_fields
        }
        assert [row["disposition"] for row in repeated_plain["audit"]] == [
            "ACCEPTED",
            "DUPLICATE",
        ]
        assert not calibration.validate_calibration_against_sources_v01(
            repeated,
            events=events,
            fold_evaluated_at=1200,
        )
    exact_plain = repeated_folds[0][0].to_plain_data()
    assert exact_plain["ordered_event_refs"] == [
        single.updates[0].to_plain_data()["accepted_feedback_ref"],
        single.updates[0].to_plain_data()["accepted_feedback_ref"],
    ]

    second = _numerical_event(
        reference,
        50,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
        event_time=1049,
        causal_sequence=500,
    )
    interleaved = calibration.bounded_gt_event_fold_v01(
        (wrapper, second, first), evaluated_at=1200
    )
    distinct = calibration.bounded_gt_event_fold_v01(
        (first, second), evaluated_at=1200
    )
    assert [row["disposition"] for row in interleaved.to_plain_data()["audit"]] == [
        "ACCEPTED",
        "ACCEPTED",
        "DUPLICATE",
    ]
    assert interleaved.to_plain_data()["accepted_occurrence_ids"] == distinct.to_plain_data()[
        "accepted_occurrence_ids"
    ]
    assert tuple(item.canonical for item in interleaved.updates) == tuple(
        item.canonical for item in distinct.updates
    )

    no_update = _numerical_event(
        reference,
        48,
        expected_fp=None,
        observed_result_fp=None,
        proposal_assessment="NOT_SCORABLE",
        eligibility="NO_UPDATE",
        event_time=1048,
    )
    repeated_no_update = calibration.bounded_gt_event_fold_v01(
        (no_update, no_update), evaluated_at=1200
    )
    repeated_no_update_plain = repeated_no_update.to_plain_data()
    assert repeated_no_update_plain["effective_sample_count"] == 0
    assert repeated_no_update_plain["accepted_occurrence_ids"] == []
    assert repeated_no_update_plain["history_observation_anchor"] is None
    assert [row["disposition"] for row in repeated_no_update_plain["audit"]] == [
        "NO_UPDATE",
        "DUPLICATE",
    ]
    assert not calibration.validate_calibration_against_sources_v01(
        repeated_no_update,
        events=(no_update, no_update),
        fold_evaluated_at=1200,
    )

    changed = repeated_folds[0][0].to_plain_data()
    changed["rating_after_fp"] -= 1
    changed["fold_id"] = calibration._identity(
        "g3_gt_event_fold_v01",
        {key: item for key, item in changed.items() if key != "fold_id"},
    )
    forged = calibration.GTEventFoldV01(
        calibration._canonical(changed), repeated_folds[0][0].updates
    )
    assert calibration.validate_calibration_against_sources_v01(
        forged,
        events=(first, first),
        fold_evaluated_at=1200,
    ) == ("g33_fold_source_mismatch",)


def test_g33_delivery_batch_128_129_256_and_257_refusal(reference):
    base = _numerical_event(
        reference,
        1900,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
        event_time=2900,
    )
    for size in reference["delivery_batch_bounds"]["accepted_sizes"][:2]:
        events = (base,) * size
        fold = calibration.bounded_gt_event_fold_v01(events, evaluated_at=5000)
        plain = fold.to_plain_data()
        assert len(plain["ordered_event_refs"]) == size
        assert len(plain["audit"]) == size
        assert plain["effective_sample_count"] == 1
        assert [row["disposition"] for row in plain["audit"]].count("DUPLICATE") == size - 1
        assert not calibration.validate_calibration_against_sources_v01(
            fold, events=events, fold_evaluated_at=5000
        )

    unique = tuple(
        _numerical_event(
            reference,
            2000 + index,
            expected_fp=500000000,
            observed_result_fp=1000000000,
            proposal_assessment="CORRECT",
        )
        for index in range(calibration.MAX_EFFECTIVE_EVENTS)
    )
    sixty_fifth = _numerical_event(
        reference,
        2064,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    duplicates = tuple(
        _same_occurrence_wrapper(
            sixty_fifth,
            feedback_label=f"g33-cap-redelivery-{index}",
            causal_sequence=10000 + index,
        )
        for index in range(191)
    )
    full_batch = unique + (sixty_fifth,) + duplicates
    assert len(full_batch) == reference["delivery_batch_bounds"]["maximum_inputs"]
    unique_only = calibration.bounded_gt_event_fold_v01(unique, evaluated_at=5000)
    bounded = calibration.bounded_gt_event_fold_v01(full_batch, evaluated_at=5000)
    bounded_plain = bounded.to_plain_data()
    dispositions = [row["disposition"] for row in bounded_plain["audit"]]
    assert len(bounded_plain["ordered_event_refs"]) == len(full_batch) == 256
    assert len(bounded_plain["audit"]) == 256
    assert dispositions.count("ACCEPTED") == calibration.MAX_EFFECTIVE_EVENTS
    assert dispositions.count("CAP_REACHED") == 1
    assert dispositions.count("DUPLICATE") == 191
    assert bounded_plain["effective_sample_count"] == calibration.MAX_EFFECTIVE_EVENTS
    assert bounded_plain["accepted_occurrence_ids"] == unique_only.to_plain_data()[
        "accepted_occurrence_ids"
    ]
    assert bounded_plain["history_observation_anchor"] == unique_only.to_plain_data()[
        "history_observation_anchor"
    ]
    assert tuple(item.canonical for item in bounded.updates) == tuple(
        item.canonical for item in unique_only.updates
    )
    assert not calibration.validate_calibration_against_sources_v01(
        bounded, events=full_batch, fold_evaluated_at=5000
    )

    single_before = calibration.bounded_gt_event_fold_v01((base,), evaluated_at=5000)
    with pytest.raises(ValueError, match="g33_event_batch"):
        calibration.bounded_gt_event_fold_v01(
            (base,) * reference["delivery_batch_bounds"]["refused_size"],
            evaluated_at=5000,
        )
    single_after = calibration.bounded_gt_event_fold_v01((base,), evaluated_at=5000)
    assert single_after.canonical == single_before.canonical
    assert tuple(item.canonical for item in single_after.updates) == tuple(
        item.canonical for item in single_before.updates
    )


def test_g33_dedup_conflict_sparse_warm_cap_and_no_update_preservation(reference):
    first = _numerical_event(
        reference,
        51,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    duplicate = _numerical_event(
        reference,
        52,
        occurrence="occurrence:g33:51",
        feedback_label="g33-repackaged-51",
        event_time=1051,
        causal_sequence=999,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    # The proposal identity is part of occurrence value, so make this a true wrapper.
    duplicate_plain = calibration._decode(duplicate.canonical)
    first_plain = calibration._decode(first.canonical)
    duplicate_plain["original_occurrence"] = deepcopy(first_plain["original_occurrence"])
    duplicate_plain["original_occurrence_id"] = first_plain["original_occurrence_id"]
    duplicate_plain["pre_decision_expectation_ref"] = first_plain[
        "pre_decision_expectation_ref"
    ]
    duplicate_plain["event_id"] = calibration._identity(
        "g3_gt_numerical_event_v01",
        {k: v for k, v in duplicate_plain.items() if k != "event_id"},
    )
    duplicate = calibration.GTNumericalEventV01(calibration._canonical(duplicate_plain))
    accepted = calibration.bounded_gt_event_fold_v01((first,), evaluated_at=1200)
    repeated = calibration.bounded_gt_event_fold_v01(
        (first, duplicate), evaluated_at=1200
    )
    assert repeated.to_plain_data()["effective_sample_count"] == 1
    assert repeated.updates[-1].canonical == accepted.updates[-1].canonical
    no_update = _numerical_event(
        reference,
        53,
        expected_fp=None,
        observed_result_fp=None,
        proposal_assessment="NOT_SCORABLE",
        eligibility="NO_UPDATE",
    )
    standalone_no_update = calibration.evaluate_gt_trust_update_v01(
        no_update, evaluated_at=1200
    )
    assert standalone_no_update.to_plain_data()["update_disposition"] == "NO_UPDATE"
    assert not calibration.validate_calibration_against_sources_v01(
        standalone_no_update,
        events=(no_update,),
        fold_evaluated_at=1200,
    )
    preserved = calibration.bounded_gt_event_fold_v01(
        (first, no_update), evaluated_at=1200
    )
    assert preserved.updates[-1].canonical == accepted.updates[-1].canonical
    detached = accepted.updates[-1].to_plain_data()
    detached["rating_after_fp"] = 0
    assert accepted.updates[-1].to_plain_data()["rating_after_fp"] == 562500000
    conflict = _numerical_event(
        reference,
        54,
        occurrence="occurrence:g33:51",
        expected_fp=500000000,
        observed_result_fp=0,
        proposal_assessment="UNSAFE",
    )
    conflict_plain = calibration._decode(conflict.canonical)
    conflict_plain["original_occurrence"] = deepcopy(first_plain["original_occurrence"])
    conflict_plain["original_occurrence_id"] = first_plain["original_occurrence_id"]
    conflict_plain["event_id"] = calibration._identity(
        "g3_gt_numerical_event_v01",
        {k: v for k, v in conflict_plain.items() if k != "event_id"},
    )
    conflict = calibration.GTNumericalEventV01(calibration._canonical(conflict_plain))
    with pytest.raises(ValueError, match="g33_occurrence_conflict"):
        calibration.bounded_gt_event_fold_v01((first, conflict), evaluated_at=1200)
    three = tuple(
        _numerical_event(
            reference,
            60 + index,
            expected_fp=500000000,
            observed_result_fp=1000000000,
            proposal_assessment="CORRECT",
        )
        for index in range(3)
    )
    assert calibration.bounded_gt_event_fold_v01(
        three[:2], evaluated_at=1300
    ).to_plain_data()["sample_state"] == "SPARSE"
    assert calibration.bounded_gt_event_fold_v01(
        three, evaluated_at=1300
    ).to_plain_data()["sample_state"] == "WARM"
    cap = reference["cap_series"]
    sixty_five = tuple(
        _numerical_event(
            reference,
            1000 + index,
            occurrence=cap["occurrence_format"].format(index=index),
            feedback_label=cap["feedback_seed_format"].format(index=index),
            event_time=cap["first_event_time"] + index,
            expected_fp=cap["expected_fp"],
            observed_result_fp=cap["observed_result_fp"],
            proposal_assessment=cap["proposal_assessment"],
        )
        for index in range(cap["event_count"])
    )
    capped = calibration.bounded_gt_event_fold_v01(
        sixty_five, evaluated_at=3000
    )
    assert capped.to_plain_data()["effective_sample_count"] == 64
    assert capped.to_plain_data()["fold_disposition"] == "CAP_REACHED"
    assert capped.to_plain_data()["audit"][-1]["disposition"] == "CAP_REACHED"


def test_g33_subject_lane_and_bad_scalar_controls(reference):
    good = _numerical_event(
        reference,
        71,
        expected_fp=500000000,
        observed_result_fp=1000000000,
        proposal_assessment="CORRECT",
    )
    for offset, field in enumerate(reference["subject_key"], start=72):
        changed_subject = deepcopy(reference["subject_key"])
        changed_subject[field] = changed_subject[field] + ":other"
        other = _numerical_event(
            reference,
            offset,
            subject=changed_subject,
            expected_fp=500000000,
            observed_result_fp=1000000000,
            proposal_assessment="CORRECT",
        )
        with pytest.raises(ValueError, match="g33_subject_stream_mismatch"):
            calibration.bounded_gt_event_fold_v01((good, other), evaluated_at=1300)
    with pytest.raises(ValueError, match="g33_integer"):
        _numerical_event(
            reference,
            73,
            expected_fp=True,
            observed_result_fp=1000000000,
            proposal_assessment="CORRECT",
        )
    with pytest.raises(ValueError):
        _numerical_event(
            reference,
            74,
            expected_fp=0.5,
            observed_result_fp=1000000000,
            proposal_assessment="CORRECT",
        )
    with pytest.raises(ValueError, match="g33_rational"):
        calibration.round_half_even_rational_v01(1, 0)
    changed_profile = calibration._decode(good.canonical)
    changed_profile["profile_id"] = "G3_FOREIGN_PROFILE"
    changed_profile["event_id"] = calibration._identity(
        "g3_gt_numerical_event_v01",
        {k: v for k, v in changed_profile.items() if k != "event_id"},
    )
    with pytest.raises(ValueError, match="g33_invalid_input"):
        calibration.GTNumericalEventV01(calibration._canonical(changed_profile))


def _reference_event(name="lawful_a"):
    corpus = json.loads((ROOT / "fixtures/gate3_reference_v01.json").read_bytes())
    source = corpus["reference_sources"][name]
    observation = feedback.build_outcome_observation_v01(
        source_bundle=source,
        profile=feedback.SOURCE_PROFILE_ID,
        explicit_times=corpus["explicit_times"],
    )
    value = feedback.build_outcome_feedback_v01(
        observation=observation,
        source_bundle=source,
        profile=feedback.SOURCE_PROFILE_ID,
    )
    return corpus, source, value, calibration.bind_outcome_feedback_event_v01(
        value, source_bundle=source, profile=feedback.SOURCE_PROFILE_ID
    )


def test_g33_reference_source_validation_dedup_and_derived_poisoning():
    corpus, source, value, event = _reference_event()
    _, _, _, wrapper = _reference_event("label_only")
    fold = calibration.bounded_gt_event_fold_v01(
        (event, wrapper), evaluated_at=corpus["explicit_times"]["timestamp"]
    )
    assert fold.to_plain_data()["effective_sample_count"] == 1
    assert fold.to_plain_data()["evidence_class"] == feedback.REFERENCE_CLASS
    equivalent = calibration.SourceBoundGTEventV01(
        bytes(event.feedback_canonical), bytes(event.source_canonical), event.source_profile_id
    )
    assert calibration.bounded_gt_event_fold_v01(
        (equivalent,), evaluated_at=corpus["explicit_times"]["timestamp"]
    ).canonical == calibration.bounded_gt_event_fold_v01(
        (event,), evaluated_at=corpus["explicit_times"]["timestamp"]
    ).canonical
    poisoned_source = deepcopy(source)
    poisoned_source["expectation"]["expected_fp"] = 0
    with pytest.raises(ValueError, match="g31_source_not_admitted"):
        calibration.bind_outcome_feedback_event_v01(
            value, source_bundle=poisoned_source, profile=feedback.SOURCE_PROFILE_ID
        )
    changed = fold.to_plain_data()
    changed["rating_after_fp"] -= 1
    changed["fold_id"] = calibration._identity(
        "g3_gt_event_fold_v01", {k: v for k, v in changed.items() if k != "fold_id"}
    )
    forged = calibration.GTEventFoldV01(calibration._canonical(changed), fold.updates)
    assert calibration.validate_calibration_against_sources_v01(
        forged,
        events=(event, wrapper),
        fold_evaluated_at=corpus["explicit_times"]["timestamp"],
    ) == ("g33_fold_source_mismatch",)
    reference_plain = calibration._plain_event(event)
    numerical_plain = deepcopy(reference_plain)
    numerical_plain["evidence_class"] = calibration.NUMERICAL_EVIDENCE_CLASS
    numerical_plain["source_profile_id"] = "G33_DECLARED_NUMERICAL_REFERENCE_V01"
    numerical_plain["event_id"] = calibration._identity(
        "g3_gt_numerical_event_v01",
        {k: v for k, v in numerical_plain.items() if k != "event_id"},
    )
    numerical = calibration.GTNumericalEventV01(
        calibration._canonical(numerical_plain)
    )
    with pytest.raises(ValueError, match="g33_evidence_lane_mismatch"):
        calibration.bounded_gt_event_fold_v01(
            (event, numerical), evaluated_at=corpus["explicit_times"]["timestamp"]
        )


def test_g33_two_processes_emit_identical_numerical_bytes():
    source = """
import hashlib,json
from hedgehog import outcome_calibration_v01 as c
f=json.load(open('fixtures/gate3_calibration_reference_v01.json'));s=f['subject_key'];w=f['advice_window']
e=c.build_numerical_reference_event_v01(subject_key=s,original_occurrence={'local_root_scope_id':s['local_root_scope_id'],'domain_scope_id':s['domain_scope_id'],'producer_occurrence_ref':'occurrence:process','proposal_ref':'proposal:process','purpose':s['advice_claim_profile_id']},feedback_id=hashlib.sha256(b'g33-process').hexdigest(),event_time=1001,causal_sequence=1,expected_fp=500000000,observed_result_fp=1000000000,proposal_assessment='CORRECT',enforcement_outcome='ALLOWED_AS_REQUIRED',update_eligibility='ELIGIBLE',pre_decision_expectation_ref='expectation:process',advice_ref=w['advice_ref'],advice_created_at=w['advice_created_at'],advice_valid_from=w['advice_valid_from'],advice_valid_to=w['advice_valid_to'],advice_ttl_seconds=w['advice_ttl_seconds'],regret_status='UNKNOWN',regret_norm_fp=None,regret_source_ref='NO_COUNTERFACTUAL',safety_status='NOT_VERIFIED_UNSAFE',producer_source_closure_ref='fixture:gate3_calibration_reference_v01',source_refs=('source:process',))
print(c.bounded_gt_event_fold_v01((e,),evaluated_at=1001).canonical.decode())
"""
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(ROOT))
    outputs = [
        subprocess.check_output(
            (sys.executable, "-B", "-c", source), cwd=ROOT, env=environment
        )
        for _ in range(2)
    ]
    assert outputs[0] == outputs[1]


@pytest.fixture(scope="module")
def native_calibration(tmp_path_factory):
    directory = (
        Path(os.environ["G33_EVIDENCE"])
        / "commands"
        / os.environ.get("G33_COMMAND", "native_calibration")
        / "native"
        if "G33_EVIDENCE" in os.environ
        else tmp_path_factory.mktemp("g33_native") / "native"
    )
    directory.mkdir(parents=True, exist_ok=False)
    fixture = json.loads((ROOT / "fixtures/landslide_sentinel/ls1_inputs_v01.json").read_bytes())
    spec = json.loads((ROOT / "fixtures/gate3_sentinel_observation_v01.json").read_bytes())
    session = ControlledEpisode(directory / "episode", fixture)
    session.ingest(
        [
            sentinel_events.observation(row["sensor"], row["value"], 120, 1)
            for row in fixture["frames"]
        ],
        120,
    )
    store = SentinelOutcomeSourceV01(session)

    def semantic():
        return sentinel_semantics.collect(
            session.frames,
            fixture["maintenance_note"],
            session.root,
            session.source.sample().evaluation_time,
            controlled=spec["response"],
            intended_role=spec["role"],
            capabilities=session.capabilities.snapshot(spec["role"]),
            observations=tuple(session.book.latest.values()),
            tick=session.tick,
            policy=session.contract,
        )[1]

    healthy = store.observe_role_v01(semantic(), expected_fp=calibration.Q // 2)
    missing = store.observe_role_v01(semantic(), expected_fp=None)
    healthy_observation, healthy_feedback = store.build_feedback_v01(healthy)
    missing_observation, missing_feedback = store.build_feedback_v01(missing)
    assert not store.validate_feedback_v01(healthy_feedback, capture=healthy)
    assert not store.validate_feedback_v01(missing_feedback, capture=missing)
    healthy_source = store.validate_capture_v01(healthy)
    missing_source = store.validate_capture_v01(missing)
    reads_before = session.source.reads
    event = calibration.bind_outcome_feedback_event_v01(
        healthy_feedback,
        source_bundle=healthy_source,
        profile=feedback.NATIVE_SOURCE_PROFILE_ID,
    )
    missing_event = calibration.bind_outcome_feedback_event_v01(
        missing_feedback,
        source_bundle=missing_source,
        profile=feedback.NATIVE_SOURCE_PROFILE_ID,
    )
    evaluated = feedback.outcome_feedback_to_plain_data_v01(healthy_feedback)["timestamp"]
    fold = calibration.bounded_gt_event_fold_v01(
        (event, missing_event), evaluated_at=evaluated
    )

    for label, capture, source, observation in (
        ("healthy", healthy, healthy_source, healthy_observation),
        ("missing", missing, missing_source, missing_observation),
    ):
        native = json.loads(capture.native_canonical)
        prospective_path = (
            directory / "episode" / f"g32_prospective_{capture.ordinal}.json"
        )
        assert prospective_path.is_file()
        (directory / f"{label}_prospective_claim_input.json").write_bytes(
            prospective_path.read_bytes()
        )
        (directory / f"{label}_native_capture.json").write_bytes(
            capture.native_canonical
        )
        (directory / f"{label}_source_canonical.json").write_bytes(
            source.canonical
        )
        (directory / f"{label}_normalized_observation.json").write_bytes(
            observation.canonical
        )
        (directory / f"{label}_capture_descriptor.json").write_bytes(
            feedback._canonical(
                {
                    "capture_id": capture.capture_id,
                    "ordinal": capture.ordinal,
                    "native_sha256": hashlib.sha256(capture.native_canonical).hexdigest(),
                    "source_sha256": hashlib.sha256(capture.source_canonical).hexdigest(),
                    "origin": "RUNTIME_ONLY_NOT_SERIALIZED",
                }
            )
        )
    (directory / "healthy_bound_event.json").write_bytes(event.feedback_canonical)
    (directory / "missing_bound_event.json").write_bytes(missing_event.feedback_canonical)
    for name, value in (
        ("healthy_feedback.json", feedback.outcome_feedback_to_plain_data_v01(healthy_feedback)),
        ("missing_feedback.json", feedback.outcome_feedback_to_plain_data_v01(missing_feedback)),
        ("gt_update.json", fold.updates[-1].to_plain_data()),
        ("gt_fold.json", fold.to_plain_data()),
    ):
        (directory / name).write_bytes(feedback._canonical(value) + b"\n")
    yield {
        "directory": directory,
        "session": session,
        "store": store,
        "healthy": healthy,
        "healthy_feedback": healthy_feedback,
        "healthy_source": healthy_source,
        "event": event,
        "missing_event": missing_event,
        "fold": fold,
        "evaluated_at": evaluated,
        "reads_before": reads_before,
    }
    assert not session.executed
    (directory / "finalizer.json").write_text(
        json.dumps(
            {
                "complete": True,
                "effect_executions": len(session.executed),
                "provider_calls": 0,
                "role_attempts": 2,
                "native_captures": 2,
                "normalized_observations": 2,
                "source_reads": session.source.reads,
                "full_D_E": "NOT_RUN",
            },
            sort_keys=True,
        )
        + "\n"
    )


def test_g33_native_sentinel_source_to_feedback_to_numerical_consumer(native_calibration):
    value = native_calibration
    fold = value["fold"]
    update = fold.updates[-1].to_plain_data()
    supplied = feedback.outcome_feedback_to_plain_data_v01(value["healthy_feedback"])
    assert update["rating_before_fp"] == calibration.Q // 2
    assert update["expected_fp"] == calibration.Q // 2
    assert update["observed_result_fp"] == calibration.Q
    assert update["rating_after_fp"] == 562500000
    assert update["half_life_seconds"] == 45900
    assert update["effective_sample_count"] == 1
    assert update["sample_state"] == "SPARSE"
    assert update["accepted_feedback_ref"] == supplied["feedback_id"]
    assert update["producer_source_closure_ref"] == supplied["source_closure_ref"]
    assert supplied["pre_decision_expectation"]["evidence_refs"][0] == update[
        "pre_decision_expectation_ref"
    ]
    assert fold.to_plain_data()["audit"][-1]["disposition"] == "NO_UPDATE"
    assert not calibration.validate_calibration_against_sources_v01(
        fold,
        events=(value["event"], value["missing_event"]),
        fold_evaluated_at=value["evaluated_at"],
    )
    assert value["session"].source.reads == value["reads_before"]
    assert not value["session"].executed
    redelivery = calibration.bounded_gt_event_fold_v01(
        (value["event"], value["event"], value["missing_event"], value["missing_event"]),
        evaluated_at=value["evaluated_at"],
    )
    assert [row["disposition"] for row in redelivery.to_plain_data()["audit"]] == [
        "ACCEPTED",
        "DUPLICATE",
        "NO_UPDATE",
        "DUPLICATE",
    ]
    assert redelivery.updates[-1].canonical == fold.updates[-1].canonical
    assert not calibration.validate_calibration_against_sources_v01(
        redelivery,
        events=(
            value["event"],
            value["event"],
            value["missing_event"],
            value["missing_event"],
        ),
        fold_evaluated_at=value["evaluated_at"],
    )


def test_g33_native_equivalent_value_poison_and_time_validation(native_calibration):
    value = native_calibration
    equivalent = calibration.SourceBoundGTEventV01(
        bytes(value["event"].feedback_canonical),
        bytes(value["event"].source_canonical),
        value["event"].source_profile_id,
    )
    positive = calibration.bounded_gt_event_fold_v01(
        (equivalent,), evaluated_at=value["evaluated_at"]
    )
    assert positive.updates[-1].canonical == value["fold"].updates[-1].canonical
    changed = value["fold"].updates[-1].to_plain_data()
    changed["rating_after_fp"] -= 1
    changed["update_id"] = calibration._identity(
        "g3_gt_trust_update_v01", {k: v for k, v in changed.items() if k != "update_id"}
    )
    forged = calibration.GTTrustUpdateV01(calibration._canonical(changed))
    assert calibration.validate_calibration_against_sources_v01(
        forged,
        events=(value["event"], value["missing_event"]),
        fold_evaluated_at=value["evaluated_at"],
    ) == ("g33_update_source_mismatch",)
    current = calibration.evaluate_gt_trust_at_v01(
        positive.updates[-1], evaluation_time=value["evaluated_at"]
    )
    assert not calibration.validate_calibration_against_sources_v01(
        current,
        events=(equivalent,),
        fold_evaluated_at=value["evaluated_at"],
        evaluation_time=value["evaluated_at"],
    )
    detached = current.to_plain_data()
    detached["review_pressure_fp"] = 0
    assert current.to_plain_data()["review_pressure_fp"] != 0
    supplied = feedback.outcome_feedback_to_plain_data_v01(value["healthy_feedback"])
    supplied["advisory_subject_key"]["policy_semantics_version"] = "coherent:foreign"
    supplied["feedback_id"] = feedback._identity(
        "g3_feedback_v01", {k: v for k, v in supplied.items() if k != "feedback_id"}
    )
    poisoned = feedback.parse_outcome_feedback_json_v01(feedback._canonical(supplied))
    with pytest.raises(ValueError, match="g31_feedback_source_mismatch"):
        calibration.bind_outcome_feedback_event_v01(
            poisoned,
            source_bundle=value["healthy_source"],
            profile=feedback.NATIVE_SOURCE_PROFILE_ID,
        )
    changed_source = json.loads(value["healthy"].source_canonical)
    changed_source["expectation"]["expected_fp"] = calibration.Q
    assert value["store"].validate_feedback_v01(
        value["healthy_feedback"],
        capture=value["healthy"],
        supplied_source=changed_source,
    ) == ("g32_supplied_source_changed",)
    assert value["session"].source.reads == value["reads_before"]
    assert not value["session"].executed
