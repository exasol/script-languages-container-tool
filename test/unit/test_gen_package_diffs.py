"""Unit tests for package-diff comparison and markdown report generation.

The tests intentionally combine:
- behavioral status checks (`NEW`, `REMOVED`, `UPDATED`, `MOVED`)
- snapshot-style markdown assertions for report rendering
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest
from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    CondaPackage,
    CondaPackages,
    Package,
    PackageFile,
    Phase,
    PipPackage,
    PipPackages,
    RPackage,
    RPackages,
)
from exasol.exaslpm.model.serialization import to_yaml_str

from exasol.slc.internal.gen_package_diffs.gen_package_diffs import (
    Installer,
    PackageDiffEntry,
    Status,
    compare_flavor,
    compare_package_lists,
    generate_dependency_diff_report_for_package_file,
)


def _package_diff_entry(
    package_name: str, package_version: str | None, build_step_name: str
) -> PackageDiffEntry:
    """Create a compact `PackageDiffEntry` test object."""
    return PackageDiffEntry(
        package=Package(name=package_name, version=package_version),
        build_step_name=build_step_name,
    )


@dataclass(frozen=True)
class ComparePackageListsCase:
    """Single input/output case for `compare_package_lists()` status checks."""

    package_list_1: list[PackageDiffEntry]
    package_list_2: list[PackageDiffEntry]
    expected_status: set[Status]


@pytest.mark.parametrize(
    "case",
    [
        ComparePackageListsCase(
            package_list_1=[_package_diff_entry("pkg_new", "1.0.0", "step_a")],
            package_list_2=[],
            expected_status={Status.REMOVED},
        ),
        ComparePackageListsCase(
            package_list_1=[],
            package_list_2=[_package_diff_entry("pkg_removed", "1.0.0", "step_a")],
            expected_status={Status.NEW},
        ),
        ComparePackageListsCase(
            package_list_1=[_package_diff_entry("pkg_updated", "2.0.0", "step_a")],
            package_list_2=[_package_diff_entry("pkg_updated", "1.0.0", "step_a")],
            expected_status={Status.UPDATED},
        ),
        ComparePackageListsCase(
            package_list_1=[_package_diff_entry("pkg_moved", "1.0.0", "step_a")],
            package_list_2=[_package_diff_entry("pkg_moved", "1.0.0", "step_b")],
            expected_status={Status.MOVED},
        ),
        ComparePackageListsCase(
            package_list_1=[
                _package_diff_entry("pkg_updated_and_moved", "2.0.0", "step_a")
            ],
            package_list_2=[
                _package_diff_entry("pkg_updated_and_moved", "1.0.0", "step_b")
            ],
            expected_status={Status.UPDATED, Status.MOVED},
        ),
        ComparePackageListsCase(
            package_list_1=[_package_diff_entry("pkg_unchanged", "1.0.0", "step_a")],
            package_list_2=[_package_diff_entry("pkg_unchanged", "1.0.0", "step_a")],
            expected_status=set(),
        ),
    ],
)
def test_compare_package_lists_status_matrix(case: ComparePackageListsCase):
    """Validate each status combination in isolation via parametrized cases."""
    diff = compare_package_lists(case.package_list_1, case.package_list_2)
    assert len(diff) == 1
    assert diff.iloc[0]["Status"] == case.expected_status


def _status_map(diff_df: pd.DataFrame) -> dict[str, set[Status]]:
    """Map package name to status set for concise assertions."""
    return {
        package: status_set
        for package, status_set in zip(diff_df["Package"], diff_df["Status"])
    }


def _write_package_file(
    package_file_path: Path,
    package_file: PackageFile,
):
    """Serialize a `PackageFile` model to YAML at the target path."""
    package_file_path.parent.mkdir(parents=True, exist_ok=True)
    package_file_path.write_text(to_yaml_str(package_file), encoding="utf-8")


def _packages_for_step(
    installer: Installer, build_step_name: str, working_copy: int
) -> list[Package]:
    """Return packages for one installer/build-step/working-copy combination.

    Package names are intentionally suffixed with status semantics, so assertions
    can directly reference expected statuses by package name.
    """
    prefix = installer.value
    package_versions = {
        "step_common": {
            1: [
                Package(name="removed", version="1.0.0"),
                Package(name="updated", version="1.0.0"),
                Package(name="unchanged", version="1.0.0"),
            ],
            2: [
                Package(name="new", version="1.0.0"),
                Package(name="updated", version="2.0.0"),
                Package(name="unchanged", version="1.0.0"),
            ],
        },
        "step_a": {
            1: [
                Package(name="moved", version="1.0.0"),
                Package(name="updated_and_moved", version="1.0.0"),
            ],
            2: [
                Package(name="moved", version="1.0.0"),
                Package(name="updated_and_moved", version="2.0.0"),
            ],
        },
        "step_b": {
            1: [
                Package(name="moved", version="1.0.0"),
                Package(name="updated_and_moved", version="1.0.0"),
            ],
            2: [
                Package(name="moved", version="1.0.0"),
                Package(name="updated_and_moved", version="2.0.0"),
            ],
        },
    }
    return [
        Package(name=f"{prefix}_{package.name}", version=package.version)
        for package in package_versions[build_step_name][working_copy]
    ]


def _phase_for_step(
    installer: Installer, build_step_name: str, working_copy: int
) -> Phase:
    """Build a phase with exactly one installer, matching package-file rules."""
    packages = _packages_for_step(installer, build_step_name, working_copy)
    phase_name = f"{build_step_name}_{installer.value}"
    if installer == Installer.APT:
        return Phase(
            name=phase_name,
            apt=AptPackages(
                packages=[AptPackage(name=p.name, version=p.version) for p in packages]
            ),
        )
    if installer == Installer.PIP:
        return Phase(
            name=phase_name,
            pip=PipPackages(
                packages=[PipPackage(name=p.name, version=p.version) for p in packages]
            ),
        )
    if installer == Installer.R:
        return Phase(
            name=phase_name,
            r=RPackages(
                packages=[RPackage(name=p.name, version=p.version) for p in packages]
            ),
        )
    return Phase(
        name=phase_name,
        conda=CondaPackages(
            packages=[CondaPackage(name=p.name, version=p.version) for p in packages]
        ),
    )


def _create_package_file(working_copy: int) -> PackageFile:
    """Create a full package file that produces all status combinations."""
    second_step = "step_a" if working_copy == 1 else "step_b"
    return PackageFile(
        build_steps=[
            BuildStep(
                name="step_common",
                phases=[
                    _phase_for_step(installer, "step_common", working_copy)
                    for installer in Installer
                ],
            ),
            BuildStep(
                name=second_step,
                phases=[
                    _phase_for_step(installer, second_step, working_copy)
                    for installer in Installer
                ],
            ),
        ]
    )


def test_compare_flavor_all_status_combinations_for_all_installers(tmp_path: Path):
    """Use real package-file parsing/comparison for both public and internal scopes."""
    flavor_rel_path = Path("flavors") / "flavor_matrix"
    root_1 = tmp_path / "wc_1"
    root_2 = tmp_path / "wc_2"

    package_file_wc_1 = _create_package_file(working_copy=1)
    package_file_wc_2 = _create_package_file(working_copy=2)

    _write_package_file(root_1 / flavor_rel_path / "packages.yml", package_file_wc_1)
    _write_package_file(root_2 / flavor_rel_path / "packages.yml", package_file_wc_2)
    _write_package_file(
        root_1 / flavor_rel_path / "flavor_base" / "packages.yml", package_file_wc_1
    )
    _write_package_file(
        root_2 / flavor_rel_path / "flavor_base" / "packages.yml", package_file_wc_2
    )

    result = compare_flavor(
        flavor_rel_path, root_1, "wc_1", flavor_rel_path, root_2, "wc_2"
    )

    for package_scope in ("public_packages", "internal_packages"):
        for installer in Installer:
            status_by_package = _status_map(result[package_scope][installer.value])
            assert status_by_package[f"{installer.value}_new"] == {Status.NEW}
            assert status_by_package[f"{installer.value}_removed"] == {Status.REMOVED}
            assert status_by_package[f"{installer.value}_updated"] == {Status.UPDATED}
            assert status_by_package[f"{installer.value}_moved"] == {Status.MOVED}
            assert status_by_package[f"{installer.value}_updated_and_moved"] == {
                Status.UPDATED,
                Status.MOVED,
            }
            assert status_by_package[f"{installer.value}_unchanged"] == set()


def test_generate_dependency_diff_report_for_package_file_without_diffs(tmp_path: Path):
    """Verify the explicit empty-output branch."""
    output_file = tmp_path / "dependency_diff.md"

    generate_dependency_diff_report_for_package_file(
        package_output_file=output_file,
        package_scope_caption="Public packages",
        flavor_name_1="flavor_a",
        working_copy_1_name="wc_1",
        flavor_name_2="flavor_b",
        working_copy_2_name="wc_2",
        diffs={},
    )

    content = output_file.read_text(encoding="utf-8")
    assert (
        '# Public packages comparison between flavor "Flavor A" in wc_1 and flavor "Flavor B" in wc_2'
        in content
    )
    assert "No packages found." in content


def _empty_report_diff() -> pd.DataFrame:
    """Return an empty diff frame with the expected report columns."""
    return pd.DataFrame(
        columns=[
            "Package",
            "Version in old",
            "Version in new",
            "Status",
            "Build-Step-1",
            "Build-Step-2",
        ]
    )


@dataclass(frozen=True)
class GenerateDependencyReportCase:
    """Input/expected-output case for markdown report snapshot checks."""

    diffs: dict[str, pd.DataFrame]
    expected_markdown: str


# Exact markdown snapshots for combinations of installers and statuses.
REPORT_CASES = [
    GenerateDependencyReportCase(
        diffs={
            Installer.APT.value: pd.DataFrame(
                [
                    {
                        "Package": "pkg_new",
                        "Version in old": "",
                        "Version in new": "1.0.0",
                        "Status": {Status.NEW},
                        "Build-Step-1": "",
                        "Build-Step-2": "build_new",
                    },
                    {
                        "Package": "pkg_removed",
                        "Version in old": "1.0.0",
                        "Version in new": "",
                        "Status": {Status.REMOVED},
                        "Build-Step-1": "build_old",
                        "Build-Step-2": "",
                    },
                    {
                        "Package": "pkg_updated",
                        "Version in old": "1.0.0",
                        "Version in new": "2.0.0",
                        "Status": {Status.UPDATED},
                        "Build-Step-1": "build_a",
                        "Build-Step-2": "build_a",
                    },
                    {
                        "Package": "pkg_moved",
                        "Version in old": "1.0.0",
                        "Version in new": "1.0.0",
                        "Status": {Status.MOVED},
                        "Build-Step-1": "build_a",
                        "Build-Step-2": "build_b",
                    },
                    {
                        "Package": "pkg_updated_and_moved",
                        "Version in old": "1.0.0",
                        "Version in new": "2.0.0",
                        "Status": {Status.UPDATED, Status.MOVED},
                        "Build-Step-1": "build_c",
                        "Build-Step-2": "build_d",
                    },
                    {
                        "Package": "pkg_unchanged",
                        "Version in old": "1.0.0",
                        "Version in new": "1.0.0",
                        "Status": set(),
                        "Build-Step-1": "build_1",
                        "Build-Step-2": "build_2",
                    },
                ]
            ),
            Installer.PIP.value: pd.DataFrame(
                [
                    {
                        "Package": "pip_pkg",
                        "Version in old": "1.0.0",
                        "Version in new": "1.0.0",
                        "Status": set(),
                        "Build-Step-1": "pip_build",
                        "Build-Step-2": "pip_build",
                    }
                ]
            ),
            Installer.R.value: _empty_report_diff(),
            Installer.CONDA.value: _empty_report_diff(),
        },
        expected_markdown="""# Internal packages comparison between flavor "Flavor C" in wc_1 and flavor "Flavor D" in wc_2

<!-- markdown-link-check-disable -->

## Apt packages

|    | Package               | Version in old   | Version in new   | Status          | Build-Step         |
|---:|:----------------------|:-----------------|:-----------------|:----------------|:-------------------|
|  5 | pkg_unchanged         | 1.0.0            | 1.0.0            |                 | build_2            |
|  3 | pkg_moved             | 1.0.0            | 1.0.0            | MOVED           | build_a -> build_b |
|  0 | pkg_new               |                  | 1.0.0            | NEW             | build_new          |
|  1 | pkg_removed           | 1.0.0            |                  | REMOVED         | build_old          |
|  2 | pkg_updated           | 1.0.0            | 2.0.0            | UPDATED         | build_a            |
|  4 | pkg_updated_and_moved | 1.0.0            | 2.0.0            | UPDATED & MOVED | build_c -> build_d |
|  4 | pkg_updated_and_moved | 1.0.0            | 2.0.0            | UPDATED & MOVED | build_c -> build_d |

## Pip packages

|    | Package   | Version in old   | Version in new   | Status   | Build-Step   |
|---:|:----------|:-----------------|:-----------------|:---------|:-------------|
|  0 | pip_pkg   | 1.0.0            | 1.0.0            |          | pip_build    |""",
    ),
    GenerateDependencyReportCase(
        diffs={
            Installer.APT.value: _empty_report_diff(),
            Installer.PIP.value: _empty_report_diff(),
            Installer.R.value: pd.DataFrame(
                [
                    {
                        "Package": "r_keep",
                        "Version in old": "1.0.0",
                        "Version in new": "1.0.0",
                        "Status": set(),
                        "Build-Step-1": "r_step",
                        "Build-Step-2": "r_step",
                    },
                    {
                        "Package": "r_drop",
                        "Version in old": "2.0.0",
                        "Version in new": "",
                        "Status": {Status.REMOVED},
                        "Build-Step-1": "r_step",
                        "Build-Step-2": "",
                    },
                ]
            ),
            Installer.CONDA.value: pd.DataFrame(
                [
                    {
                        "Package": "conda_add",
                        "Version in old": "",
                        "Version in new": "9.9.9",
                        "Status": {Status.NEW},
                        "Build-Step-1": "",
                        "Build-Step-2": "conda_step",
                    },
                    {
                        "Package": "conda_move",
                        "Version in old": "1.2.3",
                        "Version in new": "1.2.3",
                        "Status": {Status.MOVED},
                        "Build-Step-1": "a",
                        "Build-Step-2": "b",
                    },
                ]
            ),
        },
        expected_markdown="""# Internal packages comparison between flavor "Flavor C" in wc_1 and flavor "Flavor D" in wc_2

<!-- markdown-link-check-disable -->

## R packages

|    | Package   | Version in old   | Version in new   | Status   | Build-Step   |
|---:|:----------|:-----------------|:-----------------|:---------|:-------------|
|  0 | r_keep    | 1.0.0            | 1.0.0            |          | r_step       |
|  1 | r_drop    | 2.0.0            |                  | REMOVED  | r_step       |

## Conda packages

|    | Package    | Version in old   | Version in new   | Status   | Build-Step   |
|---:|:-----------|:-----------------|:-----------------|:---------|:-------------|
|  1 | conda_move | 1.2.3            | 1.2.3            | MOVED    | a -> b       |
|  0 | conda_add  |                  | 9.9.9            | NEW      | conda_step   |""",
    ),
]


@pytest.mark.parametrize("case", REPORT_CASES)
def test_generate_dependency_diff_report_for_package_file_status_and_build_step_combinations(
    tmp_path: Path, case: GenerateDependencyReportCase
):
    """Assert full markdown output for representative installer/status combinations."""
    output_file = tmp_path / "dependency_diff.md"

    generate_dependency_diff_report_for_package_file(
        package_output_file=output_file,
        package_scope_caption="Internal packages",
        flavor_name_1="flavor_c",
        working_copy_1_name="wc_1",
        flavor_name_2="flavor_d",
        working_copy_2_name="wc_2",
        diffs=case.diffs,
    )

    content = output_file.read_text(encoding="utf-8")
    assert content == case.expected_markdown
