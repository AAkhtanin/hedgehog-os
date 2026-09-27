"""Package integrity and finite evidence-basis negatives; no native execution."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from demo import verify_gate6_reference_v01 as reader


@pytest.fixture
def protocol():
    root = Path(__file__).resolve().parents[1]
    package = root / "docs/gate6_reference_v01"
    index = reader.read(package / "evidence_index.json")["resources"]
    original = reader.read(root / index["r/original_source_closure.json"]["path"])
    reviewed = reader.read(root / index["r/source_closure.json"]["path"])
    return (reader.read(package / "machine_manifest.json"),
            reader.read(package / "acceptance_matrix.json"), original, reviewed)


def test_valid_current_finite_protocol(protocol):
    reader.validate_protocol(*protocol)
    assert len(protocol[1]["rows"]) == 73
    assert len(protocol[0]["profiles"]) == 11


@pytest.mark.parametrize("target,operation", [(0,"missing"),(0,"duplicate"),(1,"missing"),(1,"duplicate")])
def test_missing_or_duplicate_required_inventory(protocol, target, operation):
    values = copy.deepcopy(protocol)
    rows = values[target]["profiles" if target == 0 else "rows"]
    if operation == "missing":
        rows.pop()
    else:
        rows.append(copy.deepcopy(rows[0]))
    with pytest.raises(ValueError, match="inventory"):
        reader.validate_protocol(*values)


def test_wrong_executed_source_basis(protocol):
    values = copy.deepcopy(protocol)
    values[2]["hedgehog/kernel/abi_v01.py"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="executed_source_basis"):
        reader.validate_protocol(*values)


@pytest.mark.parametrize("profile", ["G35", "LIVING_G36"])
def test_incompatible_original_successor_substitution(protocol, profile):
    values = copy.deepcopy(protocol)
    row = next(x for x in values[0]["profiles"] if x["profile"] == profile)
    row["execution_basis"] = reader.ORIGINAL if profile == "G35" else reader.REVIEWED
    with pytest.raises(ValueError, match="profile_source_substitution"):
        reader.validate_protocol(*values)


@pytest.mark.parametrize("key,value,reason", [
    ("protocol", "ELEVEN_FRESH_ONE_FREEZE", "not_same_freeze_eleven"),
    ("historical_G6A4", "PASS", "historical_failure_promoted"),
    ("owner_source_admission", "ACCEPTED", "unearned_admission"),
])
def test_no_retroactive_or_self_awarded_acceptance(protocol, key, value, reason):
    values = copy.deepcopy(protocol)
    values[0][key] = value
    with pytest.raises(ValueError, match=reason):
        reader.validate_protocol(*values)


def test_actual_primary_blob_missing_tampered_and_valid(tmp_path):
    root = Path(__file__).resolve().parents[1]
    index = reader.read(root/"docs/gate6_reference_v01/evidence_index.json")["resources"]
    pin = index["r/fresh/G35/G35/native/TESTFLIX.json"]
    body = (root/pin["path"]).read_bytes()
    with pytest.raises(FileNotFoundError):
        reader.checked_file(tmp_path, "primary.json", pin, git_mode="100644")
    (tmp_path/"primary.json").write_bytes(body)
    assert reader.checked_file(tmp_path, "primary.json", pin, git_mode="100644") == body
    (tmp_path/"primary.json").write_bytes(body.replace(b"TESTFLIX", b"TESTFLIY", 1))
    with pytest.raises(ValueError, match="file_pin"):
        reader.checked_file(tmp_path, "primary.json", pin)


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a//b", "a/./b", ""])
def test_relative_resource_boundary(name):
    with pytest.raises(ValueError):
        reader.relative(name)


def test_data_only_inspection_full_package():
    result = reader.inspect()
    assert result["mode"] == "DATA_ONLY"
    assert result["runtime_imports"] is False
    assert result["trust"] == "SELF_CONSISTENCY_ONLY"
    assert result["admission"] == "PENDING"
    assert result["finite_rows"] == 4 and not result["remaining_technical"]


@pytest.mark.parametrize("change", ("missing_preimage", "current_fallback", "new_test_in_original", "runtime_delta", "unbound_row"))
def test_finite_successor_source_and_row_boundaries(protocol, change):
    root = Path(__file__).resolve().parents[1]
    folder = root/reader.PACKAGE
    index = reader.read(folder/"evidence_index.json")
    current = reader.read(folder/"current_source_closure.json")
    if change == "missing_preimage":
        del index["historical_source_view"][reader.COMPAT]
    elif change == "current_fallback":
        for key in ("historical_source_view", "reviewed_source_view"):
            index[key][reader.COMPAT]["path"] = reader.COMPAT
    elif change == "new_test_in_original":
        index["historical_source_view"][reader.TEST] = index["reviewed_source_view"][reader.TEST]
    elif change == "runtime_delta":
        current["hedgehog/kernel/abi_v01.py"]["sha256"] = "0"*64
    else:
        row = next(r for r in protocol[1]["rows"] if r["id"] == "N4-05")
        row["binding"] = [b for b in row["binding"] if b.get("consumer") != "RETAINED_OBLIGATIONS"]
        with pytest.raises(ValueError, match="finite_row_binding"):
            reader.validate_protocol(*protocol)
        return
    with pytest.raises(ValueError):
        reader.source_views(index, protocol[2], protocol[3], current)


def test_model_replay_receipt_metadata_is_not_canonical_result():
    root = Path(__file__).resolve().parents[1]
    index = reader.read(root/"docs/gate6_reference_v01/evidence_index.json")["resources"]
    prior = reader.read(root/index["r/retained/MODEL/LIVE_replay.json"]["path"])
    current = copy.deepcopy(prior)
    current["observation"]["pid"] += 1
    current["observation"]["entered"] += 10
    for row in current["observation"]["identities"].values():
        row["file"] = "/independent/checkout/" + Path(row["file"]).name
    assert reader.model_replay_result(current, prior)["result"] == prior["result"]
    current["observation"]["counts"]["effect"] = 1
    with pytest.raises(ValueError, match="model_replay_operations"):
        reader.model_replay_result(current, prior)
    current = copy.deepcopy(prior)
    current["result"]["forged"] = True
    with pytest.raises(ValueError, match="model_replay_parity"):
        reader.model_replay_result(current, prior)


def test_finite_worker_owns_exactly_one_observation_scope(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path/"finite";output.mkdir()
    result = subprocess.run([sys.executable, "-B", str(root/"demo/verify_gate6_reference_v01.py"),
        "--worker", "RETAINED_OBLIGATIONS", "--source-view", str(root),
        "--resources", str(tmp_path), "--output", str(output)], cwd=root,
        env=reader.environment(root), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert set(reader.read(output/"result.json")) == {"avf", "reuse", "policy", "privacy"}
    assert reader.read(output/"pure.observation.json")["counts"] == {"sentinel": 1}
    assert reader.read(output/"audit.json")["counts"] == {"network": 0, "subprocess": 0}
