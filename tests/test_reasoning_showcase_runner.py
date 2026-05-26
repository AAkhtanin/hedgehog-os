import demo.run_reasoning_showcase as reasoning_showcase
from demo.run_reasoning_showcase import run_reasoning_showcase


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "raw_user_text",
    "chain of thought",
    "hidden reasoning",
}


def test_reasoning_showcase_prints_all_required_stories(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "[STORY] story_l0_reflex_turn_on_tv" in output
    assert "[STORY] story_memory_first_direct_reuse" in output
    assert "[STORY] story_full_certificate_pipeline" in output
    assert "[STORY] story_permission_blocked_without_confirm" in output
    assert "[STORY] story_architect_contract_violation_recovered" in output
    assert "[STORY] story_deadend_memory_avoids_bad_route" in output
    assert "story_live_gemini_architect_certificate" not in output


def test_reasoning_showcase_default_does_not_call_live_gemini(tmp_path, monkeypatch):
    class FailingRoot:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("RootOrchestrator should not be constructed for this test")

    monkeypatch.setattr(reasoning_showcase, "_story_l0_reflex", lambda _root: "l0")
    monkeypatch.setattr(reasoning_showcase, "_story_memory_first_direct_reuse", lambda _root: "reuse")
    monkeypatch.setattr(reasoning_showcase, "_story_full_certificate_pipeline", lambda _root: "full")
    monkeypatch.setattr(reasoning_showcase, "_story_permission_blocked", lambda _root: "permission")
    monkeypatch.setattr(reasoning_showcase, "_story_architect_contract_recovery", lambda _root: "contract")
    monkeypatch.setattr(reasoning_showcase, "_story_deadend_memory", lambda _root: "deadend")
    monkeypatch.setattr(reasoning_showcase, "RootOrchestrator", FailingRoot)

    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "story_live_gemini_architect_certificate" not in output


def test_reasoning_showcase_l0_story_contains_reflex_artifacts(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "ModeRouter selected deterministic_reflex" in output
    assert "LLM called: false" in output
    assert "No LLM was called: false" not in output
    assert "Architect skipped: true" in output
    assert "Executor skipped: true" in output
    assert "Root wrote Work memory: true" in output


def test_reasoning_showcase_direct_reuse_story_contains_compute_saved(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "Prior eligible Work record" in output or "prior eligible Work record" in output
    assert "ReuseGate marked best candidate as direct_reuse_candidate" in output
    assert "Root applied reuse decision direct_reuse" in output
    assert "Compute saved" in output
    assert "Root wrote new Work memory: true" in output


def test_reasoning_showcase_full_pipeline_story_contains_core_artifacts(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "InputIntake classified the request as certificate_demo" in output
    assert "DRS found no direct reuse" in output
    assert "official_online_request" in output
    assert "personal_visit" in output
    assert "legal_representative" in output
    assert "fallback_exploration" in output
    assert "AVF blocked illegal_coercion before Architect" in output
    assert "PlanGraph with 9 nodes" in output
    assert "Executor produced 9 ResultProposals" in output
    assert "Post V&V accepted 6" in output
    assert "GT selected official_online_request using gt_payoff_v0_2" in output
    assert "RootOrchestrator created FinalOutput as root_orchestrator" in output


def test_reasoning_showcase_permission_story_is_safe(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "Permission policy required confirmation" in output
    assert "Action result was blocked without confirmation" in output
    assert "No real external action occurred" in output
    assert "Final status is needs_user" in output


def test_reasoning_showcase_contract_recovery_story(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "Invalid PlanGraph contract rejected" in output
    assert "invalid_plan_graph_contract" in output
    assert "Deterministic recovery/fallback used" in output
    assert "Root still created FinalOutput as root_orchestrator" in output


def test_reasoning_showcase_deadend_memory_story(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "[STORY] story_deadend_memory_avoids_bad_route" in output
    assert "illegal_coercion blocked before Architect" in output
    assert "demo-level DeadEnd/Fraud-like DRS signal" in output
    assert "deadend:demo:illegal_coercion" in output
    assert "layer deadends" in output
    assert "type dead_end" in output
    assert "forbidden_vector_blocked" in output
    assert "remembered bad route" in output
    assert "bad vector was not sent to Architect" in output
    assert "Root remained final authority" in output
    assert "No real external action occurred" in output
    assert "not full Marennya/UP mutation" in output


def test_reasoning_showcase_live_gemini_success_story_with_mocked_root(tmp_path, monkeypatch):
    class FakeRoot:
        def __init__(self, *_args, **_kwargs):
            self.last_trace = {}

        def process_event(self, **kwargs):
            assert kwargs["architect_provider"] == "gemini"
            self.last_trace = {
                "llm_architect_result": {
                    "status": "completed",
                    "provider": "gemini",
                    "used_llm": True,
                    "fallback": "none",
                    "error": None,
                },
                "plan_graph": {
                    "plan_id": "plan:live",
                    "source_packet_id": "packet:live",
                    "request_id": "story_live_gemini_architect_certificate",
                    "nodes": [
                        {
                            "node_id": "a",
                            "vector_id": "official_online_request",
                            "executor_id": "exec",
                            "depends_on": [],
                            "task": "prepare_request_payload",
                        }
                    ],
                    "edges": [],
                },
                "gt_report": {"winner": "rp:a"},
                "result_proposals": [{"proposal_id": "rp:a", "vector_id": "official_online_request"}],
            }
            return {"created_by": "root_orchestrator"}

    monkeypatch.setattr(reasoning_showcase, "RootOrchestrator", FakeRoot)
    monkeypatch.setattr(reasoning_showcase, "_story_l0_reflex", lambda _root: "l0")
    monkeypatch.setattr(reasoning_showcase, "_story_memory_first_direct_reuse", lambda _root: "reuse")
    monkeypatch.setattr(reasoning_showcase, "_story_full_certificate_pipeline", lambda _root: "full")
    monkeypatch.setattr(reasoning_showcase, "_story_permission_blocked", lambda _root: "permission")
    monkeypatch.setattr(reasoning_showcase, "_story_architect_contract_recovery", lambda _root: "contract")
    monkeypatch.setattr(reasoning_showcase, "_story_deadend_memory", lambda _root: "deadend")

    output = run_reasoning_showcase(drs_root=tmp_path, include_live_gemini=True)

    assert "[STORY] story_live_gemini_architect_certificate" in output
    assert "Live Gemini requested: true" in output
    assert "Architect provider: gemini" in output
    assert "LLM Architect status: completed" in output
    assert "LLM Architect used_llm: true" in output
    assert "LLM Architect fallback: none" in output
    assert "Gemini produced a contract-valid PlanGraph" in output
    assert "Contract validation passed before Executor" in output
    assert "FinalOutput created_by: root_orchestrator" in output


def test_reasoning_showcase_live_gemini_error_fallback_story_with_mocked_root(tmp_path, monkeypatch):
    class FakeRoot:
        def __init__(self, *_args, **_kwargs):
            self.last_trace = {}

        def process_event(self, **_kwargs):
            self.last_trace = {
                "llm_architect_result": {
                    "status": "error",
                    "provider": "gemini",
                    "used_llm": True,
                    "fallback": "deterministic",
                    "error": "invalid_plan_graph_contract: missing plan_id",
                },
                "plan_graph": {
                    "plan_id": "plan:fallback",
                    "source_packet_id": "packet:fallback",
                    "request_id": "story_live_gemini_architect_certificate",
                    "nodes": [],
                    "edges": [],
                },
                "gt_report": {"winner": None},
                "result_proposals": [],
            }
            return {"created_by": "root_orchestrator"}

    monkeypatch.setattr(reasoning_showcase, "RootOrchestrator", FakeRoot)
    monkeypatch.setattr(reasoning_showcase, "_story_l0_reflex", lambda _root: "l0")
    monkeypatch.setattr(reasoning_showcase, "_story_memory_first_direct_reuse", lambda _root: "reuse")
    monkeypatch.setattr(reasoning_showcase, "_story_full_certificate_pipeline", lambda _root: "full")
    monkeypatch.setattr(reasoning_showcase, "_story_permission_blocked", lambda _root: "permission")
    monkeypatch.setattr(reasoning_showcase, "_story_architect_contract_recovery", lambda _root: "contract")
    monkeypatch.setattr(reasoning_showcase, "_story_deadend_memory", lambda _root: "deadend")

    output = run_reasoning_showcase(drs_root=tmp_path, include_live_gemini=True)

    assert "LLM Architect status: error" in output
    assert "LLM Architect fallback: deterministic" in output
    assert "Gemini attempt failed or produced an invalid plan" in output
    assert "Deterministic fallback/recovery used" in output
    assert "SAFE_FAIL/RECOVERED" in output


def test_reasoning_showcase_has_why_this_matters_per_story(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert output.count("WHY THIS MATTERS:") == 6


def test_reasoning_showcase_live_gemini_adds_one_why_this_matters(tmp_path, monkeypatch):
    monkeypatch.setattr(
        reasoning_showcase,
        "_story_live_gemini_architect",
        lambda _root: "[STORY] story_live_gemini_architect_certificate\n\nWHY THIS MATTERS:\nmock",
    )
    output = run_reasoning_showcase(drs_root=tmp_path, include_live_gemini=True)

    assert output.count("WHY THIS MATTERS:") == 7


def test_reasoning_showcase_does_not_leak_sensitive_or_hidden_reasoning_terms(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
