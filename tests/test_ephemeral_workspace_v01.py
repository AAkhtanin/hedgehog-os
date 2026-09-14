"""Focused EWS-1 contracts and actual common Root/Host consumption."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from demo.ephemeral_workspace_fixtures_v01 import generate
from hedgehog.domains.ephemeral_workspace import contracts_v01 as c
from hedgehog.domains.ephemeral_workspace import semantic_roles_v01 as roles, semantic_adapter_v01 as semantics
from hedgehog.domains.ephemeral_workspace.session_runtime_v01 import Workspace
from hedgehog.domains.ephemeral_workspace.media_v01 import render
from hedgehog import work_execution_host_v01 as hosts


@pytest.fixture(scope='module')
def assets(tmp_path_factory):
    return generate(tmp_path_factory.mktemp('ews_media')/'sources',6)


def test_role_causality_and_missing_fields_source_only(tmp_path,assets):
    class Variant(roles.ControlledProvider):
        def __init__(self,index,mutate):
            self.index,self.mutate=index,mutate
        def respond(self,role,context):
            value=super().respond(role,context)
            if role==roles.ROLES[self.index]:
                self.mutate(value)
            return value
    base=Workspace(tmp_path/'base',assets)
    variants=[Variant(0,lambda v:v['needs'].remove('crop')),Variant(1,lambda v:v.update(preview='contain'))]
    for i,provider in enumerate(variants):
        session=Workspace(tmp_path/str(i),assets,provider=provider)
        assert not session.services
        assert session.contract!=base.contract
        if i==0:
            with pytest.raises(ValueError,match='operation_not_allowed'):
                session.command('CROP','SQUARE')
        else:
            data=assets[0].read_bytes()
            assert render(data,0,'ORIGINAL',session.contract['preview'])!=render(data,0,'ORIGINAL',base.contract['preview'])
        session.close()
    with pytest.raises(ValueError,match='privacy_refusal'):
        Workspace(tmp_path/'block',assets,provider=Variant(2,lambda v:v.update(decision='block',conflicts=['Unapproved display requested.'])))
    for index,key in [(0,'needs'),(1,'phases'),(2,'decision')]:
        with pytest.raises(ValueError,match='semantic_closed_shape'):
            Workspace(tmp_path/f'absent{index}',assets,provider=Variant(index,lambda v,k=key:v.pop(k)))
    base.close()


def _write_capture_package(root, material):
    """Synthetic semantic evidence only; no Workspace, media fixture or provider call."""
    root.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name,value in sorted(material.items()):
        data=c.canonical(value)
        path=root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        manifest.append(dict(path=name,bytes=len(data),sha256=c.digest(data)))
    data=c.canonical(manifest)
    (root/'MANIFEST.json').write_bytes(data)
    return c.digest(data)


def _capture_package(tmp_path, *, live=False, asset_binding=True):
    base=dict(version=c.VERSION,request=c.REQUEST_A,capability_classes=list(c.CLASSES))
    if asset_binding:
        base['asset_inventory']=[dict(asset='asset:1',sha256='a'*64)]
    records=[]
    for index,role in enumerate(roles.ROLES):
        context=deepcopy(base)
        if index:
            context.update(bsep=dict(needs=records[0]['output']['needs'],source_write=False,publication=False,separate_save=True),
                route_acceptance=dict(decision='ACCEPT',scope=records[0]['output']['needs']))
        if index==2:
            context['obligations']=records[1]['output']
        output=roles.ControlledProvider().respond(role,context)
        records.append(semantics.envelope(role,context,output,mode='LIVE' if live else 'CONTROLLED_DETERMINISTIC',
            model='gemini-2.5-flash' if live else roles.ControlledProvider.model,
            attempt=index+2 if live else 0,raw=c.canonical(output).decode()))
    material={'private/semantic_captures.json':records}
    attempts=[]
    if live:
        for number,record in enumerate([records[0]]+records,1):
            failed=number==1
            attempt=dict(attempt=number,role=record['role'],model=record['model'],projection_ref=record['projection_ref'],
                status='FAILED' if failed else 'RETURNED',elapsed_seconds=0.25,response_model=record['model'],
                usage=dict(prompt_token_count=11,candidates_token_count=3,total_token_count=14))
            raw=c.canonical(dict(output_contract=record['output'])).decode() if failed else record['raw']
            if failed:
                attempt['error_type']='ValueError'
            else:
                attempt.update(response_ref=record['response_ref'],raw_sha256=c.digest(raw.encode()))
            attempts.append(attempt)
            material['private/budget/transport_%02d.json'%number]=dict(role=record['role'],context=record['context'],
                model=record['model'],attempt=number,raw=raw)
            material['private/budget/request_%02d.json'%number]=dict(role=record['role'],model=record['model'],
                contents=c.canonical(dict(role=record['role'],task=record['context'],required_top_level_fields=roles.SCHEMAS[record['order']])).decode(),
                system_instruction='Synthetic closed semantic object.',max_output_tokens=2048,automatic_retries=False,
                projection_ref=record['projection_ref'])
        material['private/budget/attempts.json']=attempts
        for index,record in enumerate(records,1):
            material['private/budget/capture_%02d.json'%index]=record
    root=tmp_path/'package'
    pin=_write_capture_package(root,material)
    config=dict(original_return_root=root,manifest_sha256=pin,expected_mode='LIVE' if live else 'CONTROLLED_DETERMINISTIC',
        records_path='private/semantic_captures.json',attempts_path='private/budget/attempts.json' if live else None)
    return config,material


def _reidentify_capture(record):
    record['raw']=c.canonical(record['output']).decode()
    record['request_ref']=c.identity('semantic_request',record['context'])
    record['projection_ref']=c.identity('semantic_projection',dict(role=record['role'],input=record['context']))
    record['response_ref']=c.identity('semantic_response',{k:v for k,v in record.items() if k!='response_ref'})


def test_full_capture_binding_and_equivalent_copy_source_only(tmp_path,assets):
    original=Workspace(tmp_path/'original',assets)
    records=deepcopy(original.captures)
    package=tmp_path/'capture_origin'
    records_path='private/semantic_captures.json'
    pin=_write_capture_package(package,{records_path:deepcopy(original.captures)})
    origin=semantics.load_capture_origin(package,manifest_sha256=pin,expected_mode='CONTROLLED_DETERMINISTIC',
        records_path=records_path)
    provider=semantics.CapturedProvider(records,[],origin=origin)
    fresh=Workspace(tmp_path/'fresh',assets,provider=provider)
    assert fresh.contract==original.contract and fresh.host is not original.host and fresh.id!=original.id
    for index in range(3):
        record=records[index]
        assert semantics.validate_capture(deepcopy(record),record['role'],record['context'])==record['output']
        for key,value in [('response_ref','ews:wrong'),('request_ref','ews:wrong'),('order',True),('version','wrong'),
                          ('model','forged'),('provider','other'),('raw','{}')]:
            changed=deepcopy(record);changed[key]=value
            with pytest.raises(ValueError):
                semantics.validate_capture(changed,record['role'],record['context'])
        changed=deepcopy(record);changed['output']['unexpected']=True
        with pytest.raises(ValueError):
            semantics.validate_capture(changed,record['role'],record['context'])
    assert provider.index==3
    changed_context=deepcopy(records[0]['context'])
    changed_context['asset_inventory'][0]['sha256']='0'*64
    with pytest.raises(ValueError,match='capture_input_binding'):
        semantics.validate_capture(records[0],records[0]['role'],changed_context)
    original.close();fresh.close()


@pytest.mark.parametrize('live',[False,True])
def test_capture_binding_and_equivalent_copy_without_workspace(tmp_path,live):
    config,_=_capture_package(tmp_path,live=live)
    origin=semantics.load_capture_origin(**config)
    records=semantics.parse(origin.records_bytes)
    attempts=semantics.parse(origin.attempts_bytes)
    provider=semantics.CapturedProvider(deepcopy(records),deepcopy(attempts),origin=origin)
    outputs=[]
    for index in range(3):
        record=records[index]
        outputs.append(provider.respond(record['role'],deepcopy(record['context'])))
        assert semantics.validate_capture(deepcopy(record),record['role'],record['context'])==record['output']
        for key,value in [('response_ref','ews:wrong'),('request_ref','ews:wrong'),('order',True),('version','wrong'),
                          ('model','forged'),('provider','other'),('raw','{}')]:
            changed=deepcopy(record);changed[key]=value
            with pytest.raises(ValueError):
                semantics.validate_capture(changed,record['role'],record['context'])
        changed=deepcopy(record);changed['output']['unexpected']=True
        with pytest.raises(ValueError):
            semantics.validate_capture(changed,record['role'],record['context'])
    assert provider.index==3
    assert roles.compile_contract(outputs)==roles.compile_contract([r['output'] for r in records])
    changed_context=deepcopy(records[0]['context'])
    changed_context['asset_inventory'][0]['sha256']='0'*64
    with pytest.raises(ValueError,match='capture_input_binding'):
        semantics.validate_capture(records[0],records[0]['role'],changed_context)
    with pytest.raises(ValueError,match='capture_role_order'):
        provider.respond(records[0]['role'],records[0]['context'])


@pytest.mark.parametrize('attack',['downgrade','mixed','coherent_output','missing','extra','reordered','last_invalid','nested_type'])
def test_capture_origin_rejects_reconstruction_before_consumption(tmp_path,attack):
    config,_=_capture_package(tmp_path,live=True)
    origin=semantics.load_capture_origin(**config)
    records=semantics.parse(origin.records_bytes)
    attempts=semantics.parse(origin.attempts_bytes)
    if attack in ('downgrade','mixed'):
        for record in records if attack=='downgrade' else records[1:2]:
            record.update(mode='CONTROLLED_DETERMINISTIC',provider='local',attempt=0)
            _reidentify_capture(record)
    if attack in ('downgrade','coherent_output'):
        records[1]['output']['preview']='contain'
        records[2]['context']['obligations']=deepcopy(records[1]['output'])
        for record in records:
            _reidentify_capture(record)
    elif attack=='missing':
        records.pop()
    elif attack=='extra':
        records.append(deepcopy(records[-1]))
    elif attack=='reordered':
        records.reverse()
    elif attack=='last_invalid':
        records[2]['output']['unexpected']=True
        _reidentify_capture(records[2])
    elif attack=='nested_type':
        records[1]['context']['bsep']['source_write']=0
        _reidentify_capture(records[1])
    with pytest.raises(ValueError):
        semantics.CapturedProvider(records,attempts,origin=origin)
    positive=semantics.CapturedProvider.from_origin(origin)
    assert positive.index==0
    for record in positive.records:
        assert positive.respond(record['role'],record['context'])==record['output']


@pytest.mark.parametrize('attempt_index',[0,1,2,3])
@pytest.mark.parametrize('field,value',[('attempt',True),('status','ARBITRARY'),('role','other'),('model','other'),
    ('projection_ref','ews:wrong'),('elapsed_seconds',False),('response_model','other'),('usage',{}),('unexpected',True)])
def test_capture_all_attempts_are_bound(tmp_path,attempt_index,field,value):
    config,_=_capture_package(tmp_path,live=True)
    origin=semantics.load_capture_origin(**config)
    attempts=semantics.parse(origin.attempts_bytes)
    attempts[attempt_index][field]=value
    with pytest.raises(ValueError,match='capture_original_history_binding'):
        semantics.CapturedProvider(semantics.parse(origin.records_bytes),attempts,origin=origin)


@pytest.mark.parametrize('target,field,value',[
    ('attempt','status','STARTED'),('attempt','role',roles.ROLES[1]),('attempt','model','other'),
    ('attempt','projection_ref','ews:wrong'),('attempt','error_type','Unknown'),('attempt','elapsed_seconds',True),
    ('attempt','usage',dict(prompt_token_count=True,candidates_token_count=3,total_token_count=14)),
    ('attempt','response_model','other'),('request','automatic_retries',0),('request','max_output_tokens',True),
    ('request','contents','{}'),('request','projection_ref','ews:wrong'),('request','unexpected',True),
    ('transport','attempt',True),('transport','role',roles.ROLES[1]),('transport','context',{}),
    ('transport','raw','{"needs":["browse"],"uncertainty":[]}'),('transport','unexpected',True)])
def test_capture_loader_checks_full_history_schema(tmp_path,target,field,value):
    config,material=_capture_package(tmp_path,live=True)
    if target=='attempt':
        material['private/budget/attempts.json'][0][field]=value
    else:
        material['private/budget/%s_01.json'%target][field]=value
    # A newly pinned malformed synthetic package must still fail structural checks.
    config['manifest_sha256']=_write_capture_package(config['original_return_root'],material)
    with pytest.raises(ValueError):
        semantics.load_capture_origin(**config)


@pytest.mark.parametrize('transport_index',[1,2,3,4])
@pytest.mark.parametrize('mutation',['none','missing','bool','wrong','extra'])
def test_capture_historical_failure_preserves_all_transport_ordinals(tmp_path,transport_index,mutation):
    # Schema-only regression with the exact original key sets. Actual original
    # manifest-bound acceptance is separately exercised by the external helper.
    config,material=_capture_package(tmp_path,live=True)
    records=material[config['records_path']]
    attempts=material['private/budget/attempts.json']
    attempts[0].pop('usage')
    attempts[0].pop('response_model')
    material.pop('private/budget/request_01.json')
    assert set(attempts[0])=={'attempt','elapsed_seconds','error_type','model','projection_ref','role','status'}
    assert attempts[0]['status']=='FAILED' and attempts[0]['attempt']==1
    for index in (1,2,3,4):
        transport=material['private/budget/transport_%02d.json'%index]
        assert set(transport)=={'attempt','context','model','raw','role'}
        assert type(transport['attempt']) is int and transport['attempt']==index
    for index in (2,3,4):
        assert set(material['private/budget/request_%02d.json'%index])=={
            'automatic_retries','contents','max_output_tokens','model','projection_ref','role','system_instruction'}
    snapshot={name:c.canonical(value) for name,value in material.items()}
    semantics._validate_history(records,attempts,snapshot,'private/budget',legacy_failure=True)
    with pytest.raises(ValueError,match='capture_attempt_shape'):
        semantics._validate_history(records,attempts,snapshot,'private/budget',legacy_failure=False)
    if mutation!='none':
        changed=deepcopy(material)
        transport=changed['private/budget/transport_%02d.json'%transport_index]
        if mutation=='missing':
            transport.pop('attempt')
        elif mutation=='bool':
            transport['attempt']=True
        elif mutation=='wrong':
            transport['attempt']=transport_index+1
        else:
            transport['unexpected']=True
        with pytest.raises(ValueError,match='capture_transport_(shape|attempt)'):
            semantics._validate_history(records,attempts,{name:c.canonical(value) for name,value in changed.items()},
                'private/budget',legacy_failure=True)
        semantics._validate_history(records,attempts,snapshot,'private/budget',legacy_failure=True)


def test_capture_origin_and_provider_snapshots_are_immutable(tmp_path):
    from dataclasses import FrozenInstanceError
    config,_=_capture_package(tmp_path,live=True)
    origin=semantics.load_capture_origin(**config)
    records=semantics.parse(origin.records_bytes)
    attempts=semantics.parse(origin.attempts_bytes)
    provider=semantics.CapturedProvider(records,attempts,origin=origin)
    expected=deepcopy(records)
    records[2]['output'].clear()
    attempts[0]['status']='ARBITRARY'
    provider.records[1]['output'].clear()
    provider.attempts.clear()
    with pytest.raises(FrozenInstanceError):
        origin.expected_mode='CONTROLLED_DETERMINISTIC'
    with pytest.raises(TypeError):
        origin.materials[0]=('replacement',b'{}')
    with pytest.raises(AttributeError):
        provider.records=[]
    # Subsequent disk mutation cannot change an already checked byte snapshot.
    (config['original_return_root']/config['records_path']).write_text('[]')
    for record in expected:
        output=provider.respond(record['role'],record['context'])
        assert output==record['output']
        output.clear()
    assert provider.records==expected
    with pytest.raises(ValueError,match='capture_material_hash'):
        semantics.load_capture_origin(**config)


def test_capture_loader_requires_independent_mode_and_pin(tmp_path):
    config,material=_capture_package(tmp_path,live=True)
    with pytest.raises(TypeError):
        semantics.CapturedProvider(material[config['records_path']],material['private/budget/attempts.json'])
    with pytest.raises(ValueError,match='capture_loader_origin_required'):
        semantics.CapturedProvider([],[],origin={})
    with pytest.raises(ValueError,match='capture_manifest_pin_mismatch'):
        semantics.load_capture_origin(**dict(config,manifest_sha256='0'*64))
    with pytest.raises(ValueError,match='capture_expected_origin_mode'):
        semantics.load_capture_origin(**dict(config,expected_mode='CONTROLLED_DETERMINISTIC',attempts_path=None))
    with pytest.raises(ValueError,match='capture_live_ledger_required'):
        semantics.load_capture_origin(**dict(config,attempts_path=None))
    with pytest.raises(ValueError,match='capture_relative_path'):
        semantics.load_capture_origin(**dict(config,records_path='../semantic_captures.json'))
    manifest_path=config['original_return_root']/'MANIFEST.json'
    manifest=semantics.parse(manifest_path.read_bytes())
    manifest[0]['bytes']=True
    data=c.canonical(manifest)
    manifest_path.write_bytes(data)
    with pytest.raises(ValueError,match='capture_manifest_inventory'):
        semantics.load_capture_origin(**dict(config,manifest_sha256=c.digest(data)))


@pytest.mark.parametrize('path',['private/budget/attempts.json','private/budget/request_01.json',
    'private/budget/transport_01.json','private/budget/capture_03.json'])
def test_capture_manifest_binds_all_side_evidence(tmp_path,path):
    config,_=_capture_package(tmp_path,live=True)
    (config['original_return_root']/path).write_text('{}')
    with pytest.raises(ValueError,match='capture_material_hash'):
        semantics.load_capture_origin(**config)


@pytest.mark.parametrize('attack',['extra','missing','symlink','authority','unknown_legacy_failure'])
def test_capture_loader_rejects_inventory_and_authority(tmp_path,attack):
    config,material=_capture_package(tmp_path,live=True)
    root=config['original_return_root']
    if attack=='extra':
        (root/'private/budget/capture_04.json').write_text('{}')
    elif attack=='missing':
        (root/'private/budget/request_01.json').unlink()
    elif attack=='symlink':
        path=root/'private/budget/transport_01.json'
        data=path.read_bytes()
        path.unlink()
        (tmp_path/'outside.json').write_bytes(data)
        path.symlink_to(tmp_path/'outside.json')
    elif attack=='authority':
        record=material[config['records_path']][2]
        record['context']['root_decision']=dict(decision='ACCEPT',permission=True)
        _reidentify_capture(record)
        config['manifest_sha256']=_write_capture_package(root,material)
    else:
        material['private/budget/attempts.json'][0].pop('usage')
        material['private/budget/attempts.json'][0].pop('response_model')
        config['manifest_sha256']=_write_capture_package(root,material)
    with pytest.raises(ValueError):
        semantics.load_capture_origin(**config)


def test_capture_historical_controlled_context_is_not_rebound(tmp_path):
    config,_=_capture_package(tmp_path,asset_binding=False)
    origin=semantics.load_capture_origin(**config)
    provider=semantics.CapturedProvider.from_origin(origin)
    record=provider.records[0]
    new_context=dict(record['context'],asset_inventory=[dict(asset='asset:1',sha256='a'*64)])
    with pytest.raises(ValueError,match='capture_input_binding'):
        provider.respond(record['role'],new_context)
    assert provider.index==0
    for record in provider.records:
        assert provider.respond(record['role'],record['context'])==record['output']


def test_capture_cli_source_only_and_historical_workspace_refusal(tmp_path,monkeypatch,capsys):
    from demo import run_ephemeral_workspace_v01 as cli
    config,_=_capture_package(tmp_path,asset_binding=False)
    def forbidden(*args,**kwargs):
        pytest.fail('source-only capture must not create a Workspace or fixtures')
    monkeypatch.setattr(cli,'Workspace',forbidden)
    monkeypatch.setattr(cli,'generate',forbidden)
    argv=['demo','--mode','captured','--original-return-root',str(config['original_return_root']),
        '--original-manifest-sha256',config['manifest_sha256'],'--replay-mode','controlled',
        '--original-records-path',config['records_path']]
    monkeypatch.setattr('sys.argv',argv+['--capture-source-only'])
    cli.main()
    report=json.loads(capsys.readouterr().out)
    assert report['roles']==3 and report['new_model_calls']==0
    assert report['asset_binding']=='HISTORICAL_CONTEXT_WITHOUT_ASSET_INVENTORY'
    assert report['workspace_execution']=='NOT_PERFORMED'
    run_dir=tmp_path/'must_not_exist'
    monkeypatch.setattr('sys.argv',argv+['--run-dir',str(run_dir)])
    with pytest.raises(ValueError,match='historical_capture_without_asset_inventory_source_only'):
        cli.main()
    assert not run_dir.exists()


def test_controlled_contrast_same_registry_actual_execution(tmp_path,assets):
    session=Workspace(tmp_path/'contrast',assets,c.REQUEST_B)
    try:
        assert session.contract['active_classes']==list(c.CLASSES[:4])
        assert 'EXPOSURE' not in session.allowed and 'CROP' not in session.allowed
        session.command('OPEN')
        original=session.preview['sha256']
        for op,value in [('EXPOSURE',5),('CROP','SQUARE')]:
            with pytest.raises(ValueError,match='operation_not_allowed'):
                session.command(op,value)
        session.command('NEXT')
        assert session.preview['sha256']!=original
        assert len(session.host.registry.action_packet_lifecycle_entries)==2
        assert session.work_results[1].consumed_fields[0].disposition=='USED'
        assert len(session.host.completed_work)==4
    finally:
        session.close('DECLINE_SAVE_END')
    assert not (session.directory/'output/selection.json').exists()
    assert session.report()['source_preserved'] and session.status=='CLOSED_SUCCESS'
    with pytest.raises(ValueError,match='workspace_not_current'):
        session.command('NEXT')


def test_current_root_save_revision_and_exact_one_sidecar(tmp_path,assets):
    session=Workspace(tmp_path/'save',assets)
    try:
        session.command('OPEN')
        session.command('SELECT',True)
        with pytest.raises(ValueError,match='save_approval_current'):
            session.command('SAVE','ews:approval:unissued')
        session.command('REQUEST_SAVE')
        previous=deepcopy(session.pending)
        old=session.approve(previous)
        session.command('RATE',5)
        with pytest.raises(ValueError,match='save_approval_current'):
            session.command('SAVE',old)
        with pytest.raises(ValueError,match='approval_candidate_changed'):
            session.approve(previous)
        session.command('REQUEST_SAVE')
        wrong=deepcopy(session.pending);wrong['slot']='foreign.json'
        with pytest.raises(ValueError,match='approval_candidate_changed'):
            session.approve(wrong)
        approval=session.approve(deepcopy(session.pending))
        intended=deepcopy(session.pending)
        session.command('SAVE',approval)
        actual=(session.directory/'output/selection.json').read_bytes()
        assert c.digest(actual)==intended['bytes_sha256'] and json.loads(actual)==intended['content']
        for ref in (approval,c.identity('approval',session.history[-1]['receipt'])):
            with pytest.raises(ValueError):
                session.command('SAVE',ref)
        assert list((session.directory/'output').iterdir())==[session.directory/'output/selection.json']
        clock=session.source.sample()
        with pytest.raises(ValueError):
            hosts.dispatch_current_action_v01(session.host,packet_id=session.history[0]['packet_id'],task_id=session.id,
                expected_revision=session.host.revision-1,evaluation_time=clock.evaluation_time,
                evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
        assert all(record['root_decision']['decision']=='ACCEPT' for record in session.history)
    finally:
        session.close()
    assert session.report()['source_preserved'] and session.status=='CLOSED_SUCCESS'


def test_mixed_semantic_obligations_source_only(tmp_path,assets):
    from demo.ephemeral_workspace_fixtures_v01 import generate_media
    media=generate_media(tmp_path/'media')
    sessions=[]
    try:
        for label,request in (('mixed',c.REQUEST_MIXED),('speech',c.REQUEST_SPEECH),('photo',c.REQUEST_B)):
            s=Workspace(tmp_path/label,assets,request,media=media);sessions.append(s)
            assert len(s.captures)==3 and all(v['mode']=='CONTROLLED_DETERMINISTIC' for v in s.captures)
            assert not s.services and s.media_review is None
        mixed,speech,photo=sessions
        assert mixed.contract['media']['audio_policy']=='SILENT_CONTINUE'
        assert speech.contract['media']['audio_policy']=='REQUIRE_AUDIO' and speech.contract['media']['speech_review']
        assert 'media' not in photo.contract and 'PLAY' not in photo.allowed and 'AudioSink' not in photo.contract['active_classes']
        assert mixed.captures[2]['context']['obligations']==mixed.captures[1]['output']
        class Conflict(roles.ControlledProvider):
            def respond(self,role,context):
                v=super().respond(role,context)
                if role==roles.ROLES[1]:v['audio_policy']='SILENT_CONTINUE'
                return v
        with pytest.raises(ValueError):Workspace(tmp_path/'conflict',assets,c.REQUEST_SPEECH,Conflict(),media=media)
    finally:
        for s in sessions:s.close()


def test_local_semantic_memory_real_descent_and_fresh_authority(tmp_path,assets):
    import sys
    from hedgehog.domains.ephemeral_workspace.semantic_adapter_v01 import LiveProvider
    from hedgehog.domains.ephemeral_workspace.memory_adapter_v01 import SemanticMemory,MemoryProvider,dependencies
    producer_calls=[]
    tool=4;event=sys.monitoring.events.PY_START
    sys.monitoring.use_tool_id(tool,'ews-memory-live-producer-observer')
    sys.monitoring.register_callback(tool,event,lambda *args:producer_calls.append('LIVE_PROVIDER_RESPOND'))
    sys.monitoring.set_local_events(tool,LiveProvider.respond.__code__,event)
    store=SemanticMemory(tmp_path/'durable_drs')
    cold=warm=None
    try:
        cold=Workspace(tmp_path/'cold',assets,c.REQUEST_B)
        dep=dependencies(cold);now=cold.source.sample().evaluation_time
        assert store.select(root=cold.root,request=cold.request,dependency=dep,now=now) is None
        record=store.remember(cold)
        assert store.select(root='root:ews:personal:foreign',request=cold.request,dependency=dep,now=now) is None
        assert store.select(root=cold.root,request=cold.request,dependency=dict(dep,policy='changed'),now=now) is None
        assert store.select(root=cold.root,request=cold.request,dependency=dep,now=now,policy='ews.changed.v01') is None
        assert store.select(root=cold.root,request=cold.request,dependency=dep,now=now+3601) is None
        provider=MemoryProvider(store)
        warm=Workspace(tmp_path/'warm',assets,c.REQUEST_B,provider,personal_root=cold.root)
        assert warm.host is not cold.host and warm.id!=cold.id and not warm.approvals and not warm.services
        assert warm.mode=='DRS_REUSE_CANDIDATE' and warm.memory_origin['record_id']==record
        assert warm.report()['semantic_drs']=='ACTUAL_CURRENT_CANDIDATE_DESCENT'
        assert warm.contract==cold.contract and warm.route_review[2].decision_id!=cold.route_review[2].decision_id
        warm.command('OPEN');warm.command('SELECT',True);warm.command('RATE',4)
        warm.command('REQUEST_SAVE');approval=warm.approve(warm.pending)
        warm.command('SAVE',approval)
        store.remember_saved(warm)
        before=(len(warm.executed),len(warm.services),c.digest((warm.directory/'output/selection.json').read_bytes()))
        info=store.select(root=warm.root,request=warm.request,dependency=dependencies(warm),now=warm.source.sample().evaluation_time,kind='saved_work')
        assert info[0]['sidecar_sha256']==warm.saved['sha256'] and info[0]['history_ref']==c.digest(warm.history)
        assert before==(len(warm.executed),len(warm.services),c.digest((warm.directory/'output/selection.json').read_bytes()))
        assert provider.calls==0
        assert producer_calls==[]
        print('MEMORY_LIVE_PRODUCER_OBSERVED_CALLS=0')
    finally:
        sys.monitoring.set_local_events(tool,LiveProvider.respond.__code__,0)
        sys.monitoring.register_callback(tool,event,None);sys.monitoring.free_tool_id(tool)
        if warm:warm.close()
        if cold:cold.close()


def test_live_stage_extension_preserves_attempts_and_reserve(tmp_path):
    from hedgehog.domains.ephemeral_workspace.semantic_adapter_v01 import LiveStageBudget
    chains=dict(main=c.REQUEST_MIXED,contrast=c.REQUEST_B)
    budget=LiveStageBudget(tmp_path,chains)
    context=dict(request=c.REQUEST_MIXED)
    index=budget.reserve('main',roles.ROLES[0],context)
    budget.finish(index,dict(status='FAILED',attempt=1,role=roles.ROLES[0],model='unit-observer-no-transport',
        projection_ref=c.identity('semantic_projection',dict(role=roles.ROLES[0],input=context)),elapsed_seconds=0,error_type='ValueError'))
    before=json.loads(budget.path.read_bytes())
    extended=LiveStageBudget(tmp_path,chains,transport_ceiling=50)
    after=json.loads(extended.path.read_bytes())
    assert after['attempts']==before['attempts'] and after['policy_changes'][0]['previous']==before['policy']
    assert after['policy_changes'][0]['attempts_preserved']==1
    with pytest.raises(ValueError,match='live_stage_policy_changed'):LiveStageBudget(tmp_path,chains)
    with pytest.raises(ValueError,match='live_stage_finite_ceiling'):LiveStageBudget(tmp_path,chains,transport_ceiling=51)
    index=extended.reserve('main',roles.ROLES[0],context)
    with pytest.raises(ValueError,match='live_stage_incomplete_attempt'):extended.reserve('contrast',roles.ROLES[0],dict(request=c.REQUEST_B))
    assert index==2


def test_memory_cold_search_precedes_semantic_preparation_source_only(tmp_path,assets):
    import time
    from types import SimpleNamespace
    from hedgehog.domains.ephemeral_workspace.memory_adapter_v01 import SemanticMemory,dependencies
    calls=[]
    class ObservedControlled(roles.ControlledProvider):
        def respond(self,role,context):
            calls.append(role)
            return super().respond(role,context)
    root='root:ews:personal:coldorder'
    store=SemanticMemory(tmp_path/'drs')
    source=SimpleNamespace(source_hashes={str(i):c.digest(p.read_bytes()) for i,p in enumerate(assets)},media_fixture=None)
    assert store.select(root=root,request=c.REQUEST_B,dependency=dependencies(source),now=int(time.time())) is None
    assert calls==[] and store.events[0]['op']=='SEARCH'
    s=Workspace(tmp_path/'cold',assets,c.REQUEST_B,ObservedControlled(),personal_root=root)
    try:
        assert calls==list(roles.ROLES) and s.work_results and not s.services
        assert dependencies(source)==dependencies(s)
        record=store.remember(s)
        selected=store.select(root=root,request=s.request,dependency=dependencies(s),now=s.source.sample().evaluation_time)
        assert selected[1]['record_id']==record
        assert [event['op'] for event in store.events]==['SEARCH','WRITE','SEARCH']
        print('COLD_ORDER=SEARCH_ABSENT_THEN_3_CONTROLLED_ROLES_ACTUAL_WORK_WRITE_ELIGIBLE_DESCENT')
    finally:s.close()


def test_memory_reference_projection_uses_bound_source_digest():
    from hedgehog.domains.ephemeral_workspace import memory_adapter_v01 as mem
    from hedgehog import drs_semantic_address_v01 as address
    source='work_results:5774b5428f8b5a4011decea879d19f50ad962e93d943823121685795e924c787'
    material=dict(kind='semantic_recipe',request=c.REQUEST_B,dependencies=dict(policy=mem.POLICY),
        value=[dict(needs=['browse'],uncertainty=[])],sources=[source])
    review=mem._review('root:ews:personal:referencecontrol',material,1895961600)
    record=mem._record(material,review,1895961600,3600,'root:ews:personal:referencecontrol')
    assert record.source_reference_ids==(c.digest(source.encode()),)
    assert record.content_fingerprint==c.digest(material)
    assert address.validate_meaning_record_v01(record)[0]


def test_controlled_material_uncertainty_refuses_before_assembly():
    context=dict(version=c.VERSION,request='Make these photographs better.',capability_classes=list(c.CLASSES))
    result=roles.ControlledProvider().respond(roles.ROLES[0],context)
    assert result['uncertainty']
    with pytest.raises(ValueError):roles.validate(roles.ROLES[0],result,context)


def test_semantic_metamorphic_contexts_no_extra_capabilities():
    from copy import deepcopy
    from hedgehog.domains.ephemeral_workspace.semantic_roles_v01 import compile_contract
    base=dict(version=c.MIXED_VERSION,request=c.REQUEST_B,capability_classes=list(c.CLASSES),
        asset_inventory=[dict(asset='opaque:one',sha256='a'*64)],media_inventory=dict(available=True))
    variants=[base,dict(base,request='Please browse, rate and select photographs. I do not need editing, video or sound.'),
        dict(base,asset_inventory=[dict(asset='renamed:asset',sha256='a'*64)]),
        dict(base,capability_classes=list(reversed(c.CLASSES))),dict(base,capability_classes=list(c.CLASSES)+['PrintingNeedle'])]
    contracts=[]
    for context in variants:
        context=deepcopy(context);values=[]
        for index,role in enumerate(roles.ROLES):
            if index:context.update(bsep=dict(needs=values[0]['needs']),route_acceptance=dict(decision='ACCEPT'))
            if index==2:context['obligations']=values[1]
            output=roles.ControlledProvider().respond(role,context);roles.validate(role,output,context);values.append(output)
        contracts.append(compile_contract(values))
    assert all(x==contracts[0] for x in contracts)
    assert not set(contracts[0]['commands']) & {'PLAY','EXPOSURE','CROP'}


def test_command_type_and_range():
    for value in [dict(op='RATE',value=True),dict(op='RATE',value=6),dict(op='SELECT',value=1),
                  dict(op='EXPOSURE',value=21),dict(op='NEXT',value=0),dict(op='CROP',value='RAW'),
                  dict(op='NEXT',value=None,extra=1)]:
        with pytest.raises(ValueError):
            c.command(value,c.BASE+c.EDIT)
    assert c.command(dict(op='RATE',value=4),c.BASE)['value']==4

def test_media_evidence_frozen_mapping_isolation():
    from types import MappingProxyType
    from hedgehog.domains.ephemeral_workspace.evidence_v01 import media_value
    original={'limits':MappingProxyType({'steps':(1,2),'result':{'status':'PASS'}})}
    plain=media_value(MappingProxyType(original))
    assert plain=={'limits':{'steps':[1,2],'result':{'status':'PASS'}}}
    plain['limits']['result']['status']='CHANGED'
    assert original['limits']['result']['status']=='PASS'
    with pytest.raises(ValueError,match='media_evidence_string_keys'):media_value(MappingProxyType({1:'bad'}))
    with pytest.raises(ValueError,match='unsupported_media_evidence_value'):media_value(object())


def _check_media_return(session, save):
    from dataclasses import replace
    from hedgehog.domains.ephemeral_workspace import media_continuation_v01 as mc
    api=mc.e;args=session.delta_arguments;source=args['source_context'];graph=args['dependency_graph'];edges=args['dependency_edges']
    bindings=tuple((v.dependent_artifact_id,v.dependency_artifact_id,v.dependency_field_pointers,v.edge_class) for v in edges)
    kw=dict(manifest=source.integrity_manifest,replay=source.integrity_replay,source_artifacts=source.baseline_source_artifacts,
        graph_version=graph.graph_version,transaction_id=graph.transaction_id,owning_root_id=graph.owning_root_id,
        domain_id=graph.domain_id,policy_version=graph.policy_version,schema_versions=graph.schema_versions,
        source_history_hash=graph.source_history_hash)
    basis,rebuilt=api.project_integrity_replay_dependency_edges_v01(**kw,edge_projection_bindings=tuple(tuple(list(v)) for v in bindings))
    assert rebuilt==edges and rebuilt is not edges and basis==graph.graph_basis_sha256
    changed=args['source_bindings'][0].baseline_source_artifact_id
    omitted=tuple(v for v in bindings if v[1]!=changed)
    try:api.project_integrity_replay_dependency_edges_v01(**kw,edge_projection_bindings=omitted)
    except ValueError as exc:assert str(exc)=='g2e_dependency_graph_missing_edge';missing=str(exc)
    else:raise AssertionError('missing real dependency accepted')
    save('N15_missing_dependency.json',dict(reason=missing,fresh_equivalent=True,omitted=changed,remaining=omitted))

    def affected(observed):
        fp=api.build_dependency_fingerprint_v01(profile=api.build_dependency_fingerprint_profile_v01(),graph=graph,
            dependency_edges=edges,source_artifacts=observed,policy_version=graph.policy_version,
            schema_versions=graph.schema_versions,source_history_hash=graph.source_history_hash)
        altered=[]
        for old in args['changed_artifact_bindings']:
            value=replace(old,observed_dependency_fingerprint=fp)
            altered.append(replace(value,changed_artifact_binding_id=api.rebuild_changed_artifact_binding_identity_v01(value)))
        delta=replace(args['delta'],dependency_fingerprint_after=fp,ordered_changed_artifact_binding_ids=tuple(v.changed_artifact_binding_id for v in altered))
        delta=replace(delta,delta_id=api.rebuild_world_state_delta_identity_v01(delta))
        request=api.build_affected_set_request_v01(delta=delta,graph=graph,trace_refs=(delta.delta_id,graph.graph_id))
        return api.compute_affected_set_v01(request=request,delta=delta,graph=graph,source_bindings=args['source_bindings'],
            changed_field_bindings=args['changed_field_bindings'],changed_artifact_bindings=tuple(altered),dependency_edges=edges,
            baseline_source_artifacts=source.baseline_source_artifacts,observed_source_artifacts=observed)

    old=source.observed_source_artifacts[2];plain=mc.abi.kernel_artifact_to_plain_dict_v01(old)
    equal=mc.abi.build_kernel_artifact_v01(**dict(plain,trace_refs=tuple(plain['trace_refs']),parent_refs=tuple(plain['parent_refs'])))
    positive=tuple(equal if v is old else v for v in source.observed_source_artifacts)
    assert equal==old and equal is not old and affected(positive)==session.delta_return.affected_result
    payload=deepcopy(plain['payload']);first=next(iter(payload['edits']));payload['edits'][first]['rating']+=1
    bad=mc.source_artifact(payload,session,session.audio_loss['observed_at'],(old.artifact_id,))
    assert not mc.abi.validate_kernel_artifact_v01(bad)
    try:affected(tuple(bad if v is old else v for v in source.observed_source_artifacts))
    except ValueError as exc:assert str(exc)=='g2e_delta_source_binding_set_mismatch';reason=str(exc)
    else:raise AssertionError('coherently changed preserved photo accepted')
    save('N15_preserved_photo.json',dict(reason=reason,fresh_equivalent=True,original=plain,changed=mc.abi.kernel_artifact_to_plain_dict_v01(bad)))
    retained=session.delta_return.recomputed_g2d_execution_bundle
    binding=retained.temporal_binding;verification=retained.temporal_verification
    report=mc.d.validate_fractal_current_temporal_binding_v01(replace(binding),source_context=retained.source_context,temporal_verification=verification)
    assert report.status=='PASS'
    rows=[]
    for name in ('evaluation_time_epoch_seconds','host_revision'):
        invalid=replace(binding,**{name:getattr(binding,name)+1})
        report=mc.d.validate_fractal_current_temporal_binding_v01(invalid,source_context=retained.source_context,temporal_verification=verification)
        assert report.status=='FAIL_CLOSED'
        rows.append(dict(field=name,status=report.status,reasons=list(report.reason_codes)))
    save('N15_temporal.json',dict(fresh_equivalent='PASS',refusals=rows))
    kept=retained.retained_consumptions[0]
    wrong=next(v for v in retained.cell_results if v.cell_id!=kept.consumed_result.cell_id)
    altered=replace(kept,consumed_result=wrong)
    swapped=replace(retained,retained_consumptions=(altered,*retained.retained_consumptions[1:]),
        temporal_verification=retained.temporal_verification)
    bad_bundle=replace(session.delta_return,recomputed_g2d_execution_bundle=swapped)
    try:mc.consume_delta(session,bad_bundle)
    except ValueError as exc:assert str(exc)=='media_unaffected_D_result_changed';wrong_reason=str(exc)
    else:raise AssertionError('genuine result from wrong cell substituted for retained sibling')
    save('N15_wrong_retained_consumer.json',dict(reason=wrong_reason,real_wrong_result=wrong.result_id,
        original_result=kept.consumed_result.result_id,scope='DOMAIN_CAUSAL_CONSUMER; NO_CHECKSUM_USED_AS_ORACLE'))
    before=session.photo_work()
    assert mc.consume_delta(session,session.delta_return)==session.media_delta['consumed']
    assert before==session.photo_work()
    save('N15_final_positive.json',dict(consumer='PASS',photo_unchanged=True))


def _mixed_save(directory,name,value):
    from hedgehog.domains.ephemeral_workspace.evidence_v01 import media_value
    (directory/name).write_bytes(c.canonical(media_value(value))+b'\n')


@pytest.fixture(scope='module',params=('optional','essential'))
def actual_mixed_return(request,tmp_path_factory):
    import os,time
    from demo.ephemeral_workspace_fixtures_v01 import generate_media
    root=Path(os.environ['EWS_MIXED_EVIDENCE'])/request.param if os.environ.get('EWS_MIXED_EVIDENCE') else tmp_path_factory.mktemp('actual_mixed_'+request.param)
    root.mkdir(parents=True,exist_ok=True)
    assets=generate(root/'photos',6);media=generate_media(root/'media')
    s=Workspace(root/'workspace',assets,c.REQUEST_MIXED if request.param=='optional' else c.REQUEST_SPEECH,lifetime=7200,media=media)
    save=lambda name,value:_mixed_save(root,name,value)
    try:
        s.command('OPEN');s.command('SELECT',True);s.command('RATE',4);s.command('EXPOSURE',3)
        before=s.photo_work();save('photo_before.json',before)
        s.prepare_media()
        save('D_output.json',s.media_review['output']);save('D_work_result.json',s.media_review['artifact'])
        s.command('PLAY');time.sleep(0.6)
        assert s.media_state['frames']>0 and s.media_state['samples']>0 and s.media_thread.is_alive(),s.media_state
        save('active_media.json',dict(s.media_state))
        if request.param=='essential':
            s.command('REVIEW_MEDIA')
            assert s.media_state['review'].startswith('AWAITING_HUMAN_SPEECH_ASSESSMENT')
        s.withdraw_audio()
        save('audio_loss.json',s.audio_loss);save('consumed.json',s.media_delta['consumed'])
        yield dict(session=s,before=before,save=save,root=root,essential=request.param=='essential')
    finally:
        if hasattr(s,'delta_return') and not (root/'common_return/E_return.json').exists():
            from hedgehog.domains.ephemeral_workspace.evidence_v01 import save_media_return
            try:save_media_return(s,root/'common_return')
            except Exception as exc:save('projection_failure.json',dict(type=type(exc).__name__,reason=str(exc)))
        s.close()
        save('report_final.json',s.report());save('captures.json',s.captures);save('media_events.json',s.media_events)
        save('all_processes_final.json',[dict(role=p.role,pid=p.process.pid,rc=p.process.poll()) for p in s.services])
        assert all(p.process.poll() is not None for p in s.services)
        assert s.media_thread is None or not s.media_thread.is_alive()


def test_actual_mixed_D_E_consumption_and_unaffected_work(actual_mixed_return):
    v=actual_mixed_return;s=v['session'];consumed=s.media_delta['consumed']
    assert s.photo_work()==v['before']
    assert s.producer_counts==dict(photo_preview=v['before']['producer_count'],media_contract=1,delta=1)
    assert consumed['audio_available'] is False
    assert s.audio_loss['receipt']['reaped'] and s.audio_loss['prior_samples']>0 and s.audio_loss['prior_frames']>0
    assert s.audio_loss['stale_packet_refusal']=='host_current_action_not_executable'
    assert s.audio_loss['observed_at']<s.media_pending['authorization']['root_bound'].canonical_projection.temporal_authority.expires_at_utc
    assert s.media_delta['bundle'].final_root_decision_result.target_root_id==s.root==s.host.owning_root_id
    assert s.media_delta['review'][2].decision=='ACCEPT'
    assert len(s.history)==(6 if v['essential'] else 5)
    v['save']('photo_after_E.json',s.photo_work())


def test_actual_mixed_coherent_public_neighbors(actual_mixed_return):
    v=actual_mixed_return
    _check_media_return(v['session'],v['save'])


def test_actual_mixed_optional_essential_and_save_once(actual_mixed_return):
    import time
    from hedgehog.domains.ephemeral_workspace.viewer_v01 import Viewer
    from tests.test_ephemeral_workspace_services_v01 import request
    import urllib.error
    v=actual_mixed_return;s=v['session'];view=Viewer(s)
    try:
        with request(view.control_url+'/state',view.control_token) as response:
            state=json.load(response)
        assert state['media']['audio']=='UNAVAILABLE'
        with request(view.control_url+'/frame/'+s.preview['frame_ref'],view.control_token) as response:
            assert c.digest(response.read())==s.preview['sha256']
        with pytest.raises(urllib.error.HTTPError):request(view.control_url+'/audio-loss',view.control_token,{})
        before=len(s.executed)
        if v['essential']:
            for op in ('PLAY','REVIEW_MEDIA'):
                with pytest.raises(ValueError,match='speech_review_audio_unavailable'):s.command(op)
            assert len(s.executed)==before and s.media_state['status']=='AUDIO_REQUIRED_PAUSED'
        else:
            old_frames=s.media_state['frames'];old_samples=s.media_state['samples']
            s.command('PLAY');time.sleep(.6);s.command('PAUSE')
            assert s.media_state['frames']>old_frames and s.media_state['samples']==old_samples
            assert s.media_state['audio']=='UNAVAILABLE'
        s.command('REQUEST_SAVE');old=deepcopy(s.pending);old_approval=s.approve(old)
        s.command('RATE',5)
        with pytest.raises(ValueError):s.command('SAVE',old_approval)
        s.command('REQUEST_SAVE')
        with pytest.raises(ValueError):s.approve(old)
        with request(view.owner_url+'/approve',view.owner_token,dict(candidate=s.pending)) as response:accepted=json.load(response)
        assert accepted['saved'] and s.write_outcome=='WRITTEN_ONCE'
        actual=(s.directory/'output/selection.json').read_bytes()
        assert c.digest(actual)==s.saved['sha256']
        with pytest.raises(ValueError):s.command('SAVE',s.saved['approval'])
        with pytest.raises(ValueError):s.command('SAVE',s.history[-1]['receipt']['artifact_id'])
        v['save']('sidecar_actual.json',json.loads(actual))
        v['save']('optional_essential_and_save.json',dict(essential=v['essential'],state=s.media_state,write=s.saved,
            old_approval_refused=True,receipt_not_permission=True,HTTP_owner_separate=True))
    finally:view.close()


def test_actual_mixed_export_and_active_close(actual_mixed_return):
    import time
    from hedgehog.domains.ephemeral_workspace.evidence_v01 import save_media_return
    v=actual_mixed_return;s=v['session']
    start=time.monotonic();pins=save_media_return(s,v['root']/'common_return')
    v['save']('projection.json',dict(pins=pins,seconds=time.monotonic()-start))
    if not v['essential']:
        s.command('SEEK',0);s.command('PLAY');assert s.media_thread.is_alive()
    start=time.monotonic();s.command('END')
    assert s.cleanup_report['status']=='CLOSED_SUCCESS' and not s.media_thread.is_alive()
    assert s.report()['source_preserved'] and s.report()['media_sources_preserved']
    with pytest.raises(ValueError):s.command('PLAY')
    v['save']('active_close.json',dict(seconds=time.monotonic()-start,cleanup=s.cleanup_report,
        saved=s.saved,finite_worker_stopped=not s.media_thread.is_alive()))
