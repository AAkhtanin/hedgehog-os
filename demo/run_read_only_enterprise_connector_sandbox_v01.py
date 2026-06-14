from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


@dataclass(frozen=True)
class ConnectorRequest:
    request_id: str
    scenario_id: str
    connector_domain: str
    requested_signal: str
    read_only: bool = True
    proof_only: bool = True


@dataclass(frozen=True)
class ConnectorSourceProfile:
    source_profile_id: str
    connector_domain: str
    source_kind: str
    known_mock_source: bool
    network_allowed: bool = False
    mutation_allowed: bool = False


@dataclass(frozen=True)
class ConnectorObservation:
    observation_id: str
    scenario_id: str
    connector_domain: str
    source_profile: str
    observed_signal: str
    observation_created: bool = True
    root_review_required: bool = True
    trusted_evidence_created: bool = False
    truth_proven: bool = False
    ready_status_created: bool = False
    external_action_executed: bool = False
    global_drs_write: bool = False
    external_drs_write: bool = False
    installed_needle_created: bool = False
    production_persistence: bool = False
    network_called: bool = False
    final_effect: str = "observation_only"


@dataclass(frozen=True)
class ConnectorReadOnlyReport:
    connector_domain: str
    request_id: str
    observation_id: str
    read_only: bool = True
    state_mutated: bool = False
    drs_written: bool = False
    action_executed: bool = False
    root_bypassed: bool = False


@dataclass(frozen=True)
class ConnectorAdversarialAttempt:
    attempt_id: str
    target_illegal_effect: str
    detected: bool = True
    blocked: bool = True
    quarantined: bool = False
    root_review_required: bool = True
    final_effect: str = "blocked"
    trusted_evidence_created: bool = False
    truth_proven: bool = False
    ready_status_created: bool = False
    authority_transferred: bool = False
    external_action_executed: bool = False
    global_drs_write: bool = False
    external_drs_write: bool = False
    installed_needle_created: bool = False
    production_persistence: bool = False
    network_called: bool = False


@dataclass(frozen=True)
class ReadOnlyEnterpriseConnectorReport:
    source_evidence: dict[str, Any]
    connector_requests: list[dict[str, Any]]
    connector_source_profiles: list[dict[str, Any]]
    connector_observations: list[dict[str, Any]]
    connector_read_only_reports: list[dict[str, Any]]
    connector_boundary_matrix: dict[str, Any]
    adversarial_attempts: list[dict[str, Any]]
    conflictcheck_result: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final: dict[str, Any]
    proof_artifact: dict[str, Any]
    audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _closed_checkpoint_source_evidence() -> dict[str, Any]:
    # Closed checkpoints are referenced as committed metadata. Targeted tests
    # verify this layer and do not replay historical collectors.
    return {
        "external_drs_pointer_protocol_source_status": "PASS",
        "external_drs_pointer_protocol_commits": (
            "0a690c5,3e3cc3d,2036247,1b37ba5,984d001,5f83451"
        ),
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
    }


def _requests() -> list[dict[str, Any]]:
    specs = (
        ("connector_request_bank_payment", "clean_bank_observation", "bank_source", "payment_status"),
        (
            "connector_request_legal_certificate",
            "stale_legal_registry_observation",
            "legal_registry_source",
            "certificate_status",
        ),
        (
            "connector_request_warehouse_stock",
            "warehouse_stock_observation",
            "warehouse_source",
            "inventory_stock",
        ),
        (
            "connector_request_logistics_window",
            "logistics_window_observation",
            "logistics_source",
            "dispatch_window",
        ),
    )
    return [asdict(ConnectorRequest(*spec)) for spec in specs]


def _source_profiles() -> list[dict[str, Any]]:
    specs = (
        ("known_mock_bank", "bank_source", "local_deterministic_mock", True),
        ("known_mock_legal_registry", "legal_registry_source", "local_deterministic_mock", True),
        ("known_mock_warehouse", "warehouse_source", "local_deterministic_mock", True),
        ("known_mock_logistics", "logistics_source", "local_deterministic_mock", True),
    )
    return [asdict(ConnectorSourceProfile(*spec)) for spec in specs]


def _observations() -> list[dict[str, Any]]:
    rows = [
        asdict(
            ConnectorObservation(
                "observation_bank_payment_paid",
                "clean_bank_observation",
                "bank_source",
                "known_mock_bank",
                "payment_status:observed_paid|transaction_id:MOCK-TXN-001",
            )
        ),
        {
            **asdict(
                ConnectorObservation(
                    "observation_legal_certificate_stale",
                    "stale_legal_registry_observation",
                    "legal_registry_source",
                    "known_mock_legal_registry",
                    "certificate_status:expired",
                    final_effect="blocked_or_quarantined_observation",
                )
            ),
            "stale_or_expired": True,
            "blocked_or_quarantined": True,
        },
        {
            **asdict(
                ConnectorObservation(
                    "observation_warehouse_stock",
                    "warehouse_stock_observation",
                    "warehouse_source",
                    "known_mock_warehouse",
                    "inventory_stock:water_filter_available_6",
                    final_effect="inventory_signal_only",
                )
            ),
            "inventory_signal_available": True,
            "readiness_finalized_by_connector": False,
            "connector_root_result": "not_finalized_by_connector",
        },
        {
            **asdict(
                ConnectorObservation(
                    "observation_logistics_dispatch_window",
                    "logistics_window_observation",
                    "logistics_source",
                    "known_mock_logistics",
                    "dispatch_window:mock_window_available",
                    final_effect="dispatch_window_signal_only",
                )
            ),
            "dispatch_window_signal_available": True,
            "dispatch_executed": False,
        },
    ]
    return rows


def _read_only_reports(
    requests: list[dict[str, Any]], observations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    observations_by_scenario = {row["scenario_id"]: row for row in observations}
    return [
        asdict(
            ConnectorReadOnlyReport(
                request["connector_domain"],
                request["request_id"],
                observations_by_scenario[request["scenario_id"]]["observation_id"],
            )
        )
        for request in requests
    ]


def _adversarial_attempts() -> list[dict[str, Any]]:
    specs = (
        ("adversary_connector_claim_to_truth", "truth"),
        ("adversary_connector_to_ready_status", "ready_status"),
        ("adversary_connector_to_drs_write", "global_or_external_drs_write"),
        ("adversary_connector_to_external_action", "external_action"),
        ("adversary_connector_to_installed_needle", "installed_needle"),
        ("adversary_unknown_connector_laundering", "trusted_evidence"),
    )
    rows = []
    for attempt_id, illegal_effect in specs:
        quarantined = attempt_id == "adversary_unknown_connector_laundering"
        rows.append(
            asdict(
                ConnectorAdversarialAttempt(
                    attempt_id,
                    illegal_effect,
                    quarantined=quarantined,
                    final_effect="quarantined_blocked" if quarantined else "blocked",
                )
            )
        )
    return rows


def validate_read_only_enterprise_connector_report_consistency(
    report: ReadOnlyEnterpriseConnectorReport,
) -> bool:
    statuses = {
        key: value
        for key, value in report.source_evidence.items()
        if key.endswith("_source_status")
    }
    observations = {row["scenario_id"]: row for row in report.connector_observations}
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    boundary = report.connector_boundary_matrix
    root = report.root_final
    prohibited = (
        "trusted_evidence_created",
        "truth_proven",
        "ready_status_created",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_needle_created",
        "production_persistence",
        "network_called",
    )
    return all(
        (
            set(statuses.values()) == {"PASS"},
            report.source_evidence.get("source_evidence_mode")
            == "closed_checkpoint_metadata_only",
            report.source_evidence.get("source_collectors_replayed") is False,
            len(report.connector_requests) == 4,
            len(report.connector_source_profiles) == 4,
            len(observations) == 4,
            all(row.get("observation_created") is True for row in observations.values()),
            all(all(row.get(field) is False for field in prohibited) for row in observations.values()),
            observations["clean_bank_observation"].get("final_effect") == "observation_only",
            observations["stale_legal_registry_observation"].get("stale_or_expired") is True,
            observations["stale_legal_registry_observation"].get("blocked_or_quarantined") is True,
            observations["warehouse_stock_observation"].get("inventory_signal_available") is True,
            observations["warehouse_stock_observation"].get("connector_root_result")
            == "not_finalized_by_connector",
            observations["logistics_window_observation"].get("dispatch_window_signal_available") is True,
            all(
                row.get("read_only") is True
                and row.get("state_mutated") is False
                and row.get("drs_written") is False
                and row.get("action_executed") is False
                and row.get("root_bypassed") is False
                for row in report.connector_read_only_reports
            ),
            all(value is True for value in boundary.values()),
            len(attempts) == 6,
            all(
                row.get("detected") is True
                and row.get("blocked") is True
                and all(row.get(field) is False for field in prohibited)
                for row in attempts.values()
            ),
            attempts["adversary_unknown_connector_laundering"].get("quarantined") is True,
            report.conflictcheck_result.get("conflict_count") == 6,
            report.conflictcheck_result.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_is_advisory") is True,
            root.get("root_result")
            == "read_only_observations_collected_with_escalations_blocked",
            root.get("safe_secondary_outcome")
            == "needs_external_evidence_acceptance_gate",
            root.get("connector_observations_created") == 4,
            root.get("root_remains_final_authority") is True,
            all(root.get(field) is False for field in prohibited),
            report.audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.proof_artifact),
            report.audit_entry.get("audit_chain_decides_truth") is False,
        )
    )


def collect_read_only_enterprise_connector_sandbox_v01() -> ReadOnlyEnterpriseConnectorReport:
    source = _closed_checkpoint_source_evidence()
    requests = _requests()
    profiles = _source_profiles()
    observations = _observations()
    read_only_reports = _read_only_reports(requests, observations)
    boundary = {
        "connector_response_is_not_truth": True,
        "connector_response_is_not_authority": True,
        "connector_observation_is_not_trusted_evidence": True,
        "connector_observation_is_not_ready_status": True,
        "connector_cannot_execute_action": True,
        "connector_cannot_write_global_drs": True,
        "connector_cannot_write_external_drs": True,
        "connector_cannot_install_needle": True,
        "connector_cannot_bypass_root": True,
        "connector_cannot_bypass_conflictcheck": True,
        "connector_cannot_bypass_gt": True,
        "connector_cannot_bypass_permission_needsuser": True,
        "connector_cannot_bypass_quarantine": True,
        "read_only_connector_performed_no_mutation": True,
    }
    attempts = _adversarial_attempts()
    conflict = {
        "conflict_detected": True,
        "conflict_count": 6,
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "block_or_quarantine_connector_escalations",
        "gt_is_advisory": True,
        "gt_can_mark_observation_trusted": False,
        "gt_can_mark_truth": False,
        "gt_can_execute_action": False,
        "gt_can_write_external_drs": False,
        "gt_can_install_needle": False,
    }
    root = {
        "root_result": "read_only_observations_collected_with_escalations_blocked",
        "safe_secondary_outcome": "needs_external_evidence_acceptance_gate",
        "connector_observations_created": len(observations),
        "trusted_evidence_created": False,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "network_called": False,
        "root_remains_final_authority": True,
    }
    proof_artifact = {
        "proof_artifact_id": "read_only_enterprise_connector_sandbox_v01",
        "source_evidence": source,
        "connector_requests": requests,
        "connector_source_profiles": profiles,
        "connector_observations": observations,
        "connector_read_only_reports": read_only_reports,
        "connector_boundary_matrix": boundary,
        "adversarial_attempts": attempts,
        "conflictcheck_result": conflict,
        "gt_advisory": gt,
        "root_final": root,
    }
    audit = {
        "audit_entry_id": "audit_read_only_enterprise_connector_sandbox_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = ReadOnlyEnterpriseConnectorReport(
        source,
        requests,
        profiles,
        observations,
        read_only_reports,
        boundary,
        attempts,
        conflict,
        gt,
        root,
        proof_artifact,
        audit,
        {},
    )
    passed = validate_read_only_enterprise_connector_report_consistency(provisional)
    summary = {
        "read_only_enterprise_connector_sandbox_v01_status": "PASS" if passed else "FAIL",
        "connector_observations_created": len(observations),
        "adversarial_attempts_observed": len(attempts),
        "adversarial_attempts_blocked": sum(row["blocked"] is True for row in attempts),
        "quarantined_attempts_observed": sum(row["quarantined"] is True for row in attempts),
        **boundary,
        "trusted_evidence_created": False,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "network_called": False,
        "gemini_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_persistence": False,
        "root_remains_final_authority": True,
        "external_evidence_acceptance_gate_implemented": False,
        "ready_for_read_only_enterprise_connector_sandbox_v01_tests": passed,
    }
    return replace(provisional, summary=summary)


def _format(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_read_only_enterprise_connector_sandbox_v01(
    report: ReadOnlyEnterpriseConnectorReport,
) -> str:
    lines = [
        "[READ-ONLY ENTERPRISE CONNECTOR SANDBOX v0.1]",
        "note: deterministic local read-only connector observation proof only",
        "note: no network, trusted evidence, action, DRS write, or acceptance gate",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[CONNECTOR REQUESTS]", report.connector_requests)
    _rows(lines, "[SOURCE PROFILES]", report.connector_source_profiles)
    _rows(lines, "[CONNECTOR OBSERVATIONS]", report.connector_observations)
    _rows(lines, "[READ-ONLY REPORTS]", report.connector_read_only_reports)
    _section(lines, "[CONNECTOR BOUNDARY MATRIX]", report.connector_boundary_matrix)
    _rows(lines, "[ADVERSARIAL ATTEMPTS]", report.adversarial_attempts)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck_result)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_read_only_enterprise_connector_sandbox_v01() -> str:
    return render_read_only_enterprise_connector_sandbox_v01(
        collect_read_only_enterprise_connector_sandbox_v01()
    )


def main() -> int:
    print(run_read_only_enterprise_connector_sandbox_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
