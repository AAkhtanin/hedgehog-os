"""Reference-only domain/Root contract control; no D/E or action execution."""
from types import SimpleNamespace
import pytest
from hedgehog.domains.testflix import kernel_adapter_v01 as kernel
from hedgehog.domains.testflix import mock_world_v01 as world
from hedgehog.domains.testflix import contracts_v01 as c, evidence_v01 as e
from hedgehog.kernel import root_decision_v01 as roots


@pytest.mark.parametrize('price,valid', ((500, True), (600, True), (700, False)))
def test_information_review_candidate_status_public_root_v09(price, valid):
    # This bridge consumes references only. These are not fabricated D returns.
    quote_refs = dict(program=SimpleNamespace(
        topology_artifact=SimpleNamespace(artifact_id='reference:review-control-topology'),
        candidate=SimpleNamespace(bsep_ref='reference:review-control-bsep')),
        results=(SimpleNamespace(result=SimpleNamespace(result_id='reference:review-control-result')),))
    before = tuple(world.CALLS)
    review = kernel.review_information_v01(transaction='transaction:review-control',
        selected='candidate:'+str(price), subject='subject:review-control', predicate='within_consent',
        value=dict(price_minor=price, consent_limit_minor=650, within_consent=valid),
        quote=quote_refs, valid=valid, root='root:testflix:bank')
    assert not roots.validate_root_decision_result_v01(kernel=review['kernel'],
        decision_input=review['inputs'], result=review['result'])
    assert (review['result'].decision == 'ACCEPT') is valid
    plain = roots.root_decision_input_to_plain_dict_v01(review['inputs'])
    assert plain['post_vv_bundle']['hard_failure_reasons'] == ([] if valid else ['candidate_validation_failed'])
    assert plain['policy_state']['identity_passed'] and plain['temporal_state']['temporal_valid']
    assert plain['permission_state']['permission_required'] is False
    assert tuple(world.CALLS) == before


def test_writeback_projection_exact_bytes_and_container_isolation_v09():
    stored={'content':{'answer':{'plan':'reference:plan','period':[10,20]}}}
    value=dict(stored=stored,stored_bytes=c.canonical_v01(stored),meaning={'ref':'reference:meaning'},
        review={'ref':'reference:review'})
    before=c.canonical_v01(stored)
    with pytest.raises(ValueError,match='^unprojectable_type:bytes$'):
        e.plain_value_v01(value)
    a=e._writeback_to_plain_v09(value);b=e._writeback_to_plain_v09(value)
    assert a==b=={k:v for k,v in value.items() if k!='stored_bytes'}
    assert c.canonical_v01(a['stored'])==value['stored_bytes']
    a['stored']['content']['answer']['period'].append(30)
    assert c.canonical_v01(stored)==before and b['stored']==stored
    with pytest.raises(ValueError,match='^stored_summary_bytes_binding$'):
        e._writeback_to_plain_v09(dict(value,stored_bytes=value['stored_bytes']+b' '))
    with pytest.raises(ValueError,match='^unprojectable_type:object$'):
        e._writeback_to_plain_v09(dict(value,unknown=object()))
    assert e._writeback_to_plain_v09(value)==b


def test_action_export_actual_native_receipt_without_runtime_handles_v09():
    from tests import test_work_composition_v01 as donor
    from hedgehog.domains.testflix import lifecycle_v01 as life
    prepared,_=donor.native_e_packet('transaction:export-receipt:v09')
    trusted=donor.e_donor.TemporalCountingSourceV03(donor.mocks.TrustedMockWorkSourceV01(
        prepared.observations,prepared.bridge,donor.e_donor._E3_TIME,'u1.controlled_utc','context:u1:dispatch'))
    host=donor.runner.host_for_prepared_action_v01(prepared,trusted)
    actual=life.dispatch_v01(dict(bound=prepared.root_bound,admitted=prepared.admitted,inputs=prepared.inputs,
        host=host,source=trusted),'task:export-receipt:v09')
    registry=actual['registry']
    context=registry.action_packet_fulfillment_attempt_contexts[-1]
    receipt=donor.abi.kernel_artifact_to_plain_dict_v01(context.receipt)
    execution=donor.firewall.native_execution_evidence_from_plain_data_v01(receipt['payload']['execution_evidence'])
    assert not donor.firewall.validate_native_execution_evidence_v01(execution)
    assert actual['context']==context and actual['execution']==execution and actual['receipt']==context.receipt
    before=(trusted.reads,donor.mocks.observed_mock_calls_v01())
    with pytest.raises(ValueError,match='^unprojectable_type:function$'):
        e.plain_value_v01(actual)
    a=e._action_record_to_plain_v09(actual);b=e._action_record_to_plain_v09(actual)
    assert a==b and not {'host','source','admitted'}.intersection(a)
    assert a['receipt']==receipt and a['context']['receipt']==receipt
    assert a['admission_snapshot']==e.plain_value_v01(donor.firewall.snapshot_admitted_capability_v01(prepared.admitted))
    a['receipt']['payload']['control_mutation']=True
    assert b['receipt']==donor.abi.kernel_artifact_to_plain_dict_v01(context.receipt)
    assert before==(trusted.reads,donor.mocks.observed_mock_calls_v01())
