import subprocess
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from exasol.exaslpm.model.package_file_config import Package, PackageFile
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession
from pydantic import BaseModel


class PackageDiffEntry(BaseModel):
    package: Package
    build_step_name: str

    def to_dict(self, version_key: str, build_step_key: str) -> dict[str, str]:
        return {
            "Package": self.package.name,
            version_key: (
                self.package.version if self.package.version else "No version specified"
            ),
            build_step_key: self.build_step_name,
        }


def check_for_duplicated_packages(df: pd.DataFrame):
    duplicates = df.duplicated(subset=["Package"])
    if any(duplicates):
        raise ValueError(f"Found duplicated packages, see package list {df}")


class Status(Enum):
    NEW = "NEW"
    REMOVED = "REMOVED"
    UPDATED = "UPDATED"
    MOVED = "MOVED"


def compare_package_lists(
    package_list_1: list[PackageDiffEntry], package_list_2: list[PackageDiffEntry]
) -> pd.DataFrame:
    package_list_1_dict = [
        pkg_diff.to_dict("Version1", "Build-Step-1") for pkg_diff in package_list_1
    ]
    package_list_1_df = pd.DataFrame(
        package_list_1_dict, columns=["Package", "Version1", "Build-Step-1"]
    )
    check_for_duplicated_packages(package_list_1_df)
    package_list_2_dict = [
        pkg_diff.to_dict("Version2", "Build-Step-2") for pkg_diff in package_list_2
    ]
    package_list_2_df = pd.DataFrame(
        package_list_2_dict, columns=["Package", "Version2", "Build-Step-2"]
    )

    check_for_duplicated_packages(package_list_2_df)
    diff_df = pd.merge(
        package_list_1_df,
        package_list_2_df,
        how="outer",
        on="Package",
        sort=False,
        validate="one_to_one",
    )
    new = diff_df["Version1"].isnull() & ~diff_df["Version2"].isnull()
    removed = diff_df["Version2"].isnull() & ~diff_df["Version1"].isnull()
    updated = (
        ~diff_df["Version1"].isnull()
        & ~diff_df["Version2"].isnull()
        & (diff_df["Version1"] != diff_df["Version2"])
    )
    moved = (
        ~diff_df["Build-Step-1"].isnull()
        & ~diff_df["Build-Step-2"].isnull()
        & (diff_df["Build-Step-1"] != diff_df["Build-Step-2"])
    )
    diff_df["Status"] = [set() for _ in range(len(diff_df))]  # type: ignore[assignment]
    diff_df.loc[new, "Status"] = diff_df.loc[new, "Status"].map(
        lambda x: x | {Status.NEW}
    )
    diff_df.loc[removed, "Status"] = diff_df.loc[removed, "Status"].map(
        lambda x: x | {Status.REMOVED}
    )
    diff_df.loc[updated, "Status"] = diff_df.loc[updated, "Status"].map(
        lambda x: x | {Status.UPDATED}
    )
    diff_df.loc[moved, "Status"] = diff_df.loc[moved, "Status"].map(
        lambda x: x | {Status.MOVED}
    )
    diff_df = diff_df.fillna("")
    diff_df = diff_df.reset_index(drop=True)
    return diff_df


class Installer(Enum):
    APT = "apt"
    PIP = "pip"
    R = "r"
    CONDA = "conda"


def _package_file_to_build_step_package_lists(
    package_file,
) -> dict[str, list[PackageDiffEntry]]:
    result: dict[str, list[PackageDiffEntry]] = {}
    for build_step in package_file.build_steps:
        for phase in build_step.phases:
            installers = [
                (Installer.APT.value, phase.apt),
                (Installer.PIP.value, phase.pip),
                (Installer.R.value, phase.r),
                (Installer.CONDA.value, phase.conda),
            ]
            for installer_name, installer in installers:
                if installer_name not in result:
                    result[installer_name] = []
                if installer and installer.packages:
                    for package in installer.packages:
                        result[installer_name].append(
                            PackageDiffEntry(
                                package=package,
                                build_step_name=build_step.name,
                            )
                        )
    return result


def _load_package_file_config(
    working_copy_root: Path, package_file: Path
) -> PackageFile | None:
    package_file_absolute = working_copy_root / package_file
    if not package_file_absolute.is_file():
        return None
    pkg_file_session = PackageFileSession(package_file=package_file_absolute)
    return pkg_file_session.package_file_config


def compare_package_file(
    package_file_1: Path,
    working_copy_1_root: Path,
    working_copy_1_name: str,
    package_file_2: Path,
    working_copy_2_root: Path,
    working_copy_2_name: str,
) -> dict[str, pd.DataFrame]:
    package_file_config_1 = _load_package_file_config(
        working_copy_1_root, package_file_1
    )
    if package_file_config_1 is None:
        return {}
    compare_same_file = (
        working_copy_1_root == working_copy_2_root and package_file_1 == package_file_2
    )
    package_file_config_2 = None
    if not compare_same_file:
        package_file_config_2 = _load_package_file_config(
            working_copy_2_root, package_file_2
        )

    build_step_packages_1 = _package_file_to_build_step_package_lists(
        package_file_config_1
    )

    build_step_packages_2: dict[str, list[PackageDiffEntry]] = {}
    if package_file_config_2 is not None:
        build_step_packages_2 = _package_file_to_build_step_package_lists(
            package_file_config_2
        )

    result = {}

    for installer in Installer:

        diff_df = compare_package_lists(
            build_step_packages_1[installer.value],
            build_step_packages_2[installer.value],
        )
        new_version_1_name = f"Version in {working_copy_2_name}"
        new_version_2_name = f"Version in {working_copy_1_name}"
        if compare_same_file:
            diff_df = diff_df[
                ["Package", "Version2", "Status", "Build-Step-1", "Build-Step-2"]
            ]
        else:
            diff_df = diff_df[
                [
                    "Package",
                    "Version1",
                    "Version2",
                    "Status",
                    "Build-Step-1",
                    "Build-Step-2",
                ]
            ]
        diff_df = diff_df.rename(
            columns={"Version1": new_version_1_name, "Version2": new_version_2_name}
        )
        result[installer.value] = diff_df

    return result


def compare_flavor(
    flavor_path_1: Path,
    working_copy_1_root: Path,
    working_copy_1_name: str,
    flavor_path_2: Path,
    working_copy_2_root: Path,
    working_copy_2_name: str,
) -> dict[str, dict[str, pd.DataFrame]]:
    public_package_file_1 = flavor_path_1 / "packages.yml"
    public_package_file_2 = flavor_path_2 / "packages.yml"
    internal_package_file_1 = flavor_path_1 / "flavor_base" / "packages.yml"
    internal_package_file_2 = flavor_path_2 / "flavor_base" / "packages.yml"

    return {
        "public_packages": compare_package_file(
            public_package_file_1,
            working_copy_1_root,
            working_copy_1_name,
            public_package_file_2,
            working_copy_2_root,
            working_copy_2_name,
        ),
        "internal_packages": compare_package_file(
            internal_package_file_1,
            working_copy_1_root,
            working_copy_1_name,
            internal_package_file_2,
            working_copy_2_root,
            working_copy_2_name,
        ),
    }


def get_last_git_tag() -> str:
    get_fetch_command = ["git", "fetch"]
    subprocess.run(get_fetch_command, stderr=subprocess.STDOUT, check=True)
    get_main_branch_command = ["git", "symbolic-ref", "refs/remotes/origin/HEAD"]
    get_main_branch_result = subprocess.run(
        get_main_branch_command, stdout=subprocess.PIPE
    )
    get_main_branch_result.check_returncode()

    main_branch_name = get_main_branch_result.stdout.decode("utf-8").strip()
    get_last_tag_command = ["git", "describe", "--abbrev=0", "--tags", main_branch_name]
    last_tag_result = subprocess.run(get_last_tag_command, stdout=subprocess.PIPE)
    last_tag_result.check_returncode()
    last_tag = last_tag_result.stdout.decode("UTF-8").strip()
    return last_tag


def checkout_git_tag_as_worktree(tmp_dir, last_tag):
    checkout_last_tag_command = ["git", "worktree", "add", tmp_dir, last_tag]
    subprocess.run(checkout_last_tag_command, stderr=subprocess.STDOUT, check=True)
    init_submodule_command = ["git", "submodule", "update", "--init"]
    subprocess.run(
        init_submodule_command, cwd=tmp_dir, stderr=subprocess.STDOUT, check=True
    )


def status_format(status_set: set[Status]) -> str:
    if len(status_set) == 0:
        return ""
    elif len(status_set) == 1:
        return list(status_set)[0].value
    else:
        result = []
        for status in Status:
            if status in status_set:
                result.append(status.value)
        return " & ".join(result)


def format_build_step(build_steps: pd.Series) -> str:
    if Status.MOVED in build_steps["Status"]:
        if build_steps["Build-Step-1"] == build_steps["Build-Step-2"]:
            return build_steps["Build-Step-1"]
        return f"{build_steps['Build-Step-1']} -> {build_steps['Build-Step-2']}"
    if build_steps["Build-Step-2"]:
        return build_steps["Build-Step-2"]
    return build_steps["Build-Step-1"]


def generate_dependency_diff_report_for_package_file(
    package_output_file: Path,
    package_scope_caption: str,
    flavor_name_1: str,
    working_copy_1_name: str,
    flavor_name_2: str,
    working_copy_2_name: str,
    diffs: dict[str, pd.DataFrame],
):
    package_output_file.parent.mkdir(parents=True, exist_ok=True)
    flavor_name_1_capitalized = flavor_name_1.capitalize()
    flavor_name_2_capitalized = flavor_name_2.capitalize()
    content = [
        f"# {package_scope_caption} comparison between "
        f"{flavor_name_1_capitalized} flavor in {working_copy_1_name} and "
        f"{flavor_name_2_capitalized} flavor in {working_copy_2_name}",
        "",
        "<!-- markdown-link-check-disable -->",
        "",
    ]
    if len(diffs) == 0:
        content.append("No packages found.")
        content.append("")
        package_output_file.write_text("\n".join(content), encoding="utf-8")
        return

    for installer in Installer:
        diffs_per_installer = diffs[installer.value]
        if len(diffs_per_installer) > 0:
            formatted_diff = pd.DataFrame()
            for status in Status:
                filter_column = diffs_per_installer["Status"].map(lambda x: status in x)
                formatted_diff = pd.concat(
                    [formatted_diff, diffs_per_installer[filter_column]]
                )
            empty_status_filter = diffs_per_installer["Status"].map(
                lambda x: len(x) == 0
            )
            formatted_diff = pd.concat(
                [formatted_diff, diffs_per_installer[empty_status_filter]]
            )

            formatted_diff["Build-Step"] = formatted_diff[
                ["Build-Step-1", "Build-Step-2", "Status"]
            ].apply(format_build_step, axis=1)
            formatted_diff["Status"] = formatted_diff["Status"].map(status_format)

            formatted_diff.sort_values(["Status", "Package"], inplace=True)

            formatted_diff.drop(["Build-Step-1", "Build-Step-2"], axis=1, inplace=True)

            content.append(f"{installer.value} packages\n")
            content.append(formatted_diff.to_markdown())
            package_output_file.write_text("\n".join(content), encoding="utf-8")


def generate_dependency_diff_report_for_flavor(
    flavor_name_1: str,
    working_copy_1_name: str,
    flavor_name_2: str,
    working_copy_2_name: str,
    diffs: dict[str, dict[str, pd.DataFrame]],
    base_output_directory: Path,
    relative_output_directory: Path,
):
    flavor_output_directory = base_output_directory / relative_output_directory
    flavor_output_directory.mkdir(parents=True, exist_ok=True)
    generate_dependency_diff_report_for_package_file(
        flavor_output_directory / "public_packages.md",
        "Public packages",
        flavor_name_1,
        working_copy_1_name,
        flavor_name_2,
        working_copy_2_name,
        diffs["public_packages"],
    )
    generate_dependency_diff_report_for_package_file(
        flavor_output_directory / "internal_packages.md",
        "Internal packages",
        flavor_name_1,
        working_copy_1_name,
        flavor_name_2,
        working_copy_2_name,
        diffs["internal_packages"],
    )
    return f"""
## {flavor_name_1}
- [Release dependencies]({relative_output_directory}/public_packages.md)
- [Build dependencies]({relative_output_directory}/internal_packages.md)
    """


def generate_dependency_diff_report_for_all_flavors(
    working_copy_1_root: Path,
    working_copy_1_name: str,
    working_copy_2_root: Path,
    working_copy_2_name: str,
    base_output_directory: Path,
):
    base_output_directory.mkdir(parents=True, exist_ok=True)
    overview_file = Path(base_output_directory, "README.md")
    overview_file_content = (
        f"# Package Version Comparison between "
        f"{working_copy_1_name} and "
        f"{working_copy_2_name}\n\n"
    )
    for flavor_path in sorted(Path(working_copy_1_root, "flavors").iterdir()):
        if flavor_path.is_dir():
            relative_flavor_path = flavor_path.relative_to(working_copy_1_root)
            relative_flavor_path_2 = relative_flavor_path
            if Path(working_copy_2_root).joinpath(relative_flavor_path).exists():
                diffs = compare_flavor(
                    relative_flavor_path,
                    working_copy_1_root,
                    working_copy_1_name,
                    relative_flavor_path,
                    working_copy_2_root,
                    working_copy_2_name,
                )
            else:
                derived_from_file = flavor_path / "flavor_base" / "derived_from"
                if derived_from_file.is_file():
                    with open(flavor_path / "flavor_base" / "derived_from") as f:
                        relative_flavor_path_2_str = f.read().strip()
                    relative_flavor_path_2 = Path(relative_flavor_path_2_str)
                    if (
                        Path(working_copy_2_root)
                        .joinpath(relative_flavor_path_2)
                        .exists()
                    ):
                        diffs = compare_flavor(
                            relative_flavor_path,
                            working_copy_1_root,
                            working_copy_1_name,
                            relative_flavor_path_2,
                            working_copy_2_root,
                            working_copy_2_name,
                        )
                    else:
                        raise Exception(
                            f"Could not find flavor {relative_flavor_path_2}"
                        )
                else:
                    diffs = compare_flavor(
                        relative_flavor_path,
                        working_copy_1_root,
                        working_copy_1_name,
                        relative_flavor_path,
                        working_copy_1_root,
                        working_copy_1_name,
                    )
            if len(diffs["public_packages"]) > 0 or len(diffs["internal_packages"]) > 0:
                flavor_1 = relative_flavor_path.name
                flavor_2 = relative_flavor_path_2.name
                if flavor_1 == flavor_2:
                    flavor_relative_output_directory = Path(flavor_1)
                else:
                    flavor_relative_output_directory = Path(f"{flavor_1}__{flavor_2}")
                overview_file_content += generate_dependency_diff_report_for_flavor(
                    flavor_1,
                    working_copy_1_name,
                    flavor_2,
                    working_copy_2_name,
                    diffs,
                    base_output_directory,
                    flavor_relative_output_directory,
                )
    with overview_file.open("wt") as f:
        f.write(overview_file_content)


def gen_package_diffs(
    output_directory: str,
    current_working_copy_name: str,
    compare_to_commit: str | None,
):
    if compare_to_commit is None:
        compare_to_commit = get_last_git_tag()
    with TemporaryDirectory() as working_copy_2_root:
        checkout_git_tag_as_worktree(working_copy_2_root, compare_to_commit)
        working_copy_root = Path(".")
        working_copy_1_name = current_working_copy_name
        working_copy_2_name = compare_to_commit
        generate_dependency_diff_report_for_all_flavors(
            working_copy_root,
            working_copy_1_name,
            Path(working_copy_2_root),
            working_copy_2_name,
            Path(output_directory),
        )
