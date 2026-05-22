import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"


def test_schema_files_are_valid_draft_2020_12_json_schemas():
    assert SCHEMAS_DIR.exists(), "schemas/ directory does not exist"

    schema_files = sorted(SCHEMAS_DIR.glob("*.schema.json"))
    assert schema_files, "schemas/ contains no *.schema.json files"

    for schema_file in schema_files:
        with schema_file.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)

        assert "$schema" in schema, f"{schema_file} is missing $schema"
        assert "$id" in schema, f"{schema_file} is missing $id"

        jsonschema.Draft202012Validator.check_schema(schema)
