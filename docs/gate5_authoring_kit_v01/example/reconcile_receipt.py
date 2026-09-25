"""Saved MOCK receipt/readback reconciliation. Never dispatch a consumed packet."""
import json
from pathlib import Path

def reconcile(folder,logical_key,payload_sha256):
    folder=Path(folder)
    if not (folder/'result.json').exists():return dict(status='UNKNOWN_REQUIRES_READBACK',dispatch=False)
    saved=json.loads((folder/'result.json').read_text());state=json.loads((folder/'disposable_batch.json').read_text())
    record=state['idempotency'].get(logical_key)
    if record is None:return dict(status='UNKNOWN_REQUIRES_READBACK',dispatch=False)
    if record['payload_sha256']!=payload_sha256:raise ValueError('same_key_changed_payload')
    attempts=[x for x in saved['executions'] if x['key']==logical_key and x['payload_sha256']==payload_sha256]
    if len(attempts)!=1 or state!=saved['readback']:return dict(status='UNKNOWN_REQUIRES_READBACK',dispatch=False)
    return dict(status='SAVED_MOCK_RECEIPT_NOT_CURRENT_PERMISSION',receipt=saved['receipt'],readback=state,dispatch=False)

def verify_example(folder):
    saved=json.loads((Path(folder)/'result.json').read_text());attempt=saved['executions'][0]
    before=(Path(folder)/'disposable_batch.json').read_bytes()
    value=reconcile(folder,attempt['key'],attempt['payload_sha256'])
    assert value['receipt']==saved['receipt'] and value['dispatch'] is False
    try:reconcile(folder,attempt['key'],'0'*64)
    except ValueError as exc:assert str(exc)=='same_key_changed_payload'
    else:raise AssertionError('changed_payload_accepted')
    assert reconcile(folder,'unknown','0'*64)['status']=='UNKNOWN_REQUIRES_READBACK'
    assert before==(Path(folder)/'disposable_batch.json').read_bytes()
    return dict(status='PASS_SAVED_MOCK_RECONCILIATION',new_dispatch=0,receipt_id=value['receipt']['artifact_id'],
        limitation='Saved exact local mock state and receipt only; not adversarial storage authentication or power-loss recovery')
if __name__=='__main__':
    import sys
    print(json.dumps(verify_example(sys.argv[1]),sort_keys=True))
