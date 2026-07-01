from __future__ import annotations

from typing import Any, Iterable, Mapping


"""
Rich Context / Bounded Context Packets core contracts.

These are bounded context packets, not raw dumps.
Context packet is not truth.
Context packet is not authority.
Context packet is not action permission.
Context packet is not FinalOutput.
Gemini proposes, Root disposes.
Root remains final authority.
Child branch is not Root.
Mock receipt is not real payment.
ExecutionEvidence is not FinalOutput.
"""


BUSINESS_REQUEST_CONTEXT_PACKET = "BusinessRequestContextPacket"
EVIDENCE_CONTEXT_PACKET = "EvidenceContextPacket"
DRS_CANDIDATE_CONTEXT_PACKET = "DRSCandidateContextPacket"
CANDIDATE_VECTOR_CONTEXT_PACKET = "CandidateVectorContextPacket"
AVF_ATTRACTOR_CONTEXT_PACKET = "AVFAttractorContextPacket"
ORCHESTRATOR_ROUTE_CONTEXT_PACKET = "OrchestratorRouteContextPacket"
ARCHITECT_PLAN_CONTEXT_PACKET = "ArchitectPlanContextPacket"
FRACTAL_BRANCH_TASK_CONTEXT_PACKET = "FractalBranchTaskContextPacket"
SANDBOX_RECEIPT_CONTEXT_PACKET = "SandboxReceiptContextPacket"
ROOT_REVIEW_CONTEXT_PACKET = "RootReviewContextPacket"


CONTEXT_PACKET_COMMON_REQUIRED_FIELDS = (
    "packet_type",
    "packet_id",
    "created_by",
    "source_refs",
    "domain",
    "root_final_authority_preserved",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "real_world_effects_allowed",
    "Root remains final authority",
)

CONTEXT_PACKET_FORBIDDEN_CLAIM_KEYS = {
    "truth_claimed": "truth_claimed_forbidden",
    "authority_claimed": "authority_claimed_forbidden",
    "action_permission_claimed": "action_permission_claimed_forbidden",
    "final_output_claimed": "final_output_claimed_forbidden",
    "connector_command_claimed": "connector_command_claimed_forbidden",
    "drs_write_claimed": "drs_write_claimed_forbidden",
    "root_bypass_claimed": "root_bypass_claimed_forbidden",
    "direct_adapter_bypass_attempted": "direct_adapter_bypass_attempted_forbidden",
}

CONTEXT_PACKET_FORBIDDEN_READINESS_CLAIM_KEYS = {
    "production_ready": "production_readiness_claim_forbidden",
    "production_ready_claimed": "production_readiness_claim_forbidden",
    "production_readiness_claimed": "production_readiness_claim_forbidden",
    "public_wow_ready": "public_wow_readiness_claim_forbidden",
    "public_wow_ready_claimed": "public_wow_readiness_claim_forbidden",
    "public_wow_readiness_claimed": "public_wow_readiness_claim_forbidden",
}

CONTEXT_PACKET_SECRET_MARKERS = (
    "api_key",
    "secret",
    "token",
    "password",
    ".tmp",
)

CONTEXT_PACKET_RAW_DUMP_MARKERS = {
    "raw_user_text": "raw_user_text_dump_forbidden",
    "raw_gemini_text": "raw_gemini_cross_role_text_forbidden",
    "raw_cross_role_text": "raw_gemini_cross_role_text_forbidden",
    "full_runner_state_dump": "unbounded_context_dump_forbidden",
    "unbounded_context_dump": "unbounded_context_dump_forbidden",
    "raw_plan_graph_context": "unbounded_plangraph_context_dump_forbidden",
    "raw_plangraph_context": "unbounded_plangraph_context_dump_forbidden",
}


def _as_tuple(value: Iterable[Any] | None) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def context_packet_default_claims() -> dict[str, Any]:
    return {
        "root_final_authority_preserved": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "root_bypass_claimed": False,
        "real_world_effects_allowed": False,
        "Root remains final authority": True,
    }


def _context_packet_base(
    *,
    packet_type: str,
    packet_id: str,
    created_by: str,
    source_refs: Iterable[Mapping[str, Any]] | None,
    domain: str,
) -> dict[str, Any]:
    return {
        "packet_type": packet_type,
        "packet_id": packet_id,
        "created_by": created_by,
        "source_refs": _as_tuple(source_refs),
        "domain": domain,
        **context_packet_default_claims(),
    }


def context_packet_validation_result(
    reasons: Iterable[str],
    packet_type: str | None,
) -> dict[str, Any]:
    reason_tuple = tuple(reasons)
    return {
        "accepted": not reason_tuple,
        "reasons": reason_tuple,
        "packet_type": packet_type,
    }


def _walk_key_values(value: Any) -> Iterable[tuple[str | None, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item
            yield from _walk_key_values(item)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield from _walk_key_values(item)


def context_packet_forbidden_claim_reasons(packet: Mapping[str, Any]) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, reason in CONTEXT_PACKET_FORBIDDEN_CLAIM_KEYS.items():
        if bool(packet.get(key)):
            _append_reason(reasons, reason)
    for key, reason in CONTEXT_PACKET_FORBIDDEN_READINESS_CLAIM_KEYS.items():
        if bool(packet.get(key)):
            _append_reason(reasons, reason)
    if packet.get("real_world_effects_allowed") is not False:
        _append_reason(reasons, "real_world_effects_allowed_forbidden")
    if packet.get("root_final_authority_preserved") is not True:
        _append_reason(reasons, "root_final_authority_not_preserved")
    if packet.get("Root remains final authority") is not True:
        _append_reason(reasons, "root_final_authority_not_preserved")
    return tuple(reasons)


def context_packet_secret_marker_reasons(
    packet: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, value in _walk_key_values(packet):
        key_text = key or ""
        value_text = value if isinstance(value, str) else ""
        for marker in CONTEXT_PACKET_SECRET_MARKERS:
            if marker in key_text or marker in value_text:
                _append_reason(reasons, f"raw_secret_marker_forbidden:{marker}")
    return tuple(reasons)


def context_packet_raw_dump_reasons(packet: Mapping[str, Any]) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, _value in _walk_key_values(packet):
        key_text = key or ""
        for marker, reason in CONTEXT_PACKET_RAW_DUMP_MARKERS.items():
            if marker in key_text:
                _append_reason(reasons, reason)
    return tuple(reasons)


def validate_context_packet_common(
    packet: Mapping[str, Any],
    *,
    expected_packet_type: str,
    required_fields: Iterable[str] = (),
) -> dict[str, Any]:
    reasons: list[str] = []
    packet_type = packet.get("packet_type")
    required = (
        *CONTEXT_PACKET_COMMON_REQUIRED_FIELDS,
        *tuple(required_fields),
    )
    for field in required:
        if field not in packet:
            _append_reason(reasons, f"missing_required_context_packet_field:{field}")

    if packet_type != expected_packet_type:
        _append_reason(reasons, f"unexpected_packet_type:{packet_type}")
    if packet_type == "mock_action_commit_packet":
        _append_reason(reasons, "context_packet_is_not_action_commit_packet")
    if packet_type == "FinalOutput":
        _append_reason(reasons, "context_packet_is_not_final_output")

    reasons.extend(context_packet_forbidden_claim_reasons(packet))
    reasons.extend(context_packet_secret_marker_reasons(packet))
    reasons.extend(context_packet_raw_dump_reasons(packet))

    return context_packet_validation_result(reasons, packet_type)


def build_business_request_context_packet(
    *,
    packet_id: str = "context_packet:business_request:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    request_id: str = "request:generic",
    business_subject: str = "generic_subject",
    requested_action: str = "review",
    explicit_blockers: Iterable[str] | None = None,
    user_visible_summary: str = "Bounded business request summary",
    forbidden_authority_fields: Iterable[str] | None = None,
    forbidden_action_fields: Iterable[str] | None = None,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=BUSINESS_REQUEST_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "request_id": request_id,
            "business_subject": business_subject,
            "requested_action": requested_action,
            "explicit_blockers": _as_tuple(explicit_blockers),
            "user_visible_summary": user_visible_summary,
            "forbidden_authority_fields": _as_tuple(forbidden_authority_fields),
            "forbidden_action_fields": _as_tuple(forbidden_action_fields),
        }
    )
    return packet


def validate_business_request_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    return validate_context_packet_common(
        packet,
        expected_packet_type=BUSINESS_REQUEST_CONTEXT_PACKET,
        required_fields=(
            "request_id",
            "business_subject",
            "requested_action",
            "explicit_blockers",
            "user_visible_summary",
            "forbidden_authority_fields",
            "forbidden_action_fields",
        ),
    )


def build_evidence_context_packet(
    *,
    packet_id: str = "context_packet:evidence:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    evidence_refs: Iterable[Mapping[str, Any]] | None = None,
    semantic_evidence_claim_refs: Iterable[str] | None = None,
    candidate_only: bool = True,
    provenance_summary: str = "Bounded evidence provenance summary",
    contradiction_flags: Iterable[str] | None = None,
    unsafe_instruction_flags: Iterable[str] | None = None,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=EVIDENCE_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "evidence_refs": _as_tuple(evidence_refs),
            "semantic_evidence_claim_refs": _as_tuple(semantic_evidence_claim_refs),
            "candidate_only": candidate_only,
            "provenance_summary": provenance_summary,
            "contradiction_flags": _as_tuple(contradiction_flags),
            "unsafe_instruction_flags": _as_tuple(unsafe_instruction_flags),
        }
    )
    return packet


def validate_evidence_context_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=EVIDENCE_CONTEXT_PACKET,
        required_fields=(
            "evidence_refs",
            "semantic_evidence_claim_refs",
            "candidate_only",
            "provenance_summary",
            "contradiction_flags",
            "unsafe_instruction_flags",
        ),
    )
    reasons = list(validation["reasons"])
    if packet.get("candidate_only") is not True:
        _append_reason(reasons, "evidence_context_must_be_candidate_only")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_drs_candidate_context_packet(
    *,
    packet_id: str = "context_packet:drs_candidate:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    candidate_ids: Iterable[str] | None = None,
    stale_flags: Mapping[str, bool] | None = None,
    conflict_flags: Mapping[str, bool] | None = None,
    reuse_eligibility_flags: Mapping[str, bool] | None = None,
    direct_reuse_allowed: bool = False,
    drs_write_permission_claimed: bool = False,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=DRS_CANDIDATE_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "candidate_ids": _as_tuple(candidate_ids),
            "stale_flags": dict(stale_flags or {}),
            "conflict_flags": dict(conflict_flags or {}),
            "reuse_eligibility_flags": dict(reuse_eligibility_flags or {}),
            "direct_reuse_allowed": direct_reuse_allowed,
            "drs_write_permission_claimed": drs_write_permission_claimed,
        }
    )
    return packet


def validate_drs_candidate_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=DRS_CANDIDATE_CONTEXT_PACKET,
        required_fields=(
            "candidate_ids",
            "stale_flags",
            "conflict_flags",
            "reuse_eligibility_flags",
            "direct_reuse_allowed",
            "drs_write_permission_claimed",
        ),
    )
    reasons = list(validation["reasons"])
    if bool(packet.get("drs_write_permission_claimed")):
        _append_reason(reasons, "drs_write_claimed_forbidden")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_candidate_vector_context_packet(
    *,
    packet_id: str = "context_packet:candidate_vector:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    vector_ids: Iterable[str] | None = None,
    selected_vector_ids: Iterable[str] | None = None,
    allowed_vector_ids: Iterable[str] | None = None,
    ranking_summary: Mapping[str, Any] | None = None,
    blocked_candidates: Iterable[str] | None = None,
    masked_candidates: Iterable[str] | None = None,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=CANDIDATE_VECTOR_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    vector_id_tuple = _as_tuple(vector_ids)
    allowed_tuple = _as_tuple(allowed_vector_ids) or vector_id_tuple
    packet.update(
        {
            "vector_ids": vector_id_tuple,
            "selected_vector_ids": _as_tuple(selected_vector_ids),
            "allowed_vector_ids": allowed_tuple,
            "ranking_summary": dict(ranking_summary or {}),
            "blocked_candidates": _as_tuple(blocked_candidates),
            "masked_candidates": _as_tuple(masked_candidates),
        }
    )
    return packet


def validate_candidate_vector_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=CANDIDATE_VECTOR_CONTEXT_PACKET,
        required_fields=(
            "vector_ids",
            "selected_vector_ids",
            "allowed_vector_ids",
            "ranking_summary",
            "blocked_candidates",
            "masked_candidates",
        ),
    )
    reasons = list(validation["reasons"])
    selected = set(packet.get("selected_vector_ids", ()))
    allowed = set(packet.get("allowed_vector_ids", ()))
    if not selected.issubset(allowed):
        _append_reason(reasons, "candidate_vector_selected_ids_not_allowed")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_avf_attractor_context_packet(
    *,
    packet_id: str = "context_packet:avf_attractor:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    hard_masks: Iterable[str] | None = None,
    soft_pressures_planned: Iterable[str] | None = None,
    risk_pressure: Mapping[str, Any] | None = None,
    conflict_pressure: Mapping[str, Any] | None = None,
    freshness_pressure: Mapping[str, Any] | None = None,
    reuse_pressure: Mapping[str, Any] | None = None,
    advisory_only: bool = True,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=AVF_ATTRACTOR_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "hard_masks": _as_tuple(hard_masks),
            "soft_pressures_planned": _as_tuple(soft_pressures_planned),
            "risk_pressure": dict(risk_pressure or {}),
            "conflict_pressure": dict(conflict_pressure or {}),
            "freshness_pressure": dict(freshness_pressure or {}),
            "reuse_pressure": dict(reuse_pressure or {}),
            "advisory_only": advisory_only,
        }
    )
    return packet


def validate_avf_attractor_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=AVF_ATTRACTOR_CONTEXT_PACKET,
        required_fields=(
            "hard_masks",
            "soft_pressures_planned",
            "risk_pressure",
            "conflict_pressure",
            "freshness_pressure",
            "reuse_pressure",
            "advisory_only",
        ),
    )
    reasons = list(validation["reasons"])
    if packet.get("advisory_only") is not True:
        _append_reason(reasons, "avf_context_must_be_advisory_only")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_orchestrator_route_context_packet(
    *,
    packet_id: str = "context_packet:orchestrator_route:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    allowed_routes: Iterable[str] | None = None,
    required_guards: Iterable[str] | None = None,
    selected_vector_ids: Iterable[str] | None = None,
    route_validation_expectations: Mapping[str, Any] | None = None,
    orchestrator_is_root: bool = False,
    creates_action_commit_packet: bool = False,
    calls_connectors: bool = False,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=ORCHESTRATOR_ROUTE_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "allowed_routes": _as_tuple(allowed_routes) or ("bounded_route",),
            "required_guards": _as_tuple(required_guards),
            "selected_vector_ids": _as_tuple(selected_vector_ids),
            "route_validation_expectations": dict(route_validation_expectations or {}),
            "orchestrator_is_root": orchestrator_is_root,
            "creates_action_commit_packet": creates_action_commit_packet,
            "calls_connectors": calls_connectors,
        }
    )
    return packet


def validate_orchestrator_route_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=ORCHESTRATOR_ROUTE_CONTEXT_PACKET,
        required_fields=(
            "allowed_routes",
            "required_guards",
            "selected_vector_ids",
            "route_validation_expectations",
            "orchestrator_is_root",
        ),
    )
    reasons = list(validation["reasons"])
    if not packet.get("allowed_routes"):
        _append_reason(reasons, "orchestrator_allowed_routes_required")
    if packet.get("orchestrator_is_root") is not False:
        _append_reason(reasons, "orchestrator_is_not_root")
    if bool(packet.get("creates_action_commit_packet")):
        _append_reason(reasons, "context_packet_is_not_action_commit_packet")
    if bool(packet.get("calls_connectors")):
        _append_reason(reasons, "connector_command_claimed_forbidden")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_architect_plan_context_packet(
    *,
    packet_id: str = "context_packet:architect_plan:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    source_route_id: str = "route:bounded",
    allowed_executor_ids: Iterable[str] | None = None,
    allowed_node_kinds: Iterable[str] | None = None,
    required_validators: Iterable[str] | None = None,
    forbidden_connector_claims: Iterable[str] | None = None,
    forbidden_action_claims: Iterable[str] | None = None,
    forbidden_final_output_claims: Iterable[str] | None = None,
    architect_is_root: bool = False,
    creates_action_commit_packet: bool = False,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=ARCHITECT_PLAN_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "source_route_id": source_route_id,
            "allowed_executor_ids": _as_tuple(allowed_executor_ids),
            "allowed_node_kinds": _as_tuple(allowed_node_kinds),
            "required_validators": _as_tuple(required_validators),
            "forbidden_connector_claims": _as_tuple(forbidden_connector_claims),
            "forbidden_action_claims": _as_tuple(forbidden_action_claims),
            "forbidden_final_output_claims": _as_tuple(forbidden_final_output_claims),
            "architect_is_root": architect_is_root,
            "creates_action_commit_packet": creates_action_commit_packet,
        }
    )
    return packet


def validate_architect_plan_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=ARCHITECT_PLAN_CONTEXT_PACKET,
        required_fields=(
            "source_route_id",
            "allowed_executor_ids",
            "allowed_node_kinds",
            "required_validators",
            "forbidden_connector_claims",
            "forbidden_action_claims",
            "forbidden_final_output_claims",
            "architect_is_root",
            "creates_action_commit_packet",
        ),
    )
    reasons = list(validation["reasons"])
    if packet.get("architect_is_root") is not False:
        _append_reason(reasons, "architect_is_not_root")
    if packet.get("creates_action_commit_packet") is not False:
        _append_reason(reasons, "architect_cannot_create_action_commit_packet")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_fractal_branch_task_context_packet(
    *,
    packet_id: str = "context_packet:fractal_branch_task:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    parent_fractal_id: str = "fractal:parent",
    branch_id: str = "branch:bounded",
    child_oai_topology: Mapping[str, str] | None = None,
    child_orchestrator: str = "bounded_branch_router",
    child_architect: str = "bounded_branch_plan",
    child_executor: str = "mock_sandbox_task_executor",
    allowed_adapter_name: str = "adapter_metadata_only",
    adapter_metadata_only: bool = True,
    expected_receipt_type: str = "mock_receipt",
    returns_to_parent: bool = True,
    child_root_created: bool = False,
    child_final_output_created: bool = False,
    child_action_commit_packet_created: bool = False,
    direct_adapter_bypass_attempted: bool = False,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=FRACTAL_BRANCH_TASK_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    topology = dict(
        child_oai_topology
        or {
            "child_orchestrator": child_orchestrator,
            "child_architect": child_architect,
            "child_executor": child_executor,
        }
    )
    packet.update(
        {
            "parent_fractal_id": parent_fractal_id,
            "branch_id": branch_id,
            "child_oai_topology": topology,
            "child_orchestrator": child_orchestrator,
            "child_architect": child_architect,
            "child_executor": child_executor,
            "allowed_adapter_name": allowed_adapter_name,
            "adapter_metadata_only": adapter_metadata_only,
            "expected_receipt_type": expected_receipt_type,
            "returns_to_parent": returns_to_parent,
            "child_root_created": child_root_created,
            "child_final_output_created": child_final_output_created,
            "child_action_commit_packet_created": child_action_commit_packet_created,
            "direct_adapter_bypass_attempted": direct_adapter_bypass_attempted,
        }
    )
    return packet


def validate_fractal_branch_task_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=FRACTAL_BRANCH_TASK_CONTEXT_PACKET,
        required_fields=(
            "parent_fractal_id",
            "branch_id",
            "child_oai_topology",
            "child_orchestrator",
            "child_architect",
            "child_executor",
            "allowed_adapter_name",
            "adapter_metadata_only",
            "expected_receipt_type",
            "returns_to_parent",
            "child_root_created",
            "child_final_output_created",
            "child_action_commit_packet_created",
            "direct_adapter_bypass_attempted",
        ),
    )
    reasons = list(validation["reasons"])
    if packet.get("returns_to_parent") is not True:
        _append_reason(reasons, "fractal_branch_must_return_to_parent")
    if packet.get("child_root_created") is not False:
        _append_reason(reasons, "fractal_branch_cannot_create_root")
    if packet.get("child_final_output_created") is not False:
        _append_reason(reasons, "fractal_branch_cannot_create_final_output")
    if packet.get("child_action_commit_packet_created") is not False:
        _append_reason(reasons, "fractal_branch_cannot_create_action_commit_packet")
    if packet.get("adapter_metadata_only") is not True:
        _append_reason(reasons, "fractal_branch_adapter_must_be_metadata_only")
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_sandbox_receipt_context_packet(
    *,
    packet_id: str = "context_packet:sandbox_receipt:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    mock_receipt_refs: Iterable[Mapping[str, Any]] | None = None,
    adapter_names: Iterable[str] | None = None,
    mock_only: bool = True,
    real_world_effects_allowed: bool = False,
    fake_connector_counter_notes: str = "fake_*_connector_called_count may rise",
    real_external_counter_expectations: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=SANDBOX_RECEIPT_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "mock_receipt_refs": _as_tuple(mock_receipt_refs),
            "adapter_names": _as_tuple(adapter_names),
            "mock_only": mock_only,
            "real_world_effects_allowed": real_world_effects_allowed,
            "fake_connector_counter_notes": fake_connector_counter_notes,
            "real_external_counter_expectations": dict(
                real_external_counter_expectations
                or {
                    "connector_called_count": 0,
                    "payment_executed_count": 0,
                    "shipment_released_count": 0,
                }
            ),
        }
    )
    return packet


def validate_sandbox_receipt_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=SANDBOX_RECEIPT_CONTEXT_PACKET,
        required_fields=(
            "mock_receipt_refs",
            "adapter_names",
            "mock_only",
            "fake_connector_counter_notes",
            "real_external_counter_expectations",
        ),
    )
    reasons = list(validation["reasons"])
    if packet.get("mock_only") is not True:
        _append_reason(reasons, "sandbox_receipt_context_must_be_mock_only")
        _append_reason(reasons, "mock_receipt_is_not_real_payment")
    if any(
        bool(packet.get(key))
        for key in (
            "payment_executed",
            "shipment_released",
            "real_payment_executed",
            "real_shipment_released",
        )
    ):
        _append_reason(reasons, "mock_receipt_is_not_real_payment")
    real_external_expectations = packet.get("real_external_counter_expectations") or {}
    for key in (
        "connector_called_count",
        "payment_executed_count",
        "shipment_released_count",
        "real_bank_api_called_count",
        "real_supplier_api_called_count",
        "real_warehouse_api_called_count",
        "action_permission_created_count",
    ):
        if bool(real_external_expectations.get(key)):
            _append_reason(
                reasons,
                f"sandbox_receipt_real_external_counter_must_remain_zero:{key}",
            )
    return context_packet_validation_result(reasons, validation["packet_type"])


def build_root_review_context_packet(
    *,
    packet_id: str = "context_packet:root_review:v01",
    created_by: str = "bounded_context_packet_builder",
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    pre_root_advisory_summary: Mapping[str, Any] | None = None,
    post_vv_summary: Mapping[str, Any] | None = None,
    gt_lgt_summary: Mapping[str, Any] | None = None,
    root_boundary_expectations: Mapping[str, Any] | None = None,
    final_output_creator: str = "root_only",
    action_commit_packet_creator: str = "root_mock_approval_gate_only",
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=ROOT_REVIEW_CONTEXT_PACKET,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "pre_root_advisory_summary": dict(pre_root_advisory_summary or {}),
            "post_vv_summary": dict(post_vv_summary or {}),
            "gt_lgt_summary": dict(gt_lgt_summary or {}),
            "root_boundary_expectations": dict(root_boundary_expectations or {}),
            "final_output_creator": final_output_creator,
            "action_commit_packet_creator": action_commit_packet_creator,
        }
    )
    return packet


def validate_root_review_context_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_context_packet_common(
        packet,
        expected_packet_type=ROOT_REVIEW_CONTEXT_PACKET,
        required_fields=(
            "pre_root_advisory_summary",
            "post_vv_summary",
            "gt_lgt_summary",
            "root_boundary_expectations",
            "final_output_creator",
            "action_commit_packet_creator",
        ),
    )
    reasons = list(validation["reasons"])
    if packet.get("final_output_creator") != "root_only":
        _append_reason(reasons, "root_review_final_output_creator_must_be_root_only")
    if packet.get("action_commit_packet_creator") != "root_mock_approval_gate_only":
        _append_reason(
            reasons,
            "root_review_action_packet_creator_must_be_root_mock_approval_gate_only",
        )
    return context_packet_validation_result(reasons, validation["packet_type"])
