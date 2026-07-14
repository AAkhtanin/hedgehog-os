from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

import pytest

from demo import run_airline_transaction_artifact_ledger_audit_v01 as audit
from demo import run_human_airline_transaction_artifact_ledger_timeline_v01 as timeline
from demo import run_tri_party_airline_live_semantic_lane_v01 as live_runner
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


def _proposal_payload(request: Mapping[str, Any], offer_id: str) -> dict[str, Any]:
    return {
        "proposal_id": f"semantic_offer_selection_proposal:{offer_id}",
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_bsep_projection_ref": request["source_bsep_projection_ref"],
        "source_client_constraint_set_id": request["source_client_constraint_set_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "candidate_set_ref": request["source_candidate_set_ref"],
        "recommended_offer_id": offer_id,
        "ranked_offer_ids": (offer_id,),
        "decision_factors": ("test_live_lane_semantic_tradeoff",),
        "preference_matches": ("test_soft_preference_match",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Test-only causal proposal.",
        "authority_created": False,
        "action_permission_created": False,
        "packet_created": False,
        "receipt_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "real_world_effects_count": 0,
    }


def _reviewer_payload(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "response_id": (
            f"canonical_actor_output:{request['actor_id']}:"
            f"{request['proposed_offer_id']}"
        ),
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_request_id": request["request_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "reviewed_offer_id": request["proposed_offer_id"],
        "review_role": request["actor_role"],
        "review_status": binding.STATUS_PASS,
        "semantic_factors": ("test_reviewer_supports_offer",),
        "blocking_conflicts": (),
        "supports_proposed_offer": True,
        "validation_status": binding.STATUS_PASS,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }


def _content_sensitive_causal_provider() -> live_runner.Provider:
    generic = live_runner.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if not isinstance(request, Mapping):
            return generic(actor_id, prompt, metadata)
        if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            soft = request["client_soft_preferences"]
            priority = tuple(soft["soft_preference_priority"])
            seat = tuple(soft["preferred_seat_characteristics"])
            offer_id = (
                binding.OFFER_B_ID
                if "extra_legroom_aisle" in priority or "extra_legroom" in seat
                else binding.OFFER_A_ID
            )
            return json.dumps(_proposal_payload(request, offer_id), sort_keys=True)
        return json.dumps(_reviewer_payload(request), sort_keys=True)

    return provider


@pytest.fixture(scope="session")
def valid_artifact_package(tmp_path_factory: pytest.TempPathFactory) -> Path:
    artifact_dir = tmp_path_factory.mktemp("airline_ledger_timeline_package")
    env = {
        live_runner.ENV_LANE: "1",
        live_runner.ENV_FAKE_PROVIDER: "1",
        live_runner.ENV_CAUSAL_BINDING: "1",
        live_runner.ENV_ARTIFACT_DIR: str(artifact_dir),
    }
    report = live_runner.collect_tri_party_airline_live_semantic_lane_v01(
        env=env,
        provider=_content_sensitive_causal_provider(),
        causal_constraints=binding.build_client_constraints_preference_a_v01(),
    )
    assert report["final_status"] == live_runner.STATUS_PASS
    return artifact_dir


def test_pass_audit_renders_exact_human_timeline(valid_artifact_package: Path) -> None:
    audit_report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=valid_artifact_package,
    )
    rendered = timeline.render_human_airline_transaction_artifact_ledger_timeline_v01(
        artifact_dir=valid_artifact_package,
    )

    assert audit_report.final_status == audit.PASS
    assert "[TIMELINE]" in rendered
    assert rendered.count("\n   artifact: ") == 19
    assert "ClientRootFinalV01" in rendered
    assert "AirlineRootFinalV01" in rendered
    assert "BankRootFinalV01" in rendered
    assert "Cross-root advisory is not a fourth Root." in rendered
    assert "Receipt did not create permission." in rendered
    assert "raw prompt" not in rendered.lower()
    assert "raw response" not in rendered.lower()
    assert "Crypto Artifact Seal implemented" not in rendered
    assert "Replay PASS" not in rendered
    assert "[FINAL STATUS]\nPASS" in rendered
    assert len(audit_report.timeline_rows) == 19


def test_timeline_uses_ledger_artifact_ids_and_dependencies(
    valid_artifact_package: Path,
) -> None:
    ledger = json.loads(
        (valid_artifact_package / audit.LEDGER_FILE).read_text(encoding="utf-8"),
    )
    audit_report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=valid_artifact_package,
    )

    assert tuple(row.artifact_type for row in audit_report.timeline_rows) == (
        ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    )
    for row, entry in zip(audit_report.timeline_rows, ledger["entries"]):
        assert row.artifact_id == entry["artifact_id"]
        assert row.depends_on == tuple(entry["depends_on"])


def test_fail_closed_and_skipped_render_no_success_story(
    valid_artifact_package: Path,
    tmp_path: Path,
) -> None:
    bad_package = tmp_path / "bad_package"
    shutil.copytree(valid_artifact_package, bad_package)
    (bad_package / audit.LEDGER_FILE).unlink()

    fail_rendered = (
        timeline.render_human_airline_transaction_artifact_ledger_timeline_v01(
            artifact_dir=bad_package,
        )
    )
    skipped_rendered = (
        timeline.render_human_airline_transaction_artifact_ledger_timeline_v01(
            env={},
        )
    )

    assert "FAIL_CLOSED" in fail_rendered
    assert "[TIMELINE]" not in fail_rendered
    assert "[FINAL STATUS]\nPASS" not in fail_rendered
    assert "SKIPPED_CLOSED" in skipped_rendered
    assert "[TIMELINE]" not in skipped_rendered
    assert "[FINAL STATUS]\nPASS" not in skipped_rendered


def test_renderer_calls_audit_collector_exactly_once_and_does_not_read_files(
    valid_artifact_package: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audit_report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=valid_artifact_package,
    )
    calls = {"count": 0}

    def fake_collect(*args: Any, **kwargs: Any) -> Any:
        calls["count"] += 1
        return audit_report

    def forbidden_read(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("timeline renderer reread package files")

    monkeypatch.setattr(
        timeline.audit,
        "collect_airline_transaction_artifact_ledger_audit_v01",
        fake_collect,
    )
    monkeypatch.setattr(Path, "read_text", forbidden_read)
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)

    rendered = timeline.render_human_airline_transaction_artifact_ledger_timeline_v01(
        artifact_dir=valid_artifact_package,
    )

    assert calls["count"] == 1
    assert "[FINAL STATUS]\nPASS" in rendered


def test_source_files_unchanged_after_audit_and_render(valid_artifact_package: Path) -> None:
    before = _source_bytes(valid_artifact_package)
    audit_report = audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=valid_artifact_package,
    )
    rendered = timeline.render_human_airline_transaction_artifact_ledger_timeline_v01(
        artifact_dir=valid_artifact_package,
    )
    after = _source_bytes(valid_artifact_package)

    assert audit_report.final_status == audit.PASS
    assert "[FINAL STATUS]\nPASS" in rendered
    assert before == after


def test_timeline_module_does_not_parse_package_separately() -> None:
    source = Path(timeline.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            calls.add(node.func.attr)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.add(node.func.id)

    assert "json" not in imports
    assert "read_text" not in calls
    assert "read_bytes" not in calls
    assert "loads" not in calls


def _source_bytes(package_dir: Path) -> dict[str, bytes]:
    return {
        filename: (package_dir / filename).read_bytes()
        for filename in audit.REQUIRED_SOURCE_FILES
    }
