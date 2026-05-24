from __future__ import annotations

from pathlib import Path

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.drs import LocalDRS
from hedgehog.executor import execute_plan_graph
from hedgehog.gt_validator import validate_gt
from hedgehog.marenna import create_marenna_after_task_record
from hedgehog.post_vv import validate_result_proposals
from hedgehog.reuse_gate import evaluate_reuse_candidates
from hedgehog.time_model import make_temporal_query, make_time_envelope
from hedgehog.up import create_up_after_task_record


class RootOrchestrator:
    def __init__(self, drs: LocalDRS, needles_dir: Path):
        self.drs = drs
        self.needles_dir = Path(needles_dir)
        self.last_trace: dict = {}

    def process_event(
        self,
        raw_user_text: str,
        request_id: str,
        session_anchor: str,
        allow_direct_reuse: bool = False,
    ) -> dict:
        canonical_goal = "Prepare a mock government certificate request plan."
        desired_state = "Mock government certificate request is prepared for human review."
        intent_id = f"intent:{request_id}"
        goal_id = f"goal:{request_id}"
        world_state_ref = f"world_state:{request_id}"

        temporal_query = make_temporal_query()
        retrieved_records = self.drs.query_records(
            temporal_query,
            ["work", "thoughts", "deadends"],
        )
        memory_source_record_ids = [
            record["record_id"] for record in retrieved_records if "record_id" in record
        ]
        memory_context_applied = len(memory_source_record_ids) > 0
        reuse_gate = evaluate_reuse_candidates(retrieved_records, temporal_query)
        reuse_decision = reuse_gate["reuse_decision"]
        reuse_applied = False
        reused_record_ids = []

        if allow_direct_reuse and reuse_decision == "direct_reuse_candidate":
            return self._process_direct_reuse(
                request_id=request_id,
                session_anchor=session_anchor,
                canonical_goal=canonical_goal,
                temporal_query=temporal_query,
                retrieved_records=retrieved_records,
                memory_source_record_ids=memory_source_record_ids,
                reuse_gate=reuse_gate,
            )

        candidate_vectors = load_candidate_vectors_from_needles(
            [
                self.needles_dir / "government_services.json",
                self.needles_dir / "fallback_exploration.json",
            ]
        )
        attractor_packet = build_attractor_packet(
            request_id=request_id,
            intent_id=intent_id,
            world_state_ref=world_state_ref,
            goal_id=goal_id,
            desired_state=desired_state,
            candidate_vectors=candidate_vectors,
            as_of=temporal_query["as_of"],
            freshness_required=temporal_query["freshness_required"],
            max_selected=4,
        )

        plan_graph = make_plan_graph(attractor_packet)
        result_proposals = execute_plan_graph(
            plan_graph,
            session_anchor=session_anchor,
        )
        vv_reports = validate_result_proposals(result_proposals)
        gt_report = validate_gt(vv_reports)

        used_proposals = self._select_used_proposals(gt_report, result_proposals)
        work_record = self._make_work_record(
            request_id=request_id,
            session_anchor=session_anchor,
            canonical_goal=canonical_goal,
            gt_report=gt_report,
            used_proposals=used_proposals,
            retrieved_record_count=len(retrieved_records),
            memory_context_applied=memory_context_applied,
            memory_source_record_ids=memory_source_record_ids,
            reuse_decision=reuse_decision,
            reuse_score_best=self._reuse_score_best(reuse_gate),
            reuse_candidate_record_id=reuse_gate["best_record_id"],
            reuse_applied=reuse_applied,
            reused_record_ids=reused_record_ids,
        )
        self.drs.write_record(work_record)
        marenna_record = create_marenna_after_task_record(
            request_id=request_id,
            session_anchor=session_anchor,
            work_record_id=work_record["record_id"],
            domain=work_record["domain"],
        )
        up_record = create_up_after_task_record(
            request_id=request_id,
            session_anchor=session_anchor,
            work_record_id=work_record["record_id"],
            source_domain=work_record["domain"],
        )
        marenna_drs_record = self._make_marenna_quarantine_record(
            request_id=request_id,
            session_anchor=session_anchor,
            work_record_id=work_record["record_id"],
            marenna_record=marenna_record,
        )
        up_drs_record = self._make_up_quarantine_record(
            request_id=request_id,
            session_anchor=session_anchor,
            work_record_id=work_record["record_id"],
            up_record=up_record,
        )
        self.drs.write_record(marenna_drs_record)
        self.drs.write_record(up_drs_record)

        final_output = {
            "final_output_id": f"final:{request_id}",
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "status": "success" if gt_report["decision"] == "accept" else "needs_user",
            "answer": (
                "Mock certificate request pipeline completed. "
                "Review the simulated work record before any real action."
            ),
            "used_proposals": used_proposals,
            "gt_report_ref": gt_report["gt_report_id"],
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": "Deterministic MVP pipeline produced a Root-only FinalOutput.",
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "root_final_output",
                    "kind": "root_orchestrator",
                }
            ],
        }

        self.last_trace = {
            "temporal_query": temporal_query,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": memory_context_applied,
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "reuse_decision": reuse_decision,
            "reuse_applied": reuse_applied,
            "reused_record_ids": reused_record_ids,
            "attractor_packet": attractor_packet,
            "plan_graph": plan_graph,
            "result_proposals": result_proposals,
            "vv_reports": vv_reports,
            "gt_report": gt_report,
            "drs_records": [work_record],
            "marenna_hook_records": [marenna_record],
            "up_hook_records": [up_record],
            "marenna_records": [marenna_drs_record["record_id"]],
            "up_records": [up_drs_record["record_id"]],
            "final_output": final_output,
        }
        return final_output

    def _process_direct_reuse(
        self,
        request_id: str,
        session_anchor: str,
        canonical_goal: str,
        temporal_query: dict,
        retrieved_records: list[dict],
        memory_source_record_ids: list[str],
        reuse_gate: dict,
    ) -> dict:
        reused_record_id = reuse_gate["best_record_id"]
        reused_record = self._record_by_id(retrieved_records, reused_record_id)
        if reused_record is None:
            raise ValueError("ReuseGate selected a missing DRS record")

        reused_record_ids = [reused_record_id]
        gt_ref = reused_record.get("gt", {}).get(
            "gt_report_id",
            f"gt:direct_reuse:{reused_record_id}",
        )
        work_record = self._make_direct_reuse_work_record(
            request_id=request_id,
            session_anchor=session_anchor,
            canonical_goal=canonical_goal,
            reused_record=reused_record,
            retrieved_record_count=len(retrieved_records),
            memory_source_record_ids=memory_source_record_ids,
            reuse_gate=reuse_gate,
            reused_record_ids=reused_record_ids,
            gt_ref=gt_ref,
        )
        self.drs.write_record(work_record)

        final_output = {
            "final_output_id": f"final:{request_id}",
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "status": "success",
            "answer": (
                "Mock direct reuse result from a trusted prior DRS record. "
                "No real external action was performed."
            ),
            "used_proposals": [],
            "gt_report_ref": gt_ref,
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": "RootFinalFromReuse created by explicit direct reuse mode.",
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "root_final_from_reuse",
                    "kind": "root_orchestrator",
                }
            ],
        }
        reuse_reference = {
            "gt_report_id": gt_ref,
            "decision": "direct_reuse_reference",
            "source_record_id": reused_record_id,
        }
        self.last_trace = {
            "temporal_query": temporal_query,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": True,
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "reuse_decision": "direct_reuse",
            "reuse_applied": True,
            "reused_record_ids": reused_record_ids,
            "architect_skipped": True,
            "executor_skipped": True,
            "attractor_packet": None,
            "plan_graph": None,
            "result_proposals": [],
            "vv_reports": [],
            "gt_report": reuse_reference,
            "drs_records": [work_record],
            "marenna_hook_records": [],
            "up_hook_records": [],
            "marenna_records": [],
            "up_records": [],
            "final_output": final_output,
        }
        return final_output

    @staticmethod
    def _select_used_proposals(gt_report: dict, result_proposals: list[dict]) -> list[str]:
        winner = gt_report.get("winner")
        if winner:
            return [winner]
        return [proposal["proposal_id"] for proposal in result_proposals]

    @staticmethod
    def _record_by_id(records: list[dict], record_id: str | None) -> dict | None:
        for record in records:
            if record.get("record_id") == record_id:
                return record
        return None

    @staticmethod
    def _make_work_record(
        request_id: str,
        session_anchor: str,
        canonical_goal: str,
        gt_report: dict,
        used_proposals: list[str],
        retrieved_record_count: int,
        memory_context_applied: bool,
        memory_source_record_ids: list[str],
        reuse_decision: str,
        reuse_score_best: float | None,
        reuse_candidate_record_id: str | None,
        reuse_applied: bool,
        reused_record_ids: list[str],
    ) -> dict:
        return {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": "Mock certificate request pipeline completed.",
                "canonical_goal": canonical_goal,
                "result": "simulated_success",
                "used_proposal_count": len(used_proposals),
                "retrieved_record_count": retrieved_record_count,
                "memory_context_applied": memory_context_applied,
                "memory_source_record_ids": memory_source_record_ids,
                "reuse_decision": reuse_decision,
                "reuse_score_best": reuse_score_best,
                "reuse_candidate_record_id": reuse_candidate_record_id,
                "reuse_applied": reuse_applied,
                "reused_record_ids": reused_record_ids,
            },
            "time_envelope": make_time_envelope(session_anchor),
            "provenance": {
                "request_id": request_id,
                "created_by": "root_orchestrator",
                "trace_refs": [
                    {
                        "trace_id": f"trace:{request_id}",
                        "span_id": "drs_writeback",
                        "kind": "root_orchestrator",
                    }
                ],
            },
            "gt": {
                "gt_report_id": gt_report["gt_report_id"],
                "half_life_hours": gt_report.get("half_life_hours", 1.0),
                "decay_rate": gt_report.get("decay_rate", 0.0),
            },
            "status": "accepted" if gt_report["decision"] == "accept" else "no_update",
        }

    @staticmethod
    def _reuse_score_best(reuse_gate: dict) -> float | None:
        best_record_id = reuse_gate.get("best_record_id")
        for score in reuse_gate.get("candidate_scores", []):
            if score.get("record_id") == best_record_id:
                return score["reuse_score"]
        return None

    @staticmethod
    def _make_direct_reuse_work_record(
        request_id: str,
        session_anchor: str,
        canonical_goal: str,
        reused_record: dict,
        retrieved_record_count: int,
        memory_source_record_ids: list[str],
        reuse_gate: dict,
        reused_record_ids: list[str],
        gt_ref: str,
    ) -> dict:
        return {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": "Mock direct reuse result from prior DRS record.",
                "canonical_goal": canonical_goal,
                "result": "direct_reuse",
                "retrieved_record_count": retrieved_record_count,
                "memory_context_applied": True,
                "memory_source_record_ids": memory_source_record_ids,
                "reuse_decision": "direct_reuse",
                "reuse_score_best": RootOrchestrator._reuse_score_best(reuse_gate),
                "reuse_candidate_record_id": reused_record["record_id"],
                "reuse_applied": True,
                "reused_record_ids": reused_record_ids,
                "architect_skipped": True,
                "executor_skipped": True,
            },
            "time_envelope": make_time_envelope(session_anchor),
            "provenance": {
                "request_id": request_id,
                "created_by": "root_orchestrator",
                "trace_refs": [
                    {
                        "trace_id": f"trace:{request_id}",
                        "span_id": "direct_reuse_writeback",
                        "kind": "root_orchestrator",
                    }
                ],
            },
            "gt": {
                "gt_report_id": gt_ref,
                "half_life_hours": reused_record.get("gt", {}).get("half_life_hours", 1.0),
                "decay_rate": reused_record.get("gt", {}).get("decay_rate", 0.0),
            },
            "status": "accepted",
        }

    @staticmethod
    def _make_marenna_quarantine_record(
        request_id: str,
        session_anchor: str,
        work_record_id: str,
        marenna_record: dict,
    ) -> dict:
        return {
            "record_id": marenna_record["marenna_record_id"],
            "layer": "quarantine",
            "type": "reflection",
            "domain": marenna_record["domain"],
            "content": {
                "summary": marenna_record["content"]["summary"],
                "hook_record_id": marenna_record["marenna_record_id"],
                "promotion_target_layer": marenna_record["promotion_target_layer"],
                "source_work_record_id": work_record_id,
            },
            "time_envelope": make_time_envelope(session_anchor),
            "provenance": {
                "request_id": request_id,
                "created_by": "marenna",
                "trace_refs": [
                    {
                        "trace_id": f"trace:{request_id}",
                        "span_id": "marenna_quarantine",
                        "kind": "marenna",
                    }
                ],
            },
            "status": "quarantined",
        }

    @staticmethod
    def _make_up_quarantine_record(
        request_id: str,
        session_anchor: str,
        work_record_id: str,
        up_record: dict,
    ) -> dict:
        return {
            "record_id": up_record["up_record_id"],
            "layer": "quarantine",
            "type": "protocol_template",
            "domain": up_record["source_domain"],
            "content": {
                "summary": up_record["content"]["summary"],
                "hook_record_id": up_record["up_record_id"],
                "promotion_target_layer": up_record["promotion_target_layer"],
                "source_work_record_id": work_record_id,
            },
            "time_envelope": make_time_envelope(session_anchor),
            "provenance": {
                "request_id": request_id,
                "created_by": "up",
                "trace_refs": [
                    {
                        "trace_id": f"trace:{request_id}",
                        "span_id": "up_quarantine",
                        "kind": "up",
                    }
                ],
            },
            "status": "quarantined",
        }
