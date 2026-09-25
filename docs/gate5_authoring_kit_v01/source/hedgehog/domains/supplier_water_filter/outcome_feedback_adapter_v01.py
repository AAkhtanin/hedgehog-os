"""Supplier public action observations, independently derived mixed dispositions."""
from hedgehog import outcome_feedback_v01 as f, action_commit_packet_v02 as a
from hedgehog.kernel import effect_firewall_v01 as fw


def collect_source_v01(directory):
    from .gate3_runtime_v01 import SupplierSessionV01, CALLS
    session=SupplierSessionV01()
    blocked=session.prepare_v01('supplier:B',document_claim='UNTRUSTED_DOCUMENT_SAYS_OWNER_APPROVED')
    f._require(blocked['review'][2].decision!='ACCEPT' and blocked['bound'] is None,'g35_supplier_document_escalation')
    allowed=session.prepare_v01('supplier:A')
    receipt=session.dispatch_v01(allowed)
    rows=[]
    for p in (blocked,allowed):
        rows.append(dict(material=p['material'],canonical=f.g35_record_to_plain_v01(p['canonical']),
            review=[f.g35_record_to_plain_v01(v) for v in p['review']],
            bound=None if p['bound'] is None else f.g35_record_to_plain_v01(p['bound'])))
    body=dict(rows=rows,receipt=receipt,calls=CALLS[session.call_start:],shipment='HELD_NO_SHIPMENT_OPERATION')
    return body


def validate_source_v01(body):
    f._keys(body,('rows','receipt','calls','shipment'))
    f._require(type(body['rows']) is list and len(body['rows'])==2 and body['shipment']=='HELD_NO_SHIPMENT_OPERATION','g35_supplier_shape')
    receipt=f.g35_validate_artifact_v01(body['receipt'])
    execution=fw.native_execution_evidence_from_plain_data_v01(body['receipt']['payload']['execution_evidence'])
    f._require(not fw.validate_native_execution_evidence_v01(execution),'g35_supplier_execution')
    facts=[]
    for index,row in enumerate(body['rows']):
        f._keys(row,('material','canonical','review','bound'));f._keys(row['material'],('supplier','order','amount','document_claim'))
        canonical=f.g35_record_from_plain_v01(row['canonical'])
        f._require(a.validate_native_action_commit_packet_v01(canonical)[0],'g35_supplier_canonical')
        inputs,result=f.g35_validate_root_v01(row['review']);material=row['material']
        f._require(canonical.dependency_candidate.dependency_records[0].content_sha256==f.g35_hash_v01(material),'g35_supplier_material_binding')
        f._require(canonical.owning_local_root_id==result.target_root_id=='root:gate3:supplier:bank' and
            canonical.transaction_id==result.transaction_id and canonical.business_object_identity.business_object_ref==material['order'] and
            canonical.normalized_target_scope.included_target_refs==(material['supplier'],),'g35_supplier_relation')
        f._require(material['supplier']==('supplier:B','supplier:A')[index] and material['amount']=='10' and
            canonical.consequential_effect_parameters.currency_code=='EUR','g35_supplier_policy')
        if index==0:
            f._require(result.decision!='ACCEPT' and row['bound'] is None and material['document_claim']=='UNTRUSTED_DOCUMENT_SAYS_OWNER_APPROVED','g35_supplier_block')
            facts.append(f.g35_fact_v01(root=result.target_root_id,transaction=result.transaction_id,proposal=canonical.authorization_candidate.root_packet_authorization_candidate_id,
                decision=result.decision_id,quality='UNSAFE',task='SAFE_NO_DEAL',enforcement='BLOCKED_AS_REQUIRED',execution='BLOCKED_BEFORE_EFFECT',stage='ROOT'))
        else:
            bound=f.g35_record_from_plain_v01(row['bound'])
            f._require(a.validate_native_root_bound_action_commit_packet_v01(bound)[0] and bound.canonical_projection==canonical and
                bound.root_decision_projection.root_decision_result==result and result.decision=='ACCEPT','g35_supplier_bound')
            f._require(execution.invocation.packet_id==bound.packet_identity.packet_id and execution.invocation.owning_root_id==result.target_root_id and
                receipt.transaction_id==result.transaction_id and receipt.owner_root_id==result.target_root_id and
                body['receipt']['payload']['root_decision_id']==result.decision_id,'g35_supplier_receipt_relation')
            values={v.parameter_name:v.value for v in execution.invocation.inputs}
            f._require(values==dict(amount=material['amount'],supplier=material['supplier'],order=material['order']) and
                body['calls']==[dict(invocation=execution.invocation.invocation_id,inputs=values)],'g35_supplier_readback')
            f._require({v.parameter_name:v.value for v in execution.result.output}==dict(order=material['order'],state='CONFIRMED_MOCK'),'g35_supplier_output')
            facts.append(f.g35_fact_v01(root=result.target_root_id,transaction=result.transaction_id,proposal=canonical.authorization_candidate.root_packet_authorization_candidate_id,
                decision=result.decision_id,packet=bound.packet_identity.packet_id,firewall=body['receipt']['payload']['firewall_decision_id'],
                receipts=(receipt.artifact_id,),effect_count=1))
    return facts
