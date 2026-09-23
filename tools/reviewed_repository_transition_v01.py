"""Read-only exact repository transitions under an external review context.

This module is initially inactive.  Its raw bytes and the complete enforcement
chain require independent bootstrap review before becoming a trusted verifier.
It never creates review context, awards functional acceptance, or changes Git.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from functools import lru_cache


VERSION = "reviewed_repository_transition_v01"
REPOSITORY = "AAkhtanin/hedgehog-os"
ACCEPTED = {
    "commit": "71e166ccb88b024fd3ca3a25e17da110c6db1a3f",
    "parent": "d199199a578c078c913a2381f595549175bd9235",
    "tree": "71e0438a4ef8532a3047a6e87061240d5b958a31",
}
CONTEXT_ENV = "HEDGEHOG_REPOSITORY_REVIEW_CONTEXT_V01"
CONTEXT_LOCAL = "reviewed_repository_transition_v01/context.json"
POLICY_PATHS = (
    "tools/reviewed_repository_transition_v01.py",
    "tools/check_active_architecture_authority_v01.py",
    "tests/test_repository_release_spine_v01.py",
    "docs/repository_transition_admission_v01.md",
)
METADATA_PATHS = (
    "specs/document_authority_index_v01.json",
    "release/successor_context_manifest_v01.json",
    "release/current_status_overlay_v01.json",
)
BOOTSTRAP_PATHS = frozenset(POLICY_PATHS) | frozenset(METADATA_PATHS) | {
    "AGENTS.md", "README.md", "specs/current_architecture_lock_v01.md",
    "tests/test_active_architecture_authority_v01.py",
    "tests/test_reviewed_repository_transition_v01.py",
}
RECORD_KEY = "repository_transition_admission_v01"
RECORD = {
    "version": VERSION,
    "authority": "SOURCE_ADMISSION_ONLY_NO_ROOT_OR_EFFECT_PERMISSION",
    "review_context": "EXTERNAL_OPERATOR_SUPPLIED_NOT_A_SIGNATURE",
    "bootstrap": "PENDING_INDEPENDENT_REVIEW_AND_SEPARATE_OWNER_LANDING",
    "contract": "docs/repository_transition_admission_v01.md",
    "historical_runtime_and_registration": "PRESERVED",
}
PROTECTED_PINS = {
    "hedgehog/kernel/work_composition_v01.py":
        "1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0",
    "fixtures/gate3_adversary_reference_v01.json":
        "5fe0e6852030c727538ae18823b375a92e2a10010e960e23ae75ef48189052f5",
    "release/completion_manifest.json":
        "a5500c8763edb31b3edf01353e461295754af4651afa7792f642b172d6ca0bd0",
    "release/integration_seam_index.json":
        "0db7692fd5d22d206afe3750c9940807b2e3b6947cd4d4b7dafa0afd98b3bb7d",
    "release/current_schema_surface_v01.json":
        "7094cc2438599ce3ae450acca4876e177df736893caf9ffba1ebcaf8480cf451",
}
SEALED_CAPSULE = "docs/showcase/gate3_closure_v01"
SEALED_MANIFEST = "2f7dc7fd21624a4119c8f54146225c7cf6f8c1d443bd985df99e0e0920abc7be"
OPERATIONS = (
    "MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD",
    "BISECT_LOG", "rebase-merge", "rebase-apply", "sequencer",
    "index.lock", "HEAD.lock", "packed-refs.lock",
)


class Refusal(ValueError):
    """A deterministic source-admission refusal, never a permission grant."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def _digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _object_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, "JSON_DUPLICATE_KEY:" + key)
        result[key] = value
    return result


def strict_json(body: bytes) -> object:
    try:
        return json.loads(body, object_pairs_hook=_object_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              Refusal("JSON_NONFINITE:" + value)))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("JSON_MALFORMED") from exc


def _keys(value: object, expected: set[str], reason: str) -> dict:
    _require(type(value) is dict and set(value) == expected, reason)
    return value


def _hex(value: object, size: int = 64) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{%d}" % size, value) is not None


def _relative(value: object) -> bool:
    return (
        type(value) is str and bool(value)
        and not any(ord(char) < 32 for char in value)
        and "\\" not in value
        and not PurePosixPath(value).is_absolute()
        and all(part not in ("", ".", "..", ".git") for part in value.split("/"))
    )


def _read_regular(file: Path, reason: str, *, repository_file: bool = False) -> bytes:
    _require(not any(parent.is_symlink() for parent in (file, *file.parents)),
             reason + ":SYMLINK")
    try:
        info = file.stat()
        _require(stat.S_ISREG(info.st_mode), reason + ":TYPE")
        allowed = (0o400, 0o600, 0o644, 0o755) if repository_file else (0o600, 0o644, 0o755)
        _require(stat.S_IMODE(info.st_mode) in allowed, reason + ":MODE")
        return file.read_bytes()
    except OSError as exc:
        raise Refusal(reason + ":UNREADABLE") from exc


def git(root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ("git", "--no-optional-locks", "-C", str(root), *args), capture_output=True
    )
    _require(completed.returncode == 0, "GIT_COMMAND:" + args[0])
    return completed.stdout


def _git_dir(root: Path) -> Path:
    return Path(git(root, "rev-parse", "--absolute-git-dir").decode().strip())


def resolve_context(root: Path, explicit: Path | None = None) -> dict | None:
    """Read external context; conflicting sources refuse without repair."""
    paths = []
    if explicit is not None:
        paths.append(Path(explicit))
    if os.environ.get(CONTEXT_ENV):
        paths.append(Path(os.environ[CONTEXT_ENV]))
    local = _git_dir(root) / CONTEXT_LOCAL
    if local.exists() or local.is_symlink():
        paths.append(local)
    if not paths:
        return None
    contexts = []
    for file in paths:
        _require(file.is_absolute(), "REVIEW_CONTEXT_ABSOLUTE_PATH_REQUIRED")
        document = strict_json(_read_regular(file, "REVIEW_CONTEXT_FILE"))
        installation = type(document) is dict and document.get("schema") == INSTALL_VERSION
        _keys(document, {
            "schema", "repository", "policy_id", "kind", "accepted_basis",
            "base", "previous", "manifest", "state", "finalized", "purpose",
        } | ({"installation"} if installation else set()), "REVIEW_CONTEXT_SHAPE")
        _require(document["schema"] in (VERSION, INSTALL_VERSION), "REVIEW_CONTEXT_VERSION")
        _require(document["repository"] == REPOSITORY, "REVIEW_CONTEXT_REPOSITORY")
        _require(document["kind"] in ((INSTALL_KIND, "DOCUMENTATION", "ENGINEERING") if installation else ("BOOTSTRAP", "DOCUMENTATION", "ENGINEERING")),
                 "REVIEW_CONTEXT_KIND")
        if installation:
            _installation_context_shape(document)
        _require(_hex(document["policy_id"]), "REVIEW_CONTEXT_POLICY")
        _require(document["accepted_basis"] == ACCEPTED, "REVIEW_CONTEXT_ACCEPTED_BASIS")
        _base_shape(document["base"])
        binding = _keys(document["manifest"], {"path", "sha256"}, "REVIEW_CONTEXT_MANIFEST")
        _require(type(binding["path"]) is str and Path(binding["path"]).is_absolute()
                 and _hex(binding["sha256"]), "REVIEW_CONTEXT_MANIFEST_BINDING")
        _require(document["state"] in ("PREPARED", "FINALIZED"), "REVIEW_CONTEXT_STATE")
        _require(document["purpose"] in ("INDEPENDENT_REVIEW", "DISPOSABLE_TEST_ONLY"),
                 "REVIEW_CONTEXT_PURPOSE")
        if document["state"] == "PREPARED":
            _require(document["finalized"] is None, "REVIEW_CONTEXT_PREPARED_TIP")
        else:
            _base_shape(document["finalized"])
        contexts.append(document)
    _require(all(document == contexts[0] for document in contexts), "REVIEW_CONTEXT_CONFLICT")
    return contexts[0]


def _base_shape(value: object) -> None:
    value = _keys(value, {"commit", "tree"}, "BASE_SHAPE")
    _require(_hex(value["commit"], 40) and _hex(value["tree"], 40), "BASE_IDENTITY")


def _identity_shape(value: object) -> None:
    value = _keys(value, {"type", "mode", "bytes", "sha256"}, "FILE_IDENTITY_SHAPE")
    _require(value["type"] == "regular" and value["mode"] in ("100644", "100755")
             and type(value["bytes"]) is int and value["bytes"] >= 0
             and _hex(value["sha256"]), "FILE_IDENTITY_VALUE")


def identity(body: bytes, mode: str) -> dict:
    return {"type": "regular", "mode": mode, "bytes": len(body), "sha256": _digest(body)}


def _manifest(context: dict) -> tuple[dict, dict[str, dict]]:
    body = _read_regular(Path(context["manifest"]["path"]), "MANIFEST_FILE")
    _require(_digest(body) == context["manifest"]["sha256"], "MANIFEST_PIN")
    value = strict_json(body)
    _keys(value, {
        "schema", "repository", "policy_id", "kind", "accepted_basis", "base",
        "previous", "governed_namespaces", "commit_message", "ledger",
    }, "MANIFEST_SHAPE")
    for key in ("schema", "repository", "policy_id", "kind", "accepted_basis", "base", "previous"):
        _require(value[key] == context[key], "CONTEXT_MANIFEST_MISMATCH:" + key)
    _require(type(value["commit_message"]) is str and bool(value["commit_message"])
             and "\n" not in value["commit_message"], "COMMIT_MESSAGE_SHAPE")
    namespaces = value["governed_namespaces"]
    _require(type(namespaces) is list and len(namespaces) == len(set(namespaces))
             and all(type(name) is str and re.fullmatch(
                 r"docs/showcase/[a-z0-9_]+_v[0-9]+", name) for name in namespaces),
             "GOVERNED_NAMESPACES")
    _require(type(value["ledger"]) is list and bool(value["ledger"]), "LEDGER_REQUIRED")
    ledger = {}
    folded = set()
    for row in value["ledger"]:
        _keys(row, {"path", "action", "pre", "post"}, "LEDGER_ROW_SHAPE")
        name = row["path"]
        _require(_relative(name), "LEDGER_UNSAFE_PATH")
        _require(name not in ledger and name.casefold() not in folded, "LEDGER_DUPLICATE_PATH")
        _require(row["action"] in ("A", "M"), "LEDGER_UNSUPPORTED_ACTION")
        _identity_shape(row["post"])
        if row["action"] == "A":
            _require(row["pre"] is None, "LEDGER_ADD_PREIMAGE")
        else:
            _identity_shape(row["pre"])
            _require(row["pre"] != row["post"], "LEDGER_NO_CHANGE")
        ledger[name] = row
        folded.add(name.casefold())
    return value, ledger


@lru_cache(maxsize=8)
def _tree_objects(common_git_dir: str, commit: str) -> dict[str, tuple[str, bytes, str]]:
    """Cache only immutable Git blobs, never current filesystem validation."""
    prefix = ("git", "--git-dir=" + common_git_dir)
    completed = subprocess.run((*prefix, "ls-tree", "-rz", commit), capture_output=True, check=True)
    entries = []
    for row in completed.stdout.split(b"\0"):
        if row:
            header, raw_name = row.split(b"\t", 1)
            mode, kind, oid = header.decode().split()
            name = raw_name.decode()
            _require(_relative(name) and kind == "blob" and mode in ("100644", "100755"),
                     "BASE_FILE_TYPE:" + name)
            entries.append((name, mode, oid))
    process = subprocess.run((*prefix, "cat-file", "--batch"), input=(
        "".join(oid + "\n" for _, _, oid in entries)).encode(), capture_output=True, check=True)
    data, offset, result = process.stdout, 0, {}
    for name, mode, oid in entries:
        end = data.index(b"\n", offset)
        found, kind, size = data[offset:end].decode().split()
        size = int(size)
        _require(found == oid and kind == "blob", "BASE_BLOB_BINDING")
        body = data[end + 1:end + 1 + size]
        _require(len(body) == size, "BASE_BLOB_SIZE")
        offset = end + 2 + size
        result[name] = (mode, body, oid)
    return result


def tree_objects(root: Path, commit: str) -> dict[str, tuple[str, bytes, str]]:
    common = git(root, "rev-parse", "--git-common-dir").decode().strip()
    directory = Path(common) if Path(common).is_absolute() else root / common
    return _tree_objects(str(directory.resolve()), commit)


def _current_file(root: Path, name: str) -> tuple[dict, str]:
    file = root / name
    body = _read_regular(file, "CURRENT_FILE:" + name, repository_file=True)
    mode = stat.S_IMODE(file.stat().st_mode)
    _require(mode in (0o400, 0o600, 0o644, 0o755), "CURRENT_MODE:" + name)
    git_mode = "100755" if mode == 0o755 else "100644"
    oid = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
    return identity(body, git_mode), oid


def policy_identity(root: Path) -> str:
    """Full raw-byte identity of the verifier, integration, binder and contract."""
    return _digest(_canonical({name: _current_file(root, name)[0] for name in POLICY_PATHS}))


def current_invariants(root: Path) -> list[str]:
    """Shared current Git safety checks, also run at the historical entry."""
    errors = []
    try:
        _require(git(root, "branch", "--show-current").strip() == b"main", "CURRENT_BRANCH")
        _require(git(root, "config", "--get", "remote.origin.url").decode().strip() in (
            "https://github.com/AAkhtanin/hedgehog-os",
            "https://github.com/AAkhtanin/hedgehog-os.git",
            "git@github.com:AAkhtanin/hedgehog-os.git",
        ), "CURRENT_REPOSITORY")
        for row in git(root, "ls-files", "-v", "-z").split(b"\0"):
            if row and not row.startswith(b"H "):
                errors.append("INDEX_HIDDEN_FLAGS")
        if any(int(flag, 16) for flag in re.findall(
                r"flags: ([a-fA-F0-9]+)", git(root, "ls-files", "--debug").decode())):
            errors.append("INDEX_DEBUG_FLAGS")
        index_path = Path(git(root, "rev-parse", "--git-path", "index").decode().strip())
        if not index_path.is_absolute():
            index_path = root / index_path
        _read_regular(index_path, "INDEX_FILE")
        for marker in OPERATIONS:
            file = Path(git(root, "rev-parse", "--git-path", marker).decode().strip())
            if not file.is_absolute():
                file = root / file
            if file.exists() or file.is_symlink():
                errors.append("GIT_OPERATION:" + marker)
    except (Refusal, OSError) as exc:
        errors.append(str(exc))
    return sorted(set(errors))


def _accepted_objects(root: Path) -> dict:
    _require(git(root, "show", "-s", "--format=%P%n%T", ACCEPTED["commit"]).decode().splitlines()
             == [ACCEPTED["parent"], ACCEPTED["tree"]], "ACCEPTED_COMMIT_PARENT_TREE")
    accepted = tree_objects(root, ACCEPTED["commit"])
    parent = tree_objects(root, ACCEPTED["parent"])
    added = set(accepted) - set(parent)
    modified = {name for name in set(accepted) & set(parent) if accepted[name] != parent[name]}
    _require(len(accepted) == 1135 and len(added) == 40 and len(modified) == 19
             and not set(parent) - set(accepted), "ACCEPTED_G37_DELTA")
    return accepted


def _metadata_and_registration(root: Path, base: dict, accepted: dict, kind: str, installation: dict | None = None) -> list[str]:
    errors = []
    pins = dict(PROTECTED_PINS)
    if installation is not None:
        pins.update({name: row["sha256"] for name, row in installation["new_registries"].items()})
    for name, pin in pins.items():
        try:
            if _digest(_read_regular(root / name, "PROTECTED_FILE:" + name, repository_file=True)) != pin:
                errors.append("PROTECTED_IDENTITY:" + name)
        except Refusal as exc:
            errors.append(str(exc))
    for name in METADATA_PATHS:
        try:
            value = strict_json(_read_regular(root / name, "METADATA_FILE:" + name, repository_file=True))
            _require(type(value) is dict, "METADATA_SHAPE:" + name)
            historical = strict_json(accepted[name][1])
            expected = strict_json(base[name][1])
            if kind == "BOOTSTRAP":
                expected = dict(expected, **{RECORD_KEY: RECORD})
            if value != expected:
                errors.append("METADATA_COHERENCE:" + name)
            for key, entry in historical.items():
                if value.get(key) != entry:
                    errors.append("HISTORICAL_METADATA:" + name + ":" + key)
            if value.get(RECORD_KEY) != RECORD:
                errors.append("ADMISSION_RECORD:" + name)
            if name == "release/current_status_overlay_v01.json" and value.get(
                    "gate3_g37_current_registration_v01") != historical.get(
                    "gate3_g37_current_registration_v01"):
                errors.append("G37_CURRENT_REGISTRATION")
        except (Refusal, KeyError) as exc:
            errors.append(str(exc))
    return errors


def _kind_rules(root: Path, manifest: dict, ledger: dict, base: dict, installation: dict | None = None) -> None:
    kind = manifest["kind"]
    capsules = manifest["governed_namespaces"]
    if kind == "BOOTSTRAP":
        _require(manifest["base"] == {key: ACCEPTED[key] for key in ("commit", "tree")}
                 and manifest["previous"] is None, "BOOTSTRAP_BASIS")
        _require(capsules == [SEALED_CAPSULE], "BOOTSTRAP_CAPSULE")
        _require(set(ledger) - {name for name in ledger if name.startswith(SEALED_CAPSULE + "/")}
                 == BOOTSTRAP_PATHS, "BOOTSTRAP_CONTROL_LEDGER")
        capsule_manifest = _read_regular(root / SEALED_CAPSULE / "MANIFEST.json", "CAPSULE_MANIFEST", repository_file=True)
        _require(_digest(capsule_manifest) == SEALED_MANIFEST, "CAPSULE_MANIFEST_PIN")
        original = strict_json(capsule_manifest)
        expected = {SEALED_CAPSULE + "/" + row["path"]: row for row in original["files"]}
        actual = {name for name in ledger if name.startswith(SEALED_CAPSULE + "/")}
        _require(len(expected) == 520 and actual == set(expected) | {SEALED_CAPSULE + "/MANIFEST.json"},
                 "BOOTSTRAP_CAPSULE_LEDGER")
        for name, row in expected.items():
            post = ledger[name]["post"]
            _require(post == {"type": "regular", "mode": "100" + row["mode"][-3:],
                              "bytes": row["bytes"], "sha256": row["sha256"]},
                     "CAPSULE_SOURCE_BINDING:" + name)
        closure = strict_json(_read_regular(
            root / SEALED_CAPSULE / "CLOSURE_ACCEPTANCE.json", "CLOSURE_RECORD", repository_file=True))
        _require(type(closure) is dict, "CLOSURE_RECORD_SHAPE")
        for key, expected_value in {
            "status": "CLOSED_PASS", "owner_commit": ACCEPTED["commit"],
            "parent": ACCEPTED["parent"], "tree": ACCEPTED["tree"],
            "changed_paths": 59, "protected_paths": 1076,
            "presentation_publication": "NOT_YET_PUBLISHED_AT_AUTHORING",
        }.items():
            _require(closure.get(key) == expected_value, "CLOSURE_RECORD:" + key)
    elif kind == INSTALL_KIND:
        _require(installation is not None and manifest["schema"] == INSTALL_VERSION,
                 "EXACT_INSTALLATION_REQUIRED")
    else:
        previous = _keys(manifest["previous"], {"manifest_sha256", "commit", "tree", "policy_id"},
                         "PREVIOUS_TRANSITION_REQUIRED")
        _require(_hex(previous["manifest_sha256"]) and previous["policy_id"] == manifest["policy_id"]
                 and {key: previous[key] for key in ("commit", "tree")} == manifest["base"],
                 "PREVIOUS_TRANSITION_BINDING")
        _require(not set(ledger) & (BOOTSTRAP_PATHS - {"README.md"}), "POLICY_MAINTENANCE_REQUIRED")
        if kind == "ENGINEERING":
            _require(not capsules and "README.md" not in ledger
                     and all(not name.startswith(("docs/showcase/", ".")) for name in ledger),
                     "ENGINEERING_SCOPE")
        else:
            _require(bool(capsules), "DOCUMENTATION_CAPSULE_REQUIRED")
            for name, row in ledger.items():
                if name == "README.md":
                    _require(row["action"] == "M", "DOCUMENTATION_NAVIGATION_ACTION")
                    old = base[name][1].decode()
                    new = (root / name).read_text()
                    lines = new.splitlines(keepends=True)
                    removed = False
                    for i, line in enumerate(lines):
                        match = re.fullmatch(r"\[[A-Za-z0-9 ,.:()_-]+\]\((docs/showcase/[a-z0-9_]+_v[0-9]+/README\.md)\)\n", line)
                        if match and match.group(1).rsplit("/", 1)[0] in capsules and "".join(
                                lines[:i] + lines[i + 1:]) == old:
                            removed = True
                    _require(removed, "DOCUMENTATION_NAVIGATION_EXACT_INSERTION")
                else:
                    _require(row["action"] == "A" and any(name.startswith(item + "/") for item in capsules),
                             "DOCUMENTATION_SCOPE:" + name)
                    _require(row["post"]["mode"] == "100644", "DOCUMENTATION_INERT_MODE")
        for name in POLICY_PATHS:
            _require(_current_file(root, name)[0] == identity(base[name][1], base[name][0]),
                     "POLICY_CHANGED:" + name)
    for capsule in capsules:
        _require(not any(name == capsule or name.startswith(capsule + "/") for name in base),
                 "PRIOR_CAPSULE_IMMUTABLE:" + capsule)


INSTALL_VERSION = "reviewed_repository_policy_installation_v01"
INSTALL_KIND = "POLICY_INSTALLATION"
REGISTRY_PATHS = tuple(name for name in PROTECTED_PINS if name.startswith("release/"))
INSTALLATION_PATHS = frozenset({
    'demo/run_gate4_reference_v01.py', 'demo/run_living_gauntlet_v01.py', 'demo/run_kernel_conformance_v01.py',
    'hedgehog/domains/airline/gate4_reference_adapter_v01.py', 'hedgehog/domains/airline/gate4_reference_history_v01.py',
    'hedgehog/gate4_reference_contracts_v01.py', 'hedgehog/gate4_strategy_reference_v01.py',
    'hedgehog/gate4_pressure_budget_v01.py', 'hedgehog/gate4_reference_runtime_v01.py',
    'hedgehog/gate4_reference_evidence_v01.py', 'hedgehog/gate4_reference_release_v01.py',
    'schemas/gate4_reference_v01.schema.json', 'fixtures/gate4_reference_v01.json',
    'fixtures/gate4_reference_native_v01.json', 'fixtures/gate4_reference_math_v01.json',
    'tests/test_gate4_reference_math_v01.py',
    'tests/test_gate4_reference_supplied_v01.py', 'tests/test_gate4_reference_preflight_v01.py',
    'tests/test_gate4_reference_native_v01.py', 'tests/test_gate4_reference_history_v01.py',
    'tests/test_gate4_reference_evidence_v01.py', 'tests/test_gate4_reference_registration_v01.py',
    'docs/gate4_reference_checkpoint_v01.md', 'docs/gate4_reference_contract_v01.md',
    'docs/gate4_reference_math_checkpoint_v01.md', 'docs/gate4_reference_native_checkpoint_v01.md',
    'docs/gate4_reference_evidence_checkpoint_v01.md', 'docs/gate4_reference_release_checkpoint_v01.md',
    'tests/test_reviewed_repository_transition_v01.py', 'tests/test_active_architecture_authority_v01.py',
}) | frozenset(POLICY_PATHS) | frozenset(REGISTRY_PATHS)


def _object_identities(objects: dict) -> dict:
    return {name: identity(value[1], value[0]) for name, value in objects.items()}


def _installation_context_shape(context: dict) -> None:
    binding = _keys(context["installation"], {"path", "sha256", "tip"}, "INSTALLATION_CONTEXT_SHAPE")
    _require(type(binding["path"]) is str and Path(binding["path"]).is_absolute()
             and _hex(binding["sha256"]), "INSTALLATION_EXTERNAL_BINDING")
    if binding["tip"] is not None:
        _base_shape(binding["tip"])


def validate_policy_installation_v01(root: Path, context: dict, manifest: dict, ledger: dict) -> dict:
    """Inactive until explicitly dispatched by the closed installation schema.

    The external expected bridge pin binds both complete policies and payload.
    This checks the new proposal; it does not claim old-policy authorization.
    All mutable Git/index/inventory checks remain in validate_transition.
    """
    _installation_context_shape(context)
    binding = context["installation"]
    raw = _read_regular(Path(binding["path"]), "INSTALLATION_BRIDGE_FILE")
    _require(_digest(raw) == binding["sha256"], "INSTALLATION_BRIDGE_PIN")
    bridge = _keys(strict_json(raw), {
        "schema", "repository", "base", "predecessor_context", "predecessor_manifest_utf8",
        "old_enforcement", "new_enforcement", "old_policy_id", "new_policy_id",
        "manifest_sha256", "ledger", "old_registries", "new_registries", "commit_message",
    }, "INSTALLATION_BRIDGE_SHAPE")
    _require(bridge["schema"] == INSTALL_VERSION and bridge["repository"] == REPOSITORY,
             "INSTALLATION_BRIDGE_VERSION")
    _base_shape(bridge["base"])
    base_id = bridge["base"]["commit"]
    _require(git(root, "rev-parse", base_id + "^{tree}").decode().strip() == bridge["base"]["tree"],
             "INSTALLATION_BASE_TREE")
    base = tree_objects(root, base_id)
    for key in ("old_enforcement", "new_enforcement"):
        _require(type(bridge[key]) is dict and set(bridge[key]) == set(POLICY_PATHS), "INSTALLATION_ENFORCEMENT_CLOSURE")
        for value in bridge[key].values():
            _identity_shape(value)
    old = {name: identity(base[name][1], base[name][0]) for name in POLICY_PATHS}
    new = {name: _current_file(root, name)[0] for name in POLICY_PATHS}
    _require(old == bridge["old_enforcement"] and new == bridge["new_enforcement"], "INSTALLATION_RAW_ENFORCEMENT")
    _require(_digest(_canonical(old)) == bridge["old_policy_id"] and
             _digest(_canonical(new)) == bridge["new_policy_id"] == context["policy_id"], "INSTALLATION_POLICY_IDS")
    previous = _keys(bridge["predecessor_context"], {
        "schema", "repository", "policy_id", "kind", "accepted_basis", "base", "previous",
        "manifest", "state", "finalized", "purpose",
    }, "INSTALLATION_PREDECESSOR_CONTEXT")
    _require(previous["schema"] == VERSION and previous["repository"] == REPOSITORY
             and previous["accepted_basis"] == ACCEPTED and previous["state"] == "FINALIZED"
             and previous["finalized"] == bridge["base"] and previous["policy_id"] == bridge["old_policy_id"],
             "INSTALLATION_FINALIZED_PREDECESSOR")
    prior_raw = bridge["predecessor_manifest_utf8"].encode()
    _require(_digest(prior_raw) == previous["manifest"]["sha256"], "INSTALLATION_PREDECESSOR_MANIFEST_PIN")
    prior = strict_json(prior_raw)
    _require(set(prior) == {"schema", "repository", "policy_id", "kind", "accepted_basis", "base", "previous", "governed_namespaces", "commit_message", "ledger"}, "INSTALLATION_PRIOR_MANIFEST_SHAPE")
    for key in ("schema", "repository", "policy_id", "kind", "accepted_basis", "base", "previous"):
        _require(prior[key] == previous[key], "INSTALLATION_PRIOR_CONTEXT:" + key)
    old_base = tree_objects(root, prior["base"]["commit"])
    expected_prior = _object_identities(old_base)
    for row in prior["ledger"]:
        _require(row["pre"] == expected_prior.get(row["path"]), "INSTALLATION_PRIOR_PREIMAGE")
        expected_prior[row["path"]] = row["post"]
    _require(expected_prior == _object_identities(base), "INSTALLATION_ADMITTED_BASE_INVENTORY")
    _require(git(root, "show", "-s", "--format=%P%n%B", base_id).decode().strip().splitlines() ==
             [prior["base"]["commit"], prior["commit_message"]], "INSTALLATION_ADMITTED_BASE_PARENT_MESSAGE")
    for key in ("old_registries", "new_registries"):
        _require(type(bridge[key]) is dict and set(bridge[key]) == set(REGISTRY_PATHS), "INSTALLATION_REGISTRY_CLOSURE")
        for value in bridge[key].values():
            _identity_shape(value)
    _require(bridge["old_registries"] == {name: identity(base[name][1], base[name][0]) for name in REGISTRY_PATHS}, "INSTALLATION_OLD_REGISTRIES")
    _require(bridge["new_registries"] == {name: _current_file(root, name)[0] for name in REGISTRY_PATHS}, "INSTALLATION_NEW_REGISTRIES")
    for name, pin in PROTECTED_PINS.items():
        if name not in REGISTRY_PATHS:
            _require(_current_file(root, name)[0]["sha256"] == pin == _digest(base[name][1]), "INSTALLATION_PROTECTED_RUNTIME:" + name)
    payload = bridge["ledger"]
    _require(type(payload) is list and bool(payload), "INSTALLATION_LEDGER_REQUIRED")
    expected = _object_identities(base)
    names = set()
    for row in payload:
        _keys(row, {"path", "action", "pre", "post"}, "INSTALLATION_LEDGER_ROW")
        name = row["path"]
        _require(_relative(name) and name not in names and name in INSTALLATION_PATHS, "INSTALLATION_PATH")
        _require(row["action"] == ("M" if name in base else "A") and row["pre"] == expected.get(name), "INSTALLATION_PREIMAGE")
        _identity_shape(row["post"]); expected[name] = row["post"]; names.add(name)
    _require(set(POLICY_PATHS) - names == {"tools/check_active_architecture_authority_v01.py"}
             and set(REGISTRY_PATHS) <= names and not names.intersection((*METADATA_PATHS, "AGENTS.md", "README.md", "specs/current_architecture_lock_v01.md")), "INSTALLATION_BOUNDED_CONTROLS")
    if manifest["kind"] == INSTALL_KIND:
        _require(manifest["base"] == bridge["base"] and manifest["ledger"] == payload
                 and context["manifest"]["sha256"] == bridge["manifest_sha256"]
                 and manifest["commit_message"] == bridge["commit_message"] and not manifest["governed_namespaces"], "INSTALLATION_EXACT_PROPOSAL")
        _require(manifest["previous"] == dict(manifest_sha256=previous["manifest"]["sha256"],
                 **bridge["base"], policy_id=bridge["old_policy_id"]), "INSTALLATION_PREVIOUS_BINDING")
        _require(binding["tip"] is None or binding["tip"] == context["finalized"], "INSTALLATION_TIP_BINDING")
    else:
        tip = binding["tip"]; _base_shape(tip)
        _require(git(root, "show", "-s", "--format=%P%n%T%n%B", tip["commit"]).decode().strip().splitlines() ==
                 [base_id, tip["tree"], bridge["commit_message"]], "INSTALLED_PARENT_TREE_MESSAGE")
        _require(_object_identities(tree_objects(root, tip["commit"])) == expected, "INSTALLED_EXACT_TREE")
        _require(tip["commit"] in git(root, "rev-list", manifest["base"]["commit"]).decode().splitlines(), "INSTALLED_BASE_ANCESTRY")
    return bridge


def validate_transition(root: Path, explicit_context: Path | None = None) -> dict:
    """Check exact current sources; never publish, finalize, or create context."""
    root = root.resolve()
    errors = current_invariants(root)
    result = {"phase": "REPOSITORY_TRANSITION_UNADMITTED", "errors": errors,
              "authority": "SOURCE_ADMISSION_ONLY", "remote_publication": "NOT_CHECKED"}
    try:
        context = resolve_context(root, explicit_context)
        _require(context is not None, "REVIEW_CONTEXT_REQUIRED")
        manifest, ledger = _manifest(context)
        _require(policy_identity(root) == context["policy_id"], "POLICY_IDENTITY")
        trusted_root = Path(__file__).resolve().parents[1]
        _require(policy_identity(trusted_root) == context["policy_id"], "EXECUTING_POLICY_IDENTITY")
        accepted = _accepted_objects(root)
        base_commit, base_tree = manifest["base"]["commit"], manifest["base"]["tree"]
        _require(git(root, "rev-parse", base_commit + "^{tree}").decode().strip() == base_tree,
                 "REVIEWED_BASE_TREE")
        ancestry = git(root, "rev-list", base_commit).decode().splitlines()
        _require(ACCEPTED["commit"] in ancestry, "REVIEWED_BASE_ANCESTRY")
        base = tree_objects(root, base_commit)
        installation = validate_policy_installation_v01(root, context, manifest, ledger) if context["schema"] == INSTALL_VERSION else None
        _kind_rules(root, manifest, ledger, base, installation)
        errors.extend(_metadata_and_registration(root, base, accepted, manifest["kind"], installation))
        for name, row in ledger.items():
            if row["action"] == "A":
                _require(name not in base, "PREIMAGE_ADD_EXISTS:" + name)
            else:
                _require(name in base and row["pre"] == identity(base[name][1], base[name][0]),
                         "PREIMAGE_IDENTITY:" + name)
        expected_names = set(base) | set(ledger)
        visible = {name.decode() for name in git(root, "ls-files", "--cached", "--others",
                                                "--exclude-standard", "-z").split(b"\0") if name}
        _require(visible == expected_names, "CURRENT_TRACKED_UNTRACKED_INVENTORY")
        capsules = set(manifest["governed_namespaces"])
        capsules.update("/".join(name.split("/")[:3]) for name in base
                        if re.match(r"docs/showcase/[a-z0-9_]+_v[0-9]+/", name))
        for capsule in sorted(capsules):
            folder = root / capsule
            _require(folder.is_dir() and not folder.is_symlink(), "GOVERNED_NAMESPACE_TYPE")
            observed = set()
            for directory, subdirs, files in os.walk(folder, followlinks=False):
                for item in (*subdirs, *files):
                    file = Path(directory) / item
                    _require(not file.is_symlink(), "GOVERNED_NAMESPACE_SYMLINK")
                observed.update((Path(directory) / item).relative_to(root).as_posix() for item in files)
            _require(observed == {name for name in expected_names if name.startswith(capsule + "/")},
                     "GOVERNED_NAMESPACE_EXTRA_OR_MISSING:" + capsule)
        actual = {}
        for name in sorted(expected_names):
            try:
                found, oid = _current_file(root, name)
                expected = ledger[name]["post"] if name in ledger else identity(base[name][1], base[name][0])
                if found != expected:
                    errors.append(("POSTIMAGE_IDENTITY:" if name in ledger else "PROTECTED_SOURCE:") + name)
                actual[name] = (found["mode"], oid)
            except Refusal as exc:
                errors.append(str(exc))
        index = {}
        for raw in git(root, "ls-files", "--stage", "-z").split(b"\0"):
            if raw:
                header, name = raw.split(b"\t", 1)
                mode, oid, stage = header.decode().split()
                name = name.decode()
                _require(stage == "0" and name not in index, "INDEX_STAGE_OR_DUPLICATE")
                index[name] = (mode, oid)
        status = {}
        for raw in git(root, "status", "--porcelain=v1", "-z", "-uall", "--ignore-submodules=none").split(b"\0"):
            if raw:
                _require(len(raw) > 3 and raw[:2] in (b" M", b"M ", b"A ", b"??"), "STATUS_UNSUPPORTED_OR_MIXED")
                name = raw[3:].decode()
                _require(name not in status, "STATUS_DUPLICATE")
                status[name] = raw[:2].decode()
        head = git(root, "rev-parse", "HEAD").decode().strip()
        parents = git(root, "show", "-s", "--format=%P", "HEAD").decode().split()
        origin = git(root, "rev-parse", "refs/remotes/origin/main").decode().strip()
        baseline_index = {name: (entry[0], entry[2]) for name, entry in base.items()}
        if head == base_commit:
            _require(context["state"] == "PREPARED", "FINALIZED_TIP_MISMATCH")
            _require(origin == base_commit, "PREPARED_ORIGIN")
            unstaged = {name: "??" if row["action"] == "A" else " M" for name, row in ledger.items()}
            staged = {name: row["action"] + " " for name, row in ledger.items()}
            _require(status == unstaged or status == staged, "EXACT_PROPOSAL_STATUS")
            expected_index = baseline_index if status == unstaged else actual
            phase = "PREPARED_UNSTAGED" if status == unstaged else "PREPARED_STAGED"
        else:
            _require(parents == [base_commit], "EXACT_IMMEDIATE_PARENT")
            _require(not status, "COMMITTED_WORKTREE_DIRTY")
            _require(origin in (base_commit, head), "COMMITTED_ORIGIN")
            committed = tree_objects(root, head)
            _require({name: (entry[0], entry[2]) for name, entry in committed.items()} == actual,
                     "COMMITTED_TREE_WORKTREE")
            changed = {name for name in set(base) | set(committed) if base.get(name) != committed.get(name)}
            _require(changed == set(ledger), "COMMITTED_EXACT_DELTA")
            _require(git(root, "show", "-s", "--format=%B", "HEAD").decode().strip() == manifest["commit_message"],
                     "COMMITTED_MESSAGE")
            tip = {"commit": head, "tree": git(root, "rev-parse", "HEAD^{tree}").decode().strip()}
            if context["state"] == "FINALIZED":
                _require(context["finalized"] == tip, "FINALIZED_TIP_MISMATCH")
            expected_index = actual
            phase = "FINALIZED" if context["state"] == "FINALIZED" else "PREPARED_COMMITTED"
        _require(index == expected_index, "INDEX_CONTENT_MODE_WORKTREE")
        result.update(kind=manifest["kind"], manifest_sha256=context["manifest"]["sha256"],
                      policy_id=context["policy_id"], checked_files=len(actual), ledger_paths=len(ledger))
        if not errors:
            result["phase"] = "REVIEWED_" + manifest["kind"] + "_" + phase
    except (Refusal, OSError, KeyError, TypeError, ValueError, subprocess.SubprocessError) as exc:
        errors.append(str(exc) if isinstance(exc, Refusal) else "MALFORMED_INPUT:" + type(exc).__name__)
    result["errors"] = sorted(set(errors))
    return result
