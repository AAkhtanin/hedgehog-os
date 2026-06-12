from __future__ import annotations

from demo.run_all_layers_applied_super_smoke import (
    collect_all_layers_applied_super_smoke,
)
from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_applied_warehouse_semantic_demo import (
    collect_applied_warehouse_semantic_demo,
)
from demo.run_drs_adversarial_stress_pack import collect_drs_adversarial_stress_pack
from demo.run_needlecandidate_lifecycle_proof import (
    collect_needlecandidate_lifecycle_proof,
)
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
)


def _by_id(rows: list[dict], key: str) -> dict[str, dict]:
    return {row[key]: row for row in rows}


def collect_human_applied_auditor_walkthrough() -> dict:
    warehouse = collect_applied_warehouse_semantic_demo()
    certificate = collect_applied_certificate_readiness_demo()
    permission = collect_permission_needsuser_ux_proof()
    needlecandidate = collect_needlecandidate_lifecycle_proof()
    retrieval = collect_applied_drs_retrieval_reuse()
    adversarial = collect_drs_adversarial_stress_pack()
    super_smoke = collect_all_layers_applied_super_smoke()

    candidates = _by_id(needlecandidate.needle_candidate_artifacts, "candidate_id")
    retrieval_finals = _by_id(
        retrieval.applied_reuse_root_final_artifacts, "root_final_artifact_id"
    )
    adversarial_finals = _by_id(
        adversarial.drs_adversarial_root_final_artifacts, "scenario"
    )

    return {
        "warehouse": {
            "status": warehouse.summary["applied_warehouse_semantic_demo_status"],
            "warehouse_id": warehouse.summary["warehouse_id"],
            "dispatch_id": warehouse.summary["dispatch_id"],
            "dispatch_readiness": warehouse.summary["dispatch_readiness"],
            "blocking_reason": warehouse.summary["blocking_reason"],
        },
        "certificate": {
            "status": certificate.summary["applied_certificate_readiness_demo_status"],
            "application_id": certificate.summary["application_id"],
            "certificate_request_id": certificate.summary["certificate_request_id"],
            "certificate_readiness": certificate.summary["certificate_readiness"],
            "blocking_reasons": certificate.summary["blocking_reasons"],
        },
        "permission": {
            "status": permission.summary["permission_needsuser_ux_proof_status"],
            "denial_blocks_action": permission.summary[
                "explicit_user_denial_blocks_action"
            ],
            "approval_is_future_permission_only": permission.summary[
                "explicit_user_approval_is_future_permission_only"
            ],
            "completed_action_without_execution_rejected": permission.summary[
                "completed_action_without_execution_rejected"
            ],
        },
        "needlecandidate": {
            "status": needlecandidate.summary["needlecandidate_lifecycle_proof_status"],
            "warehouse_action_class": candidates[
                "needle_candidate_warehouse_restock_readiness_v0_1"
            ]["allowed_action_class"],
            "certificate_action_class": candidates[
                "needle_candidate_certificate_document_update_v0_1"
            ]["allowed_action_class"],
            "candidate_status": needlecandidate.needle_candidate_gt_selection[
                "recommended_candidate_status"
            ],
            "gt_cannot_install_needles": needlecandidate.summary[
                "gt_cannot_install_needles"
            ],
            "installed_needle_created": needlecandidate.summary[
                "installed_needle_created"
            ],
        },
        "retrieval": {
            "status": retrieval.summary["applied_drs_retrieval_reuse_status"],
            "warehouse_root_decision": retrieval_finals[
                "root_reuse_warehouse_partial"
            ]["root_decision"],
            "certificate_root_decision": retrieval_finals[
                "root_reuse_certificate_needs_user"
            ]["root_decision"],
            "semantic_similarity_is_not_authority": retrieval.summary[
                "semantic_similarity_is_not_authority"
            ],
            "reuse_score_is_not_root": retrieval.summary["reuse_score_is_not_root"],
            "no_direct_ready_created": retrieval.summary["no_direct_ready_created"],
        },
        "adversarial": {
            "status": adversarial.summary["drs_adversarial_stress_pack_status"],
            "scenarios_verified": adversarial.summary["scenarios_verified"],
            "root_decisions": {
                scenario: final["root_decision"]
                for scenario, final in adversarial_finals.items()
            },
        },
        "super_smoke": {
            "status": super_smoke.summary["all_layers_applied_super_smoke_status"],
            "layers_observed": super_smoke.summary["layers_observed"],
            "source_statuses_all_pass": super_smoke.summary[
                "source_statuses_all_pass"
            ],
            "root_remains_final_authority": super_smoke.summary[
                "root_remains_final_authority"
            ],
        },
    }


def render_human_applied_auditor_walkthrough(report: dict) -> str:
    warehouse = report["warehouse"]
    certificate = report["certificate"]
    permission = report["permission"]
    needlecandidate = report["needlecandidate"]
    retrieval = report["retrieval"]
    adversarial = report["adversarial"]
    super_smoke = report["super_smoke"]

    attack_lines = [
        (
            "Spoofed high score",
            adversarial["root_decisions"]["spoofed_high_similarity_score"],
        ),
        (
            "Fake freshness",
            adversarial["root_decisions"]["fake_freshness_on_stale_record"],
        ),
        (
            "Quarantine laundering",
            adversarial["root_decisions"]["quarantine_laundering_attempt"],
        ),
        (
            "Deadend laundering",
            adversarial["root_decisions"]["deadend_laundering_attempt"],
        ),
        (
            "Permission laundering",
            adversarial["root_decisions"]["permission_laundering_attempt"],
        ),
        (
            "Domain camouflage",
            adversarial["root_decisions"]["domain_camouflage_attempt"],
        ),
        (
            "Fake audit hash",
            adversarial["root_decisions"]["fake_audit_hash_attempt"],
        ),
        (
            "Injected Root Final",
            adversarial["root_decisions"]["root_final_injection_attempt"],
        ),
    ]

    lines = [
        "HEDGEHOG OS — HUMAN APPLIED AUDITOR WALKTHROUGH",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over completed deterministic proof layers. "
        "It explains observed behavior without creating a new proof layer or capability.",
        "",
        "Nothing here performs a real external action, calls Gemini, uses the network, "
        "or creates production persistence. Root remains the final authority.",
        "",
        "2. ACT 1 — WAREHOUSE READINESS",
        "",
        f"Warehouse {warehouse['warehouse_id']} is preparing dispatch "
        f"{warehouse['dispatch_id']}. The request asks whether inventory is ready.",
        "",
        "The local stock evidence says water_filter requires 8 units but only 6 are "
        f"available. The shortage is {warehouse['blocking_reason']}.",
        "",
        f"Root result: {warehouse['dispatch_readiness']}. No dispatch, restock, or "
        "external action is executed.",
        "",
        "3. ACT 2 — CERTIFICATE READINESS",
        "",
        f"Application {certificate['application_id']} / request "
        f"{certificate['certificate_request_id']} asks for travel document readiness.",
        "",
        "The insurance_certificate is expired and the payment_receipt is missing. "
        "The safe secondary outcome is needs_user_document_update.",
        "",
        f"Root result: {certificate['certificate_readiness']}. No certificate request "
        "is submitted externally.",
        "",
        "4. ACT 3 — PERMISSION / NEEDSUSER",
        "",
        "Permission is not execution. Proof-only approval means permission may be ready "
        "for a future action layer; it does not mean an action completed.",
        "",
        "User denial keeps the action blocked. needs_user is a safe request for missing "
        "input, not a failure. A completed-action claim without execution evidence is rejected.",
        "",
        "5. ACT 4 — NEEDLECANDIDATE",
        "",
        "Safe repeated patterns may become bounded NeedleCandidate objects for Root review.",
        "",
        f"The warehouse candidate may only {needlecandidate['warehouse_action_class']}. "
        f"The certificate candidate may only {needlecandidate['certificate_action_class']}.",
        "",
        f"They remain {needlecandidate['candidate_status']}. NeedleCandidate is not an "
        "installed Needle, GT cannot install needles, Root review is required, and no "
        "production NeedleFactory exists.",
        "",
        "6. ACT 5 — APPLIED DRS RETRIEVAL / REUSE",
        "",
        "A similar warehouse request W-18 / D-2043 appears. DRS retrieves prior "
        "W-17 / D-2042 experience, and ReuseScore suggests bounded partial reuse.",
        "",
        f"Root decision: {retrieval['warehouse_root_decision']}. A similar certificate "
        f"request becomes {retrieval['certificate_root_decision']}.",
        "",
        "Semantic similarity is not authority. ReuseScore is not Root. Retrieval may "
        "propose reuse, but it cannot create direct ready.",
        "",
        "7. ACT 6 — ADVERSARIAL DRS STRESS",
        "",
        "Hostile DRS records try to force reuse through spoofed scores, false freshness, "
        "laundered quarantine/deadend/permission evidence, domain camouflage, a fake audit "
        "hash, and an injected Root Final.",
        "",
    ]
    lines.extend(f"- {label}: {decision}" for label, decision in attack_lines)
    lines.extend(
        [
            "",
            f"All {adversarial['scenarios_verified']} adversarial scenarios are blocked "
            "or downgraded. Memory cannot force Root.",
            "",
            "8. ACT 7 — ALL-LAYERS ROOT VIEW",
            "",
            f"The auditor super-smoke observes {super_smoke['layers_observed']} applied "
            f"layers. All source statuses are PASS: "
            f"{str(super_smoke['source_statuses_all_pass']).lower()}.",
            "",
            "Root is final authority. DRS retrieval, ReuseScore, GT, ConflictCheck, "
            "Audit/hash-chain, and NeedleCandidate are not final authority. Permission "
            "approval is not a completed action.",
            "",
            "9. FINAL HUMAN SUMMARY",
            "",
            "The system can use prior experience, but it does not trust prior experience blindly.",
            "The system can propose reuse, but it cannot execute without Root and permission.",
            "The system blocks poisoned, stale, quarantined, deadend, and wrong-domain memory.",
            "The system remains deterministic local proof only.",
            "It is not production, not external DRS, not Marennya, and not UP.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_human_applied_auditor_walkthrough() -> str:
    return render_human_applied_auditor_walkthrough(
        collect_human_applied_auditor_walkthrough()
    )


def main() -> int:
    print(run_human_applied_auditor_walkthrough(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
