"""Pure Supplier / Water Filter mapping into shared sealed-evidence contracts.

The adapter consumes an already-validated safe live projection, nine explicit
normalized deterministic scenario rows, one already-collected deterministic
product-trace report, and its frozen Gate-1 Supplier Kernel result. It binds
existing evidence only. It performs no provider, network, Gemini, filesystem,
package, Anchor, Replay-runner, collector, demo, authority, permission, action,
receipt, FinalOutput, or effect operation. MIXED remains visible and PASS is
derived; neither hashes nor this mapping establish semantic truth or production
certification.
"""

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
import re as _re

from hedgehog.domains.supplier_water_filter.kernel_adapter_v01 import (
    BUSINESS_MODULE_COUNT as _BUSINESS_MODULE_COUNT,
    CROSS_ROOT_EVIDENCE_COUNT as _CROSS_ROOT_EVIDENCE_COUNT,
    DEPENDENCY_EDGE_COUNT as _DEPENDENCY_EDGE_COUNT,
    FRACTAL_BRANCH_COUNT as _FRACTAL_BRANCH_COUNT,
    RECEIPT_STATUS as _KERNEL_RECEIPT_STATUS,
    RESULT_PROPOSAL_COUNT as _RESULT_PROPOSAL_COUNT,
    ROOT_DECISION_COUNT as _ROOT_DECISION_COUNT,
    SHIPMENT_STATUS as _KERNEL_SHIPMENT_STATUS,
    SOURCE_REPORT_ID as _SOURCE_REPORT_ID,
    SOURCE_RUN_ID as _SOURCE_RUN_ID,
    SOURCE_TRACE_TYPE as _SOURCE_TRACE_TYPE,
    SUPPLIER_A_STATUS as _KERNEL_SUPPLIER_A_STATUS,
    SUPPLIER_B_STATUS as _KERNEL_SUPPLIER_B_STATUS,
    TRANSACTION_ID as _TRANSACTION_ID,
    TRANSITION_CARD_COUNT as _TRANSITION_CARD_COUNT,
    SupplierWaterFilterKernelAdapterResultV01 as _SupplierKernelResultV01,
    supplier_water_filter_kernel_adapter_result_to_plain_dict_v01 as _kernel_result_plain_v01,
    validate_supplier_water_filter_kernel_adapter_result_v01 as _validate_kernel_result_v01,
)
from hedgehog.domains.supplier_water_filter.live_evidence_adapter_v01 import (
    STATUS_PASS as _LIVE_STATUS_PASS,
    SupplierWaterFilterSafeExecutionProjectionV01 as _SupplierSafeExecutionV01,
    supplier_water_filter_safe_execution_projection_to_plain_dict_v01 as _safe_execution_plain_v01,
    validate_supplier_water_filter_safe_execution_projection_v01 as _validate_safe_execution_v01,
)
from hedgehog.evidence.sealed_evidence_profile_v01 import (
    DomainEvidenceProjectionV01 as _DomainEvidenceProjectionV01,
    STATUS_PASS as _PROFILE_STATUS_PASS,
    build_domain_evidence_projection_v01 as _build_domain_projection_v01,
    build_domain_execution_identity_v01 as _build_domain_execution_identity_v01,
    build_evidence_artifact_record_v01 as _build_artifact_record_v01,
    build_live_attempt_identity_v01 as _build_live_attempt_identity_v01,
    build_programme_evidence_identity_v01 as _build_programme_identity_v01,
    build_safe_source_record_v01 as _build_safe_source_record_v01,
    domain_evidence_projection_to_plain_dict_v01 as _domain_projection_plain_v01,
    validate_domain_evidence_projection_v01 as _validate_domain_projection_v01,
)
from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01 as _CausalConsumptionRefV01,
    KernelArtifactV01 as _KernelArtifactV01,
    kernel_artifact_to_plain_dict_v01 as _kernel_artifact_plain_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    CanonicalArtifactRefV01 as _CanonicalArtifactRefV01,
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.multiroot_v01 import (
    transaction_outcome_envelope_to_plain_dict_v01 as _multiroot_outcome_plain_v01,
)


MODULE_ID = "supplier_water_filter_sealed_evidence_package_adapter_v01"
ADAPTER_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
ADAPTER_STATUSES = (STATUS_PASS, STATUS_FAIL_CLOSED)

PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
PROGRAMME_VERSION = "v0.1"
DOMAIN_ID = "supplier_water_filter"
SCENARIO_COUNT = 9
SOURCE_RECORD_COUNT = 7
ARTIFACT_RECORD_COUNT = 23
KERNEL_ARTIFACT_REF_COUNT = 23
CAUSAL_REF_COUNT = 22
MULTIROOT_OUTCOME = "MIXED"
TECHNICAL_CONFORMANCE_STATUS = "PASS"
BUSINESS_OUTCOME = "MIXED"
SUPPLIER_A_MOCK_PAYMENT_STATUS = "PASS"

SCENARIO_IDS = (
    "S-N1",
    "S-N2",
    "S-C1",
    "S-P1",
    "S-P2",
    "S-F1",
    "S-F2",
    "S-F3",
    "S-M1",
)
SCENARIO_NAMES = (
    "initial_business_blockers_root_not_ready",
    "unsafe_live_evidence_fail_closed",
    "corrected_evidence_validation_rerun",
    "supplier_a_scoped_human_approval",
    "supplier_a_mock_bank_happy_path",
    "no_human_approval_blocks_action",
    "packet_and_corridor_mutation_matrix",
    "receipt_attack_matrix",
    "integrated_mixed_business_outcome",
)

_RESULT_ID_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.sealed_evidence_adapter_result.v01"
)
_SCENARIO_INDEX_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.scenario_index.v01"
)
_SCENARIO_ROW_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.scenario_row.v01"
)
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_SCENARIO_KEYS = frozenset(
    (
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
)
_SCENARIO_SPECS = (
    (
        "S-N1",
        "initial_business_blockers_root_not_ready",
        "deterministic_initial_business_evidence",
        "PASS",
        "NOT_READY",
        "NOT_READY",
        "BLOCKED_PENDING_CORRECTION",
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-N2",
        "unsafe_live_evidence_fail_closed",
        "live_bound_negative_safe_projection",
        "FAIL_CLOSED",
        "NOT_READY",
        "NO_ACCEPTED_NEW_ROOT_FINAL",
        "BLOCKED_PENDING_CORRECTION",
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-C1",
        "corrected_evidence_validation_rerun",
        "deterministic_corrected_evidence",
        "PASS",
        "MIXED",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-P1",
        "supplier_a_scoped_human_approval",
        "deterministic_owner_approval",
        "PASS",
        "MIXED",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "APPROVED_SCOPE_ONLY",
        "ROOT_CREATED_SCOPED",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-P2",
        "supplier_a_mock_bank_happy_path",
        "live_bound_deterministic_corridor",
        "PASS",
        "MIXED",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "PASS",
        "VALID_SCOPED",
        "PASS",
        "EVIDENCE_ONLY",
    ),
    (
        "S-F1",
        "no_human_approval_blocks_action",
        "deterministic_policy_probe",
        "FAIL_CLOSED",
        "NOT_READY",
        "NO_ACTION_APPROVAL",
        "NOT_EXECUTED",
        "REJECTED",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-F2",
        "packet_and_corridor_mutation_matrix",
        "deterministic_packet_corridor_mutation",
        "FAIL_CLOSED",
        "MIXED",
        "NO_WIDENED_ROOT_DECISION",
        "UNCHANGED",
        "REJECTED",
        "REJECTED",
        "ABSENT",
    ),
    (
        "S-F3",
        "receipt_attack_matrix",
        "deterministic_receipt_attack",
        "FAIL_CLOSED",
        "MIXED",
        "NO_NEW_PERMISSION",
        "UNCHANGED",
        "UNCHANGED",
        "NO_NEW_EXECUTION",
        "ATTACK_REJECTED",
    ),
    (
        "S-M1",
        "integrated_mixed_business_outcome",
        "deterministic_integrated_outcome",
        "PASS",
        "MIXED",
        "HELD",
        "PASS",
        "VALID_SCOPED",
        "PASS",
        "EVIDENCE_ONLY",
    ),
)
_LIMITATIONS = (
    "limitation:owner_normalized_supplier_live_projection",
    "limitation:no_new_live_collection_during_r1",
    "limitation:deterministic_supplier_scenarios_are_not_provider_observations",
    "limitation:supplier_a_mock_payment_only",
    "limitation:supplier_b_blocked",
    "limitation:shipment_held",
    "limitation:receipt_evidence_only",
    "limitation:business_outcome_mixed",
    "limitation:no_real_payment_or_shipment",
    "limitation:no_package_anchor_or_replay_execution",
    "limitation:no_production_certification",
)
_KERNEL_STEP_IDS = (
    "dirty_request_received",
    "warehouse_inventory_query",
    "supplier_a_availability_query",
    "supplier_b_blocker_query",
    "legal_insurance_contract_check",
    "accounting_invoice_po_reconciliation",
    "bank_a_payment_slot_prepared",
    "bank_b_native_contract_preview",
    "top_level_semantic_route_observed_from_v1_1",
    "bsep_membrane_observed_from_v1_1",
    "top_level_live_semantic_architect_observed_from_v1_1",
    "runtime_plangraph_compiled",
    "fractal_branch_cells_dispatched",
    "branch_result_proposals_collected",
    "post_vv_validated",
    "gt_lgt_advisory_review",
    "root_first_not_ready",
    "corrected_evidence_received",
    "root_second_supplier_a_scoped_review",
    "human_approval_supplier_a_only",
    "root_created_mock_action_commit_packet_observed",
    "mock_bank_sandbox_receipt_observed",
    "final_state_summary",
)
_ARTIFACT_EVIDENCE_CLASSES = {
    "dirty_request_received": "NEGATIVE_CONFORMANCE",
    "supplier_b_blocker_query": "NEGATIVE_CONFORMANCE",
    "root_first_not_ready": "ROOT_DECISION_EVIDENCE",
    "root_second_supplier_a_scoped_review": "ROOT_DECISION_EVIDENCE",
    "final_state_summary": "ROOT_DECISION_EVIDENCE",
    "human_approval_supplier_a_only": "CORRIDOR_EVIDENCE",
    "root_created_mock_action_commit_packet_observed": "CORRIDOR_EVIDENCE",
    "mock_bank_sandbox_receipt_observed": "CORRIDOR_EVIDENCE",
}


@_dataclass(frozen=True, slots=True)
class SupplierWaterFilterSealedEvidencePackageAdapterResultV01:
    adapter_result_id: str
    adapter_version: str
    safe_execution_id: str
    scenario_index_id: str
    scenario_ids: tuple[str, ...]
    scenario_names: tuple[str, ...]
    scenario_classifications: tuple[str, ...]
    scenario_row_hashes: tuple[str, ...]
    scenario_technical_statuses: tuple[str, ...]
    scenario_business_outcomes: tuple[str, ...]
    source_run_id: str
    source_report_id: str
    source_trace_type: str
    transaction_id: str
    kernel_adapter_id: str
    kernel_manifest_hash: str
    multiroot_outcome_id: str
    multiroot_outcome: str
    supplier_a_status: str
    supplier_a_mock_payment_status: str
    supplier_b_status: str
    shipment_status: str
    receipt_status: str
    technical_conformance_status: str
    business_outcome: str
    real_payment_executed: bool
    real_shipment_released: bool
    domain_projection: _DomainEvidenceProjectionV01
    scenario_count: int
    source_record_count: int
    artifact_record_count: int
    kernel_artifact_ref_count: int
    causal_ref_count: int
    business_module_count: int
    fractal_branch_count: int
    result_proposal_count: int
    root_decision_count: int
    cross_root_evidence_count: int
    adapter_provider_call_count: int
    adapter_network_call_count: int
    adapter_gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    action_created_count: int
    receipt_created_count: int
    final_output_created_count: int
    real_world_effects_count: int
    validation_errors: tuple[str, ...]
    status: str

    def __post_init__(self) -> None:
        tuples = (
            self.scenario_ids,
            self.scenario_names,
            self.scenario_classifications,
            self.scenario_row_hashes,
            self.scenario_technical_statuses,
            self.scenario_business_outcomes,
            self.validation_errors,
        )
        if any(type(value) is not tuple for value in tuples):
            raise ValueError("supplier_water_filter_sealed_evidence_adapter_invalid")


def build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
    *,
    safe_execution: _SupplierSafeExecutionV01,
    scenario_rows: tuple[_Mapping[str, object], ...],
    source_report: _Mapping[str, object],
    kernel_adapter_result: _SupplierKernelResultV01,
) -> SupplierWaterFilterSealedEvidencePackageAdapterResultV01:
    try:
        return _build_result(
            safe_execution=safe_execution,
            scenario_rows=scenario_rows,
            source_report=source_report,
            kernel_adapter_result=kernel_adapter_result,
        )
    except ValueError as error:
        raise ValueError(_stable_reason(error)) from None
    except Exception:
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_unexpected_exception") from None


def validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
    result: object,
    *,
    safe_execution: _SupplierSafeExecutionV01,
    scenario_rows: tuple[_Mapping[str, object], ...],
    source_report: _Mapping[str, object],
    kernel_adapter_result: _SupplierKernelResultV01,
) -> tuple[str, ...]:
    try:
        errors = list(_result_structure_errors(result))
        if type(result) is not SupplierWaterFilterSealedEvidencePackageAdapterResultV01:
            return tuple(errors)
        expected = _build_result(
            safe_execution=safe_execution,
            scenario_rows=scenario_rows,
            source_report=source_report,
            kernel_adapter_result=kernel_adapter_result,
        )
        if _canonical_json_bytes_v01(_result_plain(result)) != (
            _canonical_json_bytes_v01(_result_plain(expected))
        ):
            errors.append("supplier_water_filter_sealed_evidence_adapter_context_mismatch")
            if result.adapter_result_id != expected.adapter_result_id:
                errors.append("supplier_water_filter_sealed_evidence_adapter_identity_mismatch")
        return _dedupe(errors)
    except ValueError as error:
        return (_stable_reason(error),)
    except Exception:
        return ("supplier_water_filter_sealed_evidence_adapter_unexpected_exception",)


def supplier_water_filter_sealed_evidence_package_adapter_result_to_plain_dict_v01(
    result: SupplierWaterFilterSealedEvidencePackageAdapterResultV01,
    *,
    safe_execution: _SupplierSafeExecutionV01,
    scenario_rows: tuple[_Mapping[str, object], ...],
    source_report: _Mapping[str, object],
    kernel_adapter_result: _SupplierKernelResultV01,
) -> dict[str, object]:
    try:
        if validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
            result,
            safe_execution=safe_execution,
            scenario_rows=scenario_rows,
            source_report=source_report,
            kernel_adapter_result=kernel_adapter_result,
        ):
            raise ValueError
        projection = _result_plain(result)
        _canonical_json_bytes_v01(projection)
        return projection
    except Exception:
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_invalid") from None


def _build_result(
    *,
    safe_execution: _SupplierSafeExecutionV01,
    scenario_rows: object,
    source_report: object,
    kernel_adapter_result: object,
) -> SupplierWaterFilterSealedEvidencePackageAdapterResultV01:
    _require_context(
        safe_execution=safe_execution,
        source_report=source_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    rows = _normalize_scenario_rows(scenario_rows)
    scenario_hashes = tuple(_scenario_row_hash(item) for item in rows)
    scenario_index_id = _scenario_index_identity(rows)
    source_records = _build_source_records(
        safe_execution=safe_execution,
        rows=rows,
        scenario_index_id=scenario_index_id,
        source_report=source_report,
        kernel_result=kernel_adapter_result,
    )
    artifact_records = _build_artifact_records(
        kernel_adapter_result.kernel_artifacts,
        source_records,
    )
    programme_identity = _build_programme_identity_v01(
        programme_id=PROGRAMME_ID,
        programme_version=PROGRAMME_VERSION,
    )
    domain_identity = _build_domain_execution_identity_v01(
        programme_identity=programme_identity,
        domain_id=DOMAIN_ID,
        execution_head=safe_execution.execution_head,
        source_task_id=safe_execution.source_task_id,
        run_id=safe_execution.run_id,
        report_id=safe_execution.report_id,
    )
    attempt_identity = _build_live_attempt_identity_v01(
        programme_identity=programme_identity,
        domain_execution_identity=domain_identity,
        attempt_number=1,
        package_id=f"supplier-water-filter:{safe_execution.run_id}",
        logical_package_ref=f"supplier_water_filter/{safe_execution.run_id}",
        output_directory_ref=(
            f"supplier_water_filter/{safe_execution.run_id}/sealed_package"
        ),
        provider_mode=safe_execution.provider_mode,
        model_id=safe_execution.model_id,
        expected_actor_count=6,
        provider_call_budget=6,
    )
    evidence_refs = (
        f"safe_execution:{safe_execution.safe_execution_id}",
        f"scenario_index:{scenario_index_id}",
        f"kernel_adapter:{kernel_adapter_result.adapter_id}",
        f"kernel_manifest:{kernel_adapter_result.kernel_manifest.manifest_hash}",
        f"multiroot:{kernel_adapter_result.multiroot_outcome.outcome_id}",
        *(item["evidence_refs"][0] for item in rows),
    )
    domain_projection = _build_domain_projection_v01(
        programme_identity=programme_identity,
        domain_execution_identity=domain_identity,
        attempt_identity=attempt_identity,
        source_records=source_records,
        artifact_records=artifact_records,
        kernel_artifact_refs=kernel_adapter_result.kernel_manifest.artifacts,
        causal_consumption_refs=kernel_adapter_result.causal_consumption_refs,
        evidence_refs=evidence_refs,
        limitation_refs=_LIMITATIONS,
    )
    if (
        _validate_domain_projection_v01(domain_projection)
        or domain_projection.status != _PROFILE_STATUS_PASS
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_projection_invalid")

    provisional = SupplierWaterFilterSealedEvidencePackageAdapterResultV01(
        adapter_result_id="0" * 64,
        adapter_version=ADAPTER_VERSION,
        safe_execution_id=safe_execution.safe_execution_id,
        scenario_index_id=scenario_index_id,
        scenario_ids=tuple(item["scenario_id"] for item in rows),
        scenario_names=tuple(item["scenario_name"] for item in rows),
        scenario_classifications=tuple(item["classification"] for item in rows),
        scenario_row_hashes=scenario_hashes,
        scenario_technical_statuses=tuple(
            item["technical_status"] for item in rows
        ),
        scenario_business_outcomes=tuple(
            item["business_outcome"] for item in rows
        ),
        source_run_id=kernel_adapter_result.source_run_id,
        source_report_id=kernel_adapter_result.source_report_id,
        source_trace_type=kernel_adapter_result.source_trace_type,
        transaction_id=kernel_adapter_result.transaction_id,
        kernel_adapter_id=kernel_adapter_result.adapter_id,
        kernel_manifest_hash=kernel_adapter_result.kernel_manifest.manifest_hash,
        multiroot_outcome_id=kernel_adapter_result.multiroot_outcome.outcome_id,
        multiroot_outcome=kernel_adapter_result.multiroot_outcome.outcome_status,
        supplier_a_status=kernel_adapter_result.supplier_a_status,
        supplier_a_mock_payment_status=SUPPLIER_A_MOCK_PAYMENT_STATUS,
        supplier_b_status=kernel_adapter_result.supplier_b_status,
        shipment_status=kernel_adapter_result.shipment_status,
        receipt_status=kernel_adapter_result.receipt_status,
        technical_conformance_status=TECHNICAL_CONFORMANCE_STATUS,
        business_outcome=BUSINESS_OUTCOME,
        real_payment_executed=False,
        real_shipment_released=False,
        domain_projection=domain_projection,
        scenario_count=SCENARIO_COUNT,
        source_record_count=len(source_records),
        artifact_record_count=len(artifact_records),
        kernel_artifact_ref_count=len(
            kernel_adapter_result.kernel_manifest.artifacts
        ),
        causal_ref_count=len(kernel_adapter_result.causal_consumption_refs),
        business_module_count=kernel_adapter_result.business_module_count,
        fractal_branch_count=kernel_adapter_result.fractal_branch_count,
        result_proposal_count=kernel_adapter_result.result_proposal_count,
        root_decision_count=len(
            kernel_adapter_result.multiroot_outcome.root_decisions
        ),
        cross_root_evidence_count=len(
            kernel_adapter_result.multiroot_outcome.cross_root_evidence_refs
        ),
        adapter_provider_call_count=0,
        adapter_network_call_count=0,
        adapter_gemini_call_count=0,
        created_authority_count=0,
        created_permission_count=0,
        action_created_count=0,
        receipt_created_count=0,
        final_output_created_count=0,
        real_world_effects_count=0,
        validation_errors=(),
        status=STATUS_PASS,
    )
    result = _replace_result_id(provisional, _result_identity(provisional))
    errors = _result_structure_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def _require_context(
    *,
    safe_execution: object,
    source_report: object,
    kernel_adapter_result: object,
) -> None:
    if (
        type(safe_execution) is not _SupplierSafeExecutionV01
        or _validate_safe_execution_v01(safe_execution)
        or safe_execution.status != _LIVE_STATUS_PASS
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_safe_execution_invalid")
    if type(source_report) is not dict:
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_source_invalid")
    if type(kernel_adapter_result) is not _SupplierKernelResultV01:
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_kernel_invalid")
    kernel_errors = _validate_kernel_result_v01(
        source_report=source_report,
        result=kernel_adapter_result,
    )
    if kernel_errors:
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_kernel_invalid")
    manifest_refs = kernel_adapter_result.kernel_manifest.artifacts
    if (
        type(kernel_adapter_result.kernel_artifacts) is not tuple
        or len(kernel_adapter_result.kernel_artifacts) != _TRANSITION_CARD_COUNT
        or any(type(item) is not _KernelArtifactV01 for item in kernel_adapter_result.kernel_artifacts)
        or type(manifest_refs) is not tuple
        or len(manifest_refs) != KERNEL_ARTIFACT_REF_COUNT
        or any(type(item) is not _CanonicalArtifactRefV01 for item in manifest_refs)
        or tuple(item.artifact_id for item in manifest_refs)
        != tuple(item.artifact_id for item in kernel_adapter_result.kernel_artifacts)
        or type(kernel_adapter_result.causal_consumption_refs) is not tuple
        or len(kernel_adapter_result.causal_consumption_refs) != CAUSAL_REF_COUNT
        or any(
            type(item) is not _CausalConsumptionRefV01
            for item in kernel_adapter_result.causal_consumption_refs
        )
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    if (
        safe_execution.transaction_id != _TRANSACTION_ID
        or kernel_adapter_result.transaction_id != _TRANSACTION_ID
        or kernel_adapter_result.source_run_id != _SOURCE_RUN_ID
        or kernel_adapter_result.source_report_id != _SOURCE_REPORT_ID
        or kernel_adapter_result.source_trace_type != _SOURCE_TRACE_TYPE
        or source_report.get("run_id") != _SOURCE_RUN_ID
        or source_report.get("report_id") != _SOURCE_REPORT_ID
        or source_report.get("trace_type") != _SOURCE_TRACE_TYPE
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_binding_mismatch")
    if (
        kernel_adapter_result.supplier_a_status != _KERNEL_SUPPLIER_A_STATUS
        or kernel_adapter_result.supplier_b_status != _KERNEL_SUPPLIER_B_STATUS
        or kernel_adapter_result.shipment_status != _KERNEL_SHIPMENT_STATUS
        or kernel_adapter_result.receipt_status != _KERNEL_RECEIPT_STATUS
        or kernel_adapter_result.multiroot_outcome.outcome_status != MULTIROOT_OUTCOME
        or kernel_adapter_result.multiroot_validation.final_status
        != MULTIROOT_OUTCOME
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_business_outcome_mismatch")
    geometry = (
        kernel_adapter_result.business_module_count,
        kernel_adapter_result.transition_card_count,
        kernel_adapter_result.dependency_edge_count,
        kernel_adapter_result.fractal_branch_count,
        kernel_adapter_result.result_proposal_count,
        len(kernel_adapter_result.multiroot_outcome.root_decisions),
        len(kernel_adapter_result.multiroot_outcome.cross_root_evidence_refs),
    )
    if geometry != (
        _BUSINESS_MODULE_COUNT,
        _TRANSITION_CARD_COUNT,
        _DEPENDENCY_EDGE_COUNT,
        _FRACTAL_BRANCH_COUNT,
        _RESULT_PROPOSAL_COUNT,
        _ROOT_DECISION_COUNT,
        _CROSS_ROOT_EVIDENCE_COUNT,
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    operation_counts = (
        kernel_adapter_result.provider_call_count,
        kernel_adapter_result.network_call_count,
        kernel_adapter_result.gemini_call_count,
        kernel_adapter_result.real_world_effects_count,
    )
    if any(type(value) is not int or value != 0 for value in operation_counts):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_external_call_forbidden")


def _normalize_scenario_rows(value: object) -> tuple[dict[str, object], ...]:
    if type(value) is not tuple or len(value) != SCENARIO_COUNT:
        raise ValueError("supplier_water_filter_sealed_evidence_scenario_invalid")
    rows: list[dict[str, object]] = []
    for index, (item, spec) in enumerate(zip(value, _SCENARIO_SPECS, strict=True)):
        if type(item) is not dict or frozenset(item) != _SCENARIO_KEYS:
            raise ValueError("supplier_water_filter_sealed_evidence_scenario_invalid")
        row = {key: item[key] for key in item}
        expected = {
            "scenario_id": spec[0],
            "scenario_name": spec[1],
            "classification": spec[2],
            "technical_status": spec[3],
            "business_outcome": spec[4],
            "root_status": spec[5],
            "supplier_a_status": spec[6],
            "supplier_b_status": "BLOCKED",
            "shipment_status": "HELD",
            "packet_status": spec[7],
            "corridor_status": spec[8],
            "receipt_status": spec[9],
            "additional_provider_call_count": 0,
            "additional_network_call_count": 0,
            "additional_gemini_call_count": 0,
            "real_payment_executed": False,
            "real_shipment_released": False,
            "real_world_effects_count": 0,
            "evidence_refs": (f"evidence:supplier:{spec[0].casefold()}",),
        }
        if row != expected or index != SCENARIO_IDS.index(spec[0]):
            raise ValueError("supplier_water_filter_sealed_evidence_scenario_invalid")
        rows.append(row)
    return tuple(rows)


def _build_source_records(
    *,
    safe_execution: _SupplierSafeExecutionV01,
    rows: tuple[dict[str, object], ...],
    scenario_index_id: str,
    source_report: dict[str, object],
    kernel_result: _SupplierKernelResultV01,
) -> tuple[object, ...]:
    safe_plain = _safe_execution_plain_v01(safe_execution)
    kernel_plain = _kernel_result_plain_v01(kernel_result)
    multiroot_plain = _multiroot_outcome_plain_v01(kernel_result.multiroot_outcome)
    negative_rows = [
        _scenario_plain(item)
        for item in rows
        if item["technical_status"] == STATUS_FAIL_CLOSED
    ]
    common = {
        "media_type": "application/json",
        "contains_raw_prompt": False,
        "contains_raw_provider_response": False,
        "secret_scan_passed": True,
        "real_world_effects_count": 0,
    }
    records = (
        _build_safe_source_record_v01(
            source_id=f"supplier:live-runtime:{safe_execution.safe_execution_id}",
            source_type="supplier_live_execution_runtime",
            evidence_class="EXECUTED_LIVE_RUNTIME",
            canonical_projection=safe_plain,
            trace_refs=(safe_execution.safe_execution_id, safe_execution.report_id),
            observed_provider_call_count=6,
            observed_network_call_count=6,
            observed_gemini_call_count=6,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"supplier:live-safe:{safe_execution.safe_execution_id}",
            source_type="supplier_live_safe_projection",
            evidence_class="LIVE_PROVIDER_SAFE_PROJECTION",
            canonical_projection={
                "safe_execution_id": safe_execution.safe_execution_id,
                "actor_ids": list(safe_execution.actor_ids),
                "bsep_id": safe_execution.bsep_id,
            },
            trace_refs=(safe_execution.safe_execution_id, safe_execution.bsep_id),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"supplier:scenario-index:{scenario_index_id}",
            source_type="supplier_nine_scenario_index",
            evidence_class="EXECUTED_DETERMINISTIC_RUNTIME",
            canonical_projection=[_scenario_plain(item) for item in rows],
            trace_refs=(scenario_index_id, _SOURCE_REPORT_ID),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"supplier:root:{kernel_result.multiroot_outcome.outcome_id}",
            source_type="supplier_root_multiroot_evidence",
            evidence_class="ROOT_DECISION_EVIDENCE",
            canonical_projection=multiroot_plain,
            trace_refs=(
                kernel_result.multiroot_outcome.outcome_id,
                kernel_result.multiroot_validation.validation_id,
            ),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"supplier:corridor:{kernel_result.adapter_id}",
            source_type="supplier_packet_corridor_receipt_evidence",
            evidence_class="CORRIDOR_EVIDENCE",
            canonical_projection={
                "supplier_a_mock_payment_status": SUPPLIER_A_MOCK_PAYMENT_STATUS,
                "supplier_b_status": kernel_result.supplier_b_status,
                "shipment_status": kernel_result.shipment_status,
                "receipt_status": kernel_result.receipt_status,
                "real_payment_executed": False,
                "real_shipment_released": False,
                "source_report_id": source_report["report_id"],
            },
            trace_refs=(
                safe_execution.safe_execution_id,
                "evidence:supplier:s-p1",
                "evidence:supplier:s-p2",
                "evidence:supplier:s-f3",
            ),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"supplier:negative:{scenario_index_id}",
            source_type="supplier_negative_conformance_matrix",
            evidence_class="NEGATIVE_CONFORMANCE",
            canonical_projection=negative_rows,
            trace_refs=(
                safe_execution.safe_execution_id,
                "evidence:supplier:s-n2",
                "evidence:supplier:s-f1",
                "evidence:supplier:s-f2",
                "evidence:supplier:s-f3",
            ),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"supplier:integrity:{kernel_result.adapter_id}",
            source_type="supplier_kernel_cryptographic_integrity",
            evidence_class="CRYPTOGRAPHIC_INTEGRITY",
            canonical_projection={
                "kernel_adapter": kernel_plain,
                "kernel_manifest_hash": kernel_result.kernel_manifest.manifest_hash,
                "kernel_artifact_count": len(kernel_result.kernel_manifest.artifacts),
                "causal_ref_count": len(kernel_result.causal_consumption_refs),
            },
            trace_refs=(
                kernel_result.kernel_manifest.manifest_hash,
                kernel_result.adapter_id,
            ),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
    )
    return records


def _build_artifact_records(
    artifacts: tuple[_KernelArtifactV01, ...],
    source_records: tuple[object, ...],
) -> tuple[object, ...]:
    source_by_class = {item.evidence_class: item.source_record_id for item in source_records}
    records = []
    for index, artifact in enumerate(artifacts):
        step_id = _artifact_step_id(index, artifact)
        evidence_class = _artifact_evidence_class(step_id)
        source_class = evidence_class
        if source_class not in source_by_class:
            source_class = "EXECUTED_DETERMINISTIC_RUNTIME"
        records.append(
            _build_artifact_record_v01(
                artifact_id=artifact.artifact_id,
                artifact_type=artifact.artifact_type,
                evidence_class=evidence_class,
                source_record_ids=(source_by_class[source_class],),
                canonical_projection=_kernel_artifact_plain_v01(artifact),
                authority_class=artifact.authority_class,
                owner_root_id=artifact.owner_root_id,
                trace_refs=tuple(artifact.trace_refs) or (artifact.artifact_id,),
                created_authority_count=0,
                created_permission_count=0,
                real_world_effects_count=0,
            )
        )
    return tuple(records)


def _artifact_step_id(index: int, artifact: _KernelArtifactV01) -> str:
    if index >= len(_KERNEL_STEP_IDS):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    step_id = _KERNEL_STEP_IDS[index]
    expected_artifact_id = f"supplier_water_filter_artifact:{index + 1:02d}:{step_id}"
    expected_source_component = f"supplier_water_filter_kernel_adapter_v01:{step_id}"
    if (
        artifact.artifact_id != expected_artifact_id
        or artifact.source_component != expected_source_component
    ):
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    return step_id


def _artifact_evidence_class(step_id: str) -> str:
    if step_id not in _KERNEL_STEP_IDS:
        raise ValueError("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    return _ARTIFACT_EVIDENCE_CLASSES.get(
        step_id,
        "EXECUTED_DETERMINISTIC_RUNTIME",
    )


def _scenario_plain(row: dict[str, object]) -> dict[str, object]:
    return {
        "scenario_id": row["scenario_id"],
        "scenario_name": row["scenario_name"],
        "classification": row["classification"],
        "technical_status": row["technical_status"],
        "business_outcome": row["business_outcome"],
        "root_status": row["root_status"],
        "supplier_a_status": row["supplier_a_status"],
        "supplier_b_status": row["supplier_b_status"],
        "shipment_status": row["shipment_status"],
        "packet_status": row["packet_status"],
        "corridor_status": row["corridor_status"],
        "receipt_status": row["receipt_status"],
        "additional_provider_call_count": row["additional_provider_call_count"],
        "additional_network_call_count": row["additional_network_call_count"],
        "additional_gemini_call_count": row["additional_gemini_call_count"],
        "real_payment_executed": row["real_payment_executed"],
        "real_shipment_released": row["real_shipment_released"],
        "real_world_effects_count": row["real_world_effects_count"],
        "evidence_refs": list(row["evidence_refs"]),
    }


def _scenario_row_hash(row: dict[str, object]) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=_SCENARIO_ROW_DOMAIN,
        payload=_canonical_json_bytes_v01(_scenario_plain(row)),
    )


def _scenario_index_identity(rows: tuple[dict[str, object], ...]) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=_SCENARIO_INDEX_DOMAIN,
        payload=_canonical_json_bytes_v01(
            [_scenario_plain(item) for item in rows]
        ),
    )


def _result_structure_errors(result: object) -> tuple[str, ...]:
    if type(result) is not SupplierWaterFilterSealedEvidencePackageAdapterResultV01:
        return ("supplier_water_filter_sealed_evidence_adapter_invalid",)
    errors: list[str] = []
    tuple_fields = (
        result.scenario_ids,
        result.scenario_names,
        result.scenario_classifications,
        result.scenario_row_hashes,
        result.scenario_technical_statuses,
        result.scenario_business_outcomes,
        result.validation_errors,
    )
    if any(type(value) is not tuple for value in tuple_fields):
        errors.append("supplier_water_filter_sealed_evidence_adapter_invalid")
    if (
        result.adapter_version != ADAPTER_VERSION
        or result.scenario_ids != SCENARIO_IDS
        or result.scenario_names != SCENARIO_NAMES
        or len(result.scenario_classifications) != SCENARIO_COUNT
        or len(result.scenario_row_hashes) != SCENARIO_COUNT
        or any(not _valid_sha256(value) for value in result.scenario_row_hashes)
        or len(result.scenario_technical_statuses) != SCENARIO_COUNT
        or len(result.scenario_business_outcomes) != SCENARIO_COUNT
        or result.validation_errors != ()
    ):
        errors.append("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    expected_geometry = (
        SCENARIO_COUNT,
        SOURCE_RECORD_COUNT,
        ARTIFACT_RECORD_COUNT,
        KERNEL_ARTIFACT_REF_COUNT,
        CAUSAL_REF_COUNT,
        _BUSINESS_MODULE_COUNT,
        _FRACTAL_BRANCH_COUNT,
        _RESULT_PROPOSAL_COUNT,
        _ROOT_DECISION_COUNT,
        _CROSS_ROOT_EVIDENCE_COUNT,
    )
    observed_geometry = (
        result.scenario_count,
        result.source_record_count,
        result.artifact_record_count,
        result.kernel_artifact_ref_count,
        result.causal_ref_count,
        result.business_module_count,
        result.fractal_branch_count,
        result.result_proposal_count,
        result.root_decision_count,
        result.cross_root_evidence_count,
    )
    if any(type(value) is not int for value in observed_geometry) or observed_geometry != expected_geometry:
        errors.append("supplier_water_filter_sealed_evidence_adapter_geometry_invalid")
    if (
        result.multiroot_outcome != MULTIROOT_OUTCOME
        or result.supplier_a_status != _KERNEL_SUPPLIER_A_STATUS
        or result.supplier_a_mock_payment_status != SUPPLIER_A_MOCK_PAYMENT_STATUS
        or result.supplier_b_status != _KERNEL_SUPPLIER_B_STATUS
        or result.shipment_status != _KERNEL_SHIPMENT_STATUS
        or result.receipt_status != _KERNEL_RECEIPT_STATUS
        or result.technical_conformance_status != TECHNICAL_CONFORMANCE_STATUS
        or result.business_outcome != BUSINESS_OUTCOME
        or type(result.real_payment_executed) is not bool
        or result.real_payment_executed
        or type(result.real_shipment_released) is not bool
        or result.real_shipment_released
    ):
        errors.append("supplier_water_filter_sealed_evidence_adapter_business_outcome_mismatch")
    counters = (
        result.adapter_provider_call_count,
        result.adapter_network_call_count,
        result.adapter_gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.action_created_count,
        result.receipt_created_count,
        result.final_output_created_count,
        result.real_world_effects_count,
    )
    if any(type(value) is not int or value != 0 for value in counters):
        errors.append("supplier_water_filter_sealed_evidence_adapter_external_call_forbidden")
    if (
        type(result.domain_projection) is not _DomainEvidenceProjectionV01
        or _validate_domain_projection_v01(result.domain_projection)
        or result.domain_projection.status != _PROFILE_STATUS_PASS
    ):
        errors.append("supplier_water_filter_sealed_evidence_adapter_projection_invalid")
    if result.status != STATUS_PASS:
        errors.append("supplier_water_filter_sealed_evidence_adapter_status_mismatch")
    try:
        expected_id = _result_identity(result)
    except Exception:
        expected_id = ""
    if not _valid_sha256(result.adapter_result_id) or result.adapter_result_id != expected_id:
        errors.append("supplier_water_filter_sealed_evidence_adapter_identity_mismatch")
    hashes = (
        result.safe_execution_id,
        result.scenario_index_id,
        result.kernel_adapter_id,
        result.kernel_manifest_hash,
        result.multiroot_outcome_id,
    )
    if any(not _valid_sha256(value) for value in hashes):
        errors.append("supplier_water_filter_sealed_evidence_adapter_binding_mismatch")
    return _dedupe(errors)


def _result_identity(
    result: SupplierWaterFilterSealedEvidencePackageAdapterResultV01,
) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=_RESULT_ID_DOMAIN,
        payload=_canonical_json_bytes_v01(_result_plain(result, include_id=False)),
    )


def _result_plain(
    result: SupplierWaterFilterSealedEvidencePackageAdapterResultV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projection: dict[str, object] = {}
    if include_id:
        projection["adapter_result_id"] = result.adapter_result_id
    projection.update(
        {
            "adapter_version": result.adapter_version,
            "safe_execution_id": result.safe_execution_id,
            "scenario_index_id": result.scenario_index_id,
            "scenario_ids": list(result.scenario_ids),
            "scenario_names": list(result.scenario_names),
            "scenario_classifications": list(result.scenario_classifications),
            "scenario_row_hashes": list(result.scenario_row_hashes),
            "scenario_technical_statuses": list(result.scenario_technical_statuses),
            "scenario_business_outcomes": list(result.scenario_business_outcomes),
            "source_run_id": result.source_run_id,
            "source_report_id": result.source_report_id,
            "source_trace_type": result.source_trace_type,
            "transaction_id": result.transaction_id,
            "kernel_adapter_id": result.kernel_adapter_id,
            "kernel_manifest_hash": result.kernel_manifest_hash,
            "multiroot_outcome_id": result.multiroot_outcome_id,
            "multiroot_outcome": result.multiroot_outcome,
            "supplier_a_status": result.supplier_a_status,
            "supplier_a_mock_payment_status": result.supplier_a_mock_payment_status,
            "supplier_b_status": result.supplier_b_status,
            "shipment_status": result.shipment_status,
            "receipt_status": result.receipt_status,
            "technical_conformance_status": result.technical_conformance_status,
            "business_outcome": result.business_outcome,
            "real_payment_executed": result.real_payment_executed,
            "real_shipment_released": result.real_shipment_released,
            "domain_projection": _domain_projection_plain_v01(result.domain_projection),
            "scenario_count": result.scenario_count,
            "source_record_count": result.source_record_count,
            "artifact_record_count": result.artifact_record_count,
            "kernel_artifact_ref_count": result.kernel_artifact_ref_count,
            "causal_ref_count": result.causal_ref_count,
            "business_module_count": result.business_module_count,
            "fractal_branch_count": result.fractal_branch_count,
            "result_proposal_count": result.result_proposal_count,
            "root_decision_count": result.root_decision_count,
            "cross_root_evidence_count": result.cross_root_evidence_count,
            "adapter_provider_call_count": result.adapter_provider_call_count,
            "adapter_network_call_count": result.adapter_network_call_count,
            "adapter_gemini_call_count": result.adapter_gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "action_created_count": result.action_created_count,
            "receipt_created_count": result.receipt_created_count,
            "final_output_created_count": result.final_output_created_count,
            "real_world_effects_count": result.real_world_effects_count,
            "validation_errors": list(result.validation_errors),
            "status": result.status,
        }
    )
    return projection


def _replace_result_id(
    result: SupplierWaterFilterSealedEvidencePackageAdapterResultV01,
    adapter_result_id: str,
) -> SupplierWaterFilterSealedEvidencePackageAdapterResultV01:
    values = {name: getattr(result, name) for name in result.__slots__}
    values["adapter_result_id"] = adapter_result_id
    return SupplierWaterFilterSealedEvidencePackageAdapterResultV01(**values)


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _LOWER_HEX_64.fullmatch(value) is not None


def _stable_reason(error: ValueError) -> str:
    reason = error.args[0] if len(error.args) == 1 else ""
    allowed = {
        "supplier_water_filter_sealed_evidence_adapter_invalid",
        "supplier_water_filter_sealed_evidence_adapter_safe_execution_invalid",
        "supplier_water_filter_sealed_evidence_scenario_invalid",
        "supplier_water_filter_sealed_evidence_adapter_source_invalid",
        "supplier_water_filter_sealed_evidence_adapter_kernel_invalid",
        "supplier_water_filter_sealed_evidence_adapter_geometry_invalid",
        "supplier_water_filter_sealed_evidence_adapter_binding_mismatch",
        "supplier_water_filter_sealed_evidence_adapter_business_outcome_mismatch",
        "supplier_water_filter_sealed_evidence_adapter_projection_invalid",
        "supplier_water_filter_sealed_evidence_adapter_context_mismatch",
        "supplier_water_filter_sealed_evidence_adapter_identity_mismatch",
        "supplier_water_filter_sealed_evidence_adapter_status_mismatch",
        "supplier_water_filter_sealed_evidence_adapter_external_call_forbidden",
        "supplier_water_filter_sealed_evidence_adapter_authority_creation_forbidden",
        "supplier_water_filter_sealed_evidence_adapter_permission_creation_forbidden",
        "supplier_water_filter_sealed_evidence_adapter_action_creation_forbidden",
        "supplier_water_filter_sealed_evidence_adapter_receipt_creation_forbidden",
        "supplier_water_filter_sealed_evidence_adapter_final_output_creation_forbidden",
        "supplier_water_filter_sealed_evidence_adapter_effect_forbidden",
    }
    return reason if type(reason) is str and reason in allowed else (
        "supplier_water_filter_sealed_evidence_adapter_invalid"
    )


def _dedupe(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
