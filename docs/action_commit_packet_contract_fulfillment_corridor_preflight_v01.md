# ActionCommitPacket / Contract Fulfillment Corridor Preflight v01

## 1. Header

- document_id: action_commit_packet_contract_fulfillment_corridor_preflight_v01
- document_status: PREFLIGHT
- observed_base_head: 55975eb
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- payment_executed: false
- shipment_released: false
- action_commit_packet_created: false
- receipt_created: false
- final_output_created: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false

This document defines the narrowest safe implementation path for
ActionCommitPacket / Contract Fulfillment Corridor permission hardening after
the closed DRS+AVF live semantic observation package.

This is planning only. It does not implement runtime, tests, schemas, provider
calls, connector calls, payment, shipment release, receipt creation, FinalOutput
creation, or an ActionCommitPacket runtime.

## Architecture Correction Source

This preflight is governed by:

- `docs/root_centered_phase_loops_actioncommitpacket_geometry_v01.md`

Slice A must follow that Root-centered phase-loop geometry and
ActionCommitPacket corridor semantics. In particular, Root is the phase
boundary, ActionCommitPacket is a Root-created scoped capability for the
contract/commit plane, and the Contract Fulfillment Corridor returns
evidence/status without expanding authority or restarting reasoning.

## 2. Closed Basis

Closed checkpoint:

- AVF v0.2 + Full WOW v1.2 live observation + human story renderer: PASS.
- Real-run audit:
  `docs/audit_reports/auditor_avf_v0_2_full_wow_v1_2_live_observation_real_run_v01.log`.
- Human story renderer audit:
  `docs/audit_reports/auditor_human_full_wow_v1_2_avf_live_observation_story_renderer_v01.log`.
- Full WOW v1.2 live multi-LLM/fractal lane: PASS.
- Local DRS v0.2 live observation: PASS.
- AVF v0.2 live observation: PASS.
- Human story renderer: PASS.

Closed source facts:

- DRS remembers, links, and warns, but does not decide.
- AVF hard-masks and ranks, but does not authorize.
- LLM semantic actors saw bounded AVF/DRS-informed context only.
- Orchestrator and Architect saw only bounded AVF/DRS-informed context.
- BSEP carried bounded context only.
- Branch actors remained advisory.
- Root remained final authority.
- ActionCommitPacket, receipt, mock payment, real payment, shipment release, and
  effects counters remained `0`.

The next layer is permission/action boundary hardening.

## 3. Plane Separation

Before Root:

- semantic/reasoning plane;
- advisory proposals;
- no action permission;
- DRS is advisory memory/context;
- AVF is advisory risk pressure/ranking;
- LLM semantic actors are advisory;
- branch actors are advisory;
- ResultProposals are advisory;
- Post V&V is advisory validation;
- GT/LGT is advisory review.

Root:

- only Root may emit scoped ActionCommitPacket.

After Root:

- contract/commit plane;
- scoped capability;
- deterministic corridor;
- evidence/status return;
- no new reasoning authority;
- authority never expands;
- reasoning does not restart.

Correct model:

```text
Before Root:
semantic/reasoning plane
-> advisory proposals flow toward Root.

Root:
only Root may emit scoped ActionCommitPacket.

After Root:
contract/commit plane
-> scoped capability flows into deterministic corridor
-> evidence/status returns
-> authority never expands.
```

Hard boundary:

- No wording should let receipts, adapters, banks, or the corridor become
  authority.
- No post-Root LLM reasoning authority starts.
- Evidence/status return is not permission.
- A deterministic corridor can validate, narrow, execute mock steps, and return
  status. It cannot widen scope or become Root.

## 4. ActionCommitPacket Meaning

ActionCommitPacket is:

- Root-created scoped capability packet.
- Not action by itself.
- Not FinalOutput.
- Not LLM output.
- Not DRS output.
- Not AVF output.
- Not receipt.
- Not proof of real payment.
- Not shipment release.

Human explanation:

ActionCommitPacket is like a signed, scoped, expiring instruction from Root to a
deterministic corridor. It says exactly what may be attempted, by which adapter,
for which subject, within which TTL/idempotency scope, and what is forbidden.

## 5. Current Supplier Payment Target

For this checkpoint, target only:

- one Root-created Supplier A mock payment packet;
- Supplier A only;
- Bank A MockBankSandbox only;
- Supplier B excluded;
- shipment release excluded;
- real bank excluded;
- real supplier/warehouse APIs excluded;
- no real-world effects.

Do not implement:

- post-Root LLM reasoning;
- Airline bundle;
- Hedgehog-native bank-to-bank contract;
- real API calls;
- production connector calls.

The future target is a Supplier A mock payment packet, not a general action
system.

## 6. Proposed Contract Vocabulary

Proposed future model names, not implementation:

- `ActionCommitPacketV02`
- `PermissionScopeV02`
- `ForbiddenSurfaceV02`
- `PacketTTL`
- `IdempotencyKeyV02`
- `AdapterBindingV02`
- `PacketEvidenceRefV02`
- `RootSignatureMarkerV02`
- `HumanApprovalRefV02`
- `ContractFulfillmentCorridorV01`
- `CorridorStepV01`
- `CorridorValidationReportV01`
- `MockBankIntentV01`
- `MockBankConsentV01`
- `MockPaymentOrderV01`
- `MockReceiptEvidenceV01`
- `ReturnToRootStatusV01`

## 7. ActionCommitPacket Fields

Required future packet fields:

- `packet_id`
- `packet_type`
- `root_created: true`
- `source_root_decision_ref`
- `human_approval_ref`
- `created_at`
- `expires_at`
- `ttl_seconds`
- `idempotency_key`
- `allowed_subjects`
- `forbidden_subjects`
- `allowed_actions`
- `forbidden_actions`
- `allowed_adapters`
- `forbidden_adapters`
- `payment_slot_ref`
- `creditor_ref`
- `amount`
- `currency`
- `evidence_refs`
- `drs_refs`
- `avf_refs`
- `bsep_ref`
- `root_boundary_ref`
- `production_ready_claimed: false`
- `public_auditor_ready_claimed: false`
- `real_world_effects_allowed: false`

Required explicit values for the current Supplier A mock packet:

- `allowed_subjects`: Supplier A / Adriatic Filters only.
- `forbidden_subjects`: Supplier B.
- `allowed_actions`: `mock_supplier_a_payment_intent` /
  `mock_supplier_a_payment_order` only.
- `forbidden_actions`: `supplier_b_payment`, `shipment_release`,
  `real_payment`, `real_bank_transfer`.
- `allowed_adapters`: MockBankSandbox / Bank A mock only.
- `forbidden_adapters`: `real_bank`, `real_supplier_api`,
  `real_warehouse_api`.
- `receipt_evidence_only: true`.

## 8. Contract Fulfillment Corridor

Deterministic corridor sequence:

```text
Root-created ActionCommitPacket
-> packet validation
-> mock payment intent / consent creation
-> scope check
-> amount check
-> creditor check
-> payment_slot check
-> adapter binding check
-> idempotency check
-> expiry / TTL check
-> forbidden surface check
-> mock payment order
-> mock receipt evidence
-> status/evidence return to Root
```

Every step:

- consumes packet scope;
- may narrow scope;
- cannot widen scope;
- cannot call LLM;
- cannot call real APIs;
- cannot create new permission;
- cannot create FinalOutput;
- cannot release shipment;
- mismatch returns `FAIL_CLOSED` / `RETURN_TO_ROOT`.

## 9. Mirror Contract Geometry

Core corridor invariants:

- Allowed(child) <= Allowed(parent)
- Scope(child) <= Scope(parent)
- Forbidden(child) >= Forbidden(parent)
- TTL(child) <= TTL(parent)
- Adapter(child) must be allowed by packet
- Adapter(child) in allowed_adapters(parent)
- Amount(child) == packet.amount
- Creditor(child) == packet.creditor_ref
- PaymentSlot(child) == packet.payment_slot_ref
- IdempotencyKey(child) == packet.idempotency_key

If any invariant fails:

- no action;
- no receipt;
- no payment;
- no shipment release;
- `FAIL_CLOSED`;
- `RETURN_TO_ROOT`.

## 10. Receipt Boundary

Receipt is evidence only.

Receipt is:

- status only;
- not truth;
- not authority;
- not permission;
- not FinalOutput;
- not future permission;
- not DRS authority;
- not shipment release;
- bound to `packet_id` and `idempotency_key`.

Receipt hard boundaries:

- duplicate receipt rejected;
- wrong packet receipt rejected;
- Supplier B leakage rejected;
- shipment release leakage rejected;
- receipt cannot create future permission;
- receipt cannot release shipment;
- receipt cannot authorize Supplier B.

## 11. Proposed Implementation Slices

Slice A - local packet/corridor model:

- `ActionCommitPacketV02`
- `PermissionScopeV02`
- `ForbiddenSurfaceV02`
- `AdapterBindingV02`
- `PacketTTL`
- `IdempotencyKeyV02`
- `ContractFulfillmentCorridorV01` model
- validation helpers
- no execution yet

Slice B - packet validator / corridor validator:

- validate root-created packet;
- validate scope;
- validate forbidden surfaces;
- validate adapter binding;
- validate TTL;
- validate idempotency;
- validate child corridor narrowing;
- still no mock receipt execution.

Slice C - Supplier A mock packet integration:

- Root-created Supplier A mock packet in deterministic Full WOW baseline;
- Supplier B excluded;
- shipment release excluded;
- real bank excluded;
- no real-world effects.

Slice D - MockBankSandbox corridor execution:

- mock payment intent/consent;
- scope/amount/creditor/payment_slot/idempotency/expiry checks;
- mock payment order;
- mock receipt evidence;
- receipt evidence only.

Slice E - adversarial hardening:

- duplicate packet rejected;
- expired packet rejected;
- wrong adapter rejected;
- Supplier B leakage rejected;
- shipment release leakage rejected;
- receipt cannot create future permission;
- receipt cannot release shipment;
- post-Root LLM reasoning rejected.

Slice F - audit/docs/human story:

- audit log;
- docs/spec/manifest sync;
- human story showing permission/action boundary.

## 12. Required Future Tests

Packet model:

- `packet_without_root_rejected`
- `packet_without_scope_rejected`
- `packet_without_human_approval_ref_rejected`
- `packet_without_ttl_rejected`
- `packet_without_idempotency_key_rejected`
- `packet_with_supplier_b_scope_rejected`
- `packet_with_shipment_release_scope_rejected`
- `packet_with_real_bank_adapter_rejected`
- `packet_with_real_world_effects_allowed_rejected`

Corridor geometry:

- `child_allowed_must_be_subset_of_parent`
- `child_scope_must_be_subset_of_parent`
- `child_forbidden_must_include_parent_forbidden`
- `child_ttl_must_not_exceed_parent_ttl`
- `child_adapter_must_be_allowed_by_packet`
- `child_amount_must_match_packet`
- `child_creditor_must_match_packet`
- `child_payment_slot_must_match_packet`
- `mismatch_returns_fail_closed`
- `mismatch_returns_to_root`

MockBankSandbox:

- `valid_supplier_a_packet_creates_mock_payment_order`
- `valid_supplier_a_packet_creates_mock_receipt_evidence`
- `mock_receipt_is_evidence_only`
- `mock_receipt_does_not_create_permission`
- `mock_receipt_does_not_release_shipment`
- `mock_receipt_bound_to_packet_id`
- `duplicate_receipt_rejected`
- `wrong_packet_receipt_rejected`
- `supplier_b_receipt_leakage_rejected`
- `shipment_release_receipt_leakage_rejected`

Post-Root boundary:

- `no_post_root_llm_reasoning`
- `no_post_root_orchestrator_restart`
- `no_post_root_architect_restart`
- `no_post_root_avf_authority_restart`
- `no_post_root_drs_permission_restart`
- `reasoning_does_not_restart_after_root`

## 13. Non-Goals

- no ActionCommitPacket runtime in this preflight;
- no tests in this preflight;
- no live run;
- no Gemini/provider/network;
- no real bank;
- no real supplier API;
- no real warehouse API;
- no shipment release;
- no production connector;
- no Hedgehog-native bank-to-bank contract yet;
- no Airline demo;
- no Privacy demo;
- no Finance Kill-Switch demo;
- no Vendor onboarding demo;
- no NeedleFactory;
- no Marennya;
- no UP;
- no public auditor package.

## 14. Selected Path

Recommended selected path:

Option A - Slice A local packet/corridor model first.

Reason:

Before integrating mock bank execution, the system needs typed contracts for
packet scope, forbidden surfaces, TTL, idempotency, adapter binding, child
corridor narrowing, and receipt boundary.

Rejected alternatives:

- Option B - directly extend old ActionCommitPacket / mock connector sandbox.
  Reject for now as too broad unless Slice A shows compatible reuse boundaries.
- Option C - new domain demo. Reject because new domains wait until the
  permission/action boundary is hardened.

## 15. Next Immediate Implementation After Preflight

If this preflight is accepted, implement Slice A only.

Candidate future files to propose, not create:

- `hedgehog/action_commit_packet_v02.py`
- `tests/test_action_commit_packet_contract_corridor_v02.py`

Future Slice A must remain local model only:

- no runtime corridor execution;
- no mock bank execution;
- no receipt execution;
- no provider/network/Gemini calls;
- no real connector calls;
- no action/effect counters above `0`.

## 16. Validation For This Preflight

Required validation:

```bash
python3 -m json.tool specs/machine_manifest_v0_25.json >/dev/null

git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --name-only

rg -n "action_commit_packet_contract_fulfillment_corridor_preflight_v01|Contract Fulfillment Corridor|Before Root|After Root|semantic/reasoning plane|contract/commit plane|scoped capability|authority never expands|reasoning does not restart|Allowed\\(child\\).*Allowed\\(parent\\)|Scope\\(child\\).*Scope\\(parent\\)|Forbidden\\(child\\).*Forbidden\\(parent\\)|TTL\\(child\\).*TTL\\(parent\\)|Receipt is evidence only|Supplier A mock payment packet|MockBankSandbox|Option A|Slice A" \
  docs/action_commit_packet_contract_fulfillment_corridor_preflight_v01.md

rg -n "<forbidden authority expansion wording and forbidden readiness/effect claims>" \
  docs/action_commit_packet_contract_fulfillment_corridor_preflight_v01.md || true
```

Expected changed file only:

- `docs/action_commit_packet_contract_fulfillment_corridor_preflight_v01.md`
