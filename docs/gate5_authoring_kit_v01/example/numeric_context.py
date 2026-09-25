"""Closed numerical context, derived only after public signed component checks."""
from hedgehog.external_drs import gate5_contracts_v01 as c
from numeric_profile import PROFILE

def derive_context(material, policy, use_time, history, conflicts):
    checked=c.check_bundle(material['bundle'],material['descriptor'],material['request'],
        material['status'],policy,use_time,history,conflicts,profile=PROFILE)
    b=checked['body'];p=material['descriptor']['value'];s=material['status']['value'];r=material['request']
    projection=dict(publisher=p['publisher_root_id'],recipient=policy['local_root'],
        pointer_ref=p['pointer_id'],source_revision=b['source_revision'],request_ref=r['request_id'],
        request_revision=r['request_revision'],policy_sha256=c.sha(policy),checked_at=s['checked_at'],
        valid_until=s['valid_until'],status=checked['status_entry']['state'],source_end=checked['source_end'],use_time=use_time)
    return dict(body=b,source_projection=projection)

def consume(context):
    c.shape(context,('body','source_projection'))
    b=context['body'];s=context['source_projection']
    c.validate('body',b,profile=PROFILE)
    c.shape(s,('publisher','recipient','pointer_ref','source_revision','request_ref','request_revision',
               'policy_sha256','checked_at','valid_until','status','source_end','use_time'))
    c.require(s['status']=='ACTIVE','numeric_status_required')
    c.require(s['checked_at']<=s['use_time']<min(s['valid_until'],s['checked_at']+60,s['source_end']),'numeric_time_required')
    c.require(s['source_revision']==b['source_revision'],'numeric_source_revision')
    return c.add(c.add(b['computed'],b['sample']),c.integer(s['request_revision']))
