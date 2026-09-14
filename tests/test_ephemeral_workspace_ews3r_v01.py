"""Focused presentation controls; staged media info is not a D/E acceptance."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error

import pytest

from demo.ephemeral_workspace_fixtures_v01 import generate
from hedgehog.domains.ephemeral_workspace import contracts_v01 as c
from hedgehog.domains.ephemeral_workspace import session_runtime_v01 as runtime
from hedgehog.domains.ephemeral_workspace import viewer_v01 as viewer
from tests.test_ephemeral_workspace_services_v01 import HtmlProbeInput, UI_PROBE_JS, request

RESOLVED_REQUEST=('Browse, rate and select the photographs, with manual exposure and crop adjustments to previews. '
    'Do not change originals. Video or sound are not needed. Keep the existing no-publication and separate-save restrictions.')

def evidence(name,value):
    root=os.environ.get('EWS3R_RUN_EVIDENCE')
    if root:
        path=Path(root)/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(c.canonical(value))


@pytest.fixture
def photo(tmp_path):
    expected=os.environ.get('EWS_EXPECTED_CANDIDATE')
    if expected:
        assert Path(runtime.__file__).resolve().is_relative_to(Path(expected))
    session=runtime.Workspace(tmp_path/'workspace',generate(tmp_path/'sources',1))
    try:
        yield session
    finally:
        session.close()
        assert all(s.process.poll() is not None for s in session.services)


# Reuse the existing DOM harness, adding a deferred fake HTTP response only.
# Production JavaScript is executed intact. This is NOT a rendered browser.
AUDIO_HARNESS=UI_PROBE_JS.split('(async()=>{',1)[0].replace(
    "}else if(path==='/approve'){",
    """}else if(path==='/audio-loss'){
                f.atSubmit={disabled:nodes.get('audio-loss').disabled,
                    label:nodes.get('audio-loss').textContent,result:nodes.get('result').textContent};
                await new Promise(resolve=>{f.releaseAudio=resolve;});
                ok=!f.audioError;
                f.state.owner_audio_action=null;
                f.state.media.status='SILENT_READY';f.state.media.audio='UNAVAILABLE';
                value=ok?copy(f.state):{error:f.audioError};
            }else if(path==='/approve'){""")
AUDIO_HARNESS+=r'''
(async()=>{
    const results=[];
    for(const [action,audio,label] of [
        ['CONTINUE_AFTER_LOSS','UNAVAILABLE','Continue after audio loss'],
        ['DISCONNECT','AVAILABLE','Disconnect owned audio sink']]){
        const s={...active(),media:{audio,status:'READY'},owner_audio_action:action};
        const f=fixture(pages.owner,s);await flush();
        assert.equal(f.node('audio-loss').disabled,false);
        assert.equal(f.node('audio-loss').textContent,label);
        assert.equal(f.calls.filter(x=>x.path==='/audio-loss').length,0);
        const completion=f.node('audio-loss').onclick();await flush();
        assert.equal(f.atSubmit.disabled,true);
        assert.match(f.atSubmit.label,/Validating/);
        assert.match(f.atSubmit.result,/current continuation/);
        const before=f.calls.length;await f.node('audio-loss').onclick();await f.tick();
        assert.equal(f.calls.length,before);
        f.releaseAudio();await completion;
        assert.equal(f.node('audio-loss').disabled,true);
        assert.equal(f.calls.filter(x=>x.path==='/audio-loss').length,1);
        results.push({action,label,submit:f.atSubmit,completed:f.node('result').textContent});
    }
    for(const [name,change] of [
        ['not_prepared',{owner_audio_action:null}],
        ['already_completed',{owner_audio_action:null,media:{audio:'UNAVAILABLE',status:'SILENT_READY'}}],
        ['no_media',{media:null,owner_audio_action:null}],
        ['unknown_action',{owner_audio_action:'UNKNOWN'}],
        ['expired',{status:'EXPIRED',current:false}],
        ['revoked',{status:'REVOKED',current:false}],
        ['closing',{status:'CLOSING',current:false}],
        ['closed',{status:'CLOSED_SUCCESS',current:false}]]){
        const f=fixture(pages.owner,{...active(),media:{audio:'AVAILABLE'},owner_audio_action:'DISCONNECT',...change});
        await flush();assert.equal(f.node('audio-loss').disabled,true);
        await f.node('audio-loss').onclick();
        assert.equal(f.calls.filter(x=>x.path==='/audio-loss').length,0);
        results.push({case:name,disabled:true});
    }
    const f=fixture(pages.owner,{...active(),media:{audio:'UNAVAILABLE'},owner_audio_action:'CONTINUE_AFTER_LOSS'});
    await flush();f.audioError='workspace_expired';
    const completion=f.node('audio-loss').onclick();await flush();f.releaseAudio();await completion;
    assert.equal(f.node('audio-loss').disabled,true);
    assert.equal(f.calls.filter(x=>x.path==='/audio-loss').length,1);
    results.push({case:'server_refusal_no_duplicate',result:f.node('result').textContent});
    console.log(JSON.stringify({scope:'PRODUCTION_JS_SIMULATED_DOM_HTTP_NOT_BROWSER',results}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
'''


def test_owner_audio_production_javascript():
    node=shutil.which('node')
    assert node,'Node required for production JavaScript control'
    result=subprocess.run([node,'-e',AUDIO_HARNESS],input=json.dumps(dict(owner=HtmlProbeInput(viewer.OWNER_HTML).payload())),
        text=True,capture_output=True,timeout=30)
    evidence('audio_js.json',dict(rc=result.returncode,stdout=result.stdout,stderr=result.stderr))
    assert result.returncode==0,result.stderr


def test_known_drs_mode_actual_http_and_role_refusal(photo):
    # A genuine Work-built Workspace with a mode-bearing presentation fixture.
    # No MemoryProvider descent or warm authorization is claimed by this test.
    v=viewer.Viewer(photo)
    rows=[]
    try:
        for mode,label in [('CONTROLLED_DETERMINISTIC','Controlled'),('LIVE','Live'),
                ('CAPTURED_REEXECUTION','Captured'),('DRS_REUSE_CANDIDATE','DRS reuse candidate')]:
            photo.mode=mode
            for url,token in [(v.owner_url,v.owner_token),(v.control_url,v.control_token)]:
                with request(url+'/',token) as response:
                    assert response.status==200
                    assert ('<span class="tag">'+label+'</span>').encode() in response.read()
            rows.append(dict(mode=mode,status=200))
        photo.mode='UNKNOWN'
        for url,token in [(v.owner_url,v.owner_token),(v.control_url,v.control_token)]:
            with pytest.raises(urllib.error.HTTPError) as exc:request(url+'/',token)
            assert exc.value.code==403
        photo.mode='CONTROLLED_DETERMINISTIC'
        for url,token,body,origin in [
                (v.control_url+'/audio-loss',v.control_token,{},None),
                (v.owner_url+'/audio-loss',v.control_token,{},None),
                (v.owner_url+'/audio-loss',v.owner_token,{},v.control_url),
                (v.control_url+'/approve',v.control_token,{},None),
                (v.owner_url+'/approve',v.control_token,{},None),
                (v.owner_url+'/audio-loss',v.owner_token,{},None)]:
            with pytest.raises(urllib.error.HTTPError) as exc:request(url,token,body,origin)
            assert exc.value.code==403
        assert photo.producer_counts['delta']==0 and len(photo.executed)==0
        evidence('mode_http.json',dict(scope='ACTUAL_HTTP_MODE_BEARING_WORKSPACE_NO_WARM_DESCENT',modes=rows,
            unknown=403,role_and_backend_refusals=6,delta=0,effects=0))
    finally:
        photo.mode='CONTROLLED_DETERMINISTIC'
        v.close()


def test_audio_continuation_state_information_only(photo,tmp_path):
    from hedgehog.domains.ephemeral_workspace.local_services_v01 import Service
    audio=Service('audio',photo.id,photo.deadline,photo.directory/'logs')
    saved=dict(status=photo.status,contract=photo.contract,services=photo.services)
    before=(photo.host.revision,len(photo.executed),len(photo.history),photo.source.offset,photo.source.snapshot)
    rows=[]
    try:
        assert photo.state()['owner_audio_action'] is None
        # Stage only read-side media fields, never a returned D/E result or grant.
        photo.status='ACTIVE'
        photo.contract=dict(photo.contract,media=dict(audio=True))
        photo.services=[audio]
        photo.media_state.update(audio='AVAILABLE',status='READY')
        assert photo.state()['owner_audio_action'] is None  # No prepared review.
        photo.media_review=dict(output=dict(audio=True,audio_policy='SILENT_CONTINUE'))
        assert photo.state()['owner_audio_action']=='DISCONNECT'
        rows.append(dict(case='available',action=photo.state()['owner_audio_action']))
        audio.process.kill();audio.process.wait(timeout=10)
        state=photo.state()
        assert state['media']['audio']=='UNAVAILABLE'
        assert state['owner_audio_action']=='CONTINUE_AFTER_LOSS'
        assert photo.audio_fault['kind']=='OWNED_PROCESS_EXIT'
        rows.append(dict(case='owned_dead_process',action=state['owner_audio_action']))
        fault=deepcopy(photo.audio_fault)
        for label,field,value in [('consumed','audio_loss',{}),('delta','media_delta',{}),
                ('expired','expires',0),('revoked','revoked',True),('closing','status','CLOSING'),
                ('closed','status','CLOSED_SUCCESS'),('no_owned_audio','services',[])]:
            original=getattr(photo,field)
            setattr(photo,field,value)
            try:assert photo.state()['owner_audio_action'] is None,label
            finally:setattr(photo,field,original)
            rows.append(dict(case=label,action=None))
        for output in (dict(audio=False,audio_policy='SILENT_CONTINUE'),dict(audio=True,audio_policy='UNKNOWN')):
            photo.media_review=dict(output=output)
            assert photo.state()['owner_audio_action'] is None
        photo.media_review=dict(output=dict(audio=True,audio_policy='REQUIRE_AUDIO'))
        assert photo.state()['owner_audio_action']=='CONTINUE_AFTER_LOSS'
        assert before==(photo.host.revision,len(photo.executed),len(photo.history),photo.source.offset,photo.source.snapshot)
        assert photo.producer_counts['delta']==0
        evidence('audio_state.json',dict(scope='STAGED_READ_SIDE_REVIEW_FIELDS_ACTUAL_OWNED_DEAD_PROCESS_NO_D_E',
            rows=rows,fault=fault,currentness_effects_history_source_unchanged=True))
    finally:
        receipt=audio.close()
        assert receipt['reaped']
        photo.status=saved['status'];photo.contract=saved['contract'];photo.services=saved['services']
        photo.media_review=None;photo.audio_fault=None;photo.audio_loss=None;photo.media_delta=None


def test_resolved_photo_intent_current_commands_separate_save(tmp_path):
    from demo.ephemeral_workspace_fixtures_v01 import generate_media
    from hedgehog.domains.ephemeral_workspace import semantic_roles_v01 as roles
    from hedgehog.domains.ephemeral_workspace import semantic_adapter_v01 as semantic
    root=Path(os.environ.get('EWS3R_RUN_EVIDENCE',tmp_path))/'clarified_photo'
    root.mkdir(parents=True)
    def put(name,body):
        (root/name).write_bytes(body if type(body) is bytes else c.canonical(body))
    phases=[]
    def phase(name,call):
        start=time.monotonic()
        with (root/'phases.jsonl').open('a') as f:f.write(json.dumps(dict(phase=name,event='START',monotonic=start))+'\n')
        result=call()
        row=dict(phase=name,event='RETURN',seconds=time.monotonic()-start)
        phases.append(row)
        with (root/'phases.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
        return result
    assets=phase('synthetic_sources',lambda:generate(root/'sources',2))
    media=generate_media(root/'available_media')
    original={p.name:c.digest(p.read_bytes()) for p in assets}
    session=phase('controlled_semantics_and_common_work',lambda:runtime.Workspace(root/'workspace',assets,RESOLVED_REQUEST,media=media))
    try:
        assert session.mode=='CONTROLLED_DETERMINISTIC' and len(session.captures)==3
        assert session.semantic_responses[0]['needs']==['browse','rate','select','exposure','crop']
        assert 'media' not in session.contract and not session.contract['source_write'] and not session.contract['publication']
        assert 'AudioSinkNeedle' in session.contract['dormant_classes']
        for i,record in enumerate(session.captures):
            assert record['context']['request']==RESOLVED_REQUEST
            assert record['context']['media_inventory'] and record['mode']=='CONTROLLED_DETERMINISTIC'
            semantic.validate_capture(record,roles.ROLES[i],record['context'])
        assert session.captures[2]['context']['obligations']==session.semantic_responses[1]
        assert session.route_review[2].decision=='ACCEPT'
        put('semantic_captures.json',session.captures)
        phase('OPEN',lambda:session.command('OPEN'))
        initial=session.preview.copy()
        put('preview_initial.png',session.photo_frame(initial['frame_ref']))
        phase('NEXT',lambda:session.command('NEXT'))
        assert session.preview['asset']!=initial['asset']
        phase('PREVIOUS',lambda:session.command('PREVIOUS'))
        assert session.preview['sha256']==initial['sha256']
        phase('RATE',lambda:session.command('RATE',4))
        phase('SELECT',lambda:session.command('SELECT',True))
        phase('EXPOSURE',lambda:session.command('EXPOSURE',5))
        exposed=session.preview.copy();put('preview_exposure.png',session.photo_frame(exposed['frame_ref']))
        assert exposed['sha256']!=initial['sha256']
        phase('CROP',lambda:session.command('CROP','SQUARE'))
        cropped=session.preview.copy();put('preview_crop.png',session.photo_frame(cropped['frame_ref']))
        assert cropped['sha256'] not in (initial['sha256'],exposed['sha256'])
        effect_count=len(session.executed)
        for op in ('PLAY','REVIEW_MEDIA'):
            with pytest.raises(ValueError,match='operation_not_allowed'):session.command(op)
        with pytest.raises(ValueError,match='save_approval_current'):session.command('SAVE','ews:approval:unissued')
        assert len(session.executed)==effect_count
        phase('REQUEST_SAVE',lambda:session.command('REQUEST_SAVE'))
        pending=deepcopy(session.pending)
        assert not (session.directory/'output/selection.json').exists()
        wrong=deepcopy(pending);wrong['slot']='different.json'
        with pytest.raises(ValueError,match='approval_candidate_changed'):session.approve(wrong)
        approval=phase('SCRIPTED_OWNER_CONFIRMATION',lambda:session.approve(pending,actor='SCRIPTED_OWNER_CONFIRMATION'))
        put('separate_approval.json',dict(actor='SCRIPTED_OWNER_CONFIRMATION',candidate=pending,approval=approval,
            origin='Explicit synthetic-fixture authorization; not a live owner click.'))
        phase('SAVE',lambda:session.command('SAVE',approval))
        sidecar=(session.directory/'output/selection.json').read_bytes()
        assert sidecar==c.canonical(pending['content'])+b'\n' and c.digest(sidecar)==pending['bytes_sha256']
        put('selection.json',sidecar)
        with pytest.raises(ValueError):session.command('SAVE',approval)
        assert list((session.directory/'output').iterdir())==[session.directory/'output/selection.json']
        assert all(r['root_decision']['decision']=='ACCEPT' for r in session.history)
        assert session.producer_counts['media_contract']==session.producer_counts['delta']==0
        assert all(s.role!='audio' for s in session.services)
        put('preview_comparison.json',dict(initial=initial,exposure=exposed,crop=cropped,source_sha256=original))
    finally:
        cleanup=phase('CLEANUP',lambda:session.close('SCRIPTED_OWNER_END'))
        put('cleanup.json',cleanup)
        put('report.json',session.report())
    assert cleanup['status']=='CLOSED_SUCCESS' and all(p['reaped'] for p in cleanup['processes'])
    assert not list((session.directory/'cache').iterdir())
    assert {p.name:c.digest(p.read_bytes()) for p in assets}==original
    put('COMPLETE.json',dict(status='PASS',request=RESOLVED_REQUEST,mode=session.mode,phases=phases,
        model_calls=0,E_executions=0,D_media_executions=0,common_work=True,source_preserved=True,
        sidecar_writes=1,cleanup=cleanup['status'],post_clarification_not_heldout=True))
