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
BOUNDED_SEMANTIC_EVIDENCE_PACKET_TYPE = "BoundedSemanticEvidencePacket"
ARCHITECT_PLAN_CONTEXT_PACKET = "ArchitectPlanContextPacket"
FRACTAL_BRANCH_TASK_CONTEXT_PACKET = "FractalBranchTaskContextPacket"
SANDBOX_RECEIPT_CONTEXT_PACKET = "SandboxReceiptContextPacket"
ROOT_REVIEW_CONTEXT_PACKET = "RootReviewContextPacket"

BOUNDED_SEMANTIC_EVIDENCE_PACKET_SCHEMA_VERSION = (
    "bounded_semantic_evidence_packet_v0.1"
)
BOUNDED_SEMANTIC_EVIDENCE_PACKET_CREATED_BY_DEFAULT = (
    "runtime/bounded_context_packet_builder"
)

BOUNDED_SEMANTIC_EVIDENCE_ITEM_SOURCES = (
    "provider_semantic_reasoning",
    "runtime_canonicalization",
    "validated_context_packet",
    "structured_rationale",
)
BOUNDED_SEMANTIC_EVIDENCE_ITEM_KINDS = (
    "observed_fact",
    "missing_evidence",
    "uncertainty",
    "risk_boundary",
    "rejected_route",
    "approval_condition",
    "authority_boundary",
)
BOUNDED_SEMANTIC_EVIDENCE_CONFIDENCE_LABELS = (
    "low",
    "medium",
    "high",
    "unknown",
)
BOUNDED_SEMANTIC_EVIDENCE_ITEM_FIELDS = (
    "observed_semantic_facts",
    "missing_evidence",
    "uncertainty_notes",
    "risk_boundary_notes",
    "rejected_action_routes",
    "required_approvals_or_conditions",
    "authority_boundary_notes",
)
BOUNDED_SEMANTIC_EVIDENCE_FIELDS = (
    *BOUNDED_SEMANTIC_EVIDENCE_ITEM_FIELDS,
    "selected_vector_ids",
    "required_guards",
)
BOUNDED_SEMANTIC_EVIDENCE_REQUIRED_FIELDS = (
    "packet_type",
    "packet_id",
    "created_by",
    "source_role",
    "target_role",
    "source_route_id",
    "source_proposal_id",
    "source_context_packet_id",
    "source_structured_rationale_ref",
    "source_refs",
    "schema_version",
    "domain",
    "root_final_authority_preserved",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "action_commit_packet_claimed",
    "root_bypass_claimed",
    "real_world_effects_allowed",
    "raw_user_text_included",
    "raw_cross_role_text_included",
    "ContextPacket is not truth",
    "ContextPacket is not authority",
    "BoundedSemanticEvidencePacket is not truth",
    "BoundedSemanticEvidencePacket is not authority",
    "BoundedSemanticEvidencePacket is not FinalOutput",
    "BoundedSemanticEvidencePacket is not ActionCommitPacket",
    "Evidence packet is not action permission",
    "Gemini proposes, Root disposes",
    "Root remains final authority",
    *BOUNDED_SEMANTIC_EVIDENCE_FIELDS,
)
BOUNDED_SEMANTIC_EVIDENCE_MAX_ITEM_TEXT_LENGTH = 280
BOUNDED_SEMANTIC_EVIDENCE_MAX_ITEMS_PER_FIELD = 12
BOUNDED_SEMANTIC_EVIDENCE_MAX_TOTAL_ITEMS = 48


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


def _is_non_string_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple)) and not isinstance(value, str)


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


def semantic_evidence_item(
    text: str,
    *,
    source: str,
    evidence_kind: str,
    confidence_label: str = "unknown",
    candidate_only: bool = True,
    raw_quote: bool = False,
) -> dict[str, Any]:
    return {
        "text": str(text).strip(),
        "source": source,
        "evidence_kind": evidence_kind,
        "confidence_label": confidence_label,
        "candidate_only": candidate_only,
        "raw_quote": raw_quote,
    }


def _default_semantic_evidence_item(
    text: str,
    *,
    evidence_kind: str,
) -> dict[str, Any]:
    return semantic_evidence_item(
        text,
        source="runtime_canonicalization",
        evidence_kind=evidence_kind,
        confidence_label="unknown",
    )


def _as_evidence_item_tuple(
    value: Iterable[Mapping[str, Any]] | None,
    *,
    default_text: str,
    evidence_kind: str,
) -> tuple[dict[str, Any], ...]:
    if value is None:
        return (_default_semantic_evidence_item(default_text, evidence_kind=evidence_kind),)
    return tuple(dict(item) for item in value)


def validate_semantic_evidence_items(
    items: Any,
    *,
    field: str,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not _is_non_string_sequence(items):
        return (f"bounded_semantic_evidence_items_must_be_sequence:{field}",)
    if not items:
        return (f"bounded_semantic_evidence_empty_field:{field}",)
    if len(items) > BOUNDED_SEMANTIC_EVIDENCE_MAX_ITEMS_PER_FIELD:
        _append_reason(reasons, f"bounded_semantic_evidence_too_many_items:{field}")

    for item in items:
        if not isinstance(item, Mapping):
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_must_be_mapping:{field}",
            )
            continue

        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            _append_reason(reasons, f"bounded_semantic_evidence_item_empty_text:{field}")
        elif len(text.strip()) > BOUNDED_SEMANTIC_EVIDENCE_MAX_ITEM_TEXT_LENGTH:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_text_too_long:{field}",
            )

        if "source" not in item:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_missing_source:{field}",
            )
        elif item.get("source") not in BOUNDED_SEMANTIC_EVIDENCE_ITEM_SOURCES:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_source_not_allowed:{field}",
            )

        if "evidence_kind" not in item:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_missing_kind:{field}",
            )
        elif item.get("evidence_kind") not in BOUNDED_SEMANTIC_EVIDENCE_ITEM_KINDS:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_kind_not_allowed:{field}",
            )

        if item.get("confidence_label") not in BOUNDED_SEMANTIC_EVIDENCE_CONFIDENCE_LABELS:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_confidence_label_not_allowed:{field}",
            )
        if item.get("candidate_only") is not True:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_candidate_only_must_be_true:{field}",
            )
        if item.get("raw_quote") is not False:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_raw_quote_must_be_false:{field}",
            )
    return tuple(reasons)


def _runtime_bounded_semantic_evidence_creator(created_by: Any) -> bool:
    if not isinstance(created_by, str):
        return False
    creator = created_by.strip().lower()
    if not creator.startswith("runtime/"):
        return False
    return "gemini" not in creator and "provider" not in creator


def _bounded_semantic_evidence_raw_text_reasons(
    packet: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, _value in _walk_key_values(packet):
        key_text = key or ""
        if key_text in {"raw_user_request", "raw_user_text"}:
            _append_reason(reasons, "bounded_semantic_evidence_raw_user_text_forbidden")
        if key_text == "raw_cross_role_text":
            _append_reason(
                reasons,
                "bounded_semantic_evidence_raw_cross_role_text_forbidden",
            )
        if key_text == "raw_gemini_text":
            _append_reason(
                reasons,
                "bounded_semantic_evidence_raw_gemini_text_forbidden",
            )
    return tuple(reasons)


def _bounded_semantic_evidence_unbounded_dump_reasons(
    packet: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, _value in _walk_key_values(packet):
        key_text = key or ""
        if key_text in {"full_runner_state_dump", "unbounded_context_dump"}:
            _append_reason(reasons, "unbounded_context_dump_forbidden")
        if key_text in {"raw_plan_graph_context", "raw_plangraph_context"}:
            _append_reason(reasons, "unbounded_plangraph_context_dump_forbidden")
    return tuple(reasons)


def _bounded_semantic_evidence_string_sequence_reasons(
    value: Any,
    *,
    field: str,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not _is_non_string_sequence(value):
        return (f"bounded_semantic_evidence_items_must_be_sequence:{field}",)
    if not value:
        return (f"bounded_semantic_evidence_empty_field:{field}",)
    for item in value:
        if not isinstance(item, str):
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_item_must_be_string:{field}",
            )
        elif not item.strip():
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_empty_item:{field}",
            )
    return tuple(reasons)


def _bounded_surface_text_has_marker(text: str) -> bool:
    lowered = text.lower()
    spaced = lowered.replace("_", " ").replace("-", " ")
    compact = spaced.replace(" ", "")
    phrase_markers = (
        "action permission",
        "connector command",
        "final output",
        "real world effect",
        "real robot api",
        "direct action",
        "door unlock",
        "dispatch robot",
        "execute payment",
        "payment executed",
        "shipment released",
        "create action permission",
    )
    compact_markers = ("actioncommitpacket",)
    return any(marker in spaced for marker in phrase_markers) or any(
        marker in compact for marker in compact_markers
    )


def _bounded_evidence_item_text_is_safe_negative_surface_context(
    item: Mapping[str, Any],
) -> bool:
    text = item.get("text")
    if not isinstance(text, str):
        return False
    if item.get("candidate_only") is not True or item.get("raw_quote") is not False:
        return False
    if item.get("evidence_kind") not in {
        "rejected_route",
        "risk_boundary",
        "authority_boundary",
        "approval_condition",
        "missing_evidence",
        "uncertainty",
    }:
        return False

    lowered = text.lower()
    spaced = lowered.replace("_", " ").replace("-", " ")
    compact = spaced.replace(" ", "")
    unsafe_positive_markers = (
        "execute payment",
        "payment executed",
        "shipment released",
        "connector command should run",
        "create action permission",
        "real world effect allowed",
    )
    unsafe_positive_compact_markers = ("actioncommitpacketcreated",)
    if any(marker in spaced for marker in unsafe_positive_markers):
        return False
    if any(marker in compact for marker in unsafe_positive_compact_markers):
        return False

    safe_negative_markers = (
        "rejected",
        "blocked",
        "forbidden",
        "not allowed",
        "no delegated authority",
        "no action permission",
        "without authority",
        "cannot be authorized",
        "not authority",
        "not permission",
        "root review",
        "rather than direct action",
        "must not",
        "do not",
        "does not",
        "is not",
        "are not",
    )
    return any(marker in spaced for marker in safe_negative_markers)


def _bounded_semantic_evidence_surface_value_forbidden(value: Any) -> bool:
    if isinstance(value, Mapping):
        allowed_boundary_keys = {
            "BoundedSemanticEvidencePacket is not FinalOutput",
            "BoundedSemanticEvidencePacket is not ActionCommitPacket",
            "Evidence packet is not action permission",
        }
        allowed_false_keys = {
            "action_permission_claimed",
            "final_output_claimed",
            "connector_command_claimed",
            "action_commit_packet_claimed",
            "real_world_effects_allowed",
        }
        for key, item in value.items():
            key_text = str(key)
            if key_text in allowed_boundary_keys:
                continue
            if key_text in allowed_false_keys and item is False:
                continue
            if _bounded_surface_text_has_marker(key_text):
                return True
            if (
                key_text == "text"
                and isinstance(item, str)
                and _bounded_surface_text_has_marker(item)
                and _bounded_evidence_item_text_is_safe_negative_surface_context(value)
            ):
                continue
            if _bounded_semantic_evidence_surface_value_forbidden(item):
                return True
    elif isinstance(value, (list, tuple, set, frozenset)):
        return any(
            _bounded_semantic_evidence_surface_value_forbidden(item)
            for item in value
        )
    elif isinstance(value, str):
        return _bounded_surface_text_has_marker(value)
    return False


def _bounded_semantic_evidence_real_world_surface_reasons(
    packet: Mapping[str, Any],
) -> tuple[str, ...]:
    if _bounded_semantic_evidence_surface_value_forbidden(packet):
        return ("bounded_semantic_evidence_real_world_action_surface_forbidden",)
    return ()


def _selected_vector_ids_from_route_context(
    route_context_packet: Mapping[str, Any],
) -> tuple[Any, ...]:
    return _as_tuple(route_context_packet.get("selected_vector_ids"))


def _route_id_matches_context(
    source_route_id: Any,
    route_context_packet: Mapping[str, Any],
) -> bool:
    explicit_route = (
        route_context_packet.get("selected_route_id")
        or route_context_packet.get("route_id")
        or route_context_packet.get("source_route_id")
    )
    if explicit_route:
        return source_route_id == explicit_route
    allowed_routes = set(_as_tuple(route_context_packet.get("allowed_routes")))
    return bool(source_route_id) and source_route_id in allowed_routes


def build_bounded_semantic_evidence_packet(
    *,
    packet_id: str = "context_packet:bounded_semantic_evidence:v01",
    created_by: str = BOUNDED_SEMANTIC_EVIDENCE_PACKET_CREATED_BY_DEFAULT,
    source_refs: Iterable[Mapping[str, Any]] | None = None,
    domain: str = "generic",
    source_role: str = "orchestrator",
    target_role: str = "architect",
    source_route_id: str = "route:bounded_semantic_review",
    source_proposal_id: str = "proposal:bounded_semantic_review",
    source_context_packet_id: str = "context_packet:orchestrator_route:v01",
    source_structured_rationale_ref: str = "structured_orchestrator_rationale:accepted",
    observed_semantic_facts: Iterable[Mapping[str, Any]] | None = None,
    missing_evidence: Iterable[Mapping[str, Any]] | None = None,
    uncertainty_notes: Iterable[Mapping[str, Any]] | None = None,
    risk_boundary_notes: Iterable[Mapping[str, Any]] | None = None,
    rejected_action_routes: Iterable[Mapping[str, Any]] | None = None,
    required_approvals_or_conditions: Iterable[Mapping[str, Any]] | None = None,
    authority_boundary_notes: Iterable[Mapping[str, Any]] | None = None,
    selected_vector_ids: Iterable[str] | None = None,
    required_guards: Iterable[str] | None = None,
) -> dict[str, Any]:
    packet = _context_packet_base(
        packet_type=BOUNDED_SEMANTIC_EVIDENCE_PACKET_TYPE,
        packet_id=packet_id,
        created_by=created_by,
        source_refs=source_refs,
        domain=domain,
    )
    packet.update(
        {
            "source_role": source_role,
            "target_role": target_role,
            "source_route_id": source_route_id,
            "source_proposal_id": source_proposal_id,
            "source_context_packet_id": source_context_packet_id,
            "source_structured_rationale_ref": source_structured_rationale_ref,
            "schema_version": BOUNDED_SEMANTIC_EVIDENCE_PACKET_SCHEMA_VERSION,
            "action_commit_packet_claimed": False,
            "raw_user_text_included": False,
            "raw_cross_role_text_included": False,
            "ContextPacket is not truth": True,
            "ContextPacket is not authority": True,
            "BoundedSemanticEvidencePacket is not truth": True,
            "BoundedSemanticEvidencePacket is not authority": True,
            "BoundedSemanticEvidencePacket is not FinalOutput": True,
            "BoundedSemanticEvidencePacket is not ActionCommitPacket": True,
            "Evidence packet is not action permission": True,
            "Gemini proposes, Root disposes": True,
            "observed_semantic_facts": _as_evidence_item_tuple(
                observed_semantic_facts,
                default_text="Bounded semantic fact remains candidate evidence.",
                evidence_kind="observed_fact",
            ),
            "missing_evidence": _as_evidence_item_tuple(
                missing_evidence,
                default_text="Missing evidence remains unresolved.",
                evidence_kind="missing_evidence",
            ),
            "uncertainty_notes": _as_evidence_item_tuple(
                uncertainty_notes,
                default_text="Uncertainty remains visible for Architect review.",
                evidence_kind="uncertainty",
            ),
            "risk_boundary_notes": _as_evidence_item_tuple(
                risk_boundary_notes,
                default_text="Risk boundary remains advisory and bounded.",
                evidence_kind="risk_boundary",
            ),
            "rejected_action_routes": _as_evidence_item_tuple(
                rejected_action_routes,
                default_text="External action route remains rejected.",
                evidence_kind="rejected_route",
            ),
            "required_approvals_or_conditions": _as_evidence_item_tuple(
                required_approvals_or_conditions,
                default_text="Required condition remains pending review.",
                evidence_kind="approval_condition",
            ),
            "authority_boundary_notes": _as_evidence_item_tuple(
                authority_boundary_notes,
                default_text="Root remains final authority.",
                evidence_kind="authority_boundary",
            ),
            "selected_vector_ids": _as_tuple(selected_vector_ids)
            or ("vector:bounded_semantic_review",),
            "required_guards": _as_tuple(required_guards)
            or (
                "ContextPacket validation",
                "structured rationale validation",
                "Root final authority",
            ),
        }
    )
    return packet


def validate_bounded_semantic_evidence_packet(
    packet: Mapping[str, Any],
    *,
    route_context_packet: Mapping[str, Any] | None = None,
    orchestrator_proposal: Mapping[str, Any] | None = None,
    structured_rationale_validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    packet_type = packet.get("packet_type")

    for field in BOUNDED_SEMANTIC_EVIDENCE_REQUIRED_FIELDS:
        if field not in packet:
            _append_reason(
                reasons,
                f"bounded_semantic_evidence_missing_required_field:{field}",
            )

    if packet_type != BOUNDED_SEMANTIC_EVIDENCE_PACKET_TYPE:
        _append_reason(reasons, "unexpected_packet_type:BoundedSemanticEvidencePacket")
    if packet.get("schema_version") != BOUNDED_SEMANTIC_EVIDENCE_PACKET_SCHEMA_VERSION:
        _append_reason(reasons, "bounded_semantic_evidence_schema_version_invalid")

    if not _runtime_bounded_semantic_evidence_creator(packet.get("created_by")):
        _append_reason(
            reasons,
            "bounded_semantic_evidence_packet_creator_must_be_runtime",
        )
    if packet.get("source_role") != "orchestrator":
        _append_reason(
            reasons,
            "bounded_semantic_evidence_source_role_must_be_orchestrator",
        )
    if packet.get("target_role") != "architect":
        _append_reason(
            reasons,
            "bounded_semantic_evidence_target_role_must_be_architect",
        )

    claim_reasons = {
        "truth_claimed": "bounded_semantic_evidence_truth_claim_forbidden",
        "authority_claimed": "bounded_semantic_evidence_authority_claim_forbidden",
        "action_permission_claimed": (
            "bounded_semantic_evidence_action_permission_claim_forbidden"
        ),
        "final_output_claimed": "bounded_semantic_evidence_final_output_claim_forbidden",
        "connector_command_claimed": (
            "bounded_semantic_evidence_connector_command_claim_forbidden"
        ),
        "action_commit_packet_claimed": (
            "bounded_semantic_evidence_action_commit_packet_claim_forbidden"
        ),
        "root_bypass_claimed": "bounded_semantic_evidence_root_bypass_claim_forbidden",
    }
    for field, reason in claim_reasons.items():
        if bool(packet.get(field)):
            _append_reason(reasons, reason)
    if bool(packet.get("drs_write_claimed")):
        _append_reason(reasons, "drs_write_claimed_forbidden")
    if packet.get("real_world_effects_allowed") is not False:
        _append_reason(reasons, "real_world_effects_allowed_forbidden")
    for field, reason in CONTEXT_PACKET_FORBIDDEN_READINESS_CLAIM_KEYS.items():
        if bool(packet.get(field)):
            _append_reason(reasons, reason)

    if packet.get("raw_user_text_included") is not False:
        _append_reason(
            reasons,
            "bounded_semantic_evidence_raw_user_text_included_must_be_false",
        )
    if packet.get("raw_cross_role_text_included") is not False:
        _append_reason(
            reasons,
            "bounded_semantic_evidence_raw_cross_role_text_included_must_be_false",
        )

    boundary_requirements = {
        "ContextPacket is not truth": (
            "bounded_semantic_evidence_context_packet_truth_boundary_required"
        ),
        "ContextPacket is not authority": (
            "bounded_semantic_evidence_context_packet_authority_boundary_required"
        ),
        "BoundedSemanticEvidencePacket is not truth": (
            "bounded_semantic_evidence_packet_truth_boundary_required"
        ),
        "BoundedSemanticEvidencePacket is not authority": (
            "bounded_semantic_evidence_packet_authority_boundary_required"
        ),
        "BoundedSemanticEvidencePacket is not FinalOutput": (
            "bounded_semantic_evidence_not_final_output_boundary_required"
        ),
        "BoundedSemanticEvidencePacket is not ActionCommitPacket": (
            "bounded_semantic_evidence_not_action_commit_packet_boundary_required"
        ),
        "Evidence packet is not action permission": (
            "bounded_semantic_evidence_not_action_permission_boundary_required"
        ),
        "Gemini proposes, Root disposes": (
            "bounded_semantic_evidence_gemini_root_boundary_required"
        ),
        "Root remains final authority": (
            "bounded_semantic_evidence_root_final_authority_required"
        ),
    }
    for field, reason in boundary_requirements.items():
        if packet.get(field) is not True:
            _append_reason(reasons, reason)
    if packet.get("root_final_authority_preserved") is not True:
        _append_reason(reasons, "bounded_semantic_evidence_root_final_authority_required")

    total_items = 0
    for field in BOUNDED_SEMANTIC_EVIDENCE_ITEM_FIELDS:
        items = packet.get(field)
        item_reasons = validate_semantic_evidence_items(items, field=field)
        reasons.extend(item_reasons)
        if _is_non_string_sequence(items):
            total_items += len(items)
    for field in ("selected_vector_ids", "required_guards"):
        value = packet.get(field)
        reasons.extend(
            _bounded_semantic_evidence_string_sequence_reasons(value, field=field)
        )
    if total_items > BOUNDED_SEMANTIC_EVIDENCE_MAX_TOTAL_ITEMS:
        _append_reason(reasons, "bounded_semantic_evidence_too_many_total_items")

    reasons.extend(_bounded_semantic_evidence_raw_text_reasons(packet))
    reasons.extend(_bounded_semantic_evidence_unbounded_dump_reasons(packet))
    reasons.extend(_bounded_semantic_evidence_real_world_surface_reasons(packet))
    reasons.extend(context_packet_secret_marker_reasons(packet))

    if route_context_packet is not None:
        selected_values = _as_tuple(packet.get("selected_vector_ids"))
        selected = {item for item in selected_values if isinstance(item, str)}
        route_vectors = set(_selected_vector_ids_from_route_context(route_context_packet))
        if not selected.issubset(route_vectors):
            _append_reason(
                reasons,
                "bounded_semantic_evidence_selected_vectors_must_be_subset_of_route_vectors",
            )
        if not _route_id_matches_context(packet.get("source_route_id"), route_context_packet):
            _append_reason(reasons, "bounded_semantic_evidence_source_route_mismatch")
        if packet.get("source_context_packet_id") != route_context_packet.get("packet_id"):
            _append_reason(
                reasons,
                "bounded_semantic_evidence_source_context_packet_mismatch",
            )

    if orchestrator_proposal is not None and packet.get(
        "source_proposal_id"
    ) != orchestrator_proposal.get("proposal_id"):
        _append_reason(reasons, "bounded_semantic_evidence_source_proposal_mismatch")

    if structured_rationale_validation is not None:
        if not packet.get("source_structured_rationale_ref") or structured_rationale_validation.get(
            "accepted"
        ) is not True:
            _append_reason(
                reasons,
                "bounded_semantic_evidence_source_rationale_missing_or_unaccepted",
            )

    return context_packet_validation_result(reasons, packet_type)


def bounded_semantic_evidence_packet_validation_result(
    reasons: Iterable[str],
    packet_type: str | None = BOUNDED_SEMANTIC_EVIDENCE_PACKET_TYPE,
) -> dict[str, Any]:
    return context_packet_validation_result(reasons, packet_type)


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
        "real_" + "ware" + "house_api_called_count",
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
