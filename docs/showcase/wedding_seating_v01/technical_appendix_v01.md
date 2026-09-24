# Wedding: Technical Appendix V01

The computation changed. The commitment did not.

Accepted implementation: `fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a`. Documentation preparation date: 2026-09-24.

<a id="A01"></a>

## A01 · One intent, different computers, traceable results

A. Executive result | Observed finite case study

Radiolaria’s Wedding case study follows a human request through semantic interpretation, performed work, numerical computation, original-condition checking, current review and a separately approved saved result. The computation changed. The commitment did not.

| Recorded result | What the evidence shows |
| --- | --- |
| 19 Gemini attempts | gemini-2.5-flash, two semantic roles. Fourteen distinct captures contribute to seven final episodes; initial local acceptance was 16 valid and 3 failed. |
| 2 Rigetti tasks | One physical QPU, 1,000 shots per objective. KEEP yielded 33 feasible measurements; MIX yielded 42. |
| 2 accepted plans | Each selected plan is traced to a particular raw measurement, validated, consumed by Work, accepted by OrganizerRoot and saved as JSON/HTML. |
| Portable verification | Saved supported relationships can be checked with an external pin, without a new model, QPU, native Work or effect. |

Both selected objective gaps are zero against the finite reference. This is evidence of the complete recorded activity, not a quantum speedup, a production-readiness certificate or an experiment with 107 guests.

**Accepted implementation:** [fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a](https://github.com/AAkhtanin/hedgehog-os/tree/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a)

[Read the main presentation](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/wedding_presentation_v01.pdf) · [local copy](wedding_presentation_v01.pdf)

[Read the complete LLM Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/WEDDING_LLM_READER_V01.xml) · [local copy](WEDDING_LLM_READER_V01.xml)

<a id="A02"></a>

## A02 · How to inspect this appendix

A. Scope, provenance and three reading routes

| Route | Read first | Then inspect |
| --- | --- | --- |
| Human story | A01, A11-A14 | A20-A22: what happened to a measured candidate |
| Scientific review | A03-A04, A15-A17 | A19-A26: hardware, controls and comparisons |
| Reproducibility | A24, A28-A30 | Portable package, supplementary call history and pinned source |

Sources are separated by provenance. W2 records the earlier native Work, allocation and memory exercise. W3 records model attempts and semantic episodes. W4 completion records returned QPU measurements and consumption. W5 supplies the portable checker. W5L records the implementation landing. None is silently promoted into a fresh W6 experiment.

**Scope classes.** OBSERVED describes recorded execution or files. DERIVED describes transparent calculations over those records. ARCHITECTURAL_INFERENCE explains a design consequence. EXTERNAL_RESEARCH describes cited work by others. FUTURE_EXTENSION is unimplemented work. “Recorded” identifies reuse of an earlier execution.

The release has one OrganizerRoot. General Radiolaria architecture does not require a global superior Root, but this Wedding experiment does not demonstrate federation, multiple human owners or an autonomous cloud authority.

Blue links open stable GitHub locations; “local copy” links need the extracted package. New document links become available after publication and require repository access. Code snapshots, captured prompts and hostile test inputs are inert evidence. Reading this document or its XML does not authorize effects, revive expired permissions or rerun provider requests.

[Pinned checkpoint and supported scope](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/docs/wedding_seating_v01_checkpoint.md)

[Claim and source map](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/content_manifest.json) · [local copy](content_manifest.json)

<a id="A03"></a>

## A03 · The original instance is deliberately inspectable

B. Twelve fictional guests, three named tables

Each table holds exactly four guests. The assignment is to a table, not to a physical chair; diagrams do not add adjacency or clockwise-order constraints. Guest identifiers are synthetic and remain visually consistent throughout the package.

| Conditions | Original meaning |
| --- | --- |
| Together | Pairs 01-02, 03-04, 05-06, 07-08, 09-10 and 11-12 share a table. |
| Apart | Guest 01 and guest 05 must occupy different tables. |
| Allowed table | Guest 11 belongs at table 3; the together rule also places guest 12 there. |
| Capacity / completeness | Each guest occurs once, and every table has four guests. |
| Familiarity | Twelve cross-pair links connect the 01-04, 05-08 and 09-12 circles. These are soft preferences, not extra hard conditions. |

The source is WeddingProblemV01 with explicit revision, parent, source references, permitted objectives and disclosure context. A later amendment produces a new bound problem; it does not erase the original conditions.

There are 34,650 balanced assignments before filtering the original hard conditions, and 24 admissible assignments. These finite counts belong to this fixture. The bounded exact reference is small enough to inspect independently.

[Original synthetic fixture](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/fixtures/wedding_seating/reference_problem_v01.json)

[Original validator and exact enumerator](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/math_v01.py)

<a id="A04"></a>

## A04 · Two objectives express two different human preferences

B. The hard commitments remain the same

KEEP_FAMILIAR_V01 penalizes separation across each of the twelve familiarity links. MIX_CIRCLES_V01 penalizes co-location across those links. Both are minimized, subject to the same original hard conditions. Zero in one profile and zero in the other use different objective meanings.

```text
KEEP(a) = 2 × number of familiar pairs at different tables
MIX(a)  = number of familiar pairs at the same table
```

| Finite original fixture | KEEP | MIX |
| --- | --- | --- |
| Feasible assignments | 24 | 24 |
| Minimum objective | 0 | 0 |
| Tied optimal assignments | 2 | 12 |
| Overlap of optimal sets | None | None |

The local W3 A/B comparison consumed different model-selected profiles and produced different valid plans. W4 later selected measured candidates; those hardware plans are a separate evidence stage and need not match the local tie-broken plan.

Classical exact solving and angle selection were openly performed before hardware submission. The experiment therefore makes no claim that the QPU discovered an unknown optimum or outperformed a classical solver. The measured candidate still had to be an actual returned row; a classical result was not substituted for a failed measurement.

[Objective components and penalty bounds](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/math_v01.py)

[Local semantic outputs](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w3/story/A.json) · [local copy](evidence/portable/w3/story/A.json)

<a id="A05"></a>

## A05 · Every attempted model contribution remains visible

C. One Gemini model; all nineteen serialized sends

| Call / role | Initial status | Final use | Selected field |
| --- | --- | --- | --- |
| 01 ORCH | VALIDATED | Historical | GENERATE |
| 02 ARCH | VALIDATED | Historical | KEEP_FAMILIAR |
| 03 ORCH | FAILED | Historical | GENERATE |
| 04 ORCH | VALIDATED | A | GENERATE |
| 05 ARCH | VALIDATED | A | KEEP_FAMILIAR |
| 06 ORCH | VALIDATED | B | GENERATE |
| 07 ARCH | VALIDATED | B | MIX_CIRCLES |
| 08 ORCH | VALIDATED | Historical | VALIDATE_EXISTING |
| 09 ARCH | FAILED | Historical | null / VALIDATE_EXISTING |
| 10 ORCH | VALIDATED | VERIFY | VALIDATE_EXISTING |
| 11 ARCH | VALIDATED | VERIFY | null / VALIDATE_EXISTING |
| 12 ORCH | VALIDATED | AMBIGUOUS | CLARIFY |
| 13 ARCH | VALIDATED | AMBIGUOUS | null / CLARIFY |
| 14 ORCH | VALIDATED | SR1 | GENERATE |
| 15 ARCH | FAILED | SR1 | MIX_CIRCLES |
| 16 ORCH | VALIDATED | SR2 | REVISE |
| 17 ARCH | VALIDATED | SR2 | MIX_CIRCLES |
| 18 ORCH | VALIDATED | SR3 | VALIDATE_EXISTING |
| 19 ARCH | VALIDATED | SR3 | null / VALIDATE_EXISTING |

ORCH = intent orchestrator; ARCH = requirement architect. Initial status is local contract acceptance, not a measured model-accuracy rate. Call 15 was consumed after a bounded parser repair without changing its raw answer. Five captures remain historical only.

[Full requests, raw answers and receipts](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/WEDDING_LLM_READER_V01.xml) · [local copy](WEDDING_LLM_READER_V01.xml)

<a id="A06"></a>

## A06 · Model calls 01-04: meaning and consumption

C. Summaries are paraphrases; raw responses are linked

Call 01 · ORCH · initial VALIDATED · Historical

The initial orchestrator selected GENERATE and requested review, exact search and original validation. This successful capture was retained as development history; the final A comparison used the common V02 prompt.

**Observable fields:** task_kind="GENERATE"; needs=["REQUIREMENT_REVIEW","EXACT_SEARCH","ORIGINAL_VALIDATION"]; requested_outputs=["SEATING_CANDIDATES","VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_001/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_001/response.txt)

Call 02 · ARCH · initial VALIDATED · Historical

The initial architect selected KEEP and the finite compile/solve/validate catalogue. It was not one of the fourteen final selected captures.

**Observable fields:** task_kind="GENERATE"; objective_profile="KEEP_FAMILIAR_V01"; needed_capabilities=["COMPILE_QUBO","SOLVE_EXACT","VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_002/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_002/response.txt)

Call 03 · ORCH · initial FAILED · Historical

The initial MIX response omitted VALIDATION_REPORT from requested_outputs. The local output contract refused it. The catalogue wording was clarified for both A and B, preserving this failed attempt.

**Observable fields:** task_kind="GENERATE"; needs=["REQUIREMENT_REVIEW","EXACT_SEARCH","ORIGINAL_VALIDATION"]; requested_outputs=["SEATING_CANDIDATES"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_003/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_003/response.txt)

Call 04 · ORCH · initial VALIDATED · A

Under the common V02 prompt, the orchestrator requested a complete generation path and both candidate and validation outputs. It is consumed in final episode A through captured-response reexecution.

**Observable fields:** task_kind="GENERATE"; needs=["REQUIREMENT_REVIEW","EXACT_SEARCH","ORIGINAL_VALIDATION"]; requested_outputs=["SEATING_CANDIDATES","VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_004/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_004/response.txt)

<a id="A07"></a>

## A07 · Model calls 05-08: meaning and consumption

C. Summaries are paraphrases; raw responses are linked

Call 05 · ARCH · initial VALIDATED · A

The architect selected KEEP_FAMILIAR_V01. This field reached optimization and actual Work; it is not a decorative annotation beside a separately chosen solver.

**Observable fields:** task_kind="GENERATE"; objective_profile="KEEP_FAMILIAR_V01"; needed_capabilities=["COMPILE_QUBO","SOLVE_EXACT","VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_005/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_005/response.txt)

Call 06 · ORCH · initial VALIDATED · B

The live orchestrator selected GENERATE for the mixing request, with requirement review, exact search and original validation. Final episode B records live-role origin.

**Observable fields:** task_kind="GENERATE"; needs=["REQUIREMENT_REVIEW","EXACT_SEARCH","ORIGINAL_VALIDATION"]; requested_outputs=["SEATING_CANDIDATES","VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_006/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_006/response.txt)

Call 07 · ARCH · initial VALIDATED · B

The live architect selected MIX_CIRCLES_V01. The accepted profile changed coefficients and the optimal result while preserving original hard restrictions.

**Observable fields:** task_kind="GENERATE"; objective_profile="MIX_CIRCLES_V01"; needed_capabilities=["COMPILE_QUBO","SOLVE_EXACT","VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_007/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_007/response.txt)

Call 08 · ORCH · initial VALIDATED · Historical

The first verify orchestrator asked only for ORIGINAL_VALIDATION and VALIDATION_REPORT. It was retained historically after the paired architect exposed an overstrict boundary.

**Observable fields:** task_kind="VALIDATE_EXISTING"; needs=["ORIGINAL_VALIDATION"]; requested_outputs=["VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_008/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_008/response.txt)

<a id="A08"></a>

## A08 · Model calls 09-12: meaning and consumption

C. Summaries are paraphrases; raw responses are linked

Call 09 · ARCH · initial FAILED · Historical

The architect returned a legitimate null objective for checking an existing plan. The initial parser rejected objective_scope. The repair inherited only source-bound prior profile information, without rewriting raw null.

**Observable fields:** task_kind="VALIDATE_EXISTING"; objective_profile=null; needed_capabilities=["VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_009/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_009/response.txt)

Call 10 · ORCH · initial VALIDATED · VERIFY

The resumed verify orchestrator again selected VALIDATE_EXISTING. The resulting native path did not compile a QUBO, encode a circuit or search for a new seating.

**Observable fields:** task_kind="VALIDATE_EXISTING"; needs=["ORIGINAL_VALIDATION"]; requested_outputs=["VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_010/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_010/response.txt)

Call 11 · ARCH · initial VALIDATED · VERIFY

The resumed architect returned null with VALIDATE_ORIGINAL. The bound preceding result supplied the profile for validation; the raw response remained null.

**Observable fields:** task_kind="VALIDATE_EXISTING"; objective_profile=null; needed_capabilities=["VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_011/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_011/response.txt)

Call 12 · ORCH · initial VALIDATED · AMBIGUOUS

The orchestrator selected CLARIFY and named the unresolved objective. It did not invent whether the owner wanted familiar circles or mixing.

**Observable fields:** task_kind="CLARIFY"; needs=["LOCAL_CLARIFICATION"]; requested_outputs=["CLARIFICATION"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_012/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_012/response.txt)

<a id="A09"></a>

## A09 · Model calls 13-16: meaning and consumption

C. Summaries are paraphrases; raw responses are linked

Call 13 · ARCH · initial VALIDATED · AMBIGUOUS

The architect kept objective_profile null, capabilities empty and amendments empty. AMBIGUOUS performs no native search or new seating plan.

**Observable fields:** task_kind="CLARIFY"; objective_profile=null; needed_capabilities=[]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_013/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_013/response.txt)

Call 14 · ORCH · initial VALIDATED · SR1

The orchestrator requested generation with a designated-table condition while preserving mandatory restrictions. Final SR1 consumes this genuine response as captured reexecution.

**Observable fields:** task_kind="GENERATE"; needs=["REQUIREMENT_REVIEW","EXACT_SEARCH","ORIGINAL_VALIDATION"]; requested_outputs=["SEATING_CANDIDATES","VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_014/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_014/response.txt)

Call 15 · ARCH · initial FAILED · SR1

The architect proposed one ADD for guests 07 and 08 at table 2. The consumer initially rejected collection_bound; a bounded expansion into two single-guest conditions admitted the same immutable response.

**Observable fields:** task_kind="GENERATE"; objective_profile="MIX_CIRCLES_V01"; needed_capabilities=["COMPILE_QUBO","SOLVE_EXACT","VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_015/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_015/response.txt)

Call 16 · ORCH · initial VALIDATED · SR2

The orchestrator selected REVISE for the later placement change. The earlier problem and its record were preserved rather than silently overwritten.

**Observable fields:** task_kind="REVISE"; needs=["REQUIREMENT_REVIEW","EXACT_SEARCH","ORIGINAL_VALIDATION"]; requested_outputs=["SEATING_CANDIDATES","VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_016/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_016/response.txt)

<a id="A10"></a>

## A10 · Model calls 17-19: meaning and consumption

C. Summaries are paraphrases; raw responses are linked

Call 17 · ARCH · initial VALIDATED · SR2

The architect replaced both actual prior added-condition identities, moving guests 07 and 08 to table 1. This is a source-bound revision, not an unreferenced fresh instruction.

**Observable fields:** task_kind="REVISE"; objective_profile="MIX_CIRCLES_V01"; needed_capabilities=["COMPILE_QUBO","SOLVE_EXACT","VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_017/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_017/response.txt)

Call 18 · ORCH · initial VALIDATED · SR3

The orchestrator selected VALIDATE_EXISTING for SR3, requesting only the current plan’s validation report. No new alternative was requested.

**Observable fields:** task_kind="VALIDATE_EXISTING"; needs=["ORIGINAL_VALIDATION"]; requested_outputs=["VALIDATION_REPORT"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_018/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_018/response.txt)

Call 19 · ARCH · initial VALIDATED · SR3

The architect selected VALIDATE_ORIGINAL, null objective and no amendments. SR3 inspected the revised plan without another search.

**Observable fields:** task_kind="VALIDATE_EXISTING"; objective_profile=null; needed_capabilities=["VALIDATE_ORIGINAL"]

[Original answer; full receipt in Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_019/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_019/response.txt)

<a id="A11"></a>

## A11 · Seven episodes changed the performed activity

D. Separate requests, separate source identities

| Episode | Meaning | Performed outcome |
| --- | --- | --- |
| A | Generate / KEEP | Compile, exact search, validate and consume a KEEP plan. |
| B | Generate / MIX | Same hard law; changed objective and resulting valid plan. |
| VERIFY | Inspect the existing A plan | Validate and consume; no new search or encoding. |
| AMBIGUOUS | Objective unspecified | CLARIFY; no invented objective or generated plan. |
| SR1 | Mix; put pair 07-08 at table 2 | ADD accepted after bounded group expansion; new problem revision. |
| SR2 | Move that pair to table 1 | REPLACE both prior added conditions; new result under current revision. |
| SR3 | Inspect the revised result | Validate and consume SR2’s current plan, without search. |

Final A and SR1 use genuine captured model responses in named reexecutions. B, VERIFY, AMBIGUOUS, SR2 and SR3 carry LIVE_ROLE_ORIGIN. “Live” describes the origin of the recorded role contribution, not a new model call during document preparation.

The six native tasks have 24 PURE dispatches and four searches. AMBIGUOUS is a semantic clarification episode without native Work. These are not seven labels placed over one fictional continuous task identity.

[Portable semantic evidence](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w3/story/SR3.json) · [local copy](evidence/portable/w3/story/SR3.json)

<a id="A12"></a>

## A12 · A revised condition creates a new current problem

D. SR1 → SR2 → SR3, with the old history intact

```text
SR1: ADD ALLOWED_TABLES {guest_07, guest_08} -> table_2
SR2: REPLACE both actual SR1 condition IDs -> table_1
SR3: VALIDATE_EXISTING; no amendments; no new search
```

SR2 names the actual SR1 additions. Their full identifiers are **added:cefff2237df9864e94438b6db02b436e** for guest 07 and **added:3f21ee24070770e6a7dbc90bd1272907** for guest 08. Complete group replacement avoids leaving half of the earlier instruction active.

| Observed bound output | T1 | T2 | T3 |
| --- | --- | --- | --- |
| SR1 | 01,02,09,10 | 03,04,07,08 | 05,06,11,12 |
| SR2 and SR3 | 01,02,07,08 | 03,04,09,10 | 05,06,11,12 |

The SR1 seating was valid for its own problem version. Under SR2 it is no longer current. The recorded refusal occurs at the domain-context boundary before a new Root decision; describing it as a fresh Root REJECT would invent an execution.

Owner acknowledgement is explicitly SCRIPTED_CONTROLLED_OWNER_INPUT. A real native Root review follows that bound acknowledgement, but the package does not claim a filmed human approval event or a production consent interface.

[SR1 source](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w3/story/SR1.json) · [local copy](evidence/portable/w3/story/SR1.json)

[SR2 source](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w3/story/SR2.json) · [local copy](evidence/portable/w3/story/SR2.json)

[Call 17 exact replacement fields](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/supplementary/w3/captures/attempt_017/response.txt) · [local copy](evidence/supplementary/w3/captures/attempt_017/response.txt)

<a id="A13"></a>

## A13 · Model proposals enter Work through explicit contracts

E. Native consumption, with a finite one-cell D profile

The intent orchestrator proposes the activity and needed work. The requirement architect proposes the objective and typed changes. Domain checks bind those contributions to the actual request, permitted catalogue, source problem and disclosure projection. A valid model answer is a contribution, not a permission to act.

| Boundary | Concrete responsibility |
| --- | --- |
| C / source context | Build eligible, source-bound composition inputs from the accepted role contributions. |
| D / Work | Review and perform the finite domain task using declared capabilities. W2’s measured D reviews were approximately 12.75-12.91 seconds. |
| Original validator | Check the candidate against the original conditions and the current bound problem revision. |
| OrganizerRoot | Review the current result and scope. The only owner Root in this experiment is the organizer. |
| Application / SAVE | Bind the exact output bytes and destination to a separate current save decision. |

The observed D topology is a bounded one-cell profile. A large recursive tree is not inferred from the word “fractal.” Work is real and its material outputs are consumed, but a diagram should not invent branches or a broader parallel deployment.

W2’s main controlled history used five native tasks and 23 PURE dispatches. W3’s semantic history used six tasks and 24 dispatches. Those stage-specific totals must remain separate.

[Native adapter](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/native_adapter_v01.py)

[Native capabilities](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/native_capabilities_v01.py)

<a id="A14"></a>

## A14 · Allocation and memory performed useful bounded work

E. Recorded W2 evidence, not a new learning experiment

W2’s C6 allocation has a budget of six: two mandatory jobs and four optional table diagnostics. The optional work was actually dispatched. Cohesion at tables 1 and 2 returned 4 each; mixing at tables 1 and 2 returned 2 each. These actual outputs entered the consumer; planned checks were not counted as performed.

| Mechanism | Observed use | Limit |
| --- | --- | --- |
| G4 allocator | Selected four additional diagnostics and consumed their results. | Partial diagnostic coverage; not a new calibration benchmark. |
| LocalDRS | Stored and searched meaning, applied eligibility and descended through a current Root review. | Local scope only; no external DRS federation. |
| Conflict / recovery | Kept a contradiction explicit, then continued with current valid inputs. | No restoration of old action permissions. |
| History | Supplied relevant source-bound context to new work. | No fresh GT rating or universal learning claim. |

LocalDRS recorded three writes, seven queries and two fresh Root summary descents. Five reuse-eligibility refusals comprise one time refusal and four scope refusals. Search blocked_count is zero: search hits and reuse eligibility are different denominators.

This matters because semantic contribution is larger than text generation: the system can decide which bounded checks are worthwhile and which stored context is eligible. The current experiment uses these mechanisms selectively, without claiming every Radiolaria subsystem was exercised.

[Allocation implementation](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/allocation_v01.py)

[Local memory interface](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/memory_v01.py)

<a id="A15"></a>

## A15 · The 36-variable QUBO preserves the original conditions

F. Exact formulation and a finite penalty proof

Let x[g,t] be binary: guest g is assigned to table t. There are twelve guests and three tables. Hard penalty H is a sum of nonnegative integer terms; H = 0 exactly when the modeled original conditions hold.

```text
H = Σg (Σt x[g,t] - 1)² + Σt (Σg x[g,t] - 4)²
  + Σtogether(g,h),t (x[g,t] - x[h,t])²
  + Σapart(g,h),t x[g,t] x[h,t]
  + Σforbidden(g,t) x[g,t]
```

```text
F_KEEP = Σfamiliar(g,h),t (x[g,t] - x[h,t])²
F_MIX  = Σfamiliar(g,h),t x[g,t] x[h,t]
E_KEEP = 25H + F_KEEP
E_MIX  = 13H + F_MIX
```

On any feasible assignment, F_KEEP ≤ 24 and F_MIX ≤ 12. If H is nonzero, H ≥ 1. The soft terms are nonnegative, so multiplier 25 or 13 makes every invalid state more expensive than every feasible state, provided a feasible state exists. This proves separation for the finite model; it does not prove hardware success.

The compiler expands these expressions into canonical quadratic coefficients. Independent reference enumeration checks balanced assignments and original predicate verdicts. The reference problem has 24 feasible assignments and objective minimum zero in both profiles.

[Compiler, evaluator and original-condition validator](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/math_v01.py)

<a id="A16"></a>

## A16 · Exact reduction retains every admissible assignment

F. Six mandatory pairs become ten logical bits

The six TOGETHER pairs can be represented as units. Pair 11-12 is fixed at table 3 by an original allowed-table condition. Each of the remaining five pairs uses two bits to select one of three tables; the fourth code is invalid. This is exact domain reduction, not a learned approximation.

```text
Per free pair: code 0 -> table_1
               code 1 -> table_2
               code 2 -> table_3
               code 3 -> unseated / invalid
Five free pairs × two bits = 10 logical bits
```

All 1,024 reduced basis states are defined. The 24 admissible original assignments are retained; invalid or unseated states remain subject to the original penalty. The selected raw row is decoded, never repaired by inserting a classical seating.

Substitution of the pair code into the original energy yields a diagonal cost Hamiltonian with interactions up to order four. Calling this a ten-variable QUBO would be incorrect: the canonical original model is quadratic in 36 one-hot variables; the reduced gate model has higher-order terms.

The measurement decoder uses returned measured-qubit columns, not an assumed display endianness. Its basis index is the sum of bit[q] × 2^q. Reordered-column controls preserve the same decoded candidate; malformed, duplicate or foreign columns are refused.

[Exact reduced encoding and measurement decoder](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/encoding_v02.py)

<a id="A17"></a>

## A17 · Classical preparation is part of the disclosed experiment

F. Bounded angle selection and source-circuit equivalence

The gate circuit uses a single QAOA layer. The local angle grid has 768 candidates per profile. Its selected integer grid indices are (9,22) for KEEP and (16,22) for MIX, with scale 4,096. These choices are classical preparation, not output invented by the LLM or a hidden quantum search over circuit parameters.

| Source circuit property | Recorded / derived value |
| --- | --- |
| Logical qubits | 10 |
| Nonidentity Walsh terms | 105 |
| Hadamard gates | 10 |
| RZ rotations | 105 |
| CNOT gates | 310 |
| RX mixer rotations | 10 |
| QAOA depth parameter | p = 1 |

These are submitted logical-source counts. They are not a claim about Rigetti’s physical compiled depth, physical placement or hardware error rate. The returned compiledProgram is retained separately from the source OpenQASM.

Local circuit/state checks establish equivalence to the declared finite diagonal energies and the chosen parameters. They do not simulate the actual device noise or certify a speed advantage. The returned measured rows must pass original-condition validation regardless of the circuit check.

[Circuit construction and exact finite checks](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/circuit_v02.py)

[KEEP submitted OpenQASM](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/numeric/KEEP_FAMILIAR_V01/source.qasm) · [local copy](evidence/portable/w4/numeric/KEEP_FAMILIAR_V01/source.qasm)

[MIX submitted OpenQASM](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/numeric/MIX_CIRCLES_V01/source.qasm) · [local copy](evidence/portable/w4/numeric/MIX_CIRCLES_V01/source.qasm)

<a id="A18"></a>

## A18 · The provider receives an approved numerical projection

G. Disclosure, identity and the trusted boundary

| Projection | Contains | Does not establish |
| --- | --- | --- |
| Local private context | Owner-side source and synthetic private fields. | That pseudonyms are cryptographic anonymity. |
| Semantic projection | Approved safe intent, allowed catalogue, bound structural facts and revisions. | Authority for arbitrary new actions. |
| Numerical projection | Approved OpenQASM, device, shots and result destination. | That all relational information stayed on the computer. |

The recorded cloud principal is the IAM user radiolaria-quantum, rather than the account root. That principal observation does not by itself prove a complete least-privilege policy audit. Browser login and cloud policy administration were separate owner setup activity.

The trusted computing base includes the local host/runtime, original validator, domain bridge, local environment and approved cloud account access. Low-level Braket HTTP and local file writes are separate application boundaries alongside native PURE work; they are not newly invented native effect kinds.

Hashes and pins bind exact bytes and supported relationships. They are not provider signatures, independent physical execution attestation or proof that every factual statement is true. Synthetic structural disclosure is explicit; no production confidentiality guarantee is inferred.

[Actual bridge request and scope checks](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/qpu_bridge_v01.py)

[Projection checks](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/privacy_v01.py)

[Recorded runtime and device preflight](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/read_only_preflight.json) · [local copy](evidence/portable/w4/provider/read_only_preflight.json)

<a id="A19"></a>

## A19 · Two actual tasks reached the same Rigetti device

G. Recorded account returns, not two separate computers

Amazon Braket accepted two tasks for Rigetti Cepheus-1-108Q, with 1,000 shots each. Both ran the original synthetic instance under different objective profiles. The device name and identity come from the saved response, not from an example in generic SDK documentation.

| UTC, 24 September 2026 | KEEP | MIX |
| --- | --- | --- |
| Created | 07:18:23.886 | 07:18:47.069 |
| Recorded ended | 09:00:12.621 | 09:00:13.377 |
| Task suffix | 2c896911…b59b | 470b472c…0f6d |
| Final recorded state | COMPLETED | COMPLETED |
| Requested / returned rows | 1,000 / 1,000 | 1,000 / 1,000 |

The roughly 102-minute intervals include queueing and execution. They are not QPU compute-time measurements, Root-decision latency or a speed comparison. The later 96.7104-second resume command is an operator-wrapper duration.

The account return retains action, task metadata, device identity, measured-qubit mapping, all rows and returned compiledProgram. The ledger retains the stable submission token, request identity and approved scope. Result storage identities remain linked to those same tasks.

[Durable submission and completion ledger](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/ledger.json) · [local copy](evidence/portable/w4/provider/ledger.json)

[KEEP returned result](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/KEEP_FAMILIAR_V01_results.json) · [local copy](evidence/portable/w4/provider/KEEP_FAMILIAR_V01_results.json)

[MIX returned result](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/MIX_CIRCLES_V01_results.json) · [local copy](evidence/portable/w4/provider/MIX_CIRCLES_V01_results.json)

<a id="A20"></a>

## A20 · KEEP: one measured row became an accepted saved plan

H. Original validation, native consumption and separate SAVE

| All returned measurements | Count |
| --- | --- |
| Rows | 1,000 |
| Feasible / invalid | 33 / 967 |
| Distinct feasible plans | 16 |
| Optimal / feasible nonoptimal | 5 / 28 |

```text
Selected zero-based shot index: 63
Measured bits q0..q9: 1010000001
Basis index = Σq bit[q] × 2^q = 517
```

| Table 1 | Table 2 | Table 3 |
| --- | --- | --- |
| 05, 06, 07, 08 | 01, 02, 03, 04 | 09, 10, 11, 12 |

The exact decoded assignment satisfies the original conditions and scores zero under its own objective. No local repair was applied. Because the objective is nonnegative, this feasible zero witness matches the finite reference optimum.

Rejected real row: KEEP shot 2 decodes to eight guests at table 1, none at table 2 and four at table 3, also violating APART condition_07. Invalid-sample share is not a measurement of hardware noise.

Saved evidence links raw bytes to selected index, decoded assignment, performed validation/consumption, current OrganizerRoot ACCEPT and the exact JSON/HTML SAVE claim. Re-rendering those saved bytes later is not a new authorized SAVE event.

[Selected-row validation record](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/KEEP_FAMILIAR_V01_sample_validation.json) · [local copy](evidence/portable/w4/provider/KEEP_FAMILIAR_V01_sample_validation.json)

[Actual native consumption](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/native/KEEP_FAMILIAR_V01/consume.json) · [local copy](evidence/portable/w4/native/KEEP_FAMILIAR_V01/consume.json)

[Exact accepted seating JSON](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/outputs/KEEP_FAMILIAR_V01/seating.json) · [local copy](evidence/portable/w4/outputs/KEEP_FAMILIAR_V01/seating.json)

[Separate SAVE receipts](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/outputs/KEEP_FAMILIAR_V01/save_receipts.json) · [local copy](evidence/portable/w4/outputs/KEEP_FAMILIAR_V01/save_receipts.json)

<a id="A21"></a>

## A21 · MIX: one measured row became an accepted saved plan

H. Original validation, native consumption and separate SAVE

| All returned measurements | Count |
| --- | --- |
| Rows | 1,000 |
| Feasible / invalid | 42 / 958 |
| Distinct feasible plans | 20 |
| Optimal / feasible nonoptimal | 18 / 24 |

```text
Selected zero-based shot index: 31
Measured bits q0..q9: 0010010010
Basis index = Σq bit[q] × 2^q = 292
```

| Table 1 | Table 2 | Table 3 |
| --- | --- | --- |
| 01, 02, 07, 08 | 03, 04, 09, 10 | 05, 06, 11, 12 |

The exact decoded assignment satisfies the original conditions and scores zero under its own objective. No local repair was applied. Because the objective is nonnegative, this feasible zero witness matches the finite reference optimum.

Rejected real row: MIX shot 1 decodes to table occupancies 2, 6 and 4, violating both table 1 and table 2 capacities. Invalid-sample share is not a measurement of hardware noise.

Saved evidence links raw bytes to selected index, decoded assignment, performed validation/consumption, current OrganizerRoot ACCEPT and the exact JSON/HTML SAVE claim. Re-rendering those saved bytes later is not a new authorized SAVE event.

[Selected-row validation record](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/MIX_CIRCLES_V01_sample_validation.json) · [local copy](evidence/portable/w4/provider/MIX_CIRCLES_V01_sample_validation.json)

[Actual native consumption](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/native/MIX_CIRCLES_V01/consume.json) · [local copy](evidence/portable/w4/native/MIX_CIRCLES_V01/consume.json)

[Exact accepted seating JSON](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/outputs/MIX_CIRCLES_V01/seating.json) · [local copy](evidence/portable/w4/outputs/MIX_CIRCLES_V01/seating.json)

[Separate SAVE receipts](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/outputs/MIX_CIRCLES_V01/save_receipts.json) · [local copy](evidence/portable/w4/outputs/MIX_CIRCLES_V01/save_receipts.json)

<a id="A22"></a>

## A22 · Waiting preserved identity without extending permission

I. Queueing, known-task resume and current review

W4 first ended with both original tasks QUEUED. That was a pending state, not an artificial success. Resume read the same recorded task identities. It did not create replacements, reset the episode budget or resubmit merely because the first observation window had ended.

| Event | Meaning |
| --- | --- |
| Reserve and submit | Two slots are durably reserved; request identities and client tokens are fixed. |
| Pending observation | The initial archive reports QUEUED and no accepted hardware seating. |
| Resume known tasks | Read results for existing ARNs; no new submission. |
| Fresh preparation / review | Current wall-clock context prepares and consumes returned material. Old submission permission is not revived. |
| Exact save | New current claims bind output bytes, path, result and time. |

The completed episode has no unused task allowance. An unknown submission outcome requires exact reconciliation; an automatic retry could create ambiguity about side effects. A fresh experiment would need a new approved episode and current scope.

The two-slot reservation totals $1.45 in the saved ledger. This is a bounded accounting reservation, not an invoice or a verified final AWS charge. Queue duration and host observation cost remain separately described.

[Durable reservation and resume rules](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/qpu_bridge_v01.py)

[Public operator boundaries](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/operator_v01.py)

[Original and resumed parent links](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/evidence/portable/w4/provider/ledger.json) · [local copy](evidence/portable/w4/provider/ledger.json)

<a id="A23"></a>

## A23 · Negative controls target specific acceptance boundaries

J. Recorded controlled mutations with positive neighbors

| Pair | Refused perturbation | Positive neighbor / boundary |
| --- | --- | --- |
| RP1 Egress | Private or foreign semantic material: check_egress_v01 refuses before mock transport. | The exact approved semantic projection reaches one controlled send. |
| RP2 Revision | Previously valid SR1 seating presented under current SR2. | SR2’s exact current plan passes; old plan fails current_owner_context, without a new Root REJECT. |
| RP3 Display | Coherently changed displayed plan with mismatched source relationships. | Original saved display passes supplied_displayed_plan validation. |
| RP4 Pending send | Lost acknowledgement leaves outcome unknown; blind submit fails not_a_fresh_send. | The actual recorded pending tasks later resume by the same identities, without new submission. |
| RP5 Consumed result | Substituted native material output. | The restored original passes actual_consumed_output checking. |

Additional recorded pairs cover changed QPU request scope (RP6) and expired or revoked permission (RP7). Missing or wrong external pins are separately refused. The W5 test suite also re-pins controlled modified packages with explicitly test-only pins so that semantic predicates are exercised beyond simple hash mismatch. Those pins are test instruments, not owner approval or permission to accept modified evidence.

These are finite hostile mutations, not captured attacks by real adversaries. Initial model-contract refusals and earlier failed commands remain historical failures. A successful later repair does not erase them or turn them into new experiments.

[Exact RP1-RP7 source matrix in the Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/WEDDING_LLM_READER_V01.xml) · [local copy](WEDDING_LLM_READER_V01.xml)

[Portable refusal matrix and positive controls](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/tests/test_wedding_seating_portable_v01.py)

[Actual request, codec and SAVE controls](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/tests/test_wedding_seating_qpu_v01.py)

<a id="A24"></a>

## A24 · Read-only verification checks saved relationships

K. A pinned package, a supported reader, no new experiment

Use the accepted implementation and its checked Python 3.14 environment with existing core dependencies. The read-only path does not require AWS or Gemini credentials, numpy, boto3, botocore, Braket or Google SDKs. The command reads a copied portable package; it does not install dependencies.

```text
python demo/run_wedding_seating_v01.py verify \
  --input /your/copy/evidence/portable \
  --expected-sha256 "$INDEPENDENT_MANIFEST_SHA256" \
  --output /your/new/verification.json
```

**Portable manifest identity:**
3c924898bedf03cf97df5f59cbc553e3d6f54cc9a60eaaf72c8019ac33bf1552

Obtain the expected identity from an independent trusted owner/reviewer channel. A digest printed inside an untrusted package is not an independent anchor. This appendix records the historical reviewed identity for comparison; it does not manufacture a new trust source.

Supported checks cover exact source, semantic contributions, original constraints, numerical representation, task/device/shots, all measurements, selection, performed intermediate outputs, recorded Root relationships, save bytes and recorded event times. No exact-search oracle is invoked; a nonnegative objective and feasible zero witness support the stated reference.

Unsupported: full native-schema replay, provider cryptographic attestation, current permission, arbitrary new fixtures or suboptimal references. The result classification is SAFE_DERIVED_SAVED_RELATIONSHIPS_AT_RECORDED_EVENT_TIMES.

[Verifier implementation](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/hedgehog/domains/wedding_seating/portable_v01.py)

[Verification instructions and source map](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/README.md) · [local copy](README.md)

<a id="A25"></a>

## A25 · The problem is familiar; the engineering unit differs

L. Academic comparison without a borrowed benchmark

| Source | What it contributes | Comparison boundary |
| --- | --- | --- |
| L1 PuLP | Set partitioning wedding example; explicit subsets and objective modeling. | A modeling reference, not our measured competitor. |
| L2 Bellows / Peterson | A seating formulation and a 107-person instance with best-found search and later human changes. | No claim that its 107-person plan is a proved optimum. |
| L3 OR-Tools | A CP-SAT wedding seating example and standard solver statuses. | A credible classical implementation route; not run here. |
| L4 Nicholas / Mulligan | Wedding seating mapped to classical and quantum optimizers in a 2026 preprint. | Its instances, devices and reported results are not our experiment. |
| L5 Masala Core | An extensible plugin architecture used in that research. | It is not fairly described as a rigid linear pipeline. |

Constraint models, local feasibility checks, solver plugins and quantum sampling are established ideas. The contribution illustrated here is organizing the whole activity: model-selected work, bound revisions, approved disclosure, heterogeneous computation, current acceptance and inspectable evidence.

This is an architectural comparison. There is no head-to-head timing study, quality leaderboard, universal reliability ranking or claim that Radiolaria invented feasibility checking. D-Wave’s own CQM and sample APIs already expose such checks.

[Bibliography with primary sources](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/SOURCES.md) · [local copy](SOURCES.md)

<a id="A26"></a>

## A26 · A 107-guest profile is an engineering extension

L. Concrete path, explicit unimplemented boundaries

The published instance contains twelve fictional guests. The 107-guest example belongs to cited prior work and motivates a future domain profile. The current pair reduction, capacities, schema bounds, encoding and provider contract cannot simply be stretched by replacing the number 12.

| Must change | Why |
| --- | --- |
| Domain contract / validation | Generalize N, table capacities, rule bounds and feasible assignment representation. |
| Solver / encoding | Choose an appropriate CP-SAT, MILP, decomposition or reviewed QPU formulation. Ten logical bits no longer describe the problem. |
| Budget / capability policy | Re-estimate cost and supported work. Larger search requires explicit limits and failure behavior. |
| Fixtures / acceptance | Establish independent baselines, infeasibility cases, revision tests and original-condition checking. |
| Provider / release scope | Review any new disclosure, device, task allowance and source-admission delta. |

What can stay conceptually stable is task ownership: the human intent, model contribution, current source-bound work, original-condition validation, explicit acceptance and recorded evidence chain. That is an architectural inference from separation of concerns, not a 107-person PASS.

For supported rule families, indexed assignment checking can plausibly scale with guests, tables and rule count; solver search is a separate complexity. O(N + T + M) is a prospective validator design argument under stated indexing assumptions, not a benchmark of this implementation.

Logistics and other domains are possible extensions, not deployments proved by this seating demonstration.

[Source-backed extension analysis](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/SOURCES.md) · [local copy](SOURCES.md)

<a id="A27"></a>

## A27 · Claims remain tied to their evidence class

M. Public claim map and the boundary of interpretation

| Claim group | Observed or derived basis | Limit |
| --- | --- | --- |
| C01-C07 Semantics | Nineteen immutable captures; A/B task changes; revision lineage; explicit clarification and historical failures. | Finite task/profile catalogue; no universal reasoning result. |
| C08-C13 Hardware | Exact reduction; actual returned rows; original checks; zero-gap selections; known-task continuation. | One device, two tasks; no speedup or physical attestation. |
| C14-C16 Boundaries | Approved projections, recorded IAM principal, accepted 34-file addition delta. | Synthetic privacy scope; no general least-privilege certification. |
| C17-C19 Mechanisms | Recorded G4/DRS work and current read-only saved-evidence validation. | No new learning calibration, external federation or native replay. |
| C20-C22 Architecture | Comparison, extension path and preservation of governing conditions. | Architectural inference, not a global quality ranking or automatic failover. |

Each detailed content-manifest record links its exact source member and hash, pointer or lines, derived expression, observed value, caveat, slide, appendix anchor and Reader record. Repetition across a slide and this appendix is navigation, not another test.

The hardware workflow changed from the initial annealing-oriented D-Wave plan to implemented gate-based Rigetti through Braket. Developers changed the integration. No live D-Wave-to-Rigetti automatic failover was observed.

[Machine-readable public claims](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/content_manifest.json) · [local copy](content_manifest.json)

<a id="A28"></a>

## A28 · The implementation is landed; the documents are a new capsule

M. Coverage, release state and preserved history

| Stage | Recorded validation / result |
| --- | --- |
| W1 | 24 unique tests; exact mathematical contracts and local SDK/OpenQASM checks. |
| W2 | Nine targeted tests; actual controlled native history and clean supplied proof. Full historical suite not declared all-green. |
| W3 | 20 tests and 21 subtests; two identical clean supplied results; nineteen actual Gemini attempts retained. |
| W4 completion | Two exact hardware-return chains with independent offline proof; no new submissions in completion review. |
| W5 | 17 final tests; two independent offline checks, 17.47 / 17.39 seconds, identical canonical result. |
| W5L | Six guard and six binder checks; installed offline PASS in 5.88 seconds; ordinary push and remote readback. |

W5L installed exactly 34 additions. The prior 2,508 files and all 26 special POSIX modes were preserved. Index and working tree were clean, review context FINALIZED, and the remote matched the accepted implementation commit.

These are stage-specific receipts, not one aggregate fresh test run. W6 prepares an inert documentation capsule; no model, QPU, AWS, native Work or effect execution is added. Publication remains a separate reviewed documentation landing.

The checkpoint preserves dated W3/W4 pending passages as history. Current completion records supersede their status for the exact named tasks; editing a PDF does not retroactively change historical evidence.

[W6 QA and final package checks](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/QA_REPORT.md) · [local copy](QA_REPORT.md)

[Accepted implementation checkpoint](https://github.com/AAkhtanin/hedgehog-os/blob/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a/docs/wedding_seating_v01_checkpoint.md)

<a id="A29"></a>

## A29 · Primary references define the comparison and method

M. Bibliography | accessed 24 September 2026

**L1.** COIN-OR PuLP, “A Set Partitioning Problem.” Wedding case study. [Primary documentation](https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html)

**L2.** Meghan L. Bellows and J. D. Luc Peterson, “Finding an optimal seating chart.” Annals of Improbable Research, February 2012. Full-problem description on the fifth printed PDF page. [Paper](https://improbable.com/news/2012/Optimal-seating-chart.pdf)

**L3.** Google OR-Tools, wedding_optimal_chart_sat.py; CP-SAT solution statuses. [Example](https://github.com/google/or-tools/blob/stable/examples/python/wedding_optimal_chart_sat.py); [Solver documentation](https://developers.google.com/optimization/cp/cp_solver)

**L4.** Karie A. Nicholas and Vikram Khipple Mulligan, “Entangled happily ever after: Wedding reception seating mapped to classical and quantum optimizers.” arXiv:2604.10497v2, 22 April 2026. Methods II, Results III, Discussion IV. [Preprint](https://arxiv.org/abs/2604.10497v2)

**L5.** Flatiron Institute, Masala Core public repository and README. [Repository](https://github.com/flatironinstitute/masala_public)

**T1-T4.** [D-Wave supported countries](https://support.dwavesys.com/hc/en-us/articles/360051869733-From-What-Countries-Can-I-Access-D-Wave-s-Leap-Quantum-Cloud-Service); [Braket OpenQASM submission](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-create-submit-task.html); [Braket task tracking](https://docs.aws.amazon.com/braket/latest/developerguide/braket-monitor-tasks-sdk.html); [D-Wave CQM feasibility](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/generated/dimod.ConstrainedQuadraticModel.check_feasible.html).

**M1-M5.** [OSDI 2026 artifact call](https://www.usenix.org/conference/osdi26/call-for-artifacts); [USENIX Security 2026 artifact call](https://www.usenix.org/conference/usenixsecurity26/call-for-artifacts); [CMU SEI assurance cases](https://www.sei.cmu.edu/blog/assurance-cases-and-confidence/); [NIST AI RMF Measure](https://airc.nist.gov/airmf-resources/playbook/measure/); [Assertion-Evidence approach](https://www.assertion-evidence.com/).

These sources guide claim/evidence organization, reproducibility and presentation. No conference badge, independent certification or NIST conformance is claimed. Repository links may require authorized GitHub access.

[Full source catalogue and scope notes](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/SOURCES.md) · [local copy](SOURCES.md)

<a id="A30"></a>

## A30 · Exact audit handles make independent inspection possible

M. Frozen implementation, archive anchors and next action

**Implementation commit**
fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a

**Implementation tree**
97708773152e8fc147ce64d2a965a6b9534340c4

**W3 archive SHA-256**
b90ed0636dbd58520d8840a003e4f6d3c956236d2283ee84dbf0afe3ef3f8997

**W4 hardware-completion archive SHA-256**
e257e24ffe490734d64aa4673f04998f5b1b93fb18102649879d9518e2f65171

**W5 portable manifest SHA-256**
3c924898bedf03cf97df5f59cbc553e3d6f54cc9a60eaaf72c8019ac33bf1552

**Canonical W5 verification result SHA-256**
e4a1a644776da341368af07eeb5a0317f7fca4dcda25e5bb23c7004aacad09b0

**W5L landing archive SHA-256**
a06fdde231a241383eaf2c686de2d2f3d1ff26e7d6bd88c534af8b94b07d3cea

The portable manifest is unchanged. Supplementary W3 history includes all nineteen original attempts; W2 details are separately source-bound. The old portable checker does not silently acquire authority over every newly published supplementary file.

The next step is reviewed DOCUMENTATION publication through the existing R1 process. No future publication commit is guessed inside covered files. After publication, verify the actual remote commit and document links independently.

[Full LLM Reader](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/WEDDING_LLM_READER_V01.xml) · [local copy](WEDDING_LLM_READER_V01.xml)

[Claims / sources / rendered values](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/content_manifest.json) · [local copy](content_manifest.json)

[Local package entry](https://github.com/AAkhtanin/hedgehog-os/blob/main/docs/showcase/wedding_seating_v01/README.md) · [local copy](README.md)
