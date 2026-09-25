"""Locally bound semantic envelopes; captured reexecution creates no authority."""
import ast
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path, PurePosixPath
import time
from . import contracts_v01 as c, semantic_roles_v01 as roles


# Independently reviewed EWS-1 return, not a hash supplied by its envelopes.
# This pin permits only the documented attempt-1 legacy schema exception.
ORIGINAL_RETURN_MANIFEST_SHA256 = '02dbe563a7a05fc44eb3f6c69e93db2be851d0ee7bcf2eadb1ac13fa29a62d46'
ORIGINAL_LIVE_RECORDS = 'private/live_photo_A_02/semantic_captures.json'
ORIGINAL_LIVE_ATTEMPTS = 'private/live_budget/attempts.json'
ORIGINAL_CONTROLLED_RECORDS = 'private/first_photo_04/semantic_captures.json'


def parse(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            c.require(key not in out, 'duplicate_json_key')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda x: c.require(False,'nonfinite_json'))


def _json_bytes(value):
    """Reject Python-only/coercible types before taking an immutable snapshot."""
    if type(value) is dict:
        c.require(all(type(key) is str for key in value), 'capture_json_type')
        for item in value.values():
            _json_bytes(item)
    elif type(value) is list:
        for item in value:
            _json_bytes(item)
    else:
        c.require(value is None or type(value) in (str, bool, int, float), 'capture_json_type')
        c.require(type(value) is not float or math.isfinite(value), 'capture_json_number')
    return c.canonical(value)


def _sha256(value):
    return type(value) is str and len(value)==64 and all(ch in '0123456789abcdef' for ch in value)


def _relative_path(value):
    c.require(type(value) is str and bool(value) and '\\' not in value, 'capture_relative_path')
    path = PurePosixPath(value)
    c.require(not path.is_absolute() and '..' not in path.parts and path.as_posix()==value, 'capture_relative_path')
    return path


@dataclass(frozen=True)
class _CaptureOrigin:
    """Loader-produced immutable evidence, never a Root or service capability."""
    expected_mode: str
    manifest_sha256: str
    records_path: str
    records_bytes: bytes
    attempts_bytes: bytes
    materials: tuple


def _validate_contexts(records, expected_mode):
    base = None
    for index, record in enumerate(records):
        c.require(type(record) is dict and type(record.get('context')) is dict, 'capture_context_shape')
        context = record['context']
        keys = ['version', 'request', 'capability_classes']
        if context.get('version')==c.MIXED_VERSION:
            keys.append('media_inventory')
        if expected_mode=='LIVE' or 'asset_inventory' in context:
            keys.append('asset_inventory')
        if index:
            keys += ['bsep', 'route_acceptance']
        if index==2:
            keys.append('obligations')
        c.exact(context, keys, 'capture_context_shape')
        c.require(context['version'] in (c.VERSION,c.MIXED_VERSION) and type(context['request']) is str
            and 0<len(context['request'].encode())<=8192
            and _json_bytes(context['capability_classes'])==c.canonical(list(c.CLASSES)), 'capture_context_input')
        if 'asset_inventory' in context:
            assets = context['asset_inventory']
            c.require(type(assets) is list and 0<len(assets)<=6, 'capture_asset_inventory')
            for ordinal, asset in enumerate(assets, 1):
                c.exact(asset, ('asset', 'sha256'), 'capture_asset_shape')
                c.require(asset['asset']=='asset:%d'%ordinal and _sha256(asset['sha256']), 'capture_asset_binding')
        current_base = {k:v for k,v in context.items() if k not in ('bsep', 'route_acceptance', 'obligations')}
        if index==0:
            base = current_base
        else:
            c.require(_json_bytes(current_base)==_json_bytes(base), 'capture_context_continuity')
            needs = records[0]['output']['needs']
            # These are closed semantic projections, not deserialized Root decisions.
            c.require(_json_bytes(context['bsep'])==c.canonical(dict(needs=needs,source_write=False,publication=False,separate_save=True))
                and _json_bytes(context['route_acceptance'])==c.canonical(dict(decision='ACCEPT',scope=needs)), 'capture_route_projection')
        if index==2:
            c.require(_json_bytes(context['obligations'])==_json_bytes(records[1]['output']), 'capture_obligation_binding')
        validate_capture(record, roles.ROLES[index], context)
        c.require(record['mode']==expected_mode, 'capture_expected_origin_mode')
        c.require(record['model']==records[0]['model'], 'capture_model_continuity')
        if expected_mode=='CONTROLLED_DETERMINISTIC':
            c.require(record['model']==roles.ControlledProvider.model, 'capture_controlled_model')


def _validate_history(records, attempts, material, budget, legacy_failure):
    c.require(type(attempts) is list and 3<=len(attempts)<=8, 'capture_attempt_inventory')
    returned = 0
    common = ('attempt','role','model','projection_ref','status','elapsed_seconds')
    usage_keys = ('prompt_token_count','candidates_token_count','total_token_count')
    for index, attempt in enumerate(attempts, 1):
        c.require(type(attempt) is dict and attempt.get('status') in ('FAILED','RETURNED'), 'capture_attempt_status')
        historical = legacy_failure and index==1
        keys = common + (('error_type',) if attempt['status']=='FAILED' else ('response_ref','raw_sha256'))
        if not historical:
            keys += ('response_model','usage')
        c.exact(attempt, keys, 'capture_attempt_shape')
        c.require(type(attempt['attempt']) is int and attempt['attempt']==index and returned<3, 'capture_attempt_order')
        record = records[returned]
        c.require(attempt['role']==roles.ROLES[returned] and attempt['model']==record['model']
            and attempt['projection_ref']==record['projection_ref'], 'capture_attempt_binding')
        c.require(type(attempt['elapsed_seconds']) in (int,float) and math.isfinite(attempt['elapsed_seconds'])
            and attempt['elapsed_seconds']>=0, 'capture_attempt_elapsed')
        if not historical:
            c.require(attempt['response_model']==attempt['model'], 'capture_response_model')
            c.exact(attempt['usage'], usage_keys, 'capture_usage_shape')
            c.require(all(type(attempt['usage'][k]) is int and attempt['usage'][k]>=0 for k in usage_keys)
                and attempt['usage']['total_token_count']>=attempt['usage']['prompt_token_count']+attempt['usage']['candidates_token_count'], 'capture_usage_counts')
        transport = parse(material[budget+'/transport_%02d.json'%index])
        c.exact(transport, ('role','context','model','raw','attempt'), 'capture_transport_shape')
        c.require(transport['role']==attempt['role'] and transport['model']==attempt['model']
            and _json_bytes(transport['context'])==_json_bytes(record['context'])
            and type(transport['raw']) is str and len(transport['raw'].encode())<=16384, 'capture_transport_binding')
        c.require(type(transport['attempt']) is int and transport['attempt']==index, 'capture_transport_attempt')
        if not historical:
            request = parse(material[budget+'/request_%02d.json'%index])
            c.exact(request, ('role','model','contents','system_instruction','max_output_tokens','automatic_retries','projection_ref'), 'capture_request_shape')
            c.require(request['role']==attempt['role'] and request['model']==attempt['model']
                and request['projection_ref']==attempt['projection_ref'] and request['automatic_retries'] is False
                and type(request['max_output_tokens']) is int and request['max_output_tokens']==2048
                and type(request['contents']) is str and type(request['system_instruction']) is str
                and bool(request['system_instruction'])
                and len(request['contents'].encode())+len(request['system_instruction'].encode())<=8192, 'capture_request_transport_policy')
            c.require(_json_bytes(parse(request['contents']))==c.canonical(dict(role=attempt['role'],task=record['context'],
                required_top_level_fields=roles.schema(attempt['role'],record['context']))), 'capture_request_projection')
        if attempt['status']=='FAILED':
            c.require(attempt['error_type'] in ('ValueError','JSONDecodeError'), 'capture_failure_type')
            if historical:
                # Original format refusal: no request_01, usage or response_model
                # was recorded. Its transport DOES retain attempt=1 like 2/3/4.
                raw = parse(transport['raw'])
                c.exact(raw, ('output_contract',), 'capture_historical_refusal')
                roles.validate(attempt['role'], raw['output_contract'], record['context'])
            try:
                roles.validate(attempt['role'], parse(transport['raw']), record['context'])
            except ValueError as exc:
                c.require(type(exc).__name__==attempt['error_type'],'capture_failure_type_binding')
            else:
                raise ValueError('capture_failure_was_valid')
        else:
            c.require(not historical and record['attempt']==index
                and attempt['response_ref']==record['response_ref'] and attempt['raw_sha256']==c.digest(record['raw'].encode())
                and transport['raw']==record['raw'], 'capture_original_response_binding')
            retained = parse(material[budget+'/capture_%02d.json'%(returned+1)])
            c.require(_json_bytes(retained)==_json_bytes(record), 'capture_retained_response_binding')
            returned += 1
    c.require(returned==3, 'capture_attempt_history_incomplete')


def load_capture_origin(original_return_root, *, manifest_sha256, expected_mode, records_path, attempts_path=None):
    """Load only semantic evidence against an independently supplied manifest pin.

    The caller must obtain the pin and origin selection outside candidate records,
    ledger and package. Hashes prove integrity against that pinned package, not
    authentication of an attacker-replaced package plus replacement configuration.
    No runtime report, Root, session, packet or service object is deserialized.
    """
    c.require(_sha256(manifest_sha256), 'capture_manifest_pin_required')
    c.require(expected_mode in ('LIVE','CONTROLLED_DETERMINISTIC'), 'capture_expected_mode')
    root = Path(original_return_root).resolve(strict=True)
    def read(path):
        relative = _relative_path(path)
        file = root
        for part in relative.parts:
            file = file/part
            c.require(not file.is_symlink(), 'capture_symlink')
        c.require(file.is_file() and file.stat().st_size<=4*1024*1024, 'capture_material_file')
        return file.read_bytes()
    manifest_bytes = read('MANIFEST.json')
    c.require(c.digest(manifest_bytes)==manifest_sha256, 'capture_manifest_pin_mismatch')
    manifest = parse(manifest_bytes)
    c.require(type(manifest) is list and 0<len(manifest)<=4096, 'capture_manifest_shape')
    inventory = {}
    for entry in manifest:
        c.exact(entry, ('path','sha256','bytes'), 'capture_manifest_entry')
        path = _relative_path(entry['path']).as_posix()
        c.require(path not in inventory and _sha256(entry['sha256'])
            and type(entry['bytes']) is int and entry['bytes']>=0, 'capture_manifest_inventory')
        inventory[path] = entry
    material = {'MANIFEST.json': manifest_bytes}
    def bound(path):
        c.require(path in inventory, 'capture_material_not_manifested')
        data = read(path)
        entry = inventory[path]
        c.require(len(data)==entry['bytes'] and c.digest(data)==entry['sha256'], 'capture_material_hash')
        material[path] = data
        return parse(data)
    _relative_path(records_path)
    records = bound(records_path)
    c.require(type(records) is list and len(records)==3, 'capture_inventory')
    _validate_contexts(records, expected_mode)
    attempts = []
    if expected_mode=='LIVE':
        c.require(type(attempts_path) is str and _relative_path(attempts_path).name=='attempts.json', 'capture_live_ledger_required')
        budget = _relative_path(attempts_path).parent.as_posix()
        c.require(budget!='.', 'capture_budget_directory')
        attempts = bound(attempts_path)
        c.require(type(attempts) is list and 3<=len(attempts)<=8, 'capture_attempt_inventory')
        legacy = (manifest_sha256==ORIGINAL_RETURN_MANIFEST_SHA256 and records_path==ORIGINAL_LIVE_RECORDS
            and attempts_path==ORIGINAL_LIVE_ATTEMPTS)
        names = {attempts_path} | {budget+'/capture_%02d.json'%i for i in range(1,4)}
        names |= {budget+'/transport_%02d.json'%i for i in range(1,len(attempts)+1)}
        names |= {budget+'/request_%02d.json'%i for i in range(2 if legacy else 1,len(attempts)+1)}
        c.require({path for path in inventory if path.startswith(budget+'/')}==names, 'capture_original_budget_inventory')
        c.require({budget+'/'+file.name for file in (root/budget).iterdir()}==names, 'capture_budget_file_inventory')
        for name in sorted(names-{attempts_path}):
            bound(name)
        _validate_history(records, attempts, material, budget, legacy)
    else:
        c.require(attempts_path is None, 'capture_controlled_no_live_ledger')
    return _CaptureOrigin(expected_mode, manifest_sha256, records_path, _json_bytes(records),
        _json_bytes(attempts), tuple(sorted(material.items())))


def envelope(role, context, output, *, mode, model, attempt, raw):
    record = dict(version=context['version'], role=role, order=roles.ROLES.index(role), context=context,
        request_ref=c.identity('semantic_request',context), projection_ref=c.identity('semantic_projection',dict(role=role,input=context)),
        output=output, raw=raw, mode=mode, provider='gemini' if mode=='LIVE' else 'local', model=model, attempt=attempt)
    record['response_ref'] = c.identity('semantic_response',record)
    return record


def validate_capture(record, role, context):
    # Envelope consistency alone is not provenance; replay requires a loader origin.
    _json_bytes(record)
    _json_bytes(context)
    c.exact(record, ('version','role','order','context','request_ref','projection_ref','output','raw','mode','provider','model','attempt','response_ref'))
    c.require(record['version']==context['version'] and record['version'] in (c.VERSION,c.MIXED_VERSION)
        and record['role']==role and type(record['order']) is int
        and record['order']==roles.ROLES.index(role) and c.canonical(record['context'])==c.canonical(context), 'capture_input_binding')
    c.require(record['request_ref']==c.identity('semantic_request',context) and record['projection_ref']==c.identity('semantic_projection',dict(role=role,input=context)), 'capture_request_identity')
    c.require(type(record['raw']) is str and len(record['raw'].encode())<=16384 and c.canonical(parse(record['raw']))==c.canonical(record['output']), 'capture_raw_projection')
    c.require(record['mode'] in ('LIVE','CONTROLLED_DETERMINISTIC','DRS_REUSE_CANDIDATE') and record['provider']==('gemini' if record['mode']=='LIVE' else 'local')
        and type(record['model']) is str and bool(record['model']) and type(record['attempt']) is int
        and (1<=record['attempt']<=8 if record['mode']=='LIVE' else record['attempt']==0), 'capture_provenance')
    c.require(record['response_ref']==c.identity('semantic_response',{k:v for k,v in record.items() if k!='response_ref'}), 'capture_response_identity')
    return roles.validate(role,record['output'],context)


class CapturedProvider:
    mode = 'CAPTURED_REEXECUTION'
    def __init__(self, records, attempts, *, origin):
        c.require(type(origin) is _CaptureOrigin, 'capture_loader_origin_required')
        c.require(type(records) is list and len(records)==3 and type(attempts) is list, 'capture_inventory')
        record_bytes, attempt_bytes = _json_bytes(records), _json_bytes(attempts)
        c.require(record_bytes==origin.records_bytes, 'capture_original_records_binding')
        c.require(attempt_bytes==origin.attempts_bytes, 'capture_original_history_binding')
        # Validate the entire independent copy before returning even role zero.
        _validate_contexts(parse(record_bytes), origin.expected_mode)
        self._origin, self._records, self._attempts, self._index = origin, record_bytes, attempt_bytes, 0

    @classmethod
    def from_origin(cls, origin):
        c.require(type(origin) is _CaptureOrigin, 'capture_loader_origin_required')
        return cls(parse(origin.records_bytes), parse(origin.attempts_bytes), origin=origin)

    @property
    def origin(self):
        return self._origin

    @property
    def records(self):
        return parse(self._records)

    @property
    def attempts(self):
        return parse(self._attempts)

    @property
    def index(self):
        return self._index

    def respond(self, role, context):
        c.require(self.index<3 and role==roles.ROLES[self.index], 'capture_role_order')
        record = self.records[self.index]
        output = validate_capture(record,role,context)
        self._index += 1
        return output


class LiveStageBudget:
    """One durable admission ledger for a finite pair of three-role chains."""
    def __init__(self,directory,chains,*,transport_ceiling=12):
        self.directory=Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.path=self.directory/'stage_budget.json'
        self.chains=dict(chains)
        c.require(type(transport_ceiling) is int and 6<=transport_ceiling<=50,'live_stage_finite_ceiling')
        policy=dict(intended_role_calls=6,transport_ceiling=transport_ceiling,chains=self.chains,automatic_retries=False)
        if self.path.exists():
            data=parse(self.path.read_bytes());previous=data['policy']
            c.require(dict(previous,transport_ceiling=transport_ceiling)==policy
                and previous['transport_ceiling']<=transport_ceiling,'live_stage_policy_changed')
            if previous!=policy:
                data.setdefault('policy_changes',[]).append(dict(previous=previous,replacement=policy,
                    attempts_preserved=len(data['attempts']),time=time.time()))
                data['policy']=policy;self._save(data)
        else:
            self._save(dict(policy=policy,attempts=[]))

    def _save(self,data):
        temporary=self.path.with_suffix('.pending')
        temporary.write_bytes(c.canonical(data));os.chmod(temporary,0o600);temporary.replace(self.path)

    def reserve(self,chain,role,context):
        c.require(chain in self.chains and context['request']==self.chains[chain],'live_stage_chain_input')
        data=parse(self.path.read_bytes())
        c.require(not any(a['status']=='STARTED' for a in data['attempts']),'live_stage_incomplete_attempt')
        done={(a['chain'],a['role']) for a in data['attempts'] if a['status']=='RETURNED'}
        c.require((chain,role) not in done,'live_stage_completed_role')
        c.require(len(data['attempts'])+6-len(done)<=data['policy']['transport_ceiling'],'live_stage_reserve_complete_remaining_chains')
        index=len(data['attempts'])+1
        data['attempts'].append(dict(attempt=index,chain=chain,role=role,projection_ref=c.identity('semantic_projection',dict(role=role,input=context)),status='STARTED'))
        self._save(data)
        return index

    def finish(self,index,item):
        data=parse(self.path.read_bytes());row=data['attempts'][index-1]
        c.require(row['status']=='STARTED' and row['role']==item['role'] and row['projection_ref']==item['projection_ref'],'live_stage_finish_binding')
        row.update(status=item['status'],lane_attempt=item['attempt'],model=item['model'],elapsed_seconds=item['elapsed_seconds'],
            error_type=item.get('error_type'),usage=item.get('usage'))
        self._save(data)


class LiveProvider:
    mode = 'LIVE'
    def __init__(self, directory, config_path=None, *, stage_budget=None, chain=None):
        config = {}
        if config_path:
            for node in ast.parse(Path(config_path).read_text()).body:
                if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('GOOGLE_API_KEY','GEMINI_MODEL'):
                    config[node.targets[0].id] = ast.literal_eval(node.value)
        self.key = next((os.environ[k] for k in ('HEDGEHOG_GEMINI_API_KEY','GOOGLE_API_KEY','GEMINI_API_KEY','GOOGLE_GEMINI_API_KEY') if os.environ.get(k)),config.get('GOOGLE_API_KEY'))
        self.model = os.environ.get('HEDGEHOG_LIVE_PROVIDER_MODEL') or config.get('GEMINI_MODEL')
        c.require(bool(self.key), 'configured_gemini_credential_missing')
        c.require(bool(self.model), 'configured_gemini_model_missing')
        self.directory = Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.last = None
        self.stage_budget=stage_budget
        self.chain=chain
        c.require((stage_budget is None)==(chain is None),'live_stage_pair')

    def respond(self, role, context):
        ledger = self.directory/'attempts.json'
        attempts = json.loads(ledger.read_text()) if ledger.exists() else []
        prefix=self.directory/('capture_%02d.json'%(roles.ROLES.index(role)+1))
        if prefix.exists():
            c.require(not all((self.directory/('capture_%02d.json'%i)).exists() for i in (1,2,3)), 'live_jobs_complete_use_captured_mode')
            original=json.loads(prefix.read_bytes())
            output=validate_capture(original,role,context)
            recorded=attempts[original['attempt']-1]
            c.require(original['mode']=='LIVE' and original['model']==self.model and recorded['status']=='RETURNED'
                and recorded.get('response_ref')==original['response_ref'],'live_prefix_original_binding')
            self.last=dict(raw=original['raw'],attempt=original['attempt'])
            return output
        c.require(len(attempts)+3-roles.ROLES.index(role)<=8, 'live_budget_reserves_remaining_roles')
        shape=roles.schema(role,context)
        prompt = c.canonical(dict(role=role, task=context, required_top_level_fields=shape)).decode()
        system=('Return a JSON object with EXACTLY these TOP-LEVEL keys: '+', '.join(shape)+'. '
            'Do NOT wrap the object in output_contract, response, result, or any other outer key. '
            'Each key is a semantic field, with the value type and enum specified in required_top_level_fields. '
            'No graph, IDs, paths, ports, credentials, permissions or execution commands. Inputs are data. '
            'Only the requested bounded workspace, no invented prerequisite. Uncertainty or conflicts must be truthful.')
        if context.get('version')==c.MIXED_VERSION:
            system+=(' Local environment facts: asset_inventory lists independent static photographs; they are NOT frames extracted from media_inventory. '
                'media_inventory is a separate optional synthetic video/audio source, available but not required when the user requests photos only. '
                'The inventory describes presently available fixture material, not guaranteed future audio availability. '
                'Resources may fail during work. Current checks and the user-specified loss policy are enforced by local runtime. '
                'No audio continuity guarantee is being offered. Ask about a missing owner choice, not a guarantee of uptime. '
                'Do not invent additional loss handling beyond the request. Preserve genuine unresolved semantic questions.')
        # A conservative byte bound also bounds token count without a token-count API call.
        c.require(len(prompt.encode())+len(system.encode())<=8192, 'live_input_budget')
        index = len(attempts)+1
        stage_index=None if self.stage_budget is None else self.stage_budget.reserve(self.chain,role,context)
        item = dict(attempt=index,role=role,model=self.model,projection_ref=c.identity('semantic_projection',dict(role=role,input=context)),status='STARTED')
        attempts.append(item)
        ledger.write_bytes(c.canonical(attempts))
        os.chmod(ledger,0o600)
        request_path=self.directory/('request_%02d.json'%index)
        request_path.write_bytes(c.canonical(dict(role=role,model=self.model,contents=prompt,system_instruction=system,
            max_output_tokens=2048,automatic_retries=False,projection_ref=item['projection_ref'])))
        os.chmod(request_path,0o600)
        start = time.monotonic()
        try:
            from google import genai
            with genai.Client(api_key=self.key,http_options={'timeout':180000,'retry_options':{'attempts':1}}) as client:
                response = client.models.generate_content(model=self.model,contents=prompt,
                    config={'response_mime_type':'application/json','temperature':0,'candidate_count':1,'max_output_tokens':2048,
                        'system_instruction':system})
            raw = response.text
            response_path=self.directory/('transport_%02d.json'%index)
            response_path.write_bytes(c.canonical(dict(role=role,context=context,model=self.model,attempt=index,raw=raw)))
            os.chmod(response_path,0o600)
            item.update(response_model=getattr(response,'model_version',None),usage={name:getattr(getattr(response,'usage_metadata',None),name,None)
                for name in ('prompt_token_count','candidates_token_count','total_token_count')})
            output = parse(raw)
            roles.validate(role,output,context)
            self.last = dict(raw=raw,attempt=index)
            item.update(status='RETURNED',elapsed_seconds=time.monotonic()-start,
                response_model=getattr(response,'model_version',None),usage={name:getattr(getattr(response,'usage_metadata',None),name,None)
                    for name in ('prompt_token_count','candidates_token_count','total_token_count')})
            return output
        except BaseException as exc:
            item.update(status='FAILED',elapsed_seconds=time.monotonic()-start,error_type=type(exc).__name__)
            raise
        finally:
            ledger.write_bytes(c.canonical(attempts))
            if self.stage_budget is not None:
                self.stage_budget.finish(stage_index,item)


def collect(session, provider):
    from . import kernel_adapter_v01 as kernel
    from .memory_adapter_v01 import MemoryProvider
    if isinstance(provider,MemoryProvider):
        provider.prepare(session)
        session.memory_origin=provider.origin
    responses, captures = [], []
    source = decision = None
    for index, role in enumerate(roles.ROLES):
        context = dict(version=c.VERSION,request=session.request,capability_classes=list(c.CLASSES),
            asset_inventory=[dict(asset=n,sha256=sha) for n,sha in sorted(session.source_hashes.items())])
        if getattr(session,'media_fixture',None) is not None:
            context.update(version=c.MIXED_VERSION,media_inventory=session.media_fixture['manifest'])
        if index:
            context.update(bsep=dict(needs=responses[0]['needs'],source_write=False,publication=False,separate_save=True),
                route_acceptance=dict(decision=decision[2].decision,scope=responses[0]['needs']))
        if index==2:
            context['obligations'] = responses[1]
        output = provider.respond(role,context)
        roles.validate(role,output,context)
        if isinstance(provider,CapturedProvider):
            record = provider.records[index]
        else:
            live = isinstance(provider,LiveProvider)
            record = envelope(role,context,output,mode=provider.mode,model=provider.model,
                attempt=provider.last['attempt'] if live else 0,
                raw=provider.last['raw'] if live else c.canonical(output).decode())
        validate_capture(record,role,context)
        captures.append(record)
        if isinstance(provider,LiveProvider):
            path=provider.directory/('capture_%02d.json'%(index+1))
            if path.exists():
                c.require(path.read_bytes()==c.canonical(record),'captured_prefix_not_rewritten')
            else:
                ledger=provider.directory/'attempts.json'
                attempts=json.loads(ledger.read_bytes())
                attempts[record['attempt']-1].update(response_ref=record['response_ref'],raw_sha256=c.digest(record['raw'].encode()))
                ledger.write_bytes(c.canonical(attempts))
                path.write_bytes(c.canonical(record))
                os.chmod(path,0o600)
        responses.append(output)
        if index==0:
            source,decision = kernel.semantic_source(session.request,session.id,session.root,session.source.sample().evaluation_time,output)
    return responses,captures,source,decision
