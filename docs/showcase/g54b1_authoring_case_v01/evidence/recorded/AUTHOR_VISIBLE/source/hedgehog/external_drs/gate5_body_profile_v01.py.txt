"""Source-reviewed local body profile, never a wire-selected plugin or permission.

The deployment selects one profile in trusted code after source review. There is
no name-to-module loader, public registration service or executable wire field.
The calibration default remains in gate5_contracts_v01 and needs no profile.
"""
from dataclasses import dataclass
from types import FunctionType

COMMON_BODY_FIELDS=('version','source_record_ref','source_revision','source_work_ref',
    'source_review_ref','time_envelope','ttl_base','source_lineage_refs')

@dataclass(frozen=True)
class ReviewedBodyProfileV01:
    schema_id: str
    body_fields: tuple[str,...]
    scope_fields: tuple[str,...]
    policy_accept_field: str
    validate_body: object
    validate_pointer: object
    validate_binding: object

    def __post_init__(self):
        from . import gate5_contracts_v01 as c
        c.label(self.schema_id);c.label(self.policy_accept_field)
        c.require(self.schema_id!=c.BODY_SCHEMA,'calibration_profile_not_replaceable')
        for fields in (self.body_fields,self.scope_fields):
            c.require(type(fields) is tuple and len(fields)==len(set(fields)) and len(fields)<=32,'profile_fields')
            for field in fields:c.label(field)
        c.require(set(COMMON_BODY_FIELDS)<=set(self.body_fields) and 'domain' in self.scope_fields,'profile_common_fields')
        c.require(all(type(fn) is FunctionType for fn in (self.validate_body,self.validate_pointer,self.validate_binding)), 'profile_local_functions')

def check_local_profile_v01(profile):
    if type(profile) is not ReviewedBodyProfileV01:raise ValueError('profile_local_source_required')
    profile.__post_init__()
    return profile
