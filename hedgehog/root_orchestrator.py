from __future__ import annotations

from pathlib import Path

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.drs import LocalDRS
from hedgehog.executor import execute_plan_graph
from hedgehog.gt_validator import validate_gt
from hedgehog.post_vv import validate_result_proposals
from hedgehog.time_model import make_temporal_query, make_time_envelope


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
        )
        self.drs.write_record(work_record)

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
            "attractor_packet": attractor_packet,
            "plan_graph": plan_graph,
            "result_proposals": result_proposals,
            "vv_reports": vv_reports,
            "gt_report": gt_report,
            "drs_records": [work_record],
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
    def _make_work_record(
        request_id: str,
        session_anchor: str,
        canonical_goal: str,
        gt_report: dict,
        used_proposals: list[str],
        retrieved_record_count: int,
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
