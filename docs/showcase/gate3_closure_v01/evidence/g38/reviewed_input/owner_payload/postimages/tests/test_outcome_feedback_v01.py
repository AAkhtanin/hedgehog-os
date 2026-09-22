"""Pure reference controls: no domain, Root, Host, Work, D/E or live execution."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator, validators

from hedgehog import outcome_feedback_v01 as g3
from hedgehog.kernel.abi_v01 import (
    build_kernel_artifact_v01, kernel_artifact_to_plain_dict_v01,
    kernel_artifact_to_canonical_ref_v01, validate_kernel_artifact_v01,
    validate_kernel_artifact_bundle_v01,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01, domain_separated_sha256_hex_v01

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def reference():
    return json.loads((ROOT/'fixtures/gate3_reference_v01.json').read_text())


@pytest.fixture(scope='module')
def schema():
    body = json.loads((ROOT/'schemas/outcome_feedback_v01.schema.json').read_text())
    Draft202012Validator.check_schema(body)
    exact = validators.extend(Draft202012Validator,
        type_checker=Draft202012Validator.TYPE_CHECKER.redefine('integer', lambda checker, value: type(value) is int))
    return exact(body)


def produce(reference, name='lawful_a'):
    source = deepcopy(reference['reference_sources'][name])
    observation = g3.build_outcome_observation_v01(source_bundle=source, profile=g3.SOURCE_PROFILE_ID,
        explicit_times=deepcopy(reference['explicit_times']))
    value = g3.build_outcome_feedback_v01(observation=observation, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)
    return source, observation, value


def resign(plain):
    result = deepcopy(plain)
    result['feedback_id'] = domain_separated_sha256_hex_v01(domain='g3_feedback_v01',
        payload=canonical_json_bytes_v01({k:v for k,v in result.items() if k!='feedback_id'}))
    return result


@pytest.mark.parametrize('name', ('lawful_a','lawful_b','bad_stopped','honest_missing','summary_missing',
    'correct_stop','indiscriminate_stop','transport_failure','no_expectation','label_only','unexpected_effect'))
def test_reference_assessments_are_derived_not_runtime_claims(reference, schema, name):
    source, observation, value = produce(reference, name)
    assert g3.validate_outcome_observation_v01(observation, source_bundle=source, profile=g3.SOURCE_PROFILE_ID) == ()
    assert g3.validate_outcome_feedback_against_sources_v01(value, source_bundle=source, profile=g3.SOURCE_PROFILE_ID) == ()
    plain = g3.outcome_feedback_to_plain_data_v01(value)
    assert not list(schema.iter_errors(plain))
    assert [plain[k] for k in ('proposal_assessment','enforcement_outcome','task_outcome')] == reference['expected_assessments'][name]
    assert plain['evidence_class'] == 'REFERENCE_FIXTURE_NOT_EXECUTED'
    assert plain['execution_lane'] == 'HISTORICAL_IMPORT'
    assert plain['root_decision_ref']['state'] == plain['action_packet_ref']['state'] == plain['firewall_decision_ref']['state'] == 'NOT_REACHED'
    assert plain['receipt_refs'] == [] and plain['actual_latency']['elapsed_us']['state'] == 'UNKNOWN'
    assert all(flag is False for flag in plain['non_authority_flags'].values())
    if name in ('honest_missing','summary_missing','transport_failure','no_expectation','unexpected_effect'):
        assert plain['update_eligibility'] == 'NO_UPDATE'
    if name == 'unexpected_effect':
        assert plain['policy_violations']['realized_violation_refs']
        assert plain['task_outcome'] == 'FAILED'


def test_equivalent_values_are_canonical_and_deeply_immutable(reference):
    source, _, first = produce(reference)
    second_source = json.loads(json.dumps(source))
    second_obs = g3.build_outcome_observation_v01(source_bundle=second_source, profile=g3.SOURCE_PROFILE_ID,
                                                explicit_times=reference['explicit_times'])
    second = g3.build_outcome_feedback_v01(observation=second_obs, source_bundle=second_source, profile=g3.SOURCE_PROFILE_ID)
    assert first is not second and first.canonical == second.canonical
    before = bytes(first.canonical)
    plain = g3.outcome_feedback_to_plain_data_v01(first)
    plain['advisory_subject_key']['local_root_scope_id'] = 'root:changed'
    plain['source_refs'].append('foreign')
    assert first.canonical == before and second.canonical == before
    assert g3.outcome_feedback_to_plain_data_v01(first)['source_refs'] != plain['source_refs']
    with pytest.raises(FrozenInstanceError):
        first.canonical = b'{}'
    tag = g3.TaggedValueV01('KNOWN', 12, '', ('source:count',), 'COUNT')
    copy = tag.to_plain_data()
    copy['evidence_refs'].append('new')
    assert tag.evidence_refs == ('source:count',)


def test_every_independent_call_checks_current_source_material(reference):
    source, observation, value = produce(reference)
    baseline = deepcopy(source)
    source['observation']['resource_after'] = 900
    assert g3.validate_outcome_feedback_against_sources_v01(value, source_bundle=source, profile=g3.SOURCE_PROFILE_ID) == ('g31_source_not_admitted',)
    assert g3.validate_outcome_observation_v01(observation, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)
    assert not g3.validate_outcome_feedback_against_sources_v01(value, source_bundle=baseline, profile=g3.SOURCE_PROFILE_ID)
    assert g3.validate_outcome_feedback_against_sources_v01(value, source_bundle=baseline, profile='unknown.v1') == ('g31_source_profile_unknown',)


def test_pure_source_scan_cost_is_one_per_independent_operation(reference):
    calls = []
    tool = next(number for number in range(6) if sys.monitoring.get_tool(number) is None)
    code = g3._source.__code__
    sys.monitoring.use_tool_id(tool, 'g31_source_scan_observer')
    try:
        sys.monitoring.register_callback(tool, sys.monitoring.events.PY_START, lambda code, offset: calls.append(code.co_name))
        sys.monitoring.set_local_events(tool, code, sys.monitoring.events.PY_START)
        source, observation, value = produce(reference)
        assert len(calls) == 2
        assert not g3.validate_outcome_observation_v01(observation, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)
        assert len(calls) == 3
        assert not g3.validate_outcome_feedback_against_sources_v01(value, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)
        assert len(calls) == 4
        source['observation']['resource_after'] = 900
        assert g3.validate_outcome_feedback_against_sources_v01(value, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)
        assert len(calls) == 5
    finally:
        sys.monitoring.set_local_events(tool, code, 0)
        sys.monitoring.register_callback(tool, sys.monitoring.events.PY_START, None)
        sys.monitoring.free_tool_id(tool)


def test_complete_cross_context_rehash_and_source_substitution_fail(reference):
    a, _, first = produce(reference, 'lawful_a')
    b, _, second = produce(reference, 'lawful_b')
    assert not g3.validate_outcome_feedback_structure_v01(second)
    assert not g3.validate_outcome_feedback_against_sources_v01(second, source_bundle=b, profile=g3.SOURCE_PROFILE_ID)
    assert g3.validate_outcome_feedback_against_sources_v01(second, source_bundle=a, profile=g3.SOURCE_PROFILE_ID) == ('g31_feedback_source_mismatch',)
    assert g3.validate_outcome_feedback_against_sources_v01(first, source_bundle=b, profile=g3.SOURCE_PROFILE_ID)
    a['policy']['revision'] = 'wrong.v2'
    assert g3.validate_outcome_feedback_against_sources_v01(first, source_bundle=a, profile=g3.SOURCE_PROFILE_ID)


@pytest.mark.parametrize('field,value', [('transaction_id','wrong:transaction'),('local_root_scope_id','root:foreign'),
    ('source_profile_id','unknown.source'),('scenario_id','changed.label'),('source_closure_ref','wrong:closure'),
    ('advice_claim_profile_id','claim:unknown'),('execution_lane','LIVE_CAPTURED_ORIGIN'),('task_outcome','FAILED')])
def test_rehashed_semantic_mutations_do_not_pass_context(reference, field, value):
    source, _, valid = produce(reference)
    plain = g3.outcome_feedback_to_plain_data_v01(valid)
    plain[field] = value
    if field=='source_profile_id':
        # Unknown profiles are refused by the public parser before contextual use.
        with pytest.raises(ValueError,match='^g31_source_profile_unknown$'):
            g3.parse_outcome_feedback_json_v01(canonical_json_bytes_v01(resign(plain)))
        assert not g3.validate_outcome_feedback_against_sources_v01(valid, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)
        return
    forged = g3.parse_outcome_feedback_json_v01(canonical_json_bytes_v01(resign(plain)))
    assert not g3.validate_outcome_feedback_structure_v01(forged)
    assert g3.validate_outcome_feedback_against_sources_v01(forged, source_bundle=source, profile=g3.SOURCE_PROFILE_ID) == ('g31_feedback_source_mismatch',)
    assert not g3.validate_outcome_feedback_against_sources_v01(valid, source_bundle=source, profile=g3.SOURCE_PROFILE_ID)


@pytest.mark.parametrize('mutation', ('extra','missing','version','enum','bool','float','overflow','unit','unknown_tag','authority','tagged_missing','nested_extra'))
def test_closed_schema_and_dto_invalid_neighbors(reference, schema, mutation):
    _, _, value = produce(reference)
    body = g3.outcome_feedback_to_plain_data_v01(value)
    if mutation == 'extra': body['unauthorized'] = 1
    elif mutation == 'missing': del body['other_root_evidence_refs']
    elif mutation == 'version': body['schema_version'] = 'v9'
    elif mutation == 'enum': body['enforcement_outcome'] = 'PASS'
    elif mutation == 'bool': body['pre_decision_expectation']['value'] = True
    elif mutation == 'float': body['pre_decision_expectation']['value'] = 1.0
    elif mutation == 'overflow': body['pre_decision_expectation']['value'] = 1000000001
    elif mutation == 'unit': body['pre_decision_expectation']['unit'] = 'DOLLARS'
    elif mutation == 'unknown_tag': body['root_decision_ref']['state'] = 'ACCEPT'
    elif mutation == 'authority': body['non_authority_flags']['claims_permission'] = True
    elif mutation == 'tagged_missing': body['root_decision_ref']['value'] = 'invented:root'
    elif mutation == 'nested_extra': body['avf_history_key']['brand'] = 'brand:trust'
    body = resign(body)
    assert list(schema.iter_errors(body)), mutation
    assert g3.validate_outcome_feedback_structure_v01(body), mutation


@pytest.mark.parametrize('raw', ('{"x":1,"x":2}', '{"nested":{"x":1,"x":2}}', '{"x":NaN}', '{"x":Infinity}', '{"x":1.0}', '{"x":"\\ud800"}'))
def test_public_raw_json_rejects_duplicates_and_noninteger_tokens(raw):
    with pytest.raises(ValueError):
        g3.parse_outcome_feedback_json_v01(raw)


def test_public_parser_rejects_duplicate_real_envelope_key(reference):
    _, _, value = produce(reference)
    raw = value.canonical.decode().replace('"schema_version":"v0.1"', '"schema_version":"v0.1","schema_version":"v0.1"')
    with pytest.raises(ValueError, match='g31_duplicate_json_key'):
        g3.parse_outcome_feedback_json_v01(raw)
    assert g3.parse_outcome_feedback_json_v01(value.canonical) == value


@pytest.mark.parametrize('times', [dict(ingested_time=1895184009,evaluated_at=1895184012,timestamp=1895184013),
    dict(ingested_time=1895184011,evaluated_at=1895184010,timestamp=1895184013),
    dict(ingested_time=1895184011,evaluated_at=1895184012,timestamp=1895184011),
    dict(ingested_time=1895184011,evaluated_at=1895188012,timestamp=1895188013)])
def test_explicit_time_order_and_expiry_refuse(reference, times):
    with pytest.raises(ValueError):
        g3.build_outcome_observation_v01(source_bundle=reference['reference_sources']['lawful_a'], profile=g3.SOURCE_PROFILE_ID, explicit_times=times)


def test_lookahead_and_wrong_observed_revision_fail(reference):
    for group, key, replacement in [('proposal','created_at',1895184011),('expectation','created_at',1895184011),('observation','result_revision','wrong.v2')]:
        source = deepcopy(reference['reference_sources']['lawful_a'])
        source[group][key] = replacement
        with pytest.raises(ValueError, match='g31_source_not_admitted'):
            g3.build_outcome_observation_v01(source_bundle=source, profile=g3.SOURCE_PROFILE_ID, explicit_times=reference['explicit_times'])


def test_atlas_summary_labels_occurrence_and_three_axes(reference):
    values = {name:g3.outcome_feedback_to_plain_data_v01(produce(reference,name)[2]) for name in ('lawful_a','lawful_b','label_only','bad_stopped','honest_missing','summary_missing')}
    for field in ('proposal_assessment','enforcement_outcome','task_outcome'):
        assert values['lawful_a'][field] == values['lawful_b'][field] == values['label_only'][field]
        assert values['honest_missing'][field] == values['summary_missing'][field]
    assert values['summary_missing']['task_outcome'] != 'COMPLETED'
    assert values['label_only']['observation_scope']['occurrence_ref'] == values['lawful_a']['observation_scope']['occurrence_ref']
    assert values['bad_stopped']['proposal_assessment'] == 'UNSAFE'
    assert values['bad_stopped']['enforcement_outcome'] == 'BLOCKED_AS_REQUIRED'
    assert values['honest_missing']['proposal_assessment'] == 'NOT_SCORABLE'
    assert values['lawful_a']['avf_history_key']['local_root_scope_id'] != values['lawful_b']['avf_history_key']['local_root_scope_id']
    assert len(values['lawful_a']['advisory_subject_key']) == len(values['lawful_a']['avf_history_key']) == 11


def test_abi_projection_and_structural_historical_bridge(reference):
    source, _, feedback = produce(reference)
    plain = g3.outcome_feedback_to_plain_data_v01(feedback)
    context = dict(artifact_id='g31:feedback:evidence',transaction_id=plain['transaction_id'],owner_root_id=plain['local_root_scope_id'],parent_refs=[],time_envelope=plain['time_envelope'])
    artifact = g3.project_outcome_feedback_evidence_v01(feedback, source_bundle=source, profile=g3.SOURCE_PROFILE_ID, current_abi_context=context)
    assert validate_kernel_artifact_v01(artifact) == ()
    assert validate_kernel_artifact_bundle_v01(artifacts=(artifact,)) == ()
    projected = kernel_artifact_to_plain_dict_v01(artifact)
    assert projected['payload']['feedback'] == plain
    assert projected['authority_class'] == 'EVIDENCE_ONLY'
    with pytest.raises(ValueError):
        build_kernel_artifact_v01(**{**projected, 'payload': {'transaction_id':'reserved'}, 'trace_refs':tuple(projected['trace_refs']), 'parent_refs':()})
    bridge = build_kernel_artifact_v01(**{**projected,'artifact_id':'g31:current:bridge','transaction_id':'g31:new:transaction',
        'payload':{'g3_profile_id':g3.PROFILE_ID,'historical_source':vars(kernel_artifact_to_canonical_ref_v01(artifact))}, 'trace_refs':(artifact.artifact_id,), 'parent_refs':()})
    assert validate_kernel_artifact_bundle_v01(artifacts=(bridge,)) == ()
    assert validate_kernel_artifact_bundle_v01(artifacts=(artifact,bridge))
    assert kernel_artifact_to_plain_dict_v01(artifact) == projected
    foreign = dict(context, transaction_id='g31:new:transaction')
    with pytest.raises(ValueError, match='g31_abi_context_mismatch'):
        g3.project_outcome_feedback_evidence_v01(feedback, source_bundle=source, profile=g3.SOURCE_PROFILE_ID, current_abi_context=foreign)


def test_bounds_and_numeric_oracle_remain_specification_only(reference):
    with pytest.raises(ValueError):
        g3.parse_outcome_feedback_json_v01(' ' * 65537)
    with pytest.raises(ValueError):
        g3.parse_outcome_feedback_json_v01('{"x":' + '[' * 20 + '0' + ']' * 20 + '}')
    vectors=reference['numeric_reference']
    assert vectors['negative_then_positive'][2] == [3,382812500,0,334960938,-176025391,18035,-44006348,655993652]
    assert vectors['increment_counterexample']['expected_R_new'] == 3
    assert len(vectors['decay_after_separate_currentness_check']) == 8
    assert reference['evidence_class'] == 'REFERENCE_FIXTURE_NOT_EXECUTED'
    assert vectors['CP_RANK_reference']['actual_work_consumption'] == 'NOT_EXECUTED'
