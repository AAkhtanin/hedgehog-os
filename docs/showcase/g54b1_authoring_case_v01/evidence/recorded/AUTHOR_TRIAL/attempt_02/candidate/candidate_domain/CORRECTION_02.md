# Correction 02: ImportStore local persistence reader

Candidate: football_reference_v01. State: inert correction for independent review.
Preceding independently exercised manifest: 712a382be898900eb2e17834abb1bb08c384b9c7d5922d3b1715c016527e4e7a.
This record preserves supplied feedback; it is not an execution log or an admission.

The independent review reported both workers exiting rc0 while domain checks FAILED.
Descriptor MeaningRecord/descent completed. Exact-only and explicitly approved shifted
requester events returned REFUSED / json_key after STATUS and before FETCH or requester
Work. VenueRoot produced NEEDS_CONFIRMATION and OFFER_READY, respectively. Subsequent
book/repeat lacked a selected offer and returned NEEDS_CONFIRMATION; VERIFY returned
CURRENT_STATUS_UNKNOWN. No effect ran. These are reported observations, not target
outputs embedded in the implementation.

The supplied saved-state diagnostic found two legitimate highwater composite keys,
each 173 characters, and independently reproduced json_key on their persisted bytes.
Its control-flow localization was static, not a recovered original exception traceback.
No additional execution or diagnosis of later phases is claimed here.

Public contract and mismatch:

* source/hedgehog/external_drs/gate5_contracts_v01.py
  SHA-256 db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f.
  walk at line 79 requires each object key to be an ASCII string of at most 128
  characters; decode invokes walk. authenticate_status at line 319 creates its
  highwater key from the canonical JSON array of publisher_root_id, pointer_id and
  stream_id. Each reference is validated independently; this composite string need
  not fit the wire object-key bound. check_bundle at line 384 similarly forms a
  local source-conflict identity from publisher/source record/revision.
* source/hedgehog/external_drs/gate5_lifecycle_v01.py
  SHA-256 627fa5171fbaad181c2d4e1c5e8047cc3b8b5957601a317049b05c980ae3de6f.
  Public read at line 16 uses json.loads(Path(path).read_text()). ImportStore.observe
  at lines 31-39 uses that reader, authenticates against existing highwater, then
  writes the original composite key. conflicts at lines 41-42 and import_body at
  lines 50-58 use the same persistence contract. Its calibration convenience
  validate_bundle at line 45 also reads local state with read; the candidate still
  avoids that profile-unaware convenience validator.
* source/hedgehog/external_drs/gate5_exchange_v01.py
  SHA-256 dfc22ae7beb39be05e7433bac7ceff9f2704e81c2638d0fe4727b2aa3eb36b07.
  state_write at lines 26-31 writes canonical local JSON through a pending file and
  atomic replacement. This persistence format is not itself a PipeChannel envelope.

The candidate had applied c.decode to the entire ImportStore state twice: once
after observing STATUS and once before explicit-profile bundle checking. Correction
02 imports the existing read function as read_import_state and uses it at both
sites. No migration is needed. Original keys, revisions, immutable entry hashes,
terminal observations, source conflicts, duplicates and quarantine remain intact.
The input is only store.path under this requester's own assigned state_root.

The source guard, wire decoder, signatures, profile, public APIs and transport are
unchanged. observe still authenticates and persists terminal status before the
current-use check. check_status still enforces request/nonce/pointer binding,
freshness, rollback, equivocation and terminal non-revival. check_bundle still
receives original highwater and conflicts with PROFILE explicitly. No empty-history
fallback, hashed/truncated key, history deletion, re-signing, bound increase or
payload-selected reader is introduced. No Root permission is reconstructed.

Only candidate_domain/transport.py changes runtime behavior in this correction.
Previous file SHA-256: b04655799ad2479622c00e35a92e2ea91a843ad1ec3dbc2064a6f31ec0b563db.
Corrected file SHA-256: 6659c7cbcff6015bb8ee43d18d1c6eddf9fe6d280e75288b178ba79fa49d00fa.

tests/test_native.py extends the signed component test using freshly generated
local signing capability, genuine source Work/body and public validation. It covers
a composite key exceeding 128, persistence reconstruction, unchanged wire refusal,
same-entry freshness, equivocation refusal and lawful continuation, status expiry
and request binding, explicit-profile bundle validation, source conflicts/dedup,
actual consumer Work, and persisted terminal rollback/non-revival checks.
These are authored assertions, not observed test results or peer-story evidence.
No test in the pack has been executed by the author.

README removes the unsupported unittest-discovery claim. The unchanged G54 peer
runner exposes the specified run_peer_v01 entrypoint, not a unittest facility.
A separate authorized test facility has not been supplied. Tests remain unexecuted;
no runner PASS, full native acceptance, booking, live or supplied result is claimed.

PASSPORT.json, dependencies.json and source_impact.json record this scope and retain
the previous correction history. The coordinator alone creates candidate.json from
the submitted bytes. Static syntax/JSON inspection is not source approval,
capability admission, current local authorization, installation or Gate closure.
