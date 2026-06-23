from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


ROLE_IDS = (
    "intake",
    "orchestrator",
    "architect",
    "executor",
    "verifier",
    "gt_boundary",
    "root_return",
)

FORBIDDEN_OUTPUT_KINDS = (
    "final_output",
    "action_permission",
    "direct_tool_call",
    "manifest_mutation",
    "transition_matrix_mutation",
    "network_call",
    "gemini_call",
    "connector_call",
    "root_authority_claim",
)

ROOT_BOUNDARIES = {
    "root",
    "root_orchestrator",
    "root_boundary",
    "root/orchestrator",
    "root/orchestrator review",
    "root_shaped_route",
}

ROOT_RETURN_BOUNDARIES = {
    "root_return",
    "root return",
    "root_return_boundary",
    "root return boundary",
}

EXECUTOR_BOUNDARIES = {
    "executor",
    "executor_actor",
    "executor actor",
}

VERIFIER_BOUNDARIES = {
    "verifier",
    "verifier_actor",
    "verifier actor",
    "post_vv",
    "post vv",
    "post_vv_boundary",
    "post vv boundary",
}

GT_BOUNDARIES = {
    "gt",
    "gt_boundary",
    "gt boundary",
    "gt_validator",
    "gtvalidator",
}

FINAL_OUTPUT_TARGET_BOUNDARIES = {
    "final_output",
    "finaloutput",
    "root_final",
    "root_final_output",
    "final",
    "user_final",
}

COUNTER_KEYS = (
    "actor_inputs_seen_count",
    "actor_outputs_emitted_count",
    "intake_outputs_count",
    "route_proposals_count",
    "plangraph_proposals_count",
    "result_proposals_count",
    "validation_reports_count",
    "root_review_required_count",
    "final_output_created_count",
    "action_permission_granted_count",
    "actor_authority_claimed_count",
    "llm_truth_claimed_count",
    "slm_truth_claimed_count",
    "model_confidence_authority_claimed_count",
    "prompt_injection_escalation_count",
    "actor_self_promotion_count",
    "raw_advisory_command_accepted_count",
    "raw_drs_memory_instruction_accepted_count",
    "root_boundary_bypass_count",
    "post_vv_bypass_count",
    "gt_bypass_count",
    "manifest_mutation_count",
    "transition_matrix_mutation_count",
    "network_used_count",
    "gemini_used_count",
    "connector_side_effect_count",
    "root_final_authority_preserved_count",
)


@dataclass(frozen=True)
class BoundedActorRole:
    role_id: str
    allowed_input_kinds: tuple[str, ...]
    allowed_output_kinds: tuple[str, ...]
    forbidden_output_kinds: tuple[str, ...] = FORBIDDEN_OUTPUT_KINDS
    authority_claimed: bool = False
    final_output_allowed: bool = False
    action_permission_allowed: bool = False
    network_allowed: bool = False
    gemini_allowed: bool = False
    connector_allowed: bool = False

    @property
    def role_name(self) -> str:
        return self.role_id


ROLE_CONTRACTS: dict[str, BoundedActorRole] = {
    "intake": BoundedActorRole(
        role_id="intake",
        allowed_input_kinds=(
            "raw_user_text",
            "raw_user_context",
            "user_context",
            "user_event",
            "context",
        ),
        allowed_output_kinds=(
            "structured_intent_candidate",
            "missing_info_flag",
            "intake_context",
        ),
    ),
    "orchestrator": BoundedActorRole(
        role_id="orchestrator",
        allowed_input_kinds=(
            "intent_candidate",
            "advisory_report",
            "drs_avf_advisory_report",
            "route_review_request",
            "root_review_request",
        ),
        allowed_output_kinds=(
            "root_shaped_route_proposal",
            "user_clarification_request",
            "route_proposal_to_root",
        ),
    ),
    "architect": BoundedActorRole(
        role_id="architect",
        allowed_input_kinds=("root_shaped_task", "root_shaped_route"),
        allowed_output_kinds=("plangraph_proposal",),
    ),
    "executor": BoundedActorRole(
        role_id="executor",
        allowed_input_kinds=("bounded_plan_graph",),
        allowed_output_kinds=("resultproposal_like", "result_proposal"),
    ),
    "verifier": BoundedActorRole(
        role_id="verifier",
        allowed_input_kinds=("resultproposal_like", "result_proposal"),
        allowed_output_kinds=("vv_report", "validation_report"),
    ),
    "gt_boundary": BoundedActorRole(
        role_id="gt_boundary",
        allowed_input_kinds=("vv_report", "validation_report"),
        allowed_output_kinds=("gt_report", "gt_advisory_selection_report"),
    ),
    "root_return": BoundedActorRole(
        role_id="root_return",
        allowed_input_kinds=("gt_report", "advisory_report", "root_return_bundle"),
        allowed_output_kinds=("root_review_required", "root_return_bundle"),
    ),
}


@dataclass(frozen=True)
class ActorInputEnvelope:
    role: str | BoundedActorRole
    input_kind: str
    source_boundary: str
    payload_ref: str
    root_shaped_task: bool = False
    route_id: str | None = None
    plan_graph_ref: str | None = None
    result_proposal_ref: str | None = None
    advisory_report_ref: str | None = None
    time_envelope: dict[str, Any] | None = None
    context_refs: tuple[dict[str, Any], ...] = ()
    permission_scope: str = "local_deterministic"
    network_allowed: bool = False
    gemini_allowed: bool = False
    external_action_allowed: bool = False
    raw_user_text: str | None = None
    raw_advisory_signal: str | None = None
    raw_drs_memory_ref: str | None = None
    model_kind: str | None = None
    model_confidence: float | None = None


@dataclass(frozen=True)
class ActorOutputEnvelope:
    role: str | BoundedActorRole
    output_kind: str
    payload_ref: str
    reason_codes: tuple[str, ...] = ()
    truth_claimed: bool = False
    authority_claimed: bool = False
    action_permission_claimed: bool = False
    final_output_claimed: bool = False
    direct_tool_call_claimed: bool = False
    manifest_mutation_claimed: bool = False
    transition_matrix_mutation_claimed: bool = False
    root_review_required: bool = True
    model_kind: str | None = None
    model_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActorTransitionCheck:
    transition_id: str
    from_role: str
    source_boundary: str
    to_role: str
    target_boundary: str
    input_kind: str
    output_kind: str
    accepted: bool
    blocked: bool
    reason_codes: tuple[str, ...]
    root_boundary_required: bool = True
    post_vv_required: bool = False
    gt_required: bool = False
    root_final_authority_preserved: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "from_role": self.from_role,
            "source_boundary": self.source_boundary,
            "to_role": self.to_role,
            "target_boundary": self.target_boundary,
            "input_kind": self.input_kind,
            "output_kind": self.output_kind,
            "accepted": self.accepted,
            "blocked": self.blocked,
            "reason_codes": list(self.reason_codes),
            "root_boundary_required": self.root_boundary_required,
            "post_vv_required": self.post_vv_required,
            "gt_required": self.gt_required,
            "root_final_authority_preserved": self.root_final_authority_preserved,
        }


@dataclass(frozen=True)
class ActorBoundaryReport:
    report_id: str
    actor_inputs_seen_count: int
    actor_outputs_emitted_count: int
    accepted_transitions: tuple[ActorTransitionCheck, ...]
    blocked_transitions: tuple[ActorTransitionCheck, ...]
    reason_codes: tuple[str, ...]
    root_review_required: bool = True
    final_output_created_count: int = 0
    action_permission_granted_count: int = 0
    actor_authority_claimed_count: int = 0
    root_final_authority_preserved: bool = True
    counters: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "actor_inputs_seen_count": self.actor_inputs_seen_count,
            "actor_outputs_emitted_count": self.actor_outputs_emitted_count,
            "accepted_transitions": [
                transition.to_dict() for transition in self.accepted_transitions
            ],
            "blocked_transitions": [
                transition.to_dict() for transition in self.blocked_transitions
            ],
            "reason_codes": list(self.reason_codes),
            "root_review_required": self.root_review_required,
            "final_output_created_count": self.final_output_created_count,
            "action_permission_granted_count": self.action_permission_granted_count,
            "actor_authority_claimed_count": self.actor_authority_claimed_count,
            "root_final_authority_preserved": self.root_final_authority_preserved,
            "counters": dict(self.counters),
        }


def _role_id(role: str | BoundedActorRole | None) -> str:
    if isinstance(role, BoundedActorRole):
        return role.role_id
    return str(role or "")


def _norm(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _boundary_key(value: str | None) -> str:
    normalized = _norm(value)
    return normalized.replace("-", "_")


def _is_root_boundary(value: str | None) -> bool:
    return _boundary_key(value) in ROOT_BOUNDARIES


def _is_root_or_return_boundary(value: str | None) -> bool:
    key = _boundary_key(value)
    return key in ROOT_BOUNDARIES or key in ROOT_RETURN_BOUNDARIES


def _dedupe(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _check(
    *,
    transition_id: str,
    from_role: str,
    source_boundary: str,
    to_role: str,
    target_boundary: str,
    input_kind: str,
    output_kind: str,
    blocking_reasons: Iterable[str],
    reason_codes: Iterable[str],
    post_vv_required: bool = False,
    gt_required: bool = False,
) -> ActorTransitionCheck:
    reasons = _dedupe((*reason_codes, *blocking_reasons))
    blocked = bool(tuple(blocking_reasons))
    return ActorTransitionCheck(
        transition_id=transition_id,
        from_role=from_role,
        source_boundary=source_boundary,
        to_role=to_role,
        target_boundary=target_boundary,
        input_kind=input_kind,
        output_kind=output_kind,
        accepted=not blocked,
        blocked=blocked,
        reason_codes=reasons,
        root_boundary_required=True,
        post_vv_required=post_vv_required,
        gt_required=gt_required,
        root_final_authority_preserved=True,
    )


def get_actor_role(role: str | BoundedActorRole) -> BoundedActorRole:
    role_id = _role_id(role)
    if role_id not in ROLE_CONTRACTS:
        raise ValueError(f"unknown bounded actor role: {role_id}")
    return ROLE_CONTRACTS[role_id]


def validate_actor_input(envelope: ActorInputEnvelope) -> ActorTransitionCheck:
    role_id = _role_id(envelope.role)
    reasons: list[str] = []
    blocking: list[str] = []
    role = ROLE_CONTRACTS.get(role_id)

    if role is None:
        blocking.append("unknown_actor_role")
    else:
        if envelope.input_kind not in role.allowed_input_kinds:
            blocking.append("input_kind_not_allowed_for_role")

    if envelope.network_allowed:
        blocking.append("network_not_allowed_v0_1")
    if envelope.gemini_allowed:
        blocking.append("gemini_not_allowed_v0_1")
    if envelope.external_action_allowed:
        blocking.append("external_action_not_allowed_v0_1")

    if envelope.model_kind in {"llm", "slm"} and envelope.model_confidence is not None:
        reasons.append("model_confidence_advisory_only")

    if envelope.raw_user_text is not None:
        if role_id == "intake":
            reasons.append("raw_user_text_allowed_for_intake_only")
        else:
            blocking.append("raw_user_text_forbidden_for_role")
            if role_id == "architect":
                blocking.append("raw_user_text_cannot_command_architect")

    if envelope.raw_advisory_signal is not None:
        reasons.append("raw_advisory_signal_is_signal_only")
        if role_id == "architect":
            blocking.append("raw_advisory_signal_cannot_command_architect")
        elif role_id != "orchestrator":
            blocking.append("raw_advisory_signal_invalid_for_role")

    if envelope.raw_drs_memory_ref is not None:
        reasons.append("drs_memory_not_instruction_authority")
        if role_id == "architect":
            blocking.append("raw_drs_memory_cannot_command_architect")
        elif role_id != "orchestrator":
            blocking.append("raw_drs_memory_invalid_for_role")

    if role_id == "architect":
        if not envelope.root_shaped_task:
            blocking.append("root_shaped_task_required")
        if _norm(envelope.source_boundary) not in ROOT_BOUNDARIES:
            blocking.append("root_boundary_required")

    if role_id == "executor" and not envelope.plan_graph_ref:
        blocking.append("bounded_plangraph_required")

    if role_id == "verifier" and not envelope.result_proposal_ref:
        blocking.append("resultproposal_required")

    if role_id == "orchestrator" and envelope.raw_advisory_signal is not None:
        reasons.append("advisory_signal_not_command")

    if role_id == "orchestrator" and envelope.raw_drs_memory_ref is not None:
        reasons.append("drs_memory_signal_not_instruction")

    return _check(
        transition_id=f"input:{role_id}:{envelope.input_kind}:{envelope.payload_ref}",
        from_role=envelope.source_boundary,
        source_boundary=envelope.source_boundary,
        to_role=role_id,
        target_boundary=role_id,
        input_kind=envelope.input_kind,
        output_kind="",
        blocking_reasons=blocking,
        reason_codes=reasons or ("actor_input_boundary_checked",),
    )


def validate_actor_output(envelope: ActorOutputEnvelope) -> ActorTransitionCheck:
    role_id = _role_id(envelope.role)
    reasons = list(envelope.reason_codes)
    blocking: list[str] = []
    role = ROLE_CONTRACTS.get(role_id)

    if role is None:
        blocking.append("unknown_actor_role")
    else:
        if envelope.output_kind not in role.allowed_output_kinds:
            blocking.append("output_kind_not_allowed_for_role")
        if envelope.output_kind in role.forbidden_output_kinds:
            blocking.append("forbidden_output_kind")

    if envelope.output_kind == "final_output" or envelope.final_output_claimed:
        blocking.append("final_output_blocked")
    if envelope.output_kind == "action_permission" or envelope.action_permission_claimed:
        blocking.append("action_permission_blocked")
    if envelope.truth_claimed:
        blocking.append("truth_claim_blocked")
    if envelope.authority_claimed:
        blocking.append("authority_claim_blocked")
    if envelope.direct_tool_call_claimed or envelope.output_kind == "direct_tool_call":
        blocking.append("direct_tool_call_blocked")
    if envelope.manifest_mutation_claimed or envelope.output_kind == "manifest_mutation":
        blocking.append("manifest_mutation_blocked")
    if (
        envelope.transition_matrix_mutation_claimed
        or envelope.output_kind == "transition_matrix_mutation"
    ):
        blocking.append("transition_matrix_mutation_blocked")
    if envelope.output_kind == "network_call":
        blocking.append("network_not_allowed_v0_1")
    if envelope.output_kind == "gemini_call":
        blocking.append("gemini_not_allowed_v0_1")
    if envelope.output_kind == "connector_call":
        blocking.append("connector_not_allowed_v0_1")
    if not envelope.root_review_required:
        blocking.append("root_review_required")

    if envelope.model_kind in {"llm", "slm"} and envelope.model_confidence is not None:
        reasons.append("model_confidence_advisory_only")
    if envelope.model_kind == "llm":
        reasons.append("llm_role_capable_not_activated")
    if envelope.model_kind == "slm":
        reasons.append("slm_role_capable_not_activated")

    return _check(
        transition_id=f"output:{role_id}:{envelope.output_kind}:{envelope.payload_ref}",
        from_role=role_id,
        source_boundary=role_id,
        to_role="root_return",
        target_boundary="root_return",
        input_kind="",
        output_kind=envelope.output_kind,
        blocking_reasons=blocking,
        reason_codes=reasons or ("actor_output_boundary_checked",),
        post_vv_required=role_id in {"architect", "executor"},
        gt_required=role_id in {"architect", "executor", "verifier"},
    )


def validate_actor_transition(
    actor_input: ActorInputEnvelope | None = None,
    actor_output: ActorOutputEnvelope | None = None,
    *,
    from_role: str | None = None,
    source_boundary: str | None = None,
    to_role: str | None = None,
    target_boundary: str | None = None,
    input_kind: str | None = None,
    output_kind: str | None = None,
    transition_id: str | None = None,
) -> ActorTransitionCheck:
    if actor_input is None:
        inferred_role = to_role or from_role or "orchestrator"
        actor_input = ActorInputEnvelope(
            role=inferred_role,
            input_kind=input_kind or "root_review_request",
            source_boundary=source_boundary or from_role or "unknown",
            payload_ref=f"payload:{transition_id or 'transition'}:input",
        )
    if actor_output is None:
        actor_output = ActorOutputEnvelope(
            role=to_role or _role_id(actor_input.role),
            output_kind=output_kind or "",
            payload_ref=f"payload:{transition_id or 'transition'}:output",
        )

    input_check = validate_actor_input(actor_input)
    output_check = validate_actor_output(actor_output)
    input_role = _role_id(actor_input.role)
    output_role = _role_id(actor_output.role)
    reasons = [*input_check.reason_codes, *output_check.reason_codes]
    blocking: list[str] = []
    if input_check.blocked:
        blocking.extend(input_check.reason_codes)
    if output_check.blocked:
        blocking.extend(output_check.reason_codes)
    if input_role != output_role:
        blocking.append("actor_role_confusion_blocked")

    resolved_target = target_boundary or "root_return"
    normalized_target = _boundary_key(resolved_target)
    if normalized_target in FINAL_OUTPUT_TARGET_BOUNDARIES:
        blocking.append("final_output_target_boundary_blocked")

    if input_role == "intake" and actor_output.output_kind in {
        "structured_intent_candidate",
        "missing_info_flag",
        "intake_context",
    }:
        if not _is_root_or_return_boundary(resolved_target):
            blocking.append("intake_output_must_return_to_root_or_orchestrator")

    if input_role == "orchestrator" and output_role == "orchestrator":
        if actor_output.output_kind in {
            "root_shaped_route_proposal",
            "route_proposal_to_root",
        }:
            reasons.append("route_proposal_requires_root_boundary")
            if not _is_root_or_return_boundary(resolved_target):
                blocking.append("root_boundary_bypass_blocked")
                if normalized_target == "architect":
                    blocking.append("direct_architect_command_blocked")

    if input_role == "architect" and actor_output.output_kind == "plangraph_proposal":
        if normalized_target not in EXECUTOR_BOUNDARIES:
            blocking.append("plangraph_must_route_to_executor")

    if input_role == "executor" and actor_output.output_kind in {
        "resultproposal_like",
        "result_proposal",
    }:
        if normalized_target not in VERIFIER_BOUNDARIES:
            blocking.append("resultproposal_must_route_to_verifier")

    if input_role == "verifier" and actor_output.output_kind in {
        "vv_report",
        "validation_report",
    }:
        if normalized_target not in GT_BOUNDARIES:
            blocking.append("vv_report_must_route_to_gt_boundary")

    if input_role == "gt_boundary" and actor_output.output_kind in {
        "gt_report",
        "gt_advisory_selection_report",
    }:
        if not _is_root_or_return_boundary(resolved_target):
            blocking.append("gt_report_must_route_to_root_return")

    if input_role == "root_return" and actor_output.output_kind in {
        "root_review_required",
        "root_return_bundle",
    }:
        if not _is_root_boundary(resolved_target):
            blocking.append("root_return_must_return_to_root")

    if input_role == "architect" and actor_input.raw_advisory_signal is not None:
        blocking.append("advisory_report_cannot_command_architect")
    if input_role == "architect" and actor_input.raw_drs_memory_ref is not None:
        blocking.append("drs_memory_cannot_command_architect")

    if actor_output.output_kind == "plangraph_proposal":
        reasons.append("plangraph_proposal_only")
    if actor_output.output_kind in {"resultproposal_like", "result_proposal"}:
        reasons.append("resultproposal_only")
    if actor_output.output_kind in {"vv_report", "validation_report"}:
        reasons.append("post_vv_validation_only")
    if actor_output.output_kind in {"gt_report", "gt_advisory_selection_report"}:
        reasons.append("gt_report_not_root_final")

    return _check(
        transition_id=transition_id
        or f"transition:{input_role}:{actor_input.input_kind}:{actor_output.output_kind}",
        from_role=input_role,
        source_boundary=actor_input.source_boundary,
        to_role=output_role,
        target_boundary=resolved_target,
        input_kind=actor_input.input_kind,
        output_kind=actor_output.output_kind,
        blocking_reasons=blocking,
        reason_codes=reasons or ("actor_transition_checked",),
        post_vv_required=output_role in {"architect", "executor"},
        gt_required=output_role in {"architect", "executor", "verifier"},
    )


def _zero_counters() -> dict[str, int]:
    return {key: 0 for key in COUNTER_KEYS}


def build_actor_boundary_report(
    *,
    report_id: str = "actor_boundary_report:v0_1",
    inputs: Iterable[ActorInputEnvelope] = (),
    outputs: Iterable[ActorOutputEnvelope] = (),
    transitions: Iterable[ActorTransitionCheck] = (),
) -> ActorBoundaryReport:
    input_list = tuple(inputs)
    output_list = tuple(outputs)
    transition_list = tuple(transitions)
    accepted = tuple(transition for transition in transition_list if transition.accepted)
    blocked = tuple(transition for transition in transition_list if transition.blocked)
    counters = _zero_counters()
    counters["actor_inputs_seen_count"] = len(input_list)
    counters["actor_outputs_emitted_count"] = len(output_list)
    counters["intake_outputs_count"] = sum(
        1 for output in output_list if _role_id(output.role) == "intake"
    )
    counters["route_proposals_count"] = sum(
        1 for output in output_list if output.output_kind == "root_shaped_route_proposal"
    )
    counters["plangraph_proposals_count"] = sum(
        1 for output in output_list if output.output_kind == "plangraph_proposal"
    )
    counters["result_proposals_count"] = sum(
        1
        for output in output_list
        if output.output_kind in {"resultproposal_like", "result_proposal"}
    )
    counters["validation_reports_count"] = sum(
        1
        for output in output_list
        if output.output_kind in {"vv_report", "validation_report"}
    )
    counters["root_review_required_count"] = sum(
        1 for output in output_list if output.root_review_required
    )

    for output in output_list:
        accepted_output = any(
            transition.accepted
            and transition.output_kind == output.output_kind
            and transition.from_role == _role_id(output.role)
            for transition in accepted
        )
        if accepted_output and (output.output_kind == "final_output" or output.final_output_claimed):
            counters["final_output_created_count"] += 1
        if accepted_output and output.action_permission_claimed:
            counters["action_permission_granted_count"] += 1
        if accepted_output and output.authority_claimed:
            counters["actor_authority_claimed_count"] += 1
        if accepted_output and output.model_kind == "llm" and output.truth_claimed:
            counters["llm_truth_claimed_count"] += 1
        if accepted_output and output.model_kind == "slm" and output.truth_claimed:
            counters["slm_truth_claimed_count"] += 1
        if accepted_output and output.model_confidence is not None and output.authority_claimed:
            counters["model_confidence_authority_claimed_count"] += 1
        if accepted_output and output.manifest_mutation_claimed:
            counters["manifest_mutation_count"] += 1
        if accepted_output and output.transition_matrix_mutation_claimed:
            counters["transition_matrix_mutation_count"] += 1
        if accepted_output and output.output_kind == "network_call":
            counters["network_used_count"] += 1
        if accepted_output and output.output_kind == "gemini_call":
            counters["gemini_used_count"] += 1
        if accepted_output and output.output_kind == "connector_call":
            counters["connector_side_effect_count"] += 1

    for transition in accepted:
        if "prompt_injection_blocked" in transition.reason_codes:
            counters["prompt_injection_escalation_count"] += 1
        if "actor_self_promotion_blocked" in transition.reason_codes:
            counters["actor_self_promotion_count"] += 1
        if (
            transition.to_role == "architect"
            and "raw_advisory_signal_is_signal_only" in transition.reason_codes
        ):
            counters["raw_advisory_command_accepted_count"] += 1
        if (
            transition.to_role == "architect"
            and "drs_memory_not_instruction_authority" in transition.reason_codes
        ):
            counters["raw_drs_memory_instruction_accepted_count"] += 1
        if "root_boundary_bypass_blocked" in transition.reason_codes:
            counters["root_boundary_bypass_count"] += 1
        if "post_vv_bypass_blocked" in transition.reason_codes:
            counters["post_vv_bypass_count"] += 1
        if "gt_bypass_blocked" in transition.reason_codes:
            counters["gt_bypass_count"] += 1

    root_final_authority_preserved = (
        counters["final_output_created_count"] == 0
        and counters["action_permission_granted_count"] == 0
        and counters["actor_authority_claimed_count"] == 0
        and all(transition.root_final_authority_preserved for transition in transition_list)
    )
    counters["root_final_authority_preserved_count"] = (
        1 if root_final_authority_preserved else 0
    )
    reason_codes = _dedupe(
        reason
        for transition in transition_list
        for reason in transition.reason_codes
    )
    return ActorBoundaryReport(
        report_id=report_id,
        actor_inputs_seen_count=len(input_list),
        actor_outputs_emitted_count=len(output_list),
        accepted_transitions=accepted,
        blocked_transitions=blocked,
        reason_codes=reason_codes,
        root_review_required=True,
        final_output_created_count=counters["final_output_created_count"],
        action_permission_granted_count=counters["action_permission_granted_count"],
        actor_authority_claimed_count=counters["actor_authority_claimed_count"],
        root_final_authority_preserved=root_final_authority_preserved,
        counters=counters,
    )
