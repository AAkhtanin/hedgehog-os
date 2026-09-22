#!/usr/bin/env python3
"""Validate retained G37 successors without invoking any collector."""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import demo.run_continuous_delta_runtime_g2_e_v01 as e5_demo
import demo.run_kernel_conformance_v01 as conformance_demo
import demo.run_living_gauntlet_v01 as living_demo
import hedgehog.gate3_mechanism_v01 as gate3
from hedgehog.kernel import conformance_v01 as conformance
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import root_decision_v01 as root_decision
from hedgehog.kernel import work_composition_v01 as work_composition
import hedgehog.outcome_feedback_history_v01 as outcome_history
import hedgehog.work_execution_host_v01 as work_host


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _text_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or any(type(item) is not str for item in value):
        raise TypeError("expected text list")
    return tuple(value)


def _decode_category(value: dict[str, object]):
    return conformance.ConformanceCategoryResultV01(
        result_id=value["result_id"],
        category_id=value["category_id"],
        required_check_ids=_text_tuple(value["required_check_ids"]),
        passed_check_ids=_text_tuple(value["passed_check_ids"]),
        failed_check_ids=_text_tuple(value["failed_check_ids"]),
        evidence_refs=_text_tuple(value["evidence_refs"]),
        limitation_refs=_text_tuple(value["limitation_refs"]),
        status=value["status"],
        real_world_effects_count=value["real_world_effects_count"],
    )


def _decode_domain(value: dict[str, object]):
    return conformance.DomainConformanceResultV01(
        result_id=value["result_id"],
        domain_id=value["domain_id"],
        adapter_ref=value["adapter_ref"],
        source_ref=value["source_ref"],
        required_check_ids=_text_tuple(value["required_check_ids"]),
        passed_check_ids=_text_tuple(value["passed_check_ids"]),
        failed_check_ids=_text_tuple(value["failed_check_ids"]),
        evidence_refs=_text_tuple(value["evidence_refs"]),
        limitation_refs=_text_tuple(value["limitation_refs"]),
        provider_call_count=value["provider_call_count"],
        network_call_count=value["network_call_count"],
        gemini_call_count=value["gemini_call_count"],
        real_world_effects_count=value["real_world_effects_count"],
        status=value["status"],
    )


def _decode_negative(value: dict[str, object]):
    return conformance.NegativeConformanceResultV01(
        result_id=value["result_id"],
        probe_id=value["probe_id"],
        target_contract=value["target_contract"],
        expected_reason_codes=_text_tuple(value["expected_reason_codes"]),
        observed_reason_codes=_text_tuple(value["observed_reason_codes"]),
        blocked=value["blocked"],
        evidence_refs=_text_tuple(value["evidence_refs"]),
        status=value["status"],
        real_world_effects_count=value["real_world_effects_count"],
    )


def _decode_conformance(value: dict[str, object]):
    counters = conformance.ConformanceCountersV01(**value["counters"])
    raw_claim_map = value["claim_to_current_act"]
    if (
        not isinstance(raw_claim_map, list)
        or any(not isinstance(item, list) or len(item) != 2 for item in raw_claim_map)
    ):
        raise TypeError("expected serialized claim-to-act pairs")
    claim_map = tuple(
        (claim_id, _text_tuple(act_ids)) for claim_id, act_ids in raw_claim_map
    )
    return conformance.KernelConformanceReportV01(
        report_id=value["report_id"],
        profile_id=value["profile_id"],
        conformance_version=value["conformance_version"],
        historical_profile_ref=value["historical_profile_ref"],
        claim_to_current_act=claim_map,
        current_act_count=value["current_act_count"],
        implementation_commit=value["implementation_commit"],
        category_results=tuple(_decode_category(item) for item in value["category_results"]),
        domain_results=tuple(_decode_domain(item) for item in value["domain_results"]),
        negative_test_results=tuple(
            _decode_negative(item) for item in value["negative_test_results"]
        ),
        active_gauntlet_refs=_text_tuple(value["active_gauntlet_refs"]),
        continuous_delta_runtime_execution_count=value[
            "continuous_delta_runtime_execution_count"
        ],
        continuous_delta_runtime_public_validation_status=value[
            "continuous_delta_runtime_public_validation_status"
        ],
        continuous_delta_runtime_report_sha256=value[
            "continuous_delta_runtime_report_sha256"
        ],
        continuous_delta_runtime_report_bytes=value[
            "continuous_delta_runtime_report_bytes"
        ],
        shared_conformance_e5_collector_calls=value[
            "shared_conformance_e5_collector_calls"
        ],
        shared_conformance_e5_report_sha256=value[
            "shared_conformance_e5_report_sha256"
        ],
        shared_conformance_e5_report_bytes=value[
            "shared_conformance_e5_report_bytes"
        ],
        continuous_delta_runtime_second_execution_count=value[
            "continuous_delta_runtime_second_execution_count"
        ],
        continuous_delta_runtime_cache_reuse_count=value[
            "continuous_delta_runtime_cache_reuse_count"
        ],
        continuous_delta_runtime_test_fixture_substitution_count=value[
            "continuous_delta_runtime_test_fixture_substitution_count"
        ],
        continuous_delta_runtime_private_g2d_calls=value[
            "continuous_delta_runtime_private_g2d_calls"
        ],
        continuous_delta_runtime_reconstructed_case_count=value[
            "continuous_delta_runtime_reconstructed_case_count"
        ],
        evidence_refs=_text_tuple(value["evidence_refs"]),
        limitations=_text_tuple(value["limitations"]),
        counters=counters,
        final_status=value["final_status"],
    )


class _CallMonitor:
    def __init__(self) -> None:
        self.tool_id = 5
        self.counts: dict[str, int] = {}
        functions = {
            "collector.living_successor": living_demo.collect_living_g36_v01,
            "collector.living_legacy": living_demo.collect_living_gauntlet_v01,
            "collector.conformance_successor": conformance_demo.collect_kernel_conformance_g36_v01,
            "collector.conformance_legacy": conformance_demo.collect_standalone_kernel_conformance_v01,
            "collector.gate3": gate3.collect_mechanism_v01,
            "collector.e5": e5_demo.collect_continuous_delta_runtime_g2_e_v01,
            "host.dispatch_current_action": work_host.dispatch_current_action_v01,
            "host.capture_current_source": work_host.capture_current_action_source_v01,
            "host.execute_admitted_work": work_host.execute_admitted_pure_work_v01,
            "root.decide": root_decision.decide_root_v01,
            "work.execute_review": work_composition.execute_work_task_review_v01,
            "history.review_recording": outcome_history.review_outcome_recording_v01,
            "effect.authorize": firewall.authorize_effect_request_v01,
            "effect.execute_mock": firewall.execute_mock_effect_v01,
            "effect.execute_bound": firewall.execute_bound_effect_v01,
        }
        self.functions = functions
        self.by_code = {function.__code__: name for name, function in functions.items()}

    def __enter__(self):
        sys.monitoring.use_tool_id(self.tool_id, "g37r-supplied-validation")
        sys.monitoring.register_callback(
            self.tool_id, sys.monitoring.events.PY_START, self._on_start
        )
        for code in self.by_code:
            sys.monitoring.set_local_events(
                self.tool_id, code, sys.monitoring.events.PY_START
            )
        return self

    def _on_start(self, code, instruction_offset):
        del instruction_offset
        name = self.by_code[code]
        self.counts[name] = self.counts.get(name, 0) + 1

    def __exit__(self, exc_type, exc, traceback):
        del exc_type, exc, traceback
        for code in self.by_code:
            sys.monitoring.set_local_events(
                self.tool_id, code, sys.monitoring.events.NO_EVENTS
            )
        sys.monitoring.register_callback(
            self.tool_id, sys.monitoring.events.PY_START, None
        )
        sys.monitoring.free_tool_id(self.tool_id)
        for name in self.functions:
            self.counts.setdefault(name, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--living", type=Path, required=True)
    parser.add_argument("--conformance", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    living_bytes = args.living.read_bytes()
    conformance_bytes = args.conformance.read_bytes()
    if _sha256(living_bytes) != "d84cdd50e918c36f06ea60d0c3d4154760438d7cbcd4cd9124dc9f2745bfdc08":
        raise SystemExit("retained Living identity mismatch")
    if _sha256(conformance_bytes) != "e7983c25d588878f8f535c5037bbddd519672241d6e004361188e3ff2f682b66":
        raise SystemExit("retained Conformance identity mismatch")

    living_value = json.loads(living_bytes)
    conformance_value = json.loads(conformance_bytes)
    current_registration, registration_errors = living_demo._current_registration_v01(
        args.candidate
    )
    if registration_errors or current_registration is None:
        raise SystemExit(f"current registration invalid: {registration_errors!r}")

    derived_living = deepcopy(living_value)
    prior_registration = derived_living["legacy"]["current_registration"]
    derived_living["legacy"]["current_registration"] = current_registration
    if {
        key: value
        for key, value in derived_living["legacy"].items()
        if key != "current_registration"
    } != {
        key: value
        for key, value in living_value["legacy"].items()
        if key != "current_registration"
    }:
        raise SystemExit("Living projection changed non-registration material")
    if {key: value for key, value in derived_living.items() if key != "legacy"} != {
        key: value for key, value in living_value.items() if key != "legacy"
    }:
        raise SystemExit("Living projection changed successor material")

    decoded = _decode_conformance(conformance_value["legacy"])
    projected_conformance_plain = deepcopy(conformance_value["legacy"])
    projected_conformance_plain["claim_to_current_act"] = {
        claim_id: act_ids
        for claim_id, act_ids in projected_conformance_plain["claim_to_current_act"]
    }
    if (
        conformance.kernel_conformance_report_to_plain_dict_v01(decoded)
        != projected_conformance_plain
    ):
        raise SystemExit("Conformance typed decode does not round trip")
    supplied_conformance = dict(conformance_value)
    supplied_conformance["legacy"] = decoded

    with _CallMonitor() as monitor:
        living_positive = living_demo.validate_living_g36_v01(derived_living)
        conformance_positive = conformance_demo.validate_kernel_conformance_g36_v01(
            supplied_conformance
        )

        bad_living_registration = deepcopy(derived_living)
        bad_living_registration["legacy"]["current_registration"]["base_identities"][
            "release/completion_manifest.json"
        ] = "0" * 64
        living_registration_negative = living_demo.validate_living_g36_v01(
            bad_living_registration
        )
        bad_living_binding = deepcopy(derived_living)
        bad_living_binding["gate3"]["checked_count"] += 1
        living_binding_negative = living_demo.validate_living_g36_v01(
            bad_living_binding
        )

        bad_report = replace(decoded, report_id="0" * 64)
        bad_conformance_identity = dict(supplied_conformance)
        bad_conformance_identity["legacy"] = bad_report
        conformance_identity_negative = (
            conformance_demo.validate_kernel_conformance_g36_v01(
                bad_conformance_identity
            )
        )
        bad_conformance_binding = deepcopy(conformance_value)
        bad_conformance_binding["legacy"] = decoded
        bad_conformance_binding["gate3"]["checked_count"] += 1
        conformance_binding_negative = (
            conformance_demo.validate_kernel_conformance_g36_v01(
                bad_conformance_binding
            )
        )

    if living_positive or conformance_positive:
        raise SystemExit(
            f"positive supplied validation failed: {living_positive!r} {conformance_positive!r}"
        )
    negatives = {
        "living_registration": list(living_registration_negative),
        "living_binding": list(living_binding_negative),
        "conformance_identity": list(conformance_identity_negative),
        "conformance_binding": list(conformance_binding_negative),
    }
    if any(not reasons for reasons in negatives.values()):
        raise SystemExit(f"negative control accepted: {negatives!r}")
    if any(monitor.counts.values()):
        raise SystemExit(f"forbidden operation observed: {monitor.counts!r}")

    derived_bytes = _canonical(derived_living)
    (args.output / "living_metadata_rebound_successor.json").write_bytes(derived_bytes)
    result = {
        "conformance": {
            "decode_projection": (
                "GENERIC_LIST_PAIRS_TO_TYPED_TUPLES; PUBLIC_PLAIN_MAPPING"
            ),
            "input_bytes": len(conformance_bytes),
            "input_sha256": _sha256(conformance_bytes),
            "legacy_plain_round_trip": "BYTE_VALUE_IDENTICAL",
            "public_supplied_validation": "PASS",
        },
        "forbidden_operation_counts": monitor.counts,
        "living": {
            "derived_bytes": len(derived_bytes),
            "derived_sha256": _sha256(derived_bytes),
            "input_bytes": len(living_bytes),
            "input_sha256": _sha256(living_bytes),
            "prior_base_identities": prior_registration["base_identities"],
            "projected_base_identities": current_registration["base_identities"],
            "projection": ["legacy.current_registration"],
            "public_supplied_validation": "PASS",
        },
        "negative_controls": negatives,
        "provider_calls": 0,
        "real_effects": 0,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
