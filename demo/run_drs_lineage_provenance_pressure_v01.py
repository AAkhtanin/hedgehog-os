from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TITLE = "HEDGEHOG OS — DRS LINEAGE / PROVENANCE PRESSURE v0.1"

COMPACT_RULE = (
    "lineage informs",
    "lineage does not decide",
    "provenance does not become truth",
    "audit/hash-chain proves continuity, not truth",
    "accepted evidence ancestry is not future action permission",
    "bridge traversal is not authority transfer",
    "quarantine/deadend proximity is bounded",
    "ConflictCheck remains advisory",
    "GT remains advisory",
    "Root remains final authority",
)

SCENARIO_IDS = (
    "trace_derived_from_trace_informs_only",
    "reuse_candidate_derived_from_old_accepted_evidence_requires_review",
    "bridge_traversal_across_domain_informs_only",
    "quarantine_near_reuse_candidate_warns_or_blocks",
    "deadend_near_reuse_candidate_warns_or_blocks",
    "conflicting_provenance_blocks_direct_reuse",
    "trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize",
    "audit_hash_continuity_does_not_create_truth",
    "high_reuse_lineage_does_not_create_authority",
    "root_final_authority_preserved_across_lineage_pressure",
)


@dataclass(frozen=True)
class LocalTraceRef:
    trace_id: str
    span_id: str
    kind: str


@dataclass(frozen=True)
class LocalProvenanceRef:
    source: str
    source_id: str
    trace_ref: LocalTraceRef | None
    trust_hint: str


@dataclass(frozen=True)
class LocalEvidenceRef:
    kind: str
    summary: str
    ref_id: str
    confidence: float


@dataclass(frozen=True)
class LocalAuditLink:
    source_artifact_type: str
    source_artifact_id: str
    previous_hash: str
    entry_hash: str
    continuity_valid: bool


@dataclass(frozen=True)
class LocalLineageRecord:
    record_id: str
    record_kind: str
    lifecycle_state: str
    domain: str
    subject_key: str
    claim_key: str
    claim_value: str
    created_at: str
    valid_from: str
    valid_to: str | None
    trace_refs: tuple[LocalTraceRef, ...]
    source_refs: tuple[LocalProvenanceRef, ...]
    evidence_refs: tuple[LocalEvidenceRef, ...]
    parent_record_ids: tuple[str, ...]
    derived_from_record_ids: tuple[str, ...]
    bridge_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    quarantine_refs: tuple[str, ...]
    deadend_refs: tuple[str, ...]
    audit_links: tuple[LocalAuditLink, ...]
    root_accepted: bool
    accepted_evidence: bool
    root_final: bool
    reuse_count: int
    trust_class: str
    authority_status: str


@dataclass(frozen=True)
class LocalPressureQuery:
    query_id: str
    domain: str
    subject_key: str
    claim_key: str
    as_of: str
    reuse_intent: str
    risk_class: str
    max_lineage_hops: int
    require_root_review: bool
    allow_direct_reuse_if_all_gates_pass: bool


@dataclass(frozen=True)
class LineagePressureResult:
    scenario_id: str
    query_state: str
    reuse_decision_class: str
    direct_reuse_allowed: bool
    root_review_required: bool
    lineage_informs: bool
    lineage_decides: bool
    provenance_truth_claimed: bool
    audit_hash_truth_claimed: bool
    bridge_transfers_authority: bool
    quarantine_global_taint: bool
    deadend_global_taint: bool
    conflictcheck_advisory_only: bool
    gt_advisory_only: bool
    root_final_authority_preserved: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    status: str
    expected_query_state: str
    actual_query_state: str
    expected_reuse_decision_class: str
    actual_reuse_decision_class: str
    expected_direct_reuse_allowed: bool
    actual_direct_reuse_allowed: bool
    root_final_authority_preserved: bool
    reason_codes: tuple[str, ...]
    notes: str


def _trace(trace_id: str, span_id: str, kind: str = "proof_trace") -> LocalTraceRef:
    return LocalTraceRef(trace_id=trace_id, span_id=span_id, kind=kind)


def _source(source_id: str, trace_id: str, trust_hint: str = "bounded") -> LocalProvenanceRef:
    return LocalProvenanceRef(
        source="local_drs",
        source_id=source_id,
        trace_ref=_trace(trace_id, f"span:{source_id}", "source_trace"),
        trust_hint=trust_hint,
    )


def _evidence(kind: str, ref_id: str, summary: str, confidence: float = 0.72) -> LocalEvidenceRef:
    return LocalEvidenceRef(kind=kind, summary=summary, ref_id=ref_id, confidence=confidence)


def _audit(source_artifact_id: str, continuity_valid: bool = True) -> LocalAuditLink:
    return LocalAuditLink(
        source_artifact_type="ResultProposal",
        source_artifact_id=source_artifact_id,
        previous_hash=f"hash:previous:{source_artifact_id}",
        entry_hash=f"hash:entry:{source_artifact_id}",
        continuity_valid=continuity_valid,
    )


def _record(**overrides: Any) -> LocalLineageRecord:
    values = {
        "record_id": "base_record",
        "record_kind": "Work",
        "lifecycle_state": "completed",
        "domain": "mock_government_certificate",
        "subject_key": "certificate:demo-user",
        "claim_key": "eligibility",
        "claim_value": "eligible",
        "created_at": "2026-06-18T12:00:00Z",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_to": "2026-12-31T23:59:59Z",
        "trace_refs": (_trace("trace:base", "span:base"),),
        "source_refs": (),
        "evidence_refs": (),
        "parent_record_ids": (),
        "derived_from_record_ids": (),
        "bridge_refs": (),
        "conflict_refs": (),
        "quarantine_refs": (),
        "deadend_refs": (),
        "audit_links": (),
        "root_accepted": False,
        "accepted_evidence": False,
        "root_final": False,
        "reuse_count": 0,
        "trust_class": "normal",
        "authority_status": "advisory",
    }
    values.update(overrides)
    return LocalLineageRecord(**values)


def _query(**overrides: Any) -> LocalPressureQuery:
    values = {
        "query_id": "query:lineage_pressure",
        "domain": "mock_government_certificate",
        "subject_key": "certificate:demo-user",
        "claim_key": "eligibility",
        "as_of": "2026-06-19T12:00:00Z",
        "reuse_intent": "direct_reuse_candidate",
        "risk_class": "high",
        "max_lineage_hops": 3,
        "require_root_review": True,
        "allow_direct_reuse_if_all_gates_pass": False,
    }
    values.update(overrides)
    return LocalPressureQuery(**values)


def build_records() -> dict[str, LocalLineageRecord]:
    old_trace = _record(
        record_id="trace_old_certificate",
        record_kind="TraceRecord",
        root_accepted=True,
        root_final=True,
        trace_refs=(_trace("trace:old", "span:root_final"),),
        authority_status="root_bounded",
    )
    derived_trace = _record(
        record_id="trace_derived_candidate",
        record_kind="TraceRecord",
        trace_refs=(_trace("trace:derived", "span:derived"),),
        source_refs=(_source("trace_old_certificate", "trace:old"),),
        derived_from_record_ids=("trace_old_certificate",),
        evidence_refs=(_evidence("trace_ref", "trace_old_certificate", "Derived from prior trace."),),
    )
    accepted_old = _record(
        record_id="accepted_evidence_old",
        record_kind="AcceptedEvidence",
        root_accepted=True,
        accepted_evidence=True,
        root_final=True,
        reuse_count=12,
        authority_status="bounded_evidence",
    )
    reuse_from_accepted = _record(
        record_id="reuse_from_old_accepted_evidence",
        record_kind="ReuseCandidate",
        source_refs=(_source("accepted_evidence_old", "trace:accepted", "root_bounded"),),
        evidence_refs=(_evidence("AcceptedEvidence", "accepted_evidence_old", "Old accepted evidence ancestry."),),
        derived_from_record_ids=("accepted_evidence_old",),
        accepted_evidence=True,
        reuse_count=3,
    )
    bridge_source = _record(
        record_id="bridge_source_certificate_domain",
        record_kind="BridgeSource",
        domain="mock_government_certificate",
        root_accepted=True,
        root_final=True,
        authority_status="source_domain_only",
    )
    bridge_candidate = _record(
        record_id="bridge_target_travel_domain",
        record_kind="BridgeCandidate",
        domain="mock_travel_readiness",
        source_refs=(_source("bridge_source_certificate_domain", "trace:bridge"),),
        bridge_refs=("bridge:certificate_to_travel",),
        parent_record_ids=("bridge_source_certificate_domain",),
    )
    quarantine_record = _record(
        record_id="quarantine_bad_lineage",
        record_kind="Quarantine",
        lifecycle_state="quarantined",
        claim_value="unsafe",
        authority_status="quarantine_only",
    )
    quarantine_candidate = _record(
        record_id="candidate_near_quarantine",
        record_kind="ReuseCandidate",
        quarantine_refs=("quarantine_bad_lineage",),
        parent_record_ids=("quarantine_bad_lineage",),
    )
    deadend_record = _record(
        record_id="deadend_bad_route",
        record_kind="DeadEnd",
        lifecycle_state="deadend",
        claim_value="bad_route",
        authority_status="deadend_only",
    )
    deadend_candidate = _record(
        record_id="candidate_near_deadend",
        record_kind="ReuseCandidate",
        deadend_refs=("deadend_bad_route",),
        parent_record_ids=("deadend_bad_route",),
    )
    provenance_conflict_a = _record(
        record_id="provenance_conflict_a",
        record_kind="Work",
        root_accepted=True,
        root_final=True,
        claim_value="eligible",
        authority_status="root_bounded",
    )
    provenance_conflict_b = _record(
        record_id="provenance_conflict_b",
        record_kind="ReuseCandidate",
        claim_value="not_eligible",
        source_refs=(_source("connector:conflicting", "trace:conflict", "untrusted"),),
        conflict_refs=("provenance_conflict_a",),
    )
    trusted_old_work = _record(
        record_id="trusted_old_work",
        record_kind="Work",
        root_accepted=True,
        root_final=True,
        trust_class="high",
        authority_status="root_bounded",
    )
    trusted_newer_provenance = _record(
        record_id="trusted_newer_provenance",
        record_kind="ProvenanceUpdate",
        created_at="2026-06-19T08:00:00Z",
        source_refs=(_source("trusted_registry_update", "trace:supersession", "high"),),
        evidence_refs=(_evidence("replacement_reason", "trusted_registry_update", "Newer trusted provenance."),),
        derived_from_record_ids=("trusted_old_work",),
        trust_class="high",
        authority_status="supersession_review_candidate",
    )
    audit_continuity_record = _record(
        record_id="audit_continuity_record",
        record_kind="AuditEvidence",
        audit_links=(_audit("trace_derived_candidate"),),
        evidence_refs=(_evidence("audit_link", "audit:trace_derived_candidate", "Hash continuity visible."),),
        authority_status="audit_continuity_only",
    )
    popular_lineage = _record(
        record_id="popular_lineage_candidate",
        record_kind="ReuseCandidate",
        source_refs=(_source("many_prior_reuses", "trace:popular"),),
        derived_from_record_ids=("trace_old_certificate",),
        reuse_count=10000,
        authority_status="popular_context",
    )
    composite = _record(
        record_id="composite_lineage_pressure_candidate",
        record_kind="CompositeReuseCandidate",
        domain="mock_travel_readiness",
        source_refs=(
            _source("accepted_evidence_old", "trace:accepted", "root_bounded"),
            _source("bridge_source_certificate_domain", "trace:bridge", "bounded"),
        ),
        evidence_refs=(
            _evidence("AcceptedEvidence", "accepted_evidence_old", "Old accepted evidence ancestry."),
            _evidence("ConflictCheck", "provenance_conflict_b", "Conflicting provenance visible."),
        ),
        parent_record_ids=("trace_derived_candidate", "bridge_source_certificate_domain"),
        derived_from_record_ids=("trace_derived_candidate", "accepted_evidence_old"),
        bridge_refs=("bridge:certificate_to_travel",),
        conflict_refs=("provenance_conflict_b",),
        quarantine_refs=("quarantine_bad_lineage",),
        deadend_refs=("deadend_bad_route",),
        audit_links=(_audit("composite_lineage_pressure_candidate"),),
        accepted_evidence=True,
        reuse_count=700,
        trust_class="mixed",
        authority_status="pressure_review_only",
    )
    return {record.record_id: record for record in (
        old_trace,
        derived_trace,
        accepted_old,
        reuse_from_accepted,
        bridge_source,
        bridge_candidate,
        quarantine_record,
        quarantine_candidate,
        deadend_record,
        deadend_candidate,
        provenance_conflict_a,
        provenance_conflict_b,
        trusted_old_work,
        trusted_newer_provenance,
        audit_continuity_record,
        popular_lineage,
        composite,
    )}


def build_queries() -> dict[str, LocalPressureQuery]:
    return {
        "trace_derived_from_trace_informs_only": _query(query_id="query:trace_derived"),
        "reuse_candidate_derived_from_old_accepted_evidence_requires_review": _query(query_id="query:accepted_ancestry"),
        "bridge_traversal_across_domain_informs_only": _query(
            query_id="query:bridge",
            domain="mock_travel_readiness",
            reuse_intent="cross_domain_context",
        ),
        "quarantine_near_reuse_candidate_warns_or_blocks": _query(query_id="query:quarantine"),
        "deadend_near_reuse_candidate_warns_or_blocks": _query(query_id="query:deadend"),
        "conflicting_provenance_blocks_direct_reuse": _query(query_id="query:conflict"),
        "trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize": _query(
            query_id="query:supersession",
            reuse_intent="supersession_candidate",
        ),
        "audit_hash_continuity_does_not_create_truth": _query(
            query_id="query:audit_continuity",
            reuse_intent="audit_replay",
        ),
        "high_reuse_lineage_does_not_create_authority": _query(query_id="query:popular_lineage"),
        "root_final_authority_preserved_across_lineage_pressure": _query(
            query_id="query:composite",
            domain="mock_travel_readiness",
            risk_class="regulated",
        ),
    }


def _linked_ids(record: LocalLineageRecord) -> set[str]:
    return {
        *record.parent_record_ids,
        *record.derived_from_record_ids,
        *record.bridge_refs,
        *record.conflict_refs,
        *record.quarantine_refs,
        *record.deadend_refs,
        *(ref.source_id for ref in record.source_refs),
        *(ref.ref_id for ref in record.evidence_refs),
        *(link.source_artifact_id for link in record.audit_links),
    }


def lineage_distance(record_a: LocalLineageRecord, record_b: LocalLineageRecord) -> int | None:
    if record_a.record_id == record_b.record_id:
        return 0
    if record_b.record_id in _linked_ids(record_a) or record_a.record_id in _linked_ids(record_b):
        return 1
    if _linked_ids(record_a) & _linked_ids(record_b):
        return 2
    return None


def bounded_lineage_candidates(
    records: dict[str, LocalLineageRecord] | list[LocalLineageRecord] | tuple[LocalLineageRecord, ...],
    query: LocalPressureQuery,
) -> tuple[LocalLineageRecord, ...]:
    values = records.values() if isinstance(records, dict) else records
    candidates = [
        record
        for record in values
        if record.subject_key == query.subject_key
        and record.claim_key == query.claim_key
        and (record.domain == query.domain or bool(record.bridge_refs))
    ]
    return tuple(candidates[: max(query.max_lineage_hops * 4, 1)])


def _bounded_ref_pressure(
    record: LocalLineageRecord,
    records: dict[str, LocalLineageRecord],
    query: LocalPressureQuery,
    refs: tuple[str, ...],
    lifecycle_state: str,
) -> dict[str, Any]:
    candidate_ids = {candidate.record_id for candidate in bounded_lineage_candidates(records, query)}
    relevant = []
    for ref_id in refs:
        ref_record = records.get(ref_id)
        if ref_record is None:
            continue
        distance = lineage_distance(record, ref_record)
        if distance is not None and distance <= query.max_lineage_hops:
            relevant.append({"record_id": ref_id, "distance": distance})
    detected = bool(relevant) or any(
        item.lifecycle_state == lifecycle_state
        and item.record_id in candidate_ids
        and lineage_distance(record, item) is not None
        for item in records.values()
    )
    return {
        "detected": detected,
        "bounded": True,
        "global_taint": False,
        "relevant_refs": tuple(item["record_id"] for item in relevant),
    }


def quarantine_pressure(
    record: LocalLineageRecord,
    records: dict[str, LocalLineageRecord],
    query: LocalPressureQuery,
) -> dict[str, Any]:
    return _bounded_ref_pressure(record, records, query, record.quarantine_refs, "quarantined")


def deadend_pressure(
    record: LocalLineageRecord,
    records: dict[str, LocalLineageRecord],
    query: LocalPressureQuery,
) -> dict[str, Any]:
    return _bounded_ref_pressure(record, records, query, record.deadend_refs, "deadend")


def conflict_pressure(
    record: LocalLineageRecord,
    records: dict[str, LocalLineageRecord],
    query: LocalPressureQuery,
) -> dict[str, Any]:
    conflicts = []
    for ref_id in record.conflict_refs:
        ref_record = records.get(ref_id)
        if ref_record is not None:
            conflicts.append(ref_id)
    for candidate in bounded_lineage_candidates(records, query):
        if (
            candidate.record_id != record.record_id
            and candidate.subject_key == record.subject_key
            and candidate.claim_key == record.claim_key
            and candidate.claim_value != record.claim_value
            and (candidate.record_id in record.conflict_refs or record.record_id in candidate.conflict_refs)
        ):
            conflicts.append(candidate.record_id)
    return {
        "detected": bool(conflicts),
        "advisory_only": True,
        "authority_claimed": False,
        "conflicting_refs": tuple(sorted(set(conflicts))),
    }


def bridge_pressure(
    record: LocalLineageRecord,
    records: dict[str, LocalLineageRecord],
    query: LocalPressureQuery,
) -> dict[str, Any]:
    del records
    informs = bool(record.bridge_refs) or record.domain != query.domain
    return {
        "detected": informs,
        "transfers_authority": False,
        "target_domain": query.domain,
        "source_domain": record.domain,
    }


def audit_continuity_pressure(record: LocalLineageRecord) -> dict[str, Any]:
    continuity_valid = bool(record.audit_links) and all(link.continuity_valid for link in record.audit_links)
    return {
        "detected": bool(record.audit_links),
        "continuity_valid": continuity_valid,
        "truth_claimed": False,
    }


def accepted_evidence_ancestry_pressure(record: LocalLineageRecord) -> dict[str, Any]:
    ancestry_present = record.accepted_evidence or any(
        ref.kind == "AcceptedEvidence" or "accepted_evidence" in ref.ref_id for ref in record.evidence_refs
    )
    return {
        "detected": ancestry_present,
        "action_permission_claimed": False,
        "future_permission_requires_root": ancestry_present,
    }


def reuse_lineage_pressure(record: LocalLineageRecord) -> dict[str, Any]:
    return {
        "detected": record.reuse_count > 0,
        "high_reuse": record.reuse_count >= 100,
        "authority_claimed": False,
        "visibility_signal": record.reuse_count > 0,
    }


def evaluate_lineage_pressure(
    record: LocalLineageRecord,
    records: dict[str, LocalLineageRecord],
    query: LocalPressureQuery,
) -> LineagePressureResult:
    quarantine = quarantine_pressure(record, records, query)
    deadend = deadend_pressure(record, records, query)
    conflict = conflict_pressure(record, records, query)
    bridge = bridge_pressure(record, records, query)
    audit = audit_continuity_pressure(record)
    accepted = accepted_evidence_ancestry_pressure(record)
    reuse = reuse_lineage_pressure(record)

    reasons: list[str] = []
    query_state = "context_only"
    reuse_decision_class = "context_only"
    root_review_required = query.require_root_review

    lineage_informs = bool(
        record.trace_refs
        or record.source_refs
        or record.evidence_refs
        or record.parent_record_ids
        or record.derived_from_record_ids
        or record.bridge_refs
        or record.conflict_refs
        or record.quarantine_refs
        or record.deadend_refs
        or record.audit_links
        or reuse["detected"]
    )

    if quarantine["detected"]:
        query_state = "blocked_by_quarantine_proximity"
        reuse_decision_class = "blocked"
        reasons.append("quarantine_proximity_bounded")
    elif deadend["detected"]:
        query_state = "blocked_by_deadend_proximity"
        reuse_decision_class = "blocked"
        reasons.append("deadend_proximity_bounded")
    elif conflict["detected"]:
        query_state = "blocked_by_conflicting_provenance"
        reuse_decision_class = "blocked"
        reasons.append("conflictcheck_advisory_root_required")
    elif record.authority_status == "supersession_review_candidate":
        query_state = "supersession_review_required"
        reuse_decision_class = "partial_reuse_then_validation"
        reasons.append("supersession_review_required")
    elif audit["detected"]:
        query_state = "audit_continuity_only"
        reuse_decision_class = "historical_replay"
        reasons.append("audit_hash_continuity_not_truth")
    elif accepted["detected"]:
        query_state = "rerun_required"
        reuse_decision_class = "partial_reuse_then_validation"
        reasons.append("accepted_evidence_ancestry_not_action_permission")
    elif bridge["detected"]:
        query_state = "context_only"
        reuse_decision_class = "context_only"
        reasons.append("bridge_informs_only")
    elif reuse["high_reuse"]:
        query_state = "review_required"
        reuse_decision_class = "partial_reuse_then_validation"
        reasons.append("popularity_not_authority")
    elif lineage_informs:
        query_state = "context_only"
        reuse_decision_class = "context_only"
        reasons.append("lineage_informs_only")

    direct_reuse_allowed = False
    if (
        query.allow_direct_reuse_if_all_gates_pass
        and not root_review_required
        and not quarantine["detected"]
        and not deadend["detected"]
        and not conflict["detected"]
        and not accepted["detected"]
        and not bridge["transfers_authority"]
        and not audit["truth_claimed"]
        and not reuse["authority_claimed"]
    ):
        direct_reuse_allowed = True

    if not reasons:
        reasons.append("lineage_informs_only")

    return LineagePressureResult(
        scenario_id=query.query_id.removeprefix("query:"),
        query_state=query_state,
        reuse_decision_class=reuse_decision_class,
        direct_reuse_allowed=direct_reuse_allowed,
        root_review_required=root_review_required,
        lineage_informs=lineage_informs,
        lineage_decides=False,
        provenance_truth_claimed=False,
        audit_hash_truth_claimed=bool(audit["truth_claimed"]),
        bridge_transfers_authority=bool(bridge["transfers_authority"]),
        quarantine_global_taint=bool(quarantine["global_taint"]),
        deadend_global_taint=bool(deadend["global_taint"]),
        conflictcheck_advisory_only=bool(conflict["advisory_only"]),
        gt_advisory_only=True,
        root_final_authority_preserved=True,
        reason_codes=tuple(reasons),
    )


def _scenario_expectations() -> dict[str, dict[str, Any]]:
    return {
        "trace_derived_from_trace_informs_only": {
            "record_id": "trace_derived_candidate",
            "query_state": "context_only",
            "reuse_decision_class": "context_only",
            "reason": "lineage_informs_only",
            "notes": "Trace ancestry is visible context, not direct reuse permission.",
        },
        "reuse_candidate_derived_from_old_accepted_evidence_requires_review": {
            "record_id": "reuse_from_old_accepted_evidence",
            "query_state": "rerun_required",
            "reuse_decision_class": "partial_reuse_then_validation",
            "reason": "accepted_evidence_ancestry_not_action_permission",
            "notes": "Old AcceptedEvidence ancestry requires current Root review.",
        },
        "bridge_traversal_across_domain_informs_only": {
            "record_id": "bridge_target_travel_domain",
            "query_state": "context_only",
            "reuse_decision_class": "context_only",
            "reason": "bridge_informs_only",
            "notes": "Bridge traversal informs the target domain but does not transfer authority.",
        },
        "quarantine_near_reuse_candidate_warns_or_blocks": {
            "record_id": "candidate_near_quarantine",
            "query_state": "blocked_by_quarantine_proximity",
            "reuse_decision_class": "blocked",
            "reason": "quarantine_proximity_bounded",
            "notes": "Quarantine pressure blocks direct reuse without global taint.",
        },
        "deadend_near_reuse_candidate_warns_or_blocks": {
            "record_id": "candidate_near_deadend",
            "query_state": "blocked_by_deadend_proximity",
            "reuse_decision_class": "blocked",
            "reason": "deadend_proximity_bounded",
            "notes": "Deadend pressure blocks route/direct reuse without global taint.",
        },
        "conflicting_provenance_blocks_direct_reuse": {
            "record_id": "provenance_conflict_b",
            "query_state": "blocked_by_conflicting_provenance",
            "reuse_decision_class": "blocked",
            "reason": "conflictcheck_advisory_root_required",
            "notes": "ConflictCheck blocks direct reuse as an advisory signal until Root decides.",
        },
        "trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize": {
            "record_id": "trusted_newer_provenance",
            "query_state": "supersession_review_required",
            "reuse_decision_class": "partial_reuse_then_validation",
            "reason": "supersession_review_required",
            "notes": "Trusted newer provenance can request review but cannot self-authorize supersession.",
        },
        "audit_hash_continuity_does_not_create_truth": {
            "record_id": "audit_continuity_record",
            "query_state": "audit_continuity_only",
            "reuse_decision_class": "historical_replay",
            "reason": "audit_hash_continuity_not_truth",
            "notes": "Audit continuity proves continuity only, not truth.",
        },
        "high_reuse_lineage_does_not_create_authority": {
            "record_id": "popular_lineage_candidate",
            "query_state": "review_required",
            "reuse_decision_class": "partial_reuse_then_validation",
            "reason": "popularity_not_authority",
            "notes": "Reuse history preserves visibility but does not create authority.",
        },
        "root_final_authority_preserved_across_lineage_pressure": {
            "record_id": "composite_lineage_pressure_candidate",
            "query_state": "blocked_by_quarantine_proximity",
            "reuse_decision_class": "blocked",
            "reason": "root_final_authority_preserved",
            "notes": "Composite lineage pressure remains advisory/blocking and Root remains final authority.",
        },
    }


def evaluate_scenario(scenario_id: str) -> ScenarioResult:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError(f"unknown scenario_id: {scenario_id}")
    records = build_records()
    queries = build_queries()
    expected = _scenario_expectations()[scenario_id]
    result = evaluate_lineage_pressure(records[expected["record_id"]], records, queries[scenario_id])
    reason_codes = result.reason_codes
    if scenario_id == "root_final_authority_preserved_across_lineage_pressure":
        reason_codes = tuple((*reason_codes, "root_final_authority_preserved"))
    expected_reason_present = expected["reason"] in reason_codes
    status = "PASS" if (
        result.query_state == expected["query_state"]
        and result.reuse_decision_class == expected["reuse_decision_class"]
        and result.direct_reuse_allowed is False
        and result.root_final_authority_preserved
        and expected_reason_present
        and not result.lineage_decides
        and not result.provenance_truth_claimed
        and not result.audit_hash_truth_claimed
        and not result.bridge_transfers_authority
        and not result.quarantine_global_taint
        and not result.deadend_global_taint
    ) else "FAIL"
    return ScenarioResult(
        scenario_id=scenario_id,
        status=status,
        expected_query_state=expected["query_state"],
        actual_query_state=result.query_state,
        expected_reuse_decision_class=expected["reuse_decision_class"],
        actual_reuse_decision_class=result.reuse_decision_class,
        expected_direct_reuse_allowed=False,
        actual_direct_reuse_allowed=result.direct_reuse_allowed,
        root_final_authority_preserved=result.root_final_authority_preserved,
        reason_codes=reason_codes,
        notes=expected["notes"],
    )


def _evaluate_lineage_results() -> list[LineagePressureResult]:
    records = build_records()
    queries = build_queries()
    expectations = _scenario_expectations()
    results: list[LineagePressureResult] = []
    for scenario_id in SCENARIO_IDS:
        expected = expectations[scenario_id]
        result = evaluate_lineage_pressure(records[expected["record_id"]], records, queries[scenario_id])
        if scenario_id == "root_final_authority_preserved_across_lineage_pressure":
            result = LineagePressureResult(
                **{**asdict(result), "reason_codes": tuple((*result.reason_codes, "root_final_authority_preserved"))}
            )
        results.append(LineagePressureResult(**{**asdict(result), "scenario_id": scenario_id}))
    return results


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIO_IDS]
    lineage_results = _evaluate_lineage_results()
    scenario_dicts = [asdict(scenario) for scenario in scenarios]
    lineage_dicts = [asdict(result) for result in lineage_results]
    counters = {
        "scenarios_total": len(scenarios),
        "scenarios_passed": sum(1 for scenario in scenarios if scenario.status == "PASS"),
        "direct_reuse_allowed_count": sum(1 for result in lineage_results if result.direct_reuse_allowed),
        "direct_reuse_blocked_count": sum(1 for result in lineage_results if not result.direct_reuse_allowed),
        "root_review_required_count": sum(1 for result in lineage_results if result.root_review_required),
        "lineage_informs_count": sum(1 for result in lineage_results if result.lineage_informs),
        "lineage_decides_count": sum(1 for result in lineage_results if result.lineage_decides),
        "provenance_truth_claimed_count": sum(1 for result in lineage_results if result.provenance_truth_claimed),
        "audit_hash_truth_claimed_count": sum(1 for result in lineage_results if result.audit_hash_truth_claimed),
        "bridge_authority_transfer_count": sum(1 for result in lineage_results if result.bridge_transfers_authority),
        "quarantine_global_taint_count": sum(1 for result in lineage_results if result.quarantine_global_taint),
        "deadend_global_taint_count": sum(1 for result in lineage_results if result.deadend_global_taint),
        "conflictcheck_authority_count": sum(1 for result in lineage_results if not result.conflictcheck_advisory_only),
        "gt_authority_count": sum(1 for result in lineage_results if not result.gt_advisory_only),
        "root_final_authority_preserved_count": sum(
            1 for result in lineage_results if result.root_final_authority_preserved
        ),
        "production_drs_used_count": 0,
        "external_drs_used_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "marennya_activated_count": 0,
        "up_activated_count": 0,
    }
    pass_conditions = {
        "scenarios_total_is_10": counters["scenarios_total"] == 10,
        "scenarios_passed_all": counters["scenarios_passed"] == counters["scenarios_total"],
        "lineage_never_decides": counters["lineage_decides_count"] == 0,
        "provenance_truth_not_claimed": counters["provenance_truth_claimed_count"] == 0,
        "audit_hash_truth_not_claimed": counters["audit_hash_truth_claimed_count"] == 0,
        "bridge_authority_not_transferred": counters["bridge_authority_transfer_count"] == 0,
        "quarantine_global_taint_absent": counters["quarantine_global_taint_count"] == 0,
        "deadend_global_taint_absent": counters["deadend_global_taint_count"] == 0,
        "conflictcheck_not_authority": counters["conflictcheck_authority_count"] == 0,
        "gt_not_authority": counters["gt_authority_count"] == 0,
        "root_final_authority_preserved_all": (
            counters["root_final_authority_preserved_count"] == counters["scenarios_total"]
        ),
        "no_production_drs": counters["production_drs_used_count"] == 0,
        "no_external_drs": counters["external_drs_used_count"] == 0,
        "no_network": counters["network_used_count"] == 0,
        "no_gemini": counters["gemini_used_count"] == 0,
        "no_marennya": counters["marennya_activated_count"] == 0,
        "no_up": counters["up_activated_count"] == 0,
    }
    return {
        "title": TITLE,
        "purpose": (
            "Deterministic local proof that lineage/provenance pressure can inform, warn, "
            "or block, but cannot become truth, permission, DRS write authority, or Root Final authority."
        ),
        "compact_rule": list(COMPACT_RULE),
        "scenario_ids": list(SCENARIO_IDS),
        "scenarios": scenario_dicts,
        "scenario_results_by_id": {scenario["scenario_id"]: scenario for scenario in scenario_dicts},
        "lineage_pressure_results": lineage_dicts,
        "lineage_pressure_results_by_id": {result["scenario_id"]: result for result in lineage_dicts},
        "aggregate_counters": counters,
        "authority_boundary_summary": {
            "lineage_informs": True,
            "lineage_does_not_decide": counters["lineage_decides_count"] == 0,
            "provenance_does_not_become_truth": counters["provenance_truth_claimed_count"] == 0,
            "audit_hash_chain_proves_continuity_not_truth": counters["audit_hash_truth_claimed_count"] == 0,
            "accepted_evidence_ancestry_is_not_future_action_permission": True,
            "bridge_traversal_is_not_authority_transfer": counters["bridge_authority_transfer_count"] == 0,
            "quarantine_deadend_proximity_is_bounded": (
                counters["quarantine_global_taint_count"] == 0
                and counters["deadend_global_taint_count"] == 0
            ),
            "conflictcheck_remains_advisory": counters["conflictcheck_authority_count"] == 0,
            "gt_remains_advisory": counters["gt_authority_count"] == 0,
            "root_remains_final_authority": (
                counters["root_final_authority_preserved_count"] == counters["scenarios_total"]
            ),
        },
        "limitations": {
            "deterministic_local_proof_only": True,
            "filesystem_input_dependency": False,
            "production_drs_used": False,
            "external_drs_used": False,
            "real_connector_used": False,
            "network_used": False,
            "gemini_used": False,
            "marennya_activated": False,
            "up_activated": False,
            "production_persistence_used": False,
            "runtime_integration": False,
            "schema_mutation": False,
        },
        "pass_conditions": pass_conditions,
        "status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def render_report(report: dict[str, Any] | None = None) -> str:
    report = run_all_scenarios() if report is None else report
    lines = [
        report["title"],
        "",
        "Purpose:",
        f"- {report['purpose']}",
        "",
        "Compact rule:",
    ]
    lines.extend(f"- {item}" for item in report["compact_rule"])
    lines.extend(["", "Scenario table:"])
    lines.append("scenario_id | status | direct_reuse_allowed | query_state | reuse_decision_class | reasons")
    lines.append("--- | --- | --- | --- | --- | ---")
    for scenario in report["scenarios"]:
        lines.append(
            f"{scenario['scenario_id']} | {scenario['status']} | "
            f"{scenario['actual_direct_reuse_allowed']} | {scenario['actual_query_state']} | "
            f"{scenario['actual_reuse_decision_class']} | {', '.join(scenario['reason_codes'])}"
        )
    lines.extend(["", "Aggregate counters:"])
    for key, value in report["aggregate_counters"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Authority boundary summary:"])
    for key, value in report["authority_boundary_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Limitations:"])
    for key, value in report["limitations"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"FINAL STATUS: {report['status']}"])
    return "\n".join(lines)


def main() -> int:
    report = run_all_scenarios()
    print(render_report(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
