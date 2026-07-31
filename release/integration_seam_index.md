# Current Integration Seam Index

This human-readable overlay records the R-H1B implementation-basis maintenance
and discovery seams. Every row was `IMPLEMENTATION_IN_PROGRESS` at that
implementation basis. The row statuses are basis evidence and are not the
mutable current R-H1 lifecycle authority. These are not completed Gate-2
runtime seams and this is not a final Gate-2 seam inventory.

The immutable Gate-1 evidence remains
`release/integration_seam_index.json`, SHA-256
`c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231`.
This Markdown overlay does not replace, rename, reinterpret, regenerate, or
copy that frozen JSON inventory. G2-C remains `NEXT / NOT_STARTED`.

| Seam identifier | Source path | Target path | Current status | Limitation |
| --- | --- | --- | --- | --- |
| r_h1_dependency_direct_import_inventory | `pyproject.toml` | `tests/test_repository_maintenance_contract_v01.py` | IMPLEMENTATION_IN_PROGRESS | Static direct-import coverage supports an editable checkout; it is not a lockfile or standalone-wheel proof. |
| r_h1_pep639_canonical_license | `pyproject.toml` | `LICENSE` | IMPLEMENTATION_IN_PROGRESS | Metadata and canonical bytes do not establish title, relicensing authority, patent clearance, or legal review. |
| r_h1_agpl_commercial_notice | `LICENSE` | `COMMERCIAL-LICENSING.md` | IMPLEMENTATION_IN_PROGRESS | The commercial notice is informational and non-granting; no commercial agreement or contact channel is claimed. |
| r_h1_readme_manifest_current_boundary | `README.md` | `specs/machine_manifest_v0_25.json` | IMPLEMENTATION_IN_PROGRESS | Current metadata mirrors accepted status but creates no authority or closure. |
| r_h1_manifest_status_overlay | `specs/machine_manifest_v0_25.json` | `release/current_status_overlay_v01.json` | IMPLEMENTATION_IN_PROGRESS | The overlay is metadata-only and does not replace checkpoints, audits, or owner instruction. |
| r_h1_claim_evidence_links | `release/claim_to_evidence_index.md` | `tests/`, `demo/`, `docs/audit_reports/`, and `docs/` | IMPLEMENTATION_IN_PROGRESS | At the R-H1B implementation basis, four pre-R-H1 closure claims were indexed. Any later accepted R-H1 closure claim belongs to the mutable claim-to-evidence index after audit PASS. |
| r_h1_deterministic_operator_commands | `release/one_command_gauntlet.md` | `demo/run_kernel_conformance_v01.py` and `demo/run_living_gauntlet_v01.py` | IMPLEMENTATION_IN_PROGRESS | Deterministic local execution is not production, public-release, or external clean-clone proof. |
| r_h1_notes_limitations | `release/current_release_notes.md` | `release/current_limitations.md` | IMPLEMENTATION_IN_PROGRESS | Current engineering notes are not a public release announcement and all non-claims remain binding. |
