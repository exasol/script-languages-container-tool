import os
import shlex
import subprocess
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error


class DockerLoadTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.save_path = self.test_environment.temp_dir + "/save_dir"
        self.test_environment.clean_images()
        self.save()
        self.test_environment.clean_images()

    def save(self):
        command = f"{self.test_environment.executable} save --save-directory {self.save_path} "
        self.test_environment.run_command(command, track_task_dependencies=False)
        for path, subdirs, files in os.walk(self.save_path):
            for x in files:
                print(Path(path).joinpath(x))

    def run_command(self, command: str):
        completed_process = subprocess.run(shlex.split(command))
        completed_process.check_returncode()

    def tearDown(self):
        try:
            self.test_environment.close()
        except Exception as e:
            print(e)

    def test_docker_load(self):
        command = f"{self.test_environment.executable} build --cache-directory {self.save_path} "
        self.test_environment.run_command(command, track_task_dependencies=True)


if __name__ == "__main__":
    unittest.main()
