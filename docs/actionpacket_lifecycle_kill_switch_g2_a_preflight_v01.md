# Hedgehog OS Gate 2 / G2-A
## ActionPacket Lifecycle and Kill-Switch Preflight v0.1

## 1. Metadata

```yaml
document_id: actionpacket_lifecycle_kill_switch_g2_a_preflight_v01
document_status: PREFLIGHT
preflight_status: READY_FOR_OWNER_REVIEW
gate_id: gate2_g2a_actionpacket_lifecycle_kill_switch
observed_base_head: 681625c982e46b9adcd101d7c6bd355f4bea18f3
planning_only: true
runtime_modified: false
tests_modified: false
schemas_modified: false
demos_modified: false
audits_modified: false
checkpoints_modified: false
release_surfaces_modified: false
provider_called: false
network_called: false
gemini_called: false
real_world_effects_count: 0
implementation_authorized: false
public_release_claimed: false
operational_reference_kernel_rc2_claimed: false
next_required_action: owner_review_and_preflight_commit
```

This document is the dedicated implementation preflight for
`gate2_g2a_actionpacket_lifecycle_kill_switch`. It records prospective
contracts only. It creates no runtime authority, packet, transition, receipt,
adapter call, publication, or external effect.

## 2. Gate Purpose

G2-A extends the existing `ActionCommitPacketV02` system. It does not create a
parallel action system.

The purpose is to make an already Root-authorized packet:

- stateful;
- identity-bound;
- temporally bounded;
- idempotent;
- revocable;
- supersedable;
- kill-switch enforceable;
- dependency-aware;
- immutable in historical evidence; and
- revalidated immediately before bounded mock fulfillment.

The integrated proof target is:

```text
packet created
-> correct local Root authorizes packet
-> packet enters QUEUED
-> packet enters PENDING_FULFILLMENT
-> relevant dependency or WorldState condition changes
-> evidence is accepted under the correct Root policy
-> packet becomes revoked, superseded, expired, blocked, consumed,
   or otherwise deterministically non-executable
-> Corridor refuses fulfillment
-> prior authorization remains visible
-> transition and receipt history remains immutable
-> Replay cannot turn the old packet into a new execution
-> real-world effects remain zero
```

## 3. Accepted Starting State

The observed implementation basis is:

- branch `main`;
- `HEAD` and local `refs/remotes/origin/main` equal
  `681625c982e46b9adcd101d7c6bd355f4bea18f3`;
- worktree and staging were empty before this document was created;
- Gate 1 is `CLOSED_PASS`;
- the Two-Domain All-Real Sealed Evidence Program is `CLOSED_PASS`;
- Airline, Supplier Water Filter, X1, and X2 are `CLOSED_PASS`;
- public release is `NOT CLAIMED`;
- the current engineering gate is G2-A;
- G2-A implementation is `NOT STARTED`.

Closed Gate-1 and two-domain artifacts are immutable inputs. Their closure does
not authorize production behavior, public release, or a real connector.

## 4. Governing Source of Truth

The future implementation must obey this precedence:

1. this owner-reviewed G2-A preflight for the bounded G2-A lifecycle profile;
2. `hedgehog/action_commit_packet_v02.py` for the packet, scope, Corridor,
   receipt, and local registry family being extended;
3. `hedgehog/kernel/abi_v01.py` for the existing Kernel ABI family;
4. `hedgehog/kernel/transition_registry_v01.py` for the sole legal
   transition-policy family;
5. `hedgehog/kernel/effect_firewall_v01.py` for exclusive mock-effect handle
   ownership and one-shot consumption;
6. `hedgehog/kernel/integrity_replay_v01.py` for canonical JSON and
   domain-separated SHA-256 utilities;
7. the frozen Root contracts for authority identity and precedence;
8. accepted Gate-1 and two-domain tests, audits, and checkpoints as regression
   evidence.

Current source facts that motivate this extension:

- `ActionCommitPacketV02.packet_id` and `IdempotencyKeyV02.key` are currently
  transported strings rather than rebuilt canonical identities.
- `PacketTTL` currently carries string times plus `ttl_valid` and `expired`
  assertions.
- `ActionCommitPacketRegistryV02` currently stores tuple snapshots for seen,
  consumed, terminal-receipt, expired, and failed packet facts.
- `TransitionRegistryV01` already owns immutable legal-transition policy and
  blocks unknown transitions.
- `EffectFirewallV01` already owns the opaque adapter capability, local logical
  tick checks, duplicate blocking, one-shot consumption, and evidence-only
  receipts.

This preflight extends those accepted families without reinterpreting their
closed historical identities.

## 5. Architecture Locks

The canonical semantic route remains:

```text
Orchestrator semantic route proposal
-> local validation
-> Root-controlled route acceptance
-> BSEP creation and validation
-> side-specific BSEP projections
-> Semantic Architect semantic proposal only
-> local validation
-> runtime-owned RuntimeExecutionTopology
-> bounded actors / executors / fractal child cells
```

BSEP remains the canonical semantic membrane.

Provider or LLM output owns none of:

- PlanGraph;
- nodes;
- edges;
- executor assignments;
- action topology;
- authority;
- permission.

`RuntimeExecutionTopology` remains locally built and runtime-owned.
`PlanGraph` is legacy/proof-only compatibility IR and remains outside G2-A.
It is not an unresolved architecture question. This preflight authorizes no
PlanGraph implementation, migration, cleanup, deletion, BSEP redesign,
RuntimeExecutionTopology redesign, provider-contract change, or semantic-route
change.

Root remains the only authority owner. The Registry stores state and evidence.
The Corridor enforces current executability. Receipt remains evidence only.
Real-world effects remain zero.

## 6. Authorized and Frozen Path Scope

Future create paths:

```text
demo/run_action_commit_packet_lifecycle_g2_a_v01.py
tests/test_action_commit_packet_lifecycle_g2_a_v01.py
docs/audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log
docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md
```

Future modify paths:

```text
hedgehog/action_commit_packet_v02.py
hedgehog/kernel/abi_v01.py
hedgehog/kernel/transition_registry_v01.py
hedgehog/kernel/effect_firewall_v01.py
tests/test_action_commit_packet_contract_corridor_v02.py
tests/test_kernel_abi_v01.py
tests/test_transition_registry_v01.py
tests/test_effect_firewall_v01.py
demo/run_living_gauntlet_v01.py
tests/test_living_gauntlet_v01_runner.py
hedgehog/kernel/conformance_v01.py
demo/run_kernel_conformance_v01.py
tests/test_kernel_conformance_v01_runner.py
AGENTS.md
```

`AGENTS.md` is limited to the closure active-checkpoint block and only during
an independently authorized closure pass.

Every path not listed above is frozen. A discovered need outside the list
causes:

```text
FAIL_CLOSED_SCOPE_AMENDMENT_REQUIRED
```

It does not cause silent scope expansion.

The following paths and groups are explicitly frozen:

```text
hedgehog/action_commit_packet.py
hedgehog/kernel/root_decision_v01.py
hedgehog/kernel/root_signer_isolation_v01.py
hedgehog/kernel/multiroot_v01.py
hedgehog/kernel/integrity_replay_v01.py
hedgehog/context_packets.py
hedgehog/semantic_reasoning_adapter.py
hedgehog/domains/airline/**
hedgehog/domains/supplier_water_filter/**
hedgehog/evidence/**
schemas/**
docs/evidence/two_domain_all_real_sealed_evidence_program_v01/**
docs/showcase/two_domain_master_v01/**
docs/two_domain_all_real_sealed_evidence_program_v01_checkpoint.md
README.md
specs/**
release/**
```

All BSEP, provider, LLM semantic, PlanGraph, legacy topology, accepted
Airline/Supplier source evidence, X1/X2 audits, Package, Anchor, Replay, Human
Story, and presentation surfaces are frozen. G2-B through G2-F,
public-release remediation, showcase work, production integration, and real
connectors are frozen. Real payment, booking, ticket issuance, and shipment
release are forbidden.

Frozen Root contracts may be consumed read-only. Frozen domain contracts may
be read as reference inputs. The future G2-A proof must use bounded fixtures
and adapters in its new runner rather than rewrite closed domain evidence.

## 7. Existing Contracts Being Extended

The future implementation extends:

- `ActionCommitPacketV02`, `PermissionScopeV02`, `PacketTTL`,
  `IdempotencyKeyV02`, `AdapterBindingV02`, `PacketEvidenceRefV02`,
  `ActionCommitPacketRegistryV02`, `ContractFulfillmentCorridorV01`,
  `CorridorStepV01`, and `MockReceiptEvidenceV01` in
  `hedgehog/action_commit_packet_v02.py`;
- `KERNEL_ABI_VERSION`, `LIFECYCLE_STATES`, and `KernelArtifactV01` in
  `hedgehog/kernel/abi_v01.py` through a versioned compatible profile;
- `TransitionRuleV01`, `TransitionDecisionV01`, `TransitionRegistryV01`,
  `lookup_transition_v01`, and their validators in
  `hedgehog/kernel/transition_registry_v01.py`;
- `EffectRequestV01`, `EffectCapabilityV01`, the per-invocation state, and
  mock-only effect enforcement in `hedgehog/kernel/effect_firewall_v01.py`.

The future implementation must preserve:

- Root-only packet creation;
- no expansion after Root;
- child scope containment;
- mock-only adapter binding;
- receipt non-authority;
- Registry non-authority;
- unknown-transition fail-closed;
- opaque adapter-handle ownership in the Effect Firewall;
- no module-global mutable runtime state;
- deterministic canonical identities;
- no provider, network, Gemini, or real effect.

## 8. Authority Versus Deterministic Executability

Only the correct local Root may:

- create action authority;
- widen action authority;
- renew action authority;
- revoke action authority;
- supersede action authority;
- authorize a materially different consequential effect.

Registry and Corridor perform none of those authority operations.

A new Root decision is not required merely to enforce:

- expiry under an immutable Root-bound TTL;
- a not-yet-valid temporal state;
- terminal idempotency consumption;
- an accepted terminal receipt state;
- a stale mandatory dependency;
- a malformed or inconsistent temporal contract;
- a Root-accepted policy-bound kill-switch condition;
- an already recorded revocation;
- an already recorded supersession.

For those cases, Registry records state and immutable evidence, while Corridor
recomputes and enforces current executability. Neither component creates,
widens, renews, revokes, or supersedes authority.

A new Root decision is required to:

- renew TTL;
- widen or change scope;
- authorize a materially different effect;
- issue a revocation outside a Root-bound deterministic condition;
- supersede the packet with new authority.

No redundant Root decision is required merely to observe expiry or consumed
idempotency.

## 9. Canonical ActionCommitPacketV02 Family

`ActionCommitPacketV02` is the sole canonical packet family for G2-A.

`hedgehog/action_commit_packet.py` is a compatibility-only legacy packet
surface. It is not an independent current authority family. No new G2-A
capability may depend directly on its dictionary packet.

The G2-A packet validator must rebuild:

- packet identity;
- idempotency identity;
- Root decision provenance;
- scope bindings;
- dependency bindings;
- temporal authority;
- policy binding;
- predecessor and supersession binding.

Transported `packet_id` and `idempotency_key` values are assertions. They do
not define identity.

## 10. Exact Cryptographic Canonicalization Profile

The canonical encoding profile is
`actionpacket_lifecycle_canonical_encoding_profile_v01`.

1. Identity material is a JSON array of exact two-element arrays:

   ```json
   [
     ["field_name_1", "value_1"],
     ["field_name_2", "value_2"]
   ]
   ```

2. Top-level identity material is never an unordered mapping.
3. Field order is semantically significant and profile-fixed.
4. Every profile field occurs exactly once.
5. A missing field fails closed.
6. A duplicate field name fails closed.
7. An unknown field fails closed.
8. JSON `null` never represents absence.
9. Empty string, empty array, and empty object never represent absence.
10. The sole absence sentinel is:

    ```json
    {"$hedgehog_absent": "ABSENT_V01"}
    ```

11. The sentinel object is reserved and rejected as ordinary domain data.
12. Every optional field remains in its profile position and carries the
    sentinel when absent.
13. A required field carrying the sentinel fails closed.
14. Canonical bytes come from
    `hedgehog.kernel.integrity_replay_v01.canonical_json_bytes_v01`.
15. Digests come from
    `hedgehog.kernel.integrity_replay_v01.domain_separated_sha256_hex_v01`.
16. Every digest is lowercase hexadecimal of length 64.
17. Encoding is UTF-8 without BOM, NUL, CR conversion, or non-finite numbers.
18. Boolean values fail any exact-integer field.
19. Identity strings are case-sensitive.
20. No trimming, case folding, or locale transformation occurs.
21. Identity-bearing text is normalized to Unicode NFC before validation and
    canonicalization. Normalization occurs exactly once. Lone surrogates and
    NUL fail closed.
22. A set-like string collection accepts an exact tuple of non-empty strings,
    NFC-normalizes each element, rejects duplicates after normalization, and
    emits a JSON array sorted by ascending normalized UTF-8 byte sequence.
    Caller order has no effect.
23. An ordered semantic collection accepts an exact tuple and preserves its
    contract order.
24. A consequential decimal enters identity material only as an already
    canonical string matching
    `0|-?[1-9][0-9]*(\.[0-9]*[1-9])?`. A plus sign, exponent, leading zero,
    trailing fractional zero, negative zero, binary float, and non-finite
    value fail closed.
25. A profile field addition, deletion, rename, reorder, type change,
    normalization change, sentinel change, prefix change, or domain change
    requires a new profile version, new domain separator, explicit
    compatibility law, and no reinterpretation of old identities.

All profile validators must be total over malformed input and return stable
fail-closed reason tuples. Builders may raise sanitized `ValueError` only
after validation identifies a stable reason.

## 11. Exact Packet Identity Profile

Exact constants:

```text
packet_identity_profile_id =
  action_commit_packet_identity_profile_v01

packet_identity_domain_separator =
  HEDGEHOG_ACTION_COMMIT_PACKET_ID_V01

packet_identity_prefix =
  acp_v02:
```

Exact closed material:

```text
packet_identity_material_v01 = [
  ["packet_contract_family", "ActionCommitPacketV02"],
  ["packet_contract_version", "v0.2"],
  ["owning_local_root_id", VALUE],
  ["source_root_decision_id", VALUE],
  ["source_root_decision_hash", VALUE],
  ["transaction_id", VALUE_OR_ABSENT_V01],
  ["root_owned_intent_id", VALUE_OR_ABSENT_V01],
  ["effect_class", VALUE],
  ["normalized_subject_scope", VALUE],
  ["normalized_target_scope", VALUE],
  ["normalized_permission_scope", VALUE],
  ["normalized_effect_parameters_fingerprint", VALUE],
  ["corridor_class", VALUE],
  ["adapter_binding", VALUE],
  ["dependency_fingerprint", VALUE],
  ["temporal_authority_fingerprint", VALUE],
  ["policy_version", VALUE_OR_ABSENT_V01],
  ["authority_policy_fingerprint", VALUE_OR_ABSENT_V01],
  ["predecessor_packet_id", VALUE_OR_ABSENT_V01],
  ["supersession_reason_class", VALUE_OR_ABSENT_V01]
]
```

`len(packet_identity_material_v01) == 20`.

Identifier pair law:

```text
transaction_id is ABSENT_V01
AND root_owned_intent_id is ABSENT_V01
-> FAIL_CLOSED
```

Both positions always remain present. If both identifiers exist, both are
bound. If one identifier is absent, its position contains `ABSENT_V01`.

Policy pair law:

```text
policy_version is ABSENT_V01
AND authority_policy_fingerprint is ABSENT_V01
-> FAIL_CLOSED
```

Both positions always remain present. If both policy values exist, both are
bound. If one is absent, its position contains `ABSENT_V01`.

Initial packet:

```text
predecessor_packet_id = ABSENT_V01
supersession_reason_class = ABSENT_V01
```

Renewal packet:

```text
predecessor_packet_id = exact predecessor packet_id
supersession_reason_class = "RENEWAL"
```

Superseding packet:

```text
predecessor_packet_id = exact predecessor packet_id
supersession_reason_class = exact non-empty canonical reason class
```

Revocation creates no renamed packet and changes none of this material.

Exact construction:

```text
packet_digest =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_COMMIT_PACKET_ID_V01",
    packet_identity_material_v01
  )

packet_id =
  "acp_v02:" + packet_digest
```

Validation rebuilds the value and rejects mismatch. Caller input may transport
`packet_id`; caller input never defines it.

## 12. Exact Idempotency Identity Profile

Exact constants:

```text
idempotency_identity_profile_id =
  action_idempotency_identity_profile_v01

idempotency_identity_domain_separator =
  HEDGEHOG_ACTION_IDEMPOTENCY_KEY_V01

idempotency_identity_prefix =
  idem:acp_v02:
```

Exact closed material:

```text
idempotency_identity_material_v01 = [
  ["idempotency_contract_version", "v0.1"],
  ["owning_effect_root_id", VALUE],
  ["transaction_id", VALUE_OR_ABSENT_V01],
  ["root_owned_intent_id", VALUE_OR_ABSENT_V01],
  ["logical_effect_class", VALUE],
  ["normalized_subject_scope", VALUE],
  ["normalized_target_scope", VALUE],
  ["normalized_business_object_identity", VALUE],
  ["normalized_consequential_effect_parameters", VALUE],
  ["logical_effect_namespace", VALUE]
]
```

`len(idempotency_identity_material_v01) == 10`.

Identifier pair law:

```text
transaction_id is ABSENT_V01
AND root_owned_intent_id is ABSENT_V01
-> FAIL_CLOSED
```

Both positions always remain present. If both identifiers exist, both are
bound. If one is absent, its position contains `ABSENT_V01`.

Exact construction:

```text
idempotency_digest =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_IDEMPOTENCY_KEY_V01",
    idempotency_identity_material_v01
  )

idempotency_key =
  "idem:acp_v02:" + idempotency_digest
```

Validation rebuilds the value and rejects mismatch.

Idempotency material excludes:

```text
packet_id
packet contract version
packet retry counter
packet issue time
packet expiry time
adapter implementation name
Registry state
supersession sequence
execution_attempt_id
```

A packet version, TTL change, adapter change, or retry does not create a new
logical-effect identity. A materially different consequential effect requires
a new Root decision and a new canonical idempotency identity.

## 13. Exact Nested Normalization Profiles

All ten profiles below use the encoding law in section 10. Profile ID is the
first exact field. Closed record arrays contain only records defined here.
All strings are NFC-normalized, case-sensitive, and non-empty. All set-like
string arrays use the section 10 UTF-8-byte sorting law. All ordered
two-element field arrays use their displayed order.

### 13.1 Subject scope

```text
profile_id = action_subject_scope_profile_v01
material = [
  ["profile_id", "action_subject_scope_profile_v01"],
  ["included_subject_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["excluded_subject_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY]
]
```

`included_subject_refs` has cardinality greater than or equal to 1.
The two arrays must be disjoint. Empty included scope, duplicate normalized
reference, overlap, wrong type, sentinel use, or unknown field fails closed.
`normalized_subject_scope` is this exact material, not a digest.

### 13.2 Target scope

```text
profile_id = action_target_scope_profile_v01
material = [
  ["profile_id", "action_target_scope_profile_v01"],
  ["included_target_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["excluded_target_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY]
]
```

`included_target_refs` has cardinality greater than or equal to 1.
The arrays must be disjoint. Empty included scope, duplicate normalized
reference, overlap, wrong type, sentinel use, or unknown field fails closed.
`normalized_target_scope` is this exact material.

### 13.3 Permission scope

```text
profile_id = action_permission_scope_profile_v01
material = [
  ["profile_id", "action_permission_scope_profile_v01"],
  ["allowed_action_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["forbidden_action_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["required_approval_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["prohibited_effect_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY]
]
```

`allowed_action_classes` and `required_approval_refs` each have cardinality
greater than or equal to 1. Allowed and forbidden action classes are disjoint.
Duplicates, overlap, wrong type, sentinel use, or unknown field fails closed.
`normalized_permission_scope` is this exact material.

### 13.4 Effect-parameters fingerprint

```text
profile_id = action_effect_parameters_profile_v01
parameter_record = [
  ["parameter_name", EXACT_NON_EMPTY_STRING],
  ["value_type", ONE_OF_TEXT_DECIMAL_INTEGER_BOOLEAN_REFERENCE],
  ["value", EXACT_VALUE_FOR_DECLARED_TYPE]
]
material = [
  ["profile_id", "action_effect_parameters_profile_v01"],
  ["effect_class", EXACT_NON_EMPTY_STRING],
  ["parameter_records", EXACT_SORTED_UNIQUE_PARAMETER_RECORD_ARRAY]
]
domain_separator = HEDGEHOG_ACTION_EFFECT_PARAMETERS_V01
```

`parameter_records` is sorted by normalized `parameter_name` UTF-8 bytes.
Names are unique. `TEXT` and `REFERENCE` values are NFC non-empty strings.
`DECIMAL` uses section 10 decimal normalization. `INTEGER` is signed int64
with boolean rejected. `BOOLEAN` is exact bool. An unsupported type, duplicate
name, type/value mismatch, sentinel, or unknown field fails closed.

```text
normalized_effect_parameters_fingerprint =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_EFFECT_PARAMETERS_V01",
    material
  )
```

### 13.5 Adapter binding

```text
profile_id = action_adapter_binding_profile_v01
material = [
  ["profile_id", "action_adapter_binding_profile_v01"],
  ["corridor_class", EXACT_NON_EMPTY_STRING],
  ["adapter_id", EXACT_NON_EMPTY_STRING],
  ["adapter_kind", EXACT_NON_EMPTY_STRING],
  ["adapter_version", EXACT_NON_EMPTY_STRING],
  ["mock_only", true]
]
```

All text is required. `mock_only` is exact bool and must be `true`. Sentinel
use, a real adapter, wrong type, or unknown field fails closed.
`adapter_binding` is this exact material.

### 13.6 Dependency fingerprint

```text
profile_id = action_dependency_set_profile_v01
dependency_record = [
  ["dependency_id", EXACT_NON_EMPTY_STRING],
  ["dependency_class", EXACT_NON_EMPTY_STRING],
  ["evidence_ref", EXACT_NON_EMPTY_STRING],
  ["content_sha256", EXACT_LOWERCASE_SHA256],
  ["requirement_class", ONE_OF_MANDATORY_OPTIONAL],
  ["time_envelope_id", VALUE_OR_ABSENT_V01],
  ["freshness_policy_id", VALUE_OR_ABSENT_V01],
  ["accepted_status", EXACT_NON_EMPTY_STRING]
]
material = [
  ["profile_id", "action_dependency_set_profile_v01"],
  ["dependency_records", EXACT_SORTED_UNIQUE_DEPENDENCY_RECORD_ARRAY]
]
domain_separator = HEDGEHOG_ACTION_DEPENDENCY_SET_V01
```

Records are sorted by normalized `dependency_id` UTF-8 bytes and IDs are
unique. A `MANDATORY` record requires non-sentinel `time_envelope_id` and
`freshness_policy_id`. An `OPTIONAL` record uses either two non-sentinel
values or two sentinel values. Partial time binding fails closed. Missing,
stale, replaced, contradictory, duplicate, wrong-hash, wrong-type, or unknown
dependency material fails closed.

```text
dependency_fingerprint =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_DEPENDENCY_SET_V01",
    material
  )
```

### 13.7 Temporal authority fingerprint

```text
profile_id = action_temporal_authority_profile_v01
material = [
  ["issued_at_utc", EXACT_INT64],
  ["expires_at_utc", EXACT_INT64],
  ["ttl_seconds", EXACT_POSITIVE_INT],
  ["temporal_policy_version", EXACT_NON_EMPTY_STRING]
]
domain_separator = HEDGEHOG_ACTION_TEMPORAL_AUTHORITY_V01
```

The exact derivation and failure laws are in section 14. A wrong type,
sentinel, inconsistent interval, or unknown field fails closed.

### 13.8 Authority-policy fingerprint

```text
profile_id = action_authority_policy_profile_v01
material = [
  ["profile_id", "action_authority_policy_profile_v01"],
  ["policy_version", EXACT_NON_EMPTY_STRING],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["authority_rule_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["kill_switch_condition_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["retry_policy", ONE_OF_NO_RETRY_NON_CONSUMING_RETRY],
  ["supersession_policy", ONE_OF_ROOT_DECISION_ONLY]
]
domain_separator = HEDGEHOG_ACTION_AUTHORITY_POLICY_V01
```

`authority_rule_refs` has cardinality greater than or equal to 1.
`kill_switch_condition_refs` may be empty but must be an exact array.
Duplicate, wrong-type, sentinel, or unknown material fails closed.

```text
authority_policy_fingerprint =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_AUTHORITY_POLICY_V01",
    material
  )
```

### 13.9 Business-object identity

```text
profile_id = action_business_object_identity_profile_v01
material = [
  ["profile_id", "action_business_object_identity_profile_v01"],
  ["business_object_class", EXACT_NON_EMPTY_STRING],
  ["business_object_namespace", EXACT_NON_EMPTY_STRING],
  ["business_object_ref", EXACT_NON_EMPTY_STRING],
  ["owning_effect_root_id", EXACT_NON_EMPTY_STRING]
]
```

All fields are required. Sentinel use, wrong type, or unknown field fails
closed. `normalized_business_object_identity` is this exact material.

### 13.10 Consequential effect parameters

```text
profile_id = action_consequential_effect_parameters_profile_v01
parameter_record = [
  ["parameter_name", EXACT_NON_EMPTY_STRING],
  ["value_type", ONE_OF_TEXT_DECIMAL_INTEGER_BOOLEAN_REFERENCE],
  ["value", EXACT_VALUE_FOR_DECLARED_TYPE]
]
material = [
  ["profile_id", "action_consequential_effect_parameters_profile_v01"],
  ["amount_decimal", VALUE_OR_ABSENT_V01],
  ["currency_code", VALUE_OR_ABSENT_V01],
  ["quantity_decimal", VALUE_OR_ABSENT_V01],
  ["parameter_records", EXACT_SORTED_UNIQUE_PARAMETER_RECORD_ARRAY]
]
```

`amount_decimal` and `quantity_decimal` use section 10 decimal strings.
`currency_code` is an NFC uppercase ASCII string matching `[A-Z]{3}`.
If amount is present, currency is required. Currency without amount fails
closed. Records use section 13.4 type rules and sort by normalized
`parameter_name` UTF-8 bytes. Duplicate, type mismatch, reserved sentinel as
data, or unknown field fails closed.
`normalized_consequential_effect_parameters` is this exact material.

Each nested profile is closed under its profile version. Airline-shaped and
Supplier-shaped adapters populate these domain-neutral materials without
changing field sets or importing domain authority into the kernel.

## 14. Canonical Time and Expiry Profile

```text
CanonicalExecutionTimeV01 = signed int64 UTC epoch seconds
```

Exact integer law:

```text
type(value) is int
bool is rejected
-9223372036854775808 <= value <= 9223372036854775807
```

No canonical Registry, validator, Corridor, or Replay function calls an
ambient wall clock.

Evaluation requires:

```text
evaluation_time
evaluation_time_source
evaluation_context_id
```

`evaluation_time` is `CanonicalExecutionTimeV01`.
`evaluation_time_source` and `evaluation_context_id` are exact non-empty NFC
strings bound into every observation or transition that uses them.

Exact immutable Root-bound material:

```text
temporal_authority_material_v01 = [
  ["issued_at_utc", EXACT_INT64],
  ["expires_at_utc", EXACT_INT64],
  ["ttl_seconds", EXACT_POSITIVE_INT],
  ["temporal_policy_version", EXACT_NON_EMPTY_STRING]
]
```

```text
temporal_authority_domain_separator =
  HEDGEHOG_ACTION_TEMPORAL_AUTHORITY_V01
```

Exact derivation:

```text
temporal_authority_fingerprint =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_TEMPORAL_AUTHORITY_V01",
    temporal_authority_material_v01
  )
```

Exact consistency:

```text
ttl_seconds > 0
expires_at_utc == issued_at_utc + ttl_seconds
```

The addition must remain inside signed int64 range. Overflow fails closed.

Half-open execution interval:

```text
issued_at_utc <= evaluation_time < expires_at_utc
```

Outcomes:

```text
evaluation_time < issued_at_utc
-> NOT_YET_VALID
-> NON_EXECUTABLE
-> FAIL_CLOSED FOR FULFILLMENT

evaluation_time >= expires_at_utc
-> EXPIRED
-> NON_EXECUTABLE
```

Inconsistent temporal fields fail closed without repair, field preference, or
classification as ordinary expiry. They never enter an executable Registry
state.

Existing `expired` and `ttl_valid` values are compatibility assertions only.
Canonical logic recomputes both. Assertion mismatch fails closed. Removal is
reserved for a later explicitly versioned migration.

Registry may record `EXPIRED` without a new Root decision. `EXPIRED` never
overwrites `FULFILLED_MOCK`, `RECEIPT_RECEIVED`, `REVOKED`, `SUPERSEDED`, or
another terminal consumed state. A temporal observation may be appended after
a terminal state but does not rewrite that lifecycle state.

## 15. Logical-Time Compatibility Bridge

Prospective immutable type:

```text
LogicalTimeBridgeV01 {
  bridge_id
  origin_utc_epoch_seconds
  seconds_per_tick
  bridge_policy_version
}
```

Exact bridge identity material:

```text
logical_time_bridge_material_v01 = [
  ["bridge_policy_version", EXACT_NON_EMPTY_STRING],
  ["origin_utc_epoch_seconds", EXACT_INT64],
  ["seconds_per_tick", EXACT_POSITIVE_INT]
]
```

Exact bridge identity:

```text
bridge_id =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_LOGICAL_TIME_BRIDGE_V01",
    logical_time_bridge_material_v01
  )
```

Exact conversion:

```text
canonical_epoch_seconds =
  origin_utc_epoch_seconds
  + logical_tick * seconds_per_tick
```

Every integer rejects bool. `logical_tick` is a non-negative exact int64.
`seconds_per_tick` is a positive exact int64. Multiplication, addition, and
result must remain in signed int64 range. Overflow fails closed.

An unbridged logical tick cannot prove freshness or expiry and fails closed.
Effect Firewall may retain its existing local tick rules, but they cannot
extend or contradict the canonical Root-bound packet TTL.

## 16. PacketTTL and TimeEnvelope Relationship

`PacketTTL` is the specialized Root-bound temporal authority interval for one
packet.

`TimeEnvelope` is the broader validity and freshness envelope for knowledge,
evidence, dependencies, and semantic context.

Packet executability requires:

```text
packet temporal authority valid
AND every mandatory dependency currently valid under its accepted
    TimeEnvelope and policy
```

Fresh evidence cannot renew an expired packet. An unexpired packet cannot use
a stale mandatory dependency. Packet renewal requires a new local Root
decision.

The future dependency validator must consume accepted TimeEnvelope identity and
freshness policy evidence. It must not copy freshness booleans without
recomputation against injected evaluation time.

## 17. Canonical Lifecycle State Profile

The canonical G2-A profile belongs to the existing Kernel ABI and Transition
Registry families:

```text
profile_id = action_packet_lifecycle_profile_v01
abi_family = hedgehog_kernel_abi
transition_registry_family = TransitionRegistryV01
```

Exact states:

```text
CREATED
ROOT_AUTHORIZED
QUEUED
PENDING_FULFILLMENT
FULFILLED_MOCK
RECEIPT_RECEIVED
FAILED
BLOCKED
EXPIRED
REVOKED
SUPERSEDED
```

No second independent lifecycle enum is authorized.

`hedgehog/kernel/abi_v01.py` currently freezes `KERNEL_ABI_VERSION = "v1.0"`
and historical `LIFECYCLE_STATES`. G2-A must add an explicit versioned
`action_packet_lifecycle_profile_v01` within the same ABI family. Existing
v1.0 constants, builders, validators, Registry IDs, and historical artifacts
retain their exact meaning and bytes. G2-A-aware builders explicitly select
the new profile. Legacy builders remain on v1.0.

The profile is consumed by the existing `TransitionRegistryV01` family through
a versioned Registry profile. The lifecycle profile and Registry profile must
cross-bind exact IDs. There is one current G2-A source of transition truth and
no silent change to old canonical IDs.

## 18. Legal Transition Table

Exact table columns:

| transition_id | source_state | target_state | transition_class | permitted_actor_or_component | Root_decision_required | required_evidence | idempotency_consumed | adapter_call_allowed | terminal_target | reason_code | fail_closed_conditions |
|---|---|---|---|---|---:|---|---:|---:|---:|---|---|
| g2a_t01_create_authority | CREATED | ROOT_AUTHORIZED | AUTHORITY | owning_local_root | true | exact Root decision and packet identity | false | false | false | root_authorized | wrong Root; missing or mismatched decision; invalid packet |
| g2a_t02_queue | ROOT_AUTHORIZED | QUEUED | DETERMINISTIC | lifecycle_runtime | false | valid history; valid temporal and dependency evidence | false | false | false | packet_queued | non-executable packet; invalid history |
| g2a_t03_pending | QUEUED | PENDING_FULFILLMENT | DETERMINISTIC | exclusive_corridor | false | immediate pre-fulfillment validation | false | false | false | pending_fulfillment | any current eligibility failure |
| g2a_t04_fulfill_mock | PENDING_FULFILLMENT | FULFILLED_MOCK | DETERMINISTIC_CONSUMING | exclusive_corridor | false | successful mock adapter result and consumption evidence | true | true | false | fulfilled_mock | adapter failure; missing consumption; any changed eligibility |
| g2a_t05_receipt | FULFILLED_MOCK | RECEIPT_RECEIVED | DETERMINISTIC_CONSUMING | receipt_observer | false | validated evidence-only terminal receipt | true | false | true | receipt_received | invalid receipt; wrong packet or key; authority claim |
| g2a_t06_created_block | CREATED | BLOCKED | DETERMINISTIC | lifecycle_runtime | false | exact blocking evidence | false | false | true | packet_blocked | missing evidence; authority expansion |
| g2a_t07_authorized_block | ROOT_AUTHORIZED | BLOCKED | DETERMINISTIC | lifecycle_runtime | false | exact blocking or Root-bound kill-switch evidence | false | false | true | packet_blocked | missing evidence; authority expansion |
| g2a_t08_queued_block | QUEUED | BLOCKED | DETERMINISTIC | lifecycle_runtime | false | exact blocking or Root-bound kill-switch evidence | false | false | true | packet_blocked | missing evidence; authority expansion |
| g2a_t09_pending_block | PENDING_FULFILLMENT | BLOCKED | DETERMINISTIC | exclusive_corridor | false | immediate failed eligibility evidence | false | false | true | packet_blocked | adapter already called; missing evidence |
| g2a_t10_failed_block | FAILED | BLOCKED | DETERMINISTIC | lifecycle_runtime | false | retry-ineligible evidence | false | false | true | packet_blocked | missing evidence; authority expansion |
| g2a_t11_created_expire | CREATED | EXPIRED | DETERMINISTIC | temporal_validator | false | injected time and valid temporal authority | false | false | true | packet_expired | inconsistent time; prior terminal state |
| g2a_t12_authorized_expire | ROOT_AUTHORIZED | EXPIRED | DETERMINISTIC | temporal_validator | false | injected time and valid temporal authority | false | false | true | packet_expired | inconsistent time; prior terminal state |
| g2a_t13_queued_expire | QUEUED | EXPIRED | DETERMINISTIC | temporal_validator | false | injected time and valid temporal authority | false | false | true | packet_expired | inconsistent time; prior terminal state |
| g2a_t14_pending_expire | PENDING_FULFILLMENT | EXPIRED | DETERMINISTIC | exclusive_corridor | false | immediate injected time and valid temporal authority | false | false | true | packet_expired | adapter already called; inconsistent time |
| g2a_t15_failed_expire | FAILED | EXPIRED | DETERMINISTIC | temporal_validator | false | injected time and valid temporal authority | false | false | true | packet_expired | inconsistent time; prior terminal state |
| g2a_t16_authorized_revoke | ROOT_AUTHORIZED | REVOKED | AUTHORITY | owning_local_root | true | immutable Root revocation decision | false | false | true | packet_revoked | foreign Root; missing or mismatched decision |
| g2a_t17_queued_revoke | QUEUED | REVOKED | AUTHORITY | owning_local_root | true | immutable Root revocation decision | false | false | true | packet_revoked | foreign Root; missing or mismatched decision |
| g2a_t18_pending_revoke | PENDING_FULFILLMENT | REVOKED | AUTHORITY | owning_local_root | true | immutable Root revocation decision before adapter call | false | false | true | packet_revoked | adapter already called; foreign Root |
| g2a_t19_failed_revoke | FAILED | REVOKED | AUTHORITY | owning_local_root | true | immutable Root revocation decision | false | false | true | packet_revoked | foreign Root; missing or mismatched decision |
| g2a_t20_authorized_supersede | ROOT_AUTHORIZED | SUPERSEDED | AUTHORITY | owning_local_root | true | validated successor packet and Root decision | false | false | true | packet_superseded | missing successor; predecessor mismatch; foreign Root |
| g2a_t21_queued_supersede | QUEUED | SUPERSEDED | AUTHORITY | owning_local_root | true | validated successor packet and Root decision | false | false | true | packet_superseded | missing successor; predecessor mismatch; foreign Root |
| g2a_t22_pending_supersede | PENDING_FULFILLMENT | SUPERSEDED | AUTHORITY | owning_local_root | true | validated successor before adapter call and Root decision | false | false | true | packet_superseded | adapter already called; missing successor; foreign Root |
| g2a_t23_failed_supersede | FAILED | SUPERSEDED | AUTHORITY | owning_local_root | true | validated successor packet and Root decision | false | false | true | packet_superseded | missing successor; predecessor mismatch; foreign Root |
| g2a_t24_nonconsuming_failure | PENDING_FULFILLMENT | FAILED | DETERMINISTIC | exclusive_corridor | false | immutable non-consuming failure evidence | false | false | false | fulfillment_failed_nonconsuming | effect consumed; uncertain consumption; missing failure evidence |
| g2a_t25_retry | FAILED | QUEUED | DETERMINISTIC | lifecycle_runtime | false | Root-bound retry policy and unchanged current eligibility | false | false | false | nonconsuming_retry_queued | key or packet changed; terminal evidence; stale dependency; no retry policy |

Authority transitions are packet creation, `ROOT_AUTHORIZED`, `REVOKED`,
`SUPERSEDED`, and renewal through a newly created packet. They require the
correct local Root decision. A Root-bound kill-switch is enforced as
`BLOCKED`; it does not let Registry create a `REVOKED` event.

Deterministic non-authority transitions and verdicts record or enforce
consequences without creating or widening authority.

Additional exact laws:

- Unknown transition fails closed.
- Insertion order never implies a transition.
- Lexical packet version never implies a transition.
- No latest-packet rule exists.
- A terminal state is not overwritten by a later expiry observation.
- No terminal-to-active transition exists.
- `FULFILLED_MOCK` is effect-consumed and non-executable. Its sole normal
  successor is `RECEIPT_RECEIVED`.
- A failure after effect consumption cannot return to an executable state.
- `FAILED -> QUEUED` requires immutable proof that failure was non-consuming,
  retry is Root-policy permitted, packet and key are unchanged, no terminal
  receipt exists, time is valid, no revocation or supersession exists, and
  dependencies remain current.
- `BLOCKED`, `EXPIRED`, `REVOKED`, `SUPERSEDED`, and `RECEIPT_RECEIVED` are
  non-executable terminal states.
- Transition-table change requires a new profile, new Registry identity, and
  owner review.

`TransitionRegistryV01` remains the sole legal transition-table family.
`ActionCommitPacketRegistryV02` cannot invent transition legality.

## 19. Registry State and Immutable History

`ActionCommitPacketRegistryV02` must evolve from tuple snapshot sets into a
deterministic non-authority lifecycle store. It remains in-memory,
local/mock-only, non-production, and not DRS.

The future contract separates:

- immutable event history;
- derived current lifecycle state;
- derived executability;
- idempotency consumption;
- terminal receipt binding;
- dependency status;
- authority evidence.

Exact transition identity constants:

```text
transition_identity_profile_id =
  action_packet_transition_identity_profile_v01

transition_identity_domain_separator =
  HEDGEHOG_ACTION_PACKET_TRANSITION_V01

transition_identity_prefix =
  acpt_v01:
```

Exact closed transition material:

```text
transition_identity_material_v01 = [
  ["transition_profile_version", "v0.1"],
  ["registry_profile_id", "action_packet_lifecycle_registry_profile_v01"],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["idempotency_key", EXACT_CANONICAL_IDEMPOTENCY_KEY],
  ["previous_transition_id", VALUE_OR_ABSENT_V01],
  ["source_state", EXACT_LIFECYCLE_STATE],
  ["target_state", EXACT_LIFECYCLE_STATE],
  ["transition_class", EXACT_TRANSITION_CLASS],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["root_decision_ref", VALUE_OR_ABSENT_V01],
  ["evidence_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["reason_code", EXACT_TABLE_REASON_CODE],
  ["dependency_fingerprint", EXACT_LOWERCASE_SHA256],
  ["temporal_authority_fingerprint", EXACT_LOWERCASE_SHA256],
  ["evaluation_time", EXACT_INT64],
  ["evaluation_time_source", EXACT_NON_EMPTY_STRING],
  ["evaluation_context_id", EXACT_NON_EMPTY_STRING],
  ["execution_attempt_id", VALUE_OR_ABSENT_V01],
  ["effect_consumption_class", ONE_OF_NOT_CONSUMED_CONSUMED_UNCERTAIN],
  ["receipt_ref", VALUE_OR_ABSENT_V01]
]
```

`len(transition_identity_material_v01) == 20`.

Exact identity:

```text
transition_digest =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_PACKET_TRANSITION_V01",
    transition_identity_material_v01
  )

transition_id =
  "acpt_v01:" + transition_digest
```

The first record uses `previous_transition_id = ABSENT_V01`; every later record
binds the exact prior transition ID. Authority transitions require a
non-sentinel Root decision reference. Non-authority transitions use
`ABSENT_V01` unless they cite an existing Root policy decision as evidence.
`CONSUMED` requires `FULFILLED_MOCK` or `RECEIPT_RECEIVED`.
`UNCERTAIN` always produces non-executability and cannot support retry.

History is append-only. Deletion, rewriting, arbitrary snapshot replacement,
caller-selected transition ID, missing previous link, duplicate transition,
omitted record, and history fork fail closed. Current state is reconstructed
from validated ordered history. No mutable history alias may escape.

Registry is not Root, DRS, business truth, permission, packet authority,
receipt creator, adapter invoker, payment executor, or shipment releaser.

## 20. Root Authorization, Renewal, Revocation and Supersession

Root authorization binds:

- exact owning local Root ID;
- exact source Root decision ID and hash;
- exact packet identity profile;
- exact scope and effect;
- exact dependency set;
- exact temporal authority;
- exact authority policy;
- exact idempotency identity.

Renewal requires a new local Root decision and new `packet_id`. The successor
binds its predecessor and `"RENEWAL"`. Unchanged logical effect preserves the
same `idempotency_key`. Renewal cannot reopen consumed idempotency or widen
scope without explicit new authority.

Revocation keeps packet ID and idempotency key unchanged. An immutable
Root-owned revocation event preserves the prior authorization as history and
makes current executability false.

Supersession requires a new local Root decision, a new packet ID, exact
predecessor binding, and immutable predecessor `SUPERSEDED` history. Unchanged
logical effect preserves the idempotency key. Supersession is never inferred
from time, insertion order, lexical order, or latest naming.

A foreign Root cannot authorize, renew, revoke, or supersede another Root's
packet. Existing MultiRoot contracts remain frozen.

## 21. Deterministic Non-Executability

The following produce non-executability without creating an authority change:

- temporal contract inconsistency;
- not-yet-valid evaluation;
- deterministic expiry;
- stale or missing mandatory dependency;
- accepted Root-bound kill-switch evidence;
- terminal idempotency consumption;
- terminal receipt;
- recorded revocation;
- recorded supersession;
- illegal or unknown lifecycle transition;
- malformed history;
- uncertain effect consumption;
- scope or adapter mismatch.

Registry records exact state and evidence. Corridor independently recomputes
present eligibility. A `BLOCKED` verdict under a Root-bound kill-switch does
not pretend Registry revoked authority. Historical authorization remains
auditable while present executability is false.

## 22. Retry and Terminal Consumption

```text
packet_id = exact Root authorization object/version
idempotency_key = exact logical consequential effect protected from duplicate
                  fulfillment
```

Retry before terminal consumption requires:

- same packet ID;
- same idempotency key;
- distinct `execution_attempt_id` permitted as audit metadata;
- valid packet time;
- no revocation;
- no supersession;
- current dependencies;
- explicit non-consuming failure;
- Root-bound policy permitting retry.

Retry after terminal consumption is `BLOCKED`.

Terminal consumption includes:

- successful `FULFILLED_MOCK`;
- accepted terminal receipt;
- exact terminal consumption event;
- an equivalent terminal effect closure introduced only by a new versioned
  profile.

A new packet ID cannot bypass a consumed idempotency key. Retry counter, issue
time, expiry time, adapter implementation change, and execution-attempt ID
cannot change logical-effect identity.

## 23. Dependency and Kill-Switch Evidence

Prospective domain-neutral invalidation record:

```text
profile_id = action_invalidation_evidence_profile_v01
material = [
  ["profile_id", "action_invalidation_evidence_profile_v01"],
  ["invalidation_event_id", EXACT_NON_EMPTY_STRING],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["dependency_id", EXACT_NON_EMPTY_STRING],
  ["invalidation_class", EXACT_NON_EMPTY_STRING],
  ["evidence_ref", EXACT_NON_EMPTY_STRING],
  ["evidence_sha256", EXACT_LOWERCASE_SHA256],
  ["observed_status", EXACT_NON_EMPTY_STRING],
  ["time_envelope_id", EXACT_NON_EMPTY_STRING],
  ["freshness_policy_id", EXACT_NON_EMPTY_STRING],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["authority_effect", ONE_OF_DETERMINISTIC_BLOCK_ROOT_REVOCATION_ROOT_SUPERSESSION],
  ["root_decision_ref", VALUE_OR_ABSENT_V01],
  ["evaluation_time", EXACT_INT64],
  ["evaluation_time_source", EXACT_NON_EMPTY_STRING],
  ["evaluation_context_id", EXACT_NON_EMPTY_STRING]
]
domain_separator = HEDGEHOG_ACTION_INVALIDATION_EVIDENCE_V01
```

Exact event identity:

```text
invalidation_evidence_id =
  domain_separated_sha256_hex_v01(
    "HEDGEHOG_ACTION_INVALIDATION_EVIDENCE_V01",
    material
  )
```

`ROOT_REVOCATION` and `ROOT_SUPERSESSION` require a non-sentinel exact Root
decision reference. `DETERMINISTIC_BLOCK` requires `ABSENT_V01` and a
kill-switch condition already bound by the packet authority-policy
fingerprint.

The dependency fingerprint is exactly section 13.6. It binds the
Root-accepted mandatory dependency set, content hashes, TimeEnvelope
identities, freshness policies, requirement classes, and accepted statuses.

Airline hold expiry, price change, passenger mismatch, and bank-authorization
revocation can be translated into this shape. Supplier fraud flag, legal hold,
and manual-cancellation evidence can be translated into this shape. Domain
adapters cannot create authority, change Root decisions, define transition
legality, revoke, supersede, or invoke adapters.

A changed mandatory dependency makes the old packet non-executable. It does
not mutate packet identity. Renewed authority requires a new Root decision and
new packet ID. A Root-accepted kill-switch condition can be enforced
deterministically without repeating the Root decision.

Missing, stale, replaced, contradictory, duplicate, malformed, wrong-hash, or
wrong-policy dependency evidence fails closed.

## 24. Corridor Pre-Fulfillment Enforcement

Immediately before every mock adapter invocation, the exclusive bounded
Corridor and Effect Firewall path independently verifies:

- canonical packet ID rebuild;
- canonical idempotency-key rebuild;
- owning Root binding;
- source Root decision binding;
- packet structural validity;
- Registry validity;
- legal lifecycle state;
- legal transition history;
- temporal consistency;
- not-before rule;
- present expiry;
- non-revocation;
- non-supersession;
- dependency fingerprint;
- current mandatory dependency validity;
- accepted kill-switch conditions;
- idempotency non-consumption;
- absence of terminal receipt;
- scope containment;
- adapter binding;
- no post-Root reasoning restart;
- no authority expansion;
- no real-effect permission.

Corridor trusts none of:

- caller packet ID;
- caller idempotency key;
- caller `expired`;
- caller `ttl_valid`;
- Registry current state without history validation;
- historical validity as present eligibility;
- stale dependency evidence;
- receipt as permission.

If a check fails:

- adapter calls remain zero;
- no fulfillment receipt is created;
- the blocked attempt does not consume idempotency;
- a deterministic reason code is emitted;
- immutable attempted-fulfillment evidence is appended;
- return-to-Root occurs only under the bound policy;
- real-world effects remain zero.

Corridor remains the sole adapter-handle owner.

## 25. Receipt and Ledger Preservation

Receipt is evidence only. It cannot create, renew, widen, revoke, or supersede
permission; create a packet; alter packet scope; reopen consumed idempotency;
erase history; release shipment; authorize Supplier B; become Root; or create
FinalOutput.

The future G2-A history preserves:

- original Root decision;
- original packet identity;
- original idempotency identity;
- original temporal authority tuple;
- every lifecycle transition;
- every accepted invalidation event;
- every kill-switch event;
- every attempt record;
- every consumption record;
- every receipt;
- exact reason executability ended.

Current state is reconstructable from immutable transition history.
Historical authorization can remain true as a historical fact while current
executability is false.

G2-A remains an in-memory reference-kernel proof. It does not add production
Ledger persistence. Existing Airline ledger and Supplier evidence histories
remain frozen and are used only as read-only compatibility evidence.

## 26. Replay Non-Execution and Temporal Views

Historical verification replay:

- uses original recorded evaluation time;
- reconstructs packet eligibility at that recorded moment;
- verifies transitions and evidence;
- creates no action or authority.

Present eligibility inspection:

- uses newly injected evaluation time;
- may report current expiry or another present non-executable state;
- does not rewrite the historical result;
- creates no action or authority.

Replay never invokes provider, network, Gemini, adapter, or effect; consumes
idempotency; creates receipt; renews, revokes, or supersedes packet; creates
Root decision or ActionCommitPacket; treats historical validity as current
permission; or executes an expired, revoked, superseded, blocked, or consumed
packet.

Closed Package, Anchor, Replay, and evidence artifacts remain frozen.
Lifecycle-aware Replay verification is added only through the bounded G2-A
runtime and test surface.

## 27. Legacy Dictionary Compatibility

Any legacy dictionary packet entering G2-A evaluation passes through one
deterministic compatibility adapter located in the future G2-A runner or the
authorized V02 module.

The adapter:

- rebuilds canonical packet identity;
- rebuilds canonical idempotency identity;
- maps exact Root decision provenance;
- maps exact scope material;
- maps exact dependency material;
- maps exact temporal material;
- rejects missing canonical inputs;
- rejects ambiguous canonical inputs;
- treats old identity strings as compatibility assertions only.

The adapter outputs `ActionCommitPacketV02`. It cannot grant authority,
repair invalid input, infer absent values, infer a latest packet, or preserve a
legacy identity that disagrees with canonical rebuilding.

`hedgehog/action_commit_packet.py` remains byte-frozen. Compatibility does not
create a second packet family.

## 28. Two-Domain Proof Boundary

The future proof uses bounded, public-safe, synthetic Airline-shaped and
Supplier-shaped invalidation inputs. It does not modify or rerun either closed
domain.

Airline-shaped proof:

- a Root-authorized mock intent is queued and pending;
- a hold, price, passenger, or bank-authorization dependency changes;
- the domain input maps to generic dependency or invalidation evidence;
- the same kernel law makes the packet non-executable;
- no booking, payment, ticket, provider call, or real effect occurs.

Supplier-shaped proof:

- a scoped Supplier A mock packet is queued and pending;
- fraud, legal-hold, or cancellation evidence activates a bound condition;
- the domain input maps to the same generic contract;
- Supplier B remains blocked, shipment remains held, and MIXED remains
  preserved;
- no payment, shipment release, provider call, or real effect occurs.

Both use one packet family, Root law, transition family, Registry law,
Corridor law, receipt law, and Replay non-execution law. Domain-specific
authority never enters the kernel.

## 29. Implementation Slice Plan

### SLICE G2-A1 - Canonical Profiles

- implement exact packet and idempotency profiles;
- implement `ABSENT_V01`;
- implement all nested normalization profiles;
- implement canonical time, expiry, logical-time bridge, and dependency
  fingerprint;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A2 - Lifecycle and History

- add the versioned ABI lifecycle profile;
- add the exact transition table in the existing Registry family;
- add immutable transition records;
- derive current Registry state;
- implement retry and consumption laws;
- preserve unknown-transition fail-closed;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A3 - Root-Bound Invalidation

- bind Root authorization;
- record Root revocation and supersession evidence;
- enforce renewal laws;
- validate accepted kill-switch evidence;
- prove Registry creates no authority;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A4 - Corridor Integration

- revalidate immediately before fulfillment;
- block expiry, stale dependency, consumed key, terminal receipt, revocation,
  supersession, and accepted kill switch;
- prove failed eligibility causes zero adapter calls;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A5 - Two-Domain Proof and Replay

- execute Airline-shaped and Supplier-shaped invalidation fixtures;
- preserve one kernel authority law;
- implement lifecycle-aware historical replay;
- implement present eligibility inspection;
- prove immutable history and zero effects.

Owner review and commit boundary follows this slice.

### SLICE G2-A6 - Living Gauntlet and Conformance

- add one real G2-A Living Gauntlet act;
- add one versioned lifecycle conformance category;
- execute exact negative probes;
- preserve all closed Gate-1 acts.

Owner review and commit boundary follows this slice.

### SLICE G2-A7 - Independent Audit and Internal Closure

- freeze committed implementation basis;
- run focused and bounded compatibility tests;
- reserve repository-wide full pytest for owner terminal if required;
- perform independent read-only audit;
- create internal checkpoint;
- update only the AGENTS active checkpoint;
- set next slice G2-B;
- create no public showcase and make no RC2 claim.

Implementation and audit cannot share a commit. An audit failure cannot repair
implementation.

## 30. Focused and Adversarial Test Plan

Future focused command:

```text
PYTHONBREAKPOINT=0 PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_action_commit_packet_lifecycle_g2_a_v01.py
```

Identity tests:

- exact packet field count 20 and exact order;
- exact idempotency field count 10 and exact order;
- unknown, omitted, duplicate, and reordered fields rejected;
- `ABSENT_V01` differs from null, empty string, and omission;
- both transaction and Root-owned intent bind when present;
- one absent identifier is encoded explicitly;
- both policy values bind when present;
- one absent policy value is encoded explicitly;
- forged packet ID and idempotency key rejected;
- exact prefixes and lowercase digest enforced;
- unknown or mismatched profile rejected;
- altered nested normalization rejected;
- valid identity does not prove business truth.

Packet-version and idempotency tests:

- renewal changes packet ID;
- unchanged logical effect preserves key;
- adapter or TTL change changes packet ID but preserves logical-effect key;
- material effect change requires a new key;
- new packet ID cannot bypass consumed key;
- pre-consumption retry preserves packet and key;
- post-consumption retry blocked;
- retry counter cannot change identity;
- lexical latest-name and insertion-order supersession rejected.

Time tests:

- exact integer accepted and bool rejected;
- signed int64 boundaries;
- lower half-open bound;
- one second before expiry;
- exact expiry boundary;
- not-yet-valid block;
- inconsistent issued, expires, and TTL block;
- `expired` and `ttl_valid` assertion mismatch block;
- ambient clock use unreachable;
- unbridged tick block;
- exact bridge conversion;
- malformed bridge block;
- terminal state not overwritten by expiry.

Transition tests:

- each table row positive case;
- each unlisted transition negative case;
- unknown transition block;
- wrong actor block;
- missing Root decision on authority transition;
- expiry, consumption, and stale dependency require no duplicate Root decision;
- Registry cannot create revocation or supersession;
- terminal-to-active block;
- exact non-consuming retry;
- consuming-failure retry block.

History tests:

- rebuilt transition identity;
- altered history, missing link, duplicate, fork, and snapshot rewrite rejected;
- current state reconstructed;
- authorization preserved after revocation, expiry, and supersession;
- receipt preserved after invalidation;
- no deletion helper;
- no mutable history alias.

Corridor tests:

- state, expiry, dependency, idempotency, receipt, revocation, supersession,
  and kill switch rechecked immediately before fulfillment;
- invalid packet produces zero adapter calls and no fulfillment receipt;
- Corridor creates no permission and remains sole adapter owner.

Replay tests:

- recorded time for historical replay;
- injected time for present inspection;
- historical validity grants no current execution;
- expired, revoked, superseded, and consumed packet cannot execute;
- Replay creates no packet, Root decision, receipt, consumption, or effect.

Two-domain tests:

- Airline and Supplier shapes use the generic invalidation contract;
- no domain-specific authority law;
- authority law unchanged between domains;
- Supplier MIXED and Airline evidence geometry preserved;
- real-world effects equal zero.

All malformed-public-validator tests require stable non-empty reason tuples and
no uncaught type, attribute, key, index, regex, normalization, or arithmetic
exception.

## 31. Bounded Compatibility Test Plan

Future bounded compatibility command candidate:

```text
PYTHONBREAKPOINT=0 PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_action_commit_packet_contract_corridor_v02.py \
  tests/test_action_commit_packet_core.py \
  tests/test_mock_connector_sandbox_core.py \
  tests/test_kernel_abi_v01.py \
  tests/test_transition_registry_v01.py \
  tests/test_root_decision_kernel_v01.py \
  tests/test_effect_firewall_v01.py \
  tests/test_kernel_integrity_replay_v01.py \
  tests/test_airline_ticket_purchase_corridor_v01.py \
  tests/test_airline_ticket_purchase_corridor_runtime_v01.py \
  tests/test_living_gauntlet_v01_runner.py \
  tests/test_kernel_conformance_v01_runner.py
```

Compatibility requires zero failures, skips, and xfails in selected tests.
Codex may run focused and bounded compatibility pytest in later implementation
hops. Repository-wide full pytest remains owner-terminal only.

No compatibility test may relax Gate-1 identity, Root, Registry, Firewall,
receipt, or Replay laws. No closed domain evidence is regenerated.

## 32. Living Gauntlet and Conformance Plan

Candidate Living Gauntlet act:

```text
collect_action_packet_lifecycle_gauntlet_act_v01
```

The act executes real G2-A runtime contracts and proves:

```text
packet authorized
packet queued
packet pending
dependency or kill-switch condition changes
packet becomes non-executable
Corridor refuses
prior history remains
zero effects
```

It cannot print a historical PASS label as substitute for execution.

Candidate conformance category:

```text
ActionPacketLifecycleConformance
```

It verifies:

- canonical identity;
- canonical time;
- legal transitions;
- unknown-transition block;
- Root-only authority changes;
- Registry non-authority;
- Corridor freshness enforcement;
- receipt non-authority;
- Replay non-execution;
- cross-domain invariance.

This is a versioned extension inside the existing conformance family. Existing
Gate-1 category IDs and results retain their meanings.

## 33. Independent Audit and Closure Boundary

This preflight authorizes no implementation until:

- owner reviews this exact document;
- owner approves scope;
- owner stages;
- owner commits;
- owner pushes;
- a later explicit implementation prompt is issued.

Codex never commits or pushes.

Future sequence:

```text
preflight commit
-> bounded implementation slices
-> focused tests
-> bounded compatibility tests
-> Living Gauntlet and conformance
-> owner full suite only if required
-> independent audit
-> internal G2-A checkpoint
-> AGENTS active checkpoint update
-> G2-B
```

The independent auditor reads committed implementation and evidence only,
executes no provider/network/Gemini/real effect, and patches no failure. Audit
failure is fail-closed and returns to an implementation owner flow.

The audit and checkpoint paths are created only in their separately authorized
closure pass. G2-A receives no public showcase, Package, Anchor, Replay
publication, or RC2 claim.

## 34. Definition of Done

G2-A cannot close until all conditions hold:

1. `ActionCommitPacketV02` is the sole current G2-A packet family.
2. Packet identity is rebuilt from the exact ordered profile.
3. Idempotency identity is rebuilt from the exact ordered profile.
4. Missing optional values use exact `ABSENT_V01`.
5. Identity fields cannot change under the same profile version.
6. A pending packet can be revoked before mock fulfillment.
7. An expired packet cannot execute.
8. A revoked packet cannot execute.
9. A superseded packet cannot execute.
10. A stale mandatory dependency makes the packet non-executable.
11. Accepted kill-switch evidence is deterministically enforced.
12. Consumed idempotency cannot be reused.
13. A new packet ID cannot bypass consumed logical-effect identity.
14. Unknown transition fails closed.
15. Registry creates no permission.
16. Registry executes no adapter.
17. Corridor remains sole adapter-handle owner.
18. Corridor recomputes executability immediately before fulfillment.
19. Expiry or consumption requires no redundant Root decision.
20. Root is required for creation, renewal, revocation, supersession, and
    materially changed authority.
21. Fulfilled history cannot be deleted or rewritten as never executed.
22. Current state is reconstructable from immutable history.
23. Prior authorization remains auditable after executability becomes false.
24. Receipt remains evidence only.
25. Replay cannot execute or create authority.
26. Airline and Supplier use one authority law.
27. Gate-1 Root, Transition Registry, and Corridor laws remain intact.
28. Focused tests pass.
29. Bounded compatibility tests pass.
30. Living Gauntlet lifecycle act passes.
31. Kernel Conformance lifecycle category passes.
32. Independent audit closes.
33. Real-world effects remain zero.
34. G2-A receives no standalone public showcase.
35. G2-A does not authorize the RC2 claim.
36. G2-B starts only after internal G2-A closure.

## 35. Explicit Non-Claims

G2-A is:

- not production;
- not production persistence;
- not production security;
- not a distributed Registry;
- not production PKI;
- not Root Attestation;
- not real connector readiness;
- not real payment;
- not real booking;
- not real ticket;
- not real shipment release;
- not semantic truth proof;
- not autonomous authority;
- not public release;
- not RC2;
- not Gate-2 closure;
- not G2-B implementation;
- not ActionShortcut enablement;
- not PlanGraph/BSEP work.

## 36. Fail-Closed Conditions

The implementation and review stop without authority, adapter call, receipt,
or effect on:

- path-scope expansion;
- profile-version ambiguity;
- malformed canonical material;
- missing, duplicate, reordered, or unknown profile field;
- sentinel misuse;
- non-NFC identity input after the selected normalization boundary;
- invalid decimal, integer, bool, digest, or prefix;
- packet or idempotency mismatch;
- Root identity or decision mismatch;
- temporal inconsistency or ambient-time dependence;
- unbridged logical time;
- stale, missing, replaced, contradictory, or malformed dependency;
- invalid authority-policy binding;
- illegal or unknown transition;
- wrong transition actor;
- missing Root decision for an authority transition;
- altered, omitted, duplicate, forked, or rewritten history;
- revocation or supersession;
- accepted kill-switch condition;
- consumed idempotency or terminal receipt;
- uncertain effect consumption;
- scope expansion or adapter mismatch;
- post-Root reasoning restart;
- provider, network, Gemini, real connector, or real-effect reachability;
- attempted mutation of frozen paths;
- failed focused, compatibility, Gauntlet, conformance, or audit proof.

An adjacent issue is recorded only as:

```text
OUT_OF_SCOPE_OBSERVATION
```

No adjacent issue widens this preflight.

## 37. Next Slice

The immediate next action is owner and architect review of this exact
preflight, followed by owner-controlled preflight staging, commit, and push.
Implementation remains unauthorized until a later explicit prompt.

After bounded G2-A implementation, tests, Gauntlet, conformance, independent
audit, internal checkpoint, and AGENTS closure complete, the next engineering
slice is G2-B. This document does not start G2-B, close Gate 2, claim RC2, or
authorize public release.
