# Full WOW v1.2 Manual Live Multi-LLM / Fractal Real Run — Human Story

document_id: full_wow_v1_2_manual_live_multillm_fractal_real_run_human_story_v01
document_status: HUMAN_STORY
source_audit: docs/audit_reports/auditor_full_wow_v1_2_manual_live_multillm_fractal_real_run_v01.log
source_run_id: full_wow_v1_2_manual_live_multillm_fractal_real_20260706_170024
story_status: PASS
production_ready_claimed: false
public_auditor_ready_claimed: false
real_world_effects_count: 0

## One-screen summary

Six real Gemini semantic actors participated in the completed Full WOW v1.2 manual live multi-LLM/fractal run.

They understood the business process and branch evidence: shipment context, supplier availability, Supplier B blockers, legal/accounting checks, and bank-policy boundaries. Runtime bounded and canonicalized the provider outputs, validators checked every semantic proposal, and Root remained final authority.

No payment happened. No shipment release happened. No ActionCommitPacket was created. No receipt was created. The run was a live semantic observation over a sandbox/product trace, with real_world_effects_count: 0.

## What the business scene was

The business scene was a Supplier Payment / Shipment Release Review trace around shipment SH-2042.

Supplier A can potentially support a scoped mock payment path after corrected evidence. Supplier B remains blocked because its evidence still carries mismatch, delay, and review blockers. Shipment release remains held.

The bank-like path is a boundary surface, not a permission surface. A payment slot is only a prepared shape, not permission to pay. A receipt is evidence only, not truth and not shipment release. This run remains a sandbox/product trace, not production.

## The cast of semantic actors

Top-level Orchestrator:
It saw bounded product-trace context for the v1.2 business scene. It returned a semantic route over warehouse, supplier, legal, accounting, bank, and root-merge branches. It was not allowed to decide truth, authority, action permission, FinalOutput, PlanGraph ownership, connector command, DRS write, or Root bypass.

BSEP membrane:
This was runtime-built, not an LLM actor. It carried bounded context from validated Orchestrator semantics toward Architect. It did not carry raw user text, raw provider text, raw bank secrets, raw IBAN, or bank token. BSEP is not truth, authority, or action permission.

Top-level Semantic Architect:
It saw BSEP-derived bounded context. It returned semantic plan intent: branch cells collect evidence, runtime owns local plan artifacts, validators remain required, and Root decides. Runtime retained PlanGraph ownership. Architect was not allowed to decide truth, authority, action permission, FinalOutput, connector command, DRS write, Root bypass, or provider-owned PlanGraph.

Legal branch semantic actor:
It saw bounded legal/insurance evidence. It returned advisory interpretation for parent/root review. It was not allowed to decide payment permission, create a packet, create a receipt, execute payment, release shipment, or produce FinalOutput.

Accounting branch semantic actor:
It saw bounded invoice and reconciliation evidence. It returned advisory interpretation of payable shape and remaining permission boundaries. It was not allowed to decide payment permission, create a packet, create a receipt, execute payment, release shipment, or produce FinalOutput.

Supplier B branch semantic actor:
It saw bounded Supplier B blocker evidence: invoice mismatch, delivery delay, and legal review need. It returned advisory interpretation that Supplier B remains blocked. It was not allowed to authorize Supplier B payment or shipment release.

Bank policy branch semantic actor:
It saw bounded bank-policy / contract-preview context. It returned advisory interpretation of the payment slot and policy boundary. It was not allowed to turn payment_slot into permission, create receipt truth, execute payment, or release shipment.

## Timeline of the run

1. Business trace loaded.
2. Orchestrator called.
3. Orchestrator validation accepted.
4. BSEP created.
5. BSEP validation accepted.
6. Architect called.
7. Architect validation accepted.
8. Runtime compiled PlanGraph/local plan artifacts.
9. Fractal branch cells created.
10. Legal branch actor validated.
11. Accounting branch actor validated.
12. Supplier B branch actor validated.
13. Bank policy branch actor validated.
14. Branch ResultProposals merged.
15. Post V&V validated.
16. GT/LGT advisory reviewed.
17. Root boundary evaluated.
18. Final PASS.

## What Orchestrator understood

The top-level Orchestrator understood that v1.2 should route API-like business evidence through bounded semantic review. It selected the warehouse, supplier, legal, accounting, bank, and root-merge branches.

The evidence needed was warehouse inventory, supplier availability and blockers, legal insurance and contract status, accounting invoice and PO reconciliation, and bank slot/policy evidence. Required guards included BSEP validation, semantic proposal validation, and Root final authority.

The Orchestrator did not claim truth, authority, action permission, FinalOutput, PlanGraph ownership, connector command, DRS write, or Root bypass.

## What BSEP did

BSEP was built after Orchestrator validation. BSEP was validated before Architect.

BSEP carried bounded context only. The validated packet had no raw user text, no raw provider text, no raw bank secrets, no raw IBAN, and no bank token. It also recorded that Architect received BSEP-derived context.

BSEP is not truth, authority, or action permission. It is a membrane that lets bounded context cross from the Orchestrator stage to the Semantic Architect stage.

## What Architect understood

Architect received BSEP-derived bounded context. It proposed semantic plan intent while runtime retained PlanGraph ownership.

The Architect semantics kept branch work bounded: branch cells collect evidence and return ResultProposals. Validators and Root remained required. Architect did not claim action permission, authority, FinalOutput, connector command, DRS write, or Root bypass.

## What branch-local semantic actors did

The Legal actor interpreted legal and insurance evidence as bounded branch evidence.

The Accounting actor interpreted invoice and reconciliation evidence as bounded branch evidence.

The Supplier B actor interpreted invoice mismatch, delivery delay, and legal-review need as blockers.

The Bank policy actor interpreted payment slot and contract-preview policy boundaries.

All branch actors returned advisory semantic proposals only. None created truth, permission, ActionCommitPacket, receipt, payment, or shipment release.

## What the fractal part means

Runtime created 8 branch cells. Each branch is a bounded work cell. The branches return ResultProposals, and a branch ResultProposal is not FinalOutput.

The parent/root boundary merges branch proposals and keeps authority at Root. This is the first real visible multi-LLM/fractal observation layer: multiple real semantic actors participated, but runtime kept the graph and authority boundaries.

## What the bank part means

The bank-like sandbox and policy path was visible as business evidence.

payment_slot != permission.
receipt != truth.
receipt != shipment release.

Raw bank secret, token, and IBAN did not enter LLM context. The secret scan passed.

## What Root did

Root final boundary was evaluated.

Supplier B remains blocked. Shipment remains held. Receipt remains evidence only.

No action packet was created in this live run. No receipt was created in this live run. No payment was executed. No shipment was released.

## Why this matters

This is the first live v1.2 proof that multiple real LLM semantic actors can participate in one business trace while staying inside zero-trust boundaries.

Branch-local semantic reasoning happened, runtime kept boundaries and PlanGraph ownership, and Root remained final authority. The system can be watched in terminal with artifacts, including prompts, raw responses, extracted JSON candidates, validations, summary, and secret scan.

## Counter table

| Counter | Value |
|---|---:|
| semantic_actor_call_count | 6 |
| real_provider_call_count | 6 |
| network_used_count | 6 |
| gemini_called_count | 6 |
| top_level_orchestrator_llm_call_count | 1 |
| top_level_architect_llm_call_count | 1 |
| branch_local_llm_slm_call_count | 4 |
| bsep_created_count | 1 |
| bsep_validated_count | 1 |
| architect_received_bsep_context_count | 1 |
| runtime_plangraph_compiled_count | 1 |
| fractal_branch_cells_created_count | 8 |
| branch_result_proposals_created_count | 8 |
| post_vv_validated_count | 1 |
| gt_lgt_advisory_review_count | 1 |
| root_final_boundary_evaluated_count | 1 |
| secret_scan_passed | true |
| action_commit_packet_created_count | 0 |
| receipt_created_count | 0 |
| mock_payment_executed_count | 0 |
| real_payment_executed_count | 0 |
| shipment_released_count | 0 |
| real_world_effects_count | 0 |

## Non-claims

- not production
- not public auditor final package
- no real payment
- no real shipment release
- no production connectors
- no real bank/supplier/warehouse API
- no real-world effects

## Next practical step

Next useful step is a human walkthrough runner or story renderer for v1.2 that can print this semantic story directly from artifacts, so the user does not have to read 25 files.
