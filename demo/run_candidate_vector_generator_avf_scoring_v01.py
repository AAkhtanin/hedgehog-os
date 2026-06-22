from __future__ import annotations

from tempfile import TemporaryDirectory
from typing import Any

from hedgehog.candidate_vector_generator import (
    CandidateVectorReport,
    build_avf_candidate_report,
    candidate_inputs_from_resolved_report,
)
from hedgehog.drs import LocalDRS
from hedgehog.local_drs_resolver import (
    SemanticDRSRecordInput,
    SemanticResolveQuery,
    resolve_semantic_candidates,
    write_semantic_record,
)


TITLE = "HEDGEHOG OS — CANDIDATE VECTOR GENERATOR + REAL AVF SCORING v0.1"
NOW = "2026-06-22T12:00:00+00:00"
OLD = "2026-01-01T00:00:00+00:00"

SCENARIOS = (
    "drs_resolved_candidates_generate_candidate_vectors",
    "exact_domain_and_claim_match_scores_higher_but_not_authority",
    "stale_candidate_gets_review_required_penalty",
    "quarantine_deadend_candidate_blocked_from_top_reuse",
    "conflicting_provenance_penalizes_or_blocks_candidate",
    "duplicate_spam_candidates_do_not_win_by_volume",
    "high_score_candidate_still_requires_gt_lgt_root_review",
    "schema_valid_vector_is_not_semantic_truth",
    "root_final_authority_preserved_across_avf_scoring",
)

COMPACT_RULE = (
    "Candidate vector is not truth",
    "Candidate vector is not authority",
    "AVF score is not authority",
    "Top-ranked candidate is not action permission",
    "Top-ranked candidate is not direct reuse permission",
    "DRS hit is not authority",
    "DRS reuse candidate is not action permission",
    "AVF ranking can influence review/routing only",
    "GT/LGT remains advisory",
    "Root remains final authority",
)


def _time_envelope(created_at: str = NOW, freshness_class: str = "normal") -> dict[str, Any]:
    return {
        "pt_created_at": created_at,
        "kt_asof": created_at,
        "et_observed_at": created_at,
        "ct_session_anchor": "sess_candidate_vector_generator_avf_v01",
        "ttl_seconds": 86_400,
        "freshness_class": freshness_class,
        "valid_from": created_at,
        "valid_to": None,
    }


def _temporal_query() -> dict[str, Any]:
    return {
        "as_of": NOW,
        "time_range": {"from": None, "to": NOW},
        "freshness_bias": "prefer_recent",
        "max_age_seconds": 86_400,
        "freshness_required": "normal",
    }


def _trace(trace_id: str) -> dict[str, str]:
    return {"trace_id": trace_id, "kind": "candidate_vector_generator_avf_v01"}


def _source(source_id: str, trace_id: str) -> dict[str, Any]:
    return {
        "source": "local_drs",
        "source_id": source_id,
        "trace_ref": _trace(trace_id),
    }


def _write_record(
    drs: LocalDRS,
    records_by_id: dict[str, dict[str, Any]],
    *,
    record_id: str,
    summary: str = "Root-reviewed certificate renewal memory.",
    subject_key: str = "certificate:demo-user",
    claim_key: str | None = "document_readiness",
    claim_value: str = "ready",
    created_at: str = NOW,
    freshness_class: str = "normal",
    layer: str = "work",
    status: str = "accepted",
    record_type: str = "task_outcome",
    semantic_keys: tuple[str, ...] = ("certificate", "renewal", "document_readiness"),
    extra_content: dict[str, Any] | None = None,
    source_refs: tuple[dict[str, Any], ...] | None = None,
) -> None:
    content: dict[str, Any] = {
        "summary": summary,
        "subject_key": subject_key,
        "claim_value": claim_value,
        "worldstate": {"worldstate_version": "v1"},
        "schema_valid": True,
    }
    if claim_key is not None:
        content["claim_key"] = claim_key
    if extra_content:
        content.update(extra_content)
    record = write_semantic_record(
        drs,
        SemanticDRSRecordInput(
            record_id=record_id,
            domain="mock_government_certificate",
            content=content,
            semantic_keys=semantic_keys,
            layer=layer,
            record_type=record_type,
            time_envelope=_time_envelope(created_at, freshness_class),
            trace_refs=(_trace(f"trace:{record_id}"),),
            source_refs=source_refs or (_source(f"source:{record_id}", f"trace:{record_id}"),),
            status=status,
        ),
    )
    records_by_id[record_id] = record


def _query(scenario_id: str, *, max_candidates: int = 8) -> SemanticResolveQuery:
    return SemanticResolveQuery(
        query_id=f"query:{scenario_id}",
        domain="mock_government_certificate",
        semantic_terms=("certificate", "renewal", "document_readiness"),
        content_filters={"subject_key": "certificate:demo-user"},
        temporal_query=_temporal_query(),
        worldstate={"worldstate_version": "v1"},
        require_root_review=True,
        max_candidates=max_candidates,
    )


def _build_report(
    drs: LocalDRS,
    records_by_id: dict[str, dict[str, Any]],
    scenario_id: str,
) -> CandidateVectorReport:
    resolved = resolve_semantic_candidates(drs, _query(scenario_id))
    inputs = candidate_inputs_from_resolved_report(resolved, records_by_id=records_by_id)
    return build_avf_candidate_report(inputs)


def _scenario(
    scenario_id: str,
    report: CandidateVectorReport,
    expected_reason: str,
    extra_pass: bool = True,
    note: str = "",
) -> dict[str, Any]:
    reasons = set(report.reason_codes)
    counters = report.counters
    passed = (
        bool(report.candidates)
        and expected_reason in reasons
        and report.direct_reuse_allowed_count == 0
        and counters["action_permission_granted_count"] == 0
        and counters["avf_authority_claimed_count"] == 0
        and counters["vector_truth_claimed_count"] == 0
        and counters["schema_validity_truth_claimed_count"] == 0
        and report.root_final_authority_preserved
        and extra_pass
    )
    return {
        "scenario_id": scenario_id,
        "status": "PASS" if passed else "FAIL",
        "report": report,
        "candidate_vector_count": len(report.candidates),
        "top_candidate_ids": report.top_candidate_ids,
        "reason_codes": report.reason_codes,
        "note": note,
    }


def evaluate_scenario(scenario_id: str) -> dict[str, Any]:
    with TemporaryDirectory(prefix="hedgehog_candidate_vector_avf_") as tmpdir:
        drs = LocalDRS(tmpdir)
        records_by_id: dict[str, dict[str, Any]] = {}

        if scenario_id == "drs_resolved_candidates_generate_candidate_vectors":
            _write_record(drs, records_by_id, record_id="record:fresh_candidate")
            report = _build_report(drs, records_by_id, scenario_id)
            return _scenario(
                scenario_id,
                report,
                "drs_candidate_vector_generated",
                extra_pass=report.counters["candidate_vectors_generated_count"] == 1,
            )

        if scenario_id == "exact_domain_and_claim_match_scores_higher_but_not_authority":
            _write_record(drs, records_by_id, record_id="record:exact_match")
            _write_record(
                drs,
                records_by_id,
                record_id="record:lower_overlap",
                summary="Certificate context memory without explicit claim key.",
                claim_key=None,
                semantic_keys=("certificate",),
            )
            report = _build_report(drs, records_by_id, scenario_id)
            top = report.top_candidate_ids[0] if report.top_candidate_ids else ""
            return _scenario(
                scenario_id,
                report,
                "subject_claim_match_score_applied",
                extra_pass=(
                    top == "candidate:record:exact_match"
                    and report.counters["direct_reuse_allowed_count"] == 0
                ),
                note="exact domain/claim match ranks higher but remains review-only",
            )

        if scenario_id == "stale_candidate_gets_review_required_penalty":
            _write_record(
                drs,
                records_by_id,
                record_id="record:stale_high_overlap",
                created_at=OLD,
                freshness_class="stale",
            )
            report = _build_report(drs, records_by_id, scenario_id)
            return _scenario(
                scenario_id,
                report,
                "stale_direct_reuse_block",
                extra_pass=report.counters["stale_candidate_review_required_count"] == 1,
            )

        if scenario_id == "quarantine_deadend_candidate_blocked_from_top_reuse":
            _write_record(
                drs,
                records_by_id,
                record_id="record:quarantine_candidate",
                layer="quarantine",
                status="quarantined",
                extra_content={"quarantine_proximity": True},
            )
            _write_record(
                drs,
                records_by_id,
                record_id="record:deadend_candidate",
                layer="deadends",
                status="rejected",
                record_type="dead_end",
                extra_content={"deadend_proximity": True},
            )
            report = _build_report(drs, records_by_id, scenario_id)
            return _scenario(
                scenario_id,
                report,
                "quarantine_deadend_direct_reuse_block",
                extra_pass=report.counters["quarantine_deadend_blocked_count"] == 2,
            )

        if scenario_id == "conflicting_provenance_penalizes_or_blocks_candidate":
            _write_record(
                drs,
                records_by_id,
                record_id="record:conflicting_provenance",
                extra_content={"conflicting_provenance": True},
            )
            report = _build_report(drs, records_by_id, scenario_id)
            return _scenario(
                scenario_id,
                report,
                "conflicting_provenance_penalty",
                extra_pass=report.counters["conflicting_provenance_penalized_count"] == 1,
            )

        if scenario_id == "duplicate_spam_candidates_do_not_win_by_volume":
            _write_record(drs, records_by_id, record_id="record:clean_candidate")
            for suffix in ("a", "b"):
                _write_record(
                    drs,
                    records_by_id,
                    record_id=f"record:duplicate_spam:{suffix}",
                    extra_content={
                        "duplicate_group": "poisoned_certificate_reuse",
                        "poisoning_markers": ["duplicate_spam"],
                        "repeated_external_pointer_count": 3,
                    },
                    source_refs=(
                        {
                            "source": "external_drs",
                            "source_id": f"external:pointer:{suffix}",
                            "trace_ref": _trace(f"trace:external_pointer:{suffix}"),
                        },
                    ),
                )
            report = _build_report(drs, records_by_id, scenario_id)
            top = report.top_candidate_ids[0] if report.top_candidate_ids else ""
            return _scenario(
                scenario_id,
                report,
                "duplicate_count_not_authority",
                extra_pass=(
                    report.counters["duplicate_spam_candidates_seen_count"] == 2
                    and top == "candidate:record:clean_candidate"
                ),
            )

        if scenario_id == "high_score_candidate_still_requires_gt_lgt_root_review":
            _write_record(drs, records_by_id, record_id="record:high_score_candidate")
            report = _build_report(drs, records_by_id, scenario_id)
            high_score = report.ranked_candidates[0].score >= 0.75
            return _scenario(
                scenario_id,
                report,
                "high_score_review_required",
                extra_pass=(
                    high_score
                    and report.counters["gt_lgt_review_required_count"] == 1
                    and report.counters["root_review_required_count"] == 1
                ),
            )

        if scenario_id == "schema_valid_vector_is_not_semantic_truth":
            _write_record(
                drs,
                records_by_id,
                record_id="record:schema_valid_risky",
                extra_content={
                    "schema_valid": True,
                    "upstream_looking": True,
                    "poisoning_markers": ["schema_valid_but_risky"],
                },
            )
            report = _build_report(drs, records_by_id, scenario_id)
            return _scenario(
                scenario_id,
                report,
                "schema_valid_vector_is_not_semantic_truth",
                extra_pass=report.counters["schema_validity_truth_claimed_count"] == 0,
            )

        if scenario_id == "root_final_authority_preserved_across_avf_scoring":
            _write_record(drs, records_by_id, record_id="record:composite_clean")
            _write_record(
                drs,
                records_by_id,
                record_id="record:composite_stale",
                created_at=OLD,
                freshness_class="stale",
            )
            _write_record(
                drs,
                records_by_id,
                record_id="record:composite_conflict",
                extra_content={"conflicting_provenance": True},
            )
            _write_record(
                drs,
                records_by_id,
                record_id="record:composite_quarantine",
                layer="quarantine",
                status="quarantined",
                extra_content={"quarantine_proximity": True},
            )
            _write_record(
                drs,
                records_by_id,
                record_id="record:composite_duplicate",
                extra_content={
                    "duplicate_group": "composite_poisoning",
                    "poisoning_markers": ["duplicate_spam"],
                },
            )
            report = _build_report(drs, records_by_id, scenario_id)
            return _scenario(
                scenario_id,
                report,
                "root_final_authority_preserved_across_avf_scoring",
                extra_pass=(
                    report.counters["direct_reuse_allowed_count"] == 0
                    and report.counters["action_permission_granted_count"] == 0
                    and report.root_final_authority_preserved
                ),
            )

    raise ValueError(f"unknown scenario: {scenario_id}")


def _empty_counters() -> dict[str, int]:
    return {
        "drs_candidates_input_count": 0,
        "candidate_vectors_generated_count": 0,
        "avf_scores_computed_count": 0,
        "ranked_candidates_count": 0,
        "top_ranked_candidates_count": 0,
        "direct_reuse_allowed_count": 0,
        "action_permission_granted_count": 0,
        "avf_authority_claimed_count": 0,
        "vector_truth_claimed_count": 0,
        "schema_validity_truth_claimed_count": 0,
        "stale_candidate_review_required_count": 0,
        "quarantine_deadend_blocked_count": 0,
        "conflicting_provenance_penalized_count": 0,
        "duplicate_spam_candidates_seen_count": 0,
        "duplicate_spam_authority_claimed_count": 0,
        "high_score_direct_reuse_granted_count": 0,
        "gt_lgt_review_required_count": 0,
        "root_review_required_count": 0,
        "manifest_mutation_count": 0,
        "transition_matrix_mutation_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "root_final_authority_preserved_count": 0,
    }


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIOS]
    counters = _empty_counters()
    for scenario in scenarios:
        report = scenario["report"]
        for key, value in report.counters.items():
            if key in counters and key != "root_final_authority_preserved_count":
                counters[key] += value
        counters["root_final_authority_preserved_count"] += int(
            report.root_final_authority_preserved
        )

    scenarios_passed = sum(1 for scenario in scenarios if scenario["status"] == "PASS")
    pass_conditions = {
        "scenarios_total_is_9": len(scenarios) == 9,
        "scenarios_passed": scenarios_passed == len(scenarios),
        "direct_reuse_allowed_count_zero": counters["direct_reuse_allowed_count"] == 0,
        "action_permission_granted_count_zero": (
            counters["action_permission_granted_count"] == 0
        ),
        "avf_authority_claimed_count_zero": counters["avf_authority_claimed_count"] == 0,
        "vector_truth_claimed_count_zero": counters["vector_truth_claimed_count"] == 0,
        "schema_validity_truth_claimed_count_zero": (
            counters["schema_validity_truth_claimed_count"] == 0
        ),
        "duplicate_spam_authority_claimed_count_zero": (
            counters["duplicate_spam_authority_claimed_count"] == 0
        ),
        "high_score_direct_reuse_granted_count_zero": (
            counters["high_score_direct_reuse_granted_count"] == 0
        ),
        "manifest_mutation_count_zero": counters["manifest_mutation_count"] == 0,
        "transition_matrix_mutation_count_zero": (
            counters["transition_matrix_mutation_count"] == 0
        ),
        "network_used_count_zero": counters["network_used_count"] == 0,
        "gemini_used_count_zero": counters["gemini_used_count"] == 0,
        "root_final_authority_preserved": (
            counters["root_final_authority_preserved_count"] == len(scenarios)
        ),
    }
    return {
        "title": TITLE,
        "scenarios": scenarios,
        "scenarios_total": len(scenarios),
        "scenarios_passed": scenarios_passed,
        "counters": counters,
        "pass_conditions": pass_conditions,
        "final_status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_all_scenarios()
    lines = [
        TITLE,
        "",
        "compact_rule:",
        *[f"- {line}" for line in COMPACT_RULE],
        "",
        "scenario table:",
        "scenario_id | status | vectors | top_candidate_ids | reasons",
    ]
    for scenario in result["scenarios"]:
        lines.append(
            f"{scenario['scenario_id']} | {scenario['status']} | "
            f"{scenario['candidate_vector_count']} | "
            f"{', '.join(scenario['top_candidate_ids'])} | "
            f"{', '.join(scenario['reason_codes'])}"
        )
    lines.extend(["", "aggregate counters:"])
    lines.append(f"scenarios_total: {result['scenarios_total']}")
    lines.append(f"scenarios_passed: {result['scenarios_passed']}")
    for key in sorted(result["counters"]):
        lines.append(f"{key}: {result['counters'][key]}")
    lines.extend(
        [
            "",
            "authority boundary summary:",
            "Candidate vector is not truth",
            "Candidate vector is not authority",
            "AVF score is not authority",
            "Top-ranked candidate is not action permission",
            "Top-ranked candidate is not direct reuse permission",
            "DRS hit is not authority",
            "DRS reuse candidate is not action permission",
            "GT/LGT remains advisory",
            "Root remains final authority",
            "",
            "limitations:",
            "local deterministic runtime adapter only",
            "no production AVF",
            "no production DRS",
            "no external/global DRS",
            "no network",
            "no Gemini",
            "no embeddings",
            "no LLM semantic matching",
            "no autonomous action",
            "no connector side effects",
            "no manifest mutation",
            "no transition matrix mutation",
            "Real Semantic Runtime MVP is not complete",
            "",
            f"FINAL STATUS: {result['final_status']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_all_scenarios()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
