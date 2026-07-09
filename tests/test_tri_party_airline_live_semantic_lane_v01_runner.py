from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from demo import run_tri_party_airline_live_semantic_lane_v01 as runner


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
    assert "from hedgehog" not in source
    assert "import hedgehog" not in source
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
