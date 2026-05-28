from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from demo.run_live_controlled_smoke import _result as live_controlled_smoke_result
from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator


def _sanitize_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)


def _make_request_id(chat_id: str, text: str) -> str:
    chat_part = _sanitize_id(chat_id) or "chat"
    digest = hashlib.sha256(f"{chat_id}\n{text}".encode("utf-8")).hexdigest()[:10]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"tg:{chat_part}:{stamp}:{digest}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


def _trace_file_path(drs_root: Path, request_id: str) -> Path:
    safe_request_id = _sanitize_id(request_id)
    return drs_root.parent / "logs" / "traces" / f"{safe_request_id}.json"


def _trace_value(trace: dict, key: str, default: Any = None) -> Any:
    return trace.get(key, default)


def _short_error(value: Any, limit: int = 240) -> str:
    if not value:
        return "none"
    line = " ".join(str(value).split())
    if len(line) <= limit:
        return line
    return f"{line[: limit - 3]}..."


def _debug_summary(trace: dict, final_output: dict, trace_path: Path) -> dict:
    mode_router = trace.get("mode_router", {})
    gt_report = trace.get("gt_report") or {}
    llm_result = trace.get("llm_gateway_result")
    llm_architect = trace.get("llm_architect_result") or {}
    drs_writes = final_output.get("drs_writes", [])
    execution_mode = (
        trace.get("execution_mode")
        or mode_router.get("execution_mode")
        or "unknown"
    )
    route = trace.get("route") or execution_mode
    return {
        "request_id": final_output["request_id"],
        "execution_mode": execution_mode,
        "route": route,
        "provider": (llm_result or {}).get("provider", "none"),
        "model": (llm_result or {}).get("model", "none"),
        "used_llm": bool((llm_result or {}).get("used_llm", False)),
        "llm_status": (llm_result or {}).get("status", "none"),
        "llm_provider": (llm_result or {}).get("provider", "none"),
        "llm_model": (llm_result or {}).get("model", "none"),
        "llm_used": bool((llm_result or {}).get("used_llm", False)),
        "llm_error": _short_error((llm_result or {}).get("error")),
        "general_provider": (llm_result or {}).get("provider", "none"),
        "general_model": (llm_result or {}).get("model", "none"),
        "general_llm_used": bool((llm_result or {}).get("used_llm", False)),
        "general_llm_status": (llm_result or {}).get("status", "none"),
        "general_llm_error": _short_error((llm_result or {}).get("error")),
        "architect_provider": llm_architect.get("provider")
        or trace.get("architect_provider", "deterministic"),
        "architect_model": llm_architect.get("model", "none"),
        "architect_llm_used": bool(llm_architect.get("used_llm", False)),
        "architect_status": llm_architect.get("status", "none"),
        "architect_fallback": llm_architect.get("fallback", "none"),
        "architect_error": _short_error(llm_architect.get("error")),
        "llm_architect_status": llm_architect.get("status", "none"),
        "llm_architect_provider": llm_architect.get("provider", "none"),
        "llm_architect_model": llm_architect.get("model", "none"),
        "llm_architect_used_llm": bool(llm_architect.get("used_llm", False)),
        "llm_architect_fallback": llm_architect.get("fallback", "none"),
        "llm_architect_error": _short_error(llm_architect.get("error")),
        "final_status": final_output["status"],
        "memory_context_applied": bool(trace.get("memory_context_applied", False)),
        "reuse_decision": trace.get("reuse_decision", "none"),
        "reuse_applied": bool(trace.get("reuse_applied", False)),
        "reflex_applied": bool(trace.get("reflex_applied", False)),
        "direct_reuse_applied": bool(trace.get("reuse_applied", False))
        and trace.get("reuse_decision") == "direct_reuse",
        "architect_skipped": bool(trace.get("architect_skipped", False)),
        "executor_skipped": bool(trace.get("executor_skipped", False)),
        "gt_decision": gt_report.get("decision", "none"),
        "drs_writes": list(drs_writes),
        "trace_path": str(trace_path),
    }


def _format_debug_text(summary: dict) -> str:
    lines = ["[debug]"]
    for key in [
        "request_id",
        "execution_mode",
        "route",
        "provider",
        "model",
        "used_llm",
        "llm_status",
        "llm_provider",
        "llm_model",
        "llm_used",
        "llm_error",
        "general_provider",
        "general_model",
        "general_llm_used",
        "general_llm_status",
        "general_llm_error",
        "architect_provider",
        "architect_model",
        "architect_llm_used",
        "architect_status",
        "architect_fallback",
        "architect_error",
        "llm_architect_status",
        "llm_architect_provider",
        "llm_architect_model",
        "llm_architect_used_llm",
        "llm_architect_fallback",
        "llm_architect_error",
        "final_status",
        "memory_context_applied",
        "reuse_decision",
        "reuse_applied",
        "reflex_applied",
        "direct_reuse_applied",
        "architect_skipped",
        "executor_skipped",
        "gt_decision",
        "drs_writes",
        "trace_path",
    ]:
        lines.append(f"{key}: {summary[key]}")
    return "\n".join(lines)


def _is_controlled_smoke_command(text: str) -> bool:
    return text.strip().lower() in {"/controlled_gemini", "/full_controlled_gemini"}


def _controlled_smoke_debug_text(summary: dict) -> str:
    lines = ["[debug]"]
    for key in [
        "request_id",
        "execution_mode",
        "route",
        "orchestrator_provider",
        "orchestrator_proposal_valid",
        "suggested_route",
        "guard_completeness_score",
        "guards_complete",
        "integration_gate_decision",
        "controlled_execution_performed",
        "architect_provider",
        "architect_llm_used",
        "gt_decision",
        "final_status",
        "root_final_authority",
        "root_created_final_output",
        "uncontrolled_delegation",
        "no_real_external_action",
        "drs_writes",
        "trace_path",
    ]:
        lines.append(f"{key}: {summary[key]}")
    return "\n".join(lines)


def _handle_controlled_smoke_command(
    *,
    text: str,
    chat_id: str,
    drs_root: Path,
    debug: bool,
    llm_provider: str,
) -> dict:
    request_id = _make_request_id(chat_id, text)
    provider = "gemini" if llm_provider == "gemini" else "mock"
    result = live_controlled_smoke_result(provider=provider)
    proposal_valid = result.proposal.proposal_status == "valid"
    trace_path = _trace_file_path(drs_root, request_id)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    reply_text = (
        "Controlled Gemini smoke completed."
        if result.controlled_execution_performed
        else "Controlled Gemini smoke safely blocked."
    )
    summary = {
        "request_id": request_id,
        "execution_mode": result.root.execution_mode,
        "route": result.root.route,
        "orchestrator_provider": result.proposal.provider,
        "orchestrator_proposal_valid": proposal_valid,
        "suggested_route": result.proposal.suggested_route,
        "guard_completeness_score": f"{result.guard_quality.guard_completeness_score:.2f}",
        "guards_complete": result.guard_quality.guards_complete,
        "integration_gate_decision": result.gate_decision,
        "controlled_execution_performed": result.controlled_execution_performed,
        "architect_provider": result.root.architect_provider,
        "architect_llm_used": result.root.architect_llm_used,
        "gt_decision": result.root.gt_decision,
        "final_status": result.root.final_status,
        "root_final_authority": result.root.root_final_authority,
        "root_created_final_output": result.root.root_created_final_output,
        "uncontrolled_delegation": False,
        "no_real_external_action": True,
        "drs_writes": result.root.drs_write_count,
        "trace_path": str(trace_path),
    }
    trace_payload = {
        "request_id": request_id,
        "chat_id": chat_id,
        "message_summary": {"command": text.strip().lower()},
        "final_output": {
            "request_id": request_id,
            "created_by": "root_orchestrator" if result.root.root_created_final_output else "none",
            "status": result.root.final_status,
            "answer": reply_text,
            "drs_writes": [],
        },
        "debug_summary": summary,
        "trace": {
            "execution_mode": result.root.execution_mode,
            "route": result.root.route,
            "controlled_execution_performed": result.controlled_execution_performed,
            "orchestrator_provider": result.proposal.provider,
            "suggested_route": result.proposal.suggested_route,
            "integration_gate_decision": result.gate_decision,
            "root_final_authority": result.root.root_final_authority,
            "no_real_external_action": True,
        },
    }
    trace_path.write_text(
        json.dumps(_json_safe(trace_payload), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "reply_text": reply_text,
        "debug_text": _controlled_smoke_debug_text(summary) if debug else "",
        "request_id": request_id,
        "chat_id": chat_id,
        "trace_path": str(trace_path),
        "work_record_ids": [],
        "final_status": result.root.final_status,
        "execution_mode": result.root.execution_mode,
        "route": result.root.route,
        "orchestrator_provider": result.proposal.provider,
        "orchestrator_proposal_valid": proposal_valid,
        "suggested_route": result.proposal.suggested_route,
        "guard_completeness_score": summary["guard_completeness_score"],
        "guards_complete": result.guard_quality.guards_complete,
        "integration_gate_decision": result.gate_decision,
        "controlled_execution_performed": result.controlled_execution_performed,
        "architect_provider": result.root.architect_provider,
        "architect_llm_used": result.root.architect_llm_used,
        "gt_decision": result.root.gt_decision,
        "root_final_authority": result.root.root_final_authority,
        "root_created_final_output": result.root.root_created_final_output,
        "uncontrolled_delegation": False,
        "no_real_external_action": True,
    }


def handle_telegram_text(
    *,
    text: str,
    chat_id: str,
    drs_root: Path,
    needles_dir: Path,
    debug: bool = True,
    force_full_pipeline: bool = True,
    llm_provider: str = "mock",
    llm_model: str | None = None,
    architect_provider: str = "deterministic",
    architect_model: str | None = None,
    architect_allow_config: bool = True,
    allow_reflex: bool = False,
    user_confirmed: bool = False,
) -> dict:
    drs_root = Path(drs_root)
    if _is_controlled_smoke_command(text):
        return _handle_controlled_smoke_command(
            text=text,
            chat_id=chat_id,
            drs_root=drs_root,
            debug=debug,
            llm_provider=llm_provider,
        )

    request_id = _make_request_id(chat_id, text)
    session_anchor = f"telegram:{chat_id}"
    drs = LocalDRS(drs_root)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=Path(needles_dir))

    final_output = orchestrator.process_event(
        raw_user_text=text,
        request_id=request_id,
        session_anchor=session_anchor,
        force_full_pipeline=force_full_pipeline,
        llm_provider=llm_provider,
        llm_model=llm_model,
        architect_provider=architect_provider,
        architect_model=architect_model,
        architect_allow_config=architect_allow_config,
        allow_reflex=allow_reflex,
        user_confirmed=user_confirmed,
    )

    trace_path = _trace_file_path(drs_root, request_id)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    summary = _debug_summary(orchestrator.last_trace, final_output, trace_path)
    trace_payload = {
        "request_id": request_id,
        "chat_id": chat_id,
        "message_summary": {
            "text_length": len(text),
        },
        "final_output": final_output,
        "debug_summary": summary,
        "trace": orchestrator.last_trace,
    }
    trace_path.write_text(
        json.dumps(_json_safe(trace_payload), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return {
        "reply_text": final_output["answer"],
        "debug_text": _format_debug_text(summary) if debug else "",
        "request_id": request_id,
        "chat_id": chat_id,
        "trace_path": str(trace_path),
        "work_record_ids": list(final_output.get("drs_writes", [])),
        "final_status": final_output["status"],
        "execution_mode": summary["execution_mode"],
        "route": summary["route"],
        "provider": summary["provider"],
        "model": summary["model"],
        "used_llm": summary["used_llm"],
        "llm_status": summary["llm_status"],
        "llm_provider": summary["llm_provider"],
        "llm_model": summary["llm_model"],
        "llm_used": summary["llm_used"],
        "llm_error": summary["llm_error"],
        "general_provider": summary["general_provider"],
        "general_model": summary["general_model"],
        "general_llm_used": summary["general_llm_used"],
        "general_llm_status": summary["general_llm_status"],
        "general_llm_error": summary["general_llm_error"],
        "architect_provider": summary["architect_provider"],
        "architect_model": summary["architect_model"],
        "architect_llm_used": summary["architect_llm_used"],
        "architect_status": summary["architect_status"],
        "architect_fallback": summary["architect_fallback"],
        "architect_error": summary["architect_error"],
        "llm_architect_status": summary["llm_architect_status"],
        "llm_architect_provider": summary["llm_architect_provider"],
        "llm_architect_model": summary["llm_architect_model"],
        "llm_architect_used_llm": summary["llm_architect_used_llm"],
        "llm_architect_fallback": summary["llm_architect_fallback"],
        "llm_architect_error": summary["llm_architect_error"],
    }
