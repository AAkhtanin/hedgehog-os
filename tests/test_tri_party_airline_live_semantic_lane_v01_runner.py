from __future__ import annotations

import ast
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

import pytest

from demo import run_tri_party_airline_live_semantic_lane_v01 as runner
from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    semantic_to_contract_causal_runtime_v01 as causal_runtime,
)


def _enabled_env(tmp_path: Path | None = None) -> dict[str, str]:
    return _fake_env(tmp_path)


def _fake_env(tmp_path: Path | None = None) -> dict[str, str]:
    env = {
        runner.ENV_LANE: "1",
        runner.ENV_FAKE_PROVIDER: "1",
    }
    if tmp_path is not None:
        env[runner.ENV_ARTIFACT_DIR] = str(tmp_path)
    return env


def _causal_env(tmp_path: Path | None = None) -> dict[str, str]:
    env = _fake_env(tmp_path)
    env[runner.ENV_CAUSAL_BINDING] = "1"
    return env


def _crypto_env(tmp_path: Path) -> dict[str, str]:
    env = _causal_env(tmp_path)
    env[runner.ENV_CRYPTO_ARTIFACT_SEAL] = "1"
    return env


def _real_env(tmp_path: Path | None = None) -> dict[str, str]:
    env = {
        runner.ENV_LANE: "1",
        runner.ENV_REAL_PROVIDER: "1",
    }
    if tmp_path is not None:
        env[runner.ENV_ARTIFACT_DIR] = str(tmp_path)
    return env


def _report(tmp_path: Path | None = None) -> dict[str, Any]:
    return runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(tmp_path),
    )


def _mutating_provider(
    actor_id_to_mutate: str,
    updates: Mapping[str, Any],
) -> runner.Provider:
    fake = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        raw = fake(actor_id, prompt, metadata)
        if actor_id != actor_id_to_mutate:
            return raw
        payload = json.loads(raw)
        payload.update(updates)
        return json.dumps(payload, sort_keys=True)

    return provider


def _real_provider() -> runner.Provider:
    return runner.build_fake_airline_semantic_provider_v01()


def _proposal_payload(request: Mapping[str, Any], offer_id: str) -> dict[str, Any]:
    return {
        "proposal_id": f"semantic_offer_selection_proposal:{offer_id}",
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_bsep_projection_ref": request["source_bsep_projection_ref"],
        "source_client_constraint_set_id": request["source_client_constraint_set_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "candidate_set_ref": request["source_candidate_set_ref"],
        "recommended_offer_id": offer_id,
        "ranked_offer_ids": (offer_id,),
        "decision_factors": ("test_live_lane_semantic_tradeoff",),
        "preference_matches": ("test_soft_preference_match",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Test-only causal proposal.",
        "authority_created": False,
        "action_permission_created": False,
        "packet_created": False,
        "receipt_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "real_world_effects_count": 0,
    }


def _reviewer_payload(
    request: Mapping[str, Any],
    *,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "response_id": (
            f"canonical_actor_output:{request['actor_id']}:"
            f"{request['proposed_offer_id']}"
        ),
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_request_id": request["request_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "reviewed_offer_id": request["proposed_offer_id"],
        "review_role": request["actor_role"],
        "review_status": binding.STATUS_PASS,
        "semantic_factors": ("test_reviewer_supports_offer",),
        "blocking_conflicts": (),
        "supports_proposed_offer": True,
        "validation_status": binding.STATUS_PASS,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }
    if overrides:
        payload.update(overrides)
    return payload


def _content_sensitive_causal_provider() -> runner.Provider:
    generic = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if not isinstance(request, Mapping):
            return generic(actor_id, prompt, metadata)
        if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            soft = request["client_soft_preferences"]
            priority = tuple(soft["soft_preference_priority"])
            seat = tuple(soft["preferred_seat_characteristics"])
            offer_id = (
                binding.OFFER_B_ID
                if "extra_legroom_aisle" in priority or "extra_legroom" in seat
                else binding.OFFER_A_ID
            )
            return json.dumps(_proposal_payload(request, offer_id), sort_keys=True)
        return json.dumps(_reviewer_payload(request), sort_keys=True)

    return provider


def _causal_report_for_preference(
    constraints: binding.ClientRootTravelConstraintSetV01,
    tmp_path: Path | None = None,
    provider: runner.Provider | None = None,
) -> dict[str, Any]:
    return runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_causal_env(tmp_path),
        provider=provider or _content_sensitive_causal_provider(),
        causal_constraints=constraints,
    )


def _crypto_report_for_preference(
    constraints: binding.ClientRootTravelConstraintSetV01,
    tmp_path: Path,
) -> dict[str, Any]:
    return runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_crypto_env(tmp_path),
        provider=_content_sensitive_causal_provider(),
        causal_constraints=constraints,
    )


def _schema_fixture(
    *,
    actor_id: str = binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER,
    proposed_offer_id: str = "",
) -> tuple[
    binding.AirlineSemanticSelectionInputV01,
    causal_runtime.AirlineInjectedSemanticActorRequestV01,
]:
    bsep = binding.build_valid_airline_bsep_projection_ref_v01()
    constraints = binding.build_client_constraints_preference_a_v01()
    snapshot = binding.build_airline_candidate_snapshot_v01()
    selection_input = binding.build_selection_input_v01(
        bsep,
        constraints,
        snapshot,
    )
    request = causal_runtime.build_airline_semantic_actor_request_v01(
        actor_id=actor_id,
        selection_input=selection_input,
        constraints=constraints,
        snapshot=snapshot,
        proposed_offer_id=proposed_offer_id,
    )
    return selection_input, request


def _minimal_safe_provider(*, include_empty_runtime_fields: bool = False) -> runner.Provider:
    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        actor = runner._actor_spec(actor_id)
        payload: dict[str, Any] = {
            "actor_id": actor_id,
            "transaction_id": runner.TRANSACTION_ID,
            "side": actor["side"],
            "semantic_summary": (
                f"Safe real-Gemini-like semantic summary for {actor_id}; "
                "advisory bounded airline semantic evidence only."
            ),
            "authority_created": False,
            "action_permission_created": False,
            "packet_created": False,
            "receipt_created": False,
            "payment_created": False,
            "ticket_created": False,
            "booking_created": False,
            "final_output_created": False,
            "real_payment_executed": False,
            "real_ticket_issued": False,
            "real_booking_created": False,
            "real_world_effects_count": 0,
        }
        if include_empty_runtime_fields:
            payload["what_runtime_used"] = []
            payload["what_runtime_rejected"] = []
        return json.dumps(payload, sort_keys=True)

    return provider


def test_airline_live_semantic_default_skipped_closed() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(env={})
    counters = report["counter_table"]

    assert report["final_status"] == runner.STATUS_SKIPPED_CLOSED
    assert report["skip_reason"] == "live semantic lane env gate is closed"
    assert counters["real_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0


def test_airline_live_semantic_fake_provider_pass() -> None:
    report = _report()
    counters = report["counter_table"]

    assert report["final_status"] == runner.STATUS_PASS
    assert counters["semantic_actor_call_count"] == 12
    assert counters["fake_provider_call_count"] == 12
    assert counters["real_provider_call_count"] == 0


def test_airline_live_semantic_runtime_computes_used_rejected_when_provider_omits_them() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(),
        provider=_minimal_safe_provider(),
    )

    assert report["final_status"] == runner.STATUS_PASS
    for actor in report["semantic_actor_reports"]:
        assert actor["what_runtime_used"]
        assert actor["what_runtime_rejected"]
        assert all("runtime_computed" in item for item in actor["what_runtime_used"])
        assert "provider output as truth" in actor["what_runtime_rejected"][0]
        assert "provider output as authority" in actor["what_runtime_rejected"][1]


def test_airline_live_semantic_runtime_computes_used_rejected_when_provider_returns_empty_lists() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(),
        provider=_minimal_safe_provider(include_empty_runtime_fields=True),
    )

    assert report["final_status"] == runner.STATUS_PASS
    for actor in report["semantic_actor_reports"]:
        assert actor["what_runtime_used"]
        assert actor["what_runtime_rejected"]
        assert "runtime_computed" in actor["what_runtime_used"][0]
        assert any(
            "provider output as packet or receipt creator" in item
            for item in actor["what_runtime_rejected"]
        )


def test_airline_live_semantic_prompt_does_not_ask_llm_to_fill_runtime_used_rejected(
    tmp_path: Path,
) -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(tmp_path),
        provider=_minimal_safe_provider(),
    )
    prompt_text = "\n".join(path.read_text() for path in tmp_path.glob("*_prompt.txt"))

    assert report["final_status"] == runner.STATUS_PASS
    assert '"what_runtime_used"' + ": []" not in prompt_text
    assert '"what_runtime_rejected"' + ": []" not in prompt_text
    assert "Runtime will compute what_runtime_used and what_runtime_rejected" in prompt_text
    assert "runtime computes what_runtime_used" in prompt_text
    assert "Return only semantic fields and safety flags." in prompt_text


def test_airline_live_semantic_real_gemini_like_orchestrator_response_no_runtime_fields_passes(
    tmp_path: Path,
) -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(tmp_path),
        provider=_minimal_safe_provider(),
    )
    counters = report["counter_table"]
    call_order = report["semantic_actor_call_order"]
    dependency = next(
        item
        for item in report["vertical_fractal_dependencies"]
        if item["child_actor_id"] == "bank_idempotency_risk_vertical_cell_llm"
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert counters["semantic_actor_call_count"] == 12
    assert counters["bsep_created_count"] == 1
    assert counters["bsep_validated_count"] == 1
    assert call_order.index("tri_party_airline_semantic_architect_llm") > call_order.index(
        "tri_party_airline_orchestrator_llm",
    )
    assert dependency["child_started_after_parent_validation"] is True
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_booking_created_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_live_semantic_real_provider_requires_explicit_flag() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env={runner.ENV_LANE: "1"},
    )
    counters = report["counter_table"]

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["skip_reason"] == "provider_mode_not_selected"
    assert counters["real_provider_call_count"] == 0
    assert counters["fake_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0


def test_airline_live_semantic_fake_and_real_flags_ambiguous(
    tmp_path: Path,
) -> None:
    env = _real_env(tmp_path)
    env[runner.ENV_FAKE_PROVIDER] = "1"
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(env=env)
    counters = report["counter_table"]

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["skip_reason"] == "ambiguous_provider_mode"
    assert counters["real_provider_call_count"] == 0
    assert counters["fake_provider_call_count"] == 0


def test_airline_live_semantic_real_provider_requires_artifact_dir() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(),
        provider=_real_provider(),
    )
    counters = report["counter_table"]

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["skip_reason"] == "real_provider_requires_artifact_dir"
    assert counters["real_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0


def test_airline_live_semantic_real_provider_uses_injected_provider_without_network(
    tmp_path: Path,
) -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(tmp_path),
        provider=_real_provider(),
    )
    rendered = runner.render_tri_party_airline_live_semantic_lane_v01(report)
    counters = report["counter_table"]

    assert report["final_status"] == runner.STATUS_PASS
    assert report["provider_mode"] == runner.PROVIDER_MODE_REAL
    assert "provider_mode: real_provider" in rendered
    assert counters["semantic_actor_call_count"] == 12
    assert counters["real_provider_call_count"] == 12
    assert counters["fake_provider_call_count"] == 0
    assert counters["network_used_count"] == 12
    assert counters["gemini_called_count"] == 12
    assert len(list(tmp_path.glob("*_prompt.txt"))) == 12


def test_airline_live_semantic_real_provider_error_fails_closed(
    tmp_path: Path,
) -> None:
    fake = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        if actor_id == "client_purchase_intent_reviewer_llm":
            raise RuntimeError("provider exploded with traceback sandbox_token_abc")
        return fake(actor_id, prompt, metadata)

    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(tmp_path),
        provider=provider,
    )
    rendered = runner.render_tri_party_airline_live_semantic_lane_v01(report)

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "provider_call_failed:client_purchase_intent_reviewer_llm" in report[
        "validation_errors"
    ]
    assert report["failed_actor_id"] == "client_purchase_intent_reviewer_llm"
    assert report["failed_stage"] == "provider_call"
    assert "traceback" not in rendered.lower()
    assert "sandbox_token_abc" not in rendered


def test_airline_live_semantic_real_provider_bad_output_fails_closed(
    tmp_path: Path,
) -> None:
    fake = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        if actor_id == "bank_payment_policy_reviewer_llm":
            return "{bad-json"
        return fake(actor_id, prompt, metadata)

    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(tmp_path),
        provider=provider,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["provider_mode"] == runner.PROVIDER_MODE_REAL
    assert report["failed_stage"] == "actor_validation"


def test_airline_live_semantic_real_provider_bsep_and_vertical_dependencies(
    tmp_path: Path,
) -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(tmp_path),
        provider=_real_provider(),
    )
    call_order = report["semantic_actor_call_order"]
    dependency = next(
        item
        for item in report["vertical_fractal_dependencies"]
        if item["child_actor_id"] == "airline_fare_rules_vertical_cell_llm"
    )
    fare_prompt = (
        tmp_path / "airline_fare_rules_vertical_cell_llm_prompt.txt"
    ).read_text()

    assert report["bsep_validation"]["validation_status"] == runner.STATUS_PASS
    assert call_order.index("tri_party_airline_orchestrator_llm") == 0
    assert call_order.index("tri_party_airline_semantic_architect_llm") == 1
    assert len(report["bsep_side_projections"]) == 4
    assert dependency["child_started_after_parent_validation"] is True
    assert dependency["child_received_parent_canonical_summary"] is True
    assert "Parent canonical summary" in fare_prompt
    assert "parent raw response" not in fare_prompt


def test_airline_live_semantic_real_provider_artifact_files(tmp_path: Path) -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(tmp_path),
        provider=_real_provider(),
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert len(list(tmp_path.glob("*_prompt.txt"))) == 12
    assert len(list(tmp_path.glob("*_raw_response.txt"))) == 12
    assert len(list(tmp_path.glob("*_extracted_json_candidate.json"))) == 12
    assert len([item["validation_artifact"] for item in report["semantic_actor_reports"]]) == 12
    assert len(list(tmp_path.glob("*_canonical_summary.json"))) == 12
    for name in (
        "summary.json",
        "secret_scan.json",
        "tri_party_airline_bsep_packet.json",
        "tri_party_airline_bsep_validation.json",
        "tri_party_airline_bsep_side_projections.json",
    ):
        assert (tmp_path / name).exists()


def test_airline_live_semantic_bsep_before_architect() -> None:
    report = _report()
    call_order = report["semantic_actor_call_order"]
    bsep = report["bsep_membrane"]

    assert report["counter_table"]["bsep_created_count"] == 1
    assert report["counter_table"]["bsep_validated_count"] == 1
    assert call_order.index("tri_party_airline_orchestrator_llm") == 0
    assert call_order.index("tri_party_airline_semantic_architect_llm") == 1
    assert report["bsep_validation"]["validation_status"] == runner.STATUS_PASS
    assert report["counter_table"]["bsep_side_projection_count"] == 4
    assert bsep["raw_passport_included"] is False
    assert bsep["raw_card_included"] is False
    assert bsep["raw_provider_text_included"] is False


def test_airline_live_semantic_actor_artifacts_written(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert report["final_status"] == runner.STATUS_PASS
    assert len(list(tmp_path.glob("*_prompt.txt"))) == 12
    assert len(list(tmp_path.glob("*_raw_response.txt"))) == 12
    assert len(list(tmp_path.glob("*_extracted_json_candidate.json"))) == 12
    assert len([item["validation_artifact"] for item in report["semantic_actor_reports"]]) == 12
    assert len(list(tmp_path.glob("*_canonical_summary.json"))) == 12
    for name in (
        "summary.json",
        "secret_scan.json",
        "tri_party_airline_bsep_packet.json",
        "tri_party_airline_bsep_validation.json",
        "tri_party_airline_bsep_side_projections.json",
    ):
        assert (tmp_path / name).exists()


def test_airline_live_semantic_actor_inputs_are_bounded(tmp_path: Path) -> None:
    _report(tmp_path)
    prompt_text = "\n".join(path.read_text() for path in tmp_path.glob("*_prompt.txt"))

    assert "Use bounded context only." in prompt_text
    for forbidden in (
        "raw_passport_value",
        "raw_card_number",
        "raw_iban_value",
        "raw_payment_token_value",
        "API key value",
        "sibling raw output",
    ):
        assert forbidden not in prompt_text


def test_airline_live_semantic_outputs_drive_runtime_canonicalization(
    tmp_path: Path,
) -> None:
    report = _report(tmp_path)
    actor = next(
        item
        for item in report["semantic_actor_reports"]
        if item["actor_id"] == "client_purchase_intent_reviewer_llm"
    )
    canonical = json.loads(Path(actor["canonical_summary_artifact"]).read_text())

    assert "Offer A best fits" in actor["output_semantic_summary"]
    assert canonical["semantic_summary"] == actor["output_semantic_summary"]
    assert actor["what_runtime_used"]
    assert actor["what_runtime_rejected"]
    assert report["counter_table"]["provider_output_used_as_authority_count"] == 0


def test_airline_live_semantic_bad_malformed_response_fails_closed() -> None:
    fake = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        if actor_id == "client_purchase_intent_reviewer_llm":
            return "{not-json"
        return fake(actor_id, prompt, metadata)

    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(),
        provider=provider,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["validation_errors"]


def test_airline_live_semantic_unsafe_authority_claim_fails_closed() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(),
        provider=_mutating_provider(
            "client_purchase_intent_reviewer_llm",
            {"authority_created": True},
        ),
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED


def test_airline_live_semantic_payment_ticket_booking_claim_fails_closed() -> None:
    for flag in ("payment_created", "ticket_created", "booking_created"):
        report = runner.collect_tri_party_airline_live_semantic_lane_v01(
            env=_enabled_env(),
            provider=_mutating_provider(
                "bank_payment_policy_reviewer_llm",
                {flag: True},
            ),
        )
        assert report["final_status"] == runner.STATUS_FAIL_CLOSED


def test_airline_live_semantic_vertical_child_waits_for_parent() -> None:
    report = _report()
    dependencies = {
        item["child_actor_id"]: item
        for item in report["vertical_fractal_dependencies"]
    }
    fare_child = dependencies["airline_fare_rules_vertical_cell_llm"]

    assert fare_child["parent_actor_id"] == "airline_offer_policy_reviewer_llm"
    assert fare_child["child_started_after_parent_validation"] is True
    assert fare_child["child_received_parent_canonical_summary"] is True
    assert fare_child["child_received_parent_raw_response"] is False
    assert fare_child["child_received_sibling_raw_output"] is False


def test_airline_live_semantic_parent_failure_blocks_vertical_child() -> None:
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(),
        provider=_mutating_provider(
            "airline_offer_policy_reviewer_llm",
            {"semantic_summary": ""},
        ),
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "airline_offer_policy_reviewer_llm" in report["semantic_actor_call_order"]
    assert "airline_fare_rules_vertical_cell_llm" not in report["semantic_actor_call_order"]
    assert (
        "airline_seat_baggage_vertical_cell_llm"
        not in report["semantic_actor_call_order"]
    )


def test_airline_live_semantic_cross_root_reviewer_not_fourth_root() -> None:
    report = _report()
    reviewer = next(
        item
        for item in report["semantic_actor_reports"]
        if item["actor_id"] == "tri_party_evidence_consistency_reviewer_llm"
    )

    assert reviewer["side"] == "cross_root_advisory"
    assert reviewer["authority_created"] is False
    assert all(row["boundary_preserved"] for row in report["root_boundaries"])


def test_airline_live_semantic_happy_path_mock_only() -> None:
    report = _report()
    summaries = "\n".join(report["what_each_llm_returned"].values())
    counters = report["counter_table"]

    assert "mock authorization" in summaries
    assert "mock ticket evidence" in summaries
    assert "mock PNR evidence" in summaries
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_booking_created_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_live_semantic_renderer_sections() -> None:
    rendered = runner.run_tri_party_airline_live_semantic_lane_v01(
        env=_enabled_env(),
    )

    for section in runner.REQUIRED_RENDER_SECTIONS:
        assert section in rendered
    assert "[WHAT EACH LLM RECEIVED]" in rendered
    assert "[WHAT EACH LLM RETURNED]" in rendered
    assert "[WHAT RUNTIME USED]" in rendered
    assert "[WHAT RUNTIME REJECTED]" in rendered
    assert "Tests do not ignore LLM output" in rendered
    assert "No real airline API, bank API, GDS API, payment, ticket, booking, or production effect occurs in this lane." in rendered


def test_airline_live_semantic_secret_scan_passes() -> None:
    report = _report()

    assert report["secret_scan"]["passed"] is True
    assert report["secret_scan"]["matched_markers"] == ()


def test_airline_live_semantic_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text()

    assert "google.genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "semantic_provider_adapter" not in source
    assert "run_live_provider_adapter_response_capture_v01" in source
    assert "semantic_to_contract_causal_runtime_v01" in source
    assert "semantic_to_contract_binding_v01" in source
    assert "real airline API connector" not in source
    assert "real bank API connector" not in source
    assert "production " + "ready" not in source
    assert "public auditor " + "ready" not in source
    for left, right in (
        ("AI bought a", " real ticket"),
        ("AI paid", " real money"),
        ("ClientRoot issued", " ticket"),
        ("AirlineRoot charged", " card"),
        ("BankRoot bought", " ticket"),
        ("LLM creates", " ticket"),
        ("LLM creates", " payment"),
        ("LLM creates", " ActionCommitPacket"),
        ("LLM creates", " receipt"),
        ("provider output is", " authority"),
    ):
        assert left + right not in source


def test_airline_live_semantic_real_provider_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text()

    assert "google.genai" not in source
    assert "from google import genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "_shared_live_gemini_provider" in source
    assert "api_key)" not in source
    assert "print(config" not in source
    assert "production " + "ready" not in source
    assert "public auditor " + "ready" not in source


def test_airline_live_semantic_real_provider_not_implemented_reason_removed() -> None:
    source = Path(runner.__file__).read_text()
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_real_env(),
        provider=_real_provider(),
    )

    assert "real_provider_not_implemented_in_fake_provider_patch" not in source
    assert report["skip_reason"] == "real_provider_requires_artifact_dir"
    assert "real_provider_not_implemented_in_fake_provider_patch" not in str(report)


def test_causal_gate_closed_preserves_existing_live_lane() -> None:
    report = _report()

    assert report["final_status"] == runner.STATUS_PASS
    assert (
        report["semantic_to_contract_causal_binding_v0_1"]["binding_status"]
        == "NOT_ENABLED"
    )


def test_exact_observed_bad_causal_proposer_shape_fails_without_repair() -> None:
    selection_input, request = _schema_fixture()
    payload = _proposal_payload(asdict(request), binding.OFFER_A_ID)
    payload.update(
        {
            "ranked_offer_ids": (binding.OFFER_A_ID, binding.OFFER_B_ID),
            "decision_factors": ({"price": "lower"},),
            "preference_matches": ({"seat": "window"},),
            "uncertainty_notes": (),
            "requires_root_review": False,
        },
    )

    report = (
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        )
    )

    assert report.validation_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE in report.reason_codes
    assert binding.REASON_EMPTY_PROVIDER_OUTPUT_FIELD in report.reason_codes
    assert payload["decision_factors"] == ({"price": "lower"},)
    assert payload["preference_matches"] == ({"seat": "window"},)
    assert payload["uncertainty_notes"] == ()
    assert payload["requires_root_review"] is False


def test_corrected_equivalent_causal_proposer_shape_passes() -> None:
    selection_input, request = _schema_fixture()
    payload = _proposal_payload(asdict(request), binding.OFFER_A_ID)
    payload.update(
        {
            "ranked_offer_ids": (binding.OFFER_A_ID, binding.OFFER_B_ID),
            "decision_factors": (
                "Offer A has the lower price while preserving baggage, window seat, and changeability.",
            ),
            "preference_matches": (
                "Matches lower price, window preference, included baggage, and changeability.",
            ),
            "uncertainty_notes": (
                "Recommendation remains advisory and requires ClientRoot review.",
            ),
            "requires_root_review": True,
        },
    )

    proposal, report = (
        binding.build_airline_semantic_offer_selection_proposal_from_payload_v01(
            selection_input,
            payload,
        )
    )

    assert report.validation_status == binding.STATUS_PASS
    assert report.reason_codes == ()
    assert proposal is not None
    assert proposal.recommended_offer_id == binding.OFFER_A_ID


def test_causal_proposer_schema_allows_a_and_b_without_default_or_bias() -> None:
    selection_input, request = _schema_fixture()
    schema = runner._build_causal_proposer_response_schema_v01(
        request,
        selection_input,
    )
    recommended = schema["properties"]["recommended_offer_id"]
    ranking_items = schema["properties"]["ranked_offer_ids"]["items"]

    assert set(recommended["enum"]) == {binding.OFFER_A_ID, binding.OFFER_B_ID}
    assert set(ranking_items["enum"]) == {binding.OFFER_A_ID, binding.OFFER_B_ID}
    assert recommended["enum"] == list(
        selection_input.client_hard_compatible_candidate_ids
    )
    assert "default" not in recommended
    assert "const" not in recommended
    assert schema["properties"]["proposal_id"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["requires_root_review"]["enum"] == [True]
    assert schema["required"] == list(runner.CAUSAL_PROPOSER_REQUIRED_FIELDS)
    assert set(schema["required"]) == set(
        binding.AirlineSemanticOfferSelectionProposalV01.__dataclass_fields__,
    )


def test_causal_reviewer_schema_lineage_and_conflict_surface() -> None:
    selection_input, proposer_request = _schema_fixture()
    reviewer_actor = binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER
    _, reviewer_request = _schema_fixture(
        actor_id=reviewer_actor,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    schema = runner._build_causal_reviewer_response_schema_v01(reviewer_request)
    properties = schema["properties"]

    assert schema["required"] == list(runner.CAUSAL_REVIEWER_REQUIRED_FIELDS)
    assert set(schema["required"]) == set(
        causal_runtime.AirlineInjectedReviewerResponseV01.__dataclass_fields__,
    )
    assert properties["transaction_id"]["enum"] == [reviewer_request.transaction_id]
    assert properties["actor_id"]["enum"] == [reviewer_actor]
    assert properties["source_request_id"]["enum"] == [reviewer_request.request_id]
    assert properties["source_selection_input_id"]["enum"] == [
        selection_input.selection_input_id,
    ]
    assert properties["source_candidate_set_snapshot_id"]["enum"] == [
        selection_input.source_candidate_set_snapshot_id,
    ]
    assert properties["source_candidate_set_digest"]["enum"] == [
        selection_input.source_candidate_set_digest,
    ]
    assert properties["reviewed_offer_id"]["enum"] == [binding.OFFER_A_ID]
    assert properties["review_role"]["enum"] == [reviewer_request.actor_role]
    assert properties["semantic_factors"]["minItems"] == 1
    assert properties["semantic_factors"]["items"] == {
        "type": "string",
        "minLength": 1,
    }
    assert "minItems" not in properties["blocking_conflicts"]
    assert properties["supports_proposed_offer"] == {"type": "boolean"}
    assert "enum" not in properties["supports_proposed_offer"]
    assert properties["supports_proposed_offer"].get("enum") is None
    assert properties["blocking_conflicts"]["items"] == {
        "type": "string",
        "minLength": 1,
    }
    assert properties["authority_created"]["enum"] == [False]
    assert properties["permission_created"]["enum"] == [False]
    assert properties["raw_output_used"]["enum"] == [False]
    assert properties["real_world_effects_count"]["enum"] == [0]
    assert schema["additionalProperties"] is False
    assert proposer_request.actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER


def test_causal_reviewer_schema_permits_support_reject_and_conflicts() -> None:
    _, reviewer_request = _schema_fixture(
        actor_id=binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    schema = runner._build_causal_reviewer_response_schema_v01(reviewer_request)
    properties = schema["properties"]

    assert properties["supports_proposed_offer"] == {"type": "boolean"}
    assert "enum" not in properties["supports_proposed_offer"]
    assert properties["blocking_conflicts"]["type"] == "array"
    assert properties["blocking_conflicts"]["items"] == {
        "type": "string",
        "minLength": 1,
    }
    assert "minItems" not in properties["blocking_conflicts"]


def test_causal_reviewer_prompt_has_no_approval_biased_skeleton() -> None:
    selection_input, reviewer_request = _schema_fixture(
        actor_id=binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    prompt = runner._build_prompt(
        actor=runner._actor_spec(binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER),
        actor_index=5,
        deterministic_report={"final_status": runner.STATUS_PASS},
        bsep_side_projections={},
        parent_report=None,
        causal_request=reviewer_request,
        causal_selection_input=selection_input,
    )

    assert '"supports_proposed_offer": true' not in prompt
    assert '"blocking_conflicts": []' not in prompt
    assert '"blocking_conflicts": []' not in prompt.replace(" ", "")
    assert "unsupported/conflicting outcomes are allowed" in prompt
    assert "do not copy an empty conflict list by default" in prompt
    assert "Derive supports_proposed_offer from actual semantic review" in prompt
    assert "Return false when the proposed offer is not supported" in prompt
    assert "do not assume PASS" in prompt
    assert "The placeholder skeleton is not valid output" in prompt
    assert "Response schema and local validator remain authoritative" in prompt


def test_conflicting_reviewer_payload_is_not_repaired_to_pass() -> None:
    selection_input, reviewer_request = _schema_fixture(
        actor_id=binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    payload = _reviewer_payload(
        asdict(reviewer_request),
        overrides={
            "supports_proposed_offer": False,
            "blocking_conflicts": ("fare_rule_conflict",),
        },
    )

    validation = runner._validate_causal_actor_candidate(
        candidate=payload,
        actor=runner._actor_spec(binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER),
        causal_request=reviewer_request,
        selection_input=selection_input,
        parse_errors=(),
    )

    assert validation["validation_status"] == runner.STATUS_FAIL_CLOSED
    assert binding.REASON_MULTI_ACTOR_CONFLICT in validation["errors"]
    assert binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED in validation["errors"]
    assert payload["supports_proposed_offer"] is False
    assert payload["blocking_conflicts"] == ("fare_rule_conflict",)


def test_clean_supporting_reviewer_payload_still_passes() -> None:
    selection_input, reviewer_request = _schema_fixture(
        actor_id=binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    payload = _reviewer_payload(asdict(reviewer_request))

    validation = runner._validate_causal_actor_candidate(
        candidate=payload,
        actor=runner._actor_spec(binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER),
        causal_request=reviewer_request,
        selection_input=selection_input,
        parse_errors=(),
    )

    assert validation["validation_status"] == runner.STATUS_PASS
    assert validation["errors"] == ()


def test_causal_proposer_prompt_contract_has_valid_shape_and_no_default() -> None:
    selection_input, request = _schema_fixture()
    prompt = runner._build_prompt(
        actor=runner._actor_spec(binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER),
        actor_index=3,
        deterministic_report={"final_status": runner.STATUS_PASS},
        bsep_side_projections={},
        parent_report=None,
        causal_request=request,
        causal_selection_input=selection_input,
    )

    assert "JSON arrays of non-empty strings" in prompt
    assert "Never return objects in these arrays" in prompt
    assert "requires_root_review must be true" in prompt
    assert binding.OFFER_A_ID in prompt
    assert binding.OFFER_B_ID in prompt
    assert '"decision_factors": []' not in prompt
    assert '"preference_matches": []' not in prompt
    assert '"uncertainty_notes": []' not in prompt
    assert '"requires_root_review": false' not in prompt
    assert f'"recommended_offer_id": "{binding.OFFER_A_ID}"' not in prompt
    assert f'"recommended_offer_id": "{binding.OFFER_B_ID}"' not in prompt
    assert "do not use a default offer" in prompt


def test_causal_response_schema_required_keys_match_contract_fields() -> None:
    selection_input, proposer_request = _schema_fixture()
    proposer_schema = runner._causal_provider_response_schema_v01(
        proposer_request,
        selection_input,
    )
    _, reviewer_request = _schema_fixture(
        actor_id=binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    reviewer_schema = runner._causal_provider_response_schema_v01(
        reviewer_request,
        selection_input,
    )

    assert proposer_schema["required"] == list(
        binding.AirlineSemanticOfferSelectionProposalV01.__dataclass_fields__,
    )
    assert reviewer_schema["required"] == list(
        causal_runtime.AirlineInjectedReviewerResponseV01.__dataclass_fields__,
    )


def test_real_provider_forwards_causal_schema_and_keeps_generic_schema_none(
    monkeypatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_shared_provider(**kwargs: Any) -> str:
        calls.append(dict(kwargs))
        return "{}"

    monkeypatch.setattr(runner, "_shared_live_gemini_provider", fake_shared_provider)
    real_provider = runner.build_real_airline_semantic_provider_v01("gemini-test")
    selection_input, proposer_request = _schema_fixture()
    proposer_schema = runner._causal_provider_response_schema_v01(
        proposer_request,
        selection_input,
    )
    _, reviewer_request = _schema_fixture(
        actor_id=binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        proposed_offer_id=binding.OFFER_A_ID,
    )
    reviewer_schema = runner._causal_provider_response_schema_v01(
        reviewer_request,
        selection_input,
    )
    env = {"HEDGEHOG_TEST_TIMEOUT_SECONDS": "7"}

    real_provider(
        proposer_request.actor_id,
        "proposer prompt",
        {"provider_env": env, "provider_response_schema": proposer_schema},
    )
    real_provider(
        reviewer_request.actor_id,
        "reviewer prompt",
        {"provider_env": env, "provider_response_schema": reviewer_schema},
    )
    real_provider(
        "tri_party_airline_orchestrator_llm",
        "generic prompt",
        {"provider_env": env},
    )

    assert calls[0]["response_schema"] == proposer_schema
    assert calls[0]["response_schema"] is not proposer_schema
    assert calls[1]["response_schema"] == reviewer_schema
    assert calls[1]["response_schema"] is not reviewer_schema
    assert calls[2]["response_schema"] is None
    assert [call["model_name"] for call in calls] == ["gemini-test"] * 3
    assert [call["role"] for call in calls] == [
        proposer_request.actor_id,
        reviewer_request.actor_id,
        "tri_party_airline_orchestrator_llm",
    ]
    assert all(
        call["timeout_seconds"] == runner.provider_adapter._timeout_seconds(env)
        for call in calls
    )
    assert all(call["explicit_http_timeout"] is True for call in calls)
    assert all(call["env"] == env for call in calls)


def test_no_post_provider_causal_repair_source_boundary() -> None:
    source = Path(runner.__file__).read_text()

    forbidden_snippets = (
        "str(candidate",
        "str(payload",
        "decision_factors = [str",
        "preference_matches = [str",
        "uncertainty_notes = (\"Recommendation remains advisory",
        "requires_root_review\"] = True",
        "requires_root_review = True",
        "recommended_offer_id = binding.OFFER_A_ID",
        "recommended_offer_id = binding.OFFER_B_ID",
        "return binding.OFFER_A_ID",
        "return binding.OFFER_B_ID",
    )
    for snippet in forbidden_snippets:
        assert snippet not in source


def test_causal_integrated_preference_a_passes() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )
    bridge = report["semantic_to_contract_deterministic_bridge"]

    assert report["final_status"] == runner.STATUS_PASS
    assert bridge["semantic_recommendation_id"] == binding.OFFER_A_ID
    assert bridge["deterministic_transaction_offer_id"] == binding.OFFER_A_ID
    assert bridge["deterministic_corridor_offer_id"] == binding.OFFER_A_ID
    assert bridge["all_offer_ids_match"] is True


def test_preference_a_bridge_reads_actual_corridor_contract_offer() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )
    bridge = report["semantic_to_contract_deterministic_bridge"]

    assert bridge["deterministic_transaction_offer_id"] == binding.OFFER_A_ID
    assert bridge["deterministic_corridor_offer_id"] == binding.OFFER_A_ID
    assert bridge["all_offer_ids_match"] is True


def test_causal_integrated_preference_b_passes() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_b_v01(),
    )
    bridge = report["semantic_to_contract_deterministic_bridge"]

    assert report["final_status"] == runner.STATUS_PASS
    assert bridge["semantic_recommendation_id"] == binding.OFFER_B_ID
    assert bridge["deterministic_transaction_offer_id"] == binding.OFFER_B_ID
    assert bridge["deterministic_corridor_offer_id"] == binding.OFFER_B_ID
    assert bridge["all_offer_ids_match"] is True


def test_preference_b_bridge_reads_actual_corridor_contract_offer() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_b_v01(),
    )
    bridge = report["semantic_to_contract_deterministic_bridge"]

    assert bridge["deterministic_transaction_offer_id"] == binding.OFFER_B_ID
    assert bridge["deterministic_corridor_offer_id"] == binding.OFFER_B_ID
    assert bridge["all_offer_ids_match"] is True


def test_actual_corridor_contract_offer_mismatch_fails_bridge(monkeypatch) -> None:
    original_collector = (
        runner.deterministic_airline
        .collect_tri_party_airline_ticket_purchase_mock_e2e_v01
    )

    def tampered_collector(*args: Any, **kwargs: Any) -> dict[str, Any]:
        deterministic_report = original_collector(*args, **kwargs)
        corridor_report = deterministic_report[
            "airline_ticket_purchase_corridor_v0_1"
        ]
        bad_context = replace(
            corridor_report.contract_context,
            offer_id=binding.OFFER_B_ID,
        )
        tampered_report = dict(deterministic_report)
        tampered_report["airline_ticket_purchase_corridor_v0_1"] = replace(
            corridor_report,
            contract_context=bad_context,
        )
        return tampered_report

    monkeypatch.setattr(
        runner.deterministic_airline,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        tampered_collector,
    )

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )
    bridge = report["semantic_to_contract_deterministic_bridge"]

    assert bridge["deterministic_transaction_offer_id"] == binding.OFFER_A_ID
    assert bridge["deterministic_corridor_offer_id"] == binding.OFFER_B_ID
    assert bridge["bridge_status"] == runner.STATUS_FAIL_CLOSED
    assert bridge["all_offer_ids_match"] is False
    assert report["final_status"] == runner.STATUS_FAIL_CLOSED


def test_bridge_source_does_not_copy_transaction_offer_to_corridor_offer() -> None:
    source = Path(runner.__file__).read_text()

    assert "deterministic_corridor_offer_id = deterministic_offer_id" not in source


def test_exact_twelve_actor_calls_and_order_preserved() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )

    assert report["counter_table"]["semantic_actor_call_count"] == 12
    assert report["semantic_actor_call_order"] == tuple(
        actor["actor_id"] for actor in runner.ACTOR_SPECS
    )
    assert len(set(report["semantic_actor_call_order"])) == 12


def test_exact_five_causal_and_seven_generic_actors() -> None:
    counters = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )["counter_table"]

    assert counters["causal_semantic_actor_call_count"] == 5
    assert counters["generic_semantic_actor_call_count"] == 7
    assert counters["duplicate_semantic_actor_call_count"] == 0


def test_live_lane_precollected_and_deterministic_counts() -> None:
    counters = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )["counter_table"]

    assert counters["precollected_causal_run_count"] == 1
    assert counters["provider_calls_inside_precollected_runtime_count"] == 0
    assert counters["deterministic_airline_collection_count"] == 1
    assert counters["ticket_purchase_corridor_execution_count"] == 1


def test_offer_a_and_b_use_same_candidate_snapshot() -> None:
    a_report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )
    b_report = _causal_report_for_preference(
        binding.build_client_constraints_preference_b_v01(),
    )
    a_section = a_report["semantic_to_contract_causal_binding_v0_1"]
    b_section = b_report["semantic_to_contract_causal_binding_v0_1"]

    assert a_section["source_candidate_set_ref"] == b_section[
        "source_candidate_set_ref"
    ]
    assert a_section["source_candidate_set_snapshot_id"] == b_section[
        "source_candidate_set_snapshot_id"
    ]
    assert a_section["source_candidate_set_digest"] == b_section[
        "source_candidate_set_digest"
    ]
    assert a_section["visible_candidate_ids"] == b_section["visible_candidate_ids"]
    assert a_section["airline_valid_candidate_ids"] == b_section[
        "airline_valid_candidate_ids"
    ]
    assert a_section["client_hard_compatible_candidate_ids"] == b_section[
        "client_hard_compatible_candidate_ids"
    ]


def test_causal_selection_uses_actual_live_airline_bsep_projection() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )
    section = report["semantic_to_contract_causal_binding_v0_1"]
    projection = report["bsep_side_projections"]["airline_bsep_projection"]

    assert section["actual_bsep_packet_id"] == report["bsep_membrane"][
        "bsep_packet_id"
    ]
    assert section["actual_airline_bsep_projection_ref"] == projection[
        "projection_ref"
    ]
    assert section["causal_selection_bsep_projection_ref"] == projection[
        "projection_ref"
    ]
    assert section["bsep_refs_match"] is True


def test_live_causal_mode_does_not_use_fixture_bsep_projection_builder(
    monkeypatch,
) -> None:
    def forbidden_builder():
        raise AssertionError("fixture BSEP builder must not be used")

    monkeypatch.setattr(
        binding,
        "build_valid_airline_bsep_projection_ref_v01",
        forbidden_builder,
    )

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )

    assert report["final_status"] == runner.STATUS_PASS


def test_causal_request_bsep_ref_matches_actual_live_bsep_artifact() -> None:
    seen_requests: list[Mapping[str, Any]] = []
    generic = _content_sensitive_causal_provider()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if isinstance(request, Mapping):
            seen_requests.append(request)
        return generic(actor_id, prompt, metadata)

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        provider=provider,
    )
    actual_ref = report["bsep_side_projections"]["airline_bsep_projection"][
        "projection_ref"
    ]

    assert report["final_status"] == runner.STATUS_PASS
    assert len(seen_requests) == 5
    assert {request["source_bsep_projection_ref"] for request in seen_requests} == {
        actual_ref,
    }


def test_precollected_causal_report_bsep_ref_matches_live_projection() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_b_v01(),
    )
    section = report["semantic_to_contract_causal_binding_v0_1"]

    assert section["causal_selection_bsep_projection_ref"] == section[
        "actual_airline_bsep_projection_ref"
    ]
    assert report["semantic_to_contract_deterministic_bridge"][
        "bsep_refs_match"
    ] is True


def test_tampered_live_airline_bsep_projection_stops_before_deterministic_corridor(
    monkeypatch,
) -> None:
    original = runner._build_bsep_side_projections

    def tampered(packet: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        projections = original(packet)
        projections.pop("airline_bsep_projection")
        return projections

    monkeypatch.setattr(runner, "_build_bsep_side_projections", tampered)

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert runner.REASON_LIVE_AIRLINE_BSEP_PROJECTION_MISSING in report[
        "validation_errors"
    ]
    assert report["counter_table"]["ticket_purchase_corridor_execution_count"] == 0


def test_changed_live_bsep_packet_id_with_old_typed_ref_fails_closed(
    monkeypatch,
) -> None:
    def stale_projection(**kwargs):
        return binding.build_valid_airline_bsep_projection_ref_v01(), ()

    monkeypatch.setattr(
        runner,
        "_typed_airline_bsep_projection_ref_from_live_projection",
        stale_projection,
    )

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert runner.REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH in report[
        "validation_errors"
    ]
    assert report["counter_table"]["ticket_purchase_corridor_execution_count"] == 0


def test_no_offer_a_bias_in_client_actor_spec() -> None:
    actor = runner._actor_spec(binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER)

    assert "explain why Offer A best matches" not in actor["semantic_work"]


def test_unknown_offer_stops_before_deterministic_corridor() -> None:
    generic = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if isinstance(request, Mapping) and actor_id == (
            binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER
        ):
            return json.dumps(_proposal_payload(request, "offer:unknown"), sort_keys=True)
        if isinstance(request, Mapping):
            return json.dumps(_reviewer_payload(request), sort_keys=True)
        return generic(actor_id, prompt, metadata)

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        provider=provider,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["counter_table"]["ticket_purchase_corridor_execution_count"] == 0


def test_offer_c_stops_before_deterministic_corridor() -> None:
    generic = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if isinstance(request, Mapping) and actor_id == (
            binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER
        ):
            return json.dumps(_proposal_payload(request, binding.OFFER_C_ID), sort_keys=True)
        if isinstance(request, Mapping):
            return json.dumps(_reviewer_payload(request), sort_keys=True)
        return generic(actor_id, prompt, metadata)

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        provider=provider,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["counter_table"]["ticket_purchase_corridor_execution_count"] == 0


def test_reviewer_conflict_stops_before_deterministic_corridor() -> None:
    generic = runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if isinstance(request, Mapping) and actor_id == (
            binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER
        ):
            return json.dumps(_proposal_payload(request, binding.OFFER_A_ID), sort_keys=True)
        if isinstance(request, Mapping):
            return json.dumps(
                _reviewer_payload(
                    request,
                    overrides={
                        "blocking_conflicts": ("conflict",),
                        "supports_proposed_offer": False,
                    },
                ),
                sort_keys=True,
            )
        return generic(actor_id, prompt, metadata)

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        provider=provider,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["counter_table"]["ticket_purchase_corridor_execution_count"] == 0


def test_no_direct_override_default_or_fallback() -> None:
    bridge = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )["semantic_to_contract_deterministic_bridge"]

    assert bridge["direct_offer_override_used"] is False
    assert bridge["default_offer_used"] is False
    assert bridge["silent_fallback_used"] is False


def test_artifact_capture_contains_causal_bridge_files(tmp_path: Path) -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path=tmp_path,
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert (tmp_path / "semantic_to_contract_causal_run.json").exists()
    assert (tmp_path / "semantic_to_contract_bridge.json").exists()
    assert (tmp_path / "integrated_deterministic_airline_summary.json").exists()


def test_no_network_gemini_or_real_effects() -> None:
    counters = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )["counter_table"]

    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_live_and_deterministic_import_closed_causal_runtime() -> None:
    live_source = Path(runner.__file__).read_text(encoding="utf-8")
    deterministic_source = Path(
        runner.deterministic_airline.__file__,
    ).read_text(encoding="utf-8")

    assert "semantic_to_contract_causal_runtime_v01" in live_source
    assert "semantic_to_contract_causal_runtime_v01" in deterministic_source


def test_no_provider_selection_algorithm_in_production_modules() -> None:
    live_source = Path(runner.__file__).read_text(encoding="utf-8")
    runtime_source = Path(causal_runtime.__file__).read_text(encoding="utf-8")

    assert "preference_A" not in live_source + runtime_source
    assert "preference_B" not in live_source + runtime_source
    assert "if window then" not in live_source + runtime_source


def test_slice_d_live_causal_lane_collects_ledger_and_writes_one_artifact(
    tmp_path: Path,
) -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    integration = report["airline_transaction_artifact_ledger_integration"]
    ledger = report["airline_transaction_artifact_ledger_v0_1"]
    ledger_path = tmp_path / "airline_transaction_artifact_ledger.json"

    assert report["final_status"] == runner.STATUS_PASS
    assert integration["integration_status"] == runner.STATUS_PASS
    assert integration["source_bundle_validation_status"] == runner.STATUS_PASS
    assert integration["ledger_validation_status"] == runner.STATUS_PASS
    assert integration["entry_count"] == 19
    assert integration["dependency_edge_count"] == 29
    assert integration["root_final_count"] == 3
    assert integration["source_bundle_collection_count"] == 1
    assert integration["ledger_collection_count"] == 1
    assert integration["ledger_validation_count"] == 1
    assert integration["corridor_execution_count"] == 1
    assert integration["artifact_written_count"] == 1
    assert ledger.entry_count == 19
    assert ledger.dependency_edge_count == 29
    assert ledger.root_final_count == 3
    assert ledger_path.exists()
    assert [path.name for path in tmp_path.iterdir()].count(
        "airline_transaction_artifact_ledger.json",
    ) == 1


def test_slice_d_live_written_ledger_matches_report_semantically(
    tmp_path: Path,
) -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    ledger = report["airline_transaction_artifact_ledger_v0_1"]
    written = json.loads(
        (tmp_path / "airline_transaction_artifact_ledger.json").read_text(),
    )

    assert written == runner._json_safe(ledger)


def test_slice_d_live_actual_bsep_lineage_reaches_written_ledger(
    tmp_path: Path,
) -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    projections = report["bsep_side_projections"]
    written = json.loads(
        (tmp_path / "airline_transaction_artifact_ledger.json").read_text(),
    )
    bsep_entries = {
        entry["artifact_id"]: entry
        for entry in written["entries"]
        if entry["event_type"] == "bsep_projection_created"
    }

    assert len(bsep_entries) == 4
    for projection in projections.values():
        entry = bsep_entries[projection["projection_id"]]
        assert entry["canonical_hash_input"]["projection_ref"] == (
            projection["projection_ref"]
        )
        assert entry["canonical_hash_input"]["bsep_packet_id"] == (
            projection["source_bsep_packet_id"]
        )
        assert entry["canonical_hash_input"]["side"] == projection["side"]
    assert report["semantic_to_contract_causal_binding_v0_1"][
        "actual_airline_bsep_projection_ref"
    ] == projections["airline_bsep_projection"]["projection_ref"]


def test_slice_d_live_ledger_lineage_and_call_counters() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )
    counters = report["counter_table"]
    ledger = report["airline_transaction_artifact_ledger_v0_1"]
    purchase_entry = next(
        entry
        for entry in ledger.entries
        if entry.artifact_type == "ClientPurchaseIntentV01"
    )

    assert counters["semantic_actor_call_count"] == 12
    assert counters["causal_semantic_actor_call_count"] == 5
    assert counters["generic_semantic_actor_call_count"] == 7
    assert counters["local_injected_semantic_callback_count"] == 5
    assert counters["duplicate_semantic_actor_call_count"] == 0
    assert counters["precollected_causal_run_count"] == 1
    assert counters["provider_calls_inside_precollected_runtime_count"] == 0
    assert counters["deterministic_airline_collection_count"] == 1
    assert counters["ticket_purchase_corridor_execution_count"] == 1
    assert counters["airline_transaction_artifact_ledger_source_bundle_collection_count"] == 1
    assert counters["airline_transaction_artifact_ledger_collection_count"] == 1
    assert counters["airline_transaction_artifact_ledger_validation_count"] == 1
    assert counters["airline_transaction_artifact_ledger_artifact_written_count"] == 0
    assert counters["airline_transaction_artifact_ledger_provider_calls_added_count"] == 0
    assert counters["airline_transaction_artifact_ledger_network_calls_added_count"] == 0
    assert counters["airline_transaction_artifact_ledger_gemini_calls_added_count"] == 0
    assert counters["real_world_effects_count"] == 0
    approval_snapshot = purchase_entry.canonical_hash_input["source_snapshot"][
        "purchase_approval_evidence"
    ]
    assert approval_snapshot["approval_ref"] == purchase_entry.source_validation_refs[0]
    assert approval_snapshot["approval_scope"] == (
        "selected_mock_offer_purchase_intent_only"
    )


def test_slice_d_live_integration_call_counts_are_observed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls = {
        "causal": 0,
        "deterministic": 0,
        "corridor": 0,
        "source_bundle": 0,
        "ledger_collect": 0,
        "ledger_validate": 0,
        "writer": 0,
    }
    original_causal = (
        runner.causal_runtime
        .collect_airline_semantic_to_contract_causal_run_from_precollected_payloads_v01
    )
    original_deterministic = (
        runner.deterministic_airline
        .collect_tri_party_airline_ticket_purchase_mock_e2e_v01
    )
    original_corridor = (
        runner.deterministic_airline.corridor_runtime
        .collect_airline_ticket_purchase_corridor_execution_result_v01
    )
    original_bundle = (
        runner.deterministic_airline
        ._build_airline_transaction_artifact_ledger_source_bundle_v01
    )
    original_collect = (
        runner.deterministic_airline.ledger_collector
        .collect_airline_transaction_artifact_ledger_from_source_v01
    )
    original_validate = (
        runner.deterministic_airline.ledger_collector.ledger
        .validate_airline_transaction_artifact_ledger_v01
    )
    original_writer = runner._write_airline_transaction_artifact_ledger_once

    def causal_wrapper(*args, **kwargs):
        calls["causal"] += 1
        return original_causal(*args, **kwargs)

    def deterministic_wrapper(*args, **kwargs):
        calls["deterministic"] += 1
        return original_deterministic(*args, **kwargs)

    def corridor_wrapper(*args, **kwargs):
        calls["corridor"] += 1
        return original_corridor(*args, **kwargs)

    def bundle_wrapper(*args, **kwargs):
        calls["source_bundle"] += 1
        return original_bundle(*args, **kwargs)

    def collect_wrapper(*args, **kwargs):
        calls["ledger_collect"] += 1
        return original_collect(*args, **kwargs)

    def validate_wrapper(*args, **kwargs):
        calls["ledger_validate"] += 1
        return original_validate(*args, **kwargs)

    def writer_wrapper(*args, **kwargs):
        calls["writer"] += 1
        return original_writer(*args, **kwargs)

    monkeypatch.setattr(
        runner.causal_runtime,
        "collect_airline_semantic_to_contract_causal_run_from_precollected_payloads_v01",
        causal_wrapper,
    )
    monkeypatch.setattr(
        runner.deterministic_airline,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        deterministic_wrapper,
    )
    monkeypatch.setattr(
        runner.deterministic_airline.corridor_runtime,
        "collect_airline_ticket_purchase_corridor_execution_result_v01",
        corridor_wrapper,
    )
    monkeypatch.setattr(
        runner.deterministic_airline,
        "_build_airline_transaction_artifact_ledger_source_bundle_v01",
        bundle_wrapper,
    )
    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        collect_wrapper,
    )
    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector.ledger,
        "validate_airline_transaction_artifact_ledger_v01",
        validate_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "_write_airline_transaction_artifact_ledger_once",
        writer_wrapper,
    )

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert calls == {
        "causal": 1,
        "deterministic": 1,
        "corridor": 1,
        "source_bundle": 1,
        "ledger_collect": 1,
        "ledger_validate": 1,
        "writer": 1,
    }


def test_slice_d_live_fail_closed_source_validation_writes_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def wrong_source_bundle(*_args, **_kwargs):
        return object()

    monkeypatch.setattr(
        runner.deterministic_airline,
        "_build_airline_transaction_artifact_ledger_source_bundle_v01",
        wrong_source_bundle,
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_fail_closed_ledger_validation_writes_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = (
        runner.deterministic_airline.ledger_collector
        .collect_airline_transaction_artifact_ledger_from_source_v01
    )

    def bad_collect(*args, **kwargs):
        ledger = original(*args, **kwargs)
        return replace(ledger, entry_count=18)

    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        bad_collect,
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_actual_geometry_corruption_writes_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = (
        runner.deterministic_airline.ledger_collector
        .collect_airline_transaction_artifact_ledger_from_source_v01
    )

    def bad_collect(*args, **kwargs):
        ledger = original(*args, **kwargs)
        return replace(ledger, entries=ledger.entries[:-1])

    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        bad_collect,
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_duplicate_client_root_final_missing_bank_root_final_writes_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = (
        runner.deterministic_airline.ledger_collector
        .collect_airline_transaction_artifact_ledger_from_source_v01
    )

    def bad_collect(*args, **kwargs):
        ledger = original(*args, **kwargs)
        entries = list(ledger.entries)
        bank_index = next(
            index
            for index, entry in enumerate(entries)
            if entry.artifact_type == "BankRootFinalV01"
        )
        entries[bank_index] = replace(
            entries[bank_index],
            artifact_type="ClientRootFinalV01",
        )
        return replace(ledger, entries=tuple(entries))

    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        bad_collect,
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_invalid_typed_ledger_status_writes_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = (
        runner.deterministic_airline.ledger_collector
        .collect_airline_transaction_artifact_ledger_from_source_v01
    )

    def bad_collect(*args, **kwargs):
        ledger = original(*args, **kwargs)
        return replace(ledger, validation_status=runner.STATUS_FAIL_CLOSED)

    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        bad_collect,
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_typed_ledger_validation_errors_write_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = (
        runner.deterministic_airline.ledger_collector
        .collect_airline_transaction_artifact_ledger_from_source_v01
    )

    def bad_collect(*args, **kwargs):
        ledger = original(*args, **kwargs)
        return replace(ledger, validation_errors=("forced_validation_error",))

    monkeypatch.setattr(
        runner.deterministic_airline.ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        bad_collect,
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


@pytest.mark.parametrize(
    "constraints_factory",
    (
        binding.build_client_constraints_preference_a_v01,
        binding.build_client_constraints_preference_b_v01,
    ),
)
def test_crypto_slice_d_writes_one_unanchored_manifest_and_verification(
    constraints_factory,
    tmp_path: Path,
) -> None:
    report = _crypto_report_for_preference(constraints_factory(), tmp_path)
    crypto = report["airline_crypto_artifact_seal_integration"]
    manifest_path = tmp_path / runner.CRYPTO_MANIFEST_FILE
    verification_path = tmp_path / runner.CRYPTO_VERIFICATION_FILE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    summary_text = (tmp_path / "summary.json").read_text(encoding="utf-8")
    summary = json.loads(summary_text)

    assert report["final_status"] == runner.STATUS_PASS
    assert (
        crypto["integration_status"]
        == runner.crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert crypto["integration_status"] != runner.STATUS_PASS
    assert (crypto["ledger_entry_count"], crypto["dependency_edge_count"], crypto["root_final_count"]) == (19, 29, 3)
    assert crypto["source_file_count"] == 9
    assert crypto["e1_audit_count"] == 1
    assert tuple(
        crypto[name]
        for name in (
            "source_bundle_validation_count",
            "manifest_core_collection_count",
            "envelope_collection_count",
            "post_collection_snapshot_provider_call_count",
            "verification_count",
            "manifest_artifact_written_count",
            "verification_artifact_written_count",
        )
    ) == (1, 1, 1, 1, 1, 1, 1)
    assert manifest_path.is_file()
    assert verification_path.is_file()
    assert manifest["manifest_core_hash"] == crypto["manifest_core_hash"]
    assert manifest["manifest_core"]["source_package_ref"] == tmp_path.name
    assert manifest["manifest_core"]["ordered_source_file_refs"] == list(
        runner.crypto_collector.REQUIRED_SOURCE_FILE_REFS,
    )
    assert manifest["manifest_core"]["source_file_count"] == 9
    assert len(manifest["manifest_core"]["ordered_artifact_refs"]) == 19
    assert len(manifest["manifest_core"]["ordered_artifact_hashes"]) == 19
    selected_offer_id = report["semantic_to_contract_deterministic_bridge"][
        "semantic_recommendation_id"
    ]
    expected_semantic_suffix = selected_offer_id.rsplit(":", 1)[-1]
    assert (
        "airline_hold_commit_packet:semantic_causal:"
        f"{expected_semantic_suffix}"
    ) in manifest["manifest_core"]["ordered_artifact_refs"]
    assert manifest["manifest_core"]["source_package_ref"] == tmp_path.name
    assert "/" not in manifest["manifest_core"]["source_package_ref"]
    assert "\\" not in manifest["manifest_core"]["source_package_ref"]
    assert manifest["signature"] == {
        "algorithm": "NONE",
        "key_id": "",
        "mode": "UNSIGNED_PLACEHOLDER",
        "value": "",
        "verified": False,
    }
    assert verification["verification_status"] == (
        runner.crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert verification["expected_manifest_core_hash"] is None
    assert verification["external_anchor_supplied"] is False
    assert verification["external_anchor_verified"] is False
    assert summary["airline_crypto_artifact_seal_source_boundary"] == (
        runner._crypto_source_boundary(True)
    )
    assert "airline_crypto_artifact_seal_integration" not in summary
    assert crypto["manifest_core_hash"] not in summary_text
    assert runner.CRYPTO_MANIFEST_FILE not in summary.get("artifacts", {})
    assert runner.CRYPTO_VERIFICATION_FILE not in summary.get("artifacts", {})
    assert "manifest_core_hash" not in summary
    assert "verification_report" not in summary
    assert tuple(
        report["counter_table"][name]
        for name in (
            "deterministic_airline_collection_count",
            "ticket_purchase_corridor_execution_count",
            "airline_transaction_artifact_ledger_collection_count",
        )
    ) == (1, 1, 1)
    crypto_files = tuple(
        sorted(path.name for path in tmp_path.iterdir() if "crypto_artifact" in path.name)
    )
    assert crypto_files == tuple(
        sorted((runner.CRYPTO_MANIFEST_FILE, runner.CRYPTO_VERIFICATION_FILE)),
    )
    assert not any("collection_result" in path.name for path in tmp_path.iterdir())
    assert not any("replay" in path.name.lower() for path in tmp_path.iterdir())
    assert tuple(
        crypto[name]
        for name in (
            "provider_calls_added_by_crypto_count",
            "network_calls_added_by_crypto_count",
            "gemini_calls_added_by_crypto_count",
            "crypto_created_authority_count",
            "crypto_created_permission_count",
            "crypto_created_action_count",
            "real_world_effects_count",
        )
    ) == (0, 0, 0, 0, 0, 0, 0)
    json.dumps(runner._json_safe(report), ensure_ascii=False, sort_keys=True)
    assert all(
        crypto[name] is True
        for name in (
            "source_bytes_unchanged_after_audit",
            "source_bytes_unchanged_after_collection",
            "source_bytes_unchanged_after_write",
            "source_summary_frozen_before_crypto",
        )
    )
    assert crypto["source_summary_rewritten_after_crypto"] is False
    rendered = runner.render_tri_party_airline_live_semantic_lane_v01(report)
    assert "[AIRLINE CRYPTO ARTIFACT SEAL V0.1]" in rendered
    assert "not final Crypto PASS" in rendered
    assert "No Replay and no real-world effect." in rendered


def _assert_crypto_fail(report: Mapping[str, Any], reason: str) -> None:
    crypto = report["airline_crypto_artifact_seal_integration"]
    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert crypto["integration_status"] == runner.STATUS_FAIL_CLOSED
    assert reason in crypto["validation_errors"]
    assert crypto["anchored_pass_claimed"] is False


def test_crypto_gate_closed_preserves_lane_and_calls_no_crypto(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("audit called")),
    )
    monkeypatch.setattr(
        runner.crypto_collector,
        "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("crypto called")),
    )
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    assert report["final_status"] == runner.STATUS_PASS
    assert report["airline_crypto_artifact_seal_integration"]["integration_status"] == "NOT_RUN"
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


@pytest.mark.parametrize(
    ("case", "reason"),
    (
        ("lane_closed", runner.REASON_CRYPTO_LIVE_GATE_REQUIRED),
        ("causal_closed", runner.REASON_CRYPTO_CAUSAL_GATE_REQUIRED),
        ("missing_dir", runner.REASON_CRYPTO_ARTIFACT_DIR_REQUIRED),
        ("invalid_ref", runner.REASON_CRYPTO_SOURCE_PACKAGE_REF_INVALID),
        ("manifest_exists", runner.REASON_CRYPTO_TARGET_EXISTS),
        ("verification_exists", runner.REASON_CRYPTO_TARGET_EXISTS),
    ),
)
def test_crypto_preconditions_fail_before_provider_or_transaction(
    case: str,
    reason: str,
    monkeypatch,
    tmp_path: Path,
) -> None:
    env = _crypto_env(tmp_path)
    constraints = binding.build_client_constraints_preference_a_v01()
    if case == "lane_closed":
        env.pop(runner.ENV_LANE)
    elif case == "causal_closed":
        env.pop(runner.ENV_CAUSAL_BINDING)
    elif case == "missing_dir":
        env.pop(runner.ENV_ARTIFACT_DIR)
    elif case == "invalid_ref":
        env[runner.ENV_ARTIFACT_DIR] = "."
    else:
        (tmp_path / (
            runner.CRYPTO_MANIFEST_FILE
            if case == "manifest_exists"
            else runner.CRYPTO_VERIFICATION_FILE
        )).write_text("user", encoding="utf-8")
    monkeypatch.setattr(
        runner.deterministic_airline,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("transaction executed"),
        ),
    )

    def forbidden_provider(*args, **kwargs):
        raise AssertionError("provider called")

    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=env,
        provider=forbidden_provider,
        causal_constraints=constraints,
    )
    _assert_crypto_fail(report, reason)


def test_crypto_precondition_rejects_symlink_directory(
    tmp_path: Path,
) -> None:
    actual = tmp_path / "actual"
    actual.mkdir()
    selected = tmp_path / "selected"
    selected.symlink_to(actual, target_is_directory=True)
    env = _crypto_env(selected)
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=env,
        provider=_content_sensitive_causal_provider(),
        causal_constraints=binding.build_client_constraints_preference_a_v01(),
    )
    _assert_crypto_fail(report, runner.REASON_CRYPTO_ARTIFACT_DIR_SYMLINK)


@pytest.mark.parametrize("mutation", ("missing", "symlink", "directory"))
def test_crypto_source_snapshot_rejects_missing_symlink_or_nonregular_file(
    mutation: str,
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = runner._write_summary_artifacts

    def mutate_after_summary(artifact_dir, report, artifacts):
        original(artifact_dir, report, artifacts)
        target = artifact_dir / "secret_scan.json"
        target.unlink()
        if mutation == "symlink":
            external = tmp_path.parent / f"{tmp_path.name}_external_secret.json"
            external.write_text("{}", encoding="utf-8")
            target.symlink_to(external)
        elif mutation == "directory":
            target.mkdir()

    monkeypatch.setattr(runner, "_write_summary_artifacts", mutate_after_summary)
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(report, runner.REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED)
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


def test_crypto_required_source_order_mismatch_fails_closed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    required = list(runner.ledger_audit.REQUIRED_SOURCE_FILES)
    required[0], required[1] = required[1], required[0]
    monkeypatch.setattr(runner.ledger_audit, "REQUIRED_SOURCE_FILES", tuple(required))
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(report, runner.REASON_CRYPTO_SOURCE_SCOPE_MISMATCH)


def test_crypto_detects_source_mutation_during_e1_audit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = runner.ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01

    def mutating_audit(**kwargs):
        audit = original(**kwargs)
        summary_path = Path(kwargs["artifact_dir"]) / "summary.json"
        summary_path.write_bytes(summary_path.read_bytes() + b" ")
        return audit

    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        mutating_audit,
    )
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(
        report,
        runner.REASON_CRYPTO_SOURCE_BYTES_CHANGED_DURING_AUDIT,
    )


def test_crypto_e1_audit_exception_fails_closed_after_one_call(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls = 0

    def failed_audit(**kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("private")

    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        failed_audit,
    )
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(report, runner.REASON_CRYPTO_E1_AUDIT_FAILED)
    assert calls == 1
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


@pytest.mark.parametrize("mutation", ("failed", "foreign_dir", "wrong_geometry"))
def test_crypto_rejects_failed_foreign_or_wrong_geometry_e1_audit(
    mutation: str,
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = runner.ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01

    def changed_audit(**kwargs):
        audit = original(**kwargs)
        if mutation == "failed":
            return replace(
                audit,
                final_status=runner.STATUS_FAIL_CLOSED,
                validation_errors=("forced",),
            )
        if mutation == "foreign_dir":
            return replace(audit, source_artifact_dir="foreign")
        return replace(audit, actual_entry_count=18)

    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        changed_audit,
    )
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    expected = (
        runner.REASON_CRYPTO_E1_AUDIT_FOREIGN_DIR
        if mutation == "foreign_dir"
        else runner.REASON_CRYPTO_E1_AUDIT_FAILED
    )
    _assert_crypto_fail(report, expected)


@pytest.mark.parametrize(
    "mutation",
    ("missing_source", "wrong_source", "missing_ledger", "wrong_ledger"),
)
def test_crypto_requires_exact_hidden_typed_ledger_objects(
    mutation: str,
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = runner._collect_crypto_artifact_seal_integration_v01

    def mutate_before_crypto(**kwargs):
        integrated = kwargs["integrated_deterministic_report"]
        name = (
            "_airline_transaction_artifact_ledger_source_bundle_v0_1"
            if "source" in mutation
            else "_airline_transaction_artifact_ledger_v0_1"
        )
        setattr(integrated, name, object() if mutation.startswith("wrong") else None)
        return original(**kwargs)

    monkeypatch.setattr(
        runner,
        "_collect_crypto_artifact_seal_integration_v01",
        mutate_before_crypto,
    )
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(report, runner.REASON_CRYPTO_TYPED_SOURCE_MISSING)


@pytest.mark.parametrize("stage", ("identity", "c1", "c2"))
def test_crypto_source_identity_c1_or_c2_failure_stops_derived_writes(
    stage: str,
    monkeypatch,
    tmp_path: Path,
) -> None:
    if stage == "identity":
        monkeypatch.setattr(
            runner.ledger_collector,
            "build_airline_transaction_artifact_ledger_expected_identity_from_source_v01",
            lambda **kwargs: (_ for _ in ()).throw(ValueError("private")),
        )
        reason = runner.REASON_CRYPTO_EXPECTED_IDENTITY_FAILED
    elif stage == "c1":
        monkeypatch.setattr(
            runner.crypto_collector,
            "build_airline_crypto_artifact_seal_source_bundle_v01",
            lambda **kwargs: (_ for _ in ()).throw(ValueError("private")),
        )
        reason = runner.REASON_CRYPTO_C1_SOURCE_BUNDLE_FAILED
    else:
        monkeypatch.setattr(
            runner.crypto_collector,
            "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
            lambda **kwargs: object(),
        )
        reason = runner.REASON_CRYPTO_C2_RESULT_INVALID
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(report, reason)
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


@pytest.mark.parametrize("mutation", ("changed", "malformed"))
def test_crypto_c2_callback_observation_failure_is_fail_closed(
    mutation: str,
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = runner._read_crypto_source_snapshot_v01
    calls = 0

    def changed_third_snapshot(artifact_dir):
        nonlocal calls
        calls += 1
        rows = original(artifact_dir)
        if calls == 3:
            if mutation == "malformed":
                return []
            changed = list(rows)
            changed[-1] = (changed[-1][0], changed[-1][1] + b"changed")
            return tuple(changed)
        return rows

    monkeypatch.setattr(runner, "_read_crypto_source_snapshot_v01", changed_third_snapshot)
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(report, runner.REASON_CRYPTO_C2_RESULT_INVALID)


def test_crypto_pair_writer_rolls_back_first_file_when_second_open_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_open = Path.open

    def failing_open(path, *args, **kwargs):
        if path.name == runner.CRYPTO_VERIFICATION_FILE:
            raise OSError("private")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)
    with pytest.raises(ValueError, match=f"^{runner.REASON_CRYPTO_DERIVED_WRITE_FAILED}$"):
        runner._write_crypto_artifact_pair_v01(
            artifact_dir=tmp_path,
            manifest_payload={"kind": "manifest"},
            verification_payload={"kind": "verification"},
        )
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


class _PartialWriteHandle:
    def __init__(self, handle) -> None:
        self._handle = handle

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self._handle.close()
        return False

    def write(self, text: str) -> int:
        written = self._handle.write(text[: max(1, len(text) // 2)])
        self._handle.flush()
        raise OSError("private partial write")


def test_crypto_fresh_package_rejects_existing_contents_without_changes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    summary_path = tmp_path / "summary.json"
    unrelated_path = tmp_path / "operator-note.txt"
    summary_bytes = b'{"sentinel":true}'
    unrelated_bytes = b"operator-owned"
    summary_path.write_bytes(summary_bytes)
    unrelated_path.write_bytes(unrelated_bytes)
    monkeypatch.setattr(
        runner,
        "_run_provider_lane",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("provider lane ran")),
    )
    monkeypatch.setattr(
        runner.deterministic_airline,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("transaction ran"),
        ),
    )
    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("audit ran")),
    )
    monkeypatch.setattr(
        runner.crypto_collector,
        "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Crypto C ran")),
    )

    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_crypto_env(tmp_path),
        provider=lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("provider called"),
        ),
        causal_constraints=binding.build_client_constraints_preference_a_v01(),
    )

    _assert_crypto_fail(report, runner.REASON_CRYPTO_ARTIFACT_DIR_NOT_EMPTY)
    assert summary_path.read_bytes() == summary_bytes
    assert unrelated_path.read_bytes() == unrelated_bytes


def test_crypto_partial_manifest_write_cleans_both_targets(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_open = Path.open

    def partial_manifest_open(path, *args, **kwargs):
        handle = original_open(path, *args, **kwargs)
        if path.name == runner.CRYPTO_MANIFEST_FILE:
            return _PartialWriteHandle(handle)
        return handle

    monkeypatch.setattr(Path, "open", partial_manifest_open)
    with pytest.raises(
        ValueError,
        match=f"^{runner.REASON_CRYPTO_DERIVED_WRITE_FAILED}$",
    ):
        runner._write_crypto_artifact_pair_v01(
            artifact_dir=tmp_path,
            manifest_payload={"kind": "manifest"},
            verification_payload={"kind": "verification"},
        )
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


def test_crypto_partial_verification_write_cleans_both_targets(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_open = Path.open

    def partial_verification_open(path, *args, **kwargs):
        handle = original_open(path, *args, **kwargs)
        if path.name == runner.CRYPTO_VERIFICATION_FILE:
            return _PartialWriteHandle(handle)
        return handle

    monkeypatch.setattr(Path, "open", partial_verification_open)
    with pytest.raises(
        ValueError,
        match=f"^{runner.REASON_CRYPTO_DERIVED_WRITE_FAILED}$",
    ):
        runner._write_crypto_artifact_pair_v01(
            artifact_dir=tmp_path,
            manifest_payload={"kind": "manifest"},
            verification_payload={"kind": "verification"},
        )
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


def test_crypto_post_write_text_mismatch_cleans_both_targets(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_read_text = Path.read_text

    def mismatched_read_text(path, *args, **kwargs):
        text = original_read_text(path, *args, **kwargs)
        if path.name == runner.CRYPTO_MANIFEST_FILE:
            return text + " "
        return text

    monkeypatch.setattr(Path, "read_text", mismatched_read_text)
    with pytest.raises(
        ValueError,
        match=f"^{runner.REASON_CRYPTO_DERIVED_REREAD_FAILED}$",
    ):
        runner._write_crypto_artifact_pair_v01(
            artifact_dir=tmp_path,
            manifest_payload={"kind": "manifest"},
            verification_payload={"kind": "verification"},
        )
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()


def test_crypto_cleanup_failure_has_dedicated_reason(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_open = Path.open
    original_unlink = Path.unlink

    def partial_verification_open(path, *args, **kwargs):
        handle = original_open(path, *args, **kwargs)
        if path.name == runner.CRYPTO_VERIFICATION_FILE:
            return _PartialWriteHandle(handle)
        return handle

    def failed_cleanup(path, *args, **kwargs):
        if path.name in {
            runner.CRYPTO_MANIFEST_FILE,
            runner.CRYPTO_VERIFICATION_FILE,
        }:
            raise OSError("private cleanup failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", partial_verification_open)
    monkeypatch.setattr(Path, "unlink", failed_cleanup)
    with pytest.raises(
        ValueError,
        match=f"^{runner.REASON_CRYPTO_DERIVED_CLEANUP_FAILED}$",
    ):
        runner._write_crypto_artifact_pair_v01(
            artifact_dir=tmp_path,
            manifest_payload={"kind": "manifest"},
            verification_payload={"kind": "verification"},
        )


def test_crypto_final_source_change_removes_derived_pair_without_repair(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_pair_writer = runner._write_crypto_artifact_pair_v01
    changed_summary: list[bytes] = []

    def mutating_pair_writer(**kwargs):
        paths = original_pair_writer(**kwargs)
        summary_path = kwargs["artifact_dir"] / "summary.json"
        changed = summary_path.read_bytes() + b" "
        summary_path.write_bytes(changed)
        changed_summary.append(changed)
        return paths

    monkeypatch.setattr(
        runner,
        "_write_crypto_artifact_pair_v01",
        mutating_pair_writer,
    )
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(
        report,
        runner.REASON_CRYPTO_SOURCE_BYTES_CHANGED_AFTER_WRITE,
    )
    assert not (tmp_path / runner.CRYPTO_MANIFEST_FILE).exists()
    assert not (tmp_path / runner.CRYPTO_VERIFICATION_FILE).exists()
    assert runner.CRYPTO_MANIFEST_FILE not in report["artifacts"]
    assert runner.CRYPTO_VERIFICATION_FILE not in report["artifacts"]
    assert (tmp_path / "summary.json").read_bytes() == changed_summary[0]


def test_crypto_failure_renderer_makes_no_self_consistency_claim() -> None:
    deterministic_context = (
        runner.deterministic_airline
        .build_tri_party_airline_semantic_source_context_v01()
    )
    report = runner._fail_closed_report(
        reason="causal_constraints_required",
        provider_mode=runner.PROVIDER_MODE_SKIPPED,
        model=runner.DEFAULT_MODEL,
        deterministic_report=deterministic_context,
        crypto_requested=True,
    )
    report["airline_crypto_artifact_seal_integration"]["signature_verified"] = 1
    rendered = runner.render_tri_party_airline_live_semantic_lane_v01(report)
    assert "Crypto integration failed closed" in rendered
    assert "Internally self-consistent and unanchored" not in rendered
    assert "signature verified: invalid" in rendered


def test_crypto_missing_causal_constraints_preserves_requested_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        runner,
        "_run_provider_lane",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("provider lane ran")),
    )
    monkeypatch.setattr(
        runner.deterministic_airline,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("transaction ran"),
        ),
    )
    report = runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=_crypto_env(tmp_path),
        provider=lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("provider called"),
        ),
    )
    crypto = report["airline_crypto_artifact_seal_integration"]
    assert report["validation_errors"] == ("causal_constraints_required",)
    assert report["failed_stage"] == "crypto_upstream_lane"
    assert report["airline_crypto_artifact_seal_source_boundary"][
        "integration_requested"
    ] is True
    assert crypto["integration_status"] == runner.STATUS_FAIL_CLOSED
    assert crypto["integration_status"] != "NOT_RUN"
    assert crypto["validation_errors"] == (
        runner.REASON_CRYPTO_UPSTREAM_LANE_FAILED,
    )


def test_crypto_source_transaction_failure_does_not_call_e1_audit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    audit_calls = 0

    def forbidden_audit(**kwargs):
        nonlocal audit_calls
        audit_calls += 1
        raise AssertionError("audit called")

    monkeypatch.setattr(
        runner,
        "_scan_secret_markers",
        lambda *args, **kwargs: {
            "passed": False,
            "matched_markers": ("forced",),
            "files_scanned": 0,
        },
    )
    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        forbidden_audit,
    )
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    crypto = report["airline_crypto_artifact_seal_integration"]
    _assert_crypto_fail(report, runner.REASON_CRYPTO_SOURCE_TRANSACTION_FAILED)
    assert runner.REASON_CRYPTO_E1_AUDIT_FAILED not in crypto["validation_errors"]
    assert crypto["e1_audit_count"] == 0
    assert audit_calls == 0


@pytest.mark.parametrize(
    ("payload", "reason"),
    (
        ([], runner.REASON_CRYPTO_DERIVED_PAYLOAD_INVALID),
        ({"marker": "GEMINI_API_KEY"}, runner.REASON_CRYPTO_DERIVED_SECRET_MARKER),
    ),
)
def test_crypto_payload_serialization_and_secret_boundary(
    payload: object,
    reason: str,
) -> None:
    with pytest.raises(ValueError, match=f"^{reason}$"):
        runner._crypto_payload_text_v01(payload)


def test_crypto_detects_source_change_during_derived_write(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = runner._write_crypto_artifact_pair_v01

    def mutating_pair(**kwargs):
        paths = original(**kwargs)
        summary = kwargs["artifact_dir"] / "summary.json"
        summary.write_bytes(summary.read_bytes() + b" ")
        return paths

    monkeypatch.setattr(runner, "_write_crypto_artifact_pair_v01", mutating_pair)
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    _assert_crypto_fail(
        report,
        runner.REASON_CRYPTO_SOURCE_BYTES_CHANGED_AFTER_WRITE,
    )


def test_crypto_slice_d_exact_stage_order_and_single_invocations(
    monkeypatch,
    tmp_path: Path,
) -> None:
    order: list[str] = []
    originals = {
        "audit": runner.ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01,
        "c2": runner.crypto_collector.collect_airline_crypto_artifact_seal_from_source_bundle_v01,
        "pair": runner._write_crypto_artifact_pair_v01,
    }

    def audit_wrapper(**kwargs):
        order.append("audit")
        return originals["audit"](**kwargs)

    def c2_wrapper(**kwargs):
        order.append("c2")
        return originals["c2"](**kwargs)

    def pair_wrapper(**kwargs):
        order.append("pair")
        return originals["pair"](**kwargs)

    monkeypatch.setattr(
        runner.ledger_audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        audit_wrapper,
    )
    monkeypatch.setattr(
        runner.crypto_collector,
        "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
        c2_wrapper,
    )
    monkeypatch.setattr(runner, "_write_crypto_artifact_pair_v01", pair_wrapper)
    report = _crypto_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )
    assert report["final_status"] == runner.STATUS_PASS
    assert order == ["audit", "c2", "pair"]


def test_crypto_slice_d_a_b_a_and_b_a_b_are_isolated(tmp_path: Path) -> None:
    offer_a = binding.build_client_constraints_preference_a_v01
    offer_b = binding.build_client_constraints_preference_b_v01
    hashes: list[str] = []
    offers: list[str] = []
    statuses: list[str] = []
    for index, factory in enumerate((offer_a, offer_b, offer_a, offer_b, offer_a, offer_b)):
        package = tmp_path / f"run_{index}" / "package"
        report = _crypto_report_for_preference(factory(), package)
        hashes.append(report["airline_crypto_artifact_seal_integration"]["manifest_core_hash"])
        statuses.append(
            report["airline_crypto_artifact_seal_integration"][
                "integration_status"
            ],
        )
        offers.append(
            report["semantic_to_contract_deterministic_bridge"][
                "semantic_recommendation_id"
            ],
        )
    assert offers == [
        binding.OFFER_A_ID,
        binding.OFFER_B_ID,
        binding.OFFER_A_ID,
        binding.OFFER_B_ID,
        binding.OFFER_A_ID,
        binding.OFFER_B_ID,
    ]
    assert statuses == [
        runner.crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    ] * 6
    assert all(len(value) == 64 and value == value.lower() for value in hashes)
    assert len(set(hashes)) == 6


def test_crypto_slice_d_static_boundaries() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported_roots.isdisjoint(
        {"cryptography", "Crypto", "config", "requests", "urllib"},
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"glob", "rglob"}
        for node in ast.walk(tree)
    )
    integration = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_collect_crypto_artifact_seal_integration_v01"
    )
    audit_calls = [
        node
        for node in ast.walk(integration)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr
        == "collect_airline_transaction_artifact_ledger_audit_v01"
    ]
    assert len(audit_calls) == 1
    c2_call = next(
        node
        for node in ast.walk(integration)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr
        == "collect_airline_crypto_artifact_seal_from_source_bundle_v01"
    )
    anchor_keyword = next(
        keyword
        for keyword in c2_call.keywords
        if keyword.arg == "expected_manifest_core_hash"
    )
    assert isinstance(anchor_keyword.value, ast.Constant)
    assert anchor_keyword.value.value is None
    assert "ENV_EXPECTED_MANIFEST_CORE_HASH" not in source
    assert "rglob(" not in source
    assert "latest directory" not in source.lower()
    assert "airline_transaction_artifact_ledger_slice_e2_offline" not in source
    assert ".tmp/" not in source


def test_slice_d_live_forced_secret_scan_failure_writes_no_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        runner,
        "SECRET_MARKERS",
        tuple(runner.SECRET_MARKERS) + ("airline_transaction_artifact_ledger",),
    )

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["failed_stage"] == "secret_scan"
    assert report["counter_table"][
        "airline_transaction_artifact_ledger_artifact_written_count"
    ] == 0
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_duplicate_ledger_write_is_blocked(tmp_path: Path) -> None:
    ledger_path = tmp_path / "airline_transaction_artifact_ledger.json"
    ledger_path.write_text("{}")

    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "airline_transaction_artifact_ledger_duplicate_write_blocked" in (
        report["validation_errors"]
    )
    assert ledger_path.read_text() == "{}"


def test_slice_d_live_ledger_write_io_failure_fails_closed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_open = Path.open

    def failing_open(self, *args, **kwargs):
        if self.name == "airline_transaction_artifact_ledger.json":
            raise OSError("blocked ledger write")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
        tmp_path,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "airline_transaction_artifact_ledger_write_failed" in (
        report["validation_errors"]
    )
    assert not (tmp_path / "airline_transaction_artifact_ledger.json").exists()


def test_slice_d_live_omitted_artifact_directory_writes_zero_ledgers() -> None:
    report = _causal_report_for_preference(
        binding.build_client_constraints_preference_a_v01(),
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert report["counter_table"][
        "airline_transaction_artifact_ledger_artifact_written_count"
    ] == 0


def test_slice_d_live_no_silent_bsep_fallback_source_patterns() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert 'get("projection_ref") or' not in source
    assert "fallback_projection" not in source
    assert "fixture_bsep_projection" not in source


def test_slice_d_changed_production_files_preserve_source_boundaries() -> None:
    changed_sources = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            runner.deterministic_airline.corridor_runtime.__file__,
            runner.deterministic_airline.__file__,
            runner.__file__,
        )
    )

    forbidden_snippets = (
        "import config",
        "from config",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import openai",
        "from openai",
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "import hashlib",
        "sha256",
        "Crypto Artifact Seal",
        "Replay Verifier",
        "hash chain",
        "class GenericLedger",
        "universal ledger",
    )
    for snippet in forbidden_snippets:
        assert snippet not in changed_sources
    assert "airline_transaction_artifact_ledger.json" in changed_sources
    assert "AirlineTransactionArtifactLedgerV01" not in Path(
        runner.deterministic_airline.corridor_runtime.__file__,
    ).read_text(encoding="utf-8")
