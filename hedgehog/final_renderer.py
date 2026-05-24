from __future__ import annotations


def _vv_by_proposal_id(vv_reports: list[dict]) -> dict[str, dict]:
    return {report["proposal_id"]: report for report in vv_reports}


def _needs_user_proposal_ids(result_proposals: list[dict], vv_reports: list[dict]) -> list[str]:
    reports = _vv_by_proposal_id(vv_reports)
    proposal_ids = []
    for proposal in result_proposals:
        report = reports.get(proposal["proposal_id"])
        if not report:
            continue
        if report.get("decision") == "revise" or report.get("status") == "needs_revision":
            proposal_ids.append(proposal["proposal_id"])
    return proposal_ids


def _blocked_proposal_ids(result_proposals: list[dict]) -> list[str]:
    proposal_ids = []
    for proposal in result_proposals:
        payload = proposal.get("result_payload", {})
        if isinstance(payload, dict) and payload.get("blocked_reason"):
            proposal_ids.append(proposal["proposal_id"])
    return proposal_ids


def _status_recommendation(gt_report: dict) -> str:
    decision = gt_report.get("decision")
    if decision == "accept":
        return "success"
    if decision in {"revise", "no_update"}:
        return "needs_user"
    return "failed"


def _body(status: str, selected_ids: list[str], needs_user_ids: list[str], blocked_ids: list[str]) -> str:
    parts = []
    if status == "success":
        parts.append("Deterministic MVP pipeline completed with a GT-selected proposal.")
    elif status == "needs_user":
        parts.append("Deterministic MVP pipeline needs human input before completion.")
    else:
        parts.append("Deterministic MVP pipeline did not produce a usable completion.")

    if selected_ids:
        parts.append(f"Selected proposal: {selected_ids[0]}.")
    else:
        parts.append("No GT winner proposal was selected.")

    if needs_user_ids:
        parts.append("Some proposals require human input.")
    if blocked_ids:
        parts.append("Some proposals are blocked before completion.")

    parts.append("No real external action was performed.")
    return " ".join(parts)


def render_final_draft(
    *,
    request_id: str,
    gt_report: dict,
    result_proposals: list[dict],
    vv_reports: list[dict],
    drs_writes: list[str],
    mode: str = "deterministic_mvp",
) -> dict:
    selected_proposal_ids = [gt_report["winner"]] if gt_report.get("winner") else []
    needs_user_proposal_ids = _needs_user_proposal_ids(result_proposals, vv_reports)
    blocked_proposal_ids = _blocked_proposal_ids(result_proposals)
    status = _status_recommendation(gt_report)

    warnings = []
    if needs_user_proposal_ids:
        warnings.append("human_input_required")
    if blocked_proposal_ids:
        warnings.append("blocked_proposals_present")
    if not selected_proposal_ids:
        warnings.append("no_gt_winner")

    return {
        "draft_id": f"draft:{request_id}",
        "request_id": request_id,
        "created_by": "final_renderer",
        "mode": mode,
        "status_recommendation": status,
        "body": _body(
            status=status,
            selected_ids=selected_proposal_ids,
            needs_user_ids=needs_user_proposal_ids,
            blocked_ids=blocked_proposal_ids,
        ),
        "summary": "Deterministic final draft proposal for Root review.",
        "selected_proposal_ids": selected_proposal_ids,
        "needs_user_proposal_ids": needs_user_proposal_ids,
        "blocked_proposal_ids": blocked_proposal_ids,
        "gt_report_ref": gt_report["gt_report_id"],
        "drs_writes": drs_writes,
        "claims": [
            "root_must_create_final_output",
            "gt_report_was_available",
            "result_proposals_were_validated",
            "drs_writeback_available",
        ],
        "warnings": warnings,
    }
