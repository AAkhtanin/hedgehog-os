"""Private original captures and safe, source-bound execution projections."""
import json
import os
from pathlib import Path
from . import contracts_v01 as c


def media_value(value):
    """Finite evidence values only. Runtime Host/capture handles have no fallback."""
    from dataclasses import fields,is_dataclass
    from types import MappingProxyType
    from hedgehog.kernel import abi_v01 as abi
    if value is None or type(value) in (str,int,bool,float):return value
    if type(value) is abi.KernelArtifactV01:return abi.kernel_artifact_to_plain_dict_v01(value)
    if type(value) in (tuple,list):return [media_value(v) for v in value]
    if type(value) in (dict,MappingProxyType):
        c.require(all(type(k) is str for k in value),'media_evidence_string_keys')
        return {k:media_value(v) for k,v in value.items()}
    if is_dataclass(value) and type(value).__module__.startswith('hedgehog.'):
        c.require(type(value).__module__!='hedgehog.work_execution_host_v01','runtime_origin_not_serializable')
        return {f.name:media_value(getattr(value,f.name)) for f in fields(value)}
    raise ValueError('unsupported_media_evidence_value:'+type(value).__name__)


def save_media_return(workspace,directory):
    """Portable diagnostic projection; not a restored live origin or effect replay."""
    from dataclasses import fields
    from hedgehog.kernel import fractal_runtime_v02 as d
    from hedgehog import work_execution_host_v01 as hosts
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    c.require(hasattr(workspace,'delta_return'),'media_return_required')
    bundle=workspace.delta_return
    hosts.validate_retained_action_source_capture_v01(workspace.host,workspace.audio_capture,require_current=False)
    projected={f.name:media_value(getattr(bundle,f.name)) for f in fields(bundle)
        if f.name not in ('source_context','recomputed_g2d_execution_bundle')}
    source=bundle.source_context
    projected['historical_source']={f.name:media_value(getattr(source,f.name)) for f in fields(source)
        if f.name not in ('current_source_host','current_source_capture','baseline_g2d_execution_bundle')}
    projected['temporal_binding']=media_value(bundle.recomputed_g2d_execution_bundle.temporal_binding)
    projected['origin_proof']='ACTUAL_RETAINED_HOST_VALIDATED_AT_EXPORT; NOT_RESTORED_BY_JSON'
    (directory/'E_return.json').write_bytes(c.canonical(projected))
    baseline=d.fractal_runtime_execution_bundle_to_plain_data_v02(source.baseline_g2d_execution_bundle)
    (directory/'D_baseline.json').write_bytes(c.canonical(baseline))
    retained=d.fractal_retained_work_execution_bundle_to_plain_data_v01(bundle.recomputed_g2d_execution_bundle)
    (directory/'D_retained.json').write_bytes(c.canonical(retained))
    (directory/'media_consumption.json').write_bytes(c.canonical(None if workspace.media_delta is None else workspace.media_delta['consumed']))
    return dict(baseline_sha256=c.digest(baseline),retained_sha256=c.digest(retained),E_sha256=c.digest(projected))


def save_report(workspace, directory):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    report=workspace.report()
    (directory/'report.json').write_bytes(c.canonical(report))
    private=directory/'private'
    private.mkdir(exist_ok=True,mode=0o700)
    path=private/'semantic_captures.json'
    path.write_bytes(c.canonical(workspace.captures))
    os.chmod(path,0o600)
    safe=[dict(role=r['role'],mode=r['mode'],model=r['model'],request_ref=r['request_ref'],
        projection_ref=r['projection_ref'],response_ref=r['response_ref'],output=r['output']) for r in workspace.captures]
    (directory/'semantic_safe.json').write_bytes(c.canonical(safe))
    if workspace.preview:
        source=workspace.directory/'cache'/('preview_%04d.png'%workspace.preview['version'])
        if source.is_file():
            data=source.read_bytes()
            c.require(c.digest(data)==workspace.preview['sha256'],'observed_preview_export_binding')
            (directory/('observed_preview_%04d.png'%workspace.preview['version'])).write_bytes(data)
    sidecar=workspace.directory/'output/selection.json'
    if sidecar.exists() and workspace.saved is not None:
        actual=sidecar.read_bytes()
        approved=workspace.approvals[workspace.saved['approval']]['candidate']
        c.require(c.digest(actual)==approved['bytes_sha256'] and json.loads(actual)==approved['content'],'independent_sidecar_verification')
        (directory/'verified_sidecar.json').write_bytes(actual)
    elif sidecar.exists():
        (directory/'uncertain_write.json').write_bytes(c.canonical(dict(outcome=workspace.write_outcome,
            observed_bytes=len(sidecar.read_bytes()),observed_sha256=c.digest(sidecar.read_bytes()),accepted=False)))
    return report
