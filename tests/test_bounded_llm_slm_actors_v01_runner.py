from __future__ import annotations

import subprocess
import sys

import demo.run_bounded_llm_slm_actors_v01 as runner
import hedgehog.bounded_actor_contracts as contracts
from hedgehog.bounded_actor_contracts import (
    ActorBoundaryReport,
    ActorInputEnvelope,
    ActorOutputEnvelope,
    ActorTransitionCheck,
    BoundedActorRole,
    build_actor_boundary_report,
    validate_actor_input,
    validate_actor_output,
    validate_actor_transition,
)


def _root_task_input() -> ActorInputEnvelope:
    return ActorInputEnvelope(
        role="architect",
        input_kind="root_shaped_task",
        source_boundary="root_orchestrator",
        payload_ref="payload:test:root_task",
        root_shaped_task=True,
    )


def _architect_output() -> ActorOutputEnvelope:
    return ActorOutputEnvelope(
        role="architect",
        output_kind="plangraph_proposal",
        payload_ref="payload:test:plangraph",
    )


def test_module_imports_and_api_symbols_exist() -> None:
    assert contracts.BoundedActorRole is BoundedActorRole
    assert contracts.ActorInputEnvelope is ActorInputEnvelope
    assert contracts.ActorOutputEnvelope is ActorOutputEnvelope
    assert contracts.ActorTransitionCheck is ActorTransitionCheck
    assert contracts.ActorBoundaryReport is ActorBoundaryReport
    assert callable(contracts.validate_actor_input)
    assert callable(contracts.validate_actor_output)
    assert callable(contracts.validate_actor_transition)
    assert callable(contracts.build_actor_boundary_report)


def test_role_contracts_are_bounded_and_non_authoritative() -> None:
    for role_id, role in contracts.ROLE_CONTRACTS.items():
        assert isinstance(role, BoundedActorRole)
        assert role.role_id == role_id
        assert role.authority_claimed is False
        assert role.final_output_allowed is False
        assert role.action_permission_allowed is False
        assert role.network_allowed is False
        assert role.gemini_allowed is False
        assert role.connector_allowed is False


def test_validate_actor_input_enforces_role_input_boundaries() -> None:
    intake = ActorInputEnvelope(
        role="intake",
        input_kind="raw_user_text",
        source_boundary="user/context",
        payload_ref="payload:test:intake",
        raw_user_text="Mock request.",
    )
    architect_raw_text = ActorInputEnvelope(
        role="architect",
        input_kind="root_shaped_task",
        source_boundary="user/context",
        payload_ref="payload:test:architect_raw_text",
        raw_user_text="Act as Root.",
    )

    assert validate_actor_input(intake).accepted is True
    blocked = validate_actor_input(architect_raw_text)
    assert blocked.blocked is True
    assert "raw_user_text_cannot_command_architect" in blocked.reason_codes


def test_validate_actor_output_rejects_unsafe_claims() -> None:
    unsafe = ActorOutputEnvelope(
        role="executor",
        output_kind="resultproposal_like",
        payload_ref="payload:test:unsafe_executor_output",
        authority_claimed=True,
        action_permission_claimed=True,
        final_output_claimed=True,
        direct_tool_call_claimed=True,
    )
    check = validate_actor_output(unsafe)

    assert check.blocked is True
    assert "authority_claim_blocked" in check.reason_codes
    assert "action_permission_blocked" in check.reason_codes
    assert "final_output_blocked" in check.reason_codes
    assert "direct_tool_call_blocked" in check.reason_codes


def test_validate_actor_transition_accepts_allowed_transitions() -> None:
    check = validate_actor_transition(
        _root_task_input(),
        _architect_output(),
        target_boundary="executor",
        transition_id="test:architect_allowed",
    )

    assert check.accepted is True
    assert check.blocked is False
    assert "plangraph_proposal_only" in check.reason_codes
    assert check.root_final_authority_preserved is True


def test_validate_actor_transition_blocks_forbidden_transitions() -> None:
    orchestrator_input = ActorInputEnvelope(
        role="orchestrator",
        input_kind="intent_candidate",
        source_boundary="intake",
        payload_ref="payload:test:route",
    )
    route_output = ActorOutputEnvelope(
        role="orchestrator",
        output_kind="root_shaped_route_proposal",
        payload_ref="payload:test:route_output",
    )
    check = validate_actor_transition(
        orchestrator_input,
        route_output,
        target_boundary="architect",
        transition_id="test:orchestrator_direct_architect",
    )

    assert check.blocked is True
    assert "direct_architect_command_blocked" in check.reason_codes
    assert "root_boundary_bypass_blocked" in check.reason_codes


def test_forbidden_final_output_target_boundaries_are_blocked() -> None:
    cases = (
        (
            ActorInputEnvelope(
                role="architect",
                input_kind="root_shaped_task",
                source_boundary="root_orchestrator",
                payload_ref="payload:test:architect_to_final_input",
                root_shaped_task=True,
            ),
            ActorOutputEnvelope(
                role="architect",
                output_kind="plangraph_proposal",
                payload_ref="payload:test:architect_to_final_output",
            ),
            "final_output",
            {"final_output_target_boundary_blocked", "plangraph_must_route_to_executor"},
        ),
        (
            ActorInputEnvelope(
                role="executor",
                input_kind="bounded_plan_graph",
                source_boundary="architect",
                payload_ref="payload:test:executor_to_final_input",
                plan_graph_ref="plan:test",
            ),
            ActorOutputEnvelope(
                role="executor",
                output_kind="resultproposal_like",
                payload_ref="payload:test:executor_to_final_output",
            ),
            "final_output",
            {
                "final_output_target_boundary_blocked",
                "resultproposal_must_route_to_verifier",
            },
        ),
        (
            ActorInputEnvelope(
                role="verifier",
                input_kind="resultproposal_like",
                source_boundary="executor",
                payload_ref="payload:test:verifier_to_final_input",
                result_proposal_ref="rp:test",
            ),
            ActorOutputEnvelope(
                role="verifier",
                output_kind="vv_report",
                payload_ref="payload:test:verifier_to_final_output",
            ),
            "final_output",
            {"final_output_target_boundary_blocked", "vv_report_must_route_to_gt_boundary"},
        ),
        (
            ActorInputEnvelope(
                role="gt_boundary",
                input_kind="vv_report",
                source_boundary="verifier",
                payload_ref="payload:test:gt_to_final_input",
            ),
            ActorOutputEnvelope(
                role="gt_boundary",
                output_kind="gt_report",
                payload_ref="payload:test:gt_to_final_output",
            ),
            "final_output",
            {"final_output_target_boundary_blocked", "gt_report_must_route_to_root_return"},
        ),
    )

    for actor_input, actor_output, target_boundary, expected_reasons in cases:
        check = validate_actor_transition(
            actor_input,
            actor_output,
            target_boundary=target_boundary,
        )
        assert check.blocked is True
        assert expected_reasons <= set(check.reason_codes)


def test_invalid_non_final_target_boundaries_are_blocked() -> None:
    cases = (
        (
            ActorInputEnvelope(
                role="architect",
                input_kind="root_shaped_task",
                source_boundary="root_orchestrator",
                payload_ref="payload:test:architect_to_root_return_input",
                root_shaped_task=True,
            ),
            ActorOutputEnvelope(
                role="architect",
                output_kind="plangraph_proposal",
                payload_ref="payload:test:architect_to_root_return_output",
            ),
            "root_return",
            "plangraph_must_route_to_executor",
        ),
        (
            ActorInputEnvelope(
                role="executor",
                input_kind="bounded_plan_graph",
                source_boundary="architect",
                payload_ref="payload:test:executor_to_root_return_input",
                plan_graph_ref="plan:test",
            ),
            ActorOutputEnvelope(
                role="executor",
                output_kind="resultproposal_like",
                payload_ref="payload:test:executor_to_root_return_output",
            ),
            "root_return",
            "resultproposal_must_route_to_verifier",
        ),
        (
            ActorInputEnvelope(
                role="verifier",
                input_kind="resultproposal_like",
                source_boundary="executor",
                payload_ref="payload:test:verifier_to_root_return_input",
                result_proposal_ref="rp:test",
            ),
            ActorOutputEnvelope(
                role="verifier",
                output_kind="vv_report",
                payload_ref="payload:test:verifier_to_root_return_output",
            ),
            "root_return",
            "vv_report_must_route_to_gt_boundary",
        ),
        (
            ActorInputEnvelope(
                role="gt_boundary",
                input_kind="vv_report",
                source_boundary="verifier",
                payload_ref="payload:test:gt_to_architect_input",
            ),
            ActorOutputEnvelope(
                role="gt_boundary",
                output_kind="gt_report",
                payload_ref="payload:test:gt_to_architect_output",
            ),
            "architect",
            "gt_report_must_route_to_root_return",
        ),
    )

    for actor_input, actor_output, target_boundary, expected_reason in cases:
        check = validate_actor_transition(
            actor_input,
            actor_output,
            target_boundary=target_boundary,
        )
        assert check.blocked is True
        assert expected_reason in check.reason_codes


def test_valid_canonical_actor_chain_target_boundaries_are_accepted() -> None:
    chain = (
        (
            ActorInputEnvelope(
                role="intake",
                input_kind="raw_user_text",
                source_boundary="user/context",
                payload_ref="payload:test:chain_intake_input",
                raw_user_text="Mock certificate request.",
            ),
            ActorOutputEnvelope(
                role="intake",
                output_kind="structured_intent_candidate",
                payload_ref="payload:test:chain_intake_output",
            ),
            "root_orchestrator",
        ),
        (
            ActorInputEnvelope(
                role="orchestrator",
                input_kind="intent_candidate",
                source_boundary="intake",
                payload_ref="payload:test:chain_orchestrator_input",
            ),
            ActorOutputEnvelope(
                role="orchestrator",
                output_kind="root_shaped_route_proposal",
                payload_ref="payload:test:chain_orchestrator_output",
            ),
            "root_orchestrator",
        ),
        (
            ActorInputEnvelope(
                role="architect",
                input_kind="root_shaped_task",
                source_boundary="root_orchestrator",
                payload_ref="payload:test:chain_architect_input",
                root_shaped_task=True,
            ),
            ActorOutputEnvelope(
                role="architect",
                output_kind="plangraph_proposal",
                payload_ref="payload:test:chain_architect_output",
            ),
            "executor",
        ),
        (
            ActorInputEnvelope(
                role="executor",
                input_kind="bounded_plan_graph",
                source_boundary="architect",
                payload_ref="payload:test:chain_executor_input",
                plan_graph_ref="plan:test",
            ),
            ActorOutputEnvelope(
                role="executor",
                output_kind="resultproposal_like",
                payload_ref="payload:test:chain_executor_output",
            ),
            "post_vv",
        ),
        (
            ActorInputEnvelope(
                role="verifier",
                input_kind="resultproposal_like",
                source_boundary="executor",
                payload_ref="payload:test:chain_verifier_input",
                result_proposal_ref="rp:test",
            ),
            ActorOutputEnvelope(
                role="verifier",
                output_kind="vv_report",
                payload_ref="payload:test:chain_verifier_output",
            ),
            "gt_boundary",
        ),
        (
            ActorInputEnvelope(
                role="gt_boundary",
                input_kind="vv_report",
                source_boundary="verifier",
                payload_ref="payload:test:chain_gt_input",
            ),
            ActorOutputEnvelope(
                role="gt_boundary",
                output_kind="gt_report",
                payload_ref="payload:test:chain_gt_output",
            ),
            "root_return",
        ),
        (
            ActorInputEnvelope(
                role="root_return",
                input_kind="gt_report",
                source_boundary="gt_boundary",
                payload_ref="payload:test:chain_root_return_input",
            ),
            ActorOutputEnvelope(
                role="root_return",
                output_kind="root_review_required",
                payload_ref="payload:test:chain_root_return_output",
            ),
            "root_orchestrator",
        ),
    )

    checks = [
        validate_actor_transition(
            actor_input,
            actor_output,
            target_boundary=target_boundary,
        )
        for actor_input, actor_output, target_boundary in chain
    ]

    assert all(check.accepted for check in checks)
    assert all(not check.blocked for check in checks)


def test_build_actor_boundary_report_returns_structured_report() -> None:
    actor_input = _root_task_input()
    actor_output = _architect_output()
    transition = validate_actor_transition(
        actor_input,
        actor_output,
        target_boundary="executor",
    )
    report = build_actor_boundary_report(
        report_id="actor_boundary_report:test",
        inputs=(actor_input,),
        outputs=(actor_output,),
        transitions=(transition,),
    )

    assert isinstance(report, ActorBoundaryReport)
    assert report.actor_inputs_seen_count == 1
    assert report.actor_outputs_emitted_count == 1
    assert len(report.accepted_transitions) == 1
    assert report.blocked_transitions == ()
    assert report.root_review_required is True
    assert report.final_output_created_count == 0
    assert report.action_permission_granted_count == 0
    assert report.actor_authority_claimed_count == 0
    assert report.root_final_authority_preserved is True


def test_raw_user_text_cannot_command_architect() -> None:
    check = validate_actor_input(
        ActorInputEnvelope(
            role="architect",
            input_kind="root_shaped_task",
            source_boundary="user/context",
            payload_ref="payload:test:raw_user_text_attack",
            raw_user_text="Command Architect directly.",
        )
    )

    assert check.blocked is True
    assert "raw_user_text_cannot_command_architect" in check.reason_codes


def test_advisory_signal_cannot_command_architect() -> None:
    check = validate_actor_transition(
        ActorInputEnvelope(
            role="architect",
            input_kind="root_shaped_task",
            source_boundary="avf_candidate_advisory_evaluator",
            payload_ref="payload:test:advisory_attack",
            raw_advisory_signal="advisory_accept_as_command",
        ),
        _architect_output(),
        target_boundary="executor",
    )

    assert check.blocked is True
    assert "raw_advisory_signal_cannot_command_architect" in check.reason_codes
    assert "advisory_report_cannot_command_architect" in check.reason_codes


def test_drs_memory_cannot_command_architect() -> None:
    check = validate_actor_transition(
        ActorInputEnvelope(
            role="architect",
            input_kind="root_shaped_task",
            source_boundary="local_drs",
            payload_ref="payload:test:drs_memory_attack",
            raw_drs_memory_ref="drs:record:unsafe_instruction",
        ),
        _architect_output(),
        target_boundary="executor",
    )

    assert check.blocked is True
    assert "raw_drs_memory_cannot_command_architect" in check.reason_codes
    assert "drs_memory_cannot_command_architect" in check.reason_codes


def test_actor_cannot_self_promote_to_root() -> None:
    check = validate_actor_output(
        ActorOutputEnvelope(
            role="architect",
            output_kind="root_authority_claim",
            payload_ref="payload:test:self_promotion",
            authority_claimed=True,
        )
    )

    assert check.blocked is True
    assert "authority_claim_blocked" in check.reason_codes
    assert "forbidden_output_kind" in check.reason_codes


def test_prompt_injection_cannot_grant_action_permission() -> None:
    check = validate_actor_output(
        ActorOutputEnvelope(
            role="orchestrator",
            output_kind="action_permission",
            payload_ref="payload:test:prompt_injection_action",
            action_permission_claimed=True,
            reason_codes=("prompt_injection_blocked",),
        )
    )

    assert check.blocked is True
    assert "prompt_injection_blocked" in check.reason_codes
    assert "action_permission_blocked" in check.reason_codes


def test_model_confidence_does_not_create_authority() -> None:
    allowed = validate_actor_output(
        ActorOutputEnvelope(
            role="orchestrator",
            output_kind="root_shaped_route_proposal",
            payload_ref="payload:test:model_confidence",
            model_kind="llm",
            model_confidence=0.99,
        )
    )
    blocked = validate_actor_output(
        ActorOutputEnvelope(
            role="orchestrator",
            output_kind="root_shaped_route_proposal",
            payload_ref="payload:test:model_confidence_authority",
            model_kind="llm",
            model_confidence=0.99,
            authority_claimed=True,
        )
    )

    assert allowed.accepted is True
    assert "model_confidence_advisory_only" in allowed.reason_codes
    assert blocked.blocked is True
    assert "authority_claim_blocked" in blocked.reason_codes


def test_no_actor_can_create_finaloutput() -> None:
    for role in contracts.ROLE_IDS:
        check = validate_actor_output(
            ActorOutputEnvelope(
                role=role,
                output_kind="final_output",
                payload_ref=f"payload:test:{role}:final_attempt",
                final_output_claimed=True,
            )
        )
        assert check.blocked is True
        assert "final_output_blocked" in check.reason_codes


def test_no_actor_can_mutate_manifest_or_transition_matrix() -> None:
    for output_kind, flag, expected_reason in (
        ("manifest_mutation", "manifest_mutation_claimed", "manifest_mutation_blocked"),
        (
            "transition_matrix_mutation",
            "transition_matrix_mutation_claimed",
            "transition_matrix_mutation_blocked",
        ),
    ):
        check = validate_actor_output(
            ActorOutputEnvelope(
                role="orchestrator",
                output_kind=output_kind,
                payload_ref=f"payload:test:{output_kind}",
                **{flag: True},
            )
        )
        assert check.blocked is True
        assert expected_reason in check.reason_codes


def test_no_actor_can_call_network_gemini_or_connectors() -> None:
    for output_kind, expected_reason in (
        ("network_call", "network_not_allowed_v0_1"),
        ("gemini_call", "gemini_not_allowed_v0_1"),
        ("connector_call", "connector_not_allowed_v0_1"),
    ):
        check = validate_actor_output(
            ActorOutputEnvelope(
                role="executor",
                output_kind=output_kind,
                payload_ref=f"payload:test:{output_kind}",
            )
        )
        assert check.blocked is True
        assert expected_reason in check.reason_codes

    input_check = validate_actor_input(
        ActorInputEnvelope(
            role="executor",
            input_kind="bounded_plan_graph",
            source_boundary="architect",
            payload_ref="payload:test:executor_input_flags",
            plan_graph_ref="plan:test",
            network_allowed=True,
            gemini_allowed=True,
            external_action_allowed=True,
        )
    )
    assert input_check.blocked is True
    assert "network_not_allowed_v0_1" in input_check.reason_codes
    assert "gemini_not_allowed_v0_1" in input_check.reason_codes
    assert "external_action_not_allowed_v0_1" in input_check.reason_codes


def test_runner_result_passes_required_counters_and_scenarios() -> None:
    result = runner.run_all_scenarios()
    counters = result["counters"]

    assert result["scenarios_total"] == 12
    assert result["scenarios_passed"] == result["scenarios_total"]
    assert {scenario["scenario_id"] for scenario in result["scenarios"]} == set(
        runner.SCENARIOS
    )
    assert all(scenario["status"] == "PASS" for scenario in result["scenarios"])
    assert counters["final_output_created_count"] == 0
    assert counters["action_permission_granted_count"] == 0
    assert counters["actor_authority_claimed_count"] == 0
    assert counters["llm_truth_claimed_count"] == 0
    assert counters["slm_truth_claimed_count"] == 0
    assert counters["model_confidence_authority_claimed_count"] == 0
    assert counters["prompt_injection_escalation_count"] == 0
    assert counters["actor_self_promotion_count"] == 0
    assert counters["raw_advisory_command_accepted_count"] == 0
    assert counters["raw_drs_memory_instruction_accepted_count"] == 0
    assert counters["root_boundary_bypass_count"] == 0
    assert counters["post_vv_bypass_count"] == 0
    assert counters["gt_bypass_count"] == 0
    assert counters["manifest_mutation_count"] == 0
    assert counters["transition_matrix_mutation_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["connector_side_effect_count"] == 0
    assert counters["root_final_authority_preserved_count"] == result["scenarios_total"]


def test_main_returns_zero_and_command_output_has_pass() -> None:
    assert runner.main() == 0

    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_bounded_llm_slm_actors_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    expected_markers = (
        "HEDGEHOG OS — BOUNDED LLM/SLM ACTORS v0.1",
        "FINAL STATUS: PASS",
        "scenarios_total: 12",
        "scenarios_passed: 12",
        "final_output_created_count: 0",
        "action_permission_granted_count: 0",
        "actor_authority_claimed_count: 0",
        "llm_truth_claimed_count: 0",
        "slm_truth_claimed_count: 0",
        "prompt_injection_escalation_count: 0",
        "actor_self_promotion_count: 0",
        "raw_advisory_command_accepted_count: 0",
        "raw_drs_memory_instruction_accepted_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "root_final_authority_preserved_count: 12",
    )
    for marker in expected_markers:
        assert marker in completed.stdout


def test_runner_output_includes_all_scenarios() -> None:
    output = runner.render_report(runner.run_all_scenarios())
    for scenario in runner.SCENARIOS:
        assert scenario in output


def test_runner_output_does_not_claim_public_or_runtime_completion() -> None:
    output = runner.render_report(runner.run_all_scenarios())
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "runtime " + "complete",
        "Real Semantic Runtime MVP " + "implemented",
        "Gemini " + "activated",
        "FinalOutput " + "created",
        "action permission " + "granted",
        "actor is " + "authority",
        "LLM is " + "authority",
        "SLM is " + "authority",
    )

    for marker in forbidden:
        assert marker not in output
