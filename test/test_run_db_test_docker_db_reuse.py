import os
import unittest
from pathlib import Path

from exasol_integration_test_docker_environment.lib.docker import ContextDockerClient
from exasol_integration_test_docker_environment.lib.docker.container.utils import remove_docker_container

import utils as exaslct_utils


class RunDBTestDockerDBReuseTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self._test_container_name = f"test_container_{self.test_environment.flavor_path.name}_release"
        self._db_container_name = f"db_container_{self.test_environment.flavor_path.name}_release"
        self.test_environment.clean_images()
        self.remove_docker_container()

    def tearDown(self):
        self.remove_docker_container()
        self.test_environment.close()

    def remove_docker_container(self):
        remove_docker_container([self._test_container_name, self._db_container_name])

    def get_docker_container_id(self, container: str) -> str:
        with ContextDockerClient() as docker_client:
            print("containerscontainers",[c.name for c in docker_client.containers.list()])
            return docker_client.containers.get(container).id

    def test_reuse(self):
        command = [f"{self.test_environment.executable}",
                   f"run-db-test",
                   f"{exaslct_utils.get_full_test_container_folder_parameter()}",
                   "--reuse-test-environment"]
        command_str = " ".join(command)
        self.test_environment.run_command(command_str, track_task_dependencies=True)
        old_test_container_id = self.get_docker_container_id(self._test_container_name)
        old_db_container_id = self.get_docker_container_id(self._db_container_name)
        self.test_environment.run_command(command_str, track_task_dependencies=True)
        new_test_container_id = self.get_docker_container_id(self._test_container_name)
        new_db_container_id = self.get_docker_container_id(self._db_container_name)
        self.assertEqual(old_test_container_id, new_test_container_id)
        self.assertEqual(old_db_container_id, new_db_container_id)


if __name__ == '__main__':
    unittest.main()
