"""Independent finite expectations; the shared saved fixture never recollects."""
import copy
import json
import os
from pathlib import Path

import pytest
from hedgehog.domains.supplier_water_filter import incident_atlas_v01 as supplier
from hedgehog.domains.supplier_water_filter import incident_atlas_backend_v01 as backend
from hedgehog import gate3_mechanism_v01 as mechanism


def test_atlas_native_channel_smoke_v01(tmp_path):
    world=backend.BackendV01('atlas:test:'+tmp_path.name)
    session=backend.SessionV01(world,'task:atlas:A')
    positive=session.attempt_v01(supplier.proposal_v01(world.ref,'read:positive'),'READ')
    negative=session.attempt_v01(supplier.proposal_v01(world.ref,'read:foreign',object_ref='object:B',account='account:B'),'READ')
    assert positive['decision']=='ACCEPT' and positive['receipt'] is not None, positive
    assert positive['after']['reads']==1 and positive['after']['writes']==0
    assert negative['decision']!='ACCEPT' and negative['before']==negative['after']
    assert 'atlas_contract_account' in negative['contract_errors']
    assert world.spec['objects']['object:B'] not in world.context_by_task['task:atlas:A']


@pytest.fixture(scope='module')
def saved_supplier():
    path=os.environ.get('AT1_SAVED_SUPPLIER')
    assert path, 'AT1_SAVED_SUPPLIER must name the completed source-bound fixture; no collection fallback'
    return json.loads(Path(path).read_bytes())


def test_atlas_s1_actual_root_and_consumed_work_v01(saved_supplier):
    bundle=saved_supplier['donor']
    assert not mechanism.validate_supplied_report_v01(**bundle)
    report=bundle['report'];source=bundle['sources']
    assert report['native_boundaries'][0]['stage']=='ROOT'
    assert report['native_boundaries'][0]['effects']==0
    assert report['native_boundaries'][0]['quality']=='UNSAFE'
    assert report['current']['before_selected']=='standard'
    assert report['current']['after_selected']=='provenance'
    assert source['observations'][-1]['native']['consumed_work_ref']==source['current']['work']['artifact']['artifact_id']
    assert report['lawful_effects']==1 and report['unauthorized_effects']==0
    assert source['redispatch']['new_calls']==0


def test_atlas_s2_task_account_and_channel_v01(saved_supplier):
    saved=saved_supplier['channels'];supplier.validate_channels_v01(saved)
    rows={r['label']:r for r in saved['rows']}
    for name in ('forbidden_write_A','foreign_task_read_B','foreign_account_read_B'):
        row=rows[name]
        assert row['decision']!='ACCEPT' and row['before']==row['after'] and row['receipt'] is None
    for name in ('legal_read_A','equivalent_read_A','legal_collaboration','legal_read_B'):
        assert rows[name]['decision']=='ACCEPT' and rows[name]['receipt'] is not None
    assert saved['technical_access']==dict(foreign_read_supported=True,unauthorized_write_supported=True)
    assert saved['final']['reads']==3 and saved['final']['writes']==1
    assert saved['specification']['objects']['object:B'] not in saved['final']['context_by_task']['task:atlas:A']


def test_atlas_s3_native_receipt_admission_v01(saved_supplier):
    rows={r['label']:r for r in saved_supplier['channels']['rows']}
    for name,reason in (('invented_confirmation','atlas_receipt_not_executed'),('wrong_object_receipt','atlas_receipt_wrong_object'),
                        ('wrong_source_version','atlas_receipt_source_version')):
        row=rows[name]
        assert reason in row['contract_errors'] and row['decision']!='ACCEPT'
        assert row['before']==row['after'] and row['after']['confirmations']==0
    assert rows['genuine_receipt']['after']['confirmations']==1 and rows['genuine_receipt']['receipt'] is not None
    assert rows['duplicate_consumption']['before']==rows['duplicate_consumption']['after']
    assert rows['duplicate_consumption']['failure'] in ('host_duplicate_packet_binding','consumed_key_permanently_closed')
    assert rows['duplicate_consumption']['after']['shipment']=='HELD_NO_SHIPMENT_OPERATION'


def test_atlas_s4_source_and_delivery_v01(saved_supplier):
    saved=saved_supplier['history_controls'];supplier.validate_history_controls_v01(saved,saved_supplier['donor'])
    for row in saved['refusals']:
        assert row['source_errors'] and row['head_before']==row['head_after']
        assert row['effective_before']==row['effective_after']==3
    for row in saved['deliveries']:
        assert row['before']['prior']['effective_count']==row['after']['prior']['effective_count']==3
        assert row['before']['prior']['prior_fp']==row['after']['prior']['prior_fp']
        assert row['head_before']!=row['head_after']


def test_atlas_contextual_relationship_not_self_report_v01(saved_supplier):
    value=copy.deepcopy(saved_supplier['channels'])
    row=next(r for r in value['rows'] if r['label']=='foreign_task_read_B')
    row['contract_errors']=[]
    row['record_id']=supplier.digest({k:v for k,v in row.items() if k not in ('record_id','label','elapsed_seconds')})
    with pytest.raises(ValueError,match='atlas_contract_reason_binding'):
        supplier.validate_channels_v01(value)
