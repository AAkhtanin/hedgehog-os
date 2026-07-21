from __future__ import annotations

import ast
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import fields, replace
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
from types import SimpleNamespace

import pytest

from demo import run_tri_party_airline_live_semantic_lane_v01 as lane
from demo import run_two_domain_airline_all_real_program_v01 as runner
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger
from hedgehog.domains.airline import sealed_evidence_package_adapter_v01 as adapter


EXPECTED_ACTOR_IDS = (
    "tri_party_airline_orchestrator_llm",
    "tri_party_airline_semantic_architect_llm",
    "client_purchase_intent_reviewer_llm",
    "client_profile_privacy_reviewer_llm",
    "airline_offer_policy_reviewer_llm",
    "airline_fare_rules_vertical_cell_llm",
    "airline_seat_baggage_vertical_cell_llm",
    "airline_ticketing_policy_reviewer_llm",
    "bank_payment_policy_reviewer_llm",
    "bank_idempotency_risk_vertical_cell_llm",
    "bank_payment_status_explainer_llm",
    "tri_party_evidence_consistency_reviewer_llm",
)
EXPECTED_SAFE_KEYS = frozenset(
    (
        "execution_head",
        "run_id",
        "report_id",
        "source_task_id",
        "transaction_id",
        "selected_offer_id",
        "provider_mode",
        "model_id",
        "source_final_status",
        "actors",
        "bsep",
        "root_finals",
        "corridor",
        "receipts",
        "counters",
        "raw_prompt_included",
        "raw_provider_response_included",
        "secret_scan_passed",
        "real_world_effects_count",
        "validation_errors",
    )
)
EXPECTED_RESULT_FIELDS = (
    "programme_id",
    "programme_version",
    "gate_id",
    "domain_id",
    "execution_mode",
    "execution_head",
    "attempt_number",
    "attempt_id",
    "final_status",
    "reason_code",
    "failed_stage",
    "live_collection_performed",
    "official_evidence_eligible",
    "private_attempt_preserved",
    "private_attempt_preservation_state",
    "public_safe_report_state",
    "actual_external_operation_status",
    "provider_application_call_mode",
    "collector_invocation_count",
    "injected_callback_count",
    "wrapper_callback_observed_count",
    "provider_callback_started_count",
    "provider_callback_completed_count",
    "semantic_actor_call_count",
    "causal_actor_call_count",
    "generic_actor_call_count",
    "duplicate_actor_call_count",
    "safe_execution_id",
    "safe_report_sha256",
    "private_inventory_digest",
    "safe_report_written",
    "source_provider_call_count",
    "source_network_call_count",
    "source_gemini_call_count",
    "source_real_world_effects_count",
    "actual_provider_call_count",
    "actual_network_call_count",
    "actual_gemini_call_count",
    "actual_real_world_effects_count",
    "retry_count",
    "package_created_count",
    "anchor_created_count",
    "replay_created_count",
)


class _CapturedSourceReport(dict[str, object]):
    pass


_CANONICAL_SOURCE_CONTEXT: dict[str, object] = {}


@pytest.fixture(autouse=True)
def _zero_network_and_real_provider_sentinel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempted: list[str] = []

    def blocked(name: str):
        def fail(*args, **kwargs):
            attempted.append(name)
            pytest.fail(f"forbidden external operation attempted: {name}")

        return fail

    monkeypatch.setattr(socket, "create_connection", blocked("socket.create_connection"))
    monkeypatch.setattr(socket.socket, "connect", blocked("socket.socket.connect"))
    monkeypatch.setattr(
        runner,
        "_REAL_PROVIDER_BUILDER",
        blocked("real_provider_builder"),
    )
    monkeypatch.setattr(
        lane.provider_adapter,
        "_generate_gemini_content_with_schema_fallback",
        blocked("google_generate_content"),
    )
    yield
    assert attempted == []


def _source_report(raw_directory: Path) -> _CapturedSourceReport:
    capture = runner._collect_canonical_with_capture(
        env=runner._collector_environment(runner.MODE_INJECTED, raw_directory),
        provider=runner._build_injected_provider_v01(),
        causal_constraints=binding.build_client_constraints_preference_a_v01(),
        causal_snapshot=binding.build_airline_candidate_snapshot_v01(),
    )
    report = _CapturedSourceReport(capture.report)
    report._a1_deterministic_result = capture.deterministic_result
    report._a1_ledger_source_bundle = capture.ledger_source_bundle
    report._a1_ledger_source_validation = capture.ledger_source_validation
    report._a1_ledger_item = capture.ledger_item
    report._a1_crypto_source_bundle = capture.crypto_source_bundle
    report._a1_crypto_collection_result = capture.crypto_collection_result
    _CANONICAL_SOURCE_CONTEXT.update(
        deterministic_result=capture.deterministic_result,
        ledger_source_bundle=capture.ledger_source_bundle,
        ledger_source_validation=capture.ledger_source_validation,
        crypto_collection_result=capture.crypto_collection_result,
    )
    return report


@pytest.fixture(scope="module")
def source_report(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    root = tmp_path_factory.mktemp("a1-source-report")
    return _source_report(root / runner.RAW_ATTEMPT_DIRECTORY)


def _run(
    tmp_path: Path,
    *,
    provider=None,
    progress=None,
    private_name: str = "attempt-01",
    safe_name: str = "safe-report.json",
):
    return runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_INJECTED,
        attempt_number=1,
        private_output_directory=tmp_path / private_name,
        injected_provider=provider,
        injected_safe_report_output=tmp_path / safe_name,
        progress_sink=progress,
    )


def _patch_simulated_real(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    provider_builder=None,
) -> tuple[Path, list[str]]:
    safe_path = tmp_path / "simulated-real-safe.json"
    guards: list[str] = []
    monkeypatch.setattr(runner, "_CANONICAL_SAFE_REPORT_PATH", safe_path)
    monkeypatch.setattr(runner, "_ensure_canonical_public_parent", lambda: None)
    monkeypatch.setattr(
        runner,
        "_require_real_local_preconditions",
        lambda environment: runner._RealPreconditionResult(20, 1),
    )

    def repository_guard(expected_head=None):
        guards.append(expected_head or "initial")
        assert expected_head in (None, "8e27d62cafa4e3096fb03ba22361391c46759327")
        return "8e27d62cafa4e3096fb03ba22361391c46759327"

    monkeypatch.setattr(runner, "_require_real_repository_ready", repository_guard)
    monkeypatch.setattr(lane.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        runner,
        "_REAL_PROVIDER_BUILDER",
        provider_builder or (lambda model: runner._build_injected_provider_v01()),
    )
    return safe_path, guards


def _git_ready_values() -> dict[tuple[str, ...], str]:
    head = "8e27d62cafa4e3096fb03ba22361391c46759327"
    return {
        ("rev-parse", "--show-toplevel"): str(runner._REPOSITORY_ROOT),
        ("branch", "--show-current"): "main",
        ("rev-parse", "HEAD"): head,
        ("rev-parse", "origin/main"): head,
        ("status", "--porcelain", "--untracked-files=all"): "",
        ("diff", "--cached", "--name-only"): "",
        (
            "ls-files",
            "--error-unmatch",
            "demo/run_two_domain_airline_all_real_program_v01.py",
            "tests/test_two_domain_airline_all_real_program_v01_runner.py",
        ): (
            "demo/run_two_domain_airline_all_real_program_v01.py\n"
            "tests/test_two_domain_airline_all_real_program_v01_runner.py"
        ),
    }


def _private_document_context(tmp_path: Path):
    root = tmp_path / "private-document-root"
    identity = runner._create_private_root(root)
    return root, identity, {"document_version": "v0.1", "status": "PASS"}


def _normalization(source_report: dict[str, object]) -> dict[str, object]:
    return runner.build_airline_safe_normalization_v01(
        source_report,
        execution_head="8e27d62cafa4e3096fb03ba22361391c46759327",
        deterministic_result=_CANONICAL_SOURCE_CONTEXT["deterministic_result"],
        ledger_source_bundle=_CANONICAL_SOURCE_CONTEXT["ledger_source_bundle"],
        ledger_source_validation=_CANONICAL_SOURCE_CONTEXT[
            "ledger_source_validation"
        ],
        crypto_collection_result=_CANONICAL_SOURCE_CONTEXT[
            "crypto_collection_result"
        ],
    )


def _assert_source_invalid(report: object) -> None:
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._validate_collector_report_v01(
            report,
            execution_mode=None,
            deterministic_result=_CANONICAL_SOURCE_CONTEXT[
                "deterministic_result"
            ],
            ledger_source_bundle=_CANONICAL_SOURCE_CONTEXT[
                "ledger_source_bundle"
            ],
            ledger_source_validation=_CANONICAL_SOURCE_CONTEXT[
                "ledger_source_validation"
            ],
            crypto_collection_result=_CANONICAL_SOURCE_CONTEXT[
                "crypto_collection_result"
            ],
        )
    assert captured.value.reason in (
        runner.REASON_SOURCE_GEOMETRY_INVALID,
        runner.REASON_SECRET_SCAN_FAILED,
    )


def test_public_surface_constants_and_result_geometry() -> None:
    assert runner.MODULE_ID == "two_domain_airline_all_real_program_v01"
    assert runner.PROGRAMME_ID == "two_domain_all_real_sealed_evidence_program_v01"
    assert runner.GATE_ID == "two_domain_all_real_sealed_evidence_program_v01_a1_airline_live"
    assert runner.MODEL_ID == "gemini-2.5-flash"
    assert runner.MODE_INJECTED == "injected_deterministic"
    assert runner.MODE_REAL == "real_provider"
    assert runner.ACTOR_IDS == EXPECTED_ACTOR_IDS
    assert tuple(field.name for field in fields(runner.AirlineA1ProgramResultV01)) == EXPECTED_RESULT_FIELDS
    assert runner.AirlineA1ProgramResultV01.__slots__ == EXPECTED_RESULT_FIELDS


def test_exact_expected_private_success_inventory_geometry() -> None:
    assert len(runner.EXPECTED_RAW_ATTEMPT_FILENAMES) == 72
    assert len(set(runner.EXPECTED_RAW_ATTEMPT_FILENAMES)) == 72
    assert all("/" not in item and "\\" not in item for item in runner.EXPECTED_RAW_ATTEMPT_FILENAMES)
    for actor_id in EXPECTED_ACTOR_IDS:
        assert sum(item.startswith(f"{actor_id}_") for item in runner.EXPECTED_RAW_ATTEMPT_FILENAMES) == 5


def test_injected_happy_path_calls_canonical_collector_once_with_preference_a(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    original = runner._COLLECTOR
    observed: list[tuple[object, object]] = []
    calls = 0

    def collector(**kwargs):
        nonlocal calls
        calls += 1
        observed.append((kwargs["causal_constraints"], kwargs["causal_snapshot"]))
        return original(**kwargs)

    monkeypatch.setattr(runner, "_COLLECTOR", collector)
    progress: list[dict[str, object]] = []
    result = _run(tmp_path, progress=progress.append)

    assert result.final_status == runner.STATUS_PASS
    assert calls == result.collector_invocation_count == 1
    assert observed == [
        (
            binding.build_client_constraints_preference_a_v01(),
            binding.build_airline_candidate_snapshot_v01(),
        )
    ]
    assert result.execution_mode == runner.MODE_INJECTED
    assert result.live_collection_performed is False
    assert result.official_evidence_eligible is False
    assert result.safe_report_written is True
    assert result.private_attempt_preserved is True
    assert result.private_attempt_preservation_state == runner._PRESERVATION_PRESERVED
    assert result.public_safe_report_state == runner._PUBLICATION_PRESENT
    assert result.retry_count == 0
    assert result.package_created_count == result.anchor_created_count == result.replay_created_count == 0
    assert result.injected_callback_count == 12
    completed = [row["actor_id"] for row in progress if row["event"] == "call_completed"]
    assert tuple(completed) == EXPECTED_ACTOR_IDS
    validated = [row for row in progress if row["event"] == "local_validation_completed"]
    assert len(validated) == 12
    assert all(row["validation_status"] == runner.STATUS_PASS for row in validated)
    assert not any(
        token in json.dumps(progress, sort_keys=True).casefold()
        for token in ("raw_prompt", "raw_response", "api_key", str(tmp_path).casefold())
    )


def test_injected_actual_zero_operations_are_distinct_from_source_geometry(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert (
        result.source_provider_call_count,
        result.source_network_call_count,
        result.source_gemini_call_count,
        result.source_real_world_effects_count,
    ) == (12, 12, 12, 0)
    assert (
        result.actual_provider_call_count,
        result.actual_network_call_count,
        result.actual_gemini_call_count,
        result.actual_real_world_effects_count,
    ) == (0, 0, 0, 0)
    assert (result.semantic_actor_call_count, result.causal_actor_call_count, result.generic_actor_call_count, result.duplicate_actor_call_count) == (12, 5, 7, 0)


def test_safe_normalization_exact_schema_and_nested_geometry(source_report) -> None:
    safe = _normalization(source_report)
    assert frozenset(safe) == EXPECTED_SAFE_KEYS
    assert tuple(row["actor_id"] for row in safe["actors"]) == EXPECTED_ACTOR_IDS
    assert all(frozenset(row) == {"actor_id", "safe_projection", "validation_status"} for row in safe["actors"])
    assert tuple(row["projection_ref"] for row in safe["bsep"]["projections"]) == adapter._EXPECTED_BSEP_REFS
    assert tuple(
        row["safe_projection"]["source_projection_ref"]
        for row in safe["bsep"]["projections"]
    ) == tuple(
        source_report["bsep_side_projections"][name]["projection_ref"]
        for name in runner.BSEP_PROJECTION_NAMES
    )
    assert tuple(row["root_role"] for row in safe["root_finals"]) == ("ClientRoot", "AirlineRoot", "BankRoot")
    assert len(safe["receipts"]) == 3
    assert safe["counters"] == {
        "provider_call_count": 12,
        "network_call_count": 12,
        "gemini_call_count": 12,
    }
    assert safe["provider_mode"] == lane.PROVIDER_MODE_FAKE
    assert safe["raw_prompt_included"] is False
    assert safe["raw_provider_response_included"] is False
    assert safe["secret_scan_passed"] is True
    assert safe["real_world_effects_count"] == 0
    assert safe["validation_errors"] == ()


def test_r1_safe_projection_passes_and_round_trips_deterministically(source_report) -> None:
    first_safe = _normalization(source_report)
    second_safe = _normalization(source_report)
    first = adapter.build_airline_safe_execution_projection_v01(first_safe)
    second = adapter.build_airline_safe_execution_projection_v01(second_safe)
    assert first == second
    assert first.safe_execution_id == second.safe_execution_id
    assert first.status == adapter.STATUS_FAIL_CLOSED
    assert adapter.validate_airline_safe_execution_projection_v01(first) == ()
    assert runner.validate_airline_safe_normalization_v01(first_safe) == ()
    plain = adapter.airline_safe_execution_projection_to_plain_dict_v01(first)
    assert json.loads(runner._canonical_json_line(plain)) == plain


def test_equivalent_injected_roots_produce_identical_public_safe_bytes(tmp_path: Path) -> None:
    first = _run(tmp_path, private_name="attempt-a", safe_name="safe-a.json")
    second = _run(tmp_path, private_name="attempt-b", safe_name="safe-b.json")
    assert first.final_status == second.final_status == runner.STATUS_PASS
    assert first.safe_execution_id == second.safe_execution_id
    assert first.safe_report_sha256 == second.safe_report_sha256
    assert first.attempt_id != second.attempt_id
    assert (tmp_path / "safe-a.json").read_bytes() == (tmp_path / "safe-b.json").read_bytes()


def test_private_attempt_geometry_and_generation_gate(tmp_path: Path) -> None:
    result = _run(tmp_path)
    root = tmp_path / "attempt-01"
    assert tuple(sorted(path.name for path in root.iterdir())) == tuple(
        sorted(
            (
                runner.ATTEMPT_IDENTITY_FILE,
                runner.RAW_ATTEMPT_DIRECTORY,
                runner.PRIVATE_INVENTORY_FILE,
                runner.GENERATION_GATE_FILE,
            )
        )
    )
    assert tuple(sorted(path.name for path in (root / runner.RAW_ATTEMPT_DIRECTORY).iterdir())) == runner.EXPECTED_RAW_ATTEMPT_FILENAMES
    inventory = json.loads((root / runner.PRIVATE_INVENTORY_FILE).read_text())
    gate = json.loads((root / runner.GENERATION_GATE_FILE).read_text())
    assert inventory["raw_attempt_file_count"] == 72
    assert inventory["aggregate_inventory_digest"] == result.private_inventory_digest
    assert gate["final_source_status"] == runner.STATUS_PASS
    assert gate["official_evidence_eligible"] is False
    assert gate["live_collection_performed"] is False
    assert gate["injected_callback_count"] == 12
    assert (gate["actual_provider_call_count"], gate["actual_network_call_count"], gate["actual_gemini_call_count"], gate["actual_real_world_effects_count"]) == (0, 0, 0, 0)
    attempt = json.loads((root / runner.ATTEMPT_IDENTITY_FILE).read_text())
    assert attempt["output_directory"] == str(root)
    assert attempt["output_directory_sha256"] == hashlib.sha256(str(root).encode()).hexdigest()
    assert not any(
        str(tmp_path) in path.read_text(errors="ignore")
        for path in (
            root / runner.PRIVATE_INVENTORY_FILE,
            root / runner.GENERATION_GATE_FILE,
        )
    )


@pytest.mark.parametrize(
    "mutation",
    (
        "actor_missing",
        "actor_reordered",
        "actor_failed",
        "bsep_failed",
        "bsep_projection_missing",
        "root_failed",
        "offer_changed",
        "corridor_failed",
        "counter_changed",
        "effect_changed",
        "crypto_anchor_claim",
        "crypto_byte_drift",
        "source_call_counter",
        "actor_authority",
        "bsep_authority",
        "bsep_projection_private",
        "crypto_signature",
        "crypto_rerun",
    ),
)
def test_source_geometry_mutations_fail_closed(source_report, mutation: str) -> None:
    report = deepcopy(source_report)
    if mutation == "actor_missing":
        report["semantic_actor_reports"] = report["semantic_actor_reports"][:-1]
    elif mutation == "actor_reordered":
        rows = list(report["semantic_actor_reports"])
        rows[0], rows[1] = rows[1], rows[0]
        report["semantic_actor_reports"] = tuple(rows)
    elif mutation == "actor_failed":
        rows = list(report["semantic_actor_reports"])
        rows[0]["validation_status"] = runner.STATUS_FAIL_CLOSED
    elif mutation == "bsep_failed":
        report["bsep_validation"]["validation_status"] = runner.STATUS_FAIL_CLOSED
    elif mutation == "bsep_projection_missing":
        report["bsep_side_projections"].pop("bank_bsep_projection")
    elif mutation == "root_failed":
        report["root_boundaries"][0]["boundary_preserved"] = False
    elif mutation == "offer_changed":
        report["semantic_to_contract_deterministic_bridge"]["semantic_recommendation_id"] = binding.OFFER_B_ID
    elif mutation == "corridor_failed":
        report["integrated_deterministic_airline_transaction"]["corridor_final_status"] = runner.STATUS_FAIL_CLOSED
    elif mutation == "counter_changed":
        report["counter_table"]["semantic_actor_call_count"] = 11
    elif mutation == "effect_changed":
        report["counter_table"]["real_world_effects_count"] = 1
    elif mutation == "crypto_anchor_claim":
        report["airline_crypto_artifact_seal_integration"]["external_anchor_verified"] = True
    elif mutation == "crypto_byte_drift":
        report["airline_crypto_artifact_seal_integration"]["source_bytes_unchanged_after_write"] = False
    elif mutation == "source_call_counter":
        report["counter_table"]["fake_provider_call_count"] = 11
    elif mutation == "actor_authority":
        report["semantic_actor_reports"][0]["authority_created"] = True
    elif mutation == "bsep_authority":
        report["bsep_validation"]["bsep_is_authority"] = True
    elif mutation == "bsep_projection_private":
        report["bsep_side_projections"]["client_bsep_projection"]["raw_secrets_included"] = True
    elif mutation == "crypto_signature":
        report["airline_crypto_artifact_seal_integration"]["signature_verified"] = True
    elif mutation == "crypto_rerun":
        report["airline_crypto_artifact_seal_integration"]["semantic_rerun_count"] = 1
    _assert_source_invalid(report)


@pytest.mark.parametrize(
    "field_name",
    (
        "entry_count",
        "dependency_edge_count",
        "root_final_count",
        "validation_status",
    ),
)
def test_typed_ledger_mutations_fail_closed(source_report, field_name: str) -> None:
    report = dict(source_report)
    item = source_report["airline_transaction_artifact_ledger_v0_1"]
    changed = {
        "entry_count": 18,
        "dependency_edge_count": 28,
        "root_final_count": 2,
        "validation_status": runner.STATUS_FAIL_CLOSED,
    }[field_name]
    report["airline_transaction_artifact_ledger_v0_1"] = replace(item, **{field_name: changed})
    _assert_source_invalid(report)


@pytest.mark.parametrize(
    "unsafe_text",
    (
        "/Users/admin/private/report.json",
        "Traceback: private failure",
        "GEMINI_API_KEY=private",
        "<PrivateRecord object at 0x1234abcd>",
        "file:///Users/admin/private/report.json",
    ),
)
def test_private_material_in_copied_safe_field_is_rejected(source_report, unsafe_text: str) -> None:
    report = deepcopy(source_report)
    report["semantic_actor_reports"][0]["output_semantic_summary"] = unsafe_text
    with pytest.raises(ValueError, match=f"^{runner.REASON_SAFE_NORMALIZATION_INVALID}$") as captured:
        _normalization(report)
    assert unsafe_text not in str(captured.value)


def test_whitelist_omits_private_collector_fields(source_report) -> None:
    safe = _normalization(source_report)
    rendered = runner._canonical_json_line(safe).decode("utf-8")
    assert "prompt_artifact" not in rendered
    assert "raw_response_artifact" not in rendered
    assert "provider_env" not in rendered
    assert "artifact_dir" not in rendered
    assert "absolute_path" not in rendered
    assert not any(str(value) in rendered for value in source_report["artifacts"].values())


def test_safe_negative_metadata_and_public_authorization_refs_are_accepted(source_report) -> None:
    safe = _normalization(source_report)
    safe["actors"][0]["safe_projection"]["canonical_summary"] = (
        "authorization_ref_id and token_count are bounded public metrics"
    )
    assert runner.validate_airline_safe_normalization_v01(safe) == ()
    assert adapter.build_airline_safe_execution_projection_v01(safe).status == adapter.STATUS_FAIL_CLOSED


def test_forged_safe_report_raw_material_fails_validation_and_projection(source_report) -> None:
    safe = _normalization(source_report)
    safe["actors"][0]["safe_projection"]["provider_response_backup"] = "private"
    assert runner.validate_airline_safe_normalization_v01(safe) == (runner.REASON_SAFE_NORMALIZATION_INVALID,)
    with pytest.raises(ValueError):
        adapter.build_airline_safe_execution_projection_v01(safe)


def test_partial_provider_failure_is_preserved_without_retry_or_public_report(tmp_path: Path) -> None:
    base = runner._build_injected_provider_v01()
    calls: list[str] = []

    def failing(actor_id, prompt, metadata):
        calls.append(actor_id)
        if len(calls) == 3:
            raise RuntimeError("private /Users/admin/raw secret")
        return base(actor_id, prompt, metadata)

    result = _run(tmp_path, provider=failing)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code == runner.REASON_COLLECTOR_FAILED or result.reason_code == runner.REASON_SOURCE_GEOMETRY_INVALID
    assert result.collector_invocation_count == 1
    assert result.injected_callback_count == 3
    assert result.retry_count == 0
    assert result.private_attempt_preserved is True
    assert not (tmp_path / "safe-report.json").exists()
    root = tmp_path / "attempt-01"
    assert (root / runner.ATTEMPT_IDENTITY_FILE).is_file()
    assert (root / runner.PRIVATE_INVENTORY_FILE).is_file()
    assert (root / runner.GENERATION_GATE_FILE).is_file()
    public_gate = (root / runner.GENERATION_GATE_FILE).read_text()
    assert "/Users/admin" not in public_gate
    assert "RuntimeError" not in public_gate
    assert "private /Users/admin/raw secret" not in public_gate


def test_second_invocation_same_private_path_rejected_before_callback(tmp_path: Path) -> None:
    first = _run(tmp_path)
    calls: list[str] = []

    def provider(actor_id, prompt, metadata):
        calls.append(actor_id)
        return "{}"

    second = _run(tmp_path, provider=provider, safe_name="second.json")
    assert first.final_status == runner.STATUS_PASS
    assert second.final_status == runner.STATUS_FAIL_CLOSED
    assert second.reason_code == runner.REASON_PRIVATE_PATH_EXISTS
    assert calls == []
    assert not (tmp_path / "second.json").exists()


@pytest.mark.parametrize(
    "kind",
    (
        "relative",
        "dotdot",
        "existing",
        "symlink_parent",
        "missing_parent",
        "inside_repository",
    ),
)
def test_invalid_private_paths_rejected_before_provider(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    kind: str,
) -> None:
    calls: list[str] = []

    def provider(actor_id, prompt, metadata):
        calls.append(actor_id)
        return "{}"

    if kind == "relative":
        private = Path("relative-attempt")
    elif kind == "dotdot":
        private = Path(f"{tmp_path}/child/../attempt")
    elif kind == "existing":
        private = tmp_path / "attempt"
        private.mkdir()
    elif kind == "symlink_parent":
        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real, target_is_directory=True)
        private = link / "attempt"
    elif kind == "missing_parent":
        private = tmp_path / "missing" / "attempt"
    else:
        private = Path(runner._REPOSITORY_ROOT) / "forbidden-a1-attempt"
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_INJECTED,
        attempt_number=1,
        private_output_directory=private,
        injected_provider=provider,
        injected_safe_report_output=tmp_path / "safe.json",
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code in (runner.REASON_PRIVATE_PATH_INVALID, runner.REASON_PRIVATE_PATH_EXISTS)
    assert calls == []


@pytest.mark.parametrize("attempt_number", (0, 2, -1, True, 1.0, "1"))
def test_non_exact_attempt_one_rejected_before_provider(tmp_path: Path, attempt_number) -> None:
    calls: list[str] = []

    def provider(*args):
        calls.append("called")
        return "{}"

    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_INJECTED,
        attempt_number=attempt_number,
        private_output_directory=tmp_path / "attempt",
        injected_provider=provider,
        injected_safe_report_output=tmp_path / "safe.json",
    )
    assert result.reason_code == runner.REASON_ATTEMPT_INVALID
    assert calls == []


def test_real_mode_rejects_injected_callback_before_provider(tmp_path: Path) -> None:
    calls: list[str] = []

    def provider(*args):
        calls.append("called")
        return "{}"

    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=tmp_path / "attempt",
        injected_provider=provider,
    )
    assert result.reason_code == runner.REASON_MODE_INVALID
    assert calls == []


def test_injected_mode_refuses_canonical_repository_report_path(tmp_path: Path) -> None:
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_INJECTED,
        attempt_number=1,
        private_output_directory=tmp_path / "attempt",
        injected_safe_report_output=runner._CANONICAL_SAFE_REPORT_PATH,
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.official_evidence_eligible is False
    assert not runner._CANONICAL_SAFE_REPORT_PATH.exists()


def test_public_output_is_exclusive_canonical_and_read_only(source_report, tmp_path: Path) -> None:
    safe = _normalization(source_report)
    output = tmp_path / "safe.json"
    owner = runner._write_public_safe_report(output, safe)
    runner._release_owned_output(owner)
    content = output.read_bytes()
    assert content == runner._canonical_json_line(safe)
    assert content.endswith(b"\n") and not content.endswith(b"\n\n")
    assert stat.S_IMODE(output.stat().st_mode) == 0o400
    with pytest.raises(runner._RunnerFailure):
        runner._write_public_safe_report(output, safe)


def test_public_writer_handles_short_positive_writes(source_report, tmp_path: Path, monkeypatch) -> None:
    safe = _normalization(source_report)
    original = os.write
    monkeypatch.setattr(runner, "_WRITE", lambda fd, data: original(fd, data[:3]))
    output = tmp_path / "safe.json"
    owner = runner._write_public_safe_report(output, safe)
    runner._release_owned_output(owner)
    assert output.read_bytes() == runner._canonical_json_line(safe)


@pytest.mark.parametrize("failure", ("zero_write", "fsync", "reread", "semantic"))
def test_public_write_failures_leave_no_false_pass(
    source_report,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    safe = _normalization(source_report)
    output = tmp_path / f"{failure}.json"
    if failure == "zero_write":
        monkeypatch.setattr(runner, "_WRITE", lambda fd, data: 0)
    elif failure == "fsync":
        monkeypatch.setattr(runner, "_FSYNC", lambda fd: (_ for _ in ()).throw(OSError("private")))
    elif failure == "reread":
        monkeypatch.setattr(runner, "_read_all", lambda fd: b"{}\n")
    else:
        monkeypatch.setattr(runner, "_strict_json", lambda content: {"changed": True})
    with pytest.raises((runner._RunnerFailure, runner._PublicCleanupFailure)):
        runner._write_public_safe_report(output, safe)
    assert not output.exists()


def test_noop_public_close_uses_independent_raw_close(source_report, tmp_path: Path, monkeypatch) -> None:
    safe = _normalization(source_report)
    monkeypatch.setattr(runner, "_CLOSE", lambda fd: None)
    output = tmp_path / "safe.json"
    owner = runner._write_public_safe_report(output, safe)
    runner._release_owned_output(owner)
    assert output.is_file()


def test_unproved_public_close_fails_and_removes_owned_output(
    source_report,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    safe = _normalization(source_report)
    opened: list[int] = []
    original_open = runner._OPEN
    original_close = os.close

    def tracked_open(*args, **kwargs):
        fd = original_open(*args, **kwargs)
        opened.append(fd)
        return fd

    monkeypatch.setattr(runner, "_OPEN", tracked_open)
    monkeypatch.setattr(runner, "_CLOSE", lambda fd: None)
    monkeypatch.setattr(
        runner,
        "_RAW_CLOSE",
        lambda fd: (_ for _ in ()).throw(OSError("close unavailable")),
    )
    output = tmp_path / "safe.json"
    with pytest.raises(runner._PublicCleanupFailure):
        runner._write_public_safe_report(output, safe)
    assert not output.exists()
    monkeypatch.setattr(runner, "_CLOSE", original_close)
    monkeypatch.setattr(runner, "_RAW_CLOSE", original_close)
    for fd in opened:
        try:
            original_close(fd)
        except OSError:
            pass


def test_post_write_same_length_mutation_cannot_return_pass(tmp_path: Path, monkeypatch) -> None:
    def mutate(path: Path) -> None:
        content = path.read_bytes()
        path.chmod(0o600)
        changed = bytearray(content)
        changed[10] = ord("x") if changed[10] != ord("x") else ord("y")
        path.write_bytes(bytes(changed))

    monkeypatch.setattr(runner, "_POST_PUBLIC_WRITE_HOOK", mutate)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.safe_report_written is False
    assert not (tmp_path / "safe-report.json").exists()


def _mini_inventory_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "private"
    identity = runner._create_private_root(root)
    raw = root / runner.RAW_ATTEMPT_DIRECTORY
    raw.mkdir(mode=0o700)
    (raw / "one.json").write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(runner, "EXPECTED_RAW_ATTEMPT_FILENAMES", ("one.json",))
    return root, identity, raw


def test_exact_inventory_positive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, identity, _ = _mini_inventory_root(tmp_path, monkeypatch)
    snapshot = runner._scan_success_inventory(
        root,
        identity,
        expected_root_entries=(runner.RAW_ATTEMPT_DIRECTORY,),
    )
    assert len(snapshot.rows) == 1
    assert snapshot.rows[0].logical_ref == "one.json"


@pytest.mark.parametrize("attack", ("extra", "directory", "symlink", "fifo"))
def test_inventory_unknown_and_nonregular_attacks_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    if attack == "fifo" and not hasattr(os, "mkfifo"):
        pytest.fail("POSIX mkfifo required by the supported runner environment")
    root, identity, raw = _mini_inventory_root(tmp_path, monkeypatch)
    if attack == "extra":
        (raw / "extra.json").write_text("{}\n")
    elif attack == "directory":
        (raw / "one.json").unlink()
        (raw / "one.json").mkdir()
    elif attack == "symlink":
        target = raw / "target.json"
        target.write_text("{}\n")
        (raw / "one.json").unlink()
        (raw / "one.json").symlink_to(target)
        monkeypatch.setattr(runner, "EXPECTED_RAW_ATTEMPT_FILENAMES", ("one.json", "target.json"))
    else:
        (raw / "one.json").unlink()
        os.mkfifo(raw / "one.json")
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._scan_success_inventory(
            root,
            identity,
            expected_root_entries=(runner.RAW_ATTEMPT_DIRECTORY,),
        )
    assert captured.value.reason == runner.REASON_INVENTORY_INVALID


def test_raw_inventory_mutation_after_public_write_removes_public_result(tmp_path: Path, monkeypatch) -> None:
    def add_unknown(path: Path) -> None:
        private_raw = tmp_path / "attempt-01" / runner.RAW_ATTEMPT_DIRECTORY
        (private_raw / "unknown.json").write_text("{}\n")

    monkeypatch.setattr(runner, "_POST_PUBLIC_WRITE_HOOK", add_unknown)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code == runner.REASON_INVENTORY_INVALID
    assert not (tmp_path / "safe-report.json").exists()


def test_same_byte_different_inode_raw_replacement_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def replace_member(path: Path) -> None:
        raw = tmp_path / "attempt-01" / runner.RAW_ATTEMPT_DIRECTORY
        member = raw / "tri_party_airline_bsep_validation.json"
        content = member.read_bytes()
        member.unlink()
        member.write_bytes(content)

    monkeypatch.setattr(runner, "_POST_PUBLIC_WRITE_HOOK", replace_member)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code == runner.REASON_INVENTORY_INVALID
    assert not (tmp_path / "safe-report.json").exists()


def test_mode_environments_remove_all_ambient_airline_controls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ambient = {
        key: "stale"
        for key in runner._AIRLINE_CONTROL_ENV_KEYS
    }
    ambient[runner._CREDENTIAL_ENV_KEYS[0]] = "opaque-test-value"
    ambient[runner._PROVIDER_TIMEOUT_ENV_KEY] = "20"
    monkeypatch.setitem(runner._os.__dict__, "environ", ambient)

    real = runner._collector_environment(
        runner.MODE_REAL,
        tmp_path / "real-raw",
    )
    injected = runner._collector_environment(
        runner.MODE_INJECTED,
        tmp_path / "injected-raw",
    )

    assert real[lane.ENV_REAL_PROVIDER] == "1"
    assert lane.ENV_FAKE_PROVIDER not in real
    assert injected[lane.ENV_FAKE_PROVIDER] == "1"
    assert lane.ENV_REAL_PROVIDER not in injected
    for environment, expected_delay in ((real, "2"), (injected, "0")):
        assert environment[lane.ENV_LANE] == "1"
        assert environment[lane.ENV_CAUSAL_BINDING] == "1"
        assert environment[lane.ENV_CRYPTO_ARTIFACT_SEAL] == "1"
        assert environment[lane.ENV_MODEL] == runner.MODEL_ID
        assert environment[lane.ENV_ALLOW_RAW] == "0"
        assert environment[lane.ENV_CALL_DELAY_SECONDS] == expected_delay


@pytest.mark.parametrize("target", ("private", "safe_output"))
def test_literal_dot_paths_are_rejected_before_callbacks(
    tmp_path: Path,
    target: str,
) -> None:
    calls: list[str] = []

    def provider(*args):
        calls.append("called")
        return "{}"

    private = (
        f"{tmp_path}/./attempt"
        if target == "private"
        else str(tmp_path / "attempt")
    )
    safe = (
        str(tmp_path / "safe.json")
        if target == "private"
        else f"{tmp_path}/./safe.json"
    )
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_INJECTED,
        attempt_number=1,
        private_output_directory=private,
        injected_provider=provider,
        injected_safe_report_output=safe,
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code == runner.REASON_PRIVATE_PATH_INVALID
    assert calls == []
    assert not (tmp_path / "attempt").exists()


def test_attempt_identity_binds_complete_section_nine_geometry(tmp_path: Path) -> None:
    head = "8e27d62cafa4e3096fb03ba22361391c46759327"
    first_root = tmp_path / "attempt-a"
    second_root = tmp_path / "attempt-b"
    first = runner._build_attempt_identity(
        execution_mode=runner.MODE_REAL,
        execution_head=head,
        attempt_number=1,
        private_output_directory=first_root,
    )
    second = runner._build_attempt_identity(
        execution_mode=runner.MODE_REAL,
        execution_head=head,
        attempt_number=1,
        private_output_directory=second_root,
    )
    required = {
        "programme_id",
        "domain_id",
        "execution_head",
        "attempt_number",
        "run_id",
        "report_id",
        "source_task_id",
        "package_id",
        "logical_package_ref",
        "output_directory",
        "output_directory_sha256",
        "output_directory_ref",
        "provider_mode",
        "model_id",
        "expected_actor_count",
        "provider_call_budget",
    }
    assert required.issubset(first)
    assert first["package_id"] == f"airline_sealed_evidence:{binding.TRANSACTION_ID}"
    assert first["logical_package_ref"] == runner.RAW_ATTEMPT_DIRECTORY
    assert first["output_directory_ref"] == f"airline/{lane.RUN_ID}/sealed_evidence"
    assert first["output_directory"] == str(first_root)
    assert first["output_directory_sha256"] == hashlib.sha256(
        str(first_root).encode("utf-8")
    ).hexdigest()
    assert first["provider_call_budget"] == first["expected_actor_count"] == 12
    assert first["attempt_id"] != second["attempt_id"]


@pytest.mark.parametrize("attack", ("same_inode", "replacement"))
def test_attempt_identity_mutation_or_replacement_prevents_collection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    attack: str,
) -> None:
    calls: list[str] = []

    def mutate(path: Path) -> None:
        content = path.read_bytes()
        if attack == "same_inode":
            changed = bytearray(content)
            changed[5] = ord("x") if changed[5] != ord("x") else ord("y")
            with path.open("r+b") as handle:
                handle.write(changed)
        else:
            path.unlink()
            path.write_bytes(content)

    def provider(*args):
        calls.append("called")
        return "{}"

    monkeypatch.setattr(runner, "_POST_ATTEMPT_IDENTITY_WRITE_HOOK", mutate)
    result = _run(tmp_path, provider=provider)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.private_attempt_preserved is False
    assert (
        result.private_attempt_preservation_state
        == runner._PRESERVATION_RETAINED_UNPROVED
    )
    assert calls == []
    assert not (tmp_path / "safe-report.json").exists()


@pytest.mark.parametrize(
    "failure",
    ("short_write", "zero_write", "fsync", "reread", "semantic", "replacement"),
)
def test_private_document_write_and_proof_failures_leave_no_false_document(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    failure: str,
) -> None:
    root, identity, plain = _private_document_context(tmp_path)
    leaf = "bounded_private_document.json"
    original_write = os.write
    if failure == "short_write":
        def lying_short_write(fd, data):
            original_write(fd, data[: max(1, len(data) // 2)])
            return len(data)

        monkeypatch.setattr(runner, "_WRITE", lying_short_write)
    elif failure == "zero_write":
        monkeypatch.setattr(runner, "_WRITE", lambda fd, data: 0)
    elif failure == "fsync":
        monkeypatch.setattr(
            runner,
            "_FSYNC",
            lambda fd: (_ for _ in ()).throw(OSError("private")),
        )
    elif failure == "reread":
        monkeypatch.setattr(runner, "_read_all", lambda fd: b"{}\n")
    elif failure == "semantic":
        monkeypatch.setattr(runner, "_strict_json", lambda content: {"changed": True})
    else:
        def replace_document(root_fd: int, name: str) -> None:
            path = root / name
            content = path.read_bytes()
            path.unlink()
            path.write_bytes(content)

        monkeypatch.setattr(
            runner,
            "_PRIVATE_DOCUMENT_POST_CLOSE_HOOK",
            replace_document,
        )

    with pytest.raises(runner._RunnerFailure) as captured:
        runner._write_private_document(root, identity, leaf, plain)
    assert captured.value.reason == runner.REASON_PRIVATE_METADATA_FAILED
    if failure != "replacement":
        assert not (root / leaf).exists()


def test_private_document_unproved_close_fails_closed_without_descriptor_leak(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root, identity, plain = _private_document_context(tmp_path)
    created_fds: set[int] = set()
    original_open = runner._OPEN
    original_close = os.close

    def tracked_open(*args, **kwargs):
        fd = original_open(*args, **kwargs)
        if len(args) > 1 and args[1] & os.O_CREAT:
            created_fds.add(fd)
        return fd

    def noop_created_close(fd: int) -> None:
        if fd not in created_fds:
            original_close(fd)

    def fail_created_raw_close(fd: int) -> None:
        if fd in created_fds:
            raise OSError("private")
        original_close(fd)

    monkeypatch.setattr(runner, "_OPEN", tracked_open)
    monkeypatch.setattr(runner, "_CLOSE", noop_created_close)
    monkeypatch.setattr(runner, "_RAW_CLOSE", fail_created_raw_close)
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._write_private_document(
            root,
            identity,
            "close-proof.json",
            plain,
        )
    assert captured.value.reason == runner.REASON_PRIVATE_METADATA_FAILED
    monkeypatch.setattr(runner, "_CLOSE", original_close)
    monkeypatch.setattr(runner, "_RAW_CLOSE", original_close)
    for fd in created_fds:
        try:
            original_close(fd)
        except OSError:
            pass
    assert not (root / "close-proof.json").exists()


def test_failed_preservation_metadata_never_claims_preserved(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    base = runner._build_injected_provider_v01()
    original_writer = runner._write_private_document

    def provider(actor_id, prompt, metadata):
        raise RuntimeError("private")

    def bounded_writer(root, identity, leaf, plain, **kwargs):
        if leaf != runner.ATTEMPT_IDENTITY_FILE:
            raise runner._RunnerFailure(
                runner.REASON_PRIVATE_METADATA_FAILED,
                "private_metadata",
            )
        return original_writer(root, identity, leaf, plain, **kwargs)

    monkeypatch.setattr(runner, "_write_private_document", bounded_writer)
    result = _run(tmp_path, provider=provider)
    assert base is not None
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.private_attempt_preserved is False
    assert (
        result.private_attempt_preservation_state
        == runner._PRESERVATION_RETAINED_UNPROVED
    )
    assert not (tmp_path / "safe-report.json").exists()


@pytest.mark.parametrize(
    "attack",
    ("raw_directory_replacement", "raw_mutation", "raw_chmod", "unknown_root_entry"),
)
def test_failure_preservation_requires_identical_bounded_snapshots(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    attack: str,
) -> None:
    base = runner._build_injected_provider_v01()

    def provider(actor_id, prompt, metadata):
        raise RuntimeError("private provider failure")

    def mutate(root: Path) -> None:
        raw = root / runner.RAW_ATTEMPT_DIRECTORY
        if attack == "raw_directory_replacement":
            retained = root / "retained-original-raw"
            raw.rename(retained)
            raw.mkdir(mode=0o700)
        elif attack == "raw_mutation":
            leaves = sorted(raw.iterdir())
            if leaves:
                with leaves[0].open("ab") as handle:
                    handle.write(b" ")
            else:
                (raw / "foreign.json").write_text("{}\n", encoding="utf-8")
        elif attack == "raw_chmod":
            raw.chmod(0o700)
        else:
            (root / "unknown-private-object").write_text("foreign", encoding="utf-8")

    monkeypatch.setattr(runner, "_FAILURE_PRESERVATION_HOOK", mutate)
    result = _run(tmp_path, provider=provider)
    assert base is not None
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.private_attempt_preserved is False
    assert result.private_attempt_preservation_state == runner._PRESERVATION_RETAINED_UNPROVED
    assert not (tmp_path / "safe-report.json").exists()
    if attack == "raw_directory_replacement":
        assert (tmp_path / "attempt-01" / runner.RAW_ATTEMPT_DIRECTORY).is_dir()


def test_forged_existing_failure_inventory_with_matching_digest_is_not_preserved(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def plant(path: Path) -> None:
        root = path.parent
        forged = {
            "inventory_version": "v0.1",
            "validation_status": runner.STATUS_FAIL_CLOSED,
            "raw_attempt_file_count": 0,
            "ordered_files": [],
            "aggregate_inventory_digest": runner._inventory_digest(()),
            "raw_bodies_copied_to_public_evidence": True,
        }
        inventory = root / runner.PRIVATE_INVENTORY_FILE
        inventory.write_bytes(runner._canonical_json_line(forged))
        inventory.chmod(0o600)

    monkeypatch.setattr(runner, "_POST_ATTEMPT_IDENTITY_WRITE_HOOK", plant)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.private_attempt_preservation_state == runner._PRESERVATION_RETAINED_UNPROVED
    assert not (tmp_path / "safe-report.json").exists()


def test_failure_gate_inode_replacement_cannot_be_claimed_preserved(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    original_hook = runner._PRIVATE_DOCUMENT_POST_CLOSE_HOOK

    def replace_gate(root_fd: int, leaf: str) -> None:
        if leaf != runner.GENERATION_GATE_FILE:
            return
        content_fd = os.open(leaf, os.O_RDONLY, dir_fd=root_fd)
        try:
            content = os.read(content_fd, 1_000_000)
        finally:
            os.close(content_fd)
        os.unlink(leaf, dir_fd=root_fd)
        replacement = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=root_fd)
        try:
            os.write(replacement, content)
        finally:
            os.close(replacement)

    monkeypatch.setattr(runner, "_PRIVATE_DOCUMENT_POST_CLOSE_HOOK", replace_gate)
    result = _run(
        tmp_path,
        provider=lambda actor_id, prompt, metadata: (_ for _ in ()).throw(
            RuntimeError("private")
        ),
    )
    assert original_hook is None
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.private_attempt_preservation_state == runner._PRESERVATION_RETAINED_UNPROVED
    assert (tmp_path / "attempt-01" / runner.GENERATION_GATE_FILE).exists()
    assert not (tmp_path / "safe-report.json").exists()


@pytest.mark.parametrize(
    ("attack", "expected_base_calls"),
    (
        ("unknown", 0),
        ("reordered", 0),
        ("skipped", 0),
        ("duplicate", 1),
        ("thirteenth", 12),
    ),
)
def test_provider_order_attacks_stop_before_base_invocation(
    attack: str,
    expected_base_calls: int,
) -> None:
    base_calls: list[str] = []
    observed: list[str] = []
    started: list[str] = []
    completed: list[str] = []

    def base(actor_id, prompt, metadata):
        base_calls.append(actor_id)
        return "{}"

    provider = runner._provider_for_mode(
        runner.MODE_INJECTED,
        base,
        observed,
        started,
        completed,
        None,
    )
    with pytest.raises(ValueError, match="^provider_call_geometry_invalid$"):
        if attack == "unknown":
            provider("unknown_actor", "", {})
        elif attack in ("reordered", "skipped"):
            provider(EXPECTED_ACTOR_IDS[1], "", {})
        elif attack == "duplicate":
            provider(EXPECTED_ACTOR_IDS[0], "", {})
            provider(EXPECTED_ACTOR_IDS[0], "", {})
        else:
            for actor_id in EXPECTED_ACTOR_IDS:
                provider(actor_id, "", {})
            provider("thirteenth_actor", "", {})
    assert len(base_calls) == expected_base_calls


def test_progress_failure_before_base_call_reports_zero_actual_invocations(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    base_calls: list[str] = []

    def base(actor_id, prompt, metadata):
        base_calls.append(actor_id)
        return "{}"

    safe_path, _ = _patch_simulated_real(
        monkeypatch,
        tmp_path,
        provider_builder=lambda model: base,
    )

    def fail_before_call(event: dict[str, object]) -> None:
        if event["event"] == "call_started":
            raise RuntimeError("private progress failure")

    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=tmp_path / "progress-failed-attempt",
        progress_sink=fail_before_call,
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.wrapper_callback_observed_count == 1
    assert result.provider_callback_started_count == 0
    assert result.provider_callback_completed_count == 0
    assert result.actual_provider_call_count == 0
    assert result.actual_network_call_count == 0
    assert result.actual_gemini_call_count == 0
    assert result.live_collection_performed is False
    assert result.private_attempt_preservation_state in (
        runner._PRESERVATION_PRESERVED,
        runner._PRESERVATION_RETAINED_UNPROVED,
    )
    assert base_calls == []
    assert not safe_path.exists()


def test_metadata_conversion_failure_precedes_base_provider_start_in_simulated_real(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    base_calls: list[str] = []

    class RaisingMapping(Mapping):
        def __getitem__(self, key):
            raise RuntimeError("private metadata access")

        def __iter__(self):
            raise RuntimeError("private metadata iteration")

        def __len__(self):
            return 1

    def base(actor_id, prompt, metadata):
        base_calls.append(actor_id)
        return "{}"

    def collector(**kwargs):
        kwargs["provider"](
            EXPECTED_ACTOR_IDS[0],
            "bounded",
            RaisingMapping(),
        )
        raise AssertionError("unreachable")

    safe_path, _ = _patch_simulated_real(
        monkeypatch,
        tmp_path,
        provider_builder=lambda model: base,
    )
    monkeypatch.setattr(runner, "_COLLECTOR", collector)
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=tmp_path / "metadata-failed-attempt",
    )
    assert result.wrapper_callback_observed_count == 1
    assert base_calls == []
    assert result.provider_callback_started_count == 0
    assert result.provider_callback_completed_count == 0
    assert (
        result.actual_provider_call_count,
        result.actual_network_call_count,
        result.actual_gemini_call_count,
    ) == (0, 0, 0)
    assert result.live_collection_performed is False
    assert result.actual_external_operation_status == runner._EXTERNAL_NOT_PERFORMED
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.official_evidence_eligible is False
    assert result.retry_count == 0
    assert not safe_path.exists()


def test_canonical_report_cannot_pass_with_noncanonical_observed_calls(
    monkeypatch: pytest.MonkeyPatch,
    source_report,
    tmp_path: Path,
) -> None:
    def collector(**kwargs):
        for actor_id in EXPECTED_ACTOR_IDS[:-1]:
            kwargs["provider"](actor_id, "bounded", {})
        return deepcopy(source_report)

    monkeypatch.setattr(runner, "_COLLECTOR", collector)
    result = _run(tmp_path, provider=lambda actor_id, prompt, metadata: "{}")
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code == runner.REASON_SOURCE_GEOMETRY_INVALID
    assert result.provider_callback_started_count == 11
    assert result.provider_callback_completed_count == 11
    assert not (tmp_path / "safe-report.json").exists()


def test_real_provider_metadata_disables_schema_fallback_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[dict[str, object]] = []

    def base(actor_id, prompt, metadata):
        received.append(dict(metadata))
        return "{}"

    monkeypatch.setattr(runner, "_REAL_PROVIDER_BUILDER", lambda model: base)
    started: list[str] = []
    completed: list[str] = []
    observed: list[str] = []
    provider = runner._provider_for_mode(
        runner.MODE_REAL,
        None,
        observed,
        started,
        completed,
        None,
    )
    metadata = {"provider_response_schema": {"type": "object"}, "bounded": True}
    provider(EXPECTED_ACTOR_IDS[0], "canonical", metadata)
    assert metadata["provider_response_schema"] == {"type": "object"}
    assert received == [{"bounded": True}]
    assert started == completed == [EXPECTED_ACTOR_IDS[0]]


def test_malformed_report_text_never_reaches_progress(
    monkeypatch: pytest.MonkeyPatch,
    source_report,
    tmp_path: Path,
) -> None:
    private_text = "attacker /Users/admin/private Traceback: 0x1234abcd"

    def collector(**kwargs):
        for actor_id in EXPECTED_ACTOR_IDS:
            kwargs["provider"](actor_id, "bounded", {})
        report = deepcopy(source_report)
        report["semantic_actor_reports"][0]["actor_id"] = private_text
        report["semantic_actor_reports"][0]["validation_status"] = private_text
        return report

    progress: list[dict[str, object]] = []
    monkeypatch.setattr(runner, "_COLLECTOR", collector)
    result = _run(
        tmp_path,
        provider=lambda actor_id, prompt, metadata: "{}",
        progress=progress.append,
    )
    rendered = json.dumps(progress, sort_keys=True)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert private_text not in rendered
    assert not any(row["event"] == "local_validation_completed" for row in progress)


def test_simulated_real_mode_traverses_canonical_path_without_network(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    safe_path, guards = _patch_simulated_real(monkeypatch, tmp_path)
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=tmp_path / "real-attempt",
    )
    assert result.final_status == runner.STATUS_PASS
    assert result.live_collection_performed is True
    assert result.official_evidence_eligible is True
    assert result.public_safe_report_state == runner._PUBLICATION_PRESENT
    assert result.actual_external_operation_status == runner._EXTERNAL_VERIFIED
    assert (
        result.actual_provider_call_count,
        result.actual_network_call_count,
        result.actual_gemini_call_count,
        result.actual_real_world_effects_count,
    ) == (12, 12, 12, 0)
    assert result.provider_callback_started_count == 12
    assert result.provider_callback_completed_count == 12
    assert guards == ["initial", "8e27d62cafa4e3096fb03ba22361391c46759327"]
    safe = json.loads(safe_path.read_text(encoding="utf-8"))
    assert safe["provider_mode"] == lane.PROVIDER_MODE_REAL


def test_stale_fake_environment_cannot_control_simulated_real_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    stale = {
        key: "conflicting"
        for key in runner._AIRLINE_CONTROL_ENV_KEYS
    }
    monkeypatch.setitem(runner._os.__dict__, "environ", stale)
    safe_path, _ = _patch_simulated_real(monkeypatch, tmp_path)
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=tmp_path / "stale-environment-attempt",
    )
    safe = json.loads(safe_path.read_text(encoding="utf-8"))
    assert result.final_status == runner.STATUS_PASS
    assert safe["provider_mode"] == lane.PROVIDER_MODE_REAL
    assert result.provider_callback_started_count == 12


def test_simulated_real_failure_reports_bounded_prefix_without_network_claim(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    base = runner._build_injected_provider_v01()
    calls: list[str] = []

    def failing(actor_id, prompt, metadata):
        calls.append(actor_id)
        if len(calls) == 4:
            raise RuntimeError("private")
        return base(actor_id, prompt, metadata)

    safe_path, _ = _patch_simulated_real(
        monkeypatch,
        tmp_path,
        provider_builder=lambda model: failing,
    )
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=tmp_path / "failed-real-attempt",
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.live_collection_performed is True
    assert result.official_evidence_eligible is False
    assert result.provider_callback_started_count == 4
    assert result.provider_callback_completed_count == 3
    assert result.semantic_actor_call_count == 4
    assert result.retry_count == 0
    assert result.actual_provider_call_count == 4
    assert result.actual_network_call_count == 0
    assert result.actual_gemini_call_count == 0
    assert result.actual_external_operation_status == runner._EXTERNAL_UNVERIFIED_PARTIAL
    assert result.public_safe_report_state == runner._PUBLICATION_ABSENT
    assert not safe_path.exists()


@pytest.mark.parametrize(
    "failure",
    ("wrong_venv", "missing_key", "multiple_keys", "sdk", "timeout"),
)
def test_real_local_preconditions_fail_closed_without_reading_real_credentials(
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    environment = {
        runner._CREDENTIAL_ENV_KEYS[0]: "opaque-test-value",
        runner._PROVIDER_TIMEOUT_ENV_KEY: "20",
    }
    monkeypatch.setattr(runner._sys, "prefix", str(runner._REPOSITORY_VENV_PREFIX))
    monkeypatch.setattr(runner._sys, "base_prefix", "/usr/local/base-python")
    monkeypatch.setattr(
        runner._importlib,
        "import_module",
        lambda name: SimpleNamespace(HttpOptions=lambda **kwargs: object()),
    )
    if failure == "wrong_venv":
        monkeypatch.setattr(runner._sys, "prefix", "/usr/local/foreign-venv")
    elif failure == "missing_key":
        environment.pop(runner._CREDENTIAL_ENV_KEYS[0])
    elif failure == "multiple_keys":
        environment[runner._CREDENTIAL_ENV_KEYS[1]] = "second-opaque-value"
    elif failure == "sdk":
        monkeypatch.setattr(
            runner._importlib,
            "import_module",
            lambda name: (_ for _ in ()).throw(ImportError("private")),
        )
    else:
        environment[runner._PROVIDER_TIMEOUT_ENV_KEY] = "0"
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._require_real_local_preconditions(environment)
    assert captured.value.reason == runner.REASON_LOCAL_PRECONDITION_FAILED
    assert "opaque" not in str(captured.value)


def test_real_local_preconditions_accept_one_synthetic_credential_boolean(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment = {
        runner._CREDENTIAL_ENV_KEYS[0]: "opaque-test-value",
        runner._PROVIDER_TIMEOUT_ENV_KEY: "20",
    }
    observed: list[int] = []
    monkeypatch.setattr(runner._sys, "prefix", str(runner._REPOSITORY_VENV_PREFIX))
    monkeypatch.setattr(runner._sys, "base_prefix", "/usr/local/base-python")
    monkeypatch.setattr(
        runner._importlib,
        "import_module",
        lambda name: SimpleNamespace(
            HttpOptions=lambda *, timeout: observed.append(timeout)
        ),
    )
    result = runner._require_real_local_preconditions(environment)
    assert result == runner._RealPreconditionResult(20, 1)
    assert observed == [20_000]


@pytest.mark.parametrize(
    "raw_timeout",
    ("", "0", "-1", "+1", "01", "121", "999", "garbage", " 20", "20 ", "1.0"),
)
def test_real_local_preconditions_reject_noncanonical_raw_timeout_values(
    monkeypatch: pytest.MonkeyPatch,
    raw_timeout: str,
) -> None:
    environment = {
        runner._CREDENTIAL_ENV_KEYS[0]: "opaque-test-value",
        runner._PROVIDER_TIMEOUT_ENV_KEY: raw_timeout,
    }
    monkeypatch.setattr(runner._sys, "prefix", str(runner._REPOSITORY_VENV_PREFIX))
    monkeypatch.setattr(runner._sys, "base_prefix", "/usr/local/base-python")
    monkeypatch.setattr(
        runner._importlib,
        "import_module",
        lambda name: SimpleNamespace(HttpOptions=lambda **kwargs: object()),
    )
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._require_real_local_preconditions(environment)
    assert captured.value.reason == runner.REASON_LOCAL_PRECONDITION_FAILED


@pytest.mark.parametrize(("raw_timeout", "expected"), ((None, 20), ("1", 1), ("20", 20), ("120", 120)))
def test_real_local_preconditions_accept_exact_timeout_domain(
    monkeypatch: pytest.MonkeyPatch,
    raw_timeout: str | None,
    expected: int,
) -> None:
    environment = {runner._CREDENTIAL_ENV_KEYS[0]: "opaque-test-value"}
    if raw_timeout is not None:
        environment[runner._PROVIDER_TIMEOUT_ENV_KEY] = raw_timeout
    observed: list[int] = []
    monkeypatch.setattr(runner._sys, "prefix", str(runner._REPOSITORY_VENV_PREFIX))
    monkeypatch.setattr(runner._sys, "base_prefix", "/usr/local/base-python")
    monkeypatch.setattr(
        runner._importlib,
        "import_module",
        lambda name: SimpleNamespace(
            HttpOptions=lambda *, timeout: observed.append(timeout)
        ),
    )
    result = runner._require_real_local_preconditions(environment)
    assert result.timeout_seconds == expected
    assert observed == [expected * 1000]


def test_local_precondition_failure_creates_no_attempt_and_no_provider(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        runner,
        "_require_real_local_preconditions",
        lambda environment: (_ for _ in ()).throw(
            runner._RunnerFailure(
                runner.REASON_LOCAL_PRECONDITION_FAILED,
                "local_precondition",
            )
        ),
    )
    monkeypatch.setattr(
        runner,
        "_REAL_PROVIDER_BUILDER",
        lambda model: calls.append(model),
    )
    root = tmp_path / "attempt"
    result = runner.run_two_domain_airline_all_real_program_v01(
        execution_mode=runner.MODE_REAL,
        attempt_number=1,
        private_output_directory=root,
    )
    assert result.reason_code == runner.REASON_LOCAL_PRECONDITION_FAILED
    assert calls == []
    assert not root.exists()


@pytest.mark.parametrize(
    "attack",
    (
        "branch",
        "short_head",
        "head_mismatch",
        "dirty",
        "cached",
        "missing_tracked",
        "wrong_root",
        "foreign_git_dir",
        "timeout",
    ),
)
def test_repository_provenance_attacks_fail_closed_before_provider(
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    values = _git_ready_values()
    monkeypatch.setitem(runner._os.__dict__, "environ", {})
    if attack == "branch":
        values[("branch", "--show-current")] = "feature"
    elif attack == "short_head":
        values[("rev-parse", "HEAD")] = "8e27d62"
    elif attack == "head_mismatch":
        values[("rev-parse", "origin/main")] = "0" * 40
    elif attack == "dirty":
        values[("status", "--porcelain", "--untracked-files=all")] = "?? x"
    elif attack == "cached":
        values[("diff", "--cached", "--name-only")] = "x"
    elif attack == "missing_tracked":
        values[next(key for key in values if key[0] == "ls-files")] = ""
    elif attack == "wrong_root":
        values[("rev-parse", "--show-toplevel")] = "/private/tmp"
    elif attack == "foreign_git_dir":
        monkeypatch.setitem(runner._os.__dict__, "environ", {"GIT_DIR": "/private"})
    if attack == "timeout":
        monkeypatch.setattr(
            runner,
            "_git_text",
            lambda *args: (_ for _ in ()).throw(
                runner._subprocess.TimeoutExpired("git", 5)
            ),
        )
    else:
        monkeypatch.setattr(runner, "_git_text", lambda *args: values[args])
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._require_real_repository_ready()
    assert captured.value.reason == runner.REASON_REPOSITORY_NOT_READY


def test_git_subprocess_uses_c_root_timeout_and_sanitized_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}
    monkeypatch.setitem(
        runner._os.__dict__,
        "environ",
        {"GIT_DIR": "/foreign", "GIT_CONFIG_COUNT": "9", "SAFE": "yes"},
    )

    def fake_run(command, **kwargs):
        observed.update({"command": command, **kwargs})
        return SimpleNamespace(stdout="main\n")

    monkeypatch.setattr(runner._subprocess, "run", fake_run)
    assert runner._git_text("branch", "--show-current") == "main"
    assert observed["command"][:3] == (
        "git",
        "-C",
        str(runner._REPOSITORY_ROOT),
    )
    assert observed["timeout"] == runner._GIT_TIMEOUT_SECONDS
    environment = observed["env"]
    assert "GIT_DIR" not in environment
    assert "GIT_CONFIG_COUNT" not in environment
    assert environment["GIT_OPTIONAL_LOCKS"] == "0"


@pytest.mark.parametrize(
    "mutation",
    (
        "run_id",
        "report_id",
        "lane_id",
        "deterministic_source",
        "actor_index",
        "actor_side",
        "actor_group",
        "actor_parent",
        "vertical_order",
        "root_order",
        "bsep_packet",
        "bsep_projection_lineage",
        "candidate_set_ref",
        "snapshot_id",
        "snapshot_digest",
        "visible_candidates",
        "airline_candidates",
        "client_candidates",
        "causal_bsep",
        "transaction_id",
        "semantic_recommendation",
        "client_selection",
        "airline_resolution",
        "hold_offer",
        "causal_default",
        "causal_silent_fallback",
        "bridge_transaction",
        "bridge_causal_validation",
        "bridge_status",
        "bridge_direct_override",
        "bridge_default",
        "bridge_silent_fallback",
        "bridge_authority",
        "bridge_effect",
        "deterministic_status",
        "deterministic_offer",
        "deterministic_corridor_status",
        "deterministic_corridor_count",
        "deterministic_effect",
    ),
)
def test_exact_source_lineage_mutation_matrix_fails_closed(
    source_report,
    mutation: str,
) -> None:
    report = deepcopy(source_report)
    causal = report["semantic_to_contract_causal_binding_v0_1"]
    bridge = report["semantic_to_contract_deterministic_bridge"]
    deterministic = report["integrated_deterministic_airline_transaction"]
    if mutation in ("run_id", "report_id", "lane_id"):
        report[mutation] = f"changed_{mutation}"
    elif mutation == "deterministic_source":
        report["deterministic_source"]["run_id"] = "changed"
    elif mutation == "actor_index":
        report["semantic_actor_reports"][0]["actor_index"] = 2
    elif mutation == "actor_side":
        report["semantic_actor_reports"][0]["side"] = "changed"
    elif mutation == "actor_group":
        report["semantic_actor_reports"][0]["group"] = "changed"
    elif mutation == "actor_parent":
        report["semantic_actor_reports"][5]["parent_actor_id"] = "changed"
    elif mutation == "vertical_order":
        rows = list(report["vertical_fractal_dependencies"])
        rows[0], rows[1] = rows[1], rows[0]
        report["vertical_fractal_dependencies"] = tuple(rows)
    elif mutation == "root_order":
        rows = list(report["root_boundaries"])
        rows[0], rows[1] = rows[1], rows[0]
        report["root_boundaries"] = tuple(rows)
    elif mutation == "bsep_packet":
        report["bsep_membrane"]["bsep_packet_id"] = "changed"
    elif mutation == "bsep_projection_lineage":
        report["bsep_side_projections"]["airline_bsep_projection"][
            "source_bsep_packet_id"
        ] = "changed"
    elif mutation == "candidate_set_ref":
        causal["source_candidate_set_ref"] = "changed"
    elif mutation == "snapshot_id":
        causal["source_candidate_set_snapshot_id"] = "changed"
    elif mutation == "snapshot_digest":
        causal["source_candidate_set_digest"] = "0" * 64
    elif mutation == "visible_candidates":
        causal["visible_candidate_ids"] = ()
    elif mutation == "airline_candidates":
        causal["airline_valid_candidate_ids"] = ()
    elif mutation == "client_candidates":
        causal["client_hard_compatible_candidate_ids"] = ()
    elif mutation == "causal_bsep":
        causal["actual_airline_bsep_projection_ref"] = "changed"
    elif mutation == "transaction_id":
        causal["transaction_id"] = "changed"
    elif mutation == "semantic_recommendation":
        causal["semantic_recommendation_id"] = binding.OFFER_B_ID
    elif mutation == "client_selection":
        causal["client_root_selected_offer_id"] = binding.OFFER_B_ID
    elif mutation == "airline_resolution":
        causal["airline_root_resolved_offer_id"] = binding.OFFER_B_ID
    elif mutation == "hold_offer":
        causal["hold_contract_offer_id"] = binding.OFFER_B_ID
    elif mutation == "causal_default":
        causal["default_offer_used"] = True
    elif mutation == "causal_silent_fallback":
        causal["silent_fallback_used"] = True
    elif mutation == "bridge_transaction":
        bridge["transaction_id"] = "changed"
    elif mutation == "bridge_causal_validation":
        bridge["causal_report_validation_accepted"] = False
    elif mutation == "bridge_status":
        bridge["bridge_status"] = runner.STATUS_FAIL_CLOSED
    elif mutation == "bridge_direct_override":
        bridge["direct_offer_override_used"] = True
    elif mutation == "bridge_default":
        bridge["default_offer_used"] = True
    elif mutation == "bridge_silent_fallback":
        bridge["silent_fallback_used"] = True
    elif mutation == "bridge_authority":
        bridge["provider_created_authority_count"] = 1
    elif mutation == "bridge_effect":
        bridge["real_world_effects_count"] = 1
    elif mutation == "deterministic_status":
        deterministic["collection_status"] = runner.STATUS_FAIL_CLOSED
    elif mutation == "deterministic_offer":
        deterministic["selected_offer_id"] = binding.OFFER_B_ID
    elif mutation == "deterministic_corridor_status":
        deterministic["corridor_final_status"] = runner.STATUS_FAIL_CLOSED
    elif mutation == "deterministic_corridor_count":
        deterministic["corridor_execution_count"] = 2
    else:
        deterministic["real_world_effects_count"] = 1
    _assert_source_invalid(report)


@pytest.mark.parametrize(
    "field_name",
    (
        "transaction_id",
        "root_owner",
        "depends_on",
        "evidence_class",
        "authority_class",
        "canonical_hash_input",
    ),
)
def test_forged_ledger_entry_fails_fresh_canonical_validation(
    source_report,
    field_name: str,
) -> None:
    report = dict(source_report)
    ledger_item = source_report["airline_transaction_artifact_ledger_v0_1"]
    entry = ledger_item.entries[0]
    changed = {
        "transaction_id": "changed-transaction",
        "root_owner": "ChangedRoot",
        "depends_on": ("foreign-artifact",),
        "evidence_class": "changed_evidence",
        "authority_class": "changed_authority",
        "canonical_hash_input": {"changed": True},
    }[field_name]
    changed_entry = replace(entry, **{field_name: changed})
    report["airline_transaction_artifact_ledger_v0_1"] = replace(
        ledger_item,
        entries=(changed_entry, *ledger_item.entries[1:]),
    )
    _assert_source_invalid(report)


def test_coherent_self_attested_ledger_forgery_fails_independent_source_identity(
    source_report,
) -> None:
    canonical = source_report["airline_transaction_artifact_ledger_v0_1"]
    canonical_identity = runner._ledger_collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
        source_bundle=_CANONICAL_SOURCE_CONTEXT["ledger_source_bundle"],
    )
    forged_ids = dict(canonical_identity.expected_artifact_ids)
    first_type = ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE[0]
    original_first_id = forged_ids[first_type]
    forged_ids[first_type] = "forged_airline_transaction_scope"
    forged_source_refs = replace(
        canonical_identity.expected_source_refs,
        source_run_ref="source_run:forged_self_attested",
    )
    forged_validation_refs = {
        key: tuple(value)
        for key, value in canonical_identity.expected_source_validation_refs_by_type.items()
    }
    semantic_type = "ValidatedAirlineSemanticSelectionEvidenceV01"
    forged_validation_refs[semantic_type] = (
        "forged_source_validation_ref",
        *forged_validation_refs[semantic_type][1:],
    )
    forged_source_identity = {
        key: dict(value)
        for key, value in canonical_identity.expected_source_identity_fields_by_type.items()
    }
    transaction_identity = dict(forged_source_identity[first_type])
    transaction_identity["source_run_ref"] = forged_source_refs.source_run_ref
    forged_source_identity[first_type] = transaction_identity
    forged_identity = replace(
        canonical_identity,
        expected_source_refs=forged_source_refs,
        expected_artifact_ids=forged_ids,
        expected_source_validation_refs_by_type=forged_validation_refs,
        expected_source_identity_fields_by_type=forged_source_identity,
    )
    transaction_facts = canonical.entries[0].canonical_hash_input["source_snapshot"]
    forged_entries = []
    for entry in canonical.entries:
        artifact_id = forged_ids[entry.artifact_type]
        dependencies = tuple(
            forged_ids[first_type] if item == original_first_id else item
            for item in entry.depends_on
        )
        forged_entries.append(
            ledger.build_airline_transaction_artifact_ledger_entry_from_source_v01(
                index=entry.ledger_index,
                artifact_type=entry.artifact_type,
                artifact_id=artifact_id,
                depends_on=dependencies,
                offer_id=binding.OFFER_A_ID,
                hold_id=transaction_facts["hold_id"],
                amount=transaction_facts["amount"],
                currency=transaction_facts["currency"],
                route_ref=transaction_facts["route_ref"],
                source_validation_refs=forged_validation_refs[entry.artifact_type],
                auxiliary_artifact_refs=tuple(
                    canonical_identity.expected_auxiliary_artifact_refs_by_type[
                        entry.artifact_type
                    ]
                ),
                source_identity_fields=forged_source_identity[entry.artifact_type],
            )
        )
    forged = replace(
        canonical,
        source_run_ref=forged_source_refs.source_run_ref,
        entries=tuple(forged_entries),
    )
    self_attested = ledger.validate_airline_transaction_artifact_ledger_v01(
        forged,
        expected_source_refs=forged_source_refs,
        expected_identity=forged_identity,
    )
    assert self_attested.validation_status == runner.STATUS_PASS
    _, independent, _ = runner._fresh_ledger_validation(
        forged,
        ledger_source_bundle=_CANONICAL_SOURCE_CONTEXT["ledger_source_bundle"],
        ledger_source_validation=_CANONICAL_SOURCE_CONTEXT[
            "ledger_source_validation"
        ],
    )
    assert independent.validation_status != runner.STATUS_PASS
    assert independent.validation_errors


@pytest.mark.parametrize(
    ("field_name", "changed"),
    (
        ("source_file_count", 8),
        ("ledger_entry_count", 18),
        ("dependency_edge_count", 28),
        ("root_final_count", 2),
        ("source_package_ref", "changed"),
        ("source_bundle_id", "changed"),
        ("manifest_artifact_ref", "changed.json"),
        ("verification_artifact_ref", "changed.json"),
        ("signature_mode", "SIGNED"),
        ("source_bytes_unchanged_after_audit", False),
        ("source_bytes_unchanged_after_collection", False),
        ("source_summary_frozen_before_crypto", False),
        ("source_summary_rewritten_after_crypto", True),
        ("e1_audit_count", 0),
        ("manifest_core_collection_count", 0),
        ("envelope_collection_count", 0),
        ("post_collection_snapshot_provider_call_count", 0),
        ("verification_count", 0),
        ("manifest_artifact_written_count", 0),
        ("verification_artifact_written_count", 0),
        ("ledger_recollection_count", 1),
        ("provider_calls_added_by_crypto_count", 1),
    ),
)
def test_exact_crypto_geometry_mutation_matrix_fails_closed(
    source_report,
    field_name: str,
    changed: object,
) -> None:
    report = deepcopy(source_report)
    report["airline_crypto_artifact_seal_integration"][field_name] = changed
    _assert_source_invalid(report)


@pytest.mark.parametrize(
    "field_name",
    ("manifest_core_hash", "chain_tail_hash", "source_package_hash"),
)
def test_valid_hex_crypto_summary_substitution_is_not_accepted(
    source_report,
    field_name: str,
) -> None:
    report = deepcopy(source_report)
    report["airline_crypto_artifact_seal_integration"][field_name] = "f" * 64
    _assert_source_invalid(report)


@pytest.mark.parametrize(
    "target",
    ("source", "ledger", "manifest", "verification"),
)
def test_raw_semantic_mutation_before_first_inventory_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    target: str,
) -> None:
    def mutate(root: Path, report: object, capture: object) -> None:
        if target == "source":
            leaf = capture.crypto_source_bundle.ordered_source_files_before_audit[1][0]
        elif target == "ledger":
            leaf = runner._RAW_LEDGER_FILE
        elif target == "manifest":
            leaf = lane.CRYPTO_MANIFEST_FILE
        else:
            leaf = lane.CRYPTO_VERIFICATION_FILE
        path = root / runner.RAW_ATTEMPT_DIRECTORY / leaf
        with path.open("ab") as handle:
            handle.write(b" ")

    monkeypatch.setattr(runner, "_POST_COLLECTOR_HOOK", mutate)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.reason_code == runner.REASON_SOURCE_GEOMETRY_INVALID
    assert not (tmp_path / "safe-report.json").exists()


def test_coordinated_summary_manifest_verification_hash_forgery_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    forged = "e" * 64

    def mutate(root: Path, report: object, capture: object) -> None:
        summary = report["airline_crypto_artifact_seal_integration"]
        for field_name in ("manifest_core_hash", "chain_tail_hash", "source_package_hash"):
            summary[field_name] = forged
        raw = root / runner.RAW_ATTEMPT_DIRECTORY
        for leaf in (lane.CRYPTO_MANIFEST_FILE, lane.CRYPTO_VERIFICATION_FILE):
            path = raw / leaf
            plain = json.loads(path.read_bytes())
            plain["manifest_core_hash"] = forged
            path.write_bytes(
                (json.dumps(plain, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
            )

    monkeypatch.setattr(runner, "_POST_COLLECTOR_HOOK", mutate)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "safe-report.json").exists()


def test_public_mutation_during_private_finalization_is_caught(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def mutate(path: Path) -> None:
        content = path.read_bytes()
        changed = bytearray(content)
        changed[-2] = ord("x") if changed[-2] != ord("x") else ord("y")
        path.chmod(0o600)
        with path.open("r+b") as handle:
            handle.write(changed)

    monkeypatch.setattr(runner, "_PRE_GENERATION_GATE_HOOK", mutate)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.public_safe_report_state == runner._PUBLICATION_ABSENT
    assert not (tmp_path / "safe-report.json").exists()


@pytest.mark.parametrize(
    "attack",
    (
        "inventory_same_inode",
        "inventory_replacement",
        "public_chmod",
        "public_replacement",
        "raw_drift",
        "raw_chmod",
    ),
)
def test_final_private_public_freeze_attacks_cannot_leave_promotable_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    attack: str,
) -> None:
    root = tmp_path / "attempt-01"
    safe = tmp_path / "safe-report.json"

    def mutate(path: Path) -> None:
        inventory = root / runner.PRIVATE_INVENTORY_FILE
        if attack == "inventory_same_inode":
            content = bytearray(inventory.read_bytes())
            content[-2] = ord("x")
            with inventory.open("r+b") as handle:
                handle.write(content)
        elif attack == "inventory_replacement":
            content = inventory.read_bytes()
            inventory.unlink()
            inventory.write_bytes(content)
            inventory.chmod(0o600)
        elif attack == "public_chmod":
            safe.chmod(0o600)
        elif attack == "public_replacement":
            content = safe.read_bytes()
            safe.unlink()
            safe.write_bytes(content)
            safe.chmod(0o400)
        elif attack == "raw_drift":
            raw_leaf = root / runner.RAW_ATTEMPT_DIRECTORY / runner._RAW_LEDGER_FILE
            with raw_leaf.open("ab") as handle:
                handle.write(b" ")
        else:
            (root / runner.RAW_ATTEMPT_DIRECTORY).chmod(0o700)

    monkeypatch.setattr(runner, "_PRE_GENERATION_GATE_HOOK", mutate)
    result = _run(tmp_path)
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.official_evidence_eligible is False
    assert result.public_safe_report_state != runner._PUBLICATION_PRESENT
    if attack == "public_replacement":
        assert result.public_safe_report_state == runner._PUBLICATION_ABSENCE_UNPROVEN
        assert safe.exists()
    else:
        assert not safe.exists()
    gate = root / runner.GENERATION_GATE_FILE
    if gate.exists():
        assert json.loads(gate.read_bytes())["final_source_status"] == runner.STATUS_FAIL_CLOSED


def test_public_release_failure_leaves_no_pass_gate_or_public_report(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        runner,
        "_release_owned_output",
        lambda owner: (_ for _ in ()).throw(runner._PublicCleanupFailure()),
    )
    result = _run(tmp_path)
    gate = json.loads(
        (tmp_path / "attempt-01" / runner.GENERATION_GATE_FILE).read_text()
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.public_safe_report_state == runner._PUBLICATION_ABSENT
    assert gate["final_source_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "safe-report.json").exists()


def test_final_pass_gate_failure_removes_public_report_and_pass_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    original = runner._write_private_document
    failed_once = False

    def fail_pass_gate(root, identity, leaf, plain, **kwargs):
        nonlocal failed_once
        if (
            leaf == runner.GENERATION_GATE_FILE
            and plain.get("final_source_status") == runner.STATUS_PASS
            and not failed_once
        ):
            failed_once = True
            raise runner._RunnerFailure(
                runner.REASON_PRIVATE_METADATA_FAILED,
                "private_metadata",
            )
        return original(root, identity, leaf, plain, **kwargs)

    monkeypatch.setattr(runner, "_write_private_document", fail_pass_gate)
    result = _run(tmp_path)
    gate = json.loads(
        (tmp_path / "attempt-01" / runner.GENERATION_GATE_FILE).read_text()
    )
    assert result.final_status == runner.STATUS_FAIL_CLOSED
    assert result.public_safe_report_state == runner._PUBLICATION_ABSENT
    assert gate["final_source_status"] == runner.STATUS_FAIL_CLOSED
    assert not (tmp_path / "safe-report.json").exists()


def test_generation_gate_hashes_bind_complete_private_public_chain(tmp_path: Path) -> None:
    result = _run(tmp_path)
    root = tmp_path / "attempt-01"
    attempt_bytes = (root / runner.ATTEMPT_IDENTITY_FILE).read_bytes()
    inventory_bytes = (root / runner.PRIVATE_INVENTORY_FILE).read_bytes()
    safe_bytes = (tmp_path / "safe-report.json").read_bytes()
    attempt = json.loads(attempt_bytes)
    gate = json.loads((root / runner.GENERATION_GATE_FILE).read_bytes())
    inventory = json.loads(inventory_bytes)
    raw = root / runner.RAW_ATTEMPT_DIRECTORY
    independent_rows = [
        {
            "logical_ref": leaf,
            "sha256": hashlib.sha256((raw / leaf).read_bytes()).hexdigest(),
            "byte_count": len((raw / leaf).read_bytes()),
        }
        for leaf in runner.EXPECTED_RAW_ATTEMPT_FILENAMES
    ]
    independent_digest = hashlib.sha256(
        runner._canonical_json_bytes_v01(independent_rows)
    ).hexdigest()
    safe_plain = json.loads(safe_bytes)

    def restore_tuples(value):
        if isinstance(value, list):
            return tuple(restore_tuples(item) for item in value)
        if isinstance(value, dict):
            return {key: restore_tuples(item) for key, item in value.items()}
        return value

    safe_execution = adapter.build_airline_safe_execution_projection_v01(
        restore_tuples(safe_plain)
    )
    identity_input = dict(attempt)
    attempt_id = identity_input.pop("attempt_id")
    assert attempt_id == hashlib.sha256(
        b"hedgehog.a1.airline.attempt.v01\0"
        + runner._canonical_json_bytes_v01(identity_input)
    ).hexdigest()
    assert gate["attempt_id"] == result.attempt_id == attempt_id
    assert gate["attempt_identity_sha256"] == hashlib.sha256(attempt_bytes).hexdigest()
    assert gate["private_inventory_document_sha256"] == hashlib.sha256(
        inventory_bytes
    ).hexdigest()
    assert inventory["ordered_files"] == independent_rows
    assert inventory["raw_attempt_file_count"] == len(independent_rows) == 72
    assert inventory["aggregate_inventory_digest"] == independent_digest
    assert gate["private_inventory_digest"] == independent_digest
    assert gate["safe_report_sha256"] == hashlib.sha256(safe_bytes).hexdigest()
    assert gate["safe_execution_id"] == safe_execution.safe_execution_id
    assert adapter.validate_airline_safe_execution_projection_v01(safe_execution) == ()
    assert gate["private_output_directory_sha256"] == attempt[
        "output_directory_sha256"
    ]
    assert attempt["output_directory_sha256"] == hashlib.sha256(
        str(root).encode()
    ).hexdigest()
    assert attempt["output_directory_ref"] == "airline/tri_party_airline_live_semantic_lane_v01/sealed_evidence"
    assert gate["execution_head"] == attempt["execution_head"]
    assert gate["provider_mode"] == lane.PROVIDER_MODE_FAKE
    assert gate["wrapper_callback_observed_prefix"] == list(EXPECTED_ACTOR_IDS)
    assert gate["base_provider_started_prefix"] == list(EXPECTED_ACTOR_IDS)
    assert gate["base_provider_completed_prefix"] == list(EXPECTED_ACTOR_IDS)
    assert gate["wrapper_callback_observed_count"] == 12
    assert gate["provider_callback_started_count"] == 12
    assert gate["provider_callback_completed_count"] == 12
    assert (
        gate["actual_provider_call_count"],
        gate["actual_network_call_count"],
        gate["actual_gemini_call_count"],
        gate["actual_real_world_effects_count"],
    ) == (0, 0, 0, 0)
    assert gate["official_evidence_eligible"] is False
    assert gate["package_created_count"] == 0
    assert gate["anchor_created_count"] == 0
    assert gate["replay_created_count"] == 0
    assert stat.S_IMODE((tmp_path / "safe-report.json").stat().st_mode) == 0o400
    assert str(tmp_path) not in (root / runner.GENERATION_GATE_FILE).read_text()


def test_same_private_path_is_single_use_without_attempt_advancement(tmp_path: Path) -> None:
    assert _run(tmp_path).final_status == runner.STATUS_PASS
    second = _run(tmp_path, safe_name="second-safe.json")
    assert second.reason_code == runner.REASON_PRIVATE_PATH_EXISTS
    assert not (tmp_path / "attempt_02").exists()
    assert not (tmp_path / "attempt-02").exists()


def test_real_repository_readiness_requires_synchronized_clean_tracked_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = {
        ("rev-parse", "--show-toplevel"): str(runner._REPOSITORY_ROOT),
        ("branch", "--show-current"): "main",
        ("rev-parse", "HEAD"): "8e27d62cafa4e3096fb03ba22361391c46759327",
        ("rev-parse", "origin/main"): "8e27d62cafa4e3096fb03ba22361391c46759327",
        ("status", "--porcelain", "--untracked-files=all"): "",
        ("diff", "--cached", "--name-only"): "",
        (
            "ls-files",
            "--error-unmatch",
            "demo/run_two_domain_airline_all_real_program_v01.py",
            "tests/test_two_domain_airline_all_real_program_v01_runner.py",
        ): (
            "demo/run_two_domain_airline_all_real_program_v01.py\n"
            "tests/test_two_domain_airline_all_real_program_v01_runner.py"
        ),
    }
    monkeypatch.setattr(runner, "_git_text", lambda *args: values[args])
    runner._require_real_repository_ready(
        "8e27d62cafa4e3096fb03ba22361391c46759327"
    )
    values[("status", "--porcelain", "--untracked-files=all")] = "?? unsafe"
    with pytest.raises(runner._RunnerFailure) as captured:
        runner._require_real_repository_ready(
            "8e27d62cafa4e3096fb03ba22361391c46759327"
        )
    assert captured.value.reason == runner.REASON_REPOSITORY_NOT_READY


@pytest.mark.parametrize(
    "argv",
    (
        (),
        ("--unknown",),
        ("--injected-deterministic", "--real-provider", "--attempt-number", "1", "--private-output-directory", "/private/tmp/x"),
        ("--injected-deterministic", "--attempt-number", "two", "--private-output-directory", "/private/tmp/x", "--safe-report-output", "/private/tmp/y"),
    ),
)
def test_cli_parser_failures_are_one_sanitized_json_line(
    argv: tuple[str, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert runner.main(list(argv)) == 2
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) == 1
    assert captured.err == ""
    plain = json.loads(lines[0])
    assert plain["final_status"] == runner.STATUS_FAIL_CLOSED
    assert plain["reason_code"] == runner.REASON_INVALID
    assert "usage" not in captured.out.casefold()
    assert "traceback" not in captured.out.casefold()
    assert "/private/tmp" not in captured.out


def test_cli_runtime_path_failure_is_sanitized(capsys: pytest.CaptureFixture[str]) -> None:
    owner_path = "/Users/admin/private/a1-attempt"
    argv = [
        "--injected-deterministic",
        "--attempt-number",
        "1",
        "--private-output-directory",
        owner_path,
        "--safe-report-output",
        "/Users/admin/private/safe.json",
    ]
    assert runner.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1
    assert owner_path not in captured.out
    assert "Traceback" not in captured.out


def test_injected_cli_happy_path_is_safe_and_not_official(tmp_path: Path, capsys) -> None:
    argv = [
        "--injected-deterministic",
        "--attempt-number",
        "1",
        "--private-output-directory",
        str(tmp_path / "attempt"),
        "--safe-report-output",
        str(tmp_path / "safe.json"),
    ]
    assert runner.main(argv) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    lines = captured.out.splitlines()
    assert len(lines) == 37
    summary = json.loads(lines[-1])
    assert summary["final_status"] == runner.STATUS_PASS
    assert summary["execution_mode"] == runner.MODE_INJECTED
    assert summary["live_collection_performed"] is False
    assert summary["official_evidence_eligible"] is False
    assert str(tmp_path) not in captured.out
    assert "raw_prompt" not in captured.out
    assert "raw_response" not in captured.out


def test_result_plain_projection_is_fresh_and_complete(tmp_path: Path) -> None:
    result = _run(tmp_path)
    first = runner.airline_a1_program_result_to_plain_dict_v01(result)
    second = runner.airline_a1_program_result_to_plain_dict_v01(result)
    assert tuple(first) == EXPECTED_RESULT_FIELDS
    assert first == second
    first["final_status"] = "changed"
    assert second["final_status"] == runner.STATUS_PASS


def test_static_runner_boundaries_and_single_collector_call_site() -> None:
    path = Path(runner.__file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not imports.intersection({"requests", "openai", "anthropic", "google", "vertexai", "httpx", "aiohttp", "socket", "tests"})
    assert source.count("_COLLECTOR(") == 1
    assert ".glob(" not in source
    assert ".rglob(" not in source
    assert "latest" not in source.casefold()
    assert "run_sealed_evidence_package_v01" not in source
    assert "run_sealed_evidence_anchor_v01" not in source
    assert "run_sealed_evidence_replay_v01" not in source
    assert "while attempt" not in source.casefold()
    assert "retry_count=0" in source


def test_static_tests_never_form_a_valid_real_provider_invocation() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for call in (
        node for node in ast.walk(tree) if isinstance(node, ast.Call)
    ):
        if isinstance(call.func, ast.Attribute) and call.func.attr == "main":
            rendered_call = ast.unparse(call)
            if "--real-provider" in rendered_call:
                assert "--injected-deterministic" in rendered_call
    real_test_functions = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rendered = ast.unparse(node)
            contains_real_run = any(
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr
                == "run_two_domain_airline_all_real_program_v01"
                and "execution_mode=runner.MODE_REAL" in ast.unparse(call)
                for call in ast.walk(node)
            )
            if contains_real_run:
                real_test_functions.append((node.name, rendered))
    assert real_test_functions
    for name, rendered in real_test_functions:
        if name == "test_real_mode_rejects_injected_callback_before_provider":
            continue
        if name == "test_local_precondition_failure_creates_no_attempt_and_no_provider":
            assert "_require_real_local_preconditions" in rendered
            assert "_REAL_PROVIDER_BUILDER" in rendered
            continue
        assert "_patch_simulated_real" in rendered
    assert 'monkeypatch.setattr(runner, "_REAL_PROVIDER_BUILDER"' in source
    assert not any(
        isinstance(node, ast.Attribute)
        and node.attr in ("environ", "getenv", "environb")
        for node in ast.walk(tree)
    )


@pytest.mark.parametrize(
    ("relative_path", "sha256"),
    (
        (
            "demo/run_tri_party_airline_live_semantic_lane_v01.py",
            "45d9522de549cfe1bd7e92ed8cf01f1b839b5f1e0bd1b6ca72306ebfd782ff36",
        ),
        (
            "hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py",
            "420c6ba24d1a9417eb67295e402e395b05c88fbf55703d63948507c41a6f031e",
        ),
        (
            "hedgehog/domains/airline/kernel_adapter_v01.py",
            "deebc60e3c0b7840ac58eab7e448ebae328e749239fde6e5503c571bae187dd5",
        ),
    ),
)
def test_frozen_committed_airline_inputs_match(
    relative_path: str,
    sha256: str,
) -> None:
    content = (Path(runner._REPOSITORY_ROOT) / relative_path).read_bytes()
    assert hashlib.sha256(content).hexdigest() == sha256
