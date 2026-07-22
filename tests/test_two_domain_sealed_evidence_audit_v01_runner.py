from __future__ import annotations

from dataclasses import fields, replace
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest

from demo import run_two_domain_sealed_evidence_audit_v01 as runner


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_OUTPUT = REPOSITORY_ROOT / runner.CANONICAL_OUTPUT_REF


def _canonical_snapshot(path: Path) -> tuple[object, ...]:
    try:
        entry = os.lstat(path)
    except FileNotFoundError:
        return ("ABSENT",)
    if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
        raise AssertionError("unsafe canonical X1 baseline")
    content = path.read_bytes()
    runner.strict_json_bytes_v01(content)
    return (
        "PRESENT",
        hashlib.sha256(content).hexdigest(),
        len(content),
        stat.S_IMODE(entry.st_mode),
        content,
    )


CANONICAL_BASELINE = _canonical_snapshot(CANONICAL_OUTPUT)


@pytest.fixture(scope="module")
def sources():
    return runner.load_cross_domain_sources_v01(
        repository_root=REPOSITORY_ROOT,
        source_refs=dict(runner.SOURCE_REFS),
    )


@pytest.fixture(scope="module")
def result(sources):
    return runner.build_two_domain_cross_domain_evidence_index_v01(sources)


@pytest.fixture(scope="module")
def plain(result, sources):
    return runner.cross_domain_evidence_index_to_plain_dict_v01(result, sources)


def _rehash(value):
    return replace(value, index_id=runner._identity(value))


def _replace_snapshot(sources, name, content):
    changed = []
    for item in sources.snapshots:
        if item.logical_name == name:
            changed.append(
                replace(
                    item,
                    content=content,
                    sha256=hashlib.sha256(content).hexdigest(),
                    byte_count=len(content),
                )
            )
        else:
            changed.append(item)
    return replace(sources, snapshots=tuple(changed))


def test_public_api_surface():
    assert runner.CrossDomainEvidenceIndexV01
    assert runner.build_two_domain_cross_domain_evidence_index_v01
    assert runner.validate_two_domain_cross_domain_evidence_index_v01
    assert runner.cross_domain_evidence_index_to_plain_dict_v01
    assert runner.load_cross_domain_evidence_index_v01
    assert runner.load_cross_domain_sources_v01


def test_result_field_geometry():
    assert tuple(item.name for item in fields(runner.CrossDomainEvidenceIndexV01)) == (
        "index_id",
        "index_version",
        "programme_id",
        "gate_id",
        "execution_head",
        "airline",
        "supplier_water_filter",
        "claim_evidence_matrix",
        "differences",
        "unchanged_authority_laws",
        "required_non_claims",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "real_world_effects_count",
        "validation_errors",
        "final_status",
    )


def test_all_sources_are_explicit_and_unique(sources):
    assert len(runner.SOURCE_REFS) == 25
    assert len(sources.snapshots) == 25
    assert len(set(runner.SOURCE_REFS.values())) == 25
    assert tuple(item.logical_name for item in sources.snapshots) == tuple(runner.SOURCE_REFS)


def test_every_source_hash_is_frozen(sources):
    assert {item.logical_name: item.sha256 for item in sources.snapshots} == runner.EXPECTED_HASHES


def test_every_source_is_regular_and_not_aliased(sources):
    assert len({(item.device, item.inode) for item in sources.snapshots}) == 25
    for item in sources.snapshots:
        assert stat.S_ISREG(os.lstat(REPOSITORY_ROOT / item.repository_relative_path).st_mode)
        assert not (REPOSITORY_ROOT / item.repository_relative_path).is_symlink()


def test_source_continuity_passes(sources):
    runner.verify_source_continuity_v01(sources)


def test_build_and_validation_pass(result, sources):
    assert result.final_status == "PASS"
    assert result.validation_errors == ()
    assert runner.validate_two_domain_cross_domain_evidence_index_v01(result, sources) == ()


def test_index_identity_is_domain_separated(result):
    assert result.index_id == runner._identity(result)
    raw = hashlib.sha256(runner._canonical_bytes(runner._plain(replace(result, index_id="0" * 64)))).hexdigest()
    assert result.index_id != raw


def test_serialization_and_strict_loader_round_trip(result, plain, sources):
    content = runner.canonical_json_line_v01(plain)
    assert runner.load_cross_domain_evidence_index_v01(content, sources) == result
    assert content.endswith(b"\n") and not content.endswith(b"\n\n")


def test_deterministic_rebuild_bytes(result, sources):
    second = runner.build_two_domain_cross_domain_evidence_index_v01(sources)
    assert second == result
    assert runner.canonical_json_line_v01(runner._plain(second)) == runner.canonical_json_line_v01(runner._plain(result))


def test_fresh_process_rebuild_is_deterministic(result):
    code = (
        "from pathlib import Path; import demo.run_two_domain_sealed_evidence_audit_v01 as r;"
        "s=r.load_cross_domain_sources_v01(repository_root=Path.cwd(),source_refs=dict(r.SOURCE_REFS));"
        "x=r.build_two_domain_cross_domain_evidence_index_v01(s);print(x.index_id)"
    )
    env = {**os.environ, "PYTHONPATH": ".", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONBREAKPOINT": "0"}
    first = subprocess.run((sys.executable, "-c", code), cwd=REPOSITORY_ROOT, env=env, text=True, capture_output=True, check=True)
    second = subprocess.run((sys.executable, "-c", code), cwd=REPOSITORY_ROOT, env=env, text=True, capture_output=True, check=True)
    assert first.stdout.strip() == second.stdout.strip() == result.index_id
    assert first.stderr == second.stderr == ""


@pytest.mark.parametrize(
    ("domain", "name", "value"),
    (
        ("airline", "package_index_id", runner.AIRLINE_PACKAGE_INDEX_ID),
        ("airline", "manifest_id", runner.AIRLINE_MANIFEST_ID),
        ("airline", "package_content_hash", runner.AIRLINE_PACKAGE_CONTENT_HASH),
        ("airline", "anchor_publication_id", runner.AIRLINE_ANCHOR_ID),
        ("airline", "anchored_verification_id", runner.AIRLINE_VERIFICATION_ID),
        ("airline", "replay_id", runner.AIRLINE_REPLAY_ID),
        ("supplier_water_filter", "safe_evidence_index_id", runner.SUPPLIER_SAFE_EVIDENCE_INDEX_ID),
        ("supplier_water_filter", "safe_package_index_id", runner.SUPPLIER_PACKAGE_INDEX_ID),
        ("supplier_water_filter", "manifest_id", runner.SUPPLIER_MANIFEST_ID),
        ("supplier_water_filter", "package_content_hash", runner.SUPPLIER_PACKAGE_CONTENT_HASH),
        ("supplier_water_filter", "anchor_publication_id", runner.SUPPLIER_ANCHOR_ID),
        ("supplier_water_filter", "anchored_verification_id", runner.SUPPLIER_VERIFICATION_ID),
        ("supplier_water_filter", "replay_id", runner.SUPPLIER_REPLAY_ID),
        ("supplier_water_filter", "adapter_result_id", runner.SUPPLIER_ADAPTER_ID),
        ("supplier_water_filter", "scenario_index_id", runner.SUPPLIER_SCENARIO_INDEX_ID),
    ),
)
def test_frozen_identities(result, domain, name, value):
    record = getattr(result, domain)
    assert runner.IdentityBindingV01(name, value) in record.identities


def test_airline_geometry(result):
    facts = {item.fact_name: item.fact_value for item in result.airline.public_call_geometry + result.airline.root_corridor_receipt_geometry + result.airline.outcome_and_effect_boundaries}
    assert facts == {
        "live_llm_calls": "12",
        "local_validation_pass_results": "12",
        "provider_network_gemini": "12/12/12",
        "publication_and_replay_provider_network_gemini": "0/0/0",
        "independent_root_decisions": "3",
        "corridor_count": "1",
        "evidence_receipt_count": "3",
        "transaction_evidence_status": "PASS",
        "anchor_status": "EVIDENCE_ONLY",
        "anchored_verification_status": "ANCHORED_PASS",
        "replay_status": "PASS",
        "real_world_effects": "0",
    }


def test_supplier_geometry(result):
    facts = {item.fact_name: item.fact_value for item in result.supplier_water_filter.public_call_geometry + result.supplier_water_filter.root_corridor_receipt_geometry + result.supplier_water_filter.outcome_and_effect_boundaries}
    assert facts["live_llm_calls"] == "6"
    assert facts["accepted_local_semantic_validations"] == "6"
    assert facts["scenario_order"] == "S-N1,S-N2,S-C1,S-P1,S-P2,S-F1,S-F2,S-F3,S-M1"
    assert facts["business_outcome"] == "MIXED"
    assert facts["supplier_b_status"] == "BLOCKED"
    assert facts["shipment_status"] == "HELD"
    assert facts["receipt_status"] == "EVIDENCE_ONLY"
    assert facts["real_world_effects"] == "0"


def test_claim_matrix_is_complete(result, sources):
    assert tuple(item.claim_id for item in result.claim_evidence_matrix) == (
        "X1-A01", "X1-A02", "X1-A03", "X1-S01", "X1-S02", "X1-S03",
        "X1-C01", "X1-C02", "X1-C03", "X1-C04", "X1-C05", "X1-C06", "X1-C07",
    )
    refs = {item.repository_relative_path for item in sources.snapshots}
    assert all(item.validation_status == "PASS" and set(item.evidence_refs).issubset(refs) for item in result.claim_evidence_matrix)


def test_comparison_surface_and_nonclaims(result):
    assert len(result.differences) == 5
    assert "12 versus 6 live LLM actors" in result.differences
    assert "Root authority" in result.unchanged_authority_laws
    assert "receipts are evidence only" in result.unchanged_authority_laws
    assert "not production" in result.required_non_claims
    assert "not proof that the external world changed" in result.required_non_claims


@pytest.mark.parametrize("field", ("provider_call_count", "network_call_count", "gemini_call_count", "real_world_effects_count"))
def test_nonzero_x1_operation_count_rejected(result, sources, field):
    forged = _rehash(replace(result, **{field: 1}))
    assert runner.validate_two_domain_cross_domain_evidence_index_v01(forged, sources)


def test_rehashed_airline_identity_forgery_rejected(result, sources):
    changed = replace(result.airline, identities=result.supplier_water_filter.identities)
    forged = _rehash(replace(result, airline=changed))
    assert runner.validate_two_domain_cross_domain_evidence_index_v01(forged, sources)


def test_rehashed_supplier_mixed_outcome_forgery_rejected(result, sources):
    facts = tuple(replace(item, fact_value="PASS") if item.fact_name == "business_outcome" else item for item in result.supplier_water_filter.outcome_and_effect_boundaries)
    forged = _rehash(replace(result, supplier_water_filter=replace(result.supplier_water_filter, outcome_and_effect_boundaries=facts)))
    assert runner.validate_two_domain_cross_domain_evidence_index_v01(forged, sources)


def test_rehashed_root_authority_widening_rejected(result, sources):
    laws = tuple("provider authority" if item == "Root authority" else item for item in result.unchanged_authority_laws)
    forged = _rehash(replace(result, unchanged_authority_laws=laws))
    assert runner.validate_two_domain_cross_domain_evidence_index_v01(forged, sources)


def test_rehashed_claim_evidence_removal_rejected(result, sources):
    first = replace(result.claim_evidence_matrix[0], evidence_refs=())
    forged = _rehash(replace(result, claim_evidence_matrix=(first,) + result.claim_evidence_matrix[1:]))
    assert runner.validate_two_domain_cross_domain_evidence_index_v01(forged, sources)


@pytest.mark.parametrize("value", ("../escape", "/absolute", "a/../../b", "a\\b", "", "./a"))
def test_repository_relative_path_rejections(value):
    assert runner._valid_ref(value) is False


def test_duplicate_source_path_rejected():
    refs = dict(runner.SOURCE_REFS)
    refs["supplier_human_story"] = refs["airline_human_story"]
    with pytest.raises(ValueError, match="cross_domain_source_path_invalid|cross_domain_source_alias_invalid"):
        runner.load_cross_domain_sources_v01(repository_root=REPOSITORY_ROOT, source_refs=refs)


def test_missing_source_key_rejected():
    refs = dict(runner.SOURCE_REFS)
    refs.pop("supplier_human_story")
    with pytest.raises(ValueError, match="cross_domain_source_set_invalid"):
        runner.load_cross_domain_sources_v01(repository_root=REPOSITORY_ROOT, source_refs=refs)


def test_changed_human_story_rejected(sources):
    content = sources.named("supplier_human_story").content.replace(b"business outcome remained `MIXED`", b"business outcome remained `PASS`")
    with pytest.raises(ValueError):
        runner.build_two_domain_cross_domain_evidence_index_v01(_replace_snapshot(sources, "supplier_human_story", content))


def test_changed_anchor_binding_rejected(sources):
    plain = runner.strict_json_bytes_v01(sources.named("airline_anchor").content)
    plain["package_content_hash"] = "0" * 64
    changed = runner.canonical_json_line_v01(plain)
    with pytest.raises(ValueError):
        runner.build_two_domain_cross_domain_evidence_index_v01(_replace_snapshot(sources, "airline_anchor", changed))


def test_changed_supplier_s2_rejected(sources):
    plain = runner.strict_json_bytes_v01(sources.named("supplier_s2_evidence").content)
    plain["supplier_b_status"] = "PASS"
    changed = runner.canonical_json_line_v01(plain)
    with pytest.raises(ValueError):
        runner.build_two_domain_cross_domain_evidence_index_v01(_replace_snapshot(sources, "supplier_s2_evidence", changed))


@pytest.mark.parametrize(
    "content",
    (
        b'{"a":1,"a":2}\n',
        b'{"x":NaN}\n',
        b'\xef\xbb\xbf{}\n',
        b'{}\r\n',
        b'{}\n\n',
        b'{"b":1,"a":2}\n',
        b'{"x":"\\u0000"}\n',
    ),
)
def test_unsafe_json_rejected(content):
    with pytest.raises(ValueError):
        runner.strict_json_bytes_v01(content)


def test_source_continuity_detects_changed_snapshot(monkeypatch, sources):
    original = runner._read_ref
    calls = {"count": 0}

    def changed(root_fd, logical_name, ref):
        item = original(root_fd, logical_name, ref)
        calls["count"] += 1
        if logical_name == "airline_safe_report":
            return replace(item, inode=item.inode + 1)
        return item

    monkeypatch.setattr(runner, "_read_ref", changed)
    with pytest.raises(ValueError, match="cross_domain_source_changed"):
        runner.verify_source_continuity_v01(sources)
    assert calls["count"] == 25


def test_output_write_and_reread(tmp_path):
    output = tmp_path / "x1.json"
    content = b'{"final_status":"PASS"}\n'
    runner.write_cross_domain_evidence_index_v01(output, content)
    assert output.read_bytes() == content
    assert stat.S_IMODE(output.stat().st_mode) == 0o400


def test_existing_output_collision_is_fail_closed(tmp_path):
    output = tmp_path / "x1.json"
    output.write_bytes(b"foreign\n")
    before = output.read_bytes()
    with pytest.raises(ValueError, match="cross_domain_output_write_failed"):
        runner.write_cross_domain_evidence_index_v01(output, b"{}\n")
    assert output.read_bytes() == before


def test_output_symlink_collision_is_preserved(tmp_path):
    target = tmp_path / "target"
    target.write_bytes(b"foreign\n")
    output = tmp_path / "x1.json"
    output.symlink_to(target)
    with pytest.raises(ValueError):
        runner.write_cross_domain_evidence_index_v01(output, b"{}\n")
    assert output.is_symlink() and target.read_bytes() == b"foreign\n"


def test_write_failure_cleans_only_owned_output(monkeypatch, tmp_path):
    output = tmp_path / "x1.json"
    monkeypatch.setattr(runner, "_write_all", lambda descriptor, content: (_ for _ in ()).throw(OSError()))
    with pytest.raises(ValueError, match="cross_domain_output_write_failed"):
        runner.write_cross_domain_evidence_index_v01(output, b"{}\n")
    assert not output.exists() and not output.is_symlink()


def test_duplicate_cli_option_fails_closed(capsys):
    assert runner.main(["--repository-root", str(REPOSITORY_ROOT), "--repository-root", str(REPOSITORY_ROOT)]) == 2
    assert json.loads(capsys.readouterr().out) == {"final_status": "FAIL_CLOSED", "reason": "cross_domain_audit_failed"}


def test_unknown_cli_option_fails_closed(capsys):
    assert runner.main(["--unknown"]) == 2
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"final_status": "FAIL_CLOSED", "reason": "cross_domain_audit_failed"}
    assert captured.err == ""


def test_cli_success_uses_only_explicit_output(monkeypatch, tmp_path, result, sources, capsys):
    parent = tmp_path / Path(runner.CANONICAL_OUTPUT_REF).parent
    parent.mkdir(parents=True)
    arguments = ["--repository-root", str(tmp_path)]
    for name, ref in runner.SOURCE_REFS.items():
        arguments.extend(("--" + name.replace("_", "-"), ref))
    arguments.extend(("--output", runner.CANONICAL_OUTPUT_REF))
    fake_sources = replace(sources, repository_root=tmp_path)
    monkeypatch.setattr(runner, "load_cross_domain_sources_v01", lambda **kwargs: fake_sources)
    monkeypatch.setattr(runner, "build_two_domain_cross_domain_evidence_index_v01", lambda value: result)
    monkeypatch.setattr(runner, "verify_source_continuity_v01", lambda value: None)
    monkeypatch.setattr(runner, "load_cross_domain_evidence_index_v01", lambda content, value: result)
    monkeypatch.setattr(runner, "cross_domain_evidence_index_to_plain_dict_v01", lambda value, loaded: runner._plain(value))
    assert runner.main(arguments) == 0
    output = tmp_path / runner.CANONICAL_OUTPUT_REF
    assert output.exists() and stat.S_IMODE(output.stat().st_mode) == 0o400
    summary = json.loads(capsys.readouterr().out)
    assert summary == {"final_status": "PASS", "index_id": result.index_id, "provider_network_gemini_effects": "0/0/0/0"}


def test_no_forbidden_operation_imports_or_calls():
    text = (REPOSITORY_ROOT / "demo/run_two_domain_sealed_evidence_audit_v01.py").read_text(encoding="utf-8")
    forbidden = (
        "google.generativeai",
        "google.genai",
        "requests",
        "urllib.request",
        "socket",
        "run_sealed_evidence_package_v01(",
        "run_sealed_evidence_anchor_v01(",
        "run_sealed_evidence_replay_v01(",
        "collect_two_domain_supplier_water_filter_program_v01(",
        "run_two_domain_airline_all_real_program_v01",
    )
    assert not any(item in text for item in forbidden)


def test_public_result_contains_no_private_material(plain):
    content = runner.canonical_json_line_v01(plain).decode("utf-8")
    lowered = content.casefold()
    forbidden = ("/users/", "prompt.txt", "raw_response.txt", "api_key", "traceback", "object at 0x")
    assert not any(item in lowered for item in forbidden)


def test_canonical_output_lifecycle_is_unchanged():
    assert _canonical_snapshot(CANONICAL_OUTPUT) == CANONICAL_BASELINE
