import json
from pathlib import Path

import jsonschema

from hedgehog.drs import LocalDRS
from hedgehog.marenna import create_marenna_after_task_record
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.up import create_up_after_task_record


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"
FORBIDDEN_KEYS = {
    "final_output",
    "answer",
    "raw_user_text",
    "work_mutation",
    "external_action",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_validator(schema_name: str):
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    time_envelope_schema = load_json(SCHEMAS_DIR / "time_envelope.schema.json")
    target_schema = load_json(SCHEMAS_DIR / schema_name)
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        target_schema["$id"]: target_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(target_schema, store=store)
    return jsonschema.Draft202012Validator(target_schema, resolver=resolver)


def contains_forbidden_key(value):
    if isinstance(value, dict):
        return bool(FORBIDDEN_KEYS & set(value)) or any(
            contains_forbidden_key(child) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_forbidden_key(item) for item in value)
    return False


def test_marenna_after_task_record_validates_and_stays_quarantined():
    record = create_marenna_after_task_record(
        request_id="req_marenna_001",
        session_anchor="sess_marenna_001",
        work_record_id="work:req_marenna_001",
    )

    schema_validator("marenna_record.schema.json").validate(record)
    assert record["initial_layer"] == "quarantine"
    assert record["promotion_target_layer"] == "thoughts"
    assert record["provenance"]["created_by"] == "marenna"
    assert record["status"] == "quarantined"
    assert set(record["validation"]) == {
        "static",
        "dedup",
        "rag_support",
        "self_consistency",
        "utility",
        "safety",
    }
    assert not contains_forbidden_key(record)


def test_up_after_task_record_validates_and_stays_quarantined():
    record = create_up_after_task_record(
        request_id="req_up_001",
        session_anchor="sess_up_001",
        work_record_id="work:req_up_001",
    )

    schema_validator("up_record.schema.json").validate(record)
    assert record["initial_layer"] == "quarantine"
    assert record["promotion_target_layer"] == "up"
    assert record["provenance"]["created_by"] == "up"
    assert record["status"] == "quarantined"
    assert record["actionable"] is False
    assert set(record["validation"]) == {
        "static",
        "dedup",
        "rag_support",
        "self_consistency",
        "utility",
        "safety",
    }
    assert not contains_forbidden_key(record)


def test_root_orchestrator_writes_marenna_and_up_to_quarantine(tmp_path):
    drs = LocalDRS(tmp_path)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id="req_hooks_001",
        session_anchor="sess_hooks_001",
    )

    work_record = drs.read_record("work", final_output["drs_writes"][0])
    quarantine_records = drs.read_layer("quarantine")
    quarantine_ids = {record["record_id"] for record in quarantine_records}

    assert work_record["layer"] == "work"
    assert orchestrator.last_trace["marenna_records"]
    assert orchestrator.last_trace["up_records"]
    assert set(orchestrator.last_trace["marenna_records"]) <= quarantine_ids
    assert set(orchestrator.last_trace["up_records"]) <= quarantine_ids

    for record in quarantine_records:
        assert record["layer"] == "quarantine"
        assert record["provenance"]["created_by"] in {"marenna", "up"}
        assert not contains_forbidden_key(record)
