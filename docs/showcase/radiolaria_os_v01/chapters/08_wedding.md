# Wedding: Changing the Plan Without Losing the Conditions

## The Practical Question

A seating plan is not finished merely because every guest has a table. The organizer may want familiar groups together, prefer people from different circles to meet, or change a particular placement after seeing a first result. Some conditions remain mandatory throughout. Can semantic interpretation, exact computation and an external numerical participant contribute to that evolving activity without silently changing what the organizer asked for?

The recorded Wedding profile makes this question inspectable. Twelve synthetic guests occupy three tables of four. Six pairs must sit together; guests 01 and 05 must sit apart; guest 11 must sit at table 3. Twelve familiarity pairs define the preference to optimize. These are deliberately small, explicit inputs, not observations about a real wedding. The useful outcome is a complete, checked seating arrangement, with a supported route for changing requirements and a separate route for saving a numerical result. [W-W1](../PAPER_SOURCE_KEY.md#w-w1)

There are two related but distinct evidence stages. W3 connects human-language requests to model-returned semantic fields and native Work. W4 connects previously captured meaning to an explicitly chosen quantum backend, measured candidates, classical checks, native consumption and saved files. Neither stage is a story about an external model merely writing application code. Nor should they be edited into one uninterrupted execution.

## A Model Response Becomes Work

Request A asks for a complete plan that keeps familiar circles together while retaining every mandatory restriction. Its two Gemini captures return different contributions: `WEDDING_INTENT_ORCHESTRATOR` returns `task_kind: GENERATE`, review/search/validation needs and requested outputs; `WEDDING_REQUIREMENT_ARCHITECT` returns `objective_profile: KEEP_FAMILIAR_V01`, the required capabilities and no amendments. The actual request body exposes permitted task and objective definitions, not a prescribed seating answer. [W-W1](../PAPER_SOURCE_KEY.md#w-w1), [W-W2](../PAPER_SOURCE_KEY.md#w-w2)

The returned fields do not acquire authority by being fluent or well-formed. `validate_capture_v01` checks request, role, source snapshot, response hash and serialized disclosure. `parse_payload_v01` checks the finite task, capability and amendment vocabulary. `accepted_material_v01` constructs the local owner context and material; its name describes accepted domain input, not a replacement for Root review. `_execute_material_v01` then builds the proposal, bounded Work and local review path. [W-C1](../PAPER_SOURCE_KEY.md#w-c1), [W-C2](../PAPER_SOURCE_KEY.md#w-c2)

For A, the recorded program orders `review`, `compile`, `solve`, `validate`, `consume`. Its compiler invocation really receives material containing the selected profile. The following Work records identify the producer result, downstream Work instance and `/material` field as `USED`, with `decision_effect: bind_input`. The consumed result is `[0,0,0,0,1,1,1,1,2,2,2,2]`, where 0/1/2 mean tables 1/2/3. A local final-result review records `ACCEPT`; it does not request an effect or create permission. This is evidence of use beyond the provider response alone. [W-W3](../PAPER_SOURCE_KEY.md#w-w3)

Request B changes the preference to mixing circles while retaining the same original problem. Its architect actually returns `MIX_CIRCLES_V01`. Compiler input, validation and output retain that value. The result becomes `[0,0,1,1,1,1,2,2,0,0,2,2]`. The guest set, capacity rules and mandatory conditions stay fixed; the objective and seating change. A and B have separate request identities, `request:w3:v02:a` and `request:w3:v02:b`, rather than being two states of an invented common Host. [W-W3](../PAPER_SOURCE_KEY.md#w-w3)

Origin labels matter. The selected A and SR1 native episodes are `CAPTURED_PROVIDER_RESPONSE_REEXECUTION`: genuine earlier role responses were consumed again, without another model call. B, VERIFY, AMBIGUOUS, SR2 and SR3 retain `LIVE_ROLE_ORIGIN`. Their captures are historical live-origin records, not calls made for this chapter. Native `llm: 0` counters cover the pure native lane, not the external semantic exchanges. SR1's original attempt-015 receipt remains `FAILED`, reason `collection_bound`; later captured consumption must not erase that parser failure. [W-W2](../PAPER_SOURCE_KEY.md#w-w2), [W-W3](../PAPER_SOURCE_KEY.md#w-w3)

## Change Two Placements, Preserve the Rest

The SR sequence gives a more demanding example than changing a preference label. SR1 asks for mixing while putting guests 07 and 08 at table 2. Its returned group amendment becomes two typed `ALLOWED_TABLES` conditions. The accepted problem advances to revision 2, and the output places both guests at table 2. [W-W4](../PAPER_SOURCE_KEY.md#w-w4)

SR2 asks: "seat guest_07 and guest_08 at table_1 instead of table_2." The architect's actual response in attempt 017 returns two `REPLACE` amendments. Each names its real prior added condition, its guest, `tables: ["table_1"]` and `source_ref: request:w3:v02:sr2`. The model is not allowed to replace the eight protected base conditions. The parser also requires complete replacement of the prior added requirement, preventing old and new placements from accumulating inconsistently. [W-W2](../PAPER_SOURCE_KEY.md#w-w2), [W-C1](../PAPER_SOURCE_KEY.md#w-c1)

This change has an explicit acceptance and consumption chain. The material records a `SCRIPTED_CONTROLLED_OWNER_INPUT` acknowledgement with `browser_click_claimed: false`. The proposal payload and first Work input also carry a revision Root `ACCEPT`, decision `82c4e166cb503b4f8b5717c48ac6412be0d7d653614ee4e59908fc063fdc3627`. The revised problem is revision 3, with content reference `dd8c7848b55b1325bf75589eb710ce5e6d6fe0dee6e5fa36ec3dc99aa09aefdf`. This is scripted owner input plus recorded local review, not an observed interactive browser consent. [W-W4](../PAPER_SOURCE_KEY.md#w-w4)

The compiler consumes the review result identified as `capability_result:17ade9ca7c6ba2079dd55f2a55c8acced426253d430cc60a46aab596c06d34d0`; its actual input contains the table-1 conditions. Solve, original validation and consumption follow with their own causal field references. The selected arrangement changes from SR1's `[0,0,1,1,2,2,1,1,0,0,2,2]` to `[0,0,1,1,2,2,0,0,1,1,2,2]`: guests 07/08 move to table 1 and guests 09/10 move to table 2. The eight base conditions and mixing objective remain. [W-W4](../PAPER_SOURCE_KEY.md#w-w4)

SR3 asks only to check the current plan. Its request explicitly forbids rearrangement or alternatives; its architect returns a null objective and only `VALIDATE_ORIGINAL`. The accepted context inherits the objective from the actual prior result, rather than pretending that the model selected a new one. Its program contains only `validate` and `consume`, preserving the SR2 arrangement. SR1, SR2 and SR3 remain distinct native tasks, connected where their recorded prior-result references say they are connected. [W-W4](../PAPER_SOURCE_KEY.md#w-w4)

The adverse neighbor is equally concrete. The old SR1 arrangement is `VALID` under revision 2 but `INVALID` under revision 3: the two new placement conditions fail, although its mixing score is still zero. `old_under_new.json` preserves both verdicts and `original_sr1_unchanged: true`. Its unfortunately named `current_root_refusal` field contains `current_owner_context`. In `NativeRunV01.validate_current`, that is the domain owner-context check before further validation, not a newly executed Root rejection. Separately, AMBIGUOUS returns `NEEDS_CLARIFICATION` with zero search calls instead of choosing an objective for the organizer. [W-W5](../PAPER_SOURCE_KEY.md#w-w5), [W-C2](../PAPER_SOURCE_KEY.md#w-c2)

## What the Mathematics Checks

Let `x[g,t]` be a binary indicator for guest `g` at table `t`. The original representation has 36 indicators. The nonnegative integer hard penalty `H` adds squared one-seat and four-guests-per-table deviations, pair-equality penalties for TOGETHER, same-table products for APART, and indicators for forbidden placements. `H = 0` means all original conditions hold in this finite profile. [W-C3](../PAPER_SOURCE_KEY.md#w-c3)

For the familiarity-pair set `F`, the two dimensionless soft costs are:

```text
KEEP(x) = sum_(g,h in F) sum_t (x[g,t] - x[h,t])^2
MIX(x)  = sum_(g,h in F) sum_t x[g,t] * x[h,t]
Q(x)    = P * H(x) + selected_soft_cost(x)
```

On feasible assignments KEEP counts each separated familiar pair twice; MIX counts each co-seated familiar pair once. With twelve familiarity pairs, the compiler chooses `P = 25` for KEEP and `P = 13` for MIX, one above the corresponding feasible soft bound. Given a feasible state, nonnegative integer `H` makes an invalid state's energy exceed every feasible soft score. This separation argument is not a claim that hardware finds the optimum. It is implemented by `ProblemMathV01.components`, `penalty` and `compile_optimization_v01`. [W-C3](../PAPER_SOURCE_KEY.md#w-c3)

`solve_profiles` enumerates balanced assignments; SR2 records 34,650 evaluated assignments. `validate_assignment_v01` independently reports original-condition verdicts and objective components. The separate historical enumeration record gives ten feasible arrangements and five MIX optima for each of SR1 and SR2, with minimum zero. That recorded check is pinned prior evidence, not a new enumeration executed for this chapter. [W-W4](../PAPER_SOURCE_KEY.md#w-w4), [W-W6](../PAPER_SOURCE_KEY.md#w-w6)

## A Measurement Is Still a Candidate

W4 deliberately returns to the original revision-1 problem, not the revised SR2 problem. `preparation_material_v01` consumes the captured A/B meaning under new W4 requests and binds a recorded local angle grid. Its backend field says `CURRENT_W4_OWNER_INTAKE`; historical model needs are explicitly not QPU permission. The numerical program bridge, runtime semantic roles, classical solver and QPU therefore have different jobs. Engineering supplied the supported integration; these records do not demonstrate autonomous provider discovery. [W-Q1](../PAPER_SOURCE_KEY.md#w-q1), [W-C4](../PAPER_SOURCE_KEY.md#w-c4)

The numerical encoding uses five variable guest pairs, two bits each, while the sixth pair is fixed at table 3. It is `PAIR_BINARY_10Q_V02`, an exact substitution with up-to-four-local terms, not a ten-variable QUBO. With measured logical-qubit columns `q[j]` and bits `z[j]`, `measurement_index_v02` computes `sum_j z[j] * 2^q[j]`. Each pair code 0/1/2 maps to a table; code 3 is unseated and never repaired. [W-C5](../PAPER_SOURCE_KEY.md#w-c5)

The KEEP provider result identifies Rigetti `Cepheus-1-108Q`, task `2c896911-1bd9-4c72-9d03-873fb782b59b`, and 1,000 measurements. Raw row 63 is `[1,0,1,0,0,0,0,0,0,1]`, yielding basis 517 and arrangement `[1,1,1,1,0,0,0,0,2,2,2,2]`. Classical checking finds all eleven original verdicts satisfied and objective zero. Of the 1,000 samples, 33 are valid and 967 invalid; 16 distinct valid plans appear. `samples_v01` selects by objective, then assignment, then shot, with `local_repair: false`. The result matches the recorded local optimum; it establishes no quantum advantage. [W-Q2](../PAPER_SOURCE_KEY.md#w-q2)

A measured adverse neighbor prevents a success-only account. KEEP shot 2 yields basis 128 and `[0,0,0,0,0,0,2,2,0,0,2,2]`. Its original-condition report fails capacities at tables 1 and 2 and the guest-01/guest-05 separation. The provider returned it successfully; the application cannot use it as a valid plan. [W-Q2](../PAPER_SOURCE_KEY.md#w-q2)

The separate MIX task `470b472c-590e-42ad-b4f1-6b597be40f6d` returns 42 valid and 958 invalid samples. It selects shot 31, basis 292, objective zero. Its arrangement happens to equal SR2's arrangement, but its problem reference is the original revision-1 reference. Equal seating arrays are not equal problem, task or permission identities. [W-Q2](../PAPER_SOURCE_KEY.md#w-q2)

## From Checked Sample to Saved Result

W4's consuming native program is `qpu_validate`, then `qpu_consume`. KEEP's consumption record explicitly binds the first result's `/material` into the second Work instance as `USED`. The output retains raw SHA-256 `746f6671f68dff12c31f9637c9ddefc4fa1f1692868d569316275abb144bad0e`, shot 63, basis 517 and `LIVE_QPU_RAW_DECODED_POSTSELECTED`. It is not a locally repaired plan substituted for a measurement. Native result acceptance and current save permission are separate. [W-Q3](../PAPER_SOURCE_KEY.md#w-q3)

`save_current_v01` checks the native run and submits exact bytes, path and a time-bounded local scope for a separate Root review. The KEEP JSON save receipt records `SAVED_READBACK_VERIFIED`, 520 bytes and SHA-256 `3756378338308c7f97d438519fabb3a64ae98b3c861b96e10aa46976666689c5`; the HTML has its own receipt. These are saved task-owned reports, not a reservation, invitation or physical seating action. [W-Q4](../PAPER_SOURCE_KEY.md#w-q4), [W-C6](../PAPER_SOURCE_KEY.md#w-c6)

The supported lesson is practical: interpretation can change what is computed, and a later request can validate rather than solve again, while original restrictions remain inspectable. External numerical candidates can join that activity without replacing classical checks or the owner's decisions. This chapter establishes no fresh runtime result, provider attestation, universal workflow synthesis or hardware speedup. Full identities, original-byte pins and exact field projections accompany the text; they make the account inspectable without turning recorded evidence into current authority.

## Paper Citation Namespace

W-W1 through W-W6 identify the W3 intake, semantic and native records; W-Q1 through W-Q4 identify the distinct W4 numerical and save chain; W-C1 through W-C6 identify implementation sources, not new execution evidence. Full repository paths, historical identities, selectors and source classes are collected in the [paper source key](../PAPER_SOURCE_KEY.md). These editorial labels do not rename primary evidence.

## Inspect the Recorded Fields

[CODE_AND_EDITORIAL_PROJECTIONS.json](../references/wedding/CODE_AND_EDITORIAL_PROJECTIONS.json). [SOURCE_LEDGER.json](../references/wedding/SOURCE_LEDGER.json). [CHAIN_LEDGER.json](../references/wedding/CHAIN_LEDGER.json). [PROJECTION_IDENTITIES.json](../references/wedding/PROJECTION_IDENTITIES.json). [W4_PROJECTIONS.json](../references/wedding/W4_PROJECTIONS.json). [CAPTURE_PROJECTIONS.json](../references/wedding/CAPTURE_PROJECTIONS.json). [W3_PROJECTIONS.json](../references/wedding/W3_PROJECTIONS.json).

Projection note: selected save-claim path strings are REDACTED_DERIVED. Their original-value digest and published-value digest are distinct; other selected fields remain exact. [Current projection identities](../references/wedding/PROJECTION_IDENTITIES.json). Original evidence is unchanged.
