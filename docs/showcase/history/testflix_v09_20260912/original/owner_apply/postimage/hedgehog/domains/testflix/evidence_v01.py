"""Actual P01 orchestration, supplied-report validation and portable replay."""
from collections.abc import Mapping
from dataclasses import asdict, fields, is_dataclass, replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from hedgehog.drs import LocalDRS
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.kernel import semantic_work_v01 as semantic_work
from hedgehog.kernel import root_decision_v01 as roots
from hedgehog.kernel import trust_model_v01 as trust
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import semantic_adapter_v01 as semantic
from hedgehog.domains.testflix import kernel_adapter_v01 as kernel
from hedgehog.domains.testflix import lifecycle_v01 as lifecycle
from hedgehog.domains.testflix import mock_world_v01 as world


def validate_quote_v01(request, semantics, quote):
    plan = semantic.validate_semantics_v01(request, semantics)
    records = semantics['contributions']
    common = quote['common']
    artifact = common['semantic_proposal']
    payload = abi.kernel_artifact_to_plain_dict_v01(artifact)['payload']
    c.require_v01(artifact.artifact_id==semantics['semantic_ref'] and payload['selected_plan']==asdict(plan) and
        payload['semantic_contributions']==plain_value_v01(records),'semantic_artifact_binding')
    program = quote['program']
    first = next(i for i in program.candidate.items if i.work_id=='quote')
    c.require_v01({b.input_field:b.source.value.value for b in first.inputs} ==
        dict(plan_id=plan.plan_id,price_minor=plan.price_minor,period_seconds=plan.period_seconds),'quote_input_binding')
    c.require_v01(program.candidate.task_id==request.request_id and artifact.owner_root_id=='root:testflix:user','quote_task_root')
    ok,reasons = work.validate_work_program_result_v01(program,quote['results'],**common,host_map={'root:testflix:user':quote['host']},
        review_bindings=((quote['obligation'],quote['d_source'],quote['d_bundle']),))
    c.require_v01(ok,'supplied_work_result:'+repr(reasons))
    attempts = quote['host_attempts']; events = quote['host_events']
    c.require_v01(type(attempts) is tuple and attempts==quote['host'].work_attempts[:len(attempts)] and bool(attempts) and
        attempts[-1].result==quote['results'][-1].result and
        all(any(a.result==r.result and a.task_id==request.request_id for a in attempts) for r in quote['results']),
        'quote_retained_attempts')
    c.require_v01(type(events) is tuple and events==quote['host'].events[:len(events)] and bool(events) and
        events[-1][0]=='PURE_COMPLETED' and events[-1][2]==quote['results'][-1].result.result_id,'quote_retained_events')
    actual = {r.work_id:world.values_v01(r.result.output) for r in quote['results'] if r.status=='COMPLETED'}
    c.require_v01(set(actual)=={'quote','period'} and actual['quote']['plan_id']==plan.plan_id and
        actual['quote']['price_minor']==plan.price_minor and actual['period']['quote_ref']==actual['quote']['quote_ref'] and
        actual['period']['valid_to']==request.now+plan.period_seconds,'actual_quote_outcomes')
    return actual


def selection_candidate_v01(request, semantics, quote):
    values = validate_quote_v01(request,semantics,quote)
    return dict(order_id=request.order_id,device_id=request.device_id,merchant_id=request.merchant_id,
        plan_id=semantics['selected_plan'].plan_id,amount_minor=values['quote']['price_minor'],currency=request.currency,
        quote_ref=values['quote']['quote_ref'],valid_to=values['period']['valid_to'],
        semantic_ref=semantics['semantic_ref'],bsep_ref=quote['program'].candidate.bsep_ref,
        work_result_refs=[r.result.result_id for r in quote['results']],d_report_ref=quote['d_bundle'].runtime_report.report_id)


def review_user_selection_v01(request, semantics, quote):
    candidate = selection_candidate_v01(request,semantics,quote)
    identifier = c.identity_v01('purchase_selection',candidate)
    scope = candidate['amount_minor'] in request.approved_prices_minor and \
        candidate['device_id']==request.approved_device_id and candidate['order_id']==request.approved_order_id
    consent = request.purchase_consent and scope
    transaction = quote['common']['semantic_proposal'].transaction_id
    source = semantic_work.build_semantic_work_request_v01(request_id='review:'+identifier,transaction_id=transaction,
        target_root_id='root:testflix:user',runtime_topology_ref=quote['program'].topology_artifact.artifact_id,
        bounded_context_refs=(candidate['bsep_ref'],),permitted_actor_ids=('testflix:user_policy',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(request.order_id,),
        required_evidence_classes=('QUOTE_EVIDENCE',),forbidden_claims=('authority_creation',))
    evidence = semantic_work.build_evidence_binding_v01(evidence_id='binding:'+candidate['quote_ref'],
        evidence_ref=candidate['quote_ref'],evidence_class='QUOTE_EVIDENCE',source_component_id='testflix:actual_work',
        provenance_ref=quote['results'][0].result.result_id,evidence_state='PRESENT')
    claim = semantic_work.build_normalized_claim_v01(claim_id=identifier,subject=request.order_id,predicate='bounded_purchase_selection',
        object_or_value=candidate,time_envelope_ref=quote['d_source'].router_input.local_routing_snapshot.local_routing_snapshot_id,
        provenance_refs=tuple(candidate['work_result_refs']),evidence_refs=(evidence.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution = semantic_work.build_actor_contribution_v01(contribution_id='contribution:'+identifier,request_id=source.request_id,
        actor_id='testflix:user_policy',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=candidate['bsep_ref'],
        scope=request.order_id,bounded_context_refs=(candidate['bsep_ref'],),claims=(claim,),evidence_bindings=(evidence,),
        constraint_bindings=(),uncertainty_bindings=(),requested_validators=('testflix:explicit_purchase_consent',),forbidden_claims_observed=())
    review = semantic_work.build_root_review_packet_from_contributions_v01(request=source,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    kernel = roots.build_root_decision_kernel_v01()
    temporal = request.now < candidate['valid_to']
    inputs = roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id='root:testflix:user',root_review_packet=review,
        post_vv_bundle=dict(bundle_id='post_vv:'+identifier,post_vv_passed=bool(candidate['work_result_refs']),
            validated_candidate_ids=[identifier],rejected_candidate_ids=[],required_evidence_refs=[candidate['quote_ref']],
            provided_evidence_refs=[candidate['quote_ref']],hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='gt:'+identifier,candidate_ids=[identifier],selected_candidate_id=identifier,
            score_micros_by_candidate={identifier:1000000},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',actor_role='gt',
            attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=c.identity_v01('user_constraints',dict(ceiling=request.hard_ceiling_minor,prices=request.approved_prices_minor,
            device=request.approved_device_id,order=request.approved_order_id)),identity_passed=source.target_root_id=='root:testflix:user',
            scope_passed=candidate['device_id'] in request.registered_devices,hard_policy_passed=candidate['amount_minor']<=request.hard_ceiling_minor,
            allow_accept=scope,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=True,user_permission_present=consent,permission_scope_valid=scope,
            permission_ref='consent:'+request.request_id if consent else None),
        temporal_state=dict(temporal_valid=temporal,expired=not temporal,not_before_satisfied=True,time_envelope_ref=candidate['d_report_ref']),
        conflict_state=dict(material_unresolved_conflict=bool(review.conflict_set_ids),conflict_set_ids=list(review.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    c.require_v01(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'user_root_result')
    return dict(candidate=candidate,candidate_id=identifier,source=source,contribution=contribution,review=review,kernel=kernel,inputs=inputs,result=result)


def validate_user_selection_v01(selection, request, semantics, quote):
    c.require_v01(type(selection) is dict and set(selection)=={'candidate','candidate_id','source','contribution',
        'review','kernel','inputs','result'},'user_selection_shape')
    expected = selection_candidate_v01(request,semantics,quote)
    c.require_v01(selection['candidate']==expected and selection['candidate_id']==c.identity_v01('purchase_selection',expected),'user_selection_source')
    c.require_v01(not semantic_work.validate_root_review_packet_v01(request=selection['source'],contributions=(selection['contribution'],),
        packet=selection['review'],trust_profiles=trust.build_default_component_trust_profiles_v01()),'user_selection_review')
    c.require_v01(selection['contribution'].claims[0].claim_id==selection['candidate_id'] and
        semantic_work.semantic_work_to_plain_dict_v01(selection['contribution'].claims[0])['object_or_value']==expected and
        selection['contribution'].bsep_projection_ref==expected['bsep_ref'] and
        selection['source'].runtime_topology_ref==quote['program'].topology_artifact.artifact_id,'user_selection_lineage')
    c.require_v01(selection['inputs'].root_review_packet==selection['review'] and
        not roots.validate_root_decision_result_v01(kernel=selection['kernel'],decision_input=selection['inputs'],result=selection['result']),
        'user_selection_public_result')
    c.require_v01(selection['result'].target_root_id=='root:testflix:user' and selection['result'].decision=='ACCEPT' and
        selection['result'].transaction_id==quote['common']['semantic_proposal'].transaction_id and
        selection['result'].selected_candidate_id==selection['candidate_id'],'user_selection_not_accepted')
    c.require_v01(request.purchase_consent and expected['amount_minor'] in request.approved_prices_minor and
        expected['device_id']==request.approved_device_id and expected['order_id']==request.approved_order_id,'explicit_user_consent')
    return True


def payment_admission_v01(request):
    return world.admit_v01('testflix.payment.v01','root:testflix:bank',
        (('amount','DECIMAL'),('currency','TEXT'),('merchant_id','REFERENCE'),('order_id','REFERENCE')),
        (('amount_minor','INTEGER'),('currency','TEXT'),('merchant_id','REFERENCE'),('order_id','REFERENCE'),('payment_ref','REFERENCE')),
        selectors=dict(amount=('AMOUNT','amount_decimal'),currency=('CURRENCY','currency_code'),
            order_id=('BUSINESS_OBJECT_REF','business_object_ref'),merchant_id=('TARGET_RECORD','merchant_id')),targets=(request.merchant_id,))


def issuance_admission_v01(operation, target):
    base = (('candidate_ref','REFERENCE'),('user_id','REFERENCE'),('valid_from','INTEGER'),('valid_to','INTEGER'))
    extra = (('plan_id','REFERENCE'),('payment_ref','REFERENCE')) if operation=='entitlement' else (
        ('entitlement_id','REFERENCE'),('device_id','REFERENCE'),('content_id','REFERENCE'),('quality','INTEGER'))
    inputs = base+extra
    return world.admit_v01('testflix.'+operation+'.v01','root:testflix:provider',inputs,inputs+(('issuance_ref','REFERENCE'),),
        selectors=dict(candidate_ref=('BUSINESS_OBJECT_REF','business_object_ref'),user_id=('SUBJECT_RECORD','user_id')),
        targets=(target,))


def playback_admission_v01(request):
    return world.admit_v01('testflix.playback.v01','root:testflix:device',
        (('session_ref','REFERENCE'),('device_id','REFERENCE'),('content_id','REFERENCE')),
        (('session_ref','REFERENCE'),('device_id','REFERENCE'),('content_id','REFERENCE'),('playback_ref','REFERENCE'),('playback_state','TEXT')),
        selectors=dict(session_ref=('BUSINESS_OBJECT_REF','business_object_ref'),device_id=('TARGET_RECORD','device_id')),
        targets=(request.device_id,))


def closure_admission_v01(request, operation):
    c.require_v01(operation in ('stop','close'),'closure_operation')
    root = 'root:testflix:device' if operation=='stop' else 'root:testflix:provider'
    inputs = (('session_ref','REFERENCE'),('device_id','REFERENCE'),('content_id','REFERENCE'))
    return world.admit_v01('testflix.'+operation+'.v01',root,inputs,inputs+(('closure_ref','REFERENCE'),('state','TEXT')),
        selectors=dict(session_ref=('BUSINESS_OBJECT_REF','business_object_ref'),device_id=('TARGET_RECORD','device_id')),
        targets=(request.device_id,))


def device_grant_admission_v01(request):
    inputs = (('candidate_ref','REFERENCE'),('user_id','REFERENCE'),('device_id','REFERENCE'),('content_id','REFERENCE'),
        ('valid_from','INTEGER'),('valid_to','INTEGER'),('quality','INTEGER'))
    return world.admit_v01('testflix.device_grant.v01','root:testflix:device',inputs,inputs+(('issuance_ref','REFERENCE'),),
        selectors=dict(candidate_ref=('BUSINESS_OBJECT_REF','business_object_ref'),device_id=('TARGET_RECORD','device_id'),
            user_id=('SUBJECT_RECORD','user_id')),targets=(request.device_id,))


def initial_devices_v01(request):
    """Controlled local TV profile: 720p/1080p, daily device grant, at most two registrations."""
    return tuple(c.DeviceStateV01(d,request.user_id,request.now+86400,1080,(request.content_id,)) for d in request.registered_devices)


def initial_session_device_check_v01(request, entitlement, devices):
    event = c.PlaybackRequestV01(request.request_id,request.user_id,entitlement.entitlement_id,request.device_id,
        request.content_id,request.now,7200,entitlement.candidate.plan.resolution)
    return c.validate_playback_request_v01(event,entitlement,devices,(),request.now) is not None


class TestflixHandlerV01:
    """One caller-owned request history and one persistent host per local Root."""
    def __init__(self):
        self.reports = {}
        self.hosts = {}
        self.events = []
        self.entitlements = ()
        self.sessions = ()
        self.active = ()
        self.consumed_periods = ()
        self.pending = None
        self.memory_directory = TemporaryDirectory(prefix='testflix_local_drs_')
        self.drs = LocalDRS(Path(self.memory_directory.name))
        self.writeback = None
        self.now = None
        self.devices = ()
        self.quotes = ()
        self.pending_renewal = None
        self.renewal_records = []

    def handle_v01(self, request, provider=semantic.controlled_provider_v01, *, renewal_context=None):
        c.validate_request_v01(request)
        if request.request_id in self.reports:
            report = self.reports[request.request_id]
            c.require_v01(report['request']==request,'repeated_request_changed')
            validate_report_v01(report)
            return report
        continuing = bool(self.hosts)
        if continuing:
            c.require_v01(type(renewal_context) is tuple and len(renewal_context)==2,'one_active_domain_request_per_handler')
            consent,quote_fact = renewal_context
            c.validate_renewal_intent_v01(consent,self.entitlements[-1],quote_fact,self.now)
            c.require_v01(quote_fact is self.quotes[-1] and not self.active and self.pending is None and
                request==self.renewal_request_v01(consent,quote_fact), 'renewal_actual_source')
        else:
            c.require_v01(renewal_context is None,'renewal_without_history')
        start = len(world.CALLS)
        semantics = semantic.collect_semantics_v01(request,provider)
        quote = kernel.collect_quote_work_v01(request,semantics,host_pair=self.hosts['user'] if continuing else None)
        values = validate_quote_v01(request,semantics,quote)
        selection = review_user_selection_v01(request,semantics,quote)
        validate_user_selection_v01(selection,request,semantics,quote)
        plan = semantics['selected_plan']
        if continuing:
            pay = self.admission_v01('bank','payment');ent = self.admission_v01('provider','entitlement')
            session = self.admission_v01('provider','session');play = self.admission_v01('device','playback')
        else:
            pay = payment_admission_v01(request);ent = issuance_admission_v01('entitlement',request.merchant_id)
            session = issuance_admission_v01('session',request.device_id);play = playback_admission_v01(request)
            self.hosts['user'] = (quote['host'],quote['trusted'])
            bank_quote = world.admit_v01('testflix.quote.v01','root:testflix:bank',
                (('plan_id','REFERENCE'),('price_minor','INTEGER'),('period_seconds','INTEGER')),
                (('plan_id','REFERENCE'),('price_minor','INTEGER'),('period_seconds','INTEGER'),('quote_ref','REFERENCE')))
            bank_period = world.admit_v01('testflix.period.v01','root:testflix:bank',
                (('quote_ref','REFERENCE'),('period_seconds','INTEGER'),('now','INTEGER')),(('quote_ref','REFERENCE'),('valid_to','INTEGER')))
            self.hosts['bank'] = lifecycle.new_host_v01('root:testflix:bank',(pay,bank_quote,bank_period),request.now)
            self.hosts['provider'] = lifecycle.new_host_v01('root:testflix:provider',(ent,session,closure_admission_v01(request,'close')),request.now)
            self.hosts['device'] = lifecycle.new_host_v01('root:testflix:device',(play,closure_admission_v01(request,'stop'),device_grant_admission_v01(request)),request.now)
        amount = values['quote']['price_minor']
        pay_inputs = world.records_v01(dict(amount=('DECIMAL',action.normalize_legacy_decimal_v01(str(amount//100)+'.'+str(amount%100).zfill(2))),
            currency=('TEXT',request.currency),merchant_id=('REFERENCE',request.merchant_id),order_id=('REFERENCE',request.order_id)))
        prepared = lifecycle.install_v01(*self.hosts['bank'],request,pay,pay_inputs,request.order_id,request.merchant_id,
            dict(order=request.order_id,merchant=request.merchant_id,amount_minor=amount,currency=request.currency,
                quote_ref=values['quote']['quote_ref'],user_selection=selection['result'].decision_id),quote,
            dict(quote_completed=values['quote']['price_minor']==plan.price_minor,budget_allowed=amount<=request.hard_ceiling_minor,
                user_selection_accepted=validate_user_selection_v01(selection,request,semantics,quote)))
        paid = lifecycle.dispatch_v01(prepared,request.request_id)
        c.validate_payment_relationship_v01(request,plan,paid['output'])
        ec = c.EntitlementCandidateV01(request.user_id,plan,request.merchant_id,request.order_id,paid['output']['payment_ref'],
            request.now,values['period']['valid_to'],'EXPLICIT_ONLY')
        self.validate_payment_period_v01(paid['output'],ec,request)
        ent_inputs = world.records_v01(dict(candidate_ref=('REFERENCE',ec.candidate_id),user_id=('REFERENCE',request.user_id),
            valid_from=('INTEGER',ec.valid_from),valid_to=('INTEGER',ec.valid_to),plan_id=('REFERENCE',plan.plan_id),
            payment_ref=('REFERENCE',ec.payment_receipt_ref)))
        prepared = lifecycle.install_v01(*self.hosts['provider'],request,ent,ent_inputs,ec.candidate_id,request.merchant_id,
            asdict(ec),quote,dict(payment_relationship=c.validate_payment_relationship_v01(request,plan,paid['output']),
                period_bound=ec.valid_to==request.now+plan.period_seconds))
        issued_ent = lifecycle.dispatch_v01(prepared,request.request_id)
        entitlement = c.EntitlementV01(ec,issued_ent['bound'].root_decision_projection.root_decision_result.decision_id,issued_ent['receipt'].artifact_id)
        self.consumed_periods += ((ec.payment_receipt_ref,ec.user_id,ec.valid_from,ec.valid_to,entitlement.entitlement_id),)
        c.validate_entitlement_v01(entitlement,request,plan,paid['output'],issued_ent['bound'])
        if not continuing:
            self.devices = initial_devices_v01(request)
        sc = c.SessionCandidateV01(entitlement.entitlement_id,request.user_id,request.device_id,request.content_id,
            request.now,min(request.now+7200,ec.valid_to),1,plan.resolution)
        session_inputs = world.records_v01(dict(candidate_ref=('REFERENCE',sc.candidate_id),user_id=('REFERENCE',request.user_id),
            valid_from=('INTEGER',sc.valid_from),valid_to=('INTEGER',sc.valid_to),entitlement_id=('REFERENCE',sc.entitlement_id),
            device_id=('REFERENCE',sc.device_id),content_id=('REFERENCE',sc.content_id),quality=('INTEGER',sc.quality)))
        prepared = lifecycle.install_v01(*self.hosts['provider'],request,session,session_inputs,sc.candidate_id,request.device_id,
            asdict(sc),quote,dict(entitlement_valid=c.validate_entitlement_v01(entitlement,request,plan,paid['output'],issued_ent['bound']),
                device_registered=sc.device_id in request.registered_devices,session_bound=sc.valid_to<=ec.valid_to,
                device_policy=initial_session_device_check_v01(request,entitlement,self.devices)))
        issued_session = lifecycle.dispatch_v01(prepared,request.request_id)
        grant = c.SessionV01(sc,issued_session['bound'].root_decision_projection.root_decision_result.decision_id,issued_session['receipt'].artifact_id)
        c.validate_session_v01(grant,entitlement,request,issued_session['bound'])
        play_inputs = world.records_v01(dict(session_ref=('REFERENCE',grant.session_id),device_id=('REFERENCE',request.device_id),
            content_id=('REFERENCE',request.content_id)))
        basis = c.playback_basis_v01(grant,entitlement,self.devices)
        c.validate_playback_basis_v01(basis,request.now+4)
        prepared = lifecycle.install_v01(*self.hosts['device'],request,play,play_inputs,grant.session_id,request.device_id,
            asdict(basis),quote,dict(session_valid=c.validate_session_v01(grant,entitlement,request,issued_session['bound']),
                target_allowed=request.device_id in request.registered_devices,current_session=sc.valid_from<=request.now+4<sc.valid_to),
            valid_to=min(sc.valid_to,basis.valid_to,basis.device.valid_to))
        playing = lifecycle.dispatch_v01(prepared,request.request_id)
        report = dict(request=request,semantics=semantics,quote=quote,user_selection=selection,payment=paid,entitlement_issuance=issued_ent,
            entitlement=entitlement,session_issuance=issued_session,session=grant,playback=playing,
            devices=self.devices,
            role_projections={r:semantic.role_projection_v01(request,r) for r in ('user','bank','provider','device')},
            calls=tuple((kind,identifier) for kind,identifier,_ in world.CALLS[start:]))
        validate_report_v01(report)
        self.reports[request.request_id] = report
        self.now = request.now
        self.entitlements += (entitlement,)
        self.sessions += (grant,)
        self.active = (grant.session_id,)
        if not continuing:
            self.writeback = kernel.write_summary_v01(self.drs,report)
        return report

    def advance_clock_v01(self, now):
        c.require_v01(self.now is not None and type(now) is int and now>=self.now,'domain_clock')
        for _,source in self.hosts.values():
            source.advance_clock_v01(now)
        self.now = now

    def current_view_v01(self):
        return dict(entitlements=self.entitlements,sessions=self.sessions,active=self.active,
            consumed_periods=self.consumed_periods,devices=self.devices,now=self.now)

    def validate_payment_period_v01(self, payment, candidate, request):
        c.validate_payment_relationship_v01(request,candidate.plan,payment)
        c.require_v01(candidate.payment_receipt_ref==payment['payment_ref'],'payment_candidate_ref')
        c.require_v01(not any(row[0]==candidate.payment_receipt_ref and row[1]==candidate.user_id and
            row[2:4]==(candidate.valid_from,candidate.valid_to) for row in self.consumed_periods),'payment_period_already_consumed')
        return True

    def request_entitlement_from_payment_v01(self, payment_record, candidate, request):
        """The same issuance admission gate rejects consumption before another Root packet."""
        original = next(iter(self.reports.values()))
        c.require_v01(payment_record is original['payment'] and candidate==original['entitlement'].candidate,'entitlement_payment_evidence')
        return self.validate_payment_period_v01(payment_record['output'],candidate,request)

    def set_device_state_v01(self, devices):
        c.require_v01(type(devices) is tuple and 0<len(devices)<=2 and all(type(d) is c.DeviceStateV01 for d in devices), 'device_state_type')
        old = {d.device_id:d for d in self.devices}
        c.require_v01(len({d.device_id for d in devices})==len(devices) and all(d.device_id in old and
            d.user_id==old[d.device_id].user_id and type(d.valid_to) is int and type(d.max_quality) is int and d.max_quality>0 and
            type(d.permitted_content_ids) is tuple and set(d.permitted_content_ids)<=set(old[d.device_id].permitted_content_ids) for d in devices),
            'device_authoritative_scope')
        self.devices = devices
        if self.pending is not None:
            grant = self.pending['session']
            entitlement = next(e for e in self.entitlements if e.entitlement_id==grant.candidate.entitlement_id)
            basis = c.playback_basis_v01(grant,entitlement,self.devices)
            lifecycle.refresh_dependency_v01(self.pending['device'],asdict(basis),
                min(grant.candidate.valid_to,basis.valid_to,basis.device.valid_to))

    def admission_v01(self, root, operation):
        matches = tuple(a for a in self.hosts[root][0].admitted_catalogue if a.definition.operation_id=='testflix.'+operation+'.v01')
        c.require_v01(len(matches)==1,'persistent_admission')
        return matches[0]

    def history_v01(self):
        result=dict(purchase=next(iter(self.reports.values())),writeback=self.writeback,events=tuple(self.events))
        if self.quotes:
            result.update(quotes=self.quotes,renewal_records=tuple(self.renewal_records))
        validate_history_v01(result)
        return result

    def validated_periods_v01(self):
        original = next(iter(self.reports.values()))
        renewals = tuple(row for row in self.events if type(row['event']) is c.RenewalIntentV01)
        reports = validate_period_prefix_v01(original,self.writeback,renewals)
        c.require_v01(tuple(self.reports)==tuple(row['request'].request_id for row in reports) and
            all(self.reports[row['request'].request_id] is row for row in reports),'period_report_origin')
        c.require_v01(self.entitlements==tuple(row['entitlement'] for row in reports) and
            self.consumed_periods==payment_periods_v01(reports),'period_current_lineage')
        return reports,renewals

    def observe_quote_v01(self, quote):
        c.validate_provider_quote_v01(quote)
        original = next(iter(self.reports.values()))
        c.require_v01(quote.observed_at==self.now and quote.merchant_id==original['request'].merchant_id and
            quote.plan.plan_id==original['entitlement'].candidate.plan.plan_id, 'authoritative_quote_scope_time')
        c.require_v01(quote.predecessor_id==(self.quotes[-1].quote_id if self.quotes else None),'quote_predecessor')
        self.quotes += (quote,)
        if self.pending_renewal is not None:
            pending = self.pending_renewal
            evidence = dict(pending['payment']['evidence'],provider_quote=asdict(quote))
            lifecycle.refresh_dependency_v01(pending['payment'],evidence,quote.valid_to)
        return quote

    def renewal_request_v01(self, event, quote):
        original = next(iter(self.reports.values()))['request']
        c.validate_renewal_intent_v01(event,self.entitlements[-1],quote,self.now)
        return replace(original,request_id=event.request_id,order_id=event.order_id,approved_order_id=event.order_id,
            now=event.now,purchase_consent=event.explicit_consent,approved_prices_minor=(quote.plan.price_minor,),
            hard_ceiling_minor=event.consent_limit_minor,
            catalog=tuple(quote.plan if p.plan_id==quote.plan.plan_id else p for p in original.catalog))

    def prepare_renewal_v01(self, event):
        c.require_v01(self.pending_renewal is None and bool(self.quotes),'renewal_already_pending_or_quote_missing')
        original = next(iter(self.reports.values()));quote_fact = self.quotes[-1]
        request = self.renewal_request_v01(event,quote_fact)
        c.require_v01(event.now+4<self.entitlements[-1].candidate.valid_to,'renewal_preexpiry_intent')
        before = self.current_view_v01();calls = len(world.CALLS);providers = len(semantic.PROVIDER_CALLS)
        writeback,information = kernel.write_quote_summary_v01(self.drs,original,event,quote_fact)
        interpretation = dict(selected_plan=quote_fact.plan,semantic_ref=c.identity_v01('typed_renewal',
            dict(intent=asdict(event),provider_quote=asdict(quote_fact))),contributions=())
        quote_work = kernel.collect_quote_work_v01(request,interpretation,host_pair=self.hosts['bank'],root='root:testflix:bank',
            information=information,child_scopes=('scope:testflix:renewal:quote','scope:testflix:renewal:paid-period'),
            period_start=self.entitlements[-1].candidate.valid_to,
            paid_period_basis=(original['entitlement'],next(world.values_v01(v.result.output)
                for v in original['quote']['results'] if v.work_id=='quote')))
        results = {r.work_id:world.values_v01(r.result.output) for r in quote_work['results'] if r.status=='COMPLETED'}
        c.require_v01(set(results)=={'quote','period'} and results['quote']['price_minor']==quote_fact.plan.price_minor and
            results['period']['valid_to']==self.entitlements[-1].candidate.valid_to+quote_fact.plan.period_seconds,'renewal_quote_work')
        inputs = world.records_v01(dict(amount=('DECIMAL',action.normalize_legacy_decimal_v01(
            str(quote_fact.plan.price_minor//100)+'.'+str(quote_fact.plan.price_minor%100).zfill(2))),
            currency=('TEXT',quote_fact.currency),merchant_id=('REFERENCE',quote_fact.merchant_id),order_id=('REFERENCE',event.order_id)))
        evidence = dict(provider_quote=asdict(quote_fact),intent=asdict(event),paid_entitlement_id=event.entitlement_id,
            work_quote_ref=results['quote']['quote_ref'],period_start=self.entitlements[-1].candidate.valid_to,
            period_end=results['period']['valid_to'])
        payment = lifecycle.install_v01(*self.hosts['bank'],request,self.admission_v01('bank','payment'),inputs,event.order_id,
            quote_fact.merchant_id,evidence,quote_work,dict(explicit_consent=c.validate_renewal_intent_v01(event,self.entitlements[-1],quote_fact,self.now),
                quote_result_current=results['quote']['price_minor']==quote_fact.plan.price_minor,
                root_local_work=quote_work['d_bundle'].runtime_report.owning_root_id=='root:testflix:bank'),
            valid_to=quote_fact.valid_to,transaction_id=information['report'].query.query_id)
        self.pending_renewal = dict(event=event,request=request,provider_quote=quote_fact,quote_work=quote_work,
            memory_writeback=writeback,information=information,payment=payment,before=before,
            calls=tuple(world.CALLS[calls:]),provider_calls=tuple(semantic.PROVIDER_CALLS[providers:]))
        validate_pending_renewal_v01(self.pending_renewal)
        return self.pending_renewal

    def renew_v01(self, event, provider=semantic.controlled_provider_v01):
        c.require_v01(type(event) is c.RenewalIntentV01 and bool(self.quotes),'renewal_current_quote_required')
        reports,renewals = self.validated_periods_v01()
        quote = self.quotes[-1]
        request = self.renewal_request_v01(event,quote)
        c.require_v01(self.now+4>=self.entitlements[-1].candidate.valid_to,'renewal_new_period_boundary')
        before = self.current_view_v01()
        report = self.handle_v01(request,provider,renewal_context=(event,quote))
        record = dict(event=event,before=before,after=self.current_view_v01(),information=None,route=None,
            actions=tuple(report[k] for k in ('payment','entitlement_issuance','session_issuance','playback')),
            session=report['session'],calls=report['calls'],provider_calls=report['semantics']['provider_call_ledger'],
            renewal=report,provider_quote=quote)
        validate_history_event_v01(record,next(iter(self.reports.values())),self.writeback,prior_renewals=renewals)
        self.events.append(record)
        return record

    def reprice_pending_v01(self):
        c.require_v01(self.pending_renewal is not None and bool(self.quotes),'pending_renewal_required')
        pending = self.pending_renewal;quote = self.quotes[-1]
        c.require_v01(quote.predecessor_id==pending['provider_quote'].quote_id and quote.plan.price_minor!=pending['provider_quote'].plan.price_minor,
            'meaningful_current_quote_successor')
        payment = pending['payment'];clock = payment['source'].read_current_v01()
        before_calls = len(world.CALLS);providers = len(semantic.PROVIDER_CALLS)
        prior_material = kernel.delta_material_v01(pending,quote,pending['quote_work']['d_bundle'],clock.evaluation_time)
        current_baseline = kernel.revalidate_renewal_baseline_v01(pending,clock.evaluation_time)
        material = kernel.delta_material_v01(pending,quote,current_baseline['bundle'],clock.evaluation_time,
            current_capture=current_baseline['capture'])
        delta = kernel.run_quote_delta_v01(material)
        review = review_repriced_terms_v01(delta,pending,quote)
        host = payment['host'];packet = payment['bound'].packet_identity.packet_id
        inspection = hosts.inspect_current_action_v01(host,packet_id=packet,expected_revision=host.revision,
            evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
        c.require_v01(not inspection.present_executable,'repriced_old_packet_executable')
        reason = None
        try:
            lifecycle.dispatch_v01(payment,pending['event'].request_id)
        except ValueError as exc:
            if str(exc)!='host_current_action_not_executable':
                raise
            reason = str(exc)
        calls = tuple(world.CALLS[before_calls:])
        c.require_v01(reason is not None and not any(v[0]=='EXECUTOR' for v in calls),'repriced_old_packet_executed')
        record = dict(pending=pending,observed_quote=quote,prior_source_validation=prior_material['source_validation'],
            current_baseline=current_baseline,delta=delta,review=review,inspection=inspection,dispatch_reason=reason,
            registry=host.registry,current_source=clock,calls=calls,provider_calls=tuple(semantic.PROVIDER_CALLS[providers:]))
        validate_reprice_v01(record)
        self.renewal_records.append(record)
        return record

    def authorize_repriced_payment_v01(self, record):
        validate_reprice_v01(record)
        pending=record['pending'];quote=record['observed_quote'];review=record['review']
        c.require_v01(pending is self.pending_renewal and quote is self.quotes[-1] and
            quote.observed_at<=self.now<quote.valid_to, 'repriced_current_quote')
        c.require_v01(review['result'].decision=='ACCEPT' and quote.plan.price_minor<=pending['event'].consent_limit_minor,
            'repriced_explicit_consent_limit')
        request=replace(pending['request'],request_id=c.identity_v01('repriced_payment_request',
            dict(intent=pending['event'].request_id,quote=quote.quote_id)),now=self.now,
            approved_prices_minor=(quote.plan.price_minor,))
        amount=action.normalize_legacy_decimal_v01(str(quote.plan.price_minor//100)+'.'+str(quote.plan.price_minor%100).zfill(2))
        inputs=world.records_v01(dict(amount=('DECIMAL',amount),currency=('TEXT',quote.currency),
            merchant_id=('REFERENCE',quote.merchant_id),order_id=('REFERENCE',pending['event'].order_id)))
        evidence=dict(provider_quote=asdict(quote),intent=asdict(pending['event']),
            recomputation_result_ref=record['delta']['bundle'].recomputation_result.recomputation_result_id,
            accepted_terms_decision=review['result'].decision_id,paid_entitlement_id=pending['event'].entitlement_id)
        return lifecycle.install_v01(*self.hosts['bank'],request,self.admission_v01('bank','payment'),inputs,
            pending['event'].order_id,quote.merchant_id,evidence,pending['quote_work'],
            dict(explicit_consent=pending['event'].explicit_consent,within_current_limit=quote.plan.price_minor<=pending['event'].consent_limit_minor,
                current_E_terms=review['result'].decision=='ACCEPT'),valid_to=quote.valid_to,
            transaction_id=pending['information']['report'].query.query_id)

    def grant_device_v01(self, event):
        c.validate_event_v01(event)
        c.require_v01(type(event) is c.DeviceGrantRequestV01 and event.now==self.now and self.pending is None, 'device_grant_event')
        original = next(iter(self.reports.values()));old = original['request']
        reports,renewals = self.validated_periods_v01()
        c.require_v01(event.user_id==old.user_id and event.device_id in old.registered_devices and
            event.content_id==old.content_id and event.quality==1080 and event.valid_to==event.now+86400 and
            all(v['event'].request_id!=event.request_id for v in self.events), 'device_local_grant_profile')
        before = self.current_view_v01();start = len(world.CALLS);providers = len(semantic.PROVIDER_CALLS)
        candidate = c.identity_v01('device_grant_candidate',asdict(event))
        inputs = world.records_v01(dict(candidate_ref=('REFERENCE',candidate),user_id=('REFERENCE',event.user_id),
            device_id=('REFERENCE',event.device_id),content_id=('REFERENCE',event.content_id),valid_from=('INTEGER',event.now),
            valid_to=('INTEGER',event.valid_to),quality=('INTEGER',event.quality)))
        request = replace(old,request_id=event.request_id,now=event.now,device_id=event.device_id)
        prepared = lifecycle.install_v01(*self.hosts['device'],request,self.admission_v01('device','device_grant'),inputs,
            candidate,event.device_id,dict(event=asdict(event),previous_devices=[asdict(d) for d in self.devices]),original['quote'],
            dict(local_device_profile=True,registered_device=event.device_id in old.registered_devices,explicit_fresh_grant=True))
        actual = lifecycle.dispatch_v01(prepared,event.request_id)
        c.require_v01(actual['output']['candidate_ref']==candidate,'device_grant_execution_binding')
        fresh = c.DeviceStateV01(event.device_id,event.user_id,actual['output']['valid_to'],actual['output']['quality'],(actual['output']['content_id'],))
        self.devices = tuple(fresh if d.device_id==fresh.device_id else d for d in self.devices)
        record = dict(event=event,before=before,after=self.current_view_v01(),information=None,route=None,actions=(actual,),session=None,
            calls=tuple(world.CALLS[start:]),provider_calls=tuple(semantic.PROVIDER_CALLS[providers:]))
        validate_history_event_v01(record,original,self.writeback,prior_renewals=renewals)
        self.events.append(record)
        return record

    def handle_event_v01(self, event):
        c.validate_event_v01(event)
        prior_renewals = ()
        for record in self.events:
            if record['event'].request_id==event.request_id:
                c.require_v01(record['event']==event,'repeated_event_changed')
                validate_history_event_v01(record,next(iter(self.reports.values())),self.writeback,prior_renewals=prior_renewals)
                return record
            if type(record['event']) is c.RenewalIntentV01:
                prior_renewals += (record,)
        c.require_v01(bool(self.reports) and self.pending is None,'history_not_ready')
        c.require_v01(event.now==self.now,'event_current_clock')
        original = next(iter(self.reports.values()))
        reports,renewals = self.validated_periods_v01()
        c.require_v01(event.user_id==original['request'].user_id,'event_subject')
        start = len(world.CALLS); provider_start = len(semantic.PROVIDER_CALLS)
        before = self.current_view_v01()
        if type(event) is c.InformationRequestV01:
            c.require_v01(event.entitlement_id==original['entitlement'].entitlement_id,'information_period_not_supported')
            c.require_v01(original['entitlement'].candidate.valid_from<=event.now<original['entitlement'].candidate.valid_to,
                'information_period_not_current')
            info = kernel.resolve_summary_v01(drs=self.drs,writeback=self.writeback,event=event,quote=original['quote'])
            route = kernel.route_summary_v01(original,info)
            record = dict(event=event,before=before,after=self.current_view_v01(),information=info,route=route,actions=(),session=None)
        elif type(event) is c.StopPlaybackV01:
            c.require_v01(event.session_id in self.active,'session_not_active')
            grant = next(s for s in self.sessions if s.session_id==event.session_id)
            period = resolve_period_report_v01(reports,grant.candidate.entitlement_id)
            if self.events:
                self.history_v01()
            else:
                validate_report_v01(original)
            expected_sessions = (original['session'],)+tuple(row['session'] for row in self.events
                if type(row['event']) in (c.PlaybackRequestV01,c.RenewalIntentV01))
            expected_active = self.events[-1]['after']['active'] if self.events else (original['session'].session_id,)
            c.require_v01(self.sessions==expected_sessions and self.active==expected_active,
                'stop_retained_session_lineage')
            request = replace(period['request'],request_id=event.request_id,now=event.now,device_id=grant.candidate.device_id,content_id=grant.candidate.content_id)
            actions = []
            for root,operation in (('device','stop'),('provider','close')):
                inputs = world.records_v01(dict(session_ref=('REFERENCE',grant.session_id),device_id=('REFERENCE',grant.candidate.device_id),
                    content_id=('REFERENCE',grant.candidate.content_id)))
                evidence = dict(session=asdict(grant),active_session_ids=list(before['active']),
                    stop_receipt_ref=actions[0]['receipt'].artifact_id if actions else None)
                prepared = lifecycle.install_v01(*self.hosts[root],request,self.admission_v01(root,operation),inputs,grant.session_id,
                    grant.candidate.device_id,evidence,period['quote'],dict(active=grant.session_id in self.active,
                        issued_session=grant in self.sessions,stop_observed=not actions or actions[0]['output']['state']=='STOPPED'))
                actual = lifecycle.dispatch_v01(prepared,event.request_id)
                actions.append(actual)
            self.active = tuple(s for s in self.active if s!=grant.session_id)
            record = dict(event=event,before=before,after=self.current_view_v01(),information=None,route=None,actions=tuple(actions),session=grant)
        else:
            prepared = self.prepare_playback_v01(event)
            return self.dispatch_playback_v01(prepared)
        record.update(calls=tuple(world.CALLS[start:]),provider_calls=tuple(semantic.PROVIDER_CALLS[provider_start:]))
        validate_history_event_v01(record,original,self.writeback,prior_renewals=renewals)
        self.events.append(record)
        return record

    def prepare_playback_v01(self, event):
        c.require_v01(self.pending is None and self.now==event.now,'pending_or_clock')
        c.require_v01(type(event) is c.PlaybackRequestV01,'playback_event_type')
        reports,renewals = self.validated_periods_v01()
        original = resolve_period_report_v01(reports,event.entitlement_id)
        entitlement = original['entitlement']
        c.validate_playback_request_v01(event,entitlement,self.devices,self.active,self.now)
        c.require_v01(event.content_id==original['request'].content_id and event.device_id in original['request'].registered_devices,'entitlement_content_device_scope')
        c.require_v01(event.request_id not in self.reports and all(v['event'].request_id!=event.request_id for v in self.events),'fresh_request_required')
        start = len(world.CALLS);provider_start = len(semantic.PROVIDER_CALLS)
        before = self.current_view_v01()
        request = replace(original['request'],request_id=event.request_id,now=event.now,device_id=event.device_id,content_id=event.content_id)
        sc = c.SessionCandidateV01(entitlement.entitlement_id,event.user_id,event.device_id,event.content_id,event.now,
            event.now+event.ttl_seconds,1,event.quality)
        inputs = world.records_v01(dict(candidate_ref=('REFERENCE',sc.candidate_id),user_id=('REFERENCE',sc.user_id),
            valid_from=('INTEGER',sc.valid_from),valid_to=('INTEGER',sc.valid_to),entitlement_id=('REFERENCE',sc.entitlement_id),
            device_id=('REFERENCE',sc.device_id),content_id=('REFERENCE',sc.content_id),quality=('INTEGER',sc.quality)))
        evidence = dict(candidate=asdict(sc),entitlement=asdict(entitlement),devices=[asdict(d) for d in self.devices],active_session_ids=list(self.active))
        prepared = lifecycle.install_v01(*self.hosts['provider'],request,self.admission_v01('provider','session'),inputs,
            sc.candidate_id,event.device_id,evidence,original['quote'],dict(current_entitlement=self.now+4<entitlement.candidate.valid_to,
                no_active_stream=not self.active,device_policy=c.validate_playback_request_v01(event,entitlement,self.devices,self.active,self.now) is not None))
        issued = lifecycle.dispatch_v01(prepared,event.request_id)
        grant = c.SessionV01(sc,issued['bound'].root_decision_projection.root_decision_result.decision_id,issued['receipt'].artifact_id)
        inputs = world.records_v01(dict(session_ref=('REFERENCE',grant.session_id),device_id=('REFERENCE',sc.device_id),content_id=('REFERENCE',sc.content_id)))
        basis = c.playback_basis_v01(grant,entitlement,self.devices)
        c.validate_playback_basis_v01(basis,self.now+4)
        device = lifecycle.install_v01(*self.hosts['device'],request,self.admission_v01('device','playback'),inputs,
            grant.session_id,event.device_id,asdict(basis),original['quote'],
            dict(issued_session=issued['output']['candidate_ref']==sc.candidate_id,current_session=sc.valid_from<=self.now+4<sc.valid_to,
                device_policy=c.validate_playback_request_v01(event,entitlement,self.devices,self.active,self.now) is not None),
            valid_to=min(sc.valid_to,basis.valid_to,basis.device.valid_to))
        self.sessions += (grant,)
        self.pending = dict(event=event,before=before,issued=issued,device=device,session=grant,
            calls_start=start,provider_start=provider_start)
        return self.pending

    def dispatch_playback_v01(self, prepared):
        c.require_v01(prepared is self.pending,'pending_identity')
        reports,renewals = self.validated_periods_v01()
        period = resolve_period_report_v01(reports,prepared['event'].entitlement_id)
        c.require_v01(prepared['session'].candidate.entitlement_id==period['entitlement'].entitlement_id and
            prepared['issued']['evidence']['entitlement']==asdict(period['entitlement']) and
            prepared['before']['entitlements']==self.entitlements and
            prepared['before']['consumed_periods']==self.consumed_periods,'pending_period_lineage')
        event = prepared['event']
        playing = lifecycle.dispatch_v01(prepared['device'],event.request_id)
        c.require_v01(playing['output']['playback_state']=='PLAYING','playback_not_started')
        self.active += (prepared['session'].session_id,)
        record = dict(event=event,before=prepared['before'],after=self.current_view_v01(),information=None,route=None,
            actions=(prepared['issued'],playing),session=prepared['session'],calls=tuple(world.CALLS[prepared['calls_start']:]),
            provider_calls=tuple(semantic.PROVIDER_CALLS[prepared['provider_start']:]))
        validate_history_event_v01(record,next(iter(self.reports.values())),self.writeback,prior_renewals=renewals)
        self.events.append(record)
        self.pending = None
        return record


def validate_pending_renewal_v01(pending):
    c.require_v01(type(pending) is dict and set(pending)=={'event','request','provider_quote','quote_work','memory_writeback','information',
        'payment','before','calls','provider_calls'}, 'pending_renewal_shape')
    event=pending['event'];quote=pending['provider_quote'];prior=pending['before']['entitlements'][-1]
    c.validate_renewal_intent_v01(event,prior,quote,event.now)
    c.validate_request_v01(pending['request'])
    b=pending['information'];writeback=pending['memory_writeback'];q=pending['quote_work']
    c.require_v01(b['report'].source_records==(writeback['meaning'],) and
        c.canonical_v01(b['stored'])==writeback['stored_bytes'] and b['stored']==writeback['stored'] and
        b['stored']['content']['meaning']==kernel.address_api.meaning_record_to_plain_data_v01(writeback['meaning']) and
        b['answer']==dict(quote=plain_value_v01(quote),quote_id=quote.quote_id,entitlement_id=event.entitlement_id,
            user_id=event.user_id,plan=asdict(quote.plan)) and
        json.loads(writeback['meaning'].safe_summary)==b['answer'], 'pending_quote_memory_source')
    review=b['review']
    c.require_v01(kernel.reuse.validate_existing_root_shortcut_decision_v01(resolution_report=b['report'],root_kernel=review['kernel'],
        root_decision_input=review['inputs'],root_decision_result=review['result'],use_time=event.now)[0], 'pending_quote_public_B')
    c.require_v01(q['d_source'].g2c_source_context.g2b_resolution_report is b['report'] and
        q['d_source'].router_input.owning_root_id==b['report'].query.owning_local_root_id=='root:testflix:bank' and
        q['d_source'].router_input.transaction_id==b['report'].query.query_id and
        kernel.fractal.validate_fractal_runtime_execution_bundle_v02(q['d_bundle']).status=='PASS', 'pending_B_C_D_binding')
    valid,reasons=work.validate_work_program_result_v01(q['program'],q['results'],**q['common'],host_map={'root:testflix:bank':q['host']},
        review_bindings=((q['obligation'],q['d_source'],q['d_bundle']),))
    c.require_v01(valid,'pending_actual_bank_work:'+repr(reasons))
    results={r.work_id:world.values_v01(r.result.output) for r in q['results'] if r.status=='COMPLETED'}
    c.require_v01(set(results)=={'quote','period'} and results['quote']['price_minor']==quote.plan.price_minor and
        results['quote']['plan_id']==quote.plan.plan_id and results['period']['valid_to']==prior.candidate.valid_to+quote.plan.period_seconds,
        'pending_quote_result_binding')
    payment=pending['payment'];canonical=payment['bound'].canonical_projection
    expected=dict(provider_quote=asdict(quote),intent=asdict(event),paid_entitlement_id=event.entitlement_id,
        work_quote_ref=results['quote']['quote_ref'],period_start=prior.candidate.valid_to,period_end=results['period']['valid_to'])
    digest=action.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(expected))
    c.require_v01(payment['evidence']==expected and action.validate_native_root_bound_action_commit_packet_v01(payment['bound'])[0] and
        action.validate_action_commit_packet_registry_v02(payment['pending_registry'])[0] and
        canonical.transaction_id==b['report'].query.query_id and canonical.owning_local_root_id=='root:testflix:bank' and
        canonical.dependency_candidate.dependency_records[0].content_sha256==payment['observation'].observed_content_sha256==digest,
        'pending_payment_owning_root_dependency')
    c.require_v01(payment['root_review']['request'].runtime_topology_ref==q['program'].topology_artifact.artifact_id and
        payment['root_review']['review']==payment['bound'].root_decision_projection.root_decision_input.root_review_packet and
        payment['checks']==dict(explicit_consent=True,quote_result_current=True,root_local_work=True), 'pending_actual_root_review')
    amount=action.normalize_legacy_decimal_v01(str(quote.plan.price_minor//100)+'.'+str(quote.plan.price_minor%100).zfill(2))
    c.require_v01(world.values_v01(payment['inputs'])==dict(amount=amount,currency=quote.currency,merchant_id=quote.merchant_id,
        order_id=event.order_id) and canonical.temporal_authority.expires_at_utc==min(event.now+120,quote.valid_to), 'pending_native_inputs')
    c.require_v01(type(pending['calls']) is tuple and pending['provider_calls']==() and
        tuple(i for kind,i,_ in pending['calls'] if kind=='EXECUTOR')==tuple(r.result.invocation_id for r in q['results']), 'pending_no_charge_calls')
    return True


def _repriced_terms_value_v09(delta, pending, quote):
    bundle = delta['bundle']
    source = bundle.source_context.observed_source_artifacts[0]
    payload = abi.kernel_artifact_to_plain_dict_v01(source)['payload']
    c.require_v01(payload['provider_quote']==plain_value_v01(quote) and bundle.final_root_decision_result.target_root_id=='root:testflix:bank' and
        bundle.final_root_decision_result.decision=='ACCEPT','reprice_actual_quote_result')
    selected_cell = delta['material']['projections'][0][0].cell_id
    baseline = bundle.source_context.baseline_g2d_execution_bundle
    selected = next(a.artifact_id for result,a in zip(baseline.cell_results,baseline.result_artifacts,strict=True)
        if result.cell_id==selected_cell)
    bindings = tuple(v for v in bundle.recomputed_bindings if v.prior_artifact_id==selected)
    c.require_v01(len(bindings)==1 and bindings[0].g2d_runtime_report_ref==bundle.recomputed_g2d_execution_bundle.runtime_report.report_id,
        'reprice_recomputed_quote_dependency')
    recomputed=bundle.recomputed_g2d_execution_bundle
    results=tuple(v for v in recomputed.cell_results if v.result_id==bindings[0].g2d_cell_result_ref)
    c.require_v01(len(results)==1 and results[0].cell_id==selected_cell and results[0].outcome=='COMPLETED'
        and bool(results[0].accepted_output_refs),'reprice_actual_completed_result')
    context=recomputed.observed_work_context
    consumed=tuple(a for a in context.ordered_binding_artifacts
        if abi.kernel_artifact_to_plain_dict_v01(a)['payload']['source_pair']['observed_identity_ref']==source.artifact_id
        and abi.kernel_artifact_to_plain_dict_v01(a)['payload']['topology_binding']['cell_ref']==selected_cell)
    c.require_v01(len(consumed)==1,'reprice_actual_consumed_source')
    rows=tuple(q for q in recomputed.queue_entries if q.cell_id==selected_cell and q.state=='COMPLETED'
        and set(q.observed_output_refs).intersection(results[0].accepted_output_refs))
    c.require_v01(bool(rows) and all(consumed[0].artifact_id in q.observed_evidence_refs for q in rows),
        'reprice_actual_work_outputs')
    artifacts={a.artifact_id:a for a in (*recomputed.queue_artifacts,*recomputed.result_artifacts,*context.ordered_binding_artifacts)}
    terminals={a.artifact_id for q,a in zip(recomputed.queue_entries,recomputed.queue_artifacts,strict=True) if q in rows}
    reached=set();frontier=list(terminals)
    while frontier:
        identifier=frontier.pop()
        if identifier in reached:continue
        reached.add(identifier)
        if identifier in artifacts:frontier.extend(artifacts[identifier].parent_refs)
    c.require_v01(consumed[0].artifact_id in reached,'reprice_work_source_parent_chain')
    value = dict(quote_id=quote.quote_id,amount_minor=payload['provider_quote']['plan']['price_minor'],
        consent_limit_minor=pending['event'].consent_limit_minor,consent_request_id=pending['event'].request_id,
        delta_result_ref=bundle.recomputation_result.recomputation_result_id,
        recomputed_quote_ref=bindings[0].new_artifact_id,source_artifact_ref=source.artifact_id,
        recomputed_output_refs=list(results[0].accepted_output_refs),consumed_binding_ref=consumed[0].artifact_id,
        final_delta_review=bundle.final_root_decision_result.decision_id)
    return value


def review_repriced_terms_v01(delta, pending, quote):
    bundle = delta['bundle']
    c.require_v01(kernel.delta_api.validate_continuous_delta_execution_bundle_v01(bundle).status=='PASS','reprice_required_public_E')
    value = _repriced_terms_value_v09(delta, pending, quote)
    binding = next(v for v in bundle.recomputed_bindings if v.new_artifact_id == value['recomputed_quote_ref'])
    return kernel.review_information_v01(transaction=bundle.delta.transaction_id,selected=c.identity_v01('repriced_terms',value),
        subject=pending['event'].order_id,predicate='review_repriced_renewal_against_explicit_consent',value=value,
        quote=pending['quote_work'],root='root:testflix:bank',provenance_ref=binding.g2d_cell_result_ref,
        valid=value['amount_minor']<=value['consent_limit_minor'])


def validate_reprice_v01(record):
    c.require_v01(type(record) is dict and set(record)=={'pending','observed_quote','prior_source_validation','current_baseline','delta',
        'review','inspection','dispatch_reason','registry','current_source','calls','provider_calls'},'reprice_record_shape')
    pending = record['pending'];quote = record['observed_quote'];delta = record['delta'];bundle = delta['bundle']
    validate_pending_renewal_v01(pending)
    c.require_v01(kernel.delta_api.validate_continuous_delta_execution_bundle_v01(bundle).status=='PASS','reprice_public_bundle')
    for name,value in delta['arguments'].items():
        if name!='retained_profile':
            c.require_v01(getattr(bundle,name)==value,'reprice_actual_E_input:'+name)
    c.require_v01(bundle.source_context.g2a_packet is pending['payment']['bound'] and
        bundle.source_context.g2b_resolution_report is pending['information']['report'] and
        bundle.source_context.baseline_g2d_execution_bundle is record['current_baseline']['bundle'] and
        record['current_baseline']['prior_bundle'] is pending['quote_work']['d_bundle'], 'reprice_source_lineage')
    prior = pending['provider_quote']
    c.validate_provider_quote_v01(quote)
    c.require_v01(quote.predecessor_id==prior.quote_id and quote.plan.price_minor!=prior.plan.price_minor and
        prior.observed_at<quote.observed_at<=record['current_source'].evaluation_time<
            pending['payment']['bound'].canonical_projection.temporal_authority.expires_at_utc,
        'reprice_source_time')
    review = record['review']
    c.require_v01(not semantic_work.validate_root_review_packet_v01(request=review['source'],contributions=(review['contribution'],),
        packet=review['review'],trust_profiles=trust.build_default_component_trust_profiles_v01()) and
        not roots.validate_root_decision_result_v01(kernel=review['kernel'],decision_input=review['inputs'],result=review['result']),
        'reprice_current_root_review')
    claim = semantic_work.semantic_work_to_plain_dict_v01(review['contribution'].claims[0])['object_or_value']
    c.require_v01(claim==_repriced_terms_value_v09(delta, pending, quote) and
        claim['quote_id']==quote.quote_id and claim['amount_minor']==quote.plan.price_minor and
        claim['consent_limit_minor']==pending['event'].consent_limit_minor and
        claim['delta_result_ref']==bundle.recomputation_result.recomputation_result_id and
        review['result'].target_root_id=='root:testflix:bank' and
        (review['result'].decision=='ACCEPT')==(quote.plan.price_minor<=pending['event'].consent_limit_minor),'reprice_decision_binding')
    c.require_v01(not record['inspection'].present_executable and record['dispatch_reason']=='host_current_action_not_executable' and
        not any(v[0]=='EXECUTOR' for v in record['calls']) and record['provider_calls']==(),'reprice_zero_charge')
    c.require_v01(record['registry']==pending['payment']['pending_registry'],'reprice_registry_history_preserved')
    return True


def validate_report_v01(report):
    c.require_v01(type(report) is dict and set(report)=={'request','semantics','quote','payment','entitlement_issuance',
        'entitlement','session_issuance','session','playback','role_projections','calls','user_selection','devices'},'report_shape')
    request = report['request']
    c.validate_request_v01(request)
    c.require_v01(report['devices']==initial_devices_v01(request),'initial_device_source')
    quote_values = validate_quote_v01(request,report['semantics'],report['quote'])
    validate_user_selection_v01(report['user_selection'],request,report['semantics'],report['quote'])
    plan = report['semantics']['selected_plan']
    c.require_v01(report['role_projections']=={r:semantic.role_projection_v01(request,r) for r in ('user','bank','provider','device')},'root_projections')
    for key,root,operation in (('payment','bank','payment'),('entitlement_issuance','provider','entitlement'),
        ('session_issuance','provider','session'),('playback','device','playback')):
        record = report[key]
        c.require_v01(type(record) is dict and set(record)=={'bound','admitted','inputs','material','observation','evidence','checks',
            'root_review','host','source','pending_registry','registry','context','receipt','execution','output'},'action_record_shape:'+key)
        bound = record['bound']
        c.require_v01(action.validate_native_root_bound_action_commit_packet_v01(bound)[0],'native_root_binding:'+key)
        canonical = bound.canonical_projection
        c.require_v01(canonical.owning_local_root_id=='root:testflix:'+root and
            canonical.transaction_id=='transaction:'+request.request_id+':root:testflix:'+root and
            canonical.execution_source.definition.operation_id=='testflix.'+operation+'.v01','action_root_operation:'+key)
        execution = record['execution']
        c.require_v01(not firewall.validate_native_execution_evidence_v01(execution),'actual_native_execution:'+key)
        c.require_v01(execution.invocation.inputs==record['inputs'] and execution.invocation.packet_id==bound.packet_identity.packet_id and
            execution.admission==canonical.execution_source and record['output']==world.values_v01(execution.result.output), 'execution_input_output:'+key)
        receipt = record['receipt']
        payload = abi.kernel_artifact_to_plain_dict_v01(receipt)['payload']
        c.require_v01(receipt is record['context'].receipt and
            firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])==execution,'retained_receipt:'+key)
        c.require_v01(record['context'] in record['registry'].action_packet_fulfillment_attempt_contexts,'retained_attempt:'+key)
        review = record['root_review']
        c.require_v01(type(review) is dict and set(review)=={'request','contribution','review'},'root_review_shape:'+key)
        c.require_v01(not semantic_work.validate_root_review_packet_v01(request=review['request'],contributions=(review['contribution'],),
            packet=review['review'],trust_profiles=trust.build_default_component_trust_profiles_v01()),'root_review_context:'+key)
        c.require_v01(review['review']==bound.root_decision_projection.root_decision_input.root_review_packet and
            review['request'].runtime_topology_ref==report['quote']['program'].topology_artifact.artifact_id and
            review['contribution'].bsep_projection_ref==report['quote']['program'].candidate.bsep_ref,'root_bsep_work_binding:'+key)
        c.require_v01(record['material']['corridor']==record['context'].corridor and
            record['material']['corridor_step']==record['context'].corridor_step and
            record['context'].current_dependency_observations==(record['observation'],),'actual_dispatch_context:'+key)
        pending = next(v for v in record['pending_registry'].action_packet_lifecycle_entries if v.root_bound_genesis==bound)
        c.require_v01(record['material']['transition_events']==pending.transition_events and
            record['material']['disposition_event'] in record['pending_registry'].idempotency_disposition_events,'pending_evidence_binding:'+key)
        digest = action.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(record['evidence']))
        c.require_v01(canonical.dependency_candidate.dependency_records[0].content_sha256==digest,'dependency_body_binding:'+key)
        c.require_v01(firewall.snapshot_admitted_capability_v01(record['admitted'])==execution.admission,'live_admission_binding:'+key)
        replay = action.replay_action_packet_lifecycle_history_v01(record['registry'],packet_id=bound.packet_identity.packet_id)
        c.require_v01(replay.rebuilt_packet_id==bound.packet_identity.packet_id,'native_history:'+key)
        c.require_v01(payload['real_world_effects_count']==0 and payload['receipt_evidence_only'] is True and
            all(payload[k] is False for k in ('root_decision_created','future_permission_created','final_output_created','effect_handle_exposed')),
            'effect_authority_boundary:'+key)
        c.require_v01(record['inputs']==execution.invocation.inputs and world.compute_output_v01('testflix.'+operation+'.v01',record['inputs'])==execution.result.output,
            'business_output:'+key)
    paid = report['payment']
    c.validate_payment_relationship_v01(request,plan,paid['output'])
    c.require_v01(paid['evidence']['quote_ref']==quote_values['quote']['quote_ref'],'quote_payment_binding')
    c.validate_entitlement_v01(report['entitlement'],request,plan,paid['output'],report['entitlement_issuance']['bound'])
    c.validate_session_v01(report['session'],report['entitlement'],request,report['session_issuance']['bound'])
    c.require_v01(report['entitlement_issuance']['output']['candidate_ref']==report['entitlement'].candidate.candidate_id and
        report['entitlement_issuance']['output']['plan_id']==plan.plan_id and
        report['session_issuance']['output']['candidate_ref']==report['session'].candidate.candidate_id,'issued_output_binding')
    play = report['playback']
    c.require_v01(play['bound'].canonical_projection.business_object_identity.business_object_ref==report['session'].session_id and
        play['output']['session_ref']==report['session'].session_id and play['output']['device_id']==request.device_id and
        play['output']['content_id']==request.content_id and play['output']['playback_state']=='PLAYING','device_session_binding')
    ec = report['entitlement'].candidate
    sc = report['session'].candidate
    expected_inputs = {
        'payment':dict(amount=action.normalize_legacy_decimal_v01(str(plan.price_minor//100)+'.'+str(plan.price_minor%100).zfill(2)),
            currency=request.currency,merchant_id=request.merchant_id,order_id=request.order_id),
        'entitlement_issuance':dict(candidate_ref=ec.candidate_id,user_id=request.user_id,valid_from=ec.valid_from,valid_to=ec.valid_to,
            plan_id=plan.plan_id,payment_ref=ec.payment_receipt_ref),
        'session_issuance':dict(candidate_ref=sc.candidate_id,user_id=request.user_id,valid_from=sc.valid_from,valid_to=sc.valid_to,
            entitlement_id=sc.entitlement_id,device_id=sc.device_id,content_id=sc.content_id,quality=sc.quality),
        'playback':dict(session_ref=report['session'].session_id,device_id=request.device_id,content_id=request.content_id)}
    expected_evidence = {'payment':dict(order=request.order_id,merchant=request.merchant_id,amount_minor=plan.price_minor,
        currency=request.currency,quote_ref=quote_values['quote']['quote_ref'],user_selection=report['user_selection']['result'].decision_id),
        'entitlement_issuance':asdict(ec),'session_issuance':asdict(sc),
        'playback':asdict(c.playback_basis_v01(report['session'],report['entitlement'],report['devices']))}
    expected_checks = {'payment':dict(quote_completed=quote_values['quote']['price_minor']==plan.price_minor,budget_allowed=plan.price_minor<=request.hard_ceiling_minor,
        user_selection_accepted=validate_user_selection_v01(report['user_selection'],request,report['semantics'],report['quote'])),
        'entitlement_issuance':dict(payment_relationship=c.validate_payment_relationship_v01(request,plan,paid['output']),period_bound=ec.valid_to==request.now+plan.period_seconds),
        'session_issuance':dict(entitlement_valid=c.validate_entitlement_v01(report['entitlement'],request,plan,paid['output'],report['entitlement_issuance']['bound']),
            device_registered=sc.device_id in request.registered_devices,session_bound=sc.valid_to<=ec.valid_to,
            device_policy=initial_session_device_check_v01(request,report['entitlement'],report['devices'])),
        'playback':dict(session_valid=c.validate_session_v01(report['session'],report['entitlement'],request,report['session_issuance']['bound']),
            target_allowed=request.device_id in request.registered_devices,current_session=sc.valid_from<=request.now+4<sc.valid_to)}
    for key in expected_inputs:
        c.require_v01(world.values_v01(report[key]['inputs'])==expected_inputs[key] and report[key]['evidence']==expected_evidence[key],
            'domain_input_binding:'+key)
        c.require_v01(report[key]['checks']==expected_checks[key],'local_policy_binding:'+key)
    expected_invocations = {r.invocation.invocation_id for r in report['quote']['results']}
    expected_invocations.update(report[k]['execution'].invocation.invocation_id for k in ('payment','entitlement_issuance','session_issuance','playback'))
    actual_invocations = [identifier for kind,identifier in report['calls'] if kind=='EXECUTOR']
    c.require_v01(len(actual_invocations)==len(expected_invocations) and set(actual_invocations)==expected_invocations,'actual_call_ledger')
    return True


def validate_native_history_action_v01(record, original, event, root, operation):
    expected_keys = {'bound','admitted','inputs','material','observation','evidence','checks','root_review','host','source',
        'pending_registry','registry','context','receipt','execution','output'}
    c.require_v01(type(record) is dict and set(record)==expected_keys,'history_action_shape')
    bound = record['bound']; canonical = bound.canonical_projection; execution = record['execution']
    c.require_v01(action.validate_native_root_bound_action_commit_packet_v01(bound)[0],'history_native_binding')
    c.require_v01(canonical.owning_local_root_id=='root:testflix:'+root and
        canonical.transaction_id=='transaction:'+event.request_id+':root:testflix:'+root and
        canonical.execution_source.definition.operation_id=='testflix.'+operation+'.v01' and
        canonical.evaluation_time==event.now,'history_action_owner')
    c.require_v01(not firewall.validate_native_execution_evidence_v01(execution) and
        execution.invocation.inputs==record['inputs'] and execution.invocation.packet_id==bound.packet_identity.packet_id and
        execution.admission==canonical.execution_source and firewall.snapshot_admitted_capability_v01(record['admitted'])==execution.admission,
        'history_execution_binding')
    payload = abi.kernel_artifact_to_plain_dict_v01(record['receipt'])['payload']
    c.require_v01(record['context'].receipt is record['receipt'] and
        firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])==execution and
        record['context'] in record['registry'].action_packet_fulfillment_attempt_contexts,'history_receipt_binding')
    c.require_v01(record['output']==world.values_v01(execution.result.output) and
        world.compute_output_v01('testflix.'+operation+'.v01',record['inputs'])==execution.result.output,'history_output')
    review = record['root_review']
    c.require_v01(not semantic_work.validate_root_review_packet_v01(request=review['request'],contributions=(review['contribution'],),
        packet=review['review'],trust_profiles=trust.build_default_component_trust_profiles_v01()),'history_root_review')
    c.require_v01(review['review']==bound.root_decision_projection.root_decision_input.root_review_packet and
        review['request'].runtime_topology_ref==original['quote']['program'].topology_artifact.artifact_id and
        review['contribution'].bsep_projection_ref==original['quote']['program'].candidate.bsep_ref,'history_root_context')
    digest = action.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(record['evidence']))
    c.require_v01(canonical.dependency_candidate.dependency_records[0].content_sha256==digest and
        record['observation'].observed_content_sha256==digest and
        record['context'].current_dependency_observations==(record['observation'],),'history_dependency')
    c.require_v01(record['context'].corridor==record['material']['corridor'] and
        record['context'].corridor_step==record['material']['corridor_step'],'history_corridor')
    pending = next(v for v in record['pending_registry'].action_packet_lifecycle_entries if v.root_bound_genesis==bound)
    c.require_v01(pending.transition_events==record['material']['transition_events'] and
        record['material']['disposition_event'] in record['pending_registry'].idempotency_disposition_events,'history_pending')
    c.require_v01(payload['real_world_effects_count']==0 and payload['receipt_evidence_only'] is True and
        all(payload[k] is False for k in ('root_decision_created','future_permission_created','final_output_created','effect_handle_exposed')),
        'history_non_authority')
    return True


def payment_periods_v01(reports):
    return tuple((r['entitlement'].candidate.payment_receipt_ref,r['entitlement'].candidate.user_id,
        r['entitlement'].candidate.valid_from,r['entitlement'].candidate.valid_to,r['entitlement'].entitlement_id) for r in reports)


def resolve_period_report_v01(reports, entitlement_id):
    matches = tuple(row for row in reports if row['entitlement'].entitlement_id==entitlement_id)
    c.require_v01(len(matches)==1,'current_entitlement')
    return matches[0]


def validate_period_prefix_v01(original, writeback, renewals):
    c.require_v01(type(renewals) is tuple and len(renewals)<=32,'period_prefix_shape')
    reports = (original,)
    for index,row in enumerate(renewals):
        c.require_v01(type(row) is dict and type(row.get('event')) is c.RenewalIntentV01,'period_prefix_kind')
        validate_history_event_v01(row,original,writeback,prior_renewals=renewals[:index])
        reports += (row['renewal'],)
    c.require_v01(len({r['entitlement'].entitlement_id for r in reports})==len(reports) and
        len({r['entitlement'].candidate.payment_receipt_ref for r in reports})==len(reports),'period_prefix_unique')
    return reports


def validate_history_event_v01(record, original, writeback, *, prior_renewals=()):
    reports = validate_period_prefix_v01(original,writeback,prior_renewals)
    entitlements = tuple(row['entitlement'] for row in reports)
    periods = payment_periods_v01(reports)
    if type(record) is dict and type(record.get('event')) is c.RenewalIntentV01:
        c.require_v01(set(record)=={'event','before','after','information','route','actions','session','calls','provider_calls',
            'renewal','provider_quote'},'renewal_history_shape')
        event = record['event'];report = record['renewal'];before = record['before'];after = record['after']
        c.require_v01(before['entitlements']==entitlements and before['consumed_periods']==periods,'renewal_prefix_lineage')
        predecessor = resolve_period_report_v01(reports,event.entitlement_id)['entitlement']
        c.require_v01(predecessor.candidate.valid_to==max(e.candidate.valid_to for e in entitlements),'renewal_predecessor_period')
        c.validate_renewal_intent_v01(event,predecessor,record['provider_quote'],before['now'])
        validate_report_v01(report)
        prior = original['request'];quote = record['provider_quote']
        expected_request = replace(prior,request_id=event.request_id,order_id=event.order_id,approved_order_id=event.order_id,
            now=event.now,purchase_consent=event.explicit_consent,approved_prices_minor=(quote.plan.price_minor,),
            hard_ceiling_minor=event.consent_limit_minor,catalog=tuple(quote.plan if p.plan_id==quote.plan.plan_id else p for p in prior.catalog))
        c.require_v01(report['request']==expected_request and before['now']==after['now']==event.now and
            not before['active'] and before['devices']==report['devices'] and record['information'] is None and record['route'] is None,
            'renewal_intent_current_source')
        ec = report['entitlement'].candidate;grant = report['session']
        c.require_v01(record['actions']==tuple(report[k] for k in ('payment','entitlement_issuance','session_issuance','playback')) and
            record['calls']==report['calls'] and record['provider_calls']==report['semantics']['provider_call_ledger'] and
            record['session']==grant,'renewal_actual_execution_chain')
        c.require_v01(ec.valid_from==event.now and ec.valid_to==event.now+2592000 and
            ec.valid_from+4>=before['entitlements'][-1].candidate.valid_to and
            all(e.candidate.payment_receipt_ref!=ec.payment_receipt_ref for e in before['entitlements']) and
            report['payment']['bound'].packet_identity.packet_id!=original['payment']['bound'].packet_identity.packet_id,
            'renewal_new_payment_period')
        c.require_v01(after==dict(before,entitlements=before['entitlements']+(report['entitlement'],),
            sessions=before['sessions']+(grant,),active=(grant.session_id,),consumed_periods=before['consumed_periods']+
            ((ec.payment_receipt_ref,ec.user_id,ec.valid_from,ec.valid_to,report['entitlement'].entitlement_id),)), 'renewal_history_lineage')
        return True
    c.require_v01(type(record) is dict and set(record)=={'event','before','after','information','route','actions','session','calls','provider_calls'},'history_event_shape')
    event = record['event']; c.validate_event_v01(event)
    c.require_v01(event.user_id==original['request'].user_id and record['provider_calls']==(),'history_provider_or_subject')
    before = record['before']; after = record['after']
    keys = {'entitlements','sessions','active','consumed_periods','devices','now'}
    c.require_v01(type(before) is dict and set(before)==keys and type(after) is dict and set(after)==keys,'history_view_shape')
    for view in (before,after):
        c.require_v01(type(view['sessions']) is tuple and all(type(s) is c.SessionV01 for s in view['sessions']) and
            len({s.session_id for s in view['sessions']})==len(view['sessions']) and type(view['active']) is tuple and
            len(view['active'])<=1 and set(view['active'])<={s.session_id for s in view['sessions']} and
            type(view['devices']) is tuple and 0<len(view['devices'])<=2 and all(type(d) is c.DeviceStateV01 for d in view['devices']),
            'history_view_types')
    period = original
    if type(event) is c.PlaybackRequestV01:
        period = resolve_period_report_v01(reports,event.entitlement_id)
    elif type(event) is c.StopPlaybackV01:
        c.require_v01(type(record['session']) is c.SessionV01,'stop_session_type')
        period = resolve_period_report_v01(reports,record['session'].candidate.entitlement_id)
    entitlement = period['entitlement']
    c.require_v01(before['entitlements']==after['entitlements']==entitlements and
        before['consumed_periods']==after['consumed_periods']==periods and before['now']==event.now and
        type(after['now']) is int and after['now']>=event.now and
        (type(event) is c.PlaybackRequestV01 or after['now']==event.now) and
        (type(event) is c.DeviceGrantRequestV01 or before['devices']==after['devices']),'history_purchase_immutable')
    if type(event) is c.InformationRequestV01:
        c.require_v01(event.entitlement_id==original['entitlement'].entitlement_id,'information_period_not_supported')
        c.require_v01(original['entitlement'].candidate.valid_from<=event.now<original['entitlement'].candidate.valid_to,
            'information_period_not_current')
        info = record['information']; report = info['report']; review = info['review']
        c.require_v01(type(info) is dict and set(info)=={'event','stored','report','review','budget','answer'} and
            info['event']==event and before==after and record['actions']==() and record['session'] is None,'information_shape')
        c.require_v01(type(review) is dict and set(review)=={'source','contribution','review','kernel','inputs','result'},'information_review_shape')
        c.require_v01(type(record['route']) is dict and set(record['route'])=={'review_input','decision','proposal','router_input','source_context',
            'proposal_artifact','proposal_transition_decision','root_kernel','root_decision_input','root_decision_result'},'history_C_shape')
        c.require_v01(c.canonical_v01(info['stored'])==writeback['stored_bytes'] and
            report.source_records==(writeback['meaning'],) and info['answer']==kernel.summary_facts_v01(original) and
            json.loads(report.source_records[0].safe_summary)==info['answer'],'stored_answer_lineage')
        c.require_v01(report.query.evaluation_time==event.now and report.query.scope_fingerprint==
            kernel.hashlib.sha256(c.canonical_v01(dict(user_id=event.user_id,entitlement_id=event.entitlement_id))).hexdigest(),'information_query_scope')
        c.require_v01(report.query_evaluations==(kernel.memory.evaluate_drs_candidate_v01(
            semantic_address=report.semantic_address,query=report.query,meaning_record=writeback['meaning']),),'actual_B_evaluation')
        expected_projection = kernel.compatibility.project_legacy_drs_source_v01(source_family='LOCAL_DRS_DICT',source=info['stored'],
            target_semantic_address=report.semantic_address,target_meaning_record=None)
        c.require_v01(report.source_projections==(expected_projection,) and
            kernel.memory.validate_memory_descent_budget_v01(info['budget'])[0] and
            report.retrieval_plan.proposed_budget_id==info['budget'].memory_descent_budget_id,'stored_public_B_projection')
        c.require_v01(not semantic_work.validate_root_review_packet_v01(request=review['source'],contributions=(review['contribution'],),
            packet=review['review'],trust_profiles=trust.build_default_component_trust_profiles_v01()) and
            review['inputs'].root_review_packet==review['review'],'shortcut_actual_review')
        ok,reasons = kernel.reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=review['kernel'],
            root_decision_input=review['inputs'],root_decision_result=review['result'],use_time=event.now)
        c.require_v01(ok,'history_B_shortcut:'+repr(reasons))
        c.require_v01(record['route']['source_context'].g2b_resolution_report is report and
            kernel.router.validate_root_execution_mode_decision_against_source_v01(**record['route']).validation_status=='PASS' and
            record['route']['decision'].outcome=='ACCEPT' and record['route']['proposal'].selected_mode=='direct_informational_reuse',
            'history_C_reuse')
    elif type(event) is c.DeviceGrantRequestV01:
        c.require_v01(record['information'] is None and record['route'] is None and record['session'] is None and len(record['actions'])==1,
            'device_grant_history_shape')
        row = record['actions'][0]
        validate_native_history_action_v01(row,original,event,'device','device_grant')
        candidate = c.identity_v01('device_grant_candidate',asdict(event))
        c.require_v01(event.user_id==original['request'].user_id and event.device_id in original['request'].registered_devices and
            event.content_id==original['request'].content_id and event.quality==1080 and event.valid_to==event.now+86400 and
            row['evidence']==dict(event=asdict(event),previous_devices=[asdict(d) for d in before['devices']]) and
            row['checks']==dict(local_device_profile=True,registered_device=True,explicit_fresh_grant=True), 'device_grant_local_source')
        c.require_v01(world.values_v01(row['inputs'])==dict(candidate_ref=candidate,user_id=event.user_id,device_id=event.device_id,
            content_id=event.content_id,valid_from=event.now,valid_to=event.valid_to,quality=event.quality), 'device_grant_actual_inputs')
        fresh = c.DeviceStateV01(event.device_id,event.user_id,event.valid_to,event.quality,(event.content_id,))
        c.require_v01(after==dict(before,devices=tuple(fresh if d.device_id==event.device_id else d for d in before['devices'])),
            'device_grant_effect_before_state')
    elif type(event) is c.StopPlaybackV01:
        c.require_v01(record['information'] is None and record['route'] is None and len(record['actions'])==2,'stop_shape')
        grant = record['session']
        c.require_v01(grant in before['sessions'] and grant.session_id==event.session_id and grant.session_id in before['active'],'stop_source')
        for index,(root,operation,state) in enumerate((('device','stop','STOPPED'),('provider','close','CLOSED'))):
            row = record['actions'][index]
            validate_native_history_action_v01(row,period,event,root,operation)
            inputs = dict(session_ref=grant.session_id,device_id=grant.candidate.device_id,content_id=grant.candidate.content_id)
            expected = dict(session=asdict(grant),active_session_ids=list(before['active']),
                stop_receipt_ref=record['actions'][0]['receipt'].artifact_id if index else None)
            c.require_v01(world.values_v01(row['inputs'])==inputs and row['evidence']==expected and row['output']['state']==state and
                row['checks']==dict(active=True,issued_session=True,stop_observed=True),'stop_input_lineage')
        c.require_v01(after==dict(before,active=tuple(v for v in before['active'] if v!=grant.session_id)),'closure_state_after_execution')
    else:
        c.require_v01(record['information'] is None and record['route'] is None and len(record['actions'])==2,'fresh_session_shape')
        c.validate_playback_request_v01(event,entitlement,before['devices'],before['active'],before['now'])
        c.require_v01(event.content_id==period['request'].content_id and event.device_id in period['request'].registered_devices,
            'history_entitlement_content_device_scope')
        grant = record['session'];sc = grant.candidate
        expected = c.SessionCandidateV01(entitlement.entitlement_id,event.user_id,event.device_id,event.content_id,event.now,
            event.now+event.ttl_seconds,1,event.quality)
        issued,played = record['actions']
        validate_native_history_action_v01(issued,period,event,'provider','session')
        validate_native_history_action_v01(played,period,event,'device','playback')
        c.require_v01(type(grant) is c.SessionV01 and sc==expected and grant not in before['sessions'] and
            grant.provider_decision_id==issued['bound'].root_decision_projection.root_decision_result.decision_id and
            grant.issuance_receipt_ref==issued['receipt'].artifact_id,'fresh_provider_session')
        c.require_v01(issued['bound'].canonical_projection.business_object_identity.business_object_ref==sc.candidate_id and
            world.values_v01(issued['inputs'])==dict(candidate_ref=sc.candidate_id,user_id=sc.user_id,valid_from=sc.valid_from,
                valid_to=sc.valid_to,entitlement_id=sc.entitlement_id,device_id=sc.device_id,content_id=sc.content_id,quality=sc.quality) and
            issued['evidence']==dict(candidate=asdict(sc),entitlement=asdict(entitlement),devices=[asdict(d) for d in before['devices']],
                active_session_ids=list(before['active'])) and
            issued['checks']==dict(current_entitlement=True,no_active_stream=True,device_policy=True),'fresh_session_inputs')
        c.require_v01(world.values_v01(played['inputs'])==dict(session_ref=grant.session_id,device_id=sc.device_id,content_id=sc.content_id) and
            played['bound'].canonical_projection.business_object_identity.business_object_ref==grant.session_id and
            played['evidence']==asdict(c.playback_basis_v01(grant,entitlement,after['devices'])) and
            played['checks']==dict(issued_session=True,current_session=True,device_policy=True),'fresh_device_inputs')
        basis = c.playback_basis_v01(grant,entitlement,after['devices'])
        c.validate_playback_basis_v01(basis,after['now']+4)
        c.require_v01(played['bound'].canonical_projection.temporal_authority.expires_at_utc==min(event.now+120,
            sc.valid_to,basis.valid_to,basis.device.valid_to) and
            played['context'].attempt_evidence.eligibility_evaluation_time==after['now']+4, 'actual_playback_dispatch_time')
        c.require_v01(after==dict(before,now=after['now'],sessions=before['sessions']+(grant,),active=(grant.session_id,)),'fresh_session_state')
    expected_invocations = tuple(row['execution'].invocation.invocation_id for row in record['actions'])
    c.require_v01(type(record['calls']) is tuple,'event_call_shape')
    for call in record['calls']:
        c.require_v01(type(call) is tuple and len(call)==3,'event_call_shape')
        kind,identifier,values = call
        if kind=='INPUT_VALIDATOR':
            matches = tuple(row for row in record['actions'] if row['admitted'].definition.definition_id==identifier and row['inputs']==values)
        elif kind in ('OUTPUT_VALIDATOR','EXECUTOR'):
            matches = tuple(row for row in record['actions'] if row['execution'].invocation.invocation_id==identifier and
                values==(row['execution'].result.output if kind=='OUTPUT_VALIDATOR' else row['inputs']))
        else:
            matches = ()
        c.require_v01(len(matches)==1,'event_actual_call_binding')
    actual_invocations = tuple(identifier for kind,identifier,_ in record['calls'] if kind=='EXECUTOR')
    c.require_v01(actual_invocations==expected_invocations,'event_call_ledger')
    return True


def validate_history_v01(history):
    c.require_v01(type(history) is dict and set(history) in ({'purchase','writeback','events'},
        {'purchase','writeback','events','quotes','renewal_records'}),'history_shape')
    original = history['purchase'];validate_report_v01(original)
    writeback = history['writeback']
    c.require_v01(type(writeback) is dict and set(writeback)=={'meaning','stored','stored_bytes','review'},'writeback_shape')
    meaning = writeback['meaning']; review = writeback['review']; facts = kernel.summary_facts_v01(original)
    c.require_v01(kernel.address_api.validate_meaning_record_v01(meaning)[0] and
        meaning.safe_summary==c.canonical_v01(facts).decode() and
        meaning.content_fingerprint==kernel.hashlib.sha256(c.canonical_v01(facts)).hexdigest() and
        meaning.time_envelope.pt_created_at==original['request'].now and
        meaning.source_reference_ids==(original['entitlement'].issuance_receipt_ref,),'writeback_actual_facts')
    c.require_v01(not semantic_work.validate_root_review_packet_v01(request=review['source'],contributions=(review['contribution'],),
        packet=review['review'],trust_profiles=trust.build_default_component_trust_profiles_v01()) and
        review['inputs'].root_review_packet==review['review'] and
        not roots.validate_root_decision_result_v01(kernel=review['kernel'],decision_input=review['inputs'],result=review['result']) and
        review['result'].decision=='ACCEPT' and review['result'].target_root_id=='root:testflix:user' and
        semantic_work.semantic_work_to_plain_dict_v01(review['contribution'].claims[0])['object_or_value']==facts,'writeback_root_review')
    authority = meaning.authority_envelope
    c.require_v01(authority.source_root_decision_input_id==review['inputs'].decision_input_id and
        authority.source_root_decision_id==review['result'].decision_id and authority.source_root_decision_hash==
        kernel.hashlib.sha256(c.canonical_v01(roots.root_decision_result_to_plain_dict_v01(review['result']))).hexdigest(),'writeback_root_binding')
    c.require_v01(c.canonical_v01(writeback['stored'])==writeback['stored_bytes'] and
        writeback['stored']['content']['meaning']==kernel.address_api.meaning_record_to_plain_data_v01(meaning) and
        writeback['stored']['content']['answer']==facts,'writeback_stored_binding')
    events = history['events']
    c.require_v01(type(events) is tuple and bool(events) and len(events)<=32 and
        len({v['event'].request_id for v in events})==len(events),'history_events')
    previous = None
    prior_renewals = ()
    for record in events:
        validate_history_event_v01(record,original,writeback,prior_renewals=prior_renewals)
        if previous is None:
            c.require_v01(record['before']['sessions']==(original['session'],) and
                record['before']['active']==(original['session'].session_id,),'history_initial_session')
        else:
            c.require_v01(record['before']['now']>=previous['now'] and
                record['before']==dict(previous,now=record['before']['now']),'history_state_lineage')
        previous = record['after']
        if type(record['event']) is c.RenewalIntentV01:
            prior_renewals += (record,)
    if 'quotes' in history:
        quotes=history['quotes'];records=history['renewal_records']
        c.require_v01(type(quotes) is tuple and bool(quotes) and type(records) is tuple,'history_quote_ledger')
        predecessor=None;prior_time=-1
        for quote in quotes:
            c.validate_provider_quote_v01(quote)
            c.require_v01(quote.predecessor_id==predecessor and quote.observed_at>prior_time and
                quote.merchant_id==original['request'].merchant_id and quote.plan.plan_id==original['entitlement'].candidate.plan.plan_id,
                'history_quote_succession')
            predecessor=quote.quote_id;prior_time=quote.observed_at
        c.require_v01(len({r['pending']['event'].request_id for r in records})==len(records),'history_reprice_unique')
        for record in records:
            validate_reprice_v01(record)
            pending=record['pending'];event=pending['event']
            c.require_v01(pending['provider_quote'] in quotes and record['observed_quote'] in quotes and
                event.entitlement_id==original['entitlement'].entitlement_id,'history_reprice_sources')
            preceding=tuple(v for v in events if v['after']['now']<=event.now)
            c.require_v01(bool(preceding) and pending['before']==dict(preceding[-1]['after'],now=event.now),
                'history_reprice_current_view')
        for record in events:
            if type(record['event']) is c.RenewalIntentV01:
                current=tuple(q for q in quotes if q.observed_at<=record['event'].now)
                c.require_v01(bool(current) and record['provider_quote']==current[-1],'history_renewal_current_quote')
    return True


def _writeback_to_plain_v09(writeback):
    c.require_v01(type(writeback['stored_bytes']) is bytes and
        c.canonical_v01(writeback['stored'])==writeback['stored_bytes'],'stored_summary_bytes_binding')
    return {k:plain_value_v01(v) for k,v in writeback.items() if k!='stored_bytes'}


def _action_record_to_plain_v09(record):
    result={k:plain_value_v01(v) for k,v in record.items() if k not in ('host','source','admitted')}
    result['admission_snapshot']=plain_value_v01(firewall.snapshot_admitted_capability_v01(record['admitted']))
    return result


def history_to_plain_v01(history):
    validate_history_v01(history)
    events = []
    for record in history['events']:
        row = {k:plain_value_v01(v) for k,v in record.items() if k not in ('actions','renewal')}
        if 'renewal' in record:
            row['renewal'] = report_to_plain_v01(record['renewal'])
        row['event_kind'] = type(record['event']).__name__
        row['actions'] = [{k:plain_value_v01(v) for k,v in action_record.items() if k not in ('host','source','admitted','context')}
            for action_record in record['actions']]
        events.append(row)
    writeback = _writeback_to_plain_v09(history['writeback'])
    result = dict(profile=('testflix.controlled.history.v01' if history['purchase']['semantics']['mode']=='CONTROLLED_DETERMINISTIC' else 'testflix.history.v02'),purchase=report_to_plain_v01(history['purchase']),
        writeback=writeback,events=events,scope='Pinned historical evidence; never current permission or OS-wide monitoring.')
    if 'quotes' in history:
        result['quotes']=plain_value_v01(history['quotes'])
        result['renewal_records']=[reprice_to_plain_v01(r) for r in history['renewal_records']]
    return result


def _pending_renewal_to_plain_v09(pending):
    q=pending['quote_work'];payment=pending['payment']
    projected_pending={k:plain_value_v01(v) for k,v in pending.items() if k not in ('quote_work','payment','memory_writeback')}
    projected_pending['memory_writeback']=_writeback_to_plain_v09(pending['memory_writeback'])
    projected_pending['payment']={k:plain_value_v01(v) for k,v in payment.items() if k not in ('host','source','admitted')}
    projected_pending['quote_work']={k:plain_value_v01(q[k]) for k in
        ('program','obligation','d_source','d_bundle','d_report','results','host_attempts','host_events')}
    projected_pending['quote_work']['source_context']=plain_value_v01(q['common']['source_context'])
    projected_pending['quote_work']['semantic_proposal']=plain_value_v01(q['common']['semantic_proposal'])
    return projected_pending


def reprice_to_plain_v01(record):
    validate_reprice_v01(record)
    pending=record['pending'];payment=pending['payment']
    result={k:plain_value_v01(v) for k,v in record.items() if k not in ('pending','delta','current_baseline')}
    result['pending']=_pending_renewal_to_plain_v09(pending)
    current=record['current_baseline']
    result['current_baseline']={k:plain_value_v01(v) for k,v in current.items() if k not in ('common','capture')}
    capture=current['capture']
    hosts.validate_retained_action_source_capture_v01(payment['host'],capture)
    result['current_baseline']['retained_capture_projection']={f.name:plain_value_v01(getattr(capture,f.name))
        for f in fields(capture) if f.name!='_origin'}
    result['current_baseline']['portable_origin_scope']='PINNED_RECORDED_CAPTURE_NOT_LIVE_ORIGIN_OR_PERMISSION'
    result['delta']={k:plain_value_v01(record['delta'][k]) for k in ('arguments','bundle','validation')}
    result['delta']['material']={k:plain_value_v01(v) for k,v in record['delta']['material'].items() if k not in ('pending','source_kwargs')}
    result['delta']['material']['source_context']=plain_value_v01(record['delta']['bundle'].source_context)
    return result


def seal_history_v01(history):
    payload = history_to_plain_v01(history)
    profile = integrity.build_default_seal_profile_v01()
    transaction = history['purchase']['request'].request_id
    identifier = c.identity_v01('history_payload',payload)
    artifact = integrity.build_canonical_artifact_ref_v01(artifact_id=identifier,artifact_type='TestflixRecordedEvidence',schema_version='v1',
        transaction_id=transaction,owner_root_id='root:testflix:user',authority_class='EVIDENCE_ONLY',lifecycle_state='RECORDED',payload=payload,profile=profile)
    manifest = integrity.build_artifact_manifest_v01(transaction_id=transaction,profile=profile,artifacts=(artifact,),dependency_edges=(),
        root_ownership_bindings=(integrity.RootOwnershipBindingV01(identifier,'root:testflix:user'),),
        evidence_class_bindings=(integrity.EvidenceClassBindingV01(identifier,
            'CONTROLLED_DOMAIN_EXECUTION' if payload['profile'].startswith('testflix.controlled.') else 'SEMANTIC_CAPTURED_MOCK_EFFECT_EXECUTION'),),
        authority_class_bindings=(integrity.AuthorityClassBindingV01(identifier,'EVIDENCE_ONLY'),))
    c.require_v01(integrity.verify_artifact_manifest_v01(manifest=manifest,payload_rows=((identifier,payload),),
        expected_manifest_hash=manifest.manifest_hash).verification_status=='PASS','history_seal')
    return dict(manifest=integrity.artifact_manifest_to_plain_dict_v01(manifest),payload=payload,manifest_hash=manifest.manifest_hash)


def replay_history_v01(package, *, expected_manifest_hash):
    before = (len(world.CALLS),len(semantic.PROVIDER_CALLS))
    c.require_v01(type(package) is dict and set(package)=={'manifest','payload','manifest_hash'} and
        package['manifest_hash']==expected_manifest_hash,'history_replay_pin')
    manifest = manifest_from_plain_v01(package['manifest']); payload = package['payload']
    result = integrity.verify_artifact_replay_v01(manifest=manifest,payload_rows=((manifest.artifacts[0].artifact_id,payload),),
        expected_manifest_hash=expected_manifest_hash)
    c.require_v01(result.replay_status=='PASS','history_replay_seal')
    mode = payload['purchase']['semantics']['mode']
    c.require_v01(payload['profile']==('testflix.controlled.history.v01' if mode=='CONTROLLED_DETERMINISTIC'
        else 'testflix.history.v02') and payload['purchase']['generation_mode']==mode,'history_replay_profile')
    semantic.validate_semantics_v01(c.request_from_plain_v01(payload['purchase']['request']),
        semantic.semantics_from_plain_v01(payload['purchase']['semantics']))
    ent = payload['purchase']['entitlement']
    entitlements = [ent]
    ec = ent['candidate']
    periods = [[ec['payment_receipt_ref'],ec['user_id'],ec['valid_from'],ec['valid_to'],c.identity_v01('entitlement',ent)]]
    previous = None
    for event in payload['events']:
        c.require_v01(event['before']['entitlements']==entitlements and
            event['before']['consumed_periods']==periods,'history_replay_period_prefix')
        if previous is not None:
            c.require_v01(event['before']==dict(previous,now=event['before']['now']),'history_replay_lineage')
        if event['event_kind']=='RenewalIntentV01':
            renewal = event['renewal'];ec = renewal['entitlement']['candidate']
            renewed_id = c.identity_v01('entitlement',renewal['entitlement'])
            c.require_v01(event['event']['entitlement_id'] in {p[4] for p in periods} and
                renewed_id not in {p[4] for p in periods} and ec['payment_receipt_ref'] not in {p[0] for p in periods},
                'history_replay_new_period')
            request = c.request_from_plain_v01(renewal['request'])
            c.require_v01(renewal['generation_mode']==renewal['semantics']['mode'],'history_replay_renewal_mode')
            semantic.validate_semantics_v01(request,semantic.semantics_from_plain_v01(renewal['semantics']))
            c.validate_payment_relationship_v01(request,c.PlanV01(**ec['plan']),renewal['actions']['payment']['output'])
            c.require_v01(event['event']['explicit_consent'] is True and event['event']['quote_id']==
                c.identity_v01('provider_quote',event['provider_quote']) and event['event']['consent_limit_minor']>=ec['plan']['price_minor'] and
                event['before']['entitlements']+[renewal['entitlement']]==event['after']['entitlements'] and
                ec['payment_receipt_ref']==renewal['actions']['payment']['output']['payment_ref'], 'history_replay_renewal')
            entitlements = entitlements+[renewal['entitlement']]
            periods = periods+[[ec['payment_receipt_ref'],ec['user_id'],ec['valid_from'],ec['valid_to'],renewed_id]]
        else:
            c.require_v01(event['after']['entitlements']==entitlements,'history_replay_purchase')
        c.require_v01(event['after']['consumed_periods']==periods,'history_replay_consumed_periods')
        if event['event_kind'] in ('PlaybackRequestV01','StopPlaybackV01'):
            grant=event['session'];entitlement_id=grant['candidate']['entitlement_id']
            c.require_v01(entitlement_id in {p[4] for p in periods},'history_replay_session_period')
            if event['event_kind']=='PlaybackRequestV01':
                c.require_v01(event['event']['entitlement_id']==entitlement_id,'history_replay_playback_period')
            else:
                c.require_v01(event['event']['session_id']==c.identity_v01('session',grant),'history_replay_stop_session')
        for record in event['actions']:
            execution = firewall.native_execution_evidence_from_plain_data_v01(record['execution'])
            c.require_v01(not firewall.validate_native_execution_evidence_v01(execution) and
                execution.invocation.packet_id==record['bound']['packet_identity']['packet_id'] and
                record['receipt']['payload']['execution_evidence']==record['execution'] and
                record['output']==world.values_v01(execution.result.output),'history_replay_native')
        if event['information'] is not None:
            info = event['information'];b = info['report']
            c.require_v01(info['stored']==payload['writeback']['stored'] and
                json.loads(b['source_records'][0]['safe_summary'])==info['answer'] and
                event['route']['router_input']['g2b_binding']['report_id']==b['report_id'] and
                event['route']['proposal']['selected_mode']=='direct_informational_reuse','history_replay_B_C')
        previous = event['after']
    for record in payload.get('renewal_records',()):
        current=record['current_baseline'];capture=current['retained_capture_projection']
        c.require_v01(current['portable_origin_scope']=='PINNED_RECORDED_CAPTURE_NOT_LIVE_ORIGIN_OR_PERMISSION',
            'history_replay_temporal_scope')
        bundle=record['delta']['bundle'];source=bundle['source_context']
        d=bundle['recomputed_g2d_execution_bundle'];packet=record['pending']['payment']['bound']
        expected=dict(owning_root_id=capture['owning_root_id'],transaction_id=capture['transaction_id'],
            packet_id=capture['packet_id'],evaluation_time_epoch_seconds=capture['evaluation_time'],
            evaluation_time_source=capture['evaluation_time_source'],evaluation_context_id=capture['evaluation_context_id'],
            source_revision=capture['source_revision'],host_revision=capture['host_revision'],
            capture_ordinal=capture['capture_ordinal'],observation_ids=[v['observation_id'] for v in capture['observations']],
            logical_time_bridge_id=capture['logical_time_bridge']['bridge_id'])
        c.require_v01(d['temporal_binding']==expected and source['g2a_packet']==packet==capture['root_bound_packet'] and
            packet['packet_identity']['packet_id']==capture['packet_id'] and
            source['g2a_current_observations']==capture['observations'] and source['g2a_registry']==capture['registry'] and
            source['g2b_resolution_report']['query']['query_id']==capture['transaction_id'] and
            source['g2a_root_invalidation_material']['evaluation_time']==capture['evaluation_time'],
            'history_replay_temporal_packet_binding')
        historical=d['source_context']['router_input']['local_routing_snapshot']['evaluation_time_epoch_seconds']
        c.require_v01(historical<=capture['evaluation_time'] and all(
            v['temporal_binding']==expected and v['evaluation_time_epoch_seconds']==capture['evaluation_time']
            for v in d['retained_admissions']), 'history_replay_temporal_admission')
        for consumption in d['retained_consumptions']:
            evidence=consumption['admission']['evidence']
            c.require_v01(consumption['consumed_result']==evidence['historical_cell_result'] and
                consumption['consumed_result_artifact']==evidence['historical_result_artifact'],
                'history_replay_retained_result_bytes')
        c.require_v01(record['dispatch_reason']=='host_current_action_not_executable' and
            not any(v[0]=='EXECUTOR' for v in record['calls']), 'history_replay_reprice_no_payment')
    c.require_v01(before==(len(world.CALLS),len(semantic.PROVIDER_CALLS)),'history_replay_live_calls')
    return dict(replay_status=result.replay_status,manifest_hash=expected_manifest_hash,live_capability_calls=len(world.CALLS)-before[0],
        provider_calls=len(semantic.PROVIDER_CALLS)-before[1],current_permission='NOT_INFERRED_FROM_HISTORY')


def plain_value_v01(value):
    if value is None or type(value) in (str,int,bool,float):
        return value
    if type(value) is abi.KernelArtifactV01:
        return abi.kernel_artifact_to_plain_dict_v01(value)
    if isinstance(value,Mapping):
        return {k:plain_value_v01(v) for k,v in value.items()}
    if type(value) in (tuple,list):
        return [plain_value_v01(v) for v in value]
    if is_dataclass(value) and not isinstance(value,type):
        return {f.name:plain_value_v01(getattr(value,f.name)) for f in fields(value)}
    raise ValueError('unprojectable_type:'+type(value).__name__)


def report_to_plain_v01(report):
    validate_report_v01(report)
    quote = report['quote']
    q = {k:plain_value_v01(quote[k]) for k in ('program','obligation','d_source','d_bundle','d_report','results')}
    q.update(source_context=plain_value_v01(quote['common']['source_context']),
        semantic_proposal=plain_value_v01(quote['common']['semantic_proposal']),
        admission_snapshots=[plain_value_v01(firewall.snapshot_admitted_capability_v01(a)) for a in quote['common']['catalogue']],
        host_attempts=plain_value_v01(quote['host_attempts']),host_events=plain_value_v01(quote['host_events']))
    actions = {}
    for key in ('payment','entitlement_issuance','session_issuance','playback'):
        record = report[key]
        item = {k:plain_value_v01(record[k]) for k in ('bound','inputs','material','observation','evidence','checks','root_review','pending_registry','registry','receipt','execution','output')}
        item['historical_lifecycle_replay'] = plain_value_v01(action.replay_action_packet_lifecycle_history_v01(record['registry'],
            packet_id=record['bound'].packet_identity.packet_id))
        actions[key] = item
    return dict(profile=('testflix.controlled.p01.v01' if report['semantics']['mode']=='CONTROLLED_DETERMINISTIC' else 'testflix.p01.v02'),generation_mode=report['semantics']['mode'],
        request=plain_value_v01(report['request']),semantics=plain_value_v01(report['semantics']),quote=q,actions=actions,
        user_selection=plain_value_v01(report['user_selection']),
        devices=plain_value_v01(report['devices']),
        entitlement=plain_value_v01(report['entitlement']),session=plain_value_v01(report['session']),
        role_projections=plain_value_v01(report['role_projections']),calls=plain_value_v01(report['calls']),
        claim_scope=('Actual controlled calls and typed evidence; no OS monitoring, live provider or real adapter.'
            if report['semantics']['mode']=='CONTROLLED_DETERMINISTIC' else
            'Input-bound semantic captures and actual typed work/Root decisions. Business effects are mocks. Replay is not current permission.'))


def seal_report_v01(report):
    payload = report_to_plain_v01(report)
    profile = integrity.build_default_seal_profile_v01()
    transaction = report['request'].request_id
    identifier = c.identity_v01('report_payload',payload)
    artifact = integrity.build_canonical_artifact_ref_v01(artifact_id=identifier,artifact_type='TestflixRecordedEvidence',schema_version='v1',
        transaction_id=transaction,owner_root_id='root:testflix:user',authority_class='EVIDENCE_ONLY',lifecycle_state='RECORDED',payload=payload,profile=profile)
    manifest = integrity.build_artifact_manifest_v01(transaction_id=transaction,profile=profile,artifacts=(artifact,),dependency_edges=(),
        root_ownership_bindings=(integrity.RootOwnershipBindingV01(identifier,'root:testflix:user'),),
        evidence_class_bindings=(integrity.EvidenceClassBindingV01(identifier,
            'CONTROLLED_DOMAIN_EXECUTION' if payload['profile'].startswith('testflix.controlled.') else 'SEMANTIC_CAPTURED_MOCK_EFFECT_EXECUTION'),),
        authority_class_bindings=(integrity.AuthorityClassBindingV01(identifier,'EVIDENCE_ONLY'),))
    verified = integrity.verify_artifact_manifest_v01(manifest=manifest,payload_rows=((identifier,payload),),expected_manifest_hash=manifest.manifest_hash)
    c.require_v01(verified.verification_status=='PASS','seal_verification')
    return dict(manifest=integrity.artifact_manifest_to_plain_dict_v01(manifest),payload=payload,
        manifest_hash=manifest.manifest_hash)


def manifest_from_plain_v01(value):
    c.require_v01(type(value) is dict and set(value)==set(integrity.ArtifactManifestV01.__dataclass_fields__),'manifest_shape')
    result = dict(value)
    result['seal_profile'] = integrity.SealProfileV01(**value['seal_profile'])
    for key,kind in (('artifacts',integrity.CanonicalArtifactRefV01),('dependency_edges',integrity.ArtifactDependencyEdgeV01),
        ('root_ownership_bindings',integrity.RootOwnershipBindingV01),('evidence_class_bindings',integrity.EvidenceClassBindingV01),
        ('authority_class_bindings',integrity.AuthorityClassBindingV01)):
        result[key] = tuple(kind(**v) for v in value[key])
    return integrity.ArtifactManifestV01(**result)


def replay_v01(package, *, expected_manifest_hash):
    """Historical seal/native evidence verification, no live code admission."""
    before = len(world.CALLS)
    c.require_v01(type(package) is dict and set(package)=={'manifest','payload','manifest_hash'},'replay_shape')
    c.require_v01(type(expected_manifest_hash) is str and expected_manifest_hash==package['manifest_hash'],'replay_external_pin')
    manifest = manifest_from_plain_v01(package['manifest'])
    payload = package['payload']
    result = integrity.verify_artifact_replay_v01(manifest=manifest,
        payload_rows=((manifest.artifacts[0].artifact_id,payload),),expected_manifest_hash=expected_manifest_hash)
    c.require_v01(result.replay_status=='PASS','replay_seal_refusal')
    expected_profile = 'testflix.controlled.p01.v01' if payload['generation_mode']=='CONTROLLED_DETERMINISTIC' else 'testflix.p01.v02'
    c.require_v01(payload['profile']==expected_profile and payload['generation_mode']==payload['semantics']['mode'],'replay_profile')
    request = c.request_from_plain_v01(payload['request'])
    semantic.validate_semantics_v01(request,semantic.semantics_from_plain_v01(payload['semantics']))
    c.require_v01(set(payload['actions'])=={'payment','entitlement_issuance','session_issuance','playback'},'replay_action_set')
    outputs = {}
    for key,record in payload['actions'].items():
        execution = firewall.native_execution_evidence_from_plain_data_v01(record['execution'])
        c.require_v01(record['receipt']['payload']['execution_evidence']==record['execution'],'replay_retained_execution')
        c.require_v01(execution.invocation.packet_id==record['bound']['packet_identity']['packet_id'],'replay_packet_binding')
        c.require_v01(record['output']==world.values_v01(execution.result.output),'replay_output_binding')
        c.require_v01(record['historical_lifecycle_replay']['rebuilt_packet_id']==execution.invocation.packet_id,'replay_recorded_history_binding')
        outputs[key] = record['output']
    plan = c.plan_by_id_v01(request,payload['semantics']['selected_plan']['plan_id'])
    c.validate_payment_relationship_v01(request,plan,outputs['payment'])
    ent = payload['entitlement']
    ec_data = dict(ent['candidate']);ec_data['plan'] = c.PlanV01(**ec_data['plan'])
    entitlement = c.EntitlementV01(c.EntitlementCandidateV01(**ec_data),ent['decision_id'],ent['issuance_receipt_ref'])
    session = c.SessionV01(c.SessionCandidateV01(**payload['session']['candidate']),payload['session']['provider_decision_id'],payload['session']['issuance_receipt_ref'])
    c.require_v01(entitlement.candidate.plan==plan and entitlement.candidate.payment_receipt_ref==outputs['payment']['payment_ref'], 'replay_entitlement_lineage')
    c.require_v01(session.candidate.entitlement_id==entitlement.entitlement_id and outputs['playback']['session_ref']==session.session_id,'replay_session_lineage')
    c.require_v01(payload['quote']['d_bundle']['runtime_report']['runtime_outcome']=='COMPLETED' and
        all(r['status']=='COMPLETED' for r in payload['quote']['results']),'replay_required_work')
    c.require_v01(len(world.CALLS)==before,'replay_live_code_called')
    return dict(replay_status=result.replay_status,manifest_hash=expected_manifest_hash,
        replay_id=result.replay_id,provider_calls=0,live_capability_calls=len(world.CALLS)-before,
        source='PINNED_RECORDED_EVIDENCE',scope='Public seal/native stored evidence and domain lineage; no fresh execution or new permission.')
