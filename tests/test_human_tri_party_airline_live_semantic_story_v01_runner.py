from __future__ import annotations

import json
from pathlib import Path

import pytest

from demo import run_human_tri_party_airline_live_semantic_story_v01 as story
from demo import run_tri_party_airline_live_semantic_lane_v01 as live_runner


REAL_ARTIFACT_DIR = Path(
    ".tmp/tri_party_airline_live_semantic_lane/"
    "tri_party_airline_live_semantic_lane_real_20260709_184306",
)


def _source_artifacts(tmp_path: Path) -> Path:
    env = {
        live_runner.ENV_LANE: "1",
        live_runner.ENV_REAL_PROVIDER: "1",
        live_runner.ENV_ARTIFACT_DIR: str(tmp_path),
    }
    report = live_runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=env,
        provider=live_runner.build_fake_airline_semantic_provider_v01(),
    )
    assert report["final_status"] == live_runner.STATUS_PASS
    assert report["provider_mode"] == live_runner.PROVIDER_MODE_REAL
    return tmp_path


def _story_env(artifact_dir: Path, **extra: str) -> dict[str, str]:
    env = {story.ENV_ARTIFACT_DIR: str(artifact_dir)}
    env.update(extra)
    return env


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def test_human_airline_story_default_skipped_closed() -> None:
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(env={})
    counters = report["counter_table"]

    assert report["final_status"] == story.STATUS_SKIPPED_CLOSED
    assert report["skip_reason"] == "source_artifact_dir_not_selected"
    assert counters["renderer_provider_called_count"] == 0
    assert counters["renderer_network_called_count"] == 0
    assert counters["renderer_gemini_called_count"] == 0


def test_human_airline_story_collects_pass_from_valid_artifacts(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    assert report["source_run_identity"]["final_status"] == "PASS"
    assert report["final_status"] == story.STATUS_PASS
    assert len(report["actor_cards"]) == 12
    assert report["validation_errors"] == ()


def test_human_airline_story_requires_real_provider_source(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    summary_path = artifact_dir / "summary.json"
    summary = _read_json(summary_path)
    summary["provider_mode"] = "fake_provider"
    _write_json(summary_path, summary)

    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    assert report["final_status"] == story.STATUS_FAIL_CLOSED
    assert "source_provider_mode_not_real_provider" in report["validation_errors"]


def test_human_airline_story_bsep_before_architect(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    assert "BSEP был проверен до вызова Архитектора" in report["bsep_story"]
    assert len(report["bsep_projection_story"]) == 4
    assert all("status=PASS" in item for item in report["bsep_projection_story"])


def test_human_airline_story_all_12_actor_cards_complete(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    for card in report["actor_cards"]:
        assert card["input_context_summary"]
        assert card["output_semantic_summary"]
        assert card["what_runtime_used"]
        assert card["what_runtime_rejected"]
        assert card["validation_status"] == "PASS"
        assert card["authority_created"] is False
        assert card["action_permission_created"] is False
        assert card["real_world_effects_count"] == 0


def test_human_airline_story_semantic_outputs_are_real_inputs_to_story(
    tmp_path: Path,
) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    canonical_path = artifact_dir / "client_purchase_intent_reviewer_llm_canonical_summary.json"
    canonical = _read_json(canonical_path)
    canonical["semantic_summary"] = (
        "MUTATED CANONICAL CLIENT SUMMARY FROM ARTIFACT FOR STORY TEST"
    )
    _write_json(canonical_path, canonical)

    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )
    rendered = story.render_human_tri_party_airline_live_semantic_story_v01(report)
    card = next(
        item
        for item in report["actor_cards"]
        if item["actor_id"] == "client_purchase_intent_reviewer_llm"
    )

    assert "MUTATED CANONICAL CLIENT SUMMARY" in card["output_semantic_summary"]
    assert "MUTATED CANONICAL CLIENT SUMMARY" in rendered


def test_human_airline_story_vertical_dependencies(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )
    dependencies = {
        item["child_actor_id"]: item for item in report["vertical_dependency_story"]
    }

    assert len(dependencies) == 3
    assert (
        dependencies["airline_fare_rules_vertical_cell_llm"]["parent_actor_id"]
        == "airline_offer_policy_reviewer_llm"
    )
    assert (
        dependencies["airline_seat_baggage_vertical_cell_llm"]["parent_actor_id"]
        == "airline_offer_policy_reviewer_llm"
    )
    assert (
        dependencies["bank_idempotency_risk_vertical_cell_llm"]["parent_actor_id"]
        == "bank_payment_policy_reviewer_llm"
    )
    for dependency in dependencies.values():
        assert dependency["parent_validation_status"] == "PASS"
        assert dependency["child_started_after_parent_validation"] is True
        assert dependency["child_received_parent_canonical_summary"] is True
        assert dependency["child_received_parent_raw_response"] is False
        assert dependency["child_received_sibling_raw_output"] is False


def test_human_airline_story_horizontal_groups(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    assert report["client_actor_story"]
    assert report["airline_actor_story"]
    assert report["bank_actor_story"]
    assert report["cross_root_reviewer_story"]
    assert "not a fourth Root" in report["root_authority_story"]


def test_human_airline_story_runtime_used_rejected_visible(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )
    rendered = story.render_human_tri_party_airline_live_semantic_story_v01(report)

    assert len(report["what_runtime_used"]) == 12
    assert len(report["what_runtime_rejected"]) == 12
    assert "runtime_computed: provider output as truth" in rendered
    assert "runtime_computed: provider output as authority" in rendered


def test_human_airline_story_default_does_not_print_raw_or_full_prompts(
    tmp_path: Path,
) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    prompt_text = (artifact_dir / "tri_party_airline_orchestrator_llm_prompt.txt").read_text()
    raw_text = (
        artifact_dir / "tri_party_airline_orchestrator_llm_raw_response.txt"
    ).read_text()
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )
    rendered = story.render_human_tri_party_airline_live_semantic_story_v01(report)

    assert prompt_text not in rendered
    assert raw_text not in rendered
    assert "tri_party_airline_orchestrator_llm_prompt.txt" in rendered
    assert "tri_party_airline_orchestrator_llm_raw_response.txt" in rendered
    assert report["counter_table"]["full_prompts_printed_count"] == 0
    assert report["counter_table"]["raw_responses_printed_count"] == 0


def test_human_airline_story_explicit_transparency_mode(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    prompt_text = (artifact_dir / "tri_party_airline_orchestrator_llm_prompt.txt").read_text()
    raw_text = (
        artifact_dir / "tri_party_airline_orchestrator_llm_raw_response.txt"
    ).read_text()
    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(
            artifact_dir,
            **{
                story.ENV_ALLOW_PROMPT: "1",
                story.ENV_ALLOW_RAW: "1",
            },
        ),
    )
    rendered = story.render_human_tri_party_airline_live_semantic_story_v01(report)

    assert report["final_status"] == story.STATUS_PASS
    assert prompt_text in rendered
    assert raw_text in rendered
    assert "AIza" not in rendered
    assert report["counter_table"]["full_prompts_printed_count"] == 12
    assert report["counter_table"]["raw_responses_printed_count"] == 12


def test_human_airline_story_secret_scan_failure_fails_closed(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    secret_path = artifact_dir / "secret_scan.json"
    secret = _read_json(secret_path)
    secret["passed"] = False
    _write_json(secret_path, secret)

    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(
            artifact_dir,
            **{
                story.ENV_ALLOW_PROMPT: "1",
                story.ENV_ALLOW_RAW: "1",
            },
        ),
    )

    assert report["final_status"] == story.STATUS_FAIL_CLOSED
    assert "source_secret_scan_failed" in report["validation_errors"]
    assert report["counter_table"]["full_prompts_printed_count"] == 0
    assert report["counter_table"]["raw_responses_printed_count"] == 0


def test_human_airline_story_nonzero_effect_fails_closed(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    summary_path = artifact_dir / "summary.json"
    summary = _read_json(summary_path)
    summary["counter_table"]["real_payment_executed_count"] = 1
    _write_json(summary_path, summary)

    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    assert report["final_status"] == story.STATUS_FAIL_CLOSED
    assert "forbidden_counter_nonzero:real_payment_executed_count" in report[
        "validation_errors"
    ]


def test_human_airline_story_renderer_sections(tmp_path: Path) -> None:
    artifact_dir = _source_artifacts(tmp_path)
    rendered = story.run_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(artifact_dir),
    )

    for section in (
        "[HEDGEHOG OS — AIRLINE TRI-PARTY LIVE SEMANTIC HUMAN STORY]",
        "[ONE-SCREEN SUMMARY]",
        "[BUSINESS SCENE]",
        "[ONE TRANSACTION / THREE ROOTS]",
        "[SEMANTIC LANE TIMELINE]",
        "[BSEP MEMBRANE]",
        "[SIDE-SPECIFIC BSEP PROJECTIONS]",
        "[TRANSACTION ORCHESTRATOR]",
        "[SEMANTIC ARCHITECT]",
        "[HORIZONTAL SEMANTIC ACTORS]",
        "[CLIENT SIDE ACTORS]",
        "[AIRLINE SIDE ACTORS]",
        "[AIRLINE STRICT VERTICAL FRACTALS]",
        "[BANK SIDE ACTORS]",
        "[BANK STRICT VERTICAL FRACTAL]",
        "[CROSS-ROOT CONSISTENCY REVIEWER]",
        "[ALL 12 ACTOR CARDS]",
        "[WHAT EACH LLM RECEIVED]",
        "[WHAT EACH LLM RETURNED]",
        "[WHAT RUNTIME USED]",
        "[WHAT RUNTIME REJECTED]",
        "[HOW LLM OUTPUT CHANGED THE NEXT STEP]",
        "[MOCK HAPPY PATH]",
        "[ROOT / AUTHORITY BOUNDARIES]",
        "[PRIVACY / SECRET BOUNDARY]",
        "[ARTIFACT INVENTORY]",
        "[COUNTER TABLE]",
        "[NON-CLAIMS]",
        "[NEXT GATE]",
        "[FINAL STATUS]",
    ):
        assert section in rendered
    assert story.ONE_SCREEN_SUMMARY in rendered
    assert "mock payment authorization" in rendered
    assert "mock ticket evidence" in rendered
    assert "mock PNR" in rendered
    assert "vertical child is not a parallel decorative actor" in rendered or "STRICT VERTICAL" in rendered


def test_human_airline_story_source_import_boundary() -> None:
    source = Path(story.__file__).read_text()

    assert "google.genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "import config" not in source
    assert "provider_adapter" not in source
    assert "collect_tri_party_airline_live_semantic_lane_v01" not in source
    assert "production " + "ready" not in source
    assert "public auditor " + "ready" not in source


def test_human_airline_story_optional_real_artifact_compatibility() -> None:
    if not REAL_ARTIFACT_DIR.exists():
        pytest.skip("real Airline live semantic artifact directory absent")

    report = story.collect_human_tri_party_airline_live_semantic_story_v01(
        env=_story_env(REAL_ARTIFACT_DIR),
    )

    assert report["final_status"] == story.STATUS_PASS
    assert len(report["actor_cards"]) == 12
