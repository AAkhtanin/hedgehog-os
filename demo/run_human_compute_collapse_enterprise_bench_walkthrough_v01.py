from __future__ import annotations

from demo.run_compute_collapse_enterprise_bench_v01 import (
    collect_compute_collapse_enterprise_bench_v01,
)


def render_human_compute_collapse_enterprise_bench_walkthrough_v01(report) -> str:
    source = report.source_evidence
    checkpoints = report.source_checkpoints
    purpose = report.benchmark_purpose
    request = report.enterprise_bench_request
    baseline = report.baseline_long_chain_estimate
    hedgehog = report.hedgehog_root_controlled_path
    metrics = report.compute_collapse_metrics
    boundaries = report.safety_authority_boundaries
    root = report.root_final

    lines = [
        "HEDGEHOG OS — HUMAN COMPUTE COLLAPSE ENTERPRISE BENCH WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "",
        "This is a human-readable walkthrough over the committed Compute Collapse "
        "Enterprise Bench v0.1 proof at bc606ff.",
        "",
        "It is deterministic local proof-only. It is not production economics, real "
        "billing, real latency measurement, real cloud cost measurement, killer demo "
        "authorization, or multi-LLM showcase authorization.",
        "",
        "It does not create a new runtime capability. It does not execute the naive "
        "baseline path. It does not call network or Gemini, use external APIs, "
        "execute external actions, write global DRS or External DRS, install Needles, "
        "invoke Marennya or UP, or create production persistence.",
        "",
        "Root remains final authority.",
        "",
        "2. WHAT THIS BENCHMARK EXTENDS",
        "",
        "Compute Collapse Enterprise Bench v0.1 is an enterprise extension of the "
        "earlier Economics / Compute Collapse reuse benchmark onto the dirty "
        "enterprise stack.",
        "",
        "It is not a duplicate and not a replacement for real economics measurement. "
        "It is a synthetic proof-level compute-collapse signal.",
        "",
        "3. WHY ENTERPRISE CHAOS MATTERS",
        "",
        "Enterprise Chaos Pack v0.1 is fully closed. Its commits are 082753e, "
        "104105b, 668a51a, and 03636b8.",
        "",
        "That checkpoint blocked 18 of 18 escalation attempts and quarantined plus "
        "blocked four attempts. This benchmark uses that dirty enterprise request "
        "family to compare an estimated naive long-chain path with Hedgehog's "
        "Root-controlled semantic routing and metadata reuse path.",
        "",
        "4. SOURCE CHECKPOINTS",
        "",
        *[
            f"{row['checkpoint_id']}: {row['checkpoint_status']} / "
            f"{row['closure_status']}."
            for row in checkpoints
        ],
        "",
        f"source_evidence_mode={source['source_evidence_mode']}.",
        f"source_collectors_replayed={str(source['source_collectors_replayed']).lower()}.",
        f"source_collectors_replayed_count={source['source_collectors_replayed_count']}.",
        "",
        "The source checkpoints are closed metadata, not replayed collectors.",
        "",
        "5. THE DIRTY ENTERPRISE REQUEST",
        "",
        f"request_id={request['request_id']}.",
        f"request_family={request['request_family']}.",
        "",
        "The request family includes connector observations, accepted evidence, stale "
        "legal state, DRS reuse, an external pointer claim, LLM SemanticDraft, "
        "NeedleCandidate, child-cell claim, GT advisory, ResultProposal bypass "
        "attempt, and conflicting sources.",
        "",
        "root_review_required=true.",
        "proof_only=true.",
        "",
        "6. BASELINE LONG-CHAIN ESTIMATE",
        "",
        f"path_id={baseline['path_id']}.",
        f"estimate_mode={baseline['estimate_mode']}.",
        f"real_llm_calls_executed={baseline['real_llm_calls_executed']}.",
        "",
        "The naive baseline is estimated, not executed.",
        "",
        f"baseline_llm_calls={baseline['baseline_llm_calls']}.",
        f"baseline_collector_replays={baseline['baseline_collector_replays']}.",
        f"baseline_validation_passes={baseline['baseline_validation_passes']}.",
        f"baseline_context_units={baseline['baseline_context_units']}.",
        f"baseline_action_planning_steps={baseline['baseline_action_planning_steps']}.",
        f"baseline_escalation_surfaces={baseline['baseline_escalation_surfaces']}.",
        f"baseline_unbounded_authority_risk_units="
        f"{baseline['baseline_unbounded_authority_risk_units']}.",
        f"baseline_failed_attempts={baseline['baseline_failed_attempts']}.",
        f"baseline_expensive_semantic_expansions="
        f"{baseline['baseline_expensive_semantic_expansions']}.",
        "",
        "7. HEDGEHOG ROOT-CONTROLLED PATH",
        "",
        f"path_id={hedgehog['path_id']}.",
        f"measurement_mode={hedgehog['measurement_mode']}.",
        "",
        "Hedgehog uses closed checkpoint metadata and Root-controlled reuse instead "
        "of replaying the previous stack.",
        "DRS reuse and closed checkpoint metadata are Root-approved semantic routing "
        "/ reuse signals, not authority. Root remains the final authority.",
        "",
        f"hedgehog_llm_calls={hedgehog['hedgehog_llm_calls']}.",
        f"bounded_llm_executor_nodes_used={hedgehog['bounded_llm_executor_nodes_used']}.",
        "The metric estimates one bounded Hedgehog LLM executor call in the routed "
        "path. The walkthrough itself executes no LLM, no Gemini, no network, and no "
        "API call.",
        f"hedgehog_collector_replays={hedgehog['hedgehog_collector_replays']}.",
        f"hedgehog_validation_passes={hedgehog['hedgehog_validation_passes']}.",
        f"hedgehog_context_units={hedgehog['hedgehog_context_units']}.",
        f"hedgehog_action_planning_steps={hedgehog['hedgehog_action_planning_steps']}.",
        f"hedgehog_unbounded_authority_risk_units="
        f"{hedgehog['hedgehog_unbounded_authority_risk_units']}.",
        f"hedgehog_failed_attempts={hedgehog['hedgehog_failed_attempts']}.",
        f"hedgehog_blocked_attempts={hedgehog['hedgehog_blocked_attempts']}.",
        f"hedgehog_quarantined_and_blocked="
        f"{hedgehog['hedgehog_quarantined_and_blocked']}.",
        "bounded_llm_use_only=true.",
        "",
        "8. COMPUTE COLLAPSE SIGNAL",
        "",
        f"benchmark_id={purpose['benchmark_id']}.",
        f"benchmark_type={purpose['benchmark_type']}.",
        f"comparison={purpose['comparison']}.",
        "synthetic_estimate=true.",
        "new_runtime_capability_created=false.",
        "",
        f"baseline_llm_calls={baseline['baseline_llm_calls']}.",
        f"hedgehog_llm_calls={hedgehog['hedgehog_llm_calls']}.",
        "The metric estimates one bounded Hedgehog LLM executor call in the routed "
        "path. The walkthrough itself executes no LLM, no Gemini, no network, and no "
        "API call.",
        f"llm_call_reduction={metrics['llm_call_reduction']}.",
        f"llm_call_reduction_ratio={metrics['llm_call_reduction_ratio']:.4f}.",
        "",
        f"baseline_context_units={baseline['baseline_context_units']}.",
        f"hedgehog_context_units={hedgehog['hedgehog_context_units']}.",
        f"context_unit_reduction={metrics['context_unit_reduction']}.",
        f"context_unit_reduction_ratio={metrics['context_unit_reduction_ratio']:.4f}.",
        "",
        f"collector_replay_reduction={metrics['collector_replay_reduction']}.",
        f"validation_pass_reduction={metrics['validation_pass_reduction']}.",
        f"action_planning_reduction={metrics['action_planning_reduction']}.",
        f"unbounded_authority_risk_reduction="
        f"{metrics['unbounded_authority_risk_reduction']}.",
        f"expensive_semantic_expansion_reduction="
        f"{metrics['expensive_semantic_expansion_reduction']}.",
        "",
        "These are proof-level units. They are not real billing, latency, or cloud "
        "cost measurements.",
        "",
        "9. SAFETY / AUTHORITY BOUNDARIES",
        "",
        f"root_remains_final_authority="
        f"{str(boundaries['root_remains_final_authority']).lower()}.",
        "closed_metadata_prevents_collector_replay=true.",
        "drs_reuse_prevents_unnecessary_recomputation=true.",
        "bounded_llm_use_only=true.",
        "llm_is_not_root=true.",
        "benchmark_does_not_execute_baseline=true.",
        "benchmark_does_not_authorize_action=true.",
        "benchmark_does_not_authorize_killer_demo=true.",
        "benchmark_does_not_authorize_multi_llm_showcase=true.",
        "no_network=true.",
        "no_gemini=true.",
        "no_external_action=true.",
        "no_global_drs_write=true.",
        "no_external_drs_write=true.",
        "no_installed_needle=true.",
        "no_production_persistence=true.",
        "no_marennya=true.",
        "no_up=true.",
        "audit_hash_decides_truth_false=true.",
        "",
        "10. WHAT THIS PROVES",
        "",
        "The benchmark proves a deterministic local compute-collapse signal for the "
        "dirty enterprise stack. Closed checkpoint metadata, DRS reuse, Root gates, "
        "and bounded LLM placement prevent unnecessary collector replay, validation "
        "repetition, action planning, and authority-risk expansion.",
        "",
        "It also shows that the permitted LLM use is bounded to one semantic executor "
        "node rather than an unbounded long-chain reasoning path.",
        "",
        "11. WHAT THIS DOES NOT PROVE",
        "",
        "It does not claim real cost savings, production economics, billing "
        "measurement, latency measurement, cloud cost measurement, or real-world "
        "performance.",
        "",
        "It does not authorize Killer Demo, multi-LLM showcase, real connector/API "
        "access, network or Gemini calls, external actions, global/external DRS "
        "writes, Needle installation, production persistence, Marennya, or UP.",
        "Killer Demo remains a future assembly target after maturity gates. It is not "
        "the next lifecycle step and is not authorized by this benchmark.",
        "",
        "12. ROOT FINAL",
        "",
        f"root_result={root['root_result']}.",
        f"safe_secondary_outcome={root['safe_secondary_outcome']}.",
        f"benchmark_status={root['benchmark_status']}.",
        "",
        "production_economics_claimed=false.",
        "real_billing_claimed=false.",
        "real_latency_claimed=false.",
        "real_cloud_cost_claimed=false.",
        "killer_demo_authorized=false.",
        "multi_llm_showcase_authorized=false.",
        "root_remains_final_authority=true.",
        "no_network=true.",
        "no_gemini=true.",
        "no_external_action=true.",
        "no_global_drs_write=true.",
        "no_external_drs_write=true.",
        "no_installed_needle=true.",
        "no_production_persistence=true.",
        "no_marennya=true.",
        "no_up=true.",
        "",
        "13. FINAL HUMAN SUMMARY",
        "",
        "Compute Collapse Enterprise Bench v0.1 proof is committed at bc606ff.",
        "It shows a synthetic proof-level signal: 29 estimated baseline LLM calls vs "
        "1 bounded Hedgehog LLM executor call.",
        "It shows context units reduced from 180 to 32.",
        "It reuses closed checkpoint metadata rather than replaying source collectors.",
        "It keeps Root as final authority.",
        "It does not claim real cost savings.",
        "It does not claim production economics.",
        "It does not claim billing or latency measurement.",
        "It does not authorize Killer Demo.",
        "Killer Demo remains a future assembly target after maturity gates.",
        "Next lifecycle step after this walkthrough is audit log, then docs sync.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_compute_collapse_enterprise_bench_walkthrough_v01() -> str:
    return render_human_compute_collapse_enterprise_bench_walkthrough_v01(
        collect_compute_collapse_enterprise_bench_v01()
    )


def main() -> int:
    print(run_human_compute_collapse_enterprise_bench_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
