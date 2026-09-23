"""Immutable local outbox and independently persisted mock receiver acknowledgements."""
import json
from pathlib import Path
from . import contracts_v01 as c


class Outbox:
    def __init__(self,directory):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.trail=[]

    def queue(self,report):
        raw=c.canonical(report);ref=c.identity('message',report);path=self.directory/(c.digest(ref.encode())+'.json')
        if path.exists(): c.require(path.read_bytes()==raw,'outbox_identity_conflict')
        else:
            with path.open('xb') as f:f.write(raw)
        self.trail.append(dict(state='QUEUED',message_id=ref,payload_sha256=c.digest(raw)))
        return dict(message_id=ref,payload_sha256=c.digest(raw))

    def read(self,ref):
        raw=(self.directory/(c.digest(ref.encode())+'.json')).read_bytes()
        c.require(c.identity('message',json.loads(raw))==ref,'outbox_immutable_binding')
        return raw

    def deliver(self,ref,receiver):
        raw=self.read(ref);expected=dict(message_id=ref,payload_sha256=c.digest(raw))
        self.trail.append(dict(state='ATTEMPTED',**expected))
        ack=receiver.receive(ref,raw)
        if ack!=expected or receiver.readback(ref)!=expected:
            self.trail.append(dict(state='UNKNOWN',**expected));raise ValueError('receiver_ack_not_verified')
        self.trail.append(dict(state='RECEIVED',**expected));return ack


class Receiver:
    def __init__(self,directory):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)

    def receive(self,ref,raw):
        c.require(c.identity('message',json.loads(raw))==ref,'receiver_message_binding')
        path=self.directory/(c.digest(ref.encode())+'.json')
        if path.exists(): c.require(path.read_bytes()==raw,'receiver_message_conflict')
        else:
            with path.open('xb') as f:f.write(raw)
        return self.readback(ref)

    def readback(self,ref):
        raw=(self.directory/(c.digest(ref.encode())+'.json')).read_bytes()
        return dict(message_id=ref,payload_sha256=c.digest(raw))
