from __future__ import annotations

from demo.run_drs_graph_proximity import GRAPH_PROXIMITY_WEIGHT
from demo.run_drs_graph_proximity import HOP_HALF_LIFE
from demo.run_drs_graph_proximity import collect_drs_graph_proximity
from demo.run_drs_graph_proximity import run_drs_graph_proximity


def _row_by_id(report):
    return {row.record["record_id"]: row for row in report.rows}


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


def test_runner_output_contains_title_and_summary():
    output = run_drs_graph_proximity()

    assert "[DRS GRAPH PROXIMITY / LINEAGE]" in output
    assert "[DATASET]" in output
    assert "[GRAPH LINKS]" in output
    assert "[RETRIEVAL / RANKING]" in output
    assert "[POLICY SAFETY]" in output
    assert "[SUMMARY]" in output
    assert "drs_graph_proximity_status: PASS" in output


def test_records_are_written_to_local_drs_and_read_back(tmp_path):
    report = collect_drs_graph_proximity(tmp_path)

    assert len(report.records) == 7
    assert (tmp_path / "work").exists()
    assert (tmp_path / "quarantine").exists()
    assert (tmp_path / "deadends").exists()
    assert list((tmp_path / "work").glob("*.json"))
    assert {record["record_id"] for record in report.records} == {
        "root_work",
        "child_work_direct",
        "grandchild_work",
        "fresh_but_unrelated_work",
        "nearby_deadend",
        "nearby_quarantine",
        "distant_policy_invariant",
    }


def test_every_record_has_time_envelope_and_provenance():
    report = collect_drs_graph_proximity()

    for record in report.records:
        assert record["time_envelope"]
        assert record["provenance"]
        assert record["provenance"]["trace_refs"]


def test_lineage_links_are_present_and_expected():
    report = collect_drs_graph_proximity()

    assert ("root_work", "child_work_direct") in report.links
    assert ("child_work_direct", "grandchild_work") in report.links
    assert ("child_work_direct", "nearby_quarantine") in report.links
    assert ("root_work", "nearby_deadend") in report.links


def test_no_static_hop_distance_is_stored_in_records():
    report = collect_drs_graph_proximity()

    for record in report.records:
        assert not _contains_static_distance_key(record)


def test_graph_distance_is_computed_at_query_time():
    report = collect_drs_graph_proximity()
    rows = _row_by_id(report)

    assert rows["root_work"].graph_distance == 0
    assert rows["child_work_direct"].graph_distance == 1
    assert rows["grandchild_work"].graph_distance == 2
    assert rows["fresh_but_unrelated_work"].graph_distance is None


def test_graph_proximity_formula_is_applied():
    report = collect_drs_graph_proximity()
    rows = _row_by_id(report)

    child_expected = 2 ** (-1 / HOP_HALF_LIFE)
    grandchild_expected = 2 ** (-2 / HOP_HALF_LIFE)

    assert rows["child_work_direct"].graph_proximity == child_expected
    assert rows["grandchild_work"].graph_proximity == grandchild_expected
    assert rows["fresh_but_unrelated_work"].graph_proximity == 0.0


def test_lineage_affects_ranking_against_fresh_unrelated_work():
    report = collect_drs_graph_proximity()
    rows = _row_by_id(report)

    assert rows["child_work_direct"].final_rank_score > rows["fresh_but_unrelated_work"].final_rank_score
    assert GRAPH_PROXIMITY_WEIGHT == 0.15


def test_quarantine_record_is_not_direct_reuse_eligible():
    row = _row_by_id(collect_drs_graph_proximity())["nearby_quarantine"]

    assert row.record["layer"] == "quarantine"
    assert row.direct_reuse_eligible is False
    assert row.routing_role == "quarantine"


def test_deadend_record_is_not_direct_reuse_eligible_and_is_warning():
    row = _row_by_id(collect_drs_graph_proximity())["nearby_deadend"]

    assert row.record["layer"] == "deadends"
    assert row.direct_reuse_eligible is False
    assert row.routing_role == "warning"


def test_graph_proximity_does_not_override_policy():
    rows = _row_by_id(collect_drs_graph_proximity())

    assert rows["nearby_deadend"].graph_distance == 1
    assert rows["nearby_deadend"].graph_proximity > 0
    assert rows["nearby_deadend"].policy_allowed is False
    assert rows["nearby_deadend"].direct_reuse_eligible is False
    assert rows["nearby_quarantine"].policy_allowed is False
    assert rows["nearby_quarantine"].direct_reuse_eligible is False


def test_direct_reuse_policy_remains_unchanged_for_unsafe_layers():
    report = collect_drs_graph_proximity()
    unsafe = [
        row
        for row in report.rows
        if row.record["layer"] in {"quarantine", "deadends"}
        and row.direct_reuse_eligible
    ]

    assert unsafe == []


def test_external_and_global_drs_are_not_implemented_in_output():
    output = run_drs_graph_proximity()

    assert "local_drs_only: true" in output
    assert "external_drs_network_implemented: false" in output
    assert "global_drs_implemented: false" in output
    assert "read_only_ranking_proof: true" in output
    assert "direct_reuse_policy_unchanged: true" in output


def test_output_contains_no_sensitive_terms():
    output = run_drs_graph_proximity().lower()

    assert "api_key" not in output
    assert "token" not in output
    assert "secret" not in output
    assert "raw_user_text" not in output
    assert "chain of thought" not in output
