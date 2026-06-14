from __future__ import annotations

from demo.run_read_only_enterprise_connector_sandbox_v01 import (
    collect_read_only_enterprise_connector_sandbox_v01,
)


def render_human_read_only_enterprise_connector_sandbox_walkthrough_v01(
    report,
) -> str:
    source = report.source_evidence
    requests = {row["connector_domain"]: row for row in report.connector_requests}
    observations = {row["scenario_id"]: row for row in report.connector_observations}
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    root = report.root_final
    summary = report.summary

    lines = [
        "HEDGEHOG OS — HUMAN READ-ONLY ENTERPRISE CONNECTOR SANDBOX WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Read-only Enterprise "
        "Connector Sandbox v0.1 proof.",
        "",
        "It observes four local deterministic read-only connector domains: bank_source, "
        "legal_registry_source, warehouse_source, and logistics_source.",
        "",
        "These connectors are local deterministic mock/read-only stubs. There is no "
        "real network or API access, Gemini, Telegram, Marennya, UP, production "
        "persistence, action, DRS write, or External Evidence Acceptance Gate.",
        "",
        "2. WHY THIS LAYER EXISTS",
        "",
        "External DRS Pointer Protocol proved that external pointer claims cannot "
        "become truth or trusted evidence.",
        "",
        "This layer adds the first enterprise-style external source boundary. External "
        "sources can be read as observations, but observations do not become truth or "
        "authority.",
        "",
        "This is a necessary step toward the future Enterprise Killer Demo, but it is "
        "not that demo. It prepares the next required layer: External Evidence "
        "Acceptance Gate v0.1.",
        "",
        "3. SOURCE EVIDENCE MODE",
        "",
        "The prior External DRS Pointer Protocol checkpoint is referenced as closed "
        "checkpoint metadata.",
        "",
        f"source_evidence_mode={source['source_evidence_mode']}.",
        f"source_collectors_replayed={str(source['source_collectors_replayed']).lower()}.",
        "",
        "This is targeted proof runtime hygiene, not full historical replay. Full "
        "historical replay belongs to explicit audit or super-smoke modes.",
        "",
        "4. CONNECTOR REQUESTS",
        "",
        f"bank_source requests {requests['bank_source']['requested_signal']}: bank "
        "payment status.",
        f"legal_registry_source requests "
        f"{requests['legal_registry_source']['requested_signal']}: legal certificate "
        "status.",
        f"warehouse_source requests {requests['warehouse_source']['requested_signal']}: "
        "warehouse inventory stock.",
        f"logistics_source requests {requests['logistics_source']['requested_signal']}: "
        "logistics dispatch window.",
        "",
        "Every connector request is read_only=true and proof_only=true.",
        "",
        "5. CONNECTOR OBSERVATIONS",
        "",
        "clean_bank_observation reports payment_status: observed_paid with transaction_id "
        "MOCK-TXN-001. It remains observation_only.",
        "",
        "stale_legal_registry_observation reports certificate_status: expired. It is a "
        "blocked_or_quarantined_observation.",
        "",
        "warehouse_stock_observation reports an inventory signal only. It does not "
        "finalize readiness, and its connector result remains not_finalized_by_connector.",
        "",
        "logistics_window_observation reports a dispatch-window signal only. It does "
        "not execute dispatch.",
        "",
        "6. READ-ONLY BOUNDARY",
        "",
        "For bank_source, legal_registry_source, warehouse_source, and logistics_source:",
        "",
        "read_only=true.",
        "state_mutated=false.",
        "drs_written=false.",
        "action_executed=false.",
        "root_bypassed=false.",
        "",
        "7. CONNECTOR BOUNDARY MATRIX",
        "",
        "Connector response is not truth.",
        "Connector response is not authority.",
        "Connector observation is not trusted evidence.",
        "Connector observation is not ready status.",
        "Connector cannot execute action.",
        "Connector cannot write global DRS.",
        "Connector cannot write External DRS.",
        "Connector cannot install Needle.",
        "Connector cannot bypass Root.",
        "Connector cannot bypass ConflictCheck.",
        "Connector cannot bypass GT.",
        "Connector cannot bypass permission or needs_user.",
        "Connector cannot bypass quarantine.",
        "The read-only connector performed no mutation.",
        "",
        "8. SIX ADVERSARIAL ATTEMPTS",
        "",
        f"adversary_connector_claim_to_truth: "
        f"{attempts['adversary_connector_claim_to_truth']['final_effect']}.",
        f"adversary_connector_to_ready_status: "
        f"{attempts['adversary_connector_to_ready_status']['final_effect']}.",
        f"adversary_connector_to_drs_write: "
        f"{attempts['adversary_connector_to_drs_write']['final_effect']}.",
        f"adversary_connector_to_external_action: "
        f"{attempts['adversary_connector_to_external_action']['final_effect']}.",
        f"adversary_connector_to_installed_needle: "
        f"{attempts['adversary_connector_to_installed_needle']['final_effect']}.",
        f"adversary_unknown_connector_laundering: "
        f"{attempts['adversary_unknown_connector_laundering']['final_effect']}.",
        "",
        f"{summary['adversarial_attempts_observed']} attempts were observed and "
        f"{summary['adversarial_attempts_blocked']} were blocked. "
        f"{summary['quarantined_attempts_observed']} attempt was quarantined and blocked.",
        "",
        "No trusted evidence, truth, ready status, external action, DRS write, installed "
        "Needle, production persistence, or network call was created.",
        "",
        "9. CONFLICTCHECK AND GT",
        "",
        f"ConflictCheck detects {conflict['conflict_count']} connector escalation "
        "conflicts. ConflictCheck is not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT is advisory. GT cannot mark an "
        "observation trusted, mark truth, execute action, write External DRS, or install "
        "a Needle.",
        "",
        "10. ROOT FINAL",
        "",
        f"root_result: {root['root_result']}.",
        f"safe_secondary_outcome: {root['safe_secondary_outcome']}.",
        f"connector observations created: {root['connector_observations_created']}.",
        "",
        "trusted_evidence_created=false.",
        "truth_proven=false.",
        "ready_status_created=false.",
        "external_action_executed=false.",
        "global_drs_write=false.",
        "external_drs_write=false.",
        "installed_needle_created=false.",
        "production_persistence=false.",
        "network_called=false.",
        "root_remains_final_authority=true.",
        "",
        "11. WHAT THIS PROVES",
        "",
        "Enterprise-style external source responses can be represented as read-only "
        "observations. Clean connector output still does not become trusted evidence.",
        "",
        "Stale connector output is blocked or quarantined. Adversarial escalation "
        "attempts are blocked, and unknown connector laundering is quarantined and "
        "blocked.",
        "",
        "This establishes the observation boundary needed before External Evidence "
        "Acceptance Gate v0.1.",
        "",
        "12. WHAT THIS DOES NOT PROVE",
        "",
        "It does not implement real connector/API access, call network or Gemini, or "
        "implement External Evidence Acceptance Gate.",
        "",
        "It does not accept evidence, prove truth, create ready status, write DRS, "
        "execute action, install a Needle, implement External DRS, grant production "
        "autonomy, or invoke Marennya or UP.",
        "",
        "13. FINAL HUMAN SUMMARY",
        "",
        "Four read-only connector observations were created.",
        "Six connector escalation attempts were blocked.",
        "Unknown-source laundering was quarantined and blocked.",
        "Connector response is not truth.",
        "Connector response is not authority.",
        "Connector observation is not trusted evidence.",
        "Root remains final authority.",
        "Next required layer is External Evidence Acceptance Gate v0.1.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_read_only_enterprise_connector_sandbox_walkthrough_v01() -> str:
    return render_human_read_only_enterprise_connector_sandbox_walkthrough_v01(
        collect_read_only_enterprise_connector_sandbox_v01()
    )


def main() -> int:
    print(run_human_read_only_enterprise_connector_sandbox_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
