# Hedgehog OS Gate 2 / G2-B
## DRS Semantic Address Space, Controlled Memory Descent,
## and ReuseCertificate Preflight v0.1

## 1. Metadata

```text
document_id:
  drs_semantic_address_space_reuse_certificate_g2_b_preflight_v01

document_revision:
  v0.1

document_status:
  PREFLIGHT

preflight_status:
  READY_FOR_INDEPENDENT_CONTRACT_REVIEW

gate_id:
  gate2_g2b_drs_semantic_address_space_reuse_certificate

observed_base_head:
  b78183b3bd5ecc5e9ea2201b9fe498d208423747

inventory_status:
  PASS

g2a_status:
  CLOSED_PASS

gate2_status:
  NOT_CLOSED

planning_only:
  true

implementation_authorized:
  false

preflight_commit_authorized:
  false

runtime_modified:
  false

tests_modified:
  false

schemas_modified:
  false

demos_modified:
  false

audits_modified:
  false

checkpoints_modified:
  false

release_surfaces_modified:
  false

provider_called:
  false

network_called:
  false

gemini_called:
  false

external_drs_called:
  false

connector_called:
  false

real_world_effects_count:
  0

public_release_claimed:
  false

operational_reference_kernel_rc2_claimed:
  false

g2c_started:
  false

next_required_action:
  independent_contract_review_before_preflight_commit
```

This document freezes a prospective implementation contract. It creates no
runtime authority, permission, capability, action, receipt, effect, schema, or
release state.

## 2. Gate Purpose

G2-B will establish one local reference-kernel family for stable semantic
addresses, pointer-first meaning records, explicit temporal queries, pure
query-local evaluation, hard eligibility before ranking, bounded
Root-approved memory descent, and evidence-bound informational reuse.

DRS remains semantic topology, address, resonance, lineage, provenance,
retrieval, and audit fabric. DRS is not a truth oracle, permission issuer, or
executor. A retrieval score, freshness result, GT advisory result, semantic
similarity result, or ReuseCertificate cannot become authority.

The only operational shortcut planned by this gate is a safe non-action
informational `ANSWER_SHORTCUT`, and only after an existing local Root decision,
a validated Root authorization projection, and a validated ReuseCertificate.
The certificate does not create the informational output. Root remains the
sole final authority and the existing Root-controlled final-output boundary
remains canonical.

## 3. Source-of-Truth Order

The binding source-of-truth order is:

1. clean committed repository at HEAD `b78183b3...`;
2. current AGENTS active checkpoint;
3. G2-A internal checkpoint and independent audit, only for the frozen G2-A
   boundary;
4. Human Passport;
5. invariants;
6. machine manifest;
7. accepted Gate-1 ABI, Root, Transition Registry, Effect Firewall, Corridor,
   Replay, MultiRoot, Conformance and Living Gauntlet contracts;
8. this Architect Ruling for exact G2-B decisions;
9. Gate-Based Roadmap v3.1 for gate order and release boundaries;
10. Master Roadmap v2.1 for technical target depth;
11. Math Appendix for time, aging, eligibility, ranking and reuse formulas;
12. historical DRS proofs, demos, audits and walkthroughs only as compatibility
    donors or adversarial sensors.

The following inequalities are binding:

```text
old PASS label != current canonical runtime
proof object != canonical G2-B contract
caller boolean != Root authority
score != eligibility
eligibility != permission
certificate != Root decision
```

Where historical wording differs, this preflight controls G2-B. Historical
objects are accepted only through explicit compatibility projection and never
through implicit duck typing.

## 4. G2-A and G2-C Frozen Boundaries

G2-A is `CLOSED_PASS`. These contracts and laws are frozen:

- `ActionCommitPacketV02`;
- `ActionCommitPacketRegistryV02`;
- `TransitionRegistryV01`;
- `RootDecisionKernelV01`;
- `EffectFirewallV01`;
- `ContractFulfillmentCorridorV01`;
- `ActionPacketEffectFirewallProjectionV01`;
- ActionPacket lifecycle Replay;
- ActionPacket present eligibility inspection;
- receipt non-authority;
- immutable ActionPacket history;
- Root-bound invalidation;
- idempotency;
- lifecycle transition law.

G2-B may consume validated G2-A evidence. It may not modify the G2-A
lifecycle, create another packet family, Registry, or Root, create permission,
create an effect handle, create a receipt, or convert historical ActionPacket
evidence into present authority.

G2-C is frozen. `hedgehog/mode_router.py`, adaptive execution-mode selection,
general route shortcuts, sealed-Replay mode routing, protocol-preparation mode
routing, and fractal mode selection are outside G2-B. G2-B may produce
validated evidence for later routing but must not implement the general
ExecutionModeRouter.

## 5. Hop-1 Inventory Accepted Facts

The read-only Hop-1 inventory established these accepted facts:

| Current surface | Exact evidence | Accepted status for G2-B |
| --- | --- | --- |
| Local dictionary store | `hedgehog/drs.py::LocalDRS` | Legacy compatibility input, not canonical G2-B |
| Read-path side effect | `hedgehog/drs.py::LocalDRS.layer_path` calls `mkdir(parents=True, exist_ok=True)` | Canonical reads need a new pure adapter |
| Local DRS v0.2 | `hedgehog/local_drs_v02.py::DRSRecordV02`, `DRSLineageRef`, `DRSFreshnessEnvelope`, `TemporalQueryV02`, `DRSReuseDecision`, `DRSResolveReport` | Read-only compatibility donor |
| Semantic resolver | `hedgehog/local_drs_resolver.py::SemanticDRSRecordInput`, `SemanticResolveQuery`, `ResolvedDRSCandidate`, `ResolvedDRSReport` | Compatibility and writeback donor |
| Float reuse score | `hedgehog/reuse_gate.py::compute_reuse_score`, `evaluate_reuse_candidates` | Legacy compatibility logic; not canonical ranking |
| Caller-selected shortcut request | `hedgehog/mode_router.py::route_execution` parameter `allow_direct_reuse` | Current executable compatibility surface requiring a fence |
| Orchestrator forwarding | `hedgehog/root_orchestrator.py::RootOrchestrator.process_event` forwards `allow_direct_reuse` | Narrow G2-B4 integration target |
| Informational proof donor | `hedgehog/non_action_reuse_positive_control.py::RootShortcutGateV01` and `evaluate_root_shortcut_gate_v01` | Accepted proof donor, not canonical Root authority |
| Legacy time helpers | `hedgehog/time_model.py::make_time_envelope`, `make_temporal_query`, `utc_now_iso` | Compatibility donor; ambient ISO time is noncanonical |
| Frozen schemas | `schemas/drs_record.schema.json`, `schemas/time_envelope.schema.json`, `schemas/temporal_query.schema.json` | Legacy schemas preserved unchanged |

No current surface exactly implements the complete
`SemanticAddressV01`/`MeaningRecordV01`/controlled-descent/
`ReuseCertificateV01` family frozen here. Existing direct-reuse booleans and
proof labels are neither Root decisions nor certificates.

## 6. Closed Architect Decision Register

All decisions in this register are `CLOSED`.

| Decision | Closed ruling |
| --- | --- |
| Canonical family | One versioned G2-B family; legacy families are projection inputs only |
| Semantic address | Stable seven-field meaning-family identity with prefix `drsaddr_v01:` |
| Canonical time | Exact signed-int64 UTC epoch seconds with explicit evaluation time |
| Query modes | Exactly six modes frozen in Section 15 |
| Root approval | Existing `RootDecisionKernelV01` triple; no new Root family |
| Pointer boundary | Typed local-only `MemoryPointerV01` and `ArtifactPointerV01` |
| Memory descent | Six exact classes and immutable bounded budget |
| Reuse classes | Only `CONTEXT_ONLY` and `ANSWER_SHORTCUT` operational in v0.1 |
| Legacy direct path | `allow_direct_reuse` is consideration only and must be fenced |
| G2-A history | Action and receipt history cannot authorize `ANSWER_SHORTCUT` |
| Schemas | Four new versioned schemas; three legacy schemas remain frozen |
| Proof domains | `TRAVEL_POLICY_INFORMATION` and `WAREHOUSE_MAINTENANCE_INFORMATION` |
| Read purity | Select a new pure G2-B compatibility adapter; `hedgehog/drs.py` stays frozen |
| G2-C boundary | General mode routing remains frozen |

No item in this register remains an implementation-time architecture question.

## 7. Canonical G2-B Family

The canonical family consists exactly of these immutable contract types:

1. `SemanticAddressV01`
2. `MemoryPointerV01`
3. `ArtifactPointerV01`
4. `LineageEdgeV01`
5. `DRSAuthorityEnvelopeV01`
6. `DRSTimeEnvelopeV01`
7. `MeaningRecordV01`
8. `DRSTemporalQueryV01`
9. `QueryEvaluationStateV01`
10. `ResolutionCandidateV01`
11. `RetrievalPlanV01`
12. `MemoryDescentBudgetV01`
13. `MemoryDescentRequestV01`
14. `MemoryDescentResultV01`
15. `RootShortcutAuthorizationProjectionV01`
16. `ReuseCertificateV01`
17. `DRSResolutionReportV01`
18. `LegacyDRSProjectionV01`
19. `G2AActionHistoryBindingV01`

All are frozen dataclasses. Every public validator is total over arbitrary
objects and returns `(bool, tuple[str, ...])`. Every public builder raises only
a sanitized `ValueError` whose message is the type's stable invalid reason.
Every public serializer returns deterministic plain data composed only of exact
built-in JSON-compatible types.

Every type requires exact outer and nested types. `bool` is rejected where
`int` is required. Subclasses of `str`, `int`, `tuple`, or a canonical
dataclass are rejected. Custom-equality substitutes, coercion, binary floats,
`Decimal`, numeric strings, unknown fields at schema boundaries, and mixed
schema versions fail closed.

## 8. Canonicalization and Identity Profile

Canonical identity profile `drs_g2b_identity_profile_v01` is frozen as:

1. validate every consequential field with exact built-in or exact canonical
   dataclass type;
2. project the exact ordered identity fields to a JSON array;
3. encode compact JSON with UTF-8, `ensure_ascii=True`, separators `(",", ":")`,
   and no key sorting because field order is positional;
4. prepend the exact ASCII domain tag and one LF byte;
5. compute lowercase SHA-256 hex;
6. prepend the exact identity prefix.

No Unicode normalization, case folding, trimming, alias mapping, default
insertion, numeric coercion, or omitted consequential field is permitted.
Identity rebuild must exactly equal the transported ID.

| Type | Domain tag | Prefix | Identity material |
| --- | --- | --- | --- |
| `SemanticAddressV01` | `hedgehog:drs:semantic_address:v01` | `drsaddr_v01:` | Exact seven address fields |
| `MemoryPointerV01` | `hedgehog:drs:memory_pointer:v01` | `drsmem_v01:` | Every field except `pointer_id` |
| `ArtifactPointerV01` | `hedgehog:drs:artifact_pointer:v01` | `drsart_v01:` | Every field except `pointer_id` |
| `LineageEdgeV01` | `hedgehog:drs:lineage_edge:v01` | `drsedge_v01:` | Every field except `lineage_edge_id` |
| `DRSAuthorityEnvelopeV01` | `hedgehog:drs:authority_envelope:v01` | `drsauth_v01:` | Every field except `authority_envelope_id` |
| `DRSTimeEnvelopeV01` | `hedgehog:drs:time_envelope:v01` | `drstime_v01:` | Every field except `time_envelope_id` |
| `MeaningRecordV01` | `hedgehog:drs:meaning_record:v01` | `drsmeaning_v01:` | Every field except `meaning_record_id` |
| `DRSTemporalQueryV01` | `hedgehog:drs:temporal_query:v01` | `drsquery_v01:` | Every field except `query_id` |
| `QueryEvaluationStateV01` | `hedgehog:drs:query_evaluation:v01` | `drsqeval_v01:` | Every field except `query_evaluation_id` |
| `ResolutionCandidateV01` | `hedgehog:drs:resolution_candidate:v01` | `drscandidate_v01:` | Every field except `resolution_candidate_id` |
| `RetrievalPlanV01` | `hedgehog:drs:retrieval_plan:v01` | `drsplan_v01:` | Every field except `retrieval_plan_id` |
| `MemoryDescentBudgetV01` | `hedgehog:drs:memory_descent_budget:v01` | `drsbudget_v01:` | Every field except `memory_descent_budget_id` |
| `MemoryDescentRequestV01` | `hedgehog:drs:memory_descent_request:v01` | `drsdescentreq_v01:` | Every field except `memory_descent_request_id` |
| `MemoryDescentResultV01` | `hedgehog:drs:memory_descent_result:v01` | `drsdescentres_v01:` | Every field except `memory_descent_result_id` |
| `RootShortcutAuthorizationProjectionV01` | `hedgehog:drs:root_shortcut_projection:v01` | `drsrootshortcut_v01:` | Every field except `root_shortcut_projection_id` |
| `ReuseCertificateV01` | `hedgehog:drs:reuse_certificate:v01` | `reusecert_v01:` | Every field except `certificate_id` |
| `DRSResolutionReportV01` | `hedgehog:drs:resolution_report:v01` | `drsreport_v01:` | Every field except `report_id` |
| `LegacyDRSProjectionV01` | `hedgehog:drs:legacy_projection:v01` | `drslegacyproj_v01:` | Every field except `projection_id` |
| `G2AActionHistoryBindingV01` | `hedgehog:drs:g2a_history_binding:v01` | `drsg2ahistory_v01:` | Every field except `binding_id` |

Version literals are exact `v0.1` strings unless a field table states a
profile-specific literal. Ordered tuples reject duplicates and reordering
where order is semantic.

## 9. SemanticAddressV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `address_profile_version` | `str` | Exactly `v0.1` |
| 2 | `namespace` | `str` | Bounded canonical owner/tenant partition |
| 3 | `domain` | `str` | Stable domain class |
| 4 | `subject_class` | `str` | Stable subject class |
| 5 | `intent_class` | `str` | Stable meaning intent |
| 6 | `meaning_schema_id` | `str` | Canonical meaning schema family |
| 7 | `meaning_schema_version` | `str` | Exact schema version |
| 8 | `semantic_address_id` | `str` | Rebuilt canonical ID |

Canonical ID:

```text
"drsaddr_v01:" + SHA256(
  domain-separated canonical bytes
  of the exact seven ordered fields
)
```

The identity excludes user identity, exact person identity, exact query text,
query ID, exact current time, `TimeEnvelope`, `TemporalQuery`, Root decision,
local Root ID, policy version, execution mode, retrieval score, similarity
score, GT score, lifecycle state, pointer identity, artifact identity, and
ReuseCertificate. Dynamic context belongs in query constraints and authority
evidence.

`namespace` may establish a bounded owner or tenant partition. It must match
the canonical identifier grammar, have at most 128 ASCII bytes, and must not
contain an unbounded raw user identity.

## 10. MemoryPointerV01 and ArtifactPointerV01

### MemoryPointerV01

`MemoryPointerV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `pointer_version` | `str` | Exactly `v0.1` |
| 2 | `pointer_id` | `str` | Rebuilt `drsmem_v01:` ID |
| 3 | `storage_class` | `str` | Exact memory storage class |
| 4 | `object_reference` | `str` | Canonical local object reference |
| 5 | `content_sha256` | `str` | Lowercase 64-hex digest |
| 6 | `record_class` | `str` | Exact record-class identifier |
| 7 | `byte_length` | `int` or `None` | Exact nonnegative int when known |
| 8 | `access_policy_id` | `str` | Required canonical policy reference |
| 9 | `sensitivity_class` | `str` | Exact sensitivity class |
| 10 | `allowed_use_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 11 | `forbidden_use_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 12 | `summary_read_permitted` | `bool` | Exact policy fact |
| 13 | `payload_read_permitted` | `bool` | Exact policy fact |
| 14 | `creates_authority` | `bool` | Exactly `False` |
| 15 | `creates_permission` | `bool` | Exactly `False` |

Exact `MemoryPointerV01.storage_class` vocabulary:

```text
LOCAL_MEANING_RECORD
LOCAL_LINEAGE_SET
LOCAL_CONFLICT_SET
LOCAL_DEADEND_PROOF
```

### ArtifactPointerV01

`ArtifactPointerV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `pointer_version` | `str` | Exactly `v0.1` |
| 2 | `pointer_id` | `str` | Rebuilt `drsart_v01:` ID |
| 3 | `storage_class` | `str` | Exact artifact storage class |
| 4 | `object_reference` | `str` | Canonical local object reference |
| 5 | `content_sha256` | `str` | Lowercase 64-hex digest |
| 6 | `media_type` | `str` | Exact bounded media type |
| 7 | `byte_length` | `int` or `None` | Exact nonnegative int when known |
| 8 | `access_policy_id` | `str` | Required canonical policy reference |
| 9 | `sensitivity_class` | `str` | Exact sensitivity class |
| 10 | `allowed_use_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 11 | `forbidden_use_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 12 | `summary_read_permitted` | `bool` | Exact policy fact |
| 13 | `payload_read_permitted` | `bool` | Exact policy fact |
| 14 | `creates_authority` | `bool` | Exactly `False` |
| 15 | `creates_permission` | `bool` | Exactly `False` |

Exact `ArtifactPointerV01.storage_class` vocabulary:

```text
LOCAL_DOCUMENT
LOCAL_AUDIT_TRACE
LOCAL_SEALED_EVIDENCE
```

Exact sensitivity vocabulary:

```text
PUBLIC
INTERNAL
CONFIDENTIAL_REFERENCE_ONLY
SECRET_REFERENCE_ONLY
```

No external or global storage class is executable in G2-B. A pointer neither
grants authority nor permission and is never resolved solely because it
exists. Summary access requires `summary_read_permitted`, a matching
`access_policy_id`, an allowed requested use, and no forbidden requested use.
Payload access additionally requires `payload_read_permitted`, exact local
Root approval, and descent-budget capacity. Pointer metadata contains no raw
secret.

## 11. LineageEdgeV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `lineage_edge_version` | `str` | Exactly `v0.1` |
| 2 | `lineage_edge_id` | `str` | Rebuilt canonical ID |
| 3 | `source_meaning_record_id` | `str` | Canonical source record |
| 4 | `target_meaning_record_id` | `str` | Canonical target record |
| 5 | `relation_class` | `str` | Exact relation vocabulary |
| 6 | `claim_dimension` | `str` | Exact bounded claim dimension |
| 7 | `source_history_hash` | `str` | Lowercase 64-hex digest |
| 8 | `evidence_ref_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 9 | `created_at` | `int` | Signed-int64 UTC epoch seconds |
| 10 | `recording_component` | `str` | Canonical component ID |
| 11 | `creates_authority` | `bool` | Exactly `False` |
| 12 | `transfers_authority` | `bool` | Exactly `False` |

Exact relation vocabulary:

```text
DERIVED_FROM
SUPPORTS
WARNS_AGAINST
CONTRADICTS
SUPERSEDES
REPLACES
SAME_TRACE
REFERENCES
BLOCKED_BY_POLICY
DEGRADED_FROM
```

Lineage informs provenance, conflict, warning, and bounded graph descent. It
does not decide truth, transfer authority, or authorize reuse. Cycles,
self-edges, unknown relations, duplicate edge IDs, and unbounded traversal fail
closed.

## 12. DRSAuthorityEnvelopeV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `authority_envelope_version` | `str` | Exactly `v0.1` |
| 2 | `authority_envelope_id` | `str` | Rebuilt canonical ID |
| 3 | `authority_class` | `str` | Exact source authority class |
| 4 | `owning_local_root_id` | `str` or `None` | Required for Root-accepted classes |
| 5 | `source_root_decision_input_id` | `str` or `None` | Exact Root input reference |
| 6 | `source_root_decision_id` | `str` or `None` | Exact Root result reference |
| 7 | `source_root_decision_hash` | `str` or `None` | Exact result hash |
| 8 | `authority_scope_fingerprint` | `str` | Lowercase 64-hex digest |
| 9 | `root_acceptance_state` | `str` | Exact acceptance state |
| 10 | `recording_component` | `str` | Canonical component ID |
| 11 | `creates_authority` | `bool` | Exactly `False` |
| 12 | `creates_permission` | `bool` | Exactly `False` |
| 13 | `action_permission_present` | `bool` | Exactly `False` |

Exact authority classes:

```text
UNTRUSTED_SEMANTIC_DRAFT
CONNECTOR_OBSERVATION
EVIDENCE_CANDIDATE
ROOT_ACCEPTED_CONTEXT
ROOT_ACCEPTED_WORK
ROOT_FINAL_REFERENCE
ACTION_HISTORY_REFERENCE
```

Exact Root acceptance states:

```text
UNREVIEWED
ACCEPTED_CONTEXT
ACCEPTED_WORK
REJECTED
QUARANTINED
```

Only exact validated existing Root evidence may support a Root-accepted class.
The envelope records provenance; it does not create or transfer authority.
`ROOT_FINAL_REFERENCE` remains a historical reference and cannot by itself
authorize present reuse.

## 13. DRSTimeEnvelopeV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `time_envelope_version` | `str` | Exactly `v0.1` |
| 2 | `time_envelope_id` | `str` | Rebuilt canonical ID |
| 3 | `pt_created_at` | `int` | Signed-int64 UTC epoch seconds |
| 4 | `kt_as_of` | `int` | Signed-int64 UTC epoch seconds |
| 5 | `et_observed_at` | `int` | Signed-int64 UTC epoch seconds |
| 6 | `ct_context_anchor` | `int` | Signed-int64 UTC epoch seconds |
| 7 | `ttl_seconds` | `int` | Positive signed-int64 seconds |
| 8 | `valid_from` | `int` | Signed-int64 UTC epoch seconds |
| 9 | `valid_to` | `int` | Signed-int64 UTC epoch seconds |
| 10 | `source_observed_at` | `int` | Signed-int64 UTC epoch seconds |
| 11 | `source_reported_at` | `int` | Signed-int64 UTC epoch seconds |
| 12 | `system_ingested_at` | `int` | Signed-int64 UTC epoch seconds |
| 13 | `system_verified_at` | `int` | Signed-int64 UTC epoch seconds |
| 14 | `freshness_policy_id` | `str` | Exact versioned policy ID |

Every time integer must satisfy `-(2**63) <= value <= 2**63 - 1`; `bool`,
float, `Decimal`, numeric string, int subclass, coercion, and ambient current
time are rejected. `pt_created_at + ttl_seconds` must not overflow signed
int64.

Query-time half-open laws:

```text
valid_from <= as_of < valid_to
as_of < pt_created_at + ttl_seconds
```

At exact `valid_to`, the record is invalid for that query. At exact TTL expiry,
the record is expired for freshness use. The following distinctions are
binding:

```text
TTL expiry != claim invalidity
validity interval != freshness
freshness != authority
newer != authoritative
record age score != temporal hard-gate result
```

Computed query freshness is not stored as immutable truth in this envelope. It
belongs in `QueryEvaluationStateV01`. Legacy RFC3339 or ISO values may enter
only through a strict exact compatibility parser, followed by explicit
projection and target validation.

## 14. MeaningRecordV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `meaning_record_version` | `str` | Exactly `v0.1` |
| 2 | `meaning_record_id` | `str` | Rebuilt canonical ID |
| 3 | `semantic_address` | `SemanticAddressV01` | Exact validated address |
| 4 | `predecessor_record_id` | `str` or `None` | Prior immutable version |
| 5 | `supersession_reason` | `str` or `None` | Required when predecessor exists |
| 6 | `safe_summary` | `str` | Bounded sanitized summary |
| 7 | `semantic_tags` | `tuple[str, ...]` | Exact, unique, ordered |
| 8 | `resonance_reason` | `str` | Bounded reason text |
| 9 | `memory_pointers` | `tuple[MemoryPointerV01, ...]` | Exact, unique IDs |
| 10 | `artifact_pointers` | `tuple[ArtifactPointerV01, ...]` | Exact, unique IDs |
| 11 | `source_reference_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 12 | `lineage_edges` | `tuple[LineageEdgeV01, ...]` | Exact, unique IDs |
| 13 | `time_envelope` | `DRSTimeEnvelopeV01` | Exact validated envelope |
| 14 | `authority_envelope` | `DRSAuthorityEnvelopeV01` | Exact validated envelope |
| 15 | `persistent_lifecycle_state` | `str` | Exact persistent state |
| 16 | `risk_hints` | `tuple[str, ...]` | Advisory, bounded, ordered |
| 17 | `conflict_hints` | `tuple[str, ...]` | Advisory, bounded, ordered |
| 18 | `reuse_policy_class` | `str` | Exact reuse-class vocabulary |
| 19 | `policy_version` | `str` | Exact policy version |
| 20 | `schema_versions` | `tuple[str, ...]` | Exact, unique, ordered |
| 21 | `content_fingerprint` | `str` | Lowercase 64-hex digest |
| 22 | `recording_component` | `str` | Canonical component ID |
| 23 | `local_reference_kernel_scope` | `str` | Exactly `LOCAL_REFERENCE_KERNEL` |
| 24 | `creates_authority` | `bool` | Exactly `False` |
| 25 | `creates_permission` | `bool` | Exactly `False` |

Exact persistent lifecycle vocabulary:

```text
ACTIVE
COMPLETED
REJECTED
QUARANTINED
DEADEND
ARCHIVED
```

Dense payload is forbidden. A lifecycle change creates a new immutable record
version with predecessor and reason; it does not mutate the old record.
Persistent lifecycle state is not query-local evaluation state and cannot
substitute for it. Summary, tags, reasons, hints, and metadata are bounded and
sanitized; dense content remains behind pointers.

`predecessor_record_id` and `supersession_reason` are either both `None` or
both exact nonempty strings. A superseding record also contains exactly one
coherent `SUPERSEDES` or `REPLACES` lineage edge whose canonical edge identity
is the supersession evidence identity.

## 15. DRSTemporalQueryV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `temporal_query_version` | `str` | Exactly `v0.1` |
| 2 | `query_id` | `str` | Rebuilt canonical ID |
| 3 | `query_mode` | `str` | Exact mode vocabulary |
| 4 | `semantic_address_id` | `str` | Exact canonical address |
| 5 | `scope_fingerprint` | `str` | Lowercase 64-hex digest |
| 6 | `as_of` | `int` | Signed-int64 UTC epoch seconds |
| 7 | `evaluation_time` | `int` | Explicit signed-int64 time |
| 8 | `evaluation_time_source` | `str` | Exact source vocabulary |
| 9 | `time_range_start` | `int` | Signed-int64, inclusive |
| 10 | `time_range_end` | `int` | Signed-int64, exclusive |
| 11 | `required_time_axes` | `tuple[str, ...]` | Exact, unique, ordered |
| 12 | `freshness_policy_id` | `str` | Exact policy ID |
| 13 | `max_age_seconds` | `int` | Exact nonnegative signed-int64 |
| 14 | `domain` | `str` | Must match address domain |
| 15 | `risk_class` | `str` | Exact bounded risk class |
| 16 | `reuse_intent` | `str` | Exact intent vocabulary |
| 17 | `requested_reuse_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 18 | `required_evidence_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 19 | `forbidden_changes` | `tuple[str, ...]` | Exact, unique, ordered |
| 20 | `policy_version` | `str` | Exact policy version |
| 21 | `schema_versions` | `tuple[str, ...]` | Exact, unique, ordered |
| 22 | `owning_local_root_id` | `str` | Exact local Root ID |

Exact query modes:

```text
CURRENT_DECISION
HISTORICAL_AS_OF
AUDIT_REPLAY
TREND_ANALYSIS
MEMORY_CONTEXT_ONLY
DIRECT_REUSE_CANDIDATE
```

Exact evaluation-time sources:

```text
INJECTED_CURRENT_DECISION_TIME
RECORDED_HISTORICAL_AS_OF_TIME
RECORDED_AUDIT_REPLAY_TIME
INJECTED_ANALYSIS_TIME
```

Exact reuse intents:

```text
CONTEXT
INFORMATIONAL_SHORTCUT_CONSIDERATION
WARNING_LOOKUP
HISTORY_INSPECTION
```

Only safe non-action informational queries in `CURRENT_DECISION` and
`DIRECT_REUSE_CANDIDATE` may become eligible for `ANSWER_SHORTCUT`. Other
modes may produce context, history, warning, trend, audit evidence, or a rerun
requirement, but no direct informational shortcut in G2-B v0.1.

`time_range_start <= as_of < time_range_end` is required. Every evaluation uses
the explicit `evaluation_time` and source; no ambient clock is consulted.

## 16. QueryEvaluationStateV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `query_evaluation_version` | `str` | Exactly `v0.1` |
| 2 | `query_evaluation_id` | `str` | Rebuilt canonical ID |
| 3 | `query_id` | `str` | Exact query cross-binding |
| 4 | `semantic_address_id` | `str` | Exact address cross-binding |
| 5 | `meaning_record_id` | `str` | Exact record cross-binding |
| 6 | `query_state` | `str` | Exact query-state vocabulary |
| 7 | `evaluated_at` | `int` | Exact injected evaluation time |
| 8 | `evaluation_time_source` | `str` | Must match query |
| 9 | `temporal_hard_gate_passed` | `bool` | Independently recomputed |
| 10 | `validity_interval_passed` | `bool` | Independently recomputed |
| 11 | `ttl_freshness_passed` | `bool` | Independently recomputed |
| 12 | `required_time_axes_passed` | `bool` | Exact axis check |
| 13 | `scope_passed` | `bool` | Exact address/query scope |
| 14 | `lifecycle_passed` | `bool` | Persistent-state gate |
| 15 | `policy_compatible` | `bool` | Exact policy match |
| 16 | `schema_compatible` | `bool` | Exact schema match |
| 17 | `provenance_passed` | `bool` | Exact provenance gate |
| 18 | `authority_envelope_passed` | `bool` | Exact envelope gate |
| 19 | `required_evidence_passed` | `bool` | Exact evidence gate |
| 20 | `forbidden_changes_passed` | `bool` | Exact dependency check |
| 21 | `conflict_passed` | `bool` | Independently derived |
| 22 | `quarantine_passed` | `bool` | Exact persistent state |
| 23 | `deadend_passed` | `bool` | Exact persistent state |
| 24 | `action_intent_passed` | `bool` | Non-action classification |
| 25 | `g2a_action_history_passed` | `bool` | Exact history fence |
| 26 | `permission_boundary_passed` | `bool` | No prior permission reuse |
| 27 | `current_freshness_units` | `int` | Exact integer score units |
| 28 | `observed_evidence_fingerprint` | `str` | Lowercase 64-hex digest |
| 29 | `checked_dependency_fingerprint` | `str` | Lowercase 64-hex digest |
| 30 | `source_history_hash` | `str` | Lowercase 64-hex digest |
| 31 | `action_history_binding_id` | `str` or `None` | Required for action history |
| 32 | `eligible_for_ranking` | `bool` | True only if every hard gate passes |
| 33 | `reason_codes` | `tuple[str, ...]` | Stable, ordered, exact |
| 34 | `creates_authority` | `bool` | Exactly `False` |
| 35 | `creates_permission` | `bool` | Exactly `False` |

Exact query-state vocabulary:

```text
FRESH_CANDIDATE
STALE_CONTEXT_ONLY
HISTORICAL_ONLY
WARNING_ONLY
RERUN_REQUIRED
BLOCKED_BY_TIME
BLOCKED_BY_SCOPE
BLOCKED_BY_POLICY
BLOCKED_BY_PROVENANCE
BLOCKED_BY_CONFLICT
BLOCKED_BY_QUARANTINE
BLOCKED_BY_DEADEND
BLOCKED_BY_REQUIRED_EVIDENCE
BLOCKED_BY_FORBIDDEN_CHANGE
BLOCKED_BY_ACTION_HISTORY
BLOCKED_BY_ACTION_INTENT
```

The evaluation is pure and immutable. It recomputes time fitness and every
hard gate from validated source objects. It does not trust a transported
freshness boolean or class and is never written back to persistent record
lifecycle.

## 17. Hard Eligibility Gates

Every candidate is evaluated exactly once in this conceptual order:

```text
exact type and identity validation
-> semantic address and query scope
-> persistent lifecycle gate
-> temporal hard gate
-> policy compatibility gate
-> schema compatibility gate
-> provenance and authority-envelope gate
-> required evidence gate
-> forbidden-change gate
-> conflict gate
-> quarantine/deadend gate
-> action-intent gate
-> G2-A action-history gate
-> permission boundary
-> eligible candidate set
-> deterministic ranking of eligible candidates only
```

The exact gate laws are:

| Gate | Required result for eligibility | Stable failure reason |
| --- | --- | --- |
| Type and identity | Exact canonical types and rebuilt identities | `drs_exact_type_or_identity_invalid` |
| Address and scope | Address, domain, namespace, intent, and scope match | `drs_address_scope_mismatch` |
| Lifecycle | `ACTIVE` or allowed informational `COMPLETED` record | `drs_persistent_lifecycle_blocked` |
| Time | Mode-specific interval, axes, and freshness law passes | `drs_temporal_hard_gate_failed` |
| Policy | Exact policy version and policy class compatible | `drs_policy_version_mismatch` |
| Schema | Exact ordered schema versions compatible | `drs_schema_version_mismatch` |
| Provenance | Source identity, hash, lineage, and authority envelope valid | `drs_provenance_invalid` |
| Required evidence | Every exact required class observed | `drs_required_evidence_missing` |
| Forbidden changes | No forbidden change detected | `drs_forbidden_change_detected` |
| Conflict | Independent conflict set is clear | `drs_conflict_blocked` |
| Quarantine/deadend | Neither state nor bounded lineage neighborhood is blocked | `drs_quarantine_or_deadend_blocked` |
| Action intent | Request is safe non-action informational | `drs_action_intent_shortcut_forbidden` |
| G2-A history | No disallowed action-history source | `drs_action_history_shortcut_forbidden` |
| Permission | No historical evidence is treated as current permission | `drs_permission_boundary_failed` |

Required evidence-class vocabulary:

```text
SOURCE_IDENTITY
SOURCE_INTEGRITY
PROVENANCE_CHAIN
TIME_FITNESS
POLICY_COMPATIBILITY
SCHEMA_COMPATIBILITY
CONFLICT_CLEARANCE
ROOT_DECISION
SOURCE_HISTORY
```

Ineligible candidates may remain visible in explanation, context, history, or
warning results. They must never become the selected candidate, influence the
best eligible candidate identity, create Root shortcut evidence, or receive a
ReuseCertificate.

Conflict, quarantine, deadend, and risky-proximity evidence is derived from
the exact selected record and Root-approved bounded lineage or conflict reads.
There is no global taint and no caller-supplied proximity fact.

```text
EligibleCandidates =
  candidates passing every hard gate

RankedCandidates =
  deterministic ranking over EligibleCandidates only
```

There is no global-best-before-eligibility behavior and no fallback to an
ineligible high-score candidate.

## 18. Deterministic Eligible-Only Ranking

Canonical ranking uses exact signed integer score units. Binary floats,
`Decimal`, numeric strings, coercion, and noncanonical score ranges are
rejected.

Each non-penalty component is an exact integer in `[0, 10000]`. Each penalty is
an exact integer in `[0, 10000]`. The versioned weight profile is:

| Component | Weight |
| --- | ---: |
| `semantic_similarity_units` | 3000 |
| `freshness_units` | 2000 |
| `source_authority_prior_units` | 1500 |
| `lineage_proximity_units` | 1000 |
| `historical_utility_units` | 1500 |
| `gt_advisory_prior_units` | 1000 |
| `conflict_penalty_units` | 1500 |
| `risk_penalty_units` | 1000 |
| `retrieval_cost_units` | 500 |

Exact total:

```text
total_score_units =
    3000 * semantic_similarity_units
  + 2000 * freshness_units
  + 1500 * source_authority_prior_units
  + 1000 * lineage_proximity_units
  + 1500 * historical_utility_units
  + 1000 * gt_advisory_prior_units
  - 1500 * conflict_penalty_units
  - 1000 * risk_penalty_units
  -  500 * retrieval_cost_units
```

The total must remain in signed-int64 range. Ranking order is descending
`total_score_units`, then ascending canonical `resolution_candidate_id`.
Candidate ID is the final deterministic tie-break.

Score ranks eligible candidates only. Score, GT, semantic similarity,
freshness, source prior, lineage proximity, and historical utility create no
authority or permission.

## 19. ResolutionCandidateV01 and DRSResolutionReportV01

### ResolutionCandidateV01

`ResolutionCandidateV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `resolution_candidate_version` | `str` | Exactly `v0.1` |
| 2 | `resolution_candidate_id` | `str` | Rebuilt canonical ID |
| 3 | `query_id` | `str` | Exact query binding |
| 4 | `semantic_address_id` | `str` | Exact address binding |
| 5 | `meaning_record_id` | `str` | Exact record binding |
| 6 | `query_evaluation_id` | `str` | Exact eligible evaluation |
| 7 | `safe_summary` | `str` | Bounded sanitized summary |
| 8 | `evidence_ref_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 9 | `source_history_hash` | `str` | Lowercase 64-hex digest |
| 10 | `action_history_binding_id` | `str` or `None` | Exact optional history binding |
| 11 | `semantic_similarity_units` | `int` | Exact range `[0, 10000]` |
| 12 | `freshness_units` | `int` | Exact range `[0, 10000]` |
| 13 | `source_authority_prior_units` | `int` | Exact range `[0, 10000]` |
| 14 | `lineage_proximity_units` | `int` | Exact range `[0, 10000]` |
| 15 | `historical_utility_units` | `int` | Exact range `[0, 10000]` |
| 16 | `gt_advisory_prior_units` | `int` | Exact range `[0, 10000]` |
| 17 | `conflict_penalty_units` | `int` | Exact range `[0, 10000]` |
| 18 | `risk_penalty_units` | `int` | Exact range `[0, 10000]` |
| 19 | `retrieval_cost_units` | `int` | Exact range `[0, 10000]` |
| 20 | `total_score_units` | `int` | Exact formula rebuild |
| 21 | `eligible_for_ranking` | `bool` | Exactly `True` |
| 22 | `reason_codes` | `tuple[str, ...]` | Exactly empty for eligible candidate |
| 23 | `creates_authority` | `bool` | Exactly `False` |
| 24 | `creates_permission` | `bool` | Exactly `False` |
| 25 | `creates_final_output` | `bool` | Exactly `False` |

A `ResolutionCandidateV01` is built only after all hard gates pass.

### DRSResolutionReportV01

`DRSResolutionReportV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `report_version` | `str` | Exactly `v0.1` |
| 2 | `report_id` | `str` | Rebuilt canonical ID |
| 3 | `semantic_address` | `SemanticAddressV01` | Exact validated address |
| 4 | `query` | `DRSTemporalQueryV01` | Exact validated query |
| 5 | `source_projections` | `tuple[LegacyDRSProjectionV01, ...]` | Exact, unique identities, ordered |
| 6 | `source_records` | `tuple[MeaningRecordV01, ...]` | Exact immutable source objects |
| 7 | `query_evaluations` | `tuple[QueryEvaluationStateV01, ...]` | One per source candidate |
| 8 | `eligible_candidates` | `tuple[ResolutionCandidateV01, ...]` | Eligible objects only |
| 9 | `ranked_candidate_ids` | `tuple[str, ...]` | Exact deterministic order |
| 10 | `selected_candidate_id` | `str` or `None` | First eligible rank or none |
| 11 | `retrieval_plan` | `RetrievalPlanV01` | Exact validated plan |
| 12 | `memory_descent_result` | `MemoryDescentResultV01` or `None` | Exact optional result |
| 13 | `root_shortcut_projection` | `RootShortcutAuthorizationProjectionV01` or `None` | Exact optional projection |
| 14 | `reuse_certificate` | `ReuseCertificateV01` or `None` | Exact optional certificate |
| 15 | `context_only_record_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 16 | `historical_only_record_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 17 | `warning_only_record_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 18 | `rerun_required_record_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 19 | `blocked_record_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 20 | `persistent_records_unchanged` | `bool` | Exactly `True` |
| 21 | `provider_calls` | `int` | Exactly `0` |
| 22 | `network_calls` | `int` | Exactly `0` |
| 23 | `gemini_calls` | `int` | Exactly `0` |
| 24 | `external_drs_calls` | `int` | Exactly `0` |
| 25 | `connector_calls` | `int` | Exactly `0` |
| 26 | `real_world_effects_count` | `int` | Exactly `0` on proven success |
| 27 | `final_status` | `str` | `PASS` or `FAIL_CLOSED` |
| 28 | `reason_codes` | `tuple[str, ...]` | Stable ordered reasons |

Unknown operation accounting is `-1`, never normalized to proven zero. The
report validator independently rebuilds evaluations, eligible set, score,
rank, selection, plan, descent, Root projection, and certificate
cross-bindings from the transported exact nested objects. A transported `PASS`
label or bare nested identity cannot supply proof.

## 20. RetrievalPlanV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `retrieval_plan_version` | `str` | Exactly `v0.1` |
| 2 | `retrieval_plan_id` | `str` | Rebuilt canonical ID |
| 3 | `query_id` | `str` | Exact query binding |
| 4 | `semantic_address_id` | `str` | Exact address binding |
| 5 | `proposed_record_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 6 | `proposed_memory_pointer_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 7 | `proposed_artifact_pointer_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 8 | `requested_descent_class` | `str` | Exact descent class |
| 9 | `proposed_budget_id` | `str` | Exact budget binding |
| 10 | `required_access_policy_ids` | `tuple[str, ...]` | Exact, unique, ordered |
| 11 | `reason_codes` | `tuple[str, ...]` | Stable ordered reasons |
| 12 | `root_approval_required` | `bool` | Exactly `True` |
| 13 | `creates_authority` | `bool` | Exactly `False` |
| 14 | `creates_permission` | `bool` | Exactly `False` |
| 15 | `executes_read` | `bool` | Exactly `False` |

DRS proposes this plan. The plan is not an approval and performs no read.
Proposals containing external pointers, unknown storage classes, disallowed
use classes, duplicate IDs, or a budget beyond reference ceilings fail closed.

## 21. Controlled Memory Descent

Exact descent classes:

```text
SUMMARY_ONLY
OPEN_ONE_ARTIFACT
OPEN_LINEAGE_NEIGHBORHOOD
OPEN_CONFLICT_SET
OPEN_DEADEND_PROOF
OPEN_FULL_TRACE
```

### MemoryDescentBudgetV01

`MemoryDescentBudgetV01` exact ordered fields:

| Position | Field | Exact type | Reference-kernel ceiling |
| --- | --- | --- | ---: |
| 1 | `memory_descent_budget_version` | `str` | Exactly `v0.1` |
| 2 | `memory_descent_budget_id` | `str` | Rebuilt canonical ID |
| 3 | `max_depth` | `int` | 3 |
| 4 | `max_records_opened` | `int` | 32 |
| 5 | `max_pointers_opened` | `int` | 16 |
| 6 | `max_artifacts_opened` | `int` | 4 |
| 7 | `max_bytes_opened` | `int` | 1048576 |
| 8 | `max_lineage_edges` | `int` | 32 |
| 9 | `max_conflict_records` | `int` | 16 |

All counters are exact nonnegative ints. Root may approve equal or smaller
bounds and may never expand them. `SUMMARY_ONLY` opens no payload.
`OPEN_ONE_ARTIFACT` opens at most one artifact and reaches depth at most one.

### MemoryDescentRequestV01

`MemoryDescentRequestV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `memory_descent_request_version` | `str` | Exactly `v0.1` |
| 2 | `memory_descent_request_id` | `str` | Rebuilt canonical ID |
| 3 | `retrieval_plan_id` | `str` | Exact plan binding |
| 4 | `query_id` | `str` | Exact query binding |
| 5 | `owning_local_root_id` | `str` | Exact local Root |
| 6 | `root_kernel_id` | `str` | Existing kernel identity |
| 7 | `root_decision_input_id` | `str` | Exact validated input |
| 8 | `root_decision_id` | `str` | Exact validated result |
| 9 | `root_decision_hash` | `str` | Exact result hash |
| 10 | `requested_descent_class` | `str` | Must match plan |
| 11 | `approved_descent_class` | `str` | Equal or narrower |
| 12 | `proposed_budget_id` | `str` | Must match plan |
| 13 | `approved_budget` | `MemoryDescentBudgetV01` | Equal or smaller |
| 14 | `approved_record_ids` | `tuple[str, ...]` | Subset of plan |
| 15 | `approved_memory_pointer_ids` | `tuple[str, ...]` | Subset of plan |
| 16 | `approved_artifact_pointer_ids` | `tuple[str, ...]` | Subset of plan |
| 17 | `root_approved` | `bool` | Exactly `True` after validation |
| 18 | `reason_codes` | `tuple[str, ...]` | Exactly empty on approval |
| 19 | `creates_permission` | `bool` | Exactly `False` |
| 20 | `creates_authority` | `bool` | Exactly `False` |

### MemoryDescentResultV01

`MemoryDescentResultV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `memory_descent_result_version` | `str` | Exactly `v0.1` |
| 2 | `memory_descent_result_id` | `str` | Rebuilt canonical ID |
| 3 | `memory_descent_request_id` | `str` | Exact request binding |
| 4 | `retrieval_plan_id` | `str` | Exact plan binding |
| 5 | `query_id` | `str` | Exact query binding |
| 6 | `executed_descent_class` | `str` | Must equal approved class |
| 7 | `applied_budget_id` | `str` | Exact approved budget |
| 8 | `opened_record_ids` | `tuple[str, ...]` | Exact ordered observations |
| 9 | `opened_memory_pointer_ids` | `tuple[str, ...]` | Exact ordered observations |
| 10 | `opened_artifact_pointer_ids` | `tuple[str, ...]` | Exact ordered observations |
| 11 | `traversed_lineage_edge_ids` | `tuple[str, ...]` | Exact ordered observations |
| 12 | `opened_conflict_record_ids` | `tuple[str, ...]` | Exact ordered observations |
| 13 | `depth_reached` | `int` | Within approved budget |
| 14 | `records_opened` | `int` | Exact tuple/count coherence |
| 15 | `pointers_opened` | `int` | Exact tuple/count coherence |
| 16 | `artifacts_opened` | `int` | Exact tuple/count coherence |
| 17 | `bytes_opened` | `int` | Exact observed bytes |
| 18 | `lineage_edges_traversed` | `int` | Exact tuple/count coherence |
| 19 | `conflict_records_opened` | `int` | Exact tuple/count coherence |
| 20 | `safe_summaries` | `tuple[str, ...]` | Bounded sanitized summaries |
| 21 | `opened_payload_fingerprints` | `tuple[str, ...]` | Hashes, not payloads |
| 22 | `limits_respected` | `bool` | Exactly `True` on success |
| 23 | `reason_codes` | `tuple[str, ...]` | Stable ordered reasons |
| 24 | `creates_authority` | `bool` | Exactly `False` |
| 25 | `creates_permission` | `bool` | Exactly `False` |
| 26 | `real_world_effects_count` | `int` | Exactly `0` |

No descent request executes without exact validation of
`RootDecisionKernelV01`, `RootDecisionInputV01`, and
`RootDecisionResultV01` for the correct local Root. The DRS proposes; Root
approves class and budget; the pure local resolver executes only the approved
bounded read.

## 22. RootShortcutAuthorizationProjectionV01

G2-B creates no new Root family or shortcut authority kernel. Shortcut
approval validates the exact existing triple:

```text
RootDecisionKernelV01
RootDecisionInputV01
RootDecisionResultV01
```

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `root_shortcut_projection_version` | `str` | Exactly `v0.1` |
| 2 | `root_shortcut_projection_id` | `str` | Rebuilt canonical ID |
| 3 | `owning_local_root_id` | `str` | Exact local Root |
| 4 | `root_kernel_id` | `str` | Exact existing kernel |
| 5 | `root_decision_input_id` | `str` | Exact input identity |
| 6 | `root_decision_id` | `str` | Exact result identity |
| 7 | `root_decision_hash` | `str` | Exact result hash |
| 8 | `selected_candidate_id` | `str` | Exact selected eligible candidate |
| 9 | `semantic_address_id` | `str` | Exact address binding |
| 10 | `meaning_record_id` | `str` | Exact record binding |
| 11 | `query_id` | `str` | Exact query binding |
| 12 | `query_evaluation_id` | `str` | Exact evaluation binding |
| 13 | `allowed_reuse_class` | `str` | Exact enabled class |
| 14 | `scope_fingerprint` | `str` | Lowercase 64-hex digest |
| 15 | `policy_version` | `str` | Exact policy version |
| 16 | `schema_versions` | `tuple[str, ...]` | Exact, unique, ordered |
| 17 | `valid_from` | `int` | Signed-int64, inclusive |
| 18 | `valid_to` | `int` | Signed-int64, exclusive |
| 19 | `root_shortcut_policy_ref` | `str` | Exact versioned policy ref |
| 20 | `carries_validated_authority_evidence` | `bool` | Exactly `True` |
| 21 | `creates_authority` | `bool` | Exactly `False` |
| 22 | `creates_permission` | `bool` | Exactly `False` |
| 23 | `creates_action_commit_packet` | `bool` | Exactly `False` |
| 24 | `creates_receipt` | `bool` | Exactly `False` |
| 25 | `creates_effect` | `bool` | Exactly `False` |
| 26 | `creates_final_output` | `bool` | Exactly `False` |

The projection carries validated authority evidence. It is not a Root
decision, creates no permission, and cannot construct a final output. Its
validator independently validates the existing Root triple once, exact local
Root ownership, selected candidate, scope, validity, policy, schema, and query
cross-bindings.

`RootShortcutAllowed` is a derived use-time result, not a new dataclass,
transported authority fact, caller input, or identity field. It is true only
when the exact Root projection and ReuseCertificate both validate against the
same current objects and explicit use time.

## 23. ReuseCertificateV01

Exact operational reuse-class vocabulary:

```text
CONTEXT_ONLY
ANSWER_SHORTCUT
ROUTE_SHORTCUT
SEALED_REPLAY_SHORTCUT
PROTOCOL_PREPARATION_SHORTCUT
ACTION_SHORTCUT_NOT_ENABLED_IN_REFERENCE_KERNEL
```

Operationally enabled in G2-B v0.1:

```text
CONTEXT_ONLY
ANSWER_SHORTCUT
```

Declared but not executable until later gates:

```text
ROUTE_SHORTCUT
SEALED_REPLAY_SHORTCUT
PROTOCOL_PREPARATION_SHORTCUT
```

Always disabled:

```text
ACTION_SHORTCUT_NOT_ENABLED_IN_REFERENCE_KERNEL
```

A disabled class fails closed and never silently downgrades into an enabled
shortcut. An explicit result law with a stable reason may produce a separate
`CONTEXT_ONLY` outcome.

`ReuseCertificateV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `certificate_version` | `str` | Exactly `v0.1` |
| 2 | `certificate_id` | `str` | Rebuilt canonical ID |
| 3 | `semantic_address_id` | `str` | Exact address binding |
| 4 | `meaning_record_id` | `str` | Exact record binding |
| 5 | `query_id` | `str` | Exact query binding |
| 6 | `query_evaluation_id` | `str` | Exact evaluation binding |
| 7 | `resolution_candidate_id` | `str` | Exact selected candidate |
| 8 | `root_shortcut_authorization_projection_id` | `str` | Exact projection binding |
| 9 | `owning_local_root_id` | `str` | Exact local Root |
| 10 | `root_decision_input_id` | `str` | Exact Root input |
| 11 | `root_decision_id` | `str` | Exact Root result |
| 12 | `root_decision_hash` | `str` | Exact Root result hash |
| 13 | `case_type` | `str` | Exactly `NON_ACTION_INFORMATIONAL` |
| 14 | `scope_fingerprint` | `str` | Lowercase 64-hex digest |
| 15 | `required_evidence_classes` | `tuple[str, ...]` | Exact, unique, ordered |
| 16 | `observed_evidence_fingerprint` | `str` | Lowercase 64-hex digest |
| 17 | `forbidden_changes` | `tuple[str, ...]` | Exact, unique, ordered |
| 18 | `checked_dependency_fingerprint` | `str` | Lowercase 64-hex digest |
| 19 | `valid_from` | `int` | Signed-int64, inclusive |
| 20 | `valid_to` | `int` | Signed-int64, exclusive |
| 21 | `reuse_class` | `str` | Exact enabled class |
| 22 | `policy_version` | `str` | Exact policy version |
| 23 | `schema_versions` | `tuple[str, ...]` | Exact, unique, ordered |
| 24 | `root_shortcut_policy_ref` | `str` | Exact policy reference |
| 25 | `source_history_hash` | `str` | Lowercase 64-hex digest |
| 26 | `action_history_binding_id` | `str` or `None` | Exact optional binding |
| 27 | `issued_at` | `int` | Exact signed-int64 issue time |
| 28 | `evaluated_at` | `int` | Exact signed-int64 evaluation time |
| 29 | `creates_authority` | `bool` | Exactly `False` |
| 30 | `creates_permission` | `bool` | Exactly `False` |
| 31 | `creates_final_output` | `bool` | Exactly `False` |
| 32 | `creates_action_commit_packet` | `bool` | Exactly `False` |
| 33 | `creates_receipt` | `bool` | Exactly `False` |
| 34 | `creates_capability` | `bool` | Exactly `False` |
| 35 | `creates_effect_handle` | `bool` | Exactly `False` |
| 36 | `creates_effect` | `bool` | Exactly `False` |
| 37 | `real_world_effects_count` | `int` | Exactly `0` |
| 38 | `proves_external_truth` | `bool` | Exactly `False` |
| 39 | `proves_action_occurred` | `bool` | Exactly `False` |

Certificate identity includes every consequential field. Exact cross-profile
coherence binds the certificate, address, record, query, query evaluation,
selected candidate, Root projection, local Root, Root decision triple,
policy/schema versions, scope, half-open validity, required evidence,
forbidden-change result, dependency fingerprint, and source history. No alias
mapping, implementation synonym, case-folded equality, or omitted
consequential field is valid.

ReuseCertificate does not create authority, permission, FinalOutput,
ActionCommitPacket, receipt, capability, effect handle, external truth, or
proof that an action occurred.

## 24. Root-Created Informational Output

G2-B creates no second `FinalOutput` family. A valid informational
`ANSWER_SHORTCUT` may allow Root to construct an informational answer without
Architect or Executor only after all of these independent facts pass:

1. an eligible candidate is selected;
2. the request is classified as non-action informational;
3. the exact existing Root decision is accepted;
4. `RootShortcutAuthorizationProjectionV01` validates;
5. `ReuseCertificateV01` validates;
6. every hard gate passed;
7. the certificate remains current at use time under
   `valid_from <= use_time < valid_to`;
8. policy, schema, scope, evidence, dependencies, and source history still
   match.

The certificate and DRS do not construct the final answer. Root owns the
existing final-output boundary. A failed or unavailable shortcut continues
through the normal full pipeline when policy allows; it is not a failed user
request by itself.

## 25. Legacy Compatibility Projections

Read-only projection sources:

```text
LocalDRS dict record
schema-valid DRS record
SemanticDRSRecordInput
DRSRecordV02
DRSFreshnessEnvelope
TemporalQueryV02
```

Each source passes source-family validation, source identity validation,
explicit versioned projection, canonical target validation, and projection
coherence validation. There is no implicit duck typing, silent field dropping,
or caller-selected canonical ID.

### LegacyDRSProjectionV01

`LegacyDRSProjectionV01` exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `projection_version` | `str` | Exactly `v0.1` |
| 2 | `projection_id` | `str` | Rebuilt canonical ID |
| 3 | `source_family` | `str` | Exact source-family vocabulary |
| 4 | `source_version` | `str` | Exact observed source version |
| 5 | `source_identity` | `str` | Validated source identity |
| 6 | `source_hash` | `str` | Lowercase 64-hex source hash |
| 7 | `target_semantic_address_id` | `str` | Exact target address |
| 8 | `target_meaning_record_id` | `str` or `None` | Present only after full projection |
| 9 | `projection_profile_version` | `str` | Exactly `v0.1` |
| 10 | `fields_preserved` | `tuple[str, ...]` | Exact, unique, ordered |
| 11 | `fields_synthesized` | `tuple[str, ...]` | Exact, unique, ordered |
| 12 | `fields_unavailable` | `tuple[str, ...]` | Exact, unique, ordered |
| 13 | `downgrade_restrictions` | `tuple[str, ...]` | Exact, unique, ordered |
| 14 | `projection_status` | `str` | Exact projection outcome |
| 15 | `answer_shortcut_eligible` | `bool` | False unless evidence is complete |
| 16 | `reason_codes` | `tuple[str, ...]` | Stable ordered reasons |
| 17 | `creates_authority` | `bool` | Exactly `False` |
| 18 | `creates_permission` | `bool` | Exactly `False` |

Exact source families:

```text
LOCAL_DRS_DICT
DRS_RECORD_SCHEMA_V0
SEMANTIC_DRS_RECORD_INPUT
DRS_RECORD_V02
DRS_FRESHNESS_ENVELOPE_V02
TEMPORAL_QUERY_V02
```

Exact projection outcomes:

```text
CANONICAL_CONTEXT_ONLY
RERUN_REQUIRED
BLOCKED
PROJECTION_REJECTED
CANONICAL_COMPLETE
```

Missing safety evidence is never synthesized as `PASS`. It results in context
only, rerun required, blocked, or projection rejection. No incomplete legacy
evidence can issue `ANSWER_SHORTCUT`.

## 26. Legacy Direct-Reuse Fence

The current caller boolean `allow_direct_reuse` is only a request to consider a
shortcut. It is not authority, Root approval, a ReuseCertificate, or
sufficient evidence to skip Architect or Executor.

`hedgehog/reuse_gate.py` and old mode-router results remain compatibility
evidence only. `hedgehog/mode_router.py` stays frozen for G2-C.

G2-B4 must narrowly modify `hedgehog/root_orchestrator.py` and
`tests/test_root_orchestrator_runtime.py` so that:

```text
no valid ReuseCertificate
or
no valid RootShortcutAuthorizationProjection
means
direct shortcut not taken
```

The request may continue through the normal full pipeline. Action-like
requests never take the informational shortcut. The old direct path is a
current executable compatibility surface and must be fenced; it is not
described as harmless historical code.

## 27. G2-A History and Action-Reuse Boundary

Any source linked to ActionCommitPacket, ActionPacket transition history,
idempotency disposition history, receipt, fulfillment evidence, or sealed
action Replay requires an exact `G2AActionHistoryBindingV01`.

### G2AActionHistoryBindingV01

Exact ordered fields:

| Position | Field | Exact type | Law |
| --- | --- | --- | --- |
| 1 | `binding_version` | `str` | Exactly `v0.1` |
| 2 | `binding_id` | `str` | Rebuilt canonical ID |
| 3 | `packet_id` | `str` | Exact ActionCommitPacket ID |
| 4 | `registry_id` | `str` | Exact Registry ID |
| 5 | `transition_history_sha256` | `str` | Exact immutable history hash |
| 6 | `disposition_history_sha256` | `str` | Exact immutable history hash |
| 7 | `lifecycle_state` | `str` | Exact current validated state |
| 8 | `disposition` | `str` | Exact current validated disposition |
| 9 | `reservation_owner_packet_id` | `str` or `None` | Exact reservation owner |
| 10 | `terminal_receipt_ref` | `str` or `None` | Historical evidence only |
| 11 | `current_status_validation_id` | `str` | Exact validation evidence |
| 12 | `current_status_evaluated_at` | `int` | Explicit signed-int64 time |
| 13 | `current_status_evaluation_time_source` | `str` | Exact source |
| 14 | `shortcut_eligible` | `bool` | Exactly `False` |
| 15 | `reason_codes` | `tuple[str, ...]` | Stable ordered reasons |
| 16 | `creates_authority` | `bool` | Exactly `False` |
| 17 | `creates_permission` | `bool` | Exactly `False` |

In G2-B v0.1, any action-history source is ineligible for `ANSWER_SHORTCUT`.
Allowed outcomes are limited to:

```text
CONTEXT_ONLY
HISTORICAL_ONLY
WARNING_ONLY
RERUN_REQUIRED
BLOCKED
```

Shortcut authority is explicitly rejected for an `EXPIRED`, `REVOKED`,
`SUPERSEDED`, `BLOCKED`, or `FAILED` packet; `CONSUMED` action history;
`UNCERTAIN_CLOSED` action history; receipt history; prior permission trace; or
prior Root Final. No old packet or receipt becomes present permission. No
ReuseCertificate creates an ActionCommitPacket.

Action-like requests include payment, shipment release, ticket purchase,
ticket issue, seat reservation, ActionCommitPacket creation, receipt creation,
supplier order, and maintenance execution. They fail the informational
shortcut gate before Root shortcut projection or certificate creation.

## 28. Read Purity and Secret Boundary

The canonical route is a new pure G2-B compatibility adapter in
`hedgehog/drs_g2b_compatibility_v01.py`. The alternative narrow
`hedgehog/drs.py` correction is rejected for this plan; `hedgehog/drs.py` and
`tests/test_drs_runtime.py` remain frozen.

The adapter must use read-only path inspection and file opening. It must not
call `LocalDRS.layer_path`, create a directory or file, mutate a record, update
access metadata, update lifecycle state, write query state, write cache state,
or perform writeback. Canonical retrieval leaves filesystem and persistent
record identities byte-identical.

Root-reviewed writeback is a separate operation and creates a new immutable
record version.

Canonical MeaningRecord and pointer metadata may contain only bounded,
sanitized summaries and references. Raw secrets are forbidden regardless of
key name, including credentials, passwords, API tokens, private keys, passport
numbers, payment-card numbers, CVV, raw bank account identifiers, and raw
authentication material.

Allowed secret-adjacent metadata is limited to sealed secret references,
sensitivity class, scope, access-policy reference, existence or status
metadata, and audit reference. Builders scan every supplied string value, not
field names, under a versioned deterministic rejection profile and restrict
summary digit runs and private-key or credential markers. This is a bounded
reference-kernel guard and is not claimed as production secret detection.

## 29. Immutable Writeback and Supersession

Retrieval never mutates records. A separate Root-reviewed writeback operation
may create a new immutable `MeaningRecordV01` version.

Supersession requires all of:

1. same `SemanticAddressV01` family;
2. same claim dimension;
3. valid provenance chain;
4. explicit replacement reason;
5. correct local Root acceptance;
6. allowed authority class;
7. compatible validity intervals;
8. predecessor record ID;
9. canonical supersession evidence identity;
10. old record preserved byte-identically.

Newer KT alone is insufficient. Freshness alone cannot supersede accepted
Work. `SemanticDraft`, `ConnectorObservation`, external pointer, or
`EvidenceCandidate` cannot supersede accepted Work. Connector observations
require Root acceptance. Accepted Work replacement requires the exact
`ROOT_ACCEPTED_WORK` authority class. GT is advisory only.

The writeback operation validates the proposed new record and existing
predecessor before persistence, writes once, and then reads back and validates
the exact identity. A failed write cannot mutate or partially replace the
predecessor.

## 30. Schema Plan

The following legacy schemas are frozen and are not rewritten as G2-B
canonical schemas:

```text
schemas/drs_record.schema.json
schemas/time_envelope.schema.json
schemas/temporal_query.schema.json
```

G2-B1 creates:

```text
schemas/drs_semantic_address_v01.schema.json
schemas/drs_meaning_record_v01.schema.json
schemas/drs_memory_resolution_v01.schema.json
schemas/reuse_certificate_v01.schema.json
```

Each schema uses exact version constants, `additionalProperties: false`,
required fields equal to the corresponding complete field tuple, exact
integer bounds, exact enums, exact ID patterns, exact tuple geometry, and no
cross-version union. Nested canonical objects must validate against their
exact v0.1 definitions. Unknown fields and mixed versions fail closed.

Legacy compatibility occurs through `LegacyDRSProjectionV01`, never through
schema rewriting or cross-version object mixing.

## 31. Synthetic Two-Domain Proof

The proof uses exactly two synthetic local domains and one generic law.

Domain 1:

```text
domain: TRAVEL_POLICY_INFORMATION
positive question: retrieve a current bounded travel-policy summary
negative requests:
  buy ticket
  reserve seat
  use payment reference
  issue ticket
```

Domain 2:

```text
domain: WAREHOUSE_MAINTENANCE_INFORMATION
positive question: retrieve a current bounded maintenance-interval summary
negative requests:
  release shipment
  order replacement part
  authorize supplier payment
  execute maintenance action
```

Both domains use one canonical address family, meaning-record family,
temporal-query family, eligibility law, ranking law, descent law, Root shortcut
law, and ReuseCertificate family. There is no domain-specific authority code,
closed programme rerun, real connector, external DRS, provider, network,
Gemini, or effect.

Each positive proof includes pointer-first summary retrieval, one bounded
Root-approved descent, one valid `ANSWER_SHORTCUT`, and one `CONTEXT_ONLY`
fallback. Every negative request is blocked from informational shortcut before
certificate creation.

## 32. Implementation Slice Plan

One coherent implementation sequence is frozen. A demonstrated defect may
receive a bounded correction, but a test failure does not subdivide a slice.

### G2-B1 - Canonical contracts, identities, schemas, and projections

- Authorized paths: create
  `hedgehog/drs_semantic_address_v01.py`,
  `hedgehog/drs_memory_resolution_v01.py`,
  `hedgehog/reuse_certificate_v01.py`,
  `hedgehog/drs_g2b_compatibility_v01.py`, the four v0.1 schemas, and
  `tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py`.
- Frozen paths: every path not listed for this slice, including all G2-A
  paths, `hedgehog/drs.py`, `hedgehog/mode_router.py`, and legacy schemas.
- Public symbols: immutable types, exact constants, builders, validators, and
  plain-data serializers listed in Section 34.
- Tests: exact identity, exact type, schema, projection, secret-boundary, and
  mixed-version nodes from Section 35.
- Runner use: none.
- Compatibility selection: legacy DRS schema/time tests plus exact new nodes;
  no closed programme runner.
- Commit boundary: one owner commit after independent review.
- Stop condition: all canonical objects and projections rebuild exactly; no
  runtime retrieval or shortcut is enabled.

### G2-B2 - Temporal query, query-state evaluation, hard eligibility, ranking

- Authorized paths: modify
  `hedgehog/drs_memory_resolution_v01.py` and the single G2-B focused test.
- Frozen paths: all other paths.
- Public symbols: query evaluator, eligibility builder, ranking function, and
  resolution-report builder/validator listed in Section 34.
- Tests: time boundaries, query modes, gate ordering, ineligible-high-score,
  deterministic tie-break, and advisory non-authority nodes.
- Runner use: none.
- Compatibility selection: exact time, legacy DRS, reuse-gate, and focused
  G2-B nodes.
- Commit boundary: one owner commit after independent review.
- Stop condition: eligible-only deterministic ranking passes with no shortcut
  or payload opening.

### G2-B3 - RetrievalPlan and Root-approved controlled memory descent

- Authorized paths: modify
  `hedgehog/drs_memory_resolution_v01.py` and the single G2-B focused test.
- Frozen paths: all other paths, including Root Kernel sources.
- Public symbols: retrieval-plan, budget, request, and result builders,
  validators, serializers, and pure local descent executor.
- Tests: approval, budget, pointer access, accounting, read-purity, and bounded
  traversal nodes.
- Runner use: none.
- Compatibility selection: focused Root Kernel, local DRS resolver, and G2-B
  nodes without provider or connector execution.
- Commit boundary: one owner commit after independent review.
- Stop condition: every descent is local, Root-approved, bounded, read-only,
  and zero-effect.

### G2-B4 - Root projection, certificate, informational shortcut, legacy fence

- Authorized paths: modify `hedgehog/reuse_certificate_v01.py`,
  `hedgehog/root_orchestrator.py`,
  `tests/test_root_orchestrator_runtime.py`, and the single G2-B focused test.
- Frozen paths: `hedgehog/mode_router.py`, `hedgehog/reuse_gate.py`, Root
  Kernel sources, all G2-A paths, and every other path.
- Public symbols: Root projection and certificate builders, validators,
  serializers, and the narrow orchestrator certificate input.
- Tests: Root cross-binding, certificate coherence/expiry, caller-boolean
  fence, action negatives, and Root-created informational output.
- Runner use: none.
- Compatibility selection: Root orchestrator, Root Kernel, reuse-gate, mode
  router read-only compatibility, and exact G2-B nodes.
- Commit boundary: one owner commit after independent review.
- Stop condition: only a valid projection plus certificate permits the narrow
  informational shortcut; action shortcut remains disabled.

### G2-B5 - Pure local adapter, immutable writeback, two domains

- Authorized paths: modify `hedgehog/local_drs_resolver.py` and
  `tests/test_real_local_drs_resolver_writeback_v01_runner.py`; create and
  modify `demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py`; modify
  the single G2-B focused test.
- Frozen paths: `hedgehog/drs.py`, `tests/test_drs_runtime.py`, all closed
  domain programmes, and every unlisted path.
- Public symbols: G2-B collector and total report validator; no new authority
  family.
- Tests: read purity, immutable writeback, supersession, two-domain
  invariance, report forgery, and deterministic replay.
- Runner use: run the new deterministic G2-B runner exactly once after focused
  tests pass.
- Compatibility selection: local resolver/writeback, G2-A history boundary,
  Root orchestrator, and focused G2-B nodes.
- Commit boundary: one owner commit after independent review.
- Stop condition: both synthetic domains pass with zero operations and closed
  programmes unexecuted.

### G2-B6 - Living Gauntlet and Kernel Conformance integration

- Authorized paths: modify the five Gauntlet/Conformance source and test paths
  listed in Section 33.
- Frozen paths: every G2-B1 through G2-B5 runtime path, all G2-A paths, release
  indexes, and all unlisted paths.
- Public symbols: version constants and exact versioned geometry extensions
  only; no new report family.
- Tests: exact new act, category, ten probes, historical geometry, failure,
  determinism, and zero-effect nodes.
- Runner use: one G2-B runner, one Conformance runner, and one Living Gauntlet
  runner after focused selectors pass.
- Compatibility selection: bounded DRS, Root, G2-A history, Gauntlet, and
  Conformance tests.
- Commit boundary: one owner commit after independent review.
- Stop condition: versioned extension passes without rewriting Gate-1 or G2-A
  historical geometry.

### G2-B7 - Independent audit, checkpoint, and AGENTS update

- Authorized paths: create the audit and checkpoint paths in Section 33 and
  modify only the AGENTS active-checkpoint block.
- Frozen paths: every runtime, test, demo, schema, release, README,
  specification, and closed evidence path.
- Public symbols: none.
- Tests: focused G2-B file, exact G2-B6 selector, bounded compatibility, and
  deterministic runners exactly once under an auditor non-repair law.
- Runner use: exact G2-B, Conformance, and Living Gauntlet runners once.
- Compatibility selection: one bounded selection; repository-wide suite
  remains an explicit owner decision.
- Commit boundary: one owner closure commit after architect review.
- Stop condition: independent audit and every Definition-of-Done item pass;
  otherwise create no closure files.

## 33. Authorized and Frozen Path Scope

Candidate CREATE paths:

```text
hedgehog/drs_semantic_address_v01.py
hedgehog/drs_memory_resolution_v01.py
hedgehog/reuse_certificate_v01.py
hedgehog/drs_g2b_compatibility_v01.py
schemas/drs_semantic_address_v01.schema.json
schemas/drs_meaning_record_v01.schema.json
schemas/drs_memory_resolution_v01.schema.json
schemas/reuse_certificate_v01.schema.json
tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py
demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py
```

Candidate MODIFY paths, only in the relevant slices:

```text
hedgehog/local_drs_resolver.py
tests/test_real_local_drs_resolver_writeback_v01_runner.py
hedgehog/root_orchestrator.py
tests/test_root_orchestrator_runtime.py
demo/run_living_gauntlet_v01.py
tests/test_living_gauntlet_v01_runner.py
hedgehog/kernel/conformance_v01.py
demo/run_kernel_conformance_v01.py
tests/test_kernel_conformance_v01_runner.py
AGENTS.md
```

`hedgehog/drs.py` and `tests/test_drs_runtime.py` are not candidate modify
paths because the selected read-purity route is the new
`hedgehog/drs_g2b_compatibility_v01.py` adapter.

Candidate closure CREATE paths:

```text
docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log
docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md
```

Frozen future paths and surfaces:

- all G2-A implementation, tests, runners, audit, and checkpoint files;
- Root Decision Kernel;
- Transition Registry;
- Kernel ABI unless a separately proven ABI extension is indispensable;
- Effect Firewall;
- Corridor;
- ActionPacket Registry;
- ActionPacket Replay;
- MultiRoot;
- `hedgehog/drs.py`;
- `tests/test_drs_runtime.py`;
- `hedgehog/mode_router.py`;
- `hedgehog/reuse_gate.py` as legacy compatibility logic;
- `hedgehog/external_drs/**`;
- vector store;
- embeddings;
- providers;
- connectors;
- production persistence;
- closed Airline programme;
- closed Supplier programme;
- release indexes;
- public Showcase;
- Package;
- Anchor;
- RC2 publication work;
- G2-C through G2-F implementation.

No public release or RC2 claim is authorized.

## 34. Public Symbol Plan

The following public types are authorized:

```text
SemanticAddressV01
MemoryPointerV01
ArtifactPointerV01
LineageEdgeV01
DRSAuthorityEnvelopeV01
DRSTimeEnvelopeV01
MeaningRecordV01
DRSTemporalQueryV01
QueryEvaluationStateV01
ResolutionCandidateV01
RetrievalPlanV01
MemoryDescentBudgetV01
MemoryDescentRequestV01
MemoryDescentResultV01
RootShortcutAuthorizationProjectionV01
ReuseCertificateV01
DRSResolutionReportV01
LegacyDRSProjectionV01
G2AActionHistoryBindingV01
```

Exact type function names:

| Type | Builder | Validator | Plain-data serializer |
| --- | --- | --- | --- |
| `SemanticAddressV01` | `build_semantic_address_v01` | `validate_semantic_address_v01` | `semantic_address_to_plain_data_v01` |
| `MemoryPointerV01` | `build_memory_pointer_v01` | `validate_memory_pointer_v01` | `memory_pointer_to_plain_data_v01` |
| `ArtifactPointerV01` | `build_artifact_pointer_v01` | `validate_artifact_pointer_v01` | `artifact_pointer_to_plain_data_v01` |
| `LineageEdgeV01` | `build_lineage_edge_v01` | `validate_lineage_edge_v01` | `lineage_edge_to_plain_data_v01` |
| `DRSAuthorityEnvelopeV01` | `build_drs_authority_envelope_v01` | `validate_drs_authority_envelope_v01` | `drs_authority_envelope_to_plain_data_v01` |
| `DRSTimeEnvelopeV01` | `build_drs_time_envelope_v01` | `validate_drs_time_envelope_v01` | `drs_time_envelope_to_plain_data_v01` |
| `MeaningRecordV01` | `build_meaning_record_v01` | `validate_meaning_record_v01` | `meaning_record_to_plain_data_v01` |
| `DRSTemporalQueryV01` | `build_drs_temporal_query_v01` | `validate_drs_temporal_query_v01` | `drs_temporal_query_to_plain_data_v01` |
| `QueryEvaluationStateV01` | `build_query_evaluation_state_v01` | `validate_query_evaluation_state_v01` | `query_evaluation_state_to_plain_data_v01` |
| `ResolutionCandidateV01` | `build_resolution_candidate_v01` | `validate_resolution_candidate_v01` | `resolution_candidate_to_plain_data_v01` |
| `RetrievalPlanV01` | `build_retrieval_plan_v01` | `validate_retrieval_plan_v01` | `retrieval_plan_to_plain_data_v01` |
| `MemoryDescentBudgetV01` | `build_memory_descent_budget_v01` | `validate_memory_descent_budget_v01` | `memory_descent_budget_to_plain_data_v01` |
| `MemoryDescentRequestV01` | `build_memory_descent_request_v01` | `validate_memory_descent_request_v01` | `memory_descent_request_to_plain_data_v01` |
| `MemoryDescentResultV01` | `build_memory_descent_result_v01` | `validate_memory_descent_result_v01` | `memory_descent_result_to_plain_data_v01` |
| `RootShortcutAuthorizationProjectionV01` | `build_root_shortcut_authorization_projection_v01` | `validate_root_shortcut_authorization_projection_v01` | `root_shortcut_authorization_projection_to_plain_data_v01` |
| `ReuseCertificateV01` | `build_reuse_certificate_v01` | `validate_reuse_certificate_v01` | `reuse_certificate_to_plain_data_v01` |
| `DRSResolutionReportV01` | `build_drs_resolution_report_v01` | `validate_drs_resolution_report_v01` | `drs_resolution_report_to_plain_data_v01` |
| `LegacyDRSProjectionV01` | `build_legacy_drs_projection_v01` | `validate_legacy_drs_projection_v01` | `legacy_drs_projection_to_plain_data_v01` |
| `G2AActionHistoryBindingV01` | `build_g2a_action_history_binding_v01` | `validate_g2a_action_history_binding_v01` | `g2a_action_history_binding_to_plain_data_v01` |

Additional public functions:

```text
project_legacy_drs_source_v01
evaluate_drs_candidate_v01
rank_eligible_drs_candidates_v01
execute_local_memory_descent_v01
validate_existing_root_shortcut_decision_v01
collect_drs_semantic_address_reuse_certificate_g2_b_v01
validate_drs_semantic_address_reuse_certificate_g2_b_report_v01
collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01
```

G2-B4 appends exactly these optional parameters to
`RootOrchestrator.process_event`, after all existing parameters:

```text
g2b_resolution_report: DRSResolutionReportV01 | None = None
g2b_use_time: int | None = None
```

The first contains the exact nested certificate and Root projection. The
second is the explicit signed-int64 use time. Existing callers retain current
behavior. `allow_direct_reuse=True` without both a valid report and explicit
use time cannot select the shortcut.

Authorized public constants:

```text
DRS_G2B_PROFILE_VERSION_V01
SEMANTIC_ADDRESS_PROFILE_VERSION_V01
DRS_QUERY_MODES_V01
DRS_QUERY_STATES_V01
DRS_REUSE_CLASSES_V01
DRS_ENABLED_REUSE_CLASSES_V01
DRS_MEMORY_DESCENT_CLASSES_V01
DRS_MEMORY_POINTER_STORAGE_CLASSES_V01
DRS_ARTIFACT_POINTER_STORAGE_CLASSES_V01
DRS_PERSISTENT_LIFECYCLE_STATES_V01
DRS_REFERENCE_MEMORY_DESCENT_CEILINGS_V01
DRS_RANKING_WEIGHTS_V01
```

Authorized changed public constants in G2-B6:

```text
demo.run_living_gauntlet_v01.RUNNER_VERSION:
  v1.1 -> v1.2

hedgehog.kernel.conformance_v01.CONFORMANCE_VERSION:
  v0.2 -> v0.3

hedgehog.kernel.conformance_v01.CATEGORY_IDS:
  append DRSSemanticAddressReuseCertificateConformance

hedgehog.kernel.conformance_v01.NEGATIVE_PROBE_IDS:
  append the exact ten G2-B probe IDs in Section 37
```

No new public Root, FinalOutput, packet, Registry, receipt, capability,
effect-handle, mode-router, provider, connector, or external-DRS symbol is
authorized.

## 35. Exact Test Matrix

All nodes belong to
`tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py` unless another
path is named. A negative node must receive exactly the stable reason shown;
extra, reordered, exception-derived, or unsanitized reasons fail the test.

| # | Exact test node | Required proof | Exact expected result or reason |
| ---: | --- | --- | --- |
| 1 | `test_g2b_canonical_address_identity_rebuild_is_exact` | Canonical address identity rebuild | `PASS` |
| 2 | `test_g2b_dynamic_context_is_excluded_from_address_identity` | Dynamic context cannot alter or enter address material | `drs_address_dynamic_material_forbidden` |
| 3 | `test_g2b_meaning_record_identity_and_nested_exactness` | Record identity exactness | `drs_meaning_record_identity_invalid` |
| 4 | `test_g2b_pointer_identity_rebuild_is_exact` | Both pointer identities exact | `drs_pointer_identity_invalid` |
| 5 | `test_g2b_pointer_access_policy_is_enforced` | Summary/payload/use policy cannot be bypassed | `drs_pointer_access_policy_denied` |
| 6 | `test_g2b_raw_secret_payload_is_rejected_independent_of_key_name` | Raw secret value rejected in every metadata position | `drs_secret_payload_forbidden` |
| 7 | `test_g2b_time_fields_require_exact_signed_int64` | Bool, float, Decimal, string, subclass rejected | `drs_time_type_invalid` |
| 8 | `test_g2b_half_open_validity_boundary_rejects_exact_valid_to` | `as_of == valid_to` invalid | `drs_time_validity_interval_invalid` |
| 9 | `test_g2b_half_open_ttl_boundary_rejects_exact_expiry` | Exact TTL expiry is stale | `drs_time_ttl_expired` |
| 10 | `test_g2b_missing_required_time_axis_fails_closed` | Required PT/KT/ET/CT axis cannot be absent | `drs_time_axis_missing` |
| 11 | `test_g2b_query_mode_controls_temporal_validity_and_shortcut_eligibility` | Only two modes may consider answer shortcut | `drs_query_mode_invalid_for_shortcut` |
| 12 | `test_g2b_persistent_lifecycle_is_distinct_from_query_state` | Query evaluation is never persisted | `drs_query_state_persistence_forbidden` |
| 13 | `test_g2b_retrieval_is_filesystem_and_record_read_pure` | Read creates or mutates nothing | `drs_retrieval_read_mutation_detected` |
| 14 | `test_g2b_legacy_projection_reports_every_preserved_synthesized_and_missing_field` | Projection completeness | `drs_legacy_projection_incomplete` |
| 15 | `test_g2b_missing_legacy_safety_evidence_cannot_become_shortcut` | Missing evidence cannot be synthesized | `drs_legacy_projection_shortcut_forbidden` |
| 16 | `test_g2b_hard_eligibility_precedes_ranking` | Gate sequence exact | `drs_eligibility_order_invalid` |
| 17 | `test_g2b_ineligible_highest_score_candidate_cannot_win` | High score cannot bypass a hard gate | `drs_ineligible_candidate_selected` |
| 18 | `test_g2b_ranking_tie_break_ends_with_canonical_candidate_id` | Tie-break deterministic | `drs_ranking_tie_break_invalid` |
| 19 | `test_g2b_gt_advisory_score_creates_no_authority` | GT not authority | `drs_gt_authority_forbidden` |
| 20 | `test_g2b_semantic_similarity_creates_no_authority` | Similarity not authority | `drs_similarity_authority_forbidden` |
| 21 | `test_g2b_freshness_creates_no_authority` | Freshness not authority | `drs_freshness_authority_forbidden` |
| 22 | `test_g2b_root_decision_exact_cross_binding_is_required` | Existing Root triple exact | `drs_root_decision_binding_invalid` |
| 23 | `test_g2b_wrong_local_root_is_rejected` | Only correct local Root | `drs_root_owner_mismatch` |
| 24 | `test_g2b_forged_root_shortcut_projection_is_rejected` | Projection cannot self-assert approval | `drs_root_projection_invalid` |
| 25 | `test_g2b_reuse_certificate_identity_rebuild_is_exact` | Certificate identity exact | `reuse_certificate_identity_invalid` |
| 26 | `test_g2b_reuse_certificate_cross_profile_coherence_is_exact` | Every consequential cross-binding exact | `reuse_certificate_cross_profile_mismatch` |
| 27 | `test_g2b_reuse_certificate_expires_at_exact_valid_to` | Half-open certificate validity | `reuse_certificate_expired` |
| 28 | `test_g2b_forbidden_change_blocks_reuse` | Dependency change detected | `drs_forbidden_change_detected` |
| 29 | `test_g2b_missing_required_evidence_blocks_reuse` | Required evidence exact | `drs_required_evidence_missing` |
| 30 | `test_g2b_policy_version_mismatch_blocks_reuse` | Policy exact | `drs_policy_version_mismatch` |
| 31 | `test_g2b_schema_version_mismatch_blocks_reuse` | Schema exact | `drs_schema_version_mismatch` |
| 32 | `test_g2b_conflict_blocks_reuse` | Conflict hard gate | `drs_conflict_blocked` |
| 33 | `test_g2b_quarantined_record_blocks_reuse` | Quarantine hard gate | `drs_quarantine_blocked` |
| 34 | `test_g2b_deadend_record_blocks_reuse` | Deadend hard gate | `drs_deadend_blocked` |
| 35 | `test_g2b_memory_descent_without_root_approval_is_rejected` | Descent requires exact Root approval | `drs_memory_descent_root_approval_missing` |
| 36 | `test_g2b_root_cannot_expand_reference_descent_budget` | Budget expansion rejected | `drs_memory_descent_budget_expansion` |
| 37 | `test_g2b_pointer_open_accounting_is_exact` | IDs, counts, depth, edges, bytes cohere | `drs_memory_descent_accounting_invalid` |
| 38 | `test_g2b_action_like_request_cannot_take_answer_shortcut` | Generic action intent blocked | `drs_action_intent_shortcut_forbidden` |
| 39 | `test_g2b_payment_request_cannot_take_answer_shortcut` | Payment blocked | `drs_payment_shortcut_forbidden` |
| 40 | `test_g2b_shipment_release_cannot_take_answer_shortcut` | Shipment release blocked | `drs_shipment_shortcut_forbidden` |
| 41 | `test_g2b_ticket_issue_cannot_take_answer_shortcut` | Ticket issue blocked | `drs_ticket_shortcut_forbidden` |
| 42 | `test_g2b_action_commit_packet_creation_cannot_take_answer_shortcut` | Packet creation blocked | `drs_action_packet_shortcut_forbidden` |
| 43 | `test_g2b_receipt_creation_cannot_take_answer_shortcut` | Receipt creation blocked | `drs_receipt_creation_shortcut_forbidden` |
| 44 | `test_g2b_prior_root_final_cannot_authorize_shortcut` | Old Root Final is historical | `drs_prior_root_final_shortcut_forbidden` |
| 45 | `test_g2b_prior_receipt_cannot_authorize_shortcut` | Receipt is evidence only | `drs_prior_receipt_shortcut_forbidden` |
| 46 | `test_g2b_expired_action_packet_cannot_authorize_shortcut` | Expired packet blocked | `drs_action_history_expired` |
| 47 | `test_g2b_revoked_action_packet_cannot_authorize_shortcut` | Revoked packet blocked | `drs_action_history_revoked` |
| 48 | `test_g2b_superseded_action_packet_cannot_authorize_shortcut` | Superseded packet blocked | `drs_action_history_superseded` |
| 49 | `test_g2b_blocked_action_packet_cannot_authorize_shortcut` | Blocked packet blocked | `drs_action_history_blocked` |
| 50 | `test_g2b_consumed_action_history_cannot_authorize_shortcut` | Consumed action history blocked | `drs_action_history_consumed` |
| 51 | `test_g2b_uncertain_closed_history_cannot_authorize_shortcut` | Uncertain-closed history blocked | `drs_action_history_uncertain_closed` |
| 52 | `test_g2b_caller_boolean_cannot_authorize_shortcut` | `allow_direct_reuse` is consideration only | `drs_caller_boolean_authority_forbidden` |
| 53 | `test_g2b_valid_informational_shortcut_skips_only_allowed_heavy_actors` | Architect/Executor skip only after full evidence | `PASS` |
| 54 | `test_g2b_root_remains_final_authority` | No alternate final authority | `drs_root_authority_violation` |
| 55 | `test_g2b_drs_cannot_create_final_output` | DRS non-authority | `drs_final_output_creation_forbidden` |
| 56 | `test_g2b_certificate_cannot_create_final_output` | Certificate non-authority | `reuse_certificate_final_output_forbidden` |
| 57 | `test_g2b_two_domain_generic_contract_invariance` | Same laws in both domains | `PASS` |
| 58 | `test_g2b_report_replay_is_byte_deterministic` | Deterministic Replay of G2-B report | `PASS` |
| 59 | `test_g2b_provider_network_gemini_and_effect_counters_are_zero` | Operation counters exact | `PASS` |
| 60 | `test_g2b_validators_reject_custom_equality_substitutes` | Nested exact-type resistance | `drs_exact_type_required` |
| 61 | `test_g2b_validators_reject_str_subclasses` | Exact `str` law | `drs_exact_type_required` |
| 62 | `test_g2b_validators_reject_bool_as_int` | Exact `int` law | `drs_exact_int_required` |
| 63 | `test_g2b_pickle_reconstruction_cannot_bypass_validation` | Adversarial reconstruction revalidated | `drs_serialized_reconstruction_invalid` |
| 64 | `test_g2b_schema_and_version_mixing_fails_closed` | No mixed profile | `drs_schema_version_mismatch` |
| 65 | `test_g2b_disabled_reuse_class_does_not_silently_downgrade` | Disabled class fails closed | `drs_reuse_class_disabled` |
| 66 | `test_g2b_summary_only_opens_no_payload` | Summary-only law exact | `drs_summary_only_payload_forbidden` |
| 67 | `test_g2b_open_one_artifact_obeys_depth_and_count_one` | Single-artifact law exact | `drs_open_one_artifact_limit_exceeded` |
| 68 | `test_g2b_root_reviewed_writeback_creates_new_immutable_version` | Old record byte-identical | `PASS` |
| 69 | `test_g2b_supersession_requires_root_provenance_reason_and_predecessor` | Freshness/newer alone insufficient | `drs_supersession_evidence_invalid` |

`tests/test_root_orchestrator_runtime.py` must add the exact integration node
`test_g2b_root_orchestrator_requires_certificate_and_root_projection_for_direct_reuse`
with failure reason `drs_root_shortcut_evidence_missing`.

`tests/test_real_local_drs_resolver_writeback_v01_runner.py` must add
`test_g2b_pure_adapter_and_immutable_writeback_are_separate_operations` with
failure reason `drs_read_write_boundary_violation`.

Gauntlet and Conformance nodes are frozen in Section 37. No skip, xfail,
force-pass, warning suppression, schema relaxation, or stale outer hash as the
only rejection mechanism is permitted.

## 36. Performance and Complexity Law

The implementation must not add a module-global mutable cache, cross-run
cache, ambient clock, random source, UUID, sleep, unbounded graph traversal,
unbounded pointer opening, ranking before eligibility, repeated legacy
projection per gate, repeated Root validation per field, one report
recollection per negative mutation, or arbitrary wall-clock timeout.

Within one query:

```text
project each source record once
evaluate each candidate once
rank eligible candidates once
validate Root decision once
build certificate once
```

Let:

```text
N = source records
P = proposed pointers
E = reachable lineage edges within approval
K = eligible candidates
B = approved bytes
```

Expected bounds:

| Operation | Complexity and hard bound |
| --- | --- |
| Source projection | `O(N)` time and `O(N)` canonical objects |
| Hard-gate evaluation | `O(N)` evaluations |
| Eligible ranking | `O(K log K)` time, `K <= N` |
| Pointer opening | `O(min(P, 16))` pointer operations |
| Artifact opening | At most 4 |
| Record opening | At most 32 |
| Lineage traversal | `O(min(E, 32))` |
| Conflict opening | At most 16 |
| Byte opening | `B <= 1048576` |
| Graph depth | At most 3 |
| Root validation | Exactly once per approved descent and once per shortcut |
| Certificate build | At most once per query |

Canonical validators may be linear in the size of their bounded nested tuples.
No optimization may weaken exact validation, cross-binding, eligibility, or
operation accounting.

## 37. Living Gauntlet and Kernel Conformance Plan

Living Gauntlet gains one act:

```text
act_id:
  drs_semantic_address_and_reuse_certificate

source_module:
  demo.run_living_gauntlet_v01

source_symbol:
  collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01
```

The frozen Gate-1 geometry remains `v1.0` with 13 active acts. The historical
G2-A geometry remains `v1.1` with 14 active acts. The versioned G2-B extension
is `v1.2` with 15 active acts. The old fourteen retain their exact order and
source bindings; the G2-B act is appended as row fifteen. Frozen release
indexes continue to describe v1.0 and are not rewritten.

The act calls the G2-B collector once and independently validates its report.
It proves two synthetic domains, pointer-first memory, exact time query,
eligibility before ranking, bounded Root-approved descent, one informational
`ANSWER_SHORTCUT`, context-only fallback, the action-like negative matrix,
the G2-A history fence, and zero provider/network/Gemini/effects.

Kernel Conformance gains one category:

```text
DRSSemanticAddressReuseCertificateConformance
```

Exact category checks:

```text
canonical_identity
time
pointer_policy
eligibility
ranking
descent
root_shortcut
certificate_non_authority
action_boundary
cross_domain_invariance
```

The frozen Gate-1 v0.1 geometry remains 10 categories, 2 historical domain
results, 10 negative probes, and 12 active Gauntlet refs. The historical G2-A
v0.2 geometry remains 11 categories, the same 2 historical domain results, 20
negative probes, and 13 active Gauntlet refs. The versioned G2-B extension is
v0.3 with 12 categories, the same 2 historical domain results, 30 negative
probes, and 14 active Gauntlet refs. The two synthetic G2-B domains are
validated inside category twelve and do not rewrite historical domain rows.

Exact appended negative probe IDs:

```text
drs_address_identity_forgery
drs_time_query_forgery
drs_pointer_policy_forgery
drs_eligibility_order_forgery
drs_ranking_ineligible_selection_forgery
drs_memory_descent_budget_forgery
drs_root_shortcut_authority_forgery
reuse_certificate_cross_binding_forgery
drs_action_reuse_forgery
drs_cross_domain_substitution
```

Every probe preserves the correct outer dataclass family and must produce the
exact public G2-B validator result:

```text
target:
  demo.run_drs_semantic_address_reuse_certificate_g2_b_v01
  .validate_drs_semantic_address_reuse_certificate_g2_b_report_v01

(False, ("g2b_report_fail_closed",))
```

One valid baseline report is collected for all ten mutations. The category
PASS is derived from the real act, exact ten probes, validated two-domain
geometry, and zero operation counters. Caller-supplied PASS labels are not
proof.

Exact new test nodes:

```text
tests/test_living_gauntlet_v01_runner.py::
  test_g2b6_drs_semantic_address_reuse_certificate_act_is_real_bounded_and_zero_effect

tests/test_living_gauntlet_v01_runner.py::
  test_g2b6_living_gauntlet_v12_preserves_v11_and_appends_g2b_act

tests/test_living_gauntlet_v01_runner.py::
  test_g2b6_living_gauntlet_g2b_failure_is_fail_closed_and_unknown_effect

tests/test_kernel_conformance_v01_runner.py::
  test_g2b6_conformance_v03_preserves_v02_geometry

tests/test_kernel_conformance_v01_runner.py::
  test_g2b6_drs_semantic_address_reuse_certificate_category_is_exact

tests/test_kernel_conformance_v01_runner.py::
  test_g2b6_drs_negative_probe_matrix_is_exact

tests/test_kernel_conformance_v01_runner.py::
  test_g2b6_conformance_and_gauntlet_are_deterministic_and_zero_effect
```

Gate-1 and G2-A historical geometries are validated under private frozen
version constants. Unknown or cross-mixed versions fail closed.

## 38. Independent Audit and Internal Closure Plan

G2-B7 begins only from a clean committed G2-B6 basis. The independent auditor
must remain read-only until every gate passes:

1. exact ordered commit ancestry;
2. exact path scope for G2-B1 through G2-B6;
3. static architecture and public-symbol audit;
4. complete Definition-of-Done matrix;
5. exact focused G2-B tests;
6. bounded compatibility covering DRS, time, Root, G2-A history,
   orchestrator, Gauntlet, and Conformance;
7. G2-B deterministic runner;
8. Kernel Conformance runner;
9. Living Gauntlet runner;
10. provider/network/Gemini/external-DRS/connector/effect counters all zero;
11. no G2-A reopening, G2-C implementation, release claim, or RC2 claim.

An audit failure creates no audit, checkpoint, or AGENTS change and repairs no
implementation or test.

After and only after audit PASS, create:

```text
docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log
docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md
```

Then modify only the AGENTS active-checkpoint block. Release indexes, README,
runtime, tests, schemas, demos, specifications, and G2-A files remain frozen.
The closure must state G2-B `CLOSED_PASS`, Gate 2 `NOT_CLOSED`, public release
not claimed, RC2 not claimed, and the next slice subject to a separate
architect ruling.

## 39. Definition of Done

Definition-of-Done condition count: **120**.

1. The implementation basis follows a committed, independently reviewed G2-B
   preflight.
2. G2-A remains `CLOSED_PASS` and byte-identical.
3. G2-C implementation has not started.
4. Exactly one canonical versioned G2-B family exists.
5. Legacy DRS objects remain compatibility inputs only.
6. No legacy object becomes canonical through duck typing.
7. Every compatibility source passes exact source-family validation.
8. Every compatibility source passes source identity and source-hash
   validation.
9. Every projection records preserved, synthesized, unavailable, and
   restricted fields.
10. Missing legacy safety evidence never becomes `ANSWER_SHORTCUT`.
11. Every canonical dataclass is frozen and immutable.
12. Every field tuple equals the order frozen in this document.
13. Every validator is total over arbitrary objects.
14. Every builder exposes only a sanitized stable failure reason.
15. Every serializer produces deterministic exact plain data.
16. Exact built-in types are required at every nested level.
17. `bool` is rejected wherever `int` is required.
18. `str` subclasses and custom-equality substitutes are rejected.
19. Binary floats and `Decimal` are absent from canonical identity and ranking.
20. Every canonical identity rebuild uses the exact domain-separated profile.
21. `SemanticAddressV01` identity uses exactly the seven frozen fields.
22. Dynamic user, query, time, Root, score, lifecycle, pointer, and certificate
    context is excluded from address identity.
23. Namespace is bounded and cannot carry unbounded raw user identity.
24. Canonical address ID uses prefix `drsaddr_v01:`.
25. `DRSTimeEnvelopeV01` uses exact signed-int64 UTC epoch seconds.
26. Legacy ISO time enters only through strict compatibility projection.
27. Evaluation time and evaluation-time source are always explicit.
28. Validity obeys `valid_from <= as_of < valid_to`.
29. TTL obeys `as_of < pt_created_at + ttl_seconds`.
30. Exact `valid_to` and exact TTL expiry fail their respective gates.
31. TTL expiry remains distinct from claim invalidity.
32. Validity, freshness, authority, and score remain distinct.
33. All six canonical query modes are exact and ordered.
34. Only `CURRENT_DECISION` and `DIRECT_REUSE_CANDIDATE` may consider
    `ANSWER_SHORTCUT`.
35. Historical, audit, trend, context, and warning modes cannot issue an
    answer shortcut.
36. `QueryEvaluationStateV01` is pure and immutable.
37. Query state is never persisted as record lifecycle.
38. Time fitness is independently recomputed for every query.
39. Transported freshness flags or classes cannot authorize eligibility.
40. Missing required time axes fail closed.
41. `MeaningRecordV01` contains no dense payload.
42. Bounded safe summary and metadata pass the secret-boundary profile.
43. Persistent lifecycle vocabulary is exactly the six frozen states.
44. Lifecycle change creates a new immutable record version.
45. Old record bytes remain preserved after writeback or supersession.
46. Every memory pointer uses one exact local storage class.
47. Every artifact pointer uses one exact local storage class.
48. Every pointer binds content hash, access policy, sensitivity, and allowed
    and forbidden uses.
49. Summary and payload permissions are independently enforced.
50. No external/global pointer storage class executes.
51. No pointer grants authority or permission.
52. Raw credentials, tokens, private keys, identity documents, card data, bank
    identifiers, and authentication material are rejected.
53. Only sealed references and bounded status metadata may represent secrets.
54. Secret scanning is not described as production secret detection.
55. Retrieval creates no directory or file.
56. Retrieval mutates no record, metadata, lifecycle, query state, or cache.
57. The selected pure G2-B adapter does not call `LocalDRS.layer_path`.
58. `hedgehog/drs.py` remains frozen.
59. Writeback is a separate Root-reviewed operation.
60. Writeback validates and persists one new immutable record version.
61. Hard eligibility gates execute in the exact frozen order.
62. Every ineligible candidate remains outside the eligible set.
63. Ranking receives eligible candidates only.
64. An ineligible highest-score candidate cannot become selected.
65. Ineligible candidates may remain only as context, history, warning, rerun,
    or blocked explanation.
66. No ineligible candidate creates Root shortcut evidence.
67. No ineligible candidate receives a ReuseCertificate.
68. Policy and schema compatibility require exact versions.
69. Provenance and authority-envelope evidence is independently validated.
70. Required evidence, forbidden change, conflict, quarantine, and deadend are
    hard gates.
71. Permission boundary and action-intent checks are hard gates.
72. Ranking uses exact signed integer score units.
73. All component ranges and weights equal the frozen v0.1 profile.
74. Total score formula rebuild is exact and signed-int64 safe.
75. Deterministic tie-break ends with canonical candidate ID.
76. GT, similarity, freshness, lineage, and score create no authority.
77. `ResolutionCandidateV01` exists only for an eligible evaluation.
78. Selected candidate is the first exact ranked eligible candidate or none.
79. `DRSResolutionReportV01` independently rebuilds the eligible and ranked
    sets.
80. Unknown effect accounting remains `-1`, never normalized to zero.
81. Every RetrievalPlan is proposal-only and executes no read.
82. Memory descent class is one of the six frozen classes.
83. Memory descent budget has all seven exact bounded counters.
84. No approved budget exceeds any reference-kernel ceiling.
85. Root may narrow but never expand class, IDs, or budget.
86. `SUMMARY_ONLY` opens no payload.
87. `OPEN_ONE_ARTIFACT` opens at most one artifact at depth at most one.
88. No descent executes without exact local-Root approval.
89. Pointer, record, artifact, byte, edge, conflict, and depth accounting
    exactly matches observations.
90. Controlled descent performs only bounded local reads and zero effects.
91. Existing `RootDecisionKernelV01` remains the sole shortcut authority
    kernel.
92. Root input, result, hash, kernel, owner, candidate, query, and scope
    cross-bind exactly.
93. `RootShortcutAuthorizationProjectionV01` carries evidence but creates no
    authority or permission.
94. Only `CONTEXT_ONLY` and `ANSWER_SHORTCUT` are operational in v0.1.
95. Route, sealed-Replay, and protocol-preparation shortcuts remain disabled.
96. Action shortcut remains always disabled.
97. Disabled classes do not silently downgrade.
98. `ReuseCertificateV01` identity includes every consequential field.
99. Certificate address, record, query, evaluation, candidate, Root, policy,
    schema, scope, validity, evidence, dependency, and history bindings match
    exactly.
100. Certificate validity is half-open and rechecked at use time.
101. ReuseCertificate creates no authority, permission, FinalOutput, packet,
     receipt, capability, effect, truth, or action proof.
102. Root alone constructs any informational final output.
103. The caller boolean `allow_direct_reuse` is consideration only.
104. Missing certificate or Root projection prevents direct shortcut.
105. A failed shortcut may continue only through the normal full pipeline.
106. Action-like requests cannot take an informational shortcut.
107. Every G2-A-linked source has exact immutable action-history binding.
108. Expired, revoked, superseded, blocked, failed, consumed, uncertain-closed,
     receipt, prior-permission, and prior-Root-Final history cannot authorize
     reuse.
109. No old ActionPacket or receipt becomes present permission.
110. No ReuseCertificate creates an ActionCommitPacket.
111. Supersession requires same address and claim dimension, provenance,
     reason, Root acceptance, allowed authority, compatible validity,
     predecessor, and evidence identity.
112. Newer KT, freshness, draft, observation, external pointer, candidate, or
     GT alone cannot supersede accepted Work.
113. Both synthetic domains use the same generic contracts and authority law.
114. Both positive informational cases prove bounded shortcut and context
     fallback.
115. All eight domain action-shaped requests fail closed with zero effects.
116. Living Gauntlet v1.2 appends exactly one real G2-B act without rewriting
     historical geometry.
117. Kernel Conformance v0.3 appends exactly one category and ten negative
     probes without rewriting historical geometry.
118. Focused, compatibility, deterministic runner, Gauntlet, and Conformance
     evidence all pass under the planned execution law.
119. Independent audit passes before audit, checkpoint, or AGENTS closure
     writes.
120. Provider, network, Gemini, external DRS, connector, and real-world effect
     counts remain zero, while Gate 2, production, public release, RC2, and
     G2-C remain unclaimed.

Every condition is independently auditable. No condition may be merged,
omitted, renumbered, or passed from prose when executable or structural
evidence exists.

## 40. Operation Accounting

This documentation-only pass records:

```text
tests_run_by_codex=NONE
pytest_calls=0
runner_calls=0
provider_calls=0
network_calls=0
gemini_calls=0
external_drs_calls=0
connector_calls=0
real_world_effects=0
files_created=1
files_modified=0
files_deleted=0
staged_paths=0
commits_created=0
pushes=0
```

No repository module, demo, runner, Package, Anchor, sealed Replay, Living
Gauntlet, Kernel Conformance, provider, network, Gemini, external DRS,
connector, or effect path is executed by this pass.

## 41. Explicit Non-Claims

- G2-A is not reopened.
- Gate 2 is not closed.
- G2-B implementation has not started.
- G2-C implementation has not started.
- ReuseCertificate is not authority.
- ReuseCertificate is not permission.
- ReuseCertificate is not ActionCommitPacket.
- ReuseCertificate is not receipt.
- ReuseCertificate is not capability.
- ReuseCertificate is not effect.
- ReuseCertificate is not an effect handle.
- ReuseCertificate is not a completed action.
- DRS is not truth.
- score is not authority.
- freshness is not authority.
- GT is not authority.
- semantic similarity is not authority.
- external/global DRS is not implemented.
- production DRS is not implemented.
- production persistence is not implemented.
- vector database is not required.
- embeddings are not required.
- real connectors are not implemented.
- public release is not claimed.
- RC2 is not claimed.

This preflight is not production readiness, production-security certification,
permission to implement, permission to commit, a public showcase, or an
Operational Reference Kernel RC2 claim.

## 42. Preflight Disposition

The Architect decisions are complete enough for independent contract review.
Implementation remains unauthorized until this preflight is independently
reviewed, then committed by the owner under a separate explicit authorization.

```text
G2B_PREFLIGHT_DOCUMENT_STATUS:
  READY_FOR_INDEPENDENT_CONTRACT_REVIEW

PLANNING_ONLY:
  true

IMPLEMENTATION_AUTHORIZED:
  false

PREFLIGHT_COMMIT_AUTHORIZED:
  false

G2A_REOPENED:
  false

G2C_STARTED:
  false

PROVIDER_NETWORK_GEMINI_EFFECTS:
  0/0/0/0

NEXT_ACTION:
  ARCHITECT_AND_INDEPENDENT_CONTRACT_REVIEW_BEFORE_OWNER_COMMIT
```
