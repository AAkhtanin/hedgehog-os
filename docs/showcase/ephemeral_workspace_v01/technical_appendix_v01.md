# Ephemeral Workspace v0.1

## Technical appendix

Radiolaria OS · 14 September 2026  
Committed implementation: `3f8720b75a1bda3a1df6b184e643c2de5327f838`

Ephemeral Workspace turns a bounded request into a temporary local environment for photo and media work. Its semantic roles propose needs, obligations and privacy restrictions. A deterministic compiler converts validated contributions into a finite contract. The common runtime materializes Work; local Root decisions and the persistent Host retain control over consequential operations. The environment responds to an actual resource loss, preserves unaffected work, saves one separately approved sidecar, and closes its owned resources.

This appendix describes the implemented contracts and recorded demonstrations. The principal browser run uses controlled semantic responses and real local fixture operations. Earlier Gemini and semantic-memory evidence has separate provenance. Public offline replay verifies safe derivative evidence; it does not recreate private originals or present action authority. Overall EWS acceptance is not self-awarded.

## 1. Source and evidence map

The committed [showcase](https://github.com/AAkhtanin/hedgehog-os/tree/3f8720b75a1bda3a1df6b184e643c2de5327f838/docs/showcase/ephemeral_workspace_v01) contains the current guide, source index, eighteen public evidence files, detached publication, independent pin and verification result. Its source index binds twenty-seven accepted implementation files. The historical cumulative design document is useful context, but its early timings, pending statuses and Mac-specific commands are not the current invocation guide.

The main evidence chain has four distinct stages:

| Stage | Recorded purpose |
| --- | --- |
| EWS3 | Live semantic production, strict captured continuation, mixed/photo-only contrast and LocalDRS |
| EWS3R2 | Current temporal repair and actual desktop/mobile browser story |
| EWS4R | Native BSEP safe projection, exact twelve-row proof map, safe export and offline validation |
| Main landing | Byte-preserving implementation admission, current anchor verification, commit and push |

The associated archive names, member hashes and exact selectors are recorded in `claim_evidence_matrix_v01.json` and the XML reader. Two companion records provide additional source-bound detail: [semantic inputs and outputs](presentation_evidence/semantic_boundary_io_projection_v01.json) and [historical semantic memory](presentation_evidence/historical_semantic_memory_summary_v01.json). They are explicit new derivatives with original archive/member hashes and selectors; the frozen EWS4R seal and independent anchor do not cover these newly created files. A file described as a safe historical projection is a newly written evidence-only derivative, not an exact copy of a private source or an addition to the old sealed package. Binary presentation assets have separate file identities.

## 2. The bounded task

The mixed request asks to browse, rate and select photographs, adjust exposure and crop, and review a short video with audio. Audio is optional: if it becomes unavailable, visual work should continue silently. Original sources must remain unchanged; publication is forbidden. Selected ratings and preview parameters may be saved only after a separate confirmation, followed by closure.

The declared material is finite. It comprises six synthetic photographs, an eight-second sequence of sixteen RGB PNG frames at 480 by 270 pixels and two frames per second, and mono 8 kHz, 16-bit PCM tones. The AudioSink consumes actual PCM chunks through loopback IPC. These are generated fixtures, not camera RAW development, compressed-video decoding, recorded speech or a physical speaker demonstration.

A photo-only neighboring request asks for browse, rate and select while excluding editing, video and sound. Historical EWS3 keeps the same capability availability and demonstrates different compiled operations. An audio-essential neighbor requires audio for speech review and must pause or refuse if audio is unavailable. Positive delivery of synthetic tones does not establish intelligibility or human assessment.

The request constants and typed values are defined in [contracts_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/hedgehog/domains/ephemeral_workspace/contracts_v01.py), particularly `REQUEST_MIXED`, `REQUEST_B`, `REQUEST_SPEECH` and `command`.

## 3. Three semantic roles

The semantic pipeline has three ordered duties. The orchestrator receives the request, capability class names, logical asset identifiers and source hashes, plus declared media inventory when present. It returns only requested `needs` and blocking `uncertainty`. Unsupported keys, duplicate needs, invalid dependencies and unresolved questions are refused before resource activation.

The semantic architect receives the bounded context plus the accepted needs/route projection. It proposes preview mode, cleanup behavior, selected-only save and four lifecycle phases: preview, interact, confirm_save and close. When video is selected, it also supplies an audio policy. `REQUIRE_AUDIO` is valid for the speech-review dependency; ordinary optional-audio work uses `SILENT_CONTINUE`.

The privacy reviewer sees the bounded context and architect obligations. It supplies an allow/block decision, a minimization policy and explicit conflicts. Successful assembly requires allow with no blocking conflicts. Its output affects real service transfers rather than being retained as an unused annotation.

| Principal role | Recorded output |
| --- | --- |
| Orchestrator | browse, rate, select, exposure, crop, video, audio; no uncertainty |
| Semantic architect | fit preview; on_end cleanup; selected_only save; SILENT_CONTINUE |
| Privacy reviewer | allow; preview_without_metadata; no conflicts |

The principal record labels these three responses `CONTROLLED_DETERMINISTIC`, with model identifier `local-semantic-rules-v01`. Earlier EWS3 used live Gemini responses. Role names ending in `_llm` do not turn controlled responses into live calls. All providers feed the same validators and normal Work consumers. The relevant code is [semantic_roles_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/hedgehog/domains/ephemeral_workspace/semantic_roles_v01.py) and [semantic_adapter_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/hedgehog/domains/ephemeral_workspace/semantic_adapter_v01.py), function `collect`.

## 4. BSEP and the semantic membrane

BSEP means **Bounded Semantic Evidence Packet**. The native DTO identifies orchestrator as source role, architect as target role, and `EPHEMERAL_WORKSPACE` as domain. Runtime builds it from the actual business request context, orchestrator proposal, route context and structured rationale. Its categories include observed facts, missing evidence, uncertainty, risk boundaries, rejected routes, required approvals or conditions, selected vectors and guards.

A small domain role projection is also named `bsep` in later-role context. It contains accepted needs together with `source_write=false`, `publication=false` and `separate_save=true`. The route projection carries the Root acceptance decision and its scope. This compact context is not the full native DTO. Preserving that distinction prevents a diagram from claiming that every native packet field was supplied directly to each model.

The native source is the accepted `browser_run_01/native_common_return/D_baseline.json`. The DTO selector is `/source_context/g2c_source_context/bsep_packet`; its router-binding selector is `/source_context/router_input/bsep_binding`. The public projection validates the actual DTO, surrounding source family and recorded typed binding. It exposes descriptive fields, authority-boundary flags and hashes, while raw role material and private references remain outside the public package.

BSEP explicitly disclaims truth, authority, FinalOutput and ActionCommitPacket status. It does not grant action permission, create connector commands, write DRS, bypass Root or authorize real-world effects. Its recorded rule is “Gemini proposes, Root disposes.” Those flags are a contract boundary. Their offline verification is not a reconstruction of live origin or a proof of all possible deployments.

The implementation is in [kernel_adapter_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/hedgehog/domains/ephemeral_workspace/kernel_adapter_v01.py), `semantic_source`. The public record is [bsep_safe_projection_v01.json](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/docs/showcase/ephemeral_workspace_v01/public_safe_package/bsep_safe_projection_v01.json).

## 5. Root review and current effects

The orchestrator result first returns to local Root route review. Runtime creates normalized claims, evidence bindings, explicit checks and a Root review packet. The decision input combines validation results, policy, temporal state, permission state, conflicts and advisory selection. The public Root decision kernel accepts or refuses the candidate. An architect contribution remains advisory and does not replace Root.

Route acceptance is distinct from permission for later commands. The session retains one PersonalRoot identity, one Host and cumulative command history. Each consequential command obtains its own finite native packet, actual Root-bound decision, public lifecycle installation and current Host dispatch. The Effect Firewall validates the admitted capability and actual execution result. The session then observes the receipt without treating it as permission for another action.

Currentness is checked at intake and before use. Command values bind the session, its version and exact operation. The executor checks the exact packet expiry immediately before its finite effect, independently of time spent validating it. OPEN does not authorize all later controls; history is not reset to obtain a fresh quota or improve performance numbers. UI `allowed` state is an advisory display of current eligibility, not a Root grant.

`root_review`, `prepare_command` and `dispatch` in the kernel adapter connect the domain to common Root/Host/Firewall builders. The domain does not implement an alternative authority kernel. Source hashes and effect receipts bind actual implementation and execution, but a hash alone does not establish semantic truth.

## 6. Actual Work and runtime topology

The semantic architect proposal contains the validated role responses under advisory authority. Runtime materialization creates two common Work items. `compile_contract` receives the three contributions and executes the deterministic compiler. `consume_contract` receives the first item's actual `material` output through an explicit output binding. The session reads this consumed contract to establish its operation gate.

Output validators check actual computed values. The pipeline therefore does more than store an intended plan: the next Work item consumes the preceding output. Mixed media later introduces its finite media-plan Work after genuine D materialization/review. It uses the same task and persistent Host. It is not a new U2 revision, an extra authority owner or a model-authored arbitrary execution graph.

| Capability class | Principal role |
| --- | --- |
| MediaSourceNeedle | Scoped access to original fixtures |
| RenderEngineNeedle | Derived preview rendering |
| DisplayGatewayNeedle | Derived frames only |
| ControlSurfaceNeedle | Finite typed commands |
| AudioSinkNeedle | Bounded PCM consumption |
| SidecarWriteNeedle | Dormant until independent approval |

These names describe the recorded contract classes, not general discovery of arbitrary external devices. The implementation has owned media, display and audio child processes, two viewer-server threads, and separate owner/control loopback origins. The public device-grant summary is historical evidence; it contains no material that recreates a current grant.

## 7. Typed commands and service privacy

The principal compiled contract admits ten operations: CROP, EXPOSURE, NEXT, PAUSE, PLAY, PREVIOUS, RATE, REVIEW_MEDIA, SEEK and SELECT. Lifecycle/save operations OPEN, REQUEST_SAVE, SAVE and END are handled separately. Values are closed and bounded: ratings range from zero to five; exposure uses integer tenths from negative twenty to twenty; crop is ORIGINAL, SQUARE or WIDE; seek positions range from zero to seven seconds.

There is no shell, exec, generic file-read or generic file-write command in this interface. A production-validator probe explicitly attempts those operations and observes `operation_not_allowed`. It uses a fixture continuation canary rather than constructing a complete hostile Host. Commands, polling and individual frames do not invoke a new LLM call, full D/E cycle or U2 revision.

The principal privacy policy is `preview_without_metadata`. Media renders a fresh RGB image and validates the PNG's allowed chunks and dimensions. Its transfer to session contains exactly `png`, `sha256`, `asset` and `session`. Session forwards only `png`, `sha256` and `frame_ref` to display. Producer, forwarding consumer and display consumer enforce their closed schemas. The alternative `preview_only` policy additionally permits checked derived-output dimensions and preview parameters.

The media process necessarily receives its scoped private source paths; these are not forwarded to display. Metadata stripping does not redact visible image content, isolate same-UID processes or erase pixels already viewed. Separate credentials, session identity, finite payloads and monotonic sequences constrain loopback RPC, but they are not a general OS sandbox.

## 8. Desktop and mobile evidence

The accepted browser story uses desktop dimensions 1440 by 1000 and mobile dimensions 390 by 844. Owner and bounded control pages operate the same session through separate tabs and origins. Actual controls select asset 1, set exposure to five tenths, apply SQUARE crop and produce a final rating of five. The accepted record includes a distinct save request, owner-origin approval and visible closed state.

All recorded actions are `SCRIPTED_BROWSER_TEST`. The owner's approval endpoint uses a manual-confirmation label, but that label does not prove that Andrey personally clicked. The initial control tab had a different viewport; its failed capture remains preserved before explicit correction. Accepted images were captured at their requested viewport dimensions and DPR1. Their original JPEG encoding and dimensions were independently inspected.

Presentation screenshots are illustrations of this recorded browser execution. Any public asset transformation must carry its own provenance and must not be described as an untouched original. The source browser evidence remains separate from the controlled semantic provider and from pure JavaScript tests that use a simulated DOM.

## 9. Deliberate AudioSink loss

The optional-audio scenario deliberately kills only its owned AudioSink after four actual video frames and 16,000 PCM samples. Runtime observes real process death and marks audio unavailable. Historical delivery receipts do not imply that the sink is currently alive. The media path pauses until the fresh-observation and selective-continuation route completes; unaffected photo work remains retained.

The deliberately killed child has return code negative nine. Cleanup reports it as already exited and reaped, with no fabricated graceful acknowledgement. Display and media children later acknowledge graceful close normally. Required-audio behavior is a distinct neighbor: without a current sink it must not claim successful speech review. Synthetic tones and delivery metadata never establish human intelligibility.

The original failed browser integration is part of the history. It reused an old observation interval after a real later loss and received `dependency_observation_time_invalid`; D had completed and E had not begun. The repair changes observation acquisition while retaining the old action authority. It is not a relaxation of the common validator or an extension of an expired permission.

## 10. Time, observation and immutable authority

| Event | Recorded UTC time |
| --- | --- |
| Original packet issued | 10:58:00 |
| Original packet expires | 11:00:00 |
| Owned AudioSink killed | 11:01:05 |
| New observation acquired | 11:01:26 |
| New observation interval ends | 11:03:26 |
| Original Workspace expiry | 11:16:07 |

The loss occurs sixty-five seconds after old packet expiry. Acquisition occurs eighty-six seconds after expiry and receives a new interval bounded by acquisition plus 120 seconds and the unchanged Workspace lifetime. The real source clock offset remains zero. Old packet bytes, Root-bound authority, prior dependency envelope, registry snapshot and D baseline remain unchanged; invalidation still identifies the original dependency envelope.

An independent attempt to use the old packet returns `host_current_action_not_executable`. New observation is therefore not synonymous with renewed permission. The accepted capture records ordinal one, source revision thirty and Host revision forty-one. The historical exported JSON is diagnostic evidence: it cannot recreate a live Host or its action authority. The temporal tests use explicit controlled clocks and are separately labelled from this real-clock integration.

## 11. D/E continuation and retained work

There is one top-level D setup, one public E invocation and one actual retained D recomputation within E. E follows the changed-source binding into returned D output. It checks preserved sibling evidence and the unaffected photo result before fresh informational local Root review. That review requests no effect and creates no permission. Subsequent PLAY and SAVE obtain fresh authority through their ordinary command path.

Photo Work, state and preview bytes are compared immediately before loss and automatically after E, before new commands. They match. The photo preview producer count remains three. Silent playback subsequently adds twelve frames, from four to sixteen, while PCM stays at 16,000 samples. Command/effect history stays at seven across E; later commands bring the final local synthetic command-effect count to ten.

The public [session event summary](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/docs/showcase/ephemeral_workspace_v01/public_safe_package/session_event_summary_v01.json) binds those metrics. `browser_run_01/native_common_return/media_consumption.json` in the retained EWS3R2 archive identifies changed source, recomputed result, preserved D sibling, retained consumption and final Root review. This is selective recomputation with actual work, not zero recomputation or a UI-only state change.

## 12. Exact save and owned cleanup

REQUEST_SAVE forms a candidate without writing. Separate owner-origin approval binds the session/version, output slot, selected assets, ratings, exposure, crop and intended bytes. SAVE requires a current packet and an unused matching approval. If selection or parameters change, the prior candidate is no longer exact and a new approval is required.

The principal run writes one 250-byte `selection.json`. Its SHA256 is `20e01b3ebd6f813bccf2ce51d23c71406a0f2b2cd706ab8bda92e71bed28a915`. It records selected asset 1, rating five, SQUARE crop, exposure five tenths and the original source hash. The file is a sidecar of parameters, not a transformed replacement for the original photo. Publication is not an admitted operation.

The final lifecycle is CLOSED_SUCCESS. Three owned service processes are reaped, two viewer threads close and the finite media thread stops. Original sources and the approved sidecar remain. Preview cleanup compares owned device/inode/hash identity and preserves replacements. A conflict would report CLEANUP_INCOMPLETE instead of success. Cleanup is an initial resource-owner obligation at a finite image/IPC boundary; it does not claim asynchronous preemption of arbitrary code or deletion of downloaded pixels.

## 13. Historical LocalDRS: cold, warm and changed source

The EWS3 history exercises actual LocalDRS public write, search, current eligibility and descent interfaces. A cold query finds no candidate. Validated semantic content is reviewed by Root and recorded as a finite recipe. Warm search evaluates the present query, requires fresh Root-approved SUMMARY_ONLY descent and supplies the recovered values to the existing semantic-role validators.

Warm execution skips semantic production only. It does not deserialize a Host, retain a grant, resurrect a URL token or skip a new route/resource/save decision. Recipes bind source, policy, Root and validity. Durable DRS storage is explicitly retained outside disposable workspace previews. The recorded warm semantics-plus-Work stage takes 0.161 seconds; that is not total workspace startup or a directly comparable speedup over a complete live run.

The actual `contrast_memory_04/DRS_events.json` has nine events. Rows zero and one record cold search and recipe write. Row two records a saved-work summary. Row three records a FRESH_CANDIDATE with fresh Root acceptance and summary-only descent. Rows four and five reject the old recipe as BLOCKED_BY_SCOPE with `drs_address_scope_mismatch`. Row six writes a new recipe for changed dependencies. Row seven selects the new candidate while the old remains blocked. Row eight retrieves saved-work information.

The informational request records zero model calls, effects, new service activations, new Workspace instances and sidecar writes. Its historical V1 selection has rating four, original crop and zero exposure; it is not the principal browser sidecar. Additional foreign-root, policy and expiry neighbors are focused tests with their own sources and clocks. They are not all relabelled as events in this one history.

## 14. Execution modes and failure accounting

Historical EWS3 records nine provider attempts, six accepted responses and three failures. Two early main responses request clarification and one V1 response is malformed. Accepted main and photo-only role outputs reach actual Work and Root review. Later live handlers fail on external harness approval-actor and exposure-unit mistakes. Those failures remain recorded.

The accepted responses are then consumed through strict CAPTURED_REEXECUTION. Context, role order, response identity, transport history and original capture bindings are checked. New Host and resources provide fresh execution authority. The result is not presented as an uninterrupted live end-to-end run, and the same accepted responses are not purchased again solely to disguise a harness failure.

The principal EWS3R2 browser record instead uses three CONTROLLED_DETERMINISTIC responses and zero provider calls. Its local photo/media operations are real. Their `MOCK_CONSEQUENTIAL` classification distinguishes local synthetic effects from external business effects; it does not mean no files, threads or processes existed. Loopback IPC is not erased by a declared zero external-network count.

Current security probes and later offline export/replay form additional lanes. Their counters describe their own instrumented scopes. No single aggregated number should imply that all scenarios were live, current, reexecuted on final bytes or monitored at OS level.

## 15. Twelve named proof requirements

The final map contains five current local boundary probes and seven carried historical positions. Current service probes use production handlers in owned in-process threads with generated eight-by-eight PNG fixtures. They do not construct a Workspace, Root or Host and do not execute D/E. Pure-validator probes explicitly identify their narrower boundary.

| Requirement | Evidence lane | Actual attempted boundary |
| --- | --- | --- |
| A01 | Current probe | RAW/source-byte GET after valid derived frame; 403 derived_frame_only |
| A02 | Carried EWS1R | Display credential storage listing; asserted HTTPError |
| A03 | Current probe | Valid renderer RPC source overwrite; 403 service_operation_not_allowed |
| A04 | Current probe | SHELL, EXEC, READ_FILE, WRITE_FILE; operation_not_allowed |
| A05 | Carried EWS1R | Forged save approval/control credential at owner endpoint; asserted HTTPError |
| A06 | Carried EWS1R | Existing-frame request after controlled expiry; asserted HTTPError |
| A07 | Carried EWS1R | Receipt-derived identity used as save permission; asserted ValueError |
| A08 | Carried EWS1R | foreign.json substituted into pending target; approval_candidate_changed |
| A09 | Current probe | Audio-role render request; 403 service_operation_not_allowed |
| A10 | Carried EWS1R | NEXT on a closed session; workspace_not_current |
| A11 | Current probe | Model DTO device_ids/topology_edges injection; semantic_closed_shape |
| A12 | Carried EWS3R2 | Actual optional AudioSink disappearance and selective continuation |

A07 and A08 share one historical test; the seven carried positions are not seven newly executed independent tests. A08 covers approval target substitution, not direct invocation of a file writer. A10 covers NEXT after closure, not serialized-lease replay. A09 uses an inert PNG canary named as a video source because role refusal occurs before decoding. Historical exception-only assertions do not supply an invented exact HTTP status or error string. Source-method bridges establish narrow unchanged bodies, not a new execution of historical tests.

The public [adversarial matrix](https://github.com/AAkhtanin/hedgehog-os/blob/3f8720b75a1bda3a1df6b184e643c2de5327f838/docs/showcase/ephemeral_workspace_v01/public_safe_package/adversarial_matrix_v01.json) records attempted operation, observed proof, source pins, classification and limits for every row.

## 16. Safe export, pinning and offline replay

EWS4R exports eighteen public files totaling 295,981 bytes. Sixteen are evidence-only semantic derivatives; the other two are kernel-integrity support and the sealed manifest. The common covered inventory contains seventeen file IDs because the manifest does not cover itself. The derivative graph has fifteen parent edges. A separate 1,339-byte publication binds the package identity.

The expected independent publication pin is:

```text
693fc6b5c2e8499161b40dc7bb6c22a21ca040c38325f1e657f176e9ff7bf525
```

The caller supplies this value to the verifier. The checked package must not choose its own trust anchor. The unchanged publication remains EVIDENCE_ONLY; a later detached record reports ANCHORED_PASS. Historical candidate-status and pending-pin fields inside the frozen package are deliberately retained. Main landing and independent verification are later records, not edits to old evidence.

The native BSEP derivative is validated against the actual DTO and router binding. Original native graphs contain 83 baseline artifacts and 156 retained artifacts, preserving all 83 baseline members. Their native ABI bundle checks pass. Older canonical-reference schemas remain UNSUPPORTED_NATIVE_SCHEMA. A separate private aggregate wrapper can preserve those exact native bytes, but its integrity PASS is not a native-original-manifest PASS.

Offline replay verifies the exact safe derivative graph, content, bindings and continuity. It does not inspect hidden originals, reexecute private probes, reconstruct live Host origin, grant new permission or establish semantic truth. It provides no signature, authenticated signer, trusted timestamp or Root attestation. New presentation and reader derivatives have separate identities and do not extend this frozen seal.

## 17. Measured scopes and repository admission

| Measured operation | Recorded time |
| --- | --- |
| Principal native D | 104.050 s |
| Principal complete D preparation | 113.107 s |
| Principal native E | 300.125 s |
| Principal browser launcher | 866.681 s |
| EWS4R five local probes | 1.702 s |
| EWS4R 59 evidence cases | 23.307 s |
| EWS4R export | 5.908 s |
| Main landing ten narrow tests | 86.395 s |
| Landed public replay | 1.375 s |

These scopes overlap. D preparation includes native D; complete browser time includes other steps. Their sum is not the session duration. Historical controls still have nontrivial latency, and no subsecond or production SLA is asserted. The runtime avoids an LLM, full D/E or repeated semantic preparation for every click and frame, while keeping actual current effect checks.

Main landing preserves twenty-seven accepted implementation files and nineteen frozen public files byte-for-byte. Admission updates register the exact successor without adding an authority owner. Source, tests, safe evidence and current navigation are committed in `main`; the independent landing report records matching local/remote commit and a clean owner directory. Presentation publication is a subsequent documentation operation, not another runtime admission or a reason to rerun the full demo.

## 18. Verification commands and reading the XML

From the committed repository root, with existing dependencies available, run public replay:

```sh
docs/showcase/ephemeral_workspace_v01/verify_replay.sh 693fc6b5c2e8499161b40dc7bb6c22a21ca040c38325f1e657f176e9ff7bf525
```

`EWS_PYTHON` may select an existing interpreter. Otherwise the wrapper uses the checkout's `.venv/bin/python` or `python3`. It performs no installation, export, model call or workspace launch. This public path does not require the private export inputs.

The five-probe audit is an explicit separate lane:

```sh
EWS4R_PROBE_EVIDENCE="$(mktemp -d)" .venv/bin/python -m pytest -o addopts='' tests/test_ephemeral_workspace_adversarial_v01.py
```

The historical 59-case export audit requires six genuine retained inputs: `EWS4_INPUT_ROOT`, `EWS4_SOURCE_LEDGER`, `EWS4_EXECUTION_HEAD`, `EWS4_TEST_EVIDENCE`, `EWS4R_SUPPLEMENTAL_PROOF_ROOT` and `EWS4R_SUPPLEMENTAL_MANIFEST_SHA256`. Its recorded execution head remains `e42d37fa98dfec7110b8cf75b1aceaa614f461be`, even after landing. Missing private inputs are not replaced by fake fixtures or a claimed PASS. The current showcase README defines these lanes; this appendix does not request that the user run them to view the presentation.

The XML reader combines presentation text, this technical explanation, exact public evidence, implementation sources and identified historical safe projections. It begins with a reading guide, provenance hierarchy and omissions. Exact copies are distinguished from explanatory derivatives. Binary PDF, PPTX and image assets are indexed by identity; readable text and notes carry their informational content. The reader is an inspectable account of what was built and demonstrated, not a capability token or proof that every unstated behavior is correct.
