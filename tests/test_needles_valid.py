import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"
SECRET_KEYS = {
    "credential",
    "credentials",
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from iter_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from iter_keys(item)


def assert_no_secret_keys(path: Path, payload):
    keys = {key.lower() for key in iter_keys(payload)}
    suspicious = sorted(keys & SECRET_KEYS)
    assert not suspicious, f"{path} contains suspicious secret keys: {suspicious}"


def vectors_by_id(needle):
    return {vector["vector_id"]: vector for vector in needle.get("declared_vectors", [])}


def candidate_vector_validator(candidate_schema, common_schema):
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        candidate_schema["$id"]: candidate_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(candidate_schema, store=store)
    return jsonschema.Draft202012Validator(candidate_schema, resolver=resolver)


def test_needle_files_and_declared_vectors_are_valid():
    government_path = NEEDLES_DIR / "government_services.json"
    fallback_path = NEEDLES_DIR / "fallback_exploration.json"
    common_schema_path = SCHEMAS_DIR / "common.schema.json"
    candidate_schema_path = SCHEMAS_DIR / "candidate_vector.schema.json"

    assert government_path.exists(), "needles/government_services.json does not exist"
    assert fallback_path.exists(), "needles/fallback_exploration.json does not exist"
    assert common_schema_path.exists(), "schemas/common.schema.json does not exist"
    assert candidate_schema_path.exists(), "schemas/candidate_vector.schema.json does not exist"

    government = load_json(government_path)
    fallback = load_json(fallback_path)
    common_schema = load_json(common_schema_path)
    candidate_schema = load_json(candidate_schema_path)

    assert_no_secret_keys(government_path, government)
    assert_no_secret_keys(fallback_path, fallback)

    validator = candidate_vector_validator(candidate_schema, common_schema)

    for needle_path, needle in (
        (government_path, government),
        (fallback_path, fallback),
    ):
        vectors = needle.get("declared_vectors")
        assert isinstance(vectors, list), f"{needle_path} declared_vectors must be a list"
        assert vectors, f"{needle_path} declared_vectors must not be empty"
        for vector in vectors:
            validator.validate(vector)

    government_vectors = vectors_by_id(government)
    fallback_vectors = vectors_by_id(fallback)

    illegal_coercion = government_vectors.get("illegal_coercion")
    assert illegal_coercion is not None, "illegal_coercion vector is missing"
    assert illegal_coercion["hard_forbidden"] is True
    assert illegal_coercion["branching_hint"] == "forbidden"
    assert illegal_coercion["source"] == "needle"
    assert illegal_coercion["domain"] == "government_certificate"

    fallback_exploration = fallback_vectors.get("fallback_exploration")
    assert fallback_exploration is not None, "fallback_exploration vector is missing"
    assert fallback_exploration["source"] == "fallback_template"
    assert fallback_exploration["requires_architect_creativity"] is True
    assert fallback_exploration["hard_forbidden"] is False
