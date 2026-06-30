from __future__ import annotations

import inspect

import pytest

from hedgehog.action_commit_packet import build_mock_action_commit_packet
from hedgehog.fractal_fulfillment import FULFILLMENT_BRANCH_DEFINITIONS
from hedgehog.fractal_fulfillment import FULFILLMENT_BRANCH_DIRECT_ADAPTER_CLAIM_KEYS
from hedgehog.fractal_fulfillment import FULFILLMENT_BRANCH_DRS_WRITE_CLAIM_KEYS
from hedgehog.fractal_fulfillment import (
    FULFILLMENT_BRANCH_FORBIDDEN_CONNECTOR_CLAIM_KEYS,
)
from hedgehog.fractal_fulfillment import FULFILLMENT_PARENT_FRACTAL_ID
from hedgehog.fractal_fulfillment import FULFILLMENT_REQUIRED_BRANCH_IDS
from hedgehog.fractal_fulfillment import build_fulfillment_branch_contexts
from hedgehog.fractal_fulfillment import build_fulfillment_branch_result_proposals
from hedgehog.fractal_fulfillment import build_fulfillment_merge_context
from hedgehog.fractal_fulfillment import build_topology_preservation_context
from hedgehog.fractal_fulfillment import fractal_order_fulfillment_context_default
from hedgehog.fractal_fulfillment import fulfillment_merge_context_default
from hedgehog.fractal_fulfillment import run_fractal_order_fulfillment_dag
from hedgehog.fractal_fulfillment import topology_preservation_context_default
from hedgehog.fractal_fulfillment import validate_fulfillment_branch_result_proposals
from hedgehog.fractal_fulfillment import validate_fulfillment_branch_topology
from hedgehog.fractal_fulfillment import validate_fulfillment_merge_context
from hedgehog.mock_connector_sandbox import fake_bank_adapter_v0
from hedgehog.mock_connector_sandbox import fake_supplier_adapter_v0
from hedgehog.mock_connector_sandbox import fake_warehouse_adapter_v0
from hedgehog.mock_connector_sandbox import mock_connector_sandbox_context_default
from hedgehog.mock_connector_sandbox import mock_execution_validation_context_default
from hedgehog.mock_connector_sandbox import root_mock_execution_summary
from hedgehog.mock_connector_sandbox import validate_mock_connector_sandbox_packet


SCENARIO_TIME = "2026-06-22T12:00:00+00:00"


def _root_boundary() -> dict:
    return {
        "created_by": "root_boundary",
        "decision": "ready_for_mock_action",
        "root_reviewed": True,
        "reason": "Root approves mock-only action attempt packet creation",
        "blockers_checked": {
            "legal_hold_clear": True,
            "stock_available_or_mock_reservable": True,
            "post_vv_passed": True,
            "gt_lgt_reviewed": True,
        },
        "root_reviewed_semantic_outcome": {
            "outcome_id": "root_outcome:full_semantic_e2e_supplier_payment_v01",
        },
    }


def _post_vv_context() -> dict:
    return {
        "implementation": "hedgehog.post_vv.validate_result_proposals",
        "vv_report_count": 1,
        "finalizes": False,
    }


def _gt_lgt_context() -> dict:
    return {
        "implementation": "hedgehog.gt_validator.validate_gt",
        "gt_report_id": "gt_report:full_semantic_e2e_supplier_payment_v01",
        "decision": "accept",
        "finalizes": False,
    }


def _valid_packet() -> dict:
    return build_mock_action_commit_packet(
        root_boundary=_root_boundary(),
        post_vv_context=_post_vv_context(),
        gt_lgt_context=_gt_lgt_context(),
    )


def _adapter_context(packet: dict) -> dict:
    return {
        "business_subject": packet["business_subject"],
        "supplier_payment_context_summary": {
            "mock_ready_fixture": True,
            "legal_hold_present": False,
            "water_filter_shortage": False,
        },
    }


def _valid_receipts(packet: dict) -> tuple[dict, dict, dict]:
    context = _adapter_context(packet)
    return (
        fake_bank_adapter_v0(packet, SCENARIO_TIME, context),
        fake_supplier_adapter_v0(packet, SCENARIO_TIME, context),
        fake_warehouse_adapter_v0(packet, SCENARIO_TIME, context),
    )


def _valid_branches(packet: dict) -> tuple[dict, ...]:
    return build_fulfillment_branch_contexts(packet)


def _valid_proposals(packet: dict) -> tuple[dict, ...]:
    return build_fulfillment_branch_result_proposals(
        _valid_branches(packet),
        _valid_receipts(packet),
        packet,
    )


def test_default_contexts_are_inactive() -> None:
    context = fractal_order_fulfillment_context_default()
    topology = topology_preservation_context_default()
    merge = fulfillment_merge_context_default()

    assert context["invoked"] is False
    assert context["completed"] is False
    assert context["denied"] is False
    assert context["Root remains final authority"] is True
    assert topology["validated"] is False
    assert topology["accepted"] is False
    assert merge["merge_completed"] is False


def test_branch_definitions_are_exact() -> None:
    definitions = {item["branch_name"]: item for item in FULFILLMENT_BRANCH_DEFINITIONS}

    assert len(FULFILLMENT_REQUIRED_BRANCH_IDS) == 3
    assert definitions["payment_review_branch"]["allowed_adapter"] == (
        "fake_bank_adapter_v0"
    )
    assert definitions["payment_review_branch"]["expected_receipt_type"] == (
        "mock_bank_payment_review_receipt"
    )
    assert definitions["supplier_confirmation_branch"]["allowed_adapter"] == (
        "fake_supplier_adapter_v0"
    )
    assert definitions["supplier_confirmation_branch"]["expected_receipt_type"] == (
        "mock_supplier_confirmation_receipt"
    )
    assert definitions["warehouse_reservation_branch"]["allowed_adapter"] == (
        "fake_warehouse_adapter_v0"
    )
    assert definitions["warehouse_reservation_branch"]["expected_receipt_type"] == (
        "mock_warehouse_reservation_receipt"
    )


def test_valid_branch_contexts_preserve_child_topology() -> None:
    packet = _valid_packet()
    branches = _valid_branches(packet)
    validation = validate_fulfillment_branch_topology(branches, packet)

    assert len(branches) == 3
    assert validation["accepted"] is True
    for branch in branches:
        topology = branch["child_role_topology"]
        assert topology["child_orchestrator"] == "bounded_branch_router"
        assert topology["child_architect"] == "bounded_branch_plan"
        assert topology["child_executor"] == "mock_sandbox_task_executor"
        assert branch["returns_to_parent"] is True
        assert branch["child_root_created"] is False
        assert branch["child_final_output_created"] is False
        assert branch["child_action_commit_packet_created"] is False


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("child_root_created", "child_root_authority_forbidden"),
        ("child_final_output_created", "child_final_output_forbidden"),
        ("child_action_commit_packet_created", "child_action_commit_packet_forbidden"),
        ("root_authority_claimed", "child_root_authority_forbidden"),
    ),
)
def test_child_authority_violations_are_rejected(field: str, reason: str) -> None:
    packet = _valid_packet()
    branches = [dict(branch) for branch in _valid_branches(packet)]
    branches[0][field] = True

    validation = validate_fulfillment_branch_topology(tuple(branches), packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


@pytest.mark.parametrize(
    "field",
    (
        "connector_called",
        "real_bank_api_called",
        "fake_adapter_called_directly",
        "adapter_called_directly",
        "connector_command",
    ),
)
def test_direct_adapter_and_connector_claims_are_rejected(field: str) -> None:
    assert field in FULFILLMENT_BRANCH_FORBIDDEN_CONNECTOR_CLAIM_KEYS
    packet = _valid_packet()
    branches = [dict(branch) for branch in _valid_branches(packet)]
    branches[0][field] = True

    validation = validate_fulfillment_branch_topology(tuple(branches), packet)

    assert validation["accepted"] is False
    assert "branch_connector_claimed" in validation["reasons"]
    if field in FULFILLMENT_BRANCH_DIRECT_ADAPTER_CLAIM_KEYS:
        assert "direct_adapter_bypass_attempted" in validation["reasons"]


def test_drs_write_claim_is_rejected() -> None:
    assert "drs_write_claimed" in FULFILLMENT_BRANCH_DRS_WRITE_CLAIM_KEYS
    packet = _valid_packet()
    branches = [dict(branch) for branch in _valid_branches(packet)]
    branches[0]["drs_write_claimed"] = True

    validation = validate_fulfillment_branch_topology(tuple(branches), packet)

    assert validation["accepted"] is False
    assert "branch_drs_write_forbidden" in validation["reasons"]


def test_valid_branch_result_proposals_are_accepted() -> None:
    packet = _valid_packet()
    branches = _valid_branches(packet)
    proposals = build_fulfillment_branch_result_proposals(
        branches,
        _valid_receipts(packet),
        packet,
    )
    validation = validate_fulfillment_branch_result_proposals(
        proposals,
        branches,
        packet,
    )

    assert len(proposals) == 3
    assert validation["accepted"] is True
    by_branch = {proposal["branch_id"]: proposal for proposal in proposals}
    assert by_branch["fulfillment_branch:payment_review"]["adapter_name"] == (
        "fake_bank_adapter_v0"
    )
    assert by_branch["fulfillment_branch:payment_review"]["actual_receipt_type"] == (
        "mock_bank_payment_review_receipt"
    )
    assert by_branch["fulfillment_branch:supplier_confirmation"][
        "actual_receipt_type"
    ] == "mock_supplier_confirmation_receipt"
    assert by_branch["fulfillment_branch:warehouse_reservation"][
        "actual_receipt_type"
    ] == "mock_warehouse_reservation_receipt"


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("payment_executed", "branch_real_action_claimed"),
        ("shipment_released", "branch_real_action_claimed"),
        ("connector_called", "branch_connector_claimed"),
        ("real_bank_api_called", "branch_connector_claimed"),
    ),
)
def test_branch_result_real_action_or_connector_claim_is_rejected(
    field: str,
    reason: str,
) -> None:
    packet = _valid_packet()
    branches = _valid_branches(packet)
    proposals = [dict(proposal) for proposal in _valid_proposals(packet)]
    proposals[0][field] = True

    validation = validate_fulfillment_branch_result_proposals(
        tuple(proposals),
        branches,
        packet,
    )

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("adapter_name", "fake_warehouse_adapter_v0"),
        ("actual_receipt_type", "mock_warehouse_reservation_receipt"),
    ),
)
def test_wrong_adapter_or_receipt_is_rejected(field: str, value: str) -> None:
    packet = _valid_packet()
    branches = _valid_branches(packet)
    proposals = [dict(proposal) for proposal in _valid_proposals(packet)]
    proposals[0][field] = value

    validation = validate_fulfillment_branch_result_proposals(
        tuple(proposals),
        branches,
        packet,
    )

    assert validation["accepted"] is False
    assert "branch_receipt_mismatch" in validation["reasons"]


def test_missing_branch_is_rejected_by_proposal_and_merge_validation() -> None:
    packet = _valid_packet()
    branches = tuple(
        branch
        for branch in _valid_branches(packet)
        if branch["branch_id"] != "fulfillment_branch:supplier_confirmation"
    )
    proposals = build_fulfillment_branch_result_proposals(
        branches,
        _valid_receipts(packet),
        packet,
    )
    proposal_validation = validate_fulfillment_branch_result_proposals(
        proposals,
        branches,
        packet,
    )
    merge = build_fulfillment_merge_context(proposals, proposal_validation)
    merge_validation = validate_fulfillment_merge_context(merge)

    assert proposal_validation["accepted"] is False
    assert "missing_branch" in proposal_validation["reasons"]
    assert merge_validation["accepted"] is False
    assert "missing_branch" in merge_validation["reasons"]


def test_duplicate_branch_is_rejected_by_proposal_and_merge_validation() -> None:
    packet = _valid_packet()
    branches = list(_valid_branches(packet))
    branches[1] = dict(branches[0])
    proposals = build_fulfillment_branch_result_proposals(
        tuple(branches),
        _valid_receipts(packet),
        packet,
    )
    proposal_validation = validate_fulfillment_branch_result_proposals(
        proposals,
        tuple(branches),
        packet,
    )
    merge = build_fulfillment_merge_context(proposals, proposal_validation)
    merge_validation = validate_fulfillment_merge_context(merge)

    assert proposal_validation["accepted"] is False
    assert "duplicate_branch" in proposal_validation["reasons"]
    assert merge_validation["accepted"] is False
    assert "duplicate_branch" in merge_validation["reasons"]


def test_unknown_branch_is_rejected() -> None:
    packet = _valid_packet()
    branches = [dict(branch) for branch in _valid_branches(packet)]
    branches[0]["branch_id"] = "fulfillment_branch:unknown"

    topology_validation = validate_fulfillment_branch_topology(tuple(branches), packet)

    assert topology_validation["accepted"] is False
    assert "unknown_branch" in topology_validation["reasons"]


def test_parent_merge_valid_context_is_accepted() -> None:
    packet = _valid_packet()
    branches = _valid_branches(packet)
    proposals = _valid_proposals(packet)
    proposal_validation = validate_fulfillment_branch_result_proposals(
        proposals,
        branches,
        packet,
    )
    merge = build_fulfillment_merge_context(proposals, proposal_validation)
    merge_validation = validate_fulfillment_merge_context(merge)

    assert merge["merge_id"] == "fulfillment_merge:mock_connector_receipts"
    assert merge["consumes_branch_outputs"] == 3
    assert merge["merge_completed"] is True
    assert merge["creates_final_output"] is False
    assert merge["creates_action_commit_packet"] is False
    assert merge["all_branches_returned_upward"] is True
    assert merge_validation["accepted"] is True


def test_topology_preservation_context_reports_valid_topology() -> None:
    packet = _valid_packet()
    branches = _valid_branches(packet)
    validation = validate_fulfillment_branch_topology(branches, packet)
    context = build_topology_preservation_context(branches, validation)

    assert context["validated"] is True
    assert context["accepted"] is True
    assert context["child_root_created"] is False
    assert context["child_final_output_created"] is False
    assert context["child_action_commit_packet_created"] is False
    assert context["direct_adapter_bypass_attempted"] is False
    assert context["returns_to_parent"] is True


def test_core_run_completes_with_injected_sandbox_runner() -> None:
    packet = _valid_packet()

    def sandbox_runner(**_kwargs):
        return {
            "mock_connector_sandbox_context": {
                "completed": True,
                "counters": {"root_mock_execution_summary_created_count": 0},
            },
            "mock_connector_receipts": _valid_receipts(packet),
            "execution_evidence": {
                "evidence_id": "mock_connector_execution_evidence:core",
                "receipt_count": 3,
            },
            "mock_execution_validation_context": {"accepted": True},
            "root_mock_execution_summary_context": {},
            "fail_closed": False,
            "validation_errors": (),
        }

    result = run_fractal_order_fulfillment_dag(
        gate_enabled=True,
        sandbox_gate_enabled=True,
        root_boundary=_root_boundary(),
        action_commit_packet_context={
            "packet_created": True,
            "validation": {"accepted": True},
        },
        action_commit_packet=packet,
        supplier_context={"mock_ready_fixture": True},
        scenario_time=SCENARIO_TIME,
        packet_validator=validate_mock_connector_sandbox_packet,
        sandbox_runner=sandbox_runner,
        root_summary_builder=root_mock_execution_summary,
        empty_sandbox_result={
            "mock_connector_sandbox_context": mock_connector_sandbox_context_default(
                scenario_time=SCENARIO_TIME
            ),
            "mock_connector_receipts": (),
            "execution_evidence": {},
            "mock_execution_validation_context": (
                mock_execution_validation_context_default()
            ),
            "root_mock_execution_summary_context": {},
            "fail_closed": False,
            "validation_errors": (),
        },
    )

    assert result["fail_closed"] is False
    assert result["fractal_order_fulfillment_context"]["completed"] is True
    assert result["fulfillment_merge_context"]["merge_completed"] is True
    assert len(result["fulfillment_branch_contexts"]) == 3


def test_fractal_fulfillment_core_has_no_network_or_sensitive_markers() -> None:
    import hedgehog.fractal_fulfillment as fractal_fulfillment

    source = inspect.getsource(fractal_fulfillment)
    for forbidden in (
        "requests",
        "httpx",
        "urllib",
        "socket",
        "subprocess",
        "os.system",
        "api_key",
        "secret",
        "token",
        "password",
        ".tmp",
    ):
        assert forbidden not in source
