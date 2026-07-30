from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hedgehog.action_permission import check_action_permission
from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.drs import LocalDRS
from hedgehog.drs_memory_resolution_v01 import DRSResolutionReportV01
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
from hedgehog.reuse_certificate_v01 import (
    RootShortcutAuthorizationProjectionV01,
    validate_existing_root_shortcut_decision_v01,
    validate_root_shortcut_authorization_projection_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    validate_root_decision_input_v01,
    validate_root_decision_kernel_v01,
    validate_root_decision_result_v01,
)
from hedgehog.time_model import make_temporal_query, make_time_envelope
from hedgehog.up import create_up_after_task_record


SENSITIVE_DRS_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
}
_G2B_ACTION_SHORTCUT_REASONS = (
    "drs_payment_shortcut_forbidden",
    "drs_shipment_shortcut_forbidden",
    "drs_ticket_shortcut_forbidden",
    "drs_action_packet_shortcut_forbidden",
    "drs_receipt_creation_shortcut_forbidden",
    "drs_action_intent_shortcut_forbidden",
)


def _sensitive_terms_absent(*values: Any) -> bool:
    serialized = json.dumps(values, sort_keys=True, default=str).lower()
    return not any(term in serialized for term in SENSITIVE_DRS_TERMS)


class RootOrchestrator:
    def __init__(
        self,
        drs: LocalDRS,
        needles_dir: Path,
        *,
        _g2b_root_decision_evidence: tuple[
            tuple[
                RootDecisionKernelV01,
                RootDecisionInputV01,
                RootDecisionResultV01,
            ],
            ...,
        ] = (),
    ) -> None:
        if type(_g2b_root_decision_evidence) is not tuple:
            raise ValueError("drs_root_decision_binding_invalid") from None
        identities: list[tuple[str, str, str]] = []
        for row in _g2b_root_decision_evidence:
            if (
                type(row) is not tuple
                or len(row) != 3
                or type(row[0]) is not RootDecisionKernelV01
                or type(row[1]) is not RootDecisionInputV01
                or type(row[2]) is not RootDecisionResultV01
            ):
                raise ValueError(
                    "drs_root_decision_binding_invalid"
                ) from None
            try:
                if validate_root_decision_kernel_v01(row[0]) != ():
                    raise ValueError
                if (
                    validate_root_decision_input_v01(
                        kernel=row[0],
                        decision_input=row[1],
                    )
                    != ()
                ):
                    raise ValueError
                if (
                    validate_root_decision_result_v01(
                        kernel=row[0],
                        decision_input=row[1],
                        result=row[2],
                    )
                    != ()
                ):
                    raise ValueError
                identity = (
                    row[0].kernel_id,
                    row[1].decision_input_id,
                    row[2].decision_id,
                )
                if any(type(value) is not str for value in identity):
                    raise ValueError
                if identity in identities:
                    raise ValueError
            except Exception:
                raise ValueError(
                    "drs_root_decision_binding_invalid"
                ) from None
            identities.append(identity)
        self.drs = drs
        self.needles_dir = Path(needles_dir)
        self._g2b_root_decision_evidence = _g2b_root_decision_evidence
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
        g2b_resolution_report: DRSResolutionReportV01 | None = None,
        g2b_use_time: int | None = None,
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
        legacy_mode_router = route_execution(
            raw_user_text=raw_user_text,
            retrieved_records=retrieved_records,
            reuse_gate=reuse_gate,
            allow_direct_reuse=allow_direct_reuse,
            force_full_pipeline=force_full_pipeline,
            allow_reflex=allow_reflex,
        )
        mode_router = legacy_mode_router
        g2b_shortcut_reason: str | None = None

        reflex_action = detect_reflex_action(raw_user_text)
        if (
            not force_full_pipeline
            and allow_reflex
            and reflex_action is not None
            and legacy_mode_router["execution_mode"] in {
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
                legacy_mode_router=legacy_mode_router,
                action=reflex_action,
                user_confirmed=user_confirmed,
            )

        if allow_direct_reuse and not force_full_pipeline:
            action_reason = self._classify_g2b_shortcut_request(
                raw_user_text
            )
            if action_reason is not None:
                g2b_shortcut_reason = action_reason
            elif (
                type(g2b_resolution_report) is DRSResolutionReportV01
                and g2b_use_time is not None
            ):
                projection = (
                    g2b_resolution_report.root_shortcut_projection
                )
                if (
                    type(projection)
                    is not RootShortcutAuthorizationProjectionV01
                ):
                    g2b_shortcut_reason = (
                        "drs_root_projection_invalid"
                    )
                else:
                    projection_valid, projection_reasons = (
                        validate_root_shortcut_authorization_projection_v01(
                            projection
                        )
                    )
                    if not projection_valid or projection_reasons:
                        g2b_shortcut_reason = (
                            "drs_root_projection_invalid"
                        )
                    else:
                        matches = tuple(
                            row
                            for row in self._g2b_root_decision_evidence
                            if (
                                row[0].kernel_id
                                == projection.root_kernel_id
                                and row[1].decision_input_id
                                == projection.root_decision_input_id
                                and row[2].decision_id
                                == projection.root_decision_id
                            )
                        )
                        if len(matches) == 1:
                            valid, reasons = (
                                validate_existing_root_shortcut_decision_v01(
                                    resolution_report=(
                                        g2b_resolution_report
                                    ),
                                    root_kernel=matches[0][0],
                                    root_decision_input=matches[0][1],
                                    root_decision_result=matches[0][2],
                                    use_time=g2b_use_time,
                                )
                            )
                            if valid and not reasons:
                                canonical_mode_router = {
                                    "execution_mode": "direct_reuse",
                                    "direct_reuse_allowed": True,
                                    "reason": (
                                        "g2b_root_projection_and_"
                                        "certificate_validated"
                                    ),
                                    "intent_complexity": (
                                        legacy_mode_router[
                                            "intent_complexity"
                                        ]
                                    ),
                                }
                                return (
                                    self
                                    ._process_g2b_informational_shortcut(
                                        request_id=request_id,
                                        session_anchor=session_anchor,
                                        temporal_query=temporal_query,
                                        input_intake=input_intake,
                                        retrieved_records=(
                                            retrieved_records
                                        ),
                                        memory_source_record_ids=(
                                            memory_source_record_ids
                                        ),
                                        reuse_gate=reuse_gate,
                                        legacy_mode_router=(
                                            legacy_mode_router
                                        ),
                                        mode_router=(
                                            canonical_mode_router
                                        ),
                                        report=g2b_resolution_report,
                                        use_time=g2b_use_time,
                                    )
                                )
                            g2b_shortcut_reason = (
                                reasons[0]
                                if reasons
                                else (
                                    "drs_root_shortcut_evidence_"
                                    "missing"
                                )
                            )
                        else:
                            g2b_shortcut_reason = (
                                "drs_root_decision_binding_invalid"
                            )
            else:
                g2b_shortcut_reason = (
                    "drs_root_shortcut_evidence_missing"
                )

        if legacy_mode_router["execution_mode"] == "direct_reuse":
            mode_router = {
                "execution_mode": (
                    "context_only"
                    if retrieved_records
                    else "proof_full_pipeline"
                ),
                "direct_reuse_allowed": False,
                "reason": "drs_root_shortcut_evidence_missing",
                "intent_complexity": legacy_mode_router[
                    "intent_complexity"
                ],
            }

        if (
            input_intake["intent_kind"] == "general_request"
            and not (
                g2b_resolution_report is not None
                and g2b_shortcut_reason
                in _G2B_ACTION_SHORTCUT_REASONS
            )
        ):
            return self._process_general_request(
                request_id=request_id,
                session_anchor=session_anchor,
                temporal_query=temporal_query,
                input_intake=input_intake,
                retrieved_records=retrieved_records,
                memory_source_record_ids=memory_source_record_ids,
                reuse_gate=reuse_gate,
                mode_router=mode_router,
                legacy_mode_router=legacy_mode_router,
                g2b_shortcut_reason=g2b_shortcut_reason,
                raw_user_text=raw_user_text,
                llm_provider=llm_provider,
                llm_model=llm_model,
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
                "post_vv_before_gt": bool(vv_reports) and bool(gt_report),
                "vv_reports_count": len(vv_reports),
                "gt_after_post_vv": bool(vv_reports) and bool(gt_report),
                "gt_decision": gt_report["decision"],
                "gt_committed_final_output": False,
                "root_received_dag_artifacts": bool(result_proposals)
                and bool(vv_reports)
                and bool(gt_report),
                "root_created_final_output": True,
                "no_real_external_action": dag_runner_report["no_real_external_action"],
                "uncontrolled_delegation": False,
                "audit_trace_present": True,
                "root_native_dag_path": True,
                "root_final_authority_preserved": True,
                "result_returned_to_root": bool(result_proposals)
                and bool(vv_reports)
                and bool(gt_report),
            }
            if dag_runner_report is not None
            else {
                "execution_engine": execution_engine,
                "fractal_dag_executor_used": False,
                "executor_created_final_output": False,
                "post_vv_after_dag_executor": False,
                "post_vv_before_gt": bool(vv_reports) and bool(gt_report),
                "vv_reports_count": len(vv_reports),
                "gt_after_post_vv": bool(vv_reports) and bool(gt_report),
                "gt_decision": gt_report["decision"],
                "gt_committed_final_output": False,
                "root_received_dag_artifacts": False,
                "root_created_final_output": True,
                "no_real_external_action": True,
                "uncontrolled_delegation": False,
                "audit_trace_present": True,
                "root_native_dag_path": False,
                "root_final_authority_preserved": True,
                "result_returned_to_root": bool(result_proposals)
                and bool(vv_reports)
                and bool(gt_report),
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
            plan_id=plan_graph.get("plan_id"),
        )
        if use_fractal_dag_executor and dag_trace is not None:
            dag_trace["sensitive_input_absent"] = work_record["content"][
                "sensitive_input_absent"
            ]
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
            "legacy_mode_router": legacy_mode_router,
            "g2b_shortcut_reason": g2b_shortcut_reason,
            "reuse_decision": reuse_decision,
            "reuse_applied": reuse_applied,
            "reused_record_ids": reused_record_ids,
            "direct_reuse_applied": False,
            "architect_skipped": False,
            "executor_skipped": False,
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
        legacy_mode_router: dict,
        g2b_shortcut_reason: str | None,
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
            "legacy_mode_router": legacy_mode_router,
            "g2b_shortcut_reason": g2b_shortcut_reason,
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
        legacy_mode_router: dict,
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
            "legacy_mode_router": legacy_mode_router,
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

    def _process_g2b_informational_shortcut(
        self,
        *,
        request_id: str,
        session_anchor: str,
        temporal_query: dict,
        input_intake: dict,
        retrieved_records: list[dict],
        memory_source_record_ids: list[str],
        reuse_gate: dict,
        legacy_mode_router: dict,
        mode_router: dict,
        report: DRSResolutionReportV01,
        use_time: int,
    ) -> dict:
        candidate = next(
            item
            for item in report.eligible_candidates
            if item.resolution_candidate_id
            == report.selected_candidate_id
        )
        selected_record = next(
            item
            for item in report.source_records
            if item.meaning_record_id == candidate.meaning_record_id
        )
        projection = report.root_shortcut_projection
        certificate = report.reuse_certificate
        assert projection is not None
        assert certificate is not None
        work_record = {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": selected_record.safe_summary,
                "result": "direct_reuse",
                "final_status": "success",
                "execution_mode": "direct_reuse",
                "route": "direct_reuse",
                "reuse_decision": "direct_reuse",
                "reuse_applied": True,
                "direct_reuse_applied": True,
                "architect_skipped": True,
                "executor_skipped": True,
                "g2b_report_id": report.report_id,
                "g2b_root_shortcut_projection_id": (
                    projection.root_shortcut_projection_id
                ),
                "g2b_reuse_certificate_id": (
                    certificate.certificate_id
                ),
                "g2b_selected_candidate_id": (
                    candidate.resolution_candidate_id
                ),
                "g2b_selected_meaning_record_id": (
                    selected_record.meaning_record_id
                ),
                "g2b_use_time": use_time,
                "g2b_root_decision_id": projection.root_decision_id,
                "provider_calls": 0,
                "network_calls": 0,
                "gemini_calls": 0,
                "connector_calls": 0,
                "real_world_effects_count": 0,
            },
            "time_envelope": make_time_envelope(session_anchor),
            "provenance": {
                "request_id": request_id,
                "created_by": "root_orchestrator",
                "trace_refs": [
                    {
                        "trace_id": f"trace:{request_id}",
                        "span_id": "g2b_informational_shortcut",
                        "kind": "root_orchestrator",
                    }
                ],
            },
            "gt": {
                "gt_report_id": projection.root_decision_id,
                "half_life_hours": 1.0,
                "decay_rate": 0.0,
            },
            "status": "accepted",
        }
        self.drs.write_record(work_record)
        final_output = {
            "final_output_id": f"final:{request_id}",
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "status": "success",
            "answer": selected_record.safe_summary,
            "used_proposals": [],
            "gt_report_ref": projection.root_decision_id,
            "drs_writes": [work_record["record_id"]],
            "time_envelope": make_time_envelope(session_anchor),
            "summary": selected_record.safe_summary,
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "root_g2b_informational_final",
                    "kind": "root_orchestrator",
                }
            ],
        }
        self.last_trace = {
            "temporal_query": temporal_query,
            "input_intake": input_intake,
            "retrieved_record_count": len(retrieved_records),
            "memory_context_applied": bool(memory_source_record_ids),
            "memory_source_record_ids": memory_source_record_ids,
            "reuse_gate": reuse_gate,
            "legacy_mode_router": legacy_mode_router,
            "mode_router": mode_router,
            "execution_mode": "direct_reuse",
            "route": "direct_reuse",
            "reuse_decision": "direct_reuse",
            "reuse_applied": True,
            "direct_reuse_applied": True,
            "reused_record_ids": [],
            "architect_skipped": True,
            "executor_skipped": True,
            "root_created_final_output": True,
            "root_final_authority_preserved": True,
            "g2b_report_id": report.report_id,
            "g2b_root_shortcut_projection_id": (
                projection.root_shortcut_projection_id
            ),
            "g2b_reuse_certificate_id": certificate.certificate_id,
            "g2b_use_time": use_time,
            "g2b_root_decision_id": projection.root_decision_id,
            "g2b_selected_candidate_id": (
                candidate.resolution_candidate_id
            ),
            "g2b_selected_meaning_record_id": (
                selected_record.meaning_record_id
            ),
            "g2b_shortcut_validation": "PASS",
            "provider_calls": 0,
            "network_calls": 0,
            "gemini_calls": 0,
            "connector_calls": 0,
            "real_world_effects_count": 0,
            "attractor_packet": None,
            "plan_graph": None,
            "result_proposals": [],
            "vv_reports": [],
            "gt_report": {
                "gt_report_id": projection.root_decision_id,
                "decision": "accept",
            },
            "drs_records": [work_record],
            "marenna_hook_records": [],
            "up_hook_records": [],
            "marenna_records": [],
            "up_records": [],
            "final_draft_proposal": None,
            "final_output": final_output,
        }
        return final_output

    @staticmethod
    def _classify_g2b_shortcut_request(
        raw_user_text: str,
    ) -> str | None:
        if type(raw_user_text) is not str:
            return "drs_action_intent_shortcut_forbidden"
        normalized = " ".join(
            "".join(
                character.lower()
                if character.isalnum()
                else " "
                for character in raw_user_text
            ).split()
        )
        phrases = (
            (
                (
                    "pay supplier",
                    "send payment",
                    "transfer funds",
                    "authorize payment",
                    "execute payment",
                    "make bank transfer",
                ),
                "drs_payment_shortcut_forbidden",
            ),
            (
                (
                    "release shipment",
                    "dispatch shipment",
                    "ship order",
                ),
                "drs_shipment_shortcut_forbidden",
            ),
            (
                (
                    "buy ticket",
                    "purchase ticket",
                    "book ticket",
                    "issue ticket",
                    "reserve seat",
                ),
                "drs_ticket_shortcut_forbidden",
            ),
            (
                (
                    "create actioncommitpacket",
                    "issue actioncommitpacket",
                    "generate action packet",
                    "authorize action packet",
                ),
                "drs_action_packet_shortcut_forbidden",
            ),
            (
                (
                    "create receipt",
                    "issue receipt",
                    "generate receipt",
                ),
                "drs_receipt_creation_shortcut_forbidden",
            ),
            (
                (
                    "execute maintenance",
                    "order replacement part",
                    "perform external action",
                ),
                "drs_action_intent_shortcut_forbidden",
            ),
        )
        for candidates, reason in phrases:
            if any(phrase in normalized for phrase in candidates):
                return reason
        return None

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
        plan_id: str | None = None,
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
                    "vv_reports_count": dag_trace["vv_reports_count"],
                    "gt_after_post_vv": dag_trace["gt_after_post_vv"],
                    "gt_decision": dag_trace["gt_decision"],
                    "root_created_final_output": dag_trace["root_created_final_output"],
                    "gt_committed_final_output": dag_trace["gt_committed_final_output"],
                    "root_received_dag_artifacts": dag_trace["root_received_dag_artifacts"],
                    "no_real_external_action": dag_trace["no_real_external_action"],
                    "uncontrolled_delegation": dag_trace["uncontrolled_delegation"],
                    "audit_trace_present": dag_trace["audit_trace_present"],
                    "root_native_dag_path": dag_trace["root_native_dag_path"],
                    "root_final_authority_preserved": dag_trace[
                        "root_final_authority_preserved"
                    ],
                    "post_vv_before_gt": dag_trace["post_vv_before_gt"],
                    "result_returned_to_root": dag_trace["result_returned_to_root"],
                }
            )
        provenance = {
            "request_id": request_id,
            "route": route,
            "execution_engine": dag_trace["execution_engine"] if dag_trace else "legacy_executor",
            "plan_id": plan_id,
            "gt_report_id": gt_report["gt_report_id"],
            "gt_decision": gt_report["decision"],
            "trace_path": f"trace:{request_id}",
            "created_by": "root_orchestrator",
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "drs_writeback",
                    "kind": "root_orchestrator",
                }
            ],
        }
        if dag_trace is not None:
            content["sensitive_input_absent"] = _sensitive_terms_absent(content, provenance)
        return {
            "record_id": f"work:{request_id}",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": content,
            "time_envelope": make_time_envelope(session_anchor),
            "provenance": provenance,
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
