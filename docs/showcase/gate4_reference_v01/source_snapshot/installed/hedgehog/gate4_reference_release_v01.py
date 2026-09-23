"""One bounded G4 extension with retained parent evidence, never Gate closure."""
import ast
from copy import deepcopy
from dataclasses import fields
import hashlib
import json
from pathlib import Path

KEY='gate4_reference_release_v01'
PROFILE='G44_REFERENCE_RELEASE_V01'
REGISTRY_PATHS=('release/completion_manifest.json','release/integration_seam_index.json','release/current_schema_surface_v01.json')
HISTORICAL_JSON_PINS=dict(zip(REGISTRY_PATHS,(
    '9d11bb39ae962cef79bf6507b45eb865d3fa8a7015f8a51b3453534e9a775a7a',
    '5be4a6ebcdd51a57ccc1645f98146c947a8add3d635e19963cff69086ca3a47d',
    '828fb48df580c7801652e7b3700b073dea22e16e2008d812c3ccb1cbf30a88a6')))
SCHEMA='schemas/gate4_reference_v01.schema.json'
LOADER=dict(source_path='hedgehog/gate4_reference_contracts_v01.py',schema_paths=[SCHEMA],role='single_writer_and_contextual_reference_validation')
SYMBOLS=dict(
    producer='hedgehog.domains.airline.gate4_reference_adapter_v01:native_story_v42',
    verifier='hedgehog.gate4_reference_evidence_v01:verify_package_v01',
    living='demo.run_living_gauntlet_v01:validate_living_g44_v01',
    conformance='demo.run_kernel_conformance_v01:validate_kernel_conformance_g44_v01',
    collection_owner='hedgehog.gate4_reference_release_v01:collect_release_v01',
    supplied='hedgehog.gate4_reference_release_v01:validate_release_v01',
    schema_writer='hedgehog.gate4_reference_contracts_v01:reference_schema_v01')
TESTS=tuple('tests/test_gate4_reference_'+name+'_v01.py' for name in ('math','supplied','preflight','native','history','evidence','registration'))
SOURCE_PATHS=tuple(sorted(set(s.split(':')[0].replace('.','/')+'.py' for s in SYMBOLS.values())|set(TESTS)|{
    'hedgehog/gate4_reference_runtime_v01.py','hedgehog/domains/airline/gate4_reference_history_v01.py',
    'hedgehog/gate4_strategy_reference_v01.py','hedgehog/gate4_pressure_budget_v01.py',SCHEMA}))

def require(value,reason):
    if not value:raise ValueError('g44_release:'+reason)

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def digest(v):return hashlib.sha256(canonical(v)).hexdigest()
def read(p):
    from hedgehog.gate4_reference_evidence_v01 import read_json_v01
    return read_json_v01(p)
def identity(p):
    from hedgehog.gate4_reference_evidence_v01 import _body
    return _body(p)

def registration_v01(root):
    root=Path(root)
    return dict(profile=PROFILE,status='PROPOSED_PENDING_INDEPENDENT_REVIEW',symbols=SYMBOLS,
        tests=list(TESTS),schema=SCHEMA,sources={p:identity(root/p) for p in SOURCE_PATHS},
        evidence=['CP_STRATEGY','CP_BUDGET','ORIGINAL_SOURCE_BUDGET','ACTUAL_WORK_CONSUMPTION',
            'G3_RECORDING_DESCENT','INDEPENDENT_ROOTS_CONSENT_CURRENT_TIME','REFUSALS','SUPPORTED_SAVED_VERIFICATION'],
        ownership=dict(fresh_g4_owner='collect_release_v01',supplied_g4_collectors=0,legacy_collectors=0),
        historical_counts=dict(acts=12,seams=24,current_schemas=16,retired_schemas=2),
        combined_counts=dict(historical_acts_plus_reference_profiles=13,historical_seams_plus_reference_profiles=25,current_schemas=17),
        native_replay='UNSUPPORTED_NATIVE_SCHEMA',authority='EVIDENCE_ONLY_NO_ROOT_OR_EFFECT_PERMISSION')

def historical_projection_v01(value,path,*,root):
    """All successor fields are checked before producing an immutable old view."""
    require(path in REGISTRY_PATHS and type(value) is dict and KEY in value,'registry_profile_required')
    require(value[KEY]==registration_v01(root),'registry_exact_extension')
    old=deepcopy(value);del old[KEY]
    if path==REGISTRY_PATHS[2]:
        require(old['current_schema_paths'].count(SCHEMA)==1 and old['current_loader_or_registry_refs'].count(LOADER)==1,'schema_registration')
        old['current_schema_paths'].remove(SCHEMA);old['current_loader_or_registry_refs'].remove(LOADER)
    require(digest(old)==HISTORICAL_JSON_PINS[path],'historical_registry_identity')
    return old

def validate_registration_v01(root):
    root=Path(root);values={p:read(root/p) for p in REGISTRY_PATHS}
    historical={p:historical_projection_v01(v,p,root=root) for p,v in values.items()}
    for symbol in SYMBOLS.values():
        module,name=symbol.split(':');tree=ast.parse((root/(module.replace('.','/')+'.py')).read_bytes())
        require(name in {n.name for n in tree.body if isinstance(n,ast.FunctionDef)},'registered_symbol:'+symbol)
    from hedgehog.gate4_reference_contracts_v01 import reference_schema_v01
    require(read(root/SCHEMA)==reference_schema_v01(),'exact_schema_writer')
    return dict(profile=PROFILE,registration=values[REGISTRY_PATHS[0]][KEY],
        identities={p:identity(root/p) for p in REGISTRY_PATHS},historical=historical)

def parent_registration_v01(root):
    """The G37 block stays historical, after the complete successor is checked."""
    from demo import run_living_gauntlet_v01 as l
    validate_registration_v01(root)
    block=read(Path(root)/'release/current_status_overlay_v01.json')[l._G37_REGISTRATION_KEY_V01]
    expected=dict(profile='GATE3_G37_FROZEN_RELEASE_ADMISSION_V01',basis=l._G37_BASE_V01,
        status='EXACT_SOURCE_ADMISSION_DERIVED_FROM_GIT',authority='EVIDENCE_ONLY_NO_ROOT_OR_EFFECT_HANDLE',
        base_identities=l._G37_BASE_IDENTITIES_V01,frozen_source_identities=l._G37_FROZEN_SOURCES_V01,
        rows=list(l._G37_REGISTRATION_ROWS_V01),schema_paths=['schemas/work_composition_v01.schema.json','schemas/capability_admission_v01.schema.json'])
    require(block==expected,'historical_registration_block')
    for name,pin in l._G37_FROZEN_SOURCES_V01.items():
        if name!='demo/run_kernel_conformance_v01.py':
            require(identity(Path(root)/name)['sha256']==pin,'historical_runtime_source:'+name)
    return block

def decode_conformance_v01(value):
    """Exact saved generic projection into existing typed public contracts."""
    from hedgehog.kernel import conformance_v01 as c
    def record(cls,v):
        require(set(v)=={f.name for f in fields(cls)},'parent_typed_fields')
        return cls(**{k:tuple(x) if type(x) is list else x for k,x in v.items()})
    v=deepcopy(value)
    v['counters']=record(c.ConformanceCountersV01,v['counters'])
    for key,cls in [('category_results',c.ConformanceCategoryResultV01),('domain_results',c.DomainConformanceResultV01),('negative_test_results',c.NegativeConformanceResultV01)]:
        v[key]=tuple(record(cls,x) for x in v[key])
    v['claim_to_current_act']=tuple((k,tuple(x)) for k,x in v['claim_to_current_act'])
    result=record(c.KernelConformanceReportV01,v)
    require(not c.validate_kernel_conformance_report_v01(result),'parent_conformance_public')
    projected=c.kernel_conformance_report_to_plain_dict_v01(result);expected=deepcopy(value)
    expected['claim_to_current_act']=dict(expected['claim_to_current_act'])
    require(projected==expected,'parent_conformance_round_trip')
    return result

def validate_parents_v01(*,directory,expected_manifest_sha256,root):
    """External pin, raw historical originals and admitted supplied consumers."""
    from demo import run_living_gauntlet_v01 as l,run_kernel_conformance_v01 as c
    p=Path(directory);require(identity(p/'MANIFEST.json')['sha256']==expected_manifest_sha256,'parent_manifest_pin')
    m=read(p/'MANIFEST.json');require(set(m)=={'profile','files','reports','source_impact'} and m['profile']=='G44_RETAINED_G37R_V01','parent_manifest_shape')
    for name,pin in m['files'].items():
        from hedgehog.gate4_reference_evidence_v01 import _path
        require(identity(p/_path(name))==pin,'parent_raw_identity:'+name)
    require(set(m['reports'])=={'living','conformance'},'parent_reports')
    living=read(p/m['reports']['living']);conformance=read(p/m['reports']['conformance'])
    expected=parent_registration_v01(root)
    require(living['legacy']['current_registration']==expected,'parent_registration')
    require(not l.validate_living_parent_g44_v01(living,root=root),'parent_living_public')
    typed=dict(conformance,legacy=decode_conformance_v01(conformance['legacy']))
    require(not c.validate_kernel_conformance_g36_v01(typed),'parent_conformance_successor')
    impact=m['source_impact'];require(set(impact)=={'unchanged','changed_consumers'} and
        set(impact['changed_consumers'])=={'demo/run_living_gauntlet_v01.py','demo/run_kernel_conformance_v01.py'},'parent_impact_shape')
    for name,pin in impact['unchanged'].items():require(identity(Path(root)/name)==pin,'parent_unchanged_source:'+name)
    for name,row in impact['changed_consumers'].items():
        require(set(row)=={'parent','current'} and identity(Path(root)/name)==row['current']
            and identity(p/'sources'/name)==row['parent'],'parent_changed_consumer:'+name)
    return dict(profile='G44_RETAINED_PARENT_CHECKED_V01',evidence='RECORDED_G37R_NOT_FRESH_COLLECTION',
        manifest_sha256=expected_manifest_sha256,reports={k:identity(p/v) for k,v in m['reports'].items()},
        living_status=living['legacy']['final_status'],conformance_status=conformance['legacy']['final_status'],collectors=0)

def validate_release_v01(*,parent_directory,parent_pin,package,trust,root):
    from hedgehog.gate4_reference_evidence_v01 import verify_package_v01
    registration=validate_registration_v01(root)
    parent=validate_parents_v01(directory=parent_directory,expected_manifest_sha256=parent_pin,root=root)
    g4=verify_package_v01(package=package,trust=trust)
    return dict(profile=PROFILE,status='SCOPED_COMBINED_SUPPORTED_PASS',parent=parent,g4=g4,
        registration=registration,provenance=dict(parent='RECORDED_G37R',g4_execution='RECORDED_G43',
            g4_saved_verification='FRESH',current_registration='FRESH_CHECKED'),
        collectors=dict(legacy=0,g4=0),owner_admission='NOT_PERFORMED',gate4_status='NOT_CLOSED')

def collect_release_v01(directory,*,controlled_clock=False):
    """Sole explicit fresh G4 owner. Supplied entries never invoke this function."""
    from hedgehog.domains.airline.gate4_reference_adapter_v01 import native_story_v42
    return native_story_v42(directory,controlled_clock=controlled_clock)
