# The Workspace Can Change While the Task Continues

## A Task, Not a Permanent Application

A person wants to review photographs and a short video, keep useful selections, and then finish. The environment should bring the needed capabilities together without making the person reconstruct the task whenever a participant disappears. Ephemeral Workspace gives this idea a bounded, concrete form: local media access, preview rendering, display, controls, optional audio, and a separately gated save operation become participants in one temporary activity.

The question is not simply whether a tailored interface can appear. Can the environment lose a capability, continue useful work without discarding unaffected results, save only what was separately approved, and end while leaving inspectable evidence? The principal recorded EWS3R2 browser run answers that question for synthetic local photo/media work. A separate historical EWS3 profile demonstrates later informational retrieval. These are related demonstrations, not one invented continuous session. This chapter is an editorial account bound to accepted source HEAD `2e965ecb18e545e428380eb8e9aa5a7037a388be`, not a new execution. [Sources: [WS-appendix](../PAPER_SOURCE_KEY.md#ws-appendix), [WS-claims](../PAPER_SOURCE_KEY.md#ws-claims), [WS-index](../PAPER_SOURCE_KEY.md#ws-index) in the source ledger.]

## Birth: Available Capabilities Become Actual Work

The mixed request asks to browse, rate and select photographs, adjust exposure and crop, and review video with audio. It explicitly permits silent visual continuation if audio disappears, forbids modification of originals and publication, and requires separate confirmation before saving. The fixtures comprise six synthetic photographs and an eight-second, sixteen-frame sequence, with mono 8 kHz PCM tones. They are not camera RAW development, compressed-video decoding, recorded speech, or proof of sound from a physical speaker.

Three semantic contributions make the task precise. The orchestrator supplies needs; the architect supplies preview, cleanup, save and audio obligations; the privacy reviewer supplies minimization and an allow/block decision. In the principal run these were three `CONTROLLED_DETERMINISTIC` outputs from `local-semantic-rules-v01`, with no provider call. In particular, `audio_policy="SILENT_CONTINUE"` and `minimize="preview_without_metadata"` affect subsequent work, rather than merely decorating a report.

Runtime materializes `compile_contract` and `consume_contract`: the second Work item consumes the first item's actual output. Root route review and later command authority remain separate from semantic proposals. The finite contract organizes scoped local services; it does not discover arbitrary devices or let a model author an unrestricted execution graph. One persistent Host and local Root retain the action boundary. [Exact selections: [WS-P_controlled_0](../PAPER_SOURCE_KEY.md#ws-p_controlled_0) through [WS-P_controlled_2](../PAPER_SOURCE_KEY.md#ws-p_controlled_2), [WS-P_topology](../PAPER_SOURCE_KEY.md#ws-p_topology).]

## What the Photo Controls Actually Mean

The interface supports manual rating and selection. `RATE` stores a chosen integer from zero to five; it is not an aesthetic model score. The principal scripted browser sequence selects `asset:1`, sets rating five, exposure five tenths and `SQUARE` crop. The interaction is real browser activity, but `SCRIPTED_BROWSER_TEST` is not evidence that the owner personally clicked. Even an endpoint labelled `MANUAL_OWNER_CONFIRMATION` does not change that provenance.

Exposure is a preview brightness transform, implemented as `2**(exposure/10)`, where exposure is an integer in tenths. It is not a camera sensor or RAW-pipeline claim. `SQUARE` and `WIDE` select centered aspect-ratio crops; `ORIGINAL` leaves the aspect ratio unchanged. The renderer converts input to RGB, applies these transforms, resizes within the preview bounds, and emits a fresh PNG. Originals remain unchanged; the preview is a derived representation.

Under the principal privacy policy, display receives derived pixels and bounded frame information, not source paths or embedded metadata. Removing metadata does not hide visible image content, erase pixels already viewed, or isolate processes sharing the same host account. These distinctions explain both the useful feature and its actual boundary. [Sources: [WS-render_code](../PAPER_SOURCE_KEY.md#ws-render_code), [WS-session_code](../PAPER_SOURCE_KEY.md#ws-session_code); selections [WS-P_sidecar](../PAPER_SOURCE_KEY.md#ws-p_sidecar), [WS-P_complete](../PAPER_SOURCE_KEY.md#ws-p_complete).]

## Change: Audio Disappears, the Task Does Not

After four delivered video frames and 16,000 PCM samples, the demonstration deliberately kills its owned AudioSink. This is an actual process loss, not a checkbox simulating unavailability. Media work pauses pending a fresh observation and continuation decision. Photo work remains retained.

Time matters. The old action packet had already expired when the loss occurred. The corrected path acquires new changed-source evidence within the unchanged workspace lifetime, without modifying the old packet, its Root-bound authority, or the original D baseline. The meaningful negative neighbor is an attempted use of that old packet: the recorded result is `host_current_action_not_executable`. New knowledge about a resource therefore does not renew an old permission.

The history also preserves the earlier failed integration, which reused an old observation interval and received `dependency_observation_time_invalid` before E began. The successful successor is not presented as an uninterrupted first attempt. [Sources: [WS-r2_report](../PAPER_SOURCE_KEY.md#ws-r2_report); selections [WS-P_temporal](../PAPER_SOURCE_KEY.md#ws-p_temporal), [WS-P_complete](../PAPER_SOURCE_KEY.md#ws-p_complete).]

## Continuation: Change the Affected Work, Preserve the Rest

EWS-C14 identifies one top-level D setup, one public E invocation, and one retained D recomputation within E. E follows the changed source into an actual recomputed result, retains a distinct unaffected D sibling, and records its consumption. The source implementation checks the changed-source binding, completed output, causal parent chain, retained result and photo bytes. This is selective recomputation, not zero recomputation or a UI-only status change.

EWS-C15 supplies an observable outcome. Silent playback adds twelve frames, taking the total from four to sixteen; PCM stays at 16,000 samples. Immediately before loss and automatically after E, before fresh commands, the photo Work/state/preview snapshot is equal. Its preview hash is `114187f18e0b3773feb36def9751076cf72dcd367a2fa1c3d862be0269dea298`; the photo-preview producer count stays three. Command/effect history stays seven across E, rather than being reset.

The later informational Root review requests no effect and creates no permission. PLAY and SAVE still require their own current command path. The result is useful continuity without treating either old work or new evidence as renewed authority. [Exact selections: [WS-P_consumption](../PAPER_SOURCE_KEY.md#ws-p_consumption), [WS-P_topology](../PAPER_SOURCE_KEY.md#ws-p_topology), [WS-P_events](../PAPER_SOURCE_KEY.md#ws-p_events), [WS-P_temporal](../PAPER_SOURCE_KEY.md#ws-p_temporal); code: [WS-continuation_code](../PAPER_SOURCE_KEY.md#ws-continuation_code).]

## Saving Is a Separate Decision

EWS-C16 separates requesting a save from performing it. `REQUEST_SAVE` forms a candidate without writing the output file. Owner-origin approval binds the exact session/version, output slot, selected assets, ratings, exposure, crop and intended bytes. SAVE needs an unused matching approval and a current packet. A changed selection or changed parameters no longer match the previously approved candidate.

The principal outcome is one 250-byte `selection.json`, with SHA-256 `20e01b3ebd6f813bccf2ce51d23c71406a0f2b2cd706ab8bda92e71bed28a915`. Its selection records `asset:1`, rating five, exposure `5`, `SQUARE`, and the original source digest. This sidecar saves selection and preview parameters, not a transformed replacement photograph. It neither overwrites an original nor publishes anything. Recorded approval, packet and receipt bindings explain the completed write; none can authorize the next write merely by existing in history. [Exact selections: [WS-P_save_packet](../PAPER_SOURCE_KEY.md#ws-p_save_packet), [WS-P_save_receipt](../PAPER_SOURCE_KEY.md#ws-p_save_receipt), [WS-P_sidecar](../PAPER_SOURCE_KEY.md#ws-p_sidecar); code: [WS-session_code](../PAPER_SOURCE_KEY.md#ws-session_code).]

## Ending Means Releasing Owned Resources

EWS-C21 records `CLOSED_SUCCESS`. Cleanup reaps three owned service processes, closes two viewer-server threads, and stops the finite media thread. The audio child reports `ALREADY_EXITED`, return code `-9`, and `receipt=null`. Display and media separately report `GRACEFUL_CLOSE_ACKNOWLEDGED`, return code zero. It would be false to give the killed audio child a graceful receipt.

The owner page showed a closed workspace; the archived report also records coordinator reaping and browser-tab closure. Those UI/process facts do not imply erasure of the browser's previously downloaded pixels. Storage cleanup removes only owned preview-cache files whose device, inode and content still match. A replacement is preserved; an ownership/content conflict would produce `CLEANUP_INCOMPLETE`, not a fabricated success. Original fixtures and the approved sidecar remain.

This is an initial resource-owner cleanup obligation at a finite synchronous image/IPC boundary, not asynchronous preemption of arbitrary programs or a universal host sandbox. Ephemeral refers to the working environment, not destruction of every result or every trace. [Exact selections: [WS-P_complete](../PAPER_SOURCE_KEY.md#ws-p_complete), [WS-P_teardown](../PAPER_SOURCE_KEY.md#ws-p_teardown); sources: [WS-service_code](../PAPER_SOURCE_KEY.md#ws-service_code), [WS-session_code](../PAPER_SOURCE_KEY.md#ws-session_code), [WS-r2_report](../PAPER_SOURCE_KEY.md#ws-r2_report).]

## History Remains Inspectable, Not Executable Authority

The principal record remains available as pinned evidence after closure. A distinct historical EWS3 memory sequence goes further: it writes a semantic recipe and a saved-work summary to durable LocalDRS, outside disposable previews, then retrieves information with fresh Root-reviewed `SUMMARY_ONLY` descent. Its saved selection is rating four, `ORIGINAL` crop and exposure zero, not the principal rating-five sidecar.

That historical informational request records zero model calls, effects, new service activations, new workspace instances and sidecar writes. Changed-scope neighbors return `BLOCKED_BY_SCOPE` with `drs_address_scope_mismatch`; history remains stored while current applicability changes. Accepted historical LIVE role outputs were followed by strict `CAPTURED_REEXECUTION` with fresh Host/resources. Nine provider attempts produced six accepted responses and three failures. None of that is relabelled as live semantics in the principal controlled run. [Selections: [WS-P_memory](../PAPER_SOURCE_KEY.md#ws-p_memory), [WS-P_saved_information](../PAPER_SOURCE_KEY.md#ws-p_saved_information), [WS-P_measured](../PAPER_SOURCE_KEY.md#ws-p_measured), [WS-P_live_accounting](../PAPER_SOURCE_KEY.md#ws-p_live_accounting).]

## The Common Meaning

The environment changes while the task continues because Work, resource availability, retained results, permission and history have distinct lifecycles. The person specifies purpose and significant conditions; supported capabilities carry out the organized activity. Applications and integration engineering remain necessary. The broader principle also permits memory needs to arise inside child Work, but these EWS records do not prove arbitrary child-memory chains or global discovery.

The lifecycle graph presents these relationships with separate principal and historical lanes. The public package and later presentation records are derivatives, not raw execution; the older EWS4R seal does not cover later projections or this chapter. The accompanying inspection route checks hashes and selected values without starting the workspace, importing project code or rerunning tests. It makes the account inspectable without pretending that reading evidence restores a live Host or a current grant.


## Inspect the Recorded Fields

[lifecycle_graph.json](../references/ews/lifecycle_graph.json). [source_ledger.json](../references/ews/source_ledger.json). [validation_report.json](../references/ews/validation_report.json). [selected_field_projections.json](../references/ews/selected_field_projections.json).
