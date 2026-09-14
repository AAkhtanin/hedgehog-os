"""Two loopback origins: untrusted controls cannot confirm a save."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
import threading
import urllib.request
from . import contracts_v01 as c
from .semantic_adapter_v01 import parse

STYLE = '''
:root{font-family:system-ui,-apple-system,sans-serif;color:#20252a;background:#f4f6f7;color-scheme:light;letter-spacing:0}
*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0}header{min-height:58px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:9px 24px;border-bottom:1px solid #d9dfe3;background:white}header h1{min-width:0;overflow-wrap:anywhere}header .row{flex-wrap:wrap}button{max-width:100%;white-space:normal;overflow-wrap:anywhere}.status{overflow-wrap:anywhere}.approval>div{min-width:0;max-width:100%}
h1{font-size:20px;font-weight:650;margin:0}h2{font-size:16px;margin:0 0 16px}button,input,select{font:inherit}button{border:1px solid #cbd2d8;border-radius:5px;background:white;padding:9px 13px;color:#222;cursor:pointer;min-height:40px}button:hover{background:#e8edef}button:disabled{opacity:.5;cursor:wait}.primary{background:#236b59;color:white;border-color:#236b59}.primary:hover{background:#185846}.danger{color:#a23636}small,.muted{color:#5b6871;font-size:12px}.workspace{display:grid;grid-template-columns:minmax(0,1fr) 260px;min-height:690px}.stage{padding:24px;min-width:0}.image{height:530px;display:flex;align-items:center;justify-content:center;background:#e8edef}.image img{max-width:100%;max-height:100%;object-fit:contain}.toolbar{display:flex;gap:10px;align-items:center;justify-content:space-between;margin-top:15px}.settings{padding:24px;background:#fff;border-left:1px solid #d9dfe3}.field{display:block;margin-bottom:24px;font-size:13px}.field input[type=range]{width:100%;accent-color:#236b59;margin-top:12px}.field select{width:100%;margin-top:10px;padding:8px}.rating{display:flex;gap:4px;margin-top:10px}.rating button{min-width:32px;padding:7px}.rating button.on{background:#f2cf78;border-color:#ddac43}.row{display:flex;gap:8px;align-items:center}.selected{accent-color:#236b59;width:18px;height:18px}.status{font-size:13px;margin:16px 0;min-height:22px}.error{color:#a23636}details{font-size:12px;margin-top:24px;border-top:1px solid #ddd;padding-top:14px}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:220px;overflow:auto;font-size:11px}iframe{width:100%;border:0;height:770px;display:block}.approval{padding:20px 24px;background:white;border-top:1px solid #d9dfe3;display:flex;gap:24px;align-items:flex-start}.approval section{flex:1;min-width:0}.approval pre{max-height:120px}.saved{color:#236b59}.tag{font-size:11px;padding:4px 8px;background:#e5edeb;color:#275e50;border-radius:3px}
@media(max-width:720px){header{padding:12px 14px}header h1{width:100%;font-size:17px}header .row{width:100%;justify-content:space-between}.workspace{grid-template-columns:1fr;min-height:0}.stage{padding:12px}.image{height:340px}.settings{border-left:0;border-top:1px solid #ddd;padding:18px}.field{margin-bottom:18px}.approval{padding:16px;flex-direction:column}iframe{height:1020px}.settings h2{font-size:15px}}
'''

CONTROL_HTML = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Photo Workspace</title><style>STYLE</style><body>
<main class="workspace"><section class="stage"><div class="image"><img id="preview" alt="Current derived photograph"></div>
<div class="toolbar"><button id="previous" title="Previous photograph" aria-label="Previous photograph">&#8592;</button><span id="position" class="muted"></span><button id="next" title="Next photograph" aria-label="Next photograph">&#8594;</button></div>
<div id="status" class="status" role="status"></div>
<section id="media-section" hidden><h2>Local frame sequence</h2><div class="image" style="height:270px"><img id="media-preview" alt="Current bounded media frame"></div>
<div class="toolbar"><button id="play" title="Play finite media" aria-label="Play finite media">&#9654;</button><button id="pause" title="Pause media" aria-label="Pause media">&#9208;</button><output id="media-position">0 / 8 s</output></div>
<label class="field">Position<input id="seek" type="range" min="0" max="7" step="1" value="0"></label><p id="audio-state" role="status"></p>
<button id="review-media">Review presented media</button></section>
</section><aside class="settings"><h2>Photo selection</h2><p><span class="tag">MODE</span></p>
<label class="field row"><input id="selected" class="selected" type="checkbox"> Selected</label>
<div class="field">Rating<div id="rating" class="rating"></div></div>
<label class="field" id="exposure-field">Exposure <output id="exposure-value">0.0</output><input id="exposure" type="range" min="-20" max="20" step="1" value="0"></label>
<label class="field" id="crop-field">Crop<select id="crop"><option value="ORIGINAL">Original</option><option value="SQUARE">Square</option><option value="WIDE">16:9</option></select></label>
<button class="primary" id="request-save">Request save</button><details><summary>Execution details</summary><pre id="diagnostics"></pre></details>
</aside></main><script>
const token=location.hash.slice(1);history.replaceState(null,'',location.pathname);
let seq=0,state=null,busy=false,blob=null,mediaBlob=null,generation=0,refreshing=false,stopped=false,poll=null;
const $=id=>document.getElementById(id);
const current=()=>!!state&&state.current===true&&state.status==='ACTIVE';
const permitted=op=>current()&&state.allowed.includes(op);
function syncControls(){document.querySelectorAll('button,input,select').forEach(e=>e.disabled=busy||refreshing||!permitted(e.dataset.op));}
function clearPreview(){if(blob)URL.revokeObjectURL(blob);blob=null;$('preview').removeAttribute('src');$('preview').hidden=true;}
function clearMedia(){if(mediaBlob)URL.revokeObjectURL(mediaBlob);mediaBlob=null;$('media-preview').removeAttribute('src');$('media-preview').hidden=true;}
function stateText(){return state.status+(state.current_reason?': '+state.current_reason:'');}
function failClosed(e){state=null;clearPreview();clearMedia();syncControls();$('status').textContent=e.message;$('status').className='status error';}
function stop(){stopped=true;generation++;clearInterval(poll);clearPreview();clearMedia();state=null;syncControls();}
async function api(path,data){const res=await fetch(path,{method:data?'POST':'GET',headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:data?JSON.stringify(data):undefined,cache:'no-store'});if(!res.ok){let e=await res.json();throw Error(e.error)}return res.json()}
async function refresh(){
    if(stopped)return;const ticket=++generation;refreshing=true;syncControls();
    try{
        const next=await api('/state');if(ticket!==generation||stopped)return;
        state=next;seq=state.control_sequence;
        $('position').textContent=(state.index+1)+' / '+state.assets.length;const asset=state.assets[state.index];
        $('selected').checked=asset.selected;$('exposure').value=asset.exposure;$('exposure-value').textContent=(asset.exposure/10).toFixed(1);$('crop').value=asset.crop;
        $('exposure-field').hidden=!state.allowed.includes('EXPOSURE');$('crop-field').hidden=!state.allowed.includes('CROP');
        for(const b of $('rating').children)b.classList.toggle('on',Number(b.dataset.value)<=asset.rating);
        $('diagnostics').textContent=JSON.stringify({session:state.session,root:state.root,version:state.version,status:state.status,current:state.current,mode:state.mode,preview:state.preview},null,2);
        if(current()&&state.preview){
            const r=await fetch('/frame/'+encodeURIComponent(state.preview.frame_ref),{headers:{'Authorization':'Bearer '+token},cache:'no-store'});
            if(!r.ok)throw Error((await r.json()).error||'Preview unavailable');const pixels=await r.blob();
            if(ticket!==generation||stopped)return;
            clearPreview();blob=URL.createObjectURL(pixels);$('preview').src=blob;$('preview').hidden=false;
        }else{clearPreview();$('status').textContent=stateText();}
        $('media-section').hidden=!state.media;
        if(state.media){
            $('media-position').textContent=state.media.position+' / 8 s';$('seek').value=Math.min(7,Math.floor(state.media.position));
            $('audio-state').textContent='Audio: '+state.media.audio+' | '+state.media.status+(state.media.review?' | '+state.media.review:'');
            if(current()&&state.media.frame_ref){
                const r=await fetch('/media-frame/'+encodeURIComponent(state.media.frame_ref),{headers:{'Authorization':'Bearer '+token},cache:'no-store'});
                if(r.ok){const pixels=await r.blob();if(ticket!==generation||stopped)return;clearMedia();mediaBlob=URL.createObjectURL(pixels);$('media-preview').src=mediaBlob;$('media-preview').hidden=false;}
                else{if(ticket!==generation||stopped)return;clearMedia();$('audio-state').textContent='Current media frame unavailable; awaiting refreshed reference.';}
            }else clearMedia();
        }
        parent.postMessage({type:'ews-state-changed'},'*');
        if(!state.current){clearInterval(poll);poll=null;}
    }catch(e){if(ticket===generation&&!stopped){failClosed(e);throw e;}}
    finally{if(ticket===generation){refreshing=false;syncControls();}}
}
async function command(op,value=null){
    if(stopped||busy||refreshing||!permitted(op))return;
    busy=true;generation++;syncControls();$('status').className='status';$('status').textContent='Awaiting current Root validation...';
    try{
        await api('/command',{version:1,session:state.session,sequence:++seq,command:{op,value}});await refresh();
        if(current())$('status').textContent='Applied at workspace version '+state.version;
    }catch(e){
        state=null;clearPreview();syncControls();await refresh().catch(()=>{});
        if(current()||!state){$('status').textContent=e.message;$('status').className='status error';}
    }finally{busy=false;syncControls();}
}
for(const [id,op] of Object.entries({next:'NEXT',previous:'PREVIOUS',selected:'SELECT',exposure:'EXPOSURE',crop:'CROP','request-save':'REQUEST_SAVE',play:'PLAY',pause:'PAUSE',seek:'SEEK','review-media':'REVIEW_MEDIA'}))$(id).dataset.op=op;
$('play').onclick=()=>command('PLAY');$('pause').onclick=()=>command('PAUSE');$('seek').onchange=e=>command('SEEK',Number(e.target.value));$('review-media').onclick=()=>command('REVIEW_MEDIA');
$('next').onclick=()=>command('NEXT');$('previous').onclick=()=>command('PREVIOUS');$('selected').onchange=e=>command('SELECT',e.target.checked);$('exposure').onchange=e=>command('EXPOSURE',Number(e.target.value));$('crop').onchange=e=>command('CROP',e.target.value);$('request-save').onclick=()=>command('REQUEST_SAVE');
for(let i=1;i<=5;i++){const b=document.createElement('button');b.textContent=String(i);b.title='Rate '+i;b.dataset.value=i;b.dataset.op='RATE';b.onclick=()=>command('RATE',i);$('rating').appendChild(b)}
syncControls();poll=setInterval(()=>{if(!busy&&!refreshing&&!stopped)refresh().catch(()=>{});},1000);
addEventListener('pagehide',stop);refresh().catch(()=>{});
</script></body></html>'''

OWNER_HTML = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Radiolaria | Temporary Photo Workspace</title><style>STYLE</style><body>
<header><h1>Radiolaria <span class="muted">/ Temporary workspace</span></h1><div class="row"><span class="tag">MODE</span><button id="audio-loss" hidden>Disconnect owned audio sink</button><button id="end" class="danger">Close workspace</button></div></header>
<iframe id="controls" title="Bounded photo controls" sandbox="allow-scripts allow-same-origin"></iframe>
<div class="approval"><section><h2>Owner confirmation</h2><div id="summary" class="muted">No save requested.</div><pre id="pending"></pre></section><div><button id="confirm" class="primary" disabled>Approve this sidecar</button><p id="result" class="status" role="status"></p></div></div>
<script>const token=location.hash.slice(1);history.replaceState(null,'',location.pathname);
let pending=null,state=null,busy=false,audioBusy=false,refreshing=false,generation=0,stopped=false,poll=null,controlOrigin=null;
const $=id=>document.getElementById(id);
const active=()=>!!state&&state.current===true&&state.status==='ACTIVE';
function syncControls(){
    $('confirm').disabled=busy||refreshing||!active()||state.owner_approval_available!==true||!pending||!!state.saved;
    $('end').disabled=busy||refreshing||!state||state.owner_cleanup_available!==true;
    $('audio-loss').hidden=!state||!state.media;
    const action=state&&state.owner_audio_action;
    $('audio-loss').disabled=busy||refreshing||!active()||!state.media||!['DISCONNECT','CONTINUE_AFTER_LOSS'].includes(action);
    $('audio-loss').textContent=audioBusy?'Validating audio continuation...':action==='CONTINUE_AFTER_LOSS'?
        'Continue after audio loss':action==='DISCONNECT'?'Disconnect owned audio sink':'Audio continuation unavailable';
}
function hideControls(remove=false){const frame=$('controls');if(!frame)return;frame.hidden=true;if(remove)frame.remove();}
function disposition(status,cleanup){
    if(status==='CLOSED_SUCCESS')return 'Workspace closed.';
    if(status==='CLEANUP_INCOMPLETE')return 'CLEANUP_INCOMPLETE. Foreign resources preserved: '+JSON.stringify(cleanup.foreign_preserved||[])+'; reason: '+(cleanup.retained_reason||cleanup.reason||'Cleanup not complete')+'.';
    return status+(state&&state.current_reason?': '+state.current_reason:'');
}
function render(){
    pending=active()?state.pending:null;
    $('summary').textContent=state.saved?'Saved once: '+state.saved.slot:pending?'Review the selected ratings and preview parameters.':'No save requested.';
    $('pending').textContent=pending?JSON.stringify(pending.content,null,2):'';
    if(!active()){
        const terminal=['CLOSED_SUCCESS','CLEANUP_INCOMPLETE'].includes(state.status);
        hideControls(terminal);$('result').textContent=disposition(state.status,state.cleanup||{});
        if(terminal){clearInterval(poll);poll=null;}
    }else{const frame=$('controls');if(frame)frame.hidden=false;}
    syncControls();
}
function failClosed(e){state=null;pending=null;hideControls();syncControls();$('result').textContent=e.message;}
async function api(path,data){let r=await fetch(path,{method:data?'POST':'GET',headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:data?JSON.stringify(data):undefined,cache:'no-store'});let v=await r.json();if(!r.ok)throw Error(v.error);return v}
async function refresh(){
    if(stopped)return;const ticket=++generation;refreshing=true;syncControls();
    try{
        const next=await api('/state');if(ticket!==generation||stopped)return;state=next;render();
        const frame=$('controls');
        if(active()&&frame&&!frame.getAttribute('src')){
            const link=await api('/control-link');if(ticket!==generation||stopped||!$('controls'))return;
            controlOrigin=new URL(link.url).origin;frame.src=link.url;
        }
    }catch(e){if(ticket===generation&&!stopped){failClosed(e);throw e;}}
    finally{if(ticket===generation){refreshing=false;syncControls();}}
}
addEventListener('message',e=>{const frame=$('controls');if(!stopped&&!busy&&!refreshing&&frame&&e.source===frame.contentWindow&&e.origin===controlOrigin&&e.data&&e.data.type==='ews-state-changed')refresh().catch(()=>{});});
$('confirm').onclick=async()=>{
    if($('confirm').disabled)return;busy=true;generation++;syncControls();$('result').textContent='Awaiting current save authorization...';
    try{await api('/approve',{candidate:pending});await refresh();if(active()&&state.saved)$('result').textContent='Sidecar saved.';}
    catch(e){failClosed(e);await refresh().catch(()=>{});if(active()||!state)$('result').textContent=e.message;}
    finally{busy=false;syncControls();}
};
$('end').onclick=async()=>{
    if($('end').disabled)return;busy=true;generation++;syncControls();
    try{
        const cleanup=await api('/end',{});
        state={...state,status:cleanup.status,current:false,current_reason:null,pending:null,owner_approval_available:false,owner_cleanup_available:false,cleanup};render();
    }catch(e){failClosed(e);await refresh().catch(()=>{});if(active()||!state)$('result').textContent=e.message;}
    finally{busy=false;syncControls();}
};
$('audio-loss').onclick=async()=>{
    if($('audio-loss').disabled)return;busy=true;audioBusy=true;generation++;syncControls();$('result').textContent='Awaiting current continuation validation...';
    try{await api('/audio-loss',{});await refresh();$('result').textContent='Audio continuation completed. '+state.media.status;}
    catch(e){failClosed(e);await refresh().catch(()=>{});$('result').textContent=e.message;}
    finally{busy=false;audioBusy=false;syncControls();}
};
syncControls();hideControls();poll=setInterval(()=>{if(!busy&&!refreshing&&!stopped)refresh().catch(()=>{});},1000);
addEventListener('pagehide',()=>{stopped=true;generation++;clearInterval(poll);});refresh().catch(()=>{});
</script></body></html>'''


class Viewer:
    def __init__(self,workspace):
        self.workspace=workspace
        self.owner_token,self.control_token=(secrets.token_urlsafe(32) for _ in range(2))
        self.sequence=0
        self.servers=[]
        self.threads=[]
        for role in ('control','owner'):
            server=ThreadingHTTPServer(('127.0.0.1',0),self.handler(role))
            self.servers.append(server)
        self.control_url='http://127.0.0.1:'+str(self.servers[0].server_port)
        self.owner_url='http://127.0.0.1:'+str(self.servers[1].server_port)
        for server in self.servers:
            thread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':0.1},daemon=True)
            thread.start()
            self.threads.append(thread)

    def handler(self,role):
        viewer=self
        token=self.owner_token if role=='owner' else self.control_token
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):
                pass

            def answer(self,code,value,kind='application/json'):
                body=value if type(value) is bytes else c.canonical(value)
                self.send_response(code)
                self.send_header('Content-Type',kind)
                self.send_header('Cache-Control','no-store')
                self.send_header('X-Content-Type-Options','nosniff')
                self.send_header('Referrer-Policy','no-referrer')
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' blob:; frame-src http://127.0.0.1:*; connect-src 'self'; base-uri 'none'; form-action 'none'")
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def check(self,auth=True):
                origin=f'http://127.0.0.1:{self.server.server_port}'
                c.require(self.headers.get('Host')==origin[7:],'http_host')
                c.require(self.headers.get('Origin') in (None,origin),'http_origin')
                if auth:
                    c.require(self.headers.get('Authorization')=='Bearer '+token,'http_role_credential')

            def do_GET(self):
                try:
                    self.check(self.path!='/')
                    if self.path=='/':
                        label={'CONTROLLED_DETERMINISTIC':'Controlled','LIVE':'Live','CAPTURED_REEXECUTION':'Captured',
                            'DRS_REUSE_CANDIDATE':'DRS reuse candidate'}[viewer.workspace.mode]
                        html=(OWNER_HTML if role=='owner' else CONTROL_HTML).replace('STYLE',STYLE).replace('MODE',label)
                        return self.answer(200,html.encode(),'text/html; charset=utf-8')
                    if self.path=='/state':
                        with viewer.workspace.lock:
                            return self.answer(200,dict(viewer.workspace.state(),control_sequence=viewer.sequence))
                    if role=='owner' and self.path=='/control-link':
                        return self.answer(200,dict(url=viewer.control_url+'/#'+viewer.control_token))
                    if role=='control' and self.path.startswith('/frame/'):
                        from urllib.parse import unquote
                        with viewer.workspace.lock:
                            ref=unquote(self.path[len('/frame/'):])
                            viewer.workspace.validate_frame(ref)
                            return self.answer(200,viewer.workspace.photo_frame(ref),'image/png')
                    if role=='control' and self.path.startswith('/media-frame/'):
                        from urllib.parse import unquote
                        with viewer.workspace.lock:
                            return self.answer(200,viewer.workspace.media_frame(unquote(self.path[len('/media-frame/'):])),'image/png')
                    raise ValueError('endpoint_not_allowed')
                except (ValueError,KeyError) as exc:
                    self.answer(403,dict(error=str(exc)))
                except OSError:
                    self.answer(403,dict(error='preview_unavailable'))

            def do_POST(self):
                try:
                    self.check()
                    length=int(self.headers.get('Content-Length','0'))
                    c.require(0<length<=16384,'http_payload_size')
                    value=parse(self.rfile.read(length))
                    with viewer.workspace.lock:
                        if role=='control' and self.path=='/command':
                            c.exact(value,('version','session','sequence','command'))
                            c.require(type(value['version']) is int and value['version']==1 and type(value['sequence']) is int and value['sequence']==viewer.sequence+1
                                and value['session']==viewer.workspace.id,'control_sequence_session')
                            c.require(value['command']['op'] not in ('OPEN','SAVE','END'),'control_cannot_approve')
                            c.command(value['command'],viewer.workspace.allowed)
                            viewer.sequence+=1
                            result=viewer.workspace.command(value['command']['op'],value['command']['value'])
                        elif role=='owner' and self.path=='/approve':
                            c.exact(value,('candidate',))
                            approval=viewer.workspace.approve(value['candidate'],actor='MANUAL_OWNER_CONFIRMATION')
                            result=viewer.workspace.command('SAVE',approval)
                        elif role=='owner' and self.path=='/end':
                            c.exact(value,())
                            result=viewer.workspace.close('OWNER_END')
                        elif role=='owner' and self.path=='/audio-loss':
                            c.exact(value,())
                            result=viewer.workspace.withdraw_audio()
                        else:
                            raise ValueError('endpoint_not_allowed')
                    self.answer(200,result)
                except (ValueError,KeyError,TypeError) as exc:
                    self.answer(403,dict(error=str(exc)))
                except OSError:
                    self.answer(403,dict(error='workspace_io_unavailable'))
        return Handler

    def close(self):
        for server in self.servers:
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join()
