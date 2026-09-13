# Common Action and Dynamic Composition Contract v0.1

## 1. Status, Observable Goal and Authority

CONTRACT_STATUS=PROPOSED_EXACT_NINE_PATH_SUCCESSOR
RUNTIME_IMPLEMENTATION=NOT_IMPLEMENTED
U1_U2_U3_ACCEPTANCE=NOT_CLAIMED
IMPLEMENTATION_AUTHORIZED=false

Current accepted C is `19de35c3b77725c4763b33cbac5c42118fd3c382`, tree
`165ff53990fc9451b634a526c4e7387f7767e923`, sole child of implementation I
`90cb073695bf8c5f5a2673c7aba84b6615719b37`. Gate2 and bounded internal RC2
history remain accepted. This is a proposed contract, not an executable seam,
an active schema, new runtime acceptance, public release or production claim.
Owner contract acceptance and a later exact source-edit authorization remain
separate. U1/U2/U3 are work steps, not new architectural Gates.

Before: generic action profiles exist, but modern genesis is admitted through
a Supplier payment aggregate. The mock Firewall returns bounded consumption
evidence without computing a capability's typed business result. C and D
execute real route/control work; they do not accept an arbitrary capability
program. After the assigned implementation: native nonpayment and legacy
payment use one lifecycle, actual admitted outputs feed one bounded program
handler, and the owning Root's current state gates each consequential call.
Later same-task continuation and independently admitted missing pure code are
mandatory U2/U3 results, not capabilities claimed by this document.

U0 proves only **D_ROLE=CONTROL; CONSUMER_KIND=SCRATCH_PROTOTYPE**. It does not
prove business computation, common action, composition, continuation, code
admission or DRS reuse. D's `d3local:output:*` observations are not media or
sensor results. An admitted capability must actually compute that data.

This contract is subordinate to the [Current Architecture Lock](../specs/current_architecture_lock_v01.md).
Root alone decides locally. BSEP is the semantic membrane; Architect/model
proposals, runtime topology, DRS, Post-V&V, GT, replay and receipts are not
authority. There is no SuperRoot or transfer of permissions. The existing
[Whole Gate2 checkpoint](consolidated_gate2_gauntlet_g2_f_checkpoint_v01.md)
and audit remain unchanged historical acceptance evidence for their sources.

## 2. Evidence and Source Conventions

U0 archive: `RADIOLARIA_UNIVERSALITY_U0_D_PUBLIC_BINDING_PROOF_V01_RETURN_20260908T124244Z.tar.gz`,
SHA256 `72ead838b3a2c3bea97886ae62cc496582be747909a2f424968c8e1133c14e3d`,
1069012 bytes, 221 regular members, 220 manifest rows. Independently reviewed
recorded execution is reused, not rerun by U1 preparation. Three public D
entries and three corresponding internal entries mean **three executions**,
not six. Recorded experiment elapsed time is 941.466289 seconds.

P1 and fresh equivalent P2 select full_semantic: one completed cell, 35 queue
entries, `READY_SINGLE_CELL_REVIEW`. C1 changes only
`full_semantic.policy_allowed` true to false, rebuilding policy provenance;
the same business/BSEP selects full_fractal: three completed cells, 75 queue
entries, two completed children, `READY_RECURSIVE_REVIEW`. `continue_review`
remains true; no business dispatch occurs. Missing required D input rejects;
a valid P1 bundle paired with an independently built wrong-task source fails
public contextual validation (`g2d_topology_identity_mismatch`).

Reviewer clarification: scratch supplies `review_action='ACCEPT'` as an input.
Public C/Root functions compute and validate the decision; scratch does not
fabricate a successful Root result. C's canonical route advisory is not a
post-D final Root. D produces its own ResultProposal/Post-V&V/GT/upward return.
Typed zero counts and inspected offline paths are not OS monitoring.

All unqualified existing action symbols below are in
[`hedgehog/action_commit_packet_v02.py`](../hedgehog/action_commit_packet_v02.py).
Firewall symbols are in [`effect_firewall_v01.py`](../hedgehog/kernel/effect_firewall_v01.py).
`NEW` explicitly denotes a proposed symbol, absent at C. Exact nominal types,
not duck typing, subclasses, dictionaries or model-provided callables, govern
runtime admission. New validators return `(bool, tuple[str, ...])` in action
and ordered reason tuples in Firewall, following each module's public style.
Builders reject on the first actual reason; evidence stores the actual result.
No status string supplied by the caller constitutes validation.

## 3. Immutable Action Carriers and Public Construction

NEW `NativeActionCommitPacketV01` is a frozen aggregate. Its fields, in the
following order, are mandatory; a native action has no `source_packet`, bank
account, payment slot or monetary requirement. `str` identities are normalized
by existing action identity functions. Integers exclude booleans. Tuples are
immutable and canonicalized by the existing corresponding profile builder.

| Field | Exact type | Producer and validation | Actual consumer |
| --- | --- | --- | --- |
| transaction_id, owning_local_root_id | str, str | normalized nonempty local transaction/Root; all profiles agree | candidate, Root input, registry and host |
| canonical_permission_ref, selected_canonical_action | str, str | validate_canonical_permission_ref_v01; normalized action in allowed_action_classes, never an effect-class alias | actual Root permission_state and Firewall action binding |
| normalized_subject_scope | ActionSubjectScopeProfileV01 | build/validate_action_subject_scope_profile_v01 | logical intent, candidate, containment |
| normalized_target_scope | ActionTargetScopeProfileV01 | build/validate_action_target_scope_profile_v01 | logical intent, candidate, per-target dispatch |
| normalized_permission_scope | ActionPermissionScopeProfileV01 | build/validate_action_permission_scope_profile_v01 | candidate and Firewall permission/scope checks |
| business_effect_parameters | ActionEffectParametersProfileV01 | existing project_consequential_effect_parameters_v01; exact B equation in section4 | business input resolution, separate from authorization control records |
| execution_binding | NativeExecutionBindingV01 (NEW, action module) | build/validate_native_execution_binding_v01 from the admitted source snapshot | exactly four authorization-only records |
| execution_source | CapabilityAdmissionSnapshotV01 (NEW, Firewall module) | snapshot_admitted_capability_v01 after actual trusted admission validation; structural snapshot validation is not fresh admission | reconstruct X; compare to current trusted admission before Root review/dispatch |
| normalized_effect_parameters | ActionEffectParametersProfileV01 | NEW recompose_native_action_effect_parameters_v01 and its contextual validator, using existing profile builders | A_native fingerprint, not the business logical key |
| adapter_binding | ActionAdapterBindingProfileV01 | build/validate_action_adapter_binding_profile_v01 | allowed corridor, operation implementation |
| dependency_candidate | DependencySetCandidateV01 | build/validate_dependency_set_candidate_v01 | Root dependency acceptance, eligibility and E |
| temporal_authority | ActionTemporalAuthorityProfileV01 | build/validate_action_temporal_authority_profile_v01 | current TTL, no post-Root expansion |
| authority_policy | ActionAuthorityPolicyProfileV01 | build/validate_action_authority_policy_profile_v01 | logical namespace, classes, retry and supersession |
| business_object_identity | ActionBusinessObjectIdentityProfileV01 | build/validate_action_business_object_identity_profile_v01 | owning-effect identity and idempotency |
| consequential_effect_parameters | ActionConsequentialEffectParametersProfileV01 | build/validate_action_consequential_effect_parameters_profile_v01 | intent and idempotency; absent amount/currency together |
| logical_intent | RootOwnedLogicalEffectIntentV01 | build/validate_root_owned_logical_effect_intent_v01 | same Root-owned logical effect across encodings |
| idempotency_identity | ActionIdempotencyIdentityV01 | build/validate_action_idempotency_identity_v01 | shared reservation/consumption domain |
| authorization_candidate | RootBoundPacketAuthorizationCandidateV01 | build/validate_root_bound_packet_authorization_candidate_v01 | actual semantic/Root authorization chain |
| evaluation_time, evaluation_time_source, evaluation_context_id | int, str, str | existing canonical time/context validators | eligibility baseline, not a live-state selector |
| temporal_evaluation | TemporalEvaluationV01 | evaluate_temporal_authority_v01 on retained authority/time; equality checked | actual Root temporal_state, not caller-supplied success |
| normalized_effect_parameters_fingerprint, dependency_set_candidate_fingerprint, temporal_authority_fingerprint, authority_policy_fingerprint | str each | existing fingerprint builders from the retained profiles | candidate equality and source binding |

NEW `build_native_action_commit_packet_v01` takes the above profile/context
inputs as keyword-only arguments, derives fingerprints/intent/idempotency and
candidate, and returns this aggregate. It never accepts supplied derived IDs
as authoritative. NEW `validate_native_action_commit_packet_v01(value)` checks
exact type, every profile, recomputed identities and cross-profile coherence.
The structural validator does not create Root acceptance.

NEW `NativeRootBoundActionCommitPacketV01` has exactly four fields:
`canonical_projection: NativeActionCommitPacketV01`,
`root_decision_projection: RootDecisionCandidateProjectionV01`,
`packet_identity: ActionCommitPacketIdentityResultV01`,
`dependency_acceptance_binding: PacketDependencyAcceptanceBindingV01`.
NEW `build_native_root_bound_action_commit_packet_v01(*, canonical_projection,
root_decision_projection)` computes packet and dependency identities only
after the existing actual Root kernel/input/result validate. NEW
`validate_native_root_bound_action_commit_packet_v01(value)` repeats this
binding. No fabricated legacy packet is present.

The exact common admission set is NativeRootBoundActionCommitPacketV01 OR
SupplierRootBoundActionCommitPacketV02ProjectionV01. NEW
`validate_common_root_bound_action_commit_packet_v01(value)` first dispatches
on exact type. Legacy takes its unchanged public Supplier/domain/identity
validator; native takes its validator above. NEW
`common_action_view_v01(value)` then returns a frozen `CommonActionViewV01`:
encoding tag (`SUPPLIER_V02` or `NATIVE_V01`), the original encoded object,
the canonical fields above, Root projection, packet identity and accepted
dependency binding. It copies references to validated immutable profiles,
not canonical bytes or histories. No permissive attribute-based admission.

Cross-profile invariants share one common implementation extracted from existing
`_validate_g2a1a_cross_profile_coherence_impl_v01` and the generic part of
`_validate_supplier_root_bound_projection_impl_v01`. Supplier-only tests remain
in Supplier admission, not in common dispatch. The effect-profile rebuild is
encoding-specific exactly as section4 specifies; it is not removed. The C
legacy equation cannot validate A_native by projecting consequential material
alone. CommonActionView uses optional native-only business/execution fields
(None for exact SUPPLIER_V02); it must not add fields to the legacy aggregate.
Root candidate kind/ID,
normalized claim, contribution, review packet, PostVV/GT selection, decision
input/result, transaction and owning Root remain mutually bound. Use existing
`build_root_decision_candidate_projection_v01` and its validator; add NEW
`validate_common_root_context_coherence_v01(projection, canonical_projection)`
to check native generic context and delegate legacy to
`validate_supplier_root_context_coherence_v01`. Root/time/ABI sources do not
change. A valid aggregate with a foreign or merely route-acceptance decision
is not an authorized action.

Construction order: admitted typed inputs -> generic profiles -> intent and
candidate -> actual semantic contribution/review -> PostVV/GT -> independent
owning Root decision -> candidate projection/context check -> bound packet ->
accepted dependencies -> public genesis -> reserve/activate -> queue/pending ->
current-state eligibility -> exclusive Firewall dispatch -> validated actual
result -> shared lifecycle consumption/evidence -> read-only replay.

## 4. Identity and Cross-Encoding Consumption

Canonical material uses existing ordered `CanonicalMaterialV01`,
`canonical_material_bytes_v01` and `build_domain_separated_identity_v01`;
no new JSON normalization scheme. Existing intent/idempotency equations and
domains are unchanged. In particular the material includes Root, transaction
or actual intent identity, logical class/namespace, normalized subject/target,
business object and consequential parameters. The consumption key is the
existing `ActionIdempotencyIdentityV01.idempotency_key`, scoped to its owning
effect Root. It is never a model string, chosen duplicate key or packet hash.

### 4.1 Selected Business/Execution Normalization (PROPOSED_DESIGN)

Let Q be the exact retained ActionConsequentialEffectParametersProfileV01.
It contains BUSINESS amount/currency/quantity and declared consequential
records only. The selected equations and validation order are:

1. Validate all exact nominal profiles, descriptor semantics and supplied
   business inputs. Rebuild B with existing
   `project_consequential_effect_parameters_v01(effect_class=logical_class,
   consequential_parameters=Q)`; require exact `business_effect_parameters == B`.
2. Build L with existing `build_root_owned_logical_effect_intent_v01` over
   Root, local transaction, logical class/namespace, subject/target scopes,
   business object and Q. Build K with `build_action_idempotency_identity_v01`
   over those SAME fields plus L.root_owned_intent_id. Compare full existing
   material and retained types/IDs, not just their string prefixes.
3. Reconstruct X from the actual admitted definition, implementation and
   input/output contract identities; validate the retained immutable source
   snapshot, and compare it to the host's actual trusted admission at current
   construction/review/dispatch. Snapshot consistency alone cannot admit code.
4. Build A_native from B.effect_class and B.parameter_records plus exactly
   four records, using existing `build_action_effect_parameter_record_v01`
   and `build_action_effect_parameters_profile_v01`. Compare full A_native.
5. Use existing `build_action_effect_parameters_fingerprint_v01(A_native)`
   over `action_effect_parameters_material_v01(A_native)`. Rebuild the existing
   RootBoundPacketAuthorizationCandidateV01 with this fingerprint and every
   other retained scope/adapter/dependency/time/policy/Root/intent field. Require
   full candidate equality. Actual independent Root review follows, not precedes,
   this candidate construction. All other common coherence checks stay active.

NEW frozen `NativeExecutionBindingV01` has exactly these four ordered str
fields, with the SAME reserved parameter names:
`capability_definition_ref`, `capability_implementation_ref`,
`capability_input_contract_ref`, `capability_output_contract_ref`.
Each is a canonical nonempty prefixed identity derived as section6.2 specifies.
Every corresponding record has value_type exactly REFERENCE. X has no verdict,
permission, business value or user-supplied key. NEW public action functions
`build_native_execution_binding_v01(*, admitted_capability)` and
`validate_native_execution_binding_v01(value, admission_snapshot)` bind exact
types/source identities; the builder requires actual valid admission, the
snapshot validator establishes retained consistency only. NEW
`recompose_native_action_effect_parameters_v01(*, business_effect_parameters,
execution_binding, admission_snapshot)` and
`validate_native_action_effect_parameters_v01(value, business_effect_parameters,
execution_binding, admission_snapshot)` implement steps3-4 with exact public
profile validation. Missing/extra refs, incorrect type/value/source, duplicate
names and any of the four reserved names in Q, B or declared user fields reject.
Existing canonical UTF-8 parameter-name ordering applies to the entire union;
neither insertion order nor model prose chooses canonical bytes.

A_legacy remains EXACTLY B under the old Supplier projection. Legacy coherence,
canonical materials, domains, IDs and class identity are untouched. X never
enters Q, L or K. A_native is not asserted equal to B and is not projected back
into Q by dropping arbitrary fields. Its only difference from reconstructed B
is the exact source-validated four-record union. Native builder inputs include
the admitted capability and actual business input tuple; B/X/source are derived
fields, not independently trusted caller answers. Structural native validation
does not replace current admission or actual Root acceptance.

### 4.2 Business Meaning Cannot Disappear Into a Technical Binding

The exact CapabilityBusinessSemanticsV01 declaration in section6 binds
operation_key to the policy-accepted logical_effect_namespace/class and selected
canonical action; it also fixes business-object class/namespace and an exhaustive
input mapping. operation_key equals logical_effect_namespace: two different
consequential operations cannot share it merely by changing descriptor IDs.
Distinct action implementations may share that key only under a trusted,
explicit same-operation declaration and the same Root policy. The model cannot
declare an arbitrary semantic change technical. Nontrivial code equivalence is
an admission obligation, not proved by a digest or this contract-only witness.

Every executor input is mapped to an exact Q field/record or business-object
reference; subject/target-valued input records additionally require membership
in their bound scope. Their roles remain named in Q, not lost in an unordered
set of resources. resource_refs must equal the declared target scope (canonical
set), never silently introduce another target. All input names/types/values
must equal the resolved tuple and the admitted input contract, with no extras
or implicit defaults. No executable user input is authorization-only. The four
control refs are NOT executor arguments. Pure work has its own typed input
contract, not an invented consequential K.

For the existing Supplier payment family, operation_key/logical namespace is
supplier.payment.v01, logical class PAYMENT, business object PAYMENT_SLOT in
supplier.payment_slot.v01. Input amount_decimal and currency_code map directly
to Q.amount_decimal and Q.currency_code; included creditor/slot target refs
remain the actual scope. This preserves the legacy business material, rather
than adding an operation label to an old Q. New operations needing distinct
meaning use their actual namespace/class and named consequential parameters.
Amount/currency/quantity/role/target changes must change the relevant existing
business material and therefore the L/K computation. A claimed semantic change
with unchanged authorized business material is rejected before dispatch.

A code-only or input/output-contract identity change may retain identical
B/L/K ONLY when the authorized business meaning and resolved inputs stay equal.
It changes X, A_native, its fingerprint and candidate. It needs fresh actual
Root review and, where a predecessor exists, genuine same-key supersession.
Equal K neither authorizes execution nor reopens CONSUMED/UNCERTAIN_CLOSED.
The pure design witness checks these equations using unmodified C builders;
it is not native admission, Root review or the later M03 execution proof.

Native outer material is the ordered pair `('encoding_version','native_v01')`
followed by the existing `action_commit_packet_identity_material_v01` material
from the candidate and actual source Root decision ID/hash. Its domain is
`hedgehog.common_action.native_packet.v01`; keep the existing packet ID prefix
and exact ActionCommitPacketIdentityResultV01 type so transition profiles and
prefix checks remain usable. NEW `build_native_action_packet_identity_v01`
and its contextual validator handle only this material. Common identity
admission calls the old validator for legacy. Old material, packet IDs,
canonical bytes, receipt bytes and replay never get re-encoded or reissued.

Two encodings may share a logical domain only after their validated intent
material and idempotency material equal, including Root/transaction/subjects/
targets/object/consequential values; independent Root approval binds each
packet candidate. Two overlapping instances still need the existing explicit
supersession candidate, accepted Root supersession and reservation transfer.
Do not weaken `authority_transition_requires_g2a3_binding` merely to admit a
second encoding. `CONSUMED` and `UNCERTAIN_CLOSED` remain permanently closed
for that key. If equivalence is not proved, no alias is made: reject an asserted
equivalence and require the owning Root's applicable new-intent/supersession
rule. Equal natural-language descriptions are insufficient. Test legacy then
native AND native then legacy, with coherent IDs and genuine decisions.

## 5. One Lifecycle, Corridor, Invocation and Replay

The current registry and transition tables remain the single state machine.
Native entries widen the exact `root_bound_genesis` union, not lifecycle enums.
Every generic helper reads a validated CommonActionView. Existing public
arguments/returns for legacy are retained. Native serialization is explicitly
versioned; legacy serializers and historical validators remain byte-exact.
No third module is needed for the initial native path other than the six
assigned source/proof paths in section 12.

| Stage | Existing public producer/validator/consumer | Bounded admission change |
| --- | --- | --- |
| Genesis | record_action_packet_genesis_v01; build/validate_action_packet_lifecycle_entry_v01; validate_action_commit_packet_registry_v02 | exact common bound aggregate instead of mandatory Supplier validator; retain duplicate-key and stable-intent checks |
| Activation/transitions | activate_action_packet_lifecycle_v01; append_action_packet_lifecycle_transition_v01; derive_action_packet_lifecycle_state_v01 | consume common view; existing transition registry/rule/evidence and atomic-operation requirements unchanged |
| Eligibility | inspect_action_packet_present_eligibility_v01; validate_action_packet_present_eligibility_inspection_v01 | same validated history, observations/time, retry and disposition; union corridor admission |
| Invalidation/revoke | validate_action_invalidation_evidence_against_packet_v01; record_action_packet_revocation_v01; validate_revocation_root_context_coherence_v01 | same dependency/packet/Root candidate relations via common view, absent sentinels remain absent |
| Supersession | record_action_packet_supersession_v01; validate_supersession_root_context_coherence_v01 | same stable intent/key and independent Root decision; no automatic reauthorization |
| Containment | build_action_packet_effect_firewall_projection_v01; validate_action_packet_effect_firewall_projection_v01 | common profiles in existing _g2a4a_validate_corridor_containment_v01; no synthetic payment slot |
| Attempt | execute_action_packet_mock_fulfillment_v01 | legacy default unchanged; explicit keyword-only admitted invocation extension for native/typed capability results; one preparation/attempt/lifecycle implementation |
| Receipt | observe_action_packet_effect_receipt_v01 | old receipt format unchanged; native result-aware profile verifies actual invocation/result before receipt transition |
| Replay | replay_action_packet_lifecycle_history_v01; validate_action_packet_lifecycle_replay_report_v01 | discriminated encoded genesis, common state reduction, preserved original history; never execute or create permission |

NEW `CommonCorridorStepV01` fields: `step_id:str`, `transaction_id:str`,
`owning_local_root_id:str`, `packet_id:str`, `authorization_candidate_id:str`,
`action_class:str`, `adapter_binding:ActionAdapterBindingProfileV01`,
`subject_scope:ActionSubjectScopeProfileV01`,
`target_scope:ActionTargetScopeProfileV01`,
`effect_parameters:ActionEffectParametersProfileV01`, `issued_at_utc:int`,
`expires_at_utc:int`. NEW `CommonContractFulfillmentCorridorV01` fields:
`corridor_id:str`, `transaction_id:str`, `owning_local_root_id:str`,
`packet_id:str`, `corridor_class:str`, `steps:tuple[CommonCorridorStepV01,...]`.
Corresponding `build_common_corridor_step_v01`,
`build_common_contract_fulfillment_corridor_v01` and `validate_common_corridor_v01`
derive IDs from all fields except their own IDs (domains
`hedgehog.common_action.corridor_step.v01` and `.corridor.v01`). Containment
requires one selected step and exact packet/candidate/adapter/input bindings;
subject/target/time may narrow, never expand. Accepted parameters cannot change.
Old CorridorStepV01/ContractFulfillmentCorridorV01 follow old checks first;
mixed legacy/native step/container pairs reject. No domain recipe in containment.

Public signature/type-admission inventory is the source-bound appendix in the
contract and external proposal evidence. It distinguishes unchanged legacy admission from
generic helpers reached by the common path; all are confined to action_commit_packet_v02.py.
Private helpers named here are maintenance locations, never public construction
authority. No Root/transition/ABI/integrity/time module edit is assigned.

## 6. Admitted Typed Capability and Actual Result

NEW types below are owned by the existing Firewall module. Section6.1 specifies
the deferred nominal action-type access; there is no claim that the existing
action -> Firewall import permits a reverse top-level action import.

| Type | Exact fields | Producer / validator / consumer |
| --- | --- | --- |
| CapabilityFieldV01 | name:str; value_type:TEXT/REFERENCE/DECIMAL/INTEGER/BOOLEAN; required:bool; consequential:bool; minimum:int or canonical decimal str or None; maximum:same; allowed_values:tuple[str or int or bool,...] | trusted descriptor builder; exact type/range/uniqueness checks; bound input/output validation |
| CapabilityDefinitionV01 | definition_id:str; operation_id:str; version:str; effect_kind:PURE or MOCK_CONSEQUENTIAL; business_semantics:CapabilityBusinessSemanticsV01 or None (None iff PURE); input_fields/output_fields:tuple[CapabilityFieldV01,...]; resource_refs:tuple[str,...]; input_validator_ref, output_validator_ref, executor_ref:str; code_sha256s:tuple[(str,str),...]; contract_sha256:str | build/validate_capability_definition_v01; catalogue admission; work item and Root candidate |
| AdmittedCapabilityV01 | definition:CapabilityDefinitionV01; actual input_validator/output_validator/executor callable objects; observed code identities; admission_id:str; catalogue_revision:int | admit_local_capability_v01 by trusted host, no public constructor token; validate_admitted_capability_v01; dispatch |
| BoundCapabilityInvocationV01 | invocation_id:str; admission_id:str; definition_id:str; task_id:str; work_instance_id:str; owning_root_id:str; candidate_id:str or None; packet_id:str or None; execution_attempt_id:str; inputs:tuple[ActionEffectParameterRecordV01,...]; resource_refs:tuple[str,...]; input_validation:actual typed validation evidence | build/validate_bound_capability_invocation_v01; Firewall executable call |
| CapabilityExecutionResultV01 | result_id:str; invocation_id:str; execution_attempt_id:str; admission_id:str; consumed_input_sha256:str; actual_implementation_sha256:str; output:tuple[ActionEffectParameterRecordV01,...]; output_validation:actual designated result; outcome:SUCCEEDED or FAILED_NON_CONSUMING or UNCERTAIN_CLOSED | exact bound executor and validator; lifecycle receipt and actual downstream field resolution |

NEW CapabilityValidationEvidenceV01 has exact fields definition_id:str,
validator_code_sha256:str, subject_sha256:str, invocation_id:str or None,
valid:bool and reason_codes:tuple[str,...]. Input/output validation fields
above use this exact type. Nominal callable protocols are `(definition, inputs)
-> CapabilityValidationEvidenceV01` for input, `(definition, invocation, output)
-> CapabilityValidationEvidenceV01` for output, and `(invocation) ->
tuple[ActionEffectParameterRecordV01,...]` for the admitted executor. The host
constructs CapabilityExecutionResultV01 from the observed call and actual
output-validator evidence; an executor cannot self-author an accepted receipt.
Input evidence precedes invocation ID construction: its invocation_id is None
and its subject hash binds exact inputs. Output evidence requires the actual
completed invocation ID. The evidence validator recomputes code, subject and
invocation binding. These identities are acyclic.

These are proposed public identities, not active schemas. Descriptor IDs are
domain-separated canonical hashes of all non-ID fields. Admission ID also
binds host-observed code/contract bytes, nominal callables and catalogue
revision; a presented hash is compared to trusted loaded bytes/objects. The
host owns the module loader/registration; model text cannot supply or import a
callable. Validators execute on the exact values sent to executor. Reject
duplicate fields, bool-as-int, unrecognized extra field, decimal ambiguity,
wrong domain/range, mismatched resource or changed implementation.

The candidate binds A_native from section4, while L/K bind only business Q.
Legacy issued aggregates cannot gain refs. Moving a legacy logical effect to
typed execution constructs a NEW native successor with the same proved
business material and applicable genuine Root supersession; it is not a
"legacy typed upgrade" and never changes the old aggregate. Native-to-legacy
M03 likewise requires a genuinely constructible frozen legacy candidate and
real review, not a native object relabeled Supplier. Adapter version alone
is not a code-identity check. No domain switch enters the common validator.

NEW `execute_bound_effect_v01(*, firewall, request, decision, current_tick,
invocation, admitted_capability, child_scope_refs, child_expires_at_tick,
time_envelope)` extends the EXISTING exclusive invocation
boundary. It shares authorization/capability consumption with
`authorize_effect_request_v01` and `execute_mock_effect_v01`, preserving old
API and byte behavior. An internal opaque capability is never returned to the
host/model. Revalidate current Root candidate and invocation before starting;
record actual dispatch before executing; validate actual result against inputs,
candidate, code, attempt and output contract. Do not emit a success receipt
for missing/wrong output. Existing `validate_effect_receipt_v01` admits the
exact versioned result-aware receipt profile and its contextual producer;
old exact receipt keys still apply to old receipts. Receipt is evidence only.

The native boundary accepts no caller-selected receipt ID. After actual
invocation and successful designated result validation,
`build_native_effect_receipt_v01` derives artifact_id and payload.receipt_ref
from the completed retained evidence and envelope as specified in
sections6.2-6.3. The existing `execute_mock_effect_v01` signature and
legacy receipt bytes remain unchanged.

Pure computations use NEW host `execute_admitted_pure_work_v01` with the same
catalogue/invocation/input/output checks and no effect capability/permission.
The Firewall refuses PURE-as-effect and unapproved consequential dispatch.
This is real deterministic computation in mocks, not renamed mock PASS.
Unknown dispatch outcome, timeout or exception after start remains
UNCERTAIN_CLOSED. FAILED_NON_CONSUMING needs independent evidence that no
effect invocation started; it is not the default exception conversion.

### 6.1 Exact Value Construction and Module Initialization

ActionEffectParameterRecordV01 stays at its current public action module path,
with the same exact nominal class and canonical fields. No relocation, alias
class, dictionary substitute, duck typing or seventh neutral module is allowed.
Firewall uses postponed annotations (TYPE_CHECKING imports are type-only).
At CALL TIME inside new bound-invocation/result/snapshot public builders and
validators, it performs a local `from hedgehog import action_commit_packet_v02`
and accesses that module's exact public class and builders. No such resolution,
validator call or value construction occurs in a module initializer, decorator,
dataclass default/default_factory or import-time catalogue registration.

Initialization is acyclic: existing ABI/integrity dependencies -> Firewall
type/function definitions without runtime action access -> action definitions
(which import completed Firewall) -> host definitions -> mock definitions.
Importing Firewall first is also safe: its definitions do not enter action;
later its first public call resolves the now fully initialized action module.
Importing action first completes Firewall before action reaches its own value
class definitions. Neither supported path invokes a new builder until both
modules finish. Future acceptance must test both import orders without hooks.

The mock module imports public definitions, and its EXECUTED function body
constructs outputs via existing
`action_commit_packet_v02.build_action_effect_parameter_record_v01` with exact
parameter_name/value_type/value. It never constructs output records at import
time. New Firewall validators check `type(record) is
action_commit_packet_v02.ActionEffectParameterRecordV01` and call the existing
public record validator; nominal action constructors do not call back into new
Firewall builders. This call-time dependency is distinct from the initialization
DAG. Host calls action/Firewall; action calls public snapshot validation;
Firewall calls only pure action value/canonical builders in that inner step.

### 6.2 Strict Native Execution Evidence and Acyclic Identities

All NEW snapshot types here live in Firewall and are frozen. Table field order
is canonical material order. An ID field is excluded only from its OWN defining
material, not from references by later objects. Each serializer validates exact
type/schema then uses existing action CanonicalMaterialV01 and canonical bytes;
each reader rejects absent/extra/duplicate fields and reconstructs exact nominal
types. Canonical parameter records use the existing public record material,
not Python repr or caller-provided hashes. Integers exclude bool. Optional
fields use existing canonical ABSENT in identity material and null in strict
plain serialization. Sets use UTF-8 ordering; code entries are unique by symbol,
field declarations/input/output records by name; other tuples retain their
declared semantic order. Plain ABI payload is a strict projection, not direct
insertion of Python dataclass/callable objects.

| NEW nominal type | Exact ordered fields and role |
| --- | --- |
| CapabilityBusinessInputBindingV01 | input_name:str, source_kind:str (AMOUNT, CURRENCY, QUANTITY, RECORD, SUBJECT_RECORD, TARGET_RECORD, BUSINESS_OBJECT_REF), source_name:str, value_type:str. Scalar/object selectors use source_name equal to their public field name; record selectors use the exact Q record name. SUBJECT_RECORD/TARGET_RECORD are REFERENCE records additionally checked against the corresponding scope. |
| CapabilityBusinessSemanticsV01 | operation_key:str, selected_action_class:str, logical_effect_class:str, logical_effect_namespace:str, business_object_class:str, business_object_namespace:str, input_bindings:tuple[CapabilityBusinessInputBindingV01,...]. Exact exhaustive declaration, section4.2; all consequential inputs must be declared consequential=True. |
| CapabilityCodeSnapshotV01 | public_symbol:str, source_utf8:str, source_sha256:str. Trusted host's exact loaded source bytes decoded losslessly UTF-8, hash recomputed on encoding; admitted callable/code loading provenance must bind these bytes, not just a matching symbol. No historical import. |
| CapabilityAdmissionSnapshotV01 | admission_id:str, definition:CapabilityDefinitionV01, code_sources:tuple[CapabilityCodeSnapshotV01,...], input_contract_ref:str, output_contract_ref:str, implementation_ref:str, catalogue_revision:int, host_instance_ref:str. Immutable copy from actual admitted host entry; no callable or executable capability token. Its input/output contracts include exact field declarations, validator identity and business semantics (input side); implementation includes executor AND both validator sources. |
| NativeExecutionEvidenceV01 | admission:CapabilityAdmissionSnapshotV01, invocation:BoundCapabilityInvocationV01, result:CapabilityExecutionResultV01. Exact context retained INSIDE the receipt; invocation.inputs are the actual dispatched immutable values, result.output the actual returned values. |

The public NEW snapshot producer/validator are
`snapshot_admitted_capability_v01(admitted_capability)` and
`validate_capability_admission_snapshot_v01(value)`; the former first checks
trusted admitted object identity, actual callables and observed source bytes.
The latter checks retained structure/identity only; it cannot newly authorize
execution. CapabilityDefinitionV01.operation_id equals the declared
operation_key for consequential definitions; Pure definitions have no business
semantics. New public `validate_capability_business_binding_v01(definition,
inputs, canonical_projection)` resolves every mapping in section4.2 and checks
selected action/effect/namespace/object/scopes/Q. Invocation and result public
builders/validators call it in addition to the actual designated validators.

Identity equations use existing build_domain_separated_identity_v01. Every
NEW domain below is prefixed `hedgehog.common_action.` and every ID prefix is
the stated leaf plus `:`; these do NOT replace any legacy domain/prefix:

| Leaf (domain suffix `.v01`) / ID prefix leaf | Exact defining material, in order |
| --- | --- |
| capability_input_contract | input_fields, business_semantics, input_validator_ref, input_validator_code_sha256 |
| capability_output_contract | output_fields, output_validator_ref, output_validator_code_sha256 |
| capability_implementation | code_sources (all three public callable source records, sorted by symbol) |
| capability_definition | every CapabilityDefinitionV01 field except definition_id; contract_sha256 is existing public domain-separated SHA256 on ordered input_contract_ref, output_contract_ref with domain hedgehog.common_action.capability_contract.v01, computed BEFORE definition ID |
| capability_admission | definition, code_sources, input_contract_ref, output_contract_ref, implementation_ref, catalogue_revision, host_instance_ref |
| capability_invocation | every BoundCapabilityInvocationV01 field except invocation_id; input_validation.invocation_id is None and candidate/packet/attempt already exist |
| capability_result | every CapabilityExecutionResultV01 field except result_id; output validation binds completed invocation ID, not result_id or receipt |
| native_effect_receipt | all receipt payload fields except receipt_ref, plus ordered envelope material described below; receipt_artifact_id and receipt_ref are BOTH this identity, using existing prefix effect_receipt_v01: with NEW domain hedgehog.common_action.native_effect_receipt.v01 |

NEW AdmittedCapabilityV01 additionally retains host_instance_ref:str; its
admission_id is the snapshot equation above. Input/output validator_code_sha256
comes from the matching code_sources entry; code_sha256s must equal that exact
symbol/hash tuple. Descriptor contract/hash/source consistency and trusted
registration checks precede admission. In validation evidence, subject_sha256
is existing public SHA256 with domain
hedgehog.common_action.capability_value_subject.v01 over canonical input/output
record material. It is not a separate self-referential validation ID. The
result's consumed_input_sha256 equals this invocation-input hash;
actual_implementation_sha256 is the executor source hash from the immutable
admission (all validator code is independently bound there). Both validation
evidence objects retain the actual designated reason tuple/bool; no success
flag can be selected by the executor or generated from authorization alone.

Consequently the DAG is source/contracts/semantics -> definition/admission ->
X -> A_native/fingerprint/candidate -> genuine Root/packet/attempt -> actual
input validation -> invocation -> actual output and output validation -> result
-> receipt -> existing full-receipt content hash -> attempt evidence/context.
The execution_attempt_id is the existing pre-dispatch attempt identity, not
the hash of its later evidence record. No candidate contains its own admission
consumer, no result contains receipt ID, and no receipt contains its own full
content hash or the later attempt-evidence ID.

### 6.3 Exact Receipt Admission and Historical Reconstruction

The ABI KernelArtifactV01 envelope remains EXACTLY the current EvidenceReceipt:
abi_version=v1.0, artifact_type=EvidenceReceipt, schema_version=v1,
source_component=effect_firewall, authority_class=EVIDENCE_ONLY,
lifecycle_state=RECEIPT_RECORDED, actual transaction_id/owner_root_id,
time_envelope, trace_refs=(request_id, root_decision_id, firewall_decision_id),
parent_refs=(root_decision_id,). Existing builders/ABI/transition validators
remain required. The receipt identity's ordered envelope material uses these
fields in ABI field order EXCLUDING artifact_id and payload; the payload is
already included separately above. Existing time-envelope canonical projection
is used. Identity material excludes both own-ID positions, then the resulting
ID is placed in artifact_id and payload.receipt_ref. No reserved envelope key
is introduced into payload. Byte encoding uses existing canonical JSON.

Legacy payload remains exactly its existing nineteen keys and bytes. Native
payload has exactly TWENTY-ONE keys in sorted order:

```text
action_kind
adapter_id
capability_id
effect_handle_exposed
execution_evidence
final_output_created
firewall_decision_id
future_permission_created
mock_execution_status
permission_ref
real_world_effects_count
receipt_evidence_only
receipt_profile
receipt_ref
request_id
root_confirmation_created
root_confirmation_required
root_decision_created
root_decision_id
scope_refs
selected_candidate_id
```

`receipt_profile` is exactly `common_action.execution_result.v01`;
`execution_evidence` is the strict plain projection of NativeExecutionEvidenceV01
with exactly admission/invocation/result and the recursive field sets above.
All original nineteen fields retain their exact public types and contextual
meaning. They are obtained from the actual request/decision/capability/observed
completion, never copied as caller verdicts. The terminal mock status may be
success ONLY after genuine dispatched result and successful designated output
validation. Existing zero/evidence-only/no-new-authority conditions still hold.
NEW public `build_native_effect_receipt_v01` takes the actual Firewall/request/
decision/time and exact execution evidence; `validate_native_effect_receipt_v01`
checks that context and every nested identity/binding and delegates unchanged
ABI/transition/issuer-origin checks. Both are in Firewall, not a new module.

Discrimination requires BOTH payload schema and retained encoded invocation
context: SUPPLIER_V02 legacy mock/no typed invocation -> old exact nineteen
keys with no receipt_profile; NATIVE_V01 typed invocation -> exact new profile
and twenty-one keys. Absent/wrong version on native, new keys on legacy,
unknown keys, malformed nested nominal values, or mixed lineage all reject.
Removing both new keys cannot downgrade native history to legacy. No attempt
context infers its encoding just from an untrusted receipt's discriminator.

Actual dispatch retains exact invocation and actual returned output; the host
runs the designated output validator on that invocation/output and constructs
the result. Only then can native receipt construction finish and consume the
existing capability/lifecycle slot. The receipt itself retains the complete
immutable execution evidence in
`_ActionPacketFulfillmentAttemptContextV01.receipt: KernelArtifactV01 | None`.
The existing request/decision/projection/attempt/corridor/dependency/time fields
provide independent external bindings; no companion field or hidden mutable
table is required. `observe_action_packet_effect_receipt_v01` compares the
submitted receipt to that retained exact payload, actual candidate/packet/
attempt/Root/request/decision/input/admission and existing disposition before
the usual receipt transition. Existing receipt hashing covers the entire
native payload and existing ledger/seal provenance remains mandatory.

The legacy `_expected_action_packet_effect_receipt_plain_v01` and
`_rebuild_exact_action_packet_effect_receipt_v01` keep their old behavior for
legacy only. They CANNOT synthesize native business output from authorization.
The native branch requires the retained receipt, parses the exact schema,
rebuilds all stored materials/IDs, checks input/output contract SHAPE and
original validation-evidence bindings and checks it against retained attempt
context and immutable ledger history. Missing native payload is a failure,
not a request to manufacture expected output. Shared reduction/dispositions,
transition registry and cryptographic provenance are unchanged.

Historical replay performs no executor, input/output-validator CODE execution,
DRS package import or current catalogue lookup. It recomputes stored hashes,
schemas, lineage, envelope/context bindings and transition reductions only.
Actual code source snapshots, output and original validation reasons are
execution evidence, not a newly observed successful computation. A coherently
rewritten entire history is not authenticated merely by self-consistent hashes:
existing sealed/origin provenance must still agree. No new signature/encryption
system or promise of arbitrary historical algorithm correctness is introduced.
Uncertain/missing/invalid output never produces a success receipt; the existing
appropriate non-consuming or UNCERTAIN_CLOSED disposition applies, with the
same independently evidenced non-start requirement and no free retry.

Later M01/M03/M09/M10 controls MUST first pass freshly rebuilt equivalent
native receipt/context neighbors. Change actual output with recomputed nested
hashes and obtain the real output-validator result; check against retained
observed execution, not a stale hash. Independently change candidate, code/
implementation, and attempt with coherent local IDs but wrong retained external
binding; reject the named mismatch. Remove retained execution_evidence, mix
legacy/native versions, add unknown nested keys, or supply today's catalogue
for old history; reject at the corresponding boundary. Also retain successful
old replay and actual code-only same-business native successor controls.
These are NOT_IMPLEMENTED runtime acceptance obligations, not governance tests
or results of the pure identity witness.

## 7. Authoritative Current State and Linearization

NEW `RootWorkExecutionHostV01` in `hedgehog/work_execution_host_v01.py` is one
in-process serialized owner per Root. It owns current ActionCommitPacketRegistryV02,
dependency observations, admitted catalogue, time bridge, and monotone
`state_revision:int`. A request supplies task/packet/attempt identities and
expected revision, NOT a preferred registry, observation snapshot or catalogue.
Historical values can be requested for replay only. The host reads current
trusted sources and checks exact Root, revision, inputs and time itself.

Public host operations: `build_root_work_execution_host_v01`,
`inspect_current_action_v01`, `accept_current_revocation_v01`,
`dispatch_current_action_v01`, `execute_admitted_pure_work_v01`.
The first installs trusted initial state after public validation. Each other
operation accepts the host plus IDs/context, never accepts a caller's live
registry replacement. Updates return immutable evidence plus the new revision.

Serialized order is: check expected revision -> refresh observations ->
validate Root/currentness -> reserve existing logical key -> record STARTED
attempt -> actual invocation -> validate result -> update consumption/history.
The STARTED record, durable only within this in-process host, is the invocation
linearization point. `accept_current_revocation_v01` validates its genuine
RevocationCandidate/Root projection and updates current registry/revision in
the same ordering. A revoke accepted before STARTED blocks invocation even
with valid TTL. A distinct unchanged positive control at the same timestamp
must still execute. Stale writers reject before any operation.

A post-start revoke cannot undo a past effect or promise to stop ongoing TV
playback. Stopping is a new scoped action. Four TVs are four single-effect
packet instances with actual targets/local Root decisions. A fifth target,
cross-Root candidate or expanded post-Root scope rejects. There is no batch
atomicity, distributed crash recovery, physical rollback or production guarantee.
Host reentry/concurrent writers cannot interleave the above critical section.
Uncertain interruption closes the logical key before another dispatch.

## 8. One Bounded Typed Program Handler

NEW public module `hedgehog/kernel/work_composition_v01.py` owns typed program
validation/materialization and reduction; the host owns admitted execution.
No retired PlanGraph/Needle executor is revived. No scenario-name dispatch,
domain recipe, eval, arbitrary Python expression or free model-supplied code.

| Proposed exact carrier | Fields |
| --- | --- |
| WorkLiteralV01 | value:ActionEffectParameterRecordV01 |
| WorkOutputBindingV01 | predecessor_work_id:str; output_field:str; expected_type:str |
| WorkInputBindingV01 | input_field:str; source:WorkLiteralV01 or WorkOutputBindingV01 |
| WorkBudgetV01 | max_items:int; max_children:int; max_model_calls:int; max_compute_units:int; max_revisions:int |
| WorkItemV01 | work_id:str; definition_id:str; owning_root_id:str; inputs:tuple[WorkInputBindingV01,...]; resource_refs:tuple[str,...]; depends_on:tuple[str,...]; guard:WorkOutputBindingV01 or None; review_obligation_id:str or None |
| WorkProgramCandidateV01 | task_id:str; revision_id:str; previous_revision_id:str or None; intent_ref:str; bsep_ref:str; semantic_proposal_ref:str; catalogue_revision:int; budget:WorkBudgetV01; items:tuple[WorkItemV01,...]; trigger_evidence_refs:tuple[str,...] |
| MaterializedWorkProgramV01 | candidate:WorkProgramCandidateV01; topology_artifact:KernelArtifactV01; ordered_work_ids:tuple[str,...]; source_bindings:tuple[CausalConsumptionRefV01,...] |
| WorkItemResultV01 | task_id/revision_id/work_id:str; status:str; invocation:BoundCapabilityInvocationV01 or None; result:CapabilityExecutionResultV01 or None; consumed_fields:tuple[CausalConsumptionRefV01,...]; reasons:tuple[str,...] |

`build_work_program_candidate_v01` canonicalizes and hashes all actual inputs;
`validate_work_program_candidate_v01` validates exact typed fields, uniqueness,
finite DAG/edges, contracts, budgets and bounded BSEP/semantic context.
`materialize_work_program_v01` creates runtime-owned deterministic topological
order (lexical work-ID tie break), never a Root decision.
`advance_work_program_v01` consumes supplied verified predecessor results,
catalogue/current host state and mandatory review results. It returns actual
ready dispatches/results, never recollects a replacement scenario.
`validate_work_program_result_v01` binds every result and field use to source.

Candidate ABI is SemanticArchitectProposal/ADVISORY/PROPOSED; materialized
topology is RuntimeExecutionTopology/NON_AUTHORITY/VALIDATED; work results are
ResultProposal/EVIDENCE_ONLY using existing compatible lifecycle values.
Build/validate them with public ABI functions, plus a strict new payload schema
when implementation exists. Payload cannot duplicate reserved envelope fields.
New work statuses live inside the typed payload, not old ABI enums.

Execution states: PENDING -> BLOCKED_REQUIRED_OUTPUT / BLOCKED_INVALID_INPUT /
NEEDS_CAPABILITY / SKIPPED_GUARD_FALSE / READY. READY -> RUNNING -> COMPLETED /
FAILED_NON_CONSUMING / UNCERTAIN_CLOSED. Only an actual validated result yields
COMPLETED. A strict BOOLEAN guard false is SKIPPED_GUARD_FALSE, with no output
or effect receipt; missing/nonboolean guard blocks, never silently false.
An absent mandatory predecessor blocks joins and effects; optionality must be
declared in the definition. Fanout has finite policy-limited instances, not
unbounded recursion. A blocked D report is not completed work.

At consumption, resolve predecessor by ID, validate source version and actual
output, read the named field, validate its type, and pass exactly that value
into the bound invocation. Derive CausalConsumptionRefV01 using its ACTUAL
fields: producer_actor_id, source_artifact_id, output_field,
consumer_component, downstream_artifact_id, decision_effect, disposition,
reason_code and trace_refs. These refs document executed use, not replace it.
Count/hash checks follow actual input/output binding, not the reverse.

Two accepted different programs through this same handler must change actual
operations and predecessor field reads (for example property->transform->mock
display versus observation->boolean condition->mock alarm). After common
code freeze, held-out valid input, adapter definition and dependency structure
must pass without changing common predicates or expected answers.

## 9. Required D Review and C/E/F Consumers

NEW `WorkReviewObligationV01` carries task_id, revision_id, work_id, owning_root_id,
business/BSEP/semantic source identities, actual C source/router input,
route-eligibility artifact and actual Root route review. Its obligation ID is
derived from these sources, not assigned by a model. A control result carries
the original FractalRuntimeSourceContextV02 and FractalRuntimeExecutionBundleV02.
`validate_work_review_binding_v01` checks public C/Root source consistency,
`validate_runtime_topology_source_binding_against_g2c_v02`,
`validate_runtime_execution_topology_against_sources_v02`,
`validate_fractal_runtime_execution_bundle_v02` and the exact completed upward
return for this source/task/work. No unrelated valid bundle can satisfy it.

Required review work remains blocked without that binding. The consumer reads
actual completion, return obligations and parent-transition/result provenance
to decide readiness; U0's single/recursive control difference is preserved.
No obligation is discharged by a report hash alone or by caller verdict.
Unrequired informational short paths do not get a ceremonial D run. Business
data flows separately from admitted capabilities. Before a consequential
dispatch, a separate actual owning-Root action decision binds its final typed
inputs; route permission alone is not effect permission. D/ABI stay unchanged.

| Current source location | Exact required later change | Laws retained |
| --- | --- | --- |
| execution_mode_router_v01.py: ExecutionModeSourceContextV01; build_execution_mode_source_context_v01; _source_context_errors | widen g2a_corridor/g2a_corridor_step annotations and nominal admission to the exact new validated pair; legacy pair unchanged | all-or-none source geometry and exact observation/time/transition types |
| same module: _validated_g2a_binding; build_execution_mode_g2a_binding_v01 | contextual inspection still rerun; read common canonical transaction/Root and original inspection identity fields | routing algorithm, request/domain/currentness, no router authority unchanged |
| continuous_delta_runtime_v01.py: ContinuousDeltaSourceContextV01; build_continuous_delta_source_context_v01; _source_context_reason_v01 | exact g2a_packet union and common validator/view in place of Supplier-only admission | candidate equality, mandatory Root dependency acceptance, invalidation-against-packet, time/root/transaction and topology-source relations unchanged |
| same E module: _source_context_shape_valid_v01 | retain exact source type; packet-specific validation occurs in source reason function | no broad dict admission or affected-set algorithm change |
| F runner and all24 focused tests | NO BYTE CHANGE | accepted 181/235 legacy composition; later fresh runtime regression required on modified dependencies |

C/E source carriers are runtime-only. Their current schemas do not require a
change merely for this nominal admission. D, C/E schemas, Root, transition,
ABI, time, integrity/replay, B/DRS and old focused runtime tests remain protected.
If a real serialized incompatibility is found, stop at the exact field/consumer
and propose the minimum scoped amendment; do not add a tenth U1-proposal path.
U0 does not by itself satisfy future M15 integration acceptance.

## 10. U2 Same-Task Continuation

U2 uses the same task_id and handler, not a second prewritten initial program.
At most two additional revisions in the first proof. Each revision_id hashes
task_id, previous revision, actual trigger evidence, remaining cumulative budget
and proposed items. Trigger is a real intermediate result or capability loss.
Completed immutable history is retained and referenced, never replayed as a new
effect. Reuse of its output validates original provenance and current policy.

`revise_work_program_v01` validates monotone revision linkage, bounded diff,
remaining compute/model/child/revision budgets and all affected current action
permissions. No revision replenishes budgets or expands scope. NEEDS_CAPABILITY
can trigger bounded replanning/admission; exhaustion explicitly terminates
EXHAUSTED with evidence. Root policy/budget can authorize bounded internal work
without a human click for each operation; proposals cannot authorize themselves.
Different initial U1 programs do not prove this continuation requirement.

## 11. U3 Missing Pure Code, Admission and Local DRS

U3 remains mandatory, unimplemented. A task-derived need must lack an admitted
implementation in catalogue/local DRS before cold start. Freeze common code and
the independent oracle before candidate generation/discovery. No hidden installed
function, human repair, test-chosen code hash or self-test PASS can replace this.
Controlled deterministic proposals and separately authorized model responses
are labeled separately; no provider/budget authorization is granted here.

Proposed substrate is Wasmtime Python binding in a short-lived worker, not an
installed/version-tested dependency in U1. Exact platform/version pin and
configuration validation precede U3. Raw WAT/Wasm <=16KiB, imports=[], no WASI
or host functions, integer-only independently checked feature profile, exactly
`transform(i32)->i32`, input/output domain0..255. No memory/table instances;
Store limits memories=0,tables=0,table_elements=0,memory_size=0,instances=1.
Fuel <=100000 per computation; supervisor wall budget initially30 seconds per
candidate including compilation, validation, trials and instantiation/start.
Fresh instance for each oracle input and admitted call; compiled immutable
module reuse is allowed, mutable guest state is not. Never deserialize model
or DRS-supplied native compiled cache. No engine trial is performed now.

Independent oracle covers all256 inputs plus out-of-domain rejection; it is
fixed from the need, not fitted to candidate outputs. Profile negatives include
imports, export/type mismatch, memory/table, fuel exhaustion, timeout, trap,
wrong output, changed bytes/contract version and foreign admission. Pair with
genuine positive. This proves one finite domain, not arbitrary software
correctness. No imports means no granted guest filesystem/network/system APIs;
a Python process alone is not a sandbox. Wasm Store limits are not hard whole
host/JIT RSS guarantees; engine/host vulnerabilities remain trust assumptions.

NEW later modules: capability_admission_v01.py, wasm_pure_worker_v01.py,
capability_memory_binding_v01.py. Admission binds exact bytes, contract,
resource profile, oracle evidence and actual engine configuration to the same
trusted catalogue. The same task then consumes the actual transform output,
for example as a permitted mock display parameter, through the same handler.

Need -> public `local_drs_resolver.resolve_semantic_candidates` query by
domain/semantic_terms/content_filters -> pointer/meaning/provenance/version/
hash checks -> public temporal eligibility/ranking and bounded Root-reviewed
descent -> SAME independent admission -> catalogue -> resume. Host supplies
actual local package bytes; no network federation is implied. Generated and
retrieved code are equally untrusted. Store source, contract/profile, provenance,
validated outcome and permitted memory records using existing public semantic
address/meaning/pointer and DRS functions. ReuseCertificate's informational
shortcut is not code installation or action permission.

A fresh warm task with the same suitable need must perform real need-based
search without a supplied function ID/hash shortcut and observe zero generator
calls. Recheck freshness/version/admission and fresh action permissions. Measure
generator attempts, all model calls, admission work, DRS bytes, compute/fuel and
elapsed separately cold/warm; no unmeasured speedup claim. Three future full
demos and remote DRS federation remain outside this work.

## 12. Exact Implementation Order and Protected Scope

First subsequent vertical slice is exactly six paths, under later explicit
authorization, not this proposal:

1. MODIFY hedgehog/action_commit_packet_v02.py.
2. MODIFY hedgehog/kernel/effect_firewall_v01.py.
3. ADD hedgehog/work_execution_host_v01.py.
4. ADD demo/work_composition_mock_capabilities_v01.py.
5. ADD demo/run_action_packet_portability_v01.py.
6. ADD tests/test_action_packet_portability_v01.py.

It must complete one genuine native nonpayment Root-bound operation through
current registry, actual typed dispatch/result, consumption/receipt/replay.
Immediately test legacy/native duplicate prevention both orders, same-time
revocation/positive, coherent parameter/target change, stale state and uncertain
outcome. No builder-only completion. The host owns catalogue/current state/
dispatch at that point, NOT semantic composition. New shared invocation types
live in Firewall; action imports those public types, host imports action and
Firewall. Mocks construct exact public action value types only in executed
bodies. Deferred Firewall access and the initialization/call-time distinction
are fixed in section6.1, within six paths and without a neutral type module.

Then complete U1 with C/E nominal admission and the other three paths:
ADD hedgehog/kernel/work_composition_v01.py;
ADD schemas/work_composition_v01.schema.json;
ADD tests/test_work_composition_v01.py. Use the SAME invocation/current host.
The old eleven runtime/host/proof paths are all retained. Actual new schema/seams
are registered only when implementations exist, via later approved metadata
scope. The previous29-path ledger is a multi-phase plan, not current permission.
Six later acceptance/status/claim/checkpoint paths wait for factual acceptance.

U2 stays within that later composition/host/schema/test scope. U3 additionally
proposes capability_admission_v01.py, wasm_pure_worker_v01.py,
capability_memory_binding_v01.py, schemas/capability_admission_v01.schema.json,
tests/test_capability_admission_v01.py,
tests/test_work_continuation_and_reuse_v01.py,
demo/run_capability_cold_start_reuse_v01.py and conditional pyproject.toml
dependency pin. These eight are not current write or install permission.

All unlisted current paths are frozen, including action_commit_packet.py,
Root/transition/ABI/integrity/MultiRoot/signer/semantic_work/__init__, D and its
schema, C/E schemas, B/DRS/time, old domains/tests/Gate runners, F24, accepted
checkpoints/audits, retired families and completion_manifest.json. Stop on an
actual incompatibility and name the precise minimum scope amendment. No law
weakening, duplicated payment/nonpayment state machine or scenario special case.

## 13. Assigned Acceptance Matrix (No Runtime PASS Yet)

All negatives use coherent freshly reconstructed controls and real public
validator results. A stale identity rejection is metadata coverage, not proof
of an unrelated semantic law. Record actual inputs, outputs, consumed fields,
callable/code identity and first rejection boundary. No fixed test-count quota.

| ID | Required executable evidence and paired control | Scope |
| --- | --- | --- |
| M01 | Legacy bytes/IDs/receipts/replay equal frozen baseline; reject altered history | U1 compatibility |
| M02 | Native payment/playback/other nonpayment actually consume typed parameters and produce bound outputs | U1 common lifecycle |
| M03 | Legacy then native AND native then legacy same proven intent cannot execute twice | shared consumption |
| M04 | One and four instances execute; coherent fifth target/scope expansion rejects | target parameterization, not novel program |
| M05 | Independent Roots accept locally; cross-fed candidate/Root/permission rejects | no SuperRoot |
| M06 | Rebuilt valid changed parameters/target/adapter rejected by accepted semantics, not stale hash | Root/executor binding |
| M07 | Accepted pre-start revoke blocks at valid TTL; unchanged positive at same time executes; history replay remains valid | ordering |
| M08 | Task-supplied old snapshot/stale revision cannot become live state; explicit historical inspection allowed | current host |
| M09 | Repeated/uncertain attempts cannot revive consumption; proven non-start control distinguished | no free retry |
| M10 | Actual admission checks code/callable/contract; wrong/missing result or changed implementation has no success | typed execution |
| M11 | Native nonpayment E dependency change causes actual minimal/complete recompute and invalidation; unaffected bytes persist | later C/E integration |
| M12 | Two different programs execute different operations and actual field bindings in one handler | composition, not labels |
| M13 | Mandatory producer removal/replacement blocks downstream/effect despite plausible final supplied answer | causal necessity |
| M14 | Cycle/type/unknown capability/budget fail; false guard is skipped and missing/nonboolean blocks | finite language |
| M15 | Required D source-bound completion changes consumer readiness; missing/wrong-context/blocked D rejects | U0 is supporting CONTROL evidence only |
| M16 | Freeze common code; held-out structure/input/adapter runs via unchanged predicates with actual new work | portability |
| M17 | Controlled versus authorized live proposal provenance, raw/canonical influence on actual operations | no fabricated model autonomy |
| M18 | Frozen focused meanings and F24 harness preserved; fresh modified-source regression and exact governance | no old PASS carryover |
| R01 | Real intermediate/capability-loss trigger yields same-task bounded revision | U2 continuation |
| R02 | Cumulative children/model/compute/revision budgets never reset; explicit exhaustion | U2 budget |
| R03 | Completed effects/history remain immutable; resume needs current permission | U2 currentness |
| R04 | Cold catalogue/DRS absence proved before task-derived missing need candidate | U3 necessity |
| R05 | Actual exact-code/resource/finite-domain admission, no hidden implementation/self-PASS/human repair | U3 admission |
| R06 | Same task consumes actual new implementation output through same handler | U3 causal use |
| R07 | Need-based local search, retrieve and SAME admission, no supplied hash shortcut | U3 memory |
| R08 | Fresh warm task observes zero generator calls; policy/freshness revalidated | U3 reuse |
| R09 | Changed/stale/wrong DRS package fails with coherent positive neighbor | U3 refusal |
| R10 | Deterministic fixtures and actual authorized live model evidence separately attributed | all claims |

## 14. Exact Contract-Only Successor

The nine-path proposal adds this document and modifies only Architecture Lock,
Authority Index, Successor Manifest, AGENTS, README, active guard and its two
governance test files. Eight C sources change; 903 existing paths are frozen.
No runtime/schema/seam registration or acceptance checkpoint is created.

| State | Independently required Git facts | Meaning |
| --- | --- | --- |
| P0 | original clean C/origin C, original sources | accepted closed Gate2 only |
| P1u | C/origin C, exactly eight unstaged M + this untracked A, index equals C | U1_CONTRACT_CANDIDATE_UNSTAGED |
| P1s | same exact nine entirely staged, index equals worktree, no other edits | U1_CONTRACT_CANDIDATE_STAGED, not owner acceptance |
| P2 | one clean single-parent exact9 contract child, parent C, origin C | U1_CONTRACT_COMMITTED, runtime unimplemented |
| P3 | same child clean, origin equals child | same contract-only state |

Only this immediate successor is recognized. Fixed C/tree provenance, exact
add/modify set, frozen-unlisted blobs, exact document identity and strict
control field/classification/entrypoint shapes are checked independently.
No file embeds its own future hash. Final nine hashes live in the external
proposal receipt; mutable guard/test code is not treated as a signed security
boundary. Owner review still accepts exact returned bytes, not any arbitrary
code with similar path names. Partial staging, staged/worktree mismatch,
wrong modes/types/flags, foreign origin, extra generation/merge/path, phantom
active schema/seam, runtime self-claim and unproved future phase reject.

Keep historical C closure/source checks active for historical C; the new
scoped successor checks C provenance and every unlisted byte, not a broad
descendant exception. Old945 authority and33 release node IDs and meanings
remain; new governance nodes are counted separately. Future implementation,
acceptance and independent closure require actual source-bound runs and a
separate owner boundary; neither document text nor U0 can self-award them.

## 15. Exact C Admission Maintenance Inventory

Static AST inspection of action_commit_packet_v02.py at C finds the following
31 top-level functions directly naming the two Supplier projection types or
their public validators. This is the actual selected census, not a requirement
to reproduce an earlier approximate count of35. Line numbers refer to C.
Listed private functions are maintenance locations, never callable authority
for a domain/host. Public caller contracts in sections3-9 consume the result.

| C line / function | Later treatment and reason |
| --- | --- |
| 948 _cached_root_bound_validation_v01 | Generalize exact admission cache key to include encoding and actual object/context; never use a Supplier-only validator on native |
| 6048 _build_supplier_action_commit_packet_canonical_projection_unchecked_v01 | Preserve legacy construction and byte identity; native uses its independent aggregate builder, not a fake source_packet |
| 6299 build_supplier_action_commit_packet_canonical_projection_v01 | Preserve public legacy input/return and validation |
| 6362 _validate_g2a1a_cross_profile_coherence_impl_v01 | Preserve exact legacy B equality; extract other common checks, native separately reconstructs B/L/K/X/A_native and candidate as section4, never bypasses equality |
| 6730 _validate_supplier_action_commit_packet_canonical_projection_impl_v01 | Preserve exact legacy admission first; do not widen to arbitrary objects |
| 7037 validate_supplier_action_commit_packet_canonical_projection_v01 | Preserve public Supplier-only meaning; common public validator dispatches explicitly |
| 7432 _validate_revocation_candidate_against_packet_core_v01 | Common bound view, same source authorization/packet/Root/idempotency/reason relations |
| 7489 _validate_supersession_candidate_against_packets_core_v01 | Common views for each encoding; same predecessor/successor/intent/key proof |
| 8186 _build_expected_accepted_revocation_binding_v01 | Union input/view; retain actual Root candidate and authorization hash bindings |
| 8387 _build_expected_accepted_supersession_binding_v01 | Union input/view; retain exact independent Root supersession binding |
| 8523 _validate_mandatory_dependency_local_root_acceptance_core_v01 | Common packet admission; exact candidate fingerprint and accepting local Root remain mandatory |
| 9173 _validate_action_packet_invalidation_context_core_v01 | Common view; preserve observation, revocation and supersession context checks and absence rules |
| 9513 _validate_supplier_root_context_coherence_impl_v01 | Legacy entry remains exact; extract common candidate/permission/policy/time/dependency checks for native counterpart |
| 9681 _build_supplier_root_bound_packet_v01 | Preserve legacy packet construction only; native has no legacy packet field |
| 9800 _validate_supplier_root_bound_projection_impl_v01 | Preserve legacy encoded packet checks; shared generic context extracted, never removed |
| 9922 validate_supplier_root_bound_action_commit_packet_v02_projection_v01 | Preserve public Supplier exact type; common admission dispatches to it for legacy |
| 9931 build_supplier_root_bound_action_commit_packet_v02_projection_v01 | Preserve public legacy API/return/material |
| 11210 _validate_action_packet_lifecycle_entry_core_v01 | Admit the exact two bound encodings; same single registry entry rules |
| 11284 _validate_action_packet_transition_history_core_v01 | Use shared view and encoding-aware identity; unchanged sequence/temporal/authority law |
| 11646 _packet_local_disposition_history_v01 | Union annotation/view; existing logical-key history and ownership unchanged |
| 11694 _disposition_before_transition_events_v01 | Union annotation/view; same pretransition state reconstruction |
| 11713 _validate_contextual_invalidation_transition_v01 | Common context; no new transition codes or bypass of owning Root evidence |
| 12156 _action_packet_transition_temporal_reason_v01 | Common temporal profile; exact existing time bridge/interval laws |
| 12812 _same_key_entries_are_bound_successors_v01 | Common admission; require actual existing supersession, never alias encodings automatically |
| 13832 record_action_packet_genesis_v01 | Common exact bound admission; retain consumed/uncertain permanent closure and duplicate genesis checks |
| 15067 _g2a4a_current_dependency_observation_ids_v01 | Common dependencies; observation freshness/identity/Root remains contextual |
| 15177 _g2a4a_root_scope_refs_v01 | Generic subject/target profiles; no selection by domain name |
| 15201 _g2a4a_validate_corridor_containment_v01 | Legacy checks first for legacy pair, native exact pair without source_packet reconstruction, shared normalized containment |
| 15289 _g2a4a_logical_ticks_v01 | Common temporal profile; preserve lossless public roundtrip and half-open expiry |
| 15326 _build_action_packet_effect_firewall_projection_core_v01 | Common view; exact current registry pass, packet/candidate/Root/permission/adapter/time/observation inputs |
| 15544 _build_action_packet_effect_projection_from_historical_view_v01 | Versioned input admission; historical evidence only, no current permission or dispatch |

Indirect public consumers named in section5 and their registry serializers also
receive the explicit encoded union through these helpers. ActionPacketLifecycleEntryV01
and the existing internal historical/attempt contexts keep their fields; only
their packet/corridor annotations and exact serializers need union admission.
Do not widen protected ABI carrier types or rewrite the transition registry.

Native CommonActionView additionally carries canonical_permission_ref,
selected_canonical_action and the actual temporal_evaluation above. Its Root
coherence checks exact permission_state.permission_ref, policy_state.policy_id
against authority fingerprint, temporal_state.time_envelope_ref against temporal
fingerprint, actual temporal booleans, mandatory provided/required evidence
and absent prior Root state just as the current action authorization context.
Current revocation/supersession context validators retain their separate roles.
Native mock operation and adapter identities must already use the public
`mock_action:`/`mock_adapter:` namespaces; effect_class is not substituted for
action_kind. Existing legacy vocabulary projection stays unchanged.

Firewall direct changes are build/validate_bound_capability_invocation_v01 and
execute_bound_effect_v01 as new public surfaces, with shared existing
_authorization_block_reason, _capability_valid and consumption state behind
authorize_effect_request_v01/execute_mock_effect_v01. A result-aware receipt
profile adds exact keys only for its explicit version; _effect_receipt_errors,
validate_effect_receipt_v01 and action attempt/replay contexts must discriminate
versions. Existing legacy required keys, issuer origin, capability ownership,
one-receipt/no-duplicate checks and output projection stay exact. PURE does not
obtain an EffectCapabilityV01. No hidden second Firewall/lifecycle is allowed.


## Draft U1 Retained-Work Integration Boundary

V04_IMPLEMENTATION_CONTRACT_ACCEPTANCE_PENDING. The exact retained-work profile proposed
in the G2-D addendum separates historical validated output from new current
consumption; the G2-E addendum defines its explicit preservation obligation.

U1 SHALL keep D as CONTROL over the actual reviewed task/work/Root/definition,
input/dependency/guard/resource/budget and business/BSEP/semantic source
commitment. A generic prior D review SHALL NOT authorize changed work merely
because an outer candidate or obligation is rebuilt. Reused completion SHALL
still require its mandatory review and current host history.

The first retained-work integration SHALL use a genuine source-bound legacy D
CONTROL review; it SHALL NOT relax work review validation to accept a retained
bundle by duck typing. Retained E output is evidence, not authority. Separate
current consequential Root authorization, lifecycle, actual input validation,
exclusive Firewall/corridor and present eligibility remain mandatory.

M11 SHALL remain BLOCKED until actual native packet-dependency selective
completion, complete/minimal affected work, preserved unaffected business
bytes, current eligibility refusal and applied Root-bound invalidation have
all been demonstrated. Ordinary-source last-child success is insufficient.
The original E-pair test meaning SHALL be retained when its construction is
adapted to the current exact-work review source. Historical E5 test-state
migration and full E/F acceptance SHALL be completed on one final admitted
source set. U2/U3 and final integration remain required before Testflix;
neither this amendment nor a design witness awards their acceptance.

V04 binding amendment: apply the explicit V04 review amendment in the D
addendum. Retention preserves actual historical CONTROL outputs, not a
counterfactual business-output equivalence. Current source grammar is nonempty;
closed overlays, actual current-prefix admission and preserved outer ABI
identities are mandatory. Candidate implementation and governance admission
remain unaccepted until the required actual evidence is reviewed.


## V05 Retained PLAN and Execution Amendment

This amendment supersedes the exact-eight-field review record and any
conflicting new-draft wording above. It does not change the preceding accepted
legacy contracts. These are candidate obligations, not an admission or test
result. The external V05 receipt identifies the source actually tested.

### Actual Retained Work

The supported behavior is the source-reviewed deterministic D CONTROL local
observation. Its definition consists of the complete typed topology nodes,
edges, assignments, policy, scope and input records. No invented executable,
resource-manifest or business-output field is introduced. A historical
`d3local:output:*` value may be a string in an original queue's
`observed_output_refs`, not an independent artifact. It retains its original
input and scheduling provenance; it is not claimed equal to a hypothetical
new execution's identifier.

Admission validates a nonempty ordinary causal inventory and complete internal
historical leaf closure. An empty OBSERVED_WORK_INPUT subset proves nothing.
External dependencies use a closed map of actual old/current source objects
and validated observed source-pair bindings, including presence and changed
empty values. A changed counterpart may not be omitted or replaced by old
material on both sides. Typed node, edge, assignment and policy comparisons
supplement artifact field bindings; artifact IDs alone do not prove them.
Node identity is paired with cell identity. Current time applicability comes
from the supplied routing snapshot, TTL, intervals and source envelopes.
Internal historical input/budget/dependency identities remain historical;
actual externally consumed semantic budget values are not exempt from checks.

### Exact PLAN Review

`FractalRetainedPlanReviewV01` has exactly these ten fields in order, and no ID:

```text
root_kernel: RootDecisionKernelV01
root_input: RootDecisionInputV01
root_result: RootDecisionResultV01
proposed_artifact: KernelArtifactV01
decision_artifact: KernelArtifactV01
accepted_artifact: KernelArtifactV01
review_transition: TransitionDecisionV01
accept_transition: TransitionDecisionV01
transition_registry: TransitionRegistryV01
ordered_plan_ancestor_artifacts: tuple[KernelArtifactV01, ...]
```

The transitions are actual E `g2e_t04_plan_root_review` and
`g2e_t05_plan_root_accept`, validated with their actual source/target objects.
The internal Root transition is not t04. E constructs the family before D
from current source/history and the actual E prelude. D does not import E or
collect a future E outcome. No future admission, consumption or result belongs
in the PLAN ancestry.

The three PLAN artifacts seed transitive parent traversal. The ancestor tuple
contains exactly the reachable family minus those seeds. Order the entire
family by repeatedly emitting the complete lexicographically sorted ready
batch, then filter the seeds. Unknown parents, cycles, self-edges, duplicate
tuple IDs, conflicting bodies, unreachable additions and wrong order refuse.
Overlapping builder inputs coalesce only after full public canonical-byte
equality. The family enters ABI provenance, not current event inventories.

Public validation binds the actual Root ACCEPT to one complete retained claim,
candidate, request, transaction, Root, scope and topology. Proposed/accepted
PLAN payloads equal the claim projection omitting only `trace_refs`. Proposed
trace is ordered-unique claim trace followed by delta, affected-set,
invalidation, baseline route and topology IDs. The five ordered proposed
parents remain invalidation, affected set, graph, baseline route and historical
D report. The Root decision artifact is reconstructed from the complete public
Root result with only top-level transaction moved to the envelope; exact
existing E domain, parents, traces and time apply. Accepted PLAN has the two
actual PLAN/decision parents and five trace entries including actual t04/t05.
Parent closure does not replace E's independent affectedness or D's retention
semantics. Neither the family nor a valid hash creates action authority.

### Public Entry and Consumer Closure

`run_continuous_delta_runtime_v01` appends only the optional keyword
`retained_profile: str | None = None`. Omission preserves legacy behavior.
Only exact `fractal_retained_work_v01` requests the new representation; other
types/values refuse. E derives and source-validates the base plan independently,
then converts it before the actual Root review. Public execute dispatches by
the exact nominal plan, with no second selector. Inapplicable retention refuses
without fabricating a strict affected subset or silently changing profile.

The exact-thirty-field prefix and exact-thirty-four-field retained bundle
already contain the ten-field review. The legacy twenty-eight-field bundle
remains a distinct nominal branch. Admission requires the actual current
prefix and running-slot/live-budget membership. Early causal references name
existing sources/history only. Final validation reconstructs the earlier
prefix and later consumption-to-parent/report bindings, without recursive
validation through a future bundle. E's bundle expands only its plan,
recomputed-bundle and preservation-proof fields to exact nominal unions.

There is one live global budget axis. A retained slot has actual PENDING,
READY, RUNNING, VALIDATING and COMPLETED entries, one START_NODE wall unit and
temporary parallel occupancy, then FINISH_NODE. No child allocation,
finalization, CHILD_AGGREGATE, token/provider/revise charge or refund is added.
Same-slot identical lookup returns the existing immutable consumption with no
new event; conflicts refuse. Historical input/queue/budget/result IDs never
masquerade as current execution. The new parent consumes the real retained
result and real changed-child result in canonical slot order. Current report
counts include only executed current cells. Existing outer D/E artifact ID
domains, three-parent queue geometry and Root-required return law remain exact.

RW01-RW08, both encodings and child positions, meaningful coherent negatives,
actual M11 recomputation/Root-bound applied invalidation, Work17 and native32
remain execution obligations. Collection, PLAN constructibility or a typed
eligibility refusal alone cannot discharge them. Governance admission, U1
integration, U2/U3 and complete final D/E/F acceptance remain pending until
separately supported by actual evidence on the admitted final sources.

### Atomic Current Source Capture (T3 V03 External Candidate)

This narrow successor is not governance admission. The public Host already
exposes `current_sources`; this extension adds an atomic retained observation,
not another clock, Root or action authority.

`capture_current_action_source_v01(host, *, packet_id, expected_revision,
evaluation_time, evaluation_time_source, evaluation_context_id)` acquires the
existing Host lock, enforces reentry/revision checks and refreshes its installed
trusted source. The supplied evaluation triad must equal that refreshed source.
Rollback and conflicting source revisions remain invalid. Refresh can advance
the Host revision. A successful capture appends immutable evidence to this
Host's retained capture sequence; it does not append a business event or invoke
a capability, provider, Firewall executor or Root decision.

`ActionSourceCaptureV01` retains the actual registry, registered Root-bound
packet, packet-local current observations, logical bridge, evaluation triad,
source and Host revisions, and capture ordinal. The registry and observation
values are publicly validated. Dependency membership, freshness policy and
provenance remain packet-bound. Changed content/evidence references are allowed
as observations of change, not as permission to execute the old packet.

`validate_retained_action_source_capture_v01(host, capture, *,
require_current=False)` checks this Host's origin token and retained ordinal,
then compares the complete validated capture material. Equivalent immutable
values with the genuine retained origin are supported. A copied digest cannot
create that origin. There is no module-global origin map or external clock
attestation. Verification performs no installed-source read. With
`require_current=True`, the capture must also equal the Host's current refreshed
registry/source/revision. After Host advancement the old capture remains
historically verifiable, but cannot authorize new current computation.

Actual action dispatch still performs its independent current source refresh,
Root/packet eligibility and designated validation before STARTED. Capture never
replaces that boundary. Portable projections omit the runtime origin handle and
can support pinned historical replay only, not live origin or present permission.
The owning controls are the `test_temporal_capture_*_v03` nodes in
`tests/test_action_packet_portability_v01.py`; their execution results belong to
the external source-bound receipt, not to this contract text.

Successful Host capture is not evidence that the complete later-time E/D
vertical path executes. The external candidate reaches a separate frozen D
transition time-envelope constraint, documented in the D/E addenda. Capture
does not authorize bypassing that transition or granting action permission.

### T3 V04 Capture and Transition Evidence Boundary

The V03 frozen transition limit above is historical to the V04 external
candidate. Its explicit D v0.2 temporal successor is specified in the D/E
addenda. The Host API and retained origin law are unchanged: registry structural
time comparison consumes only a finite projection, while D/E independently
validate actual Host provenance and current versus historical use. Captures
remain evidence-only and last-refresh-relative. A new consequential action
still requires ordinary current Root/packet/Host eligibility; neither an E
result nor a later timestamp transfers permission. No external-clock attestation,
OS monitor, network, provider or real-adapter operation is introduced.
