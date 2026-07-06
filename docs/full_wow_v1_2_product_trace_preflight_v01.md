# Full WOW v1.2 Product Trace Preflight v01

## 1. Header

- document_id: full_wow_v1_2_product_trace_preflight_v01
- document_status: PREFLIGHT
- base_head: 0f7318a
- target_direction: WOW v1.2 product trace + multi-LLM fractal observation
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- payment_executed: false
- shipment_released: false
- production_ready_claimed: false
- public_auditor_ready_claimed: false
- real_world_effects_count: 0

## 2. v1.1 closed basis

- Full WOW v1.1 evidence pack index:
  `docs/full_wow_v1_1_evidence_pack_index.md`.
- Full WOW v1.1 is closed as proof + audit + final rollup + human-facing
  package.
- Real Gemini lane PASS exists.
- Final integrated rollup PASS exists.
- Human-facing walkthrough PASS exists.
- Root remains final authority.
- Supplier B remains blocked.
- Shipment held.
- Receipt evidence only.
- No real payment.
- No real shipment release.

## 3. v1.2 product goal

WOW v1.2 must make the closed v1.1 architecture look like a real business
process. It is not a new architecture.

v1.2 target: same architecture, richer business surface.

v1.2 must show:

- scoped shipment inventory query;
- supplier availability / blocker query;
- legal insurance / contract check;
- accounting invoice / PO reconciliation;
- bank payment slot preparation;
- Hedgehog-native bank contract preview;
- Root first NOT_READY;
- corrected evidence;
- second run;
- scoped human approval;
- Root-created mock ActionCommitPacket;
- MockBankSandbox receipt.

Required API-like business trace:

```text
WarehouseAPI -> SupplierAPI -> Legal -> Accounting -> BankA -> BankB -> Root -> approval -> packet -> receipt
```

Architecture formula preserved:

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```

## 4. Two-lane implementation model

### Lane A — deterministic CI product trace

- stable;
- no Gemini;
- no network;
- no provider;
- no secrets;
- no real payment;
- no real shipment release;
- safe for tests.

### Lane B — manual live multi-LLM/fractal observation

- env-gated;
- not core CI dependency;
- top-level real Orchestrator;
- BSEP;
- real Semantic Architect;
- runtime-built PlanGraph / local plan artifacts;
- branch Fractal Cells;
- branch-local LLM/SLM where semantic ambiguity exists;
- artifact capture;
- secret scan;
- Root boundary.

Important correction:

- Do not remove LLM/SLM actors.
- Do not remove fractal branch execution.
- Do not hide branch work inside counters.
- Do not reduce v1.2 to one LLM summary.
- v1.2 must keep multi-LLM/fractal observation as an explicit manual lane.

## 5. Required business modules

### WarehouseAPI sandbox

- shipment-scoped inventory query;
- example: SH-2042 required items, available qty, shortage qty;
- meaning: warehouse evidence;
- does_not_authorize: shipment release.

### SupplierA API sandbox

- availability query;
- Supplier A can support scoped mock payment path;
- does_not_authorize: broad supplier payment.

### SupplierB API sandbox

- blocker/delay/mismatch query;
- Supplier B remains blocked;
- does_not_authorize: Supplier B payment.

### Legal module

- insurance/contract check;
- may use branch-local LLM/SLM if document/clause is messy;
- does_not_authorize: payment permission.

### Accounting module

- invoice/PO reconciliation;
- may use branch-local LLM/SLM for mismatch explanation;
- does_not_authorize: payment permission.

### BankA legacy sandbox

- payment slot preparation;
- masked slot visible to LLM;
- raw IBAN/token stays internal;
- payment_slot != permission;
- Root packet required before mock execution.

### BankB Hedgehog-native preview

- semantic contract review preview;
- execution_allowed=false while Supplier B blocked;
- no payment execution.

## 6. Required transition cards

Every business step must output a transition card with:

- step_id
- actor_or_module
- api_like_call
- input_summary
- output_summary
- meaning
- does_not_authorize
- next_step
- trace_id
- evidence_id

Required step_ids:

- dirty_request_received
- warehouse_inventory_query
- supplier_a_availability_query
- supplier_b_blocker_query
- legal_insurance_contract_check
- accounting_invoice_po_reconciliation
- bank_a_payment_slot_prepared
- bank_b_native_contract_preview
- top_level_live_orchestrator_semantics
- bsep_membrane_created_validated
- top_level_live_semantic_architect
- runtime_plangraph_compiled
- fractal_branch_cells_dispatched
- branch_result_proposals_collected
- post_vv_validated
- gt_lgt_advisory_review
- root_first_not_ready
- corrected_evidence_received
- root_second_supplier_a_scoped_review
- human_approval_supplier_a_only
- root_created_mock_action_commit_packet
- mock_bank_sandbox_receipt
- final_state_summary

## 7. Required fractal branches

- warehouse_branch
- supplier_a_branch
- supplier_b_branch
- legal_branch
- accounting_branch
- bank_a_branch
- bank_b_branch
- root_merge_branch

Each branch must produce:

- branch_context
- branch_evidence
- branch_result_proposal
- branch_authority_boundary
- branch_called_llm_or_slm_count
- branch_called_api_count
- branch_real_world_effects_count: 0

## 8. Branch-local LLM/SLM policy

Allowed:

- legal clause / insurance note semantic extraction;
- accounting mismatch explanation;
- supplier unstructured note explanation;
- bank policy wording explanation;
- warehouse incident note explanation if present.

Not required:

- structured WarehouseAPI stock count;
- structured bank payment slot status;
- simple deterministic availability rows.

Forbidden:

- branch LLM/SLM creates truth;
- branch LLM/SLM creates action permission;
- branch LLM/SLM creates FinalOutput;
- branch LLM/SLM creates ActionCommitPacket;
- branch LLM/SLM creates receipt;
- branch LLM/SLM executes payment;
- branch LLM/SLM releases shipment;
- branch LLM/SLM owns PlanGraph.

## 9. Secret membrane

Required bank secret split:

- Bank internal view may contain raw fake IBAN/token inside sandbox only.
- LLM-visible view gets payment_slot, beneficiary_verified, checksum status,
  payment_form_status, payment_permission_status.
- Secrets ∩ LLMContext = empty.
- payment_slot != permission.
- receipt != truth.
- receipt != shipment release.

## 10. Required counters for future v1.2

- wow_v1_2_product_trace_created_count: 1
- transition_cards_created_count: >= 23
- deterministic_product_trace_lane_count: 1
- manual_live_multillm_fractal_lane_available_count: 1
- top_level_orchestrator_llm_call_count: 1 in manual lane
- top_level_architect_llm_call_count: 1 in manual lane
- bsep_created_count: 1
- bsep_validated_count: 1
- runtime_plangraph_compiled_count: 1
- fractal_branch_cells_created_count: >= 7
- branch_result_proposals_created_count: >= 7
- warehouse_api_sandbox_call_count: 1
- supplier_a_api_sandbox_call_count: 1
- supplier_b_api_sandbox_call_count: 1
- legal_module_check_count: 1
- accounting_module_check_count: 1
- bank_a_payment_slot_prepared_count: 1
- bank_b_native_contract_preview_count: 1
- branch_local_llm_slm_call_count: >= 1 in manual observation lane
- payment_permission_granted_before_root_count: 0
- supplier_b_payment_allowed_count: 0
- shipment_released_count: 0
- real_payment_executed_count: 0
- real_world_effects_count: 0

## 11. Required implementation options

### Option A

Create v1.2 deterministic product trace runner first, then manual live
multi-LLM/fractal observation lane.

### Option B

Create both deterministic and manual live multi-LLM/fractal lanes in one larger
patch.

### Option C

Block if v1.1 evidence pack is missing or product trace requirements conflict
with passport.

### Selected option

Selected option: Option A.

Reason:

Option A gives a stable deterministic CI product trace first, then a clean
manual live multi-LLM/fractal observation layer without mixing proof stability
and live observation variability. It keeps the product trace from becoming
proof-only while preserving a separate env-gated lane for branch-local LLM/SLM
and fractal observation.

## 12. Required future files if Option A selected

Patch 1:

- `demo/run_full_wow_v1_2_product_trace.py`
- `tests/test_full_wow_v1_2_product_trace_runner.py`

Patch 2:

- `demo/run_full_wow_v1_2_manual_live_multillm_fractal_trace.py`
- `tests/test_full_wow_v1_2_manual_live_multillm_fractal_trace_runner.py`

## 13. Non-claims

- not production
- not public auditor final package
- no real payment
- no real shipment release
- no production connectors
- no real bank/supplier/warehouse API
- no real-world effects

## 14. Preflight conclusion

WOW v1.2 should proceed as a product trace, not proof-only. The deterministic
lane should show the API-like business modules and transition cards under CI.
The manual live lane should show top-level Orchestrator -> BSEP -> Semantic
Architect, runtime-built PlanGraph/local plan artifacts, Fractal Cells,
branch-local LLM/SLM where ambiguity exists, ResultProposals, Post V&V,
GT/LGT, Root final boundary, scoped approval, mock packet, and receipt.

No provider, network, Gemini, secrets, payment, shipment, sandbox adapter, or
real-world effect was used by this preflight.
