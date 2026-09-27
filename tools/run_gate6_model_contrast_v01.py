"""Finite Testflix QUALITY contrast; default is offline preparation, never live.

The isolated-process SDK interposition is experimental reference instrumentation.
It preserves the accepted exact provider class, prompt and SDK response object.
External authorization is an operator input, not authority granted by a receipt.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gemini-2.5-flash"
HOST = "generativelanguage.googleapis.com"
FIXTURE_SHA = "ce96b3d3d51b5b41ebd82dc7850a70e5b7d00fbb9e9587a63e549b0b9971c673"
ROLES = ("intent_interpreter", "provider_terms_analyst", "client_plan_selector", "contract_reviewer")
LIMITS = dict(generations=4, counts=4, external_calls=8, input_per_call=4096,
              input_total=16384, output_per_call=2048, output_total=8192,
              thinking_budget=0, candidate_count=1, retries=0, request_seconds=180, task_seconds=1800)
_INTERPOSED = False


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def quality_input():
    raw = (ROOT / "demo/testflix_fixtures_v01.json").read_bytes()
    require(len(raw) == 914 and hashlib.sha256(raw).hexdigest() == FIXTURE_SHA, "model_fixture_pin")
    value = json.loads(raw)
    require(value["preference"] == "AD_FREE", "base_preference")
    value["preference"] = "QUALITY"
    return value


def oracle(value):
    allowed = [p for p in value["catalog"] if p["price_minor"] <= value["hard_ceiling_minor"]]
    selected = sorted(allowed, key=lambda p: (-p["resolution"], p["ads"], p["price_minor"], p["plan_id"]))[0]
    return dict(plan_id=selected["plan_id"], amount_minor=selected["price_minor"],
                resolution=selected["resolution"], currency=value["currency"])


def preparation():
    from demo.run_gate6_reference_v01 import source_closure, BASE
    return dict(profile="G6_MODEL_CONTRAST_V01", base=BASE, model=MODEL, limits=LIMITS,
                source_closure_sha256=digest(source_closure()), input=quality_input(),
                input_sha256=digest(quality_input()), oracle=oracle(quality_input()),
                status="MODEL_LIVE_NOT_AUTHORIZED_NOT_RUN", provider_calls=0,
                controlled_provider="ControlledRolesV01", live_provider="LiveSemanticProviderV01",
                endpoint="https://" + HOST + "/v1beta", money="NOT_ESTIMATED_RECHECK_BEFORE_AUTHORIZATION")


def check_authorization(path, pin, output):
    require(path is not None and type(pin) is str, "MODEL_LIVE_NOT_AUTHORIZED_NOT_RUN")
    p = Path(path).resolve(); out = Path(output).resolve()
    require(p.is_file() and not Path(path).is_symlink() and ROOT not in p.parents and out not in p.parents,
            "external_authorization_required")
    raw = p.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin, "authorization_pin")
    auth = json.loads(raw); plan = preparation()
    require(set(auth) == {"profile", "run_id", "approved", "expires_epoch", "plan_sha256", "limits", "model", "output_directory"}, "authorization_shape")
    require(auth["profile"] == "G6_MODEL_EXTERNAL_AUTHORIZATION_V01" and auth["approved"] is True and
            type(auth["run_id"]) is str and bool(auth["run_id"]), "authorization_identity")
    require(type(auth["expires_epoch"]) in (int, float) and time.time() < auth["expires_epoch"], "authorization_expired")
    require(auth["plan_sha256"] == digest(plan) and auth["limits"] == LIMITS and auth["model"] == MODEL,
            "authorization_frozen_plan")
    require(auth["output_directory"] == str(out), "authorization_output_binding")
    return auth


class BudgetLedger:
    """Append/fsync reservations survive crashes; no automatic partial-chain resume."""
    def __init__(self, directory, *, classification):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = (self.directory / "budget.lock").open("a")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.path = self.directory / "budget.jsonl"
            require(not self.path.exists(), "budget_existing_chain_no_automatic_resume")
            self.file = self.path.open("x")
            self.rows = []
            self.started = time.monotonic()
            self.append(dict(event="OPEN", classification=classification, limits=LIMITS, pid=os.getpid()))
            directory_fd = os.open(self.directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except BaseException:
            self.lock.close()
            raise
    def append(self, row):
        self.file.write(json.dumps(dict(row, ordinal=len(self.rows)+1, utc_epoch=time.time()), sort_keys=True)+"\n")
        self.file.flush(); os.fsync(self.file.fileno()); self.rows.append(row)
    def reserve_count(self, role, body):
        require(time.monotonic()-self.started < LIMITS["task_seconds"], "model_task_deadline")
        reservations = [r for r in self.rows if r["event"] == "COUNT_RESERVED"]
        complete = [r for r in self.rows if r["event"] == "GENERATION_COMPLETE"]
        require(len(reservations) < 4 and role == ROLES[len(reservations)], "model_role_or_fifth_attempt")
        require(len(complete) == len(reservations), "prior_chain_incomplete_no_retry")
        self.append(dict(event="COUNT_RESERVED", role=role, body=body, request_sha256=digest(body)))
    def count_complete(self, role, count):
        require(type(count) is int and 0 < count <= 4096, "input_token_cap_or_ambiguous")
        used = sum(r["tokens"] for r in self.rows if r["event"] == "COUNT_COMPLETE")
        require(used+count <= 16384, "aggregate_input_token_cap")
        self.append(dict(event="COUNT_COMPLETE", role=role, tokens=count))
    def reserve_generation(self, role, body):
        require(self.rows[-1]["event"] == "COUNT_COMPLETE" and self.rows[-1]["role"] == role, "count_required")
        require(sum(r["event"] == "GENERATION_RESERVED" for r in self.rows) < 4, "generation_budget")
        self.append(dict(event="GENERATION_RESERVED", role=role, body=body, request_sha256=digest(body), max_output_tokens=2048))
    def close(self):
        self.file.close(); self.lock.close()


def bounded_config(config):
    require(type(config) is dict and set(config) == {"response_mime_type", "temperature", "candidate_count", "system_instruction"}, "accepted_adapter_config_shape")
    require(config["candidate_count"] == 1 and config["response_mime_type"] == "application/json" and config["temperature"] == 0,
            "accepted_adapter_config_values")
    return dict(config, max_output_tokens=2048, thinking_config={"thinking_budget": 0},
                automatic_function_calling={"disable": True})


def transport(underlying, ledger):
    import httpx
    class BudgetTransport(httpx.BaseTransport):
        def handle_request(self, request):
            require(request.method == "POST" and request.url.scheme == "https" and request.url.host == HOST and
                    request.url.port in (None, 443) and not request.url.query and not request.url.userinfo and
                    request.url.path == "/v1beta/models/"+MODEL+":generateContent", "developer_endpoint_only")
            body = json.loads(request.content)
            require(set(body) == {"contents", "systemInstruction", "generationConfig"}, "wire_body_shape")
            cfg = body["generationConfig"]
            require(cfg == {"responseMimeType": "application/json", "temperature": 0, "candidateCount": 1,
                            "maxOutputTokens": 2048, "thinkingConfig": {"thinking_budget": 0}}, "wire_generation_limits")
            require(body["systemInstruction"] and len(body["contents"]) == 1 and len(body["contents"][0]["parts"]) == 1, "wire_actual_prompt")
            role = json.loads(body["contents"][0]["parts"][0]["text"])["duty"]
            count_body = {"generateContentRequest": dict(model="models/"+MODEL, **body)}
            ledger.reserve_count(role, count_body)
            # The outer count body has no conflicting model/contents. Keys stay in headers.
            count_request = httpx.Request("POST", "https://"+HOST+"/v1beta/models/"+MODEL+":countTokens",
                headers={"content-type": "application/json", "x-goog-api-key": request.headers["x-goog-api-key"]},
                content=canonical(count_body), extensions=request.extensions)
            try:
                counted = underlying.handle_request(count_request)
                counted.read()
                require(counted.status_code == 200, "count_http_failure")
                value = json.loads(counted.content)
                count = value.get("totalTokens")
                ledger.count_complete(role, count)
                counted.close()
                ledger.reserve_generation(role, body)
                generated = underlying.handle_request(request)
                # No redirects or implicit retries; SDK receives the actual response.
                require(not 300 <= generated.status_code < 400, "redirect_refused")
                ledger.append(dict(event="GENERATION_HTTP_RETURN", role=role, http_status=generated.status_code))
                return generated
            except BaseException as error:
                ledger.append(dict(event="TRANSPORT_FAILURE", role=role, exception_type=type(error).__name__, retry=False))
                raise
        def close(self):
            underlying.close()
    return BudgetTransport()


def validate_response(response, ledger):
    usage = response.usage_metadata
    names = ("prompt_token_count", "candidates_token_count", "thoughts_token_count", "cached_content_token_count", "total_token_count")
    values = {k: getattr(usage, k, None) for k in names}
    candidates = response.candidates or []
    reasons = [getattr(c.finish_reason, "value", c.finish_reason) for c in candidates]
    observed = dict(event="PROVIDER_USAGE", model_version=response.model_version, finish_reasons=reasons,
                    usage=values, missing_usage=[k for k, v in values.items() if v is None])
    ledger.append(observed)
    require(response.model_version == MODEL and len(candidates) == 1 and reasons == ["STOP"], "model_identity_or_truncation")
    require(all(type(values[k]) is int and values[k] >= 0 for k in ("prompt_token_count", "candidates_token_count", "total_token_count")), "usage_missing")
    require(values["thoughts_token_count"] in (None, 0), "thinking_budget_exceeded")
    require(values["cached_content_token_count"] is None or type(values["cached_content_token_count"]) is int and
            0 <= values["cached_content_token_count"] <= values["prompt_token_count"], "cached_usage_inconsistent")
    count = next(r["tokens"] for r in reversed(ledger.rows) if r["event"] == "COUNT_COMPLETE")
    require(0 < values["prompt_token_count"] <= count <= 4096 and 0 < values["candidates_token_count"] <= 2048 and
            values["total_token_count"] == values["prompt_token_count"] + values["candidates_token_count"], "usage_limits_or_inconsistent")
    role = next(r["role"] for r in reversed(ledger.rows) if r["event"] == "GENERATION_RESERVED")
    ledger.append(dict(event="GENERATION_COMPLETE", role=role, usage=values))
    return response


@contextmanager
def sdk_interposition(ledger, *, offline_transport=None):
    """Only Client construction and generation configuration/accounting are wrapped."""
    global _INTERPOSED
    from google import genai
    import httpx
    require(not _INTERPOSED and threading.current_thread() is threading.main_thread() and threading.active_count() == 1,
            "interposition_concurrency_or_conflict")
    require(genai.Client.__module__ == "google.genai.client", "sdk_factory_conflict")
    forbidden = ("GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GEMINI_BASE_URL", "GOOGLE_VERTEX_BASE_URL", "GOOGLE_GENAI_BASE_URL")
    require(not any(os.environ.get(k) for k in forbidden), "conflicting_provider_routing")
    original = genai.Client
    def factory(*args, **kwargs):
        require(not args and set(kwargs) == {"api_key", "http_options"} and
                kwargs["http_options"] == {"timeout": 180000, "retry_options": {"attempts": 1}}, "adapter_client_shape")
        underlying = offline_transport if offline_transport is not None else httpx.HTTPTransport(retries=0, trust_env=False)
        http = httpx.Client(transport=transport(underlying, ledger), timeout=180, follow_redirects=False, trust_env=False)
        client = original(vertexai=False, api_key=kwargs["api_key"], http_options={
            "api_version": "v1beta", "base_url": "https://"+HOST, "timeout": 180000,
            "retry_options": {"attempts": 1}, "httpx_client": http})
        class ClientScope:
            def generate_content(self, *, model, contents, config):
                require(model == MODEL and type(contents) is str, "model_no_fallback")
                response = client.models.generate_content(model=model, contents=contents, config=bounded_config(config))
                return validate_response(response, ledger)
            def __enter__(self):
                return SimpleNamespace(models=SimpleNamespace(generate_content=self.generate_content))
            def __exit__(self, *exc):
                try:
                    client.close()
                finally:
                    http.close()
        return ClientScope()
    try:
        _INTERPOSED = True
        genai.Client = factory
        yield
    finally:
        genai.Client = original
        _INTERPOSED = False


def native_functions():
    from hedgehog.kernel import root_decision_v01 as root, effect_firewall_v01 as firewall
    from hedgehog import work_execution_host_v01 as host
    from hedgehog.domains.testflix import mock_world_v01 as world
    from hedgehog.domains.testflix.semantic_roles_v01 import ControlledRolesV01
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01
    functions = dict(Root=root.decide_root_v01, Work=host.execute_admitted_pure_work_v01,
        dispatch=host.dispatch_current_action_v01, effect=firewall.execute_bound_effect_v01,
        controlled_role=ControlledRolesV01.respond_v01, live_role=LiveSemanticProviderV01.respond_v01)
    for name in ("quote", "period", "payment", "entitlement", "session", "playback"):
        functions["executor_"+name] = getattr(world, "execute_"+name+"_v01")
    return functions


def native_scenario(output, provider):
    from demo.run_gate6_reference_v01 import observe_calls
    from hedgehog.domains.testflix import contracts_v01 as c, evidence_v01 as e, mock_world_v01 as world
    value = quality_input(); expected = oracle(value)
    request = c.request_from_plain_v01(value)
    handler = e.TestflixHandlerV01(); start = len(world.CALLS); began = time.monotonic()
    try:
        with observe_calls(native_functions(), output=output / "native_observation.json", phase="MODEL_NATIVE_HANDLER") as observed:
            report = handler.handle_v01(request, provider=provider)
        save(output / "native_observation.json", observed)
        require(observed["sentinel_live"] and observed["counts"].get("dispatch") == 4 and observed["counts"].get("effect") == 4,
                "actual_mock_action_counts")
        actual = dict(plan_id=report["semantics"]["selected_plan"].plan_id,
            amount_minor=report["payment"]["output"]["amount_minor"], currency=report["payment"]["output"]["currency"],
            resolution=report["session"].candidate.quality)
        require(actual == expected and set(handler.hosts) == {"user", "bank", "provider", "device"}, "independent_outcome_or_roots")
        require(len(handler.consumed_periods) == len(handler.entitlements) == len(handler.sessions) == len(handler.active) == 1, "mock_state_readback")
        save(output / "semantic_records.json", e.plain_value_v01(report["semantics"]))
        save(output / "mock_readback.json", dict(consumed_periods=handler.consumed_periods,
            entitlements=e.plain_value_v01(handler.entitlements), sessions=e.plain_value_v01(handler.sessions), active=handler.active,
            executor_calls=[dict(kind=k, invocation_id=i, values=e.plain_value_v01(v)) for k,i,v in world.CALLS[start:] if k == "EXECUTOR"]))
        package = e.seal_report_v01(report)
        save(output / "sealed.json", package)
        from demo.run_gate6_reference_v01 import source_closure
        summary = dict(status="CONTROLLED_NATIVE_COMPLETE" if provider.mode == "CONTROLLED_ROLE_DUTIES" else "LIVE_NATIVE_COMPLETE",
            source_closure_sha256=digest(source_closure()), input_sha256=digest(value),
            outcome=actual, mode=provider.mode, roles=list(ROLES), actual_counts=observed["counts"],
            mock_effects=4, real_world_effects=0, manifest_hash=package["manifest_hash"], seconds=time.monotonic()-began,
            consumed=dict(semantic_ref=report["semantics"]["semantic_ref"], quote=e.plain_value_v01(report["quote"]["results"]),
                          root_decision=report["user_selection"]["result"].decision_id))
        save(output / "summary.json", summary)
        return summary
    finally:
        handler.memory_directory.cleanup()


def pure_replay(package, pin, output):
    from demo.run_gate6_reference_v01 import observe_calls
    from hedgehog.domains.testflix import evidence_v01 as e
    value = json.loads(Path(package).read_bytes())
    with observe_calls(native_functions(), output=Path(output).with_suffix(".observation.json"), phase="MODEL_SEALED_PURE_REPLAY") as observed:
        result = e.replay_v01(value, expected_manifest_hash=pin)
    require(observed["sentinel_live"] and not any(v for k,v in observed["counts"].items() if k != "sentinel"), "replay_called_runtime")
    save(output, dict(result=result, observation=observed, status="PURE_REPLAY_COMPLETE"))


def execute(output, *, mode="prepare", authorization=None, authorization_sha256=None, controlled=None, config_path=None):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    if mode == "prepare":
        save(output / "preparation.json", preparation())
        return dict(status="MODEL_LIVE_NOT_AUTHORIZED_NOT_RUN")
    if mode == "controlled":
        from hedgehog.domains.testflix.semantic_roles_v01 import ControlledRolesV01
        require(not (output / "native_started.json").exists(), "native_already_started_inspect_receipts")
        save(output / "native_started.json", dict(pid=os.getpid(), started=time.time(), mode=mode))
        return native_scenario(output, ControlledRolesV01())
    require(mode == "live", "model_mode")
    auth = check_authorization(authorization, authorization_sha256, output)
    require(controlled is not None, "controlled_comparison_required")
    baseline = json.loads((Path(controlled) / "summary.json").read_bytes())
    require(baseline["status"] == "CONTROLLED_NATIVE_COMPLETE" and baseline["outcome"] == oracle(quality_input()), "controlled_baseline")
    from demo.run_gate6_reference_v01 import source_closure
    require(baseline["source_closure_sha256"] == digest(source_closure()) and baseline["input_sha256"] == digest(quality_input()), "controlled_source_input_binding")
    pure_replay(Path(controlled) / "sealed.json", baseline["manifest_hash"], output / "controlled_replay.json")
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01
    ledger = BudgetLedger(output / "budget", classification="AUTHORIZED_LIVE")
    try:
        with sdk_interposition(ledger):
            provider = LiveSemanticProviderV01(directory=output / "adapter", category="AB", config_path=config_path, captured_prefix=())
            require(type(provider) is LiveSemanticProviderV01 and provider.model == MODEL, "exact_live_provider")
            live = native_scenario(output, provider)
        require(sum(r["event"] == "GENERATION_COMPLETE" for r in ledger.rows) == 4 and live["outcome"] == baseline["outcome"], "live_four_roles_and_contrast")
        result = dict(status="LIVE_CONTRAST_COMPLETE", run_id=auth["run_id"], outcome=live["outcome"],
                      live=live, controlled=baseline, identical_generated_words_required=False, new_permission_from_replay=False)
        save(output / "comparison.json", result)
        return dict(status="PASS", classification="LIVE_CONTRAST_COMPLETE")
    finally:
        ledger.close()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("prepare", "controlled", "live", "replay"), nargs="?", default="prepare")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--authorization"); p.add_argument("--authorization-sha256")
    p.add_argument("--controlled"); p.add_argument("--config-path")
    p.add_argument("--package"); p.add_argument("--manifest-hash")
    args = p.parse_args(argv)
    if args.mode == "replay":
        pure_replay(args.package, args.manifest_hash, args.output)
        return 0
    result = execute(args.output, mode=args.mode, authorization=args.authorization,
        authorization_sha256=args.authorization_sha256, controlled=args.controlled, config_path=args.config_path)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
