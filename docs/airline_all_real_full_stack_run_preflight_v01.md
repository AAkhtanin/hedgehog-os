# Airline All-Real Full-Stack Run v0.1 Preflight

- document_id: airline_all_real_full_stack_run_preflight_v01
- document_status: PREFLIGHT
- preflight_status: READY_FOR_REVIEW
- observed_base_head: a8d5036
- implementation_base_head: a8d5036
- planning_only: true
- runtime_modified: false
- tests_modified: false
- schemas_modified: false
- specifications_modified: false
- official_run_performed: false
- provider_called: false
- network_called: false
- gemini_called: false
- package_created: false
- anchor_created: false
- replay_performed: false
- audit_created: false
- human_story_created: false
- real_airline_api_called: false
- real_bank_api_called: false
- real_gds_api_called: false
- real_payment_executed: false
- real_booking_created: false
- real_ticket_issued: false
- real_world_effects_count: 0
- production_ready_claimed: false
- root_attestation_activated: false

This preflight plans the final proof-level all-real Airline demonstration.
It does not execute it.

## Closed Basis

The following layers remain closed and are not reopened by this preflight:

- Airline 12-actor real-provider semantic lane: previously `PASS`.
- Airline semantic-to-contract causal binding: `CLOSED / PASS`.
- Ticket/Purchase Corridor: `CLOSED / PASS`.
- Transaction Artifact Ledger: `CLOSED / PASS`.
- Crypto Artifact Seal: `CLOSED / PASS`.
- Base Sealed Trace Replay: `CLOSED / PASS`.
- Root Attestation: deferred and not required.
- Current implementation basis: `a8d5036`.

A new run is required because the earlier twelve-real-Gemini run proved real
semantic participation and the deterministic Corridor before the current
Ledger, Crypto, and Replay layers existed. The existing official Crypto and
Replay package was generated through the deterministic injected-provider path.
The final showcase therefore needs one new package that combines real
twelve-actor semantics with every subsequently closed proof layer. This is a
new evidence assembly over closed contracts, not a reopening or replacement
of any layer.

## Exact Purpose

The final program demonstrates one complete proof-level transaction:

```text
fixed user travel task
-> 12 real Gemini bounded semantic actors
-> BSEP before Architect
-> validated canonical semantic evidence
-> ClientRoot decision
-> AirlineRoot authoritative offer resolution
-> deterministic five-phase Ticket/Purchase Corridor
-> mock hold/payment/ticket/PNR/receipt evidence
-> exact-source Ledger
-> Crypto Manifest and stored unanchored Verification
-> committed external Manifest Core anchor
-> fresh anchored verification
-> deterministic Sealed Trace Replay
-> independent audit
-> artifact-backed human story
-> canonical docs closure
```

This is one proof-level transaction. It is not:

- a second architecture;
- a new universal runner;
- a new Crypto layer;
- a new Replay layer;
- a Root Attestation implementation;
- a production connector integration.

## Fixed Official Scenario

- Semantic profile: Preference A.
- Transaction:
  `tri_airline_purchase:PAR-LIM:2026-08-12:client_001`.
- Expected selected offer:
  `offer:mock_airline_al:PAR-LIM:001`.
- ClientRoot: `root:client_os_001`.
- AirlineRoot: `root:mock_airline_al`.
- BankRoot: `root:mock_bank_a`.
- Resolved committed real-provider default model: `gemini-2.5-flash`.

An all-real Preference B run is not required. Deterministic and
injected-provider A/B counterfactual isolation is already closed. The final
showcase requires one coherent all-real transaction rather than a 24-call
real-provider matrix, and it will make no real-provider A/B causal-comparison
claim. Preference A must not be silently changed.

## Exact Actor Program

The current committed live-lane `ACTOR_SPECS` order is:

1. `tri_party_airline_orchestrator_llm`
2. `tri_party_airline_semantic_architect_llm`
3. `client_purchase_intent_reviewer_llm`
4. `client_profile_privacy_reviewer_llm`
5. `airline_offer_policy_reviewer_llm`
6. `airline_fare_rules_vertical_cell_llm`
7. `airline_seat_baggage_vertical_cell_llm`
8. `airline_ticketing_policy_reviewer_llm`
9. `bank_payment_policy_reviewer_llm`
10. `bank_idempotency_risk_vertical_cell_llm`
11. `bank_payment_status_explainer_llm`
12. `tri_party_evidence_consistency_reviewer_llm`

This list matches the expected topology exactly; there is no current naming
difference. The five causal-runtime actors are:

- `client_purchase_intent_reviewer_llm`
- `airline_offer_policy_reviewer_llm`
- `airline_fare_rules_vertical_cell_llm`
- `airline_seat_baggage_vertical_cell_llm`
- `tri_party_evidence_consistency_reviewer_llm`

Required counters are:

- `semantic_actor_call_count: 12`
- `causal_semantic_actor_call_count: 5`
- `generic_semantic_actor_call_count: 7`
- `duplicate_semantic_actor_call_count: 0`
- `real_provider_call_count: 12`
- `fake_provider_call_count: 0`
- `network_used_count: 12`
- `gemini_called_count: 12`

Every actor must produce the current exact local artifact package:

- bounded prompt;
- raw provider response;
- extracted JSON candidate;
- validation report;
- canonical summary.

Raw responses remain local under `.tmp`. They are not printed to the
terminal, committed, copied into audit or human documents, or exempted from
secret scanning.

## Frozen Official Identity And Paths

The future owner session must define these values once and use them without
search, substitution, or fallback:

```sh
OFFICIAL_PACKAGE='.tmp/airline_all_real_full_stack_v01/airline_all_real_full_stack_v01_preference_a_a8d5036'
OFFICIAL_PACKAGE_ROOT="${OFFICIAL_PACKAGE%/*}"
OFFICIAL_PACKAGE_REF="${OFFICIAL_PACKAGE##*/}"
TERMINAL_SAFE_LOG="${OFFICIAL_PACKAGE_ROOT}/${OFFICIAL_PACKAGE_REF}_terminal_safe.log"
OPERATOR_GATE_JSON="${OFFICIAL_PACKAGE_ROOT}/${OFFICIAL_PACKAGE_REF}_operator_gate.json"
FUTURE_ANCHOR='docs/airline_all_real_full_stack_crypto_anchor_v01.json'
GENERATION_ANCHOR_AUDIT='docs/audit_reports/auditor_airline_all_real_full_stack_v01_generation_anchor_publication.log'
FUTURE_REPLAY_REPORT='docs/airline_all_real_full_stack_replay_report_v01.json'
FINAL_REPLAY_AUDIT='docs/audit_reports/auditor_airline_all_real_full_stack_v01_anchored_replay.log'
FUTURE_HUMAN_STORY='docs/airline_all_real_full_stack_human_story_v01.md'
FUTURE_CHECKPOINT='docs/airline_all_real_full_stack_checkpoint_v01.md'
```

The package path must be absent before invocation. Its final component must
not be a symlink, the directory must not be reused, and no overwrite is
allowed. The parent may exist. There is no package discovery, latest-package
selection, fallback package, or retry into the same path. The terminal-safe
log and operator gate are outside the package and are not part of the sealed
eleven-file critical surface.

The `a8d5036` package-ref suffix identifies the frozen implementation basis.
It is not a substitute for the actual synchronized Git commit observed during
the future owner-terminal invocation. That execution commit is captured
separately in the operator gate and later becomes the anchor's
`package_generation_base_head`.

## Current Live-Runner Contract

The current public entrypoint is:

```python
collect_tri_party_airline_live_semantic_lane_v01(
    *,
    env: Mapping[str, str] | None = None,
    provider: Provider | None = None,
    causal_constraints: ClientRootTravelConstraintSetV01 | None = None,
    causal_snapshot: AirlineRootOfferCandidateSetSnapshotV01 | None = None,
) -> dict[str, Any]
```

The ordinary module `main()` cannot supply the exact Preference A constraints
and authoritative candidate snapshot, so the future official command must use
the public collector directly. It must pass:

- `build_client_constraints_preference_a_v01()`
- `build_airline_candidate_snapshot_v01()`

The current environment contract is:

- `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_LANE=1`
- `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_REAL_PROVIDER=1`
- `HEDGEHOG_AIRLINE_SEMANTIC_TO_CONTRACT_CAUSAL_BINDING=1`
- `HEDGEHOG_AIRLINE_CRYPTO_ARTIFACT_SEAL=1`
- `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ARTIFACT_DIR=$OFFICIAL_PACKAGE`
- `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_MODEL=gemini-2.5-flash`
- `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ALLOW_RAW_RESPONSE_OUTPUT=0`
- `HEDGEHOG_AIRLINE_LIVE_SEMANTIC_CALL_DELAY_SECONDS=2`

The provider adapter checks these credential variable names in exact order:

1. `HEDGEHOG_GEMINI_API_KEY`
2. `GOOGLE_API_KEY`
3. `GEMINI_API_KEY`
4. `GOOGLE_GEMINI_API_KEY`

The readiness gate checks only that at least one current credential variable
is non-empty. It never prints a value, writes a value, places a value in a
prompt, places a value in Git, or includes a credential assignment in the
official command.

## Owner-Terminal Rule

The official all-real transaction invocation is executed only by the repository owner in the owner's visible terminal.

Codex may inspect code, write this preflight, prepare later read-only
validation commands, and prepare later audit, human, and documentation updates
from accepted artifacts. Codex may not execute or retry the official
real-provider run, choose another package, publish an anchor before visible
operator validation, or run the official anchored Replay.

The evidence source of truth is:

```text
owner terminal command
-> visible output
-> actual local files
-> owner-terminal validation
-> audit/anchor publication
```

## Operator Readiness Gate

This block is planned for the future owner session. It is read-only and makes
no provider call:

```sh
set -eu

test -n "${OFFICIAL_PACKAGE:-}"
test -n "${OFFICIAL_PACKAGE_ROOT:-}"
test -n "${OFFICIAL_PACKAGE_REF:-}"
test -n "${TERMINAL_SAFE_LOG:-}"
test -n "${OPERATOR_GATE_JSON:-}"
test -n "${FUTURE_ANCHOR:-}"
test -n "${GENERATION_ANCHOR_AUDIT:-}"
test -n "${FUTURE_REPLAY_REPORT:-}"
test -n "${FINAL_REPLAY_AUDIT:-}"
test -n "${FUTURE_HUMAN_STORY:-}"
test -n "${FUTURE_CHECKPOINT:-}"

execution_head="$(git rev-parse --short HEAD)"
execution_origin_main="$(git rev-parse --short origin/main)"
test "$execution_head" = "$execution_origin_main"
test -z "$(git status --short --untracked-files=all)"
test -z "$(git diff --cached --name-only)"
git ls-files --error-unmatch \
  docs/airline_all_real_full_stack_run_preflight_v01.md >/dev/null

test ! -e "$OFFICIAL_PACKAGE"
test ! -L "$OFFICIAL_PACKAGE"
test ! -e "$TERMINAL_SAFE_LOG"
test ! -L "$TERMINAL_SAFE_LOG"
test ! -e "$OPERATOR_GATE_JSON"
test ! -L "$OPERATOR_GATE_JSON"
test ! -e "$FUTURE_ANCHOR"
test ! -L "$FUTURE_ANCHOR"
test ! -e "$FUTURE_REPLAY_REPORT"
test ! -L "$FUTURE_REPLAY_REPORT"
test ! -e "$GENERATION_ANCHOR_AUDIT"
test ! -L "$GENERATION_ANCHOR_AUDIT"
test ! -e "$FINAL_REPLAY_AUDIT"
test ! -L "$FINAL_REPLAY_AUDIT"
test ! -e "$FUTURE_HUMAN_STORY"
test ! -L "$FUTURE_HUMAN_STORY"
test ! -e "$FUTURE_CHECKPOINT"
test ! -L "$FUTURE_CHECKPOINT"

test -x .venv/bin/python
python3 -m json.tool specs/machine_manifest_v0_25.json >/dev/null

PYTHONPATH=. .venv/bin/python - <<'PY'
import os

credential_names = (
    "HEDGEHOG_GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_GEMINI_API_KEY",
)
raise SystemExit(
    0
    if any(os.environ.get(name, "").strip() for name in credential_names)
    else 1
)
PY

PYTHONPATH=. .venv/bin/python - <<'PY'
from demo import run_tri_party_airline_live_semantic_lane_v01
from demo import run_airline_transaction_artifact_ledger_audit_v01
from demo import run_airline_sealed_trace_replay_v01
from hedgehog.domains.airline import crypto_artifact_seal_v01
from hedgehog.domains.airline import crypto_artifact_seal_collector_v01
from hedgehog.domains.airline import semantic_to_contract_binding_v01
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01
from hedgehog.domains.airline import ticket_purchase_corridor_runtime_v01
from hedgehog.domains.airline import transaction_artifact_ledger_v01
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01

print("offline_import_gate: PASS")
PY
```

The readiness block records the synchronized execution commit independently
of the frozen implementation basis. Closed test evidence is the readiness
basis; this gate does not prescribe a second package-generation smoke or full
`pytest`.

## Exact Official Invocation Block

The future official invocation count is exactly one.

The owner runs the following block in the same shell after the readiness gate.
It calls the committed collector once, catches exceptions without printing
their text, writes only a bounded operator gate outside the package, and emits
one terminal-safe JSON object:

```sh
set -eu
set -o pipefail

execution_head="$(git rev-parse --short HEAD)"
execution_origin_main="$(git rev-parse --short origin/main)"
test "$execution_head" = "$execution_origin_main"
test -z "$(git status --short --untracked-files=all)"
test -z "$(git diff --cached --name-only)"
git ls-files --error-unmatch \
  docs/airline_all_real_full_stack_run_preflight_v01.md >/dev/null

if [ -e "$OFFICIAL_PACKAGE_ROOT" ] || [ -L "$OFFICIAL_PACKAGE_ROOT" ]; then
  test ! -L "$OFFICIAL_PACKAGE_ROOT"
  test -d "$OFFICIAL_PACKAGE_ROOT"
fi
test ! -e "$OFFICIAL_PACKAGE"
test ! -L "$OFFICIAL_PACKAGE"
test ! -e "$TERMINAL_SAFE_LOG"
test ! -L "$TERMINAL_SAFE_LOG"
test ! -e "$OPERATOR_GATE_JSON"
test ! -L "$OPERATOR_GATE_JSON"

mkdir -p "$OFFICIAL_PACKAGE_ROOT"

export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_LANE=1
export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_REAL_PROVIDER=1
export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_FAKE_PROVIDER=0
export HEDGEHOG_AIRLINE_SEMANTIC_TO_CONTRACT_CAUSAL_BINDING=1
export HEDGEHOG_AIRLINE_CRYPTO_ARTIFACT_SEAL=1
export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ARTIFACT_DIR="$OFFICIAL_PACKAGE"
export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_MODEL='gemini-2.5-flash'
export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ALLOW_RAW_RESPONSE_OUTPUT=0
export HEDGEHOG_AIRLINE_LIVE_SEMANTIC_CALL_DELAY_SECONDS=2
export HEDGEHOG_AIRLINE_ALL_REAL_OPERATOR_GATE_JSON="$OPERATOR_GATE_JSON"
export HEDGEHOG_AIRLINE_ALL_REAL_OFFICIAL_ROOT="$OFFICIAL_PACKAGE_ROOT"
export HEDGEHOG_AIRLINE_ALL_REAL_PACKAGE_REF="$OFFICIAL_PACKAGE_REF"
export HEDGEHOG_AIRLINE_ALL_REAL_EXECUTION_HEAD="$execution_head"
export HEDGEHOG_AIRLINE_ALL_REAL_EXECUTION_ORIGIN_MAIN="$execution_origin_main"

PYTHONPATH=. .venv/bin/python - <<'PY' | tee "$TERMINAL_SAFE_LOG"
import hashlib
import json
import os
from pathlib import Path

from demo import run_tri_party_airline_live_semantic_lane_v01 as live_lane
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay_contracts
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding

EXPECTED_ACTORS = (
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
EXPECTED_TRANSACTION = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"
EXPECTED_OFFER = "offer:mock_airline_al:PAR-LIM:001"
EXPECTED_MODEL = "gemini-2.5-flash"
IMPLEMENTATION_BASE_HEAD = "a8d5036"

package_dir = Path(os.environ[live_lane.ENV_ARTIFACT_DIR])
package_root = Path(os.environ["HEDGEHOG_AIRLINE_ALL_REAL_OFFICIAL_ROOT"])
gate_path = Path(os.environ["HEDGEHOG_AIRLINE_ALL_REAL_OPERATOR_GATE_JSON"])
execution_head = os.environ["HEDGEHOG_AIRLINE_ALL_REAL_EXECUTION_HEAD"]
execution_origin_main = os.environ[
    "HEDGEHOG_AIRLINE_ALL_REAL_EXECUTION_ORIGIN_MAIN"
]
source_package_ref = os.environ["HEDGEHOG_AIRLINE_ALL_REAL_PACKAGE_REF"]
source_package_relpath = package_dir.as_posix()

def exact_int(mapping, field_name, expected):
    value = mapping.get(field_name)
    return type(value) is int and value == expected

try:
    report = live_lane.collect_tri_party_airline_live_semantic_lane_v01(
        env=os.environ,
        causal_constraints=binding.build_client_constraints_preference_a_v01(),
        causal_snapshot=binding.build_airline_candidate_snapshot_v01(),
    )

    counters = report.get("counter_table", {})
    bridge = report.get("semantic_to_contract_deterministic_bridge", {})
    ledger = report.get("airline_transaction_artifact_ledger_integration", {})
    crypto = report.get("airline_crypto_artifact_seal_integration", {})
    actor_reports = tuple(report.get("semantic_actor_reports", ()))
    projections = report.get("bsep_side_projections", {})
    root_boundaries = tuple(report.get("root_boundaries", ()))
    actor_order = tuple(report.get("semantic_actor_call_order", ()))
    architect_report = actor_reports[1] if len(actor_reports) > 1 else {}
    bsep_packet = report.get("bsep_membrane", {})
    bsep_validation = report.get("bsep_validation", {})
    secret_scan = report.get("secret_scan", {})
    critical_refs = crypto_contracts.REQUIRED_SOURCE_FILE_REFS + (
        replay_contracts.MANIFEST_ARTIFACT_REF,
        replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
    )
    expected_actor_files = tuple(
        f"{actor_id}_{suffix}"
        for actor_id in EXPECTED_ACTORS
        for suffix in (
            "prompt.txt",
            "raw_response.txt",
            "extracted_json_candidate.json",
            "validation.json",
            "canonical_summary.json",
        )
    )

    package_entries = tuple(sorted(package_dir.iterdir()))
    package_files = tuple(
        path
        for path in package_entries
        if path.is_file() and not path.is_symlink()
    )
    sha256_inventory = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in package_files
    }
    unexpected_package_dirs = tuple(
        sorted(
            path.name
            for path in package_root.iterdir()
            if path.is_dir() and path != package_dir
        )
    )

    checks = {
        "final_status_pass": report.get("final_status") == live_lane.STATUS_PASS,
        "provider_mode_real": report.get("provider_mode") == live_lane.PROVIDER_MODE_REAL,
        "model_exact": report.get("model") == EXPECTED_MODEL,
        "transaction_exact": report.get("transaction_id") == EXPECTED_TRANSACTION,
        "actor_order_exact": actor_order == EXPECTED_ACTORS,
        "actor_order_begins_orchestrator_then_architect": (
            actor_order[:2] == EXPECTED_ACTORS[:2]
        ),
        "all_actor_validations_pass": (
            len(actor_reports) == 12
            and all(
                item.get("validation_status") == live_lane.STATUS_PASS
                and item.get("accepted") is True
                for item in actor_reports
            )
        ),
        "actor_validation_and_file_counters_exact": (
            exact_int(counters, "semantic_actor_validation_pass_count", 12)
            and exact_int(counters, "semantic_actor_validation_fail_count", 0)
            and exact_int(counters, "prompts_written_count", 12)
            and exact_int(counters, "raw_responses_written_count", 12)
            and exact_int(
                counters,
                "extracted_json_candidates_written_count",
                12,
            )
            and exact_int(counters, "validations_written_count", 12)
            and exact_int(counters, "canonical_summaries_written_count", 12)
        ),
        "bsep_counters_exact": (
            exact_int(counters, "bsep_created_count", 1)
            and exact_int(counters, "bsep_validated_count", 1)
            and exact_int(counters, "bsep_side_projection_count", 4)
        ),
        "bsep_validation_pass": (
            bsep_validation.get("validation_status") == live_lane.STATUS_PASS
        ),
        "architect_accepted_only_with_validated_bsep": (
            architect_report.get("actor_id") == EXPECTED_ACTORS[1]
            and architect_report.get("actor_index") == 2
            and architect_report.get("validation_status") == live_lane.STATUS_PASS
            and architect_report.get("accepted") is True
            and bsep_packet.get("source_orchestrator_actor_id")
            == EXPECTED_ACTORS[0]
            and bsep_validation.get("validation_status") == live_lane.STATUS_PASS
            and exact_int(counters, "bsep_created_count", 1)
            and exact_int(counters, "bsep_validated_count", 1)
        ),
        "four_bsep_projections_pass": (
            tuple(projections) == (
                "client_bsep_projection",
                "airline_bsep_projection",
                "bank_bsep_projection",
                "cross_root_bsep_projection",
            )
            and all(item.get("validation_status") == live_lane.STATUS_PASS for item in projections.values())
        ),
        "root_boundaries_preserved": (
            len(root_boundaries) == 4
            and all(
                item.get("boundary_preserved") is True
                and type(item.get("violation_count")) is int
                and item.get("violation_count") == 0
                for item in root_boundaries
            )
            and any(
                item.get("boundary")
                == "cross-root reviewer is advisory and not a fourth Root"
                for item in root_boundaries
            )
        ),
        "offer_exact": bridge.get("client_root_selected_offer_id") == EXPECTED_OFFER,
        "airline_resolution_exact": bridge.get("airline_root_resolved_offer_id") == EXPECTED_OFFER,
        "bridge_pass": bridge.get("bridge_status") == live_lane.STATUS_PASS,
        "corridor_pass": bridge.get("deterministic_corridor_final_status") == live_lane.STATUS_PASS,
        "ledger_pass": ledger.get("ledger_validation_status") == live_lane.STATUS_PASS,
        "ledger_geometry_exact": (
            exact_int(ledger, "entry_count", 19)
            and exact_int(ledger, "dependency_edge_count", 29)
            and exact_int(ledger, "root_final_count", 3)
        ),
        "crypto_unanchored_pass": crypto.get("integration_status") == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED,
        "crypto_geometry_exact": (
            exact_int(crypto, "source_file_count", 9)
            and len(critical_refs) == 11
            and all(
                (package_dir / ref).is_file()
                and not (package_dir / ref).is_symlink()
                for ref in critical_refs
            )
        ),
        "crypto_anchor_absent": (
            crypto.get("external_anchor_supplied") is False
            and crypto.get("external_anchor_verified") is False
        ),
        "signature_unverified": (
            crypto.get("signature_mode") == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            and crypto.get("signature_verified") is False
        ),
        "secret_scan_pass": report.get("secret_scan", {}).get("passed") is True,
        "actor_counters_exact": (
            exact_int(counters, "semantic_actor_call_count", 12)
            and exact_int(counters, "causal_semantic_actor_call_count", 5)
            and exact_int(counters, "generic_semantic_actor_call_count", 7)
            and exact_int(counters, "duplicate_semantic_actor_call_count", 0)
            and exact_int(counters, "real_provider_call_count", 12)
            and exact_int(counters, "fake_provider_call_count", 0)
            and exact_int(counters, "network_used_count", 12)
            and exact_int(counters, "gemini_called_count", 12)
        ),
        "duplicate_and_reconstruction_counters_zero": (
            exact_int(
                counters,
                "airline_transaction_artifact_ledger_duplicate_transaction_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_duplicate_corridor_execution_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_duplicate_collection_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_source_reconstruction_count",
                0,
            )
        ),
        "ledger_non_authority_and_effect_counters_zero": (
            exact_int(
                counters,
                "airline_transaction_artifact_ledger_provider_calls_added_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_network_calls_added_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_gemini_calls_added_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_created_authority_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_created_permission_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_created_action_count",
                0,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_real_world_effects_count",
                0,
            )
        ),
        "semantic_selection_honesty_counters_zero": (
            exact_int(counters, "direct_offer_override_count", 0)
            and exact_int(counters, "default_offer_count", 0)
            and exact_int(counters, "silent_fallback_count", 0)
        ),
        "provider_boundary_counters_zero": (
            exact_int(counters, "provider_output_used_as_truth_count", 0)
            and exact_int(counters, "provider_output_used_as_authority_count", 0)
            and exact_int(counters, "provider_created_authority_count", 0)
            and exact_int(counters, "provider_created_contract_count", 0)
            and exact_int(counters, "provider_output_created_packet_count", 0)
            and exact_int(counters, "provider_output_created_receipt_count", 0)
            and exact_int(counters, "provider_output_created_payment_count", 0)
            and exact_int(counters, "provider_output_created_ticket_count", 0)
            and exact_int(counters, "provider_output_created_booking_count", 0)
        ),
        "single_execution_counters": (
            exact_int(counters, "deterministic_airline_collection_count", 1)
            and exact_int(
                counters,
                "ticket_purchase_corridor_execution_count",
                1,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_collection_count",
                1,
            )
            and exact_int(
                counters,
                "airline_transaction_artifact_ledger_validation_count",
                1,
            )
            and exact_int(crypto, "e1_audit_count", 1)
            and exact_int(crypto, "source_bundle_validation_count", 1)
            and exact_int(crypto, "manifest_core_collection_count", 1)
            and exact_int(crypto, "envelope_collection_count", 1)
            and exact_int(
                crypto,
                "post_collection_snapshot_provider_call_count",
                1,
            )
            and exact_int(crypto, "verification_count", 1)
            and exact_int(crypto, "manifest_artifact_written_count", 1)
            and exact_int(crypto, "verification_artifact_written_count", 1)
        ),
        "crypto_byte_stability_and_write_counts": (
            crypto.get("source_bytes_unchanged_after_audit") is True
            and crypto.get("source_bytes_unchanged_after_collection") is True
            and crypto.get("source_bytes_unchanged_after_write") is True
            and crypto.get("source_summary_frozen_before_crypto") is True
            and exact_int(crypto, "manifest_artifact_written_count", 1)
            and exact_int(crypto, "verification_artifact_written_count", 1)
        ),
        "zero_external_effects": (
            exact_int(counters, "real_airline_api_called_count", 0)
            and exact_int(counters, "real_bank_api_called_count", 0)
            and exact_int(counters, "real_gds_api_called_count", 0)
            and exact_int(counters, "real_payment_executed_count", 0)
            and exact_int(counters, "real_ticket_issued_count", 0)
            and exact_int(counters, "real_booking_created_count", 0)
            and exact_int(counters, "real_world_effects_count", 0)
        ),
        "provider_created_objects_zero": all(
            item.get(field_name) is False
            for item in actor_reports
            for field_name in (
                "authority_created",
                "action_permission_created",
                "packet_created",
                "receipt_created",
                "payment_created",
                "ticket_created",
                "booking_created",
                "final_output_created",
            )
        ),
        "failure_and_secret_surface_clean": (
            tuple(report.get("validation_errors", ())) == ()
            and report.get("failed_stage") == ""
            and report.get("provider_error_sanitized") == ""
            and secret_scan.get("passed") is True
            and tuple(secret_scan.get("matched_markers", ())) == ()
        ),
        "execution_commit_synchronized": (
            execution_head == execution_origin_main
            and 7 <= len(execution_head) <= 40
            and all(character in "0123456789abcdef" for character in execution_head)
        ),
        "package_root_guard": (
            package_root.is_dir()
            and not package_root.is_symlink()
        ),
        "package_directory_guard": (
            package_dir.is_dir()
            and not package_dir.is_symlink()
            and package_dir.parent == package_root
        ),
        "direct_package_surface_regular_and_flat": (
            bool(package_entries)
            and all(
                path.is_file() and not path.is_symlink()
                for path in package_entries
            )
            and not any(path.is_dir() for path in package_entries)
        ),
        "expected_actor_and_critical_files_regular": all(
            (package_dir / ref).is_file()
            and not (package_dir / ref).is_symlink()
            for ref in expected_actor_files + critical_refs
        ),
        "package_identity_exact": (
            not package_dir.is_absolute()
            and package_dir.name == source_package_ref
            and source_package_relpath == package_dir.as_posix()
            and all(part not in ("", ".", "..") for part in package_dir.parts)
        ),
        "operator_gate_outside_package": gate_path.parent == package_root,
        "no_unexpected_package_directory": unexpected_package_dirs == (),
        "validation_errors_empty": tuple(report.get("validation_errors", ())) == (),
    }
    gate = {
        "gate_id": "airline_all_real_full_stack_v01_owner_terminal_package_gate",
        "all_checks_pass": all(checks.values()),
        "checks": checks,
        "execution_head": execution_head,
        "execution_origin_main": execution_origin_main,
        "implementation_base_head": IMPLEMENTATION_BASE_HEAD,
        "source_package_ref": source_package_ref,
        "source_package_relpath": source_package_relpath,
        "final_status": report.get("final_status"),
        "provider_mode": report.get("provider_mode"),
        "model": report.get("model"),
        "transaction_id": report.get("transaction_id"),
        "selected_offer_id": bridge.get("client_root_selected_offer_id"),
        "semantic_actor_call_count": counters.get("semantic_actor_call_count"),
        "real_provider_call_count": counters.get("real_provider_call_count"),
        "network_used_count": counters.get("network_used_count"),
        "gemini_called_count": counters.get("gemini_called_count"),
        "ledger_geometry": [ledger.get("entry_count"), ledger.get("dependency_edge_count"), ledger.get("root_final_count")],
        "source_file_count": crypto.get("source_file_count"),
        "critical_file_count": len(critical_refs),
        "crypto_status": crypto.get("integration_status"),
        "manifest_core_hash": crypto.get("manifest_core_hash"),
        "source_package_hash": crypto.get("source_package_hash"),
        "chain_tail_hash": crypto.get("chain_tail_hash"),
        "signature_mode": crypto.get("signature_mode"),
        "signature_verified": crypto.get("signature_verified"),
        "real_world_effects_count": counters.get("real_world_effects_count"),
        "package_sha256_inventory": sha256_inventory,
    }
    gate_bytes = (
        json.dumps(gate, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
        + b"\n"
    )
    with gate_path.open("xb") as handle:
        handle.write(gate_bytes)
    safe_summary = {
        "all_checks_pass": gate["all_checks_pass"],
        "final_status": gate["final_status"],
        "provider_mode": gate["provider_mode"],
        "model": gate["model"],
        "transaction_id": gate["transaction_id"],
        "selected_offer_id": gate["selected_offer_id"],
        "semantic_actor_call_count": gate["semantic_actor_call_count"],
        "crypto_status": gate["crypto_status"],
        "real_world_effects_count": gate["real_world_effects_count"],
    }
    print(json.dumps(safe_summary, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if gate["all_checks_pass"] else 1)
except Exception:
    print('{"official_invocation_status":"FAIL_CLOSED","safe_reason":"sanitized_official_invocation_failure"}')
    raise SystemExit(1)
PY
```

The block does not print a provider response, prompt, credential, exception
message, or traceback. The owner must visually confirm the safe JSON and the
shell return code before proceeding.

## One Official All-Real Transaction

The accepted generation phase requires:

- one transaction;
- one twelve-actor real-provider semantic program;
- one deterministic Airline collection;
- one five-phase Ticket/Purchase Corridor execution;
- one Ledger collection;
- one Ledger validation;
- one E1 read-only Ledger audit during Crypto integration;
- one Crypto source-bundle collection;
- one Manifest Core;
- one unsigned Envelope;
- one stored Verification Report;
- exactly one Manifest JSON write;
- exactly one stored Verification JSON write.

The committed five-phase Corridor order is:

1. `airline_offer_hold_phase`
2. `client_purchase_intent_phase`
3. `bank_payment_authorization_phase`
4. `airline_ticket_issue_phase`
5. `client_completion_phase`

Expected statuses are:

- live lane: `PASS`;
- all twelve actor validations: `PASS`;
- BSEP validation: `PASS`;
- all four BSEP projections: `PASS`;
- causal semantic run: `LOCAL_MODEL_PASS`;
- ClientRoot decision: accepted under its current contract;
- AirlineRoot resolution: `PASS`;
- deterministic Corridor: `PASS`;
- Ledger: `PASS`;
- Crypto integration: `SELF_CONSISTENT_UNANCHORED`.

The generation phase must not claim final anchored Crypto `PASS`.

## Required Transaction Evidence

The accepted package must contain and validate:

Semantic evidence:

- all twelve actor artifact sets;
- BSEP packet;
- BSEP validation;
- four BSEP side projections;
- semantic causal report;
- semantic-to-contract bridge;
- runtime-used and runtime-rejected evidence;
- secret scan;
- safe summary.

Root and Corridor evidence:

- one ClientRoot decision;
- one AirlineRoot authoritative resolution;
- one BankRoot authorization boundary;
- Airline offer packet;
- semantic-causal hold packet;
- hold receipt;
- Client purchase intent;
- Bank payment authorization;
- Airline ticket issue intent;
- mock ticket receipt;
- mock purchase receipt;
- mock PNR or booking evidence where the current contract provides it;
- exactly one Root final per Root.

Ledger evidence:

- 19 entries;
- 29 dependency edges;
- 3 Root finals;
- one ClientRoot final;
- one AirlineRoot final;
- one BankRoot final;
- cross-root advisory not a fourth Root;
- 19 unique artifact IDs;
- exact backward-only dependency order;
- retained semantic-causal hold lineage.

Crypto evidence:

- exact 9 source files;
- exactly 1 Manifest;
- exactly 1 stored Verification;
- exact 11 critical files;
- stored status `SELF_CONSISTENT_UNANCHORED`;
- external anchor supplied false;
- external anchor verified false;
- signature mode `UNSIGNED_PLACEHOLDER`;
- signature verified false;
- package source bytes unchanged through audit, collection, and write.

## Required Non-Crypto Counters

The accepted package must record:

- duplicate transaction executions: 0;
- duplicate Corridor executions: 0;
- duplicate Ledger collections: 0;
- fake provider calls: 0;
- provider-created authority: 0;
- provider-created permission: 0;
- provider-created packet: 0;
- provider-created receipt: 0;
- provider-created FinalOutput: 0;
- real airline API calls: 0;
- real bank API calls: 0;
- real GDS API calls: 0;
- real payment executions: 0;
- real ticket issuances: 0;
- real booking creations: 0;
- real-world effects: 0.

The mock ticket, mock payment authorization, mock purchase receipt, and mock
PNR are proof artifacts only. They are not real external actions.

## Package Success Gate And Post-Run Validation

The future owner-terminal gate must verify:

- final status `PASS`;
- provider mode `real_provider`;
- exact model `gemini-2.5-flash`;
- actor geometry 12 / 5 / 7;
- 12 real provider calls;
- 12 network calls;
- 12 Gemini calls;
- no fake or duplicate calls;
- every actor validation `PASS`;
- every actor report accepted;
- BSEP counters 1 / 1 / 4;
- actor order starts with Orchestrator and then Architect;
- Architect accepted only with validated BSEP;
- four projections `PASS`;
- all five artifact files written for each of twelve actors;
- Preference A selected;
- no direct override, default offer, or silent fallback;
- exact transaction identity;
- ClientRoot, AirlineRoot, and BankRoot boundaries preserved;
- cross-root reviewer remains advisory and not a fourth Root;
- Corridor `PASS`;
- Ledger 19 / 29 / 3;
- duplicate/reconstruction Ledger counters zero;
- Ledger provider/network/Gemini/authority/permission/action/effect counters
  zero;
- source files 9;
- Manifest and stored Verification present;
- Crypto status `SELF_CONSISTENT_UNANCHORED`;
- Crypto source bytes unchanged after audit, collection, and write;
- signature unverified;
- secret scan `PASS`;
- empty validation, failed-stage, provider-error, and secret-marker surfaces;
- zero real effects;
- synchronized execution `HEAD` and `origin/main` captured separately from
  implementation base `a8d5036`;
- exact package path;
- flat non-symlink regular-file package surface;
- no unexpected second package;
- safe operator gate JSON outside the package.

After the official block succeeds, the owner runs this read-only validation in
the same shell:

```sh
PYTHONPATH=. .venv/bin/python - <<'PY'
import hashlib
import json
import os
import subprocess
from pathlib import Path

from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay_contracts

package = Path(os.environ["HEDGEHOG_AIRLINE_LIVE_SEMANTIC_ARTIFACT_DIR"])
gate_path = Path(os.environ["HEDGEHOG_AIRLINE_ALL_REAL_OPERATOR_GATE_JSON"])
assert package.is_dir()
assert not package.is_symlink()
assert gate_path.parent == package.parent
assert gate_path.is_file()
assert not gate_path.is_symlink()
gate = json.loads(gate_path.read_text(encoding="utf-8"))
current_execution_head = subprocess.check_output(
    ("git", "rev-parse", "--short", "HEAD"),
    text=True,
).strip()
current_execution_origin_main = subprocess.check_output(
    ("git", "rev-parse", "--short", "origin/main"),
    text=True,
).strip()
summary = json.loads((package / "summary.json").read_text(encoding="utf-8"))
secret_scan = json.loads((package / "secret_scan.json").read_text(encoding="utf-8"))
manifest = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
    (package / replay_contracts.MANIFEST_ARTIFACT_REF).read_bytes()
)
stored_verification = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
    (package / replay_contracts.STORED_VERIFICATION_ARTIFACT_REF).read_bytes()
)
critical_refs = crypto_contracts.REQUIRED_SOURCE_FILE_REFS + (
    replay_contracts.MANIFEST_ARTIFACT_REF,
    replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
)
inventory = {
    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(package.iterdir())
    if path.is_file()
}
expected_actor_files = tuple(
    suffix
    for actor in (
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
    for suffix in (
        f"{actor}_prompt.txt",
        f"{actor}_raw_response.txt",
        f"{actor}_extracted_json_candidate.json",
        f"{actor}_validation.json",
        f"{actor}_canonical_summary.json",
    )
)

assert gate["all_checks_pass"] is True
assert gate["checks"]
assert all(type(value) is bool and value is True for value in gate["checks"].values())
assert gate["execution_head"] == current_execution_head
assert gate["execution_origin_main"] == current_execution_origin_main
assert gate["execution_head"] == gate["execution_origin_main"]
assert gate["implementation_base_head"] == "a8d5036"
assert gate["source_package_ref"] == package.name
assert gate["source_package_relpath"] == package.as_posix()
assert summary["final_status"] == "PASS"
assert summary["provider_mode"] == "real_provider"
assert summary["model"] == "gemini-2.5-flash"
assert summary["transaction_id"] == "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"
assert summary["counter_table"]["semantic_actor_call_count"] == 12
assert summary["counter_table"]["causal_semantic_actor_call_count"] == 5
assert summary["counter_table"]["generic_semantic_actor_call_count"] == 7
assert summary["counter_table"]["duplicate_semantic_actor_call_count"] == 0
assert summary["counter_table"]["real_provider_call_count"] == 12
assert summary["counter_table"]["fake_provider_call_count"] == 0
assert summary["counter_table"]["network_used_count"] == 12
assert summary["counter_table"]["gemini_called_count"] == 12
assert summary["semantic_to_contract_deterministic_bridge"]["client_root_selected_offer_id"] == "offer:mock_airline_al:PAR-LIM:001"
assert summary["semantic_to_contract_deterministic_bridge"]["bridge_status"] == "PASS"
assert summary["semantic_to_contract_deterministic_bridge"]["deterministic_corridor_final_status"] == "PASS"
assert summary["airline_transaction_artifact_ledger_integration"]["entry_count"] == 19
assert summary["airline_transaction_artifact_ledger_integration"]["dependency_edge_count"] == 29
assert summary["airline_transaction_artifact_ledger_integration"]["root_final_count"] == 3
assert gate["crypto_status"] == "SELF_CONSISTENT_UNANCHORED"
assert gate["source_file_count"] == 9
assert gate["critical_file_count"] == 11
assert gate["signature_mode"] == "UNSIGNED_PLACEHOLDER"
assert gate["signature_verified"] is False
assert secret_scan["passed"] is True
assert len(critical_refs) == 11
assert all(
    (package / ref).is_file() and not (package / ref).is_symlink()
    for ref in critical_refs
)
assert all(
    (package / ref).is_file() and not (package / ref).is_symlink()
    for ref in expected_actor_files
)
package_entries = tuple(package.iterdir())
assert package_entries
assert all(path.is_file() and not path.is_symlink() for path in package_entries)
assert not any(path.is_dir() for path in package_entries)
assert manifest["manifest_core_hash"] == gate["manifest_core_hash"]
assert stored_verification["verification_status"] == "SELF_CONSISTENT_UNANCHORED"
assert stored_verification["external_anchor_supplied"] is False
assert stored_verification["external_anchor_verified"] is False
assert stored_verification["signature_mode"] == "UNSIGNED_PLACEHOLDER"
assert stored_verification["signature_verified"] is False
assert inventory == gate["package_sha256_inventory"]
print("owner_terminal_package_validation: PASS")
PY
```

The operator gate's SHA-256 inventory becomes the frozen post-success package
inventory. No anchor may be published until this visible validation passes.

## Failure Discipline

No automatic retry.

If the official invocation fails:

- stop immediately;
- do not rerun;
- do not delete the failure package;
- do not reuse the package ref;
- do not publish an anchor;
- do not run Replay;
- do not create success audit, human, or closure documents;
- preserve only safe failure evidence;
- do not print raw responses or secrets;
- require explicit review before selecting a new package ref.

If a provider call fails partway through, prior calls remain historical local
failure evidence. The incomplete package is not authoritative, and no
self-healing or actor-output replay is allowed. A non-`PASS` final status, a
Crypto status other than `SELF_CONSISTENT_UNANCHORED`, or a failed secret scan
blocks promotion. Sensitive content must never be copied into audit text.

## External Anchor Publication Phase

After owner-terminal package validation, a separate non-runtime phase derives
the new tracked anchor from the accepted Manifest Core hash. The hash must be
independently recomputed after package completion. It must not be derived
before completion, fed back into the same generation call, or accepted merely
because the Manifest repeats its own hash.

The current committed Replay runner requires these stable v0.1 anchor ABI
values:

- `anchor_document_id: airline_crypto_artifact_seal_anchor_v01`
- `anchor_version: v0.1`
- `document_status: ANCHOR_PUBLICATION`
- `publication_slice: airline_crypto_artifact_seal_v01_slice_e1`
- `next_gate: airline_crypto_artifact_seal_v01_slice_e2_anchored_audit`
- `anchor_active_only_when_committed: true`
- `anchored_pass_claimed: false`
- `replay_allowed: false`

The exact 27-field object surface is:

1. `anchor_active_only_when_committed`
2. `anchor_document_id`
3. `anchor_version`
4. `anchored_pass_claimed`
5. `canonicalization_profile_id`
6. `chain_tail_hash`
7. `document_status`
8. `expected_manifest_core_hash`
9. `external_anchor_supplied_at_publication`
10. `external_anchor_verified_at_publication`
11. `hash_algorithm`
12. `hash_encoding`
13. `ledger_id`
14. `manifest_artifact_ref`
15. `next_gate`
16. `package_generation_base_head`
17. `publication_slice`
18. `real_world_effects_count`
19. `replay_allowed`
20. `signature_mode`
21. `signature_verified`
22. `source_package_hash`
23. `source_package_ref`
24. `source_package_relpath`
25. `transaction_id`
26. `verification_artifact_ref`
27. `verification_status_at_publication`

The new object binds the accepted package's transaction ID, Ledger ID,
Manifest Core hash, source-package hash, chain-tail hash, package ref, and
package relative path. `implementation_base_head` remains `a8d5036` in the
operator gate and audit evidence, but it is not an additional anchor field.
The anchor's `package_generation_base_head` is the exact synchronized
`execution_head` accepted by the owner-terminal operator gate. The
generation/anchor audit must compare that anchor field to the accepted gate,
and the later anchor publication commit must prove that the generation commit
is in its Git ancestry. The anchor also records the current
canonicalization/hash constants, the exact Manifest and stored Verification
artifact refs, publication-time external-anchor flags false,
`SELF_CONSISTENT_UNANCHORED`, `UNSIGNED_PLACEHOLDER`, signature verification
false, and real-world effects 0.

These values were verified against the current committed runner. They are ABI
compatibility fields, not the current project roadmap. In particular,
`replay_allowed: false` records the historical publication moment. Replay
becomes eligible only after the new anchor is committed. The new anchor path
does not replace the existing offline anchor.

Publication sequence:

1. Perform owner-terminal package generation.
2. Perform owner-terminal package validation.
3. Independently recompute the Manifest Core hash.
4. Create the new anchor and generation/anchor audit.
5. Perform owner-terminal read-only validation of both.
6. Commit and push the validated anchor and generation/anchor audit together.
7. Confirm clean synchronized `HEAD`.
8. Only then execute anchored Replay.

The package must not be rewritten.

## Anchored Replay Phase

The later anchored Replay uses the existing committed module
`demo.run_airline_sealed_trace_replay_v01` with:

- the exact accepted all-real package;
- the exact newly committed all-real anchor;
- the exact external Replay Report target.

Replay invocation count is one. It is performed later in the owner's visible
terminal and must not call Gemini or any provider, use the network, rerun
semantics, rerun the transaction or Corridor, recollect Ledger or Crypto,
create payment, booking, or ticket effects, or create a Root final.

After the anchor publication commit is synchronized and all three explicit
paths have passed read-only guards, the planned command is:

```sh
PYTHONPATH=. .venv/bin/python -m \
  demo.run_airline_sealed_trace_replay_v01 \
  --package-dir "$OFFICIAL_PACKAGE" \
  --anchor-path "$FUTURE_ANCHOR" \
  --output-path "$FUTURE_REPLAY_REPORT"
```

Expected Replay result:

- `PASS`;
- stored Verification remains `SELF_CONSISTENT_UNANCHORED`;
- fresh Verification `PASS`;
- external anchor supplied true;
- external anchor verified true;
- signature remains unverified;
- timeline rows 19;
- Ledger geometry 19 / 29 / 3;
- package geometry 9 / 11;
- all eleven critical package bytes unchanged;
- output outside the package;
- real-world effects 0.

No second all-real semantic run occurs during Replay.

## Final Evidence Program

The package, anchor, and Replay opening sequence is:

1. Perform owner-terminal package generation.
2. Perform owner-terminal package validation.
3. Independently recompute the Manifest Core hash.
4. Create the new anchor and generation/anchor audit.
5. Perform owner-terminal read-only validation of both.
6. Commit and push the validated anchor and generation/anchor audit together.
7. Confirm clean synchronized `HEAD`.
8. Only then execute anchored Replay.

After the single anchored Replay invocation:

1. Validate Replay in the owner terminal.
2. Commit the independent anchored Replay audit separately.
3. Commit the artifact-backed human story separately.
4. Commit canonical docs/spec/manifest synchronization separately.

Only the final docs-sync commit closes:

`Airline All-Real Full-Stack Run v0.1: CLOSED / PASS`

Audit, human, and documentation closure must not be merged into one
unreviewed commit.

## Human Story Expectation

The later human story explains:

- the original fixed user travel task;
- the twelve semantic actors;
- what each Root decided;
- why Preference A was selected;
- how the hold, payment authorization, ticket issue intent, mock ticket, mock
  PNR, and receipts relate;
- the 19-row Ledger timeline;
- what Crypto proved;
- why stored Verification was initially unanchored;
- what the committed anchor changed;
- what Replay reconstructed;
- why no real ticket, payment, or booking occurred.

It must not rerun runtime or expose raw provider responses or secrets.

## Root Attestation Boundary

Root Attestation remains deferred. The final all-real demonstration uses the
Ledger, Manifest, source-package hash, ordered hash chain, committed external
Manifest Core anchor, fresh anchored verification, and Base Replay.

It does not implement Root proof keypairs, Ed25519 signatures, PKI, HSM, key
rotation, or Attested Replay. The optional future strengthening remains
documented but is not activated.

## Non-Claims

- Real Gemini semantics are used in the later official generation.
- Real Gemini semantics remain advisory and bounded.
- Provider output is not truth.
- Provider output is not Root authority.
- Deterministic contracts and validators remain authoritative.
- The Airline transaction is a mock proof transaction.
- The payment is not real.
- The booking is not real.
- The ticket is not real.
- No airline, bank, or GDS API is called.
- Crypto integrity is not semantic truth.
- A committed hash anchor is not signer authentication.
- Signature verification remains false.
- Replay verification is not effect authorization.
- Not production.
- Not a legal transaction.
- Not a public-auditor final distribution package.
- No Root Attestation.

## Definition Of Done

This preflight freezes:

- why the new full-stack run is required;
- exact implementation base `a8d5036`;
- exact synchronized owner-terminal execution commit captured separately;
- exact Preference A scenario;
- exact package identity and directory;
- exact twelve actors;
- exact real-provider counters;
- exact owner-terminal boundary;
- exact current live-runner API path;
- exact environment gates;
- exact credential non-disclosure rule;
- exact single invocation and failure discipline;
- exact package success gate;
- exact Ledger geometry 19 / 29 / 3;
- exact Crypto and Replay geometry 9 / 11;
- stored unanchored Verification;
- non-circular anchor publication lifecycle;
- one validated anchor plus generation/audit publication commit;
- exact new anchor, Replay, audit, human, and checkpoint destinations;
- no Preference B real-provider requirement;
- no real external effect;
- no Root Attestation;
- no runtime or test change in this task.

Final preflight status: `READY_FOR_REVIEW`.

Next gate after preflight commit:
`airline_all_real_full_stack_run_v01_owner_terminal_execution`
