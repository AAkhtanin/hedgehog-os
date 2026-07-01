from __future__ import annotations

from pathlib import Path

import pytest

from hedgehog import context_packets as packets


def _all_valid_packets() -> tuple[tuple[dict, object], ...]:
    return (
        (
            packets.build_business_request_context_packet(
                domain="warehouse_dispatch",
                request_id="request:warehouse_dispatch:001",
                business_subject="dispatch review",
                requested_action="review_dispatch_readiness",
            ),
            packets.validate_business_request_context_packet,
        ),
        (
            packets.build_evidence_context_packet(
                domain="warehouse_dispatch",
                semantic_evidence_claim_refs=("claim:warehouse:001",),
            ),
            packets.validate_evidence_context_packet,
        ),
        (
            packets.build_drs_candidate_context_packet(
                domain="warehouse_dispatch",
                candidate_ids=("candidate:warehouse:001",),
                stale_flags={"candidate:warehouse:001": False},
                conflict_flags={"candidate:warehouse:001": False},
                reuse_eligibility_flags={"candidate:warehouse:001": False},
            ),
            packets.validate_drs_candidate_context_packet,
        ),
        (
            packets.build_candidate_vector_context_packet(
                domain="warehouse_dispatch",
                vector_ids=("vector:warehouse:001", "vector:warehouse:002"),
                selected_vector_ids=("vector:warehouse:001",),
                allowed_vector_ids=("vector:warehouse:001", "vector:warehouse:002"),
                ranking_summary={"ranked_count": 2},
            ),
            packets.validate_candidate_vector_context_packet,
        ),
        (
            packets.build_avf_attractor_context_packet(
                domain="warehouse_dispatch",
                hard_masks=("policy_block",),
                soft_pressures_planned=("freshness_pressure",),
                risk_pressure={"level": "bounded"},
            ),
            packets.validate_avf_attractor_context_packet,
        ),
        (
            packets.build_orchestrator_route_context_packet(
                domain="warehouse_dispatch",
                allowed_routes=("review_route",),
                required_guards=("temporal_query_required",),
                selected_vector_ids=("vector:warehouse:001",),
            ),
            packets.validate_orchestrator_route_context_packet,
        ),
        (
            packets.build_architect_plan_context_packet(
                domain="warehouse_dispatch",
                source_route_id="route:review",
                allowed_executor_ids=("executor:review",),
                allowed_node_kinds=("review_node",),
                required_validators=("validate_plan_graph_contract",),
            ),
            packets.validate_architect_plan_context_packet,
        ),
        (
            packets.build_fractal_branch_task_context_packet(
                domain="warehouse_dispatch",
                parent_fractal_id="fractal:warehouse:001",
                branch_id="branch:warehouse:review",
                allowed_adapter_name="fake_adapter_metadata",
                expected_receipt_type="mock_review_receipt",
            ),
            packets.validate_fractal_branch_task_context_packet,
        ),
        (
            packets.build_sandbox_receipt_context_packet(
                domain="warehouse_dispatch",
                mock_receipt_refs=({"receipt_id": "mock:receipt:001"},),
                adapter_names=("fake_adapter_metadata",),
            ),
            packets.validate_sandbox_receipt_context_packet,
        ),
        (
            packets.build_root_review_context_packet(
                domain="warehouse_dispatch",
                pre_root_advisory_summary={"status": "bounded"},
                post_vv_summary={"status": "checked"},
                gt_lgt_summary={"status": "reviewed"},
                root_boundary_expectations={"final_authority": "root_only"},
            ),
            packets.validate_root_review_context_packet,
        ),
    )


def test_all_default_builders_create_accepted_packets() -> None:
    for packet, validator in _all_valid_packets():
        validation = validator(packet)

        assert packet["root_final_authority_preserved"] is True
        assert packet["truth_claimed"] is False
        assert packet["authority_claimed"] is False
        assert packet["action_permission_claimed"] is False
        assert packet["final_output_claimed"] is False
        assert packet["connector_command_claimed"] is False
        assert packet["drs_write_claimed"] is False
        assert packet["root_bypass_claimed"] is False
        assert packet["real_world_effects_allowed"] is False
        assert packet["Root remains final authority"] is True
        assert validation["accepted"] is True
        assert validation["reasons"] == ()
        assert validation["packet_type"] == packet["packet_type"]


def test_context_packets_are_generic_not_supplier_payment_specific() -> None:
    warehouse_packet = packets.build_business_request_context_packet(
        domain="warehouse_dispatch",
        request_id="request:warehouse:001",
        business_subject="warehouse dispatch",
    )
    document_packet = packets.build_business_request_context_packet(
        domain="document_readiness",
        request_id="request:document:001",
        business_subject="document readiness",
    )

    assert packets.validate_business_request_context_packet(warehouse_packet)[
        "accepted"
    ] is True
    assert packets.validate_business_request_context_packet(document_packet)[
        "accepted"
    ] is True

    source = Path(packets.__file__).read_text()
    for forbidden in (
        "INV-2042",
        "SH-2042",
        "water_filter",
        "supplier_payment",
        "full_semantic_e2e_supplier_payment",
        "root_outcome:full_semantic_e2e_supplier_payment_v01",
    ):
        assert forbidden not in source


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("truth_claimed", "truth_claimed_forbidden"),
        ("authority_claimed", "authority_claimed_forbidden"),
        ("action_permission_claimed", "action_permission_claimed_forbidden"),
        ("final_output_claimed", "final_output_claimed_forbidden"),
        ("connector_command_claimed", "connector_command_claimed_forbidden"),
        ("drs_write_claimed", "drs_write_claimed_forbidden"),
        ("root_bypass_claimed", "root_bypass_claimed_forbidden"),
        ("direct_adapter_bypass_attempted", "direct_adapter_bypass_attempted_forbidden"),
        ("real_world_effects_allowed", "real_world_effects_allowed_forbidden"),
    ),
)
def test_common_authority_claims_are_rejected(field: str, reason: str) -> None:
    packet = packets.build_business_request_context_packet()
    packet[field] = True

    validation = packets.validate_business_request_context_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("production_ready", "production_readiness_claim_forbidden"),
        ("production_ready_claimed", "production_readiness_claim_forbidden"),
        ("public_wow_ready", "public_wow_readiness_claim_forbidden"),
        ("public_wow_ready_claimed", "public_wow_readiness_claim_forbidden"),
    ),
)
def test_production_and_public_wow_claims_are_rejected(
    field: str,
    reason: str,
) -> None:
    packet = packets.build_business_request_context_packet()
    packet[field] = True

    validation = packets.validate_business_request_context_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]

    false_packet = packets.build_business_request_context_packet()
    false_packet[field] = False
    false_validation = packets.validate_business_request_context_packet(false_packet)

    assert false_validation["accepted"] is True
    assert reason not in false_validation["reasons"]


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("raw_user_text", "unbounded text", "raw_user_text_dump_forbidden"),
        ("raw_gemini_text", "raw role text", "raw_gemini_cross_role_text_forbidden"),
        ("raw_cross_role_text", "raw role text", "raw_gemini_cross_role_text_forbidden"),
        (
            "raw_plan_graph_context",
            {"nodes": []},
            "unbounded_plangraph_context_dump_forbidden",
        ),
        ("api_key", "example-value", "raw_secret_marker_forbidden:api_key"),
    ),
)
def test_raw_dump_and_secret_markers_are_rejected(
    field: str,
    value: object,
    reason: str,
) -> None:
    packet = packets.build_business_request_context_packet()
    packet[field] = value

    validation = packets.validate_business_request_context_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


def test_candidate_vector_selected_ids_must_be_allowed() -> None:
    packet = packets.build_candidate_vector_context_packet(
        vector_ids=("vector:1",),
        selected_vector_ids=("vector:blocked",),
        allowed_vector_ids=("vector:1",),
    )

    validation = packets.validate_candidate_vector_context_packet(packet)

    assert validation["accepted"] is False
    assert "candidate_vector_selected_ids_not_allowed" in validation["reasons"]


def test_evidence_context_requires_candidate_only() -> None:
    packet = packets.build_evidence_context_packet(candidate_only=False)

    validation = packets.validate_evidence_context_packet(packet)

    assert validation["accepted"] is False
    assert "evidence_context_must_be_candidate_only" in validation["reasons"]


def test_avf_context_must_be_advisory_only() -> None:
    packet = packets.build_avf_attractor_context_packet(advisory_only=False)

    validation = packets.validate_avf_attractor_context_packet(packet)

    assert validation["accepted"] is False
    assert "avf_context_must_be_advisory_only" in validation["reasons"]


def test_orchestrator_context_cannot_be_root() -> None:
    packet = packets.build_orchestrator_route_context_packet(orchestrator_is_root=True)

    validation = packets.validate_orchestrator_route_context_packet(packet)

    assert validation["accepted"] is False
    assert "orchestrator_is_not_root" in validation["reasons"]


def test_architect_context_cannot_create_action_commit_packet() -> None:
    packet = packets.build_architect_plan_context_packet(
        creates_action_commit_packet=True
    )

    validation = packets.validate_architect_plan_context_packet(packet)

    assert validation["accepted"] is False
    assert "architect_cannot_create_action_commit_packet" in validation["reasons"]


def test_fractal_branch_context_preserves_child_topology() -> None:
    valid = packets.build_fractal_branch_task_context_packet()
    valid_validation = packets.validate_fractal_branch_task_context_packet(valid)

    assert valid_validation["accepted"] is True
    assert valid["adapter_metadata_only"] is True
    assert valid["returns_to_parent"] is True

    cases = (
        ("child_root_created", True, "fractal_branch_cannot_create_root"),
        (
            "child_final_output_created",
            True,
            "fractal_branch_cannot_create_final_output",
        ),
        (
            "child_action_commit_packet_created",
            True,
            "fractal_branch_cannot_create_action_commit_packet",
        ),
        ("returns_to_parent", False, "fractal_branch_must_return_to_parent"),
        ("adapter_metadata_only", False, "fractal_branch_adapter_must_be_metadata_only"),
        (
            "direct_adapter_bypass_attempted",
            True,
            "direct_adapter_bypass_attempted_forbidden",
        ),
    )
    for field, value, reason in cases:
        packet = packets.build_fractal_branch_task_context_packet()
        packet[field] = value
        validation = packets.validate_fractal_branch_task_context_packet(packet)

        assert validation["accepted"] is False
        assert reason in validation["reasons"]


def test_sandbox_receipt_context_is_mock_only() -> None:
    not_mock = packets.build_sandbox_receipt_context_packet(mock_only=False)
    real_world = packets.build_sandbox_receipt_context_packet(
        real_world_effects_allowed=True
    )
    real_payment_claim = packets.build_sandbox_receipt_context_packet()
    real_payment_claim["payment_executed"] = True

    not_mock_validation = packets.validate_sandbox_receipt_context_packet(not_mock)
    real_world_validation = packets.validate_sandbox_receipt_context_packet(real_world)
    real_payment_validation = packets.validate_sandbox_receipt_context_packet(
        real_payment_claim
    )

    assert not_mock_validation["accepted"] is False
    assert (
        "sandbox_receipt_context_must_be_mock_only"
        in not_mock_validation["reasons"]
    )
    assert "mock_receipt_is_not_real_payment" in not_mock_validation["reasons"]
    assert real_world_validation["accepted"] is False
    assert "real_world_effects_allowed_forbidden" in real_world_validation["reasons"]
    assert real_payment_validation["accepted"] is False
    assert "mock_receipt_is_not_real_payment" in real_payment_validation["reasons"]


@pytest.mark.parametrize(
    "counter_key",
    (
        "connector_called_count",
        "payment_executed_count",
        "real_bank_api_called_count",
    ),
)
def test_sandbox_receipt_real_external_counter_expectations_must_remain_zero(
    counter_key: str,
) -> None:
    valid_packet = packets.build_sandbox_receipt_context_packet()
    valid_validation = packets.validate_sandbox_receipt_context_packet(valid_packet)

    assert valid_validation["accepted"] is True

    invalid_packet = packets.build_sandbox_receipt_context_packet(
        real_external_counter_expectations={counter_key: 1}
    )
    invalid_validation = packets.validate_sandbox_receipt_context_packet(
        invalid_packet
    )

    assert invalid_validation["accepted"] is False
    assert (
        f"sandbox_receipt_real_external_counter_must_remain_zero:{counter_key}"
        in invalid_validation["reasons"]
    )

    zero_packet = packets.build_sandbox_receipt_context_packet(
        real_external_counter_expectations={counter_key: 0}
    )
    zero_validation = packets.validate_sandbox_receipt_context_packet(zero_packet)

    assert zero_validation["accepted"] is True


def test_root_review_creators_are_root_only() -> None:
    final_output_packet = packets.build_root_review_context_packet(
        final_output_creator="delegate"
    )
    action_packet = packets.build_root_review_context_packet(
        action_commit_packet_creator="delegate"
    )

    final_output_validation = packets.validate_root_review_context_packet(
        final_output_packet
    )
    action_packet_validation = packets.validate_root_review_context_packet(
        action_packet
    )

    assert final_output_validation["accepted"] is False
    assert (
        "root_review_final_output_creator_must_be_root_only"
        in final_output_validation["reasons"]
    )
    assert action_packet_validation["accepted"] is False
    assert (
        "root_review_action_packet_creator_must_be_root_mock_approval_gate_only"
        in action_packet_validation["reasons"]
    )


def test_missing_required_fields_are_rejected() -> None:
    packet = packets.build_business_request_context_packet()
    packet.pop("domain")

    validation = packets.validate_business_request_context_packet(packet)

    assert validation["accepted"] is False
    assert "missing_required_context_packet_field:domain" in validation["reasons"]


@pytest.mark.parametrize(
    ("packet_type", "reason"),
    (
        ("FinalOutput", "context_packet_is_not_final_output"),
        ("mock_action_commit_packet", "context_packet_is_not_action_commit_packet"),
    ),
)
def test_context_packet_is_not_final_output_or_action_commit_packet(
    packet_type: str,
    reason: str,
) -> None:
    packet = packets.build_business_request_context_packet()
    packet["packet_type"] = packet_type

    validation = packets.validate_business_request_context_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]
