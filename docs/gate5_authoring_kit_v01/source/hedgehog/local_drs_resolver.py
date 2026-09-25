from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Any

from hedgehog.drs import (
    REQUIRED_RECORD_FIELDS,
    LocalDRS,
    _safe_filename,
    assert_no_sensitive_drs_keys,
)
from hedgehog.drs_semantic_address_v01 import (
    LineageEdgeV01,
    MeaningRecordV01,
    meaning_record_to_plain_data_v01,
    validate_lineage_edge_v01,
    validate_meaning_record_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    ROOT_DECISION_ACCEPT,
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    root_decision_input_to_plain_dict_v01,
    root_decision_result_to_plain_dict_v01,
    validate_root_decision_input_v01,
    validate_root_decision_kernel_v01,
    validate_root_decision_result_v01,
)
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


_G2B_LOCAL_LAYERS_V01 = (
    "work",
    "thoughts",
    "quarantine",
    "deadends",
)
_G2B_WRITEBACK_PROPOSAL_DOMAIN_V01 = (
    "hedgehog:drs:meaning_record_writeback_proposal:v01"
)
_G2B_WRITEBACK_ROOT_RESULT_DOMAIN_V01 = (
    "hedgehog:drs:meaning_record_writeback_root_result_binding:v01"
)
_G2B_HISTORY_DOMAIN_V01 = "hedgehog:drs:meaning_record_history:v01"
_G2B_WRITEBACK_PREDICATE_V01 = (
    "authorize_g2b_immutable_meaning_record_writeback_v01"
)
_G2B_WRITEBACK_POLICY_REF_V01 = (
    "policy:drs_immutable_meaning_record_writeback:v0.1"
)
_G2B_STORAGE_PROFILE_V01 = "g2b_meaning_record_storage_v01"
_G2B_TOKEN_V01 = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _g2b_plain_copy_v01(value: object) -> object:
    return json.loads(
        json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _g2b_store_snapshot_v01(root: Path) -> tuple[tuple[object, ...], ...]:
    if not root.exists():
        return ()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("drs_legacy_source_invalid")
    rows: list[tuple[object, ...]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError("drs_legacy_source_invalid")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("drs_legacy_source_invalid")
        payload = path.read_bytes()
        rows.append(
            (
                path.relative_to(root).as_posix(),
                hashlib.sha256(payload).hexdigest(),
                len(payload),
                stat.S_IMODE(
                    path.stat(follow_symlinks=False).st_mode
                ),
            )
        )
    return tuple(rows)


def _g2b_read_local_records_v01(
    *,
    drs: LocalDRS,
    layers: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    try:
        if (
            type(drs) is not LocalDRS
            or type(layers) is not tuple
            or any(type(layer) is not str for layer in layers)
            or len(set(layers)) != len(layers)
            or any(layer not in _G2B_LOCAL_LAYERS_V01 for layer in layers)
        ):
            raise ValueError("drs_legacy_source_invalid")
        root = drs.root_path
        if not isinstance(root, Path):
            raise ValueError("drs_legacy_source_invalid")
        before = _g2b_store_snapshot_v01(root)
        if not root.exists():
            return ()
        records: list[dict[str, object]] = []
        for layer in layers:
            layer_path = root / layer
            if not layer_path.exists():
                continue
            if layer_path.is_symlink() or not layer_path.is_dir():
                raise ValueError("drs_legacy_source_invalid")
            for path in sorted(
                layer_path.iterdir(), key=lambda item: item.name
            ):
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or path.suffix != ".json"
                ):
                    raise ValueError("drs_legacy_source_invalid")
                payload = path.read_bytes()
                value = json.loads(payload.decode("utf-8"))
                if (
                    type(value) is not dict
                    or any(
                        type(key) is not str for key in value
                    )
                    or not REQUIRED_RECORD_FIELDS.issubset(value)
                    or value.get("layer") != layer
                    or type(value.get("record_id")) is not str
                    or path.name
                    != _safe_filename(value["record_id"])
                ):
                    raise ValueError("drs_legacy_source_invalid")
                assert_no_sensitive_drs_keys(value)
                records.append(_g2b_plain_copy_v01(value))
        after = _g2b_store_snapshot_v01(root)
        if before != after:
            raise ValueError("drs_read_write_boundary_violation")
        return tuple(records)
    except ValueError as exc:
        if str(exc) == "drs_read_write_boundary_violation":
            raise ValueError("drs_read_write_boundary_violation") from None
        raise ValueError("drs_legacy_source_invalid") from None
    except Exception:
        raise ValueError("drs_legacy_source_invalid") from None


def _g2b_storage_record_v01(
    *,
    meaning_record: MeaningRecordV01,
    writeback_metadata: dict[str, object],
) -> dict[str, object]:
    if (
        type(meaning_record) is not MeaningRecordV01
        or validate_meaning_record_v01(meaning_record) != (True, ())
        or type(writeback_metadata) is not dict
        or any(type(key) is not str for key in writeback_metadata)
    ):
        raise ValueError("drs_exact_type_or_identity_invalid") from None
    allowed = (
        "writeback_proposal_id",
        "supersession_evidence_id",
        "root_decision_id",
        "root_result_binding_hash",
    )
    if any(key not in allowed for key in writeback_metadata):
        raise ValueError("drs_exact_type_or_identity_invalid") from None
    metadata = {
        key: writeback_metadata.get(key) for key in allowed
    }
    record_id = meaning_record.meaning_record_id
    trace = {
        "trace_id": f"trace:{record_id}",
        "kind": "g2b_immutable_writeback",
    }
    return {
        "record_id": record_id,
        "layer": "work",
        "type": "generic",
        "domain": meaning_record.semantic_address.domain,
        "content": {
            "storage_profile": _G2B_STORAGE_PROFILE_V01,
            "canonical_meaning_record": (
                meaning_record_to_plain_data_v01(meaning_record)
            ),
            **metadata,
            "local_writeback_only": True,
            "production_persistence_claimed": False,
            "external_global_drs_write": False,
            "action_side_effects": False,
            "connector_side_effects": False,
            "creates_authority": False,
            "creates_permission": False,
            "real_world_effects_count": 0,
        },
        "time_envelope": {
            "pt_created_at": "2026-07-30T08:00:00Z",
            "kt_asof": "2026-07-30T08:00:00Z",
            "et_observed_at": "2026-07-30T08:00:00Z",
            "ct_session_anchor": "g2b5",
            "ttl_seconds": 86400,
            "freshness_class": "normal",
            "valid_from": "2026-07-30T08:00:00Z",
            "valid_to": "2026-07-31T08:00:00Z",
        },
        "provenance": {
            "request_id": f"request:{record_id}",
            "created_by": "root_orchestrator",
            "trace_refs": [trace],
        },
        "status": "accepted",
        "trace_refs": [trace],
        "source_refs": [
            {
                "source": "local_drs",
                "source_id": record_id,
                "trace_ref": trace,
            }
        ],
    }


def _g2b_predecessor_history_hash_v01(
    predecessor_record: MeaningRecordV01,
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=_G2B_HISTORY_DOMAIN_V01,
        payload=canonical_json_bytes_v01(
            meaning_record_to_plain_data_v01(predecessor_record)
        ),
    )


def _g2b_writeback_proposal_material_v01(
    *,
    predecessor_record: MeaningRecordV01,
    successor_commitment_record: MeaningRecordV01,
    claim_dimension: str,
    supersession_reason: str,
) -> tuple[object, ...]:
    return (
        "v0.1",
        predecessor_record.semantic_address.semantic_address_id,
        predecessor_record.meaning_record_id,
        successor_commitment_record.meaning_record_id,
        claim_dimension,
        supersession_reason,
        predecessor_record.authority_envelope.owning_local_root_id,
        predecessor_record.authority_envelope.authority_scope_fingerprint,
        predecessor_record.policy_version,
        predecessor_record.schema_versions,
        successor_commitment_record.time_envelope.valid_from,
        successor_commitment_record.time_envelope.valid_to,
        _g2b_predecessor_history_hash_v01(predecessor_record),
    )


def _g2b_writeback_proposal_id_v01(
    *,
    predecessor_record: MeaningRecordV01,
    successor_commitment_record: MeaningRecordV01,
    claim_dimension: str,
    supersession_reason: str,
) -> str:
    material = _g2b_writeback_proposal_material_v01(
        predecessor_record=predecessor_record,
        successor_commitment_record=successor_commitment_record,
        claim_dimension=claim_dimension,
        supersession_reason=supersession_reason,
    )
    return _g2b_writeback_proposal_id_from_material_v01(material)


def _g2b_writeback_proposal_id_from_material_v01(
    material: tuple[object, ...],
) -> str:
    return "g2bwriteback_v01:" + domain_separated_sha256_hex_v01(
        domain=_G2B_WRITEBACK_PROPOSAL_DOMAIN_V01,
        payload=canonical_json_bytes_v01(material),
    )


def _g2b_writeback_claim_preimage_v01(
    *,
    predecessor_record: MeaningRecordV01,
    successor_commitment_record: MeaningRecordV01,
    claim_dimension: str,
    supersession_reason: str,
) -> dict[str, object]:
    material = _g2b_writeback_proposal_material_v01(
        predecessor_record=predecessor_record,
        successor_commitment_record=successor_commitment_record,
        claim_dimension=claim_dimension,
        supersession_reason=supersession_reason,
    )
    names = (
        "profile_version",
        "semantic_address_id",
        "predecessor_record_id",
        "successor_commitment_record_id",
        "claim_dimension",
        "supersession_reason",
        "owning_local_root_id",
        "authority_scope_fingerprint",
        "policy_version",
        "schema_versions",
        "successor_valid_from",
        "successor_valid_to",
        "predecessor_source_history_hash",
    )
    return {
        "writeback_proposal_id": (
            _g2b_writeback_proposal_id_from_material_v01(material)
        ),
        **{
            name: list(value) if type(value) is tuple else value
            for name, value in zip(names, material, strict=True)
        },
        "writeback_policy_ref": _G2B_WRITEBACK_POLICY_REF_V01,
    }


def _g2b_writeback_root_result_hash_v01(
    *,
    root_decision_result: RootDecisionResultV01,
) -> str:
    if type(root_decision_result) is not RootDecisionResultV01:
        raise ValueError("drs_writeback_root_binding_invalid") from None
    return domain_separated_sha256_hex_v01(
        domain=_G2B_WRITEBACK_ROOT_RESULT_DOMAIN_V01,
        payload=canonical_json_bytes_v01(
            root_decision_result_to_plain_dict_v01(
                root_decision_result
            )
        ),
    )


def _g2b_wrapper_matches_v01(
    wrapper: object,
    record: MeaningRecordV01,
) -> bool:
    if (
        type(wrapper) is not dict
        or type(record) is not MeaningRecordV01
        or validate_meaning_record_v01(record) != (True, ())
        or set(wrapper)
        != {
            "record_id",
            "layer",
            "type",
            "domain",
            "content",
            "time_envelope",
            "provenance",
            "status",
            "trace_refs",
            "source_refs",
        }
    ):
        return False
    content = wrapper.get("content")
    expected_content_keys = {
        "storage_profile",
        "canonical_meaning_record",
        "writeback_proposal_id",
        "supersession_evidence_id",
        "root_decision_id",
        "root_result_binding_hash",
        "local_writeback_only",
        "production_persistence_claimed",
        "external_global_drs_write",
        "action_side_effects",
        "connector_side_effects",
        "creates_authority",
        "creates_permission",
        "real_world_effects_count",
    }
    optional_strings = (
        content.get("writeback_proposal_id")
        if type(content) is dict
        else object(),
        content.get("supersession_evidence_id")
        if type(content) is dict
        else object(),
        content.get("root_decision_id")
        if type(content) is dict
        else object(),
    )
    root_hash = (
        content.get("root_result_binding_hash")
        if type(content) is dict
        else object()
    )
    return (
        type(content) is dict
        and set(content) == expected_content_keys
        and type(wrapper.get("record_id")) is str
        and wrapper["record_id"] == record.meaning_record_id
        and type(wrapper.get("layer")) is str
        and wrapper["layer"] == "work"
        and type(wrapper.get("type")) is str
        and wrapper["type"] == "generic"
        and type(wrapper.get("domain")) is str
        and wrapper["domain"] == record.semantic_address.domain
        and type(wrapper.get("status")) is str
        and wrapper["status"] == "accepted"
        and type(wrapper.get("time_envelope")) is dict
        and type(wrapper.get("provenance")) is dict
        and type(wrapper.get("trace_refs")) is list
        and type(wrapper.get("source_refs")) is list
        and content.get("storage_profile")
        == _G2B_STORAGE_PROFILE_V01
        and type(content.get("canonical_meaning_record")) is dict
        and content.get("canonical_meaning_record")
        == meaning_record_to_plain_data_v01(record)
        and all(
            item is None or type(item) is str
            for item in optional_strings
        )
        and (
            root_hash is None
            or (
                type(root_hash) is str
                and re.fullmatch(r"[0-9a-f]{64}", root_hash)
                is not None
            )
        )
        and content.get("local_writeback_only") is True
        and content.get("production_persistence_claimed") is False
        and content.get("external_global_drs_write") is False
        and content.get("action_side_effects") is False
        and content.get("connector_side_effects") is False
        and content.get("creates_authority") is False
        and content.get("creates_permission") is False
        and type(content.get("real_world_effects_count")) is int
        and content["real_world_effects_count"] == 0
    )


def _g2b_validate_root_reviewed_writeback_geometry_v01(
    *,
    predecessor_record: MeaningRecordV01,
    successor_commitment_record: MeaningRecordV01,
    successor_record: MeaningRecordV01,
    claim_dimension: str,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
) -> tuple[str, str, LineageEdgeV01]:
    records = (
        predecessor_record,
        successor_commitment_record,
        successor_record,
    )
    if any(
        type(record) is not MeaningRecordV01
        or validate_meaning_record_v01(record) != (True, ())
        for record in records
    ):
        raise ValueError("drs_supersession_evidence_invalid") from None
    if (
        type(claim_dimension) is not str
        or _G2B_TOKEN_V01.fullmatch(claim_dimension) is None
    ):
        raise ValueError("drs_supersession_evidence_invalid") from None
    expected_tag = f"claim_dimension:{claim_dimension}"
    for record in records:
        claim_dimension_tags = tuple(
            tag
            for tag in record.semantic_tags
            if tag.startswith("claim_dimension:")
        )
        if claim_dimension_tags != (expected_tag,):
            raise ValueError(
                "drs_supersession_evidence_invalid"
            ) from None
    reason = successor_record.supersession_reason
    if type(reason) is not str or not reason or len(reason) > 1024:
        raise ValueError("drs_supersession_evidence_invalid") from None
    expected_claim = _g2b_writeback_claim_preimage_v01(
        predecessor_record=predecessor_record,
        successor_commitment_record=successor_commitment_record,
        claim_dimension=claim_dimension,
        supersession_reason=reason,
    )
    proposal_id = expected_claim["writeback_proposal_id"]
    if type(proposal_id) is not str:
        raise ValueError("drs_writeback_root_binding_invalid") from None
    if (
        type(root_kernel) is not RootDecisionKernelV01
        or type(root_decision_input) is not RootDecisionInputV01
        or type(root_decision_result) is not RootDecisionResultV01
        or validate_root_decision_kernel_v01(root_kernel) != ()
        or validate_root_decision_input_v01(
            kernel=root_kernel,
            decision_input=root_decision_input,
        )
        != ()
        or validate_root_decision_result_v01(
            kernel=root_kernel,
            decision_input=root_decision_input,
            result=root_decision_result,
        )
        != ()
    ):
        raise ValueError("drs_writeback_root_binding_invalid") from None
    owner = predecessor_record.authority_envelope.owning_local_root_id
    root_plain = root_decision_input_to_plain_dict_v01(
        root_decision_input
    )
    claims = root_plain["root_review_packet"]["synthesis_proposal"][
        "normalized_claims"
    ]
    if (
        type(owner) is not str
        or not owner
        or root_decision_input.transaction_id != proposal_id
        or root_decision_result.transaction_id != proposal_id
        or root_decision_input.target_root_id != owner
        or root_decision_result.target_root_id != owner
        or root_decision_result.decision != ROOT_DECISION_ACCEPT
        or root_decision_result.reason_code
        != "validated_candidate_accepted"
        or root_decision_result.selected_candidate_id != proposal_id
        or root_decision_result.root_commit_created is not True
        or root_decision_result.permission_created is not False
        or root_decision_result.final_output_created is not False
        or root_decision_result.effect_requested is not False
        or type(claims) is not list
        or len(claims) != 1
        or claims[0].get("claim_id") != proposal_id
        or claims[0].get("subject")
        != predecessor_record.semantic_address.semantic_address_id
        or claims[0].get("predicate")
        != _G2B_WRITEBACK_PREDICATE_V01
        or claims[0].get("object_or_value") != expected_claim
        or claims[0].get("authority_class") != "NONE"
    ):
        raise ValueError("drs_writeback_root_binding_invalid") from None
    root_hash = _g2b_writeback_root_result_hash_v01(
        root_decision_result=root_decision_result
    )
    predecessor_authority = predecessor_record.authority_envelope
    successor_authority = successor_record.authority_envelope
    commitment_authority = (
        successor_commitment_record.authority_envelope
    )
    semantic_fields = (
        "semantic_address",
        "safe_summary",
        "semantic_tags",
        "resonance_reason",
        "memory_pointers",
        "artifact_pointers",
        "time_envelope",
        "persistent_lifecycle_state",
        "risk_hints",
        "conflict_hints",
        "reuse_policy_class",
        "policy_version",
        "schema_versions",
        "content_fingerprint",
    )
    edge = (
        successor_record.lineage_edges[0]
        if len(successor_record.lineage_edges) == 1
        else None
    )
    history_hash = _g2b_predecessor_history_hash_v01(
        predecessor_record
    )
    if (
        predecessor_record.persistent_lifecycle_state != "ACTIVE"
        or predecessor_authority.authority_class
        != "ROOT_ACCEPTED_WORK"
        or predecessor_authority.root_acceptance_state
        != "ACCEPTED_WORK"
        or predecessor_authority.action_permission_present is not False
        or predecessor_record.creates_authority is not False
        or predecessor_record.creates_permission is not False
        or successor_commitment_record.predecessor_record_id is not None
        or successor_commitment_record.supersession_reason is not None
        or successor_commitment_record.lineage_edges
        or commitment_authority.authority_class
        != "EVIDENCE_CANDIDATE"
        or commitment_authority.root_acceptance_state != "UNREVIEWED"
        or successor_record.persistent_lifecycle_state != "ACTIVE"
        or successor_authority.authority_class
        != "ROOT_ACCEPTED_WORK"
        or successor_authority.root_acceptance_state != "ACCEPTED_WORK"
        or successor_authority.owning_local_root_id != owner
        or successor_authority.source_root_decision_input_id
        != root_decision_input.decision_input_id
        or successor_authority.source_root_decision_id
        != root_decision_result.decision_id
        or successor_authority.source_root_decision_hash != root_hash
        or successor_record.creates_authority is not False
        or successor_record.creates_permission is not False
        or any(
            getattr(successor_record, name)
            != getattr(successor_commitment_record, name)
            for name in semantic_fields
        )
        or successor_record.predecessor_record_id
        != predecessor_record.meaning_record_id
        or edge is None
        or validate_lineage_edge_v01(edge) != (True, ())
        or edge.relation_class not in ("SUPERSEDES", "REPLACES")
        or edge.source_meaning_record_id
        != predecessor_record.meaning_record_id
        or edge.target_meaning_record_id
        != successor_commitment_record.meaning_record_id
        or edge.claim_dimension != claim_dimension
        or edge.source_history_hash != history_hash
        or edge.evidence_ref_ids != (proposal_id,)
        or edge.creates_authority is not False
        or edge.transfers_authority is not False
        or successor_record.source_reference_ids
        != successor_commitment_record.source_reference_ids
        + (proposal_id, edge.lineage_edge_id)
        or successor_record.semantic_address
        != predecessor_record.semantic_address
    ):
        raise ValueError("drs_supersession_evidence_invalid") from None
    predecessor_time = predecessor_record.time_envelope
    successor_time = successor_record.time_envelope
    if (
        successor_time.valid_from < predecessor_time.valid_from
        or successor_time.valid_from >= predecessor_time.valid_to
        or successor_time.valid_to <= successor_time.valid_from
        or successor_time.kt_as_of < predecessor_time.kt_as_of
        or successor_time.source_observed_at
        > successor_time.system_verified_at
        or successor_time.source_reported_at
        > successor_time.system_verified_at
        or successor_time.system_ingested_at
        > successor_time.system_verified_at
    ):
        raise ValueError("drs_supersession_evidence_invalid") from None
    return proposal_id, root_hash, edge


def _g2b_write_root_reviewed_meaning_record_v01(
    *,
    drs: LocalDRS,
    predecessor_record: MeaningRecordV01,
    successor_commitment_record: MeaningRecordV01,
    successor_record: MeaningRecordV01,
    claim_dimension: str,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
) -> dict[str, object]:
    if type(drs) is not LocalDRS:
        raise ValueError("drs_supersession_evidence_invalid") from None
    proposal_id, root_hash, edge = (
        _g2b_validate_root_reviewed_writeback_geometry_v01(
            predecessor_record=predecessor_record,
            successor_commitment_record=successor_commitment_record,
            successor_record=successor_record,
            claim_dimension=claim_dimension,
            root_kernel=root_kernel,
            root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
    )
    wrappers = _g2b_read_local_records_v01(
        drs=drs,
        layers=("work",),
    )
    predecessor_wrappers = tuple(
        wrapper
        for wrapper in wrappers
        if wrapper.get("record_id")
        == predecessor_record.meaning_record_id
    )
    if (
        len(predecessor_wrappers) != 1
        or not _g2b_wrapper_matches_v01(
            predecessor_wrappers[0], predecessor_record
        )
    ):
        raise ValueError("drs_supersession_evidence_invalid") from None
    predecessor_path = (
        drs.root_path
        / "work"
        / _safe_filename(predecessor_record.meaning_record_id)
    )
    successor_path = (
        drs.root_path
        / "work"
        / _safe_filename(successor_record.meaning_record_id)
    )
    if successor_path.exists():
        raise ValueError("drs_read_write_boundary_violation") from None
    predecessor_bytes = predecessor_path.read_bytes()
    predecessor_sha = hashlib.sha256(predecessor_bytes).hexdigest()
    wrapper = _g2b_storage_record_v01(
        meaning_record=successor_record,
        writeback_metadata={
            "writeback_proposal_id": proposal_id,
            "supersession_evidence_id": edge.lineage_edge_id,
            "root_decision_id": root_decision_result.decision_id,
            "root_result_binding_hash": root_hash,
        },
    )
    try:
        drs.write_record(wrapper)
        readback_bytes = successor_path.read_bytes()
        readback = json.loads(readback_bytes.decode("utf-8"))
        from hedgehog.drs_g2b_compatibility_v01 import (
            project_legacy_drs_source_v01,
            validate_legacy_drs_projection_v01,
        )

        projection = project_legacy_drs_source_v01(
            source_family="LOCAL_DRS_DICT",
            source=readback,
            target_semantic_address=successor_record.semantic_address,
            target_meaning_record=None,
        )
        if (
            validate_legacy_drs_projection_v01(projection)
            != (True, ())
            or projection.projection_status
            != "CANONICAL_CONTEXT_ONLY"
            or projection.target_meaning_record_id is not None
            or not _g2b_wrapper_matches_v01(readback, successor_record)
            or predecessor_path.read_bytes() != predecessor_bytes
        ):
            raise ValueError
    except Exception:
        try:
            if successor_path.exists():
                successor_path.unlink()
        except Exception:
            pass
        raise ValueError("drs_read_write_boundary_violation") from None
    successor_sha = hashlib.sha256(readback_bytes).hexdigest()
    return {
        "writeback_profile_version": "v0.1",
        "writeback_proposal_id": proposal_id,
        "claim_dimension": claim_dimension,
        "supersession_evidence_id": edge.lineage_edge_id,
        "predecessor_record_id": predecessor_record.meaning_record_id,
        "successor_commitment_record_id": (
            successor_commitment_record.meaning_record_id
        ),
        "successor_record_id": successor_record.meaning_record_id,
        "root_kernel_id": root_kernel.kernel_id,
        "root_decision_input_id": root_decision_input.decision_input_id,
        "root_decision_id": root_decision_result.decision_id,
        "root_result_binding_hash": root_hash,
        "predecessor_storage_sha256_before": predecessor_sha,
        "predecessor_storage_sha256_after": hashlib.sha256(
            predecessor_path.read_bytes()
        ).hexdigest(),
        "successor_storage_sha256": successor_sha,
        "predecessor_preserved": True,
        "successor_readback_exact": True,
        "records_written": 1,
        "creates_authority": False,
        "creates_permission": False,
        "real_world_effects_count": 0,
    }


def _g2b_action_request_reason_v01(value: object) -> str | None:
    if type(value) is not str:
        return "drs_action_intent_shortcut_forbidden"
    normalized = " ".join(
        re.sub(r"[^a-z0-9]+", " ", value.lower()).split()
    )
    profiles = (
        (
            "drs_payment_shortcut_forbidden",
            (
                "pay supplier",
                "send payment",
                "transfer funds",
                "authorize payment",
                "execute payment",
                "make bank transfer",
                "use payment reference",
                "authorize supplier payment",
            ),
        ),
        (
            "drs_shipment_shortcut_forbidden",
            ("release shipment", "dispatch shipment", "ship order"),
        ),
        (
            "drs_ticket_shortcut_forbidden",
            (
                "buy ticket",
                "purchase ticket",
                "book ticket",
                "issue ticket",
                "reserve seat",
            ),
        ),
        (
            "drs_action_packet_shortcut_forbidden",
            (
                "create actioncommitpacket",
                "issue actioncommitpacket",
                "generate action packet",
                "authorize action packet",
            ),
        ),
        (
            "drs_receipt_creation_shortcut_forbidden",
            ("create receipt", "issue receipt", "generate receipt"),
        ),
        (
            "drs_action_intent_shortcut_forbidden",
            (
                "execute maintenance",
                "execute maintenance action",
                "order replacement part",
                "perform external action",
            ),
        ),
    )
    for reason, phrases in profiles:
        if any(phrase in normalized for phrase in phrases):
            return reason
    return None
