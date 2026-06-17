# Math & Algorithms Appendix v0.3
# Hedgehog OS / Fractal Reflexive OS

## 0. Purpose and Document Hierarchy

This appendix records the mathematical and algorithmic basis for Hedgehog OS:

1. Time.
2. DRS and memory-first reuse.
3. Fractalization.
4. AVF - the Attractor Viability Field.
5. Post V&V.
6. GTValidator.
7. GT-TTL.
8. Marennya.
9. UP.
10. AVF feedback.
11. Anti-sycophancy.
12. Continuous / delta runtime as a future layer.
13. Audit / hash-chain.
14. Full pipeline.
15. Pseudocode.

This document is not a replacement for `specs/human_passport_v0_25.md`.

Document hierarchy:

- The Human Passport defines MVP architecture and invariants.
- This Math Appendix defines formulas and algorithmic details.
- If there is a conflict, the Human Passport controls current MVP implementation.

This file is a math and algorithm appendix only. It does not include the Strategic Expansion Map and does not define a new implementation plan.

Privacy note:

- Raw input may exist transiently inside runtime processing.
- Work DRS records should not store `raw_user_text` unless explicitly allowed by policy.
- DRS records should prefer canonical goals, summaries, pointers, trace references, and sealed slots over raw private values.

## 1. Notation

Let:

```text
I     = input intent from a user or event
G     = canonical goal
W_t   = WorldState at time t
D     = local DRS
D_ext = external DRS / external pointers
N     = installed needles
V     = {v_1, v_2, ..., v_n}, CandidateVectors / possible solution directions
A_p   = AttractorPacket
P     = PlanGraph
R     = {r_1, r_2, ..., r_m}, ResultProposals from Executors
Q     = Post V&V reports
GT    = Game Theory Validator report
F     = FinalOutput, created only by RootOrchestrator
```

Canonical pipeline:

```text
I -> G -> W_t -> DRS_retrieval -> V -> AVF -> A_p -> P -> R -> Q -> GT -> F -> DRS_writeback
```

## 2. Time: TimeEnvelope, TemporalQuery, and Knowledge Aging

### 2.1. Four Time Axes

Every knowledge record must have a TimeEnvelope:

```text
TE = (PT, KT, ET, CT, TTL)
```

Where:

```text
PT  = Physical Time = t_created
KT  = Knowledge Time = t_asof
ET  = Event Time = t_event
CT  = Context Time = c_session
TTL = Delta t_life
```

### 2.2. TimeEnvelope

Minimal object:

```json
{
  "pt_created_at": "2026-05-21T12:00:00Z",
  "kt_asof": "2026-05-21T12:00:00Z",
  "et_observed_at": null,
  "ct_session_anchor": "sess_001",
  "ttl_seconds": 2592000,
  "freshness_class": "normal"
}
```

Invariant:

```text
forall r in DRS: TimeEnvelope(r) != empty
```

Every DRS record must have a TimeEnvelope.

### 2.3. TemporalQuery

Every retrieval must have a TemporalQuery:

```text
TQ = (as_of, range, freshness_bias, max_age)
```

Example:

```json
{
  "as_of": "2026-05-21T12:00:00Z",
  "time_range": {
    "from": null,
    "to": "2026-05-21T12:00:00Z"
  },
  "freshness_bias": "prefer_recent",
  "max_age_seconds": 2592000
}
```

Invariant:

```text
DRS.query(...) => TemporalQuery required
```

### 2.4. Knowledge Age

For record `r`:

```text
Age(r, t) = t - KT(r)
PhysicalAge(r, t) = t - PT(r)
EventAge(r, t) = t - ET(r)
```

Retrieval must explicitly choose which time axis matters most:

```text
Age_effective(r) = omega_PT Age_PT + omega_KT Age_KT + omega_ET Age_ET
omega_PT + omega_KT + omega_ET = 1
```

### 2.5. Exponential Aging

Base knowledge decay:

```text
W_t(r) = e^(-lambda Delta t)
lambda = ln(2) / t_1/2
W_t(r) = 2^(-Delta t / t_1/2)
```

If the record is fresh:

```text
Delta t ~= 0 => W_t ~= 1
```

After one half-life:

```text
Delta t = t_1/2 => W_t = 0.5
```

### 2.6. FreshnessBoost

Different record types age differently:

```text
FreshnessBoost = f(freshness_class, domain, mode)

static:        2.0
slow_changing: 1.3
normal:        1.0
fast_changing: 0.5
real_time:     0.1
```

Effective half-life:

```text
t_1/2_effective = t_1/2_base * FreshnessBoost
```

### 2.7. Temporal Validity

A record is valid for a query if:

```text
valid_from(r) <= as_of(TQ) <= valid_to(r)
```

If `valid_to = null`, there is no upper bound.

If a record is stale:

```text
Age(r) > TTL(r)
```

it is not necessarily deleted, but receives a penalty:

```text
FreshnessPenalty(r) = min(1, Age(r) / TTL(r))
```

### 2.8. Temporal Conflict

Two records conflict over time if:

```text
content(r_i) != content(r_j)
KT(r_i) < KT(r_j)
```

For `prefer_recent`:

```text
priority(r_j) > priority(r_i)
```

For `historical_as_of`, the older record may have higher priority if:

```text
KT(r_i) <= as_of < KT(r_j)
```

This matters for profile-like knowledge: an older record may have been correct at that time but incorrect now.

## 3. DRS and Memory-First Reuse

Before heavy reasoning, the system remembers. If a task was solved before and passes explicit gates, Root may reuse it. A DRS retrieval hit does not automatically mean direct reuse.

Direct reuse requires:

- explicit Root shortcut permission;
- freshness;
- GT trust;
- policy checks;
- conflict checks;
- reuse score threshold;
- valid TimeEnvelope;
- permission checks when external action is involved.

If direct reuse is not allowed, prior memory may still influence the run as `context_only` / memory-informed context.

### 3.1. Normalized Intent Key

For intent `I`:

```text
K = Hash(Intent || NormalizedParams || Domain || Mode)
```

Where:

- `Intent` is the canonicalized goal.
- `NormalizedParams` are cleaned parameters.
- `Domain` is the domain.
- `Mode` is the execution mode.

Example:

```text
goal:v25:sha256(canonical_goal + normalized_params + domain + mode)
```

### 3.2. Memory-First Reuse Condition

Reuse is eligible if there exists a record:

```text
exists r in DRS
```

such that:

```text
Key(r) = K
Quality(r) > tau_reuse
Freshness(r) > tau_fresh
PolicyOK(r) = true
GTTrust(r) > tau_gt
ConflictOK(r) = true
TimeEnvelopeValid(r) = true
RootShortcutAllowed(r) = true
```

Then Root may choose:

```text
Return(Rehydrate(r))
```

and the heavy fractal loop may be skipped only through the explicit Root direct-reuse path. Otherwise, the record contributes `context_only` / memory-informed context and the pipeline continues.

### 3.3. Reuse Score

```text
ReuseScore(r) =
  a Q(r)
  + b Freshness(r)
  + c GTTrust(r)
  + d SemanticSim(r, I)
  - e Risk(r)
  - f Conflict(r)

a + b + c + d + e + f = 1
```

Reuse is eligible if:

```text
ReuseScore(r) >= tau_reuse
```

### 3.4. Semantic Similarity

If there is no exact key, semantic reuse may be scored:

```text
Sim(q, r) = cos(Emb(q), Emb(r))
cos(a,b) = (a · b) / (||a|| ||b||)
```

Jaccard / MinHash can also be used:

```text
J(A,B) = |A intersect B| / |A union B|
```

Combined score:

```text
SemanticScore =
  alpha cos(Emb(q), Emb(r))
  + beta J(tokens(q), tokens(r))
```

### 3.5. DRS Layers

```text
DRS = Work union Thoughts union UP union DeadEnds union Quarantine
```

Layer meanings:

- `Work`: accepted facts and outcomes.
- `Thoughts`: domain lessons, Marennya, method patches.
- `UP`: cross-domain transfers, protocol templates, opportunities.
- `DeadEnds`: negative experience and blocked routes.
- `Quarantine`: raw drafts not yet promoted into working layers.

Invariant:

```text
Marennya, UP -/-> Work
```

Marennya and UP cannot directly mutate Work.

### 3.6. DRS Writeback

After each completed cycle, Root writes:

```text
DRSRecord = (layer, type, content, TimeEnvelope, provenance, GT?, status)
```

Minimal object:

```json
{
  "record_id": "drs_001",
  "layer": "work",
  "type": "task_outcome",
  "domain": "government_certificate",
  "content": {},
  "time_envelope": {},
  "provenance": {
    "request_id": "req_001",
    "plan_id": "plan_001",
    "trace_refs": []
  },
  "gt": {
    "elo": 1532,
    "regret": 0.04,
    "half_life_hours": 720,
    "decay_rate": 0.00096
  },
  "status": "active"
}
```

## 4. Fractalization

Complex tasks decompose into dependency graphs. The minimal cognitive recursion is a triad, while the operational runtime cell contains additional validation, policy, budget, and memory components.

### 4.1. Cell Types

Minimal cognitive cell:

```text
Cell_min = (Orchestrator, Architect, Executor)
```

Operational runtime cell:

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

`Cell_min` explains recursion. The operational `Cell` explains the current MVP/runtime contract.

### 4.2. Task and Decomposition

Given task `T`, decomposition is:

```text
F(T, C, B) -> (G, {t_1, t_2, ..., t_n})
```

Where:

- `C` = context / WorldState / AttractorPacket.
- `B` = budget.
- `G` = dependency graph.
- `t_i` = subtasks.

### 4.3. DAG

Plan:

```text
P = (N, E)
```

Where:

- `N` = nodes.
- `E` = directed edges.

Edge:

```text
e_ij = (n_i -> n_j)
```

means:

```text
n_j depends on output(n_i)
```

### 4.4. Ready Set

At any moment:

```text
S_ready = { n in N | deps(n) subseteq S_completed }
```

A node may run when all of its dependencies are completed.

### 4.5. Horizontal Branching

```text
T -> {t_1, t_2, t_3}
deps(t_i) = empty
```

Parallelism:

```text
Parallelism = |{t_i}_ready|
Parallelism <= B_parallel
```

### 4.6. Vertical Chain

```text
t_1 -> t_2 -> t_3 -> ... -> t_k
t_{i+1} = f_i(output(t_i))
output(t_i) required for t_{i+1}
```

### 4.7. Hybrid Branching

```text
T -> {a_1, a_2}
a_1 -> b_1 -> c_1
a_2 -> {b_2, b_3}
```

The graph may narrow and widen repeatedly.

### 4.8. Atomic Condition

A subtask is atomic if:

```text
Atomic(t) = true
```

when at least one condition holds:

```text
CostEstimate(t) < tau_atomic_cost
Uncertainty(t) < tau_uncertainty
Depth(t) >= Depth_max
ToolAvailable(t) = true
NoUsefulDecomposition(t) = true
```

If a task is atomic:

```text
Executor(t) -> ResultProposal
```

If it is not atomic:

```text
Architect(t) -> child PlanGraph / SubPlan boundary
```

`SubPlan` here means a PlanGraph-shaped child boundary. Architect still returns PlanGraph only; execution of that graph belongs to Executors / DAG Runner, which return ResultProposal only.

### 4.9. Recursive Fractal Cell

```text
Cell(T) =
  Executor(T), if Atomic(T) = true
  Orchestrator(Architect(T)), if Atomic(T) = false
```

This is a structural recursion formula, not an authority transfer rule.

A child Orchestrator is local to its child cell and cannot become global Root.

Non-atomic execution must return boundary artifacts such as a child PlanGraph,
boundary snapshot, ResultProposal-compatible artifact, trace pointer, or
quarantine record.

### 4.10. Non-Transitive Authority

Let Root call Architect `A_1`:

```text
Root -> A_1
```

If `A_1` creates child cluster `C_2`:

```text
A_1 -> C_2
```

Root does not manage `C_2` internals:

```text
Root -/-> internal(C_2)
Root -> boundary(C_2)
Root <- snapshot(C_2)
```

Root sets:

- goal;
- constraints;
- budget;
- forbidden regions;
- expected output schema.

Root does not control the internal trajectory of grandchildren.

### 4.11. Budget Propagation

Budget:

```text
B = (tokens, time, depth, parallelism, money, risk)
sum_{i=1}^{n} B_i <= B_parent
```

If a branch gets too little budget:

```text
B_i < B_min => prune(t_i)
```

### 4.12. Branch Expansion Condition

A branch expands if:

```text
ExpectedUtility(t_i) - ExpectedCost(t_i) > tau_expand
```

or:

```text
Uncertainty(t_i) > tau_uncertainty
and ValueOfInformation(t_i) > tau_voi
```

### 4.13. Branch Pruning Condition

A branch is pruned if:

```text
HardMask(t_i) = 0
or Viability(t_i) < tau_prune
or Budget(t_i) = 0
or DeadEndMatch(t_i) > tau_deadend
```

## 5. AVF - Attractor Viability Field

AVF is the pre-fractal layer. It does not solve the task. It decides which branches have the right to be born.

### 5.1. CandidateVector Generation

```text
V = CVG(W_t, G, N, DRS, Policy)
V = V_needles union V_localDRS union V_externalPointers union V_fallback
V -/-> freeLLMGeneration
```

Root/AVF does not invent CandidateVectors through free LLM generation.

### 5.2. CandidateVector

```text
v_i = (id, source, domain, features, branching_hint, capabilities, history)
x_i = [rel_i, p_i, utility_i, cost_i, risk_i, time_i, conflict_i, gt_i, novelty_i]
```

### 5.3. Feature Matrix

```text
X = [x_1; x_2; ...; x_n] in R^(n x d)
d = 9
```

### 5.4. Weight Vector

```text
w = [alpha, beta, chi, -delta, -epsilon, -zeta, -eta, lambda, rho]
```

Where:

- `alpha` = relevance weight.
- `beta` = success probability weight.
- `chi` = utility weight.
- `delta` = cost penalty.
- `epsilon` = risk penalty.
- `zeta` = time penalty.
- `eta` = conflict penalty.
- `lambda` = GT history weight.
- `rho` = novelty weight.

### 5.5. Base Viability Score

```text
VS(v_i) =
  alpha rel_i
  + beta p_i
  + chi utility_i
  - delta cost_i
  - epsilon risk_i
  - zeta time_i
  - eta conflict_i
  + lambda gt_i
  + rho novelty_i

S = Xw
```

### 5.6. HardMask

```text
HM(v_i) in {0,1}
v_i in ForbiddenRegions => HM(v_i)=0 and FV(v_i)=0
```

Examples: violence, fraud, identity substitution, privacy violation.

### 5.7. SoftMask

```text
SM(v_i) in [0,1]
SM(v_i) = 1 - penalty(v_i)
penalty(v_i) = a costPenalty + b riskPenalty + c stalenessPenalty + d uncertaintyPenalty
```

SoftMask lowers weight but does not kill the branch.

### 5.8. Final Viability

```text
FV(v_i) = HM(v_i) * SM(v_i) * VS(v_i)
```

### 5.9. Top-K Selection

```text
TopK = argtopk_{v_i in V}(FV(v_i), k)
Selected = TopK_exploit union TopK_explore
|TopK_explore| <= epsilon_explore * k
```

### 5.10. Exploration Budget

```text
epsilon_explore in [0,1]

strict:   0.00
default:  0.05
explore:  0.20
research: 0.30+
creative: 0.40+
```

Invariant:

```text
Exploration -/-> bypass(HardMask)
```

### 5.11. Cold Start

If:

```text
History(v_i) = empty
```

then:

```text
history_confidence = low
lambda H(v_i) ~= 0
rho' = rho + Delta_cold
```

Cold-start viability:

```text
VS_cold(v_i) =
  alpha rel_i
  + beta p_i^weak
  + chi utility_i^estimate
  - delta cost_i
  - epsilon risk_i
  + rho' novelty_i
```

AttractorPacket should include:

```json
{
  "history_confidence": "low",
  "fallback_to_architect_creativity": true,
  "requires_feedback_writeback": true
}
```

### 5.12. Branch Budget Allocation

```text
BB(v_i) = f(FV(v_i), Mode, TotalBudget, ExplorationPolicy)

max_fractals_i =
  floor(B_fractals * FV(v_i) / sum_j FV(v_j))

max_depth_i = BaseDepth(Mode) + DepthBoost(FV(v_i))
```

### 5.13. AttractorPacket

```text
A_p = (G, W_t, Forbidden, SelectedVectors, BranchBudgets, Time, Instructions)
ArchitectInput = AttractorPacket
```

Architect receives AttractorPacket, not raw user text.

Example:

```json
{
  "packet_id": "ap_001",
  "goal": {
    "goal_id": "goal_certificate",
    "desired_state": "certificate_obtained"
  },
  "hard_forbidden_regions": [
    "illegal_coercion",
    "fraud",
    "identity_abuse"
  ],
  "candidate_vectors": [
    {
      "vector_id": "official_online_request",
      "final_viability": 0.86,
      "branching_mode": "vertical",
      "branch_budget": {
        "max_fractals": 3,
        "max_depth": 4,
        "parallelism": 1
      }
    }
  ],
  "architect_instructions": {
    "do_not_expand_forbidden_regions": true,
    "must_return_time_assumptions": true,
    "must_return_plan_graph": true
  }
}
```

Architect returns PlanGraph only. Architect does not return ResultProposal. Executors return ResultProposal only.

## 6. Post V&V

Post V&V checks ResultProposal before GT.

### 6.1. ResultProposal

```text
r_i = (payload, evidence, cost, risks, time, trace)
```

### 6.2. VV Scores

```text
VV(r_i) = [schema_i, evidence_i, policy_i, time_i, safety_i, consistency_i]
score in [0,1]
```

### 6.3. Schema Score

```text
schema_i =
  1, if JSONSchemaValid(r_i)=true
  0, otherwise
```

### 6.4. Evidence Score

```text
evidence_i = claims_supported / claims_total
evidence_i = 0, if there are no claims
```

### 6.5. Time Score

```text
time_i = Freshness(r_i) * TimeEnvelopeValid(r_i)
time_i = 0, if there is no TimeEnvelope
```

### 6.6. Policy Score

```text
policy_i = 1 - violations_i
violations_i in [0,1]
hard violation => policy_i = 0
```

### 6.7. Safety Score

```text
safety_i = 1 - safety_risk_i
```

### 6.8. Overall VV Score

```text
VVScore(r_i) =
  a schema_i
  + b evidence_i
  + c policy_i
  + d time_i
  + e safety_i
  + f consistency_i

a + b + c + d + e + f = 1
```

If:

```text
schema_i = 0
```

then reject the proposal.

If:

```text
policy_i = 0
```

then reject the proposal.

## 7. GTValidator

GTValidator stands after Post V&V and before Root FinalOutput.

### 7.1. GT Is Not TruthProof

Invariant:

```text
GT != TruthProof
```

GT selects a stable strategy through a payoff function and updates ratings / TTL.

### 7.2. Candidates

```text
C = {c_1, c_2, ..., c_m}
```

where `c_i` is a ResultProposal, memory record, patch, or UP template.

### 7.3. Payoff Function

```text
Payoff(c_i) =
  w_1 U_i
  + w_2 R_i
  - w_3 C_i
  - w_4 V_i
  + w_5 Tr_i
  + w_6 N_i
```

Where:

- `U_i` = utility.
- `R_i` = robustness.
- `C_i` = compute/cost.
- `V_i` = violations.
- `Tr_i` = transfer score.
- `N_i` = novelty guard.

### 7.4. Utility

```text
U_i = GoalSatisfaction(c_i)
U_i = completed_requirements / total_requirements
```

### 7.5. Robustness

```text
R_i = a evidence_i + b consistency_i + c repeatability_i + d fallback_support_i
```

### 7.6. Cost

```text
C_i = a tokens_i + b walltime_i + c toolcalls_i + d money_i
```

Cost is normalized into `[0,1]`.

### 7.7. Violations

```text
V_i = HardViolation_i + SoftViolationPenalty_i
HardViolation => V_i = 1
```

A hard violation may reject the candidate independently of payoff.

### 7.8. Transfer Score

```text
Tr_i = PotentialCrossDomainUsefulness(c_i)
```

For ordinary result selection this may have low weight. For UP games it has high weight.

### 7.9. Novelty Guard

```text
N_i = Novelty_i * (1 - Risk_i)
```

Novelty is useful only when it does not violate safety.

### 7.10. Expected Outcome for Elo

For candidates `i` and `j`:

```text
E_i = 1 / (1 + 10^((R_j - R_i)/400))
E_j = 1 - E_i
```

### 7.11. Elo Update

```text
R'_i = R_i + K(S_i - E_i)
```

Where:

- `R_i` = rating.
- `K` = sensitivity coefficient.
- `S_i` = actual result.
- `E_i` = expected result.

```text
winner: S_i = 1
loser:  S_i = 0
draw:   S_i = 0.5
```

### 7.12. Regret

```text
Regret(c_i) = Payoff(c*) - Payoff(c_i)
c* = argmax_{c in C} Payoff(c)
Regret_norm = Regret / (|Payoff(c*)| + epsilon)
```

### 7.13. Dominance

Candidate `a` strictly dominates `b` if:

```text
forall k: metric_k(a) >= metric_k(b)
exists k: metric_k(a) > metric_k(b)
```

If strict dominance is found:

```text
b -> reject/archive
```

### 7.14. Mixed Strategy

If several candidates are close:

```text
mix_i = e^(tau Payoff_i) / sum_j e^(tau Payoff_j)
```

Large `tau` is nearly winner-take-all. Small `tau` is softer.

### 7.15. Early Stopping

If one candidate clearly dominates:

```text
Payoff(c_1) - Payoff(c_2) > Delta
Conf(c_1) > tau_conf
```

then the tournament may stop early.

## 8. GT-TTL and Memory Evolution

### 8.1. Half-Life Through Rating

```text
t_1/2(r) =
  base
  * sigma((Elo(r) - mu) / s)
  * (1 - Regret_norm(r))
  * FreshnessBoost(r)

sigma(x) = 1 / (1 + e^(-x))
```

### 8.2. Decay Rate

```text
decay_rate(r) = ln(2) / t_1/2(r)
```

### 8.3. Memory Survival Score

```text
Survival(r,t) =
  GTTrust(r)
  * Freshness(r,t)
  * ReuseFrequency(r)
  * UtilityHistory(r)
```

### 8.4. Garbage Collection

A record is archived if:

```text
Survival(r,t) < tau_archive
or Regret(r) > tau_regret
or ConflictWithWork(r)=true and new Work has higher temporal priority
```

### 8.5. Smart TTL

Useful knowledge lives longer:

```text
TTL'(r) = TTL(r) * (1 + alpha Utility(r) + beta Reuse(r) + gamma EloBoost(r))
```

Bad knowledge decays faster:

```text
TTL'(r) = TTL(r) * (1 - delta Regret(r) - epsilon FailureRate(r))
```

## 9. Marennya

Marennya is intra-domain reflection.

### 9.1. Trigger

```text
Trigger_M = Idle or AfterTask or Staleness or FailurePattern or GTRegretHigh
```

### 9.2. Input Bundle

```text
B_M = Work_recent union Thoughts_related union DeadEnds union GTFeedback union TraceRefs
```

### 9.3. Patch Candidate

```text
p = Marennya(B_M)
```

Types:

- reflection;
- protocol_patch;
- validator_patch;
- dead_end_candidate;
- heuristic_adjustment.

### 9.4. Patch Utility

```text
U(p) = ExpectedImprovement(p) - Risk(p) - Cost(p) + Robustness(p)
```

### 9.5. Patch Comparison

A patch passes if:

```text
U(p') > U(p_baseline) + Delta
or RegretReduction(p') > tau_regret_reduction
```

### 9.6. Marennya Quarantine

Invariant:

```text
MarennyaOutput -> Quarantine
MarennyaOutput -/-> Work
```

### 9.7. Validation Pipeline

```text
Validate_M(p) =
  Static
  and Dedup
  and RAG
  and SelfConsistency
  and Utility
  and Safety
```

Publication is allowed if:

```text
Validate_M(p) = true
p -> Thoughts
```

### 9.8. Marennya GT Game

Candidates:

```text
C_M = {baseline, patch_1, patch_2, ...}
```

Payoff:

```text
Payoff_M(p) =
  w_1 Utility(p)
  + w_2 Robustness(p)
  - w_3 Risk(p)
  - w_4 Cost(p)
  - w_5 HallucinationRisk(p)
```

The winner may be recommended for promotion.

## 10. UP

UP is the transfer and generalization layer.

### 10.1. Trigger

```text
Trigger_UP = AfterTask or PatternRepetition or HighUtilityThought or Idle
```

### 10.2. Input Bundle

```text
B_UP = Work union Thoughts union UP_related union GTFeedback
```

### 10.3. UP Candidate Types

```text
u in {opportunity, protocol_template, link}
```

### 10.4. UP Energy Function

```text
E(u) = (Novelty(u) * ExpectedUtility(u)) / (Risk(u) + CostTokens(u) + epsilon)
```

The `epsilon` term protects against division by zero.

### 10.5. Transfer Score

```text
Transfer(u) =
  DomainDistance^(-1)
  * StructuralSimilarity
  * UtilityEstimate

Transfer(u) =
  alpha Sim_structure
  + beta Sim_constraints
  + gamma Utility
  - delta Risk
```

### 10.6. UP Validation

```text
Validate_UP(u) =
  Static
  and Dedup
  and RAGSupport
  and SelfConsistency
  and Utility
  and Safety
```

If:

```text
Validate_UP(u) = true
```

then:

```text
u -> DRS_UP
```

Otherwise it remains in Quarantine or is rejected.

### 10.7. UP GT Game

Candidates:

```text
C_UP = {u_1, u_2, ..., u_n}
```

Payoff:

```text
Payoff_UP(u) =
  w_1 Transfer(u)
  + w_2 ExpectedUtility(u)
  + w_3 Novelty(u)
  - w_4 Risk(u)
  - w_5 Cost(u)
```

UP is non-actionable by default:

```text
UP(u) -/-> ExternalAction
```

## 11. AVF Feedback / ViabilityFeedback

After execution, a branch returns feedback:

```text
VF(v_i) = (predicted, actual, delta, failure_modes, gt_update)
```

### 11.1. Prediction Error

```text
Error(v_i) = |PredictedViability(v_i) - ActualUtility(v_i)|
```

### 11.2. Feature Correction

If a vector was overestimated:

```text
FV_future(v_i) = FV(v_i) - alpha Error(v_i)
```

If it was underestimated:

```text
FV_future(v_i) = FV(v_i) + beta PositiveSurprise(v_i)
```

### 11.3. DeadEnd Promotion

If a branch persistently fails:

```text
FailureRate(v_i) > tau_fail
ContextMatch(v_i) > tau_context
```

then:

```text
v_i -> DeadEnds
```

### 11.4. Successful Protocol Promotion

If:

```text
SuccessRate(v_i) > tau_success
Regret(v_i) < tau_regret
```

then:

```text
v_i -> Work/Thoughts
```

depending on record type.

## 12. Anti-Sycophancy Math

### 12.1. User-Origin Hypothesis

If a hypothesis came from the user:

```text
source(v_i) = user
TrustBoost(v_i | source=user) = 0
```

until external evidence exists.

### 12.2. Evidence Requirement

```text
Trust(v_i) =
  BaseTrust(v_i)
  + EvidenceSupport(v_i)
  + GTPrior(v_i)
  - ConflictPenalty(v_i)

BaseTrust(user_claim) <= BaseTrust(system_claim)
```

### 12.3. Counter-Branch Requirement

For risky hypotheses:

```text
If Risk(v_i) > tau => GenerateCounterVector(v_i)
```

The counter-vector must also come from an allowed source:

```text
system_template / red_team_needle / DRS conflict record
```

## 13. Continuous / Delta Runtime

This is a future layer, not MVP core.

### 13.1. World State as a Stream

```text
W(t)
```

### 13.2. Delta Update

```text
Delta W_t = W_t - W_{t-1}
Delta W_t = added union removed union changed union expired
```

The minus operator is structural, not numeric.

### 13.3. Selective Activation

```text
Relevance(module, Delta W_t) > tau_wake
```

### 13.4. ActiveNeedleSet

```text
ANS_t = { n in Needles | WakeScore(n, Delta W_t) > tau }
```

### 13.5. Delta Fractal

Do not recompute the whole fractal:

```text
F_t = Patch(F_{t-1}, Delta W_t)
```

### 13.6. Scope of Recomputation

```text
Scope(Delta W_t) = { nodes in F | depends_on(nodes, changed_state) }
```

### 13.7. Multi-Frequency Model

Different loops may run at different frequencies:

```text
L0 reflex:       100 Hz
L1 hot state:    10 Hz
L2 root update:   1 Hz
L3 deep checks:   async / idle
L4 Marennya/UP:   idle / scheduled
```

Main invariant:

```text
100Hz != full_recompute
```

`100 Hz` is the frequency of possible delta activation, not full-OS reasoning.

## 14. Audit and Hash-Chain

### 14.1. Content Hash

```text
H(r) = SHA256(canonical_json(r))
```

### 14.2. Hash-Chain

For an append-only log:

```text
H_i = SHA256(R_i || H_{i-1})
```

where `H_{i-1}` is the previous record hash.

### 14.3. Audit Event

```text
AuditEvent = (kind, payload, timestamp, hash)
```

Used for:

- DRS append;
- registry append;
- GT report;
- FinalOutput;
- Marennya/UP promotion.

## 15. Full Pipeline

The full pipeline describes one task from input/event to final output, DRS writeback, and optional Marennya / UP hooks.

Main invariant:

```text
FinalOutput is created only by RootOrchestrator.
```

### 15.1. General Pipeline Formula

```text
I -> normalize -> G
G -> WorldState -> W_t
(W_t, TQ) -> DRS -> M
(W_t, M, N) -> CVG -> V
V -> AVF -> A_p
A_p -> Architect -> P
P -> Executors -> R
R -> PostV&V -> Q
Q -> GTValidator -> GT
(R,Q,GT) -> Root -> F
(F,GT,Trace) -> Writeback -> DRS
DRS -> Hooks -> Marennya/UP
```

Where:

```text
I   = raw input / event
G   = canonical goal
W_t = WorldState at time t
TQ  = TemporalQuery
M   = memory bundle / DRS retrieval result
N   = installed needles
V   = CandidateVectors
A_p = AttractorPacket
P   = PlanGraph
R   = ResultProposals
Q   = Post V&V reports
GT  = GTValidator report
F   = FinalOutput
```

### 15.2. Step 1 - Input/Event

Input may be:

- user message;
- system event;
- needle event;
- timer event;
- external DRS signal;
- scheduled task.

Formula:

```text
I_0 = Input(raw)
```

Example:

```json
{
  "input_ref": "runtime_transient_input",
  "source": "user",
  "session_id": "sess_001"
}
```

Raw input may exist transiently at runtime, but Work DRS records should not store `raw_user_text` unless explicitly allowed by policy.

### 15.3. Step 2 - Intent Normalization

RootOrchestrator normalizes input into Intent:

```text
G = Normalize(I_0)
```

Intent contains:

- request_id;
- canonical_goal;
- domain;
- constraints;
- source_of_hypothesis;
- created_at.

Example:

```json
{
  "intent_id": "intent_001",
  "request_id": "req_001",
  "canonical_goal": "obtain_certificate_x",
  "domain": "government_certificate",
  "source_of_hypothesis": "user",
  "created_at": "2026-05-21T12:00:00Z"
}
```

Invariant: Root does not answer the user at this stage.

### 15.4. Step 3 - TemporalQuery Construction

Root builds a TemporalQuery for later retrieval:

```text
TQ = BuildTemporalQuery(G, now, mode)
```

Example:

```json
{
  "as_of": "2026-05-21T12:00:00Z",
  "time_range": {
    "from": null,
    "to": "2026-05-21T12:00:00Z"
  },
  "freshness_bias": "prefer_recent",
  "max_age_seconds": 2592000
}
```

Invariant: any DRS retrieval without TemporalQuery is forbidden.

### 15.5. Step 4 - WorldState Assembly

Root assembles world state:

```text
W_t = AssembleWorldState(G,TQ)
```

WorldState includes:

- time_context;
- user_context;
- session_context;
- local_drs_summary;
- active_policy;
- available_needles;
- recent_trace_refs.

Example:

```json
{
  "world_state_id": "ws_001",
  "request_id": "req_001",
  "intent_id": "intent_001",
  "time_context": {
    "now_utc": "2026-05-21T12:00:00Z",
    "timezone": "Europe/Tirane",
    "freshness_required": "high"
  },
  "temporal_query": {
    "as_of": "2026-05-21T12:00:00Z",
    "freshness_bias": "prefer_recent"
  },
  "active_policy": {
    "mode": "default",
    "allow_external_drs": false,
    "allow_exploration": true
  }
}
```

Invariant: WorldState must not automatically include irrelevant needles. Weather does not enter WorldState unless the task requires weather.

### 15.6. Step 5 - DRS Retrieval / Memory-First Reuse

Root queries Local DRS before plan generation:

```text
M = DRS.query(G,TQ,layers)
```

Reuse score:

```text
ReuseScore(r) =
  aQ(r)
  + bFreshness(r)
  + cGTTrust(r)
  + dSemanticSim(r,G)
  - eRisk(r)
  - fConflict(r)
```

Direct reuse may be applied only if:

```text
ReuseScore(r) >= tau_reuse
PolicyOK(r) = true
Root shortcut permission = true
```

Then:

```text
F = RootFinalFromReuse(r)
```

Even direct reuse must validate freshness:

```text
validate_freshness = true
```

If direct reuse is not permitted, memory is context-only / memory-informed and the pipeline continues.

Invariant: memory-first retrieval happens before Architect, but retrieval alone does not imply direct reuse.

### 15.7. Step 6 - CandidateVectorGenerator

If direct reuse is not applied, Root generates CandidateVectors:

```text
V = CVG(W_t, G, N, DRS, Policy)
```

Allowed sources:

- installed needles;
- local DRS;
- external DRS pointers;
- fallback exploration templates.

Forbidden source:

```text
free LLM hallucination of CandidateVectors
```

Example:

```json
[
  {
    "vector_id": "official_online_request",
    "source": "needle",
    "domain": "government_certificate"
  },
  {
    "vector_id": "personal_visit",
    "source": "needle",
    "domain": "government_certificate"
  },
  {
    "vector_id": "fallback_exploration",
    "source": "fallback",
    "requires_architect_creativity": true
  }
]
```

### 15.8. Step 7 - AVF Scoring

AVF scores CandidateVectors before Architect:

```text
X = FeatureMatrix(V)
S = Xw
FV(v_i) = HardMask(v_i) * SoftMask(v_i) * S(v_i)
```

HardMask kills forbidden branches:

```text
HM(v_i)=0 => v_i not in ArchitectInput
illegal_coercion -> HardMask=0 -> not passed to Architect
```

Selection:

```text
Selected = TopK(FV) union ExplorationBudget
```

Invariant: AVF does not build a plan. AVF builds the field of allowed directions.

### 15.9. Step 8 - AttractorPacket Creation

Root creates AttractorPacket:

```text
A_p = BuildAttractorPacket(G,W_t,SelectedVectors,Budgets,Forbidden,Time)
```

AttractorPacket contains:

- goal;
- world_state_ref;
- time_context;
- hard_forbidden_regions;
- candidate_vectors;
- branch_budget;
- exploration_budget;
- architect_instructions.

Example:

```json
{
  "packet_id": "ap_001",
  "goal": {
    "goal_id": "goal_certificate",
    "desired_state": "certificate_obtained"
  },
  "hard_forbidden_regions": [
    "illegal_coercion",
    "fraud",
    "identity_abuse"
  ],
  "candidate_vectors": [
    {
      "vector_id": "official_online_request",
      "final_viability": 0.86,
      "branching_mode": "vertical",
      "branch_budget": {
        "max_fractals": 3,
        "max_depth": 4,
        "parallelism": 1
      }
    }
  ],
  "architect_instructions": {
    "do_not_expand_forbidden_regions": true,
    "must_return_time_assumptions": true,
    "must_return_plan_graph": true
  }
}
```

Invariant: Architect receives AttractorPacket, not raw user text.

### 15.10. Step 9 - Architect Planning

Architect receives AttractorPacket and builds PlanGraph:

```text
P = Architect(A_p)
P = (Nodes, Edges)
```

Architect must return:

- plan_id;
- source_packet_id;
- time_assumptions;
- nodes;
- edges;
- executor_assignments.

Invariants:

- Architect creates PlanGraph only.
- Architect does not create FinalOutput.
- Architect does not answer the user.
- Architect does not return ResultProposal.
- Architect does not expand forbidden regions.
- Architect must return time_assumptions.

### 15.11. Step 10 - Fractal / DAG Execution

ExecutorRunner runs PlanGraph:

```text
Ready(P) = { n in Nodes | deps(n) subseteq Completed }
Parallelism <= branch_budget.parallelism
```

Each node is executed by an Executor:

```text
r_i = Executor(n_i)
```

Executor returns ResultProposal only.

Invariant: Executor must not create FinalOutput.

### 15.12. Step 11 - ResultProposals

```text
R = {r_1, r_2, ..., r_m}
```

Each ResultProposal contains:

- proposal_id;
- producer;
- vector_id;
- plan_id;
- result_payload;
- evidence;
- cost;
- risks;
- time_envelope;
- trace_refs.

Example:

```json
{
  "proposal_id": "rp_001",
  "producer": {
    "executor_id": "exec_001",
    "needle_id": "needle_government_services",
    "model_id": "stub_executor_v1"
  },
  "vector_id": "official_online_request",
  "plan_id": "plan_001",
  "result_payload": {
    "status": "success"
  },
  "evidence": [],
  "cost": {
    "tokens": 0,
    "wall_ms": 12,
    "tool_calls": 1
  },
  "risks": [],
  "time_envelope": {},
  "trace_refs": []
}
```

### 15.13. Step 12 - Post V&V

Post V&V checks every ResultProposal:

```text
Q = PostVV(R)
VV(r_i) = (schema_i, evidence_i, policy_i, time_i, safety_i, consistency_i)
VVScore(r_i) =
  a schema_i
  + b evidence_i
  + c policy_i
  + d time_i
  + e safety_i
  + f consistency_i
```

If:

```text
schema_i = 0
or policy_i = 0
```

then:

```text
r_i -> reject
```

Invariant: Post V&V happens before GTValidator.

### 15.14. Step 13 - GTValidator

GTValidator receives VVReports:

```text
GT = GTValidator(Q)
C = {q_i in Q | q_i.status = accept}
Payoff(c_i) =
  w_1 U_i
  + w_2 R_i
  - w_3 C_i
  - w_4 V_i
  + w_5 Tr_i
  + w_6 N_i
```

GT selects winner or mix:

```text
winner = argmax(Payoff(c_i))
mix_i = e^(tau Payoff_i) / sum_j e^(tau Payoff_j)
```

GT updates:

- Elo;
- regret;
- half_life;
- decay_rate;
- decision.

Elo:

```text
E_i = 1 / (1 + 10^((R_j - R_i)/400))
R'_i = R_i + K(S_i - E_i)
```

Half-life:

```text
t_1/2(r) =
  base
  * sigma((Elo(r)-mu)/s)
  * (1-Regret_norm(r))
  * FreshnessBoost(r)
```

Decay:

```text
decay_rate = ln(2) / t_1/2
```

Invariants:

- GT does not prove truth.
- GT selects stable results by payoff and updates memory.
- GT does not commit FinalOutput.

### 15.15. Step 14 - Root Final Synthesis

Root receives:

```text
(R,Q,GT)
```

and creates:

```text
F = RootFinal(R,Q,GT)
```

FinalOutput contains:

- final_output_id;
- request_id;
- `created_by = root_orchestrator`;
- status;
- answer;
- used_proposals;
- gt_report_ref;
- drs_writes;
- time_envelope.

Invariant:

```text
created_by == root_orchestrator
```

Executor, Architect, and GTValidator must not create FinalOutput.

### 15.16. Step 15 - DRS Writeback

Root writes results to DRS:

```text
DRS.write(F,GT,Trace)
```

Records may include:

- Work record;
- GT metadata;
- ViabilityFeedback;
- DeadEnd record if needed;
- Trace record if enabled.

Every record must have:

- TimeEnvelope;
- provenance;
- status;
- layer;
- type;
- domain.

If a branch failed:

```text
FailureRate(v_i) > tau => DeadEnd(v_i)
```

If a branch succeeded:

```text
Success(v_i) => Work/ProtocolCandidate
```

Invariant: DRSRecord without TimeEnvelope is forbidden.

### 15.17. Step 16 - Marennya Hook

After DRS writeback, Root may start Marennya:

```text
MarennaTrigger = AfterTask or Idle or FailurePattern or HighRegret
```

Marennya reads:

- recent Work;
- deadends;
- GT reports;
- trace refs;
- viability feedback.

It may create:

- marenna_reflection;
- marenna_patch;
- validator_patch;
- dead_end_candidate;
- heuristic_adjustment.

Primary write:

```text
MarennyaOutput -> Quarantine
```

After six-stage validation:

```text
Quarantine -> Thoughts
```

Invariant: Marennya cannot mutate Work directly.

### 15.18. Step 17 - UP Hook

UP runs after a task or while idle:

```text
UPTrigger = AfterTask or PatternRepetition or HighUtilityThought or Idle
```

UP reads:

- Work;
- Thoughts;
- related UP;
- GTFeedback.

It may create:

- up_opportunity;
- up_protocol_template;
- up_link.

Energy:

```text
E(u) = (Novelty(u) * ExpectedUtility(u)) / (Risk(u) + CostTokens(u) + epsilon)
```

Primary write:

```text
UPOutput -> Quarantine
```

After validation:

```text
Quarantine -> UP
```

Invariants:

- UP cannot mutate Work directly.
- UP is non-actionable by default.

### 15.19. Step 18 - Audit / Trace

Every significant transition may write an audit event:

```text
H(r) = SHA256(canonical_json(r))
H_i = SHA256(R_i || H_{i-1})
```

Audit is used for:

- DRS append;
- registry append;
- GT report;
- FinalOutput;
- Marennya/UP promotion;
- external DRS pointer publication.

### 15.20. Full Pipeline Pseudocode

```text
function process_request(raw_input):
    # 1. Root receives input
    intent = normalize_intent(raw_input)

    # 2. Time
    temporal_query = build_temporal_query(
        as_of = now(),
        intent = intent,
        freshness_bias = choose_freshness(intent)
    )

    # 3. WorldState
    world_state = assemble_world_state(
        intent = intent,
        temporal_query = temporal_query,
        active_policy = current_policy()
    )

    # 4. Memory-first retrieval and explicit direct-reuse gate
    memory_bundle = drs.query(
        intent = intent,
        temporal_query = temporal_query,
        layer_filter = ["work", "thoughts", "up", "deadends"]
    )

    reuse_candidate = select_reuse_candidate(memory_bundle)

    if root_allows_direct_reuse()
       and reuse_candidate.score >= TAU_REUSE
       and reuse_candidate.policy_ok
       and reuse_candidate.fresh:
        final_output = root_final_from_reuse(
            intent = intent,
            reuse_candidate = reuse_candidate,
            world_state = world_state
        )

        drs.write(
            layer = "work",
            type = "reuse_outcome",
            content = final_output,
            time_envelope = make_time_envelope()
        )

        return final_output

    # Otherwise memory is context_only / memory-informed.

    # 5. Candidate vectors
    candidate_vectors = candidate_vector_generator(
        intent = intent,
        world_state = world_state,
        installed_needles = load_needles(),
        drs_memory = memory_bundle
    )

    # 6. AVF
    attractor_packet = avf_score_and_build_packet(
        intent = intent,
        world_state = world_state,
        candidate_vectors = candidate_vectors,
        policy = world_state.active_policy
    )

    # 7. Architect
    plan_graph = architect_make_plan(
        attractor_packet = attractor_packet
    )

    assert plan_graph.time_assumptions is not None

    # 8. Executors / DAG Runner
    result_proposals = execute_plan_graph(
        plan_graph = plan_graph
    )

    assert all(is_result_proposal(r) for r in result_proposals)
    assert no_executor_final_output(result_proposals)

    # 9. Post V&V
    vv_reports = post_vv_validate(
        result_proposals = result_proposals,
        attractor_packet = attractor_packet
    )

    # 10. GT
    gt_report = gt_validate(
        vv_reports = vv_reports,
        mode = "result_selection"
    )

    # 11. Root final
    final_output = root_synthesize_final_output(
        intent = intent,
        world_state = world_state,
        result_proposals = result_proposals,
        vv_reports = vv_reports,
        gt_report = gt_report
    )

    assert final_output.created_by == "root_orchestrator"

    # 12. DRS writeback
    drs_records = drs_writeback(
        final_output = final_output,
        gt_report = gt_report,
        result_proposals = result_proposals,
        vv_reports = vv_reports,
        trace = collect_trace()
    )

    # 13. Marennya hook
    if policy_allows_marenna(world_state.active_policy):
        marenna_records = marenna_after_task(
            drs_records = drs_records,
            gt_report = gt_report
        )
        write_to_quarantine(marenna_records)

    # 14. UP hook
    if policy_allows_up(world_state.active_policy):
        up_records = up_after_task(
            drs_records = drs_records,
            gt_report = gt_report
        )
        write_to_quarantine(up_records)

    # 15. Return
    return final_output
```

### 15.21. Full Pipeline Compact String

```text
Input
-> Intent
-> TemporalQuery
-> WorldState
-> DRS memory-first retrieval
-> direct reuse? yes, only with Root permission and gates
-> RootFinalFromReuse
-> DRS writeback
-> direct reuse? no
-> CandidateVectorGenerator
-> AVF hard/soft scoring
-> AttractorPacket
-> Architect PlanGraph
-> Executor ResultProposals
-> Post V&V
-> GTValidator
-> Root FinalOutput
-> DRS writeback
-> Marennya quarantine hook
-> UP quarantine hook
-> Audit/Trace
```

## 16. Minimal Algorithms in Pseudocode

### 16.1. Root Pipeline

```text
function process_request(raw_input):
    intent = normalize_intent(raw_input)

    temporal_query = build_temporal_query(now, intent)
    world_state = assemble_world_state(intent, temporal_query)

    memory_bundle = drs_query(intent, temporal_query)
    memory_context = build_memory_context(memory_bundle)

    reuse = evaluate_reuse_gate(memory_bundle)
    if (
        root_allows_direct_reuse()
        and reuse.score >= tau_reuse
        and reuse.freshness_ok
        and reuse.gt_trust_ok
        and reuse.policy_ok
        and reuse.conflict_ok
        and reuse.time_envelope_valid
    ):
        return root_final_from_reuse(reuse)

    candidate_vectors = generate_candidate_vectors(
        intent,
        world_state,
        memory_context,
        installed_needles,
        drs
    )

    attractor_packet = avf_score(candidate_vectors, world_state.policy)

    plan_graph = architect.make_plan(attractor_packet)

    result_proposals = execute_plan(plan_graph)

    vv_reports = post_vv(result_proposals)

    gt_report = gt_validate(vv_reports)

    final_output = root_synthesize(result_proposals, vv_reports, gt_report)

    drs.write(final_output, gt_report, traces)

    marenna_hook_if_allowed()
    up_hook_if_allowed()

    return final_output
```

### 16.2. AVF Algorithm

```text
function avf_score(candidate_vectors, policy):
    X = feature_matrix(candidate_vectors)
    w = mode_weights(policy.mode)

    raw_scores = X @ w

    hard_mask = compute_hard_mask(candidate_vectors, policy)
    soft_mask = compute_soft_mask(candidate_vectors, policy)

    final_scores = raw_scores * hard_mask * soft_mask

    exploit = top_k(final_scores)
    explore = select_exploration(candidate_vectors, policy.epsilon)

    selected = exploit union explore

    return build_attractor_packet(selected)
```

### 16.3. DRS Retrieval

```text
function drs_query(intent, temporal_query, layer_filter):
    assert temporal_query is not None

    candidates = load_records(layer_filter)

    candidates = filter_by_time(candidates, temporal_query)
    candidates = filter_by_domain(candidates, intent.domain)
    candidates = score_semantic_similarity(candidates, intent)

    candidates = apply_gt_ttl_decay(candidates)
    candidates = sort_by_reuse_score(candidates)

    return top(candidates)
```

`drs_query` returns retrieved memory candidates. It does not itself authorize direct reuse; Root evaluates direct-reuse gates separately. Without those gates, retrieved records remain memory context only.

### 16.4. GT Validation

```text
function gt_validate(vv_reports):
    candidates = accepted(vv_reports)

    if candidates empty:
        return decision="rerun" or "needs_user"

    for c in candidates:
        payoff[c] = compute_payoff(c)

    winner = argmax(payoff)

    ratings = update_elo(candidates, winner)
    regrets = compute_regret(candidates, payoff)
    half_life = compute_half_life(ratings, regrets)

    return GTReport(winner, ratings, regrets, half_life)
```

### 16.5. Marennya

```text
function marenna_tick(trigger):
    bundle = collect_recent_work_thoughts_gt_deadends()

    drafts = generate_reflection_candidates(bundle)

    for draft in drafts:
        write_to_quarantine(draft)

    for draft in drafts:
        if validate_6_stage(draft):
            promote_to_thoughts(draft)
```

### 16.6. UP

```text
function up_tick(trigger):
    bundle = collect_work_thoughts_up()

    candidates = generate_transfer_candidates(bundle)

    for u in candidates:
        u.energy = novelty * expected_utility / (risk + cost + eps)
        write_to_quarantine(u)

    for u in candidates:
        if validate_6_stage(u):
            promote_to_up(u)
```

## 17. DRS Transport Boundary And Bounded LLM Node

APIs transport data. DRS represents time-scoped, contract-bound semantic
records around observations and results:

```text
DRSRecord = meaning + TimeEnvelope + contract_boundary + provenance
            + trust/audit_metadata + lifecycle_state
```

DRS does not replace APIs. An API may be a bounded source or connector, while
Root-controlled gates determine whether its observation may progress through
candidate, validation, acceptance, reuse, or rejection states.

### 17.1. Math / Invariants Sync v0.4 - Closed Enterprise Boundaries

The following formulas summarize only already closed local proof layers. They
do not add runtime enforcement, schemas, proof runners, tests, demos, real
connectors, real external DRS, production persistence, or production autonomy.

External DRS Pointer Protocol v0.1:

```text
ExternalDRSPointer = pointer/reference to external meaning trace
ExternalDRSPointer != external_drs_write
ExternalDRSPointer != global_drs_write
authority(ExternalDRSPointer) = 0
provenance_laundering(bridge_traversal) = blocked_or_quarantined
RootFinalAuthority = 1
```

External pointer candidate influence may contribute bounded reviewed context,
but it is not authority. Bridge traversal cannot launder provenance. Root
remains final authority.

Read-only Enterprise Connector Sandbox v0.1:

```text
ConnectorObservation = observation
ConnectorObservation != truth
ConnectorObservation != trusted_evidence
ConnectorObservation -> EvidenceCandidate only through bounded acceptance flow
read_only_connector_action = 0
read_only_connector_drs_write = 0
production_api_call = 0
```

ConnectorObservation is observation, not truth. ConnectorObservation is not
trusted evidence by itself. Read-only connector sandbox outputs do not execute
actions, write DRS, or call real production APIs.

External Evidence Acceptance Gate v0.1:

```text
ConnectorObservation
  -> EvidenceCandidate
  -> ValidationPacket
  -> RootDecision
  -> AcceptedEvidence | RejectedEvidence | QuarantinedEvidence

EvidenceCandidate.state = candidate_only until RootDecision
ValidationPacket != RootDecision
GT_acceptance_authority = 0
ConflictCheck_acceptance_authority = 0
AcceptedEvidence requires RootDecision
AcceptedEvidence != truth
AcceptedEvidence != ready_status
AcceptedEvidence != action
AcceptedEvidence != drs_write
AcceptedEvidence != installed_needle
```

EvidenceCandidate remains candidate_only until Root decision. ValidationPacket
is not Root acceptance. GT is not acceptance authority. ConflictCheck is not
acceptance authority. AcceptedEvidence requires Root decision. AcceptedEvidence
is not truth, ready status, action, DRS write, or installed Needle. Mock
signature, trust, and revocation checks are local proof fields, not real-world
cryptographic or registry validation.

Bounded LLM Semantic Executor Node v0.1:

```text
PlanGraph_preexists = true
Executor(llm_semantic_executor_node, bounded_mock_llm)
  -> SemanticDraft
  -> SemanticDraftResultProposal
  -> PostVV
  -> GT_advisory
  -> RootFinal

LLM is bounded Executor node capability
LLM_is_Root = 0
LLM_is_Orchestrator = 0
LLM_is_Architect_authority = 0
LLM_is_GT = 0
LLM_finalize = 0
LLM_external_action = 0
LLM_drs_write = 0
```

Bounded LLM Semantic Executor Node means the LLM is bounded Executor node
capability. It is not Root, Orchestrator, Architect authority, or GT. It does
not finalize, execute external actions, or write DRS by itself. It produces
bounded semantic draft / ResultProposal-shaped artifacts only under PlanGraph
execution. In Compute Collapse, `hedgehog_llm_calls=1` is a synthetic
routed-path estimate, not a real Gemini/API call by docs, walkthrough, or
audit.

Enterprise Chaos Pack v0.1:

```text
dirty_surfaces = {
  connector_observations,
  accepted_evidence,
  stale_legal_state,
  DRS_reuse,
  external_pointer_claim,
  LLM_semantic_draft,
  NeedleCandidate,
  child_cell_claim,
  GT_advisory,
  ResultProposal_bypass_attempt,
  conflicting_sources
}

escalation_attempts_blocked = 18 / 18
quarantined_and_blocked = 4
authority_transferred = 0
RootFinalAuthority = 1
```

Enterprise Chaos Pack composes dirty enterprise surfaces: connector
observations, accepted evidence, stale legal state, DRS reuse, external pointer
claim, LLM semantic draft, NeedleCandidate, child cell claim, GT advisory,
ResultProposal bypass attempt, and conflicting sources. 18/18 escalation
attempts were blocked. 4 attempts were quarantined and blocked. No authority
was transferred. Root remained final authority.

Compute Collapse Enterprise Bench v0.1:

```text
baseline_llm_calls = 29
hedgehog_llm_calls = 1
llm_call_reduction = 29 - 1 = 28
llm_call_reduction_ratio = 28 / 29 = 0.9655

baseline_context_units = 180
hedgehog_context_units = 32
context_unit_reduction = 180 - 32 = 148
context_unit_reduction_ratio = 148 / 180 = 0.8222
```

This is a deterministic local synthetic proof-level compute-collapse signal.
The long-chain baseline is estimated, not executed. The routed path uses closed
checkpoint metadata and Root-controlled semantic routing.
`source_collectors_replayed=false`. Closed checkpoint metadata reduces
recomputation but is not authority. DRS reuse reduces recomputation but is not
authority. Put plainly: closed checkpoint metadata is not authority. The
benchmark does not prove production economics, real billing, real latency, real
cloud cost, or real cost savings. It does not authorize Killer Demo or a
multi-LLM showcase. Killer Demo remains future assembly target after maturity
gates, not the next layer.

The bounded semantic LLM geometry is:

```text
PlanGraph_preexists
Executor(llm_semantic_executor_node)
  -> SemanticDraft
  -> SemanticDraftResultProposal
  -> PostVV
  -> GT_advisory
  -> RootFinal
```

The LLM is an `executor_node_capability`, not an authority term in the
equation. It does not modify `PlanGraph_preexists`; SemanticDraft is not truth
or final; and Post V&V, GT, and Root remain required.

Enterprise Chaos Pack v0.1 checks composition under dirty inputs:

```text
for attempt in enterprise_escalations:
    detected(attempt) = true
    blocked(attempt) = true
    authority_transfer(attempt) = 0
    action(attempt) = 0
    truth(attempt) = 0

RootFinal = blocked_all_escalations
```

Quarantine remains containment, not acceptance, truth, readiness, or action.
The deterministic local result does not establish production security or
real-world safety.

Compute Collapse Enterprise Bench v0.1 adds a small proof-level estimate over
the dirty enterprise stack:

```text
baseline = estimated_naive_long_chain
routed = root_controlled_semantic_routing(closed_checkpoint_metadata, DRS_reuse)

llm_call_signal = 29 -> 1
context_unit_signal = 180 -> 32
```

The long-chain baseline is estimated, not executed. The routed path uses closed
checkpoint metadata and Root-controlled semantic routing. These are local
benchmark signals only: not billing, not economics, and not latency. DRS reuse
reduces recomputation but is not authority. Audit hash records continuity, not
truth.

Kernel Enforcement / Transition Matrix Hardening v0.1 takes the v0.4 closed
boundary invariants and represents them as deterministic local transition
rows. It is proof-level and not production enforcement:

```text
allowed_transitions_count = 10
blocked_transitions_count = 35
transition_matrix_is_authority = false
transition_matrix_is_production_runtime_authority = false

RootFinalOutput -> DRSWriteback(local_after_root_final)
local_drs_writeback = true
global_drs_write = false
external_drs_write = false
```

The transition matrix models already proven boundary rules. It is not Root,
not authority, not production runtime authority, not a runtime rewrite, and not
schema modification. Root remains final authority.

Developer Facade / Capability Manifest UX v0.1 adds a small proof-level
admission formula for local developer manifests:

```text
CapabilityManifestDraft
  -> CapabilityManifestCandidate
  -> FacadeValidationReport
  -> RootReviewInput

validated_manifest_candidate != installed_capability
validated_manifest_candidate != installed_needle
validated_manifest_candidate != permission_to_execute
validated_manifest_candidate != accepted_evidence
validated_manifest_candidate != truth
validated_manifest_candidate != FinalOutput
permission_boundary != execution
risk_class != safety_proof
external_observation_schema != evidence_acceptance
```

The facade validates a manifest as a candidate for Root review only. It does
not install capability, authorize execution, create Needle, accept evidence,
prove truth, or replace Root.

Production Boundary Design Docs v0.1 adds a design-document boundary, not a
new runtime formula:

```text
production_boundary_design_v01 = design_doc_only
production_ready_claim = false
real_api_action_authorized = false
production_persistence_implemented = false
installed_capability_created = false
installed_needle_created = false
external_global_drs_implemented = false
```

The production boundary design defines future requirements before production
or real-world deployment claims. It does not change runtime behavior, authorize
real APIs/actions, implement persistence, install capabilities or Needles,
implement External/global DRS, or activate Marennya / UP.

Enterprise Killer Demo v0.1 / Demo A is an assembly proof, not new math:

```text
demo_a_mode = authority_safety_compute_collapse
act_count = 3
authority_attempts_blocked = 18
real_cost_savings_claimed = false
real_latency_measured = false
real_billing_measured = false
```

ACT 3 compute-collapse numbers are proof-level estimates only. Demo A does
not create production readiness, real API/action execution, installed
capability, installed Needle, External/global DRS, or Demo B document/evidence
workflow.

Enterprise Document Killer Demo B v0.1 is an applied proof, not new math:

```text
demo_b_mode = document_evidence_workflow_applied_proof
act_count = 4
baseline_document_review_units = 64
hedgehog_reuse_review_units = 18
estimated_document_review_units_saved = 46
production_economics_claimed = false
real_cost_savings_claimed = false
```

ACT 4 compute-collapse numbers are synthetic proof-level estimates only. Demo B
does not prove real OCR, PDF parsing, document extraction, connector trust,
production DRS, production runtime, production economics, or a general-purpose
document/workflow engine. Root-approved Local DRS Reuse remains advisory under
Root control; DRS reuse is not authority.

Schema Contract Alignment v0.1 Phase 1 is contract alignment, not new math:

```text
old_architect_instruction = must_return_result_proposals_only
new_architect_instruction = must_return_plan_graph_only
architect_returns_plan_graph_only = true
executor_dag_returns_resultproposal = true
runtime_jsonschema_hardening_implemented = false
```

The phase changes active Architect-facing invariant wording from old
ResultProposal-only wording to PlanGraph-only wording. It does not implement
runtime JSON Schema validation.

Schema Contract Alignment v0.1 Phase 2 is contract topology wording, not new
math:

```text
schema_contract_alignment_phase2_executor_dag_resultproposal_v01_status = complete_through_audit
patch_type = docs_spec_wording_contract_alignment
Architect -> PlanGraph
Executor -> ResultProposal
Fractal DAG -> ResultProposal-shaped boundary artifacts
Post V&V -> GT -> Root
runtime_jsonschema_hardening_implemented = false
evidence_kind_alignment_implemented = false
artifact_type_alignment_implemented = false
```

Phase 2 preserves role mapping and clarifies that ResultProposal-shaped
boundary artifacts are not FinalOutput, authority, action authorization, or DRS
writeback. It does not implement runtime JSON Schema hardening.

Runtime JSON Schema Validation Hardening v0.1 is contract/runtime boundary
hardening, not new math:

```text
runtime_jsonschema_hardening_post_vv_resultproposal_v01_status = complete_through_audit
patch_type = runtime_post_vv_incoming_resultproposal_schema_validation
result_proposal_runtime_schema_validation_present = true
post_vv_validates_incoming_resultproposal_schema = true
schema_validation_runs_before_manual_checks = true
schema_validation_is_additive = true
schema_validation_replaces_manual_checks = false
manual_policy_checks_preserved = true
manual_safety_checks_preserved = true
outgoing_vv_report_runtime_schema_validation_status = deferred
evidence_kind_alignment_implemented = false
artifact_type_alignment_implemented = false
```

This checkpoint turns the ResultProposal schema from test-only proof into
runtime boundary validation for incoming Post V&V proposals. Outgoing VVReport
validation remains future work.

Outgoing VVReport Runtime Schema Validation v0.1 is contract/runtime boundary
hardening, not new math:

```text
outgoing_vvreport_runtime_validation_v01_status = complete_through_audit
patch_type = runtime_post_vv_outgoing_vvreport_schema_validation
ResultProposal in -> Post V&V -> VVReport out
outgoing_vv_report_runtime_schema_validation_present = true
post_vv_validates_outgoing_vvreport_schema = true
outgoing_validation_runs_before_return = true
outgoing_validation_is_additive = true
outgoing_validation_replaces_manual_checks = false
fallback_vvreport_is_schema_conforming = true
root_remains_final_authority = true
evidence_kind_alignment_implemented = false
artifact_type_alignment_implemented = false
```

The Post V&V runtime schema boundary is now two-sided: ResultProposal in,
VVReport out. This does not validate every artifact in the system.

## 18. What Must Move Into a New Branch

For Codex / Antigravity, this file should exist as:

```text
specs/math_appendix_v0_3.md
```

Related files:

- `AGENTS.md`
- `specs/machine_manifest_v0_25.json`
- `schemas/*.schema.json`
- `specs/legacy_mapping.md`

Do not paste this entire appendix into `AGENTS.md`. A link is enough:

```text
For formulas and algorithms, read specs/math_appendix_v0_3.md.
```

## 19. Final Status

```text
v0.25
Engineering Passport for the MVP.

Machine Manifest v0.25
Machine map of the system.

JSON Schemas v0.25
Object contracts.

Math Appendix v0.3
Formulas and algorithms:
  - Time
  - DRS
  - Fractalization
  - AVF
  - Post V&V
  - GT
  - GT-TTL
  - Marennya
  - UP
  - AVF feedback
  - Anti-sycophancy
  - Continuous runtime
  - Audit/hash-chain
```

This is sufficient for a new branch to preserve the project mathematics.
