"""Finite loopback IPC. Same-UID subprocesses are not an OS sandbox."""
import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
import urllib.request
from . import contracts_v01 as c
from .media_v01 import render, privacy_policy, preview_dimensions, validate_transfer
from .semantic_adapter_v01 import parse


def worker(config):
    minimize = privacy_policy(config['minimize'])
    token, read_token = config['token'],config['read_token']
    state = dict(sequence=0,frame=None,frame_ref=None,closed=False,frames=0,samples=0,audio_chunks=[],batch=None,used_batches=[])
    assets = config.get('assets',{})
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass

        def answer(self,code,body,kind='application/json'):
            self.send_response(code)
            self.send_header('Content-Type',kind)
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def current(self):
            c.require(not state['closed'] and time.monotonic()<config['deadline'], 'service_not_current')
            c.require(self.headers.get('Host')==f'127.0.0.1:{self.server.server_port}', 'service_host')
            origin = self.headers.get('Origin')
            c.require(origin is None or origin==f'http://127.0.0.1:{self.server.server_port}', 'service_origin')

        def do_GET(self):
            try:
                self.current()
                c.require(config['role']=='display' and self.headers.get('Authorization')=='Bearer '+read_token, 'display_only_credential')
                c.require(self.path=='/frame/'+str(state['frame_ref']) and state['frame'] is not None, 'derived_frame_only')
                state['frames'] += 1
                self.answer(200,state['frame'],'image/png')
            except ValueError as exc:
                self.answer(403,c.canonical(dict(error=str(exc))))

        def do_POST(self):
            try:
                self.current()
                c.require(self.path=='/rpc' and self.headers.get('Authorization')=='Bearer '+token, 'rpc_auth')
                length = int(self.headers.get('Content-Length','0'))
                c.require(0<length<=5_000_000,'rpc_size')
                value = parse(self.rfile.read(length))
                c.exact(value,('version','session','sequence','op','args'))
                c.require(value['version']==c.VERSION and value['session']==config['session'] and type(value['sequence']) is int
                    and value['sequence']==state['sequence']+1,'rpc_binding_sequence')
                args, op = value['args'],value['op']
                if op=='close':
                    c.exact(args,())
                    state['closed']=True
                    result=dict(closed=True,nonce=config['nonce'],frames=state['frames'],samples=state['samples'],audio_chunks=state['audio_chunks'])
                    threading.Thread(target=self.server.shutdown,daemon=True).start()
                elif config['role']=='audio' and op=='observe':
                    c.exact(args,())
                    result=dict(session=config['session'],resource=config['nonce'],available=True,samples=state['samples'],
                        mode='HEADLESS_PCM_CONSUMPTION',sample_rate=8000,channels=1,sample_width=2)
                elif config['role']=='audio' and op=='end':
                    c.exact(args,())
                    state['batch']=None
                    result=dict(ended=True)
                elif config['role']=='audio' and op=='begin':
                    c.exact(args,('batch_ref','sample_offset','deadline'))
                    c.require(type(args['batch_ref']) is str and args['batch_ref'].startswith('ews:media_batch:') and
                        args['batch_ref'] not in state['used_batches'],'pcm_fresh_batch')
                    c.require(type(args['sample_offset']) is int and args['sample_offset'] in range(0,64000,4000),'pcm_position')
                    c.require(type(args['deadline']) in (int,float) and time.monotonic()<args['deadline']<=min(config['deadline'],time.monotonic()+10),
                        'pcm_finite_deadline')
                    c.require(len(config['pcm_chunks'])==16,'pcm_inventory')
                    state['batch']=dict(args)
                    state['used_batches'].append(args['batch_ref'])
                    result=dict(started=True,batch_ref=args['batch_ref'],sample_offset=args['sample_offset'])
                elif config['role']=='audio' and op=='consume':
                    c.exact(args,('pcm','sha256','sample_offset','frame_ref','batch_ref'))
                    c.require(type(args['pcm']) is str and type(args['sample_offset']) is int and 0<=args['sample_offset']<64000,
                        'pcm_position')
                    pcm=base64.b64decode(args['pcm'],validate=True)
                    c.require(len(pcm)==8000 and c.digest(pcm)==args['sha256'],'pcm_chunk_binding')
                    batch=state['batch']
                    c.require(batch is not None and time.monotonic()<batch['deadline'] and args['batch_ref']==batch['batch_ref'] and
                        args['sample_offset']==batch['sample_offset'],'pcm_current_batch_position')
                    c.require(args['sha256']==config['pcm_chunks'][args['sample_offset']//4000],'pcm_admitted_content')
                    c.require(type(args['frame_ref']) is str and args['frame_ref'].startswith('ews:media_frame:') and
                        type(args['batch_ref']) is str and args['batch_ref'].startswith('ews:media_batch:'),'pcm_work_binding')
                    import struct
                    peak=max(abs(v[0]) for v in struct.iter_unpack('<h',pcm))
                    state['samples']+=len(pcm)//2
                    result=dict(session=config['session'],resource=config['nonce'],samples=len(pcm)//2,
                        sample_offset=args['sample_offset'],sha256=c.digest(pcm),peak=peak,frame_ref=args['frame_ref'],batch_ref=args['batch_ref'])
                    state['audio_chunks'].append(result)
                    batch['sample_offset']+=4000
                    if batch['sample_offset']==64000:state['batch']=None
                elif config['role']=='media' and op=='render':
                    c.exact(args,('asset','exposure','crop','preview'))
                    c.require(args['asset'] in assets,'asset_scope')
                    c.require(args['preview']==config['preview'],'configured_preview')
                    c.command(dict(op='EXPOSURE',value=args['exposure']),('EXPOSURE',))
                    c.command(dict(op='CROP',value=args['crop']),('CROP',))
                    path,sha = assets[args['asset']]
                    data = Path(path).read_bytes()
                    c.require(c.digest(data)==sha,'source_changed')
                    png = render(data,args['exposure'],args['crop'],args['preview'])
                    result=dict(png=base64.b64encode(png).decode(),sha256=c.digest(png),asset=args['asset'],session=config['session'])
                    if minimize=='preview_only':
                        width,height=preview_dimensions(png)
                        result['derived']=dict(width=width,height=height,exposure=args['exposure'],crop=args['crop'],preview=args['preview'])
                    validate_transfer(result,minimize,('png','sha256','asset','session'))
                elif config['role']=='display' and op=='put':
                    png = validate_transfer(args,minimize,('png','sha256','frame_ref'))
                    c.require(type(args['frame_ref']) is str and args['frame_ref'].startswith('ews:frame:')
                        and len(args['frame_ref'])<=100,'frame_reference')
                    if minimize=='preview_only':
                        c.require(args['derived']['preview']==config['preview'],'configured_preview')
                    state['frame'],state['frame_ref']=png,args['frame_ref']
                    result=dict(frame_ref=state['frame_ref'],sha256=c.digest(png),session=config['session'],
                        minimize=minimize,transfer_fields=sorted(args),transfer_sha256=c.digest(args))
                else:
                    raise ValueError('service_operation_not_allowed')
                state['sequence']=value['sequence']
                self.answer(200,c.canonical(result))
            except OSError:
                self.answer(403,c.canonical(dict(error='service_io_unavailable')))
            except (ValueError,KeyError,TypeError) as exc:
                self.answer(403,c.canonical(dict(error=str(exc))))
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    def lifetime():
        while not state['closed']:
            if time.monotonic()>=config['deadline'] or os.getppid()!=config['parent_pid']:
                state['closed']=True
                server.shutdown()
                return
            time.sleep(0.25)
    threading.Thread(target=lifetime,daemon=True).start()
    print(json.dumps(dict(port=server.server_port,pid=os.getpid(),nonce=config['nonce'],role=config['role'])),flush=True)
    server.serve_forever(poll_interval=0.05)
    server.server_close()


class Service:
    def __init__(self,role,session,deadline,logdir,assets=None,nonce=None,
                 minimize='preview_without_metadata',preview='fit',pcm_chunks=()):
        privacy_policy(minimize)
        c.require(preview in ('fit','contain'),'configured_preview')
        self.role,self.session,self.sequence=role,session,0
        self.token,self.read_token,self.nonce=(secrets.token_urlsafe(32) for _ in range(3))
        if nonce is not None:
            self.nonce=nonce
        self.config=dict(role=role,session=session,deadline=deadline,token=self.token,read_token=self.read_token,nonce=self.nonce,
            parent_pid=os.getpid(),assets=assets or {},minimize=minimize,preview=preview,pcm_chunks=list(pcm_chunks))
        self.log=Path(logdir)/(role+'.stderr')
        self.stream=self.log.open('xb')
        self.process=subprocess.Popen([sys.executable,'-B','-m',__name__],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stream)
        self.process.stdin.write(c.canonical(self.config)+b'\n')
        self.process.stdin.close()
        line=self.process.stdout.readline()
        if not line:
            self.process.wait()
            self.stream.close()
            raise ValueError('service_start_failed:'+role)
        self.birth=json.loads(line)
        c.require(self.birth['pid']==self.process.pid and self.birth['nonce']==self.nonce,'service_birth_binding')
        self.url='http://127.0.0.1:'+str(self.birth['port'])
        self.events=[]
        self.rpc_lock=threading.RLock()
        self.close_reply=None

    def rpc(self,op,args):
        with self.rpc_lock:
            return self._rpc(op,args)

    def _rpc(self,op,args):
        started=time.monotonic()
        payload=dict(version=c.VERSION,session=self.session,sequence=self.sequence+1,op=op,args=args)
        request=urllib.request.Request(self.url+'/rpc',data=c.canonical(payload),headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json'},method='POST')
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request,timeout=10) as response:
            value=json.load(response)
        self.sequence=payload['sequence']
        self.events.append(dict(sequence=self.sequence,op=op,request_sha256=c.digest(payload),response_sha256=c.digest(value),seconds=time.monotonic()-started))
        return value

    def close(self):
        observed=self.process.poll()
        outcome='ALREADY_EXITED' if observed is not None else 'OWNER_CLOSE_REQUESTED'
        error=None
        if self.process.poll() is None:
            try:
                reply=self.rpc('close',{})
                c.require(reply['nonce']==self.nonce,'cleanup_service_identity')
                self.close_reply=reply
                outcome='GRACEFUL_CLOSE_ACKNOWLEDGED'
            except Exception as exc:
                error=type(exc).__name__
                outcome='CLOSE_FAILED_OWNED_TERMINATION'
                # This Popen is our unreaped child, never a recycled external PID.
                self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                outcome='CLOSE_DEADLINE_OWNED_KILL'
                self.process.kill()
                self.process.wait()
        self.process.wait()
        self.stream.close()
        self.process.stdout.close()
        return dict(role=self.role,pid=self.process.pid,nonce=self.nonce,returncode=self.process.returncode,reaped=True,
            receipt=self.close_reply,close_outcome=outcome,close_error=error)


if __name__=='__main__':
    worker(json.loads(sys.stdin.readline()))
