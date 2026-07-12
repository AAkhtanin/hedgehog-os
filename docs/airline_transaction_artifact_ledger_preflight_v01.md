# Airline Transaction Artifact Ledger v0.1 Preflight

## Document Header

- document_id: airline_transaction_artifact_ledger_preflight_v01
- document_status: PREFLIGHT
- observed_base_head: ee3a5ae
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- transaction_artifact_ledger_implemented: false
- crypto_artifact_seal_implemented: false
- sealed_trace_replay_verifier_implemented: false
- real_airline_api_called: false
- real_bank_api_called: false
- real_gds_api_called: false
- real_payment_executed: false
- real_ticket_issued: false
- real_booking_created: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false

This document is planning only. It creates no runtime, no tests, no ledger,
no cryptographic seal, no replay verifier, no provider call, no network call,
and no real-world effect.

## Source Basis Inspected

This dedicated preflight is based on the current committed Airline source
basis:

- `docs/airline_ticket_purchase_corridor_artifact_ledger_crypto_replay_preflight_v01.md`
- `docs/audit_reports/auditor_tri_party_airline_all_real_semantic_to_contract_causal_corridor_real_run_v01.log`
- `demo/run_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01.py`
- `tests/test_human_tri_party_airline_all_real_semantic_to_contract_causal_corridor_story_v01_runner.py`
- `hedgehog/domains/airline/semantic_to_contract_binding_v01.py`
- `hedgehog/domains/airline/semantic_to_contract_causal_runtime_v01.py`
- `hedgehog/domains/airline/ticket_purchase_corridor_v01.py`
- `hedgehog/domains/airline/ticket_purchase_corridor_runtime_v01.py`
- `demo/run_tri_party_airline_live_semantic_lane_v01.py`
- `demo/run_tri_party_airline_ticket_purchase_mock_e2e_v01.py`

The Ledger gate is now open because these prior facts are closed:

- deterministic semantic-to-contract proof: PASS
- all-real provider causal run: PASS
- combined causal/corridor audit: PASS
- deterministic Ticket/Purchase Corridor: PASS
- all-real human story renderer: PASS
- zero real-world effects

The Ledger itself is not implemented.

## Purpose

Airline Transaction Artifact Ledger v0.1 is planned as a deterministic,
immutable, ordered, dependency-aware, machine-readable, fail-closed record of
the canonical artifacts produced by one Airline transaction.

It answers:

- what artifacts exist
- which transaction they belong to
- who created each artifact
- which Root owns its authority boundary
- whether it is authority, bounded context, validation evidence, or
  evidence only
- which earlier artifacts it depends on
- which artifacts form the canonical transaction chain
- which artifacts remain auxiliary observations only

The Ledger is not:

- a database product
- a blockchain
- a cryptographic seal
- a signature
- a hash chain
- a replay engine
- an authority engine
- a permission engine
- an executor
- a Root
- a fourth Root
- a packet registry
- a truth engine
- a replacement for DRS
- a replacement for audit logs

Core sentence:

```text
Ledger records trace.
Ledger does not authorize.
Ledger does not prove truth.
Ledger does not execute.
```

## Core / Domain Boundary

The first implementation belongs under the Airline domain package:

- `hedgehog/domains/airline/transaction_artifact_ledger_v01.py`
- `tests/test_airline_transaction_artifact_ledger_v01.py`

It must not initially be placed in:

- `hedgehog/transaction_artifact_ledger_v01.py`
- universal core modules
- ActionCommitPacket core
- DRS core
- RootOrchestrator core

This is not Hedgehog OS universal kernel/core. It is an Airline domain
projection.

Reason: Airline event names and artifact relations are domain-specific:

- offer
- hold
- purchase intent
- payment authorization
- ticket intent
- ticket receipt
- purchase receipt

The reusable laws are domain-neutral:

- unique artifact identity
- one transaction identity
- ordered entries
- dependency integrity
- acyclic dependency graph
- Root ownership
- evidence/authority classification
- no secret leakage
- no authority creation by observation
- fail-closed validation

Do not extract a generic Ledger core in this program. Generic extraction may be
considered only after equivalent structures are demonstrated in at least two
actually implemented and explicitly approved domain projections. Do not
introduce an unnamed comparison domain. Do not mention or invent a second
factory domain. The Ledger is not an installed Needle. A future Airline
capability package may compose it, but that is outside this preflight.

## Planned Contracts

Slice B should plan frozen local contracts.

### AirlineTransactionArtifactLedgerEntryV01

Required fields:

- ledger_index: int
- event_type: str
- artifact_id: str
- artifact_type: str
- transaction_id: str
- root_owner: str
- created_by: str
- authority_class: str
- evidence_class: str
- depends_on: tuple[str, ...]
- event_time: str
- recorded_at: str
- source_validation_refs: tuple[str, ...]
- auxiliary_artifact_refs: tuple[str, ...]
- canonical_hash_input: mapping
- raw_secret_included: bool
- raw_provider_text_included: bool
- ledger_created_authority: bool
- ledger_created_permission: bool
- ledger_created_action: bool
- real_world_effects_count: int

### AirlineTransactionArtifactLedgerV01

Required fields:

- ledger_id
- ledger_version
- transaction_id
- source_run_ref
- source_causal_report_ref
- source_corridor_report_ref
- entries
- entry_count
- dependency_edge_count
- event_type_counts
- root_final_count
- validation_status
- validation_errors
- ledger_created_authority_count
- ledger_created_permission_count
- ledger_created_action_count
- provider_called_count
- network_used_count
- gemini_called_count
- real_world_effects_count

### AirlineTransactionArtifactLedgerValidationReportV01

Required fields:

- validation_status
- transaction_id
- entry_count
- indexes_valid
- artifact_ids_unique
- event_types_valid
- transaction_identity_valid
- dependencies_present
- dependencies_ordered
- dependency_graph_acyclic
- root_ownership_valid
- authority_classes_valid
- evidence_classes_valid
- canonical_hash_inputs_safe
- raw_secret_boundary_valid
- raw_provider_boundary_valid
- ledger_non_authority_valid
- real_effects_zero
- validation_errors

Naming may be refined to match repository conventions, but these
responsibilities must not be removed.

## Event Taxonomy

Required umbrella event types:

- transaction_started
- semantic_claim_created
- bsep_projection_created
- offer_created
- hold_created
- offer_hold_receipt_created
- purchase_intent_created
- payment_authorization_created
- ticket_intent_created
- mock_ticket_receipt_created
- mock_purchase_receipt_created
- root_final_created

Additional causally necessary event types are required to preserve honest
lineage:

- client_root_selection_decided
- airline_root_offer_resolved

Reserved future event type:

- human_approval_recorded

`human_approval_recorded` is not emitted in Slice B v0.1. The current
`AirlinePurchaseApprovalEvidenceRefV01` source contract carries
`approval_ref`, `transaction_id`, `client_root_id`, scope, and evidence-only
flags, but it does not independently carry `created_by` and `root_owner`
fields. It is therefore a source validation reference in v0.1. It may become
canonical only after an explicitly attributed source contract exists.

The following current artifacts must not be omitted silently:

- `ClientRootOfferSelectionDecisionV01`
- `AirlineRootSelectedOfferResolutionV01`
- `AirlinePurchaseApprovalEvidenceRefV01`
- `AirlineOfferHoldReceiptV01`
- corridor validation report
- Root phase gates
- causal binding report
- semantic synthesis report

Every current transaction artifact must be classified as exactly one of:

1. canonical ledger entry
2. source validation reference
3. auxiliary observation reference
4. excluded raw/private material

Do not claim an exact canonical entry count until the artifact-to-ledger
mapping is frozen in implementation.

## Artifact-To-Ledger Mapping

This artifact-to-ledger mapping is the planned basis for Slice B/C review.
Every mapped current artifact has exactly one classification.

| Current artifact class | Exact classification | Ledger event type or reference role | Root owner / authority boundary | Authority class | Evidence class | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Transaction identity / source run ref | canonical ledger entry | transaction_started | non-authoritative transaction scope | none | transaction_metadata | Starts the one transaction. |
| Validated canonical semantic evidence | canonical ledger entry | semantic_claim_created | runtime canonicalization, advisory only | advisory_canonical | canonical_semantic_evidence | Built from validated evidence, not raw provider response. |
| `ClientRootTravelConstraintSetV01` | source validation reference | semantic_claim_created input reference | ClientRoot constraint evidence | none | validation_evidence | Feeds the canonical semantic claim and ClientRoot decision. |
| `AirlineRootOfferCandidateSetSnapshotV01` | source validation reference | semantic_claim_created input reference | AirlineRoot snapshot evidence | none | validation_evidence | Feeds selection input and AirlineRoot resolution. |
| `AirlineSemanticSelectionInputV01` | source validation reference | semantic_claim_created input reference | bounded semantic input | none | validation_evidence | Carries BSEP, constraints, and snapshot lineage. |
| `AirlineSemanticOfferSelectionProposalV01` | source validation reference | semantic_claim_created proposal reference | advisory provider proposal after validation | none | validation_evidence | Provider proposal remains advisory. |
| Five `AirlineCanonicalActorSelectionReviewV01` artifacts | source validation reference | semantic_claim_created review references | advisory canonical reviews | none | validation_evidence | Five causal actor reviews feed synthesis. |
| `AirlineSemanticSelectionSynthesisReportV01` | source validation reference | semantic_claim_created synthesis reference | advisory only | none | validation_evidence | Semantic synthesis reports are source validation references only. |
| `AirlineSemanticToContractBindingReportV01` | source validation reference | semantic_claim_created binding reference | validation evidence | none | validation_evidence | Causal binding reports are source validation references only. |
| Client BSEP projection | canonical ledger entry | bsep_projection_created | Client side bounded context | bounded_context_non_authoritative | bounded_semantic_context | Non-authoritative bounded context. |
| Airline BSEP projection | canonical ledger entry | bsep_projection_created | Airline side bounded context | bounded_context_non_authoritative | bounded_semantic_context | Semantic claim depends on this validated projection. |
| Bank BSEP projection | canonical ledger entry | bsep_projection_created | Bank side bounded context | bounded_context_non_authoritative | bounded_semantic_context | Non-authoritative bounded context. |
| Cross-root advisory BSEP projection | canonical ledger entry | bsep_projection_created | cross-root advisory only | bounded_context_non_authoritative | bounded_semantic_context | Not a fourth Root. |
| `ClientRootOfferSelectionDecisionV01` | canonical ledger entry | client_root_selection_decided | ClientRoot | root_decision | root_decision_evidence | Scoped Root decision. |
| `AirlineRootSelectedOfferResolutionV01` | canonical ledger entry | airline_root_offer_resolved | AirlineRoot | root_decision | root_decision_evidence | Authoritative offer facts from snapshot. |
| `AirlineOfferPacketV01` | canonical ledger entry | offer_created | AirlineRoot | root_owned_contract | root_contract_artifact | Root-owned offer artifact. |
| `AirlineHoldCommitPacketV01` | canonical ledger entry | hold_created | AirlineRoot | root_owned_contract | root_contract_artifact | Root-created hold contract. |
| `AirlineOfferHoldReceiptV01` | canonical ledger entry | offer_hold_receipt_created | AirlineRoot | evidence_only_receipt | receipt_evidence_only | Created by `airline_hold_sandbox_v01`; depends on hold_created; creates no payment, purchase, ticket, or future permission. |
| `AirlinePurchaseApprovalEvidenceRefV01` | source validation reference | purchase_intent_created approval_ref | ClientRoot evidence scope | none | human_approval_evidence | Not a canonical ledger entry in v0.1; purchase_intent_created carries `approval_ref` in source_validation_refs; approval evidence is not assigned a fabricated creator. |
| `ClientPurchaseIntentV01` | canonical ledger entry | purchase_intent_created | ClientRoot | root_owned_contract | root_contract_artifact | Does not grant BankRoot or AirlineRoot authority. |
| `BankPaymentAuthorizationRefV01` | canonical ledger entry | payment_authorization_created | BankRoot | root_owned_contract | payment_authorization_evidence | Evidence-only remains true; settlement, real payment, ticket permission, and future permission remain false. |
| `AirlineTicketIssueIntentV01` | canonical ledger entry | ticket_intent_created | AirlineRoot | root_owned_contract | root_contract_artifact | Mock ticket issue intent only. |
| `MockTicketReceiptV01` | canonical ledger entry | mock_ticket_receipt_created | AirlineRoot | evidence_only_receipt | receipt_evidence_only | Created by `airline_ticket_sandbox_v01`; not a real ticket. |
| `MockPurchaseReceiptV01` | canonical ledger entry | mock_purchase_receipt_created | ClientRoot | evidence_only_receipt | receipt_evidence_only | Created by `client_completion_observer`; evidence-only completion receipt. |
| ClientRoot final | canonical ledger entry | root_final_created | ClientRoot | root_final | root_final_evidence | Side-specific final. |
| AirlineRoot final | canonical ledger entry | root_final_created | AirlineRoot | root_final | root_final_evidence | Side-specific final. |
| BankRoot final | canonical ledger entry | root_final_created | BankRoot | root_final | root_final_evidence | Side-specific final. |
| Root phase gates | source validation reference | phase gate references | side-specific Root boundary | none | validation_evidence | Root phase gates are source validation references only. |
| Corridor validation report | source validation reference | corridor validation reference | validation evidence | none | validation_evidence | Corridor validation reports are source validation references only. |
| Corridor run report / contract context | source validation reference | corridor report reference | validation evidence | none | validation_evidence | Confirms per-run context and selected offer. |
| Raw prompts | auxiliary observation reference | opaque prompt ref | none | none | validation_evidence | Raw prompts are auxiliary observation references only. |
| Raw responses | auxiliary observation reference | opaque raw response ref | none | none | validation_evidence | Raw responses are auxiliary observation references only and never copied into canonical_hash_input. |
| Secret/private raw material | excluded raw/private material | excluded | none | none | none | Excluded raw/private material only. |

Raw prompts and raw responses remain auxiliary observation references only.
They are never authority, never canonical semantic evidence, and never copied
into canonical_hash_input.

## Ordering

The ledger order must reflect actual transaction causality, not the textual
order of the event-type list and not wall-clock sorting.

Required causal order:

1. transaction_started
2. actual BSEP projections are created and validated
3. validated canonical semantic claim/evidence is created
4. ClientRoot makes its scoped selection decision
5. AirlineRoot resolves authoritative offer facts
6. Airline offer and hold artifacts are created
7. Airline hold receipt evidence is recorded
8. human approval evidence is referenced as source validation evidence
9. ClientRoot purchase intent is created
10. BankRoot payment authorization is recorded
11. AirlineRoot ticket intent is created
12. evidence-only mock ticket and purchase receipts are recorded
13. side-specific Root finals are recorded

`ledger_index` defines canonical order. `event_time` and `recorded_at` remain
evidence metadata.

For deterministic fixtures:

- use explicit fixed RFC3339 timestamps
- do not use `datetime.now()` in tests
- no hidden timezone assumptions
- equal timestamps must not make order ambiguous

## Dependency Rules

The planned validator must require:

- every dependency artifact exists
- dependencies point only to earlier ledger entries
- no self-dependency
- no cycle
- no undeclared dependency
- no dependency repair
- no automatic insertion of a missing artifact
- no silent reordering

Minimum dependency model:

- BSEP projections depend on transaction_started.
- semantic_claim_created depends on the actual validated Airline BSEP
  projection and its selection input lineage.
- client_root_selection_decided depends on semantic_claim_created plus
  deterministic ClientRoot constraints.
- airline_root_offer_resolved depends on client_root_selection_decided plus
  the immutable candidate snapshot.
- offer_created depends on airline_root_offer_resolved.
- hold_created depends on offer_created.
- offer_hold_receipt_created depends on hold_created.
- purchase_intent_created depends on offer_hold_receipt_created plus the
  `AirlinePurchaseApprovalEvidenceRefV01` source validation reference.
- payment_authorization_created depends on purchase_intent_created.
- ticket_intent_created depends on hold_created, purchase_intent_created, and
  payment_authorization_created.
- mock_ticket_receipt_created depends on ticket_intent_created.
- mock_purchase_receipt_created depends on mock_ticket_receipt_created,
  payment_authorization_created, and purchase_intent_created.
- each root_final_created depends only on the relevant side-local evidence set.

A Root final must not depend on foreign authority. Evidence may cross Roots.
Authority must not cross Roots.

## Root Ownership Matrix

Allowed ownership must be closed and explicit.

| Ledger artifact family | Classification | Root owner | Created by | Authority class | Evidence class |
| --- | --- | --- | --- | --- | --- |
| transaction_started | canonical ledger entry | non-authoritative transaction scope marker | deterministic runtime/collector | none | transaction_metadata |
| BSEP projections | canonical ledger entry | side-scoped context owner | bounded semantic membrane builder | bounded_context_non_authoritative | bounded_semantic_context |
| canonical semantic evidence | canonical ledger entry | advisory runtime canonicalization | runtime canonicalization | advisory_canonical | canonical_semantic_evidence |
| ClientRoot selection decision | canonical ledger entry | ClientRoot | ClientRoot | root_decision | root_decision_evidence |
| AirlinePurchaseApprovalEvidenceRefV01 | source validation reference | ClientRoot evidence scope by `client_root_id` | not emitted as a ledger entry in v0.1 | none | human_approval_evidence |
| ClientPurchaseIntentV01 | canonical ledger entry | ClientRoot | ClientRoot | root_owned_contract | root_contract_artifact |
| ClientRoot final | canonical ledger entry | ClientRoot | ClientRoot | root_final | root_final_evidence |
| MockPurchaseReceiptV01 | canonical ledger entry | ClientRoot | client_completion_observer | evidence_only_receipt | receipt_evidence_only |
| AirlineRoot selected-offer resolution | canonical ledger entry | AirlineRoot | AirlineRoot | root_decision | root_decision_evidence |
| AirlineOfferPacketV01 | canonical ledger entry | AirlineRoot | AirlineRoot | root_owned_contract | root_contract_artifact |
| AirlineHoldCommitPacketV01 | canonical ledger entry | AirlineRoot | AirlineRoot | root_owned_contract | root_contract_artifact |
| AirlineOfferHoldReceiptV01 | canonical ledger entry | AirlineRoot | airline_hold_sandbox_v01 | evidence_only_receipt | receipt_evidence_only |
| AirlineTicketIssueIntentV01 | canonical ledger entry | AirlineRoot | AirlineRoot | root_owned_contract | root_contract_artifact |
| AirlineRoot final | canonical ledger entry | AirlineRoot | AirlineRoot | root_final | root_final_evidence |
| MockTicketReceiptV01 | canonical ledger entry | AirlineRoot | airline_ticket_sandbox_v01 | evidence_only_receipt | receipt_evidence_only |
| BankPaymentAuthorizationRefV01 | canonical ledger entry | BankRoot | BankRoot | root_owned_contract | payment_authorization_evidence |
| BankRoot final | canonical ledger entry | BankRoot | BankRoot | root_final | root_final_evidence |
| Cross-root advisory BSEP projection | canonical ledger entry | advisory only | bounded semantic membrane builder | bounded_context_non_authoritative | bounded_semantic_context |
| Cross-root reviewer output | source validation reference | advisory only | bounded semantic/runtime validation | none | validation_evidence |

The cross-root reviewer/projection is advisory only, not a fourth Root and not
shared Root authority.

## Authority And Evidence Classes

Planned closed authority class allowlist:

- none
- bounded_context_non_authoritative
- advisory_canonical
- root_decision
- root_owned_contract
- evidence_only_receipt
- root_final

Planned closed evidence class allowlist:

- transaction_metadata
- bounded_semantic_context
- canonical_semantic_evidence
- root_decision_evidence
- root_contract_artifact
- validation_evidence
- human_approval_evidence
- payment_authorization_evidence
- receipt_evidence_only
- root_final_evidence

Forbidden classes:

- provider_authority
- ledger_authority
- ledger_permission
- receipt_permission
- receipt_root_final
- raw_provider_truth
- hash_proves_truth
- shared_cross_root_authority

Ledger classification records the source artifact's class. Classification does
not create that class.

## Canonical Hash Input Boundary

`canonical_hash_input` is preparation for the later Crypto gate.

It is not:

- a hash
- a signature
- a manifest
- a seal
- a hash chain

It must be:

- deterministic
- JSON-serializable
- allowlist-built
- source-derived
- independent of dictionary insertion order
- independent of memory addresses
- free of runtime object repr strings
- free of raw model output
- free of secrets

It may contain:

- schema/profile version
- ledger index
- event type
- artifact identity
- artifact type
- transaction identity
- Root owner
- created_by
- authority/evidence class
- dependency ids
- allowlisted canonical source fields
- source validation refs

It must not contain:

- raw prompt
- raw provider response
- API key
- raw passport
- card details
- IBAN
- payment token
- credentials
- unbounded private profile
- Python repr of dataclass/object
- wall-clock-generated random content

No SHA-256 computation is implemented in Ledger Slice B. Crypto Artifact Seal
remains blocked.

## Auxiliary Observation Artifacts

Raw provider prompts and responses remain observable auxiliary artifacts.

The Ledger may reference them only by opaque artifact reference.

Rules:

- raw text is not copied into a canonical entry
- raw text is not authority
- raw text is not truth
- raw text is not permission
- raw text is not canonical_hash_input
- raw text does not determine Root ownership
- removing an optional raw observation must not change an already validated
  canonical transaction meaning
- missing required canonical evidence must still fail closed

## Independent Derived-Field Recomputation

The whole-ledger validator must independently recompute derived facts from
entries. Stored fields must never be accepted as proof of themselves.

The validator must recompute:

- entry_count
- dependency_edge_count
- event_type_counts
- root_final_count
- transaction_id set
- ledger-created authority count
- ledger-created permission count
- ledger-created action count
- raw-secret count
- raw-provider-text count
- real-world-effects count

Required checks:

- stored `entry_count == len(entries)`
- stored `dependency_edge_count == sum(len(entry.depends_on) for entry in entries)`
- stored `event_type_counts` equals independently recomputed event counts
- stored `root_final_count` equals independently counted Root final entries
- `root_final_count == 3` for the valid Airline fixture
- all stored zero counters equal recomputed zero counters
- `validation_status` and `validation_errors` are produced by the independent
  validator and cannot override invalid entries

Stable planned failure reasons:

- ledger_entry_count_mismatch
- ledger_dependency_edge_count_mismatch
- ledger_event_type_counts_mismatch
- ledger_root_final_count_mismatch
- ledger_derived_counter_mismatch
- ledger_stored_validation_status_mismatch

## Fail-Closed Matrix

The planned validator must reject:

- duplicate ledger_index
- non-contiguous ledger indexes
- negative ledger index
- duplicate artifact_id
- empty artifact_id
- unknown event type
- wrong event order
- multiple transaction_started entries
- transaction_started not at index 0
- mixed transaction_id
- missing required event
- missing dependency
- dependency on a later entry
- self-dependency
- cyclic dependency
- wrong Root owner
- wrong created_by
- unknown authority class
- unknown evidence class
- provider-created contract/action artifact
- ledger-created authority
- ledger-created permission
- ledger-created action
- receipt classified as permission
- receipt classified as authority
- receipt classified as Root final
- shared summary classified as a fourth Root
- raw provider response classified as canonical authority
- secret-bearing canonical_hash_input
- raw provider text in canonical_hash_input
- malformed canonical_hash_input
- malformed timestamp
- hidden current-time fallback
- missing side-specific Root final
- ledger entry claiming FinalOutput creation
- nonzero provider/network/Gemini call count
- nonzero real airline/bank/GDS call count
- nonzero real payment/ticket/booking/effect count

The validator must never repair the ledger. It must never invent an artifact,
change a Root owner, reorder entries silently, add a missing dependency,
convert receipt evidence into permission, or convert provider output into a
Root decision.

## Single-Transaction And State Isolation

v0.1 contains one transaction per ledger.

Rules:

- no multi-transaction aggregation
- no global mutable registry
- no module-global active transaction
- no module-global current offer/hold/amount
- no cross-run state

Planned tests must prove:

- A ledger can be built
- B ledger can be built
- A can be validated after B
- B can be validated after A
- A/B/A and B/A/B do not contaminate one another
- all state is passed explicitly
- no source artifact is mutated by ledger collection

## Implementation Program

### Slice A

This dedicated preflight only.

### Slice B

Recommended files:

- `hedgehog/domains/airline/transaction_artifact_ledger_v01.py`
- `tests/test_airline_transaction_artifact_ledger_v01.py`

Scope:

- frozen local contracts
- constants and allowlists
- deterministic fixture ledger
- pure entry validators
- pure whole-ledger validator
- dependency validation
- Root ownership validation
- evidence/authority classification
- canonical_hash_input safety checks
- Offer A and Offer B fixture paths
- no runner integration
- no artifact writing
- no provider/network/Gemini
- no Crypto
- no Replay

### Slice C

- pure collector from existing validated semantic causal report and existing
  deterministic corridor report
- no semantic rerun
- no corridor rerun
- one source transaction
- one ledger
- source artifacts are not mutated

### Slice D

- integrate the collector into the existing Airline deterministic/live
  transaction path
- no new demo
- no second transaction
- no second corridor execution
- write exactly one `airline_transaction_artifact_ledger.json`

### Slice E

- ledger audit
- artifact-backed human ledger timeline
- no provider/network/Gemini
- no Crypto
- no Replay

Only after Slice E PASS and audit PASS may the next gate open:

- Airline Crypto Artifact Seal v0.1 preflight / implementation

Do not implement any slice in this task.

## Required Slice B Test Plan

Future tests must include at least:

1. valid Offer A ledger passes
2. valid Offer B ledger passes
3. transaction_started is unique and index zero
4. ledger indexes are contiguous
5. duplicate index fails
6. duplicate artifact id fails
7. mixed transaction id fails
8. missing dependency fails
9. later-entry dependency fails
10. self-dependency fails
11. cyclic dependency fails
12. wrong ClientRoot owner fails
13. wrong AirlineRoot owner fails
14. wrong BankRoot owner fails
15. cross-root reviewer as fourth Root fails
16. provider-created offer fails
17. provider-created hold fails
18. provider-created purchase intent fails
19. provider-created payment authorization fails
20. provider-created ticket intent fails
21. receipt classified as permission fails
22. receipt classified as authority fails
23. root final owned by wrong Root fails
24. missing ClientRoot final fails
25. missing AirlineRoot final fails
26. missing BankRoot final fails
27. raw provider text in canonical_hash_input fails
28. raw passport in canonical_hash_input fails
29. card/IBAN/payment token in canonical_hash_input fails
30. malformed canonical_hash_input fails
31. unknown event type fails
32. unknown authority class fails
33. unknown evidence class fails
34. nonzero ledger-created authority fails
35. nonzero ledger-created permission fails
36. nonzero ledger-created action fails
37. nonzero real effect fails
38. ledger collection does not mutate source artifacts
39. A/B/A isolation passes
40. B/A/B isolation passes
41. raw prompt/response remain auxiliary refs only
42. canonical semantic entry is built from validated canonical evidence, not
    raw provider response
43. human approval remains evidence and does not directly become ticket or
    payment permission
44. Ledger module imports no provider/network/Gemini/config/demo runner
45. Ledger module is explicitly an Airline domain projection, not universal
    core and not an installed Needle
46. lied entry_count fails
47. lied dependency_edge_count fails
48. lied event_type_counts fails
49. lied root_final_count fails
50. two Root finals with stored root_final_count three fails
51. ledger-created authority in an entry with stored count zero fails
52. nonzero effects in an entry with stored total zero fails
53. stored PASS status cannot override an invalid dependency graph
54. ambiguous artifact classification is impossible
55. every mapped current artifact has exactly one classification
56. approval evidence is not assigned a fabricated creator
57. offer hold receipt is independently present before purchase intent

## Crypto And Replay Remain Blocked

Record:

- no SHA-256 ledger manifest
- no ordered artifact hashes
- no chain head/tail
- no signature placeholder
- no signature verification
- no key management
- no PKI
- no legal non repudiation claim
- no replay runner
- no Gemini-free replay claim yet
- no tamper-proof claim

The Ledger preflight defines what may later be sealed. It does not seal
anything. Crypto Artifact Seal remains blocked. Sealed Trace Replay remains
blocked.

## Non-Claims

This preflight explicitly claims:

- no production ledger
- no database
- no blockchain
- no distributed consensus
- no cryptographic seal
- no production signature
- no key management
- no PKI
- no legal non repudiation
- no replay verifier
- no real airline API
- no real bank API
- no real GDS API
- no real payment
- no real ticket
- no real booking
- no real-world effects
- not production
- not public-auditor package
- no universal Ledger core
- no new authority engine
- no installed Needle

## Definition Of Done

This preflight is complete only because it records:

- the closed source basis
- why the Ledger gate is now open
- the exact core/domain boundary
- planned local contracts
- artifact-to-ledger mapping
- canonical vs validation vs auxiliary classification
- event taxonomy
- actual causal ordering
- dependency rules
- Root ownership matrix
- authority/evidence allowlists
- canonical_hash_input boundary
- raw/secret exclusions
- fail-closed matrix
- A/B state isolation
- Slice B/C/D/E program
- Crypto and Replay gates
- non-claims
- runtime/tests unchanged

Final status:

- preflight_status: READY_FOR_REVIEW
- next_implementation_gate: Airline Transaction Artifact Ledger v0.1 Slice B local contracts and validators only
