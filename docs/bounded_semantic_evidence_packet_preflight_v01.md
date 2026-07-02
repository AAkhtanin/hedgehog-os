# BoundedSemanticEvidencePacket Orchestrator -> Architect Preflight v0.1

document_id: bounded_semantic_evidence_packet_preflight_v01
document_status: PREFLIGHT
base_head: 4e644f0

## Source Context Inspected

- hedgehog/context_packets.py
- tests/test_context_packets_core.py
- hedgehog/semantic_reasoning_adapter.py
- tests/test_semantic_reasoning_adapter_core.py
- demo/run_live_unknown_request_dual_rich_context_v01.py
- tests/test_live_unknown_request_dual_rich_context_v01.py
- docs/semantic_reasoning_adapter_core_extraction_checkpoint_v01.md
- docs/audit_reports/auditor_semantic_reasoning_adapter_delegation_slice_c_v01.log
- README.md
- AGENTS.md
- specs/human_passport_v0_25.md
- specs/machine_manifest_v0_25.json

## Why This Layer Exists

Real Gemini Unknown Request 007 proved the live semantic spine: Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.

The semantic_reasoning_adapter is now core in hedgehog.semantic_reasoning_adapter, and the live runner delegates semantic adapter mechanics to it. The Architect still receives validated route context, but not richer bounded semantic evidence from the Orchestrator path. The next layer introduces a BoundedSemanticEvidencePacket created after Orchestrator semantic proposal validation, structured_orchestrator_rationale validation, and OrchestratorRouteContextPacket validation.

BoundedSemanticEvidencePacket carries bounded facts, missing evidence, uncertainty, risk and authority boundaries, and rejected action reasoning from Orchestrator to Architect. It must not pass raw user request text downstream. It must not pass raw cross-role Gemini text downstream. It is not a raw text dump, not an unbounded Gemini context dump, and not production action.

## Proposed Location

Preferred location:

- add the BoundedSemanticEvidencePacket contract to hedgehog.context_packets
- add or extend direct tests in tests/test_context_packets_core.py

Reason:

- this is a bounded ContextPacket family
- hedgehog.context_packets already owns OrchestratorRouteContextPacket and ArchitectPlanContextPacket
- tests/test_context_packets_core.py already exercises bounded packet builders, common validation, raw dump rejection, authority claim rejection, and selected vector subset behavior

Alternative only if implementation review demands:

- add a new hedgehog.semantic_evidence_packet module

The preferred path remains hedgehog.context_packets because BoundedSemanticEvidencePacket is a ContextPacket contract, not a provider adapter and not a rationale builder.

## Candidate Packet Fields

Packet identity:

- packet_type: BoundedSemanticEvidencePacket
- packet_id
- created_by
- source_role: orchestrator
- target_role: architect
- source_route_id
- source_proposal_id
- source_context_packet_id
- source_structured_rationale_ref
- source_refs
- schema_version

Creator policy:

- created_by must be runtime/bounded_context_packet_builder, not Gemini/provider.
- Provider/Gemini does not create BoundedSemanticEvidencePacket.
- Future validator should reject provider/Gemini-created evidence packets.
- Suggested reason string: bounded_semantic_evidence_packet_creator_must_be_runtime

Evidence fields:

- observed_semantic_facts
- missing_evidence
- uncertainty_notes
- risk_boundary_notes
- rejected_action_routes
- required_approvals_or_conditions
- selected_vector_ids
- required_guards
- authority_boundary_notes

Boundary fields:

- truth_claimed: false
- authority_claimed: false
- action_permission_claimed: false
- final_output_claimed: false
- connector_command_claimed: false
- action_commit_packet_claimed: false
- root_bypass_claimed: false
- raw_user_text_included: false
- raw_cross_role_text_included: false
- ContextPacket is not truth: true
- ContextPacket is not authority: true
- BoundedSemanticEvidencePacket is not truth: true
- BoundedSemanticEvidencePacket is not authority: true
- BoundedSemanticEvidencePacket is not FinalOutput: true
- BoundedSemanticEvidencePacket is not ActionCommitPacket: true
- Evidence packet is not action permission: true
- Gemini proposes, Root disposes: true
- Root remains final authority: true

## Evidence Item Shape

Each bounded evidence item should use a constrained object shape:

- text: non-empty string
- source: provider_semantic_reasoning | runtime_canonicalization | validated_context_packet | structured_rationale
- evidence_kind: observed_fact | missing_evidence | uncertainty | risk_boundary | rejected_route | approval_condition | authority_boundary
- confidence_label: low | medium | high | unknown
- candidate_only: true
- raw_quote: false

Rules:

- no empty strings
- no empty objects
- no raw full request text
- no raw cross-role provider text
- no long unbounded dumps
- no connector, action, final, or ActionCommitPacket surfaces
- proposed per-item text limit: 280 characters
- proposed per-field item limit: 12 items
- proposed total packet item limit: 48 items

These limits keep Architect context bounded while still carrying useful semantic evidence.

## Builder And Validator Proposal

Future core functions:

- build_bounded_semantic_evidence_packet(...)
- validate_bounded_semantic_evidence_packet(packet)
- bounded_semantic_evidence_packet_validation_result(...)
- semantic_evidence_item(...)
- validate_semantic_evidence_items(...)

Future tests:

- recommended: tests/test_context_packets_core.py
- alternative if the test file becomes too large: tests/test_bounded_semantic_evidence_packet_core.py

The validator must reject:

- missing required packet fields
- unexpected packet_type
- raw_user_request
- raw_user_text
- raw_cross_role_text
- raw_gemini_text
- truth, authority, action, final, connector, action_commit, or root_bypass claims
- empty evidence fields
- empty evidence item text
- evidence item dicts without source or evidence_kind
- overlong item text
- too many evidence items
- selected_vector_ids outside validated route vectors when route context is passed
- source_route_id must match validated OrchestratorRouteContextPacket route when route context is passed
- source_proposal_id must match validated Orchestrator proposal id when proposal context is passed
- source_context_packet_id must match OrchestratorRouteContextPacket packet_id when context packet is passed
- source_structured_rationale_ref must reference accepted structured_orchestrator_rationale when rationale validation is passed
- missing Root final authority boundary
- real-world action surfaces

Suggested lineage and creator reason strings:

- bounded_semantic_evidence_packet_creator_must_be_runtime
- bounded_semantic_evidence_source_route_mismatch
- bounded_semantic_evidence_source_proposal_mismatch
- bounded_semantic_evidence_source_context_packet_mismatch
- bounded_semantic_evidence_source_rationale_missing_or_unaccepted

The validation result should be explicit and stable, matching the existing context_packets style of clear fail-closed reason strings.

## Relationship To Existing Core

- hedgehog.semantic_reasoning_adapter builds canonical rationales from provider semantic reasoning proposals.
- hedgehog.context_packets should own the bounded packet contract.
- hedgehog.structured_rationale remains canonical rationale authority for structured_orchestrator_rationale and structured_architect_rationale builders and validators.
- BoundedSemanticEvidencePacket does not become truth.
- BoundedSemanticEvidencePacket does not become authority.
- BoundedSemanticEvidencePacket does not become DRS.
- BoundedSemanticEvidencePacket does not become AVF.
- BoundedSemanticEvidencePacket does not become ActionCommitPacket.

The packet should reference validated sources and bounded summaries. It should not duplicate structured rationale ownership or become a new authority layer.

## Runner Integration Plan

Slice A: core-only packet contract and tests.

- add BoundedSemanticEvidencePacket to hedgehog.context_packets
- add direct tests
- no runner integration
- no Gemini
- no network

Slice B: runner integration.

- demo/run_live_unknown_request_dual_rich_context_v01.py builds BoundedSemanticEvidencePacket after Orchestrator semantic proposal validation, structured_orchestrator_rationale validation, and OrchestratorRouteContextPacket validation
- runner validates the packet before Architect
- Architect provider context includes the bounded evidence packet or bounded packet summary
- Architect prompt receives bounded evidence packet context, not raw user request
- output shape may add bounded_semantic_evidence_packet and bounded_semantic_evidence_packet_validation
- initial integration may use HEDGEHOG_UNKNOWN_REQUEST_BOUNDED_SEMANTIC_EVIDENCE_PACKET=1 if a staged gate is useful

Slice C: replay smoke.

- injected or monkeypatched semantic path PASS
- Architect consumes BoundedSemanticEvidencePacket
- raw_user_request absent from Architect prompt and context
- raw cross-role text absent from Architect prompt and context
- 007 plan node shape preserved
- action counters zero
- no real Gemini or network

Slice D: optional gated real live replay.

- only after injected smoke
- preserve raw provider output in local .tmp evidence
- no action counters
- Root remains final authority

Slice E: audit and docs sync.

- audit the new bounded evidence layer
- update docs and manifest only after smoke evidence

## 007 Preservation Requirements

BoundedSemanticEvidencePacket must not change existing 007 Root decision semantics. The current semantic default path remains semantic_reasoning_adapter plus json_mime_only.

The 007-compatible local PlanGraph nodes remain:

- node:unknown_request_semantic_review
- node:root_review_gate

Additional preservation requirements:

- action counters stay zero
- compact_rationale_adapter path remains available
- full_structured_rationale path remains available
- Architect still consumes only validated upstream artifacts
- Root remains final authority

## Future Test Expectations

Core tests should prove:

- valid packet builds and validates
- raw user text is rejected
- raw Gemini text is rejected
- authority, action, final, connector, and action_commit claims are rejected
- empty evidence fields are rejected
- overlong or unbounded evidence is rejected
- evidence item missing source or evidence_kind is rejected
- packet is not truth, not authority, not FinalOutput, and not action permission
- packet builder sets BoundedSemanticEvidencePacket is not truth true
- packet builder sets BoundedSemanticEvidencePacket is not authority true
- validator rejects missing BoundedSemanticEvidencePacket is not truth and BoundedSemanticEvidencePacket is not authority boundaries
- validator rejects provider/Gemini-created packet
- validator rejects source lineage mismatch
- valid packet remains bounded and action counters stay zero
- Root remains final authority is required
- no fixture hardcodes

Runner tests should prove:

- Architect receives BoundedSemanticEvidencePacket
- Architect does not receive raw user request
- Architect prompt includes bounded facts, missing evidence, uncertainty, and risk boundary
- Orchestrator-to-Architect evidence derives from validated Orchestrator semantic output and runtime canonicalization
- invalid evidence packet blocks Architect or PlanGraph before Root
- semantic default path still PASS
- compact and full paths remain available
- counters unchanged
- action counters zero

## Authority Invariants

- Provider output is not truth.
- Provider output is not authority.
- ContextPacket is not truth.
- ContextPacket is not authority.
- BoundedSemanticEvidencePacket is not truth.
- BoundedSemanticEvidencePacket is not authority.
- structured rationale is explanation only.
- PlanGraph is not authority.
- ResultProposal is not FinalOutput.
- DRS is not truth.
- AVF/route/vector selection is not authority.
- Gemini proposes, Root disposes.
- Gemini does not create ActionCommitPacket.
- Gemini does not create FinalOutput.
- Root remains final authority.

## Non-Claims

- not production autonomy.
- not public WOW ready yet.
- no real connector.
- no real robot API.
- no door unlock.
- no robot dispatch.
- no payment/shipment/API call.
- no real-world action.
- no ActionCommitPacket from Gemini.
- no FinalOutput from Gemini.
- no NeedleFactory/Marennya/UP.

## Preflight Conclusion

BoundedSemanticEvidencePacket is the next rich-context layer after semantic_reasoning_adapter core extraction. It should be implemented as a bounded ContextPacket in hedgehog.context_packets, with direct core tests first and runner integration second.

The intended flow is:

Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.

BoundedSemanticEvidencePacket adds a validated, bounded Orchestrator-to-Architect evidence bridge. It must keep raw request text and raw provider text out of downstream Architect context, preserve 007 behavior, keep all action counters zero, and maintain Root as the only final authority.
