import ast
from dataclasses import FrozenInstanceError, replace
import json
import os
from pathlib import Path
import shutil

import pytest

from demo import run_sealed_evidence_anchor_v01 as anchor_runner
from demo import run_sealed_evidence_package_v01 as package_runner
from hedgehog.evidence.external_anchor_v01 import (
    STATUS_EVIDENCE_ONLY,
    validate_external_anchor_publication_v01,
)


def _package(tmp_path, domain="airline", name="package"):
    context = package_runner.build_disposable_fixture_context_v01(
        domain=domain,
        execution_head="7bc7b8f",
    )
    result = package_runner.run_sealed_evidence_package_v01(
        domain=domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=tmp_path / name,
        fixture_disposable=True,
    )
    return context, result, tmp_path / name


def _anchor(tmp_path, domain="airline", package_name="package", anchor_name="anchor.json"):
    context, package_result, package = _package(tmp_path, domain, package_name)
    result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain=domain,
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=tmp_path / anchor_name,
        fixture_disposable=True,
    )
    return context, package_result, package, result, tmp_path / anchor_name


def _package_with_metadata(tmp_path, metadata, name="package"):
    context = package_runner.build_disposable_fixture_context_v01(
        domain="airline",
        execution_head="7bc7b8f",
    )
    content = package_runner.canonical_json_bytes_v01(
        {
            "safety": metadata,
            "source_record_id": context.domain_projection.source_records[0].source_record_id,
        }
    ) + b"\n"
    members = (replace(context.safe_members[0], content_bytes=content),)
    package = tmp_path / name
    result = package_runner.run_sealed_evidence_package_v01(
        domain="airline",
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=members,
        output_directory=package,
        fixture_disposable=True,
    )
    return context, result, package


def _package_with_text(tmp_path, media_type="text/plain"):
    context = package_runner.build_disposable_fixture_context_v01(
        domain="airline",
        execution_head="7bc7b8f",
    )
    content = "Résumé 安全\nsecond safe line\n".encode()
    members = (
        replace(
            context.safe_members[0],
            media_type=media_type,
            content_bytes=content,
            terminal_newline_required=True,
        ),
    )
    package = tmp_path / "package"
    result = package_runner.run_sealed_evidence_package_v01(
        domain="airline",
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=members,
        output_directory=package,
        fixture_disposable=True,
    )
    return context, result, package


def _snapshot(root):
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.mark.parametrize("domain", anchor_runner.FIXTURE_DOMAINS)
def test_both_fixture_domains_publish_evidence_only(tmp_path, domain):
    context, package_result, _, result, anchor = _anchor(tmp_path, domain)
    publication = result.anchor_publication
    assert publication.domain_id == domain
    assert publication.anchor_status == STATUS_EVIDENCE_ONLY
    assert validate_external_anchor_publication_v01(
        publication,
        manifest=package_result.manifest,
        domain_projection=context.domain_projection,
        safe_file_contents=package_result.safe_file_contents,
    ) == ()
    assert anchor.read_bytes().endswith(b"\n")


def test_publication_nonclaim_flags_and_zero_counts(tmp_path):
    _, _, _, result, _ = _anchor(tmp_path)
    publication = result.anchor_publication
    assert (
        publication.external_anchor_supplied_at_publication,
        publication.external_anchor_verified_at_publication,
        publication.anchored_pass_claimed,
    ) == (False, False, False)
    assert (
        publication.publication_provider_call_count,
        publication.publication_network_call_count,
        publication.publication_gemini_call_count,
        publication.created_authority_count,
        publication.created_permission_count,
        publication.real_world_effects_count,
    ) == (0, 0, 0, 0, 0, 0)
    assert "signature_verified" not in result.summary


@pytest.mark.parametrize("domain", anchor_runner.FIXTURE_DOMAINS)
def test_deterministic_anchor_bytes_and_identity(tmp_path, domain):
    *_, first, first_path = _anchor(tmp_path, domain, "package-a", "anchor-a.json")
    *_, second, second_path = _anchor(tmp_path, domain, "package-b", "anchor-b.json")
    assert first.anchor_publication == second.anchor_publication
    assert first_path.read_bytes() == second_path.read_bytes()


def test_changed_valid_publication_base_changes_identity(tmp_path):
    context, package_result, package = _package(tmp_path)
    first = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=tmp_path / "first.json",
        fixture_disposable=True,
    )
    second = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="1234567",
        anchor_output_file=tmp_path / "second.json",
        fixture_disposable=True,
    )
    assert first.anchor_publication.anchor_publication_id != second.anchor_publication.anchor_publication_id


@pytest.mark.parametrize("base", ("ABCDEF1", "abcdef", "g234567", "a" * 41, True))
def test_malformed_publication_base_is_rejected(tmp_path, base):
    context, package_result, package = _package(tmp_path)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head=base,
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )


@pytest.mark.parametrize(
    "attack",
    ("member", "manifest", "missing", "extra", "member_symlink", "member_directory"),
)
def test_package_inventory_and_replacement_attacks_are_rejected(tmp_path, attack):
    context, package_result, package = _package(tmp_path)
    member = package / package_result.manifest.safe_file_records[0].logical_path
    if attack == "member":
        member.write_bytes(b'{"changed":true}\n')
    elif attack == "manifest":
        (package / "sealed_package_manifest_v01.json").write_bytes(b"{}\n")
    elif attack == "missing":
        member.unlink()
    elif attack == "extra":
        (package / "extra.json").write_bytes(b"{}\n")
    elif attack == "member_symlink":
        member.unlink()
        member.symlink_to(package / "sealed_package_manifest_v01.json")
    else:
        member.unlink()
        member.mkdir()
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )


def test_package_directory_symlink_is_rejected(tmp_path):
    context, package_result, package = _package(tmp_path)
    link = tmp_path / "package-link"
    link.symlink_to(package, target_is_directory=True)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=link,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )


@pytest.mark.parametrize("attack", ("domain", "projection", "manifest_domain", "kernel"))
def test_context_binding_attacks_are_rejected(tmp_path, attack):
    context, package_result, package = _package(tmp_path)
    expected_domain = "airline"
    projection = context.domain_projection
    manifest = package_result.manifest
    if attack == "domain":
        expected_domain = "supplier_water_filter"
    elif attack == "projection":
        projection = package_runner.build_disposable_fixture_context_v01(
            domain="supplier_water_filter",
            execution_head="7bc7b8f",
        ).domain_projection
    elif attack == "manifest_domain":
        manifest = replace(manifest, domain_id="supplier_water_filter")
    else:
        manifest = replace(manifest, kernel_manifest_hash="f" * 64)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain=expected_domain,
            package_directory=package,
            domain_projection=projection,
            manifest=manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )


def test_existing_and_inside_package_outputs_are_rejected(tmp_path):
    context, package_result, package = _package(tmp_path)
    existing = tmp_path / "existing.json"
    existing.write_bytes(b"unchanged")
    for output in (existing, package / "anchor.json"):
        with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
            anchor_runner.run_sealed_evidence_anchor_v01(
                expected_domain="airline",
                package_directory=package,
                domain_projection=context.domain_projection,
                manifest=package_result.manifest,
                ordered_safe_contents=package_result.safe_file_contents,
                publication_base_head="abcdef1",
                anchor_output_file=output,
                fixture_disposable=True,
            )
    assert existing.read_bytes() == b"unchanged"


def test_anchor_output_target_symlink_is_rejected(tmp_path):
    context, package_result, package = _package(tmp_path)
    target = tmp_path / "target.json"
    target.write_bytes(b"unchanged")
    output = tmp_path / "anchor-link.json"
    output.symlink_to(target)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert target.read_bytes() == b"unchanged"
    assert output.is_symlink()


def test_package_bytes_remain_immutable(tmp_path):
    context, package_result, package = _package(tmp_path)
    before = _snapshot(package)
    anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=tmp_path / "anchor.json",
        fixture_disposable=True,
    )
    assert _snapshot(package) == before


def test_anchor_output_is_canonical_one_lf_and_private(tmp_path):
    _, _, _, _, anchor = _anchor(tmp_path)
    content = anchor.read_bytes()
    assert content.endswith(b"\n") and not content.endswith(b"\n\n")
    assert b"\r" not in content
    assert content == anchor_runner.canonical_json_bytes_v01(json.loads(content)) + b"\n"
    assert anchor.stat().st_mode & 0o077 == 0


def test_result_is_frozen(tmp_path):
    *_, result, _ = _anchor(tmp_path)
    with pytest.raises(FrozenInstanceError):
        result.domain = "changed"


def test_result_summary_is_immutable_and_fixture_label_is_bound(tmp_path):
    context, package_result, package, result, _ = _anchor(tmp_path)
    with pytest.raises(TypeError):
        result.summary["anchor_status"] = "changed"
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "second-anchor.json",
            fixture_disposable=False,
        )


@pytest.mark.parametrize(
    "metadata",
    (
        {
            "contains_raw_prompt": False,
            "contains_raw_provider_response": False,
            "secret_scan_passed": True,
        },
        {
            "raw_prompt_included": False,
            "raw_provider_response_included": False,
            "secret_scan_passed": True,
        },
    ),
)
def test_anchor_accepts_safe_airline_and_supplier_metadata(tmp_path, metadata):
    context, package_result, package = _package_with_metadata(tmp_path, metadata)
    result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=tmp_path / "anchor.json",
        fixture_disposable=True,
    )
    assert result.anchor_publication.anchor_status == STATUS_EVIDENCE_ONLY


def test_anchor_scanner_allows_authorization_references_and_token_metrics(tmp_path):
    _, package_result, _ = _package(tmp_path)
    content = anchor_runner.canonical_json_bytes_v01(
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
    anchor_runner._scan_content(content, package_result.manifest.safe_file_records[0])


@pytest.mark.parametrize(
    "key,value",
    (
        ("contains_raw_prompt", True),
        ("raw_provider_response_included", True),
        ("secret_scan_passed", False),
        ("raw_prompt", False),
        ("provider_response_backup", "private"),
        ("private_key", "private"),
    ),
)
def test_anchor_scanner_rejects_mutated_unsafe_metadata(tmp_path, key, value):
    _, package_result, _ = _package(tmp_path)
    content = anchor_runner.canonical_json_bytes_v01({key: value}) + b"\n"
    with pytest.raises(ValueError):
        anchor_runner._scan_content(content, package_result.manifest.safe_file_records[0])


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
def test_anchor_rejects_security_token_and_value_bypasses(tmp_path, payload):
    _, package_result, _ = _package(tmp_path)
    content = anchor_runner.canonical_json_bytes_v01(payload) + b"\n"
    with pytest.raises(ValueError):
        anchor_runner._scan_content(content, package_result.manifest.safe_file_records[0])


@pytest.mark.parametrize(
    "content",
    (b"api_key: private\n", b"credential=private\n", b"-----BEGIN PRIVATE KEY-----\nx\n"),
)
def test_anchor_rejects_plaintext_private_material(tmp_path, content):
    _, package_result, _ = _package(tmp_path)
    record = replace(
        package_result.manifest.safe_file_records[0],
        media_type="text/plain",
    )
    with pytest.raises(ValueError):
        anchor_runner._scan_content(content, record)


@pytest.mark.parametrize("media_type", ("text/plain", "text/markdown"))
def test_anchor_accepts_safe_multiline_text(tmp_path, media_type):
    context, package_result, package = _package_with_text(tmp_path, media_type)
    result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=tmp_path / "anchor.json",
        fixture_disposable=True,
    )
    assert result.anchor_publication.anchor_status == STATUS_EVIDENCE_ONLY


@pytest.mark.parametrize("target", ("member", "manifest", "root"))
def test_anchor_detects_same_bytes_different_inode_package_replacement(
    tmp_path,
    monkeypatch,
    target,
):
    context, package_result, package = _package(tmp_path)
    original = anchor_runner._validate_package
    replaced = False

    def replacing(**kwargs):
        nonlocal replaced
        if not replaced:
            replaced = True
            if target == "root":
                saved = tmp_path / "original-package"
                package.rename(saved)
                shutil.copytree(saved, package)
            else:
                logical = (
                    "sealed_package_manifest_v01.json"
                    if target == "manifest"
                    else package_result.manifest.safe_file_records[0].logical_path
                )
                path = package.joinpath(*logical.split("/"))
                replacement = path.with_name(path.name + ".replacement")
                replacement.write_bytes(path.read_bytes())
                os.replace(replacement, path)
        return original(**kwargs)

    monkeypatch.setattr(anchor_runner, "_validate_package", replacing)
    output = tmp_path / "anchor.json"
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert not output.exists()


def test_anchor_same_bytes_output_replacement_is_preserved_and_cleanup_fails(
    tmp_path,
    monkeypatch,
):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    original = anchor_runner._write_canonical_output

    def replacing(*args, **kwargs):
        owner = original(*args, **kwargs)
        replacement = tmp_path / "replacement.json"
        replacement.write_bytes(output.read_bytes())
        os.replace(replacement, output)
        return owner

    monkeypatch.setattr(anchor_runner, "_write_canonical_output", replacing)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_cleanup_failed"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_anchor_output_fstat_failure_recovers_identity(tmp_path, monkeypatch):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    original_open = anchor_runner._os.open
    original_fstat = anchor_runner._os.fstat
    target_fd = None
    failed = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & anchor_runner._os.O_ACCMODE != anchor_runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        nonlocal failed
        if descriptor == target_fd and not failed:
            failed = True
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(anchor_runner._os, "open", tracking_open)
    monkeypatch.setattr(anchor_runner._os, "fstat", failing_fstat)
    result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=output,
        fixture_disposable=True,
    )
    assert failed is True and result.anchor_publication.anchor_status == STATUS_EVIDENCE_ONLY


def test_anchor_unprovable_initial_output_ownership_fails_cleanup_closed(
    tmp_path,
    monkeypatch,
):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    original_open = anchor_runner._os.open
    original_fstat = anchor_runner._os.fstat
    target_fd = None

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & anchor_runner._os.O_ACCMODE != anchor_runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        if descriptor == target_fd:
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(anchor_runner._os, "open", tracking_open)
    monkeypatch.setattr(anchor_runner._os, "fstat", failing_fstat)
    monkeypatch.setattr(anchor_runner, "_RAW_FSTAT", failing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_cleanup_failed"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_anchor_replacement_during_fstat_fallback_is_never_adopted(
    tmp_path,
    monkeypatch,
):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    original_open = anchor_runner._os.open
    original_fstat = anchor_runner._os.fstat
    target_fd = None
    replaced = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & anchor_runner._os.O_ACCMODE != anchor_runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def replacing_fstat(descriptor):
        nonlocal replaced
        if descriptor == target_fd and not replaced:
            replaced = True
            replacement = tmp_path / "replacement.json"
            replacement.write_bytes(b"replacement\n")
            os.replace(replacement, output)
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(anchor_runner._os, "open", tracking_open)
    monkeypatch.setattr(anchor_runner._os, "fstat", replacing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_cleanup_failed"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert output.read_bytes() == b"replacement\n"


@pytest.mark.parametrize("target", ("output", "member", "manifest"))
def test_anchor_final_release_rejects_same_inode_same_length_mutation(
    tmp_path,
    monkeypatch,
    target,
):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    original = anchor_runner._release_owned_output

    def mutating(owner, **kwargs):
        if target == "output":
            path = output
        elif target == "manifest":
            path = package / "sealed_package_manifest_v01.json"
        else:
            path = package / package_result.manifest.safe_file_records[0].logical_path
        content = bytearray(path.read_bytes())
        content[0] = ord("[") if content[0] != ord("[") else ord("{")
        with path.open("r+b") as stream:
            stream.write(content)
            stream.flush()
        return original(owner, **kwargs)

    monkeypatch.setattr(anchor_runner, "_release_owned_output", mutating)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert not output.exists()


def test_anchor_silent_close_uses_raw_fallback_without_leak(tmp_path, monkeypatch):
    context, package_result, package = _package(tmp_path)
    original_open = anchor_runner._os.open
    opened = []

    def tracking_open(*args, **kwargs):
        descriptor = original_open(*args, **kwargs)
        opened.append(descriptor)
        return descriptor

    monkeypatch.setattr(anchor_runner._os, "open", tracking_open)
    monkeypatch.setattr(anchor_runner._os, "close", lambda _descriptor: None)
    anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=tmp_path / "anchor.json",
        fixture_disposable=True,
    )
    for descriptor in set(opened):
        with pytest.raises(OSError):
            os.fstat(descriptor)


def test_anchor_unlink_failure_returns_cleanup_failed(tmp_path, monkeypatch):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    monkeypatch.setattr(
        anchor_runner._os,
        "fsync",
        lambda _descriptor: (_ for _ in ()).throw(OSError("injected")),
    )
    monkeypatch.setattr(
        anchor_runner._os,
        "unlink",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected")),
    )
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_cleanup_failed"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_anchor_noop_unlink_is_cleanup_failed(tmp_path, monkeypatch):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    monkeypatch.setattr(
        anchor_runner._os,
        "fsync",
        lambda _descriptor: (_ for _ in ()).throw(OSError("injected")),
    )
    monkeypatch.setattr(anchor_runner._os, "unlink", lambda *_args, **_kwargs: None)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_cleanup_failed"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert output.exists()


def test_anchor_output_parent_symlink_swap_is_contained(tmp_path, monkeypatch):
    context, package_result, package = _package(tmp_path)
    parent = tmp_path / "output-parent"
    parent.mkdir()
    target = tmp_path / "target-parent"
    target.mkdir()
    output = parent / "anchor.json"
    original = anchor_runner._write_canonical_output

    def swapping(*args, **kwargs):
        parent.rename(tmp_path / "original-output-parent")
        parent.symlink_to(target, target_is_directory=True)
        return original(*args, **kwargs)

    monkeypatch.setattr(anchor_runner, "_write_canonical_output", swapping)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert list(target.iterdir()) == []


def test_anchor_package_parent_symlink_swap_during_read_is_contained(
    tmp_path,
    monkeypatch,
):
    container = tmp_path / "container"
    container.mkdir()
    context, package_result, package = _package(
        tmp_path,
        name="container/package",
    )
    target = tmp_path / "target-container"
    target.mkdir()
    original = anchor_runner._validate_package

    def swapping(**kwargs):
        container.rename(tmp_path / "original-container")
        container.symlink_to(target, target_is_directory=True)
        return original(**kwargs)

    monkeypatch.setattr(anchor_runner, "_validate_package", swapping)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )
    assert list(target.iterdir()) == []


@pytest.mark.parametrize("attack", ("empty_directory", "fifo", "manifest_symlink"))
def test_anchor_exact_inventory_rejects_unexpected_and_nonregular_entries(tmp_path, attack):
    context, package_result, package = _package(tmp_path)
    target = package / "unexpected"
    if attack == "empty_directory":
        target.mkdir()
    elif attack == "fifo":
        import os

        os.mkfifo(target)
    else:
        manifest = package / "sealed_package_manifest_v01.json"
        saved = tmp_path / "saved-manifest.json"
        manifest.rename(saved)
        manifest.symlink_to(saved)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )


def test_anchor_rejects_relative_paths_and_symlinked_output_parent(tmp_path):
    context, package_result, package = _package(tmp_path)
    real_parent = tmp_path / "real"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    cases = (
        (Path("relative-package"), tmp_path / "anchor-a.json"),
        (package, Path("relative-anchor.json")),
        (package, linked_parent / "anchor.json"),
    )
    for package_path, output in cases:
        with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
            anchor_runner.run_sealed_evidence_anchor_v01(
                expected_domain="airline",
                package_directory=package_path,
                domain_projection=context.domain_projection,
                manifest=package_result.manifest,
                ordered_safe_contents=package_result.safe_file_contents,
                publication_base_head="abcdef1",
                anchor_output_file=output,
                fixture_disposable=True,
            )


def test_anchor_descriptor_read_rejects_stat_open_symlink_swap(tmp_path, monkeypatch):
    context, package_result, package = _package(tmp_path)
    member = package / package_result.manifest.safe_file_records[0].logical_path
    original_open = anchor_runner._os.open
    swapped = False

    def swapping_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if (
            path == member.name
            and flags & anchor_runner._os.O_ACCMODE == anchor_runner._os.O_RDONLY
            and not swapped
        ):
            swapped = True
            member.unlink()
            member.symlink_to(package / "sealed_package_manifest_v01.json")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(anchor_runner._os, "open", swapping_open)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=tmp_path / "anchor.json",
            fixture_disposable=True,
        )
    assert swapped is True


@pytest.mark.parametrize("failure", ("short_write", "fsync", "reread", "parsed", "post_package"))
def test_anchor_output_failures_leave_no_output(tmp_path, monkeypatch, failure):
    context, package_result, package = _package(tmp_path)
    output = tmp_path / "anchor.json"
    if failure == "short_write":
        monkeypatch.setattr(anchor_runner._os, "write", lambda _fd, _data: 0)
    elif failure == "fsync":
        monkeypatch.setattr(anchor_runner._os, "fsync", lambda _fd: (_ for _ in ()).throw(OSError("fail")))
    elif failure == "reread":
        original_read = anchor_runner._read_name_at

        def mismatching_read(parent_fd, name, **kwargs):
            identity, content = original_read(parent_fd, name, **kwargs)
            if name == output.name:
                return identity, b"{}\n"
            return identity, content

        monkeypatch.setattr(anchor_runner, "_read_name_at", mismatching_read)
    elif failure == "parsed":
        original_parse = anchor_runner._strict_json

        def mismatching_parse(content):
            parsed = original_parse(content)
            if isinstance(parsed, dict) and "anchor_publication_id" in parsed:
                return {}
            return parsed

        monkeypatch.setattr(anchor_runner, "_strict_json", mismatching_parse)
    else:
        original_write = anchor_runner._write_canonical_output
        member = package / package_result.manifest.safe_file_records[0].logical_path

        def mutating_write(*args, **kwargs):
            identity = original_write(*args, **kwargs)
            member.write_bytes(b'{"changed":true}\n')
            return identity

        monkeypatch.setattr(anchor_runner, "_write_canonical_output", mutating_write)
    with pytest.raises(ValueError, match="sealed_evidence_anchor_runner_invalid"):
        anchor_runner.run_sealed_evidence_anchor_v01(
            expected_domain="airline",
            package_directory=package,
            domain_projection=context.domain_projection,
            manifest=package_result.manifest,
            ordered_safe_contents=package_result.safe_file_contents,
            publication_base_head="abcdef1",
            anchor_output_file=output,
            fixture_disposable=True,
        )
    assert not output.exists()


@pytest.mark.parametrize(
    "argv",
    (
        ["--fixture"],
        ["--fixture", "--domain", "invalid"],
        ["--unknown", "private-value"],
        ["--fixture", "--domain", "airline", "--execution-head", "7bc7b8f", "--package", "relative", "--publication-base-head", "abcdef1", "--anchor-output", "relative"],
    ),
)
def test_anchor_cli_parser_failures_are_sanitized(argv, capsys):
    assert anchor_runner.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_anchor_runner_invalid",
        "status": "FAIL_CLOSED",
    }
    assert "usage" not in captured.out.casefold()
    assert "private-value" not in captured.out


def test_cli_success_and_sanitized_failure(tmp_path, capsys):
    _, _, package = _package(tmp_path)
    anchor = tmp_path / "anchor.json"
    args = [
        "--fixture",
        "--domain",
        "airline",
        "--execution-head",
        "7bc7b8f",
        "--package",
        str(package),
        "--publication-base-head",
        "abcdef1",
        "--anchor-output",
        str(anchor),
    ]
    assert anchor_runner.main(args) == 0
    success = capsys.readouterr()
    assert json.loads(success.out)["anchor_status"] == STATUS_EVIDENCE_ONLY
    assert success.err == "" and str(tmp_path) not in success.out
    assert anchor_runner.main(args) == 2
    failure = capsys.readouterr()
    assert json.loads(failure.out) == {
        "reason": "sealed_evidence_anchor_runner_invalid",
        "status": "FAIL_CLOSED",
    }
    assert failure.err == "" and str(tmp_path) not in failure.out


def test_anchor_cli_preserves_only_exact_cleanup_reason(tmp_path, capsys, monkeypatch):
    _, _, package = _package(tmp_path)

    def cleanup_failure(**_kwargs):
        raise ValueError(anchor_runner._CLEANUP_REASON)

    monkeypatch.setattr(anchor_runner, "run_sealed_evidence_anchor_v01", cleanup_failure)
    assert anchor_runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--package",
            str(package),
            "--publication-base-head",
            "abcdef1",
            "--anchor-output",
            str(tmp_path / "private-anchor.json"),
        ]
    ) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_anchor_runner_cleanup_failed",
        "status": "FAIL_CLOSED",
    }
    assert str(tmp_path) not in captured.out
    assert "Traceback" not in captured.out


def test_static_boundary_and_no_anchored_verification_creation():
    path = Path("demo/run_sealed_evidence_anchor_v01.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert not roots.intersection(
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
    source = path.read_text(encoding="utf-8")
    assert "build_anchored_package_verification_v01" not in source
    assert "getenv" not in source and "environ" not in source
    assert ".glob(" not in source and ".rglob(" not in source
    assert "os.walk" not in source and "_os.walk" not in source
    assert ".read_bytes(" not in source
