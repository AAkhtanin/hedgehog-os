# Local DRS v0.2 After Full WOW v1.2 Preflight v01

## 1. Header

- document_id: local_drs_v0_2_after_full_wow_v1_2_preflight_v01
- document_status: PREFLIGHT
- base_head: e3f2c7e
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- payment_executed: false
- shipment_released: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false

## 2. Closed WOW v1.2 Baseline

Full WOW v1.2 live multi-LLM/fractal human story + artifact renderer is the
closed regression baseline for Local DRS v0.2.

Closed facts:

- Full WOW v1.2 deterministic product trace PASS.
- Full WOW v1.2 manual live multi-LLM/fractal real provider run PASS.
- Full WOW v1.2 human story PASS.
- Artifact-backed story renderer PASS.
- Six real Gemini semantic actors participated.
- BSEP was created and validated.
- Runtime-owned PlanGraph/local artifacts remained runtime-owned.
- 8 fractal branch cells were represented.
- 8 Branch ResultProposals were created.
- Post V&V / GT-LGT / Root boundary remained visible.
- `real_world_effects_count: 0`.
- No production/public-auditor claim.

This becomes the DRS v0.2 regression baseline because it has realistic
business trace shape: supplier context, warehouse context, legal/accounting
context, bank boundary context, lineage-worthy artifacts, stale-risk artifacts,
blockers, and Root decisions. DRS v0.2 must learn to resolve and classify those
records without turning memory into truth, permission, or final authority.

## 3. DRS v0.2 Goal

Local DRS v0.2 upgrades DRS from simple context lookup into a local
lineage/freshness/provenance/reuse/trace layer.

The target is still local proof architecture:

- local records only;
- local resolver only;
- pointer/summary-friendly records;
- explicit time and provenance;
- explicit reuse decision reports;
- Root review preserved for every consequential reuse path.

The task-provided passport interpretation is controlling for this preflight:
APIs move data, while Hedgehog DRS moves time-scoped, contract-bound,
auditable meaning. DRS stores and routes meaning records with time scope,
contract boundaries, provenance, trust/audit metadata, and Root-controlled
reuse/acceptance gates. DRS is not a replacement for APIs and does not become
authority.

The math appendix pipeline remains:

```text
I -> G -> W_t -> DRS_retrieval -> V -> AVF -> A_p -> P -> R -> Q -> GT -> F -> DRS_writeback
```

FinalOutput `F` is created only by Root.

## 4. Non-Authority Boundaries

Core invariants:

- DRS is not truth.
- DRS is not authority.
- DRS is not permission.
- DRS hit is context only.
- Reuse candidate is not direct reuse.
- AcceptedEvidence is not future action permission.
- Old receipt is not current permission.
- Old Root Final is not silently reused.
- Root remains final authority.
- DRS writeback after Root is local proof/audit only.

Operational boundaries:

- DRS may retrieve, rank, group, classify, and explain prior records.
- DRS may emit a reuse decision class and a reason table.
- DRS may require Root review.
- DRS may not create FinalOutput.
- DRS may not create ActionCommitPacket.
- DRS may not create receipt.
- DRS may not execute payment.
- DRS may not release shipment.
- DRS may not call real bank/supplier/warehouse APIs.
- DRS may not silently convert old evidence into current permission.

## 5. Time Model

Local DRS v0.2 must make time explicit before reuse is even discussed.

Required concepts:

- TimeEnvelope: required on every DRSRecordV02.
- TemporalQuery: required on every resolver call.
- Physical Time: when the record was physically created or written.
- Knowledge Time: the as-of time the content claims to represent.
- Event Time: when the business event was observed or occurred.
- Context Time: session, run, or bounded trace context.
- TTL: lifetime or expiry bound for the record.
- validity interval: interval during which the record may be considered
  applicable as context.
- freshness: classification of time fitness for current review.
- staleness: downgrade state when time fitness is weak or expired.
- source_observed_at: when a source event was observed.
- system_ingested_at: when local runtime ingested the record.

Freshness must be computed against the TemporalQuery, not by record age alone.
A newer record alone is not authority. An older accepted record may remain
useful context but must not become action permission.

## 6. Lineage and Provenance Model

Local DRS v0.2 needs explicit references, not anonymous memory blobs.

Proposed reference concepts:

- DRSLineageRef: link to prior related DRS records.
- source_refs: records or source observations used to produce this record.
- provenance_refs: broader source/proof/audit chain references.
- prior_trace_ref: trace or run that created the record.
- root_final_ref: Root final artifact reference, if any.
- artifact_ref: artifact path/hash/id reference.
- validation_ref: validator report or validation artifact reference.

Lineage explains where context came from. Provenance explains why it is
inspectable. Neither grants authority.

## 7. Reuse Decision Classes

Local DRS v0.2 should produce explicit reuse decision classes:

- context_only: record is useful context, but the normal pipeline continues.
- partial_reuse_then_validation: part of a prior trace may seed bounded
  context, but validators and Root review remain required.
- warning_only: prior record is a warning signal, not a reusable answer.
- rerun_required: changed, stale, conflicting, or high-risk facts require a
  fresh validation path.
- blocked: prior evidence or policy pressure blocks reuse for this route.
- direct_reuse_candidate: a record may be considered for shortcut review, but
  has not been allowed.
- direct_reuse_allowed: possible only after every hard gate passes and Root
  explicitly permits shortcut.

For Local DRS v0.2 after WOW v1.2, `direct_reuse_allowed` should default false
unless every hard gate passes and Root explicitly permits shortcut.

Default expected result:

- DirectReuseAllowed: false
- ContextOnly: true, or one of partial_reuse_then_validation / warning_only /
  rerun_required / blocked
- RootReviewRequired: true

## 8. Freshness / Staleness Policy

Freshness policy:

- A fresh record may be context.
- A stale record may warn but not permit.
- A newer record alone is not authority.
- Stale receipt is not permission.
- Current payment slot is not permission.
- Old Root Final is not silently reused.
- Changed facts require rerun validation.
- Expired legal/accounting records require freshness downgrade.

Freshness classes should be explicit, for example:

- fresh_context
- stale_warning
- expired_rerun_required
- changed_fact_rerun_required
- blocked_by_policy_or_conflict

## 9. Conflict / Quarantine / Deadend Pressure

Local DRS v0.2 must treat risky proximity as pressure against reuse:

- prior blocker increases warning/block pressure;
- quarantined records cannot authorize reuse;
- deadend proximity blocks or downgrades reuse;
- conflict requires rerun validation / Root review;
- contradiction pressure should route to rerun_required or blocked until a
  future ConflictCheck layer accepts a safer route.

Quarantine proximity and deadend proximity are local query-time safety signals.
They must not taint the whole graph by default, but they must prevent direct
reuse for affected candidates unless a later explicit Root-reviewed policy
allows a narrow exception.

## 10. WOW v1.2 Baseline Scenarios

Baseline scenarios for the closed Full WOW v1.2 trace:

- Supplier A prior scoped trace found -> context_only or
  partial_reuse_then_validation.
- Supplier B blocker trace found -> warning_only / blocked.
- Old receipt trace found -> context_only, not permission.
- Old shipment-held trace found -> warning / rerun_required.
- Old Root Final found -> lineage/provenance only, not silent reuse.
- Changed warehouse fact -> rerun_required.
- Stale legal/accounting evidence -> freshness downgrade.
- Bank payment slot found -> context_only; payment_slot remains not
  permission.
- Prior mock payment evidence found -> context_only, not current payment
  permission.
- Prior receipt found -> context_only; receipt is not truth and receipt does
  not release shipment.
- DRS writeback after Root -> local proof/audit only.

## 11. Proposed Implementation Slices

### Slice A — DRS v0.2 record/time/lineage model

Create local vocabulary and contracts:

- DRSRecordV02
- DRSLineageRef
- DRSFreshnessEnvelope
- DRSReuseDecision
- DRSResolveReport

### Slice B — local resolver/reuse decision report

Create a local resolver over records with:

- freshness table;
- lineage table;
- provenance table;
- reuse decision table;
- direct_reuse_allowed reasons;
- root_review_required.

### Slice C — WOW v1.2 baseline integration

No new demo. Add a DRS v0.2 resolve section to the closed WOW v1.2 baseline:

- prior trace found;
- prior trace classified as context;
- stale/current facts marked;
- validation rerun required where facts changed;
- Root remains final authority.

### Slice D — adversarial/stale/quarantine/deadend tests

Expected adversarial coverage:

- stale record not permission;
- old receipt not action permission;
- prior Root Final not silently reused;
- quarantine proximity blocks direct reuse;
- deadend proximity blocks or downgrades reuse;
- changed facts require rerun validation;
- lineage refs preserved.

### Slice E — audit/docs sync

Expected closure artifacts:

- auditor_drs_v0_2_local_lineage_reuse_v01.log
- README / AGENTS / specs / manifest update

## 12. Required Future Tests

Expected tests:

- drs_hit_is_context_not_authority
- stale_record_not_permission
- old_receipt_not_action_permission
- prior_root_final_not_mutated
- lineage_refs_preserved
- freshness_envelope_required
- temporal_query_required
- direct_reuse_default_false
- changed_facts_require_rerun_validation
- quarantine_blocks_direct_reuse
- deadend_blocks_or_downgrades_reuse
- root_review_required_for_reuse_decision

## 13. Explicit Non-Goals

- no production DRS
- no global/external DRS
- no external DRS network
- no vector DB
- no embeddings requirement
- no real connectors
- no AVF v0.2 implementation
- no ActionCommitPacket hardening
- no Airline demo
- no Privacy demo
- no Finance Kill-Switch demo
- no Vendor onboarding demo
- no Marennya
- no UP
- no NeedleFactory
- no direct action
- no permission grant
- no bypass of Root
- no production/public-auditor claim

## 14. Required Formula

DirectReuseAllowed(r, TQ) =

```text
RootShortcutAllowed
and TimeEnvelopePresent
and TemporalQueryPresent
and TemporalHardGate
and PolicyOK
and ConflictOK
and QuarantineProximityOK
and DeadEndProximityOK
and PermissionOK
and ReuseScore >= tau
```

For Local DRS v0.2 after Full WOW v1.2:

- DirectReuseAllowed: false by default.
- ContextOnly: true for ordinary safe context records.
- RootReviewRequired: true for reuse decisions.
- partial_reuse_then_validation may seed bounded context only.
- warning_only may inform Root but not authorize.
- rerun_required is expected for changed or stale facts.
- blocked is expected for Supplier B blocker trace or quarantine/deadend
  pressure.

## 15. Selected Path

Selected path: Option A — implement DRS v0.2 Slice A record/time/lineage model
first.

Reason:

Slice A creates the vocabulary and local contracts needed before
resolver/integration/adversarial tests. Without DRSRecordV02, DRSLineageRef,
DRSFreshnessEnvelope, DRSReuseDecision, and DRSResolveReport, later resolver
behavior would either be ad hoc or would smuggle authority into loosely shaped
memory records.

## 16. Next Immediate Implementation After Preflight

If this preflight is accepted, create Slice A in a narrow runtime/test patch.
Candidate allowed future files, proposed only and not created here:

- hedgehog/drs_v02.py or hedgehog/local_drs_v02.py
- tests/test_drs_v02_local_lineage_reuse.py

Initial Slice A should remain local and deterministic:

- no provider/network/Gemini calls;
- no production DRS;
- no global/external DRS;
- no real connectors;
- no AVF v0.2 implementation;
- no ActionCommitPacket hardening;
- no new business domain.

## 17. Final Preflight Status

- selected_option: Option A
- selected_slice: Slice A
- preflight_status: PASS
- docs_only: true
- planning_only: true
- runtime_modified: false
- tests_modified: false
- schemas_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- action_commit_packet_created: false
- receipt_created: false
- payment_executed: false
- shipment_released: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false
