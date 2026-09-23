"""Passive finite source capture. Saved records never reconstruct a live Host."""
import sys
from hedgehog import outcome_feedback_v01 as f
from hedgehog.kernel import abi_v01 as abi, root_decision_v01 as roots, effect_firewall_v01 as fw
from . import kernel_adapter_v01 as k, monitoring_runtime_v01 as runtime
from .evidence_v01 import plain


def work_record_v01(program, results, artifact, catalogue):
    return dict(program=f.g35_record_to_plain_v01(program),results=f.g35_record_to_plain_v01(results),
        artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),
        admissions=f.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(v) for v in catalogue)))


class NativeObserverV01:
    """Observe only these exact returns, without replacing calls or decisions."""
    def __init__(self):
        self.tool=4;self.roots=[];self.work=[];self.prepared=[];self.actions=[]

    def __enter__(self):
        self.codes={roots.decide_root_v01.__code__:'root',runtime.Sentinel.pure_consumer.__code__:'work',
            k.prepare_command.__code__:'prepare',k.dispatch.__code__:'action'}
        sys.monitoring.use_tool_id(self.tool,'atlas-sentinel-records')
        def returned(code,offset,value):
            frame=sys._getframe(1);local=frame.f_locals;kind=self.codes[code]
            if kind=='root':
                self.roots.append([f.g35_record_to_plain_v01(v) for v in (local['kernel'],local['decision_input'],value)])
            elif kind=='work':
                program,results,artifact=value
                self.work.append(work_record_v01(program,results,artifact,local['self'].catalogue))
            elif kind=='prepare':
                authorization,inputs,observation,review=value
                self.prepared.append(dict(authorization=f.g35_record_to_plain_v01(authorization),inputs=f.g35_record_to_plain_v01(inputs),
                    observation=plain(observation),review=[f.g35_record_to_plain_v01(v) for v in review],
                    checks=dict(local['checks']),command=dict(local['values']),fact=local['fact']))
            else:
                session=local['session']
                self.actions.append(dict(effect=value,registry=f.g35_record_to_plain_v01(session.host.registry),
                    host_revision=session.host.revision,root=session.root,task=session.id))
        sys.monitoring.register_callback(self.tool,sys.monitoring.events.PY_RETURN,returned)
        for code in self.codes:sys.monitoring.set_local_events(self.tool,code,sys.monitoring.events.PY_RETURN)
        return self

    def __exit__(self,*args):
        for code in self.codes:sys.monitoring.set_local_events(self.tool,code,0)
        sys.monitoring.free_tool_id(self.tool)

    def plain_v01(self):
        return dict(roots=self.roots,work=self.work,prepared=self.prepared,actions=self.actions,
            observation_scope='FOUR_SELECTED_CODE_OBJECT_RETURNS_NOT_OS_MONITORING')
