"""Independent arithmetic and history boundary controls."""
from fractions import Fraction
import pytest
from hedgehog import outcome_calibration_v01 as cal
from tests.test_gate3_current_advisory_v01 import retained_stream, predictive_stream


def test_g34_prior_integer_boundary_oracle():
    for base in (0,1,670000000,700000000,cal.Q):
        for prior in (-cal.Q,-176025391,-1,0,1,176025391,cal.Q):
            expected=max(0,min(cal.Q,base+round(Fraction(250000000*prior,cal.Q))))
            assert cal.adjusted_avf_score_v01(base,prior)==(expected,round(Fraction(expected*1000000,cal.Q)))
    for base,prior in ((True,0),(0,False),(1.0,0),(0,cal.Q+1)):
        with pytest.raises(ValueError): cal.adjusted_avf_score_v01(base,prior)


def test_g34_closed_prior_boundary_64_and_reference_idempotence():
    from tests.test_outcome_calibration_v01 import _reference_event
    corpus,source,value,event=_reference_event()
    now=corpus['explicit_times']['timestamp']
    prior=cal.fold_avf_history_prior_v01((event,)*256,evaluated_at=now)
    assert prior.to_plain_data()['effective_count']==1
    with pytest.raises(ValueError):cal.fold_avf_history_prior_v01((event,)*257,evaluated_at=now)
    body=prior.to_plain_data()
    # Shape boundary only: this is not 64 native executions or a trusted fold.
    body.update(accepted_occurrence_ids=['reference:'+str(i) for i in range(64)],effective_count=64,
        positive=64,negative=0,sample_state='WARM')
    def value_of(data):
        data=dict(data);data['prior_id']=cal._identity('g34_avf_prior_v01',{k:v for k,v in data.items() if k!='prior_id'})
        return cal.AVFHistoryPriorV01(cal._canonical(data))
    shape=value_of(body)
    assert cal.validate_avf_prior_against_sources_v01(shape,events=(event,),evaluated_at=now)
    for changed in (dict(body,effective_count=65,positive=65),dict(body,effective_count=True),dict(body,sample_state='COLD'),
        dict(body,accepted_occurrence_ids=['duplicate']*64),dict(body,prior_fp=1.0),dict(body,source_profile='unknown')):
        with pytest.raises(ValueError):value_of(changed)
    assert not cal.validate_avf_prior_against_sources_v01(prior,events=(event,)*256,evaluated_at=now)


def _owner_relation(stream,head):
    import hashlib,json
    from hedgehog import outcome_feedback_consumer_v01 as con
    old,new=stream[:2];a=json.loads(old.feedback_canonical);b=json.loads(new.feedback_canonical)
    value=dict(profile='G34_CONTROLLED_HISTORY_OWNER_REPLACEMENT_V01',old_event=a['feedback_id'],new_event=b['feedback_id'],
        old_source_sha256=hashlib.sha256(old.source_canonical).hexdigest(),new_source_sha256=hashlib.sha256(new.source_canonical).hexdigest(),
        old_occurrence=a['observation_id'],new_occurrence=b['observation_id'],old_claim=a['gt_advice_ref'],new_claim=b['gt_advice_ref'],
        root=a['local_root_scope_id'],history_key=a['avf_history_key'],subject=a['advisory_subject_key'],predecessor=head,
        reason='Use the second predeclared correlated-input trial as the controlled comparison representative; retain the first in audit. Both failed.',
        scope='ONE_DECLARED_CONTROLLED_COMPARISON_NOT_MEASUREMENT_CORRECTION')
    value['instruction_id']=con.identity('owner_correction',value)
    return value


@pytest.fixture(scope='module')
def correction_case(retained_stream):
    import json
    from hedgehog import outcome_feedback_history_v01 as h,outcome_feedback_consumer_v01 as con
    f=retained_stream;stream=tuple(f['events']);now=max(__import__('time').time_ns()//10**9,max(json.loads(e.feedback_canonical)['timestamp'] for e in stream))
    store=h.OutcomeHistoryV01(f['directory']/'independent_correction',trusted_events=stream)
    a=json.loads(stream[0].feedback_canonical);b=json.loads(stream[1].feedback_canonical)
    snapshot,review=store.prepare_v01([a['feedback_id']],expected_head=None,evaluated_at=now)
    head=store.commit_v01(snapshot,review,expected_head=None)
    relation=_owner_relation(stream,head);raw=con.canonical(relation)
    (f['directory']/'independent_history_owner_instruction.json').write_bytes(raw)
    trusted=h.OutcomeHistoryV01(store.directory,trusted_events=stream,trusted_corrections=(raw,))
    changed,decision=trusted.prepare_v01([b['feedback_id']],expected_head=head,evaluated_at=now,
        corrections=((a['feedback_id'],b['feedback_id'],relation['reason']),))
    before=(store.directory/'epochs'/(head['snapshot_id']+'.json')).read_bytes()
    final=trusted.commit_v01(changed,decision,expected_head=head)
    assert changed.to_plain_data()['prior']['prior_fp']==snapshot.to_plain_data()['prior']['prior_fp']<0
    assert (store.directory/'epochs'/(head['snapshot_id']+'.json')).read_bytes()==before
    reopened=h.OutcomeHistoryV01(store.directory,trusted_events=stream,trusted_corrections=(raw,))
    assert reopened.read_v01(final['snapshot_id'])['snapshot']==changed.to_plain_data()
    (f['directory']/'accepted_controlled_correction.json').write_text(json.dumps(dict(instruction=relation,old_head=head,new_head=final,
        snapshot=changed.to_plain_data(),review=con.review_to_plain_v01(decision)),sort_keys=True)+'\n')
    return dict(stream=stream,now=now,head=head,final=final,relation=relation,raw=raw,directory=store.directory)


def test_g34r_independent_correction_reopen_and_once(correction_case):
    import json
    from hedgehog import outcome_feedback_history_v01 as h
    f=correction_case;rel=f['relation']
    trusted=h.OutcomeHistoryV01(f['directory'],trusted_events=f['stream'],trusted_corrections=(f['raw'],))
    with pytest.raises(ValueError):
        trusted.prepare_v01([rel['new_event']],expected_head=f['final'],evaluated_at=f['now'],
            corrections=((rel['old_event'],rel['new_event'],rel['reason']),))
    untrusted=h.OutcomeHistoryV01(f['directory'],trusted_events=f['stream'])
    with pytest.raises(ValueError,match='independent_correction_required'):untrusted.read_v01(f['final']['snapshot_id'])
    assert trusted.read_v01(f['final']['snapshot_id'])['snapshot']['corrections'][0]['instruction_id']==rel['instruction_id']


@pytest.mark.parametrize('variant',['unrelated_positive','rehash_relation','old_source','new_source','predecessor','root','scope'])
def test_g34r_correction_relation_neighbors(correction_case,tmp_path,variant):
    from copy import deepcopy
    import json,shutil
    from hedgehog import outcome_feedback_history_v01 as h,outcome_feedback_consumer_v01 as con
    f=correction_case;value=deepcopy(f['relation'])
    shutil.copytree(f['directory'],tmp_path/'history')
    (tmp_path/'history/HEAD.json').write_bytes(con.canonical(f['head']))
    trusted=h.OutcomeHistoryV01(tmp_path/'history',trusted_events=f['stream'],trusted_corrections=(f['raw'],))
    if variant=='unrelated_positive':value['new_event']=json.loads(f['stream'][3].feedback_canonical)['feedback_id']
    elif variant=='rehash_relation':value['reason']='A rehashed candidate does not grant an independent instruction.'
    elif variant in ('old_source','new_source'):value[variant+'_sha256']='0'*64
    elif variant=='predecessor':value['predecessor']=dict(f['head'],snapshot_id='0'*64)
    elif variant=='root':value['root']='foreign:root'
    else:value['scope']='foreign:scope'
    value['instruction_id']=con.identity('owner_correction',{k:v for k,v in value.items() if k!='instruction_id'})
    if variant in ('old_source','new_source','root','scope'):
        with pytest.raises(ValueError):h.OutcomeHistoryV01(tmp_path/'history',trusted_events=f['stream'],trusted_corrections=(con.canonical(value),))
    elif variant=='predecessor':
        other=h.OutcomeHistoryV01(tmp_path/'history',trusted_events=f['stream'],trusted_corrections=(con.canonical(value),))
        with pytest.raises(ValueError):other.prepare_v01([value['new_event']],expected_head=f['head'],evaluated_at=f['now'],
            corrections=((value['old_event'],value['new_event'],value['reason']),))
    else:
        with pytest.raises(ValueError):trusted.prepare_v01([value['new_event']],expected_head=f['head'],evaluated_at=f['now'],
            corrections=((value['old_event'],value['new_event'],value['reason']),))
    good=f['relation'];snapshot,review=trusted.prepare_v01([good['new_event']],expected_head=f['head'],evaluated_at=f['now'],
        corrections=((good['old_event'],good['new_event'],good['reason']),))
    assert snapshot.to_plain_data()['corrections'][0]['instruction_id']==good['instruction_id'] and review[2].decision=='ACCEPT'
