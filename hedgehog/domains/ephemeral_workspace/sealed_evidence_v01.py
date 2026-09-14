"""Public-safe evidence adapter for the frozen EWS3R2 run.

Only public offline validators are called. Historical graph checks stay inside the
private input boundary. Public replay checks sixteen derived evidence objects,
not hidden native payloads, semantic truth, or a live Host's authority.
"""
from __future__ import annotations

import hashlib
import ast
import json
import re
import stat
import unicodedata
from functools import wraps
from pathlib import Path, PurePosixPath

from hedgehog import context_packets as context_packets
from hedgehog import structured_rationale as rationale
from hedgehog import semantic_reasoning_adapter as semantic
from hedgehog.kernel import execution_mode_router_v01 as router
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.evidence import sealed_evidence_profile_v01 as profile
from hedgehog.evidence import sealed_package_v01 as package
from hedgehog.evidence import external_anchor_v01 as anchor
from hedgehog.evidence import sealed_replay_evidence_v01 as replay


INPUT_ARCHIVE = "RADIOLARIA_EPHEMERAL_WORKSPACE_EWS3R2_TEMPORAL_BROWSER_RETURN_20260914T112116Z.tar.gz"
INPUT_ARCHIVE_SHA256 = "5d6c1e7aa4bf1abbe3b2ff629ec36d85d7c2fc9bcf10cc088e87328b463992b5"
INPUT_MANIFEST_SHA256 = "a03e173e1866907a0a57c502849cc596886f44af3056e26221ac8eaed3948862"
EXECUTION_HEAD = "e42d37fa98dfec7110b8cf75b1aceaa614f461be"
RUNTIME_SHA256 = "d3841d5f6faa4dd9e8c9db6373658366d1cc89ae54b0826351de64095276c5cc"
SIDECAR_SHA256 = "20e01b3ebd6f813bccf2ce51d23c71406a0f2b2cd706ab8bda92e71bed28a915"
BSEP_SOURCE_FILE = "browser_run_01/native_common_return/D_baseline.json"
BSEP_SOURCE_SHA256 = "67eff98a00873b68690ce691d9a7b5145bbf7f8802c82e2251b852b79e597d32"
BSEP_NATIVE_SHA256 = "247912e13f057e147104d60a660f24f548f7f965a2329eefc5b6282d399c3ed1"
BSEP_PACKET_POINTER = "/source_context/g2c_source_context/bsep_packet"
BSEP_BINDING_POINTER = "/source_context/router_input/bsep_binding"
_BSEP_TRUE_FLAGS = (
    "BoundedSemanticEvidencePacket is not ActionCommitPacket",
    "BoundedSemanticEvidencePacket is not FinalOutput",
    "BoundedSemanticEvidencePacket is not authority",
    "BoundedSemanticEvidencePacket is not truth", "ContextPacket is not authority",
    "ContextPacket is not truth", "Evidence packet is not action permission",
    "Gemini proposes, Root disposes", "Root remains final authority",
    "root_final_authority_preserved",
)
_BSEP_FALSE_FLAGS = (
    "action_commit_packet_claimed", "action_permission_claimed", "authority_claimed",
    "connector_command_claimed", "drs_write_claimed", "final_output_claimed",
    "raw_cross_role_text_included", "raw_user_text_included", "real_world_effects_allowed",
    "root_bypass_claimed", "truth_claimed",
)
_BSEP_VALIDATOR_PINS = {
    "hedgehog/context_packets.py": "080c69dfe24206549fbf27ae65141105c6e4b4c802b05296f1d90026823e9f32",
    "hedgehog/structured_rationale.py": "05686cd42bc4ea0bd9b0bc2586c7df6fd51369d43ee0fb15af4c95326e3d1f03",
    "hedgehog/semantic_reasoning_adapter.py": "3900b23d3f15ee42b21b7f28895e1badf6639d56a98ce3fcbe5a9f9c072009f6",
    "hedgehog/kernel/execution_mode_router_v01.py": "4b19de7348a15cd65f1bed02bd93d848ccc490b6c7b8fe21338c3784809f79c4",
}
_EWS4R_MUTABLE_PATHS = frozenset((
    "hedgehog/domains/ephemeral_workspace/sealed_evidence_v01.py",
    "demo/run_ephemeral_workspace_evidence_v01.py",
    "tests/test_ephemeral_workspace_evidence_v01.py",
    "tests/test_ephemeral_workspace_adversarial_v01.py",
    "docs/demo_designs/ephemeral_workspace_v01.md",
))
_PREDECESSOR_SOURCE_SHA256 = {'demo/ephemeral_workspace_fixtures_v01.py': '107e8ae5e05d6dc8f081faf813b43957642414299557446a6f5fe97e11fd531b',
 'demo/run_ephemeral_workspace_evidence_v01.py': '5993a35360c8333330ccc5dc330d09def89a3b8a324ff8a6366cb702ecfca32e',
 'demo/run_ephemeral_workspace_v01.py': 'efc1acbb957b1919ce421a0cae36fc9a7881a86c359ba907cd4417a54b835425',
 'docs/demo_designs/ephemeral_workspace_v01.md': '6e1bd25027d0ee9c5b44af13197a8c46fdb497f6dc516c7493ba0fc061a3f49e',
 'hedgehog/action_commit_packet_v02.py': 'e24b8c4bd3284c4b9db8944e2a9c268d26816956880ffb0700700bbf3fdc59ac',
 'hedgehog/domains/ephemeral_workspace/__init__.py': 'f1eba5acd64fe400ab325106031e2d90f963ddb2df0e33f43eb4cc0d95b00e1f',
 'hedgehog/domains/ephemeral_workspace/capability_registry_v01.py': 'c76070da03489e0e9ec8c3784f61520ef2866ebd7a5eaf6d9470e369500e11a3',
 'hedgehog/domains/ephemeral_workspace/contracts_v01.py': '9e2a69ed5c02ae9c8febfe2d3064a967598e21c61d80eecd84fd08efad093c9b',
 'hedgehog/domains/ephemeral_workspace/evidence_v01.py': '792736b91f2a3fa264613fa6bc1bea60e4370fd8ba7f56c427fc0323f39ca1c7',
 'hedgehog/domains/ephemeral_workspace/kernel_adapter_v01.py': '15f1243f5dd0d1d798267c48359622983b99387f5b15df2b081620b7516ae1ee',
 'hedgehog/domains/ephemeral_workspace/local_services_v01.py': '1abe5cd160a9ae7475334f2b396057366ab4a7c477a7ea62288c702018f1c1a3',
 'hedgehog/domains/ephemeral_workspace/media_continuation_v01.py': '8728b7a47740736bb3d7145acb874fa1e545614e4adf3d1dd94e4230ea4d0210',
 'hedgehog/domains/ephemeral_workspace/media_v01.py': '87e2388ceab077e330c144cf3d730341e5a44fdc51131d7aa0969ad490b6d7fa',
 'hedgehog/domains/ephemeral_workspace/memory_adapter_v01.py': 'ce4944c25a03ac4ca0d2d2c3eb1b3c68ac0d5f2dd012a31a7705642b4a3ba569',
 'hedgehog/domains/ephemeral_workspace/sealed_evidence_v01.py': '70493bae9b64ba226691edcfcf9c2678f643e9732716e7f4360c07750c90ffa8',
 'hedgehog/domains/ephemeral_workspace/semantic_adapter_v01.py': 'ef42d7529134d9c7f9908dac0ddb08a62d1d9d2a838b1baf38c58316b468dfce',
 'hedgehog/domains/ephemeral_workspace/semantic_roles_v01.py': '1d1e8162df04f300143659022d067941413918bd6afe9702b7a08f701a9eb56d',
 'hedgehog/domains/ephemeral_workspace/session_runtime_v01.py': 'd3841d5f6faa4dd9e8c9db6373658366d1cc89ae54b0826351de64095276c5cc',
 'hedgehog/domains/ephemeral_workspace/viewer_v01.py': 'f77077d285128bb87f237f3c376f9ebd198fff991f7814764564633cd58e0d3b',
 'hedgehog/kernel/transition_registry_v01.py': '16d2d3c31004bccc3064c74290bad4a7303669b63c428cebf6be8763574ae0ca',
 'tests/test_action_packet_validation_cost_v01.py': '61efca1fbb1a2a8f264bba59521226ddeebe69cee86f82b1cf87c4abcb6e34a7',
 'tests/test_ephemeral_workspace_evidence_v01.py': 'f95cab31a041460fe8d07c1199ef80e03f7fcff49a265eaa3fef2dc30167901a',
 'tests/test_ephemeral_workspace_ews3r_temporal_v01.py': '474e8668916913db4597bdac2a6ce6e3ad980562e1d44d4546791a0d732bb7b6',
 'tests/test_ephemeral_workspace_ews3r_v01.py': '79dee0e9392b9c4e99159eb866045e65d73424409b175c78c03309f4e3450611',
 'tests/test_ephemeral_workspace_services_v01.py': '08650b92ee6c9f0ac776c8b0e857c9988f23b8f0e3a0000d135bca006c5f8cf7',
 'tests/test_ephemeral_workspace_v01.py': '1cfddbd3c0d682b01355f76b457567e72d31229f44f98775b560d330639f1918'}

REQUIRED_DOCUMENTS = (
    "workspace_intent_v01.json", "capability_discovery_snapshot_safe_v01.json",
    "orchestrator_semantic_summary_v01.json", "bsep_safe_projection_v01.json",
    "semantic_architect_summary_v01.json", "privacy_boundary_summary_v01.json",
    "runtime_execution_topology_safe_v01.json", "workspace_lease_safe_v01.json",
    "device_grant_summary_v01.json", "session_event_summary_v01.json",
    "sidecar_write_packet_safe_v01.json", "sidecar_write_receipt_safe_v01.json",
    "teardown_summary_v01.json", "adversarial_matrix_v01.json",
    "secret_scan_v01.json", "final_safe_execution_report_v01.json",
)
INTEGRITY_FILE = "kernel_integrity_v01.json"
MANIFEST_FILE = "sealed_package_manifest_v01.json"
_ARTIFACT_FIELDS = frozenset(("abi_version", "artifact_id", "artifact_type",
    "schema_version", "transaction_id", "owner_root_id", "source_component",
    "authority_class", "lifecycle_state", "payload", "trace_refs", "parent_refs",
    "time_envelope"))
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_FORBIDDEN_KEYS = {"pid", "port", "nonce", "socket", "audio_resource",
    "raw_prompt", "raw_response", "api_key", "access_token", "bearer_token"}
_LIMITATIONS = (
    "safe_derivative_graph_only", "private_originals_not_replayed",
    "no_live_host_origin_reconstruction", "no_semantic_truth_by_hash",
    "no_new_root_authority", "independent_lead_pin_pending",
    "no_signature_signer_timestamp_or_root_attestation",
    "original_native_schema_canonical_reference_unsupported",
    "private_aggregate_integrity_is_not_original_native_manifest",
    "native_bsep_offline_dto_validation_not_live_origin_or_authority",
    "supplemental_private_proofs_validated_at_export_not_reexecuted_by_public_replay",
    "full_ews_acceptance_not_self_awarded",
)


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return integrity.canonical_json_bytes_v01(value)


def _digest(value):
    return _sha(_canonical(value))


def _pairs(rows):
    result = {}
    for key, value in rows:
        _require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def _json(data, *, canonical=False):
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite_json")))
        if canonical:
            _require(data == _canonical(value) + b"\n", "noncanonical_json_bytes")
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise ValueError("malformed_json") from None


def _safe_path(value):
    _require(type(value) is str and value and "\\" not in value
        and not value.startswith("/") and not re.match(r"^[A-Za-z]:", value), "unsafe_path")
    parts = PurePosixPath(value).parts
    _require(parts and all(p not in (".", "..", "") for p in parts)
        and str(PurePosixPath(value)) == value, "unsafe_path")
    return parts


def _read(root, logical):
    path = Path(root)
    _no_symlink_ancestors(path)
    _require(path.is_dir() and not path.is_symlink(), "input_directory_required")
    for part in _safe_path(logical):
        path = path / part
        _require(not path.is_symlink(), "symlink_rejected")
    _require(path.exists() and stat.S_ISREG(path.stat().st_mode), "regular_file_required")
    return path.read_bytes()


def _no_symlink_ancestors(path):
    for item in (Path(path), *Path(path).parents):
        _require(not item.is_symlink(), "symlink_rejected")


def _fail_closed(function):
    @wraps(function)
    def checked(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (KeyError, TypeError, IndexError, StopIteration, AttributeError) as error:
            raise ValueError("input_structure_invalid:" + type(error).__name__) from None
    return checked


def _scan(value):
    """Inspect both decoded JSON strings and nested encoded JSON strings."""
    if isinstance(value, dict):
        for key, item in value.items():
            _require(key.lower() not in _FORBIDDEN_KEYS, "private_field_rejected")
            _scan(key)
            _scan(item)
    elif isinstance(value, list):
        for item in value:
            _scan(item)
    elif isinstance(value, str):
        _require(not any("CYRILLIC" in unicodedata.name(c, "") for c in value), "cyrillic_rejected")
        _require(not any(s in value for s in ("/Users/", "/private/", "ews:session:",
            "root:ews:personal:", "Bearer ", "-----BEGIN PRIVATE", "AIza")), "private_value_rejected")
        if value.lstrip().startswith(("{", "[", '"')):
            try:
                decoded = _json(value.encode("utf-8"))
            except ValueError:
                decoded = None
            if decoded != value and decoded is not None:
                _scan(decoded)


def _artifact(row):
    _require(type(row) is dict and set(row) == _ARTIFACT_FIELDS, "artifact_fields_invalid")
    return abi.build_kernel_artifact_v01(**{
        **row, "trace_refs": tuple(row["trace_refs"]), "parent_refs": tuple(row["parent_refs"])})


def _graph(value):
    found = {}
    def visit(item):
        if isinstance(item, dict):
            if item.get("abi_version") == "v1.0" and set(item) == _ARTIFACT_FIELDS:
                key = item["artifact_id"]
                if key in found:
                    _require(found[key] == item, "native_artifact_identity_collision")
                else:
                    found[key] = item
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    return found


def _private_graph_audit(rows, source_export):
    """Validate native ABI objects unchanged, then seal one private aggregate.

    The installed ABI accepts native v0.1/v0.2 schemas, but its public
    canonical-reference converter delegates to an integrity profile supporting
    v1 only. That refusal is retained, never repaired by relabeling native IDs.
    """
    ordered = sorted(rows, key=lambda row: row["artifact_id"])
    artifacts = tuple(_artifact(row) for row in ordered)
    abi_errors = abi.validate_kernel_artifact_bundle_v01(artifacts=artifacts)
    _require(not abi_errors, "original_native_abi_bundle_invalid")
    schemas = {}
    conversion = []
    for artifact in artifacts:
        schema = artifact.schema_version
        row = schemas.setdefault(schema, {"schema_version": schema, "artifact_count": 0,
            "converted_count": 0, "unsupported_count": 0})
        row["artifact_count"] += 1
        try:
            abi.kernel_artifact_to_canonical_ref_v01(artifact)
        except ValueError as error:
            _require(str(error) == "canonical_artifact_ref_conversion_failed" and schema != "v1",
                "unexpected_native_canonical_conversion_failure")
            row["unsupported_count"] += 1
            conversion.append({"native_artifact_id_sha256": _digest(artifact.artifact_id),
                "schema_version": schema, "reason": str(error)})
        else:
            row["converted_count"] += 1
    _require(bool(conversion), "expected_native_schema_boundary_not_observed")
    payload = {"historical_native_records": ordered,
        "native_export_canonical_sha256": _digest(source_export),
        "scope": "UNCHANGED_NATIVE_RECORDS_IN_NEW_PRIVATE_EVIDENCE_AGGREGATE"}
    wrapper = abi.build_kernel_artifact_v01(abi_version="v1.0",
        artifact_id="ews4:private_graph_aggregate:" + _digest(payload),
        artifact_type="SemanticEvidence", schema_version="v1",
        transaction_id="ews4:private_historical_graph_audit",
        owner_root_id="ews4:historical_evidence_custodian", source_component="ews4_safe_export_adapter",
        authority_class="EVIDENCE_ONLY", lifecycle_state="VALIDATED", payload=payload,
        trace_refs=(INPUT_ARCHIVE_SHA256, _digest(ordered)), parent_refs=(),
        time_envelope={"ct_session_anchor": "ews4:historical_evidence", "et_observed_at": None,
            "freshness_class": "static", "kt_asof": "2026-09-14T00:00:00Z",
            "pt_created_at": "2026-09-14T00:00:00Z", "ttl_seconds": 0,
            "valid_from": None, "valid_to": None})
    manifest, _, verification = _kernel([abi.kernel_artifact_to_plain_dict_v01(wrapper)])
    return {
        "native_artifact_count": len(artifacts),
        "native_dependency_edge_count": sum(len(a.parent_refs) for a in artifacts),
        "native_abi_bundle_status": "PASS", "native_abi_bundle_errors": list(abi_errors),
        "native_records_canonical_sha256": _digest(ordered),
        "native_export_canonical_sha256": _digest(source_export),
        "native_canonical_reference_status": "UNSUPPORTED_NATIVE_SCHEMA",
        "native_manifest_reconstruction": "NOT_SUPPORTED_BY_INSTALLED_V1_INTEGRITY_PROFILE",
        "native_schema_conversion": sorted(schemas.values(), key=lambda row: row["schema_version"]),
        "native_conversion_refusals": conversion,
        "private_aggregate_wrapper_count": 1,
        "private_aggregate_artifact_id": wrapper.artifact_id,
        "private_aggregate_manifest_hash": manifest.manifest_hash,
        "private_aggregate_manifest_scope": "ONE_NEW_EVIDENCE_ONLY_WRAPPER_CONTAINING_UNCHANGED_NATIVE_GRAPH",
        "private_aggregate_seal": verification["verification"],
        "private_aggregate_replay": {k: verification["replay"][k] for k in ("replay_status", "replay_errors",
            "replay_id", "manifest_hash", "artifact_count", "dependency_edge_count", "integrity_verified", "continuity_verified")},
        "original_native_manifest_pass_claimed": False,
        "private_payload_and_original_authority_not_published": True}


def _kernel(rows):
    by_id = {r["artifact_id"]: r for r in rows}
    _require(len(by_id) == len(rows) and rows, "artifact_id_duplicate")
    ordered = []
    pending = dict(by_id)
    while pending:
        ready = sorted(k for k, r in pending.items() if all(p in {x["artifact_id"] for x in ordered} for p in r["parent_refs"]))
        _require(bool(ready), "artifact_parent_graph_unclosed_or_cyclic")
        ordered.extend(pending.pop(k) for k in ready)
    artifacts = tuple(_artifact(row) for row in ordered)
    _require(not abi.validate_kernel_artifact_bundle_v01(artifacts=artifacts), "artifact_bundle_invalid")
    refs = tuple(abi.kernel_artifact_to_canonical_ref_v01(a) for a in artifacts)
    manifest = integrity.build_artifact_manifest_v01(
        transaction_id=artifacts[0].transaction_id,
        profile=integrity.build_default_seal_profile_v01(), artifacts=refs,
        dependency_edges=tuple(integrity.ArtifactDependencyEdgeV01(a.artifact_id, p) for a in artifacts for p in a.parent_refs),
        root_ownership_bindings=tuple(integrity.RootOwnershipBindingV01(a.artifact_id, a.owner_root_id) for a in artifacts),
        evidence_class_bindings=tuple(integrity.EvidenceClassBindingV01(a.artifact_id, "EVIDENCE_ONLY") for a in artifacts),
        authority_class_bindings=tuple(integrity.AuthorityClassBindingV01(a.artifact_id, a.authority_class) for a in artifacts))
    payloads = tuple((r["artifact_id"], r["payload"]) for r in ordered)
    seal = integrity.verify_artifact_manifest_v01(manifest=manifest, payload_rows=payloads,
        expected_manifest_hash=manifest.manifest_hash)
    replayed = integrity.verify_artifact_replay_v01(manifest=manifest, payload_rows=payloads,
        expected_manifest_hash=manifest.manifest_hash)
    _require(seal.verification_status == "PASS" and replayed.replay_status == "PASS", "kernel_verification_failed")
    return manifest, refs, {
        "manifest": integrity.artifact_manifest_to_plain_dict_v01(manifest),
        "verification": integrity.seal_verification_result_to_plain_dict_v01(seal),
        "replay": integrity.replay_verification_result_to_plain_dict_v01(replayed)}


def _source_ledger(path):
    path = Path(path)
    rows = _json(_read(path.parent, path.name))
    _require(isinstance(rows, list) and len(rows) == 27, "candidate_source_ledger_scope_invalid")
    seen = set()
    for row in rows:
        _safe_path(row["path"])
        _require(row["path"] not in seen, "source_ledger_duplicate")
        seen.add(row["path"])
        data = _read(path.parent, row["source_object"])
        _require(len(data) == row["bytes"] and _sha(data) == row["sha256"], "source_object_digest_mismatch")
    expected = set(_PREDECESSOR_SOURCE_SHA256) | _EWS4R_MUTABLE_PATHS
    _require(seen == expected, "candidate_source_ledger_scope_invalid")
    for row in rows:
        if row["path"] not in _EWS4R_MUTABLE_PATHS:
            _require(row["sha256"] == _PREDECESSOR_SOURCE_SHA256[row["path"]], "frozen_predecessor_source_changed")
    _require(next(r["sha256"] for r in rows if r["path"].endswith("/session_runtime_v01.py")) == RUNTIME_SHA256,
        "accepted_runtime_source_changed")
    return _sha(_read(path.parent, path.name)), [{k: r[k] for k in ("path", "bytes", "sha256")} for r in rows]


def _private_inputs(root, expected_manifest):
    raw = _read(root, "MANIFEST.json")
    _require(_sha(raw) == INPUT_MANIFEST_SHA256 == expected_manifest, "accepted_input_manifest_mismatch")
    rows = _json(raw)
    _require(isinstance(rows, list) and len(rows) == 551, "accepted_input_manifest_scope_invalid")
    index = {}
    for row in rows:
        _safe_path(row["path"])
        _require(row["path"] not in index, "input_manifest_duplicate")
        index[row["path"]] = row
    sources = {}
    def read(logical):
        _require(logical in index, "source_not_manifest_bound")
        data = _read(root, logical)
        row = index[logical]
        _require(len(data) == row["bytes"] and _sha(data) == row["sha256"], "source_digest_mismatch")
        sources[logical] = dict(row)
        return _json(data) if logical.endswith(".json") else data
    return read, sources


def _one(rows, key, value):
    matches = [r for r in rows if r[key] == value]
    _require(len(matches) == 1, "source_reference_not_unique")
    return matches[0]


@_fail_closed
def _native_bsep_projection(base):
    """Validate the unchanged native DTO and its recorded source family offline."""
    context = base.get("source_context", {}).get("g2c_source_context", {})
    router_input = base.get("source_context", {}).get("router_input", {})
    packet = context.get("bsep_packet")
    binding = router_input.get("bsep_binding")
    _require(type(packet) is dict and type(binding) is dict,
        "native_bsep_missing_packet_or_binding")
    business = context["business_request_context_packet"]
    route = context["bsep_route_context_packet"]
    proposal = context["bsep_orchestrator_proposal"]
    structured = context["bsep_structured_rationale"]
    rv = rationale.validate_orchestrator_structured_rationale(structured)
    pv = context_packets.validate_bounded_semantic_evidence_packet(packet,
        route_context_packet=route, orchestrator_proposal=proposal,
        structured_rationale_validation=rv)
    _require(pv["accepted"] and not pv["reasons"], "native_bsep_dto_invalid")
    _require(context_packets.validate_business_request_context_packet(business)["accepted"]
        and context_packets.validate_orchestrator_route_context_packet(route)["accepted"]
        and not semantic.validate_orchestrator_semantic_reasoning_proposal(proposal)
        and rv["accepted"], "native_bsep_surrounding_source_invalid")
    try:
        typed = router.ExecutionModeBSEPBindingV01(**{
            **binding, "source_reason_codes": tuple(binding["source_reason_codes"])})
    except (TypeError, KeyError):
        raise ValueError("native_bsep_binding_mismatch") from None
    bv = router.validate_execution_mode_bsep_binding_v01(typed)
    _require(bv.validation_status == "PASS" and not bv.reason_codes,
        "native_bsep_binding_mismatch")
    family = {
        "business_request_packet_sha256": _digest(business),
        "source_route_context_sha256": _digest(route),
        "source_proposal_sha256": _digest(proposal),
        "source_structured_rationale_sha256": _digest(structured),
        "source_packet_sha256": _digest(packet),
    }
    pairs = {
        "source_packet_id": packet["packet_id"],
        "source_packet_type": packet["packet_type"],
        "source_schema_version": packet["schema_version"],
        "source_domain": packet["domain"], "source_role": packet["source_role"],
        "target_role": packet["target_role"], "business_request_packet_id": business["packet_id"],
        "source_route_context_packet_id": route["packet_id"],
        "source_route_id": packet["source_route_id"],
        "source_proposal_id": proposal["proposal_id"],
        "source_structured_rationale_ref": "structured_rationale_v01:" + _digest(structured),
    }
    _require(all(binding[k] == v for k, v in {**family, **pairs}.items())
        and all(binding[k] == router_input[k] for k in ("request_id", "transaction_id", "owning_root_id")),
        "native_bsep_binding_mismatch")
    refs = [{"source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"], "request_id": binding["request_id"],
        "domain_id": binding["domain_id"]}]
    _require(packet["domain"] == route["domain"] == business["domain"] == binding["domain_id"]
        and business["request_id"] == binding["request_id"]
        and packet["source_refs"] == route["source_refs"] == refs
        and packet["source_context_packet_id"] == route["packet_id"]
        and packet["source_proposal_id"] == proposal["proposal_id"]
        and packet["source_structured_rationale_ref"] == pairs["source_structured_rationale_ref"]
        and route["allowed_routes"] == [packet["source_route_id"]]
        and proposal["suggested_route"] == packet["source_route_id"]
        and route["selected_vector_ids"] == proposal["selected_vector_ids"] == packet["selected_vector_ids"]
        and route["required_guards"] == proposal["required_guards"] == packet["required_guards"],
        "native_bsep_binding_mismatch")
    _require(family["source_packet_sha256"] == BSEP_NATIVE_SHA256
        and _digest(base) == BSEP_SOURCE_SHA256, "native_bsep_source_digest_mismatch")
    repository = Path(__file__).resolve().parents[3]
    _require(all(_sha(_read(repository, path)) == expected
        for path, expected in _BSEP_VALIDATOR_PINS.items()), "native_bsep_validator_source_changed")
    result = {
        "projection_kind": "NATIVE_DTO_SAFE_DERIVATIVE",
        **{k: packet[k] for k in ("packet_type", "schema_version", "domain", "source_role", "target_role", "created_by")},
        "authority_boundary_flags": {k: packet[k] for k in (*_BSEP_TRUE_FLAGS, *_BSEP_FALSE_FLAGS)},
        "source_file": BSEP_SOURCE_FILE, "source_file_sha256": BSEP_SOURCE_SHA256,
        "packet_pointer": BSEP_PACKET_POINTER, "binding_pointer": BSEP_BINDING_POINTER,
        "canonical_native_dto_sha256": family["source_packet_sha256"],
        "recorded_binding_sha256": _digest(binding), "source_family_hashes": family,
        "private_references_sha256": _digest({
            **{k: binding[k] for k in ("bsep_binding_id", "request_id", "transaction_id", "owning_root_id")},
            **pairs, "source_refs": packet["source_refs"]}),
        "offline_validation": {"packet_accepted": pv["accepted"], "packet_reasons": list(pv["reasons"]),
            "binding_status": bv.validation_status, "binding_reasons": list(bv.reason_codes),
            "surrounding_source_family_validated": True},
        "validator_source_pins": [{"path": path, "sha256": sha} for path, sha in sorted(_BSEP_VALIDATOR_PINS.items())],
        "limitations": ["offline_DTO_and_recorded_source_binding_only", "no_live_origin_or_authority_reconstruction",
            "no_raw_native_role_payload_published", "native_DTO_is_not_KernelArtifact_canonical_reference"],
    }
    _validate_native_bsep_projection(result)
    return result


def _validate_native_bsep_projection(value):
    fixed = {"projection_kind": "NATIVE_DTO_SAFE_DERIVATIVE",
        "packet_type": "BoundedSemanticEvidencePacket", "schema_version": "bounded_semantic_evidence_packet_v0.1",
        "domain": "EPHEMERAL_WORKSPACE", "source_role": "orchestrator", "target_role": "architect",
        "created_by": "runtime/bounded_context_packet_builder", "source_file": BSEP_SOURCE_FILE,
        "source_file_sha256": BSEP_SOURCE_SHA256, "canonical_native_dto_sha256": BSEP_NATIVE_SHA256,
        "packet_pointer": BSEP_PACKET_POINTER, "binding_pointer": BSEP_BINDING_POINTER,
        "offline_validation": {"packet_accepted": True, "packet_reasons": [], "binding_status": "PASS",
            "binding_reasons": [], "surrounding_source_family_validated": True},
        "validator_source_pins": [{"path": path, "sha256": sha} for path, sha in sorted(_BSEP_VALIDATOR_PINS.items())],
    }
    flags = {**{k: True for k in _BSEP_TRUE_FLAGS}, **{k: False for k in _BSEP_FALSE_FLAGS}}
    _require(type(value) is dict and all(_canonical(value.get(k)) == _canonical(v) for k, v in fixed.items())
        and value.get("authority_boundary_flags") == flags
        and all(type(v) is bool for v in value["authority_boundary_flags"].values()),
        "native_bsep_projection_mismatch")
    _require(set(value) == set(fixed) | {"authority_boundary_flags", "recorded_binding_sha256",
        "source_family_hashes", "private_references_sha256", "limitations"}
        and set(value["source_family_hashes"]) == {"business_request_packet_sha256", "source_route_context_sha256",
            "source_proposal_sha256", "source_structured_rationale_sha256", "source_packet_sha256"}
        and value["source_family_hashes"]["source_packet_sha256"] == BSEP_NATIVE_SHA256
        and all(type(v) is str and _SHA.fullmatch(v) for v in (
            value["recorded_binding_sha256"], value["private_references_sha256"], *value["source_family_hashes"].values())),
        "native_bsep_projection_mismatch")
    _scan(value)


_HISTORICAL_PROOF_PINS = {
    "receipt": "5df28caf6e640f7b37d28830ff1d6c1e5b705375803203a646c9c92b08a99ce6",
    "nodes": "8efadcceee727f4a03349597624fe35b3b3396967f9722d4d46c83c5a4d5b3ec",
    "source_ledger": "9f6be22a8d291cf44797b7892ee31ec149661004a750b1dc238fa472cf88c88c",
}
_HISTORICAL_REQUIREMENTS = frozenset(("EW-A02", "EW-A05", "EW-A06", "EW-A07", "EW-A08", "EW-A10"))
_PROBE_REQUIREMENTS = frozenset(("EW-A01", "EW-A03", "EW-A04", "EW-A09", "EW-A11"))
_A12_FACT_KEYS = ("top_level_D", "top_level_E", "nested_retained_D", "frames_before", "frames_after",
    "pcm_before", "pcm_after", "photo_and_old_authority_unchanged", "observation_seconds_after_packet_expiry")


def _supplemental_inputs(root, expected_manifest_sha256):
    _require(type(expected_manifest_sha256) is str and _SHA.fullmatch(expected_manifest_sha256),
        "supplemental_manifest_mismatch")
    raw = _read(root, "MANIFEST.json")
    _require(_sha(raw) == expected_manifest_sha256, "supplemental_manifest_mismatch")
    rows = _json(raw)
    _require(type(rows) is list and rows, "supplemental_manifest_scope_invalid")
    index, folded = {}, set()
    for row in rows:
        _require(type(row) is dict and set(row) == {"path", "bytes", "sha256"}, "supplemental_manifest_scope_invalid")
        _safe_path(row["path"])
        path = row["path"]
        _require(path != "MANIFEST.json" and unicodedata.normalize("NFC", path) == path
            and path.casefold() not in folded, "supplemental_manifest_scope_invalid")
        folded.add(path.casefold())
        index[path] = row
    actual = []
    for path in Path(root).rglob("*"):
        _require(not path.is_symlink(), "symlink_rejected")
        if not path.is_dir():
            actual.append(path.relative_to(root).as_posix())
    _require(set(actual) == set(index) | {"MANIFEST.json"}, "supplemental_manifest_scope_invalid")
    contents = {}
    for name, row in index.items():
        data = _read(root, name)
        _require(type(row["bytes"]) is int and row["bytes"] == len(data)
            and row["sha256"] == _sha(data), "supplemental_file_digest_mismatch")
        contents[name] = data
    def read(name):
        _require(name in contents, "supplemental_reference_not_bound")
        return contents[name]
    return read, index


def _source_function_exists(data, nodeid):
    try:
        tree = ast.parse(data.decode("utf-8"))
    except (SyntaxError, UnicodeError):
        raise ValueError("supplemental_source_binding_mismatch") from None
    name = nodeid.split("::")[-1].split("[")[0]
    _require(any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
        for n in ast.walk(tree)), "supplemental_source_binding_mismatch")


def _method_bytes(data, qualified_name):
    text = data.decode("utf-8")
    matches = []
    def visit(node, parts):
        scoped = isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        current = parts + (node.name,) if scoped else parts
        if scoped and ".".join(current) == qualified_name:
            matches.append(ast.get_source_segment(text, node).encode("utf-8"))
        for child in ast.iter_child_nodes(node):
            visit(child, current)
    visit(ast.parse(text), ())
    _require(len(matches) == 1, "supplemental_source_bridge_mismatch")
    return matches[0]


def _validate_source_bridge(value, requirement, read, current, pins):
    _require(value["version"] == "ews4r.source_bridge.v01"
        and value["historical_runtime_sha256"] == "d2c523f8704220ef86fa820139035a1b3e30d26d503671447e488349fb91df72"
        and value["current_runtime_sha256"] == RUNTIME_SHA256, "supplemental_source_bridge_mismatch")
    row = _one(value["rows"], "requirement", requirement)
    _require(row["carry_justified"] is True and row["production_paths"] and row["methods"]
        and type(row["impact"]) is str and row["impact"], "supplemental_source_bridge_mismatch")
    snapshots = {}
    for item in row["production_paths"]:
        path = item["path"]
        old, new = read(item["executed_source_ref"]), read(item["current_source_ref"])
        _require(path not in snapshots and _sha(old) == item["executed_sha256"]
            == _one(pins, "path", path)["sha256"] and _sha(new) == item["current_sha256"] == current[path]["sha256"],
            "supplemental_source_bridge_mismatch")
        snapshots[path] = (old, new)
    methods = []
    for item in row["methods"]:
        old, new = snapshots[item["path"]]
        old_body, new_body = (_method_bytes(data, item["qualified_name"]) for data in (old, new))
        _require(_sha(old_body) == item["executed_body_sha256"] and _sha(new_body) == item["current_body_sha256"]
            and item["body_unchanged"] is (old_body == new_body), "supplemental_source_bridge_mismatch")
        diff = read(item["diff_ref"])
        methods.append({k: item[k] for k in ("path", "qualified_name", "executed_body_sha256", "current_body_sha256", "body_unchanged")}
            | {"diff_sha256": _sha(diff)})
    return {"scope": "narrow_inspected_method_body_bridge_not_current_runtime_reexecution", "impact": row["impact"],
        "production_source_pairs": [{k: p[k] for k in ("path", "executed_sha256", "current_sha256")} for p in row["production_paths"]],
        "methods": methods}


def _probe_observation(value, row, *, private_receipts=True):
    requirement = row["requirement"]
    _require(value["version"] == "ews4r.local_boundary_probe.v01" and value["requirement"] == requirement
        and value["nodeid"] == row["nodeid"] and value["classification"] == "CURRENT_LOCAL_BOUNDARY_PROBE"
        and value["principal_run_counters_modified"] is False
        and all(type(value[k]) is int and value[k] == 0 for k in ("fixture_root_decisions", "workspace_instances",
            "D_executions", "E_executions", "provider_calls", "external_network_calls", "subprocesses")),
        "supplemental_observation_mismatch")
    denied = value["denied_requests"]
    _require(type(denied) is list and denied, "supplemental_observation_mismatch")
    if requirement in {"EW-A01", "EW-A03", "EW-A09"}:
        expected_error = "derived_frame_only" if requirement == "EW-A01" else "service_operation_not_allowed"
        operation = {"EW-A01": None, "EW-A03": "write_source", "EW-A09": "render"}[requirement]
        valid_op = {"EW-A01": None, "EW-A03": "render", "EW-A09": "observe"}[requirement]
        _require(value["instrumentation_scope"] == "IN_PROCESS_PRODUCTION_HANDLER_THREADS"
            and len(denied) == 1 and denied[0]["http_status"] == 403 and denied[0]["error"] == expected_error
            and denied[0]["operation"] == operation and value["valid_counterpart"]["http_status"] == 200
            and value["valid_counterpart"]["operation"] == valid_op
            and (not private_receipts or (all(item in value["all_request_records"] for item in (value["valid_counterpart"], *denied))
                and len(value["all_request_records"]) == value["fixture_loopback_requests"]))
            and set(value["observed_sink_attempts"]) == {"source_read_attempts", "source_write_attempts", "render_dispatches"}
            and all(type(n) is int and n == 0 for n in value["observed_sink_attempts"].values())
            and value["canary_before_sha256"] == value["canary_after_sha256"] == value["cleanup"]["source_after_sha256"]
            and all(value["cleanup"][k] is True for k in ("worker_thread_joined", "server_closed", "all_created_threads_joined"))
            and value["cleanup"]["owned_subprocesses"] == 0, "supplemental_observation_mismatch")
        role = {"EW-A01": "display_read", "EW-A03": "media_rpc", "EW-A09": "audio_rpc"}[requirement]
        _require(denied[0]["credential_role"] == value["valid_counterpart"]["credential_role"] == role
            and denied[0]["session_matches_fixture"] is value["valid_counterpart"]["session_matches_fixture"] is True
            and all(_SHA.fullmatch(value[k]) for k in ("canary_before_sha256", "canary_after_sha256")),
            "supplemental_observation_mismatch")
        if requirement == "EW-A01":
            _require(denied[0]["method"] == "GET" and denied[0]["path"] == "/sources/asset:1/raw"
                and value["valid_counterpart"]["path"].startswith("/frame/"), "supplemental_observation_mismatch")
        if requirement == "EW-A09":
            _require(denied[0]["requested_logical_asset"] == "video:source:fixture"
                and denied[0]["credential_role"] == "audio_rpc", "supplemental_observation_mismatch")
        if requirement in {"EW-A03", "EW-A09"}:
            _require(denied[0]["path"] == value["valid_counterpart"]["path"] == "/rpc"
                and denied[0]["method"] == value["valid_counterpart"]["method"] == "POST"
                and denied[0]["next_sequence"] == value["valid_counterpart"]["next_sequence"] + 1,
                "supplemental_observation_mismatch")
    elif requirement == "EW-A04":
        _require({item["operation"] for item in denied} == {"SHELL", "EXEC", "READ_FILE", "WRITE_FILE"}
            and len(denied) == 4 and all(item["error"] == "operation_not_allowed" for item in denied)
            and value["valid_counterpart"]["operation"] == "NEXT" and value["valid_counterpart"]["accepted"] is True
            and value["denied_fixture_dispatches"] == 0 and value["observed_production_dispatch_attempts"] == 0
            and value["canary_before_sha256"] == value["canary_after_sha256"]
            and _SHA.fullmatch(value["canary_before_sha256"])
            and value["valid_counterpart"]["fixture_dispatch_count"] == value["valid_counterpart"]["fixture_file_writes"] == 1
            and value["instrumentation_scope"] == "PRODUCTION_PURE_VALIDATOR_AND_FIXTURE_CONTINUATION_CANARY",
            "supplemental_observation_mismatch")
    else:
        _require(requirement == "EW-A11" and len(denied) == 2
            and {item["injected_field"] for item in denied} == {"device_ids", "topology_edges"}
            and all(item["error"] == "semantic_closed_shape" for item in denied)
            and len(value["valid_counterparts"]) == 2
            and all(item["valid_closed_shape_accepted"] is True for item in value["valid_counterparts"])
            and value["fixture_context_creates_authority"] is False and value["observed_semantic_materialization_attempts"] == 0
            and value["instrumentation_scope"] == "PRODUCTION_PURE_SEMANTIC_DTO_VALIDATOR",
            "supplemental_observation_mismatch")
    expected_error = denied[0]["error"]
    expected_http_status = denied[0].get("http_status")
    _require(row["observed_refusal"]["error"] == expected_error
        and row["observed_refusal"]["http_status"] == expected_http_status, "supplemental_observation_mismatch")
    # Closed field selection, including executing-thread counters, never configs or credentials.
    keys = ("instrumentation_scope", "fixture_scope", "valid_counterpart", "valid_counterparts", "denied_requests",
        "observed_sink_attempts", "canary_before_sha256", "canary_after_sha256", "cleanup", "fixture_loopback_requests",
        "denied_fixture_dispatches", "observed_production_dispatch_attempts", "fixture_context_creates_authority",
        "observed_semantic_materialization_attempts", "fixture_root_decisions", "workspace_instances", "D_executions", "E_executions",
        "provider_calls", "external_network_calls", "subprocesses", "principal_run_counters_modified")
    return {k: value[k] for k in keys if k in value}


@_fail_closed
def _load_supplemental_proof(root, expected_manifest_sha256, *, source_ledger_rows, principal_sources, principal_facts):
    read, index = _supplemental_inputs(root, expected_manifest_sha256)
    plan = _json(read("coverage_plan.json"))
    _require(set(plan) == {"version", "principal_archive_sha256", "rows"}
        and plan["version"] == "ews4r.supplemental_proof.v01" and plan["principal_archive_sha256"] == INPUT_ARCHIVE_SHA256,
        "supplemental_coverage_scope_invalid")
    rows = plan["rows"]
    _require(type(rows) is list and len(rows) == 12
        and {r["requirement"] for r in rows} == {"EW-A%02d" % i for i in range(1, 13)}, "supplemental_coverage_scope_invalid")
    current = {r["path"]: r for r in source_ledger_rows}
    principal = dict(principal_sources) if type(principal_sources) is dict else {r["path"]: r for r in principal_sources}
    coverage = []
    for row in sorted(rows, key=lambda r: r["requirement"]):
        requirement = row["requirement"]
        refs = row["proof_refs"]
        proof_records = [{"role": key, **index[path]} for key, path in sorted(refs.items()) if path in index]
        _require(len(proof_records) == len(refs), "supplemental_reference_not_bound")
        pins = row["source_pins"]
        _require(type(pins) is list and pins and len({p["path"] for p in pins}) == len(pins)
            and all(p["path"] in current and type(p["sha256"]) is str and _SHA.fullmatch(p["sha256"]) for p in pins),
            "supplemental_source_binding_mismatch")
        if requirement == "EW-A12":
            _require(row["proof_kind"] == "principal_accepted_run" and row["classification"] == "CARRIED_PRIOR_EVIDENCE"
                and row["nodeid"] is None, "supplemental_coverage_scope_invalid")
            record = _json(read(refs["observation"]))
            _require(record["principal_input_archive_sha256"] == INPUT_ARCHIVE_SHA256
                and record["runtime_sha256"] == RUNTIME_SHA256
                and sorted(record["principal_source_records"], key=lambda r: r["path"]) == sorted(principal.values(), key=lambda r: r["path"])
                and set(record["requested_fact_keys"]) == set(_A12_FACT_KEYS)
                and all(p["sha256"] == current[p["path"]]["sha256"] for p in pins), "supplemental_principal_binding_mismatch")
            observed = {"source": "already_validated_accepted_principal_run",
                "facts": {key: principal_facts[key] for key in _A12_FACT_KEYS}, "new_D_E_executions": 0}
            call = None
        else:
            historical = requirement in _HISTORICAL_REQUIREMENTS
            _require(row["proof_kind"] == ("historical_test_call" if historical else "current_local_probe")
                and row["classification"] == ("CARRIED_PRIOR_EVIDENCE" if historical else "CURRENT_LOCAL_BOUNDARY_PROBE"),
                "supplemental_coverage_scope_invalid")
            receipt_data, node_data = read(refs["receipt"]), read(refs["nodes"])
            receipt = _json(receipt_data)
            for output in ("stdout", "stderr"):
                logical = str(PurePosixPath(refs["receipt"]).parent / (output + ".log"))
                data = read(logical)
                _require(receipt[output] == {"bytes": len(data), "sha256": _sha(data)}, "supplemental_execution_receipt_mismatch")
            calls = [_json(line) for line in node_data.splitlines() if line.strip()]
            matches = [n for n in calls if n.get("nodeid") == row["nodeid"] and n.get("phase") == "call"]
            _require(receipt["rc"] == 0 and len(matches) == 1 and matches[0]["outcome"] == "passed",
                "supplemental_call_phase_not_passed")
            call = {k: matches[0][k] for k in ("nodeid", "phase", "outcome", "seconds")}
            _require(all(receipt["source_pins"].get(p["path"]) == p["sha256"] for p in pins),
                "supplemental_source_binding_mismatch")
            test_path = row["nodeid"].split("::")[0]
            test_sha = _one(pins, "path", test_path)["sha256"]
            body = read(refs["source_body"])
            _require(_sha(body) == test_sha, "supplemental_source_binding_mismatch")
            _source_function_exists(body, row["nodeid"])
            if historical:
                _require(all(_sha(read(refs[k])) == expected for k, expected in _HISTORICAL_PROOF_PINS.items()),
                    "supplemental_historical_proof_mismatch")
                old_ledger = _json(read(refs["source_ledger"]))
                # The archive's final ledger postdates this exact test call. The
                # immutable receipt pins its executed test body independently.
                _require(all(_one(old_ledger, "path", p["path"])["sha256"] == p["sha256"]
                    for p in pins if p["path"] != test_path),
                    "supplemental_source_binding_mismatch")
                bridge = _validate_source_bridge(_json(read(refs["source_bridge"])), requirement, read, current, pins)
                observed = {"basis": "passed_exact_historical_test_call_and_inspected_source_assertion",
                    "asserted_refusal": row["observed_refusal"], "source_bridge": bridge,
                    "executed_test_source_sha256": test_sha,
                    "historical_final_ledger_test_sha256": _one(old_ledger, "path", test_path)["sha256"],
                    "chronology": "executed_test_body_is_receipt_bound; archive_final_ledger_is_separate_later_state",
                    "current_bytes_reexecuted": False, "new_probe_counters": None}
            else:
                _require(requirement in _PROBE_REQUIREMENTS
                    and all(p["sha256"] == current[p["path"]]["sha256"] for p in pins),
                    "supplemental_source_binding_mismatch")
                observation = _json(read(refs["observation"]))
                probe_ledger_data = read(refs["source_ledger"])
                probe_ledger = _json(probe_ledger_data)
                _require(receipt["nodes"] == {"bytes": len(node_data), "sha256": _sha(node_data)}
                    and receipt["source_ledger"] == {"bytes": len(probe_ledger_data), "sha256": _sha(probe_ledger_data)}
                    and all(_one(probe_ledger, "path", p["path"])["sha256"] == p["sha256"] for p in pins),
                    "supplemental_source_binding_mismatch")
                observation_raw = read(refs["observation"])
                observed_record = _one(receipt["observation_records"], "path", "observations/" + requirement + ".json")
                _require(observed_record["bytes"] == len(observation_raw) and observed_record["sha256"] == _sha(observation_raw),
                    "supplemental_observation_mismatch")
                for item in probe_ledger:
                    source_ref = str(PurePosixPath(refs["source_ledger"]).parent / item["source_object"])
                    source_bytes = read(source_ref)
                    _require(len(source_bytes) == item["bytes"] and _sha(source_bytes) == item["sha256"]
                        and current[item["path"]]["sha256"] == item["sha256"], "supplemental_source_binding_mismatch")
                _require({p["path"]: p["sha256"] for p in observation["source_pins"]} == {p["path"]: p["sha256"] for p in pins},
                    "supplemental_source_binding_mismatch")
                observed = _probe_observation(observation, row)
        coverage.append({**{key: row[key] for key in ("requirement", "classification", "proof_kind",
            "intended_attempt", "entrypoint", "expected_boundary", "observed_refusal", "limitations")},
            "proof_records": proof_records, "executed_source_pins": [{k: p[k] for k in ("path", "sha256")} for p in pins],
            "call_phase": call, "observed_proof": observed})
    summary = {"coverage": coverage, "supplemental_manifest_sha256": expected_manifest_sha256,
        "coverage_plan_sha256": index["coverage_plan.json"]["sha256"],
        "proof_scope": "private_proof_files_checked_at_export; public_replay_checks_saved_safe_derivative_only",
        "principal_source_record_count": len(principal), "principal_run_counters_modified": False,
        "coverage_counts": {"historical_requirement_rows": 6,
            "distinct_historical_call_nodes": len({c["call_phase"]["nodeid"] for c in coverage if c["proof_kind"] == "historical_test_call"}),
            "current_local_boundary_probes": 5, "principal_accepted_runs": 1},
        "probe_counters": {"fixture_loopback_requests": sum(c["observed_proof"].get("fixture_loopback_requests", 0) for c in coverage),
            "fixture_root_decisions": 0, "workspace_instances": 0, "D_executions": 0, "E_executions": 0,
            "provider_calls": 0, "external_network_calls": 0, "subprocesses": 0},
    }
    _scan(summary)
    return summary


def _project_inputs(read):
    run = "browser_run_01/"
    f = read(run + "native_final/report.json")
    roles = read(run + "native_final/semantic_safe.json")
    base = read(run + "native_common_return/D_baseline.json")
    retained = read(run + "native_common_return/D_retained.json")
    delta = read(run + "native_common_return/E_return.json")
    consumed = read(run + "native_common_return/media_consumption.json")
    old = read(run + "temporal/original_immutable_material.json")
    old_bundle_projection = read(run + "temporal/original_D_execution_bundle_projection.json")
    fixture_before = read(run + "fixture_sources_before.json")
    fixture_after = read(run + "fixture_sources_after.json")
    after = read(run + "temporal/after_E_before_fresh_commands.json")
    before = read(run + "observations/audio_fault_before_loss/observation.json")
    auto = read(run + "observations/automatic_after_E/observation.json")
    silent = read(run + "observations/silent_frames/observation.json")
    saved = read(run + "observations/saved/observation.json")
    candidate = read(run + "observations/save_candidate/observation.json")
    complete = read(run + "complete.json")
    sidecar = read(run + "native_final/verified_sidecar.json")
    phase_bytes = read(run + "workspace/phases.jsonl")
    phases = [_json(line) for line in phase_bytes.splitlines()]
    gb, gr = _graph(base), _graph(retained)
    _require(len(gb) == 83 and len(gr) == 156 and all(gr.get(k) == v for k, v in gb.items()), "original_graph_preservation_failed")
    vb = _private_graph_audit(list(gb.values()), base)
    vr = _private_graph_audit(list(gr.values()), retained)
    original_graphs = {
        "scope": "ORIGINAL_ABI_GRAPHS_AND_SEPARATE_PRIVATE_AGGREGATE_WRAPPERS",
        "baseline_artifacts": len(gb), "retained_artifacts": len(gr),
        "baseline_unchanged_in_retained": True,
        "native_canonical_reference_status": "UNSUPPORTED_NATIVE_SCHEMA",
        "original_native_manifest_pass_claimed": False,
        "baseline_private_audit": vb, "retained_private_audit": vr,
        "public_replay_does_not_load_private_graphs": True}
    _require(len(roles) == 3 and all(r["mode"] == "CONTROLLED_DETERMINISTIC" for r in roles), "semantic_mode_mismatch")
    work = f["work_result"]["payload"]["work_results"]
    compile_row = _one(work, "work_id", "compile_contract")
    consume_row = _one(work, "work_id", "consume_contract")
    material = _one(compile_row["invocation"]["inputs"], "parameter_name", "material")["value"]
    _require(_json(material.encode()) == [r["output"] for r in roles], "semantic_work_input_mismatch")
    _require(all(r["status"] == "COMPLETED" and r["result"]["outcome"] == "SUCCEEDED" for r in work), "semantic_work_not_consumed")
    _require(any(c["source_artifact_id"] == compile_row["result"]["result_id"] and c["disposition"] == "USED" for c in consume_row["consumed_fields"]), "semantic_causal_ref_missing")
    source_art = _one(delta["historical_source"]["observed_source_artifacts"], "artifact_id", consumed["source_artifact_ref"])
    _require(source_art["payload"]["audio_source"] == after["loss_dependency"] and source_art["payload"]["content_sha256"] == _digest(after["actual_changed_fact"]), "changed_source_binding_mismatch")
    binding = _one(retained["observed_work_context"]["ordered_binding_artifacts"], "artifact_id", consumed["consumed_binding_ref"])
    cell = _one(retained["cell_results"], "result_id", consumed["recomputed_result_ref"])
    _require(binding["payload"]["source_pair"]["observed_identity_ref"] == source_art["artifact_id"]
        and binding["payload"]["topology_binding"]["cell_ref"] == cell["cell_id"]
        and cell["outcome"] == "COMPLETED" and cell["accepted_output_refs"] == consumed["output_refs"], "recomputed_result_binding_mismatch")
    queues = [q for q in retained["queue_entries"] if q["cell_id"] == cell["cell_id"] and q["state"] == "COMPLETED" and set(q["observed_output_refs"]) & set(consumed["output_refs"])]
    _require(queues and all(binding["artifact_id"] in q["observed_evidence_refs"] for q in queues), "completed_queue_causal_binding_missing")
    rc = _one(retained["retained_consumptions"], "consumption_id", consumed["retained_consumption_ref"])
    old_cell = _one(base["cell_results"], "result_id", consumed["preserved_D_result_ref"])
    _require(rc["consumed_result"] == old_cell == rc["admission"]["evidence"]["historical_cell_result"], "retained_result_changed")
    _require(rc["consumed_result_artifact"] == rc["admission"]["evidence"]["historical_result_artifact"]
        and rc["consumed_result_artifact"] in base["result_artifacts"], "retained_artifact_changed")
    _require(any(old_cell["result_id"] in c["ordered_child_result_ids"] for c in retained["cell_results"]), "retained_parent_consumption_missing")
    _require(delta["recomputation_result"]["recomputation_result_id"] == consumed["delta_result_ref"]
        and consumed == f["media_consumption"] == complete["media_consumption"], "delta_consumption_identity_mismatch")
    delta_review = delta["final_root_decision_result"]
    delta_review_artifact = delta["final_root_decision_artifact"]
    fresh_kernel, fresh_input, fresh_review = after["fresh_informational_Root_review"]
    _require(delta_review["decision"] == fresh_review["decision"] == "ACCEPT"
        and delta_review["decision_id"] == consumed["final_Root_review"]
        and delta_review["selected_candidate_id"] == consumed["delta_result_ref"]
        and delta_review["decision_input_id"] == delta["final_root_decision_input"]["decision_input_id"]
        and delta_review_artifact["payload"] == {k: v for k, v in delta_review.items() if k != "transaction_id"}
        and delta_review_artifact["transaction_id"] == delta_review["transaction_id"]
        and fresh_review["decision_input_id"] == fresh_input["decision_input_id"]
        and fresh_review["target_root_id"] == fresh_input["target_root_id"]
        and fresh_review["selected_candidate_id"] == "ews:media_continuation:" + _digest(consumed)
        and fresh_kernel["effect_access"] == "NONE"
        and all(r["root_commit_created"] and not r["effect_requested"] and not r["permission_created"]
            for r in (delta_review, fresh_review)), "recorded_root_review_binding_mismatch")
    cap = after["retained_capture"]
    observation = _one(cap["observations"], "dependency_id", after["actual_loss_observations"][0]["dependency_id"])
    tb = retained["temporal_binding"]
    _require(tb == delta["temporal_binding"] and tb["capture_ordinal"] == cap["capture_ordinal"]
        and tb["evaluation_time_epoch_seconds"] == cap["evaluation_time"]
        and tb["host_revision"] == cap["host_revision"] and tb["source_revision"] == cap["source_revision"]
        and tb["observation_ids"] == [observation["observation_id"]], "temporal_capture_binding_mismatch")
    expiry = old["temporal_authority"]["expires_at_utc"]
    _require(observation["observed_at_utc"] > expiry and observation["valid_from_utc"] == observation["observed_at_utc"]
        < observation["valid_to_utc"] <= before["state"]["expires"]
        and observation["observed_content_sha256"] == _digest(after["actual_changed_fact"]), "actual_observation_window_invalid")
    _require(cap["root_bound_packet"] == old["root_bound_packet"]
        and _digest(old) == after["original_material_sha256"]
        and after["current_original_material_sha256"] == after["original_material_sha256"]
        and _digest(old_bundle_projection) == after["original_D_bundle_sha256"] == after["current_D_bundle_sha256"]
        and after["current_host_root_bound_packet_unchanged"] is True
        and before["local_effects"] == auto["local_effects"]
        and before["command_history"] == auto["command_history"], "old_authority_or_effect_history_changed")
    _require(fixture_before == fixture_after and len(fixture_before) == 24
        and all(value in fixture_before.values() for value in before["photo_work"]["source_sha256"].values()),
        "recorded_fixture_preservation_mismatch")
    _require(before["photo_work"] == auto["photo_work"] == silent["photo_work"]
        and before["photo_pixels"]["sha256"] == auto["photo_pixels"]["sha256"] == silent["photo_pixels"]["sha256"], "photo_work_or_pixels_changed")
    for label in ("audio_fault_before_loss", "automatic_after_E", "silent_frames"):
        _require(_sha(read(run + "observations/" + label + "/photo.png")) == before["photo_pixels"]["sha256"], "photo_bytes_digest_mismatch")
    events = f["media_events"]
    _require(len(events) == f["media_state"]["frames"] == 16 and sum((x["audio"] or {}).get("samples", 0) for x in events) == 16000
        and all(x["audio"] is None for x in events[4:]) and before["state"]["media"]["frames"] == 4, "media_continuation_counts_invalid")
    approvals = saved["approvals"]
    approval_id = saved["state"]["saved"]["approval"]
    _require(len(approvals) == 1 and approvals[approval_id]["used"] is True
        and approvals[approval_id]["candidate"] == candidate["state"]["pending"], "save_approval_candidate_mismatch")
    approved = approvals[approval_id]["candidate"]
    sidecar_bytes = _canonical(sidecar) + b"\n"
    _require(approved["content"] == sidecar and _sha(sidecar_bytes) == SIDECAR_SHA256
        and approved["bytes_sha256"] == SIDECAR_SHA256 and saved["state"]["saved"]["bytes"] == len(sidecar_bytes) == 250, "sidecar_output_binding_mismatch")
    saves = [c for c in f["commands"] if _json(c["output"]["material"].encode())["op"] == "SAVE"]
    _require(len(saves) == 1, "save_count_invalid")
    save = saves[0]
    output = _json(save["output"]["material"].encode())
    _require(output["saved"] == saved["state"]["saved"], "save_receipt_output_mismatch")
    receipt = save["receipt"]["payload"]
    invocation = receipt["execution_evidence"]["invocation"]
    _require(save["root_decision"]["decision"] == "ACCEPT"
        and invocation["packet_id"] == save["packet_id"]
        and invocation["candidate_id"] == receipt["selected_candidate_id"] == save["root_decision"]["selected_candidate_id"]
        and receipt["root_decision_id"] == save["root_decision"]["decision_id"], "save_root_packet_receipt_binding_mismatch")
    command = _json(_one(invocation["inputs"], "parameter_name", "command")["value"].encode())
    _require(command["op"] == "SAVE" and command["value"] == approval_id
        and _one(invocation["inputs"], "parameter_name", "version")["value"] == approved["version"], "save_packet_approval_binding_mismatch")
    _require(complete["status"] == f["state"]["status"] == "CLOSED_SUCCESS" and complete["failure"] is None
        and not complete["media_thread_alive"] and all(not t["alive"] for t in complete["viewer_threads"]), "cleanup_incomplete")
    processes = complete["cleanup"]["processes"]
    _require(len(processes) == 3 and all(p["reaped"] and p["close_error"] is None for p in processes), "owned_process_cleanup_incomplete")
    _require(f["external_device_business_effects"] == 0 and all(delta["recomputation_result"][k] == 0 for k in ("provider_calls", "model_calls", "network_calls", "real_world_effects_count")), "source_call_or_external_effect_mismatch")
    counts = {p: sum(x["phase"] == p for x in phases) for p in ("COMMON_D_START", "COMMON_E_START", "COMMON_D_RETURN", "COMMON_E_RETURN")}
    _require(all(v == 1 for v in counts.values()), "top_level_D_E_counts_invalid")
    graph_sources = [source_art, binding, f["work_topology"], f["work_result"], save["receipt"]]
    artifact_provenance = [{"source_artifact_id": x["artifact_id"], "source_canonical_sha256": _digest(x),
        "source_payload_sha256": _digest(x["payload"])} for x in graph_sources]
    facts = {
        "mode": f["mode"], "provider_mode": "deterministic_fixture", "semantic_roles": len(roles),
        "provider_calls": delta["recomputation_result"]["provider_calls"], "network_calls": delta["recomputation_result"]["network_calls"], "gemini_calls": 0,
        "local_synthetic_command_effects": f["state"]["local_effects"], "external_business_effects": f["external_device_business_effects"],
        "sidecar_sha256": SIDECAR_SHA256, "sidecar_bytes": len(sidecar_bytes), "sidecar_writes": len(saves),
        "approval_sha256": _digest(approved), "approval_reference_sha256": _digest(approval_id),
        "save_packet_sha256": _digest(save["packet_id"]), "save_receipt_sha256": _digest(save["receipt"]),
        "photo_work_sha256": _digest(before["photo_work"]), "photo_preview_sha256": before["photo_pixels"]["sha256"],
        "old_packet_sha256": _digest(old["root_bound_packet"]), "old_material_sha256": after["original_material_sha256"],
        "retained_result_sha256": _digest(old_cell), "consumed_binding_sha256": _digest(binding),
        "delta_result_sha256": _digest(delta["recomputation_result"]), "temporal_binding_sha256": _digest(tb),
        "observation_seconds_after_packet_expiry": observation["observed_at_utc"] - expiry,
        "observation_window_seconds": observation["valid_to_utc"] - observation["valid_from_utc"],
        "capture_ordinal": cap["capture_ordinal"], "old_packet_refusal": after["stale_packet_refusal"],
        "photo_and_old_authority_unchanged": True, "frames_before": 4, "frames_after": len(events),
        "pcm_before": before["state"]["media"]["samples"], "pcm_after": f["media_state"]["samples"],
        "top_level_D": counts["COMMON_D_START"], "top_level_E": counts["COMMON_E_START"], "nested_retained_D": 1,
        "lifecycle": complete["status"], "owned_processes_reaped": len(processes),
        "viewer_threads_closed": len(complete["viewer_threads"]), "media_thread_closed": not complete["media_thread_alive"],
        "fixture_photo_hashes": sorted(before["photo_work"]["source_sha256"].values()),
        "recorded_fixture_count": len(fixture_before), "recorded_fixture_inventory_sha256": _digest(fixture_before),
        "fixture_preservation_scope": "exact_before_after_recorded_inventory_equality; original_media_not_in_public_package",
        "source_preserved_recorded": f["source_preserved"], "media_source_preserved_recorded": f["media_sources_preserved"],
        "action_class": complete["action_class"], "fresh_informational_review_sha256": _digest(after["fresh_informational_Root_review"]),
        "workspace_lifetime_seconds": before["state"]["expires"] - after["inspection"]["clock"]["source_epoch"]}
    return facts, original_graphs, artifact_provenance, roles, f, _native_bsep_projection(base)


def _documents(facts, graphs, provenance, roles, native, bsep, supplemental, sources, ledger_sha, ledger_rows, head):
    """Whitelisted fields only; native dictionaries never become package payloads."""
    contract = native["contract"]
    role_summaries = [{"role": r["role"], "mode": r["mode"], "response_sha256": _digest(r["output"]),
        "source_projection_ref_sha256": _digest(r["projection_ref"])} for r in roles]
    maps = (
        {"needs": list(roles[0]["output"]["needs"]), "source_task": "completed_local_synthetic_photo_and_media_workspace"},
        {"active_classes": list(contract["active_classes"]), "dormant_classes": list(contract["dormant_classes"]), "discovery_scope": "recorded_contract_classes_not_current_device_instances"},
        {"semantic_role": role_summaries[0], "needs": list(roles[0]["output"]["needs"]), "actual_work_consumption_verified": True},
        {"native_bsep": bsep, "compiled_contract_summary": {"contract_sha256": _digest(contract),
            "typed_commands": list(contract["commands"]), "source_write": contract["source_write"],
            "publication": contract["publication"], "projection_scope": "separate_derived_compiled_contract_summary"}},
        {"semantic_role": role_summaries[1], "audio_policy": contract["media"]["audio_policy"], "cleanup": contract["cleanup"], "save": contract["save"]},
        {"semantic_role": role_summaries[2], "minimize": contract["minimize"], "projection_method": "explicit_field_whitelist_with_private_reference_hashes", "original_private_graph_published": False},
        {"work_roles": list(native["work_topology"]["payload"]["ordered_work_ids"]), "source_topology_sha256": _digest(native["work_topology"]), "original_graph_verification": graphs,
         **{k: facts[k] for k in ("consumed_binding_sha256", "retained_result_sha256", "delta_result_sha256", "temporal_binding_sha256", "top_level_D", "top_level_E", "nested_retained_D")}},
        {k: facts[k] for k in ("workspace_lifetime_seconds", "lifecycle", "old_packet_sha256", "old_material_sha256", "observation_seconds_after_packet_expiry", "observation_window_seconds", "capture_ordinal", "old_packet_refusal")},
        {"class_roles": sorted(native["resource_plan"]), "historical_only": True, "current_grants_recreated": False, "authority_material_included": False},
        {k: facts[k] for k in ("action_class", "local_synthetic_command_effects", "frames_before", "frames_after", "pcm_before", "pcm_after", "photo_work_sha256", "photo_preview_sha256", "photo_and_old_authority_unchanged")},
        {k: facts[k] for k in ("sidecar_sha256", "sidecar_bytes", "approval_sha256", "approval_reference_sha256", "save_packet_sha256", "action_class")},
        {k: facts[k] for k in ("sidecar_sha256", "sidecar_bytes", "sidecar_writes", "approval_sha256", "save_receipt_sha256")},
        {k: facts[k] for k in ("lifecycle", "owned_processes_reaped", "viewer_threads_closed", "media_thread_closed", "source_preserved_recorded", "media_source_preserved_recorded")},
        supplemental,
        {"scan_scope": "all_emitted_decoded_JSON_and_nested_JSON_strings", "field_projection": "whitelist", "original_private_input_edited": False, "raw_media_included": False,
         "raw_semantic_envelopes_included": False, "public_fields_scan_required": True},
        {"facts": facts, "semantic_role_summaries": role_summaries,
         "mode_mapping": "CONTROLLED_DETERMINISTIC maps to deterministic_fixture; three local role responses consumed by actual Work; domain/browser/media actions were real local fixture operations",
         "provider_call_budget_scope": "zero_calls_in_this_recorded_run_not_an_owner_spending_policy",
         "original_graph_verification": graphs, "candidate_source_ledger_sha256": ledger_sha,
         "candidate_source_files": ledger_rows, "execution_head": head,
         "native_bsep_projection_sha256": _digest(bsep),
         "supplemental_proof_binding": {"supplemental_manifest_sha256": supplemental["supplemental_manifest_sha256"],
             "coverage_plan_sha256": supplemental["coverage_plan_sha256"], "safe_coverage_sha256": _digest(supplemental),
             "principal_source_record_count": supplemental["principal_source_record_count"],
             "probe_counters": supplemental["probe_counters"]},
         "candidate_commit_status": "UNCOMMITTED_CANDIDATE_NOT_OWNER_HEAD",
         "full_ews_acceptance": "NOT_SELF_AWARDED", "limitations": list(_LIMITATIONS)},
    )
    binding = {"input_archive": INPUT_ARCHIVE, "input_archive_sha256": INPUT_ARCHIVE_SHA256,
        "input_manifest_sha256": INPUT_MANIFEST_SHA256, "runtime_sha256": RUNTIME_SHA256,
        "source_records": sorted(sources.values(), key=lambda r: r["path"]),
        "source_artifacts": provenance, "verified_facts_sha256": _digest(facts),
        "supplemental_proof_manifest_sha256": supplemental["supplemental_manifest_sha256"]}
    return {name: {"document": name, "projection_kind": "DERIVED_SAFE_EVIDENCE_ONLY",
        "source_binding": binding if i == 15 else {"input_archive_sha256": INPUT_ARCHIVE_SHA256,
            "verified_facts_sha256": _digest(facts), "source_artifacts": provenance,
            "supplemental_proof_manifest_sha256": supplemental["supplemental_manifest_sha256"],
            "source_records": sorted(sources.values(), key=lambda r: r["path"])}, "summary": maps[i]}
        for i, name in enumerate(REQUIRED_DOCUMENTS)}


def _validate_coverage_summary(value):
    _require(type(value) is dict and set(value) == {"coverage", "supplemental_manifest_sha256", "coverage_plan_sha256",
        "proof_scope", "principal_source_record_count", "principal_run_counters_modified", "coverage_counts", "probe_counters"}
        and type(value["coverage"]) is list and len(value["coverage"]) == 12
        and [r["requirement"] for r in value["coverage"]] == ["EW-A%02d" % i for i in range(1, 13)]
        and value["principal_source_record_count"] == 22 and value["principal_run_counters_modified"] is False
        and value["coverage_counts"] == {"historical_requirement_rows": 6, "distinct_historical_call_nodes": 5, "current_local_boundary_probes": 5, "principal_accepted_runs": 1}
        and all(type(value[k]) is str and _SHA.fullmatch(value[k]) for k in ("supplemental_manifest_sha256", "coverage_plan_sha256")),
        "supplemental_projection_mismatch")
    _require(len({r["call_phase"]["nodeid"] for r in value["coverage"] if r["proof_kind"] == "historical_test_call"}) == 5,
        "supplemental_projection_mismatch")
    loops = 0
    for row in value["coverage"]:
        _require(set(row) == {"requirement", "classification", "proof_kind", "intended_attempt", "entrypoint",
            "expected_boundary", "observed_refusal", "limitations", "proof_records", "executed_source_pins", "call_phase", "observed_proof"},
            "supplemental_projection_mismatch")
        requirement = row["requirement"]
        historical = requirement in _HISTORICAL_REQUIREMENTS
        principal = requirement == "EW-A12"
        expected_kind = "principal_accepted_run" if principal else "historical_test_call" if historical else "current_local_probe"
        _require(row["proof_kind"] == expected_kind
            and row["classification"] == ("CURRENT_LOCAL_BOUNDARY_PROBE" if requirement in _PROBE_REQUIREMENTS else "CARRIED_PRIOR_EVIDENCE")
            and row["proof_records"] and row["executed_source_pins"], "supplemental_projection_mismatch")
        for record in row["proof_records"]:
            _safe_path(record["path"])
            _require(set(record) == {"role", "path", "bytes", "sha256"}
                and type(record["bytes"]) is int and record["bytes"] >= 0 and _SHA.fullmatch(record["sha256"]),
                "supplemental_projection_mismatch")
        for pin in row["executed_source_pins"]:
            _safe_path(pin["path"])
            _require(set(pin) == {"path", "sha256"} and _SHA.fullmatch(pin["sha256"]), "supplemental_projection_mismatch")
        if principal:
            _require(row["call_phase"] is None and set(row["observed_proof"]["facts"]) == set(_A12_FACT_KEYS)
                and row["observed_proof"]["new_D_E_executions"] == 0, "supplemental_projection_mismatch")
        else:
            _require(row["call_phase"]["phase"] == "call" and row["call_phase"]["outcome"] == "passed",
                "supplemental_projection_mismatch")
        if requirement in _PROBE_REQUIREMENTS:
            proof = row["observed_proof"]
            _require(proof["principal_run_counters_modified"] is False
                and all(type(proof[k]) is int and proof[k] == 0 for k in ("fixture_root_decisions", "workspace_instances",
                    "D_executions", "E_executions", "provider_calls", "external_network_calls", "subprocesses")),
                "supplemental_projection_mismatch")
            _require(proof["denied_requests"] and all(item["error"] == row["observed_refusal"]["error"]
                and item.get("http_status") == row["observed_refusal"]["http_status"] for item in proof["denied_requests"]),
                "supplemental_projection_mismatch")
            try:
                _probe_observation({**proof, "version": "ews4r.local_boundary_probe.v01", "requirement": requirement,
                    "classification": row["classification"], "nodeid": row["call_phase"]["nodeid"]},
                    {**row, "nodeid": row["call_phase"]["nodeid"]}, private_receipts=False)
            except ValueError:
                raise ValueError("supplemental_projection_mismatch") from None
            loops += proof["fixture_loopback_requests"]
    expected_counters = {"fixture_loopback_requests": loops, "fixture_root_decisions": 0, "workspace_instances": 0,
        "D_executions": 0, "E_executions": 0, "provider_calls": 0, "external_network_calls": 0, "subprocesses": 0}
    _require(value["probe_counters"] == expected_counters, "supplemental_projection_mismatch")


def _validate_documents(documents):
    _require(set(documents) == set(REQUIRED_DOCUMENTS), "required_document_coverage_mismatch")
    final = documents[REQUIRED_DOCUMENTS[-1]]
    facts = final["summary"]["facts"]
    binding = final["source_binding"]
    _require(binding["input_archive_sha256"] == INPUT_ARCHIVE_SHA256
        and binding["input_manifest_sha256"] == INPUT_MANIFEST_SHA256
        and binding["runtime_sha256"] == RUNTIME_SHA256, "source_binding_mismatch")
    _require(final["summary"]["execution_head"] == EXECUTION_HEAD, "verified_execution_head_required")
    bsep = documents["bsep_safe_projection_v01.json"]["summary"]["native_bsep"]
    _validate_native_bsep_projection(bsep)
    bsep_source = _one(binding["source_records"], "path", BSEP_SOURCE_FILE)
    _require(bsep_source["sha256"] == bsep["source_file_sha256"] == BSEP_SOURCE_SHA256
        and bsep_source["bytes"] == 1100235 and final["summary"]["native_bsep_projection_sha256"] == _digest(bsep),
        "native_bsep_source_digest_mismatch")
    supplemental = documents["adversarial_matrix_v01.json"]["summary"]
    _validate_coverage_summary(supplemental)
    _require(final["summary"]["supplemental_proof_binding"] == {
        "supplemental_manifest_sha256": supplemental["supplemental_manifest_sha256"],
        "coverage_plan_sha256": supplemental["coverage_plan_sha256"], "safe_coverage_sha256": _digest(supplemental),
        "principal_source_record_count": supplemental["principal_source_record_count"], "probe_counters": supplemental["probe_counters"]}
        and _one(supplemental["coverage"], "requirement", "EW-A12")["observed_proof"]["facts"]
            == {key: facts[key] for key in _A12_FACT_KEYS}, "supplemental_projection_mismatch")
    for name, document in documents.items():
        _require(set(document) == {"document", "projection_kind", "source_binding", "summary"}
            and document["document"] == name and document["projection_kind"] == "DERIVED_SAFE_EVIDENCE_ONLY", "safe_document_shape_invalid")
        _require(document["source_binding"]["input_archive_sha256"] == INPUT_ARCHIVE_SHA256
            and document["source_binding"]["verified_facts_sha256"] == _digest(facts), "verified_facts_binding_mismatch")
        _require(document["source_binding"]["source_records"] == binding["source_records"]
            and document["source_binding"]["source_artifacts"] == binding["source_artifacts"], "source_provenance_binding_mismatch")
        _require(document["source_binding"]["supplemental_proof_manifest_sha256"] == supplemental["supplemental_manifest_sha256"],
            "supplemental_projection_mismatch")
        for key, value in document["summary"].items():
            if key in facts:
                _require(value == facts[key], "cross_document_claim_mismatch")
        _scan(document)
    _require(facts["sidecar_sha256"] == SIDECAR_SHA256 and facts["sidecar_bytes"] == 250
        and facts["sidecar_writes"] == 1, "accepted_sidecar_claim_mismatch")
    for row in binding["source_records"]:
        _safe_path(row["path"])
        _require(_SHA.fullmatch(row["sha256"]) and type(row["bytes"]) is int, "source_reference_digest_invalid")
    for row in binding["source_artifacts"]:
        _require(_SHA.fullmatch(row["source_canonical_sha256"]) and _SHA.fullmatch(row["source_payload_sha256"]), "source_reference_digest_invalid")


def _safe_artifacts(documents):
    _validate_documents(documents)
    result = []
    # Fixed logical historical time identifies an export, not fresh permission.
    time = {"ct_session_anchor": "ews4:historical_evidence", "et_observed_at": None,
        "freshness_class": "static", "kt_asof": "2026-09-14T00:00:00Z",
        "pt_created_at": "2026-09-14T00:00:00Z", "ttl_seconds": 0,
        "valid_from": None, "valid_to": None}
    for name in REQUIRED_DOCUMENTS:
        payload = {"safe_document": documents[name]}
        artifact_id = "ews4:safe_projection:" + _digest(payload)
        obj = abi.build_kernel_artifact_v01(abi_version="v1.0", artifact_id=artifact_id,
            artifact_type="SemanticEvidence", schema_version="v1", transaction_id="ews4:safe_evidence_projection",
            owner_root_id="ews4:historical_evidence_custodian", source_component="ews4_safe_export_adapter",
            authority_class="EVIDENCE_ONLY", lifecycle_state="VALIDATED", payload=payload,
            trace_refs=(INPUT_ARCHIVE_SHA256, name), parent_refs=tuple(x["artifact_id"] for x in result[-1:]), time_envelope=time)
        result.append(abi.kernel_artifact_to_plain_dict_v01(obj))
    return result


def _assemble(documents):
    artifacts = _safe_artifacts(documents)
    kernel, refs, verification = _kernel(artifacts)
    verification["scope"] = "PUBLIC_SAFE_DERIVATIVE_GRAPH_ONLY"
    files = {name: _canonical(row) + b"\n" for name, row in zip(REQUIRED_DOCUMENTS, artifacts)}
    files[INTEGRITY_FILE] = _canonical(verification) + b"\n"
    files = dict(sorted(files.items()))
    final = documents[REQUIRED_DOCUMENTS[-1]]["summary"]
    programme = profile.build_programme_evidence_identity_v01(programme_id="radiolaria_ews", programme_version="v01")
    execution = profile.build_domain_execution_identity_v01(programme_identity=programme,
        domain_id="ephemeral_workspace", execution_head=final["execution_head"],
        source_task_id="ews3r2_temporal_browser", run_id="ews3r2_browser_run_01", report_id=INPUT_ARCHIVE_SHA256)
    attempt = profile.build_live_attempt_identity_v01(programme_identity=programme,
        domain_execution_identity=execution, attempt_number=1, package_id="ews4:" + _digest(documents),
        logical_package_ref="packages/ephemeral_workspace/ews4", output_directory_ref="public_safe_package",
        provider_mode="deterministic_fixture", model_id="local-semantic-rules-v01", expected_actor_count=3, provider_call_budget=0)
    source_records = []
    artifact_records = []
    for name in files:
        ec = "CRYPTOGRAPHIC_INTEGRITY" if name == INTEGRITY_FILE else "EXECUTED_DETERMINISTIC_RUNTIME"
        trace = (kernel.manifest_hash, name)
        source = profile.build_safe_source_record_v01(source_id="ews4:source:" + name,
            source_type="PUBLIC_SAFE_DERIVATIVE", evidence_class=ec,
            canonical_projection=_json(files[name]), media_type="application/json", trace_refs=trace,
            contains_raw_prompt=False, contains_raw_provider_response=False, secret_scan_passed=True,
            observed_provider_call_count=0, observed_network_call_count=0, observed_gemini_call_count=0, real_world_effects_count=0)
        source_records.append(source)
        if name != INTEGRITY_FILE:
            row = artifacts[REQUIRED_DOCUMENTS.index(name)]
            artifact_records.append(profile.build_evidence_artifact_record_v01(
                artifact_id=row["artifact_id"], artifact_type=row["artifact_type"], evidence_class=ec,
                source_record_ids=(source.source_record_id,), canonical_projection=row,
                authority_class="EVIDENCE_ONLY", owner_root_id=row["owner_root_id"], trace_refs=trace,
                created_authority_count=0, created_permission_count=0, real_world_effects_count=0))
    projection = profile.build_domain_evidence_projection_v01(programme_identity=programme,
        domain_execution_identity=execution, attempt_identity=attempt, source_records=tuple(source_records),
        artifact_records=tuple(artifact_records), kernel_artifact_refs=refs, causal_consumption_refs=(),
        evidence_refs=(INPUT_ARCHIVE_SHA256, final["candidate_source_ledger_sha256"], kernel.manifest_hash), limitation_refs=_LIMITATIONS)
    _require(not profile.validate_domain_evidence_projection_v01(projection) and projection.status == "PASS", "domain_projection_failed")
    contents = tuple(files.values())
    records = tuple(package.build_safe_file_record_v01(logical_path=name, media_type="application/json",
        content_bytes=data, evidence_class=source.evidence_class, source_record_ids=(source.source_record_id,),
        terminal_newline_required=True, secret_scan_passed=True) for (name, data), source in zip(files.items(), source_records))
    manifest = package.build_sealed_package_manifest_v01(domain_projection=projection,
        safe_file_records=records, safe_file_contents=contents, kernel_manifest_hash=kernel.manifest_hash)
    context = {"manifest": manifest, "domain_projection": projection, "safe_file_contents": contents}
    _require(not package.validate_sealed_package_manifest_v01(manifest, domain_projection=projection, safe_file_contents=contents)
        and manifest.package_status == "SELF_CONSISTENT_UNANCHORED", "sealed_package_failed")
    publication = anchor.build_external_anchor_publication_v01(**context, publication_base_head=final["execution_head"])
    _require(not anchor.validate_external_anchor_publication_v01(publication, **context), "publication_invalid")
    return files, context, publication, verification


@_fail_closed
def _write_package(documents, output_dir):
    """Internal test seam: genuine common construction, never a validation bypass."""
    files, context, publication, verification = _assemble(documents)
    target = Path(output_dir)
    _no_symlink_ancestors(target)
    _require(not target.exists(), "output_already_exists")
    _require(target.parent.is_dir() and not target.parent.is_symlink(), "output_parent_invalid")
    target.mkdir()
    for name, data in files.items():
        (target / name).write_bytes(data)
    manifest = package.sealed_package_manifest_to_plain_dict_v01(context["manifest"],
        domain_projection=context["domain_projection"], safe_file_contents=context["safe_file_contents"])
    (target / MANIFEST_FILE).write_bytes(_canonical(manifest) + b"\n")
    publication_plain = anchor.external_anchor_publication_to_plain_dict_v01(publication, **context)
    return {"status": "SELF_CONSISTENT_UNANCHORED", "errors": [], "anchor_verified": False, "publication": publication_plain,
        "manifest": manifest, "domain_projection": profile.domain_evidence_projection_to_plain_dict_v01(context["domain_projection"]),
        "kernel": verification, "file_count": len(files), "artifact_count": len(REQUIRED_DOCUMENTS),
        "independent_lead_pin": "PENDING_REVIEW_OF_ACTUAL_PUBLICATION_ID", "limitations": list(_LIMITATIONS)}


@_fail_closed
def export_package(input_root, output_dir, *, execution_head, source_ledger_path,
                   supplemental_proof_root, expected_supplemental_manifest_sha256, expected_input_manifest_sha256=None):
    """Export exact accepted inputs. Output must be a new directory."""
    _require(execution_head == EXECUTION_HEAD, "verified_execution_head_required")
    ledger_sha, ledger_rows = _source_ledger(source_ledger_path)
    read, sources = _private_inputs(input_root, expected_input_manifest_sha256 or INPUT_MANIFEST_SHA256)
    facts, graphs, provenance, roles, native, bsep = _project_inputs(read)
    supplemental = _load_supplemental_proof(supplemental_proof_root, expected_supplemental_manifest_sha256,
        source_ledger_rows=ledger_rows, principal_sources=sources, principal_facts=facts)
    documents = _documents(facts, graphs, provenance, roles, native, bsep, supplemental, sources,
        ledger_sha, ledger_rows, execution_head)
    result = _write_package(documents, output_dir)
    result["private_native_bsep_validation"] = bsep["offline_validation"]
    result["supplemental_proof_binding"] = documents[REQUIRED_DOCUMENTS[-1]]["summary"]["supplemental_proof_binding"]
    result["private_original_graph_verification"] = graphs
    result["source_records"] = sorted(sources.values(), key=lambda r: r["path"])
    result["candidate_source_ledger_sha256"] = ledger_sha
    return result


def _reopen(package_dir):
    root = Path(package_dir)
    _require(root.is_dir() and not root.is_symlink(), "package_directory_required")
    expected = set(REQUIRED_DOCUMENTS) | {INTEGRITY_FILE, MANIFEST_FILE}
    entries = list(root.iterdir())
    _require({p.name for p in entries} == expected, "package_file_coverage_mismatch")
    saved = {name: _read(root, name) for name in sorted(expected)}
    decoded = {name: _json(data, canonical=True) for name, data in saved.items()}
    for value in decoded.values():
        _scan(value)
    documents = {name: decoded[name]["payload"]["safe_document"] for name in REQUIRED_DOCUMENTS}
    files, context, publication, verification = _assemble(documents)
    _require(all(saved[name] == data for name, data in files.items()), "safe_artifact_or_kernel_mismatch")
    manifest_plain = package.sealed_package_manifest_to_plain_dict_v01(context["manifest"],
        domain_projection=context["domain_projection"], safe_file_contents=context["safe_file_contents"])
    _require(decoded[MANIFEST_FILE] == manifest_plain, "sealed_manifest_mismatch")
    return context, publication, verification


@_fail_closed
def verify_package(package_dir, *, publication_path=None, expected_anchor=None, require_anchor=False):
    """Independently reopen a directory; the expected pin is never inferred."""
    _require(type(require_anchor) is bool, "require_anchor_invalid")
    _require(not require_anchor or expected_anchor is not None, "external_expected_anchor_required")
    source, publication, kernel = _reopen(package_dir)
    publication_plain = anchor.external_anchor_publication_to_plain_dict_v01(publication, **source)
    if publication_path is not None:
        path = Path(publication_path)
        _require(_json(_read(path.parent, path.name), canonical=True) == publication_plain, "detached_publication_mismatch")
    # A second independent disk read is the reconstructed common replay side.
    reconstructed, _, _ = _reopen(package_dir)
    result = {"status": "SELF_CONSISTENT_UNANCHORED", "errors": [], "anchor_verified": False, "package_status": source["manifest"].package_status,
        "publication": publication_plain, "kernel": kernel, "sealed_replay": None,
        "anchor_verification": None, "independent_lead_pin": "PENDING_REVIEW_OF_ACTUAL_PUBLICATION_ID",
        "replay_scope": "PUBLIC_SAFE_DERIVATIVE_GRAPH_ONLY", "declared_forbidden_calls_and_effects": 0,
        "observed_call_proof": "requires_external_instrumented_harness", "limitations": list(_LIMITATIONS)}
    if expected_anchor is not None:
        _require(type(expected_anchor) is str and _SHA.fullmatch(expected_anchor), "external_expected_anchor_invalid")
        av = anchor.build_anchored_package_verification_v01(anchor_publication=publication,
            **source, supplied_anchor_publication_id=expected_anchor)
        _require(not anchor.validate_anchored_package_verification_v01(av, anchor_publication=publication,
            **source, supplied_anchor_publication_id=expected_anchor), "anchor_contract_invalid")
        _require(av.verification_status == "ANCHORED_PASS", "external_anchor_mismatch")
        replay_context = {"source_manifest": source["manifest"], "source_domain_projection": source["domain_projection"],
            "source_safe_file_contents": source["safe_file_contents"], "anchor_publication": publication,
            "anchored_verification": av, "supplied_anchor_publication_id": expected_anchor,
            "reconstructed_manifest": reconstructed["manifest"], "reconstructed_domain_projection": reconstructed["domain_projection"],
            "reconstructed_safe_file_contents": reconstructed["safe_file_contents"]}
        replayed = replay.build_sealed_replay_evidence_v01(**replay_context, evidence_refs=("independent_disk_reopen", expected_anchor))
        _require(not replay.validate_sealed_replay_evidence_v01(replayed, **replay_context)
            and replayed.replay_status == "PASS", "sealed_replay_failed")
        result.update(status="ANCHORED_PASS", anchor_verified=True, independent_lead_pin="EXPLICIT_CALLER_PIN_PROVENANCE_EXTERNAL_TO_PACKAGE",
            anchor_verification=anchor.anchored_package_verification_to_plain_dict_v01(av,
                anchor_publication=publication, **source, supplied_anchor_publication_id=expected_anchor),
            sealed_replay=replay.sealed_replay_evidence_to_plain_dict_v01(replayed, **replay_context))
    return result
