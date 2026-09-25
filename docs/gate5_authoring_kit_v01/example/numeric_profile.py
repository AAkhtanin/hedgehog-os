"""Non-target second body-profile example. Deployment supplies PROFILE explicitly."""
from hedgehog.external_drs import gate5_contracts_v01 as c
from hedgehog.external_drs.gate5_body_profile_v01 import ReviewedBodyProfileV01,COMMON_BODY_FIELDS

def validate_body(body):
    c.integer(body['sample']);c.integer(body['computed'])
    c.require(body['computed']==c.add(c.mul(3,body['sample']),2),'numeric_arithmetic')

def validate_pointer(pointer):
    c.require(pointer['safe_summary']=='Bounded integer transform evidence.','numeric_summary')

def validate_binding(body,policy,pointer):
    c.require(pointer['published_scope']=={'domain':policy['domain']} and policy['domain']=='INTEGER_TRANSFORM','numeric_scope')

PROFILE=ReviewedBodyProfileV01('BoundedIntegerTransformV01',COMMON_BODY_FIELDS+('sample','computed'),('domain',),
    'accept_transform',validate_body,validate_pointer,validate_binding)
