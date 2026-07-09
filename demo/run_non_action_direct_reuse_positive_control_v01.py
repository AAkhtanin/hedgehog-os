from __future__ import annotations

from hedgehog import non_action_reuse_positive_control as reuse


RUN_ID = "non_action_direct_reuse_positive_control_v01"
REPORT_ID = "non_action_direct_reuse_positive_control_v01"

REQUIRED_SCENARIOS = (
    "informational_policy_summary_direct_reuse",
    "same_policy_record_as_payment_permission",
    "same_policy_record_as_shipment_release",
    "same_policy_record_as_ticket_purchase",
    "stale_policy_summary_context_only",
    "high_score_without_root_shortcut",
)

NON_CLAIMS = (
    "not production",
    "not public auditor final package",
    "no Gemini/provider/network",
    "no external API",
    "no Airline implementation",
    "no payment",
    "no shipment release",
    "no ticket issue",
    "no ActionCommitPacket",
    "no receipt",
    "no FinalOutput",
    "no real-world effects",
)

NEXT_GATE = "Airline tri-party preflight after this mini-layer closes"


def collect_non_action_direct_reuse_positive_control_v01() -> dict[str, object]:
    model_report = reuse.build_non_action_direct_reuse_positive_control_report_v01()
    valid, validation_errors = reuse.validate_non_action_direct_reuse_report_v01(
        model_report,
    )
    final_status = reuse.STATUS_PASS if valid else reuse.STATUS_FAIL_CLOSED

    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "final_status": final_status,
        "model_report": _json_safe(model_report),
        "scenario_table": tuple(
            _scenario_row(decision) for decision in model_report.decisions
        ),
        "positive_control": dict(model_report.positive_control),
        "negative_controls": dict(model_report.negative_controls),
        "informational_artifacts": tuple(
            _json_safe(artifact)
            for artifact in model_report.informational_artifacts
        ),
        "counters": dict(model_report.counters),
        "validation_errors": validation_errors,
        "non_claims": NON_CLAIMS,
        "next_gate": NEXT_GATE,
    }


def render_non_action_direct_reuse_positive_control_v01(
    report: dict[str, object],
) -> str:
    counters = report["counters"]
    scenario_rows = report["scenario_table"]
    positive = report["positive_control"]
    negative = report["negative_controls"]

    lines: list[str] = []
    lines.extend(
        (
            "[NON-ACTION DIRECT REUSE POSITIVE CONTROL V0.1]",
            f"run_id: {report['run_id']}",
            f"report_id: {report['report_id']}",
            "",
            "[WHAT THIS PROVES]",
            (
                "Hedgehog OS can reuse memory to answer a safe informational "
                "question without re-running the heavy cognitive loop, but the "
                "same memory cannot authorize payment, shipment release, ticket "
                "purchase, permission, receipt, ActionCommitPacket, or any "
                "real-world action."
            ),
            "Direct reuse saves compute; it does not transfer authority.",
            "",
            "[POSITIVE INFORMATIONAL REUSE]",
            "one informational direct reuse allowed",
            "RootShortcutAllowed required",
            "Root creates informational reuse artifact",
            "Architect skipped for safe informational reuse",
            "Executor skipped for safe informational reuse",
            "heavy pipeline skipped for safe informational reuse",
            f"direct_reuse_allowed_for_information_only: {positive['direct_reuse_allowed_for_information_only']}",
            "",
            "[NEGATIVE ACTION-LIKE REUSE CONTROLS]",
            "payment reuse blocked",
            "shipment reuse blocked",
            "ticket purchase reuse blocked",
            "ActionCommitPacket creation blocked",
            "receipt creation blocked",
            "stale policy summary context-only",
            "high score without RootShortcutAllowed blocked",
            f"payment_direct_reuse_allowed: {negative['payment_direct_reuse_allowed']}",
            f"shipment_direct_reuse_allowed: {negative['shipment_direct_reuse_allowed']}",
            f"ticket_purchase_direct_reuse_allowed: {negative['ticket_purchase_direct_reuse_allowed']}",
            "",
            "[ROOT SHORTCUT GATE]",
            "RootShortcutAllowed required",
            "root_shortcut_allowed required before informational shortcut.",
            "Root creates informational reuse artifact.",
            "",
            "[SCENARIO TABLE]",
        ),
    )
    for row in scenario_rows:
        lines.append(
            "{candidate_class}: decision={decision_class}, direct_reuse_allowed={direct_reuse_allowed}, root_shortcut_allowed={root_shortcut_allowed}, root_review_required={root_review_required}".format(
                **row,
            ),
        )

    lines.append("")
    lines.append("[COUNTER TABLE]")
    for key in sorted(counters):
        lines.append(f"{key}: {counters[key]}")

    lines.extend(
        (
            "",
            "[AUTHORITY BOUNDARIES]",
            "DRS hit is not truth",
            "AVF score is not permission",
            "reuse score is not authority",
            "semantic similarity is not authority",
            "Root remains final authority",
            "provider/network/Gemini counters zero",
            "real_world_effects_count zero",
            "",
            "[NON-CLAIMS]",
        ),
    )
    lines.extend(f"- {claim}" for claim in report["non_claims"])
    lines.extend(
        (
            "",
            "[NEXT GATE]",
            str(report["next_gate"]),
            "",
            "[FINAL STATUS]",
            str(report["final_status"]),
        ),
    )
    return "\n".join(lines)


def run_non_action_direct_reuse_positive_control_v01() -> str:
    return render_non_action_direct_reuse_positive_control_v01(
        collect_non_action_direct_reuse_positive_control_v01(),
    )


def main() -> int:
    print(run_non_action_direct_reuse_positive_control_v01())
    return 0


def _scenario_row(decision: reuse.NonActionReuseDecisionV01) -> dict[str, object]:
    return {
        "scenario_id": decision.scenario_id,
        "candidate_class": decision.candidate_class,
        "decision_class": decision.decision_class,
        "direct_reuse_allowed": decision.direct_reuse_allowed,
        "direct_reuse_allowed_for_information_only": (
            decision.direct_reuse_allowed_for_information_only
        ),
        "action_reuse_blocked": decision.action_reuse_blocked,
        "root_shortcut_allowed": decision.root_shortcut_allowed,
        "root_final_from_reuse_created": decision.root_final_from_reuse_created,
        "architect_skipped": decision.architect_skipped,
        "executor_skipped": decision.executor_skipped,
        "heavy_pipeline_skipped": decision.heavy_pipeline_skipped,
        "root_review_required": decision.root_review_required,
        "reason_codes": decision.reason_codes,
        "action_permission_granted": decision.action_permission_granted,
        "action_commit_packet_created": decision.action_commit_packet_created,
        "receipt_created": decision.receipt_created,
        "payment_executed": decision.payment_executed,
        "shipment_released": decision.shipment_released,
        "ticket_issued": decision.ticket_issued,
        "provider_called": decision.provider_called,
        "network_called": decision.network_called,
        "gemini_called": decision.gemini_called,
        "real_world_effects_count": decision.real_world_effects_count,
    }


def _json_safe(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _json_safe(item)
            for key, item in value.__dict__.items()
        }
    if isinstance(value, tuple):
        return tuple(_json_safe(item) for item in value)
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


if __name__ == "__main__":
    raise SystemExit(main())
