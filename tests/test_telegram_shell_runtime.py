import json
from pathlib import Path

from hedgehog.telegram_shell import handle_telegram_text


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_telegram_shell_returns_reply_debug_request_trace_and_status(tmp_path):
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_001",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
    )

    assert result["reply_text"]
    assert result["debug_text"]
    assert result["request_id"].startswith("tg:chat_001:")
    assert result["chat_id"] == "chat_001"
    assert result["trace_path"]
    assert result["final_status"] in {"success", "partial", "needs_user", "failed"}
    assert result["execution_mode"]
    assert result["route"]


def test_telegram_shell_debug_text_has_compact_summary(tmp_path):
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_debug",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
        debug=True,
    )

    debug_text = result["debug_text"]
    assert "[debug]" in debug_text
    assert "execution_mode:" in debug_text
    assert "route:" in debug_text
    assert "provider:" in debug_text
    assert "model:" in debug_text
    assert "used_llm:" in debug_text
    assert "llm_status:" in debug_text
    assert "llm_provider:" in debug_text
    assert "llm_model:" in debug_text
    assert "llm_used:" in debug_text
    assert "llm_error:" in debug_text
    assert "final_status:" in debug_text
    assert "drs_writes:" in debug_text
    assert "trace_path:" in debug_text


def test_telegram_shell_debug_false_still_writes_trace(tmp_path):
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_no_debug",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
        debug=False,
    )

    assert result["debug_text"] == ""
    assert Path(result["trace_path"]).exists()


def test_telegram_shell_trace_path_contains_json_trace(tmp_path):
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_trace",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
    )

    trace = read_json(Path(result["trace_path"]))
    assert trace["request_id"] == result["request_id"]
    assert trace["chat_id"] == "chat_trace"
    assert trace["final_output"]["request_id"] == result["request_id"]
    assert trace["trace"]["final_output"]["created_by"] == "root_orchestrator"


def test_telegram_shell_work_record_exists_without_raw_user_text(tmp_path):
    drs_root = tmp_path / "drs"
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_work",
        drs_root=drs_root,
        needles_dir=NEEDLES_DIR,
    )

    assert result["work_record_ids"]
    work_record_id = result["work_record_ids"][0]
    work_path = drs_root / "work" / f"{work_record_id.replace(':', '_')}.json"
    assert work_path.exists()
    work_record = read_json(work_path)
    assert not contains_key(work_record, "raw_user_text")


def test_telegram_shell_force_full_pipeline_for_generic_certificate_text(tmp_path):
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_full",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
        force_full_pipeline=True,
    )
    trace = read_json(Path(result["trace_path"]))

    assert result["execution_mode"] == "proof_full_pipeline"
    assert result["route"] == "proof_full_pipeline"
    assert trace["trace"]["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert trace["trace"].get("reflex_applied", False) is False
    assert trace["trace"].get("reuse_applied", False) is False
    assert trace["trace"]["plan_graph"]["nodes"]
    assert trace["trace"]["result_proposals"]


def test_telegram_shell_full_pipeline_can_surface_architect_diagnostics(tmp_path):
    result = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_architect_diag",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
        force_full_pipeline=True,
        architect_provider="mock_llm",
    )
    trace = read_json(Path(result["trace_path"]))

    assert result["execution_mode"] == "proof_full_pipeline"
    assert result["architect_provider"] == "mock"
    assert result["llm_architect_provider"] == "mock"
    assert result["llm_architect_status"] == "completed"
    assert result["llm_architect_used_llm"] is False
    assert "architect_provider: mock" in result["debug_text"]
    assert "llm_architect_provider: mock" in result["debug_text"]
    assert trace["trace"]["llm_architect_result"]["provider"] == "mock"


def test_telegram_shell_generic_math_routes_to_llm_general(tmp_path):
    result = handle_telegram_text(
        text="x + y = 110\nx - y = 100",
        chat_id="chat_math",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
        llm_provider="mock",
    )
    trace = read_json(Path(result["trace_path"]))

    assert result["reply_text"] == "x = 105\ny = 5"
    assert result["execution_mode"] == "llm_general"
    assert result["route"] == "llm_general"
    assert result["provider"] == "mock"
    assert result["used_llm"] is False
    assert result["llm_status"] == "completed"
    assert result["llm_provider"] == "mock"
    assert result["llm_model"] == "mock_general_responder_v1"
    assert result["llm_used"] is False
    assert result["llm_error"] == "none"
    assert "Mock certificate request pipeline completed" not in result["reply_text"]
    assert "execution_mode: llm_general" in result["debug_text"]
    assert "llm_status: completed" in result["debug_text"]
    assert "llm_provider: mock" in result["debug_text"]
    assert "llm_model: mock_general_responder_v1" in result["debug_text"]
    assert "llm_used: False" in result["debug_text"]
    assert "llm_error: none" in result["debug_text"]
    assert trace["trace"]["input_intake"]["intent_kind"] == "general_request"
    assert trace["trace"]["llm_gateway_result"]["provider"] == "mock"
    assert trace["debug_summary"]["llm_status"] == "completed"


def test_telegram_shell_llm_error_debug_is_safe_and_compact(tmp_path):
    result = handle_telegram_text(
        text="Explain this general request.",
        chat_id="chat_llm_error",
        drs_root=tmp_path / "drs",
        needles_dir=NEEDLES_DIR,
        llm_provider="unsupported_provider",
    )
    trace = read_json(Path(result["trace_path"]))

    assert result["execution_mode"] == "llm_general"
    assert result["llm_status"] == "error"
    assert result["llm_provider"] == "unsupported_provider"
    assert result["llm_used"] is False
    assert result["llm_error"] != "none"
    assert len(result["llm_error"]) <= 240
    assert "api_key" not in result["llm_error"].lower()
    assert "token" not in result["llm_error"].lower()
    assert "llm_error:" in result["debug_text"]
    assert trace["debug_summary"]["llm_status"] == "error"
    assert trace["debug_summary"]["llm_error"] == result["llm_error"]


def test_telegram_shell_reflex_priority_over_existing_work_context(tmp_path):
    drs_root = tmp_path / "drs"
    first = handle_telegram_text(
        text="I need a certificate for a mock government service.",
        chat_id="chat_reflex_context_source",
        drs_root=drs_root,
        needles_dir=NEEDLES_DIR,
        debug=True,
    )

    result = handle_telegram_text(
        text="turn on tv",
        chat_id="chat_reflex_context_priority",
        drs_root=drs_root,
        needles_dir=NEEDLES_DIR,
        debug=True,
        force_full_pipeline=False,
        allow_reflex=True,
    )
    trace = read_json(Path(result["trace_path"]))

    assert first["work_record_ids"]
    assert result["execution_mode"] == "deterministic_reflex"
    assert result["route"] == "deterministic_reflex"
    assert "execution_mode: deterministic_reflex" in result["debug_text"]
    assert "reflex_applied: True" in result["debug_text"]
    assert "architect_skipped: True" in result["debug_text"]
    assert "executor_skipped: True" in result["debug_text"]
    assert trace["trace"]["memory_context_applied"] is True
    assert first["work_record_ids"][0] in trace["trace"]["memory_source_record_ids"]
