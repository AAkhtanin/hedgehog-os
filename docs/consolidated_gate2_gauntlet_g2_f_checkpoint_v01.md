# Whole Gate 2: Safe Reuse, Bounded Work and Revocable Action Eligibility

## Purpose and Outcome

Gate 2 makes the accepted Root-centered kernel operational as one bounded
thread: reuse inexpensive information when it is safe, do the necessary deeper
work when it is not, withdraw current action eligibility when dependencies
change, and recompute only what is affected. It does not turn a memory match,
route proposal or past success into permission to act.

This is the whole-Gate2 checkpoint through its final G2-F boundary. A through E
provide the mechanisms; F executes their real composition and checks seven
operational laws. The core is domain-independent. Airline and Supplier are
accepted reference domains, not deployed booking, banking or payment services.
Gates are engineering acceptance stages, not the route followed by a ticket.

The reference domains exercise different business meanings. In the accepted
[Airline comparison](../tests/test_airline_semantic_to_contract_causal_runtime_v01.py),
changing soft travel preferences changes the recommended offer, ClientRoot
selection and hold contract while the candidate snapshot and hard constraints
stay fixed; authoritative price, route and validity come from AirlineRoot's
offer records. In [Supplier Water Filter](evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_human_story_v01.md),
warehouse, legal, accounting and bank-policy evidence supports Supplier A's
scoped mock-payment review while Supplier B remains blocked and shipment
remains held; technical conformance can pass with a mixed business outcome.
Both preserve validated advisory input, Root-owned decisions, scoped contracts
and evidence-only receipts. These are separate accepted domain proofs, not one
combined business transaction or new domain executions in G2F; the eleven-stage
F thread below is its own deterministic integration scenario.

## Closure Boundary

```text
CHECKPOINT_ID=consolidated_gate2_gauntlet_g2_f_checkpoint_v01
CHECKPOINT_SCOPE=WHOLE_GATE2_A_THROUGH_F
INTENDED_G2F_STATUS=CLOSED_PASS
INTENDED_GATE2_STATUS=CLOSED_PASS
IMPLEMENTATION_BASIS=90cb073695bf8c5f5a2673c7aba84b6615719b37
MAINTENANCE_BASIS=5d6fd6d98f3412a1d999bfe84101cabe39301573
CLASS_A_BASIS=779641d1a2e1c256c8232655d02124b66e3657b3
CLOSURE_COMMIT_IDENTITY=NOT_SELF_RECORDED
EFFECTIVE_CLOSURE=ONLY_EXACT_OWNER_COMMITTED_FOURTEEN_PATH_SUCCESSOR
```

These bytes describe the intended accepted closure. In a dirty proposal on I,
the guard derives `G2F_CLOSURE_CANDIDATE`; no owner closure has occurred.
Only a single-parent exact fourteen-path child of I, with clean worktree and
origin at I before push or at that child after push, can derive
`G2F_CLOSED_PASS_COMMITTED`. Staging must be empty at validation boundaries.
The same document bytes work before and after commit; no future commit hash
is invented. An isolated test commit proves guard behavior only.

The preflight's earlier Class-A status fields and the A-E checkpoint status
snapshots remain historical to their stated bases. They do not undo the actual
M maintenance and I implementation. This checkpoint does not change their
semantic laws or silently reclassify old evidence as fresh execution.

## Layers A Through F

| Layer | Human meaning | Public mechanism and contract | Current focused test | Accepted evidence |
| --- | --- | --- | --- | --- |
| A | A Root-authorized packet can lose current eligibility without deleting its history. | `ActionCommitPacketV02`, immutable registry, `record_action_packet_revocation_v01`, `record_action_packet_supersession_v01`, `inspect_action_packet_present_eligibility_v01`; [action packet](../hedgehog/action_commit_packet_v02.py). Fulfillment remains behind the bounded Corridor/Effect Firewall. | [lifecycle tests](../tests/test_action_commit_packet_lifecycle_g2_a_v01.py) | [A checkpoint](actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md), [A audit](audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log), reused `CLOSED_PASS`. |
| B | A pointer-first memory answer may save work, never preserve action permission. | Temporal query, eligibility before ranking, Root shortcut review and ReuseCertificate: [resolution](../hedgehog/drs_memory_resolution_v01.py), [certificate](../hedgehog/reuse_certificate_v01.py). | [B tests](../tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py) | [B checkpoint](drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md), [B audit](audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log), reused `CLOSED_PASS`. |
| C | Propose the minimum permitted deterministic route; its owning Root accepts independently. | `route_execution_mode_v01`, `review_execution_mode_proposal_v01`; [router](../hedgehog/kernel/execution_mode_router_v01.py). Router cannot approve itself. | [C tests](../tests/test_execution_mode_router_g2_c_v01.py) | [C checkpoint](execution_mode_router_g2_c_checkpoint_v01.md), [C audit](audit_reports/auditor_execution_mode_router_g2_c_v01.log), reused `CLOSED_PASS`. |
| D | Execute bounded child work with explicit queues/budgets; results return upward. | `run_fractal_runtime_v02`, runtime-owned topology and `validate_fractal_cell_result_v02`; [runtime](../hedgehog/kernel/fractal_runtime_v02.py), [current addendum](fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md). | [D tests](../tests/test_fractal_runtime_g2_d_v02.py) | [corrected D checkpoint](fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_correction_checkpoint_v01.md), [v0.3.10 audit](audit_reports/auditor_fractal_runtime_g2_d_v0310_profile_d_t12_revise_projection_correction_v01.log), reused current `CLOSED_PASS`. |
| E | A changed dependency causes complete/minimal selective recomputation and fresh Root review. | `run_continuous_delta_runtime_v01`, validation of affected set, invalidation without deletion and unchanged siblings; [delta](../hedgehog/kernel/continuous_delta_runtime_v01.py), [E contract](continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md). | [E tests](../tests/test_continuous_delta_runtime_g2_e_v01.py) | [E checkpoint](continuous_delta_runtime_v0_1_g2_e_checkpoint_v01.md), [E audit](audit_reports/auditor_continuous_delta_runtime_g2_e_v01.log), reused `CLOSED_PASS`. |
| F | Demonstrate the actual consolidated A-E thread and seven laws. | Five public [runner](../demo/run_consolidated_gate2_gauntlet_g2_f_v01.py) entrypoints; [181-row preflight](consolidated_gate2_gauntlet_g2_f_preflight_v01.md), sections 6-9. | [exact F24](../tests/test_consolidated_gate2_gauntlet_g2_f_v01.py) | This whole-Gate2 checkpoint and [independent I evidence audit](audit_reports/auditor_consolidated_gate2_gauntlet_g2_f_v01.log); intended closure is topology-gated as above. |

Current corrected D is implementation `41db6c6bfbf787c04d288c5ddb40e285118d06c1`
over `2c9f2060ab0abf6dffa270dac4ffd7095d091d08`, audited at
`5001db910fcc6e68cbe03a527eccd9455d7bf063`. Older D v0.3.7/8/9 records remain
historical. E1/E2 established structural and delta contracts; E3 is accepted on
corrected D, E4's strict subtree/backpressure acceptance is corrected at
`21176be090cab9aa9b8ea9cce2ae052bed8039da`; E5 is committed at
`f582701208b603463a03d404aa841c302a8221d6`; E6 integrated Living/Conformance at
`4c133da11b8bcbd642e1aaa3413ce0a9c357731d`, followed by control-plane repair
`6079ddcfe59f582936e7b13af2753a6533117970`. The current E checkpoint binds this
sequence. No older pending marker is presented as its current state.

## The Actual Eleven-Stage Thread

1. Build deterministic WorldState, policy and fact inputs. The shared business
   request/parent correlation is `transaction:g2f:gate2:v01`. Client and Supplier
   each build row005 DRS queries; their distinct query IDs are local transactions.
2. Resolve safe informational memory. Rows001-024 carry the temporal/query,
   candidate, owning-Root shortcut and ReuseCertificate evidence. Memory is
   eligible input, not permission or completed-action proof.
3. Accept `direct_informational_reuse` under Root control. The informational
   report has no memory-descent result; heavy G2-D execution and packet creation
   for this path remain zero.
4. Rebind related work as high-risk/action-like. DRS refuses the shortcut with
   `drs_action_intent_shortcut_forbidden`; similarity cannot bypass the fence.
5. Route both Roots independently to `full_fractal`. Rows063-066 bind one parent
   MultiRoot envelope to the actual decisions and artifacts. Parent correlation
   never substitutes for a lane transaction and creates no SuperRoot.
6. Execute the bounded G2-D bundles at row069; validate proposals, Post-V&V,
   terminal GT and owning-Root return. Children return evidence, not finality.
7. Construct the row070 packet candidate from five typed public components.
   Bind rows075-084; only after the Supplier packet-authorization review,
   register, activate, queue
   and reach the immutable row098 `PENDING_FULFILLMENT` baseline. Row083 has both
   structural and supplier-context validators; no adapter is called.
8. Change one authoritative fact payload content hash. The changed source is
   in `ordered_changed_node_ids`, not `ordered_affected_ids`; affected artifacts
   and parents are derived consequences. Resolve TARGET/SIBLING by prior semantic
   identity, never by the order of bundle collections.
9. Recompute the complete/minimal affected Supplier material under fresh Root
   review. Preserve sibling bytes. Rows124/127/128 carry the accepted runtime
   artifact binding; row129 is the standalone observation with three absent
   Root sentinels. Row130 consumes that exact observation.
10. Prove two independent branches from row098: revocation rows130-144 and
    supersession rows156-181, with successor authorization at145-155. Row143
    never supplies supersession. Row173 uses authorized row154. Row180 retains
    immutable old replay; row181 refuses old PRESENT execution.
11. Validate that actual report, project plain data and render compact sorted
    JSON with exactly one terminal LF. Two fresh collections have equal plain
    projections and identical canonical renders, without a report cache.

Eight direct Root decisions occupy logical020(two),033,082,128,137,152,163.
Candidate ID, normalized claim, contribution, review packet, Post-V&V candidate,
GT choice, decision input/result and source transaction remain cross-bound.

## Seven Operational Laws and Test Traceability

The node names below are exact functions in
`tests/test_consolidated_gate2_gauntlet_g2_f_v01.py`; the complete pytest node IDs
are retained in the evidence register. Coverage is derived from test bodies and
the supplied-report validator, not inferred from names or total counts.

| Law | Positive node(s) | Negative node(s) and observable refusal | Actual evidence and public mechanism | Layer evidence |
| --- | --- | --- | --- | --- |
| 1. Safe informational reuse skips heavy work. | `test_g2f_positive_03_informational_fast_path_heavy_skip`, `test_g2f_dod_01_safe_informational_reuse` | `test_g2f_hostile_08_drs_not_authority`: extra/missing lanes and substituted DRS carrier are refused; typed authority/permission/FinalOutput claims get `drs_non_authority_law_invalid`. These are integrity/non-authority negatives, not an invented heavy-work execution. | rows023 memory_descent_result is None; rows024 shortcut validation; `laws.safe_informational_reuse_skips_heavy_work`; `validate_existing_root_shortcut_decision_v01`. | B checkpoint/audit; C route contract. |
| 2. Action-like reuse remains blocked. | `test_g2f_dod_02_action_reuse_blocked` | The same node asserts the actual negative row026 result and `drs_action_intent_shortcut_forbidden`; `test_g2f_hostile_08_drs_not_authority` separately rejects manufactured authority. | row026 action_intent_passed=False; `evaluate_drs_candidate_v01`; current request, not past permission. | B action-history fence; A lifecycle evidence. |
| 3. High-risk multi-Root work takes the deep path. | `test_g2f_positive_04_high_risk_multiroot_full_fractal_execution`, `test_g2f_dod_03_high_risk_multiroot_deep` | `test_g2f_hostile_09_router_not_authority`: foreign transaction/Root and reidentified typed router claim refusals. `test_g2f_hostile_13_no_permission_revival`: coherent wrong wrapper decision/artifact; parent builder rejects `multiroot_transaction_mismatch`. | rows005,050,057-069; `route_execution_mode_v01`, `review_execution_mode_proposal_v01`, `build_transaction_outcome_envelope_v01`; root_local_transaction_ids and eight direct Root receipts. | C independent review; D child work. |
| 4. Revoke an authorized packet before fulfillment. | `test_g2f_positive_05_packet_delta_revocation_supersession_chain`, `test_g2f_dod_04_revoke_before_fulfillment` | `test_g2f_hostile_13_no_permission_revival`: fabricated row129 Root positions rejected by public validator; changed candidate produces `revocation_root_candidate_mismatch`; separate coherent observation breaks row130 continuity. | rows098,124-144; `record_action_packet_revocation_v01`, `validate_revocation_root_context_coherence_v01`, `validate_action_invalidation_evidence_v01`; row144 non-executable. | A revocation; E changed-dependency review. |
| 5. Superseded old packets cannot replay as presently executable. | `test_g2f_dod_05_superseded_replay_blocked` | `test_g2f_hostile_14_no_stale_packet_replay`: authentic negative inspection for revived eligibility; revoked-registry cross-feed; coherent unauthorized row173 source map. | rows154,173,179-181; supersession_source_registry is row098; `record_action_packet_supersession_v01`, `replay_action_packet_lifecycle_history_v01`, `validate_action_packet_present_eligibility_inspection_v01`. | A replay/present separation. |
| 6. One fact change causes complete/minimal selective recomputation. | `test_g2f_dod_06_selective_recompute`, `test_g2f_positive_02_causal_order_and_identity_lineage` | `test_g2f_hostile_12_delta_not_authority`: wrong TARGET identity and lost sibling digest rejected; independently derived IDs survive reversed child view. `test_g2f_hostile_11_child_not_root`: missing/extra/wrong/future/self/cross-Root bindings and inconsistent reverse consumers rejected. | row117 complete/minimal plan; row120 delta bundle; delta_role_bindings and four sibling byte identities; `run_continuous_delta_runtime_v01`, `derive_fractal_child_cell_id_v02`. | D current corrected scope; E selective recompute. |
| 7. Components and aggregation create no authority. | `test_g2f_dod_07_components_non_authority` | `test_g2f_hostile_08_drs_not_authority` through `test_g2f_hostile_12_delta_not_authority`, `test_g2f_hostile_15_no_aggregate_pass`, `test_g2f_hostile_16_zero_operations`: typed DRS/router/child/registry/delta/MultiRoot refusals; aggregate/SuperRoot/permission/FinalOutput and operation summary poisons. | `validate_resolution_candidate_v01`, `validate_execution_mode_proposal_v01`, `validate_fractal_cell_result_v02`, `validate_action_commit_packet_registry_v02`, `build_continuous_delta_runtime_report_v01`, `validate_transaction_outcome_envelope_v01`; component/auxiliary receipts and operation_counts. | A-E authority laws; F supplied-report aggregation. |

The other positive nodes prove exact geometry/current callable basis (01),
canonical projection/render (06), fresh collection rather than cache (07), and
validation of the same supplied report (08). Hostile10 also covers actual
negative projection-validator results with correct type/ref; hostile12 covers
component/auxiliary relationship corruption; hostile15 covers row099's exact
enclosing owner. These are bounded conformance cases, not universal security.

## Evidence, Reproduction and Limits

The appended register binds the actual I owner execution and frozen source
identities. All 24 focused nodes, direct two-collection validation, authority943,
release32 and guards ran after the ordinary implementation commit and before
its push. The new closure proposal does not repeat F runtime. Its P1/P2 full
authority/release results and final fourteen hashes belong to the external
proposal receipt, not this document's own hash dependency chain.

Start at [README](../README.md), then this checkpoint, then the linked contract,
runtime and test. Existing offline reproduction commands (instructions, not
new execution claims here), from an installed editable checkout:

```bash
W=$(mktemp -d /private/tmp/hedgehog-g2f-reproduce.XXXXXX)
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export TMPDIR="$W" PYTHONPYCACHEPREFIX="$W/pycache" COVERAGE_FILE="$W/coverage"
PYTHONPATH=. .venv/bin/python -m pytest -p no:cacheprovider -q tests/test_consolidated_gate2_gauntlet_g2_f_v01.py
PYTHONPATH=. .venv/bin/python -m demo.run_consolidated_gate2_gauntlet_g2_f_v01 > "$W/report.json"
```

The CLI uses the same public collector/validator/projector/renderer. Focused24
took about20minutes in the accepted committed run; the separate reviewed
two-collection helper took about19minutes. These are measurements, not bounds.
A new CLI collection is optional reproduction, not a substitute for the exact
reviewed helper's two-collection/nonmutation evidence. No installation or
external service is needed for these existing local commands.

BSEP is the semantic membrane; Semantic Architect proposes; runtime owns
topology. Roots decide independently. DRS, hashes, receipts, replay and report
aggregation are evidence, not authority. Historical replay remains available
after supersession; PRESENT execution does not. The helper's zero counts are
typed-report-derived, not operating-system monitoring. Its freshness scope
checks all declared containers and samples typed-carrier identities. The full
canonical render is not stored in the accepted archive; the executed helper
computed its hash. This reviewer has not regenerated it.

Only actual accepted owner closure can support the bounded internal name
"Hedgehog OS Operational Reference Kernel RC2". Public release, production
readiness/security certification, real integrations/effects and future Gates
remain NOT_CLAIMED. Frozen Gate1 completion/seam records remain evidence; the
current overlay supplies current status. Old passports remain historical.
Roadmap v3.1 execution order and v2.1 technical WHAT remain subordinate to
accepted contracts and the owner roadmap-pair ruling; no v2.5/v3.5 is invented.
No Gate3/4 reduction, domain demo or future runtime is authorized here.

## Immutable I Evidence Register

Audit SHA-256: `0f99d042f88da3e3b663305728c067894bf8012f1eed2046a83695f56b909067`. Audit role is independent source and recorded-execution review; evidence-only, not Root authority.

| Source | SHA-256 | Bytes | LF |
| --- | --- | --- | --- |
| `demo/run_consolidated_gate2_gauntlet_g2_f_v01.py` | `579ee6918220b20998ce68569787119176634e2a072dac11a770aa432cc5dd8d` | 399910 | 2506 |
| `tests/test_consolidated_gate2_gauntlet_g2_f_v01.py` | `6ed3b73c41fb14fd41e45ba8086043db3268bbe780e1c2e9030dd5b9802151c6` | 47633 | 925 |

Owner return: `HEDGEHOG_G2F_IMPLEMENTATION_OWNER_EXECUTION_V01_RETURN_20260907T161508Z.tar.gz`, SHA-256 `4f7d687c12ee156d4df508dc8dc9962cc8e476974d80419b1051d2db4b9b5319`, 4150723 bytes, 411 members/410 manifest rows. All 195 receipts and 390 streams were reconciled.

| Owner sequence | Actual phase | rc | Process seconds | stdout SHA-256 |
| --- | --- | --- | --- | --- |
| 83 | `commit_exact_two` | 0 | 0.038509 | `bd0c922639e6ddc637c00d7ecbd693662a056fd9a38242fdbf669bed4df64c5f` |
| 104 | `postcommit_guard` | 0 | 11.081561 | `c9e32c4a6605b7a346277a8c13fe2d3ecc4f508d197f1528f43a54c1b7511f4b` |
| 105 | `postcommit_guard_optimized` | 0 | 10.853474 | `c9e32c4a6605b7a346277a8c13fe2d3ecc4f508d197f1528f43a54c1b7511f4b` |
| 106 | `postcommit_focused_collection` | 0 | 1.165612 | `73b54278e71a1561b5238fe4a4638fac7aa0406d46e35242b7a2c29735eb58c9` |
| 107 | `postcommit_focused_tests` | 0 | 1206.094445 | `63ad85395293d82c9c4b08eeff1a34857fe754903e947eeddf2bb7121ab3303a` |
| 108 | `postcommit_direct_public_receipt` | 0 | 1129.881298 | `e80e8adae3b5ed8cd3cd2d24114dd41cea71c7f3b107e846341e71cee51192de` |
| 109 | `postcommit_authority_tests` | 0 | 428.445258 | `33f1b7f9320cff6250066561bfa0ad6675fd4c71836cefef331afd7c783a8d30` |
| 110 | `postcommit_release_tests` | 0 | 3.528123 | `a49019b3fc6ce86cefffad11e64002402fb049db4e483923e73d0d376cfb69d0` |
| 130 | `push_origin_main` | 0 | 1.976038 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| 150 | `final_guard` | 0 | 11.027711 | `c9e32c4a6605b7a346277a8c13fe2d3ecc4f508d197f1528f43a54c1b7511f4b` |

Recorded pytest summaries: `24 passed, 2 warnings in 1205.51s`; `943 passed in 427.78s`; `32 passed in 2.92s`. Direct JSON SHA-256 `e80e8adae3b5ed8cd3cd2d24114dd41cea71c7f3b107e846341e71cee51192de`, 2219 bytes/1LF. Reviewed helper SHA-256 `15befe856415b3c15672d6ff85c3292fa071b99ddd75ba686f408dd1bdadccd6`. Helper-computed render: 209138 bytes, SHA-256 `e1841f01bb17c943f39fbe1e594e3ecdb6cc5a076e0e4c102bd236b97efc87e1`. Derived geometry:181 rows/235primary/94component/2auxiliary/60causal rows/274edges/155new-to-new/8Root decisions/7laws. These are verified recorded executions, not new proposal runs.

### Complete Ordered Pytest IDs

```text
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_01_report_geometry_and_current_basis
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_02_causal_order_and_identity_lineage
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_03_informational_fast_path_heavy_skip
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_04_high_risk_multiroot_full_fractal_execution
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_05_packet_delta_revocation_supersession_chain
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_06_canonical_plain_projection_and_render
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_07_independent_fresh_collections_no_cache
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_positive_08_public_validator_accepts_actual_report
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_01_safe_informational_reuse
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_02_action_reuse_blocked
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_03_high_risk_multiroot_deep
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_04_revoke_before_fulfillment
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_05_superseded_replay_blocked
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_06_selective_recompute
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_dod_07_components_non_authority
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_08_drs_not_authority
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_09_router_not_authority
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_10_registry_not_authority
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_11_child_not_root
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_12_delta_not_authority
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_13_no_permission_revival
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_14_no_stale_packet_replay
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_15_no_aggregate_pass
tests/test_consolidated_gate2_gauntlet_g2_f_v01.py::test_g2f_hostile_16_zero_operations
```
