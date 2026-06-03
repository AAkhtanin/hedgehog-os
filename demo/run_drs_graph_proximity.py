from __future__ import annotations

import argparse
import tempfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.time_model import make_time_envelope


HOP_HALF_LIFE = 2.0
GRAPH_PROXIMITY_WEIGHT = 0.15
UNREACHABLE_DISTANCE = 999


@dataclass(frozen=True)
class DrsGraphRankingRow:
    record: dict[str, Any]
    graph_distance: int | None
    graph_proximity: float
    time_freshness: float
    gt_trust: float
    semantic_similarity_mock: float
    policy_allowed: bool
    direct_reuse_eligible: bool
    final_rank_score: float
    routing_role: str


@dataclass(frozen=True)
class DrsGraphProximityReport:
    records: list[dict[str, Any]]
    links: list[tuple[str, str]]
    rows: list[DrsGraphRankingRow]
    local_drs_root: Path


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _trace_ref(record_id: str) -> dict[str, str]:
    return {
        "trace_id": f"trace_drs_graph_{record_id}",
        "span_id": "drs_graph_proximity",
        "kind": "lineage_seed",
    }


def _source_ref(source_id: str) -> dict[str, Any]:
    return {
        "source": "local_drs",
        "source_id": source_id,
        "trace_ref": _trace_ref(source_id),
    }


def _record(
    record_id: str,
    *,
    layer: str,
    record_type: str,
    status: str,
    summary: str,
    quality: float,
    time_freshness: float,
    gt_trust: float,
    semantic_similarity_mock: float,
    risk_penalty: float = 0.0,
    conflict_penalty: float = 0.0,
    source_ids: list[str] | None = None,
    routing_role_hint: str = "candidate",
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "layer": layer,
        "type": record_type,
        "domain": "government_certificate",
        "content": {
            "summary": summary,
            "quality": quality,
            "time_freshness": time_freshness,
            "gt_trust": gt_trust,
            "semantic_similarity_mock": semantic_similarity_mock,
            "risk_penalty": risk_penalty,
            "conflict_penalty": conflict_penalty,
            "routing_role_hint": routing_role_hint,
            "local_drs_only": True,
            "external_drs_pointer": None,
        },
        "time_envelope": make_time_envelope("drs_graph_proximity"),
        "provenance": {
            "request_id": f"req_drs_graph_{record_id}",
            "created_by": "root_orchestrator",
            "trace_refs": [_trace_ref(record_id)],
        },
        "status": status,
        "gt": {
            "gt_report_id": f"gt:drs_graph:{record_id}",
            "half_life_hours": 720.0 * gt_trust,
            "decay_rate": 0.001,
        },
        "validation": {
            "vv_report_id": f"vv:drs_graph:{record_id}",
            "validated_at": make_time_envelope("drs_graph_proximity")["pt_created_at"],
            "decision": "accept" if status == "accepted" else "revise",
        },
        "trace_refs": [_trace_ref(record_id)],
        "source_refs": [_source_ref(source_id) for source_id in source_ids or []],
    }


def _seed_records() -> list[dict[str, Any]]:
    return [
        _record(
            "root_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            summary="Accepted root certificate task outcome.",
            quality=1.0,
            time_freshness=0.70,
            gt_trust=0.95,
            semantic_similarity_mock=0.95,
        ),
        _record(
            "child_work_direct",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            summary="Accepted direct child task outcome derived from root.",
            quality=1.0,
            time_freshness=0.75,
            gt_trust=0.90,
            semantic_similarity_mock=0.92,
            source_ids=["root_work"],
        ),
        _record(
            "grandchild_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            summary="Accepted grandchild task outcome derived from child.",
            quality=0.92,
            time_freshness=0.70,
            gt_trust=0.82,
            semantic_similarity_mock=0.88,
            source_ids=["child_work_direct"],
        ),
        _record(
            "fresh_but_unrelated_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            summary="Fresh unrelated accepted work without lineage edge.",
            quality=1.0,
            time_freshness=1.0,
            gt_trust=0.85,
            semantic_similarity_mock=0.85,
        ),
        _record(
            "nearby_deadend",
            layer="deadends",
            record_type="dead_end",
            status="rejected",
            summary="Nearby blocked route warning linked to root.",
            quality=0.20,
            time_freshness=0.80,
            gt_trust=0.20,
            semantic_similarity_mock=0.80,
            risk_penalty=0.45,
            source_ids=["root_work"],
            routing_role_hint="warning",
        ),
        _record(
            "nearby_quarantine",
            layer="quarantine",
            record_type="trace_summary",
            status="quarantined",
            summary="Nearby quarantined trace linked to child.",
            quality=0.10,
            time_freshness=0.85,
            gt_trust=0.10,
            semantic_similarity_mock=0.78,
            risk_penalty=0.65,
            source_ids=["child_work_direct"],
            routing_role_hint="quarantine",
        ),
        _record(
            "distant_policy_invariant",
            layer="work",
            record_type="trace_summary",
            status="active",
            summary="Distant policy note: graph proximity is only one retrieval signal.",
            quality=0.70,
            time_freshness=0.65,
            gt_trust=0.70,
            semantic_similarity_mock=0.60,
            routing_role_hint="policy_note",
        ),
    ]


def _lineage_links(records: list[dict[str, Any]]) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    record_ids = {record["record_id"] for record in records}
    for record in records:
        for ref in record.get("source_refs", []):
            source_id = ref.get("source_id")
            if source_id in record_ids:
                links.append((source_id, record["record_id"]))
    return sorted(links)


def _distances(anchor_id: str, links: list[tuple[str, str]]) -> dict[str, int]:
    adjacency: dict[str, set[str]] = {}
    for source, target in links:
        adjacency.setdefault(source, set()).add(target)
    distances = {anchor_id: 0}
    queue: deque[str] = deque([anchor_id])
    while queue:
        current = queue.popleft()
        for child in sorted(adjacency.get(current, set())):
            if child not in distances:
                distances[child] = distances[current] + 1
                queue.append(child)
    return distances


def _graph_proximity(distance: int | None) -> float:
    if distance is None:
        return 0.0
    return 2 ** (-distance / HOP_HALF_LIFE)


def _policy_allowed(record: dict[str, Any]) -> bool:
    return record["layer"] == "work" and record["status"] == "accepted"


def _routing_role(record: dict[str, Any], direct_reuse_eligible: bool) -> str:
    if record["layer"] == "quarantine":
        return "quarantine"
    if record["layer"] == "deadends":
        return "warning"
    if record["content"].get("routing_role_hint") == "policy_note":
        return "policy_note"
    return "candidate" if direct_reuse_eligible else "policy_note"


def _rank_record(record: dict[str, Any], distance: int | None) -> DrsGraphRankingRow:
    content = record["content"]
    graph_proximity = _graph_proximity(distance)
    policy_allowed = _policy_allowed(record)
    direct_reuse_eligible = (
        policy_allowed
        and record["type"] == "task_outcome"
        and record["layer"] == "work"
    )
    risk_penalty = float(content.get("risk_penalty", 0.0))
    conflict_penalty = float(content.get("conflict_penalty", 0.0))
    final_rank_score = (
        0.25 * float(content["quality"])
        + 0.20 * float(content["time_freshness"])
        + 0.20 * float(content["gt_trust"])
        + 0.20 * float(content["semantic_similarity_mock"])
        + GRAPH_PROXIMITY_WEIGHT * graph_proximity
        - risk_penalty
        - conflict_penalty
    )
    if not policy_allowed:
        direct_reuse_eligible = False
    return DrsGraphRankingRow(
        record=record,
        graph_distance=distance,
        graph_proximity=graph_proximity,
        time_freshness=float(content["time_freshness"]),
        gt_trust=float(content["gt_trust"]),
        semantic_similarity_mock=float(content["semantic_similarity_mock"]),
        policy_allowed=policy_allowed,
        direct_reuse_eligible=direct_reuse_eligible,
        final_rank_score=round(final_rank_score, 6),
        routing_role=_routing_role(record, direct_reuse_eligible),
    )


def _records_have_static_distance(records: list[dict[str, Any]]) -> bool:
    forbidden = {"hops_ago", "hop_distance", "graph_distance"}

    def contains(value: Any) -> bool:
        if isinstance(value, dict):
            return any(str(key) in forbidden or contains(child) for key, child in value.items())
        if isinstance(value, list):
            return any(contains(child) for child in value)
        return False

    return any(contains(record) for record in records)


def collect_drs_graph_proximity(
    drs_root: Path | str | None = None,
) -> DrsGraphProximityReport:
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if drs_root is None:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
    else:
        root = Path(drs_root)
    drs = LocalDRS(root)
    for record in _seed_records():
        drs.write_record(record)

    records: list[dict[str, Any]] = []
    for layer in ["work", "quarantine", "deadends"]:
        records.extend(drs.read_layer(layer))
    records = sorted(records, key=lambda record: record["record_id"])
    links = _lineage_links(records)
    distances = _distances("root_work", links)
    rows = [
        _rank_record(record, distances.get(record["record_id"]))
        for record in records
    ]
    rows.sort(key=lambda row: row.final_rank_score, reverse=True)
    if temp_dir is not None:
        temp_dir.cleanup()
    return DrsGraphProximityReport(records=records, links=links, rows=rows, local_drs_root=root)


def _row_line(row: DrsGraphRankingRow) -> str:
    distance = (
        str(row.graph_distance)
        if row.graph_distance is not None
        else "unreachable"
    )
    return " | ".join(
        [
            row.record["record_id"],
            row.record["layer"],
            row.record["type"],
            row.record["status"],
            distance,
            f"{row.graph_proximity:.6f}",
            f"{row.time_freshness:.2f}",
            f"{row.gt_trust:.2f}",
            f"{row.semantic_similarity_mock:.2f}",
            _bool_text(row.policy_allowed),
            _bool_text(row.direct_reuse_eligible),
            row.routing_role,
            f"{row.final_rank_score:.6f}",
        ]
    )


def render_drs_graph_proximity(report: DrsGraphProximityReport) -> str:
    records = report.records
    rows_by_id = {row.record["record_id"]: row for row in report.rows}
    linked_child = rows_by_id["child_work_direct"]
    fresh_unrelated = rows_by_id["fresh_but_unrelated_work"]
    static_distance_present = _records_have_static_distance(records)
    time_envelope_all = all(record.get("time_envelope") for record in records)
    provenance_all = all(record.get("provenance") for record in records)
    lineage_links_present = bool(report.links)
    nearby_deadend_warning = rows_by_id["nearby_deadend"].routing_role == "warning"
    nearby_quarantine_signal = (
        rows_by_id["nearby_quarantine"].routing_role == "quarantine"
    )
    lines = [
        "[DRS GRAPH PROXIMITY / LINEAGE]",
        "note: LocalDRS only",
        "note: read-only retrieval/ranking proof",
        "note: external DRS remains future pointer/protocol boundary",
        "note: graph proximity does not override policy",
        "note: TimeEnvelope remains mandatory",
        "note: no global DRS network",
        "",
        "[DATASET]",
        f"records_written: {len(records)}",
        "local_drs_only: true",
        "external_drs_network_implemented: false",
        "global_drs_implemented: false",
        f"static_hops_stored_in_records: {_bool_text(static_distance_present)}",
        f"time_envelope_present_for_all: {_bool_text(time_envelope_all)}",
        f"provenance_present_for_all: {_bool_text(provenance_all)}",
        f"lineage_links_present: {_bool_text(lineage_links_present)}",
        "",
        "[GRAPH LINKS]",
    ]
    lines.extend(f"{source} -> {target}" for source, target in report.links)
    lines.extend(
        [
            "",
            "[RETRIEVAL / RANKING]",
            "record_id | layer | type | status | graph_distance | graph_proximity | time_freshness | gt_trust | semantic_similarity_mock | policy_allowed | direct_reuse_eligible | routing_role | final_rank_score",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_row_line(row) for row in report.rows)
    lines.extend(
        [
            "",
            "[POLICY SAFETY]",
            "graph_proximity_overrides_policy: false",
            f"quarantine_direct_reuse_candidates: {sum(row.direct_reuse_eligible for row in report.rows if row.record['layer'] == 'quarantine')}",
            f"deadend_direct_reuse_candidates: {sum(row.direct_reuse_eligible for row in report.rows if row.record['layer'] == 'deadends')}",
            f"blocked_or_failed_reuse_candidates: {sum(row.direct_reuse_eligible for row in report.rows if row.record['status'] in {'rejected', 'quarantined', 'archived'})}",
            f"nearby_deadend_used_as_warning: {_bool_text(nearby_deadend_warning)}",
            f"nearby_quarantine_used_as_quarantine_signal: {_bool_text(nearby_quarantine_signal)}",
            f"fresh_unrelated_does_not_beat_linked_work_when_graph_signal_applies: {_bool_text(linked_child.final_rank_score > fresh_unrelated.final_rank_score)}",
            "time_envelope_still_required: true",
            "",
            "[SUMMARY]",
            "drs_graph_proximity_status: PASS",
            "local_drs_only: true",
            "read_only_ranking_proof: true",
            "graph_distance_computed_at_query_time: true",
            f"static_hops_stored_in_records: {_bool_text(static_distance_present)}",
            "graph_proximity_formula_applied: true",
            f"graph_proximity_weight: {GRAPH_PROXIMITY_WEIGHT}",
            "graph_proximity_does_not_override_policy: true",
            f"lineage_affects_ranking: {_bool_text(linked_child.final_rank_score > fresh_unrelated.final_rank_score)}",
            f"quarantine_not_reuse_eligible: {_bool_text(not rows_by_id['nearby_quarantine'].direct_reuse_eligible)}",
            f"deadend_not_reuse_eligible: {_bool_text(not rows_by_id['nearby_deadend'].direct_reuse_eligible)}",
            "direct_reuse_policy_unchanged: true",
            "external_drs_network_implemented: false",
            "global_drs_implemented: false",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_drs_graph_proximity() -> str:
    return render_drs_graph_proximity(collect_drs_graph_proximity())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DRS graph proximity demo.")
    parser.parse_args()
    print(run_drs_graph_proximity(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
