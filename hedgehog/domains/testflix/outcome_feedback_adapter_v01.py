"""One shared quote/D and isolated ordinary current payment/revocation branches."""
from dataclasses import asdict, replace
import json
from pathlib import Path
import time
from hedgehog import outcome_feedback_v01 as f, action_commit_packet_v02 as a
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as fw, work_composition_v01 as work
from . import contracts_v01 as c, kernel_adapter_v01 as k, evidence_v01 as e
from . import lifecycle_v01 as life, mock_world_v01 as world, semantic_adapter_v01 as semantic


def _public_request_v01(request):
    value=e.plain_value_v01(request)
    value.pop('bank_private');value.pop('user_private')
    return value


def collect_source_v01(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    raw=json.loads((Path(__file__).resolve().parents[3]/'demo/testflix_fixtures_v01.json').read_bytes())
    raw['now']=int(time.time());raw['request_id']='request:gate3:testflix'
    request=c.request_from_plain_v01(raw);sem=semantic.collect_semantics_v01(request)
    start=time.perf_counter_ns();quote=k.collect_quote_work_v01(request,sem)
    quote_us=(time.perf_counter_ns()-start)//1000
    values=e.validate_quote_v01(request,sem,quote)
    selections=[e.review_user_selection_v01(request,sem,quote),e.review_user_selection_v01(replace(request,purchase_consent=False),sem,quote)]
    f._require(selections[0]['result'].decision=='ACCEPT' and selections[1]['result'].decision!='ACCEPT','g35_testflix_consent')
    artifact=work.work_program_result_to_artifact_v01(quote['program'],quote['results'],**quote['common'],
        host_map={'root:testflix:user':quote['host']},review_bindings=((quote['obligation'],quote['d_source'],quote['d_bundle']),))
    # Preserve the real D source/report identity. Full native D schema replay is not claimed.
    d_record=dict(source=e.plain_value_v01(quote['d_source']),
        source_binding=k.fractal.runtime_topology_source_binding_to_plain_data_v02(quote['d_bundle'].source_binding),
        report=k.fractal.fractal_runtime_report_to_plain_data_v02(quote['d_bundle'].runtime_report),
        validation=k.fractal.fractal_runtime_validation_report_to_plain_data_v02(quote['d_report']),
        review_commitment=work.work_review_commitment_to_plain_data_v01(candidate=quote['program'].candidate,
            item=quote['program'].candidate.items[0],source_context=quote['common']['source_context'],semantic_proposal=quote['common']['semantic_proposal']))
    (directory/'quote_D_source_review.json').write_bytes(f.g35_bytes_v01(d_record)+b'\n')
    branches=[]
    for name in ('lawful','revoked','fresh_neighbor'):
        current=replace(request,now=int(time.time()),request_id=request.request_id+':'+name)
        admitted=e.payment_admission_v01(current);host,source=life.new_host_v01('root:testflix:bank',(admitted,),current.now)
        inputs=world.records_v01(dict(amount=('DECIMAL','5'),currency=('TEXT',current.currency),merchant_id=('REFERENCE',current.merchant_id),order_id=('REFERENCE',current.order_id)))
        evidence=dict(order=current.order_id,merchant=current.merchant_id,amount_minor=values['quote']['price_minor'],currency=current.currency,
            quote_ref=values['quote']['quote_ref'],user_selection=selections[0]['result'].decision_id)
        prepared=life.install_v01(host,source,current,admitted,inputs,current.order_id,current.merchant_id,evidence,quote,
            dict(quote_completed=values['quote']['price_minor']==500,explicit_selection=selections[0]['result'].decision=='ACCEPT'))
        before=len([v for v in world.CALLS if v[0]=='EXECUTOR']);receipt=None;refusal=None
        if name=='revoked':
            life.revoke_current_v01(prepared,bsep_ref=quote['program'].candidate.bsep_ref,topology_ref=quote['program'].topology_artifact.artifact_id)
            try:life.dispatch_v01(prepared,current.request_id)
            except ValueError as exc:refusal=str(exc)
            else:raise ValueError('g35_revoked_action_executed')
        else:
            paid=life.dispatch_v01(prepared,current.request_id);receipt=abi.kernel_artifact_to_plain_dict_v01(paid['receipt'])
        after=len([v for v in world.CALLS if v[0]=='EXECUTOR'])
        branches.append(dict(name=name,bound=f.g35_record_to_plain_v01(prepared['bound']),registry=f.g35_record_to_plain_v01(host.registry),
            evidence=evidence,receipt=receipt,refusal=refusal,executor_delta=after-before))
    safe_request=_public_request_v01(request)
    body=dict(request=safe_request,selected_plan=asdict(sem['selected_plan']),contributions=e.plain_value_v01(sem['contributions']),
        work=f.g35_record_to_plain_v01(quote['results']),admissions=f.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(v) for v in quote['common']['catalogue'])),
        topology=abi.kernel_artifact_to_plain_dict_v01(quote['program'].topology_artifact),result=abi.kernel_artifact_to_plain_dict_v01(artifact),
        selections=[[f.g35_record_to_plain_v01(v[x]) for x in ('kernel','inputs','result')] for v in selections],
        branches=branches,D_source_review=d_record,D_and_quote_us=quote_us)
    return body


def validate_source_v01(body):
    f._keys(body,('request','selected_plan','contributions','work','admissions','topology','result','selections','branches','D_source_review','D_and_quote_us'))
    req=body['request'];f._require('bank_private' not in req and 'user_private' not in req,'g35_testflix_privacy')
    rows=f.g35_validate_work_records_v01(body['work'],body['admissions'])
    f._require(tuple(r.work_id for r in rows)==('quote','period'),'g35_testflix_work')
    v=world.values_v01(rows[0].result.output);period=world.values_v01(rows[1].result.output)
    f._require(v['plan_id']==body['selected_plan']['plan_id'] and v['price_minor']==body['selected_plan']['price_minor'] and
        period['quote_ref']==v['quote_ref'] and period['valid_to']==req['now']+v['period_seconds'] and len(rows[1].consumed_fields)==2,'g35_testflix_consumption')
    f._require(rows[0].result.output==world.compute_output_v01('testflix.quote.v01',rows[0].invocation.inputs) and
        rows[1].result.output==world.compute_output_v01('testflix.period.v01',rows[1].invocation.inputs),'g35_testflix_output')
    topology,artifact=f._g35_checked_work_relation_v01(body['topology'],body['result'],rows,body['admissions'])
    f._require(artifact.owner_root_id==topology.owner_root_id=='root:testflix:user' and
        artifact.transaction_id==topology.transaction_id and artifact.parent_refs==(topology.artifact_id,),'g35_testflix_artifact_relation')
    decisions=[f.g35_validate_root_v01(v)[1] for v in body['selections']]
    f._require(len(decisions)==2 and decisions[0].decision=='ACCEPT' and decisions[1].decision=='NEEDS_USER' and
        all(v.transaction_id==artifact.transaction_id and v.target_root_id==artifact.owner_root_id for v in decisions),'g35_testflix_selection')
    f._require(body['D_source_review']['validation']['status']=='PASS','g35_testflix_D_source')
    facts=[f.g35_fact_v01(root=artifact.owner_root_id,transaction=artifact.transaction_id,proposal=topology.artifact_id,
        decision=decisions[0].decision_id,artifact=artifact.artifact_id,work_count=2),
        f.g35_fact_v01(root=artifact.owner_root_id,transaction=artifact.transaction_id,proposal=topology.artifact_id,decision=decisions[1].decision_id,
            task='NEEDS_INPUT',enforcement='BLOCKED_AS_REQUIRED',execution='NEEDS_USER',stage='ROOT')]
    f._require([b['name'] for b in body['branches']]==['lawful','revoked','fresh_neighbor'],'g35_testflix_branch_inventory')
    for b in body['branches']:
        f._keys(b,('name','bound','registry','evidence','receipt','refusal','executor_delta'))
        bound=f.g35_record_from_plain_v01(b['bound']);registry=f.g35_record_from_plain_v01(b['registry'])
        f._require(a.validate_native_root_bound_action_commit_packet_v01(bound)[0] and a.validate_action_commit_packet_registry_v02(registry)[0],'g35_testflix_native_history')
        canonical=bound.canonical_projection;decision=bound.root_decision_projection.root_decision_result
        digest=a.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(b['evidence']))
        f._require(canonical.dependency_candidate.dependency_records[0].content_sha256==digest,'g35_testflix_material_binding')
        f._require(decision.target_root_id=='root:testflix:bank' and b['evidence']['quote_ref']==v['quote_ref'] and
            b['evidence']['user_selection']==decisions[0].decision_id,'g35_testflix_source_relation')
        state=a.derive_action_packet_lifecycle_state_v01(registry,packet_id=bound.packet_identity.packet_id)
        if b['name']=='revoked':
            f._require(state.lifecycle_state=='REVOKED' and not state.executable and b['executor_delta']==0 and
                b['receipt'] is None and b['refusal']=='host_current_action_not_executable','g35_testflix_revocation')
            facts.append(f.g35_fact_v01(root=decision.target_root_id,transaction=decision.transaction_id,proposal=canonical.authorization_candidate.root_packet_authorization_candidate_id,
                decision=decision.decision_id,packet=bound.packet_identity.packet_id,task='SAFE_NO_DEAL',enforcement='BLOCKED_AS_REQUIRED',execution='EXPIRED_OR_REVOKED',stage='CURRENTNESS'))
        else:
            receipt=f.g35_validate_artifact_v01(b['receipt']);payload=b['receipt']['payload']
            execution=fw.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
            f._require(not fw.validate_native_execution_evidence_v01(execution) and execution.invocation.packet_id==bound.packet_identity.packet_id and
                receipt.transaction_id==canonical.transaction_id and payload['root_decision_id']==decision.decision_id and
                b['executor_delta']==1 and state.lifecycle_state=='RECEIPT_RECEIVED' and state.idempotency_disposition=='CONSUMED' and
                state.terminal_receipt_ref==receipt.artifact_id and not state.executable,'g35_testflix_receipt')
            f._require(world.values_v01(execution.result.output)['amount_minor']==v['price_minor'],'g35_testflix_payment_amount')
            facts.append(f.g35_fact_v01(root=decision.target_root_id,transaction=decision.transaction_id,proposal=canonical.authorization_candidate.root_packet_authorization_candidate_id,
                decision=decision.decision_id,packet=bound.packet_identity.packet_id,firewall=payload['firewall_decision_id'],receipts=(receipt.artifact_id,),effect_count=1))
    return facts
