from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import ast
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from demo import run_living_gauntlet_v01 as runner
from demo import run_kernel_conformance_v01 as conformance_runner
from hedgehog.kernel import conformance_v01 as conformance
from hedgehog.kernel import root_signer_isolation_v01 as signer


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
    assert all(seam["effect_access"] == "NONE" for seam in planned)


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


def test_all_active_collectors_are_called_exactly_once(monkeypatch: pytest.MonkeyPatch) -> None:
    original_airline = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01
    original_smoke = runner.collect_all_layers_applied_super_smoke
    original_generic = runner.collect_generic_integrity_replay_gauntlet_act_v01
    original_signer = runner.collect_root_signer_isolation_gauntlet_act_v01
    original_semantic = runner.collect_semantic_work_contract_gauntlet_act_v01
    original_abi = runner.collect_domain_neutral_kernel_abi_gauntlet_act_v01
    original_causal = runner.collect_causal_consumption_gauntlet_act_v01
    original_transition = runner.collect_transition_registry_gauntlet_act_v01
    original_root_decision = runner.collect_root_decision_kernel_gauntlet_act_v01
    original_effect_firewall = runner.collect_effect_firewall_gauntlet_act_v01
    original_multiroot = runner.collect_generic_multiroot_gauntlet_act_v01
    original_supplier = (
        runner.collect_supplier_water_filter_portability_gauntlet_act_v01
    )
    original_conformance = (
        runner.collect_kernel_conformance_closure_gauntlet_act_v01
    )
    original_lifecycle = runner.collect_action_packet_lifecycle_gauntlet_act_v01
    calls = {
        "airline": 0,
        "smoke": 0,
        "generic": 0,
        "signer": 0,
        "semantic": 0,
        "abi": 0,
        "causal": 0,
        "transition": 0,
        "root_decision": 0,
        "effect_firewall": 0,
        "multiroot": 0,
        "supplier": 0,
        "conformance": 0,
        "lifecycle": 0,
    }

    def airline_wrapper() -> dict[str, Any]:
        calls["airline"] += 1
        return original_airline()

    def smoke_wrapper() -> Any:
        calls["smoke"] += 1
        return original_smoke()

    def generic_wrapper() -> runner.LivingGauntletActResultV01:
        calls["generic"] += 1
        return original_generic()

    def signer_wrapper() -> runner.LivingGauntletActResultV01:
        calls["signer"] += 1
        return original_signer()

    def semantic_wrapper() -> runner.LivingGauntletActResultV01:
        calls["semantic"] += 1
        return original_semantic()

    def abi_wrapper() -> runner.LivingGauntletActResultV01:
        calls["abi"] += 1
        return original_abi()

    def causal_wrapper() -> runner.LivingGauntletActResultV01:
        calls["causal"] += 1
        return original_causal()

    def transition_wrapper() -> runner.LivingGauntletActResultV01:
        calls["transition"] += 1
        return original_transition()

    def root_decision_wrapper() -> runner.LivingGauntletActResultV01:
        calls["root_decision"] += 1
        return original_root_decision()

    def effect_firewall_wrapper() -> runner.LivingGauntletActResultV01:
        calls["effect_firewall"] += 1
        return original_effect_firewall()

    def multiroot_wrapper() -> runner.LivingGauntletActResultV01:
        calls["multiroot"] += 1
        return original_multiroot()

    def supplier_wrapper() -> runner.LivingGauntletActResultV01:
        calls["supplier"] += 1
        return original_supplier()

    def conformance_wrapper(active_act_results) -> runner.LivingGauntletActResultV01:
        calls["conformance"] += 1
        return original_conformance(active_act_results)

    def lifecycle_wrapper() -> runner.LivingGauntletActResultV01:
        calls["lifecycle"] += 1
        return original_lifecycle()

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
    monkeypatch.setattr(
        runner,
        "collect_root_signer_isolation_gauntlet_act_v01",
        signer_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_semantic_work_contract_gauntlet_act_v01",
        semantic_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
        abi_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_causal_consumption_gauntlet_act_v01",
        causal_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_transition_registry_gauntlet_act_v01",
        transition_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_root_decision_kernel_gauntlet_act_v01",
        root_decision_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_effect_firewall_gauntlet_act_v01",
        effect_firewall_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_generic_multiroot_gauntlet_act_v01",
        multiroot_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_supplier_water_filter_portability_gauntlet_act_v01",
        supplier_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_kernel_conformance_closure_gauntlet_act_v01",
        conformance_wrapper,
    )
    monkeypatch.setattr(
        runner,
        "collect_action_packet_lifecycle_gauntlet_act_v01",
        lifecycle_wrapper,
    )

    exact_once_report = runner.collect_living_gauntlet_v01()

    assert exact_once_report["final_status"] == runner.STATUS_PASS
    assert calls == {
        "airline": 1,
        "smoke": 1,
        "generic": 1,
        "signer": 1,
        "semantic": 1,
        "abi": 1,
        "causal": 1,
        "transition": 1,
        "root_decision": 1,
        "effect_firewall": 1,
        "multiroot": 1,
        "supplier": 1,
        "conformance": 1,
        "lifecycle": 1,
    }
    assert exact_once_report["counters"]["active_collector_execution_count"] == 16


def test_frozen_all_real_evidence_is_not_executed(report: dict[str, Any]) -> None:
    entries = report["evidence_only_entries"]

    assert len(entries) == 1
    assert entries[0]["act_id"] == "airline_all_real_frozen_reference"
    assert entries[0]["state"] == runner.STATUS_EVIDENCE_ONLY
    assert entries[0]["executed"] is False
    assert report["counters"]["evidence_only_executed_count"] == 0


def test_planned_signer_isolation_is_not_pass(report: dict[str, Any]) -> None:
    assert "root_signer_isolation_conformance" not in {
        entry["act_id"] for entry in report["planned_entries"]
    }
    indexed = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
        if record["act_id"] == "root_signer_isolation_conformance"
    )
    assert indexed["status"] == runner.STATUS_ACTIVE
    assert indexed["status"] != runner.STATUS_PASS


def test_planned_supplier_portability_is_now_active_and_passes(
    report: dict[str, Any],
) -> None:
    assert "supplier_water_filter_portability" not in {
        entry["act_id"] for entry in report["planned_entries"]
    }
    matching = [
        entry
        for entry in report["active_act_results"]
        if entry["act_id"] == "supplier_water_filter_portability"
    ]
    assert len(matching) == 1
    supplier = matching[0]
    assert supplier["state"] == runner.STATUS_PASS
    assert supplier["runtime_status"] == runner.STATUS_PASS
    assert supplier["executed"] is True
    assert supplier["root_authority_preserved"] is True
    assert supplier["no_real_connector_or_action"] is True
    assert supplier["real_world_effects_count"] == 0


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
        record = next(
            item
            for item in manifest["active_runtime_acts"]
            if item["act_id"] == "kernel_conformance_closure"
        )
        record["status"] = "UNKNOWN"

    path = _mutated_manifest_path(tmp_path, unknown)
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "active_act_status_invalid:kernel_conformance_closure" in failed[
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


def test_stale_planned_claim_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reclassify(manifest: dict[str, Any]) -> None:
        manifest["public_claims"].append(
            {
                "act_ids": ["kernel_conformance_closure"],
                "claim_class": "PLANNED_NOT_ACTIVE",
                "claim_id": "claim_gate1_planned_not_active",
                "evidence_ref": "release/integration_seam_index.json",
                "focused_test_ref": "tests/test_living_gauntlet_v01_runner.py",
                "limitation_ref": "limitation_gate1_not_implemented",
                "runtime_ref": "not_executed:planned_gate1",
                "statement": "stale planned claim",
            }
        )

    path = _mutated_manifest_path(tmp_path, reclassify)
    monkeypatch.setattr(runner, "_COMPLETION_MANIFEST_PATH", path)

    failed = runner.collect_living_gauntlet_v01()

    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "completion_manifest_stale_planned_claim" in failed[
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
    assert statuses.count(runner.STATUS_ACTIVE) == 13
    assert statuses.count(runner.STATUS_EVIDENCE_ONLY) == 1
    assert statuses.count(runner.STATUS_PLANNED_NOT_ACTIVE) == 0


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


def test_successful_report_has_thirteen_active_acts(report: dict[str, Any]) -> None:
    assert len(report["active_act_results"]) == 16
    assert report["counters"]["active_act_count"] == 16
    assert report["counters"]["active_act_pass_count"] == 16
    assert report["counters"]["active_act_fail_closed_count"] == 0


def test_successful_report_has_no_planned_act(report: dict[str, Any]) -> None:
    assert report["planned_entries"] == []
    assert report["counters"]["planned_act_count"] == 0


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


def test_generic_adapter_seam_is_active_frozen_airline_projection() -> None:
    seam = next(
        record
        for record in _json(SEAM_INDEX_PATH)["seams"]
        if record["seam_id"] == "generic_integrity_replay_adapter"
    )

    assert seam["status"] == runner.STATUS_ACTIVE
    assert seam["source_module"] == "hedgehog.domains.airline.kernel_adapter_v01"
    assert seam["source_symbol"] == "build_airline_kernel_adapter_result_v01"
    assert seam["effect_access"] == "NONE"
    assert seam["seam_class"] == "DOMAIN_ADAPTER"


def test_g1a1_integrity_replay_seam_remains_active() -> None:
    seam = next(
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    assert seam["status"] == runner.STATUS_ACTIVE
    assert seam["effect_access"] == "NONE"
    assert seam["gate1_target"] == "generic_integrity_replay"


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
    claim_ids = {
        record["claim_id"]
        for record in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
    }
    assert "claim_gate1_planned_not_active" not in claim_ids


def test_g1a1_limitation_is_explicit() -> None:
    limitation = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if record["limitation_id"] == "limitation_g1a1_neutral_fixtures_only"
    )["statement"]

    for phrase in (
        "G1-A1 itself remains limited to neutral in-memory fixtures",
        "frozen Airline projection is separately active through G1-D1",
        "Supplier / Water Filter projection and Generic MultiRoot are separately active through G1-D2",
        "expected-hash provenance is not external trust",
        "G1-A1 does not exercise signer isolation",
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


def test_runner_version_is_v10(report: dict[str, Any]) -> None:
    assert runner._G2A_RUNNER_VERSION_V11 == "v1.1"
    assert runner.RUNNER_VERSION == "v1.3"
    assert report["runner_version"] == "v1.3"


def test_runner_introduces_no_domain_adapter_import() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert "demo.run_full_wow_v1_2_product_trace" in imported
    assert "hedgehog.domains.supplier_water_filter" in imported
    assert not any(
        name == forbidden or name.startswith(forbidden + ".")
        for name in imported
        for forbidden in (
            "requests",
            "socket",
            "os",
            "config",
            "providers",
            "gemini",
        )
    )
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called_names.intersection(
        {"getenv", "load_dotenv", "execute_real_connector", "call_real_connector"}
    )
    assert not called_attributes.intersection(
        {"getenv", "glob", "rglob", "walk", "iterdir", "execute_real_connector"}
    )


def test_generic_kernel_import_introduces_no_live_path() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")

    assert "hedgehog.kernel.integrity_replay_v01" in source
    assert "live_gemini" not in source
    assert "import requests" not in source
    assert "socket" not in source


def test_manifest_status_and_counts_are_exact() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)

    assert manifest["manifest_status"] == "ACTIVE_GATE1_G1E"
    assert manifest["runner_version"] == "v1.0"
    assert len(manifest["active_runtime_acts"]) == 13
    assert len(manifest["evidence_only_references"]) == 1
    assert len(manifest["planned_gate1_acts"]) == 0


def test_seam_index_status_is_exact() -> None:
    assert _json(SEAM_INDEX_PATH)["index_status"] == "ACTIVE_GATE1_G1E"


def test_signer_act_is_active_in_completion_manifest() -> None:
    active = {
        record["act_id"]: record
        for record in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
    }
    record = active["root_signer_isolation_conformance"]
    assert record["status"] == runner.STATUS_ACTIVE
    assert record["source_module"] == "demo.run_living_gauntlet_v01"
    assert record["source_symbol"] == (
        "collect_root_signer_isolation_gauntlet_act_v01"
    )


def test_signer_act_executes_and_passes(report: dict[str, Any]) -> None:
    result = report["active_act_results"][3]
    assert result == {
        "act_id": "root_signer_isolation_conformance",
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": "collect_root_signer_isolation_gauntlet_act_v01",
        "state": runner.STATUS_PASS,
    }


def test_all_thirteen_active_act_ids_are_exact(report: dict[str, Any]) -> None:
    assert tuple(row["act_id"] for row in report["active_act_results"]) == (
        "airline_deterministic_transaction_runtime",
        "all_layers_invariant_super_smoke",
        "generic_integrity_replay",
        "root_signer_isolation_conformance",
        "semantic_work_contract",
        "domain_neutral_kernel_abi",
        "causal_consumption",
        "transition_registry",
        "root_decision_kernel",
        "effect_firewall",
        "generic_multiroot",
        "supplier_water_filter_portability",
        "kernel_conformance_closure",
        "action_packet_lifecycle",
        "drs_semantic_address_and_reuse_certificate",
        "execution_mode_router",
    )
    assert report["counters"]["active_collector_execution_count"] == 16


def test_signer_execution_counter_is_one(report: dict[str, Any]) -> None:
    assert report["counters"]["root_signer_isolation_execution_count"] == 1


def test_signer_source_identity_is_canonical() -> None:
    assert runner._ACTIVE_ACT_SOURCES["root_signer_isolation_conformance"] == (
        "demo.run_living_gauntlet_v01",
        "collect_root_signer_isolation_gauntlet_act_v01",
    )


def test_signer_seam_transitioned_in_place_and_is_unique() -> None:
    matching = [
        record
        for record in _json(SEAM_INDEX_PATH)["seams"]
        if record["seam_id"] == "root_signer_isolation_conformance"
    ]
    assert len(matching) == 1
    seam = matching[0]
    assert seam == {
        "authority_status": "NON_ROOT_SIGNER_ISOLATION",
        "current_mode": "IN_MEMORY_TEST_ONLY_ED25519",
        "effect_access": "NONE",
        "gate1_target": "root_signer_isolation_conformance",
        "notes": (
            "Ephemeral in-memory Root-key isolation conformance only; not "
            "Airline Root Attestation, production identity, PKI, permission, "
            "authority creation, or effect access."
        ),
        "seam_class": "KERNEL_CONFORMANCE_CORE",
        "seam_id": "root_signer_isolation_conformance",
        "source_module": "hedgehog.kernel.root_signer_isolation_v01",
        "source_symbol": "verify_root_signature_v01",
        "status": runner.STATUS_ACTIVE,
    }


def test_signer_claim_has_all_four_references() -> None:
    claim = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if record["claim_id"]
        == "claim_root_signer_isolation_conformance_execution"
    )
    assert claim["claim_class"] == "EXECUTED_CONFORMANCE"
    assert claim["act_ids"] == ["root_signer_isolation_conformance"]
    assert claim["runtime_ref"].endswith(
        ":collect_root_signer_isolation_gauntlet_act_v01"
    )
    assert claim["focused_test_ref"] == "tests/test_root_signer_isolation_v01.py"
    assert claim["evidence_ref"] == "hedgehog/kernel/root_signer_isolation_v01.py"
    assert claim["limitation_ref"] == (
        "limitation_g1a2_conformance_only_signer_isolation"
    )


def test_planned_claim_is_absent_after_runtime_closure() -> None:
    claim_ids = {
        record["claim_id"]
        for record in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
    }
    assert "claim_gate1_planned_not_active" not in claim_ids


def test_g1a2_limitation_is_conformance_only_and_preserves_airline_boundary() -> None:
    statement = next(
        record["statement"]
        for record in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if record["limitation_id"]
        == "limitation_g1a2_conformance_only_signer_isolation"
    )
    for phrase in (
        "ephemeral and in-memory",
        "no key persistence",
        "production identity",
        "PKI",
        "certificate authority",
        "Airline Root Attestation",
        "UNSIGNED_PLACEHOLDER",
        "signature_verified false",
        "permission",
        "effect",
    ):
        assert phrase in statement


def test_non_claims_do_not_claim_airline_attestation_or_production_identity() -> None:
    non_claims = _json(COMPLETION_MANIFEST_PATH)["non_claims"]
    for required in (
        "not production Root signing",
        "not Airline Root Attestation",
        "not PKI",
        "not production signer identity",
        "not certificate issuance",
    ):
        assert required in non_claims
    assert "not Gate 1 closure" not in non_claims


def test_signer_fixture_metrics_are_exact() -> None:
    assert runner._collect_root_signer_isolation_fixture_metrics_v01() == {
        "capability_count": 3,
        "own_signature_pass_count": 3,
        "cross_root_signing_blocked_count": 6,
        "cross_root_verification_blocked_count": 6,
        "private_key_serialization_count": 0,
        "file_write_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }


def test_signer_exception_fails_full_report_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_signer() -> runner.LivingGauntletActResultV01:
        raise RuntimeError("test-only failure")

    monkeypatch.setattr(
        runner,
        "collect_root_signer_isolation_gauntlet_act_v01",
        fail_signer,
    )
    failed = runner.collect_living_gauntlet_v01()
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "root_signer_isolation_collector_failed" in failed["validation_errors"]


def test_signer_failure_preserves_unknown_aggregate_effects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_fixture() -> dict[str, int]:
        raise OSError("test-only failure")

    monkeypatch.setattr(
        runner,
        "_collect_root_signer_isolation_fixture_metrics_v01",
        fail_fixture,
    )
    failed = runner.collect_living_gauntlet_v01()
    assert failed["active_act_results"][3]["real_world_effects_count"] == -1
    assert failed["counters"]["real_world_effects_count"] == -1
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED


def test_counter_tampering_cannot_hide_signer_failure(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][3]["state"] = runner.STATUS_FAIL_CLOSED
    mutated["active_act_results"][3]["runtime_status"] = runner.STATUS_FAIL_CLOSED
    mutated["active_act_results"][3]["errors"] = ["signer_failure"]
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert "report_counter_mismatch:active_act_pass_count" in errors
    assert "report_counter_mismatch:active_act_fail_closed_count" in errors


def test_signer_source_identity_tampering_is_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][3]["source_symbol"] = "tampered"
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert (
        "report_active_source_identity_mismatch:root_signer_isolation_conformance"
        in errors
    )


@pytest.mark.parametrize(
    "invalid_state", (runner.STATUS_EVIDENCE_ONLY, runner.STATUS_PLANNED_NOT_ACTIVE)
)
def test_signer_active_row_cannot_be_non_active_state(
    report: dict[str, Any], invalid_state: str
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][3]["state"] = invalid_state
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert (
        "report_active_act_state_unknown:root_signer_isolation_conformance"
        in errors
    )


def test_renderer_shows_signer_as_active(report: dict[str, Any]) -> None:
    active_section = runner.render_living_gauntlet_v01(report).split(
        "[EVIDENCE-ONLY REFERENCES]", 1
    )[0]
    assert "act_id=root_signer_isolation_conformance" in active_section
    assert "state=PASS" in active_section


@pytest.mark.parametrize(
    "forbidden",
    (
        "private",
        "private_key",
        "signature_hex",
        "public_key_hex",
        "key_id",
        "commitment_hash",
        "BEGIN PRIVATE KEY",
        "BEGIN PUBLIC KEY",
    ),
)
def test_report_and_render_expose_no_cryptographic_material(
    report: dict[str, Any], forbidden: str
) -> None:
    serialized = json.dumps(report, sort_keys=True, default=list)
    rendered = runner.render_living_gauntlet_v01(report)
    assert forbidden.lower() not in serialized.lower()
    assert forbidden.lower() not in rendered.lower()


def test_two_complete_collections_are_identical_despite_ephemeral_keys() -> None:
    first = runner.collect_living_gauntlet_v01()
    second = runner.collect_living_gauntlet_v01()
    assert first == second
    assert runner.render_living_gauntlet_v01(first) == runner.render_living_gauntlet_v01(second)
    assert json.dumps(first, sort_keys=True, separators=(",", ":"), default=list) == json.dumps(
        second, sort_keys=True, separators=(",", ":"), default=list
    )


def test_signer_fixture_and_kernel_have_no_file_write_path() -> None:
    runner_source = RUNNER_PATH.read_text(encoding="utf-8")
    signer_source = (
        REPOSITORY_ROOT / "hedgehog/kernel/root_signer_isolation_v01.py"
    ).read_text(encoding="utf-8")
    fixture_source = runner_source.split(
        "def _collect_root_signer_isolation_fixture_metrics_v01", 1
    )[1].split("def _failed_act_result", 1)[0]
    for token in ("open(", ".write_text(", ".write_bytes(", "private_bytes"):
        assert token not in fixture_source
        assert token not in signer_source


def test_signer_kernel_introduces_no_domain_import() -> None:
    path = REPOSITORY_ROOT / "hedgehog/kernel/root_signer_isolation_v01.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(name.startswith("hedgehog.domains") for name in imports)
    assert not any(name.startswith(("demo", "tests")) for name in imports)


@pytest.mark.parametrize(
    ("claim_id", "wrong_class"),
    (
        (
            "claim_root_signer_isolation_conformance_execution",
            "EXECUTED_RUNTIME",
        ),
        (
            "claim_generic_integrity_replay_execution",
            "EXECUTED_CONFORMANCE",
        ),
        ("claim_airline_runtime_execution", "EXECUTED_CONFORMANCE"),
    ),
)
def test_executed_claim_classes_are_not_interchangeable(
    claim_id: str,
    wrong_class: str,
) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(
        item for item in manifest["public_claims"] if item["claim_id"] == claim_id
    )
    claim["claim_class"] = wrong_class
    errors = runner._validate_completion_manifest_v01(manifest)
    assert f"public_claim_classification_mismatch:{claim_id}" in errors


def test_public_claim_empty_act_ids_fail_closed() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(
        item
        for item in manifest["public_claims"]
        if item["claim_id"] == "claim_root_signer_isolation_conformance_execution"
    )
    claim["act_ids"] = []
    errors = runner._validate_completion_manifest_v01(manifest)
    assert (
        "public_claim_act_ids_invalid:"
        "claim_root_signer_isolation_conformance_execution"
    ) in errors


@pytest.mark.parametrize(
    ("seam_id", "wrong_status"),
    (
        ("root_signer_isolation_conformance", runner.STATUS_REFERENCE_ONLY),
        ("generic_integrity_replay_core", runner.STATUS_REFERENCE_ONLY),
        (
            "airline_transaction_artifact_ledger_reference",
            runner.STATUS_ACTIVE,
        ),
        ("core_context_packets", runner.STATUS_PLANNED_NOT_ACTIVE),
    ),
)
def test_current_seam_status_mutations_fail_closed(
    seam_id: str,
    wrong_status: str,
) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == seam_id)
    seam["status"] = wrong_status
    errors = runner._validate_integration_seam_index_v01(index)
    assert f"current_seam_status_mismatch:{seam_id}" in errors


def test_cross_root_unrelated_value_error_is_not_isolation_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = runner.sign_root_owned_commitment_v01

    def unrelated_reason(**kwargs: object) -> signer.RootSignatureV01:
        capability = kwargs["capability"]
        commitment = kwargs["commitment"]
        if capability.root_id != commitment.owner_root_id:  # type: ignore[union-attr]
            raise ValueError("signature_generation_failed")
        return original(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(
        runner,
        "sign_root_owned_commitment_v01",
        unrelated_reason,
    )
    result = runner.collect_root_signer_isolation_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.real_world_effects_count == -1


def test_generic_blocked_verification_is_not_isolation_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = runner.verify_root_signature_v01

    def incomplete_block(**kwargs: object) -> signer.RootSignatureVerificationResultV01:
        result = original(**kwargs)
        commitment = kwargs["commitment"]
        signature = kwargs["signature"]
        if signature.owner_root_id != commitment.owner_root_id:  # type: ignore[union-attr]
            return replace(
                result,
                verification_errors=("root_isolation_failed",),
                signature_verified=False,
                root_isolation_verified=False,
            )
        return result

    monkeypatch.setattr(runner, "verify_root_signature_v01", incomplete_block)
    result = runner.collect_root_signer_isolation_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.real_world_effects_count == -1


def test_exact_current_seam_status_map_matches_unchanged_index() -> None:
    seams = {
        item["seam_id"]: item["status"]
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] in runner._CURRENT_SEAMS
    }
    assert seams == runner._CURRENT_SEAM_STATUSES


def test_unchanged_release_json_still_validates_for_g1a2() -> None:
    assert runner._validate_completion_manifest_v01(
        _json(COMPLETION_MANIFEST_PATH)
    ) == ()
    assert runner._validate_integration_seam_index_v01(
        _json(SEAM_INDEX_PATH)
    ) == ()


def test_semantic_work_act_is_active_in_completion_manifest() -> None:
    record = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
        if item["act_id"] == "semantic_work_contract"
    )
    assert record == {
        "act_id": "semantic_work_contract",
        "claim_ids": [
            "claim_kernel_trust_model_conformance_execution",
            "claim_semantic_work_contract_conformance_execution",
        ],
        "focused_test": "tests/test_semantic_work_v01.py",
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": "collect_semantic_work_contract_gauntlet_act_v01",
        "status": runner.STATUS_ACTIVE,
    }


def test_semantic_work_act_executes_and_passes(report: dict[str, Any]) -> None:
    assert report["active_act_results"][4] == {
        "act_id": "semantic_work_contract",
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": "collect_semantic_work_contract_gauntlet_act_v01",
        "state": runner.STATUS_PASS,
    }
    assert report["counters"]["semantic_work_contract_execution_count"] == 1


def test_semantic_work_fixture_geometry_is_exact() -> None:
    metrics = runner._collect_semantic_work_fixture_metrics_v01()
    assert {
        key: metrics[key]
        for key in (
            "trust_profile_count",
            "contribution_count",
            "contribution_mode_count",
            "raw_claim_count",
            "normalized_claim_count",
            "duplicate_removal_count",
            "conflict_set_count",
            "missing_evidence_count",
            "root_decision_created_count",
            "permission_created_count",
            "final_output_created_count",
            "provider_call_count",
            "network_call_count",
            "gemini_call_count",
            "real_world_effects_count",
        )
    } == {
        "trust_profile_count": 18,
        "contribution_count": 5,
        "contribution_mode_count": 5,
        "raw_claim_count": 6,
        "normalized_claim_count": 5,
        "duplicate_removal_count": 1,
        "conflict_set_count": 1,
        "missing_evidence_count": 1,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    assert len(metrics["proposal_id"]) == 64
    assert len(metrics["packet_id"]) == 64


def test_semantic_work_claim_is_exact_conformance_class() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(
        item
        for item in manifest["public_claims"]
        if item["claim_id"] == "claim_semantic_work_contract_conformance_execution"
    )
    assert claim["claim_class"] == "EXECUTED_CONFORMANCE"
    assert claim["act_ids"] == ["semantic_work_contract"]
    claim["claim_class"] = "EXECUTED_RUNTIME"
    assert (
        "public_claim_classification_mismatch:"
        "claim_semantic_work_contract_conformance_execution"
    ) in runner._validate_completion_manifest_v01(manifest)


@pytest.mark.parametrize(
    ("claim_id", "focused_test", "evidence_ref"),
    (
        (
            "claim_kernel_trust_model_conformance_execution",
            "tests/test_kernel_trust_model_v01.py",
            "hedgehog/kernel/trust_model_v01.py",
        ),
        (
            "claim_semantic_work_contract_conformance_execution",
            "tests/test_semantic_work_v01.py",
            "hedgehog/kernel/semantic_work_v01.py",
        ),
    ),
)
def test_g1b1_claims_share_the_active_semantic_act(
    claim_id: str,
    focused_test: str,
    evidence_ref: str,
) -> None:
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == claim_id
    )
    assert claim["claim_class"] == "EXECUTED_CONFORMANCE"
    assert claim["act_ids"] == ["semantic_work_contract"]
    assert claim["focused_test_ref"] == focused_test
    assert claim["evidence_ref"] == evidence_ref
    assert claim["runtime_ref"].endswith(
        ":collect_semantic_work_contract_gauntlet_act_v01"
    )


def test_planned_claim_excludes_semantic_work_and_matches_current_plan() -> None:
    claims = _json(COMPLETION_MANIFEST_PATH)["public_claims"]
    assert all(item["claim_id"] != "claim_gate1_planned_not_active" for item in claims)


@pytest.mark.parametrize(
    "required_phrase",
    (
        "in-memory SemanticWork and Trust conformance slice",
        "no real cloud LLM",
        "local SLM",
        "fractal runtime",
        "no permission",
        "Root decision",
        "FinalOutput",
        "Trust Model metadata is descriptive",
        "Kernel ABI",
        "CausalConsumptionRef",
        "Effect Firewall",
    ),
)
def test_g1b1_limitation_is_explicit(required_phrase: str) -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"]
        == "limitation_g1b1_in_memory_contract_conformance_only"
    )
    assert required_phrase in statement


@pytest.mark.parametrize(
    ("seam_id", "module", "symbol"),
    (
        (
            "kernel_trust_model_core",
            "hedgehog.kernel.trust_model_v01",
            "validate_component_trust_profiles_v01",
        ),
        (
            "semantic_work_contract_core",
            "hedgehog.kernel.semantic_work_v01",
            "build_root_review_packet_from_contributions_v01",
        ),
    ),
)
def test_g1b1_seams_are_active_and_importable(
    seam_id: str,
    module: str,
    symbol: str,
) -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    matching = [item for item in seams if item["seam_id"] == seam_id]
    assert len(matching) == 1
    assert matching[0]["status"] == runner.STATUS_ACTIVE
    assert matching[0]["effect_access"] == "NONE"
    assert matching[0]["source_module"] == module
    assert matching[0]["source_symbol"] == symbol
    assert getattr(importlib.import_module(module), symbol) is not None


@pytest.mark.parametrize(
    "seam_id",
    (
        "core_context_packets",
        "core_structured_rationale",
        "core_semantic_reasoning_adapter",
    ),
)
def test_semantic_donor_seams_remain_active(seam_id: str) -> None:
    seam = next(
        item for item in _json(SEAM_INDEX_PATH)["seams"] if item["seam_id"] == seam_id
    )
    assert seam["status"] == runner.STATUS_ACTIVE


@pytest.mark.parametrize(
    ("seam_id", "wrong_status"),
    (
        ("kernel_trust_model_core", runner.STATUS_REFERENCE_ONLY),
        ("semantic_work_contract_core", runner.STATUS_REFERENCE_ONLY),
        ("kernel_trust_model_core", runner.STATUS_PLANNED_NOT_ACTIVE),
        ("semantic_work_contract_core", runner.STATUS_PLANNED_NOT_ACTIVE),
    ),
)
def test_g1b1_current_seam_status_mutation_fails_closed(
    seam_id: str,
    wrong_status: str,
) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == seam_id)
    seam["status"] = wrong_status
    assert f"current_seam_status_mismatch:{seam_id}" in (
        runner._validate_integration_seam_index_v01(index)
    )


@pytest.mark.parametrize(
    "seam_id", ("kernel_trust_model_core", "semantic_work_contract_core")
)
def test_g1b1_active_seam_cannot_gain_effect_access(seam_id: str) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == seam_id)
    seam["effect_access"] = "BOUNDED"
    assert f"seam_effect_access_forbidden:{seam_id}" in (
        runner._validate_integration_seam_index_v01(index)
    )


def test_semantic_act_exception_fails_full_report_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        runner,
        "collect_semantic_work_contract_gauntlet_act_v01",
        lambda: (_ for _ in ()).throw(RuntimeError("test-only")),
    )
    failed = runner.collect_living_gauntlet_v01()
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "semantic_work_contract_collector_failed" in failed["validation_errors"]
    assert failed["active_act_results"][4]["real_world_effects_count"] == -1
    assert failed["counters"]["real_world_effects_count"] == -1


def test_semantic_fixture_failure_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        runner,
        "_collect_semantic_work_fixture_metrics_v01",
        lambda: (_ for _ in ()).throw(OSError("sensitive test payload")),
    )
    result = runner.collect_semantic_work_contract_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.errors == ("semantic_work_contract_conformance_failed",)
    assert result.real_world_effects_count == -1


def test_semantic_source_identity_tampering_is_rejected(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][4]["source_symbol"] = "tampered"
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert "report_active_source_identity_mismatch:semantic_work_contract" in errors


def test_counter_tampering_cannot_hide_semantic_failure(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][4].update(
        {
            "state": runner.STATUS_FAIL_CLOSED,
            "runtime_status": runner.STATUS_FAIL_CLOSED,
            "errors": ["semantic_failure"],
        }
    )
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert "report_counter_mismatch:active_act_pass_count" in errors
    assert "report_counter_mismatch:active_act_fail_closed_count" in errors


@pytest.mark.parametrize(
    "invalid_state", (runner.STATUS_EVIDENCE_ONLY, runner.STATUS_PLANNED_NOT_ACTIVE)
)
def test_semantic_active_row_cannot_be_non_active(
    report: dict[str, Any], invalid_state: str
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][4]["state"] = invalid_state
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert "report_active_act_state_unknown:semantic_work_contract" in errors


def test_renderer_shows_semantic_work_as_active(report: dict[str, Any]) -> None:
    active = runner.render_living_gauntlet_v01(report).split(
        "[EVIDENCE-ONLY REFERENCES]", 1
    )[0]
    assert "act_id=semantic_work_contract" in active
    assert "state=PASS" in active


@pytest.mark.parametrize(
    "forbidden",
    (
        "claim:fixture",
        "evidence:fixture",
        "provenance:fixture",
        '"ready"',
        '"blocked"',
        '"stable"',
        "provider response",
    ),
)
def test_report_exposes_no_semantic_fixture_payload(
    report: dict[str, Any], forbidden: str
) -> None:
    serialized = json.dumps(report, sort_keys=True, default=list).lower()
    rendered = runner.render_living_gauntlet_v01(report).lower()
    assert forbidden.lower() not in serialized
    assert forbidden.lower() not in rendered


def test_g1b1_report_geometry_and_prior_acts_remain_exact(
    report: dict[str, Any],
) -> None:
    assert report["final_status"] == runner.STATUS_PASS
    assert report["counters"]["real_world_effects_count"] == 0
    assert report["active_act_results"][2]["act_id"] == "generic_integrity_replay"
    assert report["active_act_results"][3]["act_id"] == (
        "root_signer_isolation_conformance"
    )
    assert report["evidence_only_entries"][0]["act_id"] == (
        "airline_all_real_frozen_reference"
    )


@pytest.mark.parametrize(
    ("act_id", "claim_id", "source_symbol"),
    (
        (
            "domain_neutral_kernel_abi",
            "claim_domain_neutral_kernel_abi_conformance_execution",
            "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
        ),
        (
            "causal_consumption",
            "claim_causal_consumption_conformance_execution",
            "collect_causal_consumption_gauntlet_act_v01",
        ),
    ),
)
def test_g1b2_active_records_are_exact(
    act_id: str, claim_id: str, source_symbol: str
) -> None:
    record = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
        if item["act_id"] == act_id
    )
    assert record == {
        "act_id": act_id,
        "claim_ids": [claim_id],
        "focused_test": "tests/test_kernel_abi_v01.py",
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": source_symbol,
        "status": runner.STATUS_ACTIVE,
    }


@pytest.mark.parametrize(
    ("index", "act_id", "source_symbol", "counter"),
    (
        (
            5,
            "domain_neutral_kernel_abi",
            "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
            "domain_neutral_kernel_abi_execution_count",
        ),
        (
            6,
            "causal_consumption",
            "collect_causal_consumption_gauntlet_act_v01",
            "causal_consumption_execution_count",
        ),
    ),
)
def test_g1b2_acts_execute_and_pass(
    report: dict[str, Any],
    index: int,
    act_id: str,
    source_symbol: str,
    counter: str,
) -> None:
    assert report["active_act_results"][index] == {
        "act_id": act_id,
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": source_symbol,
        "state": runner.STATUS_PASS,
    }
    assert report["counters"][counter] == 1


@pytest.mark.parametrize(
    ("act_id", "source_symbol"),
    (
        (
            "domain_neutral_kernel_abi",
            "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
        ),
        ("causal_consumption", "collect_causal_consumption_gauntlet_act_v01"),
    ),
)
def test_g1b2_source_identities_are_exact(act_id: str, source_symbol: str) -> None:
    assert runner._ACTIVE_ACT_SOURCES[act_id] == (
        "demo.run_living_gauntlet_v01",
        source_symbol,
    )


@pytest.mark.parametrize(
    ("claim_id", "act_id", "symbol"),
    (
        (
            "claim_domain_neutral_kernel_abi_conformance_execution",
            "domain_neutral_kernel_abi",
            "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
        ),
        (
            "claim_causal_consumption_conformance_execution",
            "causal_consumption",
            "collect_causal_consumption_gauntlet_act_v01",
        ),
    ),
)
def test_g1b2_claims_have_exact_class_and_references(
    claim_id: str, act_id: str, symbol: str
) -> None:
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == claim_id
    )
    assert claim["claim_class"] == "EXECUTED_CONFORMANCE"
    assert claim["act_ids"] == [act_id]
    assert claim["runtime_ref"] == f"demo.run_living_gauntlet_v01:{symbol}"
    assert claim["focused_test_ref"] == "tests/test_kernel_abi_v01.py"
    assert claim["evidence_ref"] == "hedgehog/kernel/abi_v01.py"
    assert claim["limitation_ref"] == (
        "limitation_g1b2_in_memory_abi_and_counterfactual_only"
    )


@pytest.mark.parametrize(
    "claim_id",
    (
        "claim_domain_neutral_kernel_abi_conformance_execution",
        "claim_causal_consumption_conformance_execution",
    ),
)
def test_g1b2_claim_reclassified_as_runtime_fails_closed(claim_id: str) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(
        item for item in manifest["public_claims"] if item["claim_id"] == claim_id
    )
    claim["claim_class"] = "EXECUTED_RUNTIME"
    assert f"public_claim_classification_mismatch:{claim_id}" in (
        runner._validate_completion_manifest_v01(manifest)
    )


def test_g1b2_acts_remain_absent_from_current_planned_set() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    planned = tuple(item["act_id"] for item in manifest["planned_gate1_acts"])
    assert planned == ()
    assert all(
        item["claim_id"] != "claim_gate1_planned_not_active"
        for item in manifest["public_claims"]
    )
    assert "domain_neutral_kernel_abi" not in planned
    assert "causal_consumption" not in planned


@pytest.mark.parametrize(
    "phrase",
    (
        "neutral in-memory conformance fixtures",
        "the frozen Airline adapter in G1-D1",
        "Supplier / Water Filter projection with Generic MultiRoot in G1-D2",
        "no production ABI compatibility guarantee",
        "only ABI v1.0",
        "declared controlled influence, not semantic truth",
        "Transition Registry",
        "Root Decision Kernel",
        "Effect Firewall",
        "Generic MultiRoot",
        "no permission",
        "Root decision",
        "FinalOutput",
        "connector call",
        "effect is created",
    ),
)
def test_g1b2_limitation_is_explicit(phrase: str) -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"]
        == "limitation_g1b2_in_memory_abi_and_counterfactual_only"
    )
    assert phrase in statement


@pytest.mark.parametrize(
    ("seam_id", "symbol", "seam_class", "mode"),
    (
        (
            "kernel_abi_core",
            "validate_kernel_artifact_bundle_v01",
            "KERNEL_CORE",
            "PURE_IN_MEMORY_VERSIONED_ABI",
        ),
        (
            "causal_consumption_core",
            "validate_causal_counterfactual_v01",
            "KERNEL_CONFORMANCE_CORE",
            "PURE_IN_MEMORY_FIELD_LEVEL_CAUSAL_PROOF",
        ),
    ),
)
def test_g1b2_seams_are_unique_active_and_importable(
    seam_id: str, symbol: str, seam_class: str, mode: str
) -> None:
    matching = [
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == seam_id
    ]
    assert len(matching) == 1
    seam = matching[0]
    assert seam["source_module"] == "hedgehog.kernel.abi_v01"
    assert seam["source_symbol"] == symbol
    assert seam["seam_class"] == seam_class
    assert seam["current_mode"] == mode
    assert seam["status"] == runner.STATUS_ACTIVE
    assert seam["effect_access"] == "NONE"
    assert getattr(importlib.import_module(seam["source_module"]), symbol)


@pytest.mark.parametrize(
    ("seam_id", "wrong_status"),
    (
        ("kernel_abi_core", runner.STATUS_REFERENCE_ONLY),
        ("kernel_abi_core", runner.STATUS_PLANNED_NOT_ACTIVE),
        ("causal_consumption_core", runner.STATUS_REFERENCE_ONLY),
        ("causal_consumption_core", runner.STATUS_PLANNED_NOT_ACTIVE),
    ),
)
def test_g1b2_seam_status_mutations_fail_closed(
    seam_id: str, wrong_status: str
) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == seam_id)
    seam["status"] = wrong_status
    assert f"current_seam_status_mismatch:{seam_id}" in (
        runner._validate_integration_seam_index_v01(index)
    )


@pytest.mark.parametrize("seam_id", ("kernel_abi_core", "causal_consumption_core"))
def test_g1b2_active_seams_cannot_gain_effect_access(seam_id: str) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == seam_id)
    seam["effect_access"] = "BOUNDED"
    assert f"seam_effect_access_forbidden:{seam_id}" in (
        runner._validate_integration_seam_index_v01(index)
    )


def test_g1b2_seams_remain_active_without_effect_access() -> None:
    seams = {
        item["seam_id"]: item for item in _json(SEAM_INDEX_PATH)["seams"]
    }
    for seam_id in ("kernel_abi_core", "causal_consumption_core"):
        assert seams[seam_id]["status"] == runner.STATUS_ACTIVE
        assert seams[seam_id]["effect_access"] == "NONE"


def test_kernel_abi_fixture_metrics_are_exact() -> None:
    assert runner._collect_kernel_abi_fixture_metrics_v01() == {
        "artifact_count": 6,
        "valid_artifact_count": 6,
        "canonical_ref_count": 6,
        "schema_valid_projection_count": 6,
        "unknown_major_blocked": True,
        "authority_mutation_blocked": True,
        "lifecycle_mutation_blocked": True,
        "payload_authority_override_blocked": True,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }


def test_causal_fixture_metrics_are_exact() -> None:
    metrics = runner._collect_causal_consumption_fixture_metrics_v01()
    assert metrics["causal_source_artifact_count"] == 4
    assert metrics["causal_downstream_artifact_count"] == 4
    assert metrics["causal_ref_count"] == 4
    assert metrics["disposition_count"] == 4
    for key in (
        "used_ref_count",
        "rejected_ref_count",
        "ignored_ref_count",
        "blocked_ref_count",
        "used_counterfactual_proof_count",
        "rejected_authority_preservation_count",
        "ignored_downstream_preservation_count",
        "ignored_authority_preservation_count",
        "blocked_authority_preservation_count",
    ):
        assert metrics[key] == 1
    for key in (
        "root_decision_created_count",
        "permission_created_count",
        "final_output_created_count",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "real_world_effects_count",
    ):
        assert metrics[key] == 0


@pytest.mark.parametrize(
    ("collector_name", "index", "reason"),
    (
        (
            "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
            5,
            "domain_neutral_kernel_abi_collector_failed",
        ),
        (
            "collect_causal_consumption_gauntlet_act_v01",
            6,
            "causal_consumption_collector_failed",
        ),
    ),
)
def test_g1b2_collector_exception_fails_complete_report_closed(
    monkeypatch: pytest.MonkeyPatch,
    collector_name: str,
    index: int,
    reason: str,
) -> None:
    monkeypatch.setattr(
        runner,
        collector_name,
        lambda: (_ for _ in ()).throw(RuntimeError("caller text")),
    )
    failed = runner.collect_living_gauntlet_v01()
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert reason in failed["validation_errors"]
    assert failed["active_act_results"][index]["real_world_effects_count"] == -1
    assert failed["counters"]["real_world_effects_count"] == -1
    assert "caller text" not in json.dumps(failed, default=list)


@pytest.mark.parametrize(
    ("metrics_name", "collector_name", "reason"),
    (
        (
            "_collect_kernel_abi_fixture_metrics_v01",
            "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
            "domain_neutral_kernel_abi_conformance_failed",
        ),
        (
            "_collect_causal_consumption_fixture_metrics_v01",
            "collect_causal_consumption_gauntlet_act_v01",
            "causal_consumption_conformance_failed",
        ),
    ),
)
def test_g1b2_fixture_exception_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    metrics_name: str,
    collector_name: str,
    reason: str,
) -> None:
    monkeypatch.setattr(
        runner,
        metrics_name,
        lambda: (_ for _ in ()).throw(OSError("caller secret")),
    )
    result = getattr(runner, collector_name)()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.errors == (reason,)
    assert result.real_world_effects_count == -1


@pytest.mark.parametrize(
    ("index", "act_id"),
    ((5, "domain_neutral_kernel_abi"), (6, "causal_consumption")),
)
def test_g1b2_source_identity_tampering_fails(
    report: dict[str, Any], index: int, act_id: str
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][index]["source_symbol"] = "tampered"
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert f"report_active_source_identity_mismatch:{act_id}" in errors


@pytest.mark.parametrize(
    ("index", "act_id"),
    ((5, "domain_neutral_kernel_abi"), (6, "causal_consumption")),
)
def test_counter_tampering_cannot_hide_g1b2_failure(
    report: dict[str, Any], index: int, act_id: str
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][index].update(
        {
            "state": runner.STATUS_FAIL_CLOSED,
            "runtime_status": runner.STATUS_FAIL_CLOSED,
            "errors": [f"{act_id}_failure"],
        }
    )
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert "report_counter_mismatch:active_act_pass_count" in errors
    assert "report_counter_mismatch:active_act_fail_closed_count" in errors


@pytest.mark.parametrize(
    ("index", "act_id", "invalid_state"),
    (
        (5, "domain_neutral_kernel_abi", runner.STATUS_EVIDENCE_ONLY),
        (5, "domain_neutral_kernel_abi", runner.STATUS_PLANNED_NOT_ACTIVE),
        (6, "causal_consumption", runner.STATUS_EVIDENCE_ONLY),
        (6, "causal_consumption", runner.STATUS_PLANNED_NOT_ACTIVE),
    ),
)
def test_g1b2_active_acts_cannot_be_non_active(
    report: dict[str, Any], index: int, act_id: str, invalid_state: str
) -> None:
    mutated = deepcopy(report)
    mutated["active_act_results"][index]["state"] = invalid_state
    accepted, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert accepted is False
    assert f"report_active_act_state_unknown:{act_id}" in errors


@pytest.mark.parametrize("act_id", ("domain_neutral_kernel_abi", "causal_consumption"))
def test_renderer_shows_both_g1b2_acts_as_active(
    report: dict[str, Any], act_id: str
) -> None:
    active = runner.render_living_gauntlet_v01(report).split(
        "[EVIDENCE-ONLY REFERENCES]", 1
    )[0]
    assert f"act_id={act_id}" in active
    assert "state=PASS" in active


@pytest.mark.parametrize(
    "forbidden",
    (
        "candidate:alpha",
        "candidate:beta",
        "create_permission",
        "create_extended_permission",
        "presentation_style",
        "execute_now",
        "execute_later",
        "accepted_authority_state",
        "authority_request",
        "requested_external_action",
    ),
)
def test_report_exposes_no_abi_or_causal_fixture_values(
    report: dict[str, Any], forbidden: str
) -> None:
    serialized = json.dumps(report, sort_keys=True, default=list)
    rendered = runner.render_living_gauntlet_v01(report)
    assert forbidden not in serialized
    assert forbidden not in rendered


def test_g1b2_report_geometry_and_prior_acts_are_exact(
    report: dict[str, Any],
) -> None:
    assert report["final_status"] == runner.STATUS_PASS
    assert report["counters"]["real_world_effects_count"] == 0
    assert report["active_act_results"][2]["act_id"] == "generic_integrity_replay"
    assert report["active_act_results"][3]["act_id"] == (
        "root_signer_isolation_conformance"
    )
    assert report["active_act_results"][4]["act_id"] == "semantic_work_contract"
    assert report["evidence_only_entries"][0]["act_id"] == (
        "airline_all_real_frozen_reference"
    )


@pytest.mark.parametrize("contract", ("Kernel ABI", "CausalConsumptionRef"))
def test_current_manifest_does_not_describe_active_contract_as_unimplemented(
    contract: str,
) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    statements = " ".join(
        item["statement"] for item in manifest["limitations"]
    )
    assert f"{contract} remains unimplemented" not in statements
    assert f"{contract} is unimplemented" not in statements
    assert runner._active_contract_described_unimplemented(
        runner._ACTIVE_ACT_IDS, manifest["limitations"]
    ) is False


@pytest.mark.parametrize(
    "stale_statement",
    (
        "Kernel ABI remains unimplemented.",
        "CausalConsumptionRef remains unimplemented.",
        (
            "Kernel ABI, CausalConsumptionRef, Transition Registry, Root "
            "Decision Kernel, and Effect Firewall remain unimplemented."
        ),
    ),
)
def test_stale_active_contract_limitation_fails_closed(
    stale_statement: str,
) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    limitation = next(
        item
        for item in manifest["limitations"]
        if item["limitation_id"]
        == "limitation_g1b1_in_memory_contract_conformance_only"
    )
    limitation["statement"] = stale_statement
    assert "completion_manifest_active_contract_described_unimplemented" in (
        runner._validate_completion_manifest_v01(manifest)
    )


def test_supplier_adapter_seam_acknowledges_active_abi() -> None:
    seam = next(
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == "supplier_water_filter_abi_adapter"
    )
    assert seam["status"] == runner.STATUS_ACTIVE
    assert seam["source_module"] == (
        "hedgehog.domains.supplier_water_filter.kernel_adapter_v01"
    )
    assert seam["effect_access"] == "NONE"
    assert "23 Kernel artifacts" in seam["notes"]
    assert "one-Root MIXED MultiRoot result" in seam["notes"]
    assert "remains unimplemented" not in seam["notes"]


def test_stale_supplier_adapter_seam_note_fails_closed() -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(
        item
        for item in index["seams"]
        if item["seam_id"] == "supplier_water_filter_abi_adapter"
    )
    seam["notes"] = (
        "Planned Supplier and Water Filter portability adapter; "
        "no ABI is implemented."
    )
    assert "integration_seam_active_abi_described_absent" in (
        runner._validate_integration_seam_index_v01(index)
    )


@pytest.mark.parametrize(
    "act_id", ("domain_neutral_kernel_abi", "causal_consumption")
)
def test_g1b2_acts_remain_active_after_coherence_hardening(act_id: str) -> None:
    active = {
        item["act_id"]
        for item in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
    }
    assert act_id in active


def test_release_coherence_hardening_preserves_g1b2_active_results(
    report: dict[str, Any],
) -> None:
    by_id = {item["act_id"]: item for item in report["active_act_results"]}
    for act_id in ("domain_neutral_kernel_abi", "causal_consumption"):
        assert by_id[act_id]["state"] == runner.STATUS_PASS
        assert by_id[act_id]["root_authority_preserved"] is True
        assert by_id[act_id]["real_world_effects_count"] == 0


@pytest.mark.parametrize(
    ("metrics_name", "counter"),
    (
        ("_collect_kernel_abi_fixture_metrics_v01", "provider_call_count"),
        ("_collect_kernel_abi_fixture_metrics_v01", "network_call_count"),
        ("_collect_kernel_abi_fixture_metrics_v01", "gemini_call_count"),
        ("_collect_kernel_abi_fixture_metrics_v01", "real_world_effects_count"),
        ("_collect_causal_consumption_fixture_metrics_v01", "provider_call_count"),
        ("_collect_causal_consumption_fixture_metrics_v01", "network_call_count"),
        ("_collect_causal_consumption_fixture_metrics_v01", "gemini_call_count"),
        ("_collect_causal_consumption_fixture_metrics_v01", "real_world_effects_count"),
    ),
)
def test_g1b2_fixture_external_and_effect_counts_remain_zero(
    metrics_name: str, counter: str
) -> None:
    assert getattr(runner, metrics_name)()[counter] == 0


# G1-C1 Transition Registry and deterministic Root Decision Kernel regressions.


@pytest.mark.parametrize("act_id,symbol,counter", (
    ("transition_registry", "collect_transition_registry_gauntlet_act_v01", "transition_registry_execution_count"),
    ("root_decision_kernel", "collect_root_decision_kernel_gauntlet_act_v01", "root_decision_kernel_execution_count"),
))
def test_g1c1_active_act_identity_and_counter(act_id, symbol, counter, report):
    row = next(item for item in report["active_act_results"] if item["act_id"] == act_id)
    assert row["source_module"] == "demo.run_living_gauntlet_v01"
    assert row["source_symbol"] == symbol
    assert row["state"] == runner.STATUS_PASS
    assert row["executed"] is True
    assert report["counters"][counter] == 1


@pytest.mark.parametrize("act_id", ("transition_registry", "root_decision_kernel"))
def test_g1c1_acts_are_not_planned_or_evidence_only(act_id, report):
    assert act_id not in {item["act_id"] for item in report["planned_entries"]}
    assert act_id not in {item["act_id"] for item in report["evidence_only_entries"]}


@pytest.mark.parametrize("claim_id,act_id,test_ref,evidence_ref,symbol", (
    ("claim_transition_registry_runtime_execution", "transition_registry", "tests/test_transition_registry_v01.py", "hedgehog/kernel/transition_registry_v01.py", "collect_transition_registry_gauntlet_act_v01"),
    ("claim_root_decision_kernel_runtime_execution", "root_decision_kernel", "tests/test_root_decision_kernel_v01.py", "hedgehog/kernel/root_decision_v01.py", "collect_root_decision_kernel_gauntlet_act_v01"),
))
def test_g1c1_claim_exact_references(claim_id, act_id, test_ref, evidence_ref, symbol):
    claim = next(item for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"] if item["claim_id"] == claim_id)
    assert claim["claim_class"] == "EXECUTED_RUNTIME"
    assert claim["act_ids"] == [act_id]
    assert claim["focused_test_ref"] == test_ref
    assert claim["evidence_ref"] == evidence_ref
    assert claim["runtime_ref"] == f"demo.run_living_gauntlet_v01:{symbol}"
    assert claim["limitation_ref"] == "limitation_g1c1_in_memory_transition_and_root_decision_only"


@pytest.mark.parametrize("claim_id", ("claim_transition_registry_runtime_execution", "claim_root_decision_kernel_runtime_execution"))
def test_g1c1_claim_changed_to_conformance_fails(claim_id):
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(item for item in manifest["public_claims"] if item["claim_id"] == claim_id)
    claim["claim_class"] = "EXECUTED_CONFORMANCE"
    assert f"public_claim_classification_mismatch:{claim_id}" in runner._validate_completion_manifest_v01(manifest)


def test_g1c1_planned_claim_preserves_only_current_unfinished_act():
    claims = _json(COMPLETION_MANIFEST_PATH)["public_claims"]
    assert all(item["claim_id"] != "claim_gate1_planned_not_active" for item in claims)


@pytest.mark.parametrize("limitation_id,phrases", (
    ("limitation_g1c1_in_memory_transition_and_root_decision_only", ("does not mutate artifacts or execute transitions", "RootDecisionResult only", "no permission", "no effect", "separately active in G1-C2")),
    ("limitation_gate1_not_implemented", ("Gate-1 runtime implementation is active through Kernel Conformance", "independent audit", "consolidated documentation closure remain pending")),
    ("limitation_g1b1_in_memory_contract_conformance_only", ("Transition Registry and Root Decision Kernel in G1-C1", "the mock-only Effect Firewall in G1-C2", "Supplier / Water Filter projection with Generic MultiRoot in G1-D2")),
    ("limitation_g1b2_in_memory_abi_and_counterfactual_only", ("Transition Registry and Root Decision Kernel are separately active in G1-C1", "the mock-only Effect Firewall in G1-C2", "Supplier / Water Filter projection with Generic MultiRoot in G1-D2")),
))
def test_g1c1_limitations_are_coherent(limitation_id, phrases):
    statement = next(item["statement"] for item in _json(COMPLETION_MANIFEST_PATH)["limitations"] if item["limitation_id"] == limitation_id)
    assert all(phrase in statement for phrase in phrases)


@pytest.mark.parametrize("act_id,phrase,reason", (
    ("transition_registry", "Transition Registry remains unimplemented.", "completion_manifest_active_transition_described_unimplemented"),
    ("transition_registry", "No Transition Registry exists.", "completion_manifest_active_transition_described_unimplemented"),
    ("transition_registry", "Not a transition system.", "completion_manifest_active_transition_described_unimplemented"),
    ("root_decision_kernel", "Root Decision Kernel remains unimplemented.", "completion_manifest_active_root_decision_described_unimplemented"),
    ("root_decision_kernel", "No Root Decision Kernel exists.", "completion_manifest_active_root_decision_described_unimplemented"),
    ("root_decision_kernel", "Not a Root decision.", "completion_manifest_active_root_decision_described_unimplemented"),
))
def test_g1c1_stale_manifest_absence_wording_fails(act_id, phrase, reason):
    manifest = _json(COMPLETION_MANIFEST_PATH)
    assert act_id in {item["act_id"] for item in manifest["active_runtime_acts"]}
    manifest["limitations"].append({"limitation_id": f"stale:{act_id}", "statement": phrase})
    assert reason in runner._validate_completion_manifest_v01(manifest)


@pytest.mark.parametrize("seam_id,module,symbol,seam_class,authority", (
    ("transition_registry", "hedgehog.kernel.transition_registry_v01", "lookup_transition_v01", "KERNEL_CORE", "NON_ROOT_IMMUTABLE_TRANSITION_POLICY"),
    ("root_decision_kernel", "hedgehog.kernel.root_decision_v01", "decide_root_v01", "KERNEL_ROOT_BOUNDARY", "ROOT_DECISION_AUTHORITY"),
))
def test_g1c1_seam_exact_active_contract(seam_id, module, symbol, seam_class, authority):
    seam = next(item for item in _json(SEAM_INDEX_PATH)["seams"] if item["seam_id"] == seam_id)
    assert seam["status"] == runner.STATUS_ACTIVE
    assert seam["source_module"] == module
    assert seam["source_symbol"] == symbol
    assert seam["seam_class"] == seam_class
    assert seam["authority_status"] == authority
    assert seam["effect_access"] == "NONE"


@pytest.mark.parametrize("seam_id,status", (
    ("transition_registry", runner.STATUS_REFERENCE_ONLY),
    ("transition_registry", runner.STATUS_PLANNED_NOT_ACTIVE),
    ("root_decision_kernel", runner.STATUS_REFERENCE_ONLY),
    ("root_decision_kernel", runner.STATUS_PLANNED_NOT_ACTIVE),
))
def test_g1c1_active_seam_status_mutation_fails(seam_id, status):
    index = _json(SEAM_INDEX_PATH)
    next(item for item in index["seams"] if item["seam_id"] == seam_id)["status"] = status
    assert f"current_seam_status_mismatch:{seam_id}" in runner._validate_integration_seam_index_v01(index)


@pytest.mark.parametrize("seam_id", ("transition_registry", "root_decision_kernel"))
def test_g1c1_active_seam_effect_access_mutation_fails(seam_id):
    index = _json(SEAM_INDEX_PATH)
    next(item for item in index["seams"] if item["seam_id"] == seam_id)["effect_access"] = "HANDLE"
    assert f"seam_effect_access_forbidden:{seam_id}" in runner._validate_integration_seam_index_v01(index)


def test_root_decision_seam_authority_status_mutation_fails():
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == "root_decision_kernel")
    seam["authority_status"] = "NON_ROOT_ADVISORY"
    assert "current_seam_contract_mismatch:root_decision_kernel" in runner._validate_integration_seam_index_v01(index)


@pytest.mark.parametrize("seam_id,note,reason", (
    ("transition_registry", "Transition Registry is unimplemented.", "integration_seam_active_transition_described_absent"),
    ("transition_registry", "Not a transition system.", "integration_seam_active_transition_described_absent"),
    ("root_decision_kernel", "Root Decision Kernel is unimplemented.", "integration_seam_active_root_decision_described_absent"),
    ("root_decision_kernel", "Not a Root decision.", "integration_seam_active_root_decision_described_absent"),
))
def test_g1c1_active_seam_stale_note_fails(seam_id, note, reason):
    index = _json(SEAM_INDEX_PATH)
    next(item for item in index["seams"] if item["seam_id"] == seam_id)["notes"] = note
    assert reason in runner._validate_integration_seam_index_v01(index)


def test_g1c1_seams_and_effect_firewall_boundary_remain_exact():
    seams = _json(SEAM_INDEX_PATH)["seams"]
    by_id = {item["seam_id"]: item for item in seams}
    assert by_id["transition_registry"]["status"] == runner.STATUS_ACTIVE
    assert by_id["root_decision_kernel"]["status"] == runner.STATUS_ACTIVE
    assert by_id["transition_registry"]["effect_access"] == "NONE"
    assert by_id["root_decision_kernel"]["effect_access"] == "NONE"
    active = [item for item in seams if item["status"] == runner.STATUS_ACTIVE]
    assert sum(item["effect_access"] != "NONE" for item in active) == 1
    firewall = by_id["effect_firewall"]
    assert firewall["effect_access"] == "BOUNDED_EFFECT_HANDLE_OWNER"


@pytest.mark.parametrize("key,expected", (
    ("rule_count", 18), ("allow_rule_count", 8), ("return_to_root_rule_count", 4),
    ("blocked_rule_count", 6), ("canonical_lookup_count", 18),
    ("needs_user_proof_count", 1), ("needs_more_evidence_proof_count", 1),
    ("unknown_transition_blocked_count", 1), ("unknown_major_blocked_count", 1),
    ("registry_mutation_rejected_count", 1),
))
def test_transition_registry_fixture_metrics(key, expected):
    assert runner._collect_transition_registry_fixture_metrics_v01()[key] == expected


@pytest.mark.parametrize("key,expected", (
    ("result_count", 10), ("blocked_count", 3), ("needs_user_count", 1),
    ("needs_more_evidence_count", 1), ("defer_count", 1), ("reject_count", 2),
    ("no_update_count", 1), ("accept_count", 1), ("root_commit_created_count", 10),
    ("permission_created_count", 0), ("final_output_created_count", 0),
    ("effect_requested_count", 0),
))
def test_root_decision_fixture_metrics(key, expected):
    assert runner._collect_root_decision_fixture_metrics_v01()[key] == expected


@pytest.mark.parametrize("needle", (
    "claim:deterministic", "1000000", "permission:fixture", "policy_state",
    "conflict_set_ids", "missing_evidence_refs", "prior_root_state",
))
def test_g1c1_report_and_render_hide_sensitive_fixture_details(needle, report):
    serialized = json.dumps(report, sort_keys=True)
    rendered = runner.render_living_gauntlet_v01(report)
    assert needle not in serialized
    assert needle not in rendered


@pytest.mark.parametrize("act_id,reason", (
    ("transition_registry", "transition_registry_collector_failed"),
    ("root_decision_kernel", "root_decision_kernel_collector_failed"),
))
def test_g1c1_failure_counter_tampering_cannot_restore_pass(act_id, reason, report):
    mutated = deepcopy(report)
    row = next(item for item in mutated["active_act_results"] if item["act_id"] == act_id)
    row.update(state=runner.STATUS_FAIL_CLOSED, runtime_status=runner.STATUS_FAIL_CLOSED, root_authority_preserved=False, no_real_connector_or_action=False, real_world_effects_count=-1, errors=(reason,))
    mutated["counters"] = runner._derive_report_counters_v01(mutated["active_act_results"], mutated["evidence_only_entries"], mutated["planned_entries"])
    mutated["counters"]["active_act_pass_count"] = 9
    mutated["final_status"] = runner.STATUS_PASS
    valid, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert valid is False
    assert f"report_active_act_state_not_pass:{act_id}" in errors


@pytest.mark.parametrize("collector,act_id,reason", (
    ("collect_transition_registry_gauntlet_act_v01", "transition_registry", "transition_registry_collector_failed"),
    ("collect_root_decision_kernel_gauntlet_act_v01", "root_decision_kernel", "root_decision_kernel_collector_failed"),
))
def test_g1c1_collector_exception_fails_complete_report_closed(collector, act_id, reason, monkeypatch):
    def explode():
        raise RuntimeError("CALLER_SECRET")

    monkeypatch.setattr(runner, collector, explode)
    failed = runner.collect_living_gauntlet_v01()
    row = next(item for item in failed["active_act_results"] if item["act_id"] == act_id)
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert row["state"] == runner.STATUS_FAIL_CLOSED
    assert row["real_world_effects_count"] == -1
    assert row["errors"] == (reason,)
    assert "CALLER_SECRET" not in json.dumps(failed)


# G1-C2 exclusive mock-only Effect Firewall regressions.


@pytest.fixture(scope="module")
def effect_metrics() -> dict[str, Any]:
    return runner._collect_effect_firewall_fixture_metrics_v01()


def test_g1c2_effect_act_is_active_and_passes(report: dict[str, Any]) -> None:
    row = next(
        item
        for item in report["active_act_results"]
        if item["act_id"] == "effect_firewall"
    )
    assert row == {
        "act_id": "effect_firewall",
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": "collect_effect_firewall_gauntlet_act_v01",
        "state": runner.STATUS_PASS,
    }


def test_g1c2_geometry_is_exact(report: dict[str, Any]) -> None:
    assert report["final_status"] == runner.STATUS_PASS
    assert report["validation_errors"] == ()
    assert report["counters"]["active_act_fail_closed_count"] == 0
    assert report["counters"]["effect_firewall_execution_count"] == 1
    assert report["counters"]["real_world_effects_count"] == 0


def test_g1c2_effect_source_identity_is_exact() -> None:
    assert runner._ACTIVE_ACT_SOURCES["effect_firewall"] == (
        "demo.run_living_gauntlet_v01",
        "collect_effect_firewall_gauntlet_act_v01",
    )


def test_g1c2_effect_claim_has_exact_references() -> None:
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == "claim_effect_firewall_runtime_execution"
    )
    assert claim["claim_class"] == "EXECUTED_RUNTIME"
    assert claim["act_ids"] == ["effect_firewall"]
    assert claim["runtime_ref"] == (
        "demo.run_living_gauntlet_v01:collect_effect_firewall_gauntlet_act_v01"
    )
    assert claim["focused_test_ref"] == "tests/test_effect_firewall_v01.py"
    assert claim["evidence_ref"] == "hedgehog/kernel/effect_firewall_v01.py"
    assert claim["limitation_ref"] == "limitation_g1c2_in_memory_mock_effect_only"


@pytest.mark.parametrize(
    "claim_class",
    ("EXECUTED_CONFORMANCE", runner.STATUS_EVIDENCE_ONLY, runner.STATUS_PLANNED_NOT_ACTIVE),
)
def test_g1c2_effect_claim_reclassification_fails_closed(claim_class: str) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(
        item
        for item in manifest["public_claims"]
        if item["claim_id"] == "claim_effect_firewall_runtime_execution"
    )
    claim["claim_class"] = claim_class
    assert "public_claim_classification_mismatch:claim_effect_firewall_runtime_execution" in (
        runner._validate_completion_manifest_v01(manifest)
    )


def test_g1c2_effect_act_is_removed_from_all_nonactive_groups() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    report = runner.collect_living_gauntlet_v01()
    assert "effect_firewall" not in {
        item["act_id"] for item in manifest["planned_gate1_acts"]
    }
    assert "effect_firewall" not in {
        item["act_id"] for item in manifest["evidence_only_references"]
    }
    assert "effect_firewall" not in {
        item["act_id"] for item in report["planned_entries"]
    }


def test_g1c2_planned_claim_preserves_only_current_unfinished_act() -> None:
    claims = _json(COMPLETION_MANIFEST_PATH)["public_claims"]
    assert all(item["claim_id"] != "claim_gate1_planned_not_active" for item in claims)


@pytest.mark.parametrize(
    ("limitation_id", "phrase"),
    (
        ("limitation_g1c2_in_memory_mock_effect_only", "domain-neutral and in-memory"),
        ("limitation_g1c2_in_memory_mock_effect_only", "invocation-local"),
        ("limitation_g1c2_in_memory_mock_effect_only", "logical ticks"),
        ("limitation_g1c2_in_memory_mock_effect_only", "neutral mock execution"),
        ("limitation_g1c2_in_memory_mock_effect_only", "No real adapter"),
        ("limitation_g1c2_in_memory_mock_effect_only", "No real connector"),
        ("limitation_g1c2_in_memory_mock_effect_only", "no production permission registry"),
        ("limitation_g1c2_in_memory_mock_effect_only", "no revocation"),
        ("limitation_g1c2_in_memory_mock_effect_only", "supersession"),
        ("limitation_g1c2_in_memory_mock_effect_only", "distributed idempotency"),
        ("limitation_g1c2_in_memory_mock_effect_only", "receipt is evidence only"),
        ("limitation_g1c2_in_memory_mock_effect_only", "later Root confirmation"),
        ("limitation_g1c2_in_memory_mock_effect_only", "Supplier / Water Filter projection with Generic MultiRoot is separately active in G1-D2"),
        ("limitation_g1c2_in_memory_mock_effect_only", "frozen Airline projection adapter is separately active in G1-D1"),
        ("limitation_g1c2_in_memory_mock_effect_only", "not production security certification"),
        ("limitation_g1b1_in_memory_contract_conformance_only", "the mock-only Effect Firewall in G1-C2"),
        ("limitation_g1b2_in_memory_abi_and_counterfactual_only", "the mock-only Effect Firewall in G1-C2"),
        ("limitation_g1c1_in_memory_transition_and_root_decision_only", "the mock-only Effect Firewall is separately active in G1-C2"),
    ),
)
def test_g1c2_limitations_are_explicit(limitation_id: str, phrase: str) -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == limitation_id
    )
    assert phrase in statement


def test_gate1_limitation_records_active_runtime_and_pending_nonruntime_closure() -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == "limitation_gate1_not_implemented"
    )
    for required in (
        "Gate-1 runtime implementation is active through Kernel Conformance",
        "independent audit",
        "consolidated documentation closure remain pending",
    ):
        assert required in statement
    assert (
        "Only final Kernel Conformance closure remains unimplemented."
        not in statement
    )
    for active_capability in (
        "Generic MultiRoot",
        "Supplier",
        "Effect Firewall",
        "Transition Registry",
        "Root Decision Kernel",
        "Airline adapter",
    ):
        assert active_capability not in statement


@pytest.mark.parametrize(
    "phrase",
    (
        "Effect Firewall remains unimplemented.",
        "Effect Firewall is unimplemented.",
        "No effect handle exists.",
        "No effect request exists.",
        "Not effect execution.",
    ),
)
def test_g1c2_stale_manifest_absence_wording_fails_closed(phrase: str) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    manifest["limitations"].append(
        {"limitation_id": "limitation:stale:effect", "statement": phrase}
    )
    assert "completion_manifest_active_effect_firewall_described_unimplemented" in (
        runner._validate_completion_manifest_v01(manifest)
    )


@pytest.mark.parametrize(
    "statement",
    (
        "No real effect is performed.",
        "No external effect is performed.",
        "No production effect is performed.",
        "No transferable effect handle is exposed.",
    ),
)
def test_g1c2_honest_no_real_effect_wording_remains_valid(statement: str) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    manifest["limitations"].append(
        {"limitation_id": "limitation:honest:effect", "statement": statement}
    )
    assert runner._validate_completion_manifest_v01(manifest) == ()


@pytest.mark.parametrize(
    ("field", "expected"),
    (
        ("status", runner.STATUS_ACTIVE),
        ("source_module", "hedgehog.kernel.effect_firewall_v01"),
        ("source_symbol", "execute_mock_effect_v01"),
        ("seam_class", "KERNEL_EFFECT_BOUNDARY"),
        ("authority_status", "ROOT_SCOPED_EXCLUSIVE_EFFECT_BOUNDARY"),
        ("current_mode", "PURE_IN_MEMORY_MOCK_ONLY_CAPABILITY_EXECUTION"),
        ("effect_access", "BOUNDED_EFFECT_HANDLE_OWNER"),
        ("gate1_target", "effect_firewall"),
    ),
)
def test_g1c2_effect_seam_exact_contract(field: str, expected: str) -> None:
    seam = next(
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == "effect_firewall"
    )
    assert seam[field] == expected


def test_g1c2_effect_seam_is_importable() -> None:
    seam = next(
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == "effect_firewall"
    )
    module = importlib.import_module(seam["source_module"])
    assert getattr(module, seam["source_symbol"]) is runner.execute_mock_effect_v01


def test_g1c2_exclusive_effect_owner_remains_exact() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    owners = [
        item
        for item in seams
        if item["status"] == runner.STATUS_ACTIVE
        and item["effect_access"] != "NONE"
    ]
    assert [(item["seam_id"], item["effect_access"]) for item in owners] == [
        ("effect_firewall", "BOUNDED_EFFECT_HANDLE_OWNER")
    ]
    assert all(
        item["effect_access"] != "BOUNDED_EFFECT_HANDLE_OWNER_PLANNED"
        for item in seams
    )


@pytest.mark.parametrize(
    "seam_id",
    (
        "core_semantic_reasoning_adapter",
        "deterministic_airline_reference_collector",
        "core_mock_connector_sandbox",
        "core_action_commit_packet",
        "root_decision_kernel",
        "causal_consumption_core",
    ),
)
def test_g1c2_nonfirewall_seam_cannot_gain_effect_access(seam_id: str) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == seam_id)
    seam["effect_access"] = "BOUNDED_EFFECT_HANDLE_OWNER"
    errors = runner._validate_integration_seam_index_v01(index)
    assert "integration_seam_non_firewall_effect_access_forbidden" in errors
    assert "integration_seam_effect_owner_count_invalid" in errors


@pytest.mark.parametrize(
    "status", (runner.STATUS_REFERENCE_ONLY, runner.STATUS_PLANNED_NOT_ACTIVE)
)
def test_g1c2_firewall_seam_cannot_become_inactive(status: str) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == "effect_firewall")
    seam["status"] = status
    errors = runner._validate_integration_seam_index_v01(index)
    assert "current_seam_status_mismatch:effect_firewall" in errors
    assert "integration_seam_effect_owner_identity_invalid" in errors


@pytest.mark.parametrize(
    "mutation",
    (
        {"effect_access": "NONE"},
        {"effect_access": "BOUNDED_EFFECT_HANDLE_OWNER_PLANNED"},
        {"authority_status": "NON_ROOT"},
        {"source_module": "other.module"},
        {"source_symbol": "other_symbol"},
    ),
)
def test_g1c2_firewall_seam_contract_mutation_fails(mutation: dict[str, str]) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == "effect_firewall")
    seam.update(mutation)
    assert runner._validate_integration_seam_index_v01(index)


@pytest.mark.parametrize(
    "note",
    (
        "Effect Firewall is unimplemented.",
        "No effect handle exists.",
        "No effect request exists.",
        "Not effect execution.",
    ),
)
def test_g1c2_firewall_seam_stale_note_fails(note: str) -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(item for item in index["seams"] if item["seam_id"] == "effect_firewall")
    seam["notes"] = note
    assert "integration_seam_active_effect_firewall_described_absent" in (
        runner._validate_integration_seam_index_v01(index)
    )


@pytest.mark.parametrize(
    ("key", "expected"),
    (
        ("firewall_count", 1),
        ("request_count", 1),
        ("allowed_authorization_count", 1),
        ("capability_issued_count", 1),
        ("mock_effect_execution_count", 1),
        ("evidence_receipt_count", 1),
        ("return_to_root_transition_count", 1),
        ("duplicate_execution_success_count", 0),
        ("negative_test_count", 22),
        ("capability_public_exposure_count", 0),
        ("permission_created_count", 0),
        ("root_decision_created_by_firewall_count", 0),
        ("final_output_created_count", 0),
        ("real_connector_count", 0),
        ("provider_call_count", 0),
        ("network_call_count", 0),
        ("gemini_call_count", 0),
        ("real_world_effects_count", 0),
    ),
)
def test_g1c2_fixture_metrics_are_exact(
    effect_metrics: dict[str, Any], key: str, expected: int
) -> None:
    assert effect_metrics[key] == expected


@pytest.mark.parametrize(
    "needle",
    (
        "permission:fixture:effect_firewall:001",
        "scope:neutral:alpha",
        "mock_adapter:bounded_neutral_v01",
        "mock_action:record_neutral_receipt",
        "idempotency:fixture:effect_firewall:001",
        "receipt:fixture:effect_firewall:001",
        "invocation:fixture:effect_firewall:001",
        "selected_candidate_id",
        "capability_id",
        "issuer_token",
        "private state",
    ),
)
def test_g1c2_report_and_render_hide_effect_fixture_details(
    report: dict[str, Any], needle: str
) -> None:
    serialized = json.dumps(report, sort_keys=True)
    rendered = runner.render_living_gauntlet_v01(report)
    assert needle not in serialized
    assert needle not in rendered


def test_g1c2_renderer_shows_effect_act(report: dict[str, Any]) -> None:
    rendered = runner.render_living_gauntlet_v01(report)
    assert "act_id=effect_firewall | state=PASS" in rendered


def test_g1c2_effect_collector_exception_fails_complete_report_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def explode() -> None:
        raise RuntimeError("CALLER_SECRET_EFFECT")

    monkeypatch.setattr(runner, "collect_effect_firewall_gauntlet_act_v01", explode)
    failed = runner.collect_living_gauntlet_v01()
    row = next(
        item for item in failed["active_act_results"] if item["act_id"] == "effect_firewall"
    )
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert row["state"] == runner.STATUS_FAIL_CLOSED
    assert row["real_world_effects_count"] == -1
    assert row["errors"] == ("effect_firewall_collector_failed",)
    assert "CALLER_SECRET_EFFECT" not in json.dumps(failed)


def test_g1c2_counter_tampering_cannot_hide_effect_failure(
    report: dict[str, Any],
) -> None:
    mutated = deepcopy(report)
    row = next(
        item
        for item in mutated["active_act_results"]
        if item["act_id"] == "effect_firewall"
    )
    row.update(
        state=runner.STATUS_FAIL_CLOSED,
        runtime_status=runner.STATUS_FAIL_CLOSED,
        root_authority_preserved=False,
        no_real_connector_or_action=False,
        real_world_effects_count=-1,
        errors=("effect_firewall_collector_failed",),
    )
    mutated["counters"] = runner._derive_report_counters_v01(
        mutated["active_act_results"],
        mutated["evidence_only_entries"],
        mutated["planned_entries"],
    )
    mutated["counters"]["active_act_pass_count"] = 12
    mutated["counters"]["effect_firewall_execution_count"] = 1
    mutated["final_status"] = runner.STATUS_PASS
    valid, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert valid is False
    assert "report_active_act_state_not_pass:effect_firewall" in errors
    assert "report_real_world_effects_nonzero:effect_firewall" in errors


def test_g1c2_source_identity_tampering_fails(report: dict[str, Any]) -> None:
    mutated = deepcopy(report)
    row = next(
        item
        for item in mutated["active_act_results"]
        if item["act_id"] == "effect_firewall"
    )
    row["source_symbol"] = "forged_collector"
    valid, errors = runner.validate_living_gauntlet_report_v01(mutated)
    assert valid is False
    assert "report_active_source_identity_mismatch:effect_firewall" in errors


def test_g1c2_two_reports_and_renders_are_identical() -> None:
    first = runner.collect_living_gauntlet_v01()
    second = runner.collect_living_gauntlet_v01()
    assert first == second
    assert runner.render_living_gauntlet_v01(first) == runner.render_living_gauntlet_v01(second)


def test_g1d1_runner_version_and_geometry_are_exact(
    report: dict[str, Any],
) -> None:
    assert report["final_status"] == runner.STATUS_PASS
    assert report["counters"]["generic_integrity_replay_execution_count"] == 1


def test_g1d1_generic_active_record_has_exact_two_claims() -> None:
    record = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
        if item["act_id"] == "generic_integrity_replay"
    )
    assert record["source_module"] == "demo.run_living_gauntlet_v01"
    assert record["source_symbol"] == "collect_generic_integrity_replay_gauntlet_act_v01"
    assert record["claim_ids"] == [
        "claim_generic_integrity_replay_execution",
        "claim_airline_kernel_adapter_execution",
    ]


@pytest.mark.parametrize(
    "field,expected",
    (
        ("claim_class", "EXECUTED_RUNTIME"),
        ("act_ids", ["generic_integrity_replay"]),
        (
            "runtime_ref",
            "demo.run_living_gauntlet_v01:collect_generic_integrity_replay_gauntlet_act_v01",
        ),
        ("focused_test_ref", "tests/test_airline_kernel_adapter_v01.py"),
        ("evidence_ref", "hedgehog/domains/airline/kernel_adapter_v01.py"),
        ("limitation_ref", "limitation_g1d1_frozen_airline_projection_only"),
    ),
)
def test_g1d1_airline_claim_refs_are_exact(field: str, expected: object) -> None:
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == "claim_airline_kernel_adapter_execution"
    )
    assert claim[field] == expected


def _g1d1_claim_honesty_errors(manifest: dict[str, Any]) -> tuple[str, ...]:
    texts = [
        item.get("statement", "").lower()
        for key in ("public_claims", "limitations")
        for item in manifest.get(key, [])
        if isinstance(item, dict)
        and item.get("claim_id", item.get("limitation_id"))
        in {
            "claim_airline_kernel_adapter_execution",
            "limitation_g1d1_frozen_airline_projection_only",
        }
    ]
    if any("exact frozen airline proof oracle" in text for text in texts):
        return ("completion_manifest_g1d1_committed_oracle_overclaim",)
    return ()


def test_g1d1_claim_describes_deterministic_in_memory_conformance_fixture() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    claim = next(
        item
        for item in manifest["public_claims"]
        if item["claim_id"] == "claim_airline_kernel_adapter_execution"
    )
    assert "deterministic in-memory Offer A conformance fixture" in claim["statement"]
    assert "built from frozen Airline contracts" in claim["statement"]
    assert "does not load or execute the committed all-real package" in claim["statement"]
    assert _g1d1_claim_honesty_errors(manifest) == ()


@pytest.mark.parametrize(
    "phrase",
    (
        "accepted frozen Airline contract shape",
        "Offer A",
        "exact transaction",
        "three Roots",
        "type sequence",
        "19 / 29 / 3 Ledger",
        "9 / 11 Crypto",
        "deterministic and synthetic in-memory",
        "does not prove byte equality with the committed all-real package",
        "caller-supplied expected hash is not committed external trust",
        "No package or filesystem access occurs",
        "no all-real lane is rerun",
        "Human Story",
        "derived projection identity",
        "do not prove semantic truth",
        "signature verification remains false",
        "Root Attestation remains deferred",
        "Supplier / Water Filter portability and Generic MultiRoot are separately active in G1-D2",
        "not production integration",
    ),
)
def test_g1d1_limitation_is_explicit(phrase: str) -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == "limitation_g1d1_frozen_airline_projection_only"
    )
    assert phrase in statement


def test_g1d1_stale_exact_committed_oracle_wording_fails_honesty_validation() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    limitation = next(
        item
        for item in manifest["limitations"]
        if item["limitation_id"] == "limitation_g1d1_frozen_airline_projection_only"
    )
    limitation["statement"] = "This adapter accepts the exact frozen Airline proof oracle."
    assert _g1d1_claim_honesty_errors(manifest) == (
        "completion_manifest_g1d1_committed_oracle_overclaim",
    )


def test_g1d1_non_claims_exclude_committed_package_execution_and_anchor_provenance() -> None:
    non_claims = _json(COMPLETION_MANIFEST_PATH)["non_claims"]
    assert "not execution of the committed all-real package" in non_claims
    assert "not committed external Anchor provenance" in non_claims


@pytest.mark.parametrize(
    "phrase",
    (
        "Airline adapter remains unimplemented.",
        "No Airline adapter exists.",
        "Not an Airline integrity adapter.",
    ),
)
def test_g1d1_stale_manifest_absence_wording_fails(phrase: str) -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    manifest["non_claims"].append(phrase)
    assert "completion_manifest_active_airline_adapter_described_unimplemented" in (
        runner._validate_completion_manifest_v01(manifest)
    )


@pytest.mark.parametrize(
    "field,expected",
    (
        ("status", runner.STATUS_ACTIVE),
        ("authority_status", "NON_ROOT_FROZEN_DOMAIN_ADAPTER"),
        ("current_mode", "PURE_IN_MEMORY_FROZEN_AIRLINE_PROJECTION"),
        ("effect_access", "NONE"),
        ("gate1_target", "generic_integrity_replay"),
        ("seam_class", "DOMAIN_ADAPTER"),
        ("source_module", "hedgehog.domains.airline.kernel_adapter_v01"),
        ("source_symbol", "build_airline_kernel_adapter_result_v01"),
    ),
)
def test_g1d1_adapter_seam_contract_is_exact(field: str, expected: str) -> None:
    seam = next(
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    assert seam[field] == expected


def test_g1d1_airline_adapter_seam_remains_active_without_effect_access() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    seam = next(
        item for item in seams if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    assert seam["status"] == runner.STATUS_ACTIVE
    assert seam["effect_access"] == "NONE"
    assert seam["source_module"] == "hedgehog.domains.airline.kernel_adapter_v01"


def test_g1d1_airline_reference_seams_remain_reference_only() -> None:
    seams = {
        item["seam_id"]: item for item in _json(SEAM_INDEX_PATH)["seams"]
    }
    for seam_id in (
        "airline_transaction_artifact_ledger_reference",
        "airline_crypto_artifact_seal_reference",
        "airline_sealed_trace_replay_reference",
    ):
        assert seams[seam_id]["status"] == runner.STATUS_REFERENCE_ONLY


def test_g1d1_effect_firewall_remains_only_effect_owner() -> None:
    owners = [
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["status"] == runner.STATUS_ACTIVE and item["effect_access"] != "NONE"
    ]
    assert [(item["seam_id"], item["effect_access"]) for item in owners] == [
        ("effect_firewall", "BOUNDED_EFFECT_HANDLE_OWNER")
    ]


def test_g1d1_adapter_cannot_gain_effect_access() -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(
        item for item in index["seams"] if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    seam["effect_access"] = "BOUNDED_EFFECT_HANDLE_OWNER"
    errors = runner._validate_integration_seam_index_v01(index)
    assert "integration_seam_domain_adapter_effect_access_forbidden" in errors


def test_g1d1_adapter_cannot_claim_root_authority() -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(
        item for item in index["seams"] if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    seam["authority_status"] = "ROOT_DECISION_AUTHORITY"
    assert "current_seam_contract_mismatch:generic_integrity_replay_adapter" in (
        runner._validate_integration_seam_index_v01(index)
    )


def test_g1d1_adapter_source_mutation_has_stable_reason() -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(
        item for item in index["seams"] if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    seam["source_module"] = "wrong.module"
    assert "integration_seam_airline_adapter_source_mismatch" in (
        runner._validate_integration_seam_index_v01(index)
    )


def test_g1d1_stale_adapter_seam_note_fails() -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(
        item for item in index["seams"] if item["seam_id"] == "generic_integrity_replay_adapter"
    )
    seam["notes"] = "Airline adapter is unimplemented."
    assert "integration_seam_active_airline_adapter_described_absent" in (
        runner._validate_integration_seam_index_v01(index)
    )


def test_g1d1_adapter_fixture_failure_fails_generic_act_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_fixture() -> None:
        raise RuntimeError("test-only adapter failure")

    monkeypatch.setattr(
        runner,
        "_validate_frozen_airline_kernel_adapter_fixture_v01",
        fail_fixture,
    )
    result = runner.collect_generic_integrity_replay_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.runtime_status == runner.STATUS_FAIL_CLOSED
    assert result.real_world_effects_count == -1
    assert result.errors == ("generic_integrity_replay_failed",)


@pytest.mark.parametrize(
    "needle",
    (
        "airline_kernel_adapter_living_fixture_v01",
        "source_manifest_core_hash",
        "airline_artifact_hash",
        "/airline_artifact_hash",
        "used:airline_ledger_dependency_hash",
        "causal_consumption_refs",
    ),
)
def test_g1d1_report_and_render_hide_adapter_details(
    needle: str,
    report: dict[str, Any],
) -> None:
    rendered = runner.render_living_gauntlet_v01(report)
    assert needle not in repr(report)
    assert needle not in rendered


def test_g1d1_zero_external_and_effect_counters_remain_exact(
    report: dict[str, Any],
) -> None:
    counters = report["counters"]
    assert frozenset(counters) == runner._COUNTER_FIELD_NAMES
    assert "provider_call_count" not in counters
    assert "network_call_count" not in counters
    assert "gemini_called_count" not in counters
    assert counters["real_world_effects_count"] == 0

    result = next(
        item
        for item in report["active_act_results"]
        if item["act_id"] == "generic_integrity_replay"
    )
    assert result["state"] == runner.STATUS_PASS
    assert result["runtime_status"] == runner.STATUS_PASS
    assert result["executed"] is True
    assert result["root_authority_preserved"] is True
    assert result["no_real_connector_or_action"] is True
    assert result["real_world_effects_count"] == 0
    assert result["errors"] == ()


def test_g1d2_runner_version_and_geometry_are_exact(report: dict[str, Any]) -> None:
    assert report["final_status"] == runner.STATUS_PASS
    assert report["validation_errors"] == ()
    assert report["counters"]["generic_multiroot_execution_count"] == 1
    assert report["counters"]["supplier_water_filter_portability_execution_count"] == 1


def test_g1d2_new_active_and_remaining_planned_ids_are_exact() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    active_ids = tuple(item["act_id"] for item in manifest["active_runtime_acts"])
    planned_ids = tuple(item["act_id"] for item in manifest["planned_gate1_acts"])
    assert active_ids[-3:-1] == (
        "generic_multiroot",
        "supplier_water_filter_portability",
    )
    assert planned_ids == ()


@pytest.mark.parametrize(
    ("act_id", "claim_id", "focused_test", "source_symbol"),
    (
        (
            "generic_multiroot",
            "claim_generic_multiroot_execution",
            "tests/test_multiroot_v01.py",
            "collect_generic_multiroot_gauntlet_act_v01",
        ),
        (
            "supplier_water_filter_portability",
            "claim_supplier_water_filter_portability_execution",
            "tests/test_supplier_water_filter_kernel_adapter_v01.py",
            "collect_supplier_water_filter_portability_gauntlet_act_v01",
        ),
    ),
)
def test_g1d2_active_records_are_exact(act_id, claim_id, focused_test, source_symbol):
    record = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["active_runtime_acts"]
        if item["act_id"] == act_id
    )
    assert record == {
        "act_id": act_id,
        "claim_ids": [claim_id],
        "focused_test": focused_test,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": source_symbol,
        "status": runner.STATUS_ACTIVE,
    }


@pytest.mark.parametrize(
    ("claim_id", "claim_class", "act_id", "evidence_ref", "focused_ref", "runtime_symbol", "limitation_ref"),
    (
        (
            "claim_generic_multiroot_execution",
            "EXECUTED_CONFORMANCE",
            "generic_multiroot",
            "hedgehog/kernel/multiroot_v01.py",
            "tests/test_multiroot_v01.py",
            "collect_generic_multiroot_gauntlet_act_v01",
            "limitation_g1d2_generic_multiroot_conformance_only",
        ),
        (
            "claim_supplier_water_filter_portability_execution",
            "EXECUTED_RUNTIME",
            "supplier_water_filter_portability",
            "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
            "tests/test_supplier_water_filter_kernel_adapter_v01.py",
            "collect_supplier_water_filter_portability_gauntlet_act_v01",
            "limitation_g1d2_supplier_water_filter_projection_only",
        ),
    ),
)
def test_g1d2_claims_are_exact(
    claim_id, claim_class, act_id, evidence_ref, focused_ref, runtime_symbol, limitation_ref
):
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == claim_id
    )
    assert claim["claim_class"] == claim_class
    assert claim["act_ids"] == [act_id]
    assert claim["evidence_ref"] == evidence_ref
    assert claim["focused_test_ref"] == focused_ref
    assert claim["runtime_ref"] == f"demo.run_living_gauntlet_v01:{runtime_symbol}"
    assert claim["limitation_ref"] == limitation_ref


@pytest.mark.parametrize(
    ("limitation_id", "phrases"),
    (
        (
            "limitation_g1d2_generic_multiroot_conformance_only",
            ("pure in-memory", "no SuperRoot", "no authority transfer", "no permission transfer", "no real effect"),
        ),
        (
            "limitation_g1d2_supplier_water_filter_projection_only",
            ("exact deterministic Full WOW v1.2", "not arbitrary Supplier transactions", "no live provider", "derived local identity", "remains MIXED", "not production integration"),
        ),
    ),
)
def test_g1d2_limitations_are_honest(limitation_id, phrases):
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == limitation_id
    )
    assert all(phrase in statement for phrase in phrases)


@pytest.mark.parametrize(
    ("phrase", "reason"),
    (
        ("Generic MultiRoot remains unimplemented.", "completion_manifest_active_multiroot_described_unimplemented"),
        ("Not Generic MultiRoot.", "completion_manifest_active_multiroot_described_unimplemented"),
        ("Supplier / Water Filter portability remains unimplemented.", "completion_manifest_active_supplier_adapter_described_unimplemented"),
        ("Not Supplier or Water Filter portability.", "completion_manifest_active_supplier_adapter_described_unimplemented"),
    ),
)
def test_g1d2_stale_unimplemented_wording_fails(phrase, reason):
    manifest = _json(COMPLETION_MANIFEST_PATH)
    manifest["non_claims"].append(phrase)
    assert reason in runner._validate_completion_manifest_v01(manifest)


@pytest.mark.parametrize(
    ("seam_id", "expected"),
    (
        (
            "supplier_water_filter_abi_adapter",
            {
                "authority_status": "NON_ROOT_DOMAIN_ADAPTER",
                "current_mode": "PURE_IN_MEMORY_DETERMINISTIC_PRODUCT_TRACE_PROJECTION",
                "effect_access": "NONE",
                "gate1_target": "supplier_water_filter_portability",
                "seam_class": "DOMAIN_ADAPTER",
                "source_module": "hedgehog.domains.supplier_water_filter.kernel_adapter_v01",
                "source_symbol": "build_supplier_water_filter_kernel_adapter_result_v01",
                "status": runner.STATUS_ACTIVE,
            },
        ),
        (
            "multiroot_envelope",
            {
                "authority_status": "INDEPENDENT_ROOT_OUTCOME_PROTOCOL",
                "current_mode": "PURE_IN_MEMORY_SOVEREIGN_ROOT_GEOMETRY",
                "effect_access": "NONE",
                "gate1_target": "generic_multiroot",
                "seam_class": "KERNEL_ROOT_BOUNDARY",
                "source_module": "hedgehog.kernel.multiroot_v01",
                "source_symbol": "validate_multiroot_v01",
                "status": runner.STATUS_ACTIVE,
            },
        ),
    ),
)
def test_g1d2_seam_contracts_are_exact(seam_id, expected):
    seam = next(
        item for item in _json(SEAM_INDEX_PATH)["seams"] if item["seam_id"] == seam_id
    )
    for key, value in expected.items():
        assert seam[key] == value


def test_g1d2_seam_geometry_and_effect_owner_are_exact() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    assert next(
        item for item in seams if item["seam_id"] == "multiroot_envelope"
    )["status"] == runner.STATUS_ACTIVE
    assert next(
        item
        for item in seams
        if item["seam_id"] == "supplier_water_filter_abi_adapter"
    )["status"] == runner.STATUS_ACTIVE
    owners = [
        (item["seam_id"], item["effect_access"])
        for item in seams
        if item["status"] == runner.STATUS_ACTIVE and item["effect_access"] != "NONE"
    ]
    assert owners == [("effect_firewall", "BOUNDED_EFFECT_HANDLE_OWNER")]


@pytest.mark.parametrize(
    "seam_id", ("generic_integrity_replay_adapter", "supplier_water_filter_abi_adapter")
)
def test_g1d2_domain_adapters_have_no_effect_access(seam_id):
    seam = next(
        item for item in _json(SEAM_INDEX_PATH)["seams"] if item["seam_id"] == seam_id
    )
    assert seam["effect_access"] == "NONE"


def test_g1d2_supplier_adapter_cannot_gain_effect_access() -> None:
    index = _json(SEAM_INDEX_PATH)
    seam = next(
        item for item in index["seams"] if item["seam_id"] == "supplier_water_filter_abi_adapter"
    )
    seam["effect_access"] = "BOUNDED_EFFECT_HANDLE_OWNER"
    errors = runner._validate_integration_seam_index_v01(index)
    assert "integration_seam_domain_adapter_effect_access_forbidden" in errors


def test_g1d2_airline_reference_remains_evidence_only() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    assert manifest["evidence_only_references"][0]["act_id"] == "airline_all_real_frozen_reference"
    assert manifest["evidence_only_references"][0]["status"] == runner.STATUS_EVIDENCE_ONLY


@pytest.mark.parametrize(
    ("act_id", "expected_symbol"),
    (
        ("generic_multiroot", "collect_generic_multiroot_gauntlet_act_v01"),
        ("supplier_water_filter_portability", "collect_supplier_water_filter_portability_gauntlet_act_v01"),
    ),
)
def test_g1d2_active_result_is_safe_pass(report, act_id, expected_symbol):
    result = next(item for item in report["active_act_results"] if item["act_id"] == act_id)
    assert result == {
        "act_id": act_id,
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_living_gauntlet_v01",
        "source_symbol": expected_symbol,
        "state": runner.STATUS_PASS,
    }


def test_g1d2_supplier_collector_is_called_exactly_once(monkeypatch):
    original = runner.collect_full_wow_v1_2_product_trace
    calls = 0

    def counted():
        nonlocal calls
        calls += 1
        return original()

    monkeypatch.setattr(runner, "collect_full_wow_v1_2_product_trace", counted)
    result = runner.collect_supplier_water_filter_portability_gauntlet_act_v01()
    assert calls == 1
    assert result.state == runner.STATUS_PASS


def test_g1d2_source_collector_failure_fails_supplier_act_closed(monkeypatch):
    def fail():
        raise RuntimeError("test-only")

    monkeypatch.setattr(runner, "collect_full_wow_v1_2_product_trace", fail)
    result = runner.collect_supplier_water_filter_portability_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.real_world_effects_count == -1
    assert result.errors == ("supplier_water_filter_runtime_failed",)


def test_g1d2_adapter_failure_fails_supplier_act_closed(monkeypatch):
    def fail(*, source_report):
        raise ValueError("test-only")

    monkeypatch.setattr(
        runner.supplier_water_filter_adapter,
        "build_supplier_water_filter_kernel_adapter_result_v01",
        fail,
    )
    result = runner.collect_supplier_water_filter_portability_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.real_world_effects_count == -1


def test_g1d2_forged_supplier_multiroot_pass_fails_closed(monkeypatch):
    source = runner.collect_full_wow_v1_2_product_trace()
    built = (
        runner.supplier_water_filter_adapter.
        build_supplier_water_filter_kernel_adapter_result_v01(
            source_report=source
        )
    )
    forged_outcome = replace(
        built.multiroot_outcome,
        outcome_status=runner.multiroot.STATUS_PASS,
        mixed_outcomes_visible=False,
        accepted_root_ids=(
            runner.supplier_water_filter_adapter.OWNER_ROOT_ID,
        ),
        non_accepted_root_ids=(),
    )
    forged = replace(built, multiroot_outcome=forged_outcome)
    monkeypatch.setattr(
        runner,
        "collect_full_wow_v1_2_product_trace",
        lambda: source,
    )
    monkeypatch.setattr(
        runner.supplier_water_filter_adapter,
        "build_supplier_water_filter_kernel_adapter_result_v01",
        lambda *, source_report: forged,
    )
    result = runner.collect_supplier_water_filter_portability_gauntlet_act_v01()
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert result.real_world_effects_count == -1


@pytest.mark.parametrize(
    ("root_ids", "classes", "expected"),
    (
        (("root:a", "root:b", "root:c"), ("ACCEPTED",) * 3, "PASS"),
        (("root:a", "root:b", "root:c", "root:d"), ("ACCEPTED",) * 4, "PASS"),
        (("root:a", "root:b"), ("ACCEPTED", "BLOCKED"), "MIXED"),
        (("root:a", "root:b", "root:c"), ("ACCEPTED", "ACCEPTED"), "INCOMPLETE"),
    ),
)
def test_g1d2_generic_multiroot_fixture_statuses_are_visible(
    root_ids, classes, expected
):
    outcome = runner._neutral_multiroot_outcome_v01(
        transaction_id=f"transaction:g1d2:{expected.lower()}:{len(root_ids)}",
        root_ids=root_ids,
        outcome_classes=classes,
    )
    validation = runner.multiroot.validate_multiroot_v01(outcome)
    assert outcome.outcome_status == expected
    assert validation.final_status == expected
    assert validation.authority_transfer_count == 0
    assert validation.permission_creation_count == 0
    assert validation.real_world_effects_count == 0


@pytest.mark.parametrize("attack", ("unknown", "duplicate", "reserved"))
def test_g1d2_invalid_root_geometry_fails_closed(attack):
    base = runner._neutral_multiroot_outcome_v01(
        transaction_id="transaction:g1d2:attacks",
        root_ids=("root:a", "root:b", "root:c"),
        outcome_classes=("ACCEPTED",) * 3,
    )
    if attack == "unknown":
        decision = runner._neutral_root_decision_v01(
            transaction_id=base.transaction_id,
            root_id="root:unknown",
            outcome_class="ACCEPTED",
        )
        attacked = replace(base, root_decisions=(decision, *base.root_decisions[1:]))
    elif attack == "duplicate":
        attacked = replace(base, expected_root_ids=("root:a", "root:a", "root:c"))
    else:
        attacked = replace(base, expected_root_ids=("root:superroot", "root:b", "root:c"))
    assert runner.multiroot.validate_multiroot_v01(attacked).final_status == "FAIL_CLOSED"


def test_g1d2_generic_fixture_matrix_passes_with_visible_mixed_and_incomplete():
    result = runner.collect_generic_multiroot_gauntlet_act_v01()
    assert result.state == runner.STATUS_PASS
    assert result.runtime_status == runner.STATUS_PASS
    assert result.root_authority_preserved
    assert result.real_world_effects_count == 0


@pytest.mark.parametrize(
    "needle",
    (
        "Adriatic Filters",
        "Balkan Pumps",
        "INV-2042",
        "SH-2042",
        "supplier_water_filter_artifact:",
        "manifest_hash",
        "source_card_hash",
        "causal_consumption_refs",
    ),
)
def test_g1d2_report_and_renderer_hide_supplier_adapter_details(report, needle):
    rendered = runner.render_living_gauntlet_v01(report)
    assert needle not in repr(report)
    assert needle not in rendered


def test_g1d2_report_counters_are_derived_and_zero_effect(report):
    assert frozenset(report["counters"]) == runner._COUNTER_FIELD_NAMES
    assert report["counters"]["generic_multiroot_execution_count"] == 1
    assert report["counters"]["supplier_water_filter_portability_execution_count"] == 1
    assert report["counters"]["real_world_effects_count"] == 0
    assert "provider_call_count" not in report["counters"]
    assert "network_call_count" not in report["counters"]
    assert "gemini_call_count" not in report["counters"]


def test_g1d2_two_reports_and_renders_are_deterministic() -> None:
    first = runner.collect_living_gauntlet_v01()
    second = runner.collect_living_gauntlet_v01()
    assert first == second
    assert runner.render_living_gauntlet_v01(first) == runner.render_living_gauntlet_v01(second)


@pytest.fixture(scope="module")
def g1e_base_rows(report):
    return tuple(dict(item) for item in report["active_act_results"][:12])


@pytest.fixture(scope="module")
def g1e_conformance_report(g1e_base_rows, report):
    current = conformance_runner.collect_kernel_conformance_v01(
        active_act_results=(
            *g1e_base_rows,
            dict(report["active_act_results"][13]),
            dict(report["active_act_results"][14]),
            dict(report["active_act_results"][15]),
        ),
        implementation_commit="abcdef0",
    )
    categories = current.category_results[:11]
    negatives = current.negative_test_results[:20]
    active_refs = current.active_gauntlet_refs[:13]
    provisional = conformance.KernelConformanceReportV01(
        report_id="0" * 64,
        conformance_version="v0.2",
        implementation_commit=current.implementation_commit,
        category_results=categories,
        domain_results=current.domain_results,
        negative_test_results=negatives,
        active_gauntlet_refs=active_refs,
        evidence_refs=current.evidence_refs,
        limitations=current.limitations,
        counters=conformance._derive_counters(
            categories,
            current.domain_results,
            negatives,
            active_refs,
            current.evidence_refs,
        ),
        final_status=conformance.STATUS_PASS,
    )
    return conformance._replace_report_id(provisional)


def test_g1e_runner_version_and_geometry_are_exact(report):
    assert runner._G2A_RUNNER_VERSION_V11 == "v1.1"
    assert runner.RUNNER_VERSION == "v1.3"
    assert report["runner_version"] == "v1.3"
    assert report["final_status"] == runner.STATUS_PASS
    assert report["validation_errors"] == ()
    assert report["counters"]["active_act_count"] == 16
    assert report["counters"]["active_act_pass_count"] == 16
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["planned_act_count"] == 0


def test_g1e_exact_thirteenth_act_is_closure(report):
    row = report["active_act_results"][12]
    assert row["act_id"] == "kernel_conformance_closure"
    assert row["state"] == runner.STATUS_PASS
    assert row["runtime_status"] == runner.STATUS_PASS
    assert row["executed"] is True
    assert row["root_authority_preserved"] is True
    assert row["no_real_connector_or_action"] is True
    assert row["real_world_effects_count"] == 0
    assert row["errors"] == ()


def test_g1e_exact_active_order(report):
    assert tuple(item["act_id"] for item in report["active_act_results"]) == (
        "airline_deterministic_transaction_runtime",
        "all_layers_invariant_super_smoke",
        "generic_integrity_replay",
        "root_signer_isolation_conformance",
        "semantic_work_contract",
        "domain_neutral_kernel_abi",
        "causal_consumption",
        "transition_registry",
        "root_decision_kernel",
        "effect_firewall",
        "generic_multiroot",
        "supplier_water_filter_portability",
        "kernel_conformance_closure",
        "action_packet_lifecycle",
        "drs_semantic_address_and_reuse_certificate",
        "execution_mode_router",
    )


def test_g1e_base_rows_are_exact_and_exclude_closure(g1e_base_rows):
    assert type(g1e_base_rows) is tuple
    assert len(g1e_base_rows) == 12
    assert tuple(item["act_id"] for item in g1e_base_rows) == runner._ACTIVE_ACT_IDS[:12]
    assert "kernel_conformance_closure" not in {
        item["act_id"] for item in g1e_base_rows
    }


def test_g1e_collect_living_passes_same_base_tuple_to_closure(
    report, monkeypatch: pytest.MonkeyPatch
):
    base = tuple(dict(item) for item in report["active_act_results"][:12])
    captured = []

    def closure(received):
        captured.append(received)
        return runner.LivingGauntletActResultV01(**report["active_act_results"][12])

    monkeypatch.setattr(runner, "collect_living_gauntlet_base_act_results_v01", lambda: base)
    monkeypatch.setattr(
        runner,
        "collect_action_packet_lifecycle_gauntlet_act_v01",
        lambda: runner.LivingGauntletActResultV01(
            **report["active_act_results"][13]
        ),
    )
    monkeypatch.setattr(runner, "collect_kernel_conformance_closure_gauntlet_act_v01", closure)
    rebuilt = runner.collect_living_gauntlet_v01()
    assert captured == [
        (
            *base,
            dict(report["active_act_results"][13]),
            dict(report["active_act_results"][14]),
            dict(report["active_act_results"][15]),
        ),
    ]
    assert captured[0][:12] == base
    assert rebuilt["final_status"] == runner.STATUS_PASS


def test_g1e_closure_does_not_recollect_supplier(
    g1e_base_rows, report, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        runner,
        "collect_supplier_water_filter_portability_gauntlet_act_v01",
        lambda: pytest.fail("closure recollected Supplier"),
    )
    monkeypatch.setattr(runner, "resolve_current_implementation_commit_v01", lambda: "abcdef0")
    row = runner.collect_kernel_conformance_closure_gauntlet_act_v01(
        (
            *g1e_base_rows,
            dict(report["active_act_results"][13]),
            dict(report["active_act_results"][14]),
            dict(report["active_act_results"][15]),
        )
    )
    assert row.state == runner.STATUS_PASS


def test_g1e_supplier_portability_executes_once_in_report(report):
    assert report["counters"]["supplier_water_filter_portability_execution_count"] == 1
    assert sum(
        item["act_id"] == "supplier_water_filter_portability"
        for item in report["active_act_results"]
    ) == 1


def test_g1e_closure_execution_counter_is_one(report):
    assert report["counters"]["kernel_conformance_closure_execution_count"] == 1


def test_g1e_conformance_runtime_report_passes(g1e_conformance_report):
    assert conformance.validate_kernel_conformance_report_v01(
        g1e_conformance_report
    ) == ()
    assert g1e_conformance_report.final_status == conformance.STATUS_PASS


def test_g1e_conformance_geometry_is_exact(g1e_conformance_report):
    assert len(g1e_conformance_report.category_results) == 11
    assert len(g1e_conformance_report.domain_results) == 2
    assert len(g1e_conformance_report.negative_test_results) == 20
    assert all(item.status == conformance.STATUS_PASS for item in g1e_conformance_report.category_results)
    assert all(item.status == conformance.STATUS_PASS for item in g1e_conformance_report.domain_results)
    assert all(item.status == conformance.STATUS_PASS for item in g1e_conformance_report.negative_test_results)


@pytest.mark.parametrize("domain_id", ("airline", "supplier_water_filter"))
def test_g1e_domain_result_passes(g1e_conformance_report, domain_id):
    result = next(
        item for item in g1e_conformance_report.domain_results if item.domain_id == domain_id
    )
    assert result.status == conformance.STATUS_PASS
    assert (
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
        result.real_world_effects_count,
    ) == (0, 0, 0, 0)


def test_g1e_supplier_multiroot_mixed_is_visible(g1e_conformance_report):
    supplier = g1e_conformance_report.domain_results[1]
    assert "supplier_multiroot_mixed_visible" in supplier.passed_check_ids
    assert "supplier_multiroot_pass" not in supplier.required_check_ids


@pytest.mark.parametrize(
    "probe_id", conformance._G2A_NEGATIVE_PROBE_IDS_V02
)
def test_g1e_each_negative_probe_passes(g1e_conformance_report, probe_id):
    result = next(
        item
        for item in g1e_conformance_report.negative_test_results
        if item.probe_id == probe_id
    )
    assert result.status == conformance.STATUS_PASS
    assert result.blocked is True


def test_g1e_release_manifest_state_is_exact():
    manifest = _json(COMPLETION_MANIFEST_PATH)
    assert manifest["runner_version"] == "v1.0"
    assert manifest["manifest_status"] == "ACTIVE_GATE1_G1E"
    assert len(manifest["active_runtime_acts"]) == 13
    assert len(manifest["evidence_only_references"]) == 1
    assert manifest["planned_gate1_acts"] == []


def test_g1e_release_seam_state_is_exact():
    index = _json(SEAM_INDEX_PATH)
    seams = index["seams"]
    assert index["index_status"] == "ACTIVE_GATE1_G1E"
    assert len(seams) == 24
    assert sum(item["status"] == runner.STATUS_ACTIVE for item in seams) == 21
    assert sum(item["status"] == runner.STATUS_REFERENCE_ONLY for item in seams) == 3
    assert sum(item["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for item in seams) == 0


def test_g1e_conformance_seam_is_active_and_non_authority():
    seam = next(
        item
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["seam_id"] == "kernel_conformance_report"
    )
    assert seam == {
        "authority_status": "NON_AUTHORITY_CONFORMANCE_EVIDENCE",
        "current_mode": "DETERMINISTIC_MACHINE_READABLE_GATE1_CONFORMANCE",
        "effect_access": "NONE",
        "gate1_target": "kernel_conformance_closure",
        "notes": seam["notes"],
        "seam_class": "RELEASE_CONFORMANCE",
        "seam_id": "kernel_conformance_report",
        "source_module": "demo.run_kernel_conformance_v01",
        "source_symbol": "collect_kernel_conformance_v01",
        "status": runner.STATUS_ACTIVE,
    }
    for phrase in (
        "exact ten-category, two-domain, and ten-negative-probe",
        "PASS derived from execution",
        "no stored synthetic PASS",
        "no production-certification claim",
        "final independent audit",
    ):
        assert phrase in seam["notes"]


def test_g1e_effect_firewall_remains_sole_effect_owner():
    owners = [
        item["seam_id"]
        for item in _json(SEAM_INDEX_PATH)["seams"]
        if item["status"] == runner.STATUS_ACTIVE
        and item["effect_access"] != "NONE"
    ]
    assert owners == ["effect_firewall"]


@pytest.mark.parametrize(
    "seam_id",
    (
        "generic_integrity_replay_adapter",
        "supplier_water_filter_abi_adapter",
        "kernel_conformance_report",
    ),
)
def test_g1e_non_effect_seams_remain_none(seam_id):
    seam = next(
        item for item in _json(SEAM_INDEX_PATH)["seams"] if item["seam_id"] == seam_id
    )
    assert seam["effect_access"] == "NONE"


def test_g1e_planned_claim_is_absent():
    claim_ids = {
        item["claim_id"]
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
    }
    assert "claim_gate1_planned_not_active" not in claim_ids


def test_g1e_claim_is_exact():
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == "claim_kernel_conformance_closure_execution"
    )
    assert claim["claim_class"] == "EXECUTED_CONFORMANCE"
    assert claim["act_ids"] == ["kernel_conformance_closure"]
    assert claim["evidence_ref"] == "hedgehog/kernel/conformance_v01.py"
    assert claim["focused_test_ref"] == "tests/test_kernel_conformance_v01_runner.py"
    assert claim["runtime_ref"] == (
        "demo.run_living_gauntlet_v01:"
        "collect_kernel_conformance_closure_gauntlet_act_v01"
    )
    assert claim["limitation_ref"] == "limitation_g1e_kernel_conformance_scope"
    assert "no stored synthetic PASS" in claim["statement"]


def test_g1e_limitation_keeps_audit_and_docs_pending():
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == "limitation_g1e_kernel_conformance_scope"
    )
    for phrase in (
        "deterministic current-repository conformance",
        "not arbitrary domains",
        "no fresh all-real run",
        "Supplier external Anchor",
        "Airline package regeneration",
        "Root Attestation",
        "production PKI",
        "production federation",
        "production connector",
        "full-repository certification",
        "Independent audit",
        "documentation closure remain pending",
    ):
        assert phrase in statement


@pytest.mark.parametrize(
    "non_claim",
    (
        "not production",
        "not production certification",
        "not a real connector",
        "not real payment",
        "not shipment release",
        "not Root Attestation",
        "not PKI",
        "not arbitrary Supplier integration",
        "not an arbitrary Airline adapter",
        "not Gate 1 final closure",
    ),
)
def test_g1e_required_non_claims_remain(non_claim):
    assert non_claim in _json(COMPLETION_MANIFEST_PATH)["non_claims"]


def test_g1e_airline_reference_remains_evidence_only(report):
    assert report["evidence_only_entries"] == [
        {
            "act_id": "airline_all_real_frozen_reference",
            "evidence_paths": [
                "docs/airline_all_real_evidence_showcase_checkpoint_v01.md",
                "docs/audit_reports/auditor_airline_all_real_evidence_showcase_v01.log",
            ],
            "executed": False,
            "state": runner.STATUS_EVIDENCE_ONLY,
        }
    ]


def _g1e_failed_closure(report_value, base_rows, monkeypatch):
    monkeypatch.setattr(runner, "resolve_current_implementation_commit_v01", lambda: "abcdef0")
    monkeypatch.setattr(runner, "collect_kernel_conformance_v01", lambda **_: report_value)
    return runner.collect_kernel_conformance_closure_gauntlet_act_v01(base_rows)


@pytest.mark.parametrize("failure_kind", ("category", "domain", "negative"))
def test_g1e_nested_conformance_failure_closes_act(
    g1e_conformance_report, g1e_base_rows, report, monkeypatch, failure_kind
):
    if failure_kind == "category":
        value = replace(
            g1e_conformance_report,
            category_results=g1e_conformance_report.category_results[:-1],
        )
    elif failure_kind == "domain":
        failed = replace(g1e_conformance_report.domain_results[0], status="FAIL_CLOSED")
        value = replace(
            g1e_conformance_report,
            domain_results=(failed, g1e_conformance_report.domain_results[1]),
        )
    else:
        failed = replace(g1e_conformance_report.negative_test_results[0], blocked=False)
        value = replace(
            g1e_conformance_report,
            negative_test_results=(
                failed,
                *g1e_conformance_report.negative_test_results[1:],
            ),
        )
    row = _g1e_failed_closure(
        value,
        (
            *g1e_base_rows,
            dict(report["active_act_results"][13]),
            dict(report["active_act_results"][14]),
            dict(report["active_act_results"][15]),
        ),
        monkeypatch,
    )
    assert row.state == runner.STATUS_FAIL_CLOSED
    assert row.errors == ("kernel_conformance_closure_failed",)
    assert row.real_world_effects_count == -1


def test_g1e_closure_failure_makes_living_fail_closed(
    report, monkeypatch: pytest.MonkeyPatch
):
    base = tuple(dict(item) for item in report["active_act_results"][:12])
    monkeypatch.setattr(runner, "collect_living_gauntlet_base_act_results_v01", lambda: base)
    monkeypatch.setattr(
        runner,
        "collect_kernel_conformance_closure_gauntlet_act_v01",
        lambda _: runner._failed_act_result(
            act_id="kernel_conformance_closure",
            reason="kernel_conformance_closure_failed",
        ),
    )
    failed = runner.collect_living_gauntlet_v01()
    assert failed["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "kernel_conformance_closure_failed" in failed["validation_errors"]


def test_g1e_public_counters_prove_zero_external_effects(report):
    assert frozenset(report["counters"]) == runner._COUNTER_FIELD_NAMES
    assert report["counters"]["real_world_effects_count"] == 0
    assert "provider_call_count" not in report["counters"]
    assert "network_call_count" not in report["counters"]
    assert "gemini_call_count" not in report["counters"]
    assert all(
        item["no_real_connector_or_action"] is True
        for item in report["active_act_results"]
    )


@pytest.mark.parametrize(
    "needle",
    (
        "manifest_hash",
        "adapter_id",
        "artifact_id",
        "supplier_b_balkan_pumps",
        "INV-2042",
        "SH-2042",
        "expected_reason_codes",
        "observed_reason_codes",
    ),
)
def test_g1e_renderer_exposes_no_conformance_internals(report, needle):
    assert needle.lower() not in runner.render_living_gauntlet_v01(report).lower()


def test_g1e_two_reports_and_renders_are_deterministic():
    first = runner.collect_living_gauntlet_v01()
    second = runner.collect_living_gauntlet_v01()
    assert first == second
    assert runner.render_living_gauntlet_v01(first) == runner.render_living_gauntlet_v01(second)


def test_g2a6_action_packet_lifecycle_act_executes_real_runtime_and_zero_effect(
    monkeypatch: pytest.MonkeyPatch,
):
    collected = []
    validations = []
    original_collect = (
        runner._action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01
    )
    original_validate = (
        runner._action_packet_lifecycle.validate_action_commit_packet_lifecycle_g2_a_report_v01
    )

    def collect_wrapper():
        report = original_collect()
        collected.append(report)
        return report

    def validate_wrapper(report):
        result = original_validate(report)
        validations.append((report, result))
        return result

    monkeypatch.setattr(
        runner._action_packet_lifecycle,
        "collect_action_commit_packet_lifecycle_g2_a_v01",
        collect_wrapper,
    )
    monkeypatch.setattr(
        runner._action_packet_lifecycle,
        "validate_action_commit_packet_lifecycle_g2_a_report_v01",
        validate_wrapper,
    )
    result = runner.collect_action_packet_lifecycle_gauntlet_act_v01()

    assert len(collected) == 1
    assert validations == [(collected[0], (True, ()))]
    report = collected[0]
    assert tuple(
        transition.transition_rule_id
        for transition in report.airline.replay_report.recorded_transitions
    ) == (
        "g2a_t01_activate_root_authorization",
        "g2a_t02_queue",
        "g2a_t03_pending",
        "g2a_t09_pending_block",
    )
    assert tuple(
        transition.transition_rule_id
        for transition in report.supplier.replay_report.recorded_transitions
    ) == (
        "g2a_t01_activate_root_authorization",
        "g2a_t02_queue",
        "g2a_t03_pending",
        "g2a_t09_pending_block",
    )
    assert {
        report.airline.invalidation_class,
        report.supplier.invalidation_class,
    } == {"DEPENDENCY_CHANGED", "ROOT_BOUND_KILL_SWITCH"}
    assert report.same_packet_family is True
    assert report.same_transition_registry_id is True
    assert report.same_authority_law is True
    assert report.airline.lifecycle_after == report.supplier.lifecycle_after == "BLOCKED"
    assert (
        report.airline.present_inspection.present_eligibility_status
        == report.supplier.present_inspection.present_eligibility_status
        == "NON_EXECUTABLE"
    )
    assert (
        report.provider_calls,
        report.network_calls,
        report.gemini_calls,
        report.adapter_calls,
        report.receipt_creations,
        report.real_world_effects_count,
    ) == (0, 0, 0, 0, 0, 0)
    assert result == runner.LivingGauntletActResultV01(
        act_id="action_packet_lifecycle",
        errors=(),
        executed=True,
        no_real_connector_or_action=True,
        real_world_effects_count=0,
        root_authority_preserved=True,
        runtime_status=runner.STATUS_PASS,
        source_module="demo.run_living_gauntlet_v01",
        source_symbol="collect_action_packet_lifecycle_gauntlet_act_v01",
        state=runner.STATUS_PASS,
    )


def test_g2a6_living_gauntlet_v11_preserves_gate1_acts_and_appends_lifecycle_act(
    report,
):
    manifest_bytes = COMPLETION_MANIFEST_PATH.read_bytes()
    seam_bytes = SEAM_INDEX_PATH.read_bytes()
    base = runner.collect_living_gauntlet_base_act_results_v01()
    active = report["active_act_results"]

    assert runner.RUNNER_VERSION == "v1.3"
    assert runner._GATE1_RELEASE_RUNNER_VERSION_V10 == "v1.0"
    assert runner._G2A_RUNNER_VERSION_V11 == "v1.1"
    assert tuple(item["act_id"] for item in base) == runner._GATE1_ACTIVE_ACT_IDS_V10[
        :12
    ]
    assert tuple(item["act_id"] for item in active[:13]) == (
        runner._GATE1_ACTIVE_ACT_IDS_V10
    )
    assert active[12]["act_id"] == "kernel_conformance_closure"
    assert active[13]["act_id"] == "action_packet_lifecycle"
    assert tuple(
        (item["source_module"], item["source_symbol"]) for item in active[:13]
    ) == tuple(
        runner._GATE1_ACTIVE_ACT_SOURCES_V10[act_id]
        for act_id in runner._GATE1_ACTIVE_ACT_IDS_V10
    )
    assert hashlib.sha256(manifest_bytes).hexdigest() == (
        "02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466"
    )
    assert hashlib.sha256(seam_bytes).hexdigest() == (
        "c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231"
    )
    assert _json(COMPLETION_MANIFEST_PATH)["runner_version"] == "v1.0"
    assert tuple(item["act_id"] for item in active[:14]) == (
        runner._G2A_ACTIVE_ACT_IDS_V11
    )
    assert report["counters"]["active_act_count"] == 16
    assert report["counters"]["active_act_pass_count"] == 16
    assert report["counters"]["active_act_fail_closed_count"] == 0
    assert report["counters"]["active_collector_execution_count"] == 16
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["evidence_only_executed_count"] == 0
    assert report["counters"]["planned_act_count"] == 0
    assert report["counters"]["planned_executed_count"] == 0
    assert report["counters"]["action_packet_lifecycle_execution_count"] == 1
    assert tuple(item["invariant_id"] for item in report["invariant_results"]) == (
        "release_indexes_valid",
        "all_active_acts_executed_once",
        "all_active_acts_pass",
        "root_authority_preserved",
        "real_world_effects_zero",
        "no_real_connector_or_action",
        "evidence_only_not_executed",
        "planned_acts_not_executed",
        "action_packet_lifecycle_act_pass",
        "drs_semantic_address_reuse_certificate_act_pass",
        "execution_mode_router_act_pass",
    )


def test_g2a6_living_gauntlet_lifecycle_failure_is_fail_closed_and_not_normalized(
    report,
    monkeypatch: pytest.MonkeyPatch,
):
    baseline = (
        runner._action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01()
    )
    old_rows = tuple(dict(item) for item in report["active_act_results"][:12])
    cases = (
        ("exception", lambda: (_ for _ in ()).throw(RuntimeError("controlled"))),
        ("malformed", lambda: object()),
        ("validator", lambda: baseline),
        ("nonzero", lambda: replace(baseline, provider_calls=1)),
    )
    for label, collector in cases:
        with monkeypatch.context() as scoped:
            scoped.setattr(
                runner,
                "collect_living_gauntlet_base_act_results_v01",
                lambda: old_rows,
            )
            scoped.setattr(
                runner._action_packet_lifecycle,
                "collect_action_commit_packet_lifecycle_g2_a_v01",
                collector,
            )
            if label == "validator":
                scoped.setattr(
                    runner._action_packet_lifecycle,
                    "validate_action_commit_packet_lifecycle_g2_a_report_v01",
                    lambda _: (False, ("g2a5_report_fail_closed",)),
                )
            act = runner.collect_action_packet_lifecycle_gauntlet_act_v01()
            full = runner.collect_living_gauntlet_v01()

        assert act.state == runner.STATUS_FAIL_CLOSED
        assert act.runtime_status == runner.STATUS_FAIL_CLOSED
        assert act.errors == ("action_packet_lifecycle_gauntlet_act_failed",)
        assert act.root_authority_preserved is False
        assert act.no_real_connector_or_action is False
        assert act.real_world_effects_count == -1
        assert full["final_status"] == runner.STATUS_FAIL_CLOSED
        assert full["counters"]["real_world_effects_count"] == -1
        assert tuple(full["active_act_results"][:12]) == old_rows


def test_g2b6_drs_semantic_address_reuse_certificate_act_is_real_bounded_and_zero_effect(
    monkeypatch: pytest.MonkeyPatch,
):
    collected = []
    validations = []
    original_collect = (
        runner._g2b.collect_drs_semantic_address_reuse_certificate_g2_b_v01
    )
    original_validate = (
        runner._g2b.validate_drs_semantic_address_reuse_certificate_g2_b_report_v01
    )

    def collect_wrapper():
        monkeypatch.setattr(
            runner._g2b,
            "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
            original_validate,
        )
        try:
            report = original_collect()
        finally:
            monkeypatch.setattr(
                runner._g2b,
                "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
                validate_wrapper,
            )
        collected.append(report)
        return report

    def validate_wrapper(report):
        result = original_validate(report)
        validations.append((report, result))
        return result

    monkeypatch.setattr(
        runner._g2b,
        "collect_drs_semantic_address_reuse_certificate_g2_b_v01",
        collect_wrapper,
    )
    monkeypatch.setattr(
        runner._g2b,
        "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
        validate_wrapper,
    )
    result = (
        runner.collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01()
    )

    assert len(collected) == 1
    assert validations == [(collected[0], (True, ()))]
    report = collected[0]
    counters = dict(report.operation_counters)
    assert report.domain_order == (
        "TRAVEL_POLICY_INFORMATION",
        "WAREHOUSE_MAINTENANCE_INFORMATION",
    )
    assert len(report.domain_results) == 2
    assert sum(
        len(item.negative_requests) for item in report.domain_results
    ) == 8
    assert counters == dict(runner._G2B_EXPECTED_OPERATION_COUNTERS_V01)
    assert all(value == 0 for _, value in report.closed_programme_counters)
    for domain in report.domain_results:
        answer = domain.answer_report
        context = domain.context_report
        descent = answer.memory_descent_result
        certificate = answer.reuse_certificate
        evidence = domain.writeback_evidence
        assert answer.selected_candidate_id is not None
        assert answer.root_shortcut_projection is not None
        assert certificate is not None
        assert descent is not None
        assert descent.executed_descent_class == "SUMMARY_ONLY"
        assert descent.bytes_opened == 0
        assert context.selected_candidate_id is None
        assert context.root_shortcut_projection is None
        assert context.reuse_certificate is None
        assert evidence["predecessor_preserved"] is True
        assert evidence["successor_readback_exact"] is True
        assert evidence["records_written"] == 1
        assert evidence["creates_authority"] is False
        assert evidence["creates_permission"] is False
        assert evidence["real_world_effects_count"] == 0
        assert certificate.creates_authority is False
        assert certificate.creates_permission is False
        assert certificate.creates_final_output is False
        assert certificate.creates_action_commit_packet is False
        assert certificate.creates_receipt is False
        assert certificate.creates_capability is False
        assert certificate.creates_effect_handle is False
        assert certificate.creates_effect is False
    assert result == runner.LivingGauntletActResultV01(
        act_id="drs_semantic_address_and_reuse_certificate",
        errors=(),
        executed=True,
        no_real_connector_or_action=True,
        real_world_effects_count=0,
        root_authority_preserved=True,
        runtime_status=runner.STATUS_PASS,
        source_module="demo.run_living_gauntlet_v01",
        source_symbol=(
            "collect_drs_semantic_address_and_reuse_certificate_"
            "gauntlet_act_v01"
        ),
        state=runner.STATUS_PASS,
    )


def test_g2b6_living_gauntlet_v12_preserves_v11_and_appends_g2b_act(
    report,
):
    manifest_bytes = COMPLETION_MANIFEST_PATH.read_bytes()
    seam_bytes = SEAM_INDEX_PATH.read_bytes()
    active = report["active_act_results"]

    assert runner.RUNNER_VERSION == "v1.3"
    assert runner._GATE1_RELEASE_RUNNER_VERSION_V10 == "v1.0"
    assert runner._G2A_RUNNER_VERSION_V11 == "v1.1"
    assert runner._G2A_ACTIVE_ACT_IDS_V11 == (
        *runner._GATE1_ACTIVE_ACT_IDS_V10,
        "action_packet_lifecycle",
    )
    assert runner._G2B_RUNNER_VERSION_V12 == "v1.2"
    assert runner._G2B_ACTIVE_ACT_IDS_V12 == (
        *runner._G2A_ACTIVE_ACT_IDS_V11,
        "drs_semantic_address_and_reuse_certificate",
    )
    assert tuple(item["act_id"] for item in active) == runner._ACTIVE_ACT_IDS
    assert active[12]["act_id"] == "kernel_conformance_closure"
    assert active[13]["act_id"] == "action_packet_lifecycle"
    assert active[14]["act_id"] == (
        "drs_semantic_address_and_reuse_certificate"
    )
    assert tuple(
        (item["source_module"], item["source_symbol"]) for item in active[:13]
    ) == tuple(
        runner._GATE1_ACTIVE_ACT_SOURCES_V10[act_id]
        for act_id in runner._GATE1_ACTIVE_ACT_IDS_V10
    )
    assert (
        active[14]["source_module"],
        active[14]["source_symbol"],
    ) == (
        "demo.run_living_gauntlet_v01",
        (
            "collect_drs_semantic_address_and_reuse_certificate_"
            "gauntlet_act_v01"
        ),
    )
    assert hashlib.sha256(manifest_bytes).hexdigest() == (
        "02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466"
    )
    assert hashlib.sha256(seam_bytes).hexdigest() == (
        "c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231"
    )
    assert report["counters"]["active_act_count"] == 16
    assert report["counters"]["active_act_pass_count"] == 16
    assert report["counters"][
        "drs_semantic_address_reuse_certificate_execution_count"
    ] == 1


def test_g2b6_living_gauntlet_g2b_failure_is_fail_closed_and_unknown_effect(
    report,
    monkeypatch: pytest.MonkeyPatch,
):
    baseline = (
        runner._g2b.collect_drs_semantic_address_reuse_certificate_g2_b_v01()
    )
    counters = tuple(
        (name, 1 if name == "provider_calls" else value)
        for name, value in baseline.operation_counters
    )
    nonzero = runner._g2b._reidentify_report_v01(
        replace(baseline, operation_counters=counters)
    )
    base_rows = tuple(dict(item) for item in report["active_act_results"][:12])
    closure = runner.LivingGauntletActResultV01(
        **report["active_act_results"][12]
    )
    lifecycle = runner.LivingGauntletActResultV01(
        **report["active_act_results"][13]
    )
    cases = (
        (
            "collector",
            lambda: (_ for _ in ()).throw(RuntimeError("controlled")),
            None,
        ),
        ("validator", lambda: baseline, (False, ("controlled",))),
        ("nonzero", lambda: nonzero, None),
    )
    for label, collector, validation_result in cases:
        with monkeypatch.context() as scoped:
            scoped.setattr(
                runner._g2b,
                "collect_drs_semantic_address_reuse_certificate_g2_b_v01",
                collector,
            )
            if validation_result is not None:
                scoped.setattr(
                    runner._g2b,
                    (
                        "validate_drs_semantic_address_reuse_certificate_"
                        "g2_b_report_v01"
                    ),
                    lambda _: validation_result,
                )
            scoped.setattr(
                runner,
                "collect_living_gauntlet_base_act_results_v01",
                lambda: base_rows,
            )
            scoped.setattr(
                runner,
                "collect_action_packet_lifecycle_gauntlet_act_v01",
                lambda: lifecycle,
            )
            scoped.setattr(
                runner,
                "collect_kernel_conformance_closure_gauntlet_act_v01",
                lambda _: closure,
            )
            act = (
                runner.collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01()
            )
            full = runner.collect_living_gauntlet_v01()

        assert act.act_id == "drs_semantic_address_and_reuse_certificate"
        assert act.errors == (
            "drs_semantic_address_reuse_certificate_gauntlet_act_failed",
        )
        assert act.executed is True
        assert act.no_real_connector_or_action is False
        assert act.real_world_effects_count == -1
        assert act.root_authority_preserved is False
        assert act.runtime_status == runner.STATUS_FAIL_CLOSED
        assert act.state == runner.STATUS_FAIL_CLOSED
        assert "controlled" not in repr(act)
        assert full["final_status"] == runner.STATUS_FAIL_CLOSED, label
        assert full["counters"]["real_world_effects_count"] == -1, label


def test_c6_living_v13_appends_exact_execution_mode_router_act(report):
    active = report["active_act_results"]
    assert runner.RUNNER_VERSION == "v1.3"
    assert runner._G2B_RUNNER_VERSION_V12 == "v1.2"
    assert runner._ACTIVE_ACT_IDS == (
        *runner._G2B_ACTIVE_ACT_IDS_V12,
        "execution_mode_router",
    )
    assert tuple(item["act_id"] for item in active) == runner._ACTIVE_ACT_IDS
    assert tuple(item["act_id"] for item in active[:-1]) == (
        runner._G2B_ACTIVE_ACT_IDS_V12
    )
    assert active[-1] == {
        "act_id": "execution_mode_router",
        "errors": (),
        "executed": True,
        "no_real_connector_or_action": True,
        "real_world_effects_count": 0,
        "root_authority_preserved": True,
        "runtime_status": runner.STATUS_PASS,
        "source_module": "demo.run_execution_mode_router_g2_c_v01",
        "source_symbol": "collect_execution_mode_router_g2_c_v01",
        "state": runner.STATUS_PASS,
    }
    assert report["counters"]["active_act_count"] == 16
    assert report["counters"]["active_act_pass_count"] == 16
    assert report["counters"]["active_act_fail_closed_count"] == 0
    assert report["counters"]["active_collector_execution_count"] == 16
    assert report["counters"]["execution_mode_router_execution_count"] == 1
    assert report["counters"]["action_packet_lifecycle_execution_count"] == 1
    assert report["counters"][
        "drs_semantic_address_reuse_certificate_execution_count"
    ] == 1
    assert report["counters"]["real_world_effects_count"] == 0
    assert report["invariant_results"][-1] == {
        "invariant_id": "execution_mode_router_act_pass",
        "state": runner.STATUS_PASS,
    }


def test_c6_execution_mode_router_act_consumes_validated_c5_proof():
    result = runner.collect_execution_mode_router_gauntlet_act_v01()
    report = runner._g2c.collect_execution_mode_router_g2_c_v01()
    assert runner._g2c.validate_execution_mode_router_g2_c_report_v01(report) == ()
    assert runner._execution_mode_router_report_passes_living_act_v01(report) is True
    assert report.report_version == "v0.1"
    assert report.profile_id == "execution_mode_router_g2c_two_domain_proof_v01"
    assert report.domain_order == runner._G2C_EXPECTED_DOMAIN_ORDER_V13
    assert report.case_order == runner._G2C_EXPECTED_CASE_ORDER_V13
    assert len(report.case_results) == 10
    assert {item.root_outcome for item in report.case_results} == {
        "ACCEPT", "NARROW", "REJECT", "BLOCKED", "NEEDS_USER"
    }
    assert all(item.operation_steps == runner._g2c.OPERATION_STEPS for item in report.case_results)
    assert all(len(item.root_support_ids) == len(set(item.root_support_ids)) == 6 for item in report.case_results)
    assert all(
        report.case_results[index].transaction_id
        == report.case_results[index].temporal_query_id
        for index in (1, 2, 3)
    )
    assert result == runner.LivingGauntletActResultV01(
        act_id="execution_mode_router",
        errors=(),
        executed=True,
        no_real_connector_or_action=True,
        real_world_effects_count=0,
        root_authority_preserved=True,
        runtime_status=runner.STATUS_PASS,
        source_module="demo.run_execution_mode_router_g2_c_v01",
        source_symbol="collect_execution_mode_router_g2_c_v01",
        state=runner.STATUS_PASS,
    )


@pytest.mark.parametrize(
    "mutation",
    (
        lambda report: replace(
            report,
            case_order=tuple(reversed(report.case_order)),
        ),
        lambda report: replace(
            report,
            case_results=(
                replace(report.case_results[0], root_outcome="REJECT"),
                *report.case_results[1:],
            ),
        ),
        lambda report: replace(
            report,
            case_results=(
                replace(
                    report.case_results[0],
                    post_root_transition_reason="g2c_transition_reject_recorded",
                ),
                *report.case_results[1:],
            ),
        ),
        lambda report: replace(
            report,
            case_results=(
                replace(
                    report.case_results[0],
                    operation_steps=tuple(
                        reversed(report.case_results[0].operation_steps)
                    ),
                ),
                *report.case_results[1:],
            ),
        ),
        lambda report: replace(report, provider_calls=1),
    ),
)
def test_c6_invalid_c5_report_fails_living_act_closed(
    mutation,
    monkeypatch: pytest.MonkeyPatch,
):
    baseline = runner._g2c.collect_execution_mode_router_g2_c_v01()
    forged = mutation(baseline)
    assert runner._g2c.validate_execution_mode_router_g2_c_report_v01(forged)
    monkeypatch.setattr(
        runner._g2c,
        "collect_execution_mode_router_g2_c_v01",
        lambda: forged,
    )
    result = runner.collect_execution_mode_router_gauntlet_act_v01()
    assert result.act_id == "execution_mode_router"
    assert result.errors == ("execution_mode_router_gauntlet_act_failed",)
    assert result.executed is True
    assert result.no_real_connector_or_action is False
    assert result.real_world_effects_count == -1
    assert result.root_authority_preserved is False
    assert result.runtime_status == runner.STATUS_FAIL_CLOSED
    assert result.state == runner.STATUS_FAIL_CLOSED
    assert "forged" not in repr(result)


def test_c6_living_report_and_render_are_repeated_and_zero_operation():
    first = runner.collect_living_gauntlet_v01()
    second = runner.collect_living_gauntlet_v01()
    assert first == second
    assert runner.render_living_gauntlet_v01(first) == (
        runner.render_living_gauntlet_v01(second)
    )
    assert first["runner_version"] == "v1.3"
    assert first["final_status"] == runner.STATUS_PASS
    assert first["validation_errors"] == ()
    assert first["counters"]["real_world_effects_count"] == 0
    assert all(
        item["real_world_effects_count"] == 0
        and item["root_authority_preserved"] is True
        and item["no_real_connector_or_action"] is True
        for item in first["active_act_results"]
    )
