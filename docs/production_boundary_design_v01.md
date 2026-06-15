# Production Boundary Design Docs v0.1

Production Boundary Design Docs v0.1 is a boundary design document, not
production implementation.

It explains what would be required before Hedgehog OS could safely move from
local proof-of-architecture into any production or real-world deployment. It
does not claim production readiness, implement production infrastructure, or
authorize real APIs, real actions, installed Needles, External/global DRS,
production persistence, Marennya, UP, or Killer Demo.

Current closed proof stack referenced by this document:

- External DRS Pointer Protocol v0.1
- Read-only Enterprise Connector Sandbox v0.1
- External Evidence Acceptance Gate v0.1
- Bounded LLM Semantic Executor Node v0.1
- Enterprise Chaos Pack v0.1
- Compute Collapse Enterprise Bench v0.1
- Math / Invariants Sync v0.4
- Kernel Enforcement / Transition Matrix Hardening v0.1
- Developer Facade / Capability Manifest UX v0.1

## 1. STATUS AND SCOPE

This is design documentation only. It documents production boundary
requirements.

It does not implement production. It does not authorize Killer Demo. It does
not authorize real external actions.

It is not:

- production-ready claim
- production runtime implementation
- production kernel enforcement
- real connector/API integration
- real external action layer
- production capability registry
- installed Needle system
- global or External DRS implementation
- production persistence implementation
- secrets vault implementation
- live monitoring system
- Killer Demo implementation
- Marennya / UP activation

## 2. WHY THIS LAYER EXISTS

The proof stack now has enough local deterministic boundary layers to describe
what production would require.

The purpose is to prevent overclaim:

- proof-level safety is not production safety
- local deterministic tests are not deployment security
- audit logs are not legal proof
- mock signatures are not real cryptographic trust
- connector observations are not production evidence
- manifest validation is not installation
- transition matrix proof is not production enforcement

## 3. CURRENT PROOF-LEVEL GUARANTEES

The current deterministic proof stack does prove these local boundaries:

- Root-only final authority
- DRS reuse is not authority
- closed checkpoint metadata is not authority
- audit hash-chain records continuity, not truth
- ConnectorObservation is not truth
- EvidenceCandidate is not AcceptedEvidence
- AcceptedEvidence is not truth, ready status, action, DRS write, or Needle
- LLM is bounded Executor node capability, not actor, layer, or authority
- Transition Matrix is proof-only and not production runtime authority
- Developer Facade validates manifest candidates only
- validated manifest candidate is not installed capability, Needle, execution,
  evidence, truth, or FinalOutput
- no real external action
- no production persistence
- no External/global DRS write
- no installed real Needles
- Marennya and UP remain deferred

## 4. WHAT IS NOT PROVEN YET

The current stack does not prove:

- production process isolation
- sandbox escape resistance
- real cryptographic signatures
- real trust registry
- real revocation registry
- durable append-only audit storage
- production persistence semantics
- secrets vault / sealed slots
- credential lifecycle
- connector security boundary
- network egress control
- action execution boundary
- permission UX under real users
- operator review workflows
- monitoring / alerting
- rollback / incident response
- deployment threat model
- data retention / deletion policy
- legal/compliance guarantees
- multi-tenant isolation
- real billing / latency / cost measurement
- production-grade SLOs
- adversarial red-team coverage

## 5. PRODUCTION BOUNDARY REQUIREMENT MATRIX

| Boundary Area | Current Proof-Level State | Production Requirement | Required Future Artifact | Must Not Claim Yet |
| --- | --- | --- | --- | --- |
| Root authority | Root-only final authority is proven locally. | Production Root boundary with enforcement, audit, and operator recovery. | Root authority design and runtime enforcement spec. | Production autonomy or production safety. |
| Kernel enforcement / transition matrix | Transition Matrix is deterministic proof-only. | Runtime interception, policy versioning, denial reasons, and audit events. | Production kernel enforcement design. | `transition_matrix_is_production_runtime_authority=false` remains true today. |
| Capability manifest / Developer Facade | Facade validates candidate-only manifests. | Admission workflow connected to signing, review, sandboxing, and revocation. | Capability admission design. | Manifest validation as installation. |
| Capability installation | No InstalledCapability is created. | Signed package, sandbox policy, permission policy, risk class, revocation handle, audit policy. | Capability installation lifecycle. | Installed capability created. |
| Needle installation | No installed real Needles. | Root-approved install, sandbox, permission, revocation, health checks. | Needle installation design. | Installed Needle created. |
| Connector observation | Read-only proof observations only. | Connector sandbox, endpoint allowlist, provenance, egress control, and credentials. | Production connector sandbox design. | ConnectorObservation as truth or evidence. |
| Evidence acceptance | Mock validation only. | Real signatures, trust registry, revocation, freshness, conflict handling. | Production evidence trust design. | AcceptedEvidence as truth or action. |
| LLM executor nodes | Bounded Executor node capability only. | Prompt contract, schema enforcement, context minimization, tool isolation. | Production LLM node boundary design. | LLM as Root or authority. |
| DRS local records | Local proof semantic records. | Durable storage, access control, encryption, retention, migration, backup. | Production DRS persistence design. | DRS reuse as authority. |
| External/global DRS | Deferred. | External pointer verification, federation policy, no uncontrolled global write. | External/global DRS design. | External DRS implemented. |
| Audit/hash-chain | Continuity record only. | Durable append-only storage, monitoring, retention, export, review. | Production audit design. | Audit hash proves truth or legal proof. |
| Secrets / credentials | Not implemented. | Secrets vault, sealed slots, rotation, scoping, revocation, audit. | Secrets vault design. | Secrets vault implemented. |
| Permission / needs_user | Proof-level needs_user semantics. | Real user/operator prompts, consent receipts, delegation, revocation. | Permission UX design. | Permission is execution. |
| External action execution | No external actions. | Root approval, dry-run, action receipt, rollback/compensation, emergency stop. | External action boundary design. | External action authorized. |
| Production persistence | Not implemented. | Durable storage semantics, migrations, corruption handling, backup/restore. | Production persistence design. | Production persistence exists. |
| Monitoring / incident response | Not implemented. | Telemetry, alerts, quarantine dashboard, kill switch, incident review. | Monitoring and incident response design. | Live monitoring exists. |
| Marennya / UP | Deferred. | Advisory-only review, quarantine-first, Root-approved promotion. | Marennya / UP design after maturity gates. | Runtime activation. |
| Enterprise Killer Demo | Future assembly target. | Assembly of proven layers with explicit non-production language unless future production layers approve otherwise. | Killer Demo assembly plan. | Killer Demo authorized as production. |
| Public auditor packet / whitepaper | Later. | Reviewable packet summarizing proofs and limits. | Public auditor packet draft. | Legal/court proof. |

## 6. CAPABILITY INSTALLATION BOUNDARY

Developer Facade validates manifest candidates only. Production installation
would require a separate capability installation lifecycle:

```text
CapabilityManifestCandidate
-> RootReview
-> SignedCapabilityPackage
-> SandboxPolicy
-> PermissionPolicy
-> RiskClass
-> RevocationHandle
-> AuditPolicy
-> InstallationDecision
-> InstalledCapability
```

Current state:

- InstalledCapability is not created.
- InstalledNeedle is not created.
- validated manifest candidate is not installed capability.
- Root remains final authority.

## 7. CONNECTOR / API PRODUCTION BOUNDARY

Current connectors are local, read-only, mock, and proof-level.

Production connectors require:

- allowlisted endpoints
- network egress policy
- credential vault
- request signing
- response provenance
- replay protection
- rate limits
- timeout policy
- revocation
- audit trace
- failure quarantine
- human/operator permission gates for action-capable connectors

Current proof does not implement these.

## 8. EXTERNAL ACTION BOUNDARY

Current system executes no external action.

Future action execution would require:

- explicit Root approval
- user/operator permission
- action dry-run
- reversible/irreversible action classification
- risk class
- action receipt
- rollback/compensation plan where possible
- audit durability
- monitoring
- emergency stop

No current layer authorizes real external actions.

## 9. EVIDENCE / TRUST / SIGNATURE BOUNDARY

External Evidence Acceptance Gate used mock validation.

Production evidence requires:

- real cryptographic signature verification
- real trust registry
- real revocation checks
- source identity verification
- timestamp validation
- freshness/TTL enforcement
- conflict handling
- audit durability
- legal/compliance review where applicable

AcceptedEvidence is still not truth, not ready status, and not action.

## 10. DRS / PERSISTENCE BOUNDARY

Current DRS is a proof-level local semantic record model.

Production DRS requires:

- durable storage
- access control
- encryption
- data retention/deletion policy
- provenance integrity
- backup/restore
- corruption handling
- migration strategy
- privacy boundaries
- sealed secret slots / vault references
- external pointer verification
- no uncontrolled global DRS writes

DRS reuse is not authority. External/global DRS remains deferred.

## 11. LLM EXECUTOR NODE BOUNDARY

LLM remains bounded Executor node capability.

Production use would require:

- prompt contract
- output schema enforcement
- tool access isolation
- context minimization
- PII/secrets filtering
- no direct authority
- no direct DRS writes
- no direct external actions
- logging/audit of model use
- fallback / refusal / degradation behavior

LLM is not Root, not GT, and not authority.

## 12. TRANSITION MATRIX / KERNEL ENFORCEMENT BOUNDARY

Current Transition Matrix is deterministic proof-level model.

Production enforcement would require:

- central enforcement point
- generated transition table
- schema-bound artifact states
- runtime interception
- policy versioning
- denial reasons
- audit events
- compatibility migration
- test coverage
- formal review

`transition_matrix_is_authority=false`.
`transition_matrix_is_production_runtime_authority=false`.
Root remains final authority.

## 13. PERMISSION / NEEDS_USER / OPERATOR UX BOUNDARY

Current needs_user is proof-level.

Production requires:

- clear user/operator prompts
- explicit consent
- denied/timeout handling
- delegation rules
- confirmation receipts
- auditability
- revocation of permission
- child/organization policy boundaries

## 14. MONITORING / INCIDENT RESPONSE BOUNDARY

Production would require:

- event telemetry
- policy violation alerts
- anomaly detection
- audit chain monitoring
- quarantine dashboards
- kill switch / emergency stop
- incident review
- postmortem trace export

## 15. MARRENNYA / UP / AUTO-HARDENING BOUNDARY

Project docs use Marennya / Marennya spelling in nearby contexts; future docs
should keep naming consistent with the repository's current convention.

Marennya remains deferred. UP remains deferred. Manifest Auto-Hardening from
AVF/DRS Negative Traces v0.1 remains post-Killer-Demo future extension.

Negative traces may inform future advisory suggestions only. They must not
rewrite manifests automatically. They must not install capabilities. They must
not become authority. Root remains final authority.

## 16. ENTERPRISE KILLER DEMO BOUNDARY

Enterprise Killer Demo v0.1 is future assembly target after maturity gates. It
must not be implemented as a shortcut. It should assemble already proven
layers.

Before Killer Demo:

- Production Boundary Design Docs v0.1 must be closed.
- Any demo must avoid production-ready claims.
- Any demo must clearly say no real external action, no production persistence,
  and no real API unless separately authorized by future production layers.

## 17. PRODUCTION READINESS CHECKLIST

Required before any production claim:

- [ ] process isolation
- [ ] signed capabilities
- [ ] revocation
- [ ] durable audit
- [ ] secrets vault
- [ ] real connector sandbox
- [ ] permission UX
- [ ] action boundary
- [ ] monitoring
- [ ] incident response
- [ ] persistence design
- [ ] data retention policy
- [ ] security review
- [ ] red-team/adversarial testing
- [ ] legal/compliance review if applicable
- [ ] deployment threat model

## 18. PUBLIC LANGUAGE / CLAIMS POLICY

Allowed public wording:

- proof-of-architecture
- deterministic local proof
- Root-controlled runtime
- auditable boundary model
- candidate-only manifest validation
- production boundary design

Forbidden/avoid wording:

- production-ready
- autonomous enterprise agent
- real-world safety proven
- legal/court proof
- real billing proven
- real cost savings proven
- production kernel implemented
- self-healing runtime
- automatic capability installation
- automatic manifest hardening as authority
- Killer Demo authorized as production

## 19. FINAL SUMMARY

Production Boundary Design Docs v0.1 is design documentation only. It does not
implement production. It defines what must exist before production claims.

It preserves Root-only authority. It keeps Developer Facade candidate-only. It
keeps Transition Matrix proof-only. It keeps real APIs, actions, persistence,
Needles, External/global DRS, Marennya, and UP deferred.

Manifest Auto-Hardening remains post-Killer-Demo future extension. Next
lifecycle step after this design doc is audit/review or docs checkpoint, not
Killer Demo unless explicitly approved.
