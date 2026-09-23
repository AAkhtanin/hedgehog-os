"""One actual three-instance G42 fixture; no historical collector imports."""
from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import time
import pytest
from hedgehog.domains.airline import gate4_reference_adapter_v01 as a
from hedgehog.gate4_strategy_reference_v01 import evaluate_reference_strategy_v01
from hedgehog.gate4_reference_contracts_v01 import digest


@pytest.fixture(scope='session')
def native_story(request,tmp_path_factory):
    # Imported by the history module too; retain one living Host-bearing fixture.
    if not hasattr(request.config,'_g42_native_story'):
        base=Path(os.environ['G42_COMMAND_DIR']) if 'G42_COMMAND_DIR' in os.environ else tmp_path_factory.mktemp('g42')
        request.config._g42_native_story=a.native_story_v42(base/'native_story',controlled_clock=True)
    return request.config._g42_native_story


def test_native_causal_strategy_and_budget(native_story):
    story=native_story; comparisons=story['summary']['comparisons']
    assert comparisons['cp_strategy']['selected']==['g40:offer:0','g40:offer:1']
    assert comparisons['cp_budget']['cold']!=comparisons['cp_budget']['warm']
    assert comparisons['cp_budget']['actual_raw_prior']<0
    for label,live in story['lives'].items():
        assert live['final'].snapshot.usage.compute_units==9
        assert live['final'].snapshot.policy==live['policy']
        assert len(live['host'].work_attempts)==9
        assert len(live['final_output']['consumed_quanta'])==7
        assert a.consume_strategy_v42(live)==live['final_output']['strategy_report']
        hold=story['evidence'][label]['hold']
        assert hold['status']=='PREPARATION_ONLY_NOT_EXECUTED'
        assert hold['packet_validation'].validation_status=='PASS'
        assert hold['resolution'].resolved_seat_characteristics==next(r.seat_characteristics for r in live['snapshot'].authoritative_offer_records if r.offer_id==hold['hold'].offer_id)


def test_native_quota_refusals_and_real_exhaustion(native_story):
    for live in native_story['lives'].values():
        controls=live['controls']
        for name in ('extra_quantum','unlisted_definition','unlisted_material','out_of_quota_ordinal','duplicate_terminal','stale_spending_revision','wrong_original_time','wrong_budget_revision'):
            assert controls[name]
        assert controls['exhaustion']['status']=='EXHAUSTED'
        assert controls['terminal_retry']=='UNCHANGED_NO_CHARGE'
        assert a.consume_strategy_v42(live)['status']=='RECOMMENDATION'


def test_native_source_and_coherent_supplied_controls(native_story):
    live=native_story['lives']['cold']; controls={}
    original=live['snapshot']
    changed=replace(original,authoritative_offer_records=tuple(replace(r,amount=r.amount+1) for r in original.authoritative_offer_records))
    changed=replace(changed,candidate_set_digest=a.binding.compute_airline_candidate_set_digest_v01(changed))
    assert a.binding.validate_airline_candidate_snapshot_v01(changed).validation_status=='PASS'
    with pytest.raises(ValueError,match='g42_native_source_changed') as error: a.consume_strategy_v42(live,snapshot=changed)
    controls['coherent_changed_price']=str(error.value)
    assert a.consume_strategy_v42(live,snapshot=replace(original))['status']=='RECOMMENDATION'
    for field,value in [('transaction_id','g4_reference:foreign_transaction'),('evaluation_time',live['clock'].evaluation_time+1)]:
        data=deepcopy(live['strategy_inputs']);data['context'][field]=value
        coherent=evaluate_reference_strategy_v01(data,independently_bound_context=data['context']).plain()
        with pytest.raises(ValueError) as error: a.consume_strategy_v42(live,report=coherent)
        controls[field]=str(error.value)
        assert a.consume_strategy_v42(live)['status']=='RECOMMENDATION'
    native_story['journal'].save('native_supplied_controls.json',controls)


def test_native_independent_consent_and_cross_root(native_story):
    live=native_story['lives']['cold']; report=a.consume_strategy_v42(live)
    mixed=a.strategy_reviews_v42(live,missing_bank_consent=True)
    assert mixed['reviews'][a.binding.BANK_ROOT_ID][2].decision=='NEEDS_USER'
    assert mixed['outcome']['outcome_status'] in ('MIXED','INCOMPLETE')
    assert a.consume_strategy_v42(live)==report
    with pytest.raises(ValueError,match='g42_local_acceptance_required'): a.prepare_hold_v42(live,mixed)
    good=native_story['evidence']['cold']['reviews']
    assert a.prepare_hold_v42(live,good)['packet_validation'].validation_status=='PASS'
    assert len(good['cross'])==2
    assert all(x.evidence_artifact_hash==a.digest_v01(live['final_artifact']) and not x.authority_transferred and not x.permission_created for x in good['cross'])
    wrong=dict(good,reviews=dict(good['reviews']));wrong['reviews'][a.binding.AIRLINE_ROOT_ID]=good['reviews'][a.ROOT]
    with pytest.raises(ValueError,match='g42_local_acceptance_required'): a.prepare_hold_v42(live,wrong)
    other=native_story['evidence']['contrast']['reviews']
    with pytest.raises(ValueError,match='g42_review_selected_binding'): a.prepare_hold_v42(live,other)
    assert a.prepare_hold_v42(live,good)['hold'].offer_id==good['offer_id']
    native_story['journal'].save('consent_cross_root_controls.json',dict(mixed=mixed,positive=good,
        wrong_role='REFUSED',other_valid_offer='REFUSED',missing_consent='NEEDS_USER_NO_CONTINUATION'))


def test_native_declared_modes_and_no_effect_catalogue(native_story):
    for live in native_story['lives'].values():
        assert live['policy'].max_model_calls==0
        assert all(entry.definition.effect_kind=='PURE' and not entry.definition.resource_refs for entry in live['catalogue'])
        assert live['final'].snapshot.usage.model_calls==0
        assert live['basis']['time_envelope']==a.plain_v01(live['proposal'])['time_envelope']
        assert live['strategy_inputs']['context']['origin']=='NATIVE_SOURCE_BOUND_G42_V01'
        assert live['budget']['mandatory'][0]['kind']=='FINAL_CONSUMER'


def test_native_fresh_exhausted_budget_and_closed_schema(native_story):
    import jsonschema
    from hedgehog.gate4_reference_contracts_v01 import reference_schema_v01,checked,G4_REFERENCE_NUMERIC_V01
    from hedgehog.gate4_pressure_budget_v01 import evaluate_reference_pressure_v01,allocate_reference_work_budget_v01
    schema=reference_schema_v01()
    validator=jsonschema.Draft202012Validator(schema)
    results={}
    for label,live in native_story['lives'].items():
        basis=a.native_basis_v42(live)
        material=json.loads(live['consumer'].inventory.final_material)
        budget=a.derive_budget_v42(live,basis,material)
        pressure=evaluate_reference_pressure_v01(budget['pressure_inputs'],profile=G4_REFERENCE_NUMERIC_V01)
        allocation=allocate_reference_work_budget_v01(pressure,current_budget_context=budget).plain()
        assert budget['spent']==budget['total']==9
        assert allocation['status']=='BUDGET_INSUFFICIENT' and allocation['rows']==[]
        assert budget['host_revision']!=live['budget']['host_revision']
        assert a.consume_strategy_v42(live)['status']=='RECOMMENDATION'
        results[label]=allocation
        for kind,value in [('strategy_input',live['strategy_inputs']),('budget',live['budget']),('allocation_report',live['allocation'])]:
            validator.validate(dict(kind=kind,value=value))
            changed=deepcopy(value);changed['context']['native_binding']['permission_granted']=True
            with pytest.raises(ValueError):checked(kind,changed)
            with pytest.raises(jsonschema.ValidationError):validator.validate(dict(kind=kind,value=changed))
        changed=deepcopy(live['budget']);changed['mandatory'][0]['catalogue_revision']='g4_reference:foreign_catalogue'
        with pytest.raises(ValueError,match='mandatory_catalogue'):
            allocate_reference_work_budget_v01(pressure,current_budget_context=changed)
    native_story['journal'].save('current_exhausted_budgets.json',results)


def test_g43_new_consumer_original_budget_and_actual_proof(native_story):
    from hedgehog.gate4_reference_contracts_v01 import ReferenceValueV01
    for live in native_story['lives'].values():
        refusals=live['controls']['constructor_refusals']
        assert set(refusals)=={'coherent_6_1','coherent_cold_prior','coherent_source_identity','coherent_feature'}
        assert all(v['reason']=='g4_reference:native_source_derived_budget' for v in refusals.values())
        output=live['final_output']
        assert output['allocation_identity']==ReferenceValueV01('allocation_report',live['allocation']).identity
        inputs={v.parameter_name:json.loads(v.value) for v in live['final'].results[-1].invocation.inputs}
        assert a.canonical_v01(inputs['allocation_proof']['basis'])==a.canonical_v01(live['basis'])
        assert inputs['allocation_proof']['allocation']==live['allocation']
        assert output['allocation_proof_sha256']==a.digest_v01(inputs['allocation_proof'])
        assert a.strategy_work_result_v42(inputs)==output


def test_g43_current_expiry_actual_consumers(native_story):
    live=native_story['lives']['cold']; clock=live['task_clock']
    original=a.canonical_v01(dict(basis=live['basis'],proposal=live['proposal'],clock=live['clock'],policy=live['policy']))
    before=a.work.inspect_work_task_v01(live['host'],task_id=live['task_id'])
    end=a.current_use_v43(live)['valid_to']
    good=native_story['evidence']['cold']['reviews']
    future=dict(good,local=deepcopy(good['local']))
    future['local'][a.ROOT]['now']=end+1
    with pytest.raises(ValueError,match='g43_review_future_or_unrelated'):a.prepare_hold_v42(live,future)
    with pytest.raises(ValueError,match='native_clock_advance'):clock.advance_v01(clock.now_v01()-1)
    clock.advance_v01(end-1)
    assert a.consume_strategy_v42(live)['status']=='RECOMMENDATION'
    current=a.prepare_hold_v42(live,good)
    assert current['current_use']['evaluation_time']==end-1
    assert all(r['now']==end-1 for r in current['current_reviews']['local'].values())
    clock.advance_v01(end)
    for consume in (lambda:a.consume_strategy_v42(live),lambda:a.prepare_hold_v42(live,good)):
        with pytest.raises(ValueError,match='g43_current_source_expired_or_future'):consume()
    clock.advance_v01(end+1)
    with pytest.raises(ValueError):a.consume_strategy_v42(live)
    assert before==a.work.inspect_work_task_v01(live['host'],task_id=live['task_id']) and len(live['host'].work_attempts)==9
    assert original==a.canonical_v01(dict(basis=live['basis'],proposal=live['proposal'],clock=live['clock'],policy=live['policy']))
    native_story['journal'].save('current_expiry_controls.json',dict(just_before=current,at_boundary='REFUSED',after='REFUSED',
        future='REFUSED',rollback='REFUSED',original_preserved=True,usage=before))


def test_g43_shorter_offer_ttl(tmp_path,native_story):
    from hedgehog.gate4_reference_runtime_v01 import TaskClockV43
    config=a.native_config_v42();config={**config,**config['source']};now=int(time.time())
    c,s,*_=a.controlled_source_v01(config,now,'g43-short-offer')
    s=replace(s,authoritative_offer_records=tuple(replace(r,ttl_seconds=120) for r in s.authoritative_offer_records))
    s=replace(s,candidate_set_digest=a.binding.compute_airline_candidate_set_digest_v01(s))
    journal=a.JournalV01(native_story['journal'].directory/'short_offer')
    store=a.history.OutcomeHistoryV01(journal.directory/'history',trusted_events=())
    live=a.start_native_v42(label='short_offer',profile='PRICE_FIRST',config=config,constraints=c,snapshot=s,store=store,journal=journal,task_clock=TaskClockV43(now))
    a.run_allocated_v42(live,journal);review=a.strategy_reviews_v42(live)
    live['task_clock'].advance_v01(now+119)
    assert a.prepare_hold_v42(live,review)['current_use']['valid_to']==now+120
    live['task_clock'].advance_v01(now+120)
    with pytest.raises(ValueError,match='g43_current_source_expired_or_future'):a.prepare_hold_v42(live,review)
    assert s.snapshot_ttl_seconds==900 and live['final'].snapshot.usage.compute_units==9
    journal.save('shorter_offer_control.json',dict(source=s,positive=now+119,refused=now+120,units=9))
