# Hedgehog OS Gate 2 / G2-A
## ActionPacket Lifecycle and Kill-Switch Preflight v0.1

## 1. Metadata

```yaml
document_id: actionpacket_lifecycle_kill_switch_g2_a_preflight_v01
document_revision: v0.1.5
document_status: PREFLIGHT
preflight_status: READY_FOR_FINAL_INDEPENDENT_CONTRACT_REVIEW
gate_id: gate2_g2a_actionpacket_lifecycle_kill_switch
observed_base_head: 681625c982e46b9adcd101d7c6bd355f4bea18f3
correction_base_head: 20a7ae9a80a480ae60fbef3058d8e3fd6bb760ba
correction_scope: frozen_effect_firewall_vocabulary_permission_transaction_invocation_request_compatibility_closure
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
preflight_commit_authorized: false
public_release_claimed: false
operational_reference_kernel_rc2_claimed: false
next_required_action: final_independent_contract_review_v015_before_commit
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
stable logical-effect intent built and validated
-> exact packet-authorization candidate built
-> correct local Root accepts that candidate
-> Root creates immutable ActionCommitPacketV02 genesis
-> lifecycle runtime validates and activates existing Root authorization
-> ROOT_AUTHORIZED
-> QUEUED
-> PENDING_FULFILLMENT
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

1. Current repository status:
   - `AGENTS.md` active checkpoint;
   - final closed programme checkpoint.
2. Current architecture constitution:
   - Human Passport;
   - invariants;
   - machine manifest;
   - accepted Gate-1 Root, ABI, Transition Registry, Effect Firewall,
     MultiRoot, and Corridor contracts.
3. Owner-approved G2-A canon locks embedded directly in this preflight:
   - identity;
   - idempotency;
   - time and expiry;
   - authority versus deterministic executability.
4. This owner-reviewed preflight for bounded G2-A implementation details.
5. Current implementation and current tests as facts about what already
   exists.
6. Accepted committed evidence, checkpoints, and independent audits.
7. Gate-Based Roadmap v3.1 for order, dependencies, and gate boundaries.
8. Master Roadmap v2.1 for technical depth, proposed types, and detailed DoD.
9. Historical proof and compatibility surfaces as regression evidence only.

This preflight may specialize G2-A details. It may not override the Human
Passport, hard invariants, accepted Gate-1 authority law, or a newer
owner-approved contract.

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

The prospective `RootDecisionCandidateProjectionV01` is only a deterministic
bridge into the frozen Root contracts. The prospective
`ActionPacketEffectFirewallProjectionV01` is only a deterministic bridge into
the existing Effect Firewall. Neither creates a new API, authority family,
effect path, permission path, or capability owner.

Frozen Gate-1 Effect Firewall facts:

```text
EffectFirewallV01 adapter law:
  adapter_id starts with "mock_adapter:"

EffectFirewallV01 action law:
  action_kind starts with "mock_action:"

RootDecisionInput and EffectFirewall permission law:
  permission_required = true
  user_permission_present = true
  permission_scope_valid = true
  permission_ref starts with "permission:"

RootDecisionInput and EffectFirewall transaction law:
  transaction_id is an exact non-empty string

EffectRequestV01 request kind:
  request_kind in {"ExecutionRequest", "ActionCommitPacket"}

EffectFirewallV01 invocation law:
  invocation_id is one exact non-empty string
```

`EffectRequestV01` requires exact `transaction_id`, `target_root_id`,
`root_decision_id`, `selected_candidate_id`, `permission_ref`, `adapter_id`,
`action_kind`, `scope_refs`, `issued_at_tick`, `expires_at_tick`,
`idempotency_key`, and `mock_only = true`.

Existing builders derive `firewall_id`, `request_id`, `capability_id`, and
`decision_id`. Those identities are never caller-selected. G2-A consumes all
of these frozen laws without weakening or bypassing them.

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

`CREATED` is already Root-bound packet genesis. Only the correct local Root
creates packet authority before genesis. `CREATED -> ROOT_AUTHORIZED` is
lifecycle activation of the existing authority, not authority creation.
Registry and lifecycle runtime only validate, register, and activate the
already existing Root-bound object.

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

Pre-Root dependency, revocation, and supersession candidates create no
authority. Their post-Root acceptance bindings record the exact already
validated Root result and create no second decision. Lifecycle transitions
consume the accepted post-Root binding where one is required; they cannot
substitute a pre-Root candidate or synthesize acceptance.

## 9. Canonical ActionCommitPacketV02 Family

`ActionCommitPacketV02` is the sole canonical packet family for G2-A.

`hedgehog/action_commit_packet.py` is a compatibility-only legacy packet
surface. It is not an independent current authority family. No new G2-A
capability may depend directly on its dictionary packet.

The G2-A packet validator must rebuild:

- packet identity;
- idempotency identity;
- stable logical-effect intent identity;
- packet-authorization candidate identity;
- Root decision provenance;
- scope bindings;
- canonical mock adapter/action vocabulary;
- explicit canonical permission context;
- executable transaction continuity;
- dependency bindings;
- temporal authority;
- policy binding;
- predecessor and supersession binding.

Transported `packet_id` and `idempotency_key` values are assertions. They do
not define identity.

An optional transaction field remains representable in canonical identity.
Only a packet with an exact non-empty transaction and validated canonical
permission context can enter lifecycle activation or the effect path.

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
    canonical string accepted by Python full-string matching against this
    exact regex:

    ```text
    (?:0|-?(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.[0-9]*[1-9])?))
    ```

    Validation uses `re.fullmatch` and no search, prefix, suffix, or partial
    match. Accepted examples are `0`, `1`, `-1`, `1.5`, `-1.5`, `0.5`,
    `0.01`, `-0.5`, `10.01`, and `-10.01`. Rejected examples are `+1`, `01`,
    `00.5`, `.5`, `1.`, `1.0`, `0.10`, `-0`, `-0.0`, `1e3`, `NaN`, and
    `Infinity`. A plus sign, exponent, leading integer zero, trailing
    fractional zero, negative zero, binary float, and non-finite value fail
    closed.
25. A profile field addition, deletion, rename, reorder, type change,
    normalization change, sentinel change, prefix change, or domain change
    requires a new profile version, new domain separator, explicit
    compatibility law, and no reinterpretation of old identities.

The frozen repository API shape is:

```text
canonical_json_bytes_v01(value) -> bytes

domain_separated_sha256_hex_v01(
    *,
    domain: str,
    payload: bytes
) -> str
```

Every prospective identity and fingerprint uses exactly:

```text
exact_material_bytes =
  canonical_json_bytes_v01(exact_material)

exact_digest =
  domain_separated_sha256_hex_v01(
    domain="EXACT_DOMAIN_SEPARATOR",
    payload=exact_material_bytes
  )
```

Positional hash-helper invocation, raw structured payloads, dataclass payloads,
non-canonical bytes, direct `hashlib.sha256`, and omission of
`canonical_json_bytes_v01` fail closed. The frozen integrity helper is not
modified.

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
  ["dependency_set_candidate_fingerprint", VALUE],
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
packet_identity_bytes =
  canonical_json_bytes_v01(packet_identity_material_v01)

packet_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_COMMIT_PACKET_ID_V01",
    payload=packet_identity_bytes
  )

packet_id =
  "acp_v02:" + packet_digest
```

Validation rebuilds the value and rejects mismatch. Caller input may transport
`packet_id`; caller input never defines it.

The exact 18-field packet-authorization candidate is the projection of this
20-field packet material with `source_root_decision_id` and
`source_root_decision_hash` excluded. Root selects that candidate first. The
validated Root decision then supplies those two exact fields, after which the
packet ID is rebuilt. A self-consistent packet ID cannot substitute for this
ordered authorization proof.

## 12. Exact Idempotency Identity Profile

Exact constants:

```text
idempotency_identity_profile_id =
  action_idempotency_identity_profile_v01

idempotency_identity_domain_separator =
  HEDGEHOG_ACTION_IDEMPOTENCY_KEY_V01

idempotency_identity_prefix =
  idem:action_v01:
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
idempotency_identity_bytes =
  canonical_json_bytes_v01(idempotency_identity_material_v01)

idempotency_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_IDEMPOTENCY_KEY_V01",
    payload=idempotency_identity_bytes
  )

idempotency_key =
  "idem:action_v01:" + idempotency_digest
```

Validation rebuilds the value and rejects mismatch.

`root_owned_intent_id` is the exact stable
`RootOwnedLogicalEffectIntentV01` identity. It is not the Root-selected
packet-authorization candidate. The idempotency profile binds the logical
effect and therefore remains unchanged under packet-only TTL, adapter,
dependency, policy, retry, or Registry variation.

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

The idempotency prefix belongs to the logical-effect identity profile, not a
packet contract version. A packet-version change cannot change the
logical-effect key.

## 13. Exact Nested Normalization Profiles

The ten normalization profiles in sections 13.1 through 13.10 use the encoding
law in section 10. Sections 13.11 and 13.12 bind those profiles to coherence
and Root authority. Profile ID is the first exact field. Closed record arrays
contain only records defined here.
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
  ["allowed_adapter_ids", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["forbidden_adapter_ids", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["required_approval_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["prohibited_effect_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY]
]
```

`allowed_action_classes`, `allowed_adapter_ids`, and `required_approval_refs`
each have cardinality greater than or equal to 1. Allowed and forbidden action
classes are disjoint. Allowed and forbidden adapter IDs are disjoint.
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
effect_parameters_bytes =
  canonical_json_bytes_v01(material)

effect_parameters_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_EFFECT_PARAMETERS_V01",
    payload=effect_parameters_bytes
  )

normalized_effect_parameters_fingerprint =
  effect_parameters_digest
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

#### 13.5.1 EffectFirewallVocabularyProjectionV01

Exact prospective compatibility profile:

```text
EffectFirewallVocabularyProjectionV01

effect_firewall_vocabulary_projection_profile_id =
  effect_firewall_vocabulary_projection_v01

canonical_token_regex =
  ^[a-z][a-z0-9_]*$

canonical mock adapter ID =
  "mock_adapter:" + canonical_token

canonical mock action ID =
  "mock_action:" + canonical_token
```

The complete ID is NFC, non-empty, case-sensitive, and contains no
whitespace. A G2-A-native packet supplies already canonical
`mock_adapter:` adapter IDs and `mock_action:` action IDs. Native input never
receives an implicit prefix.

Exact closed current Supplier compatibility map:

| legacy kind | exact legacy ID | exact canonical Firewall ID |
|---|---|---|
| adapter | `mock_bank_sandbox` | `mock_adapter:mock_bank_sandbox` |
| adapter | `bank_a_mock` | `mock_adapter:bank_a_mock` |
| action | `mock_supplier_a_payment_intent` | `mock_action:mock_supplier_a_payment_intent` |
| action | `mock_supplier_a_payment_order` | `mock_action:mock_supplier_a_payment_order` |

No other legacy mapping is authorized. Unknown input, already-prefixed legacy
input, and double prefixing fail closed. A real or forbidden adapter/action
cannot become mock merely by prefixing it. These raw values are never mapped:

```text
real_bank
real_supplier_api
real_warehouse_api
real_payment
real_bank_transfer
shipment_release
supplier_b_payment
```

Before mapping, compatibility validation proves:

```text
raw selected adapter in legacy scope.allowed_adapters
raw selected adapter not in legacy scope.forbidden_adapters
raw selected action in legacy scope.allowed_actions
raw selected action not in legacy scope.forbidden_actions
```

Raw legacy identifiers remain compatibility evidence. They are not canonical
Firewall identifiers.

### 13.6 Dependency candidate and packet acceptance binding

#### 13.6.1 DependencySetCandidateV01

Exact pre-Root profile:

```text
DependencySetCandidateV01

dependency_set_candidate_profile_id =
  action_dependency_set_candidate_v01

dependency_set_candidate_domain_separator =
  HEDGEHOG_ACTION_DEPENDENCY_SET_CANDIDATE_V01
```

Exact ordered record material:

```text
dependency_set_candidate_record_v01 = [
  ["dependency_id", EXACT_NON_EMPTY_STRING],
  ["dependency_class", EXACT_NON_EMPTY_STRING],
  ["evidence_ref", EXACT_NON_EMPTY_STRING],
  ["content_sha256", EXACT_LOWERCASE_SHA256],
  ["requirement_class", ONE_OF_MANDATORY_OPTIONAL],
  ["time_envelope_id", VALUE_OR_ABSENT_V01],
  ["freshness_policy_id", VALUE_OR_ABSENT_V01],
  ["source_provenance_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["expected_accepting_local_root_id", EXACT_NON_EMPTY_STRING]
]
```

The record field set is exact and closed. Records are sorted by normalized
`dependency_id` UTF-8 bytes and IDs are unique. Source provenance refs are
non-empty and use the section 10 set-like ordering law. A `MANDATORY` record
requires non-sentinel `time_envelope_id` and `freshness_policy_id`. An
`OPTIONAL` record uses either two non-sentinel values or two sentinel values.
Partial time binding fails closed.

Exact set material and fingerprint:

```text
dependency_set_candidate_material_v01 = [
  ["profile_id", "action_dependency_set_candidate_v01"],
  ["dependency_records",
   EXACT_SORTED_UNIQUE_DEPENDENCY_SET_CANDIDATE_RECORD_ARRAY]
]

dependency_set_candidate_bytes =
  canonical_json_bytes_v01(dependency_set_candidate_material_v01)

dependency_set_candidate_fingerprint =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_DEPENDENCY_SET_CANDIDATE_V01",
    payload=dependency_set_candidate_bytes
  )
```

This is pre-Root evidence material awaiting a Root decision. It is not Root
acceptance and creates no authority.

The candidate material contains none of:

```text
current packet source_root_decision_id
current packet source_root_decision_hash
ROOT_ACCEPTED_FOR_PACKET as a caller assertion
packet_id
post-Root packet acceptance data
```

The packet identity and exact packet-authorization candidate bind
`dependency_set_candidate_fingerprint`. They do not bind the post-Root
acceptance object.

#### 13.6.2 PacketDependencyAcceptanceBindingV01

After the correct local Root accepts the exact packet-authorization candidate,
runtime deterministically derives:

```text
PacketDependencyAcceptanceBindingV01

packet_dependency_acceptance_binding_profile_id =
  packet_dependency_acceptance_binding_v01

packet_dependency_acceptance_binding_domain_separator =
  HEDGEHOG_PACKET_DEPENDENCY_ACCEPTANCE_BINDING_V01

packet_dependency_acceptance_binding_prefix =
  packet_dependency_acceptance_v01:
```

Exact ordered post-Root material:

```text
packet_dependency_acceptance_binding_material_v01 = [
  ["dependency_set_candidate_fingerprint", EXACT_LOWERCASE_SHA256],
  ["root_packet_authorization_candidate_id",
   EXACT_PACKET_AUTHORIZATION_CANDIDATE_ID],
  ["source_root_decision_id", EXACT_SOURCE_ROOT_DECISION_ID],
  ["source_root_decision_hash", EXACT_LOWERCASE_SHA256],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["accepted_status", "ROOT_ACCEPTED_FOR_PACKET"]
]
```

Exact identity:

```text
packet_dependency_acceptance_binding_bytes =
  canonical_json_bytes_v01(
    packet_dependency_acceptance_binding_material_v01
  )

packet_dependency_acceptance_binding_id =
  "packet_dependency_acceptance_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_PACKET_DEPENDENCY_ACCEPTANCE_BINDING_V01",
    payload=packet_dependency_acceptance_binding_bytes
  )
```

The binding is absent from `DependencySetCandidateV01`, absent from
`dependency_set_candidate_fingerprint`, and absent from its own identity
material. It changes no authority and creates no permission. It proves that
the exact local Root accepted the exact dependency candidate for the exact
authorization candidate and packet.

Prior independent evidence-acceptance decisions may remain in
`source_provenance_refs`. They cannot replace the packet's current source Root
authorization decision.

Exact cross-binding:

```text
each dependency_record.expected_accepting_local_root_id
  == packet_dependency_acceptance_binding.owning_local_root_id
  == packet.owning_local_root_id

packet_dependency_acceptance_binding.source_root_decision_id
  == packet.source_root_decision_id

packet_dependency_acceptance_binding.source_root_decision_hash
  == packet.source_root_decision_hash

packet_dependency_acceptance_binding.packet_id
  == packet.packet_id
```

The following fail closed: current source Root decision data or packet ID in
the pre-Root candidate; caller assertion of `ROOT_ACCEPTED_FOR_PACKET`; wrong
dependency fingerprint, authorization candidate, Root decision ID or hash,
owning Root, or packet ID in the post-Root binding; recursive binding
identity; and foreign Root acceptance substitution.

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
  ["supersession_policy", ONE_OF_ROOT_DECISION_ONLY],
  ["logical_effect_namespace", EXACT_NON_EMPTY_STRING],
  ["allowed_logical_effect_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["allowed_business_object_namespaces", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["allowed_corridor_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY]
]
domain_separator = HEDGEHOG_ACTION_AUTHORITY_POLICY_V01
```

`authority_rule_refs` has cardinality greater than or equal to 1.
`kill_switch_condition_refs` may be empty but must be an exact array.
Duplicate, wrong-type, sentinel, or unknown material fails closed.

```text
authority_policy_bytes =
  canonical_json_bytes_v01(material)

authority_policy_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_AUTHORITY_POLICY_V01",
    payload=authority_policy_bytes
  )

authority_policy_fingerprint =
  authority_policy_digest
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

### 13.11 Cross-Profile Coherence v0.1

```text
cross_profile_coherence_profile_id =
  action_packet_cross_profile_coherence_v01
```

The cross-profile validator consumes the exact packet, idempotency,
authority-policy, business-object, adapter-binding, effect-parameters, and
consequential-effect-parameters profile materials, plus the stable logical
intent and packet-authorization candidate. It rebuilds every nested
fingerprint and identity before testing coherence.

Identifier equality:

```text
packet.transaction_id
  == idempotency.transaction_id

packet.root_owned_intent_id
  == idempotency.root_owned_intent_id
  == rebuilt RootOwnedLogicalEffectIntentV01 identity
```

Equality includes exact `ABSENT_V01` placement.

Root ownership equality:

```text
packet.owning_local_root_id
  == idempotency.owning_effect_root_id
  == logical_intent.owning_effect_root_id
  == authority_policy.owning_local_root_id
  == business_object_identity.owning_effect_root_id
```

If the optional authority-policy fingerprint is absent, absence remains
canonical. If authority-policy material is present, Root equality is
mandatory.

Scope equality:

```text
canonical_bytes(packet.normalized_subject_scope)
  == canonical_bytes(idempotency.normalized_subject_scope)

canonical_bytes(packet.normalized_target_scope)
  == canonical_bytes(idempotency.normalized_target_scope)
```

Corridor equality:

```text
packet.corridor_class
  == adapter_binding.corridor_class
```

Policy equality when both values are non-`ABSENT_V01`:

```text
packet.policy_version
  == authority_policy.policy_version
```

The authority-policy fingerprint always rebuilds from the exact supplied
authority-policy material.

Namespace and policy membership:

```text
idempotency.logical_effect_namespace
  == authority_policy.logical_effect_namespace

idempotency.logical_effect_class
  in authority_policy.allowed_logical_effect_classes

business_object_identity.business_object_namespace
  in authority_policy.allowed_business_object_namespaces

packet.corridor_class
  in authority_policy.allowed_corridor_classes
```

Unknown namespace, alias namespace, case variant, display-name substitution,
or caller-selected policy escape fails closed.

For G2-A v0.1, exact domain-neutral effect-class equality is:

```text
packet.effect_class
  == idempotency.logical_effect_class
  == logical_intent.logical_effect_class
  == effect_parameters.effect_class
```

No alias, case conversion, domain synonym, or implementation-specific mapping
is accepted under this profile.

Exact projection constants:

```text
effect_parameter_projection_profile_id =
  action_effect_parameter_projection_v01
```

The consequential-parameter projection is constructed exactly:

1. Begin with the exact `parameter_records` from
   `normalized_consequential_effect_parameters`.
2. If `amount_decimal` is non-`ABSENT_V01`, add exactly:

   ```text
   [
     ["parameter_name", "amount_decimal"],
     ["value_type", "DECIMAL"],
     ["value", exact amount_decimal]
   ]
   ```

3. If `currency_code` is non-`ABSENT_V01`, add exactly:

   ```text
   [
     ["parameter_name", "currency_code"],
     ["value_type", "TEXT"],
     ["value", exact currency_code]
   ]
   ```

4. If `quantity_decimal` is non-`ABSENT_V01`, add exactly:

   ```text
   [
     ["parameter_name", "quantity_decimal"],
     ["value_type", "DECIMAL"],
     ["value", exact quantity_decimal]
   ]
   ```

5. Original `parameter_records` cannot use reserved names
   `amount_decimal`, `currency_code`, or `quantity_decimal`.
6. Sort combined records by normalized `parameter_name` UTF-8 bytes.
7. Reject duplicate parameter names.
8. Use the shared exact effect class.
9. Build the exact section 13.4 material.
10. Rebuild `normalized_effect_parameters_fingerprint`.

Required equality:

```text
projected_effect_parameters_material_v01 =
  exact projected section 13.4 material

projected_effect_parameters_bytes =
  canonical_json_bytes_v01(
    projected_effect_parameters_material_v01
  )

projected_effect_parameters_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_EFFECT_PARAMETERS_V01",
    payload=projected_effect_parameters_bytes
  )

packet.normalized_effect_parameters_fingerprint
  == projected_effect_parameters_digest
```

Identifier, Root, scope, Corridor, policy, effect-class, fingerprint, or
parameter-projection mismatch fails closed with a stable reason code.

Generic permission, adapter, effect, and policy coherence is mandatory:

```text
packet.adapter_binding.adapter_id
  in packet.normalized_permission_scope.allowed_adapter_ids

packet.adapter_binding.adapter_id
  not in packet.normalized_permission_scope.forbidden_adapter_ids

effect_request.action_kind
  in packet.normalized_permission_scope.allowed_action_classes

effect_request.action_kind
  not in packet.normalized_permission_scope.forbidden_action_classes

packet.effect_class
  not in packet.normalized_permission_scope.prohibited_effect_classes

packet.effect_class
  in authority_policy.allowed_logical_effect_classes

packet.adapter_binding.corridor_class
  in authority_policy.allowed_corridor_classes

business_object.namespace
  in authority_policy.allowed_business_object_namespaces

firewall.permission_ref
  in packet.normalized_permission_scope.required_approval_refs
```

For every executable packet:

```text
len(packet.normalized_permission_scope.allowed_adapter_ids) > 0
len(packet.normalized_permission_scope.allowed_action_classes) > 0
len(packet.normalized_permission_scope.required_approval_refs) > 0
```

Subject, target, adapter, action, effect, business-object, and Corridor scope
must each remain contained in both the Root-approved
packet-authorization-candidate scope and the packet permission/policy scope.
The two validated projections must describe the same bounded operation. A
legacy compatibility projection that passes Supplier-specific validation does
not prove the generic profile valid. Missing membership, prohibited
membership, empty required set, or divergence between Root-approved candidate
scope and packet permission/policy scope fails closed.

Exact permission-reference separation:

```text
canonical_permission_ref =
  exact pre-Root permission-context reference used to construct
  root_decision_input.permission_state.permission_ref

type(canonical_permission_ref) is str
canonical_permission_ref is non-empty
canonical_permission_ref starts with "permission:"
canonical_permission_ref
  == root_decision_input.permission_state.permission_ref

packet.normalized_permission_scope.required_approval_refs
  == [canonical_permission_ref]

firewall.permission_ref
  == effect_request.permission_ref
  == canonical_permission_ref
```

The array uses the section 10 set-like canonical ordering law. The
compatibility adapter never invents, derives, renames, prefixes, or repairs
`canonical_permission_ref`. A legacy packet without an explicit validated
canonical permission context cannot enter G2-A lifecycle activation.

`packet.human_approval_ref` remains evidence-only provenance. It creates no
permission, packet, or Root decision; cannot satisfy the Effect Firewall
permission law; and cannot be converted from a `human_approval:` reference
into a `permission:` reference.

The packet and idempotency identity profiles retain their optional
`transaction_id` positions. The executable path is stricter:

```text
packet.transaction_id = ABSENT_V01
  -> RootDecisionCandidateProjectionV01 forbidden
  -> lifecycle activation forbidden
  -> ROOT_AUTHORIZED forbidden
  -> QUEUED forbidden
  -> PENDING_FULFILLMENT forbidden
  -> EffectFirewallV01 construction forbidden
  -> EffectRequestV01 construction forbidden
  -> private capability forbidden
  -> adapter invocation forbidden
```

For every lifecycle-activated packet:

```text
packet.transaction_id is an exact non-empty string

packet.transaction_id
  == root_review.transaction_id
  == post_vv.transaction_id
  == gt.transaction_id
  == root_decision_input.transaction_id
  == root_decision_result.transaction_id
  == firewall.transaction_id
  == effect_request.transaction_id
```

A legacy packet lacking a canonical transaction ID requires explicit
transaction context from the surrounding accepted runtime. The compatibility
adapter cannot infer it from invoice number, payment-slot reference, creditor
reference, packet display name, source Root-decision-ref text, creation time,
or Registry order. Missing or mismatched transaction context fails closed.
For a lifecycle-activated packet, `packet_genesis_valid` includes this exact
transaction binding.

### 13.12 Stable Logical Intent and Packet Authorization v0.1

#### 13.12.1 RootOwnedLogicalEffectIntentV01

Exact constants:

```text
RootOwnedLogicalEffectIntentV01

logical_intent_profile_id =
  root_owned_logical_effect_intent_v01

logical_intent_domain_separator =
  HEDGEHOG_ROOT_OWNED_LOGICAL_EFFECT_INTENT_V01

logical_intent_prefix =
  root_logical_intent_v01:
```

Exact ordered material:

```text
root_owned_logical_effect_intent_material_v01 = [
  ["logical_intent_profile_version", "v0.1"],
  ["owning_effect_root_id", EXACT_NON_EMPTY_STRING],
  ["transaction_id", VALUE_OR_ABSENT_V01],
  ["logical_effect_class", EXACT_NON_EMPTY_STRING],
  ["normalized_subject_scope", EXACT_SUBJECT_SCOPE_MATERIAL],
  ["normalized_target_scope", EXACT_TARGET_SCOPE_MATERIAL],
  ["normalized_business_object_identity",
   EXACT_BUSINESS_OBJECT_IDENTITY_MATERIAL],
  ["normalized_consequential_effect_parameters",
   EXACT_CONSEQUENTIAL_EFFECT_PARAMETERS_MATERIAL],
  ["logical_effect_namespace", EXACT_NON_EMPTY_STRING]
]
```

`len(root_owned_logical_effect_intent_material_v01) == 9`.

Exact identity:

```text
logical_intent_bytes =
  canonical_json_bytes_v01(
    root_owned_logical_effect_intent_material_v01
  )

root_owned_intent_id =
  "root_logical_intent_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ROOT_OWNED_LOGICAL_EFFECT_INTENT_V01",
    payload=logical_intent_bytes
  )
```

This exact ID occupies the existing `root_owned_intent_id` positions in
`packet_identity_material_v01` and `idempotency_identity_material_v01`. It is
a stable canonical logical-effect identity and is not authority by itself.

It remains unchanged when only packet contract version, TTL, issue time,
expiry time, adapter implementation or version, retry attempt, dependency
snapshot, policy version, or Registry state changes. It changes when the
protected logical consequential effect changes.

Its nine fields are byte-equal to the corresponding idempotency material and
nested materials:

```text
logical_intent.logical_intent_profile_version
  == idempotency.idempotency_contract_version
  == "v0.1"

logical_intent.owning_effect_root_id
  == idempotency.owning_effect_root_id

logical_intent.transaction_id
  == idempotency.transaction_id

logical_intent.logical_effect_class
  == idempotency.logical_effect_class

canonical_bytes(logical_intent.normalized_subject_scope)
  == canonical_bytes(idempotency.normalized_subject_scope)

canonical_bytes(logical_intent.normalized_target_scope)
  == canonical_bytes(idempotency.normalized_target_scope)

canonical_bytes(logical_intent.normalized_business_object_identity)
  == canonical_bytes(idempotency.normalized_business_object_identity)

canonical_bytes(logical_intent.normalized_consequential_effect_parameters)
  == canonical_bytes(
       idempotency.normalized_consequential_effect_parameters
     )

logical_intent.logical_effect_namespace
  == idempotency.logical_effect_namespace
```

#### 13.12.2 RootBoundPacketAuthorizationCandidateV01

Exact constants:

```text
RootBoundPacketAuthorizationCandidateV01

packet_authorization_candidate_profile_id =
  root_bound_packet_authorization_candidate_v01

packet_authorization_candidate_domain_separator =
  HEDGEHOG_ROOT_BOUND_PACKET_AUTHORIZATION_CANDIDATE_V01

packet_authorization_candidate_prefix =
  root_packet_authorization_v01:
```

Exact ordered material:

```text
packet_authorization_candidate_material_v01 = [
  ["packet_contract_family", "ActionCommitPacketV02"],
  ["packet_contract_version", "v0.2"],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["transaction_id", VALUE_OR_ABSENT_V01],
  ["root_owned_intent_id", EXACT_CANONICAL_ROOT_LOGICAL_INTENT_ID],
  ["effect_class", EXACT_NON_EMPTY_STRING],
  ["normalized_subject_scope", EXACT_SUBJECT_SCOPE_MATERIAL],
  ["normalized_target_scope", EXACT_TARGET_SCOPE_MATERIAL],
  ["normalized_permission_scope", EXACT_PERMISSION_SCOPE_MATERIAL],
  ["normalized_effect_parameters_fingerprint", EXACT_LOWERCASE_SHA256],
  ["corridor_class", EXACT_NON_EMPTY_STRING],
  ["adapter_binding", EXACT_ADAPTER_BINDING_MATERIAL],
  ["dependency_set_candidate_fingerprint", EXACT_LOWERCASE_SHA256],
  ["temporal_authority_fingerprint", EXACT_LOWERCASE_SHA256],
  ["policy_version", VALUE_OR_ABSENT_V01],
  ["authority_policy_fingerprint", EXACT_LOWERCASE_SHA256],
  ["predecessor_packet_id", VALUE_OR_ABSENT_V01],
  ["supersession_reason_class", VALUE_OR_ABSENT_V01]
]
```

`len(packet_authorization_candidate_material_v01) == 18`.

Exact identity:

```text
packet_authorization_candidate_bytes =
  canonical_json_bytes_v01(
    packet_authorization_candidate_material_v01
  )

root_packet_authorization_candidate_id =
  "root_packet_authorization_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ROOT_BOUND_PACKET_AUTHORIZATION_CANDIDATE_V01",
    payload=packet_authorization_candidate_bytes
  )
```

The correct local Root accepts this exact authorization candidate. The packet
validator rebuilds it from packet fields other than source Root-decision ID
and hash, proves that Root selected it, rebuilds source decision ID and hash,
and then rebuilds packet ID.

Exact distinction:

```text
root_owned_intent_id
  = stable logical-effect identity

root_packet_authorization_candidate_id
  = exact Root-selected packet authority version

packet_id
  = exact immutable packet object including source Root decision
```

A TTL, adapter, dependency, or policy change changes the authorization
candidate, source Root decision, and packet ID, but preserves
`root_owned_intent_id` and `idempotency_key` when the logical effect is
unchanged. A material effect change changes every required logical-effect
identity.

For every executable G2-A-aware packet, `root_owned_intent_id` and
`authority_policy_fingerprint` are non-`ABSENT_V01` and rebuild exactly.

#### 13.12.3 Exact Frozen Root Validator Binding

`RootDecisionCandidateProjectionV01` is the sole deterministic projection
adapter from the three G2-A candidate kinds into the frozen Root path:

```text
packet authorization candidate
revocation candidate
supersession candidate
```

It is not a new Root API, Root kernel, authority object, permission object,
Post V&V replacement, GT replacement, or Root Review replacement. It changes
no frozen Root object after construction.

For one candidate evaluation, exact equality is required:

```text
projected_candidate_id
  == Root Review normalized-claims candidate ID
  == Post V&V validated_candidate_ids exact member
  == GT candidate_ids exact selected member
  == GT selected_candidate_id
  == RootDecisionInput candidate-set exact member
  == RootDecisionResult.selected_candidate_id
```

The candidate ID is absent from:

```text
Post V&V rejected_candidate_ids
GT rejected candidate set
GT blocked candidate set
every foreign transaction context
every foreign Root context
every unrelated decision input
every other candidate identity position
```

The exact `RootDecisionInputV01` contains the same Root Review, Post V&V, GT,
transaction, target Root, policy, permission, temporal, conflict, and prior
state context subsequently validated by the frozen Root validator.

The candidate validator consumes the exact frozen
`RootDecisionKernelV01`, `RootDecisionInputV01`, `RootDecisionResultV01`,
`validate_root_decision_result_v01`, and
`root_decision_result_to_plain_dict_v01` contracts and proves:

```text
validate_root_decision_result_v01(
  kernel=root_decision_kernel,
  decision_input=root_decision_input,
  result=root_decision_result
) == ()
root_decision_result.decision_input_id
  == root_decision_input.decision_input_id
root_decision_result.decision == "ACCEPT"
root_decision_result.reason_code == "validated_candidate_accepted"
root_decision_result.root_commit_created is true
root_decision_result.permission_created is false
root_decision_result.final_output_created is false
root_decision_result.effect_requested is false
root_decision_result.selected_candidate_id == projected_candidate_id
```

For packet authorization specifically:

```text
projected_candidate_id == root_packet_authorization_candidate_id
root_decision_result.target_root_id == packet.owning_local_root_id
packet.transaction_id is an exact non-empty string
packet.transaction_id == root_decision_input.transaction_id
packet.transaction_id == root_decision_result.transaction_id
root_decision_input.permission_state.permission_ref
  == canonical_permission_ref
packet.source_root_decision_id == root_decision_result.decision_id
packet.source_root_decision_ref == root_decision_result.decision_id
packet.root_boundary_ref == root_decision_result.decision_input_id
```

The validator must consume the exact kernel, exact decision input, and exact
result together. A structurally valid Root result from another decision input,
candidate set, transaction, target Root, Root Review packet, Post V&V context,
GT context, policy context, permission context, temporal context, conflict
context, or prior Root context fails closed.

Exact source-decision projection and content hash:

```text
source_root_decision_projection =
  root_decision_result_to_plain_dict_v01(root_decision_result)

source_root_decision_bytes =
  canonical_json_bytes_v01(source_root_decision_projection)

source_root_decision_hash =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_SOURCE_ROOT_DECISION_V01",
    payload=source_root_decision_bytes
  )
```

Transported source decision ID and hash must equal rebuilt values. A
self-consistent packet hash without a valid Root result fails closed. Registry,
Corridor, domain adapter, receipt, and Replay cannot synthesize a substitute
Root decision.

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
temporal_authority_bytes =
  canonical_json_bytes_v01(temporal_authority_material_v01)

temporal_authority_fingerprint =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_TEMPORAL_AUTHORITY_V01",
    payload=temporal_authority_bytes
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

### 14.1 Legacy Decimal Compatibility Projection

Canonical G2-A output remains the exact section 10 decimal profile.
Compatibility input uses exact Python full-string matching against:

```text
legacy_plain_decimal_input_regex =
  -?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?
```

Input is an exact string. Binary float, exponent, plus sign, leading integer
zero, malformed decimal, and non-finite input fail closed. Parsing uses exact
decimal arithmetic. Normalization removes trailing fractional zeros, then
removes the decimal point if no fractional digit remains. Negative zero fails
closed. The result must satisfy section 10.

Exact examples:

```text
"1250.00" -> "1250"
"0.50" -> "0.5"
"0.0100" -> "0.01"
```

### 14.2 PacketTTL String Compatibility Projection

Accepted timestamp forms:

```text
YYYY-MM-DDTHH:MM:SSZ
YYYY-MM-DDTHH:MM:SS+00:00
```

Exact full-string grammar:

```text
[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|\+00:00)
```

The parser uses full-string matching, validates the proleptic Gregorian
calendar for years `0001` through `9999`, validates hours `00` through `23`,
minutes and seconds `00` through `59`, and accepts only UTC `Z` or `+00:00`.
Naive time, fractional seconds, leap second, nonzero offset, malformed
calendar date, locale dependence, and ambient clock fail closed.

Compatibility conversion:

```text
PacketTTL.created_at
  -> issued_at_utc signed int64 UTC epoch seconds

PacketTTL.expires_at
  -> expires_at_utc signed int64 UTC epoch seconds

PacketTTL.ttl_seconds
  -> exact positive integer with bool rejected
```

Epoch conversion uses seconds from `1970-01-01T00:00:00Z` under the validated
UTC Gregorian representation. It then requires:

```text
expires_at_utc == issued_at_utc + ttl_seconds
```

Current `ttl_valid` and `expired` remain compatibility assertions.
`ttl_valid` must equal canonical temporal-consistency validity. `expired` must
equal the result of comparing injected `evaluation_time` with
`expires_at_utc`. Mismatch fails closed.

Scenario time and old sandbox timestamps use this same parser and convert to
epoch seconds before comparison. Lexical timestamp comparison is forbidden.

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
logical_time_bridge_bytes =
  canonical_json_bytes_v01(logical_time_bridge_material_v01)

bridge_id =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_LOGICAL_TIME_BRIDGE_V01",
    payload=logical_time_bridge_bytes
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

Exact activation semantics:

- `CREATED` is valid Root-created and Root-bound packet genesis that is
  non-executable and has no lifecycle reservation;
- `ROOT_AUTHORIZED` is that same authority object after lifecycle runtime
  registration and atomic idempotency acquisition;
- lifecycle activation requires the exact non-empty transaction continuity and
  validated canonical permission context in section 13.11;
- activation creates no authority object and no new Root decision;
- the source Root authorization bound into genesis remains unchanged.

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

Canonical machine rule shape:

```text
transition_rule_record_v01 = [
  ["transition_rule_id", EXACT_REGISTERED_RULE_ID],
  ["source_state", EXACT_LIFECYCLE_STATE],
  ["target_state", EXACT_LIFECYCLE_STATE],
  ["transition_class_code", EXACT_TRANSITION_CLASS_CODE],
  ["permitted_component_code", EXACT_COMPONENT_CODE],
  ["root_decision_requirement_code",
   EXACT_ROOT_DECISION_REQUIREMENT_CODE],
  ["required_evidence_codes",
   EXACT_ORDERED_UNIQUE_EVIDENCE_CODE_ARRAY],
  ["effect_consumption_class",
   ONE_OF_NOT_CONSUMED_CONSUMED_UNCERTAIN],
  ["adapter_invocation_relation_code",
   EXACT_ADAPTER_INVOCATION_RELATION_CODE],
  ["terminal_target", EXACT_BOOL],
  ["reason_code", EXACT_REASON_CODE],
  ["fail_closed_reason_codes",
   EXACT_ORDERED_UNIQUE_REASON_CODE_ARRAY]
]
```

Rule IDs, component codes, evidence codes, reason codes, and fail-closed reason
codes are NFC, non-empty, selected from closed vocabularies, and match
`^[a-z][a-z0-9_]*$`. They contain no spaces, punctuation, sentence prose, or
display-only wording. Lifecycle states, transition-class enums,
Root-decision-requirement enums, and effect-consumption enums are exact closed
uppercase symbolic tokens.

Exact Root-decision requirement codes:

```text
NONE
EXISTING_SOURCE_AUTHORIZATION
NEW_ROOT_REVOCATION_DECISION
NEW_ROOT_SUPERSESSION_DECISION
```

Canonical 26-rule machine table:

| transition_rule_id | source_state | target_state | transition_class_code | permitted_component_code | root_decision_requirement_code | required_evidence_codes | effect_consumption_class | adapter_invocation_relation_code | terminal_target | reason_code | fail_closed_reason_codes |
|---|---|---|---|---|---|---|---|---|---:|---|---|
| g2a_t01_activate_root_authorization | CREATED | ROOT_AUTHORIZED | LIFECYCLE_ACTIVATION | lifecycle_runtime | EXISTING_SOURCE_AUTHORIZATION | [packet_genesis_valid,source_root_authorization_valid,idempotency_acquisition_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | false | root_authorization_activated | [packet_genesis_invalid,source_root_authorization_invalid,wrong_owning_root,idempotency_acquisition_invalid] |
| g2a_t02_queue | ROOT_AUTHORIZED | QUEUED | DETERMINISTIC | lifecycle_runtime | NONE | [transition_history_valid,temporal_authority_valid,mandatory_dependencies_current,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | false | packet_queued | [packet_non_executable,transition_history_invalid,temporal_authority_invalid,mandatory_dependency_invalid,idempotency_reservation_invalid] |
| g2a_t03_pending | QUEUED | PENDING_FULFILLMENT | DETERMINISTIC | exclusive_corridor | NONE | [immediate_prefulfillment_validation_pass,transition_history_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | false | pending_fulfillment | [current_eligibility_invalid,transition_history_invalid,idempotency_reservation_invalid] |
| g2a_t04_fulfill_mock | PENDING_FULFILLMENT | FULFILLED_MOCK | DETERMINISTIC_CONSUMING | exclusive_corridor | NONE | [mock_adapter_result_valid,effect_consumption_evidence_valid,idempotency_reservation_owned] | CONSUMED | CORRIDOR_INVOCATION_CONSUMED | false | fulfilled_mock | [adapter_call_failed,effect_consumption_evidence_missing,current_eligibility_changed,idempotency_reservation_invalid] |
| g2a_t05_receipt | FULFILLED_MOCK | RECEIPT_RECEIVED | DETERMINISTIC_CONSUMING | receipt_observer | NONE | [terminal_receipt_valid,fulfillment_consumption_evidence_valid] | CONSUMED | POST_INVOCATION_RECEIPT_OBSERVATION | true | receipt_received | [receipt_invalid,packet_binding_mismatch,idempotency_binding_mismatch,receipt_authority_claimed,consumption_evidence_missing] |
| g2a_t06_created_block | CREATED | BLOCKED | DETERMINISTIC | lifecycle_runtime | NONE | [packet_genesis_valid,blocking_evidence_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_blocked | [packet_genesis_invalid,blocking_evidence_missing,authority_expansion_detected] |
| g2a_t07_authorized_block | ROOT_AUTHORIZED | BLOCKED | DETERMINISTIC | lifecycle_runtime | NONE | [blocking_evidence_valid,authority_policy_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_blocked | [blocking_evidence_missing,authority_expansion_detected,authority_policy_invalid,idempotency_reservation_invalid] |
| g2a_t08_queued_block | QUEUED | BLOCKED | DETERMINISTIC | lifecycle_runtime | NONE | [blocking_evidence_valid,authority_policy_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_blocked | [blocking_evidence_missing,authority_expansion_detected,authority_policy_invalid,idempotency_reservation_invalid] |
| g2a_t09_pending_block | PENDING_FULFILLMENT | BLOCKED | DETERMINISTIC | exclusive_corridor | NONE | [immediate_eligibility_failure_valid,adapter_not_called,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_blocked | [adapter_already_called,blocking_evidence_missing,idempotency_reservation_invalid] |
| g2a_t10_failed_block | FAILED | BLOCKED | DETERMINISTIC | lifecycle_runtime | NONE | [failed_non_consuming_provenance_valid,retry_ineligibility_evidence_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_blocked | [failed_provenance_invalid,retry_ineligibility_evidence_missing,authority_expansion_detected,idempotency_reservation_invalid] |
| g2a_t11_created_expire | CREATED | EXPIRED | DETERMINISTIC | temporal_validator | NONE | [packet_genesis_valid,temporal_authority_valid,evaluation_time_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_expired | [packet_genesis_invalid,temporal_authority_invalid,evaluation_time_invalid,prior_terminal_state] |
| g2a_t12_authorized_expire | ROOT_AUTHORIZED | EXPIRED | DETERMINISTIC | temporal_validator | NONE | [temporal_authority_valid,evaluation_time_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_expired | [temporal_authority_invalid,evaluation_time_invalid,prior_terminal_state,idempotency_reservation_invalid] |
| g2a_t13_queued_expire | QUEUED | EXPIRED | DETERMINISTIC | temporal_validator | NONE | [temporal_authority_valid,evaluation_time_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_expired | [temporal_authority_invalid,evaluation_time_invalid,prior_terminal_state,idempotency_reservation_invalid] |
| g2a_t14_pending_expire | PENDING_FULFILLMENT | EXPIRED | DETERMINISTIC | exclusive_corridor | NONE | [immediate_temporal_validation_pass,evaluation_time_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_expired | [adapter_already_called,temporal_authority_invalid,evaluation_time_invalid,idempotency_reservation_invalid] |
| g2a_t15_failed_expire | FAILED | EXPIRED | DETERMINISTIC | temporal_validator | NONE | [failed_non_consuming_provenance_valid,temporal_authority_valid,evaluation_time_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_expired | [failed_provenance_invalid,temporal_authority_invalid,evaluation_time_invalid,prior_terminal_state,idempotency_reservation_invalid] |
| g2a_t16_authorized_revoke | ROOT_AUTHORIZED | REVOKED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_REVOCATION_DECISION | [accepted_revocation_binding_valid,source_authorization_binding_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_revoked | [foreign_root,accepted_revocation_binding_invalid,source_authorization_mismatch,idempotency_reservation_invalid] |
| g2a_t17_queued_revoke | QUEUED | REVOKED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_REVOCATION_DECISION | [accepted_revocation_binding_valid,source_authorization_binding_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_revoked | [foreign_root,accepted_revocation_binding_invalid,source_authorization_mismatch,idempotency_reservation_invalid] |
| g2a_t18_pending_revoke | PENDING_FULFILLMENT | REVOKED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_REVOCATION_DECISION | [accepted_revocation_binding_valid,source_authorization_binding_valid,adapter_not_called,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_revoked | [adapter_already_called,foreign_root,accepted_revocation_binding_invalid,source_authorization_mismatch,idempotency_reservation_invalid] |
| g2a_t19_failed_revoke | FAILED | REVOKED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_REVOCATION_DECISION | [failed_non_consuming_provenance_valid,accepted_revocation_binding_valid,source_authorization_binding_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_revoked | [failed_provenance_invalid,foreign_root,accepted_revocation_binding_invalid,source_authorization_mismatch,idempotency_reservation_invalid] |
| g2a_t20_authorized_supersede | ROOT_AUTHORIZED | SUPERSEDED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_SUPERSESSION_DECISION | [successor_packet_valid,accepted_supersession_binding_valid,predecessor_binding_valid,idempotency_transfer_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_superseded | [successor_packet_missing,accepted_supersession_binding_invalid,predecessor_binding_mismatch,foreign_root,idempotency_transfer_invalid] |
| g2a_t21_queued_supersede | QUEUED | SUPERSEDED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_SUPERSESSION_DECISION | [successor_packet_valid,accepted_supersession_binding_valid,predecessor_binding_valid,idempotency_transfer_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_superseded | [successor_packet_missing,accepted_supersession_binding_invalid,predecessor_binding_mismatch,foreign_root,idempotency_transfer_invalid] |
| g2a_t22_pending_supersede | PENDING_FULFILLMENT | SUPERSEDED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_SUPERSESSION_DECISION | [successor_packet_valid,accepted_supersession_binding_valid,predecessor_binding_valid,adapter_not_called,idempotency_transfer_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_superseded | [adapter_already_called,successor_packet_missing,accepted_supersession_binding_invalid,predecessor_binding_mismatch,foreign_root,idempotency_transfer_invalid] |
| g2a_t23_failed_supersede | FAILED | SUPERSEDED | AUTHORITY_CHANGE | owning_local_root | NEW_ROOT_SUPERSESSION_DECISION | [failed_non_consuming_provenance_valid,successor_packet_valid,accepted_supersession_binding_valid,predecessor_binding_valid,idempotency_transfer_valid] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | true | packet_superseded | [failed_provenance_invalid,successor_packet_missing,accepted_supersession_binding_invalid,predecessor_binding_mismatch,foreign_root,idempotency_transfer_invalid] |
| g2a_t24_nonconsuming_failure | PENDING_FULFILLMENT | FAILED | DETERMINISTIC | exclusive_corridor | NONE | [adapter_invocation_evidence_valid,effect_nonconsumption_evidence_valid,idempotency_reservation_owned,latest_disposition_event_binding_valid] | NOT_CONSUMED | CORRIDOR_INVOCATION_NONCONSUMING | false | fulfillment_failed_nonconsuming | [adapter_not_called,effect_consumed,effect_outcome_uncertain,failure_evidence_missing,idempotency_reservation_invalid,latest_disposition_event_binding_invalid,disposition_history_changed] |
| g2a_t25_retry | FAILED | QUEUED | DETERMINISTIC | lifecycle_runtime | NONE | [failed_non_consuming_provenance_valid,retry_policy_valid,current_eligibility_valid,idempotency_reservation_owned] | NOT_CONSUMED | NO_ADAPTER_INVOCATION | false | nonconsuming_retry_queued | [failed_provenance_invalid,packet_binding_mismatch,idempotency_binding_mismatch,terminal_evidence_present,mandatory_dependency_invalid,retry_policy_invalid,idempotency_reservation_invalid] |
| g2a_t26_uncertain_adapter_outcome | PENDING_FULFILLMENT | FAILED | DETERMINISTIC_UNCERTAIN | exclusive_corridor | NONE | [adapter_invocation_evidence_valid,effect_outcome_unresolved,idempotency_reservation_owned] | UNCERTAIN | CORRIDOR_INVOCATION_UNCERTAIN | true | fulfillment_failed_consumption_uncertain | [adapter_not_called,effect_consumed,effect_non_consumption_proven,execution_attempt_evidence_missing,idempotency_binding_missing,transition_event_identity_invalid] |

The exact requirement mapping is:

- `g2a_t01_activate_root_authorization` uses
  `EXISTING_SOURCE_AUTHORIZATION`;
- `g2a_t16_*` through `g2a_t19_*` use
  `NEW_ROOT_REVOCATION_DECISION`;
- `g2a_t20_*` through `g2a_t23_*` use
  `NEW_ROOT_SUPERSESSION_DECISION`;
- every other rule uses `NONE`.

Human explanations may be stored in a separate map keyed by
`transition_rule_id`. Explanation text is non-identity metadata and is absent
from `transition_registry_material_v01`; punctuation or prose changes cannot
change `transition_registry_id`.

Exact adapter invocation relation vocabulary and mapping:

```text
NO_ADAPTER_INVOCATION
CORRIDOR_INVOCATION_CONSUMED
CORRIDOR_INVOCATION_NONCONSUMING
CORRIDOR_INVOCATION_UNCERTAIN
POST_INVOCATION_RECEIPT_OBSERVATION

g2a_t04_fulfill_mock
  -> CORRIDOR_INVOCATION_CONSUMED

g2a_t24_nonconsuming_failure
  -> CORRIDOR_INVOCATION_NONCONSUMING

g2a_t26_uncertain_adapter_outcome
  -> CORRIDOR_INVOCATION_UNCERTAIN

g2a_t05_receipt
  -> POST_INVOCATION_RECEIPT_OBSERVATION

every other transition rule
  -> NO_ADAPTER_INVOCATION
```

Exact Transition Registry identity:

```text
transition_registry_profile_id =
  action_packet_lifecycle_registry_profile_v01

transition_registry_domain_separator =
  HEDGEHOG_ACTION_PACKET_TRANSITION_REGISTRY_V01

transition_registry_prefix =
  acptr_v01:

transition_registry_material_v01 = [
  ["registry_profile_version", "v0.1"],
  ["lifecycle_profile_id", "action_packet_lifecycle_profile_v01"],
  ["ordered_transition_rules", EXACT_ORDERED_26_RULE_RECORDS]
]
```

Each ordered rule record contains every exact table column:

```text
transition_rule_id
source_state
target_state
transition_class_code
permitted_component_code
root_decision_requirement_code
required_evidence_codes
effect_consumption_class
adapter_invocation_relation_code
terminal_target
reason_code
fail_closed_reason_codes
```

Free-form English prose is absent from the Registry identity. The exact
ordered 26 machine rule records are the only rule material hashed.

Exact construction:

```text
transition_registry_bytes =
  canonical_json_bytes_v01(transition_registry_material_v01)

transition_registry_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_PACKET_TRANSITION_REGISTRY_V01",
    payload=transition_registry_bytes
  )

transition_registry_id =
  "acptr_v01:" + transition_registry_digest
```

A rule-table mutation changes Registry identity. A Registry profile label with
altered rules fails closed. Historical Gate-1 `TransitionRegistryV01`
identities remain unchanged. This is a versioned extension inside the same
Registry family, not a competing Registry.

This table contains exactly 26 registered transition rules. Each `g2a_t01_*`
through `g2a_t26_*` value is a `transition_rule_id`. A rule ID identifies
Registry policy; it is never a concrete transition-event identity.

Packet authority creation is performed by the correct local Root before packet
genesis. Lifecycle activation
`CREATED -> ROOT_AUTHORIZED` validates, records, and activates existing
authority; it creates no new Root decision or authority object. Authority
changes for renewal, revocation, and supersession require the correct local
Root. A Root-bound kill-switch is enforced as `BLOCKED`; it does not let
Registry create a `REVOKED` event.

Exact `root_decision_ref` law:

```text
EXISTING_SOURCE_AUTHORIZATION
  -> exact source packet authorization decision ID

NEW_ROOT_REVOCATION_DECISION
  -> exact new revocation Root decision ID

NEW_ROOT_SUPERSESSION_DECISION
  -> exact new successor or supersession Root decision ID

NONE
  -> ABSENT_V01
```

Root-bound policy evidence for deterministic transitions is carried through
the packet policy fingerprint and event evidence refs, not by pretending a new
Root decision occurred.

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
- `FAILED` reached through `g2a_t24_nonconsuming_failure` is non-terminal and
  potentially retryable only under the exact retry law.
- `FAILED` reached through `g2a_t26_uncertain_adapter_outcome` is terminal and
  permanently non-executable. It cannot return to `QUEUED`.
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
- immutable idempotency-disposition-event history;
- derived current lifecycle state;
- derived executability;
- idempotency reservation, ownership, and disposition;
- terminal receipt binding;
- dependency status;
- authority evidence.

The canonical validated `ActionCommitPacketV02` artifact is immutable packet
genesis. Before Registry activation:

```text
derived lifecycle state = CREATED
executable = false
idempotency disposition = UNCLAIMED
```

`CREATED` means a structurally valid, immutable, Root-created, Root-bound
`ActionCommitPacketV02` genesis whose packet identity, stable logical intent,
packet-authorization candidate, source Root decision, policy, dependency,
temporal, and compatibility bindings all validate. The packet has not yet been
activated, is non-executable, and has acquired no lifecycle idempotency
reservation. No caller-created snapshot may assert `CREATED`. A packet without
valid genesis cannot enter a lifecycle state.

The first event is
`g2a_t01_activate_root_authorization: CREATED -> ROOT_AUTHORIZED` and uses
`previous_transition_event_id = ABSENT_V01`. It references the existing source
Root authorization decision and creates no new Root decision or authority
object. Activation and the exact `RESERVE` disposition event are one atomic
in-memory Registry operation.

`ROOT_AUTHORIZED` means the already Root-bound genesis has been registered and
activated for lifecycle progression. Its source Root authorization remains
unchanged. Activation acquires either a new idempotency reservation or an
exact validated transfer and does not itself make the packet executable
without all Corridor checks.

Current state is reconstructed from immutable canonical packet genesis,
ordered validated transition events, ordered validated
idempotency-disposition events, and accepted invalidation or reconciliation
evidence. Event history alone does not reconstruct `CREATED`.

Transition and disposition journals are distinct append-only histories. A
lifecycle event does not imply a disposition event. Exact t24 appends only its
validated lifecycle event and proves byte equality of disposition history
before and after; the existing latest disposition event continues to establish
the same `RESERVED` owner.

Exact transition-event identity constants:

```text
transition_event_identity_profile_id =
  action_packet_transition_identity_profile_v01

transition_event_identity_domain_separator =
  HEDGEHOG_ACTION_PACKET_TRANSITION_V01

transition_event_identity_prefix =
  acpt_v01:
```

Every rule-required evidence item is represented by one exact typed binding:

```text
TransitionEvidenceBindingV01

transition_evidence_binding_profile_id =
  action_transition_evidence_binding_v01

transition_evidence_binding_domain_separator =
  HEDGEHOG_ACTION_TRANSITION_EVIDENCE_BINDING_V01

transition_evidence_binding_prefix =
  acpte_v01:

transition_evidence_binding_material_v01 = [
  ["evidence_code", EXACT_REGISTERED_EVIDENCE_CODE],
  ["evidence_ref", EXACT_NON_EMPTY_STRING],
  ["evidence_sha256", EXACT_LOWERCASE_SHA256],
  ["validator_profile_id", EXACT_NON_EMPTY_STRING],
  ["validation_status", "PASS"]
]
```

Exact identity:

```text
transition_evidence_binding_bytes =
  canonical_json_bytes_v01(
    transition_evidence_binding_material_v01
  )

transition_evidence_binding_id =
  "acpte_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_TRANSITION_EVIDENCE_BINDING_V01",
    payload=transition_evidence_binding_bytes
  )
```

For every transition event:

```text
set(evidence_binding.evidence_code)
  == set(selected_rule.required_evidence_codes)

count(evidence_binding for each required evidence_code)
  == 1
```

The identity-bearing collection contains exact
`transition_evidence_binding_material_v01` values in the selected rule's
`required_evidence_codes` order. Missing, duplicate, unknown, mismatched,
unvalidated, reordered, wrong-hash, or wrong-validator bindings fail closed.
Free-form evidence refs may be retained only as supplementary non-identity
audit metadata outside transition-event identity. A free-form ref cannot
satisfy a Registry-required evidence code.

Exact closed transition-event material:

```text
transition_event_identity_material_v01 = [
  ["transition_profile_version", "v0.1"],
  ["transition_registry_id", EXACT_CANONICAL_TRANSITION_REGISTRY_ID],
  ["transition_rule_id", EXACT_REGISTERED_TRANSITION_RULE_ID],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["idempotency_key", EXACT_CANONICAL_IDEMPOTENCY_KEY],
  ["previous_transition_event_id", VALUE_OR_ABSENT_V01],
  ["source_state", EXACT_LIFECYCLE_STATE],
  ["target_state", EXACT_LIFECYCLE_STATE],
  ["transition_class_code", EXACT_TRANSITION_CLASS_CODE],
  ["performed_by_component",
   EXACT_COMPONENT_CODE],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["root_decision_ref", VALUE_OR_ABSENT_V01],
  ["transition_evidence_bindings",
   EXACT_RULE_ORDERED_TRANSITION_EVIDENCE_BINDING_MATERIAL_ARRAY],
  ["reason_code", EXACT_TABLE_REASON_CODE],
  ["dependency_set_candidate_fingerprint", EXACT_LOWERCASE_SHA256],
  ["temporal_authority_fingerprint", EXACT_LOWERCASE_SHA256],
  ["evaluation_time", EXACT_INT64],
  ["evaluation_time_source", EXACT_NON_EMPTY_STRING],
  ["evaluation_context_id", EXACT_NON_EMPTY_STRING],
  ["execution_attempt_id", VALUE_OR_ABSENT_V01],
  ["effect_consumption_class", ONE_OF_NOT_CONSUMED_CONSUMED_UNCERTAIN],
  ["receipt_ref", VALUE_OR_ABSENT_V01]
]
```

`len(transition_event_identity_material_v01) == 22`.

Exact event construction:

```text
transition_event_bytes =
  canonical_json_bytes_v01(transition_event_identity_material_v01)

transition_event_digest =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_PACKET_TRANSITION_V01",
    payload=transition_event_bytes
  )

transition_event_id =
  "acpt_v01:" + transition_event_digest
```

Exact execution-attempt identity:

```text
execution_attempt_identity_profile_id =
  action_execution_attempt_identity_v01

execution_attempt_identity_domain_separator =
  HEDGEHOG_ACTION_EXECUTION_ATTEMPT_ID_V01

execution_attempt_identity_prefix =
  execution_attempt_v01:

execution_attempt_identity_material_v01 = [
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["idempotency_key", EXACT_CANONICAL_IDEMPOTENCY_KEY],
  ["attempt_ordinal", EXACT_POSITIVE_INT],
  ["evaluation_context_id", EXACT_NON_EMPTY_STRING]
]

execution_attempt_identity_bytes =
  canonical_json_bytes_v01(
    execution_attempt_identity_material_v01
  )

execution_attempt_id =
  "execution_attempt_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_EXECUTION_ATTEMPT_ID_V01",
    payload=execution_attempt_identity_bytes
  )
```

`attempt_ordinal` is one plus the count of preceding validated
`g2a_t03_pending` events for the same packet ID and idempotency key in
immutable history. It is reconstructed from history. Caller-provided ordinal,
mutable counter, external counter, Registry insertion order, wall clock, and
timestamp ordering are forbidden.

Exact rule-by-rule execution-attempt and receipt presence matrix:

| transition rule set | execution_attempt_id | receipt_ref |
|---|---|---|
| `g2a_t03_pending` | newly rebuilt exact `execution_attempt_id` | `ABSENT_V01` |
| `g2a_t04_fulfill_mock` | exact ID created by the immediately preceding validated `g2a_t03_pending` event | `ABSENT_V01` |
| `g2a_t24_nonconsuming_failure` | exact ID created by the immediately preceding validated `g2a_t03_pending` event | `ABSENT_V01` |
| `g2a_t26_uncertain_adapter_outcome` | exact ID created by the immediately preceding validated `g2a_t03_pending` event | `ABSENT_V01` |
| `g2a_t05_receipt` | exact ID bound by the validated `g2a_t04_fulfill_mock` event | exact canonical receipt reference |
| every other registered transition rule | `ABSENT_V01` | `ABSENT_V01` |

One `g2a_t03_pending` event creates one attempt identity. Exactly one of
`g2a_t04_fulfill_mock`, `g2a_t24_nonconsuming_failure`, or
`g2a_t26_uncertain_adapter_outcome` reuses it. A subsequent
`g2a_t05_receipt` reuses the same attempt identity and binds the exact receipt.
Forged attempt ID, changed ordinal, changed evaluation context, outcome-event
attempt mismatch, receipt-event attempt mismatch, missing receipt on t05, or
attempt/receipt presence on an unrelated transition fails closed.

Validation proves:

- `transition_registry_id` equals the exact Registry identity used to validate
  the event;
- `transition_rule_id` exists in the selected Registry profile;
- source state equals the selected rule;
- target state equals the selected rule;
- `transition_class_code` equals the selected rule's
  `transition_class_code`;
- `performed_by_component` equals the selected rule's
  `permitted_component_code`;
- reason code equals the selected rule;
- `root_decision_ref` satisfies the selected rule's
  `root_decision_requirement_code` exactly;
- `transition_evidence_bindings` have exact set equality, one binding per
  code, and exact order against the selected rule's
  `required_evidence_codes`;
- a validation failure uses only the selected rule's closed
  `fail_closed_reason_codes`;
- observed adapter-invocation evidence agrees with the selected rule's
  `adapter_invocation_relation_code`;
- terminal and execution-attempt/receipt presence laws agree with the selected
  rule.

The first event uses
`previous_transition_event_id = ABSENT_V01`. Every later event binds the exact
previous event ID. `g2a_t01_activate_root_authorization` binds the source
packet authorization decision ID. Revocation and supersession events bind
their exact new Root decision IDs. Rules with requirement code `NONE` use
`root_decision_ref = ABSENT_V01`; Root-bound deterministic policy evidence
travels through packet policy and typed transition evidence bindings.
`CONSUMED` requires
`FULFILLED_MOCK` or `RECEIPT_RECEIVED`. `UNCERTAIN` requires
`g2a_t26_uncertain_adapter_outcome`, terminal `FAILED`, exact execution-attempt
evidence, and permanent non-executability.

History is append-only. Deletion, rewriting, arbitrary snapshot replacement,
caller-selected event ID, unknown rule ID, rule/event mismatch, component
substitution, missing previous event, duplicate event, omitted event, reordered
history, and history fork fail closed. Current state is reconstructed from
validated immutable packet genesis plus validated ordered history. No mutable
history alias may escape.

Reconciliation evidence after an `UNCERTAIN` event is append-only,
non-state-reopening evidence. It cannot mutate the uncertain event, requeue the
packet, reopen the idempotency key, create authority, fabricate a receipt, or
invoke an adapter.

Exact `FAILED` provenance:

```text
FAILED_NON_CONSUMING =
  FAILED whose latest event rule is g2a_t24_nonconsuming_failure

FAILED_UNCERTAIN_TERMINAL =
  FAILED whose latest event rule is g2a_t26_uncertain_adapter_outcome
```

Only `FAILED_NON_CONSUMING` may source `g2a_t10_failed_block`,
`g2a_t15_failed_expire`, `g2a_t19_failed_revoke`,
`g2a_t23_failed_supersede`, or `g2a_t25_retry`.
`FAILED_UNCERTAIN_TERMINAL` permits no later lifecycle transition. Only
append-only reconciliation observations may follow, and those observations do
not change lifecycle state, idempotency disposition, authority, or
executability.

Registry is not Root, DRS, business truth, permission, packet authority,
receipt creator, adapter invoker, payment executor, or shipment releaser.

## 20. Root Authorization, Renewal, Revocation and Supersession

Root authorization binds:

- exact owning local Root ID;
- exact stable logical-effect intent ID;
- exact Root-selected packet-authorization candidate ID;
- exact source Root decision ID and hash;
- exact packet identity profile;
- exact scope and effect;
- exact dependency-set candidate fingerprint;
- exact post-Root packet dependency acceptance binding;
- exact temporal authority;
- exact authority policy;
- exact idempotency identity.

Every authorization, revocation, and supersession binding satisfies section
13.12 against the frozen Root API. Source decision ID, source decision hash,
Root boundary reference, target Root, transaction, selected candidate, prior
decision, and Root commit are rebuilt and validated. No lifecycle component
substitutes a synthetic Root result.

Only Root creates packet authority before immutable packet genesis. Lifecycle
runtime activation validates and records that authority and acquires the
idempotency reservation atomically. It creates no authority object and no new
Root decision.

Renewal requires a new local Root decision and new `packet_id`. The successor
binds its predecessor and `"RENEWAL"`. Unchanged logical effect preserves the
same `root_owned_intent_id` and `idempotency_key`. Its changed TTL, adapter,
dependency, or policy changes the packet-authorization candidate and packet
ID. Renewal cannot reopen consumed or uncertain-closed idempotency or widen
scope without explicit new authority.

### RevocationCandidateV01

Exact pre-Root candidate:

```text
RevocationCandidateV01

revocation_candidate_profile_id =
  action_revocation_candidate_v01

revocation_candidate_domain_separator =
  HEDGEHOG_ACTION_REVOCATION_CANDIDATE_V01

revocation_candidate_prefix =
  revocation_candidate_v01:

revocation_candidate_material_v01 = [
  ["candidate_profile_id", "action_revocation_candidate_v01"],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["source_authorization_decision_id",
   EXACT_SOURCE_ROOT_DECISION_ID],
  ["idempotency_key", EXACT_CANONICAL_IDEMPOTENCY_KEY],
  ["revocation_reason_class", EXACT_NON_EMPTY_STRING],
  ["evidence_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["evidence_hashes", EXACT_CORRESPONDING_LOWERCASE_SHA256_ARRAY],
  ["evaluation_time", EXACT_INT64],
  ["policy_fingerprint", EXACT_LOWERCASE_SHA256]
]
```

Evidence refs sort by normalized UTF-8 bytes. Evidence hashes have equal
cardinality and move in lockstep with their corresponding refs.

```text
revocation_candidate_bytes =
  canonical_json_bytes_v01(revocation_candidate_material_v01)

revocation_candidate_id =
  "revocation_candidate_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_REVOCATION_CANDIDATE_V01",
    payload=revocation_candidate_bytes
  )
```

The candidate excludes the new revocation Root decision ID, its hash, and the
accepted revocation binding identity. Root selects
`revocation_candidate_id` through `RootDecisionCandidateProjectionV01`.
The validated result satisfies:

```text
root_decision_result.selected_candidate_id == revocation_candidate_id
root_decision_result.target_root_id == packet.owning_local_root_id
root_decision_result.prior_decision_id == packet.source_root_decision_id
```

### SupersessionCandidateV01

Exact pre-Root candidate:

```text
SupersessionCandidateV01

supersession_candidate_profile_id =
  action_supersession_candidate_v01

supersession_candidate_domain_separator =
  HEDGEHOG_ACTION_SUPERSESSION_CANDIDATE_V01

supersession_candidate_prefix =
  supersession_candidate_v01:

supersession_candidate_material_v01 = [
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["predecessor_packet_id", EXACT_CANONICAL_PACKET_ID],
  ["successor_packet_authorization_candidate_id",
   EXACT_PACKET_AUTHORIZATION_CANDIDATE_ID],
  ["stable_logical_intent_id", EXACT_CANONICAL_ROOT_LOGICAL_INTENT_ID],
  ["idempotency_key", EXACT_CANONICAL_IDEMPOTENCY_KEY],
  ["supersession_reason_class", EXACT_NON_EMPTY_STRING],
  ["policy_fingerprint", EXACT_LOWERCASE_SHA256]
]
```

```text
supersession_candidate_bytes =
  canonical_json_bytes_v01(supersession_candidate_material_v01)

supersession_candidate_id =
  "supersession_candidate_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_SUPERSESSION_CANDIDATE_V01",
    payload=supersession_candidate_bytes
  )
```

The candidate excludes the new supersession Root decision ID, its hash, and
the accepted supersession binding identity. Root selects
`supersession_candidate_id` through `RootDecisionCandidateProjectionV01`.
The validated result satisfies:

```text
root_decision_result.selected_candidate_id == supersession_candidate_id
root_decision_result.target_root_id == predecessor_packet.owning_local_root_id
root_decision_result.prior_decision_id
  == predecessor_packet.source_root_decision_id
```

### AcceptedRevocationBindingV01

After Root accepts the exact revocation candidate, runtime derives:

```text
AcceptedRevocationBindingV01

accepted_revocation_binding_material_v01 = [
  ["revocation_candidate_id", EXACT_REVOCATION_CANDIDATE_ID],
  ["revocation_root_decision_id", EXACT_ROOT_DECISION_ID],
  ["revocation_root_decision_hash", EXACT_LOWERCASE_SHA256],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["prior_authorization_decision_id", EXACT_SOURCE_ROOT_DECISION_ID]
]
```

```text
accepted_revocation_binding_bytes =
  canonical_json_bytes_v01(accepted_revocation_binding_material_v01)

accepted_revocation_binding_id =
  "accepted_revocation_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACCEPTED_REVOCATION_BINDING_V01",
    payload=accepted_revocation_binding_bytes
  )
```

The binding is absent from the selected candidate. It creates no candidate and
has no recursive identity. A `REVOKED` transition references the accepted
binding through exact validated transition evidence, never the pre-Root
candidate alone.

### AcceptedSupersessionBindingV01

After Root accepts the exact supersession candidate, runtime derives:

```text
AcceptedSupersessionBindingV01

accepted_supersession_binding_material_v01 = [
  ["supersession_candidate_id", EXACT_SUPERSESSION_CANDIDATE_ID],
  ["supersession_root_decision_id", EXACT_ROOT_DECISION_ID],
  ["supersession_root_decision_hash", EXACT_LOWERCASE_SHA256],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["predecessor_packet_id", EXACT_CANONICAL_PACKET_ID],
  ["prior_authorization_decision_id", EXACT_SOURCE_ROOT_DECISION_ID]
]
```

```text
accepted_supersession_binding_bytes =
  canonical_json_bytes_v01(
    accepted_supersession_binding_material_v01
  )

accepted_supersession_binding_id =
  "accepted_supersession_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACCEPTED_SUPERSESSION_BINDING_V01",
    payload=accepted_supersession_binding_bytes
  )
```

The binding proves that `SupersessionCandidateV01` already bound the exact
successor packet-authorization candidate. It is absent from the pre-Root
candidate. A `SUPERSEDED` transition references the accepted binding through
exact validated transition evidence.

Revocation keeps packet ID and idempotency key unchanged. Supersession requires
a new Root decision, new packet ID, exact predecessor binding, and immutable
predecessor history. An unchanged logical effect preserves logical-intent ID
and idempotency key.

A selected candidate containing its own future Root decision, an accepted
binding with wrong candidate, decision ID or hash, owning Root, packet or
predecessor, or prior authorization decision, foreign Root substitution, or a
transition that cites only a pre-Root candidate fails closed. Supersession is
never inferred from latest name, lexical order, timestamp order, or insertion
order.

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
- terminal uncertain adapter outcome;
- scope or adapter mismatch.

Registry records exact state and evidence. Corridor independently recomputes
present eligibility. A `BLOCKED` verdict under a Root-bound kill-switch does
not pretend Registry revoked authority. Historical authorization remains
auditable while present executability is false.

An uncertain post-adapter outcome is neither `CONSUMED` nor `NOT_CONSUMED`.
It enters terminal `FAILED` through
`g2a_t26_uncertain_adapter_outcome`, permanently closes the packet and
idempotency key, and requires no redundant Root decision to enforce
non-executability. No assumption is made that the effect happened or did not
happen.

## 22. Retry and Terminal Consumption

```text
packet_id = exact Root authorization object/version
idempotency_key = exact logical consequential effect protected from duplicate
                  fulfillment
```

Exact canonical idempotency dispositions:

```text
UNCLAIMED
RESERVED
CONSUMED
UNCERTAIN_CLOSED
```

Absence of all disposition-event history for an idempotency key means
`UNCLAIMED`. `UNCLAIMED` is not serialized as an active Registry entry. A
lifecycle transition that appends no new disposition event does not imply
`UNCLAIMED`; the existing validated journal remains controlling.

Prospective append-only profile:

```text
IdempotencyDispositionEventV01

idempotency_disposition_event_profile_id =
  action_idempotency_disposition_event_v01

idempotency_disposition_event_domain_separator =
  HEDGEHOG_ACTION_IDEMPOTENCY_DISPOSITION_EVENT_V01

idempotency_disposition_event_prefix =
  idem_event_v01:
```

Exact ordered material:

```text
idempotency_disposition_event_material_v01 = [
  ["event_profile_version", "v0.1"],
  ["idempotency_key", EXACT_CANONICAL_IDEMPOTENCY_KEY],
  ["event_class", EXACT_DISPOSITION_EVENT_CLASS],
  ["from_disposition", EXACT_DISPOSITION_CLASS],
  ["to_disposition", EXACT_DISPOSITION_CLASS],
  ["from_owner_packet_id", VALUE_OR_ABSENT_V01],
  ["to_owner_packet_id", VALUE_OR_ABSENT_V01],
  ["previous_disposition_event_id", VALUE_OR_ABSENT_V01],
  ["cause_transition_event_ids",
   EXACT_ORDERED_UNIQUE_TRANSITION_EVENT_ID_ARRAY],
  ["root_decision_ref", VALUE_OR_ABSENT_V01],
  ["predecessor_packet_id", VALUE_OR_ABSENT_V01],
  ["successor_packet_id", VALUE_OR_ABSENT_V01],
  ["evidence_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["evaluation_time", EXACT_INT64],
  ["evaluation_time_source", EXACT_NON_EMPTY_STRING],
  ["evaluation_context_id", EXACT_NON_EMPTY_STRING]
]
```

`len(idempotency_disposition_event_material_v01) == 16`.

Exact event classes:

```text
RESERVE
TRANSFER_RENEWAL
TRANSFER_SUPERSESSION
CONSUME
UNCERTAIN_CLOSE
RECEIPT_CONFIRM
```

Exact identity:

```text
idempotency_disposition_event_bytes =
  canonical_json_bytes_v01(
    idempotency_disposition_event_material_v01
  )

idempotency_disposition_event_id =
  "idem_event_v01:" +
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_IDEMPOTENCY_DISPOSITION_EVENT_V01",
    payload=idempotency_disposition_event_bytes
  )
```

### Renewal and reservation-disposition matrix

Branch A covers a predecessor that remained `UNCLAIMED`, including
`CREATED -> EXPIRED`. It never completed lifecycle activation and never
acquired the key. A same-logical-effect successor with a new validated Root
authorization uses `RESERVE: UNCLAIMED -> RESERVED`.
`TRANSFER_RENEWAL` and `TRANSFER_SUPERSESSION` are forbidden because the
predecessor never owned the reservation. The successor `RESERVE` event binds
the exact predecessor relationship without asserting ownership transfer.

Branch B covers an unconsumed predecessor that owns `RESERVED` in exactly one
of these states or provenance classes:

```text
ROOT_AUTHORIZED
QUEUED
PENDING_FULFILLMENT before adapter invocation
FAILED_NON_CONSUMING
EXPIRED after lifecycle activation
BLOCKED after lifecycle activation
REVOKED after lifecycle activation
```

A same-logical-effect successor acquires that key only through
`TRANSFER_RENEWAL` for exact reason `RENEWAL` or
`TRANSFER_SUPERSESSION` for an exact non-`RENEWAL` reason. The transfer binds
old and new owner, new Root decision, predecessor and successor packet IDs,
same key, same stable logical-effect ID, transfer-authorizing policy, previous
disposition event, and required lifecycle events. If no successor exists, the
terminal predecessor retains reservation ownership. No release operation
exists.

Exact lifecycle/disposition matrix:

```text
EXACT_RECONSTRUCTED_PREDECESSOR_DISPOSITION
  = UNCLAIMED when no disposition-event history exists
  = exact latest validated to_disposition otherwise

EXACT_RECONSTRUCTED_PREDECESSOR_OWNER_VALUE
  = ABSENT_V01 when disposition is UNCLAIMED
  = exact latest validated to_owner_packet_id otherwise

EXACT_RECONSTRUCTED_OWNER_FOR_EACH_DISTINCT_KEY
  = exact independently reconstructed owner value for each canonical key
```

| predecessor lifecycle state or provenance | predecessor disposition | successor present | successor logical effect | new Root decision | permitted disposition operation | required atomic lifecycle bundle | predecessor executability | successor executability | resulting reservation owner | fail-closed reason |
|---|---|---:|---|---:|---|---|---|---|---|---|
| `CREATED -> EXPIRED` before activation | `UNCLAIMED` | yes | same | yes | `RESERVE` | validated predecessor expiry evidence + successor `g2a_t01_activate_root_authorization` + successor `RESERVE` | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `unclaimed_predecessor_transfer_forbidden` |
| `ROOT_AUTHORIZED` | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor `g2a_t20_authorized_supersede` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `atomic_reserved_transfer_invalid` |
| `QUEUED` | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor `g2a_t21_queued_supersede` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `atomic_reserved_transfer_invalid` |
| `PENDING_FULFILLMENT` before adapter invocation | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor `g2a_t22_pending_supersede` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `atomic_reserved_transfer_invalid` |
| `FAILED_NON_CONSUMING` | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor `g2a_t23_failed_supersede` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `atomic_reserved_transfer_invalid` |
| `EXPIRED` after activation | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor remains `EXPIRED` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `terminal_predecessor_transfer_invalid` |
| `BLOCKED` after activation | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor remains `BLOCKED` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `terminal_predecessor_transfer_invalid` |
| `REVOKED` after activation | `RESERVED` owned by predecessor | yes | same | yes | `TRANSFER_RENEWAL` for `RENEWAL`; `TRANSFER_SUPERSESSION` for exact non-`RENEWAL` reason | predecessor remains `REVOKED` + successor activation + exact transfer | non-executable | non-executable until queued, pending, and all Corridor checks pass | successor packet | `terminal_predecessor_transfer_invalid` |
| `SUPERSEDED` after completed transfer | `RESERVED` owned by existing successor | yes | same | yes | no operation from superseded predecessor | no lifecycle or disposition event accepted from superseded predecessor | non-executable | existing successor state unchanged | existing successor packet | `superseded_predecessor_not_reservation_owner` |
| `FULFILLED_MOCK` | `CONSUMED` | yes | same | yes | no operation | no successor activation for this key | non-executable | non-executable for this key | fulfilled predecessor packet | `consumed_key_permanently_closed` |
| `RECEIPT_RECEIVED` | `CONSUMED` | yes | same | yes | no operation | no successor activation for this key | non-executable | non-executable for this key | receipt-bound predecessor packet | `consumed_key_permanently_closed` |
| `FAILED_UNCERTAIN_TERMINAL` | `UNCERTAIN_CLOSED` | yes | same | yes | no operation | reconciliation observations only | non-executable | non-executable for this key | uncertain predecessor packet | `uncertain_key_permanently_closed` |
| exact set `{EXPIRED after activation, BLOCKED after activation, REVOKED after activation}` | `RESERVED` owned by predecessor | no | same | no | no operation | no new lifecycle bundle | non-executable | no successor | predecessor packet | `successor_absent_reservation_retained` |
| exact set `{CREATED, ROOT_AUTHORIZED, QUEUED, PENDING_FULFILLMENT, FAILED_NON_CONSUMING, EXPIRED, BLOCKED, REVOKED}` | `EXACT_RECONSTRUCTED_PREDECESSOR_DISPOSITION` | yes | different | yes | `RESERVE` on successor's distinct canonical idempotency key | successor activation + successor `RESERVE` on distinct key | `EXACT_VALIDATED_PREDECESSOR_STATE` | non-executable until queued, pending, and all Corridor checks pass | `EXACT_RECONSTRUCTED_OWNER_FOR_EACH_DISTINCT_KEY` | `logical_effect_identity_alias_forbidden` |
| exact set `{CREATED, ROOT_AUTHORIZED, QUEUED, PENDING_FULFILLMENT, FAILED_NON_CONSUMING, EXPIRED, BLOCKED, REVOKED}` | `EXACT_RECONSTRUCTED_PREDECESSOR_DISPOSITION` | yes | same | no | `NONE` | `[]` | `EXACT_VALIDATED_PREDECESSOR_STATE` | non-executable | `EXACT_RECONSTRUCTED_PREDECESSOR_OWNER_VALUE` | `new_root_decision_missing` |

`CONSUMED`, `UNCERTAIN_CLOSED`, `FULFILLED_MOCK`, and
`RECEIPT_RECEIVED` permit no transfer, renewal, retry, reuse, or reservation
reacquisition. A packet already `SUPERSEDED` cannot transfer the key again.
A later Root decision or new packet ID cannot bypass either permanent
disposition.

### Complete IdempotencyDispositionEventV01 field matrix

Every row below fixes all 16 identity fields. `EXACT_SORTED_ARRAY(...)` means
the section 10 normalized UTF-8-byte sort over the exact listed canonical
evidence-binding IDs. The `evidence_refs` field therefore contains the exact
canonical identities of the validated evidence bindings named in that row,
not free-form display refs.

Initial packet `RESERVE`:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_SUCCESSOR_CANONICAL_IDEMPOTENCY_KEY
event_class = RESERVE
from_disposition = UNCLAIMED
to_disposition = RESERVED
from_owner_packet_id = ABSENT_V01
to_owner_packet_id = EXACT_ACTIVATED_PACKET_ID
previous_disposition_event_id = ABSENT_V01
cause_transition_event_ids = [EXACT_SUCCESSOR_ACTIVATION_TRANSITION_EVENT_ID]
root_decision_ref = EXACT_SUCCESSOR_SOURCE_ROOT_AUTHORIZATION_DECISION_ID
predecessor_packet_id = ABSENT_V01
successor_packet_id = ABSENT_V01
evidence_refs = EXACT_SORTED_ARRAY(PACKET_GENESIS_EVIDENCE_ID,SOURCE_ROOT_AUTHORIZATION_EVIDENCE_ID,ACTIVATION_EVIDENCE_ID)
evaluation_time = EXACT_ACTIVATION_EVALUATION_TIME
evaluation_time_source = EXACT_ACTIVATION_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_ACTIVATION_EVALUATION_CONTEXT_ID
```

Branch-A successor `RESERVE` from an `UNCLAIMED` predecessor:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_SUCCESSOR_CANONICAL_IDEMPOTENCY_KEY
event_class = RESERVE
from_disposition = UNCLAIMED
to_disposition = RESERVED
from_owner_packet_id = ABSENT_V01
to_owner_packet_id = EXACT_ACTIVATED_SUCCESSOR_PACKET_ID
previous_disposition_event_id = ABSENT_V01
cause_transition_event_ids = [EXACT_PREDECESSOR_EXPIRY_TRANSITION_EVENT_ID,EXACT_SUCCESSOR_ACTIVATION_TRANSITION_EVENT_ID]
root_decision_ref = EXACT_SUCCESSOR_SOURCE_ROOT_AUTHORIZATION_DECISION_ID
predecessor_packet_id = EXACT_UNCLAIMED_PREDECESSOR_PACKET_ID
successor_packet_id = EXACT_ACTIVATED_SUCCESSOR_PACKET_ID
evidence_refs = EXACT_SORTED_ARRAY(PREDECESSOR_RELATIONSHIP_EVIDENCE_ID,PREDECESSOR_EXPIRY_EVIDENCE_ID,SUCCESSOR_AUTHORIZATION_EVIDENCE_ID)
evaluation_time = EXACT_SUCCESSOR_ACTIVATION_EVALUATION_TIME
evaluation_time_source = EXACT_SUCCESSOR_ACTIVATION_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_SUCCESSOR_ACTIVATION_EVALUATION_CONTEXT_ID
```

Active-predecessor `TRANSFER_RENEWAL`:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_SHARED_CANONICAL_IDEMPOTENCY_KEY
event_class = TRANSFER_RENEWAL
from_disposition = RESERVED
to_disposition = RESERVED
from_owner_packet_id = EXACT_PREDECESSOR_PACKET_ID
to_owner_packet_id = EXACT_SUCCESSOR_PACKET_ID
previous_disposition_event_id = EXACT_PREDECESSOR_LATEST_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_PREDECESSOR_SUPERSEDED_TRANSITION_EVENT_ID,EXACT_SUCCESSOR_ACTIVATION_TRANSITION_EVENT_ID]
root_decision_ref = EXACT_SUCCESSOR_SOURCE_ROOT_AUTHORIZATION_DECISION_ID
predecessor_packet_id = EXACT_PREDECESSOR_PACKET_ID
successor_packet_id = EXACT_SUCCESSOR_PACKET_ID
evidence_refs = EXACT_SORTED_ARRAY(RENEWAL_POLICY_EVIDENCE_ID,SHARED_LOGICAL_INTENT_EVIDENCE_ID,SUCCESSOR_AUTHORIZATION_EVIDENCE_ID)
evaluation_time = EXACT_TRANSFER_EVALUATION_TIME
evaluation_time_source = EXACT_TRANSFER_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_TRANSFER_EVALUATION_CONTEXT_ID
```

Terminal-predecessor `TRANSFER_RENEWAL`:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_SHARED_CANONICAL_IDEMPOTENCY_KEY
event_class = TRANSFER_RENEWAL
from_disposition = RESERVED
to_disposition = RESERVED
from_owner_packet_id = EXACT_TERMINAL_PREDECESSOR_PACKET_ID
to_owner_packet_id = EXACT_SUCCESSOR_PACKET_ID
previous_disposition_event_id = EXACT_PREDECESSOR_LATEST_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_PREDECESSOR_TERMINAL_TRANSITION_EVENT_ID,EXACT_SUCCESSOR_ACTIVATION_TRANSITION_EVENT_ID]
root_decision_ref = EXACT_SUCCESSOR_SOURCE_ROOT_AUTHORIZATION_DECISION_ID
predecessor_packet_id = EXACT_TERMINAL_PREDECESSOR_PACKET_ID
successor_packet_id = EXACT_SUCCESSOR_PACKET_ID
evidence_refs = EXACT_SORTED_ARRAY(PREDECESSOR_TERMINAL_EVIDENCE_ID,RENEWAL_POLICY_EVIDENCE_ID,SUCCESSOR_AUTHORIZATION_EVIDENCE_ID)
evaluation_time = EXACT_TRANSFER_EVALUATION_TIME
evaluation_time_source = EXACT_TRANSFER_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_TRANSFER_EVALUATION_CONTEXT_ID
```

Active-predecessor `TRANSFER_SUPERSESSION`:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_SHARED_CANONICAL_IDEMPOTENCY_KEY
event_class = TRANSFER_SUPERSESSION
from_disposition = RESERVED
to_disposition = RESERVED
from_owner_packet_id = EXACT_PREDECESSOR_PACKET_ID
to_owner_packet_id = EXACT_SUCCESSOR_PACKET_ID
previous_disposition_event_id = EXACT_PREDECESSOR_LATEST_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_PREDECESSOR_SUPERSEDED_TRANSITION_EVENT_ID,EXACT_SUCCESSOR_ACTIVATION_TRANSITION_EVENT_ID]
root_decision_ref = EXACT_SUCCESSOR_SOURCE_ROOT_AUTHORIZATION_DECISION_ID
predecessor_packet_id = EXACT_PREDECESSOR_PACKET_ID
successor_packet_id = EXACT_SUCCESSOR_PACKET_ID
evidence_refs = EXACT_SORTED_ARRAY(SUPERSESSION_POLICY_EVIDENCE_ID,SHARED_LOGICAL_INTENT_EVIDENCE_ID,SUCCESSOR_AUTHORIZATION_EVIDENCE_ID)
evaluation_time = EXACT_TRANSFER_EVALUATION_TIME
evaluation_time_source = EXACT_TRANSFER_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_TRANSFER_EVALUATION_CONTEXT_ID
```

Terminal-predecessor `TRANSFER_SUPERSESSION`:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_SHARED_CANONICAL_IDEMPOTENCY_KEY
event_class = TRANSFER_SUPERSESSION
from_disposition = RESERVED
to_disposition = RESERVED
from_owner_packet_id = EXACT_TERMINAL_PREDECESSOR_PACKET_ID
to_owner_packet_id = EXACT_SUCCESSOR_PACKET_ID
previous_disposition_event_id = EXACT_PREDECESSOR_LATEST_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_PREDECESSOR_TERMINAL_TRANSITION_EVENT_ID,EXACT_SUCCESSOR_ACTIVATION_TRANSITION_EVENT_ID]
root_decision_ref = EXACT_SUCCESSOR_SOURCE_ROOT_AUTHORIZATION_DECISION_ID
predecessor_packet_id = EXACT_TERMINAL_PREDECESSOR_PACKET_ID
successor_packet_id = EXACT_SUCCESSOR_PACKET_ID
evidence_refs = EXACT_SORTED_ARRAY(PREDECESSOR_TERMINAL_EVIDENCE_ID,SUPERSESSION_POLICY_EVIDENCE_ID,SUCCESSOR_AUTHORIZATION_EVIDENCE_ID)
evaluation_time = EXACT_TRANSFER_EVALUATION_TIME
evaluation_time_source = EXACT_TRANSFER_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_TRANSFER_EVALUATION_CONTEXT_ID
```

`CONSUME` after t04:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_OWNER_CANONICAL_IDEMPOTENCY_KEY
event_class = CONSUME
from_disposition = RESERVED
to_disposition = CONSUMED
from_owner_packet_id = EXACT_OWNER_PACKET_ID
to_owner_packet_id = EXACT_OWNER_PACKET_ID
previous_disposition_event_id = EXACT_OWNER_LATEST_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_G2A_T04_TRANSITION_EVENT_ID]
root_decision_ref = ABSENT_V01
predecessor_packet_id = ABSENT_V01
successor_packet_id = ABSENT_V01
evidence_refs = EXACT_SORTED_ARRAY(EFFECT_CONSUMPTION_EVIDENCE_ID,MOCK_ADAPTER_RESULT_EVIDENCE_ID)
evaluation_time = EXACT_T04_EVALUATION_TIME
evaluation_time_source = EXACT_T04_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_T04_EVALUATION_CONTEXT_ID
```

`UNCERTAIN_CLOSE` after t26:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_OWNER_CANONICAL_IDEMPOTENCY_KEY
event_class = UNCERTAIN_CLOSE
from_disposition = RESERVED
to_disposition = UNCERTAIN_CLOSED
from_owner_packet_id = EXACT_OWNER_PACKET_ID
to_owner_packet_id = EXACT_OWNER_PACKET_ID
previous_disposition_event_id = EXACT_OWNER_LATEST_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_G2A_T26_TRANSITION_EVENT_ID]
root_decision_ref = ABSENT_V01
predecessor_packet_id = ABSENT_V01
successor_packet_id = ABSENT_V01
evidence_refs = EXACT_SORTED_ARRAY(ADAPTER_INVOCATION_EVIDENCE_ID,EFFECT_OUTCOME_UNRESOLVED_EVIDENCE_ID)
evaluation_time = EXACT_T26_EVALUATION_TIME
evaluation_time_source = EXACT_T26_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_T26_EVALUATION_CONTEXT_ID
```

`RECEIPT_CONFIRM` after t05:

```text
event_profile_version = "v0.1"
idempotency_key = EXACT_OWNER_CANONICAL_IDEMPOTENCY_KEY
event_class = RECEIPT_CONFIRM
from_disposition = CONSUMED
to_disposition = CONSUMED
from_owner_packet_id = EXACT_OWNER_PACKET_ID
to_owner_packet_id = EXACT_OWNER_PACKET_ID
previous_disposition_event_id = EXACT_CONSUME_DISPOSITION_EVENT_ID
cause_transition_event_ids = [EXACT_G2A_T05_TRANSITION_EVENT_ID]
root_decision_ref = ABSENT_V01
predecessor_packet_id = ABSENT_V01
successor_packet_id = ABSENT_V01
evidence_refs = EXACT_SORTED_ARRAY(FULFILLMENT_CONSUMPTION_EVIDENCE_ID,TERMINAL_RECEIPT_EVIDENCE_ID)
evaluation_time = EXACT_T05_EVALUATION_TIME
evaluation_time_source = EXACT_T05_EVALUATION_TIME_SOURCE
evaluation_context_id = EXACT_T05_EVALUATION_CONTEXT_ID
```

### Non-consuming t24 unchanged-disposition law

`g2a_t24_nonconsuming_failure` records exactly:

```text
adapter invocation count = 1
effect non-consumption proven = true
lifecycle transition = PENDING_FULFILLMENT -> FAILED
FAILED provenance = FAILED_NON_CONSUMING
idempotency disposition before = RESERVED
idempotency disposition after = RESERVED
reservation owner before = exact current packet_id
reservation owner after = exact same packet_id
idempotency-disposition event appended = false
disposition-event history after
  == byte-identical disposition-event history before
latest disposition-event ID after
  == exact latest disposition-event ID before
effect_consumption_class = NOT_CONSUMED
adapter_invocation_relation_code =
  CORRIDOR_INVOCATION_NONCONSUMING
```

The t24 lifecycle transition binds the exact `execution_attempt_id`,
`adapter_invocation_evidence_valid`,
`effect_nonconsumption_evidence_valid`,
`idempotency_reservation_owned`, and
`latest_disposition_event_binding_valid` through exact
`TransitionEvidenceBindingV01` records. The unchanged disposition journal
continues to reconstruct the existing `RESERVED` disposition and exact packet
owner. No reservation is released, transferred, consumed, closed, renewed, or
recreated.

The absence of a new disposition event is not an absence of evidence. t24
evidence is the validated lifecycle transition plus its typed evidence
bindings.

Exact outcome-to-disposition mapping:

| lifecycle transition | lifecycle event | disposition event | disposition before/after | owner | atomic requirement |
|---|---|---|---|---|---|
| `g2a_t04_fulfill_mock` | appended | `CONSUME` | `RESERVED -> CONSUMED` | unchanged exact packet owner | lifecycle event plus disposition event |
| `g2a_t24_nonconsuming_failure` | appended | none | `RESERVED -> RESERVED` | unchanged exact packet owner | lifecycle event plus byte-identical journal and unchanged latest-event-ID proof |
| `g2a_t26_uncertain_adapter_outcome` | appended | `UNCERTAIN_CLOSE` | `RESERVED -> UNCERTAIN_CLOSED` | unchanged exact packet owner | lifecycle event plus disposition event |
| `g2a_t05_receipt` | appended | `RECEIPT_CONFIRM` | `CONSUMED -> CONSUMED` | unchanged exact packet owner | lifecycle event plus disposition event and exact receipt evidence |

The following lifecycle transitions append no disposition event solely because
their lifecycle state changes:

```text
g2a_t02_queue
g2a_t03_pending
g2a_t24_nonconsuming_failure
g2a_t25_retry
deterministic block
deterministic expiry
Root revocation
```

Their disposition remains exactly what validated disposition history proves.
Renewal and supersession continue to use only the exact `RESERVE` or
`TRANSFER_*` branches in the existing matrix.

The six event classes are closed. No `RELEASE` event exists. Every event after
the first binds the exact previous disposition-event ID. Fork, deletion,
rewrite, owner substitution, disposition downgrade, second transfer from a
superseded predecessor, transfer after `CONSUMED`, transfer after
`UNCERTAIN_CLOSED`, or event outside its complete atomic bundle fails closed.

`QUEUED`, `PENDING_FULFILLMENT`, t24 `FAILED_NON_CONSUMING`, and
`g2a_t25_retry` preserve the same reservation owner and byte-identical
disposition journal. `FULFILLED_MOCK` plus `CONSUME`, uncertain `FAILED` plus
`UNCERTAIN_CLOSE`, and receipt observation plus `RECEIPT_CONFIRM` are exact
atomic pairs. No event in a required pair is accepted independently. t24 is
an atomic lifecycle update with validated unchanged disposition, not a pair of
newly appended events.

Current disposition and reservation owner are reconstructed from the ordered
validated disposition-event history. Existing pre-G2-A
`used_idempotency_keys` remains compatibility snapshot evidence that a key was
seen or reserved; it is not terminal-consumption proof.

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

After exact t24, `FAILED_NON_CONSUMING` may enter `g2a_t25_retry` only under
all of those conditions. The retry uses the same packet ID, idempotency key,
`RESERVED` disposition, reservation owner, and byte-identical disposition
history. It appends no `RESERVE`, transfer, or no-op disposition event. A new
canonical execution-attempt ID is created only when the next
`g2a_t03_pending` transition is accepted.

Retry is blocked when disposition is not `RESERVED`, reservation owner differs,
t24 evidence is invalid, provenance is not `FAILED_NON_CONSUMING`, policy
forbids retry, time is invalid, a dependency is stale, packet is revoked or
superseded, terminal receipt exists, consumption evidence exists, or
uncertainty closure exists.

Retry after terminal consumption is `BLOCKED`.

Terminal consumption includes:

- successful `FULFILLED_MOCK`;
- accepted terminal receipt;
- exact terminal consumption event;
- an equivalent terminal effect closure introduced only by a new versioned
  profile.

`UNCERTAIN` is not terminal consumption and is not non-consumption. It is a
separate terminal reuse closure that closes the protected idempotency key
without classifying the effect outcome.

A new packet ID cannot bypass a consumed or uncertain-closed idempotency key.
Retry counter, issue time, expiry time, adapter implementation change, and
execution-attempt ID cannot change logical-effect identity.

`FAILED` from `g2a_t24_nonconsuming_failure` is retryable only under every
existing retry condition. `FAILED` from
`g2a_t26_uncertain_adapter_outcome` is terminal: the same packet cannot
requeue, and no packet can reuse the same idempotency key. Later proof of
consumption may bind observed receipt or effect evidence, but the protected
key remains closed. Later proof of non-consumption cannot reactivate the old
packet or key under this profile. A genuinely new consequential attempt
requires a new Root decision and a materially distinct canonical
logical-effect identity.

## 23. Dependency and Kill-Switch Evidence

Prospective domain-neutral invalidation record:

```text
profile_id = action_invalidation_evidence_profile_v01
invalidation_evidence_material_v01 = [
  ["profile_id", "action_invalidation_evidence_profile_v01"],
  ["source_invalidation_event_ref", EXACT_NON_EMPTY_STRING],
  ["packet_id", EXACT_CANONICAL_PACKET_ID],
  ["dependency_id", EXACT_NON_EMPTY_STRING],
  ["invalidation_class",
   ONE_OF_DEPENDENCY_CHANGED_DEPENDENCY_STALE_ROOT_BOUND_KILL_SWITCH_MANUAL_CANCEL_EVIDENCE_ROOT_REVOCATION_ROOT_SUPERSESSION],
  ["evidence_ref", EXACT_NON_EMPTY_STRING],
  ["evidence_sha256", EXACT_LOWERCASE_SHA256],
  ["observed_status", EXACT_NON_EMPTY_STRING],
  ["time_envelope_id", EXACT_NON_EMPTY_STRING],
  ["freshness_policy_id", EXACT_NON_EMPTY_STRING],
  ["owning_local_root_id", EXACT_NON_EMPTY_STRING],
  ["accepted_by_local_root_id", EXACT_NON_EMPTY_STRING],
  ["acceptance_root_decision_id", VALUE_OR_ABSENT_V01],
  ["acceptance_root_decision_hash", VALUE_OR_ABSENT_V01],
  ["validation_status", "LOCAL_VALIDATION_PASS"],
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
invalidation_evidence_bytes =
  canonical_json_bytes_v01(invalidation_evidence_material_v01)

invalidation_evidence_id =
  domain_separated_sha256_hex_v01(
    domain="HEDGEHOG_ACTION_INVALIDATION_EVIDENCE_V01",
    payload=invalidation_evidence_bytes
  )
```

Exact invalidation classes:

```text
DEPENDENCY_CHANGED
DEPENDENCY_STALE
ROOT_BOUND_KILL_SWITCH
MANUAL_CANCEL_EVIDENCE
ROOT_REVOCATION
ROOT_SUPERSESSION
```

`invalidation_evidence_id` is never inside its own material.
`source_invalidation_event_ref` identifies the observed source event or
observation and is not the computed evidence identity.

```text
invalidation.owning_local_root_id
  == invalidation.accepted_by_local_root_id
  == packet.owning_local_root_id
```

Exact class/effect mapping:

```text
DEPENDENCY_CHANGED
  -> DETERMINISTIC_BLOCK

DEPENDENCY_STALE
  -> DETERMINISTIC_BLOCK

ROOT_BOUND_KILL_SWITCH
  -> DETERMINISTIC_BLOCK

MANUAL_CANCEL_EVIDENCE
  -> DETERMINISTIC_BLOCK only when the exact manual-cancel condition is
     already bound into packet authority policy
  -> otherwise NEW_ROOT_REVOCATION_DECISION is required

ROOT_REVOCATION
  -> ROOT_REVOCATION

ROOT_SUPERSESSION
  -> ROOT_SUPERSESSION
```

For a deterministic block already covered by packet policy:

```text
acceptance_root_decision_id = ABSENT_V01
acceptance_root_decision_hash = ABSENT_V01
root_decision_ref = ABSENT_V01
```

Local validation and the exact three-way owning Root binding remain
mandatory. No new authority is created.

For Root revocation or supersession:

```text
acceptance_root_decision_id
  == root_decision_ref
  == validated new RootDecisionResultV01.decision_id

acceptance_root_decision_hash
  == rebuilt validated decision projection hash
```

The exact Root result is validated under section 13.12. `ROOT_REVOCATION`
invalidation evidence binds exact `AcceptedRevocationBindingV01`;
`ROOT_SUPERSESSION` invalidation evidence binds exact
`AcceptedSupersessionBindingV01`. The corresponding lifecycle transition
references the accepted post-Root binding as typed transition evidence. A
pre-Root revocation or supersession candidate cannot satisfy the transition.
Wrong owning Root, wrong accepting Root, class/effect mismatch, partial
sentinel use, deterministic block outside bound policy, foreign Root
decision, or candidate/binding substitution fails closed.

Section 13.6 separates the pre-Root
`dependency_set_candidate_fingerprint` from the post-Root
`PacketDependencyAcceptanceBindingV01`. Together they bind the exact
mandatory dependency set, content hashes, TimeEnvelope identities, freshness
policies, requirement classes, expected local Root, accepted authorization
candidate, source Root decision, and packet. Neither object recursively
contains the other.

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

`ActionPacketEffectFirewallProjectionV01` is the sole legal G2-A projection
into the existing Gate-1 effect path. It is a deterministic projection, not a
second effect path or authority surface.

Exact canonical path:

```text
packet authorization candidate
-> RootDecisionCandidateProjectionV01
-> validated RootDecisionResultV01
-> ActionCommitPacketV02 genesis
-> lifecycle activation
-> Registry state
-> immediate Corridor eligibility check
-> ActionPacketEffectFirewallProjectionV01
-> existing EffectFirewallV01
-> EffectRequestV01
-> private mock capability
-> evidence-only result
```

No parallel effect executor, action path, capability system, adapter owner, or
permission path is authorized.

Exact bridge equalities:

```text
firewall.invocation_id
  == execution_attempt_id

firewall.transaction_id
  == packet.transaction_id

firewall.target_root_id
  == packet.owning_local_root_id

firewall.root_decision_id
  == packet.source_root_decision_id

firewall.selected_candidate_id
  == root_packet_authorization_candidate_id

firewall.permission_ref
  == canonical_permission_ref

firewall.allowed_adapter_ids
  == packet.normalized_permission_scope.allowed_adapter_ids

firewall.allowed_action_kinds
  == packet.normalized_permission_scope.allowed_action_classes

firewall.root_scope_refs
  == exact non-empty canonical subject-then-target projection

firewall.maximum_expires_at_tick
  == exact bridged packet expires_at_utc tick

firewall.mock_only
  == true

firewall.effect_access_owner
  == existing frozen EffectFirewallV01 owner constant

effect_request.request_kind
  == "ActionCommitPacket"

effect_request.transaction_id
  == firewall.transaction_id

effect_request.target_root_id
  == firewall.target_root_id

effect_request.root_decision_id
  == firewall.root_decision_id

effect_request.selected_candidate_id
  == firewall.selected_candidate_id

effect_request.permission_ref
  == firewall.permission_ref

effect_request.adapter_id
  == canonical packet.adapter_binding.adapter_id

effect_request.action_kind
  == canonical selected action

effect_request.scope_refs
  == firewall.root_scope_refs

effect_request.issued_at_tick
  == exact bridged packet issued_at_utc tick

effect_request.expires_at_tick
  == exact bridged packet expires_at_utc tick

effect_request.idempotency_key
  == packet canonical idempotency_key

effect_request.mock_only
  == true
```

The `root_scope_refs` projection concatenates subject refs followed by target
refs after each source collection has been normalized, duplicate-checked, and
sorted by the section 10 normalized UTF-8-byte rule. Caller order cannot
influence the projection.

For the current Supplier compatibility fixture:

```text
canonical packet.adapter_binding.adapter_id
  == "mock_adapter:mock_bank_sandbox"

canonical selected action
  == "mock_action:mock_supplier_a_payment_order"

effect_request.adapter_id
  == "mock_adapter:mock_bank_sandbox"

effect_request.action_kind
  == "mock_action:mock_supplier_a_payment_order"
```

The selected request action remains in `firewall.allowed_action_kinds`, outside
forbidden action policy, inside Root-approved candidate scope, and inside
packet permission/policy scope. The selected adapter remains in
`firewall.allowed_adapter_ids`, outside forbidden adapter policy, mock-only,
inside Root-approved candidate scope, and inside packet permission/policy
scope.

Existing builders rebuild `firewall_id` and `request_id`. Caller-supplied
replacements fail closed.

Existing permission requirements remain exact:

```text
permission_required = true
user_permission_present = true
permission_scope_valid = true
permission_ref starts with "permission:"
```

G2-A creates no permission and cannot weaken, omit, default, or bypass these
conditions.

`LogicalTimeBridgeV01` is the sole bridge into:

```text
firewall.maximum_expires_at_tick
effect_request.issued_at_tick
effect_request.expires_at_tick
effect authorization current_tick
effect execution current_tick
```

Every projected tick must round-trip exactly through the approved bridge to
the originating canonical epoch second. Rounding, truncation, inferred origin,
inferred tick scale, ambient clock, and implicit epoch/tick conversion are
forbidden. An unrepresentable temporal projection fails closed.

Exact per-execution-attempt Firewall law:

```text
one execution_attempt_id
  -> one EffectFirewallV01 invocation_id
  -> one private per-invocation Firewall state
```

The same `EffectFirewallV01` instance is never reused for a later retry. A new
accepted t03 creates a new execution-attempt ID, new Firewall invocation, and
new private per-invocation state.

The existing Firewall's private `seen_request_ids`,
`used_idempotency_keys`, `issued_capabilities`,
`consumed_capability_ids`, and `terminal_receipt_ids` remain
per-invocation enforcement state. They do not replace the cross-attempt
`IdempotencyDispositionEventV01` journal. In particular, a key in Firewall
`used_idempotency_keys` is not by itself global `CONSUMED` truth.

Exact attempt outcomes:

```text
t04:
  current Firewall capability is consumed
  lifecycle appends t04
  disposition appends CONSUME

t24:
  current Firewall invocation is retired after proven non-consumption
  lifecycle appends t24
  no disposition event is appended
  global disposition remains RESERVED
  reservation owner remains the same packet
  later valid retry uses a new t03 attempt and new Firewall instance

t26:
  current Firewall invocation is retired
  lifecycle appends t26
  disposition appends UNCERTAIN_CLOSE
  no later Firewall invocation may use the same key

t05:
  receipt observation confirms the already consumed outcome
  disposition appends RECEIPT_CONFIRM
  no new consumption is created
```

A failed eligibility check before adapter invocation invokes no adapter,
appends no outcome transition or disposition event, exposes no capability, and
does not globally consume or close the key. No old Firewall capability or
decision survives into another execution attempt. A capability cannot be
serialized, copied, replayed, or reused.

Immediately before every mock adapter invocation, the exclusive bounded
Corridor and Effect Firewall path independently verifies:

- exact canonical JSON plus keyword-only hash API use;
- canonical packet ID rebuild;
- canonical idempotency-key rebuild;
- stable logical-intent ID rebuild;
- packet-authorization candidate ID rebuild;
- owning Root and logical-intent binding;
- exact non-empty transaction continuity through Root, packet, Firewall, and
  EffectRequest;
- exact canonical `permission:` reference from validated Root permission
  state;
- validated source Root decision ID, projection hash, and boundary binding;
- V02 operational projection coherence;
- packet structural validity;
- exact Transition Registry identity and validity;
- immutable packet genesis;
- legal lifecycle state;
- legal transition history;
- exact `FAILED` provenance;
- temporal consistency;
- not-before rule;
- present expiry;
- non-revocation;
- non-supersession;
- dependency-set candidate fingerprint;
- mandatory-dependency local Root acceptance;
- exact `PacketDependencyAcceptanceBindingV01`;
- current mandatory dependency validity;
- accepted kill-switch conditions;
- policy-bound idempotency namespace and reservation ownership;
- complete ordered idempotency-disposition-event history;
- idempotency disposition is exactly `RESERVED`;
- reservation owner equals the current packet ID;
- absence of terminal receipt;
- scope containment;
- canonical `mock_adapter:` adapter binding and canonical `mock_action:`
  selected action;
- exact `EffectRequestV01` request kind and all required fields;
- every generic permission, adapter, action, effect, business-object, and
  Corridor coherence law in section 13.11;
- every `ActionPacketEffectFirewallProjectionV01` equality;
- exact permission-state requirements;
- exact LogicalTimeBridge round-trip;
- fresh per-attempt Firewall instance and invocation/attempt equality;
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

The final pre-adapter rule is:

```text
Corridor lifecycle, Registry, dependency, and idempotency eligibility passes
AND EffectFirewallV01 authorization passes
-> private mock capability may exist
```

If either side fails, no private capability exists and the adapter is not
called.

One exclusive Corridor operation performs:

```text
validate present eligibility
-> invoke adapter at most once
-> classify the observed result
-> atomically append exactly one of:
     g2a_t04_fulfill_mock
     g2a_t24_nonconsuming_failure
     g2a_t26_uncertain_adapter_outcome
-> apply the exact branch:
     t04 + CONSUME
     t24 + validated unchanged RESERVED disposition,
           unchanged owner,
           byte-identical disposition history,
           unchanged latest disposition-event ID,
           no disposition event
     t26 + UNCERTAIN_CLOSE
```

`g2a_t04_fulfill_mock` records a proven consumed mock result from that
invocation. `g2a_t24_nonconsuming_failure` records a proven non-consuming
result from that invocation, appends no disposition event, preserves the exact
`RESERVED` owner and byte-identical disposition history, and never invokes the
adapter again.
`g2a_t26_uncertain_adapter_outcome` records an unresolvable consumption
classification from that invocation, never invokes the adapter again, and
closes idempotency as `UNCERTAIN_CLOSED`. These three outcomes are mutually
exclusive classifications of one invocation. `g2a_t05_receipt` observes and
binds a post-invocation receipt; it invokes no adapter and creates no
consumption. It appends `RECEIPT_CONFIRM` only with exact receipt and prior
consumption evidence.

Exact t24 atomicity:

```text
validate current lifecycle eligibility
-> validate current disposition == RESERVED
-> validate current reservation owner == packet_id
-> invoke adapter exactly once
-> prove non-consumption
-> construct and validate g2a_t24 transition event
-> prove disposition journal before/after byte equality
-> atomically append only the validated t24 transition event
```

If any t24 validation fails, no lifecycle event or disposition event is
appended, disposition history and owner remain unchanged, no retry is
authorized by that failed operation, no receipt is fabricated, and no second
adapter invocation occurs.

If an adapter was invoked and outcome cannot be proven `CONSUMED` or
`NOT_CONSUMED`, Corridor records
`g2a_t26_uncertain_adapter_outcome` with exact invocation evidence and
`effect_consumption_class = UNCERTAIN` and atomically appends the matching
`UNCERTAIN_CLOSE` disposition event. It fabricates no receipt, makes no
outcome assumption, performs no retry, and permanently prevents reuse of the
packet and idempotency key.

A successful `g2a_t04_fulfill_mock` and matching `CONSUME` disposition event
are one atomic in-memory operation. Neither event is accepted alone.

## 25. Receipt and Ledger Preservation

Receipt is evidence only. It cannot create, renew, widen, revoke, or supersede
permission; create a packet; alter packet scope; reopen consumed idempotency;
erase history; release shipment; authorize Supplier B; become Root; or create
FinalOutput.

The future G2-A history preserves:

- original Root decision;
- original packet identity;
- original stable logical-intent identity;
- original packet-authorization candidate identity;
- dependency-set candidate and exact packet-acceptance binding;
- revocation/supersession candidates and their accepted post-Root bindings;
- original idempotency identity;
- original temporal authority tuple;
- every lifecycle transition;
- every typed transition-evidence binding;
- every accepted invalidation event;
- every kill-switch event;
- every attempt record;
- every consumption record;
- every reservation and reservation-transfer record;
- every idempotency-disposition event and previous-event link;
- every uncertain-outcome and reconciliation record;
- every receipt;
- exact reason executability ended.

Current state is reconstructable from immutable packet genesis, ordered
transition history, ordered idempotency-disposition history, invalidation
evidence, and reconciliation evidence.
Historical authorization can remain true as a historical fact while current
executability is false.

For t24, preservation means the lifecycle journal gains the exact
`FAILED_NON_CONSUMING` event while the disposition journal remains
byte-identical and retains its exact latest event ID and `RESERVED` owner.
This difference between the two journals is intentional and auditable.

Reconciliation after an uncertain adapter outcome appends evidence only. It
cannot rewrite the uncertain event, create a receipt without actual receipt
evidence, reopen state, reopen idempotency, create permission, or invoke an
adapter.

G2-A remains an in-memory reference-kernel proof. It does not add production
Ledger persistence. Existing Airline ledger and Supplier evidence histories
remain frozen and are used only as read-only compatibility evidence.

## 26. Replay Non-Execution and Temporal Views

Historical verification replay:

- uses original recorded evaluation time;
- reconstructs packet eligibility from immutable packet genesis, the exact
  Transition Registry identity, ordered transition events, ordered
  idempotency-disposition events and reservation ownership, and Root-accepted
  dependency evidence at that recorded moment;
- verifies source Root binding, V02 operational projection, transitions,
  invalidations, and reconciliation evidence;
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

Replay treats terminal uncertain `FAILED` as permanently non-executable. It
may verify later reconciliation evidence but cannot reinterpret that evidence
as state reopening, key reuse, permission, receipt creation, or a new adapter
call.

Replay rebuilds the exact disposition state and owner from the append-only
journal. It cannot create or transfer an idempotency reservation, append a
disposition event, alter a Registry identity, synthesize packet genesis,
substitute dependency acceptance, or repair a non-self-consistent invalidation
identity.

For t24, Replay verifies the exact `FAILED_NON_CONSUMING` lifecycle event and
its typed non-consumption evidence while proving that disposition-event
history bytes and latest disposition-event ID are unchanged. It reconstructs
the same `RESERVED` disposition and exact packet owner from that unchanged
journal. Retry eligibility can arise only from exact
`FAILED_NON_CONSUMING` provenance plus every current retry check; Replay
cannot authorize or perform the retry.

Replay verifies that each accepted execution attempt used a distinct Firewall
invocation and private state. It cannot recreate a Firewall, reuse an old
instance or capability, treat per-invocation `used_idempotency_keys` as global
consumption truth, or project historical raw compatibility identifiers
directly into the frozen Firewall.

Replay verifies pre-Root candidates and their accepted post-Root bindings as
distinct immutable objects. It cannot derive a new
`PacketDependencyAcceptanceBindingV01`, `AcceptedRevocationBindingV01`, or
`AcceptedSupersessionBindingV01`; cannot submit a candidate through the frozen
Root path; and cannot invoke `ActionPacketEffectFirewallProjectionV01` to
obtain a capability.

Closed Package, Anchor, Replay, and evidence artifacts remain frozen.
Lifecycle-aware Replay verification is added only through the bounded G2-A
runtime and test surface.

## 27. Legacy Dictionary Compatibility

### Existing ActionCommitPacketV02 Operational Projection v0.1

Existing Supplier-shaped `PermissionScopeV02` fields are compatibility inputs
inside the canonical `ActionCommitPacketV02` family. They are not a second
authority model. G2-A-aware packets use generic canonical profiles.
Legacy/pre-G2-A `ActionCommitPacketV02` fixtures pass through one deterministic
compatibility projection before lifecycle evaluation.

The exact permission-scope material is:

```text
action_permission_scope_material_v01 = [
  ["profile_id", "action_permission_scope_profile_v01"],
  ["allowed_action_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["forbidden_action_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["allowed_adapter_ids", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["forbidden_adapter_ids", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["required_approval_refs", EXACT_SORTED_UNIQUE_STRING_ARRAY],
  ["prohibited_effect_classes", EXACT_SORTED_UNIQUE_STRING_ARRAY]
]
```

Current `PermissionScopeV02` projection:

```text
normalized_subject_scope.included_subject_refs
  == canonicalized scope.allowed_subjects

normalized_subject_scope.excluded_subject_refs
  == canonicalized scope.forbidden_subjects

normalized_permission_scope.allowed_action_classes
  == exact sorted unique canonical Firewall action IDs produced by
     EffectFirewallVocabularyProjectionV01 from legacy scope.allowed_actions

normalized_permission_scope.allowed_adapter_ids
  == exact sorted unique canonical Firewall adapter IDs produced by
     EffectFirewallVocabularyProjectionV01 from legacy scope.allowed_adapters

normalized_permission_scope.required_approval_refs
  == [canonical_permission_ref]

normalized_permission_scope.prohibited_effect_classes
  == []

canonical selected action_kind
  == exact mapped canonical Firewall ID of explicit legacy selected action
  == "mock_action:mock_supplier_a_payment_order"

normalized_target_scope.included_target_refs
  == canonicalized set(scope.creditor_ref, scope.payment_slot_ref)

normalized_target_scope.excluded_target_refs
  == []
```

Legacy `scope.forbidden_actions` and `scope.forbidden_adapters` remain exact
compatibility-denial evidence and are checked before any mapping. A listed
legacy value receives its exact closed canonical counterpart only for
canonical forbidden-set comparison. An unlisted raw denial value remains
compatibility evidence and cannot be promoted into any allowed surface.

Supplier compatibility projection:

```text
normalized_business_object_identity.business_object_class
  == "PAYMENT_SLOT"

normalized_business_object_identity.business_object_namespace
  == exact authority-policy-approved namespace

normalized_business_object_identity.business_object_ref
  == scope.payment_slot_ref

normalized_business_object_identity.owning_effect_root_id
  == packet.owning_local_root_id

normalized_consequential_effect_parameters.amount_decimal
  == canonicalized scope.amount

normalized_consequential_effect_parameters.currency_code
  == scope.currency

normalized_consequential_effect_parameters.quantity_decimal
  == ABSENT_V01
```

The creditor reference remains in normalized target scope and cannot drift
between packet, Corridor step, and receipt.

`packet.human_approval_ref` remains evidence only and is not copied into
`required_approval_refs`, Root permission state, Firewall permission, or
EffectRequest permission. It cannot be rewritten from `human_approval:` to
`permission:`. The explicit `canonical_permission_ref` comes only from the
validated pre-Root permission context.

Adapter compatibility:

```text
canonical adapter_binding.adapter_id
  == exact mapped canonical Firewall ID of
     legacy packet.adapter_binding.adapter_id
  == "mock_adapter:mock_bank_sandbox"

adapter_binding.adapter_kind
  == packet.adapter_binding.adapter_kind

packet.adapter_binding.real_adapter is false

adapter_binding.mock_only is true
```

The current Supplier compatibility profile binds:

```text
legacy selected adapter = "mock_bank_sandbox"
canonical selected adapter = "mock_adapter:mock_bank_sandbox"
legacy selected action = "mock_supplier_a_payment_order"
canonical selected action = "mock_action:mock_supplier_a_payment_order"
```

The legacy selected action is explicit compatibility input. It is never
inferred from tuple position, lexical order, display text, or a single
remaining candidate.

The exact empty `prohibited_effect_classes` array weakens no policy.
Executable effect class remains constrained by
`authority_policy.allowed_logical_effect_classes`, the canonical allowed-action
whitelist, selected-action membership, mock-only Firewall namespaces, and the
real-effect prohibition. Unknown or real effects remain fail closed.

A G2-A-aware `AdapterBindingV02` carries one exact `adapter_version`.
Pre-G2-A fixtures lacking it use only:

```text
PRE_G2A_ADAPTER_VERSION_V01 =
  "pre_g2a_adapter_contract_v01"
```

The compatibility projection cannot infer version from display text.

Corridor compatibility:

```text
packet.corridor_class
  == ContractFulfillmentCorridorV01.corridor_kind

Corridor packet_id
  == canonical packet_id

CorridorStep parent_packet_id
  == canonical packet_id

CorridorStep adapter_id
  == canonical adapter_binding.adapter_id

CorridorStep amount
  == canonical consequential amount

CorridorStep creditor_ref
  == canonical target creditor

CorridorStep payment_slot_ref
  == canonical business-object ref

CorridorStep idempotency_key
  == canonical idempotency key
```

Receipt compatibility:

```text
receipt.packet_id
  == canonical packet_id

receipt.adapter_id
  == canonical adapter ID

receipt.subject
  == canonical target creditor

receipt.amount and receipt.currency
  == canonical consequential parameters

receipt.idempotency_key
  == canonical idempotency key
```

All authority-relevant evidence in current packet fields is represented in the
stable logical-intent material, Root-selected packet-authorization candidate,
permission profile, dependency-candidate profile, post-Root dependency
acceptance binding, or policy profile. `drs_refs`,
`avf_refs`, and `bsep_ref` remain advisory lineage; presence creates no
authority. Divergence between operational fields and canonical profiles fails
closed.

Passing current Supplier-specific compatibility checks does not establish
generic G2-A validity. The projected packet must separately pass every section
13.11 permission/policy coherence law and every section 24
`ActionPacketEffectFirewallProjectionV01` equality before the existing Effect
Firewall can issue a private mock capability.

`PacketTTL.created_at`, `PacketTTL.expires_at`, `PacketTTL.ttl_seconds`,
`PacketTTL.ttl_valid`, and `PacketTTL.expired` use section 14 compatibility
only. Amount and currency use section 14.1 compatibility only.

### Legacy Dictionary Packet Projection

Any legacy dictionary packet entering G2-A evaluation passes through one
deterministic compatibility adapter located in the future G2-A runner or the
authorized V02 module.

The adapter:

- rebuilds canonical packet identity;
- rebuilds canonical idempotency identity;
- rebuilds the stable logical-intent identity;
- rebuilds the packet-authorization candidate identity;
- maps legacy adapter/action identifiers only through
  `EffectFirewallVocabularyProjectionV01`;
- requires explicit `canonical_permission_ref`;
- requires explicit canonical transaction context;
- requires explicit selected legacy action;
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

For the current Supplier compatibility fixture, explicit surrounding accepted
runtime context supplies:

```text
transaction_id
owning_local_root_id
stable logical-effect intent
packet-authorization candidate
canonical_permission_ref
authority policy
dependency candidate
temporal bridge
selected action
```

Missing context fails closed. No value is inferred from display wording,
invoice number, payment slot, creditor reference, packet name, creation time,
or Registry order.

Pre-G2-A packet, CorridorStep, receipt, demo, report, and closed evidence bytes
remain unchanged and are consumed read-only. Historical raw identifiers remain
valid historical compatibility evidence but are never directly supplied to
the frozen Effect Firewall. No closed Airline or Supplier artifact is
regenerated.

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
Corridor law, Effect Firewall projection, generic permission/effect coherence,
receipt law, and Replay non-execution law. Domain-specific authority never
enters the kernel.

## 29. Implementation Slice Plan

### SLICE G2-A1 - Canonical Profiles

- implement exact canonical-byte and keyword-only hashing;
- implement exact packet, idempotency, stable logical-intent,
  packet-authorization-candidate, source Root-decision projection, and V02
  operational-projection profiles;
- implement `DependencySetCandidateV01` and the separate post-Root
  `PacketDependencyAcceptanceBindingV01`;
- implement `RootDecisionCandidateProjectionV01` through the unchanged Root
  Review, Post V&V, GT, and frozen Root validator path;
- invoke the exact frozen Root validator with kernel, decision input, and
  result;
- implement `ABSENT_V01`;
- implement all nested normalization profiles;
- implement exact cross-profile coherence and consequential-parameter
  projection;
- implement `EffectFirewallVocabularyProjectionV01`, exact closed Supplier
  legacy mappings, canonical permission-reference separation, and executable
  transaction continuity;
- implement policy-bound idempotency namespace and classes;
- implement canonical time, legacy decimal and PacketTTL compatibility,
  expiry, logical-time bridge, and dependency candidate fingerprint;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A2 - Lifecycle and History

- add the versioned ABI lifecycle profile;
- add immutable packet genesis and the exact Transition Registry identity;
- add the exact 26 machine-code transition rules in the existing Registry
  family;
- implement the exact five-code adapter-invocation relation;
- implement `TransitionEvidenceBindingV01` and the rule-exact
  execution-attempt/receipt matrix;
- add immutable transition records;
- add immutable 16-field idempotency-disposition events;
- implement the complete six-class disposition-event field matrix and
  Branch-A/Branch-B renewal matrix;
- derive current Registry state;
- implement rule/event identity separation, performing-component binding,
  exact `FAILED` provenance, activation, reservation ownership and transfer,
  retry, consumption, and uncertain terminal-closure laws;
- preserve unknown-transition fail-closed;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A3 - Root-Bound Invalidation

- bind Root authorization through the exact packet-authorization candidate and
  validated `RootDecisionResultV01`;
- preserve the stable logical-intent identity independently from the
  authorization candidate;
- record Root revocation and supersession evidence;
- implement `RevocationCandidateV01`, `SupersessionCandidateV01`,
  `AcceptedRevocationBindingV01`, and
  `AcceptedSupersessionBindingV01` as exact pre-Root/post-Root pairs;
- enforce renewal laws;
- validate mandatory-dependency local Root acceptance;
- validate non-self-referential invalidation and accepted kill-switch evidence;
- prove Registry creates no authority;
- add focused adversarial tests.

Owner review and commit boundary follows this slice.

### SLICE G2-A4 - Corridor Integration

- revalidate immediately before fulfillment;
- project through the sole `ActionPacketEffectFirewallProjectionV01` into the
  existing `EffectFirewallV01` and `EffectRequestV01` path;
- project every frozen Firewall and EffectRequest field, rebuild Firewall and
  request IDs, and bind `invocation_id` to `execution_attempt_id`;
- rebuild packet, idempotency, Root, operational-projection, Registry, genesis,
  transition-history, disposition-event-history, and reservation bindings;
- enforce generic permission, adapter, action, effect, business-object, and
  Corridor coherence independently of legacy validation;
- require exact `LogicalTimeBridgeV01` round-trip for Firewall ticks;
- create one fresh private Firewall state per accepted t03 attempt and forbid
  instance or capability reuse across retries;
- block expiry, stale or unaccepted dependency, consumed key, wrong reservation
  owner, terminal receipt, revocation, supersession, uncertain-closed key, and
  accepted kill switch;
- classify one adapter invocation under exact branches: t04 plus `CONSUME`;
  t24 plus validated unchanged `RESERVED` disposition, owner, journal bytes,
  and latest disposition-event ID; t26 plus `UNCERTAIN_CLOSE`;
- record terminal uncertain adapter outcomes without fabricating receipts;
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

Lifecycle-activation tests:

- `CREATED` is already Root-bound and non-executable;
- activation creates no authority and no new Root decision;
- lifecycle runtime cannot activate invalid genesis;
- the superseded pre-v0.1.3 t01 rule identifier is rejected;
- `g2a_t01_activate_root_authorization` requires the existing source
  authorization and exact idempotency acquisition;
- activation and `RESERVE` form one complete atomic bundle.

Registry machine-identity tests:

- punctuation-only explanation change does not change Registry ID;
- prose explanation change does not change Registry ID;
- evidence-code change changes Registry ID;
- fail-code change changes Registry ID;
- code order change changes Registry ID;
- unknown evidence code is rejected;
- unknown fail code is rejected;
- free-form prose inside a machine rule is rejected;
- every rule's Root-decision requirement uses the exact closed mapping.

Logical-intent and authorization-candidate tests:

- exact stable logical-intent field count 9 and exact order;
- exact packet-authorization-candidate field count 18 and exact order;
- TTL change preserves `root_owned_intent_id` and `idempotency_key`;
- adapter-version change preserves `root_owned_intent_id` and
  `idempotency_key`;
- dependency change preserves logical intent when consequential effect is
  unchanged;
- policy-version change preserves logical intent when consequential effect is
  unchanged;
- consequential amount change changes logical intent and key;
- Root selects the packet-authorization candidate, not logical-intent ID;
- substituted authorization candidate is rejected;
- packet candidate plus source decision reconstructs exact packet ID.

Frozen Root API tests:

- exact kernel, decision input, and result validation passes;
- wrong kernel is rejected;
- wrong `RootDecisionInputV01` is rejected;
- mismatched `decision_input_id` is rejected;
- valid result from another decision context is rejected.

Idempotency-disposition-journal tests:

- exact disposition-event field count 16 and exact order;
- initial `RESERVE` chain;
- reservation fork rejected;
- renewal transfer from expired predecessor;
- renewal transfer from active predecessor with atomic supersession;
- supersession transfer;
- incomplete atomic bundle rejected;
- wrong predecessor owner rejected;
- wrong successor owner rejected;
- transfer without new Root decision rejected;
- transfer after `CONSUMED` rejected;
- transfer after `UNCERTAIN_CLOSED` rejected;
- `CONSUME` maps only to `g2a_t04_fulfill_mock`;
- `UNCERTAIN_CLOSE` maps only to
  `g2a_t26_uncertain_adapter_outcome`;
- `RECEIPT_CONFIRM` cannot create consumption;
- `RELEASE` event is rejected;
- Replay reconstructs exact disposition owner and state.

Invalidation Root-binding tests:

- owning Root mismatch rejected;
- accepting Root mismatch rejected;
- invalidation class/effect mismatch rejected;
- partial sentinel fields rejected;
- deterministic manual cancellation outside policy rejected;
- revocation or supersession decision ID and hash mismatch rejected.

Identity tests:

- every identity canonicalizes material before keyword-only hash invocation;
- positional hash invocation and raw structured payloads are rejected;
- exact packet field count 20 and exact order;
- exact idempotency field count 10 and exact order;
- exact stable logical-intent field count 9 and exact order;
- exact packet-authorization-candidate field count 18 and exact order;
- exact idempotency-disposition-event field count 16 and exact order;
- exact transition-event field count 22 and exact Registry-ID binding;
- unknown, omitted, duplicate, and reordered fields rejected;
- `ABSENT_V01` differs from null, empty string, and omission;
- both transaction and stable logical intent bind when present;
- one absent identifier is encoded explicitly;
- both policy values bind when present;
- one absent policy value is encoded explicitly;
- forged packet ID and idempotency key rejected;
- exact prefixes and lowercase digest enforced;
- unknown or mismatched profile rejected;
- altered nested normalization rejected;
- packet transaction `TX-1` versus idempotency transaction `TX-2` rejected;
- packet Root versus idempotency Root rejected;
- packet Root versus authority-policy Root rejected;
- packet Root versus business-object Root rejected;
- packet subject versus idempotency subject rejected;
- packet target versus idempotency target rejected;
- packet Corridor versus adapter Corridor rejected;
- packet policy version versus authority-policy version rejected;
- packet effect class `PAYMENT` versus logical class `SHIPMENT` rejected;
- altered consequential parameter with unchanged packet fingerprint rejected;
- reserved parameter-name collision rejected;
- stable logical-intent mismatch rejected;
- packet-authorization-candidate mismatch rejected;
- invalid or non-ACCEPT Root result rejected;
- wrong Root result reason, target, transaction, candidate, prior decision,
  commit, permission, FinalOutput, or effect flag rejected;
- source Root-decision ID, reference, boundary, and content-hash drift rejected;
- Registry profile label with altered rules rejected;
- rule-table mutation changes Transition Registry identity;
- self-referential invalidation identity rejected;
- invalidation source-ref substitution rejected;
- valid identity does not prove business truth.

Packet-version and idempotency tests:

- namespace-renaming, case-variant, display-name, and policy-escape bypasses
  rejected;
- packet-version prefix cannot change logical-effect identity;
- unknown logical-effect, business-object, or Corridor class rejected;
- atomic `g2a_t01` activation plus `RESERVE` reserves key to packet;
- different packet using reserved key rejected;
- same-packet non-consuming retry preserves reservation;
- valid atomic renewal transfer;
- valid atomic supersession transfer;
- transfer after consumption rejected;
- transfer after uncertainty rejected;
- arbitrary key release rejected;
- terminal receipt without consumption evidence rejected;
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

- legacy decimal `"1250.00"` normalizes to `"1250"`;
- legacy decimal `"0.50"` normalizes to `"0.5"`;
- legacy decimal `"0.0100"` normalizes to `"0.01"`;
- decimal accepts `0`, `1`, `-1`, `1.5`, `-1.5`, `0.5`, `0.01`, `-0.5`,
  `10.01`, and `-10.01`;
- decimal rejects `+1`, `01`, `00.5`, `.5`, `1.`, `1.0`, `0.10`, `-0`,
  `-0.0`, `1e3`, `NaN`, and `Infinity`;
- decimal validation uses exact Python `re.fullmatch`;
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
- `Z` and `+00:00` produce the same epoch second;
- malformed calendar date rejected;
- naive timestamp rejected;
- nonzero offset rejected;
- fractional seconds rejected;
- lexical timestamp comparison unreachable;
- current Supplier fixture timestamps convert exactly;
- current scenario-time fixtures convert exactly;
- PacketTTL inconsistency fails closed;
- terminal state not overwritten by expiry.

Transition tests:

- valid packet genesis derives `CREATED`;
- missing genesis and forged `CREATED` rejected;
- first event requires absent previous-event sentinel;
- each table row positive case;
- each unlisted transition negative case;
- rule ID and event ID are distinct concepts;
- unknown rule ID rejected;
- event with wrong component rejected;
- event with correct rule but wrong source or target rejected;
- event ID rebuilt;
- event binds exact Transition Registry ID;
- previous-event linkage enforced;
- unknown transition block;
- wrong actor block;
- missing Root decision on authority transition;
- expiry, consumption, and stale dependency require no duplicate Root decision;
- Registry cannot create revocation or supersession;
- terminal-to-active block;
- exact non-consuming retry;
- consuming-failure retry block.
- uncertain adapter outcome reaches terminal `FAILED`;
- uncertain outcome is not treated as `CONSUMED`;
- uncertain outcome is not treated as `NOT_CONSUMED`;
- uncertain outcome cannot retry or requeue;
- `FAILED_UNCERTAIN_TERMINAL` rejects every later lifecycle transition;
- `FAILED_NON_CONSUMING` provenance substitution rejected;
- same uncertain-closed key cannot be used by a new packet.

History tests:

- rebuilt transition-event identity;
- rebuilt idempotency-disposition-event identity;
- altered history, missing link, duplicate, fork, and snapshot rewrite rejected;
- altered disposition history, missing previous disposition link, duplicate,
  fork, owner substitution, and disposition downgrade rejected;
- reconciliation evidence after uncertainty is append-only;
- reconciliation creates no receipt, permission, adapter call, or effect;
- current state reconstructed;
- authorization preserved after revocation, expiry, and supersession;
- receipt preserved after invalidation;
- fake dependency accepted status rejected;
- dependency accepting Root, decision ID, and decision hash mismatch rejected;
- invalidation owning Root and accepting Root mismatch rejected;
- invalidation class/effect mismatch and partial sentinel use rejected;
- external evidence without local Root acceptance rejected;
- deterministic block outside bound policy rejected;
- revocation or supersession with foreign Root acceptance rejected;
- no deletion helper;
- no mutable history alias.

Operational-projection tests:

- every current `PermissionScopeV02` field maps exactly;
- `allowed_subjects`, `forbidden_subjects`, `allowed_actions`,
  `forbidden_actions`, `allowed_adapters`, and `forbidden_adapters` drift
  fails closed;
- `human_approval_ref`, `payment_slot_ref`, and `creditor_ref` drift fails
  closed;
- `amount` and `currency` drift fails closed;
- adapter ID, kind, version, real-adapter flag, and mock-only flag drift fails
  closed;
- Corridor packet, parent packet, adapter, amount, creditor, payment slot, and
  idempotency drift fails closed;
- receipt packet, adapter, subject, amount, currency, and idempotency drift
  fails closed;
- advisory DRS, AVF, and BSEP references create no authority.

Corridor tests:

- state, expiry, dependency, idempotency, receipt, revocation, supersession,
  and kill switch rechecked immediately before fulfillment;
- exact disposition journal and current reservation owner rechecked;
- t04 plus `CONSUME` applied as an atomic pair;
- t24 lifecycle transition applied atomically with unchanged `RESERVED`
  disposition, owner, journal bytes, and latest disposition-event ID;
- t26 plus `UNCERTAIN_CLOSE` applied as an atomic pair;
- t05 plus `RECEIPT_CONFIRM` applied as an atomic pair with exact receipt
  evidence;
- invalid packet produces zero adapter calls and no fulfillment receipt;
- uncertain adapter outcome creates no fabricated receipt and no retry;
- Corridor creates no permission and remains sole adapter owner.

Replay tests:

- recorded time for historical replay;
- injected time for present inspection;
- historical validity grants no current execution;
- expired, revoked, superseded, and consumed packet cannot execute;
- uncertain-closed packet and key cannot execute;
- reconciliation cannot reopen an uncertain event;
- exact disposition state and reservation owner reconstructed from journal;
- t24 lifecycle event and typed evidence reconstruct with byte-identical
  disposition journal, unchanged latest event ID, and unchanged `RESERVED`
  owner;
- retry eligibility is reported only for exact `FAILED_NON_CONSUMING`
  provenance and does not execute;
- Replay cannot append, transfer, release, consume, or close a disposition;
- Replay creates no packet, Root decision, receipt, consumption, or effect.

Two-domain tests:

- Airline and Supplier shapes use the generic invalidation contract;
- no domain-specific authority law;
- authority law unchanged between domains;
- Supplier MIXED and Airline evidence geometry preserved;
- real-world effects equal zero.

Dependency anti-cycle tests:

- pre-Root dependency candidate contains no current source Root decision;
- pre-Root dependency candidate contains no packet ID;
- caller cannot assert `ROOT_ACCEPTED_FOR_PACKET`;
- packet authorization candidate binds the pre-Root dependency fingerprint;
- post-Root binding binds the exact dependency candidate, Root decision, and
  packet;
- recursive dependency identity is rejected;
- wrong local Root acceptance is rejected.

Revocation and supersession anti-cycle tests:

- revocation candidate excludes the new decision ID and hash;
- supersession candidate excludes the new decision ID and hash;
- Root selects each exact pre-Root candidate;
- each accepted binding binds the exact validated Root decision;
- lifecycle transition requires the accepted binding;
- self-referential candidate is rejected;
- foreign Root binding is rejected.

Frozen Root projection tests:

- exact candidate ID exists in every required frozen Root surface;
- candidate missing from one required surface is rejected;
- candidate present in a rejected set is rejected;
- candidate, transaction, or target-Root substitution is rejected;
- GT or Post V&V context substitution is rejected;
- structurally valid result from another decision input is rejected;
- frozen Root kernel remains byte-unmodified;
- any frozen-Root bypass attempt is unreachable.

Effect Firewall projection tests:

- exact transaction, target Root, Root decision, and selected candidate bind;
- exact permission ref, allowed adapter set, allowed action set, and canonical
  subject/target Root scopes bind;
- exact EffectRequest adapter, action, and idempotency key bind;
- exact `LogicalTimeBridgeV01` tick round-trip passes;
- unrepresentable tick conversion is rejected;
- bypass of `EffectFirewallV01` is unreachable;
- no second effect path exists.

Adapter-invocation relation tests:

- exact five-code vocabulary is accepted;
- t04, t24, t26, and t05 have their exact relation codes;
- every other rule has `NO_ADAPTER_INVOCATION`;
- the removed boolean field is rejected;
- t24 and t26 perform no second adapter invocation;
- one invocation yields exactly one of t04, t24, or t26;
- t04 plus `CONSUME` is an atomic pair;
- t24 appends one lifecycle event and zero disposition events under exact
  unchanged-disposition proof;
- t26 plus `UNCERTAIN_CLOSE` is an atomic pair;
- t05 plus `RECEIPT_CONFIRM` and exact receipt evidence is an atomic pair.

t24 unchanged-disposition tests:

- t24 appends exactly one lifecycle transition event;
- t24 appends zero disposition events;
- t24 disposition remains `RESERVED`;
- t24 reservation owner remains the exact packet ID;
- t24 disposition-history bytes remain unchanged;
- t24 latest disposition-event ID remains unchanged;
- t24 carries the exact execution-attempt ID;
- t24 carries exact adapter-invocation, non-consumption, reservation-owner,
  and latest-disposition-event evidence bindings;
- t24 from `UNCLAIMED`, `CONSUMED`, or `UNCERTAIN_CLOSED` fails closed;
- t24 with wrong owner or altered disposition journal fails closed;
- t24 followed by valid retry preserves reservation and creates a new attempt
  only at the next t03;
- fabricated no-op disposition event is rejected;
- a seventh disposition-event class is rejected;
- `RESERVE` with `RESERVED -> RESERVED` is rejected;
- `RECEIPT_CONFIRM` without receipt evidence is rejected.

Renewal and disposition tests:

- `CREATED`-expired `UNCLAIMED` predecessor uses `RESERVE`;
- an `UNCLAIMED` predecessor cannot use `TRANSFER_RENEWAL` or
  `TRANSFER_SUPERSESSION`;
- every exact Branch-B `RESERVED` predecessor state is accepted only under its
  matrix row;
- renewal and supersession transfers bind exact owners and atomic bundles;
- absent successor preserves terminal predecessor ownership;
- no `RELEASE` event exists;
- transfer after `CONSUMED` or `UNCERTAIN_CLOSED` is rejected;
- a superseded predecessor cannot transfer twice;
- a new packet ID cannot bypass a closed key.

Transition-evidence tests:

- transition evidence-code set equals the selected rule's exact set;
- exactly one typed binding exists for each required code;
- missing, duplicate, unknown, wrong-hash, wrong-validator, and non-`PASS`
  bindings are rejected;
- free-form evidence ref cannot satisfy a required code;
- changed evidence-binding order is rejected.

Execution-attempt tests:

- t03 creates the canonical attempt identity;
- t04, t24, and t26 reuse the exact t03 attempt;
- t05 reuses that attempt and binds the exact receipt;
- unrelated transitions require both absence sentinels;
- caller-selected or mutable-counter attempt identity is rejected;
- changed ordinal or evaluation context is rejected;
- t04, t24, t26, and t05 attempt mismatch is rejected;
- missing t05 receipt and unrelated receipt presence are rejected.

Disposition-event field-matrix tests:

- every permitted matrix row is positive;
- every unlisted row is negative;
- all 16 fields are checked for each class and Branch-A/Branch-B row;
- wrong owner, predecessor, successor, Root ref, or cause-event order is
  rejected;
- incomplete atomic bundle is rejected;
- disposition history reconstructs exact state and owner.

Generic permission-coherence tests:

- adapter absent from allowed list is rejected;
- adapter present in forbidden list is rejected;
- action absent from allowed list is rejected;
- action present in forbidden list is rejected;
- effect present in prohibited list is rejected;
- effect absent from policy allowed list is rejected;
- Corridor absent from policy allowed list is rejected;
- business-object namespace absent from policy allowed list is rejected;
- permission ref absent from required approvals is rejected;
- empty allowed adapters, allowed actions, or required approvals are rejected;
- Root-approved candidate scope wider or narrower than packet projection is
  rejected;
- compatibility fixture that passes old validation but fails generic
  coherence is rejected.

Firewall vocabulary tests:

- raw `mock_bank_sandbox` and `bank_a_mock` are rejected by direct Firewall
  construction;
- raw `mock_supplier_a_payment_intent` and
  `mock_supplier_a_payment_order` are rejected as direct action kinds;
- `mock_bank_sandbox` maps exactly to
  `mock_adapter:mock_bank_sandbox`;
- `bank_a_mock` maps exactly to `mock_adapter:bank_a_mock`;
- `mock_supplier_a_payment_intent` maps exactly to
  `mock_action:mock_supplier_a_payment_intent`;
- `mock_supplier_a_payment_order` maps exactly to
  `mock_action:mock_supplier_a_payment_order`;
- unknown mapping, already-prefixed legacy input, and double prefix fail;
- a real adapter/action cannot be relabeled as mock;
- selected raw adapter and action must be allowed and not forbidden before
  mapping.

Permission-reference tests:

- `human_approval_ref` cannot satisfy `permission_ref`;
- `human_approval:` cannot be rewritten to `permission:`;
- missing explicit canonical permission context is rejected;
- missing `permission:` prefix is rejected;
- permission-ref mismatch across Root input, packet scope, Firewall, and
  EffectRequest is rejected;
- exact `canonical_permission_ref` is accepted while human approval remains
  evidence only.

Executable-transaction tests:

- an `ABSENT_V01` transaction packet cannot activate, build Firewall, build
  EffectRequest, obtain capability, or invoke adapter;
- explicit transaction context is required for legacy projection;
- transaction inference from payment slot, invoice, creditor, packet name,
  Root-decision-ref text, creation time, or Registry order is rejected;
- transaction mismatch at each Root, packet, Firewall, and request seam is
  rejected.

Complete Firewall and request tests:

- Firewall invocation ID equals execution-attempt ID and caller-selected
  invocation ID is rejected;
- request kind is exactly `ActionCommitPacket`; every other kind is rejected
  for this projection;
- request transaction, Root, decision, candidate, permission, adapter, action,
  scope, issued tick, expiry tick, idempotency, and mock-only fields bind
  exactly;
- wrong request field, unrepresentable time bridge, or `mock_only = false`
  fails closed;
- Firewall and request IDs are rebuilt and cannot be caller-defined.

Per-attempt Firewall tests:

- one t03 attempt creates one new Firewall invocation and private state;
- the same Firewall instance cannot serve a second attempt;
- t24 retires the old invocation without global key consumption;
- valid t24 retry creates a new attempt and new Firewall;
- old capability cannot enter a retry attempt;
- t04 creates `CONSUMED`, t26 creates `UNCERTAIN_CLOSED`, and t05 confirms
  without creating consumption;
- pre-invocation eligibility failure creates no outcome transition,
  disposition event, or capability.

Compatibility-preservation tests:

- historical Supplier fixtures still pass historical validators and retain raw
  IDs unchanged;
- raw historical IDs cannot bypass Firewall namespaces;
- exact compatibility projection passes generic G2-A validation;
- missing explicit surrounding context fails closed;
- closed packet, CorridorStep, receipt, demo, report, and evidence artifacts
  remain byte-identical.

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
Historical validators continue to receive unchanged historical values.
G2-A-specific compatibility tests separately prove the exact vocabulary,
permission, transaction, complete request, and per-attempt Firewall
projections; raw legacy identifiers never reach the frozen Firewall directly.

## 32. Living Gauntlet and Conformance Plan

Candidate Living Gauntlet act:

```text
collect_action_packet_lifecycle_gauntlet_act_v01
```

The act executes real G2-A runtime contracts and proves:

```text
stable logical intent built
packet authorization candidate accepted by Root
Root-bound packet genesis created
existing Root authorization activated
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

- exact canonical-byte and keyword-only hash invocation;
- canonical packet, idempotency, stable logical-intent,
  packet-authorization-candidate, and source Root-decision identity;
- exact frozen Root kernel/input/result validation;
- exact `RootDecisionCandidateProjectionV01` continuity through Root Review,
  Post V&V, GT, Root input, and Root result;
- exact V02 operational projection;
- canonical time and PacketTTL compatibility;
- immutable packet genesis;
- exact Transition Registry and transition-event identities;
- exact typed transition-evidence bindings and execution-attempt matrix;
- code-only Registry rule identity with non-identity explanations;
- exact adapter-invocation relation vocabulary and one-invocation outcome law;
- exact t24 lifecycle-only update with byte-identical disposition journal and
  unchanged `RESERVED` owner;
- legal transitions;
- exact `FAILED` provenance;
- unknown-transition block;
- Root-only authority changes;
- Registry non-authority;
- `RESERVED`, `CONSUMED`, and `UNCERTAIN_CLOSED` idempotency laws;
- immutable idempotency-disposition journal and atomic reservation transfer;
- complete Branch-A/Branch-B reservation matrix and six-class disposition
  field matrix;
- pre-Root dependency candidate plus post-Root packet acceptance binding;
- pre-Root revocation/supersession candidates plus accepted post-Root
  bindings;
- local Root dependency acceptance and non-self-referential invalidation;
- sole `ActionPacketEffectFirewallProjectionV01` and unchanged Gate-1
  Effect Firewall permission requirements;
- exact `mock_adapter:`/`mock_action:` native grammar and closed Supplier
  legacy vocabulary projection;
- explicit canonical permission reference and non-empty executable transaction
  continuity;
- complete frozen Firewall/EffectRequest field projection with rebuilt IDs;
- one fresh Firewall invocation and private state per execution attempt;
- per-invocation used-key state never substitutes for global disposition;
- generic permission/effect coherence;
- Corridor freshness enforcement;
- receipt non-authority;
- Replay non-execution;
- cross-domain invariance.

This is a versioned extension inside the existing conformance family. Existing
Gate-1 category IDs and results retain their meanings.

## 33. Independent Audit and Closure Boundary

This v0.1.5 preflight authorizes neither implementation nor a preflight
commit. Before the preflight commit:

- an independent contract reviewer examines this exact document;
- the independent review returns `PASS`;
- owner reviews that result and this exact document;
- owner explicitly authorizes the preflight commit.

Only after those conditions:

- owner approves scope;
- owner stages;
- owner commits;
- owner pushes;
- a later explicit implementation prompt is issued.

Codex never commits or pushes.

Future sequence:

```text
final independent contract review of v0.1.5
-> owner authorization
-> preflight commit
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

The pre-commit independent contract review is distinct from the later
implementation audit. Neither review may silently repair the artifact under
review.

The audit and checkpoint paths are created only in their separately authorized
closure pass. G2-A receives no public showcase, Package, Anchor, Replay
publication, or RC2 claim.

## 34. Definition of Done

G2-A cannot close until all conditions hold:

1. `ActionCommitPacketV02` is the sole current G2-A packet family.
2. Every identity uses canonical bytes and the exact keyword-only hash API.
3. Packet identity is rebuilt from the exact ordered 20-field profile.
4. Idempotency identity is rebuilt from the exact ordered 10-field profile.
5. Missing optional values use exact `ABSENT_V01`.
6. Stable logical intent is rebuilt from the exact ordered 9-field profile.
7. Packet authorization candidate is rebuilt from the exact ordered 18-field
   profile.
8. TTL, adapter, dependency, or policy-only changes preserve stable logical
   intent and idempotency when the consequential effect is unchanged.
9. Root selects the exact packet-authorization candidate rather than the
   logical-intent ID.
10. Root authorization binding is reconstructed with the exact frozen
    kernel, decision input, and result validator API.
11. `CREATED` is already Root-bound, non-executable, and unclaimed in the
    idempotency journal.
12. `CREATED -> ROOT_AUTHORIZED` activates existing authority and atomically
    acquires or transfers reservation without creating authority.
13. V02 operational fields cannot diverge from canonical profiles.
14. Cross-profile identifiers, Roots, scopes, Corridor, policy, effect class,
   and consequential parameters are exactly coherent.
15. Canonical decimals satisfy the exact full-match profile.
16. Legacy PacketTTL strings are parsed to epoch seconds and never compared
    lexically.
17. Idempotency namespace and allowed classes are policy-bound.
18. `UNCLAIMED`, `RESERVED`, `CONSUMED`, and `UNCERTAIN_CLOSED` remain
    distinct.
19. Idempotency disposition is reconstructed from an immutable ordered
    16-field disposition-event journal.
20. Reservation transfer is atomic, Root-bound, history-preserving, and has no
    release path.
21. Immutable packet genesis is explicit and cannot be caller asserted.
22. Transition Registry identity hashes only exact ordered machine-code rule
    records, never human explanation prose.
23. Transition-rule identity and transition-event identity remain distinct.
24. Every transition event binds the exact Transition Registry identity.
25. Every transition event binds its rule, performing component, decision
    requirement, evidence codes, reason, and fail codes.
26. Identity fields cannot change under the same profile version.
27. A pending packet can be revoked before mock fulfillment.
28. An expired packet cannot execute.
29. A revoked packet cannot execute.
30. A superseded packet cannot execute.
31. A stale mandatory dependency makes the packet non-executable.
32. Mandatory dependencies bind exact local Root acceptance.
33. Invalidation identity is non-self-referential and binds exact class,
    effect, owning Root, accepting Root, and decision provenance.
34. Accepted kill-switch evidence is deterministically enforced.
35. Consumed idempotency cannot be reused.
36. An uncertain adapter outcome terminally closes packet and key without
    being classified as consumed or non-consumed.
37. `FAILED_UNCERTAIN_TERMINAL` permits no outgoing lifecycle transition.
38. A new packet ID cannot bypass consumed or uncertain-closed logical-effect
    identity.
39. Unknown transition fails closed.
40. Registry creates no permission.
41. Registry executes no adapter.
42. Corridor remains sole adapter-handle owner.
43. Corridor recomputes executability, Registry history, disposition owner,
    and current reservation immediately before fulfillment.
44. Expiry, consumption, or uncertain closure requires no redundant Root
    decision.
45. Root is required for creation, renewal, revocation, supersession, and
    materially changed authority.
46. Transition, disposition, fulfillment, receipt, and uncertain history
    cannot be deleted or rewritten.
47. Reconciliation evidence is append-only and cannot reopen state or key.
48. Current state is reconstructable from immutable packet genesis, ordered
    transition events, ordered disposition events, invalidation evidence, and
    reconciliation evidence.
49. Prior authorization remains auditable after executability becomes false.
50. Receipt remains evidence only and cannot create consumption.
51. Replay reconstructs exact lifecycle and disposition history but cannot
    execute, reserve, transfer, consume, reopen, or create authority.
52. Airline and Supplier use one authority law.
53. Gate-1 Root, Transition Registry, and Corridor laws remain intact.
54. Focused tests pass.
55. Bounded compatibility tests pass.
56. Living Gauntlet lifecycle act passes.
57. Kernel Conformance lifecycle category passes.
58. Independent audit closes.
59. Real-world effects remain zero.
60. G2-A receives no standalone public showcase.
61. G2-A does not authorize the RC2 claim.
62. G2-B starts only after internal G2-A closure.
63. Dependency identity has no current-Root-decision self-reference.
64. Packet dependency acceptance is a separate post-Root binding.
65. Revocation candidate has no new-decision self-reference.
66. Supersession candidate has no new-decision self-reference.
67. Lifecycle invalidation transitions reference accepted post-Root bindings.
68. Every Root candidate traverses the exact frozen Root Review, Post V&V, GT,
    Root input, and Root result path.
69. Frozen `RootDecisionKernelV01` is neither bypassed nor modified.
70. `ActionPacketEffectFirewallProjectionV01` is the sole Gate-1 effect
    bridge.
71. Existing permission-state requirements remain mandatory.
72. Existing `EffectFirewallV01` remains the sole capability issuer.
73. Adapter invocation relation uses the exact five-code vocabulary.
74. t04, t24, and t26 are mutually exclusive classifications of one
    invocation.
75. `UNCLAIMED` renewal uses `RESERVE`, never transfer.
76. `RESERVED` renewal or supersession uses the exact atomic transfer.
77. `CONSUMED` and `UNCERTAIN_CLOSED` are permanent.
78. Transition-required evidence uses typed validated bindings.
79. Execution-attempt and receipt presence is rule-exact.
80. Every disposition event class has a complete 16-field matrix.
81. Generic permission coherence is enforced independently of legacy
    validation.
82. Runtime implementation remains unauthorized until independent review
    returns `PASS`.
83. Preflight commit remains unauthorized until independent review returns
    `PASS`.
84. Real-world effects remain zero throughout this correction and G2-A proof.
85. t24 appends no idempotency-disposition event.
86. t24 preserves exact `RESERVED` disposition and exact packet reservation
    owner.
87. t24 preserves byte-identical disposition history and the exact latest
    disposition-event ID.
88. t24 remains fully evidenced by its lifecycle transition and exact
    `TransitionEvidenceBindingV01` records.
89. The disposition-event class vocabulary remains exactly six; no seventh
    class exists and `RESERVE` cannot mean `RESERVED -> RESERVED`.
90. Native executable adapter IDs satisfy the frozen `mock_adapter:`
    namespace.
91. Native executable action IDs satisfy the frozen `mock_action:` namespace.
92. Legacy Supplier adapter/action IDs use only the exact closed four-row
    mapping.
93. A real or unknown identifier cannot be relabeled as mock.
94. Human approval evidence is not the Effect Firewall permission reference.
95. Canonical permission reference comes from validated Root permission state.
96. Every lifecycle-activated or executable packet has a non-`ABSENT_V01`
    transaction ID.
97. Transaction identity is continuous through Root Review, Post V&V, GT,
    Root input/result, packet, Firewall, and EffectRequest.
98. Firewall invocation ID equals execution-attempt ID.
99. Each accepted retry receives a new execution attempt and new Firewall
    instance.
100. EffectRequest request kind is exactly `ActionCommitPacket`.
101. Every EffectRequest field is exactly projected from packet, Root,
     permission, scope, time, and idempotency contracts.
102. Firewall per-invocation used-key state is not global consumption truth.
103. t24 may retry under a new Firewall invocation while global disposition
     remains `RESERVED`.
104. No old capability survives across execution attempts.
105. Historical compatibility values remain unchanged and cannot directly
     bypass frozen Firewall namespaces.
106. No second capability issuer or effect path exists.
107. Independent review `PASS` remains required before preflight commit.
108. Runtime implementation remains unauthorized.
109. Real-world effects remain zero.

## 35. Explicit Non-Claims

G2-A is:

- not runtime implementation;
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
- not PlanGraph/BSEP work;
- not a Root API replacement;
- not a second Transition Registry;
- not a second Effect Firewall;
- not a second Corridor;
- not a second packet family;
- not a second capability issuer or effect path;
- not a permission creator;
- not permission derived from human approval evidence;
- not mutation or reinterpretation of closed legacy artifact identifiers;
- not a production Registry;
- not distributed state;
- not real ticket issuance;
- not authorization to commit this preflight before independent review
  returns `PASS`.

## 36. Fail-Closed Conditions

The implementation and review stop without authority, adapter call, receipt,
or effect on:

- path-scope expansion;
- profile-version ambiguity;
- malformed canonical material;
- positional hash invocation, raw structured hash payload, or noncanonical
  identity bytes;
- missing, duplicate, reordered, or unknown profile field;
- sentinel misuse;
- non-NFC identity input after the selected normalization boundary;
- invalid decimal, integer, bool, digest, or prefix;
- packet or idempotency mismatch;
- missing or invalid stable logical intent;
- missing, substituted, or invalid packet-authorization candidate;
- logical intent changed by TTL, adapter, dependency, policy, retry, or
  Registry-only variation;
- invalid Root result, non-ACCEPT decision, wrong reason, wrong candidate,
  wrong boundary, or altered source decision projection hash;
- wrong Root kernel, substituted decision input, mismatched decision-input ID,
  or result from another decision context;
- V02 operational-field or compatibility-projection divergence;
- cross-profile identifier, Root, scope, Corridor, policy, effect-class, or
  consequential-parameter mismatch;
- unapproved idempotency namespace, logical-effect class, business-object
  namespace, or Corridor class;
- reserved consequential parameter-name collision;
- Root identity or decision mismatch;
- temporal inconsistency or ambient-time dependence;
- malformed, non-UTC, fractional, naive, lexically compared, or
  assertion-inconsistent PacketTTL time;
- unbridged logical time;
- stale, missing, replaced, contradictory, or malformed dependency;
- pre-Root dependency candidate containing current source Root decision,
  packet ID, post-Root acceptance, or caller-asserted accepted status;
- dependency acceptance binding with wrong candidate fingerprint,
  authorization candidate, source decision ID/hash, packet, owning Root,
  recursive identity, or foreign Root;
- invalid authority-policy binding;
- self-referential invalidation material, substituted invalidation source ref,
  false accepted status, invalid deterministic block, or foreign Root
  invalidation acceptance;
- invalidation owning/accepting/packet Root mismatch, class/effect mismatch,
  partial Root-decision sentinel use, or deterministic manual cancellation
  outside bound policy;
- revocation or supersession candidate containing its selecting Root decision
  or accepted-binding identity;
- accepted revocation or supersession binding with wrong pre-Root candidate,
  decision ID/hash, owning Root, packet/predecessor, prior authorization, or
  foreign Root;
- invalidation transition referencing a pre-Root candidate instead of its
  accepted post-Root binding;
- candidate missing from a required Root Review, Post V&V, GT, decision-input,
  or Root-result surface, or present in a rejected/blocked/foreign surface;
- candidate, transaction, target Root, policy, permission, temporal, conflict,
  prior-state, or decision-context substitution across the frozen Root path;
- illegal or unknown transition;
- unknown transition rule;
- missing or forged immutable packet genesis;
- lifecycle activation that creates authority, lacks existing source
  authorization, or lacks exact atomic idempotency acquisition;
- use of the obsolete pre-v0.1.3 t01 rule identifier;
- free-form prose in machine rule identity, unknown machine code, or
  Root-decision-requirement mismatch;
- Transition Registry identity or ordered-rule-table mismatch;
- transition rule/event source, target, class, component, reason, Root,
  adapter-invocation relation, or terminal-law mismatch;
- missing, duplicate, unknown, reordered, unvalidated, wrong-hash, or
  wrong-validator `TransitionEvidenceBindingV01`;
- free-form evidence ref used to satisfy a Registry-required evidence code;
- forged execution attempt, mutable attempt counter, changed ordinal/context,
  outcome attempt mismatch, receipt attempt mismatch, or rule-invalid
  attempt/receipt presence;
- caller-selected or malformed transition-event identity;
- wrong transition actor;
- missing Root decision for an authority transition;
- altered, omitted, duplicate, forked, or rewritten history;
- altered, omitted, duplicate, forked, released, downgraded, owner-substituted,
  or rewritten idempotency-disposition history;
- incomplete atomic activation, renewal, supersession, consumption, or
  uncertainty bundle;
- `UNCLAIMED` predecessor transfer, `RESERVED` successor reservation without
  transfer, second transfer from a superseded predecessor, or mismatch against
  the exact renewal/disposition matrix;
- disposition event field mismatch against its exact 16-field matrix;
- revocation or supersession;
- accepted kill-switch condition;
- consumed idempotency, uncertain-closed idempotency, wrong reservation owner,
  invalid reservation transfer or release, or terminal receipt without valid
  consumption evidence;
- `FAILED` provenance substitution or an outgoing lifecycle transition from
  `FAILED_UNCERTAIN_TERMINAL`;
- uncertain outcome classified as consumed or non-consumed;
- uncertain packet retry, requeue, key reuse, state reopening, event mutation,
  fabricated receipt, or reconciliation adapter call;
- scope expansion or adapter mismatch;
- direct raw legacy adapter supplied to EffectFirewall or raw legacy action
  supplied to EffectRequest;
- unknown legacy vocabulary mapping, double prefix, or real-to-mock relabeling;
- selected raw adapter/action not in the legacy allowed set or present in the
  legacy forbidden set;
- human approval used as `permission_ref`, inferred permission reference,
  missing canonical permission context, or `permission:` prefix mismatch;
- `transaction_id = ABSENT_V01` on an activated/executable packet, inferred
  transaction ID, or transaction mismatch across any Root/packet/Firewall/
  request seam;
- caller-selected Firewall invocation ID, invocation/attempt mismatch, reused
  Firewall instance, or reused old capability;
- wrong EffectRequest request kind or Root, candidate, permission, adapter,
  action, scope, tick, idempotency, or mock-only mismatch;
- per-invocation used-key state treated as terminal global consumption;
- compatibility source mutation;
- generic permission, adapter, action, effect, business-object, Corridor, or
  dual-containment failure;
- empty allowed adapter, allowed action, or required approval set;
- `ActionPacketEffectFirewallProjectionV01` mismatch, Effect Firewall bypass,
  second effect path, permission-state weakening, or unrepresentable
  LogicalTimeBridge projection;
- zero, repeated, or multiple result transitions for one adapter invocation;
- t24 or t26 attempting a second adapter invocation;
- t24 appending any disposition event;
- t24 changing disposition, reservation owner, latest disposition-event ID,
  or any disposition-history byte;
- t24 without exact non-consumption, invocation, reservation-owner, latest
  disposition-event, and execution-attempt evidence;
- t24 from a key not exactly `RESERVED` or under a reservation owner other
  than the packet ID;
- fabricated no-op disposition event, seventh disposition-event class,
  `RESERVE: RESERVED -> RESERVED`, or `RECEIPT_CONFIRM` without receipt
  evidence;
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

The immediate next action is final independent contract review of this exact
v0.1.5 preflight. The preflight commit and runtime implementation both remain
unauthorized until that review returns `PASS` and the owner issues the
corresponding explicit authorization. Codex does not stage, commit, or push.

After bounded G2-A implementation, tests, Gauntlet, conformance, independent
audit, internal checkpoint, and AGENTS closure complete, the next engineering
slice is G2-B. This document does not start G2-B, close Gate 2, claim RC2, or
authorize public release.
