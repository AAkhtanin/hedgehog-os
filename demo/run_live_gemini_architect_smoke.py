from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Any

from demo.run_root_native_full_canonical_e2e_trace import (
    RootNativeFullCanonicalE2EReport,
    collect_root_native_full_canonical_e2e_trace,
)
from hedgehog.architect import _make_deterministic_plan_graph
from hedgehog.llm_architect import make_plan_graph_with_llm
from hedgehog.llm_architect import validate_plan_graph_contract


TASK_TEXT = (
    "Create a safe certificate workflow plan and produce a Root-controlled "
    "trace artifact."
)
LIVE_ENV_GATE = "HEDGEHOG_ALLOW_LIVE_GEMINI"


@dataclass(frozen=True)
class LiveGeminiArchitectSmokeReport:
    source_report: RootNativeFullCanonicalE2EReport
    input: dict[str, Any]
    role_substitution: dict[str, Any]
    architect_artifact: dict[str, Any]
    boundary_checks: dict[str, Any]
    full_canonical_e2e_context: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _live_config_available(*, allow_config: bool = True) -> bool:
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get(
        "GOOGLE_GEMINI_API_KEY"
    ):
        return True
    if not allow_config:
        return False
    try:
        import config  # type: ignore
    except ImportError:
        return False
    return any(
        bool(getattr(config, name, None))
        for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY")
    )


def _input(
    *,
    live_requested: bool,
    live_available: bool,
    live_used: bool,
    skip_reason: str | None,
) -> dict[str, Any]:
    mode = "live_opt_in" if live_requested else "dry_run_default"
    fields: dict[str, Any] = {
        "task_id": "live_gemini_architect_smoke_certificate",
        "input_text": TASK_TEXT,
        "mode": mode,
        "live_requested": live_requested,
        "live_gemini_available": live_available,
        "live_gemini_used": live_used,
    }
    if skip_reason:
        fields["skip_reason"] = skip_reason
    fields.update(
        {
            "telegram_used": False,
            "real_external_action": False,
        }
    )
    return fields


def _role_substitution() -> dict[str, Any]:
    return {
        "substituted_role": "architect",
        "gemini_is_root": False,
        "gemini_is_orchestrator": False,
        "gemini_is_executor": False,
        "gemini_is_final_renderer": False,
        "gemini_is_gt": False,
        "gemini_writes_drs": False,
        "gemini_executes_actions": False,
        "gemini_creates_final_output": False,
    }


def _attempt_artifact(
    *,
    source_report: RootNativeFullCanonicalE2EReport,
    live_requested: bool,
    live_available: bool,
    injected_artifact: dict[str, Any] | None,
    model: str | None,
    allow_config: bool,
) -> tuple[dict[str, Any], bool]:
    attractor_packet = source_report.first_run_source.trace["attractor_packet"]
    deterministic_fallback = _make_deterministic_plan_graph(attractor_packet)
    validate_plan_graph_contract(deterministic_fallback, attractor_packet)

    live_called = False
    source = "deterministic_mock"
    artifact_received = True
    valid = True
    plan_graph_present = True
    invalid_caught = False
    contract_violation_contained = False
    fallback_to_deterministic = False
    executor_reached = False
    root_final_from_live = False

    if injected_artifact is not None:
        source = "injected_invalid"
        artifact_received = True
        try:
            validate_plan_graph_contract(injected_artifact, attractor_packet)
        except Exception:
            valid = False
            plan_graph_present = bool(injected_artifact)
            invalid_caught = True
            contract_violation_contained = True
            fallback_to_deterministic = True
        else:
            valid = True
            plan_graph_present = True
        return (
            {
                "architect_artifact_source": source,
                "architect_artifact_received": artifact_received,
                "architect_artifact_valid": valid,
                "plan_graph_contract_checked": True,
                "plan_graph_present": plan_graph_present,
                "invalid_artifact_caught": invalid_caught,
                "contract_violation_contained": contract_violation_contained,
                "fallback_to_deterministic_architect": fallback_to_deterministic,
                "executor_reached": executor_reached,
                "root_final_output_created_from_live_gemini": root_final_from_live,
            },
            live_called,
        )

    if live_requested:
        source = "live_gemini"
        if not live_available:
            return (
                {
                    "architect_artifact_source": source,
                    "architect_artifact_received": False,
                    "architect_artifact_valid": False,
                    "plan_graph_contract_checked": True,
                    "plan_graph_present": False,
                    "invalid_artifact_caught": False,
                    "contract_violation_contained": True,
                    "fallback_to_deterministic_architect": True,
                    "executor_reached": False,
                    "root_final_output_created_from_live_gemini": False,
                },
                live_called,
            )
        result = make_plan_graph_with_llm(
            attractor_packet=attractor_packet,
            provider="gemini",
            model=model,
            allow_config=allow_config,
        )
        live_called = bool(result.get("used_llm"))
        if result["status"] == "completed" and result["plan_graph"] is not None:
            validate_plan_graph_contract(result["plan_graph"], attractor_packet)
            return (
                {
                    "architect_artifact_source": source,
                    "architect_artifact_received": True,
                    "architect_artifact_valid": True,
                    "plan_graph_contract_checked": True,
                    "plan_graph_present": True,
                    "invalid_artifact_caught": False,
                    "contract_violation_contained": False,
                    "fallback_to_deterministic_architect": False,
                    "executor_reached": False,
                    "root_final_output_created_from_live_gemini": False,
                },
                live_called,
            )
        return (
            {
                "architect_artifact_source": source,
                "architect_artifact_received": bool(result.get("used_llm")),
                "architect_artifact_valid": False,
                "plan_graph_contract_checked": True,
                "plan_graph_present": False,
                "invalid_artifact_caught": bool(result.get("used_llm")),
                "contract_violation_contained": True,
                "fallback_to_deterministic_architect": True,
                "executor_reached": False,
                "root_final_output_created_from_live_gemini": False,
            },
            live_called,
        )

    return (
        {
            "architect_artifact_source": source,
            "architect_artifact_received": artifact_received,
            "architect_artifact_valid": valid,
            "plan_graph_contract_checked": True,
            "plan_graph_present": plan_graph_present,
            "invalid_artifact_caught": invalid_caught,
            "contract_violation_contained": contract_violation_contained,
            "fallback_to_deterministic_architect": fallback_to_deterministic,
            "executor_reached": executor_reached,
            "root_final_output_created_from_live_gemini": root_final_from_live,
        },
        live_called,
    )


def _boundary_checks(
    source_report: RootNativeFullCanonicalE2EReport,
    role: dict[str, Any],
    artifact: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    first_sections = source_report.first_run_source.sections
    full_canonical_pass = context["full_canonical_e2e_status"] == "PASS"
    architect_only = (
        role["substituted_role"] == "architect"
        and not role["gemini_is_root"]
        and not role["gemini_is_orchestrator"]
        and not role["gemini_is_executor"]
        and not role["gemini_is_final_renderer"]
        and not role["gemini_is_gt"]
        and not role["gemini_writes_drs"]
        and not role["gemini_executes_actions"]
        and not role["gemini_creates_final_output"]
    )
    avf_boundary_preserved = (
        full_canonical_pass
        and first_sections["avf_attractor"]["avf_runs_before_architect"]
        and first_sections["avf_attractor"]["attractor_packet_created"]
        and not first_sections["avf_attractor"][
            "architect_received_forbidden_vectors"
        ]
    )
    post_vv_boundary_preserved = (
        full_canonical_pass
        and first_sections["post_vv_gt"]["post_vv_after_dag_executor"]
        and first_sections["post_vv_gt"]["vv_reports_count"] > 0
    )
    gt_boundary_preserved = (
        full_canonical_pass
        and first_sections["post_vv_gt"]["gt_after_post_vv"]
        and not first_sections["post_vv_gt"]["gt_committed_final_output"]
    )
    root_boundary_preserved = (
        source_report.summary["first_run_root_authority_preserved"]
        and source_report.summary["second_run_root_authority_preserved"]
        and not artifact["root_final_output_created_from_live_gemini"]
    )
    reuse_gate_boundary_preserved = source_report.authority_safety[
        "reuse_gate_boundary_preserved"
    ]
    policy_bypassed = (
        not architect_only
        or role["gemini_executes_actions"]
        or role["gemini_writes_drs"]
        or role["gemini_creates_final_output"]
    )
    return {
        "avf_boundary_preserved": avf_boundary_preserved,
        "plan_graph_contract_preserved": artifact["plan_graph_contract_checked"],
        "executor_boundary_preserved": not artifact["executor_reached"],
        "post_vv_boundary_preserved": post_vv_boundary_preserved,
        "gt_boundary_preserved": gt_boundary_preserved,
        "root_boundary_preserved": root_boundary_preserved,
        "reuse_gate_boundary_preserved": reuse_gate_boundary_preserved,
        "gemini_bypassed_root": not root_boundary_preserved or not architect_only,
        "gemini_bypassed_orchestrator_boundary": not architect_only,
        "gemini_bypassed_avf": not avf_boundary_preserved,
        "gemini_bypassed_plan_graph_contract": not artifact[
            "plan_graph_contract_checked"
        ],
        "gemini_bypassed_post_vv": not post_vv_boundary_preserved,
        "gemini_bypassed_gt": not gt_boundary_preserved,
        "gemini_bypassed_policy": policy_bypassed,
    }


def _full_canonical_context(
    source_report: RootNativeFullCanonicalE2EReport,
) -> dict[str, Any]:
    return {
        "full_canonical_e2e_available": True,
        "full_canonical_e2e_status": source_report.summary[
            "root_native_full_canonical_e2e_trace_status"
        ],
        "first_run_stages_passed": source_report.summary["first_run_stages_passed"],
        "second_run_stages_passed": source_report.summary[
            "second_run_stages_passed"
        ],
        "deterministic_bridge_between_runs": source_report.summary[
            "deterministic_bridge_between_runs"
        ],
        "production_persistence_claimed": source_report.summary[
            "production_persistence_claimed"
        ],
        "production_reuse_claimed": source_report.summary["production_reuse_claimed"],
        "production_direct_reuse_executed": source_report.summary[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": source_report.summary[
            "production_final_output_created"
        ],
    }


def _authority_safety(
    role: dict[str, Any],
    boundary: dict[str, Any],
    source_report: RootNativeFullCanonicalE2EReport,
) -> dict[str, Any]:
    return {
        "root_authority_preserved": boundary["root_boundary_preserved"],
        "architect_role_is_bounded": role["substituted_role"] == "architect",
        "gemini_output_is_proposal_only": True,
        "gemini_created_final_output": role["gemini_creates_final_output"],
        "gemini_wrote_drs": role["gemini_writes_drs"],
        "gemini_executed_action": role["gemini_executes_actions"],
        "production_external_action_executed": source_report.authority_safety[
            "production_external_action_executed"
        ],
        "production_final_output_created": source_report.summary[
            "production_final_output_created"
        ],
        "production_work_record_written": source_report.summary[
            "production_work_record_written"
        ],
        "live_telegram_action_executed": False,
        "no_global_drs": source_report.authority_safety["no_global_drs"],
        "no_external_drs_network": source_report.authority_safety[
            "no_external_drs_network"
        ],
        "production_autonomy_claimed": source_report.authority_safety[
            "production_autonomy_claimed"
        ],
    }


def _summary(
    *,
    mode: str,
    live_used: bool,
    live_called: bool,
    live_requested: bool,
    live_available: bool,
    artifact: dict[str, Any],
    context: dict[str, Any],
    role: dict[str, Any],
    boundary: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    boundaries_pass = (
        context["full_canonical_e2e_status"] == "PASS"
        and boundary["avf_boundary_preserved"]
        and boundary["plan_graph_contract_preserved"]
        and boundary["executor_boundary_preserved"]
        and boundary["post_vv_boundary_preserved"]
        and boundary["gt_boundary_preserved"]
        and boundary["root_boundary_preserved"]
        and boundary["reuse_gate_boundary_preserved"]
        and not any(
            boundary[key]
            for key in (
                "gemini_bypassed_root",
                "gemini_bypassed_orchestrator_boundary",
                "gemini_bypassed_avf",
                "gemini_bypassed_plan_graph_contract",
                "gemini_bypassed_post_vv",
                "gemini_bypassed_gt",
                "gemini_bypassed_policy",
            )
        )
        and role["substituted_role"] == "architect"
        and not role["gemini_creates_final_output"]
        and not role["gemini_writes_drs"]
        and not role["gemini_executes_actions"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["production_work_record_written"]
        and not authority["production_autonomy_claimed"]
    )
    live_failure_contained = (
        not live_requested
        or (live_requested and not live_available)
        or artifact["architect_artifact_valid"]
        or (
            artifact["invalid_artifact_caught"]
            and artifact["contract_violation_contained"]
            and artifact["fallback_to_deterministic_architect"]
            and not artifact["executor_reached"]
            and not artifact["root_final_output_created_from_live_gemini"]
        )
    )
    if live_requested and not live_available:
        status = "SKIPPED" if boundaries_pass else "FAIL"
    else:
        status = "PASS" if boundaries_pass and live_failure_contained else "FAIL"
    return {
        "live_gemini_architect_smoke_status": status,
        "mode": mode,
        "live_gemini_used": live_used,
        "live_gemini_called": live_called,
        "architect_artifact_valid": artifact["architect_artifact_valid"],
        "invalid_artifact_caught": artifact["invalid_artifact_caught"],
        "fallback_to_deterministic_architect": artifact[
            "fallback_to_deterministic_architect"
        ],
        "full_canonical_e2e_status": context["full_canonical_e2e_status"],
        "root_authority_preserved": authority["root_authority_preserved"],
        "gemini_authority_granted": False,
        "gemini_created_final_output": authority["gemini_created_final_output"],
        "gemini_wrote_drs": authority["gemini_wrote_drs"],
        "gemini_executed_action": authority["gemini_executed_action"],
        "production_final_output_created": authority[
            "production_final_output_created"
        ],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "ready_for_future_orchestrator_live_smoke": boundaries_pass
        and live_failure_contained,
    }


def collect_live_gemini_architect_smoke(
    *,
    live_requested: bool = False,
    allow_config: bool = True,
    model: str | None = None,
    injected_artifact: dict[str, Any] | None = None,
) -> LiveGeminiArchitectSmokeReport:
    source_report = collect_root_native_full_canonical_e2e_trace()
    live_gate_enabled = os.environ.get(LIVE_ENV_GATE) == "1"
    live_available = live_requested and live_gate_enabled and _live_config_available(
        allow_config=allow_config
    )
    skip_reason = (
        "missing_live_gemini_configuration"
        if live_requested and not live_available
        else None
    )
    artifact, live_called = _attempt_artifact(
        source_report=source_report,
        live_requested=live_requested,
        live_available=live_available,
        injected_artifact=injected_artifact,
        model=model,
        allow_config=allow_config,
    )
    live_used = live_available and live_called
    input_fields = _input(
        live_requested=live_requested,
        live_available=live_available,
        live_used=live_used,
        skip_reason=skip_reason,
    )
    context = _full_canonical_context(source_report)
    role = _role_substitution()
    boundary = _boundary_checks(source_report, role, artifact, context)
    authority = _authority_safety(role, boundary, source_report)
    summary = _summary(
        mode=input_fields["mode"],
        live_used=live_used,
        live_called=live_called,
        live_requested=live_requested,
        live_available=live_available,
        artifact=artifact,
        context=context,
        role=role,
        boundary=boundary,
        authority=authority,
    )
    return LiveGeminiArchitectSmokeReport(
        source_report=source_report,
        input=input_fields,
        role_substitution=role,
        architect_artifact=artifact,
        boundary_checks=boundary,
        full_canonical_e2e_context=context,
        authority_safety=authority,
        summary=summary,
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def render_live_gemini_architect_smoke(
    report: LiveGeminiArchitectSmokeReport,
) -> str:
    lines = [
        "[LIVE GEMINI ARCHITECT SMOKE]",
        "note: opt-in live Gemini Architect-role smoke",
        "note: Gemini substitutes Architect proposal role only",
        "note: no production RootOrchestrator behavior change",
        "note: no live Telegram action",
        "note: no real external actions except optional Gemini model call",
        "note: no production FinalOutput created by Gemini",
        "note: no DRS write by Gemini",
        "note: no production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Root remains final authority",
        "note: PlanGraph contract / Post V&V / GT / Root boundaries preserved",
        "",
        "[INPUT]",
    ]
    lines.extend(_field_lines(report.input))
    lines.extend(["", "[ROLE SUBSTITUTION]"])
    lines.extend(_field_lines(report.role_substitution))
    lines.extend(["", "[ARCHITECT ARTIFACT]"])
    lines.extend(_field_lines(report.architect_artifact))
    lines.extend(["", "[BOUNDARY CHECKS]"])
    lines.extend(_field_lines(report.boundary_checks))
    lines.extend(["", "[FULL CANONICAL E2E CONTEXT]"])
    lines.extend(_field_lines(report.full_canonical_e2e_context))
    lines.extend(["", "[AUTHORITY / SAFETY]"])
    lines.extend(_field_lines(report.authority_safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_live_gemini_architect_smoke(*, live_requested: bool = False) -> str:
    return render_live_gemini_architect_smoke(
        collect_live_gemini_architect_smoke(live_requested=live_requested)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run optional Live Gemini Architect smoke proof."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Opt in to a live Gemini Architect-only model call when configured.",
    )
    args = parser.parse_args()
    print(run_live_gemini_architect_smoke(live_requested=args.live), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
