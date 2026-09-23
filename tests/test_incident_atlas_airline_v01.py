"""Saved actual Airline evidence and coherent contextual mutation controls."""
import copy
import json
import os
from pathlib import Path
import pytest
from hedgehog.domains.airline import incident_atlas_v01 as atlas
from hedgehog import outcome_feedback_v01 as feedback, outcome_feedback_consumer_v01 as consumer
from hedgehog.incident_atlas_v01 import digest_v01


@pytest.fixture(scope='module')
def saved_airline():
    path=os.environ.get('AT2_SAVED_AIRLINE')
    assert path, 'Use actual retained evidence; this fixture never collects runtime.'
    return json.loads(Path(path).read_bytes())


def test_airline_complete_saved_proof_v01(saved_airline):
    assert atlas.validate_airline_v01(saved_airline)


def test_airline_A1_known_offer_and_lawful_neighbor_v01(saved_airline):
    bad,good=(feedback.g35_record_from_plain_v01(saved_airline[k]) for k in ('bad','good'))
    assert bad.final_status==atlas.r.STATUS_FAIL_CLOSED and bad.hold_packet is None
    assert bad.proposal.recommended_offer_id==atlas.b.OFFER_C_ID
    assert good.final_status==atlas.r.STATUS_LOCAL_MODEL_PASS
    assert good.root_selected_offer_id==atlas.b.OFFER_A_ID==good.hold_contract_offer_id
    assert good.corridor_execution_count==0


def test_airline_A2_actual_foreign_root_refusal_v01(saved_airline):
    reads=saved_airline['reads'];atlas.validate_reads_v01(reads)
    assert reads['foreign_internal'][0] and reads['local'][0] and not reads['transferred'][0]
    assert len({r['contract']['root'] for r in reads['rows']})==3


def test_airline_A3_genuine_wrong_offer_v01(saved_airline):
    good,other=(feedback.g35_record_from_plain_v01(saved_airline[k]) for k in ('good','other'))
    assert atlas.r.validate_airline_semantic_causal_run_report_v01(other)[0]
    selection=atlas.b.build_selection_input_v01(atlas.b.build_valid_airline_bsep_projection_ref_v01(),atlas.b.build_client_constraints_preference_a_v01(),atlas.b.build_airline_candidate_snapshot_v01())
    assert atlas.b.validate_client_root_offer_selection_decision_v01(selection,other.canonical_evidence,good.client_root_decision).validation_status=='FAIL_CLOSED'
    assert atlas.b.validate_client_root_offer_selection_decision_v01(selection,good.canonical_evidence,good.client_root_decision).validation_status=='PASS'


def test_airline_A4_actual_read_and_privacy_v01(saved_airline):
    reads=saved_airline['reads'];row=reads['rows'][0]
    assert row['before']==row['after'] and row['receipt'] is None and row['decision']!='ACCEPT'
    assert reads['final']['reads']==3 and reads['final']['writes']==0
    client=reads['specification']['contracts'][0]['task']
    assert reads['final']['context_by_task'][client]==[reads['specification']['objects']['offer:public']]
    assert reads['specification']['objects']['traveler:private'] not in reads['final']['context_by_task'][client]


def test_airline_actual_history_changes_consumed_work_v01(saved_airline):
    exp=saved_airline['experience']
    assert exp['before']['projection']['selected']=='constraint'
    assert exp['after']['projection']['selected']=='provenance'
    assert exp['observation']['output']['checks'][0]['healthy'] is False
    assert exp['after']['output']['checks'][0]['healthy'] is True
    assert exp['after']['additional'] is not None
    assert exp['snapshot']['prior']['effective_count']==1
    assert saved_airline['consumption']['work_artifact_ref']==exp['after']['artifact']['artifact_id']


def test_airline_wrong_consumer_reference_v01(saved_airline):
    value=copy.deepcopy(saved_airline)
    value['consumption']['work_artifact_ref']=value['experience']['observation']['artifact']['artifact_id']
    with pytest.raises(ValueError,match='atlas_airline_consumed_result_reference'):
        atlas.validate_airline_v01(value)


def test_airline_coherent_advisory_number_v01(saved_airline):
    value=copy.deepcopy(saved_airline['experience']['after'])
    p=value['projection'];p['rows'][0]['adjusted_fp']+=1
    p['projection_id']=consumer.identity('advisory',{k:v for k,v in p.items() if k!='projection_id'})
    with pytest.raises(ValueError,match='atlas_airline_applied_history'):
        atlas.validate_current_projection_v01(value,saved_airline['experience']['snapshot'],saved_airline['experience']['head'])


def test_airline_genuine_foreign_descent_review_v01(saved_airline):
    value=copy.deepcopy(saved_airline['experience']['after'])
    value['discovery']['review']=consumer.review_to_plain_v01(feedback.g35_record_from_plain_v01(saved_airline['experience']['recording_review']))
    with pytest.raises(ValueError,match='atlas_airline_current_descent_review'):
        atlas.validate_current_projection_v01(value,saved_airline['experience']['snapshot'],saved_airline['experience']['head'])


def test_airline_equivalent_positive_after_mutations_v01(saved_airline):
    assert atlas.validate_airline_v01(json.loads(json.dumps(saved_airline)))
