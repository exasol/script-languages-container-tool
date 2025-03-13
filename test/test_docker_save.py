import os
import shlex
import subprocess
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils


class DockerSaveTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.save_path = self.test_environment.temp_dir + "/save_dir"
        self.test_environment.clean_images()

    def run_command(self, command: str):
        completed_process = subprocess.run(shlex.split(command))
        completed_process.check_returncode()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_save(self):
        command = f"{self.test_environment.executable} save --save-directory {self.save_path} "
        self.test_environment.run_command(command, track_task_dependencies=True)
        saved_files = os.listdir(
            Path(self.save_path).joinpath(self.test_environment.repository_name).parent
        )
        self.assertTrue(
            len(saved_files) > 0,
            f"Did not found saved files for repository {self.test_environment.repository_name} "
            f"in list {saved_files}",
        )


if __name__ == "__main__":
    unittest.main()
