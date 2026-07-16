"""Airline Transaction Artifact Ledger v0.1 local contracts.

This is an Airline domain projection. It is not Hedgehog OS universal
kernel/core. Exact boundary phrase: not Hedgehog OS universal kernel/core.
It is not an installed Needle.

Ledger records trace.
Ledger does not authorize.
Ledger does not prove truth.
Ledger does not execute.

This module records transaction trace only. It creates no authority,
permission, action, packet, receipt, payment, ticket, booking, or FinalOutput.
It performs no provider, network, or Gemini invocation. Crypto Artifact Seal
and Replay are not implemented.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    ticket_purchase_corridor_v01 as corridor_contracts,
)


MODULE_ID = "airline_transaction_artifact_ledger_v01"
SLICE_ID = "airline_transaction_artifact_ledger_v01_slice_b"
LEDGER_VERSION = "airline_transaction_artifact_ledger_v01"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

INDEPENDENT_DERIVED_FIELD_RECOMPUTATION_BEHAVIOR = (
    "Independent derived-field recomputation behavior"
)

TRANSACTION_ID = corridor_contracts.TRANSACTION_ID
CLIENT_ROOT_ID = corridor_contracts.CLIENT_ROOT_ID
AIRLINE_ROOT_ID = corridor_contracts.AIRLINE_ROOT_ID
BANK_ROOT_ID = corridor_contracts.BANK_ROOT_ID

OFFER_A_ID = binding.OFFER_A_ID
OFFER_B_ID = binding.OFFER_B_ID
VALID_LEDGER_OFFER_IDS = (OFFER_A_ID, OFFER_B_ID)

ROOT_OWNER_TRANSACTION_SCOPE = "transaction_scope:non_authoritative"
ROOT_OWNER_RUNTIME_CANONICALIZATION = "runtime_canonicalization:advisory"
ROOT_OWNER_BSEP_CLIENT = "bsep_side:client"
ROOT_OWNER_BSEP_AIRLINE = "bsep_side:airline"
ROOT_OWNER_BSEP_BANK = "bsep_side:bank"
ROOT_OWNER_BSEP_CROSS_ROOT = "bsep_side:cross_root_advisory"
CREATED_BY_LEDGER_FIXTURE = "deterministic_airline_ledger_fixture_builder"
CREATED_BY_BSEP_BUILDER = "bounded_semantic_membrane_builder"
CREATED_BY_RUNTIME_CANONICALIZATION = "runtime_canonicalization"
CREATED_BY_CLIENT_COMPLETION_OBSERVER = "client_completion_observer"

EVENT_TRANSACTION_STARTED = "transaction_started"
EVENT_BSEP_PROJECTION_CREATED = "bsep_projection_created"
EVENT_SEMANTIC_CLAIM_CREATED = "semantic_claim_created"
EVENT_CLIENT_ROOT_SELECTION_DECIDED = "client_root_selection_decided"
EVENT_AIRLINE_ROOT_OFFER_RESOLVED = "airline_root_offer_resolved"
EVENT_OFFER_CREATED = "offer_created"
EVENT_HOLD_CREATED = "hold_created"
EVENT_OFFER_HOLD_RECEIPT_CREATED = "offer_hold_receipt_created"
EVENT_PURCHASE_INTENT_CREATED = "purchase_intent_created"
EVENT_PAYMENT_AUTHORIZATION_CREATED = "payment_authorization_created"
EVENT_TICKET_INTENT_CREATED = "ticket_intent_created"
EVENT_MOCK_TICKET_RECEIPT_CREATED = "mock_ticket_receipt_created"
EVENT_MOCK_PURCHASE_RECEIPT_CREATED = "mock_purchase_receipt_created"
EVENT_ROOT_FINAL_CREATED = "root_final_created"
EVENT_HUMAN_APPROVAL_RECORDED = "human_approval_recorded"

EMITTED_EVENT_TYPES = (
    EVENT_TRANSACTION_STARTED,
    EVENT_BSEP_PROJECTION_CREATED,
    EVENT_SEMANTIC_CLAIM_CREATED,
    EVENT_CLIENT_ROOT_SELECTION_DECIDED,
    EVENT_AIRLINE_ROOT_OFFER_RESOLVED,
    EVENT_OFFER_CREATED,
    EVENT_HOLD_CREATED,
    EVENT_OFFER_HOLD_RECEIPT_CREATED,
    EVENT_PURCHASE_INTENT_CREATED,
    EVENT_PAYMENT_AUTHORIZATION_CREATED,
    EVENT_TICKET_INTENT_CREATED,
    EVENT_MOCK_TICKET_RECEIPT_CREATED,
    EVENT_MOCK_PURCHASE_RECEIPT_CREATED,
    EVENT_ROOT_FINAL_CREATED,
)
RESERVED_EVENT_TYPES = (EVENT_HUMAN_APPROVAL_RECORDED,)

AUTHORITY_NONE = "none"
AUTHORITY_BOUNDED_CONTEXT = "bounded_context_non_authoritative"
AUTHORITY_ADVISORY_CANONICAL = "advisory_canonical"
AUTHORITY_ROOT_DECISION = "root_decision"
AUTHORITY_ROOT_OWNED_CONTRACT = "root_owned_contract"
AUTHORITY_EVIDENCE_ONLY_RECEIPT = "evidence_only_receipt"
AUTHORITY_ROOT_FINAL = "root_final"

AUTHORITY_CLASSES = (
    AUTHORITY_NONE,
    AUTHORITY_BOUNDED_CONTEXT,
    AUTHORITY_ADVISORY_CANONICAL,
    AUTHORITY_ROOT_DECISION,
    AUTHORITY_ROOT_OWNED_CONTRACT,
    AUTHORITY_EVIDENCE_ONLY_RECEIPT,
    AUTHORITY_ROOT_FINAL,
)

EVIDENCE_TRANSACTION_METADATA = "transaction_metadata"
EVIDENCE_BOUNDED_SEMANTIC_CONTEXT = "bounded_semantic_context"
EVIDENCE_CANONICAL_SEMANTIC = "canonical_semantic_evidence"
EVIDENCE_ROOT_DECISION = "root_decision_evidence"
EVIDENCE_ROOT_CONTRACT = "root_contract_artifact"
EVIDENCE_VALIDATION = "validation_evidence"
EVIDENCE_HUMAN_APPROVAL = "human_approval_evidence"
EVIDENCE_PAYMENT_AUTHORIZATION = "payment_authorization_evidence"
EVIDENCE_RECEIPT_ONLY = "receipt_evidence_only"
EVIDENCE_ROOT_FINAL = "root_final_evidence"

EVIDENCE_CLASSES = (
    EVIDENCE_TRANSACTION_METADATA,
    EVIDENCE_BOUNDED_SEMANTIC_CONTEXT,
    EVIDENCE_CANONICAL_SEMANTIC,
    EVIDENCE_ROOT_DECISION,
    EVIDENCE_ROOT_CONTRACT,
    EVIDENCE_VALIDATION,
    EVIDENCE_HUMAN_APPROVAL,
    EVIDENCE_PAYMENT_AUTHORIZATION,
    EVIDENCE_RECEIPT_ONLY,
    EVIDENCE_ROOT_FINAL,
)

FORBIDDEN_CLASSIFICATIONS = (
    "provider_authority",
    "ledger_authority",
    "ledger_permission",
    "receipt_permission",
    "receipt_root_final",
    "raw_provider_truth",
    "hash_proves_truth",
    "shared_cross_root_authority",
)

CLASS_CANONICAL_LEDGER_ENTRY = "canonical ledger entry"
CLASS_SOURCE_VALIDATION_REFERENCE = "source validation reference"
CLASS_AUXILIARY_OBSERVATION_REFERENCE = "auxiliary observation reference"
CLASS_EXCLUDED_RAW_PRIVATE_MATERIAL = "excluded raw/private material"

ARTIFACT_TRANSACTION_SCOPE = "AirlineTransactionScopeV01"
ARTIFACT_CLIENT_BSEP_PROJECTION = "ClientBSEPProjectionV01"
ARTIFACT_AIRLINE_BSEP_PROJECTION = "AirlineBSEPProjectionV01"
ARTIFACT_BANK_BSEP_PROJECTION = "BankBSEPProjectionV01"
ARTIFACT_CROSS_ROOT_BSEP_PROJECTION = "CrossRootAdvisoryBSEPProjectionV01"
ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE = (
    "ValidatedAirlineSemanticSelectionEvidenceV01"
)
ARTIFACT_CLIENT_ROOT_SELECTION_DECISION = "ClientRootOfferSelectionDecisionV01"
ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION = "AirlineRootSelectedOfferResolutionV01"
ARTIFACT_AIRLINE_OFFER_PACKET = "AirlineOfferPacketV01"
ARTIFACT_AIRLINE_HOLD_PACKET = "AirlineHoldCommitPacketV01"
ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT = "AirlineOfferHoldReceiptV01"
ARTIFACT_CLIENT_PURCHASE_INTENT = "ClientPurchaseIntentV01"
ARTIFACT_BANK_PAYMENT_AUTHORIZATION = "BankPaymentAuthorizationRefV01"
ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT = "AirlineTicketIssueIntentV01"
ARTIFACT_MOCK_TICKET_RECEIPT = "MockTicketReceiptV01"
ARTIFACT_MOCK_PURCHASE_RECEIPT = "MockPurchaseReceiptV01"
ARTIFACT_CLIENT_ROOT_FINAL = "ClientRootFinalV01"
ARTIFACT_AIRLINE_ROOT_FINAL = "AirlineRootFinalV01"
ARTIFACT_BANK_ROOT_FINAL = "BankRootFinalV01"

SOURCE_REF_CLIENT_CONSTRAINTS = "ClientRootTravelConstraintSetV01:client_001:preference"
SOURCE_REF_CANDIDATE_SNAPSHOT = "AirlineRootOfferCandidateSetSnapshotV01:mock_airline_al:PAR-LIM"
SOURCE_REF_SELECTION_INPUT = "AirlineSemanticSelectionInputV01:airline_offer_selection"
SOURCE_REF_PROPOSAL = "AirlineSemanticOfferSelectionProposalV01:client_purchase_intent_reviewer_llm"
SOURCE_REF_ACTOR_REVIEWS = (
    "AirlineCanonicalActorSelectionReviewV01:client_purchase_intent_reviewer_llm",
    "AirlineCanonicalActorSelectionReviewV01:airline_offer_policy_reviewer_llm",
    "AirlineCanonicalActorSelectionReviewV01:airline_fare_rules_vertical_cell_llm",
    "AirlineCanonicalActorSelectionReviewV01:airline_seat_baggage_vertical_cell_llm",
    "AirlineCanonicalActorSelectionReviewV01:tri_party_evidence_consistency_reviewer_llm",
)
SOURCE_REF_SYNTHESIS = "AirlineSemanticSelectionSynthesisReportV01:five_actor_synthesis"
SOURCE_REF_CAUSAL_BINDING = "AirlineSemanticToContractBindingReportV01:local_chain"
SOURCE_REF_CORRIDOR_VALIDATION = "AirlineCorridorValidationReportV01:ticket_purchase"
SOURCE_REF_CORRIDOR_RUN = "AirlineTicketPurchaseCorridorRunReportV01:deterministic"
SOURCE_REF_ROOT_PHASE_GATE_PREFIX = "AirlineRootPhaseGateV01"
SOURCE_REF_HUMAN_APPROVAL = "AirlinePurchaseApprovalEvidenceRefV01:human_approval:client_001"

OPAQUE_PROMPT_REF = "auxiliary_artifact_ref:provider_prompt:opaque"
OPAQUE_RESPONSE_REF = "auxiliary_artifact_ref:provider_response:opaque"
SOURCE_RUN_REF_FIXTURE = "source_run:deterministic_slice_b_fixture"
SOURCE_CAUSAL_REPORT_REF_FIXTURE = "source_causal_report:deterministic_slice_b_fixture"
SOURCE_CORRIDOR_REPORT_REF_FIXTURE = (
    "source_corridor_report:deterministic_slice_b_fixture"
)

FIXED_EVENT_TIME_PREFIX = "2026-07-12T10"
FIXED_RECORDED_TIME_PREFIX = "2026-07-12T11"
RFC3339_Z_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
)

REASON_MALFORMED_ENTRY = "malformed_ledger_entry"
REASON_NEGATIVE_INDEX = "negative_ledger_index"
REASON_EMPTY_STRING_FIELD = "empty_string_field"
REASON_INVALID_STRING_FIELD = "invalid_string_field"
REASON_RESERVED_EVENT_TYPE = "reserved_event_type_emitted"
REASON_UNKNOWN_EVENT_TYPE = "unknown_event_type"
REASON_UNKNOWN_AUTHORITY_CLASS = "unknown_authority_class"
REASON_UNKNOWN_EVIDENCE_CLASS = "unknown_evidence_class"
REASON_FORBIDDEN_CLASSIFICATION = "forbidden_classification"
REASON_WRONG_ARTIFACT_CLASSIFICATION = "wrong_artifact_classification"
REASON_WRONG_ROOT_OWNER = "wrong_root_owner"
REASON_WRONG_CREATED_BY = "wrong_created_by"
REASON_WRONG_AUTHORITY_CLASS = "wrong_authority_class"
REASON_WRONG_EVIDENCE_CLASS = "wrong_evidence_class"
REASON_MALFORMED_DEPENDENCIES = "malformed_dependencies"
REASON_DUPLICATE_DEPENDENCY = "duplicate_dependency"
REASON_MALFORMED_SOURCE_REFS = "malformed_source_validation_refs"
REASON_MALFORMED_AUXILIARY_REFS = "malformed_auxiliary_artifact_refs"
REASON_MALFORMED_TIMESTAMP = "malformed_timestamp"
REASON_RAW_SECRET_INCLUDED = "raw_secret_included"
REASON_RAW_PROVIDER_TEXT_INCLUDED = "raw_provider_text_included"
REASON_LEDGER_CREATED_AUTHORITY = "ledger_created_authority"
REASON_LEDGER_CREATED_PERMISSION = "ledger_created_permission"
REASON_LEDGER_CREATED_ACTION = "ledger_created_action"
REASON_NONZERO_REAL_WORLD_EFFECTS = "nonzero_real_world_effects"
REASON_MALFORMED_CANONICAL_HASH_INPUT = "malformed_canonical_hash_input"
REASON_UNSAFE_CANONICAL_HASH_INPUT = "unsafe_canonical_hash_input"
REASON_CANONICAL_HASH_INPUT_BINDING_MISMATCH = (
    "canonical_hash_input_binding_mismatch"
)
REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH = (
    "canonical_hash_input_keyset_mismatch"
)
REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH = (
    "canonical_hash_input_source_fact_mismatch"
)
REASON_DUPLICATE_LEDGER_INDEX = "duplicate_ledger_index"
REASON_NON_CONTIGUOUS_LEDGER_INDEX = "non_contiguous_ledger_index"
REASON_DUPLICATE_ARTIFACT_ID = "duplicate_artifact_id"
REASON_MIXED_TRANSACTION_ID = "mixed_transaction_id"
REASON_TRANSACTION_STARTED_NOT_INDEX_ZERO = "transaction_started_not_index_zero"
REASON_MULTIPLE_TRANSACTION_STARTED = "multiple_transaction_started"
REASON_WRONG_EVENT_ORDER = "wrong_event_order"
REASON_MISSING_REQUIRED_EVENT = "missing_required_event"
REASON_MISSING_DEPENDENCY = "missing_dependency"
REASON_EXTRA_UNDECLARED_DEPENDENCY = "extra_undeclared_dependency"
REASON_DEPENDENCY_ON_LATER_ENTRY = "dependency_on_later_entry"
REASON_SELF_DEPENDENCY = "self_dependency"
REASON_CYCLIC_DEPENDENCY = "cyclic_dependency"
REASON_MISSING_CLIENT_ROOT_FINAL = "missing_client_root_final"
REASON_MISSING_AIRLINE_ROOT_FINAL = "missing_airline_root_final"
REASON_MISSING_BANK_ROOT_FINAL = "missing_bank_root_final"
REASON_CROSS_ROOT_REVIEWER_AS_FOURTH_ROOT = "cross_root_reviewer_as_fourth_root"
REASON_OFFER_HOLD_RECEIPT_NOT_BEFORE_PURCHASE_INTENT = (
    "offer_hold_receipt_not_before_purchase_intent"
)
REASON_HUMAN_APPROVAL_FABRICATED_CREATOR = "human_approval_fabricated_creator"
REASON_RAW_PROMPT_RESPONSE_NOT_AUXILIARY_ONLY = (
    "raw_prompt_response_not_auxiliary_only"
)
REASON_SEMANTIC_CLAIM_MISSING_SOURCE_REFS = "semantic_claim_missing_source_refs"
REASON_HUMAN_APPROVAL_NOT_SOURCE_REF = "human_approval_not_source_ref"
REASON_OFFER_INCONSISTENCY = "offer_inconsistency"
REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH = "artifact_id_source_fact_mismatch"

REASON_LEDGER_ENTRY_COUNT_MISMATCH = "ledger_entry_count_mismatch"
REASON_LEDGER_DEPENDENCY_EDGE_COUNT_MISMATCH = (
    "ledger_dependency_edge_count_mismatch"
)
REASON_LEDGER_EVENT_TYPE_COUNTS_MISMATCH = "ledger_event_type_counts_mismatch"
REASON_LEDGER_ROOT_FINAL_COUNT_MISMATCH = "ledger_root_final_count_mismatch"
REASON_LEDGER_DERIVED_COUNTER_MISMATCH = "ledger_derived_counter_mismatch"
REASON_LEDGER_STORED_VALIDATION_STATUS_MISMATCH = (
    "ledger_stored_validation_status_mismatch"
)
REASON_LEDGER_ID_MISMATCH = "ledger_id_mismatch"
REASON_LEDGER_VERSION_MISMATCH = "ledger_version_mismatch"
REASON_LEDGER_SOURCE_REF_MISMATCH = "ledger_source_ref_mismatch"
REASON_SOURCE_REF_MISMATCH = "source_ref_mismatch"
REASON_LEDGER_MALFORMED_VALIDATION_ERRORS = "ledger_malformed_validation_errors"
REASON_LEDGER_MALFORMED_COUNT = "ledger_malformed_count"
REASON_SOURCE_VALIDATION_REFS_PROFILE_MISMATCH = (
    "source_validation_refs_profile_mismatch"
)
REASON_AUXILIARY_ARTIFACT_REFS_PROFILE_MISMATCH = (
    "auxiliary_artifact_refs_profile_mismatch"
)
REASON_SOURCE_VALIDATION_REF_LINEAGE_MISMATCH = (
    "source_validation_ref_lineage_mismatch"
)
REASON_AUXILIARY_REF_LINEAGE_MISMATCH = "auxiliary_ref_lineage_mismatch"
REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH = (
    "canonical_source_lineage_mismatch"
)
REASON_UNSAFE_SOURCE_OR_AUXILIARY_REF = "unsafe_source_or_auxiliary_ref"


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerEntryV01:
    ledger_index: int
    event_type: str
    artifact_id: str
    artifact_type: str
    transaction_id: str
    root_owner: str
    created_by: str
    authority_class: str
    evidence_class: str
    depends_on: tuple[str, ...]
    event_time: str
    recorded_at: str
    source_validation_refs: tuple[str, ...]
    auxiliary_artifact_refs: tuple[str, ...]
    canonical_hash_input: Mapping[str, Any]
    raw_secret_included: bool
    raw_provider_text_included: bool
    ledger_created_authority: bool
    ledger_created_permission: bool
    ledger_created_action: bool
    real_world_effects_count: int

    def __post_init__(self) -> None:
        if isinstance(self.canonical_hash_input, MappingABC):
            object.__setattr__(
                self,
                "canonical_hash_input",
                _freeze_json(self.canonical_hash_input),
            )


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerV01:
    ledger_id: str
    ledger_version: str
    transaction_id: str
    source_run_ref: str
    source_causal_report_ref: str
    source_corridor_report_ref: str
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...]
    entry_count: int
    dependency_edge_count: int
    event_type_counts: Mapping[str, int]
    root_final_count: int
    validation_status: str
    validation_errors: tuple[str, ...]
    ledger_created_authority_count: int
    ledger_created_permission_count: int
    ledger_created_action_count: int
    provider_called_count: int
    network_used_count: int
    gemini_called_count: int
    real_world_effects_count: int

    def __post_init__(self) -> None:
        if isinstance(self.event_type_counts, MappingABC):
            object.__setattr__(
                self,
                "event_type_counts",
                _freeze_json(self.event_type_counts),
            )


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerExpectedSourceRefsV01:
    source_run_ref: str
    source_causal_report_ref: str
    source_corridor_report_ref: str


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerExpectedIdentityV01:
    expected_source_refs: AirlineTransactionArtifactLedgerExpectedSourceRefsV01
    expected_artifact_ids: Mapping[str, str]
    expected_source_validation_refs_by_type: (
        Mapping[str, tuple[str, ...]] | None
    ) = None
    expected_auxiliary_artifact_refs_by_type: (
        Mapping[str, tuple[str, ...]] | None
    ) = None
    expected_source_identity_fields_by_type: (
        Mapping[str, Mapping[str, Any]] | None
    ) = None

    def __post_init__(self) -> None:
        if isinstance(self.expected_artifact_ids, MappingABC):
            object.__setattr__(
                self,
                "expected_artifact_ids",
                _freeze_json(self.expected_artifact_ids),
            )
        source_refs = (
            self.expected_source_validation_refs_by_type
            if self.expected_source_validation_refs_by_type is not None
            else EXPECTED_SOURCE_REFS_BY_ARTIFACT_TYPE
        )
        aux_refs = (
            self.expected_auxiliary_artifact_refs_by_type
            if self.expected_auxiliary_artifact_refs_by_type is not None
            else EXPECTED_AUXILIARY_REFS_BY_ARTIFACT_TYPE
        )
        source_identity = (
            self.expected_source_identity_fields_by_type
            if self.expected_source_identity_fields_by_type is not None
            else {}
        )
        if isinstance(source_refs, MappingABC):
            object.__setattr__(
                self,
                "expected_source_validation_refs_by_type",
                _freeze_json(source_refs),
            )
        if isinstance(aux_refs, MappingABC):
            object.__setattr__(
                self,
                "expected_auxiliary_artifact_refs_by_type",
                _freeze_json(aux_refs),
            )
        if isinstance(source_identity, MappingABC):
            object.__setattr__(
                self,
                "expected_source_identity_fields_by_type",
                _freeze_json(source_identity),
            )

    @property
    def expected_artifact_ids_by_type(self) -> Mapping[str, str]:
        return self.expected_artifact_ids


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerValidationReportV01:
    validation_status: str
    transaction_id: str
    entry_count: int
    dependency_edge_count: int
    event_type_counts: Mapping[str, int]
    root_final_count: int
    indexes_valid: bool
    artifact_ids_unique: bool
    event_types_valid: bool
    transaction_identity_valid: bool
    dependencies_present: bool
    dependencies_ordered: bool
    dependency_graph_acyclic: bool
    root_ownership_valid: bool
    authority_classes_valid: bool
    evidence_classes_valid: bool
    canonical_hash_inputs_safe: bool
    raw_secret_boundary_valid: bool
    raw_provider_boundary_valid: bool
    ledger_non_authority_valid: bool
    real_effects_zero: bool
    validation_errors: tuple[str, ...]
    ledger_created_authority_count: int = 0
    ledger_created_permission_count: int = 0
    ledger_created_action_count: int = 0
    raw_secret_included_count: int = 0
    raw_provider_text_included_count: int = 0

    def __post_init__(self) -> None:
        if isinstance(self.event_type_counts, MappingABC):
            object.__setattr__(
                self,
                "event_type_counts",
                _freeze_json(self.event_type_counts),
            )


@dataclass(frozen=True)
class _ArtifactProfile:
    classification: str
    event_type: str
    root_owner: str
    created_by: str
    authority_class: str
    evidence_class: str


class _FrozenDict(MappingABC):
    __slots__ = ("_data",)

    def __init__(self, value: Mapping[str, Any]) -> None:
        object.__setattr__(self, "_data", MappingProxyType(dict(value)))

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __setattr__(self, name: str, value: Any) -> None:
        raise TypeError("frozen mapping cannot be mutated")

    def __deepcopy__(self, memo: dict[int, Any]) -> "_FrozenDict":
        return self

    def __repr__(self) -> str:
        return repr(dict(self._data))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MappingABC):
            return dict(self.items()) == dict(other.items())
        return False


ARTIFACT_PROFILES: Mapping[str, _ArtifactProfile] = MappingProxyType({
    ARTIFACT_TRANSACTION_SCOPE: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_TRANSACTION_STARTED,
        ROOT_OWNER_TRANSACTION_SCOPE,
        CREATED_BY_LEDGER_FIXTURE,
        AUTHORITY_NONE,
        EVIDENCE_TRANSACTION_METADATA,
    ),
    ARTIFACT_CLIENT_BSEP_PROJECTION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_BSEP_PROJECTION_CREATED,
        ROOT_OWNER_BSEP_CLIENT,
        CREATED_BY_BSEP_BUILDER,
        AUTHORITY_BOUNDED_CONTEXT,
        EVIDENCE_BOUNDED_SEMANTIC_CONTEXT,
    ),
    ARTIFACT_AIRLINE_BSEP_PROJECTION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_BSEP_PROJECTION_CREATED,
        ROOT_OWNER_BSEP_AIRLINE,
        CREATED_BY_BSEP_BUILDER,
        AUTHORITY_BOUNDED_CONTEXT,
        EVIDENCE_BOUNDED_SEMANTIC_CONTEXT,
    ),
    ARTIFACT_BANK_BSEP_PROJECTION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_BSEP_PROJECTION_CREATED,
        ROOT_OWNER_BSEP_BANK,
        CREATED_BY_BSEP_BUILDER,
        AUTHORITY_BOUNDED_CONTEXT,
        EVIDENCE_BOUNDED_SEMANTIC_CONTEXT,
    ),
    ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_BSEP_PROJECTION_CREATED,
        ROOT_OWNER_BSEP_CROSS_ROOT,
        CREATED_BY_BSEP_BUILDER,
        AUTHORITY_BOUNDED_CONTEXT,
        EVIDENCE_BOUNDED_SEMANTIC_CONTEXT,
    ),
    ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_SEMANTIC_CLAIM_CREATED,
        ROOT_OWNER_RUNTIME_CANONICALIZATION,
        CREATED_BY_RUNTIME_CANONICALIZATION,
        AUTHORITY_ADVISORY_CANONICAL,
        EVIDENCE_CANONICAL_SEMANTIC,
    ),
    ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_CLIENT_ROOT_SELECTION_DECIDED,
        CLIENT_ROOT_ID,
        CLIENT_ROOT_ID,
        AUTHORITY_ROOT_DECISION,
        EVIDENCE_ROOT_DECISION,
    ),
    ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_AIRLINE_ROOT_OFFER_RESOLVED,
        AIRLINE_ROOT_ID,
        AIRLINE_ROOT_ID,
        AUTHORITY_ROOT_DECISION,
        EVIDENCE_ROOT_DECISION,
    ),
    ARTIFACT_AIRLINE_OFFER_PACKET: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_OFFER_CREATED,
        AIRLINE_ROOT_ID,
        AIRLINE_ROOT_ID,
        AUTHORITY_ROOT_OWNED_CONTRACT,
        EVIDENCE_ROOT_CONTRACT,
    ),
    ARTIFACT_AIRLINE_HOLD_PACKET: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_HOLD_CREATED,
        AIRLINE_ROOT_ID,
        AIRLINE_ROOT_ID,
        AUTHORITY_ROOT_OWNED_CONTRACT,
        EVIDENCE_ROOT_CONTRACT,
    ),
    ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_OFFER_HOLD_RECEIPT_CREATED,
        AIRLINE_ROOT_ID,
        corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX,
        AUTHORITY_EVIDENCE_ONLY_RECEIPT,
        EVIDENCE_RECEIPT_ONLY,
    ),
    ARTIFACT_CLIENT_PURCHASE_INTENT: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_PURCHASE_INTENT_CREATED,
        CLIENT_ROOT_ID,
        CLIENT_ROOT_ID,
        AUTHORITY_ROOT_OWNED_CONTRACT,
        EVIDENCE_ROOT_CONTRACT,
    ),
    ARTIFACT_BANK_PAYMENT_AUTHORIZATION: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_PAYMENT_AUTHORIZATION_CREATED,
        BANK_ROOT_ID,
        BANK_ROOT_ID,
        AUTHORITY_ROOT_OWNED_CONTRACT,
        EVIDENCE_PAYMENT_AUTHORIZATION,
    ),
    ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_TICKET_INTENT_CREATED,
        AIRLINE_ROOT_ID,
        AIRLINE_ROOT_ID,
        AUTHORITY_ROOT_OWNED_CONTRACT,
        EVIDENCE_ROOT_CONTRACT,
    ),
    ARTIFACT_MOCK_TICKET_RECEIPT: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_MOCK_TICKET_RECEIPT_CREATED,
        AIRLINE_ROOT_ID,
        corridor_contracts.ADAPTER_AIRLINE_TICKET_SANDBOX,
        AUTHORITY_EVIDENCE_ONLY_RECEIPT,
        EVIDENCE_RECEIPT_ONLY,
    ),
    ARTIFACT_MOCK_PURCHASE_RECEIPT: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_MOCK_PURCHASE_RECEIPT_CREATED,
        CLIENT_ROOT_ID,
        CREATED_BY_CLIENT_COMPLETION_OBSERVER,
        AUTHORITY_EVIDENCE_ONLY_RECEIPT,
        EVIDENCE_RECEIPT_ONLY,
    ),
    ARTIFACT_CLIENT_ROOT_FINAL: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_ROOT_FINAL_CREATED,
        CLIENT_ROOT_ID,
        CLIENT_ROOT_ID,
        AUTHORITY_ROOT_FINAL,
        EVIDENCE_ROOT_FINAL,
    ),
    ARTIFACT_AIRLINE_ROOT_FINAL: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_ROOT_FINAL_CREATED,
        AIRLINE_ROOT_ID,
        AIRLINE_ROOT_ID,
        AUTHORITY_ROOT_FINAL,
        EVIDENCE_ROOT_FINAL,
    ),
    ARTIFACT_BANK_ROOT_FINAL: _ArtifactProfile(
        CLASS_CANONICAL_LEDGER_ENTRY,
        EVENT_ROOT_FINAL_CREATED,
        BANK_ROOT_ID,
        BANK_ROOT_ID,
        AUTHORITY_ROOT_FINAL,
        EVIDENCE_ROOT_FINAL,
    ),
})

CLASSIFICATION_BY_ARTIFACT_TYPE: Mapping[str, str] = MappingProxyType({
    artifact_type: profile.classification
    for artifact_type, profile in ARTIFACT_PROFILES.items()
})
SOURCE_VALIDATION_REFERENCE_ARTIFACT_TYPES = (
    "ClientRootTravelConstraintSetV01",
    "AirlineRootOfferCandidateSetSnapshotV01",
    "AirlineSemanticSelectionInputV01",
    "AirlineSemanticOfferSelectionProposalV01",
    "AirlineCanonicalActorSelectionReviewV01",
    "AirlineSemanticSelectionSynthesisReportV01",
    "AirlineSemanticToContractBindingReportV01",
    "AirlinePurchaseApprovalEvidenceRefV01",
    "AirlineRootPhaseGateV01",
    "AirlineCorridorValidationReportV01",
    "AirlineTicketPurchaseCorridorRunReportV01",
)
AUXILIARY_OBSERVATION_REFERENCE_ARTIFACT_TYPES = (
    "ProviderPromptArtifactRefV01",
    "ProviderRawResponseArtifactRefV01",
)
EXCLUDED_RAW_PRIVATE_ARTIFACT_TYPES = (
    "RawPassportMaterialV01",
    "RawPaymentInstrumentMaterialV01",
)

EXPECTED_EVENT_TYPE_SEQUENCE = (
    EVENT_TRANSACTION_STARTED,
    EVENT_BSEP_PROJECTION_CREATED,
    EVENT_BSEP_PROJECTION_CREATED,
    EVENT_BSEP_PROJECTION_CREATED,
    EVENT_BSEP_PROJECTION_CREATED,
    EVENT_SEMANTIC_CLAIM_CREATED,
    EVENT_CLIENT_ROOT_SELECTION_DECIDED,
    EVENT_AIRLINE_ROOT_OFFER_RESOLVED,
    EVENT_OFFER_CREATED,
    EVENT_HOLD_CREATED,
    EVENT_OFFER_HOLD_RECEIPT_CREATED,
    EVENT_PURCHASE_INTENT_CREATED,
    EVENT_PAYMENT_AUTHORIZATION_CREATED,
    EVENT_TICKET_INTENT_CREATED,
    EVENT_MOCK_TICKET_RECEIPT_CREATED,
    EVENT_MOCK_PURCHASE_RECEIPT_CREATED,
    EVENT_ROOT_FINAL_CREATED,
    EVENT_ROOT_FINAL_CREATED,
    EVENT_ROOT_FINAL_CREATED,
)
EXPECTED_ARTIFACT_TYPE_SEQUENCE = (
    ARTIFACT_TRANSACTION_SCOPE,
    ARTIFACT_CLIENT_BSEP_PROJECTION,
    ARTIFACT_AIRLINE_BSEP_PROJECTION,
    ARTIFACT_BANK_BSEP_PROJECTION,
    ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
    ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE,
    ARTIFACT_CLIENT_ROOT_SELECTION_DECISION,
    ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION,
    ARTIFACT_AIRLINE_OFFER_PACKET,
    ARTIFACT_AIRLINE_HOLD_PACKET,
    ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
    ARTIFACT_CLIENT_PURCHASE_INTENT,
    ARTIFACT_BANK_PAYMENT_AUTHORIZATION,
    ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT,
    ARTIFACT_MOCK_TICKET_RECEIPT,
    ARTIFACT_MOCK_PURCHASE_RECEIPT,
    ARTIFACT_CLIENT_ROOT_FINAL,
    ARTIFACT_AIRLINE_ROOT_FINAL,
    ARTIFACT_BANK_ROOT_FINAL,
)

REQUIRED_SEMANTIC_SOURCE_REFS = (
    SOURCE_REF_CLIENT_CONSTRAINTS,
    SOURCE_REF_CANDIDATE_SNAPSHOT,
    SOURCE_REF_SELECTION_INPUT,
    SOURCE_REF_PROPOSAL,
    *SOURCE_REF_ACTOR_REVIEWS,
    SOURCE_REF_SYNTHESIS,
    SOURCE_REF_CAUSAL_BINDING,
)

EXPECTED_SOURCE_REFS_BY_ARTIFACT_TYPE: Mapping[str, tuple[str, ...]] = MappingProxyType({
    ARTIFACT_TRANSACTION_SCOPE: (),
    ARTIFACT_CLIENT_BSEP_PROJECTION: (),
    ARTIFACT_AIRLINE_BSEP_PROJECTION: (),
    ARTIFACT_BANK_BSEP_PROJECTION: (),
    ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (),
    ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: REQUIRED_SEMANTIC_SOURCE_REFS,
    ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (),
    ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (),
    ARTIFACT_AIRLINE_OFFER_PACKET: (),
    ARTIFACT_AIRLINE_HOLD_PACKET: (),
    ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (),
    ARTIFACT_CLIENT_PURCHASE_INTENT: (SOURCE_REF_HUMAN_APPROVAL,),
    ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (),
    ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (),
    ARTIFACT_MOCK_TICKET_RECEIPT: (),
    ARTIFACT_MOCK_PURCHASE_RECEIPT: (),
    ARTIFACT_CLIENT_ROOT_FINAL: (
        f"{SOURCE_REF_ROOT_PHASE_GATE_PREFIX}:{ARTIFACT_CLIENT_ROOT_FINAL}",
        SOURCE_REF_CORRIDOR_VALIDATION,
        SOURCE_REF_CORRIDOR_RUN,
    ),
    ARTIFACT_AIRLINE_ROOT_FINAL: (
        f"{SOURCE_REF_ROOT_PHASE_GATE_PREFIX}:{ARTIFACT_AIRLINE_ROOT_FINAL}",
        SOURCE_REF_CORRIDOR_VALIDATION,
        SOURCE_REF_CORRIDOR_RUN,
    ),
    ARTIFACT_BANK_ROOT_FINAL: (
        f"{SOURCE_REF_ROOT_PHASE_GATE_PREFIX}:{ARTIFACT_BANK_ROOT_FINAL}",
        SOURCE_REF_CORRIDOR_VALIDATION,
        SOURCE_REF_CORRIDOR_RUN,
    ),
})

EXPECTED_AUXILIARY_REFS_BY_ARTIFACT_TYPE: Mapping[str, tuple[str, ...]] = MappingProxyType({
    artifact_type: (
        (OPAQUE_PROMPT_REF, OPAQUE_RESPONSE_REF)
        if artifact_type == ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE
        else ()
    )
    for artifact_type in ARTIFACT_PROFILES
})

FORBIDDEN_HASH_INPUT_TOKENS = (
    "api_key",
    "credential",
    "secret",
    "passport",
    "card",
    "iban",
    "payment_token",
    "raw_private_profile",
    "raw_provider",
    "provider_text",
    "raw_prompt",
    "raw_response",
    "object at 0x",
)

CANONICAL_HASH_INPUT_BASE_KEYS = (
    "schema_version",
    "ledger_index",
    "event_type",
    "artifact_id",
    "artifact_type",
    "transaction_id",
    "root_owner",
    "created_by",
    "authority_class",
    "evidence_class",
    "depends_on",
    "source_validation_refs",
)

HASH_EXTRA_NONE = ()
HASH_EXTRA_SOURCE_SNAPSHOT = ("source_snapshot",)
HASH_EXTRA_SOURCE_REFS = (
    "source_run_ref",
    "source_causal_report_ref",
    "source_corridor_report_ref",
    *HASH_EXTRA_SOURCE_SNAPSHOT,
)
HASH_EXTRA_BSEP_LINEAGE = (
    "projection_id",
    "projection_ref",
    "bsep_packet_id",
    "side",
    *HASH_EXTRA_SOURCE_SNAPSHOT,
)
HASH_EXTRA_SELECTED_OFFER = ("selected_offer_id", *HASH_EXTRA_SOURCE_SNAPSHOT)
HASH_EXTRA_AUTHORITATIVE_OFFER = (
    "selected_offer_id",
    "amount",
    "currency",
    "route_ref",
    *HASH_EXTRA_SOURCE_SNAPSHOT,
)
HASH_EXTRA_HOLD_AND_OFFER = (
    "selected_offer_id",
    "hold_id",
    "amount",
    "currency",
    "route_ref",
    *HASH_EXTRA_SOURCE_SNAPSHOT,
)
HASH_EXTRA_ROOT_FINAL = (
    *HASH_EXTRA_HOLD_AND_OFFER,
    "source_artifact_refs",
)

CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE: Mapping[str, tuple[str, ...]] = MappingProxyType({
    ARTIFACT_TRANSACTION_SCOPE: HASH_EXTRA_SOURCE_REFS,
    ARTIFACT_CLIENT_BSEP_PROJECTION: HASH_EXTRA_BSEP_LINEAGE,
    ARTIFACT_AIRLINE_BSEP_PROJECTION: HASH_EXTRA_BSEP_LINEAGE,
    ARTIFACT_BANK_BSEP_PROJECTION: HASH_EXTRA_BSEP_LINEAGE,
    ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: HASH_EXTRA_BSEP_LINEAGE,
    ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: HASH_EXTRA_SELECTED_OFFER,
    ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: HASH_EXTRA_SELECTED_OFFER,
    ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: HASH_EXTRA_AUTHORITATIVE_OFFER,
    ARTIFACT_AIRLINE_OFFER_PACKET: HASH_EXTRA_AUTHORITATIVE_OFFER,
    ARTIFACT_AIRLINE_HOLD_PACKET: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_CLIENT_PURCHASE_INTENT: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_BANK_PAYMENT_AUTHORIZATION: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_MOCK_TICKET_RECEIPT: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_MOCK_PURCHASE_RECEIPT: HASH_EXTRA_HOLD_AND_OFFER,
    ARTIFACT_CLIENT_ROOT_FINAL: HASH_EXTRA_ROOT_FINAL,
    ARTIFACT_AIRLINE_ROOT_FINAL: HASH_EXTRA_ROOT_FINAL,
    ARTIFACT_BANK_ROOT_FINAL: HASH_EXTRA_ROOT_FINAL,
})


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _is_exact_int(value: Any) -> bool:
    return type(value) is int


def _is_exact_bool(value: Any) -> bool:
    return type(value) is bool


def _is_non_empty_string(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def _valid_string_tuple(value: Any) -> bool:
    if type(value) is not tuple:
        return False
    seen: set[str] = set()
    for item in value:
        if not _is_non_empty_string(item):
            return False
        if item in seen:
            return False
        seen.add(item)
    return True


def _valid_timestamp(value: Any) -> bool:
    return type(value) is str and bool(RFC3339_Z_RE.match(value))


def _expected_event_time(index: int) -> str:
    return _timestamp(FIXED_EVENT_TIME_PREFIX, index)


def _expected_recorded_at(index: int) -> str:
    return _timestamp(FIXED_RECORDED_TIME_PREFIX, index)


def _freeze_json(value: Any) -> Any:
    if isinstance(value, MappingABC):
        return _FrozenDict({
            key: _freeze_json(item)
            for key, item in value.items()
        })
    if type(value) is list:
        return tuple(_freeze_json(item) for item in value)
    if type(value) is tuple:
        return tuple(_freeze_json(item) for item in value)
    return value


def _canonical_hash_keyset_for_artifact_type(artifact_type: str) -> frozenset[str]:
    extras = (
        CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE.get(artifact_type)
        if _is_non_empty_string(artifact_type)
        else None
    )
    if extras is None:
        extras = ()
    return frozenset((*CANONICAL_HASH_INPUT_BASE_KEYS, *extras))


def _is_json_safe(value: Any) -> bool:
    if value is None:
        return True
    if type(value) in (str, bool, int):
        return True
    if type(value) is float:
        return math.isfinite(value)
    if type(value) in (list, tuple):
        return all(_is_json_safe(item) for item in value)
    if isinstance(value, MappingABC):
        return all(type(key) is str and _is_json_safe(item) for key, item in value.items())
    return False


def _contains_forbidden_hash_token(value: Any) -> bool:
    if type(value) is str:
        lowered = value.lower()
        return any(token in lowered for token in FORBIDDEN_HASH_INPUT_TOKENS)
    if type(value) in (list, tuple):
        return any(_contains_forbidden_hash_token(item) for item in value)
    if isinstance(value, MappingABC):
        return any(
            _contains_forbidden_hash_token(key)
            or _contains_forbidden_hash_token(item)
            for key, item in value.items()
        )
    return False


def _contains_forbidden_ref_token(value: Any) -> bool:
    if type(value) is not str:
        return True
    lowered = value.lower()
    return any(
        token in lowered
        for token in (
            "permission",
            "authority",
            "secret",
            "raw",
            "passport",
            "card",
            "iban",
            "payment_token",
            "credential",
        )
    )


def _is_raw_prompt_or_response_ref(value: Any) -> bool:
    if type(value) is not str:
        return False
    lowered = value.lower()
    if lowered in (OPAQUE_PROMPT_REF, OPAQUE_RESPONSE_REF):
        return True
    normalized = lowered.replace("\\", "/")
    basename = normalized.rsplit("/", 1)[-1]
    if basename.endswith(("_prompt.txt", "_raw_response.txt")):
        return True
    segments = tuple(
        segment
        for segment in re.split(r"[:/]+", normalized)
        if segment
    )
    return any(
        segment
        in (
            "raw_prompt",
            "raw_prompt_ref",
            "provider_prompt",
            "provider_prompt_file",
            "raw_response",
            "raw_response_ref",
            "provider_raw_response",
            "provider_raw_response_file",
            "provider_response_file",
        )
        for segment in segments
    )


def _offer_suffix(offer_id: str) -> str:
    if offer_id == OFFER_A_ID:
        return "001"
    if offer_id == OFFER_B_ID:
        return "002"
    raise ValueError(f"unknown_offer_id:{offer_id}")


def _offer_record(offer_id: str) -> binding.AirlineAuthoritativeOfferRecordV01:
    snapshot = binding.build_airline_candidate_snapshot_v01()
    for record in snapshot.authoritative_offer_records:
        if record.offer_id == offer_id:
            return record
    raise ValueError(f"unknown_offer_id:{offer_id}")


def _hold_id_for_offer(offer_id: str) -> str:
    suffix = _offer_suffix(offer_id)
    return f"hold:mock_airline_al:{suffix}"


def _timestamp(prefix: str, index: int) -> str:
    return f"{prefix}:{index:02d}:00Z"


def _artifact_ids_for_offer(offer_id: str) -> Mapping[str, str]:
    suffix = _offer_suffix(offer_id)
    return {
        ARTIFACT_TRANSACTION_SCOPE: f"airline_transaction_scope:{TRANSACTION_ID}",
        ARTIFACT_CLIENT_BSEP_PROJECTION: "bsep_projection:client:001",
        ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            "bsep_projection:airline_offer_selection:001"
        ),
        ARTIFACT_BANK_BSEP_PROJECTION: "bsep_projection:bank:001",
        ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: "bsep_projection:cross_root:001",
        ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
            f"canonical_selection:{offer_id}"
        ),
        ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            f"client_root_selection_decision:{suffix}"
        ),
        ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            f"airline_root_offer_resolution:{suffix}"
        ),
        ARTIFACT_AIRLINE_OFFER_PACKET: f"airline_offer_packet:mock_airline_al:{suffix}",
        ARTIFACT_AIRLINE_HOLD_PACKET: (
            f"airline_hold_commit_packet:mock_airline_al:{suffix}"
        ),
        ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
            f"offer_hold_receipt:mock_airline_al:{suffix}"
        ),
        ARTIFACT_CLIENT_PURCHASE_INTENT: f"client_purchase_intent:client_001:{suffix}",
        ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            f"bank_payment_authorization_ref:mock_bank_a:{suffix}"
        ),
        ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
            f"airline_ticket_issue_intent:mock_airline_al:{suffix}"
        ),
        ARTIFACT_MOCK_TICKET_RECEIPT: (
            f"mock_ticket_receipt:mock_airline_al:{suffix}"
        ),
        ARTIFACT_MOCK_PURCHASE_RECEIPT: (
            f"mock_purchase_receipt:client_001:{suffix}"
        ),
        ARTIFACT_CLIENT_ROOT_FINAL: f"client_root_final:{suffix}",
        ARTIFACT_AIRLINE_ROOT_FINAL: f"airline_root_final:{suffix}",
        ARTIFACT_BANK_ROOT_FINAL: f"bank_root_final:{suffix}",
    }


def _expected_dependencies_by_artifact_type(
    ids: Mapping[str, str],
) -> Mapping[str, tuple[str, ...]]:
    return {
        ARTIFACT_TRANSACTION_SCOPE: (),
        ARTIFACT_CLIENT_BSEP_PROJECTION: (ids[ARTIFACT_TRANSACTION_SCOPE],),
        ARTIFACT_AIRLINE_BSEP_PROJECTION: (ids[ARTIFACT_TRANSACTION_SCOPE],),
        ARTIFACT_BANK_BSEP_PROJECTION: (ids[ARTIFACT_TRANSACTION_SCOPE],),
        ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (ids[ARTIFACT_TRANSACTION_SCOPE],),
        ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
            ids[ARTIFACT_AIRLINE_BSEP_PROJECTION],
        ),
        ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            ids[ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE],
        ),
        ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            ids[ARTIFACT_CLIENT_ROOT_SELECTION_DECISION],
        ),
        ARTIFACT_AIRLINE_OFFER_PACKET: (
            ids[ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION],
        ),
        ARTIFACT_AIRLINE_HOLD_PACKET: (ids[ARTIFACT_AIRLINE_OFFER_PACKET],),
        ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
            ids[ARTIFACT_AIRLINE_HOLD_PACKET],
        ),
        ARTIFACT_CLIENT_PURCHASE_INTENT: (
            ids[ARTIFACT_AIRLINE_HOLD_PACKET],
        ),
        ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            ids[ARTIFACT_CLIENT_PURCHASE_INTENT],
        ),
        ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
            ids[ARTIFACT_AIRLINE_HOLD_PACKET],
            ids[ARTIFACT_CLIENT_PURCHASE_INTENT],
            ids[ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
        ),
        ARTIFACT_MOCK_TICKET_RECEIPT: (
            ids[ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT],
        ),
        ARTIFACT_MOCK_PURCHASE_RECEIPT: (
            ids[ARTIFACT_MOCK_TICKET_RECEIPT],
            ids[ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
            ids[ARTIFACT_CLIENT_PURCHASE_INTENT],
        ),
        ARTIFACT_CLIENT_ROOT_FINAL: (
            ids[ARTIFACT_CLIENT_ROOT_SELECTION_DECISION],
            ids[ARTIFACT_CLIENT_PURCHASE_INTENT],
            ids[ARTIFACT_MOCK_PURCHASE_RECEIPT],
        ),
        ARTIFACT_AIRLINE_ROOT_FINAL: (
            ids[ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION],
            ids[ARTIFACT_AIRLINE_OFFER_PACKET],
            ids[ARTIFACT_AIRLINE_HOLD_PACKET],
            ids[ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT],
            ids[ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT],
            ids[ARTIFACT_MOCK_TICKET_RECEIPT],
        ),
        ARTIFACT_BANK_ROOT_FINAL: (
            ids[ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
        ),
    }


def _fixture_source_identity_fields(
    *,
    artifact_type: str,
    artifact_id: str,
    depends_on: tuple[str, ...],
    expected_source_refs: AirlineTransactionArtifactLedgerExpectedSourceRefsV01 | None = None,
) -> Mapping[str, Any]:
    source_refs = expected_source_refs or build_airline_transaction_artifact_ledger_fixture_source_refs_v01()
    if artifact_type == ARTIFACT_TRANSACTION_SCOPE:
        return {
            "source_run_ref": source_refs.source_run_ref,
            "source_causal_report_ref": source_refs.source_causal_report_ref,
            "source_corridor_report_ref": source_refs.source_corridor_report_ref,
            "source_snapshot": {
                "transaction_id": TRANSACTION_ID,
                "source_run_ref": source_refs.source_run_ref,
                "source_causal_report_ref": source_refs.source_causal_report_ref,
                "source_corridor_report_ref": source_refs.source_corridor_report_ref,
            },
        }
    bsep_projection_refs = {
        ARTIFACT_CLIENT_BSEP_PROJECTION: (
            "bsep_projection:client:001",
            "client",
        ),
        ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            binding.BSEP_PROJECTION_REF,
            "airline",
        ),
        ARTIFACT_BANK_BSEP_PROJECTION: (
            "bsep_projection:bank:001",
            "bank",
        ),
        ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            "bsep_projection:cross_root:001",
            "cross_root_advisory",
        ),
    }
    if artifact_type in bsep_projection_refs:
        projection_ref, side = bsep_projection_refs[artifact_type]
        return {
            "projection_id": artifact_id,
            "projection_ref": projection_ref,
            "bsep_packet_id": "bsep_packet:deterministic_slice_b_fixture:001",
            "side": side,
            "source_snapshot": {
                "projection_id": artifact_id,
                "projection_ref": projection_ref,
                "bsep_packet_id": "bsep_packet:deterministic_slice_b_fixture:001",
                "side": side,
                "transaction_id": TRANSACTION_ID,
            },
        }
    if artifact_type in {
        ARTIFACT_CLIENT_ROOT_FINAL,
        ARTIFACT_AIRLINE_ROOT_FINAL,
        ARTIFACT_BANK_ROOT_FINAL,
    }:
        return {
            "source_artifact_refs": depends_on,
            "source_snapshot": {
                "source_artifact_refs": depends_on,
                "transaction_id": TRANSACTION_ID,
            },
        }
    return {"source_snapshot": {"artifact_id": artifact_id, "transaction_id": TRANSACTION_ID}}


def _expected_source_identity_fields_for_artifact(
    *,
    artifact_type: str,
    offer_id: str,
    hold_id: str,
    amount: int,
    currency: str,
    route_ref: str,
    source_identity_fields: Mapping[str, Any],
) -> Mapping[str, Any]:
    value: dict[str, Any] = {}
    for key in CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[artifact_type]:
        if key == "selected_offer_id":
            value[key] = offer_id
        elif key == "hold_id":
            value[key] = hold_id
        elif key == "amount":
            value[key] = amount
        elif key == "currency":
            value[key] = currency
        elif key == "route_ref":
            value[key] = route_ref
        else:
            value[key] = source_identity_fields.get(key)
    return value


def _fixture_expected_source_identity_fields_by_type(
    *,
    offer_id: str,
    expected_source_refs: AirlineTransactionArtifactLedgerExpectedSourceRefsV01 | None = None,
) -> Mapping[str, Mapping[str, Any]]:
    record = _offer_record(offer_id)
    hold_id = _hold_id_for_offer(offer_id)
    ids = _artifact_ids_for_offer(offer_id)
    dependencies = _expected_dependencies_by_artifact_type(ids)
    return {
        artifact_type: _expected_source_identity_fields_for_artifact(
            artifact_type=artifact_type,
            offer_id=offer_id,
            hold_id=hold_id,
            amount=record.amount,
            currency=record.currency,
            route_ref=record.route_ref,
            source_identity_fields=_fixture_source_identity_fields(
                artifact_type=artifact_type,
                artifact_id=ids[artifact_type],
                depends_on=dependencies[artifact_type],
                expected_source_refs=expected_source_refs,
            ),
        )
        for artifact_type in EXPECTED_ARTIFACT_TYPE_SEQUENCE
    }


def _canonical_hash_input_for_entry(
    *,
    entry_index: int,
    profile: _ArtifactProfile,
    artifact_id: str,
    artifact_type: str,
    depends_on: tuple[str, ...],
    source_validation_refs: tuple[str, ...],
    offer_id: str,
    hold_id: str,
    amount: int,
    currency: str,
    route_ref: str,
    source_identity_fields: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    source_fields = source_identity_fields or {}
    value: dict[str, Any] = {
        "schema_version": LEDGER_VERSION,
        "ledger_index": entry_index,
        "event_type": profile.event_type,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "transaction_id": TRANSACTION_ID,
        "root_owner": profile.root_owner,
        "created_by": profile.created_by,
        "authority_class": profile.authority_class,
        "evidence_class": profile.evidence_class,
        "depends_on": depends_on,
        "source_validation_refs": source_validation_refs,
    }
    for key in CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[artifact_type]:
        if key == "selected_offer_id":
            value[key] = offer_id
        elif key == "hold_id":
            value[key] = hold_id
        elif key == "amount":
            value[key] = amount
        elif key == "currency":
            value[key] = currency
        elif key == "route_ref":
            value[key] = route_ref
        else:
            value[key] = source_fields.get(key)
    return _freeze_json(value)


def _source_refs_for_entry(artifact_type: str) -> tuple[str, ...]:
    return EXPECTED_SOURCE_REFS_BY_ARTIFACT_TYPE[artifact_type]


def _aux_refs_for_entry(artifact_type: str) -> tuple[str, ...]:
    return EXPECTED_AUXILIARY_REFS_BY_ARTIFACT_TYPE[artifact_type]


def _entry(
    *,
    index: int,
    artifact_type: str,
    artifact_id: str,
    depends_on: tuple[str, ...],
    offer_id: str,
    hold_id: str,
    amount: int,
    currency: str,
    route_ref: str,
    source_identity_fields: Mapping[str, Any] | None = None,
) -> AirlineTransactionArtifactLedgerEntryV01:
    return _entry_with_exact_refs(
        index=index,
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        depends_on=depends_on,
        offer_id=offer_id,
        hold_id=hold_id,
        amount=amount,
        currency=currency,
        route_ref=route_ref,
        source_validation_refs=_source_refs_for_entry(artifact_type),
        auxiliary_artifact_refs=_aux_refs_for_entry(artifact_type),
        source_identity_fields=source_identity_fields,
    )


def _entry_with_exact_refs(
    *,
    index: int,
    artifact_type: str,
    artifact_id: str,
    depends_on: tuple[str, ...],
    offer_id: str,
    hold_id: str,
    amount: int,
    currency: str,
    route_ref: str,
    source_validation_refs: tuple[str, ...],
    auxiliary_artifact_refs: tuple[str, ...],
    source_identity_fields: Mapping[str, Any] | None = None,
) -> AirlineTransactionArtifactLedgerEntryV01:
    profile = ARTIFACT_PROFILES[artifact_type]
    return AirlineTransactionArtifactLedgerEntryV01(
        ledger_index=index,
        event_type=profile.event_type,
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        transaction_id=TRANSACTION_ID,
        root_owner=profile.root_owner,
        created_by=profile.created_by,
        authority_class=profile.authority_class,
        evidence_class=profile.evidence_class,
        depends_on=depends_on,
        event_time=_timestamp(FIXED_EVENT_TIME_PREFIX, index),
        recorded_at=_timestamp(FIXED_RECORDED_TIME_PREFIX, index),
        source_validation_refs=source_validation_refs,
        auxiliary_artifact_refs=auxiliary_artifact_refs,
        canonical_hash_input=_canonical_hash_input_for_entry(
            entry_index=index,
            profile=profile,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            depends_on=depends_on,
            source_validation_refs=source_validation_refs,
            offer_id=offer_id,
            hold_id=hold_id,
            amount=amount,
            currency=currency,
            route_ref=route_ref,
            source_identity_fields=source_identity_fields,
        ),
        raw_secret_included=False,
        raw_provider_text_included=False,
        ledger_created_authority=False,
        ledger_created_permission=False,
        ledger_created_action=False,
        real_world_effects_count=0,
    )


def build_airline_transaction_artifact_ledger_entry_from_source_v01(
    *,
    index: int,
    artifact_type: str,
    artifact_id: str,
    depends_on: tuple[str, ...],
    offer_id: str,
    hold_id: str,
    amount: int,
    currency: str,
    route_ref: str,
    source_validation_refs: tuple[str, ...],
    auxiliary_artifact_refs: tuple[str, ...],
    source_identity_fields: Mapping[str, Any],
) -> AirlineTransactionArtifactLedgerEntryV01:
    return _entry_with_exact_refs(
        index=index,
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        depends_on=depends_on,
        offer_id=offer_id,
        hold_id=hold_id,
        amount=amount,
        currency=currency,
        route_ref=route_ref,
        source_validation_refs=source_validation_refs,
        auxiliary_artifact_refs=auxiliary_artifact_refs,
        source_identity_fields=source_identity_fields,
    )


def _event_type_counts(
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        if type(entry.event_type) is str:
            counts[entry.event_type] = counts.get(entry.event_type, 0) + 1
    return _FrozenDict(dict(sorted(counts.items())))


def _dependency_edge_count(
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
) -> int:
    return sum(len(entry.depends_on) for entry in entries if type(entry.depends_on) is tuple)


def build_airline_transaction_artifact_ledger_fixture_v01(
    *,
    offer_id: str,
) -> AirlineTransactionArtifactLedgerV01:
    if offer_id not in VALID_LEDGER_OFFER_IDS:
        raise ValueError(f"unknown_offer_id:{offer_id}")
    record = _offer_record(offer_id)
    hold_id = _hold_id_for_offer(offer_id)
    ids = _artifact_ids_for_offer(offer_id)
    dependencies = _expected_dependencies_by_artifact_type(ids)
    entries = tuple(
        _entry(
            index=index,
            artifact_type=artifact_type,
            artifact_id=ids[artifact_type],
            depends_on=dependencies[artifact_type],
            offer_id=offer_id,
            hold_id=hold_id,
            amount=record.amount,
            currency=record.currency,
            route_ref=record.route_ref,
            source_identity_fields=_fixture_source_identity_fields(
                artifact_type=artifact_type,
                artifact_id=ids[artifact_type],
                depends_on=dependencies[artifact_type],
            ),
        )
        for index, artifact_type in enumerate(EXPECTED_ARTIFACT_TYPE_SEQUENCE)
    )
    return AirlineTransactionArtifactLedgerV01(
        ledger_id=f"airline_transaction_artifact_ledger:{offer_id}",
        ledger_version=LEDGER_VERSION,
        transaction_id=TRANSACTION_ID,
        source_run_ref=SOURCE_RUN_REF_FIXTURE,
        source_causal_report_ref=SOURCE_CAUSAL_REPORT_REF_FIXTURE,
        source_corridor_report_ref=SOURCE_CORRIDOR_REPORT_REF_FIXTURE,
        entries=entries,
        entry_count=len(entries),
        dependency_edge_count=_dependency_edge_count(entries),
        event_type_counts=_event_type_counts(entries),
        root_final_count=sum(
            1 for entry in entries if entry.event_type == EVENT_ROOT_FINAL_CREATED
        ),
        validation_status=STATUS_PASS,
        validation_errors=(),
        ledger_created_authority_count=0,
        ledger_created_permission_count=0,
        ledger_created_action_count=0,
        provider_called_count=0,
        network_used_count=0,
        gemini_called_count=0,
        real_world_effects_count=0,
    )


def build_valid_airline_transaction_artifact_ledger_offer_a_v01() -> (
    AirlineTransactionArtifactLedgerV01
):
    return build_airline_transaction_artifact_ledger_fixture_v01(offer_id=OFFER_A_ID)


def build_valid_airline_transaction_artifact_ledger_offer_b_v01() -> (
    AirlineTransactionArtifactLedgerV01
):
    return build_airline_transaction_artifact_ledger_fixture_v01(offer_id=OFFER_B_ID)


def build_airline_transaction_artifact_ledger_fixture_source_refs_v01() -> (
    AirlineTransactionArtifactLedgerExpectedSourceRefsV01
):
    return AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
        source_run_ref=SOURCE_RUN_REF_FIXTURE,
        source_causal_report_ref=SOURCE_CAUSAL_REPORT_REF_FIXTURE,
        source_corridor_report_ref=SOURCE_CORRIDOR_REPORT_REF_FIXTURE,
    )


def build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
    *,
    offer_id: str,
    expected_source_refs: AirlineTransactionArtifactLedgerExpectedSourceRefsV01 | None = None,
) -> AirlineTransactionArtifactLedgerExpectedIdentityV01:
    source_refs = (
        expected_source_refs
        if expected_source_refs is not None
        else build_airline_transaction_artifact_ledger_fixture_source_refs_v01()
    )
    return AirlineTransactionArtifactLedgerExpectedIdentityV01(
        expected_source_refs=source_refs,
        expected_artifact_ids=_artifact_ids_for_offer(offer_id),
        expected_source_validation_refs_by_type=EXPECTED_SOURCE_REFS_BY_ARTIFACT_TYPE,
        expected_auxiliary_artifact_refs_by_type=EXPECTED_AUXILIARY_REFS_BY_ARTIFACT_TYPE,
        expected_source_identity_fields_by_type=(
            _fixture_expected_source_identity_fields_by_type(
                offer_id=offer_id,
                expected_source_refs=source_refs,
            )
        ),
    )


def _canonical_hash_input_errors(
    entry: AirlineTransactionArtifactLedgerEntryV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    value = entry.canonical_hash_input
    if not isinstance(value, MappingABC):
        return (REASON_MALFORMED_CANONICAL_HASH_INPUT,)
    if not _is_json_safe(value):
        _append_reason(reasons, REASON_MALFORMED_CANONICAL_HASH_INPUT)
    if _contains_forbidden_hash_token(value):
        _append_reason(reasons, REASON_UNSAFE_CANONICAL_HASH_INPUT)
    if any(type(key) is not str for key in value.keys()):
        _append_reason(reasons, REASON_MALFORMED_CANONICAL_HASH_INPUT)
        return tuple(reasons)
    expected_keyset = _canonical_hash_keyset_for_artifact_type(entry.artifact_type)
    if frozenset(value.keys()) != expected_keyset:
        _append_reason(reasons, REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH)
    expected = {
        "schema_version": LEDGER_VERSION,
        "ledger_index": entry.ledger_index,
        "event_type": entry.event_type,
        "artifact_id": entry.artifact_id,
        "artifact_type": entry.artifact_type,
        "transaction_id": entry.transaction_id,
        "root_owner": entry.root_owner,
        "created_by": entry.created_by,
        "authority_class": entry.authority_class,
        "evidence_class": entry.evidence_class,
        "depends_on": entry.depends_on if type(entry.depends_on) is tuple else None,
        "source_validation_refs": (
            entry.source_validation_refs
            if type(entry.source_validation_refs) is tuple
            else None
        ),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            _append_reason(reasons, REASON_CANONICAL_HASH_INPUT_BINDING_MISMATCH)
            break
    extra_keys = (
        CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE.get(
            entry.artifact_type,
            (),
        )
        if _is_non_empty_string(entry.artifact_type)
        else ()
    )
    if "selected_offer_id" in extra_keys:
        offer_id = value.get("selected_offer_id")
        if offer_id not in VALID_LEDGER_OFFER_IDS:
            _append_reason(reasons, REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH)
            return tuple(reasons)
        record = _offer_record(offer_id)
        expected_source_facts = {
            "amount": record.amount,
            "currency": record.currency,
            "route_ref": record.route_ref,
        }
        for key, expected_value in expected_source_facts.items():
            if key in extra_keys and value.get(key) != expected_value:
                _append_reason(
                    reasons,
                    REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH,
                )
                break
    if entry.artifact_type == ARTIFACT_TRANSACTION_SCOPE:
        for key in (
            "source_run_ref",
            "source_causal_report_ref",
            "source_corridor_report_ref",
        ):
            if not _is_non_empty_string(value.get(key)):
                _append_reason(
                    reasons,
                    REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH,
                )
                break
    expected_bsep_sides = {
        ARTIFACT_CLIENT_BSEP_PROJECTION: "client",
        ARTIFACT_AIRLINE_BSEP_PROJECTION: "airline",
        ARTIFACT_BANK_BSEP_PROJECTION: "bank",
        ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: "cross_root_advisory",
    }
    if (
        _is_non_empty_string(entry.artifact_type)
        and entry.artifact_type in expected_bsep_sides
    ):
        if (
            value.get("projection_id") != entry.artifact_id
            or not _is_non_empty_string(value.get("projection_ref"))
            or not _is_non_empty_string(value.get("bsep_packet_id"))
            or value.get("side") != expected_bsep_sides[entry.artifact_type]
        ):
            _append_reason(
                reasons,
                REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH,
            )
    if _is_non_empty_string(entry.artifact_type) and entry.artifact_type in {
        ARTIFACT_CLIENT_ROOT_FINAL,
        ARTIFACT_AIRLINE_ROOT_FINAL,
        ARTIFACT_BANK_ROOT_FINAL,
    }:
        source_artifact_refs = value.get("source_artifact_refs")
        if (
            type(source_artifact_refs) is not tuple
            or not source_artifact_refs
            or not all(_is_non_empty_string(ref) for ref in source_artifact_refs)
        ):
            _append_reason(
                reasons,
                REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH,
            )
    return tuple(reasons)


def validate_airline_transaction_artifact_ledger_entry_v01(
    entry: AirlineTransactionArtifactLedgerEntryV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not isinstance(entry, AirlineTransactionArtifactLedgerEntryV01):
        return (REASON_MALFORMED_ENTRY,)
    if not _is_exact_int(entry.ledger_index):
        _append_reason(reasons, REASON_MALFORMED_ENTRY)
    elif entry.ledger_index < 0:
        _append_reason(reasons, REASON_NEGATIVE_INDEX)
    for field_name in (
        "event_type",
        "artifact_id",
        "artifact_type",
        "transaction_id",
        "root_owner",
        "created_by",
        "authority_class",
        "evidence_class",
    ):
        if not _is_non_empty_string(getattr(entry, field_name)):
            _append_reason(reasons, REASON_INVALID_STRING_FIELD)
    if entry.event_type in RESERVED_EVENT_TYPES:
        _append_reason(reasons, REASON_RESERVED_EVENT_TYPE)
    elif entry.event_type not in EMITTED_EVENT_TYPES:
        _append_reason(reasons, REASON_UNKNOWN_EVENT_TYPE)
    if entry.authority_class in FORBIDDEN_CLASSIFICATIONS:
        _append_reason(reasons, REASON_FORBIDDEN_CLASSIFICATION)
    elif entry.authority_class not in AUTHORITY_CLASSES:
        _append_reason(reasons, REASON_UNKNOWN_AUTHORITY_CLASS)
    if entry.evidence_class in FORBIDDEN_CLASSIFICATIONS:
        _append_reason(reasons, REASON_FORBIDDEN_CLASSIFICATION)
    elif entry.evidence_class not in EVIDENCE_CLASSES:
        _append_reason(reasons, REASON_UNKNOWN_EVIDENCE_CLASS)
    profile = (
        ARTIFACT_PROFILES.get(entry.artifact_type)
        if _is_non_empty_string(entry.artifact_type)
        else None
    )
    if profile is None:
        _append_reason(reasons, REASON_WRONG_ARTIFACT_CLASSIFICATION)
    else:
        if profile.event_type != entry.event_type:
            _append_reason(reasons, REASON_WRONG_ARTIFACT_CLASSIFICATION)
        if profile.root_owner != entry.root_owner:
            _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
        if profile.created_by != entry.created_by:
            if entry.artifact_type == "AirlinePurchaseApprovalEvidenceRefV01":
                _append_reason(reasons, REASON_HUMAN_APPROVAL_FABRICATED_CREATOR)
            else:
                _append_reason(reasons, REASON_WRONG_CREATED_BY)
        if profile.authority_class != entry.authority_class:
            _append_reason(reasons, REASON_WRONG_AUTHORITY_CLASS)
        if profile.evidence_class != entry.evidence_class:
            _append_reason(reasons, REASON_WRONG_EVIDENCE_CLASS)
    if not _valid_string_tuple(entry.depends_on):
        if type(entry.depends_on) is tuple and len(entry.depends_on) == 0:
            pass
        else:
            _append_reason(reasons, REASON_MALFORMED_DEPENDENCIES)
    if _valid_string_tuple(entry.depends_on) and len(set(entry.depends_on)) != len(entry.depends_on):
        _append_reason(reasons, REASON_DUPLICATE_DEPENDENCY)
    if not _valid_string_tuple(entry.source_validation_refs):
        if type(entry.source_validation_refs) is tuple and len(entry.source_validation_refs) == 0:
            pass
        else:
            _append_reason(reasons, REASON_MALFORMED_SOURCE_REFS)
    elif profile is not None:
        if any(_contains_forbidden_ref_token(ref) for ref in entry.source_validation_refs):
            _append_reason(reasons, REASON_UNSAFE_SOURCE_OR_AUXILIARY_REF)
    if not _valid_string_tuple(entry.auxiliary_artifact_refs):
        if type(entry.auxiliary_artifact_refs) is tuple and len(entry.auxiliary_artifact_refs) == 0:
            pass
        else:
            _append_reason(reasons, REASON_MALFORMED_AUXILIARY_REFS)
    elif profile is not None:
        unexpected_aux_refs = (
            ref
            for ref in entry.auxiliary_artifact_refs
            if ref not in (OPAQUE_PROMPT_REF, OPAQUE_RESPONSE_REF)
        )
        if any(_contains_forbidden_ref_token(ref) for ref in unexpected_aux_refs):
            _append_reason(reasons, REASON_UNSAFE_SOURCE_OR_AUXILIARY_REF)
    if not _valid_timestamp(entry.event_time) or not _valid_timestamp(entry.recorded_at):
        _append_reason(reasons, REASON_MALFORMED_TIMESTAMP)
    elif _is_exact_int(entry.ledger_index) and (
        entry.event_time != _expected_event_time(entry.ledger_index)
        or entry.recorded_at != _expected_recorded_at(entry.ledger_index)
    ):
        _append_reason(reasons, REASON_MALFORMED_TIMESTAMP)
    if not _is_exact_bool(entry.raw_secret_included) or entry.raw_secret_included:
        _append_reason(reasons, REASON_RAW_SECRET_INCLUDED)
    if not _is_exact_bool(entry.raw_provider_text_included) or entry.raw_provider_text_included:
        _append_reason(reasons, REASON_RAW_PROVIDER_TEXT_INCLUDED)
    if not _is_exact_bool(entry.ledger_created_authority) or entry.ledger_created_authority:
        _append_reason(reasons, REASON_LEDGER_CREATED_AUTHORITY)
    if not _is_exact_bool(entry.ledger_created_permission) or entry.ledger_created_permission:
        _append_reason(reasons, REASON_LEDGER_CREATED_PERMISSION)
    if not _is_exact_bool(entry.ledger_created_action) or entry.ledger_created_action:
        _append_reason(reasons, REASON_LEDGER_CREATED_ACTION)
    if (
        not _is_exact_int(entry.real_world_effects_count)
        or entry.real_world_effects_count != 0
    ):
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    for reason in _canonical_hash_input_errors(entry):
        _append_reason(reasons, reason)
    return tuple(reasons)


def _dependency_graph_has_cycle(
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
) -> bool:
    adjacency = {
        entry.artifact_id: tuple(
            dep for dep in entry.depends_on if _is_non_empty_string(dep)
        )
        for entry in entries
        if _is_non_empty_string(entry.artifact_id)
        and _valid_string_tuple(entry.depends_on)
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dep in adjacency.get(node, ()):
            if dep in adjacency and visit(dep):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in adjacency)


def _base_ledger_errors(
    ledger: AirlineTransactionArtifactLedgerV01,
    expected_identity: AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not isinstance(ledger, AirlineTransactionArtifactLedgerV01):
        return (REASON_MALFORMED_ENTRY,)
    if type(ledger.entries) is not tuple:
        return (REASON_MALFORMED_ENTRY,)
    for entry in ledger.entries:
        entry_reasons = validate_airline_transaction_artifact_ledger_entry_v01(entry)
        for reason in entry_reasons:
            _append_reason(reasons, reason)
    entries = tuple(
        entry
        for entry in ledger.entries
        if isinstance(entry, AirlineTransactionArtifactLedgerEntryV01)
    )
    indexes = [entry.ledger_index for entry in entries if _is_exact_int(entry.ledger_index)]
    if len(indexes) != len(set(indexes)):
        _append_reason(reasons, REASON_DUPLICATE_LEDGER_INDEX)
    if sorted(indexes) != list(range(len(entries))):
        _append_reason(reasons, REASON_NON_CONTIGUOUS_LEDGER_INDEX)
    artifact_ids = [
        entry.artifact_id for entry in entries if _is_non_empty_string(entry.artifact_id)
    ]
    if len(artifact_ids) != len(set(artifact_ids)):
        _append_reason(reasons, REASON_DUPLICATE_ARTIFACT_ID)
    transaction_ids = {
        entry.transaction_id
        for entry in entries
        if _is_non_empty_string(entry.transaction_id)
    }
    expected_transaction_ids = (
        {ledger.transaction_id}
        if _is_non_empty_string(ledger.transaction_id)
        else set()
    )
    if transaction_ids != expected_transaction_ids or ledger.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_MIXED_TRANSACTION_ID)
    transaction_started = [
        entry for entry in entries if entry.event_type == EVENT_TRANSACTION_STARTED
    ]
    if len(transaction_started) != 1:
        _append_reason(reasons, REASON_MULTIPLE_TRANSACTION_STARTED)
    elif transaction_started[0].ledger_index != 0:
        _append_reason(reasons, REASON_TRANSACTION_STARTED_NOT_INDEX_ZERO)
    if tuple(entry.event_type for entry in entries) != EXPECTED_EVENT_TYPE_SEQUENCE:
        _append_reason(reasons, REASON_WRONG_EVENT_ORDER)
    if tuple(entry.artifact_type for entry in entries) != EXPECTED_ARTIFACT_TYPE_SEQUENCE:
        _append_reason(reasons, REASON_MISSING_REQUIRED_EVENT)
    anchor_offer_id = _semantic_claim_anchor_offer_id(entries)
    if anchor_offer_id is None:
        _append_reason(reasons, REASON_OFFER_INCONSISTENCY)
    expected_ids_by_type = expected_identity.expected_artifact_ids
    if expected_ids_by_type:
        supplied_ids_by_type = {
            entry.artifact_type: entry.artifact_id
            for entry in entries
            if _is_non_empty_string(entry.artifact_type)
            and _is_non_empty_string(entry.artifact_id)
        }
        for artifact_type, expected_artifact_id in expected_ids_by_type.items():
            if supplied_ids_by_type.get(artifact_type) != expected_artifact_id:
                _append_reason(reasons, REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)
                break
    for reason in _expected_lineage_errors(entries, expected_identity):
        _append_reason(reasons, reason)
    bsep_packet_ids = []
    for artifact_type in (
        ARTIFACT_CLIENT_BSEP_PROJECTION,
        ARTIFACT_AIRLINE_BSEP_PROJECTION,
        ARTIFACT_BANK_BSEP_PROJECTION,
        ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
    ):
        entry = next(
            (item for item in entries if item.artifact_type == artifact_type),
            None,
        )
        if entry is None or not isinstance(entry.canonical_hash_input, MappingABC):
            continue
        packet_id = entry.canonical_hash_input.get("bsep_packet_id")
        if _is_non_empty_string(packet_id):
            bsep_packet_ids.append(packet_id)
    if bsep_packet_ids and len(set(bsep_packet_ids)) != 1:
        _append_reason(reasons, REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH)
    by_id = {
        entry.artifact_id: entry
        for entry in entries
        if _is_non_empty_string(entry.artifact_id)
    }
    index_by_id = {
        entry.artifact_id: entry.ledger_index
        for entry in entries
        if _is_non_empty_string(entry.artifact_id)
        and _is_exact_int(entry.ledger_index)
    }
    expected_dependencies = (
        _expected_dependencies_by_artifact_type(expected_ids_by_type)
        if expected_ids_by_type
        else {}
    )
    for entry in entries:
        if not _valid_string_tuple(entry.depends_on):
            continue
        for dep in entry.depends_on:
            if dep == entry.artifact_id:
                _append_reason(reasons, REASON_SELF_DEPENDENCY)
            if dep not in by_id:
                _append_reason(reasons, REASON_MISSING_DEPENDENCY)
            elif (
                dep in index_by_id
                and _is_exact_int(entry.ledger_index)
                and index_by_id[dep] >= entry.ledger_index
            ):
                _append_reason(reasons, REASON_DEPENDENCY_ON_LATER_ENTRY)
        expected = (
            expected_dependencies.get(entry.artifact_type)
            if _is_non_empty_string(entry.artifact_type)
            else None
        )
        if expected is not None and entry.depends_on != expected:
            missing = set(expected).difference(entry.depends_on)
            extra = set(entry.depends_on).difference(expected)
            if missing:
                _append_reason(reasons, REASON_MISSING_DEPENDENCY)
            if extra:
                _append_reason(reasons, REASON_EXTRA_UNDECLARED_DEPENDENCY)
    if _dependency_graph_has_cycle(entries):
        _append_reason(reasons, REASON_CYCLIC_DEPENDENCY)
    final_types = {
        entry.artifact_type
        for entry in entries
        if entry.event_type == EVENT_ROOT_FINAL_CREATED
        and _is_non_empty_string(entry.artifact_type)
    }
    if ARTIFACT_CLIENT_ROOT_FINAL not in final_types:
        _append_reason(reasons, REASON_MISSING_CLIENT_ROOT_FINAL)
    if ARTIFACT_AIRLINE_ROOT_FINAL not in final_types:
        _append_reason(reasons, REASON_MISSING_AIRLINE_ROOT_FINAL)
    if ARTIFACT_BANK_ROOT_FINAL not in final_types:
        _append_reason(reasons, REASON_MISSING_BANK_ROOT_FINAL)
    if any(
        entry.event_type == EVENT_ROOT_FINAL_CREATED
        and entry.root_owner == ROOT_OWNER_BSEP_CROSS_ROOT
        for entry in entries
    ):
        _append_reason(reasons, REASON_CROSS_ROOT_REVIEWER_AS_FOURTH_ROOT)
    index_by_type = {
        entry.artifact_type: entry.ledger_index
        for entry in entries
        if _is_non_empty_string(entry.artifact_type)
        and _is_exact_int(entry.ledger_index)
    }
    if (
        ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT in index_by_type
        and ARTIFACT_CLIENT_PURCHASE_INTENT in index_by_type
        and index_by_type[ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT]
        >= index_by_type[ARTIFACT_CLIENT_PURCHASE_INTENT]
    ):
        _append_reason(reasons, REASON_OFFER_HOLD_RECEIPT_NOT_BEFORE_PURCHASE_INTENT)
    if (
        ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT not in index_by_type
        and ARTIFACT_CLIENT_PURCHASE_INTENT in index_by_type
    ):
        _append_reason(reasons, REASON_OFFER_HOLD_RECEIPT_NOT_BEFORE_PURCHASE_INTENT)
    if ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE not in index_by_type:
        _append_reason(reasons, REASON_MISSING_REQUIRED_EVENT)
    if ARTIFACT_CLIENT_PURCHASE_INTENT not in index_by_type:
        _append_reason(reasons, REASON_MISSING_REQUIRED_EVENT)
    if any(
        entry.artifact_type == "AirlinePurchaseApprovalEvidenceRefV01"
        for entry in entries
    ):
        _append_reason(reasons, REASON_HUMAN_APPROVAL_FABRICATED_CREATOR)
    if any(
        _is_raw_prompt_or_response_ref(ref)
        for entry in entries
        for ref in (
            entry.source_validation_refs
            if _valid_string_tuple(entry.source_validation_refs)
            else ()
        )
    ):
        _append_reason(reasons, REASON_RAW_PROMPT_RESPONSE_NOT_AUXILIARY_ONLY)
    offer_values = set()
    for entry in entries:
        value = (
            entry.canonical_hash_input.get("selected_offer_id")
            if isinstance(entry.canonical_hash_input, MappingABC)
            else None
        )
        if type(value) is str:
            offer_values.add(value)
    if anchor_offer_id is None or offer_values != {anchor_offer_id}:
        _append_reason(reasons, REASON_OFFER_INCONSISTENCY)
    return tuple(reasons)


def _derived_counts(
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
) -> dict[str, int]:
    return {
        "entry_count": len(entries),
        "dependency_edge_count": _dependency_edge_count(entries),
        "root_final_count": sum(
            1 for entry in entries if entry.event_type == EVENT_ROOT_FINAL_CREATED
        ),
        "ledger_created_authority_count": sum(
            1 for entry in entries if entry.ledger_created_authority is True
        ),
        "ledger_created_permission_count": sum(
            1 for entry in entries if entry.ledger_created_permission is True
        ),
        "ledger_created_action_count": sum(
            1 for entry in entries if entry.ledger_created_action is True
        ),
        "raw_secret_included_count": sum(
            1 for entry in entries if entry.raw_secret_included is True
        ),
        "raw_provider_text_included_count": sum(
            1 for entry in entries if entry.raw_provider_text_included is True
        ),
        "real_world_effects_count": sum(
            entry.real_world_effects_count
            for entry in entries
            if _is_exact_int(entry.real_world_effects_count)
        ),
    }


def _event_type_counts_mapping_valid(value: Any) -> bool:
    if not isinstance(value, MappingABC):
        return False
    return all(
        _is_non_empty_string(key) and _is_exact_int(count) and count >= 0
        for key, count in value.items()
    )


def _validation_errors_tuple_valid(value: Any) -> bool:
    return _valid_string_tuple(value)


def _semantic_claim_anchor_offer_id(
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
) -> str | None:
    for entry in entries:
        if entry.artifact_type != ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE:
            continue
        if not isinstance(entry.canonical_hash_input, MappingABC):
            return None
        value = entry.canonical_hash_input.get("selected_offer_id")
        if value in VALID_LEDGER_OFFER_IDS:
            return value
        return None
    return None


def _expected_source_refs_errors(
    expected_source_refs: Any,
) -> tuple[str, ...]:
    if not isinstance(
        expected_source_refs,
        AirlineTransactionArtifactLedgerExpectedSourceRefsV01,
    ):
        return (REASON_SOURCE_REF_MISMATCH,)
    if (
        not _is_non_empty_string(expected_source_refs.source_run_ref)
        or not _is_non_empty_string(expected_source_refs.source_causal_report_ref)
        or not _is_non_empty_string(expected_source_refs.source_corridor_report_ref)
    ):
        return (REASON_SOURCE_REF_MISMATCH,)
    return ()


def _expected_identity_errors(
    expected_identity: Any,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not isinstance(
        expected_identity,
        AirlineTransactionArtifactLedgerExpectedIdentityV01,
    ):
        return (REASON_SOURCE_REF_MISMATCH,)
    for reason in _expected_source_refs_errors(expected_identity.expected_source_refs):
        _append_reason(reasons, reason)
    if not isinstance(expected_identity.expected_artifact_ids, MappingABC):
        _append_reason(reasons, REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)
    else:
        if set(expected_identity.expected_artifact_ids) != set(EXPECTED_ARTIFACT_TYPE_SEQUENCE):
            _append_reason(reasons, REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)
        values = tuple(expected_identity.expected_artifact_ids.values())
        if (
            not all(_is_non_empty_string(value) for value in values)
            or len(set(values)) != len(values)
        ):
            _append_reason(reasons, REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)
    expected_tuple_maps = (
        (
            expected_identity.expected_source_validation_refs_by_type,
            REASON_SOURCE_VALIDATION_REF_LINEAGE_MISMATCH,
        ),
        (
            expected_identity.expected_auxiliary_artifact_refs_by_type,
            REASON_AUXILIARY_REF_LINEAGE_MISMATCH,
        ),
    )
    for mapping_value, reason in expected_tuple_maps:
        if not isinstance(mapping_value, MappingABC):
            _append_reason(reasons, reason)
            continue
        if set(mapping_value) != set(EXPECTED_ARTIFACT_TYPE_SEQUENCE):
            _append_reason(reasons, reason)
            continue
        for refs in mapping_value.values():
            if not _valid_string_tuple(refs):
                _append_reason(reasons, reason)
                break
    source_identity = expected_identity.expected_source_identity_fields_by_type
    if not isinstance(source_identity, MappingABC):
        _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
    elif set(source_identity) != set(EXPECTED_ARTIFACT_TYPE_SEQUENCE):
        _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
    else:
        for artifact_type, fields in source_identity.items():
            if not isinstance(fields, MappingABC):
                _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
                break
            if any(type(key) is not str for key in fields.keys()):
                _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
                break
            expected_keys = set(
                CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[artifact_type],
            )
            if set(fields.keys()) != expected_keys or not _is_json_safe(fields):
                _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
                break
    return tuple(reasons)


def _expected_lineage_errors(
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
    expected_identity: AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    entries_by_type = {
        entry.artifact_type: entry
        for entry in entries
        if _is_non_empty_string(entry.artifact_type)
    }
    source_refs_by_type = expected_identity.expected_source_validation_refs_by_type
    auxiliary_refs_by_type = expected_identity.expected_auxiliary_artifact_refs_by_type
    source_identity_by_type = expected_identity.expected_source_identity_fields_by_type
    if not (
        isinstance(source_refs_by_type, MappingABC)
        and isinstance(auxiliary_refs_by_type, MappingABC)
        and isinstance(source_identity_by_type, MappingABC)
    ):
        return (
            REASON_SOURCE_VALIDATION_REF_LINEAGE_MISMATCH,
            REASON_AUXILIARY_REF_LINEAGE_MISMATCH,
            REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
        )
    for artifact_type in EXPECTED_ARTIFACT_TYPE_SEQUENCE:
        entry = entries_by_type.get(artifact_type)
        if entry is None:
            continue
        expected_source_refs = source_refs_by_type.get(artifact_type)
        if entry.source_validation_refs != expected_source_refs:
            _append_reason(reasons, REASON_SOURCE_VALIDATION_REF_LINEAGE_MISMATCH)
            _append_reason(reasons, REASON_SOURCE_VALIDATION_REFS_PROFILE_MISMATCH)
            if artifact_type == ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE:
                _append_reason(reasons, REASON_SEMANTIC_CLAIM_MISSING_SOURCE_REFS)
            if artifact_type == ARTIFACT_CLIENT_PURCHASE_INTENT:
                _append_reason(reasons, REASON_HUMAN_APPROVAL_NOT_SOURCE_REF)
        expected_aux_refs = auxiliary_refs_by_type.get(artifact_type)
        if entry.auxiliary_artifact_refs != expected_aux_refs:
            _append_reason(reasons, REASON_AUXILIARY_REF_LINEAGE_MISMATCH)
            _append_reason(reasons, REASON_AUXILIARY_ARTIFACT_REFS_PROFILE_MISMATCH)
        expected_source_identity = source_identity_by_type.get(artifact_type)
        if not isinstance(entry.canonical_hash_input, MappingABC):
            _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
            continue
        if not isinstance(expected_source_identity, MappingABC):
            _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
            continue
        actual_source_identity = {
            key: entry.canonical_hash_input.get(key)
            for key in CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[
                artifact_type
            ]
        }
        if actual_source_identity != dict(expected_source_identity):
            _append_reason(reasons, REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)
    return tuple(reasons)


def _expected_identity_for_validation(
    ledger: AirlineTransactionArtifactLedgerV01,
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
    *,
    expected_source_refs: AirlineTransactionArtifactLedgerExpectedSourceRefsV01 | None,
    expected_identity: AirlineTransactionArtifactLedgerExpectedIdentityV01 | None,
) -> AirlineTransactionArtifactLedgerExpectedIdentityV01:
    if expected_identity is not None:
        return expected_identity
    if expected_source_refs is not None and _expected_source_refs_errors(
        expected_source_refs,
    ):
        return AirlineTransactionArtifactLedgerExpectedIdentityV01(
            expected_source_refs=expected_source_refs,
            expected_artifact_ids={},
            expected_source_validation_refs_by_type={},
            expected_auxiliary_artifact_refs_by_type={},
            expected_source_identity_fields_by_type={},
        )
    source_refs = (
        expected_source_refs
        if expected_source_refs is not None
        else build_airline_transaction_artifact_ledger_fixture_source_refs_v01()
    )
    anchor_offer_id = _semantic_claim_anchor_offer_id(entries)
    if anchor_offer_id in VALID_LEDGER_OFFER_IDS:
        return build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
            offer_id=anchor_offer_id,
            expected_source_refs=source_refs,
        )
    return AirlineTransactionArtifactLedgerExpectedIdentityV01(
        expected_source_refs=source_refs,
        expected_artifact_ids={},
        expected_source_validation_refs_by_type={},
        expected_auxiliary_artifact_refs_by_type={},
        expected_source_identity_fields_by_type={},
    )


def _ledger_envelope_errors(
    ledger: AirlineTransactionArtifactLedgerV01,
    entries: tuple[AirlineTransactionArtifactLedgerEntryV01, ...],
    expected_identity: AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    expected_source_refs = expected_identity.expected_source_refs
    offer_id = _semantic_claim_anchor_offer_id(entries)
    expected_ledger_id = (
        f"airline_transaction_artifact_ledger:{offer_id}"
        if offer_id in VALID_LEDGER_OFFER_IDS
        else None
    )
    if (
        not _is_non_empty_string(ledger.ledger_id)
        or expected_ledger_id is None
        or ledger.ledger_id != expected_ledger_id
    ):
        _append_reason(reasons, REASON_LEDGER_ID_MISMATCH)
    if ledger.ledger_version != LEDGER_VERSION:
        _append_reason(reasons, REASON_LEDGER_VERSION_MISMATCH)
    if ledger.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_MIXED_TRANSACTION_ID)
    if (
        ledger.source_run_ref != expected_source_refs.source_run_ref
        or ledger.source_causal_report_ref
        != expected_source_refs.source_causal_report_ref
        or ledger.source_corridor_report_ref
        != expected_source_refs.source_corridor_report_ref
    ):
        _append_reason(reasons, REASON_LEDGER_SOURCE_REF_MISMATCH)
        _append_reason(reasons, REASON_SOURCE_REF_MISMATCH)
    transaction_entry = next(
        (
            entry
            for entry in entries
            if entry.artifact_type == ARTIFACT_TRANSACTION_SCOPE
            and isinstance(entry.canonical_hash_input, MappingABC)
        ),
        None,
    )
    if transaction_entry is not None:
        if (
            transaction_entry.canonical_hash_input.get("source_run_ref")
            != expected_source_refs.source_run_ref
            or transaction_entry.canonical_hash_input.get("source_causal_report_ref")
            != expected_source_refs.source_causal_report_ref
            or transaction_entry.canonical_hash_input.get("source_corridor_report_ref")
            != expected_source_refs.source_corridor_report_ref
        ):
            _append_reason(reasons, REASON_SOURCE_REF_MISMATCH)
    if ledger.validation_status not in (STATUS_PASS, STATUS_FAIL_CLOSED):
        _append_reason(reasons, REASON_LEDGER_STORED_VALIDATION_STATUS_MISMATCH)
    if not _validation_errors_tuple_valid(ledger.validation_errors):
        _append_reason(reasons, REASON_LEDGER_MALFORMED_VALIDATION_ERRORS)
    for field_name in (
        "entry_count",
        "dependency_edge_count",
        "root_final_count",
        "ledger_created_authority_count",
        "ledger_created_permission_count",
        "ledger_created_action_count",
        "provider_called_count",
        "network_used_count",
        "gemini_called_count",
        "real_world_effects_count",
    ):
        if not _is_exact_int(getattr(ledger, field_name)):
            _append_reason(reasons, REASON_LEDGER_MALFORMED_COUNT)
    if not _event_type_counts_mapping_valid(ledger.event_type_counts):
        _append_reason(reasons, REASON_LEDGER_MALFORMED_COUNT)
    return tuple(reasons)


def validate_airline_transaction_artifact_ledger_v01(
    ledger: AirlineTransactionArtifactLedgerV01,
    *,
    expected_source_refs: (
        AirlineTransactionArtifactLedgerExpectedSourceRefsV01 | None
    ) = None,
    expected_identity: (
        AirlineTransactionArtifactLedgerExpectedIdentityV01 | None
    ) = None,
) -> AirlineTransactionArtifactLedgerValidationReportV01:
    if not isinstance(ledger, AirlineTransactionArtifactLedgerV01):
        return AirlineTransactionArtifactLedgerValidationReportV01(
            validation_status=STATUS_FAIL_CLOSED,
            transaction_id="",
            entry_count=0,
            dependency_edge_count=0,
            event_type_counts={},
            root_final_count=0,
            indexes_valid=False,
            artifact_ids_unique=False,
            event_types_valid=False,
            transaction_identity_valid=False,
            dependencies_present=False,
            dependencies_ordered=False,
            dependency_graph_acyclic=False,
            root_ownership_valid=False,
            authority_classes_valid=False,
            evidence_classes_valid=False,
            canonical_hash_inputs_safe=False,
            raw_secret_boundary_valid=False,
            raw_provider_boundary_valid=False,
            ledger_non_authority_valid=False,
            real_effects_zero=False,
            validation_errors=(REASON_MALFORMED_ENTRY,),
        )
    raw_entries = ledger.entries if type(ledger.entries) is tuple else ()
    entries = tuple(
        entry
        for entry in raw_entries
        if isinstance(entry, AirlineTransactionArtifactLedgerEntryV01)
    )
    actual_expected_identity = _expected_identity_for_validation(
        ledger,
        entries,
        expected_source_refs=expected_source_refs,
        expected_identity=expected_identity,
    )
    expected_identity_errors = _expected_identity_errors(actual_expected_identity)
    safe_expected_identity = (
        actual_expected_identity
        if not expected_identity_errors
        else build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
            offer_id=OFFER_A_ID,
        )
    )
    base_errors = list(_base_ledger_errors(ledger, safe_expected_identity))
    for reason in expected_identity_errors:
        _append_reason(base_errors, reason)
    for reason in _ledger_envelope_errors(
        ledger,
        entries,
        safe_expected_identity,
    ):
        _append_reason(base_errors, reason)
    counts = _derived_counts(entries)
    event_counts = _event_type_counts(entries)
    if not _is_exact_int(ledger.entry_count) or ledger.entry_count != counts["entry_count"]:
        _append_reason(base_errors, REASON_LEDGER_ENTRY_COUNT_MISMATCH)
    if (
        not _is_exact_int(ledger.dependency_edge_count)
        or ledger.dependency_edge_count != counts["dependency_edge_count"]
    ):
        _append_reason(base_errors, REASON_LEDGER_DEPENDENCY_EDGE_COUNT_MISMATCH)
    if (
        not _event_type_counts_mapping_valid(ledger.event_type_counts)
        or dict(ledger.event_type_counts) != dict(event_counts)
    ):
        _append_reason(base_errors, REASON_LEDGER_EVENT_TYPE_COUNTS_MISMATCH)
    if (
        not _is_exact_int(ledger.root_final_count)
        or ledger.root_final_count != counts["root_final_count"]
        or counts["root_final_count"] != 3
    ):
        _append_reason(base_errors, REASON_LEDGER_ROOT_FINAL_COUNT_MISMATCH)
    if (
        not _is_exact_int(ledger.ledger_created_authority_count)
        or ledger.ledger_created_authority_count != counts["ledger_created_authority_count"]
        or not _is_exact_int(ledger.ledger_created_permission_count)
        or ledger.ledger_created_permission_count != counts["ledger_created_permission_count"]
        or not _is_exact_int(ledger.ledger_created_action_count)
        or ledger.ledger_created_action_count != counts["ledger_created_action_count"]
        or not _is_exact_int(ledger.provider_called_count)
        or ledger.provider_called_count != 0
        or not _is_exact_int(ledger.network_used_count)
        or ledger.network_used_count != 0
        or not _is_exact_int(ledger.gemini_called_count)
        or ledger.gemini_called_count != 0
        or not _is_exact_int(ledger.real_world_effects_count)
        or ledger.real_world_effects_count != counts["real_world_effects_count"]
        or ledger.real_world_effects_count != 0
        or counts["raw_secret_included_count"] != 0
        or counts["raw_provider_text_included_count"] != 0
    ):
        _append_reason(base_errors, REASON_LEDGER_DERIVED_COUNTER_MISMATCH)
    independent_errors = tuple(base_errors)
    expected_status = STATUS_PASS if not independent_errors else STATUS_FAIL_CLOSED
    validation_errors = list(independent_errors)
    stored_errors_match = (
        _validation_errors_tuple_valid(ledger.validation_errors)
        and ledger.validation_errors == independent_errors
    )
    if ledger.validation_status != expected_status or not stored_errors_match:
        _append_reason(validation_errors, REASON_LEDGER_STORED_VALIDATION_STATUS_MISMATCH)
    validation_error_tuple = tuple(validation_errors)
    entry_error_set = set(
        reason
        for entry in entries
        for reason in validate_airline_transaction_artifact_ledger_entry_v01(entry)
    )
    return AirlineTransactionArtifactLedgerValidationReportV01(
        validation_status=STATUS_PASS if not validation_error_tuple else STATUS_FAIL_CLOSED,
        transaction_id=ledger.transaction_id if type(ledger.transaction_id) is str else "",
        entry_count=counts["entry_count"],
        dependency_edge_count=counts["dependency_edge_count"],
        event_type_counts=event_counts,
        root_final_count=counts["root_final_count"],
        indexes_valid=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_DUPLICATE_LEDGER_INDEX,
                REASON_NON_CONTIGUOUS_LEDGER_INDEX,
                REASON_NEGATIVE_INDEX,
            )
        ),
        artifact_ids_unique=REASON_DUPLICATE_ARTIFACT_ID not in validation_error_tuple,
        event_types_valid=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_UNKNOWN_EVENT_TYPE,
                REASON_RESERVED_EVENT_TYPE,
                REASON_WRONG_EVENT_ORDER,
                REASON_MISSING_REQUIRED_EVENT,
            )
        ),
        transaction_identity_valid=REASON_MIXED_TRANSACTION_ID not in validation_error_tuple,
        dependencies_present=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_MISSING_DEPENDENCY,
                REASON_EXTRA_UNDECLARED_DEPENDENCY,
            )
        ),
        dependencies_ordered=REASON_DEPENDENCY_ON_LATER_ENTRY not in validation_error_tuple,
        dependency_graph_acyclic=REASON_CYCLIC_DEPENDENCY not in validation_error_tuple,
        root_ownership_valid=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_WRONG_ROOT_OWNER,
                REASON_CROSS_ROOT_REVIEWER_AS_FOURTH_ROOT,
            )
        ),
        authority_classes_valid=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_UNKNOWN_AUTHORITY_CLASS,
                REASON_WRONG_AUTHORITY_CLASS,
                REASON_FORBIDDEN_CLASSIFICATION,
            )
        ),
        evidence_classes_valid=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_UNKNOWN_EVIDENCE_CLASS,
                REASON_WRONG_EVIDENCE_CLASS,
                REASON_FORBIDDEN_CLASSIFICATION,
            )
        ),
        canonical_hash_inputs_safe=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_MALFORMED_CANONICAL_HASH_INPUT,
                REASON_UNSAFE_CANONICAL_HASH_INPUT,
                REASON_CANONICAL_HASH_INPUT_BINDING_MISMATCH,
                REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH,
                REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH,
            )
        ),
        raw_secret_boundary_valid=REASON_RAW_SECRET_INCLUDED not in entry_error_set,
        raw_provider_boundary_valid=REASON_RAW_PROVIDER_TEXT_INCLUDED not in entry_error_set,
        ledger_non_authority_valid=not any(
            reason in validation_error_tuple
            for reason in (
                REASON_LEDGER_CREATED_AUTHORITY,
                REASON_LEDGER_CREATED_PERMISSION,
                REASON_LEDGER_CREATED_ACTION,
            )
        ),
        real_effects_zero=REASON_NONZERO_REAL_WORLD_EFFECTS not in validation_error_tuple
        and counts["real_world_effects_count"] == 0,
        validation_errors=validation_error_tuple,
        ledger_created_authority_count=counts["ledger_created_authority_count"],
        ledger_created_permission_count=counts["ledger_created_permission_count"],
        ledger_created_action_count=counts["ledger_created_action_count"],
        raw_secret_included_count=counts["raw_secret_included_count"],
        raw_provider_text_included_count=counts["raw_provider_text_included_count"],
    )
