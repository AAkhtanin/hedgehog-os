from demo.run_mode_selection_matrix import run_mode_selection_matrix


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "hidden reasoning",
    "chain of thought",
}


def test_mode_selection_matrix_prints_all_scenarios(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "mode_l0_reflex_turn_on_tv" in output
    assert "mode_general_math_mock" in output
    assert "mode_full_certificate_pipeline" in output
    assert "mode_memory_direct_reuse" in output


def test_mode_selection_matrix_l0_selects_reflex_without_llm(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "mode_l0_reflex_turn_on_tv | simple_command | deterministic_reflex | false | false" in output
    assert "known deterministic mock action" in output


def test_mode_selection_matrix_general_math_selects_llm_general(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "mode_general_math_mock | simple_general_question | llm_general | false | false | false" in output
    assert "simple general question uses cheap mock general responder route" in output


def test_mode_selection_matrix_full_certificate_uses_full_pipeline_and_blocks_forbidden(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "mode_full_certificate_pipeline | complex_certificate_task | proof_full_pipeline" in output
    assert "| true | false | true | official_online_request | true | complex constrained task" in output


def test_mode_selection_matrix_direct_reuse_skips_pipeline(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "mode_memory_direct_reuse | repeated_known_task | direct_reuse | false | false | true" in output
    assert "trusted eligible memory record allows direct reuse and compute saved" in output


def test_mode_selection_matrix_has_reason_for_every_scenario(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "reason_for_mode" in output
    assert output.count(" | ") >= 40
    assert "known deterministic mock action" in output
    assert "cheap mock general responder" in output
    assert "complex constrained task" in output
    assert "trusted eligible memory record" in output


def test_mode_selection_matrix_summary_explains_scaling(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)

    assert "Hedgehog OS does not use one pipeline for everything." in output
    assert "deterministic reflex to direct reuse to general LLM to full PlanGraph pipeline" in output


def test_mode_selection_matrix_does_not_leak_sensitive_terms(tmp_path):
    output = run_mode_selection_matrix(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
