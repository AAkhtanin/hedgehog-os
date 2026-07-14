from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Mapping

from demo import run_airline_transaction_artifact_ledger_audit_v01 as audit


def render_human_airline_transaction_artifact_ledger_timeline_v01(
    *,
    artifact_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=artifact_dir,
        env=env,
    )
    return render_human_airline_transaction_artifact_ledger_timeline_report_v01(
        report,
    )


def render_human_airline_transaction_artifact_ledger_timeline_report_v01(
    report: audit.AirlineTransactionArtifactLedgerAuditReportV01,
) -> str:
    if report.final_status == audit.SKIPPED_CLOSED:
        return "\n".join(
            (
                "[AIRLINE TRANSACTION ARTIFACT LEDGER - HUMAN TIMELINE V0.1]",
                "",
                "[FINAL STATUS]",
                audit.SKIPPED_CLOSED,
                "skip_reason: source_artifact_dir_not_selected",
                "No artifact package was selected. No filesystem search occurred.",
            ),
        )
    if report.final_status != audit.PASS:
        return "\n".join(
            (
                "[AIRLINE TRANSACTION ARTIFACT LEDGER - HUMAN TIMELINE V0.1]",
                "",
                "[SOURCE PACKAGE]",
                f"source_artifact_dir: {report.source_artifact_dir}",
                "",
                "[FINAL STATUS]",
                audit.FAIL_CLOSED,
                "validation_errors:",
                *[f"- {reason}" for reason in report.validation_errors],
                "",
                "[HONEST NON-CLAIMS]",
                *[f"- {claim}" for claim in report.non_claims],
            ),
        )
    lines = [
        "[AIRLINE TRANSACTION ARTIFACT LEDGER - HUMAN TIMELINE V0.1]",
        "",
        "[SOURCE PACKAGE]",
        f"selected_artifact_dir: {report.source_artifact_dir}",
        f"files_read: {report.files_read_count}",
        "rerun: none",
        "",
        "[TRANSACTION]",
        f"ledger_id: {report.ledger_id}",
        f"transaction_id: {report.transaction_id}",
        f"selected_offer_id: {report.selected_offer_id}",
        f"source_run_ref: {report.source_run_ref}",
        f"source_causal_report_ref: {report.source_causal_report_ref}",
        f"source_corridor_report_ref: {report.source_corridor_report_ref}",
        "",
        "[WHAT THE LEDGER PROVES]",
        "- records one internally consistent trace",
        "- records ordering and dependencies",
        "- records Root ownership and evidence classes",
        "- does not prove semantic truth",
        "- does not grant permission",
        "- does not execute",
        "",
        "[TIMELINE]",
    ]
    for row in report.timeline_rows:
        lines.extend(_render_row(row))
    lines.extend(
        (
            "",
            "[ROOT BOUNDARIES]",
            "- ClientRoot final: visible as ClientRootFinalV01",
            "- AirlineRoot final: visible as AirlineRootFinalV01",
            "- BankRoot final: visible as BankRootFinalV01",
            "- Cross-root advisory is not a fourth Root.",
            "",
            "[RECEIPT BOUNDARIES]",
            "- Offer/hold receipt is evidence only.",
            "- Ticket receipt is evidence only.",
            "- Purchase receipt is evidence only.",
            "- Receipt did not create permission.",
            "",
            "[INDEPENDENT AUDIT]",
            f"- entries: {report.actual_entry_count}",
            f"- dependency edges: {report.actual_dependency_edge_count}",
            f"- Root finals: {report.actual_root_final_count}",
            f"- exact sequence: {_pass_word(report.artifact_type_sequence_valid)}",
            f"- dependency checks: {_pass_word(report.dependencies_present and report.dependencies_backward_only and report.dependency_graph_acyclic)}",
            f"- selected-offer consistency: {_pass_word(report.selected_offer_chain_consistent)}",
            f"- source-reference consistency: {_pass_word(report.source_refs_consistent)}",
            f"- secret boundary: {_pass_word(report.secret_scan_passed)}",
            "",
            "[NO-RERUN / NO-EFFECT COUNTERS]",
            f"- semantic rerun: {report.semantic_rerun_count}",
            f"- corridor rerun: {report.corridor_rerun_count}",
            f"- Ledger collection: {report.ledger_collection_count}",
            f"- provider: {report.provider_call_count}",
            f"- network: {report.network_call_count}",
            f"- Gemini: {report.gemini_call_count}",
            f"- Crypto: {report.crypto_operation_count}",
            f"- Replay: {report.replay_operation_count}",
            f"- real-world effects: {report.real_world_effects_count}",
            "",
            "[HONEST LIMITS]",
            "- no Crypto Artifact Seal",
            "- no cryptographic manifest",
            "- no signature",
            "- no hash chain",
            "- no sealed replay",
            "- no production security claim",
            "- no real payment",
            "- no real ticket",
            "- no real booking",
            "",
            "[FINAL STATUS]",
            audit.PASS,
            f"next_gate: {report.next_gate}",
        ),
    )
    return "\n".join(lines)


def _render_row(
    row: audit.AirlineTransactionArtifactLedgerAuditTimelineRowV01,
) -> tuple[str, ...]:
    dependencies = ", ".join(row.depends_on) if row.depends_on else "none"
    owner = row.root_owner or "non-authoritative"
    offer = f"; selected_offer_id={row.selected_offer_id}" if row.selected_offer_id else ""
    return (
        f"{row.ledger_index + 1}. {row.human_event_label}",
        f"   artifact: {row.artifact_type} / {row.artifact_id}",
        f"   owner: {owner}; created_by={row.created_by}",
        f"   role: authority={row.authority_class}; evidence={row.evidence_class}{offer}",
        f"   dependencies ({row.dependency_count}): {dependencies}",
        f"   explanation: {row.human_explanation}",
    )


def _pass_word(value: bool) -> str:
    return audit.PASS if value else audit.FAIL_CLOSED


def timeline_report_to_json_safe(
    report: audit.AirlineTransactionArtifactLedgerAuditReportV01,
) -> dict[str, object]:
    return asdict(report)


def main() -> int:
    rendered = render_human_airline_transaction_artifact_ledger_timeline_v01()
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
