"""Five missing EWS boundaries; tiny fixtures, production validators/handlers.

Loopback handlers run in this test process so file-sink counters observe the
executing handler threads. This is not a subprocess sandbox or a Workspace run.
"""
import base64
import contextlib
import copy
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import threading
import time

from PIL import Image
import pytest

from hedgehog.domains.ephemeral_workspace import contracts_v01 as c
from hedgehog.domains.ephemeral_workspace import local_services_v01 as services
from hedgehog.domains.ephemeral_workspace import semantic_roles_v01 as roles
from hedgehog.domains.ephemeral_workspace import media_v01 as media
from hedgehog.domains.ephemeral_workspace import semantic_adapter_v01 as semantic
from hedgehog.domains.ephemeral_workspace import kernel_adapter_v01 as kernel


def _sha(data): return hashlib.sha256(data).hexdigest()
def _write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


@pytest.fixture
def evidence(request):
    directory = Path(os.environ["EWS4R_PROBE_EVIDENCE"])
    directory.mkdir(parents=True, exist_ok=True)
    def record(requirement, result):
        sources = []
        candidate = Path(__file__).resolve().parents[1]
        for label, path in [("test", Path(__file__)), *[(m.__name__, Path(m.__file__)) for m in (c, services, roles, media, semantic, kernel)]]:
            path = path.resolve()
            assert path.is_relative_to(candidate)
            data = path.read_bytes()
            sources.append({"module": label, "path": path.relative_to(candidate).as_posix(),
                            "sha256": _sha(data), "bytes": len(data)})
        result.update(version="ews4r.local_boundary_probe.v01", requirement=requirement,
            nodeid=request.node.nodeid, source_pins=sources,
            principal_run_counters_modified=False, fixture_root_decisions=0,
            workspace_instances=0, D_executions=0, E_executions=0,
            provider_calls=0, external_network_calls=0, subprocesses=0)
        _write(directory / (requirement + ".json"), result)
    return record


def _image():
    stream = io.BytesIO()
    Image.new("RGB", (8, 8), (25, 90, 145)).save(stream, format="PNG")
    return stream.getvalue()


@contextlib.contextmanager
def _service(role, tmp_path, monkeypatch, asset_id="asset:1"):
    source = tmp_path / "fixture_source.png"
    source.write_bytes(_image())
    original = source.read_bytes()
    started = time.monotonic()
    initial_threads = set(threading.enumerate())
    config = dict(role=role, session="fixture:local_probe", deadline=started + 60,
                  token="fixture_rpc_credential", read_token="fixture_read_credential",
                  nonce="fixture_birth_marker", parent_pid=os.getppid(),
                  minimize="preview_without_metadata", preview="fit",
                  assets={asset_id: [str(source), _sha(original)]}, pcm_chunks=[])
    servers, errors, births = [], [], []
    ready = threading.Event()
    owner_thread = threading.get_ident()
    counts = {"source_read_attempts": 0, "source_write_attempts": 0, "render_dispatches": 0}
    originals = (io.open, open, os.open, services.render, services.ThreadingHTTPServer)

    def path_is_source(value):
        return isinstance(value, (str, bytes, os.PathLike)) and Path(os.fsdecode(value)).absolute() == source.absolute()

    def observed_open(original_open):
        def call(file, mode="r", *args, **kwargs):
            if threading.get_ident() != owner_thread and path_is_source(file):
                counts["source_write_attempts" if any(x in str(mode) for x in "wax+") else "source_read_attempts"] += 1
            return original_open(file, mode, *args, **kwargs)
        return call

    def observed_os_open(file, flags, *args, **kwargs):
        if threading.get_ident() != owner_thread and path_is_source(file):
            writing = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            counts["source_write_attempts" if writing else "source_read_attempts"] += 1
        return originals[2](file, flags, *args, **kwargs)

    def observed_render(*args, **kwargs):
        counts["render_dispatches"] += 1
        return originals[3](*args, **kwargs)

    def server_factory(*args, **kwargs):
        server = originals[4](*args, **kwargs)
        servers.append(server)
        ready.set()
        return server

    def observe_birth(value, **kwargs):
        birth = json.loads(value)
        births.append({"same_process": birth["pid"] == os.getpid(),
                       "role_matches": birth["role"] == role,
                       "birth_matches": birth["nonce"] == config["nonce"]})

    def run():
        try:
            services.worker(config)
        except BaseException as error:
            errors.append(type(error).__name__)
            ready.set()

    with monkeypatch.context() as patch:
        patch.setattr(io, "open", observed_open(originals[0]))
        patch.setattr("builtins.open", observed_open(originals[1]))
        patch.setattr(os, "open", observed_os_open)
        patch.setattr(services, "render", observed_render)
        patch.setattr(services, "ThreadingHTTPServer", server_factory)
        patch.setattr(services, "print", observe_birth, raising=False)
        thread = threading.Thread(target=run, name="ews4r-fixture-worker", daemon=False)
        thread.start()
        assert ready.wait(5) and servers and not errors
        sequence = 0
        calls = []

        def request(method, path, *, operation=None, args=None):
            nonlocal sequence
            headers = {"Authorization": "Bearer " + (config["read_token"] if method == "GET" else config["token"])}
            payload = None
            if method == "POST":
                payload = c.canonical(dict(version=c.VERSION, session=config["session"],
                    sequence=sequence + 1, op=operation, args=args))
                headers["Content-Type"] = "application/json"
            connection = http.client.HTTPConnection("127.0.0.1", servers[0].server_port, timeout=5)
            try:
                connection.request(method, path, body=payload, headers=headers)
                response = connection.getresponse()
                data = response.read()
                decoded = json.loads(data) if response.getheader("Content-Type") == "application/json" else None
                result = {"method": method, "path": path, "operation": operation,
                          "credential_role": role + ("_read" if method == "GET" else "_rpc"),
                          "session_matches_fixture": True, "next_sequence": sequence + 1 if payload else None,
                          "http_status": response.status, "error": decoded.get("error") if isinstance(decoded, dict) else None,
                          "response_bytes_sha256": _sha(data),
                          "request_payload_sha256": None if payload is None else _sha(payload),
                          "argument_keys": sorted(args) if isinstance(args, dict) else [],
                          "requested_logical_asset": args.get("asset") if isinstance(args, dict) else None,
                          "arguments_sha256": c.digest(args) if args is not None else None}
                calls.append(result)
                if method == "POST" and response.status == 200:
                    sequence += 1
                return result, decoded, data
            finally:
                connection.close()

        state = {"source": source, "original_sha256": _sha(original), "counts": counts,
                 "calls": calls, "births": births, "request": request, "role": role}
        try:
            yield state
        finally:
            if thread.is_alive():
                reply, _, _ = request("POST", "/rpc", operation="close", args={})
                assert reply["http_status"] == 200
            thread.join(5)
            assert not thread.is_alive() and not errors
            owned_threads = [item for item in threading.enumerate() if item not in initial_threads]
            for item in owned_threads:
                item.join(2)
            assert not any(item.is_alive() for item in owned_threads)
            state["cleanup"] = {"worker_thread_joined": True, "server_closed": servers[0].fileno() == -1,
                                "owned_subprocesses": 0, "all_created_threads_joined": True,
                                "source_after_sha256": _sha(source.read_bytes()), "seconds": time.monotonic() - started}


def _probe_summary(state, valid, denied, before):
    after = dict(state["counts"])
    return {"classification": "CURRENT_LOCAL_BOUNDARY_PROBE",
            "instrumentation_scope": "IN_PROCESS_PRODUCTION_HANDLER_THREADS",
            "fixture_scope": "OWNED_LOOPBACK_SERVICE_WITH_GENERATED_8X8_PNG_NO_WORKSPACE",
            "valid_counterpart": valid, "denied_requests": denied,
            "observed_sink_attempts": {k: after[k] - before[k] for k in before},
            "canary_before_sha256": state["original_sha256"],
            "canary_after_sha256": _sha(state["source"].read_bytes()),
            "fixture_birth": state["births"], "fixture_loopback_requests": len(state["calls"])}


def test_A01_explicit_raw_read_is_denied_after_valid_derived_frame(tmp_path, monkeypatch, evidence):
    with _service("display", tmp_path, monkeypatch) as state:
        png = _image()
        put, _, _ = state["request"]("POST", "/rpc", operation="put", args={
            "png": base64.b64encode(png).decode(), "sha256": _sha(png), "frame_ref": "ews:frame:fixture"})
        valid, _, returned = state["request"]("GET", "/frame/ews:frame:fixture")
        assert put["http_status"] == valid["http_status"] == 200 and returned == png
        before = dict(state["counts"])
        denied, _, _ = state["request"]("GET", "/sources/asset:1/raw")
        result = _probe_summary(state, valid, [denied], before)
    result["cleanup"] = state["cleanup"]
    result["fixture_loopback_requests"] = len(state["calls"])
    result["all_request_records"] = state["calls"]
    evidence("EW-A01", result)
    assert denied["http_status"] == 403 and denied["error"] == "derived_frame_only"
    assert not any(result["observed_sink_attempts"].values())
    assert result["canary_before_sha256"] == result["canary_after_sha256"] == result["cleanup"]["source_after_sha256"]


def test_A03_renderer_source_overwrite_is_denied_with_valid_envelope(tmp_path, monkeypatch, evidence):
    with _service("media", tmp_path, monkeypatch) as state:
        valid, _, _ = state["request"]("POST", "/rpc", operation="render", args={
            "asset": "asset:1", "exposure": 0, "crop": "ORIGINAL", "preview": "fit"})
        assert valid["http_status"] == 200
        assert state["counts"]["source_read_attempts"] >= 1 and state["counts"]["render_dispatches"] == 1
        before = dict(state["counts"])
        denied, _, _ = state["request"]("POST", "/rpc", operation="write_source", args={
            "asset": "asset:1", "content_base64": base64.b64encode(b"forbidden overwrite").decode()})
        result = _probe_summary(state, valid, [denied], before)
    result["cleanup"] = state["cleanup"]
    result["fixture_loopback_requests"] = len(state["calls"])
    result["all_request_records"] = state["calls"]
    evidence("EW-A03", result)
    assert denied["http_status"] == 403 and denied["error"] == "service_operation_not_allowed"
    assert not any(result["observed_sink_attempts"].values())
    assert result["canary_before_sha256"] == result["canary_after_sha256"] == result["cleanup"]["source_after_sha256"]


def test_A04_explicit_shell_and_file_operations_stop_at_typed_boundary(tmp_path, monkeypatch, evidence):
    allowed = c.BASE + c.EDIT + ("OPEN", "REQUEST_SAVE", "SAVE", "END")
    canary = tmp_path / "dispatch_canary.json"
    canary.write_bytes(b"fixture unchanged")
    initial = canary.read_bytes()
    dispatches = []
    production_dispatches = []
    def forbidden_dispatch(*args, **kwargs):
        production_dispatches.append("attempted")
        raise AssertionError("probe_forbids_production_dispatch")
    monkeypatch.setattr(kernel, "dispatch", forbidden_dispatch)
    def parsed_then_fixture_dispatch(value):
        parsed = c.command(value, allowed)
        dispatches.append(parsed)
        canary.write_bytes(c.canonical(parsed))
        return "fixture_dispatch_counterpart"
    assert parsed_then_fixture_dispatch({"op": "NEXT", "value": None}) == "fixture_dispatch_counterpart"
    initial = canary.read_bytes()
    dispatches.clear()
    attempts = []
    for operation in ("SHELL", "EXEC", "READ_FILE", "WRITE_FILE"):
        try:
            returned = parsed_then_fixture_dispatch({"op": operation, "value": "fixture-only request"})
        except ValueError as error:
            attempts.append({"operation": operation, "error": str(error), "returned": None})
        else:
            attempts.append({"operation": operation, "error": None, "returned": returned})
    evidence("EW-A04", {"classification": "CURRENT_LOCAL_BOUNDARY_PROBE",
        "instrumentation_scope": "PRODUCTION_PURE_VALIDATOR_AND_FIXTURE_CONTINUATION_CANARY",
        "entrypoint": "contracts_v01.command", "denied_requests": attempts,
        "valid_counterpart": {"operation": "NEXT", "accepted": True, "fixture_dispatch_count": 1, "fixture_file_writes": 1},
        "denied_fixture_dispatches": len(dispatches), "observed_production_dispatch_attempts": len(production_dispatches),
        "canary_before_sha256": _sha(initial), "canary_after_sha256": _sha(canary.read_bytes()),
        "fixture_loopback_requests": 0})
    assert all(row["error"] == "operation_not_allowed" for row in attempts)
    assert not dispatches and not production_dispatches and canary.read_bytes() == initial


def test_A09_audio_role_cannot_request_video_source_render(tmp_path, monkeypatch, evidence):
    with _service("audio", tmp_path, monkeypatch, asset_id="video:source:fixture") as state:
        valid, body, _ = state["request"]("POST", "/rpc", operation="observe", args={})
        assert valid["http_status"] == 200 and body["available"] is True
        before = dict(state["counts"])
        denied, _, _ = state["request"]("POST", "/rpc", operation="render", args={
            "asset": "video:source:fixture", "exposure": 0, "crop": "ORIGINAL", "preview": "fit"})
        result = _probe_summary(state, valid, [denied], before)
    result["fixture_scope"] = "INERT_8X8_PNG_CANARY_NAMED_VIDEO_SOURCE_ROLE_REFUSAL_PRECEDES_DECODING"
    result["cleanup"] = state["cleanup"]
    result["fixture_loopback_requests"] = len(state["calls"])
    result["all_request_records"] = state["calls"]
    evidence("EW-A09", result)
    assert denied["http_status"] == 403 and denied["error"] == "service_operation_not_allowed"
    assert not any(result["observed_sink_attempts"].values())
    assert result["canary_before_sha256"] == result["canary_after_sha256"] == result["cleanup"]["source_after_sha256"]


def test_A11_model_supplied_device_ids_and_topology_edges_are_rejected(monkeypatch, evidence):
    context = {"version": c.VERSION, "bsep": {"needs": ["browse"]},
               "route_acceptance": "non_authorizing_fixture_context_only"}
    examples = [
        (roles.ROLES[0], {"needs": ["browse"], "uncertainty": []}, "device_ids", ["fixture_device"]),
        (roles.ROLES[1], {"preview": "fit", "cleanup": "on_end", "save": "selected_only",
                          "phases": ["preview", "interact", "confirm_save", "close"]},
         "topology_edges", [{"from": "model_node", "to": "fixture_device"}]),
    ]
    attempts = []
    accepted = []
    materialization_attempts = []
    def forbidden_materialize(*args, **kwargs):
        materialization_attempts.append("attempted")
        raise AssertionError("probe_forbids_semantic_materialization")
    monkeypatch.setattr(kernel, "materialize", forbidden_materialize)
    for role, valid, field, injected in examples:
        assert roles.validate(role, copy.deepcopy(valid), context) == valid
        accepted.append({"role": role, "valid_closed_shape_accepted": True})
        malicious = {**valid, field: injected}
        try:
            returned = roles.validate(role, malicious, context)
        except ValueError as error:
            attempts.append({"role": role, "injected_field": field, "error": str(error), "accepted": False})
        else:
            attempts.append({"role": role, "injected_field": field, "error": None, "accepted": returned == malicious})
    evidence("EW-A11", {"classification": "CURRENT_LOCAL_BOUNDARY_PROBE",
        "instrumentation_scope": "PRODUCTION_PURE_SEMANTIC_DTO_VALIDATOR",
        "entrypoint": "semantic_roles_v01.validate", "denied_requests": attempts,
        "valid_counterparts": accepted, "fixture_context_creates_authority": False,
        "observed_semantic_materialization_attempts": len(materialization_attempts), "fixture_loopback_requests": 0})
    assert not materialization_attempts
    assert all(row["error"] == "semantic_closed_shape" and not row["accepted"] for row in attempts)
