# Provider Contract Modes v0.1

document_id: provider_contract_modes_v01
document_status: CURRENT_DOCS_ONLY

This document records future-compatible provider contract mode language from the
operator / Passport Keeper. It is documentation only. It does not implement
provider_schema_lite_mode, SDK schema mode, runtime behavior, prompts, schemas,
or provider selection.

Hedgehog OS separates provider formatting from authority.

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```

Provider-side schema is not authority. JSON MIME is not authority. SDK schema
is not authority. Local validators remain required. Runtime canonicalization
remains required. Root remains final authority.

## semantic_json_mode

Status: current default / preferred for rich reasoning.

Meaning:

- Provider returns simple semantic JSON.
- Runtime canonicalizes provider semantics into internal Hedgehog artifacts.
- Local validators enforce contracts.
- Root remains final authority.

Use for:

- rich semantic reasoning
- Orchestrator proposal role
- Architect proposal role
- BSEP / rich context transfer
- unknown request reasoning
- business process reasoning

Important:

- Provider does not create internal canonical passport objects.
- Provider does not create FinalOutput.
- Provider does not create ActionCommitPacket.
- Provider does not create permission.
- Provider output is advisory only.

## provider_schema_lite_mode

Status: future optional helper.

Meaning:

- Provider-side SDK schema may constrain small stable external fields.
- Runtime still canonicalizes.
- Local validators still decide acceptance.
- Root remains final authority.

Use for:

- route_id
- selected_vector_ids
- claim booleans
- required guards
- short uncertainty notes
- simple bounded proposal shells

Allowed purpose:

- reduce malformed JSON
- reduce wrong field types
- reduce accidental extra fields
- improve provider ergonomics

Forbidden purpose:

- provider-side schema must not become trust boundary
- provider-side schema must not replace local validators
- provider-side schema must not become authority

## provider_canonical_schema_mode

Status: not default / not current route / high-risk legacy option.

Meaning:

- Provider attempts to return full internal canonical Hedgehog objects.
- This is not the current preferred architecture for live rich reasoning.

Reason:

- brittle
- slow
- model-dependent
- can confuse provider output with internal passport artifacts

May only be revisited later as:

- narrow
- explicitly gated
- non-core authority experiment

Forbidden as core:

- Do not make provider responsible for full internal structured_rationale.
- Do not make provider responsible for full PlanGraph authority.
- Do not make provider responsible for BSEP authority.
- Do not make provider responsible for FinalOutput.
- Do not make provider responsible for ActionCommitPacket.

## Switching Model

Provider contract mode may later be selected by bounded configuration surfaces
such as:

- needle manifest
- provider profile
- route policy
- capability manifest
- manual operator flag
- test lane configuration

Mode selection invariants:

- Mode selection must not bypass Root.
- Mode selection must not weaken local validation.
- Mode selection must not create action permission.
- Mode selection must not create FinalOutput.
- Mode selection is provider-interface choice, not authority transfer.

## Anti-Overclaim Lines

- This does not mean SDK schema mode is implemented now.
- This does not mean Hedgehog OS returned to provider-owned canonical objects.
- This does not mean provider-side schema replaces local validation.
- This does not mean LangChain/provider framework controls Hedgehog authority.
- This does not change the current BSEP / WOW route.

## Current BSEP Route

The current BSEP real-live route remains `semantic_json_mode` plus
`json_mime_only`. BoundedSemanticEvidencePacket is a local bounded ContextPacket
contract in `hedgehog.context_packets`, not a provider-created authority object.
The provider returns semantic JSON. Runtime canonicalizes. Validators verify.
Root decides.
