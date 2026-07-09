from __future__ import annotations

from dataclasses import dataclass, replace


STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_BLOCKED = "blocked"
STATUS_CONTEXT_ONLY = "context_only"
STATUS_INFORMATIONAL_DIRECT_REUSE_ALLOWED = (
    "direct_reuse_allowed_for_information_only"
)

DECISION_DIRECT_REUSE_ALLOWED_FOR_INFORMATION_ONLY = (
    "direct_reuse_allowed_for_information_only"
)
DECISION_ACTION_REUSE_BLOCKED = "action_reuse_blocked"
DECISION_CONTEXT_ONLY = "context_only"
DECISION_RERUN_REQUIRED = "rerun_required"
DECISION_BLOCKED = "blocked"

CANDIDATE_INFORMATIONAL_POLICY_SUMMARY_DIRECT_REUSE = (
    "informational_policy_summary_direct_reuse"
)
CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION = (
    "same_policy_record_as_payment_permission"
)
CANDIDATE_SAME_POLICY_RECORD_AS_SHIPMENT_RELEASE = (
    "same_policy_record_as_shipment_release"
)
CANDIDATE_SAME_POLICY_RECORD_AS_TICKET_PURCHASE = (
    "same_policy_record_as_ticket_purchase"
)
CANDIDATE_STALE_POLICY_SUMMARY_CONTEXT_ONLY = (
    "stale_policy_summary_context_only"
)
CANDIDATE_QUARANTINE_NEAR_POLICY_SUMMARY_BLOCKED = (
    "quarantine_near_policy_summary_blocked"
)
CANDIDATE_HIGH_SCORE_WITHOUT_ROOT_SHORTCUT = (
    "high_score_without_root_shortcut"
)

REASON_OLD_MEMORY_CAN_HELP_BUT_CANNOT_ACT = (
    "old_memory_can_help_but_cannot_act"
)
REASON_INFORMATIONAL_ANSWER_ONLY = "informational_answer_only"
REASON_NO_ACTION_PERMISSION = "no_action_permission"
REASON_NO_PAYMENT_PERMISSION = "no_payment_permission"
REASON_NO_SHIPMENT_PERMISSION = "no_shipment_permission"
REASON_NO_TICKET_PERMISSION = "no_ticket_permission"
REASON_ROOT_SHORTCUT_REQUIRED = "root_shortcut_required"
REASON_ROOT_SHORTCUT_ALLOWED = "root_shortcut_allowed"
REASON_ROOT_FINAL_FROM_REUSE_CREATED = "root_final_from_reuse_created"
REASON_ACTION_REUSE_BLOCKED = "action_reuse_blocked"
REASON_ACTION_INTENT_BLOCKS_DIRECT_REUSE = (
    "action_intent_blocks_direct_reuse"
)
REASON_EXTERNAL_EFFECT_REQUEST_BLOCKS_DIRECT_REUSE = (
    "external_effect_request_blocks_direct_reuse"
)
REASON_TEMPORAL_HARD_GATE_FAILED = "temporal_hard_gate_failed"
REASON_POLICY_GATE_FAILED = "policy_gate_failed"
REASON_CONFLICT_GATE_FAILED = "conflict_gate_failed"
REASON_QUARANTINE_GATE_FAILED = "quarantine_gate_failed"
REASON_DEADEND_GATE_FAILED = "deadend_gate_failed"
REASON_GT_TRUST_GATE_FAILED = "gt_trust_gate_failed"
REASON_REUSE_SCORE_BELOW_THRESHOLD = "reuse_score_below_threshold"
REASON_REUSE_SCORE_NOT_AUTHORITY = "reuse_score_not_authority"
REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY = (
    "semantic_similarity_not_authority"
)
REASON_DRS_HIT_NOT_TRUTH = "drs_hit_not_truth"
REASON_OLD_RECEIPT_NOT_PERMISSION = "old_receipt_not_permission"
REASON_OLD_QUOTE_NOT_TICKET_PERMISSION = "old_quote_not_ticket_permission"
REASON_OLD_TICKET_RECEIPT_NOT_FUTURE_PERMISSION = (
    "old_ticket_receipt_not_future_permission"
)
REASON_ROOT_REMAINS_FINAL_AUTHORITY = "root_remains_final_authority"

FORMULA_DIRECT_REUSE_ALLOWED_NON_ACTION = (
    "DirectReuseAllowed_non_action = RootShortcutAllowed "
    "and TemporalHardGate and PolicyOK and ConflictOK and QuarantineOK "
    "and DeadEndOK and GTTrustOK and ReuseScore >= threshold "
    "and ActionIntent = false and ExternalEffectRequested = false"
)
FORMULA_ACTION_PATHS = (
    "DirectReuseAllowed_payment = false",
    "DirectReuseAllowed_shipment_release = false",
    "DirectReuseAllowed_ticket_purchase = false",
    "DirectReuseAllowed_action_commit_packet = false",
)


@dataclass(frozen=True)
class NonActionDirectReuseRecordV01:
    record_id: str
    record_kind: str
    root_approved: bool
    informational_summary: str
    freshness_class: str
    has_time_envelope: bool
    temporal_query_present: bool
    policy_ok: bool
    conflict_ok: bool
    quarantine_ok: bool
    deadend_ok: bool
    gt_trust_ok: bool
    reuse_score: float
    semantic_similarity_score: float
    contains_receipt: bool = False
    contains_quote: bool = False
    contains_ticket_receipt: bool = False
    creates_permission: bool = False
    creates_action_commit_packet: bool = False
    creates_receipt: bool = False
    executes_payment: bool = False
    releases_shipment: bool = False
    issues_ticket: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class NonActionReuseRequestV01:
    request_id: str
    request_text: str
    requested_output_kind: str
    action_intent: bool
    external_effect_requested: bool
    asks_payment_permission: bool = False
    asks_shipment_release: bool = False
    asks_ticket_purchase: bool = False
    asks_action_commit_packet: bool = False
    asks_receipt_creation: bool = False
    asks_final_output: bool = False


@dataclass(frozen=True)
class RootShortcutGateV01:
    root_shortcut_allowed: bool
    root_shortcut_required: bool
    root_review_required: bool
    reason_codes: tuple[str, ...]
    root_is_final_authority: bool = True
    gate_is_authority: bool = False
    gate_creates_answer: bool = False
    gate_creates_permission: bool = False
    gate_creates_action_commit_packet: bool = False
    gate_creates_receipt: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class NonActionReuseDecisionV01:
    scenario_id: str
    candidate_class: str
    decision_class: str
    direct_reuse_allowed: bool
    direct_reuse_allowed_for_information_only: bool
    action_reuse_blocked: bool
    root_shortcut_allowed: bool
    root_final_from_reuse_created: bool
    architect_skipped: bool
    executor_skipped: bool
    heavy_pipeline_skipped: bool
    root_review_required: bool
    reason_codes: tuple[str, ...]
    drs_is_authority: bool = False
    avf_is_authority: bool = False
    reuse_gate_is_authority: bool = False
    reuse_score_is_authority: bool = False
    semantic_similarity_is_authority: bool = False
    informational_answer_is_permission: bool = False
    action_permission_granted: bool = False
    payment_permission_created: bool = False
    shipment_permission_created: bool = False
    ticket_permission_created: bool = False
    action_commit_packet_created: bool = False
    receipt_created: bool = False
    payment_executed: bool = False
    shipment_released: bool = False
    ticket_issued: bool = False
    provider_called: bool = False
    network_called: bool = False
    gemini_called: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class NonActionInformationalReuseArtifactV01:
    artifact_id: str
    source_record_id: str
    request_id: str
    informational_answer: str
    created_by: str
    root_created: bool
    direct_reuse_allowed_for_information_only: bool
    root_shortcut_allowed: bool
    action_permission_granted: bool = False
    payment_permission_created: bool = False
    shipment_permission_created: bool = False
    ticket_permission_created: bool = False
    action_commit_packet_created: bool = False
    receipt_created: bool = False
    payment_executed: bool = False
    shipment_released: bool = False
    ticket_issued: bool = False
    final_output_created: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class NonActionDirectReuseReportV01:
    report_id: str
    final_status: str
    scenarios_total: int
    scenarios_passed: int
    positive_control: dict[str, object]
    negative_controls: dict[str, object]
    decisions: tuple[NonActionReuseDecisionV01, ...]
    informational_artifacts: tuple[NonActionInformationalReuseArtifactV01, ...]
    counters: dict[str, int]
    validation_errors: tuple[str, ...]


def build_fresh_root_approved_policy_summary_record_v01() -> (
    NonActionDirectReuseRecordV01
):
    return NonActionDirectReuseRecordV01(
        record_id="non_action_policy_summary:full_wow_v1_2:sh_2042",
        record_kind="root_approved_informational_policy_summary",
        root_approved=True,
        informational_summary=(
            "Supplier B remains blocked, shipment SH-2042 remains held, "
            "and Supplier A mock receipt is evidence only."
        ),
        freshness_class="fresh",
        has_time_envelope=True,
        temporal_query_present=True,
        policy_ok=True,
        conflict_ok=True,
        quarantine_ok=True,
        deadend_ok=True,
        gt_trust_ok=True,
        reuse_score=0.93,
        semantic_similarity_score=0.91,
        contains_receipt=True,
    )


def build_non_action_reuse_request_v01() -> NonActionReuseRequestV01:
    return NonActionReuseRequestV01(
        request_id="request:remind_policy_summary:sh_2042",
        request_text=(
            "Remind me what the current policy summary says about "
            "Supplier B and shipment SH-2042."
        ),
        requested_output_kind="informational_answer",
        action_intent=False,
        external_effect_requested=False,
    )


def build_action_like_reuse_requests_v01() -> tuple[NonActionReuseRequestV01, ...]:
    return (
        NonActionReuseRequestV01(
            request_id="request:supplier_b_payment_permission",
            request_text="Use the old policy summary to permit Supplier B payment.",
            requested_output_kind="payment_permission",
            action_intent=True,
            external_effect_requested=True,
            asks_payment_permission=True,
        ),
        NonActionReuseRequestV01(
            request_id="request:shipment_release",
            request_text="Use the old policy summary to release shipment SH-2042.",
            requested_output_kind="shipment_release",
            action_intent=True,
            external_effect_requested=True,
            asks_shipment_release=True,
        ),
        NonActionReuseRequestV01(
            request_id="request:ticket_purchase",
            request_text="Use old travel memory to buy the ticket.",
            requested_output_kind="ticket_purchase",
            action_intent=True,
            external_effect_requested=True,
            asks_ticket_purchase=True,
        ),
        NonActionReuseRequestV01(
            request_id="request:action_commit_packet",
            request_text="Create an ActionCommitPacket from the old summary.",
            requested_output_kind="action_commit_packet",
            action_intent=True,
            external_effect_requested=False,
            asks_action_commit_packet=True,
        ),
        NonActionReuseRequestV01(
            request_id="request:receipt_creation",
            request_text="Create a receipt from the old summary.",
            requested_output_kind="receipt_creation",
            action_intent=True,
            external_effect_requested=False,
            asks_receipt_creation=True,
        ),
    )


def evaluate_root_shortcut_gate_v01(
    record: NonActionDirectReuseRecordV01,
    request: NonActionReuseRequestV01,
    *,
    reuse_score_threshold: float = 0.80,
) -> RootShortcutGateV01:
    reasons: tuple[str, ...] = (
        REASON_ROOT_SHORTCUT_REQUIRED,
        REASON_ROOT_REMAINS_FINAL_AUTHORITY,
        REASON_DRS_HIT_NOT_TRUTH,
        REASON_REUSE_SCORE_NOT_AUTHORITY,
        REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY,
    )

    if record.contains_receipt:
        reasons = _with_reason(reasons, REASON_OLD_RECEIPT_NOT_PERMISSION)
    if record.contains_quote:
        reasons = _with_reason(reasons, REASON_OLD_QUOTE_NOT_TICKET_PERMISSION)
    if record.contains_ticket_receipt:
        reasons = _with_reason(
            reasons,
            REASON_OLD_TICKET_RECEIPT_NOT_FUTURE_PERMISSION,
        )
    if not record.root_approved:
        reasons = _with_reason(reasons, REASON_ROOT_SHORTCUT_REQUIRED)
    if (
        not record.has_time_envelope
        or not record.temporal_query_present
        or record.freshness_class != "fresh"
    ):
        reasons = _with_reason(reasons, REASON_TEMPORAL_HARD_GATE_FAILED)
    if not record.policy_ok:
        reasons = _with_reason(reasons, REASON_POLICY_GATE_FAILED)
    if not record.conflict_ok:
        reasons = _with_reason(reasons, REASON_CONFLICT_GATE_FAILED)
    if not record.quarantine_ok:
        reasons = _with_reason(reasons, REASON_QUARANTINE_GATE_FAILED)
    if not record.deadend_ok:
        reasons = _with_reason(reasons, REASON_DEADEND_GATE_FAILED)
    if not record.gt_trust_ok:
        reasons = _with_reason(reasons, REASON_GT_TRUST_GATE_FAILED)
    if record.reuse_score < reuse_score_threshold:
        reasons = _with_reason(reasons, REASON_REUSE_SCORE_BELOW_THRESHOLD)
    if _request_is_action_like(request):
        reasons = _with_reason(
            reasons,
            REASON_ACTION_INTENT_BLOCKS_DIRECT_REUSE,
        )
    if request.external_effect_requested or _record_claims_effect(record):
        reasons = _with_reason(
            reasons,
            REASON_EXTERNAL_EFFECT_REQUEST_BLOCKS_DIRECT_REUSE,
        )

    root_shortcut_allowed = (
        record.root_approved
        and record.has_time_envelope
        and record.temporal_query_present
        and record.freshness_class == "fresh"
        and record.policy_ok
        and record.conflict_ok
        and record.quarantine_ok
        and record.deadend_ok
        and record.gt_trust_ok
        and record.reuse_score >= reuse_score_threshold
        and not _request_is_action_like(request)
        and not request.external_effect_requested
        and not _record_claims_effect(record)
    )
    if root_shortcut_allowed:
        reasons = _with_reason(reasons, REASON_ROOT_SHORTCUT_ALLOWED)

    return RootShortcutGateV01(
        root_shortcut_allowed=root_shortcut_allowed,
        root_shortcut_required=True,
        root_review_required=not root_shortcut_allowed,
        reason_codes=reasons,
    )


def evaluate_non_action_reuse_decision_v01(
    scenario_id: str,
    candidate_class: str,
    record: NonActionDirectReuseRecordV01,
    request: NonActionReuseRequestV01,
    *,
    reuse_score_threshold: float = 0.80,
) -> NonActionReuseDecisionV01:
    gate = evaluate_root_shortcut_gate_v01(
        record,
        request,
        reuse_score_threshold=reuse_score_threshold,
    )
    reasons = _base_decision_reasons(gate.reason_codes)

    if gate.root_shortcut_allowed:
        reasons = _with_reasons(
            reasons,
            (
                REASON_OLD_MEMORY_CAN_HELP_BUT_CANNOT_ACT,
                REASON_INFORMATIONAL_ANSWER_ONLY,
                REASON_ROOT_FINAL_FROM_REUSE_CREATED,
                REASON_NO_ACTION_PERMISSION,
                REASON_NO_PAYMENT_PERMISSION,
                REASON_NO_SHIPMENT_PERMISSION,
                REASON_NO_TICKET_PERMISSION,
            ),
        )
        return NonActionReuseDecisionV01(
            scenario_id=scenario_id,
            candidate_class=candidate_class,
            decision_class=DECISION_DIRECT_REUSE_ALLOWED_FOR_INFORMATION_ONLY,
            direct_reuse_allowed=True,
            direct_reuse_allowed_for_information_only=True,
            action_reuse_blocked=False,
            root_shortcut_allowed=True,
            root_final_from_reuse_created=True,
            architect_skipped=True,
            executor_skipped=True,
            heavy_pipeline_skipped=True,
            root_review_required=False,
            reason_codes=reasons,
        )

    if _request_is_action_like(request):
        reasons = _action_block_reasons(reasons, request)
        return NonActionReuseDecisionV01(
            scenario_id=scenario_id,
            candidate_class=candidate_class,
            decision_class=DECISION_ACTION_REUSE_BLOCKED,
            direct_reuse_allowed=False,
            direct_reuse_allowed_for_information_only=False,
            action_reuse_blocked=True,
            root_shortcut_allowed=False,
            root_final_from_reuse_created=False,
            architect_skipped=False,
            executor_skipped=False,
            heavy_pipeline_skipped=False,
            root_review_required=True,
            reason_codes=reasons,
        )

    if record.freshness_class != "fresh" or not record.has_time_envelope:
        return NonActionReuseDecisionV01(
            scenario_id=scenario_id,
            candidate_class=candidate_class,
            decision_class=DECISION_CONTEXT_ONLY,
            direct_reuse_allowed=False,
            direct_reuse_allowed_for_information_only=False,
            action_reuse_blocked=False,
            root_shortcut_allowed=False,
            root_final_from_reuse_created=False,
            architect_skipped=False,
            executor_skipped=False,
            heavy_pipeline_skipped=False,
            root_review_required=True,
            reason_codes=_with_reason(reasons, REASON_TEMPORAL_HARD_GATE_FAILED),
        )

    if not record.quarantine_ok or not record.deadend_ok:
        reason = (
            REASON_QUARANTINE_GATE_FAILED
            if not record.quarantine_ok
            else REASON_DEADEND_GATE_FAILED
        )
        return NonActionReuseDecisionV01(
            scenario_id=scenario_id,
            candidate_class=candidate_class,
            decision_class=DECISION_BLOCKED,
            direct_reuse_allowed=False,
            direct_reuse_allowed_for_information_only=False,
            action_reuse_blocked=False,
            root_shortcut_allowed=False,
            root_final_from_reuse_created=False,
            architect_skipped=False,
            executor_skipped=False,
            heavy_pipeline_skipped=False,
            root_review_required=True,
            reason_codes=_with_reason(reasons, reason),
        )

    return NonActionReuseDecisionV01(
        scenario_id=scenario_id,
        candidate_class=candidate_class,
        decision_class=DECISION_BLOCKED,
        direct_reuse_allowed=False,
        direct_reuse_allowed_for_information_only=False,
        action_reuse_blocked=False,
        root_shortcut_allowed=False,
        root_final_from_reuse_created=False,
        architect_skipped=False,
        executor_skipped=False,
        heavy_pipeline_skipped=False,
        root_review_required=True,
        reason_codes=_with_reasons(
            reasons,
            (
                REASON_ROOT_SHORTCUT_REQUIRED,
                REASON_REUSE_SCORE_NOT_AUTHORITY,
                REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY,
            ),
        ),
    )


def create_root_informational_reuse_artifact_v01(
    decision: NonActionReuseDecisionV01,
    record: NonActionDirectReuseRecordV01,
    request: NonActionReuseRequestV01,
) -> NonActionInformationalReuseArtifactV01 | None:
    if not decision.direct_reuse_allowed_for_information_only:
        return None
    return NonActionInformationalReuseArtifactV01(
        artifact_id=f"artifact:{decision.scenario_id}:root_informational_reuse",
        source_record_id=record.record_id,
        request_id=request.request_id,
        informational_answer=record.informational_summary,
        created_by="root",
        root_created=True,
        direct_reuse_allowed_for_information_only=True,
        root_shortcut_allowed=decision.root_shortcut_allowed,
    )


def build_non_action_direct_reuse_positive_control_report_v01() -> (
    NonActionDirectReuseReportV01
):
    record = build_fresh_root_approved_policy_summary_record_v01()
    info_request = build_non_action_reuse_request_v01()
    payment_request, shipment_request, ticket_request, _, _ = (
        build_action_like_reuse_requests_v01()
    )
    stale_record = replace(
        record,
        record_id="non_action_policy_summary:stale:sh_2042",
        freshness_class="stale",
    )
    high_score_without_root = replace(
        record,
        record_id="non_action_policy_summary:high_score_without_root:sh_2042",
        root_approved=False,
        reuse_score=0.99,
        semantic_similarity_score=0.99,
    )

    scenario_inputs = (
        (
            "scenario:informational_policy_summary_direct_reuse",
            CANDIDATE_INFORMATIONAL_POLICY_SUMMARY_DIRECT_REUSE,
            record,
            info_request,
        ),
        (
            "scenario:same_policy_record_as_payment_permission",
            CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION,
            record,
            payment_request,
        ),
        (
            "scenario:same_policy_record_as_shipment_release",
            CANDIDATE_SAME_POLICY_RECORD_AS_SHIPMENT_RELEASE,
            record,
            shipment_request,
        ),
        (
            "scenario:same_policy_record_as_ticket_purchase",
            CANDIDATE_SAME_POLICY_RECORD_AS_TICKET_PURCHASE,
            record,
            ticket_request,
        ),
        (
            "scenario:stale_policy_summary_context_only",
            CANDIDATE_STALE_POLICY_SUMMARY_CONTEXT_ONLY,
            stale_record,
            info_request,
        ),
        (
            "scenario:high_score_without_root_shortcut",
            CANDIDATE_HIGH_SCORE_WITHOUT_ROOT_SHORTCUT,
            high_score_without_root,
            info_request,
        ),
    )

    decisions = tuple(
        evaluate_non_action_reuse_decision_v01(
            scenario_id,
            candidate_class,
            scenario_record,
            request,
        )
        for scenario_id, candidate_class, scenario_record, request in scenario_inputs
    )
    artifacts = tuple(
        artifact
        for artifact in (
            create_root_informational_reuse_artifact_v01(
                decision,
                scenario_record,
                request,
            )
            for decision, (_, _, scenario_record, request) in zip(
                decisions,
                scenario_inputs,
            )
        )
        if artifact is not None
    )
    counters = _build_report_counters(decisions)
    positive_decision = _decision_by_candidate(
        decisions,
        CANDIDATE_INFORMATIONAL_POLICY_SUMMARY_DIRECT_REUSE,
    )
    payment_decision = _decision_by_candidate(
        decisions,
        CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION,
    )
    shipment_decision = _decision_by_candidate(
        decisions,
        CANDIDATE_SAME_POLICY_RECORD_AS_SHIPMENT_RELEASE,
    )
    ticket_decision = _decision_by_candidate(
        decisions,
        CANDIDATE_SAME_POLICY_RECORD_AS_TICKET_PURCHASE,
    )

    report = NonActionDirectReuseReportV01(
        report_id="non_action_direct_reuse_positive_control_v01",
        final_status=STATUS_PASS,
        scenarios_total=6,
        scenarios_passed=6,
        positive_control={
            "direct_reuse_allowed": positive_decision.direct_reuse_allowed,
            "direct_reuse_allowed_for_information_only": (
                positive_decision.direct_reuse_allowed_for_information_only
            ),
            "action_intent": False,
            "root_shortcut_allowed": positive_decision.root_shortcut_allowed,
            "root_final_from_reuse_created": (
                positive_decision.root_final_from_reuse_created
            ),
        },
        negative_controls={
            "payment_direct_reuse_allowed": payment_decision.direct_reuse_allowed,
            "shipment_direct_reuse_allowed": shipment_decision.direct_reuse_allowed,
            "ticket_purchase_direct_reuse_allowed": ticket_decision.direct_reuse_allowed,
            "action_permission_granted": any(
                decision.action_permission_granted for decision in decisions
            ),
            "action_commit_packet_created": any(
                decision.action_commit_packet_created for decision in decisions
            ),
            "receipt_created": any(decision.receipt_created for decision in decisions),
            "real_world_effects_count": 0,
        },
        decisions=decisions,
        informational_artifacts=artifacts,
        counters=counters,
        validation_errors=(),
    )
    valid, errors = validate_non_action_direct_reuse_report_v01(report)
    if valid:
        return report
    return replace(report, final_status=STATUS_FAIL_CLOSED, validation_errors=errors)


def validate_non_action_direct_reuse_report_v01(
    report: NonActionDirectReuseReportV01,
) -> tuple[bool, tuple[str, ...]]:
    errors: tuple[str, ...] = ()

    required_counters = _required_counters()
    for key, expected in required_counters.items():
        if report.counters.get(key) != expected:
            errors = _with_reason(errors, f"counter_mismatch:{key}")

    if report.final_status != STATUS_PASS:
        errors = _with_reason(errors, "final_status_not_pass")
    if report.scenarios_total != len(report.decisions):
        errors = _with_reason(errors, "scenario_total_mismatch")
    if report.scenarios_passed != report.scenarios_total:
        errors = _with_reason(errors, "scenario_pass_count_mismatch")

    direct_reuse_decisions = tuple(
        decision for decision in report.decisions if decision.direct_reuse_allowed
    )
    info_direct_reuse_decisions = tuple(
        decision
        for decision in report.decisions
        if decision.direct_reuse_allowed_for_information_only
    )
    if len(direct_reuse_decisions) != 1 or len(info_direct_reuse_decisions) != 1:
        errors = _with_reason(errors, "direct_reuse_count_mismatch")

    if len(report.informational_artifacts) != 1:
        errors = _with_reason(errors, "informational_artifact_count_mismatch")

    for decision in report.decisions:
        if _decision_claims_non_root_authority(decision):
            errors = _with_reason(errors, f"non_root_authority:{decision.scenario_id}")
        if _decision_claims_action_or_effect(decision):
            errors = _with_reason(errors, f"effect_claim:{decision.scenario_id}")
        if (
            decision.candidate_class
            in (
                CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION,
                CANDIDATE_SAME_POLICY_RECORD_AS_SHIPMENT_RELEASE,
                CANDIDATE_SAME_POLICY_RECORD_AS_TICKET_PURCHASE,
            )
            and not decision.action_reuse_blocked
        ):
            errors = _with_reason(errors, f"action_path_not_blocked:{decision.scenario_id}")

    for artifact in report.informational_artifacts:
        if artifact.created_by != "root" or not artifact.root_created:
            errors = _with_reason(errors, f"artifact_not_root_created:{artifact.artifact_id}")
        if _artifact_claims_action_or_effect(artifact):
            errors = _with_reason(errors, f"artifact_effect_claim:{artifact.artifact_id}")

    negative = report.negative_controls
    for key in (
        "payment_direct_reuse_allowed",
        "shipment_direct_reuse_allowed",
        "ticket_purchase_direct_reuse_allowed",
        "action_permission_granted",
        "action_commit_packet_created",
        "receipt_created",
    ):
        if negative.get(key) is not False:
            errors = _with_reason(errors, f"negative_control_mismatch:{key}")
    if negative.get("real_world_effects_count") != 0:
        errors = _with_reason(errors, "negative_control_effect_counter")

    return not errors, errors


def _request_is_action_like(request: NonActionReuseRequestV01) -> bool:
    return (
        request.action_intent
        or request.external_effect_requested
        or request.asks_payment_permission
        or request.asks_shipment_release
        or request.asks_ticket_purchase
        or request.asks_action_commit_packet
        or request.asks_receipt_creation
        or request.asks_final_output
    )


def _record_claims_effect(record: NonActionDirectReuseRecordV01) -> bool:
    return (
        record.creates_permission
        or record.creates_action_commit_packet
        or record.creates_receipt
        or record.executes_payment
        or record.releases_shipment
        or record.issues_ticket
        or record.real_world_effects_count != 0
    )


def _with_reason(reasons: tuple[str, ...], reason: str) -> tuple[str, ...]:
    if reason in reasons:
        return reasons
    return reasons + (reason,)


def _with_reasons(
    reasons: tuple[str, ...],
    extra_reasons: tuple[str, ...],
) -> tuple[str, ...]:
    for reason in extra_reasons:
        reasons = _with_reason(reasons, reason)
    return reasons


def _base_decision_reasons(gate_reasons: tuple[str, ...]) -> tuple[str, ...]:
    return _with_reasons(
        gate_reasons,
        (
            REASON_DRS_HIT_NOT_TRUTH,
            REASON_REUSE_SCORE_NOT_AUTHORITY,
            REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY,
            REASON_ROOT_REMAINS_FINAL_AUTHORITY,
        ),
    )


def _action_block_reasons(
    reasons: tuple[str, ...],
    request: NonActionReuseRequestV01,
) -> tuple[str, ...]:
    reasons = _with_reasons(
        reasons,
        (
            REASON_ACTION_REUSE_BLOCKED,
            REASON_OLD_MEMORY_CAN_HELP_BUT_CANNOT_ACT,
            REASON_NO_ACTION_PERMISSION,
        ),
    )
    if request.asks_payment_permission:
        reasons = _with_reason(reasons, REASON_NO_PAYMENT_PERMISSION)
    if request.asks_shipment_release:
        reasons = _with_reason(reasons, REASON_NO_SHIPMENT_PERMISSION)
    if request.asks_ticket_purchase:
        reasons = _with_reason(reasons, REASON_NO_TICKET_PERMISSION)
    if request.asks_action_commit_packet:
        reasons = _with_reason(reasons, REASON_ROOT_SHORTCUT_REQUIRED)
    if request.asks_receipt_creation:
        reasons = _with_reason(reasons, REASON_OLD_RECEIPT_NOT_PERMISSION)
    return reasons


def _build_report_counters(
    decisions: tuple[NonActionReuseDecisionV01, ...],
) -> dict[str, int]:
    return {
        "non_action_direct_reuse_positive_control_count": 1,
        "scenarios_total": len(decisions),
        "scenarios_passed": len(decisions),
        "direct_reuse_allowed_count": sum(
            int(decision.direct_reuse_allowed) for decision in decisions
        ),
        "non_action_direct_reuse_allowed_count": sum(
            int(decision.direct_reuse_allowed_for_information_only)
            for decision in decisions
        ),
        "root_shortcut_allowed_count": sum(
            int(decision.root_shortcut_allowed) for decision in decisions
        ),
        "root_final_from_reuse_created_count": sum(
            int(decision.root_final_from_reuse_created) for decision in decisions
        ),
        "architect_skipped_for_safe_informational_reuse_count": sum(
            int(decision.architect_skipped) for decision in decisions
        ),
        "executor_skipped_for_safe_informational_reuse_count": sum(
            int(decision.executor_skipped) for decision in decisions
        ),
        "heavy_pipeline_skipped_count": sum(
            int(decision.heavy_pipeline_skipped) for decision in decisions
        ),
        "payment_direct_reuse_allowed_count": sum(
            int(
                decision.candidate_class
                == CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION
                and decision.direct_reuse_allowed
            )
            for decision in decisions
        ),
        "shipment_direct_reuse_allowed_count": sum(
            int(
                decision.candidate_class
                == CANDIDATE_SAME_POLICY_RECORD_AS_SHIPMENT_RELEASE
                and decision.direct_reuse_allowed
            )
            for decision in decisions
        ),
        "ticket_purchase_direct_reuse_allowed_count": sum(
            int(
                decision.candidate_class
                == CANDIDATE_SAME_POLICY_RECORD_AS_TICKET_PURCHASE
                and decision.direct_reuse_allowed
            )
            for decision in decisions
        ),
        "action_permission_granted_count": sum(
            int(decision.action_permission_granted) for decision in decisions
        ),
        "action_commit_packet_created_count": sum(
            int(decision.action_commit_packet_created) for decision in decisions
        ),
        "receipt_created_count": sum(
            int(decision.receipt_created) for decision in decisions
        ),
        "payment_executed_count": sum(
            int(decision.payment_executed) for decision in decisions
        ),
        "shipment_released_count": sum(
            int(decision.shipment_released) for decision in decisions
        ),
        "ticket_issued_count": sum(
            int(decision.ticket_issued) for decision in decisions
        ),
        "avf_score_used_as_authority_count": sum(
            int(decision.avf_is_authority) for decision in decisions
        ),
        "drs_hit_used_as_authority_count": sum(
            int(decision.drs_is_authority) for decision in decisions
        ),
        "reuse_gate_used_as_root_count": sum(
            int(decision.reuse_gate_is_authority) for decision in decisions
        ),
        "root_bypass_count": sum(
            int(REASON_ROOT_REMAINS_FINAL_AUTHORITY not in decision.reason_codes)
            for decision in decisions
        ),
        "provider_called_count": sum(
            int(decision.provider_called) for decision in decisions
        ),
        "network_used_count": sum(
            int(decision.network_called) for decision in decisions
        ),
        "gemini_called_count": sum(
            int(decision.gemini_called) for decision in decisions
        ),
        "real_world_effects_count": sum(
            decision.real_world_effects_count for decision in decisions
        ),
        "root_final_authority_preserved_count": sum(
            int(REASON_ROOT_REMAINS_FINAL_AUTHORITY in decision.reason_codes)
            for decision in decisions
        ),
    }


def _required_counters() -> dict[str, int]:
    return {
        "non_action_direct_reuse_positive_control_count": 1,
        "scenarios_total": 6,
        "scenarios_passed": 6,
        "direct_reuse_allowed_count": 1,
        "non_action_direct_reuse_allowed_count": 1,
        "root_shortcut_allowed_count": 1,
        "root_final_from_reuse_created_count": 1,
        "architect_skipped_for_safe_informational_reuse_count": 1,
        "executor_skipped_for_safe_informational_reuse_count": 1,
        "heavy_pipeline_skipped_count": 1,
        "payment_direct_reuse_allowed_count": 0,
        "shipment_direct_reuse_allowed_count": 0,
        "ticket_purchase_direct_reuse_allowed_count": 0,
        "action_permission_granted_count": 0,
        "action_commit_packet_created_count": 0,
        "receipt_created_count": 0,
        "payment_executed_count": 0,
        "shipment_released_count": 0,
        "ticket_issued_count": 0,
        "avf_score_used_as_authority_count": 0,
        "drs_hit_used_as_authority_count": 0,
        "reuse_gate_used_as_root_count": 0,
        "root_bypass_count": 0,
        "provider_called_count": 0,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_world_effects_count": 0,
        "root_final_authority_preserved_count": 6,
    }


def _decision_by_candidate(
    decisions: tuple[NonActionReuseDecisionV01, ...],
    candidate_class: str,
) -> NonActionReuseDecisionV01:
    for decision in decisions:
        if decision.candidate_class == candidate_class:
            return decision
    raise ValueError(f"missing decision for candidate class: {candidate_class}")


def _decision_claims_non_root_authority(
    decision: NonActionReuseDecisionV01,
) -> bool:
    return (
        decision.drs_is_authority
        or decision.avf_is_authority
        or decision.reuse_gate_is_authority
        or decision.reuse_score_is_authority
        or decision.semantic_similarity_is_authority
    )


def _decision_claims_action_or_effect(decision: NonActionReuseDecisionV01) -> bool:
    return (
        decision.informational_answer_is_permission
        or decision.action_permission_granted
        or decision.payment_permission_created
        or decision.shipment_permission_created
        or decision.ticket_permission_created
        or decision.action_commit_packet_created
        or decision.receipt_created
        or decision.payment_executed
        or decision.shipment_released
        or decision.ticket_issued
        or decision.provider_called
        or decision.network_called
        or decision.gemini_called
        or decision.real_world_effects_count != 0
    )


def _artifact_claims_action_or_effect(
    artifact: NonActionInformationalReuseArtifactV01,
) -> bool:
    return (
        artifact.action_permission_granted
        or artifact.payment_permission_created
        or artifact.shipment_permission_created
        or artifact.ticket_permission_created
        or artifact.action_commit_packet_created
        or artifact.receipt_created
        or artifact.payment_executed
        or artifact.shipment_released
        or artifact.ticket_issued
        or artifact.final_output_created
        or artifact.real_world_effects_count != 0
    )
