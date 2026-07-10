from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


RUN_ID = "human_tri_party_airline_live_semantic_story_v01"
REPORT_ID = "human_tri_party_airline_live_semantic_story_v01"
STORY_TYPE = "artifact_backed_human_airline_live_semantic_story"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_SKIPPED_CLOSED = "SKIPPED_CLOSED"

ENV_ARTIFACT_DIR = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_STORY_ARTIFACT_DIR"
ENV_AUDIT_LOG = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_STORY_AUDIT_LOG"
ENV_ALLOW_RAW = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_STORY_ALLOW_RAW_RESPONSE_OUTPUT"
ENV_ALLOW_PROMPT = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_STORY_ALLOW_FULL_PROMPT_OUTPUT"

DEFAULT_AUDIT_LOG = (
    "docs/audit_reports/auditor_tri_party_airline_live_semantic_lane_real_run_v01.log"
)
TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"
MODEL = "gemini-2.5-flash"
NEXT_GATE = "airline_ticket_purchase_corridor_artifact_ledger_crypto_replay_preflight"

ONE_SCREEN_SUMMARY = (
    "Двенадцать реальных Gemini-акторов разобрали одну mock-авиасделку со "
    "стороны клиента, авиакомпании и банка. Их ответы действительно повлияли "
    "на семантическую обработку через extraction, validation и canonicalization, "
    "но не получили власть: BSEP ограничил контекст, Root-границы сохранились, "
    "а успешный путь закончился только mock-авторизацией платежа, mock-ticket "
    "evidence и mock-PNR без реального платежа, билета или бронирования."
)

ACTOR_IDS = (
    "tri_party_airline_orchestrator_llm",
    "tri_party_airline_semantic_architect_llm",
    "client_purchase_intent_reviewer_llm",
    "client_profile_privacy_reviewer_llm",
    "airline_offer_policy_reviewer_llm",
    "airline_fare_rules_vertical_cell_llm",
    "airline_seat_baggage_vertical_cell_llm",
    "airline_ticketing_policy_reviewer_llm",
    "bank_payment_policy_reviewer_llm",
    "bank_idempotency_risk_vertical_cell_llm",
    "bank_payment_status_explainer_llm",
    "tri_party_evidence_consistency_reviewer_llm",
)

HUMAN_ROLE_NAMES = {
    "tri_party_airline_orchestrator_llm": "Оркестратор всей авиасделки",
    "tri_party_airline_semantic_architect_llm": "Семантический архитектор сделки",
    "client_purchase_intent_reviewer_llm": "Разборщик намерения и предпочтений клиента",
    "client_profile_privacy_reviewer_llm": "Проверяющий приватность клиентского профиля",
    "airline_offer_policy_reviewer_llm": "Проверяющий предложения и правила авиакомпании",
    "airline_fare_rules_vertical_cell_llm": "Дочерняя ячейка правил тарифа",
    "airline_seat_baggage_vertical_cell_llm": "Дочерняя ячейка места и багажа",
    "airline_ticketing_policy_reviewer_llm": "Проверяющий условия mock-выпуска билета",
    "bank_payment_policy_reviewer_llm": "Проверяющий политику mock-платежа банка",
    "bank_idempotency_risk_vertical_cell_llm": "Дочерняя ячейка банковского риска и идемпотентности",
    "bank_payment_status_explainer_llm": "Объясняющий авторизацию и расчётный статус",
    "tri_party_evidence_consistency_reviewer_llm": "Межсторонний проверяющий согласованность доказательств",
}

VERTICAL_PARENT_BY_CHILD = {
    "airline_fare_rules_vertical_cell_llm": "airline_offer_policy_reviewer_llm",
    "airline_seat_baggage_vertical_cell_llm": "airline_offer_policy_reviewer_llm",
    "bank_idempotency_risk_vertical_cell_llm": "bank_payment_policy_reviewer_llm",
}

REQUIRED_SOURCE_FILES = (
    "summary.json",
    "summary.log",
    "secret_scan.json",
    "tri_party_airline_bsep_packet.json",
    "tri_party_airline_bsep_validation.json",
    "tri_party_airline_bsep_side_projections.json",
)

SOURCE_COUNTER_EXPECTATIONS = {
    "semantic_actor_call_count": 12,
    "real_provider_call_count": 12,
    "fake_provider_call_count": 0,
    "network_used_count": 12,
    "gemini_called_count": 12,
    "semantic_actor_validation_pass_count": 12,
    "semantic_actor_validation_fail_count": 0,
    "bsep_created_count": 1,
    "bsep_validated_count": 1,
    "bsep_side_projection_count": 4,
    "provider_output_used_as_truth_count": 0,
    "provider_output_used_as_authority_count": 0,
    "provider_output_created_packet_count": 0,
    "provider_output_created_receipt_count": 0,
    "provider_output_created_payment_count": 0,
    "provider_output_created_ticket_count": 0,
    "provider_output_created_booking_count": 0,
    "cross_root_authority_transfer_count": 0,
    "real_airline_api_called_count": 0,
    "real_bank_api_called_count": 0,
    "real_gds_api_called_count": 0,
    "real_payment_executed_count": 0,
    "real_ticket_issued_count": 0,
    "real_booking_created_count": 0,
    "real_world_effects_count": 0,
}

FORBIDDEN_COUNTER_KEYS = (
    "provider_output_used_as_truth_count",
    "provider_output_used_as_authority_count",
    "provider_output_created_packet_count",
    "provider_output_created_receipt_count",
    "provider_output_created_payment_count",
    "provider_output_created_ticket_count",
    "provider_output_created_booking_count",
    "cross_root_authority_transfer_count",
    "real_airline_api_called_count",
    "real_bank_api_called_count",
    "real_gds_api_called_count",
    "real_payment_executed_count",
    "real_ticket_issued_count",
    "real_booking_created_count",
    "real_world_effects_count",
)

SAFE_FALSE_FIELDS = (
    "authority_created",
    "action_permission_created",
    "packet_created",
    "receipt_created",
    "payment_created",
    "ticket_created",
    "booking_created",
    "final_output_created",
)


def collect_human_tri_party_airline_live_semantic_story_v01(
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    effective_env = dict(os.environ if env is None else env)
    artifact_dir_value = effective_env.get(ENV_ARTIFACT_DIR, "").strip()
    audit_log_value = effective_env.get(ENV_AUDIT_LOG, DEFAULT_AUDIT_LOG).strip()

    if not artifact_dir_value:
        return _skipped_report(audit_log_value)

    artifact_dir = Path(artifact_dir_value)
    audit_log = Path(audit_log_value)
    allow_prompt_requested = effective_env.get(ENV_ALLOW_PROMPT) == "1"
    allow_raw_requested = effective_env.get(ENV_ALLOW_RAW) == "1"

    validation_errors: list[str] = []
    loaded = _load_source_artifacts(artifact_dir, audit_log, validation_errors)
    if validation_errors:
        return _failed_report(
            artifact_dir=artifact_dir,
            audit_log=audit_log,
            validation_errors=validation_errors,
        )

    summary = loaded["summary"]
    secret_scan = loaded["secret_scan"]
    allow_prompt = allow_prompt_requested and secret_scan.get("passed") is True
    allow_raw = allow_raw_requested and secret_scan.get("passed") is True
    source_actor_reports = {
        item.get("actor_id"): item for item in summary.get("semantic_actor_reports", [])
    }
    actor_cards = _build_actor_cards(
        artifact_dir=artifact_dir,
        source_actor_reports=source_actor_reports,
        allow_prompt=allow_prompt,
        allow_raw=allow_raw,
        validation_errors=validation_errors,
    )
    validation_errors.extend(
        _validate_source(
            summary=summary,
            secret_scan=secret_scan,
            bsep_validation=loaded["bsep_validation"],
            bsep_side_projections=loaded["bsep_side_projections"],
            actor_cards=actor_cards,
            audit_log_text=loaded["audit_log_text"],
        ),
    )

    final_status = STATUS_PASS if not validation_errors else STATUS_FAIL_CLOSED
    if final_status != STATUS_PASS:
        allow_prompt = False
        allow_raw = False
        for card in actor_cards:
            card["prompt_displayed_in_full"] = False
            card["raw_response_displayed"] = False
            card.pop("prompt_text_for_display", None)
            card.pop("raw_response_text_for_display", None)

    bsep_projection_story = _bsep_projection_story(loaded["bsep_side_projections"])
    vertical_dependency_story = _vertical_dependency_story(actor_cards)
    counter_table = _counter_table(
        summary=summary,
        secret_scan=secret_scan,
        actor_cards=actor_cards,
        allow_prompt=allow_prompt,
        allow_raw=allow_raw,
    )

    report = {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": final_status,
        "skip_reason": "",
        "source_artifact_dir": str(artifact_dir),
        "source_audit_log": str(audit_log),
        "source_run_identity": _source_run_identity(summary),
        "one_screen_summary": ONE_SCREEN_SUMMARY,
        "business_scene": _business_scene(),
        "transaction_identity": _transaction_identity(summary),
        "three_root_story": _three_root_story(),
        "semantic_lane_timeline": _semantic_lane_timeline(summary),
        "bsep_story": _bsep_story(loaded["bsep_packet"], loaded["bsep_validation"]),
        "bsep_projection_story": bsep_projection_story,
        "actor_cards": actor_cards,
        "transaction_orchestrator_story": _actor_story(actor_cards, "tri_party_airline_orchestrator_llm"),
        "semantic_architect_story": _actor_story(actor_cards, "tri_party_airline_semantic_architect_llm"),
        "client_actor_story": _group_story(actor_cards, "client"),
        "airline_actor_story": _group_story(actor_cards, "airline", include_vertical=False),
        "airline_vertical_fractal_story": _vertical_group_story(actor_cards, "airline"),
        "bank_actor_story": _group_story(actor_cards, "bank", include_vertical=False),
        "bank_vertical_fractal_story": _vertical_group_story(actor_cards, "bank"),
        "cross_root_reviewer_story": _group_story(actor_cards, "cross_root_advisory"),
        "horizontal_actor_story": _horizontal_actor_story(summary),
        "vertical_dependency_story": vertical_dependency_story,
        "what_each_llm_received": {
            card["actor_id"]: card["input_context_summary"] for card in actor_cards
        },
        "what_each_llm_returned": {
            card["actor_id"]: card["output_semantic_summary"] for card in actor_cards
        },
        "what_runtime_used": {
            card["actor_id"]: card["what_runtime_used"] for card in actor_cards
        },
        "what_runtime_rejected": {
            card["actor_id"]: card["what_runtime_rejected"] for card in actor_cards
        },
        "semantic_influence_map": _semantic_influence_map(),
        "mock_happy_path": _mock_happy_path(),
        "root_authority_story": _root_authority_story(),
        "privacy_secret_story": _privacy_secret_story(secret_scan),
        "artifact_inventory": _artifact_inventory(artifact_dir),
        "counter_table": counter_table,
        "non_claims": _non_claims(),
        "validation_errors": tuple(validation_errors),
        "next_gate": NEXT_GATE,
    }
    return report


def render_human_tri_party_airline_live_semantic_story_v01(
    report: Mapping[str, Any],
) -> str:
    lines = [
        "[HEDGEHOG OS — AIRLINE TRI-PARTY LIVE SEMANTIC HUMAN STORY]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"story_type: {report['story_type']}",
        f"final_status: {report['final_status']}",
        f"source_artifact_dir: {report['source_artifact_dir']}",
        f"source_audit_log: {report['source_audit_log']}",
    ]
    if report["final_status"] == STATUS_SKIPPED_CLOSED:
        lines.extend(
            (
                "",
                "[FINAL STATUS]",
                str(report["final_status"]),
                f"skip_reason: {report['skip_reason']}",
            ),
        )
        return "\n".join(lines)

    lines.extend(
        (
            "",
            "[ONE-SCREEN SUMMARY]",
            str(report["one_screen_summary"]),
            "",
            "[BUSINESS SCENE]",
            str(report["business_scene"]),
            "",
            "[ONE TRANSACTION / THREE ROOTS]",
            str(report["three_root_story"]),
            "",
            "[SEMANTIC LANE TIMELINE]",
        ),
    )
    lines.extend(f"- {item}" for item in report["semantic_lane_timeline"])

    lines.extend(("", "[BSEP MEMBRANE]", str(report["bsep_story"])))
    lines.extend(("", "[SIDE-SPECIFIC BSEP PROJECTIONS]"))
    for item in report["bsep_projection_story"]:
        lines.append(f"- {item}")

    lines.extend(("", "[TRANSACTION ORCHESTRATOR]", str(report["transaction_orchestrator_story"])))
    lines.extend(("", "[SEMANTIC ARCHITECT]", str(report["semantic_architect_story"])))
    lines.extend(("", "[HORIZONTAL SEMANTIC ACTORS]", str(report["horizontal_actor_story"])))
    lines.extend(("", "[CLIENT SIDE ACTORS]"))
    lines.extend(f"- {item}" for item in report["client_actor_story"])
    lines.extend(("", "[AIRLINE SIDE ACTORS]"))
    lines.extend(f"- {item}" for item in report["airline_actor_story"])
    lines.extend(("", "[AIRLINE STRICT VERTICAL FRACTALS]"))
    lines.append(
        "vertical child is not a parallel decorative actor; children receive "
        "parent canonical summary, not parent raw response or sibling raw output, "
        "and children do not create authority or actions.",
    )
    lines.extend(f"- {item}" for item in report["airline_vertical_fractal_story"])
    lines.extend(("", "[BANK SIDE ACTORS]"))
    lines.extend(f"- {item}" for item in report["bank_actor_story"])
    lines.extend(("", "[BANK STRICT VERTICAL FRACTAL]"))
    lines.append(
        "vertical child is not a parallel decorative actor; bank risk child starts "
        "only after Bank payment parent PASS and returns upward.",
    )
    lines.extend(f"- {item}" for item in report["bank_vertical_fractal_story"])
    lines.extend(("", "[CROSS-ROOT CONSISTENCY REVIEWER]"))
    lines.extend(f"- {item}" for item in report["cross_root_reviewer_story"])

    lines.extend(("", "[ALL 12 ACTOR CARDS]"))
    for card in report["actor_cards"]:
        lines.extend(_render_actor_card(card))

    lines.extend(("", "[WHAT EACH LLM RECEIVED]"))
    for actor_id, summary in report["what_each_llm_received"].items():
        lines.append(f"- {actor_id}: {summary}")

    lines.extend(("", "[WHAT EACH LLM RETURNED]"))
    for actor_id, summary in report["what_each_llm_returned"].items():
        lines.append(f"- {actor_id}: {summary}")

    lines.extend(("", "[WHAT RUNTIME USED]"))
    for actor_id, used in report["what_runtime_used"].items():
        lines.append(f"- {actor_id}: {', '.join(used)}")

    lines.extend(("", "[WHAT RUNTIME REJECTED]"))
    for actor_id, rejected in report["what_runtime_rejected"].items():
        lines.append(f"- {actor_id}: {', '.join(rejected)}")

    lines.extend(("", "[HOW LLM OUTPUT CHANGED THE NEXT STEP]"))
    for item in report["semantic_influence_map"]:
        lines.append(f"- {item}")

    lines.extend(("", "[MOCK HAPPY PATH]", str(report["mock_happy_path"])))
    lines.extend(("", "[ROOT / AUTHORITY BOUNDARIES]", str(report["root_authority_story"])))
    lines.extend(("", "[PRIVACY / SECRET BOUNDARY]", str(report["privacy_secret_story"])))
    lines.extend(("", "[ARTIFACT INVENTORY]"))
    for key, value in report["artifact_inventory"].items():
        lines.append(f"{key}: {value}")
    lines.extend(("", "[COUNTER TABLE]"))
    for key in sorted(report["counter_table"]):
        lines.append(f"{key}: {report['counter_table'][key]}")
    lines.extend(("", "[NON-CLAIMS]"))
    lines.extend(f"- {claim}" for claim in report["non_claims"])
    lines.extend(("", "[NEXT GATE]", str(report["next_gate"])))
    lines.extend(("", "[FINAL STATUS]", str(report["final_status"])))
    if report["validation_errors"]:
        lines.append(f"validation_errors: {report['validation_errors']}")
    return "\n".join(lines)


def run_human_tri_party_airline_live_semantic_story_v01(
    *,
    env: Mapping[str, str] | None = None,
) -> str:
    return render_human_tri_party_airline_live_semantic_story_v01(
        collect_human_tri_party_airline_live_semantic_story_v01(env=env),
    )


def main() -> int:
    print(run_human_tri_party_airline_live_semantic_story_v01())
    return 0


def _skipped_report(audit_log_value: str) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": STATUS_SKIPPED_CLOSED,
        "skip_reason": "source_artifact_dir_not_selected",
        "source_artifact_dir": "",
        "source_audit_log": audit_log_value,
        "source_run_identity": {},
        "one_screen_summary": "",
        "business_scene": "",
        "transaction_identity": {},
        "three_root_story": "",
        "semantic_lane_timeline": (),
        "bsep_story": "",
        "bsep_projection_story": (),
        "actor_cards": (),
        "transaction_orchestrator_story": "",
        "semantic_architect_story": "",
        "client_actor_story": (),
        "airline_actor_story": (),
        "airline_vertical_fractal_story": (),
        "bank_actor_story": (),
        "bank_vertical_fractal_story": (),
        "cross_root_reviewer_story": (),
        "horizontal_actor_story": "",
        "vertical_dependency_story": (),
        "what_each_llm_received": {},
        "what_each_llm_returned": {},
        "what_runtime_used": {},
        "what_runtime_rejected": {},
        "semantic_influence_map": (),
        "mock_happy_path": "",
        "root_authority_story": "",
        "privacy_secret_story": "",
        "artifact_inventory": {},
        "counter_table": _skipped_counter_table(),
        "non_claims": _non_claims(),
        "validation_errors": (),
        "next_gate": NEXT_GATE,
    }


def _failed_report(
    *,
    artifact_dir: Path,
    audit_log: Path,
    validation_errors: list[str],
) -> dict[str, Any]:
    report = _skipped_report(str(audit_log))
    report.update(
        {
            "final_status": STATUS_FAIL_CLOSED,
            "skip_reason": "",
            "source_artifact_dir": str(artifact_dir),
            "validation_errors": tuple(validation_errors),
        },
    )
    return report


def _load_source_artifacts(
    artifact_dir: Path,
    audit_log: Path,
    validation_errors: list[str],
) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    if not artifact_dir.exists():
        validation_errors.append("source_artifact_dir_missing")
        return loaded
    for name in REQUIRED_SOURCE_FILES:
        if not (artifact_dir / name).exists():
            validation_errors.append(f"missing_required_source_file:{name}")
    if not audit_log.exists():
        validation_errors.append("source_audit_log_missing")
    if validation_errors:
        return loaded
    for name, key in (
        ("summary.json", "summary"),
        ("secret_scan.json", "secret_scan"),
        ("tri_party_airline_bsep_packet.json", "bsep_packet"),
        ("tri_party_airline_bsep_validation.json", "bsep_validation"),
        ("tri_party_airline_bsep_side_projections.json", "bsep_side_projections"),
    ):
        loaded[key] = _read_json(artifact_dir / name, validation_errors)
    loaded["summary_log_text"] = (artifact_dir / "summary.log").read_text()
    loaded["audit_log_text"] = audit_log.read_text()
    return loaded


def _read_json(path: Path, validation_errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        validation_errors.append(f"invalid_json:{path.name}:{exc.msg}")
        return {}
    if not isinstance(value, dict):
        validation_errors.append(f"json_root_not_object:{path.name}")
        return {}
    return value


def _build_actor_cards(
    *,
    artifact_dir: Path,
    source_actor_reports: Mapping[str, Mapping[str, Any]],
    allow_prompt: bool,
    allow_raw: bool,
    validation_errors: list[str],
) -> tuple[dict[str, Any], ...]:
    cards: list[dict[str, Any]] = []
    transactions: set[str] = set()
    for index, actor_id in enumerate(ACTOR_IDS, start=1):
        source_report = source_actor_reports.get(actor_id)
        if not source_report:
            validation_errors.append(f"missing_actor_report:{actor_id}")
            source_report = {}
        paths = {
            "prompt": artifact_dir / f"{actor_id}_prompt.txt",
            "raw": artifact_dir / f"{actor_id}_raw_response.txt",
            "extracted": artifact_dir / f"{actor_id}_extracted_json_candidate.json",
            "validation": artifact_dir / f"{actor_id}_validation.json",
            "canonical": artifact_dir / f"{actor_id}_canonical_summary.json",
        }
        for label, path in paths.items():
            if not path.exists():
                validation_errors.append(f"missing_actor_{label}_artifact:{actor_id}")
        prompt_text = paths["prompt"].read_text() if paths["prompt"].exists() else ""
        raw_text = paths["raw"].read_text() if paths["raw"].exists() else ""
        extracted = _read_json(paths["extracted"], validation_errors) if paths["extracted"].exists() else {}
        validation = _read_json(paths["validation"], validation_errors) if paths["validation"].exists() else {}
        canonical = _read_json(paths["canonical"], validation_errors) if paths["canonical"].exists() else {}
        for value in (extracted.get("transaction_id"), canonical.get("transaction_id")):
            if isinstance(value, str):
                transactions.add(value)
        card = {
            "actor_index": index,
            "actor_id": actor_id,
            "side": canonical.get("side") or source_report.get("side", ""),
            "human_role_name": HUMAN_ROLE_NAMES[actor_id],
            "validation_status": validation.get("validation_status", ""),
            "accepted": validation.get("accepted", False),
            "input_context_summary": source_report.get("input_context_summary", ""),
            "prompt_artifact_path": str(paths["prompt"]),
            "prompt_character_count": len(prompt_text),
            "prompt_displayed_in_full": allow_prompt,
            "raw_response_artifact_path": str(paths["raw"]),
            "raw_response_character_count": len(raw_text),
            "raw_response_displayed": allow_raw,
            "extracted_json_artifact_path": str(paths["extracted"]),
            "validation_artifact_path": str(paths["validation"]),
            "canonical_summary_artifact_path": str(paths["canonical"]),
            "output_semantic_summary": canonical.get("semantic_summary", ""),
            "what_runtime_used": tuple(canonical.get("what_runtime_used", ())),
            "what_runtime_rejected": tuple(canonical.get("what_runtime_rejected", ())),
            "semantic_effect_on_next_stage": _semantic_effect_for_actor(actor_id),
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
        if allow_prompt:
            card["prompt_text_for_display"] = prompt_text
        if allow_raw:
            card["raw_response_text_for_display"] = raw_text
        if actor_id in VERTICAL_PARENT_BY_CHILD:
            card.update(
                {
                    "vertical_fractal_cell": True,
                    "parent_actor_id": source_report.get(
                        "parent_actor_id",
                        VERTICAL_PARENT_BY_CHILD[actor_id],
                    ),
                    "parent_validation_status": source_report.get(
                        "parent_validation_status",
                        STATUS_PASS,
                    ),
                    "child_started_after_parent_validation": source_report.get(
                        "child_started_after_parent_validation",
                        False,
                    ),
                    "child_received_parent_canonical_summary": source_report.get(
                        "child_received_parent_canonical_summary",
                        False,
                    ),
                    "child_received_parent_raw_response": source_report.get(
                        "child_received_parent_raw_response",
                        True,
                    ),
                    "child_received_sibling_raw_output": source_report.get(
                        "child_received_sibling_raw_output",
                        True,
                    ),
                    "child_received_unbounded_context": source_report.get(
                        "child_received_unbounded_context",
                        True,
                    ),
                    "child_result_returns_to_parent_or_root_review": source_report.get(
                        "child_result_returns_to_parent_or_root_review",
                        False,
                    ),
                },
            )
        cards.append(card)
    if transactions != {TRANSACTION_ID}:
        validation_errors.append("transaction_id_mismatch_across_actor_artifacts")
    return tuple(cards)


def _validate_source(
    *,
    summary: Mapping[str, Any],
    secret_scan: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    bsep_side_projections: Mapping[str, Any],
    actor_cards: tuple[Mapping[str, Any], ...],
    audit_log_text: str,
) -> list[str]:
    errors: list[str] = []
    counters = summary.get("counter_table", {})
    if summary.get("final_status") != STATUS_PASS:
        errors.append("source_summary_final_status_not_pass")
    if summary.get("provider_mode") != "real_provider":
        errors.append("source_provider_mode_not_real_provider")
    if summary.get("model") != MODEL:
        errors.append("source_model_not_gemini_2_5_flash")
    for key, expected in SOURCE_COUNTER_EXPECTATIONS.items():
        if counters.get(key) != expected:
            errors.append(f"source_counter_mismatch:{key}")
    if bsep_validation.get("validation_status") != STATUS_PASS:
        errors.append("bsep_validation_not_pass")
    if len(bsep_side_projections) != 4:
        errors.append("bsep_projection_count_not_four")
    for projection_id in (
        "client_bsep_projection",
        "airline_bsep_projection",
        "bank_bsep_projection",
        "cross_root_bsep_projection",
    ):
        projection = bsep_side_projections.get(projection_id, {})
        if projection.get("validation_status") != STATUS_PASS:
            errors.append(f"bsep_projection_not_pass:{projection_id}")
    for card in actor_cards:
        if card["validation_status"] != STATUS_PASS or card["accepted"] is not True:
            errors.append(f"actor_validation_not_pass:{card['actor_id']}")
        if not card["input_context_summary"]:
            errors.append(f"empty_actor_input_summary:{card['actor_id']}")
        if not card["output_semantic_summary"]:
            errors.append(f"empty_actor_output_summary:{card['actor_id']}")
        if not card["what_runtime_used"]:
            errors.append(f"empty_runtime_used:{card['actor_id']}")
        if not card["what_runtime_rejected"]:
            errors.append(f"empty_runtime_rejected:{card['actor_id']}")
        for field in SAFE_FALSE_FIELDS:
            if card.get(field) is not False:
                errors.append(f"actor_forbidden_flag_true:{card['actor_id']}:{field}")
        if card.get("real_world_effects_count") != 0:
            errors.append(f"actor_effects_nonzero:{card['actor_id']}")
    if secret_scan.get("passed") is not True:
        errors.append("source_secret_scan_failed")
    if secret_scan.get("matched_markers") != []:
        errors.append("source_secret_markers_present")
    for key in FORBIDDEN_COUNTER_KEYS:
        if counters.get(key) != 0:
            errors.append(f"forbidden_counter_nonzero:{key}")
    if "audit_status: PASS" not in audit_log_text:
        errors.append("source_audit_log_not_pass")
    return errors


def _source_run_identity(summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": summary.get("run_id"),
        "report_id": summary.get("report_id"),
        "lane_id": summary.get("lane_id"),
        "provider_mode": summary.get("provider_mode"),
        "model": summary.get("model"),
        "final_status": summary.get("final_status"),
    }


def _transaction_identity(summary: Mapping[str, Any]) -> Mapping[str, Any]:
    identity = summary.get("transaction_identity", {})
    if isinstance(identity, Mapping):
        return identity
    return {"transaction_id": TRANSACTION_ID}


def _business_scene() -> str:
    return (
        "Клиент хочет mock-покупку авиабилета PAR -> LIM с бюджетом, багажом, "
        "местом и банковской mock-авторизацией. История показывает только "
        "artifact-backed presentation поверх завершённого real_provider прогона."
    )


def _three_root_story() -> str:
    return (
        "ClientRoot, AirlineRoot и BankRoot рассматривают одну transaction_id. "
        "Они обмениваются evidence-only результатами, но не передают власть между сторонами."
    )


def _semantic_lane_timeline(summary: Mapping[str, Any]) -> tuple[str, ...]:
    order = summary.get("semantic_actor_call_order", ())
    timeline = [
        "Orchestrator accepted semantics -> runtime created BSEP candidate.",
        "BSEP validation PASS -> Architect call allowed.",
        "Architect accepted semantics -> side projections exposed.",
    ]
    timeline.extend(f"actor call: {actor_id}" for actor_id in order)
    timeline.append("Runtime canonical summaries support the human mock happy-path story.")
    return tuple(timeline)


def _bsep_story(
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
) -> str:
    return (
        "Оркестратор не передал raw output напрямую Архитектору. Runtime извлёк "
        "и проверил семантическое предложение, создал BSEP, и BSEP был проверен "
        "до вызова Архитектора. Затем были созданы четыре bounded projections: "
        "client, airline, bank, cross-root. BSEP не является truth, authority, "
        "permission, packet, receipt, payment, ticket, booking или FinalOutput. "
        f"bsep_packet_id: {bsep_packet.get('bsep_packet_id')}; "
        f"validation_status: {bsep_validation.get('validation_status')}."
    )


def _bsep_projection_story(projections: Mapping[str, Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(
        f"{projection_id}: side={projection.get('side')}, status={projection.get('validation_status')}, "
        f"bounded={projection.get('bounded_context_summary')}"
        for projection_id, projection in sorted(projections.items())
    )


def _actor_story(cards: tuple[Mapping[str, Any], ...], actor_id: str) -> str:
    card = _card_by_id(cards, actor_id)
    return f"{card['human_role_name']}: {card['output_semantic_summary']}"


def _group_story(
    cards: tuple[Mapping[str, Any], ...],
    side: str,
    *,
    include_vertical: bool = True,
) -> tuple[str, ...]:
    rows = []
    for card in cards:
        if card["side"] != side:
            continue
        if not include_vertical and card.get("vertical_fractal_cell"):
            continue
        rows.append(f"{card['human_role_name']}: {card['output_semantic_summary']}")
    return tuple(rows)


def _vertical_group_story(cards: tuple[Mapping[str, Any], ...], side: str) -> tuple[str, ...]:
    return tuple(
        (
            f"{card['human_role_name']} starts after {card['parent_actor_id']} PASS, "
            "uses parent canonical summary, and returns advisory child result upward."
        )
        for card in cards
        if card["side"] == side and card.get("vertical_fractal_cell")
    )


def _horizontal_actor_story(summary: Mapping[str, Any]) -> str:
    groups = summary.get("horizontal_actor_groups", {})
    return (
        "Client, airline, and bank parent actors received bounded side projections. "
        "Horizontal actors do not require sibling raw outputs and return validated "
        f"canonical semantic results upward. groups={groups}"
    )


def _vertical_dependency_story(cards: tuple[Mapping[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    dependencies = []
    for card in cards:
        if not card.get("vertical_fractal_cell"):
            continue
        dependencies.append(
            {
                "child_actor_id": card["actor_id"],
                "parent_actor_id": card["parent_actor_id"],
                "parent_validation_status": card["parent_validation_status"],
                "child_started_after_parent_validation": card[
                    "child_started_after_parent_validation"
                ],
                "child_received_parent_canonical_summary": card[
                    "child_received_parent_canonical_summary"
                ],
                "child_received_parent_raw_response": card[
                    "child_received_parent_raw_response"
                ],
                "child_received_sibling_raw_output": card[
                    "child_received_sibling_raw_output"
                ],
                "child_received_unbounded_context": card[
                    "child_received_unbounded_context"
                ],
                "child_result_returns_to_parent_or_root_review": card[
                    "child_result_returns_to_parent_or_root_review"
                ],
                "child_creates_authority": False,
                "child_creates_action": False,
                "child_creates_payment": False,
                "child_creates_ticket": False,
                "child_creates_booking": False,
            },
        )
    return tuple(dependencies)


def _semantic_influence_map() -> tuple[str, ...]:
    return (
        "Orchestrator accepted semantics -> allowed runtime to create the BSEP candidate.",
        "BSEP validation PASS -> allowed Architect call.",
        "Architect accepted semantics -> allowed runtime to expose bounded side projections to horizontal actors.",
        "Client actors -> informed client preference and privacy interpretation.",
        "Airline offer parent actor -> enabled fare-rules and seat/baggage vertical children.",
        "Airline vertical children -> returned canonical advisory child results upward.",
        "Bank payment parent actor -> enabled idempotency/risk vertical child.",
        "Bank vertical child -> returned canonical advisory child result upward.",
        "Ticketing reviewer -> explained mock ticket evidence conditions.",
        "Payment-status reviewer -> explained authorization versus settlement.",
        "Cross-root reviewer -> checked one transaction_id, evidence-only routing, and no authority transfer.",
        "Runtime validation/canonicalization -> used accepted semantics for the mock happy-path explanation and rejected all provider authority/action claims.",
    )


def _mock_happy_path() -> str:
    return (
        "Клиентские акторы разобрали маршрут, бюджет, багаж, место и ограничения. "
        "Авиакомпания семантически сравнила mock-предложения и условия. Банковские "
        "акторы разобрали mock-авторизацию, сумму, merchant, идемпотентность и "
        "разницу между authorization и settlement. Cross-root reviewer проверил "
        "одну транзакцию и отсутствие передачи власти. Итоговый успешный путь "
        "остаётся mock-only: mock payment authorization, mock ticket evidence, "
        "mock PNR evidence. No real payment, real ticket, or real booking occurred."
    )


def _root_authority_story() -> str:
    return (
        "Root boundaries remain side-specific. ClientRoot does not authorize bank "
        "payment, AirlineRoot does not authorize payment, BankRoot does not create "
        "ticket evidence, and cross-root reviewer is advisory, not a fourth Root."
    )


def _privacy_secret_story(secret_scan: Mapping[str, Any]) -> str:
    return (
        "Prompt and raw response display is guarded by source secret scan. "
        f"secret scan passed={secret_scan.get('passed')}, matched_markers={secret_scan.get('matched_markers')}."
    )


def _artifact_inventory(artifact_dir: Path) -> dict[str, Any]:
    return {
        "prompt_files": len(list(artifact_dir.glob("*_prompt.txt"))),
        "raw_response_files": len(list(artifact_dir.glob("*_raw_response.txt"))),
        "extracted_json_candidate_files": len(
            list(artifact_dir.glob("*_extracted_json_candidate.json")),
        ),
        "validation_files": len(
            [path for path in artifact_dir.glob("*_validation.json") if not path.name.startswith("tri_party_airline_bsep_")],
        ),
        "canonical_summary_files": len(list(artifact_dir.glob("*_canonical_summary.json"))),
        "source_artifact_dir": str(artifact_dir),
    }


def _counter_table(
    *,
    summary: Mapping[str, Any],
    secret_scan: Mapping[str, Any],
    actor_cards: tuple[Mapping[str, Any], ...],
    allow_prompt: bool,
    allow_raw: bool,
) -> dict[str, int]:
    source = summary.get("counter_table", {})
    return {
        "source_semantic_actor_call_count": int(source.get("semantic_actor_call_count", 0)),
        "source_real_provider_call_count": int(source.get("real_provider_call_count", 0)),
        "source_fake_provider_call_count": int(source.get("fake_provider_call_count", 0)),
        "source_network_used_count": int(source.get("network_used_count", 0)),
        "source_gemini_called_count": int(source.get("gemini_called_count", 0)),
        "source_actor_validation_pass_count": int(source.get("semantic_actor_validation_pass_count", 0)),
        "source_actor_validation_fail_count": int(source.get("semantic_actor_validation_fail_count", 0)),
        "source_bsep_created_count": int(source.get("bsep_created_count", 0)),
        "source_bsep_validated_count": int(source.get("bsep_validated_count", 0)),
        "source_bsep_projection_count": int(source.get("bsep_side_projection_count", 0)),
        "source_vertical_fractal_cell_count": int(source.get("vertical_fractal_semantic_cell_count", 0)),
        "source_secret_scan_files_scanned": int(secret_scan.get("files_scanned", 0)),
        "source_secret_marker_match_count": len(secret_scan.get("matched_markers", ())),
        "source_real_world_effects_count": int(source.get("real_world_effects_count", 0)),
        "human_story_created_count": 1,
        "actor_cards_created_count": len(actor_cards),
        "actor_input_summaries_rendered_count": len(actor_cards),
        "actor_output_summaries_rendered_count": len(actor_cards),
        "runtime_used_sections_rendered_count": len(actor_cards),
        "runtime_rejected_sections_rendered_count": len(actor_cards),
        "vertical_dependency_cards_created_count": sum(
            int(bool(card.get("vertical_fractal_cell"))) for card in actor_cards
        ),
        "horizontal_side_groups_created_count": 3,
        "bsep_story_created_count": 1,
        "bsep_projection_story_count": 4,
        "mock_happy_path_story_created_count": 1,
        "full_prompts_printed_count": len(actor_cards) if allow_prompt else 0,
        "raw_responses_printed_count": len(actor_cards) if allow_raw else 0,
        "renderer_provider_called_count": 0,
        "renderer_network_called_count": 0,
        "renderer_gemini_called_count": 0,
        "renderer_payment_created_count": 0,
        "renderer_ticket_created_count": 0,
        "renderer_booking_created_count": 0,
        "renderer_real_world_effects_count": 0,
    }


def _skipped_counter_table() -> dict[str, int]:
    return {
        "renderer_provider_called_count": 0,
        "renderer_network_called_count": 0,
        "renderer_gemini_called_count": 0,
        "renderer_payment_created_count": 0,
        "renderer_ticket_created_count": 0,
        "renderer_booking_created_count": 0,
        "renderer_real_world_effects_count": 0,
    }


def _non_claims() -> tuple[str, ...]:
    return (
        "not production",
        "not public auditor final package",
        "no live rerun",
        "no provider call by renderer",
        "no network call by renderer",
        "no Gemini call by renderer",
        "no config/API key access",
        "no real airline API",
        "no real bank API",
        "no real GDS API",
        "no real payment",
        "no real ticket",
        "no real booking",
        "no Ticket/Purchase Corridor implementation",
        "no Transaction Artifact Ledger implementation",
        "no Crypto Artifact Seal implementation",
        "no Sealed Trace Replay Verifier implementation",
    )


def _semantic_effect_for_actor(actor_id: str) -> str:
    effects = {
        "tri_party_airline_orchestrator_llm": "allowed runtime to create the BSEP candidate after validation",
        "tri_party_airline_semantic_architect_llm": "allowed bounded side projections to feed horizontal actors",
        "client_purchase_intent_reviewer_llm": "informed client preference interpretation",
        "client_profile_privacy_reviewer_llm": "informed sealed-ref privacy explanation",
        "airline_offer_policy_reviewer_llm": "enabled airline vertical child cells",
        "airline_fare_rules_vertical_cell_llm": "returned fare advisory result upward",
        "airline_seat_baggage_vertical_cell_llm": "returned seat and baggage advisory result upward",
        "airline_ticketing_policy_reviewer_llm": "explained mock ticket evidence conditions",
        "bank_payment_policy_reviewer_llm": "enabled bank risk vertical child",
        "bank_idempotency_risk_vertical_cell_llm": "returned idempotency advisory result upward",
        "bank_payment_status_explainer_llm": "explained authorization versus settlement",
        "tri_party_evidence_consistency_reviewer_llm": "checked one transaction and evidence-only routing",
    }
    return effects[actor_id]


def _render_actor_card(card: Mapping[str, Any]) -> tuple[str, ...]:
    lines = [
        f"- actor {card['actor_index']}: {card['actor_id']} ({card['human_role_name']})",
        f"  side: {card['side']}",
        f"  validation_status: {card['validation_status']}",
        f"  input_context_summary: {card['input_context_summary']}",
        f"  prompt_artifact_path: {card['prompt_artifact_path']}",
        f"  prompt_character_count: {card['prompt_character_count']}",
        f"  prompt_displayed_in_full: {card['prompt_displayed_in_full']}",
        f"  raw_response_artifact_path: {card['raw_response_artifact_path']}",
        f"  raw_response_character_count: {card['raw_response_character_count']}",
        f"  raw_response_displayed: {card['raw_response_displayed']}",
        f"  output_semantic_summary: {card['output_semantic_summary']}",
        f"  what_runtime_used: {', '.join(card['what_runtime_used'])}",
        f"  what_runtime_rejected: {', '.join(card['what_runtime_rejected'])}",
        f"  semantic_effect_on_next_stage: {card['semantic_effect_on_next_stage']}",
    ]
    if card.get("vertical_fractal_cell"):
        lines.extend(
            (
                "  vertical_fractal_cell: true",
                f"  parent_actor_id: {card['parent_actor_id']}",
                f"  parent_validation_status: {card['parent_validation_status']}",
                f"  child_started_after_parent_validation: {card['child_started_after_parent_validation']}",
                f"  child_received_parent_canonical_summary: {card['child_received_parent_canonical_summary']}",
                f"  child_received_parent_raw_response: {card['child_received_parent_raw_response']}",
                f"  child_received_sibling_raw_output: {card['child_received_sibling_raw_output']}",
                f"  child_received_unbounded_context: {card['child_received_unbounded_context']}",
                f"  child_result_returns_to_parent_or_root_review: {card['child_result_returns_to_parent_or_root_review']}",
            ),
        )
    if card.get("prompt_displayed_in_full"):
        lines.append(f"  full_prompt: {card.get('prompt_text_for_display', '')}")
    if card.get("raw_response_displayed"):
        lines.append(f"  raw_response: {card.get('raw_response_text_for_display', '')}")
    return tuple(lines)


def _card_by_id(cards: tuple[Mapping[str, Any], ...], actor_id: str) -> Mapping[str, Any]:
    for card in cards:
        if card["actor_id"] == actor_id:
            return card
    return {"human_role_name": actor_id, "output_semantic_summary": ""}


if __name__ == "__main__":
    raise SystemExit(main())
