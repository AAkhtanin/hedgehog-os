# Technical Reference

This is an explanatory index, subordinate to `specs/current_architecture_lock_v01.md`
and existing versioned contracts. `contract_index.json` records exact source
symbols/signatures, schema paths, consumers and evidence, including source hashes.
It is not a replacement Human Passport, SDK, authority registry or runtime law.

## Authority and Lifecycle

The current route is User/Event -> local Root intake -> Orchestrator proposal ->
WorldState/temporal/local DRS -> candidate vectors/AVF masks -> Root acceptance ->
BSEP -> semantic proposal -> runtime-owned topology -> bounded Work/children ->
ResultProposal -> Post V&V -> terminal GT advisory -> independent local Root.
Only a current scoped Root ActionCommitPacket can pass the exclusive Firewall.
Receipts, signatures, local history and replay carry evidence, not new permission.
Child budgets/scopes may descend, never expand by advice or by a cached result.

`root_decision_v01._decide_validated` evaluates hard failures before advisory
scores and applies the current policy thresholds. It derives ACCEPT/REVISE/
REJECT/DEFER/NO_UPDATE according to its exact input/policy, not a provider's label.
`validate_root_decision_result_v01` recomputes the result against the input.
The semantic work contract prevents actor output from becoming FinalOutput;
Living's `current_regression_claim_mapping` binds this to semantic_work_contract,
fractal_runtime and continuous_delta_runtime, and binds Post V&V before GT to D/E.

Currentness is a source-state relation, not expiry alone. Host checks actual and
saved capture provenance, ordinal and revisions. Historical verification remains
distinct from permission to start new work. D/E retain historical material while
new source changes invalidate current eligibility and produce new identities.
Affected sets are complete/minimal by the declared dependency graph. No hidden
global PASS cache or provider callback is introduced by this packaging change.

## Accepted Numerical Profiles

G3 uses signed bounded fixed-point values, exact integers, rational half-even
rounding, explicit event/evaluation times and bounded deduplicated folds.
`evaluate_gt_trust_update_v01`, `bounded_gt_event_fold_v01`,
`evaluate_gt_decay_value_v01` and `fold_avf_history_prior_v01` preserve distinct
rating, TTL, history-prior and advisory meanings. The formulas and integer bounds
are the existing Gate3 contract and source, not inferred from the new report.

G4's `gate4_reference_contracts_v01` and math fixture define the accepted finite
planning/scoring/budget profile. Runtime Work consumes its results and Root still
decides. The historical cold/warm G4 story used nine compute units and nine
dispatches in each case. Different allocation is not a compute-saving result.
G2B's SUMMARY_ONLY descent opens zero bytes and produces a Root shortcut plus a
non-authoritative reuse certificate. G2C's ten two-domain cases exercise mode
selection and bypass refusal; E's real affected/preserved checks demonstrate
selective recomputation. None is a universal wall-clock efficiency benchmark.

## Data and Error Models

The ABI `KernelArtifactV01` carries artifact type, lifecycle state, ownership,
payload, parent/trace references and a time envelope. The schema and typed
builders/validators retain their own closed field rules. Domain adapters do not
own effect handles. Standalone supplied validators validate their own input;
exact hashes prove bytes, not semantic truth, Root consent or signer identity.

Public validation reports/reason tuples and fail-closed exceptions remain those
of the linked consumers. This package reader raises `ValueError` for missing
inventory, unsafe path, incompatible basis or failed supplied relation; it never
substitutes collection to recover a missing field. G35's fixed public request
projection produces schema arrays before validation rather than relying on a
later JSON roundtrip. The rest of the adapter and its laws are unchanged.

## Authoring and Compatibility

The accepted `docs/gate5_authoring_kit_v01/EXECUTION_CONTRACT.md`, kit manifest,
Gate5 proof freeze and exact Football per-case oracle remain the compatibility
basis. G54D initial plus three corrections remains INCOMPLETE; accepted G54D1
correction four and Gate5 closure are preserved. The reader runs supplied proof,
not a new author or candidate. The original G5 proof runs on the old adapter
source view; the current successor is not falsely claimed to satisfy that old
freeze. No module version is mixed with its successor in one interpreter.

`geometry_index.json` describes directed data/authority/action relations for
later presentation. It neither materializes execution topology nor grants any
Root ownership. Technical source admission remains separate from runtime proof.
