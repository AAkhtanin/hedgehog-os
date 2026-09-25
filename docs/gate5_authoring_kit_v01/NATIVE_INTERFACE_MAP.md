# Exact Native Interface Map

Generated from the shipped pinned source without importing it. Function signatures preserve positional/keyword/default semantics. Class fields and defaults are source annotations; custom constructors/methods are listed separately. Read the linked function body for predicates and return/report meaning. Private implementation symbols are not new extension APIs.

The G51/G52 helpers are explicitly finite calibration donors. New profile selection is local reviewed code, never a wire-loaded callable. The JSON companion contains per-entry hashes and line numbers. All paths are relative to AUTHOR_VISIBLE.

## demo.run_action_packet_portability_v01.authorize_and_prepare_action_v01

Source: `source/demo/run_action_packet_portability_v01.py:493`; SHA256 `82be33d8420e4e106203898e709399230f6d7f64d4b8243e94269bec828f88cb`.

```python
authorize_and_prepare_action_v01(canonical, admitted=None, inputs=None)
```

## demo.run_action_packet_portability_v01.build_native_work_action_v01

Source: `source/demo/run_action_packet_portability_v01.py:270`; SHA256 `82be33d8420e4e106203898e709399230f6d7f64d4b8243e94269bec828f88cb`.

```python
build_native_work_action_v01(*, admitted, inputs, root_id, transaction_id, business_object_ref)
```

## demo.run_action_packet_portability_v01.host_for_prepared_action_v01

Source: `source/demo/run_action_packet_portability_v01.py:770`; SHA256 `82be33d8420e4e106203898e709399230f6d7f64d4b8243e94269bec828f88cb`.

```python
host_for_prepared_action_v01(prepared, trusted_source=None)
```

## demo.run_action_packet_portability_v01.prepare_work_program_v01

Source: `source/demo/run_action_packet_portability_v01.py:320`; SHA256 `82be33d8420e4e106203898e709399230f6d7f64d4b8243e94269bec828f88cb`.

```python
prepare_work_program_v01(*, task_id, root_id, admitted, items, device_refs)
```

## demo.run_action_packet_portability_v01.work_literal_v01

Source: `source/demo/run_action_packet_portability_v01.py:315`; SHA256 `82be33d8420e4e106203898e709399230f6d7f64d4b8243e94269bec828f88cb`.

```python
work_literal_v01(name, value_type, value)
```

## demo.work_composition_mock_capabilities_v01.TrustedMockWorkSourceV01

Source: `source/demo/work_composition_mock_capabilities_v01.py:146`; SHA256 `f02da370499fccddf88bb2dbdbd9fe6e2a33fa4143bf205a59770f9f84bb2731`.

```python
class TrustedMockWorkSourceV01:
    def __init__(self, observations, bridge, evaluation_time, evaluation_time_source, evaluation_context_id)
    def read_current_v01(self)
    def advance_v01(self, *, evaluation_time, observations=None)
```

## demo.work_composition_mock_capabilities_v01.admit_pure_operation_v01

Source: `source/demo/work_composition_mock_capabilities_v01.py:279`; SHA256 `f02da370499fccddf88bb2dbdbd9fe6e2a33fa4143bf205a59770f9f84bb2731`.

```python
admit_pure_operation_v01(*, operation_id, input_fields, output_fields, executor, output_validator, host_instance_ref)
```

## hedgehog.action_commit_packet_v02.ActionEffectParameterRecordV01

Source: `source/hedgehog/action_commit_packet_v02.py:1719`; SHA256 `e24b8c4bd3284c4b9db8944e2a9c268d26816956880ffb0700700bbf3fdc59ac`.

```python
class ActionEffectParameterRecordV01:
    parameter_name: str
    value_type: str
    value: str | int | bool
```

## hedgehog.action_commit_packet_v02.build_action_effect_parameter_record_v01

Source: `source/hedgehog/action_commit_packet_v02.py:3397`; SHA256 `e24b8c4bd3284c4b9db8944e2a9c268d26816956880ffb0700700bbf3fdc59ac`.

```python
build_action_effect_parameter_record_v01(*, parameter_name: object, value_type: object, value: object) -> ActionEffectParameterRecordV01
```

## hedgehog.action_commit_packet_v02.validate_action_commit_packet_registry_v02

Source: `source/hedgehog/action_commit_packet_v02.py:1097`; SHA256 `e24b8c4bd3284c4b9db8944e2a9c268d26816956880ffb0700700bbf3fdc59ac`.

```python
validate_action_commit_packet_registry_v02(registry: object) -> tuple[bool, tuple[str, ...]]
```

## hedgehog.drs.LocalDRS

Source: `source/hedgehog/drs.py:65`; SHA256 `7e78be61a24f285608841cbd8d07047967fb0abf7708173eadeff5f5578553f4`.

```python
class LocalDRS:
    def __init__(self, root_path: Path | str='data/drs')
    def layer_path(self, layer: str) -> Path
    def write_record(self, record: dict) -> Path
    def read_record(self, layer: str, record_id: str) -> dict
    def read_layer(self, layer: str) -> list[dict]
    def query_records(self, temporal_query: dict, layers: list[str]) -> list[dict]
```

## hedgehog.drs_memory_resolution_v01.DRSTemporalQueryV01

Source: `source/hedgehog/drs_memory_resolution_v01.py:487`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
class DRSTemporalQueryV01:
    temporal_query_version: str
    query_id: str
    query_mode: str
    semantic_address_id: str
    scope_fingerprint: str
    as_of: int
    evaluation_time: int
    evaluation_time_source: str
    time_range_start: int
    time_range_end: int
    required_time_axes: tuple[str, ...]
    freshness_policy_id: str
    max_age_seconds: int
    domain: str
    risk_class: str
    reuse_intent: str
    requested_reuse_classes: tuple[str, ...]
    required_evidence_classes: tuple[str, ...]
    forbidden_changes: tuple[str, ...]
    policy_version: str
    schema_versions: tuple[str, ...]
    owning_local_root_id: str
```

## hedgehog.drs_memory_resolution_v01.MemoryDescentBudgetV01

Source: `source/hedgehog/drs_memory_resolution_v01.py:600`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
class MemoryDescentBudgetV01:
    memory_descent_budget_version: str
    memory_descent_budget_id: str
    max_depth: int
    max_records_opened: int
    max_pointers_opened: int
    max_artifacts_opened: int
    max_bytes_opened: int
    max_lineage_edges: int
    max_conflict_records: int
```

## hedgehog.drs_memory_resolution_v01.MemoryDescentRequestV01

Source: `source/hedgehog/drs_memory_resolution_v01.py:613`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
class MemoryDescentRequestV01:
    memory_descent_request_version: str
    memory_descent_request_id: str
    retrieval_plan_id: str
    query_id: str
    owning_local_root_id: str
    root_kernel_id: str
    root_decision_input_id: str
    root_decision_id: str
    root_decision_hash: str
    requested_descent_class: str
    approved_descent_class: str
    proposed_budget_id: str
    approved_budget: MemoryDescentBudgetV01
    approved_record_ids: tuple[str, ...]
    approved_memory_pointer_ids: tuple[str, ...]
    approved_artifact_pointer_ids: tuple[str, ...]
    root_approved: bool
    reason_codes: tuple[str, ...]
    creates_permission: bool
    creates_authority: bool
```

## hedgehog.drs_memory_resolution_v01.MemoryDescentResultV01

Source: `source/hedgehog/drs_memory_resolution_v01.py:637`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
class MemoryDescentResultV01:
    memory_descent_result_version: str
    memory_descent_result_id: str
    memory_descent_request_id: str
    retrieval_plan_id: str
    query_id: str
    executed_descent_class: str
    applied_budget_id: str
    opened_record_ids: tuple[str, ...]
    opened_memory_pointer_ids: tuple[str, ...]
    opened_artifact_pointer_ids: tuple[str, ...]
    traversed_lineage_edge_ids: tuple[str, ...]
    opened_conflict_record_ids: tuple[str, ...]
    depth_reached: int
    records_opened: int
    pointers_opened: int
    artifacts_opened: int
    bytes_opened: int
    lineage_edges_traversed: int
    conflict_records_opened: int
    safe_summaries: tuple[str, ...]
    opened_payload_fingerprints: tuple[str, ...]
    limits_respected: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool
    real_world_effects_count: int
```

## hedgehog.drs_memory_resolution_v01.QueryEvaluationStateV01

Source: `source/hedgehog/drs_memory_resolution_v01.py:513`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
class QueryEvaluationStateV01:
    query_evaluation_version: str
    query_evaluation_id: str
    query_id: str
    semantic_address_id: str
    meaning_record_id: str
    query_state: str
    evaluated_at: int
    evaluation_time_source: str
    temporal_hard_gate_passed: bool
    validity_interval_passed: bool
    ttl_freshness_passed: bool
    required_time_axes_passed: bool
    scope_passed: bool
    lifecycle_passed: bool
    policy_compatible: bool
    schema_compatible: bool
    provenance_passed: bool
    authority_envelope_passed: bool
    required_evidence_passed: bool
    forbidden_changes_passed: bool
    conflict_passed: bool
    quarantine_passed: bool
    deadend_passed: bool
    action_intent_passed: bool
    g2a_action_history_passed: bool
    permission_boundary_passed: bool
    current_freshness_units: int
    observed_evidence_fingerprint: str
    checked_dependency_fingerprint: str
    source_history_hash: str
    action_history_binding_id: str | None
    eligible_for_ranking: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool
```

## hedgehog.drs_memory_resolution_v01.RetrievalPlanV01

Source: `source/hedgehog/drs_memory_resolution_v01.py:581`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
class RetrievalPlanV01:
    retrieval_plan_version: str
    retrieval_plan_id: str
    query_id: str
    semantic_address_id: str
    proposed_record_ids: tuple[str, ...]
    proposed_memory_pointer_ids: tuple[str, ...]
    proposed_artifact_pointer_ids: tuple[str, ...]
    requested_descent_class: str
    proposed_budget_id: str
    required_access_policy_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    root_approval_required: bool
    creates_authority: bool
    creates_permission: bool
    executes_read: bool
```

## hedgehog.drs_memory_resolution_v01.build_drs_temporal_query_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:916`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
build_drs_temporal_query_v01(*, query_mode: str, semantic_address_id: str, scope_fingerprint: str, as_of: int, evaluation_time: int, evaluation_time_source: str, time_range_start: int, time_range_end: int, required_time_axes: tuple[str, ...], freshness_policy_id: str, max_age_seconds: int, domain: str, risk_class: str, reuse_intent: str, requested_reuse_classes: tuple[str, ...], required_evidence_classes: tuple[str, ...], forbidden_changes: tuple[str, ...], policy_version: str, schema_versions: tuple[str, ...], owning_local_root_id: str) -> DRSTemporalQueryV01
```

## hedgehog.drs_memory_resolution_v01.build_memory_descent_budget_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:2164`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
build_memory_descent_budget_v01(*, max_depth: int, max_records_opened: int, max_pointers_opened: int, max_artifacts_opened: int, max_bytes_opened: int, max_lineage_edges: int, max_conflict_records: int) -> MemoryDescentBudgetV01
```

## hedgehog.drs_memory_resolution_v01.build_memory_descent_request_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:2275`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
build_memory_descent_request_v01(*, retrieval_plan_id: str, query_id: str, owning_local_root_id: str, root_kernel_id: str, root_decision_input_id: str, root_decision_id: str, root_decision_hash: str, requested_descent_class: str, approved_descent_class: str, proposed_budget_id: str, approved_budget: MemoryDescentBudgetV01, approved_record_ids: tuple[str, ...], approved_memory_pointer_ids: tuple[str, ...], approved_artifact_pointer_ids: tuple[str, ...]) -> MemoryDescentRequestV01
```

## hedgehog.drs_memory_resolution_v01.build_retrieval_plan_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:2078`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
build_retrieval_plan_v01(*, query_id: str, semantic_address_id: str, proposed_record_ids: tuple[str, ...], proposed_memory_pointer_ids: tuple[str, ...], proposed_artifact_pointer_ids: tuple[str, ...], requested_descent_class: str, proposed_budget_id: str, required_access_policy_ids: tuple[str, ...], reason_codes: tuple[str, ...]) -> RetrievalPlanV01
```

## hedgehog.drs_memory_resolution_v01.evaluate_drs_candidate_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:1283`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
evaluate_drs_candidate_v01(*, semantic_address: SemanticAddressV01, query: DRSTemporalQueryV01, meaning_record: MeaningRecordV01, action_history_binding: G2AActionHistoryBindingV01 | None=None) -> QueryEvaluationStateV01
```

## hedgehog.drs_memory_resolution_v01.execute_local_memory_descent_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:2958`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
execute_local_memory_descent_v01(*, retrieval_plan: RetrievalPlanV01, proposed_budget: MemoryDescentBudgetV01, descent_request: MemoryDescentRequestV01, root_kernel: RootDecisionKernelV01, root_decision_input: RootDecisionInputV01, root_decision_result: RootDecisionResultV01, source_records: tuple[MeaningRecordV01, ...], artifact_payloads: tuple[tuple[str, bytes], ...]=()) -> MemoryDescentResultV01
```

## hedgehog.drs_memory_resolution_v01.memory_descent_result_to_plain_data_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:2518`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
memory_descent_result_to_plain_data_v01(value: object) -> dict[str, object]
```

## hedgehog.drs_memory_resolution_v01.query_evaluation_state_to_plain_data_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:1146`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
query_evaluation_state_to_plain_data_v01(value: object) -> dict[str, object]
```

## hedgehog.drs_memory_resolution_v01.retrieval_plan_to_plain_data_v01

Source: `source/hedgehog/drs_memory_resolution_v01.py:2124`; SHA256 `698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8`.

```python
retrieval_plan_to_plain_data_v01(value: object) -> dict[str, object]
```

## hedgehog.drs_semantic_address_v01.ArtifactPointerV01

Source: `source/hedgehog/drs_semantic_address_v01.py:343`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class ArtifactPointerV01:
    pointer_version: str
    pointer_id: str
    storage_class: str
    object_reference: str
    content_sha256: str
    media_type: str
    byte_length: int | None
    access_policy_id: str
    sensitivity_class: str
    allowed_use_classes: tuple[str, ...]
    forbidden_use_classes: tuple[str, ...]
    summary_read_permitted: bool
    payload_read_permitted: bool
    creates_authority: bool
    creates_permission: bool
```

## hedgehog.drs_semantic_address_v01.DRSAuthorityEnvelopeV01

Source: `source/hedgehog/drs_semantic_address_v01.py:378`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class DRSAuthorityEnvelopeV01:
    authority_envelope_version: str
    authority_envelope_id: str
    authority_class: str
    owning_local_root_id: str | None
    source_root_decision_input_id: str | None
    source_root_decision_id: str | None
    source_root_decision_hash: str | None
    authority_scope_fingerprint: str
    root_acceptance_state: str
    recording_component: str
    creates_authority: bool
    creates_permission: bool
    action_permission_present: bool
```

## hedgehog.drs_semantic_address_v01.DRSTimeEnvelopeV01

Source: `source/hedgehog/drs_semantic_address_v01.py:395`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class DRSTimeEnvelopeV01:
    time_envelope_version: str
    time_envelope_id: str
    pt_created_at: int
    kt_as_of: int
    et_observed_at: int
    ct_context_anchor: int
    ttl_seconds: int
    valid_from: int
    valid_to: int
    source_observed_at: int
    source_reported_at: int
    system_ingested_at: int
    system_verified_at: int
    freshness_policy_id: str
```

## hedgehog.drs_semantic_address_v01.LineageEdgeV01

Source: `source/hedgehog/drs_semantic_address_v01.py:362`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class LineageEdgeV01:
    lineage_edge_version: str
    lineage_edge_id: str
    source_meaning_record_id: str
    target_meaning_record_id: str
    relation_class: str
    claim_dimension: str
    source_history_hash: str
    evidence_ref_ids: tuple[str, ...]
    created_at: int
    recording_component: str
    creates_authority: bool
    transfers_authority: bool
```

## hedgehog.drs_semantic_address_v01.MeaningRecordV01

Source: `source/hedgehog/drs_semantic_address_v01.py:413`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class MeaningRecordV01:
    meaning_record_version: str
    meaning_record_id: str
    semantic_address: SemanticAddressV01
    predecessor_record_id: str | None
    supersession_reason: str | None
    safe_summary: str
    semantic_tags: tuple[str, ...]
    resonance_reason: str
    memory_pointers: tuple[MemoryPointerV01, ...]
    artifact_pointers: tuple[ArtifactPointerV01, ...]
    source_reference_ids: tuple[str, ...]
    lineage_edges: tuple[LineageEdgeV01, ...]
    time_envelope: DRSTimeEnvelopeV01
    authority_envelope: DRSAuthorityEnvelopeV01
    persistent_lifecycle_state: str
    risk_hints: tuple[str, ...]
    conflict_hints: tuple[str, ...]
    reuse_policy_class: str
    policy_version: str
    schema_versions: tuple[str, ...]
    content_fingerprint: str
    recording_component: str
    local_reference_kernel_scope: str
    creates_authority: bool
    creates_permission: bool
```

## hedgehog.drs_semantic_address_v01.MemoryPointerV01

Source: `source/hedgehog/drs_semantic_address_v01.py:324`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class MemoryPointerV01:
    pointer_version: str
    pointer_id: str
    storage_class: str
    object_reference: str
    content_sha256: str
    record_class: str
    byte_length: int | None
    access_policy_id: str
    sensitivity_class: str
    allowed_use_classes: tuple[str, ...]
    forbidden_use_classes: tuple[str, ...]
    summary_read_permitted: bool
    payload_read_permitted: bool
    creates_authority: bool
    creates_permission: bool
```

## hedgehog.drs_semantic_address_v01.SemanticAddressV01

Source: `source/hedgehog/drs_semantic_address_v01.py:312`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
class SemanticAddressV01:
    address_profile_version: str
    namespace: str
    domain: str
    subject_class: str
    intent_class: str
    meaning_schema_id: str
    meaning_schema_version: str
    semantic_address_id: str
```

## hedgehog.drs_semantic_address_v01.build_drs_authority_envelope_v01

Source: `source/hedgehog/drs_semantic_address_v01.py:1333`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
build_drs_authority_envelope_v01(*, authority_class: str, owning_local_root_id: str | None, source_root_decision_input_id: str | None, source_root_decision_id: str | None, source_root_decision_hash: str | None, authority_scope_fingerprint: str, root_acceptance_state: str, recording_component: str) -> DRSAuthorityEnvelopeV01
```

## hedgehog.drs_semantic_address_v01.build_drs_time_envelope_v01

Source: `source/hedgehog/drs_semantic_address_v01.py:1444`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
build_drs_time_envelope_v01(*, pt_created_at: int, kt_as_of: int, et_observed_at: int, ct_context_anchor: int, ttl_seconds: int, valid_from: int, valid_to: int, source_observed_at: int, source_reported_at: int, system_ingested_at: int, system_verified_at: int, freshness_policy_id: str) -> DRSTimeEnvelopeV01
```

## hedgehog.drs_semantic_address_v01.build_meaning_record_v01

Source: `source/hedgehog/drs_semantic_address_v01.py:1635`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
build_meaning_record_v01(*, semantic_address: SemanticAddressV01, predecessor_record_id: str | None, supersession_reason: str | None, safe_summary: str, semantic_tags: tuple[str, ...], resonance_reason: str, memory_pointers: tuple[MemoryPointerV01, ...], artifact_pointers: tuple[ArtifactPointerV01, ...], source_reference_ids: tuple[str, ...], lineage_edges: tuple[LineageEdgeV01, ...], time_envelope: DRSTimeEnvelopeV01, authority_envelope: DRSAuthorityEnvelopeV01, persistent_lifecycle_state: str, risk_hints: tuple[str, ...], conflict_hints: tuple[str, ...], reuse_policy_class: str, policy_version: str, schema_versions: tuple[str, ...], content_fingerprint: str, recording_component: str) -> MeaningRecordV01
```

## hedgehog.drs_semantic_address_v01.build_semantic_address_v01

Source: `source/hedgehog/drs_semantic_address_v01.py:871`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
build_semantic_address_v01(*, namespace: str, domain: str, subject_class: str, intent_class: str, meaning_schema_id: str, meaning_schema_version: str) -> SemanticAddressV01
```

## hedgehog.drs_semantic_address_v01.drs_time_envelope_to_plain_data_v01

Source: `source/hedgehog/drs_semantic_address_v01.py:1503`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
drs_time_envelope_to_plain_data_v01(value: object) -> dict[str, object]
```

## hedgehog.drs_semantic_address_v01.meaning_record_to_plain_data_v01

Source: `source/hedgehog/drs_semantic_address_v01.py:1713`; SHA256 `9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20`.

```python
meaning_record_to_plain_data_v01(value: object) -> dict[str, object]
```

## hedgehog.external_drs.gate5_body_profile_v01.ReviewedBodyProfileV01

Source: `source/hedgehog/external_drs/gate5_body_profile_v01.py:14`; SHA256 `7e434e75d1913a7fab71ebc882fb21640fd33e7324ff035bc376a4b7cd65d89f`.

```python
class ReviewedBodyProfileV01:
    schema_id: str
    body_fields: tuple[str, ...]
    scope_fields: tuple[str, ...]
    policy_accept_field: str
    validate_body: object
    validate_pointer: object
    validate_binding: object
```

## hedgehog.external_drs.gate5_body_profile_v01.check_local_profile_v01

Source: `source/hedgehog/external_drs/gate5_body_profile_v01.py:33`; SHA256 `7e434e75d1913a7fab71ebc882fb21640fd33e7324ff035bc376a4b7cd65d89f`.

```python
check_local_profile_v01(profile)
```

## hedgehog.external_drs.gate5_contracts_v01.BoundedContractV01

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:260`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
class BoundedContractV01:
    kind: str
    wire: bytes
    def plain(self)
```

## hedgehog.external_drs.gate5_contracts_v01.add

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:27`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
add(a, b)
```

## hedgehog.external_drs.gate5_contracts_v01.authenticate_status

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:309`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
authenticate_status(envelope, pointer, request, policy, now, history)
```

## hedgehog.external_drs.gate5_contracts_v01.calibration

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:55`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
calibration(reference, observations)
```

## hedgehog.external_drs.gate5_contracts_v01.canonical

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:66`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
canonical(value)
```

## hedgehog.external_drs.gate5_contracts_v01.check_bundle

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:356`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
check_bundle(bundle, pointer_envelope, request, status, policy, now, history, conflicts, *, profile=None)
```

## hedgehog.external_drs.gate5_contracts_v01.check_pointer

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:343`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
check_pointer(envelope, policy, now, *, profile=None)
```

## hedgehog.external_drs.gate5_contracts_v01.check_route

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:334`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
check_route(pointer, policy, *, visited=(), depth=0, endpoint=None)
```

## hedgehog.external_drs.gate5_contracts_v01.check_status

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:328`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
check_status(envelope, pointer, request, policy, now, history)
```

## hedgehog.external_drs.gate5_contracts_v01.contract

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:272`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
contract(kind, value)
```

## hedgehog.external_drs.gate5_contracts_v01.corrected

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:60`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
corrected(readings, offset)
```

## hedgehog.external_drs.gate5_contracts_v01.decode

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:90`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
decode(data, limit=WIRE_MAX)
```

## hedgehog.external_drs.gate5_contracts_v01.hash_value

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:121`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
hash_value(value)
```

## hedgehog.external_drs.gate5_contracts_v01.identifier

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:130`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
identifier(prefix, value, field)
```

## hedgehog.external_drs.gate5_contracts_v01.integer

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:22`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
integer(value)
```

## hedgehog.external_drs.gate5_contracts_v01.keyset

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:276`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
keyset(value)
```

## hedgehog.external_drs.gate5_contracts_v01.label

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:117`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
label(value)
```

## hedgehog.external_drs.gate5_contracts_v01.mul

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:31`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
mul(a, b)
```

## hedgehog.external_drs.gate5_contracts_v01.ratio

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:41`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
ratio(value)
```

## hedgehog.external_drs.gate5_contracts_v01.rational

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:35`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
rational(num, den)
```

## hedgehog.external_drs.gate5_contracts_v01.ref

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:113`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
ref(value)
```

## hedgehog.external_drs.gate5_contracts_v01.require

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:17`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
require(condition, reason)
```

## hedgehog.external_drs.gate5_contracts_v01.sequence

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:125`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
sequence(values, maximum=16)
```

## hedgehog.external_drs.gate5_contracts_v01.sha

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:70`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
sha(value)
```

## hedgehog.external_drs.gate5_contracts_v01.shape

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:109`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
shape(value, names)
```

## hedgehog.external_drs.gate5_contracts_v01.sign

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:282`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
sign(cap, keys, purpose, value, manifest_hash)
```

## hedgehog.external_drs.gate5_contracts_v01.temporal

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:301`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
temporal(value, now, policy)
```

## hedgehog.external_drs.gate5_contracts_v01.time_shape

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:155`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
time_shape(value)
```

## hedgehog.external_drs.gate5_contracts_v01.total

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:47`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
total(values)
```

## hedgehog.external_drs.gate5_contracts_v01.validate

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:167`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
validate(kind, value, *, profile=None)
```

## hedgehog.external_drs.gate5_contracts_v01.verify

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:290`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
verify(envelope, pinned_keys, purpose, manifest_hash)
```

## hedgehog.external_drs.gate5_contracts_v01.walk

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:74`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
walk(value, depth=0)
```

## hedgehog.external_drs.gate5_contracts_v01.with_id

Source: `source/hedgehog/external_drs/gate5_contracts_v01.py:134`; SHA256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`.

```python
with_id(kind, value)
```

## hedgehog.external_drs.gate5_exchange_v01.Budget

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:39`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
class Budget:
    def __init__(self, path, task)
    def read(self)
    def reserve(self, request)
    def received_body(self, size)
```

## hedgehog.external_drs.gate5_exchange_v01.PipeChannel

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:107`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
class PipeChannel:
    def __init__(self, read_fd, write_fd, folder)
    def exact(self, size, allow_eof=False)
    def receive(self, allow_eof=False)
    def send(self, kind, value)
    def counters(self)
```

## hedgehog.external_drs.gate5_exchange_v01.PublisherBudget

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:59`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
class PublisherBudget:
    def __init__(self, path, contexts)
    def read(self)
    def reserve(self, req)
    def response(self, req, released)
    def matches_source(self, req, revision)
    def disclosure(self, req, size)
```

## hedgehog.external_drs.gate5_exchange_v01.build_source

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:147`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
build_source(inputs, cap, keys, policy, folder)
```

## hedgehog.external_drs.gate5_exchange_v01.clock

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:15`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
clock()
```

## hedgehog.external_drs.gate5_exchange_v01.immutable

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:18`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
immutable(path, value)
```

## hedgehog.external_drs.gate5_exchange_v01.request

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:189`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
request(policy, op, pointer=None, use='LOCAL_CONTEXT', subject=None, nonce=None)
```

## hedgehog.external_drs.gate5_exchange_v01.source_time

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:141`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
source_time(now)
```

## hedgehog.external_drs.gate5_exchange_v01.state_write

Source: `source/hedgehog/external_drs/gate5_exchange_v01.py:26`; SHA256 `dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07`.

```python
state_write(path, value)
```

## hedgehog.external_drs.gate5_lifecycle_v01.ImportStore

Source: `source/hedgehog/external_drs/gate5_lifecycle_v01.py:26`; SHA256 `627fa5171fbaad181c2d4e1c5e8047cc3b8b5957601a317049b05c980ae3de6f`.

```python
class ImportStore:
    def __init__(self, folder)
    def observe(self, envelope, pointer, request, policy, now)
    def conflicts(self)
    def validate_bundle(self, bundle, descriptor, request, status, policy, now)
    def import_body(self, checked, pointer)
    def quarantine(self, reason, value)
```

## hedgehog.external_drs.gate5_native_v01.native_work

Source: `source/hedgehog/external_drs/gate5_native_v01.py:243`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
native_work(mode, root, task, values)
```

## hedgehog.external_drs.gate5_native_v01.persist_and_resolve_pointer

Source: `source/hedgehog/external_drs/gate5_native_v01.py:270`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
persist_and_resolve_pointer(envelope, folder, policy)
```

## hedgehog.external_drs.gate5_native_v01.plain

Source: `source/hedgehog/external_drs/gate5_native_v01.py:28`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
plain(value)
```

## hedgehog.external_drs.gate5_native_v01.pointer_descent_v01

Source: `source/hedgehog/external_drs/gate5_native_v01.py:110`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
pointer_descent_v01(pointer, folder, source_end)
```

## hedgehog.external_drs.gate5_native_v01.root_plain

Source: `source/hedgehog/external_drs/gate5_native_v01.py:100`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
root_plain(review)
```

## hedgehog.external_drs.gate5_native_v01.root_review

Source: `source/hedgehog/external_drs/gate5_native_v01.py:45`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
root_review(root, transaction, candidate, subject, checks, claim_value, now, predicate='g51_bounded_context_review', window=None)
```

## hedgehog.external_drs.gate5_native_v01.save

Source: `source/hedgehog/external_drs/gate5_native_v01.py:40`; SHA256 `bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec`.

```python
save(path, value)
```

## hedgehog.external_drs.gate5_supplied_v01.native_result

Source: `source/hedgehog/external_drs/gate5_supplied_v01.py:24`; SHA256 `5cbb0e4851d65496e2097147b57a4bf285d36bdca9752f75db01694efe755f69`.

```python
native_result(proof, expected_root, expected_inputs)
```

## hedgehog.external_drs.gate5_supplied_v01.record

Source: `source/hedgehog/external_drs/gate5_supplied_v01.py:15`; SHA256 `5cbb0e4851d65496e2097147b57a4bf285d36bdca9752f75db01694efe755f69`.

```python
record(cls, value, **overrides)
```

## hedgehog.external_drs.gate5_supplied_v01.root_links

Source: `source/hedgehog/external_drs/gate5_supplied_v01.py:53`; SHA256 `5cbb0e4851d65496e2097147b57a4bf285d36bdca9752f75db01694efe755f69`.

```python
root_links(value, root, selected, accepted=True)
```

## hedgehog.external_drs.gate5_supplied_v01.tuple_fields

Source: `source/hedgehog/external_drs/gate5_supplied_v01.py:20`; SHA256 `5cbb0e4851d65496e2097147b57a4bf285d36bdca9752f75db01694efe755f69`.

```python
tuple_fields(value, names)
```

## hedgehog.kernel.abi_v01.KernelArtifactV01

Source: `source/hedgehog/kernel/abi_v01.py:203`; SHA256 `cc1a660a3cdceb5c30728b27016e99a752561969d744744d55b18ce0af398d31`.

```python
class KernelArtifactV01:
    abi_version: str
    artifact_id: str
    artifact_type: str
    schema_version: str
    transaction_id: str
    owner_root_id: str
    source_component: str
    authority_class: str
    lifecycle_state: str
    payload: object
    trace_refs: tuple[str, ...]
    parent_refs: tuple[str, ...]
    time_envelope: object
```

## hedgehog.kernel.abi_v01.build_kernel_artifact_v01

Source: `source/hedgehog/kernel/abi_v01.py:326`; SHA256 `cc1a660a3cdceb5c30728b27016e99a752561969d744744d55b18ce0af398d31`.

```python
build_kernel_artifact_v01(*, abi_version: str, artifact_id: str, artifact_type: str, schema_version: str, transaction_id: str, owner_root_id: str, source_component: str, authority_class: str, lifecycle_state: str, payload: object, trace_refs: tuple[str, ...], parent_refs: tuple[str, ...], time_envelope: object) -> KernelArtifactV01
```

## hedgehog.kernel.abi_v01.kernel_artifact_to_plain_dict_v01

Source: `source/hedgehog/kernel/abi_v01.py:436`; SHA256 `cc1a660a3cdceb5c30728b27016e99a752561969d744744d55b18ce0af398d31`.

```python
kernel_artifact_to_plain_dict_v01(artifact: KernelArtifactV01) -> dict[str, object]
```

## hedgehog.kernel.abi_v01.validate_kernel_artifact_v01

Source: `source/hedgehog/kernel/abi_v01.py:377`; SHA256 `cc1a660a3cdceb5c30728b27016e99a752561969d744744d55b18ce0af398d31`.

```python
validate_kernel_artifact_v01(artifact: object) -> tuple[str, ...]
```

## hedgehog.kernel.effect_firewall_v01.BoundCapabilityInvocationV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2188`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class BoundCapabilityInvocationV01:
    invocation_id: str
    admission_id: str
    definition_id: str
    task_id: str
    work_instance_id: str
    owning_root_id: str
    candidate_id: str | None
    packet_id: str | None
    execution_attempt_id: str
    inputs: tuple[object, ...]
    resource_refs: tuple[str, ...]
    input_validation: CapabilityValidationEvidenceV01
```

## hedgehog.kernel.effect_firewall_v01.CapabilityAdmissionSnapshotV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2141`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityAdmissionSnapshotV01:
    admission_id: str
    definition: CapabilityDefinitionV01
    code_sources: tuple[CapabilityCodeSnapshotV01, ...]
    input_contract_ref: str
    output_contract_ref: str
    implementation_ref: str
    catalogue_revision: int
    host_instance_ref: str
```

## hedgehog.kernel.effect_firewall_v01.CapabilityBusinessInputBindingV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2098`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityBusinessInputBindingV01:
    input_name: str
    source_kind: str
    source_name: str
    value_type: str
```

## hedgehog.kernel.effect_firewall_v01.CapabilityBusinessSemanticsV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2106`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityBusinessSemanticsV01:
    operation_key: str
    selected_action_class: str
    logical_effect_class: str
    logical_effect_namespace: str
    business_object_class: str
    business_object_namespace: str
    input_bindings: tuple[CapabilityBusinessInputBindingV01, ...]
```

## hedgehog.kernel.effect_firewall_v01.CapabilityCodeSnapshotV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2134`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityCodeSnapshotV01:
    public_symbol: str
    source_utf8: str
    source_sha256: str
```

## hedgehog.kernel.effect_firewall_v01.CapabilityDefinitionV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2117`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityDefinitionV01:
    definition_id: str
    operation_id: str
    version: str
    effect_kind: str
    business_semantics: CapabilityBusinessSemanticsV01 | None
    input_fields: tuple[CapabilityFieldV01, ...]
    output_fields: tuple[CapabilityFieldV01, ...]
    resource_refs: tuple[str, ...]
    input_validator_ref: str
    output_validator_ref: str
    executor_ref: str
    code_sha256s: tuple[tuple[str, str], ...]
    contract_sha256: str
```

## hedgehog.kernel.effect_firewall_v01.CapabilityFieldV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2087`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityFieldV01:
    name: str
    value_type: str
    required: bool
    consequential: bool
    minimum: int | str | None
    maximum: int | str | None
    allowed_values: tuple[str | int | bool, ...]
```

## hedgehog.kernel.effect_firewall_v01.CapabilityValidationEvidenceV01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2178`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
class CapabilityValidationEvidenceV01:
    definition_id: str
    validator_code_sha256: str
    subject_sha256: str
    invocation_id: str | None
    valid: bool
    reason_codes: tuple[str, ...]
```

## hedgehog.kernel.effect_firewall_v01.build_bound_capability_invocation_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2554`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
build_bound_capability_invocation_v01(*, admitted_capability: object, task_id: str, work_instance_id: str, owning_root_id: str, candidate_id: str | None, packet_id: str | None, execution_attempt_id: str, inputs: tuple, resource_refs: tuple, canonical_projection: object=None) -> BoundCapabilityInvocationV01
```

## hedgehog.kernel.effect_firewall_v01.build_capability_business_input_binding_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2343`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
build_capability_business_input_binding_v01(*, input_name: str, source_kind: str, source_name: str, value_type: str) -> CapabilityBusinessInputBindingV01
```

## hedgehog.kernel.effect_firewall_v01.build_capability_business_semantics_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2356`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
build_capability_business_semantics_v01(*, operation_key: str, selected_action_class: str, logical_effect_class: str, logical_effect_namespace: str, business_object_class: str, business_object_namespace: str, input_bindings: tuple) -> CapabilityBusinessSemanticsV01
```

## hedgehog.kernel.effect_firewall_v01.build_capability_definition_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2403`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
build_capability_definition_v01(*, operation_id: str, version: str, effect_kind: str, business_semantics: object, input_fields: tuple, output_fields: tuple, resource_refs: tuple, input_validator_ref: str, output_validator_ref: str, executor_ref: str, code_sha256s: tuple) -> CapabilityDefinitionV01
```

## hedgehog.kernel.effect_firewall_v01.build_capability_field_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2307`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
build_capability_field_v01(*, name: str, value_type: str, required: bool, consequential: bool, minimum: object=None, maximum: object=None, allowed_values: tuple=()) -> CapabilityFieldV01
```

## hedgehog.kernel.effect_firewall_v01.build_capability_validation_evidence_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2511`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
build_capability_validation_evidence_v01(*, definition: CapabilityDefinitionV01, values: tuple, invocation_id: str | None, valid: bool, reason_codes: tuple[str, ...]) -> CapabilityValidationEvidenceV01
```

## hedgehog.kernel.effect_firewall_v01.snapshot_admitted_capability_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2474`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
snapshot_admitted_capability_v01(admitted_capability: object) -> CapabilityAdmissionSnapshotV01
```

## hedgehog.kernel.effect_firewall_v01.validate_bound_capability_invocation_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2529`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
validate_bound_capability_invocation_v01(value: object, admission_snapshot: object, canonical_projection: object=None) -> tuple[str, ...]
```

## hedgehog.kernel.effect_firewall_v01.validate_capability_admission_snapshot_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2424`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
validate_capability_admission_snapshot_v01(value: object) -> tuple[str, ...]
```

## hedgehog.kernel.effect_firewall_v01.validate_capability_execution_result_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2574`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
validate_capability_execution_result_v01(value: object, invocation: object, admission_snapshot: object) -> tuple[str, ...]
```

## hedgehog.kernel.effect_firewall_v01.validate_capability_values_v01

Source: `source/hedgehog/kernel/effect_firewall_v01.py:2321`; SHA256 `46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd`.

```python
validate_capability_values_v01(fields: object, values: object) -> tuple[str, ...]
```

## hedgehog.kernel.integrity_replay_v01.domain_separated_sha256_hex_v01

Source: `source/hedgehog/kernel/integrity_replay_v01.py:249`; SHA256 `d496354e7dbca5ff9c96943fe0d4bf777e85a88b404b67c7dfcfda116ee8d0be`.

```python
domain_separated_sha256_hex_v01(*, domain: str, payload: bytes) -> str
```

## hedgehog.kernel.root_decision_v01.RootDecisionInputV01

Source: `source/hedgehog/kernel/root_decision_v01.py:119`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
class RootDecisionInputV01:
    decision_input_id: str
    transaction_id: str
    target_root_id: str
    root_review_packet: _RootReviewPacketV01
    post_vv_bundle: object
    gt_advisory: object
    policy_state: object
    permission_state: object
    temporal_state: object
    conflict_state: object
    prior_root_state: object
```

## hedgehog.kernel.root_decision_v01.RootDecisionKernelV01

Source: `source/hedgehog/kernel/root_decision_v01.py:154`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
class RootDecisionKernelV01:
    kernel_id: str
    kernel_version: str
    transition_registry: _TransitionRegistryV01
    precedence_order: tuple[str, ...]
    llm_dependency_allowed: bool
    effect_access: str
```

## hedgehog.kernel.root_decision_v01.RootDecisionResultV01

Source: `source/hedgehog/kernel/root_decision_v01.py:134`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
class RootDecisionResultV01:
    decision_id: str
    decision_input_id: str
    transaction_id: str
    target_root_id: str
    decision: str
    reason_code: str
    selected_candidate_id: str | None
    transition_decision: _TransitionDecisionV01
    hard_failure_reasons: tuple[str, ...]
    missing_evidence_refs: tuple[str, ...]
    conflict_set_ids: tuple[str, ...]
    prior_decision_id: str | None
    root_commit_created: bool
    permission_created: bool
    final_output_created: bool
    effect_requested: bool
```

## hedgehog.kernel.root_decision_v01.build_root_decision_input_v01

Source: `source/hedgehog/kernel/root_decision_v01.py:191`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
build_root_decision_input_v01(*, transaction_id: str, target_root_id: str, root_review_packet: _RootReviewPacketV01, post_vv_bundle: object, gt_advisory: object, policy_state: object, permission_state: object, temporal_state: object, conflict_state: object, prior_root_state: object) -> RootDecisionInputV01
```

## hedgehog.kernel.root_decision_v01.build_root_decision_kernel_v01

Source: `source/hedgehog/kernel/root_decision_v01.py:163`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
build_root_decision_kernel_v01() -> RootDecisionKernelV01
```

## hedgehog.kernel.root_decision_v01.decide_root_v01

Source: `source/hedgehog/kernel/root_decision_v01.py:268`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
decide_root_v01(*, kernel: object, decision_input: object) -> RootDecisionResultV01
```

## hedgehog.kernel.root_decision_v01.root_decision_result_to_plain_dict_v01

Source: `source/hedgehog/kernel/root_decision_v01.py:369`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
root_decision_result_to_plain_dict_v01(result: RootDecisionResultV01) -> dict[str, object]
```

## hedgehog.kernel.root_decision_v01.validate_root_decision_input_v01

Source: `source/hedgehog/kernel/root_decision_v01.py:255`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
validate_root_decision_input_v01(*, kernel: object, decision_input: object) -> tuple[str, ...]
```

## hedgehog.kernel.root_decision_v01.validate_root_decision_result_v01

Source: `source/hedgehog/kernel/root_decision_v01.py:290`; SHA256 `cae47026ba5c8a52ca25b2774e7ac8e92eb4e312c2eb5d1776c3a16ee276409c`.

```python
validate_root_decision_result_v01(*, kernel: object, decision_input: object, result: object) -> tuple[str, ...]
```

## hedgehog.kernel.root_signer_isolation_v01.RootOwnedCommitmentV01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:166`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
class RootOwnedCommitmentV01:
    commitment_version: str
    commitment_id: str
    transaction_id: str
    owner_root_id: str
    commitment_scope: str
    artifact_hash: str
    manifest_hash: str
    key_id: str
```

## hedgehog.kernel.root_signer_isolation_v01.RootSignatureV01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:178`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
class RootSignatureV01:
    signature_version: str
    algorithm: str
    commitment_id: str
    transaction_id: str
    owner_root_id: str
    key_id: str
    commitment_hash: str
    signature_hex: str
```

## hedgehog.kernel.root_signer_isolation_v01.RootSignatureVerificationResultV01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:190`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
class RootSignatureVerificationResultV01:
    verification_status: str
    verification_errors: tuple[str, ...]
    trusted_key_set_verified: bool
    commitment_verified: bool
    signature_contract_verified: bool
    trusted_root_present: bool
    key_id_verified: bool
    public_key_verified: bool
    commitment_hash_verified: bool
    signature_verified: bool
    root_isolation_verified: bool
    owner_root_id: str
    key_id: str
    commitment_hash: str
```

## hedgehog.kernel.root_signer_isolation_v01.RootSignerCapabilityV01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:75`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
class RootSignerCapabilityV01:
    def __init__(self, factory_token: object, *, root_id: str, key_id: str, public_key_hex: str, private_key: _Ed25519PrivateKey) -> None
    @property
    def root_id(self) -> str
    @property
    def key_id(self) -> str
    @property
    def algorithm(self) -> str
    @property
    def public_key_hex(self) -> str
```

## hedgehog.kernel.root_signer_isolation_v01.TrustedRootKeySetV01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:156`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
class TrustedRootKeySetV01:
    key_set_version: str
    key_set_id: str
    algorithm: str
    root_ids: tuple[str, ...]
    key_ids: tuple[str, ...]
    public_key_hexes: tuple[str, ...]
```

## hedgehog.kernel.root_signer_isolation_v01.build_root_owned_commitment_v01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:279`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
build_root_owned_commitment_v01(*, commitment_id: str, transaction_id: str, owner_root_id: str, commitment_scope: str, artifact_hash: str, manifest_hash: str, key_id: str) -> RootOwnedCommitmentV01
```

## hedgehog.kernel.root_signer_isolation_v01.root_owned_commitment_to_plain_dict_v01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:387`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
root_owned_commitment_to_plain_dict_v01(commitment: RootOwnedCommitmentV01) -> dict[str, object]
```

## hedgehog.kernel.root_signer_isolation_v01.root_signature_to_plain_dict_v01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:400`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
root_signature_to_plain_dict_v01(signature: RootSignatureV01) -> dict[str, object]
```

## hedgehog.kernel.root_signer_isolation_v01.sign_root_owned_commitment_v01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:305`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
sign_root_owned_commitment_v01(*, capability: RootSignerCapabilityV01, trusted_key_set: TrustedRootKeySetV01, commitment: RootOwnedCommitmentV01) -> RootSignatureV01
```

## hedgehog.kernel.root_signer_isolation_v01.trusted_root_key_set_to_plain_dict_v01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:367`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
trusted_root_key_set_to_plain_dict_v01(key_set: TrustedRootKeySetV01) -> dict[str, object]
```

## hedgehog.kernel.root_signer_isolation_v01.verify_root_signature_v01

Source: `source/hedgehog/kernel/root_signer_isolation_v01.py:351`; SHA256 `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8`.

```python
verify_root_signature_v01(*, trusted_key_set: object, commitment: object, signature: object) -> RootSignatureVerificationResultV01
```

## hedgehog.kernel.semantic_work_v01.ActorContributionV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:194`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class ActorContributionV01:
    contribution_id: str
    request_id: str
    actor_id: str
    actor_role: str
    contribution_mode: str
    bsep_projection_ref: str
    scope: str
    bounded_context_refs: tuple[str, ...]
    claims: tuple[NormalizedClaimV01, ...]
    evidence_bindings: tuple[EvidenceBindingV01, ...]
    constraint_bindings: tuple[ConstraintBindingV01, ...]
    uncertainty_bindings: tuple[UncertaintyBindingV01, ...]
    requested_validators: tuple[str, ...]
    forbidden_claims_observed: tuple[str, ...]
```

## hedgehog.kernel.semantic_work_v01.ConflictSetV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:212`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class ConflictSetV01:
    conflict_set_id: str
    subject: str
    predicate: str
    claim_ids: tuple[str, ...]
    conflicting_values: tuple[object, ...]
    source_modes: tuple[str, ...]
    resolution_state: str
```

## hedgehog.kernel.semantic_work_v01.ConstraintBindingV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:158`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class ConstraintBindingV01:
    constraint_id: str
    subject: str
    predicate: str
    object_or_value: object
    source_ref: str
    constraint_class: str
    evaluation_state: str
```

## hedgehog.kernel.semantic_work_v01.EvidenceBindingV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:148`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class EvidenceBindingV01:
    evidence_id: str
    evidence_ref: str
    evidence_class: str
    source_component_id: str
    provenance_ref: str
    evidence_state: str
```

## hedgehog.kernel.semantic_work_v01.NormalizedClaimV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:179`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class NormalizedClaimV01:
    claim_id: str
    subject: str
    predicate: str
    object_or_value: object
    time_envelope_ref: str
    provenance_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    confidence_micros: int
    source_role: str
    source_mode: str
    authority_class: str
```

## hedgehog.kernel.semantic_work_v01.RootReviewPacketV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:238`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class RootReviewPacketV01:
    packet_id: str
    request_id: str
    transaction_id: str
    target_root_id: str
    runtime_topology_ref: str
    synthesis_proposal: SynthesisProposalV01
    contribution_ids: tuple[str, ...]
    conflict_set_ids: tuple[str, ...]
    missing_evidence_refs: tuple[str, ...]
    required_validator_ids: tuple[str, ...]
    review_state: str
    authority_class: str
    root_decision_created: bool
    permission_created: bool
    final_output_created: bool
```

## hedgehog.kernel.semantic_work_v01.SemanticWorkRequestV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:134`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class SemanticWorkRequestV01:
    request_id: str
    transaction_id: str
    target_root_id: str
    runtime_topology_ref: str
    bounded_context_refs: tuple[str, ...]
    permitted_actor_ids: tuple[str, ...]
    permitted_contribution_modes: tuple[str, ...]
    requested_subjects: tuple[str, ...]
    required_evidence_classes: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
```

## hedgehog.kernel.semantic_work_v01.SynthesisProposalV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:223`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class SynthesisProposalV01:
    proposal_id: str
    request_id: str
    source_contribution_ids: tuple[str, ...]
    normalized_claims: tuple[NormalizedClaimV01, ...]
    conflict_sets: tuple[ConflictSetV01, ...]
    missing_evidence_refs: tuple[str, ...]
    contribution_modes: tuple[str, ...]
    requested_validators: tuple[str, ...]
    synthesis_summary: str
    authority_class: str
    root_review_required: bool
```

## hedgehog.kernel.semantic_work_v01.UncertaintyBindingV01

Source: `source/hedgehog/kernel/semantic_work_v01.py:169`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
class UncertaintyBindingV01:
    uncertainty_id: str
    claim_id: str
    uncertainty_kind: str
    statement: str
    confidence_micros: int
    source_ref: str
```

## hedgehog.kernel.semantic_work_v01.build_actor_contribution_v01

Source: `source/hedgehog/kernel/semantic_work_v01.py:396`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
build_actor_contribution_v01(*, contribution_id: str, request_id: str, actor_id: str, actor_role: str, contribution_mode: str, bsep_projection_ref: str, scope: str, bounded_context_refs: tuple[str, ...], claims: tuple[NormalizedClaimV01, ...], evidence_bindings: tuple[EvidenceBindingV01, ...], constraint_bindings: tuple[ConstraintBindingV01, ...], uncertainty_bindings: tuple[UncertaintyBindingV01, ...], requested_validators: tuple[str, ...], forbidden_claims_observed: tuple[str, ...]) -> ActorContributionV01
```

## hedgehog.kernel.semantic_work_v01.build_evidence_binding_v01

Source: `source/hedgehog/kernel/semantic_work_v01.py:287`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
build_evidence_binding_v01(*, evidence_id: str, evidence_ref: str, evidence_class: str, source_component_id: str, provenance_ref: str, evidence_state: str) -> EvidenceBindingV01
```

## hedgehog.kernel.semantic_work_v01.build_normalized_claim_v01

Source: `source/hedgehog/kernel/semantic_work_v01.py:362`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
build_normalized_claim_v01(*, claim_id: str, subject: str, predicate: str, object_or_value: object, time_envelope_ref: str, provenance_refs: tuple[str, ...], evidence_refs: tuple[str, ...], confidence_micros: int, source_role: str, source_mode: str) -> NormalizedClaimV01
```

## hedgehog.kernel.semantic_work_v01.build_root_review_packet_from_contributions_v01

Source: `source/hedgehog/kernel/semantic_work_v01.py:438`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
build_root_review_packet_from_contributions_v01(*, request: SemanticWorkRequestV01, contributions: tuple[ActorContributionV01, ...], trust_profiles: tuple[_ComponentTrustProfileV01, ...]) -> RootReviewPacketV01
```

## hedgehog.kernel.semantic_work_v01.build_semantic_work_request_v01

Source: `source/hedgehog/kernel/semantic_work_v01.py:256`; SHA256 `34e6064cf62fda3b0b60ebc4f60cfdc963f3a609dfb9bd5d446c5b5bdd4c45b1`.

```python
build_semantic_work_request_v01(*, request_id: str, transaction_id: str, target_root_id: str, runtime_topology_ref: str, bounded_context_refs: tuple[str, ...], permitted_actor_ids: tuple[str, ...], permitted_contribution_modes: tuple[str, ...], requested_subjects: tuple[str, ...], required_evidence_classes: tuple[str, ...], forbidden_claims: tuple[str, ...]) -> SemanticWorkRequestV01
```

## hedgehog.kernel.trust_model_v01.ComponentTrustProfileV01

Source: `source/hedgehog/kernel/trust_model_v01.py:29`; SHA256 `6a1651bd624c78a09bfb433e3af8610d0033833d373b881e732da39381b65b2d`.

```python
class ComponentTrustProfileV01:
    component_id: str
    component_class: str
    authority_class: str
    trusted_inputs: tuple[str, ...]
    untrusted_inputs: tuple[str, ...]
    produced_artifact_classes: tuple[str, ...]
    may_create_root_decision: bool
    may_create_permission: bool
    may_request_effect: bool
    may_hold_effect_handle: bool
    compromise_assumptions: tuple[str, ...]
    fail_closed_expectation: str
```

## hedgehog.kernel.trust_model_v01.build_default_component_trust_profiles_v01

Source: `source/hedgehog/kernel/trust_model_v01.py:303`; SHA256 `6a1651bd624c78a09bfb433e3af8610d0033833d373b881e732da39381b65b2d`.

```python
build_default_component_trust_profiles_v01() -> tuple[ComponentTrustProfileV01, ...]
```

## hedgehog.kernel.work_composition_v01.WorkBudgetV01

Source: `source/hedgehog/kernel/work_composition_v01.py:66`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
class WorkBudgetV01:
    max_items: int
    max_children: int
    max_model_calls: int
    max_compute_units: int
    max_revisions: int
```

## hedgehog.kernel.work_composition_v01.WorkHistoricalOutputV01

Source: `source/hedgehog/kernel/work_composition_v01.py:33`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
class WorkHistoricalOutputV01:
    task_id: str
    revision_id: str
    predecessor_work_id: str
    invocation_id: str
    result_id: str
    admission_id: str
    result_artifact_ref: str
    output_field: str
    expected_type: str
    value: action.ActionEffectParameterRecordV01
```

## hedgehog.kernel.work_composition_v01.WorkInputBindingV01

Source: `source/hedgehog/kernel/work_composition_v01.py:60`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
class WorkInputBindingV01:
    input_field: str
    source: WorkLiteralV01 | WorkOutputBindingV01 | WorkHistoricalOutputV01
```

## hedgehog.kernel.work_composition_v01.WorkItemV01

Source: `source/hedgehog/kernel/work_composition_v01.py:75`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
class WorkItemV01:
    work_id: str
    definition_id: str
    owning_root_id: str
    inputs: tuple[WorkInputBindingV01, ...]
    resource_refs: tuple[str, ...]
    depends_on: tuple[str, ...]
    guard: WorkOutputBindingV01 | None
    review_obligation_id: str | None
```

## hedgehog.kernel.work_composition_v01.WorkLiteralV01

Source: `source/hedgehog/kernel/work_composition_v01.py:21`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
class WorkLiteralV01:
    value: action.ActionEffectParameterRecordV01
```

## hedgehog.kernel.work_composition_v01.WorkOutputBindingV01

Source: `source/hedgehog/kernel/work_composition_v01.py:26`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
class WorkOutputBindingV01:
    predecessor_work_id: str
    output_field: str
    expected_type: str
```

## hedgehog.kernel.work_composition_v01.advance_work_program_v01

Source: `source/hedgehog/kernel/work_composition_v01.py:1314`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
advance_work_program_v01(program, *, catalogue, source_context, semantic_proposal, host_map, results=(), review_bindings=(), action_authorizers=None, continuation_context=None)
```

## hedgehog.kernel.work_composition_v01.validate_work_program_result_v01

Source: `source/hedgehog/kernel/work_composition_v01.py:442`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
validate_work_program_result_v01(program, results, *, catalogue, host_map, source_context, semantic_proposal, review_bindings=(), continuation_context=None)
```

## hedgehog.kernel.work_composition_v01.work_program_result_to_artifact_v01

Source: `source/hedgehog/kernel/work_composition_v01.py:606`; SHA256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`.

```python
work_program_result_to_artifact_v01(program, results, *, catalogue, host_map, source_context, semantic_proposal, review_bindings=(), continuation_context=None)
```

## hedgehog.local_drs_resolver.ResolvedDRSCandidate

Source: `source/hedgehog/local_drs_resolver.py:159`; SHA256 `5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4`.

```python
class ResolvedDRSCandidate:
    candidate_id: str
    record_id: str
    domain: str
    match_score: float
    match_reasons: tuple[str, ...]
    review_required: bool
    blocked: bool
    direct_reuse_allowed: bool
    action_permission_granted: bool
    stale: bool
    quarantine_pressure: bool
    deadend_pressure: bool
    conflicting_provenance: bool
    changed_worldstate: bool
    poisoning_pressure: bool
    reason_codes: tuple[str, ...]
```

## hedgehog.local_drs_resolver.ResolvedDRSReport

Source: `source/hedgehog/local_drs_resolver.py:179`; SHA256 `5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4`.

```python
class ResolvedDRSReport:
    query_id: str
    candidates: tuple[ResolvedDRSCandidate, ...]
    candidate_count: int
    root_review_required: bool
    direct_reuse_allowed_count: int
    blocked_count: int
    review_required_count: int
    authority_boundary: dict[str, Any]
    counters: dict[str, int]
    reason_codes: tuple[str, ...]
```

## hedgehog.local_drs_resolver.SemanticDRSRecordInput

Source: `source/hedgehog/local_drs_resolver.py:124`; SHA256 `5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4`.

```python
class SemanticDRSRecordInput:
    record_id: str
    domain: str
    content: dict[str, Any]
    semantic_keys: tuple[str, ...] = ()
    layer: str = 'work'
    record_type: str = 'generic'
    time_envelope: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    trace_refs: tuple[dict[str, Any], ...] = ()
    source_refs: tuple[dict[str, Any], ...] = ()
    status: str = 'active'
    gt: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    root_final_ref: str | None = None
    worldstate_ref: str | None = None
    poisoning_markers: tuple[str, ...] = ()
```

## hedgehog.local_drs_resolver.SemanticResolveQuery

Source: `source/hedgehog/local_drs_resolver.py:144`; SHA256 `5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4`.

```python
class SemanticResolveQuery:
    query_id: str
    domain: str
    semantic_terms: tuple[str, ...] = ()
    content_filters: dict[str, Any] = field(default_factory=dict)
    temporal_query: dict[str, Any] | None = None
    worldstate: dict[str, Any] | None = None
    source_refs: tuple[dict[str, Any], ...] = ()
    trace_refs: tuple[dict[str, Any], ...] = ()
    max_candidates: int = 10
    require_root_review: bool = True
    risk_class: str = 'normal'
```

## hedgehog.local_drs_resolver.resolve_semantic_candidates

Source: `source/hedgehog/local_drs_resolver.py:521`; SHA256 `5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4`.

```python
resolve_semantic_candidates(drs: LocalDRS, query: SemanticResolveQuery, *, layers: tuple[str, ...]=('work', 'thoughts', 'quarantine', 'deadends')) -> ResolvedDRSReport
```

## hedgehog.local_drs_resolver.write_semantic_record

Source: `source/hedgehog/local_drs_resolver.py:258`; SHA256 `5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4`.

```python
write_semantic_record(drs: LocalDRS, record_input: SemanticDRSRecordInput) -> dict[str, Any]
```

## hedgehog.work_execution_host_v01.ActionSourceCaptureV01

Source: `source/hedgehog/work_execution_host_v01.py:33`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
class ActionSourceCaptureV01:
    owning_root_id: str
    packet_id: str
    transaction_id: str
    registry: object
    root_bound_packet: object
    observations: tuple
    logical_time_bridge: object
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    source_revision: int
    host_revision: int
    capture_ordinal: int
    _origin: object = field(repr=False, compare=False)
```

## hedgehog.work_execution_host_v01.RootWorkExecutionHostV01

Source: `source/hedgehog/work_execution_host_v01.py:146`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
class RootWorkExecutionHostV01:
    def __init__(self, *, owning_root_id, registry, catalogue, packet_bindings, current_dependency_observations, logical_time_bridge, trusted_source, task_policies=(), pure_need_permissions=())
    @property
    def revision(self)
    @property
    def state_revision(self)
    @property
    def registry(self)
    @property
    def events(self)
    @property
    def current_sources(self)
    @property
    def owning_root_id(self)
    @property
    def admitted_catalogue(self)
    @property
    def catalogue_membership_history(self)
    @property
    def pure_need_resolutions(self)
    @property
    def pure_guest_evidence(self)
    @property
    def pure_admission_attempts(self)
    @property
    def pure_generation_proposals(self)
    @property
    def completed_work(self)
    @property
    def work_attempts(self)
    @property
    def unresolved_starts(self)
    def dispatch(self, *, packet_id, task_id, expected_revision, evaluation_time, evaluation_time_source, evaluation_context_id, work_instance_id=None)
    def observe_receipt(self, *, packet_id, attempt_evidence_id, expected_revision, evaluation_time, evaluation_time_source)
    def replay(self, *, packet_id)
    def apply_revocation(self, *, packet_id, expected_revision, revocation_candidate, revocation_root_projection, accepted_revocation_binding, invalidation_evidence, transition_event)
```

## hedgehog.work_execution_host_v01.TrustedWorkSourceSnapshotV01

Source: `source/hedgehog/work_execution_host_v01.py:23`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
class TrustedWorkSourceSnapshotV01:
    observations: tuple
    logical_time_bridge: object
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    source_revision: int
```

## hedgehog.work_execution_host_v01.admit_local_capability_v01

Source: `source/hedgehog/work_execution_host_v01.py:125`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
admit_local_capability_v01(*, definition, input_validator, output_validator, executor, catalogue_revision, host_instance_ref)
```

## hedgehog.work_execution_host_v01.build_root_work_execution_host_v01

Source: `source/hedgehog/work_execution_host_v01.py:488`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
build_root_work_execution_host_v01(*, owning_root_id, registry, catalogue, packet_bindings, current_dependency_observations, logical_time_bridge, trusted_source, task_policies=(), pure_need_permissions=())
```

## hedgehog.work_execution_host_v01.capture_current_action_source_v01

Source: `source/hedgehog/work_execution_host_v01.py:712`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
capture_current_action_source_v01(host, *, packet_id, expected_revision, evaluation_time, evaluation_time_source, evaluation_context_id)
```

## hedgehog.work_execution_host_v01.dispatch_current_action_v01

Source: `source/hedgehog/work_execution_host_v01.py:496`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
dispatch_current_action_v01(host, *, packet_id, task_id, expected_revision, evaluation_time, evaluation_time_source, evaluation_context_id, work_instance_id=None)
```

## hedgehog.work_execution_host_v01.inspect_current_action_v01

Source: `source/hedgehog/work_execution_host_v01.py:519`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
inspect_current_action_v01(host, *, packet_id, expected_revision, evaluation_time, evaluation_time_source, evaluation_context_id)
```

## hedgehog.work_execution_host_v01.observe_local_capability_code_v01

Source: `source/hedgehog/work_execution_host_v01.py:101`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
observe_local_capability_code_v01(public_callable)
```

## hedgehog.work_execution_host_v01.validate_retained_action_source_capture_v01

Source: `source/hedgehog/work_execution_host_v01.py:739`; SHA256 `56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b`.

```python
validate_retained_action_source_capture_v01(host, capture, *, require_current=False)
```

## Closed Carrier Fields and Bounds

```python
LIMIT = (1 << 62) - 1
WIRE_MAX, BODY_MAX, POINTER_MAX, DEPTH_MAX = (262144, 65536, 16384, 12)
BODY_SCHEMA = 'BoundedCalibrationSummaryV01'
ROOT_A, ROOT_B = ('root:gate5:calibration', 'root:gate5:site')
UNIT, QUANTITY = ('synthetic_unit_v01', 'reference_quantity_v01')
IDS = {'pointer': ('pointer_id', 'g5pointer'), 'manifest': ('manifest_id', 'g5manifest'), 'request': ('request_id', 'g5request'), 'import': ('import_id', 'g5import'), 'disposition': ('disposition_id', 'g5disposition'), 'adaptation': ('local_view_id', 'g5adaptation')}
FIELDS = {'body': ('version', 'source_record_ref', 'source_revision', 'unit_id', 'quantity_id', 'reference', 'observations', 'n', 'total', 'correction', 'source_work_ref', 'source_review_ref', 'time_envelope', 'ttl_base', 'source_lineage_refs'), 'manifest': ('version', 'manifest_id', 'publisher', 'source_revision', 'source_refs', 'declared_schema', 'files'), 'pointer': ('version', 'pointer_id', 'publisher_root_id', 'publisher_key_id', 'semantic_address', 'source_record_ref', 'source_revision', 'source_review_ref', 'body_sha256', 'body_bytes', 'media_type', 'artifact_manifest_ref', 'safe_summary', 'published_scope', 'allowed_use_classes', 'forbidden_use_classes', 'recipient_scope', 'time_envelope', 'source_lineage_refs', 'access_policy_ref', 'revocation_stream_id', 'transport_object_id', 'creates_authority', 'creates_permission'), 'request': ('version', 'request_id', 'op', 'requester', 'publisher', 'task_ref', 'request_revision', 'pointer_ref', 'trust_profile_hash', 'use_class', 'object_id', 'allowed_size', 'nonce', 'deadline', 'issued_at', 'subject_request_ref', 'owner_transport_scope'), 'entry': ('version', 'pointer_id', 'publisher_root_id', 'stream_id', 'revision', 'state', 'effective_at', 'reason_ref', 'entry_hash'), 'status': ('version', 'entry', 'requested_pointer_hash', 'requester', 'subject_request_ref', 'request_revision', 'nonce', 'checked_at', 'valid_until'), 'release': ('version', 'state', 'request_ref', 'request_revision', 'pointer_ref', 'manifest_ref', 'body_hash', 'recipient', 'use_class', 'nonce', 'deadline', 'release_review_ref'), 'import': ('version', 'import_id', 'local_request_ref', 'pointer_ref', 'foreign_publisher', 'foreign_source_ref', 'foreign_revision', 'received_manifest_hash', 'body_hash', 'receive_event_ref', 'validation_results', 'status_entry_hash', 'dependency_fingerprint', 'policy_hash', 'creates_permission'), 'disposition': ('version', 'disposition_id', 'candidate_ref', 'parent_ref', 'state', 'local_review_ref'), 'adaptation': ('version', 'local_view_id', 'import_ref', 'foreign_source_ref', 'source_field', 'value', 'input_names', 'work_request_ref', 'local_acceptance_ref')}
COMMON_BODY_FIELDS = ('version', 'source_record_ref', 'source_revision', 'source_work_ref', 'source_review_ref', 'time_envelope', 'ttl_base', 'source_lineage_refs')
```
