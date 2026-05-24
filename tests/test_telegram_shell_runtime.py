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
