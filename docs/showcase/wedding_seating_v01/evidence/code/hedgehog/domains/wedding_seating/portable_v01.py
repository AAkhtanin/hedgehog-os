"""Externally pinned, read-only Wedding evidence at recorded event times.

Only installed code is imported. Archived code is inert source evidence. This
finite relationship reader is neither native graph replay nor provider attestation.
"""
from dataclasses import replace
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil

VERSION = 'WeddingPortableEvidenceV01'
LIMIT = 64 * 1024 * 1024


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, 'duplicate_json_key')
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))


def regular(path):
    path = Path(path)
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink_refused')
    require(path.is_file() and path.stat().st_size <= LIMIT, 'missing_or_oversize_file')
    return path.read_bytes()


def _relative(name):
    require(type(name) is str and name and '\\' not in name, 'unsafe_member')
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')), 'unsafe_member')
    return name


def load_pinned_directory_v01(root, expected_sha256, *, portable=True):
    """The independent expected identity is mandatory and checked before JSON."""
    require(type(expected_sha256) is str and re.fullmatch('[0-9a-f]{64}', expected_sha256), 'external_pin_required')
    root = Path(root)
    body = regular(root/'MANIFEST.json')
    require(sha(body) == expected_sha256, 'external_pin_mismatch')
    manifest = strict(body)
    require(type(manifest) is dict and type(manifest.get('files')) is list, 'manifest_shape')
    if portable:
        require(set(manifest) == {'version', 'files'} and manifest['version'] == VERSION, 'manifest_version')
    files = {}
    folded = set()
    for item in manifest['files']:
        require(set(item) == {'path', 'bytes', 'sha256', 'mode'}, 'manifest_row_shape')
        name = _relative(item['path'])
        require(name != 'MANIFEST.json' and name.casefold() not in folded, 'duplicate_member')
        folded.add(name.casefold())
        raw = regular(root/name)
        require(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'member_identity:'+name)
        require(item['mode'] in ('0400', '0600', '0644', '0755') and format((root/name).stat().st_mode & 0o7777, '04o') == item['mode'], 'member_mode:'+name)
        files[name] = raw
    actual = set()
    for p in root.rglob('*'):
        require(not p.is_symlink(), 'symlink_refused')
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
    require(actual == set(files) | {'MANIFEST.json'}, 'unmanifested_or_missing_member')
    return files


def _write_package(target, files, modes):
    target = Path(target)
    require(not target.exists() and not any(p.is_symlink() for p in target.parents), 'new_output_directory_required')
    target.mkdir(parents=True)
    rows = []
    for name, raw in sorted(files.items()):
        p = target/_relative(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f:
            f.write(raw)
        mode = modes.get(name, '0644')
        p.chmod(int(mode, 8))
        rows.append(dict(path=name, bytes=len(raw), sha256=sha(raw), mode=mode))
    body = canonical(dict(version=VERSION, files=rows))
    (target/'MANIFEST.json').write_bytes(body)
    return sha(body)


def export_v01(source, expected_source_sha256, semantics, expected_semantics_sha256, target):
    """Export exact saved data plus an explicit derived source-location map."""
    w4 = load_pinned_directory_v01(source, expected_source_sha256, portable=False)
    w3 = load_pinned_directory_v01(semantics, expected_semantics_sha256)
    files, modes, mapping = {}, {}, []
    for origin, values, prefix, pin in ((Path(source), w4, 'w4/', expected_source_sha256), (Path(semantics), w3, 'w3/', expected_semantics_sha256)):
        for name, raw in values.items():
            selected = name.startswith('snapshot/') if prefix == 'w4/' else name.startswith('story/')
            if not selected:
                continue
            destination = prefix + (name.removeprefix('snapshot/') if prefix == 'w4/' else name)
            files[destination] = raw
            modes[destination] = format((origin/name).stat().st_mode & 0o7777, '04o')
            mapping.append(dict(path=destination, source_member=name, source_manifest_sha256=pin, sha256=sha(raw), transformation='EXACT_BYTES_RELOCATED'))
    source_map = dict(version=VERSION, classification='DERIVED_LOCATION_PROJECTION_ORIGINAL_BYTES_PRESERVED',
        w4_manifest_sha256=expected_source_sha256, w3_manifest_sha256=expected_semantics_sha256,
        synthetic=True, no_provider_attestation=True, files=sorted(mapping, key=lambda r:r['path']))
    files['source_map.json'] = canonical(source_map)
    # Validate before producing an exported package; no collection on omissions.
    verify_material_v01(files)
    return dict(status='EXPORTED', expected_manifest_sha256=_write_package(target, files, modes),
                independent_review='PIN_MUST_BE_SUPPLIED_OUTSIDE_PACKAGE', new_external_calls=0)


def _json(files, path):
    require(path in files, 'incomplete_evidence:'+path)
    return strict(files[path])


def _root_record(run, prefix, value):
    from . import native_contracts_v01 as c
    result, incoming = run['root_result'], run['root_input']
    require(result['decision'] == 'ACCEPT' and result['selected_candidate_id'] == c.identity(prefix, value), 'recorded_root_candidate')
    require(result['decision_input_id'] == incoming['decision_input_id'], 'recorded_root_input')
    require(result['target_root_id'] == incoming['target_root_id'] and result['transaction_id'] == incoming['transaction_id'], 'recorded_root_scope')
    require(not result['permission_created'] and not result['effect_requested'], 'recorded_root_nonpermission')


def _work_chain(run, material, output, names, sample_report=None):
    from . import native_contracts_v01 as c, math_v01 as maths
    require(run['material'] == material and run['output'] == output, 'performed_material_output')
    require(run['semantic_proposal']['payload'] == material, 'performed_semantic_payload')
    items, results = run['program']['candidate']['items'], run['results']
    require([r['work_id'] for r in results] == [i['work_id'] for i in items] == names, 'performed_work_set')
    previous = material
    for i, (item, result) in enumerate(zip(items, results)):
        require(result['status'] == 'COMPLETED', 'performed_work_status')
        require(strict(result['invocation']['inputs'][0]['value']) == previous, 'performed_parent_value')
        if i:
            require(item['inputs'][0]['source'] == dict(predecessor_work_id=names[i-1], output_field='material', expected_type='TEXT'), 'performed_parent_binding')
            require(bool(result['consumed_fields']), 'performed_consumption_missing')
        actual = strict(result['result']['output'][0]['value'])
        if names[i] == 'review':
            expected = dict(previous, requirements_checked=c.problem_from_material(material).content_id, contradiction=[])
        elif names[i] == 'compile':
            expected = dict(previous, optimization=maths.compile_optimization_v01(c.problem_from_material(material),material['profile']).to_plain_v01())
        elif names[i] == 'qpu_prepare':
            expected = dict(previous, safe_output=output)
        elif names[i] == 'qpu_validate':
            expected = dict(previous, sample_validation=sample_report)
        else:
            require(names[i] == 'qpu_consume' and sample_report is not None, 'supported_work_kind')
            expected = dict(previous, safe_output=output, assignment=output['assignment'], validation=sample_report['selected']['validation'])
        require(actual == expected, 'performed_intermediate_output:'+names[i])
        previous = actual
    require(previous['safe_output'] == output, 'performed_final_output')
    _root_record(run, 'wedding_result', output)
    require(run['root_input']['target_root_id'] == material['problem']['owner_root_id'] and
            run['root_input']['transaction_id'] == 'transaction:'+material['request_ref'], 'performed_root_scope')
    require(run['owner']['request_ref'] == material['request_ref'] and run['owner']['problem'] == material['problem'] and run['owner']['profile'] == material['profile'], 'performed_owner')
    return previous


def _semantic_story(files, original):
    from . import semantic_adapter_v01 as s, native_contracts_v01 as c, supplied_v01 as supplied, math_v01 as maths
    results, runs = {}, {}
    for key in ('A', 'B', 'VERIFY', 'AMBIGUOUS', 'SR1', 'SR2', 'SR3'):
        x = _json(files, f'w3/story/{key}_intake.json')
        records = _json(files, f'w3/story/{key}_captures.json')
        actual = _json(files, f'w3/story/{key}.json')
        candidates = [c.canonical(x['current'])]
        if x['current'] == strict(original):
            candidates.append(original)
        current = next((v for v in candidates if c.digest(v) == records[0]['source_snapshot']), None)
        require(current is not None, 'semantic_source_snapshot')
        i = s.LiveIntakeV01(original, current, x['request_ref'], x['safe_intent'], tuple(x['permitted_tasks']),
            tuple(x['permitted_profiles']), x['structural_disclosure'], tuple(x['amendment_guests']), (),
            None if x['prior_output'] is None else c.canonical(x['prior_output']), x['prior_result_ref'])
        owner, expected = s.accepted_material_v01(i, records, origin=actual['material']['origin'])
        if expected['revision_acknowledgement']:
            decision = actual['material']['revision_root']
            require(decision['decision'] == 'ACCEPT' and decision['selected_candidate_id'] == c.identity('revision', expected['revision_acknowledgement']), 'semantic_revision_review')
            expected['revision_root'] = decision
        if owner.task_kind == 'VALIDATE_EXISTING':
            prior = next((v for v in runs.values() if v['artifact']['artifact_id'] == i.prior_result_ref), None)
            require(prior is not None and i.prior_output_bytes == c.canonical(prior['output']) and prior['material']['problem'] == actual['material']['problem'], 'semantic_prior_result')
            expected.update(assignment=prior['output']['assignment'], existing_result_ref=i.prior_result_ref)
        require(expected == actual['material'], 'semantic_to_performed_material:'+key)
        if owner.task_kind == 'CLARIFY':
            require(actual['status'] == 'NEEDS_CLARIFICATION' and expected['profile'] is None, 'semantic_clarification')
            results[key] = dict(status='NEEDS_CLARIFICATION', profile=None, questions=actual['questions'])
            continue
        supplied.validate_saved_run_v01(actual, owner=owner)
        require(actual['semantic_proposal']['payload'] == expected, 'semantic_proposal_binding')
        require(records[0]['capture_ref'] in c.canonical(actual['source_context']).decode(), 'semantic_BSEP_binding')
        runs[key] = actual
        results[key] = dict(status='PASS', output=actual['output'], captures=[r['capture_ref'] for r in records])
    require(maths.validate_assignment_v01(s._problem(c.canonical(runs['SR2']['owner']['problem'])), runs['SR1']['output']['assignment'], runs['SR2']['owner']['profile']).to_plain_v01()['status'] != 'VALID', 'revision_old_plan_not_invalidated')
    return results


def verify_material_v01(files):
    """Finite saved relations. Does not deserialize Host or execute native Work."""
    from . import native_contracts_v01 as c, qpu_contracts_v01 as q, qpu_application_v01 as app
    from . import qpu_bridge_v01 as bridge, qpu_output_v01 as display
    mapping = _json(files, 'source_map.json')
    require(mapping['version'] == VERSION and mapping['synthetic'] is True, 'source_map_version')
    require({r['path'] for r in mapping['files']} == set(files)-{'source_map.json'}, 'source_map_coverage')
    for item in mapping['files']:
        require(item['transformation'] == 'EXACT_BYTES_RELOCATED' and sha(files[item['path']]) == item['sha256'], 'source_map_identity')
    installed = Path(__file__).resolve().parents[3]
    for path, raw in files.items():
        if path.startswith('w4/candidate/hedgehog/') and path.endswith('.py'):
            require(regular(installed/path.removeprefix('w4/candidate/')) == raw, 'installed_source_identity:'+path)
    original = files['w4/candidate/fixtures/wedding_seating/reference_problem_v01.json']
    require(regular(installed/'fixtures/wedding_seating/reference_problem_v01.json') == original, 'installed_original_fixture')
    story = _semantic_story(files, original)
    scope = _json(files, 'w4/operator_scope.json')
    ledger = _json(files, 'w4/provider/ledger.json')
    require(len(ledger['attempts']) == 2 and {r['profile'] for r in ledger['attempts']} == set(q.PROFILES), 'hardware_profile_inventory')
    require(len({r['client_token'] for r in ledger['attempts']}) == 2 and sum(r['reserved_microusd'] for r in ledger['attempts']) <= 1450000, 'hardware_task_allowance')
    rows = []
    for row in ledger['attempts']:
        profile = row['profile']; key = 'A' if profile == q.PROFILES[0] else 'B'
        original_prep = _json(files, f'w4/native/{profile}/prepare.json')
        intake = _json(files, f'w4/basis_w3/story/{key}_intake.json')
        captures = _json(files, f'w4/basis_w3/story/{key}_captures.json')
        require(intake == _json(files, f'w3/story/{key}_intake.json') and captures == _json(files, f'w3/story/{key}_captures.json'), 'hardware_semantic_story_binding')
        _, material = app.preparation_material_v01(intake, captures, files[f'w4/basis_w1/captures/{profile}/grid.json'],
            request_ref=original_prep['material']['request_ref'], original_bytes=original)
        numeric = _json(files, f'w4/numeric/{profile}/numeric.json')
        q.check_numeric_v01(material, numeric)
        bridge.check_request_v01(row['request'], scope=scope, material=material, numeric=numeric, token=row['client_token'])
        require(c.digest(row['request']) == row['request_sha256'], 'hardware_request_hash')
        require(strict(row['actual_wire']) == row['request'] and c.digest(row['actual_wire'].encode()) == row['actual_wire_sha256'], 'hardware_actual_wire')
        _work_chain(original_prep, material, numeric, ['review', 'compile', 'qpu_prepare'])
        approval = row['approval']; claim = dict(request=row['request'], scope=scope, expires=approval['expires'])
        require(approval['request_sha256'] == row['request_sha256'] and approval['scope'] == scope and approval['native_prepare_result_ref'] == original_prep['artifact']['artifact_id'], 'submission_preparation_binding')
        _root_record(approval, 'wedding_qpu_request', claim)
        require(approval['root_input']['target_root_id'] == material['problem']['owner_root_id'] and
                approval['root_input']['transaction_id'] == 'transaction:'+material['request_ref'], 'submission_root_scope')
        require(datetime.fromisoformat(row['submitting']).timestamp() < approval['expires'], 'submission_approval_time')
        meta = row['metadata']; raw_bytes = files['w4/provider/'+_relative(row['raw_path'])]; raw = strict(raw_bytes); tm = raw['taskMetadata']
        require(row['state'] == 'VALIDATED_AND_SAVED' and meta['status'] == tm['status'] == 'COMPLETED', 'hardware_completed_state')
        require(meta['quantumTaskArn'] == tm['id'] == row['task_arn'], 'hardware_task_binding')
        require(meta['deviceArn'] == tm['deviceId'] == row['request']['deviceArn'] == scope['device_arn'], 'hardware_device_binding')
        require(meta['shots'] == tm['shots'] == row['request']['shots'] == 1000 and row['network_attempts'] == 1, 'hardware_shot_attempt_binding')
        require(raw['additionalMetadata']['action'] == strict(row['request']['action']), 'hardware_returned_action')
        require(meta['outputS3Bucket'] == row['request']['outputS3Bucket'] == scope['bucket'] and row['result_key'] == meta['outputS3Directory']+'/results.json' and meta['outputS3Directory'].startswith(row['request']['outputS3KeyPrefix']), 'hardware_S3_binding')
        for field in ('createdAt', 'endedAt'):
            require(datetime.fromisoformat(meta[field].replace('Z','+00:00')) == datetime.fromisoformat(tm[field].replace('Z','+00:00')), 'hardware_metadata_time')
        require(c.digest(raw_bytes) == row['raw_sha256'], 'hardware_raw_identity')
        report = q.samples_v01(material, numeric, raw_bytes, task_arn=row['task_arn'], allow_suboptimal=scope['feasible_suboptimal_allowed'])
        require(report == _json(files, f'w4/provider/{profile}_sample_validation.json'), 'hardware_sample_lineage')
        require(report['selected'] is not None, 'hardware_no_feasible_sample')
        # Nonnegative pair objective plus a feasible zero witness justifies 0 for
        # this installed original fixture; no search or supplied oracle is used.
        require(report['selected']['validation']['components']['objective'] == 0 and report['local_reference_objective'] == report['objective_gap'] == 0, 'supported_zero_reference')
        resume_names = [p for p in files if p.startswith(f'w4/native/{profile}/resume_prepare_') and p.endswith('.json')]
        require(len(resume_names) == 1, 'resume_preparation_inventory')
        resumed = _json(files, resume_names[0])
        _work_chain(resumed, material, numeric, ['review', 'compile', 'qpu_prepare'])
        consumed = _json(files, f'w4/native/{profile}/consume.json'); cm = consumed['material']
        require(cm['prepare_material'] == material and cm['numeric_parent'] == numeric and cm['prepare_output_sha256'] == c.digest(numeric), 'consumed_preparation_material')
        require(cm['prepare_result_ref'] == resumed['artifact']['artifact_id'] == consumed['owner']['parent_ref'] and cm['prepare_result_ref'] != original_prep['artifact']['artifact_id'], 'consumed_resume_parent')
        require(cm['submission_prepare_result_ref'] == original_prep['artifact']['artifact_id'] and cm['submission_request_sha256'] == row['request_sha256'] and cm['submission_metadata'] == meta, 'consumed_submission_parent')
        require(cm['raw_result'].encode() == raw_bytes and cm['task_arn'] == row['task_arn'] and cm['requested_shots'] == 1000, 'consumed_raw_input')
        expected, _ = q.consumed_v01(cm)
        _work_chain(consumed, cm, expected, ['qpu_validate', 'qpu_consume'], report)
        require(row['consumed_result_ref'] == consumed['artifact']['artifact_id'], 'consumed_artifact_binding')
        require(resumed['now'] <= consumed['now'] and datetime.fromisoformat(meta['endedAt'].replace('Z','+00:00')).timestamp() <= resumed['now'], 'consumption_recorded_time')
        folder = f'w4/outputs/{profile}/'
        require(files[folder+'seating.json'] == c.canonical(expected) and files[folder+'seating.html'] == display.render_v01(expected, material['problem']), 'saved_output_bytes')
        saves = _json(files, folder+'save_receipts.json')
        require(len(saves) == 2 and set(row['save_paths']) == {s['claim']['path'] for s in saves}, 'save_path_inventory')
        require({Path(s['claim']['path']).name for s in saves} == {'seating.json','seating.html'}, 'save_filename_inventory')
        for saved in saves:
            claim = saved['claim']; body = files[folder+Path(claim['path']).name]
            require(saved['status'] == 'SAVED_READBACK_VERIFIED' and claim['bytes'] == len(body) and claim['sha256'] == sha(body), 'save_exact_bytes')
            _root_record(saved, 'wedding_save', claim)
            incoming = saved['root_input']; post = dict(incoming['post_vv_bundle']['items']); temporal = dict(incoming['temporal_state']['items'])
            require(post['required_evidence_refs'] == post['provided_evidence_refs'] == [consumed['artifact']['artifact_id']], 'save_consumed_result_link')
            recorded = int(temporal['time_envelope_ref'].rsplit(':',1)[1])
            require(temporal['temporal_valid'] and not temporal['expired'] and temporal['not_before_satisfied'] and consumed['now'] <= recorded < claim['expires'], 'save_recorded_event_time')
            require(incoming['target_root_id'] == material['problem']['owner_root_id'] and incoming['transaction_id'] == 'transaction:'+cm['request_ref'], 'save_recorded_owner')
        rows.append(dict(profile=profile, task_arn=row['task_arn'], status='RECORDED_COMPLETED_CONSUMED_SAVED', raw_sha256=row['raw_sha256'],
            measurements=report['successful_shots'], valid=report['valid_samples'], invalid=report['invalid_samples'], distinct=report['distinct_valid_plans'],
            selected=expected, gap=report['objective_gap'], consumed_result_ref=row['consumed_result_ref'], save_claims=[s['claim'] for s in saves]))
    return dict(version=VERSION, status='PASS', classification='SAFE_DERIVED_SAVED_RELATIONSHIPS_AT_RECORDED_EVENT_TIMES',
        hardware=rows, semantics=story, unsupported=['FULL_NATIVE_SCHEMA_REPLAY','PROVIDER_CRYPTOGRAPHIC_ATTESTATION','CURRENT_PERMISSION','ARBITRARY_FIXTURES_OR_SUBOPTIMAL_REFERENCE'],
        operations=dict(network=0,models=0,qpu=0,Root=0,Host=0,D=0,Work=0,search=0,effects=0,DRS_writes=0))


def verify_v01(root, expected_sha256):
    try:
        return verify_material_v01(load_pinned_directory_v01(root, expected_sha256))
    except (KeyError, TypeError, IndexError, StopIteration, AttributeError) as exc:
        raise ValueError('incomplete_or_malformed_supported_evidence') from exc


def render_v01(root, expected_sha256, target):
    files = load_pinned_directory_v01(root, expected_sha256)
    verified = verify_material_v01(files)
    target = Path(target)
    require(not target.exists() and not any(p.is_symlink() for p in target.parents), 'new_output_directory_required')
    target.mkdir(parents=True)
    mapping = []
    for row in verified['hardware']:
        for suffix in ('json','html'):
            member=f"w4/outputs/{row['profile']}/seating.{suffix}"
            destination=target/row['profile']/f'seating.{suffix}'
            destination.parent.mkdir(exist_ok=True)
            destination.write_bytes(files[member])
            mapping.append(dict(source_member=member, output=destination.relative_to(target).as_posix(), sha256=sha(files[member]), transformation='EXACT_SAVED_BYTES_COPY_NOT_NEW_ROOT_SAVE'))
    (target/'render_mapping.json').write_bytes(canonical(dict(expected_manifest_sha256=expected_sha256, files=mapping)))
    return dict(status='RENDERED_VERIFIED_SAVED_BYTES', files=mapping, new_root_or_effect_calls=0)
