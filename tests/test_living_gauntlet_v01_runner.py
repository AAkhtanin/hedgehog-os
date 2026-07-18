from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import ast
import importlib
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from demo import run_living_gauntlet_v01 as runner
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
    }
    assert exact_once_report["counters"]["active_collector_execution_count"] == 10


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
    assert "planned_act_status_invalid:generic_multiroot" in failed[
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
    assert statuses.count(runner.STATUS_ACTIVE) == 10
    assert statuses.count(runner.STATUS_EVIDENCE_ONLY) == 1
    assert statuses.count(runner.STATUS_PLANNED_NOT_ACTIVE) == 3


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


def test_successful_report_has_seven_active_acts(report: dict[str, Any]) -> None:
    assert len(report["active_act_results"]) == 10
    assert report["counters"]["active_act_count"] == 10
    assert report["counters"]["active_act_pass_count"] == 10
    assert report["counters"]["active_act_fail_closed_count"] == 0


def test_successful_report_has_six_planned_acts(report: dict[str, Any]) -> None:
    assert len(report["planned_entries"]) == 3
    assert report["counters"]["planned_act_count"] == 3
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

    assert len(seams) == 24
    assert sum(item["status"] == runner.STATUS_ACTIVE for item in seams) == 17
    assert sum(item["status"] == runner.STATUS_REFERENCE_ONLY for item in seams) == 3
    assert sum(
        item["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for item in seams
    ) == 4
    effect_owners = [
        item
        for item in seams
        if item["status"] == runner.STATUS_ACTIVE
        and item["effect_access"] != "NONE"
    ]
    assert [item["seam_id"] for item in effect_owners] == ["effect_firewall"]


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

    assert len(claim["act_ids"]) == 3
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
        "G1-A1 itself does not exercise signer isolation",
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


def test_runner_version_is_v05(report: dict[str, Any]) -> None:
    assert runner.RUNNER_VERSION == "v0.7"
    assert report["runner_version"] == "v0.7"


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
    assert "import requests" not in source
    assert "socket" not in source


def test_manifest_status_and_counts_are_exact() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)

    assert manifest["manifest_status"] == "ACTIVE_GATE1_G1C2"
    assert len(manifest["active_runtime_acts"]) == 10
    assert len(manifest["evidence_only_references"]) == 1
    assert len(manifest["planned_gate1_acts"]) == 3


def test_seam_index_status_is_exact() -> None:
    assert _json(SEAM_INDEX_PATH)["index_status"] == "ACTIVE_GATE1_G1C2"


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


def test_all_nine_active_act_ids_are_exact(report: dict[str, Any]) -> None:
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
    )
    assert report["counters"]["active_collector_execution_count"] == 10


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


def test_planned_claim_has_exact_remaining_four_ids() -> None:
    claim = next(
        record
        for record in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if record["claim_id"] == "claim_gate1_planned_not_active"
    )
    assert claim["act_ids"] == [
        "generic_multiroot",
        "supplier_water_filter_portability",
        "kernel_conformance_closure",
    ]


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
        "not Gate 1 closure",
    ):
        assert required in non_claims


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


def test_planned_claim_excludes_semantic_work_and_has_eight_acts() -> None:
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == "claim_gate1_planned_not_active"
    )
    assert "semantic_work_contract" not in claim["act_ids"]
    assert claim["act_ids"] == list(runner._PLANNED_ACT_IDS)


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
    assert report["runner_version"] == "v0.7"
    assert report["final_status"] == runner.STATUS_PASS
    assert report["counters"]["active_act_count"] == 10
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["planned_act_count"] == 3
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


def test_g1b2_planned_set_is_exact() -> None:
    manifest = _json(COMPLETION_MANIFEST_PATH)
    planned = tuple(item["act_id"] for item in manifest["planned_gate1_acts"])
    claim = next(
        item
        for item in manifest["public_claims"]
        if item["claim_id"] == "claim_gate1_planned_not_active"
    )
    assert planned == runner._PLANNED_ACT_IDS
    assert claim["act_ids"] == list(runner._PLANNED_ACT_IDS)
    assert "domain_neutral_kernel_abi" not in planned
    assert "causal_consumption" not in planned


@pytest.mark.parametrize(
    "phrase",
    (
        "neutral in-memory conformance fixtures",
        "no Airline or Supplier adapter",
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


def test_g1b2_seam_geometry_is_exact() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    assert len(seams) == 24
    assert sum(item["status"] == runner.STATUS_ACTIVE for item in seams) == 17
    assert sum(item["status"] == runner.STATUS_REFERENCE_ONLY for item in seams) == 3
    assert sum(
        item["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for item in seams
    ) == 4
    assert sum(
        item["effect_access"] != "NONE"
        for item in seams
        if item["status"] == runner.STATUS_ACTIVE
    ) == 1


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
    assert report["runner_version"] == "v0.7"
    assert report["final_status"] == runner.STATUS_PASS
    assert report["counters"]["active_act_count"] == 10
    assert report["counters"]["active_act_pass_count"] == 10
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["planned_act_count"] == 3
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
    assert "against the active Kernel ABI" in seam["notes"]
    assert "domain adapter itself remains unimplemented" in seam["notes"]
    assert "no ABI is implemented" not in seam["notes"]


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


def test_release_coherence_hardening_preserves_public_geometry(
    report: dict[str, Any],
) -> None:
    assert report["runner_version"] == "v0.7"
    assert report["final_status"] == runner.STATUS_PASS
    assert report["counters"]["active_act_count"] == 10
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["planned_act_count"] == 3
    assert report["counters"]["real_world_effects_count"] == 0


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


def test_g1c1_planned_claim_exact_four_ids():
    claim = next(item for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"] if item["claim_id"] == "claim_gate1_planned_not_active")
    assert claim["act_ids"] == ["generic_multiroot", "supplier_water_filter_portability", "kernel_conformance_closure"]


@pytest.mark.parametrize("limitation_id,phrases", (
    ("limitation_g1c1_in_memory_transition_and_root_decision_only", ("does not mutate artifacts or execute transitions", "RootDecisionResult only", "no permission", "no effect", "separately active in G1-C2")),
    ("limitation_gate1_not_implemented", ("Generic MultiRoot", "portability adapters", "Kernel Conformance closure")),
    ("limitation_g1b1_in_memory_contract_conformance_only", ("separately active in G1-C1", "separately active in G1-C2")),
    ("limitation_g1b2_in_memory_abi_and_counterfactual_only", ("separately active in G1-C1", "separately active in G1-C2", "Generic MultiRoot")),
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


def test_g1c1_seam_geometry_and_effect_firewall_boundary():
    seams = _json(SEAM_INDEX_PATH)["seams"]
    assert len(seams) == 24
    assert sum(item["status"] == runner.STATUS_ACTIVE for item in seams) == 17
    assert sum(item["status"] == runner.STATUS_REFERENCE_ONLY for item in seams) == 3
    assert sum(item["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for item in seams) == 4
    active = [item for item in seams if item["status"] == runner.STATUS_ACTIVE]
    assert sum(item["effect_access"] != "NONE" for item in active) == 1
    firewall = next(item for item in seams if item["seam_id"] == "effect_firewall")
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
    assert report["runner_version"] == "v0.7"
    assert report["final_status"] == runner.STATUS_PASS
    assert report["validation_errors"] == ()
    assert report["counters"]["active_act_count"] == 10
    assert report["counters"]["active_act_pass_count"] == 10
    assert report["counters"]["active_act_fail_closed_count"] == 0
    assert report["counters"]["evidence_only_entry_count"] == 1
    assert report["counters"]["planned_act_count"] == 3
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


def test_g1c2_planned_claim_has_exact_three_remaining_acts() -> None:
    claim = next(
        item
        for item in _json(COMPLETION_MANIFEST_PATH)["public_claims"]
        if item["claim_id"] == "claim_gate1_planned_not_active"
    )
    assert claim["act_ids"] == [
        "generic_multiroot",
        "supplier_water_filter_portability",
        "kernel_conformance_closure",
    ]


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
        ("limitation_g1c2_in_memory_mock_effect_only", "Generic MultiRoot"),
        ("limitation_g1c2_in_memory_mock_effect_only", "domain adapters remain unimplemented"),
        ("limitation_g1c2_in_memory_mock_effect_only", "not production security certification"),
        ("limitation_g1b1_in_memory_contract_conformance_only", "active in G1-C2"),
        ("limitation_g1b2_in_memory_abi_and_counterfactual_only", "active in G1-C2"),
        ("limitation_g1c1_in_memory_transition_and_root_decision_only", "active in G1-C2"),
    ),
)
def test_g1c2_limitations_are_explicit(limitation_id: str, phrase: str) -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == limitation_id
    )
    assert phrase in statement


def test_gate1_limitation_no_longer_describes_firewall_as_absent() -> None:
    statement = next(
        item["statement"]
        for item in _json(COMPLETION_MANIFEST_PATH)["limitations"]
        if item["limitation_id"] == "limitation_gate1_not_implemented"
    )
    assert "Effect Firewall" not in statement
    assert "Generic MultiRoot" in statement


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


def test_g1c2_seam_geometry_and_exclusive_owner_are_exact() -> None:
    seams = _json(SEAM_INDEX_PATH)["seams"]
    assert len(seams) == 24
    assert sum(item["status"] == runner.STATUS_ACTIVE for item in seams) == 17
    assert sum(item["status"] == runner.STATUS_REFERENCE_ONLY for item in seams) == 3
    assert sum(item["status"] == runner.STATUS_PLANNED_NOT_ACTIVE for item in seams) == 4
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
    mutated["counters"]["active_act_pass_count"] = 10
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
