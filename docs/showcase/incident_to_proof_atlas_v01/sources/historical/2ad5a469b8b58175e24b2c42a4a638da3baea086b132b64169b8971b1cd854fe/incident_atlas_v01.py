"""Incident Atlas evidence index and pure supplied verification, not authority."""
import hashlib
import json
from pathlib import Path

VERSION = 'INCIDENT_ATLAS_AT1_V01'
ROOT = Path(__file__).resolve().parents[1]


def canonical_v01(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode()


def digest_v01(value):
    return hashlib.sha256(canonical_v01(value)).hexdigest()


def require_v01(condition, reason):
    if not condition:
        raise ValueError(reason)


def coverage_v01(completed=None):
    """Pending rows never inherit a neighboring card's execution status."""
    spec = json.loads((ROOT / 'fixtures/incident_atlas_cases_v01.json').read_bytes())
    completed = completed or {}
    require_v01(set(completed) <= {r['id'] for r in spec['cards']}, 'atlas_unknown_case')
    for row in spec['cards']:
        row.update(status='COMPLETED' if row['id'] in completed else 'PENDING',
                   execution='FRESH_PUBLIC' if row['id'] in completed else 'NOT_RUN',
                   evidence_refs=completed.get(row['id'], []))
    return spec


def source_identity_v01():
    """Code identity without provider/environment or Git authority assumptions."""
    names = ('hedgehog/incident_atlas_v01.py',
             'hedgehog/domains/supplier_water_filter/incident_atlas_v01.py',
             'hedgehog/domains/supplier_water_filter/incident_atlas_backend_v01.py',
             'fixtures/incident_atlas_cases_v01.json', 'fixtures/incident_atlas_supplier_v01.json')
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}


def collect_v01(directory, *, domain='SUPPLIER_WATER_FILTER'):
    require_v01(domain == 'SUPPLIER_WATER_FILTER', 'atlas_domain_not_implemented')
    from hedgehog.domains.supplier_water_filter.incident_atlas_v01 import collect_supplier_v01
    return collect_supplier_v01(Path(directory))
