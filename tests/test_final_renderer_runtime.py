from hedgehog.final_renderer import render_final_draft


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def sample_proposal(proposal_id="proposal:completed", blocked=False):
    payload = {
        "status": "simulated_success",
        "node_id": "node:sample",
        "task_completed": True,
        "artifact_type": "request_payload",
        "avf": {
            "final_viability": 0.9,
            "soft_mask": 1.0,
            "vector_id": "official_online_request",
        },
    }
    if blocked:
        payload["status"] = "needs_user"
        payload["task_completed"] = False
        payload["blocked_reason"] = "missing_human_identity_confirmation"
    return {
        "proposal_id": proposal_id,
        "result_payload": payload,
    }


def sample_vv_report(proposal_id="proposal:completed", decision="accept", status="accepted"):
    return {
        "proposal_id": proposal_id,
        "decision": decision,
        "status": status,
    }


def test_render_final_draft_returns_subordinate_draft():
    draft = render_final_draft(
        request_id="req_final_renderer_001",
        gt_report={
            "gt_report_id": "gt:sample",
            "decision": "accept",
            "winner": "proposal:completed",
        },
        result_proposals=[sample_proposal()],
        vv_reports=[sample_vv_report()],
        drs_writes=["work:req_final_renderer_001"],
    )

    assert draft["draft_id"] == "draft:req_final_renderer_001"
    assert draft["created_by"] == "final_renderer"
    assert draft["status_recommendation"] == "success"
    assert draft["body"]
    assert draft["summary"]
    assert draft["claims"]
    assert draft["selected_proposal_ids"] == ["proposal:completed"]
    assert draft["completed_proposal_ids"] == ["proposal:completed"]
    assert draft["rejected_proposal_ids"] == []
    assert "final_draft_is_not_final_output" in draft["claims"]
    assert "root_final_authority_required" in draft["claims"]
    assert not contains_key(draft, "final_output")
    assert not contains_key(draft, "raw_user_text")


def test_render_final_draft_revise_gt_recommends_needs_user():
    draft = render_final_draft(
        request_id="req_final_renderer_revise",
        gt_report={
            "gt_report_id": "gt:revise",
            "decision": "revise",
        },
        result_proposals=[],
        vv_reports=[],
        drs_writes=["work:req_final_renderer_revise"],
    )

    assert draft["status_recommendation"] == "needs_user"
    assert draft["selected_proposal_ids"] == []
    assert "no_gt_winner" in draft["warnings"]


def test_render_final_draft_records_blocked_and_needs_user_proposals():
    proposal = sample_proposal("proposal:blocked", blocked=True)
    draft = render_final_draft(
        request_id="req_final_renderer_blocked",
        gt_report={
            "gt_report_id": "gt:blocked",
            "decision": "revise",
        },
        result_proposals=[proposal],
        vv_reports=[
            sample_vv_report(
                proposal_id="proposal:blocked",
                decision="revise",
                status="needs_revision",
            )
        ],
        drs_writes=["work:req_final_renderer_blocked"],
    )

    assert draft["status_recommendation"] == "needs_user"
    assert draft["needs_user_proposal_ids"] == ["proposal:blocked"]
    assert draft["blocked_proposal_ids"] == ["proposal:blocked"]
    assert "human_input_required" in draft["warnings"]
    assert "blocked_proposals_present" in draft["warnings"]


def test_render_final_draft_records_rejected_proposals():
    proposal = sample_proposal("proposal:rejected")
    draft = render_final_draft(
        request_id="req_final_renderer_rejected",
        gt_report={
            "gt_report_id": "gt:rejected",
            "decision": "no_update",
        },
        result_proposals=[proposal],
        vv_reports=[
            sample_vv_report(
                proposal_id="proposal:rejected",
                decision="reject",
                status="rejected",
            )
        ],
        drs_writes=["work:req_final_renderer_rejected"],
    )

    assert draft["status_recommendation"] == "needs_user"
    assert draft["completed_proposal_ids"] == []
    assert draft["rejected_proposal_ids"] == ["proposal:rejected"]
    assert "rejected_proposals_present" in draft["warnings"]
    assert "no_gt_winner" in draft["warnings"]
