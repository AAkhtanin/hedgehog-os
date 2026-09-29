# Five Implementation Routes

Exact source anchors and recorded positive/refusal evidence, inspected in B6.
This is not a new runtime test or an independent approval. The machine companion
[IMPLEMENTATION_ROUTES.json](IMPLEMENTATION_ROUTES.json) retains file hashes,
line ranges, original matrix bindings and actual evidence resources.

## Root Effect

Atlas entities: ROOT, PACKET, FIREWALL, RECEIPT.

Actual Host capture origin/ordinal is checked before retained material/current revision; Root decides separately. Receipt is not repeat permission.

- Contract: [`docs/common_action_and_dynamic_composition_contract_v01.md`](../../../../docs/common_action_and_dynamic_composition_contract_v01.md).
- Implementation: [`hedgehog/kernel/root_decision_v01.py`](../../../../hedgehog/kernel/root_decision_v01.py): `decide_root_v01`, lines 268-287.
- Implementation: [`hedgehog/work_execution_host_v01.py`](../../../../hedgehog/work_execution_host_v01.py): `validate_retained_action_source_capture_v01`, lines 739-765.
- Checker/control: [`tests/test_work_composition_v01.py`](../../../../tests/test_work_composition_v01.py): `test_capture_receipt_material_reuse_and_mutation_v08`, lines 760-859.
- Checker/control: [`tests/test_work_composition_v01.py`](../../../../tests/test_work_composition_v01.py): `test_work_genuine_foreign_root_candidate_and_corridor_refused_before_install`, lines 1189-1239.
- Schema: [`schemas/kernel_artifact_v01.schema.json`](../../../../schemas/kernel_artifact_v01.schema.json).
- Recorded matrix rows: C02, A05, A10.

## Child Topology

Atlas entities: WORK, CHILD, TOPOLOGY, CONSUMPTION.

Actual child-result count consumes the parent child budget; changed Work source rejects old review, and context-free queue aliases fail. No child becomes Root.

- Contract: [`docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`](../../../../docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md).
- Implementation: [`hedgehog/kernel/fractal_runtime_v02.py`](../../../../hedgehog/kernel/fractal_runtime_v02.py): `run_fractal_runtime_v02`, lines 14837-14923.
- Checker/control: [`tests/test_work_composition_v01.py`](../../../../tests/test_work_composition_v01.py): `test_u2_r02_actual_recursive_review_child_accounting`, lines 1580-1659.
- Checker/control: [`tests/test_fractal_runtime_g2_d_v02.py`](../../../../tests/test_fractal_runtime_g2_d_v02.py): `test_d3_profile_d_raw_path_rejects_context_free_alias_micro`, lines 6920-6954.
- Schema: [`schemas/fractal_runtime_v02.schema.json`](../../../../schemas/fractal_runtime_v02.schema.json).
- Recorded matrix rows: N1-07, N1-08, N4-11.

## Memory Time

Atlas entities: MEMORY, TIME, CURRENTNESS, DRS.

Certificate validation is not final permission. Temporal current-use requires valid_from <= now < min(valid_to, TTL end, source-age end). Historical capture is distinct from current capture.

- Contract: [`docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md`](../../../../docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md).
- Implementation: [`hedgehog/reuse_certificate_v01.py`](../../../../hedgehog/reuse_certificate_v01.py): `validate_reuse_certificate_v01`, lines 747-754.
- Implementation: [`hedgehog/external_drs/gate5_contracts_v01.py`](../../../../hedgehog/external_drs/gate5_contracts_v01.py): `temporal`, lines 301-306.
- Checker/control: [`tests/test_work_composition_v01.py`](../../../../tests/test_work_composition_v01.py): `test_capture_material_local_scope_origin_mutation_and_lifetime_v06`, lines 644-757.
- Schema: [`schemas/reuse_certificate_v01.schema.json`](../../../../schemas/reuse_certificate_v01.schema.json).
- Recorded matrix rows: N1-16, A08, N4-04.

## E B C

Atlas entities: E, B, C, STATUS, POINTER.

Football E/B/C are computed offer / published body / consumer context, not the similarly named Gate2 modules. Signed request, nonce, revision, local policy, body hash and current status are bound before consumption; rollback, equivocation and terminal revival are rejected.

- Contract: [`docs/gate5_reference_contract_v01.md`](../../../../docs/gate5_reference_contract_v01.md).
- Implementation: [`hedgehog/external_drs/gate5_contracts_v01.py`](../../../../hedgehog/external_drs/gate5_contracts_v01.py): `check_bundle`, lines 356-386.
- Implementation: [`hedgehog/external_drs/gate5_contracts_v01.py`](../../../../hedgehog/external_drs/gate5_contracts_v01.py): `authenticate_status`, lines 309-325.
- Checker/control: [`tools/run_gate6_football_reference_v01.py`](../../../../tools/run_gate6_football_reference_v01.py): `supplied`, lines 322-354.
- Schema: existing closed Python profile shapes; no separate schema invented.
- Recorded matrix rows: N1-20, N4-14.

## Author Admission

Atlas entities: AUTHOR, KIT, WHAT, EXAMINER, CANDIDATE, SOURCE_ADMISSION.

Reviewed reference source, trusted runner observation and independent oracle are the declared boundary. Supplied consumers refuse candidate imports and require observed Root/dispatch/Work/effect counts zero. Source admission remains separately authorized R1, not runtime authority.

- Contract: [`docs/gate5_authoring_kit_v01/EXECUTION_CONTRACT.md`](../../../../docs/gate5_authoring_kit_v01/EXECUTION_CONTRACT.md).
- Implementation: [`tools/run_gate6_football_reference_v01.py`](../../../../tools/run_gate6_football_reference_v01.py): `execute_case`, lines 232-319.
- Implementation: [`tools/run_gate6_football_reference_v01.py`](../../../../tools/run_gate6_football_reference_v01.py): `supplied`, lines 322-354.
- Checker/control: [`tools/run_gate6_football_reference_v01.py`](../../../../tools/run_gate6_football_reference_v01.py): `check_configuration`, lines 166-174.
- Schema: existing closed Python profile shapes; no separate schema invented.
- Recorded matrix rows: D06, IDENTITY.

## Evidence Boundary

The original G6A matrix and content-addressed resources are complete in the source
bundle. Historical source pins and expected reports stay with each row; B6 checks
the resources and any declared JSON pointer, not the execution that produced them.
No examiner answers have been added to the neutral kit. Source-admission policy
is unchanged; current README replacement needs a later bounded admission decision.
