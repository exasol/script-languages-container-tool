import unittest
from typing import Dict

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.docker import ContextDockerClient
from exasol_integration_test_docker_environment.lib.docker.container.utils import (
    remove_docker_container,
)


class RunDBTestDockerDBReuseTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self._test_container_name = (
            f"test_container_{self.test_environment.flavor_path.name}_release"
        )
        self._db_container_name = (
            f"db_container_{self.test_environment.flavor_path.name}_release"
        )
        self.test_environment.clean_images()
        self.remove_docker_container()

    def tearDown(self):
        self.remove_docker_container()
        self.test_environment.close()

    def remove_docker_container(self):
        remove_docker_container([self._test_container_name, self._db_container_name])

    def test_reuse(self):
        def run_command():
            command = [
                f"{self.test_environment.executable}",
                f"run-db-test",
                f"{exaslct_utils.get_full_test_container_folder_parameter()}",
                "--reuse-test-environment",
            ]
            self.test_environment.run_command(
                " ".join(command), track_task_dependencies=True
            )

        def container_ids() -> dict[str, str]:
            return exaslct_utils.get_docker_container_ids(
                self._test_container_name,
                self._db_container_name,
            )

        run_command()
        old_ids = container_ids()
        run_command()
        new_ids = container_ids()
        self.assertEqual(old_ids, new_ids)


if __name__ == "__main__":
    unittest.main()
