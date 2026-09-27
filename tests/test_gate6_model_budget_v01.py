"""Offline real-SDK serialization controls. Fake HTTP is never live evidence."""
import copy
import json
import socket

import httpx
import pytest

from tools import run_gate6_model_contrast_v01 as model


@pytest.fixture
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("REAL_NETWORK_FORBIDDEN")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setenv("HEDGEHOG_GEMINI_API_KEY", "DUMMY_OFFLINE_KEY")
    monkeypatch.setenv("HEDGEHOG_LIVE_PROVIDER_MODEL", model.MODEL)
    for key in ("GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GEMINI_BASE_URL", "GOOGLE_VERTEX_BASE_URL", "GOOGLE_GENAI_BASE_URL"):
        monkeypatch.delenv(key, raising=False)


def wire_fixture(tmp_path, *, count=100, fail=None, usage=None, finish="STOP"):
    from hedgehog.domains.testflix.semantic_roles_v01 import ControlledRolesV01
    controlled = ControlledRolesV01()
    wires = []
    def send(request):
        body = json.loads(request.content)
        wires.append(dict(url=str(request.url), body=body))
        assert "key=" not in str(request.url)
        if request.url.path.endswith(":countTokens"):
            assert set(body) == {"generateContentRequest"}
            if fail == "count":
                return httpx.Response(503, json={"error": {"code": 503, "message": "OFFLINE_COUNT_FAILURE"}})
            return httpx.Response(200, json={"totalTokens": count})
        if fail == "generation":
            return httpx.Response(503, json={"error": {"code": 503, "message": "OFFLINE_GENERATION_FAILURE"}})
        parsed = json.loads(body["contents"][0]["parts"][0]["text"])
        value, _ = controlled.respond_v01(parsed["duty"], parsed["input"], "offline")
        return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": json.dumps(value)}]},
            "finishReason": finish}], "modelVersion": model.MODEL, "usageMetadata": usage if usage is not None else {
            "promptTokenCount": 100, "candidatesTokenCount": 20, "thoughtsTokenCount": 0,
            "cachedContentTokenCount": 0, "totalTokenCount": 120}})
    return httpx.MockTransport(send), wires


def call_roles(tmp_path, transport, ledger):
    from hedgehog.domains.testflix import contracts_v01 as c, semantic_adapter_v01 as semantic
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01
    with model.sdk_interposition(ledger, offline_transport=transport):
        provider = LiveSemanticProviderV01(directory=tmp_path / "adapter", category="AB", captured_prefix=())
        assert type(provider) is LiveSemanticProviderV01
        return semantic.collect_semantics_v01(c.request_from_plain_v01(model.quality_input()), provider)


def test_model_no_authorization_no_dispatch(tmp_path, offline):
    with pytest.raises(ValueError, match="MODEL_LIVE_NOT_AUTHORIZED_NOT_RUN"):
        model.execute(tmp_path, mode="live")
    assert not (tmp_path / "budget").exists()


def test_quality_exact_input_and_independent_oracle():
    original = json.loads((model.ROOT / "demo/testflix_fixtures_v01.json").read_bytes())
    value = model.quality_input()
    assert {k for k in value if value[k] != original[k]} == {"preference"}
    assert model.oracle(value) == dict(plan_id="plan:ab31", amount_minor=600, currency="EUR", resolution=1080)
    assert value["hard_ceiling_minor"] == 650 and value["catalog"][2]["price_minor"] == 900


def test_real_sdk_full_wire_roles_and_no_network(tmp_path, offline, record_property):
    from google import genai
    from hedgehog.domains.testflix import contracts_v01 as c, semantic_roles_v01 as roles
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import duty_v01
    original = genai.Client
    transport, wires = wire_fixture(tmp_path)
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_FAKE_HTTP_REAL_SDK")
    try:
        semantics = call_roles(tmp_path, transport, ledger)
        assert genai.Client is original
        assert len(wires) == 8
        assert [r["role"] for r in semantics["contributions"]] == list(model.ROLES)
        for ordinal, (counted, generated) in enumerate(zip(wires[::2], wires[1::2], strict=True)):
            assert counted["body"] == {"generateContentRequest": dict(model="models/"+model.MODEL, **generated["body"])}
            record = semantics["contributions"][ordinal]
            contents = json.loads(generated["body"]["contents"][0]["parts"][0]["text"])
            assert contents == dict(duty=model.ROLES[ordinal], input=record["projection"])
            assert generated["body"]["systemInstruction"]["parts"][0]["text"].endswith(duty_v01(model.ROLES[ordinal]))
            assert record["capture"]["request_ref"] == roles.request_ref_v01(c.request_from_plain_v01(model.quality_input()))
            if ordinal:
                assert record["projection"]["upstream"][-1]["output"] == semantics["contributions"][ordinal-1]["output"]
        assert semantics["selected_plan"].plan_id == "plan:ab31"
        assert sum(r["event"] == "GENERATION_COMPLETE" for r in ledger.rows) == 4
        with pytest.raises(ValueError, match="fifth_attempt"):
            ledger.reserve_count(model.ROLES[0], {})
        record_property("OFFLINE_FAKE_HTTP_REAL_SDK", json.dumps(dict(wires=wires, ledger=ledger.rows, actual_external_calls=0)))
    finally:
        ledger.close()


@pytest.mark.parametrize("count", [4097, None, True], ids=["over-cap", "missing", "boolean"])
def test_count_invalid_sends_no_generation(tmp_path, offline, count):
    transport, wires = wire_fixture(tmp_path, count=count)
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_FAKE_HTTP_REAL_SDK")
    try:
        with pytest.raises(ValueError, match="input_token_cap_or_ambiguous"):
            call_roles(tmp_path, transport, ledger)
        assert len(wires) == 1
        assert not any(r["event"] == "GENERATION_RESERVED" for r in ledger.rows)
    finally:
        ledger.close()


@pytest.mark.parametrize("failure", ["count", "generation"])
def test_failed_dispatch_no_retry_or_budget_reset(tmp_path, offline, failure):
    transport, wires = wire_fixture(tmp_path, fail=failure)
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_FAKE_HTTP_REAL_SDK")
    try:
        with pytest.raises(Exception):
            call_roles(tmp_path, transport, ledger)
        assert len(wires) == (1 if failure == "count" else 2)
        with pytest.raises(ValueError):
            ledger.reserve_count(model.ROLES[0], {})
    finally:
        ledger.close()
    with pytest.raises(ValueError, match="budget_existing_chain"):
        model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_FAKE_HTTP_REAL_SDK")
    rows = [json.loads(line) for line in (tmp_path / "budget/budget.jsonl").read_text().splitlines()]
    assert any(r["event"] == "COUNT_RESERVED" for r in rows)


def test_reservation_is_durable_before_uncertain_dispatch(tmp_path):
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_LEDGER")
    ledger.reserve_count(model.ROLES[0], {"generateContentRequest": {}})
    assert json.loads((tmp_path / "budget/budget.jsonl").read_text().splitlines()[-1])["event"] == "COUNT_RESERVED"
    ledger.close()
    with pytest.raises(ValueError, match="budget_existing_chain"):
        model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_LEDGER")


@pytest.mark.parametrize("usage,finish", [({}, "STOP"), ({"promptTokenCount": 100, "candidatesTokenCount": 2049, "totalTokenCount": 2149}, "STOP"), (None, "MAX_TOKENS")], ids=["missing", "output-cap", "truncated"])
def test_invalid_usage_or_finish_not_complete(tmp_path, offline, usage, finish):
    transport, wires = wire_fixture(tmp_path, usage=usage, finish=finish)
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE_FAKE_HTTP_REAL_SDK")
    try:
        with pytest.raises(ValueError):
            call_roles(tmp_path, transport, ledger)
        assert len(wires) == 2
        assert not any(r["event"] == "GENERATION_COMPLETE" for r in ledger.rows)
        assert any(r["event"] == "PROVIDER_USAGE" for r in ledger.rows)
    finally:
        ledger.close()


def test_interposition_exception_and_conflict_restore(tmp_path, offline):
    from google import genai
    original = genai.Client
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE")
    try:
        with pytest.raises(RuntimeError, match="controlled"):
            with model.sdk_interposition(ledger, offline_transport=httpx.MockTransport(lambda r: None)):
                with pytest.raises(ValueError, match="conflict"):
                    with model.sdk_interposition(ledger):
                        pytest.fail("nested entered")
                raise RuntimeError("controlled")
        assert genai.Client is original
    finally:
        ledger.close()


def test_redirect_and_foreign_routing_refused(tmp_path, offline, monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
    ledger = model.BudgetLedger(tmp_path / "budget", classification="OFFLINE")
    try:
        with pytest.raises(ValueError, match="conflicting_provider_routing"):
            with model.sdk_interposition(ledger):
                pytest.fail("route allowed")
        request = httpx.Request("POST", "https://elsewhere.invalid/v1beta/models/"+model.MODEL+":generateContent", json={})
        with pytest.raises(ValueError, match="developer_endpoint_only"):
            model.transport(httpx.MockTransport(lambda r: pytest.fail("dispatch")), ledger).handle_request(request)
    finally:
        ledger.close()


def test_preparation_is_not_model_completion(tmp_path, offline):
    value = model.execute(tmp_path)
    assert value["status"] == "MODEL_LIVE_NOT_AUTHORIZED_NOT_RUN"
    plan = json.loads((tmp_path / "preparation.json").read_bytes())
    assert plan["limits"] == model.LIMITS and plan["provider_calls"] == 0
