from __future__ import annotations

from pathlib import Path

import pytest

import hedgehog.structured_rationale as rationale


def _assert_common_non_authority_claims(artifact: dict) -> None:
    assert artifact["truth_claimed"] is False
    assert artifact["authority_claimed"] is False
    assert artifact["action_permission_claimed"] is False
    assert artifact["final_output_claimed"] is False
    assert artifact["connector_command_claimed"] is False
    assert artifact["drs_write_claimed"] is False
    assert artifact["action_commit_packet_claimed"] is False
    assert artifact["root_bypass_claimed"] is False
    assert artifact["root_final_authority_preserved"] is True
    assert artifact["Root remains final authority"] is True


def test_valid_orchestrator_structured_rationale_is_accepted() -> None:
    artifact = rationale.build_orchestrator_structured_rationale()

    validation = rationale.validate_orchestrator_structured_rationale(artifact)

    assert artifact["rationale_type"] == "structured_orchestrator_rationale"
    assert artifact["schema_version"] == "structured_rationale_v0.1"
    for field in rationale.ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS:
        assert field in artifact
    _assert_common_non_authority_claims(artifact)
    assert artifact["orchestrator_is_root"] is False
    assert artifact["creates_action_commit_packet"] is False
    assert artifact["calls_connectors"] is False
    assert validation["accepted"] is True
    assert validation["reasons"] == ()
    assert validation["rationale_type"] == artifact["rationale_type"]


def test_valid_architect_structured_rationale_is_accepted() -> None:
    artifact = rationale.build_architect_structured_rationale()

    validation = rationale.validate_architect_structured_rationale(artifact)

    assert artifact["rationale_type"] == "structured_architect_rationale"
    assert artifact["schema_version"] == "structured_rationale_v0.1"
    for field in rationale.ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS:
        assert field in artifact
    _assert_common_non_authority_claims(artifact)
    assert artifact["architect_is_root"] is False
    assert artifact["creates_action_commit_packet"] is False
    assert artifact["calls_connectors"] is False
    assert validation["accepted"] is True
    assert validation["reasons"] == ()
    assert validation["rationale_type"] == artifact["rationale_type"]

    artifact_text = repr(artifact)
    assert "bounded_semantic_work" in artifact_text
    assert "semantic_work_contract" in artifact_text
    assert "RuntimeExecutionTopology" in artifact_text
    assert "owned by local runtime" in artifact_text
    assert "Plan" + "Graph" not in artifact_text
    assert "plan" + "_" + "graph" not in artifact_text
    assert "Attractor" + "Packet" not in artifact_text
    assert "attractor" + "_" + "packet" not in artifact_text


@pytest.mark.parametrize(
    "retired_keyword",
    (
        "bounded_" + "plan" + "_" + "graph",
        "attractor" + "_" + "packet",
    ),
)
def test_architect_retired_vocabulary_has_no_compatibility_keyword(
    retired_keyword: str,
) -> None:
    with pytest.raises(TypeError):
        rationale.build_architect_structured_rationale(
            **{retired_keyword: ({"shape": "proposal"},)}
        )


def test_non_mapping_rationale_rejected() -> None:
    validation = rationale.validate_orchestrator_structured_rationale(("not", "mapping"))

    assert validation["accepted"] is False
    assert "structured_rationale_must_be_mapping" in validation["reasons"]
    assert validation["rationale_type"] is None


def test_wrong_schema_version_rejected() -> None:
    orchestrator = rationale.build_orchestrator_structured_rationale()
    orchestrator["schema_version"] = "wrong"

    orchestrator_validation = rationale.validate_orchestrator_structured_rationale(
        orchestrator
    )

    assert orchestrator_validation["accepted"] is False
    assert (
        "structured_rationale_schema_version_invalid"
        in orchestrator_validation["reasons"]
    )

    architect = rationale.build_architect_structured_rationale()
    architect["schema_version"] = "wrong"

    architect_validation = rationale.validate_architect_structured_rationale(architect)

    assert architect_validation["accepted"] is False
    assert (
        "structured_rationale_schema_version_invalid"
        in architect_validation["reasons"]
    )


def test_wrong_rationale_type_rejected() -> None:
    orchestrator = rationale.build_orchestrator_structured_rationale()
    orchestrator["rationale_type"] = "structured_architect_rationale"

    orchestrator_validation = rationale.validate_orchestrator_structured_rationale(
        orchestrator
    )

    assert orchestrator_validation["accepted"] is False
    assert any(
        reason.startswith("structured_rationale_unexpected_type:")
        for reason in orchestrator_validation["reasons"]
    )

    architect = rationale.build_architect_structured_rationale()
    architect["rationale_type"] = "structured_orchestrator_rationale"

    architect_validation = rationale.validate_architect_structured_rationale(architect)

    assert architect_validation["accepted"] is False
    assert any(
        reason.startswith("structured_rationale_unexpected_type:")
        for reason in architect_validation["reasons"]
    )


def test_each_missing_orchestrator_required_field_rejected() -> None:
    for field in rationale.ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS:
        artifact = rationale.build_orchestrator_structured_rationale()
        artifact.pop(field)

        validation = rationale.validate_orchestrator_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            f"structured_rationale_missing_required_field:{field}"
            in validation["reasons"]
        )


def test_each_missing_architect_required_field_rejected() -> None:
    for field in rationale.ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS:
        artifact = rationale.build_architect_structured_rationale()
        artifact.pop(field)

        validation = rationale.validate_architect_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            f"structured_rationale_missing_required_field:{field}"
            in validation["reasons"]
        )


def test_missing_role_boundary_fields_rejected() -> None:
    for field in (
        "orchestrator_is_root",
        "creates_action_commit_packet",
        "calls_connectors",
    ):
        artifact = rationale.build_orchestrator_structured_rationale()
        artifact.pop(field)

        validation = rationale.validate_orchestrator_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            f"structured_rationale_missing_required_field:{field}"
            in validation["reasons"]
        )

    for field in (
        "architect_is_root",
        "creates_action_commit_packet",
        "calls_connectors",
    ):
        artifact = rationale.build_architect_structured_rationale()
        artifact.pop(field)

        validation = rationale.validate_architect_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            f"structured_rationale_missing_required_field:{field}"
            in validation["reasons"]
        )


def test_top_level_raw_string_dump_rejected() -> None:
    artifact = rationale.build_orchestrator_structured_rationale()
    artifact["route_selection_reason"] = "x" * 900

    validation = rationale.validate_orchestrator_structured_rationale(artifact)

    assert validation["accepted"] is False
    assert (
        "structured_rationale_raw_text_forbidden" in validation["reasons"]
        or "structured_rationale_unbounded_dump_forbidden" in validation["reasons"]
    )


def test_raw_keys_rejected_recursively() -> None:
    raw_keys = (
        "raw_user_text",
        "raw_" + "ge" + "mini_text",
        "raw_cross_role_text",
        "full_runner_state_dump",
        "raw_plan_graph_context",
    )
    for raw_key in raw_keys:
        artifact = rationale.build_orchestrator_structured_rationale(
            observed_semantics=({"nested": {raw_key: "blocked"}},)
        )

        validation = rationale.validate_orchestrator_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            "structured_rationale_raw_text_forbidden" in validation["reasons"]
            or "structured_rationale_unbounded_dump_forbidden"
            in validation["reasons"]
        )


def test_raw_marker_values_rejected_recursively() -> None:
    raw_values = (
        "raw_user_text",
        "raw_" + "ge" + "mini_text",
        "raw_cross_role_text",
    )
    for raw_value in raw_values:
        artifact = rationale.build_orchestrator_structured_rationale(
            observed_semantics=({"harmless_key": raw_value},)
        )

        validation = rationale.validate_orchestrator_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert "structured_rationale_raw_text_forbidden" in validation["reasons"]

    unbounded_values = (
        "full_runner_state_dump",
        "raw_plan_graph_context",
    )
    for unbounded_value in unbounded_values:
        artifact = rationale.build_architect_structured_rationale(
            plan_shape_reason=({"harmless_key": unbounded_value},)
        )

        validation = rationale.validate_architect_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            "structured_rationale_unbounded_dump_forbidden"
            in validation["reasons"]
        )


def test_secret_markers_rejected_recursively() -> None:
    for marker in ("api_key", "secret", "token", "password", "private_key"):
        artifact = rationale.build_architect_structured_rationale(
            forbidden_surface_review=({"nested": {marker: "blocked"}},)
        )

        validation = rationale.validate_architect_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert (
            f"structured_rationale_secret_marker_forbidden:{marker}"
            in validation["reasons"]
        )


def test_authority_action_final_claims_rejected() -> None:
    cases = (
        ("truth_claimed", "structured_rationale_truth_claim_forbidden"),
        ("authority_claimed", "structured_rationale_authority_claim_forbidden"),
        (
            "action_permission_claimed",
            "structured_rationale_action_permission_claim_forbidden",
        ),
        ("final_output_claimed", "structured_rationale_final_output_claim_forbidden"),
        (
            "connector_command_claimed",
            "structured_rationale_connector_command_forbidden",
        ),
        ("drs_write_claimed", "structured_rationale_drs_write_forbidden"),
        (
            "action_commit_packet_claimed",
            "structured_rationale_action_commit_packet_forbidden",
        ),
        ("root_bypass_claimed", "structured_rationale_root_bypass_forbidden"),
    )
    for field, reason in cases:
        artifact = rationale.build_orchestrator_structured_rationale()
        artifact[field] = True

        validation = rationale.validate_orchestrator_structured_rationale(artifact)

        assert validation["accepted"] is False
        assert reason in validation["reasons"]


def test_role_boundary_rejected() -> None:
    orchestrator_root = rationale.build_orchestrator_structured_rationale()
    orchestrator_root["orchestrator_is_root"] = True
    assert "orchestrator_is_not_root" in rationale.validate_orchestrator_structured_rationale(
        orchestrator_root
    )["reasons"]

    architect_root = rationale.build_architect_structured_rationale()
    architect_root["architect_is_root"] = True
    assert "architect_is_not_root" in rationale.validate_architect_structured_rationale(
        architect_root
    )["reasons"]

    orchestrator_packet = rationale.build_orchestrator_structured_rationale()
    orchestrator_packet["creates_action_commit_packet"] = True
    assert (
        "orchestrator_cannot_create_action_commit_packet"
        in rationale.validate_orchestrator_structured_rationale(orchestrator_packet)[
            "reasons"
        ]
    )

    architect_packet = rationale.build_architect_structured_rationale()
    architect_packet["creates_action_commit_packet"] = True
    assert (
        "architect_cannot_create_action_commit_packet"
        in rationale.validate_architect_structured_rationale(architect_packet)[
            "reasons"
        ]
    )

    orchestrator_connector = rationale.build_orchestrator_structured_rationale()
    orchestrator_connector["calls_connectors"] = True
    assert (
        "orchestrator_cannot_call_connectors"
        in rationale.validate_orchestrator_structured_rationale(
            orchestrator_connector
        )["reasons"]
    )

    architect_connector = rationale.build_architect_structured_rationale()
    architect_connector["calls_connectors"] = True
    assert (
        "architect_cannot_call_connectors"
        in rationale.validate_architect_structured_rationale(architect_connector)[
            "reasons"
        ]
    )


def test_root_review_and_root_authority_rejected_if_broken() -> None:
    root_review = rationale.build_orchestrator_structured_rationale()
    root_review["root_review_required"] = False
    assert (
        "root_review_required_must_be_true"
        in rationale.validate_orchestrator_structured_rationale(root_review)[
            "reasons"
        ]
    )

    root_preserved = rationale.build_orchestrator_structured_rationale()
    root_preserved["root_final_authority_preserved"] = False
    assert (
        "root_final_authority_must_be_preserved"
        in rationale.validate_orchestrator_structured_rationale(root_preserved)[
            "reasons"
        ]
    )

    root_phrase = rationale.build_architect_structured_rationale()
    root_phrase["Root remains final authority"] = False
    assert (
        "root_final_authority_must_be_preserved"
        in rationale.validate_architect_structured_rationale(root_phrase)["reasons"]
    )


def test_unbounded_rationale_rejected() -> None:
    huge_list = tuple({"item": str(index)} for index in range(75))
    artifact = rationale.build_architect_structured_rationale(
        node_selection_reasoning=huge_list
    )

    validation = rationale.validate_architect_structured_rationale(artifact)

    assert validation["accepted"] is False
    assert "structured_rationale_unbounded_dump_forbidden" in validation["reasons"]

    huge_string = rationale.build_orchestrator_structured_rationale(
        observed_semantics=({"summary": "x" * 900},)
    )
    string_validation = rationale.validate_orchestrator_structured_rationale(
        huge_string
    )

    assert string_validation["accepted"] is False
    assert (
        "structured_rationale_unbounded_dump_forbidden"
        in string_validation["reasons"]
    )


def test_universal_domain_smoke() -> None:
    examples = (
        {
            "domain": "hotel robot access",
            "subject": "night access review",
        },
        {
            "domain": "museum artifact transfer",
            "subject": "crate handoff review",
        },
        {
            "domain": "cycling route safety",
            "subject": "route hazard review",
        },
    )
    for example in examples:
        orchestrator = rationale.build_orchestrator_structured_rationale(
            observed_semantics=(
                {
                    "domain": example["domain"],
                    "subject": example["subject"],
                },
            ),
            route_selection_reason=(
                {
                    "route": "bounded_review",
                    "reason": "review remains advisory",
                },
            ),
        )
        architect = rationale.build_architect_structured_rationale(
            plan_shape_reason=(
                {
                    "domain": example["domain"],
                    "shape": "bounded_review_plan",
                },
            )
        )

        assert rationale.validate_orchestrator_structured_rationale(orchestrator)[
            "accepted"
        ] is True
        assert rationale.validate_architect_structured_rationale(architect)[
            "accepted"
        ] is True

    source = Path(rationale.__file__).read_text()
    for forbidden in (
        "INV-2042",
        "SH-2042",
        "water_filter",
        "supplier_payment",
        "full_semantic_e2e_supplier_payment",
    ):
        assert forbidden not in source


def test_no_runtime_integration() -> None:
    module_source = Path(rationale.__file__).read_text()
    test_source = Path(__file__).read_text()

    assert "run_full" + "_semantic_e2e_v01" not in module_source
    assert "run_full" + "_semantic_e2e_v01" not in test_source
    assert "context" + "_packets" not in module_source
    assert "import " + "demo" not in module_source
    assert "import " + "demo" not in test_source
