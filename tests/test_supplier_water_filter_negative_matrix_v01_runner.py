from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest

from demo import run_supplier_water_filter_negative_matrix_v01 as runner
from demo import run_two_domain_supplier_water_filter_program_v01 as s1
from demo.run_full_wow_v1_2_product_trace import collect_full_wow_v1_2_product_trace
from hedgehog import action_commit_packet_v02 as packet
from hedgehog.domains.supplier_water_filter import kernel_adapter_v01 as kernel
from hedgehog.domains.supplier_water_filter import live_evidence_adapter_v01 as safe
from hedgehog.domains.supplier_water_filter import (
    sealed_evidence_package_adapter_v01 as sealed_adapter,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


REPOSITORY_ROOT = Path(__file__).absolute().parent.parent
ACCEPTED_REPORT = REPOSITORY_ROOT / runner.ACCEPTED_S1_REPORT_REF
CANONICAL_S2_OUTPUT = REPOSITORY_ROOT / runner.CANONICAL_S2_OUTPUT_REF


def _canonical_output_state(path: Path) -> tuple[object, ...]:
    try:
        entry = path.lstat()
    except FileNotFoundError:
        return ("ABSENT",)
    if (
        path.is_symlink()
        or not stat.S_ISREG(entry.st_mode)
        or stat.S_IMODE(entry.st_mode) != 0o400
    ):
        raise AssertionError("unsafe canonical output state")
    try:
        content = path.read_bytes()
        runner._strict_json(content)
    except (OSError, ValueError):
        raise AssertionError("malformed canonical output state") from None
    final = path.lstat()
    if (final.st_dev, final.st_ino, final.st_mode, final.st_size) != (
        entry.st_dev,
        entry.st_ino,
        entry.st_mode,
        entry.st_size,
    ):
        raise AssertionError("unstable canonical output state")
    return (
        "PRESENT",
        hashlib.sha256(content).hexdigest(),
        len(content),
        stat.S_IMODE(entry.st_mode),
        content,
        (content.endswith(b"\n"), content.endswith(b"\n\n")),
    )


CANONICAL_S2_OUTPUT_BASELINE = _canonical_output_state(CANONICAL_S2_OUTPUT)

EXPECTED_PACKAGE_ROW_SPECS = (
    ("S-N1", "initial_business_blockers_root_not_ready", "deterministic_initial_business_evidence", "PASS", "NOT_READY", "NOT_READY", "BLOCKED_PENDING_CORRECTION", "ABSENT", "NOT_ENTERED", "ABSENT"),
    ("S-N2", "unsafe_live_evidence_fail_closed", "live_bound_negative_safe_projection", "FAIL_CLOSED", "NOT_READY", "NO_ACCEPTED_NEW_ROOT_FINAL", "BLOCKED_PENDING_CORRECTION", "ABSENT", "NOT_ENTERED", "ABSENT"),
    ("S-C1", "corrected_evidence_validation_rerun", "deterministic_corrected_evidence", "PASS", "MIXED", "SUPPLIER_A_SCOPED_REVIEW_READY", "SUPPLIER_A_SCOPED_REVIEW_READY", "ABSENT", "NOT_ENTERED", "ABSENT"),
    ("S-P1", "supplier_a_scoped_human_approval", "deterministic_owner_approval", "PASS", "MIXED", "SUPPLIER_A_SCOPED_REVIEW_READY", "APPROVED_SCOPE_ONLY", "ROOT_CREATED_SCOPED", "NOT_ENTERED", "ABSENT"),
    ("S-P2", "supplier_a_mock_bank_happy_path", "live_bound_deterministic_corridor", "PASS", "MIXED", "SUPPLIER_A_SCOPED_REVIEW_READY", "PASS", "VALID_SCOPED", "PASS", "EVIDENCE_ONLY"),
    ("S-F1", "no_human_approval_blocks_action", "deterministic_policy_probe", "FAIL_CLOSED", "NOT_READY", "NO_ACTION_APPROVAL", "NOT_EXECUTED", "REJECTED", "NOT_ENTERED", "ABSENT"),
    ("S-F2", "packet_and_corridor_mutation_matrix", "deterministic_packet_corridor_mutation", "FAIL_CLOSED", "MIXED", "NO_WIDENED_ROOT_DECISION", "UNCHANGED", "REJECTED", "REJECTED", "ABSENT"),
    ("S-F3", "receipt_attack_matrix", "deterministic_receipt_attack", "FAIL_CLOSED", "MIXED", "NO_NEW_PERMISSION", "UNCHANGED", "UNCHANGED", "NO_NEW_EXECUTION", "ATTACK_REJECTED"),
    ("S-M1", "integrated_mixed_business_outcome", "deterministic_integrated_outcome", "PASS", "MIXED", "HELD", "PASS", "VALID_SCOPED", "PASS", "EVIDENCE_ONLY"),
)

EXPECTED_PROBE_ATTRIBUTION = (
    ("s_n2_raw_prompt_inclusion", "validate_supplier_water_filter_safe_execution_projection_v01", "SupplierWaterFilterSafeExecutionProjectionV01", ("raw_prompt_included",), ("supplier_water_filter_safe_execution_raw_material_forbidden", "supplier_water_filter_safe_execution_identity_mismatch")),
    ("s_n2_failed_secret_scan", "validate_supplier_water_filter_safe_execution_projection_v01", "SupplierWaterFilterSafeExecutionProjectionV01", ("secret_scan_passed",), ("supplier_water_filter_safe_execution_secret_scan_required", "supplier_water_filter_safe_execution_identity_mismatch")),
    ("s_n2_nonzero_effect", "validate_supplier_water_filter_safe_execution_projection_v01", "SupplierWaterFilterSafeExecutionProjectionV01", ("real_world_effects_count",), ("supplier_water_filter_safe_execution_effect_forbidden", "supplier_water_filter_safe_execution_status_mismatch", "supplier_water_filter_safe_execution_identity_mismatch")),
    ("s_n2_invalid_call_geometry", "validate_supplier_water_filter_safe_execution_projection_v01", "SupplierWaterFilterSafeExecutionProjectionV01", ("provider_call_count",), ("supplier_water_filter_safe_execution_call_geometry_invalid", "supplier_water_filter_safe_execution_identity_mismatch")),
    ("s_f1_missing_human_approval", "validate_action_commit_packet_v02", "ActionCommitPacketV02", ("human_approval_ref",), ("missing_human_approval_ref",)),
    ("s_f2_packet_supplier_b_scope_widening", "validate_action_commit_packet_v02", "ActionCommitPacketV02", ("scope.allowed_subjects",), ("supplier_b_scope_forbidden",)),
    ("s_f2_packet_shipment_scope_widening", "validate_action_commit_packet_v02", "ActionCommitPacketV02", ("scope.allowed_actions",), ("shipment_release_forbidden",)),
    ("s_f2_corridor_supplier_b_scope_widening", "validate_corridor_step_against_packet_v01", "CorridorStepV01", ("allowed_subjects",), ("child_allowed_not_subset_of_parent", "child_scope_not_subset_of_parent")),
    ("s_f2_corridor_shipment_scope_widening", "validate_corridor_step_against_packet_v01", "CorridorStepV01", ("allowed_actions",), ("child_allowed_not_subset_of_parent", "child_scope_not_subset_of_parent")),
    ("s_f3_receipt_future_permission", "validate_mock_receipt_evidence_v01", "MockReceiptEvidenceV01", ("creates_future_permission",), ("receipt_cannot_create_future_permission",)),
    ("s_f3_receipt_supplier_b_authority", "validate_mock_receipt_evidence_v01", "MockReceiptEvidenceV01", ("authorizes_supplier_b",), ("receipt_cannot_authorize_supplier_b",)),
    ("s_f3_receipt_final_output", "validate_mock_receipt_evidence_v01", "MockReceiptEvidenceV01", ("creates_final_output",), ("no_expansion_after_root",)),
    ("s_f3_receipt_shipment_release", "validate_mock_receipt_evidence_v01", "MockReceiptEvidenceV01", ("releases_shipment",), ("receipt_cannot_release_shipment",)),
    ("s_f3_registry_future_permission", "validate_action_commit_packet_registry_v02", "ActionCommitPacketRegistryV02", ("creates_permission",), ("registry_is_not_permission", "registry_is_not_authority")),
    ("s_f3_registry_shipment_release", "validate_action_commit_packet_registry_v02", "ActionCommitPacketRegistryV02", ("releases_shipment",), ("registry_cannot_release_shipment",)),
)


def _prepare_repository(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "repository"
    source = root / runner.ACCEPTED_S1_REPORT_REF
    output = root / runner.CANONICAL_S2_OUTPUT_REF
    source.parent.mkdir(parents=True)
    source.write_bytes(ACCEPTED_REPORT.read_bytes())
    source.chmod(0o400)
    return root, source, output


@pytest.fixture
def accepted_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    return _prepare_repository(tmp_path)


@pytest.fixture
def source(accepted_paths):
    _, source_path, _ = accepted_paths
    return runner.load_accepted_supplier_s1_source_v01(str(source_path))


@pytest.fixture
def result(source):
    return runner.build_supplier_water_filter_negative_matrix_v01(source)


@pytest.fixture(scope="module")
def product_trace():
    value = collect_full_wow_v1_2_product_trace()
    assert value["final_status"] == "PASS"
    assert value["validation_errors"] == ()
    return value


@pytest.fixture(scope="module")
def kernel_result(product_trace):
    value = kernel.build_supplier_water_filter_kernel_adapter_result_v01(
        source_report=product_trace
    )
    assert kernel.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=product_trace,
        result=value,
    ) == ()
    return value


def _negative_rows(result):
    return tuple(
        row
        for row in result.scenario_rows
        if type(row) is runner.SupplierS2NegativeScenarioResultV01
    )


def _row(result, scenario_id):
    return next(item for item in result.scenario_rows if item.scenario_id == scenario_id)


def _rehash_result(result):
    return replace(
        result,
        result_id=runner._identity(
            runner._RESULT_DOMAIN,
            runner._result_plain(result, zero_id=True),
        ),
    )


def _replace_matrix_row(result, index, value):
    rows = list(result.scenario_rows)
    rows[index] = value
    return replace(result, scenario_rows=tuple(rows))


def _cli(root: Path, source: Path, output: Path, *extra: str):
    command = (
        sys.executable,
        "-m",
        "demo.run_supplier_water_filter_negative_matrix_v01",
        "--repository-root",
        str(root),
        "--accepted-s1-report",
        str(source),
        "--output",
        str(output),
        *extra,
    )
    environment = dict(os.environ)
    environment.update(
        {
            "PYTHONBREAKPOINT": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": ".",
        }
    )
    return subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_public_constants_are_exact():
    assert runner.GATE_ID == (
        "two_domain_all_real_sealed_evidence_program_v01_s2_supplier_negative_matrix"
    )
    assert runner.ACCEPTED_S1_REPORT_SHA256 == (
        "293a6ed1f0b943557e2bd33f2ac52f49610e8924574d2784af328d964ba1d666"
    )
    assert runner.ACCEPTED_S1_RESULT_ID == (
        "31059f0fa2566cc9040f813680a3c827f41c49f07db6b5885e040a0ed48b8bb5"
    )
    assert runner.ACCEPTED_S1_EXECUTION_HEAD == (
        "e1fe7bfc44fe482814b1957840b6d8c434cad5c6"
    )
    assert runner.ACCEPTED_S1_SAFE_EXECUTION_ID == (
        "26a6d430fffded9119c5743796b2cbfccd87f67f6eee57e617a094bc9c41779c"
    )


def test_result_types_are_frozen_and_slotted(source, result):
    probe = _negative_rows(result)[0].probes[0]
    for item in (
        probe,
        _negative_rows(result)[0],
        result.package_adapter_scenario_rows[0],
        result,
    ):
        assert item.__dataclass_params__.frozen
        assert "__slots__" in vars(type(item))
        with pytest.raises((FrozenInstanceError, AttributeError)):
            item.result_id = "changed"
    assert type(source).__name__ == "_AcceptedS1Source"


def test_source_descriptor_loads_exact_accepted_binding(source):
    assert source.report_sha256 == runner.ACCEPTED_S1_REPORT_SHA256
    assert source.result.result_id == runner.ACCEPTED_S1_RESULT_ID
    assert source.result.execution_head == runner.ACCEPTED_S1_EXECUTION_HEAD
    assert source.safe_execution.safe_execution_id == runner.ACCEPTED_S1_SAFE_EXECUTION_ID
    assert (
        source.safe_execution.provider_call_count,
        source.safe_execution.network_call_count,
        source.safe_execution.gemini_call_count,
    ) == (6, 6, 6)
    assert source.safe_execution.real_world_effects_count == 0
    assert source.result.raw_prompt_included is False
    assert source.result.raw_provider_response_included is False


def test_source_typed_validators_pass(source):
    assert s1.validate_supplier_s1_program_result_v01(source.result) == ()
    assert safe.validate_supplier_water_filter_safe_execution_projection_v01(
        source.safe_execution
    ) == ()


def test_source_exact_five_rows(source):
    assert tuple(row.scenario_id for row in source.result.scenarios) == runner.PRESERVED_S1_IDS
    assert len(source.result.scenarios) == 5


def test_source_mode_must_be_0400(accepted_paths):
    _, source_path, _ = accepted_paths
    source_path.chmod(0o600)
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.load_accepted_supplier_s1_source_v01(str(source_path))


def test_source_symlink_is_rejected(tmp_path):
    root, source_path, _ = _prepare_repository(tmp_path)
    target = root / "accepted-copy.json"
    source_path.rename(target)
    source_path.symlink_to(target)
    with pytest.raises((ValueError, OSError)):
        runner.load_accepted_supplier_s1_source_v01(str(source_path))


def test_changed_source_hash_is_rejected(accepted_paths):
    _, source_path, _ = accepted_paths
    source_path.chmod(0o600)
    content = source_path.read_bytes()
    source_path.write_bytes(content.replace(b'"attempt_number":1', b'"attempt_number":2'))
    source_path.chmod(0o400)
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.load_accepted_supplier_s1_source_v01(str(source_path))


@pytest.mark.parametrize(
    "content",
    (
        b'{"a":1,"a":1}\n',
        b'{"a":NaN}\n',
        b'{"a":Infinity}\n',
        b'{"a":1}\r\n',
        b'{"a":1}',
        b'{ "a": 1 }\n',
        b"\xef\xbb\xbf{}\n",
        b'{"a":"\xff"}\n',
        b"[]\n",
    ),
)
def test_strict_json_guards(content):
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._strict_json(content)


def test_exact_nine_row_order_and_names(result):
    assert tuple(row.scenario_id for row in result.scenario_rows) == runner.MATRIX_SCENARIO_IDS
    assert tuple(row.scenario_name for row in result.scenario_rows) == (
        runner.MATRIX_SCENARIO_NAMES
    )
    assert len(result.scenario_rows) == 9


def test_exact_package_adapter_projection(result, source):
    rows = result.package_adapter_scenario_rows
    assert len(rows) == 9
    assert tuple(
        (
            row.scenario_id,
            row.scenario_name,
            row.classification,
            row.technical_status,
            row.business_outcome,
            row.root_status,
            row.supplier_a_status,
            row.packet_status,
            row.corridor_status,
            row.receipt_status,
        )
        for row in rows
    ) == EXPECTED_PACKAGE_ROW_SPECS
    for row in rows:
        assert row.supplier_b_status == "BLOCKED"
        assert row.shipment_status == "HELD"
        assert (
            row.additional_provider_call_count,
            row.additional_network_call_count,
            row.additional_gemini_call_count,
            row.real_world_effects_count,
        ) == (0, 0, 0, 0)
        assert row.real_payment_executed is False
        assert row.real_shipment_released is False
        assert row.evidence_refs == (
            f"evidence:supplier:{row.scenario_id.casefold()}",
        )
    public_rows = runner.supplier_water_filter_negative_matrix_package_rows_v01(
        result,
        source,
    )
    assert tuple(item["scenario_id"] for item in public_rows) == (
        runner.MATRIX_SCENARIO_IDS
    )
    assert all(type(item["evidence_refs"]) is tuple for item in public_rows)


def test_package_projection_is_bound_into_result_identity(source, result):
    rows = list(result.package_adapter_scenario_rows)
    rows[0] = replace(rows[0], classification="changed")
    changed = replace(result, package_adapter_scenario_rows=tuple(rows))
    assert runner._identity(
        runner._RESULT_DOMAIN,
        runner._result_plain(changed, zero_id=True),
    ) != result.result_id
    forged = _rehash_result(changed)
    assert runner.validate_supplier_water_filter_negative_matrix_v01(
        forged,
        source,
    )


def test_accepted_five_s1_rows_are_exact_objects(source, result):
    source_by_id = {row.scenario_id: row for row in source.result.scenarios}
    for row in result.scenario_rows:
        if row.scenario_id in runner.PRESERVED_S1_IDS:
            assert row is source_by_id[row.scenario_id]
            assert runner._s1_scenario_plain(row) == next(
                item
                for item in s1.supplier_s1_program_result_to_plain_dict_v01(
                    source.result
                )["scenarios"]
                if item["scenario_id"] == row.scenario_id
            )


def test_negative_rows_have_separated_attack_and_proof_status(result):
    for row in _negative_rows(result):
        assert row.attack_status == "FAIL_CLOSED"
        assert row.proof_status == "PASS"
        assert row.supplier_b_status == "BLOCKED"
        assert row.shipment_status == "HELD"
        assert row.real_payment_executed is False
        assert row.real_shipment_released is False
        assert row.real_world_effects_count == 0


def test_s_n2_is_bound_to_single_accepted_live_source(result):
    row = _row(result, "S-N2")
    assert len(row.probes) == 4
    assert all(
        probe.source_safe_execution_id == runner.ACCEPTED_S1_SAFE_EXECUTION_ID
        for probe in row.probes
    )
    assert all(
        probe.validator_api
        == "validate_supplier_water_filter_safe_execution_projection_v01"
        for probe in row.probes
    )
    reasons = {reason for probe in row.probes for reason in probe.reason_codes}
    assert "supplier_water_filter_safe_execution_raw_material_forbidden" in reasons
    assert "supplier_water_filter_safe_execution_secret_scan_required" in reasons
    assert "supplier_water_filter_safe_execution_effect_forbidden" in reasons
    assert "supplier_water_filter_safe_execution_call_geometry_invalid" in reasons


def test_s_f1_actual_stable_reason(result):
    row = _row(result, "S-F1")
    assert len(row.probes) == 1
    assert row.probes[0].reason_codes == (packet.REASON_MISSING_HUMAN_APPROVAL_REF,)
    assert row.packet_status == "REJECTED"


def test_s_f2_actual_stable_reasons(result):
    row = _row(result, "S-F2")
    assert len(row.probes) == 4
    reasons = {reason for probe in row.probes for reason in probe.reason_codes}
    assert packet.REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT in reasons
    assert packet.REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT in reasons
    assert packet.REASON_SUPPLIER_B_SCOPE_FORBIDDEN in reasons
    assert packet.REASON_SHIPMENT_RELEASE_FORBIDDEN in reasons


def test_s_f3_actual_stable_reasons(result):
    row = _row(result, "S-F3")
    assert len(row.probes) == 6
    reasons = {reason for probe in row.probes for reason in probe.reason_codes}
    assert packet.REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION in reasons
    assert packet.REASON_RECEIPT_CANNOT_AUTHORIZE_SUPPLIER_B in reasons
    assert packet.REASON_NO_EXPANSION_AFTER_ROOT in reasons
    assert packet.REASON_RECEIPT_CANNOT_RELEASE_SHIPMENT in reasons
    assert packet.REASON_REGISTRY_IS_NOT_PERMISSION in reasons
    assert packet.REASON_REGISTRY_CANNOT_RELEASE_SHIPMENT in reasons
    assert row.receipt_status == "EVIDENCE_ONLY"


def test_every_negative_probe_has_identity_and_zero_delta(result):
    probes = tuple(probe for row in _negative_rows(result) for probe in row.probes)
    assert len(probes) == 15
    assert result.negative_probe_ids == tuple(probe.probe_id for probe in probes)
    assert len(set(result.negative_probe_ids)) == 15
    for probe in probes:
        assert len(probe.probe_id) == 64
        assert probe.baseline_status == "PASS"
        assert probe.attack_status == "FAIL_CLOSED"
        assert probe.proof_status == "PASS"
        assert probe.reason_codes
        assert (
            probe.provider_call_count,
            probe.network_call_count,
            probe.gemini_call_count,
            probe.real_world_effects_count,
        ) == (0, 0, 0, 0)


def test_every_probe_has_exact_ordered_attribution(result):
    probes = tuple(probe for row in _negative_rows(result) for probe in row.probes)
    assert tuple(
        (
            probe.probe_name,
            probe.validator_api,
            probe.mutation_class,
            probe.mutation_fields,
            probe.reason_codes,
        )
        for probe in probes
    ) == EXPECTED_PROBE_ATTRIBUTION
    for probe in probes:
        assert probe.baseline_status == "PASS"
        assert probe.attack_status == "FAIL_CLOSED"
        assert probe.proof_status == "PASS"
        assert probe.source_safe_execution_id == runner.ACCEPTED_S1_SAFE_EXECUTION_ID
        assert (
            probe.provider_call_count,
            probe.network_call_count,
            probe.gemini_call_count,
            probe.real_world_effects_count,
        ) == (0, 0, 0, 0)


def test_inherited_source_and_s2_delta_counts_are_separate(result):
    assert (
        result.accepted_s1_provider_call_count,
        result.accepted_s1_network_call_count,
        result.accepted_s1_gemini_call_count,
    ) == (6, 6, 6)
    assert (
        result.s2_provider_call_count,
        result.s2_network_call_count,
        result.s2_gemini_call_count,
        result.s2_real_world_effects_count,
    ) == (0, 0, 0, 0)
    assert (
        result.s2_collector_invocation_count,
        result.s2_duplicate_live_source_count,
        result.s2_retry_count,
    ) == (0, 0, 0)


def test_actual_s2_projection_builds_and_validates_with_public_adapter(
    source,
    result,
    product_trace,
    kernel_result,
):
    rows = runner.supplier_water_filter_negative_matrix_package_rows_v01(
        result,
        source,
    )
    adapter_result = (
        sealed_adapter.build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
            safe_execution=source.safe_execution,
            scenario_rows=rows,
            source_report=product_trace,
            kernel_adapter_result=kernel_result,
        )
    )
    assert (
        sealed_adapter.validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
            adapter_result,
            safe_execution=source.safe_execution,
            scenario_rows=rows,
            source_report=product_trace,
            kernel_adapter_result=kernel_result,
        )
        == ()
    )
    assert adapter_result.status == "PASS"
    assert adapter_result.safe_execution_id == runner.ACCEPTED_S1_SAFE_EXECUTION_ID
    assert adapter_result.scenario_ids == runner.MATRIX_SCENARIO_IDS
    assert adapter_result.scenario_names == runner.MATRIX_SCENARIO_NAMES
    assert adapter_result.scenario_classifications == tuple(
        spec[2] for spec in EXPECTED_PACKAGE_ROW_SPECS
    )
    assert adapter_result.scenario_technical_statuses == tuple(
        spec[3] for spec in EXPECTED_PACKAGE_ROW_SPECS
    )
    assert adapter_result.scenario_business_outcomes == tuple(
        spec[4] for spec in EXPECTED_PACKAGE_ROW_SPECS
    )
    assert (
        adapter_result.adapter_provider_call_count,
        adapter_result.adapter_network_call_count,
        adapter_result.adapter_gemini_call_count,
        adapter_result.real_world_effects_count,
    ) == (0, 0, 0, 0)
    live_sources = tuple(
        item
        for item in adapter_result.domain_projection.source_records
        if (
            item.observed_provider_call_count,
            item.observed_network_call_count,
            item.observed_gemini_call_count,
        )
        == (6, 6, 6)
    )
    assert len(live_sources) == 1
    assert _row(result, "S-N2").probes[0].source_safe_execution_id == (
        adapter_result.safe_execution_id
    )
    assert rows[1]["classification"] == "live_bound_negative_safe_projection"
    assert rows[4]["classification"] == "live_bound_deterministic_corridor"


def test_build_validation_serialization_and_projection_cannot_reach_live_surfaces(
    monkeypatch,
    source,
    product_trace,
    kernel_result,
):
    def forbidden(*args, **kwargs):
        raise AssertionError("forbidden operation reached")

    monkeypatch.setattr(
        s1,
        "collect_two_domain_supplier_water_filter_program_v01",
        forbidden,
    )
    monkeypatch.setattr(s1, "_execute_real_attempt", forbidden)
    result = runner.build_supplier_water_filter_negative_matrix_v01(source)
    assert runner.validate_supplier_water_filter_negative_matrix_v01(
        result,
        source,
    ) == ()
    runner.supplier_water_filter_negative_matrix_to_plain_dict_v01(result, source)
    rows = runner.supplier_water_filter_negative_matrix_package_rows_v01(
        result,
        source,
    )
    adapter_result = (
        sealed_adapter.build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
            safe_execution=source.safe_execution,
            scenario_rows=rows,
            source_report=product_trace,
            kernel_adapter_result=kernel_result,
        )
    )
    assert (
        sealed_adapter.validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
            adapter_result,
            safe_execution=source.safe_execution,
            scenario_rows=rows,
            source_report=product_trace,
            kernel_adapter_result=kernel_result,
        )
        == ()
    )


@pytest.mark.parametrize(
    "mutation",
    (
        lambda rows: (*rows[:1], replace(rows[1], classification="changed"), *rows[2:]),
        lambda rows: (*rows[:1], replace(rows[1], technical_status="PASS"), *rows[2:]),
        lambda rows: (*rows[:1], replace(rows[1], additional_provider_call_count=1), *rows[2:]),
        lambda rows: (*rows[:1], replace(rows[1], evidence_refs=("changed",)), *rows[2:]),
        lambda rows: rows[:-1],
        lambda rows: (rows[1], rows[0], *rows[2:]),
    ),
)
def test_package_projection_mutation_is_rejected_by_s2_and_public_adapter(
    source,
    result,
    product_trace,
    kernel_result,
    mutation,
):
    changed_rows = tuple(mutation(result.package_adapter_scenario_rows))
    changed_result = replace(result, package_adapter_scenario_rows=changed_rows)
    assert runner.validate_supplier_water_filter_negative_matrix_v01(
        changed_result,
        source,
    )
    plain_rows = tuple(
        runner._package_adapter_row_plain(item, serialized=False)
        for item in changed_rows
        if type(item) is runner.SupplierS2PackageAdapterScenarioRowV01
    )
    with pytest.raises(ValueError):
        sealed_adapter.build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
            safe_execution=source.safe_execution,
            scenario_rows=plain_rows,
            source_report=product_trace,
            kernel_adapter_result=kernel_result,
        )


def test_each_package_projection_row_is_individually_bound(source, result):
    for index, original in enumerate(result.package_adapter_scenario_rows):
        rows = list(result.package_adapter_scenario_rows)
        rows[index] = replace(original, evidence_refs=("changed",))
        changed = _rehash_result(
            replace(result, package_adapter_scenario_rows=tuple(rows))
        )
        assert runner.validate_supplier_water_filter_negative_matrix_v01(
            changed,
            source,
        )


def test_real_public_validators_are_invoked(monkeypatch, source):
    observed = {name: 0 for name in runner.VALIDATOR_API_NAMES}

    def wrap(module, name):
        original = getattr(module, name)

        def counted(*args, **kwargs):
            observed[name] += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(module, name, counted)

    wrap(safe, "validate_supplier_water_filter_safe_execution_projection_v01")
    wrap(packet, "validate_action_commit_packet_v02")
    wrap(packet, "validate_corridor_no_post_root_reasoning_v01")
    wrap(packet, "validate_corridor_step_against_packet_v01")
    wrap(packet, "validate_packet_corridor_entry_v02")
    wrap(packet, "validate_mock_receipt_evidence_v01")
    wrap(packet, "validate_action_commit_packet_registry_v02")
    built = runner.build_supplier_water_filter_negative_matrix_v01(source)
    assert built.final_status == "PASS"
    assert all(count > 0 for count in observed.values())


def test_s_n2_baseline_must_validate_before_mutation(monkeypatch, source):
    original = safe.validate_supplier_water_filter_safe_execution_projection_v01

    def reject_baseline(value):
        if value == source.safe_execution:
            return ("baseline_invalid",)
        return original(value)

    monkeypatch.setattr(
        safe,
        "validate_supplier_water_filter_safe_execution_projection_v01",
        reject_baseline,
    )
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.build_supplier_water_filter_negative_matrix_v01(source)


def test_s_f1_packet_baseline_must_validate_before_mutation(monkeypatch, source):
    original = packet.validate_action_commit_packet_v02

    def reject_baseline(value):
        if value.human_approval_ref:
            return False, ("baseline_invalid",)
        return original(value)

    monkeypatch.setattr(packet, "validate_action_commit_packet_v02", reject_baseline)
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.build_supplier_water_filter_negative_matrix_v01(source)


def test_s_f2_corridor_baseline_must_validate_before_mutation(monkeypatch, source):
    monkeypatch.setattr(
        packet,
        "validate_corridor_no_post_root_reasoning_v01",
        lambda corridor: (False, ("baseline_invalid",)),
    )
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.build_supplier_water_filter_negative_matrix_v01(source)


def test_s_f3_receipt_baseline_must_validate_before_mutation(monkeypatch, source):
    original = packet.validate_mock_receipt_evidence_v01

    def reject_baseline(packet_value, receipt):
        if not any(
            (
                receipt.creates_future_permission,
                receipt.authorizes_supplier_b,
                receipt.creates_final_output,
                receipt.releases_shipment,
            )
        ):
            return False, ("baseline_invalid",)
        return original(packet_value, receipt)

    monkeypatch.setattr(packet, "validate_mock_receipt_evidence_v01", reject_baseline)
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.build_supplier_water_filter_negative_matrix_v01(source)


def test_accepted_attack_forces_fail_closed(monkeypatch, source):
    original = safe.validate_supplier_water_filter_safe_execution_projection_v01

    def accept_attack(value):
        if value.raw_prompt_included:
            return ()
        return original(value)

    monkeypatch.setattr(
        safe,
        "validate_supplier_water_filter_safe_execution_projection_v01",
        accept_attack,
    )
    with pytest.raises(ValueError, match=runner.REASON_PROBE_ACCEPTED):
        runner.build_supplier_water_filter_negative_matrix_v01(source)


def test_changed_reason_forces_fail_closed(monkeypatch, source):
    original = packet.validate_action_commit_packet_v02

    def changed_reason(value):
        valid, reasons = original(value)
        if value.human_approval_ref == "":
            return valid, ("wrong_reason",)
        return valid, reasons

    monkeypatch.setattr(packet, "validate_action_commit_packet_v02", changed_reason)
    with pytest.raises(ValueError, match=runner.REASON_REASON_MISMATCH):
        runner.build_supplier_water_filter_negative_matrix_v01(source)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda rows: rows[:-1],
        lambda rows: (*rows, rows[-1]),
        lambda rows: (rows[1], rows[0], *rows[2:]),
    ),
)
def test_missing_duplicate_or_reordered_rows_fail(source, result, mutation):
    changed = replace(result, scenario_rows=tuple(mutation(result.scenario_rows)))
    changed = _rehash_result(changed)
    assert runner.validate_supplier_water_filter_negative_matrix_v01(changed, source)


def test_rehashed_forged_negative_scenario_fails(source, result):
    rows = list(result.scenario_rows)
    index = next(i for i, row in enumerate(rows) if row.scenario_id == "S-F1")
    changed_row = replace(rows[index], supplier_b_status="PASS")
    changed_row = replace(
        changed_row,
        scenario_result_id=runner._identity(
            runner._NEGATIVE_SCENARIO_DOMAIN,
            runner._negative_scenario_plain(changed_row, zero_id=True),
        ),
    )
    rows[index] = changed_row
    forged = _rehash_result(replace(result, scenario_rows=tuple(rows)))
    assert runner.validate_supplier_water_filter_negative_matrix_v01(forged, source)


def test_rehashed_forged_preserved_s1_scenario_fails(source, result):
    rows = list(result.scenario_rows)
    original = rows[0]
    changed = replace(original, supplier_b_status="PASS")
    changed = replace(
        changed,
        scenario_result_id=s1._identity(
            s1._SCENARIO_DOMAIN,
            s1._scenario_plain(changed, zero_id=True),
        ),
    )
    rows[0] = changed
    forged = _rehash_result(replace(result, scenario_rows=tuple(rows)))
    assert runner.validate_supplier_water_filter_negative_matrix_v01(forged, source)


def test_altered_s1_source_identity_fails(source, result):
    changed_safe = replace(source.safe_execution, safe_execution_id="f" * 64)
    changed_source = replace(source, safe_execution=changed_safe)
    assert runner.validate_supplier_water_filter_negative_matrix_v01(
        result,
        changed_source,
    )


def test_rehashed_safe_semantic_identity_forgery_fails(source, result):
    hashes = list(source.safe_execution.actor_safe_projection_hashes)
    hashes[0] = "f" * 64
    changed_safe = replace(
        source.safe_execution,
        actor_safe_projection_hashes=tuple(hashes),
    )
    changed_safe = replace(
        changed_safe,
        safe_execution_id=safe._safe_execution_identity(changed_safe),
    )
    assert safe.validate_supplier_water_filter_safe_execution_projection_v01(
        changed_safe
    ) == ()
    changed_source = replace(source, safe_execution=changed_safe)
    assert runner.REASON_SOURCE_INVALID in (
        runner.validate_supplier_water_filter_negative_matrix_v01(
            result,
            changed_source,
        )
    )


@pytest.mark.parametrize(
    "field,value",
    (
        ("s2_provider_call_count", 1),
        ("s2_network_call_count", 1),
        ("s2_gemini_call_count", 1),
        ("s2_real_world_effects_count", 1),
        ("s2_collector_invocation_count", 1),
        ("s2_duplicate_live_source_count", 1),
        ("s2_retry_count", 1),
        ("s2_provider_call_count", True),
    ),
)
def test_nonzero_and_bool_counters_fail(source, result, field, value):
    forged = _rehash_result(replace(result, **{field: value}))
    assert runner.validate_supplier_water_filter_negative_matrix_v01(forged, source)


def test_result_plain_is_canonical_safe_and_deterministic(source, result):
    first = runner.supplier_water_filter_negative_matrix_to_plain_dict_v01(
        result,
        source,
    )
    second_result = runner.build_supplier_water_filter_negative_matrix_v01(source)
    second = runner.supplier_water_filter_negative_matrix_to_plain_dict_v01(
        second_result,
        source,
    )
    assert first == second
    assert result == second_result
    assert canonical_json_bytes_v01(first) == canonical_json_bytes_v01(second)


def test_output_contains_no_raw_or_private_material(source, result):
    content = canonical_json_bytes_v01(
        runner.supplier_water_filter_negative_matrix_to_plain_dict_v01(result, source)
    ).decode("utf-8")
    lowered = content.lower()
    for forbidden in (
        '"raw_prompt":',
        '"raw_response":',
        '"provider_response":',
        '"api_key":',
        '"credential":',
        "hedgehogprivateevidence",
        "/users/",
        "traceback",
        "object at 0x",
    ):
        assert forbidden not in lowered


def test_run_writes_canonical_mode_0400_output(accepted_paths):
    root, source_path, output = accepted_paths
    result = runner.run_supplier_water_filter_negative_matrix_v01(
        repository_root=str(root),
        source_path=str(source_path),
        output_path=str(output),
    )
    assert result.final_status == "PASS"
    assert stat.S_IMODE(output.stat().st_mode) == 0o400
    content = output.read_bytes()
    assert content.endswith(b"\n") and not content.endswith(b"\n\n")
    assert canonical_json_bytes_v01(json.loads(content)) + b"\n" == content


def test_cli_pass_summary_is_sanitized_one_line(accepted_paths):
    root, source_path, output = accepted_paths
    completed = _cli(root, source_path, output)
    assert completed.returncode == 0
    assert completed.stderr == ""
    assert completed.stdout.count("\n") == 1
    summary = json.loads(completed.stdout)
    assert summary == {
        "final_status": "PASS",
        "gate_id": runner.GATE_ID,
        "result_id": summary["result_id"],
    }
    assert len(summary["result_id"]) == 64


def test_two_fresh_process_outputs_are_byte_identical(tmp_path):
    first = _prepare_repository(tmp_path / "one")
    second = _prepare_repository(tmp_path / "two")
    first_run = _cli(*first)
    second_run = _cli(*second)
    assert first_run.returncode == second_run.returncode == 0
    assert first[2].read_bytes() == second[2].read_bytes()
    assert json.loads(first_run.stdout)["result_id"] == json.loads(second_run.stdout)[
        "result_id"
    ]


def test_existing_output_fails_closed_without_mutation(accepted_paths):
    root, source_path, output = accepted_paths
    output.write_bytes(b"foreign")
    before = output.read_bytes()
    completed = _cli(root, source_path, output)
    assert completed.returncode == 2
    assert output.read_bytes() == before
    assert json.loads(completed.stdout)["final_status"] == "FAIL_CLOSED"


def test_output_symlink_fails_closed(accepted_paths, tmp_path):
    root, source_path, output = accepted_paths
    foreign = tmp_path / "foreign"
    foreign.write_bytes(b"foreign")
    output.symlink_to(foreign)
    completed = _cli(root, source_path, output)
    assert completed.returncode == 2
    assert foreign.read_bytes() == b"foreign"


def test_parent_symlink_fails_closed(tmp_path):
    root, source_path, output = _prepare_repository(tmp_path)
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    source_content = source_path.read_bytes()
    source_path.parent.rename(real_parent / "supplier_water_filter")
    source_path.parent.symlink_to(real_parent / "supplier_water_filter")
    assert source_content
    completed = _cli(root, source_path, output)
    assert completed.returncode == 2
    assert not output.exists()


@pytest.mark.parametrize(
    "extra",
    (
        ("--unknown", "x"),
        ("positional",),
        ("--repository", "/tmp"),
        ("--output", "/tmp/duplicate"),
        ("--output=/tmp/duplicate",),
    ),
)
def test_cli_rejects_unknown_positional_abbreviated_and_duplicate_options(
    accepted_paths,
    extra,
):
    root, source_path, output = accepted_paths
    completed = _cli(root, source_path, output, *extra)
    assert completed.returncode == 2
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == {
        "final_status": "FAIL_CLOSED",
        "gate_id": runner.GATE_ID,
        "reason_code": runner.REASON_FAIL_CLOSED,
    }
    assert not output.exists()


def test_relative_paths_fail_closed():
    assert runner.main(
        [
            "--repository-root",
            ".",
            "--accepted-s1-report",
            "source.json",
            "--output",
            "output.json",
        ]
    ) == 2


def test_race_creating_foreign_output_is_preserved(monkeypatch, accepted_paths):
    root, source_path, output = accepted_paths
    original = runner._write_output

    def raced(path, content, expected_parent_identity):
        path.write_bytes(b"foreign")
        return original(path, content, expected_parent_identity)

    monkeypatch.setattr(runner, "_write_output", raced)
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner.run_supplier_water_filter_negative_matrix_v01(
            repository_root=str(root),
            source_path=str(source_path),
            output_path=str(output),
        )
    assert output.read_bytes() == b"foreign"


def test_write_failure_removes_only_owned_output(monkeypatch, accepted_paths):
    root, source_path, output = accepted_paths

    def fail_write(descriptor, content):
        raise OSError("injected")

    monkeypatch.setattr(runner, "_write_all", fail_write)
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner.run_supplier_water_filter_negative_matrix_v01(
            repository_root=str(root),
            source_path=str(source_path),
            output_path=str(output),
        )
    assert not output.exists()


def test_parent_replacement_race_fails_before_output(monkeypatch, accepted_paths, tmp_path):
    root, source_path, output = accepted_paths
    original = runner._write_output
    moved_parent = tmp_path / "moved-parent"

    def replace_parent(path, content, expected_parent_identity):
        path.parent.rename(moved_parent)
        path.parent.mkdir()
        return original(path, content, expected_parent_identity)

    monkeypatch.setattr(runner, "_write_output", replace_parent)
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner.run_supplier_water_filter_negative_matrix_v01(
            repository_root=str(root),
            source_path=str(source_path),
            output_path=str(output),
        )
    assert not output.exists()
    assert not (moved_parent / output.name).exists()


def test_cleanup_uncertainty_remains_fail_closed(monkeypatch, accepted_paths):
    root, source_path, output = accepted_paths

    def fail_write(descriptor, content):
        raise OSError("injected")

    def uncertain_cleanup(parent_fd, name, identity):
        raise OSError("uncertain")

    monkeypatch.setattr(runner, "_write_all", fail_write)
    monkeypatch.setattr(runner, "_cleanup_owned_output", uncertain_cleanup)
    with pytest.raises(OSError, match="uncertain"):
        runner.run_supplier_water_filter_negative_matrix_v01(
            repository_root=str(root),
            source_path=str(source_path),
            output_path=str(output),
        )


def test_partial_writes_complete_successfully(monkeypatch, accepted_paths):
    root, source_path, output = accepted_paths
    original = runner.os.write

    def partial(descriptor, content):
        return original(descriptor, content[: max(1, len(content) // 3)])

    monkeypatch.setattr(runner.os, "write", partial)
    runner.run_supplier_water_filter_negative_matrix_v01(
        repository_root=str(root),
        source_path=str(source_path),
        output_path=str(output),
    )
    assert output.exists()


def test_reread_failure_removes_owned_output(monkeypatch, accepted_paths):
    root, source_path, output = accepted_paths
    original = runner.os.read
    output_descriptor = {"value": None}
    original_open = runner.os.open

    def tracked_open(path, flags, *args, **kwargs):
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & os.O_ACCMODE == os.O_RDONLY:
            output_descriptor["value"] = descriptor
        return descriptor

    def changed_read(descriptor, count):
        if descriptor == output_descriptor["value"]:
            output_descriptor["value"] = None
            return b"changed"
        return original(descriptor, count)

    monkeypatch.setattr(runner.os, "open", tracked_open)
    monkeypatch.setattr(runner.os, "read", changed_read)
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner.run_supplier_water_filter_negative_matrix_v01(
            repository_root=str(root),
            source_path=str(source_path),
            output_path=str(output),
        )
    assert not output.exists()


def test_foreign_replacement_is_not_removed(monkeypatch, accepted_paths):
    root, source_path, output = accepted_paths

    def replace_then_fail(descriptor, content):
        output.unlink()
        output.write_bytes(b"foreign-replacement")
        raise OSError("injected")

    monkeypatch.setattr(runner, "_write_all", replace_then_fail)
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner.run_supplier_water_filter_negative_matrix_v01(
            repository_root=str(root),
            source_path=str(source_path),
            output_path=str(output),
        )
    assert output.read_bytes() == b"foreign-replacement"


def _assert_total_validation_failure(value, source):
    errors = runner.validate_supplier_water_filter_negative_matrix_v01(
        value,
        source,
    )
    assert type(errors) is tuple
    assert errors
    assert all(type(item) is str for item in errors)


@pytest.mark.parametrize(
    "bad_value",
    (object(), {}, None, "wrong-row"),
    ids=("object", "dict", "none", "string"),
)
def test_total_validator_rejects_arbitrary_scenario_row_values(
    source,
    result,
    bad_value,
):
    _assert_total_validation_failure(
        _replace_matrix_row(result, 0, bad_value),
        source,
    )


@pytest.mark.parametrize(
    "bad_value",
    (object(), [], {}, None, "wrong-container"),
    ids=("object", "list", "dict", "none", "string"),
)
def test_total_validator_requires_scenario_rows_tuple(source, result, bad_value):
    _assert_total_validation_failure(
        replace(result, scenario_rows=bad_value),
        source,
    )


def test_total_validator_rejects_wrong_preserved_and_negative_row_types(
    source,
    result,
):
    _assert_total_validation_failure(
        _replace_matrix_row(result, 0, result.scenario_rows[1]),
        source,
    )
    _assert_total_validation_failure(
        _replace_matrix_row(result, 1, result.scenario_rows[0]),
        source,
    )


@pytest.mark.parametrize(
    "bad_value",
    (object(), {}, None, "wrong-probe"),
    ids=("object", "dict", "none", "string"),
)
def test_total_validator_rejects_arbitrary_probe_values(source, result, bad_value):
    negative = result.scenario_rows[1]
    changed = replace(negative, probes=(bad_value,))
    _assert_total_validation_failure(
        _replace_matrix_row(result, 1, changed),
        source,
    )


@pytest.mark.parametrize(
    "bad_value",
    ([], {}, None, "wrong-container", ()),
    ids=("list", "dict", "none", "string", "empty-tuple"),
)
def test_total_validator_requires_nonempty_probe_tuple(source, result, bad_value):
    negative = result.scenario_rows[1]
    changed = replace(negative, probes=bad_value)
    _assert_total_validation_failure(
        _replace_matrix_row(result, 1, changed),
        source,
    )


@pytest.mark.parametrize(
    "field,bad_value",
    (
        ("probe_id", None),
        ("probe_id", 1),
        ("probe_id", True),
        ("probe_id", b"bytes"),
        ("probe_id", "not-a-sha256"),
        ("reason_codes", (None,)),
        ("reason_codes", (1,)),
        ("reason_codes", ["wrong-container"]),
        ("mutation_fields", (None,)),
        ("mutation_fields", (1,)),
        ("mutation_fields", ["wrong-container"]),
    ),
)
def test_total_validator_rejects_malformed_probe_fields(
    source,
    result,
    field,
    bad_value,
):
    negative = result.scenario_rows[1]
    changed_probe = replace(negative.probes[0], **{field: bad_value})
    changed_row = replace(
        negative,
        probes=(changed_probe, *negative.probes[1:]),
    )
    _assert_total_validation_failure(
        _replace_matrix_row(result, 1, changed_row),
        source,
    )


@pytest.mark.parametrize(
    "field,bad_value",
    (
        ("result_id", None),
        ("result_id", 1),
        ("result_id", True),
        ("result_id", b"bytes"),
        ("negative_probe_ids", (None,)),
        ("negative_probe_ids", (1,)),
        ("negative_probe_ids", (True,)),
        ("negative_probe_ids", (b"bytes",)),
        ("negative_probe_ids", ["wrong-container"]),
    ),
)
def test_total_validator_rejects_non_string_result_and_probe_ids(
    source,
    result,
    field,
    bad_value,
):
    _assert_total_validation_failure(
        replace(result, **{field: bad_value}),
        source,
    )


@pytest.mark.parametrize(
    "mutation",
    (
        lambda rows: (object(), *rows[1:]),
        lambda rows: rows[:-1],
        lambda rows: (*rows, rows[-1]),
        lambda rows: (rows[1], rows[0], *rows[2:]),
        lambda rows: (replace(rows[0], classification=1), *rows[1:]),
        lambda rows: (
            replace(rows[0], additional_provider_call_count=True),
            *rows[1:],
        ),
    ),
)
def test_total_validator_rejects_malformed_package_projection(
    source,
    result,
    mutation,
):
    changed = replace(
        result,
        package_adapter_scenario_rows=tuple(
            mutation(result.package_adapter_scenario_rows)
        ),
    )
    _assert_total_validation_failure(changed, source)


def test_validator_rejects_non_result(source):
    assert runner.validate_supplier_water_filter_negative_matrix_v01({}, source) == (
        runner.REASON_INVALID,
    )


@pytest.mark.parametrize(
    "bad_source",
    (object(), {}, None, "wrong-source"),
    ids=("object", "dict", "none", "string"),
)
def test_validator_rejects_non_source_without_throwing(result, bad_source):
    assert runner.validate_supplier_water_filter_negative_matrix_v01(
        result,
        bad_source,
    ) == (runner.REASON_SOURCE_INVALID,)


def test_serializer_rejects_invalid_result(source, result):
    forged = replace(result, final_status="FAIL_CLOSED")
    with pytest.raises(ValueError, match=runner.REASON_INVALID):
        runner.supplier_water_filter_negative_matrix_to_plain_dict_v01(
            forged,
            source,
        )


def test_canonical_output_state_is_unchanged_by_tests():
    assert _canonical_output_state(CANONICAL_S2_OUTPUT) == CANONICAL_S2_OUTPUT_BASELINE


def test_static_forbidden_operation_boundaries():
    tree = ast.parse(Path(runner.__file__).read_text(encoding="utf-8"))
    import_roots = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not import_roots & {
        "socket",
        "requests",
        "urllib",
        "httpx",
        "google",
        "genai",
        "openai",
        "anthropic",
    }
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert not calls & {
        "collect_two_domain_supplier_water_filter_program_v01",
        "collect_full_wow_v1_2_manual_live_multillm_fractal_trace",
        "create_package",
        "anchor",
        "replay",
    }


def test_dataclass_field_sets_are_closed():
    assert tuple(item.name for item in fields(runner.SupplierS2ValidatorProbeV01)) == (
        "probe_id",
        "probe_name",
        "validator_api",
        "mutation_class",
        "mutation_fields",
        "baseline_status",
        "attack_status",
        "proof_status",
        "reason_codes",
        "source_safe_execution_id",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "real_world_effects_count",
    )
    assert tuple(
        item.name
        for item in fields(runner.SupplierS2PackageAdapterScenarioRowV01)
    ) == (
        "scenario_id",
        "scenario_name",
        "classification",
        "technical_status",
        "business_outcome",
        "root_status",
        "supplier_a_status",
        "supplier_b_status",
        "shipment_status",
        "packet_status",
        "corridor_status",
        "receipt_status",
        "additional_provider_call_count",
        "additional_network_call_count",
        "additional_gemini_call_count",
        "real_payment_executed",
        "real_shipment_released",
        "real_world_effects_count",
        "evidence_refs",
    )
    assert tuple(
        item.name for item in fields(runner.SupplierS2NegativeMatrixResultV01)
    ) == (
        "result_id",
        "result_version",
        "programme_id",
        "gate_id",
        "domain_id",
        "implementation_sha256",
        "accepted_s1_report_ref",
        "accepted_s1_report_sha256",
        "accepted_s1_result_id",
        "accepted_s1_execution_head",
        "accepted_s1_safe_execution_id",
        "accepted_s1_provider_call_count",
        "accepted_s1_network_call_count",
        "accepted_s1_gemini_call_count",
        "s2_provider_call_count",
        "s2_network_call_count",
        "s2_gemini_call_count",
        "s2_real_world_effects_count",
        "s2_collector_invocation_count",
        "s2_duplicate_live_source_count",
        "s2_retry_count",
        "scenario_rows",
        "package_adapter_scenario_rows",
        "negative_probe_ids",
        "invoked_validator_api_names",
        "supplier_b_status",
        "shipment_status",
        "receipt_status",
        "real_payment_executed",
        "real_shipment_released",
        "final_status",
        "validation_errors",
    )


def test_implementation_identity_matches_file(result):
    assert result.implementation_sha256 == hashlib.sha256(
        Path(runner.__file__).read_bytes()
    ).hexdigest()
