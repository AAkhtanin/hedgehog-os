"""Read-only Airline/Supplier sealed-evidence comparison and X1 index writer."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import unicodedata

from demo import run_full_wow_v1_2_product_trace as product_trace_runner
from demo import run_supplier_water_filter_negative_matrix_v01 as supplier_s2
from demo import run_two_domain_airline_a2_seal_v01 as airline_runner
from hedgehog.domains.airline import sealed_evidence_a2_binding_v01 as airline_binding
from hedgehog.domains.supplier_water_filter import kernel_adapter_v01 as supplier_kernel
from hedgehog.domains.supplier_water_filter import sealed_evidence_package_adapter_v01 as supplier_adapter
from hedgehog.evidence import external_anchor_v01 as anchor_contract
from hedgehog.evidence import sealed_evidence_profile_v01 as evidence_profile
from hedgehog.evidence import sealed_package_v01 as package_contract
from hedgehog.evidence import sealed_replay_evidence_v01 as replay_contract


PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
GATE_ID = "two_domain_all_real_sealed_evidence_program_v01_x1_cross_domain_audit"
INDEX_VERSION = "v0.1"
INDEX_DOMAIN = "hedgehog-os:two-domain-cross-domain-evidence-index:v0.1"
STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
EXPECTED_HEAD = "fd745d5499aa58c1fdd070297ae27f91146e933a"
CANONICAL_OUTPUT_REF = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/"
    "cross_domain_evidence_index_v01.json"
)
MAX_SOURCE_BYTES = 4 * 1024 * 1024
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HEAD = re.compile(r"^[0-9a-f]{40}$")

AIRLINE_SAFE_REPORT_SHA256 = "2a83abbee906a3ccd047728353dfd333424cd9898e2ae39e4eca0abbecb4def7"
AIRLINE_PACKAGE_INDEX_ID = "6314b619a99d03b9a32e5a3cd581f1f28e487e2677b42a3b7e2d88d2ba12375d"
AIRLINE_MANIFEST_ID = "7b98bcbc23a0148a83c9b2d459f9d0ae35d9161c90a2938620c529e84049b8ee"
AIRLINE_PACKAGE_CONTENT_HASH = "3d8aa5aab285ead0320acf29cd3bd0e791faf6e4ba7b4c7e5b67c268d0e0a248"
AIRLINE_ANCHOR_ID = "5c198968c12f30ffa3e4e06739d889d69665017c56020686f200bbe2e89dec99"
AIRLINE_VERIFICATION_ID = "23fcd6aa8f3a5eeb788baa04a5a8181f2ebf39db194e6d6db781ae68dc49f972"
AIRLINE_REPLAY_ID = "4b04d59c237d82ef1d87a3dc9b21170db1da5e91da2d862fd1ec5ad96f56f0b2"
AIRLINE_REPLAY_SHA256 = "9caa9361746660c08b8e20f75bba5e5f07336e8dfbf0ab744ec98e1d346dac39"
AIRLINE_STORY_SHA256 = "488b9cef815184b2eb5cdd1109faac938497f344fbdcbc5a11d55e924f7b75f7"

SUPPLIER_S1_SHA256 = "293a6ed1f0b943557e2bd33f2ac52f49610e8924574d2784af328d964ba1d666"
SUPPLIER_S2_SHA256 = "8d59848127872cc813d5941f4cce587155eadc5c50ea916c07487687d4ce9969"
SUPPLIER_SAFE_EVIDENCE_INDEX_ID = "8b3ae934b9fc20cd95a4eea2add9d58cecf3653c87a5a8e56bbd26367cab6f0b"
SUPPLIER_PACKAGE_INDEX_ID = "b32b500207f65ef3cb0691646a84c5d532b0c7e619bb1cff7766ef62ff9d0925"
SUPPLIER_MANIFEST_ID = "2fa0351036c242d2bb362eb0f35d824d5bb9fb26685d0014ad632f87f32a71a8"
SUPPLIER_PACKAGE_CONTENT_HASH = "04f1bdf8a0289600730f3af5bf14e17344c2fe9b987f7e6df4defc003798b0c3"
SUPPLIER_ANCHOR_ID = "2308a41f244062ec19a30f9de6864fbb670f889cef20a3e028fbc6bb6ffe259f"
SUPPLIER_VERIFICATION_ID = "0d3438120e3bbb5f9c59309e015adaaa147b6aefa4263dcbf2bcfa19f28db529"
SUPPLIER_REPLAY_ID = "3157e9341c3e200d5bd3002f3a1858fc74188ad0fd86834e58300cb7d1d9c4ed"
SUPPLIER_REPLAY_SHA256 = "666ab84f04a9f75bc510dade055d4d4e777712aeadb013cb79b00358aff9de55"
SUPPLIER_STORY_SHA256 = "422087c73dfc7a84b5e3528395918d60e66e33b65812693f5159147daacbe533"
SUPPLIER_ADAPTER_ID = "d3a235c3614d122b17dd785c019e6bf7b93c4029d5d0058b429a353366030499"
SUPPLIER_SCENARIO_INDEX_ID = "b6ec902f266043bdef7f08ef73371fb1e5752aa84b5e87056be03b62953af20c"


SOURCE_REFS = {
    "airline_safe_report": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_execution_report_attempt_04_v01.json",
    "airline_package_index": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_package_index_v01.json",
    "airline_member_01": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01/evidence/01-airline-safe-execution-report-v01.json",
    "airline_member_02": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01/evidence/02-airline-source-lineage-v01.json",
    "airline_member_03": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01/evidence/03-airline-a2-typed-context-v01.json",
    "airline_member_04": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01/evidence/04-airline-sealed-evidence-adapter-result-v01.json",
    "airline_manifest": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01/sealed_package_manifest_v01.json",
    "airline_anchor": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_crypto_anchor_v01.json",
    "airline_replay": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_replay_report_v01.json",
    "airline_generation_audit": "docs/audit_reports/auditor_two_domain_airline_all_real_generation_attempt_04_v01.log",
    "airline_anchor_audit": "docs/audit_reports/auditor_two_domain_airline_anchor_publication_v01.log",
    "airline_replay_audit": "docs/audit_reports/auditor_two_domain_airline_anchored_replay_v01.log",
    "airline_human_story": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_human_story_v01.md",
    "supplier_s1_report": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_safe_execution_report_v01.json",
    "supplier_s2_evidence": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_water_filter_negative_matrix_v01.json",
    "supplier_safe_evidence_index": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_safe_evidence_index_v01.json",
    "supplier_package_index": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_safe_package_index_v01.json",
    "supplier_member_01": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_sealed_package_v01/evidence/01-supplier-safe-evidence-index-v01.json",
    "supplier_manifest": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_sealed_package_v01/sealed_package_manifest_v01.json",
    "supplier_anchor": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_crypto_anchor_v01.json",
    "supplier_replay": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_replay_report_v01.json",
    "supplier_s1_audit": "docs/audit_reports/auditor_two_domain_supplier_water_filter_generation_v01.log",
    "supplier_anchor_audit": "docs/audit_reports/auditor_two_domain_supplier_anchor_publication_v01.log",
    "supplier_replay_audit": "docs/audit_reports/auditor_two_domain_supplier_anchored_replay_v01.log",
    "supplier_human_story": "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_human_story_v01.md",
}

EXPECTED_HASHES = {
    "airline_safe_report": AIRLINE_SAFE_REPORT_SHA256,
    "airline_package_index": "333ee37ee3c5d85fb1158b4ad663f6464138fa2252007630f1bf2a4eae44cb25",
    "airline_member_01": AIRLINE_SAFE_REPORT_SHA256,
    "airline_member_02": "c1562090af6212c66d7a7e23cfe82f31d84fa0e6bc0fc734f9c68d1e287b3555",
    "airline_member_03": "b8418e89e2d2b67a40ac83d255c976fdfbffefa3afabe6be774456bc0ff8a4aa",
    "airline_member_04": "26c0688c1ba46266604dd91b58991c1211de1642fca36128b6c42bcf1b293a70",
    "airline_manifest": "691d39788df1738d0cd8698b5174ccdee36bf42c173582e089a6dbcf3bb074fe",
    "airline_anchor": "c551963a060f33d0407c4590db97ff4482277de7ac33b0c4fdd9ad1ed2d3d13c",
    "airline_replay": AIRLINE_REPLAY_SHA256,
    "airline_generation_audit": "9b2c4243512f6405eebdcf6cb606374d0d8d2b8593c440cb6e39556d4dd08760",
    "airline_anchor_audit": "1cfea24a111d226371a53be0d8c3eaa1d83d7ee53677b5c661b44512b21ca2cd",
    "airline_replay_audit": "bf4a6f580e369181cb03a4bea31b817ce70421137d8296039e69797c43792abc",
    "airline_human_story": AIRLINE_STORY_SHA256,
    "supplier_s1_report": SUPPLIER_S1_SHA256,
    "supplier_s2_evidence": SUPPLIER_S2_SHA256,
    "supplier_safe_evidence_index": "6d197bf9a181c621ff130f1d1a2599b1ce007e6edffdf157c41c77f736d2df5f",
    "supplier_package_index": "3a9502777cdb1c0d96cf7800d888ba5da0b19033ba0173049bf3a80e197ab200",
    "supplier_member_01": "6d197bf9a181c621ff130f1d1a2599b1ce007e6edffdf157c41c77f736d2df5f",
    "supplier_manifest": "0f87bfc7234a5c0cf3cdca6530c77dcc9a5b1d84337a8809ee9c0794afd12c92",
    "supplier_anchor": "54cf0f57b3af138cb30311f11537980e9b2b6983cd428af17b326b96d1e23f8b",
    "supplier_replay": SUPPLIER_REPLAY_SHA256,
    "supplier_s1_audit": "3405c628f5d0612f86ad464743287dbfbe666b67da267d237b9ead4729da4616",
    "supplier_anchor_audit": "2e2d9400c2d992c9bd9d0a58f4ecfd50d7f6af988ea69545c67c2e8326c8109c",
    "supplier_replay_audit": "7e5f4926355925a4e3f9e3b05fc0dabc830317307f0bce46d978a9a0687ca629",
    "supplier_human_story": SUPPLIER_STORY_SHA256,
}


@dataclass(frozen=True, slots=True)
class SourceSnapshotV01:
    logical_name: str
    repository_relative_path: str
    sha256: str
    byte_count: int
    mode: int
    device: int
    inode: int
    content: bytes


@dataclass(frozen=True, slots=True)
class LoadedCrossDomainSourcesV01:
    repository_root: Path
    snapshots: tuple[SourceSnapshotV01, ...]

    def named(self, logical_name: str) -> SourceSnapshotV01:
        matches = tuple(item for item in self.snapshots if item.logical_name == logical_name)
        if len(matches) != 1:
            raise ValueError("cross_domain_source_invalid")
        return matches[0]


@dataclass(frozen=True, slots=True)
class EvidenceFileBindingV01:
    repository_relative_path: str
    sha256: str
    byte_count: int
    mode: str


@dataclass(frozen=True, slots=True)
class IdentityBindingV01:
    identity_name: str
    identity_value: str


@dataclass(frozen=True, slots=True)
class GeometryFactV01:
    fact_name: str
    fact_value: str


@dataclass(frozen=True, slots=True)
class DomainEvidenceRecordV01:
    domain_id: str
    source_heads: tuple[IdentityBindingV01, ...]
    evidence_files: tuple[EvidenceFileBindingV01, ...]
    identities: tuple[IdentityBindingV01, ...]
    public_call_geometry: tuple[GeometryFactV01, ...]
    root_corridor_receipt_geometry: tuple[GeometryFactV01, ...]
    outcome_and_effect_boundaries: tuple[GeometryFactV01, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClaimEvidenceRowV01:
    claim_id: str
    claim_text: str
    scope: str
    evidence_refs: tuple[str, ...]
    source_hashes_and_identities: tuple[str, ...]
    validation_status: str
    limitations: tuple[str, ...]
    required_non_claims: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CrossDomainEvidenceIndexV01:
    index_id: str
    index_version: str
    programme_id: str
    gate_id: str
    execution_head: str
    airline: DomainEvidenceRecordV01
    supplier_water_filter: DomainEvidenceRecordV01
    claim_evidence_matrix: tuple[ClaimEvidenceRowV01, ...]
    differences: tuple[str, ...]
    unchanged_authority_laws: tuple[str, ...]
    required_non_claims: tuple[str, ...]
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    real_world_effects_count: int
    validation_errors: tuple[str, ...]
    final_status: str


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def canonical_json_line_v01(value: object) -> bytes:
    return _canonical_bytes(value) + b"\n"


def _plain(value: object) -> dict[str, object]:
    if not hasattr(value, "__dataclass_fields__"):
        raise ValueError("cross_domain_result_invalid")
    return asdict(value)


def _identity(result: CrossDomainEvidenceIndexV01) -> str:
    plain = _plain(result)
    plain["index_id"] = "0" * 64
    return hashlib.sha256(INDEX_DOMAIN.encode("ascii") + b"\0" + _canonical_bytes(plain)).hexdigest()


def _strict_pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError("cross_domain_json_invalid")
        result[key] = value
    return result


def _reject_nonfinite(_: str) -> object:
    raise ValueError("cross_domain_json_invalid")


def strict_json_bytes_v01(content: bytes) -> dict[str, object]:
    if (
        not content
        or len(content) > MAX_SOURCE_BYTES
        or content.startswith(b"\xef\xbb\xbf")
        or b"\0" in content
        or b"\r" in content
        or not content.endswith(b"\n")
        or content.endswith(b"\n\n")
    ):
        raise ValueError("cross_domain_json_invalid")
    try:
        text = content[:-1].decode("utf-8", "strict")
        value = json.loads(
            text,
            object_pairs_hook=_strict_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise ValueError("cross_domain_json_invalid") from None
    def unsafe(item: object) -> bool:
        if type(item) is str:
            return (
                unicodedata.normalize("NFC", item) != item
                or any(ord(character) < 32 for character in item)
            )
        if type(item) is list:
            return any(unsafe(child) for child in item)
        if type(item) is dict:
            return any(unsafe(key) or unsafe(child) for key, child in item.items())
        return False

    if type(value) is not dict or unsafe(value) or canonical_json_line_v01(value) != content:
        raise ValueError("cross_domain_json_invalid")
    return value


def _strict_public_text(content: bytes) -> str:
    if (
        not content
        or len(content) > MAX_SOURCE_BYTES
        or content.startswith(b"\xef\xbb\xbf")
        or b"\0" in content
        or b"\r" in content
        or not content.endswith(b"\n")
        or content.endswith(b"\n\n")
    ):
        raise ValueError("cross_domain_text_invalid")
    try:
        text = content.decode("utf-8", "strict")
    except UnicodeDecodeError:
        raise ValueError("cross_domain_text_invalid") from None
    if unicodedata.normalize("NFC", text) != text:
        raise ValueError("cross_domain_text_invalid")
    lowered = text.casefold()
    forbidden = ("/users/", "api_key=", "authorization: bearer", "raw_response.txt", "prompt.txt")
    if any(item in lowered for item in forbidden):
        raise ValueError("cross_domain_text_invalid")
    return text


def _valid_ref(value: str) -> bool:
    if type(value) is not str or not value or "\\" in value or "\0" in value:
        return False
    path = PurePosixPath(value)
    return (
        str(path) == value
        and not path.is_absolute()
        and all(part not in ("", ".", "..") for part in path.parts)
    )


def _open_root(root: Path) -> int:
    if not root.is_absolute() or str(root) != os.path.normpath(str(root)):
        raise ValueError("cross_domain_repository_root_invalid")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
    info = os.fstat(descriptor)
    entry = os.stat(root, follow_symlinks=False)
    if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != (entry.st_dev, entry.st_ino):
        os.close(descriptor)
        raise ValueError("cross_domain_repository_root_invalid")
    return descriptor


def _read_ref(root_fd: int, logical_name: str, ref: str) -> SourceSnapshotV01:
    if not _valid_ref(ref):
        raise ValueError("cross_domain_source_path_invalid")
    parts = PurePosixPath(ref).parts
    directory_fd = os.dup(root_fd)
    descriptor = -1
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        descriptor = os.open(parts[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
        before = os.fstat(descriptor)
        entry = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or (before.st_dev, before.st_ino) != (entry.st_dev, entry.st_ino):
            raise ValueError("cross_domain_source_invalid")
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_SOURCE_BYTES:
                raise ValueError("cross_domain_source_invalid")
            chunks.append(chunk)
        content = b"".join(chunks)
        after = os.fstat(descriptor)
        final_entry = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        identity = (before.st_dev, before.st_ino, before.st_size, stat.S_IMODE(before.st_mode))
        if identity != (after.st_dev, after.st_ino, after.st_size, stat.S_IMODE(after.st_mode)) or identity != (
            final_entry.st_dev,
            final_entry.st_ino,
            final_entry.st_size,
            stat.S_IMODE(final_entry.st_mode),
        ) or len(content) != before.st_size:
            raise ValueError("cross_domain_source_changed")
        return SourceSnapshotV01(
            logical_name=logical_name,
            repository_relative_path=ref,
            sha256=hashlib.sha256(content).hexdigest(),
            byte_count=len(content),
            mode=stat.S_IMODE(before.st_mode),
            device=before.st_dev,
            inode=before.st_ino,
            content=content,
        )
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)


def _git(repository_root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ("git", "-C", str(repository_root), *args),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode:
        raise ValueError("cross_domain_git_binding_invalid")
    return completed.stdout


def load_cross_domain_sources_v01(
    *,
    repository_root: Path,
    source_refs: dict[str, str],
    require_committed: bool = True,
) -> LoadedCrossDomainSourcesV01:
    if type(source_refs) is not dict or set(source_refs) != set(SOURCE_REFS):
        raise ValueError("cross_domain_source_set_invalid")
    if any(source_refs[name] != expected for name, expected in SOURCE_REFS.items()):
        raise ValueError("cross_domain_source_path_invalid")
    if len(set(source_refs.values())) != len(source_refs):
        raise ValueError("cross_domain_source_alias_invalid")
    root_fd = _open_root(repository_root)
    try:
        snapshots = tuple(_read_ref(root_fd, name, source_refs[name]) for name in SOURCE_REFS)
    finally:
        os.close(root_fd)
    identities = tuple((item.device, item.inode) for item in snapshots)
    if len(set(identities)) != len(identities):
        raise ValueError("cross_domain_source_alias_invalid")
    for item in snapshots:
        if item.sha256 != EXPECTED_HASHES[item.logical_name]:
            raise ValueError("cross_domain_source_hash_invalid")
        if item.repository_relative_path.endswith(".json"):
            strict_json_bytes_v01(item.content)
        else:
            _strict_public_text(item.content)
        if require_committed and _git(repository_root, "show", f"HEAD:{item.repository_relative_path}") != item.content:
            raise ValueError("cross_domain_source_not_committed")
    if require_committed:
        head = _git(repository_root, "rev-parse", "HEAD").decode("ascii").strip()
        if head != EXPECTED_HEAD:
            raise ValueError("cross_domain_head_invalid")
    loaded = LoadedCrossDomainSourcesV01(repository_root=repository_root, snapshots=snapshots)
    verify_source_continuity_v01(loaded)
    return loaded


def verify_source_continuity_v01(sources: LoadedCrossDomainSourcesV01) -> None:
    root_fd = _open_root(sources.repository_root)
    try:
        current = tuple(_read_ref(root_fd, item.logical_name, item.repository_relative_path) for item in sources.snapshots)
    finally:
        os.close(root_fd)
    for before, after in zip(sources.snapshots, current, strict=True):
        if before != after:
            raise ValueError("cross_domain_source_changed")


def _hydrate(cls: type[object], plain: object) -> object:
    return airline_binding._hydrate_dataclass(cls, plain)


def _validate_replay_chain(
    *,
    manifest: package_contract.SealedPackageManifestV01,
    domain_projection: evidence_profile.DomainEvidenceProjectionV01,
    contents: tuple[bytes, ...],
    anchor_plain: dict[str, object],
    replay_plain: dict[str, object],
    expected_anchor_id: str,
    expected_verification_id: str,
    expected_replay_id: str,
) -> None:
    publication = _hydrate(anchor_contract.ExternalAnchorPublicationV01, anchor_plain)
    verification = _hydrate(anchor_contract.AnchoredPackageVerificationV01, replay_plain.get("anchored_verification"))
    replay = _hydrate(replay_contract.SealedReplayEvidenceV01, replay_plain.get("replay_evidence"))
    reconstructed = package_contract.build_sealed_package_manifest_v01(
        domain_projection=domain_projection,
        safe_file_records=manifest.safe_file_records,
        safe_file_contents=contents,
        kernel_manifest_hash=manifest.kernel_manifest_hash,
    )
    if (
        anchor_contract.validate_external_anchor_publication_v01(
            publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=contents,
        )
        or anchor_contract.validate_anchored_package_verification_v01(
            verification,
            anchor_publication=publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=contents,
            supplied_anchor_publication_id=expected_anchor_id,
        )
        or replay_contract.validate_sealed_replay_evidence_v01(
            replay,
            source_manifest=manifest,
            source_domain_projection=domain_projection,
            source_safe_file_contents=contents,
            anchor_publication=publication,
            anchored_verification=verification,
            supplied_anchor_publication_id=expected_anchor_id,
            reconstructed_manifest=reconstructed,
            reconstructed_domain_projection=domain_projection,
            reconstructed_safe_file_contents=contents,
        )
        or publication.anchor_publication_id != expected_anchor_id
        or publication.anchor_status != "EVIDENCE_ONLY"
        or verification.anchored_verification_id != expected_verification_id
        or verification.verification_status != "ANCHORED_PASS"
        or replay.replay_id != expected_replay_id
        or replay.replay_status != STATUS_PASS
        or replay_plain.get("fixture_disposable") is not False
    ):
        raise ValueError("cross_domain_replay_chain_invalid")


def _validate_airline(sources: LoadedCrossDomainSourcesV01) -> tuple[object, ...]:
    root = sources.repository_root
    package_root = root / "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01"
    index, adapter_result, projection, manifest, contents = airline_binding.load_airline_a2_official_package_v01(
        package_root=package_root,
        package_index_path=root / SOURCE_REFS["airline_package_index"],
    )
    safe_report = strict_json_bytes_v01(sources.named("airline_safe_report").content)
    replay_plain = strict_json_bytes_v01(sources.named("airline_replay").content)
    if (
        index.index_id != AIRLINE_PACKAGE_INDEX_ID
        or manifest.manifest_id != AIRLINE_MANIFEST_ID
        or manifest.package_content_hash != AIRLINE_PACKAGE_CONTENT_HASH
        or contents[0] != sources.named("airline_safe_report").content
        or len(safe_report.get("actors", ())) != 12
        or tuple(item.get("validation_status") for item in safe_report["actors"]) != (STATUS_PASS,) * 12
        or len(safe_report.get("root_finals", ())) != 3
        or len(safe_report.get("receipts", ())) != 3
        or safe_report.get("real_world_effects_count") != 0
        or safe_report.get("counters") != {"gemini_call_count": 12, "network_call_count": 12, "provider_call_count": 12}
        or airline_binding.validate_airline_a2_typed_context_v01(strict_json_bytes_v01(contents[2]))
    ):
        raise ValueError("cross_domain_airline_invalid")
    _validate_replay_chain(
        manifest=manifest,
        domain_projection=projection,
        contents=contents,
        anchor_plain=strict_json_bytes_v01(sources.named("airline_anchor").content),
        replay_plain=replay_plain,
        expected_anchor_id=AIRLINE_ANCHOR_ID,
        expected_verification_id=AIRLINE_VERIFICATION_ID,
        expected_replay_id=AIRLINE_REPLAY_ID,
    )
    story = _strict_public_text(sources.named("airline_human_story").content)
    required = ("12 live LLM calls", "3 sovereign Roots", "1 Corridor", "3 evidence-only receipts", "ANCHORED_PASS", "Replay closed with `PASS`", "0 real-world effects")
    if any(item not in story for item in required) or adapter_result.domain_projection != projection:
        raise ValueError("cross_domain_airline_story_invalid")
    return index, adapter_result, projection, manifest, contents


def _supplier_safe_index_expected(
    *,
    source: object,
    s2_result: object,
    rows: tuple[dict[str, object], ...],
    kernel: object,
    adapter_result: object,
) -> dict[str, object]:
    return {
        "accepted_s1": {
            "report_sha256": SUPPLIER_S1_SHA256,
            "result_id": source.result.result_id,
            "safe_execution_id": source.safe_execution.safe_execution_id,
        },
        "accepted_s2": {"evidence_sha256": SUPPLIER_S2_SHA256, "result_id": s2_result.result_id},
        "adapter_result_id": adapter_result.adapter_result_id,
        "business_boundaries": {
            "business_outcome": "MIXED",
            "real_payment_executed": False,
            "real_shipment_released": False,
            "receipt_status": "EVIDENCE_ONLY",
            "shipment_status": "HELD",
            "supplier_b_status": "BLOCKED",
        },
        "domain_id": "supplier_water_filter",
        "domain_projection_id": adapter_result.domain_projection.projection_id,
        "external_operation_counts": {"gemini": 0, "network": 0, "provider": 0, "real_world_effects": 0},
        "index_id": SUPPLIER_SAFE_EVIDENCE_INDEX_ID,
        "index_version": "v0.1",
        "kernel_adapter_id": kernel.adapter_id,
        "kernel_manifest_hash": kernel.kernel_manifest.manifest_hash,
        "programme_id": PROGRAMME_ID,
        "safe_execution_id": source.safe_execution.safe_execution_id,
        "scenario_index_id": adapter_result.scenario_index_id,
        "scenario_rows": list(rows),
        "source_call_geometry": {
            "accepted_s1_gemini": 6,
            "accepted_s1_network": 6,
            "accepted_s1_provider": 6,
            "s2_gemini": 0,
            "s2_network": 0,
            "s2_provider": 0,
        },
        "source_record_ids": [item.source_record_id for item in adapter_result.domain_projection.source_records],
        "status": STATUS_PASS,
        "validation_errors": [],
    }


def _validate_supplier(sources: LoadedCrossDomainSourcesV01) -> tuple[object, ...]:
    source = supplier_s2.load_accepted_supplier_s1_source_v01(str(sources.repository_root / SOURCE_REFS["supplier_s1_report"]))
    s2_result = supplier_s2.build_supplier_water_filter_negative_matrix_v01(source)
    if supplier_s2.validate_supplier_water_filter_negative_matrix_v01(s2_result, source):
        raise ValueError("cross_domain_supplier_s2_invalid")
    if canonical_json_line_v01(supplier_s2.supplier_water_filter_negative_matrix_to_plain_dict_v01(s2_result, source)) != sources.named("supplier_s2_evidence").content:
        raise ValueError("cross_domain_supplier_s2_invalid")
    rows = supplier_s2.supplier_water_filter_negative_matrix_package_rows_v01(s2_result, source)
    product_trace = product_trace_runner.collect_full_wow_v1_2_product_trace()
    kernel = supplier_kernel.build_supplier_water_filter_kernel_adapter_result_v01(source_report=product_trace)
    if supplier_kernel.validate_supplier_water_filter_kernel_adapter_result_v01(source_report=product_trace, result=kernel):
        raise ValueError("cross_domain_supplier_kernel_invalid")
    adapter_result = supplier_adapter.build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
        safe_execution=source.safe_execution,
        scenario_rows=rows,
        source_report=product_trace,
        kernel_adapter_result=kernel,
    )
    if supplier_adapter.validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01(
        adapter_result,
        safe_execution=source.safe_execution,
        scenario_rows=rows,
        source_report=product_trace,
        kernel_adapter_result=kernel,
    ) or adapter_result.adapter_result_id != SUPPLIER_ADAPTER_ID or adapter_result.scenario_index_id != SUPPLIER_SCENARIO_INDEX_ID:
        raise ValueError("cross_domain_supplier_adapter_invalid")
    safe_index_plain = strict_json_bytes_v01(sources.named("supplier_safe_evidence_index").content)
    if _canonical_bytes(safe_index_plain) != _canonical_bytes(
        _supplier_safe_index_expected(
            source=source,
            s2_result=s2_result,
            rows=rows,
            kernel=kernel,
            adapter_result=adapter_result,
        )
    ):
        raise ValueError("cross_domain_supplier_safe_index_invalid")
    member = sources.named("supplier_member_01").content
    if member != sources.named("supplier_safe_evidence_index").content:
        raise ValueError("cross_domain_supplier_member_invalid")
    safe_record = package_contract.build_safe_file_record_v01(
        logical_path="evidence/01-supplier-safe-evidence-index-v01.json",
        media_type="application/json",
        content_bytes=member,
        evidence_class="EXECUTED_DETERMINISTIC_RUNTIME",
        source_record_ids=tuple(item.source_record_id for item in adapter_result.domain_projection.source_records),
        terminal_newline_required=True,
        secret_scan_passed=True,
    )
    manifest = _hydrate(package_contract.SealedPackageManifestV01, strict_json_bytes_v01(sources.named("supplier_manifest").content))
    contents = (member,)
    if manifest.safe_file_records != (safe_record,) or package_contract.validate_sealed_package_manifest_v01(manifest, domain_projection=adapter_result.domain_projection, safe_file_contents=contents):
        raise ValueError("cross_domain_supplier_manifest_invalid")
    package_index = strict_json_bytes_v01(sources.named("supplier_package_index").content)
    expected_package_keys = {
        "accepted_s1_report_sha256", "accepted_s2_evidence_sha256", "adapter_result_id", "domain_id",
        "domain_projection_id", "index_id", "index_version", "manifest_byte_count", "manifest_id", "manifest_sha256",
        "package_content_hash", "package_root", "package_status", "programme_id", "publication_base_head",
        "safe_evidence_index", "safe_file_records", "scenario_index_id", "validation_errors",
    }
    if (
        set(package_index) != expected_package_keys
        or package_index["index_id"] != SUPPLIER_PACKAGE_INDEX_ID
        or package_index["manifest_id"] != SUPPLIER_MANIFEST_ID
        or package_index["package_content_hash"] != SUPPLIER_PACKAGE_CONTENT_HASH
        or package_index["manifest_sha256"] != sources.named("supplier_manifest").sha256
        or package_index["manifest_byte_count"] != sources.named("supplier_manifest").byte_count
        or _canonical_bytes(package_index["safe_file_records"])
        != _canonical_bytes([asdict(safe_record)])
        or package_index["safe_evidence_index"] != {
            "byte_count": len(member),
            "content_sha256": hashlib.sha256(member).hexdigest(),
            "index_id": SUPPLIER_SAFE_EVIDENCE_INDEX_ID,
            "repository_relative_path": SOURCE_REFS["supplier_safe_evidence_index"],
        }
        or package_index["package_status"] != "SELF_CONSISTENT_UNANCHORED"
        or package_index["validation_errors"] != []
    ):
        raise ValueError("cross_domain_supplier_package_index_invalid")
    replay_plain = strict_json_bytes_v01(sources.named("supplier_replay").content)
    _validate_replay_chain(
        manifest=manifest,
        domain_projection=adapter_result.domain_projection,
        contents=contents,
        anchor_plain=strict_json_bytes_v01(sources.named("supplier_anchor").content),
        replay_plain=replay_plain,
        expected_anchor_id=SUPPLIER_ANCHOR_ID,
        expected_verification_id=SUPPLIER_VERIFICATION_ID,
        expected_replay_id=SUPPLIER_REPLAY_ID,
    )
    story = _strict_public_text(sources.named("supplier_human_story").content)
    if any(summary not in story for summary in source.result.actor_safe_summaries) or any(f"### {scenario_id}:" not in story for scenario_id in supplier_adapter.SCENARIO_IDS):
        raise ValueError("cross_domain_supplier_story_invalid")
    required = ("Supplier B remained `BLOCKED`", "shipment remained `HELD`", "receipt remained `EVIDENCE_ONLY`", "business outcome remained `MIXED`", "ANCHORED_PASS", "0 real-world effects")
    if any(item not in story for item in required):
        raise ValueError("cross_domain_supplier_story_invalid")
    return source, s2_result, kernel, adapter_result, manifest, contents


def _file_bindings(sources: LoadedCrossDomainSourcesV01, prefix: str) -> tuple[EvidenceFileBindingV01, ...]:
    return tuple(
        EvidenceFileBindingV01(item.repository_relative_path, item.sha256, item.byte_count, f"{item.mode:04o}")
        for item in sources.snapshots
        if item.logical_name.startswith(prefix)
    )


def _claim(
    claim_id: str,
    text: str,
    scope: str,
    refs: tuple[str, ...],
    bindings: tuple[str, ...],
    limitations: tuple[str, ...] = (),
    nonclaims: tuple[str, ...] = (),
) -> ClaimEvidenceRowV01:
    return ClaimEvidenceRowV01(claim_id, text, scope, refs, bindings, STATUS_PASS, limitations, nonclaims)


def build_two_domain_cross_domain_evidence_index_v01(
    sources: LoadedCrossDomainSourcesV01,
) -> CrossDomainEvidenceIndexV01:
    airline_index, airline_adapter, airline_projection, airline_manifest, _ = _validate_airline(sources)
    supplier_source, supplier_matrix, _, supplier_adapter_result, supplier_manifest, _ = _validate_supplier(sources)
    airline_refs = tuple(item.repository_relative_path for item in sources.snapshots if item.logical_name.startswith("airline_"))
    supplier_refs = tuple(item.repository_relative_path for item in sources.snapshots if item.logical_name.startswith("supplier_"))
    airline = DomainEvidenceRecordV01(
        domain_id="airline",
        source_heads=(
            IdentityBindingV01("source_execution_head", "71764c8b41f26e94b9cfdc1e821f7d8e15df4149"),
            IdentityBindingV01("p1_publication_head", "6bf4b837e21be34a8828b5a8a1eb987cf945f839"),
            IdentityBindingV01("p2_closure_head", "4024ee41fb37452456eae991cf1ade6e6af5c43b"),
        ),
        evidence_files=_file_bindings(sources, "airline_"),
        identities=(
            IdentityBindingV01("accepted_safe_report_sha256", AIRLINE_SAFE_REPORT_SHA256),
            IdentityBindingV01("package_index_id", AIRLINE_PACKAGE_INDEX_ID),
            IdentityBindingV01("manifest_id", AIRLINE_MANIFEST_ID),
            IdentityBindingV01("package_content_hash", AIRLINE_PACKAGE_CONTENT_HASH),
            IdentityBindingV01("anchor_publication_id", AIRLINE_ANCHOR_ID),
            IdentityBindingV01("anchored_verification_id", AIRLINE_VERIFICATION_ID),
            IdentityBindingV01("replay_id", AIRLINE_REPLAY_ID),
            IdentityBindingV01("adapter_result_id", airline_adapter.adapter_result_id),
            IdentityBindingV01("domain_projection_id", airline_projection.projection_id),
        ),
        public_call_geometry=(
            GeometryFactV01("live_llm_calls", "12"), GeometryFactV01("local_validation_pass_results", "12"),
            GeometryFactV01("provider_network_gemini", "12/12/12"), GeometryFactV01("publication_and_replay_provider_network_gemini", "0/0/0"),
        ),
        root_corridor_receipt_geometry=(
            GeometryFactV01("independent_root_decisions", "3"), GeometryFactV01("corridor_count", "1"), GeometryFactV01("evidence_receipt_count", "3"),
        ),
        outcome_and_effect_boundaries=(
            GeometryFactV01("transaction_evidence_status", "PASS"), GeometryFactV01("anchor_status", "EVIDENCE_ONLY"),
            GeometryFactV01("anchored_verification_status", "ANCHORED_PASS"), GeometryFactV01("replay_status", "PASS"),
            GeometryFactV01("real_world_effects", "0"),
        ),
        evidence_refs=airline_refs,
    )
    supplier = DomainEvidenceRecordV01(
        domain_id="supplier_water_filter",
        source_heads=(
            IdentityBindingV01("s1_implementation_head", "e1fe7bfc44fe482814b1957840b6d8c434cad5c6"),
            IdentityBindingV01("s2_closure_head", "a092622d3b7028e3bdd79025c9194c3680175a5a"),
            IdentityBindingV01("p1_publication_head", "c4d853392bd1bf7efaf236be63d63cf6b7c9cfbe"),
            IdentityBindingV01("p2_closure_head", "fd745d5499aa58c1fdd070297ae27f91146e933a"),
        ),
        evidence_files=_file_bindings(sources, "supplier_"),
        identities=(
            IdentityBindingV01("accepted_s1_report_sha256", SUPPLIER_S1_SHA256), IdentityBindingV01("accepted_s2_evidence_sha256", SUPPLIER_S2_SHA256),
            IdentityBindingV01("safe_evidence_index_id", SUPPLIER_SAFE_EVIDENCE_INDEX_ID), IdentityBindingV01("safe_package_index_id", SUPPLIER_PACKAGE_INDEX_ID),
            IdentityBindingV01("manifest_id", SUPPLIER_MANIFEST_ID), IdentityBindingV01("package_content_hash", SUPPLIER_PACKAGE_CONTENT_HASH),
            IdentityBindingV01("anchor_publication_id", SUPPLIER_ANCHOR_ID), IdentityBindingV01("anchored_verification_id", SUPPLIER_VERIFICATION_ID),
            IdentityBindingV01("replay_id", SUPPLIER_REPLAY_ID), IdentityBindingV01("adapter_result_id", supplier_adapter_result.adapter_result_id),
            IdentityBindingV01("scenario_index_id", supplier_adapter_result.scenario_index_id), IdentityBindingV01("domain_projection_id", supplier_adapter_result.domain_projection.projection_id),
        ),
        public_call_geometry=(
            GeometryFactV01("live_llm_calls", "6"), GeometryFactV01("accepted_local_semantic_validations", "6"),
            GeometryFactV01("accepted_s1_provider_network_gemini", "6/6/6"), GeometryFactV01("s2_s3_provider_network_gemini_effects", "0/0/0/0"),
            GeometryFactV01("scenario_count", "9"), GeometryFactV01("preserved_s1_scenarios", "5"), GeometryFactV01("validated_negative_scenarios", "4"),
        ),
        root_corridor_receipt_geometry=(
            GeometryFactV01("scenario_order", "S-N1,S-N2,S-C1,S-P1,S-P2,S-F1,S-F2,S-F3,S-M1"),
            GeometryFactV01("supplier_a_scope", "limited_mock_path_only"), GeometryFactV01("receipt_status", "EVIDENCE_ONLY"),
        ),
        outcome_and_effect_boundaries=(
            GeometryFactV01("business_outcome", "MIXED"),
            GeometryFactV01("supplier_b_status", supplier_matrix.supplier_b_status), GeometryFactV01("shipment_status", supplier_matrix.shipment_status),
            GeometryFactV01("anchor_status", "EVIDENCE_ONLY"), GeometryFactV01("anchored_verification_status", "ANCHORED_PASS"),
            GeometryFactV01("replay_status", "PASS"), GeometryFactV01("real_world_effects", "0"),
        ),
        evidence_refs=supplier_refs,
    )
    matrix = (
        _claim("X1-A01", "Airline used 12 live semantic actors, 12 local PASS results, three independent Root decisions, one Corridor, and three evidence-only receipts.", "airline", (SOURCE_REFS["airline_safe_report"], SOURCE_REFS["airline_human_story"]), (AIRLINE_SAFE_REPORT_SHA256, AIRLINE_STORY_SHA256), ("bounded mock-only transaction evidence",), ("no real payment, booking, or ticket" ,)),
        _claim("X1-A02", "Airline LLM output influenced semantic selection and routing only; it created no authority, permission, payment, booking, or ticket.", "airline", (SOURCE_REFS["airline_safe_report"], SOURCE_REFS["airline_human_story"]), (AIRLINE_SAFE_REPORT_SHA256,), ("semantic proposals are advisory",), ("not proof of semantic truth",)),
        _claim("X1-A03", "Airline Package, EVIDENCE_ONLY Anchor, ANCHORED_PASS verification, and offline Replay form one immutable PASS chain.", "airline", (SOURCE_REFS["airline_manifest"], SOURCE_REFS["airline_anchor"], SOURCE_REFS["airline_replay"]), (AIRLINE_MANIFEST_ID, AIRLINE_PACKAGE_CONTENT_HASH, AIRLINE_ANCHOR_ID, AIRLINE_VERIFICATION_ID, AIRLINE_REPLAY_ID)),
        _claim("X1-S01", "Supplier used six live semantic actors and six accepted local semantic validations, then preserved nine scenarios with five S1 and four negative rows.", "supplier_water_filter", (SOURCE_REFS["supplier_s1_report"], SOURCE_REFS["supplier_s2_evidence"]), (SUPPLIER_S1_SHA256, SUPPLIER_S2_SHA256, supplier_matrix.result_id)),
        _claim("X1-S02", "Supplier A remained limited to the mock path; Supplier B stayed BLOCKED, shipment HELD, receipt EVIDENCE_ONLY, and the business outcome MIXED.", "supplier_water_filter", (SOURCE_REFS["supplier_safe_evidence_index"], SOURCE_REFS["supplier_human_story"]), (SUPPLIER_SAFE_EVIDENCE_INDEX_ID, SUPPLIER_STORY_SHA256), ("bounded Supplier A mock path only",), ("not complete business acceptance",)),
        _claim("X1-S03", "Supplier Package, EVIDENCE_ONLY Anchor, ANCHORED_PASS verification, and offline Replay form one immutable PASS chain.", "supplier_water_filter", (SOURCE_REFS["supplier_manifest"], SOURCE_REFS["supplier_anchor"], SOURCE_REFS["supplier_replay"]), (SUPPLIER_MANIFEST_ID, SUPPLIER_PACKAGE_CONTENT_HASH, SUPPLIER_ANCHOR_ID, SUPPLIER_VERIFICATION_ID, SUPPLIER_REPLAY_ID)),
        _claim("X1-C01", "Across both domains LLM semantics remained advisory evidence and Root retained authority.", "cross_domain", (SOURCE_REFS["airline_human_story"], SOURCE_REFS["supplier_human_story"]), (AIRLINE_STORY_SHA256, SUPPLIER_STORY_SHA256), (), ("semantic evidence is not permission or action",)),
        _claim("X1-C02", "Local validation preceded Root acceptance and every Corridor remained bounded by Root-created scope.", "cross_domain", (SOURCE_REFS["airline_safe_report"], SOURCE_REFS["supplier_s2_evidence"]), (AIRLINE_SAFE_REPORT_SHA256, SUPPLIER_S2_SHA256)),
        _claim("X1-C03", "Receipts remained evidence rather than authority in both domains.", "cross_domain", (SOURCE_REFS["airline_human_story"], SOURCE_REFS["supplier_human_story"]), (AIRLINE_STORY_SHA256, SUPPLIER_STORY_SHA256), (), ("receipts do not authorize future action",)),
        _claim("X1-C04", "Package bytes froze before Anchor, Anchor bytes froze before Replay, and Replay was offline with no action or effect.", "cross_domain", (SOURCE_REFS["airline_replay_audit"], SOURCE_REFS["supplier_replay_audit"]), (EXPECTED_HASHES["airline_replay_audit"], EXPECTED_HASHES["supplier_replay_audit"])),
        _claim("X1-C05", "Raw prompts, raw provider responses, credentials, and private attempts remained unpublished.", "cross_domain", (SOURCE_REFS["airline_replay_audit"], SOURCE_REFS["supplier_replay_audit"]), (EXPECTED_HASHES["airline_replay_audit"], EXPECTED_HASHES["supplier_replay_audit"]), (), ("no private source publication",)),
        _claim("X1-C06", "Airline and Supplier have distinct Package, Anchor, anchored-verification, and Replay identities.", "cross_domain", (SOURCE_REFS["airline_replay"], SOURCE_REFS["supplier_replay"]), (AIRLINE_MANIFEST_ID, SUPPLIER_MANIFEST_ID, AIRLINE_ANCHOR_ID, SUPPLIER_ANCHOR_ID, AIRLINE_REPLAY_ID, SUPPLIER_REPLAY_ID)),
        _claim("X1-C07", "Different actor counts and business outcomes do not change the shared authority law.", "cross_domain", (SOURCE_REFS["airline_human_story"], SOURCE_REFS["supplier_human_story"]), ("airline:12:PASS", "supplier:6:MIXED"), ("domain results remain distinct",), ("not arbitrary-domain certification",)),
    )
    provisional = CrossDomainEvidenceIndexV01(
        index_id="0" * 64,
        index_version=INDEX_VERSION,
        programme_id=PROGRAMME_ID,
        gate_id=GATE_ID,
        execution_head=EXPECTED_HEAD,
        airline=airline,
        supplier_water_filter=supplier,
        claim_evidence_matrix=matrix,
        differences=(
            "12 versus 6 live LLM actors", "Airline transaction versus Supplier Water Filter workflow",
            "three-party purchase versus supplier, warehouse, and payment review", "Airline PASS transaction evidence versus Supplier MIXED business outcome",
            "Airline offers and ticket rules versus Supplier invoices, legal evidence, and warehouse blockers",
        ),
        unchanged_authority_laws=(
            "Root authority", "semantic meaning is separated from executable action", "local validators precede acceptance",
            "Corridor scope is bounded", "receipts are evidence only", "real-world effects remain zero", "Package, Anchor, and Replay are immutable and offline",
        ),
        required_non_claims=(
            "not production", "not production certification", "not arbitrary-domain certification",
            "not a real Airline, bank, supplier, warehouse, GDS, booking, ticket, payment, or shipment integration",
            "not production PKI or Root Attestation", "not proof of semantic truth", "not proof that the external world changed",
        ),
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
        validation_errors=(),
        final_status=STATUS_PASS,
    )
    result = replace(provisional, index_id=_identity(provisional))
    if _cross_domain_result_structure_errors(result, sources):
        raise ValueError("cross_domain_result_invalid")
    return result


def _cross_domain_result_structure_errors(
    result: object,
    sources: LoadedCrossDomainSourcesV01,
) -> tuple[str, ...]:
    if type(result) is not CrossDomainEvidenceIndexV01 or type(sources) is not LoadedCrossDomainSourcesV01:
        return ("cross_domain_result_invalid",)
    try:
        errors: list[str] = []
        if result.index_id != _identity(result) or _SHA256.fullmatch(result.index_id) is None:
            errors.append("cross_domain_index_identity_invalid")
        if (result.index_version, result.programme_id, result.gate_id, result.execution_head, result.final_status, result.validation_errors) != (
            INDEX_VERSION, PROGRAMME_ID, GATE_ID, EXPECTED_HEAD, STATUS_PASS, (),
        ):
            errors.append("cross_domain_result_invalid")
        if any(type(value) is not int or value != 0 for value in (result.provider_call_count, result.network_call_count, result.gemini_call_count, result.real_world_effects_count)):
            errors.append("cross_domain_operation_count_invalid")
        if tuple(item.claim_id for item in result.claim_evidence_matrix) != tuple(f"X1-{group}{number:02d}" for group, number in (("A",1),("A",2),("A",3),("S",1),("S",2),("S",3),("C",1),("C",2),("C",3),("C",4),("C",5),("C",6),("C",7))):
            errors.append("cross_domain_claim_geometry_invalid")
        all_refs = {item.repository_relative_path for item in sources.snapshots}
        if any(item.validation_status != STATUS_PASS or not item.evidence_refs or not set(item.evidence_refs).issubset(all_refs) for item in result.claim_evidence_matrix):
            errors.append("cross_domain_claim_evidence_invalid")
        if result.airline.domain_id != "airline" or result.supplier_water_filter.domain_id != "supplier_water_filter":
            errors.append("cross_domain_domain_binding_invalid")
        if result.airline.identities == result.supplier_water_filter.identities:
            errors.append("cross_domain_identity_separation_invalid")
        if "MIXED" not in tuple(item.fact_value for item in result.supplier_water_filter.outcome_and_effect_boundaries):
            errors.append("cross_domain_supplier_outcome_invalid")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("cross_domain_result_invalid",)


def validate_two_domain_cross_domain_evidence_index_v01(
    result: object,
    sources: LoadedCrossDomainSourcesV01,
) -> tuple[str, ...]:
    errors = list(_cross_domain_result_structure_errors(result, sources))
    if errors or type(result) is not CrossDomainEvidenceIndexV01:
        return tuple(dict.fromkeys(errors or ["cross_domain_result_invalid"]))
    try:
        expected = build_two_domain_cross_domain_evidence_index_v01(sources)
        if _canonical_bytes(_plain(result)) != _canonical_bytes(_plain(expected)):
            errors.append("cross_domain_context_mismatch")
            if result.index_id != expected.index_id:
                errors.append("cross_domain_index_identity_invalid")
    except Exception:
        errors.append("cross_domain_result_invalid")
    return tuple(dict.fromkeys(errors))


def cross_domain_evidence_index_to_plain_dict_v01(
    result: CrossDomainEvidenceIndexV01,
    sources: LoadedCrossDomainSourcesV01,
) -> dict[str, object]:
    if validate_two_domain_cross_domain_evidence_index_v01(result, sources):
        raise ValueError("cross_domain_result_invalid")
    plain = _plain(result)
    canonical_json_line_v01(plain)
    return plain


def load_cross_domain_evidence_index_v01(
    content: bytes,
    sources: LoadedCrossDomainSourcesV01,
) -> CrossDomainEvidenceIndexV01:
    plain = strict_json_bytes_v01(content)
    result = _hydrate(CrossDomainEvidenceIndexV01, plain)
    if validate_two_domain_cross_domain_evidence_index_v01(result, sources):
        raise ValueError("cross_domain_result_invalid")
    return result


def _write_all(descriptor: int, content: bytes) -> None:
    offset = 0
    while offset < len(content):
        written = os.write(descriptor, content[offset:])
        if written <= 0:
            raise OSError
        offset += written


def _cleanup_owned(parent_fd: int, leaf: str, identity: tuple[int, int]) -> None:
    try:
        entry = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if stat.S_ISREG(entry.st_mode) and (entry.st_dev, entry.st_ino) == identity:
        os.unlink(leaf, dir_fd=parent_fd)
        os.fsync(parent_fd)


def write_cross_domain_evidence_index_v01(output: Path, content: bytes) -> None:
    parent_fd = _open_root(output.parent)
    descriptor = -1
    identity: tuple[int, int] | None = None
    try:
        descriptor = os.open(
            output.name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o400,
            dir_fd=parent_fd,
        )
        created = os.fstat(descriptor)
        identity = (created.st_dev, created.st_ino)
        os.fchmod(descriptor, 0o400)
        _write_all(descriptor, content)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.fsync(parent_fd)
        check_fd = os.open(output.name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        try:
            check = os.fstat(check_fd)
            reread = b""
            while True:
                chunk = os.read(check_fd, 65536)
                if not chunk:
                    break
                reread += chunk
            entry = os.stat(output.name, dir_fd=parent_fd, follow_symlinks=False)
            if (
                not stat.S_ISREG(check.st_mode)
                or (check.st_dev, check.st_ino) != identity
                or (entry.st_dev, entry.st_ino) != identity
                or stat.S_IMODE(check.st_mode) != 0o400
                or reread != content
            ):
                raise OSError
        finally:
            os.close(check_fd)
    except Exception:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if identity is not None:
            _cleanup_owned(parent_fd, output.name, identity)
        raise ValueError("cross_domain_output_write_failed") from None
    finally:
        os.close(parent_fd)


def _duplicate_options(argv: tuple[str, ...]) -> bool:
    seen: set[str] = set()
    for token in argv:
        if token.startswith("--"):
            option = token.split("=", 1)[0]
            if option in seen:
                return True
            seen.add(option)
    return False


class _StrictArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError("cross_domain_cli_invalid")


def _parser() -> argparse.ArgumentParser:
    parser = _StrictArgumentParser(allow_abbrev=False)
    parser.add_argument("--repository-root", required=True)
    for name in SOURCE_REFS:
        parser.add_argument("--" + name.replace("_", "-"), required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    values = tuple(sys.argv[1:] if argv is None else argv)
    try:
        if _duplicate_options(values):
            raise ValueError
        args = _parser().parse_args(values)
        root = Path(args.repository_root)
        if not root.is_absolute():
            raise ValueError
        refs = {name: getattr(args, name) for name in SOURCE_REFS}
        output_ref = args.output
        if output_ref != CANONICAL_OUTPUT_REF or not _valid_ref(output_ref):
            raise ValueError
        output = root / output_ref
        if output.exists() or output.is_symlink():
            raise ValueError
        sources = load_cross_domain_sources_v01(repository_root=root, source_refs=refs)
        result = build_two_domain_cross_domain_evidence_index_v01(sources)
        plain = cross_domain_evidence_index_to_plain_dict_v01(result, sources)
        content = canonical_json_line_v01(plain)
        verify_source_continuity_v01(sources)
        write_cross_domain_evidence_index_v01(output, content)
        root_fd = _open_root(root)
        try:
            output_snapshot = _read_ref(root_fd, "x1_output", output_ref)
        finally:
            os.close(root_fd)
        if output_snapshot.mode != 0o400:
            raise ValueError
        loaded = load_cross_domain_evidence_index_v01(output_snapshot.content, sources)
        verify_source_continuity_v01(sources)
        if loaded != result:
            raise ValueError
        print(json.dumps({"final_status": STATUS_PASS, "index_id": result.index_id, "provider_network_gemini_effects": "0/0/0/0"}, sort_keys=True, separators=(",", ":")))
        return 0
    except (SystemExit, Exception):
        print('{"final_status":"FAIL_CLOSED","reason":"cross_domain_audit_failed"}')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
