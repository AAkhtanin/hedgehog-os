"""W5 portable relationships. Fixture pins below are TEST_ONLY, not review."""
from copy import deepcopy
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from hedgehog.domains.wedding_seating import portable_v01 as p
from hedgehog.domains.wedding_seating import operator_v01 as operator


@pytest.fixture(scope='module')
def package():
    path = os.environ.get('WEDDING_PORTABLE_EVIDENCE')
    pin = os.environ.get('WEDDING_PORTABLE_EXPECTED_SHA256')
    if not path or not pin:
        pytest.skip('Explicit source-bound saved evidence and independent pin required; never recollect')
    root = Path(path)
    files = p.load_pinned_directory_v01(root,pin)
    return root,pin,files


def repin(tmp_path, files):
    """Reach semantic predicates under an explicitly test-supplied coherent pin."""
    files = dict(files)
    mapping = p.strict(files['source_map.json'])
    mapping['files'] = [r for r in mapping['files'] if r['path'] in files]
    for row in mapping['files']:
        row['sha256'] = p.sha(files[row['path']])
    files['source_map.json'] = p.canonical(mapping)
    return p._write_package(tmp_path,files,{})


def changed(files, member, change):
    value=p.strict(files[member]);change(value);files[member]=p.canonical(value)


def test_external_pin_and_positive_neighbor_v01(package,tmp_path):
    root,pin,files=package
    assert p.verify_v01(root,pin)['status']=='PASS'
    with pytest.raises(ValueError,match='external_pin_required'):p.verify_v01(root,None)
    with pytest.raises(ValueError,match='external_pin_mismatch'):p.verify_v01(root,'0'*64)
    replaced=dict(files);replaced['source_map.json']=p.canonical(dict(p.strict(files['source_map.json']),synthetic=False))
    repin(tmp_path/'replaced',replaced)
    with pytest.raises(ValueError,match='external_pin_mismatch'):p.verify_v01(tmp_path/'replaced',pin)
    assert p.verify_v01(root,pin)['status']=='PASS'


@pytest.mark.parametrize('case,reason',[
    ('source','installed_source_identity'),
    ('coefficient','exact_numeric_source_binding'),
    ('semantic','egress_projection'),
    ('intermediate','performed_intermediate_output:compile'),
    ('sample','hardware_sample_lineage'),
    ('selected','hardware_sample_lineage'),
    ('output','performed_material_output'),
    ('save','save_consumed_result_link'),
    ('time','save_recorded_event_time'),
    ('device','hardware_device_binding'),
    ('parent','consumed_resume_parent'),
    ('root','performed_root_scope'),
    ('submission_root','submission_root_scope'),
    ('missing','incomplete_or_malformed_supported_evidence'),
])
def test_coherent_completed_bundle_refusals_v01(package,tmp_path,case,reason):
    root,pin,original=package;files=dict(original);profile='KEEP_FAMILIAR_V01'
    if case=='source':
        k='w4/candidate/hedgehog/domains/wedding_seating/math_v01.py';files[k]+=b'\n# controlled source alteration\n'
    elif case=='coefficient':
        changed(files,f'w4/numeric/{profile}/numeric.json',lambda x:x['optimization'].update(offset=x['optimization']['offset']+1))
    elif case=='semantic':
        k='w3/story/A_intake.json';changed(files,k,lambda x:x.update(safe_intent='An independently changed intent.'))
        files['w4/basis_w3/story/A_intake.json']=files[k]
    elif case=='intermediate':
        def alter(x):
            material=p.strict(x['results'][1]['result']['output'][0]['value'])
            material['optimization']['offset']+=1
            raw=p.canonical(material).decode()
            x['results'][1]['result']['output'][0]['value']=raw
            x['results'][2]['invocation']['inputs'][0]['value']=raw
        changed(files,f'w4/native/{profile}/prepare.json',alter)
    elif case=='sample':
        k=f'w4/provider/{profile}_results.json';changed(files,k,lambda x:x['measurements'][0].__setitem__(0,1-x['measurements'][0][0]))
        changed(files,'w4/provider/ledger.json',lambda x:x['attempts'][0].update(raw_sha256=p.sha(files[k])))
    elif case=='selected':
        changed(files,f'w4/provider/{profile}_sample_validation.json',lambda x:x['selected'].update(shot_index=64))
    elif case=='output':
        def alter(x):
            x['output']['assignment']=[0]*12
            x['root_result']['selected_candidate_id']='wedding_result:'+p.sha(p.canonical(x['output']))
            last=p.strict(x['results'][-1]['result']['output'][0]['value']);last['safe_output']=x['output']
            x['results'][-1]['result']['output'][0]['value']=p.canonical(last).decode()
        changed(files,f'w4/native/{profile}/consume.json',alter)
    elif case=='save':
        def alter(x):
            items=dict(x[0]['root_input']['post_vv_bundle']['items'])
            items.update(required_evidence_refs=['work_results:foreign'],provided_evidence_refs=['work_results:foreign'])
            x[0]['root_input']['post_vv_bundle']['items']=list(items.items())
        changed(files,f'w4/outputs/{profile}/save_receipts.json',alter)
    elif case=='time':
        def alter(x):
            x[0]['claim']['expires']=0
            x[0]['root_result']['selected_candidate_id']='wedding_save:'+p.sha(p.canonical(x[0]['claim']))
        changed(files,f'w4/outputs/{profile}/save_receipts.json',alter)
    elif case=='device':
        changed(files,'w4/provider/ledger.json',lambda x:x['attempts'][0]['metadata'].update(deviceArn='arn:foreign'))
    elif case=='parent':
        def alter(x):
            x['material']['prepare_result_ref']='work_results:foreign';x['owner']['parent_ref']='work_results:foreign'
        changed(files,f'w4/native/{profile}/consume.json',alter)
    elif case in ('root','submission_root'):
        def alter_root(x):
            for field in ('root_input','root_result'):
                x[field].update(target_root_id='organizer:foreign',transaction_id='transaction:foreign')
        if case=='root':
            changed(files,f'w4/native/{profile}/consume.json',alter_root)
        else:
            changed(files,'w4/provider/ledger.json',lambda x:alter_root(x['attempts'][0]['approval']))
    else:
        del files[f'w4/provider/{profile}_results.json']
    test_pin=repin(tmp_path/'TEST_ONLY_COHERENT',files)
    with pytest.raises(ValueError,match=reason):p.verify_v01(tmp_path/'TEST_ONLY_COHERENT',test_pin)
    assert p.sha((root/'MANIFEST.json').read_bytes())==pin


def test_equivalent_copy_render_and_read_only_v01(package,tmp_path):
    root,pin,files=package
    copy_pin=repin(tmp_path/'copy',deepcopy(files))
    expected=p.verify_v01(root,pin)
    assert p.verify_v01(tmp_path/'copy',copy_pin)==expected
    out=tmp_path/'render';result=p.render_v01(root,pin,out)
    assert result['new_root_or_effect_calls']==0
    for row in result['files']:
        assert (out/row['output']).read_bytes()==files[row['source_member']]
    assert p.load_pinned_directory_v01(root,pin)==files


def test_local_live_and_resume_refuse_before_transport_v01(tmp_path):
    def args(**kw):
        values=dict(mode='live-qpu',allow_native=False,allow_external=False,config=None,authorization=None,authorization_sha256=None,output=tmp_path/'episode')
        values.update(kw);return SimpleNamespace(**values)
    with pytest.raises(ValueError,match='explicit_native_authorization_required'):operator.run_v01(args())
    with pytest.raises(ValueError,match='operator_config_required'):operator.run_v01(args(allow_native=True))
    config=tmp_path/'config.json';config.write_bytes(p.canonical({}))
    with pytest.raises(ValueError,match='explicit_external_authorization_required'):operator.run_v01(args(allow_native=True,config=config))
    with pytest.raises(ValueError,match='fresh_authorization_required'):operator.run_v01(args(allow_native=True,allow_external=True,config=config))
    with pytest.raises(ValueError,match='existing_attempt_required'):operator.run_v01(args(mode='resume-provider',allow_native=True,config=config))
    folder=tmp_path/'episode/provider';folder.mkdir(parents=True)
    (folder/'ledger.json').write_bytes(p.canonical(dict(attempts=[dict(state='UNKNOWN_SUBMISSION')])))
    with pytest.raises(ValueError,match='UNKNOWN_SUBMISSION_REQUIRES_EXACT_RECONCILIATION'):operator.run_v01(args(mode='resume-provider',allow_native=True,config=config))
    (folder/'ledger.json').write_bytes(p.canonical(dict(attempts=[dict(state='VALIDATED_AND_SAVED',task_arn='recorded')])) )
    with pytest.raises(ValueError,match='completed_episode_read_only'):operator.run_v01(args(mode='resume-provider',allow_native=True,config=config))
