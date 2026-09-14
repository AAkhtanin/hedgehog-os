"""Actual loopback boundaries and cleanup; no fabricated provider responses."""
import base64
from copy import deepcopy
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import pytest
from PIL import Image, PngImagePlugin
from demo.ephemeral_workspace_fixtures_v01 import generate
from hedgehog.domains.ephemeral_workspace import contracts_v01 as c
from hedgehog.domains.ephemeral_workspace import semantic_roles_v01 as roles
from hedgehog.domains.ephemeral_workspace.local_services_v01 import Service
from hedgehog.domains.ephemeral_workspace.media_v01 import render, preview_dimensions, validate_transfer
from hedgehog.domains.ephemeral_workspace.session_runtime_v01 import Workspace
from hedgehog.domains.ephemeral_workspace.viewer_v01 import Viewer, OWNER_HTML, CONTROL_HTML


def request(url,token,body=None,origin=None):
    headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
    if origin:headers['Origin']=origin
    req=urllib.request.Request(url,data=None if body is None else c.canonical(body),headers=headers)
    return urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=120)


def test_real_media_display_boundaries_and_sequence(tmp_path):
    assets=generate(tmp_path/'sources',1)
    (tmp_path/'logs').mkdir()
    media=Service('media','ews:test',time.monotonic()+60,tmp_path/'logs',{'asset:1':[str(assets[0]),c.digest(assets[0].read_bytes())]})
    display=Service('display','ews:test',time.monotonic()+60,tmp_path/'logs')
    try:
        image=media.rpc('render',dict(asset='asset:1',exposure=0,crop='ORIGINAL',preview='fit'))
        changed=media.rpc('render',dict(asset='asset:1',exposure=5,crop='SQUARE',preview='fit'))
        assert image['sha256']!=changed['sha256']
        display.rpc('put',dict(png=image['png'],sha256=image['sha256'],frame_ref='ews:frame:1'))
        with request(display.url+'/frame/ews:frame:1',display.read_token) as response:
            assert c.digest(response.read())==image['sha256']
        for path,token,origin in [('/sources',display.read_token,None),('/frame/ews:frame:1',media.read_token,None),
                                  ('/frame/ews:frame:1',display.read_token,'https://unrelated.invalid')]:
            with pytest.raises(urllib.error.HTTPError):
                request(display.url+path,token,origin=origin)
        for session,sequence in [('ews:foreign',3),('ews:test',1)]:
            with pytest.raises(urllib.error.HTTPError):
                request(media.url+'/rpc',media.token,dict(version=c.VERSION,session=session,sequence=sequence,op='render',
                    args=dict(asset='asset:1',exposure=0,crop='ORIGINAL',preview='fit')))
        with request(display.url+'/frame/ews:frame:1',display.read_token) as response:
            assert response.status==200
    finally:
        assert media.close()['reaped']
        assert display.close()['reaped']


def test_http_owner_control_origin_and_current_frame(tmp_path):
    assets=generate(tmp_path/'sources',1)
    session=Workspace(tmp_path/'workspace',assets)
    viewer=None
    try:
        session.command('OPEN')
        viewer=Viewer(session)
        with request(viewer.owner_url+'/',viewer.owner_token) as response:
            assert b'Owner confirmation' in response.read()
        with request(viewer.control_url+'/',viewer.control_token) as response:
            assert b'Current derived photograph' in response.read()
        for url,token,body,origin in [(viewer.owner_url+'/approve',viewer.control_token,{},None),
            (viewer.control_url+'/command',viewer.owner_token,{},None),
            (viewer.control_url+'/state',viewer.control_token,None,'https://foreign.invalid'),
            (viewer.control_url+'/sources',viewer.control_token,None,None)]:
            with pytest.raises(urllib.error.HTTPError):
                request(url,token,body,origin)
        with request(viewer.control_url+'/frame/'+session.preview['frame_ref'],viewer.control_token) as response:
            assert c.digest(response.read())==session.preview['sha256']
        original=assets[0].read_bytes()
        assets[0].write_bytes(b'changed source')
        try:
            with pytest.raises(urllib.error.HTTPError):
                request(viewer.control_url+'/frame/'+session.preview['frame_ref'],viewer.control_token)
        finally:
            assets[0].write_bytes(original)
        with request(viewer.control_url+'/frame/'+session.preview['frame_ref'],viewer.control_token) as response:
            assert response.status==200
        body=dict(version=1,session=session.id,sequence=1,command=dict(op='SAVE',value='ews:approval:forged'))
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.control_url+'/command',viewer.control_token,body)
        body=dict(version=True,session=session.id,sequence=1,command=dict(op='NEXT',value=None))
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.control_url+'/command',viewer.control_token,body)
        session.close('OWNER_END')
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.control_url+'/frame/'+session.preview['frame_ref'],viewer.control_token)
    finally:
        if viewer:viewer.close()
        session.close()
    assert session.status=='CLOSED_SUCCESS' and not (session.directory/'output/selection.json').exists()


class HtmlProbeInput(HTMLParser):
    def __init__(self,html):
        super().__init__()
        self.elements=[]
        self.script=''
        self.in_script=False
        self.feed(html)

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.elements.append(dict(tag=tag,attrs=attrs))
        if tag=='script':self.in_script=True

    def handle_endtag(self,tag):
        if tag=='script':self.in_script=False

    def handle_data(self,data):
        if self.in_script:self.script+=data

    def payload(self):
        return dict(elements=self.elements,script=self.script)


# Adapted from the supplied Node close reproducer. DOM/HTTP are simulated here;
# the script and element inventory are parsed from the actual production HTML.
UI_PROBE_JS = r'''
const assert=require('node:assert/strict');
const vm=require('node:vm');
const pages=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const copy=value=>JSON.parse(JSON.stringify(value));
const flush=async()=>{for(let i=0;i<8;i++)await new Promise(resolve=>setImmediate(resolve));};
function active(allowed=['NEXT','PREVIOUS','RATE','SELECT','EXPOSURE','CROP','REQUEST_SAVE']){
    return {session:'ews:test',root:'root:test',version:1,status:'ACTIVE',current:true,current_reason:null,
        allowed,control_sequence:0,index:0,assets:[{selected:false,rating:0,exposure:0,crop:'ORIGINAL'}],
        preview:{frame_ref:'ews:frame:1'},pending:null,saved:null,mode:'CONTROLLED_DETERMINISTIC',
        owner_approval_available:false,owner_cleanup_available:true,cleanup:null};
}
function fixture(page,state=active()){
    const nodes=new Map(),all=[],listeners=new Map(),intervals=new Map(),calls=[],revoked=[];
    let timer=0;
    function element(tag,attrs={}){
        const node={tag,attrs:{...attrs},dataset:{},children:[],disabled:Object.hasOwn(attrs,'disabled'),
            hidden:Object.hasOwn(attrs,'hidden'),textContent:'',contentWindow:{},className:'',
            classList:{toggle(){}},appendChild(child){this.children.push(child);},
            remove(){this.removed=true;if(this.attrs.id)nodes.delete(this.attrs.id);},
            getAttribute(key){return Object.hasOwn(this.attrs,key)?this.attrs[key]:null;},
            removeAttribute(key){delete this.attrs[key];}};
        Object.defineProperty(node,'src',{get(){return this.attrs.src||'';},set(value){this.attrs.src=value;}});
        all.push(node);if(attrs.id)nodes.set(attrs.id,node);return node;
    }
    for(const entry of page.elements)element(entry.tag,entry.attrs);
    const f={state:copy(state),nodes,intervals,listeners,calls,revoked,commandError:null,approveError:null,stateError:false,frameError:false,
        cleanup:{status:'CLOSED_SUCCESS',reason:'OWNER_END',foreign_preserved:[]}};
    class ProbeURL extends URL {}
    ProbeURL.createObjectURL=()=> 'blob:derived';ProbeURL.revokeObjectURL=value=>revoked.push(value);
    const context={document:{getElementById:id=>nodes.get(id)||null,createElement:tag=>element(tag),
        querySelectorAll:()=>all.filter(node=>!node.removed&&['button','input','select'].includes(node.tag))},
        location:{hash:'#private-test-token',pathname:'/'},history:{replaceState(){}},
        addEventListener:(name,fn)=>{listeners.set(name,fn);},
        setInterval:fn=>{intervals.set(++timer,fn);return timer;},clearInterval:id=>intervals.delete(id),
        parent:{postMessage(){}},URL:ProbeURL,JSON,
        fetch:async(path,options={})=>{
            calls.push({path,options});let ok=true,value;
            if(path==='/state'){ok=!f.stateError;value=ok?copy(f.state):{error:'state unavailable'};}
            else if(path==='/control-link')value={url:'http://127.0.0.1:2/#separate-control-token'};
            else if(path.startsWith('/frame/')){ok=!f.frameError;value={error:'frame denied'};}
            else if(path.startsWith('/media-frame/')){ok=!f.mediaFrameError;value={error:'current_media_frame'};}
            else if(path==='/end'){
                value=copy(f.cleanup);f.state={...f.state,status:value.status,current:false,pending:null,
                    owner_approval_available:false,owner_cleanup_available:false,cleanup:value};
            }else if(path==='/command'){
                f.state.control_sequence++;if(f.afterCommand)f.afterCommand();
                ok=!f.commandError;value=ok?copy(f.state):{error:f.commandError};
            }else if(path==='/approve'){
                if(f.afterApprove)f.afterApprove();ok=!f.approveError;
                value=ok?copy(f.state):{error:f.approveError};
            }else throw Error('unexpected route '+path);
            return {ok,json:async()=>value,blob:async()=>({derived:true})};
        }};
    vm.createContext(context);vm.runInContext(page.script,context);
    f.node=id=>nodes.get(id);
    f.tick=async()=>{for(const fn of [...intervals.values()])fn();await flush();};
    f.buttons=()=>all.filter(node=>['button','input','select'].includes(node.tag));
    f.event=(name,value={})=>{const fn=listeners.get(name);if(fn)fn(value);};
    return f;
}
(async()=>{
    const results=[];
    for(const status of ['CLOSED_SUCCESS','CLEANUP_INCOMPLETE']){
        const f=fixture(pages.owner);await flush();
        f.cleanup={status,reason:'OWNER_END',foreign_preserved:status==='CLEANUP_INCOMPLETE'?['preview_0001.png']:[],
            retained_reason:'OWNERSHIP_OR_CONTENT_CHANGED_OR_UNVERIFIABLE_NOT_REMOVED'};
        const frame=f.node('controls'),queued=[...f.intervals.values()];
        assert.equal(f.node('end').disabled,false);await f.node('end').onclick();await flush();
        const text=f.node('result').textContent;
        if(status==='CLOSED_SUCCESS')assert.equal(text,'Workspace closed.');
        else{assert.ok(text.includes('CLEANUP_INCOMPLETE'));assert.ok(text.includes('preview_0001.png'));
            assert.ok(text.includes(f.cleanup.retained_reason));assert.ok(!text.includes('Workspace closed.'));}
        assert.equal(f.node('controls'),undefined);assert.equal(f.node('end').disabled,true);
        assert.equal(f.node('confirm').disabled,true);assert.equal(f.intervals.size,0);
        for(const fn of queued)fn();await flush();
        f.event('message',{source:frame.contentWindow,origin:'http://127.0.0.1:2',data:{type:'ews-state-changed'}});await flush();
        assert.equal(f.node('result').textContent,text);
        results.push({case:status,displayed:text,removed_element_callbacks:'PASS'});
    }
    {
        const s=active();s.pending={content:{selection:[]}};s.owner_approval_available=true;
        const f=fixture(pages.owner,s);await flush();assert.equal(f.node('confirm').disabled,false);
        f.approveError='approval changed';f.afterApprove=()=>{f.state.owner_approval_available=false;f.state.pending=null;};
        await f.node('confirm').onclick();await flush();
        assert.equal(f.node('confirm').disabled,true);assert.equal(f.node('end').disabled,false);
        f.state={...s,status:'EXPIRED',current:false,current_reason:'workspace_expired'};
        await f.tick();assert.equal(f.node('confirm').disabled,true);assert.equal(f.node('controls').hidden,true);
        assert.ok(f.node('result').textContent.includes('EXPIRED'));
        const count=f.calls.length;await f.node('confirm').onclick();assert.equal(f.calls.length,count);
        results.push({case:'owner_approval_error_then_expiry',status:'PASS'});
    }
    {
        const f=fixture(pages.control,active(['NEXT','RATE']));await flush();
        assert.equal(f.node('next').disabled,false);assert.equal(f.node('selected').disabled,true);
        f.commandError='controlled refusal';f.afterCommand=()=>{f.state.allowed=['RATE'];};
        await f.node('next').onclick();await flush();
        assert.equal(f.node('next').disabled,true);assert.equal(f.node('exposure').disabled,true);
        assert.equal(f.node('crop').disabled,true);assert.equal(f.node('selected').disabled,true);
        assert.equal(f.node('request-save').disabled,true);
        assert.ok(f.node('rating').children.every(node=>!node.disabled));
        f.commandError=null;f.afterCommand=()=>{f.state.version++;};
        await f.node('rating').children[0].onclick();await flush();
        const commands=f.calls.filter(call=>call.path==='/command').map(call=>JSON.parse(call.options.body));
        assert.deepEqual(commands.map(value=>value.command.op),['NEXT','RATE']);
        assert.deepEqual(commands.map(value=>value.sequence),[1,2]);
        results.push({case:'error_then_current_allowed_subset_and_positive',status:'PASS'});
    }
    for(const status of ['EXPIRED','REVOKED','WRITE_UNCERTAIN','CLOSED_SUCCESS','CLEANUP_INCOMPLETE']){
        const f=fixture(pages.control);await flush();assert.equal(f.node('preview').src,'blob:derived');
        f.state={...f.state,status,current:false,allowed:[],preview:null,current_reason:'workspace_not_current'};
        await f.tick();assert.ok(f.buttons().every(node=>node.disabled));
        assert.equal(f.node('preview').getAttribute('src'),null);assert.ok(f.revoked.includes('blob:derived'));
        assert.equal(f.intervals.size,0);const count=f.calls.length;await f.node('next').onclick();
        assert.equal(f.calls.length,count);assert.ok(f.node('status').textContent.includes(status));
        results.push({case:'control_'+status,status:'PASS'});
    }
    for(const failure of ['stateError','frameError']){
        const f=fixture(pages.control);await flush();f[failure]=true;await f.tick();
        assert.ok(f.buttons().every(node=>node.disabled));assert.equal(f.node('preview').getAttribute('src'),null);
        f[failure]=false;f.state.allowed=['NEXT'];await f.tick();
        assert.equal(f.node('next').disabled,false);assert.equal(f.node('selected').disabled,true);
        f.event('pagehide');assert.equal(f.intervals.size,0);
        results.push({case:failure+'_fail_closed_and_recovery',status:'PASS'});
    }
    process.stdout.write(JSON.stringify({scope:'Actual production HTML scripts; simulated DOM and HTTP in Node, not browser acceptance',results},null,2)+'\n');
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
'''


def test_required_audio_actual_process_death_D_gated(tmp_path):
    import os
    from demo.ephemeral_workspace_fixtures_v01 import generate_media
    from hedgehog.domains.ephemeral_workspace.evidence_v01 import save_report,media_value
    root=Path(os.environ.get('EWS3_CRASH_ROOT',str(tmp_path)))
    root.mkdir(parents=True,exist_ok=True)
    s=Workspace(root/'workspace',generate(root/'photos',2),c.REQUEST_SPEECH,media=generate_media(root/'media'))
    try:
        s.command('OPEN');s.prepare_media();s.command('PLAY');time.sleep(0.7)
        assert s.media_state['samples']>0 and s.media_thread.is_alive()
        audio=next(v for v in s.services if v.role=='audio')
        # Failure injection affects only this test's actual owned unreaped child.
        audio.process.kill();audio.process.wait()
        time.sleep(0.6)
        before=len(s.executed)
        for op in ('PLAY','REVIEW_MEDIA'):
            with pytest.raises(ValueError,match='audio_unavailable_requires_current_continuation'):s.command(op)
        assert len(s.executed)==before and s.audio_loss is None
        assert s.media_state['audio']=='UNAVAILABLE' and 'PLAY' not in s.state()['allowed']
        assert s.audio_fault['returncode'] is not None
        s.command('SELECT',True);assert s.edits['asset:1']['selected']
        receipt=audio.close()
        assert receipt['receipt'] is None and receipt['close_outcome']=='ALREADY_EXITED'
        (root/'crash_control.json').write_bytes(c.canonical(dict(status='PASS',fault=s.audio_fault,receipt=receipt,
            refused_commands=['PLAY','REVIEW_MEDIA'],effect_delta=0,photo_selection=True,D_output=s.media_review['output'])))
        (root/'D_work.json').write_bytes(c.canonical(media_value(s.media_review['artifact'])))
    finally:
        s.close();save_report(s,root/'evidence')
        assert all(v.process.poll() is not None for v in s.services)
        assert s.media_thread is None or not s.media_thread.is_alive()


def test_audio_exact_finite_batches_and_recovery(tmp_path):
    import wave
    from demo.ephemeral_workspace_fixtures_v01 import generate_media
    from hedgehog.domains.ephemeral_workspace.media_v01 import load_media
    fixture=load_media(generate_media(tmp_path/'media'))
    with wave.open(str(fixture['audio']),'rb') as stream:pcm=stream.readframes(64000)
    chunks=[pcm[i:i+8000] for i in range(0,len(pcm),8000)]
    logs=tmp_path/'logs';logs.mkdir()
    audio=Service('audio','ews:scope',time.monotonic()+20,logs,pcm_chunks=[c.digest(v) for v in chunks])
    def payload(index,batch='ews:media_batch:one'):
        return dict(pcm=base64.b64encode(chunks[index]).decode(),sha256=c.digest(chunks[index]),
            sample_offset=index*4000,frame_ref='ews:media_frame:'+str(index),batch_ref=batch)
    try:
        assert audio.rpc('observe',{})['samples']==0
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',payload(0))
        begin=dict(batch_ref='ews:media_batch:one',sample_offset=0,deadline=time.monotonic()+8)
        assert audio.rpc('begin',begin)['started']
        bad=dict(payload(0),pcm=base64.b64encode(bytes(8000)).decode(),sha256=c.digest(bytes(8000)))
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',bad)
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',payload(1))
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',payload(0,'ews:media_batch:foreign'))
        assert audio.rpc('consume',payload(0))['samples']==4000
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',payload(0))
        assert audio.rpc('consume',payload(1))['sample_offset']==4000
        audio.rpc('end',{})
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',payload(2))
        with pytest.raises(urllib.error.HTTPError):audio.rpc('begin',begin)
        fresh=dict(batch_ref='ews:media_batch:two',sample_offset=8000,deadline=time.monotonic()+0.15)
        audio.rpc('begin',fresh);time.sleep(0.2)
        with pytest.raises(urllib.error.HTTPError):audio.rpc('consume',payload(2,fresh['batch_ref']))
        fresh=dict(batch_ref='ews:media_batch:three',sample_offset=8000,deadline=time.monotonic()+4)
        audio.rpc('begin',fresh)
        actual=audio.rpc('consume',payload(2,fresh['batch_ref']))
        assert actual['sha256']==c.digest(chunks[2]) and actual['resource']==audio.nonce and actual['session']=='ews:scope'
        assert audio.rpc('observe',{})['samples']==12000
        receipt=audio.close()
        assert receipt['receipt']['samples']==12000 and receipt['reaped']
        with pytest.raises(OSError):audio.rpc('observe',{})
    finally:audio.close()


def test_actual_html_javascript_state_controls():
    node=shutil.which('node')
    if node is None:pytest.skip('Node unavailable; JavaScript logic acceptance unverified')
    payload=dict(owner=HtmlProbeInput(OWNER_HTML).payload(),control=HtmlProbeInput(CONTROL_HTML).payload())
    result=subprocess.run([node,'-e',UI_PROBE_JS],input=json.dumps(payload),text=True,capture_output=True,check=False)
    assert result.returncode==0,result.stderr
    assert len(json.loads(result.stdout)['results'])==11


def test_media_html_refusal_recovery_preserves_photo_controls():
    script=UI_PROBE_JS.split('(async()=>{')[0]+r'''
(async()=>{
 const s=active(['NEXT','PLAY','PAUSE']);s.media={position:1,audio:'AVAILABLE',status:'PLAYING',frame_ref:'ews:frame:one'};
 const f=fixture(pages.control,s);await flush();assert.equal(f.node('media-preview').src,'blob:derived');
 f.mediaFrameError=true;f.state.media.frame_ref='ews:frame:two';await f.tick();
 assert.equal(f.node('media-preview').src,'');assert.equal(f.node('media-preview').hidden,true);
 assert.match(f.node('audio-state').textContent,/unavailable/);assert.equal(f.node('next').disabled,false);
 assert.equal(f.node('preview').src,'blob:derived');
 f.mediaFrameError=false;await f.tick();assert.equal(f.node('media-preview').hidden,false);
 assert.equal(f.node('media-preview').src,'blob:derived');assert.equal(f.node('audio-state').textContent,'Audio: AVAILABLE | PLAYING');
 f.event('pagehide');assert.equal(f.node('media-preview').src,'');
 process.stdout.write('media refusal, recovery and photo preservation PASS\n');
})().catch(e=>{process.stderr.write(e.stack);process.exitCode=1;});'''
    node=shutil.which('node')
    assert node is not None
    payload=dict(control=HtmlProbeInput(CONTROL_HTML).payload())
    result=subprocess.run([node,'-e',script],input=json.dumps(payload),text=True,capture_output=True)
    assert result.returncode==0,result.stderr


def test_media_snapshot_atomic_reference_and_close(tmp_path):
    import threading
    s=Workspace(tmp_path/'w',generate(tmp_path/'photos',1))
    try:
        s.command('OPEN')
        a=('a',c.digest(b'a'),b'a');b=('b',c.digest(b'b'),b'b')
        stop=threading.Event()
        def publish():
            while not stop.is_set():s.media_snapshot=a;s.media_snapshot=b
        thread=threading.Thread(target=publish);thread.start()
        try:
            for _ in range(10000):
                for ref,expected in [('a',b'a'),('b',b'b')]:
                    try:assert s.media_frame(ref)==expected
                    except ValueError as exc:assert str(exc)=='current_media_frame'
        finally:stop.set();thread.join()
        s.media_snapshot=a;assert s.media_frame('a')==b'a'
    finally:s.close()
    assert s.media_snapshot is None


def test_expiry_and_foreign_preview_preservation(tmp_path):
    assets=generate(tmp_path/'sources',1)
    session=Workspace(tmp_path/'workspace',assets)
    try:
        session.command('OPEN')
        path=next(iter(session.owned))
        path.unlink();path.write_bytes(b'foreign replacement')
        session.source.offset=1201
        with pytest.raises(ValueError,match='workspace_expired'):
            session.command('NEXT')
        result=session.close('CONTROLLED_CLOCK_TTL_EXPIRED')
        assert result['status']=='CLEANUP_INCOMPLETE' and path.read_bytes()==b'foreign replacement'
        assert all(s.process.poll() is not None for s in session.services)
    finally:
        session.close()


def test_root_withdrawal_stops_actual_active_service(tmp_path):
    assets=generate(tmp_path/'sources',1)
    session=Workspace(tmp_path/'workspace',assets)
    try:
        session.command('OPEN')
        assert session.preview is not None
        session.revoke()
        assert session.withdrawal['decision']=='ACCEPT' and session.revoked
        with pytest.raises(ValueError,match='workspace_not_current'):
            session.command('NEXT')
        assert all(s.process.poll() is not None for s in session.services)
    finally:
        session.close()


def test_partial_activation_decode_failure_rolls_back_own_processes(tmp_path):
    source=tmp_path/'invalid.png';source.write_bytes(b'not a decodable image')
    session=Workspace(tmp_path/'workspace',(source,))
    try:
        with pytest.raises(ValueError):
            session.command('OPEN')
        assert len(session.services)==2 and all(s.process.poll() is not None for s in session.services)
        assert session.status=='CLOSED_SUCCESS' and source.read_bytes()==b'not a decodable image'
    finally:
        session.close()


def test_service_self_expires_without_another_command(tmp_path):
    (tmp_path/'logs').mkdir()
    service=Service('display','ews:expiry',time.monotonic()+1,tmp_path/'logs')
    try:
        assert service.process.wait(timeout=4)==0
        assert service.close()['reaped']
    finally:
        service.close()


def private_image(path, kind='PNG'):
    image=Image.new('RGB',(80,40),(93,120,47))
    exif=Image.Exif()
    exif[274]=6
    exif[315]='PRIVATE_ARTIST_CREDENTIAL'
    exif[34853]={1:'N',2:(12,34,56),3:'E',4:(65,43,21)}
    options=dict(exif=exif)
    if kind=='PNG':
        info=PngImagePlugin.PngInfo()
        info.add_text('source_path','/private/PRIVATE_SOURCE_PATH.png')
        info.add_itxt('credentials','PRIVATE_CREDENTIAL_TOKEN')
        options['pnginfo']=info
    image.save(path,format=kind,**options)
    return path.read_bytes()


@pytest.mark.parametrize('kind',('PNG','JPEG'))
def test_render_unconditionally_strips_exif_gps_and_png_metadata(tmp_path,kind):
    source=tmp_path/('private.'+kind.lower())
    original=private_image(source,kind)
    with Image.open(BytesIO(original)) as image:
        assert image.getexif()[315]=='PRIVATE_ARTIST_CREDENTIAL'
        assert image.getexif().get_ifd(34853)[1]=='N'
    png=render(original,0,'ORIGINAL')
    assert preview_dimensions(png)==(40,80)
    with Image.open(BytesIO(png)) as image:
        assert image.info=={} and not image.getexif()
    assert b'PRIVATE_' not in png and source.read_bytes()==original


@pytest.mark.parametrize('minimize',('preview_only','preview_without_metadata'))
def test_real_privacy_services_enforce_projection_metadata_and_refusal_recovery(tmp_path,minimize):
    source=tmp_path/'private.png'
    original=private_image(source)
    logs=tmp_path/'logs';logs.mkdir()
    media=Service('media','ews:privacy',time.monotonic()+60,logs,
        {'asset:1':[str(source),c.digest(original)]},minimize=minimize)
    display=None
    try:
        display=Service('display','ews:privacy',time.monotonic()+60,logs,minimize=minimize)
        response=media.rpc('render',dict(asset='asset:1',exposure=0,crop='ORIGINAL',preview='fit'))
        png=validate_transfer(response,minimize,('png','sha256','asset','session'))
        transfer=dict(png=response['png'],sha256=response['sha256'],frame_ref='ews:frame:privacy')
        if minimize=='preview_only':
            assert response['derived']==dict(width=40,height=80,exposure=0,crop='ORIGINAL',preview='fit')
            transfer['derived']=response['derived']
        else:
            assert set(response)=={'png','sha256','asset','session'}
        for secret in (str(source),'PRIVATE_',media.token,media.read_token,display.token,display.read_token):
            assert secret not in c.canonical(response).decode()
        assert preview_dimensions(png)==(40,80)
        receipt=display.rpc('put',transfer)
        assert receipt['minimize']==minimize and receipt['transfer_fields']==sorted(transfer)
        assert receipt['transfer_sha256']==c.digest(transfer)
        attacks=[]
        for field in ('source_path','exif','gps','credentials'):
            attack=deepcopy(transfer);attack[field]='forbidden';attacks.append(attack)
        attack=deepcopy(transfer)
        if minimize=='preview_only':
            attack.pop('derived')
        else:
            attack['derived']=dict(width=40,height=80,exposure=0,crop='ORIGINAL',preview='fit')
        attacks.append(attack)
        if minimize=='preview_only':
            for key,value in [('width',True),('height',79),('exposure',True),('crop','/private/source'),('preview','contain'),('credentials','forbidden')]:
                attack=deepcopy(transfer);attack['derived'][key]=value;attacks.append(attack)
        dirty=deepcopy(transfer)
        dirty.update(png=base64.b64encode(original).decode(),sha256=c.digest(original))
        attacks.append(dirty)
        for attack in attacks:
            with pytest.raises(urllib.error.HTTPError) as error:
                display.rpc('put',attack)
            assert error.value.code==403
            with request(display.url+'/frame/ews:frame:privacy',display.read_token) as frame:
                assert frame.read()==png
            assert display.rpc('put',deepcopy(transfer))==receipt
        with pytest.raises(urllib.error.HTTPError):
            media.rpc('render',dict(asset='asset:1',exposure=0,crop='ORIGINAL',preview='contain'))
        assert media.rpc('render',dict(asset='asset:1',exposure=0,crop='ORIGINAL',preview='fit'))==response
        source.rename(tmp_path/'preserved-source.png')
        with pytest.raises(urllib.error.HTTPError) as error:
            media.rpc('render',dict(asset='asset:1',exposure=0,crop='ORIGINAL',preview='fit'))
        assert json.load(error.value)==dict(error='service_io_unavailable')
        (tmp_path/'preserved-source.png').rename(source)
        assert source.read_bytes()==original
    finally:
        if display:assert display.close()['reaped']
        assert media.close()['reaped']


class PrivacyVariant(roles.ControlledProvider):
    def __init__(self,minimize,block=False):
        self.minimize,self.block=minimize,block

    def respond(self,role,context):
        value=super().respond(role,context)
        if role==roles.ROLES[2]:
            value.update(minimize=self.minimize)
            if self.block:value.update(decision='block',conflicts=['Unapproved display requested.'])
        return value


def test_compiled_privacy_policy_consumed_by_actual_session_after_refusal(tmp_path):
    source=tmp_path/'private.png'
    original=private_image(source)
    with pytest.raises(ValueError,match='privacy_refusal'):
        Workspace(tmp_path/'blocked',(source,),provider=PrivacyVariant('preview_only',block=True))
    assert not (tmp_path/'blocked'/'logs').exists()
    observations=[]
    for minimize in ('preview_only','preview_without_metadata'):
        session=Workspace(tmp_path/minimize,(source,),provider=PrivacyVariant(minimize))
        try:
            assert session.contract==roles.compile_contract([capture['output'] for capture in session.captures])
            assert session.work_results[1].consumed_fields[0].disposition=='USED'
            session.command('OPEN')
            session.command('EXPOSURE',3)
            report=session.report()
            consumption=report['privacy_consumption']
            assert consumption['minimize']==minimize and len(consumption['transfers'])==2
            for service in session.services:
                assert service.config['minimize']==session.contract['minimize']
                assert service.config['preview']==session.contract['preview']
            for i,transfer in enumerate(consumption['transfers']):
                assert transfer['minimize']==minimize and transfer['contract_sha256']==c.digest(session.contract)
                assert transfer['png_metadata']=='ABSENT_VERIFIED'
                assert transfer['media_sha256']==session.services[0].events[i]['response_sha256']
                assert transfer['display_receipt_sha256']==session.services[1].events[i]['response_sha256']
                assert set(transfer['media_fields'])=={'png','sha256','asset','session'}|({'derived'} if minimize=='preview_only' else set())
                assert set(transfer['display_fields'])=={'png','sha256','frame_ref'}|({'derived'} if minimize=='preview_only' else set())
                assert transfer['derived_fields']==(sorted(('width','height','exposure','crop','preview')) if minimize=='preview_only' else [])
            assert consumption['transfers'][0]['png_sha256']!=consumption['transfers'][1]['png_sha256']
            observations.append(consumption['transfers'])
            assert report['source_preserved'] and source.read_bytes()==original
            assert len(session.history)==2
        finally:
            assert session.close()['status']=='CLOSED_SUCCESS'
    assert [t['png_sha256'] for t in observations[0]]==[t['png_sha256'] for t in observations[1]]


@pytest.mark.parametrize('minimize',('preview_only','preview_without_metadata'))
def test_session_refuses_invalid_media_projection_before_display(tmp_path,monkeypatch,minimize):
    assets=generate(tmp_path/'sources',1)
    session=Workspace(tmp_path/'workspace',assets,provider=PrivacyVariant(minimize))
    try:
        session.command('OPEN')
        original=session.services[0].rpc
        calls=len(session.services[1].events)
        def tampered(op,args):
            response=original(op,args)
            if op=='render':
                if minimize=='preview_only':response['derived']['exposure']=19
                else:response['derived']=dict(width=1,height=1,exposure=0,crop='ORIGINAL',preview='fit')
            return response
        monkeypatch.setattr(session.services[0],'rpc',tampered)
        with pytest.raises(ValueError):
            session.command('EXPOSURE',2)
        assert len(session.services[1].events)==calls
        assert len(session.privacy_transfers)==1
        state=session.state()
        assert state['status']=='PREVIEW_UNAVAILABLE' and not state['current'] and state['allowed']==[] and state['preview'] is None
        with pytest.raises(ValueError,match='workspace_not_current'):
            session.command('NEXT')
    finally:
        session.close()


@pytest.mark.parametrize('foreign',('none','replacement','directory','dangling_symlink'))
def test_http_control_save_owner_approval_and_truthful_close(tmp_path,foreign):
    assets=generate(tmp_path/'sources',1)
    source_hashes=[c.digest(p.read_bytes()) for p in assets]
    session=Workspace(tmp_path/'workspace',assets)
    viewer=None
    try:
        session.command('OPEN')
        viewer=Viewer(session)
        for sequence,op,value in [(1,'SELECT',True),(2,'REQUEST_SAVE',None)]:
            body=dict(version=1,session=session.id,sequence=sequence,command=dict(op=op,value=value))
            with request(viewer.control_url+'/command',viewer.control_token,body) as response:
                state=json.load(response)
        pending=state['pending']
        assert state['owner_approval_available'] and pending
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.owner_url+'/approve',viewer.control_token,dict(candidate=pending))
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.owner_url+'/approve',viewer.owner_token,dict(candidate=pending),origin=viewer.control_url)
        with request(viewer.owner_url+'/approve',viewer.owner_token,dict(candidate=pending),origin=viewer.owner_url) as response:
            saved=json.load(response)['saved']
        output=session.directory/'output'/'selection.json'
        assert output.read_bytes()==c.canonical(pending['content'])+b'\n'
        assert c.digest(output.read_bytes())==saved['sha256'] and session.write_outcome=='WRITTEN_ONCE'
        assert len(session.history)==4 and all(record['packet_id'] for record in session.history)
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.owner_url+'/approve',viewer.owner_token,dict(candidate=pending))
        path=next(iter(session.owned))
        if foreign!='none':
            path.unlink()
            if foreign=='replacement':path.write_bytes(b'foreign replacement')
            elif foreign=='directory':path.mkdir()
            else:path.symlink_to(tmp_path/'missing-target')
        ref=session.preview['frame_ref']
        with request(viewer.owner_url+'/end',viewer.owner_token,{}) as response:
            cleanup=json.load(response)
        expected='CLOSED_SUCCESS' if foreign=='none' else 'CLEANUP_INCOMPLETE'
        assert cleanup['status']==expected and cleanup['reason']=='OWNER_END'
        assert cleanup['authority']=='INITIAL_RESOURCE_OWNER_CLEANUP_OBLIGATION'
        assert len(session.history)==4
        assert cleanup['foreign_preserved']==([] if foreign=='none' else [path.name])
        if foreign!='none':
            assert path.name not in cleanup['removed'] and 'NOT_REMOVED' in cleanup['retained_reason']
            assert path.is_symlink() if foreign=='dangling_symlink' else path.exists()
        if foreign=='replacement':assert path.read_bytes()==b'foreign replacement'
        with request(viewer.owner_url+'/end',viewer.owner_token,{}) as response:
            assert json.load(response)==cleanup
        with request(viewer.control_url+'/state',viewer.control_token) as response:
            state=json.load(response)
        assert state['status']==expected and state['cleanup']==cleanup
        assert not state['current'] and not state['owner_approval_available'] and not state['owner_cleanup_available']
        assert state['allowed']==[] and state['preview'] is None and state['pending'] is None
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.control_url+'/frame/'+ref,viewer.control_token)
        body=dict(version=1,session=session.id,sequence=3,command=dict(op='NEXT',value=None))
        with pytest.raises(urllib.error.HTTPError):
            request(viewer.control_url+'/command',viewer.control_token,body)
        assert all(service.process.poll() is not None for service in session.services)
        assert [c.digest(p.read_bytes()) for p in assets]==source_hashes
    finally:
        if viewer:viewer.close()
        session.close()


@pytest.mark.parametrize('stale',('expiry','idle','revoke'))
def test_http_state_currentness_without_effects_or_source_reads(tmp_path,monkeypatch,stale):
    assets=generate(tmp_path/'sources',1)
    class IdleVariant(roles.ControlledProvider):
        def respond(self,role,context):
            value=super().respond(role,context)
            if role==roles.ROLES[1] and stale=='idle':value['cleanup']='on_end_and_idle'
            return value
    session=Workspace(tmp_path/'workspace',assets,c.REQUEST_B,provider=IdleVariant())
    viewer=None
    try:
        session.command('OPEN')
        viewer=Viewer(session)
        ref=session.preview['frame_ref']
        if stale=='expiry':session.source.offset=1201
        elif stale=='idle':
            session.last_activity=time.monotonic()-301
        else:session.revoke()
        before=(session.host.revision,len(session.history),len(session.executed),session.status,session.cleanup_report,session.last_activity)
        read_bytes=Path.read_bytes
        def no_source_reads(path):
            assert path not in session.assets.values(),'state must not read sources'
            return read_bytes(path)
        with monkeypatch.context() as patch:
            patch.setattr(Path,'read_bytes',no_source_reads)
            for url,token in ((viewer.owner_url,viewer.owner_token),(viewer.control_url,viewer.control_token)):
                with request(url+'/state',token) as response:state=json.load(response)
                assert not state['current'] and state['allowed']==[] and state['preview'] is None and state['pending'] is None
                assert not state['owner_approval_available']
                assert state['status']==('CLOSED_SUCCESS' if stale=='revoke' else 'EXPIRED')
        assert before==(session.host.revision,len(session.history),len(session.executed),session.status,session.cleanup_report,session.last_activity)
        with pytest.raises(urllib.error.HTTPError):request(viewer.control_url+'/frame/'+ref,viewer.control_token)
        body=dict(version=1,session=session.id,sequence=1,command=dict(op='NEXT',value=None))
        with pytest.raises(urllib.error.HTTPError):request(viewer.control_url+'/command',viewer.control_token,body)
        assert len(session.history)==1
    finally:
        if viewer:viewer.close()
        session.close()
