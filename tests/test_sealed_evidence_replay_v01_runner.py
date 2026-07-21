import ast
from dataclasses import fields, replace
import json
import os
from pathlib import Path
import shutil

import pytest

from demo import run_sealed_evidence_anchor_v01 as anchor_runner
from demo import run_sealed_evidence_package_v01 as package_runner
from demo import run_sealed_evidence_replay_v01 as replay_runner
from hedgehog.evidence.external_anchor_v01 import (
    STATUS_ANCHORED_PASS,
    STATUS_FAIL_CLOSED as ANCHOR_FAIL_CLOSED,
    validate_anchored_package_verification_v01,
)
from hedgehog.evidence.sealed_evidence_profile_v01 import (
    build_domain_evidence_projection_v01,
    build_domain_execution_identity_v01,
    build_live_attempt_identity_v01,
    validate_domain_evidence_projection_v01,
)
from hedgehog.evidence.sealed_replay_evidence_v01 import (
    STATUS_FAIL_CLOSED as REPLAY_FAIL_CLOSED,
    STATUS_PASS,
    validate_sealed_replay_evidence_v01,
)


EXPECTED_RESULT_FIELDS = (
    "domain",
    "anchor_publication",
    "anchored_verification",
    "reconstructed_manifest",
    "replay_evidence",
    "fixture_disposable",
    "summary",
)


def _chain(tmp_path, domain="airline", suffix=""):
    context = package_runner.build_disposable_fixture_context_v01(
        domain=domain,
        execution_head="7bc7b8f",
    )
    package = tmp_path / f"package{suffix}"
    package_result = package_runner.run_sealed_evidence_package_v01(
        domain=domain,
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=context.safe_members,
        output_directory=package,
        fixture_disposable=True,
    )
    anchor = tmp_path / f"anchor{suffix}.json"
    anchor_result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain=domain,
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=anchor,
        fixture_disposable=True,
    )
    return context, package_result, package, anchor_result, anchor


def _chain_with_metadata(tmp_path, metadata):
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
    package = tmp_path / "package"
    package_result = package_runner.run_sealed_evidence_package_v01(
        domain="airline",
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=members,
        output_directory=package,
        fixture_disposable=True,
    )
    anchor = tmp_path / "anchor.json"
    anchor_result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=anchor,
        fixture_disposable=True,
    )
    return context, package_result, package, anchor_result, anchor


def _chain_with_text(tmp_path, media_type="text/plain"):
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
    package_result = package_runner.run_sealed_evidence_package_v01(
        domain="airline",
        domain_projection=context.domain_projection,
        kernel_manifest_hash=context.kernel_manifest_hash,
        safe_members=members,
        output_directory=package,
        fixture_disposable=True,
    )
    anchor = tmp_path / "anchor.json"
    anchor_result = anchor_runner.run_sealed_evidence_anchor_v01(
        expected_domain="airline",
        package_directory=package,
        domain_projection=context.domain_projection,
        manifest=package_result.manifest,
        ordered_safe_contents=package_result.safe_file_contents,
        publication_base_head="abcdef1",
        anchor_output_file=anchor,
        fixture_disposable=True,
    )
    return context, package_result, package, anchor_result, anchor


def _run(
    tmp_path,
    *,
    domain="airline",
    supplied_anchor_id=None,
    reconstructed_projection=None,
    evidence_refs=("fixture:replay:package", "fixture:replay:anchor"),
    suffix="",
):
    context, package_result, package, anchor_result, anchor = _chain(
        tmp_path,
        domain,
        suffix,
    )
    if supplied_anchor_id is None:
        supplied_anchor_id = anchor_result.anchor_publication.anchor_publication_id
    if reconstructed_projection is None:
        reconstructed_projection = context.domain_projection
    output = tmp_path / f"replay{suffix}.json"
    result = replay_runner.run_sealed_evidence_replay_v01(
        expected_domain=domain,
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=supplied_anchor_id,
        reconstructed_domain_projection=reconstructed_projection,
        replay_output_file=output,
        evidence_refs=evidence_refs,
        fixture_disposable=True,
    )
    return context, package_result, package, anchor_result, anchor, result, output


def _snapshot(path):
    if path.is_file():
        return path.read_bytes()
    return tuple(
        (str(item.relative_to(path)), item.read_bytes())
        for item in sorted(path.rglob("*"))
        if item.is_file()
    )


def _distinct_valid_projection(source):
    execution = build_domain_execution_identity_v01(
        programme_identity=source.programme_identity,
        domain_id=source.domain_execution_identity.domain_id,
        execution_head="abcdef2",
        source_task_id=source.domain_execution_identity.source_task_id,
        run_id=source.domain_execution_identity.run_id + ":reconstructed",
        report_id=source.domain_execution_identity.report_id + ":reconstructed",
    )
    original_attempt = source.attempt_identity
    attempt = build_live_attempt_identity_v01(
        programme_identity=source.programme_identity,
        domain_execution_identity=execution,
        attempt_number=original_attempt.attempt_number,
        package_id=original_attempt.package_id,
        logical_package_ref=original_attempt.logical_package_ref,
        output_directory_ref=original_attempt.output_directory_ref,
        provider_mode=original_attempt.provider_mode,
        model_id=original_attempt.model_id,
        expected_actor_count=original_attempt.expected_actor_count,
        provider_call_budget=original_attempt.provider_call_budget,
    )
    projection = build_domain_evidence_projection_v01(
        programme_identity=source.programme_identity,
        domain_execution_identity=execution,
        attempt_identity=attempt,
        source_records=source.source_records,
        artifact_records=source.artifact_records,
        kernel_artifact_refs=source.kernel_artifact_refs,
        causal_consumption_refs=source.causal_consumption_refs,
        evidence_refs=source.evidence_refs,
        limitation_refs=source.limitation_refs,
    )
    assert validate_domain_evidence_projection_v01(projection) == ()
    return projection


def test_public_surface_and_result_field_order():
    assert replay_runner.MODULE_ID == "run_sealed_evidence_replay_v01"
    assert replay_runner.FIXTURE_DOMAINS == ("airline", "supplier_water_filter")
    assert tuple(field.name for field in fields(replay_runner.SealedEvidenceReplayRunResultV01)) == EXPECTED_RESULT_FIELDS
    assert callable(replay_runner.run_sealed_evidence_replay_v01)
    assert callable(replay_runner.main)


@pytest.mark.parametrize("domain", replay_runner.FIXTURE_DOMAINS)
def test_exact_anchor_and_reconstruction_pass_for_both_domains(tmp_path, domain):
    context, package_result, _, anchor_result, _, result, output = _run(
        tmp_path,
        domain=domain,
    )
    verification = result.anchored_verification
    replay = result.replay_evidence
    assert result.domain == domain
    assert verification.verification_status == STATUS_ANCHORED_PASS
    assert replay.replay_status == STATUS_PASS
    assert (replay.integrity_verified, replay.continuity_verified, replay.anchor_verified) == (True, True, True)
    assert replay.source_manifest_id == replay.reconstructed_manifest_id
    assert replay.source_domain_projection_id == replay.reconstructed_domain_projection_id
    assert replay.source_package_content_hash == replay.reconstructed_package_content_hash
    assert replay.source_file_order_hash == replay.reconstructed_file_order_hash
    assert replay.source_artifact_order_hash == replay.reconstructed_artifact_order_hash
    assert validate_anchored_package_verification_v01(
        verification,
        anchor_publication=anchor_result.anchor_publication,
        manifest=package_result.manifest,
        domain_projection=context.domain_projection,
        safe_file_contents=package_result.safe_file_contents,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
    ) == ()
    assert output.read_bytes().endswith(b"\n")
    assert not output.read_bytes().endswith(b"\n\n")
    assert json.loads(output.read_text(encoding="utf-8"))["replay_evidence"]["replay_status"] == STATUS_PASS


def test_anchor_nonclaims_and_all_replay_counters_are_zero(tmp_path):
    *_, result, _ = _run(tmp_path)
    verification = result.anchored_verification
    replay = result.replay_evidence
    assert (
        verification.external_anchor_supplied,
        verification.external_anchor_verified,
        verification.manifest_binding_verified,
        verification.package_binding_verified,
    ) == (True, True, True, True)
    assert (
        verification.signature_verified,
        verification.signer_identity_verified,
        verification.root_attestation_verified,
    ) == (False, False, False)
    assert (
        replay.semantic_rerun_count,
        replay.root_decision_rerun_count,
        replay.corridor_rerun_count,
        replay.provider_call_count,
        replay.network_call_count,
        replay.gemini_call_count,
        replay.created_authority_count,
        replay.created_permission_count,
        replay.action_created_count,
        replay.receipt_created_count,
        replay.final_output_created_count,
        replay.real_world_effects_count,
    ) == (0,) * 12


def test_replay_result_summary_is_immutable_and_fixture_label_is_bound(tmp_path):
    context, package_result, package, anchor_result, anchor, result, _ = _run(tmp_path)
    with pytest.raises(TypeError):
        result.summary["replay_status"] = "changed"
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=tmp_path / "second-replay.json",
            evidence_refs=("fixture:replay:label",),
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
def test_replay_accepts_safe_airline_and_supplier_metadata(tmp_path, metadata):
    context, package_result, package, anchor_result, anchor = _chain_with_metadata(
        tmp_path,
        metadata,
    )
    result = replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
        reconstructed_domain_projection=context.domain_projection,
        replay_output_file=tmp_path / "replay.json",
        evidence_refs=("fixture:replay:safe-metadata",),
        fixture_disposable=True,
    )
    assert result.anchored_verification.verification_status == STATUS_ANCHORED_PASS
    assert result.replay_evidence.replay_status == STATUS_PASS


def test_replay_scanner_allows_authorization_references_and_token_metrics(tmp_path):
    _, package_result, _, _, _ = _chain(tmp_path)
    content = replay_runner.canonical_json_bytes_v01(
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
    replay_runner._scan_content(content, package_result.manifest.safe_file_records[0])


@pytest.mark.parametrize(
    "key,value",
    (
        ("contains_raw_provider_response", True),
        ("raw_prompt_included", 0),
        ("secret_scan_passed", False),
        ("prompt_text", "private"),
        ("provider_response_backup", "private"),
        ("credential_material", "private"),
    ),
)
def test_replay_scanner_rejects_mutated_unsafe_metadata(tmp_path, key, value):
    _, package_result, _, _, _ = _chain(tmp_path)
    content = replay_runner.canonical_json_bytes_v01({key: value}) + b"\n"
    with pytest.raises(ValueError):
        replay_runner._scan_content(content, package_result.manifest.safe_file_records[0])


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
def test_replay_rejects_security_token_and_value_bypasses(tmp_path, payload):
    _, package_result, _, _, _ = _chain(tmp_path)
    content = replay_runner.canonical_json_bytes_v01(payload) + b"\n"
    with pytest.raises(ValueError):
        replay_runner._scan_content(content, package_result.manifest.safe_file_records[0])


@pytest.mark.parametrize(
    "content",
    (b"api_key: private\n", b"credential=private\n", b"-----BEGIN PRIVATE KEY-----\nx\n"),
)
def test_replay_rejects_plaintext_private_material(tmp_path, content):
    _, package_result, _, _, _ = _chain(tmp_path)
    record = replace(
        package_result.manifest.safe_file_records[0],
        media_type="text/plain",
    )
    with pytest.raises(ValueError):
        replay_runner._scan_content(content, record)


@pytest.mark.parametrize("media_type", ("text/plain", "text/markdown"))
def test_replay_accepts_safe_multiline_text(tmp_path, media_type):
    context, package_result, package, anchor_result, anchor = _chain_with_text(
        tmp_path,
        media_type,
    )
    result = replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=(
            anchor_result.anchor_publication.anchor_publication_id
        ),
        reconstructed_domain_projection=context.domain_projection,
        replay_output_file=tmp_path / "replay.json",
        evidence_refs=("fixture:replay:multiline",),
        fixture_disposable=True,
    )
    assert result.replay_evidence.replay_status == STATUS_PASS


@pytest.mark.parametrize("target", ("member", "manifest", "root", "anchor"))
def test_replay_detects_same_bytes_different_inode_source_replacement(
    tmp_path,
    monkeypatch,
    target,
):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    original = replay_runner._validate_source_package
    replaced = False

    def replacing(**kwargs):
        nonlocal replaced
        if not replaced:
            replaced = True
            if target == "root":
                saved = tmp_path / "original-package"
                package.rename(saved)
                shutil.copytree(saved, package)
            elif target == "anchor":
                replacement = tmp_path / "anchor-replacement.json"
                replacement.write_bytes(anchor.read_bytes())
                os.replace(replacement, anchor)
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

    monkeypatch.setattr(replay_runner, "_validate_source_package", replacing)
    output = tmp_path / "replay.json"
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=(
                anchor_result.anchor_publication.anchor_publication_id
            ),
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:identity-replacement",),
            fixture_disposable=True,
        )
    assert not output.exists()


def test_replay_same_bytes_output_replacement_is_preserved_and_cleanup_fails(
    tmp_path,
    monkeypatch,
):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    original = replay_runner._write_canonical_output

    def replacing(*args, **kwargs):
        owner = original(*args, **kwargs)
        replacement = tmp_path / "replay-replacement.json"
        replacement.write_bytes(output.read_bytes())
        os.replace(replacement, output)
        return owner

    monkeypatch.setattr(replay_runner, "_write_canonical_output", replacing)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_cleanup_failed"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=(
                anchor_result.anchor_publication.anchor_publication_id
            ),
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:output-replacement",),
            fixture_disposable=True,
        )
    assert output.exists()


def test_replay_silent_close_uses_raw_fallback_without_leak(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    original_open = replay_runner._os.open
    opened = []

    def tracking_open(*args, **kwargs):
        descriptor = original_open(*args, **kwargs)
        opened.append(descriptor)
        return descriptor

    monkeypatch.setattr(replay_runner._os, "open", tracking_open)
    monkeypatch.setattr(replay_runner._os, "close", lambda _descriptor: None)
    replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
        reconstructed_domain_projection=context.domain_projection,
        replay_output_file=tmp_path / "replay.json",
        evidence_refs=("fixture:replay:close-proof",),
        fixture_disposable=True,
    )
    for descriptor in set(opened):
        with pytest.raises(OSError):
            os.fstat(descriptor)


def test_replay_unlink_failure_returns_cleanup_failed(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    monkeypatch.setattr(
        replay_runner._os,
        "fsync",
        lambda _descriptor: (_ for _ in ()).throw(OSError("injected")),
    )
    monkeypatch.setattr(
        replay_runner._os,
        "unlink",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected")),
    )
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_cleanup_failed"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:unlink-failure",),
            fixture_disposable=True,
        )
    assert output.exists()


def test_replay_noop_unlink_is_cleanup_failed(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    monkeypatch.setattr(
        replay_runner._os,
        "fsync",
        lambda _descriptor: (_ for _ in ()).throw(OSError("injected")),
    )
    monkeypatch.setattr(replay_runner._os, "unlink", lambda *_args, **_kwargs: None)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_cleanup_failed"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=(
                anchor_result.anchor_publication.anchor_publication_id
            ),
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:noop-unlink",),
            fixture_disposable=True,
        )
    assert output.exists()


def test_replay_output_parent_symlink_swap_is_contained(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    parent = tmp_path / "output-parent"
    parent.mkdir()
    target = tmp_path / "target-parent"
    target.mkdir()
    output = parent / "replay.json"
    original = replay_runner._write_canonical_output

    def swapping(*args, **kwargs):
        parent.rename(tmp_path / "original-output-parent")
        parent.symlink_to(target, target_is_directory=True)
        return original(*args, **kwargs)

    monkeypatch.setattr(replay_runner, "_write_canonical_output", swapping)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:parent-swap",),
            fixture_disposable=True,
        )
    assert list(target.iterdir()) == []


def test_replay_output_fstat_failure_recovers_identity(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    original_open = replay_runner._os.open
    original_fstat = replay_runner._os.fstat
    target_fd = None
    failed = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & replay_runner._os.O_ACCMODE != replay_runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        nonlocal failed
        if descriptor == target_fd and not failed:
            failed = True
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(replay_runner._os, "open", tracking_open)
    monkeypatch.setattr(replay_runner._os, "fstat", failing_fstat)
    result = replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
        reconstructed_domain_projection=context.domain_projection,
        replay_output_file=output,
        evidence_refs=("fixture:replay:fstat-recovery",),
        fixture_disposable=True,
    )
    assert failed is True and result.replay_evidence.replay_status == STATUS_PASS


def test_replay_output_persistent_descriptor_identity_failure_is_cleanup_failed(
    tmp_path,
    monkeypatch,
):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    original_open = replay_runner._os.open
    original_fstat = replay_runner._os.fstat
    target_fd = None

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & replay_runner._os.O_ACCMODE != replay_runner._os.O_RDONLY:
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor):
        if descriptor == target_fd:
            raise OSError("injected")
        return original_fstat(descriptor)

    monkeypatch.setattr(replay_runner._os, "open", tracking_open)
    monkeypatch.setattr(replay_runner._os, "fstat", failing_fstat)
    monkeypatch.setattr(replay_runner, "_RAW_FSTAT", failing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_cleanup_failed"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:persistent-fstat",),
            fixture_disposable=True,
        )
    assert output.exists()


def test_replay_output_replacement_during_fstat_fallback_is_never_adopted(
    tmp_path,
    monkeypatch,
):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    original_open = replay_runner._os.open
    original_fstat = replay_runner._os.fstat
    target_fd = None
    replaced = False

    def tracking_open(path, flags, *args, **kwargs):
        nonlocal target_fd
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == output.name and flags & replay_runner._os.O_ACCMODE != replay_runner._os.O_RDONLY:
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

    monkeypatch.setattr(replay_runner._os, "open", tracking_open)
    monkeypatch.setattr(replay_runner._os, "fstat", replacing_fstat)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_cleanup_failed"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:fstat-replacement",),
            fixture_disposable=True,
        )
    assert output.read_bytes() == b"replacement\n"


@pytest.mark.parametrize("target", ("output", "member", "manifest", "anchor"))
def test_replay_final_release_rejects_same_inode_same_length_mutation(
    tmp_path,
    monkeypatch,
    target,
):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    original = replay_runner._release_owned_output

    def mutating(owner, **kwargs):
        if target == "output":
            path = output
        elif target == "anchor":
            path = anchor
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

    monkeypatch.setattr(replay_runner, "_release_owned_output", mutating)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=(
                anchor_result.anchor_publication.anchor_publication_id
            ),
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:final-release-mutation",),
            fixture_disposable=True,
        )
    assert not output.exists()


def test_equivalent_chains_produce_deterministic_replay_bytes(tmp_path):
    *_, first, first_output = _run(tmp_path, suffix="-a")
    *_, second, second_output = _run(tmp_path, suffix="-b")
    assert first.anchored_verification == second.anchored_verification
    assert first.replay_evidence == second.replay_evidence
    assert first_output.read_bytes() == second_output.read_bytes()


def test_replay_rebuilds_records_and_manifest_from_reread_bytes(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    calls = {"file": 0, "manifest": 0}
    original_file = replay_runner.build_safe_file_record_v01
    original_manifest = replay_runner.build_sealed_package_manifest_v01

    def file_builder(**kwargs):
        calls["file"] += 1
        return original_file(**kwargs)

    def manifest_builder(**kwargs):
        calls["manifest"] += 1
        return original_manifest(**kwargs)

    monkeypatch.setattr(replay_runner, "build_safe_file_record_v01", file_builder)
    monkeypatch.setattr(replay_runner, "build_sealed_package_manifest_v01", manifest_builder)
    result = replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
        reconstructed_domain_projection=context.domain_projection,
        replay_output_file=tmp_path / "replay.json",
        evidence_refs=("fixture:replay:reread",),
        fixture_disposable=True,
    )
    assert calls == {"file": package_result.manifest.file_count, "manifest": 1}
    assert result.reconstructed_manifest is not package_result.manifest
    assert result.reconstructed_manifest == package_result.manifest


@pytest.mark.parametrize("wrong_id", ("0" * 64, "f" * 64))
def test_well_formed_wrong_anchor_is_coherent_fail_closed(tmp_path, wrong_id):
    context, package_result, _, anchor_result, _, result, output = _run(
        tmp_path,
        supplied_anchor_id=wrong_id,
    )
    verification = result.anchored_verification
    replay = result.replay_evidence
    assert wrong_id != anchor_result.anchor_publication.anchor_publication_id
    assert verification.verification_status == ANCHOR_FAIL_CLOSED
    assert verification.external_anchor_supplied is True
    assert verification.external_anchor_verified is False
    assert replay.replay_status == REPLAY_FAIL_CLOSED
    assert replay.anchor_verified is False
    assert validate_sealed_replay_evidence_v01(
        replay,
        source_manifest=package_result.manifest,
        source_domain_projection=context.domain_projection,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_publication=anchor_result.anchor_publication,
        anchored_verification=verification,
        supplied_anchor_publication_id=wrong_id,
        reconstructed_manifest=result.reconstructed_manifest,
        reconstructed_domain_projection=context.domain_projection,
        reconstructed_safe_file_contents=package_result.safe_file_contents,
    ) == ()
    assert output.exists()


def test_distinct_valid_reconstructed_projection_is_coherent_continuity_failure(tmp_path):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    reconstructed = _distinct_valid_projection(context.domain_projection)
    result = replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
        reconstructed_domain_projection=reconstructed,
        replay_output_file=tmp_path / "replay.json",
        evidence_refs=("fixture:replay:projection-drift",),
        fixture_disposable=True,
    )
    replay = result.replay_evidence
    assert replay.integrity_verified is True
    assert replay.anchor_verified is True
    assert replay.continuity_verified is False
    assert replay.replay_status == REPLAY_FAIL_CLOSED
    assert replay.source_manifest_id != replay.reconstructed_manifest_id
    assert replay.source_domain_projection_id != replay.reconstructed_domain_projection_id


@pytest.mark.parametrize("bad_id", ("bad", "A" * 64, "0" * 63, True, b"0" * 64))
def test_malformed_anchor_id_is_rejected_without_output(tmp_path, bad_id):
    context, package_result, package, _, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    with pytest.raises(ValueError, match="^sealed_evidence_replay_runner_invalid$"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=bad_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:invalid-anchor",),
            fixture_disposable=True,
        )
    assert not output.exists()


@pytest.mark.parametrize(
    "attack",
    ("anchor", "member", "manifest", "missing", "extra", "symlink", "directory"),
)
def test_anchor_and_package_mutations_are_rejected(tmp_path, attack):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    member = package / package_result.manifest.safe_file_records[0].logical_path
    if attack == "anchor":
        anchor.write_bytes(b"{}\n")
    elif attack == "member":
        member.write_bytes(b'{"changed":true}\n')
    elif attack == "manifest":
        (package / "sealed_package_manifest_v01.json").write_bytes(b"{}\n")
    elif attack == "missing":
        member.unlink()
    elif attack == "extra":
        (package / "extra.json").write_bytes(b"{}\n")
    elif attack == "symlink":
        member.unlink()
        member.symlink_to(package / "sealed_package_manifest_v01.json")
    else:
        member.unlink()
        member.mkdir()
    with pytest.raises(ValueError, match="^sealed_evidence_replay_runner_invalid$"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=tmp_path / "replay.json",
            evidence_refs=("fixture:replay:mutation",),
            fixture_disposable=True,
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("manifest_id", "0" * 64),
        ("package_content_hash", "0" * 64),
        ("file_count", 2),
        ("artifact_count", 2),
        ("domain_projection_id", "0" * 64),
    ),
)
def test_source_manifest_identity_count_and_hash_drift_is_rejected(tmp_path, field, value):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    forged = replace(package_result.manifest, **{field: value})
    with pytest.raises(ValueError, match="^sealed_evidence_replay_runner_invalid$"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=forged,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=tmp_path / "replay.json",
            evidence_refs=("fixture:replay:manifest-drift",),
            fixture_disposable=True,
        )


@pytest.mark.parametrize(
    "refs",
    ((), [], ("duplicate", "duplicate"), ("../escape",), ("",), ("bad\\ref",)),
)
def test_invalid_evidence_reference_geometry_is_rejected(tmp_path, refs):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    with pytest.raises(ValueError, match="^sealed_evidence_replay_runner_invalid$"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=tmp_path / "replay.json",
            evidence_refs=refs,
            fixture_disposable=True,
        )


def test_existing_and_forbidden_output_locations_are_rejected(tmp_path):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    existing = tmp_path / "existing.json"
    existing.write_bytes(b"sentinel")
    for output in (existing, package / "replay.json", anchor):
        with pytest.raises(ValueError, match="^sealed_evidence_replay_runner_invalid$"):
            replay_runner.run_sealed_evidence_replay_v01(
                expected_domain="airline",
                package_directory=package,
                source_domain_projection=context.domain_projection,
                source_manifest=package_result.manifest,
                source_safe_file_contents=package_result.safe_file_contents,
                anchor_file=anchor,
                supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
                reconstructed_domain_projection=context.domain_projection,
                replay_output_file=output,
                evidence_refs=("fixture:replay:output-boundary",),
                fixture_disposable=True,
            )
    assert existing.read_bytes() == b"sentinel"


def test_replay_output_target_symlink_is_rejected(tmp_path):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    target = tmp_path / "target.json"
    target.write_bytes(b"unchanged")
    output = tmp_path / "replay-link.json"
    output.symlink_to(target)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:output-symlink",),
            fixture_disposable=True,
        )
    assert target.read_bytes() == b"unchanged"
    assert output.is_symlink()


def test_positive_replay_does_not_mutate_package_or_anchor(tmp_path):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    package_before = _snapshot(package)
    anchor_before = _snapshot(anchor)
    replay_runner.run_sealed_evidence_replay_v01(
        expected_domain="airline",
        package_directory=package,
        source_domain_projection=context.domain_projection,
        source_manifest=package_result.manifest,
        source_safe_file_contents=package_result.safe_file_contents,
        anchor_file=anchor,
        supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
        reconstructed_domain_projection=context.domain_projection,
        replay_output_file=tmp_path / "replay.json",
        evidence_refs=("fixture:replay:immutability",),
        fixture_disposable=True,
    )
    assert _snapshot(package) == package_before
    assert _snapshot(anchor) == anchor_before


def test_mid_reconstruction_package_mutation_never_writes_replay(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    original = replay_runner._rebuild_records
    member = package / package_result.manifest.safe_file_records[0].logical_path

    def mutating_rebuild(**kwargs):
        result = original(**kwargs)
        member.write_bytes(b'{"changed":true}\n')
        return result

    monkeypatch.setattr(replay_runner, "_rebuild_records", mutating_rebuild)
    output = tmp_path / "replay.json"
    with pytest.raises(ValueError, match="^sealed_evidence_replay_runner_invalid$"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:race",),
            fixture_disposable=True,
        )
    assert not output.exists()


@pytest.mark.parametrize("attack", ("empty_directory", "fifo", "manifest_symlink"))
def test_replay_exact_inventory_rejects_unexpected_and_nonregular_entries(tmp_path, attack):
    import os

    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    target = package / "unexpected"
    if attack == "empty_directory":
        target.mkdir()
    elif attack == "fifo":
        os.mkfifo(target)
    else:
        manifest = package / "sealed_package_manifest_v01.json"
        saved = tmp_path / "saved-manifest.json"
        manifest.rename(saved)
        manifest.symlink_to(saved)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=tmp_path / "replay.json",
            evidence_refs=("fixture:replay:inventory",),
            fixture_disposable=True,
        )


def test_replay_rejects_relative_paths_and_symlinked_parent(tmp_path):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    real_parent = tmp_path / "real"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    cases = (
        (Path("relative-package"), anchor, tmp_path / "one.json"),
        (package, Path("relative-anchor.json"), tmp_path / "two.json"),
        (package, anchor, Path("relative-replay.json")),
        (package, anchor, linked_parent / "replay.json"),
    )
    for package_path, anchor_path, output in cases:
        with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
            replay_runner.run_sealed_evidence_replay_v01(
                expected_domain="airline",
                package_directory=package_path,
                source_domain_projection=context.domain_projection,
                source_manifest=package_result.manifest,
                source_safe_file_contents=package_result.safe_file_contents,
                anchor_file=anchor_path,
                supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
                reconstructed_domain_projection=context.domain_projection,
                replay_output_file=output,
                evidence_refs=("fixture:replay:path-boundary",),
                fixture_disposable=True,
            )


def test_replay_descriptor_read_rejects_stat_open_symlink_swap(tmp_path, monkeypatch):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    member = package / package_result.manifest.safe_file_records[0].logical_path
    original_open = replay_runner._os.open
    swapped = False

    def swapping_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if (
            path == member.name
            and flags & replay_runner._os.O_ACCMODE == replay_runner._os.O_RDONLY
            and not swapped
        ):
            swapped = True
            member.unlink()
            member.symlink_to(package / "sealed_package_manifest_v01.json")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(replay_runner._os, "open", swapping_open)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=tmp_path / "replay.json",
            evidence_refs=("fixture:replay:swap",),
            fixture_disposable=True,
        )
    assert swapped is True


@pytest.mark.parametrize(
    "failure",
        ("short_write", "fsync", "reread", "parsed", "post_package", "post_anchor"),
)
def test_replay_output_failures_leave_no_output(tmp_path, monkeypatch, failure):
    context, package_result, package, anchor_result, anchor = _chain(tmp_path)
    output = tmp_path / "replay.json"
    if failure == "short_write":
        monkeypatch.setattr(replay_runner._os, "write", lambda _fd, _data: 0)
    elif failure == "fsync":
        monkeypatch.setattr(replay_runner._os, "fsync", lambda _fd: (_ for _ in ()).throw(OSError("fail")))
    elif failure == "reread":
        original_read = replay_runner._read_name_at

        def mismatching_read(parent_fd, name, **kwargs):
            identity, content = original_read(parent_fd, name, **kwargs)
            if name == output.name:
                return identity, b"{}\n"
            return identity, content

        monkeypatch.setattr(replay_runner, "_read_name_at", mismatching_read)
    elif failure == "parsed":
        original_parse = replay_runner._strict_json

        def mismatching_parse(content):
            parsed = original_parse(content)
            if isinstance(parsed, dict) and "replay_evidence" in parsed:
                return {}
            return parsed

        monkeypatch.setattr(replay_runner, "_strict_json", mismatching_parse)
    else:
        original_write = replay_runner._write_canonical_output
        member = package / package_result.manifest.safe_file_records[0].logical_path

        def mutating_write(*args, **kwargs):
            identity = original_write(*args, **kwargs)
            if failure == "post_package":
                member.write_bytes(b'{"changed":true}\n')
            else:
                anchor.write_bytes(b"{}\n")
            return identity

        monkeypatch.setattr(replay_runner, "_write_canonical_output", mutating_write)
    with pytest.raises(ValueError, match="sealed_evidence_replay_runner_invalid"):
        replay_runner.run_sealed_evidence_replay_v01(
            expected_domain="airline",
            package_directory=package,
            source_domain_projection=context.domain_projection,
            source_manifest=package_result.manifest,
            source_safe_file_contents=package_result.safe_file_contents,
            anchor_file=anchor,
            supplied_anchor_publication_id=anchor_result.anchor_publication.anchor_publication_id,
            reconstructed_domain_projection=context.domain_projection,
            replay_output_file=output,
            evidence_refs=("fixture:replay:output-failure",),
            fixture_disposable=True,
        )
    assert not output.exists()


def test_cli_success_and_wrong_anchor_have_one_safe_json_line(tmp_path, capsys):
    _, _, package, anchor_result, anchor = _chain(tmp_path)
    success = replay_runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--package",
            str(package),
            "--anchor",
            str(anchor),
            "--supplied-anchor-id",
            anchor_result.anchor_publication.anchor_publication_id,
            "--replay-output",
            str(tmp_path / "cli-pass.json"),
            "--evidence-ref",
            "fixture:cli:replay",
        ]
    )
    captured = capsys.readouterr()
    assert success == 0
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out)["replay_status"] == STATUS_PASS

    failed = replay_runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--package",
            str(package),
            "--anchor",
            str(anchor),
            "--supplied-anchor-id",
            "0" * 64,
            "--replay-output",
            str(tmp_path / "cli-fail.json"),
            "--evidence-ref",
            "fixture:cli:replay",
        ]
    )
    captured = capsys.readouterr()
    assert failed == 3
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    summary = json.loads(captured.out)
    assert summary["verification_status"] == ANCHOR_FAIL_CLOSED
    assert summary["replay_status"] == REPLAY_FAIL_CLOSED
    assert "Traceback" not in captured.out
    assert str(tmp_path) not in captured.out


def test_cli_malformed_failure_is_stable_and_sanitized(tmp_path, capsys):
    _, _, package, _, anchor = _chain(tmp_path)
    code = replay_runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--package",
            str(package),
            "--anchor",
            str(anchor),
            "--supplied-anchor-id",
            "bad",
            "--replay-output",
            str(tmp_path / "cli-invalid.json"),
            "--evidence-ref",
            "fixture:cli:replay",
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_replay_runner_invalid",
        "status": "FAIL_CLOSED",
    }
    assert "Traceback" not in captured.out
    assert str(tmp_path) not in captured.out


@pytest.mark.parametrize(
    "argv",
    (
        ["--fixture"],
        ["--fixture", "--domain", "invalid"],
        ["--unknown", "private-value"],
        ["--fixture", "--domain", "airline", "--execution-head", "7bc7b8f", "--package", "relative", "--anchor", "relative", "--supplied-anchor-id", "0" * 64, "--replay-output", "relative", "--evidence-ref", "fixture:ref"],
    ),
)
def test_replay_cli_parser_failures_are_sanitized(argv, capsys):
    assert replay_runner.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_replay_runner_invalid",
        "status": "FAIL_CLOSED",
    }
    assert "usage" not in captured.out.casefold()
    assert "private-value" not in captured.out


def test_replay_cli_preserves_only_exact_cleanup_reason(tmp_path, capsys, monkeypatch):
    _, _, package, anchor_result, anchor = _chain(tmp_path)

    def cleanup_failure(**_kwargs):
        raise ValueError(replay_runner._CLEANUP_REASON)

    monkeypatch.setattr(replay_runner, "run_sealed_evidence_replay_v01", cleanup_failure)
    assert replay_runner.main(
        [
            "--fixture",
            "--domain",
            "airline",
            "--execution-head",
            "7bc7b8f",
            "--package",
            str(package),
            "--anchor",
            str(anchor),
            "--supplied-anchor-id",
            anchor_result.anchor_publication.anchor_publication_id,
            "--replay-output",
            str(tmp_path / "private-replay.json"),
            "--evidence-ref",
            "fixture:replay:cleanup",
        ]
    ) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert json.loads(captured.out) == {
        "reason": "sealed_evidence_replay_runner_cleanup_failed",
        "status": "FAIL_CLOSED",
    }
    assert str(tmp_path) not in captured.out
    assert "Traceback" not in captured.out


def test_static_dependency_boundary():
    path = Path(replay_runner.__file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_roots = {
        "anthropic",
        "demo.run_full_wow_v1_2_product_trace",
        "google",
        "httpx",
        "openai",
        "requests",
        "socket",
        "subprocess",
        "tests",
        "time",
        "uuid",
    }
    imports = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    assert not any(
        imported == root or imported.startswith(root + ".")
        for imported in imports
        for root in forbidden_roots
    )
    assert calls.isdisjoint(
        {
            "generate_content",
            "getenv",
            "run",
            "system",
            "urlopen",
            "uuid4",
        }
    )
    assert "provider" not in imports
    assert "ActionCommitPacket" not in source
    assert "real_world_effects_count" in source
    assert ".glob(" not in source and ".rglob(" not in source
    assert "os.walk" not in source and "_os.walk" not in source
    assert ".read_bytes(" not in source
