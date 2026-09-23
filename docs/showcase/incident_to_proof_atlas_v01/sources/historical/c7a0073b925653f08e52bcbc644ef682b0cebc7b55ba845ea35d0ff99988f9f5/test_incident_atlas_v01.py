"""Small index and standalone supplied-proof checks; no implicit collection."""
from hedgehog import incident_atlas_v01 as atlas


def test_atlas_pending_inventory_v01():
    index = atlas.coverage_v01()
    assert len(index['cards']) == len({r['id'] for r in index['cards']}) == 20
    assert len(index['claims']) == 15
    assert all(r['status'] == 'PENDING' and not r['evidence_refs'] for r in index['cards'])
    assert index['variants']['D1']['status'] == 'PENDING'
    assert 'risk_source:W4' in {r['id'] for r in index['risk_sources']}
