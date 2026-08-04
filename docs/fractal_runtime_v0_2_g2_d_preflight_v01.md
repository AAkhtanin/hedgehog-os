# Fractal Runtime v0.2 - Gate 2 / G2-D Architect Preflight

document_status: PREFLIGHT
document_revision: v0.1.10
guardian_review_status: ACCEPTED
g2d_preflight_accepted: true
repository_basis_branch: main
repository_basis_head: ba2e45be93aec6bc1f6de1891a9b50bb6546070d
repository_basis_origin_main: ba2e45be93aec6bc1f6de1891a9b50bb6546070d
gate_id: gate2_g2d_fractal_runtime_v0_2
gate_slice: G2-D
planning_only: true
implementation_authorized: false
implementation_started: false
r_h1_status: CLOSED_PASS
g2a_status: CLOSED_PASS
g2b_status: CLOSED_PASS
g2c_status: CLOSED_PASS
gate2_closed: false
g2e_started: false
g2f_started: false
public_release_claimed: false
rc2_claimed: false
quantum_roadmap_future_only: true

## 1. Purpose, Authority, and Scope

This document freezes the planning contract for Gate 2 slice G2-D, Fractal
Runtime v0.2. It authorizes no implementation. Its sole purpose is to define a
bounded, deterministic, runtime-owned topology and cell scheduler that may be
implemented only after separate owner authorization for each accepted slice.

The controlling route is:

```text
BSEP
-> semantic proposal
-> G2-C Root-reviewed ExecutionModeRouteEligibility
-> runtime-owned RuntimeExecutionTopology
-> bounded runtime work
-> Root
```

G2-D consumes existing authority; it creates none. It creates no truth,
permission, ActionCommitPacket, receipt, effect handle, DRS write,
FinalOutput, provider authority, connector authority, or real-world effect.
Topology creation is a visible local runtime structure, not an effect.

The sole intended canonical owner is a new Kernel module,
`hedgehog/kernel/fractal_runtime_v02.py`. Existing PlanGraph and Fractal proof
modules are not promoted into the canonical contract. G2-E continuous and
selective recomputation behavior is excluded.

## 2. Source-of-Truth and Conflict Resolution

Authority order is exact:

1. The explicit owner authorization that requested this preflight.
2. The owner route correction frozen in Section 1.
3. DeepTech Completion Roadmap v3.1 for Gate order and high-level G2-D duty.
4. Accepted G2-C preflight v0.1.6, implementation, audit, and checkpoint.
5. Accepted G2-A and G2-B preflights, implementations, audits, and checkpoints.
6. Current Human Passport, invariants, Machine Manifest, and Math Appendix.
7. Current committed Kernel/runtime contracts and tests.
8. Master Roadmap v2.1 as a non-binding technical donor when consistent with
   every higher source.
9. Historical Fractal and PlanGraph proof surfaces as classified donors only.

The DeepTech Completion Roadmap v3.1 and Master Roadmap v2.1 are owner-supplied
companion documents and are not tracked in this repository. Codex did not read
local copies. Guardian review supplied the controlling roadmap rulings used by
this correction. DeepTech v3.1 requires bounded depth and fan-out, budget
propagation, bounded revise, no-progress detection, partial failure,
backpressure, parent/child scope law, upward child return, and the existing
one-ABI `CausalConsumptionRefV01` law. Master v2.1 contributes only compatible
technical donor detail: Fractal cell input/result concepts, child monotonicity,
explicit queue states, eight budget dimensions, the integer progress formula,
and visible `DEADEND` or `NEEDS_USER` termination. These are guardian-supplied
owner-roadmap rulings, not locally inspected repository files.

No lower source can restore PlanGraph ownership, remove RouteEligibility,
create child Root authority, authorize provider-owned scheduling, or move G2-E
behavior into G2-D.

## 3. Repository Basis and Accepted Inventory

Repository basis is branch `main` at
`ba2e45be93aec6bc1f6de1891a9b50bb6546070d`, synchronized with
`origin/main`. Its parent is
`5d1c64942ec141a65ac6be9cb469d428a3cca73d`. The latest subject is
`Add future quantum-inspired mathematical roadmap v2.0`.

Accepted G2-C evidence:

- preflight commit: `4b33c8106dbb3d7b50596630cd9dcdcf3f84cfac`
- preflight SHA-256: `5bea2e49a6a5ff1c80df526a142329e7e218558f64c77be0a2f64294f2673077`
- implementation basis: `27a866ca06a331b4169c56abac9a460334d75539`
- audit commit: `72854bcdc85d19e9c6a6636f9a7eedd1929f03cb`
- audit SHA-256: `3f6aab5c26b486a463174a6d57a22097b8eee2dcd314433b27462117b21d73d5`
- closure commit: `5d1c64942ec141a65ac6be9cb469d428a3cca73d`
- checkpoint SHA-256: `28ba0de21cf6458a408911b0342d57db72ad6f6cf6e8e5aec8b87fb616802f0b`
- router module SHA-256: `29e6500ca2b6966d0b5068f9fa1cdc1ef937cb4e5c284ea3acc78b0e9103ca22`
- router schema SHA-256: `cd07223ffd6085682cee4a49781f5471997ad371b4cd3916d01c146ed7e33468`
- router tests SHA-256: `6903a7e4223f2d8c4712122fb88dbaa4b788ef84d5d85b53ce6ea1eacbbbbeec`
- two-domain proof SHA-256: `1d775010d0fdcba7d2ebbcadf50d0bc4815a99dc08785f2f6a0d635477ff8719`

The Quantum Roadmap commit is
`ba2e45be93aec6bc1f6de1891a9b50bb6546070d`; its document SHA-256 is
`c406dd84163634d55e23309a814d49c7a3ff30171059b7b95a1a38e2cc07e7b6`.
It remains future post-Gate-6 design only and changes no G2-D duty.

The complete connected review read these current files in full:

```text
AGENTS.md
README.md
specs/human_passport_v0_25.md
specs/invariants.md
specs/machine_manifest_v0_25.json
specs/math_appendix_v0_3.md
release/current_status_overlay_v01.json
release/claim_to_evidence_index.md
release/current_limitations.md
release/current_release_notes.md
docs/execution_mode_router_g2_c_preflight_v01.md
docs/audit_reports/auditor_execution_mode_router_g2_c_v01.log
docs/execution_mode_router_g2_c_checkpoint_v01.md
hedgehog/kernel/execution_mode_router_v01.py
schemas/execution_mode_router_v01.schema.json
tests/test_execution_mode_router_g2_c_v01.py
demo/run_execution_mode_router_g2_c_v01.py
hedgehog/kernel/__init__.py
hedgehog/kernel/abi_v01.py
schemas/kernel_artifact_v01.schema.json
hedgehog/kernel/transition_registry_v01.py
hedgehog/kernel/root_decision_v01.py
hedgehog/kernel/semantic_work_v01.py
hedgehog/kernel/trust_model_v01.py
hedgehog/kernel/integrity_replay_v01.py
hedgehog/kernel/effect_firewall_v01.py
tests/test_kernel_abi_v01.py
tests/test_transition_registry_v01.py
tests/test_root_decision_kernel_v01.py
tests/test_semantic_work_v01.py
tests/test_kernel_trust_model_v01.py
tests/test_kernel_integrity_replay_v01.py
docs/actionpacket_lifecycle_kill_switch_g2_a_preflight_v01.md
docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md
docs/audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log
hedgehog/action_commit_packet_v02.py
tests/test_action_commit_packet_lifecycle_g2_a_v01.py
docs/drs_semantic_address_space_reuse_certificate_g2_b_preflight_v01.md
docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md
docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log
hedgehog/drs_semantic_address_v01.py
hedgehog/drs_memory_resolution_v01.py
hedgehog/reuse_certificate_v01.py
tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py
hedgehog/fractal_cell_integration.py
hedgehog/fractal_dag_executor.py
hedgehog/fractal_fulfillment.py
hedgehog/bounded_actor_contracts.py
hedgehog/post_vv.py
hedgehog/gt_validator.py
hedgehog/root_orchestrator.py
demo/run_fractal_cell_runtime_integration_v01.py
tests/test_fractal_cell_runtime_integration_v01_runner.py
demo/run_fractal_cell_runtime.py
tests/test_fractal_cell_runtime_runner.py
demo/run_fractal_dag_executor_core.py
tests/test_fractal_dag_executor_core_runner.py
demo/run_controlled_fractal_dac_expansion_v01.py
tests/test_controlled_fractal_dac_expansion_v01_runner.py
demo/run_dual_fractal_coupling_v01.py
tests/test_dual_fractal_coupling_v01_runner.py
demo/run_full_semantic_e2e_v01.py
tests/test_full_semantic_e2e_v01_runner.py
demo/run_living_gauntlet_v01.py
tests/test_living_gauntlet_v01_runner.py
hedgehog/kernel/conformance_v01.py
demo/run_kernel_conformance_v01.py
tests/test_kernel_conformance_v01_runner.py
specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
tests/test_post_vv_runtime.py
tests/test_post_vv_from_result_proposal_runner.py
tests/test_gt_validator_runtime.py
tests/test_gt_from_validation_report_runner.py
hedgehog/time_model.py
schemas/result_proposal.schema.json
schemas/vv_report.schema.json
schemas/common.schema.json
schemas/time_envelope.schema.json
schemas/gt_report.schema.json
tests/test_repository_release_spine_v01.py
```

The complete corrected read register contains 80 paths. The v0.1.10 correction
basis is v0.1.9 SHA-256
`eac205054813e8f2a9490acfaaa76ae63d1ca015f9e4be7f65e0758d666ed15c`,
294,348 bytes, 4,328 lines, mode `0644`. The v0.1.8, v0.1.7, v0.1.6, v0.1.5,
v0.1.4, v0.1.3, v0.1.2, v0.1.1, and v0.1 correction bases remain historical
SHA-256 values
`66888c26c6160ae191926a829ed9f11f2ede71a04927a4a1f162ee9dcbb10832`,
`8ad77812060365cc2c5f78a7dd1df7624e79771ef12af5a4cf0fa844b6f61110`,
`6130f4e40ecb1add06aa52a0195a37b7592da0551bdb5bd59f0f511f7b973bce`,
`954eef1489628e7a64b646f9c0af03694fe5a1b6a19b23c4d9282b07c0288763`,
`b5af9b92a87b04ebcbf214f732ce53491eb73dca9b15334a6aab98c739dfee34`,
`a420e3e0f17a75b3bf73caaca6313576164d9baa574c84ec680bf7acfd0cc889`,
`bd1ad7639f723fcf22c6d5216d2cbfd4538b763424195cadf258eb2fc92e264e`,
`3ae3872d1396c611dc6e7b9d97470cca39020c46f175cedd146b83beca0ea24a`
and `fbcae5f64b7976203cd897aaa42697ba3775cd61f3bc2f94d7de7092056348bd`.

## 4. Architecture Lock

The exact authority sequence is:

1. Validate the actual complete G2-C source family structurally and
   contextually.
2. Accept only the actual `ExecutionModeRouteEligibility` `KernelArtifactV01`
   produced after existing Root review and the post-Root G2-C Transition.
3. Require `downstream_consumption_class=RUNTIME_TOPOLOGY_ELIGIBLE`.
4. Derive a source binding from the full object family, never an ID alone.
5. Derive the G2-D Transition decision from that binding and the actual Root
   commit carried by the source family.
6. Construct the runtime-owned topology deterministically from validated local
   policy, capability, scope, and budget facts.
7. Schedule only bounded local compute cells through the explicit queue.
8. Return child evidence upward through parent validation, current Post V&V,
   current GT advisory, and finally Root review.

These are forbidden topology permissions: `RootExecutionModeDecisionV01`, an
execution-mode proposal, a caller boolean, a mode string, a provider result, a
DRS object, a ReuseCertificate, an old packet, a receipt, or prior permission.

Provider or model output owns no topology, node, edge, assignment, budget,
queue state, parent/child scope, revise decision, permission, or authority. A
child cell never becomes Root. A child result cannot target user FinalOutput,
Root FinalOutput, an Architect command, packet creation, permission creation,
effect execution, connector execution, or DRS write.

## 5. Current Fractal and Topology Inventory

The current ABI reserves the literal `RuntimeExecutionTopology`, but no
Kernel-owned v0.2 topology dataclass or contextual G2-D schema exists. This is
the intended append seam, not a second ABI family.

The static caller scan covered all tracked text for the owner-specified terms.
The core counts were: `RuntimeExecutionTopology=29`,
`ExecutionModeRouteEligibility=16`, `RUNTIME_TOPOLOGY_ELIGIBLE=31`,
`SHORTCUT_RETURN_TO_ROOT=24`, `TERMINAL_NO_CONSUMPTION=28`,
`FractalCell=82`, `fractal_cell=454`, `fractal_dag=336`,
`PlanGraph=1023`, `FinalOutput=1490`, `max_depth=152`,
`max_parallelism=43`, `revise=115`, `budget=669`, and `queue=164`.
The exact tokens `max_fan_out`, `max_total_cells`, `no_progress`, and
`partial_failure` have no current tracked occurrence; `backpressure` has one
unrelated occurrence. G2-D therefore defines these laws explicitly instead of
pretending an existing contract owns them.

Current G2-C and shared Kernel files contain the only accepted eligibility,
ABI, Transition, SemanticWork, Root, trust, integrity, and effect-boundary
contracts. Existing Fractal modules expose PlanGraph-bound proof dataclasses,
deterministic DAG algorithms, bounded actor envelopes, and historical
parent-return behavior. They do not bind the complete G2-C source family and
cannot become the G2-D implementation owner.

## 6. Canonical-versus-Historical Classification

| Classification | Exact disposition |
|---|---|
| `CURRENT_CANON` | Current lifecycle surfaces and the owner route correction. Only their current status and authority boundaries control. |
| `ACCEPTED_G2C_SOURCE` | G2-C preflight, audit, checkpoint, router, schema, tests, and deterministic proof. These are read-only source contracts. |
| `ACCEPTED_SHARED_KERNEL` | Kernel ABI, Transition Registry, Root Decision, SemanticWork, trust, integrity, Effect Firewall, package facade, current Post V&V and GT validation seams, and their tests. They remain one shared family; only the additive explicit-time D4 changes are allowed. |
| `LEGACY_PROOF_DONOR` | `fractal_cell_integration.py`, `fractal_dag_executor.py`, `fractal_fulfillment.py`, `bounded_actor_contracts.py`, `root_orchestrator.py`, and the named Fractal/full-semantic demos and tests. Algorithms and regression expectations may inform G2-D; their types and ownership do not. |
| `HISTORICAL_DOCUMENTATION` | Historical Fractal, PlanGraph, checkpoint, audit, walkthrough, and design references. They remain evidence of earlier proofs only. |
| `DOCUMENTATION_DRIFT` | Current AGENTS/README route prose that omits the explicit G2-C Root-reviewed RouteEligibility hop. The owner correction controls; G2-D does not edit those documents. |
| `FUTURE_G2E` | Dependency fingerprints, affected-subgraph calculation, selective recomputation, downstream invalidation, continuous runtime, and delta runtime. None is implemented in G2-D. |
| `OUT_OF_SCOPE` | Unrelated FinalOutput, budget, queue, PlanGraph, provider, live lane, quantum, schema, demo, and historical occurrences. They create no G2-D obligation. |

`schemas/plan_graph.schema.json` and every PlanGraph caller are historical proof
contracts for this slice. No adapter, migration, caller migration, cleanup,
deletion, compatibility layer, or alias is planned.

## 7. Contradiction Register

Versions v0.1.1 through v0.1.9 resolved blockers A-BH. The final guardian
constructibility review identified blockers BI-BJ; v0.1.10 resolves them and
is guardian ACCEPTED under the express owner authorization controlling this
correction. Implementation remains unauthorized and unstarted:

1. **BI - typed PARENT_RETURN input family.** Signature 90 now receives the
   actual pre-Post-V&V terminal tuple, child results, partial failures,
   ResultProposal, Post V&V report, GT advisory, and exact three-report PASS
   family. The evaluator independently reconstructs those reports and derives
   observations, reasons, and the five terminal mappings from actual objects.
2. **BJ - valid gate denial versus structural corruption.** The accepted
   no-child BLOCKED branch admits only structurally valid policy, authority,
   scope, or budget denial. Identity, lineage, artifact, predecessor, event,
   state, counter, or other structural corruption returns the first
   FAIL_CLOSED report and creates no terminal queue, merge input, causal row,
   or accepted bundle.

All dependent fields, schemas, serializers, input-ref enums, templates,
classifications, signatures, precheck branches, observations, queue reasons,
Transition guards and inputs, ABI parent forms, merge inputs, actual child and
failure cardinality, proposal timing, PARENT_RETURN mapping, report counts,
causal rows, logs, slices, validation groups, proof cases, and
Living/Conformance meanings are reconciled below. Existing route wording drift
and historical PlanGraph or Fractal ownership remain classified non-blocking
evidence. Acceptance comes solely from this exact owner-authorized guardian
ruling and does not authorize G2-D1 or implementation.

## 8. G2-C RouteEligibility Consumption Contract

G2-C profile identity is
`execution_mode_router_g2c_abi_profile_v01`. Its Transition profile identity is
`execution_mode_router_g2c_transition_profile_v01`. The RouteEligibility
artifact identity domain is
`HEDGEHOG_EXECUTION_MODE_ROUTE_ELIGIBILITY_KERNEL_ARTIFACT_V01` with prefix
`emabi_route_v01:`. Its parent is the G2-C decision artifact and its exact
contextual validator rebuilds the complete source family.

Consumption classes are frozen:

| Class | Modes or outcomes | G2-D law |
|---|---|---|
| `SHORTCUT_RETURN_TO_ROOT` | `deterministic`, `sealed_replay`, `direct_informational_reuse` | Return upward. G2-D rejects consumption and creates no topology. |
| `RUNTIME_TOPOLOGY_ELIGIBLE` | `memory_informed`, `local_slm`, `cloud_llm`, `full_semantic`, `full_fractal` | The only accepted G2-D source class. |
| `TERMINAL_NO_CONSUMPTION` | `blocked`, `needs_user`, and rejected Root outcomes | G2-D rejects consumption and creates no topology. |

The topology source binding carries the actual RouteEligibility artifact ID
and canonical artifact SHA-256, proposal and Root-decision artifact IDs,
pre-Root and post-Root G2-C Transition IDs, content-derived Registry ID, G2-C
ABI profile ID, time envelope, traces, parents, request, transaction, Root,
domain, mode, and accepted scope. A source string or structurally valid foreign
artifact is insufficient.

The binding also reconstructs every G2-C value that controls topology:
`selected_local_mode_profile_id`, `selected_feasibility_row_id`,
`selected_safe_depth_rank`, `selected_expected_cost_units`,
`required_downstream_capability_ids`, `source_mode_profile_set_id`,
`source_policy_snapshot_id`, `source_capability_snapshot_id`,
`permitted_narrower_scope_refs`, `source_root_decision_result_id`, and
`source_root_transition_decision_id`. Their owners are, respectively, the
actual selected feasibility row, proposal, selected local mode profile, local
routing snapshot, Root source result, Root decision, and G2-C pre/post-Root
Transitions. Every topology-eligible selection must supply every value. The
builder derives them from objects, never from copied labels or IDs; substitution
of any one source/profile/cost/capability/policy/scope field fails closed.

`FractalRuntimePolicyV02` has one exact source-derived value table. The actual
G2-C family is validated first; its capability and scope values build the
content-derived policy; that policy then participates in
`FractalRuntimeSourceContextV02`; only then is
`RuntimeTopologySourceBindingV02` built. The direction is therefore actual
G2-C family -> source-derived policy -> source context -> source binding, with
no source-binding/policy identity cycle.

```text
policy_id=frpolicy_v02:<64 lowercase hex over every later field in declared order>
policy_profile_id=fractal_runtime_policy_g2d_v02
policy_version=v0.2
allowed_modes=TOPOLOGY_ELIGIBLE_MODES
allowed_node_kinds=NODE_KINDS
allowed_edge_kinds=EDGE_KINDS
allowed_assignment_kinds=ASSIGNMENT_KINDS
recursive_mode=full_fractal
recursive_capability_id=capability:g2d:fractal_child:v02
allowed_capability_ids=source-required capabilities followed by documented local G2-D capabilities, with no duplicate
forbidden_claims=FORBIDDEN_OUTPUT_KINDS
permitted_child_scope_refs=actual source permitted_narrower_scope_refs in source order
reference_child_count=2
queue_profile_id=node_work_queue_v02
budget_profile_id=fractal_runtime_budget_g2d_v02
max_depth=3
max_fan_out=4
max_total_cells=21
max_parallelism=4
max_revise_count=2
max_consecutive_no_progress=2
max_wall_time_units=1000
max_token_budget=100000
max_provider_calls=0
root_review_required=true
authority_created=false
permission_created=false
real_world_effects_count=0
```

`POLICY_IDS` is retired. The only fixed profile vocabulary is
`POLICY_PROFILE_IDS=(fractal_runtime_policy_g2d_v02)`. No caller supplies an
accepted policy identity. The structural builder accepts only the two
source-derived semantic tuples, validates them, fixes every profile/limit and
nonclaim field, and derives `policy_id` under
`HEDGEHOG_FRACTAL_RUNTIME_V02_POLICY` with prefix `frpolicy_v02:`. Every
`runtime_policy_id` and `policy_id` in source binding, seed, budget,
backpressure, topology payload, trace, and contextual validation is this
content-derived identity. The fixed literal occurs only as
`policy_profile_id`; queue and budget profile IDs remain distinct. Identity or
profile substitution fails closed with
`g2d_policy_profile_identity_mismatch`.

The local capability suffix is exactly
`(capability:g2d:local_runtime:v02,capability:g2d:post_vv:v02,
capability:g2d:gt_advisory:v02,capability:g2d:parent_return:v02,
capability:g2d:fractal_child:v02)`. It cannot invent provider, connector,
packet, permission, effect, Root, or FinalOutput capability. `EQUAL` scope
requires byte-equal refs. `NARROWER` requires the child ref in both the actual
G2-C `permitted_narrower_scope_refs` and policy
`permitted_child_scope_refs`; the default policy deliberately preserves the
source tuple unchanged, so both independently validated axes must agree.
Labels, prefixes, suffixes, or caller assertions
cannot prove narrowing.

## 9. Canonical Types, Identity, Serialization, and Reasons

### 9.1 Exact type geometry

```text
TOTAL_G2D_TYPE_COUNT=20
SERIALIZED_IDENTITY_TYPE_COUNT=18
RUNTIME_ONLY_CONTEXT_TYPE_COUNT=2
SCHEMA_DEFINITION_COUNT=18
```

All types are exact frozen dataclasses. Subclasses are rejected where an exact
type is required. Field order and types are:

```text
FractalRuntimePolicyV02(
  policy_id: str, policy_profile_id: str, policy_version: str,
  allowed_modes: tuple[str, ...],
  allowed_node_kinds: tuple[str, ...], allowed_edge_kinds: tuple[str, ...],
  allowed_assignment_kinds: tuple[str, ...], recursive_mode: str,
  recursive_capability_id: str,
  allowed_capability_ids: tuple[str, ...],
  forbidden_claims: tuple[str, ...],
  permitted_child_scope_refs: tuple[str, ...],
  reference_child_count: int, queue_profile_id: str,
  budget_profile_id: str, max_depth: int, max_fan_out: int,
  max_total_cells: int, max_parallelism: int, max_revise_count: int,
  max_consecutive_no_progress: int, max_wall_time_units: int,
  max_token_budget: int, max_provider_calls: int,
  root_review_required: bool, authority_created: bool,
  permission_created: bool, real_world_effects_count: int
)

FractalRuntimeBudgetV02(
  budget_id: str, policy_id: str, topology_seed_id: str,
  allocation_parent_budget_id: str | None,
  predecessor_budget_id: str | None, owning_cell_id: str,
  budget_scope: str, budget_state: str, budget_event_kind: str,
  budget_event_ref: str, max_depth: int, max_fan_out: int,
  max_total_cells: int, max_parallelism: int, max_revise_count: int,
  max_wall_time_units: int, max_token_budget: int, max_provider_calls: int,
  consumed_wall_time_units: int, consumed_token_budget: int,
  consumed_provider_calls: int, consumed_cell_count: int,
  consumed_revise_count: int, current_parallelism: int,
  remaining_wall_time_units: int, remaining_token_budget: int,
  remaining_provider_calls: int, remaining_cell_count: int,
  remaining_revise_count: int, remaining_parallel_slots: int,
  root_review_required: bool, authority_created: bool,
  permission_created: bool, action_commit_packet_created: bool,
  receipt_created: bool, final_output_created: bool,
  drs_write_created: bool, real_world_effects_count: int
)

RuntimeTopologySourceBindingV02(
  source_binding_id: str, request_id: str, transaction_id: str,
  owning_root_id: str, domain_id: str, accepted_mode: str,
  accepted_scope_ref: str, route_eligibility_artifact_id: str,
  route_eligibility_artifact_sha256: str,
  source_decision_artifact_id: str, source_proposal_artifact_id: str,
  selected_local_mode_profile_id: str,
  selected_feasibility_row_id: str,
  selected_safe_depth_rank: int,
  selected_expected_cost_units: int,
  required_downstream_capability_ids: tuple[str, ...],
  source_mode_profile_set_id: str,
  source_policy_snapshot_id: str,
  source_capability_snapshot_id: str,
  permitted_narrower_scope_refs: tuple[str, ...],
  source_root_decision_result_id: str,
  source_root_transition_decision_id: str,
  proposal_transition_decision_id: str,
  post_root_transition_decision_id: str, transition_registry_id: str,
  g2c_abi_profile_id: str, downstream_action_packet_required: bool,
  runtime_policy_id: str, source_time_envelope_ref: str,
  source_trace_refs: tuple[str, ...], source_parent_refs: tuple[str, ...],
  root_review_required: bool, authority_created: bool,
  permission_created: bool, real_world_effects_count: int
)

RuntimeTopologySeedV02(
  topology_seed_id: str, seed_version: str, profile_id: str,
  request_id: str, transaction_id: str, owning_root_id: str,
  domain_id: str, accepted_mode: str, accepted_scope_ref: str,
  source_binding_id: str, runtime_policy_id: str, root_cell_id: str,
  source_time_envelope_ref: str, trace_refs: tuple[str, ...],
  parent_refs: tuple[str, ...], root_review_required: bool,
  authority_created: bool, permission_created: bool,
  real_world_effects_count: int
)

RuntimeTopologyNodeV02(
  node_id: str, topology_seed_id: str, accepted_mode: str, node_kind: str,
  canonical_index: int, depth: int, scope_ref: str,
  cell_binding_class: str, scope_binding_class: str,
  budget_binding_class: str,
  required_capability_ids: tuple[str, ...],
  allowed_capability_ids: tuple[str, ...], forbidden_claims: tuple[str, ...],
  input_ref_derivation_class: str, input_refs: tuple[str, ...],
  trace_refs: tuple[str, ...],
  expected_output_kind: str,
  required: bool, recursive_expansion_allowed: bool,
  root_review_required: bool, authority_created: bool,
  permission_created: bool, real_world_effects_count: int
)

RuntimeTopologyEdgeV02(
  edge_id: str, topology_seed_id: str, source_node_id: str,
  target_node_id: str, edge_kind: str, canonical_index: int,
  cell_projection_class: str,
  required: bool, evidence_flow_allowed: bool,
  authority_flow_allowed: bool, trace_refs: tuple[str, ...],
  root_review_required: bool
)

RuntimeAssignmentV02(
  assignment_id: str, topology_seed_id: str, node_id: str,
  canonical_index: int, assignment_kind: str,
  executor_component_id: str, capability_ids: tuple[str, ...],
  cell_binding_class: str, scope_binding_class: str,
  budget_binding_class: str,
  provider_call_allowed: bool, network_call_allowed: bool,
  connector_call_allowed: bool, trace_refs: tuple[str, ...],
  root_review_required: bool,
  authority_created: bool, permission_created: bool,
  effect_created: bool, real_world_effects_count: int
)

RuntimeExecutionTopologyV02(
  topology_id: str, topology_version: str, topology_seed_id: str,
  request_id: str,
  transaction_id: str, owning_root_id: str, domain_id: str,
  accepted_mode: str, accepted_scope_ref: str, source_binding_id: str,
  source_route_eligibility_artifact_id: str,
  source_root_decision_artifact_id: str,
  source_proposal_artifact_id: str, runtime_policy_id: str,
  ordered_node_ids: tuple[str, ...], ordered_edge_ids: tuple[str, ...],
  ordered_assignment_ids: tuple[str, ...], root_cell_id: str,
  global_budget_id: str, time_envelope_ref: str, trace_refs: tuple[str, ...],
  parent_refs: tuple[str, ...], root_review_required: bool,
  authority_created: bool, permission_created: bool,
  action_commit_packet_created: bool, receipt_created: bool,
  final_output_created: bool, drs_write_created: bool,
  provider_calls: int, network_calls: int, real_world_effects_count: int
)

ParentChildScopeProjectionV02(
  projection_id: str, topology_id: str, parent_cell_id: str,
  child_cell_id: str, parent_scope_ref: str, child_scope_ref: str,
  scope_relation: str, budget_relation: str,
  parent_allowed_capability_ids: tuple[str, ...],
  child_allowed_capability_ids: tuple[str, ...],
  parent_forbidden_claims: tuple[str, ...],
  child_forbidden_claims: tuple[str, ...], parent_ttl_units: int,
  child_ttl_units: int, parent_budget_id: str, child_budget_id: str,
  global_budget_id: str,
  child_depth: int, parent_lineage_refs: tuple[str, ...],
  child_lineage_refs: tuple[str, ...], proof_refs: tuple[str, ...],
  root_review_required: bool, authority_created: bool,
  permission_created: bool, final_output_created: bool,
  real_world_effects_count: int
)

FractalCellInputV02(
  cell_input_id: str, topology_id: str, cell_id: str,
  parent_cell_id: str | None, request_id: str, transaction_id: str,
  owning_root_id: str, domain_id: str, accepted_mode: str,
  scope_projection_id: str | None, scope_ref: str,
  cell_budget_id: str, global_budget_id: str,
  ordered_initial_queue_entry_ids: tuple[str, ...],
  ordered_required_queue_entry_ids: tuple[str, ...],
  cell_depth: int, requested_child_count: int,
  ordered_planned_child_cell_ids: tuple[str, ...],
  ordered_node_ids: tuple[str, ...],
  evidence_refs: tuple[str, ...], context_refs: tuple[str, ...],
  required_output_kinds: tuple[str, ...],
  forbidden_output_kinds: tuple[str, ...], initial_revise_count: int,
  time_envelope_ref: str, trace_refs: tuple[str, ...],
  root_review_required: bool, authority_created: bool,
  permission_created: bool, action_commit_packet_created: bool,
  final_output_created: bool, real_world_effects_count: int
)

FractalCellQueueEntryV02(
  queue_entry_id: str, topology_id: str, topology_seed_id: str,
  cell_id: str, parent_cell_id: str | None, node_id: str,
  planned_child_cell_id: str | None, cell_depth: int,
  scope_ref: str, cell_budget_id: str, global_budget_id: str,
  state: str, prior_state: str | None,
  predecessor_queue_entry_id: str | None,
  predecessor_relation: str,
  transition_decision_id: str, canonical_priority: int,
  node_instance_sequence: int, snapshot_sequence: int,
  admission_round: int,
  queue_reason_codes: tuple[str, ...],
  observed_output_refs: tuple[str, ...],
  observed_evidence_refs: tuple[str, ...],
  advisory_refs: tuple[str, ...], lineage_refs: tuple[str, ...],
  root_review_required: bool, authority_created: bool,
  permission_created: bool, final_output_created: bool,
  drs_write_created: bool, real_world_effects_count: int
)

FractalReviseObservationV02(
  observation_id: str, topology_id: str, cell_id: str,
  queue_entry_id: str, revision_index: int,
  newly_validated_evidence_count: int,
  newly_resolved_constraints_count: int,
  newly_accepted_outputs_count: int,
  newly_introduced_conflicts_count: int, progress_units: int,
  consecutive_non_positive_count: int,
  max_consecutive_non_positive_count: int, revise_eligible: bool,
  derived_terminal_state: str | None, reason_codes: tuple[str, ...],
  cell_budget_before_id: str, global_budget_before_id: str,
  trace_refs: tuple[str, ...], root_review_required: bool,
  authority_created: bool, real_world_effects_count: int
)

FractalPartialFailureRecordV02(
  partial_failure_id: str, topology_id: str, parent_cell_id: str,
  child_cell_id: str, child_result_id: str, failure_stage: str,
  reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...],
  evidence_refs: tuple[str, ...], trace_refs: tuple[str, ...],
  allocated_cell_budget_id: str, final_cell_budget_id: str,
  global_budget_id: str,
  retry_eligible: bool, revise_eligible: bool, required_child: bool,
  sibling_independent: bool, parent_disposition: str,
  root_review_required: bool, authority_created: bool,
  permission_created: bool, final_output_created: bool,
  real_world_effects_count: int
)

FractalBackpressureStateV02(
  backpressure_id: str, topology_id: str, policy_id: str,
  evaluated_round: int, queue_capacity: int, running_count: int,
  ready_count: int, pending_count: int,
  deferred_queue_entry_ids: tuple[str, ...],
  admission_order: tuple[str, ...], backpressure_reason: str,
  reason_codes: tuple[str, ...],
  no_work_dropped: bool, lineage_refs: tuple[str, ...], global_budget_id: str,
  root_review_required: bool, authority_created: bool,
  permission_created: bool, real_world_effects_count: int
)

FractalCellResultV02(
  result_id: str, topology_id: str, topology_seed_id: str, cell_id: str,
  parent_cell_id: str | None, cell_depth: int, cell_input_id: str,
  ordered_terminal_queue_entry_ids: tuple[str, ...],
  ordered_child_result_ids: tuple[str, ...],
  outcome: str, accepted_output_refs: tuple[str, ...],
  evidence_refs: tuple[str, ...], pre_result_validation_report_id: str,
  post_vv_report_ref: str, gt_advisory_ref: str,
  partial_failure_ids: tuple[str, ...], allocated_cell_budget_id: str,
  final_cell_budget_id: str, global_budget_id: str, scope_ref: str,
  reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...],
  trace_refs: tuple[str, ...], parent_return_required: bool,
  root_review_required: bool, authority_created: bool,
  permission_created: bool, action_commit_packet_created: bool,
  receipt_created: bool, final_output_created: bool,
  drs_write_created: bool, real_world_effects_count: int
)

FractalRuntimeTraceV02(
  trace_id: str, topology_id: str, topology_seed_id: str,
  source_binding_id: str,
  ordered_queue_entry_ids: tuple[str, ...],
  state_transition_decision_ids: tuple[str, ...],
  cell_input_ids: tuple[str, ...], cell_result_ids: tuple[str, ...],
  scope_projection_ids: tuple[str, ...], revise_observation_ids: tuple[str, ...],
  partial_failure_ids: tuple[str, ...], backpressure_state_ids: tuple[str, ...],
  budget_ids: tuple[str, ...], abi_artifact_refs: tuple[str, ...],
  transition_refs: tuple[str, ...], parent_return_refs: tuple[str, ...],
  root_review_required: bool, provider_calls: int, model_calls: int,
  network_calls: int, connector_calls: int, external_drs_calls: int,
  real_world_effects_count: int
)

FractalRuntimeReportV02(
  report_id: str, report_version: str, profile_id: str,
  topology_id: str, topology_seed_id: str, topology_artifact_id: str,
  source_binding_id: str,
  request_id: str, transaction_id: str, owning_root_id: str,
  domain_id: str, accepted_mode: str, accepted_scope_ref: str,
  runtime_outcome: str, ordered_cell_result_ids: tuple[str, ...],
  completed_cell_count: int, degraded_cell_count: int,
  blocked_cell_count: int, needs_user_cell_count: int,
  deadend_cell_count: int, queue_entry_ids: tuple[str, ...],
  backpressure_state_ids: tuple[str, ...], runtime_trace_id: str,
  final_budget_id: str, parent_return_transition_decision_id: str,
  parent_return_refs: tuple[str, ...], report_status: str,
  reason_codes: tuple[str, ...], topology_created_count: int,
  provider_calls: int, model_calls: int, network_calls: int,
  connector_calls: int, external_drs_calls: int,
  action_commit_packets_created: int, permissions_created: int,
  receipts_created: int, final_outputs_created: int, drs_writes: int,
  authority_created_count: int, real_world_effects_count: int,
  root_review_required: bool
)

FractalRuntimeValidationReportV02(
  validation_report_id: str, validation_target: str,
  validated_object_id: str | None, status: str, failure_stage: str,
  reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...],
  return_to_root_required: bool, root_review_required: bool,
  authority_created: bool, permission_created: bool,
  action_commit_packet_created: bool, final_output_created: bool,
  drs_write_created: bool, real_world_effects_count: int
)

FractalRuntimeSourceContextV02(
  transition_registry: TransitionRegistryV01,
  g2c_source_context: ExecutionModeSourceContextV01,
  router_input: ExecutionModeRouterInputV01,
  proposal: ExecutionModeProposalV01,
  proposal_artifact: KernelArtifactV01,
  proposal_transition_decision: TransitionDecisionV01,
  review_input: RootExecutionModeReviewInputV01,
  decision: RootExecutionModeDecisionV01,
  root_kernel: RootDecisionKernelV01,
  root_decision_input: RootDecisionInputV01,
  root_decision_result: RootDecisionResultV01,
  decision_artifact: KernelArtifactV01,
  root_route_transition_decision: TransitionDecisionV01,
  route_eligibility_artifact: KernelArtifactV01,
  runtime_policy: FractalRuntimePolicyV02
)

FractalRuntimeExecutionBundleV02(
  source_context: FractalRuntimeSourceContextV02,
  source_binding: RuntimeTopologySourceBindingV02,
  topology_seed: RuntimeTopologySeedV02,
  budgets: tuple[FractalRuntimeBudgetV02, ...],
  topology_nodes: tuple[RuntimeTopologyNodeV02, ...],
  topology_edges: tuple[RuntimeTopologyEdgeV02, ...],
  runtime_assignments: tuple[RuntimeAssignmentV02, ...],
  topology: RuntimeExecutionTopologyV02,
  topology_artifact: KernelArtifactV01,
  queue_entries: tuple[FractalCellQueueEntryV02, ...],
  queue_artifacts: tuple[KernelArtifactV01, ...],
  scope_projections: tuple[ParentChildScopeProjectionV02, ...],
  cell_inputs: tuple[FractalCellInputV02, ...],
  revise_observations: tuple[FractalReviseObservationV02, ...],
  partial_failures: tuple[FractalPartialFailureRecordV02, ...],
  backpressure_states: tuple[FractalBackpressureStateV02, ...],
  validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
  result_proposals: tuple[dict[str, object], ...],
  post_vv_reports: tuple[dict[str, object], ...],
  gt_advisory_reports: tuple[dict[str, object], ...],
  cell_results: tuple[FractalCellResultV02, ...],
  result_artifacts: tuple[KernelArtifactV01, ...],
  runtime_trace: FractalRuntimeTraceV02,
  runtime_report: FractalRuntimeReportV02,
  report_artifact: KernelArtifactV01,
  transition_decisions: tuple[TransitionDecisionV01, ...],
  causal_consumption_refs: tuple[CausalConsumptionRefV01, ...]
)
```

The correction-sensitive canonical field counts remain exact:

```text
FractalRuntimeBudgetV02=38
FractalPartialFailureRecordV02=23
FractalBackpressureStateV02=19
FractalCellResultV02=32
FractalRuntimeTraceV02=23
FractalRuntimeReportV02=42
```

### 9.2 Exact enums

```text
TOPOLOGY_ELIGIBLE_MODES=(memory_informed,local_slm,cloud_llm,full_semantic,full_fractal)
NODE_KINDS=(MEMORY_CONTEXT,LOCAL_MODEL_DECLARATION,CLOUD_MODEL_DECLARATION,SEMANTIC_ACTOR,SEMANTIC_MERGE,FRACTAL_CELL,FRACTAL_MERGE,POST_VV,GT_ADVISORY,PARENT_RETURN)
EDGE_KINDS=(DATA_DEPENDENCY,CONTROL_DEPENDENCY,PARENT_CHILD,VALIDATION,RETURN)
ASSIGNMENT_KINDS=(LOCAL_DETERMINISTIC,LOCAL_MODEL_DECLARED,CLOUD_MODEL_DECLARED,SEMANTIC_ACTOR,FRACTAL_CHILD,VALIDATOR,ADVISORY,PARENT_RETURN)
CELL_BINDING_CLASSES=(CURRENT_CELL,CURRENT_CELL_CHILD_SLOT)
SCOPE_BINDING_CLASSES=(CURRENT_CELL_SCOPE,PERMITTED_CHILD_SCOPE)
BUDGET_BINDING_CLASSES=(CURRENT_CELL_BUDGET,CHILD_ALLOCATION_BUDGET)
BUDGET_STATES=(ALLOCATED,ACTIVE,FINAL)
BUDGET_SCOPES=(ROOT_GLOBAL_AND_CELL,CHILD_CELL_LOCAL)
BUDGET_EVENT_KINDS=(INITIAL_ALLOCATION,ACTIVATE,CELL_CREATE,START_NODE,FINISH_NODE,REVISE,CHILD_AGGREGATE,FINALIZE)
INPUT_REF_DERIVATION_CLASSES=(SOURCE_CONTEXT,PREDECESSOR_OUTPUTS,FAN_IN_OUTPUTS_0_1_2,PREDECESSOR_AND_CHILD_SLOT_1,PREDECESSOR_AND_CHILD_SLOT_2,FAN_IN_CHILD_SLOT_RETURNS_1_2)
CELL_PROJECTION_CLASSES=(ROOT_CELL_PROJECTION,FRACTAL_LEAF_PROJECTION)
QUEUE_STATES=(PENDING,READY,RUNNING,VALIDATING,COMPLETED,DEGRADED,BLOCKED,NEEDS_USER,DEADEND)
NODE_TERMINAL_OUTCOMES=(COMPLETED,DEGRADED,BLOCKED,NEEDS_USER,DEADEND)
CELL_OUTCOMES=(COMPLETED,DEGRADED,BLOCKED,NEEDS_USER,DEADEND)
VALIDATION_STATUSES=(PASS,FAIL_CLOSED)
POLICY_PROFILE_IDS=(fractal_runtime_policy_g2d_v02)
PROFILE_IDS=(fractal_runtime_g2d_profile_v02)
TOPOLOGY_VERSIONS=(v0.2)
REPORT_VERSIONS=(v0.2)
EXPECTED_OUTPUT_KINDS=(MEMORY_CONTEXT_OUTPUT,LOCAL_MODEL_DECLARATION_OUTPUT,CLOUD_MODEL_DECLARATION_OUTPUT,SEMANTIC_ACTOR_OUTPUT,SEMANTIC_MERGE_OUTPUT,FRACTAL_CELL_OUTPUT,FRACTAL_MERGE_OUTPUT,POST_VV_REPORT,GT_ADVISORY_REPORT,PARENT_RETURN_EVIDENCE)
FORBIDDEN_OUTPUT_KINDS=(FINAL_OUTPUT,ROOT_FINAL_OUTPUT,ACTION_PERMISSION,ACTION_COMMIT_PACKET,EVIDENCE_RECEIPT,EFFECT_REQUEST,CONNECTOR_COMMAND,DRS_WRITE,PARENT_ARCHITECT_COMMAND,ROOT_AUTHORITY_CLAIM)
FAILURE_STAGES=(NONE,SOURCE_CONTEXT,POLICY,SOURCE_BINDING,ROOT_CELL_ID,TOPOLOGY_SEED,BUDGET,NODE,EDGE,ASSIGNMENT,TOPOLOGY,QUEUE,SCOPE,CELL_INPUT,RESULT_PROPOSAL,CELL_RESULT_PRECONDITIONS,POST_VV,GT,CELL_RESULT,REVISE,PARTIAL_FAILURE,BACKPRESSURE,RUNTIME_TRACE,ABI,TRANSITION,CAUSAL_CONSUMPTION,CAUSAL_COUNTERFACTUAL,PARENT_RETURN,REPORT,COMPLETE_PROFILE)
FAILURE_STAGE_COUNT=30
PARENT_DISPOSITIONS=(COMPLETED,DEGRADED,BLOCKED,NEEDS_USER,DEADEND)
BACKPRESSURE_REASONS=(PARALLELISM_CAPACITY_EXHAUSTED)
VALIDATION_TARGETS=(FractalRuntimePolicyV02,FractalRuntimeBudgetV02,RuntimeTopologySourceBindingV02,RuntimeTopologySeedV02,RuntimeTopologyNodeV02,RuntimeTopologyEdgeV02,RuntimeAssignmentV02,RuntimeExecutionTopologyV02,ParentChildScopeProjectionV02,FractalCellInputV02,FractalCellQueueEntryV02,FractalReviseObservationV02,FractalPartialFailureRecordV02,FractalBackpressureStateV02,FractalCellResultV02,FractalRuntimeTraceV02,FractalRuntimeReportV02,SOURCE_CONTEXT_STRUCTURAL,SOURCE_BINDING_AGAINST_G2C,TOPOLOGY_AGAINST_SOURCES,SCOPE_PROJECTION_AGAINST_SOURCES,CELL_INPUT_AGAINST_SOURCES,RESULT_PROPOSAL,POST_VV_REPORT,GT_ADVISORY_REPORT,CELL_RESULT_PRECONDITIONS,RUNTIME_REPORT_AGAINST_SOURCES,STAGE_D_A,STAGE_D_B,STAGE_D_C,ABI_PROFILE,CAUSAL_CONSUMPTION,CAUSAL_COUNTERFACTUAL,COMPLETE_PROFILE)
VALIDATION_TARGET_COUNT=34
RUNTIME_OUTCOMES=(COMPLETED,DEGRADED,BLOCKED,NEEDS_USER,DEADEND)
REPORT_STATUSES=(PASS)
EXECUTOR_COMPONENT_IDS=(fractal_runtime_v02,fractal_scheduler_v02,post_vv_v01,gt_validator_v01,parent_return_v02)
SCOPE_RELATIONS=(EQUAL,NARROWER)
BUDGET_RELATIONS=(ROOT_BUDGET,CHILD_BUDGET)
QUEUE_PREDECESSOR_RELATIONS=(INITIAL_NONE,EXACT_IMMEDIATE_PREDECESSOR)
CAUSAL_DECISION_EFFECTS=(TOPOLOGY_SELECTION,TOPOLOGY_SCOPE,CHILD_ACTIVATION,CELL_RESULT_OUTPUT,CELL_RESULT_EVIDENCE,PARENT_CELL_AGGREGATION,RUNTIME_REPORT_AGGREGATION,RUNTIME_OUTCOME_SELECTION,UNUSED_ADVISORY,CHILD_RESULT_RETURN_BINDING,CHILD_RESULT_TERMINAL_MAPPING,CELL_TERMINAL_OUTCOME)
CAUSAL_DISPOSITIONS=(USED,REJECTED,IGNORED_WITH_REASON,BLOCKED_BY_GATE)
```

Node output mapping is exact and positional:

```text
MEMORY_CONTEXT -> MEMORY_CONTEXT_OUTPUT
LOCAL_MODEL_DECLARATION -> LOCAL_MODEL_DECLARATION_OUTPUT
CLOUD_MODEL_DECLARATION -> CLOUD_MODEL_DECLARATION_OUTPUT
SEMANTIC_ACTOR -> SEMANTIC_ACTOR_OUTPUT
SEMANTIC_MERGE -> SEMANTIC_MERGE_OUTPUT
FRACTAL_CELL -> FRACTAL_CELL_OUTPUT
FRACTAL_MERGE -> FRACTAL_MERGE_OUTPUT
POST_VV -> POST_VV_REPORT
GT_ADVISORY -> GT_ADVISORY_REPORT
PARENT_RETURN -> PARENT_RETURN_EVIDENCE
```

Required output kinds are the ordered subset demanded by the node mapping;
forbidden output kinds are the exact ten-value tuple above. Unknown literals,
aliases, or caller-invented policy, profile, cell, scope, status, outcome,
executor, relation, disposition, or reason values fail closed. `USED` is valid
only for a documented downstream identity change, `REJECTED` and
`BLOCKED_BY_GATE` block the dependent path, and `IGNORED_WITH_REASON` requires
an unchanged downstream projection and a nonempty reason.
`FractalPartialFailureRecordV02.failure_stage` and
`FractalRuntimeValidationReportV02.failure_stage` both use the exact
`FAILURE_STAGES` vocabulary; validation target uses `VALIDATION_TARGETS`.
For a validation `PASS`, `failure_stage=NONE`,
`return_to_root_required=false`, and both reason tuples are empty. The
runtime-only `SOURCE_CONTEXT_STRUCTURAL` PASS is the sole target with
`validated_object_id=None`; every built serialized, stage, or profile target
names the exact ID frozen below. For `FAIL_CLOSED`, stage is not `NONE`,
return-to-Root is true, at least one public or source reason exists, and
`validated_object_id=None`. An invalid candidate ID is never copied or
fabricated to fill a failure report. Status/stage, target/type, target/ID,
retention class, and ID-nullability substitution fail closed.

### 9.3 Identity and serialization law

The 18 serialized types use canonical UTF-8 JSON, exact ordered fields,
domain-separated SHA-256, lowercase hexadecimal digests, and these prefixes:

| Type | Identity domain | Prefix |
|---|---|---|
| `FractalRuntimePolicyV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_POLICY` | `frpolicy_v02:` |
| `FractalRuntimeBudgetV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_BUDGET` | `frbudget_v02:` |
| `RuntimeTopologySourceBindingV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_SOURCE_BINDING` | `frsource_v02:` |
| `RuntimeTopologySeedV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_TOPOLOGY_SEED` | `frseed_v02:` |
| `RuntimeTopologyNodeV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_NODE` | `frnode_v02:` |
| `RuntimeTopologyEdgeV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_EDGE` | `fredge_v02:` |
| `RuntimeAssignmentV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_ASSIGNMENT` | `frassign_v02:` |
| `RuntimeExecutionTopologyV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_TOPOLOGY` | `frtopology_v02:` |
| `ParentChildScopeProjectionV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_SCOPE_PROJECTION` | `frscope_v02:` |
| `FractalCellInputV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_CELL_INPUT` | `frcellin_v02:` |
| `FractalCellQueueEntryV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_QUEUE_ENTRY` | `frqueue_v02:` |
| `FractalReviseObservationV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_REVISE` | `frrevise_v02:` |
| `FractalPartialFailureRecordV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_PARTIAL_FAILURE` | `frfailure_v02:` |
| `FractalBackpressureStateV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_BACKPRESSURE` | `frbackpressure_v02:` |
| `FractalCellResultV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_CELL_RESULT` | `frcellresult_v02:` |
| `FractalRuntimeTraceV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_TRACE` | `frtrace_v02:` |
| `FractalRuntimeReportV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_REPORT` | `frreport_v02:` |
| `FractalRuntimeValidationReportV02` | `HEDGEHOG_FRACTAL_RUNTIME_V02_VALIDATION` | `frvalidation_v02:` |

Root cell IDs use domain `HEDGEHOG_FRACTAL_RUNTIME_V02_ROOT_CELL` and prefix
`frrootcell_v02:`. Child cell IDs use domain
`HEDGEHOG_FRACTAL_RUNTIME_V02_CHILD_CELL` and prefix `frchildcell_v02:`.
`derive_fractal_root_cell_id_v02` hashes, in exact order, source binding ID,
runtime policy ID, accepted mode, accepted scope, and literal `ROOT_CELL`.
`derive_fractal_child_cell_id_v02` hashes topology seed ID, exact parent cell
ID, canonical child index, accepted mode, selected local mode profile ID,
source mode-profile-set ID, child scope ref, runtime policy ID, ordered required
capability IDs, ordered forbidden claims, and child depth.
Neither function accepts a caller ID. For the v0.2 reference full-fractal root,
the function runs before root t02 admission for canonical child indexes 0 and
1 selected by `CHILD_SLOT_INDEX_ROWS_V02`, using the exact accepted parent
scope (`EQUAL`). The resulting IDs are plans only;
activation later reuses the same bytes and never re-derives or substitutes an
ID.

The sole seed has `seed_version=v0.2` and
`profile_id=fractal_runtime_g2d_profile_v02`. Its `trace_refs` are the source
binding `source_trace_refs` followed by source binding ID, runtime policy ID,
root cell ID, and source time-envelope ref. Its `parent_refs` are, in order,
RouteEligibility artifact ID, G2-C Root-decision artifact ID, G2-C proposal
artifact ID, and source binding ID. No lexical resorting is permitted.
Topology `parent_refs` are the seed `parent_refs` followed by topology seed ID
and root budget ID. Topology `trace_refs` are source binding ID, root cell ID,
seed ID, root budget ID, then ordered node, edge, and assignment IDs. The
Kernel topology artifact has the narrower one-parent ABI law: the exact
RouteEligibility artifact only. Object trace and parent tuples remain identity
material in their source dataclasses even when projected onto a narrower ABI
axis.

Exact integer types are required; `bool` is not accepted as `int`. The 18
canonical G2-D dataclass identities reject float, Decimal, NaN, and infinity.
The runtime-only schema-shaped ResultProposal, VVReport, and GT dictionaries
may contain only finite JSON numbers admitted by their current schemas; the
G2-D ResultProposal admits exactly the EvidenceItem confidence value `1.0` and
the fixed integer-valued cost fields. Its content-derived proposal ID hashes
those canonical JSON bytes. Wall-clock values, random values, UUIDs, process
IDs, iteration accidents, caller IDs, caller PASS, raw text, raw provider
output, secrets, callbacks, clients, connector handles, effect handles,
permissions, packets, receipts, FinalOutput, and DRS writes are excluded from
canonical identity material.

Every serialized identity excludes only its own identity field and includes
every other declared field in order. The two runtime-only contexts have no
identity: they carry already-built objects and are accepted only by complete
contextual object equality, exact ordered-tuple equality, canonical-byte
equality for plain dictionaries, and identity rebuilds. An ABI projection may
classify a source field as `CONTEXT_ONLY` only under the exact field-partition
law in Section 16; this does not remove that field from its source identity.

Static node and assignment identities contain binding classes, never runtime
cell, parent-cell, scope, budget, queue, or topology identities. Node
`input_refs` may name only source binding, policy, and earlier external
evidence/context refs. Dependencies are later-built edges. Runtime queue
snapshots instantiate those templates for concrete cells and budgets, so no
static identity points forward into a runtime instance.

The result graph is bottom-up and acyclic. A leaf result has
`ordered_child_result_ids=()` and `partial_failure_ids=()`. Actual child results
are built first in canonical child-slot order. A partial-failure record may then
name one already-built direct child result. A no-child activation-gate slot has
no child result or failure record; its terminal queue entry remains an exact
parent-result input. The parent result is built last and carries only actual
direct-child result IDs and corresponding actual failure IDs in slot order,
while its terminal queue tuple represents every required slot. A failure record
may not name its containing result, an ancestor, a future or foreign result, an
uninstantiated planned child, or a result outside the parent's exact child set.
Synthetic, duplicate, missing, or reordered child/failure identities fail
closed.

Validation reports also form an acyclic graph. The pre-result report targets
`CELL_RESULT_PRECONDITIONS` and validates the already-built cell input,
complete terminal queue tuple, exact pre-Post-V&V proposal prefix, actual child
result tuple, actual failure tuple, Post V&V report, GT advisory, completion
budget, scope, and candidate outcome. Its `validated_object_id` is
the content-derived local ResultProposal proposal ID. A later structural
`FractalCellResultV02` report may validate the built result but exists only in
`FractalRuntimeExecutionBundleV02`; it is never embedded in result identity.
No validation report may name an object whose identity depends on that report.

The exact validation-target build register is complete. Structural validation
uses the exact serialized class name, its rebuilt identity, and its owned
failure stage:

| Structural target | PASS `validated_object_id` | Owned failure stage |
|---|---|---|
| `FractalRuntimePolicyV02` | `policy_id` | `POLICY` |
| `FractalRuntimeBudgetV02` | `budget_id` | `BUDGET` |
| `RuntimeTopologySourceBindingV02` | `source_binding_id` | `SOURCE_BINDING` |
| `RuntimeTopologySeedV02` | `topology_seed_id` | `TOPOLOGY_SEED` |
| `RuntimeTopologyNodeV02` | `node_id` | `NODE` |
| `RuntimeTopologyEdgeV02` | `edge_id` | `EDGE` |
| `RuntimeAssignmentV02` | `assignment_id` | `ASSIGNMENT` |
| `RuntimeExecutionTopologyV02` | `topology_id` | `TOPOLOGY` |
| `ParentChildScopeProjectionV02` | `projection_id` | `SCOPE` |
| `FractalCellInputV02` | `cell_input_id` | `CELL_INPUT` |
| `FractalCellQueueEntryV02` | `queue_entry_id` | `QUEUE` |
| `FractalReviseObservationV02` | `observation_id` | `REVISE` |
| `FractalPartialFailureRecordV02` | `partial_failure_id` | `PARTIAL_FAILURE` |
| `FractalBackpressureStateV02` | `backpressure_id` | `BACKPRESSURE` |
| `FractalCellResultV02` | `result_id` | `CELL_RESULT` |
| `FractalRuntimeTraceV02` | `trace_id` | `RUNTIME_TRACE` |
| `FractalRuntimeReportV02` | `report_id` | `REPORT` |

`FractalRuntimeValidationReportV02` is deliberately absent from the target
registry. Its self-validator returns reasons and never creates a report about
a report. Contextual targets use this exact PASS identity and owned stage:

| Contextual target | PASS `validated_object_id` | Owned failure stage |
|---|---|---|
| `SOURCE_CONTEXT_STRUCTURAL` | `None` | `SOURCE_CONTEXT` |
| `SOURCE_BINDING_AGAINST_G2C` | `source_binding_id` | `SOURCE_BINDING` |
| `TOPOLOGY_AGAINST_SOURCES` | `topology_id` | `TOPOLOGY` |
| `SCOPE_PROJECTION_AGAINST_SOURCES` | `projection_id` | `SCOPE` |
| `CELL_INPUT_AGAINST_SOURCES` | `cell_input_id` | `CELL_INPUT` |
| `RESULT_PROPOSAL` | `proposal_id` | `RESULT_PROPOSAL` |
| `POST_VV_REPORT` | `vv_report_id` | `POST_VV` |
| `GT_ADVISORY_REPORT` | `gt_report_id` | `GT` |
| `CELL_RESULT_PRECONDITIONS` | `proposal_id` | `CELL_RESULT_PRECONDITIONS` |
| `RUNTIME_REPORT_AGAINST_SOURCES` | `report_id` | `REPORT` |
| `STAGE_D_A` | exact `frstage_v02:` projection ID | `ABI` |
| `STAGE_D_B` | exact `frstage_v02:` projection ID | `ABI` |
| `STAGE_D_C` | exact `frstage_v02:` projection ID | `ABI` |
| `ABI_PROFILE` | exact Stage-D-C projection ID | `ABI` |
| `CAUSAL_CONSUMPTION` | `frcausalprofile_v02:<64 lowercase hex>` | `CAUSAL_CONSUMPTION` |
| `CAUSAL_COUNTERFACTUAL` | `frcounterfactual_v02:<64 lowercase hex>` | `CAUSAL_COUNTERFACTUAL` |
| `COMPLETE_PROFILE` | exact report artifact ID | `COMPLETE_PROFILE` |

Stage projection IDs use domain
`HEDGEHOG_FRACTAL_RUNTIME_V02_STAGE_PROJECTION`, prefix `frstage_v02:`, and
hash the stage literal followed by the exact ordered artifact IDs.

`CausalConsumptionRefV01` has exactly the current Kernel ABI fields
`producer_actor_id`, `source_artifact_id`, `output_field`,
`consumer_component`, `downstream_artifact_id`, `decision_effect`,
`disposition`, `reason_code`, and `trace_refs`. It has no public identity field.
The causal profile uses domain
`HEDGEHOG_FRACTAL_RUNTIME_V02_CAUSAL_PROFILE`, prefix
`frcausalprofile_v02:`, and hashes this exact ordered plain object under the
existing canonical JSON law:

```text
{
  "stage_d_c_artifact_ids": [
    every exact Stage-D-C artifact_id in Stage-D-C order
  ],
  "causal_refs":
    causal_consumption_refs_to_plain_list_v01(exact_causal_refs)
}
```

The function call contributes its exact returned list. Its order is semantic
and is never sorted. No synthetic reference ID is inserted.

The counterfactual projection uses domain
`HEDGEHOG_FRACTAL_RUNTIME_V02_CAUSAL_COUNTERFACTUAL`, prefix
`frcounterfactual_v02:`, and hashes this exact ordered plain object:

```text
{
  "causal_ref":
    causal_consumption_ref_to_plain_dict_v01(exact_causal_ref),
  "mutated_source_artifact_id":
    exact validated mutated source artifact ID,
  "expected_disposition":
    exact profile-derived disposition,
  "expected_downstream_artifact_id":
    exact profile-derived accepted downstream artifact ID or JSON null
}
```

The function call contributes its exact returned dictionary. These three
projections are internal validator material and add no type or public function.
The `CAUSAL_CONSUMPTION` PASS
target names the content-derived `frcausalprofile_v02:` identity and the
`CAUSAL_COUNTERFACTUAL` PASS target names the content-derived
`frcounterfactual_v02:` identity.

Every PASS uses stage `NONE`, empty public and source reason tuples, and
`return_to_root_required=false`. `SOURCE_CONTEXT_STRUCTURAL` is the sole PASS
target with a null object ID. Every FAIL_CLOSED report uses a non-`NONE` stage,
a null object ID, at least one public or source reason, and
`return_to_root_required=true`. Target/type, target/ID, target/stage,
status/stage, retention-class, pre-result/result-report, and post-result-report
substitution fail closed. No validation report contains an ID that depends on
that report.

### 9.4 Exact public API

Each serialized type has one `build_*`, one `validate_*`, one
`*_to_plain_data_v02`, and one `rebuild_*_identity_v02` function. Their exact
stems, in type order, are:

```text
fractal_runtime_policy
fractal_runtime_budget
runtime_topology_source_binding
runtime_topology_seed
runtime_topology_node
runtime_topology_edge
runtime_assignment
runtime_execution_topology
parent_child_scope_projection
fractal_cell_input
fractal_cell_queue_entry
fractal_revise_observation
fractal_partial_failure_record
fractal_backpressure_state
fractal_cell_result
fractal_runtime_trace
fractal_runtime_report
fractal_runtime_validation_report
```

That produces 72 exact structural functions. The four runtime-context functions
are:

```text
build_fractal_runtime_source_context_v02
validate_fractal_runtime_source_context_v02
build_fractal_runtime_execution_bundle_v02
validate_fractal_runtime_execution_bundle_v02
```

The 34 exact composition functions are:

```text
validate_runtime_topology_source_binding_against_g2c_v02
derive_fractal_root_cell_id_v02
derive_fractal_child_cell_id_v02
construct_runtime_execution_topology_v02
validate_runtime_execution_topology_against_sources_v02
admit_runtime_execution_topology_v02
advance_fractal_cell_queue_v02
project_parent_child_scope_v02
validate_parent_child_scope_against_sources_v02
build_fractal_cell_input_from_queue_v02
validate_fractal_cell_input_against_sources_v02
build_fractal_cell_result_proposal_v02
validate_fractal_cell_result_proposal_v02
validate_fractal_post_vv_report_v02
validate_fractal_gt_advisory_v02
evaluate_fractal_revise_observation_v02
record_fractal_partial_failure_v02
evaluate_fractal_backpressure_v02
validate_fractal_cell_result_against_input_v02
aggregate_fractal_runtime_report_v02
run_fractal_runtime_v02
validate_fractal_runtime_report_against_sources_v02
project_runtime_execution_topology_kernel_artifact_v02
project_fractal_cell_queue_entry_kernel_artifact_v02
project_fractal_cell_result_kernel_artifact_v02
project_fractal_runtime_report_kernel_artifact_v02
validate_fractal_runtime_stage_bundle_v02
validate_fractal_runtime_abi_profile_v02
evaluate_route_eligibility_to_topology_transition_v02
evaluate_fractal_runtime_state_transition_v02
evaluate_fractal_parent_return_transition_v02
build_fractal_runtime_causal_consumption_refs_v02
validate_fractal_runtime_causal_consumption_refs_v02
validate_fractal_runtime_causal_counterfactual_v02
```

The four ResultProposal/Post V&V/GT helpers remain the final authorized helper
addition from v0.1.2. Version v0.1.9 adds or removes no public function. It
changes only signatures 41, 83, and 90 by adding `queue_reason_codes`, and
renames only the signatures 93/94 terminal parameter to
`pre_post_vv_terminal_queue_entries`. No other public signature changes, and
all staged availability remains exact.

The six exact Transition-owned functions are:

```text
build_fractal_runtime_transition_registry_profile_v02
validate_fractal_runtime_transition_registry_profile_v02
fractal_runtime_transition_registry_profile_to_plain_dict_v02
validate_fractal_runtime_transition_decision_v02
fractal_runtime_transition_decision_to_plain_dict_v02
rebuild_fractal_runtime_transition_decision_identity_v02
```

```text
FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT=110
FRACTAL_RUNTIME_TRANSITION_PUBLIC_FUNCTION_COUNT=6
TOTAL_G2D_PUBLIC_FUNCTION_COUNT=116
DIRECT_PACKAGE_G2D_ATTRIBUTE_COUNT=136
```

#### 9.4.1 Builder field-derivation register

Every declared field is classified exactly once below. `IP` means
`INPUT_PARAMETER`, `DI` `DERIVED_IDENTITY`, `FL` `FIXED_LITERAL`, `SD`
`SOURCE_DERIVED`, `CD` `CONTEXT_DERIVED`, `KD` `COUNTER_DERIVED`, and `ZN`
`ZERO_NONCLAIM`; `TE` is `DERIVED_FROM_TYPED_EVENT`. A builder accepts only the
semantic inputs shown in its exact signature; DI, FL, KD, and ZN values are
never accepted as caller authority.

| Type | Exact field classification |
|---|---|
| `FractalRuntimePolicyV02` | DI: `policy_id`; FL: `policy_profile_id,policy_version,allowed_modes,allowed_node_kinds,allowed_edge_kinds,allowed_assignment_kinds,recursive_mode,recursive_capability_id,forbidden_claims,reference_child_count,queue_profile_id,budget_profile_id,max_depth,max_fan_out,max_total_cells,max_parallelism,max_revise_count,max_consecutive_no_progress,max_wall_time_units,max_token_budget,max_provider_calls,root_review_required`; SD: `allowed_capability_ids,permitted_child_scope_refs`; ZN: `authority_created,permission_created,real_world_effects_count` |
| `FractalRuntimeBudgetV02` | DI: `budget_id`; CD: `policy_id,topology_seed_id,allocation_parent_budget_id,predecessor_budget_id,owning_cell_id,budget_scope,budget_state,budget_event_kind`; TE: `budget_event_ref` (`DERIVED_FROM_TYPED_EVENT`); SD: `max_depth,max_fan_out,max_total_cells,max_parallelism,max_revise_count,max_wall_time_units,max_token_budget,max_provider_calls`; KD: `consumed_wall_time_units,consumed_token_budget,consumed_provider_calls,consumed_cell_count,consumed_revise_count,current_parallelism,remaining_wall_time_units,remaining_token_budget,remaining_provider_calls,remaining_cell_count,remaining_revise_count,remaining_parallel_slots`; FL: `root_review_required`; ZN: `authority_created,permission_created,action_commit_packet_created,receipt_created,final_output_created,drs_write_created,real_world_effects_count` |
| `RuntimeTopologySourceBindingV02` | DI: `source_binding_id`; SD: `request_id,transaction_id,owning_root_id,domain_id,accepted_mode,accepted_scope_ref,route_eligibility_artifact_id,route_eligibility_artifact_sha256,source_decision_artifact_id,source_proposal_artifact_id,selected_local_mode_profile_id,selected_feasibility_row_id,selected_safe_depth_rank,selected_expected_cost_units,required_downstream_capability_ids,source_mode_profile_set_id,source_policy_snapshot_id,source_capability_snapshot_id,permitted_narrower_scope_refs,source_root_decision_result_id,source_root_transition_decision_id,proposal_transition_decision_id,post_root_transition_decision_id,transition_registry_id,g2c_abi_profile_id,downstream_action_packet_required,source_time_envelope_ref,source_trace_refs,source_parent_refs`; CD: `runtime_policy_id`; FL: `root_review_required`; ZN: `authority_created,permission_created,real_world_effects_count` |
| `RuntimeTopologySeedV02` | DI: `topology_seed_id`; FL: `seed_version,profile_id,root_review_required`; CD: `request_id,transaction_id,owning_root_id,domain_id,accepted_mode,accepted_scope_ref,source_binding_id,runtime_policy_id,root_cell_id,source_time_envelope_ref,trace_refs,parent_refs`; ZN: `authority_created,permission_created,real_world_effects_count` |
| `RuntimeTopologyNodeV02` | DI: `node_id`; CD: `topology_seed_id,accepted_mode,scope_ref,allowed_capability_ids,forbidden_claims,input_refs,trace_refs,expected_output_kind`; IP: `node_kind,canonical_index,depth,cell_binding_class,scope_binding_class,budget_binding_class,required_capability_ids,input_ref_derivation_class`; FL: `required,recursive_expansion_allowed,root_review_required`; ZN: `authority_created,permission_created,real_world_effects_count` |
| `RuntimeTopologyEdgeV02` | DI: `edge_id`; CD: `topology_seed_id,source_node_id,target_node_id,trace_refs`; IP: `edge_kind,canonical_index,cell_projection_class`; FL: `required,evidence_flow_allowed,authority_flow_allowed,root_review_required` |
| `RuntimeAssignmentV02` | DI: `assignment_id`; CD: `topology_seed_id,node_id,canonical_index,trace_refs`; IP: `assignment_kind,executor_component_id,capability_ids,cell_binding_class,scope_binding_class,budget_binding_class`; FL: `provider_call_allowed,network_call_allowed,connector_call_allowed,root_review_required`; ZN: `authority_created,permission_created,effect_created,real_world_effects_count` |
| `RuntimeExecutionTopologyV02` | DI: `topology_id`; FL: `topology_version,root_review_required`; CD: `topology_seed_id,request_id,transaction_id,owning_root_id,domain_id,accepted_mode,accepted_scope_ref,source_binding_id,source_route_eligibility_artifact_id,source_root_decision_artifact_id,source_proposal_artifact_id,runtime_policy_id,ordered_node_ids,ordered_edge_ids,ordered_assignment_ids,root_cell_id,global_budget_id,time_envelope_ref,trace_refs,parent_refs`; ZN: `authority_created,permission_created,action_commit_packet_created,receipt_created,final_output_created,drs_write_created,provider_calls,network_calls,real_world_effects_count` |
| `ParentChildScopeProjectionV02` | DI: `projection_id`; CD: `topology_id,parent_cell_id,child_cell_id,parent_scope_ref,child_scope_ref,parent_allowed_capability_ids,child_allowed_capability_ids,parent_forbidden_claims,child_forbidden_claims,parent_ttl_units,child_ttl_units,parent_budget_id,child_budget_id,global_budget_id,child_depth,parent_lineage_refs,child_lineage_refs,proof_refs`; KD: `scope_relation,budget_relation`; FL: `root_review_required`; ZN: `authority_created,permission_created,final_output_created,real_world_effects_count` |
| `FractalCellInputV02` | DI: `cell_input_id`; CD: `topology_id,cell_id,parent_cell_id,request_id,transaction_id,owning_root_id,domain_id,accepted_mode,scope_projection_id,scope_ref,cell_budget_id,global_budget_id,ordered_initial_queue_entry_ids,ordered_required_queue_entry_ids,cell_depth,requested_child_count,ordered_planned_child_cell_ids,ordered_node_ids,evidence_refs,context_refs,required_output_kinds,forbidden_output_kinds,time_envelope_ref,trace_refs`; FL: `initial_revise_count,root_review_required`; ZN: `authority_created,permission_created,action_commit_packet_created,final_output_created,real_world_effects_count` |
| `FractalCellQueueEntryV02` | DI: `queue_entry_id`; CD: `topology_id,topology_seed_id,cell_id,parent_cell_id,node_id,planned_child_cell_id,cell_depth,scope_ref,cell_budget_id,global_budget_id,predecessor_queue_entry_id,transition_decision_id,observed_output_refs,observed_evidence_refs,advisory_refs,lineage_refs`; IP: `queue_reason_codes`; KD: `state,prior_state,predecessor_relation,canonical_priority,node_instance_sequence,snapshot_sequence,admission_round`; FL: `root_review_required`; ZN: `authority_created,permission_created,final_output_created,drs_write_created,real_world_effects_count` |
| `FractalReviseObservationV02` | DI: `observation_id`; CD: `topology_id,cell_id,queue_entry_id,cell_budget_before_id,global_budget_before_id,trace_refs`; IP: `revision_index,newly_validated_evidence_count,newly_resolved_constraints_count,newly_accepted_outputs_count,newly_introduced_conflicts_count,consecutive_non_positive_count,max_consecutive_non_positive_count`; KD: `progress_units,revise_eligible,derived_terminal_state,reason_codes`; FL: `root_review_required`; ZN: `authority_created,real_world_effects_count` |
| `FractalPartialFailureRecordV02` | DI: `partial_failure_id`; CD: `topology_id,parent_cell_id,child_cell_id,child_result_id,evidence_refs,trace_refs,allocated_cell_budget_id,final_cell_budget_id,global_budget_id`; IP: `failure_stage,reason_codes,source_reason_codes,required_child,sibling_independent`; KD: `revise_eligible,parent_disposition`; FL: `retry_eligible,root_review_required`; ZN: `authority_created,permission_created,final_output_created,real_world_effects_count` |
| `FractalBackpressureStateV02` | DI: `backpressure_id`; CD: `topology_id,policy_id,deferred_queue_entry_ids,admission_order,lineage_refs,global_budget_id`; IP: `evaluated_round`; KD: `queue_capacity,running_count,ready_count,pending_count,backpressure_reason,reason_codes`; FL: `no_work_dropped,root_review_required`; ZN: `authority_created,permission_created,real_world_effects_count` |
| `FractalCellResultV02` | DI: `result_id`; CD: `topology_id,topology_seed_id,cell_id,parent_cell_id,cell_depth,cell_input_id,ordered_terminal_queue_entry_ids,ordered_child_result_ids,accepted_output_refs,evidence_refs,pre_result_validation_report_id,post_vv_report_ref,gt_advisory_ref,partial_failure_ids,allocated_cell_budget_id,final_cell_budget_id,global_budget_id,scope_ref,trace_refs`; KD: `outcome,reason_codes,source_reason_codes`; FL: `parent_return_required,root_review_required`; ZN: `authority_created,permission_created,action_commit_packet_created,receipt_created,final_output_created,drs_write_created,real_world_effects_count` |
| `FractalRuntimeTraceV02` | DI: `trace_id`; CD: `topology_id,topology_seed_id,source_binding_id,ordered_queue_entry_ids,state_transition_decision_ids,cell_input_ids,cell_result_ids,scope_projection_ids,revise_observation_ids,partial_failure_ids,backpressure_state_ids,budget_ids,abi_artifact_refs,transition_refs,parent_return_refs`; FL: `root_review_required`; ZN: `provider_calls,model_calls,network_calls,connector_calls,external_drs_calls,real_world_effects_count` |
| `FractalRuntimeReportV02` | DI: `report_id`; FL: `report_version,profile_id,report_status,root_review_required`; CD: `topology_id,topology_seed_id,topology_artifact_id,source_binding_id,request_id,transaction_id,owning_root_id,domain_id,accepted_mode,accepted_scope_ref,ordered_cell_result_ids,queue_entry_ids,backpressure_state_ids,runtime_trace_id,final_budget_id,parent_return_transition_decision_id,parent_return_refs`; KD: `runtime_outcome,completed_cell_count,degraded_cell_count,blocked_cell_count,needs_user_cell_count,deadend_cell_count,reason_codes,topology_created_count`; ZN: `provider_calls,model_calls,network_calls,connector_calls,external_drs_calls,action_commit_packets_created,permissions_created,receipts_created,final_outputs_created,drs_writes,authority_created_count,real_world_effects_count` |
| `FractalRuntimeValidationReportV02` | DI: `validation_report_id`; IP: `validation_target,validated_object_id,failure_stage,reason_codes,source_reason_codes`; KD: `status,return_to_root_required`; FL: `root_review_required`; ZN: `authority_created,permission_created,action_commit_packet_created,final_output_created,drs_write_created,real_world_effects_count` |

#### 9.4.2 Exact final signature and slice-availability table

The table below is the complete ordered public register. `-` means no default;
`*` fixes every following parameter as keyword-only. There is no `*args`,
`**kwargs`, callback, client, provider/connector handle, caller PASS, caller
authority boolean, caller identity, or caller Transition guard.

| # | First slice | Exact signature |
|---:|---|---|
| 1 | D1 | `build_fractal_runtime_policy_v02(*, required_downstream_capability_ids: tuple[str, ...], permitted_child_scope_refs: tuple[str, ...]) -> FractalRuntimePolicyV02` |
| 2 | D1 | `validate_fractal_runtime_policy_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 3 | D1 | `fractal_runtime_policy_to_plain_data_v02(value: FractalRuntimePolicyV02) -> dict[str, object]` |
| 4 | D1 | `rebuild_fractal_runtime_policy_identity_v02(value: FractalRuntimePolicyV02) -> str` |
| 5 | D1 | `build_fractal_runtime_budget_v02(*, policy: FractalRuntimePolicyV02, topology_seed: RuntimeTopologySeedV02, allocation_parent_budget: FractalRuntimeBudgetV02 | None, predecessor_budget: FractalRuntimeBudgetV02 | None, owning_cell_id: str, budget_scope: str, budget_state: str, budget_event_kind: str, budget_context_input: FractalCellInputV02 | None, canonical_child_index: int | None, allocation_queue_entries: tuple[FractalCellQueueEntryV02, ...], transition_decision: TransitionDecisionV01 | None, paired_cell_budget: FractalRuntimeBudgetV02 | None, child_result: FractalCellResultV02 | None) -> FractalRuntimeBudgetV02` |
| 6 | D1 | `validate_fractal_runtime_budget_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 7 | D1 | `fractal_runtime_budget_to_plain_data_v02(value: FractalRuntimeBudgetV02) -> dict[str, object]` |
| 8 | D1 | `rebuild_fractal_runtime_budget_identity_v02(value: FractalRuntimeBudgetV02) -> str` |
| 9 | D1 | `build_runtime_topology_source_binding_v02(*, source_context: FractalRuntimeSourceContextV02) -> RuntimeTopologySourceBindingV02` |
| 10 | D1 | `validate_runtime_topology_source_binding_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 11 | D1 | `runtime_topology_source_binding_to_plain_data_v02(value: RuntimeTopologySourceBindingV02) -> dict[str, object]` |
| 12 | D1 | `rebuild_runtime_topology_source_binding_identity_v02(value: RuntimeTopologySourceBindingV02) -> str` |
| 13 | D1 | `build_runtime_topology_seed_v02(source_binding: RuntimeTopologySourceBindingV02, policy: FractalRuntimePolicyV02, *, root_cell_id: str) -> RuntimeTopologySeedV02` |
| 14 | D1 | `validate_runtime_topology_seed_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 15 | D1 | `runtime_topology_seed_to_plain_data_v02(value: RuntimeTopologySeedV02) -> dict[str, object]` |
| 16 | D1 | `rebuild_runtime_topology_seed_identity_v02(value: RuntimeTopologySeedV02) -> str` |
| 17 | D1 | `build_runtime_topology_node_v02(seed: RuntimeTopologySeedV02, source_binding: RuntimeTopologySourceBindingV02, policy: FractalRuntimePolicyV02, *, canonical_index: int, node_kind: str, depth: int, scope_ref: str, cell_binding_class: str, scope_binding_class: str, budget_binding_class: str, required_capability_ids: tuple[str, ...], input_ref_derivation_class: str) -> RuntimeTopologyNodeV02` |
| 18 | D1 | `validate_runtime_topology_node_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 19 | D1 | `runtime_topology_node_to_plain_data_v02(value: RuntimeTopologyNodeV02) -> dict[str, object]` |
| 20 | D1 | `rebuild_runtime_topology_node_identity_v02(value: RuntimeTopologyNodeV02) -> str` |
| 21 | D1 | `build_runtime_topology_edge_v02(seed: RuntimeTopologySeedV02, source_node: RuntimeTopologyNodeV02, target_node: RuntimeTopologyNodeV02, *, edge_kind: str, canonical_index: int, cell_projection_class: str) -> RuntimeTopologyEdgeV02` |
| 22 | D1 | `validate_runtime_topology_edge_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 23 | D1 | `runtime_topology_edge_to_plain_data_v02(value: RuntimeTopologyEdgeV02) -> dict[str, object]` |
| 24 | D1 | `rebuild_runtime_topology_edge_identity_v02(value: RuntimeTopologyEdgeV02) -> str` |
| 25 | D1 | `build_runtime_assignment_v02(seed: RuntimeTopologySeedV02, node: RuntimeTopologyNodeV02, *, assignment_kind: str, executor_component_id: str, capability_ids: tuple[str, ...], cell_binding_class: str, scope_binding_class: str, budget_binding_class: str) -> RuntimeAssignmentV02` |
| 26 | D1 | `validate_runtime_assignment_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 27 | D1 | `runtime_assignment_to_plain_data_v02(value: RuntimeAssignmentV02) -> dict[str, object]` |
| 28 | D1 | `rebuild_runtime_assignment_identity_v02(value: RuntimeAssignmentV02) -> str` |
| 29 | D1 | `build_runtime_execution_topology_v02(source_binding: RuntimeTopologySourceBindingV02, seed: RuntimeTopologySeedV02, policy: FractalRuntimePolicyV02, *, nodes: tuple[RuntimeTopologyNodeV02, ...], edges: tuple[RuntimeTopologyEdgeV02, ...], assignments: tuple[RuntimeAssignmentV02, ...], root_cell_id: str, global_budget: FractalRuntimeBudgetV02, time_envelope_ref: str) -> RuntimeExecutionTopologyV02` |
| 30 | D1 | `validate_runtime_execution_topology_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 31 | D1 | `runtime_execution_topology_to_plain_data_v02(value: RuntimeExecutionTopologyV02) -> dict[str, object]` |
| 32 | D1 | `rebuild_runtime_execution_topology_identity_v02(value: RuntimeExecutionTopologyV02) -> str` |
| 33 | D1 | `build_parent_child_scope_projection_v02(topology: RuntimeExecutionTopologyV02, source_binding: RuntimeTopologySourceBindingV02, *, parent_cell_id: str, child_cell_id: str, parent_scope_ref: str, child_scope_ref: str, parent_allowed_capability_ids: tuple[str, ...], child_allowed_capability_ids: tuple[str, ...], parent_forbidden_claims: tuple[str, ...], child_forbidden_claims: tuple[str, ...], parent_ttl_units: int, child_ttl_units: int, parent_budget: FractalRuntimeBudgetV02, child_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, child_depth: int) -> ParentChildScopeProjectionV02` |
| 34 | D1 | `validate_parent_child_scope_projection_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 35 | D1 | `parent_child_scope_projection_to_plain_data_v02(value: ParentChildScopeProjectionV02) -> dict[str, object]` |
| 36 | D1 | `rebuild_parent_child_scope_projection_identity_v02(value: ParentChildScopeProjectionV02) -> str` |
| 37 | D1 | `build_fractal_cell_input_v02(topology: RuntimeExecutionTopologyV02, *, cell_id: str, parent_cell_id: str | None, scope_projection: ParentChildScopeProjectionV02 | None, scope_ref: str, cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, initial_queue_entries: tuple[FractalCellQueueEntryV02, ...], required_queue_entries: tuple[FractalCellQueueEntryV02, ...], cell_depth: int, requested_child_count: int, ordered_planned_child_cell_ids: tuple[str, ...], ordered_nodes: tuple[RuntimeTopologyNodeV02, ...], evidence_refs: tuple[str, ...], context_refs: tuple[str, ...], time_envelope_ref: str) -> FractalCellInputV02` |
| 38 | D1 | `validate_fractal_cell_input_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 39 | D1 | `fractal_cell_input_to_plain_data_v02(value: FractalCellInputV02) -> dict[str, object]` |
| 40 | D1 | `rebuild_fractal_cell_input_identity_v02(value: FractalCellInputV02) -> str` |
| 41 | D1 | `build_fractal_cell_queue_entry_v02(topology: RuntimeExecutionTopologyV02, seed: RuntimeTopologySeedV02, cell_input: FractalCellInputV02 | None, node: RuntimeTopologyNodeV02, cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, *, cell_id: str, parent_cell_id: str | None, planned_child_cell_id: str | None, cell_depth: int, scope_ref: str, predecessor: FractalCellQueueEntryV02 | None, transition_decision: TransitionDecisionV01, activation_parent_artifact: KernelArtifactV01 | None, local_child_result: FractalCellResultV02 | None, local_child_result_artifact: KernelArtifactV01 | None, cell_instantiation_order: tuple[str, ...], projected_node_ids: tuple[str, ...], round_start_queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_reason_codes: tuple[str, ...], observed_output_refs: tuple[str, ...], observed_evidence_refs: tuple[str, ...], advisory_refs: tuple[str, ...]) -> FractalCellQueueEntryV02` |
| 42 | D1 | `validate_fractal_cell_queue_entry_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 43 | D1 | `fractal_cell_queue_entry_to_plain_data_v02(value: FractalCellQueueEntryV02) -> dict[str, object]` |
| 44 | D1 | `rebuild_fractal_cell_queue_entry_identity_v02(value: FractalCellQueueEntryV02) -> str` |
| 45 | D1 | `build_fractal_revise_observation_v02(topology: RuntimeExecutionTopologyV02, cell_input: FractalCellInputV02, queue_entry: FractalCellQueueEntryV02, validation_report: FractalRuntimeValidationReportV02, *, revision_index: int, newly_validated_evidence_count: int, newly_resolved_constraints_count: int, newly_accepted_outputs_count: int, newly_introduced_conflicts_count: int, consecutive_non_positive_count: int, max_consecutive_non_positive_count: int, cell_budget_before: FractalRuntimeBudgetV02, global_budget_before: FractalRuntimeBudgetV02) -> FractalReviseObservationV02` |
| 46 | D1 | `validate_fractal_revise_observation_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 47 | D1 | `fractal_revise_observation_to_plain_data_v02(value: FractalReviseObservationV02) -> dict[str, object]` |
| 48 | D1 | `rebuild_fractal_revise_observation_identity_v02(value: FractalReviseObservationV02) -> str` |
| 49 | D1 | `build_fractal_partial_failure_record_v02(topology: RuntimeExecutionTopologyV02, parent_input: FractalCellInputV02, child_result: FractalCellResultV02, *, failure_stage: str, reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...], evidence_refs: tuple[str, ...], allocated_cell_budget: FractalRuntimeBudgetV02, final_cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, required_child: bool, sibling_independent: bool) -> FractalPartialFailureRecordV02` |
| 50 | D1 | `validate_fractal_partial_failure_record_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 51 | D1 | `fractal_partial_failure_record_to_plain_data_v02(value: FractalPartialFailureRecordV02) -> dict[str, object]` |
| 52 | D1 | `rebuild_fractal_partial_failure_record_identity_v02(value: FractalPartialFailureRecordV02) -> str` |
| 53 | D1 | `build_fractal_backpressure_state_v02(topology: RuntimeExecutionTopologyV02, policy: FractalRuntimePolicyV02, global_budget: FractalRuntimeBudgetV02, *, queue_entries: tuple[FractalCellQueueEntryV02, ...], evaluated_round: int) -> FractalBackpressureStateV02` |
| 54 | D1 | `validate_fractal_backpressure_state_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 55 | D1 | `fractal_backpressure_state_to_plain_data_v02(value: FractalBackpressureStateV02) -> dict[str, object]` |
| 56 | D1 | `rebuild_fractal_backpressure_state_identity_v02(value: FractalBackpressureStateV02) -> str` |
| 57 | D1 | `build_fractal_cell_result_v02(topology: RuntimeExecutionTopologyV02, cell_input: FractalCellInputV02, terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...], child_results: tuple[FractalCellResultV02, ...], *, accepted_output_refs: tuple[str, ...], evidence_refs: tuple[str, ...], pre_result_validation_report: FractalRuntimeValidationReportV02, post_vv_report: dict[str, object], gt_advisory_report: dict[str, object], partial_failures: tuple[FractalPartialFailureRecordV02, ...], allocated_cell_budget: FractalRuntimeBudgetV02, final_cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02) -> FractalCellResultV02` |
| 58 | D1 | `validate_fractal_cell_result_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 59 | D1 | `fractal_cell_result_to_plain_data_v02(value: FractalCellResultV02) -> dict[str, object]` |
| 60 | D1 | `rebuild_fractal_cell_result_identity_v02(value: FractalCellResultV02) -> str` |
| 61 | D1 | `build_fractal_runtime_trace_v02(topology: RuntimeExecutionTopologyV02, source_binding: RuntimeTopologySourceBindingV02, *, topology_artifact: KernelArtifactV01, queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...], state_transition_decisions: tuple[TransitionDecisionV01, ...], cell_inputs: tuple[FractalCellInputV02, ...], cell_results: tuple[FractalCellResultV02, ...], result_artifacts: tuple[KernelArtifactV01, ...], runtime_abi_artifacts: tuple[KernelArtifactV01, ...], scope_projections: tuple[ParentChildScopeProjectionV02, ...], revise_observations: tuple[FractalReviseObservationV02, ...], partial_failures: tuple[FractalPartialFailureRecordV02, ...], backpressure_states: tuple[FractalBackpressureStateV02, ...], budgets: tuple[FractalRuntimeBudgetV02, ...], topology_transition_decision: TransitionDecisionV01, parent_return_transition_decision: TransitionDecisionV01, root_result_artifact: KernelArtifactV01) -> FractalRuntimeTraceV02` |
| 62 | D1 | `validate_fractal_runtime_trace_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 63 | D1 | `fractal_runtime_trace_to_plain_data_v02(value: FractalRuntimeTraceV02) -> dict[str, object]` |
| 64 | D1 | `rebuild_fractal_runtime_trace_identity_v02(value: FractalRuntimeTraceV02) -> str` |
| 65 | D1 | `build_fractal_runtime_report_v02(topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, source_binding: RuntimeTopologySourceBindingV02, *, ordered_cell_results: tuple[FractalCellResultV02, ...], queue_entries: tuple[FractalCellQueueEntryV02, ...], backpressure_states: tuple[FractalBackpressureStateV02, ...], runtime_trace: FractalRuntimeTraceV02, final_budget: FractalRuntimeBudgetV02, parent_return_transition_decision: TransitionDecisionV01, root_result_artifact: KernelArtifactV01) -> FractalRuntimeReportV02` |
| 66 | D1 | `validate_fractal_runtime_report_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 67 | D1 | `fractal_runtime_report_to_plain_data_v02(value: FractalRuntimeReportV02) -> dict[str, object]` |
| 68 | D1 | `rebuild_fractal_runtime_report_identity_v02(value: FractalRuntimeReportV02) -> str` |
| 69 | D1 | `build_fractal_runtime_validation_report_v02(*, validation_target: str, validated_object_id: str | None, failure_stage: str, reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...]) -> FractalRuntimeValidationReportV02` |
| 70 | D1 | `validate_fractal_runtime_validation_report_v02(value: object) -> tuple[str, ...]` |
| 71 | D1 | `fractal_runtime_validation_report_to_plain_data_v02(value: FractalRuntimeValidationReportV02) -> dict[str, object]` |
| 72 | D1 | `rebuild_fractal_runtime_validation_report_identity_v02(value: FractalRuntimeValidationReportV02) -> str` |
| 73 | D1 | `derive_fractal_root_cell_id_v02(*, source_binding_id: str, runtime_policy_id: str, accepted_mode: str, accepted_scope_ref: str) -> str` |
| 74 | D1 | `derive_fractal_child_cell_id_v02(*, topology_seed_id: str, parent_cell_id: str, canonical_child_index: int, accepted_mode: str, selected_local_mode_profile_id: str, source_mode_profile_set_id: str, child_scope_ref: str, runtime_policy_id: str, required_capability_ids: tuple[str, ...], forbidden_claims: tuple[str, ...], child_depth: int) -> str` |
| 75 | D2 | `build_fractal_runtime_source_context_v02(*, transition_registry: TransitionRegistryV01, g2c_source_context: ExecutionModeSourceContextV01, router_input: ExecutionModeRouterInputV01, proposal: ExecutionModeProposalV01, proposal_artifact: KernelArtifactV01, proposal_transition_decision: TransitionDecisionV01, review_input: RootExecutionModeReviewInputV01, decision: RootExecutionModeDecisionV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, decision_artifact: KernelArtifactV01, root_route_transition_decision: TransitionDecisionV01, route_eligibility_artifact: KernelArtifactV01, runtime_policy: FractalRuntimePolicyV02) -> FractalRuntimeSourceContextV02` |
| 76 | D2 | `validate_fractal_runtime_source_context_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 77 | D2 | `validate_runtime_topology_source_binding_against_g2c_v02(value: object, *, source_context: FractalRuntimeSourceContextV02) -> FractalRuntimeValidationReportV02` |
| 78 | D2 | `construct_runtime_execution_topology_v02(source_context: FractalRuntimeSourceContextV02) -> RuntimeExecutionTopologyV02` |
| 79 | D2 | `validate_runtime_execution_topology_against_sources_v02(value: object, *, source_context: FractalRuntimeSourceContextV02) -> FractalRuntimeValidationReportV02` |
| 80 | D2 | `project_runtime_execution_topology_kernel_artifact_v02(topology: RuntimeExecutionTopologyV02, *, source_context: FractalRuntimeSourceContextV02, topology_transition_decision: TransitionDecisionV01) -> KernelArtifactV01` |
| 81 | D2 | `evaluate_route_eligibility_to_topology_transition_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, transition_registry: TransitionRegistryV01) -> TransitionDecisionV01` |
| 82 | D3 | `admit_runtime_execution_topology_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, topology_transition_decision: TransitionDecisionV01, cell_id: str, parent_cell_id: str | None, parent_slot_artifact: KernelArtifactV01 | None, cell_depth: int, scope_ref: str, cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, projected_nodes: tuple[RuntimeTopologyNodeV02, ...], planned_child_cell_ids: tuple[str, ...], admission_decisions: tuple[TransitionDecisionV01, ...], cell_instantiation_order: tuple[str, ...]) -> tuple[FractalCellQueueEntryV02, ...]` |
| 83 | D3 | `advance_fractal_cell_queue_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, current_entry: FractalCellQueueEntryV02, node: RuntimeTopologyNodeV02, cell_input: FractalCellInputV02, transition_decision: TransitionDecisionV01, cell_budget_after: FractalRuntimeBudgetV02, global_budget_after: FractalRuntimeBudgetV02, dependencies: tuple[FractalCellQueueEntryV02, ...], local_child_result: FractalCellResultV02 | None, local_child_result_artifact: KernelArtifactV01 | None, cell_instantiation_order: tuple[str, ...], projected_node_ids: tuple[str, ...], round_start_queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_reason_codes: tuple[str, ...], observed_output_refs: tuple[str, ...], observed_evidence_refs: tuple[str, ...], advisory_refs: tuple[str, ...]) -> FractalCellQueueEntryV02` |
| 84 | D3 | `project_parent_child_scope_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, parent_input: FractalCellInputV02, child_cell_id: str, child_scope_ref: str, parent_budget: FractalRuntimeBudgetV02, child_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02) -> ParentChildScopeProjectionV02` |
| 85 | D3 | `validate_parent_child_scope_against_sources_v02(value: object, *, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, parent_input: FractalCellInputV02, parent_budget: FractalRuntimeBudgetV02, child_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02) -> FractalRuntimeValidationReportV02` |
| 86 | D3 | `build_fractal_cell_input_from_queue_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, cell_id: str, parent_cell_id: str | None, parent_input: FractalCellInputV02 | None, parent_slot_artifact: KernelArtifactV01 | None, scope_projection: ParentChildScopeProjectionV02 | None, cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, initial_queue_entries: tuple[FractalCellQueueEntryV02, ...], initial_queue_artifacts: tuple[KernelArtifactV01, ...], ordered_planned_child_cell_ids: tuple[str, ...]) -> FractalCellInputV02` |
| 87 | D3 | `validate_fractal_cell_input_against_sources_v02(value: object, *, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, parent_input: FractalCellInputV02 | None, parent_slot_artifact: KernelArtifactV01 | None, scope_projection: ParentChildScopeProjectionV02 | None, cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...]) -> FractalRuntimeValidationReportV02` |
| 88 | D3 | `evaluate_fractal_backpressure_v02(*, topology: RuntimeExecutionTopologyV02, policy: FractalRuntimePolicyV02, global_budget: FractalRuntimeBudgetV02, queue_entries: tuple[FractalCellQueueEntryV02, ...], admission_round: int) -> FractalBackpressureStateV02 | None` |
| 89 | D3 | `project_fractal_cell_queue_entry_kernel_artifact_v02(queue_entry: FractalCellQueueEntryV02, *, topology_artifact: KernelArtifactV01, predecessor_artifact: KernelArtifactV01 | None, activation_parent_artifact: KernelArtifactV01 | None, local_child_result_artifact: KernelArtifactV01 | None, source_context: FractalRuntimeSourceContextV02) -> KernelArtifactV01` |
| 90 | D3 | `evaluate_fractal_runtime_state_transition_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, source_artifact: KernelArtifactV01, current_entry: FractalCellQueueEntryV02 | None, node: RuntimeTopologyNodeV02, cell_input: FractalCellInputV02 | None, cell_id: str, parent_cell_id: str | None, planned_child_cell_id: str | None, cell_depth: int, scope_ref: str, cell_budget_before: FractalRuntimeBudgetV02, global_budget_before: FractalRuntimeBudgetV02, dependencies: tuple[FractalCellQueueEntryV02, ...], queue_reason_codes: tuple[str, ...], observed_output_refs: tuple[str, ...], observed_evidence_refs: tuple[str, ...], advisory_refs: tuple[str, ...], local_child_result: FractalCellResultV02 | None, local_child_result_artifact: KernelArtifactV01 | None, validation_report: FractalRuntimeValidationReportV02 | None, parent_return_pre_post_vv_terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...], parent_return_child_results: tuple[FractalCellResultV02, ...], parent_return_partial_failures: tuple[FractalPartialFailureRecordV02, ...], parent_return_result_proposal: dict[str, object] | None, parent_return_post_vv_report: dict[str, object] | None, parent_return_gt_advisory_report: dict[str, object] | None, parent_return_validation_reports: tuple[FractalRuntimeValidationReportV02, ...], revise_observation: FractalReviseObservationV02 | None, backpressure_state: FractalBackpressureStateV02 | None, transition_registry: TransitionRegistryV01) -> TransitionDecisionV01 | None` |
| 91 | D4 | `build_fractal_runtime_execution_bundle_v02(*, source_context: FractalRuntimeSourceContextV02, source_binding: RuntimeTopologySourceBindingV02, topology_seed: RuntimeTopologySeedV02, budgets: tuple[FractalRuntimeBudgetV02, ...], topology_nodes: tuple[RuntimeTopologyNodeV02, ...], topology_edges: tuple[RuntimeTopologyEdgeV02, ...], runtime_assignments: tuple[RuntimeAssignmentV02, ...], topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...], scope_projections: tuple[ParentChildScopeProjectionV02, ...], cell_inputs: tuple[FractalCellInputV02, ...], revise_observations: tuple[FractalReviseObservationV02, ...], partial_failures: tuple[FractalPartialFailureRecordV02, ...], backpressure_states: tuple[FractalBackpressureStateV02, ...], validation_reports: tuple[FractalRuntimeValidationReportV02, ...], result_proposals: tuple[dict[str, object], ...], post_vv_reports: tuple[dict[str, object], ...], gt_advisory_reports: tuple[dict[str, object], ...], cell_results: tuple[FractalCellResultV02, ...], result_artifacts: tuple[KernelArtifactV01, ...], runtime_trace: FractalRuntimeTraceV02, runtime_report: FractalRuntimeReportV02, report_artifact: KernelArtifactV01, transition_decisions: tuple[TransitionDecisionV01, ...], causal_consumption_refs: tuple[CausalConsumptionRefV01, ...]) -> FractalRuntimeExecutionBundleV02` |
| 92 | D4 | `validate_fractal_runtime_execution_bundle_v02(value: object) -> FractalRuntimeValidationReportV02` |
| 93 | D4 | `build_fractal_cell_result_proposal_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, cell_input: FractalCellInputV02, pre_post_vv_terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...], child_results: tuple[FractalCellResultV02, ...], partial_failures: tuple[FractalPartialFailureRecordV02, ...], accepted_output_refs: tuple[str, ...], evidence_refs: tuple[str, ...]) -> dict[str, object]` |
| 94 | D4 | `validate_fractal_cell_result_proposal_v02(value: object, *, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, cell_input: FractalCellInputV02, pre_post_vv_terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...], child_results: tuple[FractalCellResultV02, ...], partial_failures: tuple[FractalPartialFailureRecordV02, ...]) -> FractalRuntimeValidationReportV02` |
| 95 | D4 | `validate_fractal_post_vv_report_v02(value: object, *, result_proposal: dict[str, object], source_context: FractalRuntimeSourceContextV02) -> FractalRuntimeValidationReportV02` |
| 96 | D4 | `validate_fractal_gt_advisory_v02(value: object, *, post_vv_report: dict[str, object], source_context: FractalRuntimeSourceContextV02) -> FractalRuntimeValidationReportV02` |
| 97 | D4 | `evaluate_fractal_revise_observation_v02(*, topology: RuntimeExecutionTopologyV02, cell_input: FractalCellInputV02, queue_entry: FractalCellQueueEntryV02, validation_report: FractalRuntimeValidationReportV02, cell_budget_before: FractalRuntimeBudgetV02, global_budget_before: FractalRuntimeBudgetV02, revision_index: int, newly_validated_evidence_count: int, newly_resolved_constraints_count: int, newly_accepted_outputs_count: int, newly_introduced_conflicts_count: int, consecutive_non_positive_count: int) -> FractalReviseObservationV02` |
| 98 | D4 | `record_fractal_partial_failure_v02(*, topology: RuntimeExecutionTopologyV02, parent_input: FractalCellInputV02, child_result: FractalCellResultV02, failure_stage: str, reason_codes: tuple[str, ...], source_reason_codes: tuple[str, ...], evidence_refs: tuple[str, ...], allocated_cell_budget: FractalRuntimeBudgetV02, final_cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02, required_child: bool, sibling_independent: bool) -> FractalPartialFailureRecordV02` |
| 99 | D4 | `validate_fractal_cell_result_against_input_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, cell_input: FractalCellInputV02, terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...], child_results: tuple[FractalCellResultV02, ...], partial_failures: tuple[FractalPartialFailureRecordV02, ...], result_proposal: dict[str, object], post_vv_report: dict[str, object], gt_advisory_report: dict[str, object], cell_budget: FractalRuntimeBudgetV02, global_budget: FractalRuntimeBudgetV02) -> FractalRuntimeValidationReportV02` |
| 100 | D4 | `aggregate_fractal_runtime_report_v02(*, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, source_binding: RuntimeTopologySourceBindingV02, cell_results: tuple[FractalCellResultV02, ...], queue_entries: tuple[FractalCellQueueEntryV02, ...], backpressure_states: tuple[FractalBackpressureStateV02, ...], runtime_trace: FractalRuntimeTraceV02, final_global_budget: FractalRuntimeBudgetV02, parent_return_transition_decision: TransitionDecisionV01, root_result_artifact: KernelArtifactV01) -> FractalRuntimeReportV02` |
| 101 | D4 | `run_fractal_runtime_v02(source_context: FractalRuntimeSourceContextV02) -> tuple[FractalRuntimeExecutionBundleV02 | None, FractalRuntimeValidationReportV02]` |
| 102 | D4 | `validate_fractal_runtime_report_against_sources_v02(value: object, *, source_context: FractalRuntimeSourceContextV02, source_binding: RuntimeTopologySourceBindingV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, cell_results: tuple[FractalCellResultV02, ...], queue_entries: tuple[FractalCellQueueEntryV02, ...], backpressure_states: tuple[FractalBackpressureStateV02, ...], runtime_trace: FractalRuntimeTraceV02, final_global_budget: FractalRuntimeBudgetV02, parent_return_transition_decision: TransitionDecisionV01, root_result_artifact: KernelArtifactV01) -> FractalRuntimeValidationReportV02` |
| 103 | D4 | `project_fractal_cell_result_kernel_artifact_v02(result: FractalCellResultV02, *, topology_artifact: KernelArtifactV01, terminal_queue_artifacts: tuple[KernelArtifactV01, ...], child_result_artifacts: tuple[KernelArtifactV01, ...], source_context: FractalRuntimeSourceContextV02) -> KernelArtifactV01` |
| 104 | D4 | `project_fractal_runtime_report_kernel_artifact_v02(report: FractalRuntimeReportV02, *, topology_artifact: KernelArtifactV01, result_artifacts: tuple[KernelArtifactV01, ...], source_context: FractalRuntimeSourceContextV02) -> KernelArtifactV01` |
| 105 | D4 | `validate_fractal_runtime_stage_bundle_v02(*, stage: str, artifacts: tuple[KernelArtifactV01, ...], source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, runtime_trace: FractalRuntimeTraceV02, queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...], cell_results: tuple[FractalCellResultV02, ...], result_artifacts: tuple[KernelArtifactV01, ...], runtime_report: FractalRuntimeReportV02 | None, report_artifact: KernelArtifactV01 | None) -> FractalRuntimeValidationReportV02` |
| 106 | D4 | `validate_fractal_runtime_abi_profile_v02(value: tuple[KernelArtifactV01, ...], *, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, runtime_trace: FractalRuntimeTraceV02, queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...], cell_results: tuple[FractalCellResultV02, ...], result_artifacts: tuple[KernelArtifactV01, ...], runtime_report: FractalRuntimeReportV02, report_artifact: KernelArtifactV01) -> FractalRuntimeValidationReportV02` |
| 107 | D4 | `evaluate_fractal_parent_return_transition_v02(*, source_context: FractalRuntimeSourceContextV02, root_result: FractalCellResultV02, root_result_artifact: KernelArtifactV01, ordered_cell_results: tuple[FractalCellResultV02, ...], transition_registry: TransitionRegistryV01) -> TransitionDecisionV01` |
| 108 | D4 | `build_fractal_runtime_causal_consumption_refs_v02(*, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, runtime_assignments: tuple[RuntimeAssignmentV02, ...], queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...], cell_results: tuple[FractalCellResultV02, ...], result_artifacts: tuple[KernelArtifactV01, ...], runtime_trace: FractalRuntimeTraceV02, runtime_report: FractalRuntimeReportV02, report_artifact: KernelArtifactV01) -> tuple[CausalConsumptionRefV01, ...]` |
| 109 | D4 | `validate_fractal_runtime_causal_consumption_refs_v02(value: tuple[CausalConsumptionRefV01, ...], *, source_context: FractalRuntimeSourceContextV02, topology: RuntimeExecutionTopologyV02, topology_artifact: KernelArtifactV01, runtime_assignments: tuple[RuntimeAssignmentV02, ...], queue_entries: tuple[FractalCellQueueEntryV02, ...], queue_artifacts: tuple[KernelArtifactV01, ...], cell_results: tuple[FractalCellResultV02, ...], result_artifacts: tuple[KernelArtifactV01, ...], runtime_trace: FractalRuntimeTraceV02, runtime_report: FractalRuntimeReportV02, report_artifact: KernelArtifactV01, stage_d_c_artifacts: tuple[KernelArtifactV01, ...]) -> FractalRuntimeValidationReportV02` |
| 110 | D4 | `validate_fractal_runtime_causal_counterfactual_v02(*, execution_bundle: FractalRuntimeExecutionBundleV02, causal_ref: CausalConsumptionRefV01, mutated_source_artifact: KernelArtifactV01) -> FractalRuntimeValidationReportV02` |
| 111 | D2 | `build_fractal_runtime_transition_registry_profile_v02() -> TransitionRegistryV01` |
| 112 | D2 | `validate_fractal_runtime_transition_registry_profile_v02(value: object) -> tuple[str, ...]` |
| 113 | D2 | `fractal_runtime_transition_registry_profile_to_plain_dict_v02(value: TransitionRegistryV01) -> dict[str, object]` |
| 114 | D2 | `validate_fractal_runtime_transition_decision_v02(value: object, *, registry: TransitionRegistryV01, source_artifact: KernelArtifactV01, target_artifact: KernelArtifactV01) -> tuple[str, ...]` |
| 115 | D2 | `fractal_runtime_transition_decision_to_plain_dict_v02(value: TransitionDecisionV01) -> dict[str, object]` |
| 116 | D2 | `rebuild_fractal_runtime_transition_decision_identity_v02(value: TransitionDecisionV01) -> str` |

The cumulative surface is exact: D1 has 74 module functions and no G2-D
Transition functions or facade attributes; D2 has 81 module functions and all
six Transition functions; D3 has 90 module functions and all six Transition
functions; D4 has all 110 module functions, all six Transition functions, and
136 direct package attributes. D5 and D6 add none. Before its owning slice, a
function is absent as a callable. Stubs, aliases, proxies, lazy wrappers,
fallback imports, `NotImplemented` bodies, and speculative attributes are
forbidden. D1 may import generic Transition types only; D2 adds concrete G2-D
profile imports after the Transition module owns them. The G2-D module never
imports aggregate `hedgehog.kernel`, and base modules never reverse-import it.
Any ID-typed signature parameter is an already-built identity supplied only by
the internal ordered constructor together with its owning object family; no
top-level caller string is accepted. Budget counters derive solely from the
predecessor plus event law. Queue state, prior state, priority, instance,
snapshot, round, queue reasons, and lineage derive from predecessor,
Transition, projection, and immutable scheduler context. Result outcome and
reasons derive from terminal precedence; return requirement is fixed true. Validation
status derives from stage/reasons/nullability. No builder accepts those values
as caller authority.

The v0.1.10 semantic signature delta is exact and closed: only signature 90
adds the typed PARENT_RETURN family after `validation_report` and before
`revise_observation`. Every v0.1.9 signature and semantic correction otherwise
remains exact. No other public signature changes. The contract is frozen in
D1; signature 90 first exists in D3, where every non-PARENT_RETURN call proves
the family empty/null. Its PARENT_RETURN branch is unavailable until D4 owns
the proposal, Post V&V, GT, and contextual validators. No stub, fallback,
proxy, or alternate evaluator is introduced.

`validate_fractal_runtime_validation_report_v02` is total and exception-safe.
It returns `()` for a valid report and otherwise returns the exact ordered
public reason tuple after checking type, scalar and container laws, identity
rebuild, target membership, target/ID/stage mapping, PASS/NONE and
FAIL_CLOSED/non-NONE/null-ID laws, and fixed Root-review/nonclaim fields. It
never constructs another `FractalRuntimeValidationReportV02`.

The composition signatures are contextual, not ID-copy validators. Proposal
validation receives the exact input, terminal queue, child result, and partial
failure families. Pre-result validation has no candidate `value`; it validates
those families plus proposal, Post V&V, GT, and both budgets before a result
exists and emits `CELL_RESULT_PRECONDITIONS` with the proposal ID on PASS.
Scope validation receives the parent input and all three budget axes. Cell-
input composition and validation receive the topology artifact, optional exact
parent input/slot/projection, both budgets, and exact initial queue objects and
artifacts. ABI and causal tuple validators use exact tuple annotations rather
than an unexplained object.

`run_fractal_runtime_v02` returns `(accepted_bundle,
external_complete_profile_pass)` on success. Before an accepted final bundle,
it returns `(None, first_fail_closed_report_in_canonical_operation_order)`. If
complete-profile validation rejects the final candidate, it returns
`(None, complete_profile_fail_closed_report)`. It never returns a partial or
unvalidated bundle and never fabricates a PASS.

### 9.5 Exact public reason registry

The public registry has exactly 220 unique entries in this order:

```text
g2d_type_invalid
g2d_field_count_invalid
g2d_field_type_invalid
g2d_identity_invalid
g2d_identity_mismatch
g2d_serialization_invalid
g2d_tuple_order_invalid
g2d_tuple_duplicate
g2d_text_invalid
g2d_integer_invalid
g2d_boolean_is_not_integer
g2d_float_forbidden
g2d_decimal_forbidden
g2d_nonfinite_forbidden
g2d_wall_clock_forbidden
g2d_randomness_forbidden
g2d_caller_identity_forbidden
g2d_caller_pass_forbidden
g2d_secret_material_forbidden
g2d_callback_forbidden
g2d_client_handle_forbidden
g2d_effect_handle_forbidden
g2d_raw_provider_output_forbidden
g2d_unknown_enum
g2d_source_context_invalid
g2d_g2c_context_invalid
g2d_g2c_router_input_invalid
g2d_g2c_proposal_invalid
g2d_g2c_proposal_artifact_invalid
g2d_g2c_proposal_transition_invalid
g2d_g2c_review_input_invalid
g2d_g2c_root_kernel_invalid
g2d_g2c_root_input_invalid
g2d_g2c_root_result_invalid
g2d_g2c_decision_invalid
g2d_g2c_decision_artifact_invalid
g2d_g2c_post_root_transition_invalid
g2d_route_eligibility_missing
g2d_route_eligibility_invalid
g2d_route_eligibility_substituted
g2d_route_eligibility_context_mismatch
g2d_route_class_not_topology_eligible
g2d_shortcut_consumption_forbidden
g2d_terminal_consumption_forbidden
g2d_direct_root_decision_consumption_forbidden
g2d_mode_not_topology_eligible
g2d_mode_upgrade_forbidden
g2d_mode_downgrade_forbidden
g2d_mode_profile_mismatch
g2d_full_fractal_capability_missing
g2d_non_fractal_recursion_forbidden
g2d_topology_policy_invalid
g2d_topology_source_binding_invalid
g2d_topology_identity_mismatch
g2d_topology_lineage_mismatch
g2d_topology_time_mismatch
g2d_topology_node_invalid
g2d_topology_edge_invalid
g2d_topology_assignment_invalid
g2d_topology_order_invalid
g2d_topology_cycle
g2d_topology_unknown_node
g2d_topology_duplicate_edge
g2d_topology_orphan_node
g2d_topology_parent_mismatch
g2d_topology_provider_owned_forbidden
g2d_topology_authority_claim_forbidden
g2d_queue_entry_invalid
g2d_queue_state_unknown
g2d_queue_transition_unknown
g2d_queue_transition_illegal
g2d_queue_caller_state_forbidden
g2d_queue_order_mismatch
g2d_queue_priority_source_forbidden
g2d_terminal_queue_reentry_forbidden
g2d_backpressure_invalid
g2d_backpressure_work_drop_forbidden
g2d_backpressure_lineage_missing
g2d_depth_limit_exceeded
g2d_fan_out_limit_exceeded
g2d_total_cell_limit_exceeded
g2d_parallelism_limit_exceeded
g2d_revise_limit_exceeded
g2d_wall_time_budget_exceeded
g2d_token_budget_exceeded
g2d_provider_budget_exceeded
g2d_budget_invalid
g2d_budget_negative
g2d_budget_overflow
g2d_budget_double_spend
g2d_budget_hidden_reset
g2d_sibling_budget_borrowing_forbidden
g2d_child_budget_widening
g2d_child_depth_mismatch
g2d_child_scope_widening
g2d_child_capability_widening
g2d_child_forbidden_narrowing
g2d_child_ttl_widening
g2d_child_lineage_mismatch
g2d_revise_observation_invalid
g2d_revise_progress_mismatch
g2d_revise_hidden_retry_forbidden
g2d_revise_terminal_caller_selection_forbidden
g2d_no_progress_deadend
g2d_resolvable_input_needs_user
g2d_partial_failure_invalid
g2d_required_child_failure
g2d_sibling_evidence_erasure_forbidden
g2d_success_laundering_forbidden
g2d_parent_disposition_mismatch
g2d_cell_input_invalid
g2d_cell_result_invalid
g2d_cell_result_context_mismatch
g2d_cell_root_claim_forbidden
g2d_cell_final_output_claim_forbidden
g2d_cell_permission_claim_forbidden
g2d_cell_packet_claim_forbidden
g2d_cell_receipt_claim_forbidden
g2d_cell_effect_claim_forbidden
g2d_runtime_trace_invalid
g2d_runtime_report_invalid
g2d_runtime_report_identity_mismatch
g2d_abi_profile_invalid
g2d_abi_bundle_invalid
g2d_abi_projection_substituted
g2d_transition_profile_invalid
g2d_transition_decision_substituted
g2d_parent_return_invalid
g2d_sources_valid
g2d_route_eligibility_valid
g2d_topology_constructed
g2d_topology_valid
g2d_queue_admitted
g2d_queue_state_advanced
g2d_scope_projection_valid
g2d_budget_accounting_valid
g2d_revise_progress_valid
g2d_partial_failure_recorded
g2d_backpressure_recorded
g2d_cell_result_valid
g2d_runtime_trace_valid
g2d_runtime_report_valid
g2d_abi_profile_valid
g2d_transition_topology_construction_allowed
g2d_transition_queue_admission_allowed
g2d_transition_backpressure_deferred
g2d_transition_pending_ready_allowed
g2d_transition_ready_running_allowed
g2d_transition_running_validating_allowed
g2d_transition_bounded_revise_allowed
g2d_transition_completed_recorded
g2d_transition_degraded_recorded
g2d_transition_blocked_recorded
g2d_transition_needs_user_recorded
g2d_transition_deadend_recorded
g2d_transition_completed_parent_return
g2d_transition_degraded_parent_return
g2d_transition_blocked_parent_return
g2d_transition_needs_user_parent_return
g2d_transition_deadend_parent_return
g2d_identity_dependency_cycle
g2d_topology_seed_invalid
g2d_root_cell_identity_invalid
g2d_child_cell_identity_invalid
g2d_queue_predecessor_invalid
g2d_queue_artifact_lineage_invalid
g2d_post_vv_time_source_invalid
g2d_gt_time_source_invalid
g2d_post_vv_fallback_forbidden
g2d_causal_consumption_invalid
g2d_causal_consumption_missing
g2d_causal_counterfactual_mismatch
g2d_unused_field_disposition_missing
g2d_partial_failure_result_cycle
g2d_validation_report_identity_cycle
g2d_node_instance_geometry_invalid
g2d_cell_result_postorder_invalid
g2d_child_result_direct_parent_return_forbidden
g2d_mode_template_matrix_invalid
g2d_source_profile_binding_mismatch
g2d_scope_relation_unproven
g2d_budget_predecessor_invalid
g2d_budget_allocation_oversubscribed
g2d_budget_debit_mismatch
g2d_result_proposal_invalid
g2d_post_vv_report_invalid
g2d_gt_advisory_invalid
g2d_terminal_outcome_mapping_invalid
g2d_abi_field_partition_invalid
g2d_trace_lineage_invalid
g2d_backpressure_reason_invalid
g2d_root_result_required_for_parent_return
g2d_runtime_bundle_report_missing
g2d_causal_json_pointer_invalid
g2d_causal_reason_prefix_invalid
g2d_policy_profile_identity_mismatch
g2d_cell_edge_projection_invalid
g2d_leaf_projection_unexecutable
g2d_static_input_derivation_invalid
g2d_assignment_trace_invalid
g2d_global_budget_binding_missing
g2d_budget_event_pair_mismatch
g2d_budget_state_transition_invalid
g2d_pre_root_lifecycle_escalation_forbidden
g2d_gt_report_identity_collision
g2d_gt_report_context_id_invalid
g2d_validation_status_stage_mismatch
g2d_validation_target_id_mismatch
g2d_queue_sequence_invalid
g2d_blocked_reason_selection_invalid
g2d_result_report_ref_mismatch
g2d_child_slot_activation_invalid
g2d_cell_input_build_order_invalid
g2d_node_cell_outcome_conflation
g2d_runtime_report_status_outcome_mismatch
g2d_runtime_outcome_root_result_mismatch
g2d_budget_event_context_invalid
g2d_transition_target_dependency_cycle
g2d_revise_budget_dependency_cycle
g2d_execution_bundle_dependency_cycle
```

Source-owned reasons remain separate from public G2-D reasons. Validators are
total and fail closed without leaking raw objects, exception names, stack data,
or secrets.

## 10. RuntimeExecutionTopology Contract

The topology is version `v0.2`, source-bound, immutable, acyclic, and locally
owned. Its source parent is the actual RouteEligibility artifact. The topology
seed is not the topology and creates no scheduling authority. Every seed,
cell, node, edge, assignment, queue snapshot, scope projection, and budget is
rebuilt before the complete runtime family is accepted.

Construction validates the complete G2-C profile again. It does not trust a
supplied PASS report. The request, transaction, Root, domain, accepted mode,
accepted scope, proposal artifact, decision artifact, RouteEligibility
artifact, both G2-C Transition decisions, Registry ID, ABI profile, time
envelope, traces, and parents must match the actual source objects.

The identity and execution build DAG is exact and acyclic:

1. Validate the complete actual G2-C ABI, Transition, Root, proposal, local
   profile, feasibility, routing snapshot, and RouteEligibility family.
2. Derive and validate `FractalRuntimePolicyV02` from the actual source-required
   capability tuple and actual permitted-narrower-scope tuple. Its fixed
   profile literal is not its identity.
3. Build and validate `FractalRuntimeSourceContextV02` from that policy and the
   actual G2-C family, then build and validate
   `RuntimeTopologySourceBindingV02` from the source context.
4. Derive the root cell ID from source binding, content-derived policy, mode,
   scope, and exact `ROOT_CELL` marker.
5. Build `RuntimeTopologySeedV02` from prior identities and immutable local
   profile, time, trace, and parent material.
6. Build the root `ALLOCATED` `ROOT_GLOBAL_AND_CELL` budget from the seed and
   root cell with event `INITIAL_ALLOCATION` bound to that root cell ID.
7. Build ordered static node templates from seed and exact mode rows. Static
   `SOURCE_CONTEXT` input refs are only source binding, policy, and source time;
   every runtime-derived node has `input_refs=()`.
8. Build ordered root and leaf-class edge templates from seed and already-built
   node IDs, then assignments from seed, node, canonical index, binding rows,
   exact executor/capability flags, and exact assignment traces.
9. Build and contextually validate the non-authoritative
   `RuntimeExecutionTopologyV02` candidate from the complete prior template
   family, global budget, time, traces, and parents.
10. Evaluate t01 against the actual G2-C RouteEligibility artifact and actual
    Root commit. Only an allowed t01 decision permits projection of the one
    topology artifact and Stage D-A. No queue consumption exists before this
    order completes.
11. Derive the full-fractal root's two planned child IDs from settled seed,
    parent cell, canonical child indexes 0 and 1 under
    `CHILD_SLOT_INDEX_ROWS_V02`, equal accepted scope, and policy.
    Planning creates no child instance, budget, scope projection, queue, input,
    result, cell-count debit, or causal child-result row. Non-fractal modes
    derive no planned child ID.
12. Build and validate root ACTIVATE and CELL_CREATE budget successors in that
    order. INITIAL_ALLOCATION and ACTIVATE debit no cell. Accepted CELL_CREATE
    alone debits the root once and inserts it into the instantiated-cell set.
    Append every accepted budget immediately to `BUDGET_CONSTRUCTION_LOG_V02`;
    root CELL_CREATE is the immutable allocation basis later bound to root input.
13. Derive one t02 decision per projected root node from topology-artifact pre-
    state. Build each initial PENDING snapshot from its already-built t02
    decision and project its artifact. Append every root initial entry/artifact
    pair to the queue execution-build log in root projected-node order and each
    artifact to `RUNTIME_ABI_ARTIFACT_BUILD_LOG_V02` at that accepted point.
    Child-slot snapshots carry their planned IDs; all others carry `None`.
14. Build and validate root input with the complete initial queue tuple and
    planned-child tuple. Freeze each scheduler round's latest occurrence per
    node and exact admission order. Process at most one occurrence per node;
    every decision sees all earlier accepted same-round successors and the
    latest global budget. Ordinary dependency wait creates nothing.
15. When a decision exists, build only the budget successors required by that
    rule and append each accepted budget to the budget log, then build the
    target queue snapshot and artifact and validate source/target binding.
    Non-PARENT_RETURN t08-t12 decisions build no budget successor and carry the
    current budget IDs unchanged. Append accepted queue and ABI artifacts to
    their logs. No target snapshot is an evaluator input.
16. With the exact RUNNING parent child-slot entry and artifact settled, run an
    internal deterministic activation precheck. It first proves exact source,
    queue/artifact, topology, node, assignment, parent input, policy, scope,
    planned-ID/slot, allocation-basis, budget, identity, lineage, predecessor,
    event, state, counter, type, and ordering geometry. Structural or contextual
    corruption returns the first FAIL_CLOSED report immediately. Only after
    that proof does it derive the planned child projection and one valid
    admission, denial, resolvable-input, or no-progress disposition without
    constructing a child.
17. A structurally valid denied precheck enters only the no-child activation-
    gate branch. It derives exact bounded evidence and public queue reasons,
    releases the RUNNING parent-slot reservation through t06 with no child
    result/artifact, and records exactly one valid t10 BLOCKED, t11 NEEDS_USER,
    or t12 DEADEND terminal under
    `CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02`. It creates no accepted child
    budget, scope projection, queue, input, result, partial-failure record,
    cell-count debit, activation row, child-return row, or child ABI artifact.
    Structural corruption and post-precheck candidate defects instead return
    FAIL_CLOSED and create no terminal slot, merge input, causal row, or bundle.
18. After a passing precheck, use the immutable immediate-parent CELL_CREATE
    allocation basis named by parent input, the accepted parent initial queues,
    and zero-based planned slot. Build child INITIAL_ALLOCATION from that common
    sibling epoch, then scope projection; contextually validate both. Latest
    parent-local and global budgets separately prove activation capacity.
19. Build paired child-local/global ACTIVATE successors. Commit activation only
    after those successors and projection validate. Then build paired
    CELL_CREATE successors and debit the planned cell exactly once. Only after
    accepted CELL_CREATE append the same planned ID to instantiation preorder,
    derive child t02 decisions, and admit leaf queues/artifacts whose initial
    ABI parents include the RUNNING parent-slot artifact. Append accepted
    budgets, queues, and artifacts to their respective construction logs.
20. Build and validate child input from the parent-slot artifact, parent
    evidence, scope projection, child-local CELL_CREATE allocation basis,
    current global budget, and source lineage before child node 0 becomes READY.
    Unexpected candidate failure fails closed and enters no accepted bundle.
21. Continue deterministic dependency scheduling. Budgets remain ACTIVE across
    every non-PARENT_RETURN terminal decision. For each cell, freeze the exact
    pre-Post-V&V terminal prefix after every required projected node before
    POST_VV is terminal. Build and validate one ResultProposal from that prefix,
    actual child results, and actual partial failures; then run Post V&V once
    with source KT and GT once. Build the exact RESULT_PROPOSAL, POST_VV_REPORT,
    and GT_ADVISORY_REPORT PASS reports. PARENT_RETURN signature 90 receives the
    actual complete typed family and those three reports, independently
    reconstructs them, rederives observations/reasons, reads status only from
    `result_payload.status`, and maps it through
    `PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02`. Its t08-t12 decision alone
    creates the cell completion budgets. A substituted family returns the first
    FAIL_CLOSED report and creates no dependent queue or bundle. After the
    PARENT_RETURN queue and budgets validate, complete-terminal pre-result
    validation runs and then the result/artifact is built.
22. For revise, build observation from VALIDATING state and before budgets;
    derive t07; reserve one admission slot; build paired REVISE successors;
    then build and validate READY snapshot/artifact. The observation predicts no
    successor ID and no stale or future admission state is accepted.
23. Immediately after each actual child result artifact validates, build exactly one
    zero-delta root/global ACTIVE CHILD_AGGREGATE successor from that child's
    global completion snapshot; no event interleaves. Return the child through
    its RUNNING parent slot using the latest post-aggregate global budget. t06
    introduces the result observation; t08-t12 map and copy it. Queue artifacts
    name the child result parent and append to both logs. The invoked branch is
    mutually exclusive with the no-child gate branch. Only after both slots
    terminate may FRACTAL_MERGE consume the two terminal slot returns in human
    ordinals 1 then 2; it never assumes that both slots own child results.
24. Construct results bottom-up. Every actual result binds its unique ALLOCATED
    INITIAL_ALLOCATION snapshot, unique local FINAL snapshot, and matching
    completion global snapshot. A child result precedes any failure naming it
    and its parent-slot return. No-child slots create neither result nor failure
    record. The root follows actual descendants, actual failures, the two slot
    returns, merge, complete terminal queues, and its projected PARENT_RETURN
    terminal. Ordered child-result IDs omit uninstantiated planned slots.
25. Root PARENT_RETURN alone builds the unique ROOT_GLOBAL_AND_CELL FINAL
    budget. Build the root result/artifact from it and append the artifact after
    all dependencies. Pass only that root result to one t13-t17 evaluator.
26. Build runtime trace from typed queue/result/artifact/Transition families and
    exact queue, budget, and runtime-ABI logs. Build one report from the actual
    root-result artifact. Neither builder accepts raw reference tuples.
27. Validate the report against explicit settled sources. Validate Stage D-A,
    D-B, and D-C from explicit artifact/object families, then validate the full
    ABI profile without an execution-bundle input.
28. Build and validate ordered cross-artifact `CausalConsumptionRefV01` objects
    from the same explicit settled families and exact Stage-D-C tuple.
29. Assemble the exact retained pre-bundle validation-report tuple and build
    `FractalRuntimeExecutionBundleV02` exactly once with complete causal refs.
30. Validate the final bundle. Normal runtime returns the accepted bundle and
    external `COMPLETE_PROFILE` PASS report, or `None` and the first canonical
    FAIL_CLOSED report. The external report is not inserted into the bundle.
31. Normal runtime stops at that result pair. Causal counterfactual mutation is
    a D5 proof/diagnostic call against an already accepted bundle, not a step in
    `run_fractal_runtime_v02` and not normal bundle material.

The queue execution-build log is internal deterministic state, not a new type
or public function. Every later accepted root or child successor is appended
immediately after its decision -> budget -> entry -> artifact -> contextual-
validation sequence. No later lexical, cell-preorder, result-postorder, node-
grouping, or predecessor-regrouping sort is permitted. The unchanged log is
the sole queue-order source for bundle queue entries and artifacts, runtime
trace queue and state-decision tuples, occurrence-aligned bundle Transition
objects, and retained queue reports.

`RUNTIME_ABI_ARTIFACT_BUILD_LOG_V02` is a second internal append-only log, not
a type or public function. It records each contextually accepted post-topology
queue or result artifact at its actual construction point. Child result
artifacts therefore precede the parent-slot t06 and terminal queue artifacts
that name them. The root result follows all required descendant and terminal
queue artifacts. No report artifact enters this log, and no lexical,
cell-preorder, result-postorder, node-group, queue-group, result-group, or type
sort is allowed. Runtime trace ABI refs, Stage D-B, ABI validation, and causal
construction consume this interleaved log unchanged.

`BUDGET_CONSTRUCTION_LOG_V02` is a third internal append-only log, not a type
or public function. It records every contextually accepted immutable budget at
its construction point. Bundle budgets, trace `budget_ids`, budget-chain and
completion-pair validators, and final root/global selection consume it
unchanged. No lexical, cell, event, scope, or predecessor sort is permitted.

No provisional bundle, empty causal surrogate, replacement, reverse
dependency, or fixed-point construction exists.

No fixed point, provisional ID, reverse identity, or caller-selected ID is
permitted. Static topology nodes and assignments are request-local immutable
templates with binding classes and no runtime cell, parent-cell, scope,
budget, topology, queue, or assignment reverse reference; their static
`scope_ref` is only the accepted root scope and their `depth` is template
relative. Queue snapshots
instantiate templates after topology exists. A non-`FRACTAL_CELL` node has
`planned_child_cell_id=None`; a child-slot instance carries the exact planned
child cell ID. Node-template identity never changes when that cell is planned,
and no post-topology assignment is invented. Failure at any step blocks every
dependent later object.

Negative coverage includes identity dependency cycles, caller-selected seed,
root-cell or child-cell IDs, topology substitution, node/assignment reverse
reference injection, queue predecessor substitution or broken chains, result
self/parent/forward/foreign cycles, validation-report cycles, duplicate or
reordered descendants, and a failure record absent from its parent result.

The module imports only concrete base modules. It imports no aggregate
`hedgehog.kernel`, provider, connector, live lane, historical router, or donor
demo. ABI, Root, G2-C, SemanticWork, trust, integrity, and Effect Firewall must
not reverse-import the G2-D module.

## 11. Mode-Specific Topology Profiles

No mode upgrades or downgrades. Missing capability fails closed. The future
module freezes these exact constants:

```text
MODE_NODE_TEMPLATE_ROWS_V02
MODE_EDGE_TEMPLATE_ROWS_V02
MODE_ASSIGNMENT_TEMPLATE_ROWS_V02
CELL_NODE_PROJECTION_ROWS_V02
CELL_EDGE_PROJECTION_ROWS_V02
NODE_WORK_QUEUE_V02
```

The table symbols are exact values, not implementation shorthand:

```text
SRC_CAPS = RuntimeTopologySourceBindingV02.required_downstream_capability_ids
CAP_RUNTIME = capability:g2d:local_runtime:v02
CAP_POST_VV = capability:g2d:post_vv:v02
CAP_GT = capability:g2d:gt_advisory:v02
CAP_PARENT_RETURN = capability:g2d:parent_return:v02
CAP_FRACTAL_CHILD = capability:g2d:fractal_child:v02
LOCAL_CAPS = (CAP_RUNTIME,CAP_POST_VV,CAP_GT,CAP_PARENT_RETURN,CAP_FRACTAL_CHILD)
ALL_CAPS = SRC_CAPS followed by each LOCAL_CAPS value not already present
FORBIDDEN = FORBIDDEN_OUTPUT_KINDS
CURRENT = (CURRENT_CELL,CURRENT_CELL_SCOPE,CURRENT_CELL_BUDGET)
CHILD_SLOT = (CURRENT_CELL_CHILD_SLOT,PERMITTED_CHILD_SCOPE,CHILD_ALLOCATION_BUDGET)
```

`MODE_NODE_TEMPLATE_ROWS_V02` has columns `(canonical_index,node_kind,
cell_binding_class,scope_binding_class,budget_binding_class,
required_capability_ids,allowed_capability_ids,forbidden_claims,
input_ref_derivation_class,expected_output_kind,required,
recursive_expansion_allowed,root_review_required,authority_created,
permission_created,real_world_effects_count)` and exactly these ordered
semantic rows. Every displayed row fixes the final four fields to
`(true,false,false,0)`:

For every built node, `accepted_mode` is the exact source mode,
template-relative `depth=0`, and `scope_ref` is the exact accepted root scope.
Its `trace_refs` are exactly `(topology_seed_id,source_binding_id,
canonical_index_as_decimal_text,node_kind)`.
Concrete runtime depth and any permitted narrower child scope exist only in
queue, cell-input, budget, and scope-projection instances.

| Mode | Exact ordered node rows |
|---|---|
| `memory_informed` | `(0,MEMORY_CONTEXT,CURRENT,CAP_RUNTIME,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,MEMORY_CONTEXT_OUTPUT,true,false)`; `(1,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(2,POST_VV,CURRENT,CAP_POST_VV,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,POST_VV_REPORT,true,false)`; `(3,GT_ADVISORY,CURRENT,CAP_GT,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,GT_ADVISORY_REPORT,true,false)`; `(4,PARENT_RETURN,CURRENT,CAP_PARENT_RETURN,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,PARENT_RETURN_EVIDENCE,true,false)` |
| `local_slm` | `(0,LOCAL_MODEL_DECLARATION,CURRENT,CAP_RUNTIME,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,LOCAL_MODEL_DECLARATION_OUTPUT,true,false)`; `(1,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(2,POST_VV,CURRENT,CAP_POST_VV,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,POST_VV_REPORT,true,false)`; `(3,GT_ADVISORY,CURRENT,CAP_GT,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,GT_ADVISORY_REPORT,true,false)`; `(4,PARENT_RETURN,CURRENT,CAP_PARENT_RETURN,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,PARENT_RETURN_EVIDENCE,true,false)` |
| `cloud_llm` | `(0,CLOUD_MODEL_DECLARATION,CURRENT,CAP_RUNTIME,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,CLOUD_MODEL_DECLARATION_OUTPUT,true,false)`; `(1,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(2,POST_VV,CURRENT,CAP_POST_VV,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,POST_VV_REPORT,true,false)`; `(3,GT_ADVISORY,CURRENT,CAP_GT,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,GT_ADVISORY_REPORT,true,false)`; `(4,PARENT_RETURN,CURRENT,CAP_PARENT_RETURN,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,PARENT_RETURN_EVIDENCE,true,false)` |
| `full_semantic` | `(0,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(1,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(2,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(3,SEMANTIC_MERGE,CURRENT,CAP_RUNTIME,ALL_CAPS,FORBIDDEN,FAN_IN_OUTPUTS_0_1_2,SEMANTIC_MERGE_OUTPUT,true,false)`; `(4,POST_VV,CURRENT,CAP_POST_VV,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,POST_VV_REPORT,true,false)`; `(5,GT_ADVISORY,CURRENT,CAP_GT,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,GT_ADVISORY_REPORT,true,false)`; `(6,PARENT_RETURN,CURRENT,CAP_PARENT_RETURN,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,PARENT_RETURN_EVIDENCE,true,false)` |
| `full_fractal` | `(0,SEMANTIC_ACTOR,CURRENT,SRC_CAPS,ALL_CAPS,FORBIDDEN,SOURCE_CONTEXT,SEMANTIC_ACTOR_OUTPUT,true,false)`; `(1,FRACTAL_CELL,CHILD_SLOT,CAP_FRACTAL_CHILD,ALL_CAPS,FORBIDDEN,PREDECESSOR_AND_CHILD_SLOT_1,FRACTAL_CELL_OUTPUT,true,true)`; `(2,FRACTAL_CELL,CHILD_SLOT,CAP_FRACTAL_CHILD,ALL_CAPS,FORBIDDEN,PREDECESSOR_AND_CHILD_SLOT_2,FRACTAL_CELL_OUTPUT,true,true)`; `(3,FRACTAL_MERGE,CURRENT,CAP_RUNTIME,ALL_CAPS,FORBIDDEN,FAN_IN_CHILD_SLOT_RETURNS_1_2,FRACTAL_MERGE_OUTPUT,true,false)`; `(4,POST_VV,CURRENT,CAP_POST_VV,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,POST_VV_REPORT,true,false)`; `(5,GT_ADVISORY,CURRENT,CAP_GT,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,GT_ADVISORY_REPORT,true,false)`; `(6,PARENT_RETURN,CURRENT,CAP_PARENT_RETURN,ALL_CAPS,FORBIDDEN,PREDECESSOR_OUTPUTS,PARENT_RETURN_EVIDENCE,true,false)` |

Here `CURRENT` and `CHILD_SLOT` expand into the three binding-class columns;
each capability symbol denotes a one-element tuple except `SRC_CAPS` and
`ALL_CAPS`. The six input derivation classes above are the complete
v0.2 vocabulary. `SOURCE_CONTEXT` rows have static
`input_refs=(source_binding_id,runtime_policy_id,source_time_envelope_ref)`.
Every predecessor or fan-in row has static `input_refs=()`; concrete runtime
output and evidence refs enter only cell inputs and queue snapshots. A mismatch
is `g2d_static_input_derivation_invalid`. The template node `scope_ref` is always the accepted root
scope; a concrete narrower child scope exists only on the queue/input/scope
projection runtime instance.

`MODE_EDGE_TEMPLATE_ROWS_V02` has columns `(canonical_index,
cell_projection_class,source_node_index,target_node_index,edge_kind,required,
evidence_flow_allowed,authority_flow_allowed,root_review_required,
trace_derivation)`:

| Mode | Exact ordered edge rows |
|---|---|
| `memory_informed`, `local_slm`, `cloud_llm` | `(0,ROOT_CELL_PROJECTION,0,1,DATA_DEPENDENCY,true,true,false,true,EDGE_TRACE)`; `(1,ROOT_CELL_PROJECTION,1,2,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(2,ROOT_CELL_PROJECTION,2,3,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(3,ROOT_CELL_PROJECTION,3,4,RETURN,true,true,false,true,EDGE_TRACE)` |
| `full_semantic` | `(0,ROOT_CELL_PROJECTION,0,3,DATA_DEPENDENCY,true,true,false,true,EDGE_TRACE)`; `(1,ROOT_CELL_PROJECTION,1,3,DATA_DEPENDENCY,true,true,false,true,EDGE_TRACE)`; `(2,ROOT_CELL_PROJECTION,2,3,DATA_DEPENDENCY,true,true,false,true,EDGE_TRACE)`; `(3,ROOT_CELL_PROJECTION,3,4,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(4,ROOT_CELL_PROJECTION,4,5,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(5,ROOT_CELL_PROJECTION,5,6,RETURN,true,true,false,true,EDGE_TRACE)` |
| `full_fractal` | `(0,ROOT_CELL_PROJECTION,0,1,PARENT_CHILD,true,true,false,true,EDGE_TRACE)`; `(1,ROOT_CELL_PROJECTION,0,2,PARENT_CHILD,true,true,false,true,EDGE_TRACE)`; `(2,ROOT_CELL_PROJECTION,1,3,DATA_DEPENDENCY,true,true,false,true,EDGE_TRACE)`; `(3,ROOT_CELL_PROJECTION,2,3,DATA_DEPENDENCY,true,true,false,true,EDGE_TRACE)`; `(4,ROOT_CELL_PROJECTION,3,4,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(5,ROOT_CELL_PROJECTION,4,5,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(6,ROOT_CELL_PROJECTION,5,6,RETURN,true,true,false,true,EDGE_TRACE)`; `(7,FRACTAL_LEAF_PROJECTION,0,4,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(8,FRACTAL_LEAF_PROJECTION,4,5,VALIDATION,true,true,false,true,EDGE_TRACE)`; `(9,FRACTAL_LEAF_PROJECTION,5,6,RETURN,true,true,false,true,EDGE_TRACE)` |

`EDGE_TRACE` means exactly `(topology_seed_id,source_node_id,target_node_id,
canonical_index_as_decimal_text,cell_projection_class)`. It is semantic order,
never lexical order. The full-fractal static topology is exactly seven nodes,
ten edges, and seven assignments. Its root edges are 0-6 and its leaf edges
are 7-9. No root-only edge controls a leaf and no leaf edge can short-circuit
the root `FRACTAL_MERGE`.

`MODE_ASSIGNMENT_TEMPLATE_ROWS_V02` has columns `(canonical_index,node_index,
assignment_kind,executor_component_id,capability_ids,cell_binding_class,
scope_binding_class,budget_binding_class,provider_call_allowed,
network_call_allowed,connector_call_allowed,trace_refs,
root_review_required,authority_created,permission_created,effect_created,
real_world_effects_count)`. There is exactly one row per node, in
node order, using this total mapping:

| Node kind | Assignment / component / capabilities / binding |
|---|---|
| `MEMORY_CONTEXT` | `LOCAL_DETERMINISTIC / fractal_runtime_v02 / (CAP_RUNTIME) / CURRENT` |
| `LOCAL_MODEL_DECLARATION` | `LOCAL_MODEL_DECLARED / fractal_runtime_v02 / (CAP_RUNTIME) / CURRENT` |
| `CLOUD_MODEL_DECLARATION` | `CLOUD_MODEL_DECLARED / fractal_runtime_v02 / (CAP_RUNTIME) / CURRENT` |
| `SEMANTIC_ACTOR` | `SEMANTIC_ACTOR / fractal_runtime_v02 / SRC_CAPS / CURRENT` |
| `SEMANTIC_MERGE` | `LOCAL_DETERMINISTIC / fractal_runtime_v02 / (CAP_RUNTIME) / CURRENT` |
| `FRACTAL_CELL` | `FRACTAL_CHILD / fractal_runtime_v02 / (CAP_FRACTAL_CHILD) / CHILD_SLOT` |
| `FRACTAL_MERGE` | `LOCAL_DETERMINISTIC / fractal_runtime_v02 / (CAP_RUNTIME) / CURRENT` |
| `POST_VV` | `VALIDATOR / post_vv_v01 / (CAP_POST_VV) / CURRENT` |
| `GT_ADVISORY` | `ADVISORY / gt_validator_v01 / (CAP_GT) / CURRENT` |
| `PARENT_RETURN` | `PARENT_RETURN / parent_return_v02 / (CAP_PARENT_RETURN) / CURRENT` |

The resulting five exact ordered assignment tables are:

| Mode | Exact `(canonical_index,node_index,assignment/component/caps/binding)` rows |
|---|---|
| `memory_informed` | `(0,0,LOCAL_DETERMINISTIC/fractal_runtime_v02/(CAP_RUNTIME)/CURRENT)`; `(1,1,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(2,2,VALIDATOR/post_vv_v01/(CAP_POST_VV)/CURRENT)`; `(3,3,ADVISORY/gt_validator_v01/(CAP_GT)/CURRENT)`; `(4,4,PARENT_RETURN/parent_return_v02/(CAP_PARENT_RETURN)/CURRENT)` |
| `local_slm` | `(0,0,LOCAL_MODEL_DECLARED/fractal_runtime_v02/(CAP_RUNTIME)/CURRENT)`; `(1,1,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(2,2,VALIDATOR/post_vv_v01/(CAP_POST_VV)/CURRENT)`; `(3,3,ADVISORY/gt_validator_v01/(CAP_GT)/CURRENT)`; `(4,4,PARENT_RETURN/parent_return_v02/(CAP_PARENT_RETURN)/CURRENT)` |
| `cloud_llm` | `(0,0,CLOUD_MODEL_DECLARED/fractal_runtime_v02/(CAP_RUNTIME)/CURRENT)`; `(1,1,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(2,2,VALIDATOR/post_vv_v01/(CAP_POST_VV)/CURRENT)`; `(3,3,ADVISORY/gt_validator_v01/(CAP_GT)/CURRENT)`; `(4,4,PARENT_RETURN/parent_return_v02/(CAP_PARENT_RETURN)/CURRENT)` |
| `full_semantic` | `(0,0,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(1,1,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(2,2,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(3,3,LOCAL_DETERMINISTIC/fractal_runtime_v02/(CAP_RUNTIME)/CURRENT)`; `(4,4,VALIDATOR/post_vv_v01/(CAP_POST_VV)/CURRENT)`; `(5,5,ADVISORY/gt_validator_v01/(CAP_GT)/CURRENT)`; `(6,6,PARENT_RETURN/parent_return_v02/(CAP_PARENT_RETURN)/CURRENT)` |
| `full_fractal` | `(0,0,SEMANTIC_ACTOR/fractal_runtime_v02/SRC_CAPS/CURRENT)`; `(1,1,FRACTAL_CHILD/fractal_runtime_v02/(CAP_FRACTAL_CHILD)/CHILD_SLOT)`; `(2,2,FRACTAL_CHILD/fractal_runtime_v02/(CAP_FRACTAL_CHILD)/CHILD_SLOT)`; `(3,3,LOCAL_DETERMINISTIC/fractal_runtime_v02/(CAP_RUNTIME)/CURRENT)`; `(4,4,VALIDATOR/post_vv_v01/(CAP_POST_VV)/CURRENT)`; `(5,5,ADVISORY/gt_validator_v01/(CAP_GT)/CURRENT)`; `(6,6,PARENT_RETURN/parent_return_v02/(CAP_PARENT_RETURN)/CURRENT)` |

For every assignment row provider/network/connector/authority/permission/effect
booleans are `false`; `root_review_required=true` and
`real_world_effects_count=0`. Canonical assignment index equals node index and
its trace is exactly `(topology_seed_id,node_id,
canonical_index_as_decimal_text,executor_component_id)`. Index and trace are
derived, not caller authority; mismatch is `g2d_assignment_trace_invalid`.

`CHILD_SLOT_INDEX_ROWS_V02` is the sole bridge between one-based human/template
slot labels and zero-based runtime identity/allocation indexes. Its columns and
two exact rows are:

```text
(node_index,input_ref_derivation_class,human_slot_ordinal,tuple_position,canonical_child_index)
(1,PREDECESSOR_AND_CHILD_SLOT_1,1,0,0)
(2,PREDECESSOR_AND_CHILD_SLOT_2,2,1,1)
```

`SLOT_1`, human slot ordinal 1, and node index 1 identify tuple position 0 and
canonical child index 0. `SLOT_2`, human slot ordinal 2, and node index 2
identify tuple position 1 and canonical child index 1.
`FAN_IN_CHILD_SLOT_RETURNS_1_2` consumes the two terminal parent-slot returns at
tuple positions 0 then 1. Those slot returns may bind zero, one, or two actual
child results according to their mutually exclusive completion branches.
Child-ID derivation, quotient/remainder allocation, activation, scope
projection, partial-failure order, result postorder, merge input order, and
causal rows use only these frozen rows. Implementations do not infer this
bridge by subtracting one from arbitrary labels. One-based labels are never
passed as `canonical_child_index`; zero-based indexes are never rendered as
human slot ordinals. Mismatch uses existing
`g2d_child_slot_activation_invalid` or
`g2d_node_instance_geometry_invalid` as applicable.

`CELL_NODE_PROJECTION_ROWS_V02` is exact:

| Mode / cell class | Depth | Node indexes | Requested children | Child IDs |
|---|---:|---|---:|---|
| each non-fractal root | 0 | complete five-node mode tuple | 0 | `()` |
| `full_semantic` root | 0 | `(0,1,2,3,4,5,6)` | 0 | `()` |
| `full_fractal` root | 0 | `(0,1,2,3,4,5,6)` | 2 | human slot ordinal 1 -> tuple position/canonical index 0 ID; human slot ordinal 2 -> tuple position/canonical index 1 ID |
| `full_fractal` reference child human slot ordinal 1 / canonical index 0 | 1 | `(0,4,5,6)` = `SEMANTIC_ACTOR,POST_VV,GT_ADVISORY,PARENT_RETURN` | 0 | `()` |
| `full_fractal` reference child human slot ordinal 2 / canonical index 1 | 1 | `(0,4,5,6)` = same leaf projection | 0 | `()` |
| structurally admitted depth-2 leaf | 2 | `(0,4,5,6)` = same leaf projection | 0 | `()` |

`CELL_EDGE_PROJECTION_ROWS_V02` is exact:

| Mode / cell class | Edge indexes |
|---|---|
| `memory_informed` root | `(0,1,2,3)` |
| `local_slm` root | `(0,1,2,3)` |
| `cloud_llm` root | `(0,1,2,3)` |
| `full_semantic` root | `(0,1,2,3,4,5)` |
| `full_fractal` root | `(0,1,2,3,4,5,6)` |
| `full_fractal` reference child human slot ordinal 1 / canonical index 0 | `(7,8,9)` |
| `full_fractal` reference child human slot ordinal 2 / canonical index 1 | `(7,8,9)` |
| structurally admitted depth-2 leaf | `(7,8,9)` |

Within a concrete cell, readiness uses only its exact edge projection. The
leaf path is `SEMANTIC_ACTOR -> POST_VV -> GT_ADVISORY -> PARENT_RETURN`;
`FRACTAL_MERGE` is root-only. Cross-cell activation is the Section 12
parent-slot handshake, not an implicit edge. Leaf node 0 does not become
READY merely because no leaf edge enters it. No edge is invented after
topology construction.

No implicit projection exists. Missing, extra, reordered, or substituted node,
edge, assignment, or projection rows fail closed. Memory remains context only.
For each cell input, `required_output_kinds` is the expected-output tuple of
its required projected nodes in node order and `forbidden_output_kinds` is the
complete ten-value forbidden tuple without reordering.
The complete 21-cell tree remains an isolated structural identity and budget
ceiling matrix; D5's reference topology executes only cells backed by exact
slot/projection rows. Local/cloud declarations perform zero model/provider calls in the reference
proof. `full_semantic` is non-recursive. Only `full_fractal` may request
children, and missing its exact inherited G2-C capability fails closed.

## 12. Queue and Cell State Machine

The queue is explicit; Python recursion is not the scheduler. Legal state
transitions are exactly:

```text
PENDING -> PENDING      BACKPRESSURE_DEFERRED
PENDING -> READY        DEPENDENCIES_SATISFIED
READY -> RUNNING        LOCAL_ASSIGNMENT_STARTED
RUNNING -> VALIDATING   LOCAL_RESULT_AVAILABLE
VALIDATING -> READY     BOUNDED_REVISE
VALIDATING -> COMPLETED VALIDATED_COMPLETE
VALIDATING -> DEGRADED  VALIDATED_PARTIAL
VALIDATING -> BLOCKED   REQUIRED_FAILURE
VALIDATING -> NEEDS_USER RESOLVABLE_INPUT_MISSING
VALIDATING -> DEADEND   NO_PROGRESS_OR_NONRESOLVABLE
```

Unknown transitions fail closed. Terminal states never re-enter `READY`.
Caller-supplied state is rejected; state is derived from prior state, exact
guards, budget, dependencies, and observations.

`NODE_WORK_QUEUE_V02` means one immutable queue chain per instantiated node,
not one queue per topology or cell. Every projected node has one initial
`PENDING` snapshot with `predecessor_queue_entry_id=None`; every successor
names the exact immediate predecessor from the same topology, cell, node,
scope, and budget lineage. Queue artifacts use exactly the six parent forms
frozen below: root initial, child initial, ordinary root successor, ordinary
child successor, invoked-child parent FRACTAL_CELL t06 return, and invoked-child
parent FRACTAL_CELL t08-t12 terminal mapping. The no-child gate branch uses the
ordinary successor form. Contextual validation rejects gaps, skips, forks,
reorder, foreign entries, cross-node or cross-cell predecessors, cycles, or
wrong root/child/successor/result-parent nullability. A state label alone has
no authority. Every initial snapshot carries its exact t02 semantic decision
ID; every successor carries its exact t03-t12 semantic decision ID. No queue
snapshot has an absent or caller-selected Transition decision.

Queue construction receives the typed activation parent directly. Root initial
entries require `parent_cell_id=None`, `predecessor=None`, and
`activation_parent_artifact=None`. Child initial entries require the exact
parent cell, `predecessor=None`, and the validated RUNNING parent child-slot
`KernelArtifactV01`. Ordinary root and child successors require their exact
immediate predecessor, `activation_parent_artifact=None`, and
`local_child_result_artifact=None`; a child successor inherits the
activation-parent artifact ID from predecessor lineage and cannot replace it.
Invoked-child parent FRACTAL_CELL t06 and t08-t12 successors require the exact
local child result and artifact, use no activation-parent argument, and preserve
that result artifact through validating and terminal lineage. No-child gate
t06/t10-t12 successors use the ordinary root/child successor shape with both
child-result inputs absent and preserve their exact queue reasons/evidence.

The four exact `lineage_refs` shapes are:

```text
root initial =
  topology_id, topology_seed_id, cell_id, node_id,
  cell_budget_id, global_budget_id

child initial =
  topology_id, topology_seed_id, cell_id, parent_cell_id, node_id,
  cell_budget_id, global_budget_id, activation_parent_artifact_id

root successor =
  topology_id, topology_seed_id, cell_id, node_id,
  cell_budget_id, global_budget_id, predecessor_queue_entry_id

child successor =
  topology_id, topology_seed_id, cell_id, parent_cell_id, node_id,
  cell_budget_id, global_budget_id, activation_parent_artifact_id,
  predecessor_queue_entry_id
```

Each fixed shape is followed by `observed_output_refs`, then
`observed_evidence_refs`, then `advisory_refs`, preserving field order. No
optional-position sentinel or lexical resort exists. Queue object lineage and
artifact parents are validated jointly: a missing or substituted child
activation parent, a root initial activation parent, a successor-supplied
activation parent, or lost/changed inherited child lineage fails closed. For a
parent FRACTAL_CELL t06 VALIDATING entry, the exact child result artifact ID is
inserted after predecessor lineage and before the observation tuples. Its
t08-t12 terminal successor preserves that same child result artifact ID in
lineage and `observed_output_refs`.

The queue entry binds `topology_id`, `topology_seed_id`, concrete `cell_id`,
`parent_cell_id`, template `node_id`, `cell_depth`, concrete `scope_ref`, and
both the cell-local and topology-global budget snapshots current for that
state. Non-fractal nodes have
`planned_child_cell_id=None`; a `FRACTAL_CELL` child-slot instance carries its
exact pre-admission planned child ID. Different cells may instantiate the same node template
but may never share a queue entry ID. One cell input names all initial and all
required queue entries for that cell; one cell result names all required
terminal snapshots. Missing terminal nodes, extra queue chains, duplicate node
instances, or queue/cell/node substitution fail closed.

Planning precedes instantiation. After allowed t01 and topology-artifact
validation, the full-fractal root derives exactly two equal-scope planned child
IDs for canonical indexes 0 and 1. Its input records
`requested_child_count=2` and those IDs in
`ordered_planned_child_cell_ids`; its two child-slot initial snapshots carry
the matching `planned_child_cell_id`. Every other snapshot carries `None`.
An admitted future NARROWER structural case still requires membership in both
source and policy narrowing tuples. A planned ID is not a cell instance,
allocation, projection, input, result, or proof that work ran.

The instantiation order initially contains only the root. A RUNNING slot first
undergoes an internal deterministic precheck over its exact artifact, planned
ID, slot, parent input/scope, monotonic capabilities and prohibitions,
derivable allocation, latest parent-local and global capacity, leaf projection, and failure/input
state. The precheck constructs no child object. After PASS, the runtime builds
and contextually validates the child ALLOCATED budget and scope-projection
candidates, then paired ACTIVATE successors. Activation commits only after all
three validate. Paired CELL_CREATE successors then debit the same planned ID
once. Only accepted CELL_CREATE appends it by parent preorder and slot and
permits child t02 admission, queues, input, execution, result, cell count, and
activation causal row. A structurally valid denied precheck creates none of
those child objects and instead takes the exact no-child t06/t10-t12 parent-slot
return with bounded evidence and queue reasons. Malformed precheck geometry or
an unexpected candidate failure returns FAIL_CLOSED, creates no terminal slot,
and cannot enter an accepted bundle. Node scheduling uses deterministic
dependency order plus this handshake; result construction uses a separate
postorder axis.

For every cell, projected nodes follow `CELL_NODE_PROJECTION_ROWS_V02`.
`node_instance_sequence` is the zero-based ordinal over cell instantiation
order and then projected-node order. Initial `snapshot_sequence=0`; each
same-node successor increments it by exactly one. Initial
`admission_round=0`. Each scheduler round freezes one explicit round number,
the latest accepted queue occurrence per instantiated node at round start, and
the deterministic candidate order. Every node receives at most one transition
occurrence in that round. Each individual decision uses its own latest settled
immutable pre-state after every earlier accepted occurrence in the same round;
a later decision may observe settled earlier queue/budget successors but never
future state. `round_start_queue_entries` is the immutable round-start tuple;
the explicit current entry and latest global budget carry same-round progress.
A candidate whose turn passed before its dependency became terminal waits for
the next round. No caller supplies sequence or round. Queue continuity binds
topology, cell, node, projection class, budgets, scope, predecessor, snapshot,
round, and exact Transition decision.

Within-cell readiness uses only the exact selected edge projection. A target
is eligible for local gate evaluation only after all projected source nodes are
terminal. `DATA_DEPENDENCY` and `VALIDATION` targets consume safe complete or
degraded output or exact failure evidence. `RETURN` consumes the validated
predecessor advisory/evidence. A `PARENT_CHILD` target performs the child-slot
gate locally and invokes a child only after the complete handshake below.

The deterministic admission key is
`(canonical_priority,cell_depth,node_instance_sequence,cell_id,node_id)`.
Priorities are fixed: context/compute/fractal `0`, merge `1`, Post V&V `2`, GT
`3`, parent return `4`. Provider output, token volume, child count, majority,
consensus, and compute spend cannot affect it. `max_total_cells` counts unique
instantiated cell IDs accepted at CELL_CREATE including the root, never planned
IDs, allocations, ACTIVATE events, nodes, queues, results, or artifacts.
`max_parallelism` governs occupied admission slots, not only RUNNING work.

The exact state-class consideration order within a round is: existing READY
occurrences; RUNNING occurrences with exact local child result or activation-
gate outcome available;
VALIDATING occurrences eligible for t08-t12 terminal recording; VALIDATING
occurrences eligible for t07 bounded revise; dependency-satisfied PENDING
occurrences eligible for t04; then capacity-deferred PENDING occurrences
eligible for one later t03 state. Every class uses the admission key above.

At each decision point:

```text
running_count = latest global_budget.current_parallelism
ready_count = count(latest nonterminal queue occurrences in READY)
occupied_admission_slots = running_count + ready_count
residual_admission_slots = policy.max_parallelism - occupied_admission_slots
0 <= occupied_admission_slots <= policy.max_parallelism
```

READY is a visible logical reservation and does not mutate budget counters.
`remaining_parallel_slots=max_parallelism-current_parallelism` remains an
execution-budget mirror, not full admission residual. t04 and t07 create READY
only after one residual slot is selected. t05 consumes an existing reservation
(`ready_count -= 1`, `current_parallelism += 1`), so occupied slots do not
increase. t06 releases one RUNNING slot. No stale round-start value can admit
multiple contenders into one residual slot.

For one `FractalCellInputV02`, `initial_revise_count=0`.
`ordered_initial_queue_entry_ids` contains every projected node's initial
PENDING snapshot in projected-node order. `ordered_required_queue_entry_ids`
is the required subset in the same order; all v0.2 reference nodes are
required, so the tuples are equal. No successor snapshot appears in either.
All root PENDING snapshots and t02 artifacts are built before the root input;
the root input validates before any root PENDING -> READY transition.

A full-fractal child slot can enter READY only after its projected parent
dependency is terminal and its parent cell input is valid. READY -> RUNNING
starts a local child-admission gate, not proof that a child ran. The precheck
requires the exact RUNNING parent-slot artifact, planned child ID and slot
relation, admissible output/evidence, derivable scope and allocation, leaf
projection, absence of hard failure, no resolvable missing input, and inherited
G2-C Root commit. It never requires not-yet-built child scope or budget
objects. Those candidates are built and validated before ACTIVATE/CELL_CREATE
commit. The child initial PENDING family and input are built only after commit,
in projected-node order, with exact parent-slot artifact, evidence, scope,
budgets, and source lineage before child node 0 can become READY. No incoming
leaf edge is needed, but absence of an edge is never activation authority. A
failed gate completes the parent slot's deterministic blocked, needs-user, or
deadend evaluation without child invocation; invocation count remains zero.

The evaluator uses immutable pre-state only. For t02, source is the topology
artifact, `current_entry=None`, `cell_input=None`, dependencies are empty, and
all optional observation/child/validation/revise/backpressure inputs are
absent or empty exactly as specified below. One t02 decision exists per
projected node and admission receives those decisions explicitly. For t03-t12,
source is the current queue artifact and every duplicated scalar must equal the
current entry. An ordinary unsatisfied dependency returns `None` and creates
no successor object.

Observation and reason state are exact. Every initial PENDING entry and every
t03 PENDING, t04 READY, and t05 RUNNING target has
`observed_output_refs=observed_evidence_refs=advisory_refs=()`. t06 is the sole
rule that introduces one attempt's observation tuples. t07 clears all three
observation tuples and `queue_reason_codes` to `()` while predecessor history
retains the rejected attempt. t08-t12 copy the VALIDATING observation and
reason families without sorting or substitution, subject only to exact
terminal-state reason derivation. No PENDING, READY, or RUNNING entry carries
future result refs, and no terminal entry uses stale refs or reasons from a
prior revised attempt.

`queue_reason_codes` is an identity-bearing tuple of public G2-D reasons only.
It is an explicit composition input to the structural queue builder, evaluator,
and queue-advance surface, but the runtime derives it from immutable pre-state
and exact typed local facts; the evaluator and contextual validator reconstruct
the same tuple independently. It is never external caller authority, a
free-form label, caller PASS, or a source-reason laundering surface. Its exact
state law is:

```text
t02 initial PENDING = ()
ordinary dependency wait = no successor and no new tuple
t03 PENDING = exact bounded backpressure/defer public reasons
t04 READY = ()
t05 RUNNING = ()
t06 VALIDATING = exact current-attempt public reasons; empty on positive work;
                  child_result.reason_codes on invoked FRACTAL_CELL return;
                  exact gate reasons on no-child activation-gate return
t07 READY = ()
t08 COMPLETED = ()
t09 DEGRADED = exact public degradation reasons
t10 BLOCKED = exact public hard-failure reasons
t11 NEEDS_USER = exact public resolvable-input reasons
t12 DEADEND = exact public no-progress or non-resolvable reasons
```

Source-owned reasons remain only in their source objects and later source-
reason tuples. The queue field remains a public-reason projection and cannot
manufacture, reorder, omit, duplicate, or relabel a reason.

`PARENT_RETURN_TYPED_INPUT_COMPONENTS_V02` is the exact internal component
tuple, in semantic order:

```text
(
  parent_return_pre_post_vv_terminal_queue_entries,
  parent_return_child_results,
  parent_return_partial_failures,
  parent_return_result_proposal,
  parent_return_post_vv_report,
  parent_return_gt_advisory_report,
  parent_return_validation_reports
)
```

It adds no type or public function. `QUEUE_TRANSITION_INPUT_ROWS_V02` has
exactly these eleven columns and eleven rows. `ABSENT` here is an input-mode
token only, never a queue-lineage or causal sentinel. The local-child mode
governs both the result and its artifact.

| rule_id | current_entry_mode | cell_input_mode | dependency_mode | target_observation_mode | target_queue_reason_mode | local_child_result_mode | validation_report_mode | revise_observation_mode | backpressure_mode | parent_return_family_mode |
|---|---|---|---|---|---|---|---|---|---|---|
| `t02` | `ABSENT` | `ABSENT` | `EMPTY` | `EMPTY` | `EMPTY` | `ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` |
| `t03` | `PENDING` | `REQUIRED` | `SATISFIED` | `EMPTY` | `BACKPRESSURE_DERIVED` | `ABSENT` | `ABSENT` | `ABSENT` | `REQUIRED` | `ABSENT` |
| `t04` | `PENDING` | `REQUIRED` | `SATISFIED` | `EMPTY` | `EMPTY` | `ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` |
| `t05` | `READY` | `REQUIRED` | `CURRENT_EXACT` | `EMPTY` | `EMPTY` | `ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` |
| `t06` | `RUNNING` | `REQUIRED` | `CURRENT_EXACT` | `NEW_ATTEMPT_OBSERVATION` | `NEW_ATTEMPT_DERIVED` | `RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL_ELSE_ABSENT` | `ABSENT` | `ABSENT` | `ABSENT` | `REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT` |
| `t07` | `VALIDATING` | `REQUIRED` | `CURRENT_EXACT` | `CLEAR_TO_EMPTY` | `CLEAR_TO_EMPTY` | `ABSENT` | `REVISE_OBSERVATION_STRUCTURAL_REPORT` | `REQUIRED` | `ABSENT` | `ABSENT` |
| `t08` | `VALIDATING` | `REQUIRED` | `CURRENT_EXACT` | `COPY_VALIDATING_OBSERVATION` | `COPY_VALIDATING_REASONS` | `REQUIRED_RESULT_IF_FRACTAL_CELL` | `NODE_KIND_EXACT_OR_ABSENT` | `ABSENT` | `ABSENT` | `REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT` |
| `t09` | `VALIDATING` | `REQUIRED` | `CURRENT_EXACT` | `COPY_VALIDATING_OBSERVATION` | `COPY_VALIDATING_REASONS` | `REQUIRED_RESULT_IF_FRACTAL_CELL` | `NODE_KIND_EXACT_OR_ABSENT` | `ABSENT` | `ABSENT` | `REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT` |
| `t10` | `VALIDATING` | `REQUIRED` | `CURRENT_EXACT` | `COPY_VALIDATING_OBSERVATION` | `COPY_VALIDATING_REASONS` | `RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL` | `NODE_KIND_EXACT_OR_GATE_TERMINAL` | `ABSENT` | `ABSENT` | `REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT` |
| `t11` | `VALIDATING` | `REQUIRED` | `CURRENT_EXACT` | `COPY_VALIDATING_OBSERVATION` | `COPY_VALIDATING_REASONS` | `RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL` | `NODE_KIND_EXACT_OR_GATE_TERMINAL` | `ABSENT` | `ABSENT` | `REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT` |
| `t12` | `VALIDATING` | `REQUIRED` | `CURRENT_EXACT` | `COPY_VALIDATING_OBSERVATION` | `COPY_VALIDATING_REASONS` | `RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL` | `NODE_KIND_EXACT_OR_GATE_OR_REVISE_TERMINAL` | `REQUIRED_IFF_REVISE_NO_PROGRESS_BRANCH_ELSE_ABSENT` | `ABSENT` | `REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT` |

For every non-PARENT_RETURN node the exact nullability is:

```text
parent_return_pre_post_vv_terminal_queue_entries=()
parent_return_child_results=()
parent_return_partial_failures=()
parent_return_result_proposal=None
parent_return_post_vv_report=None
parent_return_gt_advisory_report=None
parent_return_validation_reports=()
```

Any nonempty or non-null component on a non-PARENT_RETURN node fails closed.
PARENT_RETURN t06 and t08-t12 require the complete actual family. Its report
tuple is exactly, in order:

```text
(
  exact RESULT_PROPOSAL PASS report,
  exact POST_VV_REPORT PASS report,
  exact GT_ADVISORY_REPORT PASS report
)
```

Each report has `status=PASS`, `failure_stage=NONE`, the named exact validation
target, and `validated_object_id` equal respectively to proposal ID, VV report
ID, and GT report ID. The evaluator independently reruns the existing
contextual validators against the supplied actual family and requires
canonical-byte equality with this tuple; copied PASS is never authority.

```text
RESULT_PROPOSAL report:
  validation_target=RESULT_PROPOSAL
  status=PASS
  failure_stage=NONE
  validated_object_id=parent_return_result_proposal["proposal_id"]
POST_VV_REPORT report:
  validation_target=POST_VV_REPORT
  status=PASS
  failure_stage=NONE
  validated_object_id=parent_return_post_vv_report["vv_report_id"]
GT_ADVISORY_REPORT report:
  validation_target=GT_ADVISORY_REPORT
  status=PASS
  failure_stage=NONE
  validated_object_id=parent_return_gt_advisory_report["gt_report_id"]
```

The proposal is an exact built-in, recursively JSON-safe, schema-valid,
content-addressed dictionary. Its request, vector, plan, ordered actual child-
result IDs, and partial-failure IDs bind exactly to source request, cell,
topology, and the supplied typed tuples. The supplied pre-Post-V&V terminal
tuple is the exact proposal-validation family. The VV report binds proposal ID
and source KT; the GT advisory derives from exactly that one VV report and
obeys the explicit-time ID/created-at law. All three dictionaries are retained
in the bundle. Foreign, copied, reordered, duplicated, or substituted material
fails closed.

PARENT_RETURN status is read only from
`parent_return_result_proposal["result_payload"]["status"]` and is exactly one
of `completed`, `degraded`, `blocked`, `needs_user`, or `deadend`. The evaluator
rederives the proposal-ID output tuple, proposal evidence IDs in proposal
order, VV/GT advisory tuple, and exact public candidate reasons from the actual
family, requires equality with the supplied observation/reason parameters, and
then uses only `PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02`. Substitution of any
proposal, report, validation report, status, ID, time, evidence, typed child or
failure tuple, pre-terminal tuple, order, or reason returns no Transition
decision. The runtime emits the first FAIL_CLOSED report at RESULT_PROPOSAL,
POST_VV, GT, QUEUE, or TRANSITION and builds no dependent queue artifact or
accepted bundle.

FRACTAL_CELL has exactly two mutually exclusive completion branches.
`INVOKED_CHILD_RESULT_RETURN` requires accepted child CELL_CREATE, the complete
child runtime, and exact mutually bound `FractalCellResultV02` and result
artifact. t08/t09 always use this branch. t10/t11/t12 may use it only when the
child outcome maps exactly under `CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02`.

`NO_CHILD_ACTIVATION_GATE_TERMINAL` is legal only before accepted child
CELL_CREATE. The exact RUNNING parent slot exists, but no child budget,
projection, queue, input, result, partial-failure record, cell debit, activation
causal row, child-return causal row, or child ABI artifact exists. t06 releases
the parent-slot RUNNING reservation with both local child inputs absent, then
exactly one of t10/t11/t12 records the gate outcome. t07/t08/t09 are forbidden.
Its t12 uses `revise_observation=None`; only the separate bounded-revise no-
progress t12 requires the revise observation.

`CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02` is exact:

```text
VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL
  -> t06 -> t10 -> parent slot BLOCKED
RESOLVABLE_INPUT_MISSING
  -> t06 -> t11 -> parent slot NEEDS_USER
NO_PROGRESS_OR_NONRESOLVABLE
  -> t06 -> t12 -> parent slot DEADEND
```

No no-child COMPLETED or DEGRADED row exists. The t06 guard is exactly
`local_result_or_activation_gate_outcome_available` and is true iff one branch
validates. On the no-child branch, output and advisory tuples are empty;
evidence is the exact bounded parent/source precheck evidence in semantic
order; queue reasons are the exact derived gate reasons in public-registry
order. The precheck is recomputed from source context, parent input and slot
artifact, policy, immutable parent allocation basis, latest parent/global
budgets, scope/capability/forbidden facts, planned ID, canonical slot, and leaf
projection.

A valid no-child BLOCKED terminal first proves the complete source context and
RouteEligibility family; current RUNNING parent-slot queue object/artifact;
topology, node, assignment, parent input, policy, scope, planned ID and exact
slot; allocation basis and latest parent/global budgets; and every identity,
hash, predecessor, artifact parent, lineage, state, event, counter, field type,
and ordering relation. Only then may a validated hard policy prohibition,
forbidden authority claim, structurally valid non-admissible scope relation, or
structurally valid budget ceiling/capacity exhaustion derive
`VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL` and t06/t10 BLOCKED.

Type/scalar invalidity; identity/hash mismatch; forged or foreign source,
current, or parent artifact; wrong predecessor or ABI parent; broken lineage;
invalid planned ID or slot/index mapping; invalid topology/node/assignment
relation; malformed scope projection; invalid budget owner, scope, state,
event, event ref, predecessor, pairing, counter, debit, remaining value, or
arithmetic; copied PASS or reason; reason laundering; duplicate/reorder; and an
impossible optional-input combination are structural/contextual corruption.
They never normalize into an accepted slot terminal: no t06/t10 decision,
VALIDATING or terminal successor, merge input, `CELL_TERMINAL_OUTCOME` row, or
accepted bundle is built. The runtime returns the exact first FAIL_CLOSED
report. Structurally valid resolvable input remains NEEDS_USER, valid no-
progress/nonresolvable input remains DEADEND, and valid policy/scope/authority/
budget denial remains BLOCKED.

For POST_VV, child inputs are absent and the report is the exact POST_VV_REPORT
contextual report matching the observed VV report ID. For GT_ADVISORY, child
inputs are absent and the report is the exact GT_ADVISORY_REPORT contextual
report matching the observed GT report ID. All other non-FRACTAL_CELL node
outcomes derive from exact deterministic observations, expected output kind,
assignment, dependencies, budgets, source context, forbidden-output law, and
zero-operation law. For every admitted t07, the report is the exact structural
FractalReviseObservationV02 PASS report for the supplied observation. The
evaluator and queue advance receive identical target reason and observation
tuples; mismatch fails closed. No caller selects a guard, state, outcome, PASS,
terminal result, or activation-gate disposition.

The acyclic successor order is current entry/artifact, optional pre-decision
validation/revise/backpressure object, Transition decision, required budget
successors, target snapshot, target artifact, and contextual source/target
binding. Root admission has no parent-slot artifact and requires allowed t01;
child admission requires the exact RUNNING parent-slot artifact and activated
planned ID. No provisional target, post-hoc decision, or fixed point exists.

For `INVOKED_CHILD_RESULT_RETURN`, all required child nodes become terminal;
the exact pre-Post-V&V prefix builds ResultProposal, then Post V&V and GT run,
PARENT_RETURN terminates, complete-terminal pre-result validation runs, and the
child result/artifact are built and validated. The parent FRACTAL_CELL slot
remains RUNNING until that artifact exists. t06 receives both actual objects,
derives `local_result_or_activation_gate_outcome_available`, and creates a
VALIDATING target with:

```text
observed_output_refs=(child_result_artifact.artifact_id,)
observed_evidence_refs=child_result.evidence_refs
advisory_refs=(child_result.post_vv_report_ref,child_result.gt_advisory_ref)
queue_reason_codes=child_result.reason_codes
```

`CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02` is exact:

```text
COMPLETED  -> t06 -> t08 -> parent slot COMPLETED
DEGRADED   -> t06 -> t09 -> parent slot DEGRADED
BLOCKED    -> t06 -> t10 -> parent slot BLOCKED
NEEDS_USER -> t06 -> t11 -> parent slot NEEDS_USER
DEADEND    -> t06 -> t12 -> parent slot DEADEND
```

t08-t12 copy those observation tuples and the exact validating reason surface
unchanged. t07 is forbidden for a
FRACTAL_CELL parent slot after its child result exists because the child has
already completed its own bounded revisions. Only after both parent child
slots are terminal may FRACTAL_MERGE become READY.

`FAN_IN_CHILD_SLOT_RETURNS_1_2` normalizes merge input over those two terminal
parent-slot queue objects/artifacts in human slot ordinal order 1 then 2,
mapped to tuple positions/canonical indexes 0 then 1. For each slot the merge
reads exact `planned_child_cell_id`, `state`, `queue_reason_codes`,
`observed_output_refs`, `observed_evidence_refs`, `advisory_refs`, predecessor
lineage, and optional child-result-parent lineage from the terminal queue
object/artifact. An invoked slot's first output is its exact child-result
artifact ID and the typed result family must contain that result. A no-child
gate slot has empty outputs/advisories, no child result/artifact/failure record,
and carries its bounded disposition in terminal state, queue reasons, and
evidence. Both slot returns always exist;
zero, one, or two actual child results may exist. Merge preserves safe sibling
evidence and cannot upgrade BLOCKED, NEEDS_USER, or DEADEND facts.

`ordered_child_result_ids` contains actual built direct-child results only, in
slot order, omitting no-child slots. Partial failures likewise name actual
child results only. Every required slot remains represented by its terminal
queue entry in `ordered_terminal_queue_entry_ids`. A synthetic uninstantiated
child result or failure record is forbidden. Slot substitution, missing slot,
foreign result, result without slot, reordered slot, duplicate result, or
hidden no-child success fails closed. Report cell counts include instantiated
cell results only. Parent outcome and evidence derive from both terminal slot
returns together with every actual child result and actual failure record.

For every non-FRACTAL_CELL node, `local_child_result` and
`local_child_result_artifact` are `None`. Before invoked-child return both are
also `None` for FRACTAL_CELL. The invoked branch supplies both exact objects for
t06 and t08-t12; the no-child branch supplies neither for t06 and t10-t12. No
mixed branch is legal. No child result artifact can bind the other slot,
topology, parent, planned ID, scope, or result-postorder position.

The complete six queue artifact parent forms are:

```text
1 root initial = (topology_artifact_id)
2 child initial = (topology_artifact_id,RUNNING_parent_slot_artifact_id)
3 ordinary root successor =
    (topology_artifact_id,predecessor_queue_artifact_id)
4 ordinary child successor =
    (topology_artifact_id,predecessor_queue_artifact_id)
5 parent FRACTAL_CELL t06 VALIDATING successor =
    (topology_artifact_id,RUNNING_parent_slot_predecessor_artifact_id,
     exact_child_result_artifact_id)
6 parent FRACTAL_CELL t08-t12 terminal successor =
    (topology_artifact_id,VALIDATING_parent_slot_predecessor_artifact_id,
     exact_same_child_result_artifact_id)
```

Form 2 alone uses `activation_parent_artifact` and no local child result.
Forms 5 and 6 use `local_child_result_artifact` and no activation parent for the
invoked branch. The no-child branch uses ordinary successor form 3 when the
containing parent cell is root and form 4 when it is a child; it has no local
child-result parent. All other forms use neither. Every successor predecessor
is exact; no projection uses both optional parents, and no non-FRACTAL_CELL
projection uses a local child-result parent. The source dataclass remains 31
fields; this relationship is APR plus queue lineage/context, not a new source
field.

One append-only queue execution-build log records accepted occurrence order.
It begins with all root initial entry/artifact pairs in projected-node order.
Each accepted t03-t12 successor is appended immediately after contextual
validation. Each activated child's complete initial family is appended
immediately after accepted CELL_CREATE, in leaf projected-node order, after
the RUNNING parent-slot artifact already exists. Every later root or child
successor is appended immediately; ordinary dependency wait appends nothing.
No post-hoc sort is allowed. Bundle queue objects/artifacts, trace queue IDs and
state-decision IDs, bundle occurrence-aligned state decisions, and retained
queue reports consume that same queue-only log unchanged. The interleaved
runtime ABI artifact log separately supplies trace ABI refs, causal artifact
order, and Stage D-B.

`TransitionDecisionV01` identifies a semantic decision, not a unique runtime
occurrence. Equal t02 decisions across projected nodes and equal t03-t12
decisions across value-identical occurrences are legal. A queue occurrence is
identified by its target entry/artifact, predecessor, cell, node, cell/global
budgets, snapshot sequence, and admission round. Runtime trace
`state_transition_decision_ids` contains one decision ID per created queue
entry in queue build-log order and permits repeated IDs.
`transition_refs` is t01, then that complete occurrence-aligned tuple, then the
one root parent-return decision. The execution bundle's exact Transition
object tuple is the t01 decision object, then one semantic state-decision
object per created queue entry in queue build-log order, then the one t13-t17
root parent-return decision object. It permits repeated value-identical objects
and decision IDs across distinct queue occurrences. Ordinary dependency wait
creates no occurrence and adds no item. Budget identities remain occurrence-
unique through policy, seed, cell,
allocation parent, predecessor, scope/state, event kind/ref, and exact
counters even when event refs reuse one semantic decision ID. Object,
artifact, queue, result, scope, and budget identities remain unique where their
own contracts require uniqueness. Causal rows have no identity field and are
deduplicated only by complete canonical plain content; no universal semantic
decision-ID deduplication rule exists.

For each cell, upstream context, compute, merge, or child-slot paths execute
first. `pre_post_vv_terminal_queue_entries` is then frozen as all and only
required projected nodes with canonical index strictly before POST_VV, each at
its exact latest t08-t12 terminal occurrence and in projected-node order. It
excludes POST_VV, GT_ADVISORY, and PARENT_RETURN and accepts no nonterminal,
future, foreign, duplicate, missing, or reordered occurrence. The full-fractal
root tuple is root SEMANTIC_ACTOR, human slot 1 return, human slot 2 return,
FRACTAL_MERGE; a leaf tuple is its SEMANTIC_ACTOR; full-semantic contains its
three actors then SEMANTIC_MERGE.

One canonical ResultProposal is built from that exact prefix plus actual typed
child results/failures, then Post V&V runs once and GT runs once. PARENT_RETURN
receives the complete actual typed family and exact independently reconstructed
three-report tuple through signature 90. It derives and requires this exact
observation:

```text
observed_output_refs=(parent_return_result_proposal["proposal_id"],)
observed_evidence_refs=exact proposal evidence ref IDs in proposal order
advisory_refs=(parent_return_post_vv_report["vv_report_id"],
               parent_return_gt_advisory_report["gt_report_id"])
queue_reason_codes=exact derived candidate public reasons
```

`PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02` is exact:

```text
proposal status completed  -> t06 -> t08 -> PARENT_RETURN COMPLETED
proposal status degraded   -> t06 -> t09 -> PARENT_RETURN DEGRADED
proposal status blocked    -> t06 -> t10 -> PARENT_RETURN BLOCKED
proposal status needs_user -> t06 -> t11 -> PARENT_RETURN NEEDS_USER
proposal status deadend    -> t06 -> t12 -> PARENT_RETURN DEADEND
```

Status is read only from the actual proposal's `result_payload.status`. Post
V&V and GT may reject or request revise advisory treatment but cannot upgrade
the hard derived proposal status. Structural proposal, Post V&V, GT, report-
reconstruction, or family-binding failure is FAIL_CLOSED and produces no
Transition decision, terminal queue, or result. After PARENT_RETURN terminality and unique
completion budgets, signatures 57 and 99 receive the complete
`terminal_queue_entries` tuple containing every required projected node in
projected-node order. This is the exact complete terminal tuple and is distinct
from `pre_post_vv_terminal_queue_entries`. Pre-result validation proves the proposal prefix, exact
proposal/VV/GT/PARENT_RETURN linkage, complete terminality, completion budgets,
and actual-only child-result/failure cardinality before the cell result is
built. Revisions never replace `FractalCellInputV02`; revise observations,
queue snapshots, and budget successors carry revision state.

t08-t12 derive and record `NODE_TERMINAL_OUTCOMES`, not a future cell outcome.
Their support facts are exactly `node_degraded_basis_valid`,
`node_hard_failure_valid`, `node_resolvable_input_missing`, and
`node_no_progress_or_nonresolvable` as applicable. A successfully invoked Post
V&V or GT node is `COMPLETED` even if its advisory content requests revise or
no-update. The cell outcome is derived later from all node terminal states and
queue reasons, actual ordered child results and failures, Post V&V/GT content,
and terminal precedence.

There is exactly one root cell per topology. Non-fractal modes produce one root
result and no child result. The canonical positive full-fractal profile
produces the human slot ordinal 1 / canonical index 0 result, then human slot
ordinal 2 / canonical index 1 result, then the root result. A failure case may
produce zero or one child result while still producing both parent-slot
terminal returns. Every built cell result has the
fixed literal `parent_return_required=true`; false is structurally invalid.
For a child this requires upward return through its parent slot and parent
aggregation. For the root it requires the one t13-t17 runtime-report return
toward Root. The flag never permits a child to call t13-t17. Only the root
result may drive a runtime report and parent-return Transition. Child results
enter parent aggregation through their parent-slot queue return, ordered
child-result IDs, and exact cross-artifact causal refs; they never directly
invoke Root or create a report.

## 13. Bounds, Budget Propagation, and Parent/Child Scope

The reference policy ceilings are exact:

```text
max_depth=3
max_fan_out=4
max_total_cells=21
max_parallelism=4
max_revise_count=2
max_consecutive_no_progress=2
max_wall_time_units=1000
max_token_budget=100000
max_provider_calls=0
```

Root cell depth is `0`; valid cells satisfy `0 <= depth < max_depth`. Child
depth is parent depth plus one, so `max_depth=3` permits only depths 0, 1, and
2. An attempted child at depth 3 is rejected. `max_total_cells=21` is the
complete `1 + 4 + 16` tree ceiling; an attempted 22nd cell is rejected. Exact
boundary tests cover depth 0, 1, 2, attempted 3, complete 21 cells, and the
attempted 22nd cell. The 21-cell boundary is an isolated structural
cell-ID/budget-allocation validation matrix; it does not add an implicit
runtime cell projection or change the two-child D5 reference topology.
Wall-time
units are injected accounting units, not elapsed clock time. Provider budget
is zero in v0.2. All counters are non-negative exact integers.

Budget snapshots form immutable cell-local and topology-global axes and append
immediately to `BUDGET_CONSTRUCTION_LOG_V02`. Allowed state evolution is only
`ALLOCATED -> ACTIVE`, `ACTIVE -> ACTIVE`, and `ACTIVE -> FINAL`; no successor
uses a FINAL predecessor and FINAL never returns to ACTIVE. Every snapshot has
one typed event and an already-built derived event ref.

The root initial budget is `ROOT_GLOBAL_AND_CELL`, owned by
`topology_seed.root_cell_id`, has no allocation parent or predecessor, is
ALLOCATED with INITIAL_ALLOCATION, and has zero consumption. Root local and
topology-global are the same object, so every root queue has
`cell_budget_id==global_budget_id`. Every later ROOT_GLOBAL_AND_CELL snapshot
keeps the root owner and `allocation_parent_budget_id=None`; a child ID,
semantic decision, or child result may be its event source without becoming
its owner.

One hierarchical allocation law controls every child. The child's
`allocation_parent_budget_id` is the immutable allocation basis of its
immediate parent cell: the exact ACTIVE CELL_CREATE budget named by
`budget_context_input.cell_budget_id`, with the same policy/seed, owned by that
parent, bound into its accepted input before any parent node runs. For a root
child that object is root/global only because root local/global is one object.
For a nested child it is the parent's CHILD_CELL_LOCAL CELL_CREATE snapshot,
never the current root/global aggregate. Every later child-local snapshot
preserves that original immediate-parent basis through a gap-free same-cell
chain. Child local parallelism counters remain zero.

All planned siblings under one parent input share the same allocation-parent
ID, parent input, planned-child tuple, requested count, accepted initial parent
queue tuple, and quotient/remainder epoch. `allocation_queue_entries` is exactly
that initial projected queue tuple in parent-node order, not latest mutable
snapshots. Shares are frozen collectively before any child runs and can never
be recomputed, borrowed, moved, reset, or widened. Activation separately checks
the latest immediate-parent local budget and latest topology-global budget for
current capacity; neither replaces the immutable allocation basis.
`ParentChildScopeProjectionV02.parent_budget_id` equals that basis.

Allocation partitions the basis's remaining cell, revise, wall-time, token,
and provider values after mandatory local reservation. It uses the exact parent
input, zero-based index from `CHILD_SLOT_INDEX_ROWS_V02`, common initial queues,
requested sibling count, integer quotient/remainder, child depth, and subtree
cap `sum(max_fan_out**i for i in range(max_depth-child_depth))`. Unallocated
units stay with the parent. The isolated four-child/21-cell matrix proves only
the structural boundary and creates no runtime projection.

Budget construction is event-complete. `budget_event_ref` is
DERIVED_FROM_TYPED_EVENT and is never a raw parameter. No optional combination
outside this matrix is accepted:

| Event / axis | Allocation parent | Predecessor | Budget context / child index / allocation queues | Transition / paired cell / child result | State; owner; event ref |
|---|---|---|---|---|---|
| root `INITIAL_ALLOCATION` | `None` | `None` | `None / None / ()` | `None / None / None` | ALLOCATED; root; root ID |
| child `INITIAL_ALLOCATION` | exact immediate-parent CELL_CREATE basis | `None` | exact parent input / exact zero-based slot / exact parent initial queues | `None / None / None` | ALLOCATED; child; child ID |
| root `ACTIVATE` | `None` | exact root predecessor | `None / None / ()` | `None / None / None` | ACTIVE; root; root ID |
| root `CELL_CREATE` | `None` | exact root ACTIVATE | `None / None / ()` | `None / None / None` | ACTIVE; root; root ID |
| child-local `ACTIVATE` or `CELL_CREATE` | preserved immediate-parent basis | exact same-child predecessor | exact parent input / exact slot / frozen parent initial queues | `None / None / None` | ACTIVE; child; child ID |
| global paired child `ACTIVATE` or `CELL_CREATE` | `None` | exact global predecessor | same parent input / same slot / same frozen queues | `None / exact child-local successor / None` | ACTIVE; root; child ID |
| root `START_NODE` or `FINISH_NODE` | `None` | exact ACTIVE root predecessor | exact root input / `None / ()` | exact t05 or t06 / `None / None` | ACTIVE; root; decision ID |
| child-local `START_NODE` or `FINISH_NODE` | preserved basis | exact ACTIVE child predecessor | exact child input / `None / ()` | exact t05 or t06 / `None / None` | ACTIVE; child; decision ID |
| global paired child `START_NODE` or `FINISH_NODE` | `None` | exact ACTIVE global predecessor | same child input / `None / ()` | same decision / exact child-local successor / `None` | ACTIVE; root; decision ID |
| root `REVISE` | `None` | exact ACTIVE root predecessor | exact root input / `None / ()` | exact t07 / `None / None` | ACTIVE; root; t07 ID |
| child-local `REVISE` | preserved basis | exact ACTIVE child predecessor | exact child input / `None / ()` | exact t07 / `None / None` | ACTIVE; child; t07 ID |
| global paired child `REVISE` | `None` | exact ACTIVE global predecessor | same child input / `None / ()` | same t07 / exact child-local successor / `None` | ACTIVE; root; t07 ID |
| root PARENT_RETURN `FINALIZE` | `None` | exact ACTIVE root predecessor | exact root input / `None / ()` | exact PARENT_RETURN t08-t12 / `None / None` | FINAL; root; decision ID |
| child-local PARENT_RETURN `FINALIZE` | preserved basis | exact ACTIVE child predecessor | exact child input / `None / ()` | exact PARENT_RETURN t08-t12 / `None / None` | FINAL; child; decision ID |
| global paired child PARENT_RETURN `FINALIZE` | `None` | exact ACTIVE global predecessor | same child input / `None / ()` | same decision / exact child-local FINAL / `None` | ACTIVE; root; decision ID |
| root/global `CHILD_AGGREGATE` | `None` | exact child completion global budget | exact parent input / exact child slot / `()` | `None / exact child-local FINAL / exact child result` | ACTIVE; root; child result ID |

INITIAL_ALLOCATION and ACTIVATE never instantiate or debit a cell. Accepted
CELL_CREATE is the sole boundary: root local/global count becomes one; child
local count becomes one; paired global count increments once. Remaining count
decreases exactly once and the planned ID enters the instantiated-cell set only
there. Failed precheck/candidate/scope/ACTIVATE/CELL_CREATE creates no accepted
debit. `max_total_cells` counts those unique accepted CELL_CREATE IDs only.

t06 always uses FINISH_NODE, releases exact parallelism, and leaves both axes
ACTIVE. t08-t12 for every non-PARENT_RETURN node creates no budget successor;
the terminal queue reuses current cell/global IDs. A cell's projected
PARENT_RETURN terminal is its sole completion boundary. Root completion creates
the unique topology-global FINAL. Child completion first creates child-local
FINAL, then paired root/global ACTIVE FINALIZE from the same decision. The child
terminal queue names that pair, and the child result is built only afterward.
Every cell has exactly one local FINAL and the topology exactly one global FINAL.

Immediately after a child result/artifact validates, CHILD_AGGREGATE creates one
identity-visible ROOT_GLOBAL_AND_CELL ACTIVE successor. Its predecessor is the
child result's exact global completion snapshot, its event ref is result ID, and
every consumption, remaining, parallelism, and ceiling counter equals the
predecessor. No event interleaves and no debit occurs. The parent FRACTAL_CELL
t06 then uses this latest post-aggregate global budget.

The deterministic debit/state table is exact:

| Event | Cell-local axis | Root/global axis |
|---|---|---|
| root INITIAL_ALLOCATION | count 0, ALLOCATED | same object |
| root ACTIVATE | count remains 0, ACTIVE | same object |
| root CELL_CREATE | count becomes 1 exactly once | same object |
| child INITIAL_ALLOCATION | count 0, ALLOCATED | no paired successor |
| child ACTIVATE | count remains 0, ACTIVE | zero cell debit, ACTIVE pair |
| child CELL_CREATE | count becomes 1 exactly once | `consumed_cell_count += 1` exactly once |
| PENDING or READY | no successor | no successor |
| START_NODE / t05 | wall-time +1 | same debit; parallelism +1 |
| FINISH_NODE / t06 | no new local consumption | parallelism -1 |
| REVISE / t07 | revise +1 and wall-time +1 | same exact debits |
| non-PARENT_RETURN t08-t12 | no successor; reuse current ID | no successor; reuse current ID |
| child PARENT_RETURN FINALIZE | state FINAL, zero counter delta | paired state ACTIVE, zero counter delta |
| root PARENT_RETURN FINALIZE | same root/global state FINAL, zero counter delta | same object |
| CHILD_AGGREGATE | child remains FINAL | ACTIVE identity successor, every counter unchanged |
| deterministic local compute | token/provider increments zero | token/provider/model/network/connector increments zero |

`canonical_child_index` exists only for child allocation,
ACTIVATE/CELL_CREATE pairs, and CHILD_AGGREGATE. Frozen allocation queues exist
only for child allocation and ACTIVATE/CELL_CREATE pairs. Transition decision
exists only for START_NODE, FINISH_NODE, REVISE, and PARENT_RETURN FINALIZE.
Paired cell budget exists only for a global child pair or CHILD_AGGREGATE;
child result exists only for CHILD_AGGREGATE. REVISE requires the already-built
observation through t07 but no after-budget ID. No raw counter, maximum,
remaining value, event ref, or unlisted optional combination is caller input.

Negative counters, over-capacity, hidden reset, double debit or aggregate,
missing release, stale global, mismatched events/pairs, invalid state skip,
wrong immediate-parent basis or predecessor, cross-cell lineage, local
parallelism authority, sibling oversubscription/borrowing, non-PARENT_RETURN
finalization, child-global FINAL, successor from FINAL, or FINAL-to-ACTIVE fails
closed.

Parent/child laws are exact:

```text
Allowed(child) is a subset of Allowed(parent)
Scope(child) is equal to or narrower than Scope(parent)
Forbidden(child) is a superset of Forbidden(parent)
TTL(child) <= TTL(parent)
ChildBudget <= RemainingParentBudget
ChildDepth = ParentDepth + 1
ChildLineage includes the exact parent
```

A child cannot widen Root-accepted scope, add a capability absent from parent
or local policy, remove an inherited hard prohibition, borrow sibling budget,
or reset any global or local ceiling. `EQUAL` is byte equality. `NARROWER`
requires membership in both source and policy permitted-narrower tuples. An
opaque new string, caller label, prefix, or suffix does not establish the
relation.

Scope lineage tuples are exact. `parent_lineage_refs` is `(topology_id,
topology_seed_id,parent_cell_id,parent_budget_id,global_budget_id,
parent_scope_ref)`. `child_lineage_refs` is that tuple followed by
`(child_cell_id,child_budget_id,child_scope_ref,
child_depth_as_decimal_text)`. `proof_refs` is
`(source_binding_id,route_eligibility_artifact_id,runtime_policy_id,
source_policy_snapshot_id,source_capability_snapshot_id)`. It never contains
the projection ID it derives. Missing, duplicate, foreign, or reordered refs
fail closed.

Contextual scope validation receives the actual source context, topology,
parent input, parent budget, child budget, and global budget. It proves parent
and child identities, scope relation, capabilities, forbidden-set
monotonicity, TTL, both budget linkages, depth, lineage, and proof refs from
objects rather than copied IDs.

Cell-input composition is likewise object-complete. A root input requires null
parent cell, parent input, parent-slot artifact, and scope projection. A child
input requires the exact parent cell/input, RUNNING parent-slot queue artifact,
already-validated scope projection, child-local/global budgets, and initial
queue objects/artifacts. Root evidence/context refs derive in semantic order
from the actual G2-C proposal, decision, RouteEligibility, source binding,
policy, topology, topology artifact, and initial queue artifacts. Child refs
append the exact parent input, parent-slot artifact, scope projection, accepted
parent-slot output/evidence, and child initial queue artifacts. No lexical sort
is permitted. Composition accepts no raw `evidence_refs` or `context_refs`.
The contextual validator rebuilds every queue, queue artifact, budget, scope,
planned-child, evidence, context, time, trace, and parent-slot relation from
the supplied typed family.

## 14. Bounded Revise and No-Progress Detection

Revision is explicit, visible, and identity-bound. There is no hidden retry.
`retry_eligible=false` for every partial failure. Bounded revise is the only
retry-like path. `revise_eligible=true` only when all of these are true:

1. current queue state is `VALIDATING`;
2. validation explicitly requests bounded revision;
3. there is no hard policy, authority, scope, lineage, identity, or budget
   failure;
4. no user-resolvable input is missing;
5. `revise_count < max_revise_count`;
6. remaining revise budget is positive;
7. every other remaining budget permits one revision;
8. consecutive non-positive count is below the terminal threshold; and
9. the queue entry is not terminal.

Otherwise revise eligibility is false. No caller or provider may select retry,
revise, `DEADEND`, or `NEEDS_USER`. No terminal snapshot re-enters `READY`.
The exact progress formula is:

```text
progress_units =
  newly_validated_evidence_count
  + newly_resolved_constraints_count
  + newly_accepted_outputs_count
  - newly_introduced_conflicts_count
```

All four dimensions are non-negative integers. If `progress_units <= 0` for
two consecutive revisions, or the next revision would exceed
`max_revise_count=2`, the derived terminal state is `DEADEND`, except that an
explicitly identified and user-resolvable missing input derives `NEEDS_USER`.
A caller or provider cannot choose either terminal result.

Revision respects and never resets depth, fan-out, total-cell, parallelism,
wall-time, token, provider, and revise ceilings. Its t07 transition selects one
READY admission reservation without changing `current_parallelism`; exact
wall-time and revise debits occur in the successor budgets. Every revision
preserves prior input, result, evidence, conflict, budget, queue, and lineage.

`FractalReviseObservationV02` has exactly 21 fields and contains only
`cell_budget_before_id` and `global_budget_before_id`; it predicts no successor
budget identity. Its trace tuple is exactly `(topology_id,cell_id,
queue_entry_id,cell_budget_before_id,global_budget_before_id,
revision_index_as_decimal_text)`.

The exact noncyclic revise order is: current VALIDATING entry and artifact;
before budgets; observation from validated progress and before-state; t07 from
that observation; paired REVISE budget successors whose event ref is t07;
READY successor; queue artifact; then joint contextual validation of the
observation, decision, +1 revise/+1 wall-time deltas, and queue continuity.
Neither revise builder accepts a successor budget. A future identity in the
observation, circular decision, wrong debit, or mismatched event ref fails
closed.

## 15. Partial Failure and Backpressure

A child local failure preserves successful sibling evidence. A successful
sibling cannot launder a failed required child into success.

Exact parent disposition law:

- optional child failure with a valid independent sibling -> `DEGRADED`;
- required child failure with safe partial evidence permitted by policy ->
  `DEGRADED` and Root review required;
- invoked required-child hard failure or no-child hard activation gate ->
  `BLOCKED`;
- invoked or no-child resolvable missing user input -> `NEEDS_USER`;
- invoked exhausted no-progress or no-child non-resolvable path -> `DEADEND`;
- all required children valid -> `COMPLETED`.

Every result and partial-failure record uses one exact start/end/completion
triple: `allocated_cell_budget_id`, `final_cell_budget_id`, and
`global_budget_id`. The allocated object is that cell's unique accepted
INITIAL_ALLOCATION snapshot: same policy/seed/cell, ALLOCATED, no predecessor.
The final object is the same cell's unique PARENT_RETURN-produced FINALIZE
snapshot with a complete gap-free predecessor chain to allocation. All final
consumed and remaining counters come from that one immutable object.

The matching global object is the exact root/global completion snapshot paired
with the same boundary. For root, allocated is root INITIAL_ALLOCATION and
final is the unique root/global FINAL, so `final_cell_budget_id ==
global_budget_id`. For a child, allocated/final are child-local ALLOCATED/FINAL,
global is the paired root/global ACTIVE FINALIZE snapshot, and the IDs differ.
That child global ID is the exact predecessor of the immediate CHILD_AGGREGATE.
A partial-failure record copies the exact triple from its already-built child
result; its builder receives the three objects only to prove equality and
lineage, never to select alternates. Signature 99's `cell_budget` means the
exact final object and `global_budget` the matching completion object.

Mid-chain ACTIVE, foreign/sibling, allocation-with-predecessor, incomplete
chain, later aggregate, wrong completion decision/pair, unequal root
final/global IDs, or equal child final/global IDs fails closed. Every failure
also preserves parent/child, stage, public/source reasons, evidence, traces,
retry/revise eligibility, required/optional status, sibling independence, and
Root review. `retry_eligible` is always false; there is no separate retry.

Result/failure construction is strict postorder for actual children: leaf child
result and artifact first, then its immediate zero-delta CHILD_AGGREGATE, then
parent-slot t06/terminal return, then any failure record that names that built
direct child, then parent result. A no-child gate branch contributes only its
terminal parent-slot queue evidence and never fabricates a result or failure
record. Siblings follow human slot
ordinals 1 then 2, which map to tuple positions/canonical indexes 0 then 1
through `CHILD_SLOT_INDEX_ROWS_V02`. A parent carries every actual direct child
result ID and every actual corresponding failure ID in that order, omitting
uninstantiated slots while retaining every terminal slot queue ID. Self,
ancestor, future, foreign-topology, duplicate, missing, or reordered result or
failure references fail closed. A leaf has both tuples empty. A safe successful
sibling remains visible even when another child fails.

Backpressure construction accepts topology, policy, exact latest global budget,
the exact latest queue family, and explicit `evaluated_round`. Only the round is
an input field. `queue_capacity=policy.max_parallelism`; running, ready,
pending, reason, and reason codes derive from typed state and cannot be caller
values. Signature 88 passes its `admission_round` exactly as `evaluated_round`.

After all non-t03 progress and reservation selections in a round are fixed,
construct at most one `FractalBackpressureStateV02`, and only if dependency-
satisfied PENDING occurrences remain unselected solely because residual
admission slots are zero. It records latest global current parallelism, latest
READY count, exact deferred PENDING count, and queue capacity. Its
`admission_order` is exact queue IDs for READY reservation holders, eligible
RUNNING and VALIDATING occurrences, revise contenders, and dependency-ready
PENDING contenders in state-class/admission-key order. Deferred IDs are the
capacity-unselected PENDING suffix in that order. Then t03 consumes that same
state and emits PENDING successors in deferred order.

Dependencies not satisfied remain ordinary PENDING and never enter the state.
Budget exhaustion is BLOCKED, never backpressure. Available residual capacity
creates no backpressure state. t03 uses
`admission_slot_unavailable_after_ordering`; t04 uses
`admission_slot_selected`; t05 uses `ready_parallel_reservation_valid`; t07
also requires `revise_admission_slot_selected`.

A dependency-satisfied PENDING occurrence receives at most one t03 successor
for one unchanged combination of latest PENDING lineage, global budget ID,
dependency state, cell input ID, activation state, and observed input state. If
its latest PENDING snapshot already records that deferral, reevaluation creates
no backpressure object, Transition, budget, queue, artifact, log entry, or
round-only identity. It is reconsidered only after a controlling identity or
state changes.

A complete round that creates no queue occurrence, deterministic local result,
activation/CELL_CREATE, budget, result, or report progress and has no RUNNING
or READY occurrence capable of future progress fails closed with existing
queue/backpressure/no-progress reasons. It never increments rounds forever.
Misclassification, stale admission, over-reservation, drop, reorder,
unbounded unchanged defer, or scheduler spin fails closed.

## 16. ABI, Transition Registry, Root, and Package Boundaries

### 16.1 One ABI

G2-D uses `KernelArtifactV01`. Existing artifact literals remain an exact
prefix. `RuntimeExecutionTopology` already exists and is not appended again.
The only new artifact literals are, in order:

```text
FractalCellQueueEntry
FractalCellResult
FractalRuntimeReport
```

`hedgehog/kernel/abi_v01.py` and
`schemas/kernel_artifact_v01.schema.json` append those same three literals in
that order; every historical literal remains an exact prefix.

The complete family has four classes. All four use `schema_version=v0.2`,
`authority_class=ADVISORY`, exact Kernel time envelopes, recursive payload
safety, and contextual identities:

| Artifact | Domain / prefix | Source component | Lifecycle / exact parents |
|---|---|---|---|
| `RuntimeExecutionTopology` | `HEDGEHOG_FRACTAL_RUNTIME_TOPOLOGY_KERNEL_ARTIFACT_V02` / `frabi_topology_v02:` | `fractal_runtime_v02` | `VALIDATED`; exact RouteEligibility artifact |
| `FractalCellQueueEntry` | `HEDGEHOG_FRACTAL_CELL_QUEUE_ENTRY_KERNEL_ARTIFACT_V02` / `frabi_queue_v02:` | `fractal_scheduler_v02` | `VALIDATED`; six exact parent forms: root initial; child initial with RUNNING parent slot; ordinary root/child successor including no-child gate return; invoked-child parent FRACTAL_CELL t06 with child result; invoked-child parent FRACTAL_CELL t08-t12 with the same child result |
| `FractalCellResult` | `HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02` / `frabi_result_v02:` | `fractal_runtime_v02` | `COMPLETED`/`DEGRADED`/`NEEDS_USER`/`DEADEND` -> `VALIDATED`; `BLOCKED` -> `BLOCKED_FAIL_CLOSED`; topology, every ordered required terminal queue artifact, then actual ordered direct-child result artifacts |
| `FractalRuntimeReport` | `HEDGEHOG_FRACTAL_RUNTIME_REPORT_KERNEL_ARTIFACT_V02` / `frabi_report_v02:` | `fractal_runtime_v02` | same corrected terminal mapping; topology then ordered result artifacts |

No G2-D-created artifact may use `ROOT_REVIEWED`, `ROOT_ACCEPTED`, or
`ROOT_REJECTED`. Those lifecycle values require an actual later Root operation
outside G2-D. NEEDS_USER remains a NEEDS_USER decision and DEADEND returns
toward Root, but neither falsely records prior Root review. Any escalation is
`g2d_pre_root_lifecycle_escalation_forbidden`.

Every source field is classified exactly once below. `ETR` means
`ENVELOPE_TRANSACTION_ROOT`, `ATR` means `ARTIFACT_TRACE_REFS`, `APR` means
`ARTIFACT_PARENT_REFS`, and `CTX` means `CONTEXT_ONLY`.

```text
RuntimeExecutionTopologyV02
SOURCE_FIELD_COUNT=32
PAYLOAD=(topology_id,topology_version,topology_seed_id,request_id,domain_id,accepted_mode,accepted_scope_ref,source_binding_id,source_root_decision_artifact_id,source_proposal_artifact_id,runtime_policy_id,ordered_node_ids,ordered_edge_ids,ordered_assignment_ids,root_cell_id,global_budget_id,root_review_required,authority_created,permission_created,action_commit_packet_created,receipt_created,final_output_created,drs_write_created,provider_calls,network_calls,real_world_effects_count)
ETR=(transaction_id,owning_root_id)
ATR=(trace_refs)
APR=(source_route_eligibility_artifact_id)
CTX=(time_envelope_ref,parent_refs)

FractalCellQueueEntryV02
SOURCE_FIELD_COUNT=31
PAYLOAD=(queue_entry_id,topology_seed_id,cell_id,parent_cell_id,node_id,planned_child_cell_id,cell_depth,scope_ref,cell_budget_id,global_budget_id,state,prior_state,predecessor_relation,canonical_priority,node_instance_sequence,snapshot_sequence,admission_round,queue_reason_codes,observed_output_refs,observed_evidence_refs,advisory_refs,root_review_required,authority_created,permission_created,final_output_created,drs_write_created,real_world_effects_count)
ETR=()
ATR=(transition_decision_id,lineage_refs)
APR=()
CTX=(topology_id,predecessor_queue_entry_id)

FractalCellResultV02
SOURCE_FIELD_COUNT=32
PAYLOAD=(result_id,topology_seed_id,cell_id,parent_cell_id,cell_depth,cell_input_id,outcome,accepted_output_refs,evidence_refs,pre_result_validation_report_id,partial_failure_ids,allocated_cell_budget_id,final_cell_budget_id,global_budget_id,scope_ref,reason_codes,source_reason_codes,parent_return_required,root_review_required,authority_created,permission_created,action_commit_packet_created,receipt_created,final_output_created,drs_write_created,real_world_effects_count)
ETR=()
ATR=(post_vv_report_ref,gt_advisory_ref,trace_refs)
APR=()
CTX=(topology_id,ordered_terminal_queue_entry_ids,ordered_child_result_ids)

FractalRuntimeReportV02
SOURCE_FIELD_COUNT=42
PAYLOAD=(report_id,report_version,profile_id,topology_seed_id,source_binding_id,request_id,domain_id,accepted_mode,accepted_scope_ref,runtime_outcome,completed_cell_count,degraded_cell_count,blocked_cell_count,needs_user_cell_count,deadend_cell_count,backpressure_state_ids,final_budget_id,report_status,reason_codes,topology_created_count,provider_calls,model_calls,network_calls,connector_calls,external_drs_calls,action_commit_packets_created,permissions_created,receipts_created,final_outputs_created,drs_writes,authority_created_count,real_world_effects_count,root_review_required)
ETR=(transaction_id,owning_root_id)
ATR=(runtime_trace_id,parent_return_transition_decision_id,parent_return_refs)
APR=(topology_artifact_id,ordered_cell_result_ids)
CTX=(topology_id,queue_entry_ids)
```

For topology, the ABI parent tuple is the exact RouteEligibility artifact. The
six queue parent forms are exactly those in Section 12. Root initial has only
topology; child initial has topology then the RUNNING parent slot; ordinary
root/child successor has topology then predecessor and is also the exact form
for no-child gate t06/t10-t12; invoked-child parent FRACTAL_CELL t06 has
topology, its RUNNING predecessor, then the child result artifact; its t08-t12
terminal has topology, its VALIDATING predecessor, then that same child result
artifact. Queue `topology_id` and
`predecessor_queue_entry_id` are CTX because their corresponding artifact IDs
occupy APR and embedding both axes would duplicate lineage; activation-parent
equality is reconstructed from `lineage_refs` and the supplied artifact.
Result APR is derived contextually as topology artifact, every required
terminal queue artifact in projected-node order, then actual direct-child result
artifacts in child postorder. No-child slots contribute their terminal queue
parent and no synthetic result parent. Report APR
is topology then every result artifact in full result postorder. Result/report
object IDs remain source identity material even when their artifact IDs are
parents.

Topology `time_envelope_ref` is CTX because the complete envelope is the ABI
`time_envelope`; topology `parent_refs` is CTX because its broader object
lineage is checked against source objects while the ABI parent remains the
sole RouteEligibility artifact. Report `topology_id` and `queue_entry_ids` are
CTX because topology is APR and the complete queue tuple is represented in
the Stage D-B lineage/runtime trace rather than duplicated as report parents.
Every CTX value remains in source identity and must equal the actual object
family. No other field is CTX and no field is omitted.

Every payload value is copied from the contextually validated source object;
no payload value is fixture-written. Kernel envelope fields are exactly
`abi_version`, `artifact_id`, `artifact_type`, `schema_version`,
`transaction_id`, `owner_root_id`, `source_component`, `authority_class`,
`lifecycle_state`, `payload`, `trace_refs`, `parent_refs`, and
`time_envelope`. None may occur at any mapping depth inside payload. The
reserved-key scanner traverses every nested mapping, sequence, and tuple and
fails closed on cycles or reserved names.

Every artifact has `abi_version=v1.0` and `schema_version=v0.2`.
`transaction_id` and `owner_root_id` equal the validated source binding values;
queue, result, and report projections recover them through the exact topology
and source binding rather than accepting caller envelope values.

All four artifacts use the source-bound G2-C time-envelope projection in exact
order `(ct_session_anchor,et_observed_at,freshness_class,kt_asof,
pt_created_at,ttl_seconds,valid_from,valid_to)`.

Object trace and lineage construction is exact: seed trace/parents are the
Section 9 tuples; node traces are seed, source-binding, canonical node index,
node kind;
edge traces are seed, source node, target node, edge index, and projection
class; assignment traces are seed, node, assignment index, and exact executor;
topology traces are source-binding, root cell, seed, root/global budget, nodes,
edges, assignments;
scope projection parent/child lineages are exact cell ancestry and proof refs;
queue `lineage_refs` use exactly the four root-initial, child-initial, root-
successor, and child-successor base shapes in Section 12, followed by observed
output, evidence, and advisory refs in field order. Parent FRACTAL_CELL t06
inserts the exact child result artifact after predecessor lineage and its
t08-t12 terminal preserves it; artifact ATR prepends the exact Transition
decision. There is no positional sentinel. Child initial entries name the
exact parent-slot artifact and child successors preserve that
activation-parent ID. Revise traces are
`(topology_id,cell_id,queue_entry_id,cell_budget_before_id,
global_budget_before_id,revision_index_as_decimal_text)`.
Partial-failure traces are `(topology_id,parent_cell_id,child_cell_id,
child_result_id,allocated_cell_budget_id,final_cell_budget_id,
global_budget_id)` followed by evidence refs. Backpressure lineage is
`(topology_id,global_budget_id)` followed by deferred
queue IDs then admission order. Cell-input traces are `(topology_id,cell_id,
optional_scope_projection_id,cell_budget_id,global_budget_id)` followed by projected nodes, initial
queues, and required queues. Result traces are `(cell_input_id)` followed by
terminal queues, child results, output/evidence refs, pre-result validation,
failures, allocated/final cell budgets, and matching completion global budget;
Post V&V and GT refs are separate
ATR fields and are not repeated inside `trace_refs`. Runtime trace fields
retain their declared tuple order. `ordered_queue_entry_ids` and
`state_transition_decision_ids` use the queue execution-build log;
`cell_result_ids` uses canonical result postorder; `abi_artifact_refs` is
exactly `(topology_artifact_id,*RUNTIME_ABI_ARTIFACT_BUILD_LOG_V02)`; and
`transition_refs` is t01, every occurrence-aligned state decision in queue-log
order, then the one root parent-return decision. Report `parent_return_refs` is
derived as the one-element tuple containing the supplied root-result artifact
ID; artifact ATR order is runtime trace ID, parent-return decision ID, then that
root-result ref.

Trace construction receives actual topology, source binding, topology artifact,
queue entries/artifacts, occurrence-aligned state decisions, cell inputs and
results, result artifacts, the typed post-topology runtime ABI artifact log,
scope projections, revise observations, partial failures, backpressure states,
the typed budget construction log, exact t01 decision, exact t13-t17 decision,
and root-result artifact. It derives, rather than accepts, every ID tuple:

```text
ordered_queue_entry_ids = queue execution-build-log order
state_transition_decision_ids = one decision ID per queue occurrence
cell_input_ids = cell-instantiation preorder
cell_result_ids = canonical result postorder
scope_projection_ids = accepted child CELL_CREATE order
revise_observation_ids = accepted revise occurrence order in the queue log
partial_failure_ids = parent-result postorder, then direct-child slot order
backpressure_state_ids = construction order by strictly increasing evaluated_round
budget_ids = BUDGET_CONSTRUCTION_LOG_V02 order
abi_artifact_refs = (topology_artifact_id,*runtime_abi_artifact_ids)
transition_refs = (t01_id,*state_transition_decision_ids,t13_to_t17_id)
parent_return_refs = (root_result_artifact_id,)
```

`runtime_abi_artifacts` contains every queue/result artifact exactly once in
interleaved accepted construction order and contains no topology or report.
Its queue projection equals queue-artifact log order and its result projection
equals result postorder. Every artifact parent precedes its dependent. The root
result artifact is the final result artifact and binds the root result. The
report builder derives result, queue, and backpressure orders from typed values,
selects the unique ROOT_GLOBAL_AND_CELL FINAL from the budget log, and derives
parent return from the actual root-result artifact. No caller supplies ABI,
Transition, parent-return, budget-order, queue-order, or result-order refs.

No tuple contains the identity or artifact ID it derives, a not-yet-built
identity, a foreign transaction/Root/domain ref, or a lexical resort where
semantic order is required. Prohibited duplicates remain rejected for object,
artifact, queue, result, scope, and budget identities. Causal rows have no
identity field; duplicate complete canonical plain rows are rejected. Repeated
semantic Transition decision IDs are legal only in occurrence-aligned trace
and execution-bundle tuples. Self-reference, omitted field, prohibited
duplicate, wrong order, foreign ref, or CTX inequality fails closed.

Artifact ID material is canonical complete artifact plain data with only
`artifact_id` omitted, under the artifact-specific domain. Structural
validation for every class is the existing `validate_kernel_artifact_v01`;
it owns envelope, types, recursive safety, and generic identity. Exact
contextual validation is `validate_fractal_runtime_abi_profile_v02`, which
dispatches only the four literal/object pairs and owns payload/object equality,
source component,
lifecycle, time, trace, parent, transaction, Root, G2-C source, and rebuilt
contextual identity. Envelope/payload defects use public G2-D ABI reasons;
substituted source-owned objects retain their source reasons separately.

Stage D-A is exactly the G2-C proposal artifact, G2-C Root-decision artifact,
G2-C RouteEligibility artifact, then topology artifact. Stage D-B is exactly
the first three G2-C artifacts followed by
`runtime_trace.abi_artifact_refs`; topology therefore appears once as its
first runtime-trace ABI ref. Stage D-C is Stage D-B followed by exactly one
report artifact. The interleaved log places every parent before its dependent:
the RUNNING parent slot before child initial queues, each child result artifact
before its parent-slot t06 and terminal return artifacts, and all required
descendant/terminal artifacts before the root result artifact. Each stage
proves exact equality to trace refs, queue-only and result-only projections,
parent-before-dependent order, predecessor/activation/result-parent
continuity, no duplicate or extra/missing runtime artifact, no cycle, unknown
or self parent, substitution, post-hoc regrouping, and complete contextual
G2-C validity.

```text
STAGE_D_A=(g2c_proposal_artifact_id,g2c_root_decision_artifact_id,
           g2c_route_eligibility_artifact_id,topology_artifact_id)
runtime_trace.abi_artifact_refs=
  (topology_artifact_id,*RUNTIME_ABI_ARTIFACT_BUILD_LOG_V02)
STAGE_D_B=(g2c_proposal_artifact_id,g2c_root_decision_artifact_id,
           g2c_route_eligibility_artifact_id,
           *runtime_trace.abi_artifact_refs)
STAGE_D_C=(*STAGE_D_B,report_artifact_id)
```

### 16.2 One Transition Registry family

Profile ID is `fractal_runtime_g2d_transition_profile_v02`; registry version is
`v0.1`; ABI major is `1`; rule count is `17`. Registry identity is rebuilt from
the exact ordered rule projection under the existing Registry domain.

G2-D2 owns the three ABI literal appends and complete pure 17-rule profile.
Its exact authority order is actual G2-C family -> source-derived policy,
context, and binding -> seed, global budget, templates -> validated
non-authoritative topology candidate -> t01 using actual G2-C Root commit ->
topology artifact. D2 evaluates no queue rule. D3 activates t02-t12 and queue
artifacts; D4 activates result/report artifacts, t13-t17, stages, causal
profile, and facade. No topology is consumed before t01, and no later-slice
callable exists early.

| Rule | Source -> target | Attempt | Result reason |
|---|---|---|---|
| `g2d_t01_route_eligibility_to_topology` | RouteEligibility `ROOT_ACCEPTED` -> RuntimeExecutionTopology | `CONSTRUCT_RUNTIME_TOPOLOGY` | `g2d_transition_topology_construction_allowed` |
| `g2d_t02_topology_to_pending` | topology `VALIDATED` -> queue entry | `ADMIT_TOPOLOGY_QUEUE` | `g2d_transition_queue_admission_allowed` |
| `g2d_t03_pending_backpressure_defer` | PENDING -> PENDING | `DEFER_BACKPRESSURE` | `g2d_transition_backpressure_deferred` |
| `g2d_t04_pending_to_ready` | PENDING -> READY | `MARK_READY` | `g2d_transition_pending_ready_allowed` |
| `g2d_t05_ready_to_running` | READY -> RUNNING | `START_LOCAL_WORK` | `g2d_transition_ready_running_allowed` |
| `g2d_t06_running_to_validating` | RUNNING -> VALIDATING | `ENTER_VALIDATION` | `g2d_transition_running_validating_allowed` |
| `g2d_t07_validating_to_revise` | VALIDATING -> READY | `REVISE_BOUNDED` | `g2d_transition_bounded_revise_allowed` |
| `g2d_t08_validating_to_completed` | queue `VALIDATING` -> queue `COMPLETED` | `RECORD_COMPLETED` | `g2d_transition_completed_recorded` |
| `g2d_t09_validating_to_degraded` | queue `VALIDATING` -> queue `DEGRADED` | `RECORD_DEGRADED` | `g2d_transition_degraded_recorded` |
| `g2d_t10_validating_to_blocked` | queue `VALIDATING` -> queue `BLOCKED` | `RECORD_BLOCKED` | `g2d_transition_blocked_recorded` |
| `g2d_t11_validating_to_needs_user` | queue `VALIDATING` -> queue `NEEDS_USER` | `RECORD_NEEDS_USER` | `g2d_transition_needs_user_recorded` |
| `g2d_t12_validating_to_deadend` | queue `VALIDATING` -> queue `DEADEND` | `RECORD_DEADEND` | `g2d_transition_deadend_recorded` |
| `g2d_t13_completed_to_parent_return` | COMPLETED -> runtime report | `RETURN_TO_PARENT` | `g2d_transition_completed_parent_return` |
| `g2d_t14_degraded_to_parent_return` | DEGRADED -> runtime report | `RETURN_TO_PARENT` | `g2d_transition_degraded_parent_return` |
| `g2d_t15_blocked_to_parent_return` | BLOCKED -> runtime report | `RETURN_TO_PARENT` | `g2d_transition_blocked_parent_return` |
| `g2d_t16_needs_user_to_parent_return` | NEEDS_USER -> runtime report | `RETURN_TO_PARENT` | `g2d_transition_needs_user_parent_return` |
| `g2d_t17_deadend_to_parent_return` | DEADEND -> runtime report | `RETURN_TO_PARENT` | `g2d_transition_deadend_parent_return` |

The complete ordered `TransitionRuleV01` field geometry is frozen below as
`(rule_id, abi_major_version, source_artifact_type, source_lifecycle_state,
actor_role, attempted_effect, target_artifact_type, required_guards, decision,
reason_code, root_commit_required)`:

```text
(g2d_t01_route_eligibility_to_topology,1,ExecutionModeRouteEligibility,ROOT_ACCEPTED,fractal_runtime,CONSTRUCT_RUNTIME_TOPOLOGY,RuntimeExecutionTopology,(g2c_profile_valid,route_eligibility_context_valid,runtime_topology_class,runtime_policy_valid,root_commit_present),ALLOW,g2d_transition_topology_construction_allowed,true)
(g2d_t02_topology_to_pending,1,RuntimeExecutionTopology,VALIDATED,fractal_runtime,ADMIT_TOPOLOGY_QUEUE,FractalCellQueueEntry,(topology_context_valid,budget_valid,queue_capacity_visible,queue_predecessor_initial_none,root_commit_present),ALLOW,g2d_transition_queue_admission_allowed,true)
(g2d_t03_pending_backpressure_defer,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,DEFER_BACKPRESSURE,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_pending,predecessor_queue_artifact_lineage_valid,cell_activation_valid,dependencies_satisfied,cell_input_context_valid,budget_available,admission_slot_unavailable_after_ordering,lineage_preserved,root_commit_present),ALLOW,g2d_transition_backpressure_deferred,true)
(g2d_t04_pending_to_ready,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,MARK_READY,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_pending,predecessor_queue_artifact_lineage_valid,cell_activation_valid,dependencies_satisfied,cell_input_context_valid,budget_available,admission_slot_selected,root_commit_present),ALLOW,g2d_transition_pending_ready_allowed,true)
(g2d_t05_ready_to_running,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,START_LOCAL_WORK,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_ready,predecessor_queue_artifact_lineage_valid,assignment_valid,ready_parallel_reservation_valid,budget_available,root_commit_present),ALLOW,g2d_transition_ready_running_allowed,true)
(g2d_t06_running_to_validating,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,ENTER_VALIDATION,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_running,predecessor_queue_artifact_lineage_valid,cell_input_context_valid,local_result_or_activation_gate_outcome_available,running_budget_debit_present,global_parallelism_release_derivable,root_commit_present),ALLOW,g2d_transition_running_validating_allowed,true)
(g2d_t07_validating_to_revise,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,REVISE_BOUNDED,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_validating,predecessor_queue_artifact_lineage_valid,cell_validation_complete,revise_eligible,progress_policy_valid,budget_available,revise_admission_slot_selected,root_commit_present),ALLOW,g2d_transition_bounded_revise_allowed,true)
(g2d_t08_validating_to_completed,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,RECORD_COMPLETED,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_validating,predecessor_queue_artifact_lineage_valid,node_validation_complete,node_outcome_completed,budget_accounted,root_commit_present),ALLOW,g2d_transition_completed_recorded,true)
(g2d_t09_validating_to_degraded,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,RECORD_DEGRADED,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_validating,predecessor_queue_artifact_lineage_valid,node_validation_complete,node_outcome_degraded,node_degraded_basis_valid,budget_accounted,root_commit_present),RETURN_TO_ROOT,g2d_transition_degraded_recorded,true)
(g2d_t10_validating_to_blocked,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,RECORD_BLOCKED,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_validating,predecessor_queue_artifact_lineage_valid,node_validation_complete,node_outcome_blocked,node_hard_failure_valid,budget_accounted,root_commit_present),BLOCKED_FAIL_CLOSED,g2d_transition_blocked_recorded,true)
(g2d_t11_validating_to_needs_user,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,RECORD_NEEDS_USER,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_validating,predecessor_queue_artifact_lineage_valid,node_validation_complete,node_outcome_needs_user,node_resolvable_input_missing,budget_accounted,root_commit_present),NEEDS_USER,g2d_transition_needs_user_recorded,true)
(g2d_t12_validating_to_deadend,1,FractalCellQueueEntry,VALIDATED,fractal_scheduler,RECORD_DEADEND,FractalCellQueueEntry,(queue_entry_context_valid,queue_state_validating,predecessor_queue_artifact_lineage_valid,node_validation_complete,node_outcome_deadend,node_no_progress_or_nonresolvable,budget_accounted,root_commit_present),RETURN_TO_ROOT,g2d_transition_deadend_recorded,true)
(g2d_t13_completed_to_parent_return,1,FractalCellResult,VALIDATED,fractal_runtime,RETURN_TO_PARENT,FractalRuntimeReport,(cell_result_context_valid,cell_outcome_completed,source_cell_is_root,root_cell_result_context_valid,all_required_descendant_results_accounted,canonical_result_postorder_valid,parent_lineage_valid,root_review_required,root_commit_present),RETURN_TO_ROOT,g2d_transition_completed_parent_return,true)
(g2d_t14_degraded_to_parent_return,1,FractalCellResult,VALIDATED,fractal_runtime,RETURN_TO_PARENT,FractalRuntimeReport,(cell_result_context_valid,cell_outcome_degraded,source_cell_is_root,root_cell_result_context_valid,all_required_descendant_results_accounted,canonical_result_postorder_valid,parent_lineage_valid,root_review_required,root_commit_present),RETURN_TO_ROOT,g2d_transition_degraded_parent_return,true)
(g2d_t15_blocked_to_parent_return,1,FractalCellResult,BLOCKED_FAIL_CLOSED,fractal_runtime,RETURN_TO_PARENT,FractalRuntimeReport,(cell_result_context_valid,cell_outcome_blocked,source_cell_is_root,root_cell_result_context_valid,all_required_descendant_results_accounted,canonical_result_postorder_valid,parent_lineage_valid,root_review_required,root_commit_present),BLOCKED_FAIL_CLOSED,g2d_transition_blocked_parent_return,true)
(g2d_t16_needs_user_to_parent_return,1,FractalCellResult,VALIDATED,fractal_runtime,RETURN_TO_PARENT,FractalRuntimeReport,(cell_result_context_valid,cell_outcome_needs_user,source_cell_is_root,root_cell_result_context_valid,all_required_descendant_results_accounted,canonical_result_postorder_valid,parent_lineage_valid,root_review_required,root_commit_present),NEEDS_USER,g2d_transition_needs_user_parent_return,true)
(g2d_t17_deadend_to_parent_return,1,FractalCellResult,VALIDATED,fractal_runtime,RETURN_TO_PARENT,FractalRuntimeReport,(cell_result_context_valid,cell_outcome_deadend,source_cell_is_root,root_cell_result_context_valid,all_required_descendant_results_accounted,canonical_result_postorder_valid,parent_lineage_valid,root_review_required,root_commit_present),RETURN_TO_ROOT,g2d_transition_deadend_parent_return,true)
```

Every rule has `root_commit_required=true`; `root_commit_present` is derived
only from the actual validated G2-C Root result. Required guards are ordered,
content-derived facts for source context, topology or queue state, budget,
scope, outcome, parent lineage, and Root review. No caller may supply a guard
or Root-commit boolean.

G2-D reuses the existing `TransitionRuleV01`, `TransitionDecisionV01`, and
`TransitionRegistryV01` dataclasses and validators. Its validator is
profile-aware and exact, like G2-C; the historical default Registry vocabulary
is not authority for G2-D actors, attempts, guards, or reasons. Every source
and target type above is a known ABI literal after the three-literal append.
Contextual evaluators bind exact source and target artifact IDs outside the
generic decision field shape. A structurally valid decision with foreign
objects fails closed. Queue successors require exact predecessor queue
artifact lineage. The state evaluator receives no target snapshot or target
artifact. It derives the sole legal rule from immutable pre-state and returns
`TransitionDecisionV01 | None`; ordinary dependency wait returns `None` and
creates no successor. For t02 the source is topology artifact and current
entry/input are null. For t03-t12 the source is the exact current queue
artifact, duplicated scalars equal the entry, and optional report, revise, and
backpressure inputs obey `QUEUE_TRANSITION_INPUT_ROWS_V02`. t02-t05 neither
receive nor create observation refs. t06 alone introduces one attempt's
observations and current-attempt queue reasons. For FRACTAL_CELL,
`local_result_or_activation_gate_outcome_available` derives from exactly one of
the actual child result/artifact branch or the recomputed no-child activation-
gate branch. t07 clears target observations and reasons and is forbidden for
both FRACTAL_CELL completion branches. t08/t09 require actual child result
mapping; t10-t12 conditionally project either
`CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02` or
`CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02`. Other node outcomes derive from
their deterministic local observation/validation class. The evaluator and
queue advance receive identical target reasons, observations, and conditional
child-result inputs.

For every non-PARENT_RETURN evaluation, all seven components of
`PARENT_RETURN_TYPED_INPUT_COMPONENTS_V02` are exactly empty or null under the
11-column input table. For PARENT_RETURN t06 and t08-t12, signature 90 receives
the actual proposal prefix, typed child/failure families, proposal, VV report,
GT advisory, and ordered RESULT_PROPOSAL/POST_VV_REPORT/GT_ADVISORY_REPORT PASS
reports. It independently reconstructs all three reports, cross-binds source
request, cell, topology, KT, evidence, actual child/failure IDs, and report IDs,
then derives status, observations, advisories, and queue reasons from those
objects. Copied IDs, status, reasons, or PASS labels cannot select a rule.

The generic decision identity is semantic and does not contain source or
target artifact IDs, cell, node, or queue occurrence identity. Consequently,
value-identical decisions may share one `decision_id`. Contextual validation
binds each occurrence through its exact source and target artifacts, queue
predecessor, cell/node/budget lineage, snapshot sequence, and scheduler round.
Repeated decision IDs are accepted in occurrence-aligned trace and bundle
tuples; they are rejected only where a specific semantic contract requires one
unique decision, such as t01 or the one root parent-return decision.
For parent-slot return, the concrete queue/artifact occurrence, exact child
result parent, budgets, predecessor, sequence, and round remain unique even
when a generic semantic t08-t12 decision ID is value-identical elsewhere.

An allowed decision is built before required budget successors, then target
snapshot and artifact; contextual source/target binding runs last. t04 and t07
require an exact selected residual READY reservation; t05 validates and consumes
that reservation while START_NODE changes current parallelism, so occupied
admission capacity is unchanged. t06 proves the running debit and derivable
release; FINISH_NODE releases it afterward. Non-PARENT_RETURN t08-t12 create no
budget successor. No guard asserts a future mutation, and no caller supplies
guards, `root_commit_present`, state, outcome, decision, or PASS.

Rules t08-t12 authorize and record only the immutable terminal queue snapshot;
they do not create `FractalCellResultV02` or execute control flow. Terminal
queue to result is a deterministic contextual projection after pre-result
validation, Post V&V, GT, budget validation, and child-result aggregation. It
creates no authority, permission, or effect. Rules t13-t17 accept only the
exact root result and produce exactly one parent-return decision per runtime
report. A child result, partial failure, queue state, GT report, or caller label
cannot target `FractalRuntimeReport`; a child result supplied to t13-t17 fails
with `g2d_child_result_direct_parent_return_forbidden` and
`g2d_root_result_required_for_parent_return`.

### 16.3 Deterministic Post V&V and GT time boundary

G2-D4 owns exactly four public composition helpers:

```text
build_fractal_cell_result_proposal_v02
validate_fractal_cell_result_proposal_v02
validate_fractal_post_vv_report_v02
validate_fractal_gt_advisory_v02
```

Signatures 93 and 94 consume only
`pre_post_vv_terminal_queue_entries`. That tuple is the exact projected-node
terminal prefix before POST_VV and is sufficient to derive proposal status,
outputs, evidence, actual child-result IDs, and actual partial-failure IDs.
Signatures 57 and 99 retain `terminal_queue_entries`, meaning the complete
required projected-node terminal tuple after POST_VV, GT_ADVISORY,
PARENT_RETURN, and unique completion budgets exist. The two tuples are never
aliases, and the complete tuple cannot be supplied early to the proposal
helpers.

The G2-D ResultProposal top-level key order is exact:

```text
proposal_id,request_id,producer,vector_id,plan_id,result_payload,evidence,cost,risks,time_envelope,trace_refs
```

`proposal_id` is content-derived under
`HEDGEHOG_FRACTAL_RUNTIME_V02_RESULT_PROPOSAL`, prefix `frproposal_v02:`, from
the complete canonical plain dictionary with only `proposal_id` omitted.
`request_id` is the exact source request; `producer` is the exact plain dict
`{"executor_id":"fractal_runtime_v02"}`; `vector_id=cell_id`; and
`plan_id=topology_id`. The ordered `result_payload` is:

```text
artifact_type,status,task_completed,requires_human_input,blocked_reason,
cell_id,parent_cell_id,cell_depth,ordered_child_result_ids,
accepted_output_refs,evidence_refs,partial_failure_ids,dependency_depth,
authority_created,permission_created,action_commit_packet_created,
receipt_created,final_output_created,drs_write_created,
real_world_effects_count
```

`artifact_type=FractalCellLocalResult`. Status is exactly `completed`,
`degraded`, `blocked`, `needs_user`, or `deadend`. Evidence contains one exact
item per evidence ref, in order:

```json
{"kind":"simulated_executor","summary":"G2-D bounded local deterministic evidence","ref_id":"<exact evidence ref>","confidence":1.0}
```

Proposal status, outputs, evidence, `ordered_child_result_ids`, and
`partial_failure_ids` derive from the exact pre-Post-V&V terminal prefix plus
the actual typed child-result/failure families. Both parent-slot returns remain
visible to FRACTAL_MERGE even when a no-child gate slot contributes no child ID
or failure ID. A synthetic child result or failure record for an uninstantiated
planned child is forbidden.

Cost is exactly `{"tokens":0,"walltime_ms":0,"toolcalls":0}`; risks is `[]`
in the deterministic positive profile. `time_envelope` is the exact current
eight-field G2-C Kernel projection in ABI order. `trace_refs` are exact objects
in source order: `{"trace_id":"<exact ref>","kind":"g2d_runtime"}`. Raw trace
strings, PlanGraph, provider output, secret, FinalOutput, answer, and user text
are forbidden. The proposal must pass current
`schemas/result_proposal.schema.json` before Post V&V.

`FractalRuntimeExecutionBundleV02` stores the exact postorder tuples
`result_proposals`, `post_vv_reports`, and `gt_advisory_reports`. Each item is
an exact plain `dict`, not a subclass, recursively JSON-safe, schema-valid, and
compared by canonical bytes. There is exactly one proposal, one Post V&V
report, and one GT report per cell result in result postorder.

G2-D4 makes additive, backward-compatible changes to the current validators:

```python
validate_result_proposal(
    proposal: dict,
    *,
    checked_at: str | None = None,
) -> dict

validate_result_proposals(
    proposals: list[dict],
    *,
    checked_at: str | None = None,
) -> list[dict]

validate_gt(
    vv_reports: list[dict],
    game_mode: str = "result_selection",
    *,
    created_at: str | None = None,
) -> dict
```

`None` preserves every historical default call and output shape. G2-D never
passes `None`; both keywords equal the exact canonical UTC
`router_input.local_routing_snapshot.kt_asof_utc` from the validated G2-C
source. KT is the decision/evaluation axis; PT remains creation time. Batch
Post V&V passes one identical `checked_at` to every item. The existing safe
outgoing-schema rejection branch receives the same resolved time; it is not a
fallback validator. GT uses the exact explicit `created_at`. Invalid non-None
time raises, without chained exception, exactly
`ValueError("post_vv_checked_at_invalid")` or
`ValueError("gt_created_at_invalid")`. G2-D records those source-owned reasons
and fails closed; it accepts no partial output. Canonical injected time is
second-precision `YYYY-MM-DDTHH:MM:SS+00:00`; `Z`, non-UTC offsets, fractional
seconds, naive values, and values unequal to source KT fail closed. No current
default caller is migrated and no historical output is rewritten.

When `created_at is None`, all existing GT outputs, including constant revise
and no-update IDs, remain byte-for-byte compatible. The explicit-time G2-D path
passes exactly one VVReport for one proposal. Its IDs are:

```text
accepted: gt:<game_mode>:<proposal_id>
revise: gt:<game_mode>:revise:<proposal_id>
no_update: gt:<game_mode>:no_update:<proposal_id>
```

The proposal ID is read from that single VVReport; zero or multiple reports on
the G2-D helper path fail closed. Every `post_vv_report_ref` is the exact
`vv_report_id`; every `gt_advisory_ref` is the exact `gt_report_id`. Proposal,
VV, GT, and result tuples are one-to-one in result postorder and every ID is
bundle-unique. A collision, non-contextual ID, or ref mismatch fails closed.

The only G2-D validation flow is:

```text
freeze and validate pre_post_vv_terminal_queue_entries
-> build and schema-validate canonical local ResultProposal
-> independently build exact RESULT_PROPOSAL PASS report
-> validate_result_proposals(..., checked_at=source_time)
-> validate outgoing VVReport schema
-> independently build exact POST_VV_REPORT PASS report
-> validate_gt(..., created_at=source_time)
-> validate GT advisory schema
-> independently build exact GT_ADVISORY_REPORT PASS report
-> pass actual typed family and exact three-report tuple to signature 90
-> independently reconstruct reports and all proposal/VV/GT cross-bindings
-> derive status only from result_payload.status and rederive observations/reasons
-> map through PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02
-> build PARENT_RETURN t06 and exact t08-t12 terminal occurrence only after decision
-> build and validate unique completion budgets
-> validate complete terminal_queue_entries and cell-result preconditions
-> FractalCellResultV02
```

There is no `ModuleNotFoundError`, shape-only, raw PlanGraph, raw provider, or
other fallback, fabricated PASS, or hidden wall-clock path. Post V&V failure
prevents GT success and successful cell completion.

The terminal mapping is exact:

| Outcome | ResultProposal fields | Post V&V | GT | Controlling condition |
|---|---|---|---|---|
| `COMPLETED` | `completed,true,false,null` | `accept/accepted` | `accept` | valid complete, no hard failure |
| `DEGRADED` | `degraded,true,false,null` | `accept/accepted` | `accept` | valid partial-failure evidence |
| `BLOCKED` | `blocked,false,false,<exact public hard-failure reason>` | `revise/needs_revision` or `reject/rejected` | `revise` or `no_update` | hard failure; GT cannot upgrade |
| `NEEDS_USER` | `needs_user,false,true,null` | `revise/needs_revision` | `revise` | exact resolvable-input evidence |
| `DEADEND` | `deadend,false,false,g2d_no_progress_deadend` | `revise/needs_revision` | `revise` | exact no-progress evidence |

`PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02` maps the five proposal statuses to
t08, t09, t10, t11, and t12 respectively after t06. Signature 90 rederives its
local observation from the exact actual proposal/VV/GT family and exact three-
report reconstruction frozen in Section 12. Post V&V and GT cannot upgrade
that hard derived status; copied PASS/status/reason is not authority.
Structural failure returns FAIL_CLOSED and creates no result or terminal queue.

Precedence first separates corruption from valid outcomes. Any malformed type,
identity, lineage, artifact, predecessor, event, state, counter, optional-input,
or cross-binding geometry is FAIL_CLOSED. Among structurally valid outcomes,
validated hard policy/authority/scope/budget denial -> `BLOCKED`, resolvable
missing user input -> `NEEDS_USER`, exhausted revise/no-progress -> `DEADEND`,
safe partial child failure -> `DEGRADED`, otherwise valid complete ->
`COMPLETED`. Post V&V and GT are advisory validators and cannot choose or
upgrade that derived hard outcome.

`blocked_reason` is never caller-selected: COMPLETED, DEGRADED, and NEEDS_USER
use `null`; DEADEND uses `g2d_no_progress_deadend`; BLOCKED uses the first
applicable public hard-failure reason in `PUBLIC_G2D_REASON_CODES` order after
terminal precedence and public/source reason separation. COMPLETED and
DEGRADED require at least one exact evidence ref and EvidenceItem. Missing
positive evidence prevents accepted completion; failure proposals retain exact
diagnostic evidence when available.

Every complete contextually valid `FractalRuntimeReportV02` has
`report_status=PASS`, including BLOCKED, NEEDS_USER, and DEADEND runtime
outcomes. Invalid aggregation/profile material creates no canonical report or
artifact; it returns a FAIL_CLOSED validation report. Exactly one root result
exists. `runtime_outcome` and `reason_codes` equal that root result; the
parent-return decision is its one t13-t17 decision; `parent_return_refs` is its
one-element result-artifact tuple. `ordered_cell_result_ids` contains all
children and root in result postorder, and all counts derive from that tuple.
Child results influence parent aggregation and audit/count fields only; they
cannot select report outcome, reasons, return decision, or Root path.

Focused D4/D5 tests cover schema and key order, one-call-per-cell cardinality,
plain-dict shape, callable historical defaults, exact KT injection, batch
equality, source-owned invalid-time errors, safe rejection, no wall-clock use,
five terminal mappings, precedence, byte-identical outputs, and zero provider,
model, network, connector, or effect calls.

### 16.4 Causal consumption and counterfactual law

G2-D reuses the existing ABI `CausalConsumptionRefV01`; it creates no second
causal type. Causal refs are built from explicit already-settled source,
topology, assignment, queue, result, trace, report, and artifact families,
never from a final execution bundle. `FractalRuntimeExecutionBundleV02` then
stores those complete families. It is runtime-only, has no identity, and
creates no authority. Report-directed refs are built after the report artifact
exists, so causal metadata never enters a report or bundle cycle.

`CausalConsumptionRefV01` is mandatory for cross-artifact semantic influence.
Internal derivation among non-ABI dataclasses is proved by content-derived
identity, contextual validators, Transition decisions, and explicit
counterfactuals; it is not mislabeled as a generic causal ref because the ABI
validator requires actual Kernel source and downstream artifacts.

The exact artifact tuple passed to `validate_causal_consumption_bundle_v01` is
the Stage D-C tuple: G2-C proposal artifact, G2-C Root-decision artifact,
RouteEligibility artifact, every `runtime_trace.abi_artifact_refs` item in
interleaved construction order, then the report artifact. Every causal
source/downstream artifact occurs exactly once in that tuple.

Mandatory causal rows are exact:

| Source -> downstream | `output_field` | Producer / consumer | Effect / disposition / reason |
|---|---|---|---|
| RouteEligibility -> topology | `/accepted_mode` | `root_decision_v01 / fractal_runtime_v02` | `TOPOLOGY_SELECTION / USED / used:g2d_route_accepted_mode` |
| RouteEligibility -> topology | `/accepted_scope_ref` | same | `TOPOLOGY_SCOPE / USED / used:g2d_route_accepted_scope` |
| RouteEligibility -> topology | `/downstream_consumption_class` | same | `TOPOLOGY_SELECTION / USED / used:g2d_route_consumption_class` |
| exact RUNNING parent child-slot queue -> first child initial queue artifact | `/planned_child_cell_id` | exact parent assignment `executor_component_id / fractal_scheduler_v02` | `CHILD_ACTIVATION / USED / used:g2d_planned_child_activation` |
| exact child result artifact -> its parent-slot t06 VALIDATING queue artifact, one row for each listed field | `/result_id`, `/accepted_output_refs`, `/evidence_refs` | `fractal_runtime_v02 / fractal_scheduler_v02` | `CHILD_RESULT_RETURN_BINDING / USED / used:g2d_child_result_return` |
| exact child result artifact -> its parent-slot t08-t12 terminal queue artifact | `/outcome` | `fractal_runtime_v02 / fractal_scheduler_v02` | `CHILD_RESULT_TERMINAL_MAPPING / USED / used:g2d_child_result_terminal` |
| every required terminal queue artifact -> exact cell result artifact | `/state` | exact assignment `executor_component_id / fractal_runtime_v02` | `CELL_TERMINAL_OUTCOME / USED / used:g2d_terminal_outcome` |
| every required terminal queue artifact with nonempty reasons -> exact cell result artifact | `/queue_reason_codes` | exact assignment `executor_component_id / fractal_runtime_v02` | `CELL_TERMINAL_OUTCOME / USED / used:g2d_terminal_reason` |
| terminal queue -> cell result, one row per accepted output | `/observed_output_refs/<canonical index>` | exact assignment `executor_component_id / fractal_runtime_v02` | `CELL_RESULT_OUTPUT / USED / used:g2d_cell_output` |
| terminal queue -> cell result, one row per evidence item | `/observed_evidence_refs/<canonical index>` | exact assignment `executor_component_id / fractal_runtime_v02` | `CELL_RESULT_EVIDENCE / USED / used:g2d_cell_evidence` |
| validating queue -> terminal queue, rejected unsafe output | exact `/observed_output_refs/<canonical index>` | exact assignment component / `fractal_scheduler_v02` | `CELL_RESULT_OUTPUT / REJECTED / rejected:g2d_child_output` |
| validating queue -> terminal queue, hard-gated output | same | exact assignment component / `fractal_scheduler_v02` | `CELL_RESULT_OUTPUT / BLOCKED_BY_GATE / gate:g2d_child_output` |
| terminal queue -> exact cell result artifact, unused advisory | `/advisory_refs/<canonical index>` | exact assignment component / `fractal_runtime_v02` | `UNUSED_ADVISORY / IGNORED_WITH_REASON / ignored:g2d_unused_advisory` |
| direct child result -> parent cell result, four rows per child | `/result_id`, `/outcome`, `/accepted_output_refs`, `/evidence_refs` | `fractal_runtime_v02 / fractal_runtime_v02` | `PARENT_CELL_AGGREGATION / USED / used:g2d_child_result_aggregation` |
| each accepted cell result -> report, four rows per result | `/result_id`, `/outcome`, `/accepted_output_refs`, `/evidence_refs` | `fractal_runtime_v02 / fractal_runtime_v02` | `RUNTIME_REPORT_AGGREGATION / USED / used:g2d_result_aggregation` |
| exact root result -> report | `/outcome`, `/reason_codes` | `fractal_runtime_v02 / fractal_runtime_v02` | `RUNTIME_OUTCOME_SELECTION / USED / used:g2d_root_outcome_selection` |

The per-result `RUNTIME_REPORT_AGGREGATION` rows affect ordered inventory,
evidence visibility, and counts only. Only the two exact root-result
`RUNTIME_OUTCOME_SELECTION` rows select report outcome and public reasons.

There is exactly one CHILD_ACTIVATION row per activated child and none for an
unactivated plan. The downstream first child initial artifact names the source
RUNNING parent-slot artifact as its exact activation parent. Mutating the
planned ID, parent artifact, state, slot, or downstream parent binding blocks
child admission.

Every activated child also has exactly three CHILD_RESULT_RETURN_BINDING rows
for `/result_id`, `/accepted_output_refs`, and `/evidence_refs`, plus one
CHILD_RESULT_TERMINAL_MAPPING row for `/outcome`. The former downstream is its
exact parent-slot t06 VALIDATING artifact and the latter downstream is the
exact t08-t12 terminal artifact selected by
`CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02`. Both downstream artifacts name
the source child result artifact as an exact ABI parent. Existing direct-child
result to parent-cell-result aggregation rows remain required and are not
replaced. Slot/result substitution, missing result parent, wrong mapping row,
or wrong merge order fails closed.

Every required terminal queue artifact used by one cell result has one
mandatory `CELL_TERMINAL_OUTCOME` `/state` row. When its
`queue_reason_codes` is nonempty it has exactly one additional
`/queue_reason_codes` row with the same source, downstream, producer,
consumer, effect, and USED disposition. The exact reason codes are
`used:g2d_terminal_outcome` and `used:g2d_terminal_reason` respectively. The
result artifact already names every required terminal queue artifact as an ABI
parent. These rows bind terminal state and reason influence and do not replace
the existing output/evidence rows. Missing, foreign, duplicate, reordered,
wrong-cell, or unnecessary reason rows fail closed. A no-child activation-gate
slot therefore changes its parent result through its real terminal queue
artifact without a synthetic child result or child-return causal row.

The rejected/blocked downstream terminal queue artifact names the validating
queue artifact as exact predecessor parent, and no dependent child invocation
occurs. Every `output_field` is an exact valid JSON Pointer into source
payload. Each causal ref `trace_refs` tuple is exactly source artifact ID,
downstream artifact ID, runtime trace ID. Reason prefixes follow current ABI
law: `USED -> used:`, `REJECTED -> rejected:`,
`IGNORED_WITH_REASON -> ignored:`, `BLOCKED_BY_GATE -> gate:`.

Counterfactual proof has two non-confusable axes and remains D5-only.

**G2-D profile-aware actual-artifact axis.** The wrapper first validates the
accepted baseline bundle and exact causal reference. The mutated source must be
the selected row's allowed source class, preserve transaction, Root, source
component, time envelope, and every non-target branch, change exactly the
valid JSON-Pointer field, and carry the content-derived mutated artifact ID
required by its G2-D profile. It creates no authority, permission, packet,
receipt, FinalOutput, DRS write, provider/model/network/connector call, or
effect. The wrapper reconstructs the expected consequence from actual typed
source and object families:

- `USED`: the accepted downstream semantic/object/artifact projection changes
  exactly as the row requires, and any expected content-derived downstream ID
  equals the rebuilt actual artifact ID.
- `IGNORED_WITH_REASON`: the advisory field is outside the accepted downstream
  semantic projection; downstream semantics and authority remain unchanged,
  and no diagnostic mutation becomes a runtime artifact.
- `REJECTED` or `BLOCKED_BY_GATE`: the dependent path or child admission stays
  rejected/blocked with unchanged authority. If no accepted downstream
  artifact exists, the expected downstream value is JSON null.

For `CHILD_ACTIVATION`, mutation of planned child ID, parent-slot artifact,
RUNNING state, slot relation, or downstream parent binding prevents accepted
child admission and yields JSON null downstream absence. For child-result
return rows, mutating result ID/output/evidence changes or blocks the t06
artifact; mutating outcome changes or blocks the exact t08-t12 terminal
mapping. For `CELL_TERMINAL_OUTCOME`, changing terminal state changes or blocks
the exact cell-result outcome, while changing nonempty queue reasons changes or
blocks the exact result public-reason projection. A no-child gate terminal
changes the parent result without fabricating a child result. Generic stable-ID
diagnostics remain non-runtime and D5-only.

**Generic stable-ID diagnostic axis.** The wrapper may call the existing
`validate_causal_counterfactual_v01` only with internal non-executable
diagnostic projections that satisfy its stable-ID precondition. Baseline and
mutated diagnostic source copies retain the baseline artifact ID and envelope
while differing only at the selected payload pointer. Baseline and mutated
diagnostic downstream copies retain the baseline downstream artifact ID and
envelope; their payload equality or inequality represents the already-derived
profile-aware disposition, and their authority projections remain byte-equal.
These copies are never inserted into the execution bundle, Stage D-C, runtime
trace, causal tuple, accepted ABI family, or release evidence and create no
accepted content-addressed runtime claim. When the profile-aware axis derives
no accepted downstream artifact, the generic validator is not called; the
wrapper proves exact absence itself. Actual changed-ID content-addressed
source/downstream artifacts are never passed directly to the generic validator.

The final `CAUSAL_COUNTERFACTUAL` report binds the Section 9 internal plain
projection. PASS names its exact content-derived identity; failure has a null
object ID and exact public/source reasons.

Invalid JSON Pointer, reason prefix, producer, consumer, source, downstream,
parent binding, index, disposition, decision effect, trace order, duplicate,
missing or extra mandatory row, or a fabricated ref for a non-artifact
internal field fails closed.

### 16.5 Noncyclic pre-bundle validation and final assembly

Report validation receives the explicit source context/binding, topology and
artifact, result and queue tuples, backpressure tuple, trace, final global
budget, parent-return decision, and root-result artifact. Stage validation
receives exact object/artifact families and applies this nullability:

| Stage | Runtime report | Report artifact | Active family |
|---|---|---|---|
| `STAGE_D_A` | `None` | `None` | validated G2-C family and topology artifact only |
| `STAGE_D_B` | `None` | `None` | D-A plus complete queue and result families |
| `STAGE_D_C` | exact required | exact required | D-B plus the one report family |

D2 may generically validate and record the D-A tuple. The public G2-D stage
validator first exists in D4 and revalidates D-A, D-B, and D-C from settled
bytes; no early D4 callable is created. ABI-profile validation likewise
receives explicit complete object/artifact families. Causal construction and
validation receive those families plus the exact Stage-D-C artifact tuple,
which is passed unchanged to `validate_causal_consumption_bundle_v01`.

The exact retained pre-bundle `validation_reports` tuple is:

1. one `SOURCE_CONTEXT_STRUCTURAL` report;
2. one `SOURCE_BINDING_AGAINST_G2C` report;
3. one `RuntimeTopologySeedV02` report;
4. one `TOPOLOGY_AGAINST_SOURCES` report;
5. every `FractalCellQueueEntryV02` report in exact queue build-log order;
6. every `SCOPE_PROJECTION_AGAINST_SOURCES` report in canonical child-slot
   order;
7. every `CELL_INPUT_AGAINST_SOURCES` report in cell-instantiation order;
8. every `CELL_RESULT_PRECONDITIONS` report in result postorder;
9. every `FractalCellResultV02` report in result postorder;
10. one `RUNTIME_REPORT_AGAINST_SOURCES` report;
11. `STAGE_D_A`;
12. `STAGE_D_B`;
13. `STAGE_D_C`.

Transient reports are consumed immediately and re-derived by
`COMPLETE_PROFILE`: structural policy, budget, source-binding, node, edge,
assignment, topology, scope-projection, cell-input, revise, partial-failure,
backpressure, trace, and runtime-report reports; `RESULT_PROPOSAL`;
`POST_VV_REPORT`; `GT_ADVISORY_REPORT`; `ABI_PROFILE`; and
`CAUSAL_CONSUMPTION`. External-only reports are `COMPLETE_PROFILE` and
`CAUSAL_COUNTERFACTUAL`. Retained, transient-rederived, and external-only
classes are exact, mutually exclusive, and collectively complete.

The exact RESULT_PROPOSAL, POST_VV_REPORT, and GT_ADVISORY_REPORT PASS tuple
supplied to each PARENT_RETURN occurrence is deterministic transient material,
not copied authority. The actual proposal/VV/GT dictionaries and typed child,
failure, and pre-terminal families remain bundle-retained. COMPLETE_PROFILE
independently reconstructs the same three canonical report bytes from those
retained objects and proves they equal the family used by signature 90.

Successful ABI and causal profile validation agree against the same Stage-D-C
facts without storing duplicate value-identical reports. Final normal assembly
is exact: build report and artifact; validate report; validate D-A/B/C;
validate ABI profile; build and validate causal refs; build the final execution
bundle exactly once; validate it; return `(bundle,
external COMPLETE_PROFILE PASS)`. Any earlier failure returns `(None,
first FAIL_CLOSED report)`; final complete-profile failure returns `(None,
COMPLETE_PROFILE FAIL_CLOSED)`. The external report is never inserted into the
same bundle it validates.

Counterfactual validation is D5 proof/diagnostic work after an accepted runtime
result. `run_fractal_runtime_v02` never calls it, it is not required to build a
normal bundle, and its report is external. The counterfactual validator remains
the sole causal API allowed to receive the accepted final bundle and performs
no provider, model, connector, network, or effect operation.

No provisional bundle, candidate replacement, empty causal tuple, dataclass
replacement, reverse dependency, or fixed point is permitted.

### 16.6 One Root law and one package mutation

`RootDecisionKernelV01` is read-only. There is no child Root, mini-Root,
FractalRoot, SuperRoot, or independent decision engine. Runtime evidence
returns upward; G2-D never creates FinalOutput.

The package facade is mutated exactly once in G2-D4. It exposes all 20 types,
110 module functions, and six Transition-profile functions as 136 direct,
object-identical attributes. Historical `hedgehog.kernel.__all__` remains
byte-, value-, and order-identical. No proxy, wrapper, lazy import, fallback,
alias family, or star export is added.

## 17. G2-A, G2-B, G2-C, and G2-E Bindings

G2-A remains `CLOSED_PASS` and read-only. G2-D carries
`downstream_action_packet_required` as a validated declaration only. It creates
no packet or permission. Old, expired, revoked, superseded, consumed, blocked,
failed, uncertain-closed, receipt, and prior-permission state cannot authorize
a topology or cell.

G2-B remains `CLOSED_PASS` and read-only. `memory_informed` may carry exact
validated context refs. DRS ranking, lineage, certificate, prior success, or
ReuseCertificate creates no instruction authority. Memory never widens scope
or capability.

G2-C remains `CLOSED_PASS` and read-only. G2-D uses its public contextual
validators and actual source objects. It duplicates no router, Root projection,
ABI profile, or Transition profile.

G2-E is deferred. G2-D does not implement dependency fingerprints,
affected-subgraph computation, selective recomputation, downstream
invalidation, continuous runtime, or delta runtime. The ordered node, edge,
assignment, lineage, evidence, trace, and parent refs are non-authoritative
forward seams only; they do not authorize G2-E behavior.

## 18. Historical PlanGraph and Fractal Donor Disposition

| Surface | Classification | Allowed donor value | Forbidden promotion |
|---|---|---|---|
| `hedgehog/fractal_cell_integration.py` | `LEGACY_PROOF_DONOR` | frozen result/trace ideas, bounded parent return | its PlanGraph binding, child Root language, or types as G2-D canon |
| `hedgehog/fractal_dag_executor.py` | `LEGACY_PROOF_DONOR` | deterministic dependency ordering and bounded execution ideas | PlanGraph as topology owner or provider-owned scheduling |
| `hedgehog/fractal_fulfillment.py` | `LEGACY_PROOF_DONOR` | local deterministic partial-result examples | effect, packet, permission, or final authority |
| `hedgehog/bounded_actor_contracts.py` | `LEGACY_PROOF_DONOR` | bounded actor envelope invariants | a second G2-D ABI or authority family |
| `hedgehog/post_vv.py` and `hedgehog/gt_validator.py` | `ACCEPTED_SHARED_KERNEL` additive D4 time seam plus historical validation donor | current result validation and advisory behavior with explicit injected-time extension | replacement validator, fallback, Root replacement, or child finalization |
| `hedgehog/root_orchestrator.py` | `LEGACY_PROOF_DONOR` for return flow | evidence that results return upward | canonical G2-D Root or module dependency |
| named Fractal/full-semantic demos and tests | `LEGACY_PROOF_DONOR` | regression evidence and deterministic fixtures | runtime imports, test-helper imports, unverified success assertions, or canonical IDs |
| PlanGraph schema/callers | `HISTORICAL_DOCUMENTATION` or `OUT_OF_SCOPE` | historical regression only | adapter, migration, cleanup, deletion, or compatibility slice |

The cleanest seam is confirmed as `hedgehog/kernel/fractal_runtime_v02.py`.
It does not depend on provider-owned PlanGraph.

## 19. Exact Path Ledger

### 19.1 Implementation create paths

| Path | Owning slice |
|---|---|
| `hedgehog/kernel/fractal_runtime_v02.py` | G2-D1 |
| `schemas/fractal_runtime_v02.schema.json` | G2-D1 |
| `tests/test_fractal_runtime_g2_d_v02.py` | G2-D1 |
| `demo/run_fractal_runtime_g2_d_v02.py` | G2-D5 |

### 19.2 Additive shared paths

| Path | Owning slice |
|---|---|
| `hedgehog/kernel/abi_v01.py` | G2-D2 |
| `schemas/kernel_artifact_v01.schema.json` | G2-D2 |
| `tests/test_kernel_abi_v01.py` | G2-D2 |
| `hedgehog/kernel/transition_registry_v01.py` | G2-D2 |
| `tests/test_transition_registry_v01.py` | G2-D2 |
| `hedgehog/kernel/__init__.py` | G2-D4, sole facade mutation |
| `hedgehog/post_vv.py` | G2-D4, additive explicit-time seam |
| `tests/test_post_vv_runtime.py` | G2-D4 |
| `hedgehog/gt_validator.py` | G2-D4, additive explicit-time seam |
| `tests/test_gt_validator_runtime.py` | G2-D4 |
| `demo/run_living_gauntlet_v01.py` | G2-D6 |
| `tests/test_living_gauntlet_v01_runner.py` | G2-D6 |
| `hedgehog/kernel/conformance_v01.py` | G2-D6 |
| `demo/run_kernel_conformance_v01.py` | G2-D6 |
| `tests/test_kernel_conformance_v01_runner.py` | G2-D6 |

### 19.3 Read-only consumers and donors

```text
hedgehog/kernel/execution_mode_router_v01.py
schemas/execution_mode_router_v01.schema.json
tests/test_execution_mode_router_g2_c_v01.py
demo/run_execution_mode_router_g2_c_v01.py
hedgehog/kernel/root_decision_v01.py
hedgehog/kernel/semantic_work_v01.py
hedgehog/kernel/trust_model_v01.py
hedgehog/kernel/integrity_replay_v01.py
hedgehog/kernel/effect_firewall_v01.py
hedgehog/action_commit_packet_v02.py
hedgehog/drs_semantic_address_v01.py
hedgehog/drs_memory_resolution_v01.py
hedgehog/reuse_certificate_v01.py
hedgehog/fractal_cell_integration.py
hedgehog/fractal_dag_executor.py
hedgehog/fractal_fulfillment.py
hedgehog/bounded_actor_contracts.py
hedgehog/root_orchestrator.py
all named historical Fractal demos and tests
```

Ledger arithmetic is exact: 4 create paths, 15 additive shared paths, 57
current read-only paths from the 80-path read register, and 10 closure-only
paths. The four Post V&V/GT runner tests added to the read register remain
read-only donors; only the two exact runtime tests above are additive paths.

### 19.4 Closure-only paths

```text
AGENTS.md
README.md
specs/machine_manifest_v0_25.json
release/current_status_overlay_v01.json
release/claim_to_evidence_index.md
release/current_limitations.md
release/current_release_notes.md
tests/test_repository_release_spine_v01.py
docs/audit_reports/auditor_fractal_runtime_g2_d_v02.log
docs/fractal_runtime_v0_2_g2_d_checkpoint_v01.md
```

Closure-only paths are forbidden during G2-D1 through G2-D6. Every unlisted
path is frozen. A discovered need outside this ledger stops the owning slice
for scope amendment.

## 20. Exact Six-Slice Implementation Plan

1. **G2-D1 - Canonical contracts, identities, schema, and reason registry.**
   Create 20 canonical dataclasses including `RuntimeTopologySeedV02`, the
   corrected static-template/runtime-instance field geometry, bottom-up
   result/failure/validation DAG, root/child cell derivation, exact mode
   node/edge/assignment/projection tables, planned-child field names, the
   21-field revise observation, event-complete budget signature, pre-state
   Transition signature, 34-target/30-stage registries, nonrecursive report
   self-validator, corrected contextual/run/pre-bundle signatures, 18 schema
   definitions, canonical causal-reference plain-material law, the queue
   builder's typed activation-parent, local-child-result, and
   `queue_reason_codes` inputs, four base lineage shapes,
   `CHILD_SLOT_INDEX_ROWS_V02`, corrected
   11-column `QUEUE_TRANSITION_INPUT_ROWS_V02`,
   `CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02`,
   `CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02`,
   `PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02`,
   `PARENT_RETURN_TYPED_INPUT_COMPONENTS_V02`, final signature-90 actual-family
   contract, valid gate-denial versus structural-failure boundary, fixed
   `parent_return_required=true`, immediate-parent sibling allocation basis,
   create-only cell debit, one-cell/one-root finalization matrix,
   allocated/final result/failure budget names, exact backpressure input/field
   derivation, typed trace/report contracts, preserved signatures and sole
   v0.1.10 signature-90 delta,
   the queue field and merge-input literal renames, appended
   `CELL_TERMINAL_OUTCOME` effect, 220 reasons, and
   74 structural public functions. No topology
   execution, ABI append, Transition profile, or package mutation.
2. **G2-D2 - G2-C binding and deterministic topology construction.** Add the
   complete selected profile/capability/cost/policy/scope source binding,
   source-derived policy/context, ten-edge full-fractal topology, exact
   root/leaf projections including `FAN_IN_CHILD_SLOT_RETURNS_1_2`, and
   validated non-authoritative topology candidate.
   Append three ABI literals and the complete pure 17-rule Transition profile;
   evaluate t01 against actual G2-C Root commit, then project the topology
   artifact. The cumulative surface is 81 module and six Transition functions.
   No queue consumption, cell execution, or package facade.
3. **G2-D3 - Queue, bounds, budgets, scope, and backpressure.** Add the exact
   planned root child IDs before admission, generic t02 decisions, initial
   inputs before readiness, activation precheck, allocation/scope candidate
   validation, ACTIVATE/CELL_CREATE commit, parent-slot artifact lineage,
   pre-state t03-t12 decisions, decision -> budget -> queue -> artifact
   construction, occurrence-aligned semantic decisions, immutable per-node
   predecessor chains, immediate-parent sibling allocation basis, complete
   context/owner/nullability budget matrix, CELL_CREATE-only debit, unique
   PARENT_RETURN completion, child-local FINAL/global ACTIVE pairing, immediate
   zero-delta aggregate, the exact one-based label/zero-based child-index bridge, complete
   t02-t12 observation/reason/nullability laws, successful child-result and
   no-child activation-gate returns into the exact parent FRACTAL_CELL slot,
   slot-normalized FRACTAL_MERGE with no synthetic result, exact
   `queue_reason_codes`, six queue ABI parent forms, sequential latest-
   settled admission, READY reservations, bounded one-state-per-round
   backpressure, unchanged-defer suppression, one append-only queue-only log,
   one budget log, and one interleaved runtime ABI artifact log with no re-sort,
   child-result return/terminal causal rows, monotonicity, deterministic
   admission/defer precedence, no scheduler spin, and full-fractal-only expansion. Child initial
   construction receives the exact parent-slot artifact and successors
   preserve its lineage. Signature 90 rejects every nonempty/non-null PARENT_RETURN
   family on non-PARENT_RETURN calls; its actual-family branch remains
   unavailable until D4. The cumulative surface is 90 module and six Transition
   functions. D3 freezes and implements queue-side return mechanics but does
   not construct results, reports, or invoke t13-t17.
4. **G2-D4 - Results, deterministic validation, causal consumption, remaining
   ABI, and sole facade mutation.** Add revise/no-progress, retry=false,
   pre-decision revise observation, t07 -> budget -> queue order, bottom-up
   failure/result construction with exact allocated/final/global budgets and
   actual-only child/failure cardinality, four ResultProposal/Post V&V/GT
   helpers, pre-Post-V&V proposal prefix, complete terminal pre-result tuple,
   exact PARENT_RETURN proposal-status mapping from the actual signature-90
   family, independent RESULT_PROPOSAL/POST_VV_REPORT/GT_ADVISORY_REPORT PASS
   reconstruction, KT seams, context-unique GT IDs, raw proposal/VV/GT bundle
   storage, node/cell outcome separation, corrected pre-Root
   lifecycles, root-result report projection, t13-t17, result/report artifacts,
   exact contextual scope/input/proposal validators, exact cross-artifact
   causal rows including `CELL_TERMINAL_OUTCOME` state/reason rows and canonical
   plain profile material, explicit pre-bundle
   report/stage/ABI/causal validation from the typed three-log runtime trace,
   typed report parent-return derivation, Stage D-B
   interleaved artifact-build order, one
   final bundle build, external COMPLETE_PROFILE validation and corrected run
   result pair, complete ABI partitions and Stage D-A/B/C, all 110 module and
   six Transition functions, 136 direct attributes, and immutable `__all__`.
   Normal runtime performs no counterfactual call. Root remains unmodified.
5. **G2-D5 - Deterministic two-domain proof and complete negative matrix.**
   Create the public runner, use actual source builders, prove all 72 cases,
   repeated run-pair byte equality, identity/postorder/template/queue/budget/
   time/ABI/causal/substitution matrices, execute profile-aware actual-artifact
   counterfactual proof calls only against accepted bundles, optionally apply
   the compatible generic stable-ID diagnostic only to non-runtime copies, and
   prove zero operations. Counterfactual identity uses canonical causal plain
   material and JSON-null downstream absence.
6. **G2-D6 - Living and Conformance integration.** Append Living v1.4,
   Conformance v0.5, and Conformance runner v0.4 while preserving every
   historical prefix and zero-operation boundary.

There is no seventh slice and no adapter, migration, caller migration,
cleanup, compatibility, or G2-E slice. Each slice requires separate owner
authorization after this preflight is accepted and committed.

## 21. Exact Validation Geometry

There are exactly 20 cumulative validation groups:

| # | Group | Owner | Positive and negative obligation |
|---:|---|---|---|
| 1 | `static_surface_schema_import` | D1 | AST, schema, UTF-8, exact staged public signatures/availability, no stubs, import direction and path ownership; reject forbidden imports, speculative attributes, or extra paths. |
| 2 | `canonical_types_fields_enums` | D1 | Exact 20 types and field counts, final signature 90, 11-column queue-input table, `PARENT_RETURN_TYPED_INPUT_COMPONENTS_V02`, valid-denial row, `queue_reason_codes`, fixed `parent_return_required=true`, 34 targets, 30 stages, and unchanged reason/count geometry. |
| 3 | `acyclic_identity_and_serialization` | D1 | Exact 18 identities and acyclic successful-child or valid no-child gate return -> slot-normalized merge -> actual proposal/VV/GT family and reconstructed reports -> PARENT_RETURN -> complete-terminal pre-result -> result/causal/final-bundle DAG; reject synthetic results, reverse refs, provisional identities, fixed points, or raw-reference cycles. |
| 4 | `structural_validators_and_reasons` | D1 | Total validators, exact target/ID/stage maps, nonrecursive self-validation, no copied PASS/status/reason, exact valid-denial versus corruption boundary, and 220 unique reasons; structural corruption returns FAIL_CLOSED and creates no accepted terminal surface. |
| 5 | `complete_g2c_source_context` | D2 | Actual complete G2-C profile; reject missing, copied, foreign, or substituted sources. |
| 6 | `route_eligibility_consumption` | D2 | Exact topology class; reject shortcuts, terminals, direct Root decision, ID-only input. |
| 7 | `mode_topology_profiles` | D2 | Exact five node/edge/assignment tables using `FAN_IN_CHILD_SLOT_RETURNS_1_2`, root/leaf projections, ten-edge full-fractal graph, and exact human slot ordinal/tuple position/canonical index bridge; reject unexecutable, missing, extra, reordered, substituted, inferred, or implicit rows. |
| 8 | `topology_identity_lineage` | D2 | Static input derivation, assignment trace, source-bound policy and settled planned child IDs; planning never claims activation; validated candidate -> t01 -> topology artifact remains exact. |
| 9 | `queue_state_predecessor_and_order` | D3 | Root input/planned IDs, exact queue-reason law, 11-column t02-t12 inputs, parent-return family nullability, exact observed/reason reconstruction, successful child and valid no-child returns, six ABI forms, latest-settled order, READY reservations, and one queue log. |
| 10 | `bounds_and_budget` | D3 | Immediate-parent sibling basis, common initial queue epoch, zero-based slots, latest parent/global capacity, create-only debit, paired accounting, unique finalization, and exact valid budget denial versus malformed owner/scope/state/event/predecessor/counter FAIL_CLOSED geometry. |
| 11 | `scope_capability_ttl_lineage` | D3 | Exact child monotonicity with actual parent input and all budget objects; reject ID-only proof or scope/capability/TTL/forbidden/lineage widening. |
| 12 | `recursion_and_backpressure` | D3 | Full-fractal-only recursion; running plus READY capacity; deterministic state-class order; one bounded backpressure state per round; ordinary dependency wait; BLOCKED precedence; unchanged-defer suppression; and no spin. |
| 13 | `revise_retry_and_no_progress` | D4 | Retry=false; observation contains before budgets only and precedes t07; t07 precedes paired budgets and READY queue; reject future budget IDs, hidden retry, reset, or caller terminal choice. |
| 14 | `partial_failure_and_parent_return` | D4 | Actual child completion precedes result; failures name actual child results only; no-child slots retain terminal evidence with no synthetic result/failure; immediate aggregate, sibling/postorder, and required-slot laws remain exact. |
| 15 | `transition_abi_facade_and_stage_bundles` | D4 | Queue ABI field rename, success/no-child parent-form selection, terminal queue parents of results, typed logs and Stage D-B, six parent forms, exact 32/31/32/42 partitions, root-only return, and 136 attrs. |
| 16 | `deterministic_post_vv_gt_time_boundary` | D4 | Actual proposal/VV/GT objects, exact pre-Post-V&V and child/failure tuples, independently reconstructed three-report PASS family, source KT, five status mappings, complete terminals, safe rejection, defaults, and no copied ID/PASS/status authority. |
| 17 | `causal_consumption_and_counterfactuals` | D4 | COMPLETE_PROFILE rederives typed equality; accepted terminal queues alone create `CELL_TERMINAL_OUTCOME` rows; structural corruption creates no terminal, causal row, merge input, or bundle; existing child-return rows and D5-only counterfactual remain acyclic. |
| 18 | `two_domain_positive_determinism` | D5 | Exact 36 primary deterministic/constructive cases, including only ten domain-positive modes, with repeated values/bytes/IDs. |
| 19 | `complete_negative_and_zero_operation` | D5 | Exact 36 primary fail-closed cases, embedded negative mutations, and all authority/effect counters zero across 72 cases. |
| 20 | `living_conformance_final_profile` | D6 | Version appends, historical prefixes, new act/category/probes/refs, corrected profile and zero effects. |

Activation is cumulative: D1 activates groups 1-4; D2 adds 5-8; D3 adds
9-12; D4 adds 13-17; D5 adds 18-19; D6 adds 20. No later slice weakens an
earlier group.

Future validation commands are exact and use
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.` with `.venv/bin/python`. Static checks
precede pytest in every slice. No full repository pytest is authorized.

- D1-D3: run the owning `-k d1`, `-k d2`, or `-k d3` selection, then the
  complete `tests/test_fractal_runtime_g2_d_v02.py` once after executable bytes
  settle. D1 also parses and Draft-2020-12-validates the new schema.
- D4: run exact D4 selectors in the new test, exact new explicit-time nodes in
  `tests/test_post_vv_runtime.py` and `tests/test_gt_validator_runtime.py`, and
  exact G2-D nodes in Kernel ABI and Transition tests. After executable bytes
  settle, run each complete affected file at most once. No Root test is run
  unless static import/hash inspection demonstrates a real dependency.

The exact new explicit-time node IDs are:

```text
tests/test_post_vv_runtime.py::test_g2d_explicit_checked_at_is_used_exactly_v02
tests/test_post_vv_runtime.py::test_g2d_batch_post_vv_uses_one_explicit_time_v02
tests/test_post_vv_runtime.py::test_g2d_post_vv_default_remains_callable_v02
tests/test_post_vv_runtime.py::test_g2d_post_vv_invalid_explicit_time_fails_closed_v02
tests/test_post_vv_runtime.py::test_g2d_post_vv_explicit_time_avoids_wall_clock_v02
tests/test_post_vv_runtime.py::test_g2d_post_vv_safe_rejection_uses_explicit_time_v02
tests/test_gt_validator_runtime.py::test_g2d_explicit_created_at_is_used_exactly_v02
tests/test_gt_validator_runtime.py::test_g2d_gt_default_remains_callable_v02
tests/test_gt_validator_runtime.py::test_g2d_gt_invalid_explicit_time_fails_closed_v02
tests/test_gt_validator_runtime.py::test_g2d_gt_explicit_time_avoids_wall_clock_v02
tests/test_gt_validator_runtime.py::test_g2d_gt_explicit_ids_are_proposal_bound_v02
tests/test_gt_validator_runtime.py::test_g2d_gt_explicit_single_report_required_v02
tests/test_gt_validator_runtime.py::test_g2d_gt_historical_revise_no_update_ids_unchanged_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_build_fractal_cell_result_proposal_contract_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_validate_fractal_cell_result_proposal_contract_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_validate_fractal_post_vv_report_contract_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_validate_fractal_gt_advisory_contract_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_post_vv_gt_explicit_time_repeated_bytes_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_context_unique_report_ref_alignment_v02
tests/test_fractal_runtime_g2_d_v02.py::test_d4_root_report_status_and_outcome_projection_v02
```
- D5: run `python -m demo.run_fractal_runtime_g2_d_v02` twice and compare the
  exact accepted `(bundle,external COMPLETE_PROFILE report)` projection bytes;
  execute the profile-aware actual-artifact counterfactual proof only after
  that accepted result; invoke the generic validator only for a compatible
  non-runtime stable-ID diagnostic with an accepted downstream; then run `-k
  d5` and the complete new G2-D test file once. Bounded
  compatibility selectors cover the public G2-C contextual validators, G2-A
  history fence, G2-B context law, ABI, Transition, Root, SemanticWork, trust,
  and integrity without replaying historical runners.
- D6: do not separately invoke Living or Conformance runners. Run the complete
  Living test file once and complete Conformance test file once; their tests
  own repeated collection/render validation. Each is expected to exceed 20
  minutes because the committed files already carry large historical prefix
  matrices. This cost is called out in advance and neither file is duplicated
  inside another cumulative suite in the same hop.

All test selections, exact nodes, and protected hashes must be restated in the
owner authorization for the relevant slice. No pytest function count is
frozen.

## 22. Two-Domain Deterministic Proof

Domains remain exactly:

```text
TRAVEL_POLICY_INFORMATION
WAREHOUSE_MAINTENANCE_INFORMATION
```

The canonical proof has exactly 72 ordered cases:

| # | Case ID | Expected result |
|---:|---|---|
| 1 | `g2d_case:travel:memory_informed:v02` | non-recursive `COMPLETED` |
| 2 | `g2d_case:travel:local_slm:v02` | non-recursive `COMPLETED` |
| 3 | `g2d_case:travel:cloud_llm_narrow:v02` | narrowed non-recursive `COMPLETED` |
| 4 | `g2d_case:travel:full_semantic:v02` | non-recursive multi-actor `COMPLETED` |
| 5 | `g2d_case:travel:full_fractal:v02` | two bounded children, `COMPLETED` |
| 6 | `g2d_case:warehouse:memory_informed:v02` | non-recursive `COMPLETED` |
| 7 | `g2d_case:warehouse:local_slm:v02` | non-recursive `COMPLETED` |
| 8 | `g2d_case:warehouse:cloud_llm:v02` | non-recursive `COMPLETED` |
| 9 | `g2d_case:warehouse:full_semantic:v02` | non-recursive multi-actor `COMPLETED` |
| 10 | `g2d_case:warehouse:full_fractal:v02` | two bounded children, `COMPLETED` |
| 11 | `g2d_case:negative:deterministic_shortcut:v02` | `FAIL_CLOSED`, shortcut forbidden |
| 12 | `g2d_case:negative:sealed_replay_shortcut:v02` | `FAIL_CLOSED`, shortcut forbidden |
| 13 | `g2d_case:negative:direct_reuse_shortcut:v02` | `FAIL_CLOSED`, shortcut forbidden |
| 14 | `g2d_case:negative:blocked_terminal:v02` | `FAIL_CLOSED`, terminal forbidden |
| 15 | `g2d_case:negative:needs_user_terminal:v02` | `FAIL_CLOSED`, terminal forbidden |
| 16 | `g2d_case:negative:root_reject_terminal:v02` | `FAIL_CLOSED`, terminal forbidden |
| 17 | `g2d_case:negative:direct_root_decision:v02` | `FAIL_CLOSED`, direct bypass |
| 18 | `g2d_case:negative:route_substitution:v02` | `FAIL_CLOSED`, artifact substitution |
| 19 | `g2d_case:negative:cross_domain_source:v02` | `FAIL_CLOSED`, domain mismatch |
| 20 | `g2d_case:negative:foreign_id_only:v02` | `FAIL_CLOSED`, contextual mismatch |
| 21 | `g2d_case:negative:scope_widening:v02` | `FAIL_CLOSED` |
| 22 | `g2d_case:negative:capability_widening:v02` | `FAIL_CLOSED` |
| 23 | `g2d_case:negative:fractal_capability_missing:v02` | `FAIL_CLOSED`, no fallback |
| 24 | `g2d_case:negative:mode_upgrade:v02` | `FAIL_CLOSED` |
| 25 | `g2d_case:negative:mode_downgrade:v02` | `FAIL_CLOSED` |
| 26 | `g2d_case:negative:g2b_instruction_authority:v02` | `FAIL_CLOSED` |
| 27 | `g2d_case:negative:g2a_history_authority:v02` | `FAIL_CLOSED` |
| 28 | `g2d_case:negative:depth_overflow:v02` | parameterized depth 0/1/2 accepted boundary and attempted depth 3 `BLOCKED` |
| 29 | `g2d_case:negative:fan_out_overflow:v02` | `BLOCKED` |
| 30 | `g2d_case:negative:total_cell_overflow:v02` | exact 21-cell structural boundary; allocation/ACTIVATE uncounted; debit only at accepted CELL_CREATE; attempted 22nd cell `BLOCKED` |
| 31 | `g2d_case:parallelism_backpressure:v02` | latest-settled sequential admission, READY reservations, one bounded state per round, visible `PENDING`, no drop |
| 32 | `g2d_case:negative:token_budget_overflow:v02` | `BLOCKED` |
| 33 | `g2d_case:negative:time_budget_overflow:v02` | `BLOCKED` |
| 34 | `g2d_case:negative:provider_budget_overflow:v02` | `BLOCKED` |
| 35 | `g2d_case:negative:scope_budget_monotonic_matrix:v02` | scope/TTL/forbidden/budget/borrowing mutations all `FAIL_CLOSED` |
| 36 | `g2d_case:negative:revise_count_overflow:v02` | `DEADEND` |
| 37 | `g2d_case:no_progress_deadend:v02` | `DEADEND` after two non-positive revisions |
| 38 | `g2d_case:resolvable_missing_input:v02` | `NEEDS_USER` |
| 39 | `g2d_case:required_child_partial:v02` | invoked child result is `DEGRADED`; actual failure record and safe sibling evidence are preserved |
| 40 | `g2d_case:required_child_hard_failure:v02` | invoked BLOCKED result and structurally valid no-child policy/scope/authority/budget denial are bounded BLOCKED paths; identity, lineage, artifact, or malformed-budget corruption is FAIL_CLOSED with no slot terminal |
| 41 | `g2d_case:negative:child_authority_claims:v02` | Root/FinalOutput/permission/packet/receipt/effect claims all `FAIL_CLOSED` |
| 42 | `g2d_case:repeated_canonical_equality:v02` | two reports and rendered bytes exactly equal |
| 43 | `g2d_case:identity:acyclic_graph_rebuild:v02` | invoked-child or valid no-child return -> slot merge -> actual proposal/VV/GT and exact reconstructed reports -> PARENT_RETURN -> complete-terminal validation -> result/causal/final bundle remains acyclic |
| 44 | `g2d_case:negative:queue_predecessor_substitution:v02` | foreign, missing, duplicated, reordered, or skipped predecessor entry/artifact fails closed |
| 45 | `g2d_case:deterministic:post_vv_gt_injected_time:v02` | two explicit-time Post V&V/GT paths are value-, ID-, and byte-identical; no wall clock |
| 46 | `g2d_case:causal:used_field_counterfactual:v02` | valid typed operational mutation changes the expected topology/result/report artifact and `USED` ref |
| 47 | `g2d_case:causal:blocked_and_ignored_dispositions:v02` | invalid mutation blocks child invocation with `BLOCKED_BY_GATE`; unused advisory leaves the non-executable generic counterfactual downstream identity unchanged with `IGNORED_WITH_REASON` |
| 48 | `g2d_case:identity:child_result_partial_failure_postorder:v02` | exact actual-child allocated/final/global lineage and copied failure budgets in postorder; no-child gate slots fabricate no failure record; invalid refs fail closed |
| 49 | `g2d_case:identity:pre_result_validation_no_cycle:v02` | pre-Post-V&V tuple -> proposal validation -> VV validation -> GT validation -> PARENT_RETURN decision -> complete-terminal validation -> result order is exact and cycle-free |
| 50 | `g2d_case:runtime:node_work_queue_cell_aggregation:v02` | two terminal slot returns always reach merge while zero, one, or two child results are case-valid; queue/budget/runtime-ABI logs and counts remain exact |
| 51 | `g2d_case:runtime:five_mode_exact_template_rows:v02` | every exact node, edge, assignment, and projection row rebuilds; one row mutation changes identity and fails contextual validation |
| 52 | `g2d_case:source:selected_profile_capability_scope_binding:v02` | selected feasibility/profile/cost/capability/policy/scope values rebuild from actual G2-C sources; every substitution fails closed |
| 53 | `g2d_case:budget:allocation_predecessor_debit_matrix:v02` | valid budget denial is distinct from malformed budget identity/state/event/predecessor/counter geometry; allocation, create-only debit, finalization, pairing, reserve/release/revise, and overflow remain exact |
| 54 | `g2d_case:validation:resultproposal_postvv_gt_outcome_matrix:v02` | actual proposal/VV/GT objects and exact independent three-report reconstruction drive the five PARENT_RETURN mappings with KT and no copied PASS authority |
| 55 | `g2d_case:transition:root_only_parent_return:v02` | fixed return flag and exactly one root/global FINAL before root-only t13-t17; children aggregate upward and cannot enter t13-t17 |
| 56 | `g2d_case:abi:complete_field_partition_and_trace:v02` | queue ABI reason-field rename, invoked/no-child parent-form selection, typed trace, six forms, and exact Stage D-B refs preserve 32/31/32/42 partitions |
| 57 | `g2d_case:causal:exact_pointer_reason_bundle:v02` | accepted terminal queues create exact CELL_TERMINAL_OUTCOME rows; structural corruption creates none; activation/child-return rows and D5-only diagnostics remain exact |
| 58 | `g2d_case:queue:backpressure_precedence:v02` | READY reservations, one state per round, unchanged t03 suppression; dependency wait stays ordinary PENDING; budget exhaustion blocks; no drop/reorder |
| 59 | `g2d_case:identity:policy_profile_separation:v02` | fixed profile and source-bound policy hash rebuild; identity/profile substitution fails closed |
| 60 | `g2d_case:runtime:full_fractal_leaf_edge_projection:v02` | root edges 0-6; leaves `(0,4,5,6)`/`(7,8,9)`; slots 1/2 map to indexes 0/1; FRACTAL_MERGE consumes slot returns rather than assuming two child results |
| 61 | `g2d_case:budget:cell_global_event_pairing:v02` | immediate-parent basis, child-local FINAL/global ACTIVE completion pair, immediate zero-delta aggregate, create-only debit, start/release/revise deltas, and stale/missing/forged pair failures |
| 62 | `g2d_case:abi:pre_root_lifecycle_boundary:v02` | no G2-D result/report uses Root-reviewed/accepted/rejected lifecycle; NEEDS_USER and DEADEND remain VALIDATED advisory artifacts returned toward Root |
| 63 | `g2d_case:validation:context_unique_gt_report_ids:v02` | explicit accepted/revise/no-update GT IDs are proposal-bound and unique; historical defaults unchanged; result refs rebuild |
| 64 | `g2d_case:validation:pass_none_stage_contract:v02` | exact 34-target/30-stage map and canonical causal-profile identity from Stage-D-C IDs plus the complete plain causal list; PASS requires NONE and exact ID/nullability; FAIL_CLOSED requires real stage/reason and null object ID |
| 65 | `g2d_case:queue:instance_snapshot_round_and_blocked_reason:v02` | exact round/state order, bounded admission, queue-reason laws, and proof that no copied queue reason or proposal status selects a terminal rule |
| 66 | `g2d_case:runtime:child_slot_input_node_outcome_order:v02` | successful child result returns before merge; structurally valid denied activation terminalizes its exact slot without child invocation, and merge still executes |
| 67 | `g2d_case:validation:root_result_report_and_slice_surface:v02` | exact `(bundle_or_none,terminal_report)` return with external COMPLETE_PROFILE; root owns outcome/return; staged 74/81/90/110 surfaces have no stubs |
| 68 | `g2d_case:budget:typed_event_and_child_allocation_context:v02` | two-child runtime and isolated four-child structural quotient/remainder share one immutable immediate-parent sibling basis; no implicit projection, recompute, borrow, raw ref, or wrong slot |
| 69 | `g2d_case:runtime:planned_child_activation_boundary:v02` | planned ID remains uncounted; valid denied precheck follows bounded t06/t10-t12 return, while malformed candidate geometry fails closed before any terminal successor |
| 70 | `g2d_case:transition:prestate_decision_budget_queue_order:v02` | signature 90 receives the actual typed PARENT_RETURN family; decision precedes budget/queue/artifact construction and no post-hoc status mapping exists |
| 71 | `g2d_case:revise:observation_before_t07_and_budget:v02` | observation has before budgets only; observation -> t07 -> paired REVISE budgets -> READY is exact; future ID, circular decision, wrong debit, or event mismatch fails closed |
| 72 | `g2d_case:bundle:prebundle_validation_causal_final_assembly:v02` | final bundle equality proves the exact retained proposal/VV/GT and three-report family used by PARENT_RETURN, terminal causal rows, actual-only children, and external COMPLETE_PROFILE |

Cases use actual public G2-C source builders and validators. No test helper,
donor-private function, fixture-written identity, unverified success assertion, or historical
output is accepted. Every selected RouteEligibility, topology, node, edge,
assignment, budget, queue, Transition, ABI artifact, result, trace, and report
identity is rebuilt.

Cases 1-10 are the only domain-positive matrix. Group 18 owns cases 1-10, 42,
43, 45, 46, 48-57, 59-61, 63, 64, and 66-72: 36 primary
deterministic/constructive rows.
Group 19 owns cases 11-41, 44, 47, 58, 62, and 65: 36 primary fail-closed
rows. Embedded negative mutations remain inside their owning case and do not
change the primary count. Guardian cases 68-72 are constructibility rows, not
additional domain-positive modes; 36 + 36 = 72.

All cases derive exact zero counters for provider, model, network, connector,
external DRS, packet, permission, receipt, FinalOutput, DRS write, authority,
and real-world effect. Positive cases have `topology_created_count=1`; that is
reported separately and is never treated as an effect.

## 23. Living Gauntlet and Kernel Conformance Plan

Append-only versions are:

```text
Living Gauntlet: v1.3 -> v1.4
Kernel Conformance: v0.4 -> v0.5
Kernel Conformance runner: v0.3 -> v0.4
```

Living appends act ID `fractal_runtime` at position 17. Its source is
`demo.run_fractal_runtime_g2_d_v02` symbol
`collect_fractal_runtime_g2_d_v02`. It adds
`fractal_runtime_execution_count=1`. The historical 16-act prefix is exact.

Conformance appends category `FractalRuntimeConformance` at position 14 with
these exact check IDs:

```text
policy_identity_and_staged_surface
executable_templates_and_child_activation
queue_input_outcome_and_result_order
paired_budget_events_and_backpressure
resultproposal_unique_gt_kt_validation
pre_root_four_artifact_abi_partitions
transition_profile_and_root_only_report
causal_pointer_reason_and_root_outcome
two_domain_seventy_two_case_boundary
zero_authority_and_operations
```

It appends active ref `fractal_runtime` at position 16 and these ten probes:

```text
fractal_runtime_report_identity_forgery
fractal_runtime_route_eligibility_substitution
fractal_runtime_direct_root_decision_bypass
fractal_runtime_mode_profile_forgery
fractal_runtime_scope_budget_widening
fractal_runtime_queue_transition_forgery
fractal_runtime_recursive_capability_forgery
fractal_runtime_no_progress_forgery
fractal_runtime_child_authority_forgery
fractal_runtime_zero_operation_forgery
```

Final geometry is 17 Living acts, 14/14 Conformance categories, unchanged 2/2
historical domains, 50/50 negative probes, and 16 active refs. Existing acts,
categories, domains, probes, refs, render lines, identities, and counters remain
exact prefixes. G2-D6 consumes the validated D5 report; it does not reconstruct
the 72 cases or fabricate PASS. The ten G2-D probe IDs remain exact. The ten
checks collectively cover successful invoked-child and no-child FRACTAL_CELL
terminal branches; exact activation-gate terminal mapping; state-specific
`queue_reason_codes`; slot-normalized FRACTAL_MERGE; no synthetic child result
or failure record; actual-only ordered child results; pre-Post-V&V versus
complete terminal tuples; exact PARENT_RETURN proposal-status mapping;
actual signature-90 proposal/VV/GT typed inputs; independently reconstructed
RESULT_PROPOSAL, POST_VV_REPORT, and GT_ADVISORY_REPORT PASS reports; valid
gate denial versus structural corruption with no copied PASS/status/reason;
`CELL_TERMINAL_OUTCOME` causal rows only for accepted terminals; the existing
six queue ABI parent forms;
immediate-parent allocation and create-only debit; unique finalization and
zero-delta aggregate; bounded latest-settled admission; exact queue, budget, and
runtime-ABI logs; typed trace/report and Stage D-B ordering; fixed
`parent_return_required=true` with root-only t13-t17; exact
`(bundle_or_none,terminal_report)` surface; one final bundle and external
COMPLETE_PROFILE; D5-only counterfactual axes; four-artifact partitions; exact
72-case evidence; and zero operations. Existing policy, topology,
lifecycle, GT, report, and causal boundaries remain covered across those same
ten IDs. No eleventh check, category, or probe is added. G2-D6 consumes the
validated D5 result pair and report and does not reconstruct the 72 cases.

## 24. Audit, Checkpoint, and Closure Law

After separately authorized and committed G2-D1 through G2-D6:

1. perform one independent read-only non-repairing G2-D audit;
2. commit the accepted audit separately;
3. perform a separately authorized checkpoint and current-status sync;
4. mark G2-D `CLOSED_PASS` only if audit and closure guards pass;
5. keep Gate 2 `NOT_CLOSED`;
6. set G2-E to `NEXT / NOT_STARTED` without authorizing it.

No implementation slice self-closes G2-D. Closure surfaces, audit, checkpoint,
release notes, status overlay, manifest, README, and AGENTS are not
implementation paths.

## 25. Current Non-Claims and Limitations

- G2-D implementation is not authorized and not started.
- Gate 2 is not closed.
- G2-E and G2-F are not started.
- Public release, RC2, production readiness, production security
  certification, and production distributed runtime are not claimed.
- Live provider and external connector execution are not claimed.
- Physical QPU use and quantum implementation are not claimed or started.
- RuntimeExecutionTopology is not authority.
- A child cell is not Root; a child result is not FinalOutput.
- Topology creates no permission, packet, receipt, DRS write, FinalOutput, or
  effect.
- The deterministic proof performs zero provider, model, network, connector,
  external-DRS, packet, permission, receipt, FinalOutput, DRS-write,
  authority, and real-world-effect operations.
- Real-world effects remain zero.
- R-IP1 and the future Quantum Roadmap do not block, authorize, enlarge, or
  redesign G2-D through G2-F.
- No publication is allowed before Gate 6 closure and separate owner approval.

The preflight does not prove production scheduling, distributed execution,
provider execution, persistence, fault tolerance, security certification, or
performance. The deterministic reference proof is local, in-memory, bounded,
and zero-effect.

## 26. Final Authorization State

This planning artifact is guardian ACCEPTED under the express owner-authorized
acceptance ruling for v0.1.10 after BI-BJ correction and static validation. It
is ready only for an owner-controlled preflight commit. Acceptance is not
self-issued and authorizes no G2-D1 implementation, code, schema, test, runner,
facade, audit, checkpoint, release, G2-E, G2-F, or quantum work. G2-D and Gate 2
remain open.

```text
G2D_PREFLIGHT_DOCUMENT_REVISION=v0.1.10
G2D_PREFLIGHT_GUARDIAN_STATUS=ACCEPTED
G2D_PREFLIGHT_ACCEPTED=true
G2D_IMPLEMENTATION_AUTHORIZED=false
G2D_IMPLEMENTATION_STARTED=false
EXACT_G2D_SLICE_COUNT=6
TOTAL_G2D_TYPE_COUNT=20
SERIALIZED_IDENTITY_TYPE_COUNT=18
RUNTIME_ONLY_CONTEXT_TYPE_COUNT=2
SCHEMA_DEFINITION_COUNT=18
FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT=110
FRACTAL_RUNTIME_TRANSITION_PUBLIC_FUNCTION_COUNT=6
TOTAL_G2D_PUBLIC_FUNCTION_COUNT=116
PUBLIC_G2D_REASON_COUNT=220
VALIDATION_TARGET_COUNT=34
FAILURE_STAGE_COUNT=30
DIRECT_PACKAGE_G2D_ATTRIBUTE_COUNT=136
EXACT_VALIDATION_GROUP_COUNT=20
CANONICAL_TWO_DOMAIN_CASE_COUNT=72
TRANSITION_PROFILE_RULE_COUNT=17
ABI_G2D_ARTIFACT_CLASS_COUNT=4
ABI_ARTIFACT_LITERAL_APPEND_COUNT=3
D1_MODULE_PUBLIC_FUNCTION_COUNT=74
D2_MODULE_PUBLIC_FUNCTION_COUNT=81
D3_MODULE_PUBLIC_FUNCTION_COUNT=90
D4_MODULE_PUBLIC_FUNCTION_COUNT=110
PARENT_RETURN_TYPED_INPUT_FAMILY_FROZEN=true
PARENT_RETURN_REPORT_RECONSTRUCTION_FROZEN=true
COPIED_PARENT_RETURN_PASS_FORBIDDEN=true
VALID_GATE_DENIAL_STRUCTURAL_FAILURE_SEPARATION_FROZEN=true
STRUCTURAL_CORRUPTION_CREATES_TERMINAL_SLOT=false
CHILD_ACTIVATION_GATE_TERMINAL_PATH_FROZEN=true
FRACTAL_CELL_RESULT_OR_GATE_BRANCH_FROZEN=true
QUEUE_REASON_SURFACE_FROZEN=true
SLOT_NORMALIZED_FRACTAL_MERGE_FROZEN=true
SYNTHETIC_UNINSTANTIATED_CHILD_RESULT_FORBIDDEN=true
ACTUAL_ONLY_CHILD_RESULT_CARDINALITY_FROZEN=true
PRE_POST_VV_PROPOSAL_INPUT_FROZEN=true
COMPLETE_TERMINAL_RESULT_INPUT_FROZEN=true
PARENT_RETURN_PROPOSAL_STATUS_MAPPING_FROZEN=true
TERMINAL_QUEUE_OUTCOME_CAUSAL_ROWS_REQUIRED=true
CAUSAL_REF_SYNTHETIC_ID_FORBIDDEN=true
CAUSAL_PROFILE_CANONICAL_PLAIN_MATERIAL_FROZEN=true
COUNTERFACTUAL_JSON_NULL_ABSENCE_FROZEN=true
CHILD_QUEUE_BUILDER_ACTIVATION_PARENT_FROZEN=true
CHILD_QUEUE_LINEAGE_VARIANTS_FROZEN=true
CHILD_QUEUE_PARENT_SLOT_ABI_LINEAGE_FROZEN=true
BUDGET_CONTEXT_INPUT_ROLE_FROZEN=true
ROOT_GLOBAL_BUDGET_OWNER_FROZEN=true
CHILD_LOCAL_BUDGET_OWNER_FROZEN=true
BUDGET_OPTIONAL_INPUT_NULLABILITY_FROZEN=true
QUEUE_EXECUTION_BUILD_LOG_FROZEN=true
STAGE_D_B_BUILD_LOG_ORDER_FROZEN=true
CHILD_SLOT_LABEL_INDEX_BRIDGE_FROZEN=true
QUEUE_TRANSITION_INPUT_NULLABILITY_FROZEN=true
QUEUE_OBSERVATION_STATE_LAW_FROZEN=true
CHILD_RESULT_PARENT_SLOT_RETURN_FROZEN=true
CHILD_RESULT_PARENT_SLOT_CAUSAL_ROWS_REQUIRED=true
QUEUE_ABI_PARENT_FORM_COUNT=6
HIERARCHICAL_SIBLING_ALLOCATION_BASIS_FROZEN=true
CELL_COUNT_DEBIT_AT_CREATE_ONLY=true
SINGLE_CELL_FINALIZATION_BOUNDARY_FROZEN=true
CHILD_GLOBAL_COMPLETION_REMAINS_ACTIVE=true
UNIQUE_ROOT_GLOBAL_FINAL_FROZEN=true
CHILD_AGGREGATE_ZERO_DELTA_FROZEN=true
RESULT_ALLOCATED_FINAL_BUDGET_LINEAGE_FROZEN=true
BACKPRESSURE_FIELD_DERIVATION_FROZEN=true
READY_RESERVATION_CAPACITY_FROZEN=true
LATEST_SETTLED_TRANSITION_ORDER_FROZEN=true
REPEATED_UNCHANGED_DEFER_FORBIDDEN=true
SCHEDULER_NO_SPIN_FROZEN=true
BUDGET_CONSTRUCTION_LOG_FROZEN=true
RUNTIME_ABI_ARTIFACT_BUILD_LOG_FROZEN=true
STAGE_D_B_INTERLEAVED_ARTIFACT_ORDER_FROZEN=true
TYPED_TRACE_REFERENCE_DERIVATION_FROZEN=true
TYPED_REPORT_PARENT_RETURN_DERIVATION_FROZEN=true
PARENT_RETURN_REQUIRED_FIXED_TRUE=true
SEMANTIC_TRANSITION_OCCURRENCE_SEPARATION_FROZEN=true
REPEATED_TRANSITION_DECISION_IDS_ALLOWED=true
ACTUAL_CONTENT_ADDRESSED_COUNTERFACTUAL_FROZEN=true
GENERIC_STABLE_ID_DIAGNOSTIC_NONRUNTIME=true
COUNTERFACTUAL_D5_ONLY=true
RUNTIME_RESULT_PAIR_FROZEN=true
COMPLETE_PROFILE_REPORT_EXTERNAL=true
EXECUTION_BUNDLE_BUILT_ONCE=true
TRANSITION_PROFILE_FIRST_AVAILABLE_SLICE=G2-D2
PACKAGE_FACADE_FIRST_AVAILABLE_SLICE=G2-D4
FUTURE_FUNCTION_STUBS_ALLOWED=false
BUDGET_TYPED_EVENT_CONTEXT_FROZEN=true
CHILD_ALLOCATION_CONTEXT_FROZEN=true
PLANNED_CHILD_ACTIVATION_SEPARATION_FROZEN=true
TRANSITION_TARGET_DEPENDENCY_CYCLE_FORBIDDEN=true
DECISION_BUDGET_QUEUE_ARTIFACT_ORDER_FROZEN=true
REVISE_OBSERVATION_PREDECISION_FROZEN=true
REVISE_AFTER_BUDGET_IDENTITY_FORBIDDEN=true
PREBUNDLE_VALIDATION_AND_CAUSAL_ASSEMBLY_FROZEN=true
VALIDATION_TARGET_ID_STAGE_MAP_FROZEN=true
VALIDATION_REPORT_SELF_RECURSION_FORBIDDEN=true
PRE_RESULT_VALIDATION_SURFACE_FROZEN=true
DYNAMIC_CONTEXTUAL_VALIDATOR_INPUTS_FROZEN=true
CHILD_ACTIVATION_PRECHECK_COMMIT_ORDER_FROZEN=true
CHILD_ACTIVATION_CAUSAL_ROW_REQUIRED=true
IMPLEMENTATION_CREATE_PATH_COUNT=4
ADDITIVE_SHARED_PATH_COUNT=15
CURRENT_READ_ONLY_PATH_COUNT=57
CLOSURE_ONLY_PATH_COUNT=10
LIVING_ACT_COUNT=17
CONFORMANCE_CATEGORY_COUNT=14
G2D_NEGATIVE_PROBE_COUNT=10
CONFORMANCE_NEGATIVE_PROBE_COUNT=50
ACTIVE_GAUNTLET_REF_COUNT=16
RUNTIME_TOPOLOGY_SOURCE_BOUND=true
POLICY_IDENTITY_PROFILE_SEPARATION_FROZEN=true
ROOT_LEAF_EDGE_PROJECTIONS_EXECUTABLE=true
CHILD_SLOT_ACTIVATION_FROZEN=true
CELL_INPUT_BUILD_ORDER_FROZEN=true
NODE_CELL_OUTCOME_SEPARATION_FROZEN=true
STATIC_INPUT_DERIVATION_FIELD_FROZEN=true
ASSIGNMENT_TRACE_FROZEN=true
CELL_GLOBAL_BUDGET_AXES_FROZEN=true
BUDGET_EVENT_PAIRING_FROZEN=true
ACTIVE_BUDGET_SUCCESSOR_ALLOWED=true
PRE_ROOT_LIFECYCLE_ESCALATION_FORBIDDEN=true
EXPLICIT_GT_REPORT_IDS_CONTEXT_UNIQUE=true
HISTORICAL_GT_DEFAULTS_PRESERVED=true
VALIDATION_PASS_NONE_STAGE_FROZEN=true
VALIDATION_FAILURE_OBJECT_ID_NULL=true
QUEUE_INSTANCE_SNAPSHOT_ROUND_ORDER_FROZEN=true
BLOCKED_REASON_PRECEDENCE_FROZEN=true
ROOT_RESULT_OWNS_RUNTIME_OUTCOME=true
STATIC_TOPOLOGY_RUNTIME_INSTANCE_SEPARATION_FROZEN=true
NODE_WORK_QUEUE_FROZEN=true
CHILD_PARENT_RESULT_POSTORDER_FROZEN=true
VALIDATION_REPORT_IDENTITY_CYCLE_FORBIDDEN=true
COMPLETE_G2C_PROFILE_CAPABILITY_SCOPE_BOUND=true
BUDGET_ALLOCATION_PREDECESSOR_DEBIT_LAW_FROZEN=true
RESULT_PROPOSAL_POST_VV_GT_CONTRACT_FROZEN=true
G2D_INJECTED_TIME_AXIS=KT
ROOT_ONLY_PARENT_RETURN_FROZEN=true
ABI_FIELD_PARTITION_COMPLETE=true
CAUSAL_JSON_POINTER_AND_REASON_PREFIX_LAW_FROZEN=true
ACYCLIC_IDENTITY_BUILD_ORDER_FROZEN=true
TOPOLOGY_SEED_PRESENT=true
QUEUE_PREDECESSOR_CHAIN_FROZEN=true
DETERMINISTIC_POST_VV_GT_TIME_BOUNDARY_FROZEN=true
CAUSAL_CONSUMPTION_REFS_REQUIRED=true
RETRY_ELIGIBLE_ALWAYS_FALSE=true
DIRECT_ROOT_DECISION_CONSUMPTION_FORBIDDEN=true
SHORTCUT_ROUTE_CONSUMPTION_FORBIDDEN=true
TERMINAL_ROUTE_CONSUMPTION_FORBIDDEN=true
FULL_FRACTAL_ONLY_RECURSIVE=true
CHILD_CELL_CAN_BECOME_ROOT=false
TOPOLOGY_CREATES_AUTHORITY=false
TOPOLOGY_CREATES_PERMISSION=false
TOPOLOGY_CREATES_EFFECT=false
G2E_STARTED=false
G2F_STARTED=false
GATE2_CLOSED=false
PUBLIC_RELEASE_CLAIMED=false
RC2_CLAIMED=false
QUANTUM_IMPLEMENTATION_STARTED=false
PYTEST_RUN=false
RUNNER_EXECUTED=false
REAL_WORLD_EFFECTS_COUNT=0
READY_FOR_OWNER_PREFLIGHT_COMMIT=true
```
