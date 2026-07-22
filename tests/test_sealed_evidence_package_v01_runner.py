import ast
import copy
from dataclasses import FrozenInstanceError, fields, replace
import json
import os
from pathlib import Path
import shutil

import pytest

from demo import run_sealed_evidence_package_v01 as runner
from hedgehog.evidence.sealed_evidence_profile_v01 import (
    build_domain_evidence_projection_v01,
    validate_domain_evidence_projection_v01,
)
from hedgehog.evidence.sealed_package_v01 import (
    MANIFEST_FILENAME,
    STATUS_SELF_CONSISTENT_UNANCHORED,
    validate_sealed_package_manifest_v01,
)


def _context(domain="airline", execution_head="7bc7b8f"):
    return runner.build_disposable_fixture_context_v01(
        domain=domain,
        execution_head=execution_head,
    )


def _run(tmp_path, domain="airline", name="package"):
    context = _context(domain)
    result = runner.run_sealed_evidence_package_v01(
        domain=domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=tmp_path / name,
        fixture_disposable=True,
    )
    return context, result, tmp_path / name


def _tree_bytes(root):
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.mark.parametrize("domain", runner.FIXTURE_DOMAINS)
def test_positive_disposable_fixture_domains(tmp_path, domain):
    context, result, package = _run(tmp_path, domain)
    assert validate_domain_evidence_projection_v01(context.domain_projection) == ()
    assert result.manifest.package_status == STATUS_SELF_CONSISTENT_UNANCHORED
    assert validate_sealed_package_manifest_v01(
        result.manifest,
        domain_projection=context.domain_projection,
        safe_file_contents=result.safe_file_contents,
    ) == ()
    assert result.manifest.domain_id == domain
    assert result.manifest.file_count == 1
    assert result.manifest.artifact_count == 1
    assert set(_tree_bytes(package)) == {
        result.manifest.safe_file_records[0].logical_path,
        MANIFEST_FILENAME,
    }


def test_fixture_domains_have_distinct_identities():
    airline = _context("airline")
    supplier = _context("supplier_water_filter")
    assert airline.domain_projection.projection_id != supplier.domain_projection.projection_id
    assert airline.kernel_manifest_hash != supplier.kernel_manifest_hash
    assert airline.safe_members[0].content_bytes != supplier.safe_members[0].content_bytes


def test_exact_zero_package_counters_and_safe_summary(tmp_path):
    _, result, _ = _run(tmp_path)
    manifest = result.manifest
    assert (
        manifest.packaging_provider_call_count,
        manifest.packaging_network_call_count,
        manifest.packaging_gemini_call_count,
        manifest.created_authority_count,
        manifest.created_permission_count,
        manifest.real_world_effects_count,
    ) == (0, 0, 0, 0, 0, 0)
    assert result.summary["package_status"] == STATUS_SELF_CONSISTENT_UNANCHORED
    assert not any("path" in key for key in result.summary)


@pytest.mark.parametrize("domain", runner.FIXTURE_DOMAINS)
def test_equivalent_runs_are_byte_identical_across_roots(tmp_path, domain):
    _, first, first_path = _run(tmp_path, domain, "first")
    _, second, second_path = _run(tmp_path, domain, "second")
    assert first.manifest == second.manifest
    assert _tree_bytes(first_path) == _tree_bytes(second_path)


def test_manifest_is_written_last(tmp_path, monkeypatch):
    writes = []
    original = runner._write_package_file

    def recording(owner, logical_path, content):
        writes.append(logical_path)
        return original(owner, logical_path, content)

    monkeypatch.setattr(runner, "_write_package_file", recording)
    _run(tmp_path)
    assert writes[-1] == MANIFEST_FILENAME
    assert writes.count(MANIFEST_FILENAME) == 1


def test_existing_output_is_refused_without_overwrite(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    marker = output / "marker"
    marker.write_bytes(b"unchanged")
    context = _context()
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert marker.read_bytes() == b"unchanged"


def test_output_target_symlink_is_refused_without_touching_target(tmp_path):
    target = tmp_path / "owned-target"
    target.mkdir()
    marker = target / "marker"
    marker.write_bytes(b"unchanged")
    output = tmp_path / "package-link"
    output.symlink_to(target, target_is_directory=True)
    context = _context()
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert marker.read_bytes() == b"unchanged"
    assert output.is_symlink()


def test_source_inputs_are_immutable(tmp_path):
    context = _context()
    before_projection = context.domain_projection
    before_members = copy.deepcopy(context.safe_members)
    runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    assert context.domain_projection == before_projection
    assert context.safe_members == before_members


@pytest.mark.parametrize("attack", ("missing", "reordered", "duplicate", "casefold", "nfc"))
def test_member_inventory_attacks_are_rejected(tmp_path, attack):
    context = _context()
    original = context.safe_members[0]
    extra = replace(original, logical_path="evidence/02-extra.json")
    if attack == "missing":
        members = ()
    elif attack == "reordered":
        members = (extra, original)
    elif attack == "duplicate":
        members = (original, original)
    elif attack == "casefold":
        members = (original, replace(original, logical_path=original.logical_path.upper()))
    else:
        members = (original, replace(original, logical_path="evidence/02-e\u0301.json"))
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=members,
            output_directory=tmp_path / attack,
            fixture_disposable=True,
        )


@pytest.mark.parametrize(
    "logical_path",
    (
        "/absolute.json",
        "../traversal.json",
        "evidence/../traversal.json",
        "C:/private.json",
        "C:\\private.json",
        "\\\\server\\share\\x.json",
        "//server/share/x.json",
        "evidence//empty.json",
        "evidence/./dot.json",
        MANIFEST_FILENAME,
        MANIFEST_FILENAME.upper(),
    ),
)
def test_logical_path_and_manifest_self_reference_attacks(tmp_path, logical_path):
    context = _context()
    member = replace(context.safe_members[0], logical_path=logical_path)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=(member,),
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )


@pytest.mark.parametrize(
    "content",
    (
        b'{"raw_prompt":"private"}\n',
        b'{"value":"GEMINI_API_KEY=private"}\n',
        b'{"value":"/Users/private/file"}\n',
        b'{"value":"Traceback:"}\n',
        b'{"value":"<Private object at 0x1234abcd>"}\n',
        b'{"value":"0x1234abcd"}\n',
        b'\xef\xbb\xbf{"value":1}\n',
        b'{"value":1}\r\n',
        b'{"value":"x\x00y"}\n',
        b'{"a":1,"a":2}\n',
        b'{"value":NaN}\n',
        b'{"value":1}\n\n',
        b'\xff\n',
    ),
)
def test_raw_private_secret_and_invalid_json_bytes_are_rejected(tmp_path, content):
    context = _context()
    member = replace(context.safe_members[0], content_bytes=content)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=(member,),
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )


@pytest.mark.parametrize("kernel_hash", ("bad", "f" * 64))
def test_invalid_or_ungrounded_kernel_hash_is_rejected(tmp_path, kernel_hash):
    context = _context()
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=kernel_hash,
            safe_members=context.safe_members,
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )


@pytest.mark.parametrize("attack", ("content", "extra", "missing", "symlink", "directory"))
def test_completed_package_snapshot_attacks_are_rejected(tmp_path, attack):
    context, result, package = _run(tmp_path)
    record = result.manifest.safe_file_records[0]
    member = package / record.logical_path
    if attack == "content":
        member.write_bytes(b'{"changed":true}\n')
    elif attack == "extra":
        (package / "extra.json").write_bytes(b"{}\n")
    elif attack == "missing":
        member.unlink()
    elif attack == "symlink":
        member.unlink()
        member.symlink_to(package / MANIFEST_FILENAME)
    else:
        member.unlink()
        member.mkdir()
    with pytest.raises(ValueError):
        runner._validate_package_directory(
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=result.manifest,
            ordered_safe_contents=result.safe_file_contents,
        )


def test_manifest_and_member_json_are_canonical_with_one_lf(tmp_path):
    _, result, package = _run(tmp_path)
    for path, content in _tree_bytes(package).items():
        assert content.endswith(b"\n")
        assert not content.endswith(b"\n\n")
        assert b"\r" not in content
        parsed = json.loads(content)
        assert content == runner.canonical_json_bytes_v01(parsed) + b"\n"
    assert MANIFEST_FILENAME not in {
        item.logical_path for item in result.manifest.safe_file_records
    }


def test_directory_and_files_are_private_where_supported(tmp_path):
    _, result, package = _run(tmp_path)
    assert package.stat().st_mode & 0o077 == 0
    for record in result.manifest.safe_file_records:
        assert (package / record.logical_path).stat().st_mode & 0o077 == 0
    assert (package / MANIFEST_FILENAME).stat().st_mode & 0o077 == 0


def test_dataclasses_are_frozen_and_public_api_is_present(tmp_path):
    context, result, _ = _run(tmp_path)
    with pytest.raises(FrozenInstanceError):
        context.domain = "changed"
    with pytest.raises(FrozenInstanceError):
        result.domain = "changed"
    assert tuple(field.name for field in fields(runner.SafeMemberInputV01)) == (
        "logical_path",
        "media_type",
        "content_bytes",
        "evidence_class",
        "source_record_ids",
        "terminal_newline_required",
    )
    assert callable(runner.run_sealed_evidence_package_v01)


def test_result_summary_is_deeply_immutable(tmp_path):
    _, result, _ = _run(tmp_path)
    with pytest.raises(TypeError):
        result.summary["package_status"] = "changed"


def test_disposable_fixture_label_cannot_be_downgraded(tmp_path):
    context = _context()
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=tmp_path / "package",
            fixture_disposable=False,
        )


@pytest.mark.parametrize(
    "metadata",
    (
        {
            "contains_raw_prompt": False,
            "contains_raw_provider_response": False,
            "secret_scan_passed": True,
            "style": "airline",
        },
        {
            "raw_prompt_included": False,
            "raw_provider_response_included": False,
            "secret_scan_passed": True,
            "style": "supplier_water_filter",
        },
    ),
)
def test_safe_negative_metadata_is_accepted(tmp_path, metadata):
    context = _context()
    content = runner.canonical_json_bytes_v01(
        {"safety": metadata, "source_record_id": context.domain_projection.source_records[0].source_record_id}
    ) + b"\n"
    member = replace(context.safe_members[0], content_bytes=content)
    result = runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=(member,),
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    assert result.manifest.package_status == STATUS_SELF_CONSISTENT_UNANCHORED


def test_airline_authorization_references_and_token_metrics_are_safe(tmp_path):
    context = _context()
    content = runner.canonical_json_bytes_v01(
        {
            "authorization_count": 1,
            "authorization_decision_id": "decision:safe",
            "authorization_ref_id": "authorization:safe",
            "authorization_status": "MOCK_ONLY",
            "controlled_token_overlap": False,
            "required_payment_authorization_ref_id": "payment:safe",
            "source_payment_authorization_ref_id": "source:safe",
            "token_count": 12,
            "token_overlap_score": 0.0,
            "validation_note": "Precomposed multilingual résumé 安全",
        }
    ) + b"\n"
    member = replace(context.safe_members[0], content_bytes=content)
    result = runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=(member,),
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    assert result.safe_file_contents == (content,)


@pytest.mark.parametrize(
    ("domain", "logical_path", "payload"),
    (
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {
                "auxiliary_artifact_refs": [
                    "auxiliary_artifact_ref:provider_response:opaque"
                ]
            },
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {"output_field": "/airline_artifact_hash"},
        ),
        (
            "airline",
            "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
            {"output_field": "/airline_artifact_hash"},
        ),
        (
            "supplier_water_filter",
            "evidence/01-source.json",
            {"output_field": "/source_card_hash"},
        ),
    ),
)
def test_closed_contextual_safe_references_pass_initial_and_reread_scans(
    tmp_path,
    monkeypatch,
    domain,
    logical_path,
    payload,
):
    context = _context(domain)
    content = runner.canonical_json_bytes_v01(payload) + b"\n"
    member = replace(
        context.safe_members[0],
        logical_path=logical_path,
        content_bytes=content,
    )
    calls = []
    original = runner._scan_safe_content

    def recording(value, **kwargs):
        calls.append((kwargs["domain"], kwargs["logical_path"]))
        return original(value, **kwargs)

    monkeypatch.setattr(runner, "_scan_safe_content", recording)
    result = runner.run_sealed_evidence_package_v01(
        domain=domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=(member,),
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    assert result.safe_file_contents == (content,)
    assert calls == [(domain, logical_path)] * 3


@pytest.mark.parametrize(
    ("domain", "logical_path", "payload"),
    (
        (
            "supplier_water_filter",
            "evidence/03-airline-a2-typed-context-v01.json",
            {"output_field": "/airline_artifact_hash"},
        ),
        (
            "airline",
            "evidence/02-airline-source-lineage-v01.json",
            {"output_field": "/airline_artifact_hash"},
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {"other_field": "/airline_artifact_hash"},
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {
                "auxiliary_artifact_refs":
                    "auxiliary_artifact_ref:provider_response:opaque"
            },
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {
                "auxiliary_artifact_refs": [
                    "AUXILIARY_ARTIFACT_REF:PROVIDER_RESPONSE:OPAQUE"
                ]
            },
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {
                "auxiliary_artifact_refs": [
                    "prefix:auxiliary_artifact_ref:provider_response:opaque"
                ]
            },
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {
                "auxiliary_observation_refs": [
                    "auxiliary_artifact_ref:provider_response:opaque:suffix"
                ]
            },
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {
                "auxiliary_observation_refs": [
                    "auxiliary_artifact_ref:provider_respons\uff45:opaque"
                ]
            },
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {"output_field": "/source_card_hash"},
        ),
        (
            "supplier_water_filter",
            "evidence/01-source.json",
            {"output_field": "/airline_artifact_hash"},
        ),
        (
            "airline",
            "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
            {"output_field": "/safe_projection_hash"},
        ),
        (
            "airline",
            "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
            {"output_field": "/etc/passwd"},
        ),
        (
            "airline",
            "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
            {"output_field": "/Users/private/file"},
        ),
        (
            "airline",
            "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
            {"output_field": "/airline/artifact/hash"},
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {"auxiliary_artifact_refs": ["provider_response:arbitrary"]},
        ),
        (
            "airline",
            "evidence/03-airline-a2-typed-context-v01.json",
            {"value": "raw provider response body"},
        ),
    ),
)
def test_contextual_safe_reference_near_misses_remain_rejected(
    tmp_path,
    domain,
    logical_path,
    payload,
):
    context = _context(domain)
    member = replace(
        context.safe_members[0],
        logical_path=logical_path,
        content_bytes=runner.canonical_json_bytes_v01(payload) + b"\n",
    )
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=(member,),
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )
    assert not (tmp_path / "package").exists()


@pytest.mark.parametrize(
    "key,value",
    (
        ("contains_raw_prompt", True),
        ("contains_raw_provider_response", 0),
        ("raw_prompt_included", "false"),
        ("raw_provider_response_included", True),
        ("secret_scan_passed", False),
        ("raw_prompt", False),
        ("prompt_text", "private"),
        ("raw_response", "private"),
        ("provider_response_backup", "private"),
        ("api_key", "private"),
        ("private_key", "private"),
        ("credential_material", "private"),
    ),
)
def test_unsafe_or_inverted_safety_metadata_is_rejected(tmp_path, key, value):
    context = _context()
    content = runner.canonical_json_bytes_v01({key: value}) + b"\n"
    member = replace(context.safe_members[0], content_bytes=content)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=(member,),
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )
    assert not (tmp_path / "package").exists()


@pytest.mark.parametrize(
    "payload",
    (
        {"password": "private"},
        {"access_token": "private"},
        {"refresh_token": "private"},
        {"bearer_token": "private"},
        {"auth_token": "private"},
        {"client_secret": "private"},
        {"secret_value": "private"},
        {"authorization": "Bearer private"},
        {"authorization_header": "Bearer private"},
        {"credential": "private"},
        {"note": "raw_prompt: private"},
        {"p\u0430ssword": "private"},
        {"raw_pr\u043empt": "private"},
        {"ｒａｗ＿ｐｒｏｍｐｔ": "private"},
        {"ｒａｗ＿ｐｒｏｍｐｔ＿ｉｎｃｌｕｄｅｄ": False},
        {"ｐｒｉｖａｔｅ＿ｋｅｙ": "private"},
    ),
)
def test_security_token_and_value_bypasses_are_rejected(tmp_path, payload):
    context = _context()
    content = runner.canonical_json_bytes_v01(payload) + b"\n"
    member = replace(context.safe_members[0], content_bytes=content)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=(member,),
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )


@pytest.mark.parametrize(
    "content",
    (
        b"api_key: private\n",
        b"credential=private\n",
        b"-----BEGIN PRIVATE KEY-----\nprivate\n",
        b"\xff\xfe\n",
    ),
)
def test_plaintext_secrets_and_invalid_utf8_are_rejected(tmp_path, content):
    context = _context()
    member = replace(
        context.safe_members[0],
        media_type="text/plain",
        content_bytes=content,
        terminal_newline_required=True,
    )
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=(member,),
            output_directory=tmp_path / "package",
            fixture_disposable=True,
        )


@pytest.mark.parametrize("media_type", ("text/plain", "text/markdown"))
def test_safe_multiline_text_is_consistently_packaged(tmp_path, media_type):
    context = _context()
    content = "Résumé 安全\nsecond safe line\n".encode()
    member = replace(
        context.safe_members[0],
        media_type=media_type,
        content_bytes=content,
        terminal_newline_required=True,
    )
    result = runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=(member,),
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    assert result.safe_file_contents == (content,)


def test_fixture_classification_requires_complete_projection_equality(tmp_path):
    context = _context()
    exact = context.domain_projection
    near = build_domain_evidence_projection_v01(
        programme_identity=exact.programme_identity,
        domain_execution_identity=exact.domain_execution_identity,
        attempt_identity=exact.attempt_identity,
        source_records=exact.source_records,
        artifact_records=exact.artifact_records,
        kernel_artifact_refs=exact.kernel_artifact_refs,
        causal_consumption_refs=exact.causal_consumption_refs,
        evidence_refs=exact.evidence_refs,
        limitation_refs=(*exact.limitation_refs, "fixture:near-but-distinct"),
    )
    assert validate_domain_evidence_projection_v01(near) == ()
    assert runner._projection_is_disposable_fixture(exact) is True
    assert runner._projection_is_disposable_fixture(near) is False
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=near,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=tmp_path / "wrongly-labelled",
            fixture_disposable=True,
        )
    result = runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=near,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=tmp_path / "near-fixture",
        fixture_disposable=False,
    )
    assert result.fixture_disposable is False


@pytest.mark.parametrize("target", ("member", "manifest", "root"))
def test_same_bytes_different_inode_replacement_fails_closed(tmp_path, monkeypatch, target):
    context = _context()
    output = tmp_path / "package"
    original = runner._validate_package_directory
    replaced = False

    def replacing(**kwargs):
        nonlocal replaced
        if not replaced:
            replaced = True
            if target == "root":
                saved = tmp_path / "owned-root"
                output.rename(saved)
                shutil.copytree(saved, output)
            else:
                logical = (
                    MANIFEST_FILENAME
                    if target == "manifest"
                    else context.safe_members[0].logical_path
                )
                path = output.joinpath(*logical.split("/"))
                replacement = path.with_name(path.name + ".replacement")
                replacement.write_bytes(path.read_bytes())
                os.replace(replacement, path)
        return original(**kwargs)

    monkeypatch.setattr(runner, "_validate_package_directory", replacing)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_package_root_one_shot_fstat_failure_uses_raw_descriptor_fallback(
    tmp_path,
    monkeypatch,
):
    context = _context()
    output = tmp_path / "package"
    original_open = runner._os.open
    original_fstat = runner._os.fstat
    target_fd = None
    failed = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & getattr(runner._os, "O_DIRECTORY", 0):
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        nonlocal failed
        if descriptor == target_fd and not failed:
            failed = True
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "fstat", failing_fstat)
    result = runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=output,
        fixture_disposable=True,
    )
    assert failed is True
    assert result.manifest.package_status == STATUS_SELF_CONSISTENT_UNANCHORED


def test_package_root_replacement_during_fstat_fallback_is_never_adopted(
    tmp_path,
    monkeypatch,
):
    context = _context()
    output = tmp_path / "package"
    original_open = runner._os.open
    original_fstat = runner._os.fstat
    target_fd = None
    replaced = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & getattr(runner._os, "O_DIRECTORY", 0):
            target_fd = descriptor
        return descriptor

    def replacing_fstat(descriptor):
        nonlocal replaced
        if descriptor == target_fd and not replaced:
            replaced = True
            output.rename(tmp_path / "original-package")
            output.mkdir()
            (output / "replacement-marker").write_text("replacement", encoding="utf-8")
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "fstat", replacing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert (output / "replacement-marker").read_text(encoding="utf-8") == "replacement"


def test_post_open_member_fstat_failure_recovers_exact_ownership(tmp_path, monkeypatch):
    context = _context()
    original_open = runner._os.open
    original_fstat = runner._os.fstat
    member_name = Path(context.safe_members[0].logical_path).name
    target_fd = None
    failed = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == member_name and flags & runner._os.O_ACCMODE != runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        nonlocal failed
        if descriptor == target_fd and not failed:
            failed = True
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "fstat", failing_fstat)
    result = runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    assert failed is True
    assert result.manifest.package_status == STATUS_SELF_CONSISTENT_UNANCHORED


def test_member_descriptor_identity_persistent_failure_is_cleanup_failed(
    tmp_path,
    monkeypatch,
):
    context = _context()
    output = tmp_path / "package"
    original_open = runner._os.open
    original_fstat = runner._os.fstat
    member_name = Path(context.safe_members[0].logical_path).name
    target_fd = None

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == member_name and flags & runner._os.O_ACCMODE != runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        if descriptor == target_fd:
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "fstat", failing_fstat)
    monkeypatch.setattr(runner, "_RAW_FSTAT", failing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_member_replacement_during_fstat_fallback_is_never_adopted(
    tmp_path,
    monkeypatch,
):
    context = _context()
    output = tmp_path / "package"
    member_name = Path(context.safe_members[0].logical_path).name
    member_path = output / "evidence" / member_name
    original_open = runner._os.open
    original_fstat = runner._os.fstat
    target_fd = None
    replaced = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == member_name and flags & runner._os.O_ACCMODE != runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def replacing_fstat(descriptor):
        nonlocal replaced
        if descriptor == target_fd and not replaced:
            replaced = True
            replacement = member_path.with_name("replacement.json")
            replacement.write_bytes(b"replacement\n")
            os.replace(replacement, member_path)
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "fstat", replacing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert member_path.read_bytes() == b"replacement\n"


@pytest.mark.parametrize("target", ("member", "manifest"))
def test_final_release_rejects_same_inode_same_length_byte_mutation(
    tmp_path,
    monkeypatch,
    target,
):
    context = _context()
    output = tmp_path / "package"
    original = runner._release_owned_package

    def mutating(owner, **kwargs):
        logical = (
            MANIFEST_FILENAME if target == "manifest" else context.safe_members[0].logical_path
        )
        path = output.joinpath(*logical.split("/"))
        content = bytearray(path.read_bytes())
        content[0] = ord("[") if content[0] != ord("[") else ord("{")
        with path.open("r+b") as stream:
            stream.write(content)
            stream.flush()
        return original(owner, **kwargs)

    monkeypatch.setattr(runner, "_release_owned_package", mutating)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert not output.exists()


def test_member_write_close_and_raw_close_failure_is_cleanup_failed(
    tmp_path,
    monkeypatch,
):
    context = _context()
    output = tmp_path / "package"
    member_name = Path(context.safe_members[0].logical_path).name
    original_open = runner._os.open
    original_close = runner._os.close
    original_raw_close = runner._RAW_CLOSE
    original_write = runner._os.write
    target_fd = None

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == member_name and flags & runner._os.O_ACCMODE != runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_write(descriptor, content):
        if descriptor == target_fd:
            return 0
        return original_write(descriptor, content)

    def failing_close(descriptor):
        if descriptor == target_fd:
            raise OSError("injected normal close")
        return original_close(descriptor)

    def failing_raw_close(descriptor):
        if descriptor == target_fd:
            raise OSError("injected raw close")
        return original_raw_close(descriptor)

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "write", failing_write)
    monkeypatch.setattr(runner._os, "close", failing_close)
    monkeypatch.setattr(runner, "_RAW_CLOSE", failing_raw_close)
    try:
        with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
            runner.run_sealed_evidence_package_v01(
                domain=context.domain,
                domain_projection=context.domain_projection,
                kernel_manifest_hash=context.kernel_manifest_hash,
                safe_members=context.safe_members,
                output_directory=output,
                fixture_disposable=True,
            )
    finally:
        if target_fd is not None:
            try:
                original_raw_close(target_fd)
            except OSError:
                pass


def test_silent_close_uses_raw_fallback_without_descriptor_leak(tmp_path, monkeypatch):
    context = _context()
    opened = []
    original_open = runner._os.open

    def tracking_open(*args, **kwargs):
        descriptor = original_open(*args, **kwargs)
        opened.append(descriptor)
        return descriptor

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "close", lambda _descriptor: None)
    runner.run_sealed_evidence_package_v01(
        domain=context.domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=tmp_path / "package",
        fixture_disposable=True,
    )
    for descriptor in set(opened):
        with pytest.raises(OSError):
            os.fstat(descriptor)


@pytest.mark.parametrize("operation", ("unlink", "rmdir"))
def test_cleanup_operation_failure_is_stable_and_never_claims_success(
    tmp_path,
    monkeypatch,
    operation,
):
    context = _context()
    output = tmp_path / "package"
    monkeypatch.setattr(
        runner,
        "_validate_package_directory",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("injected")),
    )
    if operation == "unlink":
        monkeypatch.setattr(
            runner._os,
            "unlink",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected")),
        )
    else:
        monkeypatch.setattr(
            runner._os,
            "rmdir",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected")),
        )
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )


@pytest.mark.parametrize("operation", ("unlink", "rmdir"))
def test_noop_cleanup_operation_is_detected(tmp_path, monkeypatch, operation):
    context = _context()
    output = tmp_path / "package"
    monkeypatch.setattr(
        runner,
        "_validate_package_directory",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("injected")),
    )
    monkeypatch.setattr(
        runner._os,
        operation,
        lambda *_args, **_kwargs: None,
    )
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_close_fallback_failure_returns_cleanup_reason(tmp_path, monkeypatch):
    context = _context()
    original_open = runner._os.open
    original_close = runner._os.close
    opened = []

    def tracking_open(*args, **kwargs):
        descriptor = original_open(*args, **kwargs)
        opened.append(descriptor)
        return descriptor

    monkeypatch.setattr(runner._os, "open", tracking_open)
    monkeypatch.setattr(runner._os, "close", lambda _descriptor: None)
    monkeypatch.setattr(
        runner,
        "_RAW_CLOSE",
        lambda _descriptor: (_ for _ in ()).throw(OSError("injected")),
    )
    try:
        with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
            runner.run_sealed_evidence_package_v01(
                domain=context.domain,
                domain_projection=context.domain_projection,
                kernel_manifest_hash=context.kernel_manifest_hash,
                safe_members=context.safe_members,
                output_directory=tmp_path / "package",
                fixture_disposable=True,
            )
    finally:
        for descriptor in set(opened):
            try:
                original_close(descriptor)
            except OSError:
                pass


def test_output_parent_symlink_swap_is_contained(tmp_path, monkeypatch):
    context = _context()
    parent = tmp_path / "parent"
    parent.mkdir()
    target = tmp_path / "target"
    target.mkdir()
    output = parent / "package"
    original = runner._create_owned_package

    def swapping(path):
        saved = tmp_path / "original-parent"
        parent.rename(saved)
        parent.symlink_to(target, target_is_directory=True)
        return original(path)

    monkeypatch.setattr(runner, "_create_owned_package", swapping)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert list(target.iterdir()) == []


def test_inventory_directory_symlink_swap_is_contained(tmp_path, monkeypatch):
    context = _context()
    output = tmp_path / "package"
    target = tmp_path / "target"
    target.mkdir()
    original = runner._inventory_at
    swapped = False

    def swapping(*args, **kwargs):
        nonlocal swapped
        if not swapped:
            swapped = True
            evidence = output / "evidence"
            evidence.rename(tmp_path / "owned-evidence")
            evidence.symlink_to(target, target_is_directory=True)
        return original(*args, **kwargs)

    monkeypatch.setattr(runner, "_inventory_at", swapping)
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_cleanup_failed"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert list(target.iterdir()) == []
    assert (output / "evidence").is_symlink()


@pytest.mark.parametrize("attack", ("empty_directory", "extra_file", "fifo"))
def test_exact_tree_rejects_unexpected_entries(tmp_path, attack):
    context, result, package = _run(tmp_path)
    target = package / "unexpected"
    if attack == "empty_directory":
        target.mkdir()
    elif attack == "extra_file":
        target.write_bytes(b"extra")
    else:
        os.mkfifo(target)
    with pytest.raises(ValueError):
        runner._validate_package_directory(
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=result.manifest,
            ordered_safe_contents=result.safe_file_contents,
        )


def test_output_parent_symlink_and_relative_path_are_rejected(tmp_path):
    context = _context()
    real_parent = tmp_path / "real"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    for output in (linked_parent / "package", Path("relative-package")):
        with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
            runner.run_sealed_evidence_package_v01(
                domain=context.domain,
                domain_projection=context.domain_projection,
                kernel_manifest_hash=context.kernel_manifest_hash,
                safe_members=context.safe_members,
                output_directory=output,
                fixture_disposable=True,
            )


def test_descriptor_read_rejects_stat_open_symlink_swap(tmp_path, monkeypatch):
    context, result, package = _run(tmp_path)
    member = package / result.manifest.safe_file_records[0].logical_path
    original_open = runner._os.open
    swapped = False

    def swapping_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if (
            path == member.name
            and flags & runner._os.O_ACCMODE == runner._os.O_RDONLY
            and not swapped
        ):
            swapped = True
            member.unlink()
            member.symlink_to(package / MANIFEST_FILENAME)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(runner._os, "open", swapping_open)
    with pytest.raises((ValueError, OSError)):
        runner._validate_package_directory(
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=result.manifest,
            ordered_safe_contents=result.safe_file_contents,
        )
    assert swapped is True


@pytest.mark.parametrize(
    "failure",
        ("short_write", "fsync", "reread", "parsed", "post_validate"),
)
def test_failed_package_creation_removes_only_invocation_owned_output(
    tmp_path,
    monkeypatch,
    failure,
):
    context = _context()
    output = tmp_path / "package"
    if failure == "short_write":
        monkeypatch.setattr(runner._os, "write", lambda _fd, _data: 0)
    elif failure == "fsync":
        monkeypatch.setattr(runner._os, "fsync", lambda _fd: (_ for _ in ()).throw(OSError("fail")))
    elif failure == "reread":
        original_read = runner._read_name_at

        def mismatching_read(*args, **kwargs):
            identity, _content = original_read(*args, **kwargs)
            return identity, b"mismatch"

        monkeypatch.setattr(runner, "_read_name_at", mismatching_read)
    elif failure == "parsed":
        original_parse = runner._strict_json_loads

        def mismatching_parse(value):
            parsed = original_parse(value)
            if isinstance(parsed, dict) and "manifest_id" in parsed:
                return {}
            return parsed

        monkeypatch.setattr(runner, "_strict_json_loads", mismatching_parse)
    else:
        monkeypatch.setattr(
            runner,
            "_validate_package_directory",
            lambda **_kwargs: (_ for _ in ()).throw(ValueError("fail")),
        )
    with pytest.raises(ValueError, match="sealed_evidence_package_runner_invalid"):
        runner.run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=output,
            fixture_disposable=True,
        )
    assert not output.exists()


@pytest.mark.parametrize(
    "argv",
    (
        ["--fixture"],
        ["--fixture", "--domain", "invalid", "--execution-head", "7bc7b8f", "--output", "/tmp/x"],
        ["--unknown", "private-value"],
        ["--fixture", "--domain", "airline", "--execution-head", "7bc7b8f", "--output", "relative"],
    ),
)
def test_cli_parser_and_relative_path_failures_are_sanitized(argv, capsys):
    assert runner.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_package_runner_invalid",
        "status": "FAIL_CLOSED",
    }
    assert "usage" not in captured.out.casefold()
    assert "private-value" not in captured.out


def test_cli_success_and_sanitized_existing_output_failure(tmp_path, capsys):
    output = tmp_path / "package"
    assert runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--output",
            str(output),
        ]
    ) == 0
    success = capsys.readouterr()
    line = json.loads(success.out)
    assert line["package_status"] == STATUS_SELF_CONSISTENT_UNANCHORED
    assert success.err == ""
    assert str(tmp_path) not in success.out
    assert runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--output",
            str(output),
        ]
    ) == 2
    failure = capsys.readouterr()
    assert json.loads(failure.out) == {
        "reason": "sealed_evidence_package_runner_invalid",
        "status": "FAIL_CLOSED",
    }
    assert failure.err == ""
    assert str(tmp_path) not in failure.out


def test_cli_preserves_only_exact_cleanup_reason(tmp_path, capsys, monkeypatch):
    def cleanup_failure(**_kwargs):
        raise ValueError(runner._CLEANUP_REASON)

    monkeypatch.setattr(runner, "run_sealed_evidence_package_v01", cleanup_failure)
    output = tmp_path / "private-output"
    assert runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--output",
            str(output),
        ]
    ) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_package_runner_cleanup_failed",
        "status": "FAIL_CLOSED",
    }
    assert str(tmp_path) not in captured.out
    assert "Traceback" not in captured.out


def test_static_import_and_call_boundary():
    tree = ast.parse(
        Path("demo/run_sealed_evidence_package_v01.py").read_text(encoding="utf-8")
    )
    import_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            import_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_roots.add(node.module.split(".")[0])
    assert not import_roots.intersection(
        {
            "requests",
            "urllib",
            "http",
            "socket",
            "subprocess",
            "openai",
            "anthropic",
            "google",
            "genai",
            "tests",
            "time",
            "random",
            "uuid",
            "secrets",
        }
    )
    calls = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    assert not calls.intersection(
        {
            "generate_content",
            "request",
            "urlopen",
            "connect",
            "collect",
            "execute_action",
            "create_receipt",
        }
    )
    source = Path("demo/run_sealed_evidence_package_v01.py").read_text(
        encoding="utf-8"
    )
    assert "getenv" not in source
    assert "environ" not in source
    assert ".glob(" not in source and ".rglob(" not in source
    assert "os.walk" not in source and "_os.walk" not in source
    assert ".read_bytes(" not in source
