# Hedgehog OS Two-Domain All-Real Sealed Evidence Program v0.1
## A2 Airline Seal Source-Agnostic Preflight

document_id: two_domain_all_real_sealed_evidence_program_v01_a2_airline_seal_preflight
document_version: v0.4
document_status: BLOCKED_PENDING_ACCEPTED_ATTEMPT_04
local_packageability_implementation_gate: READY_FOR_REVIEW
official_publication_gate: BLOCKED_PENDING_ACCEPTED_ATTEMPT_04
governing_repository_head: 3d82573a6f0f8891a81a7bad6d1c9b667448c0ae
package_provider_network_gemini_effect_counts: 0 / 0 / 0 / 0
anchor_provider_network_gemini_effect_counts: 0 / 0 / 0 / 0
replay_provider_network_gemini_effect_counts: 0 / 0 / 0 / 0
full_repository_pytest: NOT_RUN

## 1. Decision

Official Airline A2 Package, Anchor, and Replay publication is blocked until a
separately accepted Airline Attempt 04 contains the complete persisted
`AirlineTicketPurchaseCorridorRunReportV01` and every other typed source
required by the frozen Airline adapter.

The A2 architecture has two strictly discriminated modes:

1. `LOCAL_NONPUBLICATION_PACKAGEABILITY`, using only a
   `LOCAL_NONPUBLICATION_SOURCE`; and
2. `OFFICIAL_ATTEMPT_04_A2`, using only an `OFFICIAL_ACCEPTED_SOURCE`.

The source variants are closed immutable types. They are not one dictionary,
one dataclass with optional acceptance fields, or one object whose meaning is
inferred from paths. A local source can never be converted, promoted, cast, or
filled into an official source.

The shared R1 Package, Anchor, and Replay CLIs remain fixture-only and
ineligible for official A2. Both A2 Package modes exercise the frozen shared
typed Package API with `fixture_disposable=False`; the local mode remains
nonpublication because its source type, identities, output law, and eligibility
are different from the official mode.

## 2. Historical Boundary

Accepted Airline Attempt 03 remains immutable genuine `CLOSED_PASS` execution
evidence. The Attempt 03 read-only forensic verdict found no complete stored
`AirlineTicketPurchaseCorridorRunReportV01` across 72 accepted inventory rows,
35 inventory JSON files, and three accepted metadata JSON files. Attempt 03 is
`A2_SOURCE_INCOMPLETE` only for typed packaging-source sufficiency.

Attempt 03 is immutable historical predecessor evidence explaining why a new
complete source attempt is required. It is not an official A2 content source.
No Attempt 03 field may be repaired, inferred, combined, synthesized, or
reconstructed for A2.

## 3. Closed Source Variants

### 3.1 LOCAL_NONPUBLICATION_SOURCE

The future immutable type is
`AirlineA2LocalNonpublicationSourceV01`. Its exact fields and types are:

| Field | Exact type and law |
| --- | --- |
| `source_variant` | `Literal["LOCAL_NONPUBLICATION_SOURCE"]` |
| `source_identity_id` | 64-character lowercase SHA-256 identity |
| `attempt_number` | exact `int`, value `4` |
| `attempt_id` | non-empty temporary Attempt 04 identity |
| `execution_head` | exact 40-character source execution head |
| `implementation_content_sha256` | canonical digest from Section 9.2 |
| `attempt_identity_sha256` | 64-character lowercase SHA-256 |
| `private_inventory_sha256` | 64-character lowercase SHA-256 |
| `private_inventory_digest` | 64-character lowercase SHA-256 |
| `generation_gate_sha256` | 64-character lowercase SHA-256 |
| `corridor_archive_logical_name` | exact `raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json` |
| `corridor_archive_sha256` | 64-character lowercase SHA-256 |
| `corridor_archive_byte_count` | exact positive `int` |
| `safe_report_logical_name` | exact literal `safe-report-v01.json`; derived, never caller-selected |
| `safe_report_sha256` | 64-character lowercase SHA-256 |
| `safe_report_byte_count` | exact positive `int` |
| `safe_execution_id` | local safe projection identity |
| `execution_mode` | `Literal["simulated_real"]` |
| `safe_execution_compatibility_provider_mode` | `Literal["real_provider"]`, local safe-object compatibility geometry only; never the shared attempt provider mode |
| `model_id` | `Literal["gemini-2.5-flash"]` |
| `provider_application_call_mode` | `Literal["json_mime_no_response_schema_single_application_call"]` |
| `actor_ids` | exact ordered tuple of the frozen twelve actor IDs |
| `wrapper_callback_observed_count` | exact `int`, value `12` |
| `provider_callback_started_count` | exact source-shaped `int`, value `12` |
| `provider_callback_completed_count` | exact source-shaped `int`, value `12` |
| `collector_invocation_count` | exact `int`, value `1` |
| `deterministic_airline_collection_count` | exact `int`, value `1` |
| `ticket_purchase_corridor_execution_count` | exact `int`, value `1` |
| `airline_transaction_artifact_ledger_collection_count` | exact `int`, value `1` |
| `airline_crypto_artifact_seal_collection_count` | exact `int`, value `1` |
| `outbound_provider_sdk_call_count` | exact `int`, value `0` |
| `outbound_network_call_count` | exact `int`, value `0` |
| `outbound_gemini_call_count` | exact `int`, value `0` |
| `real_world_effects_count` | exact `int`, value `0` |
| `official_evidence_eligible` | exact `bool`, value `false` |
| `validation_errors` | exact empty `tuple[str, ...]` |

This type contains no accepted-audit path, accepted-audit hash, accepted audit
disposition, official acceptance claim, null acceptance placeholder, or
sentinel official path. Its builder and projection are:

```text
build_airline_a2_local_nonpublication_source_v01(*, every non-derived runtime
field above) -> AirlineA2LocalNonpublicationSourceV01
validate_airline_a2_local_nonpublication_source_v01(
    source: object,
) -> tuple[str, ...]
airline_a2_local_nonpublication_source_to_plain_dict_v01(
    source: AirlineA2LocalNonpublicationSourceV01,
) -> dict[str, object]
```

The builder derives `source_variant`, `source_identity_id`, `attempt_number`,
`corridor_archive_logical_name`, `safe_report_logical_name`, `execution_mode`,
`model_id`, `provider_application_call_mode`, the fixed geometry constants,
`official_evidence_eligible`, and empty validation errors. In particular,
`safe_report_logical_name` is never an argument.

Only the local packageability Process B path uses this type. The public parent
API accepts no source object, and the official Package/member builder rejects
this type by exact type before constructing any SafeMember. There is no
conversion function from this type to the official type.

The local adapter entry point constructs a valid shared
`DomainEvidenceProjectionV01` with this exact law:

| Projection field | Exact local value |
| --- | --- |
| S1 evidence class | `EXECUTED_DETERMINISTIC_RUNTIME` |
| S2 evidence class | `EXECUTED_DETERMINISTIC_RUNTIME` |
| S1 observed provider/network/Gemini counts | `0 / 0 / 0` |
| S2 observed provider/network/Gemini counts | `0 / 0 / 0` |
| attempt `provider_mode` | `deterministic_fixture` |
| attempt `provider_call_budget` | `0` |
| attempt `expected_actor_count` | `12` |
| source provider/network/Gemini counts | `0 / 0 / 0` |
| projection provider/network/Gemini counts | `0 / 0 / 0` |
| created authority/permission/effects | `0 / 0 / 0` |
| required limitation ref | `limitation:local_simulated_real_compatibility_geometry_permanently_nonpublication` |

S3, S4, S5, and S6 retain the truthful `ROOT_DECISION_EVIDENCE`,
`CORRIDOR_EVIDENCE`, `CRYPTOGRAPHIC_INTEGRITY`, and `REPLAY_EVIDENCE`
classes. The compatibility fields in `LOCAL_NONPUBLICATION_SOURCE` may record
twelve injected callbacks, starts, and completions, but those values never map
to `SafeSourceRecordV01.observed_provider_call_count`,
`observed_network_call_count`, `observed_gemini_call_count`, or any shared
projection call counter.

The `LOCAL_NONPUBLICATION_SOURCE` and `OFFICIAL_ACCEPTED_SOURCE` strings are
source-variant discriminants. They are never evidence classes and are never
passed as an `evidence_class` value.

### 3.2 OFFICIAL_ACCEPTED_SOURCE

The future immutable type is `AirlineA2OfficialAcceptedSourceV01`. Its exact
fields and types are:

| Field | Exact type and law |
| --- | --- |
| `source_variant` | `Literal["OFFICIAL_ACCEPTED_SOURCE"]` |
| `source_identity_id` | 64-character lowercase SHA-256 identity |
| `attempt_number` | exact `int`, value `4` |
| `attempt_id` | exact independently audited Attempt 04 ID |
| `execution_head` | exact committed Attempt 04 execution head |
| `attempt_identity_sha256` | exact accepted identity-document SHA-256 |
| `private_inventory_sha256` | exact accepted inventory-document SHA-256 |
| `private_inventory_digest` | exact accepted aggregate inventory digest |
| `generation_gate_sha256` | exact accepted generation-gate SHA-256 |
| `corridor_archive_logical_name` | exact `raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json` |
| `corridor_archive_sha256` | exact accepted archive SHA-256 |
| `corridor_archive_byte_count` | exact accepted positive `int` |
| `public_safe_report_path` | exact committed repository-relative Attempt 04 safe-report path |
| `public_safe_report_sha256` | exact committed safe-report SHA-256 |
| `public_safe_report_byte_count` | exact committed positive `int` |
| `safe_execution_id` | exact accepted safe execution ID |
| `generation_audit_path` | exact committed repository-relative Attempt 04 audit path |
| `generation_audit_sha256` | exact committed audit SHA-256 |
| `accepted_audit_status` | `Literal["CLOSED_PASS"]` |
| `accepted_audit_disposition` | `Literal["ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE"]` |
| `provider_mode` | `Literal["real_provider"]` |
| `model_id` | `Literal["gemini-2.5-flash"]` |
| `provider_application_call_mode` | `Literal["json_mime_no_response_schema_single_application_call"]` |
| `actor_ids` | exact ordered tuple of the frozen twelve actor IDs |
| `wrapper_callback_observed_count` | exact `int`, value `12` |
| `provider_callback_started_count` | exact `int`, value `12` |
| `provider_callback_completed_count` | exact `int`, value `12` |
| `provider_call_count` | exact `int`, value `12` |
| `network_call_count` | exact `int`, value `12` |
| `gemini_call_count` | exact `int`, value `12` |
| `collector_invocation_count` | exact `int`, value `1` |
| `deterministic_airline_collection_count` | exact `int`, value `1` |
| `ticket_purchase_corridor_execution_count` | exact `int`, value `1` |
| `airline_transaction_artifact_ledger_collection_count` | exact `int`, value `1` |
| `airline_crypto_artifact_seal_collection_count` | exact `int`, value `1` |
| `duplicate_actor_call_count` | exact `int`, value `0` |
| `retry_count` | exact `int`, value `0` |
| `fallback_call_count` | exact `int`, value `0` |
| `package_created_count` | exact source-attempt `int`, value `0` |
| `anchor_created_count` | exact source-attempt `int`, value `0` |
| `replay_created_count` | exact source-attempt `int`, value `0` |
| `real_world_effects_count` | exact `int`, value `0` |
| `official_evidence_eligible` | exact `bool`, value `true` |
| `validation_errors` | exact empty `tuple[str, ...]` |

Its exact API is:

```text
build_airline_a2_official_accepted_source_v01(*, every field above except
source_identity_id) -> AirlineA2OfficialAcceptedSourceV01
validate_airline_a2_official_accepted_source_v01(
    source: object,
) -> tuple[str, ...]
airline_a2_official_accepted_source_to_plain_dict_v01(
    source: AirlineA2OfficialAcceptedSourceV01,
) -> dict[str, object]
```

The pure builder validates only already verified exact values and performs no
filesystem or Git access. The official loader in Section 6.8 verifies the exact
Attempt 04 identity, committed execution head, committed safe-report bytes,
committed generation-audit bytes, complete Corridor archive, inventory
geometry, source hashes, audit disposition, audit status, and zero-effect law
before calling the builder. The official entry point rejects a local source,
temporary path, missing audit field, uncommitted report or audit byte, wrong
attempt number, wrong head, or wrong source variant before typed hydration or
SafeMember construction.

Both `accepted_audit_status=CLOSED_PASS` and
`accepted_audit_disposition=ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE`
are mandatory. Those values and `generation_audit_sha256` participate in the
official source identity. Audit acceptance never rewrites source evidence.

### 3.3 Source Identity Formula

For each variant, `source_identity_id` is SHA-256 over canonical JSON with
domain separator:

```text
hedgehog-os:airline-a2-source-identity:v0.1:<source_variant>
```

followed by the Section-5 canonical JSON bytes of every field of that variant
except `source_identity_id`. Source identity contains only source-attempt facts,
accepted report/audit bindings where the official variant requires them, and
local proof facts where the local variant requires them. It contains no future
Package ID, Package root, logical Package ref, package-index path, Manifest ID,
or package-content hash.

Corridor archive acceptance has no validation-identity field. Acceptance
requires canonical stored bytes to equal the hydrated typed report's canonical
bytes plus one LF, exact archive SHA-256 and byte count equality with the
verified private inventory, production
`validate_airline_ticket_purchase_corridor_run_v01` PASS with empty validation
errors, and exact hydrated typed equality. No replacement identity is derived.

## 4. Closed Package Invocation Variants

Package invocation identity is separate from source identity. There are exactly
three closed immutable invocation types. They are not one type with optional
fields, and callers do not choose Package IDs or logical output references.

### 4.1 LOCAL_PRECOMMIT_PACKAGE_INVOCATION

The immutable type is `AirlineA2LocalPrecommitPackageInvocationV01`:

| Field | Exact type and law |
| --- | --- |
| `invocation_variant` | `Literal["LOCAL_PRECOMMIT_PACKAGE_INVOCATION"]` |
| `package_invocation_id` | derived 64-character lowercase SHA-256 |
| `base_head` | strict lowercase 40-character Git hash verified as the current base HEAD |
| `implementation_content_sha256` | exact twelve-path content SHA-256 from Section 9.2 |
| `local_source_identity_id` | exact validated `LOCAL_NONPUBLICATION_SOURCE` identity |
| `package_id` | deterministically derived exact string |
| `logical_package_ref` | deterministically derived exact string |
| `package_output_ref` | deterministically derived invocation-local logical ref |
| `package_index_output_ref` | deterministically derived invocation-local logical ref |

This type contains no committed implementation-head field and no publication
head or publication claim. Its domain separator is:

```text
hedgehog-os:airline-a2-package-invocation:v0.1:LOCAL_PRECOMMIT_PACKAGE_INVOCATION
```

The derived fields are exactly:

```text
package_id = airline_a2_local_precommit_package:<local_source_identity_id>:<implementation_content_sha256>
logical_package_ref = airline/a2/local/precommit/<local_source_identity_id>/<implementation_content_sha256>
package_output_ref = <logical_package_ref>/package
package_index_output_ref = <logical_package_ref>/package-index
```

### 4.2 LOCAL_COMMITTED_PACKAGE_INVOCATION

The immutable type is `AirlineA2LocalCommittedPackageInvocationV01`:

| Field | Exact type and law |
| --- | --- |
| `invocation_variant` | `Literal["LOCAL_COMMITTED_PACKAGE_INVOCATION"]` |
| `package_invocation_id` | derived 64-character lowercase SHA-256 |
| `committed_head` | strict lowercase 40-character clean I1 HEAD |
| `origin_main_head` | strict lowercase 40-character hash exactly equal to `committed_head` |
| `implementation_content_sha256` | same exact twelve-path digest used by the precommit gate |
| `local_source_identity_id` | exact validated `LOCAL_NONPUBLICATION_SOURCE` identity |
| `package_id` | deterministically derived exact string |
| `logical_package_ref` | deterministically derived exact string |
| `package_output_ref` | deterministically derived invocation-local logical ref |
| `package_index_output_ref` | deterministically derived invocation-local logical ref |
| `official_publication_claimed` | `Literal[False]` |

This type contains no publication-base head. Its domain separator is:

```text
hedgehog-os:airline-a2-package-invocation:v0.1:LOCAL_COMMITTED_PACKAGE_INVOCATION
```

The derived fields are exactly:

```text
package_id = airline_a2_local_committed_package:<local_source_identity_id>:<committed_head>:<implementation_content_sha256>
logical_package_ref = airline/a2/local/committed/<local_source_identity_id>/<committed_head>/<implementation_content_sha256>
package_output_ref = <logical_package_ref>/package
package_index_output_ref = <logical_package_ref>/package-index
```

### 4.3 OFFICIAL_PACKAGE_INVOCATION

The immutable type is `AirlineA2OfficialPackageInvocationV01`:

| Field | Exact type and law |
| --- | --- |
| `invocation_variant` | `Literal["OFFICIAL_PACKAGE_INVOCATION"]` |
| `package_invocation_id` | derived 64-character lowercase SHA-256 |
| `official_source_identity_id` | exact validated `OFFICIAL_ACCEPTED_SOURCE` identity |
| `implementation_head` | exact Attempt 04 execution head and committed I1 implementation head |
| `publication_base_head` | strict lowercase 40-character clean publication-base HEAD |
| `package_id` | deterministically derived exact string |
| `logical_package_ref` | deterministically derived exact string |
| `package_output_ref` | exact repository-relative official Package root |
| `package_index_output_ref` | exact repository-relative official package-index output |

Its domain separator is:

```text
hedgehog-os:airline-a2-package-invocation:v0.1:OFFICIAL_PACKAGE_INVOCATION
```

The derived fields are exactly:

```text
package_id = airline_a2_official_package:<official_source_identity_id>:<publication_base_head>
logical_package_ref = airline/a2/official/attempt-04/<official_source_identity_id>/<publication_base_head>
package_output_ref = docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01
package_index_output_ref = docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_package_index_v01.json
```

### 4.4 Invocation Identity and APIs

For each variant, `package_invocation_id` is SHA-256 over its ASCII domain
separator, one NUL byte, and the Section-5 canonical JSON bytes of every field
except `package_invocation_id`, under canonical lexicographic key order. All
derived fields are computed before that hash. The exact APIs are:

```text
build_airline_a2_local_precommit_package_invocation_v01(
    *, base_head: str, implementation_content_sha256: str,
    local_source_identity_id: str,
) -> AirlineA2LocalPrecommitPackageInvocationV01
validate_airline_a2_local_precommit_package_invocation_v01(
    invocation: object,
) -> tuple[str, ...]
airline_a2_local_precommit_package_invocation_to_plain_dict_v01(
    invocation: AirlineA2LocalPrecommitPackageInvocationV01,
) -> dict[str, object]
build_airline_a2_local_committed_package_invocation_v01(
    *, committed_head: str, origin_main_head: str,
    implementation_content_sha256: str, local_source_identity_id: str,
) -> AirlineA2LocalCommittedPackageInvocationV01
validate_airline_a2_local_committed_package_invocation_v01(
    invocation: object,
) -> tuple[str, ...]
airline_a2_local_committed_package_invocation_to_plain_dict_v01(
    invocation: AirlineA2LocalCommittedPackageInvocationV01,
) -> dict[str, object]
build_airline_a2_official_package_invocation_v01(
    *, official_source_identity_id: str, implementation_head: str,
    publication_base_head: str,
) -> AirlineA2OfficialPackageInvocationV01
validate_airline_a2_official_package_invocation_v01(
    invocation: object,
) -> tuple[str, ...]
airline_a2_official_package_invocation_to_plain_dict_v01(
    invocation: AirlineA2OfficialPackageInvocationV01,
) -> dict[str, object]
```

Equal source identity, equal canonical typed-context bytes, and equal invocation
variant bytes must produce equal adapter result, `DomainEvidenceProjectionV01`,
SafeFiles, Manifest ID, and package-content hash.

## 5. Exact Evidence and Source-Record Law

Only evidence classes frozen by the shared Section-26 profile are allowed.
No class may be invented or aliased.

### 5.1 Official Four-Member Package

| Member | Evidence class | Exact content law |
| --- | --- | --- |
| `evidence/01-airline-safe-execution-report-v01.json` | `EXECUTED_LIVE_RUNTIME` | byte-identical committed accepted Attempt 04 public safe report |
| `evidence/02-airline-source-lineage-v01.json` | `HISTORICAL_REFERENCE` | canonical references only to the committed Attempt 04 safe report, committed generation audit, and immutable source identities; introduces no execution claim |
| `evidence/03-airline-a2-typed-context-v01.json` | `EXECUTED_DETERMINISTIC_RUNTIME` | freshly generated deterministic typed reconstruction context |
| `evidence/04-airline-sealed-evidence-adapter-result-v01.json` | `EXECUTED_DETERMINISTIC_RUNTIME` | freshly generated deterministic adapter and domain-projection result |

### 5.2 Local Nonpublication Four-Member Package

All four local members use `EXECUTED_DETERMINISTIC_RUNTIME`. Member 01 is an
explicit simulated-real safe projection and is not live evidence. Member 02 is
local deterministic nonpublication lineage, contains no accepted-audit path,
hash, disposition, or official claim, and binds the local source variant.
Members 03 and 04 are the deterministic typed context and adapter/domain
projection. All local bytes and identities are permanently ineligible for
official publication.

All members use `application/json`, pass the shared secret scanner, use exactly
one terminal LF, and use the source-record selections below.

### 5.3 Frozen Source Records and Selections

The exact six records, in adapter constructor order, are:

| Symbol | Exact `source_type` | Official source-record evidence class |
| --- | --- | --- |
| `S1` | `airline_live_execution_safe_projection` | `EXECUTED_LIVE_RUNTIME` |
| `S2` | `airline_bsep_safe_projection` | `LIVE_PROVIDER_SAFE_PROJECTION` |
| `S3` | `airline_three_root_final_evidence` | `ROOT_DECISION_EVIDENCE` |
| `S4` | `airline_corridor_and_receipt_evidence` | `CORRIDOR_EVIDENCE` |
| `S5` | `airline_ledger_and_crypto_evidence` | `CRYPTOGRAPHIC_INTEGRITY` |
| `S6` | `airline_replay_and_gate1_kernel_evidence` | `REPLAY_EVIDENCE` |

`Sx` always means the exact validated `source_record_id` produced for that
record. It is never a caller-supplied label. SafeMember selections are:

| Member | Ordered `source_record_ids` |
| --- | --- |
| member 01 | `(S1,)` |
| member 02 | `(S1, S5, S6)` |
| member 03 | `(S1, S2, S3, S4, S5, S6)` |
| member 04 | `(S1, S2, S3, S4, S5, S6)` |

No member may add, omit, reorder, replace, or accept caller-provided source
record IDs.

The local adapter entry point uses `EXECUTED_DETERMINISTIC_RUNTIME` for both S1
and S2 and sets both records' observed provider, network, and Gemini counts to
zero. The legacy and official adapter paths retain the frozen official classes
and official `12 / 12 / 12` source-call law above.

In official mode the shared attempt identity uses `provider_mode=real_provider`,
`provider_call_budget=12`, and `expected_actor_count=12`. S1/S2 and the complete
source-record set produce exact source provider/network/Gemini counts
`12 / 12 / 12`; projection provider/network/Gemini counts remain `0 / 0 / 0`
because A2 projection itself makes no outbound call.

### 5.4 Exact Member 02 Schemas

Member 02 has two closed schemas. Keys appear below in exact canonical
lexicographic byte order. The local schema is:

```text
limitations: list[str]
lineage_id: str
lineage_version: Literal["v0.1"]
package_invocation_identity: exact plain projection of one local invocation variant
safe_report_binding: object
source_identity: exact plain projection of AirlineA2LocalNonpublicationSourceV01
source_record_ids: list[str]
source_variant: Literal["LOCAL_NONPUBLICATION_SOURCE"]
```

The local `safe_report_binding` has exactly these keys:

```text
byte_count: int
logical_name: str
official_evidence_eligible: Literal[False]
safe_execution_id: str
sha256: str
```

Its `source_record_ids` is exactly `[S1, S5, S6]`. Its `limitations` equals
the exact ordered local tuple in Section 6.7, including
`limitation:local_simulated_real_compatibility_geometry_permanently_nonpublication`.
It contains no `audit_binding`, audit key, null audit placeholder, accepted
disposition, or official claim.

The official schema is:

```text
audit_binding: object
limitations: list[str]
lineage_id: str
lineage_version: Literal["v0.1"]
safe_report_binding: object
source_identity: exact plain projection of AirlineA2OfficialAcceptedSourceV01
source_record_ids: list[str]
source_variant: Literal["OFFICIAL_ACCEPTED_SOURCE"]
```

The official `audit_binding` and `safe_report_binding` have exactly:

```text
audit_binding:
  accepted_audit_disposition: Literal["ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE"]
  accepted_audit_status: Literal["CLOSED_PASS"]
  repository_relative_path: str
  sha256: str
safe_report_binding:
  byte_count: int
  official_evidence_eligible: Literal[True]
  repository_relative_path: str
  safe_execution_id: str
  sha256: str
```

Its `source_record_ids` is exactly `[S1, S5, S6]`; `limitations` equals the
exact ordered official tuple in Section 6.7. Member 02 introduces no
new execution claim. It contains no Package ID, Package invocation ID, logical
or physical output ref, publication head, Manifest fact, or package-content
fact. Its identity covers only the accepted Attempt-04 source identity,
committed safe-report binding, committed generation-audit binding, exact
S1/S5/S6 source-record IDs, historical limitations, lineage version, and its
zeroed identity slot.

Official Package invocation identity is instead bound by members 03 and 04,
the Package index, the Manifest, and Package-content identity. Local member 02
remains `EXECUTED_DETERMINISTIC_RUNTIME` and retains its local invocation
binding.

The lineage identity domains are respectively:

```text
hedgehog-os:airline-a2-member-02-lineage:v0.1:LOCAL_NONPUBLICATION_SOURCE
hedgehog-os:airline-a2-member-02-lineage:v0.1:OFFICIAL_ACCEPTED_SOURCE
```

For identity derivation, `lineage_id` is replaced by exactly 64 ASCII zeroes;
SHA-256 covers the ASCII domain, one NUL byte, and the canonical JSON bytes of
that zeroed object without terminal LF. The resulting lowercase digest replaces
the zero slot.

### 5.5 Exact Member 03 Typed-Context Schema

Member 03 has this exact top-level key set in canonical lexicographic order:

```text
crypto_source_projection: object
external_operation_counts: object
historical_replay_input_projection: object
historical_replay_report_projection: object
kernel_adapter_projection: object
ledger_source_projection: object
package_invocation_id: str
reconstruction_geometry: object
safe_execution_projection: object
source_identity_id: str
source_variant: Literal["LOCAL_NONPUBLICATION_SOURCE", "OFFICIAL_ACCEPTED_SOURCE"]
typed_context_id: str
typed_context_version: Literal["v0.1"]
validation_errors: list[str]
```

`safe_execution_projection` is the exact canonical plain projection of
`AirlineSafeExecutionProjectionV01`, with exactly these keys:

```text
actor_ids, actor_safe_projection_hashes, actor_validation_statuses,
airline_root_final_hash, airline_root_final_id, bank_root_final_hash,
bank_root_final_id, bsep_packet_id, bsep_projection_hashes,
bsep_projection_refs, bsep_safe_hash, client_root_final_hash,
client_root_final_id, corridor_report_hash, corridor_report_id,
execution_head, gemini_call_count, model_id, network_call_count,
provider_call_count, provider_mode, raw_prompt_included,
raw_provider_response_included, real_world_effects_count, receipt_ids,
receipt_safe_hashes, report_id, run_id, safe_execution_id,
safe_execution_version, secret_scan_passed, selected_offer_id,
source_final_status, source_task_id, status, transaction_id, validation_errors
```

`ledger_source_projection` has exactly two keys, `ledger_item` and
`source_bundle`. `ledger_item` is the canonical plain projection of the exact
validated `AirlineTransactionArtifactLedgerV01`, including its 19 ordered
entries. `source_bundle` has exactly the following keys, with every nested
object represented by its committed canonical plain projection and every tuple
represented as an order-preserving JSON array:

```text
airline_bsep_projection, airline_root_final, auxiliary_observation_refs,
bank_bsep_projection, bank_root_final, causal_report, client_bsep_projection,
client_root_final, corridor_report, cross_root_bsep_projection,
expected_source_refs, hold_packet, hold_receipt, mock_purchase_receipt,
mock_ticket_receipt, offer_packet, payment_authorization_ref,
purchase_approval_evidence, purchase_intent, source_bundle_id,
source_validation_refs, ticket_issue_intent, transaction_id
```

`crypto_source_projection` has exactly two keys: `collection_result`, the
complete canonical plain projection of
`AirlineCryptoArtifactSealCollectionResultV01` using the exact field set in
Section 6.3, and `ordered_source_files`, the exact nine source-byte rows in
committed Crypto order.

`historical_replay_input_projection` has exactly:

```text
accepted_ledger_audit, envelope, expected_manifest_core_hash,
fresh_anchored_verification_report, ledger_item, ordered_source_files,
source_package_ref, stored_verification_report
```

`historical_replay_report_projection` is the complete canonical plain
projection of `AirlineSealedTraceReplayReportV01` with exactly the field set in
Section 6.5. `kernel_adapter_projection` is the complete canonical plain
projection of `AirlineKernelAdapterResultV01` with exactly the field set in
Section 6.6. No projection accepts an extra key.

Every `ordered_source_files` item has exactly these keys in canonical order:

```text
base64: str
byte_count: int
logical_name: str
sha256: str
```

`base64` is RFC 4648 standard base64 with required padding, ASCII only, and no
whitespace. Hydration uses strict base64 decoding, requires re-encoding to the
identical string, verifies exact byte count and lowercase SHA-256, and preserves
the array order. A Python `bytes` object, object representation, pickle, or
implicit UTF-8 conversion is forbidden.

`reconstruction_geometry` has exactly:

```text
actor_count: 12
corridor_delegation_count: 8
corridor_phase_count: 5
corridor_transition_count: 4
critical_file_count: 11
crypto_source_file_count: 9
dependency_edge_count: 29
ledger_entry_count: 19
replay_timeline_row_count: 19
root_final_count: 3
source_record_count: 6
```

`external_operation_counts` has exactly:

```text
a2_effect_call_count: 0
a2_gemini_call_count: 0
a2_network_call_count: 0
a2_provider_sdk_call_count: 0
```

`validation_errors` is exactly `[]`. Member-03 reread must reconstruct all six
typed inputs listed in Section 6, rerun every named committed validator, and
produce typed values equal to the pre-serialization values. This equality is a
required test, not an inference from matching hashes.

Its identity domain is:

```text
hedgehog-os:airline-a2-member-03-typed-context:v0.1:<source_variant>
```

For identity derivation, `typed_context_id` is replaced by 64 ASCII zeroes and
the same domain-plus-NUL hash law is applied.

### 5.6 Exact Member 04 Adapter Projection Schema

Member 04 has exactly these top-level keys in canonical lexicographic order:

```text
adapter_projection_id: str
adapter_projection_version: Literal["v0.1"]
adapter_result: object
domain_evidence_projection: object
package_invocation_id: str
source_identity_id: str
source_record_ids: list[str]
source_variant: Literal["LOCAL_NONPUBLICATION_SOURCE", "OFFICIAL_ACCEPTED_SOURCE"]
validation_result: object
zero_effect_geometry: object
```

`adapter_result` is the exact canonical plain projection of
`AirlineSealedEvidencePackageAdapterResultV01` and has exactly:

```text
action_created_count, adapter_gemini_call_count, adapter_network_call_count,
adapter_provider_call_count, adapter_result_id, adapter_version,
artifact_record_count, causal_ref_count, created_authority_count,
created_permission_count, critical_file_count, crypto_manifest_core_hash,
domain_projection, final_output_created_count, kernel_adapter_id,
kernel_artifact_ref_count, kernel_manifest_hash, ledger_id,
real_world_effects_count, receipt_created_count, replay_row_count,
root_final_count, safe_execution_id, selected_offer_id, source_bundle_id,
source_file_count, source_package_ref, source_record_count, source_replay_id,
status, transaction_id, validation_errors
```

`domain_evidence_projection` is the exact canonical plain projection of the
same validated `DomainEvidenceProjectionV01` embedded in `adapter_result` and
has exactly:

```text
artifact_records, attempt_identity, causal_consumption_refs,
created_authority_count, created_permission_count, domain_execution_identity,
evidence_refs, kernel_artifact_refs, limitation_refs, programme_identity,
projection_gemini_call_count, projection_id, projection_network_call_count,
projection_provider_call_count, real_world_effects_count,
source_gemini_call_count, source_network_call_count,
source_provider_call_count, source_records, status
```

The two domain-projection objects must be equal. `source_record_ids` is exactly
`[S1, S2, S3, S4, S5, S6]`. `validation_result` has exactly:

```text
adapter_status: Literal["PASS"]
adapter_validation_errors: list[str]
domain_projection_status: Literal["PASS"]
domain_projection_validation_errors: list[str]
```

Both error arrays are empty. `zero_effect_geometry` has exactly:

```text
action_created_count: 0
created_authority_count: 0
created_permission_count: 0
final_output_created_count: 0
projection_created_authority_count: 0
projection_created_permission_count: 0
projection_real_world_effects_count: 0
real_world_effects_count: 0
receipt_created_count: 0
```

Its identity domain is:

```text
hedgehog-os:airline-a2-member-04-adapter-projection:v0.1:<source_variant>
```

For identity derivation, `adapter_projection_id` is replaced by 64 ASCII
zeroes and the same domain-plus-NUL hash law is applied.

### 5.7 Canonical Bytes and SafeFile Binding

Members 02, 03, and 04 use strict JSON-compatible values only. Their canonical
JSON algorithm is exactly `json.dumps(value, ensure_ascii=False,
sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`.
The stored content is those bytes plus exactly one LF. There is no BOM, NUL,
CR, trailing whitespace, trailing object, duplicate key, non-finite number, or
surrogate. Arrays preserve the normative order specified above.

Each member's `byte_count` is the length of the final bytes including LF, and
its content SHA-256 is over those exact final bytes. Each member passes the
shared secret scanner. Descriptor-bound reread must prove exact inode, mode,
bytes, canonical parse, identity recomputation, hash, byte count, schema, and
semantic equality. Member 01 remains byte-identical to its mode-appropriate
safe report; it is not recanonicalized.

## 6. Six Exact Adapter Inputs and Hydration Map

The A2 typed context contains exactly these six values in this order:

1. `AirlineSafeExecutionProjectionV01`;
2. `AirlineTransactionArtifactLedgerSourceBundleV01`;
3. `AirlineCryptoArtifactSealCollectionResultV01`;
4. `AirlineSealedTraceReplayInputV01`;
5. `AirlineSealedTraceReplayReportV01`; and
6. `AirlineKernelAdapterResultV01`.

No seventh adapter input, auxiliary untyped context slot, `SimpleNamespace`,
fixture object, default builder, or invented value is permitted.

### 6.1 AirlineSafeExecutionProjectionV01

The mode-appropriate safe report has the closed builder input keys
`execution_head`, `run_id`, `report_id`, `source_task_id`, `transaction_id`,
`selected_offer_id`, `provider_mode`, `model_id`, `source_final_status`,
`actors`, `bsep`, `root_finals`, `corridor`, `receipts`, `counters`,
`raw_prompt_included`, `raw_provider_response_included`,
`secret_scan_passed`, `real_world_effects_count`, and `validation_errors`.

The committed builder
`build_airline_safe_execution_projection_v01` maps those keys exhaustively:

- direct scalar fields: `execution_head`, `run_id`, `report_id`,
  `source_task_id`, `transaction_id`, `selected_offer_id`, `provider_mode`,
  `model_id`, and `source_final_status`;
- twelve ordered actor rows to `actor_ids`,
  `actor_safe_projection_hashes`, and `actor_validation_statuses`;
- BSEP packet and four ordered projections to `bsep_packet_id`,
  `bsep_safe_hash`, `bsep_projection_refs`, and `bsep_projection_hashes`;
- three ordered Root rows to `client_root_final_id`,
  `client_root_final_hash`, `airline_root_final_id`,
  `airline_root_final_hash`, `bank_root_final_id`, and
  `bank_root_final_hash`;
- Corridor and three receipt rows to `corridor_report_id`,
  `corridor_report_hash`, `receipt_ids`, and `receipt_safe_hashes`;
- counters and safety fields to `provider_call_count`, `network_call_count`,
  `gemini_call_count`, `raw_prompt_included`,
  `raw_provider_response_included`, `secret_scan_passed`,
  `real_world_effects_count`, and `validation_errors`; and
- the builder derives only `safe_execution_version`, `status`, and
  `safe_execution_id` under its committed identity law.

Validation and canonical projection use
`validate_airline_safe_execution_projection_v01` and
`airline_safe_execution_projection_to_plain_dict_v01`.

### 6.2 AirlineTransactionArtifactLedgerSourceBundleV01

Every field is sourced as follows:

| Target field or closed field set | Exact source or derivation |
| --- | --- |
| `source_bundle_id` | canonical `run_id:report_id:causal_report.scenario_id` from the validated safe report and `semantic_to_contract_causal_run.json` |
| `transaction_id` | exact equal value in causal run, Corridor report, bridge, deterministic summary, and stored Ledger |
| `expected_source_refs` | exact `AirlineTransactionArtifactLedgerExpectedSourceRefsV01` deterministically derived from `source_bundle_id`, causal report identity, and `corridor_report.run_id` |
| `client_bsep_projection`, `airline_bsep_projection`, `bank_bsep_projection`, `cross_root_bsep_projection` | exact four ordered `AirlineTransactionArtifactLedgerBSEPProjectionSourceV01` values from BSEP packet, validation, side projections, transaction ID, and safe false/zero fields |
| `causal_report` | strict hydration of the complete `semantic_to_contract_causal_run.json` object |
| `offer_packet`, `hold_packet`, `hold_receipt`, `purchase_approval_evidence`, `purchase_intent`, `payment_authorization_ref`, `ticket_issue_intent`, `mock_ticket_receipt`, `mock_purchase_receipt` | exact typed Corridor artifacts from the persisted report contract context and phase evidence refs, cross-bound to the corresponding stored Ledger entry identity and canonical hash input; no value comes from a fixture or free constant |
| `corridor_report` | strict hydration of `raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json` into the existing typed field, never an auxiliary dictionary |
| `client_root_final`, `airline_root_final`, `bank_root_final` | exact three ordered `AirlineTransactionArtifactLedgerRootFinalSourceV01` values from stored Ledger Root-final entries, causal/Corridor refs, transaction ID, and false/zero fields |
| `source_validation_refs` | exact tuple `(expected_source_refs.source_run_ref, expected_source_refs.source_causal_report_ref, expected_source_refs.source_corridor_report_ref)` |
| `auxiliary_observation_refs` | exact committed `EXPECTED_AUXILIARY_OBSERVATION_REFS` after stored Ledger equality proves the same tuple |

Strict hydration uses the committed dataclass constructors for
`AirlineTransactionArtifactLedgerExpectedSourceRefsV01`,
`AirlineTransactionArtifactLedgerBSEPProjectionSourceV01`,
`AirlineTransactionArtifactLedgerRootFinalSourceV01`, every named Corridor
contract type, `AirlineSemanticCausalRunReportV01`, and
`AirlineTransactionArtifactLedgerSourceBundleV01`. It then uses:

- `validate_airline_semantic_causal_run_report_v01`;
- every production Corridor artifact validator;
- `validate_airline_ticket_purchase_corridor_run_v01`;
- `validate_airline_transaction_artifact_ledger_source_bundle_v01`; and
- `build_airline_transaction_artifact_ledger_expected_identity_from_source_v01`.

The expected Ledger identity must validate the strictly hydrated stored
`AirlineTransactionArtifactLedgerV01` through
`validate_airline_transaction_artifact_ledger_v01`. Process B does not collect
or reconstruct a new Ledger.

### 6.3 AirlineCryptoArtifactSealCollectionResultV01

The exact fields are
`collection_status`, `source_bundle_id`, `source_package_ref`,
`transaction_id`, `ledger_id`, `manifest_core_hash`,
`expected_manifest_core_hash`, `source_bundle_validation_report`,
`manifest_core`, `envelope`, `verification_report`,
`source_bytes_unchanged_after_audit`,
`source_bytes_unchanged_after_collection`,
`source_bundle_validation_count`, `manifest_core_collection_count`,
`envelope_collection_count`, `post_collection_snapshot_provider_call_count`,
`verification_count`, `audit_rerun_count`, `ledger_recollection_count`,
`semantic_rerun_count`, `corridor_rerun_count`, `provider_call_count`,
`network_call_count`, `gemini_call_count`,
`collector_created_authority_count`, `collector_created_permission_count`,
`collector_created_action_count`, `real_world_effects_count`, and
`collection_errors`.

Identity, status, hashes, source refs, all stage counters, all zero counters,
and errors come exactly from the validated `summary.json` Crypto integration,
the raw manifest, and the raw verification document. `manifest_core`,
`envelope`, and `verification_report` are strict typed hydration of those two
raw Crypto documents. `source_bundle_validation_report` is reproduced only by
validating the exact stored nine-source bytes, stored Ledger, accepted ledger
audit projection, and expected identity through
`build_airline_crypto_artifact_seal_source_bundle_v01` and
`validate_airline_crypto_artifact_seal_source_bundle_v01`; no Crypto collector
is called.

The result uses the exact
`AirlineCryptoArtifactSealCollectionResultV01` constructor, followed by
`validate_airline_crypto_artifact_seal_collection_result_v01` and
`airline_crypto_artifact_seal_collection_result_to_plain_dict_v01`.

### 6.4 AirlineSealedTraceReplayInputV01

Its exact fields map as follows:

| Field | Exact source or derivation |
| --- | --- |
| `source_package_ref` | validated Crypto manifest/source integration |
| `accepted_ledger_audit` | exact typed projection of the stored accepted Ledger audit facts and the nine accepted source rows |
| `ledger_item` | strictly hydrated stored Ledger, already validated against source-bundle-derived identity |
| `envelope` | strictly hydrated raw Crypto manifest envelope |
| `stored_verification_report` | strictly hydrated raw Crypto verification report |
| `fresh_anchored_verification_report` | deterministic committed Crypto verification over the same envelope, Ledger, exact nine source bytes, and expected manifest hash; this is internal historical adapter context, not an A2 Anchor owner publication |
| `expected_manifest_core_hash` | exact manifest core hash from the validated envelope |
| `ordered_source_files` | exact nine frozen Crypto source logical names and byte strings in committed order |

The accepted audit uses
`AirlineCryptoArtifactSealAcceptedLedgerAuditV01` and
`validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01`. The fresh
verification uses `verify_airline_crypto_artifact_seal_v01` with no network or
external Anchor publication. The replay input uses
`build_airline_sealed_trace_replay_input_v01` and
`validate_airline_sealed_trace_replay_input_v01`.

### 6.5 AirlineSealedTraceReplayReportV01

The complete closed field set is:

```text
replay_status, replay_version, replay_id, source_package_ref, transaction_id,
ledger_id, manifest_core_hash, expected_manifest_core_hash,
stored_verification_status, fresh_anchored_verification_status,
stored_verification_contract_verified,
fresh_anchored_verification_contract_verified, external_anchor_supplied,
external_anchor_verified, signature_mode, signature_verified,
integrity_verified, continuity_verified, ledger_verified,
manifest_binding_verified, artifact_hashes_verified, chain_order_verified,
dependency_graph_verified, root_ownership_verified,
authority_evidence_boundaries_verified, packet_lineage_verified,
receipt_lineage_verified, transaction_identity_verified,
source_refs_verified, secret_boundary_verified, source_bytes_unchanged,
critical_package_bytes_unchanged, timeline_complete,
root_attestation_required, root_attestation_present, source_file_count,
critical_package_file_count, ledger_entry_count, dependency_edge_count,
root_final_count, client_root_final_count, airline_root_final_count,
bank_root_final_count, timeline_row_count, ledger_audit_count,
anchored_verification_count, post_replay_snapshot_provider_call_count,
transaction_rerun_count, semantic_rerun_count, corridor_rerun_count,
ledger_recollection_count, crypto_collection_count, provider_call_count,
network_call_count, gemini_call_count, replay_created_authority_count,
replay_created_permission_count, replay_created_action_count,
replay_created_packet_count, replay_created_receipt_count,
replay_created_final_output_count, real_world_effects_count,
reconstructed_timeline, verification_errors
```

Every field is deterministically produced from the validated replay input and
exact stored package bytes by the committed pure
`verify_airline_sealed_trace_replay_v01` path. It is historical adapter context,
not the future official A2 Replay owner operation. Validation and projection
use `validate_airline_sealed_trace_replay_report_v01` and
`airline_sealed_trace_replay_report_to_plain_dict_v01`. Process B performs no
transaction, semantic, Corridor, Ledger, or Crypto recollection.

### 6.6 AirlineKernelAdapterResultV01

The complete field set is:

```text
adapter_id, adapter_version, transaction_id, selected_offer_id,
source_package_ref, source_replay_id, source_manifest_core_hash,
source_stored_verification_status, source_fresh_verification_status,
source_signature_verified, root_ids, kernel_artifacts, kernel_manifest,
kernel_unanchored_verification, kernel_anchored_verification, kernel_replay,
causal_consumption_refs, ledger_entry_count, dependency_edge_count,
root_final_count, source_file_count, critical_file_count, timeline_row_count,
provider_call_count, network_call_count, gemini_call_count,
real_world_effects_count
```

Every field is derived only from the validated replay input and report by
`build_airline_kernel_adapter_result_v01`. Validation and projection use
`validate_airline_kernel_adapter_result_v01` and
`airline_kernel_adapter_result_to_plain_dict_v01`.

### 6.7 Final Adapter API

The frozen legacy APIs remain byte-for-byte and behaviorally unchanged:

```text
build_airline_sealed_evidence_package_adapter_result_v01
validate_airline_sealed_evidence_package_adapter_result_v01
airline_sealed_evidence_package_adapter_result_to_plain_dict_v01
```

They continue to represent the legacy Attempt-1 identity geometry. No A2 code
changes their parameters, output, validation, or identity. The adapter module
does not import `sealed_evidence_a2_binding_v01`; the A2 binding imports and
maps into the adapter-owned contract below. This dependency direction is
mandatory and prevents a circular import.

The adapter module adds the immutable
`AirlineSealedEvidencePackageAdapterInvocationV01` with exactly these fields:

| Field | Exact type and mode law |
| --- | --- |
| `invocation_mode` | `Literal["LOCAL_NONPUBLICATION", "OFFICIAL_ACCEPTED"]` |
| `attempt_number` | exact `int`, value `4` |
| `package_id` | exact non-empty Package invocation value |
| `logical_package_ref` | exact non-empty Package invocation value |
| `output_directory_ref` | exact non-empty Package invocation value |
| `provider_mode` | local `deterministic_fixture`; official `real_provider` |
| `model_id` | exact `gemini-2.5-flash` |
| `expected_actor_count` | exact `int`, value `12` |
| `provider_call_budget` | local `0`; official `12` |
| `s1_evidence_class` | local `EXECUTED_DETERMINISTIC_RUNTIME`; official `EXECUTED_LIVE_RUNTIME` |
| `s2_evidence_class` | local `EXECUTED_DETERMINISTIC_RUNTIME`; official `LIVE_PROVIDER_SAFE_PROJECTION` |
| `s1_observed_provider_call_count` | local `0`; official `12` |
| `s1_observed_network_call_count` | local `0`; official `12` |
| `s1_observed_gemini_call_count` | local `0`; official `12` |
| `s2_observed_provider_call_count` | exact `int`, value `0` in both modes |
| `s2_observed_network_call_count` | exact `int`, value `0` in both modes |
| `s2_observed_gemini_call_count` | exact `int`, value `0` in both modes |
| `limitation_refs` | exact mode-derived ordered tuple below; never caller-supplied |

The exact official tuple is byte-for-byte the frozen legacy adapter tuple:

```text
(
    "limitation:par_lim_only_airline_geometry",
    "limitation:frozen_accepted_airline_evidence",
    "limitation:mock_corridor",
    "limitation:no_new_all_real_run_during_r1",
    "limitation:no_real_ticket_booking_payment_bank_gds_connector_action",
    "limitation:no_arbitrary_airline_integration",
    "limitation:no_production_signer",
    "limitation:no_signer_identity_verification",
    "limitation:no_root_attestation",
    "limitation:no_pki",
    "limitation:no_production_certification",
    "limitation:owner_built_safe_normalization_not_raw_provider_report",
)
```

The exact local deterministic nonpublication tuple is:

```text
(
    "limitation:par_lim_only_airline_geometry",
    "limitation:mock_corridor",
    "limitation:no_real_ticket_booking_payment_bank_gds_connector_action",
    "limitation:no_arbitrary_airline_integration",
    "limitation:no_production_signer",
    "limitation:no_signer_identity_verification",
    "limitation:no_root_attestation",
    "limitation:no_pki",
    "limitation:no_production_certification",
    "limitation:owner_built_safe_normalization_not_raw_provider_report",
    "limitation:local_simulated_real_compatibility_geometry_permanently_nonpublication",
)
```

The invocation builder accepts no `limitation_refs` argument. Its exact APIs
are:

```text
build_airline_sealed_evidence_package_adapter_invocation_v01(
    *, invocation_mode: Literal["LOCAL_NONPUBLICATION", "OFFICIAL_ACCEPTED"],
    package_id: str, logical_package_ref: str, output_directory_ref: str,
) -> AirlineSealedEvidencePackageAdapterInvocationV01
validate_airline_sealed_evidence_package_adapter_invocation_v01(
    invocation: object,
) -> tuple[str, ...]
airline_sealed_evidence_package_adapter_invocation_to_plain_dict_v01(
    invocation: AirlineSealedEvidencePackageAdapterInvocationV01,
) -> dict[str, object]
```

The builder derives every fixed mode-dependent field and the complete exact
limitation tuple solely from `invocation_mode`; callers do not provide or
override them. The new adapter-result entry point is:

```text
build_airline_sealed_evidence_package_adapter_result_for_invocation_v01(
    *, invocation: AirlineSealedEvidencePackageAdapterInvocationV01,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: AirlineSealedTraceReplayInputV01,
    replay_report: AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: AirlineKernelAdapterResultV01,
) -> AirlineSealedEvidencePackageAdapterResultV01
validate_airline_sealed_evidence_package_adapter_result_for_invocation_v01(
    result: object,
    *, invocation: AirlineSealedEvidencePackageAdapterInvocationV01,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: AirlineSealedTraceReplayInputV01,
    replay_report: AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: AirlineKernelAdapterResultV01,
) -> tuple[str, ...]
airline_sealed_evidence_package_adapter_result_for_invocation_to_plain_dict_v01(
    result: AirlineSealedEvidencePackageAdapterResultV01,
    *, invocation: AirlineSealedEvidencePackageAdapterInvocationV01,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: AirlineSealedTraceReplayInputV01,
    replay_report: AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: AirlineKernelAdapterResultV01,
) -> dict[str, object]
```

Both new modes derive `LiveAttemptIdentityV01` from the adapter-owned
invocation object, including Attempt 4, Package ID, logical Package ref, output
directory ref, provider mode, model, actor count, and provider budget. They do
not use the legacy hard-coded Attempt-1 values.

The A2 binding maps either local Package invocation variant into
`invocation_mode=LOCAL_NONPUBLICATION`, maps `package_id`,
`logical_package_ref`, and `package_output_ref` to the adapter fields. The
adapter-owned builder derives the exact local tuple, including
`limitation:local_simulated_real_compatibility_geometry_permanently_nonpublication`.
Local S1 and S2 use `EXECUTED_DETERMINISTIC_RUNTIME` with observed counts
`0 / 0 / 0` each. All four BSEP-derived artifact records also use
`EXECUTED_DETERMINISTIC_RUNTIME`. The shared attempt uses
`provider_mode=deterministic_fixture`, budget `0`, and expected actor count
`12`; source and projection provider/network/Gemini totals are both
`0 / 0 / 0`. No live-evidence class appears anywhere in the local projection.

The A2 binding maps `OFFICIAL_PACKAGE_INVOCATION` into
`invocation_mode=OFFICIAL_ACCEPTED`, with its exact Package ID, logical Package
ref, and Package output ref. Official S1 uses `EXECUTED_LIVE_RUNTIME` with
observed counts `12 / 12 / 12`; official S2 uses
`LIVE_PROVIDER_SAFE_PROJECTION` with observed counts `0 / 0 / 0`. The four
BSEP-derived artifact records retain `LIVE_PROVIDER_SAFE_PROJECTION`. The
shared attempt uses `provider_mode=real_provider`, budget `12`, and expected
actor count `12`; source totals are `12 / 12 / 12` and projection-operation
totals are `0 / 0 / 0`.

The resulting `domain_projection` must pass
`validate_domain_evidence_projection_v01`. Neither entry point infers an
attempt number from a run ID or path.

### 6.8 Pure Builders and Descriptor-Bound Loaders

Every source, invocation, typed-context, and member builder in the future A2
binding module is pure. A builder accepts already verified values, constructs
immutable typed objects, derives identities, and runs validators. It does not
open a path, inspect Git, import a runner, use `Path.cwd()`, read an environment
variable, discover a repository, or scan a directory.

Filesystem and Git verification belongs only to these two public loader APIs:

```text
load_airline_a2_local_nonpublication_source_v01(
    *, repository_root: Path, attempt_directory: Path, safe_report_path: Path,
    expected_attempt_id: str, expected_execution_head: str,
    expected_attempt_identity_sha256: str,
    expected_private_inventory_sha256: str,
    expected_private_inventory_digest: str,
    expected_generation_gate_sha256: str,
    expected_corridor_archive_sha256: str,
    expected_corridor_archive_byte_count: int,
    expected_safe_report_sha256: str,
    expected_safe_report_byte_count: int,
    expected_safe_execution_id: str,
    implementation_content_sha256: str,
) -> tuple[
    AirlineA2LocalNonpublicationSourceV01,
    AirlineSafeExecutionProjectionV01,
    AirlineTransactionArtifactLedgerSourceBundleV01,
    AirlineCryptoArtifactSealCollectionResultV01,
    AirlineSealedTraceReplayInputV01,
    AirlineSealedTraceReplayReportV01,
    AirlineKernelAdapterResultV01,
]

load_airline_a2_official_accepted_source_v01(
    *, repository_root: Path, accepted_attempt_directory: Path,
    safe_report_path: Path, generation_audit_path: Path,
    expected_attempt_id: str, expected_execution_head: str,
    expected_publication_base_head: str,
    expected_attempt_identity_sha256: str,
    expected_private_inventory_sha256: str,
    expected_private_inventory_digest: str,
    expected_generation_gate_sha256: str,
    expected_corridor_archive_sha256: str,
    expected_corridor_archive_byte_count: int,
    expected_safe_report_sha256: str,
    expected_safe_report_byte_count: int,
    expected_safe_execution_id: str,
    expected_generation_audit_sha256: str,
) -> tuple[
    AirlineA2OfficialAcceptedSourceV01,
    AirlineSafeExecutionProjectionV01,
    AirlineTransactionArtifactLedgerSourceBundleV01,
    AirlineCryptoArtifactSealCollectionResultV01,
    AirlineSealedTraceReplayInputV01,
    AirlineSealedTraceReplayReportV01,
    AirlineKernelAdapterResultV01,
]
```

Both loaders require exact type checks and keyword-only arguments. The official
loader proves that `safe_report_path` and `generation_audit_path` are the exact
repository-relative paths under the supplied `repository_root`, verifies their
committed bytes and Git identity at `expected_publication_base_head`, verifies
Attempt 04 inventory and Corridor archive, and validates the independent audit.
It then passes only verified values into the pure official source builder. The
local loader has no audit input and cannot construct an official source.

The local loader requires the safe-report descriptor's logical name and the
Process-A result field `safe_report_logical_name` to equal the exact literal
`safe-report-v01.json`; neither value is accepted from a caller or inferred
from an arbitrary basename.

Attempt number `4`, model `gemini-2.5-flash`, application-call mode
`json_mime_no_response_schema_single_application_call`, audit status
`CLOSED_PASS`, and audit disposition
`ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE` are frozen validator
constants, not caller flags. Every future value in the official loader
signature is supplied explicitly by the owner CLI.

Neither loader uses implicit CWD, module-relative discovery, `latest` lookup,
environment fallback, repository scanning, or inferred paths. The official
owner CLI supplies `repository_root` and every expected identity and hash
explicitly.

## 7. Descriptor-Bound Source Allowlist

Process B may open only the following strictly verified metadata and selected
structured source files.

Metadata:

- `attempt_identity_v01.json`;
- `private_inventory_v01.json`;
- `generation_gate_v01.json`;
- the mode-appropriate safe report; and
- the committed generation audit only for `OFFICIAL_ACCEPTED_SOURCE`.

Selected raw structured sources:

- `raw_attempt/semantic_to_contract_causal_run.json`;
- `raw_attempt/semantic_to_contract_bridge.json`;
- `raw_attempt/integrated_deterministic_airline_summary.json`;
- `raw_attempt/tri_party_airline_bsep_packet.json`;
- `raw_attempt/tri_party_airline_bsep_validation.json`;
- `raw_attempt/tri_party_airline_bsep_side_projections.json`;
- `raw_attempt/airline_transaction_artifact_ledger.json`;
- `raw_attempt/airline_crypto_artifact_seal_manifest_v01.json`;
- `raw_attempt/airline_crypto_artifact_seal_verification_v01.json`;
- whitelist-only safe geometry from `raw_attempt/summary.json`;
- `raw_attempt/secret_scan.json`; and
- `raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json`.

Every allowlisted structured file is descriptor-opened, bounded-read, and
checked against its exact private-inventory SHA-256 and byte count before strict
parse and validation. Every path component and opened file uses non-following
access, regular-file checks, parent and entry/descriptor device-inode agreement,
parent-symlink rejection, strict UTF-8, duplicate-key rejection,
non-finite-number rejection, exact canonical form where required, and reread
identity checks.

For every non-allowlisted raw prompt, raw provider response, extracted
candidate, and unlisted actor artifact, Process B does not open the body, stream
it, decode it, parse it, or recompute its body hash. It validates only the
private-inventory row shape and that row's binding through the already verified
aggregate inventory digest and generation gate; official mode additionally
binds those facts through the accepted independent audit. No claim of direct
file-byte verification is made for a forbidden body. Those files are never
normalized, copied, printed, or used for hydration.

## 8. Exact A2 Implementation Scope

The Attempt 04 archival slice modifies exactly:

1. `demo/run_tri_party_airline_live_semantic_lane_v01.py`;
2. `tests/test_tri_party_airline_live_semantic_lane_v01_runner.py`;
3. `demo/run_two_domain_airline_all_real_program_v01.py`; and
4. `tests/test_two_domain_airline_all_real_program_v01_runner.py`.

The exact frozen implementation-content order is:

1. `demo/run_tri_party_airline_live_semantic_lane_v01.py`
2. `tests/test_tri_party_airline_live_semantic_lane_v01_runner.py`
3. `demo/run_two_domain_airline_all_real_program_v01.py`
4. `tests/test_two_domain_airline_all_real_program_v01_runner.py`
5. `demo/run_sealed_evidence_package_v01.py`
6. `tests/test_sealed_evidence_package_v01_runner.py`
7. `hedgehog/domains/airline/sealed_evidence_a2_binding_v01.py`
8. `tests/test_airline_sealed_evidence_a2_binding_v01.py`
9. `demo/run_two_domain_airline_a2_seal_v01.py`
10. `tests/test_two_domain_airline_a2_seal_v01_runner.py`
11. `hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py`
12. `tests/test_airline_sealed_evidence_package_adapter_v01.py`

The pre-live implementation scope is exactly twelve paths. No thirteenth code
or test path is authorized. The shared Package implementation remains frozen
except for the closed contextual safe-reference compatibility repair in
Section 8.1. No general scanner relaxation is authorized.

### 8.1 Closed Shared Package Scanner Compatibility

The shared Package scanner may add only the exact domain/member/key/value
context exceptions specified by this preflight for the frozen Airline opaque
response reference, the frozen Airline artifact-hash JSON pointer, and the
existing Supplier source-card JSON pointer. Absolute filesystem paths,
arbitrary provider-response values, raw bodies, credentials, secrets, and all
other JSON pointers remain rejected during both the initial and descriptor-
reread scans.

## 9. Local Packageability Owner Mode

The owner-visible module is
`demo/run_two_domain_airline_a2_seal_v01.py`. Its public Python entry points
are:

```text
main(argv: list[str] | None = None) -> int
run_airline_a2_local_packageability_v01(
    *, gate_phase: Literal["precommit", "committed-head"],
    temporary_root: Path, implementation_content_sha256: str,
    verified_head: str, repository_root: Path,
) -> AirlineA2LocalPackageabilityResultV01
```

This parent API accepts no Package invocation object or invocation ID.
`verified_head` means the verified base HEAD in `precommit` and the verified
clean implementation HEAD in `committed-head`. The function creates the owned
temporary root, launches Process A, then launches fresh Process B, and returns
`AirlineA2LocalPackageabilityResultV01`.

The exact precommit owner command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --local-packageability \
  --gate-phase precommit \
  --repository-root <explicit-absolute-repository-root> \
  --temporary-root <new-absent-absolute-temporary-root> \
  --implementation-content-sha256 <canonical-twelve-file-digest> \
  --base-head <exact-base-head>
```

The exact committed-head owner command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --local-packageability \
  --gate-phase committed-head \
  --repository-root <explicit-absolute-repository-root> \
  --temporary-root <new-absent-absolute-temporary-root> \
  --implementation-content-sha256 <same-canonical-twelve-file-digest> \
  --committed-head <exact-clean-implementation-head>
```

`--base-head` is mandatory for `precommit` and forbidden for `committed-head`.
`--committed-head` is mandatory for `committed-head` and forbidden for
`precommit`. Both tokens are strict lowercase 40-character hashes and are
independently verified against the required repository state. Both phases
require the same implementation-content SHA-256. `--local-packageability` is
mutually exclusive with `--package`, `--anchor`, and `--replay`. Duplicate
options, abbreviations, environment fallbacks, implicit paths, or unknown
options fail before output. The public API and owner CLI require the explicit
absolute `repository_root`; CWD, module location, and environment cannot supply
it implicitly.

The parent creates one invocation-owned absent root. In precommit mode it
launches these exact fresh subprocesses with non-owner internal modes:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --_local-process-a \
  --gate-phase precommit \
  --repository-root <explicit-absolute-repository-root> \
  --temporary-root <owned-root> \
  --synthetic-predecessor-root <owned-root/synthetic-predecessors> \
  --attempt-output <owned-root/attempt-04> \
  --safe-report-output <owned-root/safe-report-v01.json> \
  --implementation-content-sha256 <digest> \
  --base-head <exact-base-head> \
  --process-result-output <owned-root/process-a-result-v01.json>

PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --_local-process-b \
  --gate-phase precommit \
  --repository-root <same-explicit-absolute-repository-root> \
  --temporary-root <owned-root> \
  --attempt-directory <owned-root/attempt-04> \
  --safe-report <owned-root/safe-report-v01.json> \
  --process-a-result <owned-root/process-a-result-v01.json> \
  --implementation-content-sha256 <same-digest> \
  --base-head <same-exact-base-head> \
  --package-root <owned-root/local-package>
```

In committed-head mode it launches:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --_local-process-a \
  --gate-phase committed-head \
  --repository-root <explicit-absolute-repository-root> \
  --temporary-root <owned-root> \
  --synthetic-predecessor-root <owned-root/synthetic-predecessors> \
  --attempt-output <owned-root/attempt-04> \
  --safe-report-output <owned-root/safe-report-v01.json> \
  --implementation-content-sha256 <digest> \
  --committed-head <exact-clean-implementation-head> \
  --process-result-output <owned-root/process-a-result-v01.json>

PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --_local-process-b \
  --gate-phase committed-head \
  --repository-root <same-explicit-absolute-repository-root> \
  --temporary-root <owned-root> \
  --attempt-directory <owned-root/attempt-04> \
  --safe-report <owned-root/safe-report-v01.json> \
  --process-a-result <owned-root/process-a-result-v01.json> \
  --implementation-content-sha256 <same-digest> \
  --committed-head <same-exact-clean-implementation-head> \
  --package-root <owned-root/local-package>
```

Process A invokes
`run_two_domain_airline_all_real_program_v01` through its future Attempt 04
real-mode branch with established simulated-real provider and predecessor
dependency injection. It uses `attempt_number=4`, the frozen twelve-actor
order, and the production persistence seam. It does not use an Attempt 03
execution branch or a fixture-only archival helper. Process A exits after
writing its temporary attempt and safe projection.

### 9.1 Process-A Result Contract

The internal boundary file is exactly `process-a-result-v01.json`, represented
by immutable `AirlineA2LocalProcessAResultV01`. Its closed typed fields are:

```text
result_id: str
result_version: Literal["v0.1"]
gate_phase: Literal["precommit", "committed-head"]
verified_head_token: str
implementation_content_sha256: str
attempt_id: str
execution_head: str
attempt_identity_sha256: str
private_inventory_sha256: str
private_inventory_digest: str
generation_gate_sha256: str
corridor_archive_logical_name: Literal["raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json"]
corridor_archive_sha256: str
corridor_archive_byte_count: int
safe_report_logical_name: Literal["safe-report-v01.json"]
safe_report_sha256: str
safe_report_byte_count: int
safe_execution_id: str
wrapper_callback_observed_count: Literal[12]
provider_callback_started_count: Literal[12]
provider_callback_completed_count: Literal[12]
semantic_actor_call_count: Literal[12]
causal_actor_call_count: Literal[5]
generic_actor_call_count: Literal[7]
duplicate_actor_call_count: Literal[0]
collector_invocation_count: Literal[1]
deterministic_airline_collection_count: Literal[1]
ticket_purchase_corridor_execution_count: Literal[1]
airline_transaction_artifact_ledger_collection_count: Literal[1]
airline_crypto_artifact_seal_collection_count: Literal[1]
outbound_provider_sdk_call_count: Literal[0]
outbound_network_call_count: Literal[0]
outbound_gemini_call_count: Literal[0]
real_world_effects_count: Literal[0]
final_status: Literal["PASS"]
validation_errors: tuple[str, ...], exact empty tuple
```

The exact pure APIs are:

```text
build_airline_a2_local_process_a_result_v01(
    *, gate_phase: Literal["precommit", "committed-head"],
    verified_head_token: str, implementation_content_sha256: str,
    attempt_id: str, execution_head: str,
    attempt_identity_sha256: str, private_inventory_sha256: str,
    private_inventory_digest: str, generation_gate_sha256: str,
    corridor_archive_sha256: str, corridor_archive_byte_count: int,
    safe_report_sha256: str, safe_report_byte_count: int,
    safe_execution_id: str, wrapper_callback_observed_count: int,
    provider_callback_started_count: int,
    provider_callback_completed_count: int, semantic_actor_call_count: int,
    causal_actor_call_count: int, generic_actor_call_count: int,
    duplicate_actor_call_count: int, collector_invocation_count: int,
    deterministic_airline_collection_count: int,
    ticket_purchase_corridor_execution_count: int,
    airline_transaction_artifact_ledger_collection_count: int,
    airline_crypto_artifact_seal_collection_count: int,
    outbound_provider_sdk_call_count: int, outbound_network_call_count: int,
    outbound_gemini_call_count: int, real_world_effects_count: int,
) -> AirlineA2LocalProcessAResultV01
validate_airline_a2_local_process_a_result_v01(
    result: object,
) -> tuple[str, ...]
airline_a2_local_process_a_result_to_plain_dict_v01(
    result: AirlineA2LocalProcessAResultV01,
) -> dict[str, object]
```

The builder derives the two fixed logical names, `result_version`,
`final_status`, empty errors, and `result_id`. The identity domain is exactly:

```text
hedgehog-os:airline-a2-local-process-a-result:v0.1
```

Identity derivation replaces `result_id` with exactly 64 ASCII zeroes and
hashes the ASCII domain, one NUL byte, and canonical JSON without terminal LF.
Stored bytes use the Section-5 canonical JSON algorithm plus exactly one LF.
The runner writes the absent file exclusively with non-following descriptor
access, a full-write loop, fsync, proven close, descriptor-bound reread, strict
parse, canonical-byte equality, reconstructed typed equality, exact mode and
parent/entry/inode identity checks. Cleanup removes only the exact
invocation-owned inode.

The object contains no raw body, credential, absolute path, invocation ID,
Package ID, output ref, or caller-selected identity. Process B never trusts it
alone: every ID, hash, byte count, logical name, phase, head, and counter is
cross-checked against the descriptor-verified attempt metadata, inventory,
Corridor archive, safe report, and owner-supplied gate inputs.

Process B is a fresh interpreter. It receives only explicit paths and hashes,
loads and validates the Process-A result and descriptor-verified files, derives
`LOCAL_NONPUBLICATION_SOURCE`, then derives the phase-appropriate local Package
invocation. Only Process B performs those derivations. It opens the temporary
attempt through the production A2 reader, hydrates the six typed inputs,
validates the adapter and domain projection, constructs the four local members,
calls the frozen shared Package Python API exactly once with
`fixture_disposable=False`, and rereads the Package from disk. No invocation
ID or object, Python object, descriptor, module state, or process memory crosses
from Process A.

Cleanup removes only descriptor-proven invocation-owned paths. Failure to
prove ownership leaves retained residue reported fail-closed and never removes
a foreign inode.

### 9.2 Implementation-Content Identity

The canonical implementation-content digest is SHA-256 over the domain
separator

```text
hedgehog-os:airline-attempt-04-a2-twelve-path-content:v0.1
```

followed by one NUL byte and, for each path in the exact twelve-path order in
Section 8, the ASCII logical path, one NUL byte, the canonical ASCII decimal
byte count, one NUL byte, and the exact file bytes. Normatively:

```text
SHA256(
  b"hedgehog-os:airline-attempt-04-a2-twelve-path-content:v0.1\0"
  + for each ordered path:
      path_ascii
      + b"\0"
      + canonical_ascii_decimal_byte_count
      + b"\0"
      + exact_file_bytes
)
```

The precommit gate binds this digest without claiming a clean committed head.
The repeated postcommit gate requires the identical digest, the supplied exact
committed HEAD, HEAD equal to origin/main, a clean worktree, empty staging, and
zero canonical A1/A2 output paths. Only that postcommit PASS authorizes one
real Attempt 04.

### 9.3 Exit and Terminal Contract

PASS emits exactly two stdout lines: one sanitized canonical JSON summary and
the literal `ATTEMPT_04_LOCAL_PACKAGEABILITY_GATE=PASS`. PASS has empty stderr
and exit code `0`. FAIL emits exactly one sanitized canonical JSON line, empty
stderr, and exit code `2`. No output contains an absolute path, raw value,
traceback, exception text, object representation, memory address, credential,
prompt, response, or candidate body.

### 9.4 Counter Separation

Source-shaped adapter geometry uses the committed field names:

```text
wrapper_callback_observed_count = 12
provider_callback_started_count = 12
provider_callback_completed_count = 12
semantic_actor_call_count = 12
causal_actor_call_count = 5
generic_actor_call_count = 7
duplicate_actor_call_count = 0
collector_invocation_count = 1
deterministic_airline_collection_count = 1
ticket_purchase_corridor_execution_count = 1
airline_transaction_artifact_ledger_collection_count = 1
airline_crypto_artifact_seal_collection_count = 1
```

Independently observed harness operations use different fields:

```text
outbound_provider_sdk_call_count = 0
outbound_network_call_count = 0
outbound_gemini_call_count = 0
real_world_effects_count = 0
```

No field serves both meanings. The local source may carry the frozen
real-provider-shaped adapter geometry only while the
`LOCAL_NONPUBLICATION_SOURCE` discriminant, `execution_mode=simulated_real`,
`official_evidence_eligible=false`, and all four zero outbound counters are
present and validated. It is never described as executed live evidence.

## 10. Official Package Owner Mode

The future owner command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --package \
  --repository-root <explicit-absolute-repository-root> \
  --publication-base-head <exact-clean-publication-base-head> \
  --accepted-attempt-directory <explicit-accepted-attempt-04-directory> \
  --accepted-attempt-id <exact-accepted-attempt-04-id> \
  --execution-head <exact-accepted-attempt-04-head> \
  --expected-attempt-identity-sha256 <exact-attempt-identity-sha256> \
  --expected-private-inventory-sha256 <exact-private-inventory-sha256> \
  --expected-private-inventory-digest <exact-private-inventory-digest> \
  --expected-generation-gate-sha256 <exact-generation-gate-sha256> \
  --expected-corridor-archive-sha256 <exact-corridor-archive-sha256> \
  --expected-corridor-archive-byte-count <exact-corridor-archive-byte-count> \
  --safe-report <committed-attempt-04-safe-report> \
  --expected-safe-report-sha256 <exact-safe-report-sha256> \
  --expected-safe-report-byte-count <exact-safe-report-byte-count> \
  --expected-safe-execution-id <exact-safe-execution-id> \
  --generation-audit <committed-attempt-04-generation-audit> \
  --expected-generation-audit-sha256 <exact-generation-audit-sha256> \
  --package-root <new-absent-official-package-root> \
  --package-index-output <new-absent-official-package-index>
```

Every option is mandatory and duplicate-rejected. The source must be Attempt
04. Before constructing any typed object or SafeMember, the command verifies
the exact official source variant, attempt identity, committed report and
audit, complete Corridor archive, 73-file inventory geometry, and every source
hash. It passes the explicit repository root and publication-base head to the
official loader, then derives `AirlineA2OfficialPackageInvocationV01`; no
Package identity or output ref is accepted from the caller. Latest-attempt
discovery, repository scanning, environment fallback, implicit path, Attempt
03 substitution, temporary path, local-source promotion, or uncommitted
report/audit bytes are forbidden.

G2 freezes the ten `--expected-*` future values after accepted Attempt 04.
I1 remains generic and requires those values as explicit owner inputs; no I1
code change after G2 may embed an Attempt-04 hash. The CLI maps every option
one-to-one into `load_airline_a2_official_accepted_source_v01`; it performs no
Markdown parsing, implicit CWD lookup, environment fallback, or repository
discovery.

The supplied `--package-root` and `--package-index-output` are explicit safety
inputs, not caller-selected identities. After strict lexical and descriptor
validation under `--repository-root`, they must equal the exact derived
repository-relative refs in Section 4.3 and both targets must be absent. Any
alias or different path fails before member construction.

### 10.1 Exact Anchor Owner Mode

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 --anchor --repository-root <repository-root-absolute-path> --package-root <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01 --package-index <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_package_index_v01.json --publication-base-head <exact-clean-G2-head> --anchor-output <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_crypto_anchor_v01.json
```

The Anchor mode requires exactly every listed flag and verifies the frozen
Package/index bytes in the worktree that was clean at the verified G2 base
before Package wrote them. It writes an absent invocation-owned Anchor output
exclusively, rereads it, and closes `EVIDENCE_ONLY`. It does not claim
`ANCHORED_PASS`.

### 10.2 Exact Replay Owner Mode

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 --replay --repository-root <repository-root-absolute-path> --p1-head <exact-committed-P1-head> --package-root <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01 --package-index <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_package_index_v01.json --anchor-file <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_crypto_anchor_v01.json --supplied-anchor-publication-id <exact-anchor-publication-id> --replay-output <repository-root-absolute-path>/docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_replay_report_v01.json
```

Replay requires exactly every listed flag, verifies the exact committed P1
tree and supplied Anchor publication identity, opens Package/index/Anchor
read-only, and exclusively writes then rereads the absent invocation-owned
Replay output.

### 10.3 Owner-Mode Parser and Terminal Law

`--local-packageability`, `--package`, `--anchor`, and `--replay` are pairwise
mutually exclusive. For each owner mode every displayed flag is mandatory,
flags belonging only to another mode are forbidden, and ordinary or
`--name=value` duplicates, abbreviations, unknown options, or positional
arguments fail before output creation. No environment fallback or inferred
path is allowed.

Package, Anchor, and Replay PASS each emit exactly one sanitized canonical JSON
summary line, empty stderr, and exit code `0`. Their FAIL path emits exactly one
sanitized canonical JSON line, empty stderr, and exit code `2`. Output contains
no private path, credential, raw value, traceback, exception text, object
representation, or memory address. Cleanup removes only a descriptor-proven
invocation-owned inode and never removes a foreign replacement. Package,
Anchor, and Replay make provider/network/Gemini/effect calls `0 / 0 / 0 / 0`.

The governing publication artifacts remain:

- `docs/audit_reports/auditor_two_domain_airline_anchor_publication_v01.log`;
- `docs/audit_reports/auditor_two_domain_airline_anchored_replay_v01.log`; and
- `docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_human_story_v01.md`.

## 11. Local and Official Package Geometry

The local Package root is invocation-owned, absent, outside the repository,
and noncanonical. Canonical Package and index writes are both zero; Anchor and
Replay owner operations are both zero. Local output cannot be accepted by the
official Package, Anchor, or Replay commands.

After accepted Attempt 04 and G2, the official Package root is:

`docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01`

Its exact sorted member inventory is the four Section-5 members plus
`sealed_package_manifest_v01.json`, written last and excluded from its own
SafeFile inventory. The adjacent package index is:

`docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_package_index_v01.json`

The index binds the official source identity, Package invocation identity,
typed context, adapter result, domain projection, all SafeFiles, Manifest ID
and bytes, package-content hash, member hashes, and exact repository-relative
Package root.

### 11.1 Exact Official Package-Index Contract

The A2 binding module owns the immutable official-only type
`AirlineA2SafePackageIndexV01`. Its top-level keys, shown in exact canonical
lexicographic order, are closed:

```text
adapter_result_id: str
domain_projection_id: str
index_id: str
index_version: Literal["v0.1"]
logical_package_ref: str
manifest_byte_count: int
manifest_id: str
manifest_sha256: str
member_03_typed_context_id: str
member_04_adapter_projection_id: str
package_content_hash: str
package_id: str
package_invocation_identity: AirlineA2OfficialPackageInvocationV01
package_root: Literal["docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_sealed_package_v01"]
package_status: Literal["SELF_CONSISTENT_UNANCHORED"]
safe_file_records: tuple[SafeFileRecordV01, ...]
source_identity: AirlineA2OfficialAcceptedSourceV01
source_variant: Literal["OFFICIAL_ACCEPTED_SOURCE"]
validation_errors: tuple[str, ...]
```

`validation_errors` is exactly the empty tuple and projects as `[]`.
`source_identity` and `package_invocation_identity` project as exact closed
plain objects. `safe_file_records` contains exactly four typed records in
member-01 through member-04 order and projects as a JSON array of four exact
plain `SafeFileRecordV01` rows. Each row has exactly these keys in canonical
lexicographic order:

```text
byte_count: int
content_sha256: str
evidence_class: str
file_record_id: str
logical_path: str
media_type: str
secret_scan_passed: bool
source_record_ids: list[str]
terminal_newline_required: bool
```

`source_identity` is the exact plain projection of
`AirlineA2OfficialAcceptedSourceV01`; `package_invocation_identity` is the
exact plain projection of `AirlineA2OfficialPackageInvocationV01`. No key in
either nested projection may be omitted or added. The four rows must equal the
descriptor-reread Package member bytes, the exact
Section-5 logical paths, evidence classes, media type, source-record
selections, terminal-LF law, and secret-scan results. The source identity and
Package invocation must be validated official variants. Package ID, logical
Package ref, Package root, and invocation ID must equal the exact derived
`OFFICIAL_PACKAGE_INVOCATION` fields. The member-03 and member-04 identities
must equal the identities in their strict descriptor-reread canonical bytes.
`adapter_result_id` and `domain_projection_id` must equal the validated member-04
objects. Manifest ID, Manifest SHA-256, Manifest byte count, and
package-content hash must equal the validated descriptor-reread
`SealedPackageManifestV01` and its exact canonical bytes.

The index identity domain is exactly:

```text
hedgehog-os:airline-a2-safe-package-index:v0.1
```

To derive `index_id`, replace that field with exactly 64 ASCII zeroes,
serialize the complete zeroed plain projection as canonical JSON without a
terminal LF, and hash the ASCII domain, one NUL byte, and those bytes with
SHA-256. The resulting lowercase digest replaces the zero slot. Its exact APIs
in `hedgehog/domains/airline/sealed_evidence_a2_binding_v01.py` are:

```text
build_airline_a2_safe_package_index_v01(
    *, source: AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2OfficialPackageInvocationV01,
    member_03_typed_context_id: str,
    member_04_adapter_projection_id: str,
    adapter_result: AirlineSealedEvidencePackageAdapterResultV01,
    domain_projection: DomainEvidenceProjectionV01,
    safe_file_records: tuple[SafeFileRecordV01, ...],
    manifest: SealedPackageManifestV01,
    manifest_sha256: str, manifest_byte_count: int,
) -> AirlineA2SafePackageIndexV01
validate_airline_a2_safe_package_index_v01(
    index: object, *, source: AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2OfficialPackageInvocationV01,
    adapter_result: AirlineSealedEvidencePackageAdapterResultV01,
    domain_projection: DomainEvidenceProjectionV01,
    safe_file_records: tuple[SafeFileRecordV01, ...],
    manifest: SealedPackageManifestV01,
    manifest_sha256: str, manifest_byte_count: int,
) -> tuple[str, ...]
airline_a2_safe_package_index_to_plain_dict_v01(
    index: AirlineA2SafePackageIndexV01,
) -> dict[str, object]
```

The builder derives `package_content_hash` from the validated Manifest; it
does not accept that identity independently. It rejects a local source or a
local Package invocation before index construction. Local packageability never
writes this canonical index.

The index bytes are canonical UTF-8 JSON plus exactly one terminal LF. The
official writer requires an absent output and uses exclusive non-following
creation, a complete-write loop, file fsync, close, parent-directory fsync,
descriptor-bound reopen, strict duplicate-key/non-finite rejecting parse,
typed reconstruction, validator PASS, plain-projection equality, exact byte
equality, and descriptor/direntry identity agreement. Cleanup may remove only
the exact invocation-owned inode; a foreign replacement is never removed.
Descriptor-bound Package inventory verification must prove every member and
Manifest hash, byte count, mode, identity, sorted logical path, and aggregate
relationship before the index can PASS.

Anchor and Replay accept only a successfully validated
`AirlineA2SafePackageIndexV01` whose source identity, Package invocation,
typed-context identity, adapter-projection identity, adapter-result identity,
domain-projection identity, four SafeFile rows, Manifest, package-content hash,
and Package root all equal the independently descriptor-reread Package bytes.
No index field may substitute for that disk proof.

## 12. Package, Anchor, and Replay Sequence

After the official gate becomes `READY_FOR_REVIEW`:

1. Package validates `OFFICIAL_ACCEPTED_SOURCE`, builds one Package through the
   frozen typed API with `fixture_disposable=False`, and writes its owned
   official Package and index into the clean G2 worktree.
2. The runner closes and descriptor-rereads every Package/index byte. Package
   and index become frozen and immutable within the P1 operation but are not
   yet Git-committed. Their status is `SELF_CONSISTENT_UNANCHORED`.
3. Anchor reads those exact frozen, descriptor-reread worktree bytes, calls the
   frozen typed Anchor API once, and writes `EVIDENCE_ONLY`; it does not claim
   `ANCHORED_PASS`.
4. An independent Anchor audit verifies the exact Package, index, and Anchor.
5. P1 commits Package, index, Anchor, and Anchor audit together. There is no
   Package-only commit boundary.
6. Replay reads only the committed P1 bytes, verifies the exact P1 head,
   obtains matching verification `ANCHORED_PASS`, calls the frozen typed Replay
   API once, and closes `PASS`.
7. P2 commits Replay, Replay audit, Human Story, and checkpoint closure.

A coherent mismatch is `FAIL_CLOSED`. No layer mutates accepted source or an
earlier frozen publication layer.

## 13. Shared API Reconciliation

The programme Section-26 wording naming the three standalone shared runners is
stale only for official A2 owner-command orchestration because those CLIs are
fixture-only. The reviewed domain-local Airline A2 runner supersedes that
owner-command routing only. The three shared typed APIs and every shared
Package, Manifest, Anchor, verification, Replay, descriptor, cleanup, status,
and nonclaim law remain authoritative and unchanged. Disposable fixtures stay
ineligible. Supplier S3 and shared domain-neutral contracts are unchanged.

The Airline seam owns only strict source-variant verification, typed hydration,
source and Package invocation identities, source-record selection, SafeMember
construction, package-index binding, mode isolation, and owner orchestration.
It does not duplicate shared cryptographic or filesystem law.

## 14. Frozen Surfaces and Scope

Frozen surfaces are Attempts 01, 02, and 03; future accepted Attempt 04 after
audit freeze; actor order and prompts; semantic contracts; provider adapter,
model, timeout, and one-call mode; BSEP; all three Roots; Corridor contracts,
builders, validators, and execution; Ledger contracts and collector; Crypto
contracts and collector; historical replay; Kernel and Airline Kernel adapter;
shared evidence profile; shared Package, Anchor, and Replay; Supplier; and all
existing Attempt 03 public evidence.

Only archival persistence, Attempt 04 orchestration/predecessor/public-output
law, and the six A2 paths are in scope. Supplier remains prohibited until
Airline A2 publication closes.

## 15. Commit Boundaries

- `G1`: AGENTS, this corrected A2 preflight, and the Attempt 04 preflight only.
- `I1`: exactly twelve authorized implementation/test paths; focused tests and
  precommit local packageability PASS; no live call or publication.
- `L1`: repeat local packageability on the clean committed I1 HEAD with the
  identical implementation-content digest and zero repository output.
- `E1`: exactly one owner-terminal Attempt 04; no automatic repeat.
- `E2`: independent Attempt 04 audit and distinct safe-report/audit commit.
- `G2`: update this preflight with exact accepted Attempt 04 identities and
  hashes; move official A2 to `READY_FOR_REVIEW`.
- `P1`: official Package, index, Anchor, and independent Anchor audit commit.
- `P2`: read-only verification, Replay, Replay audit, Human Story, and
  checkpoint closure commit.

No boundary may be collapsed or rewritten post hoc.

## 16. Failure and Nonclaims

Every source variant, lineage, schema, type, identity, allowlist, inventory,
hash, byte, mode, source record, typed context, adapter, projection, Manifest,
Package, Anchor, Replay, ownership, or cleanup mismatch fails closed. Cleanup
removes only exact invocation-owned objects. Frozen evidence is never deleted,
rewritten, repaired, relabelled, or promoted.

A2 creates no authority, permission, action, payment, booking, ticket issuance,
receipt authority, Root Attestation, signer identity, PKI claim, external
timestamp claim, or real-world effect. Historical mock Corridor and receipt
evidence remains evidence only. Root remains final authority. This is not
production or a production-security claim.

## 17. Immediate Next Gate

The only next owner-reviewed gate is:

`two_domain_all_real_sealed_evidence_program_v01_a1_attempt_04_complete_corridor_capture_implementation`

No provider call or official A2 output is authorized by this document.
