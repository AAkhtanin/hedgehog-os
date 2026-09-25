"""One source-owned atomic disposable booking snapshot through native MOCK dispatch."""
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_exchange_v01 as x
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall, abi_v01 as abi
from demo import run_action_packet_portability_v01 as donor
from candidate_domain.domain import need, Refusal, inventory_check, available, overlap, logical_object, planning_equal
from candidate_domain.policy import approve_booking
from candidate_domain.storage import read, save, state, object_path
from candidate_domain.native import review

# Per owning process, bound only by local reviewed dispatch code. Never serialized authority.
_ACTIVE=None

def current_checks(ctx,payload):
    r=ctx['request']; body=ctx['body']; i=ctx['inventory']; policy=ctx['policy']
    approve_booking(r,body,policy)
    need(policy['status']=='ACTIVE' and policy['release_enabled'] and policy['publish_enabled'],
         'booking_current_owner_policy')
    terminal=read(ctx['state_root']/'source_terminal.json',{})
    source_key=c.sha([body['source_record_ref'],body['source_revision']])
    need(source_key not in terminal,'booking_source_terminal')
    x_now=x.clock()
    c.temporal(body['time_envelope'],x_now,dict(max_source_age=policy['max_source_age'],max_validity_horizon=300))
    need(planning_equal(r,body['offer']['request']) and body['offer']['status']=='OFFER_READY','booking_offer_binding')
    inventory_check(i,r)
    need(i['revision']==body['offer']['schedule_revision'],'booking_schedule_changed')
    need(payload==ctx['payload'],'booking_exact_payload')
    fields={f['field_id']:f for f in i['fields']}
    ledger=read(ctx['state_root']/'registry.json',dict(records=[],idempotency={}))
    for s in body['offer']['slots']:
        f=fields.get(s['field_id'])
        need(f is not None and f['surface']=='natural_grass' and f['full_size'] and
             f['price_minor']==s['price_minor'] and available(f,s['start_utc'],s['end_utc']),
             'booking_current_occupancy_or_tariff')
        need(not any(row['field_id']==s['field_id'] and row['venue_ref']==s['venue_ref'] and
                     overlap((row['start_utc'],row['end_utc']),(s['start_utc'],s['end_utc']))
                     for row in ledger['records']),'booking_registry_overlap')
    return ledger

def validate_inputs(definition,inputs):
    errors=firewall.validate_capability_values_v01(definition.input_fields,inputs)
    if not errors:
        try:
            values={v.parameter_name:v.value for v in inputs}
            need(_ACTIVE is not None and values['device_ref']==_ACTIVE['request']['venue_ref'],'effect_local_context')
            current_checks(_ACTIVE,c.decode(values['payload_json'].encode()))
        except ValueError as exc:
            errors=('football_action_input:'+str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=inputs,
        invocation_id=None,valid=not errors,reason_codes=errors)

def execute_booking(invocation):
    ctx=_ACTIVE
    need(ctx is not None and invocation.packet_id==ctx['packet_ref'] and
         invocation.owning_root_id==ctx['policy']['local_root'],'effect_live_packet_binding')
    ctx['stages'].append(dict(stage='EXECUTOR_STARTED',invocation_ref=invocation.invocation_id,utc=x.clock()))
    values={v.parameter_name:v.value for v in invocation.inputs}
    payload=c.decode(values['payload_json'].encode())
    old=current_checks(ctx,payload)
    key=ctx['native_key']
    need(key not in old['idempotency'],'terminal_key_never_dispatched')
    entry=dict(payload_sha256=c.sha(payload),packet_ref=invocation.packet_id,
               object_ref=logical_object(ctx['request']),slots=payload['slots'],request_sha256=c.sha(ctx['request']))
    new=dict(records=old['records']+payload['slots'],idempotency=dict(old['idempotency']))
    new['idempotency'][key]=entry
    # The only business-state write in this package. Both three slots and key are replaced together.
    state(ctx['state_root']/'registry.json',new)
    ctx['stages'].append(dict(stage='MUTATION_COMMITTED',snapshot_sha256=c.sha(new),utc=x.clock()))
    ctx['readback']=read(ctx['state_root']/'registry.json')
    need(ctx['readback']==new,'effect_readback_mismatch')
    output=dict(state='COMMITTED',payload_sha256=c.sha(payload),snapshot_sha256=c.sha(new))
    ctx['output']=output
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=k,value_type='TEXT',value=output[k])
                 for k in ('payload_sha256','snapshot_sha256','state'))

def validate_output(definition,invocation,output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors:
        values={v.parameter_name:v.value for v in output}
        if _ACTIVE is None:
            errors=('football_effect_output_context',)
        else:
            ledger=read(_ACTIVE['state_root']/'registry.json')
            entry=None if ledger is None else ledger['idempotency'].get(_ACTIVE.get('native_key'))
            expected=dict(state='COMMITTED',payload_sha256=c.sha(_ACTIVE['payload']),snapshot_sha256=c.sha(ledger))
            if (entry is None or values!=expected or entry['payload_sha256']!=expected['payload_sha256'] or
                entry['slots']!=_ACTIVE['payload']['slots'] or
                not all(s in ledger['records'] for s in entry['slots'])):
                errors=('football_effect_output_readback',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,
        invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)

def admit(device):
    functions=(validate_inputs,validate_output,execute_booking)
    code=tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
    operation_key='football.book.v01'
    semantics=firewall.build_capability_business_semantics_v01(operation_key=operation_key,
        selected_action_class='mock_action:football_booking',logical_effect_class='BOOK',
        logical_effect_namespace=operation_key,business_object_class='BOOKING',
        business_object_namespace='football.registry.v01',input_bindings=tuple(
            firewall.build_capability_business_input_binding_v01(input_name=k,source_kind=source,
            source_name=k,value_type=t) for k,t,source in
            (('device_ref','REFERENCE','TARGET_RECORD'),('payload_json','TEXT','RECORD'))))
    definition=firewall.build_capability_definition_v01(operation_id=semantics.operation_key,version='v01',
        effect_kind='MOCK_CONSEQUENTIAL',business_semantics=semantics,
        input_fields=tuple(firewall.build_capability_field_v01(name=k,value_type=t,required=True,consequential=True)
            for k,t in (('device_ref','REFERENCE'),('payload_json','TEXT'))),
        output_fields=tuple(firewall.build_capability_field_v01(name=k,value_type='TEXT',required=True,consequential=False)
            for k in ('payload_sha256','snapshot_sha256','state')),resource_refs=(device,),
        input_validator_ref=code[0].public_symbol,output_validator_ref=code[1].public_symbol,executor_ref=code[2].public_symbol,
        code_sha256s=tuple((s.public_symbol,s.source_sha256) for s in code))
    return hosts.admit_local_capability_v01(definition=definition,input_validator=validate_inputs,
        output_validator=validate_output,executor=execute_booking,catalogue_revision=0,host_instance_ref='host:football:booking')

def reconcile(state_root,r):
    saved=read(object_path(state_root,r))
    if saved is None:
        return None
    need(planning_equal(r,saved['request']),'same_logical_object_changed_payload')
    if r['operation']=='CONFIRM_MOCK_BOOKING':
        need(r==saved['request'],'same_logical_object_changed_confirmation')
    ledger=read(state_root/'registry.json')
    need(ledger is not None and saved['native_key'] in ledger['idempotency'],
         'history_state_missing','CURRENT_STATUS_UNKNOWN')
    entry=ledger['idempotency'][saved['native_key']]
    need(entry==saved['entry'] and all(s in ledger['records'] for s in saved['booking']['slots']) and
         saved['receipt']['artifact_id']==saved['booking']['receipt_ref'],
         'history_readback_mismatch','CURRENT_STATUS_UNKNOWN')
    return dict(saved=saved,readback=ledger)

def book(r,i,body,p,state_root,folder):
    global _ACTIVE
    old=reconcile(state_root,r)
    need(old is None,'use_history_branch')
    pending=state_root/'attempts'/(c.sha(logical_object(r))+'.json')
    prior=read(pending)
    need(prior is None or prior.get('outcome')=='NO_EXECUTOR_START',
         'previous_outcome_requires_readback','CURRENT_STATUS_UNKNOWN')
    payload=dict(request=r,offer_sha256=c.sha(body),schedule_revision=body['offer']['schedule_revision'],
                 inventory_sha256=c.sha(i),slots=body['offer']['slots'],total_minor=body['offer']['total_minor'],currency=r['currency'])
    ctx=dict(request=r,inventory=i,body=body,policy=p,state_root=state_root,payload=payload,stages=[],packet_ref=None)
    current_checks(ctx,payload)
    now=x.clock()
    consent=review(p['local_root'],'transaction:football:consent:'+c.sha(r),'candidate:football:consent:'+c.sha(payload),
        logical_object(r),dict(explicit_owner_consent=any(a['request_sha256']==c.sha(r) and
        a['offer_request_sha256']==c.sha(body['offer']['request']) and a['approval_ref']==r['owner_approval_ref'] for a in p['book_approvals']),
        schedule_current=i['revision']==body['offer']['schedule_revision']),
        dict(request=r,offer_sha256=c.sha(body),payload_sha256=c.sha(payload),inventory_sha256=c.sha(i)),
        now,folder,'consent_review',window=(body['time_envelope']['valid_from'],
        c.temporal(body['time_envelope'],now,dict(max_source_age=p['max_source_age'],max_validity_horizon=300))))
    need(consent[2].decision=='ACCEPT','local_booking_review_refused')
    _ACTIVE=ctx
    host=None
    try:
        admitted=admit(r['venue_ref'])
        inputs=tuple(action.build_action_effect_parameter_record_v01(parameter_name=k,value_type=t,value=v)
            for k,t,v in (('device_ref','REFERENCE',r['venue_ref']),('payload_json','TEXT',c.canonical(payload).decode())))
        canonical=donor.build_native_work_action_v01(admitted=admitted,inputs=inputs,root_id=p['local_root'],
            transaction_id='transaction:'+logical_object(r),business_object_ref=logical_object(r))
        prepared=donor.authorize_and_prepare_action_v01(canonical,admitted,inputs)
        ctx['packet_ref']=prepared.root_bound.packet_identity.packet_id
        ctx['native_key']=canonical.idempotency_identity.idempotency_key
        host=donor.host_for_prepared_action_v01(prepared)
        save(folder/'action_packet.json',n.plain(canonical))
        save(folder/'action_root.json',n.plain(prepared.root_bound.root_decision_projection))
        save(folder/'action_admission.json',n.plain(firewall.snapshot_admitted_capability_v01(admitted)))
        state(pending,dict(packet_ref=ctx['packet_ref'],native_key=ctx['native_key'],payload_sha256=c.sha(payload),outcome='PENDING'))
        ctx['stages'].append(dict(stage='HOST_ATTEMPT',utc=x.clock()))
        registry,revision=hosts.dispatch_current_action_v01(host,packet_id=ctx['packet_ref'],
            task_id='task:football:book:'+c.sha(r),expected_revision=host.revision,evaluation_time=1014,
            evaluation_time_source='u1.controlled_utc',evaluation_context_id='context:u1:dispatch')
        attempt=registry.action_packet_fulfillment_attempt_contexts[-1]
        receipt=attempt.receipt
        if receipt is None and not any(s['stage']=='EXECUTOR_STARTED' for s in ctx['stages']):
            raise Refusal('host_nonconsuming_refusal')
        need(receipt is not None and 'output' in ctx,'missing_native_receipt','CURRENT_STATUS_UNKNOWN')
        need(bool(host.work_attempts) and host.work_attempts[-1].result is not None and
             host.work_attempts[-1].result.outcome=='SUCCEEDED','native_effect_not_successful','CURRENT_STATUS_UNKNOWN')
        receipt_plain=abi.kernel_artifact_to_plain_dict_v01(receipt)
        ledger=read(state_root/'registry.json')
        need(ledger==ctx['readback'],'post_dispatch_readback','CURRENT_STATUS_UNKNOWN')
        booking=dict(state='COMMITTED',receipt_ref=receipt_plain['artifact_id'],packet_ref=ctx['packet_ref'],
            payload_sha256=c.sha(payload),snapshot_sha256=c.sha(ledger),slots=body['offer']['slots'],request_sha256=c.sha(r))
        saved=dict(request=r,body=body,booking=booking,native_key=ctx['native_key'],
            entry=ledger['idempotency'][ctx['native_key']],receipt=receipt_plain,original_snapshot=ledger,
            consent_review_ref=consent[2].decision_id)
        # Save the actual receipt before optional presentation evidence.
        save(object_path(state_root,r),saved)
        save(folder/'receipt.json',receipt_plain)
        save(folder/'state_readback.json',ledger)
        save(folder/'host_outcome.json',dict(attempt=n.plain(attempt),revision=revision,events=n.plain(host.events),
            work_attempts=n.plain(host.work_attempts),stages=ctx['stages']))
        return booking
    except Exception as exc:
        started=any(s['stage']=='EXECUTOR_STARTED' for s in ctx['stages'])
        save(folder/'action_failure.json',dict(error_type=type(exc).__name__,error=str(exc),stages=ctx['stages'],
            readback=read(state_root/'registry.json'),host_events=None if host is None else n.plain(host.events),
            prohibition='NO_BLIND_RETRY'))
        if not started and pending.exists():
            state(pending,dict(read(pending),outcome='NO_EXECUTOR_START'))
        if started:
            raise Refusal('action_outcome_requires_readback:'+str(exc),'CURRENT_STATUS_UNKNOWN') from exc
        raise
    finally:
        _ACTIVE=None
