from __future__ import annotations

import json
import math
import os
import time
from collections.abc import Mapping as MappingABC
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from demo import run_airline_transaction_artifact_ledger_audit_v01 as ledger_audit
from demo import run_live_provider_adapter_response_capture_v01 as provider_adapter
from demo import run_tri_party_airline_ticket_purchase_mock_e2e_v01 as deterministic_airline
from demo.run_live_unknown_request_dual_rich_context_v01 import (
    _call_live_gemini_provider as _shared_live_gemini_provider,
)
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as causal_runtime
from hedgehog.domains.airline import semantic_provider_canonicalization_v01 as semantic_canonicalization
from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import (
    transaction_artifact_ledger_collector_v01 as ledger_collector,
)
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


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
ENV_CRYPTO_ARTIFACT_SEAL = "HEDGEHOG_AIRLINE_CRYPTO_ARTIFACT_SEAL"

CRYPTO_MANIFEST_FILE = "airline_crypto_artifact_seal_manifest_v01.json"
CRYPTO_VERIFICATION_FILE = "airline_crypto_artifact_seal_verification_v01.json"
CRYPTO_SOURCE_SUMMARY_ROLE = "sealed_source_input_not_crypto_result"
CRYPTO_NEXT_GATE = "airline_crypto_artifact_seal_v01_slice_e1_anchor_publication"

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
REASON_CRYPTO_LIVE_GATE_REQUIRED = "crypto_live_lane_gate_required"
REASON_CRYPTO_CAUSAL_GATE_REQUIRED = "crypto_causal_binding_gate_required"
PROVIDER_RESULT_MAX_UTF8_BYTES = 16384
PROVIDER_JSON_MAX_DEPTH = 32
PROVIDER_JSON_MAX_NODES = 1024
PROVIDER_JSON_MAX_COLLECTION_WIDTH = 128
PROVIDER_RESULT_INVALID = "provider_result_invalid"
REASON_CRYPTO_ARTIFACT_DIR_REQUIRED = "crypto_artifact_dir_required"
REASON_CRYPTO_ARTIFACT_DIR_SYMLINK = "crypto_artifact_dir_symlink"
REASON_CRYPTO_ARTIFACT_DIR_INVALID = "crypto_artifact_dir_invalid"
REASON_CRYPTO_ARTIFACT_DIR_NOT_EMPTY = "crypto_artifact_dir_not_empty"
REASON_CRYPTO_SOURCE_PACKAGE_REF_INVALID = "crypto_source_package_ref_invalid"
REASON_CRYPTO_TARGET_EXISTS = "crypto_derived_artifact_target_exists"
REASON_CRYPTO_UPSTREAM_LANE_FAILED = "crypto_upstream_lane_failed"
REASON_CRYPTO_SOURCE_TRANSACTION_FAILED = "crypto_source_transaction_failed"
REASON_CRYPTO_SOURCE_SCOPE_MISMATCH = "crypto_required_source_scope_mismatch"
REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED = "crypto_source_snapshot_failed"
REASON_CRYPTO_SOURCE_BYTES_CHANGED_DURING_AUDIT = (
    "crypto_source_bytes_changed_during_audit"
)
REASON_CRYPTO_E1_AUDIT_FAILED = "crypto_e1_audit_failed"
REASON_CRYPTO_E1_AUDIT_FOREIGN_DIR = "crypto_e1_audit_foreign_directory"
REASON_CRYPTO_E1_PROJECTION_FAILED = "crypto_e1_projection_failed"
REASON_CRYPTO_TYPED_SOURCE_MISSING = "crypto_typed_ledger_source_missing"
REASON_CRYPTO_EXPECTED_IDENTITY_FAILED = "crypto_expected_identity_failed"
REASON_CRYPTO_C1_SOURCE_BUNDLE_FAILED = "crypto_c1_source_bundle_failed"
REASON_CRYPTO_C2_COLLECTION_FAILED = "crypto_c2_collection_failed"
REASON_CRYPTO_C2_RESULT_INVALID = "crypto_c2_result_invalid"
REASON_CRYPTO_DERIVED_PAYLOAD_INVALID = "crypto_derived_payload_invalid"
REASON_CRYPTO_DERIVED_SECRET_MARKER = "crypto_derived_secret_marker"
REASON_CRYPTO_DERIVED_WRITE_FAILED = "crypto_derived_artifact_write_failed"
REASON_CRYPTO_DERIVED_REREAD_FAILED = "crypto_derived_artifact_reread_failed"
REASON_CRYPTO_DERIVED_CLEANUP_FAILED = "crypto_derived_artifact_cleanup_failed"
REASON_CRYPTO_SOURCE_BYTES_CHANGED_AFTER_WRITE = (
    "crypto_source_bytes_changed_after_write"
)

CRYPTO_FAILURE_REASONS = (
    REASON_CRYPTO_LIVE_GATE_REQUIRED,
    REASON_CRYPTO_CAUSAL_GATE_REQUIRED,
    REASON_CRYPTO_ARTIFACT_DIR_REQUIRED,
    REASON_CRYPTO_ARTIFACT_DIR_SYMLINK,
    REASON_CRYPTO_ARTIFACT_DIR_INVALID,
    REASON_CRYPTO_ARTIFACT_DIR_NOT_EMPTY,
    REASON_CRYPTO_SOURCE_PACKAGE_REF_INVALID,
    REASON_CRYPTO_TARGET_EXISTS,
    REASON_CRYPTO_UPSTREAM_LANE_FAILED,
    REASON_CRYPTO_SOURCE_TRANSACTION_FAILED,
    REASON_CRYPTO_SOURCE_SCOPE_MISMATCH,
    REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED,
    REASON_CRYPTO_SOURCE_BYTES_CHANGED_DURING_AUDIT,
    REASON_CRYPTO_E1_AUDIT_FAILED,
    REASON_CRYPTO_E1_AUDIT_FOREIGN_DIR,
    REASON_CRYPTO_E1_PROJECTION_FAILED,
    REASON_CRYPTO_TYPED_SOURCE_MISSING,
    REASON_CRYPTO_EXPECTED_IDENTITY_FAILED,
    REASON_CRYPTO_C1_SOURCE_BUNDLE_FAILED,
    REASON_CRYPTO_C2_COLLECTION_FAILED,
    REASON_CRYPTO_C2_RESULT_INVALID,
    REASON_CRYPTO_DERIVED_PAYLOAD_INVALID,
    REASON_CRYPTO_DERIVED_SECRET_MARKER,
    REASON_CRYPTO_DERIVED_WRITE_FAILED,
    REASON_CRYPTO_DERIVED_REREAD_FAILED,
    REASON_CRYPTO_DERIVED_CLEANUP_FAILED,
    REASON_CRYPTO_SOURCE_BYTES_CHANGED_AFTER_WRITE,
)

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
    artifact_dir_value = effective_env.get(ENV_ARTIFACT_DIR, "")
    artifact_dir = Path(artifact_dir_value) if artifact_dir_value else None
    crypto_requested = effective_env.get(ENV_CRYPTO_ARTIFACT_SEAL) == "1"
    if crypto_requested:
        crypto_precondition_error = _crypto_precondition_error(
            effective_env,
            artifact_dir,
        )
        if crypto_precondition_error:
            deterministic_context = (
                deterministic_airline
                .build_tri_party_airline_semantic_source_context_v01()
            )
            report = _fail_closed_report(
                reason=crypto_precondition_error,
                provider_mode=PROVIDER_MODE_SKIPPED,
                model=effective_env.get(ENV_MODEL, DEFAULT_MODEL),
                deterministic_report=deterministic_context,
                crypto_requested=True,
            )
            report["airline_crypto_artifact_seal_source_boundary"] = (
                _crypto_source_boundary(True)
            )
            report["airline_crypto_artifact_seal_integration"] = (
                _crypto_failure_integration(crypto_precondition_error)
            )
            report["failed_stage"] = "crypto_precondition"
            return report
    deterministic_report = (
        deterministic_airline.build_tri_party_airline_semantic_source_context_v01()
        if causal_gate_open
        else deterministic_airline.collect_tri_party_airline_ticket_purchase_mock_e2e_v01()
    )

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
            crypto_requested=crypto_requested,
        )

    if causal_gate_open and causal_constraints is None:
        return _fail_closed_report(
            reason="causal_constraints_required",
            provider_mode=PROVIDER_MODE_SKIPPED,
            model=effective_env.get(ENV_MODEL, DEFAULT_MODEL),
            deterministic_report=deterministic_report,
            crypto_requested=crypto_requested,
        )
    if not fake_selected and not real_selected:
        return _fail_closed_report(
            reason="provider_mode_not_selected",
            provider_mode=PROVIDER_MODE_SKIPPED,
            model=effective_env.get(ENV_MODEL, DEFAULT_MODEL),
            deterministic_report=deterministic_report,
            crypto_requested=crypto_requested,
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
                crypto_requested=crypto_requested,
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
        crypto_requested=crypto_requested,
    )
    return report


def _exact_crypto_boolean_text(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "invalid"


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

    ledger_summary = report.get("airline_transaction_artifact_ledger_integration", {})
    if ledger_summary and ledger_summary.get("integration_status") != "NOT_RUN":
        lines.extend(
            (
                "",
                "[AIRLINE TRANSACTION ARTIFACT LEDGER V0.1]",
                f"integration status: {ledger_summary.get('integration_status', '')}",
                f"Ledger ID: {ledger_summary.get('ledger_id', '')}",
                f"transaction ID: {ledger_summary.get('transaction_id', '')}",
                f"selected offer: {ledger_summary.get('selected_offer_id', '')}",
                "source refs: "
                f"{ledger_summary.get('source_run_ref', '')}; "
                f"{ledger_summary.get('source_causal_report_ref', '')}; "
                f"{ledger_summary.get('source_corridor_report_ref', '')}",
                "source-bundle validation: "
                f"{ledger_summary.get('source_bundle_validation_status', '')}",
                f"Ledger validation: {ledger_summary.get('ledger_validation_status', '')}",
                f"entries: {ledger_summary.get('entry_count', 0)}",
                f"dependency edges: {ledger_summary.get('dependency_edge_count', 0)}",
                f"Root finals: {ledger_summary.get('root_final_count', 0)}",
                f"corridor executions: {ledger_summary.get('corridor_execution_count', 0)}",
                f"Ledger collections: {ledger_summary.get('ledger_collection_count', 0)}",
                f"artifact written: {bool(ledger_summary.get('artifact_written_count', 0))}",
                "Ledger-created authority: "
                f"{ledger_summary.get('ledger_created_authority_count', 0)}",
                "Ledger-created permission: "
                f"{ledger_summary.get('ledger_created_permission_count', 0)}",
                "Ledger-created action: "
                f"{ledger_summary.get('ledger_created_action_count', 0)}",
                "provider/network/Gemini calls added by Ledger: "
                f"{ledger_summary.get('provider_calls_added_by_ledger_count', 0)}/"
                f"{ledger_summary.get('network_calls_added_by_ledger_count', 0)}/"
                f"{ledger_summary.get('gemini_calls_added_by_ledger_count', 0)}",
                f"real-world effects: {ledger_summary.get('real_world_effects_count', 0)}",
            ),
        )

    crypto_boundary = report.get("airline_crypto_artifact_seal_source_boundary", {})
    crypto_summary = report.get("airline_crypto_artifact_seal_integration", {})
    if (
        isinstance(crypto_boundary, MappingABC)
        and crypto_boundary.get("integration_requested") is True
        and isinstance(crypto_summary, MappingABC)
    ):
        crypto_status = crypto_summary.get("integration_status")
        if (
            type(crypto_status) is str
            and crypto_status
            == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
        ):
            crypto_claim = (
                "Internally self-consistent and unanchored; not final Crypto PASS."
            )
        elif type(crypto_status) is str and crypto_status == STATUS_FAIL_CLOSED:
            crypto_claim = (
                "Crypto integration failed closed; no internal self-consistency "
                "or Crypto PASS is claimed."
            )
        else:
            crypto_claim = (
                "Crypto integration status is invalid; no internal self-consistency "
                "or Crypto PASS is claimed."
            )
        lines.extend(
            (
                "",
                "[AIRLINE CRYPTO ARTIFACT SEAL V0.1]",
                f"integration status: {crypto_summary.get('integration_status', '')}",
                f"source package ref: {crypto_summary.get('source_package_ref', '')}",
                f"transaction ID: {crypto_summary.get('transaction_id', '')}",
                f"Ledger ID: {crypto_summary.get('ledger_id', '')}",
                "Ledger geometry: "
                f"{crypto_summary.get('ledger_entry_count', 0)} / "
                f"{crypto_summary.get('dependency_edge_count', 0)} / "
                f"{crypto_summary.get('root_final_count', 0)}",
                f"source files: {crypto_summary.get('source_file_count', 0)}",
                f"Manifest Core hash: {crypto_summary.get('manifest_core_hash', '')}",
                f"chain tail hash: {crypto_summary.get('chain_tail_hash', '')}",
                f"source-package hash: {crypto_summary.get('source_package_hash', '')}",
                f"signature mode: {crypto_summary.get('signature_mode', '')}",
                "signature verified: "
                f"{_exact_crypto_boolean_text(crypto_summary.get('signature_verified'))}",
                "external anchor supplied: "
                f"{_exact_crypto_boolean_text(crypto_summary.get('external_anchor_supplied'))}",
                "external anchor verified: "
                f"{_exact_crypto_boolean_text(crypto_summary.get('external_anchor_verified'))}",
                "source bytes stable after audit/collection/write: "
                f"{_exact_crypto_boolean_text(crypto_summary.get('source_bytes_unchanged_after_audit'))}/"
                f"{_exact_crypto_boolean_text(crypto_summary.get('source_bytes_unchanged_after_collection'))}/"
                f"{_exact_crypto_boolean_text(crypto_summary.get('source_bytes_unchanged_after_write'))}",
                f"manifest file: {crypto_summary.get('manifest_artifact_ref', '')}",
                f"verification file: {crypto_summary.get('verification_artifact_ref', '')}",
                f"next gate: {crypto_summary.get('next_gate', '')}",
                crypto_claim,
                "Not signer authentication, PKI, non-repudiation, trusted timestamping, or a production-security claim.",
                "No Replay and no real-world effect.",
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
        causal_request = metadata.get("semantic_to_contract_request")
        if isinstance(causal_request, Mapping):
            if actor_id == causal_runtime.ACTOR_ORDER[0]:
                return json.dumps(
                    {
                        "recommended_offer_id": binding.OFFER_A_ID,
                        "ranked_offer_ids": [binding.OFFER_A_ID],
                        "decision_factors": ["preference_a_exact_fit"],
                        "preference_matches": ["lower_price", "window_seat"],
                        "uncertainty_notes": ["requires_client_root_review"],
                        "requires_root_review": True,
                        "semantic_summary": (
                            "Offer A best matches the declared preferences."
                        ),
                    },
                    sort_keys=True,
                )
            return json.dumps(
                {
                    "supports_proposed_offer": True,
                    "semantic_factors": ["offer_a_is_hard_compatible"],
                    "blocking_conflicts": [],
                },
                sort_keys=True,
            )
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
        return _shared_live_gemini_provider(
            prompt=prompt,
            model_name=model,
            timeout_seconds=provider_adapter._timeout_seconds(provider_env),
            explicit_http_timeout=True,
            env=provider_env,
            response_schema=None,
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
    crypto_requested: bool = False,
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
        candidate, parse_errors = _preprocess_provider_result(raw_response)
        if parse_errors:
            failed_actor_id = actor_id
            failed_stage = "provider_result_validation"
            provider_error_sanitized = PROVIDER_RESULT_INVALID
            validation_errors.append(f"{PROVIDER_RESULT_INVALID}:{actor_id}")
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
        extracted_json_artifact = _write_json_artifact(
            artifact_dir,
            f"{actor_id}_extracted_json_candidate.json",
            candidate,
            artifacts,
            artifact_counts,
            "extracted_json_candidates_written_count",
        )
        if causal_request is not None and causal_selection_input is not None:
            canonicalization = (
                semantic_canonicalization
                .canonicalize_airline_causal_provider_response_v01(
                    raw_provider_response=raw_response,
                    request=causal_request,
                    bsep_projection=causal_bsep_projection,
                    constraints=causal_constraints,
                    selection_input=causal_selection_input,
                    snapshot=actual_causal_snapshot,
                )
            )
            semantic_plain = (
                asdict(canonicalization.extracted_semantic_object)
                if canonicalization.extracted_semantic_object is not None
                else None
            )
            canonical_plain = (
                asdict(canonicalization.runtime_canonical_artifact)
                if canonicalization.runtime_canonical_artifact is not None
                else None
            )
            errors = tuple(
                dict.fromkeys(
                    (*parse_errors,
                     *canonicalization.semantic_validation.reason_codes,
                     *canonicalization.canonical_validation.reason_codes)
                )
            )
            validation = {
                "accepted": canonicalization.final_status == STATUS_PASS,
                "validation_status": canonicalization.final_status,
                "errors": errors,
                "evidence_categories": {
                    "raw_provider_response": {
                        "artifact_ref": raw_response_artifact,
                        "unchanged": canonicalization.raw_provider_response
                        == raw_response,
                    },
                    "extracted_semantic_object": semantic_plain,
                    "semantic_envelope_validation": asdict(
                        canonicalization.semantic_validation
                    ),
                    "runtime_canonical_artifact": canonical_plain,
                    "canonical_validation": asdict(
                        canonicalization.canonical_validation
                    ),
                    "field_ownership_provenance": asdict(
                        canonicalization.field_ownership
                    ),
                },
            }
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
                    causal_proposer_payload = canonical_plain or {}
                    causal_proposal = canonicalization.runtime_canonical_artifact
                else:
                    causal_reviewer_payloads[actor_id] = canonical_plain or {}
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
                canonical_plain or candidate,
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
                        bsep_side_projections=bsep_side_projections,
                        ledger_source_bundle_id=(
                            f"{RUN_ID}:{REPORT_ID}:{causal_report.scenario_id}"
                        ),
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
        "airline_transaction_artifact_ledger_v0_1": (
            _integrated_ledger(integrated_deterministic_report)
        ),
        "airline_transaction_artifact_ledger_integration": (
            _integrated_ledger_summary(integrated_deterministic_report)
        ),
        "airline_crypto_artifact_seal_source_boundary": (
            _crypto_source_boundary(crypto_requested)
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
    ledger_json, ledger_prepare_error = _prepare_airline_transaction_artifact_ledger_json(
        artifact_dir,
        report,
    )
    if ledger_prepare_error:
        validation_errors.append(ledger_prepare_error)
        report["validation_errors"] = tuple(validation_errors)
        report["final_status"] = STATUS_FAIL_CLOSED
        report["failed_stage"] = "airline_transaction_artifact_ledger_write"
        ledger_json = ""
    secret_scan = _scan_secret_markers(
        report,
        artifact_dir,
        additional_texts=(ledger_json,) if ledger_json else (),
    )
    report["secret_scan"] = secret_scan
    if not secret_scan["passed"]:
        report["final_status"] = STATUS_FAIL_CLOSED
        report["failed_stage"] = "secret_scan"
        report["validation_errors"] = tuple(
            list(report["validation_errors"]) + ["secret_scan_failed"],
        )
        ledger_json = ""
    ledger_write_error = _write_airline_transaction_artifact_ledger_once(
        artifact_dir,
        report,
        artifacts,
        ledger_json=ledger_json,
    )
    if ledger_write_error:
        report["validation_errors"] = tuple(
            list(report["validation_errors"]) + [ledger_write_error],
        )
        report["final_status"] = STATUS_FAIL_CLOSED
        report["failed_stage"] = "airline_transaction_artifact_ledger_write"
    report["counter_table"] = _counter_table(
        report=report,
        provider_call_count=provider_call_count,
        artifact_counts=artifact_counts,
        provider_mode=provider_mode,
        delay_applied_count=delay_applied_count,
        call_delay_seconds=call_delay_seconds,
    )
    _write_json_named(artifact_dir, "secret_scan.json", secret_scan, artifacts)
    _write_summary_artifacts(artifact_dir, report, artifacts)
    if crypto_requested:
        try:
            crypto_integration = _collect_crypto_artifact_seal_integration_v01(
                artifact_dir=artifact_dir,
                report=report,
                integrated_deterministic_report=integrated_deterministic_report,
                artifacts=artifacts,
            )
        except (TypeError, AttributeError, ValueError, KeyError, IndexError, OSError):
            crypto_integration = _crypto_failure_integration(
                REASON_CRYPTO_C2_COLLECTION_FAILED,
            )
        report["airline_crypto_artifact_seal_integration"] = crypto_integration
        if (
            crypto_integration.get("integration_status")
            != crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
        ):
            crypto_errors = tuple(crypto_integration.get("validation_errors", ()))
            report["final_status"] = STATUS_FAIL_CLOSED
            report["failed_stage"] = "airline_crypto_artifact_seal_integration"
            report["validation_errors"] = tuple(
                dict.fromkeys(tuple(report["validation_errors"]) + crypto_errors),
            )
    else:
        report["airline_crypto_artifact_seal_integration"] = (
            _not_run_crypto_integration()
        )
    report["artifacts"] = artifacts
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
        "airline_transaction_artifact_ledger_v0_1": None,
        "airline_transaction_artifact_ledger_integration": (
            _not_run_ledger_summary()
        ),
        "airline_crypto_artifact_seal_source_boundary": (
            _crypto_source_boundary(False)
        ),
        "airline_crypto_artifact_seal_integration": (
            _not_run_crypto_integration()
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
    crypto_requested: bool = False,
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
    if crypto_requested:
        report["airline_crypto_artifact_seal_source_boundary"] = (
            _crypto_source_boundary(True)
        )
        report["airline_crypto_artifact_seal_integration"] = (
            _crypto_failure_integration(REASON_CRYPTO_UPSTREAM_LANE_FAILED)
        )
        report["failed_stage"] = "crypto_upstream_lane"
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
    causal_prompt_lines: tuple[str, ...] = ()
    if causal_request is not None:
        allowed_ids = tuple(causal_request.client_hard_compatible_candidate_ids)
        causal_prompt_lines = (
            "Return exactly the named semantic JSON fields and no mechanical fields.",
            (
                "Allowed hard-compatible offer ids: "
                + ", ".join(allowed_ids)
            ),
            "Candidate semantic records: "
            + json.dumps(_json_safe(causal_request.authoritative_candidate_projection), sort_keys=True),
            "Client hard constraints: "
            + json.dumps(_json_safe(causal_request.client_hard_constraints), sort_keys=True),
            "Client soft preferences: "
            + json.dumps(_json_safe(causal_request.client_soft_preferences), sort_keys=True),
            "JSON MIME shape and the local semantic and canonical validators are mandatory.",
        )
        if causal_request.actor_id == causal_runtime.ACTOR_ORDER[0]:
            causal_prompt_lines += (
                "recommended_offer_id: non-empty JSON string selected by semantic comparison from the allowed hard-compatible offer ids; no default.",
                "ranked_offer_ids: non-empty JSON array of unique allowed hard-compatible offer-id strings in genuine semantic rank order.",
                "decision_factors: non-empty JSON array of non-empty semantic-factor strings.",
                "preference_matches: non-empty JSON array of non-empty declared-preference match strings.",
                "uncertainty_notes: non-empty JSON array of non-empty uncertainty strings.",
                "requires_root_review: JSON boolean asserting mandatory Root review.",
                "semantic_summary: non-empty advisory JSON string.",
            )
        else:
            causal_prompt_lines += (
                "supports_proposed_offer: JSON boolean derived neutrally from actual semantic review; support and rejection are both allowed.",
                "semantic_factors: non-empty JSON array of non-empty review-factor strings.",
                "blocking_conflicts: JSON array containing every actual blocking-conflict string and no invented conflict.",
                "The proposed offer to review is: " + causal_request.proposed_offer_id,
                "Local semantic and canonical validators remain authoritative for shape and safety.",
            )
    return_rule = (
        "Return only the exact fields in the named causal semantic contract."
        if causal_request is not None
        else "Return only semantic fields and safety flags."
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
            return_rule,
            "Do not create payment, ticket, booking, packet, receipt, authority, or FinalOutput.",
            "No raw passport, raw card, raw IBAN, raw payment token, raw private profile, API key, connector credential, raw provider text from other actors, or peer raw content is allowed.",
            *causal_prompt_lines,
            *(("Explicit JSON skeleton:", json.dumps(json_skeleton, sort_keys=True)) if causal_request is None else ()),
        ),
    )


def _preprocess_provider_result(
    value: object,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    if type(value) is not str:
        return {}, (PROVIDER_RESULT_INVALID,)
    try:
        encoded = value.encode("utf-8", errors="strict")
    except UnicodeError:
        return {}, (PROVIDER_RESULT_INVALID,)
    if (
        not encoded
        or len(encoded) > PROVIDER_RESULT_MAX_UTF8_BYTES
        or "\x00" in value
        or "\r" in value
        or "\ufeff" in value
    ):
        return {}, (PROVIDER_RESULT_INVALID,)

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in items:
            if key in result:
                raise ValueError
            result[key] = item
        return result

    try:
        parsed = json.loads(
            value,
            object_pairs_hook=pairs,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError(constant)
            ),
        )
    except (
        json.JSONDecodeError,
        ValueError,
        TypeError,
        OverflowError,
        RecursionError,
    ):
        return {}, (PROVIDER_RESULT_INVALID,)
    if type(parsed) is not dict:
        return {}, (PROVIDER_RESULT_INVALID,)
    if not _provider_json_tree_is_bounded(parsed):
        return {}, (PROVIDER_RESULT_INVALID,)
    return parsed, ()


def _provider_json_tree_is_bounded(root: dict[str, object]) -> bool:
    stack: list[tuple[object, int]] = [(root, 0)]
    node_count = 0
    while stack:
        value, depth = stack.pop()
        node_count += 1
        if node_count > PROVIDER_JSON_MAX_NODES or depth > PROVIDER_JSON_MAX_DEPTH:
            return False
        if type(value) is dict:
            if len(value) > PROVIDER_JSON_MAX_COLLECTION_WIDTH:
                return False
            for key, item in value.items():
                if not _provider_json_string_is_safe(key):
                    return False
                stack.append((item, depth + 1))
        elif type(value) is list:
            if len(value) > PROVIDER_JSON_MAX_COLLECTION_WIDTH:
                return False
            stack.extend((item, depth + 1) for item in value)
        elif type(value) is str:
            if not _provider_json_string_is_safe(value):
                return False
        elif type(value) is float:
            if not math.isfinite(value):
                return False
        elif value is not None and type(value) not in (bool, int):
            return False
    return True


def _provider_json_string_is_safe(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return "\x00" not in value and "\r" not in value and "\ufeff" not in value


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
            "authority_created": False,
            "permission_created": False,
            "real_world_effects_count": 0,
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
    projection_ref = airline_projection.get("projection_ref")
    if type(projection_ref) is not str or not projection_ref:
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
        projection_ref = ""
    for false_field in (
        "raw_secrets_included",
        "raw_provider_text_included",
        "authority_created",
        "permission_created",
    ):
        if airline_projection.get(false_field) is not False:
            errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
    effects_count = airline_projection.get("real_world_effects_count")
    if type(effects_count) is not int or effects_count != 0:
        errors.append(REASON_LIVE_BSEP_CAUSAL_PROJECTION_LINEAGE_MISMATCH)
        effects_count = 1
    typed_projection = binding.AirlineBSEPProjectionRefV01(
        projection_ref=projection_ref,
        transaction_id=str(airline_projection.get("transaction_id", "")),
        projection_side="airline_offer_selection",
        validation_status=str(airline_projection.get("validation_status", "")),
        raw_secret_included=airline_projection.get("raw_secrets_included") is True,
        authority_created=airline_projection.get("authority_created") is True,
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
        (airline_bsep_projection or {}).get("projection_ref", ""),
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


def _not_run_ledger_summary() -> dict[str, Any]:
    return {
        "integration_status": "NOT_RUN",
        "source_bundle_validation_status": "NOT_RUN",
        "source_bundle_validation_errors": (),
        "ledger_validation_status": "NOT_RUN",
        "ledger_validation_errors": (),
        "ledger_id": "",
        "transaction_id": "",
        "source_run_ref": "",
        "source_causal_report_ref": "",
        "source_corridor_report_ref": "",
        "selected_offer_id": "",
        "entry_count": 0,
        "dependency_edge_count": 0,
        "root_final_count": 0,
        "source_bundle_collection_count": 0,
        "ledger_collection_count": 0,
        "ledger_validation_count": 0,
        "corridor_execution_count": 0,
        "duplicate_transaction_count": 0,
        "duplicate_corridor_execution_count": 0,
        "duplicate_ledger_collection_count": 0,
        "source_reconstruction_count": 0,
        "provider_calls_added_by_ledger_count": 0,
        "network_calls_added_by_ledger_count": 0,
        "gemini_calls_added_by_ledger_count": 0,
        "ledger_created_authority_count": 0,
        "ledger_created_permission_count": 0,
        "ledger_created_action_count": 0,
        "real_world_effects_count": 0,
        "artifact_written_count": 0,
    }


def _crypto_source_boundary(integration_requested: bool) -> dict[str, Any]:
    return {
        "integration_requested": integration_requested,
        "source_summary_role": CRYPTO_SOURCE_SUMMARY_ROLE,
        "manifest_artifact_ref": CRYPTO_MANIFEST_FILE,
        "verification_artifact_ref": CRYPTO_VERIFICATION_FILE,
        "expected_manifest_core_hash": None,
        "anchored_pass_claimed": False,
        "crypto_result_embedded_in_source_summary": False,
    }


def _crypto_integration_template(
    *,
    integration_status: str,
    validation_errors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "integration_status": integration_status,
        "source_bundle_id": "",
        "source_package_ref": "",
        "ledger_id": "",
        "transaction_id": "",
        "manifest_core_hash": "",
        "chain_tail_hash": "",
        "source_package_hash": "",
        "ledger_entry_count": 0,
        "dependency_edge_count": 0,
        "root_final_count": 0,
        "source_file_count": 0,
        "e1_audit_count": 0,
        "source_bundle_validation_count": 0,
        "manifest_core_collection_count": 0,
        "envelope_collection_count": 0,
        "post_collection_snapshot_provider_call_count": 0,
        "verification_count": 0,
        "manifest_artifact_written_count": 0,
        "verification_artifact_written_count": 0,
        "source_bytes_unchanged_after_audit": False,
        "source_bytes_unchanged_after_collection": False,
        "source_bytes_unchanged_after_write": False,
        "source_summary_frozen_before_crypto": False,
        "source_summary_rewritten_after_crypto": False,
        "expected_manifest_core_hash": None,
        "external_anchor_supplied": False,
        "external_anchor_verified": False,
        "anchored_pass_claimed": False,
        "signature_mode": crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER,
        "signature_verified": False,
        "audit_rerun_count": 0,
        "ledger_recollection_count": 0,
        "semantic_rerun_count": 0,
        "corridor_rerun_count": 0,
        "provider_calls_added_by_crypto_count": 0,
        "network_calls_added_by_crypto_count": 0,
        "gemini_calls_added_by_crypto_count": 0,
        "crypto_created_authority_count": 0,
        "crypto_created_permission_count": 0,
        "crypto_created_action_count": 0,
        "real_world_effects_count": 0,
        "manifest_artifact_ref": CRYPTO_MANIFEST_FILE,
        "verification_artifact_ref": CRYPTO_VERIFICATION_FILE,
        "validation_errors": validation_errors,
        "next_gate": CRYPTO_NEXT_GATE,
    }


def _not_run_crypto_integration() -> dict[str, Any]:
    return _crypto_integration_template(
        integration_status="NOT_RUN",
        validation_errors=(),
    )


def _crypto_failure_integration(
    reason: str,
    **observed: Any,
) -> dict[str, Any]:
    safe_reason = (
        reason if reason in CRYPTO_FAILURE_REASONS else REASON_CRYPTO_C2_COLLECTION_FAILED
    )
    result = _crypto_integration_template(
        integration_status=STATUS_FAIL_CLOSED,
        validation_errors=(safe_reason,),
    )
    result.update(observed)
    result["integration_status"] = STATUS_FAIL_CLOSED
    result["validation_errors"] = (safe_reason,)
    result["expected_manifest_core_hash"] = None
    result["anchored_pass_claimed"] = False
    return result


def _crypto_exception_reason(exc: BaseException, fallback: str) -> str:
    if (
        len(exc.args) == 1
        and type(exc.args[0]) is str
        and exc.args[0] in CRYPTO_FAILURE_REASONS
    ):
        return exc.args[0]
    return fallback


def _crypto_precondition_error(
    env: Mapping[str, str],
    artifact_dir: Path | None,
) -> str:
    if env.get(ENV_LANE) != "1":
        return REASON_CRYPTO_LIVE_GATE_REQUIRED
    if env.get(ENV_CAUSAL_BINDING) != "1":
        return REASON_CRYPTO_CAUSAL_GATE_REQUIRED
    if artifact_dir is None:
        return REASON_CRYPTO_ARTIFACT_DIR_REQUIRED
    try:
        if artifact_dir.is_symlink():
            return REASON_CRYPTO_ARTIFACT_DIR_SYMLINK
        if artifact_dir.exists() and not artifact_dir.is_dir():
            return REASON_CRYPTO_ARTIFACT_DIR_INVALID
    except OSError:
        return REASON_CRYPTO_ARTIFACT_DIR_INVALID
    package_ref_validation = (
        crypto_contracts.validate_airline_crypto_source_package_ref_v01(
            artifact_dir.name,
        )
    )
    if package_ref_validation.validation_status != crypto_contracts.STATUS_PASS:
        return REASON_CRYPTO_SOURCE_PACKAGE_REF_INVALID
    try:
        if any(
            target.exists() or target.is_symlink()
            for target in (
                artifact_dir / CRYPTO_MANIFEST_FILE,
                artifact_dir / CRYPTO_VERIFICATION_FILE,
            )
        ):
            return REASON_CRYPTO_TARGET_EXISTS
        if artifact_dir.exists():
            for filename in crypto_collector.REQUIRED_SOURCE_FILE_REFS:
                source_target = artifact_dir / filename
                if source_target.is_symlink() or (
                    source_target.exists() and not source_target.is_file()
                ):
                    return REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED
            if next(artifact_dir.iterdir(), None) is not None:
                return REASON_CRYPTO_ARTIFACT_DIR_NOT_EMPTY
    except OSError:
        return REASON_CRYPTO_ARTIFACT_DIR_INVALID
    return ""


def _read_crypto_source_snapshot_v01(
    artifact_dir: Path,
) -> tuple[tuple[str, bytes], ...]:
    if artifact_dir.is_symlink() or not artifact_dir.is_dir():
        raise ValueError(REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED)
    rows: list[tuple[str, bytes]] = []
    for filename in crypto_collector.REQUIRED_SOURCE_FILE_REFS:
        path = artifact_dir / filename
        if path.is_symlink() or not path.is_file():
            raise ValueError(REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED)
        try:
            rows.append((filename, path.read_bytes()))
        except OSError as exc:
            raise ValueError(REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED) from exc
    return tuple(rows)


def _project_e1_audit_for_crypto_v01(
    audit_report: object,
    *,
    artifact_dir: Path,
) -> crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    if (
        type(audit_report)
        is not ledger_audit.AirlineTransactionArtifactLedgerAuditReportV01
    ):
        raise ValueError(REASON_CRYPTO_E1_AUDIT_FAILED)
    if Path(audit_report.source_artifact_dir) != artifact_dir:
        raise ValueError(REASON_CRYPTO_E1_AUDIT_FOREIGN_DIR)
    projected = crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        audit_id=audit_report.audit_id,
        audit_version=audit_report.audit_version,
        final_status=audit_report.final_status,
        required_source_files=audit_report.required_source_files,
        files_read_count=audit_report.files_read_count,
        ledger_id=audit_report.ledger_id,
        transaction_id=audit_report.transaction_id,
        selected_offer_id=audit_report.selected_offer_id,
        source_run_ref=audit_report.source_run_ref,
        source_causal_report_ref=audit_report.source_causal_report_ref,
        source_corridor_report_ref=audit_report.source_corridor_report_ref,
        actual_entry_count=audit_report.actual_entry_count,
        actual_dependency_edge_count=audit_report.actual_dependency_edge_count,
        actual_root_final_count=audit_report.actual_root_final_count,
        client_root_final_count=audit_report.client_root_final_count,
        airline_root_final_count=audit_report.airline_root_final_count,
        bank_root_final_count=audit_report.bank_root_final_count,
        artifact_ids_unique=audit_report.artifact_ids_unique,
        ledger_indexes_contiguous=audit_report.ledger_indexes_contiguous,
        artifact_type_sequence_valid=audit_report.artifact_type_sequence_valid,
        dependencies_present=audit_report.dependencies_present,
        dependencies_backward_only=audit_report.dependencies_backward_only,
        dependency_graph_acyclic=audit_report.dependency_graph_acyclic,
        root_final_set_valid=audit_report.root_final_set_valid,
        root_ownership_valid=audit_report.root_ownership_valid,
        authority_evidence_boundaries_valid=(
            audit_report.authority_evidence_boundaries_valid
        ),
        canonical_hash_inputs_safe=audit_report.canonical_hash_inputs_safe,
        source_refs_consistent=audit_report.source_refs_consistent,
        transaction_identity_consistent=(
            audit_report.transaction_identity_consistent
        ),
        selected_offer_chain_consistent=(
            audit_report.selected_offer_chain_consistent
        ),
        secret_scan_passed=audit_report.secret_scan_passed,
        stored_validation_status=audit_report.stored_validation_status,
        stored_validation_errors=audit_report.stored_validation_errors,
        audit_created_authority_count=audit_report.audit_created_authority_count,
        audit_created_permission_count=audit_report.audit_created_permission_count,
        audit_created_action_count=audit_report.audit_created_action_count,
        semantic_rerun_count=audit_report.semantic_rerun_count,
        corridor_rerun_count=audit_report.corridor_rerun_count,
        ledger_collection_count=audit_report.ledger_collection_count,
        provider_call_count=audit_report.provider_call_count,
        network_call_count=audit_report.network_call_count,
        gemini_call_count=audit_report.gemini_call_count,
        crypto_operation_count=audit_report.crypto_operation_count,
        replay_operation_count=audit_report.replay_operation_count,
        real_world_effects_count=audit_report.real_world_effects_count,
        validation_errors=audit_report.validation_errors,
    )
    validation = (
        crypto_collector
        .validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
            projected,
        )
    )
    if validation.validation_status != crypto_contracts.STATUS_PASS:
        raise ValueError(REASON_CRYPTO_E1_PROJECTION_FAILED)
    return projected


def _crypto_payload_text_v01(payload: object) -> str:
    if type(payload) is not dict:
        raise ValueError(REASON_CRYPTO_DERIVED_PAYLOAD_INVALID)
    validation = crypto_contracts.validate_airline_crypto_canonical_json_value_v01(
        payload,
    )
    if validation.validation_status != crypto_contracts.STATUS_PASS:
        raise ValueError(REASON_CRYPTO_DERIVED_PAYLOAD_INVALID)
    try:
        text = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    except (TypeError, ValueError) as exc:
        raise ValueError(REASON_CRYPTO_DERIVED_PAYLOAD_INVALID) from exc
    if any(marker in text for marker in SECRET_MARKERS):
        raise ValueError(REASON_CRYPTO_DERIVED_SECRET_MARKER)
    return text


def _cleanup_crypto_artifact_paths_v01(
    created_paths: tuple[Path, ...],
) -> bool:
    cleanup_failed = False
    for path in reversed(created_paths):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            cleanup_failed = True
    for path in created_paths:
        try:
            if path.exists() or path.is_symlink():
                cleanup_failed = True
        except OSError:
            cleanup_failed = True
    return not cleanup_failed


def _write_crypto_artifact_pair_v01(
    *,
    artifact_dir: Path,
    manifest_payload: object,
    verification_payload: object,
) -> tuple[Path, Path]:
    manifest_text = _crypto_payload_text_v01(manifest_payload)
    verification_text = _crypto_payload_text_v01(verification_payload)
    manifest_path = artifact_dir / CRYPTO_MANIFEST_FILE
    verification_path = artifact_dir / CRYPTO_VERIFICATION_FILE
    try:
        if (
            manifest_path.exists()
            or manifest_path.is_symlink()
            or verification_path.exists()
            or verification_path.is_symlink()
        ):
            raise ValueError(REASON_CRYPTO_TARGET_EXISTS)
    except OSError as exc:
        raise ValueError(REASON_CRYPTO_DERIVED_WRITE_FAILED) from exc

    created_paths: list[Path] = []
    try:
        manifest_handle = manifest_path.open("x", encoding="utf-8")
        created_paths.append(manifest_path)
        with manifest_handle as handle:
            handle.write(manifest_text)
        verification_handle = verification_path.open("x", encoding="utf-8")
        created_paths.append(verification_path)
        with verification_handle as handle:
            handle.write(verification_text)
    except Exception as exc:
        reason = REASON_CRYPTO_DERIVED_WRITE_FAILED
        if not _cleanup_crypto_artifact_paths_v01(tuple(created_paths)):
            reason = REASON_CRYPTO_DERIVED_CLEANUP_FAILED
        raise ValueError(reason) from exc
    try:
        actual_manifest_text = manifest_path.read_text(encoding="utf-8")
        actual_verification_text = verification_path.read_text(encoding="utf-8")
        parsed_manifest = json.loads(actual_manifest_text)
        parsed_verification = json.loads(actual_verification_text)
    except Exception as exc:
        reason = REASON_CRYPTO_DERIVED_REREAD_FAILED
        if not _cleanup_crypto_artifact_paths_v01(tuple(created_paths)):
            reason = REASON_CRYPTO_DERIVED_CLEANUP_FAILED
        raise ValueError(reason) from exc
    if (
        actual_manifest_text != manifest_text
        or actual_verification_text != verification_text
        or parsed_manifest != manifest_payload
        or parsed_verification != verification_payload
    ):
        reason = REASON_CRYPTO_DERIVED_REREAD_FAILED
        if not _cleanup_crypto_artifact_paths_v01(tuple(created_paths)):
            reason = REASON_CRYPTO_DERIVED_CLEANUP_FAILED
        raise ValueError(reason)
    return manifest_path, verification_path


def _crypto_collection_successful(
    result: object,
) -> bool:
    if type(result) is not crypto_collector.AirlineCryptoArtifactSealCollectionResultV01:
        return False
    contract = crypto_collector.validate_airline_crypto_artifact_seal_collection_result_v01(
        result,
    )
    verification = result.verification_report
    return bool(
        contract.validation_status == crypto_contracts.STATUS_PASS
        and result.collection_status
        == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
        and result.manifest_core is not None
        and result.envelope is not None
        and verification is not None
        and verification.verification_status
        == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
        and result.source_bytes_unchanged_after_audit is True
        and result.source_bytes_unchanged_after_collection is True
        and result.expected_manifest_core_hash is None
        and verification.expected_manifest_core_hash is None
        and verification.external_anchor_supplied is False
        and verification.external_anchor_verified is False
        and verification.signature_mode
        == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
        and verification.signature_verified is False
        and all(
            type(getattr(result, field_name)) is int
            and getattr(result, field_name) == 1
            for field_name in crypto_collector.COLLECTION_STAGE_COUNT_FIELDS
        )
        and all(
            type(getattr(result, field_name)) is int
            and getattr(result, field_name) == 0
            for field_name in crypto_collector.COLLECTION_ZERO_COUNTER_FIELDS
        )
    )


def _collect_crypto_artifact_seal_integration_v01(
    *,
    artifact_dir: Path | None,
    report: Mapping[str, Any],
    integrated_deterministic_report: Mapping[str, Any] | None,
    artifacts: dict[str, Any],
) -> dict[str, Any]:
    if artifact_dir is None:
        return _crypto_failure_integration(REASON_CRYPTO_ARTIFACT_DIR_REQUIRED)
    if report.get("final_status") != STATUS_PASS:
        return _crypto_failure_integration(REASON_CRYPTO_SOURCE_TRANSACTION_FAILED)
    if (
        tuple(ledger_audit.REQUIRED_SOURCE_FILES)
        != crypto_collector.REQUIRED_SOURCE_FILE_REFS
    ):
        return _crypto_failure_integration(REASON_CRYPTO_SOURCE_SCOPE_MISMATCH)
    try:
        before_audit = _read_crypto_source_snapshot_v01(artifact_dir)
    except (TypeError, ValueError, OSError):
        return _crypto_failure_integration(REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED)

    audit_count = 1
    try:
        audit_report = (
            ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01(
                artifact_dir=artifact_dir,
            )
        )
    except Exception:
        return _crypto_failure_integration(
            REASON_CRYPTO_E1_AUDIT_FAILED,
            e1_audit_count=audit_count,
        )
    try:
        after_audit = _read_crypto_source_snapshot_v01(artifact_dir)
    except (TypeError, ValueError, OSError):
        return _crypto_failure_integration(
            REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED,
            e1_audit_count=audit_count,
        )
    if after_audit != before_audit:
        return _crypto_failure_integration(
            REASON_CRYPTO_SOURCE_BYTES_CHANGED_DURING_AUDIT,
            e1_audit_count=audit_count,
        )
    try:
        accepted_audit = _project_e1_audit_for_crypto_v01(
            audit_report,
            artifact_dir=artifact_dir,
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError):
        reason = (
            REASON_CRYPTO_E1_AUDIT_FOREIGN_DIR
            if type(audit_report)
            is ledger_audit.AirlineTransactionArtifactLedgerAuditReportV01
            and Path(audit_report.source_artifact_dir) != artifact_dir
            else REASON_CRYPTO_E1_AUDIT_FAILED
        )
        return _crypto_failure_integration(reason, e1_audit_count=audit_count)

    if integrated_deterministic_report is None:
        return _crypto_failure_integration(
            REASON_CRYPTO_TYPED_SOURCE_MISSING,
            e1_audit_count=audit_count,
            source_bytes_unchanged_after_audit=True,
        )
    typed_source_bundle = getattr(
        integrated_deterministic_report,
        "_airline_transaction_artifact_ledger_source_bundle_v0_1",
        None,
    )
    typed_ledger = getattr(
        integrated_deterministic_report,
        "_airline_transaction_artifact_ledger_v0_1",
        None,
    )
    if (
        type(typed_source_bundle)
        is not ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01
        or type(typed_ledger)
        is not ledger_contracts.AirlineTransactionArtifactLedgerV01
    ):
        return _crypto_failure_integration(
            REASON_CRYPTO_TYPED_SOURCE_MISSING,
            e1_audit_count=audit_count,
            source_bytes_unchanged_after_audit=True,
        )
    try:
        expected_identity = (
            ledger_collector
            .build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
                source_bundle=typed_source_bundle,
            )
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError):
        return _crypto_failure_integration(
            REASON_CRYPTO_EXPECTED_IDENTITY_FAILED,
            e1_audit_count=audit_count,
            source_bytes_unchanged_after_audit=True,
        )
    source_package_ref = artifact_dir.name
    source_bundle_id = (
        "airline_crypto_artifact_seal_source_bundle:"
        f"{typed_ledger.transaction_id}:{source_package_ref}"
    )
    try:
        crypto_source_bundle = (
            crypto_collector.build_airline_crypto_artifact_seal_source_bundle_v01(
                source_bundle_id=source_bundle_id,
                source_package_ref=source_package_ref,
                accepted_audit=accepted_audit,
                ledger_item=typed_ledger,
                expected_identity=expected_identity,
                ordered_source_files_before_audit=before_audit,
                ordered_source_files_after_audit=after_audit,
            )
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError):
        return _crypto_failure_integration(
            REASON_CRYPTO_C1_SOURCE_BUNDLE_FAILED,
            source_bundle_id=source_bundle_id,
            source_package_ref=source_package_ref,
            e1_audit_count=audit_count,
            source_bytes_unchanged_after_audit=True,
        )

    def post_collection_snapshot_provider() -> object:
        return _read_crypto_source_snapshot_v01(artifact_dir)

    try:
        collection_result = (
            crypto_collector.collect_airline_crypto_artifact_seal_from_source_bundle_v01(
                source_bundle=crypto_source_bundle,
                post_collection_snapshot_provider=post_collection_snapshot_provider,
                expected_manifest_core_hash=None,
            )
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, OSError):
        return _crypto_failure_integration(
            REASON_CRYPTO_C2_COLLECTION_FAILED,
            source_bundle_id=source_bundle_id,
            source_package_ref=source_package_ref,
            e1_audit_count=audit_count,
            source_bytes_unchanged_after_audit=True,
        )
    if not _crypto_collection_successful(collection_result):
        return _crypto_failure_integration(
            REASON_CRYPTO_C2_RESULT_INVALID,
            source_bundle_id=source_bundle_id,
            source_package_ref=source_package_ref,
            e1_audit_count=audit_count,
            source_bytes_unchanged_after_audit=True,
        )
    collection_plain = (
        crypto_collector
        .airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
            collection_result,
        )
    )
    manifest_payload = collection_plain.get("envelope")
    verification_payload = collection_plain.get("verification_report")
    try:
        manifest_path, verification_path = _write_crypto_artifact_pair_v01(
            artifact_dir=artifact_dir,
            manifest_payload=manifest_payload,
            verification_payload=verification_payload,
        )
    except (TypeError, ValueError, OSError) as exc:
        return _crypto_failure_integration(
            _crypto_exception_reason(exc, REASON_CRYPTO_DERIVED_WRITE_FAILED),
            source_bundle_id=source_bundle_id,
            source_package_ref=source_package_ref,
            e1_audit_count=audit_count,
            source_bundle_validation_count=1,
            manifest_core_collection_count=1,
            envelope_collection_count=1,
            post_collection_snapshot_provider_call_count=1,
            verification_count=1,
            source_bytes_unchanged_after_audit=True,
            source_bytes_unchanged_after_collection=True,
            source_summary_frozen_before_crypto=True,
        )
    artifacts[CRYPTO_MANIFEST_FILE] = str(manifest_path)
    artifacts[CRYPTO_VERIFICATION_FILE] = str(verification_path)
    try:
        after_write = _read_crypto_source_snapshot_v01(artifact_dir)
    except (TypeError, ValueError, OSError):
        cleanup_succeeded = _cleanup_crypto_artifact_paths_v01(
            (manifest_path, verification_path),
        )
        artifacts.pop(CRYPTO_MANIFEST_FILE, None)
        artifacts.pop(CRYPTO_VERIFICATION_FILE, None)
        return _crypto_failure_integration(
            (
                REASON_CRYPTO_SOURCE_SNAPSHOT_FAILED
                if cleanup_succeeded
                else REASON_CRYPTO_DERIVED_CLEANUP_FAILED
            ),
            e1_audit_count=audit_count,
            source_bundle_validation_count=1,
            manifest_core_collection_count=1,
            envelope_collection_count=1,
            post_collection_snapshot_provider_call_count=1,
            verification_count=1,
            manifest_artifact_written_count=1,
            verification_artifact_written_count=1,
            source_bytes_unchanged_after_audit=True,
            source_bytes_unchanged_after_collection=True,
            source_summary_frozen_before_crypto=True,
        )
    if after_write != before_audit:
        cleanup_succeeded = _cleanup_crypto_artifact_paths_v01(
            (manifest_path, verification_path),
        )
        artifacts.pop(CRYPTO_MANIFEST_FILE, None)
        artifacts.pop(CRYPTO_VERIFICATION_FILE, None)
        return _crypto_failure_integration(
            (
                REASON_CRYPTO_SOURCE_BYTES_CHANGED_AFTER_WRITE
                if cleanup_succeeded
                else REASON_CRYPTO_DERIVED_CLEANUP_FAILED
            ),
            e1_audit_count=audit_count,
            source_bundle_validation_count=1,
            manifest_core_collection_count=1,
            envelope_collection_count=1,
            post_collection_snapshot_provider_call_count=1,
            verification_count=1,
            manifest_artifact_written_count=1,
            verification_artifact_written_count=1,
            source_bytes_unchanged_after_audit=True,
            source_bytes_unchanged_after_collection=True,
            source_summary_frozen_before_crypto=True,
        )
    manifest_core = collection_result.manifest_core
    verification_report = collection_result.verification_report
    assert manifest_core is not None
    assert verification_report is not None
    return {
        "integration_status": crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED,
        "source_bundle_id": source_bundle_id,
        "source_package_ref": source_package_ref,
        "ledger_id": manifest_core.ledger_id,
        "transaction_id": manifest_core.transaction_id,
        "manifest_core_hash": collection_result.manifest_core_hash,
        "chain_tail_hash": manifest_core.chain_tail_hash,
        "source_package_hash": manifest_core.source_package_hash,
        "ledger_entry_count": manifest_core.ledger_entry_count,
        "dependency_edge_count": manifest_core.dependency_edge_count,
        "root_final_count": manifest_core.root_final_count,
        "source_file_count": manifest_core.source_file_count,
        "e1_audit_count": audit_count,
        "source_bundle_validation_count": collection_result.source_bundle_validation_count,
        "manifest_core_collection_count": collection_result.manifest_core_collection_count,
        "envelope_collection_count": collection_result.envelope_collection_count,
        "post_collection_snapshot_provider_call_count": (
            collection_result.post_collection_snapshot_provider_call_count
        ),
        "verification_count": collection_result.verification_count,
        "manifest_artifact_written_count": 1,
        "verification_artifact_written_count": 1,
        "source_bytes_unchanged_after_audit": True,
        "source_bytes_unchanged_after_collection": (
            collection_result.source_bytes_unchanged_after_collection
        ),
        "source_bytes_unchanged_after_write": True,
        "source_summary_frozen_before_crypto": True,
        "source_summary_rewritten_after_crypto": False,
        "expected_manifest_core_hash": None,
        "external_anchor_supplied": verification_report.external_anchor_supplied,
        "external_anchor_verified": verification_report.external_anchor_verified,
        "anchored_pass_claimed": False,
        "signature_mode": verification_report.signature_mode,
        "signature_verified": verification_report.signature_verified,
        "audit_rerun_count": 0,
        "ledger_recollection_count": 0,
        "semantic_rerun_count": 0,
        "corridor_rerun_count": 0,
        "provider_calls_added_by_crypto_count": 0,
        "network_calls_added_by_crypto_count": 0,
        "gemini_calls_added_by_crypto_count": 0,
        "crypto_created_authority_count": 0,
        "crypto_created_permission_count": 0,
        "crypto_created_action_count": 0,
        "real_world_effects_count": 0,
        "manifest_artifact_ref": CRYPTO_MANIFEST_FILE,
        "verification_artifact_ref": CRYPTO_VERIFICATION_FILE,
        "validation_errors": (),
        "next_gate": CRYPTO_NEXT_GATE,
    }


def _integrated_ledger(
    deterministic_report: Mapping[str, Any] | None,
) -> Any:
    if deterministic_report is None:
        return None
    typed_ledger = getattr(
        deterministic_report,
        "_airline_transaction_artifact_ledger_v0_1",
        None,
    )
    if typed_ledger is not None:
        return typed_ledger
    return deterministic_report.get("airline_transaction_artifact_ledger_v0_1")


def _integrated_ledger_summary(
    deterministic_report: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if deterministic_report is None:
        return _not_run_ledger_summary()
    summary = deterministic_report.get(
        "airline_transaction_artifact_ledger_integration",
    )
    if isinstance(summary, MappingABC):
        return dict(summary)
    return _not_run_ledger_summary()


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
    ledger_summary = report.get("airline_transaction_artifact_ledger_integration", {})
    if not isinstance(ledger_summary, MappingABC):
        ledger_summary = {}
    return {
        "semantic_actor_call_count": len(actor_reports),
        "causal_semantic_actor_call_count": causal_actor_count,
        "generic_semantic_actor_call_count": len(actor_reports) - causal_actor_count,
        "local_injected_semantic_callback_count": (
            causal_actor_count if provider_mode == PROVIDER_MODE_FAKE else 0
        ),
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
        "airline_transaction_artifact_ledger_source_bundle_collection_count": int(
            ledger_summary.get("source_bundle_collection_count", 0),
        ),
        "airline_transaction_artifact_ledger_source_bundle_pass_count": int(
            ledger_summary.get("source_bundle_validation_status") == STATUS_PASS,
        ),
        "airline_transaction_artifact_ledger_collection_count": int(
            ledger_summary.get("ledger_collection_count", 0),
        ),
        "airline_transaction_artifact_ledger_validation_count": int(
            ledger_summary.get("ledger_validation_count", 0),
        ),
        "airline_transaction_artifact_ledger_pass_count": int(
            ledger_summary.get("ledger_validation_status") == STATUS_PASS,
        ),
        "airline_transaction_artifact_ledger_entry_count": int(
            ledger_summary.get("entry_count", 0),
        ),
        "airline_transaction_artifact_ledger_dependency_edge_count": int(
            ledger_summary.get("dependency_edge_count", 0),
        ),
        "airline_transaction_artifact_ledger_root_final_count": int(
            ledger_summary.get("root_final_count", 0),
        ),
        "airline_transaction_artifact_ledger_duplicate_collection_count": int(
            ledger_summary.get("duplicate_ledger_collection_count", 0),
        ),
        "airline_transaction_artifact_ledger_duplicate_corridor_execution_count": int(
            ledger_summary.get("duplicate_corridor_execution_count", 0),
        ),
        "airline_transaction_artifact_ledger_duplicate_transaction_count": int(
            ledger_summary.get("duplicate_transaction_count", 0),
        ),
        "airline_transaction_artifact_ledger_source_reconstruction_count": int(
            ledger_summary.get("source_reconstruction_count", 0),
        ),
        "airline_transaction_artifact_ledger_provider_calls_added_count": int(
            ledger_summary.get("provider_calls_added_by_ledger_count", 0),
        ),
        "airline_transaction_artifact_ledger_network_calls_added_count": int(
            ledger_summary.get("network_calls_added_by_ledger_count", 0),
        ),
        "airline_transaction_artifact_ledger_gemini_calls_added_count": int(
            ledger_summary.get("gemini_calls_added_by_ledger_count", 0),
        ),
        "airline_transaction_artifact_ledger_created_authority_count": int(
            ledger_summary.get("ledger_created_authority_count", 0),
        ),
        "airline_transaction_artifact_ledger_created_permission_count": int(
            ledger_summary.get("ledger_created_permission_count", 0),
        ),
        "airline_transaction_artifact_ledger_created_action_count": int(
            ledger_summary.get("ledger_created_action_count", 0),
        ),
        "airline_transaction_artifact_ledger_artifact_written_count": int(
            ledger_summary.get("artifact_written_count", 0),
        ),
        "airline_transaction_artifact_ledger_real_world_effects_count": int(
            ledger_summary.get("real_world_effects_count", 0),
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
        "local_injected_semantic_callback_count",
        "duplicate_semantic_actor_call_count",
        "precollected_causal_run_count",
        "provider_calls_inside_precollected_runtime_count",
        "causal_report_pass_count",
        "deterministic_airline_collection_count",
        "deterministic_airline_pass_count",
        "ticket_purchase_corridor_execution_count",
        "ticket_purchase_corridor_pass_count",
        "airline_transaction_artifact_ledger_source_bundle_collection_count",
        "airline_transaction_artifact_ledger_source_bundle_pass_count",
        "airline_transaction_artifact_ledger_collection_count",
        "airline_transaction_artifact_ledger_validation_count",
        "airline_transaction_artifact_ledger_pass_count",
        "airline_transaction_artifact_ledger_entry_count",
        "airline_transaction_artifact_ledger_dependency_edge_count",
        "airline_transaction_artifact_ledger_root_final_count",
        "airline_transaction_artifact_ledger_duplicate_collection_count",
        "airline_transaction_artifact_ledger_duplicate_corridor_execution_count",
        "airline_transaction_artifact_ledger_duplicate_transaction_count",
        "airline_transaction_artifact_ledger_source_reconstruction_count",
        "airline_transaction_artifact_ledger_provider_calls_added_count",
        "airline_transaction_artifact_ledger_network_calls_added_count",
        "airline_transaction_artifact_ledger_gemini_calls_added_count",
        "airline_transaction_artifact_ledger_created_authority_count",
        "airline_transaction_artifact_ledger_created_permission_count",
        "airline_transaction_artifact_ledger_created_action_count",
        "airline_transaction_artifact_ledger_artifact_written_count",
        "airline_transaction_artifact_ledger_real_world_effects_count",
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


ROOT_FINAL_ARTIFACT_TYPES = (
    "ClientRootFinalV01",
    "AirlineRootFinalV01",
    "BankRootFinalV01",
)


def _ledger_actual_geometry_is_valid(ledger: Any) -> bool:
    entries = tuple(getattr(ledger, "entries", ()))
    artifact_type_sequence = tuple(
        getattr(entry, "artifact_type", "") for entry in entries
    )
    root_final_counts = {
        artifact_type: artifact_type_sequence.count(artifact_type)
        for artifact_type in ROOT_FINAL_ARTIFACT_TYPES
    }
    actual_entry_count = len(entries)
    actual_dependency_edge_count = sum(
        len(getattr(entry, "depends_on", ())) for entry in entries
    )
    actual_root_final_count = sum(
        1 for artifact_type in artifact_type_sequence
        if artifact_type in ROOT_FINAL_ARTIFACT_TYPES
    )
    return (
        getattr(ledger, "validation_status", "") == STATUS_PASS
        and getattr(ledger, "validation_errors", None) == ()
        and artifact_type_sequence
        == deterministic_airline.ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
        and all(count == 1 for count in root_final_counts.values())
        and actual_entry_count == 19
        and actual_dependency_edge_count == 29
        and actual_root_final_count == 3
        and getattr(ledger, "entry_count", None) == actual_entry_count
        and getattr(
            ledger,
            "dependency_edge_count",
            None,
        ) == actual_dependency_edge_count
        and getattr(ledger, "root_final_count", None) == actual_root_final_count
    )


def _prepare_airline_transaction_artifact_ledger_json(
    artifact_dir: Path | None,
    report: dict[str, Any],
) -> tuple[str, str]:
    if artifact_dir is None:
        return "", ""
    summary = report.get("airline_transaction_artifact_ledger_integration", {})
    ledger = report.get("airline_transaction_artifact_ledger_v0_1")
    if (
        report.get("final_status") != STATUS_PASS
        or not isinstance(summary, dict)
        or summary.get("integration_status") != STATUS_PASS
        or summary.get("source_bundle_validation_status") != STATUS_PASS
        or summary.get("ledger_validation_status") != STATUS_PASS
        or ledger is None
    ):
        return "", ""
    if not _ledger_actual_geometry_is_valid(ledger):
        return "", "airline_transaction_artifact_ledger_actual_geometry_mismatch"
    try:
        return json.dumps(_json_safe(ledger), indent=2, sort_keys=True), ""
    except (TypeError, ValueError):
        return "", "airline_transaction_artifact_ledger_serialization_failed"


def _write_airline_transaction_artifact_ledger_once(
    artifact_dir: Path | None,
    report: dict[str, Any],
    artifacts: dict[str, Any],
    *,
    ledger_json: str,
) -> str:
    if artifact_dir is None or not ledger_json:
        return ""
    summary = report.get("airline_transaction_artifact_ledger_integration", {})
    if (
        report.get("final_status") != STATUS_PASS
        or not isinstance(summary, dict)
        or summary.get("integration_status") != STATUS_PASS
    ):
        return ""
    path = artifact_dir / "airline_transaction_artifact_ledger.json"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(ledger_json)
    except FileExistsError:
        return "airline_transaction_artifact_ledger_duplicate_write_blocked"
    except OSError:
        return "airline_transaction_artifact_ledger_write_failed"
    artifacts["airline_transaction_artifact_ledger.json"] = str(path)
    summary["artifact_written_count"] = 1
    return ""


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
    *,
    additional_texts: tuple[str, ...] = (),
) -> dict[str, Any]:
    scanned = [json.dumps(_json_safe(report), sort_keys=True)]
    scanned.extend(additional_texts)
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
        return {
            field.name: _json_safe(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, MappingABC):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


if __name__ == "__main__":
    raise SystemExit(main())
