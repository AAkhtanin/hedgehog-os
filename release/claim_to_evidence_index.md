# Claim-to-Evidence Index

This lightweight current index links accepted closure claims to committed
evidence. It does not create authority, replace an audit or checkpoint, close
Gate 2, or declare a public release.

## Accepted Claims

| Claim identifier | Exact claim wording | Current status | Focused tests | Runtime or demo | Independent audit | Checkpoint | Limitation or non-claim |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim_gate1_domain_neutral_reference_kernel_closed_pass | The Hedgehog OS Domain-Neutral Reference Kernel Gate 1 is CLOSED_PASS. | CLOSED_PASS | `tests/test_kernel_conformance_v01_runner.py` | `demo/run_kernel_conformance_v01.py` | `docs/audit_reports/auditor_domain_neutral_reference_kernel_gate1_v01.log` | `docs/domain_neutral_reference_kernel_gate1_checkpoint_v01.md` | Gate 1 closure is proof-of-architecture evidence, not Gate-2 closure, public release, RC2, or production readiness. |
| claim_two_domain_all_real_sealed_evidence_program_closed_pass | The Two-Domain All-Real Sealed Evidence Program is CLOSED_PASS. | CLOSED_PASS | `tests/test_two_domain_airline_all_real_program_v01_runner.py`; `tests/test_two_domain_supplier_water_filter_program_v01_runner.py` | Not applicable; the accepted programme evidence is sealed and is not rerun here. | `docs/audit_reports/auditor_two_domain_all_real_sealed_evidence_program_v01.log` | `docs/two_domain_all_real_sealed_evidence_program_v01_checkpoint.md` | Programme closure does not close Gate 2 or authorize a new real-provider, connector, or effect run. |
| claim_g2a_actionpacket_lifecycle_kill_switch_closed_pass | Gate 2 slice G2-A ActionPacket lifecycle and kill-switch is CLOSED_PASS. | CLOSED_PASS | `tests/test_action_commit_packet_lifecycle_g2_a_v01.py` | `demo/run_action_commit_packet_lifecycle_g2_a_v01.py` | `docs/audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log` | `docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md` | This is an internal Gate-2 slice closure; Gate 2 remains NOT_CLOSED and no public-release or production claim follows. |
| claim_g2b_drs_semantic_address_reuse_certificate_closed_pass | Gate 2 slice G2-B DRS semantic address space, controlled memory descent, and ReuseCertificate is CLOSED_PASS. | CLOSED_PASS | `tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py` | `demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py` | `docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log` | `docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md` | This is an internal Gate-2 slice closure; DRS is not truth, ReuseCertificate is not authority, and Gate 2 remains NOT_CLOSED. |

## R-H1A Maintenance Implementation Evidence - Not a Closure Claim

- At the R-H1A implementation boundary, R-H1 was
  `IMPLEMENTATION_IN_PROGRESS`.
- R-H1A implementation commit:
  `e3a80c2ab535b724254a007e0c6ffeef0cbbd04c`.
- Implementation paths: `pyproject.toml`, `LICENSE`,
  `COMMERCIAL-LICENSING.md`, and
  `tests/test_repository_maintenance_contract_v01.py`.
- Focused owner-terminal validation: `233 passed`.
- Limitation at that boundary: R-H1 as a whole remained
  `IMPLEMENTATION_IN_PROGRESS`; no accepted R-H1 audit and checkpoint had yet
  been synchronized into R-H1 closure status.

R-H1A is not an independent audit, R-H1 closure, public release, RC2,
Gate-2 closure, production-readiness claim, or security certification.
