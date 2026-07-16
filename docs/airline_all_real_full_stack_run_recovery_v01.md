# Airline All-Real Full-Stack Run v0.1 — Recovery Authorization 01

- document_status: RECOVERY_AUTHORIZATION
- authorization_status: AUTHORIZED
- original_preflight_commit: 6e007a4
- original_implementation_basis: a8d5036
- compatibility_repair_commit: 38ad0b0
- prior_official_invocation_count: 1
- prior_official_invocation_status: FAIL_CLOSED
- prior_real_provider_call_count: 12
- prior_network_call_count: 12
- prior_gemini_call_count: 12
- prior_real_world_effects_count: 0
- automatic_retry: false
- recovery_official_invocation_limit: 1
- root_attestation_activated: false

## Preserved Failure Evidence

The first official owner-terminal invocation is preserved unchanged at:

`.tmp/airline_all_real_full_stack_v01/airline_all_real_full_stack_v01_preference_a_a8d5036`

Its operator gate and terminal-safe log remain beside that package. The failed
package is historical evidence. It is not repaired, promoted, deleted, or
reused.

The primary failure was the Ledger false-positive
`raw_prompt_response_not_auxiliary_only` against accepted typed reviewer
response identifiers. The derivative failure was
`ledger_stored_validation_status_mismatch`.

## Accepted Repair

Commit `38ad0b0` replaces the broad lexical prompt/response check with an exact
raw-evidence classifier. Raw prompts, raw responses, opaque raw references,
and prompt/raw-response file references remain blocked.

Validation before this authorization:

- focused tests: 411 PASS;
- closed-chain compatibility tests: 1230 PASS;
- real-shaped offline Bridge: PASS;
- Corridor execution count: 1;
- Ledger: PASS with 19 entries, 29 dependencies, and 3 Root finals;
- Crypto: SELF_CONSISTENT_UNANCHORED with 9 source files and 11 critical files;
- provider, network, and Gemini calls during repair: 0;
- prior failure evidence: byte-for-byte unchanged.

## Authorized Recovery Identity

Recovery package root:

`.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0`

Recovery package ref:

`airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1`

Recovery package path:

`.tmp/airline_all_real_full_stack_v01_recovery_38ad0b0/airline_all_real_full_stack_v01_preference_a_a8d5036_recovery_38ad0b0_r1`

The `a8d5036` component preserves the original full-stack implementation
basis. The `38ad0b0` component identifies the accepted Ledger compatibility
repair. The actual synchronized execution HEAD is recorded independently by
the owner-terminal operator gate.

Exactly one recovery invocation is authorized. There is no automatic retry.

## Required Recovery Result

The recovery package may be promoted only if it records:

- provider mode: real_provider;
- model: gemini-2.5-flash;
- real provider / network / Gemini calls: 12 / 12 / 12;
- all twelve actor validations: PASS;
- Preference A selected;
- Bridge: PASS;
- Corridor execution count: 1;
- Ledger: PASS, 19 / 29 / 3;
- Crypto: SELF_CONSISTENT_UNANCHORED;
- package geometry: 9 source files / 11 critical files;
- signature mode: UNSIGNED_PLACEHOLDER;
- signature verified: false;
- secret scan: PASS;
- real-world effects: 0.

No anchor or Replay is authorized before owner-terminal validation passes.

## Failure Discipline

If the recovery invocation fails:

- stop;
- do not rerun;
- preserve the recovery package as failure evidence;
- do not publish an anchor;
- do not run Replay;
- require another explicit review.

## Next Gate

`airline_all_real_full_stack_run_v01_owner_terminal_recovery_execution`
