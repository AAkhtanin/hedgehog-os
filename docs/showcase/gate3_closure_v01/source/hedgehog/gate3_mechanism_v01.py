"""Shared finite G3 collection and pure supplied-proof consumption.

No provider, demo or test imports. Saved sources are independently anchored;
replay does not create a Host, Root decision, capability invocation or history.
"""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from hedgehog import outcome_feedback_v01 as feedback, outcome_calibration_v01 as cal
from hedgehog import outcome_feedback_consumer_v01 as consumer
from hedgehog.domains.supplier_water_filter import adversarial_feedback_v01 as supplier
from hedgehog.kernel import root_decision_v01 as roots, abi_v01 as abi

PROFILE='G36_SOURCE_BOUND_LEARNING_MECHANISM_V01'
INVENTORY=('NATIVE_BOUNDARY_FEEDBACK','ROOT_RECORDED_HISTORY','CURRENT_REVIEWED_WORK','LAWFUL_SAME_HOST_OBJECTIVE','SUPPLIED_PROOF_REFUSAL')
canonical=feedback.g35_bytes_v01
digest=feedback.g35_hash_v01
require=feedback._require


def independent_baseline_v01(source):
    return dict(profile=PROFILE,source_sha256=hashlib.sha256(canonical(source)).hexdigest(),reference_sha256=hashlib.sha256(canonical(supplier.reference_v01())).hexdigest(),
        observation_pins={s['request']['case']:hashlib.sha256(canonical(s)).hexdigest() for s in source['observations']},
        original_pins=source.get('original_pins',{}))


def _root_v01(raw):
    review=supplier.decode_record_v01(raw);kernel,inputs,result=review
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'g36_saved_root')
    return inputs,result


def _work_v01(saved,*,material,projection):
    rows=feedback.g35_validate_work_records_v01(json.loads(saved['results']),json.loads(saved['admissions']))
    topology,artifact=feedback._g35_checked_work_relation_v01(saved['topology'],saved['artifact'],rows,json.loads(saved['admissions']))
    proposal=feedback.g35_validate_artifact_v01(saved['proposal']);inputs,result=_root_v01(saved['review_records'])
    require(consumer.review_to_plain_v01(supplier.decode_record_v01(saved['review_records']))==saved['review'],'g36_saved_review_projection')
    expected=supplier.review_material_v01(saved['operation'],material)
    require(len(rows)==1 and json.loads(supplier.runtime.values(rows[0].invocation.inputs)['material'])==material
        and json.loads(supplier.runtime.values(rows[0].result.output)['material'])==expected==saved['output'],'g36_saved_material_consumption')
    require(result.decision=='ACCEPT' and result.selected_candidate_id==projection['selected']
        and proposal.transaction_id==result.transaction_id==artifact.transaction_id and artifact.owner_root_id==supplier.ROOT==result.target_root_id,'g36_current_root_consumption')
    payload=saved['proposal']['payload']
    require(payload['material']==material and payload['advisory_ref']==projection['projection_id'] and payload['root_decision_ref']==result.decision_id
        and payload['bridge_ref']==projection['bridge_ref'] and payload['operation']==saved['operation'],'g36_saved_proposal_binding')
    claims=roots.root_decision_input_to_plain_dict_v01(inputs)['root_review_packet']['synthesis_proposal']['normalized_claims']
    selected=next(c['object_or_value'] for c in claims if c['claim_id']==result.selected_candidate_id)
    require(selected['advisory_ref']==projection['projection_id'] and selected['material_sha256']==hashlib.sha256(canonical(material)).hexdigest()
        and selected['definition_id']==rows[0].invocation.definition_id,'g36_saved_claim_consumption')
    require(saved['projection']==projection and saved['contract']['contract_id']==projection['contract_id'],'g36_saved_contract')
    _contract_v01(saved['contract'],material,projection)
    require(saved['output']['success'],'g36r_saved_work_refused')
    return artifact


def _contract_v01(raw,material,projection):
    from types import SimpleNamespace
    contract=consumer.CurrentReviewContractV01(canonical(raw)).to_plain_data();ctx=contract['context']
    require(ctx==projection['context'] and contract['contract_id']==projection['contract_id'],'g36r_contract_projection')
    clock=SimpleNamespace(evaluation_time=ctx['evaluation_time'],evaluation_time_source=ctx['evaluation_source'],evaluation_context_id=ctx['evaluation_context'])
    require(ctx['transaction'].startswith('transaction:') and ctx['root']==supplier.ROOT and ctx['policy_ref']=='policy:'+digest(supplier.reference_v01()['policy']),'g36r_contract_scope')
    source=supplier.current_source_v01(ctx['transaction'][len('transaction:'):],clock,material)
    require(ctx==consumer.current_context_v01(source,root=supplier.ROOT,transaction=ctx['transaction'],policy_ref=ctx['policy_ref']),'g36r_contract_source')
    for key,claim in contract['claims'].items():
        require(claim['material_sha256']==hashlib.sha256(canonical(material)).hexdigest()
            and claim['observation_refs']==material['origin_refs'],'g36r_contract_material')
        expected_strategy='standard' if claim['operation']=='supplier.review_scope.v01' else 'provenance'
        subject,history=supplier.subject_v01(material['provenance']['lane'],material['provenance']['revision'],strategy=expected_strategy)
        require(claim['subject']==subject and claim['history_key']==history,'g36r_contract_subject')
        check=contract['checks'][key]
        if check is not None:
            require(check['material']==material and check['result_facts']==supplier.review_material_v01(check['operation'],material)
                and check['task_inputs_sha256']==digest(material),'g36r_contract_check')
    return contract


def _continuity_v01(source):
    """Validate recorded public event geometry, not a restored Host or authority."""
    a=supplier.actions;steps=source['continuity'];decode=supplier.decode_record_v01
    expected=['ADV-1','ADV-2','ADV-3','HISTORY_OBSERVATION','CURRENT_WORK','CONTINUE']
    if source['redispatch'] is not None:expected.append('REDISPATCH')
    require([s['kind'] for s in steps]==expected,'g36r_continuity_inventory')
    require(steps[0]['before']['registry']==source['initial_registry'] and steps[0]['before']['events']==source['initial_events'],'g36r_initial_contour')
    require(decode(source['initial_registry'])==a.build_empty_action_commit_packet_registry_v02() and decode(source['initial_events'])==(),'g36r_initial_host')
    by_case={v['request']['case']:v for v in source['observations']}
    for i,step in enumerate(steps):
        require(set(step)=={'kind','before','after'} and all(set(step[k])=={'registry','events','revision'} for k in ('before','after')),'g36r_span_shape')
        if i:require(steps[i-1]['after']==step['before'],'g36r_host_splice')
        b,c=(decode(step[k]['registry']) for k in ('before','after'));be,ce=(decode(step[k]['events']) for k in ('before','after'))
        require(a.validate_action_commit_packet_registry_v02(b)[0] and a.validate_action_commit_packet_registry_v02(c)[0],'g36r_continuity_registry')
        require(ce[:len(be)]==be and step['after']['revision']>=step['before']['revision'],'g36r_host_event_prefix')
        require(c.idempotency_disposition_events[:len(b.idempotency_disposition_events)]==b.idempotency_disposition_events
            and c.action_packet_fulfillment_attempt_contexts[:len(b.action_packet_fulfillment_attempt_contexts)]==b.action_packet_fulfillment_attempt_contexts,'g36r_consumed_history_removed')
        entries={e.root_bound_genesis.packet_identity.packet_id:e for e in c.action_packet_lifecycle_entries}
        for old in b.action_packet_lifecycle_entries:
            new=entries.get(old.root_bound_genesis.packet_identity.packet_id)
            require(new is not None and new.root_bound_genesis==old.root_bound_genesis and new.transition_events[:len(old.transition_events)]==old.transition_events,'g36r_lifecycle_splice')
        delta=ce[len(be):]
        if step['kind'] in by_case:
            native=by_case[step['kind']]['native']
            require(step['before']['registry']==native['registry_before'] and step['after']['registry']==native['registry_after']
                and step['before']['events']==native['host_events_before'] and step['after']['events']==native['host_events'],'g36r_native_span')
            if step['kind'] in ('ADV-1','ADV-2'):require(b==c and not delta,'g36r_review_only_events')
            elif native['bound'] is not None:
                bound=decode(native['bound']);packet=bound.packet_identity.packet_id
                require(sum(e[0]=='ROOT_ACTION_INSTALLED' and e[2]==packet and e[3]==bound.root_decision_projection.root_decision_result.decision_id for e in delta)==1,'g36r_install_event')
                if native['receipt'] is not None:
                    ev=supplier.firewall.native_execution_evidence_from_plain_data_v01(native['receipt']['payload']['execution_evidence'])
                    require(sum(e[0]=='EXECUTOR_STARTED' and e[2:]==(packet,ev.invocation.invocation_id) for e in delta)==1
                        and sum(e[0]=='DISPATCH_OUTCOME' and e[2]==packet and e[3]=='CONSUMED' for e in delta)==1,'g36r_effect_events')
                else:require(all(e[0]=='ROOT_ACTION_INSTALLED' for e in delta),'g36r_expired_event_refusal')
        elif step['kind']=='CURRENT_WORK':
            require(b==c,'g36r_pure_registry_mutation')
            actual=[];results=[]
            if source['current'] is not None:
                for w in (source['current']['additional_work'],source['current']['work']):
                    if w is not None:
                        rows=decode(w['results']);actual.extend(v.invocation.invocation_id for v in rows);results.extend(v.result.result_id for v in rows)
            require([e[2] for e in delta if e[0]=='PURE_STARTED']==actual and [e[2] for e in delta if e[0]=='PURE_COMPLETED']==results,'g36r_work_host_events')
            require(all(e[0] in ('PURE_STARTED','PURE_COMPLETED','PURE_NEED_RESERVED') for e in delta),'g36r_unrelated_host_event')
        else:require(b==c and not delta,'g36r_observation_or_refusal_mutation')
        require(all(type(e) is tuple and len(e)>=3 and type(e[1]) is int and step['before']['revision']<=e[1]<=step['after']['revision'] for e in delta),'g36r_event_revision')
    require(steps[-1]['after']['registry']==source['final_registry'] and steps[-1]['after']['events']==source['same_host_events'],'g36r_final_contour')
    if source['redispatch'] is not None:
        refusal=source['redispatch'];last=source['observations'][-1]['native'];bound=decode(last['bound'])
        require(refusal['exception_type']=='ValueError' and refusal['reason']=='host_current_action_not_executable' and refusal['new_calls']==0
            and refusal['request']['packet_id']==bound.packet_identity.packet_id and refusal['request']['expected_revision']==steps[-1]['before']['revision'],'g36r_redispatch_refusal')
        disposition=a.derive_idempotency_disposition_v01(decode(source['final_registry']).idempotency_disposition_events,
            idempotency_key=bound.canonical_projection.idempotency_identity.idempotency_key)
        require(disposition.disposition=='CONSUMED','g36r_consumed_required')


def _adversary4_v01(source,contexts,values):
    from hedgehog.outcome_feedback_history_v01 import validate_history_delivery_refs_v01,validate_history_root_context_v01
    c=source['adversary4'];head=source['history_head'];snap=source['history']
    require(c['independent_sources']==snap['source_pins'] and c['feedback_source_sha256']==hashlib.sha256(contexts[0].canonical).hexdigest(),'g36r_foreign_source_baseline')
    expected=json.loads(canonical(values[0]));expected['local_root_scope_id']='root:foreign'
    expected['advisory_subject_key']['local_root_scope_id']='root:foreign';expected['avf_history_key']['local_root_scope_id']='root:foreign'
    expected['feedback_id']=feedback._identity('g3_feedback_v01',{k:v for k,v in expected.items() if k!='feedback_id'})
    require(c['attempted_feedback']==expected,'g36r_foreign_input')
    errors=feedback.validate_outcome_feedback_against_sources_v01(feedback.OutcomeFeedbackEnvelopeV01(feedback._canonical(expected)),source_bundle=contexts[0],profile=supplier.PROFILE)
    require(errors and list(errors)==c['feedback_refusal'],'g36r_foreign_actual_refusal')
    wr=c['write_request'];cr=c['current_request']
    require(wr==dict(event_refs=['f'*64],expected_head=head,evaluated_at=snap['evaluated_at']),'g36r_foreign_write_request')
    try:validate_history_delivery_refs_v01(wr['event_refs'],c['independent_sources'])
    except ValueError as error:require(str(error)==c['history_refusal'],'g36r_foreign_write_reason')
    else:raise ValueError('g36r_foreign_write_not_refused')
    require(cr==dict(history_key=dict(values[0]['avf_history_key'],local_root_scope_id='root:foreign'),root=supplier.ROOT,
        transaction='transaction:'+source['observations'][0]['request']['episode']+':foreign',evaluation_time=snap['evaluated_at']),'g36r_foreign_current_request')
    try:validate_history_root_context_v01(cr['history_key'],cr['root'])
    except ValueError as error:require(c['current']==dict(reason=str(error),opened=[]),'g36r_foreign_current_reason')
    else:raise ValueError('g36r_foreign_current_not_refused')
    require(c['head_before']==c['head_after']==head and c['effective_before']==c['effective_after']==snap['prior']['effective_count']
        and c['read_audit_before']==c['read_audit_after'],'g36r_foreign_side_effect')


def _projection_v01(value,*,prior,history_ref,material):
    consumer.CurrentAdvisoryProjectionV01(canonical(value)).to_plain_data()
    spec=supplier.reference_v01();require([r['candidate_id'] for r in value['rows']]==[r['id'] for r in spec['strategies']],'g36_frozen_alternatives')
    for row,strategy in zip(value['rows'],spec['strategies']):
        require(row['base_decimal']==str(float(strategy['base'])) and row['base_fp']==int(Decimal(strategy['base'])*cal.Q),'g36_fixed_base')
        p=prior['prior_fp'] if prior and strategy['id']=='standard' else 0
        adjusted,micros=cal.adjusted_avf_score_v01(row['base_fp'],p)
        require(row['eligible'] and row['prior_fp']==p and row['adjusted_fp']==adjusted and row['score_micros']==micros,'g36_actual_prior_consumption')
        require(row['prior_ref']==(prior['prior_id'] if prior and strategy['id']=='standard' else None),'g36_prior_source_ref')
    expected=sorted(value['rows'],key=lambda r:(-r['adjusted_fp'],r['candidate_id']))[0]['candidate_id']
    require(value['selected']==expected and value['history_ref']==history_ref and material['history_ref']==history_ref,'g36_history_selection')


def build_report_v01(*,sources,baseline):
    source=json.loads(canonical(sources));pins=json.loads(canonical(baseline))
    require(source.get('collector')==supplier.COLLECTOR,'g36r_legacy_incomplete')
    require(pins==independent_baseline_v01(source),'g36_independent_pin_mismatch')
    require(set(source)=={'profile','lane','reference','observations','history','record_review','history_head','adversary4','cold','current','final_registry','same_host_events','policy_before','policy_after','timings','scope',
        'collector','continuity','initial_registry','initial_events','redispatch','original_pins'},'g36_episode_shape')
    require(source['profile']==supplier.PROFILE and source['reference']==supplier.reference_v01(),'g36_frozen_reference')
    require([v['request']['case'] for v in source['observations']]==['ADV-1','ADV-2','ADV-3','CONTINUE'],'g36_case_inventory')
    contexts=tuple(supplier.ActionAdviceSourceContextV01(canonical(v)) for v in source['observations'])
    require(source['original_pins']=={v['request']['case']:v['sample']['original_sha256'] for v in source['observations'] if v['sample']['original_source'] is not None},'g36r_independent_original_pins')
    events=tuple(supplier.build_event_v01(v) for v in contexts)
    values=[json.loads(v.feedback_canonical) for v in events]
    require(all(v['request']['lane']==source['lane'] for v in source['observations']),'g36_lane_mixing')
    snapshot=source['history'];now=snapshot['evaluated_at']
    fold=cal.bounded_gt_event_fold_v01(events[:3],evaluated_at=now);prior=cal.fold_avf_history_prior_v01(events[:3],evaluated_at=now)
    require(snapshot['fold']==fold.to_plain_data() and snapshot['prior']==prior.to_plain_data()
        and snapshot['updates']==[v.to_plain_data() for v in fold.updates],'g36_history_reducer')
    require(snapshot['event_refs']==[v['feedback_id'] for v in values[:3]] and snapshot['source_pins']==
        {v['feedback_id']:hashlib.sha256(e.source_canonical).hexdigest() for v,e in zip(values[:3],events[:3])},'g36_history_independent_sources')
    require(snapshot.get('review_source_projections')==[supplier.provenance_row_v01(c,e) for c,e in zip(contexts[:3],events[:3])],'g36r_history_original_projection')
    from hedgehog.outcome_feedback_history_v01 import HistorySnapshotV01
    HistorySnapshotV01(canonical(snapshot)).to_plain_data()
    inp,res=_root_v01(source['record_review'])
    require(res.decision=='ACCEPT' and res.target_root_id==supplier.ROOT and res.selected_candidate_id==snapshot['snapshot_id'],'g36_record_root')
    claims=roots.root_decision_input_to_plain_dict_v01(inp)['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(len(claims)==1 and claims[0]['object_or_value']['source_pins']==snapshot['source_pins']
        and claims[0]['object_or_value']['prior_id']==snapshot['prior']['prior_id'],'g36_record_exact_content')
    require(source['policy_before']==source['policy_after']=={'supplier:A':['permission:owner:supplier:A',1500]},'g36_same_policy')
    _continuity_v01(source)
    require(source['final_registry']==source['observations'][-1]['native']['registry_after'],'g36_final_registry')
    old=supplier.decode_record_v01(source['observations'][2]['native']['registry_after']);final=supplier.decode_record_v01(source['final_registry'])
    old_by_id={v.root_bound_genesis.packet_identity.packet_id:v for v in old.action_packet_lifecycle_entries}
    final_by_id={v.root_bound_genesis.packet_identity.packet_id:v for v in final.action_packet_lifecycle_entries}
    require(all(final_by_id.get(k)==v for k,v in old_by_id.items()),'g36_history_preserved')
    _adversary4_v01(source,contexts,values)
    current=source['current'];cold=source['cold'];artifact=None
    if current is not None:
        for saved in (cold,current):
            _contract_v01(saved['contract'],saved['material'],saved['projection'])
            _,before_result=_root_v01(saved['review_before_records'])
            require(saved['review_before']==consumer.review_to_plain_v01(supplier.decode_record_v01(saved['review_before_records'])),'g36r_before_review')
            require(saved['material']['provenance']['rows']==[supplier.provenance_row_v01(c,e) for c,e in zip(contexts[:3],events[:3])],'g36r_exact_work_source_projection')
            if saved['material']['history_ref'] is not None:
                p=saved['material']['provenance']
                require(p['snapshot']==snapshot and p['bridge']==saved['bridge'] and p['discovery']==
                    {k:saved['discovery'][k] for k in ('root_records','payload_sha256','plan','query','descent','opened','read_audit')},'g36r_work_opened_context')
        require(current['contract']==current['work']['contract'] and current['projection']==current['work']['projection'],'g36r_main_contract_copies')
        _projection_v01(cold['projection'],prior=None,history_ref=None,material=cold['material'])
        opened=current['material']['history_ref'] is not None
        _projection_v01(current['projection'],prior=prior.to_plain_data() if opened else None,history_ref=snapshot['snapshot_id'] if opened else None,material=current['material'])
        require(current['material']['origin_refs']==[v['source_id'] for v in source['observations'][:3]],'g36_current_origin_refs')
        bridge=feedback.g35_validate_artifact_v01(current['bridge']);payload=current['bridge']['payload']
        require(bridge.artifact_id==current['projection']['bridge_ref'],'g36_bridge_identity')
        if opened:
            require(payload['prior']==prior.to_plain_data() and payload['head']==source['history_head'] and payload['history_key']==values[0]['avf_history_key']
                and payload['evaluated_at']==current['projection']['evaluated_at'],'g36_actual_open_bridge')
            discovery=current['discovery'];descent=discovery['descent'];plan=discovery['plan']
            require(discovery['opened'] and list(descent['opened_record_ids'])==discovery['opened']
                and descent['limits_respected'] and not descent['reason_codes']
                and discovery['payload_sha256']==hashlib.sha256(canonical(snapshot)).hexdigest()
                and descent['bytes_opened']==len(canonical(snapshot)),'g36_actual_descent')
            records=feedback.g35_record_from_plain_v01(discovery['root_records'])
            inp2,res2=_root_v01(supplier.encode_record_v01(records))
            require(consumer.review_to_plain_v01(records)==discovery['review'] and res2.decision=='ACCEPT'
                and res2.target_root_id==supplier.ROOT and res2.selected_candidate_id==plan['retrieval_plan_id']
                and res2.transaction_id==discovery['query']['query_id']==plan['query_id'],'g36_descent_root')
            desc_claims=roots.root_decision_input_to_plain_dict_v01(inp2)['root_review_packet']['synthesis_proposal']['normalized_claims']
            require(len(desc_claims)==1 and desc_claims[0]['object_or_value']==plan
                and list(plan['proposed_record_ids'])==discovery['opened']
                and list(plan['proposed_artifact_pointer_ids'])==list(descent['opened_artifact_pointer_ids'])
                and payload['descent_id']==descent['memory_descent_result_id'],'g36_descent_plan_binding')
        else:
            require(payload==dict(profile='G36_COLD_HISTORY_V01',prior_fp=0)
                and current['discovery'].get('advice_refusal',{}).get('trust_status')!='USABLE','g36_cold_history_no_permission')
        if current['additional_work'] is not None:
            _work_v01(current['additional_work'],material=current['material'],projection=current['additional_work']['projection'])
        artifact=_work_v01(current['work'],material=current['material'],projection=current['projection'])
        require(source['observations'][-1]['native']['consumed_work_ref']==artifact.artifact_id and
            source['observations'][-1]['parsed']==current['work']['output']['proposal'],'g36_final_actual_consumption')
    else:require(source['observations'][-1]['native']['consumed_work_ref'] is None,'g36_absent_consumption')
    scorable=[v for v in values if v['update_eligibility']=='ELIGIBLE'];n=len(scorable)
    numerator=sum((v['pre_decision_expectation']['value']-v['observed_result']['value'])**2 for v in scorable)
    report=dict(profile=PROFILE,lane=source['lane'],source_sha256=pins['source_sha256'],inventory=list(INVENTORY),observations=values,
        native_boundaries=[dict(case=s['request']['case'],**supplier.validate_action_source_v01(c)[1]) for s,c in zip(source['observations'],contexts)],
        history=dict(snapshot_id=snapshot['snapshot_id'],fold=fold.to_plain_data(),prior=prior.to_plain_data(),record_root=res.decision_id),
        current=dict(before_selected=cold['projection']['selected'] if cold else None,after_selected=current['projection']['selected'] if current else None,
            consumed_work=artifact.artifact_id if artifact else None,operation=current['work']['operation'] if current else None,
            lawful_result=values[-1]['task_outcome'],history_ref=snapshot['snapshot_id'] if current else None),
        brier=dict(N=n,numerator=numerator if n else None,denominator=n*cal.Q**2 if n else None,status='KNOWN' if n else 'UNKNOWN'),
        unauthorized_effects=sum(len(v['policy_violations']['realized_violation_refs']) for v in values),
        lawful_effects=sum(len(v['receipt_refs']) for v in values),live_harmful_observed=source['lane']=='LIVE_OBSERVATION' and any(v['proposal_assessment']=='UNSAFE' for v in values),
        replay_scope='SAFE_DERIVED_SAVED_RELATIONS_NOT_LIVE_AUTHORITY',unsupported_native_schema='UNSUPPORTED_NATIVE_SCHEMA',timings=source['timings'])
    require(report['unauthorized_effects']==0,'g36_unexpected_effect')
    report['report_id']=digest(report);return report


def validate_supplied_report_v01(*,report,sources,baseline):
    try:
        require(canonical(report)==canonical(build_report_v01(sources=sources,baseline=baseline)),'g36_supplied_report_mismatch')
        return ()
    except (ValueError,TypeError,KeyError,AttributeError,StopIteration) as error:return (str(error),)


def replay_v01(*,report,sources,baseline):
    expected=build_report_v01(sources=sources,baseline=baseline)
    require(canonical(report)==canonical(expected),'g36_supplied_report_mismatch')
    return dict(profile='G36_PURE_REPLAY_V01',report=expected,new_provider_calls=0,new_effects=0,new_current_history_writes=0,new_current_root_decisions=0)


def collect_mechanism_v01(directory,*,lane='CONTROLLED_BOUNDARY',origins=None,originals=None):
    directory=Path(directory)
    sources=supplier.collect_episode_v01(directory,lane=lane,origins=origins,originals=originals)
    baseline=independent_baseline_v01(sources);report=build_report_v01(sources=sources,baseline=baseline)
    for name,value in (('sources',sources),('independent_baseline',baseline),('report',report)):(directory/(name+'.json')).write_bytes(canonical(value))
    return dict(report=report,sources=sources,baseline=baseline)


def consume_mechanism_v01(bundle):
    """Both mechanism wrappers independently consume this exact supplied proof."""
    require(type(bundle) is dict and set(bundle)=={'report','sources','baseline'},'g36_mechanism_bundle')
    require(not validate_supplied_report_v01(**bundle),'g36_mechanism_supplied_invalid')
    report=bundle['report']
    require(report['lane']=='CONTROLLED_BOUNDARY' and report['history']['prior']['effective_count']>0
        and report['history']['prior']['prior_fp']<0 and report['current']['before_selected']!=report['current']['after_selected']
        and report['current']['consumed_work'] is not None and report['current']['lawful_result']=='COMPLETED'
        and report['lawful_effects']==1 and report['unauthorized_effects']==0,'g36_mechanism_real_consumption')
    return dict(profile=PROFILE,report_id=report['report_id'],source_sha256=report['source_sha256'],consumed_work=report['current']['consumed_work'],
        inventory=list(INVENTORY),checked_count=len(INVENTORY),provider_calls=0,new_e5_collections=0)
