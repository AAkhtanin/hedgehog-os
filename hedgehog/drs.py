from __future__ import annotations

import json
from pathlib import Path


DRS_LAYERS = {"work", "thoughts", "up", "quarantine", "deadends"}
REQUIRED_RECORD_FIELDS = {
    "record_id",
    "layer",
    "type",
    "domain",
    "content",
    "time_envelope",
    "provenance",
    "status",
}
SENSITIVE_KEY_FRAGMENTS = {
    "credential",
    "credentials",
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "private_key",
    "card_number",
    "cvv",
    "passport_number",
}


def _safe_filename(record_id: str) -> str:
    safe = "".join(char if char.isalnum() or char in "._-" else "_" for char in record_id)
    return f"{safe}.json"


def iter_json_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from iter_json_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_keys(item)


def assert_no_sensitive_drs_keys(record: dict) -> None:
    for key in iter_json_keys(record):
        normalized = key.lower()
        if any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS):
            raise ValueError(f"DRS record contains sensitive key name: {key}")


def _validate_pointer(record: dict) -> None:
    if "pointer" not in record:
        return
    pointer = record["pointer"]
    if not isinstance(pointer, dict):
        raise ValueError("DRS record pointer must be an object")
    if "storage_kind" not in pointer or "ref" not in pointer:
        raise ValueError("DRS record pointer requires storage_kind and ref")


class LocalDRS:
    def __init__(self, root_path: Path | str = "data/drs"):
        self.root_path = Path(root_path)

    def layer_path(self, layer: str) -> Path:
        if layer not in DRS_LAYERS:
            raise ValueError(f"invalid DRS layer: {layer}")
        path = self.root_path / layer
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_record(self, record: dict) -> Path:
        missing = REQUIRED_RECORD_FIELDS - set(record)
        if missing:
            raise ValueError(f"DRS record missing required fields: {sorted(missing)}")
        if not record.get("time_envelope"):
            raise ValueError("DRS record requires time_envelope")
        assert_no_sensitive_drs_keys(record)
        _validate_pointer(record)

        layer = record["layer"]
        path = self.layer_path(layer) / _safe_filename(record["record_id"])
        payload = json.dumps(record, indent=2, sort_keys=True)

        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                existing = json.load(handle)
            if existing != record:
                raise ValueError(f"DRS record already exists with different content: {path}")
            return path

        path.write_text(payload, encoding="utf-8")
        return path

    def read_record(self, layer: str, record_id: str) -> dict:
        path = self.layer_path(layer) / _safe_filename(record_id)
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def read_layer(self, layer: str) -> list[dict]:
        path = self.layer_path(layer)
        records = []
        for record_path in sorted(path.glob("*.json")):
            with record_path.open("r", encoding="utf-8") as handle:
                records.append(json.load(handle))
        return records

    def query_records(self, temporal_query: dict, layers: list[str]) -> list[dict]:
        if not temporal_query or "as_of" not in temporal_query:
            raise ValueError("TemporalQuery with as_of is required")

        records = []
        for layer in layers:
            for record in self.read_layer(layer):
                if record.get("time_envelope"):
                    records.append(json.loads(json.dumps(record)))
        return records
