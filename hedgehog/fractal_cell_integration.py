from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from hedgehog.bounded_actor_contracts import (
    ActorBoundaryReport,
    ActorInputEnvelope,
    ActorOutputEnvelope,
    ActorTransitionCheck,
    build_actor_boundary_report,
    validate_actor_input,
    validate_actor_output,
    validate_actor_transition,
)
from hedgehog.fractal_dag_executor import run_fractal_dag_executor
from hedgehog.gt_validator import validate_gt
from hedgehog.time_model import utc_now_iso

try:
    from hedgehog.post_vv import validate_result_proposals as _runtime_validate_result_proposals
except ModuleNotFoundError:
    _runtime_validate_result_proposals = None


FINAL_TARGET_ALIASES = {
    "final_output",
    "finaloutput",
    "root_final",
    "root_final_output",
    "final",
    "user_final",
    "user_finaloutput",
    "user_final_output",
}

COUNTER_KEYS = (
    "cells_started_count",
    "child_actor_inputs_seen_count",
    "child_actor_outputs_emitted_count",
    "child_result_proposals_count",
    "child_validation_reports_count",
    "child_gt_reports_count",
    "parent_return_reports_count",
    "root_review_required_count",
    "post_vv_fallback_used_count",
    "final_output_created_count",
    "action_permission_granted_count",
    "child_root_claimed_count",
    "child_authority_claimed_count",
    "child_finaloutput_claimed_count",
    "child_action_permission_claimed_count",
    "child_actor_self_promotion_count",
    "parent_boundary_bypass_count",
    "post_vv_bypass_count",
    "gt_bypass_count",
    "parent_architect_commanded_count",
    "recursive_depth_limit_exceeded_count",
    "unbounded_child_spawn_count",
    "child_consensus_authority_claimed_count",
    "manifest_mutation_count",
    "transition_matrix_mutation_count",
    "network_used_count",
    "gemini_used_count",
    "connector_side_effect_count",
    "root_final_authority_preserved_count",
)


@dataclass(frozen=True)
class FractalCellInput:
    parent_route_id: str
    root_shaped_task_ref: str
    plan_graph_ref: str
    actor_boundary_report_ref: str | None = None
    drs_candidate_refs: tuple[str, ...] = ()
    avf_advisory_refs: tuple[str, ...] = ()
    time_context_refs: tuple[str, ...] = ()
    permission_scope: str = "local_deterministic_no_action"
    max_cell_depth: int = 1
    current_cell_depth: int = 1
    max_child_cells_per_parent: int = 1
    network_allowed: bool = False
    gemini_allowed: bool = False
    external_action_allowed: bool = False
    child_root_claimed: bool = False
    child_cells_requested: int = 0
    child_consensus_claimed_authority: bool = False
    child_majority_claimed_authority: bool = False
    child_compute_volume_claimed_authority: bool = False


@dataclass(frozen=True)
class FractalCellBoundary:
    boundary_id: str
    cell_id: str
    parent_cell_id: str | None
    parent_route_id: str | None
    boundary_kind: str
    current_cell_depth: int
    max_cell_depth: int
    max_child_cells_per_parent: int
    accepted_actor_transitions: tuple[ActorTransitionCheck, ...] = ()
    blocked_actor_transitions: tuple[ActorTransitionCheck, ...] = ()
    reason_codes: tuple[str, ...] = ()
    accepted: bool = True
    blocked: bool = False
    root_review_required: bool = True
    parent_return_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_id": self.boundary_id,
            "cell_id": self.cell_id,
            "parent_cell_id": self.parent_cell_id,
            "parent_route_id": self.parent_route_id,
            "boundary_kind": self.boundary_kind,
            "current_cell_depth": self.current_cell_depth,
            "max_cell_depth": self.max_cell_depth,
            "max_child_cells_per_parent": self.max_child_cells_per_parent,
            "accepted_actor_transitions": [
                transition.to_dict() for transition in self.accepted_actor_transitions
            ],
            "blocked_actor_transitions": [
                transition.to_dict() for transition in self.blocked_actor_transitions
            ],
            "reason_codes": list(self.reason_codes),
            "accepted": self.accepted,
            "blocked": self.blocked,
            "root_review_required": self.root_review_required,
            "parent_return_required": self.parent_return_required,
        }


@dataclass(frozen=True)
class FractalCellResult:
    cell_id: str
    parent_cell_id: str | None
    child_result_proposal_ref: str | None
    child_validation_report_ref: str | None
    child_gt_advisory_ref: str | None
    trace_refs: tuple[dict[str, Any], ...]
    lineage_refs: tuple[dict[str, Any], ...]
    reason_codes: tuple[str, ...]
    final_output_claimed: bool = False
    action_permission_claimed: bool = False
    root_authority_claimed: bool = False
    child_root_claimed: bool = False
    root_review_required: bool = True
    current_cell_depth: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "parent_cell_id": self.parent_cell_id,
            "child_result_proposal_ref": self.child_result_proposal_ref,
            "child_validation_report_ref": self.child_validation_report_ref,
            "child_gt_advisory_ref": self.child_gt_advisory_ref,
            "trace_refs": list(self.trace_refs),
            "lineage_refs": list(self.lineage_refs),
            "reason_codes": list(self.reason_codes),
            "final_output_claimed": self.final_output_claimed,
            "action_permission_claimed": self.action_permission_claimed,
            "root_authority_claimed": self.root_authority_claimed,
            "child_root_claimed": self.child_root_claimed,
            "root_review_required": self.root_review_required,
            "current_cell_depth": self.current_cell_depth,
        }


@dataclass(frozen=True)
class FractalCellTrace:
    trace_id: str
    parent_route_id: str
    cell_lineage: tuple[str, ...]
    child_actor_transition_refs: tuple[str, ...]
    child_result_refs: tuple[str, ...]
    parent_return_refs: tuple[str, ...]
    recursion_guard_refs: tuple[str, ...]
    blocked_transition_refs: tuple[str, ...]
    root_review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "parent_route_id": self.parent_route_id,
            "cell_lineage": list(self.cell_lineage),
            "child_actor_transition_refs": list(self.child_actor_transition_refs),
            "child_result_refs": list(self.child_result_refs),
            "parent_return_refs": list(self.parent_return_refs),
            "recursion_guard_refs": list(self.recursion_guard_refs),
            "blocked_transition_refs": list(self.blocked_transition_refs),
            "root_review_required": self.root_review_required,
        }


@dataclass(frozen=True)
class FractalCellBoundaryReport:
    report_id: str
    cells_started_count: int
    child_actor_inputs_seen_count: int
    child_actor_outputs_emitted_count: int
    child_result_proposals_count: int
    child_validation_reports_count: int
    child_gt_reports_count: int
    parent_return_reports_count: int
    blocked_transitions: tuple[Any, ...]
    recursion_guard_results: tuple[str, ...]
    root_review_required: bool = True
    final_output_created_count: int = 0
    action_permission_granted_count: int = 0
    root_final_authority_preserved: bool = True
    actor_boundary_report_ref: str | None = None
    actor_boundary_report: ActorBoundaryReport | None = None
    reason_codes: tuple[str, ...] = ()
    counters: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "cells_started_count": self.cells_started_count,
            "child_actor_inputs_seen_count": self.child_actor_inputs_seen_count,
            "child_actor_outputs_emitted_count": self.child_actor_outputs_emitted_count,
            "child_result_proposals_count": self.child_result_proposals_count,
            "child_validation_reports_count": self.child_validation_reports_count,
            "child_gt_reports_count": self.child_gt_reports_count,
            "parent_return_reports_count": self.parent_return_reports_count,
            "blocked_transitions": [_to_dict(item) for item in self.blocked_transitions],
            "recursion_guard_results": list(self.recursion_guard_results),
            "root_review_required": self.root_review_required,
            "final_output_created_count": self.final_output_created_count,
            "action_permission_granted_count": self.action_permission_granted_count,
            "root_final_authority_preserved": self.root_final_authority_preserved,
            "actor_boundary_report_ref": self.actor_boundary_report_ref,
            "actor_boundary_report": (
                self.actor_boundary_report.to_dict()
                if self.actor_boundary_report is not None
                else None
            ),
            "reason_codes": list(self.reason_codes),
            "counters": dict(self.counters),
        }


def _to_dict(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _norm(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _boundary_key(value: str | None) -> str:
    return _norm(value).replace("-", "_").replace("/", "_").replace(" ", "_")


def _role_id(role: Any) -> str:
    return str(getattr(role, "role_id", role))


def _dedupe(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _blocked_boundary(
    *,
    boundary_id: str,
    cell_id: str,
    parent_cell_id: str | None,
    parent_route_id: str | None,
    boundary_kind: str,
    current_cell_depth: int,
    max_cell_depth: int,
    max_child_cells_per_parent: int,
    reason_codes: Iterable[str],
    accepted_actor_transitions: Iterable[ActorTransitionCheck] = (),
    blocked_actor_transitions: Iterable[ActorTransitionCheck] = (),
) -> FractalCellBoundary:
    reasons = _dedupe(reason_codes)
    return FractalCellBoundary(
        boundary_id=boundary_id,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        parent_route_id=parent_route_id,
        boundary_kind=boundary_kind,
        current_cell_depth=current_cell_depth,
        max_cell_depth=max_cell_depth,
        max_child_cells_per_parent=max_child_cells_per_parent,
        accepted_actor_transitions=tuple(accepted_actor_transitions),
        blocked_actor_transitions=tuple(blocked_actor_transitions),
        reason_codes=reasons,
        accepted=not reasons,
        blocked=bool(reasons),
        root_review_required=True,
        parent_return_required=True,
    )


def _permission_claims(scope: str, needles: tuple[str, ...]) -> bool:
    normalized = _boundary_key(scope)
    return any(needle in normalized for needle in needles)


def validate_fractal_cell_input(
    cell_input: FractalCellInput,
    *,
    cell_id: str = "fractal_cell:v0_1",
    parent_cell_id: str | None = None,
) -> FractalCellBoundary:
    reasons: list[str] = []
    if cell_input.child_root_claimed:
        reasons.append("child_root_claim_blocked")
    if cell_input.network_allowed:
        reasons.append("network_forbidden")
    if cell_input.gemini_allowed:
        reasons.append("gemini_forbidden")
    if cell_input.external_action_allowed:
        reasons.append("external_action_forbidden")
    if not cell_input.root_shaped_task_ref:
        reasons.append("root_shaped_task_required")
    if not cell_input.parent_route_id:
        reasons.append("parent_route_required")
    if cell_input.current_cell_depth > cell_input.max_cell_depth:
        reasons.append("recursive_depth_limit_exceeded")
    if cell_input.max_cell_depth <= 0:
        reasons.append("max_cell_depth_invalid")
    if cell_input.max_child_cells_per_parent <= 0:
        reasons.append("max_child_cells_invalid")
    if _permission_claims(
        cell_input.permission_scope,
        ("action_permission", "action_authority", "execute_real_action"),
    ):
        reasons.append("action_permission_scope_blocked")
    if _permission_claims(
        cell_input.permission_scope,
        ("finaloutput", "final_output", "root_final", "final_authority"),
    ):
        reasons.append("final_output_permission_scope_blocked")
    if cell_input.child_cells_requested > cell_input.max_child_cells_per_parent:
        reasons.append("unbounded_child_spawn_blocked")
    if cell_input.child_consensus_claimed_authority:
        reasons.append("child_consensus_authority_blocked")
    if cell_input.child_majority_claimed_authority:
        reasons.append("child_majority_authority_blocked")
    if cell_input.child_compute_volume_claimed_authority:
        reasons.append("child_compute_volume_authority_blocked")

    return _blocked_boundary(
        boundary_id=f"cell_input_boundary:{cell_id}",
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        parent_route_id=cell_input.parent_route_id or None,
        boundary_kind="input_validation",
        current_cell_depth=cell_input.current_cell_depth,
        max_cell_depth=cell_input.max_cell_depth,
        max_child_cells_per_parent=cell_input.max_child_cells_per_parent,
        reason_codes=reasons,
    )


def _clone_transition_with_reasons(
    check: ActorTransitionCheck,
    extra_reasons: Iterable[str],
) -> ActorTransitionCheck:
    reasons = _dedupe((*check.reason_codes, *extra_reasons))
    return ActorTransitionCheck(
        transition_id=check.transition_id,
        from_role=check.from_role,
        source_boundary=check.source_boundary,
        to_role=check.to_role,
        target_boundary=check.target_boundary,
        input_kind=check.input_kind,
        output_kind=check.output_kind,
        accepted=False,
        blocked=True,
        reason_codes=reasons,
        root_boundary_required=check.root_boundary_required,
        post_vv_required=check.post_vv_required,
        gt_required=check.gt_required,
        root_final_authority_preserved=check.root_final_authority_preserved,
    )


def validate_child_actor_transition(
    actor_input: ActorInputEnvelope,
    actor_output: ActorOutputEnvelope,
    *,
    target_boundary: str,
    transition_id: str,
) -> ActorTransitionCheck:
    check = validate_actor_transition(
        actor_input,
        actor_output,
        target_boundary=target_boundary,
        transition_id=transition_id,
    )
    key = _boundary_key(target_boundary)
    role_id = _role_id(actor_input.role)
    extra_blocking: list[str] = []
    if (
        key in FINAL_TARGET_ALIASES
        or "finaloutput" in key
        or "final_output" in key
        or "user_final" in key
    ):
        extra_blocking.append("child_target_boundary_blocked")
    if (
        role_id == "gt_boundary"
        and actor_output.output_kind in {"gt_report", "gt_advisory_selection_report"}
        and key in {"architect", "parent_architect", "parent_architect_command"}
    ):
        extra_blocking.append("child_target_boundary_blocked")
        extra_blocking.append("parent_architect_command_blocked")
    if (
        role_id == "root_return"
        and actor_output.output_kind in {"root_review_required", "root_return_bundle"}
        and key in FINAL_TARGET_ALIASES
    ):
        extra_blocking.append("child_target_boundary_blocked")

    if extra_blocking:
        return _clone_transition_with_reasons(check, extra_blocking)
    return check


def _default_plan_graph(cell_input: FractalCellInput) -> dict[str, Any]:
    plan_id = cell_input.plan_graph_ref or "plan:fractal_cell:v0_1"
    return {
        "plan_id": plan_id,
        "request_id": cell_input.parent_route_id,
        "source_packet_id": cell_input.root_shaped_task_ref,
        "time_assumptions": {
            "as_of": "2026-06-24T00:00:00Z",
            "freshness_required": "normal",
            "assumptions": [
                "child cell receives a Root-shaped task",
                "child cell output returns upward for parent review",
            ],
        },
        "branch_budget": {
            "max_nodes": 4,
            "max_parallelism": 2,
            "max_depth": cell_input.max_cell_depth,
        },
        "nodes": [
            {
                "node_id": "child_node:bounded_resultproposal",
                "vector_id": "fractal_cell_bounded_candidate",
                "task": "bounded_child_resultproposal",
                "task_kind": "bounded_child_resultproposal",
                "executor_id": "child_executor_bounded_v0_1",
                "depends_on": [],
                "expected_output": "result_proposal",
                "atomic": True,
                "payload": {
                    "root_shaped_task_ref": cell_input.root_shaped_task_ref,
                    "parent_route_id": cell_input.parent_route_id,
                    "authority_claimed": False,
                    "action_permission_claimed": False,
                },
            }
        ],
        "edges": [],
        "executor_assignments": [
            {
                "executor_id": "child_executor_bounded_v0_1",
                "node_ids": ["child_node:bounded_resultproposal"],
                "mode": "simulate",
            }
        ],
    }


def _fallback_validate_result_proposals(
    proposals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for proposal in proposals:
        proposal_id = str(proposal.get("proposal_id", "missing_proposal"))
        reports.append(
            {
                "vv_report_id": f"vv:{proposal_id}",
                "proposal_id": proposal_id,
                "status": "needs_revision",
                "decision": "revise",
                "checked_at": utc_now_iso(),
                "scores": {
                    "schema": 0.0,
                    "evidence": 0.0,
                    "policy": 0.0,
                    "time": 0.0,
                    "safety": 0.0,
                    "consistency": 0.0,
                },
                "overall_score": 0.0,
                "violations": [
                    {
                        "violation_id": "post_vv_runtime_unavailable_review_required",
                        "kind": "consistency",
                        "description": (
                            "Real Post V&V runtime was unavailable; child output "
                            "requires real Post V&V or Root review."
                        ),
                    }
                ],
                "normalized_features": {
                    "utility": 0.0,
                    "robustness": 0.0,
                    "compute_cost": 0.0,
                    "violations": 1.0,
                    "transfer": 0.0,
                    "novelty_guard": 0.0,
                },
                "vector_id": proposal.get("vector_id"),
                "execution_status": "post_vv_runtime_unavailable_review_required",
                "notes": [
                    "post_vv_runtime_unavailable_review_required",
                    "post_vv_fallback_not_authority",
                    "child_output_requires_real_post_vv_or_root_review",
                ],
                "trace_refs": proposal.get("trace_refs", []),
            }
        )
    return reports


def _validate_child_result_proposals(
    proposals: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    if _runtime_validate_result_proposals is None:
        return _fallback_validate_result_proposals(proposals), True
    return _runtime_validate_result_proposals(proposals), False


def _canonical_child_actor_chain(
    *,
    cell_input: FractalCellInput,
    child_result_proposal_ref: str,
    child_validation_report_ref: str,
    child_gt_advisory_ref: str,
) -> tuple[
    tuple[ActorInputEnvelope, ...],
    tuple[ActorOutputEnvelope, ...],
    tuple[ActorTransitionCheck, ...],
]:
    inputs = (
        ActorInputEnvelope(
            role="intake",
            input_kind="raw_user_context",
            source_boundary="parent_root_orchestrator",
            payload_ref=f"payload:{cell_input.parent_route_id}:child_intake",
        ),
        ActorInputEnvelope(
            role="orchestrator",
            input_kind="intent_candidate",
            source_boundary="child_intake",
            payload_ref=f"payload:{cell_input.parent_route_id}:child_route",
            route_id=cell_input.parent_route_id,
        ),
        ActorInputEnvelope(
            role="architect",
            input_kind="root_shaped_task",
            source_boundary="root_orchestrator",
            payload_ref=cell_input.root_shaped_task_ref,
            root_shaped_task=True,
        ),
        ActorInputEnvelope(
            role="executor",
            input_kind="bounded_plan_graph",
            source_boundary="child_architect",
            payload_ref=cell_input.plan_graph_ref,
            plan_graph_ref=cell_input.plan_graph_ref,
        ),
        ActorInputEnvelope(
            role="verifier",
            input_kind="resultproposal_like",
            source_boundary="child_executor",
            payload_ref=child_result_proposal_ref,
            result_proposal_ref=child_result_proposal_ref,
        ),
        ActorInputEnvelope(
            role="gt_boundary",
            input_kind="vv_report",
            source_boundary="child_verifier",
            payload_ref=child_validation_report_ref,
        ),
        ActorInputEnvelope(
            role="root_return",
            input_kind="gt_report",
            source_boundary="child_gt_boundary",
            payload_ref=child_gt_advisory_ref,
        ),
    )
    outputs = (
        ActorOutputEnvelope(
            role="intake",
            output_kind="structured_intent_candidate",
            payload_ref=f"payload:{cell_input.parent_route_id}:intent_candidate",
        ),
        ActorOutputEnvelope(
            role="orchestrator",
            output_kind="root_shaped_route_proposal",
            payload_ref=f"payload:{cell_input.parent_route_id}:root_shaped_route",
        ),
        ActorOutputEnvelope(
            role="architect",
            output_kind="plangraph_proposal",
            payload_ref=cell_input.plan_graph_ref,
        ),
        ActorOutputEnvelope(
            role="executor",
            output_kind="resultproposal_like",
            payload_ref=child_result_proposal_ref,
        ),
        ActorOutputEnvelope(
            role="verifier",
            output_kind="vv_report",
            payload_ref=child_validation_report_ref,
        ),
        ActorOutputEnvelope(
            role="gt_boundary",
            output_kind="gt_report",
            payload_ref=child_gt_advisory_ref,
        ),
        ActorOutputEnvelope(
            role="root_return",
            output_kind="root_return_bundle",
            payload_ref=f"parent_return:{cell_input.parent_route_id}",
        ),
    )
    targets = (
        "root_orchestrator",
        "root_orchestrator",
        "executor",
        "post_vv",
        "gt_boundary",
        "root_return",
        "root_orchestrator",
    )
    transitions = tuple(
        validate_child_actor_transition(
            actor_input,
            actor_output,
            target_boundary=target,
            transition_id=f"child_chain:{cell_input.parent_route_id}:{index}",
        )
        for index, (actor_input, actor_output, target) in enumerate(
            zip(inputs, outputs, targets, strict=True),
            start=1,
        )
    )
    return inputs, outputs, transitions


def validate_fractal_cell_output(
    result: FractalCellResult,
) -> FractalCellBoundary:
    reasons: list[str] = []
    if result.final_output_claimed:
        reasons.append("child_finaloutput_claim_blocked")
    if result.action_permission_claimed:
        reasons.append("child_action_permission_claim_blocked")
    if result.root_authority_claimed:
        reasons.append("child_root_authority_claim_blocked")
    if result.child_root_claimed:
        reasons.append("child_root_claim_blocked")
    if not result.child_result_proposal_ref:
        reasons.append("child_resultproposal_required")
    if result.current_cell_depth > 1 and not result.parent_cell_id:
        reasons.append("parent_cell_required_for_child")
    if not result.trace_refs:
        reasons.append("trace_refs_required")
    if not result.root_review_required:
        reasons.append("root_review_required")

    return _blocked_boundary(
        boundary_id=f"cell_output_boundary:{result.cell_id}",
        cell_id=result.cell_id,
        parent_cell_id=result.parent_cell_id,
        parent_route_id=None,
        boundary_kind="output_validation",
        current_cell_depth=result.current_cell_depth,
        max_cell_depth=max(result.current_cell_depth, 1),
        max_child_cells_per_parent=1,
        reason_codes=reasons,
    )


def _zero_counters() -> dict[str, int]:
    return {key: 0 for key in COUNTER_KEYS}


def build_fractal_cell_boundary_report(
    *,
    report_id: str = "fractal_cell_boundary_report:v0_1",
    cell_input: FractalCellInput | None = None,
    result: FractalCellResult | None = None,
    input_boundary: FractalCellBoundary | None = None,
    output_boundary: FractalCellBoundary | None = None,
    actor_boundary_report: ActorBoundaryReport | None = None,
    dag_runner_report: dict[str, Any] | None = None,
    vv_reports: Iterable[dict[str, Any]] = (),
    gt_report: dict[str, Any] | None = None,
    post_vv_fallback_used: bool = False,
    extra_blocked_transitions: Iterable[Any] = (),
    recursion_guard_results: Iterable[str] = (),
) -> FractalCellBoundaryReport:
    vv_report_list = tuple(vv_reports)
    blocked: list[Any] = list(extra_blocked_transitions)
    if actor_boundary_report is not None:
        blocked.extend(actor_boundary_report.blocked_transitions)
    if input_boundary is not None and input_boundary.blocked:
        blocked.append(input_boundary)
    if output_boundary is not None and output_boundary.blocked:
        blocked.append(output_boundary)

    result_output_blocked = output_boundary.blocked if output_boundary else False
    unsafe_result_accepted = bool(
        result is not None
        and not result_output_blocked
        and (
            result.final_output_claimed
            or result.action_permission_claimed
            or result.root_authority_claimed
            or result.child_root_claimed
        )
    )
    input_blocked = input_boundary.blocked if input_boundary else False
    cells_started_count = 1 if result is not None and not input_blocked else 0
    child_result_proposals_count = 0
    if dag_runner_report is not None:
        child_result_proposals_count = len(dag_runner_report.get("result_proposals") or [])
    elif result is not None and result.child_result_proposal_ref:
        child_result_proposals_count = 1

    counters = _zero_counters()
    counters["cells_started_count"] = cells_started_count
    counters["child_actor_inputs_seen_count"] = (
        actor_boundary_report.actor_inputs_seen_count
        if actor_boundary_report is not None
        else 0
    )
    counters["child_actor_outputs_emitted_count"] = (
        actor_boundary_report.actor_outputs_emitted_count
        if actor_boundary_report is not None
        else 0
    )
    counters["child_result_proposals_count"] = child_result_proposals_count
    counters["child_validation_reports_count"] = len(vv_report_list)
    counters["child_gt_reports_count"] = 1 if gt_report is not None else 0
    counters["parent_return_reports_count"] = (
        1 if result is not None and result.root_review_required and not result_output_blocked else 0
    )
    counters["post_vv_fallback_used_count"] = 1 if post_vv_fallback_used else 0
    counters["root_review_required_count"] = (
        1
        if (
            (result is not None and result.root_review_required)
            or (input_boundary is not None and input_boundary.root_review_required)
        )
        else 0
    )
    counters["final_output_created_count"] = 1 if unsafe_result_accepted and result.final_output_claimed else 0
    counters["action_permission_granted_count"] = (
        1 if unsafe_result_accepted and result.action_permission_claimed else 0
    )
    counters["child_root_claimed_count"] = (
        1 if unsafe_result_accepted and result.child_root_claimed else 0
    )
    counters["child_authority_claimed_count"] = (
        1 if unsafe_result_accepted and result.root_authority_claimed else 0
    )
    counters["child_finaloutput_claimed_count"] = counters["final_output_created_count"]
    counters["child_action_permission_claimed_count"] = counters[
        "action_permission_granted_count"
    ]
    counters["root_final_authority_preserved_count"] = 1 if not unsafe_result_accepted else 0

    reason_codes = _dedupe(
        (
            *(input_boundary.reason_codes if input_boundary is not None else ()),
            *(output_boundary.reason_codes if output_boundary is not None else ()),
            *(actor_boundary_report.reason_codes if actor_boundary_report is not None else ()),
            *(result.reason_codes if result is not None else ()),
            *(
                (
                    "post_vv_fallback_used_review_required",
                    "post_vv_runtime_unavailable_review_required",
                    "post_vv_fallback_not_authority",
                    "child_output_requires_real_post_vv_or_root_review",
                )
                if post_vv_fallback_used
                else ()
            ),
            *tuple(recursion_guard_results),
            *(
                reason
                for item in blocked
                for reason in getattr(item, "reason_codes", ())
            ),
        )
    )
    root_final_authority_preserved = all(
        counters[key] == 0
        for key in (
            "final_output_created_count",
            "action_permission_granted_count",
            "child_root_claimed_count",
            "child_authority_claimed_count",
            "child_finaloutput_claimed_count",
            "child_action_permission_claimed_count",
            "parent_boundary_bypass_count",
            "post_vv_bypass_count",
            "gt_bypass_count",
            "parent_architect_commanded_count",
            "recursive_depth_limit_exceeded_count",
            "unbounded_child_spawn_count",
            "child_consensus_authority_claimed_count",
            "manifest_mutation_count",
            "transition_matrix_mutation_count",
            "network_used_count",
            "gemini_used_count",
            "connector_side_effect_count",
        )
    )
    counters["root_final_authority_preserved_count"] = (
        1 if root_final_authority_preserved else 0
    )
    return FractalCellBoundaryReport(
        report_id=report_id,
        cells_started_count=counters["cells_started_count"],
        child_actor_inputs_seen_count=counters["child_actor_inputs_seen_count"],
        child_actor_outputs_emitted_count=counters["child_actor_outputs_emitted_count"],
        child_result_proposals_count=counters["child_result_proposals_count"],
        child_validation_reports_count=counters["child_validation_reports_count"],
        child_gt_reports_count=counters["child_gt_reports_count"],
        parent_return_reports_count=counters["parent_return_reports_count"],
        blocked_transitions=tuple(blocked),
        recursion_guard_results=tuple(recursion_guard_results),
        root_review_required=True,
        final_output_created_count=counters["final_output_created_count"],
        action_permission_granted_count=counters["action_permission_granted_count"],
        root_final_authority_preserved=root_final_authority_preserved,
        actor_boundary_report_ref=(
            actor_boundary_report.report_id if actor_boundary_report is not None else None
        ),
        actor_boundary_report=actor_boundary_report,
        reason_codes=reason_codes,
        counters=counters,
    )


def run_bounded_fractal_cell(
    cell_input: FractalCellInput,
    *,
    plan_graph: dict[str, Any] | None = None,
    cell_id: str = "fractal_cell:v0_1",
    parent_cell_id: str | None = "parent_cell:root_boundary",
) -> dict[str, Any]:
    input_boundary = validate_fractal_cell_input(
        cell_input,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
    )
    if input_boundary.blocked:
        report = build_fractal_cell_boundary_report(
            report_id=f"fractal_cell_boundary_report:{cell_id}",
            cell_input=cell_input,
            input_boundary=input_boundary,
            recursion_guard_results=input_boundary.reason_codes,
        )
        return {
            "status": "blocked",
            "input_boundary": input_boundary,
            "output_boundary": None,
            "result": None,
            "trace": None,
            "boundary_report": report,
            "actor_boundary_report": None,
            "dag_runner_report": None,
            "vv_reports": [],
            "gt_report": None,
        }

    active_plan_graph = plan_graph or _default_plan_graph(cell_input)
    dag_runner_report = run_fractal_dag_executor(
        active_plan_graph,
        runner_id=f"runner:{cell_id}:fractal_dag",
        session_anchor=f"session:{cell_id}",
    )
    result_proposals = list(dag_runner_report.get("result_proposals") or [])
    vv_reports, post_vv_fallback_used = _validate_child_result_proposals(
        result_proposals
    )
    gt_report = validate_gt(vv_reports, game_mode="fractal_cell_child_selection")
    child_result_proposal_ref = (
        result_proposals[0]["proposal_id"] if result_proposals else None
    )
    child_validation_report_ref = (
        vv_reports[0]["vv_report_id"] if vv_reports else None
    )
    child_gt_advisory_ref = gt_report.get("gt_report_id")

    actor_inputs, actor_outputs, actor_transitions = _canonical_child_actor_chain(
        cell_input=cell_input,
        child_result_proposal_ref=child_result_proposal_ref or "missing_child_result",
        child_validation_report_ref=child_validation_report_ref or "missing_child_vv",
        child_gt_advisory_ref=child_gt_advisory_ref or "missing_child_gt",
    )
    actor_boundary_report = build_actor_boundary_report(
        report_id=f"actor_boundary_report:{cell_id}",
        inputs=actor_inputs,
        outputs=actor_outputs,
        transitions=actor_transitions,
    )
    trace_refs = (
        {
            "trace_id": f"trace:{cell_id}",
            "span_id": "child_cell_result",
            "kind": "fractal_cell_integration",
        },
    )
    result_reason_codes = [
        "child_resultproposal_only",
        "child_output_returns_to_parent_root_boundary",
        "root_review_required",
    ]
    if post_vv_fallback_used:
        result_reason_codes.extend(
            [
                "post_vv_fallback_used_review_required",
                "post_vv_runtime_unavailable_review_required",
                "post_vv_fallback_not_authority",
                "child_output_requires_real_post_vv_or_root_review",
            ]
        )

    result = FractalCellResult(
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        child_result_proposal_ref=child_result_proposal_ref,
        child_validation_report_ref=child_validation_report_ref,
        child_gt_advisory_ref=child_gt_advisory_ref,
        trace_refs=trace_refs,
        lineage_refs=(
            {
                "parent_route_id": cell_input.parent_route_id,
                "root_shaped_task_ref": cell_input.root_shaped_task_ref,
                "current_cell_depth": cell_input.current_cell_depth,
                "max_cell_depth": cell_input.max_cell_depth,
            },
        ),
        reason_codes=tuple(result_reason_codes),
        final_output_claimed=False,
        action_permission_claimed=False,
        root_authority_claimed=False,
        child_root_claimed=False,
        root_review_required=True,
        current_cell_depth=cell_input.current_cell_depth,
    )
    output_boundary = validate_fractal_cell_output(result)
    trace = FractalCellTrace(
        trace_id=f"fractal_cell_trace:{cell_id}",
        parent_route_id=cell_input.parent_route_id,
        cell_lineage=(parent_cell_id or "root_boundary", cell_id),
        child_actor_transition_refs=tuple(
            transition.transition_id for transition in actor_transitions
        ),
        child_result_refs=tuple(
            ref
            for ref in (
                child_result_proposal_ref,
                child_validation_report_ref,
                child_gt_advisory_ref,
            )
            if ref
        ),
        parent_return_refs=(f"parent_return:{cell_input.parent_route_id}",),
        recursion_guard_refs=(
            f"max_cell_depth:{cell_input.max_cell_depth}",
            f"current_cell_depth:{cell_input.current_cell_depth}",
            f"max_child_cells_per_parent:{cell_input.max_child_cells_per_parent}",
        ),
        blocked_transition_refs=tuple(
            transition.transition_id
            for transition in actor_boundary_report.blocked_transitions
        ),
        root_review_required=True,
    )
    boundary_report = build_fractal_cell_boundary_report(
        report_id=f"fractal_cell_boundary_report:{cell_id}",
        cell_input=cell_input,
        result=result,
        input_boundary=input_boundary,
        output_boundary=output_boundary,
        actor_boundary_report=actor_boundary_report,
        dag_runner_report=dag_runner_report,
        vv_reports=vv_reports,
        gt_report=gt_report,
        post_vv_fallback_used=post_vv_fallback_used,
        recursion_guard_results=trace.recursion_guard_refs,
    )
    return {
        "status": "completed" if output_boundary.accepted else "blocked",
        "input_boundary": input_boundary,
        "output_boundary": output_boundary,
        "result": result,
        "trace": trace,
        "boundary_report": boundary_report,
        "actor_boundary_report": actor_boundary_report,
        "dag_runner_report": dag_runner_report,
        "vv_reports": vv_reports,
        "gt_report": gt_report,
    }


def make_default_fractal_cell_input(
    *,
    parent_route_id: str = "route:fractal_cell:v0_1",
    root_shaped_task_ref: str = "root_task:fractal_cell:v0_1",
    plan_graph_ref: str = "plan:fractal_cell:v0_1",
    current_cell_depth: int = 1,
    max_cell_depth: int = 2,
    max_child_cells_per_parent: int = 2,
) -> FractalCellInput:
    return FractalCellInput(
        parent_route_id=parent_route_id,
        root_shaped_task_ref=root_shaped_task_ref,
        plan_graph_ref=plan_graph_ref,
        actor_boundary_report_ref="actor_boundary_report:bounded_llm_slm:v0_1",
        drs_candidate_refs=("drs_candidate:signal_only",),
        avf_advisory_refs=("avf_advisory:signal_only",),
        time_context_refs=("time_context:deterministic_v0_1",),
        permission_scope="local_deterministic_no_action",
        max_cell_depth=max_cell_depth,
        current_cell_depth=current_cell_depth,
        max_child_cells_per_parent=max_child_cells_per_parent,
    )
