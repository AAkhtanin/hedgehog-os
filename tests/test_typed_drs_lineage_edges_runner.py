from __future__ import annotations

from demo.run_typed_drs_lineage_edges import REQUIRED_EDGE_TYPES
from demo.run_typed_drs_lineage_edges import collect_typed_drs_lineage_edges
from demo.run_typed_drs_lineage_edges import run_typed_drs_lineage_edges


def _candidate_by_id(report):
    return {candidate.record["record_id"]: candidate for candidate in report.candidates}


def _edge_by_type(report):
    return {edge.edge_type: edge for edge in report.edges}


def _contains_static_distance_key(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in {"hops_ago", "hop_distance", "graph_distance"}:
                return True
            if _contains_static_distance_key(child):
                return True
    if isinstance(value, list):
        return any(_contains_static_distance_key(child) for child in value)
    return False


def test_runner_output_contains_required_sections():
    output = run_typed_drs_lineage_edges()

    assert "[TYPED DRS LINEAGE EDGES]" in output
    assert "[DATASET]" in output
    assert "[TYPED EDGES]" in output
    assert "[QUERY-TIME INTERPRETATION]" in output
    assert "[POLICY SAFETY]" in output
    assert "[SUMMARY]" in output
    assert "typed_drs_lineage_edges_status: PASS" in output


def test_records_are_written_and_read_from_local_drs(tmp_path):
    report = collect_typed_drs_lineage_edges(tmp_path)

    assert len(report.records) == 10
    assert (tmp_path / "work").exists()
    assert (tmp_path / "quarantine").exists()
    assert (tmp_path / "deadends").exists()
    assert list((tmp_path / "work").glob("*.json"))
    assert {record["record_id"] for record in report.records} == {
        "root_work",
        "child_work",
        "grandchild_work",
        "nearby_dead_end",
        "nearby_blocked_trace",
        "nearby_degraded_trace",
        "nearby_needs_user_trace",
        "nearby_quarantine",
        "supportive_work",
        "unrelated_fresh_work",
    }


def test_every_record_has_time_envelope_and_provenance():
    report = collect_typed_drs_lineage_edges()

    for record in report.records:
        assert record["time_envelope"]
        assert record["provenance"]
        assert record["provenance"]["trace_refs"]


def test_all_required_edge_types_are_present():
    report = collect_typed_drs_lineage_edges()

    assert {edge.edge_type for edge in report.edges} == REQUIRED_EDGE_TYPES
    assert report.summary["edge_types_present"] == 8


def test_typed_edges_are_extracted_from_records():
    report = collect_typed_drs_lineage_edges()
    raw_edges = [
        edge
        for record in report.records
        for edge in record["content"].get("typed_edges", [])
    ]

    assert raw_edges
    assert len(raw_edges) == len(report.edges)
    assert {edge["edge_type"] for edge in raw_edges} == REQUIRED_EDGE_TYPES


def test_graph_distance_is_computed_at_query_time():
    rows = _candidate_by_id(collect_typed_drs_lineage_edges())

    assert rows["root_work"].graph_distance == 0
    assert rows["child_work"].graph_distance == 1
    assert rows["grandchild_work"].graph_distance == 2
    assert rows["unrelated_fresh_work"].graph_distance is None


def test_static_hop_distance_is_not_stored_in_records():
    report = collect_typed_drs_lineage_edges()

    for record in report.records:
        assert not _contains_static_distance_key(record)
    assert report.summary["static_hops_stored_in_records"] is False


def test_supports_edge_contributes_positive_reuse_signal():
    edge = _edge_by_type(collect_typed_drs_lineage_edges())["supports"]

    assert edge.policy_effect == "positive"
    assert edge.contributes_positive_reuse_signal is True
    assert edge.can_make_target_direct_reuse_eligible is False


def test_warns_against_edge_does_not_contribute_positive_reuse_signal():
    edge = _edge_by_type(collect_typed_drs_lineage_edges())["warns_against"]

    assert edge.policy_effect == "warning"
    assert edge.contributes_positive_reuse_signal is False
    assert edge.can_make_target_direct_reuse_eligible is False


def test_blocked_by_policy_edge_produces_blocking_evidence():
    report = collect_typed_drs_lineage_edges()
    edge = _edge_by_type(report)["blocked_by_policy"]
    row = _candidate_by_id(report)["nearby_blocked_trace"]

    assert edge.policy_effect == "blocked"
    assert row.typed_blocking_score > 0
    assert row.final_edge_interpretation == "blocked_signal"


def test_requires_user_edge_produces_needs_user_evidence():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())[
        "nearby_needs_user_trace"
    ]

    assert row.typed_needs_user_score > 0
    assert row.final_edge_interpretation == "needs_user_signal"


def test_degraded_from_edge_produces_degraded_evidence():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())[
        "nearby_degraded_trace"
    ]

    assert row.typed_degraded_score > 0
    assert row.final_edge_interpretation == "degraded_signal"


def test_contradicts_edge_produces_contradiction_evidence():
    report = collect_typed_drs_lineage_edges()
    edge = _edge_by_type(report)["contradicts"]
    row = _candidate_by_id(report)["child_work"]

    assert edge.policy_effect == "contradiction"
    assert row.typed_contradiction_score > 0


def test_contradiction_source_is_quarantine_and_non_reusable():
    report = collect_typed_drs_lineage_edges()
    edge = _edge_by_type(report)["contradicts"]
    source = _candidate_by_id(report)[edge.from_record_id]

    assert source.record["record_id"] == "nearby_quarantine"
    assert source.taxonomy_kind == "quarantine"
    assert source.direct_reuse_eligible is False
    assert report.safety["contradiction_source_not_reused"] is True


def test_contradiction_target_is_signal_not_auto_blocked_in_v0_1():
    report = collect_typed_drs_lineage_edges()
    edge = _edge_by_type(report)["contradicts"]
    target = _candidate_by_id(report)[edge.to_record_id]

    assert target.record["record_id"] == "child_work"
    assert target.typed_contradiction_score > 0
    assert report.safety["contradiction_target_auto_blocked"] is False
    assert report.summary["contradiction_target_auto_blocked"] is False
    assert report.safety["contradiction_target_requires_future_conflict_check"] is True
    assert report.summary["contradiction_target_requires_future_conflict_check"] is True


def test_quarantine_record_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())["nearby_quarantine"]

    assert row.taxonomy_kind == "quarantine"
    assert row.direct_reuse_eligible is False
    assert row.routing_role == "quarantine"


def test_dead_end_record_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())["nearby_dead_end"]

    assert row.taxonomy_kind == "dead_end"
    assert row.direct_reuse_eligible is False
    assert row.routing_role == "deadend"


def test_blocked_trace_record_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())[
        "nearby_blocked_trace"
    ]

    assert row.taxonomy_kind == "blocked_trace"
    assert row.direct_reuse_eligible is False


def test_degraded_trace_record_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())[
        "nearby_degraded_trace"
    ]

    assert row.taxonomy_kind == "degraded_trace"
    assert row.direct_reuse_eligible is False


def test_needs_user_trace_record_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_typed_drs_lineage_edges())[
        "nearby_needs_user_trace"
    ]

    assert row.taxonomy_kind == "needs_user_trace"
    assert row.direct_reuse_eligible is False


def test_typed_edges_do_not_override_policy():
    report = collect_typed_drs_lineage_edges()

    assert report.safety["typed_edges_are_signals_only"] is True
    assert report.safety["typed_edges_override_policy"] is False
    assert report.safety["conflict_check_implemented"] is False
    assert report.summary["typed_edges_do_not_override_policy"] is True
    assert report.safety["unsafe_direct_reuse_candidates"] == 0


def test_direct_reuse_policy_unchanged():
    report = collect_typed_drs_lineage_edges()

    assert report.safety["direct_reuse_policy_unchanged"] is True
    assert report.summary["direct_reuse_policy_unchanged"] is True


def test_reuse_score_is_not_implemented():
    report = collect_typed_drs_lineage_edges()
    output = run_typed_drs_lineage_edges()

    assert report.summary["ReuseScore_implemented"] is False
    assert report.summary["conflict_check_implemented"] is False
    assert report.summary["typed_edges_are_signals_only"] is True
    assert "ReuseScore_implemented: false" in output
    assert "conflict_check_implemented: false" in output
    assert "typed_edges_are_signals_only: true" in output


def test_external_and_global_drs_are_not_implemented():
    output = run_typed_drs_lineage_edges()

    assert "local_drs_only: true" in output
    assert "external_drs_network_implemented: false" in output
    assert "global_drs_implemented: false" in output
    assert "schema_refactor_performed: false" in output


def test_output_contains_no_sensitive_terms():
    output = run_typed_drs_lineage_edges().lower()

    assert "api_key" not in output
    assert "token" not in output
    assert "secret" not in output
    assert "raw_user_text" not in output
    assert "chain of thought" not in output
