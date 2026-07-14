from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

import pytest

from demo import run_airline_transaction_artifact_ledger_audit_v01 as audit
from demo import run_tri_party_airline_live_semantic_lane_v01 as live_runner
from demo import run_tri_party_airline_ticket_purchase_mock_e2e_v01 as mock_runner
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as causal_runtime
from hedgehog.domains.airline import ticket_purchase_corridor_runtime_v01 as corridor_runtime
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01 as ledger_collector
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


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


def _reviewer_payload(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
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


def _content_sensitive_causal_provider() -> live_runner.Provider:
    generic = live_runner.build_fake_airline_semantic_provider_v01()

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


@pytest.fixture(scope="session")
def valid_artifact_package(tmp_path_factory: pytest.TempPathFactory) -> Path:
    artifact_dir = tmp_path_factory.mktemp("airline_ledger_audit_package")
    env = {
        live_runner.ENV_LANE: "1",
        live_runner.ENV_FAKE_PROVIDER: "1",
        live_runner.ENV_CAUSAL_BINDING: "1",
        live_runner.ENV_ARTIFACT_DIR: str(artifact_dir),
    }
    report = live_runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=env,
        provider=_content_sensitive_causal_provider(),
        causal_constraints=binding.build_client_constraints_preference_a_v01(),
    )
    assert report["final_status"] == live_runner.STATUS_PASS
    assert (artifact_dir / audit.LEDGER_FILE).exists()
    return artifact_dir


def _copy_package(source: Path, tmp_path: Path) -> Path:
    target = tmp_path / "package"
    shutil.copytree(source, target)
    return target


def _load_json(package_dir: Path, filename: str) -> dict[str, Any]:
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


def _write_json(package_dir: Path, filename: str, payload: Mapping[str, Any]) -> None:
    (package_dir / filename).write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _guard_runtime_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("audit attempted forbidden runtime call")

    monkeypatch.setattr(
        live_runner,
        "collect_tri_party_airline_live_semantic_lane_v01",
        forbidden,
    )
    monkeypatch.setattr(
        causal_runtime,
        "collect_airline_semantic_to_contract_causal_run_v01",
        forbidden,
    )
    monkeypatch.setattr(
        mock_runner,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        forbidden,
    )
    monkeypatch.setattr(
        corridor_runtime,
        "collect_airline_ticket_purchase_corridor_execution_result_v01",
        forbidden,
    )
    monkeypatch.setattr(
        ledger_collector,
        "collect_airline_transaction_artifact_ledger_from_source_v01",
        forbidden,
    )


def test_no_selected_artifact_directory_skips_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    _guard_runtime_calls(monkeypatch)
    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(env={})

    assert report.final_status == audit.SKIPPED_CLOSED
    assert report.validation_errors == ("source_artifact_dir_not_selected",)
    assert report.files_read_count == 0


def test_valid_package_audits_pass_without_rerun(
    valid_artifact_package: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _source_bytes(valid_artifact_package)
    _guard_runtime_calls(monkeypatch)
    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=valid_artifact_package,
    )
    after = _source_bytes(valid_artifact_package)

    assert report.final_status == audit.PASS
    assert report.files_read_count == len(audit.REQUIRED_SOURCE_FILES)
    assert report.actual_entry_count == 19
    assert report.actual_dependency_edge_count == 29
    assert report.actual_root_final_count == 3
    assert report.artifact_type_sequence_valid is True
    assert report.root_final_set_valid is True
    assert report.client_root_final_count == 1
    assert report.airline_root_final_count == 1
    assert report.bank_root_final_count == 1
    assert report.selected_offer_chain_consistent is True
    assert report.transaction_identity_consistent is True
    assert report.source_refs_consistent is True
    assert report.secret_scan_passed is True
    assert len(report.timeline_rows) == 19
    assert report.semantic_rerun_count == 0
    assert report.corridor_rerun_count == 0
    assert report.ledger_collection_count == 0
    assert report.provider_call_count == 0
    assert report.network_call_count == 0
    assert report.gemini_call_count == 0
    assert report.crypto_operation_count == 0
    assert report.replay_operation_count == 0
    assert report.real_world_effects_count == 0
    assert before == after


@pytest.mark.parametrize(
    "mutation_name",
    (
        "missing_ledger_file",
        "invalid_json",
        "wrong_json_root_type",
        "missing_ledger_entry",
        "reordered_entries",
        "duplicate_artifact_id",
        "non_contiguous_index",
        "forward_dependency",
        "missing_dependency",
        "stored_counts_over_actual_18_28_2",
        "duplicate_client_root_missing_bank_root",
        "wrong_root_owner",
        "receipt_classified_as_permission",
        "provider_authority_classification",
        "selected_offer_mismatch_causal",
        "selected_offer_mismatch_integrated_summary",
        "transaction_mismatch",
        "bsep_packet_mismatch",
        "missing_bsep_side_projection",
        "source_ref_mismatch",
        "secret_scan_fail",
        "non_empty_matched_markers",
        "raw_secret_included_true",
        "raw_provider_text_included_true",
        "ledger_created_authority_nonzero",
        "real_world_effect_nonzero",
        "malformed_canonical_hash_input",
        "canonical_artifact_id_mismatch",
        "canonical_dependency_mismatch",
        "missing_summary_transaction_id",
        "missing_integrated_selected_offer_id",
        "missing_causal_semantic_recommendation_id",
        "causal_root_selected_offer_mismatch",
        "causal_hold_contract_offer_mismatch",
        "nested_client_root_selected_offer_mismatch",
        "nested_airline_root_selected_offer_mismatch",
        "causal_hold_packet_offer_mismatch",
        "summary_status_failure",
        "causal_status_failure",
        "bridge_status_failure",
        "integrated_status_failure",
        "bsep_validation_accepted_false",
        "bsep_validation_errors_non_empty",
        "bsep_projection_authority_created",
        "bsep_projection_failed_validation",
        "coordinated_source_ref_rewrite",
        "summary_embedded_ledger_differs",
        "summary_embedded_bridge_differs",
        "ledger_provider_network_gemini_counter_nonzero",
        "missing_ledger_aggregate_counter",
        "entry_real_world_effect_missing",
        "entry_real_world_effect_bool",
        "entry_real_world_effect_string",
        "ledger_validation_errors_empty_dict",
        "artifact_type_as_list",
        "dependency_value_as_dict",
    ),
)
def test_mutated_packages_fail_closed_without_exception(
    valid_artifact_package: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation_name: str,
) -> None:
    package_dir = _copy_package(valid_artifact_package, tmp_path)
    _apply_mutation(package_dir, mutation_name)
    _guard_runtime_calls(monkeypatch)

    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=package_dir,
    )

    assert report.final_status == audit.FAIL_CLOSED
    assert report.validation_errors


def test_timeline_rows_match_committed_sequence(valid_artifact_package: Path) -> None:
    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=valid_artifact_package,
    )

    assert report.final_status == audit.PASS
    assert tuple(row.ledger_index for row in report.timeline_rows) == tuple(range(19))
    assert tuple(row.artifact_type for row in report.timeline_rows) == (
        ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    )
    ledger = _load_json(valid_artifact_package, audit.LEDGER_FILE)
    assert tuple(row.artifact_id for row in report.timeline_rows) == tuple(
        entry["artifact_id"] for entry in ledger["entries"]
    )
    assert tuple(row.depends_on for row in report.timeline_rows) == tuple(
        tuple(entry["depends_on"]) for entry in ledger["entries"]
    )


@pytest.mark.parametrize(
    ("mutation_name", "expected_reason", "coordinated_duplicate_view"),
    (
        (
            "causal_canonical_evidence_offer_mismatch",
            "selected_offer_identity_mismatch",
            False,
        ),
        (
            "causal_client_root_recommended_offer_mismatch",
            "selected_offer_identity_mismatch",
            False,
        ),
        (
            "causal_airline_root_authoritative_offer_mismatch",
            "selected_offer_identity_mismatch",
            False,
        ),
        (
            "causal_airline_root_resolved_offer_mismatch",
            "selected_offer_identity_mismatch",
            False,
        ),
        (
            "ledger_canonical_recommended_offer_mismatch_coordinated",
            "selected_offer_identity_mismatch",
            True,
        ),
        (
            "nested_causal_transaction_mismatch",
            "transaction_identity_mismatch",
            False,
        ),
        (
            "causal_provider_created_authority_count_one",
            "causal_provider_created_authority_count_not_zero",
            False,
        ),
        (
            "causal_provider_created_contract_count_one",
            "causal_provider_created_contract_count_not_zero",
            False,
        ),
        (
            "causal_real_world_effects_count_one",
            "causal_real_world_effects_count_not_zero",
            False,
        ),
        (
            "bridge_causal_report_validation_false_coordinated",
            "bridge_causal_report_validation_accepted_not_true",
            True,
        ),
        (
            "bridge_provider_authority_count_one_coordinated",
            "bridge_provider_created_authority_count_mismatch",
            True,
        ),
        (
            "bridge_real_world_effects_count_one_coordinated",
            "bridge_real_world_effects_count_mismatch",
            True,
        ),
        (
            "bsep_validation_authority_true_coordinated",
            "bsep_validation_bsep_is_authority_not_false",
            True,
        ),
        (
            "bsep_validation_creates_packet_true_coordinated",
            "bsep_validation_bsep_creates_packet_not_false",
            True,
        ),
        (
            "bsep_packet_authority_created_true_coordinated",
            "bsep_packet_authority_created_not_false",
            True,
        ),
        (
            "bsep_packet_raw_provider_text_true_coordinated",
            "bsep_packet_raw_provider_text_included_not_false",
            True,
        ),
        (
            "bsep_projection_authority_created_true_coordinated",
            "bsep_projection_authority_created_not_false:client_bsep_projection",
            True,
        ),
        (
            "integrated_real_world_effects_count_one_coordinated",
            "integrated_real_world_effects_nonzero",
            True,
        ),
        (
            "summary_validation_errors_non_empty",
            "summary_validation_errors_not_empty",
            False,
        ),
    ),
)
def test_final_e1_source_safety_and_lineage_guards(
    valid_artifact_package: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation_name: str,
    expected_reason: str,
    coordinated_duplicate_view: bool,
) -> None:
    package_dir = _copy_package(valid_artifact_package, tmp_path)
    _apply_final_e1_mutation(package_dir, mutation_name)
    _guard_runtime_calls(monkeypatch)

    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=package_dir,
    )

    assert report.final_status == audit.FAIL_CLOSED
    assert expected_reason in report.validation_errors
    if coordinated_duplicate_view:
        assert not any(
            reason.startswith("duplicate_view_mismatch")
            for reason in report.validation_errors
        )


@pytest.mark.parametrize(
    ("mutation_name", "expected_reason"),
    (
        ("actor_reviews_empty", "causal_actor_reviews_shape_mismatch"),
        ("actor_reviews_shortened", "causal_actor_reviews_shape_mismatch"),
        ("reviewer_responses_empty", "causal_reviewer_responses_shape_mismatch"),
        ("reviewer_responses_shortened", "causal_reviewer_responses_shape_mismatch"),
        (
            "actor_recommended_offer_ids_empty",
            "causal_actor_recommended_offer_ids_shape_mismatch",
        ),
        (
            "actor_recommended_offer_ids_shortened",
            "causal_actor_recommended_offer_ids_shape_mismatch",
        ),
        ("actor_reviews_duplicate_actor", "causal_actor_reviews_duplicate_actor"),
        ("reviewer_responses_foreign_actor", "causal_reviewer_responses_foreign_actor"),
        (
            "actor_recommended_offer_ids_malformed_pair",
            "causal_actor_recommended_offer_ids_pair_malformed",
        ),
        (
            "deleted_proposal_transaction_id",
            "transaction_observation_missing:causal.proposal.transaction_id",
        ),
        (
            "deleted_local_chain_validation_transaction_id",
            "transaction_observation_missing:causal.local_chain_validation.transaction_id",
        ),
        (
            "deleted_reviewer_response_transaction_id",
            "transaction_observation_missing:causal.reviewer_responses[0].transaction_id",
        ),
    ),
)
def test_final_e1_closed_causal_collection_and_required_transaction_ids(
    valid_artifact_package: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation_name: str,
    expected_reason: str,
) -> None:
    package_dir = _copy_package(valid_artifact_package, tmp_path)
    _apply_final_causal_shape_mutation(package_dir, mutation_name)
    _guard_runtime_calls(monkeypatch)

    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=package_dir,
    )

    assert report.final_status == audit.FAIL_CLOSED
    assert expected_reason in report.validation_errors


def test_audit_production_files_do_not_import_forbidden_boundaries() -> None:
    forbidden_roots = {
        "hashlib",
        "cryptography",
        "Crypto",
        "requests",
        "urllib",
        "httpx",
        "openai",
        "google",
        "subprocess",
        "socket",
        "config",
    }
    for path in (
        Path(audit.__file__),
        Path("demo/run_human_airline_transaction_artifact_ledger_timeline_v01.py"),
    ):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        assert not (imports & forbidden_roots)


def test_audit_production_files_do_not_call_runtime_or_collector() -> None:
    forbidden_call_names = {
        "collect_tri_party_airline_live_semantic_lane_v01",
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        "collect_airline_semantic_to_contract_causal_run_v01",
        "collect_airline_ticket_purchase_corridor_execution_result_v01",
        "collect_airline_transaction_artifact_ledger_from_source_v01",
    }
    for path in (
        Path(audit.__file__),
        Path("demo/run_human_airline_transaction_artifact_ledger_timeline_v01.py"),
    ):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {
            node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Attribute, ast.Name))
        }
        assert not (names & forbidden_call_names)


def _source_bytes(package_dir: Path) -> dict[str, bytes]:
    return {
        filename: (package_dir / filename).read_bytes()
        for filename in audit.REQUIRED_SOURCE_FILES
    }


def _apply_mutation(package_dir: Path, mutation_name: str) -> None:
    if mutation_name == "missing_ledger_file":
        (package_dir / audit.LEDGER_FILE).unlink()
        return
    if mutation_name == "invalid_json":
        (package_dir / audit.LEDGER_FILE).write_text("{", encoding="utf-8")
        return
    if mutation_name == "wrong_json_root_type":
        (package_dir / audit.LEDGER_FILE).write_text("[]", encoding="utf-8")
        return

    if mutation_name in {
        "selected_offer_mismatch_causal",
        "selected_offer_mismatch_integrated_summary",
        "transaction_mismatch",
        "bsep_packet_mismatch",
        "missing_bsep_side_projection",
        "source_ref_mismatch",
        "secret_scan_fail",
        "non_empty_matched_markers",
        "missing_summary_transaction_id",
        "missing_integrated_selected_offer_id",
        "missing_causal_semantic_recommendation_id",
        "causal_root_selected_offer_mismatch",
        "causal_hold_contract_offer_mismatch",
        "nested_client_root_selected_offer_mismatch",
        "nested_airline_root_selected_offer_mismatch",
        "causal_hold_packet_offer_mismatch",
        "summary_status_failure",
        "causal_status_failure",
        "bridge_status_failure",
        "integrated_status_failure",
        "bsep_validation_accepted_false",
        "bsep_validation_errors_non_empty",
        "bsep_projection_authority_created",
        "bsep_projection_failed_validation",
        "coordinated_source_ref_rewrite",
        "summary_embedded_ledger_differs",
        "summary_embedded_bridge_differs",
    }:
        _apply_source_file_mutation(package_dir, mutation_name)
        return

    ledger = _load_json(package_dir, audit.LEDGER_FILE)
    entries = ledger["entries"]
    if mutation_name == "missing_ledger_entry":
        entries.pop()
    elif mutation_name == "reordered_entries":
        entries[1], entries[2] = entries[2], entries[1]
    elif mutation_name == "duplicate_artifact_id":
        entries[1]["artifact_id"] = entries[0]["artifact_id"]
    elif mutation_name == "non_contiguous_index":
        entries[1]["ledger_index"] = 3
    elif mutation_name == "forward_dependency":
        entries[1]["depends_on"].append(entries[2]["artifact_id"])
    elif mutation_name == "missing_dependency":
        entries[1]["depends_on"].append("missing:dependency")
    elif mutation_name == "stored_counts_over_actual_18_28_2":
        entries.pop()
        ledger["entry_count"] = 19
        ledger["dependency_edge_count"] = 29
        ledger["root_final_count"] = 3
    elif mutation_name == "duplicate_client_root_missing_bank_root":
        _entry_for_type(entries, ledger_contracts.ARTIFACT_BANK_ROOT_FINAL)[
            "artifact_type"
        ] = ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL
    elif mutation_name == "wrong_root_owner":
        _entry_for_type(entries, ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL)[
            "root_owner"
        ] = ledger_contracts.BANK_ROOT_ID
    elif mutation_name == "receipt_classified_as_permission":
        _entry_for_type(entries, ledger_contracts.ARTIFACT_MOCK_TICKET_RECEIPT)[
            "authority_class"
        ] = ledger_contracts.AUTHORITY_ROOT_OWNED_CONTRACT
    elif mutation_name == "provider_authority_classification":
        entries[0]["authority_class"] = "provider_authority"
    elif mutation_name == "raw_secret_included_true":
        entries[0]["raw_secret_included"] = True
    elif mutation_name == "raw_provider_text_included_true":
        entries[0]["raw_provider_text_included"] = True
    elif mutation_name == "ledger_created_authority_nonzero":
        entries[0]["ledger_created_authority"] = True
    elif mutation_name == "real_world_effect_nonzero":
        entries[0]["real_world_effects_count"] = 1
    elif mutation_name == "ledger_provider_network_gemini_counter_nonzero":
        ledger["provider_called_count"] = 1
        ledger["network_used_count"] = 1
        ledger["gemini_called_count"] = 1
    elif mutation_name == "missing_ledger_aggregate_counter":
        del ledger["provider_called_count"]
    elif mutation_name == "entry_real_world_effect_missing":
        del entries[0]["real_world_effects_count"]
    elif mutation_name == "entry_real_world_effect_bool":
        entries[0]["real_world_effects_count"] = False
    elif mutation_name == "entry_real_world_effect_string":
        entries[0]["real_world_effects_count"] = "0"
    elif mutation_name == "ledger_validation_errors_empty_dict":
        ledger["validation_errors"] = {}
    elif mutation_name == "artifact_type_as_list":
        entries[0]["artifact_type"] = []
    elif mutation_name == "dependency_value_as_dict":
        entries[1]["depends_on"][0] = {}
    elif mutation_name == "malformed_canonical_hash_input":
        entries[0]["canonical_hash_input"] = []
    elif mutation_name == "canonical_artifact_id_mismatch":
        entries[0]["canonical_hash_input"]["artifact_id"] = "forged"
    elif mutation_name == "canonical_dependency_mismatch":
        entries[1]["canonical_hash_input"]["depends_on"] = []
    else:
        raise AssertionError(f"unknown mutation {mutation_name}")
    _write_json(package_dir, audit.LEDGER_FILE, ledger)


def _apply_source_file_mutation(package_dir: Path, mutation_name: str) -> None:
    if mutation_name == "selected_offer_mismatch_causal":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["semantic_recommendation_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "selected_offer_mismatch_integrated_summary":
        payload = _load_json(package_dir, audit.INTEGRATED_FILE)
        payload["selected_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.INTEGRATED_FILE, payload)
    elif mutation_name == "transaction_mismatch":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        payload["transaction_id"] = "transaction:forged"
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    elif mutation_name == "bsep_packet_mismatch":
        payload = _load_json(package_dir, audit.BSEP_PROJECTIONS_FILE)
        payload["bank_bsep_projection"]["source_bsep_packet_id"] = "bsep:forged"
        _write_json(package_dir, audit.BSEP_PROJECTIONS_FILE, payload)
    elif mutation_name == "missing_bsep_side_projection":
        payload = _load_json(package_dir, audit.BSEP_PROJECTIONS_FILE)
        del payload["bank_bsep_projection"]
        _write_json(package_dir, audit.BSEP_PROJECTIONS_FILE, payload)
    elif mutation_name == "source_ref_mismatch":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        payload["airline_transaction_artifact_ledger_integration"][
            "source_run_ref"
        ] = "source_run:forged"
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    elif mutation_name == "secret_scan_fail":
        payload = _load_json(package_dir, audit.SECRET_SCAN_FILE)
        payload["passed"] = False
        _write_json(package_dir, audit.SECRET_SCAN_FILE, payload)
    elif mutation_name == "non_empty_matched_markers":
        payload = _load_json(package_dir, audit.SECRET_SCAN_FILE)
        payload["matched_markers"] = ["api_key"]
        _write_json(package_dir, audit.SECRET_SCAN_FILE, payload)
    elif mutation_name == "missing_summary_transaction_id":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        del payload["transaction_id"]
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    elif mutation_name == "missing_integrated_selected_offer_id":
        payload = _load_json(package_dir, audit.INTEGRATED_FILE)
        del payload["selected_offer_id"]
        _write_json(package_dir, audit.INTEGRATED_FILE, payload)
    elif mutation_name == "missing_causal_semantic_recommendation_id":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        del payload["semantic_recommendation_id"]
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_root_selected_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["root_selected_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_hold_contract_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["hold_contract_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "nested_client_root_selected_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["client_root_decision"]["selected_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "nested_airline_root_selected_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["airline_root_resolution"]["selected_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_hold_packet_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["hold_packet"]["offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "summary_status_failure":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        payload["final_status"] = audit.FAIL_CLOSED
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    elif mutation_name == "causal_status_failure":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["final_status"] = audit.FAIL_CLOSED
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "bridge_status_failure":
        payload = _load_json(package_dir, audit.BRIDGE_FILE)
        payload["bridge_status"] = audit.FAIL_CLOSED
        _write_json(package_dir, audit.BRIDGE_FILE, payload)
    elif mutation_name == "integrated_status_failure":
        payload = _load_json(package_dir, audit.INTEGRATED_FILE)
        payload["collection_status"] = audit.FAIL_CLOSED
        _write_json(package_dir, audit.INTEGRATED_FILE, payload)
    elif mutation_name == "bsep_validation_accepted_false":
        payload = _load_json(package_dir, audit.BSEP_VALIDATION_FILE)
        payload["accepted"] = False
        _write_json(package_dir, audit.BSEP_VALIDATION_FILE, payload)
    elif mutation_name == "bsep_validation_errors_non_empty":
        payload = _load_json(package_dir, audit.BSEP_VALIDATION_FILE)
        payload["errors"] = ["bsep_error"]
        _write_json(package_dir, audit.BSEP_VALIDATION_FILE, payload)
    elif mutation_name == "bsep_projection_authority_created":
        payload = _load_json(package_dir, audit.BSEP_PROJECTIONS_FILE)
        payload["client_bsep_projection"]["authority_created"] = True
        _write_json(package_dir, audit.BSEP_PROJECTIONS_FILE, payload)
    elif mutation_name == "bsep_projection_failed_validation":
        payload = _load_json(package_dir, audit.BSEP_PROJECTIONS_FILE)
        payload["client_bsep_projection"]["validation_status"] = audit.FAIL_CLOSED
        _write_json(package_dir, audit.BSEP_PROJECTIONS_FILE, payload)
    elif mutation_name == "coordinated_source_ref_rewrite":
        ledger = _load_json(package_dir, audit.LEDGER_FILE)
        summary = _load_json(package_dir, audit.SUMMARY_FILE)
        forged = {
            "source_run_ref": "source_run:forged",
            "source_causal_report_ref": "source_causal_report:forged",
            "source_corridor_report_ref": "source_corridor_report:forged",
        }
        for key, value in forged.items():
            ledger[key] = value
            ledger["entries"][0]["canonical_hash_input"][key] = value
            summary["airline_transaction_artifact_ledger_integration"][key] = value
            summary["airline_transaction_artifact_ledger_v0_1"][key] = value
            summary["airline_transaction_artifact_ledger_v0_1"]["entries"][0][
                "canonical_hash_input"
            ][key] = value
        _write_json(package_dir, audit.LEDGER_FILE, ledger)
        _write_json(package_dir, audit.SUMMARY_FILE, summary)
    elif mutation_name == "summary_embedded_ledger_differs":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        payload["airline_transaction_artifact_ledger_v0_1"]["ledger_id"] = (
            "airline_transaction_artifact_ledger:summary_forged"
        )
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    elif mutation_name == "summary_embedded_bridge_differs":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        payload["semantic_to_contract_deterministic_bridge"][
            "bridge_status"
        ] = audit.FAIL_CLOSED
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    else:
        raise AssertionError(f"unknown source mutation {mutation_name}")


def _apply_final_e1_mutation(package_dir: Path, mutation_name: str) -> None:
    if mutation_name == "causal_canonical_evidence_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["canonical_evidence"]["recommended_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_client_root_recommended_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["client_root_decision"]["recommended_offer_id"] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_airline_root_authoritative_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["airline_root_resolution"][
            "authoritative_offer_ref"
        ] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_airline_root_resolved_offer_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["airline_root_resolution"][
            "resolved_offer_record_ref"
        ] = binding.OFFER_B_ID
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "ledger_canonical_recommended_offer_mismatch_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.LEDGER_FILE,
            "airline_transaction_artifact_ledger_v0_1",
            _set_first_canonical_recommended_offer_to_b,
        )
    elif mutation_name == "nested_causal_transaction_mismatch":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["proposal"]["transaction_id"] = "transaction:forged"
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_provider_created_authority_count_one":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["provider_created_authority_count"] = 1
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_provider_created_contract_count_one":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["provider_created_contract_count"] = 1
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "causal_real_world_effects_count_one":
        payload = _load_json(package_dir, audit.CAUSAL_FILE)
        payload["real_world_effects_count"] = 1
        _write_json(package_dir, audit.CAUSAL_FILE, payload)
    elif mutation_name == "bridge_causal_report_validation_false_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BRIDGE_FILE,
            "semantic_to_contract_deterministic_bridge",
            lambda payload: payload.__setitem__(
                "causal_report_validation_accepted",
                False,
            ),
        )
    elif mutation_name == "bridge_provider_authority_count_one_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BRIDGE_FILE,
            "semantic_to_contract_deterministic_bridge",
            lambda payload: payload.__setitem__("provider_created_authority_count", 1),
        )
    elif mutation_name == "bridge_real_world_effects_count_one_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BRIDGE_FILE,
            "semantic_to_contract_deterministic_bridge",
            lambda payload: payload.__setitem__("real_world_effects_count", 1),
        )
    elif mutation_name == "bsep_validation_authority_true_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BSEP_VALIDATION_FILE,
            "bsep_validation",
            lambda payload: payload.__setitem__("bsep_is_authority", True),
        )
    elif mutation_name == "bsep_validation_creates_packet_true_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BSEP_VALIDATION_FILE,
            "bsep_validation",
            lambda payload: payload.__setitem__("bsep_creates_packet", True),
        )
    elif mutation_name == "bsep_packet_authority_created_true_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BSEP_PACKET_FILE,
            "bsep_membrane",
            lambda payload: payload.__setitem__("authority_created", True),
        )
    elif mutation_name == "bsep_packet_raw_provider_text_true_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BSEP_PACKET_FILE,
            "bsep_membrane",
            lambda payload: payload.__setitem__("raw_provider_text_included", True),
        )
    elif mutation_name == "bsep_projection_authority_created_true_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.BSEP_PROJECTIONS_FILE,
            "bsep_side_projections",
            lambda payload: payload["client_bsep_projection"].__setitem__(
                "authority_created",
                True,
            ),
        )
    elif mutation_name == "integrated_real_world_effects_count_one_coordinated":
        _mutate_standalone_and_summary_copy(
            package_dir,
            audit.INTEGRATED_FILE,
            "integrated_deterministic_airline_transaction",
            lambda payload: payload.__setitem__("real_world_effects_count", 1),
        )
    elif mutation_name == "summary_validation_errors_non_empty":
        payload = _load_json(package_dir, audit.SUMMARY_FILE)
        payload["validation_errors"] = ["summary_error"]
        _write_json(package_dir, audit.SUMMARY_FILE, payload)
    else:
        raise AssertionError(f"unknown final E1 mutation {mutation_name}")


def _apply_final_causal_shape_mutation(
    package_dir: Path,
    mutation_name: str,
) -> None:
    payload = _load_json(package_dir, audit.CAUSAL_FILE)
    if mutation_name == "actor_reviews_empty":
        payload["actor_reviews"] = []
    elif mutation_name == "actor_reviews_shortened":
        payload["actor_reviews"] = payload["actor_reviews"][:4]
    elif mutation_name == "reviewer_responses_empty":
        payload["reviewer_responses"] = []
    elif mutation_name == "reviewer_responses_shortened":
        payload["reviewer_responses"] = payload["reviewer_responses"][:3]
    elif mutation_name == "actor_recommended_offer_ids_empty":
        payload["synthesis"]["actor_recommended_offer_ids"] = []
    elif mutation_name == "actor_recommended_offer_ids_shortened":
        payload["synthesis"]["actor_recommended_offer_ids"] = (
            payload["synthesis"]["actor_recommended_offer_ids"][:4]
        )
    elif mutation_name == "actor_reviews_duplicate_actor":
        payload["actor_reviews"][1]["actor_id"] = payload["actor_reviews"][0][
            "actor_id"
        ]
    elif mutation_name == "reviewer_responses_foreign_actor":
        payload["reviewer_responses"][0]["actor_id"] = "foreign_actor_llm"
    elif mutation_name == "actor_recommended_offer_ids_malformed_pair":
        payload["synthesis"]["actor_recommended_offer_ids"][0] = ["actor_only"]
    elif mutation_name == "deleted_proposal_transaction_id":
        del payload["proposal"]["transaction_id"]
    elif mutation_name == "deleted_local_chain_validation_transaction_id":
        del payload["local_chain_validation"]["transaction_id"]
    elif mutation_name == "deleted_reviewer_response_transaction_id":
        del payload["reviewer_responses"][0]["transaction_id"]
    else:
        raise AssertionError(f"unknown causal shape mutation {mutation_name}")
    _write_json(package_dir, audit.CAUSAL_FILE, payload)


def _mutate_standalone_and_summary_copy(
    package_dir: Path,
    filename: str,
    summary_key: str,
    mutator: Any,
) -> None:
    standalone = _load_json(package_dir, filename)
    summary = _load_json(package_dir, audit.SUMMARY_FILE)
    embedded = summary[summary_key]
    mutator(standalone)
    mutator(embedded)
    _write_json(package_dir, filename, standalone)
    _write_json(package_dir, audit.SUMMARY_FILE, summary)


def _set_first_canonical_recommended_offer_to_b(payload: dict[str, Any]) -> None:
    for entry in payload["entries"]:
        canonical = entry.get("canonical_hash_input")
        if isinstance(canonical, dict) and _set_nested_key_once(
            canonical,
            "recommended_offer_id",
            binding.OFFER_B_ID,
        ):
            return
    raise AssertionError("no recommended_offer_id found in Ledger canonical input")


def _set_nested_key_once(value: Any, key: str, replacement: Any) -> bool:
    if isinstance(value, dict):
        if key in value:
            value[key] = replacement
            return True
        return any(_set_nested_key_once(item, key, replacement) for item in value.values())
    if isinstance(value, list):
        return any(_set_nested_key_once(item, key, replacement) for item in value)
    return False


def _entry_for_type(entries: list[dict[str, Any]], artifact_type: str) -> dict[str, Any]:
    for entry in entries:
        if entry["artifact_type"] == artifact_type:
            return entry
    raise AssertionError(f"missing {artifact_type}")
