# Real Local DRS Resolver / Writeback v0.1 — Preflight

## 1. Current Checkpoint

* preflight_id: real_local_drs_resolver_writeback_preflight_v01
* preflight_status: COMPLETE
* current_head_before_layer: 1e1afe6
* roadmap_block: Real Semantic Runtime MVP
* starts Real Semantic Runtime MVP
* follows STOP PROOF-ONLY EXPANSION GATE
* runtime_modified: false
* schemas_modified: false
* tests_modified: false
* demos_modified: false
* proof_started: false
* audit_started: false
* human_walkthrough_started: false

This preflight starts the first runtime-facing layer after the general plan
runtime gate. It inspects existing DRS runtime, schema, proof, and test assets
before any patch plan or implementation.

## 2. Purpose

Real Local DRS Resolver / Writeback v0.1 starts the local semantic runtime
primitive:

```text
write meaning
resolve meaning
reuse under Root review
```

The purpose is to turn existing proof/demo DRS memory behavior into a bounded
local runtime primitive that can write semantic records, resolve candidate
records, and expose reuse candidates for Root review. This layer must preserve
the existing architecture rule that memory can inform the runtime but cannot
become truth, authority, action permission, or final output authority.

## 3. Non-goals / Boundaries

This preflight does not implement anything. The future layer also must preserve
these boundaries unless a later reviewed patch explicitly changes scope:

* no production DRS
* no external/global DRS
* no network
* no Gemini
* no autonomous action
* no connector side effects
* no public WOW
* no whitepaper/public auditor packet
* no Marennya/UP
* no self-modifying manifest
* no transition matrix mutation
* no DRS poisoning resistance layer implemented separately unless folded as acceptance criteria

This preflight does not create the Real Semantic Runtime MVP as complete. It
only identifies the first local runtime primitive needed to begin that block.

## 4. Existing Assets Found

Relevant runtime/data structure assets:

| Asset | Observed role | Preflight interpretation |
| --- | --- | --- |
| `hedgehog/drs.py` | Defines `LocalDRS`, DRS layers, required fields, sensitive-key rejection, pointer validation, file-backed `write_record`, `read_record`, `read_layer`, and `query_records`. | This is the primary existing runtime seam. It is already local, bounded, and file-backed by default. |
| `hedgehog/reuse_gate.py` | Computes deterministic freshness, GT trust, policy, conflict, reuse score, and candidate decision. `evaluate_reuse_candidates` returns `direct_reuse_candidate` or `context_only`, with `reused_record_ids` empty. | This is an existing advisory candidate scorer, not Root authority. |
| `hedgehog/time_model.py` | Provides `make_time_envelope()` and `make_temporal_query()`. | Existing TimeEnvelope / TemporalQuery helpers should be reused for local runtime tests. |
| `hedgehog/external_drs/record.py`, `hedgehog/external_drs/resolver.py`, `hedgehog/external_drs/index.py` | Present but empty. | External/global DRS is not implemented and should remain out of scope. |

Relevant schema assets:

| Asset | Observed role | Preflight interpretation |
| --- | --- | --- |
| `schemas/drs_record.schema.json` | Strict Local DRS Record schema with required `record_id`, `layer`, `type`, `domain`, `content`, `time_envelope`, `provenance`, `status`; optional pointer, GT, validation, hash, previous_hash, trace_refs, source_refs; `additionalProperties: false`. | Sufficient for a v0.1 local resolver/writeback proof if semantic metadata is placed inside existing allowed objects. No schema change is required by preflight. |
| `schemas/time_envelope.schema.json` | Defines DRS temporal envelope shape used by `DRSRecord`. | Runtime-facing resolver must continue requiring time-aware records. |
| `schemas/common.schema.json` | Defines shared IDs, TraceRef, ProvenanceRef, domains, and common primitive refs. | Existing provenance and trace vocabulary can support the first local resolver proof. |

Relevant focused tests:

| Asset | Existing coverage | Remaining gap |
| --- | --- | --- |
| `tests/test_drs_runtime.py` | Tests LocalDRS write/read/schema validation, pointer validation, sensitive-key rejection, duplicate write idempotence, same id/different content rejection, TimeEnvelope requirement, TemporalQuery requirement, and layer separation. | Does not yet test semantic resolution or Root-reviewed reuse candidates as one runtime primitive. |
| `tests/test_drs_writeback_from_root_final_runner.py` | Tests proof-only writeback from Root Final artifacts. | Writeback is audit/proof-local and not a reusable runtime resolver primitive. |
| `tests/test_applied_drs_retrieval_reuse_runner.py` | Tests applied retrieval/reuse candidates, stale/quarantine/deadend/wrong-domain/permission boundaries. | Candidate logic is proof-level, not a reusable local resolver/writeback module. |
| `tests/test_long_lived_drs_ttl_aging_stress_v01_runner.py` | Tests TTL, aging, stale record, old AcceptedEvidence, quarantine/deadend, and Root shortcut boundaries. | Does not create a runtime resolver/writeback seam. |
| `tests/test_drs_lineage_provenance_pressure_v01_runner.py` | Tests lineage/provenance pressure across 10 scenarios. | Pressure remains proof-local and not a runtime resolver. |
| `tests/test_compromised_upstream_pack_v01_runner.py` | Tests compromised upstream source boundaries. | Source compromise pressure is not yet folded into local resolver acceptance criteria. |

Relevant proof/demo assets:

| Asset | Existing behavior |
| --- | --- |
| `demo/run_drs_writeback_from_root_final.py` | Proof-only local audit writeback from valid RootFinal artifacts; blocks raw upstream inputs, malicious DRS write claims, production persistence claims, and action claims. |
| `demo/run_applied_drs_retrieval_reuse.py` | Proof-only DRS retrieval/reuse candidates across warehouse/certificate/stale/quarantine/deadend/wrong-domain/permission scenarios. |
| `demo/run_drs_lifecycle_semantics.py` | Proof-only DRS lifecycle semantics for completed, degraded, blocked, failed, rejected, quarantined, deadend, and promotion candidate records. |
| `demo/run_long_lived_drs_ttl_aging_stress_v01.py` | Proof-only long-lived DRS TTL/aging stress with stale record and Root review rules. |
| `demo/run_drs_lineage_provenance_pressure_v01.py` | Proof-only lineage/provenance pressure showing lineage informs and does not decide. |
| `demo/run_compromised_upstream_pack_v01.py` | Proof-only compromised upstream pack showing sources, schema-valid content, pointers, ValidationPacket, EvidenceCandidate, and AcceptedEvidence do not become truth or authority. |
| `demo/run_root_final_from_gt_decision.py` | Root Final proof boundary showing Root creates final artifacts from GTDecision, not from raw upstream artifacts. |
| `demo/run_semantic_reuse_pipeline.py` and `demo/run_root_semantic_reuse_*` | Proof-only semantic reuse pipeline and Root review/gate/final traces. |
| `demo/run_reuse_score.py` | Advisory LocalDRS reuse score proof; score is not Root, policy, or ReuseGate. |

Relevant roadmap/status docs:

| Asset | Observed role |
| --- | --- |
| `README.md`, `AGENTS.md`, `specs/human_passport_v0_25.md`, `specs/machine_manifest_v0_25.json` | Current checkpoint identifies STOP PROOF-ONLY EXPANSION GATE and the Real Semantic Runtime MVP block. |
| `specs/invariants.md` | Records architecture invariants for DRS, reuse, Root authority, and non-authority of memory signals. |
| `docs/*_preflight_v01.md` | Existing pattern for read-only preflight docs. |

## 5. Proposed Implementation Seam

The smallest safe runtime-facing seam for v0.1 is a local resolver/writeback
primitive that composes the existing file-backed `LocalDRS` instead of
creating an unrelated store.

Recommended seam for the future patch plan:

* Use `LocalDRS` as the persistence boundary for local test/runtime records.
* Use temporary/local test paths in focused tests to avoid production
  persistence claims.
* Add a narrow resolver/writeback module only after patch-plan review. A likely
  location is a small `hedgehog/` runtime module that composes `LocalDRS`,
  `time_model`, and existing advisory reuse scoring rather than changing
  RootOrchestrator behavior in v0.1.
* Keep semantic matching deterministic and structured. For v0.1, this can be
  exact or token-set matching over explicit `domain`, `content`, `trace_refs`,
  `source_refs`, TimeEnvelope, lifecycle status, and provenance fields.
* Expose reuse as candidate output only. A DRS hit or high score must not create
  action permission or final output.

Expected primitive shape:

1. Write semantic record.
2. Preserve provenance/source/context.
3. Resolve candidate records by semantic query/context.
4. Expose reuse candidates only as candidates.
5. Require Root review before reuse affects final output.
6. Mark stale, quarantined, deadend, and contradictory records as
   review-forcing, not authority.

File-backed `LocalDRS` is favored over a pure in-memory store because it already
exists, is covered by focused tests, preserves layer separation, rejects
dangerous fields, requires TimeEnvelope, and gives writeback behavior a real
local boundary. An in-memory fixture can still be used inside tests only if it
is implemented as a temporary `LocalDRS` root path or a thin test helper.

## 6. Required Invariants

The future patch plan and proof must preserve these invariants:

* DRS record is not truth
* DRS hit is not authority
* DRS reuse candidate is not action permission
* DRS freshness is advisory, not final authority
* stale DRS record cannot silently reuse
* quarantined/deadend proximity forces review
* conflicting provenance blocks direct ready/reuse
* Root remains final authority
* resolver cannot mutate manifest
* resolver cannot mutate transition matrix
* resolver cannot call network/Gemini/connectors
* writeback cannot create production persistence claims

Additional boundary constraints:

* Local writeback records Root-reviewed semantic outcomes only.
* Local resolve returns candidates, review states, and reason codes, not final
  actions.
* Direct reuse remains blocked in the first proof unless a future Root-reviewed
  gate explicitly approves it under a separate reviewed scope.
* GT / LGT and ReuseScore remain advisory/selection layers.

## 7. DRS Poisoning Gate Folded Into Acceptance Criteria

Because this layer begins real write/resolve/reuse behavior, basic
anti-poisoning guardrails must be acceptance criteria for v0.1:

* duplicate/spam records cannot become authority
* compromised/stale/upstream-looking records cannot become truth
* repeated external pointer cannot become trust
* schema-valid DRS record cannot become semantic truth
* accepted historical evidence cannot become future action permission
* poisoning pressure can force Root review/quarantine, not reuse

This is not the separate DRS Poisoning Resistance v0.1 layer. It is the minimum
guardrail needed so the first local resolver/writeback primitive does not
weaken the already closed Compromised Upstream and DRS Lineage boundaries.

## 8. Proposed Proof Scope For Next Step

The next patch plan should define a deterministic focused proof runner. It
should not be implemented in this preflight.

Expected future proof scenarios:

1. `write_then_resolve_semantic_record_candidate_only`
2. `stale_record_forces_root_review`
3. `quarantine_proximity_blocks_direct_reuse`
4. `changed_worldstate_blocks_old_reuse`
5. `conflicting_provenance_blocks_reuse`
6. `duplicate_poisoning_pressure_does_not_create_authority`
7. `root_review_required_before_reuse_affects_final_output`
8. `writeback_records_root_final_without_action_side_effects`

Suggested future proof output:

* local writeback table
* local resolve query table
* candidate table
* stale/quarantine/deadend/conflict/poisoning reason table
* Root review boundary table
* aggregate counters
* final PASS/FAIL line

## 9. Proposed Counters For Future Proof

Proposed counters:

* records_written_count
* resolve_queries_count
* candidates_returned_count
* direct_reuse_allowed_count: 0
* root_review_required_count
* stale_record_reuse_blocked_count
* quarantine_reuse_blocked_count
* conflicting_provenance_blocked_count
* poisoning_pressure_authority_claimed_count: 0
* manifest_mutation_count: 0
* transition_matrix_mutation_count: 0
* production_drs_used_count: 0
* external_drs_used_count: 0
* network_used_count: 0
* gemini_used_count: 0
* root_final_authority_preserved_count

Suggested PASS conditions:

* records_written_count is greater than 0.
* resolve_queries_count is greater than 0.
* candidates_returned_count is greater than 0.
* direct_reuse_allowed_count == 0.
* root_review_required_count is greater than 0.
* stale_record_reuse_blocked_count is greater than 0.
* quarantine_reuse_blocked_count is greater than 0.
* conflicting_provenance_blocked_count is greater than 0.
* poisoning_pressure_authority_claimed_count == 0.
* manifest_mutation_count == 0.
* transition_matrix_mutation_count == 0.
* production_drs_used_count == 0.
* external_drs_used_count == 0.
* network_used_count == 0.
* gemini_used_count == 0.
* root_final_authority_preserved_count equals the future scenario count.

## 10. Risks / Decisions Needed

Implementation choices for the patch plan:

| Decision | Observed facts | Preflight recommendation |
| --- | --- | --- |
| In-memory vs local file-backed DRS for v0.1 | `LocalDRS` is already file-backed, layer-separated, and covered by focused tests. | Prefer local file-backed `LocalDRS` with test temp dirs. Avoid a separate in-memory-only DRS unless it is only a fixture wrapper. |
| Reuse existing DRSRecord structures vs new minimal runtime object | `schemas/drs_record.schema.json` already allows `content`, `provenance`, `trace_refs`, `source_refs`, TimeEnvelope, validation, hash, and previous_hash while forbidding additional top-level properties. | Reuse existing DRSRecord shape for stored records. Put semantic metadata inside allowed fields. |
| Module location | Current `LocalDRS` lives in `hedgehog/drs.py`; proof runners live in `demo/`. | Patch plan should decide between a small `hedgehog/local_drs_resolver.py` composing `LocalDRS` or a narrow extension to `hedgehog/drs.py`. Avoid demo-only implementation if this is a runtime-facing primitive. |
| Schema vocabulary sufficiency | Existing schema has enough fields for v0.1 candidate/writeback tests, but no first-class semantic resolver object. | No schema change for v0.1 unless patch-plan review finds a hard blocker. |
| Root integration | Existing Root Final and semantic reuse proofs are proof-level and do not alter production RootOrchestrator behavior. | v0.1 should expose Root-review-required outputs and avoid changing production Root final behavior unless separately approved. |
| Full test scope | This will likely touch `hedgehog/` runtime code in the future patch. | Focused tests are required for the proof patch, and full pytest should be required before closure/docs sync if runtime code changes. |
| Poisoning scope | Compromised Upstream Pack is closed; DRS Poisoning Resistance remains a later gated layer. | Fold only minimum poisoning guardrails into acceptance criteria; do not expand into the separate poisoning layer. |

## 11. Recommended Next Step

Recommended next step:

Real Local DRS Resolver / Writeback v0.1 PATCH PLAN

The patch plan should define the exact future runtime-facing module boundary,
focused proof runner, focused tests, scenario table, counters, and validation
commands before any implementation begins.
