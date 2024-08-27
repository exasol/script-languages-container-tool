import filecmp
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

import importlib_metadata
import importlib_resources

from exasol_script_languages_container_tool.lib.tasks.install_starter_scripts.run_starter_script_installation import (
    run_starter_script_installation,
)

PACKAGE_IDENTITY = "exasol-script-languages-container-tool"
MODULE_IDENTITY = PACKAGE_IDENTITY.replace("-", "_")
TARGET_EXASLCT_SCRIPTS_DIR = "exaslct_scripts"


class InstallStarterScriptTests(unittest.TestCase):

    def test_positive(self):
        with tempfile.TemporaryDirectory() as target_dir:
            target_path = Path(target_dir)
            run_starter_script_installation(
                target_path, target_path / TARGET_EXASLCT_SCRIPTS_DIR, False
            )

            exaslct_script_path = (
                importlib_resources.files(MODULE_IDENTITY) / "starter_scripts"
            )
            self.assertTrue(exaslct_script_path.is_dir())
            cmp_res = filecmp.dircmp(
                exaslct_script_path, target_path / TARGET_EXASLCT_SCRIPTS_DIR
            )
            self.assertTrue(len(cmp_res.common) > 0)
            self.assertEqual(len(cmp_res.left_only), 0)
            self.assertEqual(len(cmp_res.right_only), 1)
            self.assertEqual(cmp_res.right_only[0], "exaslct.sh")
            exaslct_link = target_path / "exaslct"
            self.assertTrue(exaslct_link.exists() and exaslct_link.is_symlink())

    def _build_docker_runner(self):
        build_docker_runner_img_script = (
            Path(__file__).parent.parent.absolute()
            / "scripts"
            / "build"
            / "build_docker_runner_image.sh"
        )
        completed_process = subprocess.run(
            [str(build_docker_runner_img_script)], stdout=subprocess.PIPE
        )
        completed_process.check_returncode()
        current_runner_image_name = completed_process.stdout.decode("utf-8").strip("\n")
        return current_runner_image_name

    def _build_docker_runner_release_tag(
        self, current_runner_image_name: str, script_dir: str
    ):
        construct_docker_runner_image_script = (
            Path(script_dir)
            / TARGET_EXASLCT_SCRIPTS_DIR
            / "construct_docker_runner_image_name.sh"
        )
        version = importlib_metadata.version(MODULE_IDENTITY)
        completed_process = subprocess.run(
            ["bash", str(construct_docker_runner_image_script), f"{version}"],
            stdout=subprocess.PIPE,
        )
        completed_process.check_returncode()
        target_docker_runner_image_name = completed_process.stdout.decode(
            "utf-8"
        ).strip("\n")
        completed_process = subprocess.run(
            [
                "docker",
                "tag",
                current_runner_image_name,
                target_docker_runner_image_name,
            ]
        )

        completed_process.check_returncode()

    def test_execute_help(self):

        # First we build the image of the current GIT commit
        current_runner_image_name = self._build_docker_runner()

        with tempfile.TemporaryDirectory() as target_dir:
            target_path = Path(target_dir)
            # Now we install the starter scripts
            run_starter_script_installation(
                target_path, target_path / TARGET_EXASLCT_SCRIPTS_DIR, False
            )

            # Now we use the 'construct_docker_runner_image_name.sh' in
            # the installed scripts to get the name of the correct tag.
            # This tag must match with what 'exaslct' will try to use later.
            # Thus we also test if the installed version of 'construct_docker_runner_image_name.sh' works as expected.
            self._build_docker_runner_release_tag(
                script_dir=target_dir,
                current_runner_image_name=current_runner_image_name,
            )

            # Finally we call the installed version of 'exaslct'.
            # This is supposed to use the previously generated docker runner image.
            command = f"{target_dir}/exaslct --help"
            completed_process = subprocess.run(
                shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            try:
                completed_process.check_returncode()
            except subprocess.CalledProcessError as ex:
                print(
                    f"Error executing exaslct. Log is \n'{completed_process.stdout.decode('utf-8')}'",
                    flush=True,
                )
                raise ex


if __name__ == "__main__":
    unittest.main()
