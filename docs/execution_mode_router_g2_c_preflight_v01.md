# Hedgehog OS / Fractal Reflexive OS
## Gate 2 / G2-C - ExecutionModeRouter Architect Preflight v0.1.6

```text
document_status: PREFLIGHT
document_revision: v0.1.6
guardian_review_status: ACCEPTED
repository_basis_branch: main
repository_basis_head: 3cd5c4db2fc6e9e3b04a309decc5682ed6f4ea21
repository_basis_origin_main: 3cd5c4db2fc6e9e3b04a309decc5682ed6f4ea21
gate_id: gate2_g2c_execution_mode_router
gate_slice: G2-C
planning_only: true
implementation_authorized: false
implementation_started: false
r_h1_status: CLOSED_PASS
g2a_status: CLOSED_PASS
g2b_status: CLOSED_PASS
gate2_closed: false
g2c_preflight_accepted: true
public_release_claimed: false
rc2_claimed: false
production_readiness_claimed: false
production_security_certification_claimed: false
```

## 1. Purpose, Authority, and Scope

This accepted document freezes the exact planning contract for G2-C. Acceptance
applies only to this planning artifact. It does not authorize G2-C1, implement
a runtime, modify a schema, close Gate 2, or make a release claim. No accepted
field in this document self-authorizes a code change.

The binding control architecture is:

```text
BSEP
-> semantic proposal
-> runtime-owned RuntimeExecutionTopology
-> Root
```

`ExecutionModeRouter` is a deterministic bounded Kernel function inside this
Root-controlled route. It proposes a safe execution mode from validated local
facts. It is not a sovereign actor and creates no truth, authority, permission,
packet, topology, receipt, write, final output, provider call, or effect.

G2-A and G2-B remain `CLOSED_PASS` and read-only. G2-C does not implement G2-D,
G2-E, or G2-F. R-IP1 does not block G2-C through G2-F. No public publication is
allowed before Gate 6 closure and separate explicit owner approval.

## 2. Source-of-Truth and Conflict Resolution

The exact hierarchy is:

1. Current explicit owner instruction.
2. DeepTech Completion Roadmap v3.1 for Gate order and high-level architecture.
3. Master Roadmap v2.1 only as a non-binding mathematical or implementation
   donor when it does not conflict with a higher source.
4. The active current-checkpoint block in `AGENTS.md`.
5. Accepted R-H1, G2-A, and G2-B checkpoints and audits.
6. Human Passport, invariants, and Machine Manifest.
7. Current committed Kernel/runtime contracts and tests.
8. The completed read-only G2-C inventory and contradiction register.
9. Historical proof and documentation surfaces as evidence only.

### 2.1 Material conflict register

| Conflict | Higher source | Lower source | Exact disposition |
|---|---|---|---|
| Current owner route versus older execution vectors | Owner instruction | historical proof text | The owner route in Section 1 controls; inactive surfaces create no implementation obligation. |
| Canonical G2-C router versus current proof router | Owner instruction and accepted inventory | `hedgehog/mode_router.py` | The current proof router remains unchanged and is not imported by G2-C. |
| Root review before topology versus the current SemanticWork topology-reference field | Owner route | `SemanticWorkRequestV01.runtime_topology_ref` | The G2-C Root profile uses exact sentinel `g2c:runtime_topology:not_created_before_root_review:v01`; profile validation proves that no topology object or topology identity was created. |
| Independent request identity versus Kernel transaction identity | Owner correction | earlier draft | `request_id` and `transaction_id` are separate and cross-bound; neither is derived from the other. |
| A string time reference versus KernelArtifact time envelope | Current Kernel ABI | earlier draft | The local snapshot freezes all eight source scalars and reconstructs the exact existing envelope. |
| One Kernel ABI versus a separate G2-C envelope | Owner correction | earlier draft | Three artifact literals and contextual projections append to the existing `KernelArtifactV01` family. |
| One Transition Registry versus a private transition machine | Owner correction | earlier draft | A separate validated G2-C profile uses the existing `TransitionRegistryV01` dataclass while the default 18-rule registry remains exact. |
| One Root Decision law versus an independent review engine | Owner correction | earlier draft | Every G2-C route decision projects an actual validated `RootDecisionResultV01`. |
| Copied source status versus actual source validation | Owner correction | earlier draft | Actual source objects and public source validators are mandatory. |
| Fresh action reasoning versus existing-packet eligibility | G2-A boundary and owner correction | earlier draft | New action reasoning may route without a packet; only continuation of an existing packet requires present eligibility. |
| Context-only memory versus direct reuse | Accepted G2-B contract | earlier draft | Three exact binding states distinguish absence, advisory context, and the complete direct shortcut family. |
| Full semantic depth versus full fractal depth | Owner instruction | incomplete proof vocabulary | They remain distinct; actual fractal expansion belongs to G2-D. |
| Raw request to typed G2-B query | Accepted G2-B boundary | current Root intake | The cross-binding remains absent; G2-C consumes already validated typed objects. |

No lower source silently overrides a higher source.

## 3. Repository Basis and Accepted Inventory

The repository basis is synchronized branch `main` at
`3cd5c4db2fc6e9e3b04a309decc5682ed6f4ea21`.

Accepted basis:

- R-H1 is `CLOSED_PASS`.
- R-H1 checkpoint is
  `docs/clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md`.
- Its SHA-256 is
  `58e26aac7a44e18775de7b6d5baf5c12665c3b5c746e4cc0784ec060a97ecd8a`.
- G2-A is `CLOSED_PASS`.
- G2-B is `CLOSED_PASS`.
- Gate 2 is `NOT_CLOSED`.
- G2-C implementation is `NOT_STARTED` and `NOT_AUTHORIZED`.

The accepted inventory and this correction review establish:

- no canonical general `ExecutionModeRouter` exists;
- the proof router has one active `RootOrchestrator` caller and direct tests;
- proposal mode, effective Root mode, and trace mode are distinct and untyped;
- actual business-request, BSEP, rationale, Replay, G2-A, G2-B, ABI,
  Transition Registry, SemanticWork, trust, and Root validators exist;
- no generic `RuntimeExecutionTopology` builder or validator exists;
- raw-user-request to canonical G2-B typed-query binding is absent;
- Root remains sole final authority;
- no file changed during the accepted inventory.

## 4. Architecture Lock

The exact route is:

1. A locally validated BSEP and its actual source family provide bounded
   meaning.
2. The router validates source-bound input and deterministically evaluates ten
   mode rows.
3. The router emits a non-authoritative semantic routing proposal.
4. Root reviews the proposal through the existing Root Decision law.
5. A contextually validated Root `ACCEPT` or scope-only `NARROW` may produce a
   route-eligibility ABI artifact.
6. Only route eligibility whose downstream class is
   `RUNTIME_TOPOLOGY_ELIGIBLE` may later be consumed by a G2-D topology builder.
7. G2-C never constructs topology, child cells, actors, nodes, edges,
   assignments, permissions, packets, effects, receipts, DRS writes, or final
   output.
8. Root retains final authority after later execution and validation.

No provider, model, DRS result, ReuseCertificate, AVF result, GT result, BSEP,
router result, or topology creates authority or effect permission.

## 5. Canonical Mode Vocabulary

The exact ordered vocabulary is:

1. `deterministic`
2. `sealed_replay`
3. `direct_informational_reuse`
4. `memory_informed`
5. `local_slm`
6. `cloud_llm`
7. `full_semantic`
8. `full_fractal`
9. `blocked`
10. `needs_user`

Spelling is exact lowercase snake_case. Aliases, numbered labels, proof-router
labels, SemanticWork contribution labels, and unknown values fail closed. No
runtime mapping or compatibility adapter exists.

`full_semantic` is complete non-fractal semantic depth. `full_fractal` means
bounded fractal capability is required. G2-C may propose `full_fractal`, but
G2-D owns actual expansion. Missing declared fractal capability is explicit and
cannot silently fall back to `full_semantic`.

The `direct_protocol` declaration is `OUT_OF_SCOPE_FOR_G2C_V01` and is not a
canonical mode.

## 6. Routing Position and Shortcut Law

Every nonterminal mode requires a valid BSEP source family and Root review.
`deterministic`, `sealed_replay`, and `direct_informational_reuse` may terminate
without provider work or topology when their exact evidence contracts pass,
but they still return through Root. `memory_informed`, `local_slm`, `cloud_llm`,
`full_semantic`, and `full_fractal` recommend later compute depth only.

No shortcut bypasses Root or applicable policy, scope, freshness, G2-A, G2-B,
permission, firewall, corridor, Post V&V, GT, or conflict boundaries. A mode
recommendation never performs downstream work.

### 6.1 Global scalar, text, sequence, and reason law

All canonical strings are UTF-8 and Unicode NFC. Validators reject surrogates,
NUL, C0/C1 control characters, non-NFC text, and empty strings where the field
is required. Exact bounds are:

- project-defined G2-C identity/ref text: 1..256 Unicode scalar values and
  pattern `^[A-Za-z][A-Za-z0-9_.:/-]{0,255}$`; every project-defined identity
  also has the exact prefix frozen in Section 7.1;
- machine code: 1..64 ASCII characters and pattern
  `^[A-Z][A-Z0-9_]{0,63}$`;
- public G2-C reason code: at most 128 ASCII characters and exact pattern
  `^g2c_[a-z0-9_]{1,124}$`;
- SHA-256: exactly 64 lowercase hexadecimal characters;
- general bounded text: 1..512 Unicode scalar values;
- tuples: exact tuple type, no tuple subclass, maximum 64 members unless an
  exact smaller cardinality is frozen;
- trace/reference tuples: unique, supplied in canonical lexical order;
- reason tuples: unique and ordered by the public registry, not caller order;
- mode profiles: exactly eight in executable-mode order;
- feasibility rows: exactly ten in canonical mode order.

Semantically ordered tuples are not implicitly sorted. A noncanonical supplied
order is rejected. Canonical set-like tuples are constructed in lexical order
and validators reject duplicate or reordered input.

Integers require exact `int`, reject `bool` and subclasses, and use signed
64-bit bounds. Costs are in `0..9223372036854775807`. The twelve serialized
G2-C types and all G2-C-owned typed identity material forbid `float`,
`Decimal`, NaN, infinity, mutable nested mappings, wall-clock reads,
randomness, locale lookup, and object representation. All G2-C costs and times
are exact integers.

This strict G2-C scalar law does not rewrite source canonicalization. The
existing `canonical_json_bytes_v01` accepts finite JSON floats, rejects
non-finite floats, unsupported value types, cycles, and lone Unicode
surrogates, and emits deterministic UTF-8 JSON. A materialized Python `dict`
cannot contain duplicate keys. Source validators remain authoritative for
their own source shapes. A finite BSEP donor value such as `confidence: 0.66`
is accepted only when the complete current source validator accepts it; it
participates in the source object's current canonical bytes and digest but is
never copied into a G2-C typed scalar field. NaN and positive or negative
infinity fail closed.

Identity classes remain distinct. Project-defined G2-C prefixed identities
use the G2-C pattern and exact prefix. Source-native identities, including
`TransitionRegistryV01.registry_id`, `TransitionDecisionV01.decision_id`,
`RootDecisionKernelV01.kernel_id`, source Root decision IDs, and source query
IDs, use their exact source validators and source identity laws. A valid
source-native lowercase 64-hex identity may begin with a decimal digit and is
not forced through the G2-C alphabetic-prefix pattern. Every SHA-256 field is
exactly 64 lowercase hex. Source-owned reason codes remain source-governed,
need not have a `g2c_` prefix, and are not silently inserted into the public
G2-C reason registry.

### 6.2 Request, transaction, Root, domain, and time law

`request_id`, `transaction_id`, `owning_root_id`, and `domain_id` are independent
required identities. Request and transaction must not equal merely by builder
assignment; exact equality is rejected and tests prove independent values.
Every consequential identity,
binding, local profile, proposal, review, decision, ABI artifact, and source
projection cross-binds all four values. Kernel ABI and Root Decision inputs use
the exact `transaction_id`.

The business-request source is an exact plain `dict` returned by
`build_business_request_context_packet`. Its subclass is rejected. Validation
requires `validate_business_request_context_packet(packet)["accepted"] is True`,
empty source reasons, exact `request_id`, and `packet["domain"] == domain_id`.

The G2-C business source reference has this exact plain shape and key order:

```text
source: G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01
packet_id: <business request packet_id>
request_id: <request_id>
domain_id: <domain_id>
```

It occurs exactly once in both the route-context `source_refs` and BSEP
`source_refs`. A foreign request/domain packet fails closed. BSEP has no native
transaction field; transaction and Root are explicit local cross-bindings and
are never described as source-native evidence.

The local snapshot contains:

```text
evaluation_time_epoch_seconds
pt_created_at_utc
kt_asof_utc
et_observed_at_utc
ct_session_anchor
ttl_seconds
freshness_class
valid_from_utc
valid_to_utc
time_envelope_ref
```

Timestamp grammar is exactly `YYYY-MM-DDTHH:MM:SS+00:00`, with no fraction and
no alternative offset. Epoch values are in
`-62135596800..253402300799`; conversion uses UTC and
`kt_asof_utc` is exactly the canonical conversion of
`evaluation_time_epoch_seconds`. `pt_created_at_utc <= kt_asof_utc`,
`et_observed_at_utc <= kt_asof_utc`, and
`valid_from_utc <= kt_asof_utc < valid_to_utc`. `ttl_seconds` equals the exact
integer difference between valid-to and valid-from. Freshness is one of
`static`, `slow_changing`, `normal`, `fast_changing`, or `real_time`.

There is exactly one time-envelope-reference law. Its domain is
`HEDGEHOG_EXECUTION_MODE_TIME_ENVELOPE_REF_V01` and its prefix is
`emtime_v01:`. Identity material is exactly the current eight-field Kernel
time-envelope plain data in this order:

```text
ct_session_anchor
et_observed_at
freshness_class
kt_asof
pt_created_at
ttl_seconds
valid_from
valid_to
```

The identity is `emtime_v01:` plus
`domain_separated_sha256_hex_v01(domain="HEDGEHOG_EXECUTION_MODE_TIME_ENVELOPE_REF_V01", payload=canonical_json_bytes_v01(exact_eight_field_plain_data))`.
`evaluation_time_epoch_seconds` validates and derives `kt_asof`; it is not a
ninth identity-material field. Every Kernel artifact reconstructs the same
eight-field envelope and checks this same reference identity.

G2-A evaluation time and G2-B query/use time equal the explicit epoch value.
No wall clock, timezone database, or locale is consulted.

## 7. Canonical Types and Identity

The canonical module is `hedgehog/kernel/execution_mode_router_v01.py`.

```text
TOTAL_G2C_TYPE_COUNT=13
SERIALIZED_IDENTITY_TYPE_COUNT=12
RUNTIME_ONLY_SOURCE_CONTEXT_TYPE_COUNT=1
LOCAL_MODE_PROFILE_COUNT=8
```

All thirteen are frozen dataclasses. Exact-type checks reject subclasses. The
schema `schemas/execution_mode_router_v01.schema.json` covers exactly the first
twelve plain-data forms. The runtime source context is not serialized, has no
identity, is not an artifact, and is never provider supplied.

### 7.1 Type and identity registry

| # | Type | Serialized | Identity field | Domain tag | Prefix |
|---:|---|---:|---|---|---|
| 1 | `ExecutionModeBSEPBindingV01` | true | `bsep_binding_id` | `HEDGEHOG_EXECUTION_MODE_BSEP_BINDING_V01` | `embsep_v01:` |
| 2 | `ExecutionModeReplayBindingV01` | true | `replay_binding_id` | `HEDGEHOG_EXECUTION_MODE_REPLAY_BINDING_V01` | `emreplay_v01:` |
| 3 | `ExecutionModeG2ABindingV01` | true | `g2a_binding_id` | `HEDGEHOG_EXECUTION_MODE_G2A_BINDING_V01` | `emg2a_v01:` |
| 4 | `ExecutionModeG2BBindingV01` | true | `g2b_binding_id` | `HEDGEHOG_EXECUTION_MODE_G2B_BINDING_V01` | `emg2b_v01:` |
| 5 | `ExecutionModeLocalModeProfileV01` | true | `local_mode_profile_id` | `HEDGEHOG_EXECUTION_MODE_LOCAL_MODE_PROFILE_V01` | `emprofile_v01:` |
| 6 | `ExecutionModeLocalRoutingSnapshotV01` | true | `local_routing_snapshot_id` | `HEDGEHOG_EXECUTION_MODE_LOCAL_ROUTING_SNAPSHOT_V01` | `emlocal_v01:` |
| 7 | `ExecutionModeRouterInputV01` | true | `router_input_id` | `HEDGEHOG_EXECUTION_MODE_ROUTER_INPUT_V01` | `eminput_v01:` |
| 8 | `ExecutionModeFeasibilityRowV01` | true | `feasibility_row_id` | `HEDGEHOG_EXECUTION_MODE_FEASIBILITY_ROW_V01` | `emrow_v01:` |
| 9 | `ExecutionModeProposalV01` | true | `proposal_id` | `HEDGEHOG_EXECUTION_MODE_PROPOSAL_V01` | `emproposal_v01:` |
| 10 | `RootExecutionModeReviewInputV01` | true | `root_review_input_id` | `HEDGEHOG_ROOT_EXECUTION_MODE_REVIEW_INPUT_V01` | `emreview_v01:` |
| 11 | `RootExecutionModeDecisionV01` | true | `decision_id` | `HEDGEHOG_ROOT_EXECUTION_MODE_DECISION_V01` | `emdecision_v01:` |
| 12 | `ExecutionModeValidationReportV01` | true | `validation_report_id` | `HEDGEHOG_EXECUTION_MODE_VALIDATION_REPORT_V01` | `emvalidation_v01:` |
| 13 | `ExecutionModeSourceContextV01` | false | none | none | none |

For each serialized type, canonical plain data follows field order, omits only
the identity field, freezes nested values, encodes with
`canonical_json_bytes_v01`, hashes with `domain_separated_sha256_hex_v01`, and
adds the exact prefix. Every consequential field participates. Rebuilders must
reproduce the identity byte-for-byte.

#### 7.1.1 Global non-identity SHA-256 law

Every G2-C-generated field ending in `_sha256` is exactly
`hashlib.sha256(canonical_json_bytes_v01(exact_frozen_plain_material)).hexdigest()`
unless this section explicitly identifies it as a copied and revalidated
source-native hash. A G2-C `*_id` uses its exact domain-separated identity law;
an ID and a plain digest are never interchanged.

The business-request/BSEP family uses plain SHA-256 over the exact normalized
current source plain data accepted by each current source validator:

| Field | Exact material |
|---|---|
| `business_request_packet_sha256` | complete accepted business-request packet plain `dict` |
| `source_route_context_sha256` | complete accepted route-context packet plain `dict` |
| `source_proposal_sha256` | complete accepted orchestrator proposal plain `dict` |
| `source_structured_rationale_sha256` | complete accepted structured-rationale plain `dict` |
| `source_packet_sha256` | complete accepted BSEP packet plain `dict` |

`source_family_sha256` is the plain SHA-256 of this exact named canonical
object, constructed in the listed key order:

```text
business_request_packet_sha256: <business_request_packet_sha256>
source_route_context_sha256: <source_route_context_sha256>
source_proposal_sha256: <source_proposal_sha256>
source_structured_rationale_sha256: <source_structured_rationale_sha256>
source_packet_sha256: <source_packet_sha256>
```

Each key's value is the corresponding constituent digest. The five complete
source dictionaries are transitively bound by those constituent digests; no
second family framing or alternate key vocabulary is valid.

`source_replay_sha256` is the plain SHA-256 of the complete accepted output of
`sealed_replay_evidence_to_plain_dict_v01` after the actual replay family has
validated.

For G2-A, `source_inspection_sha256` is the plain SHA-256 of one exact
inspection projection in `ActionPacketPresentEligibilityInspectionV01` field
order: `inspection_profile_id`, `registry_id`, `packet_id`, `evaluation_time`,
`evaluation_time_source`, `evaluation_context_id`, `historical_state`,
`present_eligibility_status`, `present_executable`, `retry_eligible`,
`reason_codes`, `transition_history_sha256`, `disposition_history_sha256`,
`historical_result_unchanged`, `creates_authority`, `creates_permission`,
`creates_packet`, `creates_receipt`, `adapter_calls`, and
`real_world_effects_count`. `historical_state` is a named plain object in exact
`ActionPacketLifecycleStateV01` field order. The binding's
`transition_history_sha256` and `disposition_history_sha256` are copied
verbatim from the validated inspection and checked against the current replay
projection. They retain the source-native history-hash law and are not
relabelled as G2-C-generated digests.

For G2-B, `report_sha256` is the plain SHA-256 of
`drs_resolution_report_to_plain_data_v01(report)`. The
`compatibility_projection_set_sha256` material is the exact ordered tuple of
validated `legacy_drs_projection_to_plain_data_v01` projections.
`source_root_decision_sha256` is the plain SHA-256 of
`root_decision_result_to_plain_dict_v01(actual_source_root_result)`. Each is
computed only after its complete source family validates.

`mode_profile_set_sha256` is the plain SHA-256 of the exact ordered eight
serialized `ExecutionModeLocalModeProfileV01` plain projections. The proposal
field `source_bsep_sha256` is copied exactly from the validated
`bsep_binding.source_packet_sha256`. Any G2-B query scope fingerprint is the
plain SHA-256 of the exact UTF-8 bytes of the canonical scope reference, as
required by the current source query builder. No source-native hash is
relabelled as a G2-C-generated hash.

### 7.2 Exact field tables

#### 7.2.1 ExecutionModeBSEPBindingV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `bsep_binding_id` | `str`, canonical identity |
| 2 | `binding_state` | literal `BOUNDED_SEMANTIC_EVIDENCE_BOUND` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `business_request_packet_id` | exact source packet ID |
| 8 | `business_request_packet_sha256` | lowercase SHA-256 |
| 9 | `source_packet_id` | exact BSEP packet ID |
| 10 | `source_packet_sha256` | lowercase SHA-256 |
| 11 | `source_packet_type` | `BoundedSemanticEvidencePacket` |
| 12 | `source_schema_version` | `bounded_semantic_evidence_packet_v0.1` |
| 13 | `source_route_context_packet_id` | exact route packet ID |
| 14 | `source_route_context_sha256` | lowercase SHA-256 |
| 15 | `source_route_id` | exact BSEP route ID |
| 16 | `source_proposal_id` | exact proposal ID |
| 17 | `source_proposal_sha256` | lowercase SHA-256 |
| 18 | `source_structured_rationale_ref` | exact BSEP rationale ref |
| 19 | `source_structured_rationale_sha256` | lowercase SHA-256 |
| 20 | `source_family_sha256` | digest of ordered five-source family |
| 21 | `source_domain` | exact BSEP domain, equals `domain_id` |
| 22 | `source_role` | exact source value `orchestrator` |
| 23 | `target_role` | exact source value `architect` |
| 24 | `source_reason_codes` | empty `tuple[str, ...]` after all source validators pass |
| 25 | `root_final_authority_preserved` | exact true |
| 26 | `authority_created` | exact false |
| 27 | `permission_created` | exact false |
| 28 | `action_commit_packet_created` | exact false |
| 29 | `final_output_created` | exact false |
| 30 | `real_world_effects_count` | exact zero |

The family digest follows the single named constituent-digest law in Section
7.1.1. The BSEP validator receives the freshly derived structured-rationale
validation result. No copied acceptance field is serialized.

#### 7.2.2 ExecutionModeReplayBindingV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `replay_binding_id` | canonical `str` |
| 2 | `binding_state` | `NOT_APPLICABLE` or `SEALED_REPLAY_BOUND` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `replay_id` | `str | None` |
| 8 | `source_replay_sha256` | lowercase SHA-256 or `None` |
| 9 | `replay_status` | `NOT_APPLICABLE` or exact source `PASS` |
| 10 | `source_manifest_id` | `str | None` |
| 11 | `reconstructed_manifest_id` | `str | None` |
| 12 | `anchor_publication_id` | `str | None` |
| 13 | `anchored_verification_id` | `str | None` |
| 14 | `source_domain_projection_id` | `str | None` |
| 15 | `reconstructed_domain_projection_id` | `str | None` |
| 16 | `package_id` | `str | None` |
| 17 | `logical_package_ref` | `str | None` |
| 18 | `source_package_content_hash` | lowercase SHA-256 or `None` |
| 19 | `reconstructed_package_content_hash` | lowercase SHA-256 or `None` |
| 20 | `integrity_verified` | exact `bool` |
| 21 | `continuity_verified` | exact `bool` |
| 22 | `anchor_verified` | exact `bool` |
| 23 | `evidence_refs` | `tuple[str, ...]` |
| 24 | `authority_created` | exact false |
| 25 | `permission_created` | exact false |
| 26 | `action_commit_packet_created` | exact false |
| 27 | `receipt_created` | exact false |
| 28 | `final_output_created` | exact false |
| 29 | `real_world_effects_count` | exact zero |

Absent state requires fields 7..19 `None`, booleans false, and empty refs.
Bound state requires exact validated source identities and all three validation
booleans true.

#### 7.2.3 ExecutionModeG2ABindingV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `g2a_binding_id` | canonical `str` |
| 2 | `binding_state` | `NO_PACKET` or `PRESENT_INSPECTION_BOUND` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `source_inspection_sha256` | lowercase SHA-256 or `None` |
| 8 | `inspection_profile_id` | `str | None` |
| 9 | `registry_id` | `str | None` |
| 10 | `packet_id` | `str | None` |
| 11 | `evaluation_time` | exact signed-int64 |
| 12 | `evaluation_time_source` | exact `str` |
| 13 | `evaluation_context_id` | exact `str` |
| 14 | `historical_lifecycle_state` | source lifecycle literal or `NO_PACKET` |
| 15 | `failed_provenance` | `str | None` |
| 16 | `transition_event_count` | nonnegative exact `int` |
| 17 | `execution_attempt_count` | nonnegative exact `int` |
| 18 | `idempotency_disposition` | source literal or `NOT_APPLICABLE` |
| 19 | `reservation_owner_packet_id` | `str | None` |
| 20 | `terminal_receipt_ref` | `str | None` |
| 21 | `lifecycle_terminal` | exact `bool` |
| 22 | `eligible_for_corridor_revalidation` | exact `bool` |
| 23 | `present_eligibility_status` | source literal or `NOT_APPLICABLE` |
| 24 | `present_executable` | exact `bool` |
| 25 | `retry_eligible` | exact `bool` |
| 26 | `source_reason_codes` | ordered source tuple |
| 27 | `transition_history_sha256` | lowercase SHA-256 or `None` |
| 28 | `disposition_history_sha256` | lowercase SHA-256 or `None` |
| 29 | `historical_result_unchanged` | exact `bool` |
| 30 | `authority_created` | exact false |
| 31 | `permission_created` | exact false |
| 32 | `packet_created` | exact false |
| 33 | `receipt_created` | exact false |
| 34 | `adapter_calls` | exact zero |
| 35 | `real_world_effects_count` | exact zero |

For `NO_PACKET`, the exact values are:

```text
source_inspection_sha256=None
inspection_profile_id=None
registry_id=None
packet_id=None
evaluation_time=local_routing_snapshot.evaluation_time_epoch_seconds
evaluation_time_source=local_routing_snapshot.created_by
evaluation_context_id=local_routing_snapshot.local_routing_snapshot_id
historical_lifecycle_state=NO_PACKET
failed_provenance=None
transition_event_count=0
execution_attempt_count=0
idempotency_disposition=NOT_APPLICABLE
reservation_owner_packet_id=None
terminal_receipt_ref=None
lifecycle_terminal=false
eligible_for_corridor_revalidation=false
present_eligibility_status=NOT_APPLICABLE
present_executable=false
retry_eligible=false
source_reason_codes=()
transition_history_sha256=None
disposition_history_sha256=None
historical_result_unchanged=true
authority_created=false
permission_created=false
packet_created=false
receipt_created=false
adapter_calls=0
real_world_effects_count=0
```

`PRESENT_INSPECTION_BOUND` is derived from the actual complete inspection and
source context. Its evaluation time, source, and context ID equal the same
local snapshot epoch, creator, and snapshot ID. The source inspection has no
native identity, so G2-C never claims one. Any copied lifecycle or eligibility
literal, or mixed `NO_PACKET`/present geometry, fails closed with
`g2c_g2a_relation_invalid`.

#### 7.2.4 ExecutionModeG2BBindingV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `g2b_binding_id` | canonical `str` |
| 2 | `binding_state` | `NOT_APPLICABLE`, `RESOLUTION_CONTEXT_BOUND`, or `DIRECT_REUSE_BOUND` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `report_id` | `str | None` |
| 8 | `report_sha256` | lowercase SHA-256 or `None` |
| 9 | `semantic_address_id` | `str | None` |
| 10 | `query_id` | `str | None`; equals transaction for bound states |
| 11 | `query_evaluation_ids` | `tuple[str, ...]` |
| 12 | `eligible_candidate_ids` | `tuple[str, ...]` |
| 13 | `ranked_candidate_ids` | `tuple[str, ...]` |
| 14 | `selected_candidate_id` | `str | None` |
| 15 | `retrieval_plan_id` | `str | None` |
| 16 | `memory_descent_result_id` | `str | None` |
| 17 | `root_shortcut_projection_id` | `str | None` |
| 18 | `reuse_certificate_id` | `str | None` |
| 19 | `compatibility_projection_ids` | exact source projection IDs |
| 20 | `compatibility_projection_set_sha256` | lowercase SHA-256 or `None` |
| 21 | `use_time` | signed-int64 or `None` |
| 22 | `source_root_kernel_id` | `str | None` |
| 23 | `source_root_decision_input_id` | `str | None` |
| 24 | `source_root_decision_id` | `str | None` |
| 25 | `source_root_decision_sha256` | lowercase SHA-256 or `None` |
| 26 | `freshness_state` | `NOT_APPLICABLE`, `CURRENT`, or `STALE` |
| 27 | `lineage_state` | `NOT_APPLICABLE` or `VALIDATED` |
| 28 | `quarantine_present` | exact `bool` |
| 29 | `deadend_present` | exact `bool` |
| 30 | `context_available` | exact derived `bool` |
| 31 | `direct_informational_reuse_eligible` | exact derived `bool` |
| 32 | `source_reason_codes` | ordered source tuple |
| 33 | `persistent_records_unchanged` | exact `bool` |
| 34 | `authority_created` | exact false |
| 35 | `permission_created` | exact false |
| 36 | `action_commit_packet_created` | exact false |
| 37 | `receipt_created` | exact false |
| 38 | `capability_created` | exact false |
| 39 | `topology_created` | exact false |
| 40 | `final_output_created` | exact false |
| 41 | `drs_write_created` | exact false |
| 42 | `real_world_effects_count` | exact zero |

The exact three-state geometry is:

- `NOT_APPLICABLE`: every source ID and source SHA is `None`; all source ID
  tuples are empty; selection, retrieval, memory descent, shortcut,
  certificate, use time, and Root fields are `None`; freshness and lineage are
  `NOT_APPLICABLE`; quarantine, deadend, context availability, and direct
  eligibility are false; source reasons are empty; persistent records are
  unchanged; every creation flag is false; effects are zero.
- `RESOLUTION_CONTEXT_BOUND`: the complete report validates with
  `query_mode=MEMORY_CONTEXT_ONLY`, `reuse_intent=CONTEXT`, and requested reuse
  classes exactly `(CONTEXT_ONLY,)`; compatibility equals
  `report.source_projections`; use time equals the query evaluation time and
  local snapshot epoch; the Root triple, shortcut, certificate, eligible
  candidates, ranked IDs, and selected candidate are absent; context-only
  record IDs are nonempty; context is available; direct eligibility is false;
  freshness is `STALE`; lineage is `VALIDATED`; quarantine/deadend reflect the
  actual query-evaluation states; reasons are empty; no state or effect changes.
- `DIRECT_REUSE_BOUND`: the complete direct report, selected eligible ranked
  candidate, shortcut, certificate, compatibility tuple, use-time validation,
  and Root Kernel/Input/Result triple all validate; freshness is `CURRENT`;
  lineage is `VALIDATED`; quarantine and deadend are false; context and direct
  eligibility are true; reasons are empty; no state or effect changes.

A shortcut or certificate without the complete valid Root triple is partial
direct geometry and fails closed; it is not reclassified as context-only.
Invalid source produces no binding. The state is derived, never caller
selected. Partial Root triples, wrong query transactions, and substituted
source objects fail closed.

The binding state is derived, never caller selected. Bound states require:

```text
router_input.transaction_id
== router_input.g2b_binding.transaction_id
== resolution_report.query.query_id
```

`DRSTemporalQueryV01.query_id` is the existing
`drsquery_v01:<64-lowercase-hex>` derived identity produced by
`build_drs_temporal_query_v01`. The current direct-reuse Root input and result
retain `transaction_id == query.query_id`. G2-C v0.1 defines neither a raw
request-to-query constructor nor a general outer-transaction/subquery bridge.

```text
RAW_USER_REQUEST_TO_G2B_QUERY_CROSS_BINDING_IMPLEMENTED=false
OUTER_TRANSACTION_TO_G2B_SUBQUERY_BINDING_IMPLEMENTED=false
```

#### 7.2.5 ExecutionModeLocalModeProfileV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `local_mode_profile_id` | canonical `str` |
| 2 | `request_id` | `str` |
| 3 | `transaction_id` | `str` |
| 4 | `owning_root_id` | `str` |
| 5 | `domain_id` | `str` |
| 6 | `mode` | one executable canonical mode |
| 7 | `policy_snapshot_id` | `str` |
| 8 | `capability_snapshot_id` | `str` |
| 9 | `cost_model_id` | `str` |
| 10 | `policy_allowed` | exact `bool` |
| 11 | `scope_allowed` | exact `bool` |
| 12 | `risk_allowed` | exact `bool` |
| 13 | `privacy_allowed` | exact `bool` |
| 14 | `capability_state` | `NOT_REQUIRED`, `AVAILABLE`, or `UNAVAILABLE` |
| 15 | `capability_id` | `str | None` |
| 16 | `cost_unit` | literal `normalized_cost_units_v01` |
| 17 | `cost_units` | nonnegative signed-int64 |
| 18 | `local_reason_codes` | builder-derived ordered public G2-C tuple; never caller supplied |
| 19 | `authority_created` | exact false |
| 20 | `permission_created` | exact false |
| 21 | `real_world_effects_count` | exact zero |

Replay and direct-reuse profiles require `NOT_REQUIRED` and `None` capability.
The other six executable modes require a nonempty declared capability ID; an
unavailable capability retains that ID and uses `UNAVAILABLE`.

Valid-but-negative local reasons are derived in this exact order:

```text
g2c_policy_forbidden
g2c_scope_forbidden
g2c_risk_forbidden
g2c_privacy_forbidden
g2c_capability_unavailable
```

Each false local gate contributes its exact reason. Required
`UNAVAILABLE` capability contributes `g2c_capability_unavailable`.
`NOT_REQUIRED` is legal only for `sealed_replay` and
`direct_informational_reuse`. The builder derives the complete tuple in this
order and accepts no reason argument. Validation reconstructs it exactly:
duplicates, omission of a false gate, added reasons, or reordered reasons fail
closed. A fully allowed coherent profile has `local_reason_codes=()`.

Invalid cost type, bool-as-int, negative value, signed-int64 overflow, or wrong
cost unit is a structural builder/validator failure. No valid local profile,
router input, or proposal is produced. `g2c_cost_invalid` appears only in the
resulting FAIL_CLOSED validation report, never in a valid profile's
`local_reason_codes`.

#### 7.2.6 ExecutionModeLocalRoutingSnapshotV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `local_routing_snapshot_id` | canonical `str` |
| 2 | `created_by` | `OWNING_LOCAL_ROOT_ROUTING_SNAPSHOT_V01` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `request_class` | machine code |
| 8 | `action_class` | `ACTION` or `NON_ACTION` |
| 9 | `action_packet_relation` | `NOT_APPLICABLE`, `NEW_ACTION_NO_PACKET`, or `EXISTING_PACKET_ATTEMPT` |
| 10 | `scope_class` | machine code |
| 11 | `scope_ref` | `str` |
| 12 | `permitted_narrower_scope_refs` | canonical `tuple[str, ...]` |
| 13 | `risk_class` | `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` |
| 14 | `policy_snapshot_id` | `str` |
| 15 | `capability_snapshot_id` | `str` |
| 16 | `cost_model_id` | `str` |
| 17 | `required_user_input_state` | `COMPLETE` or `MISSING_RESOLVABLE` |
| 18 | `hard_block_state` | `CLEAR` or `BLOCKED` |
| 19 | `evaluation_time_epoch_seconds` | exact bounded `int` |
| 20 | `pt_created_at_utc` | exact UTC timestamp |
| 21 | `kt_asof_utc` | exact UTC timestamp from field 19 |
| 22 | `et_observed_at_utc` | exact UTC timestamp |
| 23 | `ct_session_anchor` | `str` |
| 24 | `ttl_seconds` | nonnegative signed-int64 |
| 25 | `freshness_class` | current Kernel freshness literal |
| 26 | `valid_from_utc` | exact UTC timestamp |
| 27 | `valid_to_utc` | exact UTC timestamp |
| 28 | `time_envelope_ref` | exact rebuilt reference |
| 29 | `mode_profile_set_id` | `emprofiles_v01:` identity |
| 30 | `mode_profile_set_sha256` | lowercase SHA-256 |
| 31 | `mode_profiles` | exact eight-item `tuple[ExecutionModeLocalModeProfileV01, ...]` |
| 32 | `authority_created` | exact false |
| 33 | `permission_created` | exact false |
| 34 | `real_world_effects_count` | exact zero |

The profile-set identity and digest cover the complete ordered profile tuple
plus request, transaction, Root, domain, policy, capability, and cost-model
identities. There is no caller-supplied cost-snapshot identity and no circular
snapshot material.

The nested identities are frozen:

```text
time envelope domain: HEDGEHOG_EXECUTION_MODE_TIME_ENVELOPE_REF_V01
time envelope prefix: emtime_v01:
profile-set domain: HEDGEHOG_EXECUTION_MODE_LOCAL_MODE_PROFILE_SET_V01
profile-set prefix: emprofiles_v01:
```

`time_envelope_ref` uses the exact Section 6.2 identity over current Kernel
plain data in order: `ct_session_anchor`, `et_observed_at`,
`freshness_class`, `kt_asof`, `pt_created_at`, `ttl_seconds`, `valid_from`, and
`valid_to`. `mode_profile_set_sha256` is the plain SHA-256 of the exact
ordered eight plain profile projections. `mode_profile_set_id` hashes
`request_id`, `transaction_id`, `owning_root_id`, `domain_id`,
`policy_snapshot_id`, `capability_snapshot_id`, `cost_model_id`, that
digest, and the exact ordered local profile IDs. Callers supply neither nested
identity.

#### 7.2.7 ExecutionModeRouterInputV01

| # | Field | Exact type |
|---:|---|---|
| 1 | `router_input_id` | canonical `str` |
| 2 | `request_id` | `str` |
| 3 | `transaction_id` | `str` |
| 4 | `owning_root_id` | `str` |
| 5 | `bsep_binding` | exact `ExecutionModeBSEPBindingV01` |
| 6 | `local_routing_snapshot` | exact `ExecutionModeLocalRoutingSnapshotV01` |
| 7 | `replay_binding` | exact `ExecutionModeReplayBindingV01` |
| 8 | `g2a_binding` | exact `ExecutionModeG2ABindingV01` |
| 9 | `g2b_binding` | exact `ExecutionModeG2BBindingV01` |
| 10 | `trace_refs` | exact builder-derived unique lexical tuple; never caller supplied |

```text
ROUTER_INPUT_FIELD_COUNT=10
```

Domain is cross-bound through all nested bindings and the local snapshot. No
free mode, policy, capability, availability, cost, permission, or authority
field exists here.

#### 7.2.8 ExecutionModeFeasibilityRowV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `feasibility_row_id` | canonical `str` |
| 2 | `source_input_id` | `str` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `mode` | canonical mode |
| 8 | `category` | `EXECUTABLE` or `TERMINAL` |
| 9 | `safe_depth_rank` | exact rank or `None` for terminal |
| 10 | `feasibility_status` | `FEASIBLE`, `INFEASIBLE`, `TERMINAL_SELECTED`, or `TERMINAL_NOT_SELECTED` |
| 11 | `local_mode_profile_id` | profile ID or `None` for terminal |
| 12 | `required_evidence_refs` | canonical tuple |
| 13 | `satisfied_evidence_refs` | canonical tuple |
| 14 | `missing_evidence_codes` | ordered public reason tuple |
| 15 | `reason_codes` | ordered public reason tuple |
| 16 | `required_capability_id` | `str | None` |
| 17 | `cost_units` | nonnegative signed-int64 or `None` for terminal |
| 18 | `downstream_compute_class` | `NONE`, `MEMORY_INFORMED`, `LOCAL_SLM`, `CLOUD_LLM`, `FULL_SEMANTIC`, `FULL_FRACTAL`, or `TERMINAL` |
| 19 | `root_review_required` | exact true |
| 20 | `authority_created` | exact false |
| 21 | `permission_created` | exact false |
| 22 | `real_world_effects_count` | exact zero |

Every row has deterministic evidence ordering. The universal prefix is
`(bsep_binding_id, local_routing_snapshot_id)`. Every executable row then
contains its `local_mode_profile_id`. Mode additions follow exactly:

| Mode | Ordered additions after the universal prefix and local profile |
|---|---|
| `deterministic` | deterministic capability ID |
| `sealed_replay` | replay binding ID, then replay ID when bound |
| `direct_informational_reuse` | G2-B binding ID, report ID, ReuseCertificate ID, source Root decision ID |
| `memory_informed` | G2-B binding ID, report ID, memory-informed capability ID |
| `local_slm` | local-SLM capability ID |
| `cloud_llm` | cloud-LLM capability ID |
| `full_semantic` | full-semantic capability ID |
| `full_fractal` | full-fractal capability ID |

For `EXISTING_PACKET_ATTEMPT`, append G2-A binding ID, packet ID, then source
inspection SHA-256. Fresh action and non-action rows append no invented packet
reference. Terminal rows contain only the universal two references.
`satisfied_evidence_refs` is the exact ordered subset whose sources validate;
`missing_evidence_codes` contains registered reasons, never fabricated refs.

#### 7.2.9 ExecutionModeProposalV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `proposal_id` | canonical `str` |
| 2 | `source_input_id` | `str` |
| 3 | `request_id` | `str` |
| 4 | `transaction_id` | `str` |
| 5 | `owning_root_id` | `str` |
| 6 | `domain_id` | `str` |
| 7 | `source_bsep_binding_id` | `str` |
| 8 | `source_bsep_packet_id` | `str` |
| 9 | `source_bsep_sha256` | lowercase SHA-256 |
| 10 | `source_local_routing_snapshot_id` | `str` |
| 11 | `source_replay_binding_id` | `str` |
| 12 | `source_g2a_binding_id` | `str` |
| 13 | `source_g2b_binding_id` | `str` |
| 14 | `selected_mode` | canonical mode |
| 15 | `selected_safe_depth_rank` | exact rank or `None` |
| 16 | `selected_local_mode_profile_id` | `str | None` |
| 17 | `selected_expected_cost_units` | exact `int | None` |
| 18 | `proposed_scope_ref` | `str | None`; absent for terminal |
| 19 | `ordered_feasibility_rows` | exact ten rows in canonical mode order |
| 20 | `selected_feasibility_row_id` | exact selected row ID |
| 21 | `reason_codes` | ordered public reason tuple |
| 22 | `required_downstream_capability_ids` | canonical tuple |
| 23 | `downstream_consumption_class` | `SHORTCUT_RETURN_TO_ROOT`, `RUNTIME_TOPOLOGY_ELIGIBLE`, or `TERMINAL_NO_CONSUMPTION` |
| 24 | `downstream_action_packet_required` | exact derived `bool` |
| 25 | `root_review_required` | exact true |
| 26 | `authority_created` | exact false |
| 27 | `permission_created` | exact false |
| 28 | `action_commit_packet_created` | exact false |
| 29 | `receipt_created` | exact false |
| 30 | `topology_created` | exact false |
| 31 | `final_output_created` | exact false |
| 32 | `drs_write_created` | exact false |
| 33 | `real_world_effects_count` | exact zero |

#### 7.2.10 RootExecutionModeReviewInputV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `root_review_input_id` | canonical `str` |
| 2 | `request_id` | `str` |
| 3 | `transaction_id` | `str` |
| 4 | `owning_root_id` | `str` |
| 5 | `domain_id` | `str` |
| 6 | `proposal_id` | `str` |
| 7 | `router_input_id` | `str` |
| 8 | `proposal_artifact_id` | exact contextually validated proposal Kernel artifact ID |
| 9 | `proposal_transition_decision_id` | exact contextually validated proposal-to-Root Transition decision ID |
| 10 | `created_by` | `OWNING_LOCAL_ROOT_EXECUTION_MODE_REVIEW_V01` |
| 11 | `review_action` | `ACCEPT`, `NARROW`, `REJECT`, or `TERMINAL_FROM_PROPOSAL` |
| 12 | `proposed_mode` | exact proposal mode |
| 13 | `proposed_scope_ref` | `str | None` |
| 14 | `accepted_scope_ref` | `str | None` |
| 15 | `scope_narrowing_proof_id` | rebuilt `str | None` |
| 16 | `narrowing_basis_refs` | canonical tuple |
| 17 | `policy_snapshot_id` | exact `router_input.local_routing_snapshot.policy_snapshot_id` |
| 18 | `evaluation_time_epoch_seconds` | exact snapshot epoch |
| 19 | `time_envelope_ref` | exact snapshot reference |
| 20 | `root_local_context_id` | exact Section 12.2 derived identity; never caller supplied |
| 21 | `trace_refs` | exact builder-derived unique lexical tuple; never caller supplied |

`proposal_artifact_id` is the validated proposal artifact, and
`proposal_transition_decision_id` is the validated pre-Root G2-C
`RETURN_TO_ROOT` decision. The review input cannot be built before both
validate. `policy_snapshot_id` binds the policy identity, never the local
routing snapshot identity.

```text
ROOT_REVIEW_INPUT_FIELD_COUNT=21
```

#### 7.2.11 RootExecutionModeDecisionV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `decision_id` | canonical `str` |
| 2 | `root_review_input_id` | `str` |
| 3 | `proposal_id` | `str` |
| 4 | `router_input_id` | `str` |
| 5 | `request_id` | `str` |
| 6 | `transaction_id` | `str` |
| 7 | `owning_root_id` | `str` |
| 8 | `domain_id` | `str` |
| 9 | `outcome` | `ACCEPT`, `NARROW`, `REJECT`, `BLOCKED`, or `NEEDS_USER` |
| 10 | `accepted_mode` | executable mode or `None` |
| 11 | `accepted_scope_ref` | `str | None` |
| 12 | `scope_narrowing_proof_id` | `str | None` |
| 13 | `downstream_consumption_class` | proposal class or `TERMINAL_NO_CONSUMPTION` after rejection |
| 14 | `downstream_action_packet_required` | exact derived `bool` |
| 15 | `source_root_decision_id` | actual source ID |
| 16 | `source_root_decision_input_id` | actual source input ID |
| 17 | `source_root_decision` | exact current Root decision literal |
| 18 | `source_root_reason_code` | exact current Root reason |
| 19 | `source_root_transition_decision_id` | actual existing Root Kernel source Transition ID |
| 20 | `source_root_transition_decision` | exact existing Root Kernel source Transition decision |
| 21 | `reason_codes` | exact one-item G2-C Root projection reason tuple |
| 22 | `route_eligibility_candidate` | non-authoritative true only for contextually valid `ACCEPT`/`NARROW` |
| 23 | `authority_created` | exact false; source Root authority is referenced, not recreated |
| 24 | `permission_created` | exact false |
| 25 | `action_commit_packet_created` | exact false |
| 26 | `receipt_created` | exact false |
| 27 | `topology_created` | exact false |
| 28 | `final_output_created` | exact false |
| 29 | `drs_write_created` | exact false |
| 30 | `real_world_effects_count` | exact zero |

```text
ROOT_DECISION_FIELD_COUNT=30
```

The projection reason tuple is exactly `(g2c_root_accept_projected,)`,
`(g2c_root_narrow_projected,)`, `(g2c_root_reject_projected,)`,
`(g2c_root_blocked_projected,)`, or `(g2c_root_needs_user_projected,)` for the
corresponding outcome. It is distinct from `source_root_reason_code` and is
included in serialization, identity, schema, structural/contextual validation,
and the decision ABI-safe payload immediately after
`source_root_transition_decision`.

For ACCEPT/NARROW, `downstream_action_packet_required` copies the proposal.
For REJECT/BLOCKED/NEEDS_USER it is false. RouteEligibility copies the accepted
decision value and exists only for ACCEPT/NARROW.

`route_eligibility_candidate` is false for REJECT, BLOCKED, and NEEDS_USER.
It is only a candidate marker: it permits no route consumption, topology,
permission, or ActionCommitPacket. Only a contextually validated
`ExecutionModeRouteEligibility` Kernel artifact created after the post-Root
G2-C Transition permits bounded downstream route consumption.

- `SHORTCUT_RETURN_TO_ROOT` returns an accepted bounded shortcut upward to
  Root.
- `RUNTIME_TOPOLOGY_ELIGIBLE` is the only eligibility class a later G2-D
  topology builder may consume.
- `TERMINAL_NO_CONSUMPTION` creates no RouteEligibility artifact.

Direct downstream use of `RootExecutionModeDecisionV01` as route permission
fails closed with `g2c_route_decision_bypass_forbidden`.

#### 7.2.12 ExecutionModeValidationReportV01

| # | Field | Exact type / law |
|---:|---|---|
| 1 | `validation_report_id` | canonical `str` |
| 2 | `validation_target` | exact target enum below |
| 3 | `validated_artifact_id` | `str | None` |
| 4 | `request_id` | `str | None` |
| 5 | `transaction_id` | `str | None` |
| 6 | `owning_root_id` | `str | None` |
| 7 | `domain_id` | `str | None` |
| 8 | `validation_status` | `PASS` or `FAIL_CLOSED` |
| 9 | `failure_stage` | exact stage enum below |
| 10 | `return_to_root_required` | false on PASS, true on FAIL_CLOSED |
| 11 | `reason_codes` | ordered public reason tuple |
| 12 | `source_reason_codes` | ordered source-owned tuple |
| 13 | `authority_created` | exact false |
| 14 | `permission_created` | exact false |
| 15 | `real_world_effects_count` | exact zero |

Validation targets are exactly:

```text
ExecutionModeBSEPBindingV01
ExecutionModeReplayBindingV01
ExecutionModeG2ABindingV01
ExecutionModeG2BBindingV01
ExecutionModeLocalModeProfileV01
ExecutionModeLocalRoutingSnapshotV01
ExecutionModeRouterInputV01
ExecutionModeFeasibilityRowV01
ExecutionModeProposalV01
RootExecutionModeReviewInputV01
RootExecutionModeDecisionV01
ExecutionModeValidationReportV01
SOURCE_CONTEXT_STRUCTURAL
ROUTER_INPUT_AGAINST_SOURCES
PROPOSAL_AGAINST_SOURCES
ROOT_REVIEW_AGAINST_SOURCES
ROOT_DECISION_AGAINST_SOURCE
ROUTE_ELIGIBILITY_AGAINST_SOURCE
ABI_PROFILE
TRANSITION_PROFILE
```

```text
VALIDATION_TARGET_COUNT=20
```

Identity fields 4..7 are either all present and exact or all `None`. PASS for
`SOURCE_CONTEXT_STRUCTURAL` uses all `None` because structural source-context
validation does not trust source contents as canonical identities. A
`FAIL_CLOSED` report before safe identity extraction also uses all `None`.
Every other PASS after router-input recognition requires all four values.
No partial identity tuple is valid.

Failure stages are exactly `NONE`, `STRUCTURAL`, `SOURCE_CONTEXT`,
`BUSINESS_REQUEST`, `BSEP`, `REPLAY`, `G2A`, `G2B`, `LOCAL_PROFILE`,
`TIME_ENVELOPE`, `FEASIBILITY`, `SELECTION`, `PROPOSAL`, `ROOT_REVIEW`,
`ROOT_DECISION`, `ABI`, `TRANSITION`, and `ROUTE_ELIGIBILITY`. PASS requires
`NONE`; FAIL_CLOSED forbids `NONE`.

#### 7.2.13 ExecutionModeSourceContextV01

| # | Field | Exact runtime type / presence law |
|---:|---|---|
| 1 | `business_request_context_packet` | exact plain `dict[str, object]` |
| 2 | `bsep_packet` | exact plain `dict[str, object]` |
| 3 | `bsep_route_context_packet` | exact plain `dict[str, object]` |
| 4 | `bsep_orchestrator_proposal` | exact plain `dict[str, object]` |
| 5 | `bsep_structured_rationale` | exact plain `dict[str, object]` |
| 6 | `sealed_replay_evidence` | `SealedReplayEvidenceV01 | None` |
| 7 | `replay_source_manifest` | `SealedPackageManifestV01 | None` |
| 8 | `replay_source_domain_projection` | `DomainEvidenceProjectionV01 | None` |
| 9 | `replay_source_safe_file_contents` | exact `tuple[bytes, ...]` |
| 10 | `replay_anchor_publication` | `ExternalAnchorPublicationV01 | None` |
| 11 | `replay_anchored_verification` | `AnchoredPackageVerificationV01 | None` |
| 12 | `replay_supplied_anchor_publication_id` | `str | None` |
| 13 | `replay_reconstructed_manifest` | `SealedPackageManifestV01 | None` |
| 14 | `replay_reconstructed_domain_projection` | `DomainEvidenceProjectionV01 | None` |
| 15 | `replay_reconstructed_safe_file_contents` | exact `tuple[bytes, ...]` |
| 16 | `g2a_inspection` | `ActionPacketPresentEligibilityInspectionV01 | None` |
| 17 | `g2a_registry` | `ActionCommitPacketRegistryV02 | None` |
| 18 | `g2a_packet_id` | `str | None` |
| 19 | `g2a_corridor` | `ContractFulfillmentCorridorV01 | None` |
| 20 | `g2a_corridor_step` | `CorridorStepV01 | None` |
| 21 | `g2a_current_dependency_observations` | exact `tuple[ActionDependencyCurrentObservationV01, ...]` |
| 22 | `g2a_logical_time_bridge` | `LogicalTimeBridgeV01 | None` |
| 23 | `g2a_evaluation_time` | signed-int64 or `None` |
| 24 | `g2a_evaluation_time_source` | `str | None` |
| 25 | `g2a_evaluation_context_id` | `str | None` |
| 26 | `g2a_transition_registry_profile` | `ActionPacketTransitionRegistryProfileV01 | None` |
| 27 | `g2b_resolution_report` | `DRSResolutionReportV01 | None` |
| 28 | `g2b_compatibility_projections` | exact `tuple[LegacyDRSProjectionV01, ...]` |
| 29 | `g2b_use_time` | signed-int64 or `None` |
| 30 | `g2b_root_kernel` | `RootDecisionKernelV01 | None` |
| 31 | `g2b_root_decision_input` | `RootDecisionInputV01 | None` |
| 32 | `g2b_root_decision_result` | `RootDecisionResultV01 | None` |
| 33 | `g2b_writeback_evidence` | exact `None` in v0.1 |

The five BSEP-family values are actual source objects. The source context holds
no provider client, connector, callback, effect handle, secret, credential,
topology, or final output. Exact conditional presence matrices are frozen in
Sections 8, 13, and 14.

The complete structural presence matrix is:

| Family/state | Required shape |
|---|---|
| Replay absent | fields 6..15 are exact `None`/empty geometry |
| Replay bound | every field 6..15 is present and exact |
| G2-A `NO_PACKET` | inspection, registry, packet, corridor, step, logical-time bridge, and ActionPacket Transition profile are `None`; dependency observations empty; evaluation time, source, and context ID have exact local source types |
| G2-A `PRESENT_INSPECTION_BOUND` | every G2-A source field is present and has exact source type; dependency observations are an exact tuple |
| G2-B `NOT_APPLICABLE` | report absent; compatibility tuple empty; use time absent; Root triple absent; writeback `None` |
| G2-B `RESOLUTION_CONTEXT_BOUND` | report present; compatibility tuple exact; use time present; Root triple absent; writeback `None` |
| G2-B `DIRECT_REUSE_BOUND` | report present; compatibility tuple exact; use time present; complete Root triple present; writeback `None` |

Any partial or mixed family shape fails structural validation. Cross-family
identity, time, digest, request, transaction, Root, domain, binding-state, and
local-snapshot equality belongs only to contextual validation against a router
input.

#### 7.2.14 Exact schema contract

All three G2-C `KernelArtifactV01` projections freeze `abi_version="v1.0"`
and `schema_version="v0.1"`. These exact values participate in each contextual
Kernel artifact identity.

`schemas/execution_mode_router_v01.schema.json` has exactly:

```text
$schema: https://json-schema.org/draft/2020-12/schema
$id: https://hedgehog.local/schemas/execution_mode_router_v01.schema.json
title: Hedgehog ExecutionModeRouter v0.1
top-level $ref: #/$defs/ExecutionModeRouterInputV01
serialized definition count: 12
```

The twelve definitions are exactly the serialized types in Section 7.1;
`ExecutionModeSourceContextV01` is absent. Every dataclass field is required,
nullable fields use exact null unions, every object has
`additionalProperties: false`, arrays carry the frozen cardinality bounds,
and enums, integer bounds, identity patterns, source-native identity
exceptions, SHA patterns, and the 128-character public-reason pattern match
the Python contract. `schemas/kernel_artifact_v01.schema.json` changes only by
appending the three exact G2-C artifact-type enum literals.

### 7.3 Exact public function surface

`PUBLIC_G2C_FUNCTIONS_V01` is exactly the following final ordered tuple. It is
the G2-C4-and-later public target, not a requirement that every callable exist
after G2-C1. The six profile/data functions identified below live in
`transition_registry_v01.py` and first exist in G2-C4; every other G2-C-specific
name lives in `execution_mode_router_v01.py`, with all sixty-eight complete by
G2-C4. `abi_v01.py` and `root_decision_v01.py` own no G2-C-specific public
function.

```text
build_execution_mode_source_context_v01
validate_execution_mode_source_context_v01
build_execution_mode_bsep_binding_v01
build_execution_mode_replay_not_applicable_binding_v01
build_execution_mode_replay_binding_v01
build_execution_mode_g2a_no_packet_binding_v01
build_execution_mode_g2a_binding_v01
build_execution_mode_g2b_not_applicable_binding_v01
build_execution_mode_g2b_binding_v01
build_execution_mode_local_mode_profile_v01
build_execution_mode_local_routing_snapshot_v01
build_execution_mode_router_input_v01
evaluate_execution_mode_feasibility_v01
select_execution_mode_v01
build_execution_mode_proposal_v01
build_execution_mode_validation_report_v01
build_root_execution_mode_review_input_v01
build_execution_mode_root_decision_source_v01
project_root_execution_mode_decision_v01
route_execution_mode_v01
review_execution_mode_proposal_v01
validate_execution_mode_router_input_against_sources_v01
validate_execution_mode_proposal_against_sources_v01
validate_root_execution_mode_review_input_against_sources_v01
validate_root_execution_mode_decision_against_source_v01
validate_execution_mode_route_eligibility_against_source_v01
project_execution_mode_proposal_kernel_artifact_v01
project_root_execution_mode_decision_kernel_artifact_v01
project_execution_mode_route_eligibility_kernel_artifact_v01
validate_execution_mode_abi_profile_v01
build_execution_mode_transition_registry_profile_v01
validate_execution_mode_transition_registry_profile_v01
execution_mode_transition_registry_profile_to_plain_dict_v01
validate_execution_mode_transition_decision_v01
execution_mode_transition_decision_to_plain_dict_v01
rebuild_execution_mode_transition_decision_identity_v01
evaluate_execution_mode_proposal_to_root_transition_v01
evaluate_execution_mode_root_route_transition_v01
validate_execution_mode_bsep_binding_v01
execution_mode_bsep_binding_to_plain_data_v01
rebuild_execution_mode_bsep_binding_identity_v01
validate_execution_mode_replay_binding_v01
execution_mode_replay_binding_to_plain_data_v01
rebuild_execution_mode_replay_binding_identity_v01
validate_execution_mode_g2a_binding_v01
execution_mode_g2a_binding_to_plain_data_v01
rebuild_execution_mode_g2a_binding_identity_v01
validate_execution_mode_g2b_binding_v01
execution_mode_g2b_binding_to_plain_data_v01
rebuild_execution_mode_g2b_binding_identity_v01
validate_execution_mode_local_mode_profile_v01
execution_mode_local_mode_profile_to_plain_data_v01
rebuild_execution_mode_local_mode_profile_identity_v01
validate_execution_mode_local_routing_snapshot_v01
execution_mode_local_routing_snapshot_to_plain_data_v01
rebuild_execution_mode_local_routing_snapshot_identity_v01
validate_execution_mode_router_input_v01
execution_mode_router_input_to_plain_data_v01
rebuild_execution_mode_router_input_identity_v01
validate_execution_mode_feasibility_row_v01
execution_mode_feasibility_row_to_plain_data_v01
rebuild_execution_mode_feasibility_row_identity_v01
validate_execution_mode_proposal_v01
execution_mode_proposal_to_plain_data_v01
rebuild_execution_mode_proposal_identity_v01
validate_root_execution_mode_review_input_v01
root_execution_mode_review_input_to_plain_data_v01
rebuild_root_execution_mode_review_input_identity_v01
validate_root_execution_mode_decision_v01
root_execution_mode_decision_to_plain_data_v01
rebuild_root_execution_mode_decision_identity_v01
validate_execution_mode_validation_report_v01
execution_mode_validation_report_to_plain_data_v01
rebuild_execution_mode_validation_report_identity_v01
```

The tuple contains exactly seventy-four names:

```text
PUBLIC_G2C_FUNCTION_COUNT=74
```

The final thirty-six entries are, in Section 7.1 order, each serialized type's
structural validator, plain-data serializer, and identity rebuilder. No implied
or wildcard tuple member exists.

The six Transition-owned functions are exactly
`build_execution_mode_transition_registry_profile_v01`,
`validate_execution_mode_transition_registry_profile_v01`,
`execution_mode_transition_registry_profile_to_plain_dict_v01`,
`validate_execution_mode_transition_decision_v01`,
`execution_mode_transition_decision_to_plain_dict_v01`, and
`rebuild_execution_mode_transition_decision_identity_v01`. They first exist in
G2-C4. G2-C1 through G2-C3 may not create a stub, alias, `NotImplemented` body,
placeholder callable, speculative package attribute, import fallback, lazy
missing-symbol proxy, or any early future-owned implementation merely to
satisfy facade tests.

Exact signatures:

```python
def build_execution_mode_source_context_v01(*, business_request_context_packet: dict[str, object], bsep_packet: dict[str, object], bsep_route_context_packet: dict[str, object], bsep_orchestrator_proposal: dict[str, object], bsep_structured_rationale: dict[str, object], sealed_replay_evidence: SealedReplayEvidenceV01 | None, replay_source_manifest: SealedPackageManifestV01 | None, replay_source_domain_projection: DomainEvidenceProjectionV01 | None, replay_source_safe_file_contents: tuple[bytes, ...], replay_anchor_publication: ExternalAnchorPublicationV01 | None, replay_anchored_verification: AnchoredPackageVerificationV01 | None, replay_supplied_anchor_publication_id: str | None, replay_reconstructed_manifest: SealedPackageManifestV01 | None, replay_reconstructed_domain_projection: DomainEvidenceProjectionV01 | None, replay_reconstructed_safe_file_contents: tuple[bytes, ...], g2a_inspection: ActionPacketPresentEligibilityInspectionV01 | None, g2a_registry: ActionCommitPacketRegistryV02 | None, g2a_packet_id: str | None, g2a_corridor: ContractFulfillmentCorridorV01 | None, g2a_corridor_step: CorridorStepV01 | None, g2a_current_dependency_observations: tuple[ActionDependencyCurrentObservationV01, ...], g2a_logical_time_bridge: LogicalTimeBridgeV01 | None, g2a_evaluation_time: int | None, g2a_evaluation_time_source: str | None, g2a_evaluation_context_id: str | None, g2a_transition_registry_profile: ActionPacketTransitionRegistryProfileV01 | None, g2b_resolution_report: DRSResolutionReportV01 | None, g2b_compatibility_projections: tuple[LegacyDRSProjectionV01, ...], g2b_use_time: int | None, g2b_root_kernel: RootDecisionKernelV01 | None, g2b_root_decision_input: RootDecisionInputV01 | None, g2b_root_decision_result: RootDecisionResultV01 | None, g2b_writeback_evidence: None) -> ExecutionModeSourceContextV01
def validate_execution_mode_source_context_v01(value: object) -> ExecutionModeValidationReportV01
def build_execution_mode_bsep_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, source_context: ExecutionModeSourceContextV01) -> ExecutionModeBSEPBindingV01
def build_execution_mode_replay_not_applicable_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str) -> ExecutionModeReplayBindingV01
def build_execution_mode_replay_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, source_context: ExecutionModeSourceContextV01) -> ExecutionModeReplayBindingV01
def build_execution_mode_g2a_no_packet_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, evaluation_time: int, evaluation_time_source: str, evaluation_context_id: str) -> ExecutionModeG2ABindingV01
def build_execution_mode_g2a_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, source_context: ExecutionModeSourceContextV01) -> ExecutionModeG2ABindingV01
def build_execution_mode_g2b_not_applicable_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str) -> ExecutionModeG2BBindingV01
def build_execution_mode_g2b_binding_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, source_context: ExecutionModeSourceContextV01) -> ExecutionModeG2BBindingV01
def build_execution_mode_local_mode_profile_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, mode: str, policy_snapshot_id: str, capability_snapshot_id: str, cost_model_id: str, policy_allowed: bool, scope_allowed: bool, risk_allowed: bool, privacy_allowed: bool, capability_state: str, capability_id: str | None, cost_units: int) -> ExecutionModeLocalModeProfileV01
def build_execution_mode_local_routing_snapshot_v01(*, request_id: str, transaction_id: str, owning_root_id: str, domain_id: str, request_class: str, action_class: str, action_packet_relation: str, scope_class: str, scope_ref: str, permitted_narrower_scope_refs: tuple[str, ...], risk_class: str, policy_snapshot_id: str, capability_snapshot_id: str, cost_model_id: str, required_user_input_state: str, hard_block_state: str, evaluation_time_epoch_seconds: int, pt_created_at_utc: str, et_observed_at_utc: str, ct_session_anchor: str, ttl_seconds: int, freshness_class: str, valid_from_utc: str, valid_to_utc: str, mode_profiles: tuple[ExecutionModeLocalModeProfileV01, ...]) -> ExecutionModeLocalRoutingSnapshotV01
def build_execution_mode_router_input_v01(*, request_id: str, transaction_id: str, owning_root_id: str, bsep_binding: ExecutionModeBSEPBindingV01, local_routing_snapshot: ExecutionModeLocalRoutingSnapshotV01, replay_binding: ExecutionModeReplayBindingV01, g2a_binding: ExecutionModeG2ABindingV01, g2b_binding: ExecutionModeG2BBindingV01) -> ExecutionModeRouterInputV01
def evaluate_execution_mode_feasibility_v01(*, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01) -> tuple[ExecutionModeFeasibilityRowV01, ...]
def select_execution_mode_v01(*, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, ordered_rows: tuple[ExecutionModeFeasibilityRowV01, ...]) -> ExecutionModeFeasibilityRowV01
def build_execution_mode_proposal_v01(*, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, ordered_rows: tuple[ExecutionModeFeasibilityRowV01, ...], selected_row: ExecutionModeFeasibilityRowV01) -> ExecutionModeProposalV01
def build_execution_mode_validation_report_v01(*, validation_target: str, validated_artifact_id: str | None, request_id: str | None, transaction_id: str | None, owning_root_id: str | None, domain_id: str | None, validation_status: str, failure_stage: str, return_to_root_required: bool, reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...]) -> ExecutionModeValidationReportV01
def build_root_execution_mode_review_input_v01(*, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, review_action: str, accepted_scope_ref: str | None, narrowing_basis_refs: tuple[str, ...]) -> RootExecutionModeReviewInputV01
def build_execution_mode_root_decision_source_v01(*, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, root_kernel: RootDecisionKernelV01) -> tuple[SemanticWorkRequestV01, NormalizedClaimV01, ActorContributionV01, RootReviewPacketV01, RootDecisionInputV01, RootDecisionResultV01]
def project_root_execution_mode_decision_v01(*, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01) -> RootExecutionModeDecisionV01
def route_execution_mode_v01(*, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01) -> tuple[ExecutionModeProposalV01 | None, ExecutionModeValidationReportV01]
def review_execution_mode_proposal_v01(*, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01) -> tuple[RootExecutionModeDecisionV01 | None, RootDecisionKernelV01 | None, RootDecisionInputV01 | None, RootDecisionResultV01 | None, ExecutionModeValidationReportV01]
def validate_execution_mode_router_input_against_sources_v01(*, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01) -> ExecutionModeValidationReportV01
def validate_execution_mode_proposal_against_sources_v01(*, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01) -> ExecutionModeValidationReportV01
def validate_root_execution_mode_review_input_against_sources_v01(*, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01) -> ExecutionModeValidationReportV01
def validate_root_execution_mode_decision_against_source_v01(*, decision: RootExecutionModeDecisionV01, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01) -> ExecutionModeValidationReportV01
def validate_execution_mode_route_eligibility_against_source_v01(*, route_eligibility_artifact: KernelArtifactV01, decision: RootExecutionModeDecisionV01, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, decision_artifact: KernelArtifactV01, root_route_transition_decision: TransitionDecisionV01) -> ExecutionModeValidationReportV01
def project_execution_mode_proposal_kernel_artifact_v01(*, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01) -> KernelArtifactV01
def project_root_execution_mode_decision_kernel_artifact_v01(*, decision: RootExecutionModeDecisionV01, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01) -> KernelArtifactV01
def project_execution_mode_route_eligibility_kernel_artifact_v01(*, decision: RootExecutionModeDecisionV01, review_input: RootExecutionModeReviewInputV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, decision_artifact: KernelArtifactV01, root_route_transition_decision: TransitionDecisionV01) -> KernelArtifactV01 | None
def validate_execution_mode_abi_profile_v01(*, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, review_input: RootExecutionModeReviewInputV01, decision: RootExecutionModeDecisionV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, decision_artifact: KernelArtifactV01, root_route_transition_decision: TransitionDecisionV01, route_eligibility_artifact: KernelArtifactV01 | None) -> ExecutionModeValidationReportV01
def build_execution_mode_transition_registry_profile_v01() -> TransitionRegistryV01
def validate_execution_mode_transition_registry_profile_v01(registry: object) -> tuple[str, ...]
def execution_mode_transition_registry_profile_to_plain_dict_v01(registry: TransitionRegistryV01) -> dict[str, object]
def validate_execution_mode_transition_decision_v01(*, registry: TransitionRegistryV01, decision: object) -> tuple[str, ...]
def execution_mode_transition_decision_to_plain_dict_v01(*, registry: TransitionRegistryV01, decision: TransitionDecisionV01) -> dict[str, object]
def rebuild_execution_mode_transition_decision_identity_v01(decision: TransitionDecisionV01) -> str
def evaluate_execution_mode_proposal_to_root_transition_v01(*, registry: TransitionRegistryV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, proposal_artifact: KernelArtifactV01) -> TransitionDecisionV01
def evaluate_execution_mode_root_route_transition_v01(*, registry: TransitionRegistryV01, proposal_transition_decision: TransitionDecisionV01, review_input: RootExecutionModeReviewInputV01, decision: RootExecutionModeDecisionV01, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01, source_context: ExecutionModeSourceContextV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, proposal_artifact: KernelArtifactV01, decision_artifact: KernelArtifactV01) -> TransitionDecisionV01
```

The router-input builder derives `trace_refs` as the unique lexical tuple of
business-request packet ID, BSEP binding ID, local-routing-snapshot ID, Replay
binding ID, G2-A binding ID, and G2-B binding ID. It accepts no trace tuple.
The Root-review builder derives `root_local_context_id` under Section 12.2 and
derives review traces as the unique lexical tuple of proposal artifact ID,
proposal Transition decision ID, proposal ID, router-input ID, and Root-local
context ID. It accepts neither value from a caller. The Root source builder
calls and validates the exact complete tuple from
`build_default_component_trust_profiles_v01()` internally and accepts no
trust-profile tuple. The local-mode-profile builder derives its complete
canonical `local_reason_codes` from the gate, capability, and cost fields and
accepts no reason tuple.

The first six module-owned pure/profile functions are exactly the six
`transition_registry_v01.py` names in the ordered tuple. Contextual Transition,
Root, and ABI orchestration remains in `execution_mode_router_v01.py`.

For each `X` in the exact serialized type order, the public suffix has these
fully frozen signatures, with the names below replacing `X`:

```python
def validate_execution_mode_bsep_binding_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_bsep_binding_to_plain_data_v01(value: ExecutionModeBSEPBindingV01) -> dict[str, object]
def rebuild_execution_mode_bsep_binding_identity_v01(value: ExecutionModeBSEPBindingV01) -> str
def validate_execution_mode_replay_binding_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_replay_binding_to_plain_data_v01(value: ExecutionModeReplayBindingV01) -> dict[str, object]
def rebuild_execution_mode_replay_binding_identity_v01(value: ExecutionModeReplayBindingV01) -> str
def validate_execution_mode_g2a_binding_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_g2a_binding_to_plain_data_v01(value: ExecutionModeG2ABindingV01) -> dict[str, object]
def rebuild_execution_mode_g2a_binding_identity_v01(value: ExecutionModeG2ABindingV01) -> str
def validate_execution_mode_g2b_binding_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_g2b_binding_to_plain_data_v01(value: ExecutionModeG2BBindingV01) -> dict[str, object]
def rebuild_execution_mode_g2b_binding_identity_v01(value: ExecutionModeG2BBindingV01) -> str
def validate_execution_mode_local_mode_profile_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_local_mode_profile_to_plain_data_v01(value: ExecutionModeLocalModeProfileV01) -> dict[str, object]
def rebuild_execution_mode_local_mode_profile_identity_v01(value: ExecutionModeLocalModeProfileV01) -> str
def validate_execution_mode_local_routing_snapshot_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_local_routing_snapshot_to_plain_data_v01(value: ExecutionModeLocalRoutingSnapshotV01) -> dict[str, object]
def rebuild_execution_mode_local_routing_snapshot_identity_v01(value: ExecutionModeLocalRoutingSnapshotV01) -> str
def validate_execution_mode_router_input_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_router_input_to_plain_data_v01(value: ExecutionModeRouterInputV01) -> dict[str, object]
def rebuild_execution_mode_router_input_identity_v01(value: ExecutionModeRouterInputV01) -> str
def validate_execution_mode_feasibility_row_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_feasibility_row_to_plain_data_v01(value: ExecutionModeFeasibilityRowV01) -> dict[str, object]
def rebuild_execution_mode_feasibility_row_identity_v01(value: ExecutionModeFeasibilityRowV01) -> str
def validate_execution_mode_proposal_v01(value: object) -> ExecutionModeValidationReportV01
def execution_mode_proposal_to_plain_data_v01(value: ExecutionModeProposalV01) -> dict[str, object]
def rebuild_execution_mode_proposal_identity_v01(value: ExecutionModeProposalV01) -> str
def validate_root_execution_mode_review_input_v01(value: object) -> ExecutionModeValidationReportV01
def root_execution_mode_review_input_to_plain_data_v01(value: RootExecutionModeReviewInputV01) -> dict[str, object]
def rebuild_root_execution_mode_review_input_identity_v01(value: RootExecutionModeReviewInputV01) -> str
def validate_root_execution_mode_decision_v01(value: object) -> ExecutionModeValidationReportV01
def root_execution_mode_decision_to_plain_data_v01(value: RootExecutionModeDecisionV01) -> dict[str, object]
def rebuild_root_execution_mode_decision_identity_v01(value: RootExecutionModeDecisionV01) -> str
def validate_execution_mode_validation_report_v01(value: object) -> tuple[str, ...]
def execution_mode_validation_report_to_plain_data_v01(value: ExecutionModeValidationReportV01) -> dict[str, object]
def rebuild_execution_mode_validation_report_identity_v01(value: ExecutionModeValidationReportV01) -> str
```

No implementation-time naming or signature decision remains.

### 7.4 Complete ordered public reason-code registry

The exact registry, in order, is:

```text
g2c_exact_type_invalid
g2c_scalar_invalid
g2c_sequence_invalid
g2c_identity_invalid
g2c_identity_mismatch
g2c_request_binding_mismatch
g2c_transaction_binding_mismatch
g2c_root_binding_mismatch
g2c_domain_binding_mismatch
g2c_time_envelope_invalid
g2c_time_envelope_ref_identity_mismatch
g2c_source_context_invalid
g2c_source_context_structural_target_invalid
g2c_source_object_absent
g2c_source_object_substituted
g2c_source_digest_mismatch
g2c_source_validator_failed
g2c_business_request_invalid
g2c_business_request_ref_invalid
g2c_route_context_invalid
g2c_semantic_proposal_invalid
g2c_structured_rationale_invalid
g2c_bsep_invalid
g2c_replay_binding_invalid
g2c_g2a_relation_invalid
g2c_g2a_present_inspection_invalid
g2c_g2b_binding_invalid
g2c_g2b_binding_state_derivation_mismatch
g2c_g2b_query_transaction_mismatch
g2c_g2b_shortcut_invalid
g2c_g2b_use_time_invalid
g2c_local_mode_profile_invalid
g2c_local_mode_profile_set_invalid
g2c_mode_profile_set_identity_mismatch
g2c_policy_forbidden
g2c_scope_forbidden
g2c_risk_forbidden
g2c_privacy_forbidden
g2c_capability_unavailable
g2c_cost_invalid
g2c_noncanonical_mode
g2c_required_evidence_missing
g2c_action_shortcut_forbidden
g2c_deterministic_feasible
g2c_sealed_replay_feasible
g2c_direct_informational_reuse_feasible
g2c_memory_informed_feasible
g2c_local_slm_feasible
g2c_cloud_llm_feasible
g2c_full_semantic_feasible
g2c_full_fractal_feasible
g2c_hard_block_present
g2c_user_input_required
g2c_no_safe_mode
g2c_feasibility_row_invalid
g2c_selection_invalid
g2c_selection_tie_break_applied
g2c_proposal_rows_invalid
g2c_proposal_selected_row_mismatch
g2c_proposal_sources_valid
g2c_review_action_invalid
g2c_terminal_review_mismatch
g2c_scope_narrowing_invalid
g2c_root_input_invalid
g2c_root_result_invalid
g2c_root_mapping_invalid
g2c_policy_snapshot_binding_mismatch
g2c_terminal_contribution_scope_mismatch
g2c_root_accept_projected
g2c_root_narrow_projected
g2c_root_reject_projected
g2c_root_blocked_projected
g2c_root_needs_user_projected
g2c_abi_profile_invalid
g2c_abi_reserved_payload_key
g2c_abi_artifact_identity_mismatch
g2c_abi_parent_lineage_mismatch
g2c_abi_bundle_validation_failed
g2c_abi_projection_substituted
g2c_transition_profile_invalid
g2c_transition_registry_identity_mismatch
g2c_transition_decision_invalid
g2c_transition_decision_identity_mismatch
g2c_transition_root_review_required
g2c_transition_route_accept_allowed
g2c_transition_scope_narrow_allowed
g2c_transition_reject_recorded
g2c_transition_blocked_recorded
g2c_transition_needs_user_recorded
g2c_transition_guard_invalid
g2c_transition_root_commit_required
g2c_transition_substituted
g2c_proposal_transition_missing
g2c_proposal_transition_substituted
g2c_post_root_transition_missing
g2c_post_root_transition_substituted
g2c_route_eligibility_invalid
g2c_route_decision_bypass_forbidden
g2c_invalid_source_no_proposal
g2c_fail_closed_return_to_root
```

```text
PUBLIC_G2C_REASON_COUNT=100
```

The accepted registry performs exactly one hard-block reason rename in place;
`g2c_hard_block_present` occupies the same registry position. No other reason
is added or removed. `g2c_cost_invalid` remains
reachable only through structural profile construction/validation failure.
The five Root projection reasons are reachable through the serialized
`RootExecutionModeDecisionV01.reason_codes` field.

Every G2-C reason used by a builder, validator, feasibility row, Root review,
ABI projection, transition evaluation, case fixture, or negative test belongs
to this registry exactly once. Source-owned reasons remain source-owned.
Structural and contextual PASS reports use `reason_codes=()`; source PASS
reasons are not copied. Positive mode feasibility reasons live on FEASIBLE
rows, terminal selection reasons on the selected terminal row, Root projection
reasons on `RootExecutionModeDecisionV01`, Transition reasons on the existing
`TransitionDecisionV01`, and local profiles hold only derived negative gate
reasons. Static validation
extracts every complete backticked value used in a reason-code position,
requires membership, requires registry uniqueness and order, and rejects an
unreachable entry unless it is explicitly marked reserved. This registry has
no reserved entries.

Mandatory trigger ownership is exact:

| Validation group | Public reasons whose trigger is owned by the group |
|---:|---|
| 1 | `g2c_exact_type_invalid`, `g2c_scalar_invalid`, `g2c_sequence_invalid` |
| 2 | `g2c_identity_invalid`, `g2c_identity_mismatch`, `g2c_request_binding_mismatch`, `g2c_transaction_binding_mismatch`, `g2c_root_binding_mismatch`, `g2c_domain_binding_mismatch` |
| 3 | no additional reason; exercises the exact structural reasons owned by group 1 |
| 4 | no runtime reason; proves registry declaration, uniqueness, order, and reachability |
| 5 | `g2c_business_request_invalid`, `g2c_business_request_ref_invalid`, `g2c_route_context_invalid`, `g2c_semantic_proposal_invalid`, `g2c_structured_rationale_invalid`, `g2c_bsep_invalid`, `g2c_source_digest_mismatch` |
| 6 | `g2c_replay_binding_invalid` |
| 7 | `g2c_g2a_relation_invalid`, `g2c_g2a_present_inspection_invalid` |
| 8 | `g2c_g2b_binding_invalid`, `g2c_g2b_binding_state_derivation_mismatch`, `g2c_g2b_query_transaction_mismatch`, `g2c_g2b_shortcut_invalid`, `g2c_g2b_use_time_invalid` |
| 9 | `g2c_time_envelope_invalid`, `g2c_time_envelope_ref_identity_mismatch`, `g2c_local_mode_profile_invalid`, `g2c_local_mode_profile_set_invalid`, `g2c_mode_profile_set_identity_mismatch`, `g2c_policy_forbidden`, `g2c_scope_forbidden`, `g2c_risk_forbidden`, `g2c_privacy_forbidden`, `g2c_capability_unavailable`, `g2c_cost_invalid` |
| 10 | `g2c_source_context_invalid`, `g2c_source_context_structural_target_invalid`, `g2c_source_object_absent`, `g2c_source_validator_failed` |
| 11 | `g2c_invalid_source_no_proposal`, `g2c_fail_closed_return_to_root` |
| 12 | `g2c_noncanonical_mode`, `g2c_deterministic_feasible`, `g2c_sealed_replay_feasible`, `g2c_direct_informational_reuse_feasible`, `g2c_memory_informed_feasible`, `g2c_local_slm_feasible`, `g2c_cloud_llm_feasible`, `g2c_full_semantic_feasible`, `g2c_full_fractal_feasible` |
| 13 | `g2c_required_evidence_missing`, `g2c_action_shortcut_forbidden` |
| 14 | `g2c_feasibility_row_invalid`, `g2c_selection_invalid`, `g2c_selection_tie_break_applied` |
| 15 | `g2c_hard_block_present`, `g2c_user_input_required`, `g2c_no_safe_mode` |
| 16 | `g2c_proposal_rows_invalid`, `g2c_proposal_selected_row_mismatch`, `g2c_proposal_sources_valid` |
| 17 | `g2c_abi_profile_invalid`, `g2c_abi_reserved_payload_key`, `g2c_abi_artifact_identity_mismatch`, `g2c_abi_parent_lineage_mismatch`, `g2c_abi_bundle_validation_failed`, `g2c_route_decision_bypass_forbidden` |
| 18 | `g2c_transition_profile_invalid`, `g2c_transition_registry_identity_mismatch`, `g2c_transition_decision_invalid`, `g2c_transition_decision_identity_mismatch`, `g2c_transition_root_review_required`, `g2c_transition_route_accept_allowed`, `g2c_transition_scope_narrow_allowed`, `g2c_transition_reject_recorded`, `g2c_transition_blocked_recorded`, `g2c_transition_needs_user_recorded`, `g2c_transition_guard_invalid`, `g2c_transition_root_commit_required`, `g2c_proposal_transition_missing`, `g2c_proposal_transition_substituted`, `g2c_post_root_transition_missing`, `g2c_post_root_transition_substituted` |
| 19 | `g2c_root_input_invalid`, `g2c_root_result_invalid`, `g2c_root_mapping_invalid` |
| 20 | `g2c_review_action_invalid`, `g2c_terminal_review_mismatch`, `g2c_scope_narrowing_invalid`, `g2c_policy_snapshot_binding_mismatch`, `g2c_terminal_contribution_scope_mismatch`, `g2c_root_accept_projected`, `g2c_root_narrow_projected`, `g2c_root_reject_projected`, `g2c_root_blocked_projected`, `g2c_root_needs_user_projected`, `g2c_route_eligibility_invalid` |
| 21 | `g2c_source_object_substituted`, `g2c_abi_projection_substituted`, `g2c_transition_substituted` |
| 22 | no additional reason; reruns groups 1..21 through append-only Living and Conformance acts |

### 7.5 One Kernel ABI profile

The append-only profile is:

```text
profile_id: execution_mode_router_g2c_abi_profile_v01
profile_version: v0.1
abi_version: v1.0
artifact_types:
  - ExecutionModeProposal
  - RootExecutionModeDecision
  - ExecutionModeRouteEligibility
```

Existing ABI tuples remain an exact prefix. The three literals append to
`ARTIFACT_TYPES` and the same three enum values append to
`schemas/kernel_artifact_v01.schema.json`; no other schema key changes.
Every one of the three G2-C Kernel artifacts uses exact
`abi_version="v1.0"` and `schema_version="v0.1"`; neither value is inferred
from a caller, and both participate in the contextual artifact ID.

The current Kernel envelope reserves these names:

```text
abi_version
artifact_id
artifact_type
schema_version
transaction_id
owner_root_id
source_component
authority_class
lifecycle_state
payload
trace_refs
parent_refs
time_envelope
```

G2-C applies a stronger recursive pre-build scan: none of those keys may occur
at any mapping depth in a G2-C payload, including nested rows. The envelope is
the sole ABI source for transaction, owner Root, source component, authority,
lifecycle, traces, parents, and time. Complete G2-C dataclass plain data is not
placed directly in payload.

Projection matrix:

| Artifact | Authority | Lifecycle | Source | Exact parent refs |
|---|---|---|---|---|
| `ExecutionModeProposal` | `ADVISORY` | `VALIDATED` | `execution_mode_router_v01` | `()` |
| `RootExecutionModeDecision` | `ROOT_OWNED` | outcome-derived | `root_decision_v01` | proposal artifact only |
| `ExecutionModeRouteEligibility` | `ROOT_AUTHORIZED` | `ROOT_ACCEPTED` | `root_decision_v01` | decision artifact only |

Outcome-derived decision lifecycle is `ROOT_ACCEPTED` for ACCEPT/NARROW,
`ROOT_REJECTED` for REJECT, `BLOCKED_FAIL_CLOSED` for BLOCKED, and
`ROOT_REVIEWED` for NEEDS_USER.

#### 7.5.1 Exact ABI-safe payloads

Proposal payload order is exactly:

```text
proposal_id
source_input_id
request_id
domain_id
source_bsep_binding_id
source_bsep_packet_id
source_bsep_sha256
source_local_routing_snapshot_id
source_replay_binding_id
source_g2a_binding_id
source_g2b_binding_id
selected_mode
selected_safe_depth_rank
selected_local_mode_profile_id
selected_expected_cost_units
proposed_scope_ref
ordered_feasibility_row_ids
selected_feasibility_row_id
reason_codes
required_downstream_capability_ids
downstream_consumption_class
downstream_action_packet_required
root_review_required
authority_created
permission_created
action_commit_packet_created
receipt_created
topology_created
final_output_created
drs_write_created
real_world_effects_count
```

`ordered_feasibility_row_ids` is derived from the exact ten source rows. The
rows remain identity-bound in `ExecutionModeProposalV01` and are omitted from
payload because their nested plain forms contain reserved envelope names.

Decision payload order is exactly:

```text
decision_id
root_review_input_id
proposal_id
router_input_id
request_id
domain_id
outcome
accepted_mode
accepted_scope_ref
scope_narrowing_proof_id
downstream_consumption_class
downstream_action_packet_required
source_root_decision_id
source_root_decision_input_id
source_root_decision
source_root_reason_code
source_root_transition_decision_id
source_root_transition_decision
reason_codes
route_eligibility_candidate
authority_created
permission_created
action_commit_packet_created
receipt_created
topology_created
final_output_created
drs_write_created
real_world_effects_count
```

RouteEligibility payload order is exactly:

```text
request_id
domain_id
decision_id
accepted_mode
accepted_scope_ref
downstream_consumption_class
downstream_action_packet_required
abi_profile_id
transition_registry_id
root_route_transition_decision_id
topology_created
permission_created
action_commit_packet_created
final_output_created
real_world_effects_count
```

It contains no transaction or Root field; those are envelope-only. The fixed
creation values are false/false/false/false/zero. Only
`RUNTIME_TOPOLOGY_ELIGIBLE` may later be consumed by G2-D.
`SHORTCUT_RETURN_TO_ROOT` returns upward without topology.
`TERMINAL_NO_CONSUMPTION` creates no eligibility artifact.

#### 7.5.2 Contextual Kernel artifact identities

The generic ABI accepts textual IDs, but G2-C rebuilds each ID from the exact
`KernelArtifactV01` plain projection with `artifact_id` omitted:
`abi_version`, `artifact_type`, `schema_version`, `transaction_id`,
`owner_root_id`, `source_component`, `authority_class`,
`lifecycle_state`, exact ABI-safe payload, traces, parents, and exact
eight-field time envelope.

| Artifact | Domain | Prefix |
|---|---|---|
| proposal | `HEDGEHOG_EXECUTION_MODE_PROPOSAL_KERNEL_ARTIFACT_V01` | `emabi_proposal_v01:` |
| decision | `HEDGEHOG_EXECUTION_MODE_DECISION_KERNEL_ARTIFACT_V01` | `emabi_decision_v01:` |
| route eligibility | `HEDGEHOG_EXECUTION_MODE_ROUTE_ELIGIBILITY_KERNEL_ARTIFACT_V01` | `emabi_route_v01:` |

Identity is prefix plus
`domain_separated_sha256_hex_v01(domain=<exact>, payload=canonical_json_bytes_v01(<material>))`.
The contextual ABI validator rebuilds all three; a structurally valid
caller-selected ID is insufficient.

#### 7.5.3 Trace, parent, and bundle law

Proposal parents are `()`. Proposal traces are the unique lexical tuple of
business-request packet ID, BSEP binding ID, router input ID, local snapshot
ID, Replay binding ID, G2-A binding ID, G2-B binding ID, and proposal ID.

Decision parents are `(proposal_artifact.artifact_id,)`. Decision traces are
the unique lexical tuple of proposal artifact ID, proposal ID, review input ID,
source Root decision ID, source Root Transition decision ID, and decision ID.

RouteEligibility parents are `(decision_artifact.artifact_id,)`. Its traces
are the unique lexical tuple of decision artifact ID, decision ID, G2-C
Transition registry ID, and post-Root route Transition decision ID. BSEP
bindings, G2-C dataclasses, Root results, and Transition decisions are not
Kernel artifact parents.

The current `validate_kernel_artifact_bundle_v01` is mandatory:

```text
Stage A: (proposal_artifact,)
Stage B: (proposal_artifact, decision_artifact)
Stage C ACCEPT/NARROW:
  (proposal_artifact, decision_artifact, route_eligibility_artifact)
Stage C REJECT/BLOCKED/NEEDS_USER:
  (proposal_artifact, decision_artifact)
```

Unknown or non-artifact parent, self-parent, duplicate edge, transaction
mismatch, cycle, artifact-ID substitution, or reordered causal chain fails
closed.

#### 7.5.4 Complete contextual ABI profile

`validate_execution_mode_abi_profile_v01` receives proposal, router input,
source context, proposal artifact, proposal-to-Root Transition decision, review
input, G2-C decision, actual Root Kernel/Input/Result, decision artifact,
post-Root G2-C Transition decision, and optional RouteEligibility artifact. It
proves rebuilt artifact IDs, recursive payload safety, exact envelope
transaction/Root/time, traces, parents, all applicable bundle stages, both G2-C
Transition identities, review lineage, source Root result and source Root
Transition, outcome-dependent eligibility presence, and all zero-creation
claims. A supplied PASS report is never authority.

## 8. Router Input Contract

The public routing entrypoint requires both exact input and runtime context.
Structural validation proves shape and identity only. The first operational
step is `validate_execution_mode_router_input_against_sources_v01`, which reruns
the complete source family and all cross-bindings.

The canonical input excludes raw user text, provider output, secrets,
credentials, unvalidated dictionaries, caller authorization booleans,
provider-selected mode, permission or receipt as route authority, final output,
topology, nodes, edges, assignments, and callbacks.

```text
RAW_USER_REQUEST_TO_G2B_QUERY_CROSS_BINDING_IMPLEMENTED=false
OUTER_TRANSACTION_TO_G2B_SUBQUERY_BINDING_IMPLEMENTED=false
```

### 8.1 Business-request and BSEP source binding

The BSEP builder directly calls, in this order:

1. `validate_business_request_context_packet`;
2. `validate_orchestrator_route_context_packet`;
3. `validate_orchestrator_semantic_reasoning_proposal`;
4. `validate_orchestrator_structured_rationale`;
5. `validate_bounded_semantic_evidence_packet` with actual route context,
   actual proposal, and the freshly derived rationale result.

Exact current source builders and their keyword surfaces are frozen as follows:

| Current builder | Exact source arguments used by the G2-C fixture profile |
|---|---|
| `build_business_request_context_packet` | `packet_id`, `created_by`, `source_refs`, `domain`, `request_id`, `business_subject`, `requested_action`, `explicit_blockers`, `user_visible_summary`, `forbidden_authority_fields`, `forbidden_action_fields` |
| `build_orchestrator_route_context_packet` | `packet_id`, `created_by`, `source_refs`, `domain`, `allowed_routes`, `required_guards`, `selected_vector_ids`, `route_validation_expectations`, `orchestrator_is_root`, `creates_action_commit_packet`, `calls_connectors` |
| `build_orchestrator_structured_rationale` | `observed_semantics`, `route_selection_reason`, `rejected_routes`, `required_guards_reasoning`, `selected_vector_reasoning`, `uncertainty_notes`, `authority_boundary`, `root_review_required` |
| `build_bounded_semantic_evidence_packet` | `packet_id`, `created_by`, `source_refs`, `domain`, `source_role`, `target_role`, `source_route_id`, `source_proposal_id`, `source_context_packet_id`, `source_structured_rationale_ref`, `observed_semantic_facts`, `missing_evidence`, `uncertainty_notes`, `risk_boundary_notes`, `rejected_action_routes`, `required_approvals_or_conditions`, `authority_boundary_notes`, `selected_vector_ids`, `required_guards` |

The orchestrator semantic proposal is the actual exact plain provider/runtime
proposal dict; there is no current canonical proposal dataclass builder. It is
accepted only when
`validate_orchestrator_semantic_reasoning_proposal(payload) -> ()`.
The remaining exact current validation signatures are:

```python
def validate_business_request_context_packet(packet: Mapping[str, Any]) -> dict[str, Any]
def validate_orchestrator_route_context_packet(packet: Mapping[str, Any]) -> dict[str, Any]
def validate_orchestrator_structured_rationale(rationale: Any) -> dict[str, Any]
def validate_bounded_semantic_evidence_packet(packet: Mapping[str, Any], *, route_context_packet: Mapping[str, Any] | None = None, orchestrator_proposal: Mapping[str, Any] | None = None, structured_rationale_validation: Mapping[str, Any] | None = None) -> dict[str, Any]
```

All first five source values require exact plain `dict`, not a subclass. The
semantic proposal validator must return `()`. The other four validators must
return accepted results with empty reasons. Exact canonical bytes for these
current dict contracts use `canonical_json_bytes_v01` after recursive plain-data
normalization that rejects non-string keys, unsupported values, cycles,
surrogates, non-finite floats, and duplicate keys in materialized mappings.
Finite JSON floats accepted by the complete current source validator remain in
the exact source bytes and digests; they never become G2-C typed scalar fields.

The additional local G2-C cross-validation is exact:

- the business request is the exact plain output of
  `build_business_request_context_packet`, its current validator is accepted
  with empty reasons, request and domain match, its packet ID is nonempty, all
  authority/action/final/effect fields are safe, and it contains no raw secret
  or unbounded request dump;
- the exact Section 6.2 business source-reference record occurs once in
  `route_context.source_refs` and once in `bsep_packet.source_refs`, with the
  exact packet ID, request ID, and domain and no duplicate;
- route allowed routes equal `(bsep_packet.source_route_id,)`; route and BSEP
  vector and guard tuples are equal; route expectations are exactly
  `root_review_required=true` and
  `selected_only_allowed_vectors=true`; orchestrator-is-Root, packet creation,
  and connector calls are false;
- the orchestrator proposal key set equals
  `ORCHESTRATOR_SEMANTIC_REASONING_REQUIRED_FIELDS`; its current validator
  returns `()`; proposal and route IDs, vectors, and guards cross-bind;
  `needs_review` and `root_review_required` are true; `confidence` has exact
  type `int` or `float`, is not `bool`, is finite, and lies in `0.0..1.0`;
  every current truth, authority, permission, final-output, connector-command,
  DRS-write, provider-owned-execution-representation, and Root-bypass claim is
  false; every required semantic field passes its current bounded validator;
- the structured rationale is the exact plain builder output, validates with
  empty reasons, requires Root review, and keeps orchestrator-is-Root, packet,
  connector, truth, authority, permission, final-output, DRS-write, and bypass
  claims false;
- the BSEP validates with empty reasons using the newly derived rationale
  validation result, and its request, route, proposal, rationale, vectors,
  guards, roles, domain, schema, creator, authority boundaries, and zero-effect
  fields all cross-bind.

Matching one ID, one digest, or a copied `accepted=true` result is
insufficient. All failures use the existing source-binding G2-C reasons; this
cross-validation adds no public reason.

The structured rationale has no native identity. G2-C computes its canonical
digest after the current validator passes and requires the BSEP reference to be
exactly `structured_rationale_v01:` followed by that lowercase digest. This is
an explicit local projection and is never represented as a source-native ID.

### 8.2 Replay source binding

Bound Replay uses the actual `SealedReplayEvidenceV01`, source and reconstructed
`SealedPackageManifestV01`, source and reconstructed
`DomainEvidenceProjectionV01`, both safe-byte tuples,
`ExternalAnchorPublicationV01`, `AnchoredPackageVerificationV01`, and supplied
anchor ID. It calls `validate_sealed_replay_evidence_v01` with every exact
argument. PASS, source/package/scope/integrity identities, and all zero
operation counters are derived. Copied strings cannot create a binding.

The exact source validator call is:

```python
def validate_sealed_replay_evidence_v01(result: object, *, source_manifest: SealedPackageManifestV01, source_domain_projection: DomainEvidenceProjectionV01, source_safe_file_contents: tuple[bytes, ...], anchor_publication: ExternalAnchorPublicationV01, anchored_verification: AnchoredPackageVerificationV01, supplied_anchor_publication_id: str, reconstructed_manifest: SealedPackageManifestV01, reconstructed_domain_projection: DomainEvidenceProjectionV01, reconstructed_safe_file_contents: tuple[bytes, ...]) -> tuple[str, ...]
```

Its canonical digest uses
`sealed_replay_evidence_to_plain_dict_v01` with the same complete argument set.
Source and reconstructed manifests are independently validated through current
package/anchor/replay validators before the local binding identity is built.

### 8.3 Local mode profiles and snapshot

Only creator `OWNING_LOCAL_ROOT_ROUTING_SNAPSHOT_V01` may build the local
snapshot. Every profile cross-binds request, transaction, Root, domain, policy,
capability, and cost model. Mode-specific policy/scope/risk/privacy results are
not replaced by one global allow flag.

`request_class`, `scope_class`, and `risk_class` are identity-bound Root-local
audit and policy-lineage labels. G2-C does not interpret their spelling and
they do not independently make a mode feasible. Routing consumes only each
profile's policy, scope, risk, privacy, capability, and cost results.

`memory_informed` requires G2-B state `RESOLUTION_CONTEXT_BOUND` or
`DIRECT_REUSE_BOUND`, `context_available=true`, its own declared AVAILABLE
semantic capability, and all four profile gates. Memory presence without
context availability is insufficient and never creates a direct shortcut.
G2-B context is advisory evidence, not compute capability. Required capability
states are explicit for deterministic, memory, local model, cloud model, full
semantic, and full fractal. Replay and direct reuse require no compute
capability.

## 9. Per-Mode Feasibility Matrix

Feasibility is exact and produces all ten rows.

| Mode | Rank | Required validated facts | G2-A relation | G2-B / Replay law | Downstream compute | Exact no-fallback blocker |
|---|---:|---|---|---|---|---|
| `deterministic` | 10 | local profile allows policy/scope/risk/privacy and declared deterministic capability is AVAILABLE | any coherent relation; existing attempt must be eligible | neither creates authority | `NONE` | capability/policy failure |
| `sealed_replay` | 20 | bound valid Replay and local profile allows all four gates | non-action or fresh action only; cannot revive existing invalid packet | `SEALED_REPLAY_BOUND` | `NONE` | absent/invalid Replay |
| `direct_informational_reuse` | 30 | non-action, local profile allows all gates, complete current direct chain | `NOT_APPLICABLE` only | `DIRECT_REUSE_BOUND` and exact use-time validation | `NONE` | any stale/incompatible/quarantine/deadend/action fact |
| `memory_informed` | 40 | local profile allows all gates and dedicated memory capability AVAILABLE | coherent relation; existing attempt eligibility only when work continues that packet | context may be `RESOLUTION_CONTEXT_BOUND`; no shortcut | `MEMORY_INFORMED` | memory alone or missing capability |
| `local_slm` | 50 | local profile allows all gates and local capability AVAILABLE | coherent relation | memory only advisory | `LOCAL_SLM` | missing/prohibited capability |
| `cloud_llm` | 50 | local profile allows policy/scope/risk/privacy and cloud capability AVAILABLE | coherent relation | provider cannot select mode | `CLOUD_LLM` | privacy/policy/capability failure |
| `full_semantic` | 60 | local profile allows all gates and full semantic capability AVAILABLE | coherent relation | no child execution implied | `FULL_SEMANTIC` | unavailable required semantic depth |
| `full_fractal` | 70 | local profile allows all four gates and declared future full-fractal capability is AVAILABLE | coherent relation | all required source bindings validate; G2-D is not implemented here | `FULL_FRACTAL` | absent capability; no fallback |
| `blocked` | none | valid input with hard blocker or no safe executable mode | invalid existing packet can select this terminal | evidence remains non-authority | `TERMINAL` | terminal, no fallback |
| `needs_user` | none | valid input with explicit user-resolvable missing choice/consent/confirmation/clarification and no hard blocker | no packet created | not a generic error | `TERMINAL` | terminal, no fallback |

Classification labels add no hidden row predicate. In particular,
`BOUNDED_FRACTAL_REQUIRED` is fixture metadata only. Full fractal is selected
only when its exact profile and source bindings pass and every feasible
shallower mode loses under minimum-safe-depth selection.

Global terminal law is exact:

- with `hard_block_state=BLOCKED`, every executable row is INFEASIBLE and
  includes `g2c_hard_block_present`; blocked is TERMINAL_SELECTED with exactly
  `(g2c_hard_block_present,)`; needs-user is TERMINAL_NOT_SELECTED;
- with hard block clear and `required_user_input_state=MISSING_RESOLVABLE`,
  every executable row is INFEASIBLE, includes `g2c_user_input_required`, and
  includes `g2c_required_evidence_missing` in `missing_evidence_codes`;
  needs-user is TERMINAL_SELECTED with exactly
  `(g2c_user_input_required,)`; blocked is TERMINAL_NOT_SELECTED;
- with hard block clear and user input complete, executable feasibility is
  evaluated normally; if no executable mode is feasible, blocked is selected
  with exactly `(g2c_no_safe_mode,)`.

Hard block wins when both global conditions exist. Source-invalid or malformed
input returns a fail-closed report and no proposal. No executable row remains
FEASIBLE while a hard block or unresolved global user-input requirement exists.

Per-mode action relation:

| Mode | NON_ACTION | ACTION / new | Existing packet attempt |
|---|---|---|---|
| deterministic | allowed if feasible | `NEW_ACTION_NO_PACKET`; later packet gate required | present inspection must pass |
| sealed_replay | allowed if exact Replay | allowed only as non-executing evidence; later packet gate required | cannot revive invalid packet |
| direct_informational_reuse | allowed | forbidden | forbidden |
| memory_informed | allowed | bounded reasoning allowed; later packet gate required | present inspection required if continuing packet |
| local_slm | allowed | bounded reasoning allowed; later packet gate required | present inspection required if continuing packet |
| cloud_llm | allowed | bounded reasoning allowed; later packet gate required | present inspection required if continuing packet |
| full_semantic | allowed | bounded reasoning allowed; later packet gate required | present inspection required if continuing packet |
| full_fractal | allowed | declaration-only route; later packet gate required | present inspection required if continuing packet |
| blocked | terminal | terminal | terminal for invalid packet |
| needs_user | terminal | terminal | terminal only for resolvable evidence gap |

## 10. Feasibility-Before-Cost and Selection

Stage 1 determines executable feasibility from source validation, policy,
scope, evidence, risk, privacy, freshness, capability, G2-A, and G2-B. Stage 2
chooses minimum safe depth.

Safe ranks are exactly:

```text
deterministic=10
sealed_replay=20
direct_informational_reuse=30
memory_informed=40
local_slm=50
cloud_llm=50
full_semantic=60
full_fractal=70
blocked=None
needs_user=None
```

The exact executable selection key is:

```text
(safe_depth_rank, cost_units, canonical_mode_index)
```

Cost is used only after feasibility and only has meaningful comparative effect
inside a shared depth. It cannot create feasibility, grant authority, override
safe depth, or hide missing capability. Missing, malformed, foreign-profile, or
overflowing cost fails closed. An independently feasible shallower mode is a
selection, not a downgrade. No silent downgrade exists.

Feasibility-row derivation is exact:

- `required_evidence_refs` has the universal BSEP/snapshot prefix, the local
  profile for executable rows, and only the concrete source/capability IDs in
  the per-mode table; it contains no `None` or placeholder and adds packet
  evidence only for `EXISTING_PACKET_ATTEMPT`;
- `satisfied_evidence_refs` is the order-preserving subset whose actual source,
  binding, profile, and capability state validates and contains no foreign ID;
- `missing_evidence_codes` contains only
  `g2c_required_evidence_missing` and/or `g2c_capability_unavailable`, in public
  registry order; policy, scope, risk, privacy, packet-shortcut, hard-block,
  and terminal-selection reasons never appear there;
- a FEASIBLE executable row has exactly its one mode-positive feasibility
  reason; an INFEASIBLE row has no positive reason and has the nonempty,
  registry-ordered deduplicated union of local, source/evidence,
  action-shortcut, and global reasons;
- selected blocked has exactly `g2c_hard_block_present` or `g2c_no_safe_mode`;
  selected needs-user has exactly `g2c_user_input_required`; nonselected
  terminal rows have empty reasons; terminal profile, rank, capability, and
  cost are `None` and downstream compute is `TERMINAL`.

No fixture supplies a derived row reason.

## 11. Router Proposal Contract

Every valid input yields exactly ten feasibility rows in canonical order and
one selected row ID. No row can be removed, duplicated, repartitioned, or
substituted. Structural validation and contextual reconstruction both require
complete equality.

Downstream class mapping is exact:

- deterministic, sealed replay, and direct informational reuse:
  `SHORTCUT_RETURN_TO_ROOT`;
- memory-informed, local model, cloud model, full semantic, and full fractal:
  `RUNTIME_TOPOLOGY_ELIGIBLE`;
- blocked and needs-user: `TERMINAL_NO_CONSUMPTION`.

Proposal `reason_codes` always contains `g2c_proposal_sources_valid`. It also
contains `g2c_selection_tie_break_applied` only when at least two feasible
executable modes share the selected minimum rank and at least two of those
share the minimum cost, so canonical index is actually required. Unequal-cost
comparison at a shared rank emits no tie-break reason.

`required_downstream_capability_ids` is the selected capability singleton for
deterministic, memory-informed, local-SLM, cloud-LLM, full-semantic, and
full-fractal modes; it is empty for replay, direct reuse, blocked, and
needs-user.

`downstream_action_packet_required` is true exactly for an executable selected
row with local `action_class=ACTION` and
`action_packet_relation=NEW_ACTION_NO_PACKET`. It is false for non-action,
existing-packet attempts, blocked, and needs-user. This declares a later
Root-owned effect gate; no packet or permission is created.

The proposal contains no raw text, provider output, secret, callback, client,
connector, effect handle, topology node/edge, assignment, permission, packet,
receipt, DRS write, or final output.

The operational result law is exact:

- valid source-bound input: proposal present and report PASS;
- malformed input, missing source, source mismatch, or source validator
  failure: proposal `None`, report FAIL_CLOSED, return-to-Root true;
- blocked/needs-user proposals exist only for structurally and contextually
  valid facts.

## 12. Root Review Contract

Review input is built only from actual validated proposal, router input, source
context, validated proposal Kernel artifact, validated proposal-to-Root
`RETURN_TO_ROOT` Transition decision, owning Root, explicit review action, and
local scope material. It has no caller-selected mode and cannot exist before
the pre-Root Transition.

Review matrix:

| Proposal | Review action | Accepted mode/scope | Source Root result | Eligibility candidate |
|---|---|---|---|---|
| executable | `ACCEPT` | same mode, proposed scope | `ACCEPT`, `validated_candidate_accepted` | true, non-authoritative |
| executable | `NARROW` | same mode, one allowlisted narrower scope | `ACCEPT`, `validated_candidate_accepted` | true, non-authoritative |
| executable | `REJECT` | none | `REJECT`, `policy_rejected_candidate` | false |
| blocked | `TERMINAL_FROM_PROPOSAL` | none | `BLOCKED_FAIL_CLOSED`, `hard_policy_violation` | false |
| needs-user | `TERMINAL_FROM_PROPOSAL` | none | `NEEDS_USER`, `user_permission_missing` | false |

Illegal combinations, mode substitution, broader scope, non-allowlisted scope,
forged narrowing, Root substitution, stale context, source result mismatch, or
Transition mismatch fail closed.

### 12.1 Exact scope-narrowing identity

Narrowing never changes mode. The accepted scope must occur exactly once in the
snapshot's `permitted_narrower_scope_refs`. The proof is rebuilt under
`HEDGEHOG_EXECUTION_MODE_SCOPE_NARROWING_V01`, prefix `emnarrow_v01:`, from:

```text
request_id
transaction_id
owning_root_id
proposal_id
proposed_scope_ref
accepted_scope_ref
policy_snapshot_id
evaluation_time_epoch_seconds
narrowing_basis_refs
```

`narrowing_basis_refs` is a nonempty unique lexical tuple. A free proof string
is not accepted.

### 12.2 Existing SemanticWork and Root Decision source profile

The profile uses actual current types and builders:

- `SemanticWorkRequestV01` via `build_semantic_work_request_v01`;
- `NormalizedClaimV01` via `build_normalized_claim_v01`;
- `ActorContributionV01` via `build_actor_contribution_v01`;
- `RootReviewPacketV01` via
  `build_root_review_packet_from_contributions_v01`;
- exact default trust profiles via
  `build_default_component_trust_profiles_v01`;
- `RootDecisionKernelV01` via `build_root_decision_kernel_v01`;
- `RootDecisionInputV01` via `build_root_decision_input_v01`;
- `RootDecisionResultV01` via `decide_root_v01` and
  `validate_root_decision_result_v01`.

The SemanticWork request uses exact request/transaction/Root identities,
absence sentinel `g2c:runtime_topology:not_created_before_root_review:v01`,
bounded context refs equal the G2-C source identities, permitted actor
`execution_mode_router_v01`, contribution mode `DETERMINISTIC`, requested
subject `execution_mode_route`, evidence classes `BSEP` and
`EXECUTION_MODE_FEASIBILITY`, and forbidden claims `AUTHORITY`, `PERMISSION`,
`EFFECT`, `TOPOLOGY`, and `FINAL_OUTPUT`.

The normalized claim ID is the proposal ID, predicate is `selected_mode`, value
is the canonical selected mode, source role is `deterministic_runtime`, source
mode is `DETERMINISTIC`, authority is current fixed `NONE`, and evidence refs
are exact binding IDs. The contribution uses actor ID
`execution_mode_router_v01`, role `deterministic_runtime`, exact BSEP binding,
the exact scope law below, no forbidden claims, and current default
`deterministic_runtime` trust profile. All current validators pass before Root
input is built.

For an executable proposal, contribution scope equals
`proposal.proposed_scope_ref == local_routing_snapshot.scope_ref` before
optional narrowing. For `blocked` or `needs_user`,
`proposal.proposed_scope_ref is None`, while contribution scope equals the
local snapshot scope solely as bounded Root-review context. That terminal
scope is not an accepted route; terminal decision scope remains `None` and no
RouteEligibility is created.

No current builder argument is implicit. The exact profile arguments are:

| Current builder | Exact G2-C argument projection |
|---|---|
| `build_semantic_work_request_v01` | `request_id=router_input.request_id`; `transaction_id=router_input.transaction_id`; `target_root_id=router_input.owning_root_id`; exact absence sentinel; `bounded_context_refs=(business_request_packet_id, bsep_binding_id, router_input_id, proposal_id)`; `permitted_actor_ids=("execution_mode_router_v01",)`; `permitted_contribution_modes=("DETERMINISTIC",)`; `requested_subjects=("execution_mode_route",)`; `required_evidence_classes=("BSEP", "EXECUTION_MODE_FEASIBILITY")`; `forbidden_claims=("AUTHORITY", "PERMISSION", "EFFECT", "TOPOLOGY", "FINAL_OUTPUT")` |
| `build_evidence_binding_v01` for BSEP | deterministic evidence ID; `evidence_ref=bsep_binding_id`; `evidence_class="BSEP"`; `source_component_id="execution_mode_router_v01"`; `provenance_ref=source_family_sha256`; `evidence_state="PRESENT"` |
| `build_evidence_binding_v01` for feasibility | deterministic evidence ID; `evidence_ref=selected_feasibility_row_id`; `evidence_class="EXECUTION_MODE_FEASIBILITY"`; same component; `provenance_ref=proposal_id`; `evidence_state="PRESENT"` |
| `build_normalized_claim_v01` | `claim_id=proposal_id`; `subject="execution_mode_route"`; `predicate="selected_mode"`; `object_or_value=selected_mode`; snapshot time reference; `provenance_refs=(bsep_binding_id, router_input_id)`; evidence refs equal the two bindings; `confidence_micros=1000000`; role/mode as above |
| `build_actor_contribution_v01` | deterministic contribution ID; exact request; actor ID/role `execution_mode_router_v01`/`deterministic_runtime`; mode `DETERMINISTIC`; `bsep_projection_ref=bsep_binding_id`; executable proposal scope or terminal local-snapshot review scope under the exact law above; exact bounded refs; one claim; two evidence bindings; empty constraint and uncertainty tuples; `requested_validators=("execution_mode_proposal_sources_v01",)`; empty forbidden-observed tuple |
| `build_root_review_packet_from_contributions_v01` | exact request, one exact contribution, and the internally built and validated complete tuple from `build_default_component_trust_profiles_v01()`; caller trust profiles are forbidden |

All G2-C Root source-support identities use common domain
`HEDGEHOG_EXECUTION_MODE_ROOT_SOURCE_SUPPORT_V01`. Every material begins, in
order, with `kind`, `request_id`, `transaction_id`, `owning_root_id`,
`domain_id`, `proposal_id`, `router_input_id`, `proposal_artifact_id`, and
`proposal_transition_decision_id`. No support identity is caller supplied.

| Support object | Prefix | Kind | Exact kind-specific material |
|---|---|---|---|
| BSEP evidence | `emrootev_v01:` | `BSEP_EVIDENCE` | `bsep_binding_id`, `source_family_sha256` |
| feasibility evidence | `emrootev_v01:` | `FEASIBILITY_EVIDENCE` | `selected_feasibility_row_id`, selected mode, complete ordered feasibility-row ID tuple |
| actor contribution | `emrootcontrib_v01:` | `ACTOR_CONTRIBUTION` | BSEP evidence ID, feasibility evidence ID, exact contribution scope, selected mode |
| Post-V&V bundle | `emrootpostvv_v01:` | `POST_VV_BUNDLE` | both evidence IDs, contribution ID, review action, validated-candidate tuple, rejected-candidate tuple |
| GT advisory | `emrootgt_v01:` | `GT_ADVISORY` | contribution ID, review action, candidate tuple, selected candidate ID, ordered score-micros tuple, exact current GT Transition fields |
| Root-local review context | `emrootctx_v01:` | `ROOT_LOCAL_CONTEXT` | `policy_snapshot_id`, `time_envelope_ref`, proposed scope, accepted scope, scope-narrowing proof ID, narrowing basis refs |

Each identity is its prefix plus the domain-separated SHA-256 of its exact
named material. `post_vv_bundle.bundle_id`, `gt_advisory.advisory_id`,
`root_local_context_id`, both evidence IDs, and contribution ID are rebuilt
from these laws. They are local support projections, not source-native IDs.

Cross-bindings are exact:

- `policy_state.policy_id == local_routing_snapshot.policy_snapshot_id`;
- `temporal_state.time_envelope_ref == local_routing_snapshot.time_envelope_ref`;
- `conflict_state.conflict_set_ids == root_review_packet.conflict_set_ids == ()`;
- `permission_state.permission_ref is None` except the exact current
  NEEDS_USER shape, which also uses `None` under this profile;
- the embedded source Root Transition is the actual validated default-Registry
  `RETURN_TO_ROOT` decision.

The seven exact Root input object key sets are:

```text
post_vv_bundle:
  bundle_id
  hard_failure_reasons
  post_vv_passed
  provided_evidence_refs
  rejected_candidate_ids
  required_evidence_refs
  validated_candidate_ids

gt_advisory:
  actor_role
  advisory_id
  advisory_only
  attempted_effect
  candidate_ids
  creates_final_output
  requests_effect
  score_micros_by_candidate
  selected_candidate_id
  source_artifact_type
  source_lifecycle_state
  target_artifact_type

policy_state:
  allow_accept
  conflict_policy
  hard_policy_passed
  identity_passed
  no_candidate_policy
  policy_id
  scope_passed

permission_state:
  permission_ref
  permission_required
  permission_scope_valid
  user_permission_present

temporal_state:
  expired
  not_before_satisfied
  temporal_valid
  time_envelope_ref

conflict_state:
  conflict_set_ids
  material_unresolved_conflict

prior_root_state:
  prior_decision
  prior_decision_id
  prior_selected_candidate_id
```

Exact values common to every case are: Post-V&V pass true, no hard failures,
provided and required refs equal the two bound evidence refs, proposal ID as the
only validated candidate, no rejected candidates; GT advisory ID derived from
proposal, advisory-only true, proposal as its only candidate and score key,
score `1000000`, no final output or effect request, and exact current GT
transition fields; policy identity/scope true, conflict policy `REJECT`,
no-candidate policy `REJECT`; permission-scope true; temporal valid true,
expired false, not-before true; conflict IDs are empty and material conflict is
false; all prior values `None`.

The exact current one-claim profile has one normalized claim whose claim ID is
the G2-C proposal ID, two PRESENT evidence bindings, and no contradictory
claim. The current SemanticWork builder therefore produces
`root_review_packet.conflict_set_ids == ()` and
`root_review_packet.missing_evidence_refs == ()`. Every Root input copies that
empty conflict tuple, and every successful Root result reports an empty
conflict tuple. The BSEP remains bound through bounded context, evidence,
provenance, proposal identity, and G2-C source/ABI lineage; its packet ID is not
a SemanticWork ConflictSet ID.

A forged conflict tuple containing `bsep_binding.source_packet_id` fails before
Root decision creation with source reason
`root_decision_conflict_state_invalid`. The contextual G2-C report uses
`reason_codes=(g2c_root_input_invalid,)` and records that source-owned reason
only in `source_reason_codes`.

Outcome deltas are exact: REJECT sets only `allow_accept=false`; BLOCKED sets
only `hard_policy_passed=false`; NEEDS_USER sets `permission_required=true`,
`user_permission_present=false`, and `permission_ref=None`. ACCEPT/NARROW use
`allow_accept=true`, hard policy true, and permission not required. The GT input
selected candidate remains proposal ID for all five source-result cases; the
existing Root result clears it for non-ACCEPT outcomes according to current
law.

The GT transition fields are exactly `GTAdvisoryReport`, `VALIDATED`, `gt`,
`CREATE_ROOT_DECISION`, and `RootDecision`; it is advisory-only, creates no
final output, and requests no effect. ACCEPT/NARROW select proposal ID. REJECT
sets `allow_accept=false`. BLOCKED sets `hard_policy_passed=false` and therefore
uses current first exact hard reason `hard_policy_violation`. NEEDS_USER sets
permission required, user permission absent, and scope valid. All other fields
are exact coherent safe values. Every current builder argument is supplied;
source result is validated and has `root_commit_created=true`, no permission,
no final output, and no effect.

`RootExecutionModeDecisionV01` is only a projection of this source result. No
independent decision engine exists.

The mandatory read-only source-contract probe passed using the actual
current public SemanticWork, trust-profile, and Root builders and validators.
It observed empty packet conflicts and missing evidence, the sole proposal claim,
source ACCEPT/REJECT/BLOCKED_FAIL_CLOSED/NEEDS_USER with Root commit, NARROW as
the same ACCEPT result plus separate G2-C narrowing proof, and exact rejection
of the forged BSEP conflict. Provider, network, connector, packet, receipt,
write, topology, FinalOutput, and effect counters remain zero.

### 12.3 Structural and contextual validation

Structural validators check exact type, fields, enums, identity, immutable
shape, order, and fixed non-authority values. They do not claim to validate
absent source objects.

The SourceContext structural validator checks only exact
`ExecutionModeSourceContextV01` type, exact nested runtime source types,
presence/absence family geometry, absence of partial Root, Replay, or G2-A
families, and absence of provider/client/effect objects. It has no local
snapshot or router input and therefore does not compare G2-A evaluation time
to snapshot epoch, G2-B use time to snapshot epoch, query ID to transaction,
request/domain/Root identities, or source digests to serialized bindings.
Those cross-bindings belong only to
`validate_execution_mode_router_input_against_sources_v01`, which receives
both router input and SourceContext.

Contextual validators rerun source validation. Proposal validation reruns input,
all ten feasibility rows, selection, nested identities, and exact row equality.
Root review validation reruns proposal/context, proposal artifact, pre-Root
Transition, and narrowing. Root decision validation additionally requires the
actual Root Kernel/Input/Result and distinguishes its embedded default-Registry
Transition from both G2-C profile Transitions. Eligibility validation requires
the post-Root G2-C Transition. A valid identity alone is never sufficient for
ABI projection, transition evaluation, eligibility, or future topology
consumption.

### 12.4 Exact operation order

1. Validate source context structurally.
2. Validate router input against actual sources.
3. Evaluate all ten feasibility rows.
4. Select the exact row.
5. Build and contextually validate the proposal.
6. Project and validate the proposal Kernel artifact.
7. Validate Stage-A bundle.
8. Evaluate proposal-to-Root `RETURN_TO_ROOT` Transition.
9. Build and contextually validate Root review input.
10. Build and validate the actual existing Root Decision source family.
11. Project and contextually validate the G2-C Root decision.
12. Project and validate the decision Kernel artifact.
13. Validate Stage-B bundle.
14. Evaluate the post-Root G2-C Transition.
15. For ACCEPT/NARROW only, project and validate RouteEligibility.
16. Validate the applicable Stage-C bundle.
17. Validate the complete G2-C ABI/Transition/Root profile.

No Root review input exists until step 8 has passed. No G2-C Root decision
exists until step 10 has passed. No decision Kernel artifact exists until step
11 has passed. No post-Root G2-C Transition exists until steps 11 through 13
have passed. No RouteEligibility exists until step 14 has passed. No complete
profile PASS exists until step 17 has passed. No topology is created by any
G2-C step.

## 13. G2-A Binding

G2-A remains read-only. Exact relation law:

- NON_ACTION requires `NOT_APPLICABLE` plus G2-A `NO_PACKET`;
- new action intent requires `NEW_ACTION_NO_PACKET` plus G2-A `NO_PACKET`;
- existing packet continuation requires `EXISTING_PACKET_ATTEMPT` plus
  `PRESENT_INSPECTION_BOUND`.

A new action request may select safe reasoning or compute without an existing
packet. Its proposal declares that a later Root-owned packet gate is required
before effect. G2-C creates no packet, permission, corridor step, effect handle,
receipt, completed action, or effect.

The serialized `NO_PACKET` values are exactly the complete field matrix in
Section 7.2.3. Contextual validation additionally proves that evaluation time,
source, and context ID equal the local snapshot epoch, creator, and snapshot
ID. No source inspection, registry, packet, corridor, step, logical-time
bridge, dependency observation, or ActionPacket Transition profile is present.

For present inspection, source context carries actual
`ActionPacketPresentEligibilityInspectionV01`,
`ActionCommitPacketRegistryV02`, packet ID,
`ContractFulfillmentCorridorV01`, `CorridorStepV01`, exact dependency
observations, `LogicalTimeBridgeV01`, evaluation time/source/context, and
`ActionPacketTransitionRegistryProfileV01`.

The binding builder calls
`validate_action_packet_present_eligibility_inspection_v01` with every exact
argument. Its local source SHA-256 is over the actual inspection's complete
declared field projection, including recursively projected
`ActionPacketLifecycleStateV01`. It derives lifecycle, provenance, event and
attempt counts, disposition, reservation owner, terminal receipt, executable
status, retry status, source reasons, and both history hashes.

The inspection and registry do not expose a native G2-C request, transaction,
or domain field. Those three values are explicit owning-Root local
cross-bindings, while packet and nested Root ownership must match every source
field that actually exists. The document does not relabel local values as
source-native evidence.

The exact current source signatures are:

```python
def inspect_action_packet_present_eligibility_v01(registry: object, *, packet_id: object, corridor: object, corridor_step: object, current_dependency_observations: object, logical_time_bridge: object, evaluation_time: object, evaluation_time_source: object, evaluation_context_id: object, action_packet_transition_registry_profile: object | None = None) -> ActionPacketPresentEligibilityInspectionV01
def validate_action_packet_present_eligibility_inspection_v01(report: object, registry: object, *, packet_id: object, corridor: object, corridor_step: object, current_dependency_observations: object, logical_time_bridge: object, evaluation_time: object, evaluation_time_source: object, evaluation_context_id: object, action_packet_transition_registry_profile: object | None = None) -> tuple[bool, tuple[str, ...]]
```

Expiry, kill, revoke, supersession, stale dependency, consumed/uncertain
disposition, corridor mismatch, or invalid current eligibility blocks the
packet-dependent attempt. Historical success cannot revive it. This is a fence
against packet revival, not a prohibition on fresh unrelated reasoning.

## 14. G2-B Binding

G2-B remains read-only. The exact nested source family uses current:

- `SemanticAddressV01` and `validate_semantic_address_v01`;
- `DRSTemporalQueryV01` and `validate_drs_temporal_query_v01`;
- `QueryEvaluationStateV01` and `validate_query_evaluation_state_v01`;
- `ResolutionCandidateV01` and `validate_resolution_candidate_v01`;
- `RetrievalPlanV01` and `validate_retrieval_plan_v01`;
- optional `MemoryDescentResultV01` and its validator;
- `RootShortcutAuthorizationProjectionV01` and its validator;
- `ReuseCertificateV01` and its validator;
- `LegacyDRSProjectionV01` and `validate_legacy_drs_projection_v01`;
- `DRSResolutionReportV01` and `validate_drs_resolution_report_v01`;
- actual Root Kernel/Input/Result and
  `validate_existing_root_shortcut_decision_v01` for direct reuse.

Conditional presence:

| Binding state | Report | compatibility tuple | use time | Root triple | Direct eligible |
|---|---|---|---|---|---:|
| `NOT_APPLICABLE` | absent | empty | absent | absent | false |
| `RESOLUTION_CONTEXT_BOUND` | complete valid report | exactly report `source_projections` | exact epoch | all absent | false |
| `DIRECT_REUSE_BOUND` | complete valid report | exactly report `source_projections` | exact epoch | all present | true |

`NOT_APPLICABLE` has every source ID/SHA and use/Root field `None`, every source
tuple empty, freshness and lineage `NOT_APPLICABLE`, no quarantine/deadend,
`context_available=false`, direct eligibility false, empty source reasons,
unchanged persistent records, false creation flags, and zero effects.

Context-bound reports use exact query mode `MEMORY_CONTEXT_ONLY`, reuse intent
`CONTEXT`, and requested classes `(CONTEXT_ONLY,)`. They require no eligible or
ranked candidate, no selection, no shortcut/certificate, no Root triple, and a
nonempty `context_only_record_ids` tuple. They derive
`context_available=true`, direct eligibility false, freshness `STALE`, lineage
`VALIDATED`, and quarantine/deadend only from actual blocked query-evaluation
states. They make advisory context available, not compute capability and not a
direct answer.

Direct state requires selected fresh candidate, valid projection and
certificate, exact compatibility projections, informational non-action class,
scope/policy/schema compatibility, no quarantine/deadend, no invalid G2-A
history, half-open use-time validity, zero operations, and successful existing
Root shortcut validation. It derives freshness `CURRENT`, lineage `VALIDATED`,
`context_available=true`, and direct eligibility true. `INVALID` is not a
valid serialized lineage value; invalid source produces no binding.

The bound builder accepts no `binding_state` argument. It derives
`RESOLUTION_CONTEXT_BOUND` only from a valid report, exact compatibility
tuple, coherent use time, and absent Root triple. It derives
`DIRECT_REUSE_BOUND` only when the same family validates, the complete Root
triple is present, and `validate_existing_root_shortcut_decision_v01` returns
`(True, ())`. One or two Root-triple members, an invalid complete shortcut,
substitution, or an attempt to request or hide state fails closed; no invalid
direct family is silently downgraded to context-only.

For bound states, query `owning_local_root_id` equals router Root, query domain
equals router domain, query evaluation/use time equals snapshot epoch, and the
derived query ID equals router and binding transaction IDs. The query is built
by `build_drs_temporal_query_v01`; its `drsquery_v01:<64hex>` identity becomes
the G2-C transaction for this v0.1 profile. Request identity remains distinct.
Direct state additionally requires source Root input/result transaction IDs to
equal query ID.

The exact compatibility projection type is `LegacyDRSProjectionV01`; its name
describes the accepted G2-B compatibility source, not a G2-C adapter. The tuple
must equal report `source_projections` exactly and each current validator must
pass. A raw dictionary or copied report/certificate/Root ID never suffices.

There is no public standalone writeback validator, so
`g2b_writeback_evidence` is exactly `None` and does not influence routing.

`memory_informed` requires either bound G2-B state, context availability true,
its dedicated AVAILABLE capability, and all local gates. Direct reuse remains
independently restricted to `DIRECT_REUSE_BOUND`.

The direct shortcut call is exactly:

```python
def validate_existing_root_shortcut_decision_v01(*, resolution_report: DRSResolutionReportV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, use_time: int) -> tuple[bool, tuple[str, ...]]
```

Report canonical bytes come from `drs_resolution_report_to_plain_data_v01`;
compatibility bytes come from `legacy_drs_projection_to_plain_data_v01` in
exact report order; Root-result bytes come from
`root_decision_result_to_plain_dict_v01`. These digests are rebuilt after all
public source validators pass.

## 15. Historical/Out-of-Scope Disposition

This is the sole bounded classification of historical execution-representation
surfaces.

| Surface | Classification | Active G2-C authority | Disposition |
|---|---|---:|---|
| current proof router and caller booleans | LEGACY | false | unchanged and not imported by G2-C |
| proof-router labels and matrices | HISTORICAL | false | canonical validators reject them; no mapping |
| numbered labels and old branches | HISTORICAL | false | evidence only; no deletion or cleanup |
| `direct_protocol` declaration | OUT_OF_SCOPE | false | `OUT_OF_SCOPE_FOR_G2C_V01` |

They create no adapter, migration, caller migration, compatibility workstream,
slice, cleanup, deletion, or design authority.

## 16. Contradiction Register Disposition

CR-14 is `ACTIVE_CONTRACT_CONFLICT`. CR-19 and CR-20 remain inactive findings
and create no work.

| ID | Subject | Classification | Exact disposition | Owner decision remains |
|---|---|---|---|---:|
| CR-01 | Owner route versus older execution vectors | `IMPLEMENTATION_DOC_CONFLICT` | Section 4 controls; Section 15 is the sole inactive classification. | false |
| CR-02 | Raw-text/dict input versus bounded typed input | `ACTIVE_CONTRACT_CONFLICT` | Exact source-bound thirteen-type contract; runtime context mandatory. | false |
| CR-03 | Caller booleans influence routing | `DUPLICATED_AUTHORITY` | Local Root profiles and actual source validators own facts. | false |
| CR-04 | Proof labels versus ten-mode vocabulary | `IMPLEMENTATION_TEST_CONFLICT` | Exact validator rejects them; no mapping. | false |
| CR-05 | Proposal, effective Root mode, and trace mode conflated | `AMBIGUOUS_SEMANTICS` | Proposal, source Root result, decision projection, and trace refs are distinct. | false |
| CR-06 | Raw reuse dictionary implies shortcut | `ACTIVE_CONTRACT_CONFLICT` | Complete actual G2-B direct chain required. | false |
| CR-07 | Text alias/reflex path toward action | `ACTIVE_CONTRACT_CONFLICT` | No aliases; action relation and Root review are explicit. | false |
| CR-08 | Incidental branch order versus minimum safe depth | `MISSING_BINDING` | Exact ranks and two-stage selection frozen. | false |
| CR-09 | No bounded cost contract | `MISSING_BINDING` | Eight Root-local mode profiles cross-bind deterministic integer cost. | false |
| CR-10 | Blocked and needs-user conflated | `MISSING_BINDING` | Separate terminal rows and hard-block precedence frozen. | false |
| CR-11 | Capability/privacy availability incomplete | `UNSPECIFIED_CURRENTLY` | Mode-specific profile gates and six declared capability identities frozen. | false |
| CR-12 | Semantic and fractal depth conflated | `AMBIGUOUS_SEMANTICS` | Distinct modes and no fallback. | false |
| CR-13 | Generic topology reference without builder | `MISSING_BINDING` | Absence sentinel and route eligibility; G2-C creates no topology. | false |
| CR-14 | SemanticWork requires a topology ref before semantic work | `ACTIVE_CONTRACT_CONFLICT` | Exact absence sentinel preserves current shape and owner order. | false |
| CR-15 | Default Registry versus G2-C review | `AMBIGUOUS_SEMANTICS` | Separate append-only profile validator plus contextual evaluator; default exact. | false |
| CR-16 | Semantic contribution vocabulary confused with execution modes | `AMBIGUOUS_SEMANTICS` | Vocabularies remain disjoint. | false |
| CR-17 | `direct_protocol` resembles a mode | `OUT_OF_SCOPE` | Explicitly not a mode. | false |
| CR-18 | Raw request to typed G2-B query absent | `UNSPECIFIED_CURRENTLY` | Remains false; validated typed objects only. | false |
| CR-19 | Inactive numbered representations | `HISTORICAL_ONLY` | Section 15 only. | false |
| CR-20 | Inactive proof/document branches | `OUT_OF_SCOPE` | Section 15 only. | false |

## 17. Exact Implementation Path Ledger

Every connected path has one classification.

### 17.1 REQUIRED_NEW_PATH

| Path | Exact G2-C ownership | Slice |
|---|---|---|
| `hedgehog/kernel/execution_mode_router_v01.py` | thirteen types, source bindings, public API, validation, feasibility, proposal, Root/ABI/Registry projections | G2-C1..G2-C4 |
| `schemas/execution_mode_router_v01.schema.json` | exactly twelve serialized forms | G2-C1 |
| `tests/test_execution_mode_router_g2_c_v01.py` | validation groups 1..21 | G2-C1..G2-C5 |
| `demo/run_execution_mode_router_g2_c_v01.py` | exact deterministic ten-case proof | G2-C5 |

### 17.2 REQUIRED_ADDITIVE_MUTATION

| Path | Exact G2-C-owned append | Historical material frozen | Protecting test | Slice |
|---|---|---|---|---|
| `hedgehog/kernel/__init__.py` | after all G2-C router and Transition symbols exist in G2-C4, append direct imports/attributes for thirteen G2-C types and seventy-four G2-C functions; preserve historical `kernel.__all__` exactly | every existing import, direct attribute, and the complete historical `kernel.__all__` tuple byte-for-byte and order-for-order | new G2-C contract tests plus historical package-surface tests | G2-C4 |
| `hedgehog/kernel/abi_v01.py` | append only the three exact artifact-type literals | current dataclass, generic builders/validators, current artifact IDs, and every existing literal/order prefix | `tests/test_kernel_abi_v01.py` | G2-C1 |
| `tests/test_kernel_abi_v01.py` | append three-literal, v1-envelope-preservation, and no-base-orchestration/import assertions | every existing assertion | itself | G2-C1/G2-C4 |
| `schemas/kernel_artifact_v01.schema.json` | append only three artifact enum literals | every other schema definition | ABI/schema tests | G2-C1 |
| `hedgehog/kernel/transition_registry_v01.py` | append only G2-C profile constants/vocabularies, six plain rules, pure profile builder/validator/serializer, and pure profile-aware TransitionDecision validator/serializer/identity rebuilder | default 18-rule bytes, ID, rules, builder, validator, errors, lookup, constants, and import direction | `tests/test_transition_registry_v01.py` | G2-C4 |
| `tests/test_transition_registry_v01.py` | append pure profile/decision identity, serialization, guard-order, commit, content-ID, and default-preservation tests | all existing assertions | itself | G2-C4 |
| `hedgehog/kernel/conformance_v01.py` | append v0.4 category/probes | v0.1..v0.3 semantics | runner tests | G2-C6 |
| `demo/run_kernel_conformance_v01.py` | append runner v0.3 G2-C act | prior acts/output | `tests/test_kernel_conformance_v01_runner.py` | G2-C6 |
| `tests/test_kernel_conformance_v01_runner.py` | append v0.4/v0.3 and preservation assertions | prior assertions | itself | G2-C6 |
| `demo/run_living_gauntlet_v01.py` | append Living v1.3 G2-C act | v1.0..v1.2 rows and identities | `tests/test_living_gauntlet_v01_runner.py` | G2-C6 |
| `tests/test_living_gauntlet_v01_runner.py` | append v1.3 and preservation assertions | prior assertions | itself | G2-C6 |

```text
REQUIRED_ADDITIVE_MUTATION_PATH_COUNT=11
DIRECT_PACKAGE_G2C_ATTRIBUTE_COUNT=87
```

The Kernel artifact schema does require the narrow append because the current
enum would reject all three profile artifacts. No other schema change is
required.

Focused G2-C tests are cumulative. C1 tests import only the implemented C1
surface directly from `execution_mode_router_v01.py` and do not require future
package attributes. C2 and C3 likewise test their owner-module surfaces without
requiring the final facade. C4 tests require the complete facade and exact
object identities. C5 and C6 preserve it. Historical tests remain unmodified
unless their own path is explicitly additive in this ledger.

### 17.3 READ_ONLY_CONSUMER

Each literal path below is read-only:

- `hedgehog/context_packets.py`
- `hedgehog/semantic_reasoning_adapter.py`
- `hedgehog/structured_rationale.py`
- `tests/test_context_packets_core.py`
- `tests/test_semantic_reasoning_adapter_core.py`
- `tests/test_structured_rationale_core.py`
- `hedgehog/evidence/sealed_evidence_profile_v01.py`
- `hedgehog/evidence/sealed_package_v01.py`
- `hedgehog/evidence/external_anchor_v01.py`
- `hedgehog/evidence/sealed_replay_evidence_v01.py`
- `tests/test_sealed_evidence_profile_v01.py`
- `tests/test_sealed_evidence_package_v01_runner.py`
- `tests/test_sealed_evidence_anchor_v01_runner.py`
- `tests/test_sealed_evidence_replay_v01_runner.py`
- `hedgehog/action_commit_packet_v02.py`
- `tests/test_action_commit_packet_lifecycle_g2_a_v01.py`
- `hedgehog/drs_semantic_address_v01.py`
- `hedgehog/drs_memory_resolution_v01.py`
- `hedgehog/reuse_certificate_v01.py`
- `hedgehog/drs_g2b_compatibility_v01.py`
- `demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py`
- `tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py`
- `hedgehog/kernel/integrity_replay_v01.py`
- `hedgehog/kernel/semantic_work_v01.py`
- `hedgehog/kernel/trust_model_v01.py`
- `hedgehog/kernel/root_decision_v01.py`
- `schemas/semantic_work_v01.schema.json`
- `tests/test_semantic_work_v01.py`
- `tests/test_kernel_trust_model_v01.py`
- `tests/test_root_decision_kernel_v01.py`
- `tests/test_schema_files_valid.py`
- `demo/run_full_semantic_e2e_v01.py`
- `demo/run_live_unknown_request_dual_rich_context_v01.py`
- `demo/run_supplier_payment_shipment_release_review_wow_v1_1.py`
- `tests/test_full_semantic_e2e_v01_runner.py`
- `tests/test_live_unknown_request_dual_rich_context_v01.py`

The exact BSEP donor is `demo/run_full_semantic_e2e_v01.py` for the current
business-request/route/BSEP construction chain. The warehouse action donor is
`demo/run_supplier_payment_shipment_release_review_wow_v1_1.py`. The exact
two-domain G2-B donor is
`demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py`. The future G2-C
runner uses current public builders, not donor private helpers or historical
outputs.

Base-Kernel dependency direction is exact. `abi_v01.py`,
`transition_registry_v01.py`, and `root_decision_v01.py` import no G2-C router.
The Transition module remains pure, deterministic, immutable,
lookup/profile-data oriented, and free of Root and SemanticWork imports.
`execution_mode_router_v01.py` imports concrete base submodules and never the
aggregate `hedgehog.kernel` package. G2-C payload projection, recursive payload
scan, contextual artifact IDs, bundle staging, contextual Transition
evaluation, Root source shaping, support identities, and complete profile
validation all live in the router module. Package direct imports and attributes
are appended once in G2-C4, only after all thirteen types, sixty-eight router
functions, and six Transition-profile functions exist and validate. G2-C1,
G2-C2, and G2-C3 do not modify `hedgehog/kernel/__init__.py`; G2-C5 does not
modify it; G2-C6 verifies it without mutation. The existing `kernel.__all__`
tuple remains byte-for-byte and order-for-order unchanged: no G2-C name is
added to the star-export surface, and no historical import or attribute is
removed or reordered. The 87 direct names are the thirteen G2-C types plus 68
router-module functions plus six pure Transition-profile functions. The exact
arithmetic is `13 + 68 + 6 = 87`, `68 + 6 = 74`, and `13 + 74 = 87`. Focused
tests require each direct package attribute to be the identical object from its
owning module and require `kernel.__all__` to equal the committed pre-G2-C
tuple. The dependency
direction is generic base contracts -> G2-C composition/profile -> package
export; no base import cycle is permitted.

### 17.4 HISTORICAL_OUT_OF_SCOPE

- `hedgehog/mode_router.py`
- `demo/run_mode_selection_matrix.py`
- `tests/test_mode_router_runtime.py`
- `tests/test_mode_selection_matrix_runner.py`

Their sole disposition is Section 15.

### 17.5 FROZEN_EVIDENCE

- `docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md`
- `docs/audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log`
- `docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md`
- `docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log`
- all accepted R-H1, G2-A, G2-B, sealed, live, release, owner, and private
  evidence.

### 17.6 CLOSURE_ONLY_PATH

- `docs/audit_reports/auditor_execution_mode_router_g2_c_v01.log`
- `docs/execution_mode_router_g2_c_checkpoint_v01.md`
- active status sections of `AGENTS.md`, README, Machine Manifest, current
  overlay, claim index, limitations, and current notes;
- Human Passport only if a later separately authorized narrow additive update
  is proven necessary.

No closure-only path is authorized in G2-C1..G2-C6.

## 18. Exact G2-C1 through G2-C6 Slice Plan

Exactly six slices exist, in dependency order.

### G2-C1 - Canonical Scalar Law, Types, Schema, Local Mode Profiles, Structural Validators, and ABI Vocabulary

Owns thirteen types, twelve serialized forms, request/transaction/domain/time
identities, local profiles and snapshot, serializers, identities, structural
validators, reason registry, ABI vocabulary/schema enum,
the single time-envelope-reference law, G2-C/source scalar distinction,
source-native identity exceptions, exact non-identity SHA framing, schema
metadata/versions, G2-C ABI-safe projections and contextual artifact identities
in the router module, import-cycle prevention, derived router traces,
time-envelope-ref and mode-profile-set identities, SourceContext structural
target, the single BSEP family-digest framing, the final ordered 74-name target
tuple as planning data, immutable pre-facade `kernel.__all__` expectations, the
thirty-field Root decision schema shape, structural cost-invalid handling,
C1-owned router functions, and contract tests. G2-C1 does not implement package
exports or expose the final 87 direct attributes; its tests import C1-owned
symbols directly from `execution_mode_router_v01.py`.

### G2-C2 - Actual Business-Request, BSEP, Replay, G2-A, and G2-B Source Bindings

Owns actual source context, public source validator calls, causal BSEP family,
Replay, action relation/inspection, derived G2-B context/direct-reuse state,
bound-query transaction law, exact source digest framing, structural/contextual
SourceContext separation, exact presence matrices, contextual router-input
validation, exact BSEP route/proposal/rationale cross-validation, exact G2-A
NO_PACKET values, G2-B context availability, and substitution rejection.
It adds only its source-binding/contextual functions and focused tests to the
router module, reruns C1, and does not mutate the package facade or create a
future C3/C4 symbol.

### G2-C3 - Feasibility, Minimum-Safe-Depth Selection, Cost, Terminal Law, and Proposal

Owns ten-mode feasibility, local profiles and derived local reasons, exact
evidence-ref order, shared local/cloud depth, cost tie-break, invalid-input
no-proposal law, terminal precedence, exact ten-row proposal, and the
non-authoritative `route_eligibility_candidate` marker. It also owns
classification-label non-authority, global hard-block/user-input infeasibility,
the renamed hard-block reason, and exact proposal capability/packet derivation.
It adds only feasibility, selection, terminal, and proposal functions/tests to
the router module, reruns C1/C2, and does not mutate the package facade or
create a future C4 symbol.

### G2-C4 - Existing Root Decision Projection, Contextual ABI, Transition Registry, and Route Eligibility

Owns pure G2-C TransitionDecision profile law, Root support identities, derived
review context/traces and default trust profiles, proposal artifact and Stage-A
bundle, proposal-to-Root Transition, review lineage/action, exact unchanged
Root Decision source law, narrowing, decision artifact and Stage-B bundle,
post-Root Transition, optional RouteEligibility, Stage-C bundle, complete
contextual ABI profile, direct-decision-consumption rejection, and no mutation
of `root_decision_v01.py`. It also owns exact empty Root conflict geometry, the
real source-contract probe, serialized G2-C Root projection reasons, the
decision ABI payload update, and per-stage reason ownership. G2-C4 completes
all sixty-eight router-module functions, creates the six Transition-profile
functions, validates all seventy-four exact signatures and all thirteen types,
then performs the sole `hedgehog/kernel/__init__.py` mutation. That mutation
exposes exactly 87 direct object-identical attributes while preserving
`kernel.__all__` and import direction. It occurs only after all owner-module
symbols validate; no second facade hop exists.

### G2-C5 - Two-Domain Deterministic Proof and Complete Negative Matrix

Owns exact ten cases, actual source builders, all five Root outcomes, terminal
scope, G2-B query identity, source/Root/ABI/Registry/Transition substitution,
all new scalar/SHA/schema/support/trace/import/operation-order negatives,
recursive payload and lineage negatives, domain invariance, repeated equality,
all accepted positive/negative corrections, failure injection, and zero
operations.

### G2-C6 - Living Gauntlet and Kernel Conformance Integration

Owns Living v1.3, Conformance v0.4, Conformance runner v0.3, corrected complete
seventeen-step source/ABI/Registry/Root/eligibility proof, historical
preservation, complete-profile proof, base-module import/history preservation,
verification of the unchanged G2-C4 package facade, immutable package `__all__`,
87 object-identical direct package attributes, corrected Root conflict/profile
geometry, and no Gate-2 closure. G2-C6 consumes and verifies the facade; it does
not create, own, or modify that facade mutation.

No seventh, adapter, migration, caller-migration, or cleanup slice exists.
Implementation requires accepted committed preflight and separate owner
authorization.

## 19. Exact 22-Group Validation Geometry

Exactly twenty-two groups are frozen; pytest function count is not frozen.

1. Exact thirteen types, Root decision thirty fields, twelve serialized schema
   definitions, metadata, SourceContext target, and artifact schema versions.
2. One BSEP family-digest law, exact constituent SHA material, all G2-C and
   support identities, and repeated canonical bytes.
3. Cumulative API/facade validation with one staged law:
   G2-C1 freezes the final 74-name tuple, validates exact signatures for every
   currently implemented C1-owned function, proves no future-owned stub exists,
   preserves historical `kernel.__all__`, proves no facade mutation, and checks
   import direction. G2-C2 requires all C1/C2 functions and signatures, no
   C3/C4 stub, an unmodified facade, and all C1 checks. G2-C3 requires all
   C1..C3 router functions and exact signatures, keeps the six Transition
   functions absent, keeps the facade unmodified, and preserves earlier checks.
   G2-C4 requires all sixty-eight router functions, all six Transition-profile
   functions, all seventy-four exact signatures, all thirteen types, exactly
   87 object-identical direct package attributes, unchanged `kernel.__all__`,
   and clean imports. G2-C5 and G2-C6 preserve the complete G2-C4 API and facade
   unchanged.
4. Exact 100-reason registry, corrected regex, `g2c_hard_block_present`, old
   reason absence, uniqueness, order, declared use, and reachability.
5. Actual business/route/proposal/rationale/BSEP cross-validation, exact source
   reference, finite confidence, false forbidden claims, source-family digest,
   and non-finite rejection.
6. Actual sealed-Replay full-context validation, structural/contextual presence
   separation, and substitution matrix.
7. Exact G2-A NO_PACKET field matrix, NEW_ACTION/EXISTING relation, PRESENT
   derivation, snapshot evaluation-context binding, and source validation.
8. Exact G2-B NOT_APPLICABLE/RESOLUTION_CONTEXT_BOUND/DIRECT_REUSE_BOUND
   matrices, no `INVALID` lineage, no partial shortcut downgrade, derived state,
   query transaction, and context availability.
9. Root-local eight-mode profiles, exact five valid local reason sources,
   structural invalid-cost failure, profile-set SHA/ID, gates, capability, cost,
   and time reference.
10. Classification labels cannot authorize a mode; source-native raw-hex IDs,
    derived router traces, actual-context cross-bindings, absence, copied
    status, and substitution are checked.
11. Invalid, malformed, or source-invalid input returns FAIL_CLOSED and creates
    no proposal.
12. Exact executable positive-row reasons, ten-mode positive/terminal matrix,
    canonical-label rejection, and no hidden full-fractal class gate.
13. Exact per-mode evidence refs, global user-input requirements, action
    relation/shortcut, privacy/policy/scope/risk/availability/freshness, and no
    silent fallback.
14. Exact `missing_evidence_codes`, feasibility before cost, shared local/cloud
    tier, integer cost, and exact cost/canonical-index tie-break reason.
15. Global hard-block infeasibility, global needs-user infeasibility, hard-block
    precedence, no-safe-mode selection, and terminal-row law.
16. Exact ten-row proposal, selected row, proposal reason tuple, downstream
    capability IDs, packet-required formula, terminal contribution scope,
    downstream class, non-authority, and zero objects.
17. Root decision thirty-field identity/schema/ABI payload including projection
    reason; three ABI-safe payloads, contextual IDs, bundles, decision-bypass
    rejection, schema enum, and generic ABI preservation.
18. Content-derived G2-C Registry, six rules, exact TransitionDecision law,
    pre/post evaluators, commit derivation, substitution rejection, and default
    Registry preservation.
19. Existing Root law, exact empty packet/input/result conflict geometry,
    BSEP-ID conflict rejection, support IDs, derived default trust profiles,
    read-only Root module/tests, and no independent Root.
20. Root review context/traces, source versus G2-C Transitions, exact five Root
    projection reason tuples, accepted-only packet-required copying, narrowing,
    and RouteEligibility as sole bounded route-consumption authority.
21. Exact two-domain ten-case proof and every updated source/G2-A/G2-B/profile/
    feasibility/proposal/Root/package negative, repeated equality, failure
    injection, and zero operations.
22. Living v1.3 and Conformance v0.4/runner v0.3 repeat all corrected invariants,
    preserve immutable `__all__`, base import direction, ABI/Registry/Root
    history, and Gate-2 non-closure.

### 19.1 Correction-cluster coverage

| Correction cluster | Exact groups |
|---|---|
| types, thirty-field Root decision, schema metadata, and versions | 1, 2, 3, 17 |
| G2-C scalar law versus finite source floats | 3, 5, 21 |
| project/source identities, non-identity SHA, time/profile/support IDs | 2, 5, 9, 10, 17, 19, 21 |
| staged API availability, final C4 facade, immutable `__all__`, import direction | 3, 10, 19, 20, 22 |
| exact public reason and hard-block rename law | 4, 9, 15, 18, 21 |
| business request/BSEP cross-validation and single family SHA | 2, 5, 10, 21 |
| Replay | 6, 10, 21 |
| G2-A exact NO_PACKET and PRESENT relation | 7, 10, 13, 21 |
| G2-B three states, context, query, and no downgrade | 8, 10, 13, 21 |
| local mode profiles, structural cost, reasons, profile-set | 2, 4, 9, 13, 14, 21 |
| structural/contextual SourceContext split | 1, 6, 7, 8, 10, 11, 21 |
| invalid source creates no proposal | 10, 11 |
| classification non-authority, ten modes, feasibility, tie-break, terminals | 10, 12, 13, 14, 15 |
| evidence refs/proposal derived fields/terminal scope | 13, 14, 16, 21 |
| ABI payload/artifact IDs/lineage/bundles and decision bypass | 2, 3, 17, 20, 21, 22 |
| pure TransitionDecision and two contextual stages | 18, 20, 21, 22 |
| existing Root conflict law, probe, projection reasons, and support IDs | 17, 19, 20, 21, 22 |
| two-domain substitutions and zero operations | 21 |
| Living/Conformance/history preservation | 22 |

## 20. Two-Domain Proof Contract

The exact domains and fixtures are:

```text
TRAVEL_POLICY_INFORMATION
g2c_fixture:travel_policy_information:v01

WAREHOUSE_MAINTENANCE_INFORMATION
g2c_fixture:warehouse_maintenance_information:v01

CANONICAL_SCENARIO_COUNT=10
```

The runner builds actual business request, route context, semantic proposal,
structured rationale, BSEP, Replay family, G2-A family, G2-B family, local
profiles, Root source objects, ABI artifacts, and contextual Transition
decisions through public current builders and validators. Hardcoded acceptance
strings and fabricated references cannot satisfy a positive case.

### 20.1 Exact case identities and outcomes

Shared exact identities:

- travel Root: `root:g2c:travel_policy_information:v01`;
- warehouse Root: `root:g2c:warehouse_maintenance_information:v01`;
- domain values are the exact uppercase literals above;
- request and transaction IDs are independent and never equal; cases 2, 3, and
  4 derive transaction from the actual G2-B temporal query;
- all BSEP bindings are `BOUNDED_SEMANTIC_EVIDENCE_BOUND`;
- all times use epoch `1785542400`, UTC `2026-08-01T00:00:00+00:00`, valid
  from the same instant to `2026-08-01T01:00:00+00:00`, TTL 3600, static
  freshness, and case-specific session anchor;
- all counters are zero.

Literal identity matrix:

| Case | Request ID | Transaction ID | Root ID | Domain ID |
|---:|---|---|---|---|
| 1 | `request:g2c:travel:sealed_replay:v01` | `transaction:g2c:travel:sealed_replay:v01` | `root:g2c:travel_policy_information:v01` | `TRAVEL_POLICY_INFORMATION` |
| 2 | `request:g2c:travel:direct_informational_reuse:v01` | `DERIVED_DRS_TEMPORAL_QUERY_ID` | `root:g2c:travel_policy_information:v01` | `TRAVEL_POLICY_INFORMATION` |
| 3 | `request:g2c:travel:memory_informed:v01` | `DERIVED_DRS_TEMPORAL_QUERY_ID` | `root:g2c:travel_policy_information:v01` | `TRAVEL_POLICY_INFORMATION` |
| 4 | `request:g2c:travel:cloud_llm_narrow:v01` | `DERIVED_DRS_TEMPORAL_QUERY_ID` | `root:g2c:travel_policy_information:v01` | `TRAVEL_POLICY_INFORMATION` |
| 5 | `request:g2c:travel:full_semantic_reject:v01` | `transaction:g2c:travel:full_semantic_reject:v01` | `root:g2c:travel_policy_information:v01` | `TRAVEL_POLICY_INFORMATION` |
| 6 | `request:g2c:warehouse:deterministic_new_action:v01` | `transaction:g2c:warehouse:deterministic_new_action:v01` | `root:g2c:warehouse_maintenance_information:v01` | `WAREHOUSE_MAINTENANCE_INFORMATION` |
| 7 | `request:g2c:warehouse:local_slm:v01` | `transaction:g2c:warehouse:local_slm:v01` | `root:g2c:warehouse_maintenance_information:v01` | `WAREHOUSE_MAINTENANCE_INFORMATION` |
| 8 | `request:g2c:warehouse:full_fractal_fixture_capability:v01` | `transaction:g2c:warehouse:full_fractal_fixture_capability:v01` | `root:g2c:warehouse_maintenance_information:v01` | `WAREHOUSE_MAINTENANCE_INFORMATION` |
| 9 | `request:g2c:warehouse:blocked_existing_packet:v01` | `transaction:g2c:warehouse:blocked_existing_packet:v01` | `root:g2c:warehouse_maintenance_information:v01` | `WAREHOUSE_MAINTENANCE_INFORMATION` |
| 10 | `request:g2c:warehouse:needs_user:v01` | `transaction:g2c:warehouse:needs_user:v01` | `root:g2c:warehouse_maintenance_information:v01` | `WAREHOUSE_MAINTENANCE_INFORMATION` |

Cases 2, 3, and 4 call `build_drs_temporal_query_v01` with this exact material:

| Argument | Case 2 | Cases 3 and 4 |
|---|---|---|
| `query_mode` | `DIRECT_REUSE_CANDIDATE` | `MEMORY_CONTEXT_ONLY` |
| `semantic_address_id` | actual case `SemanticAddressV01.semantic_address_id` | actual case `SemanticAddressV01.semantic_address_id` |
| `scope_fingerprint` | lowercase SHA-256 of exact case scope ref | lowercase SHA-256 of exact case scope ref |
| `as_of`, `evaluation_time` | `1785542400`, `1785542400` | `1785542400`, `1785542400` |
| `evaluation_time_source` | `INJECTED_CURRENT_DECISION_TIME` | `INJECTED_ANALYSIS_TIME` |
| `time_range_start`, `time_range_end` | `1785542400`, `1785546000` | `1785542400`, `1785546000` |
| `required_time_axes` | `("PT","KT","ET","CT","TTL","VALIDITY")` | `("KT","TTL","VALIDITY")` |
| `freshness_policy_id`, `max_age_seconds` | `freshness:g2c:v01`, `3600` | `freshness:g2c:v01`, `3600` |
| `domain`, `risk_class` | exact travel domain, `LOW` | exact travel domain, `LOW` |
| `reuse_intent` | `INFORMATIONAL_SHORTCUT_CONSIDERATION` | `CONTEXT` |
| `requested_reuse_classes` | `("ANSWER_SHORTCUT",)` | `("CONTEXT_ONLY",)` |
| `required_evidence_classes` | exact current nine-class G2-B ordered tuple | exact current nine-class G2-B ordered tuple |
| `forbidden_changes` | `("POLICY_CHANGED",)` | `("POLICY_CHANGED",)` |
| `policy_version`, `schema_versions` | exact case policy ID, `("v0.1",)` | exact case policy ID, `("v0.1",)` |
| `owning_local_root_id` | exact travel Root | exact travel Root |

The current builder derives the exact `drsquery_v01:<64hex>`; that ID becomes
the router, G2-B binding, SemanticWork, source Root, and ABI transaction ID.
It never equals the independent request ID.

For each case, `selected_feasibility_row_id` is exactly the rebuilt identity of
the row at that selected mode's canonical index in the ten-row tuple. A
fixture-supplied row ID is forbidden.

| # | Case suffix / exact case ID | Source states | Selected / Root | Downstream / eligibility |
|---:|---|---|---|---|
| 1 | `g2c_case:travel:sealed_replay:v01` | replay BOUND; G2-A NO_PACKET; G2-B NOT_APPLICABLE; NON_ACTION | `sealed_replay`; ACCEPT | SHORTCUT_RETURN_TO_ROOT / present |
| 2 | `g2c_case:travel:direct_informational_reuse:v01` | replay NA; G2-A NO_PACKET; G2-B DIRECT_REUSE_BOUND; NON_ACTION | `direct_informational_reuse`; ACCEPT | SHORTCUT_RETURN_TO_ROOT / present |
| 3 | `g2c_case:travel:memory_informed:v01` | replay NA; G2-A NO_PACKET; G2-B RESOLUTION_CONTEXT_BOUND; NON_ACTION | `memory_informed`; ACCEPT | RUNTIME_TOPOLOGY_ELIGIBLE / present |
| 4 | `g2c_case:travel:cloud_llm_narrow:v01` | replay NA; G2-A NO_PACKET; G2-B RESOLUTION_CONTEXT_BOUND; NON_ACTION | `cloud_llm`; NARROW | RUNTIME_TOPOLOGY_ELIGIBLE / present |
| 5 | `g2c_case:travel:full_semantic_reject:v01` | replay NA; G2-A NO_PACKET; G2-B NA; NON_ACTION | `full_semantic`; REJECT | TERMINAL_NO_CONSUMPTION / absent |
| 6 | `g2c_case:warehouse:deterministic_new_action:v01` | replay NA; G2-A NO_PACKET; G2-B NA; ACTION/NEW_ACTION_NO_PACKET | `deterministic`; ACCEPT | SHORTCUT_RETURN_TO_ROOT / present; later packet true, created false |
| 7 | `g2c_case:warehouse:local_slm:v01` | replay NA; G2-A NO_PACKET; G2-B NA; NON_ACTION | `local_slm`; ACCEPT | RUNTIME_TOPOLOGY_ELIGIBLE / present |
| 8 | `g2c_case:warehouse:full_fractal_fixture_capability:v01` | replay NA; G2-A NO_PACKET; G2-B NA; NON_ACTION | `full_fractal`; ACCEPT | RUNTIME_TOPOLOGY_ELIGIBLE / present; topology false |
| 9 | `g2c_case:warehouse:blocked_existing_packet:v01` | replay NA; G2-A PRESENT but ineligible; G2-B NA; ACTION/EXISTING_PACKET_ATTEMPT | `blocked`; BLOCKED | TERMINAL_NO_CONSUMPTION / absent |
| 10 | `g2c_case:warehouse:needs_user:v01` | replay NA; G2-A NO_PACKET; G2-B NA; ACTION/NEW_ACTION_NO_PACKET | `needs_user`; NEEDS_USER | TERMINAL_NO_CONSUMPTION / absent |

Exact per-stage reasons are separate and never conflated:

| # | Selected row reason | Proposal reason tuple | Source Root reason | G2-C Root projection tuple | Pre-Root Transition reason | Post-Root Transition reason |
|---:|---|---|---|---|---|---|
| 1 | `g2c_sealed_replay_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_accept_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_route_accept_allowed` |
| 2 | `g2c_direct_informational_reuse_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_accept_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_route_accept_allowed` |
| 3 | `g2c_memory_informed_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_accept_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_route_accept_allowed` |
| 4 | `g2c_cloud_llm_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_narrow_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_scope_narrow_allowed` |
| 5 | `g2c_full_semantic_feasible` | `(g2c_proposal_sources_valid,)` | `policy_rejected_candidate` | `(g2c_root_reject_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_reject_recorded` |
| 6 | `g2c_deterministic_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_accept_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_route_accept_allowed` |
| 7 | `g2c_local_slm_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_accept_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_route_accept_allowed` |
| 8 | `g2c_full_fractal_feasible` | `(g2c_proposal_sources_valid,)` | `validated_candidate_accepted` | `(g2c_root_accept_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_route_accept_allowed` |
| 9 | `g2c_hard_block_present` | `(g2c_proposal_sources_valid,)` | `hard_policy_violation` | `(g2c_root_blocked_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_blocked_recorded` |
| 10 | `g2c_user_input_required` | `(g2c_proposal_sources_valid,)` | `user_permission_missing` | `(g2c_root_needs_user_projected,)` | `g2c_transition_root_review_required` | `g2c_transition_needs_user_recorded` |

`CONTEXT` in case 4 is exact `RESOLUTION_CONTEXT_BOUND`; `NA` is exact
`NOT_APPLICABLE`. Review actions are ACCEPT, NARROW, REJECT, and
TERMINAL_FROM_PROPOSAL as implied by the Root outcome.

Every case's actual `RootReviewPacketV01`, Root input, and Root result has
`conflict_set_ids=()`. Cases 3 and 4 have nonempty context-only record IDs,
context available true, direct eligibility false, freshness `STALE`, lineage
`VALIDATED`, no shortcut/certificate, and no Root triple. Case 8 treats
`BOUNDED_FRACTAL_REQUIRED` as audit metadata only; its profile is the only safe
feasible executable profile, its capability is AVAILABLE, and all shallower
modes are independently infeasible. Case 9 uses
`g2c_hard_block_present`. Case 10 has false proposal/decision packet-required
values and no RouteEligibility. Case 6 has true proposal, accepted decision,
and shortcut RouteEligibility packet-required values while packet creation
remains false.

### 20.2 Exact eight-profile values per case

Profile order is `deterministic`, `sealed_replay`,
`direct_informational_reuse`, `memory_informed`, `local_slm`, `cloud_llm`,
`full_semantic`, `full_fractal`. Every profile has policy/scope/risk/privacy
`true` unless an exact override below says false. Replay/direct capability is
`NOT_REQUIRED/None`; every other mode has ID
`capability:g2c:<mode>:v01`. `A` means AVAILABLE and `U` means UNAVAILABLE.

| Case # | Capability states in profile order | Cost units in profile order | Exact gate override |
|---:|---|---|---|
| 1 | U, NR, NR, U, U, U, U, U | 10,20,30,40,50,60,70,80 | direct reuse infeasible because G2-B NA |
| 2 | U, NR, NR, U, U, U, U, U | 10,20,30,40,50,60,70,80 | Replay infeasible because absent |
| 3 | U, NR, NR, A, U, U, U, U | 10,20,30,40,50,60,70,80 | G2-B context not direct |
| 4 | U, NR, NR, U, U, A, U, U | 10,20,30,40,70,50,80,90 | narrower scope `scope:g2c:travel:public_summary:v01` allowlisted |
| 5 | U, NR, NR, U, U, U, A, U | 10,20,30,40,50,60,70,80 | source Root policy `allow_accept=false` only during review |
| 6 | A, NR, NR, U, U, U, U, U | 10,20,30,40,50,60,70,80 | later packet required true |
| 7 | U, NR, NR, U, A, U, U, U | 10,20,30,40,50,60,70,80 | none |
| 8 | U, NR, NR, U, U, U, U, A | 10,20,30,40,50,60,70,80 | request class `BOUNDED_FRACTAL_REQUIRED`; declaration only |
| 9 | U, NR, NR, U, U, U, U, U | 10,20,30,40,50,60,70,80 | hard block and invalid existing packet |
| 10 | U, NR, NR, U, U, U, U, U | 10,20,30,40,50,60,70,80 | user input missing, hard block clear |

`NR` means `NOT_REQUIRED`. Every declared unavailable capability retains its
exact capability ID. Policy, capability snapshot, and cost-model IDs are
`policy:g2c:<case-suffix>:v01`, `capabilities:g2c:<case-suffix>:v01`, and
`cost_model:g2c:deterministic:v01`. Profile IDs, set IDs, and digests are built,
never fixture-written.

The sibling selection variations are exact:

1. local and cloud both feasible at rank 50, costs 40 and 50: local selected;
2. local and cloud both feasible at rank 50, costs 60 and 40: cloud selected;
3. both feasible and cost 40: local selected by canonical index;
4. local infeasible at cost 1 and cloud feasible at cost 40: cloud selected;
   cost does not admit local.

The first two unequal-cost probes do not emit a tie-break reason. The equal
minimum-cost probe emits `g2c_selection_tie_break_applied` after
`g2c_proposal_sources_valid` in public registry order.

Deterministic positive probes additionally prove that a complete accepted
source fixture containing finite `confidence=0.66` validates and produces a
stable source digest; a valid source-native raw 64-hex identity beginning with
a decimal digit is accepted when its source validator accepts it; all three
Kernel artifacts use `schema_version="v0.1"`; and every Root support identity,
router trace tuple, Root-review context identity, and Root-review trace tuple
rebuilds exactly.

### 20.3 Exact negative and zero-operation matrix

Every case executes the exact seventeen-step order in Section 12.4, including
proposal artifact, Stage-A bundle, pre-Root `RETURN_TO_ROOT`, Root review,
actual Root result, decision artifact, Stage-B bundle, post-Root Transition,
optional RouteEligibility, and Stage-C bundle.

Each case has sibling negatives for business-request substitution, BSEP source
substitution, family digest mismatch, source validator failure, source absence,
copied status without source, cross-domain context, request/transaction/Root
substitution, time-envelope mismatch, G2-A relation mismatch, G2-B state
mismatch, Root result substitution, ABI artifact substitution, Transition rule
substitution, and caller-supplied guard attempt. The complete added matrix also
rejects a reserved ABI key at top level or nested depth, caller-selected ABI
artifact ID, non-artifact or unknown parent, missing/substituted proposal
Transition, caller-forced proposal ALLOW, literal Registry ID substitution,
caller-selected G2-B state, literal transaction in place of derived query ID,
terminal contribution `None` scope, wrong policy identity, wrong profile-set
identity, and wrong time-envelope-ref identity.

The matrix also rejects NaN, positive infinity, negative infinity, wrong
time-envelope domain or material, wrong plain-SHA framing, wrong ABI schema
version, direct use of `RootExecutionModeDecisionV01` as route permission,
false or substituted `route_eligibility_candidate`, TransitionDecision identity
substitution, default-Registry serialization used as G2-C profile authority,
wrong G2-C profile Registry ID, wrong satisfied-guard order, wrong
`root_commit_present`, wrong Root support identity, caller-supplied router
trace, caller-supplied Root-review context or trace, caller-supplied local
reason tuple, non-default trust-profile injection, a base ABI import of the
router, a base Transition import of the router/Root/SemanticWork, a base Root
import of the router, aggregate `hedgehog.kernel` import from the router,
SourceContext structural validation claiming snapshot equality, and every
operation-order barrier bypass. Existing source/Root/ABI/Registry/Transition
substitution negatives remain mandatory.

The accepted matrix additionally rejects a BSEP packet ID inserted into Root
conflicts, alternate BSEP family-digest framing, any true forbidden proposal
claim, invalid confidence, a partial G2-B shortcut family, caller-selected G2-B
state, context state with empty context-only records, serialized G2-B lineage
`INVALID`, an invalid-cost profile returned as valid, any FEASIBLE executable
row under hard block or missing user input, full-fractal feasibility inferred
from request-class spelling, a missing or wrong Root projection reason, a
terminal proposal claiming a downstream packet requirement, a G2-C name added
to `kernel.__all__`, and a missing or non-identical direct package G2-C
attribute.

Facade probe timing is cumulative: positive and negative package-facade probes
first become mandatory in G2-C4, G2-C5 includes them in the complete case and
negative matrix, and G2-C6 preserves them through Living/Conformance. C1..C3
fabricate no missing package attribute, append no G2-C name to `kernel.__all__`,
and expect no Transition-profile function before G2-C4. From G2-C4 onward, a
missing final attribute, wrong owner-module identity, or widened `__all__`
fails closed.

Every case expects exactly zero provider/model/network/connector/external-DRS
calls, packet creation, permission creation, receipt creation, topology
creation, DRS write, final output, and real-world effects. No accepted live or
sealed historical programme is rerun.


## 21. Living Gauntlet and Kernel Conformance

Repository evidence freezes:

```text
LIVING_GAUNTLET_RUNNER_VERSION=v1.3
KERNEL_CONFORMANCE_VERSION=v0.4
KERNEL_CONFORMANCE_RUNNER_VERSION=v0.3
```

Current versions are Living v1.2, Conformance v0.3, and Conformance runner
v0.2; the listed versions are the exact next append-only values.

### 21.1 G2-C Transition Registry profile

The module/profile constant is:

```text
profile_id: execution_mode_router_g2c_transition_profile_v01
registry_version: v0.1
abi_major_version: 1
rule_count: 6
```

`profile_id` is not a `TransitionRegistryV01` field. The actual
`registry_id` is the lowercase 64-hex digest under current family domain
`hedgehog.kernel.transition_registry.v01` over
`{"registry_version":"v0.1","abi_major_version":1,"rules":[<six exact plain rules>]}`.
The profile validator reconstructs it.

The default 18-rule registry bytes, ID, canonical rules, builder, validator,
lookup, private default errors, constants, and tests remain exact. Separate
G2-C-profile-only tuples freeze artifact types, actor roles, attempted effects,
guard IDs, reasons, and six rules. The default lookup is not used as G2-C
profile authority.

G2-C retains the existing `TransitionDecisionV01`; no new Transition-decision
dataclass exists. Its exact field order is:

```text
decision_id
registry_id
rule_id
abi_major_version
source_artifact_type
source_lifecycle_state
actor_role
attempted_effect
target_artifact_type
required_guards
satisfied_guards
missing_guards
decision
reason_code
root_commit_required
root_commit_present
matched
```

The existing identity domain is
`hedgehog.kernel.transition_decision.v01`. `decision_id` is raw lowercase
64-hex without a G2-C prefix. Identity material is the complete plain
17-field decision with `decision_id` omitted. It is transaction-neutral
because the existing source type has no transaction field; the contextual
evaluators and ABI profile prove transaction, Root, proposal, and artifact
binding without changing the source type.

For every successful G2-C profile decision, `registry_id` equals the rebuilt
profile registry ID, `rule_id` is one exact profile rule, `required_guards`
equals the exact rule tuple, `satisfied_guards` equals that tuple in exact
rule order, `missing_guards == ()`, `matched is true`, decision and reason
equal the rule, and the decision identity rebuilds exactly. The pre-Root
decision has `root_commit_required=false` and `root_commit_present=false`.
Every post-Root decision has both values true, with commit presence derived
from the actual validated `RootDecisionResultV01`.

`transition_registry_v01.py` adds the four pure profile-aware operations
`execution_mode_transition_registry_profile_to_plain_dict_v01`,
`validate_execution_mode_transition_decision_v01`,
`execution_mode_transition_decision_to_plain_dict_v01`, and
`rebuild_execution_mode_transition_decision_identity_v01` with the exact
signatures frozen once in Section 7.3.

The profile serializer and validator do not use the default-registry-only
`transition_decision_to_plain_dict_v01` as authority. Private profile-aware
construction is followed by the profile-aware public validator. Invalid shape
uses `g2c_transition_decision_invalid`; identity mismatch uses
`g2c_transition_decision_identity_mismatch`.

| Rule ID | Source / state | Actor / attempted effect | Target | Required contextual guards | Decision / reason | root_commit_required |
|---|---|---|---|---|---|---:|
| `g2c_transition:proposal_to_root_review:v01` | `ExecutionModeProposal` / `VALIDATED` | `execution_mode_router` / `ENTER_ROOT_REVIEW` | `RootExecutionModeDecision` | `proposal_sources_valid`, `proposal_artifact_valid`, `target_root_bound` | `RETURN_TO_ROOT` / `g2c_transition_root_review_required` | false |
| `g2c_transition:root_accept_to_route:v01` | `RootExecutionModeDecision` / `ROOT_ACCEPTED` | `root` / `ACCEPT_ROUTE` | `ExecutionModeRouteEligibility` | `root_result_valid`, `accepted_mode_valid`, `accepted_scope_valid`, `consumption_class_valid` | `ALLOW` / `g2c_transition_route_accept_allowed` | true |
| `g2c_transition:root_narrow_to_route:v01` | `RootExecutionModeDecision` / `ROOT_ACCEPTED` | `root` / `NARROW_SCOPE` | `ExecutionModeRouteEligibility` | `root_result_valid`, `accepted_mode_valid`, `narrowing_proof_valid`, `consumption_class_valid` | `ALLOW` / `g2c_transition_scope_narrow_allowed` | true |
| `g2c_transition:root_reject_record:v01` | `RootExecutionModeDecision` / `ROOT_REJECTED` | `root` / `REJECT_ROUTE` | `RootExecutionModeDecision` | `root_result_valid`, `terminal_consumption_forbidden` | `RETURN_TO_ROOT` / `g2c_transition_reject_recorded` | true |
| `g2c_transition:root_block_record:v01` | `RootExecutionModeDecision` / `BLOCKED_FAIL_CLOSED` | `root` / `BLOCK_ROUTE` | `RootExecutionModeDecision` | `root_result_valid`, `terminal_consumption_forbidden` | `BLOCKED_FAIL_CLOSED` / `g2c_transition_blocked_recorded` | true |
| `g2c_transition:root_needs_user_record:v01` | `RootExecutionModeDecision` / `ROOT_REVIEWED` | `root` / `REQUEST_USER_INPUT` | `RootExecutionModeDecision` | `root_result_valid`, `terminal_consumption_forbidden` | `NEEDS_USER` / `g2c_transition_needs_user_recorded` | true |

`evaluate_execution_mode_proposal_to_root_transition_v01` receives the G2-C
registry, proposal, router input, source context, and validated proposal
artifact. It derives every lookup field, accepts no caller guards or commit
boolean, selects only the first rule, and contextually reconstructs the
`RETURN_TO_ROOT` decision before review input exists. It never returns ALLOW
and never creates a Root decision.

`evaluate_execution_mode_root_route_transition_v01` receives the registry,
validated pre-Root decision, review input, G2-C decision, proposal, router
input, source context, actual Root Kernel/Input/Result, proposal artifact, and
decision artifact. It derives every field, including
`root_commit_present=root_decision_result.root_commit_created`, and selects one
of the five post-Root rules. It accepts no caller guard tuple or commit boolean.
All post-Root rules require `root_commit_required=true`. ACCEPT/NARROW target
RouteEligibility; terminal rules create none. Root-result or either Transition
substitution fails closed.

Default Registry validation, G2-C profile validation, and contextual evaluation
are separate named operations.

### 21.2 New deterministic acts

Living and Conformance prove all ten modes, actual request/BSEP/rationale source
family, independent request/transaction identity, Replay/G2-A/G2-B bindings,
eight local profiles, invalid-source no-proposal, one ABI, one Registry profile,
one existing Root law, shortcut versus topology route class, all substitutions,
two-domain invariance, and exact zero counters.

They also execute the exact seventeen-step order, prove recursive payload
safety, contextual artifact IDs, Stage-A/B/C bundles, derived G2-B query
transactions and states, terminal contribution scope, separate pre-Root and
post-Root G2-C Transitions, content-derived Registry identity, source Root
Transition lineage, no caller guards, and no source-free status or copied-ref
authority.

They also prove no independent Root engine, source-free acceptance, copied-ref
authority, existing-packet requirement for fresh action reasoning, packet,
permission, receipt, topology, final output, or effect creation. Historical
rows remain byte/semantic-history preserved. G2-C6 does not close Gate 2.

## 22. Audit and Closure Law

After separately authorized slices pass:

1. freeze exact implementation basis;
2. perform one independent non-repairing audit;
3. create exactly
   `docs/audit_reports/auditor_execution_mode_router_g2_c_v01.log`;
4. commit accepted audit separately;
5. only then create
   `docs/execution_mode_router_g2_c_checkpoint_v01.md` and separately
   synchronize current status;
6. record closure commit as `NOT_SELF_RECORDED`;
7. keep Gate 2 `NOT_CLOSED`;
8. keep G2-D `NEXT / NOT_STARTED`;
9. keep all release/production/security claims false.

Closure-only synchronization is limited to the active AGENTS checkpoint,
README current boundary, Machine Manifest current metadata, current overlay,
claim index, limitations, current notes, and Human Passport only if a narrow
canonical additive need is proven and separately authorized. No historical
material is rewritten.

## 23. Frozen Evidence and Non-Claims

Exact frozen evidence remains:

```text
release/completion_manifest.json
02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466

release/integration_seam_index.json
c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231
```

Accepted G2-A, G2-B, R-H1, sealed, live, publication, and private evidence is
unchanged.

```text
GATE2_STATUS=NOT_CLOSED
G2C_IMPLEMENTATION_STATUS=NOT_STARTED
G2C_IMPLEMENTATION_AUTHORIZED=false
G2D_STATUS=NOT_STARTED
G2E_STATUS=NOT_STARTED
G2F_STATUS=NOT_STARTED
PUBLIC_RELEASE=NOT_CLAIMED
RC2=NOT_CLAIMED
PRODUCTION_READINESS=NOT_CLAIMED
PRODUCTION_SECURITY_CERTIFICATION=NOT_CLAIMED
RAW_USER_REQUEST_TO_G2B_QUERY_CROSS_BINDING_IMPLEMENTED=false
EXTERNAL_GLOBAL_DRS_IMPLEMENTED=false
REAL_WORLD_EFFECTS=0
```

## 24. Explicit Exclusions

G2-C excludes public publication, Gate-2 closure, R-IP1 dependency, G2-D/E/F
implementation, runtime effect execution, new packet lifecycle, G2-A/G2-B
reopening, provider/DRS/certificate authority, final output outside Root,
inactive-surface migration or cleanup, broad refactor, compatibility adapter,
caller migration, real provider/network/connector/external-DRS calls, and any
pytest-function-count commitment.

No deletion is authorized. No second ABI, Registry family, or Root law is
created.

## 25. Implementation Acceptance Gates

Preflight acceptance does not itself authorize implementation. Slice
acceptance is cumulative: each slice passes the gates it owns and reruns every
applicable gate from earlier committed slices. A future-owned gate is not
required before its owning slice, and no future surface may be satisfied by a
stub or placeholder. G2-C6 alone must pass the complete final implementation
profile. Independent audit and closure synchronization occur only after G2-C6.

The cumulative activation map is exact:

- G2-C1 activates structural types/schemas; scalar, identity, digest, and time
  laws; local profile structure; generic ABI vocabulary; the C1 function and
  signature subset; and the immutable pre-facade package boundary.
- G2-C2 additionally activates actual business/BSEP/Replay/G2-A/G2-B sources,
  contextual source validation, and source-substitution negatives.
- G2-C3 additionally activates feasibility, terminal precedence, cost,
  tie-break, proposal, and invalid-source/no-proposal law.
- G2-C4 additionally activates existing Root projection, contextual ABI,
  Transition profile, RouteEligibility, all 74 functions, all 87 package
  attributes, immutable `kernel.__all__`, and the complete import-cycle gate.
- G2-C5 additionally activates the exact ten-case proof, complete negative and
  substitution matrix, two-domain invariance, and zero-operation proof.
- G2-C6 additionally activates Living v1.3, Conformance v0.4, Conformance
  runner v0.3, and the complete final-profile/historical-preservation proof.
- after G2-C6, an independent non-repairing audit and separate checkpoint/status
  synchronization may occur; Gate 2 still remains open.

The existing final gate inventory remains intact as the complete G2-C6 profile:

1. synchronized repository and exact path guard;
2. slice-owned path scope only;
3. exact type field order, thirty-field Root decision, schema metadata, and
   ABI/schema-version agreement;
4. canonical serialization, G2-C identities, source-native identity handling,
   and every exact non-identity SHA rebuild;
5. total structural/contextual validators and exact SourceContext separation;
6. actual business/BSEP/Replay/G2-A/G2-B source validation, the single BSEP
   family digest, exact NO_PACKET values, and three-state context law;
7. request/transaction/Root/domain/time cross-binding;
8. exact ten-row mode matrix and global hard-block/user-input infeasibility;
9. feasibility-before-cost and selection law;
10. invalid-source no-proposal law;
11. existing read-only Root Decision source mapping, exact empty conflict
    geometry, support identities, derived trust profiles, projection reasons,
    and review matrix;
12. one contextual ABI profile, exact artifact IDs, and Stage-A/B/C bundles;
13. one pure six-rule Registry profile, exact TransitionDecision identity, and
    two contextual evaluators;
14. route-eligibility class law and direct-decision-consumption rejection;
15. complete negative/substitution matrix;
16. exact two-domain ten-case proof and zero counters;
17. Living v1.3;
18. Conformance v0.4 and runner v0.3, including base-module import-cycle,
    immutable package `__all__`, 87 direct package attributes, and historical
    guards;
19. independent non-repairing audit;
20. separate closure synchronization without Gate-2 closure.

Codex may run focused tests and bounded deterministic runners. Blanket/full
pytest requires explicit owner re-authorization. If materially necessary, the
owner must receive the exact terminal command and a precise explanation of why
focused evidence is insufficient.

## 26. Final Authorization State

This v0.1.6 preflight is accepted as a planning artifact only. No implementation
has started. G2-C1 requires a later separate explicit owner authorization, and
no accepted preflight field self-authorizes code changes.

```text
document_status=PREFLIGHT
document_revision=v0.1.6
guardian_review_status=ACCEPTED
TOTAL_G2C_TYPE_COUNT=13
SERIALIZED_IDENTITY_TYPE_COUNT=12
RUNTIME_ONLY_SOURCE_CONTEXT_TYPE_COUNT=1
LOCAL_MODE_PROFILE_COUNT=8
ROUTER_INPUT_FIELD_COUNT=10
CANONICAL_MODE_COUNT=10
CANONICAL_SCENARIO_COUNT=10
ROOT_REVIEW_INPUT_FIELD_COUNT=21
ROOT_DECISION_FIELD_COUNT=30
PUBLIC_G2C_FUNCTION_COUNT=74
PUBLIC_G2C_REASON_COUNT=100
REQUIRED_ADDITIVE_MUTATION_PATH_COUNT=11
DIRECT_PACKAGE_G2C_ATTRIBUTE_COUNT=87
PACKAGE_FACADE_FIRST_AVAILABLE_SLICE=G2-C4
PACKAGE_FACADE_MUTATION_COUNT=1
TRANSITION_PROFILE_FUNCTIONS_FIRST_AVAILABLE_SLICE=G2-C4
FUTURE_FUNCTION_STUBS_ALLOWED=false
G2C1_REQUIRES_FINAL_PACKAGE_FACADE=false
G2C2_MUTATES_KERNEL_PACKAGE_FACADE=false
G2C3_MUTATES_KERNEL_PACKAGE_FACADE=false
G2C4_MUTATES_KERNEL_PACKAGE_FACADE=true
G2C6_VERIFIES_KERNEL_PACKAGE_FACADE=true
VALIDATION_GROUP_3_STAGED=true
SLICE_ACCEPTANCE_CUMULATIVE=true
FINAL_COMPLETE_PROFILE_REQUIRED_AT_G2C6=true
EXACT_SLICE_COUNT=6
EXACT_VALIDATION_GROUP_COUNT=22
REQUEST_AND_TRANSACTION_DISTINCT=true
ACTUAL_BUSINESS_REQUEST_BOUND=true
ACTUAL_STRUCTURED_RATIONALE_BOUND=true
SOURCE_BOUND_ROUTING_REQUIRED=true
SOURCE_FREE_PASS_REJECTED=true
INVALID_SOURCE_CREATES_PROPOSAL=false
MODE_SPECIFIC_ROOT_LOCAL_PROFILES=true
STANDALONE_COST_TYPE_REMOVED=true
ONE_KERNEL_ABI_FAMILY=true
ONE_TRANSITION_REGISTRY_FAMILY=true
ONE_ROOT_DECISION_LAW=true
CALLER_SUPPLIED_TRANSITION_GUARDS_FORBIDDEN=true
ROUTE_ELIGIBILITY_DISTINGUISHES_SHORTCUT_AND_TOPOLOGY=true
ROOT_REVIEW_CONFLICT_IDS_EXACT=true
ROOT_SOURCE_PROBE_PASS=true
BSEP_SOURCE_FAMILY_SHA_SINGLE_LAW=true
BSEP_SOURCE_CROSS_VALIDATION_FROZEN=true
G2A_NO_PACKET_MATRIX_FROZEN=true
G2B_STATE_MATRIX_FROZEN=true
MEMORY_INFORMED_REQUIRES_G2B_CONTEXT=true
REQUEST_CLASS_ROUTING_AUTHORITY=false
SCOPE_CLASS_ROUTING_AUTHORITY=false
RISK_CLASS_ROUTING_AUTHORITY=false
MODE_PROFILE_VALID_REASONS_EXCLUDE_COST_INVALID=true
HARD_BLOCK_GLOBAL_FEASIBILITY_FROZEN=true
USER_INPUT_GLOBAL_FEASIBILITY_FROZEN=true
FEASIBILITY_ROW_DERIVATION_FROZEN=true
PROPOSAL_DERIVED_FIELD_LAWS_FROZEN=true
ROOT_PROJECTION_REASONS_SERIALIZED=true
KERNEL_PACKAGE_ALL_UNCHANGED=true
G2C_PREFLIGHT_ACCEPTED=true
G2C_IMPLEMENTATION_AUTHORIZED=false
G2C_IMPLEMENTATION_STARTED=false
GATE2_CLOSED=false
R_IP1_BLOCKS_G2C_THROUGH_G2F=false
PUBLICATION_BEFORE_GATE6_ALLOWED=false
PUBLIC_RELEASE_CLAIMED=false
REAL_WORLD_EFFECTS=0
```
