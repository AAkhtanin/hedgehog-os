from __future__ import annotations

import ast
from contextlib import contextmanager
import hashlib
import importlib.metadata
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import Iterator

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPOSITORY_ROOT / "pyproject.toml"
LICENSE_PATH = REPOSITORY_ROOT / "LICENSE"
COMMERCIAL_NOTICE_PATH = REPOSITORY_ROOT / "COMMERCIAL-LICENSING.md"
SIGNER_TEST_PATH = REPOSITORY_ROOT / "tests/test_root_signer_isolation_v01.py"

CANONICAL_GNU_SOURCE_DESCRIPTION = (
    "Complete GNU Affero General Public License version 3 text fetched by "
    "the owner from the official GNU Project HTTPS path"
)
CANONICAL_GNU_SOURCE_URL = "https://www.gnu.org/licenses/agpl-3.0.txt"
CANONICAL_AGPL_SOURCE_SHA256 = (
    "0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0"
)

APPROVED_DEPENDENCY_DECLARATIONS = (
    "jsonschema",
    "pytest",
    "pyTelegramBotAPI",
    "google-genai",
    "cryptography==48.0.0",
    "referencing",
    "httpx",
    "httpcore",
    "Pillow",
    "python-pptx",
    "pypdf",
    "reportlab",
)

DIRECT_IMPORT_ROOT_TO_DISTRIBUTION = {
    "cryptography": "cryptography",
    "jsonschema": "jsonschema",
    "pytest": "pytest",
    "referencing": "referencing",
    "google": "google-genai",
    "httpx": "httpx",
    "httpcore": "httpcore",
    "telebot": "pyTelegramBotAPI",
    "PIL": "Pillow",
    "pptx": "python-pptx",
    "pypdf": "pypdf",
    "reportlab": "reportlab",
}

BUILD_SYSTEM_IMPORT_ROOT_TO_REQUIREMENT = {
    "setuptools": "setuptools>=77.0.3",
}

REPOSITORY_IMPORT_ROOTS = {
    "hedgehog",
    "demo",
    "tests",
    "telegram_bot",
    "config",
}


def _pyproject() -> dict[str, object]:
    with PYPROJECT_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _distribution_name(declaration: str) -> str:
    return re.split(r"[\s<>=!~;\[]", declaration, maxsplit=1)[0]


def _normalized_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _repository_python_paths() -> tuple[Path, ...]:
    completed = subprocess.run(
        (
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "*.py",
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    return tuple(sorted({
        (REPOSITORY_ROOT / raw.decode("utf-8")).resolve()
        for raw in completed.stdout.split(b"\0")
        if raw
    }))


def _direct_import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module
        ):
            roots.add(node.module.split(".", 1)[0])
    return roots


def _signer_test_requires_exact_cryptography_version() -> bool:
    tree = ast.parse(
        SIGNER_TEST_PATH.read_text(encoding="utf-8"),
        filename=str(SIGNER_TEST_PATH),
    )
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.Eq)
            and len(node.comparators) == 1
        ):
            continue
        left = node.left
        right = node.comparators[0]
        if (
            isinstance(left, ast.Attribute)
            and left.attr == "__version__"
            and isinstance(left.value, ast.Name)
            and left.value.id == "cryptography"
            and isinstance(right, ast.Constant)
            and right.value == "48.0.0"
        ):
            return True
    return False


@contextmanager
def _working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def test_pyproject_dependency_and_direct_import_contract() -> None:
    pyproject = _pyproject()
    project = pyproject["project"]
    assert isinstance(project, dict)
    dependencies = tuple(project["dependencies"])
    build_system = pyproject["build-system"]
    assert isinstance(build_system, dict)
    build_requirements = tuple(build_system["requires"])

    assert dependencies == APPROVED_DEPENDENCY_DECLARATIONS
    assert "optional-dependencies" not in project
    assert dependencies.count("cryptography==48.0.0") == 1
    assert _signer_test_requires_exact_cryptography_version()

    for declaration in dependencies:
        if declaration == "cryptography==48.0.0":
            continue
        assert not re.search(r"[<>=!~]", declaration)

    declared_names = {
        _normalized_distribution_name(_distribution_name(declaration))
        for declaration in dependencies
    }
    mapped_names = {
        _normalized_distribution_name(distribution)
        for distribution in DIRECT_IMPORT_ROOT_TO_DISTRIBUTION.values()
    }
    assert mapped_names == declared_names
    assert "setuptools" not in declared_names

    project_import_roots = set(DIRECT_IMPORT_ROOT_TO_DISTRIBUTION)
    build_system_import_roots = set(BUILD_SYSTEM_IMPORT_ROOT_TO_REQUIREMENT)
    expected_import_roots = project_import_roots | build_system_import_roots

    repository_python_paths = _repository_python_paths()
    current_test_path = Path(__file__).resolve()
    assert current_test_path in repository_python_paths
    assert "setuptools" in _direct_import_roots(current_test_path)
    assert "setuptools" in build_system_import_roots
    assert "setuptools" not in project_import_roots

    observed_roots: set[str] = set()
    ignored_roots = set(sys.stdlib_module_names) | REPOSITORY_IMPORT_ROOTS
    for path in repository_python_paths:
        observed_roots.update(_direct_import_roots(path) - ignored_roots)

    unknown_import_roots = observed_roots - expected_import_roots
    assert unknown_import_roots == set()
    assert observed_roots == expected_import_roots
    assert observed_roots & project_import_roots == project_import_roots
    assert observed_roots & build_system_import_roots == build_system_import_roots

    approved_build_requirements = set(
        BUILD_SYSTEM_IMPORT_ROOT_TO_REQUIREMENT.values()
    )
    assert set(build_requirements) == approved_build_requirements
    assert len(build_requirements) == len(approved_build_requirements)
    assert BUILD_SYSTEM_IMPORT_ROOT_TO_REQUIREMENT["setuptools"] == (
        "setuptools>=77.0.3"
    )
    assert (
        BUILD_SYSTEM_IMPORT_ROOT_TO_REQUIREMENT["setuptools"]
        in build_requirements
    )


def test_build_system_contract_is_pep639_compatible() -> None:
    build_system = _pyproject()["build-system"]
    assert isinstance(build_system, dict)
    assert build_system["build-backend"] == "setuptools.build_meta"
    assert build_system["requires"] == ["setuptools>=77.0.3"]

    requirement = build_system["requires"][0]
    assert isinstance(requirement, str)
    match = re.fullmatch(r"setuptools>=(\d+)\.(\d+)\.(\d+)", requirement)
    assert match is not None
    assert tuple(int(part) for part in match.groups()) >= (77, 0, 3)
    assert "==" not in requirement
    assert "<" not in requirement


def test_license_metadata_and_canonical_bytes_are_exact() -> None:
    project = _pyproject()["project"]
    assert isinstance(project, dict)
    assert project["license"] == "AGPL-3.0-only"
    assert project["license-files"] == ["LICENSE"]

    assert CANONICAL_GNU_SOURCE_DESCRIPTION == (
        "Complete GNU Affero General Public License version 3 text fetched by "
        "the owner from the official GNU Project HTTPS path"
    )
    assert CANONICAL_GNU_SOURCE_URL == (
        "https://www.gnu.org/licenses/agpl-3.0.txt"
    )
    assert LICENSE_PATH.is_file()
    assert _sha256(LICENSE_PATH) == CANONICAL_AGPL_SOURCE_SHA256


def test_prepared_metadata_carries_spdx_expression_and_license() -> None:
    try:
        import setuptools
        from setuptools import build_meta
    except Exception as exc:
        try:
            observed_version = importlib.metadata.version("setuptools")
        except importlib.metadata.PackageNotFoundError:
            observed_version = "UNAVAILABLE"
        pytest.fail(
            "accepted PEP-639 metadata proof cannot run: "
            f"setuptools_version={observed_version}; "
            f"error={type(exc).__name__}: {exc}"
        )

    observed_version = getattr(setuptools, "__version__", "UNKNOWN")
    with tempfile.TemporaryDirectory(prefix="hedgehog-r-h1a-metadata-") as raw:
        temporary_root = Path(raw)
        assert REPOSITORY_ROOT not in temporary_root.parents

        shutil.copyfile(PYPROJECT_PATH, temporary_root / "pyproject.toml")
        shutil.copyfile(LICENSE_PATH, temporary_root / "LICENSE")
        package_dir = temporary_root / "hedgehog"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("", encoding="utf-8")
        metadata_dir = temporary_root / "metadata"
        metadata_dir.mkdir()

        try:
            with _working_directory(temporary_root):
                dist_info_name = build_meta.prepare_metadata_for_build_wheel(
                    str(metadata_dir)
                )
        except Exception as exc:
            pytest.fail(
                "accepted PEP-639 metadata proof failed: "
                f"setuptools_version={observed_version}; "
                f"error={type(exc).__name__}: {exc}"
            )

        dist_info = metadata_dir / dist_info_name
        metadata = (dist_info / "METADATA").read_text(encoding="utf-8")
        assert "License-Expression: AGPL-3.0-only\n" in metadata

        prepared_license = dist_info / "licenses" / "LICENSE"
        assert prepared_license.is_file()
        assert _sha256(prepared_license) == CANONICAL_AGPL_SOURCE_SHA256


def test_commercial_notice_is_non_granting_and_contact_free() -> None:
    assert COMMERCIAL_NOTICE_PATH.is_file()
    notice = COMMERCIAL_NOTICE_PATH.read_text(encoding="utf-8")
    lowered = notice.lower()
    normalized = " ".join(lowered.split())

    required_statements = (
        "agpl-3.0-only",
        "separately executed written agreement with the rights holder",
        "this file is informational only",
        "does not grant a commercial or proprietary license",
        "does not modify or supplement the agpl-3.0-only terms",
        "does not state or imply that a commercial agreement currently exists",
        "no owner-designated commercial contact channel is currently "
        "published in this repository",
        "no email address, website, form, issue tracker, or other platform "
        "is designated as a commercial contact channel by this file",
        "no claim is made here regarding",
    )
    for statement in required_statements:
        assert statement in normalized

    for denied_claim in (
        "title;",
        "relicensing authority;",
        "patent clearance;",
        "legal review;",
        "public release;",
        "rc2;",
        "production readiness;",
        "production security certification.",
    ):
        assert denied_claim in lowered

    assert re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        notice,
        flags=re.IGNORECASE,
    ) is None
    assert re.search(r"https?://|www\.", notice, flags=re.IGNORECASE) is None
    assert "github issues" not in lowered
    assert "contact@" not in lowered
    assert "example.com" not in lowered
    assert "tbd" not in lowered
    assert not any(symbol in notice for symbol in ("$", "€", "£"))
    assert "pricing" not in lowered
    assert "payment instructions" not in lowered
    assert "negotiation procedures" not in lowered
    assert "contract template" not in lowered
    assert "warranty" not in lowered
    assert "indemnity" not in lowered
