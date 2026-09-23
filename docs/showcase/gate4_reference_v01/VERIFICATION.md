# Verification guide

## A. Data-only inspection — the quick start

Open `READ_ME_FIRST.md`, the PDF and technical appendix, then follow `presentation/claim_evidence_matrix_v01.json`. Run from the capsule directory:

```sh
python3 -I -B verify_data.py --capsule .
```

This standard-library program checks safe regular paths, the detached file inventory, byte counts, SHA256, exact proof/parent rows and pins, source bodies, evidence equality, XML body round trips and claim locators. It reads Python source as text/AST; it does not import the project, run tests, execute evidence, invoke models, create a Host or perform replay. It checks present files against declared identities, not the authenticity of an untrusted replacement inventory. Obtain the return digest or publication pin from the actual handoff.

`source_snapshot/` and the evidence source directories are **review-only snapshots**. Their presence is not an instruction to execute them. The 34 installed postimages, 123 current checker closure entries, 34 historical producer entries, 222 proof manifest rows and 75 retained-parent rows remain distinct. `READER_INDEX.json`, the detached Reader index, binds every included file, including companion binaries; binary bodies are not embedded in XML.

## B. Supplied semantic verification — matching trusted environment required

The saved G45 tested result is `evidence/g45/installed_supplied/combined.json`. Its exact command/cwd/environment receipt is `evidence/g45/commands/091_installed_supplied/receipt.json`. The recorded command was:

```text
/Users/admin/Projects/hedgehog-os/.venv/bin/python -B /Users/admin/Projects/hedgehog-os-gate4-g45-VbYwCeTe/supplied_installed.py
```

That historical instrumentation wrapper invoked the installed public `demo.run_living_gauntlet_v01.validate_living_g44_v01` with the exact parent directory/pin, proof package and unchanged TEST_SUPPLIED_PIN. Its body is included only to explain what was measured. These historical absolute paths document the original run; they are not dependencies that the reader must recreate. Do not execute the archived helper or archived checker code.

The recorded result completed in 19.859283 seconds. Its 1,151,634 bytes and SHA256 `136b2a76da196e42923886ffc5cf47d89e51d99ec8cc6c7ac549cfaea106b4b9` match the complete G44 Living and Conformance combined outputs. `installed_supplied/execution.json` contains named forbidden-call and network counters at zero and 430 pure saved Root-result validations; these are not 430 fresh decisions. The presentation build does not claim a fresh semantic replay or reproduce that timing.

The pinned public demo CLI accepts the following forms **from a separately trusted, admitted installation**. The examples below use the actual capsule-relative package/trust paths; set `CAPSULE` to the absolute path of this capsule and run in the trusted repository. `python` must name the matching trusted interpreter. The G45 saved command above tested the combined public validator; these CLI examples describe the installed argument interface and are not represented as new tested runs.

```sh
python -B -m demo.run_gate4_reference_v01 inspect
python -B -m demo.run_gate4_reference_v01 verify --package "$CAPSULE/evidence/g44/portable_publication_final" --trust "$CAPSULE/evidence/g44/TEST_SUPPLIED_PIN_FINAL.json"
python -B -m demo.run_gate4_reference_v01 replay --package "$CAPSULE/evidence/g44/portable_publication_final" --trust "$CAPSULE/evidence/g44/TEST_SUPPLIED_PIN_FINAL.json" --output "$NEW_RESULT"
```

The output path must be new. `inspect` is inert but retains its historical admission labels; it is not a current closure query. `collect` and `render` are NOT_IMPLEMENTED. `export` uses explicit saved inputs. `native` and `preflight` execute work and are unnecessary for this publication.

### Environment and source admission

The current verifier checks actual imported repository/transitive source origins and exact `checker_environment_v44` equality. Its full recorded environment is at `evidence/g44/portable_publication_final/MANIFEST.json#/checker_environment`:

| Component | Recorded value |
|---|---|
| Implementation | CPython |
| Python | `3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0 (clang-2100.0.123.102)]` |
| jsonschema | `4.26.0` |
| referencing | `0.37.0` |
| Python executable bytes | `52448` |
| Python executable SHA256 | `2477b47fa3ae65b9574eb18a15edb364e96948eaa1875ad3f1c80d780efc9c12` |

Actual G45 interpreter: `/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/bin/python3.14`. Imported origins are retained in `evidence/g45/installed_supplied/imported_origins.json`; the checker bytes are present for inspection in the exact proof package. Same version strings alone do not satisfy executable and source identity checks.

No universally runnable clean-clone environment bundle is provided. Broad replay on arbitrary computers is unsupported. Do not disable equality/source/origin guards, alter original TTLs, substitute archived modules into the import path or use a fake clock to obtain a PASS. Supported semantic use requires the matching trusted installed context and current admission. The G45 installed context/bridge is historical evidence; it does not authorize a new POLICY_INSTALLATION or let this documentation admit itself.

### Trust and semantic scope

The proof's `PUBLICATION.json` has SHA256 `8e7c4cb6412981436b704d2cc94736de91783d93a77849076007725029d9d08f`; its `MANIFEST.json` has SHA256 `16cee34833de46c4fd03dee9da3990d03815237567dfecc7cc9870f69d6d6f02`. The retained-parent manifest pin is `109c37f42ca220782971991c63f40037041d5c4548997fa1ab11262c578c81cd`. The original test trust record remains `TEST_SUPPLIED_PIN`. A separate independent review may bind these bytes without changing that origin.

Semantic scope is `SAFE_DERIVED_SAVED_RELATIONSHIPS_AT_RECORDED_EVENT_TIMES`; full native canonical replay remains `UNSUPPORTED_NATIVE_SCHEMA`. It validates supported saved relationships, not a full reconstruction of the native graph or current permission. Schema shape, arithmetic validity, contextual suitability and owner permission remain separate obligations.

## C. Fresh native collection

Fresh native collection is a separately authorized execution activity. It is unnecessary for data inspection or supplied validation and was not run to create this presentation. No all-suite, Living/Conformance native collection or new model/provider call is required by this capsule.

## Recorded tests and limits

Do not add epoch counts: G41 records 110 pure-math tests; G43 records 26 nodes/78 phases (including 17 native/history/preflight nodes); G44 final focused command 0017 records 33 PASS / 1 FAIL and 102 phases in 45.056284 seconds. The failed inherited test requested mode 04644 but the environment produced 0644. Actual 0644 validation and separate mode substitutions have their own records. The failed test remains a FAIL, with its accepted environment limitation, and G45 did not rerun or relabel it.

Times describe their recorded scopes, not an SLA. G43 native story, G44 supplied validation and the disposable publication rehearsal have different coverage. Inclusive nested durations cannot be summed as CPU time. Local in-process trust boundaries do not establish protection against arbitrary hostile same-UID Python or the whole OS.
