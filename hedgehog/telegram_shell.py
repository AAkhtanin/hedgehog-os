from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
) -> dict:
    drs_root = Path(drs_root)
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
    }
