from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping


RUN_ID = "human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01"
REPORT_ID = "human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01"
STORY_TYPE = "artifact_backed_all_real_airline_semantic_to_contract_causal_corridor_story"

PASS = "PASS"
FAIL_CLOSED = "FAIL_CLOSED"
SKIPPED_CLOSED = "SKIPPED_CLOSED"

ENV_ARTIFACT_DIR = "HEDGEHOG_AIRLINE_ALL_REAL_CAUSAL_STORY_ARTIFACT_DIR"
ENV_AUDIT_LOG = "HEDGEHOG_AIRLINE_ALL_REAL_CAUSAL_STORY_AUDIT_LOG"
ENV_ALLOW_RAW = "HEDGEHOG_AIRLINE_ALL_REAL_CAUSAL_STORY_ALLOW_RAW_RESPONSES"
ENV_ALLOW_PROMPT = "HEDGEHOG_AIRLINE_ALL_REAL_CAUSAL_STORY_ALLOW_FULL_PROMPTS"

DEFAULT_AUDIT_LOG = (
    "docs/audit_reports/"
    "auditor_tri_party_airline_all_real_semantic_to_contract_causal_corridor_real_run_v01.log"
)
EXPECTED_AUDIT_ID = (
    "auditor_tri_party_airline_all_real_semantic_to_contract_causal_corridor_real_run_v01"
)
EXPECTED_SOURCE_RUN_NAME = (
    "tri_party_airline_live_semantic_causal_all_real_preference_a_20260712_084540"
)
EXPECTED_SOURCE_SUFFIX = (
    ".tmp/tri_party_airline_live_semantic_causal_all_real/"
    "tri_party_airline_live_semantic_causal_all_real_preference_a_20260712_084540"
)
EXPECTED_HEAD = "acc1350"
EXPECTED_PROVIDER_MODE = "real_provider"
EXPECTED_MODEL = "gemini-2.5-flash"
EXPECTED_OFFER_ID = "offer:mock_airline_al:PAR-LIM:001"
EXPECTED_TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"

REJECTED_SOURCE_MARKERS = (
    "proposer_smoke",
    "causal_reviewer_smoke",
    "real_cross_root_consistency_reviewer_smoke",
    "20260712_083900",
)

REQUIRED_SOURCE_FILES = (
    "all_real_operator_gate_check.json",
    "summary.json",
    "summary.log",
    "secret_scan.json",
    "semantic_to_contract_causal_run.json",
    "semantic_to_contract_bridge.json",
    "integrated_deterministic_airline_summary.json",
    "tri_party_airline_bsep_packet.json",
    "tri_party_airline_bsep_validation.json",
    "tri_party_airline_bsep_side_projections.json",
)

EXPECTED_EVIDENCE_SHA256 = {
    "integrated_deterministic_airline_summary.json": (
        "3bd7ea12f57b754608899fcf80975d67233024767fdc05d36701786fcbd6764c"
    ),
    "all_real_operator_gate_check.json": (
        "11b5de0bfb5f1ec016ca1c91d3996fbddeb83028a11b0ccc89496652b2a87d2f"
    ),
    "secret_scan.json": (
        "c2ddc66f3baa0c4f0cc56b4b23d5b771d56cd5714b49918674064c6b718bfb66"
    ),
    "semantic_to_contract_bridge.json": (
        "ce8ddeb20deb3721b4a4e19f7dd6a7bd13d3ebd1c66c18156d9614108aa865f2"
    ),
    "semantic_to_contract_causal_run.json": (
        "7db2bf5ff162d36855746970343f0aded3193a45cc64d872a5b4cd315ae36406"
    ),
    "summary.json": (
        "64fd49e2cd7cc8ba0cd249c0e2d839e846a98edf53cef3489b078e1ef23afe5d"
    ),
    "summary.log": (
        "2873d9d54f87062b8c811c9a09748cf8167eafccec510dd85bf64a1367daed87"
    ),
}

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

CAUSAL_ACTOR_IDS = (
    "client_purchase_intent_reviewer_llm",
    "airline_offer_policy_reviewer_llm",
    "airline_fare_rules_vertical_cell_llm",
    "airline_seat_baggage_vertical_cell_llm",
    "tri_party_evidence_consistency_reviewer_llm",
)

HUMAN_ROLE_NAMES = {
    "tri_party_airline_orchestrator_llm": "Оркестратор всей авиасделки",
    "tri_party_airline_semantic_architect_llm": "Семантический архитектор",
    "client_purchase_intent_reviewer_llm": "Проверяющий намерение клиента",
    "client_profile_privacy_reviewer_llm": "Проверяющий приватность клиента",
    "airline_offer_policy_reviewer_llm": "Проверяющий предложения AirlineRoot",
    "airline_fare_rules_vertical_cell_llm": "Дочерняя ячейка правил тарифа",
    "airline_seat_baggage_vertical_cell_llm": "Дочерняя ячейка места и багажа",
    "airline_ticketing_policy_reviewer_llm": "Проверяющий mock-выпуск билета",
    "bank_payment_policy_reviewer_llm": "Проверяющий mock-платеж банка",
    "bank_idempotency_risk_vertical_cell_llm": "Дочерняя ячейка банковского риска",
    "bank_payment_status_explainer_llm": "Объясняющий статус mock-платежа",
    "tri_party_evidence_consistency_reviewer_llm": "Межсторонний проверяющий evidence",
}

PARENT_BY_CHILD = {
    "airline_fare_rules_vertical_cell_llm": "airline_offer_policy_reviewer_llm",
    "airline_seat_baggage_vertical_cell_llm": "airline_offer_policy_reviewer_llm",
    "bank_idempotency_risk_vertical_cell_llm": "bank_payment_policy_reviewer_llm",
}

ACTOR_SAFE_FALSE_FIELDS = (
    "authority_created",
    "action_permission_created",
    "packet_created",
    "receipt_created",
    "payment_created",
    "ticket_created",
    "booking_created",
    "final_output_created",
    "real_payment_executed",
    "real_ticket_issued",
    "real_booking_created",
)

BSEP_PACKET_SAFE_FALSE_FIELDS = (
    "raw_passport_included",
    "raw_card_included",
    "raw_iban_included",
    "raw_payment_token_included",
    "raw_private_profile_included",
    "raw_provider_text_included",
    "raw_response_dump_included",
    "authority_created",
    "action_permission_created",
    "payment_created",
    "ticket_created",
    "booking_created",
    "final_output_created",
)

BSEP_PROJECTION_EXPECTED_SIDES = {
    "client_bsep_projection": ("client",),
    "airline_bsep_projection": ("airline",),
    "bank_bsep_projection": ("bank",),
    "cross_root_bsep_projection": ("cross_root", "cross_root_advisory"),
}

BSEP_PROJECTION_SAFE_FALSE_FIELDS = (
    "raw_secrets_included",
    "raw_provider_text_included",
)

ACCEPTED_ACTOR_SIDES = (
    "transaction",
    "client",
    "airline",
    "bank",
    "cross_root",
    "cross_root_advisory",
)

KNOWN_CAUSAL_REVIEW_STATUSES = (
    PASS,
    FAIL_CLOSED,
    "REQUIRES_ROOT_REVIEW",
)

ZERO_COUNTERS = (
    "direct_offer_override_count",
    "default_offer_count",
    "silent_fallback_count",
    "provider_created_authority_count",
    "provider_created_contract_count",
    "runtime_receipt_created_count",
    "real_airline_api_called_count",
    "real_bank_api_called_count",
    "real_gds_api_called_count",
    "real_payment_executed_count",
    "real_ticket_issued_count",
    "real_booking_created_count",
    "real_world_effects_count",
)

SOURCE_COUNTER_EXPECTATIONS = {
    "semantic_actor_call_count": 12,
    "causal_semantic_actor_call_count": 5,
    "generic_semantic_actor_call_count": 7,
    "duplicate_semantic_actor_call_count": 0,
    "real_provider_call_count": 12,
    "fake_provider_call_count": 0,
    "network_used_count": 12,
    "gemini_called_count": 12,
    "deterministic_airline_collection_count": 1,
    "ticket_purchase_corridor_execution_count": 1,
    "direct_offer_override_count": 0,
    "default_offer_count": 0,
    "silent_fallback_count": 0,
    "provider_created_authority_count": 0,
    "provider_created_contract_count": 0,
    "runtime_receipt_created_count": 0,
    "real_airline_api_called_count": 0,
    "real_bank_api_called_count": 0,
    "real_gds_api_called_count": 0,
    "real_payment_executed_count": 0,
    "real_ticket_issued_count": 0,
    "real_booking_created_count": 0,
    "real_world_effects_count": 0,
}

NEXT_PRESENTATION_GATE = (
    "artifact-backed human story for the all-real semantic-to-contract causal corridor run"
)
NEXT_ENGINEERING_GATE = (
    "Airline Transaction Artifact Ledger v0.1 preflight / implementation"
)


def collect_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    active_env = dict(os.environ if env is None else env)
    artifact_dir_value = active_env.get(ENV_ARTIFACT_DIR, "").strip()
    audit_log_value = active_env.get(ENV_AUDIT_LOG, DEFAULT_AUDIT_LOG).strip()
    if not artifact_dir_value:
        return _skipped_report(audit_log_value)

    artifact_dir = Path(artifact_dir_value)
    audit_log = Path(audit_log_value)
    allow_raw_requested = active_env.get(ENV_ALLOW_RAW) == "1"
    allow_prompt_requested = active_env.get(ENV_ALLOW_PROMPT) == "1"
    errors: list[str] = []

    loaded = _load_artifact_package(artifact_dir, audit_log, errors)
    secret_scan = _mapping(loaded.get("secret_scan"))
    source_path_accepted = not _path_errors(artifact_dir)
    allow_transparency = secret_scan.get("passed") is True and source_path_accepted
    allow_raw = allow_raw_requested and allow_transparency
    allow_prompt = allow_prompt_requested and allow_transparency

    actor_cards = _build_actor_cards(
        artifact_dir=artifact_dir,
        summary=_mapping(loaded.get("summary")),
        allow_raw=allow_raw,
        allow_prompt=allow_prompt,
        errors=errors,
    )
    actor_cards = _attach_causal_review_facts(actor_cards, _mapping(loaded.get("causal")), errors)
    errors.extend(_validate_loaded_artifacts(loaded, actor_cards, artifact_dir))

    if errors:
        allow_raw = False
        allow_prompt = False
        actor_cards = tuple(_hide_prompt_and_raw(card) for card in actor_cards)

    final_status = PASS if not errors else FAIL_CLOSED
    story_data = _story_data(loaded, actor_cards)
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": final_status,
        "skip_reason": "",
        "source_artifact_dir": str(artifact_dir),
        "source_audit_log": str(audit_log),
        "source_run_name": EXPECTED_SOURCE_RUN_NAME,
        "source_integrity": _source_integrity(loaded),
        "actor_cards": actor_cards,
        "causal_actor_cards": tuple(
            card for card in actor_cards if card["actor_id"] in CAUSAL_ACTOR_IDS
        ),
        "six_offer_references": story_data["six_offer_references"],
        "bounded_offer_set": story_data["bounded_offer_set"],
        "proposer_story": story_data["proposer_story"],
        "bsep_story": story_data["bsep_story"],
        "vertical_dependencies": story_data["vertical_dependencies"],
        "causal_reviews": story_data["causal_reviews"],
        "synthesis_story": story_data["synthesis_story"],
        "runtime_used": story_data["runtime_used"],
        "runtime_rejected": story_data["runtime_rejected"],
        "counter_table": _counter_table(
            loaded=loaded,
            actor_cards=actor_cards,
            allow_raw=allow_raw,
            allow_prompt=allow_prompt,
        ),
        "validation_errors": tuple(_dedupe(errors)),
        "non_claims": _non_claims(),
        "next_presentation_gate": NEXT_PRESENTATION_GATE,
        "next_engineering_gate_after_story": NEXT_ENGINEERING_GATE,
    }


def render_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
    report: Mapping[str, Any],
) -> str:
    lines = [
        "[HEDGEHOG OS — AIRLINE ALL-REAL CAUSAL CORRIDOR HUMAN STORY]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"story_type: {report['story_type']}",
        f"final_status: {report['final_status']}",
    ]
    if report["final_status"] == SKIPPED_CLOSED:
        lines.extend(
            (
                "",
                "[FINAL STATUS]",
                "SKIPPED_CLOSED",
                f"skip_reason: {report['skip_reason']}",
            ),
        )
        return "\n".join(lines)
    if report["final_status"] != PASS:
        lines.extend(
            (
                "",
                "[FINAL STATUS]",
                "FAIL_CLOSED",
                "validation_errors:",
            ),
        )
        lines.extend(f"- {error}" for error in report["validation_errors"])
        return "\n".join(lines)

    lines.extend(
        (
            "",
            "[ONE-SCREEN SUMMARY]",
            (
                "Одна Airline mock-транзакция прошла через двенадцать реальных "
                "Gemini-акторов, три side-specific Root, один выбранный offer и "
                "один deterministic Ticket/Purchase Corridor. Семантика выбрала "
                "Offer 001, но власть осталась у ClientRoot, AirlineRoot и BankRoot. "
                "Ни реального платежа, ни реального билета, ни реального бронирования "
                "не произошло."
            ),
            "",
            "[THE CLIENT REQUEST]",
            _client_request_story(report),
            "",
            "[BOUNDED OFFER SET]",
        ),
    )
    lines.extend(f"- {item}" for item in report["bounded_offer_set"])
    lines.extend(("", "[WHAT GEMINI RECOMMENDED]", _format_mapping(report["proposer_story"])))
    lines.extend(("", "[BSEP MEMBRANE]"))
    lines.extend(f"- {item}" for item in report["bsep_story"])
    lines.extend(("", "[ALL 12 ACTOR CARDS]"))
    for card in report["actor_cards"]:
        lines.extend(_render_actor_card(card))
    lines.extend(("", "[HORIZONTAL SEMANTIC WORK]"))
    lines.extend(_horizontal_story(report["actor_cards"]))
    lines.extend(("", "[VERTICAL FRACTAL WORK]"))
    lines.extend(_vertical_story(report["vertical_dependencies"]))
    lines.extend(("", "[THE FIVE CAUSAL ACTORS]"))
    lines.extend(_causal_actor_story(report["causal_reviews"]))
    lines.extend(("", "[MULTI-ACTOR SYNTHESIS]", _format_mapping(report["synthesis_story"])))
    lines.extend(
        (
            "",
            "[HOW SEMANTICS CHANGED THE CONTRACT]",
            "Preference A -> Gemini proposal -> five validated causal reviews -> synthesis -> "
            "canonical evidence -> ClientRoot decision -> AirlineRoot authoritative resolution -> "
            "Root-created hold -> deterministic Airline transaction -> actual corridor contract context.",
        ),
    )
    lines.extend(("", "[THE SIX OFFER REFERENCES]"))
    for key, value in report["six_offer_references"].items():
        lines.append(f"{key}: {value}")
    lines.extend(
        (
            "",
            "[THREE ROOTS, THREE AUTHORITY BOUNDARIES]",
            (
                "ClientRoot владеет намерением клиента и человеческим approval scope. "
                "AirlineRoot владеет offer, hold и mock-ticket issue. BankRoot владеет "
                "mock payment authorization. Cross-root reviewer является advisory, "
                "не четвёртым Root. Evidence может пересекать Roots, authority не переходит."
            ),
            "",
            "[THE DETERMINISTIC TICKET/PURCHASE CORRIDOR]",
            (
                "Пять Root-centered фаз читаются как простой путь: AirlineRoot удержал "
                "выбранный offer, ClientRoot оформил purchase intent после человеческого "
                "approval scope, BankRoot дал bounded mock authorization, AirlineRoot "
                "создал mock-ticket evidence, а ClientRoot наблюдал completion. Была одна "
                "deterministic collection и один corridor execution, с immutable per-run "
                "context и evidence-only receipts."
            ),
            "",
            "[WHAT RUNTIME USED]",
        ),
    )
    lines.extend(f"- {item}" for item in report["runtime_used"])
    lines.extend(("", "[WHAT RUNTIME REJECTED]"))
    lines.extend(f"- {item}" for item in report["runtime_rejected"])
    lines.extend(("", "[WHAT DID NOT HAPPEN]"))
    for key in ZERO_COUNTERS:
        lines.append(f"{key}: {report['counter_table'].get(key, 0)}")
    lines.extend(
        (
            "",
            "[PROVENANCE NOTE]",
            (
                "Это continuous twelve-call all-real run из каталога 084540. Actor outputs "
                "не replayed, fake provider не использовался. lane_id содержит legacy строку "
                "fake_provider, но provider_mode, counters и artifacts показывают real_provider."
            ),
            "",
            "[HONEST LIMITS]",
        ),
    )
    lines.extend(f"- {claim}" for claim in report["non_claims"])
    lines.extend(
        (
            "",
            "[FINAL STATUS]",
            "PASS",
            f"next_presentation_gate: {report['next_presentation_gate']}",
            f"next_engineering_gate_after_story: {report['next_engineering_gate_after_story']}",
        ),
    )
    return "\n".join(lines)


def run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
    *,
    env: Mapping[str, str] | None = None,
) -> str:
    return render_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
        collect_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01(
            env=env,
        ),
    )


def main() -> int:
    print(run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01())
    return 0


def _skipped_report(audit_log_value: str) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": SKIPPED_CLOSED,
        "skip_reason": "source_artifact_dir_not_selected",
        "source_artifact_dir": "",
        "source_audit_log": audit_log_value,
        "source_run_name": "",
        "source_integrity": {},
        "actor_cards": (),
        "causal_actor_cards": (),
        "six_offer_references": {},
        "bounded_offer_set": (),
        "proposer_story": {},
        "bsep_story": (),
        "vertical_dependencies": (),
        "causal_reviews": (),
        "synthesis_story": {},
        "runtime_used": (),
        "runtime_rejected": (),
        "counter_table": _skipped_counters(),
        "validation_errors": (),
        "non_claims": _non_claims(),
        "next_presentation_gate": NEXT_PRESENTATION_GATE,
        "next_engineering_gate_after_story": NEXT_ENGINEERING_GATE,
    }


def _load_artifact_package(
    artifact_dir: Path,
    audit_log: Path,
    errors: list[str],
) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    errors.extend(_path_errors(artifact_dir))
    if not artifact_dir.exists():
        errors.append("source_artifact_dir_missing")
        return loaded
    for name in REQUIRED_SOURCE_FILES:
        if not (artifact_dir / name).exists():
            errors.append(f"missing_required_source_file:{name}")
    for actor_id in ACTOR_IDS:
        for suffix in (
            "prompt.txt",
            "raw_response.txt",
            "extracted_json_candidate.json",
            "validation.json",
            "canonical_summary.json",
        ):
            if not (artifact_dir / f"{actor_id}_{suffix}").exists():
                errors.append(f"missing_actor_artifact:{actor_id}:{suffix}")
    if not audit_log.exists():
        errors.append("source_audit_log_missing")
    if errors:
        return loaded

    json_files = {
        "operator": "all_real_operator_gate_check.json",
        "summary": "summary.json",
        "secret_scan": "secret_scan.json",
        "causal": "semantic_to_contract_causal_run.json",
        "bridge": "semantic_to_contract_bridge.json",
        "integrated": "integrated_deterministic_airline_summary.json",
        "bsep_packet": "tri_party_airline_bsep_packet.json",
        "bsep_validation": "tri_party_airline_bsep_validation.json",
        "bsep_projections": "tri_party_airline_bsep_side_projections.json",
    }
    for key, name in json_files.items():
        loaded[key] = _read_json_object(artifact_dir / name, errors)
    loaded["summary_log_text"] = _read_text(artifact_dir / "summary.log", errors)
    loaded["console_log_text"] = _read_text(artifact_dir / "console.log", errors)
    loaded["audit_log_text"] = _read_text(audit_log, errors)
    loaded["hashes"] = _compute_evidence_hashes(artifact_dir, errors)
    return loaded


def _path_errors(artifact_dir: Path) -> list[str]:
    errors: list[str] = []
    text = str(artifact_dir)
    if artifact_dir.name != EXPECTED_SOURCE_RUN_NAME:
        errors.append("source_run_name_mismatch")
    for marker in REJECTED_SOURCE_MARKERS:
        if marker in text:
            errors.append(f"rejected_source_marker:{marker}")
    return errors


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"json_unreadable:{path.name}:{type(exc).__name__}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"json_root_not_object:{path.name}")
        return {}
    return value


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"text_unreadable:{path.name}:{type(exc).__name__}")
        return ""


def _compute_evidence_hashes(artifact_dir: Path, errors: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name, expected in EXPECTED_EVIDENCE_SHA256.items():
        path = artifact_dir / name
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"evidence_hash_unreadable:{name}:{type(exc).__name__}")
            continue
        hashes[name] = digest
        if digest != expected:
            errors.append(f"evidence_fingerprint_mismatch:{name}")
    return hashes


def _build_actor_cards(
    *,
    artifact_dir: Path,
    summary: Mapping[str, Any],
    allow_raw: bool,
    allow_prompt: bool,
    errors: list[str],
) -> tuple[dict[str, Any], ...]:
    source_reports = _source_actor_report_map(summary.get("semantic_actor_reports"), errors)
    cards: list[dict[str, Any]] = []
    for index, actor_id in enumerate(ACTOR_IDS, start=1):
        report = _mapping(source_reports.get(actor_id))
        prompt_path = artifact_dir / f"{actor_id}_prompt.txt"
        raw_path = artifact_dir / f"{actor_id}_raw_response.txt"
        extracted_path = artifact_dir / f"{actor_id}_extracted_json_candidate.json"
        validation_path = artifact_dir / f"{actor_id}_validation.json"
        canonical_path = artifact_dir / f"{actor_id}_canonical_summary.json"
        prompt_text = _read_text(prompt_path, errors) if prompt_path.exists() else ""
        raw_text = _read_text(raw_path, errors) if raw_path.exists() else ""
        extracted = _read_json_object(extracted_path, errors) if extracted_path.exists() else {}
        validation = _read_json_object(validation_path, errors) if validation_path.exists() else {}
        canonical = _read_json_object(canonical_path, errors) if canonical_path.exists() else {}
        report_side = _required_enum_string(
            report.get("side"),
            ACCEPTED_ACTOR_SIDES,
            f"actor_side_invalid:{actor_id}",
            errors,
        )
        canonical_side = _optional_enum_string(
            canonical.get("side"),
            ACCEPTED_ACTOR_SIDES,
            f"actor_side_invalid:{actor_id}",
            errors,
        )
        side = canonical_side or report_side or _default_side(actor_id)
        input_context_summary = _required_non_empty_string(
            report.get("input_context_summary"),
            f"actor_input_context_summary_invalid:{actor_id}",
            errors,
        )
        extracted_semantic_summary = _optional_non_empty_string(
            extracted.get("semantic_summary"),
            f"actor_extracted_semantic_summary_invalid:{actor_id}",
            errors,
        )
        canonical_semantic_summary = _required_non_empty_string(
            canonical.get("semantic_summary"),
            f"actor_canonical_semantic_summary_invalid:{actor_id}",
            errors,
        )
        runtime_used = _string_array(
            canonical.get("what_runtime_used"),
            f"canonical_what_runtime_used_invalid:{actor_id}",
            errors,
            allow_empty=False,
        )
        runtime_rejected = _string_array(
            canonical.get("what_runtime_rejected"),
            f"canonical_what_runtime_rejected_invalid:{actor_id}",
            errors,
            allow_empty=False,
        )
        card = {
            "actor_index": index,
            "actor_id": actor_id,
            "human_role_name": HUMAN_ROLE_NAMES[actor_id],
            "side": side,
            "parent_actor_id": PARENT_BY_CHILD.get(actor_id, ""),
            "bounded_input_summary": input_context_summary,
            "provider_returned": extracted_semantic_summary or canonical_semantic_summary,
            "validation_status": validation.get("validation_status", ""),
            "accepted": validation.get("accepted", True),
            "validation_errors": _string_array(
                validation.get("errors", []),
                f"actor_validation_errors_invalid:{actor_id}",
                errors,
                allow_empty=True,
            ),
            "canonical_semantic_summary": canonical_semantic_summary,
            "what_runtime_used": runtime_used,
            "what_runtime_rejected": runtime_rejected,
            "authority_created": bool(report.get("authority_created", False)),
            "action_permission_created": bool(report.get("action_permission_created", False)),
            "packet_created": bool(report.get("packet_created", False)),
            "receipt_created": bool(report.get("receipt_created", False)),
            "payment_created": bool(report.get("payment_created", False)),
            "ticket_created": bool(report.get("ticket_created", False)),
            "booking_created": bool(report.get("booking_created", False)),
            "final_output_created": bool(report.get("final_output_created", False)),
            "real_payment_executed": bool(report.get("real_payment_executed", False)),
            "real_ticket_issued": bool(report.get("real_ticket_issued", False)),
            "real_booking_created": bool(report.get("real_booking_created", False)),
            "real_world_effects_count": _safe_int(report.get("real_world_effects_count", 0)),
            "prompt_artifact_path": str(prompt_path),
            "raw_response_artifact_path": str(raw_path),
            "prompt_displayed_in_full": allow_prompt,
            "raw_response_displayed": allow_raw,
            "prompt_character_count": len(prompt_text),
            "raw_response_character_count": len(raw_text),
        }
        if allow_prompt:
            card["prompt_text_for_display"] = prompt_text
        if allow_raw:
            card["raw_response_text_for_display"] = raw_text
        cards.append(card)
    return tuple(cards)


def _hide_prompt_and_raw(card: Mapping[str, Any]) -> dict[str, Any]:
    hidden = dict(card)
    hidden["prompt_displayed_in_full"] = False
    hidden["raw_response_displayed"] = False
    hidden.pop("prompt_text_for_display", None)
    hidden.pop("raw_response_text_for_display", None)
    return hidden


def _attach_causal_review_facts(
    actor_cards: tuple[Mapping[str, Any], ...],
    causal: Mapping[str, Any],
    errors: list[str],
) -> tuple[dict[str, Any], ...]:
    reviews = _causal_actor_review_map(causal.get("actor_reviews"), errors)
    enriched: list[dict[str, Any]] = []
    for card in actor_cards:
        row = dict(card)
        review = _mapping(reviews.get(card["actor_id"]))
        row["causal_review_semantic_factors"] = _string_array(
            review.get("semantic_factors", []),
            f"causal_review_semantic_factors_invalid:{card['actor_id']}",
            errors,
            allow_empty=card["actor_id"] not in CAUSAL_ACTOR_IDS,
        )
        row["causal_review_blocking_conflicts"] = _string_array(
            review.get("blocking_conflicts", []),
            f"causal_review_blocking_conflicts_invalid:{card['actor_id']}",
            errors,
            allow_empty=True,
        )
        if card["actor_id"] in CAUSAL_ACTOR_IDS:
            row["causal_review_status"] = _required_enum_string(
                review.get("review_status"),
                KNOWN_CAUSAL_REVIEW_STATUSES,
                f"causal_review_status_invalid:{card['actor_id']}",
                errors,
            )
        else:
            row["causal_review_status"] = ""
        enriched.append(row)
    return tuple(enriched)


def _validate_loaded_artifacts(
    loaded: Mapping[str, Any],
    actor_cards: tuple[Mapping[str, Any], ...],
    artifact_dir: Path,
) -> list[str]:
    errors: list[str] = []
    operator = _mapping(loaded.get("operator"))
    summary = _mapping(loaded.get("summary"))
    secret_scan = _mapping(loaded.get("secret_scan"))
    causal = _mapping(loaded.get("causal"))
    bridge = _mapping(loaded.get("bridge"))
    integrated = _mapping(loaded.get("integrated"))
    bsep_packet = _mapping(loaded.get("bsep_packet"))
    bsep_validation = _mapping(loaded.get("bsep_validation"))
    bsep_projections = _mapping(loaded.get("bsep_projections"))
    audit_log_text = str(loaded.get("audit_log_text", ""))
    counters = _mapping(summary.get("counter_table"))

    errors.extend(_validate_audit_log(audit_log_text))

    if operator.get("final_status") != PASS:
        errors.append("operator_final_status_not_pass")
    if operator.get("provider_mode") != EXPECTED_PROVIDER_MODE:
        errors.append("operator_provider_mode_not_real_provider")
    if operator.get("all_checks_pass") is not True:
        errors.append("operator_checks_not_pass")
    if operator.get("selected_offer") != EXPECTED_OFFER_ID:
        errors.append("operator_selected_offer_mismatch")
    if operator.get("missing_actor_artifacts") != []:
        errors.append("operator_missing_actor_artifacts")
    if operator.get("missing_integrated_artifacts") != []:
        errors.append("operator_missing_integrated_artifacts")

    if summary.get("final_status") != PASS:
        errors.append("summary_final_status_not_pass")
    if summary.get("provider_mode") != EXPECTED_PROVIDER_MODE:
        errors.append("summary_provider_mode_not_real_provider")
    if summary.get("model") != EXPECTED_MODEL:
        errors.append("summary_model_mismatch")
    if summary.get("validation_errors") != []:
        errors.append("summary_validation_errors_not_empty")
    actor_order = _string_array(
        summary.get("semantic_actor_call_order"),
        "semantic_actor_call_order_invalid",
        errors,
        allow_empty=False,
    )
    reports = _object_array(
        summary.get("semantic_actor_reports"),
        "semantic_actor_reports_invalid",
        errors,
    )
    report_actor_ids: list[str] = []
    for item in reports:
        actor_id = item.get("actor_id")
        if _is_non_empty_string(actor_id):
            report_actor_ids.append(actor_id)
        else:
            errors.append("semantic_actor_report_actor_id_invalid")
    if len(reports) != 12:
        errors.append("summary_actor_report_count_mismatch")
    if tuple(actor_order) != ACTOR_IDS:
        errors.append("summary_actor_order_mismatch")
    if tuple(report_actor_ids) != ACTOR_IDS:
        errors.append("summary_actor_report_order_mismatch")
    for key, expected in SOURCE_COUNTER_EXPECTATIONS.items():
        if counters.get(key) != expected:
            errors.append(f"source_counter_mismatch:{key}")
    if len(set(actor_order)) != len(actor_order):
        errors.append("duplicate_actor_call_detected")

    if secret_scan.get("passed") is not True:
        errors.append("secret_scan_failed")
    if secret_scan.get("files_scanned") != 67:
        errors.append("secret_scan_file_count_mismatch")
    if secret_scan.get("matched_markers") != []:
        errors.append("secret_scan_matched_markers_present")

    if causal.get("final_status") != "LOCAL_MODEL_PASS":
        errors.append("causal_final_status_not_local_model_pass")
    if causal.get("validation_errors") != []:
        errors.append("causal_validation_errors_not_empty")
    actor_reviews = _object_array(
        causal.get("actor_reviews"),
        "causal_actor_reviews_invalid",
        errors,
    )
    actor_review_ids: list[str] = []
    for item in actor_reviews:
        actor_id = item.get("actor_id")
        if _is_non_empty_string(actor_id):
            actor_review_ids.append(actor_id)
        else:
            errors.append("causal_actor_review_actor_id_invalid")
        _string_array(
            item.get("semantic_factors"),
            f"causal_actor_review_semantic_factors_invalid:{actor_id}",
            errors,
            allow_empty=False,
        )
        _string_array(
            item.get("blocking_conflicts", []),
            f"causal_actor_review_blocking_conflicts_invalid:{actor_id}",
            errors,
            allow_empty=True,
        )
    if len(actor_reviews) != 5:
        errors.append("causal_actor_review_count_mismatch")
    if tuple(actor_review_ids) != CAUSAL_ACTOR_IDS:
        errors.append("causal_actor_review_order_mismatch")
    if causal.get("provider_created_authority_count") != 0:
        errors.append("provider_created_authority_nonzero")
    if causal.get("provider_created_contract_count") != 0:
        errors.append("provider_created_contract_nonzero")
    if causal.get("real_world_effects_count") != 0:
        errors.append("causal_real_world_effects_nonzero")
    proposal = _mapping(causal.get("proposal"))
    evidence = _mapping(causal.get("canonical_evidence"))
    synthesis = _mapping(causal.get("synthesis"))
    if proposal.get("recommended_offer_id") != EXPECTED_OFFER_ID:
        errors.append("proposal_recommendation_mismatch")
    if evidence.get("source_proposal_id") != proposal.get("proposal_id"):
        errors.append("canonical_evidence_not_bound_to_actual_proposal")
    if evidence.get("source_actor_id") != proposal.get("actor_id"):
        errors.append("canonical_evidence_actor_mismatch")
    if evidence.get("recommended_offer_id") != proposal.get("recommended_offer_id"):
        errors.append("canonical_evidence_recommendation_mismatch")
    if synthesis.get("synthesis_status") != PASS:
        errors.append("synthesis_not_pass")
    if synthesis.get("unresolved_conflict_present") is not False:
        errors.append("synthesis_unresolved_conflict_present")

    if bridge.get("bridge_status") != PASS:
        errors.append("bridge_status_not_pass")
    if bridge.get("all_offer_ids_match") is not True:
        errors.append("bridge_offer_ids_do_not_match")
    if bridge.get("bsep_refs_match") is not True:
        errors.append("bridge_bsep_refs_do_not_match")
    if bridge.get("causal_report_validation_accepted") is not True:
        errors.append("bridge_causal_report_not_accepted")
    if bridge.get("deterministic_report_final_status") != PASS:
        errors.append("bridge_deterministic_report_not_pass")
    if bridge.get("deterministic_corridor_final_status") != PASS:
        errors.append("bridge_deterministic_corridor_not_pass")
    if bridge.get("deterministic_collection_count") != 1:
        errors.append("deterministic_collection_count_not_one")
    if bridge.get("corridor_execution_count") != 1:
        errors.append("corridor_execution_count_not_one")
    for flag in ("direct_offer_override_used", "default_offer_used", "silent_fallback_used"):
        if bridge.get(flag) is not False:
            errors.append(f"bridge_forbidden_flag_true:{flag}")
    six_refs = _six_offer_references(bridge)
    for key, value in six_refs.items():
        if value != EXPECTED_OFFER_ID:
            errors.append(f"six_offer_reference_mismatch:{key}")

    if integrated.get("collection_status") != PASS:
        errors.append("integrated_collection_not_pass")
    if integrated.get("corridor_final_status") != PASS:
        errors.append("integrated_corridor_not_pass")
    if integrated.get("corridor_execution_count") != 1:
        errors.append("integrated_corridor_execution_count_not_one")
    if integrated.get("selected_offer_id") != EXPECTED_OFFER_ID:
        errors.append("integrated_selected_offer_mismatch")
    if integrated.get("real_world_effects_count") != 0:
        errors.append("integrated_real_world_effects_nonzero")

    if bsep_validation.get("validation_status") != PASS or bsep_validation.get("errors") != []:
        errors.append("bsep_validation_not_pass")
    _validate_bsep_artifacts(
        summary=summary,
        bsep_packet=bsep_packet,
        bsep_projections=bsep_projections,
        errors=errors,
    )
    airline_ref = _mapping(bsep_projections.get("airline_bsep_projection")).get("projection_ref")
    if bridge.get("actual_airline_bsep_projection_ref") != bridge.get(
        "causal_selection_bsep_projection_ref",
    ):
        errors.append("bridge_bsep_refs_do_not_match")
    if bridge.get("actual_airline_bsep_projection_ref") != airline_ref:
        errors.append("actual_live_airline_bsep_ref_mismatch")
    if bridge.get("causal_selection_bsep_projection_ref") != airline_ref:
        errors.append("causal_bsep_ref_mismatch")
    if bridge.get("actual_bsep_packet_id") != bsep_packet.get("bsep_packet_id"):
        errors.append("actual_bsep_packet_id_mismatch")

    for card in actor_cards:
        if card["validation_status"] != PASS:
            errors.append(f"actor_validation_not_pass:{card['actor_id']}")
        if "accepted" in card and card["accepted"] is not True:
            errors.append(f"actor_not_accepted:{card['actor_id']}")
        if card["validation_errors"] != ():
            errors.append(f"actor_validation_errors:{card['actor_id']}")
        if not card["bounded_input_summary"]:
            errors.append(f"actor_bounded_input_empty:{card['actor_id']}")
        if not card["canonical_semantic_summary"]:
            errors.append(f"actor_canonical_summary_empty:{card['actor_id']}")
        if not card["what_runtime_used"]:
            errors.append(f"actor_runtime_used_empty:{card['actor_id']}")
        if not card["what_runtime_rejected"]:
            errors.append(f"actor_runtime_rejected_empty:{card['actor_id']}")
        for field in ACTOR_SAFE_FALSE_FIELDS:
            if card.get(field) not in (False, 0):
                errors.append(f"actor_forbidden_field_true:{card['actor_id']}:{field}")
        if card.get("real_world_effects_count") != 0:
            errors.append(f"actor_real_world_effects_nonzero:{card['actor_id']}")

    vertical_deps = _sequence(summary.get("vertical_fractal_dependencies"))
    for dep in vertical_deps:
        if not isinstance(dep, Mapping):
            errors.append("vertical_dependency_not_object")
            continue
        if dep.get("parent_validation_status") != PASS:
            errors.append(f"vertical_parent_not_pass:{dep.get('child_actor_id')}")
        for field in (
            "child_started_after_parent_validation",
            "child_received_parent_canonical_summary",
            "child_result_returns_to_parent_or_root_review",
        ):
            if dep.get(field) is not True:
                errors.append(f"vertical_required_true_mismatch:{dep.get('child_actor_id')}:{field}")
        for field in ("child_received_parent_raw_response", "child_received_sibling_raw_output"):
            if dep.get(field) is not False:
                errors.append(f"vertical_required_false_mismatch:{dep.get('child_actor_id')}:{field}")

    for key in ZERO_COUNTERS:
        if counters.get(key, 0) != 0:
            errors.append(f"zero_counter_nonzero:{key}")
    if artifact_dir.name != EXPECTED_SOURCE_RUN_NAME:
        errors.append("artifact_dir_not_expected_all_real_run")
    return errors


def _validate_audit_log(text: str) -> list[str]:
    required = (
        f"audit_id: {EXPECTED_AUDIT_ID}",
        "audit_status: PASS",
        f"observed_head: {EXPECTED_HEAD}",
        f"source_run_name: {EXPECTED_SOURCE_RUN_NAME}",
        "provider_mode: real_provider",
        f"selected_offer_id: {EXPECTED_OFFER_ID}",
        "real_world_effects_count: 0",
        "transaction_artifact_ledger_implemented: false",
        "crypto_artifact_seal_implemented: false",
        "sealed_trace_replay_verifier_implemented: false",
    )
    return [f"audit_log_missing_required_text:{item}" for item in required if item not in text]


def _validate_bsep_artifacts(
    *,
    summary: Mapping[str, Any],
    bsep_packet: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
    errors: list[str],
) -> None:
    if bsep_packet.get("validation_status") != PASS:
        errors.append("bsep_packet_not_pass")
    if bsep_packet.get("transaction_id") != EXPECTED_TRANSACTION_ID:
        errors.append("bsep_packet_transaction_id_mismatch")
    if bsep_packet.get("source_orchestrator_actor_id") != ACTOR_IDS[0]:
        errors.append("bsep_packet_source_orchestrator_mismatch")
    for field in BSEP_PACKET_SAFE_FALSE_FIELDS:
        if bsep_packet.get(field) is not False:
            errors.append(f"bsep_packet_forbidden_flag_true:{field}")

    embedded_packet = _mapping(summary.get("bsep_membrane"))
    for field in (
        "bsep_packet_id",
        "transaction_id",
        "source_orchestrator_actor_id",
        "validation_status",
        *BSEP_PACKET_SAFE_FALSE_FIELDS,
    ):
        if embedded_packet.get(field) != bsep_packet.get(field):
            errors.append(f"summary_bsep_packet_contradiction:{field}")

    packet_id = bsep_packet.get("bsep_packet_id")
    embedded_projections = _mapping(summary.get("bsep_side_projections"))
    for projection_id, expected_sides in BSEP_PROJECTION_EXPECTED_SIDES.items():
        projection = _mapping(bsep_projections.get(projection_id))
        embedded_projection = _mapping(embedded_projections.get(projection_id))
        if projection.get("validation_status") != PASS:
            errors.append(f"bsep_projection_not_pass:{projection_id}")
        if projection.get("side") not in expected_sides:
            errors.append(f"bsep_projection_side_mismatch:{projection_id}")
        if projection.get("source_bsep_packet_id") != packet_id:
            errors.append(f"bsep_projection_packet_id_mismatch:{projection_id}")
        if projection.get("transaction_id") != EXPECTED_TRANSACTION_ID:
            errors.append(f"bsep_projection_transaction_id_mismatch:{projection_id}")
        for field in BSEP_PROJECTION_SAFE_FALSE_FIELDS:
            if projection.get(field) is not False:
                errors.append(f"bsep_projection_forbidden_flag_true:{projection_id}:{field}")
        for field in (
            "projection_ref",
            "side",
            "source_bsep_packet_id",
            "transaction_id",
            "validation_status",
            *BSEP_PROJECTION_SAFE_FALSE_FIELDS,
        ):
            if embedded_projection.get(field) != projection.get(field):
                errors.append(f"summary_bsep_projection_contradiction:{projection_id}:{field}")


def _story_data(
    loaded: Mapping[str, Any],
    actor_cards: tuple[Mapping[str, Any], ...],
) -> dict[str, Any]:
    causal = _mapping(loaded.get("causal"))
    bridge = _mapping(loaded.get("bridge"))
    summary = _mapping(loaded.get("summary"))
    bsep_packet = _mapping(loaded.get("bsep_packet"))
    bsep_validation = _mapping(loaded.get("bsep_validation"))
    bsep_projections = _mapping(loaded.get("bsep_projections"))
    proposal = _mapping(causal.get("proposal"))
    proposer_request = _mapping(causal.get("proposer_request"))
    synthesis = _mapping(causal.get("synthesis"))
    evidence = _mapping(causal.get("canonical_evidence"))
    return {
        "six_offer_references": _six_offer_references(bridge),
        "bounded_offer_set": _bounded_offer_set(proposer_request),
        "proposer_story": {
            "recommended_offer_id": proposal.get("recommended_offer_id", ""),
            "semantic_summary": proposal.get("semantic_summary", ""),
            "decision_factors": tuple(_sequence(proposal.get("decision_factors"))),
            "preference_matches": tuple(_sequence(proposal.get("preference_matches"))),
            "uncertainty_notes": tuple(_sequence(proposal.get("uncertainty_notes"))),
            "requires_root_review": proposal.get("requires_root_review"),
        },
        "bsep_story": _bsep_story(bsep_packet, bsep_validation, bsep_projections, bridge),
        "vertical_dependencies": tuple(_sequence(summary.get("vertical_fractal_dependencies"))),
        "causal_reviews": tuple(_sequence(causal.get("actor_reviews"))),
        "synthesis_story": {
            "synthesis_status": synthesis.get("synthesis_status", ""),
            "canonical_actor_output_refs": tuple(_sequence(synthesis.get("canonical_actor_output_refs"))),
            "actor_recommended_offer_ids": tuple(_sequence(synthesis.get("actor_recommended_offer_ids"))),
            "actor_conflicts": tuple(_sequence(synthesis.get("actor_conflicts"))),
            "unresolved_conflict_present": synthesis.get("unresolved_conflict_present"),
            "accepted_semantic_factors": tuple(_sequence(synthesis.get("accepted_semantic_factors"))),
            "rejected_semantic_factors": tuple(_sequence(synthesis.get("rejected_semantic_factors"))),
            "canonical_selection_id": evidence.get("canonical_selection_id", ""),
            "source_proposal_id": evidence.get("source_proposal_id", ""),
            "source_actor_id": evidence.get("source_actor_id", ""),
        },
        "runtime_used": _runtime_used(actor_cards, synthesis, evidence),
        "runtime_rejected": _runtime_rejected(actor_cards, synthesis, evidence),
    }


def _source_integrity(loaded: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "expected_source_run_name": EXPECTED_SOURCE_RUN_NAME,
        "expected_source_suffix": EXPECTED_SOURCE_SUFFIX,
        "evidence_hashes": dict(_mapping(loaded.get("hashes"))),
        "fingerprint_count": len(_mapping(loaded.get("hashes"))),
        "fingerprints_are_crypto_seal": False,
    }


def _six_offer_references(bridge: Mapping[str, Any]) -> dict[str, str]:
    return {
        "semantic_recommendation": str(bridge.get("semantic_recommendation_id", "")),
        "clientroot_selected_offer": str(bridge.get("client_root_selected_offer_id", "")),
        "airlineroot_resolved_offer": str(bridge.get("airline_root_resolved_offer_id", "")),
        "hold_contract_offer": str(bridge.get("hold_contract_offer_id", "")),
        "deterministic_transaction_offer": str(bridge.get("deterministic_transaction_offer_id", "")),
        "actual_corridor_contract_context_offer": str(
            bridge.get("deterministic_corridor_offer_id", ""),
        ),
    }


def _bounded_offer_set(proposer_request: Mapping[str, Any]) -> tuple[str, ...]:
    visible = tuple(str(item) for item in _sequence(proposer_request.get("visible_candidate_ids")))
    compatible = set(str(item) for item in _sequence(proposer_request.get("client_hard_compatible_candidate_ids")))
    projection = _sequence(proposer_request.get("authoritative_candidate_projection"))
    rows: list[str] = []
    for item in projection:
        if not isinstance(item, Mapping):
            continue
        offer_id = str(item.get("offer_id", ""))
        status = "hard-compatible" if offer_id in compatible else "visible but ClientRoot-incompatible"
        rows.append(
            f"{offer_id}: {status}; amount={item.get('amount')} {item.get('currency')}; "
            f"baggage={item.get('baggage_included')}; seat={item.get('seat_characteristics')}; "
            f"changeable={item.get('changeable')}; overnight_layover={item.get('overnight_layover')}"
        )
    if not rows:
        rows = [f"{offer_id}: visible" for offer_id in visible]
    rows.append("List order is not treated as a recommendation.")
    return tuple(rows)


def _bsep_story(
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
    bridge: Mapping[str, Any],
) -> tuple[str, ...]:
    rows = [
        f"actual_bsep_packet_id: {bsep_packet.get('bsep_packet_id', '')}",
        f"bsep_validation_status: {bsep_validation.get('validation_status', '')}",
        f"live_airline_bsep_ref: {bridge.get('actual_airline_bsep_projection_ref', '')}",
        f"causal_selection_bsep_ref: {bridge.get('causal_selection_bsep_projection_ref', '')}",
        f"bsep_refs_match: {bridge.get('bsep_refs_match')}",
        "BSEP PASS occurred before Architect provider material became bounded side context.",
        "No raw passport, card, IBAN, payment token, or raw provider dump was included.",
    ]
    for key in (
        "client_bsep_projection",
        "airline_bsep_projection",
        "bank_bsep_projection",
        "cross_root_bsep_projection",
    ):
        projection = _mapping(bsep_projections.get(key))
        rows.append(
            f"{key}: status={projection.get('validation_status', '')}; "
            f"projection_ref={projection.get('projection_ref', '')}"
        )
    return tuple(rows)


def _runtime_used(
    actor_cards: tuple[Mapping[str, Any], ...],
    synthesis: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[str, ...]:
    rows: list[str] = []
    for card in actor_cards:
        rows.append(f"{card['actor_id']}: {', '.join(card['what_runtime_used'])}")
    rows.append(f"synthesis: {', '.join(str(item) for item in _sequence(synthesis.get('what_runtime_used')))}")
    rows.append(f"canonical_evidence: {', '.join(str(item) for item in _sequence(evidence.get('what_runtime_used')))}")
    return tuple(rows)


def _runtime_rejected(
    actor_cards: tuple[Mapping[str, Any], ...],
    synthesis: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[str, ...]:
    rows: list[str] = []
    for card in actor_cards:
        rows.append(f"{card['actor_id']}: {', '.join(card['what_runtime_rejected'])}")
    rows.append(
        f"synthesis: {', '.join(str(item) for item in _sequence(synthesis.get('what_runtime_rejected')))}"
    )
    rows.append(
        f"canonical_evidence: {', '.join(str(item) for item in _sequence(evidence.get('what_runtime_rejected')))}"
    )
    return tuple(rows)


def _counter_table(
    *,
    loaded: Mapping[str, Any],
    actor_cards: tuple[Mapping[str, Any], ...],
    allow_raw: bool,
    allow_prompt: bool,
) -> dict[str, int]:
    summary = _mapping(loaded.get("summary"))
    counters = _mapping(summary.get("counter_table"))
    result = {key: _safe_int(counters.get(key, 0)) for key in SOURCE_COUNTER_EXPECTATIONS}
    for key in ZERO_COUNTERS:
        result[key] = _safe_int(counters.get(key, 0))
    result.update(
        {
            "human_story_created_count": 1,
            "actor_cards_rendered_count": len(actor_cards),
            "causal_actor_cards_rendered_count": len(
                [card for card in actor_cards if card["actor_id"] in CAUSAL_ACTOR_IDS],
            ),
            "six_offer_references_rendered_count": 6,
            "full_prompts_printed_count": len(actor_cards) if allow_prompt else 0,
            "raw_responses_printed_count": len(actor_cards) if allow_raw else 0,
            "renderer_live_lane_rerun_count": 0,
            "renderer_deterministic_runner_rerun_count": 0,
            "renderer_corridor_execution_count": 0,
            "renderer_provider_called_count": 0,
            "renderer_network_called_count": 0,
            "renderer_gemini_called_count": 0,
            "renderer_packet_created_count": 0,
            "renderer_receipt_created_count": 0,
            "renderer_payment_created_count": 0,
            "renderer_ticket_created_count": 0,
            "renderer_booking_created_count": 0,
            "renderer_real_world_effects_count": 0,
        },
    )
    return result


def _skipped_counters() -> dict[str, int]:
    return {
        "renderer_live_lane_rerun_count": 0,
        "renderer_deterministic_runner_rerun_count": 0,
        "renderer_corridor_execution_count": 0,
        "renderer_provider_called_count": 0,
        "renderer_network_called_count": 0,
        "renderer_gemini_called_count": 0,
        "renderer_packet_created_count": 0,
        "renderer_receipt_created_count": 0,
        "renderer_payment_created_count": 0,
        "renderer_ticket_created_count": 0,
        "renderer_booking_created_count": 0,
        "renderer_real_world_effects_count": 0,
    }


def _client_request_story(report: Mapping[str, Any]) -> str:
    proposer = _mapping(report["proposer_story"])
    return (
        "Preference A означает: клиент предпочитает более низкую цену, место у окна "
        "и changeable option. Hard constraints остаются отдельно: бюджет, валюта, "
        "даты, маршрут, багаж и запрет overnight layover. Gemini мог интерпретировать "
        "soft preferences, но не переписывал hard constraints. "
        f"Actual recommendation summary: {proposer.get('semantic_summary', '')}"
    )


def _horizontal_story(actor_cards: tuple[Mapping[str, Any], ...]) -> tuple[str, ...]:
    sides = {"client": [], "airline": [], "bank": [], "cross_root_advisory": []}
    for card in actor_cards:
        side = str(card.get("side", ""))
        if side in sides and not card.get("parent_actor_id"):
            sides[side].append(str(card["actor_id"]))
    return tuple(
        f"{side}: independent validated semantic work by {', '.join(ids)}"
        for side, ids in sides.items()
        if ids
    )


def _vertical_story(dependencies: tuple[Any, ...]) -> tuple[str, ...]:
    rows = []
    for dep in dependencies:
        if not isinstance(dep, Mapping):
            continue
        rows.append(
            f"{dep.get('parent_actor_id')} -> {dep.get('child_actor_id')}: "
            f"parent_status={dep.get('parent_validation_status')}; "
            f"started_after_parent={dep.get('child_started_after_parent_validation')}; "
            f"parent_canonical_summary={dep.get('child_received_parent_canonical_summary')}; "
            f"parent_raw_response={dep.get('child_received_parent_raw_response')}; "
            f"sibling_raw_output={dep.get('child_received_sibling_raw_output')}"
        )
    return tuple(rows)


def _causal_actor_story(causal_reviews: tuple[Any, ...]) -> tuple[str, ...]:
    rows = []
    for item in causal_reviews:
        if not isinstance(item, Mapping):
            continue
        rows.append(
            f"{item.get('actor_id')}: role={item.get('review_role')}; "
            f"reviewed_offer={item.get('reviewed_offer_id')}; status={item.get('review_status')}; "
            f"semantic_factors={item.get('semantic_factors')}; conflicts={item.get('blocking_conflicts')}"
        )
    return tuple(rows)


def _render_actor_card(card: Mapping[str, Any]) -> tuple[str, ...]:
    rows = [
        f"- actor {card['actor_index']}: {card['actor_id']} ({card['human_role_name']})",
        f"  side: {card['side']}",
        f"  parent_actor: {card.get('parent_actor_id', '')}",
        f"  bounded_input_summary: {card['bounded_input_summary']}",
        f"  provider_returned: {card['provider_returned']}",
        f"  validation_status: {card['validation_status']}",
        f"  canonical_semantic_summary: {card['canonical_semantic_summary']}",
        f"  what_runtime_used: {', '.join(card['what_runtime_used'])}",
        f"  what_runtime_rejected: {', '.join(card['what_runtime_rejected'])}",
        f"  authority_created: {card['authority_created']}",
        f"  action_permission_created: {card['action_permission_created']}",
        f"  real_world_effects_count: {card['real_world_effects_count']}",
        f"  prompt_displayed_in_full: {card['prompt_displayed_in_full']}",
        f"  raw_response_displayed: {card['raw_response_displayed']}",
    ]
    if card.get("causal_review_semantic_factors"):
        rows.append(
            f"  causal_review_semantic_factors: {', '.join(card['causal_review_semantic_factors'])}"
        )
        rows.append(
            f"  causal_review_blocking_conflicts: {', '.join(card['causal_review_blocking_conflicts'])}"
        )
        rows.append(f"  causal_review_status: {card['causal_review_status']}")
    if card.get("prompt_displayed_in_full"):
        rows.append(f"  full_prompt: {card.get('prompt_text_for_display', '')}")
    if card.get("raw_response_displayed"):
        rows.append(
            f"  raw_provider_material_non_authoritative: {card.get('raw_response_text_for_display', '')}"
        )
    return tuple(rows)


def _format_mapping(value: Mapping[str, Any]) -> str:
    return "; ".join(f"{key}={value[key]}" for key in sorted(value))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return ()


def _object_array(value: Any, reason: str, errors: list[str]) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        errors.append(reason)
        return ()
    rows: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append(reason)
            continue
        rows.append(item)
    return tuple(rows)


def _string_array(
    value: Any,
    reason: str,
    errors: list[str],
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        errors.append(reason)
        return ()
    if not value and not allow_empty:
        errors.append(reason)
        return ()
    rows: list[str] = []
    for item in value:
        if not _is_non_empty_string(item):
            errors.append(reason)
            continue
        rows.append(item)
    return tuple(rows)


def _required_non_empty_string(value: Any, reason: str, errors: list[str]) -> str:
    if not _is_non_empty_string(value):
        errors.append(reason)
        return ""
    return value


def _optional_non_empty_string(value: Any, reason: str, errors: list[str]) -> str:
    if value is None:
        return ""
    if not _is_non_empty_string(value):
        errors.append(reason)
        return ""
    return value


def _required_enum_string(
    value: Any,
    accepted: tuple[str, ...],
    reason: str,
    errors: list[str],
) -> str:
    text = _required_non_empty_string(value, reason, errors)
    if text and text not in accepted:
        errors.append(reason)
        return ""
    return text


def _optional_enum_string(
    value: Any,
    accepted: tuple[str, ...],
    reason: str,
    errors: list[str],
) -> str:
    text = _optional_non_empty_string(value, reason, errors)
    if text and text not in accepted:
        errors.append(reason)
        return ""
    return text


def _source_actor_report_map(value: Any, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    rows = _object_array(value, "semantic_actor_reports_invalid", errors)
    result: dict[str, Mapping[str, Any]] = {}
    for item in rows:
        actor_id = item.get("actor_id")
        if not _is_non_empty_string(actor_id):
            errors.append("semantic_actor_report_actor_id_invalid")
            continue
        result[actor_id] = item
    return result


def _causal_actor_review_map(value: Any, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    rows = _object_array(value, "causal_actor_reviews_invalid", errors)
    result: dict[str, Mapping[str, Any]] = {}
    for item in rows:
        actor_id = item.get("actor_id")
        if not _is_non_empty_string(actor_id):
            errors.append("causal_actor_review_actor_id_invalid")
            continue
        result[actor_id] = item
    return result


def _is_non_empty_string(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def _default_side(actor_id: str) -> str:
    if actor_id.startswith("client_"):
        return "client"
    if actor_id.startswith("airline_"):
        return "airline"
    if actor_id.startswith("bank_"):
        return "bank"
    if actor_id.startswith("tri_party_evidence"):
        return "cross_root_advisory"
    return "transaction"


def _safe_int(value: Any) -> int:
    if type(value) is bool:
        return 0
    if isinstance(value, int):
        return value
    return 0


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return tuple(result)


def _non_claims() -> tuple[str, ...]:
    return (
        "Preference A all-real run only",
        "no all-real Preference B claim",
        "no real-provider A/B counterfactual claim",
        "injected A/B proof is separate",
        "mock ticket and mock PNR evidence only",
        "not production",
        "not public-auditor package",
        "Ledger not implemented",
        "Crypto Seal not implemented",
        "Replay not implemented",
        "audit fingerprints are not Crypto Artifact Seal",
    )


if __name__ == "__main__":
    raise SystemExit(main())
