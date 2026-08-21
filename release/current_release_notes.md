# Current Engineering Notes

These are current engineering notes, not a public release announcement.

## G2-D v0.3.10 contract-only correction hop

- Accepted guardian ruling: `APPROVE_PROFILE_D_CORRECTION_AND_E4_BACKPRESSURE_SCOPE_RECONCILIATION`.
- Active status: `CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING`.
- Active cumulative addendum: `docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`.
- Active cumulative v0.3.10 addendum SHA-256: `1655fbed584e24c980dda723d9e7521b4540ec528128f436ec4f458f7f40563d`.
- Embedded historical v0.3.9 suffix remains byte-exact: SHA-256 `1bbe028a4c757330b4ba94aec461e5bfbb1d1ef7496a68593dc20106c4867445`, 212148 bytes, 4185 LF.
- Repository basis: `36c43db9045d56666e961b54b4f9b272079f41a8`.
- `V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE=YES`.
- `V0310_G2D_RUNTIME_SEMANTICS_CHANGED=NO`.
- `V0310_G2E4_ACCEPTANCE_OVERLAY_SEMANTICS_CHANGED=YES`.
- `G2D_POSITIVE_BACKPRESSURE_LAW_CHANGED=NO`.

The hop records two bounded findings. First, the v0.3.9 Profile-D projection
reapplies the generic dependency-free child outcome after a public, settled
t12 revise decision and masks the accepted `DEADEND` target with `COMPLETED`.
Second, the standard strict-selective E4 contour lawfully has residual capacity
at both public backpressure calls, so requiring a fabricated nonempty carrier
is an invalid cross-slice acceptance overconstraint.

The corrected E4 acceptance geometry is exact and ordered:

1. baseline public call: `max_parallelism=3`, `current_parallelism=0`, latest `READY=0`, `occupied=0`, `residual=3`, 7 lawful latest queue entries;
2. conditional public call: `max_parallelism=3`, `current_parallelism=1`, latest `READY=1`, `occupied=2`, `residual=1`, 15 lawful latest queue entries.

Both queue tuples use exact append-log latest order and both public results are `None`.
Backpressure state/trace tuples, t03, and budget-exceeded reason remain
absent. The public call count remains exactly two. Nonempty revise observations,
partial failures, unresolved artifact IDs, unaffected sibling canonical bytes,
exact no-progress/blocked reasons, the non-ACCEPT Root decision, and final
fail-closed report remain mandatory. The independent G2-D 3/3 positive
backpressure witness is preserved without semantic change.

The failure contour stores exactly two revise observations in order: an
eligible positive observation followed by a noneligible `DEADEND` observation
on the same `VALIDATING` queue and revision binding. Profile-D must select
exactly one qualifying noneligible `DEADEND`; the lawful eligible observation
is not a duplicate or competing candidate. Missing proof or more than one
qualifying `DEADEND` fails closed.

Public revise semantics are likewise unchanged. E4 makes exactly four explicit public revise calls.
The future runtime repair must factor exact
deterministic reconstruction behind a private helper used directly by
transition and Profile-D projection; the public evaluator delegates to the
same helper. Internal reconstruction therefore contributes zero nested public calls
instead of the observed inflated count of 101.

## Scope and lifecycle

This contract-only hop changes exactly ten paths:

1. `docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`
2. `tests/test_fractal_runtime_g2_d_v02.py`
3. `AGENTS.md`
4. `README.md`
5. `specs/machine_manifest_v0_25.json`
6. `release/current_status_overlay_v01.json`
7. `release/claim_to_evidence_index.md`
8. `release/current_limitations.md`
9. `release/current_release_notes.md`
10. `tests/test_repository_release_spine_v01.py`

No runtime implementation is authorized or included. A later separate owner
authorization may change only `hedgehog/kernel/fractal_runtime_v02.py` and the
existing G2-D contract test item, without collected-item growth or public/schema
change.

The contract commit must first be followed by a mandatory nonsemantic
release-consumer maintenance commit changing exactly
`tests/test_repository_release_spine_v01.py`. Contract bytes retain
prospective identity placeholders; the maintenance version alone records the
contract commit and freezes the derived runtime/test/full-index-patch
SHA/byte/LF identities. It changes no runtime or G2-D test implementation,
semantic law, authority, acceptance, or closure claim.

B -> C -> M -> I, cumulative acceptance, re-audit, and reclosure occur only in
a clean isolated Git worktree. They must never be applied atop the dirty
owner-primary E4 patch. That parked input remains byte-exact: patch SHA-256
`fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0`,
117645 bytes, 2708 LF; runtime/test postimages
`825fb732504725d200761cb2dbfddbf0f6ca94b5b946f32b0bdc8b5876f1985f` and
`49982e9dbf1968550c46ddaf04770f1d5d81bfa3b6f32fc8612ee7ca631d456f`.

Reserved future audit:
`docs/audit_reports/auditor_fractal_runtime_g2_d_v0310_profile_d_t12_revise_projection_correction_v01.log`.

Reserved future checkpoint:
`docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_correction_checkpoint_v01.md`.

Required order is: contract commit; derive and commit the exact one-path
release-consumer maintenance; separate implementation authorization; G2-D
implementation and cumulative acceptance; implementation commit as
`REAUDIT_PENDING`; lifecycle sync; independent read-only re-audit; additive
v0.3.10 checkpoint/reclosure; fresh unchanged G2-E3 V06; then E4 pair 2/2,
complete E4 18/18, and complete E1-E4 68/68 before a transparent E4 corrective
commit.

## Current boundary

- R-H1, Gate 1, the Two-Domain programme, G2-A, G2-B, and G2-C are `CLOSED_PASS`.
- Historical G2-D v0.3.9 is `CLOSED_PASS_ON_V039_BYTES`.
- Active G2-D v0.3.10 implementation authorization, start, existence, commit, owner acceptance, independent re-audit, checkpoint, and reclosure are false or `NOT_CREATED`.
- G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`.
- G2-E4 strict subtree is `IMPLEMENTED_COMMITTED_PASS`; anti-gaming acceptance is `BLOCKED_PENDING_G2D_V0310_RECLOSURE`.
- G2-E5, G2-E6, and G2-F are `NOT_STARTED_NOT_AUTHORIZED`.
- Gate 2 is `NOT_CLOSED`.
- The two owner-supplied roadmaps remain unchanged.
- Public release, RC2, production readiness, production security certification, and successor baseline remain `NOT_CLAIMED`.
- No authority, permission, packet, receipt, FinalOutput, DRS write, provider/model/network/connector action, external-DRS action, or real-world effect is created.
- Real-world effects remain zero.

Current surfaces:

- [Status overlay](current_status_overlay_v01.json)
- [Claim-to-evidence index](claim_to_evidence_index.md)
- [Integration seam index](integration_seam_index.md)
- [Deterministic one-command gauntlet](one_command_gauntlet.md)
- [Current limitations](current_limitations.md)

- Added the non-implementing future Quantum-Inspired Mathematical Extension Roadmap v2.0. This private design record changes no current runtime, gate status, conformance result, release claim, or authority law and does not authorize implementation before the tagged Gate-6 baseline.
