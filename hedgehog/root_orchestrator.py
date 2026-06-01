from __future__ import annotations

from pathlib import Path

from hedgehog.action_permission import check_action_permission
from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.drs import LocalDRS
from hedgehog.executor import execute_plan_graph
from hedgehog.final_renderer import render_final_draft
from hedgehog.fractal_dag_executor import run_fractal_dag_executor
from hedgehog.gt_validator import validate_gt
from hedgehog.input_intake import classify_input_text
from hedgehog.llm_gateway import generate_general_answer
from hedgehog.llm_architect import make_plan_graph_with_llm
from hedgehog.llm_architect import validate_plan_graph_contract
from hedgehog.marenna import create_marenna_after_task_record
from hedgehog.mode_router import route_execution
from hedgehog.post_vv import validate_result_proposals
from hedgehog.reflex import detect_reflex_action, execute_reflex_action
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
        force_full_pipeline: bool = True,
        allow_reflex: bool = False,
        user_confirmed: bool = False,
        llm_provider: str = "mock",
        llm_model: str | None = None,
        architect_provider: str = "deterministic",
        architect_model: str | None = None,
        architect_allow_config: bool = True,
        use_fractal_dag_executor: bool = False,
    ) -> dict:
        canonical_goal = "Prepare a mock government certificate request plan."
        desired_state = "Mock government certificate request is prepared for human review."
        intent_id = f"intent:{request_id}"
        goal_id = f"goal:{request_id}"
        world_state_ref = f"world_state:{request_id}"

        temporal_query = make_temporal_query()
        input_intake = classify_input_text(raw_user_text)
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
        mode_router = route_execution(
            raw_user_text=raw_user_text,
            retrieved_records=retrieved_records,
            reuse_gate=reuse_gate,
            allow_direct_reuse=allow_direct_reuse,
            force_full_pipeline=force_full_pipeline,
            allow_reflex=allow_reflex,
        )

        reflex_action = detect_reflex_action(raw_user_text)
        if (
            not force_full_pipeline
            and allow_reflex
            and reflex_action is not None
            and mode_router["execution_mode"] in {
                "deterministic_reflex_candidate",
                "proof_full_pipeline",
            }
        ):
            return self._process_reflex(
                request_id=request_id,
                session_anchor=session_anchor,
                temporal_query=temporal_query,
                retrieved_records=retrieved_records,
                memory_source_record_ids=memory_source_record_ids,
                reuse_gate=reuse_gate,
                mode_router=mode_router,
                action=reflex_action,
                user_confirmed=user_confirmed,
            )

        if input_intake["intent_kind"] == "general_request":
            return self._process_general_request(
                request_id=request_id,
                session_anchor=session_anchor,
                temporal_query=temporal_query,
                input_intake=input_intake,
                retrieved_records=retrieved_records,
                memory_source_record_ids=memory_source_record_ids,
                reuse_gate=reuse_gate,
                mode_router=mode_router,
                raw_user_text=raw_user_text,
                llm_provider=llm_provider,
                llm_model=llm_model,
            )

        if mode_router["execution_mode"] == "direct_reuse":
            return self._process_direct_reuse(
                request_id=request_id,
                session_anchor=session_anchor,
                canonical_goal=canonical_goal,
                temporal_query=temporal_query,
                retrieved_records=retrieved_records,
                memory_source_record_ids=memory_source_record_ids,
                reuse_gate=reuse_gate,
                mode_router=mode_router,
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

        llm_architect_result = None
        if architect_provider == "deterministic":
            plan_graph = make_plan_graph(attractor_packet)
        else:
            provider = "mock" if architect_provider == "mock_llm" else architect_provider
            llm_architect_result = make_plan_graph_with_llm(
                attractor_packet=attractor_packet,
                provider=provider,
                model=architect_model,
                allow_config=architect_allow_config,
            )
            if (
                llm_architect_result["status"] == "completed"
                and llm_architect_result["plan_graph"] is not None
            ):
                try:
                    validate_plan_graph_contract(
                        llm_architect_result["plan_graph"],
                        attractor_packet,
                    )
                    plan_graph = llm_architect_result["plan_graph"]
                except ValueError as exc:
                    llm_architect_result = {
                        **llm_architect_result,
                        "status": "error",
                        "plan_graph": None,
                        "error": str(exc),
                        "warnings": [
                            *llm_architect_result.get("warnings", []),
                            "invalid_plan_graph_contract",
                        ],
                        "fallback": "deterministic",
                    }
                    plan_graph = make_plan_graph(attractor_packet)
            else:
                llm_architect_result = {
                    **llm_architect_result,
                    "fallback": "deterministic",
                }
                plan_graph = make_plan_graph(attractor_packet)
        dag_runner_report = None
        if use_fractal_dag_executor:
            dag_runner_report = run_fractal_dag_executor(
                plan_graph,
                runner_id=f"runner:{request_id}:fractal_dag",
                session_anchor=session_anchor,
            )
            result_proposals = dag_runner_report["result_proposals"]
        else:
            result_proposals = execute_plan_graph(
                plan_graph,
                session_anchor=session_anchor,
            )
        vv_reports = validate_result_proposals(result_proposals)
        gt_report = validate_gt(vv_reports)
        execution_engine = "fractal_dag" if use_fractal_dag_executor else "legacy_executor"
        dag_trace = (
            {
                "execution_engine": execution_engine,
                "fractal_dag_executor_used": True,
                "dag_runner_status": dag_runner_report["status"],
                "dag_ready_sequence_present": bool(dag_runner_report["ready_sequence"]),
                "dag_execution_batches_present": bool(dag_runner_report["execution_batches"]),
                "dag_result_proposals_count": len(result_proposals),
                "dag_child_boundary_snapshots": dag_runner_report["child_boundary_snapshots"],
                "executor_created_final_output": dag_runner_report["executor_created_final_output"],
                "post_vv_after_dag_executor": bool(vv_reports),
                "gt_after_post_vv": bool(vv_reports) and bool(gt_report),
                "root_received_dag_artifacts": bool(result_proposals)
                and bool(vv_reports)
                and bool(gt_report),
                "no_real_external_action": dag_runner_report["no_real_external_action"],
                "uncontrolled_delegation": False,
            }
            if dag_runner_report is not None
            else {
                "execution_engine": execution_engine,
                "fractal_dag_executor_used": False,
                "executor_created_final_output": False,
                "post_vv_after_dag_executor": False,
                "gt_after_post_vv": bool(vv_reports) and bool(gt_report),
                "root_received_dag_artifacts": False,
                "no_real_external_action": True,
                "uncontrolled_delegation": False,
            }
        )

        used_proposals = self._select_used_proposals(gt_report, result_proposals)
        work_record_id = f"work:{request_id}"
        final_draft = render_final_draft(
            request_id=request_id,
            gt_report=gt_report,
            result_proposals=result_proposals,
            vv_reports=vv_reports,
            drs_writes=[work_record_id],
        )
        final_status = self._final_status_from_draft(gt_report, final_draft)
        work_record = self._make_work_record(
            request_id=request_id,
            session_anchor=session_anchor,
            canonical_goal=canonical_goal,
            gt_report=gt_report,
            final_draft=final_draft,
            final_status=final_status,
            used_proposals=used_proposals,
            execution_mode=mode_router["execution_mode"],
            route=mode_router["execution_mode"],
            retrieved_record_count=len(retrieved_records),
            memory_context_applied=memory_context_applied,
            memory_source_record_ids=memory_source_record_ids,
            reuse_decision=reuse_decision,
            reuse_score_best=self._reuse_score_best(reuse_gate),
            reuse_candidate_record_id=reuse_gate["best_record_id"],
            reuse_applied=reuse_applied,
            reused_record_ids=reused_record_ids,
            dag_trace=dag_trace if use_fractal_dag_executor else None,
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
            "status": final_status,
            "answer": final_draft["body"],
            "used_proposals": used_proposals,
            "gt_report_ref": gt_report["gt_report_id"],
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": final_draft["summary"],
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
            "input_intake": input_intake,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": memory_context_applied,
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "mode_router": mode_router,
            "reuse_decision": reuse_decision,
            "reuse_applied": reuse_applied,
            "reused_record_ids": reused_record_ids,
            "attractor_packet": attractor_packet,
            "llm_architect_result": llm_architect_result,
            "plan_graph": plan_graph,
            "execution_engine": execution_engine,
            "dag_runner_report": dag_runner_report,
            **dag_trace,
            "result_proposals": result_proposals,
            "vv_reports": vv_reports,
            "gt_report": gt_report,
            "drs_records": [work_record],
            "marenna_hook_records": [marenna_record],
            "up_hook_records": [up_record],
            "marenna_records": [marenna_drs_record["record_id"]],
            "up_records": [up_drs_record["record_id"]],
            "final_draft_proposal": final_draft,
            "final_output": final_output,
        }
        return final_output

    def _process_general_request(
        self,
        request_id: str,
        session_anchor: str,
        temporal_query: dict,
        input_intake: dict,
        retrieved_records: list[dict],
        memory_source_record_ids: list[str],
        reuse_gate: dict,
        mode_router: dict,
        raw_user_text: str,
        llm_provider: str,
        llm_model: str | None,
    ) -> dict:
        llm_result = generate_general_answer(
            text=raw_user_text,
            request_id=request_id,
            provider=llm_provider,
            model=llm_model,
        )
        final_status = self._general_final_status(llm_result)
        gt_ref = f"gt:llm_general:{request_id}"
        work_record = self._make_general_work_record(
            request_id=request_id,
            session_anchor=session_anchor,
            llm_result=llm_result,
            final_status=final_status,
            retrieved_record_count=len(retrieved_records),
            memory_source_record_ids=memory_source_record_ids,
            reuse_gate=reuse_gate,
            gt_ref=gt_ref,
        )
        self.drs.write_record(work_record)

        final_output = {
            "final_output_id": f"final:{request_id}",
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "status": final_status,
            "answer": llm_result["answer"] or "General responder failed to produce an answer.",
            "used_proposals": [],
            "gt_report_ref": gt_ref,
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": "General request handled by subordinate GeneralResponder.",
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "root_llm_general",
                    "kind": "root_orchestrator",
                }
            ],
        }
        gt_reference = {
            "gt_report_id": gt_ref,
            "decision": "accept" if llm_result["status"] == "completed" else "revise",
        }
        self.last_trace = {
            "temporal_query": temporal_query,
            "input_intake": input_intake,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": bool(memory_source_record_ids),
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "mode_router": mode_router,
            "execution_mode": "llm_general",
            "route": "llm_general",
            "reuse_decision": "none" if not memory_source_record_ids else reuse_gate["reuse_decision"],
            "reuse_applied": False,
            "reused_record_ids": [],
            "reflex_applied": False,
            "direct_reuse_applied": False,
            "architect_skipped": True,
            "executor_skipped": True,
            "attractor_packet": None,
            "plan_graph": None,
            "result_proposals": [],
            "vv_reports": [],
            "gt_report": gt_reference,
            "llm_gateway_result": llm_result,
            "drs_records": [work_record],
            "marenna_hook_records": [],
            "up_hook_records": [],
            "marenna_records": [],
            "up_records": [],
            "final_output": final_output,
        }
        return final_output

    def _process_reflex(
        self,
        request_id: str,
        session_anchor: str,
        temporal_query: dict,
        retrieved_records: list[dict],
        memory_source_record_ids: list[str],
        reuse_gate: dict,
        mode_router: dict,
        action: dict,
        user_confirmed: bool,
    ) -> dict:
        permission = check_action_permission(action, user_confirmed=user_confirmed)
        reflex_result = execute_reflex_action(action, permission)
        reflex_applied = reflex_result["status"] == "simulated_success"
        gt_ref = f"gt:reflex:{request_id}"
        gt_reference = {
            "gt_report_id": gt_ref,
            "decision": "accept" if reflex_applied else "revise",
            "action_id": action["action_id"],
        }
        work_record_id = f"work:{request_id}"
        final_draft = render_final_draft(
            request_id=request_id,
            gt_report=gt_reference,
            result_proposals=[],
            vv_reports=[],
            drs_writes=[work_record_id],
            mode="deterministic_reflex",
        )
        final_status = self._final_status_from_draft(gt_reference, final_draft)
        work_record = self._make_reflex_work_record(
            request_id=request_id,
            session_anchor=session_anchor,
            action=action,
            reflex_result=reflex_result,
            final_draft=final_draft,
            final_status=final_status,
            retrieved_record_count=len(retrieved_records),
            memory_source_record_ids=memory_source_record_ids,
            gt_ref=gt_ref,
        )
        self.drs.write_record(work_record)

        final_output = {
            "final_output_id": f"final:{request_id}",
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "status": final_status,
            "answer": final_draft["body"],
            "used_proposals": [],
            "gt_report_ref": gt_ref,
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": final_draft["summary"],
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "root_reflex",
                    "kind": "root_orchestrator",
                }
            ],
        }
        self.last_trace = {
            "temporal_query": temporal_query,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": bool(memory_source_record_ids),
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "mode_router": mode_router,
            "execution_mode": "deterministic_reflex",
            "reuse_decision": reuse_gate["reuse_decision"],
            "reuse_applied": False,
            "reused_record_ids": [],
            "reflex_applied": reflex_applied,
            "reflex_result": reflex_result,
            "permission": permission,
            "architect_skipped": True,
            "executor_skipped": True,
            "attractor_packet": None,
            "plan_graph": None,
            "result_proposals": [],
            "vv_reports": [],
            "gt_report": gt_reference,
            "drs_records": [work_record],
            "marenna_hook_records": [],
            "up_hook_records": [],
            "marenna_records": [],
            "up_records": [],
            "final_draft_proposal": final_draft,
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
        mode_router: dict,
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
        reuse_reference = {
            "gt_report_id": gt_ref,
            "decision": "accept",
            "source_record_id": reused_record_id,
        }
        work_record_id = f"work:{request_id}"
        final_draft = render_final_draft(
            request_id=request_id,
            gt_report=reuse_reference,
            result_proposals=[],
            vv_reports=[],
            drs_writes=[work_record_id],
            mode="direct_reuse",
        )
        final_status = self._final_status_from_draft(reuse_reference, final_draft)
        work_record = self._make_direct_reuse_work_record(
            request_id=request_id,
            session_anchor=session_anchor,
            canonical_goal=canonical_goal,
            reused_record=reused_record,
            final_draft=final_draft,
            final_status=final_status,
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
            "status": final_status,
            "answer": final_draft["body"],
            "used_proposals": [],
            "gt_report_ref": gt_ref,
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": final_draft["summary"],
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "root_final_from_reuse",
                    "kind": "root_orchestrator",
                }
            ],
        }
        self.last_trace = {
            "temporal_query": temporal_query,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": True,
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "mode_router": mode_router,
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
            "final_draft_proposal": final_draft,
            "final_output": final_output,
        }
        return final_output

    @staticmethod
    def _final_status_from_draft(gt_report: dict, final_draft: dict) -> str:
        gt_decision = gt_report.get("decision")
        recommendation = final_draft.get("status_recommendation")
        if gt_decision == "accept" and recommendation == "success":
            return "success"
        if gt_decision in {"revise", "needs_user", "no_update"}:
            return "needs_user"
        if recommendation == "needs_user":
            return "needs_user"
        return "failed"

    @staticmethod
    def _general_final_status(llm_result: dict) -> str:
        if llm_result["status"] == "completed":
            return "success"
        if llm_result["status"] == "blocked":
            return "needs_user"
        return "failed"

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
        final_draft: dict,
        final_status: str,
        used_proposals: list[str],
        execution_mode: str,
        route: str,
        retrieved_record_count: int,
        memory_context_applied: bool,
        memory_source_record_ids: list[str],
        reuse_decision: str,
        reuse_score_best: float | None,
        reuse_candidate_record_id: str | None,
        reuse_applied: bool,
        reused_record_ids: list[str],
        dag_trace: dict | None = None,
    ) -> dict:
        content = {
            "summary": "Mock certificate request pipeline completed.",
            "canonical_goal": canonical_goal,
            "result": "simulated_success" if final_status == "success" else "needs_user",
            "final_status": final_status,
            "execution_mode": execution_mode,
            "route": route,
            "selected_proposal_ids": list(final_draft["selected_proposal_ids"]),
            "completed_proposal_ids": list(final_draft["completed_proposal_ids"]),
            "needs_user_proposal_ids": list(final_draft["needs_user_proposal_ids"]),
            "blocked_proposal_ids": list(final_draft["blocked_proposal_ids"]),
            "rejected_proposal_ids": list(final_draft["rejected_proposal_ids"]),
            "gt_report_ref": gt_report["gt_report_id"],
            "gt_decision": gt_report["decision"],
            "final_draft_ref": final_draft["draft_id"],
            "final_draft_summary": final_draft["summary"],
            "final_draft_claims": list(final_draft["claims"]),
            "final_draft_warnings": list(final_draft["warnings"]),
            "used_proposal_count": len(used_proposals),
            "retrieved_record_count": retrieved_record_count,
            "memory_context_applied": memory_context_applied,
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_decision": reuse_decision,
            "reuse_score_best": reuse_score_best,
            "reuse_candidate_record_id": reuse_candidate_record_id,
            "reuse_applied": reuse_applied,
            "reused_record_ids": reused_record_ids,
            "reflex_applied": False,
            "direct_reuse_applied": False,
            "architect_skipped": False,
            "executor_skipped": False,
        }
        if dag_trace is not None:
            content.update(
                {
                    "execution_engine": dag_trace["execution_engine"],
                    "fractal_dag_executor_used": dag_trace["fractal_dag_executor_used"],
                    "dag_runner_status": dag_trace["dag_runner_status"],
                    "dag_result_proposals_count": dag_trace["dag_result_proposals_count"],
                    "dag_child_boundary_snapshots": dag_trace["dag_child_boundary_snapshots"],
                    "executor_created_final_output": dag_trace["executor_created_final_output"],
                    "post_vv_after_dag_executor": dag_trace["post_vv_after_dag_executor"],
                    "gt_after_post_vv": dag_trace["gt_after_post_vv"],
                    "root_received_dag_artifacts": dag_trace["root_received_dag_artifacts"],
                    "no_real_external_action": dag_trace["no_real_external_action"],
                    "uncontrolled_delegation": dag_trace["uncontrolled_delegation"],
                }
            )
        return {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": content,
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
    def _make_general_work_record(
        request_id: str,
        session_anchor: str,
        llm_result: dict,
        final_status: str,
        retrieved_record_count: int,
        memory_source_record_ids: list[str],
        reuse_gate: dict,
        gt_ref: str,
    ) -> dict:
        return {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "general",
            "content": {
                "summary": "General request handled by subordinate GeneralResponder.",
                "canonical_goal": "Answer a general user request.",
                "result": llm_result["status"],
                "final_status": final_status,
                "execution_mode": "llm_general",
                "route": "llm_general",
                "method": "llm_gateway_general_responder",
                "provider": llm_result["provider"],
                "model": llm_result["model"],
                "used_llm": llm_result["used_llm"],
                "selected_proposal_ids": [],
                "completed_proposal_ids": [],
                "needs_user_proposal_ids": [],
                "blocked_proposal_ids": [],
                "rejected_proposal_ids": [],
                "gt_report_ref": gt_ref,
                "gt_decision": "accept" if llm_result["status"] == "completed" else "revise",
                "final_draft_ref": None,
                "final_draft_summary": "GeneralResponder result used by Root.",
                "final_draft_claims": list(llm_result["claims"]),
                "final_draft_warnings": list(llm_result["warnings"]),
                "retrieved_record_count": retrieved_record_count,
                "memory_context_applied": bool(memory_source_record_ids),
                "memory_source_record_ids": memory_source_record_ids,
                "reuse_decision": "none" if not memory_source_record_ids else reuse_gate["reuse_decision"],
                "reuse_score_best": RootOrchestrator._reuse_score_best(reuse_gate),
                "reuse_candidate_record_id": reuse_gate.get("best_record_id"),
                "reuse_applied": False,
                "reused_record_ids": [],
                "reflex_applied": False,
                "direct_reuse_applied": False,
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
                        "span_id": "llm_general_writeback",
                        "kind": "root_orchestrator",
                    }
                ],
            },
            "gt": {
                "gt_report_id": gt_ref,
                "half_life_hours": 1.0,
                "decay_rate": 0.0,
            },
            "status": "accepted" if llm_result["status"] == "completed" else "no_update",
        }

    @staticmethod
    def _make_direct_reuse_work_record(
        request_id: str,
        session_anchor: str,
        canonical_goal: str,
        reused_record: dict,
        final_draft: dict,
        final_status: str,
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
                "final_status": final_status,
                "execution_mode": "direct_reuse",
                "route": "direct_reuse",
                "selected_proposal_ids": list(final_draft["selected_proposal_ids"]),
                "completed_proposal_ids": list(final_draft["completed_proposal_ids"]),
                "needs_user_proposal_ids": list(final_draft["needs_user_proposal_ids"]),
                "blocked_proposal_ids": list(final_draft["blocked_proposal_ids"]),
                "rejected_proposal_ids": list(final_draft["rejected_proposal_ids"]),
                "gt_report_ref": gt_ref,
                "gt_decision": "accept",
                "final_draft_ref": final_draft["draft_id"],
                "final_draft_summary": final_draft["summary"],
                "final_draft_claims": list(final_draft["claims"]),
                "final_draft_warnings": list(final_draft["warnings"]),
                "retrieved_record_count": retrieved_record_count,
                "memory_context_applied": True,
                "memory_source_record_ids": memory_source_record_ids,
                "reuse_decision": "direct_reuse",
                "reuse_score_best": RootOrchestrator._reuse_score_best(reuse_gate),
                "reuse_candidate_record_id": reused_record["record_id"],
                "reuse_applied": True,
                "reused_record_ids": reused_record_ids,
                "reflex_applied": False,
                "direct_reuse_applied": True,
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
    def _make_reflex_work_record(
        request_id: str,
        session_anchor: str,
        action: dict,
        reflex_result: dict,
        final_draft: dict,
        final_status: str,
        retrieved_record_count: int,
        memory_source_record_ids: list[str],
        gt_ref: str,
    ) -> dict:
        return {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "device_control",
            "content": {
                "summary": "Mock deterministic reflex action trace.",
                "canonical_goal": "Execute a safe mock deterministic reflex action.",
                "result": reflex_result["status"],
                "final_status": final_status,
                "execution_mode": "deterministic_reflex",
                "route": "deterministic_reflex",
                "selected_proposal_ids": list(final_draft["selected_proposal_ids"]),
                "completed_proposal_ids": list(final_draft["completed_proposal_ids"]),
                "needs_user_proposal_ids": list(final_draft["needs_user_proposal_ids"]),
                "blocked_proposal_ids": list(final_draft["blocked_proposal_ids"]),
                "rejected_proposal_ids": list(final_draft["rejected_proposal_ids"]),
                "gt_report_ref": gt_ref,
                "gt_decision": "accept" if reflex_result["status"] == "simulated_success" else "revise",
                "final_draft_ref": final_draft["draft_id"],
                "final_draft_summary": final_draft["summary"],
                "final_draft_claims": list(final_draft["claims"]),
                "final_draft_warnings": list(final_draft["warnings"]),
                "action_id": action["action_id"],
                "action_status": reflex_result["status"],
                "permission_reason": reflex_result["permission_reason"],
                "protocol_step_count": reflex_result["protocol_step_count"],
                "protocol_steps_executed": list(reflex_result["protocol_steps_executed"]),
                "protocol_mock_only": reflex_result["protocol_mock_only"],
                "retrieved_record_count": retrieved_record_count,
                "memory_context_applied": bool(memory_source_record_ids),
                "memory_source_record_ids": memory_source_record_ids,
                "reuse_decision": "none",
                "reuse_applied": False,
                "reused_record_ids": [],
                "reflex_applied": reflex_result["status"] == "simulated_success",
                "direct_reuse_applied": False,
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
                        "span_id": "reflex_writeback",
                        "kind": "root_orchestrator",
                    }
                ],
            },
            "gt": {
                "gt_report_id": gt_ref,
                "half_life_hours": 1.0,
                "decay_rate": 0.0,
            },
            "status": "accepted" if reflex_result["status"] == "simulated_success" else "active",
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
