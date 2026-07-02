from __future__ import annotations

from copy import deepcopy
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
            packets.build_bounded_semantic_evidence_packet(
                domain="warehouse_dispatch",
                source_route_id="review_route",
                selected_vector_ids=("vector:warehouse:001",),
            ),
            packets.validate_bounded_semantic_evidence_packet,
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


def _semantic_item(
    text: str = "Generic bounded evidence remains candidate only.",
    *,
    evidence_kind: str = "observed_fact",
) -> dict:
    return packets.semantic_evidence_item(
        text,
        source="runtime_canonicalization",
        evidence_kind=evidence_kind,
    )


def _valid_bounded_semantic_evidence_packet() -> dict:
    return packets.build_bounded_semantic_evidence_packet(
        source_route_id="route:generic_review",
        source_proposal_id="proposal:generic_review",
        source_context_packet_id="context_packet:orchestrator_route:generic",
        selected_vector_ids=("vector:generic_review",),
        required_guards=("ContextPacket validation", "Root final authority"),
    )


def _valid_route_context_for_bsep() -> dict:
    return packets.build_orchestrator_route_context_packet(
        packet_id="context_packet:orchestrator_route:generic",
        allowed_routes=("route:generic_review",),
        selected_vector_ids=("vector:generic_review",),
        required_guards=("ContextPacket validation", "Root final authority"),
    )


def test_bounded_semantic_evidence_packet_builder_produces_valid_packet() -> None:
    packet = _valid_bounded_semantic_evidence_packet()

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is True
    assert validation["reasons"] == ()
    assert packet["packet_type"] == packets.BOUNDED_SEMANTIC_EVIDENCE_PACKET_TYPE
    assert (
        packet["created_by"]
        == packets.BOUNDED_SEMANTIC_EVIDENCE_PACKET_CREATED_BY_DEFAULT
    )
    assert packet["truth_claimed"] is False
    assert packet["authority_claimed"] is False
    assert packet["action_permission_claimed"] is False
    assert packet["final_output_claimed"] is False
    assert packet["connector_command_claimed"] is False
    assert packet["action_commit_packet_claimed"] is False
    assert packet["root_bypass_claimed"] is False
    assert packet["raw_user_text_included"] is False
    assert packet["raw_cross_role_text_included"] is False
    assert packet["ContextPacket is not truth"] is True
    assert packet["ContextPacket is not authority"] is True
    assert packet["BoundedSemanticEvidencePacket is not truth"] is True
    assert packet["BoundedSemanticEvidencePacket is not authority"] is True
    assert packet["BoundedSemanticEvidencePacket is not FinalOutput"] is True
    assert packet["BoundedSemanticEvidencePacket is not ActionCommitPacket"] is True
    assert packet["Evidence packet is not action permission"] is True
    assert packet["Root remains final authority"] is True
    assert "action_permission" not in packet
    assert "connector_command" not in packet
    assert "final_output" not in packet


def test_bounded_semantic_evidence_packet_item_helper_shape() -> None:
    item = packets.semantic_evidence_item(
        "  Bounded fact  ",
        source="validated_context_packet",
        evidence_kind="observed_fact",
        confidence_label="medium",
    )

    assert item == {
        "text": "Bounded fact",
        "source": "validated_context_packet",
        "evidence_kind": "observed_fact",
        "confidence_label": "medium",
        "candidate_only": True,
        "raw_quote": False,
    }


def test_bounded_semantic_evidence_packet_validator_rejects_missing_required_fields() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet.pop("packet_id")
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_missing_required_field:packet_id"
        in validation["reasons"]
    )

    packet = _valid_bounded_semantic_evidence_packet()
    packet.pop("source_route_id")
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_missing_required_field:source_route_id"
        in validation["reasons"]
    )


def test_bounded_semantic_evidence_packet_validator_rejects_wrong_packet_type() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet["packet_type"] = "OtherPacket"

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert "unexpected_packet_type:BoundedSemanticEvidencePacket" in validation["reasons"]


def test_bounded_semantic_evidence_packet_creator_must_be_runtime() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet["created_by"] = "Gemini/provider"

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_packet_creator_must_be_runtime"
        in validation["reasons"]
    )


def test_bounded_semantic_evidence_packet_rejects_production_and_public_wow_claims() -> None:
    cases = (
        ("production_ready", "production_readiness_claim_forbidden"),
        ("production_ready_claimed", "production_readiness_claim_forbidden"),
        ("public_wow_ready", "public_wow_readiness_claim_forbidden"),
        ("public_wow_ready_claimed", "public_wow_readiness_claim_forbidden"),
    )

    for field, reason in cases:
        packet = _valid_bounded_semantic_evidence_packet()
        packet[field] = True
        validation = packets.validate_bounded_semantic_evidence_packet(packet)

        assert validation["accepted"] is False
        assert reason in validation["reasons"]

        false_packet = _valid_bounded_semantic_evidence_packet()
        false_packet[field] = False
        false_validation = packets.validate_bounded_semantic_evidence_packet(
            false_packet
        )

        assert false_validation["accepted"] is True
        assert reason not in false_validation["reasons"]


def test_bounded_semantic_evidence_packet_schema_version_must_match() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet["schema_version"] = "wrong_version"

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert "bounded_semantic_evidence_schema_version_invalid" in validation["reasons"]


def test_bounded_semantic_evidence_packet_roles_are_fixed() -> None:
    valid = _valid_bounded_semantic_evidence_packet()
    valid_validation = packets.validate_bounded_semantic_evidence_packet(valid)

    assert valid_validation["accepted"] is True

    source_cases = ("provider", "gemini")
    for role in source_cases:
        packet = _valid_bounded_semantic_evidence_packet()
        packet["source_role"] = role
        validation = packets.validate_bounded_semantic_evidence_packet(packet)

        assert validation["accepted"] is False
        assert (
            "bounded_semantic_evidence_source_role_must_be_orchestrator"
            in validation["reasons"]
        )

    target_cases = ("root", "provider")
    for role in target_cases:
        packet = _valid_bounded_semantic_evidence_packet()
        packet["target_role"] = role
        validation = packets.validate_bounded_semantic_evidence_packet(packet)

        assert validation["accepted"] is False
        assert (
            "bounded_semantic_evidence_target_role_must_be_architect"
            in validation["reasons"]
        )


def test_bounded_semantic_evidence_packet_boundaries_are_required() -> None:
    cases = (
        (
            "BoundedSemanticEvidencePacket is not truth",
            "bounded_semantic_evidence_packet_truth_boundary_required",
        ),
        (
            "BoundedSemanticEvidencePacket is not authority",
            "bounded_semantic_evidence_packet_authority_boundary_required",
        ),
        (
            "Root remains final authority",
            "bounded_semantic_evidence_root_final_authority_required",
        ),
    )

    for field, reason in cases:
        packet = _valid_bounded_semantic_evidence_packet()
        packet.pop(field)
        validation = packets.validate_bounded_semantic_evidence_packet(packet)

        assert validation["accepted"] is False
        assert reason in validation["reasons"]


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        (
            "raw_user_request",
            "raw request",
            "bounded_semantic_evidence_raw_user_text_forbidden",
        ),
        (
            "raw_user_text",
            "raw text",
            "bounded_semantic_evidence_raw_user_text_forbidden",
        ),
        (
            "raw_cross_role_text",
            "raw role text",
            "bounded_semantic_evidence_raw_cross_role_text_forbidden",
        ),
        (
            "raw_gemini_text",
            "raw provider text",
            "bounded_semantic_evidence_raw_gemini_text_forbidden",
        ),
    ),
)
def test_bounded_semantic_evidence_packet_rejects_raw_text_and_raw_cross_role_text(
    field: str,
    value: object,
    reason: str,
) -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet[field] = value

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("full_runner_state_dump", "unbounded_context_dump_forbidden"),
        ("unbounded_context_dump", "unbounded_context_dump_forbidden"),
        ("raw_plan_graph_context", "unbounded_plangraph_context_dump_forbidden"),
        ("raw_plangraph_context", "unbounded_plangraph_context_dump_forbidden"),
    ),
)
def test_bounded_semantic_evidence_packet_rejects_unbounded_raw_dumps(
    field: str,
    reason: str,
) -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet[field] = {"dump": "too much context"}

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("truth_claimed", "bounded_semantic_evidence_truth_claim_forbidden"),
        ("authority_claimed", "bounded_semantic_evidence_authority_claim_forbidden"),
        (
            "action_permission_claimed",
            "bounded_semantic_evidence_action_permission_claim_forbidden",
        ),
        ("final_output_claimed", "bounded_semantic_evidence_final_output_claim_forbidden"),
        (
            "connector_command_claimed",
            "bounded_semantic_evidence_connector_command_claim_forbidden",
        ),
        (
            "action_commit_packet_claimed",
            "bounded_semantic_evidence_action_commit_packet_claim_forbidden",
        ),
        ("root_bypass_claimed", "bounded_semantic_evidence_root_bypass_claim_forbidden"),
    ),
)
def test_bounded_semantic_evidence_packet_rejects_claims(
    field: str,
    reason: str,
) -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet[field] = True

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


@pytest.mark.parametrize(
    ("mutator", "reason"),
    (
        (
            lambda packet: packet.update({"observed_semantic_facts": ()}),
            "bounded_semantic_evidence_empty_field:observed_semantic_facts",
        ),
        (
            lambda packet: packet.update(
                {"observed_semantic_facts": (_semantic_item("   "),)}
            ),
            "bounded_semantic_evidence_item_empty_text:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].pop("source"),
            "bounded_semantic_evidence_item_missing_source:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].pop("evidence_kind"),
            "bounded_semantic_evidence_item_missing_kind:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].update(
                {"source": "unbounded_source"}
            ),
            "bounded_semantic_evidence_item_source_not_allowed:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].update(
                {"evidence_kind": "unbounded_kind"}
            ),
            "bounded_semantic_evidence_item_kind_not_allowed:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].update(
                {"confidence_label": "certain"}
            ),
            "bounded_semantic_evidence_item_confidence_label_not_allowed:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].update(
                {"candidate_only": False}
            ),
            "bounded_semantic_evidence_item_candidate_only_must_be_true:observed_semantic_facts",
        ),
        (
            lambda packet: packet["observed_semantic_facts"][0].update(
                {"raw_quote": True}
            ),
            "bounded_semantic_evidence_item_raw_quote_must_be_false:observed_semantic_facts",
        ),
    ),
)
def test_bounded_semantic_evidence_packet_rejects_empty_and_invalid_items(
    mutator: object,
    reason: str,
) -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    mutator(packet)

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


def test_bounded_semantic_evidence_packet_rejects_overlong_and_too_many_items() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet["observed_semantic_facts"] = (
        _semantic_item("x" * (packets.BOUNDED_SEMANTIC_EVIDENCE_MAX_ITEM_TEXT_LENGTH + 1)),
    )
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_item_text_too_long:observed_semantic_facts"
        in validation["reasons"]
    )

    packet = _valid_bounded_semantic_evidence_packet()
    packet["observed_semantic_facts"] = tuple(
        _semantic_item(f"item {index}")
        for index in range(
            packets.BOUNDED_SEMANTIC_EVIDENCE_MAX_ITEMS_PER_FIELD + 1
        )
    )
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_too_many_items:observed_semantic_facts"
        in validation["reasons"]
    )

    packet = _valid_bounded_semantic_evidence_packet()
    for field in packets.BOUNDED_SEMANTIC_EVIDENCE_ITEM_FIELDS:
        packet[field] = tuple(
            packets.semantic_evidence_item(
                f"{field} item {index}",
                source="runtime_canonicalization",
                evidence_kind="observed_fact",
            )
            for index in range(7)
        )
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert "bounded_semantic_evidence_too_many_total_items" in validation["reasons"]


def test_bounded_semantic_evidence_packet_source_lineage_matches_context() -> None:
    route_context = _valid_route_context_for_bsep()
    proposal = {"proposal_id": "proposal:generic_review"}
    rationale_validation = {"accepted": True}
    packet = _valid_bounded_semantic_evidence_packet()

    validation = packets.validate_bounded_semantic_evidence_packet(
        packet,
        route_context_packet=route_context,
        orchestrator_proposal=proposal,
        structured_rationale_validation=rationale_validation,
    )

    assert validation["accepted"] is True

    route_mismatch = deepcopy(packet)
    route_mismatch["source_route_id"] = "route:other"
    route_validation = packets.validate_bounded_semantic_evidence_packet(
        route_mismatch,
        route_context_packet=route_context,
    )
    assert route_validation["accepted"] is False
    assert "bounded_semantic_evidence_source_route_mismatch" in route_validation["reasons"]

    proposal_mismatch = deepcopy(packet)
    proposal_mismatch["source_proposal_id"] = "proposal:other"
    proposal_validation = packets.validate_bounded_semantic_evidence_packet(
        proposal_mismatch,
        orchestrator_proposal=proposal,
    )
    assert proposal_validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_source_proposal_mismatch"
        in proposal_validation["reasons"]
    )

    context_mismatch = deepcopy(packet)
    context_mismatch["source_context_packet_id"] = "context_packet:other"
    context_validation = packets.validate_bounded_semantic_evidence_packet(
        context_mismatch,
        route_context_packet=route_context,
    )
    assert context_validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_source_context_packet_mismatch"
        in context_validation["reasons"]
    )

    rationale_validation = packets.validate_bounded_semantic_evidence_packet(
        packet,
        structured_rationale_validation={"accepted": False},
    )
    assert rationale_validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_source_rationale_missing_or_unaccepted"
        in rationale_validation["reasons"]
    )


def test_bounded_semantic_evidence_packet_selected_vectors_must_match_route_context() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet["selected_vector_ids"] = ("vector:not_from_route",)

    validation = packets.validate_bounded_semantic_evidence_packet(
        packet,
        route_context_packet=_valid_route_context_for_bsep(),
    )

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_selected_vectors_must_be_subset_of_route_vectors"
        in validation["reasons"]
    )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        (
            "selected_vector_ids",
            (" ",),
            "bounded_semantic_evidence_empty_item:selected_vector_ids",
        ),
        (
            "selected_vector_ids",
            ({"id": "vector"},),
            "bounded_semantic_evidence_item_must_be_string:selected_vector_ids",
        ),
        (
            "required_guards",
            (" ",),
            "bounded_semantic_evidence_empty_item:required_guards",
        ),
        (
            "required_guards",
            ({"guard": "Root"},),
            "bounded_semantic_evidence_item_must_be_string:required_guards",
        ),
    ),
)
def test_bounded_semantic_evidence_packet_selected_vectors_and_guards_require_non_empty_strings(
    field: str,
    value: object,
    reason: str,
) -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet[field] = value

    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]

    valid_packet = _valid_bounded_semantic_evidence_packet()
    valid_packet["selected_vector_ids"] = ("vector:generic_review",)
    valid_packet["required_guards"] = ("Root final authority",)
    valid_validation = packets.validate_bounded_semantic_evidence_packet(valid_packet)

    assert valid_validation["accepted"] is True


def test_bounded_semantic_evidence_packet_rejects_real_world_action_surface() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    packet["nested"] = {"connector_command": ""}
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_real_world_action_surface_forbidden"
        in validation["reasons"]
    )

    packet = _valid_bounded_semantic_evidence_packet()
    packet["observed_semantic_facts"] = (
        _semantic_item("real_world_effect remains forbidden"),
    )
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is False
    assert (
        "bounded_semantic_evidence_real_world_action_surface_forbidden"
        in validation["reasons"]
    )

    safe_packet = _valid_bounded_semantic_evidence_packet()
    safe_packet["action_permission_claimed"] = False
    safe_packet["connector_command_claimed"] = False
    safe_packet["final_output_claimed"] = False
    safe_packet["real_world_effects_allowed"] = False
    safe_validation = packets.validate_bounded_semantic_evidence_packet(safe_packet)

    assert safe_validation["accepted"] is True


def test_bounded_semantic_evidence_packet_is_not_truth_authority_final_action_permission() -> None:
    packet = _valid_bounded_semantic_evidence_packet()
    validation = packets.validate_bounded_semantic_evidence_packet(packet)

    assert validation["accepted"] is True
    assert packet["ContextPacket is not truth"] is True
    assert packet["ContextPacket is not authority"] is True
    assert packet["BoundedSemanticEvidencePacket is not truth"] is True
    assert packet["BoundedSemanticEvidencePacket is not authority"] is True
    assert packet["BoundedSemanticEvidencePacket is not FinalOutput"] is True
    assert packet["Evidence packet is not action permission"] is True
    assert packet["Root remains final authority"] is True


def test_context_packets_core_no_bsep_fixture_hardcodes() -> None:
    source = Path(packets.__file__).read_text()
    for forbidden in (
        "manual-live-unknown-request-real-gemini-007",
        "gemini-2.5-flash",
        "city archive",
        "sealed historical artifact",
        "HOTEL-17",
        "ROBOT-CLEAN-2042",
        "R-101",
        "supplier payment",
        "warehouse",
        "certificate",
    ):
        assert forbidden not in source


def test_context_packets_core_no_provider_network_imports() -> None:
    source = Path(packets.__file__).read_text()
    for forbidden in (
        "google",
        "genai",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "subprocess",
        "provider_adapter",
        "run_live_unknown_request",
    ):
        assert forbidden not in source
