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


def needle_validator(needle_schema, candidate_schema, common_schema):
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        candidate_schema["$id"]: candidate_schema,
        "candidate_vector.schema.json": candidate_schema,
        "https://hedgehog-os.local/schemas/candidate_vector.schema.json": candidate_schema,
        needle_schema["$id"]: needle_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(needle_schema, store=store)
    return jsonschema.Draft202012Validator(needle_schema, resolver=resolver)


def test_needle_files_and_declared_vectors_are_valid():
    government_path = NEEDLES_DIR / "government_services.json"
    fallback_path = NEEDLES_DIR / "fallback_exploration.json"
    common_schema_path = SCHEMAS_DIR / "common.schema.json"
    candidate_schema_path = SCHEMAS_DIR / "candidate_vector.schema.json"
    needle_schema_path = SCHEMAS_DIR / "needle.schema.json"

    assert government_path.exists(), "needles/government_services.json does not exist"
    assert fallback_path.exists(), "needles/fallback_exploration.json does not exist"
    assert common_schema_path.exists(), "schemas/common.schema.json does not exist"
    assert candidate_schema_path.exists(), "schemas/candidate_vector.schema.json does not exist"
    assert needle_schema_path.exists(), "schemas/needle.schema.json does not exist"

    government = load_json(government_path)
    fallback = load_json(fallback_path)
    common_schema = load_json(common_schema_path)
    candidate_schema = load_json(candidate_schema_path)
    needle_schema = load_json(needle_schema_path)

    assert_no_secret_keys(government_path, government)
    assert_no_secret_keys(fallback_path, fallback)

    validator = candidate_vector_validator(candidate_schema, common_schema)
    full_needle_validator = needle_validator(needle_schema, candidate_schema, common_schema)

    for needle_path, needle in (
        (government_path, government),
        (fallback_path, fallback),
    ):
        full_needle_validator.validate(needle)
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

    actions = {action["action_id"]: action for action in government.get("declared_actions", [])}
    assert "mock_turn_on_tv" in actions
    assert "mock_order_pizza" in actions
    assert actions["mock_turn_on_tv"]["real_execution_supported"] is False
    assert actions["mock_turn_on_tv"]["audit_required"] is True
    assert actions["mock_turn_on_tv"]["drs_writeback_required"] is True
    assert [step["kind"] for step in actions["mock_turn_on_tv"]["protocol_steps"]] == [
        "validate_input",
        "permission_check",
        "mock_execute",
        "audit_marker",
    ]
    assert all(step["mock_only"] is True for step in actions["mock_turn_on_tv"]["protocol_steps"])
    assert actions["mock_order_pizza"]["requires_confirmation"] is True
    assert actions["mock_order_pizza"]["risk_level"] == "purchase"
    assert [step["kind"] for step in actions["mock_order_pizza"]["protocol_steps"]] == [
        "validate_input",
        "permission_check",
        "mock_execute",
        "mock_receipt",
        "audit_marker",
    ]
