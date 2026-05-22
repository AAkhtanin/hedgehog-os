import json
from pathlib import Path

import jsonschema

from hedgehog.drs import LocalDRS, SENSITIVE_KEY_FRAGMENTS
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def final_output_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    time_envelope_schema = load_json(SCHEMAS_DIR / "time_envelope.schema.json")
    final_output_schema = load_json(SCHEMAS_DIR / "final_output.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        final_output_schema["$id"]: final_output_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(final_output_schema, store=store)
    return jsonschema.Draft202012Validator(final_output_schema, resolver=resolver)


def make_orchestrator(tmp_path):
    drs = LocalDRS(tmp_path)
    return RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR), drs


def run_demo(tmp_path, request_id="req_root_001"):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id=request_id,
        session_anchor="sess_root_001",
    )
    return orchestrator, drs, final_output


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def contains_sensitive_key(value):
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower()
            if any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS):
                return True
            if contains_sensitive_key(child):
                return True
    if isinstance(value, list):
        return any(contains_sensitive_key(item) for item in value)
    return False


def test_root_orchestrator_creates_valid_final_output_and_work_record(tmp_path):
    _, drs, final_output = run_demo(tmp_path)

    final_output_validator().validate(final_output)
    assert final_output["created_by"] == "root_orchestrator"
    assert final_output["status"] in {"success", "partial", "needs_user", "failed"}
    assert final_output["answer"]
    assert final_output["used_proposals"]
    assert final_output["drs_writes"]

    work_record = drs.read_record("work", final_output["drs_writes"][0])
    assert work_record["layer"] == "work"
    assert work_record["time_envelope"]
    assert {"pt_created_at", "kt_asof", "ct_session_anchor", "ttl_seconds"} <= set(
        work_record["time_envelope"]
    )
    assert work_record["provenance"]["created_by"] == "root_orchestrator"


def test_root_orchestrator_does_not_persist_raw_text_or_sensitive_content_keys(tmp_path):
    _, drs, final_output = run_demo(tmp_path, request_id="req_root_002")
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    assert not contains_key(final_output, "raw_user_text")
    assert not contains_key(work_record, "raw_user_text")
    assert not contains_sensitive_key(work_record["content"])


def test_root_orchestrator_excludes_forbidden_vector_from_output_and_drs(tmp_path):
    orchestrator, drs, final_output = run_demo(tmp_path, request_id="req_root_003")
    work_record = drs.read_record("work", final_output["drs_writes"][0])
    node_vector_ids = {
        node["vector_id"] for node in orchestrator.last_trace["plan_graph"]["nodes"]
    }
    proposal_vector_ids = {
        proposal["vector_id"] for proposal in orchestrator.last_trace["result_proposals"]
    }

    assert "illegal_coercion" not in node_vector_ids
    assert "illegal_coercion" not in proposal_vector_ids
    assert all("illegal_coercion" not in proposal_id for proposal_id in final_output["used_proposals"])
    assert "illegal_coercion" not in json.dumps(work_record["content"], sort_keys=True)


def test_root_orchestrator_final_output_references_gt_report_from_trace(tmp_path):
    orchestrator, _, final_output = run_demo(tmp_path, request_id="req_root_004")
    gt_report = orchestrator.last_trace["gt_report"]

    assert gt_report["gt_report_id"]
    assert final_output["gt_report_ref"] == gt_report["gt_report_id"]
    assert orchestrator.last_trace["final_output"] == final_output
