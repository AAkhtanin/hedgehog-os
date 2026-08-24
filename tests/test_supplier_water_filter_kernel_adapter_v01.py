from __future__ import annotations

import ast
import copy
from dataclasses import fields, is_dataclass, replace
import inspect
from pathlib import Path

import pytest

from demo.run_full_wow_v1_2_product_trace import (
    collect_full_wow_v1_2_product_trace,
)
from hedgehog.domains import supplier_water_filter as supplier_package
from hedgehog.domains.supplier_water_filter import kernel_adapter_v01 as adapter
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.kernel import multiroot_v01 as multiroot


EXPECTED_FIELDS = (
    "adapter_id",
    "adapter_version",
    "source_run_id",
    "source_report_id",
    "source_trace_type",
    "transaction_id",
    "owner_root_id",
    "supplier_a_status",
    "supplier_b_status",
    "shipment_status",
    "receipt_status",
    "kernel_artifacts",
    "kernel_manifest",
    "kernel_unanchored_verification",
    "kernel_anchored_verification",
    "kernel_replay",
    "causal_consumption_refs",
    "multiroot_outcome",
    "multiroot_validation",
    "business_module_count",
    "transition_card_count",
    "dependency_edge_count",
    "fractal_branch_count",
    "result_proposal_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "real_world_effects_count",
)
EXPECTED_FUNCTIONS = (
    "build_supplier_water_filter_kernel_adapter_result_v01",
    "validate_supplier_water_filter_kernel_adapter_result_v01",
    "supplier_water_filter_kernel_adapter_result_to_plain_dict_v01",
)
EXPECTED_MODULE_IDS = (
    "warehouse_api_sandbox",
    "supplier_a_api_sandbox",
    "supplier_b_api_sandbox",
    "legal_module",
    "accounting_module",
    "bank_a_legacy_sandbox",
    "bank_b_hedgehog_native_preview",
)

RETIRED_RUNTIME_EVENT = "runtime_" + "plan" + "graph_compiled"


@pytest.fixture(scope="module")
def source_report() -> dict[str, object]:
    report = collect_full_wow_v1_2_product_trace()
    assert report["final_status"] == "PASS"
    assert report["validation_errors"] == ()
    return report


@pytest.fixture(scope="module")
def result(source_report):
    built = adapter._build_exact_result(source_report)
    assert adapter._result_structure_errors(built) == ()
    assert adapter.build_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report
    ) == built
    assert not adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report, result=built
    )
    return built


def _mutated(report: dict[str, object], path: tuple[object, ...], value: object):
    changed = copy.deepcopy(report)
    cursor = changed
    for item in path[:-1]:
        cursor = cursor[item]
    cursor[path[-1]] = value
    return changed


def _contains_forbidden_projection_value(value: object) -> bool:
    if isinstance(value, tuple) or isinstance(value, bytes) or is_dataclass(value):
        return True
    if isinstance(value, dict):
        return any(
            _contains_forbidden_projection_value(key)
            or _contains_forbidden_projection_value(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_projection_value(item) for item in value)
    return False


def _rebuild_artifact(
    artifact,
    *,
    payload: dict[str, object] | None = None,
    trace_refs: tuple[str, ...] | None = None,
):
    plain = abi.kernel_artifact_to_plain_dict_v01(artifact)
    return abi.build_kernel_artifact_v01(
        abi_version=artifact.abi_version,
        artifact_id=artifact.artifact_id,
        artifact_type=artifact.artifact_type,
        schema_version=artifact.schema_version,
        transaction_id=artifact.transaction_id,
        owner_root_id=artifact.owner_root_id,
        source_component=artifact.source_component,
        authority_class=artifact.authority_class,
        lifecycle_state=artifact.lifecycle_state,
        payload=plain["payload"] if payload is None else payload,
        trace_refs=artifact.trace_refs if trace_refs is None else trace_refs,
        parent_refs=artifact.parent_refs,
        time_envelope=plain["time_envelope"],
    )


def _rebuild_result_integrity(result, artifacts):
    manifest = adapter._build_manifest_from_artifacts(artifacts)
    payload_rows = tuple(
        (artifact.artifact_id, abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"])
        for artifact in artifacts
    )
    unanchored = integrity.verify_artifact_manifest_v01(
        manifest=manifest,
        payload_rows=payload_rows,
    )
    anchored = integrity.verify_artifact_manifest_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    replay = integrity.verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    changed = replace(
        result,
        kernel_artifacts=artifacts,
        kernel_manifest=manifest,
        kernel_unanchored_verification=unanchored,
        kernel_anchored_verification=anchored,
        kernel_replay=replay,
    )
    return replace(changed, adapter_id=adapter._adapter_id(changed))


def _rebuild_result_multiroot(result, decision):
    outcome = multiroot.build_transaction_outcome_envelope_v01(
        transaction_id=adapter.TRANSACTION_ID,
        expected_root_ids=(adapter.OWNER_ROOT_ID,),
        root_decisions=(decision,),
        cross_root_evidence_refs=(),
    )
    validation = multiroot.validate_multiroot_v01(outcome)
    changed = replace(
        result,
        multiroot_outcome=outcome,
        multiroot_validation=validation,
    )
    return replace(changed, adapter_id=adapter._adapter_id(changed))


def _rebuild_supplier_decision(result, **changes):
    decision = result.multiroot_outcome.root_decisions[0]
    values = {
        "transaction_id": decision.transaction_id,
        "root_id": decision.root_id,
        "root_decision_id": decision.root_decision_id,
        "source_decision_ref": decision.source_decision_ref,
        "outcome_class": decision.outcome_class,
        "reason_code": decision.reason_code,
        "selected_subject_id": decision.selected_subject_id,
        "evidence_refs": decision.evidence_refs,
        "cross_root_input_refs": decision.cross_root_input_refs,
    }
    values.update(changes)
    return multiroot.build_root_decision_envelope_v01(**values)


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("MODULE_ID", "supplier_water_filter_kernel_adapter_v01"),
        ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1d2"),
        ("ADAPTER_VERSION", "v0.1"),
        ("SOURCE_RUN_ID", "full_wow_v1_2_product_trace_v01"),
        ("SOURCE_REPORT_ID", "full_wow_v1_2_product_trace_v01"),
        ("SOURCE_TRACE_TYPE", "deterministic_product_trace_lane"),
        ("TRANSACTION_ID", "supplier_water_filter:SH-2042:INV-2042"),
        ("OWNER_ROOT_ID", "root:supplier_water_filter_business_owner"),
        ("SUPPLIER_A_STATUS", "SUPPLIER_A_SCOPED_REVIEW_READY"),
        ("SUPPLIER_B_STATUS", "BLOCKED"),
        ("SHIPMENT_STATUS", "HELD"),
        ("RECEIPT_STATUS", "EVIDENCE_ONLY"),
        ("BUSINESS_MODULE_COUNT", 7),
        ("TRANSITION_CARD_COUNT", 23),
        ("DEPENDENCY_EDGE_COUNT", 22),
        ("FRACTAL_BRANCH_COUNT", 8),
        ("RESULT_PROPOSAL_COUNT", 8),
        ("ROOT_DECISION_COUNT", 1),
        ("CROSS_ROOT_EVIDENCE_COUNT", 0),
    ),
)
def test_constants_are_exact(name, expected):
    assert getattr(adapter, name) == expected


@pytest.mark.parametrize(("index", "field_name"), enumerate(EXPECTED_FIELDS))
def test_public_dataclass_field_order(index, field_name):
    assert fields(adapter.SupplierWaterFilterKernelAdapterResultV01)[index].name == field_name


def test_public_dataclass_is_frozen_and_slotted(result):
    assert adapter.SupplierWaterFilterKernelAdapterResultV01.__dataclass_params__.frozen
    assert "__slots__" in vars(adapter.SupplierWaterFilterKernelAdapterResultV01)
    with pytest.raises((AttributeError, TypeError)):
        result.adapter_version = "changed"


def test_public_function_surface_is_exact():
    public_functions = tuple(
        name
        for name, value in vars(adapter).items()
        if not name.startswith("_")
        and inspect.isfunction(value)
        and value.__module__ == adapter.__name__
    )
    assert public_functions == EXPECTED_FUNCTIONS
    assert "annotations" not in vars(adapter)


def test_package_surface_is_exact():
    assert supplier_package.__all__ == (
        "SupplierWaterFilterKernelAdapterResultV01",
        "build_supplier_water_filter_kernel_adapter_result_v01",
        "validate_supplier_water_filter_kernel_adapter_result_v01",
        "supplier_water_filter_kernel_adapter_result_to_plain_dict_v01",
    )
    assert all(hasattr(supplier_package, name) for name in supplier_package.__all__)


@pytest.mark.parametrize(
    "forbidden_name",
    (
        "collect_source_report",
        "collect_full_wow_v1_2_product_trace",
        "load_package",
        "load_source_report",
        "read_filesystem",
        "execute_effect",
        "execute_real_effect",
        "register_provider",
    ),
)
def test_forbidden_public_apis_are_absent(forbidden_name):
    assert not hasattr(adapter, forbidden_name)


def test_source_identity_and_geometry_are_accepted(source_report, result):
    assert adapter._source_report_errors(source_report) == ()
    assert result.business_module_count == 7
    assert result.transition_card_count == 23
    assert result.dependency_edge_count == 22
    assert result.fractal_branch_count == 8
    assert result.result_proposal_count == 8


def test_current_topology_event_is_runtime_owned_non_authority(result):
    artifact = result.kernel_artifacts[11]
    plain = abi.kernel_artifact_to_plain_dict_v01(artifact)
    assert artifact.artifact_id == (
        "supplier_water_filter_artifact:12:"
        "runtime_execution_topology_materialized"
    )
    assert artifact.artifact_type == "RuntimeExecutionTopology"
    assert artifact.authority_class == "NON_AUTHORITY"
    assert artifact.lifecycle_state == "VALIDATED"
    assert artifact.parent_refs == (result.kernel_artifacts[10].artifact_id,)
    assert result.kernel_artifacts[12].parent_refs == (artifact.artifact_id,)
    assert plain["payload"]["step_id"] == (
        "runtime_execution_topology_materialized"
    )
    assert RETIRED_RUNTIME_EVENT not in repr(plain)


def test_retired_topology_event_has_no_compatibility_input_path(source_report):
    changed = copy.deepcopy(source_report)
    changed["transition_cards"][10]["next_step"] = RETIRED_RUNTIME_EVENT
    changed["transition_cards"][11]["step_id"] = RETIRED_RUNTIME_EVENT
    errors = adapter._source_report_errors(changed)
    assert "supplier_water_filter_source_geometry_mismatch" in errors
    assert "supplier_water_filter_source_report_hash_mismatch" in errors
    with pytest.raises(ValueError):
        adapter.build_supplier_water_filter_kernel_adapter_result_v01(
            source_report=changed
        )


def test_topology_vocabulary_repair_preserves_root_effect_and_reference_behavior(
    source_report, result
):
    assert result.multiroot_outcome.expected_root_ids == (adapter.OWNER_ROOT_ID,)
    assert len(result.multiroot_outcome.root_decisions) == 1
    assert result.multiroot_outcome.root_decisions[0].outcome_class == "HELD"
    assert source_report["business_boundaries"]["root_remains_final_authority"]
    assert source_report["real_world_effects_count"] == result.real_world_effects_count == 0
    assert result.transition_card_count == 23
    assert result.dependency_edge_count == 22
    assert result.fractal_branch_count == 8
    assert result.result_proposal_count == 8


def test_complete_source_report_identity_is_exact(source_report, result):
    assert adapter._source_report_hash(source_report) == (
        adapter._EXPECTED_SOURCE_REPORT_HASH
    )
    assert adapter._EXPECTED_SOURCE_REPORT_HASH == (
        "4c72d34880b959928499fe1917556f29f42351a05d6cdc7a8844ced3059bbc3a"
    )
    assert adapter._source_report_errors(source_report) == ()
    assert adapter.build_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report
    ) == result
    assert adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report,
        result=result,
    ) == ()


@pytest.mark.parametrize(("index", "module_id"), enumerate(EXPECTED_MODULE_IDS))
def test_source_business_module_order(source_report, index, module_id):
    assert source_report["business_modules"][index]["module_id"] == module_id


@pytest.mark.parametrize(
    ("path", "value", "expected_reason"),
    (
        (("run_id",), "wrong", "supplier_water_filter_source_identity_mismatch"),
        (("report_id",), "wrong", "supplier_water_filter_source_identity_mismatch"),
        (("trace_type",), "wrong", "supplier_water_filter_source_identity_mismatch"),
        (("product_trace_status",), "FAIL_CLOSED", "supplier_water_filter_source_report_invalid"),
        (("final_status",), "FAIL_CLOSED", "supplier_water_filter_source_report_invalid"),
        (("v1_2_implemented_scope",), "other", "supplier_water_filter_source_report_invalid"),
        (("manual_live_multillm_fractal_lane_implemented",), True, "supplier_water_filter_source_report_invalid"),
        (("production_ready_claimed",), True, "supplier_water_filter_source_report_invalid"),
        (("public_auditor_ready_claimed",), True, "supplier_water_filter_source_report_invalid"),
        (("validation_errors",), ("bad",), "supplier_water_filter_source_report_invalid"),
        (("business_modules",), (), "supplier_water_filter_source_geometry_mismatch"),
        (("business_modules", 0, "module_id"), "changed", "supplier_water_filter_source_geometry_mismatch"),
        (("business_modules", 0, "items_checked", 0, "shortage_qty"), 3, "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 1, "can_cover_shortage_qty"), 1, "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 2, "supplier_status"), "available", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 2, "invoice_status"), "match", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 2, "delivery_status"), "ready", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 2, "legal_status"), "clear", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 4, "payment_permission_status"), "granted", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 5, "payment_permission_status"), "granted", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_modules", 6, "execution_allowed"), True, "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_boundaries", "supplier_B_final_status"), "PASS", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_boundaries", "shipment_final_status"), "RELEASED", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_boundaries", "receipt_final_status"), "AUTHORITY", "supplier_water_filter_source_business_outcome_mismatch"),
        (("business_boundaries", "root_remains_final_authority"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("post_vv_gt_root", "root_first_decision"), "READY", "supplier_water_filter_source_business_outcome_mismatch"),
        (("post_vv_gt_root", "root_second_decision"), "PASS", "supplier_water_filter_source_business_outcome_mismatch"),
        (("approval_packet_receipt_boundary", "human_approval_scope"), "all", "supplier_water_filter_source_business_outcome_mismatch"),
        (("approval_packet_receipt_boundary", "root_created_mock_action_commit_packet_observed"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("approval_packet_receipt_boundary", "product_trace_created_action_commit_packet_count"), 1, "supplier_water_filter_source_business_outcome_mismatch"),
        (("transition_cards",), (), "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "step_id"), "changed", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "evidence_id"), "", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "evidence_id"), "forged:evidence", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "actor_or_module"), "forged actor", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "api_like_call"), "forged call", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "input_summary"), "forged input", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "output_summary"), "forged output", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "meaning"), "forged meaning", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "next_step"), "wrong", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "trace_id"), "wrong", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "does_not_authorize"), "", "supplier_water_filter_source_geometry_mismatch"),
        (("transition_cards", 0, "does_not_authorize"), "authorizes payment", "supplier_water_filter_source_geometry_mismatch"),
        (("fractal_branches",), (), "supplier_water_filter_source_geometry_mismatch"),
        (("fractal_branches", 1, "branch_id"), "warehouse_branch", "supplier_water_filter_source_geometry_mismatch"),
        (("fractal_branches", 0, "branch_result_proposal"), "forged_result_proposal", "supplier_water_filter_source_geometry_mismatch"),
        (("fractal_branches", 0, "branch_called_llm_or_slm_count"), 1, "supplier_water_filter_source_geometry_mismatch"),
        (("fractal_branches", 0, "branch_real_world_effects_count"), 1, "supplier_water_filter_source_geometry_mismatch"),
        (("branch_result_proposals",), (), "supplier_water_filter_source_geometry_mismatch"),
        (("branch_result_proposals", 0, "result_proposal_id"), "forged_result_proposal", "supplier_water_filter_source_geometry_mismatch"),
        (("branch_result_proposals", 0, "source_branch_id"), "supplier_a_branch", "supplier_water_filter_source_geometry_mismatch"),
        (("branch_result_proposals", 0, "authority_claimed"), True, "supplier_water_filter_source_geometry_mismatch"),
        (("branch_result_proposals", 0, "action_permission_claimed"), True, "supplier_water_filter_source_geometry_mismatch"),
        (("branch_result_proposals", 0, "final_output_claimed"), True, "supplier_water_filter_source_geometry_mismatch"),
        (("drs_v0_2_resolve", "drs_v0_2_status"), "FAIL_CLOSED", "supplier_water_filter_source_business_outcome_mismatch"),
        (("drs_v0_2_resolve", "records_evaluated_count"), 10, "supplier_water_filter_source_business_outcome_mismatch"),
        (("drs_v0_2_resolve", "direct_reuse_allowed_count"), 1, "supplier_water_filter_source_business_outcome_mismatch"),
        (("avf_v0_2_evaluation", "avf_v0_2_status"), "FAIL_CLOSED", "supplier_water_filter_source_business_outcome_mismatch"),
        (("avf_v0_2_evaluation", "candidates_evaluated_count"), 8, "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "root_created"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "accepted_for_mock_corridor"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "mock_bank_sandbox_executed"), True, "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "allowed_subjects"), ("supplier_a_adriatic_filters", "supplier_b_balkan_pumps"), "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "forbidden_subjects"), ("shipment_sh_2042",), "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "allowed_actions"), ("mock_supplier_a_payment_intent", "mock_supplier_a_payment_order", "shipment_release"), "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "forbidden_actions"), ("supplier_b_payment", "real_payment", "real_bank_transfer"), "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "allowed_adapters"), ("mock_bank_sandbox", "bank_a_mock", "real_bank"), "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "forbidden_adapters"), ("real_supplier_api", "real_warehouse_api"), "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "payment_slot_ref"), "payment_slot:forged", "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "creditor_ref"), "supplier_b_balkan_pumps", "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "amount"), "9999.00", "supplier_water_filter_source_business_outcome_mismatch"),
        (("action_commit_packet_v0_2_integration", "currency"), "USD", "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "receipt_validated"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "receipt_permission_created"), True, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "receipt_authorizes_supplier_b"), True, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "receipt_releases_shipment"), True, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "supplier_b_excluded"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "shipment_release_excluded"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "real_bank_excluded"), False, "supplier_water_filter_source_business_outcome_mismatch"),
        (("mock_bank_sandbox_v0_2_corridor_execution", "real_payment_executed"), True, "supplier_water_filter_source_business_outcome_mismatch"),
        (("counters", "action_commit_packet_v0_2_created_by_root_count"), 0, "supplier_water_filter_source_business_outcome_mismatch"),
        (("counters", "action_commit_packet_v0_2_created_by_llm_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
        (("counters", "action_commit_packet_v0_2_supplier_b_scope_allowed_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
        (("counters", "mock_bank_sandbox_v0_2_real_bank_api_called_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
        (("counters", "mock_bank_sandbox_v0_2_provider_called_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
        (("counters", "mock_bank_sandbox_v0_2_network_called_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
        (("counters", "mock_bank_sandbox_v0_2_gemini_called_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
        (("counters", "real_world_effects_count"), 1, "supplier_water_filter_effect_creation_forbidden"),
    ),
)
def test_source_mutation_fails_closed(source_report, path, value, expected_reason):
    changed = _mutated(source_report, path, value)
    errors = adapter._source_report_errors(changed)
    assert expected_reason in errors
    assert "supplier_water_filter_source_report_hash_mismatch" in errors
    assert "supplier_water_filter_unexpected_exception" not in errors
    with pytest.raises(ValueError):
        adapter.build_supplier_water_filter_kernel_adapter_result_v01(
            source_report=changed
        )


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("business_modules", 0, "does_not_authorize"), "shipment release authorized"),
        (("business_modules", 5, "llm_visible_raw_iban"), True),
        (("runtime_plan", "plan_graph_is_authority"), True),
        (("runtime_plan", "provider_owned_plangraph_count"), 1),
        (("fractal_branches", 0, "branch_authority_boundary"), "branch creates permission"),
        (("branch_result_proposals", 0, "evidence_summary"), "Supplier B payment approved"),
        (("counters", "llm_visible_secret_count"), 1),
        (("counters", "plan_graph_authority_count"), 1),
        (("forged_authority_claim",), True),
        (("action_commit_packet_v0_2_integration", "real_payment_authorized"), True),
        (("mock_bank_sandbox_v0_2_corridor_execution", "shipment_released"), True),
    ),
)
def test_complete_source_hash_rejects_unbound_or_additional_fields(
    source_report, path, value
):
    changed = _mutated(source_report, path, value)
    errors = adapter._source_report_errors(changed)
    assert "supplier_water_filter_source_report_hash_mismatch" in errors
    assert "supplier_water_filter_unexpected_exception" not in errors
    with pytest.raises(ValueError):
        adapter.build_supplier_water_filter_kernel_adapter_result_v01(
            source_report=changed
        )


def test_complete_hash_preserves_existing_detailed_diagnostic(source_report):
    changed = _mutated(source_report, ("run_id",), "forged_run")
    errors = adapter._source_report_errors(changed)
    assert errors[0] == "supplier_water_filter_source_identity_mismatch"
    assert "supplier_water_filter_source_report_hash_mismatch" in errors
    assert "supplier_water_filter_unexpected_exception" not in errors


def test_frozen_source_card_hashes_and_evidence_order_are_exact(source_report):
    cards = source_report["transition_cards"]
    assert tuple(adapter._source_card_hash(card) for card in cards) == (
        adapter._EXPECTED_SOURCE_CARD_HASHES
    )
    assert tuple(card["evidence_id"] for card in cards) == (
        adapter._EXPECTED_EVIDENCE_IDS
    )
    assert adapter._EXPECTED_EVIDENCE_IDS[9] == adapter._EXPECTED_EVIDENCE_IDS[10]


def test_reordered_branch_rows_fail_closed(source_report):
    changed = copy.deepcopy(source_report)
    branches = changed["fractal_branches"]
    changed["fractal_branches"] = (branches[1], branches[0], *branches[2:])
    errors = adapter._source_report_errors(changed)
    assert "supplier_water_filter_source_geometry_mismatch" in errors
    with pytest.raises(ValueError):
        adapter.build_supplier_water_filter_kernel_adapter_result_v01(
            source_report=changed
        )


def test_reordered_result_proposals_fail_closed(source_report):
    changed = copy.deepcopy(source_report)
    proposals = changed["branch_result_proposals"]
    changed["branch_result_proposals"] = (
        proposals[1],
        proposals[0],
        *proposals[2:],
    )
    errors = adapter._source_report_errors(changed)
    assert "supplier_water_filter_source_geometry_mismatch" in errors


@pytest.mark.parametrize(("index", "mapping"), enumerate(adapter._STEP_MAPPING))
def test_exact_artifact_mapping(result, index, mapping):
    step_id, artifact_type, authority, lifecycle = mapping
    artifact = result.kernel_artifacts[index]
    plain = abi.kernel_artifact_to_plain_dict_v01(artifact)
    assert artifact.artifact_id == f"supplier_water_filter_artifact:{index + 1:02d}:{step_id}"
    assert artifact.artifact_type == artifact_type
    assert artifact.authority_class == authority
    assert artifact.lifecycle_state == lifecycle
    assert artifact.source_component == f"{adapter.MODULE_ID}:{step_id}"
    assert artifact.parent_refs == (() if index == 0 else (result.kernel_artifacts[index - 1].artifact_id,))
    assert artifact.trace_refs[:2] == (
        f"source_run:{adapter.SOURCE_RUN_ID}",
        f"source_report:{adapter.SOURCE_REPORT_ID}",
    )
    assert set(plain["payload"]) == adapter._PAYLOAD_KEYS
    assert plain["payload"]["source_index"] == index


def test_generic_manifest_and_replay_geometry(result):
    manifest = result.kernel_manifest
    assert (manifest.artifact_count, manifest.dependency_edge_count) == (23, 22)
    assert manifest.root_ownership_binding_count == 23
    assert manifest.evidence_class_binding_count == 23
    assert manifest.authority_class_binding_count == 23
    assert result.kernel_unanchored_verification.verification_status == integrity.STATUS_SELF_CONSISTENT_UNANCHORED
    assert result.kernel_anchored_verification.verification_status == "PASS"
    assert result.kernel_replay.replay_status == "PASS"
    assert result.kernel_replay.integrity_verified
    assert result.kernel_replay.continuity_verified
    assert result.kernel_replay.root_ownership_verified
    assert result.kernel_replay.evidence_classes_verified
    assert result.kernel_replay.authority_classes_verified


def test_coherent_wrong_source_card_hash_fails_standalone_projection(result):
    first_plain = abi.kernel_artifact_to_plain_dict_v01(result.kernel_artifacts[0])
    forged_payload = dict(first_plain["payload"])
    forged_payload["source_card_hash"] = "0" * 64
    forged_first = _rebuild_artifact(
        result.kernel_artifacts[0], payload=forged_payload
    )
    changed = _rebuild_result_integrity(
        result, (forged_first, *result.kernel_artifacts[1:])
    )
    assert changed.kernel_unanchored_verification.verification_status == (
        integrity.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert changed.kernel_anchored_verification.verification_status == "PASS"
    assert changed.kernel_replay.replay_status == "PASS"
    errors = adapter._result_structure_errors(changed)
    assert "supplier_water_filter_artifact_projection_invalid" in errors
    with pytest.raises(
        ValueError, match="^supplier_water_filter_kernel_adapter_invalid$"
    ) as exc_info:
        adapter.supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(
            changed
        )
    assert exc_info.value.__cause__ is None


def test_trace_evidence_ref_must_match_payload_evidence_id(result):
    artifact = result.kernel_artifacts[2]
    changed_artifact = _rebuild_artifact(
        artifact,
        trace_refs=(*artifact.trace_refs[:2], "source_evidence:forged:evidence"),
    )
    artifacts = (
        *result.kernel_artifacts[:2],
        changed_artifact,
        *result.kernel_artifacts[3:],
    )
    changed = _rebuild_result_integrity(result, artifacts)
    assert "supplier_water_filter_artifact_projection_invalid" in (
        adapter._result_structure_errors(changed)
    )


def test_different_valid_mixed_root_decision_fails_standalone(result):
    decision = _rebuild_supplier_decision(
        result,
        reason_code="held:different_but_structurally_valid_reason",
    )
    changed = _rebuild_result_multiroot(result, decision)
    assert changed.multiroot_validation.final_status == multiroot.STATUS_MIXED
    assert "supplier_water_filter_multiroot_invalid" in (
        adapter._result_structure_errors(changed)
    )


def test_reordered_multiroot_evidence_refs_fail_standalone(result):
    evidence_refs = result.multiroot_outcome.root_decisions[0].evidence_refs
    decision = _rebuild_supplier_decision(
        result,
        evidence_refs=tuple(reversed(evidence_refs)),
    )
    changed = _rebuild_result_multiroot(result, decision)
    assert changed.multiroot_validation.final_status == multiroot.STATUS_MIXED
    assert "supplier_water_filter_multiroot_invalid" in (
        adapter._result_structure_errors(changed)
    )


@pytest.mark.parametrize("index", range(adapter.DEPENDENCY_EDGE_COUNT))
def test_exact_causal_rows(result, index):
    source = result.kernel_artifacts[index]
    downstream = result.kernel_artifacts[index + 1]
    ref = result.causal_consumption_refs[index]
    assert ref.source_artifact_id == source.artifact_id
    assert ref.downstream_artifact_id == downstream.artifact_id
    assert ref.producer_actor_id == source.source_component
    assert ref.consumer_component == downstream.source_component
    assert ref.output_field == "/source_card_hash"
    assert ref.decision_effect == "ordered_transition_card_continuity"
    assert ref.disposition == "USED"
    assert ref.reason_code == "used:supplier_water_filter_ordered_trace_hash"
    assert ref.trace_refs == (adapter.SOURCE_REPORT_ID, source.artifact_id, downstream.artifact_id)


def test_causal_bundle_validates(result):
    assert not abi.validate_causal_consumption_bundle_v01(
        artifacts=result.kernel_artifacts,
        causal_refs=result.causal_consumption_refs,
    )


@pytest.mark.parametrize("mutation", ("reverse", "wrong_pointer", "wrong_consumer", "reverse_row"))
def test_self_rehashed_causal_mutations_are_rejected(source_report, result, mutation):
    refs = result.causal_consumption_refs
    if mutation == "reverse":
        changed_refs = tuple(reversed(refs))
    elif mutation == "wrong_pointer":
        changed_refs = (replace(refs[0], output_field="/meaning"), *refs[1:])
    elif mutation == "wrong_consumer":
        changed_refs = (replace(refs[0], consumer_component=refs[0].producer_actor_id), *refs[1:])
    else:
        changed_refs = (
            replace(
                refs[0],
                source_artifact_id=refs[0].downstream_artifact_id,
                downstream_artifact_id=refs[0].source_artifact_id,
            ),
            *refs[1:],
        )
    changed = replace(result, causal_consumption_refs=changed_refs)
    try:
        changed = replace(changed, adapter_id=adapter._adapter_id(changed))
    except ValueError:
        pass
    errors = adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report, result=changed
    )
    assert "supplier_water_filter_causal_projection_invalid" in errors


def test_duplicate_causal_ref_is_rejected_semantically(source_report, result):
    changed = replace(
        result,
        causal_consumption_refs=(result.causal_consumption_refs[0],) * 2
        + result.causal_consumption_refs[2:],
    )
    errors = adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report, result=changed
    )
    assert "supplier_water_filter_causal_projection_invalid" in errors
    assert errors != ("supplier_water_filter_adapter_id_mismatch",)


def test_multiroot_business_outcome_remains_mixed(result):
    outcome = result.multiroot_outcome
    validation = result.multiroot_validation
    assert outcome.expected_root_ids == (adapter.OWNER_ROOT_ID,)
    assert len(outcome.root_decisions) == 1
    assert outcome.root_decisions[0].outcome_class == "HELD"
    assert outcome.outcome_status == multiroot.STATUS_MIXED
    assert outcome.mixed_outcomes_visible
    assert outcome.accepted_root_ids == ()
    assert outcome.non_accepted_root_ids == (adapter.OWNER_ROOT_ID,)
    assert validation.final_status == multiroot.STATUS_MIXED
    assert validation.errors == ()
    assert validation.unknown_root_ids == ()
    assert validation.duplicate_root_ids == ()
    assert validation.missing_root_ids == ()


def test_forged_multiroot_pass_is_rejected(source_report, result):
    forged = replace(
        result.multiroot_outcome,
        outcome_status=multiroot.STATUS_PASS,
        mixed_outcomes_visible=False,
        accepted_root_ids=(adapter.OWNER_ROOT_ID,),
        non_accepted_root_ids=(),
    )
    changed = replace(result, multiroot_outcome=forged)
    errors = adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report, result=changed
    )
    assert "supplier_water_filter_multiroot_invalid" in errors


def _result_mutation(result, field_name):
    if field_name == "adapter_id":
        return replace(result, adapter_id="0" * 64)
    value = getattr(result, field_name)
    if isinstance(value, str):
        return replace(result, **{field_name: value + ":changed"})
    if type(value) is int:
        return replace(result, **{field_name: value + 1})
    if field_name == "kernel_artifacts":
        return replace(result, kernel_artifacts=tuple(reversed(value)))
    if field_name == "kernel_manifest":
        return replace(result, kernel_manifest=replace(value, transaction_id="changed"))
    if field_name in {"kernel_unanchored_verification", "kernel_anchored_verification"}:
        return replace(result, **{field_name: replace(value, verification_status="BLOCKED_FAIL_CLOSED")})
    if field_name == "kernel_replay":
        return replace(result, kernel_replay=replace(value, replay_status="BLOCKED_FAIL_CLOSED"))
    if field_name == "causal_consumption_refs":
        return replace(result, causal_consumption_refs=tuple(reversed(value)))
    if field_name == "multiroot_outcome":
        return replace(result, multiroot_outcome=replace(value, outcome_status="PASS"))
    if field_name == "multiroot_validation":
        return replace(result, multiroot_validation=replace(value, final_status="PASS"))
    raise AssertionError(field_name)


@pytest.mark.parametrize("field_name", EXPECTED_FIELDS)
def test_all_result_fields_participate_in_validation(source_report, result, field_name):
    changed = _result_mutation(result, field_name)
    errors = adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source_report, result=changed
    )
    assert errors
    assert "supplier_water_filter_unexpected_exception" not in errors
    if field_name != "adapter_id":
        assert errors != ("supplier_water_filter_adapter_id_mismatch",)


def test_projection_is_json_safe_and_independent(result):
    projection = adapter.supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(result)
    assert not _contains_forbidden_projection_value(projection)
    integrity.canonical_json_bytes_v01(projection)
    projection["kernel_artifacts"][0]["payload"]["meaning"] = "changed"
    assert adapter.supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(result) != projection


def test_builds_are_deterministic_and_source_is_unchanged(source_report):
    before = copy.deepcopy(source_report)
    first = adapter.build_supplier_water_filter_kernel_adapter_result_v01(source_report=source_report)
    second = adapter.build_supplier_water_filter_kernel_adapter_result_v01(source_report=source_report)
    assert first == second
    assert first.adapter_id == second.adapter_id
    assert adapter.supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(first) == adapter.supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(second)
    assert source_report == before


@pytest.mark.parametrize(
    "forbidden_import",
    (
        "demo",
        "tests",
        "hedgehog.domains.airline",
        "action_commit_packet",
        "effect_firewall",
        "provider",
        "gemini",
        "config",
        "os",
        "pathlib",
        "tempfile",
        "shutil",
        "subprocess",
        "socket",
        "requests",
        "urllib",
    ),
)
def test_production_import_boundary(forbidden_import):
    path = Path(adapter.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert not any(
        name == forbidden_import or name.startswith(forbidden_import + ".")
        for name in imports
    )


@pytest.mark.parametrize(
    "forbidden_call",
    ("open", "read", "write", "getenv", "environ", "register_adapter", "execute_real_effect"),
)
def test_production_has_no_forbidden_call(forbidden_call):
    tree = ast.parse(Path(adapter.__file__).read_text(encoding="utf-8"))
    names = tuple(
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    )
    attributes = tuple(
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    )
    assert forbidden_call not in names
    assert forbidden_call not in attributes
