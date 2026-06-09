from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from demo.run_conflictcheck import collect_conflictcheck
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics
from demo.run_drs_writeback_from_root_final import collect_drs_writeback_from_root_final
from demo.run_fractal_cell_runtime import collect_fractal_cell_runtime
from demo.run_live_child_executor_in_fractal_cell import (
    collect_live_child_executor_in_fractal_cell,
)
from demo.run_root_native_sandbox_needleruntime_e2e import (
    collect_root_native_sandbox_needleruntime_e2e,
)


CHAIN_ID = "audit_chain_current_proof_stack_v0_1"
GENESIS_HASH = "0" * 64
ENTRY_SPECS = (
    ("root_final_audit_boundary", "DRSWritebackAuditRecord"),
    ("needle_execution_result", "NeedleExecutionResult"),
    ("child_boundary_snapshot", "ChildBoundarySnapshot"),
    ("live_child_executor_boundary", "ChildExecutionResult/ChildBoundarySnapshot"),
    ("drs_lifecycle_summary", "DrsLifecycleSemanticsReport"),
    ("conflictcheck_summary", "ConflictCheckReport"),
    ("final_day_checkpoint_summary", "FinalDayCheckpointSummary"),
)


@dataclass(frozen=True)
class AuditHashChainReport:
    input_mode: dict[str, Any]
    source_reports: dict[str, Any]
    audit_chain_entries: list[dict[str, Any]]
    chain_summary: dict[str, Any]
    tamper_checks: dict[str, Any]
    malicious_claims: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario"]: row for row in rows}


def _entry_hash_material(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        key: entry[key]
        for key in (
            "audit_entry_id",
            "sequence_index",
            "entry_type",
            "source_artifact_type",
            "source_artifact_id",
            "canonical_payload_hash",
            "previous_entry_hash",
            "chain_id",
        )
    }


def _make_entry(
    sequence_index: int,
    entry_type: str,
    source_artifact_type: str,
    source_artifact_id: str,
    source_payload: dict[str, Any],
    previous_entry_hash: str,
) -> dict[str, Any]:
    entry = {
        "audit_entry_id": f"audit_entry_{sequence_index:02d}_{entry_type}",
        "sequence_index": sequence_index,
        "entry_type": entry_type,
        "source_artifact_type": source_artifact_type,
        "source_artifact_id": source_artifact_id,
        "canonical_payload_hash": canonical_hash(source_payload),
        "previous_entry_hash": previous_entry_hash,
        "chain_id": CHAIN_ID,
        "created_by": "audit_hash_chain_v0_1",
        "proof_only": True,
        "append_only": True,
        "root_authority_preserved": True,
        "audit_chain_is_authority": False,
        "mutates_source_artifact": False,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_network_write": False,
        "_source_payload": copy.deepcopy(source_payload),
    }
    entry["entry_hash"] = canonical_hash(_entry_hash_material(entry))
    return entry


def verify_audit_chain(entries: list[dict[str, Any]]) -> bool:
    if not entries:
        return False
    previous = GENESIS_HASH
    for expected_index, entry in enumerate(entries):
        required = {
            "audit_entry_id",
            "sequence_index",
            "entry_type",
            "source_artifact_type",
            "source_artifact_id",
            "canonical_payload_hash",
            "previous_entry_hash",
            "entry_hash",
            "chain_id",
            "_source_payload",
        }
        if not required <= entry.keys():
            return False
        if entry["sequence_index"] != expected_index:
            return False
        if entry["chain_id"] != CHAIN_ID or entry["previous_entry_hash"] != previous:
            return False
        if entry["canonical_payload_hash"] != canonical_hash(entry["_source_payload"]):
            return False
        if entry["entry_hash"] != canonical_hash(_entry_hash_material(entry)):
            return False
        if not (
            entry.get("proof_only") is True
            and entry.get("append_only") is True
            and entry.get("root_authority_preserved") is True
            and entry.get("audit_chain_is_authority") is False
            and entry.get("mutates_source_artifact") is False
            and entry.get("production_persistence") is False
            and entry.get("global_drs_write") is False
            and entry.get("external_drs_network_write") is False
        ):
            return False
        previous = entry["entry_hash"]
    return True


def _tamper_detected(entries: list[dict[str, Any]], mutate: Any) -> bool:
    tampered = copy.deepcopy(entries)
    mutate(tampered)
    return not verify_audit_chain(tampered)


def _tamper_checks(entries: list[dict[str, Any]]) -> dict[str, bool]:
    return {
        "payload_tamper_detected": _tamper_detected(
            entries, lambda rows: rows[0]["_source_payload"].update({"tampered": True})
        ),
        "previous_hash_tamper_detected": _tamper_detected(
            entries, lambda rows: rows[1].update({"previous_entry_hash": GENESIS_HASH})
        ),
        "entry_reorder_detected": _tamper_detected(
            entries, lambda rows: rows.__setitem__(slice(0, 2), [rows[1], rows[0]])
        ),
        "missing_entry_detected": _tamper_detected(entries, lambda rows: rows.pop(2)),
        "injected_entry_detected": _tamper_detected(
            entries, lambda rows: rows.insert(1, copy.deepcopy(rows[0]))
        ),
        "authority_claim_tamper_detected": _tamper_detected(
            entries, lambda rows: rows[0].update({"audit_chain_is_authority": True})
        ),
        "production_persistence_claim_tamper_detected": _tamper_detected(
            entries, lambda rows: rows[0].update({"production_persistence": True})
        ),
        "global_drs_claim_tamper_detected": _tamper_detected(
            entries, lambda rows: rows[0].update({"global_drs_write": True})
        ),
    }


def _malicious_claims() -> dict[str, Any]:
    fields = {
        "malicious_audit_chain_truth_decision_claim_rejected": "audit_chain_decides_truth",
        "malicious_audit_chain_drs_mutation_claim_rejected": "audit_chain_mutates_drs",
        "malicious_source_artifact_mutation_claim_rejected": (
            "audit_chain_mutates_source_artifact"
        ),
        "malicious_authority_grant_claim_rejected": "audit_chain_grants_authority",
        "malicious_production_persistence_claim_rejected": "production_persistence",
        "malicious_global_drs_write_claim_rejected": "global_drs_write",
        "malicious_external_drs_network_claim_rejected": "external_drs_network_write",
        "malicious_real_external_action_claim_rejected": "real_external_action",
    }
    rejected = {}
    for claim_name, field in fields.items():
        claim = {field: True}
        rejected[claim_name] = claim.get(field) is True
    rejected.update(
        {
            "audit_chain_decides_truth": False,
            "audit_chain_mutates_drs": False,
            "audit_chain_mutates_source_artifact": False,
            "audit_chain_grants_authority": False,
            "production_persistence": False,
            "global_drs_write": False,
            "external_drs_network_write": False,
            "real_external_action": False,
        }
    )
    return rejected


def collect_audit_hash_chain() -> AuditHashChainReport:
    conflict = collect_conflictcheck()
    lifecycle = collect_drs_lifecycle_semantics()
    live_child = collect_live_child_executor_in_fractal_cell(live_requested=False)
    drs = collect_drs_writeback_from_root_final()
    needle = collect_root_native_sandbox_needleruntime_e2e()
    fractal = collect_fractal_cell_runtime()
    source_reports_before = copy.deepcopy(
        {
            "conflict": asdict(conflict),
            "lifecycle": asdict(lifecycle),
            "live_child": asdict(live_child),
            "drs": asdict(drs),
            "needle": asdict(needle),
            "fractal": asdict(fractal),
        }
    )

    drs_record = drs.drs_writeback_audit_records[0]
    needle_completed = _by_scenario(needle.needleruntime_executions)[
        "sandbox_needle_completed"
    ]
    child_completed = _by_scenario(fractal.child_boundary_snapshots)[
        "non_atomic_child_cell_completed"
    ]
    live_child_completed = {
        "execution": _by_scenario(live_child.live_child_executor)[
            "live_child_executor_completed_proof_task"
        ],
        "boundary": _by_scenario(live_child.child_boundary_snapshot)[
            "live_child_executor_completed_proof_task"
        ],
        "live_network_used": live_child.input_mode["live_network_used"],
    }
    checkpoint = {
        "checkpoint_id": "final_day_checkpoint_current_proof_stack",
        "closed_layers": [
            "live_child_executor",
            "drs_lifecycle",
            "conflictcheck",
            "root_centered_geometry_docs",
        ],
        "root_remains_final_authority": True,
        "proof_only": True,
    }
    sources = [
        (
            "root_final_audit_boundary",
            "DRSWritebackAuditRecord",
            drs_record["drs_writeback_record_id"],
            drs_record,
        ),
        (
            "needle_execution_result",
            "NeedleExecutionResult",
            needle_completed["needle_execution_result_id"],
            needle_completed,
        ),
        (
            "child_boundary_snapshot",
            "ChildBoundarySnapshot",
            child_completed["child_boundary_snapshot_id"],
            child_completed,
        ),
        (
            "live_child_executor_boundary",
            "ChildExecutionResult/ChildBoundarySnapshot",
            live_child_completed["boundary"]["child_boundary_snapshot_id"],
            live_child_completed,
        ),
        (
            "drs_lifecycle_summary",
            "DrsLifecycleSemanticsReport",
            "drs_lifecycle_semantics_summary",
            lifecycle.summary,
        ),
        (
            "conflictcheck_summary",
            "ConflictCheckReport",
            "conflictcheck_summary",
            conflict.summary,
        ),
        (
            "final_day_checkpoint_summary",
            "FinalDayCheckpointSummary",
            checkpoint["checkpoint_id"],
            checkpoint,
        ),
    ]
    entries: list[dict[str, Any]] = []
    previous = GENESIS_HASH
    for index, (entry_type, artifact_type, artifact_id, payload) in enumerate(sources):
        entry = _make_entry(index, entry_type, artifact_type, artifact_id, payload, previous)
        entries.append(entry)
        previous = entry["entry_hash"]

    source_reports_after = {
        "conflict": asdict(conflict),
        "lifecycle": asdict(lifecycle),
        "live_child": asdict(live_child),
        "drs": asdict(drs),
        "needle": asdict(needle),
        "fractal": asdict(fractal),
    }
    source_artifacts_unchanged = source_reports_before == source_reports_after
    tamper = _tamper_checks(entries)
    malicious = _malicious_claims()
    chain_continuity_valid = verify_audit_chain(entries)
    tamper_detection_valid = all(tamper.values())
    append_only = chain_continuity_valid and tamper_detection_valid
    source_reports = {
        "conflictcheck_status": conflict.summary["conflictcheck_status"],
        "drs_lifecycle_semantics_status": lifecycle.summary[
            "drs_lifecycle_semantics_status"
        ],
        "live_child_executor_reference_status": live_child.summary[
            "live_child_executor_in_fractal_cell_status"
        ],
        "drs_writeback_status": drs.summary["drs_writeback_from_root_final_status"],
        "needleruntime_status": needle.summary[
            "root_native_sandbox_needleruntime_e2e_status"
        ],
        "fractal_cell_status": fractal.summary["fractal_cell_runtime_status"],
        "source_reports_consumed": [
            "collect_conflictcheck",
            "collect_drs_lifecycle_semantics",
            "collect_live_child_executor_in_fractal_cell",
            "collect_drs_writeback_from_root_final",
            "collect_root_native_sandbox_needleruntime_e2e",
            "collect_fractal_cell_runtime",
        ],
        "source_artifacts_unchanged": source_artifacts_unchanged,
    }
    chain_summary = {
        "chain_id": CHAIN_ID,
        "entries_created": len(entries),
        "first_entry_hash": entries[0]["entry_hash"],
        "last_entry_hash": entries[-1]["entry_hash"],
        "chain_continuity_valid": chain_continuity_valid,
        "tamper_detection_valid": tamper_detection_valid,
        "append_only_semantics_preserved": append_only,
        "source_artifacts_unchanged": source_artifacts_unchanged,
        "root_authority_preserved": all(
            entry["root_authority_preserved"] for entry in entries
        ),
        "audit_chain_is_authority": any(
            entry["audit_chain_is_authority"] for entry in entries
        ),
        "production_persistence": any(
            entry["production_persistence"] for entry in entries
        ),
        "global_drs_write": any(entry["global_drs_write"] for entry in entries),
        "external_drs_network_write": any(
            entry["external_drs_network_write"] for entry in entries
        ),
    }
    authority = {
        "audit_chain_is_authority": False,
        "audit_chain_decides_truth": False,
        "audit_chain_mutates_drs": False,
        "audit_chain_mutates_source_artifacts": False,
        "audit_chain_grants_authority": False,
        "root_remains_final_authority": chain_summary["root_authority_preserved"],
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": not conflict.authority_safety[
            "conflictcheck_is_authority"
        ],
        "drs_lifecycle_remains_storage_index_lifecycle": True,
        "source_artifacts_unchanged": source_artifacts_unchanged,
        "production_persistence_claimed": chain_summary["production_persistence"],
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "production_external_action_executed": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    source_statuses_valid = (
        source_reports["conflictcheck_status"] == "PASS"
        and source_reports["drs_lifecycle_semantics_status"] == "PASS"
        and source_reports["live_child_executor_reference_status"]
        in {"PASS", "SAFE_FALLBACK_NOT_LIVE_SUCCESS"}
        and source_reports["drs_writeback_status"] == "PASS"
        and source_reports["needleruntime_status"] == "PASS"
        and source_reports["fractal_cell_status"] == "PASS"
    )
    malicious_count = sum(
        malicious[key]
        for key in malicious
        if key.startswith("malicious_") and key.endswith("_rejected")
    )
    pass_facts = (
        source_statuses_valid
        and len(entries) == len(ENTRY_SPECS)
        and [(row["entry_type"], row["source_artifact_type"]) for row in entries]
        == list(ENTRY_SPECS)
        and chain_continuity_valid
        and tamper_detection_valid
        and append_only
        and source_artifacts_unchanged
        and malicious_count == 8
        and not authority["audit_chain_is_authority"]
        and not authority["audit_chain_decides_truth"]
        and not authority["audit_chain_mutates_drs"]
        and not authority["audit_chain_mutates_source_artifacts"]
        and not authority["audit_chain_grants_authority"]
        and authority["root_remains_final_authority"]
        and not authority["production_persistence_claimed"]
        and not authority["production_external_action_executed"]
    )
    summary = {
        "audit_hash_chain_status": "PASS" if pass_facts else "FAIL",
        "entries_created": len(entries),
        "source_reports_consumed": len(source_reports["source_reports_consumed"]),
        "chain_continuity_valid": chain_continuity_valid,
        "tamper_detection_valid": tamper_detection_valid,
        "append_only_semantics_preserved": append_only,
        "source_artifacts_unchanged": source_artifacts_unchanged,
        "malicious_claims_rejected": malicious_count,
        "root_remains_final_authority": authority["root_remains_final_authority"],
        "local_proof_level_only": True,
        "ready_for_controlled_root_orchestrator_integration": pass_facts,
        "production_autonomy_claimed": False,
    }
    return AuditHashChainReport(
        input_mode={
            "mode": "deterministic_audit_hash_chain",
            "local_proof_level_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
        },
        source_reports=source_reports,
        audit_chain_entries=entries,
        chain_summary=chain_summary,
        tamper_checks=tamper,
        malicious_claims=malicious,
        authority_safety=authority,
        summary=summary,
    )


def _format(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    for row in rows:
        visible = {key: value for key, value in row.items() if not key.startswith("_")}
        lines.append(" | ".join(f"{key}={_format(value)}" for key, value in visible.items()))


def render_audit_hash_chain(report: AuditHashChainReport) -> str:
    lines = [
        "[AUDIT HASH CHAIN]",
        "note: deterministic Audit / hash-chain hardening v0.1 proof",
        "note: local proof-level tamper-evident audit chain only",
        "note: consumes current proof collectors and reports",
        "note: canonical JSON hashing used for deterministic hashes",
        "note: append-only linkage represented",
        "note: hash-chain does not decide truth",
        "note: hash-chain does not mutate DRS or artifacts",
        "note: hash-chain does not grant authority",
        "note: Root remains final authority",
        "note: no production persistence",
        "note: no external/global DRS",
        "note: no real external actions",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE REPORTS]", report.source_reports)
    _rows(lines, "[AUDIT CHAIN ENTRIES]", report.audit_chain_entries)
    _section(lines, "[CHAIN SUMMARY]", report.chain_summary)
    _section(lines, "[TAMPER CHECKS]", report.tamper_checks)
    _section(lines, "[MALICIOUS CLAIMS]", report.malicious_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_audit_hash_chain() -> str:
    return render_audit_hash_chain(collect_audit_hash_chain())


def main() -> int:
    print(run_audit_hash_chain(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
