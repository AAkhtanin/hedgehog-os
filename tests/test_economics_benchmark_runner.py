from demo.run_economics_benchmark import run_economics_benchmark


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "hidden reasoning",
    "chain of thought",
}


def _row(output: str, scenario: str) -> list[str]:
    for line in output.splitlines():
        if line.startswith(f"{scenario} | "):
            return [part.strip() for part in line.split("|")]
    raise AssertionError(f"missing row for {scenario}")


def test_economics_benchmark_prints_all_required_scenarios(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)

    assert "econ_l0_reflex_turn_on_tv" in output
    assert "econ_direct_reuse_certificate" in output
    assert "econ_general_math_mock" in output
    assert "econ_full_certificate_pipeline" in output


def test_economics_l0_cost_lower_than_baseline(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)
    row = _row(output, "econ_l0_reflex_turn_on_tv")

    assert row[1] == "deterministic_reflex"
    assert row[2] == "0"
    assert int(row[5]) < int(row[6])
    assert "deterministic reflex avoided planning" in row[9]


def test_economics_direct_reuse_cost_lower_than_baseline_and_no_llm(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)
    row = _row(output, "econ_direct_reuse_certificate")

    assert row[1] == "direct_reuse"
    assert row[2] == "0"
    assert int(row[5]) < int(row[6])
    assert "trusted reusable Work record" in row[9]


def test_economics_general_math_avoids_full_pipeline(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)
    row = _row(output, "econ_general_math_mock")

    assert row[1] == "llm_general"
    assert row[3] == "0"
    assert row[4] == "0"
    assert "avoided the PlanGraph pipeline" in row[9]
    assert "live_gemini: false" in output


def test_economics_full_certificate_has_highest_routed_cost(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)
    rows = {
        name: _row(output, name)
        for name in [
            "econ_l0_reflex_turn_on_tv",
            "econ_direct_reuse_certificate",
            "econ_general_math_mock",
            "econ_full_certificate_pipeline",
        ]
    }
    full_cost = int(rows["econ_full_certificate_pipeline"][5])

    assert rows["econ_full_certificate_pipeline"][1] == "proof_full_pipeline"
    assert full_cost > int(rows["econ_l0_reflex_turn_on_tv"][5])
    assert full_cost > int(rows["econ_direct_reuse_certificate"][5])
    assert full_cost > int(rows["econ_general_math_mock"][5])
    assert "complex constrained task justifies" in rows["econ_full_certificate_pipeline"][9]


def test_economics_summary_fields_present(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)

    assert "total_routed_units:" in output
    assert "total_baseline_units:" in output
    assert "total_units_saved:" in output
    assert "savings_ratio:" in output
    assert "routed_llm_calls:" in output
    assert "baseline_llm_calls_estimate:" in output


def test_economics_output_says_simulated_not_provider_billing(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)

    assert "simulated model, not provider billing" in output
    assert "no real external actions were performed" in output


def test_economics_output_does_not_leak_sensitive_terms(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered


def test_economics_default_does_not_call_live_gemini(tmp_path):
    output = run_economics_benchmark(drs_root=tmp_path)

    assert "live_gemini: false" in output
    assert "llm_calls |" in output
