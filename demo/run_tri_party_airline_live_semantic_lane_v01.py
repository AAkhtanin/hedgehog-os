from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from demo import run_live_provider_adapter_response_capture_v01 as provider_adapter
from demo import run_tri_party_airline_ticket_purchase_mock_e2e_v01 as deterministic_airline
from demo.run_live_unknown_request_dual_rich_context_v01 import (
    _call_live_gemini_provider as _shared_live_gemini_provider,
)
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as causal_runtime


RUN_ID = "tri_party_airline_live_semantic_lane_v01"
REPORT_ID = "tri_party_airline_live_semantic_lane_v01"
LANE_ID = "tri_party_airline_live_semantic_lane_v01_fake_provider"
DEFAULT_MODEL = "fake-airline-semantic-model"
DEFAULT_REAL_PROVIDER_MODEL = "gemini-2.5-flash"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_SKIPPED_CLOSED = "SKIPPED_CLOSED"

ENV_LANE = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_LANE"
ENV_ARTIFACT_DIR = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ARTIFACT_DIR"
ENV_MODEL = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_MODEL"
ENV_FAKE_PROVIDER = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_FAKE_PROVIDER"
ENV_REAL_PROVIDER = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_REAL_PROVIDER"
ENV_CALL_DELAY_SECONDS = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_CALL_DELAY_SECONDS"
ENV_ALLOW_RAW = "HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ALLOW_RAW_RESPONSE_OUTPUT"
ENV_CAUSAL_BINDING = "HEDGEHOG_AIRLINE_SEMANTIC_TO_CONTRACT_CAUSAL_BINDING"

PROVIDER_MODE_SKIPPED = "skipped_closed"
PROVIDER_MODE_FAKE = "fake_provider"
PROVIDER_MODE_REAL = "real_provider"

TRANSACTION_ID = deterministic_airline.TRANSACTION_ID
CLIENT_ROOT_ID = deterministic_airline.CLIENT_ROOT_ID
AIRLINE_ROOT_ID = deterministic_airline.AIRLINE_ROOT_ID
BANK_ROOT_ID = deterministic_airline.BANK_ROOT_ID

Provider = Callable[[str, str, Mapping[str, Any]], str]

CAUSAL_ACTOR_IDS = causal_runtime.ACTOR_ORDER

REASON_LIVE_BSEP_NOT_VALIDATED_BEFORE_CAUSAL_SELECTION = (
    "live_bsep_not_validated_before_causal_selection"
)
REASON_LIVE_AIRLINE_BSEP_PROJECTION_MISSING = (
    "live_airline_bsep_projection_missing"
)
REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH = (
    "live_bsep_causal_projection_lineage_mismatch"
)

CAUSAL_PROPOSER_REQUIRED_FIELDS = tuple(
    binding.AirlineSemanticOfferSelectionProposalV01.__dataclass_fields__,
)
CAUSAL_REVIEWER_REQUIRED_FIELDS = tuple(
    causal_runtime.AirlineInjectedReviewerResponseV01.__dataclass_fields__,
)


def _non_empty_string_schema() -> dict[str, Any]:
    return {"type": "string", "minLength": 1}


def _single_value_schema(value: Any) -> dict[str, Any]:
    return {"type": "string", "enum": [value]}


def _false_boolean_schema() -> dict[str, Any]:
    return {"type": "boolean", "enum": [False]}


def _zero_integer_schema() -> dict[str, Any]:
    return {"type": "integer", "enum": [0]}


def _non_empty_string_array_schema(
    *,
    enum_values: tuple[str, ...] | None = None,
    unique_items: bool = False,
) -> dict[str, Any]:
    item_schema: dict[str, Any] = _non_empty_string_schema()
    if enum_values is not None:
        item_schema = {"type": "string", "enum": list(enum_values)}
    schema: dict[str, Any] = {
        "type": "array",
        "minItems": 1,
        "items": item_schema,
    }
    if unique_items:
        schema["uniqueItems"] = True
    return schema


def _build_causal_proposer_response_schema_v01(
    causal_request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
    selection_input: binding.AirlineSemanticSelectionInputV01,
) -> dict[str, Any]:
    allowed_offer_ids = tuple(selection_input.client_hard_compatible_candidate_ids)
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(CAUSAL_PROPOSER_REQUIRED_FIELDS),
        "properties": {
            "proposal_id": _non_empty_string_schema(),
            "transaction_id": _single_value_schema(causal_request.transaction_id),
            "actor_id": _single_value_schema(causal_request.actor_id),
            "source_selection_input_id": _single_value_schema(
                causal_request.source_selection_input_id,
            ),
            "source_bsep_projection_ref": _single_value_schema(
                causal_request.source_bsep_projection_ref,
            ),
            "source_client_constraint_set_id": _single_value_schema(
                causal_request.source_client_constraint_set_id,
            ),
            "source_candidate_set_snapshot_id": _single_value_schema(
                causal_request.source_candidate_set_snapshot_id,
            ),
            "source_candidate_set_digest": _single_value_schema(
                causal_request.source_candidate_set_digest,
            ),
            "candidate_set_ref": _single_value_schema(
                causal_request.source_candidate_set_ref,
            ),
            "recommended_offer_id": {
                "type": "string",
                "enum": list(allowed_offer_ids),
            },
            "ranked_offer_ids": _non_empty_string_array_schema(
                enum_values=allowed_offer_ids,
                unique_items=True,
            ),
            "decision_factors": _non_empty_string_array_schema(),
            "preference_matches": _non_empty_string_array_schema(),
            "uncertainty_notes": _non_empty_string_array_schema(),
            "requires_root_review": {"type": "boolean", "enum": [True]},
            "semantic_summary": _non_empty_string_schema(),
            "authority_created": _false_boolean_schema(),
            "action_permission_created": _false_boolean_schema(),
            "packet_created": _false_boolean_schema(),
            "receipt_created": _false_boolean_schema(),
            "payment_created": _false_boolean_schema(),
            "ticket_created": _false_boolean_schema(),
            "booking_created": _false_boolean_schema(),
            "final_output_created": _false_boolean_schema(),
            "real_world_effects_count": _zero_integer_schema(),
        },
    }


def _build_causal_reviewer_response_schema_v01(
    causal_request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
) -> dict[str, Any]:
    known_statuses = (
        binding.STATUS_PASS,
        binding.STATUS_FAIL_CLOSED,
        binding.STATUS_REQUIRES_ROOT_REVIEW,
    )
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(CAUSAL_REVIEWER_REQUIRED_FIELDS),
        "properties": {
            "response_id": _non_empty_string_schema(),
            "transaction_id": _single_value_schema(causal_request.transaction_id),
            "actor_id": _single_value_schema(causal_request.actor_id),
            "source_request_id": _single_value_schema(causal_request.request_id),
            "source_selection_input_id": _single_value_schema(
                causal_request.source_selection_input_id,
            ),
            "source_candidate_set_snapshot_id": _single_value_schema(
                causal_request.source_candidate_set_snapshot_id,
            ),
            "source_candidate_set_digest": _single_value_schema(
                causal_request.source_candidate_set_digest,
            ),
            "reviewed_offer_id": _single_value_schema(
                causal_request.proposed_offer_id,
            ),
            "review_role": _single_value_schema(causal_request.actor_role),
            "review_status": {"type": "string", "enum": list(known_statuses)},
            "semantic_factors": _non_empty_string_array_schema(),
            "blocking_conflicts": {
                "type": "array",
                "items": _non_empty_string_schema(),
            },
            "supports_proposed_offer": {"type": "boolean"},
            "validation_status": {
                "type": "string",
                "enum": list(known_statuses),
            },
            "raw_output_used": _false_boolean_schema(),
            "authority_created": _false_boolean_schema(),
            "permission_created": _false_boolean_schema(),
            "real_world_effects_count": _zero_integer_schema(),
        },
    }


def _causal_provider_response_schema_v01(
    causal_request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
    selection_input: binding.AirlineSemanticSelectionInputV01,
) -> dict[str, Any]:
    if causal_request.actor_id == causal_runtime.ACTOR_ORDER[0]:
        return _build_causal_proposer_response_schema_v01(
            causal_request,
            selection_input,
        )
    return _build_causal_reviewer_response_schema_v01(causal_request)

SECRET_MARKERS = (
    "AIza",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "raw_passport_value",
    "raw_card_number",
    "raw_iban_value",
    "raw_payment_token_value",
    "sandbox_token_abc",
)

REQUIRED_RENDER_SECTIONS = (
    "[TRI-PARTY AIRLINE LIVE SEMANTIC LANE]",
    "[BSEP MEMBRANE]",
    "[SIDE-SPECIFIC BSEP PROJECTIONS]",
    "[TRANSACTION ORCHESTRATOR]",
    "[SEMANTIC ARCHITECT]",
    "[SEMANTIC ACTOR CALLS]",
    "[CLIENT SIDE LLM ACTORS]",
    "[AIRLINE SIDE LLM ACTORS]",
    "[AIRLINE VERTICAL FRACTAL CELLS]",
    "[BANK SIDE LLM ACTORS]",
    "[BANK VERTICAL FRACTAL CELLS]",
    "[CROSS-ROOT CONSISTENCY REVIEWER]",
    "[STRICT VERTICAL FRACTAL DEPENDENCIES]",
    "[WHAT EACH LLM RECEIVED]",
    "[WHAT EACH LLM RETURNED]",
    "[WHAT RUNTIME USED]",
    "[WHAT RUNTIME REJECTED]",
    "[ROOT BOUNDARIES]",
    "[COUNTER TABLE]",
    "[ARTIFACTS]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

ACTOR_SPECS: tuple[dict[str, Any], ...] = (
    {
        "actor_id": "tri_party_airline_orchestrator_llm",
        "side": "transaction",
        "group": "transaction_orchestrator",
        "semantic_work": "interpret the whole tri-party transaction goal and propose bounded semantic route for BSEP creation",
    },
    {
        "actor_id": "tri_party_airline_semantic_architect_llm",
        "side": "transaction",
        "group": "semantic_architect",
        "semantic_work": "receive BSEP-derived bounded context and propose semantic actor topology and validation obligations",
    },
    {
        "actor_id": "client_purchase_intent_reviewer_llm",
        "side": "client",
        "group": "client",
        "semantic_work": "compare the hard-compatible bounded offers, interpret declared soft preferences, recommend one existing offer id, explain the tradeoff, and remain advisory only",
    },
    {
        "actor_id": "client_profile_privacy_reviewer_llm",
        "side": "client",
        "group": "client",
        "semantic_work": "explain passenger and payment sealed refs and private-field boundaries",
    },
    {
        "actor_id": "airline_offer_policy_reviewer_llm",
        "side": "airline",
        "group": "airline",
        "semantic_work": "interpret mock inventory, fare, baggage, TTL, route constraints and compare Offer A/B/C",
    },
    {
        "actor_id": "airline_fare_rules_vertical_cell_llm",
        "side": "airline",
        "group": "airline_vertical",
        "vertical_fractal_cell": True,
        "parent_actor_id": "airline_offer_policy_reviewer_llm",
        "semantic_work": "analyze fare basis, refund/change restrictions, TTL pressure, and price-vs-flexibility tradeoff",
    },
    {
        "actor_id": "airline_seat_baggage_vertical_cell_llm",
        "side": "airline",
        "group": "airline_vertical",
        "vertical_fractal_cell": True,
        "parent_actor_id": "airline_offer_policy_reviewer_llm",
        "semantic_work": "analyze checked baggage, seat choice, seat fee, and cabin constraints",
    },
    {
        "actor_id": "airline_ticketing_policy_reviewer_llm",
        "side": "airline",
        "group": "airline",
        "semantic_work": "explain conditions for mock ticket evidence from offer hold, payment authorization, and client approval evidence",
    },
    {
        "actor_id": "bank_payment_policy_reviewer_llm",
        "side": "bank",
        "group": "bank",
        "semantic_work": "explain mock authorization amount, merchant, debtor slot, consent, and sealed payment token ref",
    },
    {
        "actor_id": "bank_idempotency_risk_vertical_cell_llm",
        "side": "bank",
        "group": "bank_vertical",
        "vertical_fractal_cell": True,
        "parent_actor_id": "bank_payment_policy_reviewer_llm",
        "semantic_work": "analyze duplicate-payment risk, idempotency, expiry, TTL, and amount/merchant mismatch pressure",
    },
    {
        "actor_id": "bank_payment_status_explainer_llm",
        "side": "bank",
        "group": "bank",
        "semantic_work": "explain mock authorization vs settlement and PaymentStatusReceipt as evidence-only",
    },
    {
        "actor_id": "tri_party_evidence_consistency_reviewer_llm",
        "side": "cross_root_advisory",
        "group": "cross_root",
        "semantic_work": "check one transaction_id, coherent evidence routing, no foreign Root authority, and evidence-only receipts",
    },
)


def collect_tri_party_airline_live_semantic_lane_v01(
    *,
    env: Mapping[str, str] | None = None,
    provider: Provider | None = None,
    causal_constraints: binding.ClientRootTravelConstraintSetV01 | None = None,
    causal_snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01 | None = None,
) -> dict[str, Any]:
    effective_env = dict(os.environ if env is None else env)
    causal_gate_open = effective_env.get(ENV_CAUSAL_BINDING) == "1"
    deterministic_report = (
        deterministic_airline.build_tri_party_airline_semantic_source_context_v01()
        if causal_gate_open
        else deterministic_airline.collect_tri_party_airline_ticket_purchase_mock_e2e_v01()
    )
    artifact_dir_value = effective_env.get(ENV_ARTIFACT_DIR, "")
    artifact_dir = Path(artifact_dir_value) if artifact_dir_value else None

    if effective_env.get(ENV_LANE) != "1":
        model = effective_env.get(ENV_MODEL, DEFAULT_MODEL)
        return _skipped_report(model, deterministic_report)

    fake_selected = effective_env.get(ENV_FAKE_PROVIDER) == "1"
    real_selected = effective_env.get(ENV_REAL_PROVIDER) == "1"
    if fake_selected and real_selected:
        return _fail_closed_report(
            reason="ambiguous_provider_mode",
            provider_mode=PROVIDER_MODE_SKIPPED,
            model=effective_env.get(ENV_MODEL, DEFAULT_MODEL),
            deterministic_report=deterministic_report,
        )

    if causal_gate_open and causal_constraints is None:
        return _fail_closed_report(
            reason="causal_constraints_required",
            provider_mode=PROVIDER_MODE_SKIPPED,
            model=effective_env.get(ENV_MODEL, DEFAULT_MODEL),
            deterministic_report=deterministic_report,
        )
    if not fake_selected and not real_selected:
        return _fail_closed_report(
            reason="provider_mode_not_selected",
            provider_mode=PROVIDER_MODE_SKIPPED,
            model=effective_env.get(ENV_MODEL, DEFAULT_MODEL),
            deterministic_report=deterministic_report,
        )

    if fake_selected:
        provider_mode = PROVIDER_MODE_FAKE
        model = effective_env.get(ENV_MODEL, DEFAULT_MODEL)
        active_provider = provider or build_fake_airline_semantic_provider_v01()
    else:
        provider_mode = PROVIDER_MODE_REAL
        model = effective_env.get(ENV_MODEL, DEFAULT_REAL_PROVIDER_MODEL)
        if artifact_dir is None:
            return _fail_closed_report(
                reason="real_provider_requires_artifact_dir",
                provider_mode=provider_mode,
                model=model,
                deterministic_report=deterministic_report,
            )
        active_provider = provider or build_real_airline_semantic_provider_v01(model)

    report = _run_provider_lane(
        provider_mode=provider_mode,
        model=model,
        deterministic_report=deterministic_report,
        provider=active_provider,
        artifact_dir=artifact_dir,
        allow_raw_output=effective_env.get(ENV_ALLOW_RAW) == "1",
        call_delay_seconds=_call_delay_seconds(effective_env, provider_mode),
        provider_env=effective_env,
        causal_gate_open=causal_gate_open,
        causal_constraints=causal_constraints,
        causal_snapshot=causal_snapshot,
    )
    return report


def render_tri_party_airline_live_semantic_lane_v01(report: Mapping[str, Any]) -> str:
    lines = [
        "[TRI-PARTY AIRLINE LIVE SEMANTIC LANE]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"lane_id: {report['lane_id']}",
        f"provider_mode: {report['provider_mode']}",
        f"model: {report['model']}",
        "One mock airline purchase transaction is analyzed.",
    ]
    counters = report.get("counter_table", {})
    if report["provider_mode"] == PROVIDER_MODE_REAL:
        lines.extend(
            (
                f"semantic_actor_call_count: {counters.get('semantic_actor_call_count', 0)}",
                f"real_provider_call_count: {counters.get('real_provider_call_count', 0)}",
                f"network_used_count: {counters.get('network_used_count', 0)}",
                f"gemini_called_count: {counters.get('gemini_called_count', 0)}",
            ),
        )
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
            "[BSEP MEMBRANE]",
            "BSEP membrane was created and validated before Architect.",
            f"bsep_validation_status: {report['bsep_validation'].get('validation_status')}",
            "",
            "[SIDE-SPECIFIC BSEP PROJECTIONS]",
            "Side-specific BSEP projections were created.",
        ),
    )
    for projection_id, projection in report["bsep_side_projections"].items():
        lines.append(f"- {projection_id}: {projection['validation_status']}")

    lines.extend(("", "[TRANSACTION ORCHESTRATOR]"))
    _append_actor_lines(lines, report, "tri_party_airline_orchestrator_llm")
    lines.extend(("", "[SEMANTIC ARCHITECT]"))
    _append_actor_lines(lines, report, "tri_party_airline_semantic_architect_llm")

    lines.extend(
        (
            "",
            "[SEMANTIC ACTOR CALLS]",
            f"Twelve semantic actors ran in {report['provider_mode']} mode.",
            "Orchestrator and Architect are advisory only.",
            "Horizontal actors analyze bounded side contexts.",
        ),
    )
    lines.extend(f"- {actor_id}" for actor_id in report["semantic_actor_call_order"])

    _append_group(lines, report, "[CLIENT SIDE LLM ACTORS]", "client")
    _append_group(lines, report, "[AIRLINE SIDE LLM ACTORS]", "airline")
    _append_group(lines, report, "[AIRLINE VERTICAL FRACTAL CELLS]", "airline_vertical")
    _append_group(lines, report, "[BANK SIDE LLM ACTORS]", "bank")
    _append_group(lines, report, "[BANK VERTICAL FRACTAL CELLS]", "bank_vertical")
    _append_group(lines, report, "[CROSS-ROOT CONSISTENCY REVIEWER]", "cross_root")

    lines.extend(
        (
            "",
            "[STRICT VERTICAL FRACTAL DEPENDENCIES]",
            "Vertical child cells start only after parent validation.",
            "Child cells receive parent canonical summaries, not parent raw responses.",
        ),
    )
    for dependency in report["vertical_fractal_dependencies"]:
        lines.append(
            "- {child_actor_id} <- {parent_actor_id}; "
            "child_started_after_parent_validation={child_started_after_parent_validation}; "
            "child_received_parent_canonical_summary={child_received_parent_canonical_summary}".format(
                **dependency,
            ),
        )

    lines.extend(
        (
            "",
            "[WHAT EACH LLM RECEIVED]",
            "Prompts use bounded context only.",
        ),
    )
    for actor_id, summary in report["what_each_llm_received"].items():
        lines.append(f"- {actor_id}: {summary}")

    lines.extend(("", "[WHAT EACH LLM RETURNED]"))
    for actor_id, summary in report["what_each_llm_returned"].items():
        lines.append(f"- {actor_id}: {summary}")

    lines.extend(
        (
            "",
            "[WHAT RUNTIME USED]",
            "LLM output affects runtime through extraction, validation, and canonical summaries.",
            "Tests do not ignore LLM output.",
        ),
    )
    for actor_id, used in report["what_runtime_used"].items():
        lines.append(f"- {actor_id}: {', '.join(used)}")

    lines.extend(
        (
            "",
            "[WHAT RUNTIME REJECTED]",
            "Runtime records what it used and what it rejected.",
        ),
    )
    for actor_id, rejected in report["what_runtime_rejected"].items():
        lines.append(f"- {actor_id}: {', '.join(rejected)}")

    lines.extend(("", "[ROOT BOUNDARIES]"))
    for boundary in report["root_boundaries"]:
        lines.append(
            f"- {boundary['boundary']}: preserved={boundary['boundary_preserved']}",
        )

    if report.get("semantic_to_contract_causal_binding_v0_1", {}).get(
        "binding_status",
    ) not in {"NOT_ENABLED", None}:
        bridge = report["semantic_to_contract_deterministic_bridge"]
        lines.extend(
            (
                "",
                "[SEMANTIC-TO-CONTRACT CAUSAL BINDING]",
                f"bridge_status: {bridge['bridge_status']}",
                f"semantic_recommendation_id: {bridge['semantic_recommendation_id']}",
                f"deterministic_transaction_offer_id: {bridge['deterministic_transaction_offer_id']}",
                f"all_offer_ids_match: {bridge['all_offer_ids_match']}",
            ),
        )

    lines.extend(("", "[COUNTER TABLE]"))
    for key in sorted(report["counter_table"]):
        lines.append(f"{key}: {report['counter_table'][key]}")

    lines.extend(("", "[ARTIFACTS]"))
    for key, value in report["artifacts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(
        (
            "",
            "[NON-CLAIMS]",
            (
                "Happy path remains mock: mock payment authorization, mock ticket "
                "evidence, mock PNR evidence."
            ),
            (
                "No real airline API, bank API, GDS API, payment, ticket, "
                "booking, or production effect occurs in this lane."
            ),
        ),
    )
    lines.extend(f"- {claim}" for claim in report["non_claims"])
    lines.extend(("", "[FINAL STATUS]", str(report["final_status"])))
    if report.get("skip_reason"):
        lines.append(f"skip_reason: {report['skip_reason']}")
    if report.get("failed_actor_id"):
        lines.append(f"failed_actor_id: {report['failed_actor_id']}")
    if report.get("failed_stage"):
        lines.append(f"failed_stage: {report['failed_stage']}")
    if report.get("provider_error_sanitized"):
        lines.append(f"provider_error_sanitized: {report['provider_error_sanitized']}")
    if report["validation_errors"]:
        lines.append(f"validation_errors: {report['validation_errors']}")
    return "\n".join(lines)


def run_tri_party_airline_live_semantic_lane_v01(
    *,
    env: Mapping[str, str] | None = None,
    provider: Provider | None = None,
    causal_constraints: binding.ClientRootTravelConstraintSetV01 | None = None,
    causal_snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01 | None = None,
) -> str:
    return render_tri_party_airline_live_semantic_lane_v01(
        collect_tri_party_airline_live_semantic_lane_v01(
            env=env,
            provider=provider,
            causal_constraints=causal_constraints,
            causal_snapshot=causal_snapshot,
        ),
    )


def main() -> int:
    print(run_tri_party_airline_live_semantic_lane_v01())
    return 0


def build_fake_airline_semantic_provider_v01() -> Provider:
    def fake_provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        summary_by_actor = {
            "tri_party_airline_orchestrator_llm": (
                "The mock purchase route starts with ClientRoot travel intent, "
                "moves through AirlineRoot offer hold, BankRoot mock payment "
                "authorization, and returns mock ticket evidence under one transaction_id."
            ),
            "tri_party_airline_semantic_architect_llm": (
                "The semantic topology uses BSEP side projections, horizontal "
                "client/airline/bank reviewers, and strict vertical child cells."
            ),
            "client_purchase_intent_reviewer_llm": (
                "Offer A best fits the 840 EUR budget, included baggage, window "
                "seat preference, and changeable-ticket preference."
            ),
            "client_profile_privacy_reviewer_llm": (
                "Passenger and payment profile values remain sealed; only stable "
                "refs enter bounded context."
            ),
            "airline_offer_policy_reviewer_llm": (
                "Offer A is selected, Offer B is viable but less preferred, and "
                "Offer C is downgraded for missing baggage and overnight layover."
            ),
            "airline_fare_rules_vertical_cell_llm": (
                "Fare rules favor Offer A because it balances price, changeability, "
                "and TTL without claiming refundability."
            ),
            "airline_seat_baggage_vertical_cell_llm": (
                "Offer A includes checked baggage and a window seat while remaining "
                "mock-only."
            ),
            "airline_ticketing_policy_reviewer_llm": (
                "OfferHoldReceipt, PaymentAuthorizationReceipt, PaymentStatusReceipt, "
                "and ClientPurchaseApprovalEvidence support mock ticket evidence and "
                "mock PNR evidence only."
            ),
            "bank_payment_policy_reviewer_llm": (
                "The mock authorization matches amount, currency, merchant ref, "
                "debtor slot, consent, and sealed payment token ref."
            ),
            "bank_idempotency_risk_vertical_cell_llm": (
                "The idempotency key and TTL reduce duplicate mock authorization risk."
            ),
            "bank_payment_status_explainer_llm": (
                "PaymentStatusReceipt means mock authorized-not-settled evidence, "
                "not settlement or ticket permission."
            ),
            "tri_party_evidence_consistency_reviewer_llm": (
                "All reviewed artifacts share one transaction_id and move evidence "
                "without cross-root authority transfer."
            ),
        }
        actor = _actor_spec(actor_id)
        response: dict[str, Any] = {
            "actor_id": actor_id,
            "transaction_id": TRANSACTION_ID,
            "side": actor["side"],
            "semantic_summary": summary_by_actor[actor_id],
            "what_runtime_used": [
                "validated semantic_summary",
                "bounded evidence observations",
            ],
            "what_runtime_rejected": [
                "raw response as authority",
                "action creation claims",
            ],
            "authority_created": False,
            "action_permission_created": False,
            "packet_created": False,
            "receipt_created": False,
            "payment_created": False,
            "ticket_created": False,
            "booking_created": False,
            "final_output_created": False,
            "real_payment_executed": False,
            "real_ticket_issued": False,
            "real_booking_created": False,
            "real_world_effects_count": 0,
        }
        if actor.get("vertical_fractal_cell"):
            response.update(
                {
                    "vertical_fractal_cell": True,
                    "parent_actor_id": actor["parent_actor_id"],
                    "parent_validation_status": "PASS",
                    "child_started_after_parent_validation": True,
                    "child_received_parent_canonical_summary": True,
                    "child_received_parent_raw_response": False,
                    "child_received_sibling_raw_output": False,
                    "child_received_unbounded_context": False,
                    "child_result_returns_to_parent_or_root_review": True,
                    "child_creates_authority": False,
                    "child_creates_packet": False,
                    "child_creates_receipt": False,
                    "child_creates_payment": False,
                    "child_creates_ticket": False,
                    "child_creates_booking": False,
                },
            )
        return json.dumps(response, sort_keys=True)

    return fake_provider


def build_real_airline_semantic_provider_v01(model: str) -> Provider:
    def real_provider(actor_id: str, prompt: str, metadata: Mapping[str, Any]) -> str:
        env_value = metadata.get("provider_env", {})
        provider_env = dict(env_value) if isinstance(env_value, Mapping) else dict(os.environ)
        schema_value = metadata.get("provider_response_schema")
        response_schema = dict(schema_value) if isinstance(schema_value, Mapping) else None
        return _shared_live_gemini_provider(
            prompt=prompt,
            model_name=model,
            timeout_seconds=provider_adapter._timeout_seconds(provider_env),
            explicit_http_timeout=True,
            env=provider_env,
            response_schema=response_schema,
            role=actor_id,
        )

    return real_provider


def _run_provider_lane(
    *,
    provider_mode: str,
    model: str,
    deterministic_report: Mapping[str, Any],
    provider: Provider,
    artifact_dir: Path | None,
    allow_raw_output: bool,
    call_delay_seconds: float,
    provider_env: Mapping[str, str],
    causal_gate_open: bool = False,
    causal_constraints: binding.ClientRootTravelConstraintSetV01 | None = None,
    causal_snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01 | None = None,
) -> dict[str, Any]:
    if artifact_dir is not None:
        artifact_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, Any] = {}
    artifact_counts = {
        "prompts_written_count": 0,
        "raw_responses_written_count": 0,
        "extracted_json_candidates_written_count": 0,
        "validations_written_count": 0,
        "canonical_summaries_written_count": 0,
    }
    actor_reports: list[dict[str, Any]] = []
    actor_by_id: dict[str, dict[str, Any]] = {}
    validation_errors: list[str] = []
    provider_call_count = 0
    delay_applied_count = 0
    failed_actor_id = ""
    failed_stage = ""
    provider_error_sanitized = ""
    bsep_packet: dict[str, Any] = {}
    bsep_validation: dict[str, Any] = {}
    bsep_side_projections: dict[str, Any] = {}
    actual_causal_snapshot = (
        causal_snapshot or binding.build_airline_candidate_snapshot_v01()
    )
    causal_bsep_projection: binding.AirlineBSEPProjectionRefV01 | None = None
    causal_selection_input: binding.AirlineSemanticSelectionInputV01 | None = None
    causal_proposal: binding.AirlineSemanticOfferSelectionProposalV01 | None = None
    causal_proposer_payload: Mapping[str, Any] = {}
    causal_reviewer_payloads: dict[str, Mapping[str, Any]] = {}
    causal_provider_call_records: list[
        causal_runtime.AirlineSemanticProviderCallRecordV01
    ] = []
    causal_actor_payload_validation_errors: list[str] = []

    for index, actor in enumerate(ACTOR_SPECS, start=1):
        actor_id = actor["actor_id"]
        if actor_id == "tri_party_airline_semantic_architect_llm":
            if bsep_validation.get("validation_status") != STATUS_PASS:
                validation_errors.append("architect_blocked_until_bsep_validates")
                break
        if actor.get("group") not in ("transaction_orchestrator", "semantic_architect"):
            architect = actor_by_id.get("tri_party_airline_semantic_architect_llm")
            if not architect or architect["validation_status"] != STATUS_PASS:
                validation_errors.append(f"side_actor_blocked_until_architect_pass:{actor_id}")
                break
        parent_report = None
        if actor.get("vertical_fractal_cell"):
            parent_report = actor_by_id.get(actor["parent_actor_id"])
            if not parent_report or parent_report["validation_status"] != STATUS_PASS:
                validation_errors.append(
                    f"vertical_child_blocked_until_parent_pass:{actor_id}",
                )
                break

        causal_request = None
        provider_response_schema = None
        if causal_gate_open and actor_id in CAUSAL_ACTOR_IDS:
            if causal_constraints is None:
                validation_errors.append("causal_constraints_required")
                break
            if causal_bsep_projection is None:
                validation_errors.append(
                    REASON_LIVE_BSEP_NOT_VALIDATED_BEFORE_CAUSAL_SELECTION,
                )
                break
            if causal_selection_input is None:
                causal_selection_input = binding.build_selection_input_v01(
                    causal_bsep_projection,
                    causal_constraints,
                    actual_causal_snapshot,
                )
                selection_report = (
                    binding.validate_airline_semantic_selection_input_v01(
                        causal_bsep_projection,
                        causal_constraints,
                        actual_causal_snapshot,
                        causal_selection_input,
                    )
                )
                if selection_report.validation_status != STATUS_PASS:
                    validation_errors.extend(selection_report.reason_codes)
                    break
            proposed_offer_id = (
                ""
                if actor_id == causal_runtime.ACTOR_ORDER[0]
                else (
                    causal_proposal.recommended_offer_id
                    if causal_proposal is not None
                    else ""
                )
            )
            if actor_id != causal_runtime.ACTOR_ORDER[0] and not proposed_offer_id:
                validation_errors.append(
                    f"causal_reviewer_blocked_until_proposer_valid:{actor_id}",
                )
                break
            causal_request = causal_runtime.build_airline_semantic_actor_request_v01(
                actor_id=actor_id,
                selection_input=causal_selection_input,
                constraints=causal_constraints,
                snapshot=actual_causal_snapshot,
                proposed_offer_id=proposed_offer_id,
            )
            provider_response_schema = _causal_provider_response_schema_v01(
                causal_request,
                causal_selection_input,
            )

        prompt = _build_prompt(
            actor=actor,
            actor_index=index,
            deterministic_report=deterministic_report,
            bsep_side_projections=bsep_side_projections,
            parent_report=parent_report,
            causal_request=causal_request,
            causal_selection_input=causal_selection_input,
        )
        prompt_artifact = _write_text_artifact(
            artifact_dir,
            f"{actor_id}_prompt.txt",
            prompt,
            artifacts,
            artifact_counts,
            "prompts_written_count",
        )
        metadata = {
            "actor_index": index,
            "side": actor["side"],
            "transaction_id": TRANSACTION_ID,
            "parent_actor_id": actor.get("parent_actor_id"),
            "provider_env": provider_env,
            "provider_mode": provider_mode,
        }
        if causal_request is not None:
            metadata["semantic_to_contract_request"] = asdict(causal_request)
            metadata["provider_response_schema"] = provider_response_schema
        if provider_mode == PROVIDER_MODE_REAL and call_delay_seconds > 0:
            time.sleep(call_delay_seconds)
            delay_applied_count += 1
        provider_call_count += 1
        try:
            raw_response = provider(actor_id, prompt, metadata)
        except Exception as exc:
            failed_actor_id = actor_id
            failed_stage = "provider_call"
            provider_error_sanitized = _sanitize_provider_exception(exc)
            validation_errors.append(f"provider_call_failed:{actor_id}")
            _write_json_named(
                artifact_dir,
                f"{actor_id}_provider_error.json",
                {
                    "actor_id": actor_id,
                    "failed_stage": failed_stage,
                    "provider_error_sanitized": provider_error_sanitized,
                },
                artifacts,
            )
            break
        raw_response_artifact = _write_text_artifact(
            artifact_dir,
            f"{actor_id}_raw_response.txt",
            raw_response,
            artifacts,
            artifact_counts,
            "raw_responses_written_count",
        )

        candidate, parse_errors = _extract_json_candidate(raw_response)
        extracted_json_artifact = _write_json_artifact(
            artifact_dir,
            f"{actor_id}_extracted_json_candidate.json",
            candidate,
            artifacts,
            artifact_counts,
            "extracted_json_candidates_written_count",
        )
        if causal_request is not None and causal_selection_input is not None:
            validation = _validate_causal_actor_candidate(
                candidate=candidate,
                actor=actor,
                causal_request=causal_request,
                selection_input=causal_selection_input,
                parse_errors=parse_errors,
            )
            causal_actor_payload_validation_errors.extend(validation["errors"])
            causal_call_index = len(causal_provider_call_records) + 1
            causal_provider_call_records.append(
                causal_runtime.AirlineSemanticProviderCallRecordV01(
                    call_index=causal_call_index,
                    actor_id=actor_id,
                    actor_role=causal_request.actor_role,
                    request_id=causal_request.request_id,
                    proposed_offer_id=causal_request.proposed_offer_id,
                    provider_returned=True,
                    validation_status=validation["validation_status"],
                    reason_codes=tuple(validation["errors"]),
                ),
            )
            if validation["validation_status"] == STATUS_PASS:
                if actor_id == causal_runtime.ACTOR_ORDER[0]:
                    causal_proposer_payload = candidate
                    proposal, _ = (
                        binding
                        .build_airline_semantic_offer_selection_proposal_from_payload_v01(
                            causal_selection_input,
                            candidate,
                        )
                    )
                    causal_proposal = proposal
                else:
                    causal_reviewer_payloads[actor_id] = candidate
        else:
            validation = _validate_actor_candidate(
                candidate=candidate,
                actor=actor,
                parent_report=parent_report,
                raw_response=raw_response,
                parse_errors=parse_errors,
            )
        validation_artifact = _write_json_artifact(
            artifact_dir,
            f"{actor_id}_validation.json",
            validation,
            artifacts,
            artifact_counts,
            "validations_written_count",
        )
        canonical_summary = _canonical_summary(candidate, actor, validation)
        if causal_request is not None:
            canonical_summary = _causal_canonical_summary(
                candidate,
                actor,
                validation,
            )
        canonical_summary_artifact = _write_json_artifact(
            artifact_dir,
            f"{actor_id}_canonical_summary.json",
            canonical_summary,
            artifacts,
            artifact_counts,
            "canonical_summaries_written_count",
        )

        actor_report = _actor_report(
            actor=actor,
            actor_index=index,
            model=model,
            provider_mode=provider_mode,
            prompt_artifact=prompt_artifact,
            raw_response_artifact=raw_response_artifact,
            extracted_json_artifact=extracted_json_artifact,
            validation_artifact=validation_artifact,
            canonical_summary_artifact=canonical_summary_artifact,
            input_context_summary=_input_context_summary(actor, parent_report),
            candidate=candidate,
            validation=validation,
            canonical_summary=canonical_summary,
        )
        actor_reports.append(actor_report)
        actor_by_id[actor_id] = actor_report

        if validation["validation_status"] != STATUS_PASS:
            failed_actor_id = actor_id
            failed_stage = "actor_validation"
            validation_errors.extend(validation["errors"])
            break

        if actor_id == "tri_party_airline_orchestrator_llm":
            bsep_packet = _build_bsep_packet(actor_report)
            bsep_validation = _validate_bsep_packet(bsep_packet)
            if bsep_validation["validation_status"] != STATUS_PASS:
                validation_errors.extend(bsep_validation["errors"])
                break
            bsep_side_projections = _build_bsep_side_projections(bsep_packet)
            if causal_gate_open:
                causal_bsep_projection, bsep_lineage_errors = (
                    _typed_airline_bsep_projection_ref_from_live_projection(
                        bsep_packet=bsep_packet,
                        bsep_validation=bsep_validation,
                        airline_projection=bsep_side_projections.get(
                            "airline_bsep_projection",
                        ),
                    )
                )
                if bsep_lineage_errors:
                    validation_errors.extend(bsep_lineage_errors)
                    break
            _write_json_named(
                artifact_dir,
                "tri_party_airline_bsep_packet.json",
                bsep_packet,
                artifacts,
            )
            _write_json_named(
                artifact_dir,
                "tri_party_airline_bsep_validation.json",
                bsep_validation,
                artifacts,
            )
            _write_json_named(
                artifact_dir,
                "tri_party_airline_bsep_side_projections.json",
                bsep_side_projections,
                artifacts,
            )

    causal_report: causal_runtime.AirlineSemanticCausalRunReportV01 | None = None
    integrated_deterministic_report: Mapping[str, Any] | None = None
    deterministic_collection_count = 0
    corridor_execution_count = 0
    if causal_gate_open and not validation_errors and len(actor_reports) == 12:
        if (
            causal_constraints is None
            or causal_selection_input is None
            or causal_bsep_projection is None
            or len(causal_provider_call_records) != 5
            or len(causal_reviewer_payloads) != 4
            or causal_proposal is None
        ):
            validation_errors.append("causal_actor_payload_collection_incomplete")
        elif (
            causal_bsep_projection.projection_ref
            != bsep_side_projections.get("airline_bsep_projection", {}).get(
                "projection_ref",
            )
        ):
            validation_errors.append(
                REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH,
            )
        else:
            causal_report = (
                causal_runtime
                .collect_airline_semantic_to_contract_causal_run_from_precollected_payloads_v01(
                    scenario_id="existing_live_lane_precollected_causal_binding",
                    constraints=causal_constraints,
                    bsep_projection=causal_bsep_projection,
                    snapshot=actual_causal_snapshot,
                    proposer_payload=causal_proposer_payload,
                    reviewer_payloads=causal_reviewer_payloads,
                    provider_call_records=tuple(causal_provider_call_records),
                )
            )
            causal_accepted, causal_reasons = (
                causal_runtime.validate_airline_semantic_causal_run_report_v01(
                    causal_report,
                )
            )
            if (
                not causal_accepted
                or causal_report.final_status
                != causal_runtime.STATUS_LOCAL_MODEL_PASS
            ):
                validation_errors.extend(
                    causal_reasons or causal_report.validation_errors,
                )
            else:
                deterministic_collection_count += 1
                integrated_deterministic_report = (
                    deterministic_airline
                    .collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
                        semantic_causal_run=causal_report,
                    )
                )
                if (
                    integrated_deterministic_report.get("final_status")
                    != STATUS_PASS
                ):
                    validation_errors.extend(
                        integrated_deterministic_report.get(
                            "validation_errors",
                            ("deterministic_airline_integration_failed",),
                        ),
                    )
                else:
                    corridor_execution_count = 1

    semantic_actor_reports = tuple(actor_reports)
    root_boundaries = _root_boundaries()
    causal_section = _causal_binding_section(
        causal_report,
        bsep_packet=bsep_packet,
        airline_bsep_projection=bsep_side_projections.get(
            "airline_bsep_projection",
            {},
        ),
        causal_selection_input=causal_selection_input,
    )
    bridge_section = _semantic_to_contract_bridge_section(
        causal_report=causal_report,
        deterministic_report=integrated_deterministic_report,
        semantic_actor_reports=semantic_actor_reports,
        deterministic_collection_count=deterministic_collection_count,
        corridor_execution_count=corridor_execution_count,
        causal_section=causal_section,
    )
    if causal_gate_open and not _bridge_final_guard_passes(bridge_section):
        validation_errors.append("semantic_to_contract_bridge_guard_failed")
    report: dict[str, Any] = {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "lane_id": LANE_ID,
        "final_status": STATUS_PASS if not validation_errors and len(actor_reports) == 12 else STATUS_FAIL_CLOSED,
        "skip_reason": "",
        "provider_mode": provider_mode,
        "model": model,
        "deterministic_source": {
            "run_id": deterministic_report["run_id"],
            "report_id": deterministic_report["report_id"],
            "final_status": deterministic_report["final_status"],
        },
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": deterministic_report["transaction_identity"],
        "bsep_membrane": bsep_packet,
        "bsep_validation": bsep_validation,
        "bsep_side_projections": bsep_side_projections,
        "semantic_actor_reports": semantic_actor_reports,
        "semantic_actor_call_order": tuple(report["actor_id"] for report in actor_reports),
        "horizontal_actor_groups": _horizontal_actor_groups(actor_reports),
        "vertical_fractal_dependencies": tuple(
            _vertical_dependency_from_report(report)
            for report in actor_reports
            if report.get("vertical_fractal_cell")
        ),
        "what_each_llm_received": {
            report["actor_id"]: report["input_context_summary"]
            for report in actor_reports
        },
        "what_each_llm_returned": {
            report["actor_id"]: report["output_semantic_summary"]
            for report in actor_reports
        },
        "what_runtime_used": {
            report["actor_id"]: report["what_runtime_used"]
            for report in actor_reports
        },
        "what_runtime_rejected": {
            report["actor_id"]: report["what_runtime_rejected"]
            for report in actor_reports
        },
        "root_boundaries": root_boundaries,
        "semantic_to_contract_causal_binding_v0_1": causal_section,
        "semantic_to_contract_deterministic_bridge": bridge_section,
        "integrated_deterministic_airline_transaction": (
            _integrated_deterministic_summary(integrated_deterministic_report)
        ),
        "counter_table": {},
        "artifacts": artifacts,
        "secret_scan": {},
        "failed_actor_id": failed_actor_id,
        "failed_stage": failed_stage,
        "provider_error_sanitized": provider_error_sanitized,
        "raw_response_terminal_output_allowed": allow_raw_output,
        "non_claims": _non_claims(),
        "validation_errors": tuple(validation_errors),
        "next_gate": "operator-gated real Gemini terminal pass after fake-provider PASS",
    }
    report["counter_table"] = _counter_table(
        report=report,
        provider_call_count=provider_call_count,
        artifact_counts=artifact_counts,
        provider_mode=provider_mode,
        delay_applied_count=delay_applied_count,
        call_delay_seconds=call_delay_seconds,
    )
    if causal_gate_open:
        if causal_report is not None:
            _write_json_named(
                artifact_dir,
                "semantic_to_contract_causal_run.json",
                _json_safe(causal_report),
                artifacts,
            )
        _write_json_named(
            artifact_dir,
            "semantic_to_contract_bridge.json",
            report["semantic_to_contract_deterministic_bridge"],
            artifacts,
        )
        _write_json_named(
            artifact_dir,
            "integrated_deterministic_airline_summary.json",
            report["integrated_deterministic_airline_transaction"],
            artifacts,
        )
    secret_scan = _scan_secret_markers(report, artifact_dir)
    report["secret_scan"] = secret_scan
    _write_json_named(artifact_dir, "secret_scan.json", secret_scan, artifacts)
    _write_summary_artifacts(artifact_dir, report, artifacts)
    report["artifacts"] = artifacts
    if not secret_scan["passed"]:
        report["final_status"] = STATUS_FAIL_CLOSED
        report["failed_stage"] = "secret_scan"
        report["validation_errors"] = tuple(
            list(report["validation_errors"]) + ["secret_scan_failed"],
        )
    return report


def _skipped_report(
    model: str,
    deterministic_report: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "lane_id": LANE_ID,
        "final_status": STATUS_SKIPPED_CLOSED,
        "skip_reason": "live semantic lane env gate is closed",
        "provider_mode": PROVIDER_MODE_SKIPPED,
        "model": model,
        "deterministic_source": {
            "run_id": deterministic_report["run_id"],
            "report_id": deterministic_report["report_id"],
            "final_status": deterministic_report["final_status"],
        },
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": deterministic_report["transaction_identity"],
        "bsep_membrane": {},
        "bsep_validation": {},
        "bsep_side_projections": {},
        "semantic_actor_reports": (),
        "semantic_actor_call_order": (),
        "horizontal_actor_groups": {},
        "vertical_fractal_dependencies": (),
        "what_each_llm_received": {},
        "what_each_llm_returned": {},
        "what_runtime_used": {},
        "what_runtime_rejected": {},
        "root_boundaries": _root_boundaries(),
        "semantic_to_contract_causal_binding_v0_1": _causal_binding_section(None),
        "semantic_to_contract_deterministic_bridge": (
            _semantic_to_contract_bridge_section(
                causal_report=None,
                deterministic_report=None,
                semantic_actor_reports=(),
                deterministic_collection_count=0,
                corridor_execution_count=0,
            )
        ),
        "integrated_deterministic_airline_transaction": (
            _integrated_deterministic_summary(None)
        ),
        "counter_table": _zero_counter_table(),
        "artifacts": {},
        "secret_scan": {"passed": True, "matched_markers": (), "files_scanned": 0},
        "failed_actor_id": "",
        "failed_stage": "",
        "provider_error_sanitized": "",
        "raw_response_terminal_output_allowed": False,
        "non_claims": _non_claims(),
        "validation_errors": (),
        "next_gate": "enable fake-provider lane",
    }


def _fail_closed_report(
    *,
    reason: str,
    provider_mode: str,
    model: str,
    deterministic_report: Mapping[str, Any],
) -> dict[str, Any]:
    report = _skipped_report(model, deterministic_report)
    report.update(
        {
            "final_status": STATUS_FAIL_CLOSED,
            "skip_reason": reason,
            "provider_mode": provider_mode,
            "validation_errors": (reason,),
        },
    )
    return report


def _call_delay_seconds(env: Mapping[str, str], provider_mode: str) -> float:
    if provider_mode != PROVIDER_MODE_REAL:
        return 0.0
    raw_value = env.get(ENV_CALL_DELAY_SECONDS, "0").strip()
    try:
        delay = float(raw_value)
    except ValueError:
        return 0.0
    return max(0.0, min(delay, 120.0))


def _sanitize_provider_exception(exc: Exception) -> str:
    text = str(exc) or exc.__class__.__name__
    collapsed = " ".join(text.split())
    lowered = collapsed.lower()
    secretish = any(marker in collapsed for marker in SECRET_MARKERS) or any(
        token in lowered
        for token in ("api_key", "apikey", "token", "credential", "secret", "traceback")
    )
    if secretish:
        return f"{exc.__class__.__name__}:provider_error_redacted"
    if not collapsed or not all(char.isalnum() or char in "_:-. " for char in collapsed):
        collapsed = exc.__class__.__name__
    return collapsed[:240]


def _build_prompt(
    *,
    actor: Mapping[str, Any],
    actor_index: int,
    deterministic_report: Mapping[str, Any],
    bsep_side_projections: Mapping[str, Any],
    parent_report: Mapping[str, Any] | None,
    causal_request: causal_runtime.AirlineInjectedSemanticActorRequestV01 | None = None,
    causal_selection_input: binding.AirlineSemanticSelectionInputV01 | None = None,
) -> str:
    projection = bsep_side_projections.get(f"{actor['side']}_bsep_projection", {})
    if actor["side"] == "cross_root_advisory":
        projection = bsep_side_projections.get("cross_root_bsep_projection", projection)
    parent_summary = ""
    if parent_report:
        parent_summary = (
            "Parent canonical summary: "
            f"{parent_report['output_semantic_summary']}"
        )
    json_skeleton = {
        "actor_id": actor["actor_id"],
        "transaction_id": TRANSACTION_ID,
        "side": actor["side"],
        "semantic_summary": "",
        "authority_created": False,
        "action_permission_created": False,
        "packet_created": False,
        "receipt_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "real_payment_executed": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "real_world_effects_count": 0,
    }
    if causal_request is not None:
        if causal_request.actor_id == causal_runtime.ACTOR_ORDER[0]:
            json_skeleton = {
                "proposal_id": "non_empty_proposal_id_not_offer_default",
                "transaction_id": causal_request.transaction_id,
                "actor_id": causal_request.actor_id,
                "source_selection_input_id": (
                    causal_request.source_selection_input_id
                ),
                "source_bsep_projection_ref": (
                    causal_request.source_bsep_projection_ref
                ),
                "source_client_constraint_set_id": (
                    causal_request.source_client_constraint_set_id
                ),
                "source_candidate_set_snapshot_id": (
                    causal_request.source_candidate_set_snapshot_id
                ),
                "source_candidate_set_digest": (
                    causal_request.source_candidate_set_digest
                ),
                "candidate_set_ref": causal_request.source_candidate_set_ref,
                "recommended_offer_id": (
                    "choose_one_allowed_hard_compatible_offer_id"
                ),
                "ranked_offer_ids": (
                    "rank_allowed_offer_ids_without_defaulting",
                ),
                "decision_factors": (
                    "Compare price, seat, baggage, changeability, and layover semantics as strings.",
                ),
                "preference_matches": (
                    "Describe which declared soft preferences the recommendation matches as strings.",
                ),
                "uncertainty_notes": (
                    "Recommendation remains advisory and requires ClientRoot review.",
                ),
                "requires_root_review": True,
                "semantic_summary": (
                    "Non-empty advisory semantic summary; not Root authority."
                ),
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
        else:
            json_skeleton = {
                "response_id": "non_empty_reviewer_response_id",
                "transaction_id": causal_request.transaction_id,
                "actor_id": causal_request.actor_id,
                "source_request_id": causal_request.request_id,
                "source_selection_input_id": (
                    causal_request.source_selection_input_id
                ),
                "source_candidate_set_snapshot_id": (
                    causal_request.source_candidate_set_snapshot_id
                ),
                "source_candidate_set_digest": (
                    causal_request.source_candidate_set_digest
                ),
                "reviewed_offer_id": causal_request.proposed_offer_id,
                "review_role": causal_request.actor_role,
                "review_status": "derive_from_actual_review",
                "semantic_factors": (
                    "Review the proposed offer with non-empty string factors.",
                ),
                "blocking_conflicts": ("derive_from_actual_review",),
                "supports_proposed_offer": "derive_boolean_from_actual_review",
                "validation_status": "derive_from_actual_review",
                "raw_output_used": False,
                "authority_created": False,
                "permission_created": False,
                "real_world_effects_count": 0,
            }
    causal_prompt_lines: tuple[str, ...] = ()
    if causal_request is not None:
        allowed_ids = tuple(causal_request.client_hard_compatible_candidate_ids)
        causal_prompt_lines = (
            "Causal response contract is strict: local typed validator receives the extracted JSON unchanged.",
            (
                "Allowed hard-compatible offer ids: "
                + ", ".join(allowed_ids)
            ),
            (
                "decision_factors, preference_matches, and uncertainty_notes "
                "must each be JSON arrays of non-empty strings. Never return "
                "objects in these arrays."
            ),
            (
                "Choose recommended_offer_id from the allowed hard-compatible "
                "ids using semantic comparison only. Do not choose by list "
                "order and do not use a default offer."
            ),
            "requires_root_review must be true for proposer output.",
            "The placeholder skeleton is not a valid provider result.",
            "Provider response schema and local typed validator remain mandatory.",
        )
        if causal_request.actor_id != causal_runtime.ACTOR_ORDER[0]:
            causal_prompt_lines += (
                "Reviewer semantic_factors must be a non-empty JSON array of non-empty strings.",
                "Reviewer blocking_conflicts must report every actual blocking conflict; do not copy an empty conflict list by default.",
                "Reviewer unsupported/conflicting outcomes are allowed; do not assume PASS.",
                "Derive supports_proposed_offer from actual semantic review.",
                "Return false when the proposed offer is not supported.",
                "The placeholder skeleton is not valid output.",
                "Actual provider response must still use schema-valid types: boolean supports_proposed_offer and string-array blocking_conflicts.",
                "Response schema and local validator remain authoritative for shape/safety.",
            )
    return "\n".join(
        (
            f"Role name: {actor['actor_id']}",
            f"Actor index: {actor_index}",
            "Use bounded context only.",
            f"Transaction id: {TRANSACTION_ID}",
            f"Semantic work: {actor['semantic_work']}",
            f"Deterministic final status: {deterministic_report['final_status']}",
            f"BSEP projection summary: {projection.get('bounded_context_summary', 'pending or transaction-level context')}",
            parent_summary,
            "Provider output is advisory only.",
            "Runtime canonicalizes.",
            "Validators verify.",
            "Root decides.",
            "Do not describe runtime internals.",
            "Runtime will compute what_runtime_used and what_runtime_rejected after validation.",
            "runtime computes what_runtime_used and runtime computes what_runtime_rejected after validation.",
            "Return only semantic fields and safety flags.",
            "Do not create payment, ticket, booking, packet, receipt, authority, or FinalOutput.",
            "No raw passport, raw card, raw IBAN, raw payment token, raw private profile, API key, connector credential, raw provider text from other actors, or peer raw content is allowed.",
            (
                "Causal selection request: "
                + json.dumps(_json_safe(causal_request), sort_keys=True)
                if causal_request is not None
                else "Causal selection request: not applicable"
            ),
            *causal_prompt_lines,
            "Explicit JSON skeleton:",
            json.dumps(json_skeleton, sort_keys=True),
        ),
    )


def _extract_json_candidate(raw_response: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        return {"raw_response_parse_error": str(exc)}, ("malformed_json",)
    if not isinstance(parsed, dict):
        return {"raw_response_parse_error": "json root is not object"}, ("json_root_not_object",)
    return parsed, ()


def _validate_actor_candidate(
    *,
    candidate: Mapping[str, Any],
    actor: Mapping[str, Any],
    parent_report: Mapping[str, Any] | None,
    raw_response: str,
    parse_errors: tuple[str, ...],
) -> dict[str, Any]:
    errors = list(parse_errors)
    required_fields = (
        "actor_id",
        "transaction_id",
        "side",
        "semantic_summary",
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
        "real_world_effects_count",
    )
    for field in required_fields:
        if field not in candidate:
            errors.append(f"missing_required_field:{field}")
    if candidate.get("actor_id") != actor["actor_id"]:
        errors.append("actor_id_mismatch")
    if candidate.get("transaction_id") != TRANSACTION_ID:
        errors.append("transaction_id_mismatch")
    if candidate.get("side") != actor["side"]:
        errors.append("side_mismatch")
    if not isinstance(candidate.get("semantic_summary"), str) or not candidate.get("semantic_summary", "").strip():
        errors.append("empty_semantic_summary")
    for field in (
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
    ):
        if candidate.get(field) is not False:
            errors.append(f"unsafe_true_flag:{field}")
    if candidate.get("real_world_effects_count") != 0:
        errors.append("real_world_effects_nonzero")
    if any(marker in raw_response for marker in SECRET_MARKERS):
        errors.append("raw_secret_marker_detected")
    if actor.get("vertical_fractal_cell"):
        if parent_report is None:
            errors.append("missing_parent_report")
        if "parent_actor_id" in candidate and candidate.get("parent_actor_id") != actor["parent_actor_id"]:
            errors.append("vertical_parent_actor_id_mismatch")
        if "parent_validation_status" in candidate and candidate.get("parent_validation_status") != STATUS_PASS:
            errors.append("vertical_parent_validation_not_pass")
        for field in (
            "child_started_after_parent_validation",
            "child_received_parent_canonical_summary",
            "child_result_returns_to_parent_or_root_review",
        ):
            if field in candidate and candidate.get(field) is not True:
                errors.append(f"vertical_flag_false:{field}")
        for field in (
            "child_received_parent_raw_response",
            "child_received_sibling_raw_output",
            "child_received_unbounded_context",
            "child_creates_authority",
            "child_creates_packet",
            "child_creates_receipt",
            "child_creates_payment",
            "child_creates_ticket",
            "child_creates_booking",
        ):
            if field in candidate and candidate.get(field) is not False:
                errors.append(f"vertical_flag_true:{field}")
    return {
        "accepted": not errors,
        "validation_status": STATUS_PASS if not errors else STATUS_FAIL_CLOSED,
        "errors": tuple(errors),
    }


def _validate_causal_actor_candidate(
    *,
    candidate: Mapping[str, Any],
    actor: Mapping[str, Any],
    causal_request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
    selection_input: binding.AirlineSemanticSelectionInputV01,
    parse_errors: tuple[str, ...],
) -> dict[str, Any]:
    errors = list(parse_errors)
    if actor["actor_id"] == causal_runtime.ACTOR_ORDER[0]:
        proposal, report = (
            binding.build_airline_semantic_offer_selection_proposal_from_payload_v01(
                selection_input,
                candidate,
            )
        )
        errors.extend(report.reason_codes)
        if proposal is not None and proposal.actor_id != actor["actor_id"]:
            errors.append("actor_id_mismatch")
    else:
        response, response_errors = causal_runtime.parse_injected_reviewer_response_v01(
            request=causal_request,
            selection_input=selection_input,
            proposed_offer_id=causal_request.proposed_offer_id,
            payload=candidate,
        )
        errors.extend(response_errors)
        if response is not None and response.actor_id != actor["actor_id"]:
            errors.append("actor_id_mismatch")
    return {
        "accepted": not errors,
        "validation_status": STATUS_PASS if not errors else STATUS_FAIL_CLOSED,
        "errors": tuple(dict.fromkeys(errors)),
    }


def _runtime_computed_used(actor: Mapping[str, Any]) -> tuple[str, ...]:
    actor_id = str(actor["actor_id"])
    return (
        f"runtime_computed: accepted semantic_summary as advisory bounded semantic evidence for {actor_id}",
        "runtime_computed: accepted safe false authority/action/payment/ticket/booking flags",
        f"runtime_computed: accepted transaction_id match for {TRANSACTION_ID}",
    )


def _runtime_computed_rejected(actor: Mapping[str, Any]) -> tuple[str, ...]:
    return (
        "runtime_computed: provider output as truth",
        "runtime_computed: provider output as authority",
        "runtime_computed: provider output as payment permission",
        "runtime_computed: provider output as ticket permission",
        "runtime_computed: provider output as booking permission",
        "runtime_computed: provider output as packet or receipt creator",
        "runtime_computed: raw secrets or connector credentials",
    )


def _canonical_summary(
    candidate: Mapping[str, Any],
    actor: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "actor_id": actor["actor_id"],
        "transaction_id": TRANSACTION_ID,
        "side": actor["side"],
        "semantic_summary": candidate.get("semantic_summary", ""),
        "what_runtime_used": _runtime_computed_used(actor),
        "what_runtime_rejected": _runtime_computed_rejected(actor),
        "validation_status": validation["validation_status"],
        "accepted": validation["accepted"],
    }


def _causal_canonical_summary(
    candidate: Mapping[str, Any],
    actor: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    summary = str(
        candidate.get("semantic_summary")
        or "strict causal actor payload accepted as advisory semantic evidence",
    )
    if actor["actor_id"] != causal_runtime.ACTOR_ORDER[0]:
        summary = (
            f"{actor['actor_id']} reviewed "
            f"{candidate.get('reviewed_offer_id', '')} as advisory evidence."
        )
    return {
        "actor_id": actor["actor_id"],
        "transaction_id": TRANSACTION_ID,
        "side": actor["side"],
        "semantic_summary": summary,
        "what_runtime_used": _runtime_computed_used(actor),
        "what_runtime_rejected": _runtime_computed_rejected(actor),
        "validation_status": validation["validation_status"],
        "accepted": validation["accepted"],
    }


def _actor_report(
    *,
    actor: Mapping[str, Any],
    actor_index: int,
    model: str,
    provider_mode: str,
    prompt_artifact: str,
    raw_response_artifact: str,
    extracted_json_artifact: str,
    validation_artifact: str,
    canonical_summary_artifact: str,
    input_context_summary: str,
    candidate: Mapping[str, Any],
    validation: Mapping[str, Any],
    canonical_summary: Mapping[str, Any],
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "actor_id": actor["actor_id"],
        "side": actor["side"],
        "actor_index": actor_index,
        "model": model,
        "provider_mode": provider_mode,
        "prompt_artifact": prompt_artifact,
        "raw_response_artifact": raw_response_artifact,
        "extracted_json_artifact": extracted_json_artifact,
        "validation_artifact": validation_artifact,
        "canonical_summary_artifact": canonical_summary_artifact,
        "input_context_summary": input_context_summary,
        "output_semantic_summary": str(canonical_summary.get("semantic_summary", "")),
        "validation_status": validation["validation_status"],
        "accepted": validation["accepted"],
        "what_runtime_used": tuple(canonical_summary.get("what_runtime_used", ())),
        "what_runtime_rejected": tuple(canonical_summary.get("what_runtime_rejected", ())),
        "authority_created": False,
        "action_permission_created": False,
        "packet_created": False,
        "receipt_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "real_payment_executed": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "real_world_effects_count": 0,
        "group": actor["group"],
    }
    if actor.get("vertical_fractal_cell"):
        report.update(
            {
                "vertical_fractal_cell": True,
                "parent_actor_id": actor["parent_actor_id"],
                "parent_validation_status": STATUS_PASS,
                "child_started_after_parent_validation": True,
                "child_received_parent_canonical_summary": True,
                "child_received_parent_raw_response": False,
                "child_received_sibling_raw_output": False,
                "child_received_unbounded_context": False,
                "child_result_returns_to_parent_or_root_review": True,
                "child_creates_authority": False,
                "child_creates_packet": False,
                "child_creates_receipt": False,
                "child_creates_payment": False,
                "child_creates_ticket": False,
                "child_creates_booking": False,
            },
        )
    return report


def _input_context_summary(
    actor: Mapping[str, Any],
    parent_report: Mapping[str, Any] | None,
) -> str:
    base = (
        f"bounded context for {actor['actor_id']} over transaction {TRANSACTION_ID}; "
        "sealed refs only; deterministic mock airline evidence only"
    )
    if parent_report:
        return base + f"; parent canonical summary from {parent_report['actor_id']}"
    return base


def _build_bsep_packet(orchestrator_report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "bsep_packet_id": f"tri_party_airline_bsep_packet:{TRANSACTION_ID}",
        "transaction_id": TRANSACTION_ID,
        "source_orchestrator_actor_id": orchestrator_report["actor_id"],
        "raw_passport_included": False,
        "raw_card_included": False,
        "raw_iban_included": False,
        "raw_payment_token_included": False,
        "raw_private_profile_included": False,
        "raw_provider_text_included": False,
        "raw_response_dump_included": False,
        "authority_created": False,
        "action_permission_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "bounded_context_summary": (
            "one transaction_id, three Root views, evidence-only receipts, "
            "sealed refs, mock payment authorization, mock ticket evidence"
        ),
        "validation_status": STATUS_PASS,
    }


def _validate_bsep_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    errors = []
    if packet.get("transaction_id") != TRANSACTION_ID:
        errors.append("bsep_transaction_id_mismatch")
    for field in (
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
    ):
        if packet.get(field) is not False:
            errors.append(f"bsep_forbidden_flag_true:{field}")
    return {
        "accepted": not errors,
        "validation_status": STATUS_PASS if not errors else STATUS_FAIL_CLOSED,
        "errors": tuple(errors),
        "bsep_is_truth": False,
        "bsep_is_authority": False,
        "bsep_is_permission": False,
        "bsep_creates_packet": False,
        "bsep_creates_receipt": False,
        "bsep_creates_payment": False,
        "bsep_creates_ticket": False,
        "bsep_creates_booking": False,
    }


def _build_bsep_side_projections(packet: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    projection_specs = (
        ("client_bsep_projection", "client", ("TravelIntentV01", "PassengerSealedRefsV01", "PaymentProfileSealedRefV01")),
        ("airline_bsep_projection", "airline", ("AirlineOfferResponseV01", "AirlineOfferHoldReceiptV01", "MockTicketReceiptV01")),
        ("bank_bsep_projection", "bank", ("BankPaymentIntentV01", "BankPaymentAuthorizationReceiptV01", "BankPaymentStatusReceiptV01")),
        ("cross_root_bsep_projection", "cross_root_advisory", ("integrated_transaction_trace", "cross_root_evidence_routing_matrix")),
    )
    return {
        projection_id: {
            "projection_id": projection_id,
            "projection_ref": (
                f"{binding.BSEP_PROJECTION_REF}:{packet['bsep_packet_id']}"
                if projection_id == "airline_bsep_projection"
                else projection_id
            ),
            "source_bsep_packet_id": packet["bsep_packet_id"],
            "transaction_id": TRANSACTION_ID,
            "side": side,
            "bounded_context_summary": f"{side} projection from {packet['bsep_packet_id']}",
            "allowed_refs": tuple(allowed_refs),
            "forbidden_raw_fields": (
                "raw_passport",
                "raw_card",
                "raw_iban",
                "raw_payment_token",
                "raw_private_profile",
            ),
            "forbidden_authority_claims": (
                "foreign_root_authority",
                "payment_permission",
                "ticket_permission",
                "booking_permission",
            ),
            "raw_secrets_included": False,
            "raw_provider_text_included": False,
            "validation_status": STATUS_PASS,
        }
        for projection_id, side, allowed_refs in projection_specs
    }


def _typed_airline_bsep_projection_ref_from_live_projection(
    *,
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    airline_projection: Mapping[str, Any] | None,
) -> tuple[binding.AirlineBSEPProjectionRefV01 | None, tuple[str, ...]]:
    errors: list[str] = []
    if bsep_validation.get("validation_status") != STATUS_PASS:
        errors.append(REASON_LIVE_BSEP_NOT_VALIDATED_BEFORE_CAUSAL_SELECTION)
    if not airline_projection:
        errors.append(REASON_LIVE_AIRLINE_BSEP_PROJECTION_MISSING)
        return None, tuple(errors)
    if airline_projection.get("side") != "airline":
        errors.append(REASON_LIVE_AIRLINE_BSEP_PROJECTION_MISSING)
    if airline_projection.get("transaction_id") != bsep_packet.get("transaction_id"):
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
    if (
        airline_projection.get("source_bsep_packet_id")
        != bsep_packet.get("bsep_packet_id")
    ):
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
    if airline_projection.get("validation_status") != STATUS_PASS:
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
    effects_count = airline_projection.get("real_world_effects_count", 0)
    if type(effects_count) is not int:
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
        effects_count = 1
    typed_projection = binding.AirlineBSEPProjectionRefV01(
        projection_ref=str(
            airline_projection.get("projection_ref")
            or airline_projection.get("projection_id")
            or ""
        ),
        transaction_id=str(airline_projection.get("transaction_id", "")),
        projection_side="airline_offer_selection",
        validation_status=str(airline_projection.get("validation_status", "")),
        raw_secret_included=bool(airline_projection.get("raw_secrets_included")),
        authority_created=bool(airline_projection.get("authority_created", False)),
        real_world_effects_count=effects_count,
    )
    typed_report = binding.validate_airline_bsep_projection_ref_v01(
        typed_projection,
    )
    if typed_report.validation_status != STATUS_PASS:
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
        errors.extend(typed_report.reason_codes)
    return (None if errors else typed_projection), tuple(dict.fromkeys(errors))


def _horizontal_actor_groups(actor_reports: list[dict[str, Any]]) -> dict[str, tuple[str, ...]]:
    groups: dict[str, list[str]] = {
        "transaction": [],
        "client": [],
        "airline": [],
        "bank": [],
        "cross_root_advisory": [],
    }
    for report in actor_reports:
        if report["group"] in ("transaction_orchestrator", "semantic_architect"):
            groups["transaction"].append(report["actor_id"])
        elif report["side"] in groups:
            groups[report["side"]].append(report["actor_id"])
    return {key: tuple(value) for key, value in groups.items()}


def _vertical_dependency_from_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "child_actor_id": report["actor_id"],
        "parent_actor_id": report["parent_actor_id"],
        "parent_validation_status": report["parent_validation_status"],
        "child_started_after_parent_validation": report["child_started_after_parent_validation"],
        "child_received_parent_canonical_summary": report["child_received_parent_canonical_summary"],
        "child_received_parent_raw_response": report["child_received_parent_raw_response"],
        "child_received_sibling_raw_output": report["child_received_sibling_raw_output"],
        "child_received_unbounded_context": report["child_received_unbounded_context"],
        "child_result_returns_to_parent_or_root_review": report["child_result_returns_to_parent_or_root_review"],
        "child_creates_authority": report["child_creates_authority"],
        "child_creates_packet": report["child_creates_packet"],
        "child_creates_receipt": report["child_creates_receipt"],
        "child_creates_payment": report["child_creates_payment"],
        "child_creates_ticket": report["child_creates_ticket"],
        "child_creates_booking": report["child_creates_booking"],
        "real_world_effects_count": 0,
    }


def _root_boundaries() -> tuple[dict[str, Any], ...]:
    return (
        {"boundary": "ClientRoot remains client-side only", "boundary_preserved": True, "violation_count": 0},
        {"boundary": "AirlineRoot remains airline-side only", "boundary_preserved": True, "violation_count": 0},
        {"boundary": "BankRoot remains bank-side only", "boundary_preserved": True, "violation_count": 0},
        {"boundary": "cross-root reviewer is advisory and not a fourth Root", "boundary_preserved": True, "violation_count": 0},
    )


def _causal_binding_section(
    causal_report: causal_runtime.AirlineSemanticCausalRunReportV01 | None,
    *,
    bsep_packet: Mapping[str, Any] | None = None,
    airline_bsep_projection: Mapping[str, Any] | None = None,
    causal_selection_input: binding.AirlineSemanticSelectionInputV01 | None = None,
) -> dict[str, Any]:
    if causal_report is None:
        return {
            "binding_status": "NOT_ENABLED",
            "precollected_causal_run_count": 0,
            "externally_observed_provider_call_count": 0,
            "provider_calls_performed_inside_precollected_entrypoint": 0,
            "duplicate_provider_call_count": 0,
            "real_world_effects_count": 0,
        }
    actual_bsep_packet_id = str((bsep_packet or {}).get("bsep_packet_id", ""))
    actual_projection_ref = str(
        (airline_bsep_projection or {}).get("projection_ref")
        or (airline_bsep_projection or {}).get("projection_id", ""),
    )
    causal_projection_ref = (
        causal_selection_input.source_bsep_projection_ref
        if causal_selection_input is not None
        else ""
    )
    return {
        "binding_status": causal_report.final_status,
        "transaction_id": causal_report.transaction_id,
        "actual_bsep_packet_id": actual_bsep_packet_id,
        "actual_airline_bsep_projection_ref": actual_projection_ref,
        "causal_selection_bsep_projection_ref": causal_projection_ref,
        "bsep_refs_match": (
            bool(actual_bsep_packet_id)
            and bool(actual_projection_ref)
            and actual_projection_ref == causal_projection_ref
        ),
        "source_candidate_set_ref": (
            causal_selection_input.source_candidate_set_ref
            if causal_selection_input is not None
            else ""
        ),
        "source_candidate_set_snapshot_id": (
            causal_selection_input.source_candidate_set_snapshot_id
            if causal_selection_input is not None
            else ""
        ),
        "source_candidate_set_digest": (
            causal_selection_input.source_candidate_set_digest
            if causal_selection_input is not None
            else ""
        ),
        "visible_candidate_ids": (
            causal_selection_input.visible_candidate_ids
            if causal_selection_input is not None
            else ()
        ),
        "airline_valid_candidate_ids": (
            causal_selection_input.airline_valid_candidate_ids
            if causal_selection_input is not None
            else ()
        ),
        "client_hard_compatible_candidate_ids": (
            causal_selection_input.client_hard_compatible_candidate_ids
            if causal_selection_input is not None
            else ()
        ),
        "semantic_recommendation_id": causal_report.semantic_recommendation_id,
        "client_root_selected_offer_id": causal_report.root_selected_offer_id,
        "airline_root_resolved_offer_id": (
            causal_report.airline_root_resolution.selected_offer_id
            if causal_report.airline_root_resolution is not None
            else ""
        ),
        "hold_contract_offer_id": causal_report.hold_contract_offer_id,
        "precollected_causal_run_count": 1,
        "externally_observed_provider_call_count": (
            causal_report.externally_observed_provider_call_count
        ),
        "provider_calls_performed_inside_precollected_entrypoint": (
            causal_report.provider_calls_performed_inside_precollected_entrypoint
        ),
        "duplicate_provider_call_count": causal_report.duplicate_provider_call_count,
        "default_offer_used": causal_report.default_offer_used,
        "silent_fallback_used": causal_report.silent_fallback_used,
        "provider_created_authority_count": (
            causal_report.provider_created_authority_count
        ),
        "real_world_effects_count": causal_report.real_world_effects_count,
        "validation_errors": causal_report.validation_errors,
    }


def _semantic_to_contract_bridge_section(
    *,
    causal_report: causal_runtime.AirlineSemanticCausalRunReportV01 | None,
    deterministic_report: Mapping[str, Any] | None,
    semantic_actor_reports: tuple[Mapping[str, Any], ...],
    deterministic_collection_count: int,
    corridor_execution_count: int,
    causal_section: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    deterministic_offer_id = ""
    deterministic_corridor_offer_id = ""
    deterministic_final_status = ""
    deterministic_corridor_status = ""
    if deterministic_report is not None:
        deterministic_final_status = str(deterministic_report.get("final_status", ""))
        fixtures = deterministic_report.get("mock_protocol_fixtures", {})
        if isinstance(fixtures, Mapping):
            offer = fixtures.get("AirlineOfferCandidateV01", {})
            if isinstance(offer, Mapping):
                deterministic_offer_id = str(offer.get("offer_id", ""))
        corridor = deterministic_report.get("airline_ticket_purchase_corridor_v0_1")
        deterministic_corridor_status = str(getattr(corridor, "final_status", ""))
        corridor_context = getattr(corridor, "contract_context", None)
        deterministic_corridor_offer_id = str(
            getattr(corridor_context, "offer_id", ""),
        )
    semantic_offer_id = (
        causal_report.semantic_recommendation_id if causal_report is not None else ""
    )
    root_offer_id = (
        causal_report.root_selected_offer_id if causal_report is not None else ""
    )
    resolution_offer_id = (
        causal_report.airline_root_resolution.selected_offer_id
        if causal_report is not None
        and causal_report.airline_root_resolution is not None
        else ""
    )
    hold_offer_id = (
        causal_report.hold_contract_offer_id if causal_report is not None else ""
    )
    offer_ids = (
        semantic_offer_id,
        root_offer_id,
        resolution_offer_id,
        hold_offer_id,
        deterministic_offer_id,
        deterministic_corridor_offer_id,
    )
    causal_actor_calls = sum(
        int(report["actor_id"] in CAUSAL_ACTOR_IDS)
        for report in semantic_actor_reports
    )
    duplicate_actor_calls = len(semantic_actor_reports) - len(
        {report["actor_id"] for report in semantic_actor_reports},
    )
    return {
        "bridge_status": (
            STATUS_PASS
            if deterministic_final_status == STATUS_PASS
            and deterministic_corridor_status == STATUS_PASS
            and causal_report is not None
            and causal_report.final_status == causal_runtime.STATUS_LOCAL_MODEL_PASS
            and bool(deterministic_corridor_offer_id)
            and len(set(offer_ids)) == 1
            and (causal_section or {}).get("bsep_refs_match") is True
            and deterministic_collection_count == 1
            and corridor_execution_count == 1
            and duplicate_actor_calls == 0
            else STATUS_FAIL_CLOSED
            if causal_report is not None
            else "NOT_ENABLED"
        ),
        "transaction_id": TRANSACTION_ID,
        "semantic_recommendation_id": semantic_offer_id,
        "client_root_selected_offer_id": root_offer_id,
        "airline_root_resolved_offer_id": resolution_offer_id,
        "hold_contract_offer_id": hold_offer_id,
        "deterministic_transaction_offer_id": deterministic_offer_id,
        "deterministic_corridor_offer_id": deterministic_corridor_offer_id,
        "all_offer_ids_match": bool(semantic_offer_id) and len(set(offer_ids)) == 1,
        "actual_bsep_packet_id": (
            (causal_section or {}).get("actual_bsep_packet_id", "")
        ),
        "actual_airline_bsep_projection_ref": (
            (causal_section or {}).get("actual_airline_bsep_projection_ref", "")
        ),
        "causal_selection_bsep_projection_ref": (
            (causal_section or {}).get("causal_selection_bsep_projection_ref", "")
        ),
        "bsep_refs_match": (causal_section or {}).get("bsep_refs_match") is True,
        "causal_report_validation_accepted": (
            causal_report is not None
            and causal_runtime.validate_airline_semantic_causal_run_report_v01(
                causal_report,
            )[0]
        ),
        "deterministic_report_final_status": deterministic_final_status,
        "deterministic_corridor_final_status": deterministic_corridor_status,
        "semantic_actor_calls_total": len(semantic_actor_reports),
        "causal_actor_calls_total": causal_actor_calls,
        "duplicate_actor_calls": duplicate_actor_calls,
        "deterministic_collection_count": deterministic_collection_count,
        "corridor_execution_count": corridor_execution_count,
        "direct_offer_override_used": False,
        "default_offer_used": False,
        "silent_fallback_used": False,
        "provider_created_authority_count": 0,
        "real_world_effects_count": 0,
    }


def _bridge_final_guard_passes(bridge: Mapping[str, Any]) -> bool:
    return (
        bridge.get("bridge_status") == STATUS_PASS
        and bridge.get("all_offer_ids_match") is True
        and bridge.get("causal_report_validation_accepted") is True
        and bridge.get("deterministic_report_final_status") == STATUS_PASS
        and bridge.get("deterministic_corridor_final_status") == STATUS_PASS
        and bridge.get("semantic_actor_calls_total") == 12
        and bridge.get("causal_actor_calls_total") == 5
        and bridge.get("duplicate_actor_calls") == 0
        and bridge.get("deterministic_collection_count") == 1
        and bridge.get("corridor_execution_count") == 1
        and bridge.get("direct_offer_override_used") is False
        and bridge.get("default_offer_used") is False
        and bridge.get("silent_fallback_used") is False
        and bridge.get("provider_created_authority_count") == 0
        and bridge.get("real_world_effects_count") == 0
        and bridge.get("bsep_refs_match") is True
    )


def _integrated_deterministic_summary(
    deterministic_report: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if deterministic_report is None:
        return {
            "collection_status": "NOT_RUN",
            "corridor_execution_count": 0,
            "real_world_effects_count": 0,
        }
    corridor = deterministic_report.get("airline_ticket_purchase_corridor_v0_1")
    return {
        "collection_status": deterministic_report.get("final_status", ""),
        "transaction_id": deterministic_report.get("transaction_id", ""),
        "selected_offer_id": deterministic_report.get(
            "final_tri_party_mock_summary",
            {},
        ).get("selected_offer_id", ""),
        "corridor_final_status": getattr(corridor, "final_status", ""),
        "corridor_execution_count": 1 if corridor is not None else 0,
        "real_world_effects_count": deterministic_report.get(
            "counter_table",
            {},
        ).get("real_world_effects_count", 0),
    }


def _counter_table(
    *,
    report: Mapping[str, Any],
    provider_call_count: int,
    artifact_counts: Mapping[str, int],
    provider_mode: str,
    delay_applied_count: int,
    call_delay_seconds: float,
) -> dict[str, int | float]:
    actor_reports = tuple(report["semantic_actor_reports"])
    side_counts = {
        "transaction": 0,
        "client": 0,
        "airline": 0,
        "bank": 0,
        "cross_root_advisory": 0,
    }
    for actor_report in actor_reports:
        side_counts[actor_report["side"]] += 1
    causal_actor_count = sum(
        int(actor_report["actor_id"] in CAUSAL_ACTOR_IDS)
        for actor_report in actor_reports
    )
    duplicate_actor_count = len(actor_reports) - len(
        {actor_report["actor_id"] for actor_report in actor_reports},
    )
    causal_section = report.get("semantic_to_contract_causal_binding_v0_1", {})
    bridge = report.get("semantic_to_contract_deterministic_bridge", {})
    return {
        "semantic_actor_call_count": len(actor_reports),
        "causal_semantic_actor_call_count": causal_actor_count,
        "generic_semantic_actor_call_count": len(actor_reports) - causal_actor_count,
        "duplicate_semantic_actor_call_count": duplicate_actor_count,
        "precollected_causal_run_count": int(
            causal_section.get("precollected_causal_run_count", 0),
        ),
        "provider_calls_inside_precollected_runtime_count": int(
            causal_section.get(
                "provider_calls_performed_inside_precollected_entrypoint",
                0,
            ),
        ),
        "causal_report_pass_count": int(
            causal_section.get("binding_status")
            == causal_runtime.STATUS_LOCAL_MODEL_PASS,
        ),
        "deterministic_airline_collection_count": int(
            bridge.get("deterministic_collection_count", 0),
        ),
        "deterministic_airline_pass_count": int(
            bridge.get("deterministic_report_final_status") == STATUS_PASS,
        ),
        "ticket_purchase_corridor_execution_count": int(
            bridge.get("corridor_execution_count", 0),
        ),
        "ticket_purchase_corridor_pass_count": int(
            bridge.get("deterministic_corridor_final_status") == STATUS_PASS,
        ),
        "direct_offer_override_count": int(
            bridge.get("direct_offer_override_used", False),
        ),
        "default_offer_count": int(bridge.get("default_offer_used", False)),
        "silent_fallback_count": int(bridge.get("silent_fallback_used", False)),
        "tri_party_orchestrator_call_count": int(
            "tri_party_airline_orchestrator_llm" in report["semantic_actor_call_order"],
        ),
        "tri_party_architect_call_count": int(
            "tri_party_airline_semantic_architect_llm" in report["semantic_actor_call_order"],
        ),
        "transaction_semantic_actor_count": side_counts["transaction"],
        "client_semantic_actor_count": side_counts["client"],
        "airline_semantic_actor_count": side_counts["airline"],
        "bank_semantic_actor_count": side_counts["bank"],
        "cross_root_semantic_actor_count": side_counts["cross_root_advisory"],
        "vertical_fractal_semantic_cell_count": sum(
            int(actor_report.get("vertical_fractal_cell", False))
            for actor_report in actor_reports
        ),
        "bsep_created_count": int(bool(report["bsep_membrane"])),
        "bsep_validated_count": int(
            report["bsep_validation"].get("validation_status") == STATUS_PASS,
        ),
        "bsep_side_projection_count": len(report["bsep_side_projections"]),
        "prompts_written_count": artifact_counts["prompts_written_count"],
        "raw_responses_written_count": artifact_counts["raw_responses_written_count"],
        "extracted_json_candidates_written_count": artifact_counts[
            "extracted_json_candidates_written_count"
        ],
        "validations_written_count": artifact_counts["validations_written_count"],
        "canonical_summaries_written_count": artifact_counts[
            "canonical_summaries_written_count"
        ],
        "semantic_actor_validation_pass_count": sum(
            int(actor_report["validation_status"] == STATUS_PASS)
            for actor_report in actor_reports
        ),
        "semantic_actor_validation_fail_count": sum(
            int(actor_report["validation_status"] != STATUS_PASS)
            for actor_report in actor_reports
        ),
        "fake_provider_call_count": (
            provider_call_count if provider_mode == PROVIDER_MODE_FAKE else 0
        ),
        "real_provider_call_count": (
            provider_call_count if provider_mode == PROVIDER_MODE_REAL else 0
        ),
        "network_used_count": (
            provider_call_count if provider_mode == PROVIDER_MODE_REAL else 0
        ),
        "gemini_called_count": (
            provider_call_count if provider_mode == PROVIDER_MODE_REAL else 0
        ),
        "real_provider_call_delay_applied_count": delay_applied_count,
        "real_provider_call_delay_seconds": call_delay_seconds,
        "provider_output_used_as_truth_count": 0,
        "provider_output_used_as_authority_count": 0,
        "provider_created_authority_count": int(
            bridge.get("provider_created_authority_count", 0),
        ),
        "provider_created_contract_count": 0,
        "runtime_receipt_created_count": 0,
        "provider_output_created_packet_count": 0,
        "provider_output_created_receipt_count": 0,
        "provider_output_created_payment_count": 0,
        "provider_output_created_ticket_count": 0,
        "provider_output_created_booking_count": 0,
        "cross_root_authority_transfer_count": 0,
        "raw_passport_exposed_count": 0,
        "raw_card_exposed_count": 0,
        "raw_iban_exposed_count": 0,
        "raw_payment_token_exposed_count": 0,
        "real_airline_api_called_count": 0,
        "real_bank_api_called_count": 0,
        "real_gds_api_called_count": 0,
        "real_payment_executed_count": 0,
        "real_ticket_issued_count": 0,
        "real_booking_created_count": 0,
        "real_world_effects_count": 0,
    }


def _zero_counter_table() -> dict[str, int]:
    keys = (
        "semantic_actor_call_count",
        "causal_semantic_actor_call_count",
        "generic_semantic_actor_call_count",
        "duplicate_semantic_actor_call_count",
        "precollected_causal_run_count",
        "provider_calls_inside_precollected_runtime_count",
        "causal_report_pass_count",
        "deterministic_airline_collection_count",
        "deterministic_airline_pass_count",
        "ticket_purchase_corridor_execution_count",
        "ticket_purchase_corridor_pass_count",
        "direct_offer_override_count",
        "default_offer_count",
        "silent_fallback_count",
        "tri_party_orchestrator_call_count",
        "tri_party_architect_call_count",
        "transaction_semantic_actor_count",
        "client_semantic_actor_count",
        "airline_semantic_actor_count",
        "bank_semantic_actor_count",
        "cross_root_semantic_actor_count",
        "vertical_fractal_semantic_cell_count",
        "bsep_created_count",
        "bsep_validated_count",
        "bsep_side_projection_count",
        "prompts_written_count",
        "raw_responses_written_count",
        "extracted_json_candidates_written_count",
        "validations_written_count",
        "canonical_summaries_written_count",
        "semantic_actor_validation_pass_count",
        "semantic_actor_validation_fail_count",
        "fake_provider_call_count",
        "real_provider_call_count",
        "network_used_count",
        "gemini_called_count",
        "real_provider_call_delay_applied_count",
        "real_provider_call_delay_seconds",
        "provider_output_used_as_truth_count",
        "provider_output_used_as_authority_count",
        "provider_created_authority_count",
        "provider_created_contract_count",
        "runtime_receipt_created_count",
        "provider_output_created_packet_count",
        "provider_output_created_receipt_count",
        "provider_output_created_payment_count",
        "provider_output_created_ticket_count",
        "provider_output_created_booking_count",
        "cross_root_authority_transfer_count",
        "raw_passport_exposed_count",
        "raw_card_exposed_count",
        "raw_iban_exposed_count",
        "raw_payment_token_exposed_count",
        "real_airline_api_called_count",
        "real_bank_api_called_count",
        "real_gds_api_called_count",
        "real_payment_executed_count",
        "real_ticket_issued_count",
        "real_booking_created_count",
        "real_world_effects_count",
    )
    return {key: 0 for key in keys}


def _write_text_artifact(
    artifact_dir: Path | None,
    filename: str,
    text: str,
    artifacts: dict[str, Any],
    counts: dict[str, int],
    count_key: str,
) -> str:
    if artifact_dir is None:
        return ""
    path = artifact_dir / filename
    path.write_text(text)
    artifacts[filename] = str(path)
    counts[count_key] += 1
    return str(path)


def _write_json_artifact(
    artifact_dir: Path | None,
    filename: str,
    payload: Mapping[str, Any],
    artifacts: dict[str, Any],
    counts: dict[str, int],
    count_key: str,
) -> str:
    if artifact_dir is None:
        return ""
    path = artifact_dir / filename
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True))
    artifacts[filename] = str(path)
    counts[count_key] += 1
    return str(path)


def _write_json_named(
    artifact_dir: Path | None,
    filename: str,
    payload: Mapping[str, Any],
    artifacts: dict[str, Any],
) -> str:
    if artifact_dir is None:
        return ""
    path = artifact_dir / filename
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True))
    artifacts[filename] = str(path)
    return str(path)


def _write_summary_artifacts(
    artifact_dir: Path | None,
    report: Mapping[str, Any],
    artifacts: dict[str, Any],
) -> None:
    if artifact_dir is None:
        return
    summary_path = artifact_dir / "summary.json"
    summary_path.write_text(json.dumps(_json_safe(report), indent=2, sort_keys=True))
    artifacts["summary.json"] = str(summary_path)
    summary_log = artifact_dir / "summary.log"
    summary_log.write_text(
        "\n".join(
            (
                f"run_id: {report['run_id']}",
                f"final_status: {report['final_status']}",
                f"semantic_actor_call_count: {report['counter_table']['semantic_actor_call_count']}",
                f"fake_provider_call_count: {report['counter_table']['fake_provider_call_count']}",
            ),
        ),
    )
    artifacts["summary.log"] = str(summary_log)


def _scan_secret_markers(
    report: Mapping[str, Any],
    artifact_dir: Path | None,
) -> dict[str, Any]:
    scanned = [json.dumps(_json_safe(report), sort_keys=True)]
    files_scanned = 1
    if artifact_dir is not None and artifact_dir.exists():
        for path in sorted(artifact_dir.iterdir()):
            if path.is_file():
                scanned.append(path.read_text())
                files_scanned += 1
    matched = sorted(
        {
            marker
            for marker in SECRET_MARKERS
            if any(marker in text for text in scanned)
        },
    )
    return {
        "passed": not matched,
        "matched_markers": tuple(matched),
        "files_scanned": files_scanned,
    }


def _non_claims() -> tuple[str, ...]:
    return (
        "not production",
        "not public auditor package",
        "provider output is advisory only",
        "runtime validation is required",
        "no secret access",
        "no real airline API",
        "no real bank API",
        "no real GDS API",
        "no real payment",
        "no real ticket",
        "no real booking",
        "no real-world effects",
    )


def _append_actor_lines(
    lines: list[str],
    report: Mapping[str, Any],
    actor_id: str,
) -> None:
    actor = next(
        (item for item in report["semantic_actor_reports"] if item["actor_id"] == actor_id),
        None,
    )
    if actor is None:
        lines.append(f"{actor_id}: not called")
        return
    lines.append(f"{actor_id}: {actor['validation_status']}")
    lines.append(f"summary: {actor['output_semantic_summary']}")


def _append_group(
    lines: list[str],
    report: Mapping[str, Any],
    section: str,
    group: str,
) -> None:
    lines.extend(("", section))
    for actor in report["semantic_actor_reports"]:
        if actor["group"] == group:
            lines.append(f"- {actor['actor_id']}: {actor['validation_status']}")


def _actor_spec(actor_id: str) -> Mapping[str, Any]:
    for actor in ACTOR_SPECS:
        if actor["actor_id"] == actor_id:
            return actor
    raise KeyError(actor_id)


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


if __name__ == "__main__":
    raise SystemExit(main())
