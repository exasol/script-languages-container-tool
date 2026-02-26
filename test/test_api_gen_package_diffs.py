import contextlib
import filecmp
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error

from exasol.slc.api import generate_package_diffs


def copy_dir_contents(src: str | Path, dst: str | Path):
    src = Path(src)
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)

    # Copy entries from src/* into dst/*
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def create_temp_git_slc_repo(
    source_path_one: str, source_path_two: str, tag_name: str = "v1.0.0"
) -> tuple[tempfile.TemporaryDirectory, Path]:
    def run(cmd, cwd: Path):
        subprocess.run(cmd, cwd=str(cwd), check=True, text=True)

    branch = "main"

    def init_repo(repo_path: Path):
        run(["git", "init", "--initial-branch", branch], cwd=repo_path)
        run(["git", "config", "user.name", "Test User"], cwd=repo_path)
        run(["git", "config", "user.email", "test@example.com"], cwd=repo_path)

    tmp = tempfile.TemporaryDirectory(prefix="exal_gen_package_diffs")
    root = Path(tmp.name)

    repo = root / "repo"  # Path(tmp.name)
    repo.mkdir()
    origin = root / "origin.git"
    origin.mkdir()

    # Create a bare origin and set its HEAD to main
    init_repo(origin)

    # init origin repo and create tag
    copy_dir_contents(source_path_one, origin)
    run(["git", "add", "-A"], cwd=origin)
    run(["git", "commit", "-m", f"Add {Path(source_path_one).name}"], cwd=origin)
    run(["git", "tag", tag_name], cwd=origin)

    # init local repo with changes
    init_repo(repo)
    run(["git", "remote", "add", "origin", str(origin)], cwd=repo)
    run(["git", "fetch"], cwd=repo)
    run(["git", "reset", "--hard", "origin/main"], cwd=repo)

    # step 2
    copy_dir_contents(source_path_two, repo)
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-m", f"Add {Path(source_path_two).name}"], cwd=repo)

    return tmp, repo


@contextlib.contextmanager
def tmp_cwd(cwd: Path):
    old_dir = os.getcwd()
    os.chdir(cwd)
    yield None
    os.chdir(old_dir)


class RunDBTestDockerPassThroughTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tmp_root, repo_dir = tmp, repo = create_temp_git_slc_repo(
            exaslct_utils.GEN_PKG_DIFF_LAST_TAG_DIRECTORY,
            exaslct_utils.GEN_PKG_DIFF_CURRENT_DIRECTORY,
            tag_name="1.0.0",
        )
        assert (repo_dir / ".git").exists()
        cls.tmp_root = tmp_root
        cls.repo_dir = repo_dir

    @classmethod
    def tearDownClass(cls):
        cls.tmp_root.cleanup()

    def check_resulting_dir_equality(self, dcmp):
        if dcmp.diff_files or dcmp.right_only or dcmp.left_only:
            dcmp.report()
            self.fail("dcmp detected changed file(s)")
        for sub_dcmp in dcmp.subdirs.values():
            self.check_resulting_dir_equality(sub_dcmp)

    def test_gen_package_diffs_all_flavors(self):
        current_working_copy_name = "2.0.0"
        with tempfile.TemporaryDirectory() as tmp_gen_package_diff_out:
            with tmp_cwd(self.repo_dir):
                generate_package_diffs(
                    output_package_diff_directory=tmp_gen_package_diff_out,
                    current_working_copy_name=current_working_copy_name,
                )
                dcmp = filecmp.dircmp(
                    exaslct_utils.GEN_PKG_DIFF_EXPECTED_RESULT_DIRECTORY,
                    tmp_gen_package_diff_out,
                )

                self.check_resulting_dir_equality(dcmp)

    def test_gen_package_diffs_build_step(self):
        current_working_copy_name = "2.0.0"
        with tempfile.TemporaryDirectory() as tmp_gen_package_diff_out:
            with tmp_cwd(
                exaslct_utils.GEN_PKG_DIFF_CURRENT_DIRECTORY
                / "flavors"
                / "flavor_one"
                / "flavor_base"
            ):
                generate_package_diffs(
                    output_package_diff_directory=tmp_gen_package_diff_out,
                    current_working_copy_name=current_working_copy_name,
                    build_step_path_1="build_step_one",
                    build_step_path_2="build_step_two",
                )
                dcmp = filecmp.dircmp(
                    exaslct_utils.GEN_PKG_DIFF_EXPECTED_RESULT_BUILD_STEP_DIRECTORY,
                    tmp_gen_package_diff_out,
                )

                self.check_resulting_dir_equality(dcmp)


if __name__ == "__main__":
    unittest.main()
