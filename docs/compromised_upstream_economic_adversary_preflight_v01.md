# Compromised Upstream / Economic Adversary / DRS Poisoning v0.1 — Read-only Preflight

## 1. Status

* preflight_id: compromised_upstream_economic_adversary_preflight_v01
* preflight_status: COMPLETE
* latest_checkpoint_commit: 9b70726
* previous_layer: DRS Lineage / Provenance Pressure v0.1
* roadmap_layer: Compromised Upstream / Economic Adversary / DRS poisoning-adversarial maturity
* repair_started: false
* patch_plan_started: false
* proof_started: false
* runtime_modified: false
* schemas_modified: false
* tests_modified: false
* production_drs_implemented: false
* external_drs_implemented: false
* network_used: false
* gemini_used: false
* marennya_activated: false
* up_activated: false
* negative_trace_implemented: false
* auto_governance_implemented: false
* manifest_hardening_implemented: false
* transition_matrix_mutated: false

## 2. Scope

This is read-only preflight. It does not create an adversarial proof, does not
implement production/external DRS, does not implement Negative Trace
governance, does not mutate the manifest or transition matrix, and does not
create auto-hardening.

The purpose is to identify the safest next Patch Plan boundary for the current
roadmap layer by inspecting existing repo surfaces, closed proofs, schemas, and
audit summaries.

## 3. Roadmap Placement

* Previous closed layer: DRS Lineage / Provenance Pressure v0.1.
* Current layer: Compromised Upstream / Economic Adversary / DRS poisoning-adversarial maturity.
* Later layer after this track: Kernel Enforcement Integration / Forbidden Transition Regression, unless a later controlling roadmap names a different exact next layer.
* Future V2 / Negative Trace / Marennya / UP remain deferred.

The DRS Lineage / Provenance Pressure checkpoint closed the rule that lineage
and provenance can inform, warn, rank, or block, but cannot decide. The next
roadmap track should now pressure-test adversarial upstream inputs and
memory-poisoning attempts without turning Negative Trace, manifest hardening,
transition matrix mutation, Marennya, or UP into current work.

## 4. Existing Adversarial Surfaces

Observed surfaces are listed only where repo evidence was found.

| Surface | Observed file / proof / schema | Already protects | Does not yet protect | Mode | Risk if added incorrectly |
| --- | --- | --- | --- | --- | --- |
| ConnectorObservation | `demo/run_read_only_enterprise_connector_sandbox_v01.py`; `docs/audit_reports/auditor_read_only_enterprise_connector_sandbox_v01.log`; `specs/human_passport_v0_25.md` | Bank, legal, warehouse, and logistics outputs remain read-only observations; connector output is not truth, ready status, DRS write, or action. | Does not model a deliberately compromised known upstream source across a combined adversarial maturity pack. | Blocking for escalation; observation itself is advisory. | A compromised source could be accidentally treated as truth or trusted evidence. |
| EvidenceCandidate | `demo/run_external_evidence_acceptance_gate_v01.py`; `tests/test_external_evidence_acceptance_gate_v01_runner.py`; `docs/audit_reports/auditor_external_evidence_acceptance_gate_v01.log` | Candidate-only before Root decision; cannot become AcceptedEvidence, truth, ready status, action, or DRS write by itself. | Does not yet test economic/adversarial repetition trying to turn many candidates into authority. | Candidate/advisory until Root. | Candidate volume could be mistaken for acceptance or readiness. |
| ValidationPacket | `demo/run_external_evidence_acceptance_gate_v01.py`; `specs/math_appendix_v0_3.md` | ValidationPacket is not Root acceptance; GT and ConflictCheck are not acceptance authority. | Does not model signed-looking stale legal source pressure as a dedicated adversarial scenario. | Advisory validation input. | Validation metadata could be mistaken for Root acceptance. |
| AcceptedEvidence | `demo/run_external_evidence_acceptance_gate_v01.py`; Long-lived DRS TTL Aging proof and audit; lineage pressure proof | AcceptedEvidence requires Root decision, but remains bounded evidence; old AcceptedEvidence is not future action permission. | Does not yet test fake repeated successes or attacker reuse pressure trying to make AcceptedEvidence action permission. | Bounded evidence, not authority. | Accepted evidence ancestry could be laundered into action permission or direct reuse. |
| RejectedEvidence | `demo/run_external_evidence_acceptance_gate_v01.py`; `demo/run_conflictcheck.py` | Rejected evidence remains rejected and conflict-aware. | Does not yet test repeated fake negative traces trying to rewrite governance. | Blocking/advisory depending route. | Rejection history could be misused as automatic governance mutation. |
| QuarantinedEvidence | `demo/run_external_evidence_acceptance_gate_v01.py`; DRS Lifecycle; TTL/aging and lineage pressure proofs | Unknown-source evidence and proximity to quarantine can warn or block; quarantine taint is bounded. | Does not yet test quarantine flood / DoS pressure across an adversarial maturity proof. | Blocking or warning, never authority. | Quarantine flood could be treated as global graph shutdown or forced DoS. |
| ExternalDRSPointer | `demo/run_external_drs_pointer_protocol_v01.py`; `docs/audit_reports/auditor_external_drs_pointer_protocol_v01.log`; schema pointer storage kind in `schemas/drs_record.schema.json` | External pointer candidates cannot self-promote into trusted evidence, truth, DRS write, installed capability, or action. | Does not yet test economic trust laundering through repeated pointer references plus lineage pressure. | Advisory pointer candidate. | Pointer reference could be misread as external/global trust. |
| ConflictCheck report | `demo/run_conflictcheck.py`; `tests/test_conflictcheck_runner.py`; `docs/audit_reports/auditor_conflictcheck.log` | Flags contradiction/risk families and recommends Root/GT review, reuse/promotion block, quarantine review, or invalidation review without deciding truth or mutating DRS. | Does not yet combine compromised upstream and DRS poisoning in one pressure run. | Advisory until Root, sometimes blocking recommendation. | ConflictCheck could be misused as truth, invalidation, promotion, or governance authority. |
| DRS lifecycle states | `demo/run_drs_lifecycle_semantics.py`; `schemas/drs_record.schema.json`; `docs/audit_reports/auditor_drs_lifecycle_semantics.log` | Represents completed, degraded, blocked, failed, rejected, quarantined, deadend, and promotion_candidate states; quarantine release and deadend override require Root. | Does not yet model attacker-created lifecycle floods or poisoned reuse clusters. | Storage/lifecycle, not judge. | Lifecycle state could be used as self-authorizing memory authority. |
| DRS deadend/quarantine proximity | `demo/run_drs_graph_proximity.py`; Long-lived DRS TTL Aging proof; DRS Lineage / Provenance Pressure proof | Proximity can warn or block and is bounded; deadend/quarantine does not globally taint the graph. | Does not yet test adversarial flood pressure attempting global DoS. | Query-time ranking/warning/blocking signal. | Proximity could be made into unbounded traversal or graph-wide taint. |
| lineage/provenance pressure | `demo/run_drs_lineage_provenance_pressure_v01.py`; `docs/audit_reports/auditor_drs_lineage_provenance_pressure_v01.log` | Lineage informs, lineage does not decide; provenance does not become truth; audit/hash-chain proves continuity, not truth. | Does not yet model attacker-controlled provenance and poisoned lineage pressure. | Advisory pressure signal. | Attacker lineage could be confused with authority or truth. |
| audit hash-chain | `demo/run_audit_hash_chain.py`; `docs/audit_reports/auditor_audit_hash_chain.log`; lineage pressure proof | Proves continuity and tamper evidence only; does not mutate DRS or prove truth. | Does not yet test fake negative traces attempting governance or manifest mutation. | Evidence continuity, not authority. | Hash continuity could be mistaken for truth or policy authorization. |
| schema validation | `schemas/result_proposal.schema.json`; `schemas/common.schema.json`; Runtime JSON Schema Validation Hardening audit | ResultProposal rejects unexpected top-level fields; EvidenceItem.kind is constrained; Post V&V validates shape. | No adversarial proof yet combining schema-valid poisoned content with compromised upstream pressure. | Blocking for malformed artifacts. | Schema validity could be mistaken for semantic truth. |
| transition matrix forbidden transitions | `demo/run_kernel_enforcement_transition_matrix_v01.py`; `docs/audit_reports/auditor_kernel_enforcement_transition_matrix_v01.log` | Allows 10 bounded transitions and blocks 35 forbidden transitions; transition matrix is not authority or production runtime. | Does not yet test fake negative traces trying to mutate the matrix. | Proof-level blocking matrix. | A future proof could accidentally treat transition rows as mutable governance. |
| capability manifest / facade validation | `demo/run_developer_facade_capability_manifest_ux_v01.py`; `docs/audit_reports/auditor_developer_facade_capability_manifest_ux_v01.log` | Validated manifest candidates are RootReviewInput only; 10 adversarial manifest attempts are blocked. | Does not yet test attacker-generated negative traces or poisoned DRS records trying to force manifest hardening. | Candidate/advisory until Root review. | Manifest candidate could be mistaken for installed capability or governance update. |
| production boundary non-goals | `specs/human_passport_v0_25.md`; `specs/demo_baseline_v0_25.md`; `README.md` | Production Boundary Design Docs v0.1 documents non-claims and future gates. | Does not itself prove compromised upstream or DRS poisoning behavior. | Documentation boundary. | Preflight/proof language could overclaim production security. |
| LLM semantic executor bounded behavior | `demo/run_bounded_llm_semantic_executor_node_v01.py`; `docs/audit_reports/auditor_bounded_llm_semantic_executor_node_v01.log` | LLM remains bounded Executor node capability and cannot finalize, write DRS, or execute actions. | Does not yet test LLM-generated economic/adversarial poisoned traces in the current track. | Bounded ResultProposal/SemanticDraft path. | SemanticDraft could be treated as truth or adversarial governance input. |
| chaos pack scenarios | `demo/run_enterprise_chaos_pack_v01.py`; `docs/audit_reports/auditor_enterprise_chaos_pack_v01.log` | Blocks 18 escalation attempts over dirty enterprise surfaces; four unsafe cross-boundary cases are quarantined and blocked. | It is a broad closed pack, but it does not specifically separate compromised upstream, DRS poisoning, and economic/adversary pressure into reviewed next-layer patches. | Blocking showcase/proof pack. | Reusing it as a mega-proof could hide which boundary failed or was overloaded. |

## 5. Threat Classes To Map

| Threat class | Existing coverage | Missing proof behavior | Expected safe outcome | Authority boundary | Why Root remains required |
| --- | --- | --- | --- | --- | --- |
| compromised_bank_source | Connector sandbox models `bank_source`; Acceptance Gate accepts only bounded mock bank evidence after Root decision. | Dedicated compromised known-source scenario where a bank-like source lies while appearing known. | Create observation/candidate only; force validation/conflict review; no truth, action, ready status, or DRS write. | Source is observation; EvidenceCandidate is candidate-only. | Only Root can accept evidence and still cannot turn it into action permission. |
| stale_legal_source_signed_looking | Connector sandbox blocks stale legal output; Acceptance Gate rejects stale legal certificate and signature/revocation failures. | Signed-looking but stale legal source that appears formally valid yet fails freshness/time review. | Review or rejection; stale source cannot become current truth. | ValidationPacket and signature-looking fields are not Root acceptance. | Root must decide after freshness, conflict, and acceptance gates. |
| warehouse_source_contradiction | Applied warehouse/document demos and ConflictCheck cover `not_ready` and invalid ready contradictions. | Compromised warehouse source contradicting prior world state under adversarial pressure. | Block ready claim or require Root review. | ConflictCheck remains advisory until Root. | Root decides readiness and final status. |
| external_pointer_trust_laundering | External DRS Pointer Protocol blocks pointer self-promotion and provenance laundering; lineage proof blocks bridge authority transfer. | Repeated pointer + bridge + provenance pressure trying to launder trust. | Reject or quarantine trust-laundering attempt. | ExternalDRSPointer is pointer only, not trust. | Root must review any later accepted evidence path. |
| repeated_fake_negative_traces | Negative Trace and Manifest Auto-Hardening are explicitly deferred in AGENTS; audit hash proves continuity only. | Proof that repeated fake negative traces cannot mutate manifest, transition matrix, or governance. | Records remain bounded pressure; no governance mutation. | Audit/history is not governance. | Root and separately approved governance layers are required before any mutation. |
| fake_successful_patterns | DRS Lifecycle has repeated_success_protocol_candidate and requires Root, repeated validation, sandbox tests/manifest where applicable. | Attacker-controlled fake successful patterns attempting reuse or installed capability authority. | Promotion/reuse requires review; no direct authority. | ReuseScore, lineage, and success history are advisory. | Root controls promotion, reuse, and any final output. |
| drs_poisoning_attempt | DRS lifecycle, taxonomy, TTL/aging, graph proximity, and lineage pressure block unsafe reuse and authority from memory. | Unified poisoning scenario where hostile records enter memory-like surfaces and try to drive final reuse. | Block/quarantine or require review; memory remains non-authoritative. | DRS is storage/index/lifecycle, not judge. | Root must decide any final reuse/writeback path. |
| reuse_poisoning | Semantic reuse pipeline, ReuseGate traces, TTL aging, and lineage pressure block stale/unsafe direct reuse. | Attacker uses high reuse, old AcceptedEvidence, or poisoned lineage to force direct reuse. | Direct reuse blocked or Root review required. | ReuseScore/ReuseBoost/history are advisory and cannot override hard gates. | RootShortcutAllowed and Root final authority remain required. |
| quarantine_flood_dos_pressure | TTL/aging and lineage proofs bound proximity and taint; DRS lifecycle contains quarantine. | Flood scenario showing many quarantine records do not globally shut down graph or force unbounded traversal. | Bounded review window; local blocks/warnings only. | Quarantine is containment, not global taint. | Root controls escalation, release, and final action. |
| old_not_ready_laundered_into_ready | Applied warehouse/document demos prove `not_ready`; TTL aging blocks stale reuse; lineage proof blocks provenance authority. | Direct old `not_ready` laundering into ready through lineage/reuse pressure. | Block ready claim; require fresh validation and Root. | Old evidence/history is not future action permission. | Root final status cannot be created by memory. |
| quarantine_made_to_look_safe | Quarantine lifecycle and proximity proofs block direct reuse and global taint. | Repetition/popularity around quarantine making it appear safe. | Keep quarantine bounded and non-reusable until Root review. | Popularity and proximity are not authority. | Root controls quarantine release. |
| negative_trace_governance_mutation_attempt | Kernel transition matrix and developer facade block unauthorized manifest/transition claims; Negative Trace remains deferred. | Explicit proof that fake negative traces cannot mutate manifest, transition matrix, or auto-hardening state. | No mutation; route to future reviewed layer. | Trace history is not governance authority. | Root and approved governance patch plan are required. |

## 6. Candidate Future Scenarios

These are scenario candidates for the adversarial maturity track.

| Scenario | Attacker input / pressure | Existing surface involved | Expected outcome | Authority boundary | Non-goal | Suggested reason code |
| --- | --- | --- | --- | --- | --- | --- |
| compromised_bank_source_cannot_create_truth | Known bank-like source claims payment truth and readiness. | ConnectorObservation, EvidenceCandidate, ValidationPacket. | Observation/candidate only; blocked from truth and action. | Source is not truth; Root remains final authority. | No real bank connector. | compromised_source_not_truth |
| stale_legal_source_signed_looking_forces_review | Legal registry-like source is signed-looking but stale. | Connector sandbox, Acceptance Gate, TTL/TimeEnvelope. | Review or reject; no current truth. | Signed-looking source is not truth. | No real signature or registry validation. | stale_signed_source_requires_review |
| warehouse_source_contradiction_blocks_ready | Warehouse source claims ready against known shortage. | Applied warehouse proof, ConflictCheck. | Ready claim blocked; Root review required. | ConflictCheck remains advisory until Root. | No production warehouse integration. | conflicting_warehouse_provenance_blocks_ready |
| external_pointer_trust_laundering_rejected | External pointer repeats trust claims through bridge/provenance. | ExternalDRSPointer, bridge traversal, lineage pressure. | Reject/quarantine trust laundering. | External pointer is not trust. | No external/global DRS. | external_pointer_trust_laundering_rejected |
| repeated_fake_negative_traces_do_not_mutate_governance | Many fake negative trace records request policy/manifest change. | Audit hash-chain, kernel transition matrix, developer facade. | No manifest or transition mutation. | Repeated traces are not governance. | No Negative Trace governance implementation. | repeated_traces_not_governance |
| fake_successful_patterns_do_not_create_reuse_authority | Repeated fake successes seek direct reuse/promotion. | DRS Lifecycle, ReuseScore, TTL aging, lineage pressure. | Review required; no direct reuse authority. | Fake success does not create reuse authority. | No Needle installation or auto-promotion. | fake_success_not_reuse_authority |
| drs_poisoning_attempt_blocks_or_quarantines_candidate | Poisoned local record tries to enter reuse candidate set. | DRS lifecycle, schema validation, provenance pressure. | Block/quarantine candidate or require Root review. | DRS poisoning cannot make memory authority. | No production persistent graph. | drs_poisoning_blocked_or_quarantined |
| reuse_poisoning_requires_root_review | Poisoned reuse history tries to bypass gates. | Semantic reuse pipeline, ReuseGate, TTL aging. | Root review required; direct reuse blocked. | Reuse history is not Root. | No production direct reuse execution. | reuse_poisoning_root_review_required |
| quarantine_flood_does_not_force_global_dos | Many quarantine records near candidate try to shut down all routes. | Quarantine/deadend proximity, bounded lineage candidates. | Bounded local block/warn; no global DoS. | Quarantine flood can be bounded without global DoS. | No production DoS simulation. | quarantine_flood_bounded_not_global_dos |
| old_not_ready_cannot_be_laundered_into_ready | Old not_ready record is reused through lineage/bridge/popularity. | Applied demos, TTL aging, lineage pressure. | Ready claim blocked; fresh review required. | Old not_ready cannot become ready through lineage/reuse pressure. | No real document submission. | old_not_ready_not_laundered_to_ready |
| quarantine_cannot_be_made_safe_by_repetition | Repeated near-quarantine reuse makes safety claims. | DRS lifecycle, proximity, lineage pressure. | Quarantine remains bounded warning/blocking signal. | Popularity is not safety. | No quarantine release automation. | repeated_quarantine_not_safe |
| root_final_authority_preserved_under_economic_pressure | Composite pressure: compromised source, pointer laundering, fake success, negative traces, quarantine flood. | All inspected proof surfaces. | All non-Root authority flags false; Root review/final boundary preserved. | Root remains final authority. | No combined production security claim. | root_final_authority_preserved_under_pressure |

## 7. Required Invariants For Future Proof

* compromised upstream source is not truth
* signed-looking source is not truth
* external pointer is not trust
* repeated traces are not governance
* negative traces do not mutate manifest
* negative traces do not mutate transition matrix
* fake success does not create reuse authority
* old not_ready cannot become ready through lineage/reuse pressure
* quarantine flood can be bounded without global DoS
* DRS poisoning cannot make memory authority
* ConflictCheck remains advisory until Root
* GT remains advisory/selection
* Root remains final authority
* audit/hash-chain proves continuity, not truth
* AcceptedEvidence is bounded evidence, not future action permission

## 8. Recommended Split / Next Patch Plan

Recommendation: Option B, split the track into smaller proof layers.

1. Compromised Upstream Pack v0.1
2. DRS Poisoning Resistance v0.1
3. Economic Adversary Pack v0.1

Why this is safer than one combined proof:

* Proof size: the candidate scenario list spans connector trust, stale legal
  source handling, warehouse contradiction, external pointer laundering,
  lineage pressure, DRS poisoning, reuse poisoning, quarantine flood, fake
  success, and fake negative trace governance pressure. One combined proof
  would be large enough to hide which boundary is actually under test.
* Semantic overload: repo evidence already separates ConnectorObservation /
  EvidenceCandidate / ValidationPacket / AcceptedEvidence from DRS lifecycle,
  reuse, lineage, audit, transition matrix, and manifest surfaces. Combining
  all in one first patch risks mixing source compromise with memory poisoning
  and governance/economic pressure.
* Local deterministic scope: a first Compromised Upstream Pack can remain
  local and deterministic by reusing the existing connector/evidence/pointer
  vocabulary without touching runtime or schema.
* Negative Trace deferral: keeping fake negative trace governance mutation in
  a later Economic Adversary Pack avoids accidentally implementing Negative
  Trace governance or auto-hardening now.
* Auto-governance avoidance: DRS Poisoning Resistance can test memory
  contamination and quarantine flood without manifest or transition matrix
  mutation.
* Root final: each split can assert Root final authority in a focused way.
* Roadmap proximity: the roadmap wording names Compromised Upstream /
  Economic Adversary / DRS poisoning-adversarial maturity as a track, not
  necessarily as one monolithic proof.

The next patch plan should therefore be:

Compromised Upstream Pack v0.1 Patch Plan

It should cover the first four to six upstream-source scenarios before moving
to DRS poisoning and economic/governance pressure.

## 9. Likely Implementation Strategy For Future Proof

Because the recommendation is split, the first future proof should be:

* `demo/run_compromised_upstream_pack_v01.py`
* `tests/test_compromised_upstream_pack_v01_runner.py`

Suggested first-patch scenarios:

1. `compromised_bank_source_cannot_create_truth`
2. `stale_legal_source_signed_looking_forces_review`
3. `warehouse_source_contradiction_blocks_ready`
4. `external_pointer_trust_laundering_rejected`
5. `accepted_evidence_from_compromised_source_is_not_action_permission`
6. `root_final_authority_preserved_under_compromised_upstream_pressure`

The future proof must be local deterministic only.

It must not:

* implement production DRS
* implement external/global DRS
* call network
* call Gemini
* activate Marennya
* activate UP
* implement Negative Trace governance
* auto-mutate manifest
* auto-mutate transition matrix
* install Needle
* execute external actions

## 10. Gaps Found

Supported gaps from inspected files:

* Compromised upstream is not yet unified into one focused proof. The connector
  sandbox and Acceptance Gate cover read-only observations and candidate
  acceptance boundaries, but they do not isolate a deliberately compromised
  known upstream source as the next maturity layer.
* External pointer and AcceptedEvidence gates exist, but not under sustained
  economic pressure where repeated references try to launder trust or action
  permission.
* Lineage/provenance pressure exists, but not with attacker-controlled source
  pressure as the explicit input.
* DRS poisoning and quarantine flood are not jointly tested. Existing TTL,
  proximity, lifecycle, and lineage proofs show bounded behavior but do not
  model adversarial flood pressure as the main scenario.
* False negative traces are parked as future governance candidates and not
  active. AGENTS explicitly defers Negative Trace and Manifest Auto-Hardening.
* There is no proof that fake repeated negative traces cannot mutate manifest.
  Kernel and facade proofs block unauthorized transition and manifest claims,
  but fake negative trace governance mutation is not yet a named scenario.
* There is no proof that fake successful patterns cannot create direct reuse
  authority under adversarial control. DRS Lifecycle has repeated success
  protocol candidates, but those are not attacker-pressure scenarios.
* There is no dedicated proof that a stale signed-looking legal source forces
  review. Existing stale legal and signature/revocation checks are local proof
  fields, not real-world validation.
* There is no production connector sandbox. Existing connector work is
  read-only and proof-only.
* There is no global DRS. External pointer protocol remains local proof-only
  pointer topology.

## 11. Non-goals

* no production DRS
* no external/global DRS
* no real connector trust
* no network
* no Gemini
* no Marennya
* no UP
* no Negative Trace implementation
* no auto-governance
* no manifest hardening implementation
* no transition matrix mutation
* no installed Needle
* no production persistence
* no production connector sandbox
* no full pytest run in preflight
* no proof runner in preflight

## 12. Recommended Next Action

Create the selected Patch Plan next:

Compromised Upstream Pack v0.1 Patch Plan

Do not start the proof runner before patch plan review. The patch plan should
keep the first proof local deterministic, source-focused, and explicitly
separate from later DRS Poisoning Resistance v0.1 and Economic Adversary Pack
v0.1.
