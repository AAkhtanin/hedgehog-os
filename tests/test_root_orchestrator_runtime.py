import json
from pathlib import Path

import jsonschema

from hedgehog.drs import LocalDRS, SENSITIVE_KEY_FRAGMENTS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def final_output_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    time_envelope_schema = load_json(SCHEMAS_DIR / "time_envelope.schema.json")
    final_output_schema = load_json(SCHEMAS_DIR / "final_output.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        final_output_schema["$id"]: final_output_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(final_output_schema, store=store)
    return jsonschema.Draft202012Validator(final_output_schema, resolver=resolver)


def make_orchestrator(tmp_path):
    drs = LocalDRS(tmp_path)
    return RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR), drs


def run_demo(tmp_path, request_id="req_root_001"):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id=request_id,
        session_anchor="sess_root_001",
    )
    return orchestrator, drs, final_output


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def contains_sensitive_key(value):
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower()
            if any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS):
                return True
            if contains_sensitive_key(child):
                return True
    if isinstance(value, list):
        return any(contains_sensitive_key(item) for item in value)
    return False


def test_root_orchestrator_creates_valid_final_output_and_work_record(tmp_path):
    orchestrator, drs, final_output = run_demo(tmp_path)

    final_output_validator().validate(final_output)
    final_draft = orchestrator.last_trace["final_draft_proposal"]
    assert final_draft["created_by"] == "final_renderer"
    assert final_output["answer"] == final_draft["body"]
    assert final_output["created_by"] == "root_orchestrator"
    assert final_output["created_by"] != final_draft["created_by"]
    assert final_draft["completed_proposal_ids"]
    assert final_output["status"] in {"success", "partial", "needs_user", "failed"}
    assert final_output["answer"]
    assert final_output["used_proposals"]
    assert final_output["drs_writes"]
    assert not contains_key(final_draft, "final_output")

    work_record = drs.read_record("work", final_output["drs_writes"][0])
    content = work_record["content"]
    assert work_record["layer"] == "work"
    assert work_record["time_envelope"]
    assert {"pt_created_at", "kt_asof", "ct_session_anchor", "ttl_seconds"} <= set(
        work_record["time_envelope"]
    )
    assert work_record["provenance"]["created_by"] == "root_orchestrator"
    assert content["final_status"] == final_output["status"]
    assert content["gt_report_ref"] == final_output["gt_report_ref"]
    assert content["final_draft_ref"] == final_draft["draft_id"]
    assert content["completed_proposal_ids"]
    assert content["selected_proposal_ids"]
    assert content["selected_proposal_ids"] == final_draft["selected_proposal_ids"]
    assert content["final_draft_claims"] == final_draft["claims"]
    assert content["final_draft_warnings"] == final_draft["warnings"]


def test_root_orchestrator_generic_math_routes_to_llm_general_not_certificate_pipeline(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="x + y = 110\nx - y = 100",
        request_id="req_general_math",
        session_anchor="sess_general_math",
        llm_provider="mock",
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    final_output_validator().validate(final_output)
    assert orchestrator.last_trace["input_intake"]["intent_kind"] == "general_request"
    assert orchestrator.last_trace["execution_mode"] == "llm_general"
    assert orchestrator.last_trace["route"] == "llm_general"
    assert orchestrator.last_trace["architect_skipped"] is True
    assert orchestrator.last_trace["executor_skipped"] is True
    assert orchestrator.last_trace["llm_gateway_result"]["provider"] == "mock"
    assert final_output["created_by"] == "root_orchestrator"
    assert final_output["answer"] == "x = 105\ny = 5"
    assert "certificate request pipeline completed" not in final_output["answer"].lower()
    assert work_record["domain"] == "general"
    assert work_record["content"]["execution_mode"] == "llm_general"
    assert work_record["content"]["route"] == "llm_general"
    assert work_record["content"]["provider"] == "mock"
    assert work_record["content"]["model"] == "mock_general_responder_v1"
    assert work_record["content"]["used_llm"] is False
    assert work_record["content"]["method"] == "llm_gateway_general_responder"
    assert not contains_key(work_record["content"], "raw_user_text")


def test_root_orchestrator_certificate_text_still_uses_proof_pipeline(tmp_path):
    orchestrator, _, final_output = run_demo(tmp_path, request_id="req_certificate_pipeline")

    assert orchestrator.last_trace["input_intake"]["intent_kind"] == "certificate_demo"
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert orchestrator.last_trace["llm_architect_result"] is None
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert orchestrator.last_trace["result_proposals"]
    assert final_output["created_by"] == "root_orchestrator"


def test_root_orchestrator_optional_mock_llm_architect_still_creates_final_output(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="I need a mock government certificate request.",
        request_id="req_root_mock_llm_architect",
        session_anchor="sess_root_mock_llm_architect",
        architect_provider="mock_llm",
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    final_output_validator().validate(final_output)
    assert orchestrator.last_trace["llm_architect_result"]["status"] == "completed"
    assert orchestrator.last_trace["llm_architect_result"]["provider"] == "mock"
    assert orchestrator.last_trace["llm_architect_result"]["used_llm"] is False
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert final_output["created_by"] == "root_orchestrator"
    assert work_record["content"]["execution_mode"] == "proof_full_pipeline"


def test_root_orchestrator_falls_back_when_llm_architect_returns_invalid_plan_graph(
    tmp_path,
    monkeypatch,
):
    import hedgehog.root_orchestrator as root_module

    def fake_invalid_llm_architect(**_kwargs):
        return {
            "status": "completed",
            "provider": "gemini",
            "model": "test-gemini",
            "used_llm": True,
            "plan_graph": {
                "nodes": []
            },
            "error": None,
            "warnings": [],
            "prompt_contract": {},
        }

    monkeypatch.setattr(
        root_module,
        "make_plan_graph_with_llm",
        fake_invalid_llm_architect,
    )
    orchestrator, _ = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="I need a mock government certificate request.",
        request_id="req_invalid_llm_architect",
        session_anchor="sess_invalid_llm_architect",
        architect_provider="gemini",
    )

    assert final_output["created_by"] == "root_orchestrator"
    assert orchestrator.last_trace["llm_architect_result"]["status"] == "error"
    assert orchestrator.last_trace["llm_architect_result"]["fallback"] == "deterministic"
    assert "invalid_plan_graph_contract" in orchestrator.last_trace["llm_architect_result"]["error"]
    assert orchestrator.last_trace["plan_graph"]["plan_id"]
    assert orchestrator.last_trace["result_proposals"]


def test_root_orchestrator_does_not_persist_raw_text_or_sensitive_content_keys(tmp_path):
    _, drs, final_output = run_demo(tmp_path, request_id="req_root_002")
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    assert not contains_key(final_output, "raw_user_text")
    assert not contains_key(work_record, "raw_user_text")
    assert not contains_sensitive_key(work_record["content"])


def test_root_orchestrator_excludes_forbidden_vector_from_output_and_drs(tmp_path):
    orchestrator, drs, final_output = run_demo(tmp_path, request_id="req_root_003")
    work_record = drs.read_record("work", final_output["drs_writes"][0])
    node_vector_ids = {
        node["vector_id"] for node in orchestrator.last_trace["plan_graph"]["nodes"]
    }
    proposal_vector_ids = {
        proposal["vector_id"] for proposal in orchestrator.last_trace["result_proposals"]
    }

    assert "illegal_coercion" not in node_vector_ids
    assert "illegal_coercion" not in proposal_vector_ids
    assert all("illegal_coercion" not in proposal_id for proposal_id in final_output["used_proposals"])
    assert "illegal_coercion" not in json.dumps(work_record["content"], sort_keys=True)


def test_root_orchestrator_final_output_references_gt_report_from_trace(tmp_path):
    orchestrator, _, final_output = run_demo(tmp_path, request_id="req_root_004")
    gt_report = orchestrator.last_trace["gt_report"]

    assert gt_report["gt_report_id"]
    assert final_output["gt_report_ref"] == gt_report["gt_report_id"]
    assert orchestrator.last_trace["final_output"] == final_output


def test_root_orchestrator_second_run_reuses_prior_work_record(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)

    first_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id="req_reuse_001",
        session_anchor="sess_reuse_001",
    )
    assert orchestrator.last_trace["retrieved_record_count"] == 0
    assert orchestrator.last_trace["memory_context_applied"] is False
    assert orchestrator.last_trace["memory_source_record_ids"] == []
    assert orchestrator.last_trace["reuse_gate"]["reuse_decision"] == "none"
    assert orchestrator.last_trace["reuse_gate"]["candidate_scores"] == []
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert orchestrator.last_trace["mode_router"]["reason"] == "forced_full_pipeline_for_demo"
    assert orchestrator.last_trace["reuse_decision"] == "none"
    assert orchestrator.last_trace["reuse_applied"] is False
    assert orchestrator.last_trace["reused_record_ids"] == []

    second_output = orchestrator.process_event(
        raw_user_text="I need another certificate for a mock government service.",
        request_id="req_reuse_002",
        session_anchor="sess_reuse_002",
    )
    assert orchestrator.last_trace["retrieved_record_count"] >= 1

    first_record = drs.read_record("work", first_output["drs_writes"][0])
    second_record = drs.read_record("work", second_output["drs_writes"][0])

    assert orchestrator.last_trace["memory_context_applied"] is True
    assert first_record["record_id"] in orchestrator.last_trace["memory_source_record_ids"]
    assert "reuse_gate" in orchestrator.last_trace
    assert orchestrator.last_trace["reuse_gate"]["candidate_scores"]
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert orchestrator.last_trace["reuse_decision"] == "context_only"
    assert orchestrator.last_trace["reuse_applied"] is False
    assert orchestrator.last_trace["reused_record_ids"] == []
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert orchestrator.last_trace["result_proposals"]
    if orchestrator.last_trace["reuse_decision"] == "direct_reuse_candidate":
        assert orchestrator.last_trace["reuse_applied"] is False
    assert second_record["content"]["retrieved_record_count"] >= 1
    assert second_record["content"]["memory_context_applied"] is True
    assert first_record["record_id"] in second_record["content"]["memory_source_record_ids"]
    assert second_record["content"]["reuse_decision"] == "context_only"
    assert "reuse_score_best" in second_record["content"]
    assert second_record["content"]["reuse_candidate_record_id"] == first_record["record_id"]
    assert second_record["content"]["reuse_applied"] is False
    assert second_record["content"]["reused_record_ids"] == []
    assert second_record["content"]["final_status"] == second_output["status"]
    assert second_record["content"]["execution_mode"] == "proof_full_pipeline"
    assert second_record["content"]["route"] == "proof_full_pipeline"
    assert first_record["record_id"] != second_record["record_id"]
    assert first_record["layer"] == "work"
    assert second_record["layer"] == "work"


def test_root_orchestrator_direct_reuse_candidate_still_runs_full_pipeline(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    strong_record = {
        "record_id": "work:strong_direct_candidate",
        "layer": "work",
        "type": "task_outcome",
        "domain": "government_certificate",
        "content": {
            "summary": "Strong prior mock certificate outcome."
        },
        "time_envelope": make_time_envelope("sess_strong_candidate"),
        "provenance": {
            "request_id": "req_strong_candidate",
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "gt": {
            "gt_report_id": "gt:strong:candidate",
            "half_life_hours": 2_000.0,
            "decay_rate": 0.0001,
        },
        "status": "accepted",
    }
    drs.write_record(strong_record)

    final_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id="req_direct_candidate_001",
        session_anchor="sess_direct_candidate_001",
        allow_direct_reuse=False,
    )

    assert orchestrator.last_trace["reuse_decision"] == "direct_reuse_candidate"
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert orchestrator.last_trace["reuse_applied"] is False
    assert orchestrator.last_trace["reused_record_ids"] == []
    assert orchestrator.last_trace["reuse_gate"]["candidate_scores"][0]["eligible"] is True
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert orchestrator.last_trace["result_proposals"]
    assert final_output["created_by"] == "root_orchestrator"


def test_root_orchestrator_direct_reuse_enabled_skips_architect_and_executor(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    strong_record = {
        "record_id": "work:direct_reuse_source",
        "layer": "work",
        "type": "task_outcome",
        "domain": "government_certificate",
        "content": {
            "summary": "Strong prior mock certificate outcome."
        },
        "time_envelope": make_time_envelope("sess_direct_reuse_source"),
        "provenance": {
            "request_id": "req_direct_reuse_source",
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "gt": {
            "gt_report_id": "gt:direct:reuse:source",
            "half_life_hours": 2_000.0,
            "decay_rate": 0.0001,
        },
        "status": "accepted",
    }
    drs.write_record(strong_record)

    final_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id="req_direct_reuse_001",
        session_anchor="sess_direct_reuse_001",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    final_output_validator().validate(final_output)
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "direct_reuse"
    assert orchestrator.last_trace["mode_router"]["direct_reuse_allowed"] is True
    assert orchestrator.last_trace["reuse_decision"] == "direct_reuse"
    assert orchestrator.last_trace["reuse_applied"] is True
    assert orchestrator.last_trace["reused_record_ids"] == ["work:direct_reuse_source"]
    assert orchestrator.last_trace["architect_skipped"] is True
    assert orchestrator.last_trace["executor_skipped"] is True
    assert orchestrator.last_trace["plan_graph"] is None
    assert orchestrator.last_trace["result_proposals"] == []
    assert orchestrator.last_trace["vv_reports"] == []
    assert orchestrator.last_trace["final_draft_proposal"]["created_by"] == "final_renderer"
    assert orchestrator.last_trace["final_draft_proposal"]["mode"] == "direct_reuse"
    assert final_output["created_by"] == "root_orchestrator"
    assert final_output["status"] == "success"
    assert final_output["used_proposals"] == []
    assert work_record["content"]["result"] == "direct_reuse"
    assert work_record["content"]["final_status"] == final_output["status"]
    assert work_record["content"]["execution_mode"] == "direct_reuse"
    assert work_record["content"]["route"] == "direct_reuse"
    assert work_record["content"]["reused_record_ids"] == ["work:direct_reuse_source"]
    assert work_record["content"]["reuse_applied"] is True
    assert work_record["content"]["direct_reuse_applied"] is True
    assert work_record["content"]["reuse_decision"] == "direct_reuse"
    assert work_record["content"]["architect_skipped"] is True
    assert work_record["content"]["executor_skipped"] is True


def test_root_orchestrator_context_only_does_not_shortcut_with_direct_reuse_enabled(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    first_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id="req_context_only_source",
        session_anchor="sess_context_only_source",
    )

    second_output = orchestrator.process_event(
        raw_user_text="I need another certificate for a mock government service.",
        request_id="req_context_only_enabled",
        session_anchor="sess_context_only_enabled",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    second_record = drs.read_record("work", second_output["drs_writes"][0])

    assert first_output["drs_writes"][0] in orchestrator.last_trace["memory_source_record_ids"]
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "context_only"
    assert orchestrator.last_trace["reuse_decision"] == "context_only"
    assert orchestrator.last_trace["reuse_applied"] is False
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert orchestrator.last_trace["result_proposals"]
    assert second_record["content"]["result"] == "simulated_success"
    assert second_record["content"]["reuse_applied"] is False


def test_root_orchestrator_force_full_pipeline_prevents_direct_reuse_even_when_allowed(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    strong_record = {
        "record_id": "work:force_full_pipeline_source",
        "layer": "work",
        "type": "task_outcome",
        "domain": "government_certificate",
        "content": {
            "summary": "Strong prior mock certificate outcome."
        },
        "time_envelope": make_time_envelope("sess_force_full_pipeline_source"),
        "provenance": {
            "request_id": "req_force_full_pipeline_source",
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "gt": {
            "gt_report_id": "gt:force:full:pipeline:source",
            "half_life_hours": 2_000.0,
            "decay_rate": 0.0001,
        },
        "status": "accepted",
    }
    drs.write_record(strong_record)

    final_output = orchestrator.process_event(
        raw_user_text="I need a certificate for a mock government service.",
        request_id="req_force_full_pipeline_001",
        session_anchor="sess_force_full_pipeline_001",
        allow_direct_reuse=True,
        force_full_pipeline=True,
    )

    assert orchestrator.last_trace["reuse_gate"]["reuse_decision"] == "direct_reuse_candidate"
    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert orchestrator.last_trace["reuse_decision"] == "direct_reuse_candidate"
    assert orchestrator.last_trace["reuse_applied"] is False
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert orchestrator.last_trace["result_proposals"]
    assert final_output["created_by"] == "root_orchestrator"


def test_root_orchestrator_turn_on_tv_defaults_to_proof_full_pipeline(tmp_path):
    orchestrator, _ = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="req_reflex_default_full_pipeline",
        session_anchor="sess_reflex_default_full_pipeline",
    )

    assert orchestrator.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert orchestrator.last_trace["plan_graph"]["nodes"]
    assert orchestrator.last_trace["result_proposals"]
    assert final_output["created_by"] == "root_orchestrator"


def test_root_orchestrator_reflex_turn_on_tv_skips_architect_and_executor(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="req_reflex_turn_on_tv",
        session_anchor="sess_reflex_turn_on_tv",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    final_output_validator().validate(final_output)
    assert orchestrator.last_trace["execution_mode"] == "deterministic_reflex"
    assert orchestrator.last_trace["reflex_applied"] is True
    assert orchestrator.last_trace["architect_skipped"] is True
    assert orchestrator.last_trace["executor_skipped"] is True
    assert orchestrator.last_trace["plan_graph"] is None
    assert orchestrator.last_trace["result_proposals"] == []
    assert orchestrator.last_trace["final_draft_proposal"]["created_by"] == "final_renderer"
    assert orchestrator.last_trace["final_draft_proposal"]["mode"] == "deterministic_reflex"
    assert final_output["status"] == "success"
    assert work_record["content"]["final_status"] == final_output["status"]
    assert work_record["content"]["execution_mode"] == "deterministic_reflex"
    assert work_record["content"]["route"] == "deterministic_reflex"
    assert work_record["content"]["action_id"] == "mock_turn_on_tv"
    assert work_record["content"]["action_status"] == "simulated_success"
    assert work_record["content"]["permission_reason"] == "allowed"
    assert work_record["content"]["protocol_step_count"] == 4
    assert work_record["content"]["protocol_steps_executed"] == [
        "validate_tv_command",
        "check_tv_permission",
        "mock_tv_execute",
        "audit_tv_command",
    ]
    assert work_record["content"]["protocol_mock_only"] is True
    assert work_record["content"]["reflex_applied"] is True
    assert work_record["content"]["architect_skipped"] is True
    assert work_record["content"]["executor_skipped"] is True


def test_root_orchestrator_reflex_order_pizza_blocks_without_confirmation(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="order pizza",
        request_id="req_reflex_order_pizza_blocked",
        session_anchor="sess_reflex_order_pizza_blocked",
        allow_reflex=True,
        force_full_pipeline=False,
        user_confirmed=False,
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    final_output_validator().validate(final_output)
    assert final_output["status"] == "needs_user"
    assert orchestrator.last_trace["execution_mode"] == "deterministic_reflex"
    assert orchestrator.last_trace["reflex_applied"] is False
    assert orchestrator.last_trace["final_draft_proposal"]["created_by"] == "final_renderer"
    assert orchestrator.last_trace["final_draft_proposal"]["mode"] == "deterministic_reflex"
    assert orchestrator.last_trace["architect_skipped"] is True
    assert orchestrator.last_trace["executor_skipped"] is True
    assert work_record["content"]["action_id"] == "mock_order_pizza"
    assert work_record["content"]["action_status"] == "blocked"
    assert work_record["content"]["permission_reason"] == "confirmation_required"
    assert work_record["content"]["protocol_step_count"] == 3
    assert "mock_pizza_execute" not in work_record["content"]["protocol_steps_executed"]
    assert "mock_pizza_receipt" not in work_record["content"]["protocol_steps_executed"]
    assert work_record["content"]["protocol_mock_only"] is True
    assert work_record["content"]["final_status"] == final_output["status"]
    assert work_record["content"]["execution_mode"] == "deterministic_reflex"
    assert work_record["content"]["route"] == "deterministic_reflex"
    assert work_record["content"]["reflex_applied"] is False
    assert work_record["content"]["architect_skipped"] is True
    assert work_record["content"]["executor_skipped"] is True


def test_root_orchestrator_reflex_order_pizza_confirmed_is_mock_success(tmp_path):
    orchestrator, drs = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="order pizza",
        request_id="req_reflex_order_pizza_confirmed",
        session_anchor="sess_reflex_order_pizza_confirmed",
        allow_reflex=True,
        force_full_pipeline=False,
        user_confirmed=True,
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    final_output_validator().validate(final_output)
    assert final_output["status"] == "success"
    assert orchestrator.last_trace["reflex_applied"] is True
    assert orchestrator.last_trace["reflex_result"]["status"] == "simulated_success"
    assert work_record["content"]["action_id"] == "mock_order_pizza"
    assert work_record["content"]["action_status"] == "simulated_success"
    assert work_record["content"]["permission_reason"] == "allowed"
    assert work_record["content"]["protocol_step_count"] == 5
    assert work_record["content"]["protocol_steps_executed"] == [
        "validate_pizza_order",
        "check_pizza_permission",
        "mock_pizza_execute",
        "mock_pizza_receipt",
        "audit_pizza_order",
    ]
    assert work_record["content"]["protocol_mock_only"] is True
