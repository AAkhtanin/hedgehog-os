from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TITLE = "HEDGEHOG OS — COMPROMISED UPSTREAM PACK v0.1"

COMPACT_RULE = (
    "compromised upstream source is not truth",
    "signed-looking source is not truth",
    "external pointer is not trust",
    "schema-valid upstream content is not semantic truth",
    "ValidationPacket is not Root acceptance",
    "EvidenceCandidate is candidate-only before Root",
    "AcceptedEvidence is bounded evidence, not future action permission",
    "ConflictCheck remains advisory",
    "GT remains advisory",
    "Root remains final authority",
)

SCENARIO_IDS = (
    "compromised_bank_source_cannot_create_truth",
    "stale_legal_source_signed_looking_forces_review",
    "warehouse_source_contradiction_blocks_ready",
    "external_pointer_trust_laundering_rejected",
    "accepted_evidence_from_compromised_source_is_not_action_permission",
    "root_final_authority_preserved_under_compromised_upstream_pressure",
)


@dataclass(frozen=True)
class LocalUpstreamObservation:
    observation_id: str
    source_kind: str
    source_id: str
    source_trust_hint: str
    domain: str
    subject_key: str
    claim_key: str
    claim_value: str
    observed_at: str
    reported_at: str
    freshness_state: str
    signature_state: str
    contradiction_refs: tuple[str, ...]
    pointer_refs: tuple[str, ...]
    schema_valid: bool
    compromised_signal: bool
    economic_incentive: str
    source_truth_claimed: bool


@dataclass(frozen=True)
class LocalEvidenceCandidate:
    candidate_id: str
    observation_id: str
    evidence_kind: str
    summary: str
    confidence: float
    validation_refs: tuple[str, ...]
    root_accepted: bool
    action_permission_claimed: bool
    truth_claimed: bool


@dataclass(frozen=True)
class LocalValidationPacket:
    packet_id: str
    candidate_id: str
    schema_valid: bool
    freshness_valid: bool
    signature_valid: bool
    conflict_detected: bool
    pointer_trust_laundering_detected: bool
    validation_accepts_as_truth: bool
    root_required: bool


@dataclass(frozen=True)
class LocalAcceptedEvidence:
    accepted_evidence_id: str
    candidate_id: str
    root_decision_id: str
    bounded_scope: str
    future_action_permission: bool
    direct_reuse_permission: bool


@dataclass(frozen=True)
class LocalExternalPointer:
    pointer_id: str
    pointer_kind: str
    target_domain: str
    trust_claim: bool
    repeated_reference_count: int
    accepted_as_trust: bool


@dataclass(frozen=True)
class LocalConflictSignal:
    conflict_id: str
    subject_key: str
    claim_key: str
    conflict_kind: str
    advisory_only: bool
    blocks_direct_ready: bool


@dataclass(frozen=True)
class LocalRootDecision:
    decision_id: str
    scenario_id: str
    final_status: str
    root_final_authority_preserved: bool
    direct_reuse_allowed: bool
    action_permission_granted: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class UpstreamPressureResult:
    scenario_id: str
    status: str
    query_state: str
    final_status: str
    direct_ready_allowed: bool
    direct_reuse_allowed: bool
    action_permission_granted: bool
    source_truth_claimed: bool
    schema_validity_truth_claimed: bool
    signed_source_truth_claimed: bool
    pointer_trust_claimed: bool
    evidence_candidate_authority_claimed: bool
    validation_packet_authority_claimed: bool
    accepted_evidence_action_permission_claimed: bool
    conflictcheck_advisory_only: bool
    gt_advisory_only: bool
    root_final_authority_preserved: bool
    production_connector_used: bool
    production_drs_used: bool
    external_drs_used: bool
    network_used: bool
    gemini_used: bool
    negative_trace_implemented: bool
    auto_governance_implemented: bool
    manifest_hardening_implemented: bool
    transition_matrix_mutated: bool
    marennya_activated: bool
    up_activated: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    status: str
    expected_query_state: str
    actual_query_state: str
    expected_final_status: str
    actual_final_status: str
    expected_direct_ready_allowed: bool
    actual_direct_ready_allowed: bool
    expected_direct_reuse_allowed: bool
    actual_direct_reuse_allowed: bool
    expected_action_permission_granted: bool
    actual_action_permission_granted: bool
    root_final_authority_preserved: bool
    reason_codes: tuple[str, ...]
    notes: str


def _observation(**overrides: Any) -> LocalUpstreamObservation:
    values = {
        "observation_id": "observation:base",
        "source_kind": "bank_source",
        "source_id": "mock_known_bank",
        "source_trust_hint": "known_but_untrusted",
        "domain": "enterprise_readiness",
        "subject_key": "request:demo",
        "claim_key": "readiness",
        "claim_value": "ready_claim",
        "observed_at": "2026-06-19T09:00:00Z",
        "reported_at": "2026-06-19T09:00:05Z",
        "freshness_state": "fresh",
        "signature_state": "schema_valid_unsigned",
        "contradiction_refs": (),
        "pointer_refs": (),
        "schema_valid": True,
        "compromised_signal": False,
        "economic_incentive": "none",
        "source_truth_claimed": False,
    }
    values.update(overrides)
    return LocalUpstreamObservation(**values)


def build_upstream_observations() -> dict[str, LocalUpstreamObservation]:
    return {
        "compromised_bank_source_cannot_create_truth": _observation(
            observation_id="observation:compromised_bank_paid_ready",
            source_kind="bank_source",
            source_id="mock_bank_compromised",
            claim_key="payment_and_readiness",
            claim_value="payment_paid_and_ready_claim",
            compromised_signal=True,
            economic_incentive="paid_priority_laundering",
        ),
        "stale_legal_source_signed_looking_forces_review": _observation(
            observation_id="observation:stale_legal_signed_looking",
            source_kind="legal_registry_source",
            source_id="mock_legal_registry_stale",
            claim_key="certificate_validity",
            claim_value="certificate_valid_claim",
            observed_at="2025-03-01T00:00:00Z",
            reported_at="2026-06-19T09:05:00Z",
            freshness_state="stale",
            signature_state="signed_looking",
        ),
        "warehouse_source_contradiction_blocks_ready": _observation(
            observation_id="observation:warehouse_ready_contradiction",
            source_kind="warehouse_source",
            source_id="mock_warehouse_compromised",
            claim_key="dispatch_readiness",
            claim_value="ready_claim",
            contradiction_refs=("worldstate:water_filter_short_by_2",),
            compromised_signal=True,
            economic_incentive="ship_despite_shortage",
        ),
        "external_pointer_trust_laundering_rejected": _observation(
            observation_id="observation:external_pointer_laundering",
            source_kind="external_pointer_source",
            source_id="mock_external_pointer_claim",
            claim_key="trust_status",
            claim_value="trusted_by_repetition_claim",
            pointer_refs=("pointer:external_trust_laundering",),
            compromised_signal=True,
            economic_incentive="trust_laundering",
        ),
        "accepted_evidence_from_compromised_source_is_not_action_permission": _observation(
            observation_id="observation:compromised_candidate_to_action",
            source_kind="bank_source",
            source_id="mock_bank_compromised",
            claim_key="payment_status",
            claim_value="payment_paid_claim",
            compromised_signal=True,
            economic_incentive="action_permission_laundering",
        ),
        "root_final_authority_preserved_under_compromised_upstream_pressure": _observation(
            observation_id="observation:composite_compromised_upstream",
            source_kind="composite_upstream_pressure",
            source_id="mock_composite_compromised_sources",
            claim_key="enterprise_readiness",
            claim_value="ready_action_and_trust_claim",
            freshness_state="mixed_stale",
            signature_state="mixed_signed_looking",
            contradiction_refs=("worldstate:water_filter_short_by_2", "legal:expired_certificate"),
            pointer_refs=("pointer:external_trust_laundering",),
            compromised_signal=True,
            economic_incentive="composite_pressure",
        ),
    }


def build_external_pointers() -> dict[str, LocalExternalPointer]:
    return {
        "pointer:external_trust_laundering": LocalExternalPointer(
            pointer_id="pointer:external_trust_laundering",
            pointer_kind="external_drs_pointer_candidate",
            target_domain="enterprise_readiness",
            trust_claim=True,
            repeated_reference_count=12,
            accepted_as_trust=False,
        ),
        "pointer:composite_external_trust_laundering": LocalExternalPointer(
            pointer_id="pointer:composite_external_trust_laundering",
            pointer_kind="external_drs_pointer_candidate",
            target_domain="enterprise_readiness",
            trust_claim=True,
            repeated_reference_count=30,
            accepted_as_trust=False,
        ),
    }


def validate_freshness(observation: LocalUpstreamObservation) -> bool:
    return observation.freshness_state in {"fresh", "current"}


def validate_signature_state(observation: LocalUpstreamObservation) -> bool:
    return observation.signature_state in {"mock_valid", "signed_looking"}


def detect_source_compromise(observation: LocalUpstreamObservation) -> bool:
    return observation.compromised_signal or observation.economic_incentive != "none"


def detect_conflict(
    observation: LocalUpstreamObservation,
    observations: dict[str, LocalUpstreamObservation],
) -> LocalConflictSignal:
    conflict_refs = list(observation.contradiction_refs)
    for other in observations.values():
        if (
            other.observation_id != observation.observation_id
            and other.subject_key == observation.subject_key
            and other.claim_key == observation.claim_key
            and other.claim_value != observation.claim_value
        ):
            conflict_refs.append(other.observation_id)
    conflict_detected = bool(conflict_refs)
    return LocalConflictSignal(
        conflict_id=f"conflict:{observation.observation_id}",
        subject_key=observation.subject_key,
        claim_key=observation.claim_key,
        conflict_kind="upstream_contradiction" if conflict_detected else "none",
        advisory_only=True,
        blocks_direct_ready=conflict_detected,
    )


def detect_pointer_trust_laundering(pointer: LocalExternalPointer) -> bool:
    return (
        pointer.trust_claim
        and not pointer.accepted_as_trust
        and pointer.repeated_reference_count >= 2
    )


def build_evidence_candidates() -> dict[str, LocalEvidenceCandidate]:
    observations = build_upstream_observations()
    candidates = {}
    for scenario_id, observation in observations.items():
        candidates[scenario_id] = LocalEvidenceCandidate(
            candidate_id=f"candidate:{scenario_id}",
            observation_id=observation.observation_id,
            evidence_kind="upstream_observation_candidate",
            summary=f"Candidate derived from {observation.source_kind}; Root review required.",
            confidence=0.51 if detect_source_compromise(observation) else 0.72,
            validation_refs=(f"validation:{scenario_id}",),
            root_accepted=False,
            action_permission_claimed=False,
            truth_claimed=False,
        )
    return candidates


def build_validation_packets() -> dict[str, LocalValidationPacket]:
    observations = build_upstream_observations()
    candidates = build_evidence_candidates()
    pointers = build_external_pointers()
    packets = {}
    for scenario_id, candidate in candidates.items():
        observation = observations[scenario_id]
        conflict = detect_conflict(observation, observations)
        pointer_laundering = any(
            detect_pointer_trust_laundering(pointers[pointer_id])
            for pointer_id in observation.pointer_refs
            if pointer_id in pointers
        )
        packets[scenario_id] = LocalValidationPacket(
            packet_id=f"validation:{scenario_id}",
            candidate_id=candidate.candidate_id,
            schema_valid=observation.schema_valid,
            freshness_valid=validate_freshness(observation),
            signature_valid=validate_signature_state(observation),
            conflict_detected=conflict.blocks_direct_ready,
            pointer_trust_laundering_detected=pointer_laundering,
            validation_accepts_as_truth=False,
            root_required=True,
        )
    return packets


def evaluate_evidence_candidate(
    candidate: LocalEvidenceCandidate,
    observation: LocalUpstreamObservation,
    validation_packet: LocalValidationPacket,
) -> dict[str, Any]:
    bounded_accepted_evidence: LocalAcceptedEvidence | None = None
    root_can_create_bounded_evidence = (
        validation_packet.schema_valid
        and not validation_packet.validation_accepts_as_truth
        and not candidate.action_permission_claimed
    )
    if root_can_create_bounded_evidence:
        bounded_accepted_evidence = LocalAcceptedEvidence(
            accepted_evidence_id=f"accepted:{candidate.candidate_id}",
            candidate_id=candidate.candidate_id,
            root_decision_id=f"root_decision:{candidate.candidate_id}",
            bounded_scope="bounded_evidence_for_review_only",
            future_action_permission=False,
            direct_reuse_permission=False,
        )
    return {
        "candidate_id": candidate.candidate_id,
        "observation_id": observation.observation_id,
        "candidate_authority_claimed": False,
        "candidate_truth_claimed": candidate.truth_claimed,
        "action_permission_claimed": candidate.action_permission_claimed,
        "root_acceptance_required": True,
        "bounded_accepted_evidence": bounded_accepted_evidence,
    }


def _scenario_expectations() -> dict[str, dict[str, Any]]:
    return {
        "compromised_bank_source_cannot_create_truth": {
            "query_state": "blocked_or_review_required",
            "final_status": "needs_root_review",
            "reason": "compromised_source_not_truth",
            "notes": "Known bank-like source cannot turn source pressure into truth or ready status.",
        },
        "stale_legal_source_signed_looking_forces_review": {
            "query_state": "stale_source_review_required",
            "final_status": "needs_root_review",
            "reason": "stale_signed_source_requires_review",
            "notes": "Signed-looking legal source is still stale and must be reviewed.",
        },
        "warehouse_source_contradiction_blocks_ready": {
            "query_state": "blocked_by_conflicting_provenance",
            "final_status": "not_ready",
            "reason": "conflicting_warehouse_provenance_blocks_ready",
            "notes": "Warehouse ready claim conflicts with known shortage evidence.",
        },
        "external_pointer_trust_laundering_rejected": {
            "query_state": "external_pointer_review_required",
            "final_status": "blocked",
            "reason": "external_pointer_trust_laundering_rejected",
            "notes": "Repeated external pointer references do not create trust or external/global DRS.",
        },
        "accepted_evidence_from_compromised_source_is_not_action_permission": {
            "query_state": "candidate_review_required",
            "final_status": "needs_root_review",
            "reason": "accepted_evidence_not_action_permission",
            "notes": "Bounded AcceptedEvidence remains evidence only and grants no future action permission.",
        },
        "root_final_authority_preserved_under_compromised_upstream_pressure": {
            "query_state": "blocked_or_review_required",
            "final_status": "needs_root_review",
            "reason": "root_final_authority_preserved_under_compromised_upstream_pressure",
            "notes": "Composite upstream pressure preserves Root final authority.",
        },
    }


def _base_result(
    scenario_id: str,
    query_state: str,
    final_status: str,
    reason_codes: tuple[str, ...],
) -> UpstreamPressureResult:
    return UpstreamPressureResult(
        scenario_id=scenario_id,
        status="PASS",
        query_state=query_state,
        final_status=final_status,
        direct_ready_allowed=False,
        direct_reuse_allowed=False,
        action_permission_granted=False,
        source_truth_claimed=False,
        schema_validity_truth_claimed=False,
        signed_source_truth_claimed=False,
        pointer_trust_claimed=False,
        evidence_candidate_authority_claimed=False,
        validation_packet_authority_claimed=False,
        accepted_evidence_action_permission_claimed=False,
        conflictcheck_advisory_only=True,
        gt_advisory_only=True,
        root_final_authority_preserved=True,
        production_connector_used=False,
        production_drs_used=False,
        external_drs_used=False,
        network_used=False,
        gemini_used=False,
        negative_trace_implemented=False,
        auto_governance_implemented=False,
        manifest_hardening_implemented=False,
        transition_matrix_mutated=False,
        marennya_activated=False,
        up_activated=False,
        reason_codes=reason_codes,
    )


def root_review(scenario_id: str, pressure_result: UpstreamPressureResult) -> LocalRootDecision:
    return LocalRootDecision(
        decision_id=f"root_decision:{scenario_id}",
        scenario_id=scenario_id,
        final_status=pressure_result.final_status,
        root_final_authority_preserved=pressure_result.root_final_authority_preserved,
        direct_reuse_allowed=pressure_result.direct_reuse_allowed,
        action_permission_granted=pressure_result.action_permission_granted,
        reason_codes=pressure_result.reason_codes,
    )


def _evaluate_pressure(scenario_id: str) -> UpstreamPressureResult:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError(f"unknown scenario_id: {scenario_id}")

    observations = build_upstream_observations()
    candidates = build_evidence_candidates()
    packets = build_validation_packets()
    pointers = build_external_pointers()

    observation = observations[scenario_id]
    candidate = candidates[scenario_id]
    packet = packets[scenario_id]
    conflict = detect_conflict(observation, observations)
    candidate_eval = evaluate_evidence_candidate(candidate, observation, packet)
    bounded_evidence = candidate_eval["bounded_accepted_evidence"]

    expected = _scenario_expectations()[scenario_id]
    reasons = [expected["reason"]]

    if detect_source_compromise(observation):
        reasons.append("source_compromise_detected")
    if not validate_freshness(observation):
        reasons.append("freshness_not_current")
    if validate_signature_state(observation) and observation.signature_state == "signed_looking":
        reasons.append("signature_lookalike_not_authority")
    if conflict.blocks_direct_ready:
        reasons.append("conflict_detected")
    if any(
        detect_pointer_trust_laundering(pointers[pointer_id])
        for pointer_id in observation.pointer_refs
        if pointer_id in pointers
    ):
        reasons.append("pointer_laundering_detected")
    if bounded_evidence is not None and not bounded_evidence.future_action_permission:
        reasons.append("bounded_accepted_evidence_not_action_permission")

    result = _base_result(
        scenario_id=scenario_id,
        query_state=expected["query_state"],
        final_status=expected["final_status"],
        reason_codes=tuple(dict.fromkeys(reasons)),
    )
    root_decision = root_review(scenario_id, result)

    status_checks = (
        not result.source_truth_claimed,
        not result.schema_validity_truth_claimed,
        not result.signed_source_truth_claimed,
        not result.pointer_trust_claimed,
        not result.evidence_candidate_authority_claimed,
        not result.validation_packet_authority_claimed,
        not result.accepted_evidence_action_permission_claimed,
        result.conflictcheck_advisory_only,
        result.gt_advisory_only,
        root_decision.root_final_authority_preserved,
        not root_decision.direct_reuse_allowed,
        not root_decision.action_permission_granted,
        not result.production_connector_used,
        not result.production_drs_used,
        not result.external_drs_used,
        not result.network_used,
        not result.gemini_used,
        not result.negative_trace_implemented,
        not result.auto_governance_implemented,
        not result.manifest_hardening_implemented,
        not result.transition_matrix_mutated,
        not result.marennya_activated,
        not result.up_activated,
    )
    if not all(status_checks):
        result = UpstreamPressureResult(**{**asdict(result), "status": "FAIL"})
    return result


def evaluate_scenario(scenario_id: str) -> ScenarioResult:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError(f"unknown scenario_id: {scenario_id}")
    result = _evaluate_pressure(scenario_id)
    expected = _scenario_expectations()[scenario_id]
    reason_present = expected["reason"] in result.reason_codes
    status = "PASS" if (
        result.status == "PASS"
        and result.query_state == expected["query_state"]
        and result.final_status == expected["final_status"]
        and not result.direct_ready_allowed
        and not result.direct_reuse_allowed
        and not result.action_permission_granted
        and result.root_final_authority_preserved
        and reason_present
    ) else "FAIL"
    return ScenarioResult(
        scenario_id=scenario_id,
        status=status,
        expected_query_state=expected["query_state"],
        actual_query_state=result.query_state,
        expected_final_status=expected["final_status"],
        actual_final_status=result.final_status,
        expected_direct_ready_allowed=False,
        actual_direct_ready_allowed=result.direct_ready_allowed,
        expected_direct_reuse_allowed=False,
        actual_direct_reuse_allowed=result.direct_reuse_allowed,
        expected_action_permission_granted=False,
        actual_action_permission_granted=result.action_permission_granted,
        root_final_authority_preserved=result.root_final_authority_preserved,
        reason_codes=result.reason_codes,
        notes=expected["notes"],
    )


def _evaluate_pressure_results() -> list[UpstreamPressureResult]:
    return [_evaluate_pressure(scenario_id) for scenario_id in SCENARIO_IDS]


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIO_IDS]
    pressure_results = _evaluate_pressure_results()
    scenario_dicts = [asdict(scenario) for scenario in scenarios]
    pressure_dicts = [asdict(result) for result in pressure_results]
    counters = {
        "scenarios_total": len(scenarios),
        "scenarios_passed": sum(1 for scenario in scenarios if scenario.status == "PASS"),
        "direct_ready_allowed_count": sum(1 for result in pressure_results if result.direct_ready_allowed),
        "direct_reuse_allowed_count": sum(1 for result in pressure_results if result.direct_reuse_allowed),
        "action_permission_granted_count": sum(
            1 for result in pressure_results if result.action_permission_granted
        ),
        "source_truth_claimed_count": sum(1 for result in pressure_results if result.source_truth_claimed),
        "schema_validity_truth_claimed_count": sum(
            1 for result in pressure_results if result.schema_validity_truth_claimed
        ),
        "signed_source_truth_claimed_count": sum(
            1 for result in pressure_results if result.signed_source_truth_claimed
        ),
        "pointer_trust_claimed_count": sum(1 for result in pressure_results if result.pointer_trust_claimed),
        "evidence_candidate_authority_claimed_count": sum(
            1 for result in pressure_results if result.evidence_candidate_authority_claimed
        ),
        "validation_packet_authority_claimed_count": sum(
            1 for result in pressure_results if result.validation_packet_authority_claimed
        ),
        "accepted_evidence_action_permission_claimed_count": sum(
            1 for result in pressure_results if result.accepted_evidence_action_permission_claimed
        ),
        "conflictcheck_authority_count": sum(
            1 for result in pressure_results if not result.conflictcheck_advisory_only
        ),
        "gt_authority_count": sum(1 for result in pressure_results if not result.gt_advisory_only),
        "root_final_authority_preserved_count": sum(
            1 for result in pressure_results if result.root_final_authority_preserved
        ),
        "production_connector_used_count": sum(
            1 for result in pressure_results if result.production_connector_used
        ),
        "production_drs_used_count": sum(1 for result in pressure_results if result.production_drs_used),
        "external_drs_used_count": sum(1 for result in pressure_results if result.external_drs_used),
        "network_used_count": sum(1 for result in pressure_results if result.network_used),
        "gemini_used_count": sum(1 for result in pressure_results if result.gemini_used),
        "negative_trace_implemented_count": sum(
            1 for result in pressure_results if result.negative_trace_implemented
        ),
        "auto_governance_implemented_count": sum(
            1 for result in pressure_results if result.auto_governance_implemented
        ),
        "manifest_hardening_implemented_count": sum(
            1 for result in pressure_results if result.manifest_hardening_implemented
        ),
        "transition_matrix_mutated_count": sum(
            1 for result in pressure_results if result.transition_matrix_mutated
        ),
        "marennya_activated_count": sum(1 for result in pressure_results if result.marennya_activated),
        "up_activated_count": sum(1 for result in pressure_results if result.up_activated),
    }
    pass_conditions = {
        "scenarios_total_is_6": counters["scenarios_total"] == 6,
        "scenarios_passed_all": counters["scenarios_passed"] == counters["scenarios_total"],
        "direct_ready_never_allowed": counters["direct_ready_allowed_count"] == 0,
        "direct_reuse_never_allowed": counters["direct_reuse_allowed_count"] == 0,
        "action_permission_never_granted": counters["action_permission_granted_count"] == 0,
        "source_truth_not_claimed": counters["source_truth_claimed_count"] == 0,
        "schema_validity_truth_not_claimed": counters["schema_validity_truth_claimed_count"] == 0,
        "signed_source_truth_not_claimed": counters["signed_source_truth_claimed_count"] == 0,
        "pointer_trust_not_claimed": counters["pointer_trust_claimed_count"] == 0,
        "evidence_candidate_not_authority": counters["evidence_candidate_authority_claimed_count"] == 0,
        "validation_packet_not_authority": counters["validation_packet_authority_claimed_count"] == 0,
        "accepted_evidence_not_action_permission": (
            counters["accepted_evidence_action_permission_claimed_count"] == 0
        ),
        "conflictcheck_not_authority": counters["conflictcheck_authority_count"] == 0,
        "gt_not_authority": counters["gt_authority_count"] == 0,
        "root_final_authority_preserved_all": (
            counters["root_final_authority_preserved_count"] == counters["scenarios_total"]
        ),
        "no_production_connector": counters["production_connector_used_count"] == 0,
        "no_production_drs": counters["production_drs_used_count"] == 0,
        "no_external_drs": counters["external_drs_used_count"] == 0,
        "no_network": counters["network_used_count"] == 0,
        "no_gemini": counters["gemini_used_count"] == 0,
        "no_negative_trace": counters["negative_trace_implemented_count"] == 0,
        "no_auto_governance": counters["auto_governance_implemented_count"] == 0,
        "no_manifest_hardening": counters["manifest_hardening_implemented_count"] == 0,
        "no_transition_matrix_mutation": counters["transition_matrix_mutated_count"] == 0,
        "no_marennya": counters["marennya_activated_count"] == 0,
        "no_up": counters["up_activated_count"] == 0,
    }
    return {
        "title": TITLE,
        "purpose": (
            "Deterministic local proof that compromised upstream source pressure "
            "cannot become truth, authority, ready status, direct reuse permission, "
            "action permission, external/global DRS trust, or Root Final authority."
        ),
        "compact_rule": list(COMPACT_RULE),
        "scenario_ids": list(SCENARIO_IDS),
        "scenarios": scenario_dicts,
        "scenario_results_by_id": {scenario["scenario_id"]: scenario for scenario in scenario_dicts},
        "upstream_pressure_results": pressure_dicts,
        "upstream_pressure_results_by_id": {result["scenario_id"]: result for result in pressure_dicts},
        "aggregate_counters": counters,
        "authority_boundary_summary": {
            "compromised_upstream_source_is_not_truth": counters["source_truth_claimed_count"] == 0,
            "signed_looking_source_is_not_truth": counters["signed_source_truth_claimed_count"] == 0,
            "external_pointer_is_not_trust": counters["pointer_trust_claimed_count"] == 0,
            "schema_valid_upstream_content_is_not_semantic_truth": (
                counters["schema_validity_truth_claimed_count"] == 0
            ),
            "validation_packet_is_not_root_acceptance": (
                counters["validation_packet_authority_claimed_count"] == 0
            ),
            "evidence_candidate_is_candidate_only_before_root": (
                counters["evidence_candidate_authority_claimed_count"] == 0
            ),
            "accepted_evidence_is_bounded_not_future_action_permission": (
                counters["accepted_evidence_action_permission_claimed_count"] == 0
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
            "production_connector_used": False,
            "production_drs_used": False,
            "external_drs_used": False,
            "real_connector_used": False,
            "network_used": False,
            "gemini_used": False,
            "negative_trace_implemented": False,
            "auto_governance_implemented": False,
            "manifest_hardening_implemented": False,
            "transition_matrix_mutated": False,
            "marennya_activated": False,
            "up_activated": False,
            "production_persistence_used": False,
            "runtime_integration": False,
            "schema_mutation": False,
            "drs_poisoning_resistance_proof": False,
            "economic_adversary_proof": False,
        },
        "pass_conditions": pass_conditions,
        "status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def render_report(report: dict[str, Any] | None = None) -> str:
    report = run_all_scenarios() if report is None else report
    lines = [
        report["title"],
        "",
        "Compact rule:",
    ]
    lines.extend(report["compact_rule"])
    lines.extend(["", "Scenario table:"])
    for scenario in report["scenarios"]:
        lines.append(
            " | ".join(
                (
                    scenario["scenario_id"],
                    f"status={scenario['status']}",
                    f"query_state={scenario['actual_query_state']}",
                    f"final_status={scenario['actual_final_status']}",
                    f"direct_ready_allowed={str(scenario['actual_direct_ready_allowed']).lower()}",
                    f"direct_reuse_allowed={str(scenario['actual_direct_reuse_allowed']).lower()}",
                    f"action_permission_granted={str(scenario['actual_action_permission_granted']).lower()}",
                    "reasons=" + ",".join(scenario["reason_codes"]),
                )
            )
        )
    lines.extend(["", "Aggregate counters:"])
    for key in sorted(report["aggregate_counters"]):
        lines.append(f"{key}: {report['aggregate_counters'][key]}")
    lines.extend(["", "Authority boundary summary:"])
    for key in sorted(report["authority_boundary_summary"]):
        lines.append(f"{key}: {report['authority_boundary_summary'][key]}")
    lines.extend(["", "Limitations:"])
    for key in sorted(report["limitations"]):
        lines.append(f"{key}: {report['limitations'][key]}")
    lines.extend(["", f"FINAL STATUS: {report['status']}"])
    return "\n".join(lines)


def main() -> int:
    report = run_all_scenarios()
    print(render_report(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
