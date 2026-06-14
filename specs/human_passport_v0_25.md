# Hedgehog OS / Fractal Reflexive OS Human Passport v0.25

Version v0.25 is an MVP engineering passport. It is not the full final OS theory.
It is the bridge from concept to a GitHub proof-of-architecture demo that a new
LLM or coding agent can read before implementation.

The purpose of this document is to preserve the architecture, contracts,
invariants, and success criteria for the MVP. It should be treated as an
engineering guide, not marketing material and not a prompt for a generic
chatbot.

Long-term expansion beyond the MVP is documented separately in
`docs/strategic_expansion_map.md`. That document is a strategic vision map, not
an implementation sprint. If there is a conflict between this MVP passport and
the strategic expansion map, this MVP passport controls current implementation
work.



## 1. Project Identity

Hedgehog OS / Fractal Reflexive OS is not a chatbot.

It is a proof-of-architecture demo for a cognitive/fractal runtime. The system
is organized around controlled transformation of a user/event into intent,
time-aware world state, memory-first retrieval, candidate branch generation,
deterministic branch viability scoring, planning, execution, validation,
game-theoretic memory update, and final output creation by the root control
plane.

The MVP is not the full OS. It does not attempt to implement every future layer,
network protocol, continuous runtime, autonomous tool environment, or external
ecosystem integration. It proves the spine of the architecture with small local
deterministic components.

The demo domain is a mock government certificate request. The domain is chosen
because it has enough structure to exercise forms, requirements, evidence,
policy checks, temporal validity, reuse, validation, and final answer assembly.

The goal is to prove the pipeline, not to integrate real government APIs,
banks, YouTube, Telegram, or UI.

Core pipeline:

```text
User/Event
-> RootOrchestrator
-> Intent
-> TemporalQuery
-> WorldState
-> Local DRS retrieval
-> CandidateVectorGenerator
-> AVF
-> AttractorPacket
-> Architect
-> PlanGraph
-> Executors
-> ResultProposals
-> Post V&V
-> GTValidator
-> Root FinalOutput
-> DRS writeback
-> Audit/Trace
```

Marennya and UP are separate deferred lateral/upward systemic directions, not
mandatory post-pipeline modules in the downward canonical vector.

### Root-Centered Capability Geometry

The core pipeline is one flat observable projection, not the full architecture.
Hedgehog OS is a multidimensional Root-centered geometry of bounded directed
capabilities.

Root is the point of sovereignty and the only final commit boundary in its
contour. "Vassal of my vassal is not my vassal": bounded local authority in a
child cell or nested capability does not automatically propagate upward,
sideways, outward, or into Root.

A needle is not a plugin. It is a directed bounded capability / capability
contract anchored in Root. A complex needle may contain local O/A/E rhythm,
PlanGraph, DAG, child cells, validators, local memory, or checks, but it never
becomes Root.

Canonical execution is the main downward Root-controlled runtime vector; it is
not merely an ordinary needle. Marennya is a lateral reflective systemic
needle-like direction and UP is an upward transfer/opportunity systemic
needle-like direction. Both are deferred, proposal-only, quarantine-first, and
Root-approved. They are not required for the first applied semantic demos.

DRS is semantic topology and an address/resonance/lineage/audit/trust/TTL/
conflict/reuse/promotion fabric. It is not a memory database, vector store, or
authority. Dense artifacts remain outside DRS behind pointers. External DRS is
controlled transfer of verified meaning traces; external experience is
candidate influence, not authority.

See `docs/passport_geometry_root_needles.md`.

### Observable Zero Trust Runtime Proof

The current auditor-facing checkpoint is:

```bash
python -m demo.run_canonical_pipeline_trace
```

It is not a chatbot demo and not a LangChain-style agent chain. It is an
observable role-bounded runtime trace showing Root authority, explicit
Orchestrator-stage / Route Assembly, allowed CandidateVector sources, AVF /
HardMask / SoftMask before Architect, Root-created AttractorPacket, Architect
input as AttractorPacket only, Architect output as PlanGraph, Fractal DAG
Executor Core execution, ResultProposal-only Executor output, Post V&V before
GT, GT selection without commit, artifact return to Root, Root-only FinalOutput,
DRS writeback / audit, no real external actions, and no uncontrolled
delegation.

The DAG runner connects to the Root-controlled pipeline after Architect: it
executes Architect PlanGraph and returns ResultProposals. RootOrchestrator
remains the authority and commit boundary. The DAG runner is not Root, does not
own execution authority, and does not commit output.

Current gaps: this is a demo-runtime proof, not production OS runtime.
Production recursive child-cell execution is not implemented yet. Real external
API/needle execution is not enabled here. Live Gemini/SLM Orchestrator is a
later layer, not the default. `fallback` vs `fallback_template` naming cleanup
is minor backlog.

Current bounded graph and lineage checkpoints:

- Large Graph / Bounded Fractal Stress v0.1 proves deterministic bounded
  behavior for oversized or malformed PlanGraphs. It demonstrates max_nodes,
  max_edges, max_depth, max_parallelism, cycle detection, unknown dependency
  detection, child boundary snapshots, and bounded GT candidate summaries. It
  does not prove production 10k-node execution. The stress runner does not call
  the real GT runtime; it proves a GT boundary / bounded summary check
  (`gt_runtime_called: false`, `gt_boundary_mode: bounded_summary_check`) and
  does not send the raw large graph to GT.
- DRS Graph Proximity / Lineage v0.1 proves a LocalDRS-only read-only
  retrieval/ranking signal. Records store links through source_refs / lineage
  refs, not static hop counters. `graph_distance` is computed at query time and
  `graph_proximity = 2 ** (-distance / hop_half_life)`. GraphProximity is only a
  ranking signal; it does not change ReuseGate, override policy, or make
  Quarantine / DeadEnds / blocked / failed / degraded records direct-reuse
  eligible.
- Chaos Survival Showcase v0.1 is an auditor-facing showcase / evidence
  aggregator over existing deterministic proof modules. It composes
  NeedleRuntime Chaos, Canonical Needle Outcome Trace with real GTValidator
  integration, Needle Outcome DRS Routing Persistence, Large Graph / Bounded
  Fractal Stress, and DRS Graph Proximity / Lineage. It demonstrates containment
  and safe routing under broken needles, malformed graphs, unsafe reuse
  candidates, and graph-near bad records. It is not a new core runtime layer,
  does not claim production autonomy, does not claim global DRS or production
  retrieval, and does not claim production 10k-node execution. Its PASS summary
  is derived from computed section predicates.
- Compute Collapse via DRS Reuse v0.1 is an auditor-facing showcase / evidence
  aggregator over existing deterministic cold-start, Root direct reuse,
  LocalDRS, ReuseGate, and unsafe DRS routing proofs. It complements Chaos
  Survival Showcase: Chaos Survival demonstrates resilience / safety /
  containment; Compute Collapse demonstrates efficiency / reuse / zero
  re-planning path. It shows cold_start_full_pipeline, memory_context_only,
  eligible_direct_reuse, and unsafe_records_not_reused. Direct reuse requires
  eligible Work, context memory is not direct reuse, Root remains final
  authority, unsafe records are not reused, and GT does not commit FinalOutput.
  Compute units are illustrative deterministic units derived from route flags,
  not real token billing. This must not be described as absolute zero cost, real
  token savings proven, production autonomy, or a production billing benchmark.
- DRS Layer Taxonomy v0.1 is an engineering hardening layer, not a showcase. It
  clarifies broad LocalDRS DeadEnds/reporting semantics without a schema
  refactor, ReuseGate change, global DRS, external DRS, or unsafe reuse. It
  classifies work_candidate / successful_work, quarantine, dead_end,
  blocked_trace, degraded_trace, and needs_user_trace at routing/report/content
  semantics level. Only accepted successful Work is direct-reuse eligible in the
  demo. timeout is degraded_trace, permission_required is needs_user_trace,
  blocked_trace is not success, quarantine is not Work, and the taxonomy truth
  flags are derived from classified rows.
- Typed DRS Lineage Edges v0.1 is the next completed engineering hardening layer. It is a
  LocalDRS-only typed-edge proof that distinguishes derived_from, same_trace,
  warns_against, blocked_by_policy, requires_user, degraded_from, supports, and
  contradicts relationships. It does not perform a schema refactor, change
  ReuseGate, implement ReuseScore, implement ConflictCheck, implement
  global/external DRS, or make unsafe records reusable. Typed edges are
  query-time semantic signals only: supports / derived_from can contribute
  evidence but not direct reuse eligibility, warning/blocking/needs-user/
  degraded/contradiction edges do not become success, and contradiction targets
  require future ConflictCheck / ReuseScore handling.
- ReuseScore v0.1 is the next completed engineering hardening layer. It is a
  LocalDRS-only advisory/ranking proof that consumes Typed DRS Lineage Edges
  candidates and computes deterministic illustrative scores from visible
  components: quality, freshness, gt_trust, semantic_similarity,
  graph_proximity, typed_positive_signal, warning_penalty, blocking_penalty,
  needs_user_penalty, degraded_penalty, contradiction_penalty, and risk_penalty.
  Raw scores are computed before policy gates are applied. ReuseScore is not
  Root, not ReuseGate, not policy override, not production ConflictCheck, not
  global/external DRS, not real token billing, and not production autonomy.
  High score cannot override policy: direct reuse still requires eligible
  successful Work, context memory is not direct reuse, unsafe taxonomy records
  remain non-reusable, and contradiction-risk candidates become
  needs_conflict_check until future ConflictCheck exists.
- Semantic Reuse Pipeline Integration v0.1 is the next completed engineering
  integration proof. It connects the completed semantic stack:
  LocalDRS retrieval -> taxonomy-aware filtering -> typed edge interpretation ->
  graph proximity -> ReuseScore -> ReuseGate / Root boundary -> direct reuse
  candidate or full pipeline fallback. It structurally consumes
  collect_reuse_score(), preserves the source Typed DRS Lineage Edges report,
  evaluates scenario rows, and separates recommendations from authority. It is
  not production RootOrchestrator integration, production autonomy, global DRS,
  external DRS, a ReuseGate replacement, a Root bypass, direct reuse execution,
  FinalOutput creation, real external action, live Gemini, or Telegram action.
  It proves eligible direct reuse can be recommended but not committed by the
  pipeline, context memory is not direct reuse, contradiction routes to
  needs_conflict_check, high score does not override policy, and quarantine /
  needs_user / degraded / dead_end records are not reused. PASS is derived from
  stages, scenarios, and boundary facts.
- The current DRS semantic stack is DRS Graph Proximity / Lineage v0.1, DRS
  Layer Taxonomy v0.1, Typed DRS Lineage Edges v0.1, ReuseScore v0.1, and
  Semantic Reuse Pipeline Integration v0.1.
- Root-controlled Semantic Reuse Decision Trace v0.1 is the next completed
  dry-run proof. It consumes Semantic Reuse Pipeline recommendations, maps them
  into Root-controlled decisions, does not change production RootOrchestrator
  behavior, does not execute direct reuse, does not create production
  FinalOutput, does not write production Work records, and does not grant
  authority to the semantic pipeline. Direct reuse candidates are accepted only
  for ReuseGate review, not execution; needs_full_pipeline, conflict,
  policy-blocked, quarantine, needs_user, degraded, and dead_end recommendations
  map to their respective Root dry-run decisions.
- Root-controlled Semantic Reuse Gate Trace v0.1 is the paired dry-run proof.
  It consumes the Root decision trace, performs gate review only for the
  Root-approved direct reuse candidate, and leaves all other routes as
  non-gate routes. Gate approval means the candidate returns upward to Root for
  final decision; it is not production execution. ReuseGate does not create
  FinalOutput, does not execute direct reuse, semantic pipeline does not commit,
  and Root remains final authority.
- Root-controlled Semantic Reuse Final Decision Trace v0.1 is the completed
  Root-controlled dry-run proof. It consumes the Gate Trace, does not change
  production RootOrchestrator behavior, does not execute production direct
  reuse, does not create production FinalOutput, does not perform real external
  actions, does not write production Work records, and grants no authority to
  the semantic pipeline or ReuseGate. It creates only a trace-level Root final
  decision artifact.
- Final decision mapping is explicit: gate-approved candidate ->
  root_final_accepts_controlled_direct_reuse_trace; full pipeline fallback ->
  root_final_selects_full_pipeline_fallback; conflict check ->
  root_final_requires_conflict_check; policy block ->
  root_final_blocks_policy_route; quarantine -> root_final_routes_to_quarantine;
  needs_user -> root_final_requires_user_input; degraded ->
  root_final_marks_degraded_trace; dead_end -> root_final_rejects_dead_end.
- root_final_accepts_controlled_direct_reuse_trace is still trace/dry-run, not
  production direct reuse execution. The trace final decision artifact is not
  production FinalOutput.
- Root-native Semantic Reuse E2E Trace v0.1 is now complete. It is the first
  deterministic end-to-end semantic reuse trace, consumes the Semantic Reuse
  Authority Stack Audit, and shows input task -> TemporalQuery -> LocalDRS
  retrieval -> taxonomy-aware filtering -> typed edge interpretation -> graph
  proximity -> ReuseScore -> semantic reuse recommendation -> Root decision ->
  ReuseGate review -> Root final dry-run decision -> trace-level final answer
  artifact -> audit visibility.
- The selected scenario is eligible_direct_reuse_candidate:
  direct_reuse_candidate -> root_accepts_direct_reuse_candidate_for_gate_review
  -> gate_review_accepts_candidate_for_root_final_decision ->
  root_final_accepts_controlled_direct_reuse_trace. The artifact kind is
  trace_level_final_answer_artifact, created_by = root_orchestrator, with
  production_final_output = false, production_action_executed = false, and
  production_work_record_written = false.
- E2E safety semantics: semantic pipeline recommends only, ReuseScore remains
  advisory, Root decides, ReuseGate guards, Root final trace decides, context
  memory is not direct reuse, high score does not override policy,
  contradiction does not auto-reuse, unsafe reuse candidates remain zero,
  LocalDRS is local-only, external/global DRS are not implemented, and
  production autonomy is not claimed.
- Proof status for the E2E trace: 12 stages passed, 229 focused tests passed,
  749 full-suite tests passed, and the sensitive scan found no secret terms.
- Current semantic reuse chain: Semantic Reuse Authority Stack Audit ->
  Root-native Semantic Reuse E2E Trace -> deterministic trace-level final answer
  artifact -> no production execution.
- Root-native Full Canonical E2E Trace v0.1 is now complete. It is a
  deterministic full canonical E2E proof that composes a first-run canonical
  Root-controlled path with a second-run semantic reuse authority path.
- First-run canonical path: input task -> Root intake / Orchestrator boundary ->
  Architect / PlanGraph -> AVF / Attractor formation -> DAG / Executor ->
  ResultProposals -> Post V&V -> GT -> Root trace artifact -> LocalDRS
  writeback / audit visibility.
- First-run proof semantics: root_authority_preserved_first_run = true,
  architect_does_not_answer_user = true, executor_does_not_create_final_output =
  true, gt_does_not_create_final_output = true,
  first_run_created_root_trace_artifact = true,
  first_run_local_drs_writeback_visible = true,
  first_run_local_work_record_written_in_proof = true, and
  production_external_action_executed = false.
- Second-run semantic reuse path: repeat/similar task -> TemporalQuery ->
  LocalDRS retrieval -> taxonomy / typed edges / graph proximity -> ReuseScore
  -> Semantic Pipeline recommendation -> Root decision -> ReuseGate review ->
  Root final dry-run decision -> trace-level semantic reuse answer artifact.
- Second-run proof semantics: second_run_stages_passed = 12,
  selected_scenario = eligible_direct_reuse_candidate,
  semantic_reuse_path_used = true, second_run_root_authority_preserved = true,
  reuse_gate_boundary_preserved = true, semantic_pipeline_recommends_only =
  true, and reuse_score_advisory_only = true.
- Bridge honesty: bridge_mode = deterministic_proof_linkage,
  deterministic_bridge_between_runs = true, production_persistence_claimed =
  false, production_reuse_claimed = false, and production_reuse_not_executed =
  true. Local proof DRS writeback is visible; production persistence and
  production reuse are not claimed.
- Full Canonical E2E safety flags: production_direct_reuse_executed = false,
  production_final_output_created = false, production_work_record_written =
  false, production_external_action_executed = false, no_real_external_actions =
  true, no_live_gemini = true, no_telegram_actions = true, no_global_drs = true,
  no_external_drs_network = true, and production_autonomy_claimed = false.
- Proof status: first_run_stages_passed = 9, second_run_stages_passed = 12,
  250 focused tests passed, 770 full-suite tests passed, sensitive scan found no
  secret terms, commit = 83f59a2 Add Root-native full canonical E2E trace.
- Current status: first-run Root-controlled canonical path -> local proof
  DRS/audit visibility -> second-run semantic reuse authority path -> Root final
  dry-run reuse decision -> no production execution.
- Optional Live Gemini Architect Smoke v0.1 is complete. It is an opt-in
  role-substitution smoke proof inside the Full Canonical E2E boundary.
- Gemini may substitute only the Architect proposal role. It does not become
  Root, Orchestrator, Executor, GT, or FinalRenderer; create FinalOutput; write
  DRS; execute actions; or bypass AVF, PlanGraph contract, Executor, Post V&V,
  GT, Root, ReuseGate, policy, or permission gates.
- Default mode is `dry_run_default`, deterministic, network-free, does not call
  live Gemini, uses `architect_artifact_source = deterministic_mock`, and keeps
  `plan_graph_contract_checked = true`.
- Live mode is opt-in through explicit `--live`, `HEDGEHOG_ALLOW_LIVE_GEMINI =
  1`, and Gemini configuration. Missing config reports SKIPPED instead of
  crashing. Invalid live artifacts are caught, contained, kept away from
  Executor and Root final output, and fall back visibly to deterministic
  Architect.
- Boundary checks derive from the Full Canonical E2E source report, role flags,
  artifact containment, and context facts. Rendered output does not print
  credential environment names or secret terms.
- Proof status: 212 focused tests passed, 788 full-suite tests passed,
  sensitive scan found no secret terms, default dry-run status PASS, and
  ready_for_future_orchestrator_live_smoke = true.
- Ordered Live Gemini Orchestrator-to-Architect Smoke v0.1 is complete. It
  proves an opt-in ordered role-substitution path: Root boundary -> live Gemini
  Orchestrator proposal -> schema-backed local validation -> live Gemini
  Architect proposal -> Architect contract check -> no production execution.
- Final success evidence:
  `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log`.
  It proves orchestrator_initial_attempt_valid=true,
  orchestrator_active_proposal_source=live_gemini,
  orchestrator_active_proposal_is_fallback=false,
  temporal_query_required_value=true, downstream_actors_missing=[],
  downstream_actors_extra=[], architect_artifact_source=live_gemini,
  architect_artifact_valid=true, production_final_output_created=false, and
  production_external_action_executed=false.
- Gemini did not receive Root authority, write DRS, execute actions, create
  FinalOutput, activate Marennya / UP, use Telegram, or perform real external
  actions. Older ordered Gemini fallback reports are historical safety evidence
  only and must not be used as proof of dual-live success.
- Controlled Orchestrator Matrix Gate v0.1 is complete. It is a deterministic
  Root-controlled gate proof. Orchestrator matrix is an input artifact, not
  authority. Root creates RootMatrixGateDecision artifacts and may accept,
  reject, or downgrade a matrix.
- Gate decision semantics: accept means a valid matrix may become future AVF
  input; reject means an unsafe or invalid matrix cannot continue; downgrade
  means a partially usable matrix may continue only with unsafe or incomplete
  claims removed.
- Verified gate scenarios: valid_matrix_accept accepted;
  missing_temporal_query_reject rejected; incomplete_guards_downgrade_or_reject
  downgraded with missing guards listed, downgraded_matrix_created=true, and
  unsafe_claims_removed=true; wrong_downstream_actors_reject rejected with
  missing/extra actor diagnostics; forbidden_bypass_reject rejected;
  high_confidence_policy_block rejected with high_confidence_overrides_policy =
  false and policy_beats_orchestrator_confidence = true; fallback_route_visible
  keeps fallback_route_visible = true and fallback_route_executed = false.
- Gate proof status: scenarios_verified = 7, accepted_count = 1,
  rejected_count = 5, downgraded_count = 1,
  controlled_orchestrator_matrix_gate_status = PASS, 110 focused tests passed,
  859 full-suite tests passed, and sensitive scan found no secret terms.
- Gate evidence:
  `docs/audit_reports/auditor_controlled_orchestrator_matrix_gate_report.log`.
  The runner verifies the final ordered Gemini 2.5 success report before using
  it as live-role context: success_report_exists = true,
  success_report_verified = true, success_report_missing_markers = [],
  ordered_live_context_mode = success_report_verified,
  live_orchestrator_can_create_valid_matrix = true, and
  live_architect_can_create_valid_artifact = true.
- Gate boundary semantics: AVF is not invoked, AttractorPacket is not created,
  Architect / Executor / Post V&V / GT are not reached, Orchestrator does not
  write DRS or create FinalOutput, production_final_output_created = false,
  production_external_action_executed = false, global/external DRS are not
  implemented, and Marennya / UP are not invoked.
- AVF / Attractor Formation from accepted Matrix v0.1 is complete. It is a
  deterministic AVF / Attractor proof that consumes Controlled Orchestrator
  Matrix Gate v0.1 without hardcoding Matrix Gate PASS.
- AVF forms AttractorPacket-like artifacts only from accepted or downgraded
  RootMatrixGateDecision outputs. Rejected matrices do not reach AVF and create
  no AttractorPacket. AVF remains independent; Orchestrator hints are hints, not
  commands; HardMask and policy beat Orchestrator confidence; Root may downgrade
  or override matrix claims.
- Verified AVF behavior: source_matrix_gate_status = PASS,
  valid_matrix_accept forms an AttractorPacket-like artifact,
  incomplete_guards_downgrade_or_reject forms a limited artifact with
  downgraded claims visible, and missing_temporal_query_reject,
  high_confidence_policy_block, forbidden_bypass_reject, and
  wrong_downstream_actors_reject are blocked before AVF.
- AVF proof status: avf_attractor_from_accepted_matrix_status = PASS,
  scenarios_verified = 6, attractor_packets_created = 2,
  accepted_matrix_packets = 1, downgraded_matrix_packets = 1,
  rejected_matrix_packets = 0, rejected_matrices_blocked_before_avf = true,
  avf_independent = true,
  ready_for_architect_from_bounded_attractor_packet = true, 91 focused tests
  passed, 880 full-suite tests passed, and sensitive scan found no secret terms.
- AVF evidence:
  `docs/audit_reports/auditor_avf_attractor_from_accepted_matrix_report.log`.
  Architect and Executor are not invoked, AVF does not create FinalOutput, write
  DRS, or execute actions, Orchestrator does not write DRS, no production
  FinalOutput or external action is created, global/external DRS are not
  implemented, and Marennya / UP remain deferred.
- Architect from bounded AttractorPacket v0.1 is complete. It consumes AVF /
  Attractor Formation from accepted Matrix v0.1 without hardcoding AVF PASS.
  Architect receives only bounded AVF output, not raw Orchestrator matrix, raw
  unchecked user intent, rejected matrix, or invalid/unbounded AttractorPacket.
  Accepted and downgraded bounded packets create valid PlanGraph proposals;
  rejected matrix, raw Orchestrator matrix, raw unchecked user intent, and
  invalid/unbounded packet inputs are blocked; invalid Architect artifact is
  contained. PlanGraph contract is checked, Executor / Post V&V / GT are not
  invoked, Architect does not create FinalOutput, write DRS, or execute actions,
  and Marennya / UP remain deferred.
- Proof status: architect_from_bounded_attractor_packet_status = PASS,
  scenarios_verified = 7, valid_plan_graph_proposals_created = 2,
  accepted_packet_plan_proposals = 1, downgraded_packet_plan_proposals = 1,
  raw_orchestrator_matrix_blocked = true, raw_user_intent_blocked = true,
  rejected_matrix_blocked = true, invalid_packet_blocked = true,
  invalid_architect_artifact_contained = true,
  ready_for_dag_executor_from_valid_plan_graph = true, 93 focused tests passed,
  903 full-suite tests passed, and sensitive scan found no secret terms.
- Evidence:
  `docs/audit_reports/auditor_architect_from_bounded_attractor_packet_report.log`.
- DAG / Executor from valid PlanGraph v0.1 is complete. It consumes Architect
  from bounded AttractorPacket v0.1 without hardcoding Architect PASS.
  Executor receives only validated PlanGraph nodes, not invalid Architect
  artifact, raw Architect text, raw Orchestrator matrix, raw user intent, or
  unvalidated PlanGraph. Accepted valid PlanGraph creates ResultProposal;
  downgraded valid PlanGraph creates limited/degraded ResultProposal; invalid
  Architect artifact, raw Architect text, raw Orchestrator matrix, raw user
  intent, and unvalidated PlanGraph are blocked before Executor.
- Executor returns ResultProposal only, does not create FinalOutput, does not
  write DRS directly, and does not execute real external actions. Post V&V and
  GT are not invoked yet; no production FinalOutput or production external
  action is created; global/external DRS are not implemented; Marennya / UP
  remain deferred.
- Proof status: dag_executor_from_valid_plan_graph_status = PASS,
  scenarios_verified = 7, result_proposals_created = 2,
  accepted_plan_result_proposals = 1, downgraded_plan_result_proposals = 1,
  invalid_architect_artifact_blocked = true, raw_architect_text_blocked = true,
  raw_orchestrator_matrix_blocked = true, raw_user_intent_blocked = true,
  unvalidated_plan_graph_blocked = true,
  executor_receives_only_validated_plan_graph_nodes = true,
  ready_for_post_vv_from_result_proposal = true, 85 focused tests passed,
  923 full-suite tests passed, and sensitive scan found no secret terms.
- Evidence:
  `docs/audit_reports/auditor_dag_executor_from_valid_plan_graph_report.log`.
- Post V&V from ResultProposal v0.1 is complete. It consumes DAG / Executor from
  valid PlanGraph v0.1 without hardcoding DAG / Executor PASS. Post V&V receives
  only ResultProposal artifacts, not raw Executor text, raw Architect PlanGraph,
  raw Orchestrator matrix, raw user intent, or real action output. It validates
  ResultProposal only and creates ValidationReport / V&VReport only.
- Verified behavior: source_dag_executor_status = PASS, completed
  ResultProposal creates accepted ValidationReport, degraded ResultProposal
  creates degraded ValidationReport, raw upstream inputs are blocked, malicious
  FinalOutput and DRS write claims are rejected, malformed ResultProposal is
  rejected, GT is not invoked, and Root Final is not invoked.
- Proof status: post_vv_from_result_proposal_status = PASS,
  scenarios_verified = 10, validation_reports_created = 5,
  accepted_validation_reports = 1, degraded_validation_reports = 1,
  rejected_validation_reports = 3, post_vv_receives_only_result_proposal = true,
  ready_for_gt_from_validation_report = true, 87 focused tests passed, 946
  full-suite tests passed, and sensitive scan found no secret terms.
- Evidence:
  `docs/audit_reports/auditor_post_vv_from_result_proposal_report.log`. The next
  completed layer is GT from ValidationReport v0.1.
- GT from ValidationReport v0.1 is complete. It consumes Post V&V from
  ResultProposal v0.1 without hardcoding Post V&V PASS. GT receives only
  ValidationReport / V&VReport artifacts, not raw ResultProposal, raw Executor
  text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, or
  real action output. GT creates GTDecision / selection artifact only.
- Verified behavior: source_post_vv_status = PASS, accepted ValidationReport
  creates accept GTDecision, degraded ValidationReport creates degrade
  GTDecision, rejected ValidationReport creates reject GTDecision, raw upstream
  inputs are blocked, malicious FinalOutput / DRS write / action execution claims
  are rejected, malformed ValidationReport is rejected, and Root Final is not
  invoked.
- Proof status: gt_from_validation_report_status = PASS, scenarios_verified = 13,
  gt_decisions_created = 7, accepted_gt_decisions = 1, degraded_gt_decisions = 1,
  rejected_gt_decisions = 5, gt_receives_only_validation_report = true,
  ready_for_root_final_from_gt_decision = true, 91 focused tests passed, 971
  full-suite tests passed, and sensitive scan found no secret terms.
- Evidence:
  `docs/audit_reports/auditor_gt_from_validation_report.log`.
- Root Final from GTDecision v0.1 is complete. It consumes GT from
  ValidationReport v0.1 without hardcoding GT PASS. Root Final receives only
  GTDecision / selection artifacts, not raw ValidationReport, raw ResultProposal,
  raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user
  intent, or real action output. Root creates FinalOutput / trace-level final
  artifact only, Root is the only final-output authority, and GT does not create
  FinalOutput.
- Verified behavior: source_gt_status = PASS; accept / degrade / reject
  GTDecision artifacts create accepted / degraded / rejected RootFinalArtifact
  outputs; raw upstream inputs are blocked; malicious GT FinalOutput, DRS write,
  and action claims are rejected; malformed GTDecision is rejected; DRS writeback
  is not invoked.
- Proof status: root_final_from_gt_decision_status = PASS,
  scenarios_verified = 14, root_final_artifacts_created = 7,
  accepted_root_final_artifacts = 1, degraded_root_final_artifacts = 1,
  rejected_root_final_artifacts = 5, root_final_receives_only_gt_decision = true,
  root_is_only_final_output_authority = true,
  ready_for_full_canonical_chain_trace = true, drs_writeback_invoked = false,
  production_external_action_executed = false, production_persistence_claimed =
  false, 94 focused tests passed, 997 full-suite tests passed, and sensitive scan
  found no secret terms.
- Evidence:
  `docs/audit_reports/auditor_root_final_from_gt_decision.log`.

DRS Writeback / Audit from Root Final v0.1 is complete. It is a deterministic
proof-level boundary that actually consumes `collect_root_final_from_gt_decision()`
without hardcoding Root Final PASS. Only valid RootFinalArtifact inputs may
create `local_audit_only` records. Raw upstream artifacts and real action output
are blocked; malformed RootFinalArtifact inputs and malicious global DRS,
external DRS network, production persistence, Root DRS write, and action claims
are rejected.

Proof status: PASS, scenarios_verified = 16, records_created = 3,
accepted/degraded/rejected = 1/1/1, Root authority preserved, production
persistence and external actions false, 98 focused tests passed, 1037 full-suite
tests passed, and the sensitive scan found no secret terms. Evidence:
`docs/audit_reports/auditor_drs_writeback_from_root_final.log`.

DRS is not the full memory, a decision authority, or a vector store. It is an
address/resonance/lineage/audit layer for Root-authorized access to memory. Root
remains commit authority; external/global DRS remains a future pointer/protocol
boundary.

Root-native sandbox NeedleRuntime E2E v0.1 is complete. It sources a validated
PlanGraph node from the existing Architect proof and demonstrates a
Root-approved bounded sandbox/mock capability call through NeedleExecutionResult,
ResultProposal, Post V&V, GTDecision, and Root FinalArtifact. NeedleRuntime is
not authority; needle outcome is evidence, not final truth; unsafe, degraded,
blocked, and failed outcomes remain visible downstream.

The proof verifies 11 scenarios, including completed, timeout, invalid JSON,
contract mismatch, permission-required, forbidden-action, raw-output, and four
malicious-claim cases. Status is PASS; completed/degraded/blocked_or_failed =
1/1/4, malicious_claims_rejected = 4, 70 focused tests and 1057 full-suite tests
passed, and the sensitive scan found no secret terms. Evidence:
`docs/audit_reports/auditor_root_native_sandbox_needleruntime_e2e.log`.

Needles are bounded capability contracts, not Executor-owned plugins. This is
not default RootOrchestrator integration, production external execution, real
API/device access, Telegram, credential vault, production DRS persistence, or
external/global DRS.

Fractal Cell Runtime v0.1 is complete. It is a deterministic bounded child-cell
proof, not a long chain. The parent PlanGraph now proves atomic node -> ordinary
Executor, needle-bound node -> sandbox NeedleRuntime, and non-atomic node ->
bounded child fractal cell. A `child_cell_required` node creates ChildCellRequest;
a deterministic mini-cell may run child Orchestrator / Architect / Executor;
ChildBoundarySnapshot returns upward; and the parent adapter creates a
ResultProposal-compatible artifact for Post V&V, GT, and Root Final.

Completed, degraded, blocked, and failed child outcomes remain visible. The
child cell and child Orchestrator are not Root; child output is boundary evidence,
not a final answer; no child FinalOutput, parent DRS write, real external action,
or live child LLM/SLM is allowed. Recursion and execution are bounded by depth
and budget, and parent DRS promotion remains Root-authorized only.

ChildBoundarySnapshot is addressable experience, not an installed needle. A
successful child trace does not automatically create a needle. Future lifecycle
work may represent `experience_record -> reuse_candidate -> protocol_candidate ->
NeedleCandidate -> installed needle`, with Root as commit authority.

Proof status: PASS, scenarios_verified=12, completed/degraded/blocked_or_failed =
1/1/2, malicious_child_claims_rejected=5, focused tests passed=56, full suite
passed=1069, sensitive scan clear. Evidence:
`docs/audit_reports/auditor_fractal_cell_runtime.log`.

Live Child Executor in Fractal Cell v0.1 is complete. It is an opt-in live
Gemini proof inside one bounded child cell, not a long chain. Gemini substitutes
only child Executor; it is not child Orchestrator, child Architect, or Root. It
receives one Architect-provided bounded node contract, not a free instruction,
and may return only ChildExecutionResult JSON/evidence.

The node contract defines node identity, task kind, inputs/refs, constraints,
expected output schema, allowed capability, forbidden actions, permission mode,
risk, budget, and required result type. The proof-only task completed and
reached accepted Root Final. The action-like request was detected, blocked, and
preserved through ChildBoundarySnapshot, parent adapter, Post V&V, GT, and
rejected Root Final with no hidden success.

ChildExecutionResult is bounded experience/evidence only. It is not FinalOutput,
DRS writeback, a needle, a protocol template, or production action execution.
No API/tool call, real action, child FinalOutput, parent DRS write, Root bypass,
or Post V&V / GT / Root bypass is allowed.

Live proof status: PASS, mode=live_opt_in, live network used, child Executor
only, malicious_claims_rejected=6, focused deterministic tests passed=36, full
suite passed=1082, sensitive scan clear. Deterministic safe-fallback and live
PASS evidence: `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_deterministic.log`
and `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_LIVE.log`.

DRS Lifecycle Semantics v0.2 is complete. It consumes current proof collectors
and creates local/proof-level, pointer-first ExperienceRecord objects for Root
Final audit, sandbox NeedleRuntime outcomes, ChildBoundarySnapshots, live child
results, blocked action-like traces, and synthetic promotion examples.

It represents completed, degraded, blocked, failed, rejected, quarantined,
deadend, and promotion_candidate states. The promotion ladder represents
experience_record, reuse_candidate, protocol_candidate, and needle_candidate;
installed_needle_ref is supported only and installed_needle_count remains 0.
Automatic needle creation is blocked. Root approval, repeated validation,
sandbox tests, manifest, and permission model gates remain explicit.

Trust and TTL hints are advisory; conflict status defaults to `not_checked`;
quarantine release and deadend override require Root. DRS remains
address/resonance/lineage/audit, not full memory, decision authority, vector
store, automatic NeedleFactory, or external/global DRS. Root remains commit
authority. Proof status: PASS, records_created=13, malicious_claims_rejected=5,
focused tests passed=75, full suite passed=1097, sensitive scan clear. Evidence:
`docs/audit_reports/auditor_drs_lifecycle_semantics.log`.

ConflictCheck v0.1 is complete. It deterministically consumes the 13
ExperienceRecord objects from `collect_drs_lifecycle_semantics()`, creates 11
ConflictCandidatePair objects, and emits 11 ConflictReport objects. It covers
completed/completed, completed/deadend, reuse/quarantine, promotion/rejected,
stale/fresh, trust-level, action-like/reuse, permission/action, protocol/deadend,
needle-candidate/quarantine, and compatible completed-lineage comparisons.

ConflictCheck may recommend Root or GT review, reuse or promotion block,
quarantine review, or invalidation review. It does not execute recommendations,
decide final truth, mutate DRS, invalidate, promote, demote, delete, rewrite, or
commit. Lifecycle records remain unchanged. GT review remains advisory until
Root; DRS remains storage/index/lifecycle rather than judge.

Proof status: PASS, candidate_pairs_created=11, conflict_reports_created=11,
flagged_conflicts=6, root_review_required_reports=10, no_conflict_reports=1,
malicious_claims_rejected=8, focused tests passed=47, full suite passed=1116,
sensitive scan clear. Evidence: `docs/audit_reports/auditor_conflictcheck.log`.

Audit / hash-chain hardening v0.1 is complete. It consumes ConflictCheck, DRS
Lifecycle, deterministic Live Child Executor reference, DRS writeback,
sandbox NeedleRuntime, and Fractal Cell proof collectors and creates seven
proof-level append-only evidence links. Source artifacts remain unchanged.

Consumed collectors:

- `collect_conflictcheck`;
- `collect_drs_lifecycle_semantics`;
- `collect_live_child_executor_in_fractal_cell` in deterministic/reference mode;
- `collect_drs_writeback_from_root_final`;
- `collect_root_native_sandbox_needleruntime_e2e`;
- `collect_fractal_cell_runtime`.

Chain entries are `root_final_audit_boundary`, `needle_execution_result`,
`child_boundary_snapshot`, `live_child_executor_boundary`,
`drs_lifecycle_summary`, `conflictcheck_summary`, and
`final_day_checkpoint_summary`.

Hash-chain proves continuity, not truth. It detects payload, linkage, order,
missing/injected entry, authority, persistence, and global DRS claim tampering.
It does not decide truth, validate semantic correctness, mutate DRS or source
artifacts, grant authority, replace GT / ConflictCheck / Root, implement
blockchain, or provide production persistence. Root remains final authority.

Proof status: PASS, entries_created=7, chain_continuity_valid=true,
tamper_detection_valid=true, append_only_semantics_preserved=true,
source_artifacts_unchanged=true, malicious_claims_rejected=8, focused tests
passed=49, full suite passed=1131 with 37 warnings, sensitive scan clear.
The verified tamper checks are `payload_tamper_detected`,
`previous_hash_tamper_detected`, `entry_reorder_detected`,
`missing_entry_detected`, `injected_entry_detected`,
`authority_claim_tamper_detected`,
`production_persistence_claim_tamper_detected`, and
`global_drs_claim_tamper_detected`.
`ready_for_controlled_root_orchestrator_integration=true`.
Evidence: `docs/audit_reports/auditor_audit_hash_chain.log`.

Controlled RootOrchestrator Route Assembly Integration v0.1 is complete. This
is a standalone deterministic route-assembly integration proof. It consumes
existing proof collectors and verifies boundary continuity. It does not yet
replace production RootOrchestrator runtime.

The Orchestrator-stage has delegated bounded route-assembly authority inside
the Root boundary. It may propose or assemble normalized intent, TemporalQuery,
WorldState request/assembly, DRS retrieval request, CandidateVectors, guards,
route/mode, decomposition mode, an AttractorPacket draft, and ask_user / block /
escalate recommendations.

Orchestrator proposes AVF inputs; it does not manage AVF. Root / MatrixGate /
RouteGate / Policy validate the proposal before AVF output can reach Architect.
AVF remains an independent filter/scoring/HardMask layer. HardMask remains
stronger than Orchestrator confidence.

The proof verifies continuity across MatrixGate / RouteGate, AVF / HardMask,
bounded Architect input, DAG / Executor PlanGraph boundary, Post V&V, GT, Root
Final, DRS Lifecycle, ConflictCheck, and audit/hash-chain. It covers:

- `safe_warehouse_inventory_route`;
- `forbidden_action_route_blocked`;
- `hardmask_beats_orchestrator_confidence`;
- `ask_user_recommendation`;
- `decomposition_route_to_child_cell`;
- `direct_needle_call_attempt_rejected`;
- `drs_write_attempt_rejected`;
- `malicious_authority_claims_rejected`.

Orchestrator is not Root. It does not create FinalOutput, write DRS, execute
actions, call needles directly, bypass gates or AVF, manage AVF, override
HardMask, install needles, promote protocol candidates, release quarantine,
mutate ConflictReports, decide truth, or grant authority.

Proof status: PASS, scenarios_verified=8, malicious_claims_rejected=14, focused
tests passed=67, full suite passed=1149 with 37 warnings, sensitive scan clear,
production_autonomy_claimed=false. Evidence:
`docs/audit_reports/auditor_controlled_root_orchestrator_route_assembly.log`.

This proof does not activate an autonomous RootOrchestrator, call live Gemini
or network, use Telegram, execute real external actions, create production
persistence, implement global/external DRS, invoke Marennya / UP, or implement
NeedleFactory / NeedleForge.

Corrected roadmap:

1. Root-centered geometry docs sync - complete.
2. Audit/hash-chain hardening and docs sync - complete.
3. Controlled RootOrchestrator Route Assembly and docs sync - complete.
4. Applied Warehouse and Applied Certificate demos/docs/audits - complete.
5. Permission / NeedsUser proof/docs/audits - complete.
6. NeedleCandidate lifecycle proof/docs/audits - complete.
7. Applied DRS Retrieval / Reuse proof and postcommit audit - complete.
8. Proof test report fixture optimization - complete.
9. DRS adversarial stress pack, all-layers super-smoke, human walkthrough, and
   full-stack audit - complete.
10. Applied-stack docs sync - complete.
11. Travel / Multi-condition Readiness Demo - complete.
12. Multi-domain Applied Smoke v0.2 - complete.
13. Controlled Fractal DAC Expansion v0.1 - complete.
14. Dual Fractal Coupling / Interlocking DAC Proof v0.1 - complete.
15. Cross-domain DRS Traversal / DRS Bridge Proof v0.1 - complete.
16. Needle adversarial / safety pack v0.1 - complete.
17. External DRS Pointer Protocol v0.1 - complete.
18. Codex/performance-rule hygiene patch - complete.
19. Read-only Enterprise Connector Sandbox v0.1 - complete.
20. Read-only Enterprise Connector Sandbox docs sync - complete.
21. External Evidence Acceptance Gate v0.1 - complete.
22. External Evidence Acceptance Gate docs sync - complete.
23. Bounded LLM Semantic Executor Node v0.1 - complete through docs sync.
24. Enterprise Chaos Pack v0.1 - complete through docs sync.
25. Compute Collapse Enterprise Bench v0.1 or next approved hardening layer.
27. Math Appendix Sync v0.4.
28. Production Boundary Design Docs v0.1.
29. Enterprise Killer Demo v0.1.

The current priority is proving the applied Root-controlled canonical path, not
self-improvement. Marennya / UP may remain deferred stubs for a long time.

The full pipeline is the maximum cognitive loop, not the mandatory path for
every user action. Novel, risky, ambiguous, conflicting, high-value, or
multi-branch tasks may require the full loop. Frequent and simple actions should
route to cheaper execution modes when policy allows.

The system therefore requires an explicit `ExecutionModeRouter` / `ModeRouter`
before selecting pipeline depth. The router must be budget-aware: latency,
token cost, risk, novelty, confidence, provenance need, installed needles,
DRS candidates, reuse gates, and action permission all influence the selected
mode. DRS, needles, AVF, reuse gates, and cached protocols are compute-saving
mechanisms, not latency sources. Expensive LLM/SLM calls should happen later,
less often, and with narrower context.

Execution levels:

- `L0 deterministic_reflex`: ready needle, known safe deterministic action, no
  Architect, no heavy LLM. Example: switch TV input, open a known device view,
  or repeat a safe local UI action. Still requires policy checks, permission
  checks if actionful, minimal trace/audit, and DRS writeback when state changes
  or an action was performed.
- `L1 direct_reuse`: fresh trusted DRS record or protocol replay. RootFinalFromReuse
  or direct protocol execution is allowed only after explicit gates: ReuseScore,
  Freshness, GTTrust, PolicyOK, ConflictCheck, TimeEnvelope validity, and
  ActionPermission if external action is involved. Architect/Executor may be
  skipped only if explicit Root shortcut logic exists and tests prove the
  shortcut was legal.
- `L2 memory_informed_execution`: prior records found, but shortcut not allowed.
  Full or partial pipeline may still run with constrained context. `retrieved_records > 0`
  means memory context was applied, not direct reuse.
- `L3 avf_architect_execution`: AVF selects candidate vectors and creates
  AttractorPacket; Architect creates PlanGraph. Used when a task needs planning
  but not full deep branching.
- `L4 full_fractal_reasoning`: multiple branches, Executors, Post V&V, GT
  selection, and full DRS writeback. Used for novel, ambiguous, high-risk,
  high-value, or multi-path tasks.
- `L5 deferred_reflection`: Marennya, UP, deep research, idle validation, and
  scheduled work. This is after-task, idle, scheduled, or deferred and is not
  part of the immediate user-response critical path unless explicitly requested.

### Needle Contract v0.2

Needles now declare not only `CandidateVector` objects but also action metadata:

- `action_id`;
- `intent_aliases`;
- `capability`;
- `execution_mode`;
- `risk_level`;
- confirmation policy;
- mock/real support flags;
- audit and writeback requirements.

This makes L0 deterministic reflex and future protocol execution
contract-driven. A TV, pizza, airline, calendar, bank, or corporate needle
should expose a bounded grammar of allowed actions instead of forcing a large
LLM to infer the workflow each time.

For MVP all actions remain mock-only and real external execution is forbidden.
Declared action metadata may route simple requests toward cheap execution, but
it must not bypass Root, permission checks, policy, audit, or required DRS
writeback.

### Needle Protocol Steps v0.3

A needle can now declare a bounded mock workflow for an action:

`validate_input -> permission_check -> mock_execute -> mock_receipt -> audit_marker`

This is still not real external execution. It is a deterministic protocol
skeleton proving that future TV, pizza, airline, calendar, bank, or corporate
needles can expose constrained workflows without requiring a large LLM to invent
the process each time.

### Canonical Needle Topology

Needles are contract modules and capability boundaries, not plugins owned by
Executor. A needle may be Root-visible, cluster-local, or branch-bound. An
Executor or runtime port may execute a permitted bounded capability call, but
it does not own the needle and cannot grant sovereignty.

Loading a needle does not grant sovereignty. A needle-local Orchestrator, if
present, is local to that needle or fractal cell; it is not global Root.

Needle outcomes pass through canonical pipeline boundaries:

```text
NeedleExecutionResult / bounded capability output
-> ResultProposal
-> Post V&V
-> GTValidator runtime report
-> Root-visible routing semantics
-> LocalDRS Work / Quarantine / DeadEnds persistence
```

Executor may call a permitted needle capability, but Root owns authority.
Needle output must not bypass Post V&V, GT, Root commit, audit, DRS writeback,
or quarantine policy.

Marennya and UP are built-in systemic/internal needles:

- Marennya is a reflective/internal-improvement needle.
- UP is a transfer/cross-domain-opportunity needle.

They are not ordinary external action needles. Future systemic needle classes
may include action, data, device, validator, reflective, transfer, scheduler,
policy/governance, and memory-evolution/GT.

Future engineers may define additional systemic/internal needles of similar
class. A systemic needle may contain its own bounded local fractal cycle, but it
must not receive global sovereignty. It must produce canonical boundary
artifacts such as `ResultProposal`, `QuarantineRecord`, `VVReport`, `GTReport`,
`DRS pointer`, or `AuditEvent`. It must preserve Root authority,
TimeEnvelope / TemporalQuery discipline, DRS layer separation,
quarantine-first behavior for cognitive mutations, and the rule that only Root
creates `FinalOutput`.

The current needle outcome checkpoint proves the local canonical boundary for
simulated needle outcomes. `NeedleExecutionResult` becomes a
ResultProposal-compatible artifact, Post V&V runs, the real `GTValidator`
runtime produces a report, Root-visible routing semantics are computed, and
LocalDRS persists the result into Work, Quarantine, or DeadEnds.

Routing semantics in the current MVP:

- completed accepted outcome -> Work / `task_outcome`;
- `invalid_json` -> Quarantine;
- `schema_validation_failed` -> Quarantine;
- `unknown_exception` -> Quarantine or failed trace;
- `contract_version_mismatch` -> DeadEnds / blocked trace;
- `circuit_breaker_open` -> DeadEnds / blocked trace;
- `timeout` -> degraded trace, not successful Work;
- `permission_required` -> needs_user / blocked trace, not completed action.

Safety invariants:

- Work != Quarantine.
- Work != DeadEnds.
- degraded trace != successful Work.
- permission_required != completed action.
- blocked != success.
- failed / quarantined / degraded / blocked / deadend records are not
  direct-reuse eligible.
- only accepted completed Work candidate is direct-reuse eligible in this MVP
  demo.
- DRS Layer Taxonomy v0.1 makes these meanings explicit without changing
  physical LocalDRS layers: work_candidate / successful_work is the only
  direct-reuse eligible case; quarantine covers invalid_json,
  schema_validation_failed, and unknown_exception / failed payloads; dead_end
  covers stable bad routes such as contract_version_mismatch /
  contract_boundary; blocked_trace covers guard, policy, permission boundary,
  circuit breaker, or runtime safety blocks; degraded_trace covers timeout or
  service instability; needs_user_trace covers permission_required or missing
  human input. It does not override policy, does not make unsafe records
  reusable, and does not implement global/external DRS.
- Typed DRS Lineage Edges v0.1 then clarifies record relationships at query
  time: derived_from, same_trace, warns_against, blocked_by_policy,
  requires_user, degraded_from, supports, and contradicts. Records do not store
  static hops_ago / hop_distance / graph_distance. Typed edges are semantic
  signals only in v0.1; they do not override policy, do not implement ReuseScore
  or ConflictCheck, do not auto-block contradiction targets, and do not make
  unsafe records reusable.

This does not yet prove full Root-level needle planning, AVF selection over
live external needles, production external API execution, global DRS,
NeedleFactory, marketplace, or Internet-of-Meaning behavior.

## 2. Non-Goals

The MVP explicitly is not:

- a chatbot;
- a LangChain-like simple agent;
- a full operating system implementation;
- an external DRS network implementation;
- a real external API integration project;
- a UI-first project;
- a rewrite of legacy code;
- a place to remove Time, GT, AVF, or DRS layers for simplicity.

The proof must keep the architectural layers even when individual components
are implemented as deterministic stubs.

## 3. Core Roles

### Human Owner / Sovereign

The human is above Root. The human sets policies, permissions, modes, autonomy
boundaries, and installed needles.

The system may optimize within these boundaries, but it does not outrank the
human owner. The human decides what capabilities are installed, which external
actions are permitted, what autonomy level is acceptable, and which modes are
active.

### RootOrchestrator

Root is the cognitive control plane.

In the future Root may be LLM/SLM. In the MVP Root may be deterministic Python.
Root is not a dumb dispatcher. Root owns the whole cognitive pipeline and is the
only component allowed to create `FinalOutput`.

Root:

- normalizes intent;
- assembles `WorldState`;
- performs memory-first retrieval;
- runs `CandidateVectorGenerator`;
- runs AVF;
- creates `AttractorPacket`;
- calls Architect;
- dispatches Executors;
- collects `ResultProposal` objects;
- runs Post V&V;
- runs GTValidator;
- creates `FinalOutput`;
- writes DRS records;
- triggers Marennya/UP hooks.

Hard rule:

```text
FinalOutput = RootOrchestrator only
```

### Root vs FinalRenderer

Root owns authority, validation, policy, commit, and DRS writeback.
`FinalRenderer` owns only draft generation.

This separation allows weak Root-SLM deployments. Root does not need to be the
best prose generator, but it must remain the final policy and commit authority.

`FinalRenderer` returns `FinalDraftProposal`, never `FinalOutput`.
`FinalDraftProposal` is a subordinate artifact that Root may use, reject, or
rewrite before creating `FinalOutput`.

A stronger LLM, SLM, or needle may later replace the deterministic
`FinalRenderer`, but the contract remains the same: it returns
`FinalDraftProposal` only and has no DRS writeback, external action, or final
commit authority.

### Architect

Architect receives `AttractorPacket`, not raw user text.

Architect returns `PlanGraph` only. It must not answer the user and must not
produce final output. Architect turns approved attractor vectors into a graph of
work, executor assignments, dependencies, and time assumptions.

Architect must include `time_assumptions`.

Architect must respect forbidden regions and branch budgets. It may plan within
the space exposed by AVF, but it must not reintroduce hard-masked branches.

### Executor

Executor runs a plan node.

Executor returns `ResultProposal` only. It may simulate work, produce structured
payloads, cite evidence, estimate cost, and report risk. It must never produce
`FinalOutput`.

### Post V&V

Post V&V checks `ResultProposal` objects before GTValidator.

It validates schema, evidence, time, policy, safety, consistency, and forbidden
region compliance. Invalid proposals are rejected or marked as unusable before
game-theoretic selection.

### GTValidator

GTValidator runs after Post V&V and before Root `FinalOutput`.

GT does not prove truth. It selects a robust strategy under payoff and updates
memory evolution parameters such as Elo, regret, half-life, and decay rate.

The GT layer is a decision and memory-evolution mechanism. It is not a
substitute for evidence, policy, or truth verification.

### Marennya

Marennya is intradomain reflection.

It studies recent work, related thoughts, dead ends, GT feedback, and traces
inside the same domain. Its outputs may include reflections, protocol patches,
validator patches, dead-end candidates, and heuristic adjustments.

Marennya writes first to quarantine. It can promote to `Thoughts` only after
validation. It never mutates `Work` directly.

### UP!

UP is the cross-domain transfer/opportunity layer.

It looks for protocol templates, opportunities, and structural transfers across
domains. UP writes first to quarantine and can promote to the `UP` layer only
after validation.

UP is non-actionable by default. It must not trigger external actions directly.
It never mutates `Work` directly.

## 4. Fundamental Invariants

These invariants are non-negotiable:

1. `FinalOutput` is created only by `RootOrchestrator`.
2. Executor returns `ResultProposal` only.
3. Architect returns `PlanGraph` only.
4. Architect receives `AttractorPacket`, not raw user text.
5. Every `DRSRecord` must include `TimeEnvelope`.
6. Every DRS retrieval must use `TemporalQuery`.
7. `WorldState` must not automatically pull irrelevant needles.
8. Memory-first retrieval happens before Architect.
9. `CandidateVector` values must come only from:
   - installed needles;
   - Local DRS;
   - external DRS pointers;
   - fallback templates.
10. `CandidateVector` values must not be freely hallucinated by LLM.
11. AVF must run before Architect.
12. AVF must hard-mask forbidden vectors before Architect.
13. AVF scoring must be deterministic/vectorized, not free-form LLM reasoning.
14. Post V&V runs before GTValidator.
15. GTValidator must update Elo/regret/half_life or explicitly return
    `no_update`.
16. Marennya and UP must write to quarantine first.
17. Marennya and UP must not mutate `Work` directly.
18. `Work` / `Thoughts` / `UP` / `DeadEnds` / `Quarantine` must remain
    separate.
19. Exploration cannot bypass `HardMask`.
20. User-origin hypothesis gets no automatic trust boost.

These rules preserve the difference between a controlled cognitive runtime and
a normal agent loop. A component may be stubbed in the MVP, but the contract must
remain intact.

## 5. Time Model

Time is first-class because memory is not timeless. A reused record can be
historically true, locally useful, stale for the current task, or invalid for
the current `as_of`. The system must know which case it is handling.

Every `DRSRecord` requires `TimeEnvelope`.

```text
TimeEnvelope TE = (PT, KT, ET, CT, TTL)
```

Where:

- `PT` = Physical Time / `created_at`.
- `KT` = Knowledge Time / `as_of`.
- `ET` = Event Time / domain event time.
- `CT` = Context Time / session/task anchor.
- `TTL` = initial life window.

Every retrieval requires `TemporalQuery`.

```text
TemporalQuery TQ = (as_of, time_range, freshness_bias, max_age)
```

Age by knowledge time:

```text
Age(r, t) = t - KT(r)
```

Effective age:

```text
Age_effective(r) =
omega_PT * Age_PT +
omega_KT * Age_KT +
omega_ET * Age_ET
```

with:

```text
omega_PT + omega_KT + omega_ET = 1
```

Time decay:

```text
W_t(r) = e^(-lambda * Delta t)
```

```text
lambda = ln(2) / t_half
```

Equivalent:

```text
W_t(r) = 2^(-Delta t / t_half)
```

FreshnessBoost modifies effective half-life:

```text
t_half_effective = t_half_base * FreshnessBoost
```

Temporal conflict means two records can both be valid historically but not
equally valid for the current `as_of`. This is why old profile/context snapshots
are not blindly reused. Retrieval must compare records through temporal
validity, freshness, and task relevance.

## 6. DRS: Distributed Reflexive Store / Local DRS in MVP

DRS is not just memory. It is addressable, layered, time-aware, GT-aware memory.

The MVP uses local JSON DRS. The local implementation proves the memory contract
without implementing the future external DRS network.

LocalDRS is the only implemented DRS runtime. External DRS remains a future
pointer/protocol boundary. Global DRS / Internet of Meaning is not implemented.
DRS records are addressable meaning records with `TimeEnvelope`, provenance, GT
metadata, validation metadata, trace refs, and routing semantics.

Layers:

- `Work`: canonical task outcomes and accepted records.
- `Thoughts`: validated Marennya reflections / intradomain lessons.
- `UP`: validated cross-domain opportunities / protocol templates.
- `DeadEnds`: negative paths / failed branches / forbidden approaches.
- `Quarantine`: raw Marennya/UP drafts before validation.

`DRSRecord` fields:

- `record_id`;
- `layer`;
- `type`;
- `domain`;
- `content`;
- `time_envelope`;
- `provenance`;
- optional `gt`;
- `status`.

### Pointer-first DRS model

DRS behaves like a more complex DNS for memory, capabilities, and knowledge
routes. It is a registry/resolver/index for addressable memory records, not a
centralized dump of all user memory.

DRS may point to local, private, project, vault, vector, document, or external
DRS storage. A pointer-first record stores layer, domain, type, pointer metadata,
access policy, time envelope, provenance, GT metadata, summary, and hash. The
payload itself may live elsewhere.

Personal secrets, identity data, payment data, credentials, tokens, passwords,
passport numbers, card numbers, and private keys must live in secure
vault/storage systems, not directly inside DRS record content. DRS records may
reference those secure locations through explicit storage pointers and access
policies.

Future production versions should use a Credential Vault / sealed secret slot
model. DRS may store references, scopes, provenance, permission rules, access
policies, and audit metadata for secrets, but not raw secret values. LLM/SLM
components may reason over the existence, type, scope, and permission state of
a sealed slot without seeing the secret itself.

For the MVP, inline content is allowed only for mock demo simplicity. Inline
content must remain small, local, non-secret, and schema-compatible.

Memory-first reuse formula:

```text
ReuseScore(r) =
a*Q(r)
+ b*Freshness(r)
+ c*GTTrust(r)
+ d*SemanticSim(r, I)
- e*Risk(r)
- f*Conflict(r)
```

Reuse allowed if:

```text
ReuseScore(r) >= tau_reuse
and PolicyOK(r) = true
and Freshness(r) >= tau_fresh
```

Semantic similarity:

```text
Sim(q, r) = cos(Emb(q), Emb(r))
```

```text
cos(a,b) = (a * b) / (||a|| ||b||)
```

Optional token similarity:

```text
J(A,B) = |A intersection B| / |A union B|
```

Combined:

```text
SemanticScore =
alpha*cos(Emb(q), Emb(r))
+ beta*J(tokens(q), tokens(r))
```

## 7. WorldState

`WorldState` is assembled by Root before planning.

`WorldState` includes:

- `time_context`;
- `temporal_query`;
- `user_context`;
- `session_context`;
- `local_drs_summary`;
- `active_policy`;
- available needles;
- recent trace refs.

`WorldState` is not a dump of all memory. It is a relevant, time-aware packet.
It must not automatically include irrelevant context like weather unless the
intent or an installed needle requires it.

## 8. Fractalization

Minimal cognitive cell:

```text
Cell_min = (Orchestrator, Architect, Executor)
```

The operational canonical cell used by the runtime is wider:

```text
Cell = (
  Orchestrator,
  Architect,
  Executor / DAG Runner,
  Post V&V,
  GT / selection,
  Budget,
  Policy,
  EventLog,
  MemoryIO
)
```

`Cell_min` explains recursion. The wider `Cell` explains the MVP/runtime
contract.

Recursive rule:

```text
Cell(T) =
Executor(T), if Atomic(T) = true
Orchestrator(Architect(T)), if Atomic(T) = false
```

Task decomposition:

```text
F(T, C, B) -> (G, {t_1, t_2, ..., t_n})
```

where:

- `T` = task;
- `C` = context / `WorldState` / `AttractorPacket`;
- `B` = budget;
- `G` = graph;
- `t_i` = subtasks.

PlanGraph:

```text
P = (N, E)
```

`N` is the set of nodes. `E` is the set of directed edges.

Ready set:

```text
Ready(P) = { n in N | deps(n) subset Completed }
```

Horizontal branching means independent branches can run in parallel.

Vertical branching means `t1 -> t2 -> t3`, where the next step requires previous
output.

Hybrid branching means a graph may expand, contract, and expand again.

Atomic condition:

```text
Atomic(t)=true
```

if at least one holds:

- `CostEstimate(t) < tau_atomic_cost`;
- `Uncertainty(t) < tau_uncertainty`;
- `Depth(t) >= Depth_max`;
- `ToolAvailable(t)=true`;
- `NoUsefulDecomposition(t)=true`.

Budget propagation:

```text
sum B_i <= B_parent
```

Branch expansion:

```text
ExpectedUtility(t_i) - ExpectedCost(t_i) > tau_expand
```

or:

```text
Uncertainty(t_i) > tau_uncertainty
and ValueOfInformation(t_i) > tau_voi
```

Branch pruning:

```text
HardMask(t_i)=0
or Viability(t_i) < tau_prune
or Budget(t_i)=0
or DeadEndMatch(t_i) > tau_deadend
```

Axiom:

```text
A vassal's vassal is not my vassal.
```

Root sets boundary conditions, budgets, forbidden regions, and expected output
schema. Root does not micromanage nested cluster internals. Root evaluates
returned snapshots.

## 9. AVF - Attractor Viability Field

AVF is the pre-fractal branch viability field.

AVF does not solve the task. AVF decides which branches have the right to be
born.

Position:

```text
WorldState + DRS
-> CandidateVectorGenerator
-> AVF
-> AttractorPacket
-> Architect
```

CandidateVector sources:

```text
V = V_needles union V_localDRS union V_externalPointers union V_fallback
```

Hard invariant:

```text
V must not come from free LLM hallucination.
```

CandidateVector features:

```text
x_i = [
rel_i,
p_success_i,
utility_i,
cost_i,
risk_i,
time_penalty_i,
policy_conflict_i,
gt_prior_i,
novelty_i
]
```

Feature matrix:

```text
X in R^(n x d)
```

`d = 9` in MVP.

Weight vector:

```text
w = [
alpha,
beta,
chi,
-delta,
-epsilon,
-zeta,
-eta,
lambda,
rho
]
```

Viability score:

```text
VS(v_i) =
alpha*rel_i
+ beta*p_success_i
+ chi*utility_i
- delta*cost_i
- epsilon*risk_i
- zeta*time_penalty_i
- eta*policy_conflict_i
+ lambda*gt_prior_i
+ rho*novelty_i
```

Vectorized form:

```text
S = Xw
```

HardMask:

```text
HM(v_i) in {0,1}
```

If `v_i` is forbidden:

```text
HM(v_i)=0
```

SoftMask:

```text
SM(v_i) in [0,1]
```

Final viability:

```text
FV(v_i) = HM(v_i) * SM(v_i) * VS(v_i)
```

Top-K:

```text
TopK = argtopk(FV(v_i), k)
```

Exploration:

```text
Selected = TopK_exploit union TopK_explore
```

Exploration cannot bypass `HardMask`.

Cold start:

```text
history_confidence = low
fallback_to_architect_creativity = true
requires_feedback_writeback = true
```

Boost novelty:

```text
rho' = rho + Delta_cold
```

`AttractorPacket` includes:

- goal;
- `world_state_ref`;
- `time_context`;
- `hard_forbidden_regions`;
- `candidate_vectors`;
- `branch_budget`;
- `exploration_budget`;
- `architect_instructions`.

## 10. Architect and PlanGraph

Architect receives `AttractorPacket`.

Architect must output `PlanGraph`.

`PlanGraph` includes:

- `plan_id`;
- `source_packet_id`;
- `time_assumptions`;
- nodes;
- edges;
- executor assignments.

Architect must not:

- create `FinalOutput`;
- answer user;
- expand forbidden regions;
- ignore branch budgets.

## 11. Executors and ResultProposal

Executor receives a plan node and returns `ResultProposal`.

`ResultProposal` includes:

- `proposal_id`;
- `producer`;
- `vector_id`;
- `plan_id`;
- `result_payload`;
- evidence;
- cost;
- risks;
- `time_envelope`;
- `trace_refs`.

Executor must not include `final_output`.

## 12. Post V&V

Post V&V validates `ResultProposal` objects before GT.

Scores:

```text
VV(r_i) =
[
schema_i,
evidence_i,
policy_i,
time_i,
safety_i,
consistency_i
]
```

Overall:

```text
VVScore(r_i) =
a*schema_i
+ b*evidence_i
+ c*policy_i
+ d*time_i
+ e*safety_i
+ f*consistency_i
```

Reject rules:

```text
If schema_i = 0 -> reject.
If policy_i = 0 -> reject.
```

Evidence score:

```text
evidence_i = claims_supported / claims_total
```

Time score:

```text
time_i = Freshness(r_i) * TimeEnvelopeValid(r_i)
```

## 13. GTValidator

GTValidator runs after Post V&V.

GT does not prove truth. GT selects a robust candidate under payoff and updates
memory evolution.

Candidates:

```text
C = {c_1, c_2, ..., c_m}
```

Payoff:

```text
Payoff(c_i) =
w1*U_i
+ w2*R_i
- w3*C_i
- w4*V_i
+ w5*Tr_i
+ w6*N_i
```

where:

- `U` = utility;
- `R` = robustness;
- `C` = compute/cost;
- `V` = violations;
- `Tr` = transfer score;
- `N` = novelty guard.

Robustness:

```text
R_i =
a*evidence_i
+ b*consistency_i
+ c*repeatability_i
+ d*fallback_support_i
```

Cost normalized:

```text
C_i =
a*tokens_i
+ b*walltime_i
+ c*toolcalls_i
+ d*money_i
```

Novelty guard:

```text
N_i = Novelty_i * (1 - Risk_i)
```

Elo expected score:

```text
E_i = 1 / (1 + 10^((R_j - R_i)/400))
```

Elo update:

```text
R'_i = R_i + K * (S_i - E_i)
```

Regret:

```text
Regret(c_i) = Payoff(c*) - Payoff(c_i)
```

where:

```text
c* = argmax Payoff(c)
```

Mixed strategy:

```text
mix_i =
exp(tau*Payoff_i) / sum_j exp(tau*Payoff_j)
```

Dominance:

Candidate `a` strictly dominates `b` if all metrics are `>=` and at least one
metric is `>`.

Early stopping:

If payoff gap and confidence exceed thresholds, tournament may stop early.

### GT v0.2 AVF/vector-aware scoring design

GT is not TruthProof. It does not prove that an answer is true or that an
external action happened. GT selects the most viable candidate under explicit
payoff and policy constraints after Post V&V.

The current v0.1/v0.1.1 GT report surface should be preserved:

- `candidate_scores`;
- `winner_payoff`;
- `regret_summary`;
- `tie_detected`;
- `tie_break_rule`.

GT v0.2 should add architecture-aware signals to the scoring surface:

- `vector_id`;
- AVF `final_viability`;
- AVF `soft_mask`;
- `artifact_type`;
- `execution_status`;
- human burden / `needs_user` burden;
- `fallback_role_penalty`;
- `primary_path_bonus`;
- `risk_level`;
- `dependency_depth`;
- `reuse_potential`;
- `evidence_strength` when available.

Conceptual payoff:

```text
payoff_v0_2 =
    base_payoff_v0_1
    + avf_viability_bonus
    + primary_path_bonus
    + reuse_potential_bonus
    + evidence_strength_bonus
    - fallback_role_penalty
    - human_burden_penalty
    - dependency_depth_penalty
    - risk_level_penalty
```

Vector role policy:

- `official_online_request`: primary path; receives a positive bonus when safe.
- `personal_visit`: backup/physical path; receives a moderate bonus when the
  official online path is incomplete.
- `legal_representative`: delegated path; useful, but has higher authorization
  burden.
- `fallback_exploration`: exploratory fallback; should not beat primary paths
  only because of lexical id.
- `illegal_coercion`: forbidden; `HardMask=0`; never enters GT as an executable
  winner.

If v0.2 payoff is still tied, the tie-break should be:

1. lower risk;
2. lower human burden;
3. higher AVF `final_viability`;
4. higher evidence strength;
5. lower cost;
6. higher robustness;
7. deterministic `proposal_id`.

GT v0.2 boundaries:

- no LLM calls;
- no action execution;
- no direct DRS mutation;
- richer scoring metadata may feed Marennya/UP later;
- Marennya/UP may consume GT scores, regret, dominance, and dead-end signals.

Expected future tests:

- `fallback_exploration` cannot win over `official_online_request` when base
  payoff is equal and the official path is safe.
- Higher AVF viability wins when risk and cost are equal.
- A high-burden `needs_user` candidate loses to a completed lower-burden
  candidate when payoff is otherwise equal.
- `illegal_coercion` never appears as executable winner.
- Tie information remains visible if all v0.2 components are equal.

## 14. GT-TTL and Memory Evolution

Half-life:

```text
t_half(r) =
base
* sigmoid((Elo(r)-mu)/s)
* (1 - Regret_norm(r))
* FreshnessBoost(r)
```

Sigmoid:

```text
sigmoid(x) = 1 / (1 + e^(-x))
```

Decay rate:

```text
decay_rate(r) = ln(2) / t_half(r)
```

Memory survival:

```text
Survival(r,t) =
GTTrust(r)
* Freshness(r,t)
* ReuseFrequency(r)
* UtilityHistory(r)
```

Garbage/archive rule:

Archive if:

```text
Survival(r,t) < tau_archive
or Regret(r) > tau_regret
or ConflictWithWork(r)=true and newer Work has higher temporal priority.
```

Smart TTL extension:

```text
TTL'(r)=TTL(r)*(1 + alpha*Utility(r) + beta*Reuse(r) + gamma*EloBoost(r))
```

Smart TTL shrink:

```text
TTL'(r)=TTL(r)*(1 - delta*Regret(r) - epsilon*FailureRate(r))
```

## 15. Marennya

Marennya is intradomain reflection.

Triggers:

```text
Trigger_M =
Idle
or AfterTask
or Staleness
or FailurePattern
or GTRegretHigh
```

Input bundle:

```text
B_M =
Work_recent
union Thoughts_related
union DeadEnds
union GTFeedback
union TraceRefs
```

Output types:

- reflection;
- protocol_patch;
- validator_patch;
- dead_end_candidate;
- heuristic_adjustment.

Patch utility:

```text
U(p)=
ExpectedImprovement(p)
- Risk(p)
- Cost(p)
+ Robustness(p)
```

Validation:

```text
Validate_M(p)=
Static
and Dedup
and RAG
and SelfConsistency
and Utility
and Safety
```

Marennya output goes to Quarantine first. Only after validation can it be
promoted to `Thoughts`. Marennya must never mutate `Work` directly.

Marennya GT game:

```text
Payoff_M(p)=
w1*Utility(p)
+ w2*Robustness(p)
- w3*Risk(p)
- w4*Cost(p)
- w5*HallucinationRisk(p)
```

## 16. UP!

UP is cross-domain transfer.

Triggers:

```text
Trigger_UP =
AfterTask
or PatternRepetition
or HighUtilityThought
or Idle
```

Input bundle:

```text
B_UP =
Work
union Thoughts
union UP_related
union GTFeedback
```

Candidate types:

- opportunity;
- protocol_template;
- link.

Energy:

```text
E(u)=
Novelty(u)*ExpectedUtility(u) /
(Risk(u)+CostTokens(u)+epsilon)
```

Transfer score:

```text
Transfer(u)=
alpha*Sim_structure
+ beta*Sim_constraints
+ gamma*Utility
- delta*Risk
```

Validation:

```text
Validate_UP(u)=
Static
and Dedup
and RAGSupport
and SelfConsistency
and Utility
and Safety
```

If valid:

```text
u -> DRS_UP
```

UP GT game:

```text
Payoff_UP(u)=
w1*Transfer(u)
+ w2*ExpectedUtility(u)
+ w3*Novelty(u)
- w4*Risk(u)
- w5*Cost(u)
```

UP is non-actionable by default. UP must not trigger external actions directly.

## 17. AVF Feedback / ViabilityFeedback

After task execution, each vector can produce feedback:

```text
VF(v_i) =
(predicted, actual, delta, failure_modes, gt_update)
```

Prediction error:

```text
Error(v_i)=
|PredictedViability(v_i) - ActualUtility(v_i)|
```

If vector was overestimated:

```text
FV_future(v_i)=FV(v_i) - alpha*Error(v_i)
```

If vector was underestimated:

```text
FV_future(v_i)=FV(v_i) + beta*PositiveSurprise(v_i)
```

DeadEnd promotion:

If:

```text
FailureRate(v_i) > tau_fail
and ContextMatch(v_i) > tau_context
```

then:

```text
v_i -> DeadEnds
```

Successful protocol promotion:

If:

```text
SuccessRate(v_i) > tau_success
and Regret(v_i) < tau_regret
```

then the candidate can become `Work` or `Thoughts` depending on type.

## 18. Anti-Sycophancy

User-origin hypothesis gets no trust boost solely because the user proposed it:

```text
TrustBoost(v_i | source=user) = 0
```

Trust:

```text
Trust(v_i)=
BaseTrust(v_i)
+ EvidenceSupport(v_i)
+ GTPrior(v_i)
- ConflictPenalty(v_i)
```

`BaseTrust(user_claim)` must not be higher than `BaseTrust(system_claim)`.

Risky hypotheses require counter-vector:

```text
If Risk(v_i) > tau
then GenerateCounterVector(v_i)
```

Counter-vector must come from an allowed source:

- system template;
- red-team needle;
- DRS conflict record.

## 19. Continuous / Delta Runtime Future Layer

This is future-ready, not required for MVP.

WorldState as stream:

```text
W(t)
```

Delta:

```text
Delta W_t = W_t - W_(t-1)
```

Structurally:

```text
Delta W_t = added union removed union changed union expired
```

Selective activation:

```text
Relevance(module, Delta W_t) > tau_wake
```

ActiveNeedleSet:

```text
ANS_t =
{ n in Needles | WakeScore(n, Delta W_t) > tau }
```

Delta fractal:

```text
F_t = Patch(F_(t-1), Delta W_t)
```

Scope of recomputation:

```text
Scope(Delta W_t)=
{ nodes in F | depends_on(nodes, changed_state) }
```

Important:

100Hz does not mean full recompute. 100Hz means possible delta activation
frequency.

## 20. Audit and Hash Chain

Audit / hash-chain hardening v0.1 is a local proof-level append-only linkage
over current proof artifacts. It hardens the Root-centered proof geometry, not
a linear long-chain. Hash-chain proves continuity, not truth.

Content hash:

```text
H(r)=SHA256(canonical_json(r))
```

Hash chain:

```text
H_i = SHA256(R_i || H_(i-1))
```

`AuditEvent`:

- kind;
- payload;
- timestamp;
- hash.

Used for:

- DRS append;
- registry append;
- GT report;
- `FinalOutput`;
- Marennya/UP promotion;
- external DRS pointer publication.

The v0.1 proof does not mutate DRS or source artifacts, decide truth, validate
semantic correctness, grant authority, replace GT / ConflictCheck / Root,
implement blockchain, or provide production persistence.

## 20.1 Applied Warehouse Semantic Proof

Applied Warehouse Semantic Demo / Warehouse-Style Proof v0.1 is the first
applied "meat" proof over the Root-centered canonical geometry. It processes
warehouse W-17 / dispatch D-2042 from local WorldState through DRS retrieval,
controlled route assembly, gates, AVF, bounded planning/execution, Post V&V,
GT, Root Final, DRS Lifecycle, ConflictCheck, and proof-level audit linkage.

The explicit stock evidence is `water_filter` required=8 and current=6. Root
Final therefore reports `dispatch_readiness=not_ready`, missing
`water_filter=2`, and no external action. `invalid_ready_certificate` is
rejected; `completed_not_ready_certificate` is accepted; needs-user restock
confirmation remains a secondary valid recommendation.

The applied proof creates explicit PlanGraph, node-result, validation, GT
selection, local lifecycle, ConflictReport, applied artifact, and applied audit
entry objects. PASS depends on `validate_applied_report_consistency()`, which
rejects a wrong applied audit hash, missing validation row, or missing
short-stock conflict report.

These lifecycle and audit objects are local proof evidence only. They are not
production persistence, global/external DRS, blockchain, or production
warehouse execution. Applied demos must not automatically create
`protocol_candidate` or `needle_candidate` unless that lifecycle is explicitly
under test. Root remains final authority; GT and ConflictCheck remain advisory;
hash-chain proves continuity, not truth.

## 20.2 Applied Certificate / Document Readiness Proof

Applied Certificate / Document Readiness Demo v0.1 is the second applied
semantic proof. It demonstrates that the Root-centered canonical geometry
transfers from warehouse readiness to certificate/document readiness.

For application APP-77 / certificate request CERT-310, local WorldState shows
valid passport and residency documents, an expired insurance certificate, and
a missing payment receipt. Root Final must not say ready; it reports
`certificate_readiness=not_ready`, preserves both blocking reasons, and
executes no external submission.

The proof creates explicit applied certificate PlanGraph, document-check,
validation, GT-selection, local lifecycle, ConflictReport, artifact, and audit
entry objects. The completed not-ready result is accepted, invalid ready is
rejected, and needs-user document update remains a valid secondary
recommendation. ConflictCheck remains advisory until Root; hash-chain proves
continuity, not truth.

The local lifecycle records are proof evidence only, not production
persistence or global/external DRS. This demo does not test promotion:
`protocol_candidate_created=false`, `needle_candidate_created=false`, and
`installed_needle_created=false`. The next applied layer is Permission/NeedsUser
UX proof, not Marennya / UP or NeedleForge.

## 20.3 Permission / NeedsUser UX Proof

Permission / NeedsUser UX Proof v0.1 closes the permission boundary after the
warehouse and certificate applied demos. Permission is not execution, approval
is not completed action, and `needs_user` is not failure.

Five deterministic scenarios cover warehouse dispatch/restock permission,
certificate submission with missing documents, unsafe permission bypass,
explicit denial, and proof-only approval. Dispatch, restock, and submission do
not execute. Invalid permission bypass and completed-action-without-execution
claims are rejected; denial remains blocked; proof-only approval produces only
`permission_ready_for_future_action_layer`.

The proof creates explicit permission request, needs-user, response,
validation, GT, Root Final, local lifecycle, ConflictReport, proof artifact,
and audit entry objects. Root may create `needs_user_pending_permission`,
`denied_by_user_blocked`, or `permission_ready_for_future_action_layer`; it
must not create completed dispatch, restock, submission, or external-action
claims.

Lifecycle records are local proof evidence only: `permission_experience_record`,
`permission_blocked_trace`, `permission_denial_deadend`,
`permission_bypass_quarantine`, and `permission_future_action_reuse_candidate`.
ConflictCheck remains advisory until Root. The permission audit entry hashes
the permission proof artifact; hash-chain proves continuity, not truth.

This proof creates no protocol candidate, needle candidate, or installed
needle. It is not production UX, production permission service, real action,
production persistence, global/external DRS, NeedleForge, or Marennya / UP.
The following completed capability-evolution layer is NeedleCandidate
lifecycle / NeedleForge prototype.

## 20.4 NeedleCandidate Lifecycle / NeedleForge Prototype

NeedleCandidate lifecycle / NeedleForge prototype v0.1 is the first
proof-level capability-evolution layer after Permission / NeedsUser. Repeated
safe applied patterns may become bounded NeedleCandidate objects only after
accepted applied evidence, explicit permission boundaries, unsafe-variant
rejection, advisory GT review, and Root disposition.

The safe warehouse candidate may prepare a restock request only; it forbids
dispatch, restock execution, and external ordering. The safe certificate
candidate may prepare a user document-update request only; it forbids
submission, government API contact, and ready-without-documents claims. Both
require permission, remain non-installable, and reach Root only as
`candidate_pending_review`.

The safe candidate IDs are
`needle_candidate_warehouse_restock_readiness_v0_1` and
`needle_candidate_certificate_document_update_v0_1`. Their allowed action
classes are `prepare_restock_request_only` and
`prepare_user_document_update_request_only`. The warehouse evidence is W-17 /
D-2042 `water_filter short_by_2`; the certificate evidence is APP-77 /
CERT-310 expired insurance plus missing payment receipt.

Unsafe auto-submit and permission-bypass candidates are quarantined; ready
override is rejected as conflict. Validation also rejects an installed needle
without Root installation. GT is advisory, is not truth proof, recommends only
the two safe candidates, and cannot install needles. Root alone may create
`candidate_pending_review`, `candidate_rejected`, or `candidate_quarantined`.
The exact unsafe reasons are external submission forbidden in the proof-level
layer, contradiction with applied evidence, and violation of the
Permission/NeedsUser proof. Root must not create an installed or production
needle, executable external action, completed dispatch/restock/submission, or
ready override.

Validation accepts `warehouse_restock_candidate` and
`certificate_document_update_candidate` only as
`accepted_as_candidate_pending_review`. It rejects
`unsafe_auto_submit_candidate` and `unsafe_permission_bypass_candidate` as
`rejected_quarantined`, `unsafe_ready_override_candidate` as
`rejected_conflict`, and `installed_needle_without_root_install` as rejected.

The proof creates explicit source evidence, candidate, validation, GT, Root
Final, local lifecycle, ConflictReport, proof artifact, and audit entry
objects. Lifecycle records are local proof evidence only, not production
persistence, global DRS, or an installed registry. ConflictCheck remains
advisory until Root. The audit entry hashes the proof artifact and links to
prior audit evidence; hash-chain proves continuity, not truth.

The explicit artifact groups are `needle_candidate_source_evidence`,
`needle_candidate_artifacts`, `needle_candidate_validation_rows`,
`needle_candidate_gt_selection`, `needle_candidate_root_final_artifacts`,
`needle_candidate_drs_lifecycle_records`, `needle_candidate_conflict_reports`,
`needle_candidate_proof_artifact`, and `needle_candidate_audit_entry`.
Candidates carry source/domain scope, allowed action class, forbidden actions,
permission and Root-review requirements, `proof_only=true`,
`installable_now=false`, `installed_needle_created=false`,
`production_persistence=false`, and `global_drs_write=false`.

The local lifecycle records are `needle_candidate_experience_record`,
`needle_candidate_reuse_pattern_record`,
`needle_candidate_pending_review_record`,
`needle_candidate_quarantine_auto_submit`,
`needle_candidate_quarantine_permission_bypass`, and
`needle_candidate_conflict_ready_override`. ConflictCheck flags auto-submit
against the no-external-action boundary, ready override against applied
evidence, and permission bypass against Permission/NeedsUser, while preserving
no-conflict reports for both safe candidates.

The exact conflict reports are
`conflict_auto_submit_candidate_vs_no_external_action_boundary`,
`conflict_ready_override_candidate_vs_applied_evidence`, and
`conflict_permission_bypass_candidate_vs_permission_needsuser_boundary`, plus
no-conflict reports for the safe warehouse and certificate candidates.

The proof audit entry is `audit_needlecandidate_lifecycle_v0_1`. It hashes
`needle_candidate_proof_artifact`, links to the previous proof hash-chain, is
proof-only, does not write global DRS or production persistence, and does not
decide truth.

NeedleCandidate is not an installed Needle. NeedleForge prototype is not
production NeedleFactory. No installed needle, real action, production
persistence, global/external DRS, External DRS pointer protocol, Marennya, or
UP is implemented.

## 20.5 Applied DRS Retrieval / Reuse

Applied DRS Retrieval / Reuse v0.1 is a deterministic local proof that DRS may
retrieve prior applied evidence and propose bounded reuse candidates, but
retrieval is not authority. ReuseScore is advisory, semantic similarity is
insufficient, GT remains advisory, and Root alone decides final reuse.

Seven scenarios verify warehouse partial reuse, certificate needs-user reuse,
stale high-similarity evidence, quarantined and deadend reuse attempts, a
wrong-domain near match, and a permission trace incorrectly proposed as
completed-action evidence. Freshness, WorldState compatibility, permission,
quarantine/deadend proximity, ConflictCheck, and audit evidence remain
mandatory boundaries.

The explicit artifact groups are `applied_drs_query_artifacts`,
`applied_drs_retrieval_candidates`, `applied_reuse_score_rows`,
`applied_reuse_gate_rows`, `applied_reuse_worldstate_checks`,
`applied_reuse_freshness_checks`,
`applied_reuse_quarantine_deadend_checks`,
`applied_reuse_conflict_reports`, `applied_reuse_gt_selection`,
`applied_reuse_root_final_artifacts`,
`applied_reuse_drs_lifecycle_records`, `applied_reuse_proof_artifact`, and
`applied_reuse_audit_entry`.

Root may decide `partial_reuse_then_rerun_validation`,
`partial_reuse_then_needs_user`, `rerun_required`,
`block_reuse_quarantined_record`, `block_or_ask_user`, or
`reject_completed_action_reuse`. Root must not create direct ready, completed
dispatch/restock/submission/external action, protocol candidate, NeedleCandidate,
installed needle, or global DRS write.

Gate outcomes are explicit: warehouse similarity is
`accepted_as_partial_reuse_candidate`; certificate similarity is
`accepted_as_needs_user_reuse_candidate`; stale evidence is
`downgraded_to_rerun_required`; quarantine is `blocked_quarantine`; deadend is
`blocked_or_ask_user`; wrong-domain similarity is `rejected_domain_mismatch`;
and permission-as-completed-action is `rejected_conflict`.

The proof creates local proof-level lifecycle records only. ConflictCheck flags
permission-as-completed-action, wrong-domain, stale, quarantined, and deadend
reuse risks while preserving no-conflict reports for bounded warehouse partial
reuse and certificate needs-user reuse. ConflictCheck remains advisory until
Root. `audit_applied_drs_retrieval_reuse_v0_1` hashes the proof artifact and
links to prior audit evidence; hash-chain proves continuity, not truth.

The local lifecycle records are `applied_reuse_query_record`,
`applied_reuse_candidate_record`, `applied_partial_reuse_record`,
`applied_needs_user_reuse_record`, `applied_stale_reuse_downgrade_record`,
`applied_quarantine_reuse_block_record`, `applied_deadend_reuse_block_record`,
`applied_domain_mismatch_record`, and
`applied_permission_trace_conflict_record`. ConflictCheck reports cover
permission trace reuse as completed action, wrong-domain near match, stale
high-similarity evidence, quarantined reuse, and deadend reuse, plus no-conflict
reports for warehouse partial reuse and certificate needs-user reuse.

Proof status: PASS, scenarios_verified=7, targeted tests passed=22, focused
tests passed=120, full suite passed=1269 with 37 warnings, sensitive scan
clear, explicit artifacts consistent, and production autonomy not claimed.
The module-scoped fixture optimization removed repeated heavy report collection
and reduced targeted proof test time to about 15.55 seconds. Evidence:
`docs/audit_reports/auditor_applied_drs_retrieval_reuse.log` and
`docs/audit_reports/auditor_applied_drs_retrieval_reuse_postcommit.log`;
commits `0bbf81a`, `3fdc78e`, and `420b005`.

This layer consumes NeedleCandidate source proof but creates no new
NeedleCandidate. It is not production DRS, persistence, a real vector database,
global/external DRS, External DRS pointer protocol, direct ready, real external
action, Marennya, UP, or autonomous production runtime. After the local Needle
adversarial / safety checkpoint, the next engineering direction is External
DRS Pointer Protocol v0.1, not External DRS implementation.

## 20.6 Applied Stack Checkpoint — DRS Adversarial / Super-Smoke / Human Walkthrough

The deterministic local applied stack is closed through three auditor-facing
views:

- DRS Adversarial Stress Pack v0.1 blocks, rejects, or downgrades eight hostile
  memory scenarios: spoofed score, fake freshness, quarantine laundering,
  deadend laundering, permission laundering, domain camouflage, fake audit
  hash, and injected Root Final.
- The all-layers applied super-smoke observes warehouse, certificate,
  Permission/NeedsUser, NeedleCandidate lifecycle, applied DRS retrieval/reuse,
  DRS adversarial stress, ConflictCheck, and audit/hash-chain together. All
  eight source statuses PASS.
- The human applied auditor walkthrough is explanatory prose only. It is not a
  proof layer, capability layer, runtime, or test suite.

Root remains final authority. DRS retrieval, ReuseScore, GT, ConflictCheck,
audit/hash-chain, NeedleCandidate, and permission approval are not final
authority. Permission approval is not completed action. Hostile DRS records
cannot force reuse, Root bypass, ready state, completed action, candidate or
installed-needle creation, production persistence, or global/external DRS
writes.

Evidence: DRS adversarial targeted tests passed=14; all-layers super-smoke
targeted tests passed=12; full suite passed=1295 with 37 warnings; walkthrough
manually inspected; sensitive scan clear. Commits: `398dace`, `9824431`,
`27a5b1b`, and `db18c6e`.

This checkpoint has no real external action, completed dispatch/restock/
certificate submission, direct ready override, installed Needle, production
NeedleFactory, production persistence, global DRS, external DRS network,
Gemini call inside these deterministic demos, Telegram action, Marennya, or UP.

## 20.7 Applied + Fractal + Coupling Checkpoint

Multi-domain Applied Smoke v0.2 proves that warehouse, certificate, and travel
domains can be observed together without merging authority. Controlled Fractal
DAC Expansion v0.1 proves that a complex parent request can decompose into
bounded local child-cell candidates under Root aggregation. Dual Fractal
Coupling v0.1 proves that two parent DACs may resonate through shared semantic
evidence without transferring authority, execution, DRS writes, or
cross-finalization.

Child-cell candidates are proof-mode local structures, not real autonomous
agents. Shared evidence can inform but cannot decide. Root remains the only
final authority, and "vassal of my vassal is not my vassal" remains preserved
across decomposition and coupling.

## 20.8 Cross-domain DRS Bridge v0.1 Checkpoint

Cross-domain DRS Bridge v0.1 is accepted as `PASS_WITH_WARNINGS`. It is
passport-valid only as local proof-only traversal over already established
bounded semantic coupling edges. It grows from Dual Coupling but does not
become External DRS.

The proof demonstrates local traversal of candidate evidence from certificate
checks into travel checks. Bridge traversal can inform, but cannot decide,
finalize, execute, transfer authority, write global/external DRS, or prove
truth. Bridge traversal is not provenance laundering.

This checkpoint does not prove External DRS Pointer Protocol, remote
retrieval, public or global semantic fabric, signatures, trust registry,
revocation, production persistence, or adversarial external-record safety.
Root-only final authority and "vassal of my vassal is not my vassal" remain
preserved.

## 20.9 Needle adversarial / safety pack v0.1 Checkpoint

Needle adversarial / safety pack v0.1 is complete. It validates safety
boundaries before External DRS Pointer Protocol by proving that eight
escalation attempts are blocked. The provenance-laundering attempt is
quarantined and blocked.

The proof establishes that retrieval is not truth, DRS bridge traversal is not
authority, coupling edges are not command channels, child proposals are not
parent finals, DAG nodes are not Root, GT is not authority, audit hashes are
not truth, and NeedleCandidate is not installed Needle. Root review is required
for capability, Root final is required for action, and an explicit installation
boundary is required for a Needle.

This checkpoint does not prove full adversarial safety for all future external
records and does not implement NeedleFactory, External DRS, production RAG,
production Needle installation, or production autonomy. Root-only final
authority remains preserved.

## 20.10 External DRS Pointer Protocol v0.1 Checkpoint

External DRS Pointer Protocol v0.1 is complete as a deterministic local
proof-only pointer protocol. It validates quarantine, review, and explicit
acceptance boundaries before real External DRS or connector work.

The proof observes two external pointer candidates, accepts zero, blocks six
escalation attempts, and quarantines/blocks the unknown-source laundering
attempt. Pointer candidates cannot self-promote into trusted evidence, truth,
authority, ready status, installed Needle, DRS write, or external action.

This checkpoint does not implement External DRS, production RAG, global
semantic fabric, remote retrieval, connector/API access, production Needle
installation, or production autonomy. Root-only final authority remains
preserved.

## 20.11 Read-only Enterprise Connector Sandbox v0.1 Checkpoint

Read-only Enterprise Connector Sandbox v0.1 is complete as a deterministic
local proof-only observation boundary. It models `bank_source`,
`legal_registry_source`, `warehouse_source`, and `logistics_source` through
local read-only connector observations.

The proof creates four observations, blocks six escalation attempts, and
quarantines/blocks one unknown-source laundering attempt. Connector response
is not truth or authority; connector observation is not trusted evidence or
ready status. Root remains final authority.

This checkpoint prepares External Evidence Acceptance Gate v0.1. It does not
implement real connector/API access, network retrieval, evidence acceptance,
DRS writes, external actions, installed Needles, or production persistence.

## 20.12 External Evidence Acceptance Gate v0.1 Checkpoint

External Evidence Acceptance Gate v0.1 is complete as a deterministic local
proof-only acceptance boundary:
`ConnectorObservation -> EvidenceCandidate -> ValidationPacket -> RootDecision
-> AcceptedEvidence / RejectedEvidence / QuarantinedEvidence`.

The proof creates six candidates and validation packets. Root accepts two,
rejects three, and quarantines one. EvidenceCandidate remains candidate-only;
ValidationPacket is not Root acceptance; AcceptedEvidence exists only after
Root decision and remains bounded from truth, ready status, action, DRS write,
and Needle installation.

This checkpoint does not implement External DRS, real connectors/APIs, real
signature/trust/revocation validation, network access, production persistence,
action execution, ready status, or Needle installation. Root remains final
authority.

## 20.13 Bounded LLM Semantic Executor Node v0.1 Checkpoint

Bounded LLM Semantic Executor Node v0.1 is closed through proof, human
walkthrough, wording cleanup, and audit. It proves this bounded Executor-side
geometry:

```text
Architect-created PlanGraph -> Executor -> llm_semantic_executor_node
-> bounded mock LLM -> SemanticDraft -> SemanticDraftResultProposal
-> Post V&V -> GT advisory -> Root Final
```

The LLM is only `executor_node_capability`. It is not Root, Orchestrator,
Architect, GT, Post V&V, or a new global authority layer. It cannot create or
modify PlanGraph, route, accept evidence, prove truth, create ready status,
execute action, write DRS, install Needle, or create Root Final.

The proof created four PlanGraph nodes and one each of the bounded LLM call
envelope, SemanticDraft, SemanticDraftResultProposal, passing Post V&V check,
GT advisory, and Root semantic final. All nine adversarial attempts were
blocked. It uses `source_evidence_mode=closed_checkpoint_metadata_only` and
`source_collectors_replayed=false`; no network, Gemini call, or production
persistence occurred.

## 20.14 Enterprise Chaos Pack v0.1 Checkpoint

Enterprise Chaos Pack v0.1 is complete through proof `082753e`, human
walkthrough `104105b`, audit log `668a51a`, and docs sync.
It is a deterministic local proof-only stress pack over one dirty enterprise
request combining connector observations, accepted evidence, stale legal
state, DRS reuse, external pointer claims, cross-domain bridge traversal, LLM
SemanticDraft, NeedleCandidate, child-cell claims, GT advice, permission /
needs_user, audit hash, and ResultProposal bypass attempts.

The 18 detected and blocked escalation classes are:

- `connector_observation_to_truth`
- `connector_observation_to_accepted_evidence`
- `accepted_evidence_to_external_action`
- `accepted_evidence_to_ready_status`
- `semantic_draft_to_truth`
- `semantic_draft_to_root_final`
- `semantic_draft_to_action`
- `drs_reuse_to_authority`
- `external_pointer_to_global_drs_write`
- `bridge_traversal_to_provenance_laundering`
- `needlecandidate_to_installed_needle`
- `child_cell_to_autonomous_actor`
- `gt_recommendation_to_root_authority`
- `audit_hash_to_truth`
- `permission_needsuser_to_execution`
- `root_bypass_via_resultproposal`
- `time_envelope_stale_to_current`
- `conflicting_sources_to_ready`

The external-pointer write, bridge provenance-laundering, stale-time-envelope,
and conflicting-source attempts are quarantined and blocked. The report uses
`source_evidence_mode=closed_checkpoint_metadata_only`,
`source_collectors_replayed=false`, and `source_collectors_replayed_count=0`
for four closed checkpoints.

Observed totals: attempts observed/detected/blocked=18/18/18,
quarantined-and-blocked=4, Root finals=1, and external actions, global DRS
writes, external DRS writes, installed Needles, network calls, Gemini calls,
and production-persistence writes=0. `root_remains_final_authority=true`,
`enterprise_ready=false`, and `truth_proven=false`.

This does not prove production security or real-world safety, perform real
connector/API access, call Gemini/network, execute external action, implement
global/external DRS, install Needles, create production persistence, implement
a killer demo or multi-LLM showcase, or authorize Marennya/UP. Audit hash
records continuity, not truth.

Marennya and UP remain deferred until the internal system has mature
multi-domain traces, DRS reuse, adversarial memory defense, controlled fractal
expansion, dual coupling, DRS bridge evidence, chaos/failure traces, math
alignment, and production-boundary design. They are not early decorative
analytics.

## 21. Legacy Code Position

Legacy code is donor/reference only.

Mapping:

- `engine.py` -> RootOrchestrator skeleton.
- `manager.py` -> WorldStateAssembler donor, but weather becomes optional needle.
- `client.py` -> LocalDRS donor, but add `TimeEnvelope`, `TemporalQuery`, schema validation.
- `fractal.py` -> DAG execution donor.
- `run.py` -> executor runner donor, but wrap outputs as `ResultProposal`.
- `validators.py` / `finalize.py` -> Post V&V donor.
- `validator.py` -> GTValidator donor.
- `logging_audit.py` -> audit donor.
- `embeddings.py` / `similar_lsh.py` / `vector_store.py` -> semantic search/dedup donor.
- `index.py` / `record.py` / `resolver.py` -> future ExternalDRS pointer layer.
- `architect` / `executor` prompts -> legacy reference only.

Never use legacy `config.py`.

Never commit secrets.

## 22. MVP Demo Success Criteria

The demo succeeds if:

1. Cold-start scenario runs end-to-end.
2. Reuse scenario uses prior DRS records.
3. Forbidden vector is blocked by AVF before Architect.
4. Architect receives `AttractorPacket`.
5. Executor returns `ResultProposal` only.
6. Post V&V validates proposal.
7. GTValidator produces `GTReport` and half-life.
8. Root creates `FinalOutput`.
9. DRS writeback creates `Work` record with `TimeEnvelope`.
10. Marennya writes quarantine reflection.
11. UP writes quarantine protocol template.
12. Second run demonstrates memory-informed behavior through DRS retrieval, lineage, reuse/context metadata, or controlled direct reuse when explicitly enabled.
13. Future demos should additionally prove improved vector scoring, dead-end avoidance, and GT/TTL convergence.

## 23. Required Tone of This Document

This document is an engineering passport.

It should be detailed. It should not be marketing. It must not overpromise. It
must clearly separate the MVP from future layers.

Formulas should stay readable. Invariants should stay explicit. If a future
implementation has to choose between convenience and preserving the architecture,
it should preserve the architecture and document the tradeoff.
