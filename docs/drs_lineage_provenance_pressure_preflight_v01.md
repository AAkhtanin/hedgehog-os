# DRS Lineage / Provenance Pressure v0.1 - Read-only Preflight

## 1. Status

* preflight_id: drs_lineage_provenance_pressure_preflight_v01
* preflight_status: COMPLETE
* latest_checkpoint_commit: c1f0abd
* roadmap_layer: DRS Lineage / Provenance Pressure v0.1
* repair_started: false
* proof_started: false
* runtime_modified: false
* schemas_modified: false
* tests_modified: false
* production_drs_implemented: false
* external_drs_implemented: false
* full_suite_green_claimed: false
* production_ready_claimed: false
* public_auditor_ready_claimed: false

## 2. Scope

This is a read-only preflight. It does not create lineage runtime, does not
modify DRS schemas, does not implement production DRS, and does not create a
proof runner yet.

The preflight inspected existing docs, schemas, deterministic proof runners,
focused tests, and audit summaries for lineage and provenance surfaces. It did
not run full pytest, did not edit runtime, did not edit schemas, did not edit
tests, did not edit demos, did not create an audit log, and did not touch local
`_audit_exports/` evidence.

## 3. Roadmap Placement

* Previous closed layer: Long-lived DRS TTL / Aging Stress v0.1.
* Repair checkpoint: Full Suite Drift Repair Phase 1.
* Current layer: DRS Lineage / Provenance Pressure v0.1.
* Next later layer: Compromised Upstream / Economic Adversary Pack v0.1.

This layer follows the TTL aging proof because long-lived memory pressure is
not only age pressure. It is also ancestry, bridge, provenance, conflict,
quarantine, and deadend pressure.

Core rule for this layer:

```text
lineage informs
lineage does not decide
provenance does not become truth
```

## 4. Existing Lineage/Provenance Surfaces

Observed active schema surfaces:

| surface | observed location | fields / semantics found | preflight interpretation |
| --- | --- | --- | --- |
| DRS provenance | `schemas/drs_record.schema.json` | required `provenance` with `request_id`, `created_by`, `trace_refs` | Active DRS records require provenance and trace refs. |
| DRS trace refs | `schemas/drs_record.schema.json` | top-level `trace_refs` array | Active records can carry direct trace references outside provenance. |
| DRS source refs | `schemas/drs_record.schema.json` | top-level `source_refs` array of `ProvenanceRef` | Active records can reference sources, but do not define pressure semantics. |
| TraceRef | `schemas/common.schema.json` | `trace_id`, optional `span_id`, optional `kind` | Generic trace reference primitive exists. |
| ProvenanceRef | `schemas/common.schema.json` | `source`, optional `source_id`, optional `trace_ref` | Source can be `user`, `system`, `needle`, `local_drs`, `external_drs`, `fallback`, `executor`, or `validator`. |
| EvidenceItem | `schemas/common.schema.json` | `kind`, `summary`, optional `ref_id`, optional `confidence` | Evidence can point to supporting records without becoming authority. |
| ResultProposal trace refs | `schemas/result_proposal.schema.json` | required `trace_refs`; evidence array of `EvidenceItem` | Executor output can carry trace and evidence references. |
| FinalOutput trace refs | `schemas/final_output.schema.json` | optional `trace_refs`, `used_proposals`, `gt_report_ref`, `drs_writes` | Root final artifacts can cite upstream proposals and trace refs. |
| GTReport refs | `schemas/gt_report.schema.json` | candidate ids, winner, mix, ratings, candidate_scores | GT can select/advice over candidates but is not final authority. |
| CandidateVector provenance refs | `schemas/candidate_vector.schema.json` | `provenance_refs` found by scan | Candidate vectors can retain provenance references. |

Observed proof-local and documentation surfaces:

| surface | observed location | fields / semantics found | preflight interpretation |
| --- | --- | --- | --- |
| typed lineage edges | `demo/run_typed_drs_lineage_edges.py`, `tests/test_typed_drs_lineage_edges_runner.py` | `typed_edges` with `derived_from`, `same_trace`, `warns_against`, `blocked_by_policy`, `requires_user`, `degraded_from`, `supports`, `contradicts` | Typed lineage exists as LocalDRS proof-local content; it is query-time signal only. |
| graph lineage links | `demo/run_drs_graph_proximity.py` | `source_refs`, lineage links, query-time graph distance, graph proximity | Query-time graph proximity exists and does not override policy. |
| quarantine/deadend proximity | `demo/run_drs_graph_proximity.py`, `demo/run_applied_drs_retrieval_reuse.py`, TTL aging proof | `quarantine_proximity`, `deadend_proximity`, nearby quarantine/deadend routing roles | Prior proofs cover blocking/warning behavior, not unified lineage pressure. |
| applied reuse provenance | `demo/run_applied_drs_retrieval_reuse.py` | `source_record_id`, `source_domain`, `target_domain`, `direct_reuse_allowed=false`, `root_review_required=true` | Reuse candidates carry source/target fields and remain review-bound. |
| ConflictCheck links | `demo/run_conflictcheck.py` | `ConflictCandidatePair`, `ConflictReport`, `root_review_required`, `reuse_block_recommended`, `quarantine_review_recommended` | ConflictCheck can flag provenance pressure but remains advisory. |
| audit hash-chain links | `demo/run_audit_hash_chain.py` | `previous_entry_hash`, `entry_hash`, `source_artifact_type`, `source_artifact_id`, `chain_continuity_valid` | Hash-chain continuity exists and explicitly does not decide truth. |
| bridge traversal | `demo/run_cross_domain_drs_bridge_v01.py` | bridge registry, traversal request, traversal steps, boundary matrix, source/target domains | Cross-domain bridge can inform but cannot decide, finalize, execute, or transfer authority. |
| external pointer protocol | `demo/run_external_drs_pointer_protocol_v01.py`, docs/audit summaries | pointer candidates, no accepted external pointer, no global/external DRS write | External pointer semantics exist as proof-level pointer protocol, not external/global DRS. |
| external evidence acceptance | `demo/run_external_evidence_acceptance_gate_v01.py`, audit summaries | ConnectorObservation -> EvidenceCandidate -> ValidationPacket -> RootDecision -> AcceptedEvidence | AcceptedEvidence is Root-created and bounded; it is not truth/action/DRS write. |
| DRS lifecycle records | `demo/run_drs_lifecycle_semantics.py`, docs/audit summaries | completed, degraded, blocked, failed, rejected, quarantined, deadend, promotion_candidate | Lifecycle surfaces exist, but lineage pressure across them is not unified. |
| parent/child boundaries | Fractal Cell / live child proof docs and tests | ChildBoundarySnapshot, child/parent references | Child outputs are boundary evidence, not final truth or authority. |
| artifact vocabulary | artifact_type Mapping docs/specs | `artifact_type`, `source_artifact_type`, `EvidenceItem.kind`, `TraceRef.kind`, lifecycle/status axes | Vocabulary clarifies metadata axes but does not implement pressure logic. |

Representability check:

| target pressure | existing artifacts that can represent it | current limitation |
| --- | --- | --- |
| trace derived from trace | `trace_refs`, `source_refs`, typed `derived_from`, audit hash-chain entries | No unified lineage pressure scenario combining trace ancestry and reuse outcome. |
| reuse derived from accepted evidence | Applied DRS retrieval candidates, External Evidence Acceptance Gate AcceptedEvidence, TTL aging AcceptedEvidence boundary | No proof specifically combines old AcceptedEvidence ancestry with direct reuse pressure. |
| bridge traversal across domains | Cross-domain DRS Bridge registry/request/steps/result | Existing bridge proof is isolated and not combined with reuse/TTL/provenance pressure. |
| quarantine proximity | DRS graph proximity, typed `contradicts`, applied reuse quarantine candidate, TTL bounded proximity | Covered in pieces, not as lineage/provenance pressure over ancestry. |
| deadend proximity | DRS graph proximity, applied reuse deadend candidate, ConflictCheck completed/deadend and protocol/deadend conflicts | Covered in pieces, not as pressure table for derived traces. |
| conflicting provenance | ConflictCheck reports, External Evidence Acceptance Gate rejected/quarantined evidence, typed `contradicts` | Conflict is advisory; no dedicated provenance-pressure proof runner yet. |

Active schemas are sufficient for a deterministic proof-local runner that uses
existing generic fields (`trace_refs`, `source_refs`, `provenance`,
EvidenceItem `ref_id`, ResultProposal `trace_refs`, audit hashes). Active
schemas are not sufficient for a production lineage-pressure runtime or a
first-class schema-defined lineage-pressure object. This layer should therefore
start proof-local only.

## 5. Candidate Pressure Scenarios

Proposed future proof scenarios:

| scenario | input shape | expected query_state / outcome | authority boundary | why Root remains required |
| --- | --- | --- | --- | --- |
| trace_derived_from_trace_informs_only | Local records with `trace_refs`, `source_refs`, and typed `derived_from` from prior trace to candidate trace | `context_only` or `fresh_candidate_for_review`; no direct final reuse by lineage alone | Lineage may raise ranking/context but cannot pass hard gates alone | Root must decide whether derived trace evidence is usable in current context. |
| reuse_candidate_derived_from_old_accepted_evidence_requires_review | Reuse candidate points to old Root-created AcceptedEvidence and a current TemporalQuery | `rerun_required` or `partial_reuse_then_validation`; direct reuse blocked unless all current gates pass | AcceptedEvidence ancestry is bounded evidence, not future action permission | Root must recheck freshness, permission, policy, and action boundary. |
| bridge_traversal_across_domain_informs_only | Certificate-domain bridge traversal informs travel-domain target | `warning_only` or `context_only`; target not finalized by traversal | Bridge traversal can inform but cannot transfer authority | Root in the target domain must review and decide. |
| quarantine_near_reuse_candidate_warns_or_blocks | Candidate has source_refs or typed edge near quarantine record | `blocked_by_quarantine_proximity` or `warning_only` depending threshold | Quarantine proximity can warn/block but cannot globally taint graph | Root review is required for quarantine release/override. |
| deadend_near_reuse_candidate_warns_or_blocks | Candidate has source_refs or typed edge near deadend record | `blocked_by_deadend_proximity` or `warning_only` depending threshold | Deadend proximity can warn/block route reuse but cannot become authority | Root must decide whether a route remains viable or needs rerun. |
| conflicting_provenance_blocks_direct_reuse | ConflictCheck candidate pair: same subject/claim with incompatible provenance | `blocked_by_conflict`; direct reuse false | ConflictCheck recommends; it does not decide truth or mutate DRS | Root must resolve truth/commit/invalidation/reuse. |
| trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize | Newer high-authority accepted record references older work and includes replacement reason | `rerun_required` or `supersession_review_required`; no self-authorized replacement | Provenance and trust class may request review, not direct supersession | RootAcceptedForSupersession remains required. |
| audit_hash_continuity_does_not_create_truth | Audit chain has valid previous/entry hashes over source artifacts | `historical_evidence` or `audit_continuity_only` | Audit/hash-chain proves continuity, not truth | Root must still assess current truth/action/use. |
| high_reuse_lineage_does_not_create_authority | Candidate has many reuse descendants and high ReuseScore/ReuseBoost | `context_only` or `partial_reuse_then_validation`; direct reuse blocked if hard gate fails | Popularity and lineage preserve visibility/ranking only | Root and hard gates decide direct reuse. |
| root_final_authority_preserved_across_lineage_pressure | Composite scenario with derived trace, bridge, quarantine, deadend, conflict, and audit links | PASS only if Root final authority is preserved and no non-Root artifact decides | All pressure surfaces remain advisory or blocking signals | Root remains final authority for final output, reuse, override, and commit. |

## 6. Required Invariants

* lineage informs, lineage does not decide
* provenance does not become truth
* provenance does not create authority
* audit/hash-chain proves continuity, not truth
* DRS lineage cannot authorize direct reuse by itself
* accepted evidence ancestry is not future action permission
* bridge traversal is not external/global DRS
* quarantine proximity can warn/block but cannot globally taint the graph
* deadend proximity can warn/block but cannot globally taint the graph
* ConflictCheck remains advisory until Root
* GT remains advisory/selection
* Root remains final authority

Related current-stage guardrails to preserve:

* DRS retrieval is not direct reuse.
* ReuseScore / ReuseBoost / graph proximity are ranking or visibility signals,
  not authority.
* EvidenceItem.kind and artifact_type are classification metadata, not truth.
* ExternalDRSPointer is a pointer/reference, not external/global DRS write.
* AcceptedEvidence is bounded evidence, not ready status, action permission,
  DRS write, or installed Needle.

## 7. Likely Implementation Strategy For Future Proof

Recommended future proof files, not created in this preflight:

* `demo/run_drs_lineage_provenance_pressure_v01.py`
* `tests/test_drs_lineage_provenance_pressure_v01_runner.py`

Future proof shape:

* Local deterministic Python only.
* Standard-library data structures or dataclasses.
* Fixed local records and queries, no real connector.
* Reuse active schema field names where useful: `trace_refs`, `source_refs`,
  `provenance`, EvidenceItem `ref_id`, `previous_hash`, `entry_hash`.
* Keep pressure semantics proof-local unless a separate schema patch plan is
  approved.
* Produce a scenario table with expected query_state/outcome, direct reuse
  decision, authority boundary, and reason codes.
* Derive PASS from scenario results, not hardcoded PASS text.

The future proof must not:

* implement production DRS
* implement external/global DRS
* call network
* call Gemini
* activate Marennya
* activate UP
* mutate schemas unless separately approved
* install Needle
* execute external actions

## 8. Gaps Found

Supported gaps from inspected files:

| gap_id | evidence | risk | recommended next action |
| --- | --- | --- | --- |
| gap_lineage_pressure_unified_proof | Typed lineage, graph proximity, bridge traversal, applied reuse, ConflictCheck, audit hash-chain, and TTL aging exist as separate proofs. | Reviewers can see the pieces but not a single pressure scenario across ancestry, provenance, quarantine/deadend, bridge, conflict, and audit. | Create DRS Lineage / Provenance Pressure v0.1 Patch Plan. |
| gap_schema_first_class_pressure_object | Active schemas provide `trace_refs`, `source_refs`, `provenance`, EvidenceItem refs, and hashes, but no first-class lineage pressure schema. | Runtime/schema implementation would be premature and could overfit proof semantics. | Keep first proof proof-local; defer schema patch plan. |
| gap_old_accepted_evidence_ancestry | TTL aging and External Evidence Acceptance Gate state AcceptedEvidence limits; applied reuse has source record links. | Old AcceptedEvidence ancestry is not yet stress-tested as lineage pressure. | Add scenario `reuse_candidate_derived_from_old_accepted_evidence_requires_review`. |
| gap_bridge_plus_reuse_pressure | Cross-domain bridge proof is isolated and informs only; applied reuse has source/target domains. | Bridge traversal could be misunderstood as provenance laundering or authority transfer. | Add bridge traversal scenario in pressure proof. |
| gap_quarantine_deadend_lineage_pressure | Existing proofs block quarantine/deadend reuse, but not in one composite ancestry pressure runner. | Nearby bad lineage could be overtrusted or globally over-tainted. | Add bounded proximity scenarios with no global taint. |
| gap_conflicting_provenance_pressure | ConflictCheck covers many pair types; typed `contradicts` is proof-local and advisory. | Conflicting provenance could be mistaken for auto-truth or auto-invalidation. | Add conflicting provenance scenario that blocks direct reuse and requires Root. |
| gap_audit_continuity_pressure | Audit hash-chain proves continuity, not truth, but is not combined with lineage pressure. | A valid chain could be misread as current truth. | Add audit continuity scenario. |
| gap_no_production_graph_traversal | Existing graph/proximity proofs are LocalDRS deterministic; no production persistent graph traversal exists. | A future implementation could accidentally imply production graph authority. | Keep non-goals explicit and require bounded proof before runtime. |

No gap was found requiring immediate runtime, schema, test, demo, README,
AGENTS, manifest, or audit-log modification in this preflight.

## 9. Recommended Next Patch

Recommended next patch:

DRS Lineage / Provenance Pressure v0.1 Patch Plan

The patch plan should define the future proof runner and scenario table before
any proof implementation. It should specify local records, local queries,
reason codes, expected query states, authority boundaries, and validation
commands.

Do not start the proof runner before the patch plan is reviewed.

## 10. Non-goals

* no production DRS
* no external/global DRS
* no real connector trust
* no network
* no Gemini
* no Marennya
* no UP
* no Negative Trace
* no auto-governance
* no manifest hardening
* no transition matrix mutation
* no installed Needle
* no production persistence
* no broad schema rewrite
* no full pytest run in preflight

## 11. Inspected Source Summary

Read-only scans inspected:

* roadmap/status docs: `README.md`, `AGENTS.md`, `specs/human_passport_v0_25.md`,
  `specs/machine_manifest_v0_25.json`, `specs/invariants.md`,
  `specs/demo_scenario.md`, `specs/demo_baseline_v0_25.md`,
  `specs/math_appendix_v0_3.md`, `specs/schema_package_v0_25_reference.md`
* active schemas: `schemas/drs_record.schema.json`,
  `schemas/common.schema.json`, `schemas/result_proposal.schema.json`,
  `schemas/final_output.schema.json`, `schemas/gt_report.schema.json`,
  `schemas/candidate_vector.schema.json`
* relevant proof runners/tests discovered by `rg`: typed DRS lineage edges,
  DRS graph proximity, applied DRS retrieval/reuse, cross-domain DRS bridge,
  ConflictCheck, audit hash-chain, External DRS pointer protocol, External
  Evidence Acceptance Gate, DRS lifecycle semantics, and Long-lived DRS TTL
  Aging Stress

Important read-only observation:

The repository already has many lineage and provenance ingredients. The next
layer should pressure-combine them without letting any one surface become
authority.
