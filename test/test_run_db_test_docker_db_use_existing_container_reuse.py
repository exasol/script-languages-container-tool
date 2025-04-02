import unittest
from pathlib import Path
from typing import Dict

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.docker.container.utils import (
    remove_docker_container,
)


class DockerRunDBTestDockerUseExistingContainerReuse(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.test_environment.clean_images()
        self._test_container_name = (
            f"test_container_{self.test_environment.flavor_path.name}_release"
        )
        self._db_container_name = (
            f"db_container_{self.test_environment.flavor_path.name}_release"
        )
        self.tmp_container_file_dir = (
            Path(self.test_environment.temp_dir) / f"export_{self.__class__.__name__}"
        )

    def tearDown(self):
        self.remove_docker_container()
        self.test_environment.close()

    def remove_docker_container(self):
        remove_docker_container(
            [
                f"test_container_{self.test_environment.name}",
                f"db_container_{self.test_environment.name}",
            ]
        )

    def test_run_db_tests_docker_db_use_existing_container(self):
        def run_command(container_file: str):
            command = [
                f"{self.test_environment.executable}",
                f"run-db-test",
                f"{exaslct_utils.get_full_test_container_folder_parameter()}",
                "--reuse-test-environment",
                "--use-existing-container",
                container_file,
            ]
            self.test_environment.run_command(
                " ".join(command), track_task_dependencies=True
            )

        def container_ids() -> Dict[str, str]:
            return exaslct_utils.get_docker_container_ids(
                self._test_container_name,
                self._db_container_name,
            )

        exported_container_file = self._build_container_file()

        run_command(str(exported_container_file))
        old_ids = container_ids()
        run_command(str(exported_container_file))
        new_ids = container_ids()
        self.assertEqual(old_ids, new_ids)

    def _build_container_file(self):
        command = [
            self.test_environment.executable,
            "export",
            "--export-path",
            str(self.tmp_container_file_dir),
        ]
        self.test_environment.run_command(" ".join(command))
        exported_container_file_glob = list(
            self.tmp_container_file_dir.glob("**/*.tar.gz")
        )
        self.assertEqual(len(exported_container_file_glob), 1)
        exported_container_file = exported_container_file_glob[0]
        return exported_container_file


if __name__ == "__main__":
    unittest.main()
