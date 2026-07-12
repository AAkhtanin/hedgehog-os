from __future__ import annotations

import ast
import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from demo import (
    run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01
    as story,
)


REAL_ARTIFACT_DIR = Path(
    ".tmp/tri_party_airline_live_semantic_causal_all_real/"
    "tri_party_airline_live_semantic_causal_all_real_preference_a_20260712_084540"
)
REAL_AUDIT_LOG = Path(story.DEFAULT_AUDIT_LOG)


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(artifact_dir: Path) -> dict[str, str]:
    return {
        name: hashlib.sha256((artifact_dir / name).read_bytes()).hexdigest()
        for name in story.EXPECTED_EVIDENCE_SHA256
    }


def _env(artifact_dir: Path, audit_log: Path, **extra: str) -> dict[str, str]:
    env = {
        story.ENV_ARTIFACT_DIR: str(artifact_dir),
        story.ENV_AUDIT_LOG: str(audit_log),
    }
    env.update(extra)
    return env


def _actor_side(actor_id: str) -> str:
    if actor_id.startswith("client_"):
        return "client"
    if actor_id.startswith("airline_"):
        return "airline"
    if actor_id.startswith("bank_"):
        return "bank"
    if actor_id.startswith("tri_party_evidence"):
        return "cross_root_advisory"
    return "transaction"


def _base_counter_table() -> dict[str, int | float]:
    counters = dict(story.SOURCE_COUNTER_EXPECTATIONS)
    counters.update(
        {
            "semantic_actor_validation_pass_count": 12,
            "semantic_actor_validation_fail_count": 0,
            "bsep_created_count": 1,
            "bsep_validated_count": 1,
            "bsep_side_projection_count": 4,
            "provider_output_used_as_truth_count": 0,
            "provider_output_used_as_authority_count": 0,
            "real_provider_call_delay_applied_count": 12,
            "real_provider_call_delay_seconds": 30.0,
        },
    )
    return counters


def _actor_report(actor_id: str, index: int) -> dict[str, object]:
    return {
        "actor_id": actor_id,
        "actor_index": index,
        "side": _actor_side(actor_id),
        "provider_mode": "real_provider",
        "validation_status": "PASS",
        "accepted": True,
        "input_context_summary": f"bounded source summary for {actor_id}",
        "output_semantic_summary": f"provider semantic summary for {actor_id}",
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


def _canonical(actor_id: str) -> dict[str, object]:
    return {
        "actor_id": actor_id,
        "side": _actor_side(actor_id),
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "validation_status": "PASS",
        "semantic_summary": f"canonical summary for {actor_id}",
        "what_runtime_used": [f"used canonical {actor_id}"],
        "what_runtime_rejected": [
            "runtime_computed: provider output as truth",
            "runtime_computed: provider output as authority",
        ],
    }


def _actor_validation() -> dict[str, object]:
    return {"validation_status": "PASS", "accepted": True, "errors": []}


def _actor_extracted(actor_id: str) -> dict[str, object]:
    return {
        "actor_id": actor_id,
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "semantic_summary": f"extracted provider summary for {actor_id}",
        "authority_created": False,
        "action_permission_created": False,
        "real_world_effects_count": 0,
    }


def _bsep_packet() -> dict[str, object]:
    return {
        "bsep_packet_id": "tri_party_airline_bsep_packet:tri_airline_purchase:PAR-LIM:2026-08-12:client_001",
        "source_orchestrator_actor_id": story.ACTOR_IDS[0],
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "validation_status": "PASS",
        "raw_passport_included": False,
        "raw_card_included": False,
        "raw_iban_included": False,
        "raw_payment_token_included": False,
        "raw_private_profile_included": False,
        "raw_provider_text_included": False,
        "raw_response_dump_included": False,
        "authority_created": False,
        "action_permission_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
    }


def _bsep_projections() -> dict[str, object]:
    packet_id = _bsep_packet()["bsep_packet_id"]
    return {
        "client_bsep_projection": {
            "projection_ref": "client_bsep_projection",
            "side": "client",
            "source_bsep_packet_id": packet_id,
            "transaction_id": story.EXPECTED_TRANSACTION_ID,
            "validation_status": "PASS",
            "raw_secrets_included": False,
            "raw_provider_text_included": False,
        },
        "airline_bsep_projection": {
            "projection_ref": f"bsep_projection:airline_offer_selection:001:{packet_id}",
            "side": "airline",
            "source_bsep_packet_id": packet_id,
            "transaction_id": story.EXPECTED_TRANSACTION_ID,
            "validation_status": "PASS",
            "raw_secrets_included": False,
            "raw_provider_text_included": False,
        },
        "bank_bsep_projection": {
            "projection_ref": "bank_bsep_projection",
            "side": "bank",
            "source_bsep_packet_id": packet_id,
            "transaction_id": story.EXPECTED_TRANSACTION_ID,
            "validation_status": "PASS",
            "raw_secrets_included": False,
            "raw_provider_text_included": False,
        },
        "cross_root_bsep_projection": {
            "projection_ref": "cross_root_bsep_projection",
            "side": "cross_root",
            "source_bsep_packet_id": packet_id,
            "transaction_id": story.EXPECTED_TRANSACTION_ID,
            "validation_status": "PASS",
            "raw_secrets_included": False,
            "raw_provider_text_included": False,
        },
    }


def _causal_run() -> dict[str, object]:
    offer = story.EXPECTED_OFFER_ID
    source_bsep_ref = _bsep_projections()["airline_bsep_projection"]["projection_ref"]
    proposal = {
        "proposal_id": "client_purchase_intent_reviewer_llm:proposal:001",
        "actor_id": "client_purchase_intent_reviewer_llm",
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "source_selection_input_id": "selection_input:airline:PAR-LIM:001",
        "source_bsep_projection_ref": source_bsep_ref,
        "source_client_constraint_set_id": "client_constraints:client_001:preference_a",
        "source_candidate_set_snapshot_id": "candidate_snapshot:mock_airline_al:PAR-LIM:001",
        "source_candidate_set_digest": "digest:001",
        "candidate_set_ref": "candidate_set:mock_airline_al:PAR-LIM:2026-08-12:v01",
        "recommended_offer_id": offer,
        "ranked_offer_ids": [offer, "offer:mock_airline_al:PAR-LIM:002"],
        "decision_factors": ["lower price", "window seat"],
        "preference_matches": ["lower price matched", "window matched"],
        "uncertainty_notes": ["Recommendation remains advisory and requires ClientRoot review."],
        "requires_root_review": True,
        "semantic_summary": "Offer 001 matches the lower price and window seat preference.",
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
    actor_reviews = []
    for actor_id in story.CAUSAL_ACTOR_IDS:
        actor_reviews.append(
            {
                "canonical_actor_output_id": f"canonical:{actor_id}",
                "transaction_id": story.EXPECTED_TRANSACTION_ID,
                "actor_id": actor_id,
                "source_selection_input_id": "selection_input:airline:PAR-LIM:001",
                "source_candidate_set_snapshot_id": "candidate_snapshot:mock_airline_al:PAR-LIM:001",
                "source_candidate_set_digest": "digest:001",
                "reviewed_offer_id": offer,
                "review_role": "proposer" if actor_id == "client_purchase_intent_reviewer_llm" else "reviewer",
                "review_status": "PASS",
                "semantic_factors": [f"{actor_id} supports Offer 001"],
                "blocking_conflicts": [],
                "supports_proposed_offer": True,
                "validation_status": "PASS",
                "raw_output_used": False,
                "authority_created": False,
                "permission_created": False,
                "real_world_effects_count": 0,
            },
        )
    return {
        "run_id": "airline_semantic_to_contract_causal_runtime_v01",
        "final_status": "LOCAL_MODEL_PASS",
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "validation_errors": [],
        "semantic_recommendation_id": offer,
        "root_selected_offer_id": offer,
        "hold_contract_offer_id": offer,
        "provider_created_authority_count": 0,
        "provider_created_contract_count": 0,
        "real_world_effects_count": 0,
        "proposal": proposal,
        "proposer_request": {
            "transaction_id": story.EXPECTED_TRANSACTION_ID,
            "source_bsep_projection_ref": source_bsep_ref,
            "source_selection_input_id": "selection_input:airline:PAR-LIM:001",
            "visible_candidate_ids": [
                offer,
                "offer:mock_airline_al:PAR-LIM:002",
                "offer:mock_airline_al:PAR-LIM:003",
            ],
            "client_hard_compatible_candidate_ids": [
                offer,
                "offer:mock_airline_al:PAR-LIM:002",
            ],
            "client_hard_constraints": {
                "max_amount": 840,
                "currency": "EUR",
                "baggage_required": True,
                "avoid_overnight_layover": True,
            },
            "client_soft_preferences": {
                "preferred_seat_characteristics": ["window"],
                "soft_preference_priority": ["lower_price", "window_seat"],
                "changeable_preferred": True,
            },
            "authoritative_candidate_projection": [
                {
                    "offer_id": offer,
                    "amount": 782,
                    "currency": "EUR",
                    "baggage_included": True,
                    "seat_characteristics": ["window", "standard"],
                    "changeable": True,
                    "overnight_layover": False,
                },
                {
                    "offer_id": "offer:mock_airline_al:PAR-LIM:002",
                    "amount": 806,
                    "currency": "EUR",
                    "baggage_included": True,
                    "seat_characteristics": ["extra_legroom", "aisle"],
                    "changeable": True,
                    "overnight_layover": False,
                },
                {
                    "offer_id": "offer:mock_airline_al:PAR-LIM:003",
                    "amount": 741,
                    "currency": "EUR",
                    "baggage_included": False,
                    "seat_characteristics": ["middle"],
                    "changeable": True,
                    "overnight_layover": True,
                },
            ],
        },
        "actor_reviews": actor_reviews,
        "synthesis": {
            "synthesis_status": "PASS",
            "canonical_actor_output_refs": [f"canonical:{actor}" for actor in story.CAUSAL_ACTOR_IDS],
            "actor_recommended_offer_ids": [[actor, offer] for actor in story.CAUSAL_ACTOR_IDS],
            "actor_conflicts": [],
            "unresolved_conflict_present": False,
            "accepted_semantic_factors": ["all_canonical_actor_outputs_support_offer"],
            "rejected_semantic_factors": ["raw_sibling_outputs"],
            "what_runtime_used": ["canonical_actor_outputs", "explicit_recommended_offer_id"],
            "what_runtime_rejected": ["raw_actor_outputs", "provider_authority"],
        },
        "canonical_evidence": {
            "validation_status": "PASS",
            "canonical_selection_id": f"canonical_selection:{offer}",
            "source_proposal_id": proposal["proposal_id"],
            "source_actor_id": proposal["actor_id"],
            "recommended_offer_id": offer,
            "what_runtime_used": ["accepted_validated_recommendation_id"],
            "what_runtime_rejected": ["provider_output_as_truth_rejected"],
            "real_world_effects_count": 0,
        },
        "client_root_decision": {"selected_offer_id": offer},
        "airline_root_resolution": {"selected_offer_id": offer},
        "hold_packet": {"offer_id": offer},
    }


def _bridge() -> dict[str, object]:
    offer = story.EXPECTED_OFFER_ID
    bsep_ref = _bsep_projections()["airline_bsep_projection"]["projection_ref"]
    return {
        "bridge_status": "PASS",
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "semantic_recommendation_id": offer,
        "client_root_selected_offer_id": offer,
        "airline_root_resolved_offer_id": offer,
        "hold_contract_offer_id": offer,
        "deterministic_transaction_offer_id": offer,
        "deterministic_corridor_offer_id": offer,
        "all_offer_ids_match": True,
        "actual_bsep_packet_id": _bsep_packet()["bsep_packet_id"],
        "actual_airline_bsep_projection_ref": bsep_ref,
        "causal_selection_bsep_projection_ref": bsep_ref,
        "bsep_refs_match": True,
        "causal_report_validation_accepted": True,
        "deterministic_report_final_status": "PASS",
        "deterministic_corridor_final_status": "PASS",
        "deterministic_collection_count": 1,
        "corridor_execution_count": 1,
        "direct_offer_override_used": False,
        "default_offer_used": False,
        "silent_fallback_used": False,
        "provider_created_authority_count": 0,
        "real_world_effects_count": 0,
        "semantic_actor_calls_total": 12,
        "causal_actor_calls_total": 5,
        "duplicate_actor_calls": 0,
    }


def _summary() -> dict[str, object]:
    reports = [_actor_report(actor_id, index) for index, actor_id in enumerate(story.ACTOR_IDS, start=1)]
    for report in reports:
        if report["actor_id"] in story.PARENT_BY_CHILD:
            report["parent_actor_id"] = story.PARENT_BY_CHILD[report["actor_id"]]
    return {
        "run_id": "tri_party_airline_live_semantic_lane_v01",
        "report_id": "tri_party_airline_live_semantic_lane_v01",
        "lane_id": "tri_party_airline_live_semantic_lane_v01_fake_provider",
        "final_status": "PASS",
        "provider_mode": "real_provider",
        "model": "gemini-2.5-flash",
        "validation_errors": [],
        "transaction_id": story.EXPECTED_TRANSACTION_ID,
        "semantic_actor_call_order": list(story.ACTOR_IDS),
        "semantic_actor_reports": reports,
        "counter_table": _base_counter_table(),
        "bsep_membrane": _bsep_packet(),
        "bsep_validation": {"validation_status": "PASS", "accepted": True, "errors": []},
        "bsep_side_projections": _bsep_projections(),
        "vertical_fractal_dependencies": [
            {
                "parent_actor_id": "airline_offer_policy_reviewer_llm",
                "child_actor_id": "airline_fare_rules_vertical_cell_llm",
                "parent_validation_status": "PASS",
                "child_started_after_parent_validation": True,
                "child_received_parent_canonical_summary": True,
                "child_received_parent_raw_response": False,
                "child_received_sibling_raw_output": False,
                "child_result_returns_to_parent_or_root_review": True,
            },
            {
                "parent_actor_id": "airline_offer_policy_reviewer_llm",
                "child_actor_id": "airline_seat_baggage_vertical_cell_llm",
                "parent_validation_status": "PASS",
                "child_started_after_parent_validation": True,
                "child_received_parent_canonical_summary": True,
                "child_received_parent_raw_response": False,
                "child_received_sibling_raw_output": False,
                "child_result_returns_to_parent_or_root_review": True,
            },
            {
                "parent_actor_id": "bank_payment_policy_reviewer_llm",
                "child_actor_id": "bank_idempotency_risk_vertical_cell_llm",
                "parent_validation_status": "PASS",
                "child_started_after_parent_validation": True,
                "child_received_parent_canonical_summary": True,
                "child_received_parent_raw_response": False,
                "child_received_sibling_raw_output": False,
                "child_result_returns_to_parent_or_root_review": True,
            },
        ],
        "root_boundaries": [
            {"boundary": "ClientRoot", "boundary_preserved": True, "violation_count": 0},
            {"boundary": "AirlineRoot", "boundary_preserved": True, "violation_count": 0},
            {"boundary": "BankRoot", "boundary_preserved": True, "violation_count": 0},
            {"boundary": "cross-root reviewer advisory", "boundary_preserved": True, "violation_count": 0},
        ],
    }


def _write_fixture(tmp_path: Path, monkeypatch, mutate=None, patch_hashes: bool = True) -> tuple[Path, Path]:
    artifact_dir = tmp_path / story.EXPECTED_SOURCE_RUN_NAME
    artifact_dir.mkdir(parents=True)
    audit_log = tmp_path / "audit.log"
    payloads: dict[str, dict[str, object]] = {
        "all_real_operator_gate_check.json": {
            "final_status": "PASS",
            "provider_mode": "real_provider",
            "all_checks_pass": True,
            "selected_offer": story.EXPECTED_OFFER_ID,
            "missing_actor_artifacts": [],
            "missing_integrated_artifacts": [],
            "actual_actor_order": list(story.ACTOR_IDS),
        },
        "summary.json": _summary(),
        "secret_scan.json": {"passed": True, "files_scanned": 67, "matched_markers": []},
        "semantic_to_contract_causal_run.json": _causal_run(),
        "semantic_to_contract_bridge.json": _bridge(),
        "integrated_deterministic_airline_summary.json": {
            "collection_status": "PASS",
            "corridor_final_status": "PASS",
            "corridor_execution_count": 1,
            "selected_offer_id": story.EXPECTED_OFFER_ID,
            "transaction_id": story.EXPECTED_TRANSACTION_ID,
            "real_world_effects_count": 0,
        },
        "tri_party_airline_bsep_packet.json": _bsep_packet(),
        "tri_party_airline_bsep_validation.json": {
            "validation_status": "PASS",
            "accepted": True,
            "errors": [],
        },
        "tri_party_airline_bsep_side_projections.json": _bsep_projections(),
    }
    for filename, payload in payloads.items():
        _write_json(artifact_dir / filename, payload)
    (artifact_dir / "summary.log").write_text("summary PASS\n", encoding="utf-8")
    (artifact_dir / "console.log").write_text("console PASS\n", encoding="utf-8")
    for index, actor_id in enumerate(story.ACTOR_IDS, start=1):
        (artifact_dir / f"{actor_id}_prompt.txt").write_text(
            f"prompt for {actor_id} index {index}",
            encoding="utf-8",
        )
        (artifact_dir / f"{actor_id}_raw_response.txt").write_text(
            f"raw response for {actor_id}",
            encoding="utf-8",
        )
        _write_json(artifact_dir / f"{actor_id}_extracted_json_candidate.json", _actor_extracted(actor_id))
        _write_json(artifact_dir / f"{actor_id}_validation.json", _actor_validation())
        _write_json(artifact_dir / f"{actor_id}_canonical_summary.json", _canonical(actor_id))
    audit_log.write_text(
        "\n".join(
            (
                f"audit_id: {story.EXPECTED_AUDIT_ID}",
                "audit_status: PASS",
                "observed_head: acc1350",
                f"source_run_name: {story.EXPECTED_SOURCE_RUN_NAME}",
                "provider_mode: real_provider",
                f"selected_offer_id: {story.EXPECTED_OFFER_ID}",
                "real_world_effects_count: 0",
                "transaction_artifact_ledger_implemented: false",
                "crypto_artifact_seal_implemented: false",
                "sealed_trace_replay_verifier_implemented: false",
            ),
        ),
        encoding="utf-8",
    )
    if mutate is not None:
        mutate(artifact_dir, audit_log)
    if patch_hashes:
        monkeypatch.setattr(story, "EXPECTED_EVIDENCE_SHA256", _hashes(artifact_dir))
    return artifact_dir, audit_log


def _collect(artifact_dir: Path, audit_log: Path, **extra: str) -> dict[str, object]:
    return story.collect_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log, **extra),
    )


def test_default_run_is_skipped_closed() -> None:
    report = story.collect_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(env={})
    assert report["final_status"] == story.SKIPPED_CLOSED
    assert report["counter_table"]["renderer_provider_called_count"] == 0


def test_valid_all_real_shaped_artifact_package_renders_pass(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    report = _collect(artifact_dir, audit_log)
    rendered = story.render_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(report)
    assert report["final_status"] == story.PASS
    assert "[FINAL STATUS]\nPASS" in rendered


def test_exact_twelve_actor_order_is_required(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        order = summary["semantic_actor_call_order"]
        order[0], order[1] = order[1], order[0]
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "summary_actor_order_mismatch" in report["validation_errors"]


def test_all_five_actor_artifacts_per_actor_are_required(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    (artifact_dir / f"{story.ACTOR_IDS[0]}_prompt.txt").unlink()
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert any("missing_actor_artifact" in error for error in report["validation_errors"])


def test_every_actor_validation_must_pass(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        path = artifact_dir / "client_purchase_intent_reviewer_llm_validation.json"
        payload = _read_json(path)
        payload["validation_status"] = "FAIL_CLOSED"
        _write_json(path, payload)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "actor_validation_not_pass:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_provider_mode_must_be_real_provider(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["provider_mode"] = "fake_provider"
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "summary_provider_mode_not_real_provider" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_fake_provider_call_count_must_be_zero(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["counter_table"]["fake_provider_call_count"] = 1
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "source_counter_mismatch:fake_provider_call_count" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_real_provider_gemini_network_counts_must_be_twelve(tmp_path: Path, monkeypatch) -> None:
    for key in ("real_provider_call_count", "gemini_called_count", "network_used_count"):
        def mutate(artifact_dir: Path, _audit_log: Path, key=key) -> None:
            summary = _read_json(artifact_dir / "summary.json")
            summary["counter_table"][key] = 11
            _write_json(artifact_dir / "summary.json", summary)

        artifact_dir, audit_log = _write_fixture(tmp_path / key, monkeypatch, mutate=mutate)
        assert f"source_counter_mismatch:{key}" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_bsep_must_pass_before_architect(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.PASS
    assert any("PASS occurred before Architect" in item for item in report["bsep_story"])


def test_all_four_bsep_projections_must_pass(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        projections = _read_json(artifact_dir / "tri_party_airline_bsep_side_projections.json")
        projections["bank_bsep_projection"]["validation_status"] = "FAIL_CLOSED"
        _write_json(artifact_dir / "tri_party_airline_bsep_side_projections.json", projections)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bsep_projection_not_pass:bank_bsep_projection" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_actual_live_airline_bsep_ref_must_match_causal_bsep_ref(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        bridge = _read_json(artifact_dir / "semantic_to_contract_bridge.json")
        bridge["causal_selection_bsep_projection_ref"] = "wrong"
        _write_json(artifact_dir / "semantic_to_contract_bridge.json", bridge)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bridge_bsep_refs_do_not_match" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_five_causal_actor_reviews_are_visible(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    report = _collect(artifact_dir, audit_log)
    assert len(report["causal_reviews"]) == 5
    assert len(report["causal_actor_cards"]) == 5


def test_synthesis_and_canonical_evidence_are_visible(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    synthesis = _collect(artifact_dir, audit_log)["synthesis_story"]
    assert synthesis["synthesis_status"] == "PASS"
    assert synthesis["canonical_selection_id"]


def test_canonical_evidence_is_bound_to_actual_proposer(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    synthesis = _collect(artifact_dir, audit_log)["synthesis_story"]
    assert synthesis["source_proposal_id"] == "client_purchase_intent_reviewer_llm:proposal:001"
    assert synthesis["source_actor_id"] == "client_purchase_intent_reviewer_llm"


def test_all_six_offer_references_independently_read_and_match(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    refs = _collect(artifact_dir, audit_log)["six_offer_references"]
    assert len(refs) == 6
    assert all(value == story.EXPECTED_OFFER_ID for value in refs.values())


def test_deterministic_collection_count_must_be_one(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        bridge = _read_json(artifact_dir / "semantic_to_contract_bridge.json")
        bridge["deterministic_collection_count"] = 2
        _write_json(artifact_dir / "semantic_to_contract_bridge.json", bridge)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "deterministic_collection_count_not_one" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_corridor_execution_count_must_be_one(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        integrated = _read_json(artifact_dir / "integrated_deterministic_airline_summary.json")
        integrated["corridor_execution_count"] = 2
        _write_json(artifact_dir / "integrated_deterministic_airline_summary.json", integrated)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "integrated_corridor_execution_count_not_one" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_duplicate_actor_call_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["semantic_actor_call_order"][-1] = summary["semantic_actor_call_order"][0]
        summary["counter_table"]["duplicate_semantic_actor_call_count"] = 1
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    errors = _collect(artifact_dir, audit_log)["validation_errors"]
    assert "duplicate_actor_call_detected" in errors


def test_duplicate_corridor_execution_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["counter_table"]["ticket_purchase_corridor_execution_count"] = 2
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "source_counter_mismatch:ticket_purchase_corridor_execution_count" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_direct_override_default_fallback_fails_closed(tmp_path: Path, monkeypatch) -> None:
    for flag in ("direct_offer_override_used", "default_offer_used", "silent_fallback_used"):
        def mutate(artifact_dir: Path, _audit_log: Path, flag=flag) -> None:
            bridge = _read_json(artifact_dir / "semantic_to_contract_bridge.json")
            bridge[flag] = True
            _write_json(artifact_dir / "semantic_to_contract_bridge.json", bridge)

        artifact_dir, audit_log = _write_fixture(tmp_path / flag, monkeypatch, mutate=mutate)
        assert f"bridge_forbidden_flag_true:{flag}" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_provider_authority_or_contract_claim_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        causal = _read_json(artifact_dir / "semantic_to_contract_causal_run.json")
        causal["provider_created_contract_count"] = 1
        _write_json(artifact_dir / "semantic_to_contract_causal_run.json", causal)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "provider_created_contract_nonzero" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_nonzero_real_effect_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["counter_table"]["real_world_effects_count"] = 1
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "source_counter_mismatch:real_world_effects_count" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_secret_scan_failure_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        secret = _read_json(artifact_dir / "secret_scan.json")
        secret["passed"] = False
        _write_json(artifact_dir / "secret_scan.json", secret)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "secret_scan_failed" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_wrong_source_directory_fails_closed(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    wrong_dir = tmp_path / "wrong_source_directory"
    artifact_dir.rename(wrong_dir)
    report = _collect(wrong_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "source_run_name_mismatch" in report["validation_errors"]


def test_hybrid_smoke_directory_fails_closed(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    smoke_dir = tmp_path / f"{story.EXPECTED_SOURCE_RUN_NAME}_proposer_smoke"
    artifact_dir.rename(smoke_dir)
    report = _collect(smoke_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert any(error.startswith("rejected_source_marker:proposer_smoke") for error in report["validation_errors"])


def test_evidence_fingerprint_mismatch_fails_closed(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    (artifact_dir / "summary.log").write_text("changed after expected hashes\n", encoding="utf-8")
    report = _collect(artifact_dir, audit_log)
    assert "evidence_fingerprint_mismatch:summary.log" in report["validation_errors"]


def test_malformed_json_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    (artifact_dir / "summary.json").write_text("{not json", encoding="utf-8")
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert any(error.startswith("json_unreadable:summary.json") for error in report["validation_errors"])


def test_non_object_json_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    (artifact_dir / "summary.json").write_text("[]", encoding="utf-8")
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "json_root_not_object:summary.json" in report["validation_errors"]


def test_semantic_actor_call_order_integer_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["semantic_actor_call_order"] = 7
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "semantic_actor_call_order_invalid" in report["validation_errors"]


def test_semantic_actor_call_order_containing_list_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["semantic_actor_call_order"][0] = ["not", "an", "actor"]
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "semantic_actor_call_order_invalid" in report["validation_errors"]


def test_semantic_actor_reports_list_actor_id_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["semantic_actor_reports"][0]["actor_id"] = ["bad"]
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "semantic_actor_report_actor_id_invalid" in report["validation_errors"]


def test_causal_actor_review_bad_actor_id_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    for bad_value in (["bad"], {"bad": "actor"}):
        def mutate(artifact_dir: Path, _audit_log: Path, bad_value=bad_value) -> None:
            causal = _read_json(artifact_dir / "semantic_to_contract_causal_run.json")
            causal["actor_reviews"][0]["actor_id"] = bad_value
            _write_json(artifact_dir / "semantic_to_contract_causal_run.json", causal)

        artifact_dir, audit_log = _write_fixture(tmp_path / str(type(bad_value).__name__), monkeypatch, mutate=mutate)
        report = _collect(artifact_dir, audit_log)
        assert report["final_status"] == story.FAIL_CLOSED
        assert "causal_actor_review_actor_id_invalid" in report["validation_errors"]


def test_what_runtime_used_object_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["what_runtime_used"] = {"not": "an array"}
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "canonical_what_runtime_used_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_canonical_semantic_summary_object_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["semantic_summary"] = {"malformed": "semantic object"}
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "actor_canonical_semantic_summary_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_canonical_semantic_summary_list_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["semantic_summary"] = ["malformed", "semantic", "list"]
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "actor_canonical_semantic_summary_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_extracted_semantic_summary_object_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        extracted = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_extracted_json_candidate.json")
        extracted["semantic_summary"] = {"malformed": "semantic object"}
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_extracted_json_candidate.json", extracted)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "actor_extracted_semantic_summary_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_extracted_semantic_summary_boolean_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        extracted = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_extracted_json_candidate.json")
        extracted["semantic_summary"] = True
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_extracted_json_candidate.json", extracted)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "actor_extracted_semantic_summary_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_canonical_side_list_or_object_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    for value in (["client"], {"side": "client"}):
        def mutate(artifact_dir: Path, _audit_log: Path, value=value) -> None:
            canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
            canonical["side"] = value
            _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

        artifact_dir, audit_log = _write_fixture(tmp_path / type(value).__name__, monkeypatch, mutate=mutate)
        report = _collect(artifact_dir, audit_log)
        assert report["final_status"] == story.FAIL_CLOSED
        assert "actor_side_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_input_context_summary_object_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        summary = _read_json(artifact_dir / "summary.json")
        summary["semantic_actor_reports"][2]["input_context_summary"] = {"bad": "summary"}
        _write_json(artifact_dir / "summary.json", summary)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert report["final_status"] == story.FAIL_CLOSED
    assert "actor_input_context_summary_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_causal_review_status_object_or_list_returns_fail_closed(tmp_path: Path, monkeypatch) -> None:
    for value in ({"status": "PASS"}, ["PASS"]):
        def mutate(artifact_dir: Path, _audit_log: Path, value=value) -> None:
            causal = _read_json(artifact_dir / "semantic_to_contract_causal_run.json")
            causal["actor_reviews"][0]["review_status"] = value
            _write_json(artifact_dir / "semantic_to_contract_causal_run.json", causal)

        artifact_dir, audit_log = _write_fixture(tmp_path / type(value).__name__, monkeypatch, mutate=mutate)
        report = _collect(artifact_dir, audit_log)
        assert report["final_status"] == story.FAIL_CLOSED
        assert "causal_review_status_invalid:client_purchase_intent_reviewer_llm" in report["validation_errors"]


def test_malformed_semantic_text_absent_from_minimal_fail_closed_rendering(tmp_path: Path, monkeypatch) -> None:
    marker = "MALFORMED SEMANTIC TEXT SHOULD NOT RENDER"

    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["semantic_summary"] = {"marker": marker}
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert "FAIL_CLOSED" in rendered
    assert marker not in rendered


def test_valid_string_semantic_summary_mutation_still_changes_pass_story(tmp_path: Path, monkeypatch) -> None:
    marker = "VALID SOURCE-DERIVED CANONICAL MUTATION"

    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["semantic_summary"] = marker
        extracted = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_extracted_json_candidate.json")
        extracted["semantic_summary"] = marker
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_extracted_json_candidate.json", extracted)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    rendered = story.render_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(report)
    assert report["final_status"] == story.PASS
    assert marker in rendered


def test_actor_card_builder_does_not_coerce_semantic_fields_with_str() -> None:
    source = Path(story.__file__).read_text(encoding="utf-8")
    actor_builder = source.split("def _build_actor_cards", 1)[1].split("def _hide_prompt_and_raw", 1)[0]
    forbidden = (
        'str(report.get("input_context_summary"',
        'str(\n                extracted.get("semantic_summary")',
        'str(canonical.get("semantic_summary"',
        'str(canonical.get("side")',
        '"provider_returned": str(',
        '"canonical_semantic_summary": str(',
    )
    for snippet in forbidden:
        assert snippet not in actor_builder


def test_invalid_utf8_prompt_or_raw_response_fails_closed_without_exception(tmp_path: Path, monkeypatch) -> None:
    cases = (
        "tri_party_airline_orchestrator_llm_prompt.txt",
        "tri_party_airline_orchestrator_llm_raw_response.txt",
    )
    for filename in cases:
        artifact_dir, audit_log = _write_fixture(tmp_path / filename, monkeypatch)
        (artifact_dir / filename).write_bytes(b"\xff\xfe\xfa")
        report = _collect(artifact_dir, audit_log)
        assert report["final_status"] == story.FAIL_CLOSED
        assert any(
            error.startswith(f"text_unreadable:{filename}:UnicodeDecodeError")
            for error in report["validation_errors"]
        )


def test_bsep_raw_passport_flag_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        packet = _read_json(artifact_dir / "tri_party_airline_bsep_packet.json")
        packet["raw_passport_included"] = True
        _write_json(artifact_dir / "tri_party_airline_bsep_packet.json", packet)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(artifact_dir, audit_log)
    assert "bsep_packet_forbidden_flag_true:raw_passport_included" in report["validation_errors"]


def test_bsep_raw_provider_text_flag_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        packet = _read_json(artifact_dir / "tri_party_airline_bsep_packet.json")
        packet["raw_provider_text_included"] = True
        _write_json(artifact_dir / "tri_party_airline_bsep_packet.json", packet)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bsep_packet_forbidden_flag_true:raw_provider_text_included" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_bsep_projection_raw_secrets_flag_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        projections = _read_json(artifact_dir / "tri_party_airline_bsep_side_projections.json")
        projections["airline_bsep_projection"]["raw_secrets_included"] = True
        _write_json(artifact_dir / "tri_party_airline_bsep_side_projections.json", projections)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bsep_projection_forbidden_flag_true:airline_bsep_projection:raw_secrets_included" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_bsep_projection_raw_provider_text_flag_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        projections = _read_json(artifact_dir / "tri_party_airline_bsep_side_projections.json")
        projections["airline_bsep_projection"]["raw_provider_text_included"] = True
        _write_json(artifact_dir / "tri_party_airline_bsep_side_projections.json", projections)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bsep_projection_forbidden_flag_true:airline_bsep_projection:raw_provider_text_included" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_bsep_projection_source_packet_id_mismatch_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        projections = _read_json(artifact_dir / "tri_party_airline_bsep_side_projections.json")
        projections["airline_bsep_projection"]["source_bsep_packet_id"] = "wrong_packet"
        _write_json(artifact_dir / "tri_party_airline_bsep_side_projections.json", projections)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bsep_projection_packet_id_mismatch:airline_bsep_projection" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_bsep_transaction_id_mismatch_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        packet = _read_json(artifact_dir / "tri_party_airline_bsep_packet.json")
        packet["transaction_id"] = "wrong_transaction"
        _write_json(artifact_dir / "tri_party_airline_bsep_packet.json", packet)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "bsep_packet_transaction_id_mismatch" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_standalone_bsep_contradicts_summary_bsep_fails_closed(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        packet = _read_json(artifact_dir / "tri_party_airline_bsep_packet.json")
        packet["raw_card_included"] = True
        _write_json(artifact_dir / "tri_party_airline_bsep_packet.json", packet)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    errors = _collect(artifact_dir, audit_log)["validation_errors"]
    assert "summary_bsep_packet_contradiction:raw_card_included" in errors


def test_fail_closed_render_does_not_claim_no_raw_data(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        packet = _read_json(artifact_dir / "tri_party_airline_bsep_packet.json")
        packet["raw_provider_text_included"] = True
        _write_json(artifact_dir / "tri_party_airline_bsep_packet.json", packet)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert "FAIL_CLOSED" in rendered
    assert "No raw passport, card, IBAN, payment token, or raw provider dump was included." not in rendered


def test_raw_responses_hidden_by_default(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert "raw response for tri_party_airline_orchestrator_llm" not in rendered
    assert "raw_response_displayed: False" in rendered


def test_prompts_hidden_by_default(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert "prompt for tri_party_airline_orchestrator_llm" not in rendered
    assert "prompt_displayed_in_full: False" in rendered


def test_transparency_mode_requires_passing_secret_scan(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        secret = _read_json(artifact_dir / "secret_scan.json")
        secret["passed"] = False
        _write_json(artifact_dir / "secret_scan.json", secret)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    report = _collect(
        artifact_dir,
        audit_log,
        **{story.ENV_ALLOW_RAW: "1", story.ENV_ALLOW_PROMPT: "1"},
    )
    assert report["final_status"] == story.FAIL_CLOSED
    assert report["counter_table"]["raw_responses_printed_count"] == 0
    assert report["counter_table"]["full_prompts_printed_count"] == 0


def test_semantic_story_text_changes_when_source_semantic_summary_changes(tmp_path: Path, monkeypatch) -> None:
    marker = "MUTATED SOURCE PROPOSER SUMMARY"

    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        causal = _read_json(artifact_dir / "semantic_to_contract_causal_run.json")
        causal["proposal"]["semantic_summary"] = marker
        _write_json(artifact_dir / "semantic_to_contract_causal_run.json", causal)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert marker in rendered


def test_reviewer_card_changes_when_source_semantic_factors_change(tmp_path: Path, monkeypatch) -> None:
    marker = "MUTATED REVIEWER FACTOR"

    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        causal = _read_json(artifact_dir / "semantic_to_contract_causal_run.json")
        causal["actor_reviews"][1]["semantic_factors"] = [marker]
        _write_json(artifact_dir / "semantic_to_contract_causal_run.json", causal)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert marker in rendered


def test_runtime_used_section_is_source_derived(tmp_path: Path, monkeypatch) -> None:
    marker = "MUTATED RUNTIME USED"

    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["what_runtime_used"] = [marker]
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert marker in rendered


def test_runtime_rejected_section_is_source_derived(tmp_path: Path, monkeypatch) -> None:
    marker = "MUTATED RUNTIME REJECTED"

    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        canonical = _read_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json")
        canonical["what_runtime_rejected"] = [marker]
        _write_json(artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json", canonical)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    assert marker in rendered


def test_russian_human_story_sections_are_present(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    rendered = story.run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        env=_env(artifact_dir, audit_log),
    )
    for section in (
        "[HEDGEHOG OS — AIRLINE ALL-REAL CAUSAL CORRIDOR HUMAN STORY]",
        "[ONE-SCREEN SUMMARY]",
        "[THE CLIENT REQUEST]",
        "[BOUNDED OFFER SET]",
        "[WHAT GEMINI RECOMMENDED]",
        "[BSEP MEMBRANE]",
        "[ALL 12 ACTOR CARDS]",
        "[HORIZONTAL SEMANTIC WORK]",
        "[VERTICAL FRACTAL WORK]",
        "[THE FIVE CAUSAL ACTORS]",
        "[MULTI-ACTOR SYNTHESIS]",
        "[HOW SEMANTICS CHANGED THE CONTRACT]",
        "[THE SIX OFFER REFERENCES]",
        "[THREE ROOTS, THREE AUTHORITY BOUNDARIES]",
        "[THE DETERMINISTIC TICKET/PURCHASE CORRIDOR]",
        "[WHAT RUNTIME USED]",
        "[WHAT RUNTIME REJECTED]",
        "[WHAT DID NOT HAPPEN]",
        "[PROVENANCE NOTE]",
        "[HONEST LIMITS]",
        "[FINAL STATUS]",
    ):
        assert section in rendered
    assert "Одна Airline mock-транзакция" in rendered


def test_changing_offer_reference_breaks_pass(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        bridge = _read_json(artifact_dir / "semantic_to_contract_bridge.json")
        bridge["deterministic_corridor_offer_id"] = "offer:mock_airline_al:PAR-LIM:002"
        _write_json(artifact_dir / "semantic_to_contract_bridge.json", bridge)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "six_offer_reference_mismatch:actual_corridor_contract_context_offer" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_changing_bsep_lineage_breaks_pass(tmp_path: Path, monkeypatch) -> None:
    def mutate(artifact_dir: Path, _audit_log: Path) -> None:
        bridge = _read_json(artifact_dir / "semantic_to_contract_bridge.json")
        bridge["actual_airline_bsep_projection_ref"] = "wrong"
        _write_json(artifact_dir / "semantic_to_contract_bridge.json", bridge)

    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch, mutate=mutate)
    assert "actual_live_airline_bsep_ref_mismatch" in _collect(artifact_dir, audit_log)["validation_errors"]


def test_renderer_does_not_import_or_call_live_semantic_runner() -> None:
    source = Path(story.__file__).read_text(encoding="utf-8")
    assert "run_tri_party_airline_live_semantic_lane_v01" not in source
    assert "collect_tri_party_airline_live_semantic_lane_v01" not in source


def test_renderer_does_not_import_or_call_deterministic_airline_runner() -> None:
    source = Path(story.__file__).read_text(encoding="utf-8")
    assert "run_tri_party_airline_ticket_purchase_mock_e2e_v01" not in source
    assert "collect_tri_party_airline_ticket_purchase_mock_e2e_v01" not in source


def test_renderer_does_not_import_provider_adapters() -> None:
    source = Path(story.__file__).read_text(encoding="utf-8")
    assert "provider_adapter" not in source
    assert "_shared_live_gemini_provider" not in source


def test_renderer_does_not_import_google_requests_urllib_openai_subprocess_or_config() -> None:
    tree = ast.parse(Path(story.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = {"google", "google.genai", "requests", "urllib", "openai", "subprocess", "config"}
    assert not imported.intersection(forbidden)


def test_renderer_does_not_implement_ledger_crypto_or_replay() -> None:
    source = Path(story.__file__).read_text(encoding="utf-8")
    assert "TransactionArtifactLedger" not in source
    assert "CryptoArtifactSeal" not in source
    assert "SealedTraceReplayVerifier" not in source


def test_renderer_creates_no_packet_receipt_payment_ticket_booking_or_effect(tmp_path: Path, monkeypatch) -> None:
    artifact_dir, audit_log = _write_fixture(tmp_path, monkeypatch)
    counters = _collect(artifact_dir, audit_log)["counter_table"]
    assert counters["renderer_packet_created_count"] == 0
    assert counters["renderer_receipt_created_count"] == 0
    assert counters["renderer_payment_created_count"] == 0
    assert counters["renderer_ticket_created_count"] == 0
    assert counters["renderer_booking_created_count"] == 0
    assert counters["renderer_real_world_effects_count"] == 0


def test_optional_real_artifact_compatibility() -> None:
    if not REAL_ARTIFACT_DIR.exists() or not REAL_AUDIT_LOG.exists():
        pytest.skip("all-real Airline causal artifact package absent")
    report = _collect(REAL_ARTIFACT_DIR, REAL_AUDIT_LOG)
    assert report["final_status"] == story.PASS
    assert len(report["actor_cards"]) == 12
