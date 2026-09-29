# Experience, Choice and the Cost of Continuing Work

Radiolaria's useful memory is not merely a transcript. Within accepted finite profiles, an earlier result can change which review is proposed, where inspection work is spent, or whether an unchanged informational calculation needs repeating. The practical objective is to preserve useful work as activity continues without preserving yesterday's permission. Experience helps organise the next computation; the current owner still decides what may happen.

This chapter describes accepted source at `2e965ecb18e545e428380eb8e9aa5a7037a388be`, using separately identified recorded executions. It does not claim a new run. The G6A evidence index distinguishes original, reviewed historical, and current retained-obligation sources; they are not one composite execution. Source and check references below resolve through the companion [ledger](../references/experience/source_ledger.md). [E01](../PAPER_SOURCE_KEY.md#e01)

## What an Outcome Can Teach

An Outcome Feedback Envelope distinguishes the quality of advice, the task outcome and enforcement. A bad proposal blocked correctly is negative evidence about that advice and positive evidence about the boundary, not a successful business action. Missing prospective expectations are not retrospectively manufactured. In the retained G35 five-domain report, fourteen unique occurrences yield zero scorable observations; those sources do not justify numerical learning merely because they contain completed work or refusals. [E02](../PAPER_SOURCE_KEY.md#e02), [E04](../PAPER_SOURCE_KEY.md#e04)

The G36R Supplier episode provides the more specific learning mechanism. Its ADV-3 record has `UNSAFE` advice, `BLOCKED_AS_REQUIRED` enforcement and `SAFE_NO_DEAL`, at `CURRENTNESS`, without a Firewall decision or effect receipt. Two earlier prepared-but-undispatched cases are `NO_UPDATE`. One eligible negative occurrence produces a sparse history, subsequently consumed through current local DRS/Root review. The selected review changes from `standard` to `provenance`; actual `supplier.review_provenance.v01` Work consumes the full bound material. A separate lawful continuation completes with one mock effect. The refusal therefore informs later scrutiny without becoming a permanent ban or a transferable authorisation. [E03](../PAPER_SOURCE_KEY.md#e03)

That episode is historical captured reexecution of previously acquired provider-origin material. Its report's `LIVE_OBSERVATION` label must be read with the history lane `CAPTURED_REEXECUTION`; it is not a fresh provider call. Nor should it be joined to the separate controlled Airline experiment below as one task. [E03](../PAPER_SOURCE_KEY.md#e03)

The numerical representation uses exact integers with scale `Q = 1,000,000,000`. A normalised value is its stored integer divided by Q; these are dimensionless advisory quantities, not calibrated probabilities of safety. Signed rational rounding, `RHE`, means nearest integer with ties to even. For an eligible source-bound event, the implemented rating update is:

```text
R_next = clamp(R + RHE(125000000 * (O - E) / Q), 0, Q)
```

Here `R` and prospective expectation `E` are integers in `[0,Q]`; observed result `O` is either `0` or `Q`. The expectation is fixed before the outcome, not substituted with the preceding rating. Comparable subject/profile/lane, non-future event time and the 64-effective-event limit are premises. Redelivery does not create another independent occurrence. Ineligible or unscorable events preserve the rating. `_evaluate_from_plain` implements the rule; source-bound validation and named rounding/deduplication checks are in E02.

## Inset 1: Negative Experience Reallocates Inspection

In the recorded G4 Airline comparison, a controlled prediction is incorrect even though enforcement is `ALLOWED_AS_REQUIRED`. The update takes `R=500000000`, `E=Q`, `O=0` to `375000000`. The separately computed signed prior starts at zero and follows:

```text
signal = 2*O - Q
P_next = clamp(P + RHE(62500000 * (signal - P) / Q), -Q, Q)
```

Thus one admitted negative occurrence gives `P_next=-62500000`. This is `SPARSE`, not a mature reputation. `fold_avf_history_prior_v01` uses the GT fold's admitted occurrence set and comparable history keys. [E02](../PAPER_SOURCE_KEY.md#e02), [E05](../PAPER_SOURCE_KEY.md#e05)

G4 uses that raw prior once in its five-feature pressure rule:

```text
z_i = RHE((4*r_i + 2*l_i - 2*u_i - c_i + p_i) / 8)
w_i = RHE(10^12 * exp((z_i - max(z)) / 250000000))
```

The first four inputs are fixed-point integers in `[0,Q]`: configured relevance, lineage, uncertainty and estimated cost. The prior is in `[-Q,Q]`; weights are dimensionless integer apportionment weights. Hard-false branches are excluded first; unresolved required evidence prevents allocation, rather than being softened by the score. [E05](../PAPER_SOURCE_KEY.md#e05)

Both offers have `r=l=800000000`, `u=500000000`, and lower/upper quotas of 2/6 dispatch units. Costs are `400000000` and `430000000`. Cold pressures are `425000000` and `421250000`; applying the negative prior only to offer 0 lowers its pressure to `417187500`. The nine-unit original budget has already spent one unit on the initial constraint and reserves one final-consumer unit, leaving seven. Lower-first capped apportionment gives:

| Offer | Cold weight | Cold units | Warm weight | Warm units |
| --- | ---: | ---: | ---: | ---: |
| 0 | 1000000000000 | 4 | 983881318977 | 3 |
| 1 | 985111939603 | 3 | 1000000000000 | 4 |

After allocating both minima, three units remain. Exact rational shares, floors and the largest remainder assign the last unit; stable identifiers resolve ties. Recorded performed-work lists confirm the allocation was consumed, not merely printed. Both instances use nine dispatch units. This is changed expenditure, not fewer total calls or a speedup. Implementation: `evaluate_reference_pressure_v01` and `allocate_reference_work_budget_v01`; checks and exact fractions: E05.

The separate strategy contrast changes the configured utility profile from price-first to comfort-first and selects offer 0 versus offer 1. Its bounded feasible/individual-rationality/Pareto calculation is advisory. Client, airline and bank retain distinct decisions; the recorded hold is preparation, not an executed booking. [E07](../PAPER_SOURCE_KEY.md#e07)

## History Must Be Opened Again

Stored numerical history is not silently injected into the next task. The G4 retained evidence records descriptor discovery, Root approval, payload read, public-open validation and numerical source validation. The current bridge binds history to the receiving transaction. A later decision time requires requalification; expiry rejects current consumption while leaving the original evidence intact. [E06](../PAPER_SOURCE_KEY.md#e06)

Age also changes advice. After separate time admission, `evaluate_gt_decay_value_v01` computes `T=RHE(R*2^(-a/h))`, with integer age `a` and half-life `h` in seconds. Whole half-life multiples use exact rational division; the implementation returns zero at 64 half-lives. Only usable trust produces pressure `Q-T`; non-usable trust produces maximum pressure and recommends review. The implemented recommendation threshold is `T<600000000`. None of these calculations can suppress mandatory policy review or extend an expired advice window. E02 supplies the half-life premises, formula and checks.

## Inset 2: Reuse Avoids Domain Work, Not Current Review

G6A's retained N4-04 witness addresses a different question: can the same informational answer be returned without recalculating it? Its native calibration input is integer readings `[8,10,9]` and reference `10`. The source formula is:

```text
s = sum(readings) = 27; n = len(readings) = 3
correction = (n*reference - s)/n = (30-27)/3 = 1/1
```

The output fields are `total=27`, `n=3`, `correction_num=1`, `correction_den=1`. Readings/reference are bounded integer domain values with no declared physical unit; correction is an exact reduced rational in the same abstract unit, and `n` is a count. `gate5_contracts_v01.calibration`, the native executor and `check_reuse` provide the implementation/check chain. [E08](../PAPER_SOURCE_KEY.md#e08)

The cold observation counts one domain executor and one Host Work call. The warm observation counts zero of each, one stored read and two Root decision calls. Its answer must match the persisted summary, exact business inputs, owner, policy, schema and scope fingerprint. Changing a reading to `[8,10,8]` produces `warm_business_binding`; expiry and substituting the cold Root decision also fail. Those observed function counts cover the current process/thread only; child activity is explicitly `UNOBSERVED_NOT_ZERO`. Setup and cold writeback are not inside the same measured window. No wall-clock speedup follows. [E08](../PAPER_SOURCE_KEY.md#e08)

N4-05 makes the policy condition concrete. In a closed two-record store, validated replacement lineage and Root-reviewed writeback derive the current tip independently of list order. The predecessor remains historically valid, but a new current-policy Root review refuses its use. Summary-only descent opens zero payload bytes; restricted artifact descent returns `drs_pointer_access_policy_denied`. This is an explicit local policy composition, not a global supersession service. [E09](../PAPER_SOURCE_KEY.md#e09)

## Memory Inside Continuing Work

Memory need not occur only at outer intake. Implemented common-composition interfaces bind typed outputs to downstream inputs and retain exact historical fields across revisions. A missing pure capability is observed at a specific Work item, bound to its actual input, current task and revision. The bounded continuation path searches local DRS, evaluates current eligibility, obtains Root-reviewed artifact descent, retrieves source and independently readmits it before installation and use. Finding remembered code does not install it automatically. [E11](../PAPER_SOURCE_KEY.md#e11)

Nested execution has a separate concrete basis: recursive review accounts for child cells, and retained-work checks consume one preserved child result with a newly computed selected child result in canonical parent-slot order. These are not evidence that every child autonomously searches memory. The stronger general picture, recursively created child-local DRS activity under arbitrary nesting, remains an architectural generalisation not demonstrated by the targeted sources. E11 distinguishes implementation, test assertions and historical checkpoint evidence.

The common outcome is useful continuity with renewed grounds for use. Scores remain advice; an independent Root decision and the exclusive effect path remain necessary for consequential action. The four approved programme deferments are N1-18, N1-19, N4-12 and N4-13. Full StrongGT/FullAVF, strategic regret/stability, robust/minimax/CVaR/sensitivity and LGT are not supplied by these bounded numerical profiles. External authorship does not cancel those deferments. [E10](../PAPER_SOURCE_KEY.md#e10), [E12](../PAPER_SOURCE_KEY.md#e12)


## Inspect the Recorded Fields

[Source ledger](../references/experience/source_ledger.md).

Source routes: [E01](../PAPER_SOURCE_KEY.md#e01).
