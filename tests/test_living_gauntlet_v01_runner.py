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


def test_both_collectors_are_called_exactly_once(monkeypatch: pytest.MonkeyPatch) -> None:
    original_airline = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01
    original_smoke = runner.collect_all_layers_applied_super_smoke
    calls = {"airline": 0, "smoke": 0}

    def airline_wrapper() -> dict[str, Any]:
        calls["airline"] += 1
        return original_airline()

    def smoke_wrapper() -> Any:
        calls["smoke"] += 1
        return original_smoke()

    monkeypatch.setattr(
        runner,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        airline_wrapper,
    )
    monkeypatch.setattr(runner, "collect_all_layers_applied_super_smoke", smoke_wrapper)

    exact_once_report = runner.collect_living_gauntlet_v01()

    assert exact_once_report["final_status"] == runner.STATUS_PASS
    assert calls == {"airline": 1, "smoke": 1}
    assert exact_once_report["counters"]["active_collector_execution_count"] == 2


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
    assert "planned_act_status_invalid:generic_integrity_replay" in failed[
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
    assert statuses.count(runner.STATUS_ACTIVE) == 2
    assert statuses.count(runner.STATUS_EVIDENCE_ONLY) == 1
    assert statuses.count(runner.STATUS_PLANNED_NOT_ACTIVE) == 11
