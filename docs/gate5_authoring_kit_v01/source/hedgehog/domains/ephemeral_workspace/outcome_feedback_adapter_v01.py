"""Current minimal Workspace source and pure safe-derived observation checks."""
import hashlib
import json
from pathlib import Path
from hedgehog import outcome_feedback_v01 as f
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import effect_firewall_v01 as fw
from . import contracts_v01 as c, capability_registry_v01 as caps
from . import semantic_roles_v01 as roles


def collect_source_v01(directory):
    from .session_runtime_v01 import Workspace
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    asset=directory/'synthetic_asset.ppm'
    asset.write_bytes(b'P6\n1 1\n255\n\x40\x80\xc0')
    request='Browse, rate and select photos; manual exposure and crop previews. Do not change originals. No video or sound.'
    session=Workspace(directory/'workspace',[asset],request,roles.ControlledProvider(),media=None)
    # The saved contract is the actual second result, never a replacement render.
    privacy=dict(decision='block',minimize='preview_without_metadata',conflicts=['synthetic_private_metadata'])
    try:roles.validate(roles.ROLES[2],privacy,{})
    except ValueError as exc:refusal=str(exc)
    else:raise ValueError('g35_privacy_not_refused')
    body=dict(request=request,roles=session.semantic_responses,contract=session.contract,
        work=f.g35_record_to_plain_v01(session.work_results),admissions=f.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(v) for v in session.catalogue[:2])),topology=abi.kernel_artifact_to_plain_dict_v01(session.program.topology_artifact),
        result=abi.kernel_artifact_to_plain_dict_v01(session.work_artifact),
        root=[f.g35_record_to_plain_v01(v) for v in session.route_review],
        privacy_input=privacy,privacy_refusal=refusal,asset_sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),
        services=len(session.services),effects=len(session.executed),producer_counts=session.producer_counts)
    return body


def validate_source_v01(body):
    f._keys(body,('request','roles','contract','work','admissions','topology','result','root','privacy_input','privacy_refusal',
        'asset_sha256','services','effects','producer_counts'))
    f._require(body['services']==0 and body['effects']==0 and body['producer_counts']==dict(photo_preview=0,media_contract=0,delta=0),'g35_workspace_effect')
    inputs,result=f.g35_validate_root_v01(body['root'])
    f._require(result.decision=='ACCEPT','g35_workspace_root')
    rows=f.g35_validate_work_records_v01(body['work'],body['admissions'])
    topology,artifact=f._g35_checked_work_relation_v01(body['topology'],body['result'],rows,body['admissions'])
    f._require(artifact.owner_root_id==topology.owner_root_id==result.target_root_id and
        artifact.transaction_id==topology.transaction_id==result.transaction_id,'g35_workspace_root_binding')
    f._require(tuple(r.work_id for r in rows)==('compile_contract','consume_contract'),'g35_workspace_work')
    actual=json.loads(caps.values(rows[-1].result.output)['material'])
    f._require(actual==body['contract']==roles.compile_contract(body['roles']),'g35_workspace_contract_output')
    f._require(caps.values(rows[1].invocation.inputs)=={'material':caps.values(rows[0].result.output)['material']} and
        len(rows[1].consumed_fields)==1 and rows[1].consumed_fields[0].source_artifact_id==rows[0].result.result_id and
        rows[1].consumed_fields[0].output_field=='/material' and
        rows[1].consumed_fields[0].downstream_artifact_id==rows[1].invocation.work_instance_id,'g35_workspace_consumption')
    f._require(body['result']['payload']['work_results'][1]['result']['result_id']==rows[1].result.result_id,'g35_workspace_artifact_result')
    try:roles.validate(roles.ROLES[2],body['privacy_input'],{})
    except ValueError as exc:f._require(str(exc)==body['privacy_refusal']=='privacy_refusal','g35_privacy_reason')
    else:raise ValueError('g35_privacy_refusal_missing')
    f._require(not actual['source_write'] and not actual['publication'] and actual['minimize']=='preview_without_metadata','g35_privacy_scope')
    common=dict(root=result.target_root_id,transaction=result.transaction_id,proposal=topology.artifact_id)
    return [f.g35_fact_v01(**common,decision=result.decision_id,artifact=artifact.artifact_id,work_count=len(rows)),
        f.g35_fact_v01(**common,task='SAFE_NO_DEAL',enforcement='BLOCKED_AS_REQUIRED',execution='BLOCKED_BEFORE_EFFECT',stage='SEMANTIC_VALIDATION')]
