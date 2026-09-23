"""AT4 supplied controls: saved actual execution, never an implicit collector."""
import copy
import json
import os
from pathlib import Path
import pytest
from hedgehog import outcome_feedback_v01 as f
from hedgehog.domains.ephemeral_workspace import incident_atlas_proof_v01 as p


@pytest.fixture(scope='module')
def saved_workspace():
    name=os.environ.get('AT4_SAVED_WORKSPACE')
    assert name,'Supply actual AT4 evidence; no pytest collection fallback'
    return json.loads(Path(name).read_bytes())


def test_workspace_supplied_complete_v01(saved_workspace):
    assert p.validate_workspace_v01(saved_workspace)


def test_workspace_W1_W2_actual_ingress_v01(saved_workspace):
    for row in saved_workspace['W1']+saved_workspace['W2']:p.validate_ingress_v01(row)
    p.validate_native_input_v01(saved_workspace)


def test_workspace_coherent_allowed_operation_not_refusal_v01(saved_workspace):
    row=copy.deepcopy(saved_workspace['W1'][0]);row['command']=dict(op='RATE',value=3)
    with pytest.raises(ValueError,match='atlas_workspace_ingress_was_allowed'):p.validate_ingress_v01(row)


def test_workspace_valid_packet_wrong_current_version_v01(saved_workspace):
    p.validate_native_input_v01(saved_workspace)
    row=copy.deepcopy(saved_workspace);row['native_input']['wrong_inputs']=row['native_input']['inputs']
    with pytest.raises(ValueError,match='atlas_workspace_wrong_input_context'):p.validate_native_input_v01(row)


def test_workspace_W3_original_restored_and_same_name_changed_v01(saved_workspace):
    p.validate_code_v01(saved_workspace['W3'])


def test_workspace_coherent_code_identity_substitution_v01(saved_workspace):
    row=copy.deepcopy(saved_workspace['W3']);row['original_source']=row['changed_source'];row['original_sha256']=row['changed_sha256']
    with pytest.raises(ValueError,match='atlas_workspace_code_source'):p.validate_code_v01(row)


def test_workspace_W4_closed_recipe_current_descent_v01(saved_workspace):
    p.validate_memory_v01(saved_workspace)


def test_workspace_recipe_executable_pointer_refused_v01(saved_workspace):
    row=copy.deepcopy(saved_workspace)
    row['memory_events'][0]['record']['content']['record']['artifact_pointers']=['invented:permission']
    with pytest.raises(ValueError,match='atlas_workspace_recipe_projection'):p.validate_memory_v01(row)


@pytest.mark.parametrize('label',('closed_permission','false_completed','invented_evidence','wrong_version','valid_old_result_as_current'))
def test_workspace_D1_contextual_poison_v01(saved_workspace,label):
    row=next(v for v in saved_workspace['D1_controls'] if v['label']==label)
    if row['supplied_result'] is not None:f.g35_validate_artifact_v01(row['supplied_result'])
    with pytest.raises(ValueError,match=row['reason']):
        p.atlas.check_summary_v01(row['derivative']['output'],row['context'],row['supplied_result'])


def test_workspace_native_missing_then_completed_v01(saved_workspace):
    p.validate_required_v01(saved_workspace)
    row=copy.deepcopy(saved_workspace);row['missing_required']['snapshot']['outcome']='COMPLETED'
    with pytest.raises(ValueError,match='atlas_workspace_required_missing_source'):p.validate_required_v01(row)


def test_workspace_false_success_not_feedback_sample_v01(saved_workspace):
    observed=saved_workspace['experience']['observation']
    source=f.PredictiveOutcomeSourceContextV01(p.c.canonical(observed['predictive']))
    good=f.OutcomeFeedbackEnvelopeV01(p.c.canonical(observed['feedback']))
    assert not f.validate_outcome_feedback_against_sources_v01(good,source_bundle=source,profile=f.PREDICTIVE_SOURCE_PROFILE_ID)
    old=saved_workspace['summary_capture']['capture_id']
    poison=p.c.identity('controlled_poison',saved_workspace['D1_controls'][1]['derivative'])
    def replace_refs(value):
        if type(value) is str:return value.replace(old,poison)
        if type(value) is list:return [replace_refs(v) for v in value]
        if type(value) is dict:return {k:replace_refs(v) for k,v in value.items()}
        return value
    bad=replace_refs(observed['feedback'])
    bad['feedback_id']=f._identity('g3_feedback_v01',{k:v for k,v in bad.items() if k!='feedback_id'})
    forged=f.OutcomeFeedbackEnvelopeV01(p.c.canonical(bad))
    errors=f.validate_outcome_feedback_against_sources_v01(forged,source_bundle=source,profile=f.PREDICTIVE_SOURCE_PROFILE_ID)
    assert errors, 'A reidentified positive caption is not evidence for the poisoned claim'
    assert saved_workspace['experience']['snapshot']['prior']['effective_count']==1


def test_workspace_actual_history_changes_consumed_work_v01(saved_workspace):
    assert p.workproof.validate_experience_v01(saved_workspace)
    p.validate_consumption_v01(saved_workspace)


def test_workspace_valid_wrong_work_cannot_substitute_v01(saved_workspace):
    row=copy.deepcopy(saved_workspace);old=row['experience']['observation']
    p.workproof.validate_work_v01(old)
    row['consumption']['material']['work_artifact_ref']=old['artifact']['artifact_id']
    row['consumption']['material']['output_sha256']=p.c.digest(old['output'])
    with pytest.raises(ValueError,match='atlas_workspace_consumed_result'):p.validate_consumption_v01(row)


def test_workspace_sidecar_requires_exact_confirmation_v01(saved_workspace):
    row=copy.deepcopy(saved_workspace);row['exact_approval']=row['previous_approval']
    with pytest.raises(ValueError,match='atlas_workspace_command_consumption|atlas_workspace_exact_approval'):p.validate_consumption_v01(row)


def test_workspace_original_positive_after_controls_v01(saved_workspace):
    assert p.validate_workspace_v01(json.loads(json.dumps(saved_workspace)))
