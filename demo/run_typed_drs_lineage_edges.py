from __future__ import annotations

import argparse
import tempfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.time_model import make_time_envelope


REQUIRED_EDGE_TYPES = {
    "derived_from",
    "same_trace",
    "warns_against",
    "blocked_by_policy",
    "requires_user",
    "degraded_from",
    "supports",
    "contradicts",
}
UNSAFE_TAXONOMY_KINDS = {
    "quarantine",
    "dead_end",
    "blocked_trace",
    "degraded_trace",
    "needs_user_trace",
}


@dataclass(frozen=True)
class TypedDrsEdge:
    edge_type: str
    from_record_id: str
    to_record_id: str
    from_taxonomy_kind: str
    to_taxonomy_kind: str
    policy_effect: str
    contributes_positive_reuse_signal: bool
    can_make_target_direct_reuse_eligible: bool


@dataclass(frozen=True)
class TypedDrsCandidate:
    record: dict[str, Any]
    taxonomy_kind: str
    graph_distance: int | None
    typed_positive_score: float
    typed_warning_score: float
    typed_blocking_score: float
    typed_needs_user_score: float
    typed_degraded_score: float
    typed_contradiction_score: float
    policy_allowed: bool
    direct_reuse_eligible: bool
    routing_role: str
    final_edge_interpretation: str


@dataclass(frozen=True)
class TypedDrsLineageReport:
    records: list[dict[str, Any]]
    edges: list[TypedDrsEdge]
    candidates: list[TypedDrsCandidate]
    safety: dict[str, Any]
    summary: dict[str, Any]
    local_drs_root: Path


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _trace_ref(record_id: str) -> dict[str, str]:
    return {
        "trace_id": "trace_typed_drs_lineage",
        "span_id": record_id,
        "kind": "typed_lineage_seed",
    }


def _typed_edge(edge_type: str, source_id: str, target_id: str) -> dict[str, str]:
    return {
        "edge_type": edge_type,
        "from_record_id": source_id,
        "to_record_id": target_id,
    }


def _record(
    record_id: str,
    *,
    layer: str,
    record_type: str,
    status: str,
    taxonomy_kind: str,
    summary: str,
    direct_reuse_eligible: bool = False,
    typed_edges: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "layer": layer,
        "type": record_type,
        "domain": "government_certificate",
        "content": {
            "summary": summary,
            "taxonomy_kind": taxonomy_kind,
            "typed_edges": typed_edges or [],
            "direct_reuse_eligible": direct_reuse_eligible,
            "successful_work_record": (
                layer == "work"
                and record_type == "task_outcome"
                and status == "accepted"
            ),
            "local_drs_only": True,
            "external_drs_pointer": None,
            "schema_refactor_performed": False,
        },
        "time_envelope": make_time_envelope("typed_drs_lineage_edges"),
        "provenance": {
            "request_id": f"req_typed_drs_{record_id}",
            "created_by": "root_orchestrator",
            "trace_refs": [_trace_ref(record_id)],
        },
        "status": status,
        "gt": {
            "gt_decision": "accept" if status == "accepted" else "revise",
            "gt_report_id": f"gt:typed-drs:{record_id}",
        },
        "validation": {
            "vv_status": "completed" if status == "accepted" else "blocked",
            "vv_report_id": f"vv:typed-drs:{record_id}",
        },
        "trace_refs": [_trace_ref(record_id)],
        "source_refs": [
            {
                "source": "local_drs",
                "source_id": edge["from_record_id"],
                "edge_type": edge["edge_type"],
            }
            for edge in typed_edges or []
        ],
    }


def _seed_records() -> list[dict[str, Any]]:
    return [
        _record(
            "root_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            taxonomy_kind="work_candidate",
            summary="Accepted root work candidate.",
            direct_reuse_eligible=True,
        ),
        _record(
            "child_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            taxonomy_kind="work_candidate",
            summary="Accepted child work derived from root.",
            direct_reuse_eligible=True,
            typed_edges=[_typed_edge("derived_from", "root_work", "child_work")],
        ),
        _record(
            "grandchild_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            taxonomy_kind="work_candidate",
            summary="Accepted grandchild work derived from child.",
            direct_reuse_eligible=True,
            typed_edges=[
                _typed_edge("derived_from", "child_work", "grandchild_work")
            ],
        ),
        _record(
            "nearby_dead_end",
            layer="deadends",
            record_type="dead_end",
            status="rejected",
            taxonomy_kind="dead_end",
            summary="Stable bad route warning.",
            typed_edges=[
                _typed_edge("warns_against", "nearby_dead_end", "child_work")
            ],
        ),
        _record(
            "nearby_blocked_trace",
            layer="deadends",
            record_type="trace_summary",
            status="blocked",
            taxonomy_kind="blocked_trace",
            summary="Route blocked by policy boundary.",
            typed_edges=[
                _typed_edge("blocked_by_policy", "nearby_blocked_trace", "root_work")
            ],
        ),
        _record(
            "nearby_degraded_trace",
            layer="deadends",
            record_type="trace_summary",
            status="degraded",
            taxonomy_kind="degraded_trace",
            summary="Timeout degraded from child path.",
            typed_edges=[
                _typed_edge("degraded_from", "child_work", "nearby_degraded_trace")
            ],
        ),
        _record(
            "nearby_needs_user_trace",
            layer="deadends",
            record_type="trace_summary",
            status="blocked",
            taxonomy_kind="needs_user_trace",
            summary="Permission required before route can proceed.",
            typed_edges=[
                _typed_edge(
                    "requires_user", "nearby_needs_user_trace", "child_work"
                )
            ],
        ),
        _record(
            "nearby_quarantine",
            layer="quarantine",
            record_type="trace_summary",
            status="quarantined",
            taxonomy_kind="quarantine",
            summary="Invalid payload contradicts candidate path.",
            typed_edges=[
                _typed_edge("contradicts", "nearby_quarantine", "child_work")
            ],
        ),
        _record(
            "supportive_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            taxonomy_kind="work_candidate",
            summary="Accepted work supporting child candidate.",
            direct_reuse_eligible=True,
            typed_edges=[
                _typed_edge("supports", "supportive_work", "child_work"),
                _typed_edge("same_trace", "child_work", "supportive_work"),
            ],
        ),
        _record(
            "unrelated_fresh_work",
            layer="work",
            record_type="task_outcome",
            status="accepted",
            taxonomy_kind="work_candidate",
            summary="Fresh accepted work without typed edge to anchor.",
            direct_reuse_eligible=True,
        ),
    ]


def _records_have_static_distance(records: list[dict[str, Any]]) -> bool:
    forbidden = {"hops_ago", "hop_distance", "graph_distance"}

    def contains(value: Any) -> bool:
        if isinstance(value, dict):
            return any(str(key) in forbidden or contains(child) for key, child in value.items())
        if isinstance(value, list):
            return any(contains(child) for child in value)
        return False

    return any(contains(record) for record in records)


def _edge_policy(edge_type: str) -> tuple[str, bool]:
    mapping = {
        "derived_from": ("positive", True),
        "same_trace": ("neutral", False),
        "warns_against": ("warning", False),
        "blocked_by_policy": ("blocked", False),
        "requires_user": ("needs_user", False),
        "degraded_from": ("degraded", False),
        "supports": ("positive", True),
        "contradicts": ("contradiction", False),
    }
    return mapping[edge_type]


def _extract_edges(records: list[dict[str, Any]]) -> list[TypedDrsEdge]:
    taxonomy_by_id = {
        record["record_id"]: record["content"]["taxonomy_kind"] for record in records
    }
    edges: list[TypedDrsEdge] = []
    for record in records:
        for raw_edge in record["content"].get("typed_edges", []):
            edge_type = raw_edge["edge_type"]
            from_id = raw_edge["from_record_id"]
            to_id = raw_edge["to_record_id"]
            policy_effect, positive = _edge_policy(edge_type)
            edges.append(
                TypedDrsEdge(
                    edge_type=edge_type,
                    from_record_id=from_id,
                    to_record_id=to_id,
                    from_taxonomy_kind=taxonomy_by_id[from_id],
                    to_taxonomy_kind=taxonomy_by_id[to_id],
                    policy_effect=policy_effect,
                    contributes_positive_reuse_signal=positive,
                    can_make_target_direct_reuse_eligible=False,
                )
            )
    return sorted(edges, key=lambda edge: (edge.edge_type, edge.from_record_id, edge.to_record_id))


def _distances(anchor_id: str, edges: list[TypedDrsEdge]) -> dict[str, int]:
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        if edge.edge_type in {"derived_from", "same_trace", "supports"}:
            adjacency.setdefault(edge.from_record_id, set()).add(edge.to_record_id)
        elif edge.edge_type in {
            "warns_against",
            "blocked_by_policy",
            "requires_user",
            "contradicts",
        }:
            adjacency.setdefault(edge.to_record_id, set()).add(edge.from_record_id)
        elif edge.edge_type == "degraded_from":
            adjacency.setdefault(edge.from_record_id, set()).add(edge.to_record_id)
    distances = {anchor_id: 0}
    queue: deque[str] = deque([anchor_id])
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, set())):
            if target not in distances:
                distances[target] = distances[current] + 1
                queue.append(target)
    return distances


def _policy_allowed(record: dict[str, Any]) -> bool:
    return (
        record["layer"] == "work"
        and record["status"] == "accepted"
        and record["content"]["taxonomy_kind"] == "work_candidate"
    )


def _routing_role(record: dict[str, Any]) -> str:
    taxonomy_kind = record["content"]["taxonomy_kind"]
    if taxonomy_kind == "work_candidate":
        return "candidate"
    if taxonomy_kind == "quarantine":
        return "quarantine"
    if taxonomy_kind == "dead_end":
        return "deadend"
    return taxonomy_kind


def _interpretation(
    record: dict[str, Any],
    positive: float,
    warning: float,
    blocking: float,
    needs_user: float,
    degraded: float,
    contradiction: float,
) -> str:
    taxonomy_kind = record["content"]["taxonomy_kind"]
    if taxonomy_kind == "quarantine":
        return "quarantine_signal"
    if contradiction:
        return "contradiction_signal"
    if needs_user:
        return "needs_user_signal"
    if blocking:
        return "blocked_signal"
    if degraded:
        return "degraded_signal"
    if warning:
        return "warning_signal"
    if positive:
        return "positive_candidate_signal"
    return "unrelated_or_neutral"


def _candidate_rows(
    records: list[dict[str, Any]], edges: list[TypedDrsEdge]
) -> list[TypedDrsCandidate]:
    by_id = {record["record_id"]: record for record in records}
    distances = _distances("root_work", edges)
    rows: list[TypedDrsCandidate] = []
    for record in records:
        record_id = record["record_id"]
        incoming = [edge for edge in edges if edge.to_record_id == record_id]
        outgoing = [edge for edge in edges if edge.from_record_id == record_id]
        positive = float(
            sum(
                1
                for edge in incoming + outgoing
                if edge.policy_effect == "positive"
                and edge.from_taxonomy_kind == "work_candidate"
            )
        )
        warning = float(
            sum(
                1
                for edge in incoming + outgoing
                if edge.policy_effect == "warning"
            )
        )
        blocking = float(
            sum(
                1
                for edge in incoming + outgoing
                if edge.policy_effect == "blocked"
            )
        )
        needs_user = float(
            sum(
                1
                for edge in incoming + outgoing
                if edge.policy_effect == "needs_user"
            )
        )
        degraded = float(
            sum(
                1
                for edge in incoming + outgoing
                if edge.policy_effect == "degraded"
            )
        )
        contradiction = float(
            sum(
                1
                for edge in incoming + outgoing
                if edge.policy_effect == "contradiction"
            )
        )
        policy_allowed = _policy_allowed(record)
        direct_reuse_eligible = (
            bool(record["content"].get("direct_reuse_eligible"))
            and policy_allowed
            and record["content"]["taxonomy_kind"] not in UNSAFE_TAXONOMY_KINDS
        )
        if record["content"]["taxonomy_kind"] == "work_candidate" and record_id not in by_id:
            direct_reuse_eligible = False
        rows.append(
            TypedDrsCandidate(
                record=record,
                taxonomy_kind=record["content"]["taxonomy_kind"],
                graph_distance=distances.get(record_id),
                typed_positive_score=positive,
                typed_warning_score=warning,
                typed_blocking_score=blocking,
                typed_needs_user_score=needs_user,
                typed_degraded_score=degraded,
                typed_contradiction_score=contradiction,
                policy_allowed=policy_allowed,
                direct_reuse_eligible=direct_reuse_eligible,
                routing_role=_routing_role(record),
                final_edge_interpretation=_interpretation(
                    record,
                    positive,
                    warning,
                    blocking,
                    needs_user,
                    degraded,
                    contradiction,
                ),
            )
        )
    return sorted(rows, key=lambda row: row.record["record_id"])


def _safety(candidates: list[TypedDrsCandidate], edges: list[TypedDrsEdge]) -> dict[str, Any]:
    by_edge_type = {edge.edge_type: edge for edge in edges}
    candidates_by_id = {candidate.record["record_id"]: candidate for candidate in candidates}
    contradiction_edges = [edge for edge in edges if edge.edge_type == "contradicts"]
    contradiction_sources = [
        candidates_by_id[edge.from_record_id]
        for edge in contradiction_edges
    ]
    contradiction_targets = [
        candidates_by_id[edge.to_record_id]
        for edge in contradiction_edges
    ]
    conflict_check_implemented = False
    contradiction_source_not_reused = bool(contradiction_sources) and all(
        not candidate.direct_reuse_eligible for candidate in contradiction_sources
    )
    contradiction_target_auto_blocked = False
    contradiction_target_requires_future_conflict_check = (
        bool(contradiction_targets) and not conflict_check_implemented
    )
    return {
        "typed_edges_are_signals_only": True,
        "conflict_check_implemented": conflict_check_implemented,
        "typed_edges_override_policy": False,
        "supports_edge_can_help_work_candidate": (
            by_edge_type["supports"].contributes_positive_reuse_signal is True
        ),
        "warns_against_not_positive_reuse": (
            by_edge_type["warns_against"].contributes_positive_reuse_signal is False
        ),
        "blocked_by_policy_not_success": all(
            not candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "blocked_trace"
        ),
        "requires_user_not_completed_action": all(
            not candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "needs_user_trace"
        ),
        "degraded_from_not_stable_success": all(
            not candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "degraded_trace"
        ),
        "contradicts_not_reuse_candidate": contradiction_source_not_reused,
        "contradiction_source_not_reused": contradiction_source_not_reused,
        "contradiction_target_auto_blocked": contradiction_target_auto_blocked,
        "contradiction_target_requires_future_conflict_check": (
            contradiction_target_requires_future_conflict_check
        ),
        "quarantine_direct_reuse_candidates": sum(
            candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "quarantine"
        ),
        "deadend_direct_reuse_candidates": sum(
            candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "dead_end"
        ),
        "blocked_direct_reuse_candidates": sum(
            candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "blocked_trace"
        ),
        "degraded_direct_reuse_candidates": sum(
            candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "degraded_trace"
        ),
        "needs_user_direct_reuse_candidates": sum(
            candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind == "needs_user_trace"
        ),
        "unsafe_direct_reuse_candidates": sum(
            candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
        ),
        "direct_reuse_policy_unchanged": all(
            not candidate.direct_reuse_eligible
            for candidate in candidates
            if candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
        ),
    }


def _summary(
    records: list[dict[str, Any]],
    edges: list[TypedDrsEdge],
    candidates: list[TypedDrsCandidate],
    safety: dict[str, Any],
) -> dict[str, Any]:
    static_distance_present = _records_have_static_distance(records)
    edge_types = {edge.edge_type for edge in edges}
    positive_vs_warning = (
        any(edge.edge_type == "supports" and edge.contributes_positive_reuse_signal for edge in edges)
        and any(
            edge.edge_type == "warns_against"
            and not edge.contributes_positive_reuse_signal
            for edge in edges
        )
    )
    pass_status = (
        len(records) >= 10
        and edge_types == REQUIRED_EDGE_TYPES
        and not static_distance_present
        and all(record.get("time_envelope") for record in records)
        and all(record.get("provenance") for record in records)
        and safety["typed_edges_are_signals_only"]
        and not safety["conflict_check_implemented"]
        and safety["contradiction_source_not_reused"]
        and not safety["contradiction_target_auto_blocked"]
        and safety["contradiction_target_requires_future_conflict_check"]
        and safety["direct_reuse_policy_unchanged"]
        and safety["unsafe_direct_reuse_candidates"] == 0
        and positive_vs_warning
    )
    return {
        "typed_drs_lineage_edges_status": "PASS" if pass_status else "FAIL",
        "edge_types_present": len(edge_types),
        "records_interpreted": len(candidates),
        "graph_distance_computed_at_query_time": True,
        "typed_edges_interpreted_at_query_time": True,
        "typed_edges_are_signals_only": safety["typed_edges_are_signals_only"],
        "conflict_check_implemented": safety["conflict_check_implemented"],
        "static_hops_stored_in_records": static_distance_present,
        "typed_edges_do_not_override_policy": not safety["typed_edges_override_policy"],
        "positive_edges_distinguished_from_warning_edges": positive_vs_warning,
        "blocked_edges_distinguished_from_deadends": any(
            candidate.taxonomy_kind == "blocked_trace"
            and candidate.routing_role == "blocked_trace"
            for candidate in candidates
        )
        and any(candidate.taxonomy_kind == "dead_end" for candidate in candidates),
        "needs_user_edges_distinguished_from_completed_actions": safety[
            "requires_user_not_completed_action"
        ],
        "degraded_edges_distinguished_from_stable_deadends": safety[
            "degraded_from_not_stable_success"
        ],
        "contradiction_edges_not_reused": safety["contradicts_not_reuse_candidate"],
        "contradiction_source_not_reused": safety["contradiction_source_not_reused"],
        "contradiction_target_auto_blocked": safety[
            "contradiction_target_auto_blocked"
        ],
        "contradiction_target_requires_future_conflict_check": safety[
            "contradiction_target_requires_future_conflict_check"
        ],
        "direct_reuse_policy_unchanged": safety["direct_reuse_policy_unchanged"],
        "ReuseScore_implemented": False,
        "local_drs_only": True,
        "external_drs_network_implemented": False,
        "global_drs_implemented": False,
        "schema_refactor_performed": False,
    }


def collect_typed_drs_lineage_edges(
    drs_root: Path | str | None = None,
) -> TypedDrsLineageReport:
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
    edges = _extract_edges(records)
    candidates = _candidate_rows(records, edges)
    safety = _safety(candidates, edges)
    summary = _summary(records, edges, candidates, safety)
    if temp_dir is not None:
        temp_dir.cleanup()
    return TypedDrsLineageReport(
        records=records,
        edges=edges,
        candidates=candidates,
        safety=safety,
        summary=summary,
        local_drs_root=root,
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def _edge_line(edge: TypedDrsEdge) -> str:
    return " | ".join(
        [
            edge.edge_type,
            edge.from_record_id,
            edge.to_record_id,
            edge.from_taxonomy_kind,
            edge.to_taxonomy_kind,
            edge.policy_effect,
            _bool_text(edge.contributes_positive_reuse_signal),
            _bool_text(edge.can_make_target_direct_reuse_eligible),
        ]
    )


def _candidate_line(candidate: TypedDrsCandidate) -> str:
    distance = (
        str(candidate.graph_distance)
        if candidate.graph_distance is not None
        else "unreachable"
    )
    return " | ".join(
        [
            candidate.record["record_id"],
            candidate.taxonomy_kind,
            distance,
            f"{candidate.typed_positive_score:.1f}",
            f"{candidate.typed_warning_score:.1f}",
            f"{candidate.typed_blocking_score:.1f}",
            f"{candidate.typed_needs_user_score:.1f}",
            f"{candidate.typed_degraded_score:.1f}",
            f"{candidate.typed_contradiction_score:.1f}",
            _bool_text(candidate.policy_allowed),
            _bool_text(candidate.direct_reuse_eligible),
            candidate.routing_role,
            candidate.final_edge_interpretation,
        ]
    )


def render_typed_drs_lineage_edges(report: TypedDrsLineageReport) -> str:
    records = report.records
    static_distance_present = _records_have_static_distance(records)
    typed_edges_present = bool(report.edges)
    time_envelope_all = all(record.get("time_envelope") for record in records)
    provenance_all = all(record.get("provenance") for record in records)
    lines = [
        "[TYPED DRS LINEAGE EDGES]",
        "note: LocalDRS typed-edge proof only",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no schema refactor in v0.1 unless explicitly needed",
        "note: typed edges do not change direct reuse policy",
        "note: typed edge proximity does not override policy",
        "note: ReuseScore is not implemented in this layer",
        "",
        "[DATASET]",
        f"records_written: {len(records)}",
        "local_drs_only: true",
        "external_drs_network_implemented: false",
        "global_drs_implemented: false",
        "schema_refactor_performed: false",
        f"static_hops_stored_in_records: {_bool_text(static_distance_present)}",
        f"typed_edges_present: {_bool_text(typed_edges_present)}",
        f"time_envelope_present_for_all: {_bool_text(time_envelope_all)}",
        f"provenance_present_for_all: {_bool_text(provenance_all)}",
        "",
        "[TYPED EDGES]",
        "edge_type | from_record_id | to_record_id | from_taxonomy_kind | to_taxonomy_kind | policy_effect | contributes_positive_reuse_signal | can_make_target_direct_reuse_eligible",
        "--- | --- | --- | --- | --- | --- | --- | ---",
    ]
    lines.extend(_edge_line(edge) for edge in report.edges)
    lines.extend(
        [
            "",
            "[QUERY-TIME INTERPRETATION]",
            "record_id | taxonomy_kind | graph_distance | typed_positive_score | typed_warning_score | typed_blocking_score | typed_needs_user_score | typed_degraded_score | typed_contradiction_score | policy_allowed | direct_reuse_eligible | routing_role | final_edge_interpretation",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_candidate_line(candidate) for candidate in report.candidates)
    lines.extend(["", "[POLICY SAFETY]"])
    lines.extend(_field_lines(report.safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_typed_drs_lineage_edges() -> str:
    return render_typed_drs_lineage_edges(collect_typed_drs_lineage_edges())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Typed DRS Lineage Edges demo.")
    parser.parse_args()
    print(run_typed_drs_lineage_edges(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
