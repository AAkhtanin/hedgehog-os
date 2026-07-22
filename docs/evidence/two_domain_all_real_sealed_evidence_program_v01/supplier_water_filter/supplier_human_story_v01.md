# Supplier Water Filter: Evidence from Intent to Offline Replay

## Business Need and Boundaries

The bounded business need was to review whether a Supplier A mock-payment path could proceed for the Water Filter transaction while Supplier B blockers and shipment evidence remained unresolved. The live semantic lane identified evidence needed from warehouse inventory, supplier availability and blockers, legal insurance and contract status, accounting reconciliation, and the bank payment-slot and policy preview. A payment slot was not payment permission.

The six LLM calls contributed advisory semantic selection and routing only. Runtime canonicalization, BSEP, DRS, AVF, deterministic validators, Root decisions, the scoped ActionCommitPacket, Corridor validation, receipt validation, Kernel integrity, Package, Anchor verification, and Replay remained locally owned. LLM output created no truth, authority, permission, payment, shipment release, receipt authority, FinalOutput, connector command, or production action.

## Complete Public-Safe Semantic Contributions

The following are the complete accepted public-safe semantic objects. They contain no prompt text, provider-response body, credential, private Attempt material, or private path.

### 1. Top-Level Orchestrator

```json
{"action_permission_claimed":false,"authority_claimed":false,"bypass_root_claimed":false,"connector_command_claimed":false,"drs_write_claimed":false,"evidence_needed":["warehouse inventory","supplier availability and blockers","legal insurance and contract status","accounting invoice and PO reconciliation","bank payment slot and policy preview"],"final_output_claimed":false,"plan_graph_claimed":false,"proposal_id":"orchestrator-semantic-wow-v1-2-001","required_guards":["BSEP validation","semantic proposal validation","Root final authority"],"root_review_required":true,"route_reasoning":["Route API-like business evidence through bounded semantic review."],"selected_branch_ids":["warehouse_branch","supplier_a_branch","supplier_b_branch","legal_branch","accounting_branch","bank_a_branch","bank_b_branch","root_merge_branch"],"suggested_route":"supplier_payment_shipment_review_v1_2","truth_claimed":false,"uncertainty_notes":["Provider semantics remain candidate-only until runtime validation and Root review."]}
```

### 2. Top-Level Semantic Architect

```json
{"action_permission_claimed":false,"authority_boundary_reasoning":["Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides."],"authority_claimed":false,"branch_intent_reasoning":["Branch cells collect bounded evidence and return ResultProposals."],"connector_command_claimed":false,"drs_write_claimed":false,"executor_constraint_reasoning":["No executor is authorized by provider output."],"final_output_claimed":false,"forbidden_surface_reasoning":["Provider output cannot create ActionCommitPacket, receipt, payment, shipment release, connector command, or FinalOutput."],"plan_shape_reasoning":["Runtime builds local plan artifacts after semantic validation."],"proposal_id":"architect-semantic-wow-v1-2-001","required_validators":["Architect semantic proposal validation","branch ResultProposal validation","Post V&V","GT/LGT advisory review","Root final boundary"],"result_proposal_summary":"Supplier A may proceed only to scoped review. Supplier B remains blocked. Shipment release remains held. Receipt remains evidence only.","return_to_root_reasoning":["The semantic proposal returns to Root because provider output is advisory only."],"root_bypass_claimed":false,"root_recommendation":"needs_more_evidence","selected_branch_ids":["warehouse_branch","supplier_a_branch","supplier_b_branch","legal_branch","accounting_branch","bank_a_branch","bank_b_branch","root_merge_branch"],"source_route_id":"orchestrator-semantic-wow-v1-2-001","truth_claimed":false,"validator_coverage_reasoning":["Semantic, BSEP, branch, Post V&V, GT/LGT, and Root checks remain required."]}
```

### 3. Legal Clause Semantic Extractor

```json
{"action_commit_packet_claimed":false,"action_permission_claimed":false,"authority_claimed":false,"branch_semantic_proposal_id":"legal_clause_semantic_extractor-semantic-001","connector_command_claimed":false,"evidence_interpretation":"Evidence supports bounded parent and Root review only.","final_output_claimed":false,"payment_execution_claimed":false,"receipt_claimed":false,"recommended_branch_status":"accepted_for_parent_review","return_to_parent_reasoning":"Branch output returns to parent/root boundary as semantic evidence only.","semantic_summary":"Branch semantic observation remains advisory.","shipment_release_claimed":false,"source_branch_id":"legal_branch","truth_claimed":false,"uncertainty_notes":["Branch semantics remain candidate-only until validation and Root review."]}
```

### 4. Accounting Mismatch Semantic Explainer

```json
{"action_commit_packet_claimed":false,"action_permission_claimed":false,"authority_claimed":false,"branch_semantic_proposal_id":"accounting_mismatch_semantic_explainer-semantic-001","connector_command_claimed":false,"evidence_interpretation":"Evidence supports bounded parent and Root review only.","final_output_claimed":false,"payment_execution_claimed":false,"receipt_claimed":false,"recommended_branch_status":"accepted_for_parent_review","return_to_parent_reasoning":"Branch output returns to parent/root boundary as semantic evidence only.","semantic_summary":"Branch semantic observation remains advisory.","shipment_release_claimed":false,"source_branch_id":"accounting_branch","truth_claimed":false,"uncertainty_notes":["Branch semantics remain candidate-only until validation and Root review."]}
```

### 5. Supplier B Unstructured Note Interpreter

```json
{"action_commit_packet_claimed":false,"action_permission_claimed":false,"authority_claimed":false,"branch_semantic_proposal_id":"supplier_b_unstructured_note_interpreter-semantic-001","connector_command_claimed":false,"evidence_interpretation":"Evidence supports bounded parent and Root review only.","final_output_claimed":false,"payment_execution_claimed":false,"receipt_claimed":false,"recommended_branch_status":"accepted_for_parent_review","return_to_parent_reasoning":"Branch output returns to parent/root boundary as semantic evidence only.","semantic_summary":"Branch semantic observation remains advisory.","shipment_release_claimed":false,"source_branch_id":"supplier_b_branch","truth_claimed":false,"uncertainty_notes":["Branch semantics remain candidate-only until validation and Root review."]}
```

### 6. Bank Policy Semantic Reviewer

```json
{"action_commit_packet_claimed":false,"action_permission_claimed":false,"authority_claimed":false,"branch_semantic_proposal_id":"bank_policy_semantic_reviewer-semantic-001","connector_command_claimed":false,"evidence_interpretation":"Evidence supports bounded parent and Root review only.","final_output_claimed":false,"payment_execution_claimed":false,"receipt_claimed":false,"recommended_branch_status":"accepted_for_parent_review","return_to_parent_reasoning":"Branch output returns to parent/root boundary as semantic evidence only.","semantic_summary":"Branch semantic observation remains advisory.","shipment_release_claimed":false,"source_branch_id":"bank_b_branch","truth_claimed":false,"uncertainty_notes":["Branch semantics remain candidate-only until validation and Root review."]}
```

## Nine Scenarios in Frozen Order

### S-N1: Initial Business Blockers, Root Not Ready

Intent: expose unresolved business evidence before action. The semantic evidence requested bounded warehouse, supplier, legal, accounting, and bank-policy review. Deterministic validation kept the blockers visible. Root returned `NOT_READY`; Supplier A was `BLOCKED_PENDING_CORRECTION`, Supplier B was `BLOCKED`, shipment was `HELD`, and packet, Corridor, and receipt remained absent. The row passed as proof that no action occurred.

### S-N2: Unsafe Live Evidence Fails Closed

Intent: prove that accepted live semantics could not be widened into unsafe public evidence. The safe-projection validator rejected raw-material inclusion, a failed secret scan, nonzero effects, and invalid call geometry. No new Root final was accepted. Supplier A remained blocked pending correction, Supplier B remained `BLOCKED`, shipment remained `HELD`, and packet, Corridor, and receipt remained absent. The attacked projections were `FAIL_CLOSED`; the rejection proof passed.

### S-C1: Corrected Evidence Validation Rerun

Intent: revalidate corrected evidence without another provider call. The semantic evidence remained advisory, and deterministic validators performed a fresh evaluation rather than mutating the first Root result. Root reached `SUPPLIER_A_SCOPED_REVIEW_READY` only. Supplier B remained `BLOCKED`, shipment remained `HELD`, and no packet, Corridor, receipt, payment, or shipment release existed.

### S-P1: Supplier A Scoped Human Approval

Intent: apply explicit human approval only to Supplier A. Validators checked the approval reference, scope, beneficiary, bank policy, payment slot, expiry, forbidden subjects, and forbidden actions. Root alone created the scoped ActionCommitPacket. Supplier A became `APPROVED_SCOPE_ONLY`; Supplier B, real-bank action, and shipment release remained excluded. Corridor was not entered and no receipt existed.

### S-P2: Supplier A Mock-Bank Happy Path

Intent: exercise only the scoped Supplier A mock-payment path. Validators checked the Root-created packet, mock intent, consent, order, receipt, and terminal receipt observation. The bounded Corridor passed and the receipt remained `EVIDENCE_ONLY`. Supplier B remained `BLOCKED`, shipment remained `HELD`, and no real payment, settlement, bank call, or shipment release occurred.

### S-F1: No Human Approval Blocks Action

Intent: prove that action cannot proceed without the required human approval reference. The ActionCommitPacket validator returned `missing_human_approval_ref`. Root created no action approval; the packet was rejected, Corridor was not entered, and no receipt or execution remained.

### S-F2: Packet and Corridor Mutation Matrix

Intent: reject Supplier B, shipment-release, and scope-widening mutations. The public packet and Corridor validators returned the governed scope and subset failures, including `supplier_b_scope_forbidden`, `shipment_release_forbidden`, `child_allowed_not_subset_of_parent`, and `child_scope_not_subset_of_parent`. No widened Root decision survived; packet and Corridor attacks were rejected, while Supplier B stayed `BLOCKED` and shipment stayed `HELD`.

### S-F3: Receipt Attack Matrix

Intent: prove that receipt and registry evidence cannot create future permission or authority. Public MockBank receipt and registry validators rejected attempts to authorize Supplier B, expand authority after Root, release shipment, or turn registry state into permission. The receipt attack was rejected, with no new execution, permission, authority, payment, or shipment release.

### S-M1: Integrated Mixed Business Outcome

Intent: preserve the complete bounded result rather than report a false all-business PASS. Technical conformance passed and Supplier A's scoped mock path passed. Root held the broader boundary; Supplier B remained `BLOCKED`, shipment remained `HELD`, and the receipt remained `EVIDENCE_ONLY`. The business outcome remained `MIXED` with zero real-world effects.

## Package, Anchor, and Offline Replay

The accepted S1 and S2 identities were projected into safe evidence and sealed in the Supplier Package. The Package and adjacent indexes remained `SELF_CONSISTENT_UNANCHORED`. The stored Anchor remained `EVIDENCE_ONLY`; it did not claim anchored PASS at publication time.

P2 supplied the exact stored Anchor publication identity to a fresh verification. The matching verification returned `ANCHORED_PASS`. Offline Replay reconstructed the same Manifest, safe-member order, domain projection, package content hash, and evidence continuity, then closed `PASS`. Replay did not rerun semantics, Root, Corridor, provider calls, or business actions.

The complete operational geometry is: 6 live provider/network/Gemini calls in accepted S1; deterministic S2 and S3 with 0 new provider/network/Gemini calls; Supplier B `BLOCKED`; shipment `HELD`; receipt `EVIDENCE_ONLY`; business outcome `MIXED`; and 0 real-world effects. Prompts, provider-response bodies, credentials, and private Attempt material are intentionally not published.
