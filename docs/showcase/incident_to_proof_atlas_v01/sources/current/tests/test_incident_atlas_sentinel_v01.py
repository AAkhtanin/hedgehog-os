"""Focused contextual controls on preserved native AT5 execution, never recollection."""
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from hedgehog import outcome_feedback_v01 as f
from hedgehog.domains.landslide_sentinel import incident_atlas_proof_v01 as proof
from hedgehog.domains.landslide_sentinel import contracts_v01 as c, events_v01 as events, semantic_adapter_v01 as sem
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode
from hedgehog.domains.landslide_sentinel.incident_atlas_v01 import fixture_v01


@pytest.fixture(scope='module')
def saved():
    path=os.environ.get('AT5_SAVED_SENTINEL')
    assert path,'AT5_SAVED_SENTINEL required; no implicit collector'
    return json.loads(Path(path).read_bytes())


def context(snapshot):
    cap=events.CapabilityState(snapshot['capabilities']['profile'])
    cap.site_online=snapshot['capabilities']['site_cloud_available'];cap.revision=snapshot['capabilities']['revision']
    book=proof.book_v01(snapshot)
    return SimpleNamespace(root=snapshot['root'],contract=snapshot['policy'],tick=snapshot['tick'],book=book,capabilities=cap,fixture=fixture_v01(),
        frames=[events.compatibility(v) for v in book.latest.values() if v['value'] is not None])


def test_at5_correct_copy_and_native_neighbors(saved):
    value=copy.deepcopy(saved)
    proof.freshness_v01(value,value['native']);proof.correlation_v01(value,value['native'])
    proof.continuation_v01(value,value['native']);proof.actions_v01(value)
    assert value==saved


def test_at5_fresh_delivery_cannot_refresh_stale_event(saved):
    n=saved['n1'];source=context(n['before']);claim=copy.deepcopy(n['controlled_claim'])
    sem.validate_bound(claim)
    with pytest.raises(ValueError,match='semantic_stale_local_measurement'):ControlledEpisode.role_material(source,claim)
    assert all(v['received']==source.tick and source.tick-v['observed_end']>c.POLICY['max_local_age_seconds']
        for v in claim['context']['sources'].values() if 'observation_id' in v)
    assert ControlledEpisode.role_material(context(n['neighbor']['snapshot']),n['neighbor']['semantic'])


def test_at5_actual_independence_and_redelivery(saved):
    n=saved['n2'];book=proof.book_v01(n['before']);history=copy.deepcopy(book.history)
    book.ingest(n['redelivery']*2,book.tick)
    assert book.history==history and len({v['lineage'] for v in n['redelivery']})==1
    assert not c.observability(n['work']['material'])['hard_critical']
    assert c.observability(saved['continuation']['positive']['material'])['hard_critical']


@pytest.mark.parametrize('variant',['late_context','old_policy','old_calibration'])
def test_at5_valid_semantics_wrong_current_context(saved,variant):
    v=saved['continuation'];claim=copy.deepcopy(v['late']['old_semantic']);source=context(v['before'])
    sem.validate_bound(claim)
    if variant=='late_context':source=context(v['waiting']);reason='role_current_context'
    elif variant=='old_policy':source.contract=dict(source.contract,version='sentinel.policy.changed');reason='role_current_root_policy'
    else:source.contract=dict(source.contract,calibration='calibration:sentinel:v02');reason='role_current_root_policy'
    with pytest.raises(ValueError,match=reason):ControlledEpisode.role_material(source,claim)


@pytest.mark.parametrize('variant',['off_checks','recovery_span','budget_reset','pending_returned','consumed_work','consumed_material'])
def test_at5_contextual_supplied_poison(saved,variant):
    v=copy.deepcopy(saved);row=v['continuation']
    if variant=='off_checks':row['late']['derived_checks']['measured_clearance']=True;reason='off_checks_must_come_from_sources'
    elif variant=='recovery_span':row['recovery'][-1]['assessment']['measured_spans']['reserve']=29;reason='measured_recovery'
    elif variant=='budget_reset':row['waiting']['budgets']['optional_context']['spent']=0;reason='pending_budget_preserved'
    elif variant=='pending_returned':row['waiting']['pending_return']=copy.deepcopy(row['joined']['pending_return']);reason='same_pending_episode'
    elif variant=='consumed_work':row['consumption']['claim']['selected_result_ref']=v['experience']['values']['before']['work']['artifact']['artifact_id'];reason='consumed_selected_work'
    else:row['consumption']['material']['tick']+=1;row['consumption']['claim']['current_input_sha256']=c.digest(row['consumption']['material']);reason='consumed_selected_work'
    with pytest.raises(ValueError,match=reason):proof.continuation_v01(v,v['native'])


def test_at5_reidentified_false_feedback(saved):
    exp=saved['experience'];bad=copy.deepcopy(exp['feedback'])
    bad['proposal_assessment']='CORRECT'
    bad['feedback_id']=f._identity('g3_feedback_v01',{k:v for k,v in bad.items() if k!='feedback_id'})
    altered=f.OutcomeFeedbackEnvelopeV01(c.canonical(bad))
    reasons=f.validate_outcome_feedback_against_sources_v01(altered,
        source_bundle=f.PredictiveOutcomeSourceContextV01(c.canonical(exp['source'])),profile=f.PREDICTIVE_SOURCE_PROFILE_ID)
    assert reasons==('g31_feedback_source_mismatch',)


def test_at5_changed_effective_prior_rejected(saved):
    exp=copy.deepcopy(saved['experience']);value=exp['values']['after']
    value['projection']['rows'][0]['prior_fp']=0
    from hedgehog import outcome_feedback_consumer_v01 as con
    value['projection']['projection_id']=con.identity('advisory',{k:v for k,v in value['projection'].items() if k!='projection_id'})
    with pytest.raises(ValueError):proof.current_work_v01(value,exp,native=saved['native'],learned=True,extra=exp['values']['after_check'])


def test_at5_current_source_requires_recorded_intake(saved):
    exp=saved['experience'];ctx=exp['values']['after']['contract']['context']
    original=proof.saved_current_source_v01(ctx,exp,saved['native'])
    assert c.canonical(original)==c.canonical(exp['values']['after']['work']['source'])
    foreign={'roots':[row for row in saved['native']['roots'] if row[2]['fields']['transaction_id']!=ctx['transaction']]}
    with pytest.raises(ValueError,match='saved_intake_missing'):proof.saved_current_source_v01(ctx,exp,foreign)
    assert proof.saved_current_source_v01(ctx,exp,saved['native'])==original


def test_at5_native_receipt_source_binding(saved):
    altered=copy.deepcopy(saved)
    altered['native']['prepared'][0]['fact']['stable_sources_marker']='controlled:foreign'
    with pytest.raises(ValueError,match='action_source'):proof.actions_v01(altered)


def test_at5_counts_and_historical_limits(saved):
    assert saved['new_provider_calls']==0
    assert saved['counts']['mock_effect']==3 and saved['counts']['signal_effect']==2
    assert saved['counts']['report_effect']==1 and saved['counts']['public_D']==saved['counts']['public_E']==0
    assert saved['experience']['feedback_samples']==1
    assert saved['continuation']['worker_joined'] and saved['continuation']['optional_profile']=='CONTROLLED_BARRIER_STUB'
