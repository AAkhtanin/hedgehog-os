"""Actual AT3 saved sources; no fixture invokes a domain collector."""
import copy
import json
import os
from pathlib import Path
import pytest
from hedgehog import outcome_feedback_v01 as f, outcome_feedback_consumer_v01 as consumer
from hedgehog.domains.testflix import incident_atlas_proof_v01 as proof

@pytest.fixture(scope='module')
def saved_testflix():
    name=os.environ.get('AT3_SAVED_TESTFLIX')
    assert name, 'Supply the actual AT3 collector result; never collect in pytest'
    return json.loads(Path(name).read_bytes())

def test_testflix_supplied_complete_v01(saved_testflix):
    assert proof.validate_testflix_v01(saved_testflix)

def test_testflix_T1_pending_changed_quote_v01(saved_testflix):
    t=saved_testflix['T1']
    assert proof.inspect_saved_v01(t['before']).present_executable
    actual=proof.validate_refusal_v01(t['refusal'])
    assert actual.historical_state.lifecycle_state=='PENDING_FULFILLMENT'
    assert actual.historical_state.idempotency_disposition!='CONSUMED'
    assert t['before']['bound']==t['refusal']['action']['bound']

def test_testflix_coherent_old_quote_substitution_v01(saved_testflix):
    value=copy.deepcopy(saved_testflix);t=value['T1']
    old=t['before']['clock']['observations']
    t['refusal']['action']['clock']['observations']=old
    t['current_observation']=t['before']['observation']
    actual=proof.inspect_saved_v01(t['refusal']['action'])
    assert actual.present_executable, 'Unchanged original quote is a lawful neighbor'
    t['refusal']['inspection']=f.g35_record_to_plain_v01(actual)
    with pytest.raises(ValueError,match='atlas_testflix_saved_current_refusal'):
        proof.validate_cards_v01(value)

def test_testflix_T2_expiry_and_owner_revocation_v01(saved_testflix):
    t=saved_testflix['T2']
    expiry=proof.validate_refusal_v01(t['expiry']);revoked=proof.validate_refusal_v01(t['revocation'])
    assert expiry.evaluation_time==t['deadline']
    assert revoked.historical_state.lifecycle_state=='REVOKED'
    assert revoked.evaluation_time<t['deadline']

def test_testflix_coherent_expiry_time_misbinding_v01(saved_testflix):
    value=copy.deepcopy(saved_testflix);row=value['T2']['expiry']
    row['action']['clock']['evaluation_time']+=1
    row['inspection']=f.g35_record_to_plain_v01(proof.inspect_saved_v01(row['action']))
    assert not proof.validate_refusal_v01(row).present_executable
    with pytest.raises(ValueError,match='atlas_testflix_T2_exact_expiry'):
        proof.validate_cards_v01(value)

def test_testflix_T3_same_receipt_no_second_purchase_v01(saved_testflix):
    t=saved_testflix['T3']
    assert t['before']==t['after']
    assert proof.validate_refusal_v01(t['retry']).historical_state.idempotency_disposition=='CONSUMED'
    assert t['extension_reason']=='payment_period_already_consumed'

def test_testflix_genuine_wrong_operation_receipt_v01(saved_testflix):
    payment=copy.deepcopy(saved_testflix['actions']['payment'])
    session=saved_testflix['actions']['session_issuance']
    proof.validate_action_v01(session)
    for key in ('receipt','execution','context','output'):payment[key]=copy.deepcopy(session[key])
    with pytest.raises(ValueError,match='atlas_testflix_receipt_context'):
        proof.validate_action_v01(payment)

def test_testflix_prediction_history_changes_work_v01(saved_testflix):
    assert proof.validate_experience_v01(saved_testflix)
    exp=saved_testflix['experience']
    assert exp['observation']['output']['checks'][0]['healthy'] is True
    assert exp['before']['projection']['selected']=='provenance'
    assert exp['after']['projection']['selected']=='constraint'
    assert exp['snapshot']['prior']['effective_count']==1

def test_testflix_coherent_advisory_score_v01(saved_testflix):
    value=copy.deepcopy(saved_testflix['experience']['after']);p=value['projection']
    p['rows'][0]['adjusted_fp']+=1
    p['projection_id']=consumer.identity('advisory',{k:v for k,v in p.items() if k!='projection_id'})
    with pytest.raises(ValueError,match='atlas_testflix_applied_history'):
        proof.validate_current_projection_v01(value,saved_testflix['experience']['snapshot'],saved_testflix['experience']['head'])

def test_testflix_T4_memory_is_consumed_not_permission_v01(saved_testflix):
    assert proof.validate_memory_v01(saved_testflix)
    t=saved_testflix['T4']
    assert proof.validate_review_v01(t['no_consent']['review'])[1].decision=='NEEDS_USER'
    assert proof.validate_review_v01(t['explicit_consent']['review'])[1].decision=='ACCEPT'
    assert t['before']==t['after']

def test_testflix_genuine_consent_review_substitution_v01(saved_testflix):
    value=copy.deepcopy(saved_testflix);t=value['T4']
    assert proof.validate_review_v01(t['explicit_consent']['review'])[1].decision=='ACCEPT'
    t['no_consent']['review']=copy.deepcopy(t['explicit_consent']['review'])
    with pytest.raises(ValueError,match='atlas_testflix_memory_current_consent'):
        proof.validate_memory_v01(value)

def test_testflix_fresh_session_consumes_current_work_v01(saved_testflix):
    assert proof.validate_consumption_v01(saved_testflix)
    assert saved_testflix['counts']['main_payments']==1
    assert saved_testflix['counts']['new_paid_periods']==1

def test_testflix_genuine_wrong_work_reference_v01(saved_testflix):
    value=copy.deepcopy(saved_testflix);old=value['experience']['observation']
    proof.validate_work_v01(old)
    value['consumption']['material']['work_artifact_ref']=old['artifact']['artifact_id']
    value['consumption']['material']['output_sha256']=proof.digest(old['output'])
    with pytest.raises(ValueError,match='atlas_testflix_consumed_result_reference'):
        proof.validate_consumption_v01(value)

def test_testflix_equivalent_positive_after_controls_v01(saved_testflix):
    assert proof.validate_testflix_v01(json.loads(json.dumps(saved_testflix)))

def test_testflix_work_predicate_uses_actual_device_scope_v01(saved_testflix):
    material=copy.deepcopy(saved_testflix['experience']['after']['material'])
    assert proof.native.evaluate_v01(material)['checks'][0]['healthy']
    material['devices'][0]['max_quality']=1
    assert not proof.native.evaluate_v01(material)['checks'][0]['healthy']

def test_testflix_wrong_history_recording_review_v01(saved_testflix):
    exp=saved_testflix['experience']
    foreign=proof.feedback.g35_record_from_plain_v01(exp['after']['current_review'])
    with pytest.raises(ValueError):
        proof.validate_recording_review_v01(exp['snapshot'],foreign)
