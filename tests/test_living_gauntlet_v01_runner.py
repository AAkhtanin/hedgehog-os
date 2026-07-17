from __future__ import annotations

from copy import deepcopy
import ast
import importlib
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from demo import run_living_gauntlet_v01 as runner


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
COMPLETION_MANIFEST_PATH = REPOSITORY_ROOT / "release/completion_manifest.json"
SEAM_INDEX_PATH = REPOSITORY_ROOT / "release/integration_seam_index.json"
RUNNER_PATH = REPOSITORY_ROOT / "demo/run_living_gauntlet_v01.py"


@pytest.fixture(scope="module")
def report() -> dict[str, Any]:
    return runner.collect_living_gauntlet_v01()


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _mutated_manifest_path(
    tmp_path: Path,
    mutate: Callable[[dict[str, Any]], None],
) -> Path:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    mutate(manifest)
    path = tmp_path / "completion_manifest.json"
    path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return path


def test_release_indexes_parse_as_strict_json() -> None:
    completion = runner._load_strict_json_object(COMPLETION_MANIFEST_PATH)
    seams = runner._load_strict_json_object(SEAM_INDEX_PATH)

    assert completion["document_id"] == "living_release_completion_manifest_v01"
    assert seams["document_id"] == "living_release_integration_seam_index_v01"


def test_release_indexes_have_exact_required_top_level_fields() -> None:
    completion = _json(COMPLETION_MANIFEST_PATH)
    seams = _json(SEAM_INDEX_PATH)

    assert set(completion) == runner._MANIFEST_FIELD_NAMES
    assert set(seams) == runner._SEAM_INDEX_FIELD_NAMES
    assert runner._validate_completion_manifest_v01(completion) == ()
    assert runner._validate_integration_seam_index_v01(seams) == ()


def test_release_index_ids_are_unique() -> None:
    completion = _json(COMPLETION_MANIFEST_PATH)
    seams = _json(SEAM_INDEX_PATH)
    act_ids = [
        record["act_id"]
        for field in (
            "active_runtime_acts",
            "evidence_only_references",
            "planned_gate1_acts",
        )
        for record in completion[field]
    ]
    seam_ids = [record["seam_id"] for record in seams["seams"]]

    assert len(act_ids) == len(set(act_ids))
    assert len(seam_ids) == len(set(seam_ids))


def test_current_seam_symbols_are_importable() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    current = [
        seam for seam in seams if seam["status"] != runner.STATUS_PLANNED_NOT_ACTIVE
    ]

    for seam in current:
        module = importlib.import_module(seam["source_module"])
        assert getattr(module, seam["source_symbol"]) is not None


def test_planned_seams_are_not_current_runtime() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    planned = [seam for seam in seams if seam["seam_id"] in runner._PLANNED_SEAM_IDS]

    assert len(planned) == len(runner._PLANNED_SEAM_IDS)
    assert all(seam["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for seam in planned)
    assert all(seam["source_symbol"] is None for seam in planned)
    assert all(
        seam["effect_access"] == "NONE" or seam["seam_id"] == "effect_firewall"
        for seam in planned
    )


def test_active_airline_act_executes_and_passes(report: dict[str, Any]) -> None:
    result = report["active_act_results"][0]

    assert result["act_id"] == "airline_deterministic_transaction_runtime"
    assert result["executed"] is True
    assert result["runtime_status"] == runner.STATUS_PASS
    assert result["state"] == runner.STATUS_PASS
    assert result["root_authority_preserved"] is True
    assert result["real_world_effects_count"] == 0


def test_invariant_super_smoke_executes_and_passes(report: dict[str, Any]) -> None:
    result = report["active_act_results"][1]

    assert result["act_id"] == "all_layers_invariant_super_smoke"
    assert result["executed"] is True
    assert result["runtime_status"] == runner.STATUS_PASS
    assert result["state"] == runner.STATUS_PASS
    assert result["root_authority_preserved"] is True
    assert result["no_real_connector_or_action"] is True


def test_all_three_collectors_are_called_exactly_once(monkeypatch: pytest.MonkeyPatch) -> None:
    original_airline = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01
    original_smoke = runner.collect_all_layers_applied_super_smoke
    original_generic = runner.collect_generic_integrity_replay_gauntlet_act_v01
    calls = {"airline": 0, "smoke": 0, "generic": 0}

    def airline_wrapper() -> dict[str, Any]:
        calls["airline"] += 1
        return original_airline()

    def smoke_wrapper() -> Any:
        calls["smoke"] += 1
        return original_smoke()

    def generic_wrapper() -> runner.LivingGauntletActResultV01:
        calls["generic"] += 1
        return original_generic()

    monkeypatch.setattr(
        runner,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        airline_wrapper,
    )
    monkeypatch.setattr(runner, "collect_all_layers_applied_super_smoke", smoke_wrapper)
    monkeypatch.setattr(
        runner,
        "collect_generic_integrity_replay_gauntlet_act_v01",
        generic_wrapper,
    )

    exact_once_report = runner.collect_living_gauntlet_v01()

    assert exact_once_report["final_status"] == runner.STATUS_PASS
    assert calls == {"airline": 1, "smoke": 1, "generic": 1}
    assert exact_once_report["counters"]["active_collector_execution_count"] == 3


def test_frozen_all_real_evidence_is_not_executed(report: dict[str, Any]) -> None:
    entries = report["evidence_only_entries"]

    assert len(entries) == 1
    assert entries[0]["act_id"] == "airline_all_real_frozen_reference"
    assert entries[0]["state"] == runner.STATUS_EVIDENCE_ONLY
    assert entries[0]["executed"] is False
    assert report["counters"]["evidence_only_executed_count"] == 0


def test_planned_signer_isolation_is_not_pass(report: dict[str, Any]) -> None:
    signer = next(
        entry
        for entry in report["planned_entries"]
        if entry["act_id"] == "root_signer_isolation_conformance"
    )

    assert signer["state"] == runner.STATUS_PLANNED_NOT_ACTIVE
    assert signer["state"] != runner.STATUS_PASS
    assert signer["executed"] is False


def test_planned_supplier_portability_is_not_pass(report: dict[str, Any]) -> None:
    supplier = next(
        entry
        for entry in report["planned_entries"]
        if entry["act_id"] == "supplier_water_filter_portability"
    )

    assert supplier["state"] == runner.STATUS_PLANNED_NOT_ACTIVE
    assert supplier["state"] != runner.STATUS_PASS
    assert supplier["executed"] is False


def test_nonzero_real_world_effects_fail_closed(report: dict[str, Any]) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][0]["real_world_effects_count"] = 1

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_real_world_effects_nonzero:airline_deterministic_transaction_runtime" in errors
    assert "report_failed_checks_not_fail_closed" in errors


def test_lost_root_authority_fails_closed(report: dict[str, Any]) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][1]["root_authority_preserved"] = False

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_root_authority_lost:all_layers_invariant_super_smoke" in errors


def test_active_fail_closed_state_with_success_counters_is_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][0]["state"] = runner.STATUS_FAIL_CLOSED

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert (
        "report_active_act_state_not_pass:airline_deterministic_transaction_runtime"
        in errors
    )
    assert "report_counter_mismatch:active_act_pass_count" in errors
    assert "report_counter_mismatch:active_act_fail_closed_count" in errors


def test_active_runtime_status_not_pass_is_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][0]["runtime_status"] = runner.STATUS_FAIL_CLOSED

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert (
        "report_active_runtime_status_not_pass:airline_deterministic_transaction_runtime"
        in errors
    )


def test_nonempty_nested_active_errors_are_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][1]["errors"] = ["nested_failure"]

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_active_act_errors_present:all_layers_invariant_super_smoke" in errors


def test_active_source_identity_tampering_is_rejected(
    report: dict[str, Any],
) -> None:
    for field, value in (
        ("source_module", "demo.tampered_collector"),
        ("source_symbol", "collect_tampered"),
    ):
        mutated = deepcopy(report)
        mutated["active_act_results"][0][field] = value

        accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

        assert accepted is False
        assert (
            "report_active_source_identity_mismatch:airline_deterministic_transaction_runtime"
            in errors
        )


def test_missing_or_extra_active_result_field_is_rejected(
    report: dict[str, Any],
) -> None:
    missing = deepcopy(report)
    missing["active_act_results"][0].pop("runtime_status")
    extra = deepcopy(report)
    extra["active_act_results"][0]["unexpected"] = True

    for mutated in (missing, extra):
        accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

        assert accepted is False
        assert (
            "report_active_act_field_surface_mismatch:airline_deterministic_transaction_runtime"
            in errors
        )


def test_caller_supplied_counters_inconsistent_with_rows_are_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["counters"]["active_collector_execution_count"] = 1

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_counter_mismatch:active_collector_execution_count" in errors


def test_collector_exception_preserves_unknown_aggregate_effect_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_airline() -> dict[str, Any]:
        raise RuntimeError("deterministic test failure")

    monkeypatch.setattr(
        runner,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        fail_airline,
    )

    failed = runner.collect_living_gauntlet_v01()
    final_section = runner.render_living_gauntlet_v01(failed).split(
        "[FINAL STATUS]", 1
    )[1]

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert failed["active_act_results"][0]["real_world_effects_count"] == -1
    assert failed["counters"]["real_world_effects_count"] == -1
    assert "real_world_effects_count=-1" in final_section
    assert "real_world_effects_count=0" not in final_section


def test_collector_failure_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_airline() -> dict[str, Any]:
        raise RuntimeError("deterministic test failure")

    monkeypatch.setattr(
        runner,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        fail_airline,
    )

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert failed["active_act_results"][0]["state"] == runner.STATUS_FAIL_CLOSED
    assert "airline_collector_failed" in failed["validation_errors"]


def test_missing_manifest_field_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _mutated_manifest_path(
        tmp_path,
        lambda manifest: manifest.pop("non_claims"),
    )
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "completion_manifest_field_surface_mismatch" in failed["validation_errors"]


def test_duplicate_act_id_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def duplicate(manifest: dict[str, Any]) -> None:
        manifest["active_runtime_acts"].append(
            deepcopy(manifest["active_runtime_acts"][0])
        )

    path = _mutated_manifest_path(tmp_path, duplicate)
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "active_act_duplicate_id" in failed["validation_errors"]
    assert "completion_manifest_duplicate_act_id" in failed["validation_errors"]


def test_unknown_status_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unknown(manifest: dict[str, Any]) -> None:
        manifest["planned_gate1_acts"][0]["status"] = "UNKNOWN"

    path = _mutated_manifest_path(tmp_path, unknown)
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "planned_act_status_invalid:root_signer_isolation_conformance" in failed[
        "validation_errors"
    ]


def test_evidence_only_act_cannot_satisfy_active_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reclassify(manifest: dict[str, Any]) -> None:
        claim = next(
            item
            for item in manifest["public_claims"]
            if item["claim_id"] == "claim_airline_all_real_frozen_evidence"
        )
        claim["claim_class"] = "EXECUTED_RUNTIME"

    path = _mutated_manifest_path(tmp_path, reclassify)
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "public_claim_classification_mismatch:claim_airline_all_real_frozen_evidence" in failed[
        "validation_errors"
    ]


def test_planned_act_cannot_satisfy_active_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reclassify(manifest: dict[str, Any]) -> None:
        claim = next(
            item
            for item in manifest["public_claims"]
            if item["claim_id"] == "claim_gate1_planned_not_active"
        )
        claim["claim_class"] = "EXECUTED_RUNTIME"

    path = _mutated_manifest_path(tmp_path, reclassify)
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "public_claim_classification_mismatch:claim_gate1_planned_not_active" in failed[
        "validation_errors"
    ]


def test_renderer_contains_all_required_sections(report: dict[str, Any]) -> None:
    rendered = runner.render_living_gauntlet_v01(report)

    for section in (
        "[ACTIVE EXECUTED ACTS]",
        "[EVIDENCE-ONLY REFERENCES]",
        "[PLANNED GATE-1 ACTS]",
        "[INVARIANTS]",
        "[NON-CLAIMS]",
        "[FINAL STATUS]",
    ):
        assert section in rendered
    assert "final_status=PASS" in rendered


def test_serialization_and_rendering_are_deterministic(report: dict[str, Any]) -> None:
    first_render = runner.render_living_gauntlet_v01(report)
    second_render = runner.render_living_gauntlet_v01(deepcopy(report))
    first_json = json.dumps(report, sort_keys=True, separators=(",", ":"))
    second_json = json.dumps(deepcopy(report), sort_keys=True, separators=(",", ":"))

    assert first_render == second_render
    assert first_json == second_json


def test_runner_imports_no_provider_network_or_live_runner() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert not imported & {"requests", "socket", "urllib", "urllib.request"}
    assert not any("live" in name or "gemini" in name for name in imported)
    assert "os.environ" not in source
    assert "Path.glob" not in source
    assert ".rglob(" not in source
    assert "os.walk" not in source
    assert "importlib" not in source


def test_runner_performs_no_tmp_or_raw_evidence_access() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")

    assert ".tmp" not in source
    assert "config.py" not in source
    assert "_prompt.txt" not in source
    assert "_raw_response.txt" not in source
    assert "audit_reports" not in source
    assert "write_text" not in source
    assert "write_bytes" not in source


def test_main_returns_zero_only_for_pass(
    report: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(runner, "collect_living_gauntlet_v01", lambda: report)
    assert runner.main() == 0
    assert "final_status=PASS" in capsys.readouterr().out

    failed = deepcopy(report)
    failed["final_status"] = runner.STATUS_FAIL_CLOSED
    failed["validation_errors"] = ("forced_test_failure",)
    monkeypatch.setattr(runner, "collect_living_gauntlet_v01", lambda: failed)
    assert runner.main() != 0
    assert "final_status=FAIL_CLOSED" in capsys.readouterr().out


def test_manifest_claims_have_all_explicit_references() -> None:
    claims = _json(COMPLETION_MANIFEST_PATH)["public_claims"]

    for claim in claims:
        for field in (
            "runtime_ref",
            "focused_test_ref",
            "evidence_ref",
            "limitation_ref",
        ):
            assert isinstance(claim[field], str)
            assert claim[field]


def test_manifest_stores_no_synthetic_pass_for_indexed_acts() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    statuses = [
        record["status"]
        for field in (
            "active_runtime_acts",
            "evidence_only_references",
            "planned_gate1_acts",
        )
        for record in manifest[field]
    ]

    assert runner.STATUS_PASS not in statuses
    assert statuses.count(runner.STATUS_ACTIVE) == 3
    assert statuses.count(runner.STATUS_EVIDENCE_ONLY) == 1
    assert statuses.count(runner.STATUS_PLANNED_NOT_ACTIVE) == 10


def test_generic_integrity_replay_act_is_active() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    active = {record["act_id"]: record for record in manifest["active_runtime_acts"]}

    assert active["generic_integrity_replay"]["status"] == runner.STATUS_ACTIVE
    assert active["generic_integrity_replay"]["source_symbol"] == (
        "collect_generic_integrity_replay_gauntlet_act_v01"
    )


def test_generic_integrity_replay_act_executes_and_passes(
    report: dict[str, Any],
) -> None:
    result = report["active_act_results"][2]

    assert result == {
        "act_id": "generic_integrity_replay",
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": "collect_generic_integrity_replay_gauntlet_act_v01",
        "state": runner.STATUS_PASS,
    }


def test_successful_report_has_three_active_acts(report: dict[str, Any]) -> None:
    assert len(report["active_act_results"]) == 3
    assert report["counters"]["active_act_count"] == 3
    assert report["counters"]["active_act_pass_count"] == 3
    assert report["counters"]["active_act_fail_closed_count"] == 0


def test_successful_report_has_ten_planned_acts(report: dict[str, Any]) -> None:
    assert len(report["planned_entries"]) == 10
    assert report["counters"]["planned_act_count"] == 10
    assert "generic_integrity_replay" not in {
        entry["act_id"] for entry in report["planned_entries"]
    }


def test_evidence_only_reference_count_remains_one(report: dict[str, Any]) -> None:
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["evidence_only_executed_count"] == 0


def test_generic_execution_counter_is_one(report: dict[str, Any]) -> None:
    assert report["counters"]["generic_integrity_replay_execution_count"] == 1


def test_generic_act_source_identity_is_canonical() -> None:
    assert runner._ACTIVE_ACT_SOURCES["generic_integrity_replay"] == (
        "demo.run_living_gauntlet_v01",
        "collect_generic_integrity_replay_gauntlet_act_v01",
    )


def test_generic_active_seam_is_importable() -> None:
    seam = next(
        record
        for record in _json(SEAM_INDEX_PATH)["seams"]
        if record["seam_id"] == "generic_integrity_replay_core"
    )
    module = importlib.import_module(seam["source_module"])

    assert seam["status"] == runner.STATUS_ACTIVE
    assert getattr(module, seam["source_symbol"]) is not None


def test_generic_adapter_seam_remains_planned() -> None:
    seam = next(
        record
        for record in _json(SEAM_INDEX_PATH)["seams"]
        if record["seam_id"] == "generic_integrity_replay_adapter"
    )

    assert seam["status"] == runner.STATUS_PLANNED_NOT_ACTIVE
    assert seam["source_symbol"] is None
    assert "G1-D1" in seam["notes"]
    assert "G1-D2" in seam["notes"]
    assert "no adapter exists in G1-A1" in seam["notes"]


def test_seam_index_has_exact_g1a1_geometry() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]

    assert len(seams) == 20
    assert sum(item["status"] == runner.STATUS_ACTIVE for item in seams) == 9
    assert sum(item["status"] == runner.STATUS_REFERENCE_ONLY for item in seams) == 3
    assert sum(
        item["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for item in seams
    ) == 8
    assert all(
        item["effect_access"] == "NONE"
        for item in seams
        if item["status"] == runner.STATUS_ACTIVE
    )


def test_manifest_contains_honest_generic_runtime_claim() -> None:
    claim = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if record["claim_id"] == "claim_generic_integrity_replay_execution"
    )

    assert claim["claim_class"] == "EXECUTED_RUNTIME"
    assert claim["act_ids"] == ["generic_integrity_replay"]
    assert claim["evidence_ref"] == "hedgehog/kernel/integrity_replay_v01.py"
    assert "linear and fan-out domain-neutral in-memory fixtures" in claim["statement"]


def test_planned_claim_excludes_generic_integrity_replay() -> None:
    claim = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if record["claim_id"] == "claim_gate1_planned_not_active"
    )

    assert len(claim["act_ids"]) == 10
    assert "generic_integrity_replay" not in claim["act_ids"]


def test_g1a1_limitation_is_explicit() -> None:
    limitation = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if record["limitation_id"] == "limitation_g1a1_neutral_fixtures_only"
    )["statement"]

    for phrase in (
        "Only neutral in-memory fixtures",
        "Airline and Supplier adapters are not implemented",
        "expected-hash provenance is not external trust",
        "signer isolation is not implemented",
    ):
        assert phrase in limitation


def test_frozen_airline_reference_remains_evidence_only() -> None:
    record = _json(COMPLETION_MANIFEST_PATH)["evidence_only_references"][0]

    assert record["act_id"] == "airline_all_real_frozen_reference"
    assert record["status"] == runner.STATUS_EVIDENCE_ONLY


def test_generic_act_exception_fails_full_report_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_generic() -> runner.LivingGauntletActResultV01:
        raise RuntimeError("test-only failure")

    monkeypatch.setattr(
        runner,
        "collect_generic_integrity_replay_gauntlet_act_v01",
        fail_generic,
    )
    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "generic_integrity_replay_collector_failed" in failed["validation_errors"]


def test_generic_act_failure_preserves_unknown_effect_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_fixtures() -> tuple[dict[str, Any], ...]:
        raise ValueError("test-only failure")

    monkeypatch.setattr(
        runner,
        "_collect_generic_integrity_replay_fixture_records_v01",
        fail_fixtures,
    )
    failed = runner.collect_living_gauntlet_v01()

    assert failed["active_act_results"][2]["real_world_effects_count"] == -1
    assert failed["counters"]["real_world_effects_count"] == -1
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED


def test_counter_tampering_cannot_hide_generic_failure(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][2]["state"] = runner.STATUS_FAIL_CLOSED
    mutated["active_act_results"][2]["runtime_status"] = runner.STATUS_FAIL_CLOSED
    mutated["active_act_results"][2]["errors"] = ["generic_failure"]

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_counter_mismatch:active_act_pass_count" in errors
    assert "report_counter_mismatch:active_act_fail_closed_count" in errors


def test_generic_source_identity_tampering_is_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][2]["source_symbol"] = "tampered"

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_active_source_identity_mismatch:generic_integrity_replay" in errors


def test_generic_active_row_cannot_be_evidence_only(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][2]["state"] = runner.STATUS_EVIDENCE_ONLY

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_active_act_state_unknown:generic_integrity_replay" in errors


def test_generic_active_row_cannot_be_planned(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][2]["state"] = runner.STATUS_PLANNED_NOT_ACTIVE

    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)

    assert accepted is False
    assert "report_active_act_state_unknown:generic_integrity_replay" in errors


def test_renderer_shows_generic_active_act(report: dict[str, Any]) -> None:
    active_section = runner.render_living_gauntlet_v01(report).split(
        "[EVIDENCE-ONLY REFERENCES]", 1
    )[0]

    assert "act_id=generic_integrity_replay" in active_section
    assert "state=PASS" in active_section


def test_runner_version_is_v02(report: dict[str, Any]) -> None:
    assert runner.RUNNER_VERSION == "v0.2"
    assert report["runner_version"] == "v0.2"


def test_runner_introduces_no_domain_adapter_import() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert "hedgehog.domains.airline.kernel_adapter_v01" not in imported
    assert not any("supplier_water_filter" in name for name in imported)


def test_generic_kernel_import_introduces_no_live_path() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")

    assert "hedgehog.kernel.integrity_replay_v01" in source
    assert "live_gemini" not in source
    assert "requests" not in source
    assert "socket" not in source


def test_manifest_status_and_counts_are_exact() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)

    assert manifest["manifest_status"] == "ACTIVE_GATE1_G1A1"
    assert len(manifest["active_runtime_acts"]) == 3
    assert len(manifest["evidence_only_references"]) == 1
    assert len(manifest["planned_gate1_acts"]) == 10


def test_seam_index_status_is_exact() -> None:
    assert _json(SEAM_INDEX_PATH)["index_status"] == "ACTIVE_GATE1_G1A1"
