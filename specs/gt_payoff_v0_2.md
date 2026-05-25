# GT Payoff v0.2 Design

This document defines the planned GT v0.2 payoff design. It is a design
baseline, not a runtime implementation.

GT is not TruthProof. GT does not prove truth, perform actions, or certify that
an external state changed. GT selects the most viable candidate under explicit
payoff and policy constraints after Post V&V.

## Preserved v0.1 / v0.1.1 Surface

GT v0.2 must preserve the current observable GT report surface:

- `candidate_scores`;
- `winner_payoff`;
- `regret_summary`;
- `tie_detected`;
- `tie_break_rule`.

GT v0.1.1 tie-break policy remains visible:

```text
lower_risk
-> lower_cost
-> higher_robustness
-> higher_utility
-> deterministic proposal_id
```

## Additional v0.2 Signals

GT v0.2 should score architecture-aware information that is already present or
derivable from the local runtime:

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

## Conceptual Formula

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

The formula is intentionally explicit and local. It must not use LLM reasoning.

## Vector Role Policy

- `official_online_request`: primary path; positive bonus when safe.
- `personal_visit`: backup/physical path; moderate bonus when the official
  online path is incomplete.
- `legal_representative`: delegated path; useful but higher authorization
  burden.
- `fallback_exploration`: exploratory fallback; should not beat primary paths
  only by lexical id.
- `illegal_coercion`: forbidden; `HardMask=0`; never enters GT as an executable
  winner.

## Tie-Break v0.2

If payoff remains tied after v0.2 components:

1. lower risk;
2. lower human burden;
3. higher AVF `final_viability`;
4. higher evidence strength;
5. lower cost;
6. higher robustness;
7. deterministic `proposal_id`.

Tie visibility remains mandatory. If all v0.2 components are equal, GT should
still report `tie_detected`, `tie_candidate_ids`, and the applied tie-break
rule.

## Boundaries

- GT v0.2 must not call LLMs.
- GT v0.2 must not execute actions.
- GT v0.2 must not mutate DRS directly.
- GT v0.2 may output richer scoring metadata for Marennya and UP later.
- Marennya and UP should later consume GT v0.2 scores, regret, dominance, and
  dead-end signals.

## Future Runtime Tests

- `fallback_exploration` cannot win over `official_online_request` when base
  payoff is equal and the official path is safe.
- Higher AVF viability candidate wins when risk and cost are equal.
- A high-burden `needs_user` candidate loses to a completed lower-burden
  candidate when payoff is otherwise equal.
- `illegal_coercion` never appears as executable winner.
- Tie information remains visible if all v0.2 components are equal.
