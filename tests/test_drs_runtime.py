import json
from pathlib import Path

import jsonschema
import pytest

from hedgehog.drs import LocalDRS
from hedgehog.time_model import make_temporal_query, make_time_envelope


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def drs_record_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    time_envelope_schema = load_json(SCHEMAS_DIR / "time_envelope.schema.json")
    drs_record_schema = load_json(SCHEMAS_DIR / "drs_record.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        drs_record_schema["$id"]: drs_record_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(drs_record_schema, store=store)
    return jsonschema.Draft202012Validator(drs_record_schema, resolver=resolver)


def make_record(record_id="record_001", layer="work", record_type="task_outcome"):
    return {
        "record_id": record_id,
        "layer": layer,
        "type": record_type,
        "domain": "government_certificate",
        "content": {
            "summary": "Mock certificate result."
        },
        "time_envelope": make_time_envelope("sess_drs_001"),
        "provenance": {
            "request_id": "req_drs_001",
            "created_by": "root_orchestrator",
            "trace_refs": [
                {
                    "trace_id": "trace_drs_001"
                }
            ],
        },
        "status": "accepted",
    }


def test_local_drs_writes_reads_and_validates_work_record(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()
    written_path = drs.write_record(record)

    assert written_path.exists()
    loaded = drs.read_record("work", "record_001")
    assert loaded == record
    drs_record_validator().validate(loaded)


def test_local_drs_writes_pointer_record(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record(
        record_id="identity_pointer_001",
        layer="work",
        record_type="identity_pointer",
    )
    record["domain"] = "user_identity"
    record["content"] = {
        "summary": "Pointer to secure local vault record."
    }
    record["pointer"] = {
        "storage_kind": "local_secure_vault",
        "ref": "vault://identity/passport/main",
        "access_policy": {
            "visibility": "private",
            "requires_user_confirmation": True,
            "read_summary_only": True,
            "read_payload_allowed": False,
            "write_allowed": False,
            "allowed_use": ["form_filling"],
            "forbidden_use": ["sharing_without_confirmation"],
        },
        "summary": "Secure identity vault pointer",
        "hash": "mock_hash",
    }

    path = drs.write_record(record)
    loaded = drs.read_record("work", "identity_pointer_001")

    assert path.exists()
    assert loaded == record
    drs_record_validator().validate(loaded)


def test_write_record_rejects_secret_like_content_keys(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()
    record["content"] = {
        "passport_number": "DO_NOT_STORE"
    }

    with pytest.raises(ValueError):
        drs.write_record(record)


def test_write_record_rejects_nested_secret_like_keys(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()
    record["content"] = {
        "nested": {
            "credentials": {
                "username": "x"
            }
        }
    }

    with pytest.raises(ValueError):
        drs.write_record(record)


def test_write_record_rejects_malformed_pointer(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record(record_type="document_pointer")
    record["pointer"] = {
        "storage_kind": "local_secure_vault"
    }

    with pytest.raises(ValueError):
        drs.write_record(record)


def test_write_record_allows_identical_duplicate_write(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()

    first_path = drs.write_record(record)
    second_path = drs.write_record(record)

    assert second_path == first_path


def test_write_record_allows_same_object_with_different_existing_format(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()
    written_path = drs.write_record(record)
    written_path.write_text(json.dumps(record), encoding="utf-8")

    assert drs.write_record(record) == written_path


def test_write_record_rejects_different_object_with_same_record_id(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()
    drs.write_record(record)
    changed_record = make_record()
    changed_record["content"]["summary"] = "Different result."

    with pytest.raises(ValueError):
        drs.write_record(changed_record)


def test_write_record_rejects_missing_time_envelope(tmp_path):
    drs = LocalDRS(tmp_path)
    record = make_record()
    del record["time_envelope"]

    with pytest.raises(ValueError):
        drs.write_record(record)


def test_query_records_requires_temporal_query(tmp_path):
    drs = LocalDRS(tmp_path)

    with pytest.raises(ValueError):
        drs.query_records({}, ["work"])


def test_query_records_reads_only_requested_layers_and_keeps_layers_separate(tmp_path):
    drs = LocalDRS(tmp_path)
    work_record = make_record(record_id="work_001", layer="work")
    thought_record = make_record(
        record_id="thought_001",
        layer="thoughts",
        record_type="reflection",
    )
    drs.write_record(work_record)
    drs.write_record(thought_record)

    work_results = drs.query_records(make_temporal_query(), ["work"])
    thought_results = drs.query_records(make_temporal_query(), ["thoughts"])

    assert [record["record_id"] for record in work_results] == ["work_001"]
    assert [record["record_id"] for record in thought_results] == ["thought_001"]
    assert drs.read_layer("work")[0]["layer"] == "work"
    assert drs.read_layer("thoughts")[0]["layer"] == "thoughts"


def test_invalid_layer_raises_value_error(tmp_path):
    drs = LocalDRS(tmp_path)

    with pytest.raises(ValueError):
        drs.layer_path("weather")


def test_gitkeep_files_are_ignored(tmp_path):
    drs = LocalDRS(tmp_path)
    work_path = drs.layer_path("work")
    (work_path / ".gitkeep").write_text("", encoding="utf-8")

    assert drs.read_layer("work") == []
