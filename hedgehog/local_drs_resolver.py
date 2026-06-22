from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.reuse_gate import compute_reuse_score
from hedgehog.time_model import make_temporal_query, make_time_envelope


UNSAFE_TRUE_KEYS = {
    "action_executed",
    "action_permission_claimed",
    "action_permission_granted",
    "authority_claimed",
    "autonomous_action_executed",
    "bypass_root",
    "connector_action_executed",
    "connector_side_effect",
    "connector_side_effects",
    "external_drs_implemented",
    "external_drs_network_write",
    "external_drs_used",
    "external_drs_write",
    "external_global_drs_implemented",
    "external_global_drs_used",
    "external_global_drs_write",
    "future_action_permission",
    "gemini_used",
    "global_drs_implemented",
    "global_drs_used",
    "global_drs_write",
    "manifest_mutated",
    "manifest_mutation",
    "manifest_mutation_claimed",
    "network_used",
    "pointer_trust_claimed",
    "production_drs_implemented",
    "production_drs_used",
    "production_external_action_executed",
    "production_persistence",
    "production_persistence_claimed",
    "real_external_action_executed",
    "root_bypass",
    "root_final_authority_bypassed",
    "schema_validity_truth_claimed",
    "semantic_truth_claimed",
    "source_truth_claimed",
    "transition_matrix_mutated",
    "transition_matrix_mutation",
    "transition_matrix_mutation_claimed",
    "truth_claimed",
    "validation_packet_authority_claimed",
}

RAW_ARTIFACT_TYPES = {
    "ConnectorObservation",
    "connector_observation",
    "EvidenceCandidate",
    "evidence_candidate",
    "ResultProposal",
    "result_proposal",
    "ValidationPacket",
    "validation_packet",
}

RAW_ARTIFACT_TYPE_TOKENS = {
    "connector_observation",
    "connectorobservation",
    "evidence_candidate",
    "evidencecandidate",
    "result_proposal",
    "resultproposal",
    "validation_packet",
    "validationpacket",
}

ROOT_REVIEWED_WRITEBACK_TYPE_TOKENS = {
    "root_final",
    "rootfinal",
    "root_final_output",
    "rootfinaloutput",
    "root_reviewed_semantic_outcome",
    "rootreviewedsemanticoutcome",
}

RAW_SHAPE_KEYS = {"packet_id", "candidate_id", "result_payload"}


@dataclass(frozen=True)
class SemanticDRSRecordInput:
    record_id: str
    domain: str
    content: dict[str, Any]
    semantic_keys: tuple[str, ...] = ()
    layer: str = "work"
    record_type: str = "generic"
    time_envelope: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    trace_refs: tuple[dict[str, Any], ...] = ()
    source_refs: tuple[dict[str, Any], ...] = ()
    status: str = "active"
    gt: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    root_final_ref: str | None = None
    worldstate_ref: str | None = None
    poisoning_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticResolveQuery:
    query_id: str
    domain: str
    semantic_terms: tuple[str, ...] = ()
    content_filters: dict[str, Any] = field(default_factory=dict)
    temporal_query: dict[str, Any] | None = None
    worldstate: dict[str, Any] | None = None
    source_refs: tuple[dict[str, Any], ...] = ()
    trace_refs: tuple[dict[str, Any], ...] = ()
    max_candidates: int = 10
    require_root_review: bool = True
    risk_class: str = "normal"


@dataclass(frozen=True)
class ResolvedDRSCandidate:
    candidate_id: str
    record_id: str
    domain: str
    match_score: float
    match_reasons: tuple[str, ...]
    review_required: bool
    blocked: bool
    direct_reuse_allowed: bool
    action_permission_granted: bool
    stale: bool
    quarantine_pressure: bool
    deadend_pressure: bool
    conflicting_provenance: bool
    changed_worldstate: bool
    poisoning_pressure: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ResolvedDRSReport:
    query_id: str
    candidates: tuple[ResolvedDRSCandidate, ...]
    candidate_count: int
    root_review_required: bool
    direct_reuse_allowed_count: int
    blocked_count: int
    review_required_count: int
    authority_boundary: dict[str, Any]
    counters: dict[str, int]
    reason_codes: tuple[str, ...]


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def _assert_no_unsafe_claims(value: Any, *, context: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower()
            if normalized in UNSAFE_TRUE_KEYS and _is_truthy(child):
                raise ValueError(f"{context} rejects unsafe claim: {key}")
            _assert_no_unsafe_claims(child, context=context)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _assert_no_unsafe_claims(item, context=context)


def _trace_refs_for(record_id: str, trace_refs: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    if trace_refs:
        return [dict(ref) for ref in trace_refs]
    return [{"trace_id": f"trace:{record_id}", "kind": "local_drs_resolver"}]


def _normalize_provenance(
    record_id: str,
    provenance: dict[str, Any] | None,
    trace_refs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    allowed = {"request_id", "created_by", "trace_refs"}
    if provenance:
        extra = set(provenance) - allowed
        if extra:
            raise ValueError(f"DRS provenance contains unsupported fields: {sorted(extra)}")
        normalized = dict(provenance)
        normalized.setdefault("request_id", f"req:{record_id}")
        normalized.setdefault("created_by", "root_orchestrator")
        normalized.setdefault("trace_refs", _trace_refs_for(record_id, trace_refs))
        return normalized
    return {
        "request_id": f"req:{record_id}",
        "created_by": "root_orchestrator",
        "trace_refs": _trace_refs_for(record_id, trace_refs),
    }


def _enriched_content(record_input: SemanticDRSRecordInput) -> dict[str, Any]:
    content = dict(record_input.content)
    if record_input.semantic_keys:
        content["semantic_keys"] = list(record_input.semantic_keys)
    if record_input.root_final_ref:
        content["root_final_ref"] = record_input.root_final_ref
    if record_input.worldstate_ref:
        content["worldstate_ref"] = record_input.worldstate_ref
    if record_input.poisoning_markers:
        content["poisoning_markers"] = list(record_input.poisoning_markers)
    content.setdefault("drs_record_is_truth", False)
    content.setdefault("drs_hit_is_authority", False)
    content.setdefault("drs_reuse_candidate_is_action_permission", False)
    return content


def write_semantic_record(
    drs: LocalDRS,
    record_input: SemanticDRSRecordInput,
) -> dict[str, Any]:
    _assert_no_unsafe_claims(record_input.content, context="write_semantic_record")

    trace_refs = _trace_refs_for(record_input.record_id, record_input.trace_refs)
    provenance = _normalize_provenance(
        record_input.record_id,
        record_input.provenance,
        tuple(trace_refs),
    )
    record = {
        "record_id": record_input.record_id,
        "layer": record_input.layer,
        "type": record_input.record_type,
        "domain": record_input.domain,
        "content": _enriched_content(record_input),
        "time_envelope": record_input.time_envelope
        or make_time_envelope("sess_real_local_drs_resolver_v01"),
        "provenance": provenance,
        "status": record_input.status,
        "trace_refs": trace_refs,
    }
    if record_input.source_refs:
        record["source_refs"] = [dict(ref) for ref in record_input.source_refs]
    if record_input.gt:
        record["gt"] = dict(record_input.gt)
    if record_input.validation:
        record["validation"] = dict(record_input.validation)

    _assert_no_unsafe_claims(record, context="write_semantic_record")
    drs.write_record(record)
    return record


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _is_stale(record: dict[str, Any], temporal_query: dict[str, Any]) -> bool:
    envelope = record.get("time_envelope") or {}
    if str(envelope.get("freshness_class", "")).lower() in {"stale", "expired"}:
        return True
    valid_to = _parse_time(envelope.get("valid_to"))
    as_of = _parse_time(temporal_query.get("as_of"))
    if valid_to and as_of and valid_to < as_of:
        return True
    return compute_reuse_score(record, temporal_query)["freshness"] < 0.5


def _tokens(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, dict):
        result: set[str] = set()
        for key, child in value.items():
            result.update(_tokens(key))
            result.update(_tokens(child))
        return result
    if isinstance(value, (list, tuple, set)):
        result = set()
        for item in value:
            result.update(_tokens(item))
        return result
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", str(value).lower())
        if token
    }


def _content_filter_match(content: dict[str, Any], filters: dict[str, Any]) -> bool:
    return all(content.get(key) == value for key, value in filters.items())


def _source_trace_overlap(record: dict[str, Any], query: SemanticResolveQuery) -> tuple[bool, bool]:
    record_sources = {
        (ref.get("source"), ref.get("source_id"))
        for ref in record.get("source_refs", [])
    }
    query_sources = {
        (ref.get("source"), ref.get("source_id"))
        for ref in query.source_refs
    }
    record_traces = {
        ref.get("trace_id")
        for ref in record.get("trace_refs", [])
    } | {
        ref.get("trace_id")
        for ref in (record.get("provenance", {}).get("trace_refs") or [])
    }
    query_traces = {ref.get("trace_id") for ref in query.trace_refs}
    return bool(record_sources & query_sources), bool(record_traces & query_traces)


def _signature(record: dict[str, Any]) -> tuple[Any, ...]:
    content = record.get("content") or {}
    if "duplicate_group" in content:
        return (record.get("domain"), "duplicate_group", content.get("duplicate_group"))
    return (
        record.get("domain"),
        content.get("subject_key"),
        content.get("claim_key"),
        content.get("claim_value"),
    )


def _duplicate_counts(records: list[dict[str, Any]]) -> dict[tuple[Any, ...], int]:
    counts: dict[tuple[Any, ...], int] = {}
    for record in records:
        signature = _signature(record)
        if any(value is not None for value in signature[1:]):
            counts[signature] = counts.get(signature, 0) + 1
    return counts


def _worldstate_changed(record: dict[str, Any], query: SemanticResolveQuery) -> bool:
    if not query.worldstate:
        return False
    content = record.get("content") or {}
    record_worldstate = content.get("worldstate")
    if not isinstance(record_worldstate, dict):
        record_worldstate = {
            key: content[key]
            for key in ("worldstate_version", "worldstate_hash", "claim_value")
            if key in content
        }
    for key, current_value in query.worldstate.items():
        if key in record_worldstate and record_worldstate[key] != current_value:
            return True
    return False


def _has_external_pointer_pressure(record: dict[str, Any]) -> bool:
    content = record.get("content") or {}
    if int(content.get("repeated_external_pointer_count") or 0) > 1:
        return True
    return any(ref.get("source") == "external_drs" for ref in record.get("source_refs", []))


def _candidate_from_record(
    record: dict[str, Any],
    query: SemanticResolveQuery,
    temporal_query: dict[str, Any],
    duplicate_counts: dict[tuple[Any, ...], int],
) -> ResolvedDRSCandidate | None:
    if record.get("domain") != query.domain:
        return None

    content = record.get("content") or {}
    filter_match = _content_filter_match(content, query.content_filters)
    query_tokens = _tokens(query.semantic_terms)
    record_tokens = _tokens(
        {
            "record_id": record.get("record_id"),
            "domain": record.get("domain"),
            "content": content,
            "status": record.get("status"),
        }
    )
    token_overlap = query_tokens & record_tokens
    source_overlap, trace_overlap = _source_trace_overlap(record, query)
    if query.content_filters and not filter_match:
        return None
    if query.semantic_terms and not (token_overlap or source_overlap or trace_overlap):
        return None

    match_reasons: list[str] = ["domain_exact_match"]
    if filter_match and query.content_filters:
        match_reasons.append("explicit_content_key_match")
    if token_overlap:
        match_reasons.append("controlled_token_overlap")
    if source_overlap:
        match_reasons.append("source_refs_overlap")
    if trace_overlap:
        match_reasons.append("trace_refs_overlap")

    stale = _is_stale(record, temporal_query)
    quarantine_pressure = (
        record.get("layer") == "quarantine"
        or record.get("status") == "quarantined"
        or bool(content.get("quarantine_proximity"))
    )
    deadend_pressure = (
        record.get("layer") == "deadends"
        or record.get("type") == "dead_end"
        or bool(content.get("deadend_proximity"))
    )
    conflicting_provenance = bool(
        content.get("conflicting_provenance")
        or content.get("conflict_detected")
        or (record.get("validation") or {}).get("decision") == "reject"
    )
    changed_worldstate = _worldstate_changed(record, query)
    duplicate_pressure = duplicate_counts.get(_signature(record), 0) > 1
    poisoning_pressure = bool(
        duplicate_pressure
        or content.get("poisoning_markers")
        or content.get("compromised_signal")
        or content.get("upstream_looking")
        or _has_external_pointer_pressure(record)
    )

    blocked = any(
        (
            quarantine_pressure,
            deadend_pressure,
            conflicting_provenance,
            changed_worldstate,
            poisoning_pressure,
        )
    )
    review_required = query.require_root_review or stale or blocked
    reasons: list[str] = [
        "candidate_only_root_review_required",
        "root_review_required_before_reuse_affects_final_output",
    ]
    if stale:
        reasons.append("stale_record_forces_root_review")
    if quarantine_pressure or deadend_pressure:
        reasons.append("quarantine_proximity_blocks_direct_reuse")
    if changed_worldstate:
        reasons.append("changed_worldstate_blocks_old_reuse")
    if conflicting_provenance:
        reasons.append("conflicting_provenance_blocks_reuse")
    if poisoning_pressure:
        reasons.append("duplicate_poisoning_pressure_does_not_create_authority")
    if content.get("schema_valid") is True:
        reasons.append("schema_valid_record_not_semantic_truth")
    if content.get("accepted_evidence") is True:
        reasons.append("accepted_historical_evidence_not_future_action_permission")
    if _has_external_pointer_pressure(record):
        reasons.append("repeated_external_pointer_not_trust")

    base_score = 1.0 if "domain_exact_match" in match_reasons else 0.0
    base_score += 0.25 if filter_match and query.content_filters else 0.0
    base_score += min(0.5, len(token_overlap) * 0.1)
    base_score += 0.1 if source_overlap else 0.0
    base_score += 0.1 if trace_overlap else 0.0

    return ResolvedDRSCandidate(
        candidate_id=f"candidate:{record['record_id']}",
        record_id=record["record_id"],
        domain=record["domain"],
        match_score=round(min(base_score, 1.0), 3),
        match_reasons=tuple(match_reasons),
        review_required=review_required,
        blocked=blocked,
        direct_reuse_allowed=False,
        action_permission_granted=False,
        stale=stale,
        quarantine_pressure=quarantine_pressure,
        deadend_pressure=deadend_pressure,
        conflicting_provenance=conflicting_provenance,
        changed_worldstate=changed_worldstate,
        poisoning_pressure=poisoning_pressure,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def resolve_semantic_candidates(
    drs: LocalDRS,
    query: SemanticResolveQuery,
    *,
    layers: tuple[str, ...] = ("work", "thoughts", "quarantine", "deadends"),
) -> ResolvedDRSReport:
    temporal_query = query.temporal_query or make_temporal_query()
    records = drs.query_records(temporal_query, list(layers))
    counts = _duplicate_counts(records)
    candidates = [
        candidate
        for record in records
        if (
            candidate := _candidate_from_record(
                record,
                query,
                temporal_query,
                counts,
            )
        )
        is not None
    ]
    candidates.sort(key=lambda item: (-item.match_score, item.record_id))
    candidates = candidates[: max(query.max_candidates, 0)]
    reason_codes = tuple(
        dict.fromkeys(
            reason
            for candidate in candidates
            for reason in candidate.reason_codes
        )
    )
    counters = {
        "candidates_returned_count": len(candidates),
        "direct_reuse_allowed_count": 0,
        "root_review_required_count": sum(1 for item in candidates if item.review_required),
        "stale_record_reuse_blocked_count": sum(1 for item in candidates if item.stale),
        "quarantine_reuse_blocked_count": sum(
            1 for item in candidates if item.quarantine_pressure or item.deadend_pressure
        ),
        "changed_worldstate_reuse_blocked_count": sum(
            1 for item in candidates if item.changed_worldstate
        ),
        "conflicting_provenance_blocked_count": sum(
            1 for item in candidates if item.conflicting_provenance
        ),
        "duplicate_poisoning_records_seen_count": sum(
            1 for item in candidates if item.poisoning_pressure
        ),
        "poisoning_pressure_authority_claimed_count": 0,
        "action_permission_granted_count": 0,
        "manifest_mutation_count": 0,
        "transition_matrix_mutation_count": 0,
        "production_drs_used_count": 0,
        "external_drs_used_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
    }
    return ResolvedDRSReport(
        query_id=query.query_id,
        candidates=tuple(candidates),
        candidate_count=len(candidates),
        root_review_required=query.require_root_review
        or any(candidate.review_required for candidate in candidates),
        direct_reuse_allowed_count=0,
        blocked_count=sum(1 for candidate in candidates if candidate.blocked),
        review_required_count=counters["root_review_required_count"],
        authority_boundary={
            "drs_record_is_truth": False,
            "drs_hit_is_authority": False,
            "drs_reuse_candidate_is_action_permission": False,
            "freshness_is_final_authority": False,
            "root_final_authority_preserved": True,
            "local_file_backed_drs_is_production_drs": False,
            "resolver_mutated_manifest": False,
            "resolver_mutated_transition_matrix": False,
            "resolver_called_network": False,
            "resolver_called_gemini": False,
            "resolver_called_connectors": False,
        },
        counters=counters,
        reason_codes=reason_codes,
    )


def _normalize_artifact_type(value: Any) -> str:
    normalized = str(value or "").strip()
    normalized = re.sub(r"(?<!^)(?=[A-Z])", "_", normalized)
    normalized = re.sub(r"[\s:-]+", "_", normalized)
    return normalized.lower()


def _has_root_writeback_identity(artifact: dict[str, Any]) -> bool:
    return bool(artifact.get("final_artifact_id") or artifact.get("outcome_id")) and bool(
        artifact.get("root_final_status")
    )


def _is_root_reviewed_artifact(artifact: dict[str, Any]) -> bool:
    artifact_type = artifact.get("artifact_type")
    normalized_type = _normalize_artifact_type(artifact_type)
    if artifact.get("artifact_type") in RAW_ARTIFACT_TYPES or normalized_type in RAW_ARTIFACT_TYPE_TOKENS:
        return False
    root_writeback_type = (
        not artifact_type or normalized_type in ROOT_REVIEWED_WRITEBACK_TYPE_TOKENS
    )
    raw_shape = any(key in artifact for key in RAW_SHAPE_KEYS)
    if raw_shape and not (
        normalized_type in ROOT_REVIEWED_WRITEBACK_TYPE_TOKENS
        and _has_root_writeback_identity(artifact)
    ):
        return False
    return (
        artifact.get("created_by") == "root_orchestrator"
        and artifact.get("root_reviewed") is True
        and root_writeback_type
        and _has_root_writeback_identity(artifact)
    )


def write_root_final_record(
    drs: LocalDRS,
    artifact: dict[str, Any],
    *,
    record_id: str | None = None,
) -> dict[str, Any]:
    _assert_no_unsafe_claims(artifact, context="write_root_final_record")
    if not _is_root_reviewed_artifact(artifact):
        raise ValueError("write_root_final_record requires Root-reviewed semantic outcome")

    artifact_id = artifact.get("final_artifact_id") or artifact.get("outcome_id")
    trace_refs = tuple(artifact.get("trace_refs") or [{"trace_id": f"trace:{artifact_id}"}])
    status = artifact.get("root_final_status")
    record_status = "accepted" if status in {"accepted", "completed", "success"} else "no_update"
    content = {
        "root_final_artifact_id": artifact_id,
        "root_final_status": status,
        "root_reviewed": True,
        "local_writeback_only": True,
        "action_side_effects": False,
        "connector_side_effects": False,
        "production_persistence_claimed": False,
        "external_global_drs_write": False,
        "root_final_authority_preserved": True,
        "summary": artifact.get("summary", "Root-reviewed semantic outcome recorded locally."),
    }
    return write_semantic_record(
        drs,
        SemanticDRSRecordInput(
            record_id=record_id or f"root_final_record:{artifact_id}",
            layer="work",
            record_type="trace_summary",
            domain=artifact.get("domain", "mock_government_certificate"),
            content=content,
            semantic_keys=("root_final", "writeback", str(status)),
            time_envelope=artifact.get("time_envelope")
            or make_time_envelope("sess_real_local_drs_writeback_v01"),
            provenance={
                "request_id": artifact.get("request_id", f"req:{artifact_id}"),
                "created_by": "root_orchestrator",
                "trace_refs": [dict(ref) for ref in trace_refs],
            },
            trace_refs=tuple(dict(ref) for ref in trace_refs),
            source_refs=(
                {
                    "source": "system",
                    "source_id": str(artifact_id),
                    "trace_ref": dict(trace_refs[0]),
                },
            ),
            status=record_status,
            root_final_ref=str(artifact_id),
        ),
    )
