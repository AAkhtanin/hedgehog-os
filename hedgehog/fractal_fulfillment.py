from __future__ import annotations

from typing import Any, Callable, Mapping

from hedgehog.mock_connector_sandbox import MOCK_CONNECTOR_SANDBOX_ADAPTERS


FULFILLMENT_PARENT_FRACTAL_ID = "fractal_order_fulfillment:root_mock_packet_v01"

FULFILLMENT_BRANCH_DEFINITIONS = (
    {
        "branch_key": "payment",
        "branch_name": "payment_review_branch",
        "branch_id": "fulfillment_branch:payment_review",
        "child_cell_id": "child_cell:fulfillment:payment_review",
        "allowed_adapter": "fake_bank_adapter_v0",
        "allowed_action_kind": "mock_supplier_payment_review",
        "branch_task": "review mock supplier payment through sandbox receipt",
        "expected_receipt_type": "mock_bank_payment_review_receipt",
        "expected_status": "mock_payment_review_recorded",
    },
    {
        "branch_key": "supplier",
        "branch_name": "supplier_confirmation_branch",
        "branch_id": "fulfillment_branch:supplier_confirmation",
        "child_cell_id": "child_cell:fulfillment:supplier_confirmation",
        "allowed_adapter": "fake_supplier_adapter_v0",
        "allowed_action_kind": "mock_supplier_payment_review",
        "branch_task": "record mock supplier confirmation through sandbox receipt",
        "expected_receipt_type": "mock_supplier_confirmation_receipt",
        "expected_status": "mock_supplier_review_recorded",
    },
    {
        "branch_key": "warehouse",
        "branch_name": "warehouse_reservation_branch",
        "branch_id": "fulfillment_branch:warehouse_reservation",
        "child_cell_id": "child_cell:fulfillment:warehouse_reservation",
        "allowed_adapter": "fake_warehouse_adapter_v0",
        "allowed_action_kind": "mock_shipment_reservation_review",
        "branch_task": "record mock warehouse reservation through sandbox receipt",
        "expected_receipt_type": "mock_warehouse_reservation_receipt",
        "expected_status": "mock_reservation_review_recorded",
    },
)

FULFILLMENT_REQUIRED_BRANCH_IDS = tuple(
    definition["branch_id"] for definition in FULFILLMENT_BRANCH_DEFINITIONS
)
FULFILLMENT_BRANCH_BY_ID = {
    definition["branch_id"]: definition
    for definition in FULFILLMENT_BRANCH_DEFINITIONS
}

FULFILLMENT_BRANCH_FORBIDDEN_CONNECTOR_CLAIM_KEYS = (
    "connector_called",
    "real_connector_called",
    "bank_api_called",
    "supplier_api_called",
    "warehouse_api_called",
    "real_bank_api_called",
    "real_supplier_api_called",
    "real_warehouse_api_called",
    "connector_command",
    "connector_command_claimed",
    "fake_adapter_called_directly",
    "adapter_called_directly",
)

FULFILLMENT_BRANCH_DIRECT_ADAPTER_CLAIM_KEYS = frozenset(
    {
        "connector_bypass_attempted",
        "connector_command",
        "connector_command_claimed",
        "fake_adapter_called_directly",
        "adapter_called_directly",
    }
)

FULFILLMENT_BRANCH_DRS_WRITE_CLAIM_KEYS = frozenset(
    {
        "drs_write_claimed",
        "write_drs",
        "drs_writeback_claimed",
    }
)

FRACTAL_ORDER_FULFILLMENT_COUNTER_KEYS = (
    "fractal_order_fulfillment_dag_invoked_count",
    "fractal_order_fulfillment_dag_completed_count",
    "fractal_order_fulfillment_dag_denied_count",
    "fractal_order_fulfillment_requires_packet_count",
    "fractal_order_fulfillment_requires_sandbox_count",
    "fulfillment_child_cells_started_count",
    "fulfillment_child_cells_completed_count",
    "fulfillment_payment_branch_started_count",
    "fulfillment_payment_branch_completed_count",
    "fulfillment_supplier_branch_started_count",
    "fulfillment_supplier_branch_completed_count",
    "fulfillment_warehouse_branch_started_count",
    "fulfillment_warehouse_branch_completed_count",
    "fulfillment_branch_result_proposals_created_count",
    "fulfillment_branch_merge_completed_count",
    "fulfillment_topology_preserved_count",
    "fulfillment_child_orchestrator_invoked_count",
    "fulfillment_child_architect_invoked_count",
    "fulfillment_child_executor_invoked_count",
    "fulfillment_child_root_created_count",
    "fulfillment_child_final_output_created_count",
    "fulfillment_child_action_commit_packet_created_count",
    "fulfillment_child_direct_adapter_bypass_blocked_count",
    "fulfillment_missing_branch_blocked_count",
    "fulfillment_duplicate_branch_blocked_count",
    "fulfillment_unknown_branch_blocked_count",
    "fulfillment_branch_real_action_claim_blocked_count",
    "fulfillment_branch_receipt_mismatch_blocked_count",
    "fulfillment_root_final_authority_preserved_count",
)

SandboxRunner = Callable[..., Mapping[str, Any]]
PacketValidator = Callable[[Mapping[str, Any] | None, Mapping[str, Any], str], Mapping[str, Any]]
BranchContextBuilder = Callable[[Mapping[str, Any]], tuple[Mapping[str, Any], ...]]
BranchTopologyValidator = Callable[
    [tuple[Mapping[str, Any], ...], Mapping[str, Any]],
    Mapping[str, Any],
]
BranchProposalBuilder = Callable[
    [tuple[Mapping[str, Any], ...], tuple[Mapping[str, Any], ...], Mapping[str, Any]],
    tuple[Mapping[str, Any], ...],
]
BranchProposalValidator = Callable[
    [tuple[Mapping[str, Any], ...], tuple[Mapping[str, Any], ...], Mapping[str, Any]],
    Mapping[str, Any],
]
MergeBuilder = Callable[[tuple[Mapping[str, Any], ...], Mapping[str, Any]], Mapping[str, Any]]
SummaryBuilder = Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]


def fractal_order_fulfillment_zero_counters() -> dict[str, int]:
    return {key: 0 for key in FRACTAL_ORDER_FULFILLMENT_COUNTER_KEYS}


def fractal_order_fulfillment_context_default() -> dict[str, Any]:
    return {
        "layer": "Fractal Order Fulfillment DAG",
        "gate_enabled": False,
        "invoked": False,
        "completed": False,
        "denied": False,
        "denial_reasons": (),
        "parent_fractal_id": FULFILLMENT_PARENT_FRACTAL_ID,
        "packet_validated": False,
        "sandbox_required": True,
        "branch_count": 0,
        "merge_completed": False,
        "topology_preserved": False,
        "Root remains final authority": True,
        "counters": fractal_order_fulfillment_zero_counters(),
    }


def topology_preservation_context_default() -> dict[str, Any]:
    return {
        "validated": False,
        "accepted": False,
        "reasons": (),
        "child_orchestrator_present": False,
        "child_architect_present": False,
        "child_executor_present": False,
        "child_root_created": False,
        "child_final_output_created": False,
        "child_action_commit_packet_created": False,
        "direct_adapter_bypass_attempted": False,
        "real_world_effects_allowed": False,
        "returns_to_parent": False,
    }


def fulfillment_merge_context_default() -> dict[str, Any]:
    return {
        "merge_id": "fulfillment_merge:mock_connector_receipts",
        "consumes_branch_outputs": 0,
        "missing_branches": (),
        "duplicate_branches": (),
        "unknown_branches": (),
        "receipt_mismatches": (),
        "all_branches_returned_upward": False,
        "creates_final_output": False,
        "creates_action_commit_packet": False,
        "real_world_effects_allowed": False,
        "merge_completed": False,
        "root_final_authority_preserved": True,
    }


def fulfillment_forbidden_connector_claim_reasons(
    value: Mapping[str, Any],
) -> tuple[str, ...]:
    truthy_claim_keys = {
        key
        for key in FULFILLMENT_BRANCH_FORBIDDEN_CONNECTOR_CLAIM_KEYS
        if bool(value.get(key))
    }
    if not truthy_claim_keys:
        return ()

    reasons = ["branch_connector_claimed"]
    if truthy_claim_keys & FULFILLMENT_BRANCH_DIRECT_ADAPTER_CLAIM_KEYS:
        reasons.append("direct_adapter_bypass_attempted")
    if truthy_claim_keys - FULFILLMENT_BRANCH_DIRECT_ADAPTER_CLAIM_KEYS:
        reasons.append("branch_real_action_claimed")
    return tuple(reasons)


def build_fulfillment_branch_contexts(
    packet: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    branches: list[dict[str, Any]] = []
    for definition in FULFILLMENT_BRANCH_DEFINITIONS:
        branches.append(
            {
                "child_cell_id": definition["child_cell_id"],
                "parent_fractal_id": FULFILLMENT_PARENT_FRACTAL_ID,
                "branch_id": definition["branch_id"],
                "branch_name": definition["branch_name"],
                "child_role_topology": {
                    "child_orchestrator": "bounded_branch_router",
                    "child_architect": "bounded_branch_plan",
                    "child_executor": "mock_sandbox_task_executor",
                },
                "input_packet_id": packet["packet_id"],
                "allowed_adapter": definition["allowed_adapter"],
                "allowed_action_kind": definition["allowed_action_kind"],
                "branch_task": definition["branch_task"],
                "branch_status": "topology_planned",
                "expected_receipt_type": definition["expected_receipt_type"],
                "expected_status": definition["expected_status"],
                "produced_receipt_type": None,
                "returns_to_parent": True,
                "creates_final_output": False,
                "creates_action_commit_packet": False,
                "root_authority_claimed": False,
                "connector_bypass_attempted": False,
                "real_world_effects_allowed": False,
                "child_root_created": False,
                "child_final_output_created": False,
                "child_action_commit_packet_created": False,
            }
        )
    return tuple(branches)


def validate_fulfillment_branch_topology(
    branch_contexts: tuple[Mapping[str, Any], ...],
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    branch_ids = [str(branch.get("branch_id", "")) for branch in branch_contexts]
    branch_id_set = set(branch_ids)
    duplicate_branches = tuple(
        sorted({branch_id for branch_id in branch_ids if branch_ids.count(branch_id) > 1})
    )
    missing_branches = tuple(
        branch_id
        for branch_id in FULFILLMENT_REQUIRED_BRANCH_IDS
        if branch_id not in branch_id_set
    )
    unknown_branches = tuple(
        sorted(
            branch_id
            for branch_id in branch_id_set
            if branch_id not in FULFILLMENT_BRANCH_BY_ID
        )
    )
    receipt_mismatches: list[str] = []
    if missing_branches:
        reasons.append("missing_branch")
    if duplicate_branches:
        reasons.append("duplicate_branch")
    if unknown_branches:
        reasons.append("unknown_branch")

    for branch in branch_contexts:
        branch_id = str(branch.get("branch_id", ""))
        definition = FULFILLMENT_BRANCH_BY_ID.get(branch_id)
        topology = branch.get("child_role_topology") or {}
        if topology.get("child_orchestrator") != "bounded_branch_router":
            reasons.append("child_orchestrator_topology_invalid")
        if topology.get("child_architect") != "bounded_branch_plan":
            reasons.append("child_architect_topology_invalid")
        if topology.get("child_executor") != "mock_sandbox_task_executor":
            reasons.append("child_executor_topology_invalid")
        if branch.get("input_packet_id") != packet.get("packet_id"):
            reasons.append("branch_input_packet_mismatch")
        if branch.get("returns_to_parent") is not True:
            reasons.append("branch_must_return_upward")
        if branch.get("creates_final_output") is not False:
            reasons.append("child_final_output_forbidden")
        if branch.get("creates_action_commit_packet") is not False:
            reasons.append("child_action_commit_packet_forbidden")
        if branch.get("root_authority_claimed") is not False:
            reasons.append("child_root_authority_forbidden")
        if branch.get("child_root_created") is not False:
            reasons.append("child_root_authority_forbidden")
        if branch.get("child_final_output_created") is not False:
            reasons.append("child_final_output_forbidden")
        if branch.get("child_action_commit_packet_created") is not False:
            reasons.append("child_action_commit_packet_forbidden")
        if branch.get("connector_bypass_attempted") is not False:
            reasons.append("direct_adapter_bypass_attempted")
        reasons.extend(fulfillment_forbidden_connector_claim_reasons(branch))
        if branch.get("real_world_effects_allowed") is not False:
            reasons.append("branch_real_action_claimed")
        if branch.get("payment_executed") is True or branch.get("shipment_released") is True:
            reasons.append("branch_real_action_claimed")
        if any(bool(branch.get(key)) for key in FULFILLMENT_BRANCH_DRS_WRITE_CLAIM_KEYS):
            reasons.append("branch_drs_write_forbidden")
        if definition:
            expected_pairs = (
                ("allowed_adapter", definition["allowed_adapter"]),
                ("allowed_action_kind", definition["allowed_action_kind"]),
                ("expected_receipt_type", definition["expected_receipt_type"]),
                ("expected_status", definition["expected_status"]),
            )
            for field, expected in expected_pairs:
                if branch.get(field) != expected:
                    receipt_mismatches.append(branch_id or "unknown")

    if receipt_mismatches:
        reasons.append("branch_receipt_mismatch")

    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
        "missing_branches": missing_branches,
        "duplicate_branches": duplicate_branches,
        "unknown_branches": unknown_branches,
        "receipt_mismatches": tuple(dict.fromkeys(receipt_mismatches)),
    }


def build_fulfillment_branch_result_proposals(
    branch_contexts: tuple[Mapping[str, Any], ...],
    receipts: tuple[Mapping[str, Any], ...],
    packet: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    receipts_by_adapter = {
        str(receipt.get("adapter_name")): receipt for receipt in receipts
    }
    proposals: list[dict[str, Any]] = []
    for branch in branch_contexts:
        receipt = receipts_by_adapter.get(str(branch.get("allowed_adapter")), {})
        proposals.append(
            {
                "proposal_type": "fulfillment_branch_result_proposal",
                "branch_id": branch["branch_id"],
                "parent_fractal_id": branch["parent_fractal_id"],
                "source_packet_id": packet["packet_id"],
                "adapter_name": branch["allowed_adapter"],
                "expected_receipt_type": branch["expected_receipt_type"],
                "actual_receipt_type": receipt.get("receipt_type"),
                "receipt_ref": {
                    "adapter_name": receipt.get("adapter_name"),
                    "receipt_type": receipt.get("receipt_type"),
                    "source_packet_id": receipt.get("source_packet_id"),
                    "status": receipt.get("status"),
                },
                "branch_status": "completed",
                "mock_only": True,
                "real_world_effects_allowed": False,
                "returns_to_parent": True,
                "child_root_created": False,
                "child_final_output_created": False,
                "child_action_commit_packet_created": False,
                "direct_adapter_bypass_attempted": False,
                "root_final_authority_preserved": True,
            }
        )
    return tuple(proposals)


def validate_fulfillment_branch_result_proposals(
    proposals: tuple[Mapping[str, Any], ...],
    branch_contexts: tuple[Mapping[str, Any], ...],
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    proposal_branch_ids = [str(proposal.get("branch_id", "")) for proposal in proposals]
    proposal_branch_set = set(proposal_branch_ids)
    missing_branches = tuple(
        branch_id
        for branch_id in FULFILLMENT_REQUIRED_BRANCH_IDS
        if branch_id not in proposal_branch_set
    )
    duplicate_branches = tuple(
        sorted(
            {
                branch_id
                for branch_id in proposal_branch_ids
                if proposal_branch_ids.count(branch_id) > 1
            }
        )
    )
    unknown_branches = tuple(
        sorted(
            branch_id
            for branch_id in proposal_branch_set
            if branch_id not in FULFILLMENT_BRANCH_BY_ID
        )
    )
    receipt_mismatches: list[str] = []
    if missing_branches:
        reasons.append("missing_branch")
    if duplicate_branches:
        reasons.append("duplicate_branch")
    if unknown_branches:
        reasons.append("unknown_branch")

    branch_context_by_id = {
        str(branch.get("branch_id")): branch for branch in branch_contexts
    }
    for proposal in proposals:
        branch_id = str(proposal.get("branch_id", ""))
        definition = FULFILLMENT_BRANCH_BY_ID.get(branch_id)
        branch_context = branch_context_by_id.get(branch_id, {})
        if proposal.get("proposal_type") != "fulfillment_branch_result_proposal":
            reasons.append("branch_result_proposal_type_invalid")
        if proposal.get("parent_fractal_id") != FULFILLMENT_PARENT_FRACTAL_ID:
            reasons.append("parent_fractal_id_invalid")
        if proposal.get("source_packet_id") != packet.get("packet_id"):
            reasons.append("branch_source_packet_mismatch")
        if proposal.get("branch_status") != "completed":
            reasons.append("branch_status_invalid")
        if proposal.get("mock_only") is not True:
            reasons.append("branch_mock_only_required")
        if proposal.get("real_world_effects_allowed") is not False:
            reasons.append("branch_real_action_claimed")
        if proposal.get("returns_to_parent") is not True:
            reasons.append("branch_must_return_upward")
        if proposal.get("child_root_created") is not False:
            reasons.append("child_root_authority_forbidden")
        if proposal.get("child_final_output_created") is not False:
            reasons.append("child_final_output_forbidden")
        if proposal.get("child_action_commit_packet_created") is not False:
            reasons.append("child_action_commit_packet_forbidden")
        if proposal.get("direct_adapter_bypass_attempted") is not False:
            reasons.append("direct_adapter_bypass_attempted")
        reasons.extend(fulfillment_forbidden_connector_claim_reasons(proposal))
        if proposal.get("root_final_authority_preserved") is not True:
            reasons.append("root_final_authority_not_preserved")
        if proposal.get("payment_executed") is True or proposal.get("shipment_released") is True:
            reasons.append("branch_real_action_claimed")
        if definition:
            if proposal.get("adapter_name") != definition["allowed_adapter"]:
                receipt_mismatches.append(branch_id)
            if proposal.get("expected_receipt_type") != definition["expected_receipt_type"]:
                receipt_mismatches.append(branch_id)
            if proposal.get("actual_receipt_type") != definition["expected_receipt_type"]:
                receipt_mismatches.append(branch_id)
            receipt_ref = proposal.get("receipt_ref") or {}
            if receipt_ref.get("adapter_name") != definition["allowed_adapter"]:
                receipt_mismatches.append(branch_id)
            if receipt_ref.get("receipt_type") != definition["expected_receipt_type"]:
                receipt_mismatches.append(branch_id)
            if receipt_ref.get("source_packet_id") != packet.get("packet_id"):
                receipt_mismatches.append(branch_id)
            if receipt_ref.get("status") != definition["expected_status"]:
                receipt_mismatches.append(branch_id)
        if branch_context and proposal.get("adapter_name") != branch_context.get("allowed_adapter"):
            receipt_mismatches.append(branch_id)

    if receipt_mismatches:
        reasons.append("branch_receipt_mismatch")
    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
        "missing_branches": missing_branches,
        "duplicate_branches": duplicate_branches,
        "unknown_branches": unknown_branches,
        "receipt_mismatches": tuple(dict.fromkeys(receipt_mismatches)),
        "all_branches_returned_upward": all(
            proposal.get("returns_to_parent") is True for proposal in proposals
        )
        and len(proposals) == len(FULFILLMENT_REQUIRED_BRANCH_IDS),
    }


def build_fulfillment_merge_context(
    proposals: tuple[Mapping[str, Any], ...],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "merge_id": "fulfillment_merge:mock_connector_receipts",
        "consumes_branch_outputs": len(proposals),
        "missing_branches": tuple(validation.get("missing_branches", ())),
        "duplicate_branches": tuple(validation.get("duplicate_branches", ())),
        "unknown_branches": tuple(validation.get("unknown_branches", ())),
        "receipt_mismatches": tuple(validation.get("receipt_mismatches", ())),
        "all_branches_returned_upward": bool(
            validation.get("all_branches_returned_upward")
        ),
        "creates_final_output": False,
        "creates_action_commit_packet": False,
        "real_world_effects_allowed": False,
        "merge_completed": bool(validation.get("accepted")),
        "root_final_authority_preserved": True,
    }


def validate_fulfillment_merge_context(
    merge_context: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    if merge_context.get("merge_id") != "fulfillment_merge:mock_connector_receipts":
        reasons.append("fulfillment_merge_id_invalid")
    if merge_context.get("consumes_branch_outputs") != len(
        FULFILLMENT_REQUIRED_BRANCH_IDS
    ):
        reasons.append("missing_branch")
    if tuple(merge_context.get("missing_branches", ())) != ():
        reasons.append("missing_branch")
    if tuple(merge_context.get("duplicate_branches", ())) != ():
        reasons.append("duplicate_branch")
    if tuple(merge_context.get("unknown_branches", ())) != ():
        reasons.append("unknown_branch")
    if tuple(merge_context.get("receipt_mismatches", ())) != ():
        reasons.append("branch_receipt_mismatch")
    if merge_context.get("all_branches_returned_upward") is not True:
        reasons.append("branch_must_return_upward")
    if merge_context.get("creates_final_output") is not False:
        reasons.append("child_final_output_forbidden")
    if merge_context.get("creates_action_commit_packet") is not False:
        reasons.append("child_action_commit_packet_forbidden")
    if merge_context.get("real_world_effects_allowed") is not False:
        reasons.append("branch_real_action_claimed")
    if merge_context.get("merge_completed") is not True:
        reasons.append("fulfillment_merge_not_completed")
    if merge_context.get("root_final_authority_preserved") is not True:
        reasons.append("root_final_authority_not_preserved")
    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
    }


def build_topology_preservation_context(
    branch_contexts: tuple[Mapping[str, Any], ...],
    topology_validation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "validated": True,
        "accepted": bool(topology_validation.get("accepted")),
        "reasons": tuple(topology_validation.get("reasons", ())),
        "child_orchestrator_present": all(
            (branch.get("child_role_topology") or {}).get("child_orchestrator")
            == "bounded_branch_router"
            for branch in branch_contexts
        ),
        "child_architect_present": all(
            (branch.get("child_role_topology") or {}).get("child_architect")
            == "bounded_branch_plan"
            for branch in branch_contexts
        ),
        "child_executor_present": all(
            (branch.get("child_role_topology") or {}).get("child_executor")
            == "mock_sandbox_task_executor"
            for branch in branch_contexts
        ),
        "child_root_created": any(
            branch.get("child_root_created") is True for branch in branch_contexts
        ),
        "child_final_output_created": any(
            branch.get("child_final_output_created") is True
            for branch in branch_contexts
        ),
        "child_action_commit_packet_created": any(
            branch.get("child_action_commit_packet_created") is True
            for branch in branch_contexts
        ),
        "direct_adapter_bypass_attempted": any(
            branch.get("connector_bypass_attempted") is True
            or branch.get("fake_adapter_called_directly") is True
            or branch.get("adapter_called_directly") is True
            for branch in branch_contexts
        ),
        "real_world_effects_allowed": any(
            branch.get("real_world_effects_allowed") is True
            for branch in branch_contexts
        ),
        "returns_to_parent": all(
            branch.get("returns_to_parent") is True for branch in branch_contexts
        ),
    }


def fulfillment_failure_result(
    *,
    fulfillment_context: dict[str, Any],
    topology_context: dict[str, Any],
    counters: dict[str, int],
    reasons: tuple[str, ...],
    branch_contexts: tuple[Mapping[str, Any], ...] = (),
    branch_result_proposals: tuple[Mapping[str, Any], ...] = (),
    merge_context: Mapping[str, Any] | None = None,
    sandbox_result: Mapping[str, Any] | None = None,
    empty_sandbox_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    counters["fractal_order_fulfillment_dag_denied_count"] = 1
    if "fractal_order_fulfillment_requires_valid_action_commit_packet" in reasons:
        counters["fractal_order_fulfillment_requires_packet_count"] = 1
    if "fractal_order_fulfillment_requires_mock_connector_sandbox" in reasons:
        counters["fractal_order_fulfillment_requires_sandbox_count"] = 1
    if "missing_branch" in reasons:
        counters["fulfillment_missing_branch_blocked_count"] = 1
    if "duplicate_branch" in reasons:
        counters["fulfillment_duplicate_branch_blocked_count"] = 1
    if "unknown_branch" in reasons:
        counters["fulfillment_unknown_branch_blocked_count"] = 1
    if "direct_adapter_bypass_attempted" in reasons:
        counters["fulfillment_child_direct_adapter_bypass_blocked_count"] = 1
    if "branch_real_action_claimed" in reasons or "branch_connector_claimed" in reasons:
        counters["fulfillment_branch_real_action_claim_blocked_count"] = 1
    if "branch_receipt_mismatch" in reasons:
        counters["fulfillment_branch_receipt_mismatch_blocked_count"] = 1

    fulfillment_context.update(
        {
            "denied": True,
            "denial_reasons": reasons,
            "branch_count": len(branch_contexts),
            "counters": counters,
        }
    )
    topology_context.update(
        {
            "validated": True,
            "accepted": False,
            "reasons": reasons,
        }
    )
    default_sandbox_result = empty_sandbox_result or {
        "mock_connector_sandbox_context": {},
        "mock_connector_receipts": (),
        "execution_evidence": {},
        "mock_execution_validation_context": {},
        "root_mock_execution_summary_context": {},
        "fail_closed": False,
        "validation_errors": (),
    }
    return {
        "fractal_order_fulfillment_context": fulfillment_context,
        "fulfillment_branch_contexts": tuple(dict(item) for item in branch_contexts),
        "fulfillment_branch_result_proposals": tuple(
            dict(item) for item in branch_result_proposals
        ),
        "fulfillment_merge_context": dict(merge_context or fulfillment_merge_context_default()),
        "topology_preservation_context": topology_context,
        "sandbox_result": dict(sandbox_result or default_sandbox_result),
        "fail_closed": True,
        "validation_errors": reasons,
    }


def run_fractal_order_fulfillment_dag(
    *,
    gate_enabled: bool,
    sandbox_gate_enabled: bool,
    root_boundary: Mapping[str, Any],
    action_commit_packet_context: Mapping[str, Any],
    action_commit_packet: Mapping[str, Any] | None,
    supplier_context: Mapping[str, Any],
    scenario_time: str,
    packet_validator: PacketValidator,
    sandbox_runner: SandboxRunner,
    root_summary_builder: SummaryBuilder,
    empty_sandbox_result: Mapping[str, Any],
    branch_context_builder: BranchContextBuilder = build_fulfillment_branch_contexts,
    branch_topology_validator: BranchTopologyValidator = validate_fulfillment_branch_topology,
    branch_proposal_builder: BranchProposalBuilder = build_fulfillment_branch_result_proposals,
    branch_proposal_validator: BranchProposalValidator = validate_fulfillment_branch_result_proposals,
    merge_builder: MergeBuilder = build_fulfillment_merge_context,
) -> dict[str, Any]:
    fulfillment_context = fractal_order_fulfillment_context_default()
    topology_context = topology_preservation_context_default()
    if not gate_enabled:
        return {
            "fractal_order_fulfillment_context": fulfillment_context,
            "fulfillment_branch_contexts": (),
            "fulfillment_branch_result_proposals": (),
            "fulfillment_merge_context": fulfillment_merge_context_default(),
            "topology_preservation_context": topology_context,
            "sandbox_result": None,
            "fail_closed": False,
            "validation_errors": (),
        }

    counters = fractal_order_fulfillment_zero_counters()
    counters["fractal_order_fulfillment_dag_invoked_count"] = 1
    fulfillment_context.update(
        {
            "gate_enabled": True,
            "invoked": True,
            "counters": counters,
        }
    )

    packet = dict(action_commit_packet or {})
    packet_accepted = (
        action_commit_packet_context.get("packet_created") is True
        and (action_commit_packet_context.get("validation") or {}).get("accepted")
        is True
        and bool(packet)
    )
    if not packet_accepted:
        reasons = ("fractal_order_fulfillment_requires_valid_action_commit_packet",)
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=reasons,
            empty_sandbox_result=empty_sandbox_result,
        )

    packet_validation = packet_validator(packet, root_boundary, scenario_time)
    if not packet_validation["accepted"]:
        reasons = (
            "fractal_order_fulfillment_requires_valid_action_commit_packet",
            *tuple(packet_validation["reasons"]),
        )
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=reasons,
            empty_sandbox_result=empty_sandbox_result,
        )
    fulfillment_context["packet_validated"] = True

    if not sandbox_gate_enabled:
        reasons = ("fractal_order_fulfillment_requires_mock_connector_sandbox",)
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=reasons,
            empty_sandbox_result=empty_sandbox_result,
        )

    branch_contexts = tuple(branch_context_builder(packet))
    topology_validation = branch_topology_validator(branch_contexts, packet)
    topology_context.update(
        build_topology_preservation_context(branch_contexts, topology_validation)
    )
    if not topology_validation["accepted"]:
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=tuple(topology_validation["reasons"]),
            branch_contexts=branch_contexts,
            empty_sandbox_result=empty_sandbox_result,
        )

    counters["fulfillment_child_cells_started_count"] = 3
    counters["fulfillment_payment_branch_started_count"] = 1
    counters["fulfillment_supplier_branch_started_count"] = 1
    counters["fulfillment_warehouse_branch_started_count"] = 1
    counters["fulfillment_child_orchestrator_invoked_count"] = 3
    counters["fulfillment_child_architect_invoked_count"] = 3
    counters["fulfillment_child_executor_invoked_count"] = 3
    counters["fulfillment_topology_preserved_count"] = 1

    sandbox_result = sandbox_runner(
        root_boundary=root_boundary,
        action_commit_packet_context=action_commit_packet_context,
        action_commit_packet=packet,
        supplier_context=supplier_context,
        create_root_summary=False,
    )
    if sandbox_result["fail_closed"]:
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=tuple(sandbox_result["validation_errors"]),
            branch_contexts=branch_contexts,
            sandbox_result=sandbox_result,
            empty_sandbox_result=empty_sandbox_result,
        )

    branch_result_proposals = tuple(
        branch_proposal_builder(
            branch_contexts,
            tuple(sandbox_result["mock_connector_receipts"]),
            packet,
        )
    )
    proposal_validation = branch_proposal_validator(
        branch_result_proposals,
        branch_contexts,
        packet,
    )
    merge_context = dict(
        merge_builder(
            branch_result_proposals,
            proposal_validation,
        )
    )
    if not proposal_validation["accepted"]:
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=tuple(proposal_validation["reasons"]),
            branch_contexts=branch_contexts,
            branch_result_proposals=branch_result_proposals,
            merge_context=merge_context,
            sandbox_result=sandbox_result,
            empty_sandbox_result=empty_sandbox_result,
        )

    merge_validation = validate_fulfillment_merge_context(merge_context)
    if not merge_validation["accepted"]:
        reasons = tuple(
            dict.fromkeys(
                tuple(merge_validation["reasons"])
            )
        )
        return fulfillment_failure_result(
            fulfillment_context=fulfillment_context,
            topology_context=topology_context,
            counters=counters,
            reasons=reasons,
            branch_contexts=branch_contexts,
            branch_result_proposals=branch_result_proposals,
            merge_context=merge_context,
            sandbox_result=sandbox_result,
            empty_sandbox_result=empty_sandbox_result,
        )

    completed_branches = []
    proposals_by_branch = {
        proposal["branch_id"]: proposal for proposal in branch_result_proposals
    }
    for branch in branch_contexts:
        proposal = proposals_by_branch[branch["branch_id"]]
        completed = dict(branch)
        completed.update(
            {
                "branch_status": "completed",
                "produced_receipt_type": proposal["actual_receipt_type"],
            }
        )
        completed_branches.append(completed)

    counters["fractal_order_fulfillment_dag_completed_count"] = 1
    counters["fulfillment_child_cells_completed_count"] = 3
    counters["fulfillment_payment_branch_completed_count"] = 1
    counters["fulfillment_supplier_branch_completed_count"] = 1
    counters["fulfillment_warehouse_branch_completed_count"] = 1
    counters["fulfillment_branch_result_proposals_created_count"] = 3
    counters["fulfillment_branch_merge_completed_count"] = 1
    counters["fulfillment_root_final_authority_preserved_count"] = 1
    summary = root_summary_builder(
        packet,
        sandbox_result["execution_evidence"],
    )
    sandbox_context = dict(sandbox_result["mock_connector_sandbox_context"])
    sandbox_counters = dict(sandbox_context.get("counters") or {})
    sandbox_counters["root_mock_execution_summary_created_count"] = 1
    sandbox_context["counters"] = sandbox_counters
    sandbox_result = {
        **sandbox_result,
        "mock_connector_sandbox_context": sandbox_context,
        "root_mock_execution_summary_context": summary,
    }
    fulfillment_context.update(
        {
            "completed": True,
            "branch_count": 3,
            "merge_completed": True,
            "topology_preserved": True,
            "counters": counters,
        }
    )
    topology_context.update(
        {
            "validated": True,
            "accepted": True,
            "reasons": (),
        }
    )
    return {
        "fractal_order_fulfillment_context": fulfillment_context,
        "fulfillment_branch_contexts": tuple(completed_branches),
        "fulfillment_branch_result_proposals": branch_result_proposals,
        "fulfillment_merge_context": merge_context,
        "topology_preservation_context": topology_context,
        "sandbox_result": sandbox_result,
        "fail_closed": False,
        "validation_errors": (),
    }
