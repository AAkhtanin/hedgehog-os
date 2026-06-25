# Live Provider Adapter / Response Capture v0.1 PREFLIGHT

## Checkpoint

- preflight_id: live_provider_adapter_response_capture_preflight_v01
- preflight_status: COMPLETE
- base_head: 321e0b8
- previous_layer: Optional Live LLM Evidence Reader Smoke v0.1
- previous_layer_closed: true
- previous_layer_mode: response_file_validation_only
- planning_only: true
- patch_plan_created: false
- runtime_modified: false
- tests_created: false
- demos_created: false
- schemas_modified: false
- audit_log_created: false
- network_called: false
- provider_called: false
- gemini_called: false
- groq_called: false
- local_slm_called: false
- secrets_accessed: false
- connectors_called: false
- commit_created: false

## Purpose

Define the future layer that will perform one explicit controlled live
provider call and capture the raw provider response as an untrusted artifact.

This is not WOW v0.2. This is not the Supplier Payment live integration layer
yet. This is not Full Semantic E2E. This is not production. This is not
NeedleFactory, Marennya, or UP.

## Core Future Pipeline

explicit user/local config
-> one controlled provider call
-> raw provider response captured as artifact
-> artifact treated as untrusted response file
-> existing Optional Live LLM Evidence Reader Smoke validation path
-> exactly one SemanticEvidenceClaim-compatible candidate
-> candidate-only
-> Root review required
-> no action, no connector, no FinalOutput

## Critical Distinction

The previous Optional Live LLM Evidence Reader Smoke v0.1 layer validated
response files only. This future layer will add the provider-call boundary and
raw-response capture. It must still feed the captured artifact back through the
response-file validation lane.

## Required Future Safety Boundaries

- default mode offline/fail-closed
- provider call explicit-only
- no provider call in tests unless explicitly gated
- no silent fallback to deterministic PASS
- no secrets printed
- no raw API key/token in prompt, logs, reports, or audit
- no bank/supplier/warehouse connector
- no payment
- no shipment release
- no FinalOutput from provider output
- provider output is not truth
- provider output is not authority
- provider output is not action permission
- SemanticEvidenceClaim remains candidate evidence only
- Root remains final authority

## Future Allowed Providers

- Gemini
- Groq
- local SLM command or local endpoint only if separately approved later

Important: do not approve arbitrary command adapter in this preflight. For
v0.1, prefer one explicit provider adapter with strict env/config and timeout.
If provider config is absent, runtime must return SKIPPED_CLOSED or
FAIL_CLOSED, not fake PASS.

## Future Raw Artifact

The future runtime should save raw response to a local artifact path, for
example:

```text
_audit_exports/live_provider_response_capture/
```

Do not create this folder in preflight.

## Future Acceptance

- one explicit live provider call can be performed
- raw provider response is saved
- saved response can be validated by the already closed response-file lane
- invalid JSON fails closed
- authority/action/FinalOutput/connector claims fail closed
- unexpected fields fail closed
- secret-like keys/values fail closed
- prompt injection is preserved as evidence, not instruction
- Root review is required

## Forbidden

- do not start Supplier Payment Live Evidence Integration
- do not call supplier/payment/warehouse systems
- do not create ActionCommitPacket
- do not create Permission UX
- do not claim Full Semantic E2E
- do not claim Real Semantic Runtime MVP complete
- do not claim public WOW
- do not start Needle Authoring Passport
- do not start NeedleFactory
- do not start Marennya / UP
- do not add production connectors
- do not call network/Gemini/Groq/model APIs in this preflight
- do not access secrets
- do not create runtime code, tests, demos, schemas, or audit logs
- do not modify README, specs, audit indexes, or AGENTS.md

## Final Preflight Verdict

Next layer after this preflight, if approved and committed, is:
Live Provider Adapter / Response Capture v0.1 patch plan.
